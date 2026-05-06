import { useI18n } from "@/lib/i18n";

// Type contract per spec §5: value is text-only.
// NEVER ReactNode — that would let a future contributor pass HTML
// through every PII field, defeating React's default escaping.
type Props = {
  label: string;
  value: string | number | null | undefined;
};

export function FieldRow({ label, value }: Props) {
  const { t } = useI18n();
  const isMissing = value === null || value === undefined || value === "";

  return (
    <div className="grid grid-cols-[1fr_auto] gap-2 py-2 border-b border-border/50 last:border-b-0 text-sm">
      <span className="text-muted-foreground">{label}</span>
      {isMissing ? (
        <span className="text-right text-muted-foreground/60 italic">
          —{" "}
          <span className="text-[10px] not-italic">· {t("fieldNotExtracted")}</span>
        </span>
      ) : (
        <span className="text-right font-medium">{value}</span>
      )}
    </div>
  );
}
