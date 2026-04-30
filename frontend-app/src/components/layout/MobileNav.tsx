import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, FileSearch, FileText, Settings } from "lucide-react";
import { useI18n } from "@/lib/i18n";

type NavItemType = { key: "dashboard" | "transactions" | "settings"; href: string; icon: typeof LayoutDashboard };

const leftItems: NavItemType[] = [
  { key: "dashboard", href: "/dashboard", icon: LayoutDashboard },
  { key: "transactions", href: "/transactions", icon: FileText },
];

const rightItems: NavItemType[] = [
  { key: "settings", href: "/settings", icon: Settings },
];

export default function MobileNav() {
  const location = useLocation();
  const { t } = useI18n();
  const isAnalyzeActive = location.pathname === "/analyze";

  const NavItem = ({ item }: { item: (typeof leftItems)[0] }) => {
    const isActive = location.pathname === item.href;
    return (
      <Link
        to={item.href}
        className={`flex flex-col items-center justify-center gap-0.5 min-w-[60px] py-1.5 text-[10px] font-medium transition-colors ${
          isActive ? "text-primary" : "text-muted-foreground"
        }`}
      >
        <item.icon className="h-5 w-5" />
        {t(item.key)}
      </Link>
    );
  };

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50">
      <div className="relative bg-card/95 backdrop-blur-lg border-t border-border h-16 flex items-center justify-between px-6">
        {/* Left nav items */}
        <div className="flex items-center gap-4">
          {leftItems.map((item) => (
            <NavItem key={item.href} item={item} />
          ))}
        </div>

        {/* Center FAB */}
        <Link
          to="/analyze"
          className={`absolute left-1/2 -translate-x-1/2 -top-5 h-[52px] w-[52px] rounded-2xl flex items-center justify-center shadow-lg transition-all duration-200 ${
            isAnalyzeActive
              ? "bg-primary text-primary-foreground shadow-primary/40 scale-105"
              : "bg-primary text-primary-foreground shadow-primary/25 hover:scale-105 hover:shadow-primary/40"
          }`}
          aria-label={t("newAnalysis")}
        >
          <FileSearch className="h-5 w-5" />
        </Link>

        {/* Right nav items */}
        <div className="flex items-center gap-4">
          {rightItems.map((item) => (
            <NavItem key={item.href} item={item} />
          ))}
        </div>
      </div>
    </nav>
  );
}
