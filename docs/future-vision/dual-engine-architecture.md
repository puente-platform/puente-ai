# Dual-Engine Architecture — Vision Doc

**Status:** Vision, not status.
**Last authored:** 2026-05-04
**Audience:** Founder, AI assistants (Claude, Cursor), future engineers.

---

## Doc-State Rules (read first)

This doc maps a strategic framing of Puente AI ("Compliance Engine"
+ "Optimization Engine") onto the actual codebase, so that AI
assistants discussing roadmap don't drift into hallucinated
capability claims.

It follows the same Doc-State Policy as `docs/CLAUDE.md`:

1. **No ticket statuses in this file.** Each capability is pinned
   to a code path (if shipped) and a Jira ID (if a ticket exists),
   never to "Done / In Progress / To Do." Ticket status drifts
   weekly; that's the Jira board's job, not this doc's.
2. **Verify before citing.** Before telling the user "Puente has
   shipped X," confirm the cited code path exists in the current
   working tree. If a Jira ID is cited, check
   `docs/JIRA_BOARD_SNAPSHOT.md` for the per-ticket detail (or
   query the Atlassian MCP for live state).
3. **Vision rows are honest "not started" by default.** A pillar
   row that says "no file" means there is no implementation in
   the repo today. Do not pattern-match a vaguely related file
   into being the implementation.
4. **On conflict with `docs/CLAUDE.md` "Current Build Status":**
   CLAUDE.md wins. This doc is the longer-horizon framing;
   CLAUDE.md is the capability ledger.

---

## The Framing in One Paragraph

Puente AI is being built as a two-stage system. Stage one — the
**Compliance Engine** — turns messy, unstructured trade documents
into structured, auditable data (a deterministic-parsing problem,
in CS terms a compiler). Stage two — the **Optimization Engine**
— turns that structured data into routing and inventory decisions
under uncertainty (a stochastic-modeling problem, in CS terms a
pathfinding algorithm over a noisy network). Today, stage one is
substantially shipped; stage two is unbuilt. The strategic moat
is the **data flywheel** between them: every document the
Compliance Engine processes generates labeled training data the
Optimization Engine will eventually need. That flywheel is
plumbed at the storage layer but not yet closed at the training
layer.

This framing does not change the v0.3 PRD priority — compliance
first, optimization later. It only gives the existing roadmap a
shared vocabulary.

---

## Pillar 1 — Compliance Engine (Data Ingestion Layer)

The "sensors" of the system. Takes a trade document in, returns
extracted fields + compliance gap analysis + payment routing
recommendation in <15 seconds. CS analogy: a compiler that lowers
unstructured human input into a structured executable form.

| Capability                       | Code path                                       | Jira ID(s)         | Gap                                                                                                  |
| -------------------------------- | ----------------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
| PDF upload → GCS                 | `backend/app/routes/upload.py`                  | KAN-16 (scoping)   | None at MVP scope.                                                                                   |
| Invoice extraction (Document AI) | `backend/app/services/document_ai.py`           | KAN-2, KAN-44      | Invoice-only schema. No bill of lading, no certificate of origin, no packing list parsers.           |
| LLM analysis layer               | `backend/app/services/gemini.py`                | KAN-3, KAN-42      | 3-tier auth resolution wired; Vertex Express path dormant pending project-block clearance.           |
| Compliance gap detection         | `backend/app/services/compliance.py`            | KAN-4              | Rule-based, US-import-direction-only. US→LATAM export rules (EAR, BIS, DR-CAFTA CoO) not yet built. |
| US→LATAM export compliance rules | no file                                         | KAN-21 (un-parked) | Not started. Sequencing dependency on KAN-22 per ticket description.                                 |
| Payment routing recommendation   | `backend/app/services/payment_routing.py`       | KAN-5, KAN-23      | **Deterministic, not learned.** Rules-based today; this is what the Optimization Engine will replace. |
| Persistence (multi-tenant)       | `backend/app/services/firestore.py`             | KAN-6, KAN-16      | Path-scoped subcollection `transactions/{user_id}/docs/{doc_id}`. None at current scope.            |
| Auth (Firebase JWT)              | `backend/app/services/auth.py`                  | KAN-15             | None at current scope.                                                                               |
| User onboarding (PII profile)    | `backend/app/routes/onboarding.py`              | (no KAN cited)     | Fintech-security audited 2026-04-30.                                                                 |
| Frontend (extraction UX)         | `frontend-app/src/pages/AnalyzePage.tsx` et al. | KAN-33, KAN-34, KAN-35 | Lovable-migrated Vite + React, deployed to Cloud Run service `puente-frontend`.                  |

**Honest status of Pillar 1:** the MVP loop (upload → extract →
analyze → comply → route → persist → display) is end-to-end
operational for the LATAM→US import direction with invoice-class
documents. The two largest in-pillar gaps are (a) the US→LATAM
direction (KAN-21) and (b) document classes beyond invoices.
Neither is an "Optimization Engine" item — both extend Pillar 1.

---

## Pillar 2 — Optimization Engine (Predictive Modeler)

The "pathfinder." Takes the structured data produced by Pillar 1,
combined with external signals (port congestion, carrier
performance, FX volatility), and outputs probabilistic
recommendations: "reroute through Port B," "pre-file document X,"
"hold the wire 24h, FX moves your way." CS analogy: a
reinforcement-learning agent over a Markov decision process whose
state space includes both the trade graph and the regulatory
graph.

| Capability                              | Code path | Jira ID(s) | Prerequisite                                                                                         |
| --------------------------------------- | --------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| Carrier / port telemetry ingestion      | no file   | none       | Identify a feed (carrier APIs, marine traffic providers, customs broker EDI). Decision not made.    |
| Time-series store (delays, fees, FX)    | no file   | none       | Schema TBD. Could ride on Firestore initially; likely needs a columnar store at scale.              |
| Markov model — port congestion          | no file   | none       | Telemetry ingestion above + ≥6 months of history.                                                   |
| Reinforcement-learning router           | no file   | none       | Closed-loop reward signal (see Data Flywheel below). Today there is no observable "did the recommendation save money" event in the system. |
| Decision-support / Nash-equilibrium UX  | no file   | none       | Pillar 1 frontend pattern is the precedent; new module.                                             |
| Calibration / confidence propagation    | partial   | none       | See "Open architectural question" below.                                                            |

**Honest status of Pillar 2:** zero implementation. The closest
adjacent code is `payment_routing.py`, which is a deterministic
rules engine — it is the *interface surface* the Optimization
Engine will eventually replace, not a precursor implementation.
Anyone (human or LLM) claiming Puente has "ML routing" today is
wrong; what Puente has is LLM-based document analysis (Pillar 1)
and rules-based routing (Pillar 1's tail).

---

## The Data Flywheel — Plumbed vs. Closed

The strategic claim is that Pillar 1 produces the training data
Pillar 2 needs, creating a moat competitors with no document
ingestion can't replicate. State of that flywheel today:

| Flywheel stage                                  | State   | Notes                                                                                                              |
| ----------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------ |
| Per-tenant, per-document storage                | Plumbed | `transactions/{user_id}/docs/{doc_id}` per KAN-16. Every analyzed document is captured.                            |
| Extraction confidence captured                  | Partial | Document AI returns confidence; Gemini returns analysis scores; KAN-44 added partial-drift warning. Not unified.   |
| Routing recommendation captured                 | Plumbed | `payment_routing.py` writes the recommendation snapshot at decision time.                                          |
| **Outcome capture (was the recommendation acted on, did it save money, did the shipment clear on time)** | **Not started** | This is the missing rung. Without it, there is no reward signal and the Optimization Engine has no labels to learn from. |
| Training pipeline                               | Not started | No `notebooks/`, no `training/`, no model registry.                                                                |
| Feedback into Pillar 1 (recommendation → next-shipment prior) | Not started | Architectural pattern is unbuilt.                                                                                  |

**Implication:** the most valuable single piece of work the
roadmap could pull *toward* the Optimization Engine — without
actually building it — is **outcome capture on the Compliance
Engine's recommendations**. That's a Pillar 1 ticket in scope and
a Pillar 2 prerequisite in effect. Worth raising with `ceo-scope`
when the Pillar 1 compliance-rule expansions (KAN-21, additional
document classes) feel close to shippable.

---

## Open Architectural Question — Confidence Propagation

The clean "deterministic = compliance, stochastic = optimization"
split in the framing is convenient but slightly misleading for
Puente specifically. Pillar 1 is *already* probabilistic at the
edges:

- Document AI returns per-field confidence.
- Gemini returns a fraud-likelihood score and analysis text whose
  reliability varies by document quality.
- KAN-44 added partial-drift detection because the v2 schema
  itself is non-deterministic across vendor releases.

Today these signals are computed and discarded (or surfaced
ad-hoc to the user). There is no unified `confidence` metadata
field that travels with a record from extraction → compliance →
routing → persistence. When the Optimization Engine eventually
trains on Firestore history, the absence of that metadata will
mean every record looks equally trustworthy — which it isn't.

This is the kind of small-now-big-later decision worth pricing
into a Phase 2.5 ticket. It is **not** in scope today, and it is
not on the Jira board today (as of the date in this doc's header).
Surfaced here so it doesn't get lost when Pillar 2 work begins.

---

## Pointers

- **Capability ledger (authoritative):** `docs/CLAUDE.md` →
  "Current Build Status."
- **Per-ticket detail:** `docs/JIRA_BOARD_SNAPSHOT.md` (refresh
  cadence: weekly via Cursor's Atlassian MCP). For live state,
  query the Atlassian MCP directly.
- **Strategic positioning narrative:** `docs/PRD.md` v0.3 (esp.
  §1 Vision and §2 Problem).
- **Investor-facing framing:** `docs/future-vision/pitch-deck-outline.md`,
  `docs/future-vision/investor-teaser.md`.
- **Scope decisions:** invoke the `ceo-scope` agent. It reads PRD
  + current Jira state and returns a four-mode verdict. This doc
  does not encode scope decisions; it only frames the option
  space.

---

*If you are an AI assistant reading this: when the user discusses
"compliance engine," "optimization engine," "RL routing," "data
flywheel," "Markov port model," or any near-synonym, label every
capability claim explicitly as `[Shipped: <code path>]`,
`[Tracked: KAN-X]`, or `[Not in repo]`. Defer scope and
sequencing decisions to the `ceo-scope` agent rather than
asserting them here.*
