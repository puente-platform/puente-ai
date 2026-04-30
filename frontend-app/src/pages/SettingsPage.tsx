import { useI18n } from "@/lib/i18n";
import { Card, CardContent } from "@/components/ui/card";
import { Globe, User, Bell, Key, CreditCard, Ship, TrendingUp, Map, Lock } from "lucide-react";
import { useState } from "react";

const settingsNav = [
  { key: "profile" as const, icon: User },
  { key: "language" as const, icon: Globe },
  { key: "notifications" as const, icon: Bell },
  { key: "apiKeys" as const, icon: Key },
];

export default function SettingsPage() {
  const { t, lang, setLang } = useI18n();
  const [activeSection, setActiveSection] = useState<string>("language");

  const roadmap = [
    { version: "V2", title: t("roadmapV2Title"), desc: t("roadmapV2"), icon: CreditCard },
    { version: "V3", title: t("roadmapV3Title"), desc: t("roadmapV3"), icon: Ship },
    { version: "V4", title: t("roadmapV4Title"), desc: t("roadmapV4"), icon: TrendingUp },
    { version: "V5", title: t("roadmapV5Title"), desc: t("roadmapV5"), icon: Map },
  ];

  return (
    <div className="space-y-6 md:space-y-8">
      <h1 className="font-display text-2xl md:text-3xl font-bold">{t("settingsTitle")}</h1>

      <div className="grid md:grid-cols-[220px_1fr] gap-4 md:gap-6">
        {/* Nav - horizontal scroll on mobile, vertical on desktop */}
        <div className="flex md:flex-col gap-1 overflow-x-auto pb-2 md:pb-0 -mx-4 px-4 md:mx-0 md:px-0 scrollbar-none">
          {settingsNav.map((item) => (
            <button
              key={item.key}
              onClick={() => setActiveSection(item.key)}
              className={`flex items-center gap-2 md:gap-3 whitespace-nowrap px-3 md:px-4 py-2 md:py-2.5 rounded-lg text-sm font-medium transition-all duration-200 text-left shrink-0 ${
                activeSection === item.key
                  ? "text-primary bg-primary/10 border border-gold-subtle"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              <item.icon className="h-4 w-4" />
              {t(item.key)}
            </button>
          ))}
        </div>

        {/* Content */}
        <div>
          {activeSection === "language" && (
            <Card className="bg-gradient-card border-border">
              <CardContent className="p-5 md:p-8">
                <h2 className="font-display text-xl md:text-2xl font-bold">{t("langTitle")}</h2>
                <p className="mt-2 text-sm text-muted-foreground">{t("langDesc")}</p>

                <div className="mt-5 md:mt-6 flex rounded-xl overflow-hidden border border-border">
                  <button
                    onClick={() => setLang("en")}
                    className={`flex-1 flex items-center justify-center gap-2 md:gap-3 py-3 md:py-4 text-sm md:text-base font-semibold transition-all duration-200 ${
                      lang === "en"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    🇺🇸 {lang === "en" ? "ENGLISH" : "EN"}
                  </button>
                  <button
                    onClick={() => setLang("es")}
                    className={`flex-1 flex items-center justify-center gap-2 md:gap-3 py-3 md:py-4 text-sm md:text-base font-semibold transition-all duration-200 ${
                      lang === "es"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    🇪🇸 {lang === "es" ? "ESPAÑOL" : "ES"}
                  </button>
                </div>

                <div className="mt-5 md:mt-6 rounded-lg border-l-4 border-primary bg-muted p-3 md:p-4">
                  <p className="text-sm font-semibold text-primary">{t("aiNoteLabel")}</p>
                  <p className="mt-1 text-xs md:text-sm text-muted-foreground">{t("aiNote")}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection !== "language" && (
            <Card className="bg-gradient-card border-border">
              <CardContent className="p-6 md:p-8 text-center text-muted-foreground">
                <Lock className="h-8 w-8 mx-auto mb-3 text-muted-foreground/50" />
                <p className="font-medium">{t("comingSoon")}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Roadmap V2–V5 */}
      <div>
        <p className="text-[11px] font-semibold tracking-wider text-primary uppercase mb-1">{t("exploringFuture")}</p>
        <h2 className="font-display text-xl md:text-2xl font-bold">{t("roadmapTitle")}</h2>
        <div className="mt-4 md:mt-6 grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          {roadmap.map((item) => (
            <Card key={item.version} className="bg-gradient-card border-border opacity-50">
              <CardContent className="p-3 md:p-5">
                <div className="flex items-start justify-between mb-2 md:mb-3">
                  <div className="h-8 w-8 md:h-10 md:w-10 rounded-lg bg-muted flex items-center justify-center">
                    <item.icon className="h-4 w-4 md:h-5 md:w-5 text-muted-foreground" />
                  </div>
                  <span className="text-[9px] md:text-[10px] font-bold text-muted-foreground border border-border rounded px-1 md:px-1.5 py-0.5">{item.version}</span>
                </div>
                <h3 className="font-display font-bold text-xs md:text-sm">{item.title}</h3>
                <p className="mt-1 text-[10px] md:text-xs text-muted-foreground line-clamp-2">{item.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
