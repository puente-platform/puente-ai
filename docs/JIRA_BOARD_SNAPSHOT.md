# Jira Board Snapshot — Puente AI

**Source:** Jira MCP (`searchJiraIssuesUsingJql`) + direct Jira updates applied in-session.
**Point in time:** 2026-04-22.
**Purpose:** Fast, high-resolution board snapshot for future sessions without re-scraping Jira.

---

## Context

- **Project:** Puente AI — AI-native invoice intelligence + compliance + payment routing.
- **Jira site:** [jaysworkspace-37010190.atlassian.net](https://jaysworkspace-37010190.atlassian.net)
- **Project key:** `KAN`
- **Cloud ID:** `a077f57a-6ec3-4caf-adae-22ce16a35c1c`

## Ticket counts (2026-04-22)

- **Total:** 43 (`KAN-1` through `KAN-43`)
- **Done:** 15
- **In Progress / In Review:** 4
- **To Do:** 24
- **Types:** 5 Stories, 22 Tasks, 16 Features
- **Priority mix:** 37 Medium, 3 High, 3 Highest
- **Unassigned:** 5 (`KAN-20`, `KAN-28`, `KAN-29`, `KAN-30`, `KAN-31`)

---

## Done (15) — shipped

| Key | Type | Summary |
|---|---|---|
| KAN-2 | Story | Enable Vertex AI Document AI to extract invoice fields |
| KAN-3 | Story | Build Gemini Flash analysis endpoint |
| KAN-4 | Story | Add compliance gap detection |
| KAN-5 | Story | Build payment routing recommendation |
| KAN-6 | Story | Update Firestore with analysis results |
| KAN-7 | Task | Refactor Firestore client singleton + async/sync fix |
| KAN-15 | Feature | Add authentication via Firebase JWT |
| KAN-16 | Feature | Multi-tenant data isolation (moved to Done 2026-04-22 update pass) |
| KAN-19 | Feature | FastAPI docs enabled (`/docs`, `/redoc`) (moved to Done 2026-04-22 update pass) |
| KAN-23 | Feature | Build `POST /api/v1/routing` endpoint |
| KAN-24 | Task | Update top-level transaction status to `routed` after persistence |
| KAN-25 | Task | Store `routing_total_savings_usd` as float |
| KAN-33 | Task | Remove silent demo fallback in `AnalyzePage` |
| KAN-34 | Task | Wire JWT through `authedFetch` + `RequireAuth` |
| KAN-35 | Task | Logout button + reset-password route + `VITE_API_URL` |

Notes from latest update pass:

- `KAN-16` has a comment tying completion to PR #36 (`f160bb7`) and 105 tests.
- `KAN-19` has a comment tying completion to PR #36 (`f9a6b4a`) and `test_docs.py`.

---

## In Progress / In Review (4)

- **KAN-32** (Feature, High) — Frontend auth wire-up + demo-fallback cleanup rollup parent.
- **KAN-37** (Task, Highest) — CORS + Firebase authorized domains blocker.
  - Backend CORS portion is shipped (PR #35, `5edce5c`).
  - Remaining manual step: Firebase Authorized Domains update before closure.
- **KAN-42** (Task, High, **In Review**) — Vertex Express API key auth for Gemini client.
  - PR [#38](https://github.com/puente-platform/puente-ai/pull/38) on `feat/vertex-express-gemini-auth` (commits `d14fbab`, `fe9bf67`), 107/107 tests passing, Copilot + CodeRabbit review comments addressed.
  - Shipped to give `get_gemini_client()` a Vertex Express branch (priority #1 over AI Studio and SA/ADC).
  - **Runtime-blocked today.** Vertex Express curl against `puente-ai-dev` returned the same 404 we've seen from SA and owner auth — the project-level Vertex allowlist/consent issue swallows every Vertex AI endpoint regardless of auth mechanism. Evidence in terminal session `1.txt:886-925`.
  - **Closure criteria revised:** merges when CI green + review approved. Runtime verification of the Vertex Express path specifically is deferred until the project-level block clears — at that point we flip Cloud Run env vars back with no code change.
  - Today's `/analyze` unblock pivots to AI Studio (see `KAN-43`).
  - **Naming note:** branch name and commit messages use the obsolete identifier "KAN-52"; Jira auto-assigned this work as KAN-42. No git history rewrite planned.
- **KAN-43** (Task, Highest, **In Progress**) — AI Studio Pay-as-you-go unblock for `/analyze` (Vertex project-level 404 workaround).
  - The one endpoint that got past auth during the 2026-04-22 incident was AI Studio (`generativelanguage.googleapis.com`) — it returned a clean `429 RESOURCE_EXHAUSTED, limit: 0`, meaning the AI Studio key + endpoint + project wiring all work; only the AI Studio plan tier is gating at Free.
  - Operational steps (no code change — PR #38's #2 fallback branch already routes AI Studio): upgrade `puente-ai-dev` AI Studio plan Free → Pay-as-you-go at `aistudio.google.com/app/plan`; set `GEMINI_API_KEY` + `GEMINI_MODEL` on Cloud Run (ideally via Secret Manager); remove `VERTEX_API_KEY` from Cloud Run; end-to-end smoke test `/analyze` from the Lovable preview.
  - Rollback-to-Vertex plan: when the project-level block on `puente-ai-dev` clears, swap Cloud Run env vars (`VERTEX_API_KEY` in, `GEMINI_API_KEY` out) with zero code change.
  - Post-unblock: rotate the AI Studio key — it lived in shared LLM session context during debugging.

---

## To Do (24) — grouped by theme

### Epic / lifecycle

- **KAN-1** — Phase 2 Invoice Intelligence Pipeline epic (child delivery largely complete, parent still open).

### Backend hardening / tech debt

- **KAN-8** — Add `asyncio.to_thread()` in analyze path
- **KAN-9** — `analyze.py` cleanup + status handling fix
- **KAN-10** — Firestore success-path cleanup (`error`, `updated_at`, merge docs)
- **KAN-11** — Upload atomicity and cleanup on partial failure
- **KAN-12** — Sanitize client-facing upload errors
- **KAN-13** — Document AI highest-confidence field selection
- **KAN-14** — Rename `VERTEX_AI_LOCATION` to clearer shared location var
- **KAN-20** — Reject invalid country codes (no silent `"US"` default)
- **KAN-38** — Fix default Gemini location in `backend/app/services/gemini.py` (`global` fallback -> `us-central1`) + add unit test
- **KAN-39** — Assert required Cloud Run env vars in `backend-deploy.yml` and fail workflow if required vars are missing
- **KAN-40** — Document required runtime service-account IAM roles and exact `gcloud` binding commands
- **KAN-41** — Align `VERTEX_AI_LOCATION` / `GCP_LOCATION` naming semantics (coordinate with `KAN-14`)

### Discovery / strategy-coupled

- **KAN-17** — HS code classification
- **KAN-18** — Landed cost estimation
- **KAN-21** — Export corridor compliance rules
- **KAN-22** — Customer interviews

### Phase 3 surfaces and compliance UX

- **KAN-26** — Phase 3 parent
- **KAN-27** — OFAC/SDN screening engine
- **KAN-28** — HTS detection + confidence scoring
- **KAN-29** — Antidumping/CVD checks
- **KAN-30** — Plain-language compliance summaries
- **KAN-31** — Risk/compliance UX integration
- **KAN-36** — Label/wire remaining demo surfaces

---

## Strategic hygiene applied on 2026-04-22

- Added **PARKED** comments to `KAN-17`, `KAN-21`, and `KAN-26` through `KAN-31`:
  - "PARKED 2026-04-21 pending strategic reframe. Do not assign or start. Re-evaluate after FinCEN MSB is filed and first paying broker pilot lands."
- Added rollup note on `KAN-32` that it stays in progress until `KAN-36` and `KAN-37` close.
- Assigned frontend rollup tickets to Jay: `KAN-32`, `KAN-33`, `KAN-34`, `KAN-35`, `KAN-36`, `KAN-37`.
- Created four new Medium-priority, `tech-debt` labeled, Jay-assigned tasks during refresh pass.
- Jira auto-assigned these as `KAN-38` through `KAN-41` (requested "KAN-45–48" numbering cannot be forced at create-time).

---

## Operational focus for next session

1. **Unblock `/analyze` via AI Studio (`KAN-43`, Highest):** upgrade `puente-ai-dev` AI Studio plan to Pay-as-you-go; set `GEMINI_API_KEY` + `GEMINI_MODEL` on Cloud Run and remove `VERTEX_API_KEY`; verify `/analyze` returns 200 from Lovable; rotate the AI Studio key. This is the actual production-unblock.
2. Merge PR #38 (`KAN-42`) to land the Vertex Express branch in code as a future-toggle path, then move `KAN-42` to Done (runtime verification of the Vertex Express path is deferred per `KAN-43` runtime-block note).
3. Finish the manual Firebase Authorized Domains step, then close `KAN-37`.
4. Decide whether to close `KAN-1` parent epic now that most Phase 2 children are done.
5. Triage unassigned hardening/compliance work: `KAN-20`, `KAN-28` to `KAN-31`.
6. Execute tech-debt queue (`KAN-38` to `KAN-41`) to harden deploy/runtime reliability.

---

## Repo pointers

- Project guide: [docs/CLAUDE.md](./CLAUDE.md)
- Session brief template: [docs/CLAUDE_SESSION_BRIEF_TEMPLATE.md](./CLAUDE_SESSION_BRIEF_TEMPLATE.md)
- Active backend plan history: [plans/kan-16-multi-tenant-isolation/plan.md](../plans/kan-16-multi-tenant-isolation/plan.md)
- Live API: https://puente-backend-519686233522.us-central1.run.app

---

*Jira is source of truth. Refresh this file after any status transition, major comment policy change, or ticket creation/deprecation decision.*
