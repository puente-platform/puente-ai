# backend/tests/test_onboarding.py
"""
13 unit tests for POST /api/v1/onboarding and GET /api/v1/onboarding.

Uses the fake-module injection pattern from test_upload_route.py and
test_compliance_route.py so heavy GCP/Firebase deps are never imported.

The Pydantic models (app.models.onboarding) are imported directly — they
have no GCP dependencies and are testable without mocking.
"""
import importlib.util
import os
import pathlib
import sys
import types
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers to import the real Pydantic models without any GCP deps
# ---------------------------------------------------------------------------

_BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND_DIR))

from app.models.onboarding import OnboardingProfileIn, OnboardingProfileOut  # noqa: E402

# ---------------------------------------------------------------------------
# Module loader — injects fakes for everything the route imports from GCP
# ---------------------------------------------------------------------------

MODULE_PATH = _BACKEND_DIR / "app" / "routes" / "onboarding.py"


class _HTTPException(Exception):
    def __init__(self, status_code: int, detail: str = ""):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _make_fake_doc(data: dict | None, exists: bool = True):
    snap = MagicMock()
    snap.exists = exists
    snap.to_dict.return_value = data if exists else None
    return snap


def load_onboarding_module():
    """
    Load app.routes.onboarding with all GCP / Firebase deps stubbed out.
    Returns (module, HTTPException_class, FakeResponse_class).
    """
    fake_fastapi = types.ModuleType("fastapi")
    fake_fastapi_responses = types.ModuleType("fastapi.responses")
    fake_app = types.ModuleType("app")
    fake_services = types.ModuleType("app.services")
    fake_auth_mod = types.ModuleType("app.services.auth")
    fake_firestore_svc = types.ModuleType("app.services.firestore")
    fake_models = types.ModuleType("app.models")
    fake_models_onboarding = types.ModuleType("app.models.onboarding")
    fake_google = types.ModuleType("google")
    fake_cloud = types.ModuleType("google.cloud")
    fake_fs = types.ModuleType("google.cloud.firestore")

    # Sentinel objects the route uses
    fake_fs.DELETE_FIELD = "___DELETE___"
    fake_fs.SERVER_TIMESTAMP = "___SERVER_TS___"

    # Pass-through transactional decorator so unit tests bypass real
    # Firestore transaction wiring. Production uses the real decorator,
    # which provides atomic read-decide-write + automatic retry.
    def _passthrough_transactional(func):
        return func
    fake_fs.transactional = _passthrough_transactional

    class FakeAPIRouter:
        def __init__(self, *args, **kwargs):
            pass

        def post(self, path, **kw):
            def decorator(fn):
                return fn
            return decorator

        def get(self, path, **kw):
            def decorator(fn):
                return fn
            return decorator

    class _Status:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_404_NOT_FOUND = 404
        HTTP_500_INTERNAL_SERVER_ERROR = 500

    class FakeResponse:
        """Simulates FastAPI's Response object (used to override status code)."""
        def __init__(self):
            self.status_code: int | None = None

    fake_fastapi.APIRouter = FakeAPIRouter
    fake_fastapi.Depends = lambda dep: dep
    fake_fastapi.HTTPException = _HTTPException
    fake_fastapi.Response = FakeResponse
    fake_fastapi.status = _Status

    async def _fake_get_current_user():
        raise AssertionError("Patch get_current_user per test")

    fake_auth_mod.get_current_user = _fake_get_current_user

    def _fake_get_firestore_client():
        raise AssertionError("Patch get_firestore_client per test")

    fake_firestore_svc.get_firestore_client = _fake_get_firestore_client

    # Wire real Pydantic models so the route's type annotations work
    fake_models_onboarding.OnboardingProfileIn = OnboardingProfileIn
    fake_models_onboarding.OnboardingProfileOut = OnboardingProfileOut

    fake_services.auth = fake_auth_mod
    fake_services.firestore = fake_firestore_svc
    fake_models.onboarding = fake_models_onboarding
    fake_app.services = fake_services
    fake_app.models = fake_models
    fake_cloud.firestore = fake_fs
    fake_google.cloud = fake_cloud

    fake_modules = {
        "fastapi": fake_fastapi,
        "fastapi.responses": fake_fastapi_responses,
        "app": fake_app,
        "app.services": fake_services,
        "app.services.auth": fake_auth_mod,
        "app.services.firestore": fake_firestore_svc,
        "app.models": fake_models,
        "app.models.onboarding": fake_models_onboarding,
        "google": fake_google,
        "google.cloud": fake_cloud,
        "google.cloud.firestore": fake_fs,
    }

    mod_name = "test_target_onboarding_route"
    if mod_name in sys.modules:
        del sys.modules[mod_name]

    spec = importlib.util.spec_from_file_location(mod_name, MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, fake_modules, clear=False):
        assert spec.loader is not None
        spec.loader.exec_module(mod)

    return mod, _HTTPException, FakeResponse


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_FULL_DOC = {
    "displayName": "Maria Garcia",
    "company": "LT Inc",
    "corridors": ["mia-bog", "mia-sdq"],
    "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
    "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
    "completedAt": None,
}


def _make_db_mock(existing_data=None, exists=True):
    """Return (db, doc_ref) — doc_ref.get returns the specified snapshot.

    db.transaction() returns a Mock whose .set(doc_ref, payload, merge=True)
    is forwarded to doc_ref.set(payload, merge=True). This keeps existing
    assertions on doc_ref.set.call_args working after the bug_003 refactor
    (writes now go through the transaction object, not directly on doc_ref)."""
    db = MagicMock()
    doc_ref = MagicMock()
    snap = _make_fake_doc(existing_data, exists=exists)
    doc_ref.get = MagicMock(return_value=snap)
    doc_ref.set = MagicMock(return_value=None)
    db.collection.return_value.document.return_value = doc_ref

    transaction = MagicMock()
    transaction.set = lambda dr, payload, merge=True: doc_ref.set(payload, merge=merge)
    db.transaction = MagicMock(return_value=transaction)

    return db, doc_ref


# ---------------------------------------------------------------------------
# 1. test_post_onboarding_creates_record
# ---------------------------------------------------------------------------

class TestPostOnboardingCreatesRecord(unittest.IsolatedAsyncioTestCase):
    """201 on first write."""

    async def test_post_onboarding_creates_record(self):
        mod, _, FakeResponse = load_onboarding_module()

        db, doc_ref = _make_db_mock(existing_data=None, exists=False)
        after_write_snap = _make_fake_doc({
            "displayName": "Maria Garcia",
            "company": "LT Inc",
            "corridors": ["mia-bog"],
            "createdAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
            "completedAt": None,
        })
        doc_ref.get = MagicMock(side_effect=[
            _make_fake_doc(None, exists=False),
            after_write_snap,
        ])

        body = OnboardingProfileIn(
            displayName="Maria Garcia",
            company="LT Inc",
            corridors=["mia-bog"],
        )
        resp = FakeResponse()
        with patch.object(mod, "get_firestore_client", return_value=db):
            result = await mod.upsert_onboarding_profile(body, {"uid": "test-uid-001"}, resp)

        # First write: response.status_code is NOT overridden to 200 (decorator provides 201)
        self.assertIsInstance(result, OnboardingProfileOut)
        self.assertEqual(result.displayName, "Maria Garcia")
        self.assertIsNotNone(result.createdAt)
        self.assertNotEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# 2. test_post_onboarding_updates_existing
# ---------------------------------------------------------------------------

class TestPostOnboardingUpdatesExisting(unittest.IsolatedAsyncioTestCase):
    """200 on second write (response.status_code overridden to 200)."""

    async def test_post_onboarding_updates_existing(self):
        mod, _, FakeResponse = load_onboarding_module()

        existing = {**_FULL_DOC}
        after_write_snap = _make_fake_doc({
            **existing,
            "displayName": "Maria Updated",
            "updatedAt": datetime(2026, 4, 30, 12, 0, 0, tzinfo=timezone.utc),
        })

        db, doc_ref = _make_db_mock(existing_data=existing, exists=True)
        doc_ref.get = MagicMock(side_effect=[
            _make_fake_doc(existing, exists=True),
            after_write_snap,
        ])

        body = OnboardingProfileIn(displayName="Maria Updated")
        resp = FakeResponse()
        with patch.object(mod, "get_firestore_client", return_value=db):
            result = await mod.upsert_onboarding_profile(body, {"uid": "test-uid-001"}, resp)

        self.assertIsInstance(result, OnboardingProfileOut)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result.displayName, "Maria Updated")


# ---------------------------------------------------------------------------
# 3. test_post_onboarding_invalid_corridor
# ---------------------------------------------------------------------------

class TestPostOnboardingInvalidCorridor(unittest.IsolatedAsyncioTestCase):
    """Unknown corridor ID raises Pydantic ValidationError (becomes 400 via FastAPI)."""

    def test_post_onboarding_invalid_corridor(self):
        with self.assertRaises(Exception) as ctx:
            OnboardingProfileIn(corridors=["mia-bog", "mia-xyz-unknown"])
        self.assertIn("corridors", str(ctx.exception).lower())


# ---------------------------------------------------------------------------
# 4. test_post_onboarding_rejects_uid_in_body
# ---------------------------------------------------------------------------

class TestPostOnboardingRejectsUidInBody(unittest.IsolatedAsyncioTestCase):
    """uid/userId/sub in body → ValidationError (becomes 400)."""

    def test_rejects_uid(self):
        with self.assertRaises(Exception) as ctx:
            OnboardingProfileIn.model_validate({"uid": "injected-uid"})
        self.assertIn("uid", str(ctx.exception))

    def test_rejects_userId(self):
        with self.assertRaises(Exception) as ctx:
            OnboardingProfileIn.model_validate({"userId": "injected-userId"})
        self.assertIn("userId", str(ctx.exception))

    def test_rejects_sub(self):
        with self.assertRaises(Exception) as ctx:
            OnboardingProfileIn.model_validate({"sub": "injected-sub"})
        self.assertIn("sub", str(ctx.exception))


# ---------------------------------------------------------------------------
# 5. test_post_onboarding_ignores_client_completedAt
# ---------------------------------------------------------------------------

class TestPostOnboardingIgnoresClientCompletedAt(unittest.IsolatedAsyncioTestCase):
    """
    completedAt is not a field on OnboardingProfileIn.
    Even a malicious client sending completedAt in JSON will have it dropped at
    the Pydantic boundary — it never reaches Firestore through the body.
    """

    def test_completedAt_not_a_field_on_input_model(self):
        self.assertNotIn("completedAt", OnboardingProfileIn.model_fields)

    def test_client_completedAt_is_dropped_at_pydantic_boundary(self):
        profile = OnboardingProfileIn.model_validate(
            {"displayName": "Test", "completedAt": "2020-01-01T00:00:00Z"}
        )
        self.assertFalse(hasattr(profile, "completedAt"))


# ---------------------------------------------------------------------------
# 6. test_post_onboarding_markComplete_sets_completedAt_once
# ---------------------------------------------------------------------------

class TestPostOnboardingMarkCompleteOnce(unittest.IsolatedAsyncioTestCase):
    """
    First markComplete=True stamps completedAt.
    Second markComplete=True is a no-op (immutability guarantee).
    """

    async def test_first_markComplete_sets_completedAt(self):
        mod, _, FakeResponse = load_onboarding_module()

        existing = {
            "displayName": "Alice",
            "company": "Corp",
            "corridors": [],
            "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "completedAt": None,
        }
        after_snap = _make_fake_doc({
            **existing,
            "completedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
        })

        db, doc_ref = _make_db_mock(existing_data=existing, exists=True)
        doc_ref.get = MagicMock(side_effect=[
            _make_fake_doc(existing, exists=True),
            after_snap,
        ])

        body = OnboardingProfileIn(markComplete=True)
        resp = FakeResponse()
        with patch.object(mod, "get_firestore_client", return_value=db):
            await mod.upsert_onboarding_profile(body, {"uid": "uid-alice"}, resp)

        set_call_args = doc_ref.set.call_args[0][0]
        self.assertIn("completedAt", set_call_args)
        self.assertEqual(set_call_args["completedAt"], mod.fs.SERVER_TIMESTAMP)

    async def test_upsert_runs_inside_firestore_transaction(self):
        # bug_003 from ultrareview: read-decide-write for completedAt was a
        # TOCTOU race. The handler now wraps the read+write in a Firestore
        # transaction so two concurrent markComplete:true requests cannot
        # both observe absent and both stamp SERVER_TIMESTAMP. This test
        # verifies the transaction is actually invoked — atomicity itself
        # is provided by Firestore at runtime, not testable in unit mocks.
        mod, _, FakeResponse = load_onboarding_module()
        db, doc_ref = _make_db_mock(existing_data=None, exists=False)
        after_snap = _make_fake_doc({
            "displayName": "Maria",
            "createdAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
            "completedAt": None,
        })
        doc_ref.get = MagicMock(side_effect=[
            _make_fake_doc(None, exists=False),
            after_snap,
        ])

        body = OnboardingProfileIn(displayName="Maria")
        resp = FakeResponse()
        with patch.object(mod, "get_firestore_client", return_value=db):
            await mod.upsert_onboarding_profile(body, {"uid": "uid-maria"}, resp)

        # The route must request a transaction from the Firestore client.
        db.transaction.assert_called_once()

    async def test_second_markComplete_is_noop_on_completedAt(self):
        mod, _, FakeResponse = load_onboarding_module()

        existing = {
            "displayName": "Alice",
            "company": "Corp",
            "corridors": [],
            "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "completedAt": datetime(2026, 4, 15, tzinfo=timezone.utc),  # already stamped
        }
        after_snap = _make_fake_doc({
            **existing,
            "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
        })

        db, doc_ref = _make_db_mock(existing_data=existing, exists=True)
        doc_ref.get = MagicMock(side_effect=[
            _make_fake_doc(existing, exists=True),
            after_snap,
        ])

        body = OnboardingProfileIn(markComplete=True)
        resp = FakeResponse()
        with patch.object(mod, "get_firestore_client", return_value=db):
            await mod.upsert_onboarding_profile(body, {"uid": "uid-alice"}, resp)

        set_call_args = doc_ref.set.call_args[0][0]
        self.assertNotIn("completedAt", set_call_args)


# ---------------------------------------------------------------------------
# 7. test_post_omitted_field_preserves_existing
# ---------------------------------------------------------------------------

class TestPostOmittedFieldPreservesExisting(unittest.IsolatedAsyncioTestCase):
    """
    POST {displayName: "X"} must not clear company or corridors.
    Only fields in model_fields_set appear in the Firestore write payload.
    """

    async def test_omitted_fields_not_in_write_payload(self):
        mod, _, FakeResponse = load_onboarding_module()

        existing = {
            "displayName": "Old Name",
            "company": "Old Corp",
            "corridors": ["mia-bog"],
            "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "completedAt": None,
        }
        after_snap = _make_fake_doc({
            **existing,
            "displayName": "New Name",
            "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
        })

        db, doc_ref = _make_db_mock(existing_data=existing, exists=True)
        doc_ref.get = MagicMock(side_effect=[
            _make_fake_doc(existing, exists=True),
            after_snap,
        ])

        body = OnboardingProfileIn(displayName="New Name")
        # Confirm company and corridors are NOT in model_fields_set
        self.assertNotIn("company", body.model_fields_set)
        self.assertNotIn("corridors", body.model_fields_set)

        resp = FakeResponse()
        with patch.object(mod, "get_firestore_client", return_value=db):
            await mod.upsert_onboarding_profile(body, {"uid": "uid-partial"}, resp)

        set_call_args = doc_ref.set.call_args[0][0]
        self.assertNotIn("company", set_call_args)
        self.assertNotIn("corridors", set_call_args)
        self.assertIn("displayName", set_call_args)


# ---------------------------------------------------------------------------
# 8. test_post_null_field_clears_existing
# ---------------------------------------------------------------------------

class TestPostNullFieldClearsExisting(unittest.IsolatedAsyncioTestCase):
    """
    POST {company: null} writes DELETE_FIELD sentinel to Firestore,
    which removes the field from the document.
    """

    async def test_explicit_null_writes_delete_field(self):
        mod, _, FakeResponse = load_onboarding_module()

        existing = {
            "displayName": "Maria",
            "company": "Old Corp",
            "corridors": ["mia-bog"],
            "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "completedAt": None,
        }
        after_snap = _make_fake_doc({
            "displayName": "Maria",
            "corridors": ["mia-bog"],
            "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
            "completedAt": None,
        })

        db, doc_ref = _make_db_mock(existing_data=existing, exists=True)
        doc_ref.get = MagicMock(side_effect=[
            _make_fake_doc(existing, exists=True),
            after_snap,
        ])

        # company=None explicitly set → it's in model_fields_set
        body = OnboardingProfileIn.model_validate({"company": None})
        self.assertIn("company", body.model_fields_set)
        self.assertIsNone(body.company)

        resp = FakeResponse()
        with patch.object(mod, "get_firestore_client", return_value=db):
            await mod.upsert_onboarding_profile(body, {"uid": "uid-delete"}, resp)

        set_call_args = doc_ref.set.call_args[0][0]
        self.assertIn("company", set_call_args)
        self.assertEqual(set_call_args["company"], mod.fs.DELETE_FIELD)


# ---------------------------------------------------------------------------
# 9. test_post_onboarding_validates_displayName_charset
# ---------------------------------------------------------------------------

class TestPostOnboardingValidatesDisplayNameCharset(unittest.IsolatedAsyncioTestCase):
    """
    - Control char \\x07 → rejected
    - Length 81 → rejected
    - Valid NFKC-normalized string → passes
    - Pre-NFKC fullwidth character → normalized (not rejected)
    """

    def test_rejects_control_char(self):
        with self.assertRaises(Exception):
            OnboardingProfileIn(displayName="Valid\x07Name")

    def test_rejects_length_81(self):
        with self.assertRaises(Exception):
            OnboardingProfileIn(displayName="A" * 81)

    def test_valid_name_passes(self):
        profile = OnboardingProfileIn(displayName="Maria García")
        self.assertEqual(profile.displayName, "Maria García")

    def test_nfkc_normalization_applied(self):
        # Fullwidth Latin capital A (U+FF21) → plain 'A' under NFKC
        profile = OnboardingProfileIn(displayName="Ａlice")
        self.assertEqual(profile.displayName, "Alice")

    def test_nfkc_expansion_rejected_when_post_normalize_exceeds_max_length(self):
        # bug_004 from ultrareview: NFKC expansion (e.g. U+FB03 'ﬃ' → 'ffi')
        # used to bypass max_length=80 because length validation ran BEFORE
        # normalization. After the fix, normalization runs mode='before' and
        # StringConstraints sees the post-normalization length.
        # 30 × U+FB03 = 30 raw chars → 90 chars after NFKC (> 80 max).
        ffi_ligature = "ﬃ" * 30  # noqa: do-not-log-pii (test data)
        with self.assertRaises(Exception):
            OnboardingProfileIn(displayName=ffi_ligature)

    def test_nfkc_expansion_company_rejected_when_post_normalize_exceeds_max(self):
        # Same bug, company field. U+FDFA (Arabic ligature) → 18 chars under NFKC.
        # 120 × U+FDFA = 120 raw chars → 2160 chars after NFKC (> 120 max).
        arabic_ligature = "ﷺ" * 120  # noqa: do-not-log-pii (test data)
        with self.assertRaises(Exception):
            OnboardingProfileIn(company=arabic_ligature)


# ---------------------------------------------------------------------------
# 10. test_post_onboarding_missing_auth
# ---------------------------------------------------------------------------

class TestPostOnboardingMissingAuth(unittest.IsolatedAsyncioTestCase):
    """
    Verifies the handler signature wires get_current_user dependency.
    The actual 401 response is enforced by the auth service (tested in test_auth.py).
    """

    def test_handler_has_current_user_parameter(self):
        import inspect
        mod, _, _ = load_onboarding_module()
        sig = inspect.signature(mod.upsert_onboarding_profile)
        self.assertIn("current_user", sig.parameters)

    def test_get_handler_has_current_user_parameter(self):
        import inspect
        mod, _, _ = load_onboarding_module()
        sig = inspect.signature(mod.get_onboarding_profile)
        self.assertIn("current_user", sig.parameters)


# ---------------------------------------------------------------------------
# 11. test_get_onboarding_returns_record
# ---------------------------------------------------------------------------

class TestGetOnboardingReturnsRecord(unittest.IsolatedAsyncioTestCase):
    """GET returns 200 + OnboardingProfileOut when profile exists."""

    async def test_returns_profile(self):
        mod, _, _ = load_onboarding_module()

        doc_data = {
            "displayName": "Maria Garcia",
            "company": "LT Inc",
            "corridors": ["mia-bog", "mia-sdq"],
            "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
            "completedAt": datetime(2026, 4, 30, tzinfo=timezone.utc),
        }

        db = MagicMock()
        doc_ref = MagicMock()
        doc_ref.get = MagicMock(return_value=_make_fake_doc(doc_data))
        db.collection.return_value.document.return_value = doc_ref

        with patch.object(mod, "get_firestore_client", return_value=db):
            result = await mod.get_onboarding_profile({"uid": "test-uid-001"})

        self.assertIsInstance(result, OnboardingProfileOut)
        self.assertEqual(result.displayName, "Maria Garcia")
        self.assertEqual(result.company, "LT Inc")
        self.assertIsNotNone(result.completedAt)


# ---------------------------------------------------------------------------
# 12. test_get_onboarding_404_when_empty
# ---------------------------------------------------------------------------

class TestGetOnboarding404WhenEmpty(unittest.IsolatedAsyncioTestCase):
    """GET returns 404 before any POST."""

    async def test_returns_404(self):
        mod, HTTPException, _ = load_onboarding_module()

        db = MagicMock()
        doc_ref = MagicMock()
        doc_ref.get = MagicMock(return_value=_make_fake_doc(None, exists=False))
        db.collection.return_value.document.return_value = doc_ref

        with patch.object(mod, "get_firestore_client", return_value=db):
            with self.assertRaises(_HTTPException) as ctx:
                await mod.get_onboarding_profile({"uid": "unknown-uid"})

        self.assertEqual(ctx.exception.status_code, 404)


# ---------------------------------------------------------------------------
# 13. test_get_onboarding_cross_tenant_isolated
# ---------------------------------------------------------------------------

class TestGetOnboardingCrossTenantIsolated(unittest.IsolatedAsyncioTestCase):
    """
    uid from the token is the ONLY uid used in the Firestore path.
    No URL parameter or body field can redirect the lookup to another user's doc.
    """

    async def test_get_uses_token_uid_only(self):
        mod, _, _ = load_onboarding_module()

        doc_data = {
            "displayName": "Alice",
            "company": "AliceCo",
            "corridors": [],
            "createdAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "completedAt": None,
        }

        call_log: list[str] = []

        db = MagicMock()
        doc_ref = MagicMock()
        doc_ref.get = MagicMock(return_value=_make_fake_doc(doc_data))

        def _collection(name):
            coll = MagicMock()
            def _document(uid):
                call_log.append(uid)
                return doc_ref
            coll.document = _document
            return coll

        db.collection = _collection

        current_user = {"uid": "uid-alice"}
        with patch.object(mod, "get_firestore_client", return_value=db):
            await mod.get_onboarding_profile(current_user)

        self.assertEqual(call_log, ["uid-alice"])
        self.assertNotIn("uid-bob", call_log)


if __name__ == "__main__":
    unittest.main()
