import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "app"
    / "routes"
    / "compliance.py"
)


def load_compliance_module():
    fake_fastapi = types.ModuleType("fastapi")
    fake_pydantic = types.ModuleType("pydantic")
    fake_app = types.ModuleType("app")
    fake_services = types.ModuleType("app.services")
    fake_compliance_service = types.ModuleType("app.services.compliance")
    fake_firestore = types.ModuleType("app.services.firestore")
    fake_auth = types.ModuleType("app.services.auth")

    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class APIRouter:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def post(self, _path):
            def decorator(func):
                return func
            return decorator

    def Depends(dependency):
        return dependency

    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    async def _placeholder_async(*_args, **_kwargs):
        raise AssertionError("Test should patch async dependency")

    def _placeholder_sync(*_args, **_kwargs):
        raise AssertionError("Test should patch sync dependency")

    fake_fastapi.APIRouter = APIRouter
    fake_fastapi.Depends = Depends
    fake_fastapi.HTTPException = HTTPException
    fake_pydantic.BaseModel = BaseModel

    fake_compliance_service.check_compliance = _placeholder_sync
    fake_firestore.get_transaction = _placeholder_async
    fake_firestore.save_compliance_result = _placeholder_async
    fake_auth.get_current_user = _placeholder_async

    fake_services.compliance = fake_compliance_service
    fake_services.firestore = fake_firestore
    fake_services.auth = fake_auth
    fake_app.services = fake_services

    fake_modules = {
        "fastapi": fake_fastapi,
        "pydantic": fake_pydantic,
        "app": fake_app,
        "app.services": fake_services,
        "app.services.compliance": fake_compliance_service,
        "app.services.firestore": fake_firestore,
        "app.services.auth": fake_auth,
    }

    module_name = "test_target_compliance_route"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, fake_modules):
        assert spec.loader is not None
        spec.loader.exec_module(module)

    return module, HTTPException


class FakeResult:
    def __init__(self, payload):
        self.payload = payload
        self.compliance_level = types.SimpleNamespace(value=payload["compliance_level"])
        self.missing_documents = payload["missing_documents"]

    def to_dict(self):
        return self.payload


class ComplianceRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_document_returns_404(self):
        module, http_exception_class = load_compliance_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=None),
        ):
            with self.assertRaises(http_exception_class) as exc:
                await module.run_compliance_check(
                    module.ComplianceRequest(document_id="doc-404"),
                    current_user={"uid": "test-user-1"},
                )

        self.assertEqual(exc.exception.status_code, 404)

    async def test_missing_extraction_returns_422(self):
        module, http_exception_class = load_compliance_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={"status": "uploaded", "extraction": None}),
        ):
            with self.assertRaises(http_exception_class) as exc:
                await module.run_compliance_check(
                    module.ComplianceRequest(document_id="doc-422"),
                    current_user={"uid": "test-user-1"},
                )

        self.assertEqual(exc.exception.status_code, 422)

    async def test_success_persists_compliance_only_fields(self):
        module, _ = load_compliance_module()
        compliance_payload = {
            "compliance_level": "MEDIUM",
            "gap_count": 1,
            "missing_documents": [{"code": "IN_MISSING_FORM_15CA"}],
            "warnings": [],
            "passed_checks": ["Commercial Invoice present"],
        }

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={"extraction": {"amount": 45000}}),
        ), patch.object(
            module,
            "check_compliance",
            return_value=FakeResult(compliance_payload),
        ), patch.object(
            module,
            "save_compliance_result",
            AsyncMock(),
        ) as save_compliance_result:
            response = await module.run_compliance_check(
                module.ComplianceRequest(document_id="doc-1"),
                current_user={"uid": "test-user-1"},
            )

        save_compliance_result.assert_awaited_once_with(
            "doc-1",
            compliance_payload,
            user_id="test-user-1",
        )
        # Explicit propagation assertion — user_id must reach save_compliance_result
        self.assertEqual(
            save_compliance_result.call_args.kwargs["user_id"], "test-user-1"
        )
        self.assertEqual(response["status"], "compliance_checked")
        self.assertEqual(response["compliance_level"], "MEDIUM")
        self.assertEqual(response["gap_count"], 1)

    async def test_checker_error_returns_500(self):
        module, http_exception_class = load_compliance_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={"extraction": {"amount": 100}}),
        ), patch.object(
            module,
            "check_compliance",
            side_effect=RuntimeError("boom"),
        ):
            with self.assertRaises(http_exception_class) as exc:
                await module.run_compliance_check(
                    module.ComplianceRequest(document_id="doc-err"),
                    current_user={"uid": "test-user-1"},
                )

        self.assertEqual(exc.exception.status_code, 500)
        self.assertEqual(
            exc.exception.detail,
            "Compliance check failed due to an internal error.",
        )

    async def test_persistence_error_returns_500(self):
        module, http_exception_class = load_compliance_module()
        compliance_payload = {
            "compliance_level": "HIGH",
            "gap_count": 0,
            "missing_documents": [],
            "warnings": [],
            "passed_checks": [],
        }

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={"extraction": {"amount": 100}}),
        ), patch.object(
            module,
            "check_compliance",
            return_value=FakeResult(compliance_payload),
        ), patch.object(
            module,
            "save_compliance_result",
            AsyncMock(side_effect=RuntimeError("db write failed")),
        ):
            with self.assertRaises(http_exception_class) as exc:
                await module.run_compliance_check(
                    module.ComplianceRequest(document_id="doc-db-fail"),
                    current_user={"uid": "test-user-1"},
                )

        self.assertEqual(exc.exception.status_code, 500)
        self.assertEqual(
            exc.exception.detail,
            "Compliance result could not be saved.",
        )


    async def test_compliance_short_circuits_when_already_compliance_checked(self):
        module, _ = load_compliance_module()

        stored_compliance = {
            "compliance_level": "LOW",
            "gap_count": 0,
            "missing_documents": [],
            "warnings": [],
            "passed_checks": ["Commercial Invoice present"],
        }
        transaction = {
            "status": "compliance_checked",
            "extraction": {"fields": {"invoice_amount": {"value": "2500"}}},
            "compliance": stored_compliance,
        }

        save_mock = AsyncMock()
        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module, "save_compliance_result", save_mock
        ):
            response = await module.run_compliance_check(
                module.ComplianceRequest(document_id="doc-cc"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "already_checked")
        self.assertEqual(response["compliance_level"], stored_compliance["compliance_level"])
        self.assertEqual(response["missing_documents"], stored_compliance["missing_documents"])
        self.assertEqual(response["gap_count"], stored_compliance["gap_count"])
        save_mock.assert_not_called()

    async def test_compliance_short_circuits_when_already_routed(self):
        module, _ = load_compliance_module()

        stored_compliance = {
            "compliance_level": "MEDIUM",
            "gap_count": 1,
            "missing_documents": [{"code": "US_MISSING_ISF"}],
            "warnings": [],
            "passed_checks": [],
        }
        transaction = {
            "status": "routed",
            "extraction": {"fields": {"invoice_amount": {"value": "2500"}}},
            "compliance": stored_compliance,
        }

        save_mock = AsyncMock()
        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module, "save_compliance_result", save_mock
        ):
            response = await module.run_compliance_check(
                module.ComplianceRequest(document_id="doc-routed"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "already_checked")
        self.assertEqual(response["compliance_level"], stored_compliance["compliance_level"])
        self.assertEqual(response["missing_documents"], stored_compliance["missing_documents"])
        self.assertEqual(response["gap_count"], stored_compliance["gap_count"])
        save_mock.assert_not_called()

    async def test_compliance_runs_on_routed_doc_without_stored_compliance(self):
        module, _ = load_compliance_module()

        transaction = {
            "status": "routed",
            "extraction": {
                "fields": {"invoice_amount": {"value": "5000"}}
            },
            # no "compliance" key — doc went uploaded -> extracted ->
            # analyzed -> routed, skipping /compliance. A follow-up
            # /compliance call must be allowed to backfill.
        }

        fresh_result = {
            "compliance_level": "HIGH",
            "gap_count": 0,
            "missing_documents": [],
            "warnings": [],
            "passed_checks": ["Commercial Invoice present"],
        }

        class FakeComplianceResult:
            def to_dict(self):
                return fresh_result

            compliance_level = type(
                "Level", (), {"value": "HIGH"}
            )()
            missing_documents = []

        check_mock = MagicMock(return_value=FakeComplianceResult())
        save_mock = AsyncMock()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module, "check_compliance", check_mock
        ), patch.object(
            module, "save_compliance_result", save_mock
        ):
            response = await module.run_compliance_check(
                module.ComplianceRequest(document_id="doc-routed-backfill"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "compliance_checked")
        self.assertEqual(response["compliance_level"], "HIGH")
        check_mock.assert_called_once()
        save_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
