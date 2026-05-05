import { useI18n } from "@/lib/i18n";
import type { Party } from "@/lib/extraction-helpers";

type Props = {
  label: string;
  party: Party | null;
};

export function PartyCard({ label, party }: Props) {
  const { t } = useI18n();

  if (!party) return null;

  return (
    <div>
      <p className="text-[9px] font-semibold tracking-wider text-muted-foreground/80 uppercase mb-1.5">
        {label}
      </p>
      <p className="text-sm font-display font-bold text-foreground mb-1">{party.name}</p>
      {party.address ? (
        <p className="text-xs text-muted-foreground/90 leading-snug whitespace-pre-line">
          {party.address}
        </p>
      ) : (
        <p className="text-xs text-muted-foreground/60 italic">— · {t("fieldNotExtracted")}</p>
      )}
      <div className="mt-2 space-y-0.5">
        {party.email ? (
          <p className="text-xs text-muted-foreground">{party.email}</p>
        ) : (
          <p className="text-xs text-muted-foreground/60 italic">— · {t("fieldNotExtracted")}</p>
        )}
        {party.phone ? (
          <p className="text-xs text-muted-foreground">{party.phone}</p>
        ) : (
          <p className="text-xs text-muted-foreground/60 italic">— · {t("fieldNotExtracted")}</p>
        )}
      </div>
      {party.taxId && (
        <span className="inline-flex mt-2 px-2 py-0.5 rounded-full bg-muted text-muted-foreground text-[10px]">
          {party.taxId}
        </span>
      )}
    </div>
  );
}
