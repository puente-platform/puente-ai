import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2, ArrowLeft, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { useI18n } from "@/lib/i18n";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  CORRIDOR_OPTIONS,
  getOnboarding,
  markOnboarded,
  saveOnboarding,
} from "@/lib/onboarding";
import puenteIconColor from "@/assets/puente-icon-color.png";

type StepId = "language" | "profile" | "corridors" | "done";
const STEPS: StepId[] = ["language", "profile", "corridors", "done"];

export default function OnboardingPage() {
  const { t, lang, setLang } = useI18n();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stepIndex, setStepIndex] = useState(0);
  const [displayName, setDisplayName] = useState(user?.displayName ?? "");
  const [company, setCompany] = useState("");
  const [corridors, setCorridors] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  // Hydrate form state from any existing onboarding record (e.g. user reopens
  // the flow after partial completion). Server is source of truth via
  // getOnboarding(); falls back to localStorage cache on network failure.
  //
  // hydratedForUidRef gates against a slow network round-trip clobbering
  // input the user typed while the GET was in flight. Keyed by uid (not a
  // simple boolean) so a sign-out + sign-in-as-different-user resets the
  // gate and re-hydrates from the new account — without this, a sticky
  // boolean ref would leak the previous user's profile across accounts on
  // the same browser session (Copilot + CodeRabbit flagged this).
  const hydratedForUidRef = useRef<string | null | undefined>(null);
  useEffect(() => {
    if (hydratedForUidRef.current !== user?.uid) {
      hydratedForUidRef.current = null; // reset on uid change
    }
    let cancelled = false;
    (async () => {
      const existing = await getOnboarding(user?.uid);
      if (cancelled || !existing || hydratedForUidRef.current === user?.uid) return;
      hydratedForUidRef.current = user?.uid;
      if (existing.displayName) setDisplayName(existing.displayName);
      if (existing.company) setCompany(existing.company);
      if (existing.corridors) setCorridors(existing.corridors);
    })();
    return () => { cancelled = true; };
  }, [user?.uid]);

  const stepId = STEPS[stepIndex];
  const totalVisibleSteps = STEPS.length - 1; // exclude "done" from "X of Y"

  const goNext = () => setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
  const goBack = () => setStepIndex((i) => Math.max(i - 1, 0));

  const persistProfile = async () => {
    if (!user?.uid) return;
    try {
      await saveOnboarding(user.uid, {
        displayName: displayName.trim() || undefined,
        company: company.trim() || undefined,
        corridors,
      });
    } catch {
      // Non-fatal: user can retry on Finish; we don't want to block
      // step navigation on a network error.
    }
  };

  const handleFinish = async () => {
    if (!user?.uid) {
      navigate("/dashboard");
      return;
    }
    setSubmitting(true);
    try {
      await saveOnboarding(user.uid, {
        displayName: displayName.trim() || undefined,
        company: company.trim() || undefined,
        corridors,
      });
      await markOnboarded(user.uid);
      navigate("/dashboard");
    } catch {
      // Surface a soft failure: stay on the Done step so the user can retry.
      // Without this, the spinner just stops and the user sees no signal that
      // anything went wrong (bug_007 from ultrareview).
      toast.error(
        lang === "es"
          ? "No pudimos guardar tu perfil. Intenta de nuevo."
          : "Could not save your profile. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkip = async () => {
    if (user?.uid) {
      try { await markOnboarded(user.uid); } catch { /* non-fatal */ }
    }
    navigate("/dashboard");
  };

  const toggleCorridor = (id: string) => {
    setCorridors((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id],
    );
  };

  const canContinue = (() => {
    if (stepId === "profile") return displayName.trim().length > 0;
    return true;
  })();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden px-4 py-10">
      <div className="absolute top-[-200px] left-[-100px] w-[500px] h-[500px] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-150px] right-[-50px] w-[400px] h-[400px] rounded-full bg-primary/8 blur-[100px] pointer-events-none" />

      <button
        onClick={handleSkip}
        className="absolute top-6 right-6 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
      >
        {t("onbSkip")}
      </button>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-[520px]"
      >
        <div className="flex items-center justify-center gap-2 mb-8">
          <img src={puenteIconColor} alt="Puente AI" className="h-8 w-8" />
          <span className="font-display text-lg font-bold tracking-tight text-foreground">
            PUENTE AI
          </span>
        </div>

        {stepId !== "done" && (
          <div className="mb-6">
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-2 uppercase tracking-wider font-medium">
              <span>
                {t("onbStepLabel")} {stepIndex + 1} {t("onbOf")} {totalVisibleSteps}
              </span>
            </div>
            <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-primary"
                initial={false}
                animate={{ width: `${((stepIndex + 1) / totalVisibleSteps) * 100}%` }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              />
            </div>
          </div>
        )}

        <div className="rounded-2xl border border-border bg-card/80 backdrop-blur-xl p-8 shadow-xl shadow-black/5 dark:shadow-black/20">
          <AnimatePresence mode="wait">
            {stepId === "language" && (
              <motion.div
                key="language"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                <h1 className="text-2xl font-display font-bold text-foreground">
                  {t("onbLangTitle")}
                </h1>
                <p className="mt-2 text-sm text-muted-foreground mb-6">
                  {t("onbLangSubtitle")}
                </p>

                <div className="grid grid-cols-1 gap-3">
                  {(["en", "es"] as const).map((code) => {
                    const selected = lang === code;
                    return (
                      <button
                        key={code}
                        type="button"
                        onClick={() => setLang(code)}
                        className={`flex items-center justify-between rounded-xl border px-4 py-4 text-left transition-all ${
                          selected
                            ? "border-primary bg-primary/5 ring-2 ring-primary/30"
                            : "border-border hover:border-primary/50 hover:bg-muted/50"
                        }`}
                      >
                        <div>
                          <div className="font-semibold text-foreground">
                            {code === "en" ? t("onbLangEn") : t("onbLangEs")}
                          </div>
                          <div className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider">
                            {code}
                          </div>
                        </div>
                        {selected && (
                          <div className="h-6 w-6 rounded-full bg-primary text-primary-foreground grid place-items-center">
                            <Check className="h-4 w-4" />
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {stepId === "profile" && (
              <motion.div
                key="profile"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                <h1 className="text-2xl font-display font-bold text-foreground">
                  {t("onbProfileTitle")}
                </h1>
                <p className="mt-2 text-sm text-muted-foreground mb-6">
                  {t("onbProfileSubtitle")}
                </p>

                <div className="space-y-5">
                  <div className="space-y-1.5">
                    <Label htmlFor="onb-name" className="text-sm font-medium">
                      {t("onbProfileName")}
                    </Label>
                    <Input
                      id="onb-name"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder={t("onbProfileNamePlaceholder")}
                      maxLength={80}
                      className="h-11 bg-muted/50 border-border focus:border-primary"
                      autoFocus
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="onb-company" className="text-sm font-medium">
                      {t("onbProfileCompany")}
                    </Label>
                    <Input
                      id="onb-company"
                      value={company}
                      onChange={(e) => setCompany(e.target.value)}
                      placeholder={t("onbProfileCompanyPlaceholder")}
                      maxLength={120}
                      className="h-11 bg-muted/50 border-border focus:border-primary"
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {stepId === "corridors" && (
              <motion.div
                key="corridors"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                <h1 className="text-2xl font-display font-bold text-foreground">
                  {t("onbCorridorsTitle")}
                </h1>
                <p className="mt-2 text-sm text-muted-foreground mb-6">
                  {t("onbCorridorsSubtitle")}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {CORRIDOR_OPTIONS.map((c) => {
                    const selected = corridors.includes(c.id);
                    return (
                      <button
                        key={c.id}
                        type="button"
                        onClick={() => toggleCorridor(c.id)}
                        className={`flex items-center justify-between rounded-xl border px-4 py-3 text-left transition-all text-sm ${
                          selected
                            ? "border-primary bg-primary/5 ring-2 ring-primary/30"
                            : "border-border hover:border-primary/50 hover:bg-muted/50"
                        }`}
                      >
                        <span className="font-medium text-foreground">{c.label[lang]}</span>
                        {selected && (
                          <div className="h-5 w-5 rounded-full bg-primary text-primary-foreground grid place-items-center shrink-0">
                            <Check className="h-3 w-3" />
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {stepId === "done" && (
              <motion.div
                key="done"
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="text-center py-4"
              >
                <div className="mx-auto h-14 w-14 rounded-full bg-primary/15 grid place-items-center mb-5">
                  <Check className="h-7 w-7 text-primary" strokeWidth={3} />
                </div>
                <h1 className="text-2xl font-display font-bold text-foreground">
                  {t("onbDoneTitle").replace("{name}", displayName.split(" ")[0] || (lang === "es" ? "amig@" : "friend"))}
                </h1>
                <p className="mt-2 text-sm text-muted-foreground">{t("onbDoneSubtitle")}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Footer nav */}
          <div className="mt-8 flex items-center justify-between gap-3">
            {stepId !== "done" && stepIndex > 0 ? (
              <Button variant="ghost" onClick={goBack} className="gap-1">
                <ArrowLeft className="h-4 w-4" />
                {t("onbBack")}
              </Button>
            ) : (
              <span />
            )}

            {stepId !== "done" ? (
              <Button
                onClick={() => {
                  void persistProfile();
                  goNext();
                }}
                disabled={!canContinue}
                className="gap-1 font-semibold"
              >
                {t("onbContinue")}
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleFinish}
                disabled={submitting}
                size="lg"
                className="w-full font-semibold"
              >
                {submitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  t("onbFinish")
                )}
              </Button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
