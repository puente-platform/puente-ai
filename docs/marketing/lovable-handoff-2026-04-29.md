# Lovable Handoff — Puente AI Website Copy Refresh

**Date:** 2026-04-29
**Aligned to:** PRD v0.3, BRAND.md (positioning + tagline)
**Target:** `puente-platform/puente-ai-insights` (Lovable Vite + React app)
**Scope:** Copy text only. No visual / aesthetic changes — keep the existing design system, colors, typography, components, and layout exactly as they are.
**How to use:** Paste the block in §A below into Lovable as a single prompt.

---

## A. Paste-into-Lovable prompt

> Refresh the customer-facing copy on the Puente AI marketing site. **This is a copy-only refresh — do not change colors, typography, components, layout, or any visual styling.** Use existing CSS variables and components as-is. Only update the strings below (and the small structural items called out under §8). Apply all changes in one PR and push a preview build.
>
> ### 1. Hero — `LandingPage.tsx` + `AnimatedHeroText.tsx`
>
> **`tagline`** (brand tagline — populate the existing tagline element):
> - EN: `Pay less. Move faster.`
> - ES: `Paga menos. Mueve más rápido.`
>
> **`heroDesc`** (sub-hero):
> - EN: `Upload an invoice, a manifest, or a bill of lading — in any language. We extract the data, score the fraud risk, flag compliance gaps, and show you the cheapest legal way to settle. Both directions of the corridor. Built with the brokers who clear the shipment.`
> - ES: `Sube una factura, un manifiesto o un conocimiento de embarque — en el idioma que sea. Extraemos los datos, calificamos el riesgo de fraude, señalamos los faltantes de cumplimiento y te mostramos la forma más barata y legal de liquidar. En las dos direcciones del corredor. Construido junto a los agentes aduanales que despachan el embarque.`
>
> **Headline** — if there is a static headline element, set it to the locked one-liner:
> - EN: `Puente AI turns a trade document into compliance and payment routing in 15 seconds — for SMEs and customs brokers in the US–LATAM trade corridor.`
> - ES: `Puente AI convierte un documento de comercio en cumplimiento y ruta de pago en 15 segundos — para PyMEs y agentes aduanales del corredor EE. UU.–LATAM.`
>
> **CTAs** (re-use existing button components, just update labels):
> - `startExploring` (primary): EN `Analyze a document` / ES `Analizar un documento`
> - `browseMarkets` (secondary): EN `For customs brokers` / ES `Para agentes aduanales` — link to `/for-brokers` if the route exists, otherwise anchor to the broker section
> - `signInButton`: EN `Sign in` / ES `Iniciar sesión`
> - `getStarted`: EN `Get started` / ES `Empezar`
>
> **Animated rotating text** — replace the country/dollar list in `AnimatedHeroText.tsx` with this 8-frame bidirectional rotation. Keep the existing animation, styling, and behavior unchanged — only the strings change. Drop Brazilian and Chilean (out of current corridor scope); add Dominican.
>
> EN rotation:
> 1. Pay your Colombian supplier **$1,200 less**. Today.
> 2. Get paid by your Mexican buyer **5 days sooner**. Today.
> 3. Pay your Dominican supplier **$1,800 less**. Today.
> 4. Get paid by your Peruvian buyer **5 days sooner**. Today.
> 5. Pay your Mexican supplier **$2,400 less**. Today.
> 6. Get paid by your Colombian buyer **5 days sooner**. Today.
> 7. Pay your Peruvian supplier **$1,500 less**. Today.
> 8. Get paid by your Dominican buyer **5 days sooner**. Today.
>
> ES rotation:
> 1. Págale a tu proveedor colombiano **$1,200 menos**. Hoy.
> 2. Cóbrale a tu comprador mexicano **5 días antes**. Hoy.
> 3. Págale a tu proveedor dominicano **$1,800 menos**. Hoy.
> 4. Cóbrale a tu comprador peruano **5 días antes**. Hoy.
> 5. Págale a tu proveedor mexicano **$2,400 menos**. Hoy.
> 6. Cóbrale a tu comprador colombiano **5 días antes**. Hoy.
> 7. Págale a tu proveedor peruano **$1,500 menos**. Hoy.
> 8. Cóbrale a tu comprador dominicano **5 días antes**. Hoy.
>
> **Microcopy disclosure** — add a small line of supporting text directly beneath the rotation, using whatever existing `text-muted-foreground` (or equivalent) treatment the page already uses for fine print. If no slot exists, add one as plain text — do not introduce new visual styling. New i18n keys `heroDisclosureEn` / `heroDisclosureEs`:
> - EN: `Recommended savings vs. a 5% wire baseline. Puente shows you the cheapest legal route — execution is your call.`
> - ES: `Ahorros estimados frente a una transferencia bancaria del 5%. Puente te muestra la ruta más barata y legal — la ejecución la decides tú.`
>
> **Refactor note (data only, no visual change):** if the rotation array currently hardcodes country + role + amount as a single concatenated string, restructure it to an array of objects with `country`, `role`, `savingsToken`, `closer` fields so EN/ES localization doesn't have to duplicate the rotation logic. The rendered output should look identical.
>
> ### 2. Stats row — `LandingPage.tsx`
>
> Update labels (i18n keys):
> - `statInvoice`: EN `Document → analysis` / ES `Documento → análisis`
> - `statCorridors`: EN `Corridors supported` / ES `Corredores cubiertos`
> - `statTests`: EN `Backend tests passing` / ES `Pruebas de backend en verde`
> - `statInfra`: EN `Compliance + routing signals` / ES `Señales de cumplimiento y ruta`
>
> Update hardcoded values (`statValues` / `statValuesEs` arrays, lines 28–29):
> 1. `~15s`
> 2. EN `5 corridors` / ES `5 corredores`
> 3. EN `113 tests` / ES `113 pruebas`
> 4. EN `Wire vs. stablecoin` / ES `Banco vs. stablecoin`
>
> ### 3. Features section — `LandingPage.tsx` (6 blocks)
>
> Section title:
> - `featuresTitle1`: EN `Built for both sides of the corridor` / ES `Construido para los dos lados del corredor`
> - `featuresTitle2`: EN `One workflow. SME and broker.` / ES `Un solo flujo. PyME y agente aduanal.`
>
> Six feature blocks:
>
> **`feat1Title` / `feat1Desc`:**
> - EN: `Upload anything. In any language.` / `PDFs, scans, WhatsApp photos. Spanish, English, Portuguese, Chinese. The AI reads the document so you don't re-key the data.`
> - ES: `Sube lo que sea. En el idioma que sea.` / `PDFs, escaneos, fotos de WhatsApp. Español, inglés, portugués, chino. La IA lee el documento para que no tengas que volver a capturar los datos.`
>
> **`feat2Title` / `feat2Desc`:**
> - EN: `Cheapest legal payment route, every time` / `We compare bank wire, stablecoin (USDC), and alternatives — and show you the savings in dollars before you settle. You execute through your bank or wallet; Puente shows the route.`
> - ES: `La ruta de pago más barata y legal, cada vez` / `Comparamos transferencia bancaria, stablecoin (USDC) y alternativas — y te mostramos el ahorro en dólares antes de liquidar. Tú ejecutas con tu banco o billetera; Puente te muestra la ruta.`
>
> **`feat3Title` / `feat3Desc`:**
> - EN: `Compliance gaps before the shipment moves` / `Required documents per corridor and per direction — US↔Colombia, US↔Mexico, US↔Dominican Republic, US↔Peru. We flag what's missing before customs does.`
> - ES: `Faltantes de cumplimiento antes de que el embarque salga` / `Documentos requeridos por corredor y por dirección — EE. UU.↔Colombia, EE. UU.↔México, EE. UU.↔República Dominicana, EE. UU.↔Perú. Señalamos lo que falta antes de que aduanas lo haga.`
>
> **`feat4Title` / `feat4Desc`:**
> - EN: `White-label intelligence for licensed brokers` / `Carlos clears 20–50 SME files at once. Puente reads the documents, classifies the line items, and flags the edge cases — so you spend your hours on the complex shipments, not on retyping invoice fields. Broker-augmentation, not broker-replacement.`
> - ES: `Inteligencia para agentes aduanales con licencia, marca blanca` / `Carlos despacha de 20 a 50 expedientes a la vez. Puente lee los documentos, clasifica las partidas y señala los casos límite — para que dediques tus horas a los embarques complejos, no a recapturar facturas. Aumentamos al agente, no lo reemplazamos.`
>
> **`feat5Title` / `feat5Desc`:**
> - EN: `Fraud risk, scored 0–100` / `Counterparty patterns, amount anomalies, corridor risk, document consistency. Plain-English (or plain-Spanish) explanation of every flag — not a black box.`
> - ES: `Riesgo de fraude, calificado 0–100` / `Patrones de contraparte, anomalías de monto, riesgo del corredor, consistencia documental. Explicación en español (o inglés) sencillo de cada señal — sin caja negra.`
>
> **`feat6Title` / `feat6Desc`:**
> - EN: `Spanish first. Not translated.` / `The interface, the AI prompts, and the customer support thread are written in Spanish from the start. The product was built by a team that speaks the language — not localized after the fact.`
> - ES: `En español de verdad. No traducido.` / `La interfaz, los prompts de IA y el soporte se escriben en español desde el principio. El producto lo construye un equipo que habla el idioma — no se localiza al final.`
>
> ### 4. CTA block — `LandingPage.tsx`
>
> - `ctaTitle`: EN `Run one document through Puente. See what 15 seconds tells you.` / ES `Pasa un documento por Puente. Mira lo que te dicen 15 segundos.`
> - `ctaDesc`: EN `No credit card. No phone call. Upload an invoice or a manifest, in English or Spanish, and see the extraction, the compliance check, the fraud score, and the recommended payment route — in under a minute.` / ES `Sin tarjeta. Sin llamada. Sube una factura o un manifiesto, en inglés o en español, y mira la extracción, el control de cumplimiento, el puntaje de fraude y la ruta de pago recomendada — en menos de un minuto.`
> - `ctaButton`: EN `Analyze a document` / ES `Analizar un documento`
>
> ### 5. FAQ accordion — `frequently-asked-questions-accordion.tsx`
>
> Six Q&A pairs. Q1 and Q4 are load-bearing (V1-honesty trust answers) — do not paraphrase.
>
> **Q1:**
> - `faq1Q` EN: `Are you a bank? Do you move my money?` / ES: `¿Son un banco? ¿Mueven mi dinero?`
> - `faq1A` EN: `No. Puente AI is a trade intelligence platform. We read your documents, score risk, check compliance, and **recommend** the cheapest legal payment route. You execute the payment through your existing bank, broker, or wallet. We will roll out direct settlement (V2) only after the relevant licenses (FinCEN MSB in the US, EPE with the BCRD in the Dominican Republic) are filed and approved.`
> - `faq1A` ES: `No. Puente AI es una plataforma de inteligencia comercial. Leemos tus documentos, calificamos el riesgo, revisamos el cumplimiento y **recomendamos** la ruta de pago más barata y legal. Tú ejecutas el pago con tu banco, agente o billetera. La liquidación directa (V2) la habilitaremos solo después de obtener las licencias correspondientes (FinCEN MSB en EE. UU., EPE con el BCRD en República Dominicana).`
>
> **Q2:**
> - `faq2Q` EN: `How do you calculate the savings number?` / ES: `¿Cómo calculan el ahorro que muestran?`
> - `faq2A` EN: `We compare a baseline traditional bank wire (typical fee 3–7%, plus 5–7 business days settlement) against alternative routes — most often a USDC stablecoin route — and show the dollar difference. The recommendation is exactly that: a recommendation. Real-world rates vary by your bank, your supplier's bank, and the day. We aim to land within 10% of actuals.`
> - `faq2A` ES: `Comparamos una transferencia bancaria tradicional como base (comisión típica 3–7%, más 5–7 días hábiles) contra rutas alternativas — usualmente una ruta de stablecoin USDC — y mostramos la diferencia en dólares. La recomendación es eso: una recomendación. Las tarifas reales varían según tu banco, el banco de tu proveedor y el día. Buscamos quedar dentro del 10% de las cifras reales.`
>
> **Q3:**
> - `faq3Q` EN: `How do you verify a supplier or buyer?` / ES: `¿Cómo verifican a un proveedor o comprador?`
> - `faq3A` EN: `We extract counterparty data from the documents you upload, score it against amount anomalies, corridor patterns, and document consistency, and flag anything unusual with a plain-language explanation. We do not maintain a global supplier registry, and we do not represent that any counterparty is "verified" beyond what the documents show. Sanctions screening (Phase 3) is a planned capability, not yet live.`
> - `faq3A` ES: `Extraemos los datos de la contraparte de los documentos que subes, los calificamos contra anomalías de monto, patrones del corredor y consistencia documental, y señalamos cualquier cosa inusual con una explicación en lenguaje sencillo. No mantenemos un registro global de proveedores y no afirmamos que una contraparte esté "verificada" más allá de lo que muestran los documentos. La revisión de sanciones (Fase 3) es una capacidad planeada, todavía no activa.`
>
> **Q4:**
> - `faq4Q` EN: `Is this legal? Stablecoin payments, AI-driven compliance — what's the regulatory story?` / ES: `¿Esto es legal? Pagos en stablecoin, cumplimiento por IA — ¿cuál es la historia regulatoria?`
> - `faq4A` EN: `V1 (today) is a recommendations layer — fully legal as a software product, the same way an FX comparison site is legal. V2 (settlement execution) requires money-transmission licensing: we are pursuing FinCEN MSB registration in the US, Florida MTL state-level licensing, and EPE registration with the BCRD in the Dominican Republic before any direct money movement goes live. Until those are complete, settlement happens through your existing rails — not through Puente.`
> - `faq4A` ES: `V1 (hoy) es una capa de recomendaciones — legal como producto de software, igual que un comparador de tipos de cambio. V2 (ejecución de pagos) requiere licencias de transmisión de dinero: estamos tramitando el registro MSB ante FinCEN en EE. UU., la licencia MTL del estado de Florida, y el registro como EPE ante el BCRD en República Dominicana antes de habilitar movimiento de dinero directo. Hasta entonces, la liquidación se hace por tus rieles actuales — no por Puente.`
>
> **Q5:**
> - `faq5Q` EN: `Is my data safe?` / ES: `¿Mis datos están seguros?`
> - `faq5A` EN: `Every customer's documents and analysis are isolated by user ID — your invoices live in a path the rest of our customer base cannot read. We use Firebase Auth (Google Identity Platform) for sign-in, and JSON Web Tokens for every API call. Document storage is on Google Cloud Storage in the United States. We do not sell data, we do not share data with third parties beyond the AI providers needed to process the document, and we delete documents on request.`
> - `faq5A` ES: `Los documentos y análisis de cada cliente están aislados por ID de usuario — tus facturas viven en una ruta que el resto de nuestros clientes no puede leer. Usamos Firebase Auth (Google Identity Platform) para iniciar sesión y JSON Web Tokens en cada llamada a la API. El almacenamiento documental está en Google Cloud Storage en Estados Unidos. No vendemos datos, no los compartimos con terceros más allá de los proveedores de IA necesarios para procesar el documento, y los borramos a petición.`
>
> **Q6:**
> - `faq6Q` EN: `Do I need to change banks or brokers?` / ES: `¿Tengo que cambiar de banco o de agente aduanal?`
> - `faq6A` EN: `No. Puente works alongside your current bank, your current broker, and your current freight forwarder. If you have a customs broker you trust, we make their job faster — we don't replace them. If you have a banking relationship that's giving you 1.5% on wires (rare), keep it; we'll tell you when it's the right route. We add intelligence; we don't ask you to rip and replace.`
> - `faq6A` ES: `No. Puente funciona junto a tu banco, tu agente aduanal y tu agente de carga actuales. Si tienes un agente aduanal de confianza, le aceleramos el trabajo — no lo reemplazamos. Si tu banco te cobra 1.5% en transferencias (poco común), quédate con él; te diremos cuando esa sea la mejor ruta. Sumamos inteligencia; no te pedimos que cambies todo.`
>
> ### 6. Trust footer — `TrustFooter.tsx`
>
> - `encrypted`: EN `TLS encrypted. JWT-authenticated.` / ES `Cifrado TLS. Autenticado por JWT.`
> - `corridorVerified`: EN `Built for the US–LATAM corridor` / ES `Construido para el corredor EE. UU.–LATAM`
> - `poweredBy`: EN `Document AI + Gemini on Google Cloud` / ES `Document AI + Gemini sobre Google Cloud`
> - `privacy`: EN `Privacy` / ES `Privacidad`
> - `terms`: EN `Terms` / ES `Términos`
> - **Year fix:** replace hardcoded `© 2026 Puente AI` with `© {new Date().getFullYear()} Puente AI`. Wordmark `Puente AI` stays brand-locked, never localized.
>
> ### 7. Login / Signup
>
> - `signInTitle`: EN `Welcome back` / ES `Bienvenido de vuelta`
> - `signInSubtitle`: EN `Pick up where you left off — your documents, your routes, your transactions.` / ES `Continúa donde lo dejaste — tus documentos, tus rutas, tus transacciones.`
> - `signUpTitle`: EN `Create your Puente account` / ES `Crea tu cuenta de Puente`
> - `signUpSubtitle`: EN `Free to start. No credit card. Analyze your first document in under a minute.` / ES `Empezar es gratis. Sin tarjeta. Analiza tu primer documento en menos de un minuto.`
> - `loginTrust`: EN `Built for SMEs and customs brokers in the US–LATAM corridor.` / ES `Construido para PyMEs y agentes aduanales del corredor EE. UU.–LATAM.`
> - `noAccount`: EN `New here? Create an account.` / ES `¿Nuevo aquí? Crea una cuenta.`
> - `alreadyHaveAccount`: EN `Already have an account? Sign in.` / ES `¿Ya tienes cuenta? Inicia sesión.`
>
> ### 8. Hardcoded → i18n migrations (text + bilingual support, no visual change)
>
> - **`AnalyzePage.tsx` lines 134/138** — move to i18n:
>   - `analyzeRequestFailed`: EN `Analysis failed — check your connection and try again` / ES `El análisis falló — revisa tu conexión e intenta de nuevo`
>   - `retry`: EN `Try again` / ES `Intentar de nuevo`
> - **`TransactionsPage.tsx` line 184** — replace hardcoded `USA → COL` with a function that renders origin-arrow-destination from each transaction record's `origin` and `destination` fields. Must support **both directions**: `COL → USA`, `USA → COL`, `MEX → USA`, `USA → DOM`, `USA → PER`, `PER → USA`, `USA → MEX`, `DOM → USA`. Use ISO-3166 alpha-3 country codes; the `→` arrow is locale-neutral. Keep existing styling on the cell.
> - **`ResetPasswordPage.tsx`** — entire form (lines 45/55/58/64/86) currently hardcoded EN. Move to i18n keys with the same component / styling, just bilingual:
>   - `resetPasswordTitle`: EN `Reset your password` / ES `Restablece tu contraseña`
>   - `resetPasswordSubtitle`: EN `Enter the email you signed up with. We'll send you a link to set a new password.` / ES `Ingresa el correo con el que te registraste. Te enviaremos un enlace para definir una nueva contraseña.`
>   - `resetPasswordEmailLabel`: EN `Email` / ES `Correo electrónico`
>   - `resetPasswordEmailPlaceholder`: EN `you@yourcompany.com` / ES `tu@tuempresa.com`
>   - `resetPasswordSubmitButton`: EN `Send reset link` / ES `Enviar enlace`
>   - `resetPasswordSuccess`: EN `Check your inbox — the link expires in 1 hour.` / ES `Revisa tu bandeja — el enlace vence en 1 hora.`
>   - `resetPasswordError`: EN `We couldn't send that link. Check the email and try again.` / ES `No pudimos enviar el enlace. Revisa el correo e intenta de nuevo.`
> - **`NotFound.tsx` line 15** — move to i18n keys, same component / styling:
>   - `notFoundTitle`: EN `That page doesn't exist.` / ES `Esa página no existe.`
>   - `notFoundDesc`: EN `Maybe you came in from an old link, or maybe we moved something. Head back home and we'll get you to where you were going.` / ES `Tal vez llegaste por un enlace viejo, o tal vez movimos algo. Vuelve al inicio y te llevamos a donde ibas.`
>   - `notFoundCta`: EN `Back to home` / ES `Volver al inicio`
>
> ### 9. Testimonials carousel — leave as-is
>
> Do not edit the 13 hardcoded testimonials in `testimonials-background-with-drag.tsx`. The founder is reviewing them separately and will give a follow-up directive when permission-cleared customer quotes are available (gated on the broker/customer interview phase). No change in this PR.
>
> ### 10. Demo-data badge (KAN-36 prep, copy only)
>
> Until the dashboard / explorer / insights / transactions pages move off mock data, add a `demoDataBadge` i18n key and surface it in each mock-driven page header using whatever badge / pill component the page already uses (re-use existing styling — do not introduce new visual treatment):
> - EN: `Sample data — your live numbers will appear after your first analysis`
> - ES: `Datos de ejemplo — tus cifras reales aparecerán después de tu primer análisis`
>
> ### Constraints (non-negotiable)
>
> - **No visual / aesthetic changes.** Keep all existing colors, typography, sizes, spacing, gradients, animations, and component structure exactly as they are. This PR is copy text and i18n keys only.
> - Every new string must exist in both EN and ES. The Spanish was written in Spanish (neutral LatAm, "tú" form) — do not machine-translate it or "improve" it.
> - Do not invent customer names, dollar savings, or pilot counts. The 113 tests / ~15s / 5 corridors numbers are real and may be used.
> - Do not write any string that says we "send," "settle," "wire," or "transfer" money. We "show," "compare," "recommend," "flag," "score." V1 is a recommendations layer.
> - Do not reference any regulatory license as "held," "filed," or "approved" — only as "pursuing."
>
> ### When done
>
> Push a preview build and ping the founder. Verification checklist for the founder before merge:
>
> - [ ] Hero rotation cycles 8 frames, alternating supplier and buyer framings, both languages
> - [ ] Microcopy disclosure visible beneath the rotation in both languages
> - [ ] Stat row labels and values updated, both languages
> - [ ] All six features updated, both languages
> - [ ] FAQ has six Q&A pairs in both languages; Q1 and Q4 are word-for-word as specified
> - [ ] Trust footer reads "Document AI + Gemini on Google Cloud" / "sobre Google Cloud"
> - [ ] Year in trust footer is computed at runtime, not hardcoded
> - [ ] Transactions page renders both corridor directions, not just `USA → COL`
> - [ ] Reset password page is bilingual
> - [ ] 404 page is bilingual
> - [ ] AnalyzePage error/retry strings are bilingual
> - [ ] Testimonials carousel is unchanged
> - [ ] No CSS / styling / layout changes — site looks identical to before, just with new copy

---

## B. Out of scope (explicit)

- **All visual / aesthetic changes** — the founder likes the current look-and-feel. No color, typography, layout, or component changes.
- Testimonials carousel content or visibility — founder is handling separately when permission-cleared quotes are available.
- Dashboard / Explorer / Insights / Settings copy refresh — gated on KAN-36 (mock-data replacement).
- DESIGN.md cleanup (route to docs-engineering separately).
- Backend API copy (Gemini / Document AI error messages). Different work stream.

---

## C. Founder verification before merge

Read the checklist in §A on the live preview before approving Lovable's PR. Two highest-risk items:

1. **FAQ #1 and #4 word-for-word** — these are the V1-honesty trust answers. If Lovable paraphrases either, reject the PR.
2. **Visual parity** — site should look identical to today's site, only the words differ. Open the current production site in one tab and the preview in another and compare. If anything visual has changed, reject the PR and ask Lovable to revert styling.

Everything else is recoverable in a follow-up commit.
