import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useI18n } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";
import { useAuth } from "@/lib/auth";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Sun, Moon, Eye, EyeOff, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { isOnboarded } from "@/lib/onboarding";
import { auth } from "@/lib/firebase";
import puenteIconColor from "@/assets/puente-icon-color.png";

export default function LoginPage() {
  const { t, lang, setLang } = useI18n();
  const { theme, toggleTheme } = useTheme();
  const { signIn, signUp, signInWithGoogle, signInWithApple, resetPassword } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isSignUp, setIsSignUp] = useState(searchParams.get("mode") === "signup");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isSignUp) {
        await signUp(email, password, name || undefined);
        toast.success("Account created!");
        navigate("/onboarding");
      } else {
        await signIn(email, password);
        toast.success("Welcome back!");
        const uid = auth.currentUser?.uid;
        const onboarded = await isOnboarded(uid).catch(() => false);
        navigate(onboarded ? "/dashboard" : "/onboarding");
      }
    } catch (err: any) {
      const code = err?.code || "";
      if (code === "auth/email-already-in-use") toast.error("Email already in use");
      else if (code === "auth/invalid-credential") toast.error("Invalid email or password");
      else if (code === "auth/weak-password") toast.error("Password must be at least 6 characters");
      else toast.error(err?.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSocial = async (provider: "google" | "apple") => {
    setLoading(true);
    try {
      if (provider === "google") await signInWithGoogle();
      else await signInWithApple();
      const uid = auth.currentUser?.uid;
      const onboarded = await isOnboarded(uid).catch(() => false);
      navigate(onboarded ? "/dashboard" : "/onboarding");
    } catch (err: any) {
      if (err?.code !== "auth/popup-closed-by-user") {
        toast.error(err?.message || "Authentication failed");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!email) {
      toast.error(lang === "es" ? "Ingresa tu correo primero" : "Enter your email first");
      return;
    }
    try {
      await resetPassword(email);
      toast.success(lang === "es" ? "Correo de recuperación enviado" : "Password reset email sent");
    } catch {
      toast.error(lang === "es" ? "Error al enviar correo" : "Failed to send reset email");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden px-4">
      {/* Ambient glow effects */}
      <div className="absolute top-[-200px] left-[-100px] w-[500px] h-[500px] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-150px] right-[-50px] w-[400px] h-[400px] rounded-full bg-primary/8 blur-[100px] pointer-events-none" />

      {/* Top bar controls */}
      <div className="absolute top-6 right-6 flex items-center gap-3">
        <button
          onClick={() => setLang(lang === "en" ? "es" : "en")}
          className="text-xs font-bold tracking-wider text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded-md hover:bg-muted"
        >
          {lang === "en" ? "ES" : "EN"}
        </button>
        <button
          onClick={toggleTheme}
          className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-[420px]"
      >
        {/* Card */}
        <div className="rounded-2xl border border-border bg-card/80 backdrop-blur-xl p-8 shadow-xl shadow-black/5 dark:shadow-black/20">
          {/* Logo */}
          <div className="flex items-center justify-center gap-2 mb-8">
            <img src={puenteIconColor} alt="Puente AI" className="h-7 w-7" />
            <span className="font-display text-lg font-bold tracking-tight text-foreground">PUENTE AI</span>
          </div>

          {/* Heading */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-display font-bold text-foreground">
              {isSignUp ? t("signUpTitle") : t("signInTitle")}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {isSignUp ? t("signUpSubtitle") : t("signInSubtitle")}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {isSignUp && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-1.5"
              >
                <Label htmlFor="name" className="text-sm font-medium">
                  {t("loginName")}
                </Label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t("loginNamePlaceholder")}
                  className="h-11 bg-muted/50 border-border focus:border-primary"
                />
              </motion.div>
            )}

            <div className="space-y-1.5">
              <Label htmlFor="email" className="text-sm font-medium">
                {t("loginEmail")}
              </Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("loginEmailPlaceholder")}
                className="h-11 bg-muted/50 border-border focus:border-primary"
                required
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-sm font-medium">
                  {t("loginPassword")}
                </Label>
                {!isSignUp && (
                  <button
                    type="button"
                    onClick={handleForgotPassword}
                    className="text-xs text-primary hover:underline font-medium"
                  >
                    {t("forgotPassword")}
                  </button>
                )}
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="h-11 bg-muted/50 border-border focus:border-primary pr-10"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button type="submit" size="lg" className="w-full h-11 font-semibold" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : isSignUp ? t("signUpButton") : t("signInButton")}
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-muted-foreground uppercase tracking-wider">{t("orContinueWith")}</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Social buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="h-11 gap-2 text-sm font-medium" disabled={loading} onClick={() => handleSocial("google")}>
              <svg className="h-4 w-4" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google
            </Button>
            <Button variant="outline" className="h-11 gap-2 text-sm font-medium" disabled={loading} onClick={() => handleSocial("apple")}>
              <svg className="h-4 w-4 fill-foreground" viewBox="0 0 24 24">
                <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
              </svg>
              Apple
            </Button>
          </div>

          {/* Toggle sign in / sign up */}
          <p className="mt-6 text-center text-sm text-muted-foreground">
            {isSignUp ? t("alreadyHaveAccount") : t("noAccount")}{" "}
            <button
              onClick={() => setIsSignUp(!isSignUp)}
              className="text-primary font-semibold hover:underline"
            >
              {isSignUp ? t("signInLink") : t("signUpLink")}
            </button>
          </p>
        </div>

        {/* Trust footer */}
        <p className="mt-6 text-center text-[11px] text-muted-foreground">
          🔒 {t("loginTrust")}
        </p>
      </motion.div>
    </div>
  );
}
