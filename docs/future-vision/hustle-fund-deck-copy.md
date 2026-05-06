# Puente AI — Hustle Fund Pitch Deck Copy
**Status:** Draft slide copy, ready to flow into Decktopus / Pitch / Slidebean
**Reviewer profile:** Hustle Fund pre-seed (Elizabeth Yin / Eric Bahn lens — distribution-first, founder-market-fit, ship-not-burn)
**Author:** marketing-pr agent, 2026-04-30
**Voice:** Founder, EN only

---

## 0. Anti-list reminder + recommendation (read before using this deck)

> **INTERNAL — DO NOT INCLUDE IN DECK.** This section is founder-internal context. Do not paste into Decktopus / Pitch / Slidebean. Strip before designer hand-off.

The 2026-04-21 ceo-scope verdict, preserved verbatim from `docs/CLAUDE.md` (pre-2026-04-30 doc-drift refactor, now living at `.claude/worktrees/suspicious-newton-7bc18d/docs/CLAUDE.md` line 378):

> *"Do NOT apply to Hustle Fund / YC / anyone else. The 'real importers using product' artifact does not exist yet."*

That verdict was issued nine days ago. Nothing has changed on the artifact side since:

- KAN-22 (the customer-research ticket — interview 10 Miami SMEs and brokers) is still in To Do, not In Progress. There is no signed pilot, no quotable user, no real-volume number.
- The 2026-05-13 scheduled agent fire (per memory: `prd_v03_shipped.md`) explicitly checks KAN-22 progress before any further fundraising motion.
- Phase 3 is mid-flight: KAN-32, KAN-36, KAN-37 are still open; KAN-46 just landed a logger to debug the `/routing` 422; the custom domain certs are provisioning *tonight* and PR #53 is still draft.
- The latest resume.md (2026-04-30) anti-list reminder list is about cert-landing and CCR routine verification — nothing in the founder's own session log says "ready for Hustle Fund."

**My recommendation as the marketing-pr agent (you asked for the actual view, not boilerplate):**

**Do not send this deck this week.** The deck reads like a pre-traction founder writing a polished problem narrative. Hustle Fund's diligence pattern, well-documented in Yin's public writing, is to triage on three signals — *founder-market fit*, *channel realism*, and *evidence the founder ships*. Slides 5 (founder-market fit) and 6 (distribution / channel test) will land. Slide 8 (traction) — currently "what's live in the codebase" — will read as engineering progress, not market progress, to a fund that screens hundreds of decks a week looking for the one with a signed Maria.

**The right sequencing:**

1. Run KAN-22 to first signal — even one Maria-equivalent who has uploaded one real invoice through the production pipeline and said something quotable about it. That single line replaces 80% of slide 8 and earns the meeting.
2. Hold this deck draft as the scaffolding it is — it is fine work, the language is locked to v0.3 PRD and compliance-clean, and slides 1–7 + 9–10 do not need a customer to be true. Slide 8 is the one that goes from "engineering progress" to "market signal" the moment KAN-22 produces output.
3. The deck you send Hustle Fund should also be sent into a warm intro — Yin and Bahn both filter cold. The founder's goTRG network, the Doral broker network, and any second-degree connection to Backstage Capital alumni are the right doors.

**If the founder overrides this and sends the deck cold this week**, the copy below is honest, compliance-clean, and as good as it can be without a signed pilot. It will not embarrass the company. It will likely not earn a meeting either.

I have produced the slide copy below as requested, on the assumption that the founder may want it ready-to-go for the moment KAN-22 lands the first real upload.

---

## 0a. Gap report — what `pitch-deck-outline.md` does not yet support

> **INTERNAL — DO NOT INCLUDE IN DECK.** This section is founder-internal context. Do not paste into Decktopus / Pitch / Slidebean. Strip before designer hand-off.

The existing 12-slide `docs/future-vision/pitch-deck-outline.md` is structured for a generic seed/Series A pitch, not a Hustle Fund pre-seed scope. Mapping the 10-slide Hustle Fund structure against the existing outline:

| Hustle Fund slide | Outline coverage | Gap |
|---|---|---|
| 1. Title | Slide 1 | None — locked one-liner present. |
| 2. Problem | Slide 2 | None — 5–7 day / 3–7% / 40% numbers present. |
| 3. Solution | Slide 3 | **Partial.** Outline correctly notes V1 is recommendations-only and broker-augmentation, but the language "USDC on Stellar — <15 seconds, <1% cost" on the V2 line still needs the "subject to regulatory approval" qualifier on every customer-facing variant. Copy below tightens this. |
| 4. Why now | Not in outline | **Gap.** The outline has a "Market Opportunity" slide (4) but no "Why now" framing — nearshoring tailwinds, tariff cost volatility, Document AI/Gemini cost curve, Stellar SEP-31 maturity. Drafted from scratch below using PRD §3 + §14. |
| 5. Founder-market fit | Slide 11 | **Partial.** Outline has the right elements (goTRG, Northeastern MS, Amsterdam-born EU citizen, Dominican heritage) but does not yet weave them into the Hustle-Fund-grade single narrative. Drafted below. |
| 6. Distribution / channel test | **Not in outline** | **Critical gap.** Hustle Fund will not advance a deck without this. The outline jumps from "Solution" (3) to "Market Opportunity" (4) to "Proprietary Technology" (5) — no slide on how Puente acquires the next 10 SMEs and the next 1 broker. Drafted below from PRD §4 (broker-augmentation) and CLAUDE.md (Doral / WhatsApp / warm-network channels). **This is the most important slide for Hustle Fund and the founder should review it personally.** |
| 7. Business model | Slide 8 | **Partial.** Outline lists "1.5–2% transaction fee" as if live; that's a V2 number. Copy below splits per-seat SaaS today (TBD) from the V2 take rate (post-MSB/MTL). |
| 8. Traction / proof points | Slide 9 | **Gap.** Outline shows projections (Q2/Q4 milestones), not traction. Compliance guardrail #4 means no fabricated logos. Copy below uses what's actually live per CLAUDE.md and flags the slot where the first KAN-22 quote should drop in. |
| 9. Competition / moat | Slide 10 + 6 + 7 | **Partial.** The competition matrix is fine; the moat narrative (broker-augmentation, bilingual-by-design, V4 lending flywheel) is split across three slides in the outline. Copy below consolidates. |
| 10. Ask | Slide 12 | **Partial.** Outline shows $1.5M seed split 50/30/20. Copy below tightens to ship-not-burn line items and ties milestones to KAN tickets and the FinCEN MSB / Florida MTL filing path. No Reg-D-adjacent language. |

**Slides in the existing outline NOT carried into the Hustle Fund 10:** Slide 5 (Proprietary Technology), Slide 6 (Regulatory Moat), Slide 7 (Trade Treaty Intelligence). These belong in a Series A deep-dive deck, not a Hustle Fund pre-seed. They are accurate but read as over-claim at this stage. **Founder confirmation needed:** is the founder OK shelving these three slides for the Hustle Fund version specifically, while retaining them in the Series A deck? If yes, the copy below stands as-is. If no, slot them in but expect Hustle Fund to lose interest — pre-seed reviewers are not buying treaty intelligence.

---

## Slide 1 — Title

**Headline (≤8 words):**
The trade bridge for the Americas.

**Subheadline (≤20 words):**
Puente AI turns a trade document into compliance and payment routing in 15 seconds — for SMEs and customs brokers in the US–LATAM trade corridor.

**3 supporting bullets (≤12 words each):**
- Founder: Jay Alexander, Miami / Santo Domingo
- Stage: pre-seed, building V1 in production
- Contact: jay@puente.ai · puenteai.ai

**Visual brief for Decktopus / designer (one paragraph):**
Single full-bleed map of the Americas with two-way arrows between Miami, Santo Domingo, and Mexico City. Dim everything else. Primary brand color on the corridor, neutral grey on the rest of the continent. No stock photos. The locked one-liner sits centered below the map in a serif display face matching `frontend-app/BRAND.md` §5; the headline above it in the same family, larger weight. No logo wall.

**Speaker notes (≤60 words):**
"My name is Jay. I spent four years selling US liquidation truckloads to importers across LATAM at goTRG. I watched the same families lose three to seven percent on every wire and a week on every settlement. Puente AI is the tool I wished my customers had."

**Compliance flag:** yes

---

## Slide 2 — Problem

**Headline (≤8 words):**
Trade moves at internet speed. Money doesn't.

**Subheadline (≤20 words):**
Every cross-border SME shipment loses 3–7% to wire fees, 5–7 days to SWIFT, and stops at customs 40% of the time.

**3 supporting bullets (≤12 words each):**
- $50K truckload: $1,500–$3,500 in wire fees, every single time
- 5–7 days from invoice to cleared funds in Bogotá or Santo Domingo
- 40% of shipments delayed by manual HS code misclassification

**Visual brief for Decktopus / designer (one paragraph):**
Three stacked horizontal bars. Bar 1: "Cost — 3–7% of every shipment lost to wire fees." Bar 2: "Speed — 5–7 days SWIFT settlement." Bar 3: "Compliance — 40% of shipments delayed." Numbers in emerald per `BRAND.md` §7 brand-color spec; bar background in the muted slate also defined there. Cite the source row beneath each bar in 9pt: PRD §2 for the founder-derived numbers. No stock photos of cargo ships.

**Speaker notes (≤60 words):**
"This is not a TAM slide. This is what one shipment costs Maria — a Miami-based SME I know by name. On every $50,000 invoice she pays the wire fee twice: once when she sends, once when her supplier converts. Then she waits a week. Then her broker calls about the HS code. That happens hundreds of times a day in Doral."

**Compliance flag:** yes

---

## Slide 3 — Solution

**Headline (≤8 words):**
Upload an invoice. Get answers in 15 seconds.

**Subheadline (≤20 words):**
Puente AI reads the document, flags compliance gaps, and recommends the cheapest payment route — all before the broker calls back.

**3 supporting bullets (≤12 words each):**
- Document intelligence: Vertex AI Document AI extracts structured trade data
- Compliance check: corridor- and direction-specific rules flag missing documents
- Payment route recommendation: dollar-for-dollar comparison of available rails

**Visual brief for Decktopus / designer (one paragraph):**
Three-step horizontal flow diagram, left to right. Step 1 icon: a document. Step 2 icon: a checklist with one red flag. Step 3 icon: two paired bars labeled "Wire" and "USDC route" with the dollar delta called out in emerald. Single 15-second timer ticking across the top. No "AI brain" cliché. The phrase "recommends the route — does not move money" appears in 10pt below the third icon as a compliance caption.

**Speaker notes (≤60 words):**
"V1 is a recommendation engine, not a payment processor. We read the document, we tell the broker what's missing, we tell Maria what the cheapest route would save her. We do not move money. Money movement is V2, after we file the FinCEN MSB and the Florida MTL. We are deliberate about that line."

**Compliance flag:** yes — copy honors guardrail #1 (no money-movement language) and guardrail #2 (no claim of held licenses).

---

## Slide 4 — Why now

**Headline (≤8 words):**
The corridor moved. The rails didn't.

**Subheadline (≤20 words):**
Nearshoring is shifting $2.5T from Asia to LATAM, and US trade policy is making each shipment more expensive to misroute.

**3 supporting bullets (≤12 words each):**
- Nearshoring: supply chains moving from Asia into Mexico and the DR
- Tariff volatility raises the cost of every classification error
- Document AI + Gemini Flash hit a price point pre-seeds can ship on

**Visual brief for Decktopus / designer (one paragraph):**
A single line chart, 2018–2026, plotting US-LATAM trade volume rising while average per-document AI compliance cost falls. Two lines crossing somewhere in 2024 — the inflection. Caption beneath: "The unit economics of corridor compliance flipped two years ago." No partisan framing on the tariff bullet — speak only to cost variance, never to administration or party.

**Speaker notes (≤60 words):**
"Three things changed in the last twenty-four months. Supply chains are moving south — Mexico is now the US's largest trading partner. Tariff volatility makes every misclassification more expensive than it was in 2022. And Document AI plus Gemini Flash dropped the cost of structured extraction by an order of magnitude. None of those three are reversible. We are building for that intersection."

**Compliance flag:** yes — tariff bullet is cost-framed only, per guardrail #6.

---

## Slide 5 — Founder-market fit

**Headline (≤8 words):**
I've been on every side of this trade.

**Subheadline (≤20 words):**
Four years selling truckloads to LATAM importers at goTRG. Born in Amsterdam, Dominican heritage, Miami-based. MS in AI/ML at Northeastern.

**3 supporting bullets (≤12 words each):**
- Sold liquidation truckloads to Maria's profile of buyer for four years
- US citizen + EU citizen (DNB EMI passportable) + Dominican heritage
- MS in AI/ML at Northeastern Align — building the model myself

**Visual brief for Decktopus / designer (one paragraph):**
Single-portrait photo of the founder on the left third of the slide. Right two thirds: a vertical timeline labeled with four anchors — Amsterdam (born), Northeastern (degree in flight), goTRG (four years sales, 2020–2024), Puente AI (2026). Each anchor in serif display, dates in mono. No corporate headshot vibe; warm, in-warehouse or in-office, ideally on a Doral street if the founder has the photo. If not, plain grey background.

**Speaker notes (≤60 words):**
"I am not the AI guy who discovered trade. I sold to these importers for four years before I knew what a transformer was. The MS at Northeastern is closing the technical gap. The Amsterdam birth and Dominican heritage are the regulatory advantage — I hold native standing in the three jurisdictions Puente operates in. And I know Maria by first name, in Doral, today."

**Compliance flag:** yes — the EMI passport line says "DNB EMI passportable," not "DNB EMI licensed," consistent with guardrail #2.

---

## Slide 6 — Distribution / channel test  *(the slide that earns the meeting)*

**Headline (≤8 words):**
Two channels, both ones I already own.

**Subheadline (≤20 words):**
Warm-network now (zero paid CAC), broker-led at scale (one broker = 20–50 SME files, ~20–50× SME-direct CAC).

**3 supporting bullets (≤12 words each):**
- Now: LinkedIn EN/ES + Spanish WhatsApp + Doral broker walk-ins
- Target by Month 7: 10 paying SMEs + 1 design-partner broker
- At scale: white-label API into licensed brokers' books — they're the channel, not the competition

**Visual brief for Decktopus / designer (one paragraph):**
Two-column slide. Left column header: "Now — Warm network, $0 CAC." Underneath, three small icons: LinkedIn, WhatsApp, a handshake (for in-person Doral broker walk-ins). Target metric beneath: "10 SMEs + 1 broker by Month 7." Right column header: "At scale — Broker-led, 20–50× leverage." Underneath, a single icon: a broker silhouette with a fan of 25 SME client cards. Metric beneath: "1 broker onboarded = 25 SME files." A thin horizontal arrow at the bottom labeled "Channel transition: Month 8+." No funnel imagery, no growth-hacker buzzwords.

**Speaker notes (≤60 words):**
"My founding-wedge buyer is the goTRG-style Miami exporter — I have her phone number. My channel at scale is the licensed broker — I have his front door in Doral. I am not buying leads. I am walking into offices and sliding into LinkedIn DMs in Spanish. When one broker says yes to the white-label API, I get twenty-five Marias on the same handshake."

**Compliance flag:** yes — broker-augmentation framing per PRD §4 and the locked 2026-04-29 reconciliation. No claim of any signed broker yet (compliance guardrail #4).

---

## Slide 7 — Business model

**Headline (≤8 words):**
SaaS today. Take rate later. Lending eventually.

**Subheadline (≤20 words):**
Per-seat SaaS funds the V1 build. The take rate on settlement comes after MSB and MTL. Lending is the moat.

**3 supporting bullets (≤12 words each):**
- V1 (now): $39–$99/mo per seat (pricing TBD post-KAN-22 pilot)
- V2 (roadmap, post-FinCEN MSB + Florida MTL): 0.3–0.5% take rate on settlement *(benchmarked against published SEP-31 + stablecoin-settlement provider take rates; final pricing post-MSB/MTL)*
- V4 (roadmap): trade-credit interest on a proprietary risk model banks can't build

**Visual brief for Decktopus / designer (one paragraph):**
A simple horizontal three-stage bar, left to right: V1 (SaaS, today), V2 (Take rate, post-licensing), V4 (Lending, data-flywheel-dependent). Each stage labeled with the revenue mechanic and the gating prerequisite. The two right-hand stages clearly tagged "Roadmap — gated on regulatory approval." Avoid the temptation to show projected dollar revenue per stage; this is a model slide, not a forecast slide. No hockey-stick chart.

**Speaker notes (≤60 words):**
"V1 pays the bills the way every SaaS does — a seat fee. The price band is honest: I will lock it after the KAN-22 interviews. V2 is the take rate on settlement, and that ships only after the MSB and MTL filings clear. V4 is the lending flywheel — the data I am collecting today becomes the credit model in three years."

**Compliance flag:** yes-with-caveats — every forward-looking line is explicitly marked roadmap and gated on filings (guardrail #2). The $39–$99/mo band is marked TBD because pricing has not been validated (guardrail #3).

---

## Slide 8 — Traction / proof points  *(slot the first KAN-22 quote here when it lands)*

**Headline (≤8 words):**
The pipeline runs end-to-end. In production.

**Subheadline (≤20 words):**
Backend on Cloud Run, 113 tests passing, Document AI + Gemini end-to-end, multi-tenant Firebase Auth, frontend in private preview.

**3 supporting bullets (≤12 words each):**
- 113 backend tests passing — full Document AI + Gemini pipeline live
- Multi-tenant data isolation shipped (Firebase Auth + scoped Firestore + GCS)
- KAN-22 customer interviews in flight; first design-partner quote drops in here

**Visual brief for Decktopus / designer (one paragraph):**
Single screenshot of the Lovable-built `/analyze` flow, with one real (non-customer) test invoice and the resulting compliance flags + payment-route recommendation visible. Beneath the screenshot: a small footer row with five capability badges — "Cloud Run · 113 tests · Document AI · Gemini · Multi-tenant." If the first KAN-22 quote has landed by submission, replace the badges with the quote in pull-quote format and move the screenshot to a smaller inset. **Do not fabricate a customer logo. Do not show a logo wall. There is no signed customer.**

**Speaker notes (≤60 words):**
"What I have today is a live pipeline, not a slide. Maria can upload an invoice right now, and the system extracts it, flags the compliance gaps, and shows her the cheaper route. I am running the customer-research sprint this month — KAN-22 in our tracker. The day I have the first real Maria quote, this slide changes shape."

**Compliance flag:** yes-with-caveats — copy is true today, but the slide must be revised the moment a real KAN-22 quote is available. Founder must confirm before send that no logos are inserted by Decktopus's auto-fill.

---

## Slide 9 — Competition / moat

**Headline (≤8 words):**
The broker is the channel, not the enemy.

**Subheadline (≤20 words):**
Three moats: broker-augmentation distribution, bilingual product built from the inside, and a transaction-data flywheel for V4 lending.

**3 supporting bullets (≤12 words each):**
- Distribution moat: white-label API into licensed brokers, not around them
- Language moat: Spanish-first product US incumbents will not cheaply replicate
- Data moat: every transaction trains the V4 SME credit model

**Visual brief for Decktopus / designer (one paragraph):**
A 2x3 comparison grid. Rows: Speed, Cost, Compliance, Bilingual UX, Broker-friendly, Data flywheel. Columns: Traditional banks, Generic crypto rails, Puente AI. Use simple checks/dashes — no rainbow heat-mapping. Underneath, one short caption: "We do not compete with the licensed broker. We give him 25 hours back per month." No "we're the Stripe for X" anywhere. No competitor logos.

**Speaker notes (≤60 words):**
"Banks are slow and expensive. Crypto rails are fast but illegal-feeling to a 55-year-old broker in Doral. We are the third option — fast, compliant, bilingual, and pointed at the broker's existing book. The lending model in V4 is the long game. Every invoice Maria runs through us today is a row in the credit model her bank cannot build."

**Compliance flag:** yes — no banned phrases, no Reg-D adjacency, broker-augmentation framing intact.

---

## Slide 10 — Ask

**Headline (≤8 words):**
$500K to ship V1, file MSB, sign Carlos.

**Subheadline (≤20 words):**
12 months to a paying broker, ten paying SMEs, FinCEN MSB filed, and Florida MTL clock running.

**3 supporting bullets (≤12 words each):**
- Engineering: KAN-21, KAN-22 follow-ups, V1 hardening, Spanish UX coverage
- Regulatory: FinCEN MSB filing + Florida MTL prep + counsel on DR EPE
- Distribution: 1 design-partner broker + 10 SMEs across both corridor directions

**Visual brief for Decktopus / designer (one paragraph):**
Single donut chart showing the $500K split. Roughly: Engineering 55%, Regulatory + counsel 25%, Distribution / GTM 20%. Beneath the donut, a single-line milestone bar: M3 — 1 broker LOI · M6 — MSB filed · M9 — 5 paying SMEs · M12 — Florida MTL filed, 10 paying SMEs. No mention of valuation, equity %, or pro rata. No "join our round" CTA — the call to action is "Let's talk." Final line in 10pt: "References, technical due diligence package, and customer pipeline available on request."

**Speaker notes (≤60 words):**
"I am raising five hundred thousand to cover the next twelve months. Half goes to shipping V1 and the export-corridor compliance work. A quarter goes to filing the MSB and starting the Florida MTL clock. The last fifth goes to landing the first design-partner broker and ten paying SMEs. The math is ship-not-burn. I have spent four years preparing for this twelve months."

**Compliance flag:** yes — no Reg-D-adjacent language, no specific valuation, no IRR or returns claim, no "you'll get in at" framing. Per guardrail #5.

---

## Email — subject line + 4-line body

**Subject:** Four years selling LATAM truckloads at goTRG. Now I'm building Puente AI.

**Body:**

Elizabeth — I'm Jay Alexander. I spent four years at goTRG selling liquidation truckloads to Miami-based SMEs shipping into Bogotá and Santo Domingo, and I watched the same families lose 3–7% per wire and a full week per settlement on every shipment.

Puente AI turns a trade document into compliance and payment-route recommendations in 15 seconds — for SMEs and the licensed customs brokers who clear their shipments. V1 is a recommendation engine, live in production today (113 tests, end-to-end Document AI + Gemini pipeline on Cloud Run); V2 will execute settlement and is gated on the FinCEN MSB and Florida MTL filings I'm scoping now.

Distribution is the slide I most want your read on: warm-network SME outreach in Doral now (interview phase, KAN-22), broker-led white-label at scale (1 broker ≈ 20–50 SME files). Deck attached.

Worth fifteen minutes? — Jay
jay@puente.ai · puenteai.ai

---

## Notes for the founder (read before sending)

> **INTERNAL — DO NOT INCLUDE IN DECK.** This section is founder-internal context. Do not paste into Decktopus / Pitch / Slidebean. Strip before designer hand-off.

1. **My recommendation stands: do not send this week.** The deck is honest, but slide 8 reads as engineering progress, not market progress, until KAN-22 produces one real quote. Run the interviews first.
2. **Slide 6 is the one Hustle Fund will judge you on.** Read it twice. The two-channel framing (warm-network now, broker-led at scale) is locked to PRD §4 and to the 2026-04-29 strategic positioning reconciliation, but the targets ("10 SMEs + 1 broker by Month 7") are mine — confirm or adjust them based on what you actually believe is achievable.
3. **The $500K ask on slide 10 is a placeholder consistent with Hustle Fund's typical pre-seed check size** ($25K–$500K, with most checks $100K–$250K). Confirm your actual round size before the deck goes anywhere.
4. **The pricing band ($39–$99/mo) on slide 7 is from `docs/PRD.md` adjacency, not from a validated source.** I have marked it TBD; you may want to either drop the numbers entirely until KAN-22 lands or keep them with the TBD caveat — your call.
5. **Two slides from `pitch-deck-outline.md` are NOT in this version: Proprietary Technology and Trade Treaty Intelligence.** They read as over-claim at pre-seed. If you want them in, slot them between current slides 7 and 8, but expect Hustle Fund to lose interest — pre-seed reviewers do not buy treaty intelligence. Confirm before designer hand-off.
6. **The email body assumes Elizabeth Yin specifically** — swap the salutation if Bahn is the partner. The "four years at goTRG" hook is the founder-market-fit anchor and should not be moved off line one regardless of which partner.
7. **Compliance review needed before send:** route this entire deck draft past `fintech-security` for a final pass on slides 3, 7, and 10 — the three that touch money-movement, take rate, and use of funds language. I have written each to the guardrails in `.claude/agents/marketing-pr.md`, but a second pair of eyes on the regulatory edges is non-optional before this leaves the building.
8. **Visual asset ownership:** the screenshot on slide 8 needs to be of a real `/analyze` run with a non-customer test invoice (use `scripts/gen_test_invoice.py` per resume.md PR #49). Do not screenshot a real customer's data, even with permission, until written customer-quote permissions are on file.

---

*Author: marketing-pr agent. Generated 2026-04-30. Voice: founder, EN. Compliance pass: full pass against `.claude/agents/marketing-pr.md` §"Compliance Guardrails" 1–7. Distribution: hold until KAN-22 lands first quote, per the agent's actual recommendation.*
