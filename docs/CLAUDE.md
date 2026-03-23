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
- Payment routing recommendation (KAN-5) — next
- Firestore analysis results update (KAN-6) — pending

---

## Live URLs

Production API:
https://puente-backend-519686233522.us-central1.run.app

Endpoints:
- GET  /health
- GET  /
- POST /api/v1/upload
- POST /api/v1/analyze  ← Phase 2, not yet built

---

## Tech Stack

Backend:
- Python 3.11, FastAPI, Uvicorn
- GCP Cloud Run (us-central1)
- GCP Cloud Storage (bucket: puente-documents-dev)
- GCP Firestore (database: default, collection: transactions)
- Vertex AI Gemini Flash + Document AI
- Langflow for agent orchestration (Phase 2)

Frontend (Phase 3):
- Next.js 14, TailwindCSS, Shadcn/ui
- Google Stitch for design
- Deployed on Vercel

CI/CD:
- GitHub Actions → .github/workflows/backend-deploy.yml
- Triggers on push to main when backend/** changes
- Builds Docker image → pushes to Artifact Registry → 
  deploys to Cloud Run

---

## Repository Structure
```
puente-ai/
├── .github/
│   └── workflows/
│       └── backend-deploy.yml   ← CI/CD: push to main → Cloud Run
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point, router registration
│   │   ├── routes/
│   │   │   ├── upload.py        ← POST /api/v1/upload — PDF → GCS
│   │   │   ├── analyze.py       ← POST /api/v1/analyze — KAN-3
│   │   │   └── compliance.py    ← POST /api/v1/compliance — KAN-4
│   │   └── services/
│   │       ├── firestore.py     ← Firestore operations (transactions collection)
│   │       ├── document_ai.py   ← Vertex AI Document AI extraction — KAN-2
│   │       ├── gemini.py        ← Gemini Flash analysis — KAN-3
│   │       └── compliance.py    ← Rule-based compliance engine — KAN-4
│   ├── tests/
│   │   ├── test_analyze.py      ← KAN-3 tests
│   │   ├── test_compliance.py   ← KAN-4 service tests (14 cases)
│   │   ├── test_compliance_route.py ← KAN-4 route tests (5 cases)
│   │   └── test_firestore.py    ← Firestore service tests (5 cases)
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── PRD.md                   ← Product requirements
│   ├── NOTICE.md                ← IP protection
│   └── future-vision/           ← DR strategy, investor docs
└── frontend/                    ← Phase 3: Next.js 14, TailwindCSS, Shadcn/ui
```

---

## Key Conventions

Commit messages follow Conventional Commits:
- feat: new feature
- fix: bug fix
- docs: documentation
- ci: CI/CD changes
- chore: maintenance

Commit messages reference Jira tickets:
- feat(KAN-2): integrate Vertex AI Document AI

Branch naming:
- feature/KAN-2-document-ai
- fix/KAN-7-upload-timeout

---

## GCP Project

Project ID: puente-ai-dev
Region: us-central1
Organization: No organization (personal account)

Services enabled:
- Cloud Run
- Cloud Storage
- Firestore
- Vertex AI
- Document AI
- Artifact Registry
- Cloud Build

---

## Environment Variables

Backend requires:
- GCP_PROJECT_ID=puente-ai-dev
- GCS_BUCKET_NAME=puente-documents-dev
- ENVIRONMENT=production (or development)
- VERTEX_AI_LOCATION=us-central1

Local dev uses backend/.env
Production uses Cloud Run environment variables

---

## The User

Primary persona: "Maria"
- Miami-based importer, bilingual English/Spanish
- Buys liquidation truckloads, ships to LATAM
- Uses WhatsApp for business communication
- Pain: wire fees (3-7%), slow settlement (5-7 days),
  customs complexity, unknown landed cost

Every feature passes this test:
"Does this make Maria's business stronger?"

---

## What NOT To Do

- Never commit .env files or credential JSON files
- Never hardcode GCP keys in source code
- Never deploy without tests passing
- Never add new dependencies without updating 
  requirements.txt with pip freeze
- Never skip the venv when running Python commands

---

*Last updated: March 2026*
*Next update: When Phase 2 is complete*