# Jira Board Snapshot — Puente AI

**Source:** Cursor IDE Claude instance with direct Jira connection, briefing received 2026-04-21.
**Point in time:** 2026-04-21. For current state, always query Jira directly.
**Purpose:** Give future AI sessions a fast, high-resolution view of ticket inventory + suggested sequencing without re-scraping Jira.

---

## Context

- **Project:** Puente AI — AI-driven invoice intelligence + payment routing platform (GCP stack: Document AI, Gemini Flash, Firestore, Firebase Auth, FastAPI).
- **Jira site:** `jaysworkspace-37010190.atlassian.net`
- **Project key:** `KAN`
- **Owner:** jayalexander1127 (sole assignee on all 31 tickets, all Medium priority).

## Ticket counts (2026-04-21)

- **Total:** 31 (KAN-1 through KAN-31)
- **Done:** 10 (32%)
- **In Progress:** 1 (3%)
- **To Do:** 20 (65%)
- **Types:** 5 Stories, 12 Tasks, 14 Features

---

## Done (10) — shipped

Core invoice pipeline is live end-to-end: PDF → extraction → analysis → compliance → routing → persistence → auth.

| Key | Type | Summary | Resolved |
|---|---|---|---|
| KAN-2 | Story | Vertex AI Document AI invoice field extraction | 2026-03-21 |
| KAN-3 | Story | Gemini Flash analysis endpoint (fraud score + summary) | 2026-03-22 |
| KAN-4 | Story | Compliance gap detection (LOW/MEDIUM/HIGH + missing docs) | 2026-03-23 |
| KAN-5 | Story | Payment routing recommendation (USDC vs wire savings) | 2026-03-23 |
| KAN-23 | Feature | `POST /api/v1/routing` endpoint wired to routing engine | 2026-03-24 |
| KAN-24 | Task | `save_routing_result` updates top-level status to `"routed"` | 2026-03-26 |
| KAN-25 | Task | `save_routing_result`: store `routing_total_savings_usd` as float, not string | 2026-03-26 |
| KAN-15 | Feature | JWT auth via Firebase Auth / GCP Identity Platform | 2026-03-27 |
| KAN-6 | Story | Update Firestore with analysis results | 2026-04-20 |
| KAN-7 | Task | Firestore client singleton + async/sync fix | 2026-04-20 |

Latest two (KAN-6, KAN-7) close out the Firestore persistence + architectural cleanup tracked in `docs/superpowers/plans/2026-04-20-kan-6-firestore-pipeline-persistence.md`.

---

## In Progress (1)

- **KAN-16** (Feature) — Multi-tenant data isolation. Scope all Firestore queries to `user_id`. Prerequisite for multi-user production. Remaining pre-pilot blocker now that KAN-15 (auth) has shipped.

---

## To Do (20) — grouped by theme

### Epic / stale (1)
- **KAN-1** — Phase 2 Invoice Intelligence Pipeline epic. All child stories are Done; ticket likely just needs status close.

### Backend hardening / tech debt (8) — "fix before real users"
- **KAN-8** — `asyncio.to_thread()` for Document AI calls
- **KAN-9** — `analyze.py` cleanup + stuck-`processing` ValueError
- **KAN-10** — `firestore.py` clear error on success, add `updated_at`, document `merge=True`
- **KAN-11** — `upload.py` GCS+Firestore atomicity (cleanup on Firestore failure)
- **KAN-12** — `upload.py` sanitize client-facing error messages
- **KAN-13** — `document_ai.py` last-wins → highest-confidence field selection
- **KAN-14** — Rename `VERTEX_AI_LOCATION` → `GCP_LOCATION`
- **KAN-20** — `payment_routing.py` raise `ValueError` on invalid country codes (no silent `"US"` default)

### Cost & classification (3)
- **KAN-17** — HS code classification via Gemini
- **KAN-18** — Landed cost estimation (duties + port fees + settlement)
- **KAN-19** — Enable FastAPI `/docs` and deploy

### Export corridor & research (2)
- **KAN-21** — US → LATAM export corridor compliance rules (gated by KAN-22)
- **KAN-22** — Customer interview with one Miami exporter (gates KAN-21 and Phase 3)

### Phase 3 — niche positioning for importers/exporters, ES/PT surfaces (6)
- **KAN-26** — Phase 3 niche + compliance checklist (parent)
- **KAN-27** — AI-assisted OFAC/SDN screening engine
- **KAN-28** — HTS code detection + confidence scoring
- **KAN-29** — Antidumping/CVD rule checks by corridor + product
- **KAN-30** — Plain-language compliance summaries for operators
- **KAN-31** — Risk/compliance UX integration in landing + app

---

## Suggested sequencing (from briefing)

1. Finish **KAN-16** (multi-tenant isolation) — blocker for real users.
2. Sweep the 8 hardening tasks (**KAN-8–14, KAN-20**) — small, in-code, same files.
3. Do **KAN-22** customer interview before any Phase 3 feature work.
4. Close **KAN-1** (Phase 2 epic) as Done.
5. Phase 3 compliance work (**KAN-26–31**) after interview signal.
6. **KAN-17 / KAN-18 / KAN-19** (cost + docs) can slot in opportunistically.

---

## Repo pointers

- Workspace: `/Users/jay/Projects/puente-ai`
- Project guide: `docs/CLAUDE.md`
- Most recent plan: `docs/superpowers/plans/2026-04-20-kan-6-firestore-pipeline-persistence.md`
- Live API: `https://puente-backend-519686233522.us-central1.run.app`

---

*Snapshot maintained via Cursor agent briefings. When ticket state diverges from this file, Jira is the source of truth — update this file and `docs/CLAUDE.md` together.*
