import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useI18n } from "@/lib/i18n";

type Frame = { prefix: string; amount: string; suffix: string };

const frames: Record<"en" | "es", Frame[]> = {
  en: [
    { prefix: "Pay your Colombian supplier", amount: "$1,200 less", suffix: ". Today." },
    { prefix: "Get paid by your Mexican buyer", amount: "5 days sooner", suffix: ". Today." },
    { prefix: "Pay your Dominican supplier", amount: "$1,800 less", suffix: ". Today." },
    { prefix: "Get paid by your Peruvian buyer", amount: "5 days sooner", suffix: ". Today." },
    { prefix: "Pay your Mexican supplier", amount: "$2,400 less", suffix: ". Today." },
    { prefix: "Get paid by your Colombian buyer", amount: "5 days sooner", suffix: ". Today." },
    { prefix: "Pay your Peruvian supplier", amount: "$1,500 less", suffix: ". Today." },
    { prefix: "Get paid by your Dominican buyer", amount: "5 days sooner", suffix: ". Today." },
  ],
  es: [
    { prefix: "Págale a tu proveedor colombiano", amount: "$1,200 menos", suffix: ". Hoy." },
    { prefix: "Cóbrale a tu comprador mexicano", amount: "5 días antes", suffix: ". Hoy." },
    { prefix: "Págale a tu proveedor dominicano", amount: "$1,800 menos", suffix: ". Hoy." },
    { prefix: "Cóbrale a tu comprador peruano", amount: "5 días antes", suffix: ". Hoy." },
    { prefix: "Págale a tu proveedor mexicano", amount: "$2,400 menos", suffix: ". Hoy." },
    { prefix: "Cóbrale a tu comprador colombiano", amount: "5 días antes", suffix: ". Hoy." },
    { prefix: "Págale a tu proveedor peruano", amount: "$1,500 menos", suffix: ". Hoy." },
    { prefix: "Cóbrale a tu comprador dominicano", amount: "5 días antes", suffix: ". Hoy." },
  ],
};

const slideTransition = {
  duration: 0.7,
  ease: [0.22, 1, 0.36, 1] as const,
};

export default function AnimatedHeroText() {
  const { lang, t } = useI18n();
  const [index, setIndex] = useState(0);
  const list = frames[lang];

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % list.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [list.length]);

  const current = list[index];

  return (
    <span className="block">
      <span className="block min-h-[3.45em] font-body text-3xl font-bold leading-tight tracking-tight md:text-5xl lg:text-7xl">
        <AnimatePresence mode="wait">
          <motion.span
            key={`${lang}-${index}`}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={slideTransition}
            className="inline"
          >
            {current.prefix}{" "}
            <span className="text-gradient-gold whitespace-nowrap">{current.amount}</span>
            {current.suffix}
          </motion.span>
        </AnimatePresence>
      </span>
      <span className="mt-4 block text-xs italic text-muted-foreground md:text-sm">
        {t("heroDisclosure")}
      </span>
    </span>
  );
}
