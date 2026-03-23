import importlib.util
import os
import pathlib
import sys
import types
import unittest
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
    def __init__(self, document_id, store):
        self.document_id = document_id
        self.store = store
        self.set_calls = []

    def set(self, data, merge=False):
        self.set_calls.append({"data": data, "merge": merge})
        if merge and self.document_id in self.store:
            self.store[self.document_id] = self._deep_merge(
                self.store[self.document_id], data
            )
        else:
            self.store[self.document_id] = data

    def get(self):
        return FakeSnapshot(self.store.get(self.document_id))

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
                    result[key], value)
            else:
                result[key] = value
        return result


class FakeCollectionReference:
    def __init__(self, store, refs):
        self.store = store
        self.refs = refs

    def document(self, document_id):
        ref = self.refs.get(document_id)
        if ref is None:
            ref = FakeDocumentReference(document_id, self.store)
            self.refs[document_id] = ref
        return ref


class FakeClient:
    instances = []

    def __init__(self, project):
        self.project = project
        self.store = {}
        self.refs = {}
        self.__class__.instances.append(self)

    def collection(self, name):
        return FakeCollectionReference(self.store, self.refs)


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

    module_name = "test_target_firestore"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, fake_modules):
        assert spec.loader is not None
        spec.loader.exec_module(module)

    return module


class FirestoreServiceTests(unittest.IsolatedAsyncioTestCase):
    def test_get_firestore_client_is_singleton(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            first_client = module.get_firestore_client()
            second_client = module.get_firestore_client()

        self.assertIs(first_client, second_client)
        self.assertEqual(len(FakeClient.instances), 1)
        self.assertEqual(FakeClient.instances[0].project, "demo-project")

    async def test_create_transaction_record_persists_uploaded_state(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            transaction = await module.create_transaction_record(
                "doc-1",
                "invoice.pdf",
                "invoices/2026/03/22/doc-1.pdf",
                4096,
            )

        self.assertEqual(transaction["status"], "uploaded")
        client = FakeClient.instances[-1]
        saved = client.store["doc-1"]
        self.assertEqual(saved["filename"], "invoice.pdf")
        self.assertEqual(saved["file_size_bytes"], 4096)
        self.assertIsNone(saved["error"])

    async def test_save_extraction_sets_default_timestamp_and_clears_error(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.save_extraction(
                "doc-2",
                {"fields": {"invoice_amount": {"value": "500"}}},
            )

        client = FakeClient.instances[-1]
        saved = client.store["doc-2"]
        self.assertEqual(saved["status"], "extracted")
        self.assertIn("extracted_at", saved)
        self.assertIsNone(saved["error"])

    async def test_save_analysis_flattens_summary_fields(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.save_analysis(
                "doc-3",
                {
                    "fraud_assessment": {
                        "score": 18,
                        "flags": ["address mismatch"],
                        "explanation": "Mostly consistent.",
                    },
                    "compliance_assessment": {
                        "level": "LOW risk",
                        "missing_documents": ["CFDI"],
                    },
                    "routing_recommendation": {
                        "recommended_method": "USDC",
                    },
                },
            )

        client = FakeClient.instances[-1]
        saved = client.store["doc-3"]
        self.assertEqual(saved["status"], "analyzed")
        self.assertEqual(saved["analysis"]["fraud_score"], 18)
        self.assertEqual(saved["analysis"]["routing_recommendation"], "USDC")
        self.assertEqual(saved["analysis"]["missing_documents"], ["CFDI"])
        self.assertIn("analyzed_at", saved)

    async def test_save_compliance_result_sets_compliance_without_overwriting_summary(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.create_transaction_record(
                "doc-4",
                "invoice.pdf",
                "invoices/doc-4.pdf",
                1024,
            )
            await module.save_compliance_result(
                "doc-4",
                {
                    "compliance_level": "MEDIUM",
                    "gap_count": 1,
                    "missing_documents": [{"code": "US_MISSING_ISF"}],
                    "warnings": ["Shipment mode missing for US import."],
                    "passed_checks": ["Commercial Invoice present"],
                },
            )

        client = FakeClient.instances[-1]
        saved = client.store["doc-4"]
        self.assertEqual(saved["status"], "uploaded")
        self.assertEqual(saved["compliance"]["compliance_level"], "MEDIUM")
        self.assertEqual(saved["analysis"]["compliance_level"], "MEDIUM")
        self.assertEqual(
            saved["analysis"]["missing_documents"][0]["code"],
            "US_MISSING_ISF",
        )
        self.assertEqual(saved["analysis"]["fraud_score"], None)
        self.assertIn("compliance_checked_at", saved)


if __name__ == "__main__":
    unittest.main()
