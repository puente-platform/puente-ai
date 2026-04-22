# CLAUDE.md — Puente AI Codebase Context

This file gives AI assistants (Claude, Cursor) permanent 
context about the Puente AI codebase so engineers don't 
need to re-explain the project on every session.

---

## What This Project Is

Puente AI is an AI-powered trade intelligence and payment 
infrastructure platform for the Americas. It serves 
Miami-based SME importers (primary persona: "Maria") who 
move goods between the US and LATAM markets.

Core value proposition: upload a trade document → AI 
extracts data → fraud score + compliance check + payment 
routing recommendation in <15 seconds.

---

## Current Build Status

Phase 1 — Complete
- FastAPI backend deployed on GCP Cloud Run
- PDF upload → GCS storage working
- Firestore transaction records working
- GitHub Actions CI/CD auto-deploys on push to main

Phase 2 — Complete (invoice intelligence pipeline shipped end-to-end)
- Vertex AI Document AI invoice extraction (KAN-2) ✅ Done
- Gemini Flash analysis endpoint (KAN-3) ✅ Done
- Compliance gap detection (KAN-4) ✅ Done
- Payment routing engine service (KAN-5) ✅ Done
- POST /api/v1/routing endpoint (KAN-23) ✅ Done (PR #21 merged 2026-03-24)
- Firestore analysis results persistence (KAN-6) ✅ Done (PR #30 merged 2026-04-20)
- Firestore singleton + async/sync fix (KAN-7) ✅ Done (PR #30)
- Firebase Auth / GCP Identity Platform JWT (KAN-15) ✅ Done (2026-03-27)
- Multi-tenant data isolation (KAN-16) ✅ Done (PR #36 merged 2026-04-21) — path-based Firestore subcollection `transactions/{user_id}/docs/{doc_id}` + scoped GCS paths `users/{user_id}/documents/...`; cross-tenant reads return 404
- FastAPI /docs + /redoc with Bearer security (KAN-19) ✅ Done (PR #36 bundled)
- CORS regex expanded for `*.lovableproject.com` frontend preview (PR #35 merged 2026-04-21; half of Jira KAN-37)

Phase 3 — Frontend hardening in flight (Lovable-built Vite + React app)
- Silent demo fallback removed from AnalyzePage (KAN-33) ✅ Done
- JWT `authedFetch` + `RequireAuth` route gating (KAN-34) ✅ Done
- Logout dropdown + /reset-password route + `VITE_API_URL` env var (KAN-35) ✅ Done
- Mock data replacement on /dashboard, /explorer, /insights, /transactions (KAN-36) ⏳ To Do
- Firebase Console authorized-domains for Lovable preview (KAN-37 second half) ⏳ Manual founder action

Test Coverage: 105 tests passing
- test_analyze.py (6 tests)
- test_auth.py (12 tests)
- test_compliance.py (14 tests)
- test_compliance_route.py (8 tests)
- test_docs.py (3 tests) ← KAN-19
- test_firestore.py (14 tests)
- test_gemini.py (4 tests)
- test_isolation.py (4 tests) ← KAN-16 cross-tenant
- test_migrate_script.py (5 tests) ← KAN-16 migration
- test_payment_routing.py (20 tests)
- test_pipeline_integration.py (2 tests)
- test_routing_route.py (8 tests)
- test_upload_route.py (5 tests)

---

## Live URLs

Production API:
https://puente-backend-519686233522.us-central1.run.app

Endpoints (live):
- GET  /health
- GET  /
- GET  /docs               ← KAN-19 Swagger UI with Bearer auth scheme declared
- GET  /redoc              ← KAN-19
- GET  /openapi.json       ← KAN-19 machine-readable schema
- POST /api/v1/upload      ← scoped to `users/{uid}/documents/...` per KAN-16
- POST /api/v1/analyze     ← requires `DOCUMENT_AI_PROCESSOR_ID` env var on Cloud Run
- POST /api/v1/compliance
- POST /api/v1/routing     ← KAN-23

Frontend (Lovable preview):
`https://{lovable-preview-subdomain}.lovableproject.com`
- Env var: `VITE_API_URL` (defaults to the Cloud Run URL above)
- Auth: Firebase Auth with `authedFetch` attaching `Authorization: Bearer {idToken}`

---

## Tech Stack

Backend:
- Python 3.11, FastAPI, Uvicorn
- GCP Cloud Run (us-central1)
- GCP Cloud Storage (bucket: puente-documents-dev)
- GCP Firestore (database: default, collection: transactions; subcollection: docs)
- Vertex AI Gemini Flash + Document AI
- Firebase Auth / GCP Identity Platform

Frontend:
- Vite + React + TypeScript + shadcn/ui + TailwindCSS
- Firebase Auth client SDK
- Built and hosted via Lovable (project `11330f28-95e3-48bf-8f58-776e62b33067`)
- Repo: `github.com/puente-platform/puente-ai-insights` (private)
- The in-repo `frontend/` directory is a **legacy Vite scaffold** that predates the Lovable-built app. It is not deployed, not wired into CI, and kept only for reference. All active frontend work happens in the Lovable repo above.

CI/CD:
- GitHub Actions → .github/workflows/backend-deploy.yml
- Triggers on push to main when backend/** changes
- Triggers on all PRs (docs-only PRs skip build, pass CI)
- Builds Docker image → Artifact Registry → Cloud Run

---

## Repository Structure

puente-ai/
├── .github/workflows/backend-deploy.yml
├── firestore.indexes.json       ← KAN-16: collectionGroup("docs") composite index
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry, CORS, router registration, /docs override with Bearer scheme
│   │   ├── routes/
│   │   │   ├── upload.py        ← POST /api/v1/upload (KAN-16 user_id plumbing, Annotated dep)
│   │   │   ├── analyze.py       ← POST /api/v1/analyze (KAN-3)
│   │   │   ├── compliance.py    ← POST /api/v1/compliance (KAN-4)
│   │   │   └── routing.py       ← POST /api/v1/routing (KAN-23)
│   │   └── services/
│   │       ├── auth.py          ← Firebase JWT verifier, `get_current_user` (KAN-15)
│   │       ├── firestore.py     ← All Firestore ops; user_id keyword-only (KAN-16)
│   │       ├── document_ai.py   ← Document AI extraction (KAN-2)
│   │       ├── gemini.py        ← Gemini Flash analysis (KAN-3)
│   │       ├── compliance.py    ← Rule-based compliance (KAN-4)
│   │       └── payment_routing.py ← Routing engine (KAN-5)
│   ├── scripts/
│   │   └── migrate_firestore_tenant_scoping.py ← KAN-16 idempotent migration, --dry-run, 500-op batches
│   ├── tests/ (105 tests)
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── PRD.md
│   ├── CLAUDE.md                ← this file
│   ├── JIRA_BOARD_SNAPSHOT.md   ← per-ticket detail, refreshed by Cursor MCP
│   ├── FOUNDER_SCORECARD.md     ← weekly Friday review template
│   ├── WEEKLY_OPERATING_RHYTHM.md
│   ├── MONDAY_PLANNING_TEMPLATE.md
│   ├── CLAUDE_SESSION_BRIEF_TEMPLATE.md
│   ├── NOTICE.md
│   └── test-assets/
│       └── commercial-invoice-dummy-filled-000090.pdf ← KAN-16 test fixture
├── plans/
│   └── kan-16-multi-tenant-isolation/plan.md ← executed, branch merged
├── frontend/                     ← LEGACY pre-Lovable Vite scaffold, not deployed
└── (active frontend lives in `puente-platform/puente-ai-insights` — see Tech Stack)

---

## Jira Board — Summary

Full ticket-by-ticket detail lives in `docs/JIRA_BOARD_SNAPSHOT.md` (refreshed via Cursor's Atlassian MCP). Canonical source of truth: `jaysworkspace-37010190.atlassian.net/KAN`.

As of 2026-04-21: **37 total tickets, 15 Done, 2 In Progress, 20 To Do.**

DONE (15)
- KAN-2, 3, 4, 5, 6, 7, 15, 23 — invoice pipeline + auth (shipped 2026-03 through 2026-04-20)
- KAN-24 — `save_routing_result` writes top-level `status="routed"` after successful persistence, so `GET /transaction/{id}` reflects the `/routing` response (shipped 2026-04-20)
- KAN-25 — `routing_total_savings_usd` persisted as a float (narrow, documented exception to the Decimal-string money policy — see Money Math section)
- KAN-16 — multi-tenant data isolation (PR #36, 2026-04-21)
- KAN-19 — FastAPI /docs + Bearer scheme (PR #36 bundled, 2026-04-21)
- KAN-33, 34, 35 — Lovable frontend auth hardening (shipped 2026-04-21)

IN PROGRESS (2)
- KAN-32 — Frontend auth wire-up rollup parent; stays open until KAN-36 + KAN-37 close
- KAN-37 — CORS + Firebase authorized domains; backend CORS half shipped via PR #35 (commit `5edce5c`), Firebase Console step is founder-manual

TO DO — active
- KAN-36 — Mock data replacement on /dashboard, /explorer, /insights, /transactions
- KAN-22 — Miami importer interviews (strategic priority — target 10, not 1, per Perplexity diligence report)

TO DO — backend hardening (parked until strategic reframe closes)
- KAN-8, 9, 10, 11, 12, 13, 14, 20 — pre-pilot tech debt
- KAN-18 — landed cost estimation (reframe candidate: "real-time Trump tariff volatility calculator")

TO DO — PARKED by Cursor agent 2026-04-21 pending strategic reframe
- KAN-17 — HS code classification (KlearNow.AI is already at 95%; likely integrate rather than build)
- KAN-21 — US→LATAM export corridor (imports are the wedge; park)
- KAN-26 through KAN-31 — Phase 3 Jewish-importer niche work (reframe candidate: Miami Latino importer community / goTRG network)

TO DO — legacy
- KAN-1 — Phase 2 invoice intelligence epic (all child stories shipped; epic status close pending)

NOT YET CREATED (strategic, from Perplexity diligence — hold until this week's demo loop closes)
- KAN-38 FinCEN MSB registration, KAN-39 Florida MTL filing, KAN-40 customs broker POA, KAN-41 broker white-label API, KAN-42 Miami↔LATAM compliance API, KAN-43 Venezuela OFAC premium tier, KAN-44 trade-credit dataset schema

---

## Key Conventions

Commit messages (Conventional Commits):
- feat(KAN-X): new feature
- fix(KAN-X): bug fix
- docs: documentation only
- ci: CI/CD changes
- chore: maintenance

**Jira ↔ commit-label caveat (2026-04-21):** PR #35 CORS work landed with commits labeled `fix(KAN-33)` before Cursor locked the Jira numbering. The Jira-canonical ticket for CORS is **KAN-37**, and KAN-33 is actually "Remove silent demo fallback" (Lovable). Future PRs should use Jira-canonical numbers — no retro-edit of main's history.

Branch naming:
- feature/KAN-X-description
- fix/KAN-X-description
- chore/X-description

---

## Money Math & Idempotency Policy

Use this as a team policy:

Money precision, quantization, and idempotency policy:
- All monetary and fee-percentage values use Python `Decimal`, never `float`.
- Quantize before persistence:
  - USD amounts: `0.01` with `ROUND_HALF_UP`
  - percentages/spreads: `0.0001` with `ROUND_HALF_UP`
- Firestore has no native Decimal type, so authoritative money values are stored
  as normalized strings for exact round-trip and auditability.
- Retry-prone writes must be idempotent: repeated execution converges to the same
  final state (e.g., set `status="routed"` and overwrite the same routing snapshot).
- This prevents precision drift, inconsistent totals, and duplicate side effects
  under concurrency, keeping results deterministic and customer-safe.

**Known narrow exception:** `routing_total_savings_usd` is stored as a float, not a string (KAN-25). Worth a separate look at firestore.py + payment_routing.py to confirm whether this is deliberate (Firestore aggregation) or should be aligned to the policy. Not urgent — no production users.

---

## Dependency Management Policy

Use this standard for Python dependencies in `backend/`:

- `requirements.txt` = runtime dependencies only (needed in production).
- `requirements-dev.txt` = development/testing dependencies.
- `requirements-dev.txt` should include runtime deps via:
  `-r requirements.txt`

Important:
- In a `requirements*.txt` file, `-r` means "include another requirements file."
- It does **not** mean recursive filesystem search.

Classification rules:
- If imported by `backend/app/**` at runtime → put in `requirements.txt`.
- If only used for tests, linting, formatting, or local dev tooling
  (e.g., `pytest`, `ruff`, `black`, `mypy`) → put in `requirements-dev.txt`.

Recommended workflow:
1. Activate venv.
2. Install dependency.
3. Place it in the correct file (`requirements.txt` or `requirements-dev.txt`).
4. Run tests.
5. Keep production images installing only `requirements.txt`.

Install examples:
- Runtime only: `pip install -r requirements.txt`
- Dev/test env: `pip install -r requirements-dev.txt`

---

## FastAPI Handler Conventions (post-KAN-16)

- Every `/api/v1/*` handler must extract `user_id = current_user["uid"]` from `Depends(get_current_user)`.
- Use the modern Annotated pattern: `current_user: Annotated[dict[str, Any], Depends(get_current_user)]`. Satisfies Ruff B008.
- Do NOT add `dependencies=[Depends(get_current_user)]` at the router level AND as a parameter — that double-verifies the JWT (Copilot flagged this on PR #36).
- Pass `user_id` as a keyword argument to every `firestore.py` and GCS function. `user_id` is keyword-only in `firestore.py` — forgetting it is a compile-time error, not a silent leak.
- Cross-tenant access returns 404, not 403 (doesn't leak existence).

---

## GCP Project

Project ID: puente-ai-dev
Region: us-central1

---

## Environment Variables

Backend — **required** on Cloud Run. Deploy will succeed without them but `/analyze` will 500 at runtime:
- `GCP_PROJECT_ID=puente-ai-dev`
- `GCS_BUCKET_NAME=puente-documents-dev`
- `DOCUMENT_AI_PROCESSOR_ID={processor id}` — added to Cloud Run 2026-04-21 after the revision-27 `/analyze` outage caused by this variable being unset
- `ENVIRONMENT=production`

Backend — **optional** (have working defaults or are only consulted on specific code paths):
- `VERTEX_AI_LOCATION` — defaults to `"us"` in code if unset
- `EXTRA_ALLOWED_ORIGINS` — CSV of origins appended to the hardcoded CORS allow list. Each entry must match `^https?://[domain][.TLD](:port)?$` with a real TLD of 2+ chars; the regex therefore rejects `localhost` (no TLD) and wildcards, which is why `localhost:3000` / `localhost:5173` are hardcoded in `backend/app/main.py` rather than env-driven.

Frontend (Lovable):
- `VITE_API_URL` — optional, defaults to the production Cloud Run URL.

**Tech-debt worth ticketing:** the GitHub Actions deploy workflow (`backend-deploy.yml`) should assert the required env vars exist on the target Cloud Run service before promoting traffic. The 2026-04-21 revision-27 `/analyze` 500 was caused by `DOCUMENT_AI_PROCESSOR_ID` being missing on Cloud Run (the KAN-19 `/docs` work shipped in the same window but was unrelated to the outage).

---

## The User

Primary persona: "Maria"
- Miami-based importer, bilingual English/Spanish
- Buys liquidation truckloads, ships to LATAM
- Pain: wire fees (3-7%), slow settlement (5-7 days),
  customs complexity, unknown landed cost

Secondary persona: "Carlos the Exporter" (deprioritized per Perplexity reframe)
- Miami-based exporter shipping US goods to LATAM
- Imports-first corridor focus means KAN-21/22 persona details are parked, not retired

Customs broker persona (new per Perplexity reframe, 2026-04-21)
- Licensed South Florida customs broker with 20–50 importer clients
- Puente is positioned as broker-augmentation (white-label API), not broker-replacement
- Deep detail in `docs/PRD.md` and the forthcoming Strategic Priors section

Every feature passes this test:
"Does this make Maria's business stronger OR a licensed broker's workflow faster?"

---

## What NOT To Do

- Never commit .env files or credentials
- Never hardcode GCP keys in source code
- Never deploy without tests passing
- Always `pip freeze` (or equivalent) after installing packages
- Never skip venv when running Python
- Never use "Fix all with Copilot"
- Always review each Copilot suggestion individually
- Any code review finding not fixed immediately = Jira ticket
- Never push directly to main — always PR
- Never add a router-level auth Depends on top of a parameter-level one — double JWT verification (KAN-16 post-review fix)
- Never catch bare `Exception` around `response.json()` — narrow to `(ValueError, json.JSONDecodeError)` (CodeRabbit PR #36)

---

## Next Steps (this-week punch list, per ceo-scope verdict 2026-04-21)

1. **Verify the `/analyze` prod fix end-to-end.** Cloud Run revision `puente-backend-00027-4vq` was redeployed with `DOCUMENT_AI_PROCESSOR_ID` set. Upload a real invoice through the Lovable preview and confirm `/analyze` returns 200 with real extraction, not a 500. If it still fails, check IAM on the Cloud Run runtime SA (`roles/documentai.apiUser`, `roles/aiplatform.user`).
2. **KAN-37 second half (founder, 1 min).** Firebase Console → Auth → Settings → Authorized domains → add Lovable preview/published domain. Blocks Firebase popup-based sign-in until done.
3. **KAN-36 (frontend).** Replace mock data on /dashboard, /explorer, /insights, /transactions with real API queries — or add a clearly visible "Demo data" badge.
4. **File FinCEN MSB registration (founder, ~1 day).** Free online filing. Starts the Florida MTL clock. Runs in parallel to the engineering work.
5. **End-to-end smoke test with one real Miami importer contact.** This is the fundraising artifact.
6. **Author a "Strategic Priors" section in this file** capturing the 8 locked decisions from the Perplexity diligence report — founder to draft.

---

## Anti-list (per ceo-scope, do NOT do this week)

- Do NOT create KAN-38–44 yet. Ticket during pivot without working demo = graveyard.
- Do NOT engage the $10K fintech attorney until MSB is filed (free filing informs the brief).
- Do NOT close/kill KAN-17, 21, 26–31. Already PARKED with comments; deletion is irreversible and reframe is 72 hours old.
- Do NOT touch KAN-8–14, KAN-20 tech-debt. Not load-bearing for demo or MSB.
- Do NOT apply to Hustle Fund / YC / anyone else. The "real importers using product" artifact does not exist yet.

---

*Last updated: 2026-04-22 — reconciled with live Jira board (37 tickets, 15 Done, 2 In Progress, 20 To Do) following KAN-16/19 merge, KAN-33/34/35 Lovable ship, KAN-37 split status, and ceo-scope verdict on Perplexity strategic reframe. Per-ticket detail in `docs/JIRA_BOARD_SNAPSHOT.md`.*
