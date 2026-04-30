# CLAUDE.md — Puente AI Codebase Context

This file gives AI assistants (Claude, Cursor) permanent 
context about the Puente AI codebase so engineers don't 
need to re-explain the project on every session.

---

## What This Project Is

Puente AI is an AI-powered trade intelligence and payment 
infrastructure platform for the **US–LATAM trade corridor**. 
It serves Miami-based SME traders (founding persona: "Maria") 
and the licensed customs brokers who clear their shipments 
(co-equal persona: "Carlos") — in **both corridor directions**: 
LATAM→US imports of produce, manufactured goods, and raw 
materials; and US→LATAM exports of liquidation goods, 
equipment, and consumer goods.

**One-liner (locked 2026-04-29):**
*"Puente AI turns a trade document into compliance and payment 
routing in 15 seconds — for SMEs and customs brokers in the 
US–LATAM trade corridor."*

Core value proposition: upload a trade document → AI 
extracts data → fraud score + compliance check + payment 
routing recommendation in <15 seconds.

---

## Doc-State Policy (read this first)

This file holds **project invariants** — things that don't change
sprint-to-sprint: tech stack, env vars, conventions, money-math
policy, persona definitions, persistent gotchas. Anything in here
should be true regardless of which Jira ticket is in flight today.

**Volatile state lives elsewhere:**

1. **Jira board** is the source of truth for ticket status.
   `jaysworkspace-37010190.atlassian.net/KAN`. Query via Atlassian
   MCP (Cursor) when you need a current ticket state — do NOT trust
   the enumerations inside this file or `JIRA_BOARD_SNAPSHOT.md`
   without verifying against Jira.
2. **`docs/JIRA_BOARD_SNAPSHOT.md`** is a point-in-time mirror of
   the Jira board. Refreshed via Cursor's Atlassian MCP. The
   refresh is **currently a manual cadence** (founder runs it as
   needed, typically weekly); a recurring `/schedule`d routine to
   automate it is a planned follow-up — see the snapshot file's
   own header for the last "Point in time:" timestamp before
   trusting any state in it.
3. **`plans/_context/YYYY-MM-DD-resume.md`** is the most recent
   session handoff. **If a resume.md file exists with a date newer
   than this CLAUDE.md's last-updated footer, read it before doing
   anything else** — it is the most current view of in-flight work,
   open PRs, and "next literal step." On conflict: `resume.md` wins
   for status; `CLAUDE.md` wins for project invariants. The
   `plans/_context/` directory is gitignored, so the resume.md
   only exists on the machine where the prior session ran — if
   you don't see one, ask the founder for the last handoff.
4. **`plans/{feature}/plan.md`** is the in-flight implementation
   plan for a multi-commit feature. Authored by `task-decomposer`,
   updated step-by-step during execution.

**Why this policy exists:** earlier versions of this file
enumerated Done / In Progress / To Do tickets inline. That
enumeration drifted every time a ticket moved on the board, and
the drift compounded across sessions because Claude trusts this
file at session start. The fix is to keep state in one place
(Jira) and have this file point at it instead of mirroring it.

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
- Vertex Express API key auth branch in `get_gemini_client()` (KAN-42) ✅ Done (PR #38 merged 2026-04-22) — new 3-tier resolution order: `VERTEX_API_KEY` → `GEMINI_API_KEY` → ADC/SA. Currently a future-toggle: the `puente-ai-dev` project-level Vertex AI block still returns 404 for Vertex Express too, so Cloud Run runs the AI Studio branch (`GEMINI_API_KEY`) until the block clears.
- AI Studio Pay-as-you-go production unblock for `/analyze` (KAN-43) ✅ Done (ops-only, no code) — upgraded `puente-ai-dev` AI Studio plan Free → PAYG to clear the `429 RESOURCE_EXHAUSTED limit: 0`, set `GEMINI_API_KEY` + `GEMINI_MODEL` on Cloud Run, removed `VERTEX_API_KEY`. Rollback-to-Vertex-Express is zero-code once the project block clears.
- Document AI Invoice Parser v2 entity-type mapping fix (KAN-44) ✅ Done (PR #39 merged 2026-04-22; follow-ups in PR #40) — v2 emits snake_case entity types; legacy mapping was PascalCase, so every real upload landed with `extraction.fields == {}` and `/routing` 422'd on "Transaction amount is required". Fix realigns `field_mapping` keys to v2 (`total_amount` → `invoice_amount`, `supplier_name` → `exporter_name`, …), adds partial-drift detection that warns on any unknown top-level entity type, and pins the contract with `backend/tests/test_document_ai.py` (8 tests).
- CI deploy-workflow env-var safety fix (KAN-44 sibling) ✅ Done (PR #39 `backend-deploy.yml`) — switched `gcloud run deploy --set-env-vars` → `--update-env-vars` (merge semantics) so future backend deploys no longer silently wipe manually-set runtime env vars like `GEMINI_API_KEY`, `DOCUMENT_AI_PROCESSOR_ID`, or `GEMINI_MODEL`.
- `DEFAULT_GEMINI_MODEL` aligned to Cloud Run runtime ✅ Done (PR #41 merged 2026-04-22) — bumped in-code default from `gemini-2.0-flash-001` (deprecated for new callers) to `gemini-2.5-flash-lite`.

Phase 3 — Frontend hardening (Lovable-built Vite + React app, in private repo `puente-platform/puente-ai-insights`)
- Silent demo fallback removed from AnalyzePage (KAN-33) ✅ Done
- JWT `authedFetch` + `RequireAuth` route gating (KAN-34) ✅ Done
- Logout dropdown + /reset-password route + `VITE_API_URL` env var (KAN-35) ✅ Done

(In-flight Phase 3 tickets — KAN-36 mock-data replacement, KAN-37 Firebase authorized-domains second half — are tracked in Jira; their status is intentionally NOT enumerated here so this section stays a capability history rather than a drift-prone status mirror.)

Test Coverage: 113 tests passing
- test_analyze.py (6 tests)
- test_auth.py (12 tests)
- test_compliance.py (14 tests)
- test_compliance_route.py (8 tests)
- test_docs.py (3 tests) ← KAN-19
- test_document_ai.py (8 tests) ← KAN-44: v2 snake_case mapping + partial-drift detection + ignored-types silence contract
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
- POST /api/v1/onboarding  ← Firestore-backed user profile, `users/{uid}` PII; uid from token only, server-set timestamps, NFKC + length validation, null-vs-missing merge semantics
- GET  /api/v1/onboarding  ← returns 404 if not onboarded; uid from token (not an enumeration oracle)

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
- GCP Firestore (database: default; collections: `transactions` + subcollection `docs`, and `users/{uid}` for onboarding profiles — PII-bearing, owner-only via `firestore.rules`)
- Vertex AI Gemini Flash + Document AI
- Firebase Auth / GCP Identity Platform

Frontend:
- **Lives in this monorepo at `frontend-app/`** as of 2026-04-30 (migrated from Lovable's separate private repo `puente-platform/puente-ai-insights`; see "Last updated" footer).
- Vite + React + TypeScript + shadcn/ui + TailwindCSS, ~50 deps
- Firebase Auth client SDK
- React Query (`@tanstack/react-query`), React Hook Form + Zod, Recharts, framer-motion
- Built-in i18n at `frontend-app/src/lib/i18n.tsx` (EN/ES, browser `Accept-Language` detection at startup)
- Playwright e2e configured (`frontend-app/playwright.config.ts`)
- Vitest unit tests (`frontend-app/vitest.config.ts`)
- Deployed as a Cloud Run static container (nginx serving the Vite build output) at service `puente-frontend`, region `us-central1`. Multi-stage `Dockerfile` in `frontend-app/`.
- **Lovable's role going forward:** design-sandbox-only. The Lovable project (`11330f28-95e3-48bf-8f58-776e62b33067`) and its GitHub mirror (`puente-platform/puente-ai-insights`) remain available for greenfield UI exploration via prompt-driven iteration, but they are **no longer the production source of truth**. Production frontend changes happen as PRs against `frontend-app/` in this repo. If a Lovable session produces something worth keeping, port it over manually (or via agent edit on `frontend-app/`). Disconnect the Lovable GitHub integration when convenient so the bot stops pushing to the orphaned mirror — not blocking but recommended hygiene.

CI/CD:
- GitHub Actions → `.github/workflows/backend-deploy.yml` (backend → Cloud Run service `puente-backend`)
- GitHub Actions → `.github/workflows/frontend-deploy.yml` (frontend → Cloud Run service `puente-frontend`)
- Both trigger on push to main scoped by path (`backend/**` and `frontend-app/**` respectively)
- Both trigger on PRs scoped by path; PR runs do build smoke (frontend) / test smoke (backend) but do not deploy
- Both build Docker image → Artifact Registry → Cloud Run, both use `--update-env-vars` merge semantics (KAN-44 sibling fix from 2026-04-22)

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
│   │   │   ├── routing.py       ← POST /api/v1/routing (KAN-23)
│   │   │   └── onboarding.py    ← POST/GET /api/v1/onboarding; PII-safe logging, Firestore `users/{uid}`, fintech-security-audited 2026-04-30
│   │   └── services/
│   │       ├── auth.py          ← Firebase JWT verifier, `get_current_user` (KAN-15)
│   │       ├── firestore.py     ← All Firestore ops; user_id keyword-only (KAN-16)
│   │       ├── document_ai.py   ← Document AI extraction (KAN-2); v2 snake_case `field_mapping` + `_ignored_entity_types` + partial-drift warning (KAN-44)
│   │       ├── gemini.py        ← Gemini Flash analysis (KAN-3); 3-tier `get_gemini_client()` resolution: VERTEX_API_KEY → GEMINI_API_KEY → ADC/SA (KAN-42); `DEFAULT_GEMINI_MODEL="gemini-2.5-flash-lite"`
│   │       ├── compliance.py    ← Rule-based compliance (KAN-4)
│   │       └── payment_routing.py ← Routing engine (KAN-5)
│   ├── scripts/
│   │   └── migrate_firestore_tenant_scoping.py ← KAN-16 idempotent migration, --dry-run, 500-op batches
│   ├── tests/ (113 tests — includes `test_document_ai.py` for KAN-44)
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
├── frontend-app/                 ← ACTIVE frontend (Vite + React + shadcn/ui, deployed to Cloud Run service `puente-frontend`)
│   ├── Dockerfile                ← multi-stage Vite build → nginx static-serve
│   ├── nginx.conf.template       ← Cloud Run-portable (envsubst on $PORT at boot)
│   ├── package.json              ← npm; bun.lock retained for Lovable-import parity, npm is the CI default
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── components.json           ← shadcn/ui registry
│   ├── playwright.config.ts      ← e2e
│   ├── vitest.config.ts          ← unit
│   ├── index.html
│   ├── public/
│   ├── src/
│   │   ├── App.tsx               ← root, wraps I18nProvider
│   │   ├── lib/i18n.tsx          ← built-in i18n (EN/ES, browser Accept-Language detection)
│   │   ├── pages/                ← LandingPage, AnalyzePage, OnboardingPage, SettingsPage, TransactionsPage, ResetPasswordPage, NotFound
│   │   ├── components/
│   │   │   ├── ui/               ← shadcn/ui primitives
│   │   │   └── layout/           ← TopBar, AppSidebar, MobileNav, TrustFooter
│   │   ├── hooks/
│   │   ├── assets/
│   │   └── test/                 ← vitest setup
│   ├── BRAND.md                  ← brand identity / positioning truth (v0.3 aligned)
│   └── docs/DESIGN.md            ← visual / design-system spec
├── scripts/
│   └── gen_test_invoice.py       ← reportlab generator for /api/v1/analyze smoke-test PDFs
└── (Lovable mirror `puente-platform/puente-ai-insights` is NO LONGER the source of truth — kept available as a design sandbox; see Tech Stack > Frontend > Lovable's role)

---

## Jira Board — Pointer

Ticket states are NOT enumerated in this file (see Doc-State Policy
above — the enumeration drifted every sprint).

- **Source of truth:** Jira board at `jaysworkspace-37010190.atlassian.net/KAN`.
  Query via Atlassian MCP (Cursor) for the current state of any ticket.
- **Fallback:** `docs/JIRA_BOARD_SNAPSHOT.md` — point-in-time mirror,
  refreshed weekly via Cursor's Atlassian MCP. Check the "Point in time"
  header before trusting it; if older than 7 days, run a refresh.
- **In-flight work:** check the latest `plans/_context/YYYY-MM-DD-resume.md`
  if one exists, then open PRs (`gh pr list`).
- **Naming caveat:** earlier drafts of this file reserved IDs `KAN-38`
  through `KAN-44` for strategic tickets (FinCEN MSB, Florida MTL,
  customs broker POA, broker white-label API, etc.) — those IDs were
  subsequently consumed by tech-debt and incident-response work.
  Strategic tickets land at `KAN-45`+ when created.

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

Backend — **Gemini auth (exactly one path must resolve)** — consumed by `get_gemini_client()` in `backend/app/services/gemini.py` in this order:
1. `VERTEX_API_KEY` — Vertex Express API-key auth against Vertex AI endpoints. Preferred path (keeps traffic inside GCP for billing + quotas). Currently unset on Cloud Run because the `puente-ai-dev` project-level block also 404s on Vertex Express. Flip back once the block clears — zero code change.
2. `GEMINI_API_KEY` — Google AI Studio API key. **Currently serving production** (KAN-43 unblock). Paired with `GEMINI_MODEL` (set to `gemini-2.5-flash-lite`). **Rotated post-2026-04-22 incident** (founder action; the key echoed in debugging session output during the incident response was revoked). Rotate again on any future exposure. Until KAN-45 lands Secret Manager refs, follow the safer rotation pattern: do NOT paste the new key on the `gcloud` command line — use `--update-secrets ...:latest` or pipe from a temp file followed by `shred -u`. See `docs/JIRA_BOARD_SNAPSHOT.md` operational-focus list for the exact command pattern.
3. ADC / service account on the Cloud Run runtime SA — legacy fallback. Not currently used.

Backend — **optional** (have working defaults or are only consulted on specific code paths):
- `GEMINI_MODEL` — overrides `DEFAULT_GEMINI_MODEL` in `gemini.py`. Cloud Run currently sets `gemini-2.5-flash-lite`; the in-code default matches as of PR #41.
- `VERTEX_AI_LOCATION` — defaults to `"us"` in code if unset. KAN-41 tracks renaming/aligning this with `GCP_LOCATION`.
- `EXTRA_ALLOWED_ORIGINS` — CSV of origins appended to the hardcoded CORS allow list. Each entry must match `^https?://[domain][.TLD](:port)?$` with a real TLD of 2+ chars; the regex therefore rejects `localhost` (no TLD) and wildcards, which is why `localhost:3000` / `localhost:5173` are hardcoded in `backend/app/main.py` rather than env-driven.

Frontend (Lovable):
- `VITE_API_URL` — optional, defaults to the production Cloud Run URL.

**Deploy-workflow env-var safety (fixed 2026-04-22, KAN-44 sibling):** `backend-deploy.yml` now uses `gcloud run deploy --update-env-vars` (merge semantics) instead of `--set-env-vars` (replace semantics). Previously, every backend deploy silently wiped any env var not re-listed in the workflow — including the `GEMINI_API_KEY`, `DOCUMENT_AI_PROCESSOR_ID`, and `GEMINI_MODEL` variables managed out-of-band via `gcloud run services update`. **KAN-39** still tracks adding a required-env-var assertion step to the workflow — that would have caught the 2026-04-21 `/analyze` outage at promotion time rather than on the first live request.

---

## The Users (post-2026-04-29 reconciliation)

Puente AI serves two co-equal personas on every transaction. The corridor is direction-agnostic — both flows count.

Primary SME persona: "Maria"
- Miami-based cross-border SME operator, bilingual English/Spanish
- Founding-wedge profile: buys US liquidation truckloads (goTRG, B-Stock, Direct Liquidation) and ships them to resellers in Bogotá, Caracas, Lima, or Santo Domingo. In US customs terms she is technically an exporter, even though the Miami trade community self-identifies as "importers." This is the corridor the founder knows from the goTRG sales role.
- Product also serves the inverse flow — Miami SMEs bringing LATAM-origin goods (produce, manufacturing, raw materials) into the US — without changing the value proposition. Same upload, same compliance check, same payment recommendation; just a different importer of record.
- Pain: wire fees (3–7%), slow settlement (5–7 days), customs complexity, unknown landed cost

Co-equal broker persona: "Carlos"
- Licensed US customs broker / freight forwarder, based in Miami, Doral, or one of the US-Mexico land-border crossings (Laredo, El Paso, McAllen, San Diego)
- Manages 20–50 SME clients across both corridor directions
- Spends ~40% of his time on manual document review and HS code classification
- Puente is positioned as **broker-augmentation** (white-label API into his book), not broker-replacement

**The previous "Carlos the Exporter" persona has been retired** as a separate entity — Maria's founding-wedge profile already IS the US→LATAM exporter, and the corridor-direction-agnostic framing makes a separate "exporter persona" redundant. **KAN-21** (the engineering ticket for US→LATAM export compliance rules — EAR, BIS export licenses, DR-CAFTA Certificate of Origin, dual-use goods, routed export detection) was simultaneously **un-parked**: it is no longer "parked because imports are the wedge"; it builds the US→LATAM half of the now-direction-agnostic corridor. Sequencing dependency on KAN-22 still holds per the ticket description.

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

## Next Steps & Anti-list — Pointer

This file used to inline the weekly punch list and the "do NOT do
this week" anti-list. Both drifted every Monday. They now live in:

- **`docs/JIRA_BOARD_SNAPSHOT.md` → "Operational focus for next session"** —
  prioritized punch list, refreshed alongside the Jira snapshot.
- **`plans/_context/YYYY-MM-DD-resume.md` → "NEXT LITERAL STEPS"** —
  immediate next-action handoff between sessions.

If you need a strategic verdict on what to do this week (vs. what
not to), invoke the `ceo-scope` agent — it reads the PRD + current
sprint state and returns a four-mode scope verdict. Verdicts are
not committed to this file; they go in the session log.

---

*Last updated: 2026-04-30 (later) — frontend repo migration. Pulled the Lovable-built frontend out of its separate private mirror (`puente-platform/puente-ai-insights@f2db10b`) and into this monorepo at `frontend-app/`. Deleted the legacy `frontend/` Vite scaffold (was just two `.gitkeep` files, never deployed). Added `frontend-app/Dockerfile` (multi-stage Vite → nginx) + `frontend-app/nginx.conf.template` (Cloud Run-portable, envsubst on `$PORT`) + `.github/workflows/frontend-deploy.yml` (mirrors `backend-deploy.yml` conventions, deploys to Cloud Run service `puente-frontend` in `us-central1`, uses `--update-env-vars` merge semantics). Tech Stack and Repository Structure sections updated to reflect the new layout. Lovable's role going forward: design-sandbox-only, no longer the production source of truth — see Tech Stack > Frontend > Lovable's role. The `gcp/welcome-email/` Cloud Function scaffold from Lovable was dropped during the snapshot (per the 2026-04-30 four-agent architectural verdict, future email integration goes on the existing FastAPI Cloud Run as `POST /api/v1/notifications/email`, not a separate Cloud Function). Companion follow-ups, all separate tickets: (i) backend CORS update to allow the new `puente-frontend-XXX-uc.a.run.app` origin once the first Cloud Run deploy completes, (ii) custom domain wiring (Namecheap-purchased domain not yet pointed at anything), (iii) updating the `frontend-engineer` agent prompt to reflect the new in-monorepo file scope, (iv) optional disconnect of the Lovable GitHub integration so the bot stops pushing to the orphaned mirror. No backend code changes in this PR; backend tests unaffected.*

*Previous: 2026-04-30 — doc-drift prevention pass. Added the **Doc-State Policy** section at the top of this file, replaced the inline `Jira Board — Summary` enumeration (lines that drifted every sprint as tickets moved on the board) with a thin pointer at `docs/JIRA_BOARD_SNAPSHOT.md` + Jira, replaced the inline `Next Steps` and `Anti-list` punch lists with pointers at the snapshot's operational-focus section + `plans/_context/YYYY-MM-DD-resume.md`. Added the resume-pointer convention (next session reads the latest resume.md if present). Reflected the post-2026-04-22 GEMINI_API_KEY rotation as completed in the Environment Variables section. Companion changes: `docs/JIRA_BOARD_SNAPSHOT.md` operational-focus list updated to remove the now-completed rotation item and add KAN-46 (`/routing` 422 root-cause logging, shipped via PR #46 commit 503ae35, fixes the regression surfaced by the KAN-43 close-out smoke test). No code changes; tests unaffected.*

*Previous: 2026-04-29 — strategic positioning reconciliation. Locked the company one-liner and rewrote PRD §1, §2, §3, §4, §5, §11, §13 (now v0.3) to be corridor-direction-agnostic: Puente serves both LATAM→US imports and US→LATAM exports, with Maria as the founding-wedge SME persona and Carlos elevated from secondary to co-equal broker persona. Retired the separate "Carlos the Exporter" persona (Maria's founding profile already covers it). KAN-21 un-parked and returned to active To Do (it builds the US→LATAM compliance-rules half of the corridor; comment posted to Jira with the un-parking rationale). Pitch deck and investor teaser updated to lead with the new one-liner and explicit broker-augmentation distribution wedge.*

*Previous update: 2026-04-22 (late) — reconciled with live Jira board (44 tickets, 18 Done, 2 In Progress, 24 To Do) after the 2026-04-22 Gemini/Document AI incident response: KAN-42 (Vertex Express, PR #38), KAN-43 (AI Studio PAYG unblock, ops-only), KAN-44 (Document AI v2 snake_case mapping + partial-drift detection, PR #39 + PR #40), PR #41 (`DEFAULT_GEMINI_MODEL` aligned to `gemini-2.5-flash-lite`), and the sibling CI-safety fix switching `backend-deploy.yml` from `--set-env-vars` → `--update-env-vars`. Test suite: 113 passing (added `test_document_ai.py`). Per-ticket detail in `docs/JIRA_BOARD_SNAPSHOT.md`.*
