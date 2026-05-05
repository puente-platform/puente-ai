import { useI18n } from "@/lib/i18n";
import { GoodsSection } from "./sections/GoodsSection";
import { CostBreakdownSection } from "./sections/CostBreakdownSection";
import { PartiesSection } from "./sections/PartiesSection";
import { DatesSection } from "./sections/DatesSection";

export type ViewMode = "operator" | "broker";

type Props = {
  extraction: { fields?: Record<string, unknown>; line_items?: unknown[] };
  invoiceAmount: number;
  viewMode?: ViewMode;
};

export function InvoiceDetailSections({
  extraction,
  invoiceAmount,
  viewMode = "operator",
}: Props) {
  const { t } = useI18n();

  if (viewMode === "broker") {
    // Forward-compat seam per spec §5. Carlos broker view is gated on
    // KAN-22 customer interview signal. Throwing keeps us honest:
    // unblocking it requires a deliberate code change with a tracked owner.
    throw new Error(
      "Broker view unimplemented — gated on KAN-22 signal. " +
      "See parked Jira ticket for owner."
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="text-center text-[10px] tracking-[0.15em] uppercase text-muted-foreground/70 my-2">
        — {t("sectionDividerLabel")} —
      </div>
      <GoodsSection extraction={extraction} invoiceAmount={invoiceAmount} />
      <CostBreakdownSection extraction={extraction} />
      <PartiesSection extraction={extraction} />
      <DatesSection extraction={extraction} />
    </div>
  );
}
