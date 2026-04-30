"use client";
import React, { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { IconMinus, IconPlus } from "@tabler/icons-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";

const faqKeys = [
  { q: "faq1Q", a: "faq1A" },
  { q: "faq2Q", a: "faq2A" },
  { q: "faq3Q", a: "faq3A" },
  { q: "faq4Q", a: "faq4A" },
  { q: "faq5Q", a: "faq5A" },
  { q: "faq6Q", a: "faq6A" },
] as const;

export default function FrequentlyAskedQuestionsAccordion() {
  const [open, setOpen] = useState<string | null>(null);
  const { t } = useI18n();

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-20">
      <div className="mb-10">
        <h2 className="text-center font-display text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          {t("faqTitle")}
        </h2>
      </div>
      <div className="divide-y divide-border">
        {faqKeys.map((faq) => (
          <FAQItem
            key={faq.q}
            question={t(faq.q)}
            answer={t(faq.a)}
            open={open}
            setOpen={setOpen}
          />
        ))}
      </div>
    </div>
  );
}

const FAQItem = ({
  question,
  answer,
  setOpen,
  open,
}: {
  question: string;
  answer: string;
  open: string | null;
  setOpen: (open: string | null) => void;
}) => {
  const isOpen = open === question;

  return (
    <div className="py-4">
      <button
        className="flex w-full items-start gap-4 text-left"
        onClick={() => setOpen(isOpen ? null : question)}
      >
        <div className="relative mt-1 flex h-5 w-5 shrink-0 items-center justify-center">
          <IconPlus
            className={cn(
              "absolute h-5 w-5 text-muted-foreground transition-all duration-200",
              isOpen ? "rotate-90 scale-0" : "rotate-0 scale-100"
            )}
          />
          <IconMinus
            className={cn(
              "absolute h-5 w-5 text-muted-foreground transition-all duration-200",
              isOpen ? "rotate-0 scale-100" : "-rotate-90 scale-0"
            )}
          />
        </div>
        <div className="flex-1">
          <span className="text-base font-medium text-foreground">
            {question}
          </span>
          <AnimatePresence mode="wait">
            {isOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="overflow-hidden"
              >
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {answer}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </button>
    </div>
  );
};
