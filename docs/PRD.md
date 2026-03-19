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
Miami → Mexico City, Miami → Bogotá, Miami → Lima corridors.
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