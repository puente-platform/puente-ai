import { useI18n } from "@/lib/i18n";
import { Lock, ShieldCheck, Cloud } from "lucide-react";

export default function TrustFooter() {
  const { t } = useI18n();
  return (
    <footer className="border-t border-border px-6 py-4 flex flex-wrap items-center justify-between gap-4 text-xs text-muted-foreground">
      <div className="flex items-center gap-6">
        <span className="flex items-center gap-1">
          <Lock className="h-3 w-3" /> {t("encrypted")}
        </span>
        <span className="flex items-center gap-1">
          <ShieldCheck className="h-3 w-3" /> {t("corridorVerified")}
        </span>
        <span className="flex items-center gap-1">
          <Cloud className="h-3 w-3" /> {t("poweredBy")}
        </span>
      </div>
      <div className="flex items-center gap-4">
        <span className="cursor-pointer hover:text-primary">{t("privacy")}</span>
        <span className="cursor-pointer hover:text-primary">{t("terms")}</span>
        <span>© {new Date().getFullYear()} Puente AI</span>
      </div>
    </footer>
  );
}
