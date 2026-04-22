# Jira Board Snapshot — Puente AI

**Source:** Jira MCP (`searchJiraIssuesUsingJql`) + direct Jira updates applied in-session.
**Point in time:** 2026-04-22 (late — post Gemini/Document AI incident close-out).
**Purpose:** Fast, high-resolution board snapshot for future sessions without re-scraping Jira.

---

## Context

- **Project:** Puente AI — AI-native invoice intelligence + compliance + payment routing.
- **Jira site:** [jaysworkspace-37010190.atlassian.net](https://jaysworkspace-37010190.atlassian.net)
- **Project key:** `KAN`
- **Cloud ID:** `a077f57a-6ec3-4caf-adae-22ce16a35c1c`

## Ticket counts (2026-04-22, late)

- **Total:** 44 (`KAN-1` through `KAN-44`)
- **Done:** 18
- **In Progress / In Review:** 2
- **To Do:** 24
- **Unassigned:** 5 (`KAN-20`, `KAN-28`, `KAN-29`, `KAN-30`, `KAN-31`)

Change since previous snapshot: KAN-42, KAN-43, KAN-44 moved to Done after the 2026-04-22 Gemini/Document AI incident close-out (see Done table below).

---

## Done (18) — shipped

| Key | Type | Summary |
|---|---|---|
| KAN-2 | Story | Enable Vertex AI Document AI to extract invoice fields |
| KAN-3 | Story | Build Gemini Flash analysis endpoint |
| KAN-4 | Story | Add compliance gap detection |
| KAN-5 | Story | Build payment routing recommendation |
| KAN-6 | Story | Update Firestore with analysis results |
| KAN-7 | Task | Refactor Firestore client singleton + async/sync fix |
| KAN-15 | Feature | Add authentication via Firebase JWT |
| KAN-16 | Feature | Multi-tenant data isolation (PR #36, 2026-04-21) |
| KAN-19 | Feature | FastAPI docs enabled (`/docs`, `/redoc`) (PR #36 bundled, 2026-04-21) |
| KAN-23 | Feature | Build `POST /api/v1/routing` endpoint |
| KAN-24 | Task | Update top-level transaction status to `routed` after persistence |
| KAN-25 | Task | Store `routing_total_savings_usd` as float |
| KAN-33 | Task | Remove silent demo fallback in `AnalyzePage` |
| KAN-34 | Task | Wire JWT through `authedFetch` + `RequireAuth` |
| KAN-35 | Task | Logout button + reset-password route + `VITE_API_URL` |
| KAN-42 | Task | Vertex Express API key auth branch in `get_gemini_client()` (PR #38, 2026-04-22) |
| KAN-43 | Task | AI Studio PAYG plan upgrade + Cloud Run env flip to unblock `/analyze` (ops-only, 2026-04-22) |
| KAN-44 | Task | Document AI Invoice Parser v2 entity-type mapping fix + partial-drift detection (PR #39 + PR #40, 2026-04-22) |

Notes from latest update pass:

- `KAN-16` has a comment tying completion to PR #36 (`f160bb7`) and 105 tests.
- `KAN-19` has a comment tying completion to PR #36 (`f9a6b4a`) and `test_docs.py`.
- `KAN-42` lands as a future-toggle: the `puente-ai-dev` project-level Vertex block still 404s even against Vertex Express, so Cloud Run runs the AI Studio branch. Branch/commit history uses the obsolete "KAN-52" identifier — no git rewrite planned.
- `KAN-43` is ops-only: no commits, but the code path it activates is the `GEMINI_API_KEY` fallback that KAN-42 wired. Post-close-out action: rotate the AI Studio key (was echoed in debugging session output).
- `KAN-44` ships the Invoice Parser v2 snake_case fix (PR #39: `0f2da66`, `c553cd9`) plus CodeRabbit/Copilot follow-ups (PR #40: `83b6a7e`, `c0410cc`). CI workflow also switched `--set-env-vars` → `--update-env-vars` to stop future deploys wiping manually-set runtime env vars. Test suite: 113 passing (added `backend/tests/test_document_ai.py` with 8 tests pinning the v2 contract and drift-detection semantics).

---

## In Progress / In Review (2)

- **KAN-32** (Feature, High) — Frontend auth wire-up + demo-fallback cleanup rollup parent. Stays open until KAN-36 + KAN-37 close.
- **KAN-37** (Task, Highest) — CORS + Firebase authorized domains blocker.
  - Backend CORS portion is shipped (PR #35, `5edce5c`).
  - Remaining manual step: founder adds the Lovable preview/published domain under Firebase Console → Auth → Settings → Authorized domains before closure.

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

1. **End-to-end verify `/analyze` + `/routing` from Lovable preview.** All three KAN-44 fixes are live on Cloud Run (PR #39 mapping, PR #40 drift detection, PR #41 model default). Primary evidence of success: `/routing` returns a recommendation instead of `422 Transaction amount is required`. Secondary signal: Cloud Run logs are clean of `processor-version drift` warnings (any match points to a concrete entity-type rename worth chasing).
2. **Rotate the AI Studio API key (founder, ~2 min).** Current `GEMINI_API_KEY` was echoed in debugging session output. Create new key at aistudio.google.com/app/apikey → `gcloud run services update puente-backend --update-env-vars GEMINI_API_KEY=NEW_KEY --region us-central1` → revoke old key.
3. **Finish KAN-37 manual step** (Firebase Authorized Domains), then close KAN-37 and likely KAN-32 rollup.
4. **KAN-36 (frontend):** replace mock data on /dashboard, /explorer, /insights, /transactions with real API queries, or ship a visible "Demo data" badge.
5. **KAN-39 (tech-debt, ~1 hour):** add a required-env-var assertion step to `backend-deploy.yml`. The `--set-env-vars` → `--update-env-vars` fix shipped in PR #39 stops deploys from *wiping* env vars; KAN-39 stops deploys from *promoting traffic* when a required var is missing. Complementary guardrails.
6. **Close KAN-1 parent epic** — all child stories are Done; only the epic itself remains open.
7. **Triage unassigned hardening/compliance work** (`KAN-20`, `KAN-28–31`) once the demo loop closes. `KAN-26`–`KAN-31` are currently PARKED pending strategic reframe.

---

## Repo pointers

- Project guide: [docs/CLAUDE.md](./CLAUDE.md)
- Session brief template: [docs/CLAUDE_SESSION_BRIEF_TEMPLATE.md](./CLAUDE_SESSION_BRIEF_TEMPLATE.md)
- Active backend plan history: [plans/kan-16-multi-tenant-isolation/plan.md](../plans/kan-16-multi-tenant-isolation/plan.md)
- Live API: https://puente-backend-519686233522.us-central1.run.app

---

*Jira is source of truth. Refresh this file after any status transition, major comment policy change, or ticket creation/deprecation decision.*
