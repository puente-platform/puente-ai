# Jira Board Snapshot — Puente AI

**Source:** Jira MCP (`searchJiraIssuesUsingJql` + per-ticket `getJiraIssue`) + direct Jira updates applied in-session.
**Point in time:** 2026-04-29 (evening — post-PRD-v0.3 strategic positioning reconciliation).
**Purpose:** Fast, high-resolution board snapshot for future sessions without re-scraping Jira.

---

## Context

- **Project:** Puente AI — AI-native invoice intelligence + compliance + payment routing for the US–LATAM trade corridor.
- **Jira site:** [jaysworkspace-37010190.atlassian.net](https://jaysworkspace-37010190.atlassian.net)
- **Project key:** `KAN`
- **Cloud ID:** `a077f57a-6ec3-4caf-adae-22ce16a35c1c`

## Ticket counts (2026-04-29, live from Jira)

- **Total:** 45 (`KAN-1` through `KAN-45`)
- **Done:** 17
- **In Progress:** 2 (`KAN-32`, `KAN-37`)
- **In Review:** 1 (`KAN-43`)
- **To Do:** 25
- **Unassigned:** 7 (`KAN-20`, `KAN-28`, `KAN-29`, `KAN-30`, `KAN-31`, `KAN-44`, `KAN-45`)

**Changes since previous snapshot (2026-04-22 late):**

- **+1 new ticket:** `KAN-45` — Move runtime secrets to Secret Manager refs on Cloud Run (Medium, To Do, labels: `infra`, `secrets`, `security`, `tech-debt`). Created 2026-04-22 as the hardening follow-up to the KAN-43 AI Studio key rotation; the previous key value printed in plain `gcloud describe` output and the lesson was "rotation should never expose the key in shell history."
- **KAN-43 status correction:** previous snapshot listed it as Done; live Jira state is and was **In Review**. The AI Studio Pay-as-you-go unblock is operational and serving prod, but the ticket itself is not formally closed. Action: verify the production fix and transition In Review → Done.
- **KAN-21 strategic reframe (this session, 2026-04-29):** un-parking comment posted (comment id 10081) documenting that the previous "imports are the wedge" parking rationale is invalidated by the PRD v0.3 corridor-direction-agnostic reframe. Status field still in To Do (PARKED bucket); manual move from PARKED → active backlog still needed on the board.

---

## ⚠️ Deltas since this snapshot was written (2026-04-30, manual patch)

This snapshot is a 2026-04-29 evening point-in-time capture. The
following Jira state changes happened **after** the snapshot was
written and are documented here so anyone reading this file in
the brief window before the next weekly Cursor-MCP refresh has
the current picture. Always cross-check against live Jira.

- **`KAN-43` In Review → Done** (2026-04-30 02:31 UTC) — KAN-43 close-out smoke test confirmed `/analyze` 200 in 6.97s with zero ERROR-severity entries in 7d; audit-trail comment id `10082` posted before the transition. Revision serving prod: `puente-backend-00037-6t7`.
- **`KAN-44` To Do → Done** — Document AI snake_case mapping fix landed and re-verified by the same 2026-04-30 02:31 UTC smoke test. The mapping fix shipped in PR #39 + PR #40 on 2026-04-22; the Jira board state lagged the merge.
- **`KAN-46` filed** (2026-04-30 02:36 UTC, To Do, High priority, unassigned, `infra`/`backend`/`tech-debt` labels) — *"Routing /api/v1/routing returns 422 post-KAN-44; Document AI v2 emits 2 new untyped entities (`remit_to_name`, `supplier_iban`)."* Surfaced by the same KAN-43 close-out smoke test. **First-fix-step** (the one-line debuggability commit on `backend/app/routes/routing.py:114-117`) shipped via PR #46 (commit `503ae35`, merged 2026-04-30 03:12 UTC). Full audit scope (route-required-field classification + the two new untyped entities) still open.
- **`KAN-22` To Do → In Progress** (2026-04-30) — founder began the Miami importer / customs broker interview track. The KAN-21 un-block signal (≥2 interviews with US→LATAM exporters/brokers AND ≥1 unprompted DR-CAFTA / BIS export-license mention) is now actively being chased.
- **AI Studio `GEMINI_API_KEY` rotated** (founder, 2026-04-30) — the key that was echoed in 2026-04-22 debugging session output has been rotated and the old key revoked. Production `/analyze` continued working through the rotation. KAN-45 (Secret Manager refs) remains the structural follow-up so future rotations don't depend on remembering the safer-rotation-pattern command.

**Updated counts (delta-applied):** Done **19** (KAN-43, KAN-44 added), In Progress **3** (KAN-22 added), To Do **23** (KAN-43, KAN-44 removed; KAN-46 added). Net total: 46 tickets (`KAN-1`–`KAN-46`). **For canonical state, query Jira via Atlassian MCP — these deltas are best-effort patches against a known-stale point-in-time snapshot, and the per-section headers below still carry the original 2026-04-29 counts (e.g., `## Done (17)`) for traceability rather than being rewritten in place.**

---

## Done (17) — shipped

| Key | Type | Summary | Resolved |
|---|---|---|---|
| KAN-2 | Story | Enable Vertex AI Document AI to extract invoice fields | 2026-03-21 |
| KAN-3 | Story | Build Gemini Flash analysis endpoint | 2026-03-22 |
| KAN-4 | Story | Add compliance gap detection | 2026-03-23 |
| KAN-5 | Story | Build payment routing recommendation | 2026-03-23 |
| KAN-6 | Story | Update Firestore with analysis results | 2026-04-20 |
| KAN-7 | Task | Refactor Firestore client singleton + async/sync fix | 2026-04-20 |
| KAN-15 | Feature | Authentication via Firebase JWT / GCP Identity Platform | 2026-03-27 |
| KAN-16 | Feature | Multi-tenant data isolation — scope all Firestore queries to user_id | 2026-04-22 (PR #36, Miami business day 2026-04-21) |
| KAN-19 | Feature | API documentation — enable FastAPI `/docs` and `/redoc` | 2026-04-22 (PR #36 bundled) |
| KAN-23 | Feature | Build `POST /api/v1/routing` endpoint | 2026-03-24 |
| KAN-24 | Task | `save_routing_result`: top-level `status="routed"` after persistence | 2026-03-26 |
| KAN-25 | Task | `save_routing_result`: store `routing_total_savings_usd` as float | 2026-03-26 |
| KAN-33 | Task | Remove silent demo fallback in `AnalyzePage` | 2026-04-22 |
| KAN-34 | Task | Wire JWT through `authedFetch` + gate routes with `RequireAuth` | 2026-04-22 |
| KAN-35 | Task | Logout button + `/reset-password` route + `VITE_API_URL` env var | 2026-04-22 |
| KAN-42 | Task | Vertex Express API key auth branch in `get_gemini_client()` (PR #38) | 2026-04-22 |
| KAN-44 | Task | Document AI Invoice Parser v2 entity-type mapping fix + partial-drift detection (PR #39 + PR #40) | 2026-04-22 |

Notes:

- **KAN-16** completion comment ties to PR #36 (`f160bb7`) and 105 tests at the time of merge.
- **KAN-19** completion comment ties to PR #36 (`f9a6b4a`) and `test_docs.py`.
- **KAN-42** lands as a future-toggle: the `puente-ai-dev` project-level Vertex block still 404s even against Vertex Express, so Cloud Run runs the AI Studio branch via `GEMINI_API_KEY`. Branch/commit history uses an obsolete "KAN-52" identifier from a pre-numbering-lock draft — no git rewrite planned.
- **KAN-44** ships the Invoice Parser v2 snake_case fix (PR #39: `0f2da66`, `c553cd9`) plus CodeRabbit/Copilot follow-ups (PR #40: `83b6a7e`, `c0410cc`). CI workflow also switched `--set-env-vars` → `--update-env-vars` to stop future deploys wiping manually-set runtime env vars. Test suite: 113 passing (added `backend/tests/test_document_ai.py` with 8 tests pinning the v2 contract and drift-detection semantics).

---

## In Progress (2)

- **KAN-32** (Feature, High, labels: `auth`, `frontend`, `pilot-blocker`) — Frontend auth wire-up + kill silent demo fallback rollup parent. Stays open until KAN-36 + KAN-37 close.
- **KAN-37** (Task, Highest, labels: `backend`, `cors`, `demo-blocker`, `pilot-blocker`) — CORS whitelist `*.lovableproject.com` + Firebase Authorized Domains.
  - Backend CORS portion shipped (PR #35, commit `5edce5c`).
  - **Remaining manual step (founder, ~1 min):** Firebase Console → Auth → Settings → Authorized Domains → add the Lovable preview/published domain. Blocks Firebase popup-based sign-in until done.

## In Review (1)

- **KAN-43** (Task, Highest, labels: `ai-studio`, `operational`, `production-incident`, `unblock`, `vertex-ai`) — AI Studio Pay-as-you-go unblock for `/analyze`. Operationally complete and serving production traffic since 2026-04-22; needs a formal Done transition. Suggested verification before close: confirm `/analyze` returns 200 from Lovable preview against a real invoice and Cloud Run logs are clean of `RESOURCE_EXHAUSTED` and `processor-version drift` warnings.

---

## To Do (25) — grouped by theme

### Epic / lifecycle

- **KAN-1** — Phase 2 Invoice Intelligence Pipeline epic. All child stories shipped; only the parent epic itself remains open. Close on next Jira pass.

### Backend hardening / tech debt (Medium priority unless noted)

- **KAN-8** — Add `asyncio.to_thread()` in analyze path for non-blocking Document AI calls. `[tech-debt]`
- **KAN-9** — `analyze.py` cleanup: imports, ValueError-leaves-status-stuck-on-processing, remove `/analyze/force` mention. `[tech-debt]`
- **KAN-10** — `firestore.py`: clear `error` field on success, add `updated_at` to `save_extraction`, document `merge=True` tradeoff. `[tech-debt]`
- **KAN-11** — `upload.py`: GCS + Firestore writes are not atomic — add cleanup on Firestore failure. `[tech-debt]`
- **KAN-12** — `upload.py`: sanitize client-facing error messages before production. `[tech-debt]`
- **KAN-13** — `document_ai.py`: field extraction uses last-wins — change to highest-confidence selection. `[tech-debt]`
- **KAN-14** — Rename `VERTEX_AI_LOCATION` to `GCP_LOCATION` for clarity. (Coordinate with KAN-41.)
- **KAN-20** — `payment_routing.py`: raise `ValueError` on invalid/missing country codes instead of silently defaulting to `"US"`. `<unassigned>`
- **KAN-38** — Fix default Gemini location in `backend/app/services/gemini.py` (`global` fallback → `us-central1`) + add unit test. `[tech-debt]`
- **KAN-39** — Assert required Cloud Run env vars in `backend-deploy.yml` and fail workflow if any required var is missing. `[tech-debt]`
- **KAN-40** — Document required runtime SA IAM roles + exact `gcloud` binding commands. `[tech-debt]`
- **KAN-41** — Align `VERTEX_AI_LOCATION` / `GCP_LOCATION` naming semantics. (Coordinate with KAN-14.) `[tech-debt]`
- **KAN-45** — **NEW (2026-04-22):** Move runtime secrets to Secret Manager refs on Cloud Run. Pulls `GEMINI_API_KEY` + `DOCUMENT_AI_PROCESSOR_ID` (+ reserved `VERTEX_API_KEY`) out of plain Cloud Run env vars and into `secretKeyRef` so `gcloud run services describe` no longer emits raw values. Sibling to KAN-39 (KAN-39 prevents deploy with missing required vars; KAN-45 prevents those vars from being human-readable post-deploy). Includes a rotation runbook for `docs/CLAUDE.md`. `[infra, secrets, security, tech-debt]` `<unassigned>`

### Discovery / strategy-coupled (Medium)

- **KAN-17** — HS code classification — Gemini prompt per product description. **Status: PARKED** (per 2026-04-21 strategic reframe — KlearNow.AI is at 95%; integrate rather than build).
- **KAN-18** — Landed cost estimation — duties + port fees + settlement cost. **Reframe candidate:** "real-time Trump tariff volatility calculator" (per Perplexity diligence).
- **KAN-21** — Add export corridor compliance rules for US → LATAM shipments (EAR / BIS export-license / DR-CAFTA Certificate of Origin / dual-use goods / routed-export-transaction flags into `services/compliance.py`). **Status: UN-PARKED 2026-04-29** per PRD v0.3 reframe — see comment id 10081. Concrete engineering scope; sequencing dependency on KAN-22 customer interviews still holds. **Manual board move from PARKED bucket → active To Do still needed.**
- **KAN-22** — Customer research — interview Miami SMEs and customs brokers (target: 10, not 1, per Perplexity diligence). Strategic priority for the demo loop.

### Phase 3 surfaces and compliance UX (Medium, all PARKED 2026-04-21 pending strategic reframe)

- **KAN-26** — Phase 3 parent: Niche positioning (legacy framing) + compliance checklist. **Reframe candidate:** Miami Latino trader community / goTRG network.
- **KAN-27** — AI-assisted OFAC/SDN screening engine.
- **KAN-28** — HTS code detection and confidence scoring. `<unassigned>`
- **KAN-29** — Antidumping/CVD rule checks by corridor + product. `<unassigned>`
- **KAN-30** — Plain-language compliance summaries for operators. `<unassigned>`
- **KAN-31** — Risk/compliance UX integration in landing + app. `<unassigned>`

### Frontend (active)

- **KAN-36** — Label or wire remaining demo surfaces (`/dashboard`, `/explorer`, `/insights`, `/transactions`) — replace mock data with real API queries OR ship a visible "Demo data" badge. `[demo-data, frontend, pilot-polish]`

---

## Strategic hygiene applied 2026-04-29 (this session)

1. **PRD v0.3 strategic positioning reconciliation** — locked the company one-liner and rewrote PRD §1 / §2 / §3 / §4 / §5 / §11 / §13 to be corridor-direction-agnostic. Maria reframed honestly as Miami-based cross-border SME (founding-wedge profile is the goTRG-style US→LATAM exporter); Carlos elevated from secondary to co-equal broker persona; "Carlos the Exporter" persona retired (Maria's founding profile already covers it). **PR #43 merged 2026-04-30T00:10:00Z** (≈2026-04-29 8:10 PM Miami) via squash; branch was `docs/2026-04-29-positioning-reconcile` with main commit `015aa9a` plus reviewer-feedback follow-ups `33e0283` (Copilot + CodeRabbit) and `18976ef` (US–LATAM hyphen → en-dash normalization).
2. **KAN-21 un-parking comment posted** (comment id 10081). Reframed from PARKED-because-imports-are-the-wedge to active-engineering-ticket. Manual board move still pending.
3. **One stray "Miami importers" reference** in `docs/future-vision/vc-email-sequence.md` updated to "Miami SMEs and brokers (both directions)".
4. **Pitch deck + investor teaser** (`docs/future-vision/pitch-deck-outline.md`, `investor-teaser.md`) updated to lead with the new locked one-liner and add the broker-augmentation distribution wedge.
5. **New agents added to `.claude/agents/`** — branch `feature/marketing-pr-agent` pushed and **PR #44 OPEN** (*"feat(agents): expand subagent suite + plans/ directory"*). Beyond the original two agents this session authored, the branch now bundles 3 additional commits (gitignore + 5 more specialized subagents + plans/ scaffolding) authored after my session handed it off:
   - **`marketing-pr`** (commit `e771929`, this session) — Senior Marketing & PR Lead with Ogilvy / Brunswick / Edelman pedigree. Output capabilities: website copy, press releases, social, email that converts. 7 fintech compliance guardrails baked in. Includes first asset `docs/marketing/2026-04-29-linkedin-broker-augmentation.md` (bilingual EN/ES founder-voice LinkedIn post on the broker-augmentation positioning, working draft awaiting founder review).
   - **`mentor`** (commit `cbacd95`, this session) — Personal technical tutor adapted from a personal AgentForge solo-dev mentor template with Jay's developer profile, Puente-flavored analogies, the fintech-engineering and bilingual-reasoning habits, and the Maria & Carlos test. Read-only.
   - Plus 5 additional subagents + plans/ directory scaffolding added by a parallel session (commit `ede6668`) and a gitignore tidy (`ce247eb`).

---

## Operational focus for next session

> Updated 2026-04-30 alongside the doc-drift-prevention pass. Items
> the founder finished on 2026-04-30 are crossed out for traceability.

**Hot path (right now):**

1. **KAN-46 follow-up — re-fire the Lovable preview smoke test against a real invoice.** PR #46 (commit `503ae35`) added the `logger.warning` on `routing.py:114-117`; the next prod reproduction now leaves the actual failing-field name in Cloud Run logs. Pull it via `gcloud logging read --project puente-ai-dev "resource.type=cloud_run_revision AND severity>=WARNING AND textPayload:\"Routing recommendation failed\"" --limit 20 --freshness 1d --format=json`.
2. **KAN-46 audit scope** (after step 1 lands the failing-field name) — route-required-field classification + the two new untyped Document AI v2 entities (`remit_to_name`, `supplier_iban`) that need to be added to `backend/app/services/document_ai.py` field_mapping. Either fold the mapping addition into the same KAN-46 fix branch or spin a new ticket; the resume.md noted that splitting "the 422 itself" from "the two untyped entities" would create false separation, so prefer one ticket.
3. **Move KAN-21 status from PARKED bucket → active To Do** on the Jira board UI. Comment id 10081 explains the un-parking rationale; the board status field still needs the manual click. Engineering work remains gated on KAN-22 interview signal.
4. **KAN-37 manual step (founder, ~1 min).** Firebase Console → Auth → Settings → Authorized Domains → add Lovable preview/published domain. Then close KAN-37 and likely KAN-32 rollup.

**Founder track (this week, owned by founder, parallel to engineering):**

5. **KAN-22 customer interviews** — currently In Progress. Target ≥10 Miami SMEs and customs brokers (Perplexity diligence target). KAN-21 un-block signal: ≥2 interviews with US→LATAM exporters/brokers AND ≥1 unprompted DR-CAFTA Cert-of-Origin or BIS export-license mention. Use the marketing-pr agent's first asset (`docs/marketing/2026-04-29-linkedin-broker-augmentation.md`) as outreach copy when the founder approves it for publication.
6. **File FinCEN MSB registration (~1 day, free).** Starts the Florida MTL clock; runs in parallel to engineering.

**Tech-debt (next sprint, after the demo loop closes):**

7. **KAN-39** (~1 hour) — required-env-var assertion in `backend-deploy.yml`. Complements the `--set-env-vars` → `--update-env-vars` fix already shipped in PR #39.
8. **KAN-45** (~2–3 hours) — Secret Manager refs for `GEMINI_API_KEY` + `DOCUMENT_AI_PROCESSOR_ID`. Sibling to KAN-39; together they cover deploy-time *and* post-deploy hardening. Also removes the founder-must-remember-the-safer-rotation-pattern dependency on the next key rotation.
9. **Close KAN-1 epic** — all child stories shipped; only the parent remains open.

**Strategic hygiene (rolling):**

10. **Triage unassigned hardening/compliance work** (`KAN-20`, `KAN-28–31`, `KAN-44`, `KAN-45`, `KAN-46`) once the demo loop closes. KAN-26–31 currently PARKED pending strategic reframe.

**Done in the 2026-04-29 → 2026-04-30 sessions** (kept here briefly for traceability; will rotate out on the next Cursor-MCP refresh):

- ~~PR #43 (PRD v0.3 positioning reconcile)~~ ✅ merged 2026-04-30T00:10:00Z (`4b6f0c3`)
- ~~PR #44 (subagent suite + plans/ directory)~~ ✅ merged 2026-04-30T02:44:49Z (`6f1f0e9`)
- ~~PR #45 (this snapshot file)~~ ✅ merged 2026-04-30T02:41:40Z (`ea1f9ec`)
- ~~PR #46 (KAN-46 first-fix step)~~ ✅ merged 2026-04-30T03:12:43Z (`503ae35`)
- ~~Verify KAN-43 production fix and transition In Review → Done~~ ✅ done 2026-04-30 02:31 UTC
- ~~Rotate the AI Studio `GEMINI_API_KEY`~~ ✅ done 2026-04-30 (founder); old key revoked. KAN-45 still tracks the Secret Manager hardening.
- ~~End-to-end `/analyze` + `/routing` smoke test from the Lovable preview~~ ✅ done 2026-04-30 02:31 UTC (200 in 6.97s on `/analyze`; the same test surfaced KAN-46 on the `/routing` 422)

---

## Repo pointers

> **Note:** several pointers below land on `main` only after **PR #44** merges — `docs/marketing/`, the expanded `.claude/agents/` set (11 agents), and `plans/` were authored on the `feature/marketing-pr-agent` branch and do not yet exist on this PR's base. They are listed forward-looking so this snapshot is correct on the day PR #44 lands; until then, paths marked **(post-PR-#44)** below resolve to 404 on `main`.
>
- Project guide: [docs/CLAUDE.md](./CLAUDE.md) — last updated 2026-04-29 with the PRD v0.3 reconciliation footer.
- Product requirements: [docs/PRD.md](./PRD.md) — v0.3, locked one-liner in §1.
- Marketing asset library: [docs/marketing/](./marketing/) **(post-PR-#44)** — first asset `2026-04-29-linkedin-broker-augmentation.md` (working draft).
- Agent prompts: [.claude/agents/](../.claude/agents/) **(post-PR-#44)** — 11 agents registered (the original 4 on `main` today, plus `marketing-pr`, `mentor`, `architect`, `frontend-engineer`, `qa-engineer`, `task-decomposer`, `context-keeper` landing with PR #44).
- Plan files directory: [plans/](../plans/) **(post-PR-#44)** — feature plans authored by `task-decomposer` before multi-commit work begins; first entries are `kan-16-multi-tenant-isolation/plan.md` (executed) and `kan-21-export-corridor-compliance/plan.md` (queued).
- Live API: https://puente-backend-519686233522.us-central1.run.app

---

*Jira is source of truth. Refresh this file after any status transition, major comment policy change, or ticket creation/deprecation decision. Refresh command: `searchJiraIssuesUsingJql` with `jql: "project = KAN ORDER BY key ASC"`, `maxResults: 100`, `fields: ["summary", "status", "priority", "issuetype", "labels", "resolutiondate", "updated", "assignee"]`.*
