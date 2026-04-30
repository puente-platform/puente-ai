import { useState } from "react";
import { motion } from "framer-motion";
import { Brain, Sparkles, TrendingUp, AlertTriangle, Globe, ArrowRight, Lightbulb, Shield } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

const insightKeys = [
  { type: "opportunity", icon: TrendingUp, titleKey: "insight1Title" as const, descKey: "insight1Desc" as const, confidence: 92, tagKeys: ["tagCoffee", "tagColombia", "tagHS0901"] as const },
  { type: "risk", icon: AlertTriangle, titleKey: "insight2Title" as const, descKey: "insight2Desc" as const, confidence: 98, tagKeys: ["tagSteel", "tagBrazil", "tagTariffChange"] as const },
  { type: "opportunity", icon: Globe, titleKey: "insight3Title" as const, descKey: "insight3Desc" as const, confidence: 87, tagKeys: ["tagPeru", "tagFreshProduce", "tagFTA"] as const },
  { type: "optimization", icon: Lightbulb, titleKey: "insight4Title" as const, descKey: "insight4Desc" as const, confidence: 85, tagKeys: ["tagChile", "tagWine", "tagLogistics"] as const },
  { type: "risk", icon: Shield, titleKey: "insight5Title" as const, descKey: "insight5Desc" as const, confidence: 95, tagKeys: ["tagEcuador", "tagCompliance", "tagProduce"] as const },
];

const typeConfigKeys: Record<string, { labelKey: "opportunityLabel" | "riskAlertLabel" | "optimizationLabel"; color: string }> = {
  opportunity: { labelKey: "opportunityLabel", color: "text-emerald" },
  risk: { labelKey: "riskAlertLabel", color: "text-warm-amber" },
  optimization: { labelKey: "optimizationLabel", color: "text-ocean" },
};

export default function InsightsPage() {
  const { t } = useI18n();
  const [filter, setFilter] = useState("all");

  const filtered = filter === "all" ? insightKeys : insightKeys.filter((i) => i.type === filter);

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
            <Brain className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="font-display text-3xl font-bold">{t("insightsTitle")}</h1>
            <p className="text-muted-foreground">{t("insightsDesc")}</p>
          </div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex flex-wrap gap-2">
        {[
          { key: "all", labelKey: "allInsights" as const },
          { key: "opportunity", labelKey: "opportunities" as const },
          { key: "risk", labelKey: "riskAlerts" as const },
          { key: "optimization", labelKey: "optimizations" as const },
        ].map((f) => (
          <Button key={f.key} variant={filter === f.key ? "default" : "outline"} size="sm" onClick={() => setFilter(f.key)}>
            {t(f.labelKey)}
          </Button>
        ))}
      </motion.div>

      <div className="space-y-4">
        {filtered.map((insight, i) => {
          const config = typeConfigKeys[insight.type];
          return (
            <motion.div key={insight.titleKey} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.07 }}>
              <Card className="group cursor-pointer bg-gradient-card transition-all duration-300 hover:border-primary/30">
                <CardContent className="p-6">
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    <div className="flex-1">
                      <div className="mb-2 flex items-center gap-2">
                        <insight.icon className={`h-4 w-4 ${config.color}`} />
                        <span className={`text-xs font-semibold uppercase tracking-wider ${config.color}`}>{t(config.labelKey)}</span>
                        <span className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                          <Sparkles className="h-3 w-3" />{insight.confidence}% {t("confidence")}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold">{t(insight.titleKey)}</h3>
                      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{t(insight.descKey)}</p>
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {insight.tagKeys.map((tagKey) => (
                          <Badge key={tagKey} variant="secondary" className="text-[10px]">{t(tagKey)}</Badge>
                        ))}
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" className="shrink-0 text-primary">
                      {t("details")} <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
