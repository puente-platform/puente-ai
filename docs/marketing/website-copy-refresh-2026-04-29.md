# Website Copy Refresh — Puente AI

**Author:** Senior Marketing & Communications Lead
**Date:** 2026-04-29
**Aligned to:** PRD v0.3 (commit `4b6f0c3`, PR #43, merged 2026-04-29)
**Target surface:** `puente-platform/puente-ai-insights` (Lovable-built Vite + React app)
**Status:** Draft for founder review → Lovable handoff

---

## 1. Positioning summary

Puente AI is the trade intelligence layer for the **US–LATAM corridor — both directions**. Upload a trade document (invoice, packing list, BL) and in roughly 15 seconds the platform extracts the data, scores fraud risk, flags compliance gaps, and recommends the cheapest legal payment route — savings shown in dollars, before anything moves. We serve two co-equal users on every shipment: **Maria**, the Miami-based bilingual SME owner moving goods between the US and LATAM, and **Carlos**, the licensed US customs broker clearing those shipments for 20–50 SME clients. We're broker-augmentation, not broker-replacement: the broker is the channel. **V1 today is a recommendations layer** — it shows you what to do; it does not move money. Settlement execution comes in V2, after the regulatory groundwork is done. Spanish is built in from day one, not translated on the way out.

---

## 2. What changed and why

- **Corridor is now bidirectional.** Old hero copy reads US→LATAM only ("Pay your supplier $XXX less"). PRD v0.3 §3 explicitly serves LATAM→US imports *and* US→LATAM exports as co-equal flows. Hero rotation, features, FAQ, and trust copy all need to express both directions.
- **Carlos is co-equal, not a footnote.** PRD v0.3 §4 elevates the licensed broker from secondary persona to co-equal customer. The site currently speaks only to Maria. We need a section, not just a sentence, for brokers — broker-augmentation framing, white-label hint, "we make your next clearance faster, not your next layoff easier."
- **V1 honesty.** Several existing strings (testimonials especially) imply or state that Puente moves money. V1 *recommends* — it compares wire vs. stablecoin and shows the savings; it does not execute. Until MSB / Florida MTL / DR EPE are filed and approved, copy must say "shows you," "compares," "recommends," "routes-of-record" — never "sends," "settles," "wires for you."
- **The locked one-liner.** PRD §1 now contains a verbatim, locked one-liner. The hero headline must be that line (or the tightest possible derivative). No paraphrase.
- **Stats sanity-check.** "~15s" is real (PRD §9 V1 success metric, end-to-end <15s). "5 Corridors" maps to the V2 roadmap (Mexico City, Bogotá, Lima, Santo Domingo, plus the founding wedge) — it's a *planned* corridor count, not a live-payment count, so we mark it "supported" not "settling." "113 tests" is real (CLAUDE.md). The fourth stat ("Compliance Signals") is fine; tighten the wording.
- **Country list reframe.** The animated hero currently runs Colombian / Mexican / Brazilian / Peruvian / Chilean — outdated (Brazil is Phase 5, not now; DR is the strategic wedge per §14 Founder Notes). New rotation drops Brazil and Chile, adds Dominican, and alternates *paying a supplier* (US→LATAM) with *getting paid by a buyer* (LATAM→US) so the bidirectional story lives in the most-seen surface on the site.
- **Testimonials.** The 13 hardcoded quotes pre-date the v0.3 reframe and (per inventory) include broker, importer, and exporter voices — that's good — but several almost certainly imply settlement that doesn't exist yet. Flag for review (see §6). Do not fabricate replacements.
- **Founder voice — soft.** The site is brand-voice, not founder-voice, which is correct for the customer-facing surface. The Santo Domingo / Amsterdam / goTRG origin story belongs in `/about`, not the hero. Keep the homepage clean.

---

## 3. Hero block

### 3.1 Animated rotating text (replaces `AnimatedHeroText.tsx` country/dollar list)

Goal: express bidirectional corridor + dollar specificity in the most-seen surface.

**Structure:** rotate eight lines, alternating *pay a supplier* (US→LATAM exporter framing) with *get paid by a buyer* (LATAM→US importer framing). Dollar amounts are illustrative *recommended* savings vs. a 5% wire baseline on a representative shipment size — never claimed as a guaranteed outcome and never claimed as money Puente moved.

**EN rotation (8 frames):**
1. Pay your Colombian supplier **$1,200 less**. Today.
2. Get paid by your Mexican buyer **5 days sooner**. Today.
3. Pay your Dominican supplier **$1,800 less**. Today.
4. Get paid by your Peruvian buyer **5 days sooner**. Today.
5. Pay your Mexican supplier **$2,400 less**. Today.
6. Get paid by your Colombian buyer **5 days sooner**. Today.
7. Pay your Peruvian supplier **$1,500 less**. Today.
8. Get paid by your Dominican buyer **5 days sooner**. Today.

**ES rotation (8 frames, written in Spanish — neutral LatAm, "tú" form to match existing keys):**
1. Págale a tu proveedor colombiano **$1,200 menos**. Hoy.
2. Cóbrale a tu comprador mexicano **5 días antes**. Hoy.
3. Págale a tu proveedor dominicano **$1,800 menos**. Hoy.
4. Cóbrale a tu comprador peruano **5 días antes**. Hoy.
5. Págale a tu proveedor mexicano **$2,400 menos**. Hoy.
6. Cóbrale a tu comprador colombiano **5 días antes**. Hoy.
7. Págale a tu proveedor peruano **$1,500 menos**. Hoy.
8. Cóbrale a tu comprador dominicano **5 días antes**. Hoy.

**Required disclosure (microcopy under the rotation, both languages — V1 honesty):**
- EN: *Recommended savings vs. a 5% wire baseline. Puente shows you the cheapest legal route — execution is your call.*
- ES: *Ahorros estimados frente a una transferencia bancaria del 5%. Puente te muestra la ruta más barata y legal — la ejecución la decides tú.*

### 3.2 Static hero — headline, sub, CTAs

**Headline (EN, locked one-liner verbatim):**
> Puente AI turns a trade document into compliance and payment routing in 15 seconds — for SMEs and customs brokers in the US–LATAM trade corridor.

**Headline (ES, written in Spanish, not translated — preserves the 15-second beat and the SME + broker pairing):**
> Puente AI convierte un documento de comercio en cumplimiento y ruta de pago en 15 segundos — para PyMEs y agentes aduanales del corredor EE. UU.–LATAM.

**Sub-hero (EN):**
> Upload an invoice, a manifest, or a bill of lading — in any language. We extract the data, score the fraud risk, flag compliance gaps, and show you the cheapest legal way to settle. Both directions of the corridor. Built with the brokers who clear the shipment.

**Sub-hero (ES):**
> Sube una factura, un manifiesto o un conocimiento de embarque — en el idioma que sea. Extraemos los datos, calificamos el riesgo de fraude, señalamos los faltantes de cumplimiento y te mostramos la forma más barata y legal de liquidar. En las dos direcciones del corredor. Construido junto a los agentes aduanales que despachan el embarque.

**Primary CTA (EN / ES):** *Analyze a document* / *Analizar un documento*
**Secondary CTA (EN / ES):** *For customs brokers* / *Para agentes aduanales* — links to `/for-brokers` (or anchors to the broker section if no separate route)
**Sign-in CTA (unchanged copy, retained):** *Sign in* / *Iniciar sesión*

---

## 4. Section-by-section table

Format: `i18n key | current EN | current ES | proposed EN | proposed ES | rationale`

### 4.1 Hero (LandingPage.tsx)

| i18n key | current EN | current ES | proposed EN | proposed ES | rationale |
|---|---|---|---|---|---|
| `tagline` | (not captured in inventory) | (not captured) | Trade intelligence for the US–LATAM corridor. Both directions. | Inteligencia comercial para el corredor EE. UU.–LATAM. En las dos direcciones. | Tagline must telegraph bidirectional in 8 words. |
| `heroDesc` | (not captured) | (not captured) | Upload an invoice, a manifest, or a bill of lading — in any language. We extract the data, score the fraud risk, flag compliance gaps, and show you the cheapest legal way to settle. Both directions of the corridor. Built with the brokers who clear the shipment. | Sube una factura, un manifiesto o un conocimiento de embarque — en el idioma que sea. Extraemos los datos, calificamos el riesgo de fraude, señalamos los faltantes de cumplimiento y te mostramos la forma más barata y legal de liquidar. En las dos direcciones del corredor. Construido junto a los agentes aduanales que despachan el embarque. | V1 honest verbs ("show," "score," "flag"); bidirectional + broker named. |
| `startExploring` | (not captured) | (not captured) | Analyze a document | Analizar un documento | Verb-led, single-action. Names the actual product affordance. |
| `browseMarkets` | (not captured) | (not captured) | For customs brokers | Para agentes aduanales | Surfaces Carlos in the hero. Existing key reused for new destination. |
| `signInButton` | (not captured) | (not captured) | Sign in | Iniciar sesión | Unchanged. |
| `getStarted` | (not captured) | (not captured) | Get started | Empezar | Unchanged. |

### 4.2 Stats row (LandingPage.tsx — 4 cards)

| i18n key | current EN | current ES | proposed EN | proposed ES | rationale |
|---|---|---|---|---|---|
| `statInvoice` | (not captured) | (not captured) | Document → analysis | Documento → análisis | Names what the 15s actually measures. |
| `statCorridors` | (not captured) | (not captured) | Corridors supported | Corredores cubiertos | "Supported" — recommendations live, settlement V2. Honest. |
| `statTests` | (not captured) | (not captured) | Backend tests passing | Pruebas de backend en verde | Real number per CLAUDE.md (113). Engineering-trust signal. |
| `statInfra` | (not captured) | (not captured) | Compliance + routing signals | Señales de cumplimiento y ruta | "Signals" — V1 honest. We recommend, we don't execute. |

**Hardcoded stat values** (`statValues` / `statValuesEs` in LandingPage.tsx — see §5 for line refs):

| Stat slot | proposed EN | proposed ES | rationale |
|---|---|---|---|
| 1 | ~15s | ~15s | Real per PRD §9; keep. |
| 2 | 5 corridors | 5 corredores | Mexico, Colombia, Peru, DR, plus founding wedge. Roadmap-anchored. |
| 3 | 113 tests | 113 pruebas | Real per CLAUDE.md. Updates over time — flag for periodic refresh. |
| 4 | Wire vs. stablecoin | Banco vs. stablecoin | What the routing signal actually compares. Concrete. |

### 4.3 Features section (LandingPage.tsx, 6 feature blocks)

Two-block bias: three for Maria, three for Carlos. Both personas should see themselves above the fold of this section.

| i18n key | current EN | current ES | proposed EN | proposed ES | rationale |
|---|---|---|---|---|---|
| `featuresTitle1` | (not captured) | (not captured) | Built for both sides of the corridor | Construido para los dos lados del corredor | Bidirectional in the section title. |
| `featuresTitle2` | (not captured) | (not captured) | One workflow. SME and broker. | Un solo flujo. PyME y agente aduanal. | Names co-equal personas. |
| `feat1Title` | (not captured) | (not captured) | Upload anything. In any language. | Sube lo que sea. En el idioma que sea. | Maria-facing. Document agnosticism = real Gemini capability per PRD §5. |
| `feat1Desc` | (not captured) | (not captured) | PDFs, scans, WhatsApp photos. Spanish, English, Portuguese, Chinese. The AI reads the document so you don't re-key the data. | PDFs, escaneos, fotos de WhatsApp. Español, inglés, portugués, chino. La IA lee el documento para que no tengas que volver a capturar los datos. | Concrete formats + concrete languages. No "AI-powered" superlative. |
| `feat2Title` | (not captured) | (not captured) | Cheapest legal payment route, every time | La ruta de pago más barata y legal, cada vez | "Recommend" framing baked in. V1 honest. |
| `feat2Desc` | (not captured) | (not captured) | We compare bank wire, stablecoin (USDC), and alternatives — and show you the savings in dollars before you settle. You execute through your bank or wallet; Puente shows the route. | Comparamos transferencia bancaria, stablecoin (USDC) y alternativas — y te mostramos el ahorro en dólares antes de liquidar. Tú ejecutas con tu banco o billetera; Puente te muestra la ruta. | Explicit "you execute, we recommend" — V1 honesty front and center. |
| `feat3Title` | (not captured) | (not captured) | Compliance gaps before the shipment moves | Faltantes de cumplimiento antes de que el embarque salga | Surfaces the value: catch errors before demurrage. |
| `feat3Desc` | (not captured) | (not captured) | Required documents per corridor and per direction — US↔Colombia, US↔Mexico, US↔Dominican Republic, US↔Peru. We flag what's missing before customs does. | Documentos requeridos por corredor y por dirección — EE. UU.↔Colombia, EE. UU.↔México, EE. UU.↔República Dominicana, EE. UU.↔Perú. Señalamos lo que falta antes de que aduanas lo haga. | Bidirectional ("↔") in the body. Concrete corridors. |
| `feat4Title` | (not captured) | (not captured) | White-label intelligence for licensed brokers | Inteligencia para agentes aduanales con licencia, marca blanca | Carlos-facing. Names the channel. |
| `feat4Desc` | (not captured) | (not captured) | Carlos clears 20–50 SME files at once. Puente reads the documents, classifies the line items, and flags the edge cases — so you spend your hours on the complex shipments, not on retyping invoice fields. Broker-augmentation, not broker-replacement. | Carlos despacha de 20 a 50 expedientes a la vez. Puente lee los documentos, clasifica las partidas y señala los casos límite — para que dediques tus horas a los embarques complejos, no a recapturar facturas. Aumentamos al agente, no lo reemplazamos. | Speaks to Carlos's day. Defangs the "are you replacing me" objection in-line. |
| `feat5Title` | (not captured) | (not captured) | Fraud risk, scored 0–100 | Riesgo de fraude, calificado 0–100 | Concrete output. No "AI-powered." |
| `feat5Desc` | (not captured) | (not captured) | Counterparty patterns, amount anomalies, corridor risk, document consistency. Plain-English (or plain-Spanish) explanation of every flag — not a black box. | Patrones de contraparte, anomalías de monto, riesgo del corredor, consistencia documental. Explicación en español (o inglés) sencillo de cada señal — sin caja negra. | Maps to PRD §5 capability. Names the explainability. |
| `feat6Title` | (not captured) | (not captured) | Spanish first. Not translated. | En español de verdad. No traducido. | Differentiator most US fintechs can't claim. |
| `feat6Desc` | (not captured) | (not captured) | The interface, the AI prompts, and the customer support thread are written in Spanish from the start. The product was built by a team that speaks the language — not localized after the fact. | La interfaz, los prompts de IA y el soporte se escriben en español desde el principio. El producto lo construye un equipo que habla el idioma — no se localiza al final. | PRD §5 + §14 Founder Notes; Heritage as Competitive Advantage. |

### 4.4 CTA block (LandingPage.tsx)

| i18n key | current EN | current ES | proposed EN | proposed ES | rationale |
|---|---|---|---|---|---|
| `ctaTitle` | (not captured) | (not captured) | Run one document through Puente. See what 15 seconds tells you. | Pasa un documento por Puente. Mira lo que te dicen 15 segundos. | Specific. Verb-led. Mirrors hero. |
| `ctaDesc` | (not captured) | (not captured) | No credit card. No phone call. Upload an invoice or a manifest, in English or Spanish, and see the extraction, the compliance check, the fraud score, and the recommended payment route — in under a minute. | Sin tarjeta. Sin llamada. Sube una factura o un manifiesto, en inglés o en español, y mira la extracción, el control de cumplimiento, el puntaje de fraude y la ruta de pago recomendada — en menos de un minuto. | Removes friction objections; explicitly bilingual. |
| `ctaButton` | (not captured) | (not captured) | Analyze a document | Analizar un documento | Mirrors hero primary CTA. Single source of truth. |

### 4.5 FAQ accordion (`frequently-asked-questions-accordion.tsx`)

| i18n key | current EN | current ES | proposed EN | proposed ES | rationale |
|---|---|---|---|---|---|
| `faq1Q` | Are you a bank? | (not captured) | Are you a bank? Do you move my money? | ¿Son un banco? ¿Mueven mi dinero? | Forward the V1-honesty answer; drives the most important compliance question to the top. |
| `faq1A` | (not captured) | (not captured) | No. Puente AI is a trade intelligence platform. We read your documents, score risk, check compliance, and **recommend** the cheapest legal payment route. You execute the payment through your existing bank, broker, or wallet. We will roll out direct settlement (V2) only after the relevant licenses (FinCEN MSB in the US, EPE with the BCRD in the Dominican Republic) are filed and approved. | No. Puente AI es una plataforma de inteligencia comercial. Leemos tus documentos, calificamos el riesgo, revisamos el cumplimiento y **recomendamos** la ruta de pago más barata y legal. Tú ejecutas el pago con tu banco, agente o billetera. La liquidación directa (V2) la habilitaremos solo después de obtener las licencias correspondientes (FinCEN MSB en EE. UU., EPE con el BCRD en República Dominicana). | Locks the V1 honest answer + names the V2 path without overcommitting. |
| `faq2Q` | (not captured) | (not captured) | How do you calculate the savings number? | ¿Cómo calculan el ahorro que muestran? | Numbers earn trust only when the math is visible. |
| `faq2A` | (not captured) | (not captured) | We compare a baseline traditional bank wire (typical fee 3–7%, plus 5–7 business days settlement) against alternative routes — most often a USDC stablecoin route — and show the dollar difference. The recommendation is exactly that: a recommendation. Real-world rates vary by your bank, your supplier's bank, and the day. We aim to land within 10% of actuals. | Comparamos una transferencia bancaria tradicional como base (comisión típica 3–7%, más 5–7 días hábiles) contra rutas alternativas — usualmente una ruta de stablecoin USDC — y mostramos la diferencia en dólares. La recomendación es eso: una recomendación. Las tarifas reales varían según tu banco, el banco de tu proveedor y el día. Buscamos quedar dentro del 10% de las cifras reales. | Quantifies accuracy target (PRD §9 success metric). Manages expectations. |
| `faq3Q` | (not captured) | (not captured) | How do you verify a supplier or buyer? | ¿Cómo verifican a un proveedor o comprador? | Was implicit "supplier"; bidirectional fix. |
| `faq3A` | (not captured) | (not captured) | We extract counterparty data from the documents you upload, score it against amount anomalies, corridor patterns, and document consistency, and flag anything unusual with a plain-language explanation. We do not maintain a global supplier registry, and we do not represent that any counterparty is "verified" beyond what the documents show. Sanctions screening (Phase 3) is a planned capability, not yet live. | Extraemos los datos de la contraparte de los documentos que subes, los calificamos contra anomalías de monto, patrones del corredor y consistencia documental, y señalamos cualquier cosa inusual con una explicación en lenguaje sencillo. No mantenemos un registro global de proveedores y no afirmamos que una contraparte esté "verificada" más allá de lo que muestran los documentos. La revisión de sanciones (Fase 3) es una capacidad planeada, todavía no activa. | Honest scope. Doesn't overpromise OFAC/sanctions checking that isn't shipped. |
| `faq4Q` | (not captured) | (not captured) | Is this legal? Stablecoin payments, AI-driven compliance — what's the regulatory story? | ¿Esto es legal? Pagos en stablecoin, cumplimiento por IA — ¿cuál es la historia regulatoria? | Anticipates the broker objection. |
| `faq4A` | (not captured) | (not captured) | V1 (today) is a recommendations layer — fully legal as a software product, the same way an FX comparison site is legal. V2 (settlement execution) requires money-transmission licensing: we are pursuing FinCEN MSB registration in the US, Florida MTL state-level licensing, and EPE registration with the BCRD in the Dominican Republic before any direct money movement goes live. Until those are complete, settlement happens through your existing rails — not through Puente. | V1 (hoy) es una capa de recomendaciones — legal como producto de software, igual que un comparador de tipos de cambio. V2 (ejecución de pagos) requiere licencias de transmisión de dinero: estamos tramitando el registro MSB ante FinCEN en EE. UU., la licencia MTL del estado de Florida, y el registro como EPE ante el BCRD en República Dominicana antes de habilitar movimiento de dinero directo. Hasta entonces, la liquidación se hace por tus rieles actuales — no por Puente. | Names the licenses without claiming any are filed/granted. Founder note: confirm timing language ("pursuing" is correct as of 2026-04-29). |
| `faq5Q` | (not captured) | (not captured) | Is my data safe? | ¿Mis datos están seguros? | Universal SME concern. |
| `faq5A` | (not captured) | (not captured) | Every customer's documents and analysis are isolated by user ID — your invoices live in a path the rest of our customer base cannot read. We use Firebase Auth (Google Identity Platform) for sign-in, and JSON Web Tokens for every API call. Document storage is on Google Cloud Storage in the United States. We do not sell data, we do not share data with third parties beyond the AI providers needed to process the document, and we delete documents on request. | Los documentos y análisis de cada cliente están aislados por ID de usuario — tus facturas viven en una ruta que el resto de nuestros clientes no puede leer. Usamos Firebase Auth (Google Identity Platform) para iniciar sesión y JSON Web Tokens en cada llamada a la API. El almacenamiento documental está en Google Cloud Storage en Estados Unidos. No vendemos datos, no los compartimos con terceros más allá de los proveedores de IA necesarios para procesar el documento, y los borramos a petición. | Maps to KAN-16 multi-tenant work that's actually shipped. Specific = trustworthy. |
| `faq6Q` | (not captured) | (not captured) | Do I need to change banks or brokers? | ¿Tengo que cambiar de banco o de agente aduanal? | Most-feared customer-acquisition objection in this market. |
| `faq6A` | (not captured) | (not captured) | No. Puente works alongside your current bank, your current broker, and your current freight forwarder. If you have a customs broker you trust, we make their job faster — we don't replace them. If you have a banking relationship that's giving you 1.5% on wires (rare), keep it; we'll tell you when it's the right route. We add intelligence; we don't ask you to rip and replace. | No. Puente funciona junto a tu banco, tu agente aduanal y tu agente de carga actuales. Si tienes un agente aduanal de confianza, le aceleramos el trabajo — no lo reemplazamos. Si tu banco te cobra 1.5% en transferencias (poco común), quédate con él; te diremos cuando esa sea la mejor ruta. Sumamos inteligencia; no te pedimos que cambies todo. | Defuses the broker objection AND the "switch banks" objection in one answer. Carlos sees it. Maria sees it. |

### 4.6 Trust footer (`TrustFooter.tsx`)

| i18n key | current EN | current ES | proposed EN | proposed ES | rationale |
|---|---|---|---|---|---|
| `encrypted` | (not captured) | (not captured) | TLS encrypted. JWT-authenticated. | Cifrado TLS. Autenticado por JWT. | Concrete > generic "secure." |
| `corridorVerified` | (not captured) | (not captured) | Built for the US–LATAM corridor | Construido para el corredor EE. UU.–LATAM | "Verified" was vague; "built for" is honest and specific. |
| `poweredBy` | (not captured) | (not captured) | Document AI + Gemini on Google Cloud | Document AI + Gemini sobre Google Cloud | Names the actual tech stack — credibility without buzzword bingo. |
| `privacy` | (not captured) | (not captured) | Privacy | Privacidad | Unchanged. |
| `terms` | (not captured) | (not captured) | Terms | Términos | Unchanged. |
| (hardcoded) `© 2026 Puente AI` | © 2026 Puente AI | © 2026 Puente AI | © {currentYear} Puente AI | © {currentYear} Puente AI | Move year out of hardcoded — see §5. |

### 4.7 Login / Signup

| i18n key | current EN | current ES | proposed EN | proposed ES | rationale |
|---|---|---|---|---|---|
| `signInTitle` | (not captured) | (not captured) | Welcome back | Bienvenido de vuelta | Warmer than generic "Sign in." |
| `signInSubtitle` | (not captured) | (not captured) | Pick up where you left off — your documents, your routes, your transactions. | Continúa donde lo dejaste — tus documentos, tus rutas, tus transacciones. | Specific re-entry promise. |
| `signUpTitle` | (not captured) | (not captured) | Create your Puente account | Crea tu cuenta de Puente | Plain. |
| `signUpSubtitle` | (not captured) | (not captured) | Free to start. No credit card. Analyze your first document in under a minute. | Empezar es gratis. Sin tarjeta. Analiza tu primer documento en menos de un minuto. | Removes the two largest signup-form objections. |
| `loginTrust` | (not captured) | (not captured) | Built for SMEs and customs brokers in the US–LATAM corridor. | Construido para PyMEs y agentes aduanales del corredor EE. UU.–LATAM. | Reinforces both personas. |
| `noAccount` | (not captured) | (not captured) | New here? Create an account. | ¿Nuevo aquí? Crea una cuenta. | Unchanged copy intent. |
| `alreadyHaveAccount` | (not captured) | (not captured) | Already have an account? Sign in. | ¿Ya tienes cuenta? Inicia sesión. | Unchanged copy intent. |

### 4.8 Other pages — only if positioning shift forces an edit

**TransactionsPage.tsx** — line 184 currently displays `USA → COL` as a hardcoded corridor token. Bidirectional reframe means transaction rows must support both directions of arrow. See §5 for the proposed component-level edit. No i18n key change required, but transaction list headers should add an `i18n` key for "Direction" / "Dirección" if not present.

**Dashboard, Explorer, Insights** — KAN-36 still has these on mock data. Until KAN-36 lands, page copy edits would write against mock data — defer this section's copy refresh. Add a banner key:

| i18n key | proposed EN | proposed ES | rationale |
|---|---|---|---|
| `demoDataBadge` | Sample data — your live numbers will appear after your first analysis | Datos de ejemplo — tus cifras reales aparecerán después de tu primer análisis | Required by KAN-36 punch list (CLAUDE.md). Replaces "live"-feeling mock numbers with an honest signal. |

**AnalyzePage.tsx** — line 134/138 hardcoded `Request failed` / `Retry`. See §5. Strings should move to i18n.

**ResetPasswordPage.tsx** — entire form (lines 45/55/58/64/86) hardcoded. See §5.

**NotFound.tsx** — line 15 hardcoded. See §5.

---

## 5. Hardcoded edits (component-level changes for Lovable)

Each row gives the file path, the line, and the current → proposed change. Where the file already supports bilingual copy via i18n, the proposed string moves into a new i18n key rather than staying hardcoded.

| File | Line(s) | Current | Proposed action | Notes |
|---|---|---|---|---|
| `src/components/AnimatedHeroText.tsx` | 5–22 | Hardcoded array of country names + dollar amounts (one direction only) | Replace with the 8-frame bidirectional rotation in §3.1 — one EN array, one ES array, switched on locale | Animated tokens shouldn't be hardcoded inside the rotation array; move the country/role/amount into structured objects so we can localize without duplicating the rotation logic. |
| `src/pages/LandingPage.tsx` | 28–29 | `statValues = ['~15s', '5 Corridors', 'Route Comparison', 'Compliance Signals']`; `statValuesEs = […]` (likely English-only or shallow ES) | Replace per §4.2 stat values table. Keep arrays but pull labels from i18n via the `statInvoice/statCorridors/statTests/statInfra` keys — only the *values* should remain in the component. | Reduces drift; values change quarterly (113 tests will become 130). |
| `src/pages/LandingPage.tsx` | 73, 200, 216 | `PUENTE AI` wordmark hardcoded | Leave as hardcoded — wordmark is brand-locked, never localized. | No edit. |
| `src/components/testimonials-background-with-drag.tsx` | 68–177 | 13 hardcoded testimonials (EN/ES/PT) | See §6 — flag for review, do not edit copy here. | Founder permission required before any testimonial publishes. |
| `src/components/TrustFooter.tsx` | (year) | `© 2026 Puente AI` hardcoded | Replace with `© {new Date().getFullYear()} Puente AI` (or move to i18n with a `footerCopyright` key that interpolates the year) | Already wrong on Jan 1, 2027. |
| `src/components/TrustFooter.tsx` | (brand) | `Puente AI` token | Leave hardcoded; brand. | No edit. |
| `src/pages/AnalyzePage.tsx` | 134 | `Request failed` (hardcoded EN) | Move to i18n key `analyzeRequestFailed` — EN: `Analysis failed — check your connection and try again` / ES: `El análisis falló — revisa tu conexión e intenta de nuevo` | Adds bilingual support; clarifies likely cause. |
| `src/pages/AnalyzePage.tsx` | 138 | `Retry` (hardcoded EN) | Move to i18n key `retry` — EN: `Try again` / ES: `Intentar de nuevo` | "Try again" reads more naturally than "Retry" outside a developer audience. |
| `src/pages/TransactionsPage.tsx` | 184 | Hardcoded corridor token `USA → COL` | Replace with a function that renders origin-arrow-destination from the transaction record's `origin` and `destination` fields, supporting both directions (`COL → USA`, `USA → COL`, `MEX → USA`, `USA → DOM`, etc.). Use ISO-3166 alpha-3 country codes for the tokens; arrow `→` is locale-neutral. | Bidirectional. The data model already supports this — only the rendering is one-direction-coded. |
| `src/pages/ResetPasswordPage.tsx` | 45, 55, 58, 64, 86 | Entire form hardcoded EN | Move to i18n keys: `resetPasswordTitle`, `resetPasswordSubtitle`, `resetPasswordEmailLabel`, `resetPasswordEmailPlaceholder`, `resetPasswordSubmitButton`, `resetPasswordSuccess`, `resetPasswordError`. EN/ES strings below. | Bilingual parity. |
| `src/pages/ResetPasswordPage.tsx` | (new key) `resetPasswordTitle` | — | EN: `Reset your password` / ES: `Restablece tu contraseña` | |
| `src/pages/ResetPasswordPage.tsx` | (new key) `resetPasswordSubtitle` | — | EN: `Enter the email you signed up with. We'll send you a link to set a new password.` / ES: `Ingresa el correo con el que te registraste. Te enviaremos un enlace para definir una nueva contraseña.` | |
| `src/pages/ResetPasswordPage.tsx` | (new key) `resetPasswordEmailLabel` | — | EN: `Email` / ES: `Correo electrónico` | |
| `src/pages/ResetPasswordPage.tsx` | (new key) `resetPasswordEmailPlaceholder` | — | EN: `you@yourcompany.com` / ES: `tu@tuempresa.com` | |
| `src/pages/ResetPasswordPage.tsx` | (new key) `resetPasswordSubmitButton` | — | EN: `Send reset link` / ES: `Enviar enlace` | |
| `src/pages/ResetPasswordPage.tsx` | (new key) `resetPasswordSuccess` | — | EN: `Check your inbox — the link expires in 1 hour.` / ES: `Revisa tu bandeja — el enlace vence en 1 hora.` | |
| `src/pages/ResetPasswordPage.tsx` | (new key) `resetPasswordError` | — | EN: `We couldn't send that link. Check the email and try again.` / ES: `No pudimos enviar el enlace. Revisa el correo e intenta de nuevo.` | |
| `src/pages/NotFound.tsx` | 15 | Hardcoded `404` page copy (EN) | Move to i18n keys `notFoundTitle`, `notFoundDesc`, `notFoundCta`. EN: `That page doesn't exist.` / `Maybe you came in from an old link, or maybe we moved something. Head back home and we'll get you to where you were going.` / `Back to home`. ES: `Esa página no existe.` / `Tal vez llegaste por un enlace viejo, o tal vez movimos algo. Vuelve al inicio y te llevamos a donde ibas.` / `Volver al inicio`. | Bilingual parity; voice-consistent. |

---

## 6. Testimonials review (`testimonials-background-with-drag.tsx`, lines 68–177)

**Hard rule:** the founder has confirmed there are zero signed pilot customers as of 2026-04-29 (per CLAUDE.md and PRD §9 — KAN-22 interview phase, no pilots). Any testimonial that reads as a real customer attribution is a compliance and trust risk. We will not invent quotes. We will not approve copy that implies real customers we don't have.

**Recommendation:** Until at least 3 signed pilot customers per the PRD §9 Year 1 business metric agree in writing to be quoted, the testimonials carousel should either (a) be hidden, or (b) be replaced with **clearly-labeled persona vignettes** that explicitly say "Composite — based on 30+ Miami trader conversations" or similar.

### 6.1 Per-quote disposition (without seeing the actual current text)

Without having access to the 13 current quotes' verbatim text, here is the founder-facing rubric for a same-week review pass. Apply each to every quote:

1. **Does it name a real person and/or a real company?** If yes — verify written permission exists. No permission → retire.
2. **Does it imply Puente moved money / settled a payment / "saved me $X on my last wire"?** If yes — retire (V1 honesty violation, regardless of permission).
3. **Does it imply a corridor direction we don't yet officially serve in copy** (Brazil, Chile, Argentina) **or imply we hold a license we haven't filed** (FinCEN, EPE, MTL)? If yes — retire.
4. **Is the speaker a broker?** If yes and the quote is permission-cleared and V1-honest — keep, and tag it as a Carlos voice in the carousel (improves persona balance per §1).
5. **Is the speaker an SME importer or exporter?** Same test as 4 — keep if cleared and V1-honest, retire otherwise.
6. **Is the quote short, specific, and verb-led?** ("Cut my document review time in half on Mexican manifests" beats "Puente is amazing.") If long, vague, or generic — retire even if permission-cleared.

### 6.2 Thematic gaps a real (future) customer quote could fill

Founder should source quotes — once permission-cleared — that hit one of these themes. We have not written the quotes; these are the briefs to use when interviewing a future customer for the carousel:

- **Carlos-voice broker quote on document throughput** — "I clear N more files per day; the routine ones go in 15 seconds." (Carlos persona; CLAUDE.md broker-augmentation positioning.)
- **Maria-voice US→LATAM exporter on payment savings** — "On a [$X] truckload to Bogotá I saw the wire-vs-stablecoin gap in dollars before I committed. I picked the cheaper route." (Maria founding-wedge; V1-honest verb "saw," not "saved.")
- **Maria-voice LATAM→US importer on compliance** — "Puente caught a missing Certificate of Origin on a Mexican shipment before my broker did. We fixed it the same day." (Bidirectional; broker-augmentation, not broker-replacement.)
- **Spanish-first product experience quote** — "The interface speaks the way I do. I don't translate every screen in my head." (Differentiator — most US fintech can't claim it.)
- **WhatsApp/relationship-first quote** — once Phase 3 ships — "I sent an invoice photo over WhatsApp and got the analysis back in the same thread." (Aligns with PRD §15 future vision; only deploy after Phase 3 lives.)

### 6.3 Interim (this-month) recommendation for the carousel

Replace the current carousel with one of:

- **Option A (cleanest):** Hide the testimonials section entirely until KAN-22 yields at least 3 written-permission quotes. Replace with a "Why we built this" founder-quote block (single short founder voice, attributed to the founder by name, drawn from PRD §14 — no fabrication required).
- **Option B (intermediate):** Keep the carousel, but populate it with 5–7 *clearly-labeled* persona vignettes with the badge "Composite voice, drawn from N+ trader conversations in Miami and Doral, 2026." This is honest and still gives the section visual life.

**Default recommendation:** Option A. Cleaner, smaller compliance surface, and the founder-quote block is a stronger trust signal than carousel filler.

**Founder-quote block (drop-in copy, founder-voice, EN + ES, ready to use):**

EN:
> "I watched immigrant business owners in Miami lose thousands per shipment to wire fees and customs errors. They knew what they were buying, they knew what it was worth, and the system charged them for the privilege of moving their own money. Puente AI is the tool I wish they had when I was selling to them.
> — Jay Alexander, founder"

ES:
> "Vi a dueños de negocios inmigrantes en Miami perder miles de dólares por envío en transferencias y errores aduanales. Sabían qué estaban comprando, sabían cuánto valía, y el sistema les cobraba por el privilegio de mover su propio dinero. Puente AI es la herramienta que ojalá hubieran tenido cuando yo les vendía.
> — Jay Alexander, fundador"

---

## 7. Lovable handoff prompt — see `docs/marketing/lovable-handoff-2026-04-29.md`

The Lovable handoff has been moved to a dedicated file: **`docs/marketing/lovable-handoff-2026-04-29.md`**. Paste §A of that doc into Lovable.

**Why a separate file:** the founder confirmed the current site aesthetic is staying — colors, typography, layout, components, animations all unchanged. The Lovable handoff is therefore scoped to **copy text only** (i18n strings + a few hardcoded → i18n migrations). All visual / render directives have been removed and replaced with an explicit "no aesthetic changes; site should look identical, only the words differ" constraint and a side-by-side visual-parity check before merge.

This doc (`website-copy-refresh-2026-04-29.md`) remains the working reference — it has the full section-by-section EN / ES copy tables (§3 hero, §4 sections, §5 hardcoded edits, §6 testimonials review). The Lovable handoff doc is a tighter, paste-ready version of the same copy with the visual-parity guardrail baked in.

**If conflicts:** the Lovable handoff doc is canonical for what ships. Any item in this doc that prescribes render treatment (color, typography, sizes, layout) is superseded by the "no aesthetic changes" stance. Specifically: §6.3 below recommends hiding the testimonials carousel and adding a founder-quote block — that recommendation is **deferred** at the founder's direction; the carousel stays as-is for now and the founder will revisit when permission-cleared customer quotes are available.

---

## 8. Notes for the founder

- **One-liner is locked.** I used the PRD §1 verbatim line as the EN hero headline. The ES version was written in Spanish, not translated — confirm it reads well to a Dominican / Colombian / Mexican ear before publish.
- **Stat #2 ("5 corridors").** The number maps to Mexico, Colombia, Peru, DR, plus the founding-wedge (US→LATAM liquidation). If the founder prefers a different corridor count, that's a one-line change.
- **Stat #3 ("113 tests").** This will drift. Suggest a quarterly refresh cadence — or move the value to a build-time constant generated from the test runner output.
- **FAQ #4 — regulatory language.** I wrote "we are pursuing FinCEN MSB registration, Florida MTL, and EPE." Per CLAUDE.md punch-list item #6, MSB is not yet filed. "Pursuing" is honest; "filed" would not be. If the founder files FinCEN MSB this week, update FAQ #4 to "We have filed for FinCEN MSB registration; we are pursuing Florida MTL and EPE." If timing is uncertain, leave "pursuing."
- **Testimonials — deferred per founder direction.** §6.3 below recommends hiding the carousel and replacing it with a founder-quote block. The founder has confirmed they are keeping the current site aesthetic intact (no layout changes), so the carousel stays as-is for now. The founder-quote block in §6.3 remains available as a future option once permission-cleared customer quotes are sourced (gated on KAN-22). The §6 testimonial-review rubric still applies — if any of the 13 current quotes imply settlement Puente doesn't do, those individual quotes should be retired in a separate, copy-only edit.
- **Bidirectional corridor in `TransactionsPage.tsx`.** The `USA → COL` hardcoded token (line 184) is the single biggest copy-data drift on the site relative to v0.3. Even if no other change ships, this one should — the data model already supports both directions; only the renderer is locked.
- **Animated hero dollar amounts.** I used $1,200 / $1,500 / $1,800 / $2,400 — all illustrative against the 5% wire baseline on representative truckload sizes. They are not pulled from a specific customer transaction. If the founder wants, we can tighten these to a single round number ($1,500 across the board) to reduce visual noise. The disclosure under the rotation is non-negotiable from a compliance standpoint.
- **Spanish register — `tú` vs. `usted`.** I used `tú` throughout, matching the existing project's i18n register per the inventory note. For the broker-facing `/for-brokers` route (when built), I'd recommend `usted` — Carlos is older, more formal, and "Sr./Sra." is the WhatsApp default in that segment. Flag for follow-up.
- **Page audit not in scope.** Dashboard, Explorer, Insights, Settings copy refresh is gated on KAN-36 (mock-data replacement). Once KAN-36 lands, a follow-up doc covers those pages.
- **Compliance review:** This doc passes V1 honesty, no fabricated customers, no claimed licenses, and explicit broker-augmentation framing. Recommend routing through `fintech-security` for a final compliance read before publish — especially FAQ #4 and the hero microcopy disclosure.

---

*Built to be paste-ready. Hand to Lovable, run a preview build, ship.*
