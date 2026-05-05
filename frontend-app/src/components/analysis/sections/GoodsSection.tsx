import { Package } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { DashboardSection } from "../DashboardSection";
import { LineItemsTable } from "../LineItemsTable";

type Props = {
  extraction: { line_items?: unknown[] };
  invoiceAmount: number;
};

export function GoodsSection({ extraction, invoiceAmount }: Props) {
  const { t } = useI18n();
  const items = (extraction.line_items ?? []) as Parameters<typeof LineItemsTable>[0]["items"];
  const count = items.length;
  const subtitle = count === 1
    ? t("goodsLineItem").replace("{count}", "1")
    : t("goodsLineItems").replace("{count}", String(count));

  return (
    <DashboardSection title={`${t("sectionGoods")}${count > 0 ? ` · ${subtitle}` : ""}`} icon={Package}>
      <LineItemsTable items={items} invoiceAmount={invoiceAmount} />
    </DashboardSection>
  );
}
