import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { I18nProvider } from "@/lib/i18n";
import { ThemeProvider } from "@/lib/theme";
import { AuthProvider, useAuth } from "@/lib/auth";
import AppLayout from "@/components/layout/AppLayout";
import LandingPage from "./pages/LandingPage";
import AboutPage from "./pages/AboutPage";
import DashboardPage from "./pages/DashboardPage";
import AnalyzePage from "./pages/AnalyzePage";
import ExplorerPage from "./pages/ExplorerPage";
import InsightsPage from "./pages/InsightsPage";
import TransactionsPage from "./pages/TransactionsPage";
import SettingsPage from "./pages/SettingsPage";
import LoginPage from "./pages/LoginPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import OnboardingPage from "./pages/OnboardingPage";
import NotFound from "./pages/NotFound";
import { isOnboarded } from "@/lib/onboarding";

function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen grid place-items-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

// isOnboarded is async (Firestore-backed). Async route guard pattern:
// resolve the boolean in an effect, render a spinner while pending, then
// either pass through or redirect. Guards against the cross-account leak
// (reset state when user.uid changes — Copilot/CodeRabbit flagged a sticky
// hydratedRef pattern in OnboardingPage; the same risk applies here).
function RequireOnboarded({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  const [onboarded, setOnboarded] = useState<boolean | null>(null);

  useEffect(() => {
    if (!user?.uid) {
      setOnboarded(null);
      return;
    }
    let cancelled = false;
    setOnboarded(null); // reset on uid change
    isOnboarded(user.uid)
      .then((result) => { if (!cancelled) setOnboarded(result); })
      .catch(() => { if (!cancelled) setOnboarded(false); });
    return () => { cancelled = true; };
  }, [user?.uid]);

  if (loading || (user && onboarded === null)) {
    return (
      <div className="min-h-screen grid place-items-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  if (!onboarded) return <Navigate to="/onboarding" replace />;
  return children;
}

const App = () => (
  <TooltipProvider>
    <ThemeProvider>
      <I18nProvider>
        <AuthProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            {/* Onboarding — auth required, but not gated by onboarded status */}
            <Route
              path="/onboarding"
              element={
                <RequireAuth>
                  <OnboardingPage />
                </RequireAuth>
              }
            />
            {/* App pages — gated by auth + onboarding completion */}
            <Route element={<RequireOnboarded><AppLayout /></RequireOnboarded>}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/analyze" element={<AnalyzePage />} />
              <Route path="/explorer" element={<ExplorerPage />} />
              <Route path="/insights" element={<InsightsPage />} />
              <Route path="/transactions" element={<TransactionsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
          </BrowserRouter>
        </AuthProvider>
      </I18nProvider>
    </ThemeProvider>
  </TooltipProvider>
);

export default App;
