import { createContext, useContext, useState, useEffect, ReactNode } from "react";

type Lang = "en" | "es";

const SUPPORTED_LANGS: Lang[] = ["en", "es"];
const STORAGE_KEY = "puente.lang";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 365; // 1 year

/** Read a cookie value by name (browser-safe). */
function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`));
  if (!match) return null;
  try {
    return decodeURIComponent(match.slice(name.length + 1));
  } catch {
    return null;
  }
}

/** Write a cookie with sane defaults (1y, path=/, SameSite=Lax). */
function writeCookie(name: string, value: string) {
  if (typeof document === "undefined") return;
  try {
    const secure = typeof location !== "undefined" && location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${name}=${encodeURIComponent(value)}; Max-Age=${COOKIE_MAX_AGE}; Path=/; SameSite=Lax${secure}`;
  } catch {
    // Ignore — cookies may be disabled
  }
}

/**
 * Detect the user's preferred language from:
 *   1. Persisted choice in localStorage
 *   2. Persisted choice in cookie (fallback when localStorage is unavailable)
 *   3. navigator.languages / navigator.language (browser Accept-Language)
 *   4. Fallback to English
 */
function detectLang(): Lang {
  if (typeof window === "undefined") return "en";

  // 1. localStorage
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && SUPPORTED_LANGS.includes(stored as Lang)) {
      return stored as Lang;
    }
  } catch {
    // localStorage may be unavailable (private mode, SSR-like envs) — ignore
  }

  // 2. Cookie fallback
  const cookieLang = readCookie(STORAGE_KEY);
  if (cookieLang && SUPPORTED_LANGS.includes(cookieLang as Lang)) {
    return cookieLang as Lang;
  }

  // 3. Browser Accept-Language
  const candidates: string[] =
    (typeof navigator !== "undefined" &&
      (navigator.languages?.length ? [...navigator.languages] : [navigator.language])) ||
    [];

  for (const tag of candidates) {
    const base = tag.toLowerCase().split("-")[0];
    if (SUPPORTED_LANGS.includes(base as Lang)) return base as Lang;
  }

  // 4. Fallback
  return "en";
}


const translations = {
  // Sidebar
  dashboard: { en: "Dashboard", es: "Inicio" },
  newAnalysis: { en: "New Analysis", es: "Nuevo Análisis" },
  transactions: { en: "Transactions", es: "Transacciones" },
  settings: { en: "Settings", es: "Configuración" },
  explorer: { en: "Explorer", es: "Explorador" },
  aiInsights: { en: "AI Insights", es: "IA Insights" },
  tradeIntelligence: { en: "TRADE INTELLIGENCE", es: "INTELIGENCIA COMERCIAL" },
  roadmap: { en: "Roadmap", es: "Hoja de Ruta" },

  // Dashboard
  greeting: { en: "Hello, Maria 👋", es: "Hola, Maria 👋" },
  corridorActive: { en: "Your current corridor US → Colombia is active.", es: "Tu corredor actual US → Colombia está activo." },
  transfersMonth: { en: "TRANSFERS THIS MONTH", es: "TRANSFERENCIAS ESTE MES" },
  savedMonth: { en: "SAVED THIS MONTH", es: "AHORRADO ESTE MES" },
  avgRisk: { en: "AVG. FRAUD RISK", es: "RIESGO PROMEDIO" },
  pendingDocs: { en: "PENDING DOCUMENTS", es: "DOCUMENTOS PENDIENTES" },
  recentTransactions: { en: "Recent Transactions", es: "Transacciones Recientes" },
  viewAll: { en: "View All", es: "Ver Todos" },
  uploadInvoice: { en: "Analyze New Invoice →", es: "Analizar Nueva Factura →" },
  uploadCta: { en: "Analyze New Invoice", es: "Analizar Nueva Factura" },
  uploadCtaDesc: { en: "Analyze your trade documents with AI to optimize exchange rates and compliance.", es: "Analiza tus documentos comerciales con IA para optimizar tasas de cambio y cumplimiento." },
  newAnalysisCta: { en: "New Real-Time Analysis", es: "Nuevo Análisis en Tiempo Real" },
  corridorBreakdown: { en: "Corridor Breakdown", es: "Desglose de Corredor" },
  trendUp: { en: "+8% trend", es: "+8% tendencia" },
  riskLow: { en: "Low", es: "Bajo" },

  // Supplier names & subtitles
  supplierAlimentos: { en: "Alimentos del Caribe", es: "Alimentos del Caribe" },
  supplierAlimentosSub: { en: "Caribbean Foods", es: "Alimentos del Caribe" },
  supplierTejidos: { en: "Tejidos Medellín", es: "Tejidos Medellín" },
  supplierTejidosSub: { en: "Medellín Textiles", es: "Tejidos Medellín" },
  supplierSuministros: { en: "Suministros Bogotá", es: "Suministros Bogotá" },
  supplierSuministrosSub: { en: "Bogotá Supplies", es: "Suministros Bogotá" },

  // Table headers
  date: { en: "DATE", es: "FECHA" },
  supplier: { en: "SUPPLIER", es: "PROVEEDOR" },
  amount: { en: "AMOUNT", es: "MONTO" },
  risk: { en: "RISK", es: "RIESGO" },
  status: { en: "STATUS", es: "ESTADO" },

  // Status labels
  uploaded: { en: "Uploaded", es: "Subido" },
  processing: { en: "Processing...", es: "Procesando..." },
  extracted: { en: "Extracted", es: "Extraído" },
  analyzed: { en: "Analyzed", es: "Analizado" },
  compliance_checked: { en: "Compliance ✓", es: "Cumplimiento ✓" },
  routed: { en: "Routed ✓", es: "Enrutado ✓" },
  failed: { en: "Error", es: "Error" },

  // Analysis
  step1: { en: "Upload", es: "Subir" },
  step2: { en: "Processing", es: "Procesando" },
  step3: { en: "Results", es: "Resultados" },
  uploadTitle: { en: "Upload your invoice", es: "Sube tu factura" },
  uploadSub: { en: "PDF, photo, or scan · any language", es: "PDF, foto, o escaneo · cualquier idioma" },
  uploadOr: { en: "or click to select", es: "o haz clic para seleccionar" },
  processingTime: { en: "~12 seconds", es: "~12 segundos" },
  processingTrust: { en: "Corridor verification included in analysis", es: "Verificación de corredor incluida en el análisis" },
  fraudRisk: { en: "FRAUD RISK", es: "RIESGO DE FRAUDE" },
  compliance: { en: "COMPLIANCE & CUSTOMS", es: "COMPLIANCE & ADUANA" },
  paymentOpt: { en: "PAYMENT OPTIMIZATION", es: "OPTIMIZACIÓN DE PAGO" },
  youSave: { en: "You save", es: "Ahorras" },
  recommended: { en: "RECOMMENDED", es: "RECOMENDADO" },
  sameDay: { en: "Same day ✓", es: "Mismo día ✓" },
  viewDetails: { en: "View details →", es: "Ver detalles →" },
  saveHistory: { en: "SAVE TO HISTORY", es: "GUARDAR EN HISTORIAL" },
  lowRisk: { en: "LOW RISK", es: "RIESGO BAJO" },
  noAlerts: { en: "No alerts detected", es: "Sin alertas detectadas" },
  cleanHistory: { en: "Clean entity history", es: "Historial de entidad limpio" },
  compliancePass: { en: "COMPLIANCE ✓", es: "CUMPLIMIENTO ✓" },
  corridor: { en: "CORRIDOR", es: "CORREDOR" },
  mostExpensive: { en: "MOST EXPENSIVE", es: "MÁS CARO" },
  totalSavings: { en: "Total potential savings", es: "Potencial de ahorro total" },
  selectedSupplier: { en: "SELECTED SUPPLIER", es: "PROVEEDOR SELECCIONADO" },
  tradeCorridor: { en: "TRADE CORRIDOR", es: "CORREDOR DE COMERCIO" },
  invoiceAmount: { en: "INVOICE AMOUNT", es: "MONTO DE FACTURA" },
  outOf100: { en: "OF 100", es: "DE 100" },
  ofacCleared: { en: "OFAC/SDN Cleared", es: "OFAC/SDN Despejado" },
  ofacDesc: { en: "No matches found in blacklists.", es: "No se encontraron coincidencias en listas negras." },
  htsDetected: { en: "HTS Code 6204.62", es: "Código HTS 6204.62" },
  htsDesc: { en: "Automatically detected from invoice.", es: "Detectado automáticamente en la factura." },
  taxWithholding: { en: "Colombia Tax Withholding", es: "Retención fiscal Colombia" },
  taxDesc: { en: "Requires manual review by local agent.", es: "Requiere revisión manual del agente local." },
  commission: { en: "Commission", es: "Comisión" },
  days12: { en: "1–2 days", es: "1–2 días" },
  days35: { en: "3–5 days", es: "3–5 días" },
  pipelineUploaded: { en: "Uploaded", es: "Subido" },
  pipelineExtracting: { en: "Extracting...", es: "Extrayendo..." },
  pipelineAnalyzing: { en: "Analyzing...", es: "Analizando..." },
  pipelineRouting: { en: "Routing...", es: "Enrutando..." },
  apiWarmingUp: { en: "Our AI is warming up — showing you a sample result", es: "Nuestra IA se está calentando — mostrando un resultado de ejemplo" },
  demoNotice: { en: "DEMO RESULT", es: "RESULTADO DEMO" },
  riskHigh: { en: "High risk", es: "Riesgo alto" },
  riskMedium: { en: "Medium risk", es: "Riesgo medio" },
  missingPrefix: { en: "Missing", es: "Falta" },
  unknownCorridor: { en: "Unknown", es: "Desconocido" },
  unknownSupplier: { en: "Unknown supplier", es: "Proveedor desconocido" },
  daySingular: { en: "day", es: "día" },
  dayPlural: { en: "days", es: "días" },
  wireTransfer: { en: "Wire transfer", es: "Transferencia bancaria" },

  // Transactions page
  transactionHistory: { en: "Transaction History", es: "Historial de Transacciones" },
  exportCsv: { en: "Export CSV", es: "Exportar CSV" },
  saved: { en: "SAVED", es: "AHORRADO" },
  complianceCol: { en: "COMPLIANCE", es: "CUMPLIMIENTO" },
  actions: { en: "ACTIONS", es: "ACCIONES" },
  totalSaved: { en: "Total Estimated Saved", es: "Total Ahorrado Estimado" },
  topCorridor: { en: "TOP CORRIDOR", es: "CORREDOR PRINCIPAL" },
  complianceRate: { en: "COMPLIANCE RATE", es: "TASA DE CUMPLIMIENTO" },
  optimal: { en: "Optimal", es: "Óptimo" },
  statusFilter: { en: "STATUS", es: "ESTADO" },
  all: { en: "All", es: "Todos" },
  error: { en: "Error", es: "Error" },
  riskLowLabel: { en: "Low", es: "Bajo" },
  riskMedLabel: { en: "Med", es: "Medio" },
  riskHighLabel: { en: "High", es: "Alto" },

  // Settings
  settingsTitle: { en: "Settings", es: "Configuración" },
  profile: { en: "Profile", es: "Perfil" },
  language: { en: "Language", es: "Idioma" },
  notifications: { en: "Notifications", es: "Notificaciones" },
  apiKeys: { en: "API Keys", es: "API Keys" },
  langTitle: { en: "Interface language", es: "Idioma de la interfaz" },
  langDesc: { en: "Change the interface language instantly.", es: "Cambia el idioma de toda la plataforma instantáneamente." },
  aiNote: { en: "The selected language will affect both the interface and AI-generated responses.", es: "El idioma seleccionado afectará tanto a la interfaz como a las respuestas generadas por el motor de IA." },
  aiNoteLabel: { en: "AI Note", es: "Nota de IA" },
  comingSoon: { en: "Coming Soon", es: "Próximamente" },
  roadmapTitle: { en: "Coming Soon (V2–V5)", es: "Próximamente (V2–V5)" },
  exploringFuture: { en: "EXPLORING THE FUTURE", es: "EXPLORANDO EL FUTURO" },
  roadmapV2: { en: "Instant transaction settlement", es: "Liquidación instantánea de transacciones" },
  roadmapV3: { en: "Tariff prediction and optimization", es: "Predicción de aranceles y optimización" },
  roadmapV4: { en: "Dynamic credit lines based on real shipping history.", es: "Líneas de crédito dinámicas basadas en historial de carga real." },
  roadmapV5: { en: "Direct connection with IoT sensors at critical logistics nodes.", es: "Conexión directa con sensores IoT en nodos logísticos críticos." },

  // Trust
  encrypted: { en: "TLS encrypted. JWT-authenticated.", es: "Cifrado TLS. Autenticado por JWT." },
  corridorVerified: { en: "Built for the US–LATAM corridor", es: "Construido para el corredor EE. UU.–LATAM" },
  poweredBy: { en: "Document AI + Gemini on Google Cloud", es: "Document AI + Gemini sobre Google Cloud" },

  // Settings roadmap titles
  roadmapV2Title: { en: "Payment Execution Rails", es: "Rieles de Ejecución de Pagos" },
  roadmapV3Title: { en: "Customs Intelligence", es: "Inteligencia Aduanera" },
  roadmapV4Title: { en: "Trade Credit", es: "Crédito Comercial" },
  roadmapV5Title: { en: "Border Infrastructure", es: "Infraestructura Fronteriza" },

  // Sidebar roadmap
  sidebarV2: { en: "V2 Payment Rails", es: "V2 Rieles de Pago" },
  sidebarV3: { en: "V3 Customs Intel", es: "V3 Intel Aduanera" },
  sidebarV4: { en: "V4 Trade Credit", es: "V4 Crédito Comercial" },
  sidebarV5: { en: "V5 Border Infra", es: "V5 Infra Fronteriza" },

  // Insight tags
  tagCoffee: { en: "Coffee", es: "Café" },
  tagColombia: { en: "Colombia", es: "Colombia" },
  tagHS0901: { en: "HS 0901", es: "HS 0901" },
  tagSteel: { en: "Steel", es: "Acero" },
  tagBrazil: { en: "Brazil", es: "Brasil" },
  tagTariffChange: { en: "Tariff Change", es: "Cambio Arancelario" },
  tagPeru: { en: "Peru", es: "Perú" },
  tagFreshProduce: { en: "Fresh Produce", es: "Productos Frescos" },
  tagFTA: { en: "FTA", es: "TLC" },
  tagChile: { en: "Chile", es: "Chile" },
  tagWine: { en: "Wine", es: "Vino" },
  tagLogistics: { en: "Logistics", es: "Logística" },
  tagEcuador: { en: "Ecuador", es: "Ecuador" },
  tagCompliance: { en: "Compliance", es: "Cumplimiento" },
  tagProduce: { en: "Produce", es: "Productos" },

  // Analyze page
  ofacMatchFound: { en: "Match found", es: "Coincidencia encontrada" },

  // Misc
  vsWire: { en: "vs. bank wire", es: "vs. wire bancaria" },
  thisMonth: { en: "this month", es: "este mes" },
  volume: { en: "volume", es: "volumen" },
  privacy: { en: "Privacy", es: "Privacidad" },
  terms: { en: "Terms", es: "Términos" },
  contact: { en: "Contact", es: "Contacto" },
  getStarted: { en: "Get Started", es: "Comenzar" },
  getStartedFree: { en: "Get Started Free", es: "Comenzar Gratis" },

  // Landing page
  tagline: { en: "Trade intelligence for the US–LATAM corridor. Both directions.", es: "Inteligencia comercial para el corredor EE. UU.–LATAM. En las dos direcciones." },
  heroTitle1: { en: "Puente AI turns a trade document into compliance and payment routing in 15 seconds", es: "Puente AI convierte un documento de comercio en cumplimiento y ruta de pago en 15 segundos" },
  heroTitle2: { en: "for SMEs and customs brokers in the US–LATAM trade corridor.", es: "para PyMEs y agentes aduanales del corredor EE. UU.–LATAM." },
  heroDesc: { en: "Upload an invoice, a manifest, or a bill of lading — in any language. We extract the data, score the fraud risk, flag compliance gaps, and show you the cheapest legal way to settle. Both directions of the corridor. Built with the brokers who clear the shipment.", es: "Sube una factura, un manifiesto o un conocimiento de embarque — en el idioma que sea. Extraemos los datos, calificamos el riesgo de fraude, señalamos los faltantes de cumplimiento y te mostramos la forma más barata y legal de liquidar. En las dos direcciones del corredor. Construido junto a los agentes aduanales que despachan el embarque." },
  heroDisclosure: { en: "Recommended savings vs. a 5% wire baseline. Puente shows you the cheapest legal route — execution is your call.", es: "Ahorros estimados frente a una transferencia bancaria del 5%. Puente te muestra la ruta más barata y legal — la ejecución la decides tú." },
  startExploring: { en: "Analyze a document", es: "Analizar un documento" },
  browseMarkets: { en: "For customs brokers", es: "Para agentes aduanales" },
  statInvoice: { en: "Document → analysis", es: "Documento → análisis" },
  statCorridors: { en: "Corridors supported", es: "Corredores cubiertos" },
  statTests: { en: "Saved vs. bank wire", es: "Ahorrado vs. transferencia bancaria" },
  statInfra: { en: "Compliance + routing signals", es: "Señales de cumplimiento y ruta" },
  featuresTitle1: { en: "Built for both sides of the corridor", es: "Construido para los dos lados del corredor" },
  featuresTitle2: { en: "One workflow. SME and broker.", es: "Un solo flujo. PyME y agente aduanal." },
  featuresDesc: { en: "Three answers for the importer or exporter. Three answers for the broker who clears the shipment. Same workflow.", es: "Tres respuestas para el importador o exportador. Tres respuestas para el agente que despacha el embarque. Mismo flujo." },
  feat1Title: { en: "Upload anything. In any language.", es: "Sube lo que sea. En el idioma que sea." },
  feat1Desc: { en: "PDFs, scans, WhatsApp photos. Spanish, English, Portuguese, Chinese. The AI reads the document so you don't re-key the data.", es: "PDFs, escaneos, fotos de WhatsApp. Español, inglés, portugués, chino. La IA lee el documento para que no tengas que volver a capturar los datos." },
  feat2Title: { en: "Cheapest legal payment route, every time", es: "La ruta de pago más barata y legal, cada vez" },
  feat2Desc: { en: "We compare bank wire, stablecoin (USDC), and alternatives — and show you the savings in dollars before you settle. You execute through your bank or wallet; Puente shows the route.", es: "Comparamos transferencia bancaria, stablecoin (USDC) y alternativas — y te mostramos el ahorro en dólares antes de liquidar. Tú ejecutas con tu banco o billetera; Puente te muestra la ruta." },
  feat3Title: { en: "Compliance gaps before the shipment moves", es: "Faltantes de cumplimiento antes de que el embarque salga" },
  feat3Desc: { en: "Required documents per corridor and per direction — US↔Colombia, US↔Mexico, US↔Dominican Republic, US↔Peru. We flag what's missing before customs does.", es: "Documentos requeridos por corredor y por dirección — EE. UU.↔Colombia, EE. UU.↔México, EE. UU.↔República Dominicana, EE. UU.↔Perú. Señalamos lo que falta antes de que aduanas lo haga." },
  feat4Title: { en: "White-label intelligence for licensed brokers", es: "Inteligencia para agentes aduanales con licencia, marca blanca" },
  feat4Desc: { en: "Carlos clears 20–50 SME files at once. Puente reads the documents, classifies the line items, and flags the edge cases — so you spend your hours on the complex shipments, not on retyping invoice fields. Broker-augmentation, not broker-replacement.", es: "Carlos despacha de 20 a 50 expedientes a la vez. Puente lee los documentos, clasifica las partidas y señala los casos límite — para que dediques tus horas a los embarques complejos, no a recapturar facturas. Aumentamos al agente, no lo reemplazamos." },
  feat5Title: { en: "Fraud risk, scored 0–100", es: "Riesgo de fraude, calificado 0–100" },
  feat5Desc: { en: "Counterparty patterns, amount anomalies, corridor risk, document consistency. Plain-English (or plain-Spanish) explanation of every flag — not a black box.", es: "Patrones de contraparte, anomalías de monto, riesgo del corredor, consistencia documental. Explicación en español (o inglés) sencillo de cada señal — sin caja negra." },
  feat6Title: { en: "Spanish first. Not translated.", es: "En español de verdad. No traducido." },
  feat6Desc: { en: "The interface, the AI prompts, and the customer support thread are written in Spanish from the start. The product was built by a team that speaks the language — not localized after the fact.", es: "La interfaz, los prompts de IA y el soporte se escriben en español desde el principio. El producto lo construye un equipo que habla el idioma — no se localiza al final." },
  ctaTitle: { en: "Run one document through Puente. See what 15 seconds tells you.", es: "Pasa un documento por Puente. Mira lo que te dicen 15 segundos." },
  ctaDesc: { en: "No credit card. No phone call. Upload an invoice or a manifest, in English or Spanish, and see the extraction, the compliance check, the fraud score, and the recommended payment route — in under a minute.", es: "Sin tarjeta. Sin llamada. Sube una factura o un manifiesto, en inglés o en español, y mira la extracción, el control de cumplimiento, el puntaje de fraude y la ruta de pago recomendada — en menos de un minuto." },
  ctaButton: { en: "Analyze a document", es: "Analizar un documento" },
  demoDataBadge: { en: "Sample data — your live numbers will appear after your first analysis", es: "Datos de ejemplo — tus cifras reales aparecerán después de tu primer análisis" },
  founderQuoteEn: { en: "I watched immigrant business owners in Miami lose thousands per shipment to wire fees and customs errors. They knew what they were buying, they knew what it was worth, and the system charged them for the privilege of moving their own money. Puente AI is the tool I wish they had when I was selling to them.", es: "Vi a dueños de negocios inmigrantes en Miami perder miles de dólares por envío en transferencias y errores aduanales. Sabían qué estaban comprando, sabían cuánto valía, y el sistema les cobraba por el privilegio de mover su propio dinero. Puente AI es la herramienta que ojalá hubieran tenido cuando yo les vendía." },
  founderAttribution: { en: "— Jay Alexander, founder", es: "— Jay Alexander, fundador" },
  founderSectionTitle: { en: "Why we built this", es: "Por qué lo construimos" },

  // Explorer page
  explorerTitle: { en: "Market Explorer", es: "Explorador de Mercado" },
  explorerDesc: { en: "Search products, HS codes, and countries across LATAM markets", es: "Busca productos, códigos HS y países en mercados de LATAM" },
  searchPlaceholder: { en: "Search by product name or HS code…", es: "Buscar por nombre de producto o código HS…" },
  allCountries: { en: "All Countries", es: "Todos los Países" },
  noResults: { en: "No results found. Try a different search term or country.", es: "Sin resultados. Prueba con otro término de búsqueda o país." },
  riskLabel: { en: "risk", es: "riesgo" },

  // Insights page
  insightsTitle: { en: "AI Insights", es: "IA Insights" },
  insightsDesc: { en: "Intelligent trade recommendations powered by market analysis", es: "Recomendaciones comerciales inteligentes basadas en análisis de mercado" },
  allInsights: { en: "All Insights", es: "Todos los Insights" },
  opportunities: { en: "Opportunities", es: "Oportunidades" },
  riskAlerts: { en: "Risk Alerts", es: "Alertas de Riesgo" },
  optimizations: { en: "Optimizations", es: "Optimizaciones" },
  details: { en: "Details", es: "Detalles" },
  confidence: { en: "confidence", es: "confianza" },
  opportunityLabel: { en: "Opportunity", es: "Oportunidad" },
  riskAlertLabel: { en: "Risk Alert", es: "Alerta de Riesgo" },
  optimizationLabel: { en: "Optimization", es: "Optimización" },

  // Insights content
  insight1Title: { en: "Colombian Coffee Imports Trending Up", es: "Importaciones de Café Colombiano en Alza" },
  insight1Desc: { en: "Coffee imports from Colombia have risen 12% this quarter. With the current USD/COP exchange rate favoring buyers, consider increasing purchase volume for Q2.", es: "Las importaciones de café de Colombia han subido 12% este trimestre. Con la tasa USD/COP actual favoreciendo compradores, considera aumentar el volumen de compra para Q2." },
  insight2Title: { en: "New Tariff on Brazilian Steel — April 1", es: "Nuevo Arancel al Acero Brasileño — 1 de Abril" },
  insight2Desc: { en: "The US is imposing a 15% tariff increase on Brazilian steel imports (HS 7206-7229). Pre-ship existing orders before the deadline to avoid $180K+ in additional duties.", es: "EE.UU. impondrá un aumento de 15% en aranceles al acero brasileño (HS 7206-7229). Envía los pedidos existentes antes de la fecha límite para evitar $180K+ en aranceles adicionales." },
  insight3Title: { en: "Emerging Route: Lima → Miami Fresh Produce", es: "Ruta Emergente: Lima → Miami Productos Frescos" },
  insight3Desc: { en: "Peruvian fresh produce exports to Miami have grown 34% YoY. Avocados, blueberries, and asparagus lead the surge. Low tariff rates under the US-Peru TPA.", es: "Las exportaciones de productos frescos de Perú a Miami han crecido 34% interanual. Aguacates, arándanos y espárragos lideran el auge. Tarifas bajas bajo el TPA US-Perú." },
  insight4Title: { en: "Consolidate Chilean Wine Shipments", es: "Consolida Envíos de Vino Chileno" },
  insight4Desc: { en: "Analysis suggests consolidating your 3 separate Chilean wine shipments into one monthly container could save ~$24K annually in logistics costs.", es: "El análisis sugiere que consolidar tus 3 envíos separados de vino chileno en un contenedor mensual podría ahorrar ~$24K anuales en costos logísticos." },
  insight5Title: { en: "Compliance Update: Ecuador Produce Standards", es: "Actualización de Cumplimiento: Estándares de Productos de Ecuador" },
  insight5Desc: { en: "Ecuador has updated phytosanitary certification requirements for banana and pineapple exports. Ensure all shipments after March 15 include the new Form EC-2026.", es: "Ecuador actualizó los requisitos de certificación fitosanitaria para exportaciones de banana y piña. Asegúrate de que todos los envíos después del 15 de marzo incluyan el nuevo Formulario EC-2026." },

  // Login / Signup
  signInTitle: { en: "Welcome back", es: "Bienvenido de nuevo" },
  signInSubtitle: { en: "Pick up where you left off — your documents, your routes, your transactions.", es: "Continúa donde lo dejaste — tus documentos, tus rutas, tus transacciones." },
  signUpTitle: { en: "Create your Puente account", es: "Crea tu cuenta de Puente" },
  signUpSubtitle: { en: "Free to start. No credit card. Analyze your first document in under a minute.", es: "Empezar es gratis. Sin tarjeta. Analiza tu primer documento en menos de un minuto." },
  loginName: { en: "Full Name", es: "Nombre Completo" },
  loginNamePlaceholder: { en: "Maria Rodriguez", es: "Maria Rodriguez" },
  loginEmail: { en: "Email", es: "Correo Electrónico" },
  loginEmailPlaceholder: { en: "maria@company.com", es: "maria@empresa.com" },
  loginPassword: { en: "Password", es: "Contraseña" },
  forgotPassword: { en: "Forgot password?", es: "¿Olvidaste tu contraseña?" },
  signInButton: { en: "Sign In", es: "Iniciar Sesión" },
  signUpButton: { en: "Create Account", es: "Crear Cuenta" },
  orContinueWith: { en: "or continue with", es: "o continúa con" },
  noAccount: { en: "Don't have an account?", es: "¿No tienes una cuenta?" },
  alreadyHaveAccount: { en: "Already have an account?", es: "¿Ya tienes una cuenta?" },
  signUpLink: { en: "Sign up", es: "Regístrate" },
  signInLink: { en: "Sign in", es: "Inicia sesión" },
  loginTrust: { en: "Built for SMEs and customs brokers in the US–LATAM corridor.", es: "Construido para PyMEs y agentes aduanales del corredor EE. UU.–LATAM." },

  // FAQ
  faqTitle: { en: "Frequently Asked Questions", es: "Preguntas Frecuentes" },
  faq1Q: { en: "Are you a bank? Do you move my money?", es: "¿Son un banco? ¿Mueven mi dinero?" },
  faq1A: { en: "No. Puente AI is a trade intelligence platform. We read your documents, score risk, check compliance, and recommend the cheapest legal payment route. You execute the payment through your existing bank, broker, or wallet. We will roll out direct settlement (V2) only after the relevant licenses (FinCEN MSB in the US, EPE with the BCRD in the Dominican Republic) are filed and approved.", es: "No. Puente AI es una plataforma de inteligencia comercial. Leemos tus documentos, calificamos el riesgo, revisamos el cumplimiento y recomendamos la ruta de pago más barata y legal. Tú ejecutas el pago con tu banco, agente o billetera. La liquidación directa (V2) la habilitaremos solo después de obtener las licencias correspondientes (FinCEN MSB en EE. UU., EPE con el BCRD en República Dominicana)." },
  faq2Q: { en: "How do you calculate the savings number?", es: "¿Cómo calculan el ahorro que muestran?" },
  faq2A: { en: "We compare a baseline traditional bank wire (typical fee 3–7%, plus 5–7 business days settlement) against alternative routes — most often a USDC stablecoin route — and show the dollar difference. The recommendation is exactly that: a recommendation. Real-world rates vary by your bank, your supplier's bank, and the day. We aim to land within 10% of actuals.", es: "Comparamos una transferencia bancaria tradicional como base (comisión típica 3–7%, más 5–7 días hábiles) contra rutas alternativas — usualmente una ruta de stablecoin USDC — y mostramos la diferencia en dólares. La recomendación es eso: una recomendación. Las tarifas reales varían según tu banco, el banco de tu proveedor y el día. Buscamos quedar dentro del 10% de las cifras reales." },
  faq3Q: { en: "How do you verify a supplier or buyer?", es: "¿Cómo verifican a un proveedor o comprador?" },
  faq3A: { en: "We extract counterparty data from the documents you upload, score it against amount anomalies, corridor patterns, and document consistency, and flag anything unusual with a plain-language explanation. We do not maintain a global supplier registry, and we do not represent that any counterparty is 'verified' beyond what the documents show. Sanctions screening (Phase 3) is a planned capability, not yet live.", es: "Extraemos los datos de la contraparte de los documentos que subes, los calificamos contra anomalías de monto, patrones del corredor y consistencia documental, y señalamos cualquier cosa inusual con una explicación en lenguaje sencillo. No mantenemos un registro global de proveedores y no afirmamos que una contraparte esté 'verificada' más allá de lo que muestran los documentos. La revisión de sanciones (Fase 3) es una capacidad planeada, todavía no activa." },
  faq4Q: { en: "Is this legal? Stablecoin payments, AI-driven compliance — what's the regulatory story?", es: "¿Esto es legal? Pagos en stablecoin, cumplimiento por IA — ¿cuál es la historia regulatoria?" },
  faq4A: { en: "V1 (today) is a recommendations layer — fully legal as a software product, the same way an FX comparison site is legal. V2 (settlement execution) requires money-transmission licensing: we are pursuing FinCEN MSB registration in the US, Florida MTL state-level licensing, and EPE registration with the BCRD in the Dominican Republic before any direct money movement goes live. Until those are complete, settlement happens through your existing rails — not through Puente.", es: "V1 (hoy) es una capa de recomendaciones — legal como producto de software, igual que un comparador de tipos de cambio. V2 (ejecución de pagos) requiere licencias de transmisión de dinero: estamos tramitando el registro MSB ante FinCEN en EE. UU., la licencia MTL del estado de Florida, y el registro como EPE ante el BCRD en República Dominicana antes de habilitar movimiento de dinero directo. Hasta entonces, la liquidación se hace por tus rieles actuales — no por Puente." },
  faq5Q: { en: "Is my data safe?", es: "¿Mis datos están seguros?" },
  faq5A: { en: "Every customer's documents and analysis are isolated by user ID — your invoices live in a path the rest of our customer base cannot read. We use Firebase Auth (Google Identity Platform) for sign-in, and JSON Web Tokens for every API call. Document storage is on Google Cloud Storage in the United States. We do not sell data, we do not share data with third parties beyond the AI providers needed to process the document, and we delete documents on request.", es: "Los documentos y análisis de cada cliente están aislados por ID de usuario — tus facturas viven en una ruta que el resto de nuestros clientes no puede leer. Usamos Firebase Auth (Google Identity Platform) para iniciar sesión y JSON Web Tokens en cada llamada a la API. El almacenamiento documental está en Google Cloud Storage en Estados Unidos. No vendemos datos, no los compartimos con terceros más allá de los proveedores de IA necesarios para procesar el documento, y los borramos a petición." },
  faq6Q: { en: "Do I need to change banks or brokers?", es: "¿Tengo que cambiar de banco o de agente aduanal?" },
  faq6A: { en: "No. Puente works alongside your current bank, your current broker, and your current freight forwarder. If you have a customs broker you trust, we make their job faster — we don't replace them. If you have a banking relationship that's giving you 1.5% on wires (rare), keep it; we'll tell you when it's the right route. We add intelligence; we don't ask you to rip and replace.", es: "No. Puente funciona junto a tu banco, tu agente aduanal y tu agente de carga actuales. Si tienes un agente aduanal de confianza, le aceleramos el trabajo — no lo reemplazamos. Si tu banco te cobra 1.5% en transferencias (poco común), quédate con él; te diremos cuando esa sea la mejor ruta. Sumamos inteligencia; no te pedimos que cambies todo." },

  // Hardcoded → i18n migrations
  analyzeRequestFailed: { en: "Analysis failed — check your connection and try again", es: "El análisis falló — revisa tu conexión e intenta de nuevo" },
  retry: { en: "Try again", es: "Intentar de nuevo" },
  resetPasswordTitle: { en: "Reset your password", es: "Restablece tu contraseña" },
  resetPasswordSubtitle: { en: "Choose a new password for your account.", es: "Elige una nueva contraseña para tu cuenta." },
  resetPasswordSuccessTitle: { en: "Your password has been updated.", es: "Tu contraseña fue actualizada." },
  resetPasswordSuccessMsg: { en: "Password updated successfully.", es: "Contraseña actualizada correctamente." },
  resetPasswordContinue: { en: "Continue to sign in", es: "Continuar a iniciar sesión" },
  resetPasswordNewLabel: { en: "New password", es: "Nueva contraseña" },
  resetPasswordSubmit: { en: "Update password", es: "Actualizar contraseña" },
  resetPasswordBack: { en: "Back to sign in", es: "Volver a iniciar sesión" },
  resetPasswordMissingCode: { en: "Missing or invalid reset code.", es: "Código de restablecimiento ausente o inválido." },
  resetPasswordMinLength: { en: "Password must be at least 6 characters.", es: "La contraseña debe tener al menos 6 caracteres." },
  notFoundTitle: { en: "That page doesn't exist.", es: "Esa página no existe." },
  notFoundDesc: { en: "Maybe you came in from an old link, or maybe we moved something. Head back home and we'll get you to where you were going.", es: "Tal vez llegaste por un enlace viejo, o tal vez movimos algo. Vuelve al inicio y te llevamos a donde ibas." },
  notFoundCta: { en: "Back to home", es: "Volver al inicio" },

  // SEO
  seoTitle: { en: "Puente AI | Compare LATAM Supplier Payment Routes Before You Send", es: "Puente AI | Compara rutas de pago a proveedores en LATAM antes de enviar" },
  seoDesc: { en: "Upload an invoice and compare cross-border payment options by cost, speed, and risk signals. Built for US importers paying LATAM suppliers.", es: "Sube una factura y compara opciones de pago internacional por costo, velocidad y señales de riesgo. Para importadores de EE.UU. que pagan proveedores en LATAM." },

  // About page
  about: { en: "About", es: "Nosotros" },
  aboutSeoTitle: { en: "About Puente AI | Trade Intelligence, US–LATAM", es: "Sobre Puente AI | Inteligencia comercial EE.UU.–LATAM" },
  aboutSeoDesc: { en: "Puente AI is the trade intelligence layer for US–LATAM importers and exporters. Score fraud, check compliance, and find the cheapest legal payment route in ~15s.", es: "Puente AI es la capa de inteligencia comercial para importadores y exportadores EE.UU.–LATAM. Califica fraude, revisa cumplimiento y encuentra la ruta de pago más barata y legal en ~15s." },
  aboutOgImageAlt: { en: "Puente AI — trade intelligence for the US–LATAM corridor", es: "Puente AI — inteligencia comercial para el corredor EE.UU.–LATAM" },
  aboutHeroEyebrow: { en: "About Puente AI", es: "Sobre Puente AI" },
  aboutHeroTitle1: { en: "The trade intelligence layer for the", es: "La capa de inteligencia comercial del" },
  aboutHeroTitle2: { en: "US–LATAM corridor.", es: "corredor EE.UU.–LATAM." },
  aboutHeroSub: { en: "Pay less. Move faster. Built for the importers and exporters who keep Miami connected to the rest of the Americas.", es: "Paga menos. Muévete más rápido. Hecho para los importadores y exportadores que mantienen a Miami conectado con el resto de las Américas." },

  aboutMissionTitle: { en: "Our mission", es: "Nuestra misión" },
  aboutMissionBody: { en: "Cross-border trade between the United States and Latin America still runs on slow wires, opaque fees, and paperwork that gets re-typed by hand. We think importers and exporters deserve better. Puente AI reads your trade documents in about 15 seconds, scores fraud risk, flags compliance gaps, and tells you the cheapest legal way to pay — in dollars, before anything moves.", es: "El comercio entre Estados Unidos y América Latina todavía corre sobre transferencias lentas, comisiones opacas y papeleo que se re-escribe a mano. Creemos que los importadores y exportadores merecen algo mejor. Puente AI lee tus documentos comerciales en unos 15 segundos, califica el riesgo de fraude, marca brechas de cumplimiento y te dice la forma legal más barata de pagar — en dólares, antes de mover nada." },

  aboutWhoTitle: { en: "Who we serve", es: "A quién servimos" },
  aboutWhoBody: { en: "We serve two co-equal users on every shipment: Maria, the bilingual Miami SME owner moving goods north-to-south, and her counterpart in Bogotá, Santo Domingo, or São Paulo moving goods the other way. Our product is built for non-technical operators who want clarity, not jargon.", es: "Servimos a dos usuarios igual de importantes en cada envío: Maria, la dueña bilingüe de una pyme en Miami que mueve mercancía de norte a sur, y su contraparte en Bogotá, Santo Domingo o São Paulo que mueve mercancía en sentido contrario. Nuestro producto está hecho para operadores no técnicos que quieren claridad, no jerga." },

  aboutApproachTitle: { en: "How we work", es: "Cómo trabajamos" },
  aboutApproachBody: { en: "We are a trade intelligence platform — not a bank and not a money transmitter. We do not move your funds. We read documents, score risk, and recommend the cheapest legal route; you execute through your existing bank, broker, or wallet. Direct settlement (V2) will only ship after the relevant licenses are filed and approved.", es: "Somos una plataforma de inteligencia comercial — no un banco ni un transmisor de dinero. No movemos tus fondos. Leemos documentos, calificamos riesgo y recomendamos la ruta más barata y legal; tú ejecutas con tu banco, agente o billetera. La liquidación directa (V2) solo se lanzará después de obtener las licencias correspondientes." },

  aboutValuesTitle: { en: "What we believe", es: "En qué creemos" },
  aboutValue1Title: { en: "Honesty over hype", es: "Honestidad antes que ruido" },
  aboutValue1Body: { en: "We show real numbers, real limitations, and real timelines. No fabricated customers, no claimed licenses we don't have.", es: "Mostramos números reales, limitaciones reales y plazos reales. Sin clientes inventados ni licencias que no tengamos." },
  aboutValue2Title: { en: "Augment, don't replace", es: "Sumar, no reemplazar" },
  aboutValue2Body: { en: "Your customs broker, your bank, your freight forwarder — keep them. We make their work faster and your decisions sharper.", es: "Tu agente aduanal, tu banco, tu agente de carga — quédate con ellos. Hacemos su trabajo más rápido y tus decisiones más certeras." },
  aboutValue3Title: { en: "Bilingual by default", es: "Bilingüe por diseño" },
  aboutValue3Body: { en: "English, Spanish, Portuguese. Every screen, every doc, every alert — in the language the operator actually speaks.", es: "Inglés, español, portugués. Cada pantalla, cada documento, cada alerta — en el idioma que el operador realmente habla." },
  aboutValue4Title: { en: "Privacy by isolation", es: "Privacidad por aislamiento" },
  aboutValue4Body: { en: "Your documents live in a path no other customer can read. We don't sell data and we delete on request.", es: "Tus documentos viven en una ruta que ningún otro cliente puede leer. No vendemos datos y los borramos a petición." },

  aboutCtaTitle: { en: "Ready to see it work?", es: "¿Listo para verlo funcionar?" },
  aboutCtaBody: { en: "Upload a real invoice and get a fraud score, compliance check, and payment recommendation in about 15 seconds.", es: "Sube una factura real y obtén una calificación de fraude, revisión de cumplimiento y recomendación de pago en unos 15 segundos." },
  aboutCtaButton: { en: "Start a free analysis", es: "Iniciar un análisis gratis" },

  // Onboarding flow
  onbStepLabel: { en: "Step", es: "Paso" },
  onbOf: { en: "of", es: "de" },
  onbBack: { en: "Back", es: "Atrás" },
  onbContinue: { en: "Continue", es: "Continuar" },
  onbFinish: { en: "Go to dashboard", es: "Ir al panel" },
  onbSkip: { en: "Skip for now", es: "Omitir por ahora" },

  onbWelcomeKicker: { en: "Welcome to Puente AI", es: "Bienvenido a Puente AI" },

  onbLangTitle: { en: "Choose your language", es: "Elige tu idioma" },
  onbLangSubtitle: {
    en: "We'll use this for the dashboard, alerts, and your welcome email.",
    es: "Lo usaremos para el panel, alertas y tu correo de bienvenida.",
  },
  onbLangEn: { en: "English", es: "Inglés" },
  onbLangEs: { en: "Spanish", es: "Español" },

  onbProfileTitle: { en: "Tell us about you", es: "Cuéntanos sobre ti" },
  onbProfileSubtitle: {
    en: "Just the basics — we'll personalize the dashboard.",
    es: "Solo lo esencial — personalizaremos el panel.",
  },
  onbProfileName: { en: "Your name", es: "Tu nombre" },
  onbProfileNamePlaceholder: { en: "Maria Rodriguez", es: "Maria Rodriguez" },
  onbProfileCompany: { en: "Company", es: "Empresa" },
  onbProfileCompanyPlaceholder: { en: "Acme Imports LLC", es: "Importaciones Acme S.A." },

  onbCorridorsTitle: { en: "Which trade corridors do you use?", es: "¿Qué corredores comerciales usas?" },
  onbCorridorsSubtitle: {
    en: "Pick all that apply. We'll prioritize routes and rates for these.",
    es: "Selecciona todos los que apliquen. Priorizaremos rutas y tarifas para estos.",
  },

  onbDoneTitle: { en: "You're all set, {name}", es: "Todo listo, {name}" },
  onbDoneSubtitle: {
    en: "Your dashboard is ready. Run your first analysis whenever you are.",
    es: "Tu panel está listo. Ejecuta tu primer análisis cuando quieras.",
  },
};

type TranslationKey = keyof typeof translations;

interface I18nContextType {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: TranslationKey) => string;
}

const I18nContext = createContext<I18nContextType>({
  lang: "en",
  setLang: () => {},
  t: (key) => translations[key]?.en || key,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => detectLang());

  // Persist explicit language choices so they survive reloads.
  // We write to BOTH localStorage and a cookie so the choice is recoverable
  // even if one of them is unavailable (private mode, third-party blocking, etc.).
  const setLang = (next: Lang) => {
    setLangState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Ignore storage errors (private mode, quota, etc.)
    }
    writeCookie(STORAGE_KEY, next);
  };

  // Keep <html lang> in sync for accessibility & SEO.
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = lang;
    }
  }, [lang]);

  const t = (key: TranslationKey) => translations[key]?.[lang] || key;
  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
