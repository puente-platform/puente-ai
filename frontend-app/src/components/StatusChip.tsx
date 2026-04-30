import { useI18n } from "@/lib/i18n";

type StatusKey = "uploaded" | "processing" | "extracted" | "analyzed" | "compliance_checked" | "routed" | "failed";

const statusStyles: Record<StatusKey, string> = {
  uploaded: "bg-muted text-muted-foreground",
  processing: "bg-primary/20 text-primary pill-pulse",
  extracted: "bg-ocean/15 text-ocean",
  analyzed: "bg-ocean/15 text-ocean",
  compliance_checked: "bg-emerald/15 text-emerald",
  routed: "bg-emerald/15 text-emerald",
  failed: "bg-danger-red/15 text-danger-red",
};

export default function StatusChip({ status }: { status: StatusKey }) {
  const { t } = useI18n();
  const label = t(status as any);
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${statusStyles[status]}`}>
      {label}
    </span>
  );
}
