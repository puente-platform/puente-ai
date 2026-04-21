# Weekly Operating Rhythm — Puente AI

This is the execution cadence for a solo founder + AI operator stack.

Use with:
- `docs/MONDAY_PLANNING_TEMPLATE.md`
- `docs/FOUNDER_SCORECARD.md`

---

## Monday -> Friday Cadence (10 Bullets)

1. Monday morning: lock the week to 3 outcomes max using `MONDAY_PLANNING_TEMPLATE.md`.
2. Map every outcome to Jira tickets (KAN IDs) with clear owners and Definition of Done.
3. Assign explicit AI roles: Cursor (execution), Claude (code/testing), Gemini (options/UX), Perplexity (research/evidence).
4. Ship one meaningful slice by end of Tuesday (not partial scaffolding).
5. Wednesday midday: run a 20-minute risk check (security, compliance wording, latency, cost per doc).
6. Keep auth/tenant boundaries and legal-safe language as non-negotiables in all shipped work.
7. Thursday: finish integration, tests, and docs so Friday is demo-ready.
8. Friday morning: demo what is done, not what is in progress; capture proof points and blockers.
9. Friday afternoon: complete `FOUNDER_SCORECARD.md` with a numeric weekly grade and root-cause misses.
10. Before ending Friday: pre-draft next week theme and top outcomes to reduce Monday startup friction.

---

## Non-Negotiable Rules

- WIP cap: maximum 3 active outcomes per week.
- No hidden work: every meaningful task maps to a ticket.
- No "done" without test evidence or demo evidence.
- No new feature starts before high-risk blockers are addressed.
- Business logic remains provider-agnostic (especially payment rails integrations).

---

## KPI Minimum Set (Track Weekly)

- Delivery: tickets completed vs committed
- Reliability: API success rate, error rate, P95 latency
- Unit economics: cost per analyzed document
- GTM: active pilots, conversion/proof signals
- Trust: security/compliance issues opened vs resolved

---

## Escalation Triggers

Trigger an immediate strategy reset if any are true:
- Two consecutive weeks below 70% committed delivery
- Material security/compliance issue without owner
- Rising cost per document for two straight weeks
- No customer signal/progress for two consecutive weeks

When triggered, pause new scope for 48 hours and run a focused replanning cycle.
