import importlib.util
import os
import pathlib
import sys
import types
import unittest
from decimal import Decimal
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

    Supports the subcollection path pattern used by KAN-16 tenant scoping:
        db.collection("transactions").document(user_id).collection("docs").document(doc_id)

    Each FakeDocumentReference carries a reference to the root store (a nested
    dict keyed by path tuples) and its own path tuple so reads/writes are
    correctly scoped.
    """

    def __init__(self, path: tuple, root_store: dict):
        # path is a tuple of path segments, e.g.
        # ("transactions", "user-a", "docs", "doc-1")
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
        """Return a sub-collection reference scoped under this document's path."""
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
    """
    Fake Firestore CollectionReference.

    path_prefix is a tuple of path segments up to (and including) this
    collection's name — e.g. ("transactions",) for the root collection,
    or ("transactions", "user-a", "docs") for a subcollection.
    """

    def __init__(self, path_prefix: tuple, root_store: dict):
        self._path_prefix = path_prefix
        self._root_store = root_store

    def document(self, document_id: str) -> FakeDocumentReference:
        return FakeDocumentReference(
            path=self._path_prefix + (document_id,),
            root_store=self._root_store,
        )


class FakeClient:
    instances = []

    def __init__(self, project):
        self.project = project
        # root_store is the single shared dict for the whole fake Firestore.
        # Keys are path tuples: ("transactions", user_id, "docs", doc_id)
        self.root_store: dict = {}
        self.__class__.instances.append(self)

    def collection(self, name: str) -> FakeCollectionReference:
        return FakeCollectionReference(
            path_prefix=(name,),
            root_store=self.root_store,
        )

    def get_doc(self, *path_segments) -> dict | None:
        """Test helper: read a doc by path segments without going through the API."""
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
                user_id="user-a",
            )

        self.assertEqual(transaction["status"], "uploaded")
        client = FakeClient.instances[-1]
        # Verify doc is stored at the tenant-scoped subcollection path
        saved = client.get_doc("transactions", "user-a", "docs", "doc-1")
        self.assertIsNotNone(saved)
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
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-2")
        self.assertIsNotNone(saved)
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
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-3")
        self.assertIsNotNone(saved)
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
                user_id="user-a",
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
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-4")
        self.assertIsNotNone(saved)
        self.assertEqual(saved["status"], "compliance_checked")
        self.assertEqual(saved["compliance"]["compliance_level"], "MEDIUM")
        self.assertEqual(saved["analysis"]["compliance_level"], "MEDIUM")
        self.assertEqual(
            saved["analysis"]["missing_documents"][0]["code"],
            "US_MISSING_ISF",
        )
        self.assertEqual(saved["analysis"]["fraud_score"], None)
        self.assertIn("compliance_checked_at", saved)

    async def test_save_compliance_result_sets_status_to_compliance_checked(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.create_transaction_record(
                "doc-compliance-status",
                "invoice.pdf",
                "invoices/doc-compliance-status.pdf",
                2048,
                user_id="user-a",
            )
            await module.save_compliance_result(
                "doc-compliance-status",
                {
                    "compliance_level": "HIGH",
                    "gap_count": 0,
                    "missing_documents": [],
                    "warnings": [],
                    "passed_checks": ["All required documents present"],
                },
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-compliance-status")
        self.assertIsNotNone(saved)
        self.assertEqual(saved["status"], "compliance_checked")

    async def test_save_routing_result_sets_status_and_saves_string_amount(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.save_routing_result(
                "doc-routing-1",
                {
                    "recommended_method": "local_pse",
                    "total_savings_usd": Decimal("841.00"),
                },
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-routing-1")
        self.assertIsNotNone(saved)
        self.assertEqual(saved["status"], "routed")
        self.assertEqual(saved["routing_recommended_method"], "local_pse")
        self.assertEqual(saved["routing_total_savings_usd"], "841.00")
        self.assertIsNone(saved["error"])
        self.assertIn("routed_at", saved)

    async def test_save_routing_result_quantizes_decimal_half_up(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.save_routing_result(
                "doc-routing-2",
                {
                    "recommended_method": "wise",
                    "total_savings_usd": Decimal("841.005"),
                },
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-routing-2")
        # ROUND_HALF_UP expected: 841.005 -> 841.01
        self.assertEqual(saved["routing_total_savings_usd"], "841.01")

    async def test_save_routing_result_handles_string_numeric_input(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.save_routing_result(
                "doc-routing-3",
                {
                    "recommended_method": "dlocal",
                    "total_savings_usd": "841.0",
                },
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-routing-3")
        self.assertEqual(saved["routing_total_savings_usd"], "841.00")

    async def test_save_routing_result_defaults_none_to_zero(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.save_routing_result(
                "doc-routing-4",
                {
                    "recommended_method": "swift_wire",
                    "total_savings_usd": None,
                },
                user_id="user-a",
            )

        client = FakeClient.instances[-1]
        saved = client.get_doc("transactions", "user-a", "docs", "doc-routing-4")
        self.assertEqual(saved["routing_total_savings_usd"], "0.00")

    async def test_save_routing_result_raises_on_invalid_savings_value(self):
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            with self.assertRaises(ValueError):
                await module.save_routing_result(
                    "doc-routing-5",
                    {
                        "recommended_method": "wise",
                        "total_savings_usd": "abc",
                    },
                    user_id="user-a",
                )

    # --- KAN-16: Cross-user isolation tests ---

    async def test_cross_user_get_transaction_returns_none_for_wrong_user(self):
        """User B cannot read User A's document — get_transaction returns None.

        This is the path-based isolation guarantee: transactions/{user_id}/docs/{doc_id}
        means user B's path simply has no document at that location.
        """
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            # User A creates a document
            await module.create_transaction_record(
                "doc-shared-id",
                "user-a-invoice.pdf",
                "invoices/user-a-invoice.pdf",
                2048,
                user_id="user-a",
            )

            # User B attempts to read the same doc_id under their own path
            result = await module.get_transaction(
                "doc-shared-id",
                user_id="user-b",
            )

        # Must return None — user B has no doc at transactions/user-b/docs/doc-shared-id
        self.assertIsNone(result)

    async def test_cross_user_save_does_not_overwrite_other_users_doc(self):
        """User B writing to the same doc_id does not affect User A's document.

        With subcollection isolation, user B's write lands at
        transactions/user-b/docs/doc-overlap — a different Firestore path from
        transactions/user-a/docs/doc-overlap.
        """
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            # User A uploads a doc
            await module.create_transaction_record(
                "doc-overlap",
                "user-a-invoice.pdf",
                "invoices/user-a.pdf",
                1000,
                user_id="user-a",
            )

            # User B saves routing result with the same doc_id
            await module.save_routing_result(
                "doc-overlap",
                {
                    "recommended_method": "swift_wire",
                    "total_savings_usd": "50.00",
                },
                user_id="user-b",
            )

            # User A's doc should be unchanged (still "uploaded", not "routed")
            user_a_doc = await module.get_transaction(
                "doc-overlap",
                user_id="user-a",
            )
            # User B's doc is correctly stored under user-b's path
            user_b_doc = await module.get_transaction(
                "doc-overlap",
                user_id="user-b",
            )

        self.assertIsNotNone(user_a_doc)
        self.assertEqual(user_a_doc["status"], "uploaded")
        self.assertEqual(user_a_doc["filename"], "user-a-invoice.pdf")

        self.assertIsNotNone(user_b_doc)
        self.assertEqual(user_b_doc["status"], "routed")

    async def test_cross_user_doc_stored_at_correct_subcollection_path(self):
        """Documents are stored at transactions/{user_id}/docs/{doc_id} — not at the root.

        Verifies path structure by inspecting the fake store's key directly.
        """
        module = load_firestore_module()

        with patch.dict(
            os.environ,
            {"GCP_PROJECT_ID": "demo-project"},
            clear=True,
        ):
            await module.create_transaction_record(
                "doc-path-check",
                "invoice.pdf",
                "invoices/invoice.pdf",
                512,
                user_id="user-c",
            )

        client = FakeClient.instances[-1]

        # Correct subcollection path must exist
        correct_path = ("transactions", "user-c", "docs", "doc-path-check")
        self.assertIn(correct_path, client.root_store)

        # Old flat path must NOT exist
        flat_path = ("transactions", "doc-path-check")
        self.assertNotIn(flat_path, client.root_store)


if __name__ == "__main__":
    unittest.main()
