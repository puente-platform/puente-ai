import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, FileSearch, FileText, Settings, Cloud, Search, Brain } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import puenteLogoWhite from "@/assets/puente-logo-white.png";

const navItems = [
  { key: "dashboard" as const, href: "/dashboard", icon: LayoutDashboard },
  { key: "newAnalysis" as const, href: "/analyze", icon: FileSearch, highlight: true },
  { key: "explorer" as const, href: "/explorer", icon: Search },
  { key: "aiInsights" as const, href: "/insights", icon: Brain },
  { key: "transactions" as const, href: "/transactions", icon: FileText },
  { key: "settings" as const, href: "/settings", icon: Settings },
];

export default function AppSidebar() {
  const location = useLocation();
  const { t } = useI18n();

  return (
    <aside className="hidden md:flex md:w-[240px] md:flex-col md:fixed md:inset-y-0 bg-sidebar border-r border-sidebar-border">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="px-6 pt-6 pb-8">
          <Link to="/" className="flex flex-col gap-1">
            <div
              className="h-8 w-[160px] bg-gradient-gold"
              style={{
                WebkitMaskImage: `url(${puenteLogoWhite})`,
                WebkitMaskSize: "contain",
                WebkitMaskRepeat: "no-repeat",
                WebkitMaskPosition: "left center",
                maskImage: `url(${puenteLogoWhite})`,
                maskSize: "contain",
                maskRepeat: "no-repeat",
                maskPosition: "left center",
              }}
            />
            <div className="text-[11px] font-medium tracking-widest uppercase text-sidebar-foreground/50">
              {t("tradeIntelligence")}
            </div>
          </Link>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-sidebar-primary/15 text-sidebar-primary border border-sidebar-primary/20"
                    : item.highlight
                      ? "text-sidebar-primary hover:bg-sidebar-accent"
                      : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent"
                }`}
              >
                <item.icon className="h-4 w-4" />
                {t(item.key)}
              </Link>
            );
          })}
        </nav>

        {/* Roadmap */}
        <div className="px-3 mb-4">
          <div className="text-[10px] font-semibold tracking-wider text-sidebar-foreground/40 uppercase px-3 mb-2">{t("roadmap")}</div>
          {(["sidebarV2", "sidebarV3", "sidebarV4", "sidebarV5"] as const).map((key) => (
            <div key={key} className="flex items-center gap-2 px-3 py-1.5 text-xs text-sidebar-foreground/30">
              <span className="h-1.5 w-1.5 rounded-full bg-sidebar-foreground/20" />
              {t(key)}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 text-[11px] italic text-sidebar-foreground/40 border-t border-sidebar-border">
          <Cloud className="inline h-3 w-3 mr-1" />
          {t("poweredBy")}
        </div>
      </div>
    </aside>
  );
}
