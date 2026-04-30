import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Globe, Package, TrendingUp } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useI18n } from "@/lib/i18n";

const mockProducts = [
  { hs: "0901.11", name: "Coffee, not roasted", nameEs: "Café, sin tostar", country: "Colombia", trend: "+12%", value: "$340M", risk: "low" },
  { hs: "2709.00", name: "Crude petroleum oils", nameEs: "Petróleo crudo", country: "Brazil", trend: "+5%", value: "$2.1B", risk: "medium" },
  { hs: "0803.10", name: "Bananas, fresh", nameEs: "Bananas, frescas", country: "Ecuador", trend: "+8%", value: "$180M", risk: "low" },
  { hs: "7403.11", name: "Refined copper cathodes", nameEs: "Cátodos de cobre refinado", country: "Chile", trend: "-3%", value: "$890M", risk: "low" },
  { hs: "2204.21", name: "Wine in containers ≤2L", nameEs: "Vino en envases ≤2L", country: "Argentina", trend: "+15%", value: "$95M", risk: "low" },
  { hs: "0804.30", name: "Pineapples, fresh", nameEs: "Piñas, frescas", country: "Costa Rica", trend: "+6%", value: "$62M", risk: "low" },
  { hs: "7108.12", name: "Gold, non-monetary", nameEs: "Oro, no monetario", country: "Peru", trend: "+22%", value: "$1.4B", risk: "high" },
  { hs: "4001.10", name: "Natural rubber latex", nameEs: "Látex de caucho natural", country: "Guatemala", trend: "+3%", value: "$28M", risk: "medium" },
];

const countries = ["All Countries", "Colombia", "Brazil", "Chile", "Peru", "Ecuador", "Argentina", "Mexico", "Costa Rica", "Guatemala"];
const countriesEs = ["Todos los Países", "Colombia", "Brasil", "Chile", "Perú", "Ecuador", "Argentina", "México", "Costa Rica", "Guatemala"];

export default function ExplorerPage() {
  const { t, lang } = useI18n();
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState("All Countries");

  const countryList = lang === "es" ? countriesEs : countries;

  const filtered = mockProducts.filter((p) => {
    const searchName = lang === "es" ? p.nameEs : p.name;
    const matchesQuery = !query || searchName.toLowerCase().includes(query.toLowerCase()) || p.hs.includes(query);
    const matchesCountry = country === "All Countries" || country === "Todos los Países" || p.country === country;
    return matchesQuery && matchesCountry;
  });

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-display text-3xl font-bold">{t("explorerTitle")}</h1>
        <p className="mt-1 text-muted-foreground">{t("explorerDesc")}</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder={t("searchPlaceholder")} value={query} onChange={(e) => setQuery(e.target.value)} className="pl-10" />
        </div>
        <Select value={country} onValueChange={setCountry}>
          <SelectTrigger className="w-full sm:w-[200px]">
            <Globe className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {countryList.map((c, i) => (
              <SelectItem key={c} value={countries[i]}>{c}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </motion.div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((p, i) => (
          <motion.div key={p.hs} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <Card className="group cursor-pointer bg-gradient-card transition-all duration-300 hover:border-primary/30 hover:glow-gold">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <Badge variant="secondary" className="text-xs font-mono">HS {p.hs}</Badge>
                  <Badge variant={p.risk === "high" ? "destructive" : "secondary"} className="text-[10px]">
                    {p.risk === "low" ? t("riskLowLabel") : p.risk === "medium" ? t("riskMedLabel") : t("riskHighLabel")} {t("riskLabel")}
                  </Badge>
                </div>
                <h3 className="mt-3 text-lg font-semibold group-hover:text-primary transition-colors">
                  {lang === "es" ? p.nameEs : p.name}
                </h3>
                <div className="mt-3 flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1"><Globe className="h-3.5 w-3.5" />{p.country}</span>
                  <span className="flex items-center gap-1"><Package className="h-3.5 w-3.5" />{p.value}</span>
                  <span className={`flex items-center gap-1 font-medium ${p.trend.startsWith("+") ? "text-emerald" : "text-destructive"}`}>
                    <TrendingUp className="h-3.5 w-3.5" />{p.trend}
                  </span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="mt-16 text-center">
          <Search className="mx-auto h-10 w-10 text-muted-foreground" />
          <p className="mt-4 text-muted-foreground">{t("noResults")}</p>
        </div>
      )}
    </div>
  );
}
