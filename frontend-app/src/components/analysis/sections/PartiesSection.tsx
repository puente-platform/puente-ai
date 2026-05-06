import { Building2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { DashboardSection } from "../DashboardSection";
import { PartyCard } from "../PartyCard";
import { partyFromFields } from "@/lib/extraction-helpers";

type Props = {
  extraction: { fields?: Record<string, unknown> };
};

export function PartiesSection({ extraction }: Props) {
  const { t } = useI18n();
  const fields = extraction.fields ?? {};

  const exporter = partyFromFields(fields, "exporter");
  const importer = partyFromFields(fields, "importer");
  const shipping = partyFromFields(fields, "shipping");
  const allMissing = !exporter && !importer && !shipping;

  return (
    <DashboardSection title={t("sectionParties")} icon={Building2}>
      {allMissing ? (
        <p className="text-sm text-muted-foreground/60 italic">— · {t("fieldNotExtracted")}</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <PartyCard label={t("partyExporter")} party={exporter} />
          <PartyCard label={t("partyImporter")} party={importer} />
          <PartyCard label={t("partyShipTo")} party={shipping} />
        </div>
      )}
    </DashboardSection>
  );
}
