# Puente AI — Product Requirements Document
**Version:** 0.2  
**Author:** Jay Alexander  
**Date:** March 2026  
**Status:** Draft

---

## 1. Vision

Puente AI is the trade intelligence and payment infrastructure 
for the Americas — starting with Miami's liquidation import 
corridor and expanding to every major US-LATAM border crossing.

The long-term goal is a vertically integrated platform that 
handles the entire lifecycle of a cross-border SME transaction:
document intelligence → compliance → payment routing → 
customs preparation → trade credit.

Think Stripe, but for cross-border trade finance in the Americas.

---

## 2. Problem

Small and medium enterprises (SMEs) importing goods into the 
US from Latin America, or exporting US liquidation goods to 
LATAM markets, face five compounding friction points on every 
single transaction:

**Cost**
Traditional bank wire transfers charge 3–7% in fees on every 
settlement. On a $50,000 truckload that's $1,500–$3,500 gone 
before the goods even arrive.

**Speed**
SWIFT wire settlements take 5–7 business days. Suppliers in 
Colombia, Mexico, and Peru won't release the next shipment 
until the previous one clears. Slow payments mean slower 
inventory turns and lost deals.

**HS Code Classification**
Every product crossing a border needs a Harmonized System 
(HS) code for customs. A single liquidation truckload from 
a US retailer can contain 400+ mixed SKUs — electronics, 
clothing, appliances, toys. Classifying each one correctly 
requires a customs broker charging $150–300/hour. 
Misclassification means fines and shipment holds.

**Customs Documentation**
Commercial invoices, bills of lading, certificates of origin, 
packing lists — each corridor has different requirements. 
Missing or incorrect documents stop shipments at the border. 
The importer pays demurrage fees while their goods sit in a 
bonded warehouse.

**Unknown Landed Cost**
Importers often don't know their true landed cost until goods 
arrive. Purchase price + duties + tariffs + port fees + 
brokerage + settlement costs = surprises that turn profitable 
deals into losses.

---

## 3. Market Context

Miami is the financial and logistics capital of the Americas:

- Port of Miami handles $50B+ in annual trade volume
- Doral, FL is home to thousands of LATAM-focused import/
  export businesses
- The US-Mexico border (Laredo, El Paso, McAllen, San Diego) 
  handles $300B+ in annual commercial trade
- High inflation in Argentina, Venezuela, and other LATAM 
  markets is driving demand for USD-denominated settlements
  and stablecoin alternatives

The liquidation and returns import corridor is a specific, 
underserved niche within this market:
- US retailers generate $800B+ in returns annually
- A significant portion is liquidated as truckload lots
- Miami-based buyers purchase these lots and ship them to 
  LATAM markets for resale
- This corridor is high-volume, relationship-driven, and 
  almost entirely manual in its financial operations

---

## 4. User

**Primary Persona: Maria**
- Miami-based importer, age 35–55
- Born in Colombia, Venezuela, Dominican Republic or Mexico — bilingual English/Spanish 
- Managing $500K–$5M per year in trade volume
- Buys liquidation truckloads from US companies like goTRG, 
  B-Stock, or Direct Liquidation
- Ships to resellers in Bogotá, Caracas, Lima, or Mexico City
- Not technical — uses WhatsApp, email, and basic software
- Has a customs broker she trusts but finds expensive
- Banks with a local Miami bank that charges her full wire fees

**Her core frustration:**
"I know what I'm buying, I know what it's worth, I know my 
buyer in Bogotá is waiting. Why does it take a week, cost me 
thousands in fees, and require me to call my customs broker 
every single time just to move money and clear goods?"

**Secondary Persona: Carlos**
- Customs broker or freight forwarder in Miami or Laredo
- Manages 20–50 importer clients simultaneously
- Spends 40% of his time on manual document review and 
  HS code classification
- Would pay for a tool that automates the routine work so 
  he can focus on complex cases

---

## 5. Solution

Puente AI is an AI-powered trade intelligence assistant that 
automates the most painful parts of cross-border SME trade.

**Core capabilities (V1 — building now):**

1. **Document Ingestion**
   Upload any trade document — invoice, bill of lading, 
   packing list, manifest — in any language. PDF, image, 
   or scan. Gemini handles Spanish, Portuguese, English, 
   and Chinese natively.

2. **Intelligent Extraction**
   AI reads the document and pulls structured data — 
   parties, amounts, currencies, dates, line items, 
   product descriptions — with no manual data entry.

3. **HS Code Classification**
   For manifests with multiple SKUs, AI assigns the correct 
   HS code to each product automatically. Flags edge cases 
   for human review. Reduces customs broker dependency for 
   routine shipments.

4. **Fraud Risk Scoring**
   Transaction scored 0–100 based on counterparty patterns, 
   amount anomalies, corridor risk, and document consistency.
   Plain-English explanation of any flags.

5. **Compliance Gap Detection**
   Checks required documents for the specific corridor 
   (US→Colombia, US→Mexico, etc.). Shows exactly what's 
   missing before the shipment moves.

6. **Payment Route Recommendation**
   Compares Traditional Bank Wire vs Stablecoin (USDC/Stellar) 
   vs alternatives. Shows cost, speed, and savings in dollars.
   Maria sees: "Save $1,200 and 5 days by settling via USDC."

7. **Landed Cost Estimation**
   Calculates estimated total landed cost including duties 
   by HS code, port fees, and settlement costs — before 
   the buyer commits to the purchase.

**Language:** Full Spanish and English support throughout. 
UI toggle. Documents accepted in any language.

---

## 6. Product Roadmap

### V1 — Trade Intelligence Layer (building now)
Document upload → AI extraction → fraud score → 
compliance check → routing recommendation → landed cost
Target: working demo by Month 4

### V2 — Payment Execution (Year 1)
Actual stablecoin settlements via USDC on Stellar or Ripple.
Miami → Mexico City, Miami → Bogotá, Miami → Lima, Miami → Santo Domingo (DR-CAFTA) corridors.
Requires: MSB registration, legal review, banking partnerships.

### V3 — Customs Intelligence (Year 2)
Automated customs document preparation. Integration with 
US CBP ACE portal and Mexican SAT APIs. Full landed cost 
accuracy. Reduce customs broker dependency for routine 
shipments by 70%.

### V4 — Trade Credit + Invoice Financing (Year 3)
Net-30 terms and invoice financing for verified importers.
Risk model powered by Puente's own transaction history —
not FICO scores. Every transaction processed in V1–V3 
trains a proprietary credit risk model banks cannot replicate.

### V5 — Border Infrastructure (Year 5+)
Embedded in freight brokers, customs agents, and logistics 
platforms at Laredo, El Paso, McAllen, and San Diego crossings.
The intelligence layer underneath the entire US-LATAM 
commercial trade corridor.

---

## 7. Why the Lending Moat is Real

Traditional banks assess SME credit risk using FICO scores 
and tax returns — backward-looking, blunt instruments that 
systematically underserve immigrant-owned businesses with 
thin US credit histories but profitable, high-volume 
import operations.

After processing 500 transactions for Maria, Puente AI knows:
- Her average invoice size and payment timing
- Her supplier reliability across corridors
- Her seasonal volume patterns
- Her compliance track record
- Her landed cost accuracy vs actuals

That is a real-time, forward-looking risk model built from 
actual trade behavior. It prices credit more accurately than 
any bank can. That data flywheel — more transactions → 
better risk model → cheaper capital → more transactions — 
is the billion dollar moat. It only exists if we start 
collecting clean, structured transaction data in V1 today.

---

## 8. Technical Architecture

- **Frontend:** Next.js 14, TailwindCSS, Shadcn/ui → Vercel
- **Backend:** FastAPI + Uvicorn → GCP Cloud Run
- **Storage:** GCP Cloud Storage (documents)
- **Database:** GCP Firestore (transaction records)
- **AI Engine:** Vertex AI Gemini Flash + Document AI
- **Agent Orchestration:** Langflow
- **Observability:** Arize Phoenix
- **CI/CD:** GitHub Actions → GCP Cloud Run
- **Languages:** English + Spanish (Phase 1), 
  Portuguese (Phase 2)

**Future stack additions:**
- Tavily (Phase 3 — sanctions checking)
- Stablecoin rails via Stellar or Ripple SDK (Phase V2)
- DataStax (Phase 5 — vector search at scale)

---

## 9. Success Metrics

### Technical (V1)
- Document field extraction accuracy: >90%
- HS code classification accuracy: >85%
- End-to-end analysis time: <15 seconds
- API uptime: >99%

### Product (V1)
- First-time user understands results without instructions
- Cost savings recommendation accurate within 10% of 
  real-world rates
- Spanish UI fully functional and natural — not translated, 
  designed

### Business (Year 1)
- 10 Miami importers interviewed before building
- 3 pilot users running real transactions by Month 7
- 1 customs broker or freight forwarder as design partner

---

## 10. Out of Scope (V1)

Deliberate exclusions — not oversights:

- Real payment execution (legal groundwork first)
- Regulatory licensing — MSB, FinCEN, lending licenses
- Mobile application
- Multi-user team accounts
- Email or WhatsApp notifications
- Production security hardening
- Actual stablecoin transactions

**Stablecoin note:** V1 recommends and shows savings. 
Execution comes in V2 after legal review. The recommendation 
engine is fully buildable and valuable on its own.

---

## 11. Open Questions

Research to be answered by customer interviews:

- [ ] Which corridor hurts most — Mexico, Colombia, or Peru?
- [ ] Is the #1 pain fees, speed, or HS classification?
- [ ] Do importers trust AI for compliance, or do they need 
      human sign-off?
- [ ] Would customs brokers use this as a tool or see it 
      as a threat?
- [ ] What document formats are most common — PDF invoices, 
      Excel manifests, WhatsApp photos of paper docs?
- [ ] Is there appetite for stablecoin settlement among 
      LATAM suppliers, or is USD wire still preferred?

---

## 12. Founder Context

The founder has direct experience in this market:
- Former sales role at goTRG (Return Pros) — sold liquidation 
  truckloads to LATAM importers
- Direct exposure to HS code, customs, and wire settlement 
  pain from the seller side
- Miami-based — direct access to the target customer
- MS in AI/ML at Northeastern University (Align program) — 
  building the technical capability in parallel with the product

This is not a solution looking for a problem. This is a 
founder who watched the problem happen for years and is now 
building the tools to fix it.

---

## 13. Revision History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | March 2026 | Initial draft |
| 0.2 | March 2026 | Added liquidation corridor angle, |
|     |             | Spanish support, stablecoin vision, |
|     |             | lending moat, border expansion roadmap |

## 14. Founder Notes 

This section captures the founder's personal motivation and long-term 
vision. It exists to keep the north star visible during the hard months 
of building, and to inform future strategic decisions without 
contaminating near-term execution.

### Why This Exists

Puente AI is not a solution looking for a problem. It was born from 
direct, personal exposure to the friction it solves. As a former sales 
professional at goTRG (Return Pros), the founder watched Miami-based 
importers — many of them Latino, many of them Dominican — lose thousands 
of dollars per shipment to wire fees, customs errors, and compliance 
delays they didn't fully understand. That experience is the product's 
foundation.

### Heritage as Competitive Advantage

The founder was born in Amsterdam, Netherlands, holding EU citizenship 
with a direct pathway to DNB (Dutch Central Bank) EMI licensing — 
passportable across all 27 EU member states under PSD2. This provides 
native regulatory standing in the US, EU, and Dominican Republic 
simultaneously — the three primary jurisdictions Puente AI operates in.

Most US fintech companies enter LATAM markets by hiring local 
consultants and translating their English UI. Puente AI is built from 
the inside out — Spanish first, relationship first, community first.

### The Santo Domingo Vision

The long-term goal is to establish Puente AI's regional Latin American 
headquarters in Santo Domingo, Dominican Republic. This is not purely 
sentimental — it is strategic:

- The DR holds DR-CAFTA (duty-free access to the US market)
- The DR holds the EU-CARIFORUM EPA (duty-free access to all 27 EU 
  markets)
- The DR is actively pursuing Mercosur integration (South American 
  gateway)
- Google's $500M Digital Exchange Hub (March 2026) makes the DR a 
  legitimate AI processing hub for the Caribbean basin
- Puerto Caucedo (DP World) is expanding to 2.25M TEU capacity — 
  a direct on-ramp for the liquidation goods corridor in the PRD

A Santo Domingo HQ means: local engineering talent, regulatory 
proximity to the BCRD, cultural credibility with Dominican and 
Caribbean suppliers, and access to Law 171-07 tax incentives for 
foreign investment.

### The Personal Mission

To build something that makes the people who look like Maria — 
immigrant-owned SMEs moving goods between the Americas — as financially 
empowered as the large corporations they compete against. 

Every feature we build should pass this test:
"Does this make Maria's business stronger?"

If yes, build it.
If no, cut it.

---

## 15. Future Vision — Ideas Parked for the Right Moment

These are real, researched ideas that belong in Puente AI's future 
but not in the current build. They are documented here so they are 
never lost and can be picked up at the right phase.

**Review cadence:** Revisit this section at the start of each new 
phase to determine if anything has moved from "future" to "now."

---

### Dominican Republic Regulatory Path (V2 prerequisite)

To legally execute USDC payments in the DR, Puente AI will need to 
register as an Entidad de Pago Electrónico (EPE) with the Central 
Bank of the Dominican Republic (BCRD).

Key requirements as of March 2026:
- Minimum paid-in capital: RD$15,000,000 (~$255,000 USD)
- Dominican subsidiary incorporation (S.R.L. or S.A.)
- AML/KYC compliance under Law 155-17
- Compliance officer resident in the DR
- External IT audit from a BCRD-approved firm
- Cybersecurity manual per Circular 01/24

This is a post-revenue milestone. Pursue after V1 has real users 
and the seed round is closed.

**Key contact when ready:**
ProDominicana — Investment Director: Marcial Smester
servicios@prodominicana.gob.do | +1 809-530-5505

---

### Stellar SEP-31 Integration (V2 technical path)

For the Miami → Santo Domingo corridor, the technical implementation 
uses Stellar's SEP-31 (Cross-Border Payments) protocol:

- SEP-10: Authentication between sending and receiving anchors
- SEP-12: KYC data exchange compliant with both FinCEN and Law 155-17
- SEP-31: Actual USDC movement from Miami sender to DR receiver
- Off-ramp: DR receiving anchor converts USDC to DOP via 
  Pagos al Instante (BCRD's instant payment system)

Stellar is the right choice over Ripple for this use case — Stellar 
was designed for SME cross-border payments, Ripple for bank-to-bank. 
Maria is not a bank.

Revisit this when V2 payment execution begins (Year 1 post-launch).

---

### Trade Agreement Intelligence Layer (V3 feature)

The DR's unique treaty position creates a compliance intelligence 
opportunity no competitor currently offers:

DR-CAFTA — 0% tariffs on 97% of US-DR goods. Puente AI can 
automatically generate Certificates of Origin to claim these savings.

EU-CARIFORUM EPA — Duty-free access to all 27 EU markets. Enables 
a future Miami → DR → Rotterdam corridor.

Mercosur (active negotiations, 2026) — If finalized, enables 
DR-hub routing for Argentina and Brazil trade with the US.

Build this as an automatic treaty-mapping layer in V3 when the 
customs intelligence module is live. Every HS code classification 
should automatically flag applicable treaty benefits.

### WhatsApp-First Interface (Phase 3)

Primary delivery channel for Puente AI intelligence 
will be WhatsApp Business API. Maria uploads an invoice 
photo via WhatsApp and receives analysis results in the 
same thread within 15 seconds.

Secondary channels:
- Telegram bot (developer testing and tech-savvy users)
- SMS notifications (payment confirmations, status updates)
- Native mobile app (Phase 4, after product-market fit)

Implementation: WhatsApp Business API via Meta's official 
Cloud API + Twilio for SMS fallback.

Maria sends invoice photo via WhatsApp
        ↓
WhatsApp Business API webhook
        ↓
Your FastAPI backend receives the image
        ↓
Vertex AI Document AI extracts invoice data
        ↓
Gemini analyzes fraud + compliance + routing
        ↓
WhatsApp Business API sends back formatted response
        ↓
Maria sees results in her existing WhatsApp

---

### High-Value Sector Expansion (V4+)

As the DR transitions from liquidation goods to high-value 
manufacturing, new verticals open for Puente AI:

Pedernales Rare Earths — 150M+ tons identified (February 2026). 
Specialized trade finance for mineral export equipment.

Purdue Semiconductor Partnership — DR workforce training for chip 
assembly. High-precision exports require fast, transparent payment 
rails and complex multi-treaty compliance.

Pedernales Spaceport (LOD Holdings, $600M) — Aerospace components 
require sophisticated customs handling Puente AI can provide.

These are V4+ opportunities. Do not build for them until V1 has 
proven the core loop.

---

### The Lending Moat — Full Vision

Every transaction processed in V1 through V3 trains a proprietary 
credit risk model. By Year 3, Puente AI will know more about Maria's 
business than her bank does:

- Average invoice size and payment timing
- Supplier reliability by corridor
- Seasonal volume patterns  
- Compliance track record
- Landed cost accuracy vs actuals

This data becomes the foundation for net-30 invoice financing 
at rates traditional banks cannot offer to immigrant-owned SMEs 
with thin US credit histories.

The data flywheel:
More transactions → better risk model → cheaper capital → 
more transactions → larger Series A valuation.

This is worth billions. It only exists if we collect clean, 
structured data starting today in V1.

---

### ProDominicana Partnership (Year 1 post-launch)

Target: Pilot program onboarding 50 SMEs in Dominican Free Trade 
Zones (Zonas Francas) onto Puente AI.

Approach ProDominicana after V1 has real transaction volume to 
show. A working product with 10 paying users is worth more in 
that meeting than the best pitch deck in the world.

Strategic framing when ready:
"We are the compliance and liquidity engine for the three largest 
economic blocs touching the DR — DR-CAFTA, EU-CARIFORUM, and 
Mercosur. Our Santo Domingo HQ processes trade intelligence for 
every SME entering or exiting Dominican Free Trade Zones."

---

### Border Crossing Expansion (V5)

US-Mexico land border crossings by priority:
1. Laredo, TX — $300B+ annual trade volume
2. El Paso, TX  
3. McAllen, TX
4. San Diego, CA

Distribution strategy: Partner with freight brokers and customs 
agents who already serve these importers. Become their AI layer, 
not their competitor.

This is a Year 5 initiative. The Miami corridor proves the model. 
The border crossings scale it.

---

*Last updated: March 2026*
*Next review: When Phase 1 is complete and first real user is onboarded*