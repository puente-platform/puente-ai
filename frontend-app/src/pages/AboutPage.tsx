import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { motion } from "framer-motion";
import { ArrowRight, Sun, Moon, Shield, Globe, HeartHandshake, Lock } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";
import TrustFooter from "@/components/layout/TrustFooter";
import puenteIconColor from "@/assets/puente-icon-color.png";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: "easeOut" },
  }),
};

export default function AboutPage() {
  const { t, lang, setLang } = useI18n();
  const { theme, toggleTheme } = useTheme();

  const values = [
    { icon: Shield, title: t("aboutValue1Title"), body: t("aboutValue1Body") },
    { icon: HeartHandshake, title: t("aboutValue2Title"), body: t("aboutValue2Body") },
    { icon: Globe, title: t("aboutValue3Title"), body: t("aboutValue3Body") },
    { icon: Lock, title: t("aboutValue4Title"), body: t("aboutValue4Body") },
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Helmet>
        <html lang={lang} />
        <title>{t("aboutSeoTitle")}</title>
        <meta name="description" content={t("aboutSeoDesc")} />
        <link rel="canonical" href="https://puente.ai/about" />

        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="Puente AI" />
        <meta property="og:url" content="https://puente.ai/about" />
        <meta property="og:title" content={t("aboutSeoTitle")} />
        <meta property="og:description" content={t("aboutSeoDesc")} />
        <meta property="og:locale" content={lang === "es" ? "es_ES" : "en_US"} />
        <meta property="og:locale:alternate" content={lang === "es" ? "en_US" : "es_ES"} />
        <meta property="og:image" content="https://lovable.dev/opengraph-image-p98pqg.png" />
        <meta property="og:image:alt" content={t("aboutOgImageAlt")} />

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={t("aboutSeoTitle")} />
        <meta name="twitter:description" content={t("aboutSeoDesc")} />
        <meta name="twitter:image" content="https://lovable.dev/opengraph-image-p98pqg.png" />
        <meta name="twitter:image:alt" content={t("aboutOgImageAlt")} />
      </Helmet>

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-navy text-white">
        <div className="container flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <img src={puenteIconColor} alt="" className="h-7 w-7" />
            <span className="font-display text-lg font-bold text-white tracking-tight">PUENTE AI</span>
          </Link>

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
            <Button variant="default" size="sm" asChild>
              <Link to="/login?mode=signup" className="text-xs sm:text-sm">{t("getStarted")}</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-32 pb-16">
        <div className="pointer-events-none absolute top-20 right-[-200px] h-[500px] w-[500px] rounded-full bg-primary/5 blur-[120px]" />
        <div className="container relative">
          <motion.div initial="hidden" animate="visible" className="mx-auto max-w-3xl text-center">
            <motion.div custom={0} variants={fadeUp} className="mb-6 inline-flex items-center gap-2 rounded-full border border-gold-subtle bg-muted/50 px-4 py-1.5 text-sm text-primary">
              {t("aboutHeroEyebrow")}
            </motion.div>
            <motion.h1 custom={1} variants={fadeUp} className="font-display text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
              {t("aboutHeroTitle1")}{" "}
              <span className="text-gradient-gold">{t("aboutHeroTitle2")}</span>
            </motion.h1>
            <motion.p custom={2} variants={fadeUp} className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
              {t("aboutHeroSub")}
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Mission + Who */}
      <section className="py-12">
        <div className="container">
          <div className="mx-auto grid max-w-5xl gap-8 md:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="rounded-xl border bg-card p-8">
              <h2 className="font-display text-2xl font-bold">{t("aboutMissionTitle")}</h2>
              <p className="mt-4 text-muted-foreground leading-relaxed">{t("aboutMissionBody")}</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }} className="rounded-xl border bg-card p-8">
              <h2 className="font-display text-2xl font-bold">{t("aboutWhoTitle")}</h2>
              <p className="mt-4 text-muted-foreground leading-relaxed">{t("aboutWhoBody")}</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Approach */}
      <section className="py-12">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mx-auto max-w-3xl rounded-xl border bg-card p-8 text-center">
            <h2 className="font-display text-2xl font-bold md:text-3xl">{t("aboutApproachTitle")}</h2>
            <p className="mt-4 text-muted-foreground leading-relaxed">{t("aboutApproachBody")}</p>
          </motion.div>
        </div>
      </section>

      {/* Values */}
      <section className="py-16">
        <div className="container">
          <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center font-display text-3xl font-bold md:text-4xl">
            {t("aboutValuesTitle")}
          </motion.h2>
          <div className="mx-auto mt-12 grid max-w-5xl gap-6 md:grid-cols-2">
            {values.map((v, i) => (
              <motion.div
                key={v.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="group rounded-xl border bg-card p-6 transition-all duration-300 hover:border-primary/30 hover:glow-gold"
              >
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary/20">
                  <v.icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold">{v.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{v.body}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mx-auto max-w-3xl rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/10 via-card to-card p-10 text-center">
            <h2 className="font-display text-3xl font-bold md:text-4xl">{t("aboutCtaTitle")}</h2>
            <p className="mx-auto mt-4 max-w-xl text-muted-foreground">{t("aboutCtaBody")}</p>
            <Button variant="default" size="lg" asChild className="mt-8">
              <Link to="/login?mode=signup">
                {t("aboutCtaButton")} <ArrowRight className="ml-1 h-5 w-5" />
              </Link>
            </Button>
          </motion.div>
        </div>
      </section>

      <TrustFooter />
    </div>
  );
}
