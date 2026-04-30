import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";

import FrequentlyAskedQuestionsAccordion from "@/components/ui/frequently-asked-questions-accordion";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { useTheme } from "@/lib/theme";
import { useI18n } from "@/lib/i18n";
import puenteLogo from "@/assets/puente-logo.png";
import puenteLogoWhite from "@/assets/puente-logo-white.png";
import puenteIconColor from "@/assets/puente-icon-color.png";
import AnimatedHeroText from "@/components/AnimatedHeroText";
import {
  Globe,
  Zap,
  Shield,
  TrendingUp,
  Search,
  Brain,
  ArrowRight,
  Sun,
  Moon,
} from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: "easeOut" },
  }),
};

const featureIcons = [TrendingUp, Search, Brain, Shield, Globe, Zap];

const statValues = ["~15s", "5 corridors", "Up to 80%", "Wire vs. stablecoin"];
const statValuesEs = ["~15s", "5 corredores", "Hasta 80%", "Banco vs. stablecoin"];

export default function LandingPage() {
  const { theme, toggleTheme } = useTheme();
  const { lang, setLang, t } = useI18n();

  const features = [
    { icon: featureIcons[0], title: t("feat1Title"), desc: t("feat1Desc") },
    { icon: featureIcons[1], title: t("feat2Title"), desc: t("feat2Desc") },
    { icon: featureIcons[2], title: t("feat3Title"), desc: t("feat3Desc") },
    { icon: featureIcons[3], title: t("feat4Title"), desc: t("feat4Desc") },
    { icon: featureIcons[4], title: t("feat5Title"), desc: t("feat5Desc") },
    { icon: featureIcons[5], title: t("feat6Title"), desc: t("feat6Desc") },
  ];

  const sv = lang === "es" ? statValuesEs : statValues;
  const stats = [
    { value: sv[0], label: t("statInvoice") },
    { value: sv[1], label: t("statCorridors") },
    { value: sv[2], label: t("statTests") },
    { value: sv[3], label: t("statInfra") },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Helmet>
        <title>{t("seoTitle")}</title>
        <meta name="description" content={t("seoDesc")} />
        <meta property="og:title" content={t("seoTitle")} />
        <meta property="og:description" content={t("seoDesc")} />
      </Helmet>
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-navy text-white">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <img src={puenteIconColor} alt="" className="h-7 w-7" />
            <span className="font-display text-lg font-bold text-white tracking-tight">PUENTE AI</span>
          </div>

          <div className="hidden lg:flex items-center gap-1">
            {[
              { label: t("dashboard"), href: "/dashboard" },
              { label: t("explorer"), href: "/explorer" },
              { label: t("aiInsights"), href: "/insights" },
              { label: t("about"), href: "/about" },
            ].map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className="rounded-lg px-4 py-2 text-sm font-medium text-white/70 hover:text-white transition-colors"
              >
                {item.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-1 sm:gap-2">
            <div className="flex items-center gap-1 text-xs font-medium mr-1 sm:mr-2">
              <button onClick={() => setLang("en")} className={lang === "en" ? "text-primary font-bold" : "text-white/60"}>EN</button>
              <span className="text-white/30">|</span>
              <button onClick={() => setLang("es")} className={lang === "es" ? "text-primary font-bold" : "text-white/60"}>ES</button>
            </div>
            <button onClick={toggleTheme} className="h-8 w-8 sm:h-9 sm:w-9 rounded-lg flex items-center justify-center text-white/70 hover:text-primary hover:bg-white/10 transition-colors">
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <Button variant="ghost" size="sm" className="hidden sm:inline-flex text-white/70 hover:text-white hover:bg-white/10" asChild>
              <Link to="/login">{t("signInButton")}</Link>
            </Button>
            <Button variant="default" size="sm" asChild>
              <Link to="/login?mode=signup" className="text-xs sm:text-sm">{t("getStarted")}</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-32 pb-20">
        <div className="pointer-events-none absolute top-20 right-[-200px] h-[500px] w-[500px] rounded-full bg-primary/5 blur-[120px]" />
        <div className="pointer-events-none absolute bottom-0 left-[-100px] h-[300px] w-[300px] rounded-full bg-ocean/5 blur-[100px]" />

        <div className="container relative">
          <motion.div className="mx-auto max-w-3xl text-center" initial="hidden" animate="visible">
            <motion.div custom={0} variants={fadeUp} className="mb-6 inline-flex items-center gap-2 rounded-full border border-gold-subtle bg-muted/50 px-4 py-1.5 text-sm text-primary">
              <Zap className="h-3.5 w-3.5" />
              {t("tagline")}
            </motion.div>

            <motion.h1 custom={1} variants={fadeUp}>
              <AnimatedHeroText />
            </motion.h1>

            <motion.p custom={2} variants={fadeUp} className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground">
              {t("heroDesc")}
            </motion.p>

            <motion.div custom={3} variants={fadeUp} className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Button variant="default" size="lg" asChild>
                <Link to="/login?mode=signup">
                  {t("startExploring")} <ArrowRight className="ml-1 h-5 w-5" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to="/explorer">{t("browseMarkets")}</Link>
              </Button>
            </motion.div>
          </motion.div>

          {/* Stats */}
          <motion.div initial="hidden" animate="visible" className="mt-20 grid grid-cols-2 gap-4 lg:gap-6 lg:grid-cols-4">
            {stats.map((stat, i) => (
              <motion.div key={stat.label} custom={i + 4} variants={fadeUp} className="rounded-xl border bg-card p-4 md:p-6 text-center">
                <div className="font-display text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-gradient-gold leading-tight">{stat.value}</div>
                <div className="mt-1 text-xs md:text-sm text-muted-foreground">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mx-auto mb-16 max-w-2xl text-center">
            <h2 className="font-display text-3xl font-bold md:text-4xl">
              {t("featuresTitle1")}{" "}
              <span className="text-gradient-gold">{t("featuresTitle2")}</span>
            </h2>
            <p className="mt-4 text-muted-foreground">{t("featuresDesc")}</p>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => (
              <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}
                className="group rounded-xl border bg-card p-6 transition-all duration-300 hover:border-primary/30 hover:glow-gold"
              >
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary/20">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Founder quote (testimonials carousel hidden until permission-cleared customer quotes are available) */}
      <section className="bg-muted/30 py-24">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mx-auto max-w-3xl rounded-2xl border border-gold-subtle bg-card p-10 md:p-14 text-center"
          >
            <p className="text-xs font-semibold tracking-widest text-primary uppercase">
              {t("founderSectionTitle")}
            </p>
            <blockquote className="mt-6 font-display text-xl md:text-2xl leading-relaxed text-foreground">
              &ldquo;{t("founderQuoteEn")}&rdquo;
            </blockquote>
            <p className="mt-6 text-sm text-muted-foreground">
              {t("founderAttribution")}
            </p>
          </motion.div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-12 bg-muted/30">
        <FrequentlyAskedQuestionsAccordion />
      </section>

      {/* CTA */}
      <section className="bg-navy py-24">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="mx-auto max-w-2xl rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-12 text-center"
          >
            <div className="flex items-center justify-center gap-2 mb-4">
              <img src={puenteIconColor} alt="" className="h-9 w-9" />
              <span className="font-display text-2xl font-bold text-white tracking-tight">PUENTE AI</span>
            </div>
            <h2 className="font-display text-3xl font-bold text-white">{t("ctaTitle")}</h2>
            <p className="mt-4 text-white/70">{t("ctaDesc")}</p>
            <Button variant="default" size="lg" className="mt-8" asChild>
              <Link to="/login?mode=signup">{t("ctaButton")} <ArrowRight className="ml-1 h-5 w-5" /></Link>
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-navy border-t border-white/10 py-10">
        <div className="container flex flex-col items-center justify-between gap-4 text-sm text-white/60 md:flex-row">
          <div className="flex items-center gap-2">
            <img src={puenteIconColor} alt="" className="h-5 w-5" />
            <span className="font-display text-sm font-semibold text-white/80">PUENTE AI</span>
            <span>© 2026</span>
          </div>
          <div className="flex gap-6">
            <span className="cursor-pointer hover:text-white">{t("privacy")}</span>
            <span className="cursor-pointer hover:text-white">{t("terms")}</span>
            <span className="cursor-pointer hover:text-white">{t("contact")}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
