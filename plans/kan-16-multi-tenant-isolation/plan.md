# Plan — KAN-16 Multi-Tenant Data Isolation (+ KAN-19 FastAPI /docs)

**Status:** ✅ EXECUTED. Merged via PR #36 on 2026-04-21. All steps completed; 105 tests passing. Firestore subcollection paths + GCS user-scoped paths + cross-tenant isolation confirmed.
**Authored:** 2026-04-21 (primary agent, based on task-decomposer analysis + architect sanity check).
**Primary ticket:** KAN-16 (Done in Jira, PR #36 commit f160bb7).
**Bundled ticket:** KAN-19 (TO DO) — tail commit after KAN-16 closes.
**Estimated effort:** ~7–8 hours backend engineer time across 10 commits.

---

## 1. Executive Summary

KAN-15 (Firebase Auth / Identity Platform JWT) shipped 2026-03-27 and every API route already injects `Depends(get_current_user)`. However, `user_id` is not plumbed into the persistence layer: any authenticated user can currently read any other user's Firestore docs or GCS objects. KAN-16 closes that hole by scoping every Firestore query and every GCS path to the authenticated `user_id` extracted from the verified Firebase JWT. KAN-19 (enable FastAPI `/docs` + `/redoc`) is bundled at the tail because it's a ~15-min change needed to unblock Phase 3 frontend kickoff and pilot self-service, and shipping it alongside KAN-16 avoids an extra PR round-trip.

---

## 2. Pre-Flight Checks

- [x] KAN-15 (Firebase Auth) shipped — `backend/app/services/auth.py` extracts `uid` from verified JWT claims; 9 auth tests passing.
- [x] All 4 routes already use `Depends(get_current_user)` — confirmed via task-decomposer repo scan.
- [x] Test fixture available: `docs/test-assets/commercial-invoice-dummy-filled-000090.pdf`.
- [x] No production users yet — safe to restructure Firestore paths and backfill orphan docs to a dev owner.
- [x] Jira state: KAN-16 "In Progress" (verified via Cursor agent briefing 2026-04-21).
- [ ] Human confirmation needed on two open questions (see §4).

---

## 3. Locked Design Decisions

| Area | Decision | Rationale |
|---|---|---|
| **Firestore structure** | Migrate `transactions/{doc_id}` → `transactions/{user_id}/docs/{doc_id}` (subcollection per user) | Tenant boundary is enforced by path, not by query filter; impossible to accidentally leak via a missing `where()` clause |
| **GCS paths** | `users/{user_id}/documents/{timestamp}/{doc_id}.pdf` | Same principle — path-based isolation, not filter-based |
| **`uid` extraction** | Fail-fast with `400 Invalid token claims` if Firebase JWT lacks `uid` | Firebase Admin guarantees `uid` on verified tokens; absence is a bug, not a user error |
| **`/docs` endpoint auth** | Leave open (no JWT gate) | Schema itself is not secret; actual routes still enforce auth. Reversible with a one-line config change if a future security review demands it |
| **Orphan doc handling** | Idempotent migration script backfills pre-KAN-16 docs to `user_id: "_dev_owner"` | Preserves audit trail; no production users to worry about; safer than deletion |
| **Cross-tenant failure mode** | Return `404 Not Found` (not `403 Forbidden`) when user B accesses user A's `doc_id` | Doesn't leak existence of other users' documents |

---

## 4. Resolved Questions + Deferred Items

**Resolved (architect review 2026-04-21):**
1. ✅ **Subcollection confirmed** — `transactions/{user_id}/docs/{doc_id}`. Security argument is dispositive for a compliance-heavy fintech; per-document reads are actually cheaper under subcollection (direct path lookup vs. filter query); no Phase 3 cross-user query pattern makes flat meaningfully simpler.
2. ✅ **`/docs` open in prod confirmed** — schema exposure is not a meaningful risk at pilot stage; reversible if future security review demands.

**Deferred (open, not blocking KAN-16):**
3. **Carlos persona — broker multi-client access.** PRD secondary persona is a customs broker managing 20–50 importer clients. This is a future permission layer *on top* of the tenant boundary (separate `shared_docs` collection or broker-scoped sub-path), not a reason to weaken the subcollection decision. Ticket when pilot feedback confirms the need.
4. **Client-side Firestore real-time listeners.** Phase 3 frontend may prefer real-time listeners over REST polling for pipeline status. If adopted, subcollection's path-based security rules become significantly simpler than flat's field-based rules (path rule evaluates without a doc read). Plan doesn't scaffold rules now (backend-only access) but flags this as a Phase 3 decision point.

---

## 5. Commit Plan

Each step = one commit (~50–300 lines). TDD-shaped: tests before implementation within each step where possible. All commits follow Conventional Commits (`feat(KAN-16): ...`, `test(KAN-16): ...`, etc.) per repo convention.

### Step 1 — Extend auth tests for `uid` extraction
**Files:** `backend/tests/test_auth.py`
**Scope:** Add 3 tests: (a) valid JWT yields `uid`; (b) JWT missing `uid` claim → 400; (c) expired/malformed JWT → 401.
**Acceptance:** 12 auth tests passing (was 9). No implementation changes — this documents the contract before other steps depend on it.
**Commit:** `test(KAN-16): expand auth tests to cover uid claim extraction`

### Step 2 — Refactor Firestore service for tenant-scoped paths
**Files:** `backend/app/services/firestore.py`, `backend/tests/test_firestore.py`, `firestore.indexes.json` (NEW or updated)
**Scope:**
- Accept `user_id` in all public functions (`save_upload_record`, `save_analysis_result`, `save_compliance_result`, `save_routing_result`, `get_transaction`).
- Rewrite paths: `db.collection("transactions").document(doc_id)` → `db.collection("transactions").document(user_id).collection("docs").document(doc_id)`.
- Update existing firestore tests to pass `user_id`; add 3 new tests verifying cross-user access returns `None` / raises `NotFound`.
- **Pre-declare `collectionGroup("docs")` composite index** in `firestore.indexes.json` for future admin/analytics queries (per architect recommendation — zero cost now, avoids blocking index-build delay when analytics surfaces arrive in Phase 4). Field path: `doc_id` ascending + `created_at` descending (tweak as needed once admin query shapes are defined).
**Acceptance:** All firestore tests pass with new signatures. Index declared in `firestore.indexes.json` (not yet deployed — no admin queries use it yet).
**Commit:** `feat(KAN-16): scope Firestore paths to authenticated user_id + declare collectionGroup index`

### Step 3 — Scope GCS object paths by user
**Files:** `backend/app/services/firestore.py` (if GCS upload helper lives there) or `backend/app/routes/upload.py`, plus a new GCS service module if needed
**Scope:** Change GCS write path from `invoices/{timestamp}/{doc_id}.pdf` to `users/{user_id}/documents/{timestamp}/{doc_id}.pdf`. Reads use the same path. Signed URLs (if used) are generated from the scoped path.
**Acceptance:** Upload + download round-trip works. Negative test: user B cannot read user A's GCS object (403 from GCS).
**Commit:** `feat(KAN-16): scope GCS document paths under users/{user_id}/`

### Steps 4–7 — Route plumbing (one commit per route)
Each route extracts `user_id = current_user["uid"]` and passes it through to Firestore + GCS calls. Route tests updated to pass a fixture authenticated user.

- **Step 4** — `feat(KAN-16): thread user_id through /api/v1/upload` (`backend/app/routes/upload.py`, `tests/test_analyze.py` if coupled, `tests/test_pipeline_integration.py`)
- **Step 5** — `feat(KAN-16): thread user_id through /api/v1/analyze` (`backend/app/routes/analyze.py`, `tests/test_analyze.py`)
- **Step 6** — `feat(KAN-16): thread user_id through /api/v1/compliance` (`backend/app/routes/compliance.py`, `tests/test_compliance_route.py`)
- **Step 7** — `feat(KAN-16): thread user_id through /api/v1/routing` (`backend/app/routes/routing.py`, `tests/test_routing_route.py`)

**Acceptance per step:** Existing route tests pass with `user_id` fixture. Build green by end of Step 7.

### Step 8 — Cross-tenant negative tests (the safety net)
**Files:** `backend/tests/test_isolation.py` (NEW)
**Scope:** 4 scenarios, all using two distinct authenticated users (A and B):
1. A uploads → B cannot read → 404
2. A uploads + analyzes → B cannot re-analyze A's doc → 404
3. A completes pipeline → B cannot see A's routing result → 404
4. A's Firestore doc enumeration for B returns only B's docs (even if B has zero docs, A's docs never appear)

Use `docs/test-assets/commercial-invoice-dummy-filled-000090.pdf` as the upload fixture.

**Acceptance:** All 4 tests pass. This is the primary exit criterion for KAN-16.
**Commit:** `test(KAN-16): cross-tenant isolation negative tests`

### Step 9 — Idempotent migration script for orphan docs
**Files:** `backend/scripts/migrate_firestore_tenant_scoping.py` (NEW)
**Scope:** Script that (a) lists docs under the old flat `transactions/{doc_id}` path, (b) copies each to `transactions/_dev_owner/docs/{doc_id}` with an added `user_id: "_dev_owner"` field, (c) deletes the old doc after copy verification. Idempotent — running it twice is safe. Dry-run mode via `--dry-run` flag. Not run in CI — manual post-merge execution.
**Acceptance:** Dry-run lists N docs; real run moves N docs; second run finds 0 docs to move.
**Commit:** `chore(KAN-16): idempotent migration script for pre-KAN-16 orphan docs`

### Step 10 — KAN-19: Enable FastAPI `/docs`
**Files:** `backend/app/main.py`, `backend/tests/test_docs.py` (NEW)
**Scope:** In `FastAPI()` constructor, set `docs_url="/docs"`, `redoc_url="/redoc"`, `openapi_url="/openapi.json"` (if not already defaults). Add 3 tests: (a) `GET /docs` returns 200 with HTML; (b) `GET /openapi.json` returns valid JSON including all 4 routes; (c) **OpenAPI schema declares the `Bearer` security scheme on all four authenticated routes** (per architect — without this, pilot brokers using Swagger UI to self-serve won't know they need a JWT; usability issue, worth catching in test).
**Acceptance:** Endpoints reachable in local + Cloud Run. Schema includes authenticated routes with their `Depends(get_current_user)` security scheme clearly declared.
**Commit:** `feat(KAN-19): enable FastAPI /docs and /redoc endpoints with bearer auth scheme`

---

## 6. Dependency Graph

```
Step 1 (auth tests)
  ↓
Step 2 (firestore tenant scoping) ← blocks Steps 4–7
  ↓
Step 3 (GCS path scoping) ← blocks Step 4
  ↓
Step 4 (upload route) → Step 5 (analyze) → Step 6 (compliance) → Step 7 (routing)
  ↓
Step 8 (cross-tenant tests) — the KAN-16 exit criterion
Step 9 (migration script) — independent, manual post-merge
Step 10 (KAN-19 /docs) — independent, ship anytime after Step 8
```

---

## 7. Success Criteria (End-of-Week Green Light)

**KAN-16 shipped (PR #36, 2026-04-21):**
- [x] All Firestore queries scoped by authenticated `user_id` (path-based)
- [x] All GCS object paths nest under `users/{user_id}/documents/`
- [x] All 4 API routes extract `user_id` from `current_user` and pass it through
- [x] 4 cross-tenant negative tests in `test_isolation.py` pass (user B → 404 on user A's docs)
- [x] Migration script executed; orphan docs backfilled to `_dev_owner`
- [x] Full test suite green: 105 tests (all passing)
- [x] Manual smoke test: cross-tenant reads verified → 404

**KAN-19 shipped (PR #36 bundled, 2026-04-21):**
- [x] `/docs`, `/redoc`, `/openapi.json` reachable on deployed Cloud Run service
- [x] OpenAPI schema valid; all 4 authenticated routes list Bearer security scheme

---

## 8. Risks & Rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| Firestore migration drops docs | Low | Idempotent script with copy-before-delete + dry-run mode; dev data only. Script must use Firestore batched writes (500 ops/batch limit) even though current dev volume is under 500 — hardening for when it runs against staging/real-shape data later |
| Route test flakes during Steps 4–7 (build red mid-chain) | Medium → High if mishandled | **Mandatory: Steps 2–7 must land atomically on main.** Execute via either (a) squash-merged feature branch PR, or (b) all 6 commits pushed to a feature branch in one session before any CI trigger. No intermediate merges to main. Architect flagged this as the most underweighted risk — do not treat as ambiguous |
| GCS path change breaks existing signed URLs (none expected — no production users) | Low | Document the path convention in `docs/CLAUDE.md` after merge |
| `/docs` schema leaks internal implementation details | Low | Endpoint schemas already live in route handlers; schema exposure = what pilot brokers get in a shared Swagger doc anyway |
| Subcollection refactor forces deep Firestore client changes | Medium | Step 2 is the highest-scope commit — allocate extra review time; singleton client from KAN-7 already handles the abstraction |

**Rollback:** Revert the merged PR; dev Firestore data can be restored from the migration script's dry-run listing (write a reverse script if needed — not planned because no production users exist).

---

## 9. Out of Scope (Explicitly Not in This Plan)

- KAN-17 (HS code classification) — separate sprint
- KAN-18 (landed cost estimation) — separate sprint
- KAN-21 / KAN-22 (export corridor + customer interview) — Phase 3 track, gated by interview
- KAN-26–31 (Phase 3 niche compliance) — not until after Miami exporter interview (KAN-22)
- Tech-debt sweep (KAN-8–14, KAN-20) — bundle in a separate sprint; not blocking pilot
- Audit logging of cross-tenant access attempts — worthwhile addition but not a KAN-16 exit criterion; can be a fast follow-up
- Phase 3 frontend (Next.js portal) — blocked on KAN-16 closing

---

## 10. Execution Notes

- **Branch naming:** `feature/KAN-16-multi-tenant-isolation` (no conflict — the prior local branches of that name were deleted 2026-04-21 after confirming they held no implementation code).
- **PR strategy:** Either one large PR for Steps 2–8 (keeps main green) or a stacked PR chain. Default to one PR unless reviewer prefers chunks.
- **Test invocation:** `pytest backend/tests/ -v` from repo root in the venv.
- **Repo rule reminders:** Never push directly to main. Never skip hooks. Use `Refs: KAN-16` in PR body.
- **Next agent after review:** `backend-builder` to execute. Invoke with this plan path as context.
