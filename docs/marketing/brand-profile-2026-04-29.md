# Puente AI — Brand Profile (Social-Media Tool)

**Author:** Senior Marketing & Communications Lead
**Date:** 2026-04-29
**Aligned to:** PRD v0.3 (`docs/PRD.md`), website copy refresh 2026-04-29 (`marketing/website-copy-refresh-2026-04-29.md`), CLAUDE.md as of 2026-04-30, official brand guide (`puente-ai-brand-guide.pdf` v1, generated from `src/index.css` + `tailwind.config.ts`), `BRAND.md` (brand identity / positioning truth), `DESIGN.md` (visual / design-system spec), `puente-linkedin-philosophy.md` (Gilded Meridian visual philosophy + voice).
**Use:** Paste into a social-media content tool's Brand Profile UI — three independent fields (Brand Brief, Writing Style, Image Style).

---

## Section 1 — Brand Brief

Tagline: *Pay less. Move faster.* Tone: trustworthy like a bank, warm like a Miami neighbor (BRAND.md §9). Positioning: trade intelligence layer for the US–LATAM corridor (BRAND.md §9; DESIGN.md §1). Puente AI is not a bank, not a money transmitter, and does not move funds (BRAND.md §9 — "What we are NOT").

Puente AI turns a trade document into compliance and payment routing in 15 seconds — for SMEs and customs brokers in the US–LATAM trade corridor. The corridor runs in both directions, and Puente serves both. LATAM-origin produce, manufactured goods, and raw materials moving into the US through Miami, Laredo, El Paso, McAllen, and San Diego. US-origin liquidation goods, equipment, and consumer goods moving out to Bogotá, Mexico City, Lima, Santo Domingo, and the broader Caribbean basin. Same upload, same compliance check, same payment-route recommendation — only the importer of record changes.

There are two co-equal users on every shipment. Maria is the Miami-based bilingual SME owner, age 35–55, born in Colombia, Venezuela, the Dominican Republic, or Mexico, managing $500K–$5M a year in cross-border trade volume. She lives on WhatsApp and runs her business from a phone in a warehouse. Carlos is the licensed US customs broker or freight forwarder clearing Maria's shipments — he holds 20–50 active client files and spends roughly 40% of his working hours on routine document review and HS code classification. Puente is broker-augmentation, not broker-replacement. The licensed broker is the channel, the final signer on every regulated certification, and the customer we make faster — never the competitor we work around.

V1 today is a recommendations layer. We read the document with Document AI plus Gemini, extract the fields, score fraud risk, flag compliance gaps, and recommend the cheapest legal payment route — usually a wire-vs-stablecoin comparison, in dollars, before anything moves. We do not move money. We do not send, settle, wire, or transfer funds on a customer's behalf. The customer executes through their existing bank, broker, or wallet. V2 will add direct settlement execution, but only after FinCEN MSB registration in the US, Florida MTL state-level licensing, and EPE registration with the BCRD in the Dominican Republic — none of which are filed yet. Until those are approved we describe V2 as a roadmap milestone, never as a current capability.

Brand pillars: V1 honesty (the product recommends; we say so). Bilingual day one (Spanish is written in Spanish, never machine-translated). Broker-augmentation (we make the licensed broker faster, not obsolete). Fintech-grade trust (specific numbers, named technology, no superlatives). LATAM-warm but US-clean (relationship-first community sensibility, fintech-disciplined claims).

Puente AI is not a bank, a wallet, a crypto exchange, a remittance app, or a broker-replacement. It is a trade intelligence platform that happens to recommend payment rails alongside compliance and fraud signals.

Topics worth writing about: trade compliance for the US–LATAM corridor, customs brokerage as a profession and a workflow, US-Mexico land-border friction, Miami and Doral as a trade-finance ecosystem, the Dominican Republic as a Caribbean-basin hub, stablecoin payment rails (USDC on Stellar) as a wire alternative, OFAC and HS code practical implications for SMEs, the founder-build journey, immigrant-business-owner economics, nearshoring and what it means for SMEs.

Topics to avoid: anything implying Puente moves money today, any reference to MSB / Florida MTL / DR EPE as if approved or filed when they are not, fabricated customer counts, fake testimonials, partisan tariff framing, generic "AI revolution" copy, crypto-investment talk that could read as a securities offer.

Direct-response clarity meets fintech discipline. Specific over generic. Verbs over adjectives. Spanish first-class, never bolt-on.

---

## Section 2 — Writing Style

Sentence length runs short and declarative. Variable rhythm: a punchy 5-word line followed by a 20-word setup, then back to short. No 40-word sentences. If a sentence needs a comma to breathe a third time, it should be two sentences.

Lead with the strongest specific claim, a number, or a named scene. Never open with "In today's fast-paced…", "In a world where…", or any other throat-clear. The first eight words decide whether the post earns the rest.

Paragraphs are one to three sentences. Air between paragraphs. The reader scans first, then reads.

Use V1-honest verbs only. Show. Compare. Flag. Recommend. Surface. Score. Route. Verify. Extract. Explain. Read. Classify. In product context, do not use: send, settle, wire, transfer-on-behalf, move money, pay your supplier, settle the invoice, complete the transaction. The product recommends; the customer executes. Copy that blurs that line creates real legal exposure.

Numbers are always specific. "$1,200 less" beats "save money." "15 seconds" beats "fast." "20–50 active client files" beats "many clients." Round numbers that aren't actually round are a tell — use the real ones (113 tests, not 100; ~15s, not 10s). Per BRAND.md §9 copy rules: prefer dollar figures over percentages whenever possible — "You save $1,240" beats "You save 4.2%."

Plain language over jargon (BRAND.md §9): "Fraud Score" not "Risk Assessment Matrix." Bilingual dual-labels are reserved for critical financial terms only — do not dual-label every UI string. Never say "verified supplier" unless the documents support it; never claim licenses we don't hold; never invent customers (BRAND.md §9 don'ts).

Bilingual posture: when the line lands in both languages, write each from a blank page. Spanish is neutral LatAm, "tú" form. Read the Spanish out loud and ask whether a Dominican, a Colombian, or a Mexican would recognize it as written by someone who speaks the language. Do not write English-with-Spanish-flavor. Write Spanish. Supported languages per BRAND.md §9: EN / ES / PT. Preserve proper nouns and locations in their original language — *Tejidos Medellín*, *São Paulo*, *Doral*, *Santo Domingo* — never anglicize them.

Punctuation: em-dashes earn their keep for emphasis. No exclamation points. No ALL-CAPS except brand names (Puente AI, USDC, FinCEN, BCRD). Quotation marks are for actual quotes only — do not "scare-quote" product features. Oxford commas on.

Emojis are sparing. One per post maximum, only if it does structural work. Acceptable: ✅ ❌ ⚠️ → for marking a list or a flow. Banned: 🚀 💰 🔥 💪 🌟 — fintech-bro energy that erodes trust with this audience.

Format mix across posts: alternate between Vertical Writing (short lines, occasional bullets, lots of air), Process Deep Dive (one specific story unfolded paragraph by paragraph), and Modern Parable (one observed scene leading to one principle). Do not use Scannable Syllabus emoji-heavy format — too transactional for a trust-led category. Do not use Lowercase Journal informal-lowercase style — off-brand for fintech.

Hooks: lead with a number ("40% of a customs broker's week is spent on work AI can do in 15 seconds"), a counterintuitive claim ("The smartest tool you can sell to the Miami trade community is one that makes the broker's day faster, not one that replaces him"), or a named scene ("My mom paid 7% on a $40K wire to Santo Domingo last month"). Never open with a rhetorical question to the reader.

CTAs are rare, specific, and one per post. "Analyze a document at puente.ai" beats "DM me to learn more." "30 minutes of your time this month" beats "let's connect." If the post has no clear next action, it has no CTA — a strong observation post can stand without one.

Founder vs brand voice. Founder posts (Jay) are first-person, plainspoken, can use Modern Parable structure with one observed scene from Miami / Doral / Santo Domingo / the goTRG years. Brand posts are third-person, claim-led, evidence-anchored, with the locked one-liner doing the heavy lifting up top.

If a sentence sounds like it could appear on any fintech LinkedIn account, rewrite it.

Restraint as a discipline. The Gilded Meridian visual philosophy treats text as "a whisper against the gradient's roar — thin, luminous, spaced with architectural precision" (`puente-linkedin-philosophy.md` §IV). The copy equivalent: confidence to use fewer words, to let the number carry the line, to delete the adjective. Trustworthy like a bank, warm like a Miami neighbor (BRAND.md §9 tone anchor) — that pair is the stress-test for every sentence.

---

## Section 3 — Image Style

Overall direction is "Gilded Meridian" — the visual philosophy named in `puente-linkedin-philosophy.md`: a meridian of trust rendered in gold and deep navy, with the diagonal as the sacred line of transit between origin and destination. Editorial-clean, document-forward, scientific-visualization-adjacent. Closer to *The Economist* and *FT Weekend* than to a bouncy app-store landing page. Closer to an astronomical chart than to a SaaS marketing page.

### Color palette (authoritative — `puente-ai-brand-guide.pdf` §2 + `BRAND.md` §2 — extracted from `src/index.css` and `tailwind.config.ts`)

Brand colors — use the named token, never the raw hex, in any product surface. In marketing image work, these are the only colors permitted:

- **Gold (Primary)** — `#F9B405` · HSL `43 96% 50%` · token `--gold` / `--primary` · Tailwind `bg-primary`. This is the brand signal color: primary CTAs, logo gradient, premium emphasis. *"Gold is the signal — intelligence surfacing, value revealed, the precise moment an algorithm transforms raw data into actionable insight"* (`puente-linkedin-philosophy.md` §II).
- **Gold Light** — `#F7BB53` · HSL `38 92% 65%` · token `--gold-light` · Tailwind `bg-gold-light`. Top stop of the gold gradient.
- **Dark Navy** — `#202836` · HSL `217 26% 17%` · token `--navy` · Tailwind `bg-navy`. The vault. Bedrock of institutional trust. Sidebar background in both light and dark mode (`puente-ai-brand-guide.pdf` §3 — "Sidebar es siempre navy en ambos modos"). *"Deep navy is the vault — the bedrock of institutional trust, the weight of compliance, the gravity of secure infrastructure"* (`puente-linkedin-philosophy.md` §II).
- **Navy Light** — `#333C4C` · HSL `217 20% 25%` · token `--navy-light` · Tailwind `bg-navy-light`. Navy variants only.
- **Ocean (Teal)** — `#287AA3` · HSL `200 60% 40%` · token `--ocean` · Tailwind `bg-ocean`. Routing visualization, intermediary frequency between navy and gold.
- **Emerald (Savings)** — `#079667` · HSL `160 91% 31%` · token `--emerald` · Tailwind `bg-emerald`. **Reserved for savings figures and success states only** — `compliance ✓`, `routed ✓`, the dollar-savings number on the results screen. The savings figure rule is non-negotiable: 56px DM Sans 700 in `text-emerald` (`puente-ai-brand-guide.pdf` §1, §7; BRAND.md §1, §7). Never demote it. Never use Emerald as a background.
- **Warm Amber** — `#F9B405` · HSL `43 96% 50%` · token `--warm-amber` · Tailwind `bg-warm-amber`. LATAM / warmth accent. Same hex as Gold but used in a warmth-signal context.
- **Amber Orange** — `#AB6C07` · HSL `37 92% 35%` · token `--amber-orange` · Tailwind `bg-amber-orange`. LATAM / warmth accent, deeper. Final stop in the gold gradient.
- **Danger Red** — `#DC2828` · HSL `0 72% 51%` · token `--danger-red` · Tailwind `bg-danger-red`. Error states only.

Surfaces / semantic tokens (`puente-ai-brand-guide.pdf` §3):

- Light mode: `--background` `#F7F5F1` (warm cream), `--foreground` `#0E1629` (near-black ink), `--card` `#FDFCFB`, `--muted` `#F0EEE9`, `--muted-foreground` `#6A717F`, `--border` `#E5E1DA`.
- Dark mode: `--background` `#0C1116`, `--foreground` `#F8F9FA`, `--card` `#111821`, `--muted` `#1A222C`, `--muted-foreground` `#7B899D`, `--border` `#242C37`, `--primary` `#FABB1E` (slightly brighter gold for dark surfaces), `--sidebar-background` `#111721`.

Brand gradients and effects (`puente-ai-brand-guide.pdf` §4):

- `text-gradient-gold` — gold gradient for hero headlines, linear 135°: gold-light → gold → amber-orange.
- `bg-gradient-gold` — 135° gold fill for logo, premium CTAs, brand icons.
- `bg-gradient-navy` — subtle vertical fade `background → card`.
- `glow-gold` — gold box-shadow 30/60px for hover on cards and CTAs.
- `glass` — glassmorphism: backdrop-blur-xl + `bg-card/80` + border-bottom.

Usage map by context (`puente-ai-brand-guide.pdf` §7):

- Primary CTAs: `bg-primary` (gold) over navy or cream.
- Sidebar / fixed nav: `bg-sidebar` (navy).
- Savings figures: `text-emerald`, 56px bold — unbreakable rule.
- Success states (`compliance ✓`, `routed ✓`): emerald.
- Processing states: navy with `pill-pulse`.
- Errors: `bg-danger-red`.
- LATAM / warmth accents: `warm-amber` / `amber-orange`.
- Trust signals (footer): `text-muted-foreground` + subtle icons.

### Typography (authoritative — `puente-ai-brand-guide.pdf` §1 + BRAND.md §1)

- **Headings (H1–H6) — Funnel Display**, weights 300–800. Token `font-display`.
- **Body / UI — DM Sans**, weights 400, 500, 600, 700. Default on `<body>`. Token `font-body`.
- **Savings figures — DM Sans 700, 56px, color emerald.** Product rule, never override.
- Both families load from Google Fonts in `src/index.css`.
- Hard rule: never mix in a third family. If a piece needs accent, use weight or size within Funnel Display + DM Sans.
- Numerals are tabular when they appear in data viz.

(Note: `DESIGN.md` §4 names "Plus Jakarta Sans / Inter" as legacy placeholders. The brand guide PDF + `src/index.css` are the source of truth — Funnel Display + DM Sans is what actually ships. Use those.)

### Logo (`puente-ai-brand-guide.pdf` §10 equivalent — drawn from BRAND.md §10)

- Mark: abstract bridge-arc forming a stylized "P".
- Wordmark: `PUENTE AI` in Funnel Display Bold, tracking-tight.
- On dark backgrounds: white logo asset masked with `bg-gradient-gold`.
- On light backgrounds: color logo asset directly.
- Minimum clear space: equal to the height of the "P" mark on all sides.

### Composition

Composition leans on negative space and the diagonal. *"The diagonal is sacred here — it is the line of transit, the corridor between nations, the angle at which light catches a bridge cable at dawn"* (`puente-linkedin-philosophy.md` §I). One focal element per image. Document-as-hero is the default move: an invoice corner, a customs stamp, a redacted line item, a packing-list grid, the texture of trade. Avoid layouts that put a person's face at the center unless the post is specifically a founder portrait.

Geometric elements — circles, nodes, connecting lines, dot grids, thin luminous pathways — are encouraged when they echo the topology of trade networks. They must be deployed with restraint, "with the precision of astronomical charts" (`puente-linkedin-philosophy.md` §III). Nothing random. No decoration for decoration's sake.

### Photography

When used, photography lives in real working environments. Miami warehouses, Doral logistics offices, Port of Miami, Laredo border crossings, Santo Domingo back-offices. Diverse subjects reflecting actual SME owners and brokers — Latina women business owners, Latino brokers, mixed Anglo/Latino teams. Working hands, working desks, real documents on real surfaces. Avoid stock business-people, fake smiling, glossy lifestyle imagery, and conference-room cliché.

### Illustration

Illustration is line-based and monoline. Document-forward. Restraint over playfulness (`puente-linkedin-philosophy.md` §V — "the craft of invisible labor"). *The Economist* or *FT Weekend* editorial illustration is the reference. Avoid 3D isometric scenes, bouncy 3D character mascots, and corporate Memphis (squiggles, tossed shapes, primary-color confetti).

### Data visualization

Clean and minimal. One comparison per chart. Routing-vs-baseline savings should appear as a simple paired bar (wire vs. stablecoin) with the dollar savings called out in `text-emerald` and the baseline labeled — never an unlabeled "save 80%" claim. Always disclose the baseline (typically a 5% wire fee). Always show units. Tabular numerals.

### Shape system (`puente-ai-brand-guide.pdf` §5)

- `--radius` — `0.75rem` (12px), base radius for cards and buttons.
- `radius-md` — `calc(var(--radius) - 2px)`.
- `radius-sm` — `calc(var(--radius) - 4px)`.

### Bilingual layout

When copy appears in an image, design must accommodate Spanish strings that run roughly 25% longer than the English equivalent. Do not crop the Spanish to fit an English-sized box. Do not shrink the Spanish font to make it fit. Either re-flow the layout or trim the English so both languages breathe.

### Explicitly off-brand

A third typeface beyond Funnel Display + DM Sans. Raw hex values used directly in components instead of semantic tokens. Demoting the savings figure below 56px or out of emerald. Using emerald as a background. Neon accents. 3D character mascots. Dollar-sign rain. Hand-drawn doodle aesthetic. Dark-isometric-tech-bro grids. Generic stock business-people. Conference-room handshakes. "Blockchain glow" imagery. Crypto-bro candle charts. AI-art uncanny-valley faces. Corporate Memphis (squiggles, tossed shapes, primary-color confetti). Anything that competes with the navy-and-gold meridian.

When in doubt: how would *The Economist* illustrate this if they covered LatAm trade fintech, with a navy-and-gold palette and a savings number in emerald? Default to that.

---

## How to use this

Copy Section 1 into the Brand Brief tab. Copy Section 2 into the Writing Style tab. Copy Section 3 into the Image Style tab. Set Adaptive Writing Style to OFF — the explicit guidance here should override post-history learning, especially while the post corpus is small and uneven. Set Image Style to Custom (none of the presets fully fit a US–LATAM fintech-trade brand). Re-run this profile after major positioning shifts: when KAN-22 yields written-permission customer quotes, when V2 settlement actually ships, or whenever the locked one-liner moves.
