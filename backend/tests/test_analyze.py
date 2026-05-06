import importlib.util
import os
import pathlib
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "app"
    / "routes"
    / "analyze.py"
)


def load_analyze_module():
    fake_fastapi = types.ModuleType("fastapi")
    fake_pydantic = types.ModuleType("pydantic")
    fake_starlette_concurrency = types.ModuleType(
        "starlette.concurrency"
    )
    fake_app = types.ModuleType("app")
    fake_services = types.ModuleType("app.services")
    fake_document_ai = types.ModuleType("app.services.document_ai")
    fake_firestore = types.ModuleType("app.services.firestore")
    fake_gemini = types.ModuleType("app.services.gemini")
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

    async def run_in_threadpool(func, *args, **kwargs):
        return func(*args, **kwargs)

    async def _placeholder_async(*_args, **_kwargs):
        raise AssertionError("Test should patch async dependency")

    def _placeholder_sync(*_args, **_kwargs):
        raise AssertionError("Test should patch sync dependency")

    fake_fastapi.APIRouter = APIRouter
    fake_fastapi.Depends = Depends
    fake_fastapi.HTTPException = HTTPException
    fake_pydantic.BaseModel = BaseModel
    fake_starlette_concurrency.run_in_threadpool = run_in_threadpool

    fake_document_ai.extract_invoice_data = _placeholder_sync
    fake_gemini.analyze_trade_document = _placeholder_sync
    fake_firestore.get_transaction = _placeholder_async
    fake_firestore.update_transaction_status = _placeholder_async
    fake_firestore.save_extraction = _placeholder_async
    fake_firestore.save_analysis = _placeholder_async
    fake_auth.get_current_user = _placeholder_async

    fake_services.document_ai = fake_document_ai
    fake_services.firestore = fake_firestore
    fake_services.gemini = fake_gemini
    fake_services.auth = fake_auth
    fake_app.services = fake_services

    fake_modules = {
        "fastapi": fake_fastapi,
        "pydantic": fake_pydantic,
        "starlette.concurrency": fake_starlette_concurrency,
        "app": fake_app,
        "app.services": fake_services,
        "app.services.document_ai": fake_document_ai,
        "app.services.firestore": fake_firestore,
        "app.services.gemini": fake_gemini,
        "app.services.auth": fake_auth,
    }

    module_name = "test_target_analyze"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, fake_modules):
        assert spec.loader is not None
        spec.loader.exec_module(module)

    return module, HTTPException


class AnalyzeRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_already_analyzed_returns_cached_payload(self):
        module, _ = load_analyze_module()

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(
                return_value={
                    "status": "analyzed",
                    "extraction": {"fields": {}},
                    "full_analysis": {"fraud_assessment": {"score": 5}},
                }
            ),
        ), patch.object(
            module,
            "update_transaction_status",
            AsyncMock(),
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-1"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "already_analyzed")
        self.assertEqual(
            response["analysis"]["fraud_assessment"]["score"],
            5,
        )

    async def test_reuses_saved_extraction_and_skips_document_ai(self):
        module, _ = load_analyze_module()
        extraction = {"fields": {"invoice_amount": {"value": "500"}}}
        analysis = {"fraud_assessment": {"score": 20}}

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(
                return_value={
                    "status": "failed",
                    "extraction": extraction,
                }
            ),
        ) as get_transaction, patch.object(
            module,
            "update_transaction_status",
            AsyncMock(),
        ) as update_status, patch.object(
            module,
            "save_extraction",
            AsyncMock(),
        ) as save_extraction, patch.object(
            module,
            "save_analysis",
            AsyncMock(),
        ) as save_analysis, patch.object(
            module,
            "extract_invoice_data",
            side_effect=AssertionError("Document AI should not run"),
        ), patch.object(
            module,
            "analyze_trade_document",
            return_value=analysis,
        ) as analyze_trade_document:
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-2"),
                current_user={"uid": "test-user-1"},
            )

        # Read-side isolation: the initial get_transaction must receive
        # user_id so the Firestore lookup is scoped to the authenticated
        # user's subcollection. A missing user_id on the read path would
        # let another tenant's doc leak in before any write-side check.
        get_transaction.assert_awaited_once_with("doc-2", user_id="test-user-1")
        self.assertEqual(
            get_transaction.call_args.kwargs["user_id"], "test-user-1"
        )

        update_status.assert_awaited_once_with(
            "doc-2", "processing", user_id="test-user-1"
        )
        save_extraction.assert_not_called()
        analyze_trade_document.assert_called_once()
        save_analysis.assert_awaited_once_with(
            "doc-2", analysis, user_id="test-user-1"
        )
        # Explicit propagation assertion — user_id must reach save_analysis
        self.assertEqual(
            save_analysis.call_args.kwargs["user_id"], "test-user-1"
        )
        self.assertEqual(response["status"], "analyzed")
        self.assertEqual(response["analysis"], analysis)

    async def test_missing_extraction_runs_document_ai_then_gemini(self):
        module, _ = load_analyze_module()
        extraction = {"fields": {"invoice_id": {"value": "INV-1"}}}
        analysis = {"fraud_assessment": {"score": 12}}

        with patch.dict(
            os.environ,
            {
                "GCS_BUCKET_NAME": "puente-docs",
                "DOCUMENT_AI_PROCESSOR_ID": "processor-1",
                "GCP_PROJECT_ID": "demo-project",
            },
            clear=True,
        ), patch.object(
            module,
            "get_transaction",
            AsyncMock(
                return_value={
                    "status": "uploaded",
                    "blob_name": "invoices/doc-3.pdf",
                }
            ),
        ), patch.object(
            module,
            "update_transaction_status",
            AsyncMock(),
        ) as update_status, patch.object(
            module,
            "save_extraction",
            AsyncMock(),
        ) as save_extraction, patch.object(
            module,
            "save_analysis",
            AsyncMock(),
        ) as save_analysis, patch.object(
            module,
            "extract_invoice_data",
            return_value=extraction,
        ) as extract_invoice_data, patch.object(
            module,
            "analyze_trade_document",
            return_value=analysis,
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-3"),
                current_user={"uid": "test-user-1"},
            )

        update_status.assert_awaited_once_with(
            "doc-3", "processing", user_id="test-user-1"
        )
        extract_invoice_data.assert_called_once_with(
            "gs://puente-docs/invoices/doc-3.pdf"
        )
        save_extraction.assert_awaited_once()
        saved_extraction = save_extraction.await_args.args[1]
        self.assertEqual(saved_extraction["document_id"], "doc-3")
        # Verify user_id propagated to save_extraction
        self.assertEqual(
            save_extraction.call_args.kwargs["user_id"], "test-user-1"
        )
        save_analysis.assert_awaited_once_with(
            "doc-3", analysis, user_id="test-user-1"
        )
        self.assertEqual(response["status"], "analyzed")

    async def test_inferred_fields_merge_into_extraction_for_routing(self):
        """KAN-48 Task 3c: Gemini-inferred seller_country/incoterms/
        country_of_origin merge into extraction.fields when Document AI
        didn't extract them. Routing reads extraction.fields.seller_country
        from Firestore, so the merged extraction must be persisted.
        """
        module, _ = load_analyze_module()
        extraction = {
            "fields": {
                "invoice_id": {"value": "DA-2026-00847"},
                "invoice_amount": {"value": "91324.20"},
            },
        }
        analysis = {
            "fraud_assessment": {"score": 12, "flags": []},
            "inferred_fields": {
                "seller_country": "CO",
                "incoterms": "FOB Bogotá",
                "country_of_origin": "Various (see items)",
                "inference_evidence": "supplier address Bogotá, Colombia",
            },
        }

        with patch.dict(
            os.environ,
            {
                "GCS_BUCKET_NAME": "puente-docs",
                "DOCUMENT_AI_PROCESSOR_ID": "processor-1",
                "GCP_PROJECT_ID": "demo-project",
            },
            clear=True,
        ), patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value={
                "status": "uploaded",
                "blob_name": "invoices/doc-9.pdf",
            }),
        ), patch.object(
            module, "update_transaction_status", AsyncMock(),
        ), patch.object(
            module, "save_extraction", AsyncMock(),
        ) as save_extraction, patch.object(
            module, "save_analysis", AsyncMock(),
        ), patch.object(
            module, "extract_invoice_data", return_value=extraction,
        ), patch.object(
            module, "analyze_trade_document", return_value=analysis,
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-9"),
                current_user={"uid": "test-user-1"},
            )

        merged = response["extraction"]
        self.assertEqual(merged["fields"]["seller_country"]["value"], "CO")
        self.assertEqual(
            merged["fields"]["seller_country"]["source"], "gemini_inferred"
        )
        self.assertEqual(
            merged["fields"]["incoterms"]["value"], "FOB Bogotá",
        )
        self.assertEqual(
            merged["fields"]["country_of_origin"]["value"],
            "Various (see items)",
        )

        # The merged extraction must be persisted so routing.py reads it
        # — at least one save_extraction call carries the merged fields.
        save_calls = save_extraction.await_args_list
        self.assertGreater(len(save_calls), 0)
        last_saved_extraction = save_calls[-1].args[1]
        self.assertEqual(
            last_saved_extraction["fields"]["seller_country"]["value"],
            "CO",
        )

    async def test_inferred_seller_country_does_not_overwrite_existing(self):
        """If Document AI already extracted the field (rare), Gemini's
        inference does NOT overwrite it. Conservative merge.
        """
        module, _ = load_analyze_module()
        extraction = {
            "fields": {
                "invoice_id": {"value": "INV-1"},
                "invoice_amount": {"value": "100"},
                "seller_country": {"value": "MX", "confidence": 0.95},
            },
        }
        analysis = {
            "fraud_assessment": {"score": 12, "flags": []},
            "inferred_fields": {
                "seller_country": "CO",
                "incoterms": "",
                "country_of_origin": "",
                "inference_evidence": "",
            },
        }

        with patch.dict(
            os.environ,
            {
                "GCS_BUCKET_NAME": "puente-docs",
                "DOCUMENT_AI_PROCESSOR_ID": "processor-1",
                "GCP_PROJECT_ID": "demo-project",
            },
            clear=True,
        ), patch.object(
            module, "get_transaction",
            AsyncMock(return_value={
                "status": "uploaded",
                "blob_name": "x.pdf",
            }),
        ), patch.object(
            module, "update_transaction_status", AsyncMock(),
        ), patch.object(
            module, "save_extraction", AsyncMock(),
        ), patch.object(
            module, "save_analysis", AsyncMock(),
        ), patch.object(
            module, "extract_invoice_data", return_value=extraction,
        ), patch.object(
            module, "analyze_trade_document", return_value=analysis,
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-10"),
                current_user={"uid": "test-user-1"},
            )

        merged = response["extraction"]
        self.assertEqual(
            merged["fields"]["seller_country"]["value"], "MX"
        )
        # Confidence preserved (no overwrite to gemini_inferred source)
        self.assertEqual(
            merged["fields"]["seller_country"].get("confidence"), 0.95
        )

    async def test_merge_recomputes_extraction_summary_flags(self):
        """KAN-48 (PR #64 review): after merging inferred incoterms /
        country_of_origin into extraction.fields, the corresponding
        extraction_summary booleans must update too. Otherwise a re-run
        of analyze feeds Gemini a stale `has_incoterms: false` and we
        keep re-asking Gemini to infer values we've already filled in.
        """
        module, _ = load_analyze_module()
        extraction = {
            "fields": {"invoice_amount": {"value": "100"}},
            "extraction_summary": {
                "has_incoterms": False,
                "has_country_of_origin": False,
                "has_hs_code": False,
            },
        }
        analysis = {
            "fraud_assessment": {"score": 10, "flags": []},
            "inferred_fields": {
                "seller_country": "CO",
                "incoterms": "FOB Bogotá",
                "country_of_origin": "Various (see items)",
                "inference_evidence": "supplier address Bogotá, Colombia",
            },
        }

        with patch.dict(
            os.environ,
            {
                "GCS_BUCKET_NAME": "puente-docs",
                "DOCUMENT_AI_PROCESSOR_ID": "processor-1",
                "GCP_PROJECT_ID": "demo-project",
            },
            clear=True,
        ), patch.object(
            module, "get_transaction",
            AsyncMock(return_value={
                "status": "uploaded",
                "blob_name": "x.pdf",
            }),
        ), patch.object(
            module, "update_transaction_status", AsyncMock(),
        ), patch.object(
            module, "save_extraction", AsyncMock(),
        ) as save_extraction, patch.object(
            module, "save_analysis", AsyncMock(),
        ), patch.object(
            module, "extract_invoice_data", return_value=extraction,
        ), patch.object(
            module, "analyze_trade_document", return_value=analysis,
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-12"),
                current_user={"uid": "test-user-1"},
            )

        summary = response["extraction"]["extraction_summary"]
        self.assertTrue(summary["has_incoterms"])
        self.assertTrue(summary["has_country_of_origin"])

        # The persisted extraction also carries the recomputed summary.
        last_saved = save_extraction.await_args_list[-1].args[1]
        self.assertTrue(
            last_saved["extraction_summary"]["has_incoterms"]
        )
        self.assertTrue(
            last_saved["extraction_summary"]["has_country_of_origin"]
        )

    async def test_empty_inferred_values_skipped_in_merge(self):
        """Gemini may emit empty strings if it can't infer. Merge must
        not write empty fields to extraction.fields — those would mask
        the absence and confuse downstream consumers.
        """
        module, _ = load_analyze_module()
        extraction = {
            "fields": {"invoice_amount": {"value": "100"}},
        }
        analysis = {
            "fraud_assessment": {"score": 10, "flags": []},
            "inferred_fields": {
                "seller_country": "",
                "incoterms": "",
                "country_of_origin": "",
                "inference_evidence": "",
            },
        }

        with patch.dict(
            os.environ,
            {
                "GCS_BUCKET_NAME": "puente-docs",
                "DOCUMENT_AI_PROCESSOR_ID": "processor-1",
                "GCP_PROJECT_ID": "demo-project",
            },
            clear=True,
        ), patch.object(
            module, "get_transaction",
            AsyncMock(return_value={
                "status": "uploaded",
                "blob_name": "x.pdf",
            }),
        ), patch.object(
            module, "update_transaction_status", AsyncMock(),
        ), patch.object(
            module, "save_extraction", AsyncMock(),
        ), patch.object(
            module, "save_analysis", AsyncMock(),
        ), patch.object(
            module, "extract_invoice_data", return_value=extraction,
        ), patch.object(
            module, "analyze_trade_document", return_value=analysis,
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-11"),
                current_user={"uid": "test-user-1"},
            )

        merged_fields = response["extraction"]["fields"]
        self.assertNotIn("seller_country", merged_fields)
        self.assertNotIn("incoterms", merged_fields)
        self.assertNotIn("country_of_origin", merged_fields)

    async def test_runtime_error_marks_document_failed(self):
        module, http_exception_class = load_analyze_module()

        with patch.dict(
            os.environ,
            {
                "GCS_BUCKET_NAME": "puente-docs",
                "DOCUMENT_AI_PROCESSOR_ID": "processor-1",
                "GCP_PROJECT_ID": "demo-project",
            },
            clear=True,
        ), patch.object(
            module,
            "get_transaction",
            AsyncMock(
                return_value={
                    "status": "uploaded",
                    "blob_name": "invoices/doc-4.pdf",
                }
            ),
        ), patch.object(
            module,
            "update_transaction_status",
            AsyncMock(),
        ) as update_status, patch.object(
            module,
            "extract_invoice_data",
            side_effect=RuntimeError("Document AI timeout"),
        ):
            with self.assertRaises(http_exception_class) as exc:
                await module.analyze_document(
                    module.AnalyzeRequest(document_id="doc-4"),
                    current_user={"uid": "test-user-1"},
                )

        self.assertEqual(exc.exception.status_code, 502)
        self.assertEqual(exc.exception.detail, "Document AI timeout")
        self.assertEqual(update_status.await_count, 2)
        self.assertEqual(
            update_status.await_args_list[1].args,
            ("doc-4", "failed"),
        )
        self.assertEqual(
            update_status.await_args_list[1].kwargs,
            {"error": "Document AI timeout", "user_id": "test-user-1"},
        )


    async def test_analyze_short_circuits_when_status_is_routed(self):
        module, _ = load_analyze_module()

        stored_analysis = {
            "fraud_assessment": {"score": 10, "flags": []},
            "compliance_assessment": {
                "level": "LOW", "missing_documents": []
            },
            "routing_recommendation": {"recommended_method": "USDC"},
        }
        transaction = {
            "status": "routed",
            "extraction": {"fields": {"invoice_amount": {"value": "1000"}}},
            "full_analysis": stored_analysis,
        }

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module,
            "update_transaction_status",
            AsyncMock(),
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-routed"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "already_analyzed")
        self.assertEqual(response["analysis"], stored_analysis)

    async def test_analyze_short_circuits_when_status_is_compliance_checked(self):
        module, _ = load_analyze_module()

        stored_analysis = {
            "fraud_assessment": {"score": 7, "flags": []},
            "compliance_assessment": {
                "level": "LOW", "missing_documents": []
            },
            "routing_recommendation": {"recommended_method": "wise"},
        }
        transaction = {
            "status": "compliance_checked",
            "extraction": {"fields": {"invoice_amount": {"value": "2500"}}},
            "full_analysis": stored_analysis,
        }

        with patch.object(
            module,
            "get_transaction",
            AsyncMock(return_value=transaction),
        ), patch.object(
            module,
            "update_transaction_status",
            AsyncMock(),
        ):
            response = await module.analyze_document(
                module.AnalyzeRequest(document_id="doc-compliance-checked"),
                current_user={"uid": "test-user-1"},
            )

        self.assertEqual(response["status"], "already_analyzed")
        self.assertEqual(response["analysis"], stored_analysis)


if __name__ == "__main__":
    unittest.main()
