# Puente AI — Go-To-Market Scope

**Document type:** Scope brief (not the executed strategy).
**Author:** Senior Marketing & Communications Lead.
**Date:** 2026-05-05.
**Aligned to:** PRD v0.3 (`docs/PRD.md`, locked 2026-04-29), `docs/CLAUDE.md` invariants, `docs/future-vision/dual-engine-architecture.md`, `docs/future-vision/hustle-fund-deck-copy.md`, `docs/marketing/website-copy-refresh-2026-04-29.md`, `frontend-app/BRAND.md`.
**Recipient:** marketing collaborator picking up GTM execution.
**Status:** Founder-review draft. Read end-to-end before scoping work.

---

## 0. How to read this doc

This is a **scope** document — what we will go to market with, to whom, why now, through which channels, in which sequence, and how we will know it worked. It is not the campaign plan and it is not the creative. The collaborator inheriting this should be able to read it once and know exactly what they are signing up to build, where the lines are around regulated claims, and what is explicitly off the table for V1.

If anything in this scope conflicts with `docs/PRD.md` or `docs/CLAUDE.md`, those documents win and this one is wrong. Flag the conflict back to the founder before building from it.

---

## 1. Context & Why Now

Puente AI is a pre-seed fintech operating in the US–LATAM trade corridor — a $2.5T annual flow where SMEs and licensed customs brokers move goods in both directions and lose 3–7% per shipment to wire fees, 5–7 days to SWIFT settlement, and an estimated 40% of shipments to manual HS code misclassification (PRD §2, §3).

Three structural shifts make the next twelve months the right window:

- **Nearshoring tailwinds.** Supply chains are migrating from Asia to Mexico and the Caribbean basin. Mexico is now the US's largest trading partner. The Dominican Republic sits at the intersection of DR-CAFTA, EU-CARIFORUM, and Mercosur (in active negotiation) — a uniquely positioned hub. PRD §3, §14.
- **Tariff cost variance.** US trade policy is making each shipment more expensive to misroute. We frame this as a cost-volatility tailwind only — never partisan. PRD §15 and the marketing-pr compliance guardrails.
- **AI cost curve.** Document AI plus Gemini Flash dropped the cost of structured trade-document extraction by an order of magnitude in the last 24 months. Pre-seed teams can now ship the compliance layer that would have required a Series B in 2022. Confirmed by the live Cloud Run pipeline, 113 backend tests passing (CLAUDE.md "Current Build Status").

**What is actually live today** (per `docs/CLAUDE.md`, do not exaggerate):

- FastAPI backend on GCP Cloud Run; multi-tenant Firebase Auth / scoped Firestore + GCS isolation; 113 tests passing.
- End-to-end pipeline: upload → Document AI extraction → Gemini analysis → compliance check → payment-route recommendation, in roughly 15 seconds.
- Vite + React frontend in `frontend-app/`, deployed to Cloud Run service `puente-frontend`. Bilingual EN/ES via `src/lib/i18n.tsx`.

**What is NOT yet live** (do not market V2 capabilities as available):

- Real stablecoin payment execution. V1 *recommends*; V2 will *settle*.
- FinCEN MSB registration, Florida MTL, BCRD EPE — all on the punch-list, none filed.
- Signed pilot customers. KAN-22 customer-interview phase is in flight; no quotable user yet.
- HS code production-grade classification accuracy.

This GTM is therefore aimed at **earning the first signed pilot and the first design-partner broker**, not at scaling acquisition.

---

## 2. Ideal Customer Profile (ICP) — both sides of the corridor

We sell into one shipment, two co-equal users. PRD §4, locked 2026-04-29.

### 2.1 Maria — primary SME persona

- Miami-based bilingual (EN/ES) SME owner, age 35–55, born in Colombia, Venezuela, the Dominican Republic, or Mexico.
- Manages $500K–$5M per year in cross-border trade volume.
- **Founding-wedge profile:** US→LATAM exporter — buys US liquidation truckloads from goTRG, B-Stock, Direct Liquidation; ships to resellers in Bogotá, Caracas, Lima, Santo Domingo. The founder spent four years selling into this exact buyer at goTRG.
- **Inverse flow served too:** LATAM→US importer bringing produce, manufactured goods, raw materials into the US. Same upload, same compliance check, same payment recommendation; only the importer of record changes.
- Lives on WhatsApp and runs the business from a phone in a warehouse.
- Pain: wire fees, slow settlement, customs complexity, unknown landed cost.

### 2.2 Carlos — co-equal broker persona

- Licensed US customs broker or freight forwarder, based in Miami / Doral or one of the US-Mexico land-border crossings (Laredo, El Paso, McAllen, San Diego).
- Manages 20–50 active SME client files across both corridor directions.
- Spends roughly 40% of working hours on routine document review and HS code classification.
- Pays for tools that automate routine work and white-label cleanly to his importer/exporter clients.

**Distribution implication:** Carlos is the channel, not the competition. One signed broker = 20–50 SME files on the same handshake. PRD §4 and the 2026-04-29 reconciliation lock this as **broker-augmentation, not broker-replacement**. Every customer-facing asset must read this way.

### 2.3 Out-of-scope segments for V1 GTM

- Enterprise importers above $50M annual trade volume — different buying motion, different compliance footprint, different sales cycle.
- Brazil and Argentina corridors. Brazil is Phase 5 (PRD §11, SISCOMEX/RADAR work). Argentina has no near-term wedge.
- Crypto-native traders. We do not lead with stablecoin language to a degen audience; the audience is bank-banked SMEs and licensed brokers.
- Consumer remittances. We are not a Wise or a Remitly.

---

## 3. Positioning

### 3.1 Locked one-liner (use verbatim)

> *Puente AI turns a trade document into compliance and payment routing in 15 seconds — for SMEs and customs brokers in the US–LATAM trade corridor.*

This line lives in PRD §1 and is locked as of the 2026-04-29 v0.3 reconciliation. Do not paraphrase in customer-facing copy. The hero on www.puenteai.ai uses this verbatim. Press releases use this verbatim. Email subject lines and social hooks may derive a tighter beat from it, but the full sentence appears in the body.

### 3.2 Tagline (locked)

> *Pay less. Move faster.*

From `frontend-app/BRAND.md` §9. Use in image overlays, deck title slides, conference banners, signature lines.

### 3.3 V1 honesty — non-negotiable

V1 is a **recommendations layer**. We read the document, score risk, flag compliance gaps, and recommend the cheapest legal payment route. **We do not move money.** Banned phrases in customer-facing copy: *send money, settle payments, transfer funds, wire money to your supplier, pay your supplier through Puente.* Acceptable phrases: *show you the cheapest route, compare wire vs. stablecoin in dollar savings, recommend how to settle this invoice.* See `marketing-pr` agent compliance guardrails 1–7.

### 3.4 What we are NOT

- Not a bank.
- Not a money transmitter.
- Not a broker-replacement.
- Not a crypto exchange.
- Not a remittance app.

`BRAND.md` §9 — keep this list visible to anyone writing copy.

### 3.5 KAN-21 / KAN-22 gate

Two product-side gates the marketing collaborator must respect:

- **KAN-22** — customer-interview phase. Until KAN-22 yields at least one written-permission quote, no fabricated testimonials, no logo walls, no implied customer counts. The current site testimonials carousel is under review; see `docs/marketing/website-copy-refresh-2026-04-29.md` §6.
- **KAN-21** — un-parked but gated on KAN-22. Builds the US→LATAM export-direction compliance rules (EAR, BIS, DR-CAFTA Certificate of Origin). Until it ships, do not promise direction-specific export-compliance features in copy.

---

## 4. Channel Mix & Sequencing

Two-channel strategy, anchored to where the audience already lives. No paid acquisition in V1 — every dollar that would have gone to ads goes to KAN-22 interview travel and broker walk-ins.

### 4.1 Now — Warm network, $0 CAC

| Channel | Audience | Asset cadence | Voice |
|---|---|---|---|
| **LinkedIn** (founder + brand) | B2B fintech, broker community, investor-adjacent | 2 founder-voice + 1 brand-voice per week | Founder-voice long-form (300–800 words) on Mondays; brand-voice claim-led on Thursdays |
| **WhatsApp Business** | Doral/Miami SME network; founder's goTRG warm list | 1:1 outbound + broadcast list; no spam | Spanish-first, "tú" form for SMEs, "usted" for brokers |
| **Doral broker walk-ins** | Carlos persona, in-person | Weekly route, 3–5 offices per visit | Founder-led; collaborator does not need to staff this |
| **Trade-press pitch** | JOC, American Shipper, FreightWaves, Container News, Miami Herald, Diario Las Américas, Listín Diario | 1 pitch per month, paired with a real milestone | Brunswick-discipline; numbers, no superlatives |

Goal of this stage: **10 paying SMEs + 1 design-partner broker by Month 7** (per the hustle-fund-deck-copy slide 6 target — confirm with founder before locking).

### 4.2 At scale — Broker-led, 20–50× leverage

Once V1 has its first design-partner broker, the GTM motion shifts: every new broker onboarded = 20–50 SME files on the same handshake. This is the **broker-augmentation distribution wedge** locked in PRD §4 and Slide 6 of the hustle-fund deck. The white-label API into the licensed broker's book is the channel surface; the marketing collaborator's job here is producing the broker-facing one-pager, the demo script, and the white-label co-marketing template — not running ad campaigns.

### 4.3 Channels deliberately out of scope (V1)

- Paid Google / Meta / LinkedIn advertising. Premature; CAC will be uninformative without product-market fit signals.
- Influencer / creator marketing. Wrong audience trust profile for a pre-MSB fintech.
- TikTok / Instagram Reels at scale. Instagram remains a brand-presence channel for founder voice and Latino-business-community visibility, not a primary acquisition channel.
- Podcasting (own show). Guest appearances yes, owning a show no — too high a fixed cost for the stage.
- Trade-show booths. Worth attending (eMerge Americas, MIAS, NCBFAA) as a walker, not a sponsor.

---

## 5. Launch Phases

The "launch" frame here is not a single Big Bang — it is a sequenced rollout against KAN-22 and the first-broker milestone. Dates are illustrative; founder confirms before the collaborator builds against them.

### 5.1 T-30 — Foundation

Pre-launch hardening. The site, the brand book, the email infrastructure, the social accounts, and the first set of evergreen assets must be in place before any external push.

- Confirm www.puenteai.ai copy reflects the v0.3 reconciliation (already drafted in `docs/marketing/website-copy-refresh-2026-04-29.md` and `docs/marketing/lovable-handoff-2026-04-29.md`).
- Stand up `hello@puenteai.ai` and `jay@puenteai.ai` with proper SPF/DKIM/DMARC. Email-deliverability is non-negotiable for cold outreach.
- LinkedIn brand page polished; founder profile aligned to the v0.3 one-liner.
- WhatsApp Business account verified; broadcast list seeded with the Doral / goTRG warm network.
- Press kit assembled: founder bio (50/100/250-word), brand book, two product screenshots, locked one-liner.
- KAN-22 interview script finalized (this is a product-team artifact, but the marketing collaborator should review it for any leakage of unsupportable claims).

### 5.2 Launch Week — First externally-visible motion

Triggered by either (a) KAN-22 yielding the first written-permission quote, or (b) the first signed broker LOI. Whichever comes first is the launch trigger. Do not launch without one of those two.

- Day 1: Founder LinkedIn post — "Why I'm building this." 600–800 words, founder-voice. Bilingual EN/ES.
- Day 2: Brand-voice LinkedIn announcement — locked one-liner, the new website hero, single CTA to *Analyze a document*.
- Day 3: Trade-press pitch goes out (JOC / FreightWaves / Miami Herald). Founder-bio + locked one-liner + the actual milestone (signed broker or quotable customer).
- Day 4: WhatsApp broadcast to the warm list — Spanish-first, single sentence, single CTA, link to the analyze page.
- Day 5: First Carlos-facing one-pager published to `/for-brokers`; Doral walk-in route runs against it.
- Day 6–7: Reactive comment & inbound-press handling. Hold replies to anything that asks about V2 settlement until counsel-cleared.

### 5.3 T+30 — First evidence

The window where we earn the second pilot, the second broker, and the first piece of earned media that names a customer.

- Founder weekly update goes live on a fixed cadence (Friday EOD). Format: shipped / shipping / stuck / asks. List sent to friends-and-family + advisor + pre-seed investor circle. Not public.
- LinkedIn cadence holds at 2 founder + 1 brand per week.
- Spanish-language press pitch (Diario Las Américas, Listín Diario, Acento.com.do) goes out paired with a real DR-corridor milestone.
- First "behind the build" Instagram post — Santo Domingo / Miami imagery, founder-voice, captions in Spanish-first or bilingual.
- Begin tracking and reporting against §6 KPIs.

### 5.4 T+90 — Repeatable motion

The point where the GTM stops being a launch and starts being a flywheel. Marker: 5 paying SMEs + 1 active design-partner broker + 1 piece of earned media in a tier-1 trade outlet.

- Begin testing the broker-led co-marketing template — joint LinkedIn post, joint email signature, joint webinar.
- First persona-specific landing pages live: `/for-importers`, `/for-brokers`, `/for-exporters`. Localized.
- First nurture email sequence (3-touch) live for SME leads who upload a document but do not return within 7 days.
- Investor-prospecting cold email sequence ready (separate from marketing flow; coordinate with `docs/future-vision/vc-email-sequence.md` and the hustle-fund-deck recommendation to *not* send the deck cold).

---

## 6. Measurement & KPIs

Direct-response discipline: every campaign has one measurable outcome. Brand metrics are secondary at this stage.

### 6.1 North-star (single number)

**Number of SMEs who have uploaded one real (non-test) document through the production pipeline in the last 30 days.** This is the closest proxy to product-market fit at our stage. Pull from Firestore `transactions/{user_id}/docs/{doc_id}` per the multi-tenant scoping in CLAUDE.md.

### 6.2 Acquisition KPIs

- Signed-up SMEs per month (by source: LinkedIn, WhatsApp, broker referral, direct, press).
- First-document-upload rate within 14 days of signup.
- Doral broker walk-in conversion to LOI conversation.
- Trade-press placements per month (tier-1: JOC, FreightWaves, American Shipper, Miami Herald; tier-2: regional Spanish-language press).

### 6.3 Engagement KPIs

- LinkedIn impressions, engagement rate, follower growth on both founder and brand accounts.
- Email open / click / reply rates on the founder weekly update and any nurture sequences.
- WhatsApp broadcast read-through rate.

### 6.4 Trust KPIs (qualitative)

- Number of unsolicited inbound messages from licensed brokers per month.
- Number of customer / broker conversations that yield a written-permission quote.
- Press placements that quote the locked one-liner verbatim.

### 6.5 Anti-KPIs (do not optimize for these)

- Twitter follower count.
- Instagram likes per post.
- Generic "brand awareness" surveys.
- Vanity press placements that do not name a real product capability.

---

## 7. Risks & Failure Modes

What can go wrong, in declining order of probability.

### 7.1 Compliance drift

A copy variant slips through that implies Puente moves money, or claims a license we have not filed, or names a customer who has not signed a permission release. Mitigation: every asset routes through the `marketing-pr` compliance pass and (for any regulatory-edge claim) through `fintech-security`. The seven guardrails in `.claude/agents/marketing-pr.md` are non-negotiable.

### 7.2 Broker alienation

A campaign reads as "AI replaces your customs broker" and the Doral broker network turns hostile. The corridor is small; this would be hard to recover from. Mitigation: every asset that mentions Maria also acknowledges Carlos. Broker-augmentation framing is locked.

### 7.3 Spanish-as-translation, not Spanish-as-craft

A piece of marketing copy gets machine-translated into Spanish and ships before a native speaker reviews it. The Miami / Doral / Dominican audience reads bad Spanish as inauthentic in three seconds. Mitigation: every Spanish asset is written in Spanish from a blank page. Founder reviews tone (especially `tú` vs. `usted` — `tú` for SMEs, `usted` for brokers, no exceptions).

### 7.4 Premature investor outreach

A campaign treats Hustle Fund / YC / pre-seed lists as a marketing channel. Per the 2026-04-21 ceo-scope verdict (preserved in `docs/future-vision/hustle-fund-deck-copy.md` §0), the artifact does not exist yet — investor outreach is premature until KAN-22 lands a real customer quote. Marketing collaborator should treat investor-prospecting as a separate workstream and coordinate with the founder before any send.

### 7.5 Tariff / political framing

A copy variant takes a partisan tariff position and alienates half the Miami Latino SME community in one post. Mitigation: speak to cost variance only, never to administration or party. Compliance guardrail #6.

### 7.6 KAN-22 underdelivers

The customer-interview phase yields zero quotable users in 60 days. The "Launch Week" trigger never fires. Mitigation: the Foundation phase work (T-30) has independent value — site refresh, email infrastructure, brand book, press kit are useful regardless. Hold the launch trigger; do not invent traction.

---

## 8. Out of Scope (V1 GTM)

Deliberate exclusions, not oversights.

- **Paid media.** No Google, Meta, LinkedIn, or programmatic ads. Revisit at T+90 only if organic acquisition has reached saturation against the warm network.
- **TV, radio, OOH.** Not appropriate for the stage or the audience.
- **Trade-show sponsorship.** Booth presence at eMerge Americas 2026 or NCBFAA is OK as a walker, not as a sponsor.
- **Influencer or creator partnerships.**
- **Brand campaigns without a measurable outcome.** Every asset has a CTA or it does not ship.
- **Customer testimonials or logo walls** until KAN-22 yields written-permission quotes.
- **Stablecoin / crypto positioning** as the lead message. Stablecoin is a route comparison, not the brand.
- **English-only campaigns.** If a campaign cannot ship in Spanish, it does not ship.
- **V2 settlement messaging** in any present-tense form. Roadmap-only, gated on filings.
- **Non-LATAM corridors** — Asia, Africa, intra-Europe. Out of scope for V1 GTM.
- **Consumer-facing positioning** — Puente is B2B; we do not market to individual senders.

---

## 9. Open Questions for the Recipient

Confirm or revise these before scoping the build. None of these are blockers for reading the doc; all of them affect what you actually do next.

1. **What is the actual launch trigger?** Section 5.2 names two — first KAN-22 quote *or* first signed broker LOI — whichever comes first. Confirm the founder agrees, and if there's a third trigger (closed pre-seed round, public product page going live, etc.), name it.
2. **What is the founder's preferred publish cadence on the founder LinkedIn account?** I have proposed 2 posts per week; if the founder can sustain only 1, we plan around that — fewer posts of higher quality beat a missed cadence.
3. **What budget will exist for Spanish-language native review?** A line item for a Dominican-Spanish or Mexican-Spanish editor on every Spanish asset (for the first six months) is the right unit of investment. Roughly $200–$500 per month at the freelance rate. Confirm or cut.
4. **Press contacts — does the founder have warm intros into JOC, FreightWaves, Miami Herald, or Listín Diario?** Cold press pitches at this stage have a low hit rate. A warm intro from the founder's goTRG network or LinkedIn second-degree is worth ten cold pitches.
5. **Investor outreach — in scope or out?** The hustle-fund-deck-copy doc explicitly recommends *not* sending the deck this week. If the marketing collaborator is being asked to run an investor-prospecting flow alongside the customer-acquisition GTM, that's a second workstream and should be scoped separately.
6. **Domain & email setup — is this done?** The brand book references www.puenteai.ai; CLAUDE.md says the custom domain is provisioning. Confirm that founder@puenteai.ai, hello@puenteai.ai, and jay@puenteai.ai resolve before any external send.
7. **Compliance review path.** I have referenced the `fintech-security` agent for regulatory-edge review. Confirm the marketing collaborator has access to that review path (via the founder, via counsel, or via the agent), or name a substitute reviewer.

---

## 10. References (read these next, in this order)

1. `docs/PRD.md` v0.3 — especially §1 (locked one-liner), §3 (market context), §4 (personas), §5 (V1 capabilities), §10 (V1 out of scope), §11 (open questions), §14 (founder notes — narrative substrate).
2. `docs/CLAUDE.md` — invariants, tech stack, what's actually live, environment.
3. `docs/future-vision/dual-engine-architecture.md` — the Compliance Engine vs. Optimization Engine framing; what is shipped vs. what is roadmap.
4. `docs/future-vision/hustle-fund-deck-copy.md` — most recent narrative thinking on positioning and channel; especially the Slide 6 distribution / channel test.
5. `docs/marketing/brand-profile-2026-04-29.md` — the full brand profile, including image style and writing style guides.
6. `docs/marketing/website-copy-refresh-2026-04-29.md` — section-by-section site copy, EN/ES.
7. `frontend-app/BRAND.md` — locked color, typography, and voice tokens.
8. `.claude/agents/marketing-pr.md` — the `marketing-pr` agent prompt; the operating manual for any new marketing asset and the source of the seven compliance guardrails.

---

*This scope is the working contract between the founder and the marketing collaborator. Treat it as living — when the locked one-liner moves, when KAN-22 lands, when V2 ships, this doc updates. If the doc and the PRD ever conflict, the PRD wins.*
