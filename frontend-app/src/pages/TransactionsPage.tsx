import { useI18n } from "@/lib/i18n";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Check, AlertTriangle, MoreVertical } from "lucide-react";
import { useState } from "react";

const txData = [
  { date: "12 Oct", supplierKey: "supplierAlimentos" as const, subKey: "supplierAlimentosSub" as const, invoice: "INV-84920-AC", flags: "🇺🇸→🇨🇴", amount: "$14,200", saved: "+$846", risk: "low" as const, compliance: true },
  { date: "10 Oct", supplierKey: "supplierTejidos" as const, subKey: "supplierTejidosSub" as const, invoice: "INV-22104-TM", flags: "🇺🇸→🇲🇽", amount: "$8,500", saved: "+$312", risk: "medium" as const, compliance: true },
  { date: "05 Oct", supplierKey: "supplierSuministros" as const, subKey: "supplierSuministrosSub" as const, invoice: "INV-39410-SB", flags: "🇺🇸→🇨🇴", amount: "$32,100", saved: "—", risk: "high" as const, compliance: false },
];

const riskDots: Record<string, string> = { low: "bg-emerald", medium: "bg-warm-amber", high: "bg-danger-red" };

export default function TransactionsPage() {
  const { t } = useI18n();
  const [activeFilter, setActiveFilter] = useState("all");

  const statusFilters = [
    { key: "all", label: t("all") },
    { key: "uploaded", label: t("uploaded") },
    { key: "processing", label: t("processing") },
    { key: "analyzed", label: t("analyzed") },
    { key: "error", label: t("error") },
  ];

  const riskLabels: Record<string, string> = {
    low: t("riskLowLabel"),
    medium: t("riskMedLabel"),
    high: t("riskHighLabel"),
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <h1 className="font-display text-2xl md:text-3xl font-bold">{t("transactionHistory")}</h1>
        <Button variant="outline" size="sm" className="gap-2 self-start">
          <Download className="h-4 w-4" /> {t("exportCsv")}
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2 md:gap-3">
        <span className="text-[10px] md:text-xs font-semibold text-muted-foreground uppercase tracking-wider">{t("statusFilter")}:</span>
        {statusFilters.map((f) => (
          <button
            key={f.key}
            onClick={() => setActiveFilter(f.key)}
            className={`px-2.5 md:px-3 py-1 md:py-1.5 rounded-full text-[11px] md:text-xs font-medium transition-all duration-200 ${
              activeFilter === f.key
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:text-foreground hover:bg-muted/80"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Mobile card list / Desktop table */}
      {/* Mobile: card-based layout */}
      <div className="md:hidden space-y-3">
        {txData.map((tx, i) => (
          <Card key={i} className="bg-gradient-card border-border">
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-medium text-sm">{t(tx.supplierKey)}</p>
                  <p className="text-[10px] text-muted-foreground">{t(tx.subKey)} · {tx.invoice}</p>
                </div>
                <span className="text-lg">{tx.flags}</span>
              </div>
              <div className="flex items-center justify-between mt-3">
                <div>
                  <p className="text-xs text-muted-foreground">{t("amount")}</p>
                  <p className="font-bold">{tx.amount}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">{t("saved")}</p>
                  {tx.saved !== "—" ? (
                    <span className="inline-flex px-2 py-0.5 rounded-full bg-emerald/15 text-emerald text-xs font-semibold">{tx.saved}</span>
                  ) : (
                    <span className="text-muted-foreground text-sm">—</span>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">{t("risk")}</p>
                  <span className="flex items-center gap-1 text-xs font-medium">
                    <span className={`h-2 w-2 rounded-full ${riskDots[tx.risk]}`} />
                    {riskLabels[tx.risk]}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
                <span className="text-xs text-muted-foreground">{tx.date}</span>
                <div className="flex items-center gap-3">
                  {tx.compliance ? (
                    <Check className="h-4 w-4 text-emerald" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-warm-amber" />
                  )}
                  <button className="text-muted-foreground hover:text-foreground">
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Desktop: table layout */}
      <Card className="bg-gradient-card border-border hidden md:block">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("date")}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("supplier")}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("corridor")}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("amount")}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("saved")}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("risk")}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("complianceCol")}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("actions")}</th>
                </tr>
              </thead>
              <tbody>
                {txData.map((tx, i) => (
                  <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                    <td className="px-5 py-3 text-muted-foreground">{tx.date}</td>
                    <td className="px-5 py-3">
                      <div className="font-medium">{t(tx.supplierKey)}</div>
                      <div className="text-[10px] text-muted-foreground">{t(tx.subKey)} · {tx.invoice}</div>
                    </td>
                    <td className="px-5 py-3 text-lg">{tx.flags}</td>
                    <td className="px-5 py-3 font-medium">{tx.amount}</td>
                    <td className="px-5 py-3">
                      {tx.saved !== "—" ? (
                        <span className="inline-flex px-2 py-0.5 rounded-full bg-emerald/15 text-emerald text-xs font-semibold">{tx.saved}</span>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3">
                      <span className="flex items-center gap-1.5 text-xs font-medium">
                        <span className={`h-2 w-2 rounded-full ${riskDots[tx.risk]}`} />
                        {riskLabels[tx.risk]}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      {tx.compliance ? (
                        <Check className="h-5 w-5 text-emerald" />
                      ) : (
                        <AlertTriangle className="h-5 w-5 text-warm-amber" />
                      )}
                    </td>
                    <td className="px-5 py-3">
                      <button className="text-muted-foreground hover:text-foreground">
                        <MoreVertical className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
        <Card className="border-gold-subtle glow-gold bg-gradient-card">
          <CardContent className="p-4 md:p-6">
            <p className="font-display text-base md:text-lg font-bold">{t("totalSaved")}</p>
            <p className="text-3xl md:text-4xl font-bold text-gradient-gold mt-1 md:mt-2">$1,158</p>
            <p className="text-xs text-emerald mt-1">+12.4% {t("thisMonth")}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-4 md:p-5">
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("topCorridor")}</p>
            <p className="text-lg md:text-xl font-bold mt-1 md:mt-2">USA ↔ COL</p>
            <p className="text-sm text-primary font-medium">64% {t("volume")}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-card border-border">
          <CardContent className="p-4 md:p-5">
            <p className="text-[10px] md:text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">{t("complianceRate")}</p>
            <p className="text-lg md:text-xl font-bold mt-1 md:mt-2">98.2%</p>
            <p className="text-sm text-emerald font-medium">{t("optimal")}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
