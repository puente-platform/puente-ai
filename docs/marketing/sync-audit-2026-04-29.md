# Sync Audit — Marketing Artifacts vs. Authoritative Brand References

**Author:** Senior Marketing & Communications Lead
**Date:** 2026-04-29
**Audited against:**
- `puente-ai-brand-guide.pdf` v1 (official brand guide, generated from `src/index.css` + `tailwind.config.ts`)
- `BRAND.md` (brand identity / positioning truth)
- `DESIGN.md` (visual / design-system spec)
- `puente-linkedin-philosophy.md` (Gilded Meridian visual philosophy + voice)

**Artifacts audited:**
- `marketing/brand-profile-2026-04-29.md` — Brand Profile for social-media tool (now updated in place; see Section B below)
- `marketing/website-copy-refresh-2026-04-29.md` — website copy refresh draft
- `docs/marketing/2026-04-29-linkedin-broker-augmentation.md` — published founder LinkedIn post

---

## A. In sync (already aligned across artifacts and references)

- **Locked one-liner.** All three artifacts use the PRD §1 verbatim line: *"Puente AI turns a trade document into compliance and payment routing in 15 seconds — for SMEs and customs brokers in the US–LATAM trade corridor."* Confirmed in `brand-profile-2026-04-29.md` §1, `website-copy-refresh-2026-04-29.md` §3.2, and structurally implied in the LinkedIn post hook.
- **Trade intelligence platform / layer framing.** BRAND.md §9 names Puente "Trade intelligence layer for the US–LATAM corridor" and DESIGN.md §1 names it "a trade intelligence platform." Both phrasings are used in the website copy and the brand profile §1.
- **"Not a bank, not a money transmitter, do not move funds."** BRAND.md §9 "What we are NOT" is mirrored in `brand-profile-2026-04-29.md` §1 ("Puente AI is not a bank, a wallet, a crypto exchange, a remittance app, or a broker-replacement") and in `website-copy-refresh-2026-04-29.md` §4.5 FAQ #1 ("No. Puente AI is a trade intelligence platform... we do not move money in V1").
- **V1 honesty / verb discipline.** "Show, compare, flag, recommend, surface, score, route" — and never "send, settle, wire, transfer-on-behalf" — is consistently applied across the website copy (FAQ #1, FAQ #4, hero microcopy disclosure), the LinkedIn post body, and the brand profile §2.
- **Bilingual posture.** Spanish written from a blank page (not translated) is honored in all three artifacts: hero rotation (§3.1), FAQ (§4.5), CTA (§4.4) of website copy; full ES body of the LinkedIn post; and §2 of the brand profile.
- **Maria + Carlos co-equal personas.** Every customer-facing surface treats both. PRD §4 + BRAND.md §9 (Maria as target persona) + the corridor-direction-agnostic CLAUDE.md guidance — all consistently applied.
- **Savings figure rule.** `text-emerald`, 56px, DM Sans 700 — surfaced explicitly in `brand-profile-2026-04-29.md` §3 after the update, matching `puente-ai-brand-guide.pdf` §1 + §7 + BRAND.md §1.
- **Numbers earn trust.** Specific dollar amounts ($1,200 / $1,500 / $1,800 / $2,400) and concrete claims (113 tests, ~15s, 5 corridors, 20–50 broker client files) are used in place of vague adjectives across the website copy, the LinkedIn post, and the brand profile §2.
- **Tone anchor.** "Trustworthy like a bank, warm like a Miami neighbor" (BRAND.md §9) is now explicitly cited in `brand-profile-2026-04-29.md` §1 and §2.

---

## B. Drifted (now fixed in `marketing/brand-profile-2026-04-29.md`)

Format: file → field → was → now → source citation.

| File | Field | Was | Now | Source |
|---|---|---|---|---|
| `brand-profile-2026-04-29.md` | §3 — primary brand color (Gold) | "Puente Orange (a warm orange roughly #F39C2E, drawn from the existing logo)" | **Gold (Primary) `#F9B405`**, HSL `43 96% 50%`, token `--gold` / `--primary`, Tailwind `bg-primary` | `puente-ai-brand-guide.pdf` p. 1 §2 ("Colores principales (marca)"); BRAND.md §2 |
| `brand-profile-2026-04-29.md` | §3 — navy / ink | "deep navy / ink (roughly #0F1729)" | **Dark Navy `#202836`**, HSL `217 26% 17%`, token `--navy`. Plus **Navy Light `#333C4C`** for variants. | `puente-ai-brand-guide.pdf` p. 1 §2; BRAND.md §2 |
| `brand-profile-2026-04-29.md` | §3 — green accent | "corridor green (roughly #1FB07F) reserved for 'saved,' 'approved,' 'recommended,' or 'in-policy' states" | **Emerald (Savings) `#079667`**, HSL `160 91% 31%`, token `--emerald`. Reserved for savings figures (56px DM Sans 700) and success states (`compliance ✓`, `routed ✓`). Never as a background. | `puente-ai-brand-guide.pdf` p. 1 §2 + p. 4 §7 ("Cifras de ahorro: text-emerald · 56px bold · regla irrompible"); BRAND.md §1 + §7 |
| `brand-profile-2026-04-29.md` | §3 — palette completeness | Three placeholder colors (orange, navy, green) | Full nine-color brand palette + light/dark semantic tokens + brand gradients (`text-gradient-gold`, `bg-gradient-gold`, `bg-gradient-navy`, `glow-gold`, `glass`). Adds Ocean Teal `#287AA3`, Gold Light `#F7BB53`, Warm Amber `#F9B405`, Amber Orange `#AB6C07`, Danger Red `#DC2828`, plus all light/dark `--background` `--foreground` `--card` `--muted` `--border` `--sidebar-background` tokens. | `puente-ai-brand-guide.pdf` pp. 1–2 §2 + §3 + §4; BRAND.md §2–4 |
| `brand-profile-2026-04-29.md` | §3 — surface color | "Surfaces are white or off-white" (vague) | Light mode `--background` `#F7F5F1` (warm cream); dark mode `--background` `#0C1116`. Card `#FDFCFB` light / `#111821` dark. | `puente-ai-brand-guide.pdf` p. 2 §3 |
| `brand-profile-2026-04-29.md` | §3 — body / UI typeface | "clean geometric sans (Inter, IBM Plex Sans, or similar)" — placeholder guess | **DM Sans** (weights 400, 500, 600, 700) — default on `<body>`, token `font-body` | `puente-ai-brand-guide.pdf` p. 1 §1; BRAND.md §1 |
| `brand-profile-2026-04-29.md` | §3 — heading typeface | "humanist serif (Source Serif, Lora, or similar) is acceptable for headline emphasis only" — wrong category and wrong faces | **Funnel Display** (weights 300–800) — token `font-display` for all H1–H6. No serif. No third family. | `puente-ai-brand-guide.pdf` p. 1 §1; BRAND.md §1 |
| `brand-profile-2026-04-29.md` | §3 — type stack rule | (silent) | Hard rule: never mix in a third family. If a piece needs accent, use weight or size within Funnel Display + DM Sans. | `puente-ai-brand-guide.pdf` p. 1 §1 ("Regla: nunca mezclar otras familias"); BRAND.md §1 |
| `brand-profile-2026-04-29.md` | §3 — savings-figure rule | (absent) | Savings figures: DM Sans 700, 56px, `text-emerald`. Unbreakable product rule. | `puente-ai-brand-guide.pdf` p. 1 §1 + p. 4 §7; BRAND.md §1 + §7 |
| `brand-profile-2026-04-29.md` | §3 — visual philosophy framing | "editorial-clean meets document-forward... closer to *The Economist* and *FT Weekend*" | Same plus the named **Gilded Meridian** philosophy: navy-and-gold meridian, the diagonal as sacred line of transit, dot grids and luminous pathways with the precision of astronomical charts. | `puente-linkedin-philosophy.md` §I–V |
| `brand-profile-2026-04-29.md` | §3 — gradients | "This is not a bright-gradient brand" (forbidden) | Reframed: brand-sanctioned gradients exist (`text-gradient-gold`, `bg-gradient-gold`, `bg-gradient-navy`) and are part of the system. Random/decorative gradients remain off-brand; the navy-to-gold gradient is "a narrative of transformation" (philosophy §II) and is encouraged. | `puente-ai-brand-guide.pdf` p. 2 §4; `puente-linkedin-philosophy.md` §II |
| `brand-profile-2026-04-29.md` | §3 — logo rules | (absent) | Mark = bridge-arc "P". Wordmark = `PUENTE AI` in Funnel Display Bold, tracking-tight. White logo on dark + masked with `bg-gradient-gold`. Minimum clear space = height of the "P". | BRAND.md §10 |
| `brand-profile-2026-04-29.md` | §3 — shape system | (absent) | `--radius` = `0.75rem` (12px) base for cards/buttons. | `puente-ai-brand-guide.pdf` p. 2 §5; BRAND.md §5 |
| `brand-profile-2026-04-29.md` | §3 — off-brand list | Generic list (gradient backgrounds, neon, mascots, etc.) | Same plus Puente-specific: a third typeface beyond Funnel Display + DM Sans; raw hex values used in components instead of semantic tokens; demoting the savings figure below 56px or out of emerald; using emerald as a background. | `puente-ai-brand-guide.pdf` p. 1 §2 ("Nunca uses HEX directo"), §1 ("nunca mezclar otras familias"), §7 ("regla irrompible") |
| `brand-profile-2026-04-29.md` | §1 — positioning phrasing | (lacked the locked tagline + tone anchor) | Now leads with: tagline *"Pay less. Move faster."* + tone *"trustworthy like a bank, warm like a Miami neighbor"* + positioning *"trade intelligence layer for the US–LATAM corridor"* — all attributed to BRAND.md §9. | BRAND.md §9 |
| `brand-profile-2026-04-29.md` | §2 — copy do's | (generic) | Adds BRAND.md §9 specifics: plain language ("Fraud Score" not "Risk Assessment Matrix"), dollar figures over percentages, dual-language labels for critical financial terms only, no fabricated customers, no claimed licenses, no "verified supplier" without document support. | BRAND.md §9 ("Copy do's & don'ts") |
| `brand-profile-2026-04-29.md` | §2 — bilingual posture | "Spanish is neutral LatAm, 'tú' form" (correct but incomplete) | Same plus BRAND.md §9 language scope: EN / ES / PT supported, with proper nouns and locations preserved in their original language (*Tejidos Medellín*, *São Paulo*, *Doral*, *Santo Domingo*). | BRAND.md §9 (Idiomas) |
| `brand-profile-2026-04-29.md` | §2 — restraint / tone close | (absent) | New closing paragraph cites the Gilded Meridian §IV restraint principle ("text as a whisper against the gradient's roar") and pairs it with the bank-warmth tone test from BRAND.md §9. | `puente-linkedin-philosophy.md` §IV; BRAND.md §9 |
| `brand-profile-2026-04-29.md` | front-matter "Aligned to:" | Listed PRD, website copy, CLAUDE.md only | Adds the four authoritative reference docs by name (brand guide PDF, BRAND.md, DESIGN.md, philosophy doc). | meta |

---

## C. Drifted (NOT auto-fixed — needs founder decision)

These are conflicts in `website-copy-refresh-2026-04-29.md` or `docs/marketing/2026-04-29-linkedin-broker-augmentation.md` that touch shipped or about-to-ship copy. I have not edited those files. Each item below names where, what conflicts, recommended fix, and the source citation.

### C.1 — Tagline absent from website copy refresh

**Where:** `website-copy-refresh-2026-04-29.md` §3.2 (Static hero), §1 (Positioning summary).
**Conflict:** BRAND.md §9 names *"Pay less. Move faster."* as the brand tagline. The website copy refresh leads with the locked one-liner (correct) but never surfaces the tagline anywhere — not in the hero, not as an eyebrow line above the headline, not in the trust footer.
**Recommended fix:** Add *"Pay less. Move faster."* (EN) / *"Paga menos. Mueve más rápido."* (ES) as a tagline element somewhere on the homepage — most natural placements are (a) above-the-headline eyebrow, (b) below the hero CTAs as a tagline strip, or (c) in the trust footer alongside the corridor-built-for line. Founder picks the placement; the tagline itself is non-negotiable.
**Source:** `puente-ai-brand-guide.pdf` p. 4 §8 ("Tagline: Pay less. Move faster."); BRAND.md §9.

### C.2 — Trust footer references "Document AI + Gemini on Google Cloud" as `poweredBy`; brand guide names a different "Powered by" string for trust signaling

**Where:** `website-copy-refresh-2026-04-29.md` §4.6 (Trust footer), `poweredBy` proposed string.
**Conflict:** The website copy proposes *"Document AI + Gemini on Google Cloud"* / *"Document AI + Gemini sobre Google Cloud"* — accurate and specific, which is good. However, `DESIGN.md` §11 names a canonical footer line: *"Powered by Google Cloud AI."* This is shorter and matches what the brand guide implies as a trust-footer pattern (`puente-ai-brand-guide.pdf` p. 4 §7 — "Trust signals (footer): `text-muted-foreground` + iconos sutiles").
**Recommended fix:** Founder picks. **Option A (more specific, current proposal):** keep "Document AI + Gemini on Google Cloud" — names the actual stack, more credible to technically literate readers. **Option B (matches DESIGN.md):** revert to *"Powered by Google Cloud AI"* / *"Impulsado por Google Cloud AI"* — shorter, scans faster in a footer, matches the existing canonical string. Recommendation: Option A — the current website copy proposal is more honest and specific, and DESIGN.md predates the v0.3 reconciliation. But this is a brand-system call, not a marketing call.
**Source:** `DESIGN.md` §11 ("Footer: 'Powered by Google Cloud AI.'"); `puente-ai-brand-guide.pdf` p. 4 §7.

### C.3 — DESIGN.md names a different palette + typography (legacy, but document is named in brand-system folder)

**Where:** `DESIGN.md` §4 ("Design Tokens").
**Conflict:** DESIGN.md §4 lists `dark-navy: #0A1628`, `deep-teal: #0D7F7F`, `emerald: #059669`, `warm-amber: #F5A623`, `slate: #0F172A`, plus typefaces "Plus Jakarta Sans 700" (headlines) and "Inter 400" (body). All seven of these values disagree with the brand guide PDF (which is the load-bearing source: `#202836` Dark Navy, `#287AA3` Ocean Teal, `#079667` Emerald, `#F9B405` Warm Amber, Funnel Display + DM Sans).
**Recommended fix:** Not a marketing-artifact change — this is a docs-engineering issue. **DESIGN.md §4 should be deprecated or rewritten** to reference the brand guide PDF + `src/index.css` rather than asserting its own (legacy, drifted) values. Until that happens, anyone consulting DESIGN.md in isolation will pull wrong colors and typefaces. Recommend a header note at the top of DESIGN.md: *"§4 Design Tokens are legacy placeholders. The source of truth for color and typography is `puente-ai-brand-guide.pdf` v1 and the live `src/index.css` / `tailwind.config.ts`."*
**Source:** `puente-ai-brand-guide.pdf` p. 1 §1 + §2; BRAND.md §1 + §2.

### C.4 — LinkedIn post is fully aligned

**Where:** `docs/marketing/2026-04-29-linkedin-broker-augmentation.md`.
**Conflict:** None. The post passes the LinkedIn philosophy doc on every load-bearing dimension:
- **Founder voice / first-person / Modern Parable structure** — uses the goTRG observed-scene preamble ("After 4 years selling US liquidation truckloads...") and lands on a single principle ("broker-augmentation, not broker-replacement"). Matches the philosophy doc's restraint principle (`puente-linkedin-philosophy.md` §IV–V).
- **V1-honest verbs** — "the math is honest about what each option costs and what each option saves." No "send / settle / wire / transfer." Matches BRAND.md §9 don'ts and the brand profile §2 verb discipline.
- **Bilingual EN + ES, written from blank pages.** Confirmed — the ES post is not a translation; "atrapados en trabajo que la IA puede hacer en 15 segundos" is idiomatic Spanish, not English-with-Spanish-flavor.
- **Specific numbers** — 4 years, 40%, 20–50 active client files, 15 seconds, 30 minutes. No vague claims.
- **Single-action CTA** — DM the founder for a 30-minute call.
- **No prohibited claims** — no fabricated customer counts, no claimed licenses, no partisan tariff framing.
- **Tone** — trustworthy + Miami-warm. Matches BRAND.md §9 tone anchor.

The Spanish-vocabulary follow-up note in §"Notes for the founder" item 4 (LinkedIn ES "agente de aduana" vs. WhatsApp "broker aduanero") is correctly flagged for founder decision and is consistent with the bilingual posture rule. **Verdict: aligned. Ship it.**

**Source:** `puente-linkedin-philosophy.md` §I–V; BRAND.md §9; brand profile §2.

### C.5 — Animated hero rotation does not visually anchor on emerald savings figure

**Where:** `website-copy-refresh-2026-04-29.md` §3.1 (animated rotating text frames 1–8).
**Conflict:** The brand guide is unambiguous that the dollar-savings figure is the visual anchor — `text-emerald`, 56px DM Sans 700, "regla irrompible" (`puente-ai-brand-guide.pdf` p. 4 §7). The animated hero rotation foregrounds the savings number ("$1,200 less", "$1,800 less", etc.) which is correct in copy terms, but the website copy doc does not specify that the dollar amount within each frame should render in `text-emerald` at the brand-guide-mandated treatment. As specced today, a Lovable implementer might render the entire frame in a single foreground color and miss the emerald-on-savings rule.
**Recommended fix:** Add a render note to §3.1 of `website-copy-refresh-2026-04-29.md`: *"Within each animated frame, the dollar-savings token (`$1,200 less` / `5 días antes` etc.) must render in `text-emerald` per the brand guide savings-figure rule (`puente-ai-brand-guide.pdf` §7). The surrounding sentence renders in the default `--foreground`. Both render in DM Sans (token `font-body`), with the savings figure at heading-display weight."*
**Source:** `puente-ai-brand-guide.pdf` p. 1 §1 + p. 4 §7; BRAND.md §1 + §7.

### C.6 — Stat-row colors and treatments unspecified

**Where:** `website-copy-refresh-2026-04-29.md` §4.2 (Stats row, four stat values: ~15s, 5 corridors, 113 tests, Wire vs. stablecoin).
**Conflict:** The brand guide's usage map (`puente-ai-brand-guide.pdf` p. 4 §7) maps numeric values to specific tokens — savings figures to emerald; processing states to navy + `pill-pulse`; success states to emerald. The current §4.2 spec gives strings but no rendering treatment, which leaves the four stat numbers (~15s, 5 corridors, 113 tests) up to the implementer's interpretation. Stat #2 ("5 corridors") and stat #3 ("113 tests") are not "savings" — applying emerald there would dilute the savings-figure rule.
**Recommended fix:** Add a render note to §4.2: *"Stat values render in DM Sans 700 in `--foreground` (light mode `#0E1629`, dark mode `#F8F9FA`). Do **not** render stat-row numbers in emerald — emerald is reserved for savings figures and success states. Stat-row treatment is type-weight-led, not color-led."*
**Source:** `puente-ai-brand-guide.pdf` p. 4 §7; BRAND.md §7.

### C.7 — Founder-quote block typography unspecified

**Where:** `website-copy-refresh-2026-04-29.md` §6.3 (Founder-quote block drop-in copy).
**Conflict:** The founder quote is specified in copy but not in render. Pull-quotes in a brand system this disciplined typically warrant a treatment note (typeface, size, color, alignment, attribution typography). The brand guide §1 names Funnel Display for headings and DM Sans for body; the philosophy doc §IV calls for "thin, luminous, spaced with architectural precision." A founder pull-quote on a public homepage is a load-bearing piece of trust copy and deserves an explicit treatment.
**Recommended fix:** Add to §6.3: *"Render the founder quote in Funnel Display 400 at large display size (suggest 32–40px depending on viewport), color `--foreground`, italic optional. Attribution line ('— Jay Alexander, founder') in DM Sans 500, `text-muted-foreground`, smaller. Block left-aligned, with a subtle gold accent rule on the left edge using `border-gold-subtle` (`puente-ai-brand-guide.pdf` §4) to visually anchor the quote without competing with the hero."*
**Source:** `puente-ai-brand-guide.pdf` p. 1 §1 + p. 2 §4; `puente-linkedin-philosophy.md` §IV.

---

## Summary

- **Brand profile** — color palette, typography, logo rules, and visual philosophy fully reconciled to the four authoritative references. File updated in place.
- **Website copy refresh** — copy is on-positioning and V1-honest; six rendering / brand-system notes (C.1, C.2, C.5, C.6, C.7) flagged for founder decision before Lovable handoff. None require copy rewrites — they require render-treatment additions.
- **LinkedIn post** — fully aligned. Ship it.
- **DESIGN.md** — has drifted color and typography values that disagree with the brand guide PDF; recommend a deprecation header on §4 (out of marketing-team scope; flagged here for the founder to route to docs-engineering).

**Files touched:**
- `marketing/brand-profile-2026-04-29.md` (edited in place)
- `marketing/sync-audit-2026-04-29.md` (this file)

**Files flagged but not edited:**
- `marketing/website-copy-refresh-2026-04-29.md`
- `docs/marketing/2026-04-29-linkedin-broker-augmentation.md`
- `DESIGN.md` (out of scope, but flagged for docs-engineering follow-up)
