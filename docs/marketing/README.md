# Puente AI — Marketing & PR Asset Library

This directory holds all customer-facing and press-facing copy produced for Puente AI. The `marketing-pr` agent (see `.claude/agents/marketing-pr.md`) is the primary author; the founder is the publisher.

---

## Directory Layout

```
docs/marketing/
├── README.md                           ← this file
├── website/                            ← website copy (hero, value-prop, About, FAQ, footer, persona-specific landing pages)
├── press/                              ← press releases, media advisories, founder bios, journalist Q&A briefings
├── social/                             ← LinkedIn, Twitter/X, Instagram, WhatsApp Business
├── email/                              ← cold outreach, nurture sequences, founder weekly updates, transactional copy
├── sales/                              ← one-pagers, demo scripts (5/15/30-min), email signatures, talk-tracks
├── investor/                           ← investor cold email, follow-up copy (NOT the pitch deck — that lives in docs/future-vision/)
└── YYYY-MM-DD-<slug>.md                ← single-asset working drafts, dated for traceability
```

Sub-directories are created on demand. Single-asset working drafts can live at the top level using the dated-slug pattern (e.g., `2026-04-29-linkedin-broker-augmentation.md`).

---

## Authoring Conventions

Every asset in this directory follows the `marketing-pr` agent's output format:

- **Header block:** asset type, audience, goal, voice, language, compliance pass status.
- **Headline / Subject / Hook** — written and rewritten until it earns 60% of the word count.
- **Body** — ready-to-publish copy.
- **Spanish version** — when bilingual; written in Spanish from a blank page, not translated from the English.
- **CTA** — verb-led, single-action.
- **Visual / asset brief** — when applicable.
- **Suggested distribution** — channels, sequencing, paid vs. organic, founder-account vs. brand-account.
- **A/B variants** — when applicable.
- **Notes for the founder** — anything needing founder confirmation before publishing (compliance edges, unverifiable claims, customer permissions).

---

## Compliance Pass Status (every asset must carry one of these)

| Status | Meaning |
|---|---|
| `yes` | Asset clears all 7 compliance guardrails in `.claude/agents/marketing-pr.md`. Safe to publish. |
| `yes-with-caveats` | Asset clears compliance but contains a placeholder (e.g., `[N]` for a customer count, or a TBD dollar figure) that must be filled or removed before publishing. |
| `needs fintech-security review` | Asset contains language that may approach regulated-claim territory. Must be reviewed by the `fintech-security` agent (or the founder + counsel) before publishing. |
| `needs ceo-scope review` | Asset implies a positioning or roadmap commitment not in the current PRD. Must be reviewed by the `ceo-scope` agent before publishing. |

---

## What This Directory Is NOT For

- **Investor pitch deck construction** — that lives in `docs/future-vision/pitch-deck-outline.md` and is owned by the founder. The `marketing-pr` agent can polish individual slides or write the email that carries the deck, but the deck itself is not a marketing-team artifact.
- **Internal product copy** — error messages, button labels, in-app onboarding microcopy. That's a frontend-engineer concern, with marketing-pr available for tone review on request.
- **Engineering documentation, API references, runbooks** — that's `docs/`, `docs/api-contracts/`, and `docs/ADR/`.
- **Legal documents, terms of service, privacy policy** — those require counsel, not marketing.

---

## Versioning

Marketing assets are committed to git for the same reasons code is: traceability, reviewability, and revertibility. When an asset is published, the publication date and channel are recorded in the asset's "Notes for the founder" section, and the file moves from `working draft` to `published` status (or stays at the top level if the dated-slug pattern is being used).

---

*This directory was created 2026-04-29 alongside the `marketing-pr` agent. First asset: `2026-04-29-linkedin-broker-augmentation.md` — a founder-voice LinkedIn post articulating the broker-augmentation positioning to the Miami SME and customs broker community, bilingual EN/ES.*
