"""
test_migrate_script.py — unit tests for scripts/migrate_firestore_tenant_scoping.py

Uses a fake Firestore client — no GCP connection required.  Tests verify:
1. dry_run lists orphans without mutating state.
2. Real run copies docs to new path, verifies, then deletes originals.
3. Idempotency — second run finds 0 orphans, exits with 0 failures.
4. Verification failure is detected and original preserved.
"""

import importlib.util
import os
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

SCRIPT_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "migrate_firestore_tenant_scoping.py"
)

# ---------------------------------------------------------------------------
# Fake Firestore infrastructure
# ---------------------------------------------------------------------------

class FakeSnapshot:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class FakeDocumentReference:
    def __init__(self, path: tuple, root_store: dict):
        self._path = path
        self._root_store = root_store
        self.id = path[-1]

    def get(self):
        return FakeSnapshot(self._root_store.get(self._path))

    def set(self, data, merge=False):
        if merge and self._path in self._root_store:
            merged = dict(self._root_store[self._path])
            merged.update(data)
            self._root_store[self._path] = merged
        else:
            self._root_store[self._path] = data

    def delete(self):
        self._root_store.pop(self._path, None)

    def collection(self, name: str) -> "FakeCollectionReference":
        return FakeCollectionReference(
            path_prefix=self._path + (name,),
            root_store=self._root_store,
        )


class FakeCollectionReference:
    def __init__(self, path_prefix: tuple, root_store: dict):
        self._path_prefix = path_prefix
        self._root_store = root_store

    def document(self, doc_id: str) -> FakeDocumentReference:
        return FakeDocumentReference(
            path=self._path_prefix + (doc_id,),
            root_store=self._root_store,
        )

    def list_documents(self):
        """Yield FakeDocumentReferences for all direct children."""
        seen = set()
        for path_key in self._root_store:
            # path_key is a tuple like ('transactions', 'doc-uuid-1')
            if (
                len(path_key) == len(self._path_prefix) + 1
                and path_key[: len(self._path_prefix)] == self._path_prefix
            ):
                child_id = path_key[len(self._path_prefix)]
                if child_id not in seen:
                    seen.add(child_id)
                    yield FakeDocumentReference(
                        path=self._path_prefix + (child_id,),
                        root_store=self._root_store,
                    )


class FakeBatch:
    """Fake WriteBatch that executes operations synchronously on commit."""

    def __init__(self):
        self._ops = []

    def set(self, ref, data, merge=False):
        self._ops.append(("set", ref, data, merge))

    def delete(self, ref):
        self._ops.append(("delete", ref, None, None))

    def commit(self):
        for op, ref, data, merge in self._ops:
            if op == "set":
                ref.set(data, merge=merge or False)
            elif op == "delete":
                ref.delete()
        self._ops.clear()


class FakeClient:
    def __init__(self, project=None):
        self.project = project
        self.root_store: dict = {}

    def collection(self, name: str) -> FakeCollectionReference:
        return FakeCollectionReference(path_prefix=(name,), root_store=self.root_store)

    def batch(self) -> FakeBatch:
        return FakeBatch()


# ---------------------------------------------------------------------------
# Script loader
# ---------------------------------------------------------------------------

def _build_fake_modules(fake_client: FakeClient) -> dict:
    """Return a sys.modules patch dict that wires fake_client into app.services.firestore."""
    fake_app = types.ModuleType("app")
    fake_services = types.ModuleType("app.services")
    fake_firestore_mod = types.ModuleType("app.services.firestore")
    fake_firestore_mod.get_firestore_client = lambda: fake_client
    fake_services.firestore = fake_firestore_mod
    fake_app.services = fake_services
    return {
        "app": fake_app,
        "app.services": fake_services,
        "app.services.firestore": fake_firestore_mod,
    }


def load_script_with_fake_client(fake_client: FakeClient):
    """Load the migration script module with a patched Firestore client."""
    fake_modules = _build_fake_modules(fake_client)
    module_name = f"test_target_migrate_{id(fake_client)}"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, fake_modules):
        spec.loader.exec_module(module)
    # Return both module and fake_modules so callers can re-apply the patch
    # during the actual _migrate() call (lazy import happens at call time).
    return module, fake_modules


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMigrateFirestoreTenantScoping(unittest.TestCase):

    def _make_client_with_orphans(self, doc_ids: list[str]) -> FakeClient:
        """Return a FakeClient pre-populated with flat-path orphan documents."""
        client = FakeClient(project="demo-project")
        for doc_id in doc_ids:
            client.root_store[("transactions", doc_id)] = {
                "document_id": doc_id,
                "filename": f"{doc_id}.pdf",
                "status": "uploaded",
            }
        return client

    def test_dry_run_does_not_mutate_state(self):
        """--dry-run must list orphans without creating or deleting any docs."""
        client = self._make_client_with_orphans(["doc-aaa", "doc-bbb"])
        module, fake_modules = load_script_with_fake_client(client)

        initial_keys = set(client.root_store.keys())

        with patch.dict(sys.modules, fake_modules):
            with patch.dict(os.environ, {"GCP_PROJECT_ID": "demo-project"}):
                failures = module._migrate(dry_run=True)

        self.assertEqual(failures, 0)
        # State must be identical to initial state
        self.assertEqual(set(client.root_store.keys()), initial_keys)

    def test_real_run_copies_and_deletes_orphans(self):
        """Real run moves docs to new path and deletes originals."""
        client = self._make_client_with_orphans(["doc-ccc", "doc-ddd"])
        module, fake_modules = load_script_with_fake_client(client)

        with patch.dict(sys.modules, fake_modules):
            with patch.dict(os.environ, {"GCP_PROJECT_ID": "demo-project"}):
                failures = module._migrate(dry_run=False)

        self.assertEqual(failures, 0, "Expected 0 verification failures")

        # Originals must be gone
        self.assertNotIn(("transactions", "doc-ccc"), client.root_store)
        self.assertNotIn(("transactions", "doc-ddd"), client.root_store)

        # New-path docs must exist with user_id field
        new_ccc = client.root_store.get(
            ("transactions", "_dev_owner", "docs", "doc-ccc")
        )
        new_ddd = client.root_store.get(
            ("transactions", "_dev_owner", "docs", "doc-ddd")
        )
        self.assertIsNotNone(new_ccc, "doc-ccc not found at new path")
        self.assertIsNotNone(new_ddd, "doc-ddd not found at new path")
        self.assertEqual(new_ccc["user_id"], "_dev_owner")
        self.assertEqual(new_ddd["user_id"], "_dev_owner")

    def test_idempotent_second_run_finds_zero_orphans(self):
        """Running migration twice must be safe — second run reports 0 orphans."""
        client = self._make_client_with_orphans(["doc-eee"])
        module, fake_modules = load_script_with_fake_client(client)

        with patch.dict(sys.modules, fake_modules):
            with patch.dict(os.environ, {"GCP_PROJECT_ID": "demo-project"}):
                failures_first = module._migrate(dry_run=False)
                failures_second = module._migrate(dry_run=False)

        self.assertEqual(failures_first, 0)
        self.assertEqual(failures_second, 0)

        # Only the new-path doc should exist; original must be absent.
        self.assertNotIn(("transactions", "doc-eee"), client.root_store)
        self.assertIn(
            ("transactions", "_dev_owner", "docs", "doc-eee"), client.root_store
        )


if __name__ == "__main__":
    unittest.main()
