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

Phase 2 — In Progress (current sprint)
- Vertex AI Document AI invoice extraction (KAN-2) ✅ Done
- Gemini Flash analysis endpoint (KAN-3) ✅ Done
- Compliance gap detection (KAN-4) ✅ Done
- Payment routing engine service (KAN-5) ✅ Done
- POST /api/v1/routing endpoint (KAN-23) ✅ Done (PR #21 merged 2026-03-24)
- Firestore analysis results update (KAN-6) ✅ Done (PR #30 merged 2026-04-20)

Test Coverage: 81 tests passing
- test_analyze.py (6 tests)
- test_auth.py (9 tests)
- test_compliance.py (14 tests)
- test_compliance_route.py (7 tests)
- test_firestore.py (11 tests)
- test_gemini.py (4 tests)
- test_payment_routing.py (20 tests)
- test_pipeline_integration.py (2 tests)
- test_routing_route.py (8 tests)

---

## Live URLs

Production API:
https://puente-backend-519686233522.us-central1.run.app

Endpoints (live):
- GET  /health
- GET  /
- POST /api/v1/upload
- POST /api/v1/analyze
- POST /api/v1/compliance
- POST /api/v1/routing  ← KAN-23 (PR #21 merged 2026-03-24)

---

## Tech Stack

Backend:
- Python 3.11, FastAPI, Uvicorn
- GCP Cloud Run (us-central1)
- GCP Cloud Storage (bucket: puente-documents-dev)
- GCP Firestore (database: default, collection: transactions)
- Vertex AI Gemini Flash + Document AI

Frontend (Phase 3 — not started):
- Next.js 14, TailwindCSS, Shadcn/ui
- Google Stitch for design
- Deployed on Vercel

CI/CD:
- GitHub Actions → .github/workflows/backend-deploy.yml
- Triggers on push to main when backend/** changes
- Triggers on all PRs (docs-only PRs skip build, pass CI)
- Builds Docker image → Artifact Registry → Cloud Run

---

## Repository Structure

puente-ai/
├── .github/workflows/backend-deploy.yml
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry, router registration
│   │   ├── routes/
│   │   │   ├── upload.py        ← POST /api/v1/upload
│   │   │   ├── analyze.py       ← POST /api/v1/analyze (KAN-3)
│   │   │   ├── compliance.py    ← POST /api/v1/compliance (KAN-4)
│   │   │   └── routing.py       ← POST /api/v1/routing (KAN-23)
│   │   └── services/
│   │       ├── firestore.py     ← All Firestore operations
│   │       ├── document_ai.py   ← Document AI extraction (KAN-2)
│   │       ├── gemini.py        ← Gemini Flash analysis (KAN-3)
│   │       ├── compliance.py    ← Rule-based compliance (KAN-4)
│   │       └── payment_routing.py ← Routing engine (KAN-5)
│   ├── tests/
│   │   ├── test_analyze.py
│   │   ├── test_auth.py
│   │   ├── test_compliance.py
│   │   ├── test_compliance_route.py
│   │   ├── test_firestore.py
│   │   ├── test_gemini.py
│   │   ├── test_payment_routing.py
│   │   ├── test_pipeline_integration.py
│   │   └── test_routing_route.py
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── PRD.md
│   ├── CLAUDE.md  ← this file
│   └── NOTICE.md
└── frontend/  ← Phase 3, not started

---

## Jira Board — Full Ticket List

TO DO (14 tickets):
- KAN-1:  Phase 2 Invoice Intelligence Pipeline (epic — all child stories shipped; epic still open in Jira)
- KAN-8:  Add asyncio.to_thread() to analyze endpoint (tech-debt)
- KAN-9:  Fix analyze.py imports, ValueError handling (tech-debt)
- KAN-10: Fix firestore.py error field on success (tech-debt)
- KAN-11: upload.py GCS/Firestore atomic writes (tech-debt)
- KAN-12: upload.py sanitize error messages (tech-debt)
- KAN-13: document_ai.py highest-confidence field selection (tech-debt)
- KAN-14: Rename VERTEX_AI_LOCATION to GCP_LOCATION (tech-debt)
- KAN-17: HS code classification
- KAN-18: Landed cost estimation
- KAN-19: API documentation — enable FastAPI /docs
- KAN-20: payment_routing.py raise ValueError on invalid country codes (tech-debt)
- KAN-21: Export corridor compliance rules US → LATAM
- KAN-22: Customer research — interview one Miami exporter

IN PROGRESS (1):
- KAN-16: Multi-tenant data isolation (BLOCKER — remaining pre-pilot blocker; no implementation code yet)

DONE (10) — chronological:
- KAN-2:  Vertex AI Document AI extraction (resolved 2026-03-21)
- KAN-3:  Gemini Flash analysis endpoint (resolved 2026-03-22)
- KAN-4:  Compliance gap detection (resolved 2026-03-23)
- KAN-5:  Payment routing engine service (resolved 2026-03-23)
- KAN-23: POST /api/v1/routing endpoint (resolved 2026-03-24, PR #21)
- KAN-24: save_routing_result update status to "routed" (resolved 2026-03-26)
- KAN-25: routing_total_savings_usd normalized Decimal string (resolved 2026-03-26)
- KAN-15: JWT via Firebase Auth / GCP Identity Platform (resolved 2026-03-27)
- KAN-6:  Update Firestore with analysis results (resolved 2026-04-20, PR #30)
- KAN-7:  Refactor Firestore client to singleton + async/sync fix (resolved 2026-04-20, PR #30)

---

## Key Conventions

Commit messages (Conventional Commits):
- feat(KAN-X): new feature
- fix(KAN-X): bug fix
- docs: documentation only
- ci: CI/CD changes
- chore: maintenance

Branch naming:
- feature/KAN-23-routing-endpoint
- fix/KAN-X-description
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

## GCP Project

Project ID: puente-ai-dev
Region: us-central1

---

## Environment Variables

Backend requires:
- GCP_PROJECT_ID=puente-ai-dev
- GCS_BUCKET_NAME=puente-documents-dev
- DOCUMENT_AI_PROCESSOR_ID=<processor id>
- ENVIRONMENT=production
- VERTEX_AI_LOCATION=us-central1

---

## The User

Primary persona: "Maria"
- Miami-based importer, bilingual English/Spanish
- Buys liquidation truckloads, ships to LATAM
- Pain: wire fees (3-7%), slow settlement (5-7 days),
  customs complexity, unknown landed cost

Secondary persona: "Carlos the Exporter"
- Miami-based exporter shipping US goods to LATAM
- Larger transaction sizes, heavier compliance burden
- KAN-21/KAN-22 address this corridor

Every feature passes this test:
"Does this make Maria's business stronger?"

---

## What NOT To Do

- Never commit .env files or credentials
- Never hardcode GCP keys in source code
- Never deploy without tests passing
- Always pip freeze after installing packages
- Never skip venv when running Python
- Never use "Fix all with Copilot"
- Always review each Copilot suggestion individually
- Any code review finding not fixed immediately = Jira ticket
- Never push directly to main — always PR

---

## Next Steps (when starting new session)

1. Smoke-test the deployed Cloud Run pipeline end-to-end with a real invoice (upload → analyze → compliance → routing → stored result)
2. Run task-decomposer on KAN-16 — multi-tenant data isolation; the remaining pre-pilot blocker now that KAN-15 (Firebase Auth) has shipped
3. Bundle KAN-19 (enable FastAPI /docs) into the same sprint — small, but needed for frontend + pilot self-service
4. Miro architecture diagram — board exists at
   https://miro.com/app/board/uXjVGtw4xQQ=/

---

*Last updated: 2026-04-21 — reconciled with Jira source of truth: KAN-15 (Firebase Auth) shipped 2026-03-27 (previously still listed as TO DO — drift corrected), KAN-24/25 closed 2026-03-26, KAN-6/7 closed 2026-04-20 (PR #30). Next blocker: KAN-16 multi-tenant isolation.*