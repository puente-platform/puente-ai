import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { confirmPasswordReset } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, Check, AlertTriangle } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export default function ResetPasswordPage() {
  const { t } = useI18n();
  const [searchParams] = useSearchParams();
  const oobCode = searchParams.get("oobCode");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!oobCode) {
      setError(t("resetPasswordMissingCode"));
      return;
    }
    if (password.length < 6) {
      setError(t("resetPasswordMinLength"));
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await confirmPasswordReset(auth, oobCode, password);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-navy grid place-items-center p-4">
      <Card className="w-full max-w-md bg-gradient-card border-gold-subtle">
        <CardContent className="p-6 space-y-5">
          <div>
            <h1 className="text-2xl font-display font-bold">{t("resetPasswordTitle")}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              {success ? t("resetPasswordSuccessTitle") : t("resetPasswordSubtitle")}
            </p>
          </div>

          {success ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-emerald">
                <Check className="h-5 w-5" />
                <span className="text-sm font-medium">{t("resetPasswordSuccessMsg")}</span>
              </div>
              <Button asChild className="w-full">
                <Link to="/login">{t("resetPasswordContinue")}</Link>
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">{t("resetPasswordNewLabel")}</label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  minLength={6}
                  autoComplete="new-password"
                />
              </div>
              {error && (
                <div className="flex items-start gap-2 text-sm text-danger-red">
                  <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span className="break-words">{error}</span>
                </div>
              )}
              <Button type="submit" disabled={submitting} className="w-full">
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : t("resetPasswordSubmit")}
              </Button>
              <p className="text-xs text-center text-muted-foreground">
                <Link to="/login" className="hover:text-primary">{t("resetPasswordBack")}</Link>
              </p>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
