import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


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

    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class APIRouter:
        def post(self, _path):
            def decorator(func):
                return func
            return decorator

    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    async def _placeholder_async(*_args, **_kwargs):
        raise AssertionError("Test should patch async dependency")

    def _placeholder_sync(*_args, **_kwargs):
        raise AssertionError("Test should patch sync dependency")

    fake_fastapi.APIRouter = APIRouter
    fake_fastapi.HTTPException = HTTPException
    fake_pydantic.BaseModel = BaseModel

    fake_compliance_service.check_compliance = _placeholder_sync
    fake_firestore.get_transaction = _placeholder_async
    fake_firestore.save_compliance_result = _placeholder_async

    fake_services.compliance = fake_compliance_service
    fake_services.firestore = fake_firestore
    fake_app.services = fake_services

    fake_modules = {
        "fastapi": fake_fastapi,
        "pydantic": fake_pydantic,
        "app": fake_app,
        "app.services": fake_services,
        "app.services.compliance": fake_compliance_service,
        "app.services.firestore": fake_firestore,
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
                    module.ComplianceRequest(document_id="doc-404")
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
                    module.ComplianceRequest(document_id="doc-422")
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
                module.ComplianceRequest(document_id="doc-1")
            )

        save_compliance_result.assert_awaited_once_with(
            "doc-1",
            compliance_payload,
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
                    module.ComplianceRequest(document_id="doc-err")
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
                    module.ComplianceRequest(document_id="doc-db-fail")
                )

        self.assertEqual(exc.exception.status_code, 500)
        self.assertEqual(
            exc.exception.detail,
            "Compliance result could not be saved.",
        )


if __name__ == "__main__":
    unittest.main()
