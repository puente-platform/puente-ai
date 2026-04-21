import importlib.util
import os
import pathlib
import sys
import types
import unittest
from decimal import Decimal
from typing import ClassVar
from unittest.mock import patch


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "app"
    / "services"
    / "firestore.py"
)


class FakeSnapshot:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class FakeDocumentReference:
    """
    Fake Firestore DocumentReference supporting subcollections.

    Mirrors the implementation in test_firestore.py — path-tuple keyed store
    so the subcollection path transactions/{user_id}/docs/{doc_id} is correctly
    represented.
    """

    def __init__(self, path: tuple, root_store: dict):
        self._path = path
        self._root_store = root_store
        self.set_calls = []

    def set(self, data, merge=False):
        self.set_calls.append({"data": data, "merge": merge})
        if merge and self._path in self._root_store:
            self._root_store[self._path] = self._deep_merge(
                self._root_store[self._path], data
            )
        else:
            self._root_store[self._path] = data

    def get(self):
        return FakeSnapshot(self._root_store.get(self._path))

    def collection(self, name: str) -> "FakeCollectionReference":
        return FakeCollectionReference(
            path_prefix=self._path + (name,),
            root_store=self._root_store,
        )

    @staticmethod
    def _deep_merge(base: dict, updates: dict) -> dict:
        result = dict(base)
        for key, value in updates.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = FakeDocumentReference._deep_merge(
                    result[key], value
                )
            else:
                result[key] = value
        return result


class FakeCollectionReference:
    def __init__(self, path_prefix: tuple, root_store: dict):
        self._path_prefix = path_prefix
        self._root_store = root_store

    def document(self, document_id: str) -> FakeDocumentReference:
        return FakeDocumentReference(
            path=self._path_prefix + (document_id,),
            root_store=self._root_store,
        )


class FakeClient:
    instances: ClassVar[list["FakeClient"]] = []

    def __init__(self, project):
        self.project = project
        self.root_store: dict = {}
        self.__class__.instances.append(self)

    def collection(self, name: str) -> FakeCollectionReference:
        return FakeCollectionReference(
            path_prefix=(name,),
            root_store=self.root_store,
        )

    def get_doc(self, *path_segments) -> dict | None:
        """Test helper: read a doc by path segments."""
        return self.root_store.get(path_segments)


def load_firestore_module():
    FakeClient.instances = []

    fake_google = types.ModuleType("google")
    fake_cloud = types.ModuleType("google.cloud")
    fake_firestore = types.ModuleType("google.cloud.firestore")

    fake_firestore.Client = FakeClient
    fake_firestore.CollectionReference = FakeCollectionReference
    fake_firestore.DocumentReference = FakeDocumentReference

    fake_cloud.firestore = fake_firestore
    fake_google.cloud = fake_cloud

    fake_modules = {
        "google": fake_google,
        "google.cloud": fake_cloud,
        "google.cloud.firestore": fake_firestore,
    }

    module_name = "test_target_firestore_integration"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, fake_modules):
        assert spec.loader is not None
        spec.loader.exec_module(module)

    return module


TIMESTAMP_FIELDS = {
    "uploaded_at",
    "updated_at",
    "extracted_at",
    "analyzed_at",
    "compliance_checked_at",
    "routed_at",
}

# The test user for pipeline integration tests.
# Uses the default _dev_owner sentinel consistent with the KAN-16 migration plan.
TEST_USER_ID = "_dev_owner"


def strip_timestamps(doc: dict) -> dict:
    """Return a shallow copy of doc with timestamp fields removed.

    Idempotency in this project is semantic: a re-run converges to the
    same final state modulo the updated_at / *_at fields, which naturally
    drift between calls because the clock advances.
    """
    return {k: v for k, v in doc.items() if k not in TIMESTAMP_FIELDS}


class PipelineIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_full_pipeline_writes_routed_doc_with_decimal_string(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.create_transaction_record(
                "pipeline-doc",
                "invoice.pdf",
                "invoices/2026/04/pipeline-doc.pdf",
                8192,
                user_id=TEST_USER_ID,
            )
            await module.save_extraction(
                "pipeline-doc",
                {"fields": {"invoice_amount": {"value": "47500"}}},
                user_id=TEST_USER_ID,
            )
            await module.save_analysis(
                "pipeline-doc",
                {
                    "fraud_assessment": {
                        "score": 12,
                        "flags": [],
                        "explanation": "Normal supplier pattern.",
                    },
                    "compliance_assessment": {
                        "level": "LOW",
                        "missing_documents": [],
                    },
                    "routing_recommendation": {
                        "recommended_method": "USDC",
                    },
                },
                user_id=TEST_USER_ID,
            )
            await module.save_compliance_result(
                "pipeline-doc",
                {
                    "compliance_level": "LOW",
                    "gap_count": 0,
                    "missing_documents": [],
                    "warnings": [],
                    "passed_checks": ["Commercial Invoice present"],
                },
                user_id=TEST_USER_ID,
            )
            await module.save_routing_result(
                "pipeline-doc",
                {
                    "recommended_method": "usdc_stellar",
                    "total_savings_usd": Decimal("1250.50"),
                },
                user_id=TEST_USER_ID,
            )

        client = FakeClient.instances[-1]
        # KAN-16: docs live at transactions/{user_id}/docs/{doc_id}
        saved = client.get_doc("transactions", TEST_USER_ID, "docs", "pipeline-doc")
        self.assertIsNotNone(saved)

        self.assertEqual(saved["status"], "routed")
        self.assertEqual(saved["routing_total_savings_usd"], "1250.50")
        self.assertEqual(saved["routing_recommended_method"], "usdc_stellar")
        self.assertIsInstance(saved["routing_total_savings_usd"], str)
        self.assertEqual(saved["routing"]["total_savings_usd"], "1250.50")
        self.assertIsInstance(saved["routing"]["total_savings_usd"], str)

        self.assertEqual(saved["analysis"]["fraud_score"], 12)
        self.assertEqual(saved["analysis"]["compliance_level"], "LOW")
        self.assertEqual(saved["analysis"]["routing_recommendation"], "USDC")

        self.assertEqual(saved["compliance"]["compliance_level"], "LOW")
        self.assertEqual(saved["compliance"]["passed_checks"], [
            "Commercial Invoice present"
        ])

        self.assertIsNone(saved["error"])

    async def test_rerunning_routing_converges_to_same_semantic_state(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.create_transaction_record(
                "rerun-doc",
                "invoice.pdf",
                "invoices/rerun-doc.pdf",
                4096,
                user_id=TEST_USER_ID,
            )
            await module.save_extraction(
                "rerun-doc",
                {"fields": {"invoice_amount": {"value": "10000"}}},
                user_id=TEST_USER_ID,
            )
            await module.save_analysis(
                "rerun-doc",
                {
                    "fraud_assessment": {"score": 5, "flags": []},
                    "compliance_assessment": {"level": "LOW",
                                              "missing_documents": []},
                    "routing_recommendation": {"recommended_method": "wise"},
                },
                user_id=TEST_USER_ID,
            )
            await module.save_compliance_result(
                "rerun-doc",
                {
                    "compliance_level": "LOW",
                    "missing_documents": [],
                    "gap_count": 0,
                    "warnings": [],
                    "passed_checks": [],
                },
                user_id=TEST_USER_ID,
            )
            routing_payload = {
                "recommended_method": "wise",
                "total_savings_usd": Decimal("300.00"),
            }
            await module.save_routing_result(
                "rerun-doc",
                routing_payload,
                user_id=TEST_USER_ID,
            )

            client = FakeClient.instances[-1]
            first_snapshot = strip_timestamps(
                dict(client.get_doc("transactions", TEST_USER_ID, "docs", "rerun-doc"))
            )

            # Re-run the terminal save with the same input. Timestamps
            # will drift (clock advanced), but every other field must
            # converge to the same state — that is the KAN-6 idempotency
            # contract as written in docs/CLAUDE.md's Money Math policy.
            await module.save_routing_result(
                "rerun-doc",
                routing_payload,
                user_id=TEST_USER_ID,
            )
            second_snapshot = strip_timestamps(
                dict(client.get_doc("transactions", TEST_USER_ID, "docs", "rerun-doc"))
            )

        self.assertEqual(first_snapshot, second_snapshot)
        self.assertEqual(first_snapshot["status"], "routed")
        self.assertEqual(
            first_snapshot["routing_total_savings_usd"], "300.00"
        )
        self.assertEqual(
            first_snapshot["routing"]["total_savings_usd"], "300.00"
        )
        self.assertIsInstance(
            first_snapshot["routing"]["total_savings_usd"], str
        )


if __name__ == "__main__":
    unittest.main()
