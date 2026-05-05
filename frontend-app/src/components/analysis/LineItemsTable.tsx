import { useI18n } from "@/lib/i18n";
import { Check, AlertTriangle } from "lucide-react";
import { parseAmount } from "@/lib/extraction-helpers";

// Provisional threshold per spec §6.
// Validate empirically against ≥3 real invoices when KAN-22 lands;
// raise to 0.02 if Document AI rounding causes false discrepancies on
// clean invoices.
const RECONCILIATION_THRESHOLD = 0.01;

type LineItem = {
  description?: string | null;
  quantity?: number | null;
  unit_price?: number | null;
  amount?: number | null;
};

type Props = {
  items: LineItem[];
  invoiceAmount: number;
};

function fmtCurrency(n: number | null | undefined): string {
  if (n == null) return "—";
  return `$${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function LineItemsTable({ items, invoiceAmount }: Props) {
  const { t } = useI18n();

  if (!items || items.length === 0) {
    return null;
  }

  const sum = items.reduce((acc, li) => acc + parseAmount(li.amount), 0);
  const diff = invoiceAmount === 0 ? 0 : Math.abs(sum - invoiceAmount) / invoiceAmount;
  const matched = diff <= RECONCILIATION_THRESHOLD;

  return (
    <div>
      {/* Column headers — visible on md+ */}
      <div className="hidden md:grid grid-cols-[3fr_0.6fr_1fr_1.2fr] gap-2 px-4 py-2.5 bg-muted/50 text-[10px] font-semibold tracking-wider text-muted-foreground uppercase border border-b-0 border-border rounded-t-lg">
        <span>{t("goodsColDescription")}</span>
        <span className="text-right">{t("goodsColQty")}</span>
        <span className="text-right">{t("goodsColUnit")}</span>
        <span className="text-right">{t("goodsColAmount")}</span>
      </div>

      {/* Rows — each item appears once in the DOM.
          On md+ the inner grid makes a 4-col table row.
          On mobile the same markup collapses to a readable card via flex-wrap. */}
      <div className="border border-border md:rounded-t-none rounded-lg overflow-hidden">
        {items.map((li, i) => (
          <div
            key={i}
            className={`px-3 md:px-4 py-2.5 text-sm flex flex-wrap md:grid md:grid-cols-[3fr_0.6fr_1fr_1.2fr] gap-2 items-baseline${i > 0 ? " border-t border-border/60" : ""}`}
          >
            <span className="w-full md:w-auto font-medium md:font-normal">{li.description ?? "—"}</span>
            <span className="text-xs text-muted-foreground md:text-sm md:text-right">{li.quantity ?? "—"}</span>
            <span className="text-xs text-muted-foreground md:text-sm md:text-right">{fmtCurrency(li.unit_price)}</span>
            <span className="ml-auto md:ml-0 text-sm font-semibold md:text-right">{fmtCurrency(li.amount)}</span>
          </div>
        ))}
      </div>

      {/* Reconciliation pill */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-dashed border-border">
        <span className="text-[11px] text-muted-foreground">{t("goodsTotalLabel")}</span>
        <div className="flex items-center gap-2.5">
          <span className="text-sm font-semibold">{fmtCurrency(sum)}</span>
          {matched ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald/15 text-emerald text-[11px] font-semibold">
              <Check className="h-3 w-3" /> {t("goodsMatched")}
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-warm-amber/15 text-warm-amber text-[11px] font-semibold">
              <AlertTriangle className="h-3 w-3" /> {t("goodsDiscrepancy")}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
