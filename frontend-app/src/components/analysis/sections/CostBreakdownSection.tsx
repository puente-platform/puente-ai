import { Receipt } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { DashboardSection } from "../DashboardSection";
import { FieldRow } from "../FieldRow";
import { fieldString, parseAmount } from "@/lib/extraction-helpers";

type Props = {
  extraction: { fields?: Record<string, unknown> };
};

function fmtCurrency(n: number): string {
  return `$${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function maybeAmount(v: unknown): string | null {
  if (v == null || v === "") return null;
  const n = parseAmount(v);
  return n === 0 ? null : fmtCurrency(n);
}

export function CostBreakdownSection({ extraction }: Props) {
  const { t } = useI18n();
  const fields = extraction.fields ?? {};

  const net = maybeAmount(fields.net_amount);
  const tax = maybeAmount(fields.tax_amount);
  const freight = maybeAmount(fields.freight_charge);
  const discount = maybeAmount(fields.discount_amount);
  const total = maybeAmount(fields.total_amount ?? fields.invoice_amount);
  const currency = fieldString(fields.currency) ?? null;

  return (
    <DashboardSection title={t("sectionCost")} icon={Receipt}>
      <div className="grid grid-cols-1 md:grid-cols-2 md:gap-x-6">
        <div>
          <FieldRow label={t("costNet")} value={net} />
          <FieldRow label={t("costTax")} value={tax} />
          <FieldRow label={t("costFreight")} value={freight} />
        </div>
        <div>
          <FieldRow label={t("costCurrency")} value={currency} />
          <FieldRow label={t("costDiscount")} value={discount} />
          <div className="grid grid-cols-[1fr_auto] gap-2 py-3 border-t border-gold-subtle/40 mt-1.5 text-sm">
            <span className="font-semibold text-primary">{t("costInvoiceTotal")}</span>
            <span className="text-right text-primary font-bold text-base">
              {total ?? "—"}
            </span>
          </div>
        </div>
      </div>
    </DashboardSection>
  );
}
