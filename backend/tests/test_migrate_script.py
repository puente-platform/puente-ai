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

    def __init__(self, drop_set_ids: set | None = None):
        self._ops = []
        # Doc IDs to silently drop set ops for — simulates writes that
        # appear to succeed but leave no record (the failure mode
        # verification is designed to catch).
        self._drop_set_ids = drop_set_ids or set()

    def set(self, ref, data, merge=False):
        self._ops.append(("set", ref, data, merge))

    def delete(self, ref):
        self._ops.append(("delete", ref, None, None))

    def commit(self):
        for op, ref, data, merge in self._ops:
            if op == "set":
                if ref.id in self._drop_set_ids:
                    continue  # Silently drop — simulates a lost write
                ref.set(data, merge=merge or False)
            elif op == "delete":
                ref.delete()
        self._ops.clear()


class FakeClient:
    def __init__(self, project=None, drop_set_ids: set | None = None):
        self.project = project
        self.root_store: dict = {}
        # If set, batch() returns a FakeBatch that drops set ops for any
        # ref whose doc_id matches — used by failure-path tests.
        self._drop_set_ids = drop_set_ids or set()

    def collection(self, name: str) -> FakeCollectionReference:
        return FakeCollectionReference(path_prefix=(name,), root_store=self.root_store)

    def batch(self) -> FakeBatch:
        return FakeBatch(drop_set_ids=self._drop_set_ids)


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

    def test_verification_failure_preserves_original(self):
        """If verification fails for a doc, its original must NOT be deleted."""
        # FakeClient silently drops the set op for "doc-fail" — the destination
        # document never materializes, verification sees missing, delete is
        # skipped for the whole batch.
        client = FakeClient(
            project="demo-project",
            drop_set_ids={"doc-fail"},
        )
        for doc_id in ["doc-fail", "doc-ok"]:
            client.root_store[("transactions", doc_id)] = {
                "document_id": doc_id,
                "status": "uploaded",
            }
        module, fake_modules = load_script_with_fake_client(client)

        with patch.dict(sys.modules, fake_modules):
            with patch.dict(os.environ, {"GCP_PROJECT_ID": "demo-project"}):
                failures = module._migrate(dry_run=False)

        # One verification failure should be reported for the exit code.
        self.assertEqual(failures, 1)

        # Safety invariant: failed-verify doc's original MUST survive.
        self.assertIn(("transactions", "doc-fail"), client.root_store)
        # The destination write was dropped — no new-path record for doc-fail.
        self.assertNotIn(
            ("transactions", "_dev_owner", "docs", "doc-fail"),
            client.root_store,
        )

        # Per-batch gating semantics: doc-ok shared the failing batch, so its
        # original is also preserved (delete_batch was skipped for the batch).
        # The copy itself succeeded, so doc-ok DOES exist at the new path.
        self.assertIn(("transactions", "doc-ok"), client.root_store)
        self.assertIn(
            ("transactions", "_dev_owner", "docs", "doc-ok"),
            client.root_store,
        )

    def test_failure_in_one_batch_does_not_block_other_batches(self):
        """Per-batch gating fix — a failure in batch 1 must NOT skip batch 2's deletes."""
        client = FakeClient(
            project="demo-project",
            drop_set_ids={"doc-batch1-fail"},
        )
        # 4 docs arranged so that at _MAX_DOCS_PER_BATCH=2 they form 2 batches:
        #   batch 1: doc-batch1-fail (verify fails), doc-batch1-ok
        #   batch 2: doc-batch2-ok-a, doc-batch2-ok-b (both clean)
        for doc_id in [
            "doc-batch1-fail",
            "doc-batch1-ok",
            "doc-batch2-ok-a",
            "doc-batch2-ok-b",
        ]:
            client.root_store[("transactions", doc_id)] = {
                "document_id": doc_id,
                "status": "uploaded",
            }
        module, fake_modules = load_script_with_fake_client(client)

        # Force 2 batches by shrinking the per-batch cap just for this test.
        original_max = module._MAX_DOCS_PER_BATCH
        module._MAX_DOCS_PER_BATCH = 2
        try:
            with patch.dict(sys.modules, fake_modules):
                with patch.dict(os.environ, {"GCP_PROJECT_ID": "demo-project"}):
                    failures = module._migrate(dry_run=False)
        finally:
            module._MAX_DOCS_PER_BATCH = original_max

        # Exactly one verification failure (the dropped doc in batch 1).
        self.assertEqual(failures, 1)

        # Batch 1: both originals preserved (per-batch delete gate held).
        self.assertIn(("transactions", "doc-batch1-fail"), client.root_store)
        self.assertIn(("transactions", "doc-batch1-ok"), client.root_store)

        # Batch 2: the critical assertion. Before the per-batch fix, the
        # cumulative `failures>0` from batch 1 would have skipped batch 2's
        # deletes too. Post-fix, batch 2 commits its deletes independently.
        self.assertNotIn(
            ("transactions", "doc-batch2-ok-a"), client.root_store
        )
        self.assertNotIn(
            ("transactions", "doc-batch2-ok-b"), client.root_store
        )
        # And the new-path copies exist for batch 2.
        self.assertIn(
            ("transactions", "_dev_owner", "docs", "doc-batch2-ok-a"),
            client.root_store,
        )
        self.assertIn(
            ("transactions", "_dev_owner", "docs", "doc-batch2-ok-b"),
            client.root_store,
        )


if __name__ == "__main__":
    unittest.main()
