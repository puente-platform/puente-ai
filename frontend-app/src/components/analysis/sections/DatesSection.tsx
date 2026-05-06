import { Calendar } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { DashboardSection } from "../DashboardSection";
import { FieldRow } from "../FieldRow";
import { fieldString, formatDate, formatPaymentTerms } from "@/lib/extraction-helpers";

type Props = {
  extraction: { fields?: Record<string, unknown> };
};

export function DatesSection({ extraction }: Props) {
  const { t } = useI18n();
  const fields = extraction.fields ?? {};

  return (
    <DashboardSection title={t("sectionDates")} icon={Calendar}>
      <div className="grid grid-cols-1 md:grid-cols-2 md:gap-x-6">
        <div>
          <FieldRow label={t("datesInvoiceDate")} value={formatDate(fields.invoice_date)} />
          <FieldRow label={t("datesDueDate")} value={formatDate(fields.due_date)} />
        </div>
        <div>
          <FieldRow label={t("datesPaymentTerms")} value={formatPaymentTerms(fields.payment_terms)} />
          <FieldRow label={t("datesPurchaseOrder")} value={fieldString(fields.purchase_order)} />
        </div>
      </div>
    </DashboardSection>
  );
}
