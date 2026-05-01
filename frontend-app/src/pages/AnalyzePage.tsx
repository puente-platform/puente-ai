import { useState, useRef } from "react";
import { useI18n } from "@/lib/i18n";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Check, Loader2, ShieldCheck, AlertTriangle, ArrowRight } from "lucide-react";
import {
  uploadDocument, analyzeDocument, routeDocument,
  type AnalyzeResponse, type RoutingResponse,
} from "@/lib/puente-api";

type Step = 1 | 2 | 3;

export default function AnalyzePage() {
  const { t } = useI18n();
  const [step, setStep] = useState<Step>(1);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [analysisData, setAnalysisData] = useState<AnalyzeResponse | null>(null);
  const [routingData, setRoutingData] = useState<RoutingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (file: File) => {
    setStep(2);
    setPipelineStep(0);
    setError(null);

    try {
      // Step 1: Upload
      setPipelineStep(1);
      const uploadRes = await uploadDocument(file);
      const docId = uploadRes.document_id;

      // Step 2: Analyze
      setPipelineStep(2);
      const analyzeRes = await analyzeDocument(docId);
      setAnalysisData(analyzeRes);

      // Step 3: Route
      setPipelineStep(3);
      const amount = computeInvoiceAmount(analyzeRes);
      let routingRes: RoutingResponse | null = null;
      try {
        routingRes = await routeDocument(docId, amount);
      } catch (routingErr) {
        // Backend often rejects routing if it can't find an amount.
        // Fall back to the routing_recommendation embedded in analyze.
        console.warn("Routing endpoint failed, using analyze fallback:", routingErr);
        routingRes = routingFromAnalysis(analyzeRes, amount);
      }
      setRoutingData(routingRes);

      // Done
      setPipelineStep(4);
      setTimeout(() => setStep(3), 600);
    } catch (err) {
      console.error("API error:", err);
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setStep(1);
      setPipelineStep(0);
    }
  };

  const onUploadClick = () => fileInputRef.current?.click();

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  };

  const onRetry = () => {
    setError(null);
    fileInputRef.current?.click();
  };

  const pipelineNodes = [
    { key: "uploaded", label: t("pipelineUploaded") },
    { key: "extracting", label: t("pipelineExtracting") },
    { key: "analyzing", label: t("pipelineAnalyzing") },
    { key: "routing", label: t("pipelineRouting") },
  ];

  const steps = [
    { num: 1, label: t("step1") },
    { num: 2, label: t("step2") },
    { num: 3, label: t("step3") },
  ];

  return (
    <div className="max-w-[900px] mx-auto space-y-6 md:space-y-8">
      {/* Hidden file input */}
      <input ref={fileInputRef} type="file" accept=".pdf" className="hidden" onChange={onFileChange} />

      {/* Progress bar */}
      <div className="flex items-center justify-center gap-0">
        {steps.map((s, i) => (
          <div key={s.num} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`h-8 w-8 md:h-10 md:w-10 rounded-full flex items-center justify-center text-xs md:text-sm font-bold transition-all ${
                  step > s.num
                    ? "bg-primary text-primary-foreground"
                    : step === s.num
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                }`}
              >
                {step > s.num ? <Check className="h-4 w-4 md:h-5 md:w-5" /> : s.num}
              </div>
              <span className={`mt-1 md:mt-1.5 text-[10px] md:text-xs font-medium uppercase tracking-wider ${step >= s.num ? "text-primary" : "text-muted-foreground"}`}>
                {s.label}
              </span>
            </div>
            {i < 2 && (
              <div className={`w-12 md:w-[120px] h-0.5 mx-2 md:mx-4 mt-[-18px] ${step > s.num ? "bg-primary" : "bg-muted"}`} />
            )}
          </div>
        ))}
      </div>

      {/* Error state */}
      {error && step === 1 && (
        <Card className="border-danger-red/40 bg-danger-red/5">
          <CardContent className="p-5 space-y-3">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-danger-red shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-danger-red">{t("analyzeRequestFailed")}</p>
                <p className="text-sm text-muted-foreground mt-1 break-words">{error}</p>
              </div>
            </div>
            <Button onClick={onRetry} variant="default">{t("retry")}</Button>
          </CardContent>
        </Card>
      )}

      {/* Step 1 - Upload */}
      {step === 1 && (
        <div className="flex justify-center px-2">
          <div
            onClick={onUploadClick}
            onDrop={onDrop}
            onDragOver={(e) => e.preventDefault()}
            className="w-full max-w-[680px] h-[200px] md:h-[280px] border-2 border-dashed border-primary/40 rounded-xl flex flex-col items-center justify-center gap-2 md:gap-3 cursor-pointer hover:bg-primary/5 hover:border-primary/60 transition-all duration-300 px-4"
          >
            <Upload className="h-10 w-10 md:h-12 md:w-12 text-primary" />
            <p className="text-base md:text-lg font-display font-bold text-center">{t("uploadTitle")}</p>
            <p className="text-xs md:text-sm text-muted-foreground text-center">{t("uploadSub")}</p>
            <p className="text-xs md:text-sm text-muted-foreground">{t("uploadOr")}</p>
          </div>
        </div>
      )}

      {/* Step 2 - Processing */}
      {step === 2 && (
        <div className="text-center space-y-6 md:space-y-8">
          <div className="flex items-center justify-center gap-2 md:gap-4 flex-wrap">
            {pipelineNodes.map((node, i) => (
              <div key={node.key} className="flex items-center gap-2 md:gap-4">
                <div className="flex flex-col items-center gap-1 md:gap-1.5">
                  <div
                    className={`h-8 w-8 md:h-10 md:w-10 rounded-full flex items-center justify-center transition-all ${
                      i < pipelineStep
                        ? "bg-primary text-primary-foreground"
                        : i === pipelineStep
                          ? "bg-primary text-primary-foreground pill-pulse"
                          : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {i < pipelineStep ? <Check className="h-3.5 w-3.5 md:h-4 md:w-4" /> : i === pipelineStep ? <Loader2 className="h-3.5 w-3.5 md:h-4 md:w-4 animate-spin" /> : <span className="text-[10px] md:text-xs">{i + 1}</span>}
                  </div>
                  <span className="text-[9px] md:text-[11px] font-medium text-muted-foreground">
                    {node.label}
                  </span>
                </div>
                {i < 3 && <div className={`w-4 md:w-8 h-0.5 mt-[-18px] ${i < pipelineStep ? "bg-primary" : "bg-muted"}`} />}
              </div>
            ))}
          </div>
          <div>
            <Loader2 className="h-6 w-6 animate-spin text-primary mx-auto" />
            <p className="mt-3 text-xs md:text-sm text-muted-foreground">{t("processingTime")}</p>
            <p className="mt-1 text-[10px] md:text-xs text-muted-foreground">{t("processingTrust")}</p>
          </div>
        </div>
      )}

      {/* Step 3 - Results */}
      {step === 3 && analysisData && routingData && (
        <ResultsView analysis={analysisData} routing={routingData} />
      )}
    </div>
  );
}

function parseAmount(v: unknown): number {
  if (typeof v === "number") return v;
  if (v && typeof v === "object" && "value" in (v as Record<string, unknown>)) {
    return parseAmount((v as Record<string, unknown>).value);
  }
  if (typeof v === "string") {
    const n = parseFloat(v.replace(/[^0-9.\-]/g, ""));
    return Number.isFinite(n) ? n : 0;
  }
  return 0;
}

function fieldString(v: unknown): string | undefined {
  if (v == null) return undefined;
  if (typeof v === "string") return v;
  if (typeof v === "number") return String(v);
  if (typeof v === "object" && "value" in (v as Record<string, unknown>)) {
    return fieldString((v as Record<string, unknown>).value);
  }
  return undefined;
}

function computeInvoiceAmount(a: AnalyzeResponse): number {
  const fields = a.extraction?.fields as Record<string, unknown> | undefined;
  const direct = fields ? parseAmount(fields["total_amount"] ?? fields["invoice_amount"] ?? fields["total"]) : 0;
  if (direct > 0) return direct;
  const items = a.extraction?.line_items ?? [];
  return items.reduce((sum, li) => sum + parseAmount(li.amount), 0);
}

function routingFromAnalysis(a: AnalyzeResponse, _amount: number): RoutingResponse {
  // Fall back to whatever the analyze response's routing_recommendation block
  // contains. If the backend produced no recommendation (typically because
  // country of origin / corridor weren't extracted with confidence — see the
  // pending Document AI extraction-upgrade ticket), return an empty routes
  // array so the UI can show an honest "data unavailable" card instead of
  // synthesizing fake $500 / $125 fallback numbers.
  const r = a.analysis?.routing_recommendation;
  if (!r || (r.traditional_cost_usd == null && r.puente_cost_usd == null)) {
    return {
      document_id: a.document_id,
      savings: 0,
      routes: [],
    };
  }
  const traditional = r.traditional_cost_usd ?? 0;
  const puente = r.puente_cost_usd ?? 0;
  const puenteDays = r.puente_days ?? 1;
  const traditionalDays = r.traditional_days ?? 3;
  return {
    document_id: a.document_id,
    savings: r.savings_usd ?? Math.max(traditional - puente, 0),
    routes: [
      {
        provider: "Puente USDC",
        fee: puente,
        delivery_time: `__DAYS__:${puenteDays}`,
        recommended: true,
      },
      {
        provider: r.recommended_method ?? "__WIRE_TRANSFER__",
        fee: traditional,
        delivery_time: `__DAYS__:${traditionalDays}`,
        recommended: false,
      },
    ],
  };
}

function ResultsView({ analysis, routing }: { analysis: AnalyzeResponse; routing: RoutingResponse }) {
  const { t } = useI18n();

  const fraud = analysis.analysis?.fraud_assessment;
  const comp = analysis.analysis?.compliance_assessment;
  const fields = analysis.extraction?.fields as Record<string, unknown> | undefined;

  const fraudScore = fraud?.score ?? 0;
  const fraudFlags = fraud?.flags ?? [];
  const supplierName = fieldString(fields?.["exporter_name"]) ?? fieldString(fields?.["supplier_name"]) ?? t("unknownSupplier");
  const corridor = comp?.corridor && comp.corridor !== "Unknown" ? comp.corridor : "—";
  const invoiceAmount = computeInvoiceAmount(analysis);
  const currency = fieldString(fields?.["currency"]) ?? "USD";

  const savings = routing.savings ?? 0;
  const routes = routing.routes ?? [];

  // Detect "routing data unavailable" — backend returned no usable routing
  // recommendation (typically because seller_country / corridor wasn't
  // extracted, so the routing engine fell to _DEFAULT_CORRIDOR with $0
  // savings). Render an honest fallback card instead of misleading $0
  // savings + RECOMMENDED badge with synthesized numbers.
  const routingUnavailable = routes.length === 0 || (savings === 0 && corridor === "—");

  const isLowRisk = fraudScore < 40;
  const riskColor = isLowRisk ? "text-emerald" : fraudScore < 70 ? "text-warm-amber" : "text-danger-red";
  const riskBg = isLowRisk ? "bg-emerald/15" : fraudScore < 70 ? "bg-warm-amber/15" : "bg-danger-red/15";
  const strokeColor = isLowRisk ? "hsl(160,91%,31%)" : fraudScore < 70 ? "hsl(38,92%,50%)" : "hsl(0,84%,60%)";

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Invoice Header */}
      <Card className="bg-gradient-card border-gold-subtle">
        <CardContent className="p-4 md:p-5 grid grid-cols-2 md:flex md:flex-wrap md:items-center md:justify-between gap-3 md:gap-4">
          <div>
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("selectedSupplier")}</p>
            <p className="text-base md:text-xl font-display font-bold">{supplierName}</p>
          </div>
          <div>
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("tradeCorridor")}</p>
            <p className="text-sm md:text-lg font-medium">{corridor}</p>
          </div>
          <div>
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("invoiceAmount")}</p>
            <p className="text-xl md:text-2xl font-bold text-primary">${invoiceAmount.toLocaleString()} <span className="text-xs md:text-sm font-normal text-muted-foreground">{currency}</span></p>
          </div>
          <span className="inline-flex px-3 py-1 rounded-full bg-ocean/15 text-ocean text-xs font-medium self-start">{t("analyzed")}</span>
        </CardContent>
      </Card>

      {/* Three Result Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Fraud Risk */}
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-4 md:p-5 text-center">
            <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase mb-3 md:mb-4">{t("fraudRisk")}</p>
            <div className="relative mx-auto w-[100px] h-[100px] md:w-[120px] md:h-[120px]">
              <svg viewBox="0 0 120 120" className="w-full h-full">
                <circle cx="60" cy="60" r="50" fill="none" stroke="hsl(215,25%,14%)" strokeWidth="8" />
                <circle cx="60" cy="60" r="50" fill="none" stroke={strokeColor} strokeWidth="8" strokeDasharray={`${fraudScore * 3.14} ${100 * 3.14}`} strokeLinecap="round" transform="rotate(-90 60 60)" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-3xl md:text-4xl font-bold ${riskColor}`}>{fraudScore}</span>
                <span className="text-[10px] text-muted-foreground">{t("outOf100")}</span>
              </div>
            </div>
            <div className="mt-3">
              <span className={`inline-flex px-3 py-1 rounded-full ${riskBg} ${riskColor} text-xs font-semibold`}>
                <ShieldCheck className="h-3 w-3 mr-1" /> {isLowRisk ? t("lowRisk") : `${fraudScore}/100`}
              </span>
            </div>
            <div className="mt-3 md:mt-4 space-y-2 text-left text-sm">
              {fraudFlags.length === 0 && (
                <>
                  <div className="flex items-center gap-2 text-emerald">
                    <Check className="h-4 w-4 shrink-0" /> {t("noAlerts")}
                  </div>
                  <div className="flex items-center gap-2 text-emerald">
                    <Check className="h-4 w-4 shrink-0" /> {t("cleanHistory")}
                  </div>
                </>
              )}
              {fraudFlags.slice(0, 4).map((alert, i) => (
                <div key={i} className="flex items-center gap-2 text-warm-amber">
                  <AlertTriangle className="h-4 w-4 shrink-0" /> {alert}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Compliance */}
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-4 md:p-5">
            <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase mb-3 md:mb-4">{t("compliance")}</p>
            {(() => {
              const lvl = (comp?.level ?? "").toUpperCase();
              const isHigh = lvl.includes("HIGH");
              const isMed = lvl.includes("MED");
              const cls = isHigh ? "bg-danger-red/15 text-danger-red" : isMed ? "bg-warm-amber/15 text-warm-amber" : "bg-emerald/15 text-emerald";
              const label = isHigh ? t("riskHigh") : isMed ? t("riskMedium") : t("compliancePass");
              return (
                <span className={`inline-flex px-3 py-1 rounded-full ${cls} text-xs font-semibold mb-3`}>{label}</span>
              );
            })()}
            <div className="mt-3 rounded-lg bg-muted p-3 mb-3 md:mb-4">
              <p className="text-[10px] font-semibold tracking-wider text-muted-foreground uppercase">{t("corridor")}</p>
              <p className="text-sm font-medium mt-0.5">{comp?.corridor && comp.corridor !== "Unknown" ? comp.corridor : "—"}</p>
            </div>
            <div className="space-y-2.5 md:space-y-3 text-sm">
              {(comp?.flags ?? []).slice(0, 4).map((flag, i) => (
                <div key={`f-${i}`} className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-warm-amber shrink-0 mt-0.5" />
                  <span className="text-xs text-muted-foreground">{flag}</span>
                </div>
              ))}
              {(comp?.missing_documents ?? []).slice(0, 3).map((doc, i) => (
                <div key={`m-${i}`} className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-danger-red shrink-0 mt-0.5" />
                  <span className="text-xs text-muted-foreground">{t("missingPrefix")}: {doc}</span>
                </div>
              ))}
              {(!comp?.flags || comp.flags.length === 0) && (!comp?.missing_documents || comp.missing_documents.length === 0) && (
                <div className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-emerald shrink-0 mt-0.5" />
                  <span className="text-xs text-muted-foreground">{t("ofacDesc")}</span>
                </div>
              )}
            </div>
            <button className="mt-3 md:mt-4 text-sm font-medium text-primary hover:underline flex items-center gap-1">
              {t("viewDetails")} <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </CardContent>
        </Card>

        {/* Payment Routing — honest "data unavailable" fallback when backend
            couldn't compute (typically because seller_country wasn't
            extracted). Drops the misleading RECOMMENDED badge + $0. */}
        {routingUnavailable ? (
          <Card className="border-border bg-gradient-card">
            <CardContent className="p-4 md:p-5">
              <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("paymentOpt")}</p>
              <div className="mt-3 mb-3 flex items-start gap-2">
                <AlertTriangle className="h-5 w-5 text-warm-amber shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-display font-bold">{t("routingUnavailableTitle")}</p>
                  <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
                    {t("routingUnavailableBody")}
                  </p>
                </div>
              </div>
              <Button variant="outline" size="lg" className="w-full mt-3" onClick={() => window.location.reload()}>
                {t("routingUnavailableCta")}
              </Button>
            </CardContent>
          </Card>
        ) : (
        <Card className="border-gold-subtle glow-gold relative">
          <div className="absolute -top-3 right-4">
            <span className="inline-flex px-3 py-1 rounded-full bg-primary text-primary-foreground text-[10px] font-bold uppercase tracking-wider">
              {t("recommended")}
            </span>
          </div>
          <CardContent className="p-4 md:p-5 pt-6 bg-gradient-card rounded-lg">
            <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("paymentOpt")}</p>
            <p className="text-xs text-muted-foreground mt-1">{t("totalSavings")}</p>
            <div className="mt-2 mb-3 md:mb-4">
              <span className="text-sm text-emerald font-medium">{t("youSave")}</span>
              <span className="ml-1 text-[10px] text-muted-foreground">{currency}</span>
              <div className="text-emerald font-bold leading-none text-[44px] md:text-[56px]">
                ${savings.toLocaleString()}
              </div>
            </div>

            <div className="space-y-0 border border-border rounded-lg overflow-hidden">
              {routes.map((route, i) => {
                const localizedProvider = route.provider === "__WIRE_TRANSFER__" ? t("wireTransfer") : route.provider;
                const daysMatch = typeof route.delivery_time === "string" && route.delivery_time.startsWith("__DAYS__:")
                  ? Number(route.delivery_time.slice("__DAYS__:".length))
                  : null;
                const localizedDelivery = daysMatch !== null
                  ? `${daysMatch} ${daysMatch === 1 ? t("daySingular") : t("dayPlural")}`
                  : route.delivery_time;
                return (
                  <div key={i} className={`flex items-center justify-between p-3 ${i === 0 ? "bg-muted/50" : "border-t border-border"}`}>
                    <div>
                      <p className="text-[11px] md:text-xs font-bold uppercase">{localizedProvider}</p>
                      <p className={`text-[10px] ${route.recommended ? "text-emerald" : route === routes[routes.length - 1] ? "text-danger-red font-semibold" : "text-muted-foreground"}`}>
                        {route.recommended ? (t("sameDay")) : route === routes[routes.length - 1] ? t("mostExpensive") : ""}
                        {localizedDelivery && !route.recommended && ` ${localizedDelivery}`}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`text-base md:text-lg ${route.recommended ? "font-bold text-primary" : "font-medium text-muted-foreground"}`}>${route.fee}</p>
                      {route.recommended && <p className="text-[10px] text-muted-foreground uppercase">{t("commission")}</p>}
                    </div>
                  </div>
                );
              })}
            </div>

            <Button variant="default" size="lg" className="w-full mt-4">
              {t("viewDetails")}
            </Button>
            <button className="w-full mt-2 text-xs font-medium text-muted-foreground uppercase tracking-wider hover:text-primary text-center">
              {t("saveHistory")}
            </button>
          </CardContent>
        </Card>
        )}
      </div>
    </div>
  );
}
