// Pure helpers for Document AI extraction values. No React imports.
// Factored from AnalyzePage.tsx so section components can reuse.

import type { AnalyzeResponse } from "./puente-api";

type ValueLike = unknown;

export function parseAmount(v: ValueLike): number {
  if (typeof v === "number") return v;
  if (v && typeof v === "object" && "value" in (v as Record<string, unknown>)) {
    return parseAmount((v as Record<string, unknown>).value);
  }
  if (typeof v === "string") {
    const n = parseFloat(v.replace(/[^0-9.\-]/g, ""));
    return Number.isFinite(n) ? n : 0;
  }
  return 0;
}

export function fieldString(v: ValueLike): string | undefined {
  if (v == null) return undefined;
  if (typeof v === "string") return v;
  if (typeof v === "number") return String(v);
  if (typeof v === "object" && "value" in (v as Record<string, unknown>)) {
    return fieldString((v as Record<string, unknown>).value);
  }
  return undefined;
}

export function computeInvoiceAmount(a: AnalyzeResponse): number {
  const fields = a.extraction?.fields as Record<string, unknown> | undefined;
  // Check field *presence* before parsing so a legitimate $0 total doesn't
  // fall through to the line-items sum. fieldString returns undefined when the
  // field is absent/null; a defined string (even "0") means the extractor
  // found something and we should honour it, even if it parsed to 0.
  const totalRaw =
    fields?.["total_amount"] ?? fields?.["invoice_amount"] ?? fields?.["total"];
  if (fieldString(totalRaw) !== undefined) {
    return parseAmount(totalRaw);
  }
  // No header total present — derive from line-items sum.
  const items = a.extraction?.line_items ?? [];
  return items.reduce((sum, li) => sum + parseAmount((li as { amount?: unknown }).amount), 0);
}

const MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function formatDate(v: ValueLike): string | undefined {
  const s = fieldString(v);
  if (!s) return undefined;
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return undefined;
  return `${MONTHS_SHORT[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
}

export function formatPaymentTerms(v: ValueLike): string | undefined {
  const s = fieldString(v);
  if (!s) return undefined;
  const trimmed = s.trim().replace(/\s+/g, " ");
  return trimmed.length === 0 ? undefined : trimmed;
}

export type Party = {
  name: string;
  address: string | undefined;
  email: string | undefined;
  phone: string | undefined;
  taxId: string | undefined;
};

export function partyFromFields(
  fields: Record<string, unknown>,
  prefix: "exporter" | "importer" | "shipping",
): Party | null {
  const nameKey = prefix === "shipping" ? "shipping_recipient" : `${prefix}_name`;
  const addressKey = prefix === "shipping" ? "shipping_address" : `${prefix}_address`;
  const emailKey = `${prefix}_email`;
  const phoneKey = `${prefix}_phone`;
  const taxIdKey = `${prefix}_tax_id`;

  const name = fieldString(fields[nameKey]);
  if (!name) return null;

  return {
    name,
    address: fieldString(fields[addressKey]),
    email: fieldString(fields[emailKey]),
    phone: fieldString(fields[phoneKey]),
    taxId: fieldString(fields[taxIdKey]),
  };
}
