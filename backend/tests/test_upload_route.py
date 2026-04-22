"""
Tests for /api/v1/upload route — KAN-16 tenant isolation.

Uses the same fake-module injection pattern as test_analyze.py so the
heavy GCP / Firebase dependencies are never imported.
"""
import importlib.util
import io
import os
import pathlib
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "app"
    / "routes"
    / "upload.py"
)

TEST_USER_ID = "user-abc-123"


def load_upload_module():
    fake_fastapi = types.ModuleType("fastapi")
    fake_app = types.ModuleType("app")
    fake_services = types.ModuleType("app.services")
    fake_firestore = types.ModuleType("app.services.firestore")
    fake_auth = types.ModuleType("app.services.auth")
    fake_google = types.ModuleType("google")
    fake_cloud = types.ModuleType("google.cloud")
    fake_storage = types.ModuleType("google.cloud.storage")

    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class APIRouter:
        def __init__(self, *args, **kwargs):
            pass

        def post(self, _path):
            def decorator(func):
                return func
            return decorator

    def Depends(dependency):
        return dependency

    # Fake UploadFile that reads from an in-memory bytes buffer
    class FakeUploadFile:
        def __init__(self, filename: str, content: bytes):
            self.filename = filename
            self._content = content

        async def read(self):
            return self._content

        async def close(self):
            pass

    async def _placeholder_async(*_args, **_kwargs):
        raise AssertionError("Test should patch async dependency")

    def _placeholder_sync(*_args, **_kwargs):
        raise AssertionError("Test should patch sync dependency")

    # Wire fakes
    fake_fastapi.APIRouter = APIRouter
    fake_fastapi.Depends = Depends
    fake_fastapi.HTTPException = HTTPException
    fake_fastapi.UploadFile = FakeUploadFile
    fake_fastapi.File = lambda *a, **kw: None  # File(...) sentinel

    fake_firestore.create_transaction_record = _placeholder_async
    fake_auth.get_current_user = _placeholder_async

    # Fake storage.Client and bucket/blob chain
    fake_blob = MagicMock()
    fake_blob.upload_from_string = MagicMock()
    fake_blob.delete = MagicMock()

    fake_bucket = MagicMock()
    fake_bucket.blob = MagicMock(return_value=fake_blob)

    fake_storage_client = MagicMock()
    fake_storage_client.bucket = MagicMock(return_value=fake_bucket)

    class FakeStorageClient:
        def __init__(self, project=None):
            self.project = project

        def bucket(self, name):
            return fake_bucket

    fake_storage.Client = FakeStorageClient

    fake_services.firestore = fake_firestore
    fake_services.auth = fake_auth
    fake_app.services = fake_services
    fake_cloud.storage = fake_storage
    fake_google.cloud = fake_cloud

    fake_modules = {
        "fastapi": fake_fastapi,
        "app": fake_app,
        "app.services": fake_services,
        "app.services.firestore": fake_firestore,
        "app.services.auth": fake_auth,
        "google": fake_google,
        "google.cloud": fake_cloud,
        "google.cloud.storage": fake_storage,
    }

    module_name = "test_target_upload_route"
    # Force fresh load
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, fake_modules):
        assert spec.loader is not None
        spec.loader.exec_module(module)

    return module, HTTPException, fake_blob, fake_bucket


class UploadRouteFirestoreUserIdTests(unittest.IsolatedAsyncioTestCase):
    """Step 4: verify user_id is passed explicitly to create_transaction_record."""

    async def test_firestore_called_with_correct_user_id(self):
        """create_transaction_record must receive user_id from the JWT uid claim."""
        module, _, fake_blob, fake_bucket = load_upload_module()

        fake_bucket.blob.side_effect = None
        fake_bucket.blob.return_value = fake_blob
        fake_blob.upload_from_string = MagicMock()

        current_user = {"uid": TEST_USER_ID}
        fake_file = module.UploadFile("invoice.pdf", b"%PDF-fake-content")

        create_mock = AsyncMock(return_value={})
        with patch.dict(
            os.environ,
            {"GCS_BUCKET_NAME": "puente-docs-dev", "GCP_PROJECT_ID": "demo"},
        ), patch.object(
            module,
            "create_transaction_record",
            create_mock,
        ):
            await module.upload_document(
                file=fake_file,
                current_user=current_user,
            )

        create_mock.assert_awaited_once()
        call_kwargs = create_mock.await_args.kwargs
        self.assertEqual(
            call_kwargs.get("user_id"),
            TEST_USER_ID,
            f"Expected user_id={TEST_USER_ID!r} in Firestore call, got: {call_kwargs}",
        )

    async def test_different_uid_produces_different_gcs_path(self):
        """GCS paths for two distinct users must not overlap."""
        module, _, fake_blob, fake_bucket = load_upload_module()

        paths_by_user: dict[str, list[str]] = {}

        def make_capture(uid):
            captured = []
            paths_by_user[uid] = captured

            def _blob(name):
                captured.append(name)
                return MagicMock()
            return _blob

        for uid in ("user-A", "user-B"):
            fake_bucket.blob.side_effect = make_capture(uid)
            fake_file = module.UploadFile("invoice.pdf", b"%PDF-data")
            with patch.dict(
                os.environ,
                {"GCS_BUCKET_NAME": "puente-docs-dev", "GCP_PROJECT_ID": "demo"},
            ), patch.object(
                module,
                "create_transaction_record",
                AsyncMock(return_value={}),
            ):
                await module.upload_document(
                    file=fake_file,
                    current_user={"uid": uid},
                )

        path_a = paths_by_user["user-A"][0]
        path_b = paths_by_user["user-B"][0]
        self.assertIn("user-A", path_a)
        self.assertIn("user-B", path_b)
        self.assertNotIn("user-A", path_b)
        self.assertNotIn("user-B", path_a)


class UploadRouteGCSPathTests(unittest.IsolatedAsyncioTestCase):
    """Verify the GCS blob path is scoped under users/{user_id}/documents/."""

    async def test_gcs_blob_path_contains_user_id(self):
        """Step 3: blob_name must follow users/{user_id}/documents/{ts}/{doc_id}.pdf."""
        module, _, fake_blob, fake_bucket = load_upload_module()

        # Capture the blob name passed to bucket.blob()
        captured_blob_names = []
        fake_bucket.blob.side_effect = lambda name: (
            captured_blob_names.append(name) or MagicMock()
        )

        current_user = {"uid": TEST_USER_ID}
        fake_file = module.UploadFile("invoice.pdf", b"%PDF-fake-content")

        with patch.dict(
            os.environ,
            {"GCS_BUCKET_NAME": "puente-docs-dev", "GCP_PROJECT_ID": "demo"},
        ), patch.object(
            module,
            "create_transaction_record",
            AsyncMock(return_value={}),
        ):
            response = await module.upload_document(
                file=fake_file,
                current_user=current_user,
            )

        self.assertEqual(len(captured_blob_names), 1)
        blob_name = captured_blob_names[0]
        self.assertTrue(
            blob_name.startswith(f"users/{TEST_USER_ID}/documents/"),
            f"Expected GCS path to start with 'users/{TEST_USER_ID}/documents/', got: {blob_name}",
        )
        self.assertTrue(
            blob_name.endswith(".pdf"),
            f"Expected GCS path to end with '.pdf', got: {blob_name}",
        )
        self.assertEqual(response["status"], "uploaded")

    async def test_non_pdf_returns_400(self):
        module, http_exception_class, _, _ = load_upload_module()

        fake_file = module.UploadFile("invoice.txt", b"plain text")
        current_user = {"uid": TEST_USER_ID}

        with self.assertRaises(http_exception_class) as exc:
            await module.upload_document(
                file=fake_file,
                current_user=current_user,
            )

        self.assertEqual(exc.exception.status_code, 400)

    async def test_oversized_file_returns_400(self):
        module, http_exception_class, _, _ = load_upload_module()

        oversized = b"A" * (10 * 1024 * 1024 + 1)
        fake_file = module.UploadFile("big.pdf", oversized)
        current_user = {"uid": TEST_USER_ID}

        with self.assertRaises(http_exception_class) as exc:
            await module.upload_document(
                file=fake_file,
                current_user=current_user,
            )

        self.assertEqual(exc.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
