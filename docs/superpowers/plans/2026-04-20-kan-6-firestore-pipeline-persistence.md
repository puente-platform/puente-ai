# KAN-6: Firestore Pipeline Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the upload → analyze → compliance → routing pipeline loop in Firestore by persisting the compliance status transition, protecting against backward status transitions, and proving end-to-end convergence with an integration test.

**Architecture:** Most of KAN-6 is already implemented — `save_extraction`, `save_analysis`, `save_compliance_result`, and `save_routing_result` exist in `backend/app/services/firestore.py` with Decimal-as-string money handling, singleton client, and status transitions for analyze + routing. The remaining gaps are: (1) `save_compliance_result` never writes `status="compliance_checked"`; (2) `/analyze` can overwrite a `routed` doc back to `analyzed` because its idempotency short-circuit is too narrow; (3) `/compliance` has no idempotency short-circuit at all; (4) no test exercises the full pipeline + re-run convergence; (5) routing route computes `result.to_dict()` twice (minor bug).

**Tech Stack:** Python 3.11, FastAPI, google-cloud-firestore, pytest/unittest, asyncio. No new dependencies.

**Ambiguity decisions locked in (default recommendations accepted 2026-04-20):**
1. Idempotency bar = semantic equality ignoring `updated_at`/`*_at` timestamps — not byte-identical.
2. Status-downgrade guard lives at the **route layer** only (mirrors existing `analyze.py:84` pattern). Service-layer transactional guards are out of scope for this ticket.
3. `save_compliance_result` writes `status="compliance_checked"` unconditionally; the compliance route short-circuits before calling save if status is already `"compliance_checked"` or `"routed"`.
4. `/analyze` widens its short-circuit to cover `"analyzed"`, `"compliance_checked"`, and `"routed"` — all return the stored analysis without re-running Gemini.
5. KAN-7 (singleton), KAN-24 (routed status), KAN-25 (Decimal string) are confirmed already-implemented in code and will be closed out in `docs/CLAUDE.md` as part of this ticket.
6. Scope envelope = 5 code changes + 1 integration test + 1 docs update. No service-layer transactional guards, no Firestore security rules work.

**Out of scope (explicitly):**
- Service-layer transactional downgrade guards (deferred to a future tech-debt ticket if races bite).
- Compliance route requiring `status=="analyzed"` as a hard prerequisite (current code only requires `extraction` to exist — that's a separate bug).
- Any renames to response payload fields (e.g., `"already_analyzed"` stays even though it's returned for routed docs too).
- KAN-15 auth work or KAN-16 multi-tenant isolation.

**Test strategy:**
- Unit tests extend existing `test_firestore.py` (status write), `test_analyze.py` (widened short-circuit), `test_compliance_route.py` (new short-circuit).
- New integration test at `backend/tests/test_pipeline_integration.py` reuses the `FakeClient` + `load_firestore_module` loader from `test_firestore.py` to drive all four save functions end-to-end and assert semantic equality across an idempotent re-run.
- All pytest commands assume the repository root as the working directory and venv at `backend/venv`. Invocation: `backend/venv/bin/python -m pytest backend/tests/... -v` (relies on `backend/conftest.py:5` adding `backend/` to `sys.path`).

**Risks:**
- Updating `save_compliance_result` to write `status` breaks the existing test at `test_firestore.py:238` which asserts status stays `"uploaded"` after compliance save. Task 1 updates that assertion as part of the behavior change.
- Widening the analyze short-circuit means a user who re-uploads the same document_id with new content will get stale results until they use a fresh document_id. This is consistent with the current behavior for `"analyzed"` and is documented in the response message.
- Compliance short-circuit returns the stored compliance dict verbatim — if a future migration changes the compliance schema, old stored dicts will still be returned. Not new risk; same as analyze.

**Rollout:** Standard — merge to main triggers `.github/workflows/backend-deploy.yml` to rebuild Cloud Run image. No migration, no data backfill. Existing docs with no `status="compliance_checked"` transition simply stay at `"analyzed"` — they still route successfully because `routing.py:62` already accepts `"analyzed"` as a valid prior state.

---

## File Structure

**Files modified:**
- `backend/app/services/firestore.py` — `save_compliance_result` adds `"status": "compliance_checked"` to its merge payload (Task 1).
- `backend/app/routes/analyze.py` — widen idempotency check from `== "analyzed"` to `in {"analyzed", "compliance_checked", "routed"}` (Task 2).
- `backend/app/routes/compliance.py` — add status short-circuit for `compliance_checked` and `routed` docs, placed between the 404 check and the extraction check (Task 3).
- `backend/app/routes/routing.py` — reuse `routing_dict` in the response body instead of calling `result.to_dict()` twice (Task 4).
- `backend/tests/test_firestore.py` — add new status-write assertion; update existing `test_save_compliance_result_sets_compliance_without_overwriting_summary` to reflect new contract (Task 1).
- `backend/tests/test_analyze.py` — add tests covering widened short-circuit for `compliance_checked` and `routed` (Task 2).
- `backend/tests/test_compliance_route.py` — add short-circuit test (Task 3).
- `docs/CLAUDE.md` — move KAN-6, KAN-7, KAN-24, KAN-25 from To Do to Done; update Phase 2 status line for KAN-6 (Task 6).

**Files created:**
- `backend/tests/test_pipeline_integration.py` — end-to-end pipeline test that exercises all four save functions against FakeClient and asserts semantic idempotent convergence (Task 5).

---

## Task 1: `save_compliance_result` persists `status="compliance_checked"`

**Files:**
- Modify: `backend/app/services/firestore.py:215-245`
- Modify: `backend/tests/test_firestore.py:211-246` (update existing assertion)
- Test: `backend/tests/test_firestore.py` (add new assertion)

- [ ] **Step 1: Add failing test for new status contract**

Append this method to the `FirestoreServiceTests` class in `backend/tests/test_firestore.py` (right after `test_save_compliance_result_sets_compliance_without_overwriting_summary`):

```python
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
        )

    client = FakeClient.instances[-1]
    saved = client.store["doc-compliance-status"]
    self.assertEqual(saved["status"], "compliance_checked")
```

- [ ] **Step 2: Run the new test to verify it fails**

Run: `backend/venv/bin/python -m pytest backend/tests/test_firestore.py::FirestoreServiceTests::test_save_compliance_result_sets_status_to_compliance_checked -v`

Expected: FAIL with `AssertionError: 'uploaded' != 'compliance_checked'`

- [ ] **Step 3: Implement the status write in `save_compliance_result`**

In `backend/app/services/firestore.py`, replace the `save_compliance_result` body's `.set(...)` payload (currently at lines 231-244) with this version that adds a `status` field:

```python
    await asyncio.to_thread(
        _get_document_ref(document_id).set,
        {
            "status": "compliance_checked",
            "compliance": compliance,
            "analysis": {
                "compliance_level": compliance.get("compliance_level"),
                "missing_documents": compliance.get("missing_documents"),
            },
            "compliance_checked_at": now,
            "updated_at": now,
            "error": None,
        },
        merge=True,
    )
```

- [ ] **Step 4: Run the new test to verify it passes**

Run: `backend/venv/bin/python -m pytest backend/tests/test_firestore.py::FirestoreServiceTests::test_save_compliance_result_sets_status_to_compliance_checked -v`

Expected: PASS

- [ ] **Step 5: Update the existing status assertion in the older test**

The older test `test_save_compliance_result_sets_compliance_without_overwriting_summary` asserts `saved["status"] == "uploaded"` at `backend/tests/test_firestore.py:238`. With the new behavior it must assert `"compliance_checked"`. Change this line:

```python
        self.assertEqual(saved["status"], "uploaded")
```

to:

```python
        self.assertEqual(saved["status"], "compliance_checked")
```

- [ ] **Step 6: Run the full firestore test suite to verify all green**

Run: `backend/venv/bin/python -m pytest backend/tests/test_firestore.py -v`

Expected: all tests pass (11 total — 10 existing + 1 new).

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/firestore.py backend/tests/test_firestore.py
git commit -m "$(cat <<'EOF'
feat(KAN-6): persist status="compliance_checked" in save_compliance_result

Closes the compliance stage of the pipeline status transition. Previously
save_compliance_result wrote compliance block + timestamps but never
advanced the document status, so transactions went uploaded -> analyzed ->
routed skipping the compliance_checked stage entirely.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Widen `/analyze` idempotency short-circuit

**Files:**
- Modify: `backend/app/routes/analyze.py:83-93`
- Test: `backend/tests/test_analyze.py` (append new test cases)

- [ ] **Step 1: Add failing tests for `routed` and `compliance_checked` short-circuits**

Append both methods below to the `AnalyzeRouteTests` class in `backend/tests/test_analyze.py`. Note the loader returns a `(module, HTTPException)` tuple — existing tests destructure as `module, _ = load_analyze_module()`, so we follow the same pattern. The tests assert that calling `/analyze` on a doc already past the analyze stage returns the stored analysis and does not invoke Gemini:

```python
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
                module.AnalyzeRequest(document_id="doc-routed")
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
                module.AnalyzeRequest(document_id="doc-compliance-checked")
            )

        self.assertEqual(response["status"], "already_analyzed")
        self.assertEqual(response["analysis"], stored_analysis)
```

Note: the short-circuit branch in `analyze.py:85-92` returns early before Gemini is reached, so we do not need to patch `analyze_trade_document` to prove it was not invoked — the `_placeholder_sync` default in the loader would raise `AssertionError` if the short-circuit leaked, which is a stronger guarantee than a mock call-count check.

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `backend/venv/bin/python -m pytest backend/tests/test_analyze.py -k "short_circuits_when_status" -v`

Expected: FAIL — current code re-runs the extraction/analysis path because `current_status == "analyzed"` is narrower than the new contract.

- [ ] **Step 3: Widen the short-circuit condition**

In `backend/app/routes/analyze.py`, replace line 84:

```python
        if current_status == "analyzed":
```

with:

```python
        if current_status in ("analyzed", "compliance_checked", "routed"):
```

No other code changes are needed — the response payload already pulls from `transaction.get("full_analysis")` and `transaction.get("extraction")`, both of which survive the merge=True writes at downstream stages.

- [ ] **Step 4: Run the new tests to verify they pass**

Run: `backend/venv/bin/python -m pytest backend/tests/test_analyze.py -k "short_circuits_when_status" -v`

Expected: PASS.

- [ ] **Step 5: Run the full analyze test suite to guard against regressions**

Run: `backend/venv/bin/python -m pytest backend/tests/test_analyze.py -v`

Expected: all tests pass (6 total — 4 existing + 2 new).

- [ ] **Step 6: Commit**

```bash
git add backend/app/routes/analyze.py backend/tests/test_analyze.py
git commit -m "$(cat <<'EOF'
feat(KAN-6): widen /analyze short-circuit to protect routed docs

Previously /analyze only short-circuited when status == "analyzed". If a
caller hit /analyze on a doc that had progressed to "compliance_checked"
or "routed", the route would re-run Gemini and save_analysis would merge
status back to "analyzed", clobbering the downstream pipeline state.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: `/compliance` short-circuits when already checked or routed

**Files:**
- Modify: `backend/app/routes/compliance.py:30-48`
- Test: `backend/tests/test_compliance_route.py` (append new test cases)

- [ ] **Step 1: Add failing tests for the new short-circuit**

Append both methods to the `ComplianceRouteTests` class in `backend/tests/test_compliance_route.py`. The loader returns `(module, HTTPException)` — follow the existing `module, _ = load_compliance_module()` destructuring pattern:

```python
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
                module.ComplianceRequest(document_id="doc-cc")
            )

        self.assertEqual(response["status"], "already_checked")
        self.assertEqual(response["compliance"], stored_compliance)
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
                module.ComplianceRequest(document_id="doc-routed")
            )

        self.assertEqual(response["status"], "already_checked")
        self.assertEqual(response["compliance"], stored_compliance)
        save_mock.assert_not_called()
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `backend/venv/bin/python -m pytest backend/tests/test_compliance_route.py -k "short_circuits_when_already" -v`

Expected: FAIL — current code calls `check_compliance` and `save_compliance_result` regardless of existing status.

- [ ] **Step 3: Implement the short-circuit in the compliance route**

In `backend/app/routes/compliance.py`, replace the body of `run_compliance_check` from line 30 through line 48 (the 404 check plus the extraction check) with this version. The short-circuit goes between the 404 check and the extraction check so routed docs don't get 422'd on a missing extraction field that slipped in some odd recovery path:

```python
    # Step 1 — fetch the document from Firestore
    transaction = await get_transaction(request.document_id)
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail=f"Document {request.document_id} not found",
        )

    # Step 2 — idempotent short-circuit: don't re-run compliance or downgrade
    # the status if the doc has already progressed past this stage.
    current_status = transaction.get("status")
    if current_status in ("compliance_checked", "routed"):
        return {
            "document_id": request.document_id,
            "status": "already_checked",
            "message": "Compliance check already completed.",
            "compliance": transaction.get("compliance"),
        }

    # Step 3 — make sure we have extraction data to work with
    extraction = transaction.get("extraction")
    if not isinstance(extraction, dict) or not extraction:
        raise HTTPException(
            status_code=422,
            detail=(
                "Document has not been extracted yet. "
                "Call /analyze first."
            ),
        )
```

Leave lines 49 onward (the `check_compliance` call, save, and return) untouched — the existing step numbers in the comments will drift by one, which is a cosmetic concern that can be addressed separately if bothersome.

- [ ] **Step 4: Run the new tests to verify they pass**

Run: `backend/venv/bin/python -m pytest backend/tests/test_compliance_route.py -k "short_circuits_when_already" -v`

Expected: PASS.

- [ ] **Step 5: Run the full compliance route test suite to guard against regressions**

Run: `backend/venv/bin/python -m pytest backend/tests/test_compliance_route.py -v`

Expected: all tests pass (7 total — 5 existing + 2 new).

- [ ] **Step 6: Commit**

```bash
git add backend/app/routes/compliance.py backend/tests/test_compliance_route.py
git commit -m "$(cat <<'EOF'
feat(KAN-6): /compliance short-circuits for already-checked or routed docs

Previously /compliance would re-run check_compliance and re-save even if
the doc had already been compliance_checked or routed. Combined with
save_compliance_result now writing status, that would downgrade a routed
doc's status back to "compliance_checked". Short-circuit returns stored
compliance and leaves status untouched.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Remove duplicate `result.to_dict()` call in `/routing`

**Files:**
- Modify: `backend/app/routes/routing.py:115-133`

- [ ] **Step 1: Verify current test coverage already exercises the response path**

Run: `backend/venv/bin/python -m pytest backend/tests/test_routing_route.py -v`

Expected: all 8 tests pass. They assert on `response["routing"]["recommended_method"]`, so any regression in the response shape will fail them. No new test is required for this refactor.

- [ ] **Step 2: Reuse `routing_dict` in the response body**

In `backend/app/routes/routing.py`, replace the return block at lines 128-133:

```python
    return {
        "document_id": request.document_id,
        "status": "routed",
        "routing_saved": routing_saved,
        "routing": result.to_dict(),  # <- computed again here
    }
```

with:

```python
    return {
        "document_id": request.document_id,
        "status": "routed",
        "routing_saved": routing_saved,
        "routing": routing_dict,
    }
```

- [ ] **Step 3: Run the routing route suite to confirm still green**

Run: `backend/venv/bin/python -m pytest backend/tests/test_routing_route.py -v`

Expected: all 8 tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/app/routes/routing.py
git commit -m "$(cat <<'EOF'
refactor(KAN-6): reuse routing_dict in /routing response body

The comment at routing.py:115 already said "compute once" but the return
body called result.to_dict() a second time. Dead work with no observable
difference — same object content, two allocations per request.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: End-to-end pipeline integration test

**Files:**
- Create: `backend/tests/test_pipeline_integration.py`

- [ ] **Step 1: Write the integration test**

Create `backend/tests/test_pipeline_integration.py` with the following content. It reuses the `FakeClient` + `load_firestore_module` loader pattern from `test_firestore.py` to drive all four save functions against a single in-memory store, then re-runs the terminal save and asserts semantic equality ignoring timestamps:

```python
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
                    result[key], value
                )
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
            )
            await module.save_extraction(
                "pipeline-doc",
                {"fields": {"invoice_amount": {"value": "47500"}}},
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
            )
            await module.save_routing_result(
                "pipeline-doc",
                {
                    "recommended_method": "usdc_stellar",
                    "total_savings_usd": Decimal("1250.50"),
                },
            )

        client = FakeClient.instances[-1]
        saved = client.store["pipeline-doc"]

        self.assertEqual(saved["status"], "routed")
        self.assertEqual(saved["routing_total_savings_usd"], "1250.50")
        self.assertEqual(saved["routing_recommended_method"], "usdc_stellar")
        self.assertIsInstance(saved["routing_total_savings_usd"], str)

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
            )
            await module.save_extraction(
                "rerun-doc",
                {"fields": {"invoice_amount": {"value": "10000"}}},
            )
            await module.save_analysis(
                "rerun-doc",
                {
                    "fraud_assessment": {"score": 5, "flags": []},
                    "compliance_assessment": {"level": "LOW",
                                              "missing_documents": []},
                    "routing_recommendation": {"recommended_method": "wise"},
                },
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
            )
            routing_payload = {
                "recommended_method": "wise",
                "total_savings_usd": Decimal("300.00"),
            }
            await module.save_routing_result("rerun-doc", routing_payload)

            client = FakeClient.instances[-1]
            first_snapshot = strip_timestamps(dict(client.store["rerun-doc"]))

            # Re-run the terminal save with the same input. Timestamps
            # will drift (clock advanced), but every other field must
            # converge to the same state — that is the KAN-6 idempotency
            # contract as written in docs/CLAUDE.md's Money Math policy.
            await module.save_routing_result("rerun-doc", routing_payload)
            second_snapshot = strip_timestamps(dict(client.store["rerun-doc"]))

        self.assertEqual(first_snapshot, second_snapshot)
        self.assertEqual(first_snapshot["status"], "routed")
        self.assertEqual(
            first_snapshot["routing_total_savings_usd"], "300.00"
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the integration test to verify it passes**

Run: `backend/venv/bin/python -m pytest backend/tests/test_pipeline_integration.py -v`

Expected: 2 tests pass.

- [ ] **Step 3: Run the full test suite to confirm overall green**

Run: `backend/venv/bin/python -m pytest backend/tests/ -v`

Expected: all tests pass. Actual count at PR #30 time is 82 tests (the plan's original 60 baseline was stale in `docs/CLAUDE.md` — the real baseline included the auth suite which was already merged). Increment: +1 (Task 1) + 2 (Task 2) + 2 (Task 3) + 2 (Task 5) + 1 (Review A negative test) = 8 new tests on top of the real 74-test baseline.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_pipeline_integration.py
git commit -m "$(cat <<'EOF'
test(KAN-6): end-to-end pipeline integration test with idempotent re-run

Drives create -> extract -> analyze -> compliance -> route against the
FakeClient loader and asserts the final doc has status="routed",
routing_total_savings_usd stored as a Decimal string, and that a second
save_routing_result call converges to the same semantic state modulo
timestamps — the ceo-scope success signal for KAN-6.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Close out KAN-6, KAN-7, KAN-24, KAN-25 in docs/CLAUDE.md

**Files:**
- Modify: `docs/CLAUDE.md`

- [ ] **Step 1: Update the Phase 2 status line for KAN-6**

In `docs/CLAUDE.md`, find the line that currently reads:

```text
- Firestore analysis results update (KAN-6) 🔄 Next Up
```

Replace it with:

```text
- Firestore analysis results update (KAN-6) ✅ Done
```

- [ ] **Step 2: Move KAN-6, KAN-7, KAN-24, KAN-25 out of the TO DO list**

In the Jira board section of `docs/CLAUDE.md`, remove these four lines from the TO DO list:

```text
- KAN-6:  Update Firestore with analysis results
- KAN-7:  Refactor Firestore client to singleton (tech-debt)
- KAN-24: save_routing_result update status to "routed" (tech-debt)
- KAN-25: routing_total_savings_usd store as normalized Decimal string (tech-debt)
```

- [ ] **Step 3: Add the four tickets to the DONE list**

Add these four lines to the DONE list (under KAN-23) in `docs/CLAUDE.md`:

```text
- KAN-6:  Update Firestore with analysis results
- KAN-7:  Refactor Firestore client to singleton
- KAN-24: save_routing_result update status to "routed"
- KAN-25: routing_total_savings_usd store as normalized Decimal string
```

Update the DONE count header accordingly (should become 9 — 5 prior + 4 new).

Update the TO DO count header to subtract 4 (was 20 after prior cleanup; becomes 16).

- [ ] **Step 4: Update the "Last updated" footer**

Replace the existing footer line `*Last updated: April 2026 (...)*` with:

```text
*Last updated: April 2026 (KAN-6 pipeline persistence closed; KAN-7/24/25 tech-debt closed inline)*
```

- [ ] **Step 5: Verify no other doc references KAN-6 as open**

Run this search to confirm no stragglers:

```text
Grep pattern: "KAN-6:.*(To Do|TO DO|In Progress)"
```

Expected: no matches after edits. If any remain, fix them in the same commit.

- [ ] **Step 6: Commit**

```bash
git add docs/CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(KAN-6): mark KAN-6 and overlapping tech-debt tickets Done

KAN-6 (Firestore analysis results update) is complete — compliance status
transition persisted, analyze idempotency widened, pipeline integration
test proves semantic convergence on re-run. KAN-7 (singleton client),
KAN-24 (routed status), and KAN-25 (Decimal-string savings) were closed
inline during prior work and are now marked Done.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Final Verification

- [ ] **Step 1: Run the full backend test suite one more time**

Run: `backend/venv/bin/python -m pytest backend/tests/ -v`

Expected: 82 tests pass, 0 failures, 0 errors.

- [ ] **Step 2: Verify git log shows the expected six commits**

Run: `git log --oneline -6`

Expected (top to bottom): docs commit (Task 6), integration test commit (Task 5), routing refactor commit (Task 4), compliance route commit (Task 3), analyze commit (Task 2), firestore service commit (Task 1).

- [ ] **Step 3: Confirm success signal**

Open `backend/tests/test_pipeline_integration.py` and confirm both test methods ran and passed in the Task 5 step-3 run. This is the exact ceo-scope success signal for KAN-6:

> A full pipeline run (`/upload` → `/analyze` → `/compliance` → `/routing`) leaves a single `transactions` doc with `status="routed"`, Decimal-as-string monetary fields, and re-running the final step produces an identical doc (idempotent).
