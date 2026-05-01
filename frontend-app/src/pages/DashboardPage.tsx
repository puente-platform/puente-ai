import { useEffect, useState } from "react";
import { useI18n } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";
import { useAuth } from "@/lib/auth";
import { CORRIDOR_OPTIONS, getOnboarding } from "@/lib/onboarding";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight, ShieldCheck, Upload, TrendingUp, TrendingDown } from "lucide-react";
import StatusChip from "@/components/StatusChip";
import { motion } from "framer-motion";

const transactions = [
  { date: "Oct 24, 2024", supplierKey: "supplierAlimentos" as const, subKey: "supplierAlimentosSub" as const, flags: "🇺🇸→🇨🇴", amount: "$14,200", riskKey: "riskLowLabel" as const, riskColor: "text-emerald", status: "routed" as const },
  { date: "Oct 22, 2024", supplierKey: "supplierTejidos" as const, subKey: "supplierTejidosSub" as const, flags: "🇺🇸→🇨🇴", amount: "$8,500", riskKey: "riskMedLabel" as const, riskColor: "text-warm-amber", status: "analyzed" as const },
  { date: "Oct 21, 2024", supplierKey: "supplierSuministros" as const, subKey: "supplierSuministrosSub" as const, flags: "🇺🇸→🇨🇴", amount: "$32,100", riskKey: "riskHighLabel" as const, riskColor: "text-danger-red", status: "failed" as const },
];

const corridorData = [
  { name: "US→Colombia 🇨🇴", value: 42, lightColor: "#B45309", darkColor: "#F59E0B", trend: 8 },
  { name: "US→Mexico 🇲🇽", value: 28, lightColor: "#92400E", darkColor: "#D97706", trend: -3 },
  { name: "US→DR 🇩🇴", value: 18, lightColor: "#D97706", darkColor: "#FBBF24", trend: 12 },
  { name: "US→Brazil 🇧🇷", value: 12, lightColor: "#78350F", darkColor: "#92400E", trend: -1 },
];

export default function DashboardPage() {
  const { t, lang } = useI18n();
  const { theme } = useTheme();
  const { user } = useAuth();
  const isDark = theme === "dark";

  // Pull onboarding profile to personalize the greeting + corridor line.
  // Falls back gracefully if the profile isn't loaded yet (cache miss + slow
  // network) — getOnboarding internally falls back to localStorage on error.
  const [corridors, setCorridors] = useState<string[]>([]);
  useEffect(() => {
    if (!user?.uid) return;
    let cancelled = false;
    getOnboarding(user.uid).then((profile) => {
      if (!cancelled) setCorridors(profile?.corridors ?? []);
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [user?.uid]);

  // Use the first segment of displayName (e.g. "Jay" from "Jay Rodriguez").
  // Firebase displayName can be null (just-signed-up users), in which case we
  // show a name-less fallback greeting rather than the literal "{name}".
  const firstName = user?.displayName?.trim().split(/\s+/)[0] ?? "";
  const greeting = firstName
    ? t("greeting").replace("{name}", firstName)
    : t("greetingFallback");

  // Corridor line: render the first selected corridor's localized label,
  // or a "multiple corridors" / "set your corridors" fallback.
  const corridorLine = (() => {
    if (corridors.length === 0) return t("corridorActiveNone");
    if (corridors.length > 1) return t("corridorActivePlural");
    const opt = CORRIDOR_OPTIONS.find((c) => c.id === corridors[0]);
    const label = opt?.label[lang] ?? corridors[0];
    return t("corridorActive").replace("{corridor}", label);
  })();

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Greeting */}
      <div>
        <h1 className="font-display text-2xl md:text-3xl font-bold">{greeting}</h1>
        <p className="mt-1 flex items-center gap-1.5 text-xs md:text-sm text-muted-foreground">
          <ShieldCheck className="h-4 w-4 text-primary shrink-0" />
          {corridorLine}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 md:gap-4 lg:grid-cols-4">
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-3 md:p-5">
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("transfersMonth")}</p>
            <div className="mt-1.5 md:mt-2 flex items-end gap-2 md:gap-3">
              <span className="text-2xl md:text-3xl font-bold">12</span>
              <span className="text-[10px] md:text-xs font-medium text-primary mb-1">{t("trendUp")}</span>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-3 md:p-5">
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("savedMonth")}</p>
            <div className="mt-1.5 md:mt-2">
              <span className="text-2xl md:text-3xl font-bold text-gradient-gold">$4,280</span>
              <p className="text-[10px] md:text-xs text-muted-foreground mt-0.5">{t("vsWire")}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-3 md:p-5">
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("avgRisk")}</p>
            <div className="mt-1.5 md:mt-2 flex items-center gap-2 md:gap-3">
              <ShieldCheck className="h-5 w-5 md:h-6 md:w-6 text-emerald shrink-0" />
              <div>
                <span className="text-sm md:text-lg font-bold text-emerald">{t("riskLow")}</span>
                <span className="text-xs md:text-sm text-muted-foreground ml-1">(14/100)</span>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-3 md:p-5">
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("pendingDocs")}</p>
            <div className="mt-1.5 md:mt-2 flex items-center gap-2">
              <span className="text-2xl md:text-3xl font-bold">3</span>
              <span className="h-2.5 w-2.5 rounded-full bg-warm-amber animate-pulse"></span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Two-column layout */}
      <div className="grid lg:grid-cols-[1fr_380px] gap-4 md:gap-6">
        {/* Left - Recent Transactions */}
        <Card className="bg-gradient-card border-border overflow-hidden">
          <CardContent className="p-0">
            <div className="flex items-center justify-between px-4 md:px-5 pt-4 md:pt-5 pb-3">
              <h2 className="font-display text-lg font-bold">{t("recentTransactions")}</h2>
              <Link to="/transactions" className="flex items-center gap-1 text-sm font-medium text-primary hover:underline">
                {t("viewAll")} <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm min-w-[520px]">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-3 md:px-5 py-2.5 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("date")}</th>
                    <th className="px-3 md:px-5 py-2.5 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("supplier")}</th>
                    <th className="px-3 md:px-5 py-2.5 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("amount")}</th>
                    <th className="px-3 md:px-5 py-2.5 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("risk")}</th>
                    <th className="px-3 md:px-5 py-2.5 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("status")}</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx, i) => (
                    <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="px-3 md:px-5 py-3 text-muted-foreground whitespace-nowrap">{tx.date}</td>
                      <td className="px-3 md:px-5 py-3">
                        <div className="font-medium">{t(tx.supplierKey)}</div>
                        <div className="text-xs text-muted-foreground">{t(tx.subKey)} · {tx.flags}</div>
                      </td>
                      <td className="px-3 md:px-5 py-3 font-medium whitespace-nowrap">{tx.amount}</td>
                      <td className={`px-3 md:px-5 py-3 text-xs font-semibold ${tx.riskColor}`}>{t(tx.riskKey)}</td>
                      <td className="px-3 md:px-5 py-3"><StatusChip status={tx.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Right column */}
        <div className="space-y-6">
          {/* Upload CTA */}
          <Card className="border-gold-subtle bg-gradient-card glow-gold overflow-hidden">
            <CardContent className="p-6">
              <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center mb-4">
                <Upload className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-display text-xl font-bold flex items-center gap-2">
                {t("uploadCta")} <ArrowRight className="h-5 w-5 text-primary" />
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">{t("uploadCtaDesc")}</p>
              <Button variant="default" size="lg" className="w-full mt-5" asChild>
                <Link to="/analyze">{t("newAnalysisCta")}</Link>
              </Button>
            </CardContent>
          </Card>

          {/* Corridor Breakdown */}
          <Card className="bg-gradient-card border-border">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-5">
                <h3 className="font-display text-base font-bold">{t("corridorBreakdown")}</h3>
                <span className="text-sm font-semibold text-gradient-gold">$54k</span>
              </div>
              <div className="space-y-4">
                {corridorData.map((c, i) => (
                  <div key={c.name} className="group space-y-1.5 cursor-pointer">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground group-hover:text-foreground transition-colors duration-200">{c.name}</span>
                      <div className="flex items-center gap-1.5">
                        <span className="font-medium group-hover:text-foreground transition-colors duration-200">{c.value}%</span>
                        <span className={`flex items-center gap-0.5 text-[11px] font-semibold ${c.trend >= 0 ? 'text-emerald' : 'text-danger-red'}`}>
                          {c.trend >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                          {Math.abs(c.trend)}%
                        </span>
                      </div>
                    </div>
                    <div className="h-2 w-full rounded-full bg-muted overflow-hidden group-hover:h-2.5 transition-all duration-200">
                      <motion.div
                        className="h-full rounded-full transition-shadow duration-200"
                        style={{ backgroundColor: isDark ? c.darkColor : c.lightColor, boxShadow: 'none' }}
                        whileHover={{ boxShadow: `0 0 12px ${isDark ? c.darkColor : c.lightColor}80` }}
                        initial={{ width: 0 }}
                        animate={{ width: `${c.value}%` }}
                        transition={{ duration: 0.8, delay: i * 0.15, ease: [0.25, 0.46, 0.45, 0.94] }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
