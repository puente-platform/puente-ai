import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { useI18n } from "@/lib/i18n";

const NotFound = () => {
  const location = useLocation();
  const { t } = useI18n();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted">
      <div className="max-w-md text-center px-6">
        <h1 className="mb-4 text-4xl font-bold">404</h1>
        <p className="mb-2 text-xl font-semibold text-foreground">{t("notFoundTitle")}</p>
        <p className="mb-6 text-sm text-muted-foreground">{t("notFoundDesc")}</p>
        <a href="/" className="text-primary underline hover:text-primary/90">
          {t("notFoundCta")}
        </a>
      </div>
    </div>
  );
};

export default NotFound;
