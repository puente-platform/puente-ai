# Analyze Dashboard — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship 4 new dashboard sections (Goods · Cost breakdown · Parties · Dates & terms) beneath the existing 3-card verdict bar on `AnalyzePage`, surfacing fields the backend already extracts. No new API surface, no new state, no new design tokens.

**Architecture:** Stacked-section layered MVP. Two new generic primitives (`<DashboardSection>`, `<FieldRow>`) + two specific composites (`<LineItemsTable>`, `<PartyCard>`) + four section components composed inside one wrapper (`<InvoiceDetailSections>`) wired into `AnalyzePage` `ResultsView` at one integration point. Forward-compat seam: `viewMode='operator' | 'broker'` prop, with `'broker'` branch deliberately throwing until KAN-22 customer interview signal lands.

**Tech Stack:** React 18 · TypeScript · Tailwind · shadcn/ui · vitest · @testing-library/react · @playwright/test (via `lovable-agent-playwright-config`) · existing `useI18n` hook with EN+ES.

**Spec reference:** `docs/superpowers/specs/2026-05-05-analyze-dashboard-phase-1-design.md`

---

## File Structure

### New files

```
frontend-app/src/lib/
  extraction-helpers.ts                                    # factored helpers + new ones

frontend-app/src/lib/__tests__/
  extraction-helpers.test.ts

frontend-app/src/test/fixtures/
  extraction-rich.ts                                       # all 14 fields + 4 line items
  extraction-sparse.ts                                     # 3 fields only

frontend-app/src/components/analysis/
  DashboardSection.tsx
  FieldRow.tsx
  LineItemsTable.tsx
  PartyCard.tsx
  InvoiceDetailSections.tsx
  sections/
    GoodsSection.tsx
    CostBreakdownSection.tsx
    PartiesSection.tsx
    DatesSection.tsx

frontend-app/src/components/analysis/__tests__/
  DashboardSection.test.tsx
  FieldRow.test.tsx
  LineItemsTable.test.tsx
  PartyCard.test.tsx
  InvoiceDetailSections.test.tsx

frontend-app/src/components/analysis/sections/__tests__/
  GoodsSection.test.tsx
  CostBreakdownSection.test.tsx
  PartiesSection.test.tsx
  DatesSection.test.tsx

frontend-app/e2e/
  analyze-detail-sections.spec.ts
  analyze-empty-state.spec.ts
```

### Modified files

- `frontend-app/src/lib/i18n.tsx` — add ~30 EN+ES keys for new section labels
- `frontend-app/src/pages/AnalyzePage.tsx` — replace inline helpers with imports (lines 218–246 region) + render `<InvoiceDetailSections>` after the 3-card grid in `ResultsView`

---

## Tasks

### Task 1: Feature branch + baseline check

**Files:** none yet — verifying environment

- [ ] **Step 1: Create feature branch**

```bash
# from the repo root
git checkout -b feat/analyze-dashboard-phase-1
```

Expected: switched to new branch.

- [ ] **Step 2: Install + verify deps in frontend-app**

```bash
cd frontend-app
npm install
```

Expected: clean install, no errors.

- [ ] **Step 3: Run baseline tests to confirm green**

```bash
npm test
```

Expected: all existing tests pass. If any fail, stop and triage before proceeding.

- [ ] **Step 4: Verify dev server boots**

```bash
npm run dev &
sleep 5
curl -sI http://localhost:8080/ | head -1
kill %1
```

Expected: `HTTP/1.1 200 OK`. (Adjust port if Vite picks differently — check `vite.config.ts`.)

- [ ] **Step 5: No commit yet** — environment-only verification.

---

### Task 2: Factor extraction helpers (TDD)

**Files:**
- Create: `frontend-app/src/lib/extraction-helpers.ts`
- Create: `frontend-app/src/lib/__tests__/extraction-helpers.test.ts`
- Modify: `frontend-app/src/pages/AnalyzePage.tsx` (lines 218–246 region — remove inline helpers, import from new file)

- [ ] **Step 1: Write the failing test file**

`frontend-app/src/lib/__tests__/extraction-helpers.test.ts`:

```typescript
import { describe, expect, it } from "vitest";
import {
  parseAmount,
  fieldString,
  computeInvoiceAmount,
  formatDate,
  formatPaymentTerms,
  partyFromFields,
} from "../extraction-helpers";

describe("parseAmount", () => {
  it("handles number directly", () => {
    expect(parseAmount(100)).toBe(100);
  });
  it("unwraps {value: x} shape from Document AI", () => {
    expect(parseAmount({ value: 250.5 })).toBe(250.5);
  });
  it("strips currency formatting from string", () => {
    expect(parseAmount("$1,234.56")).toBe(1234.56);
  });
  it("returns 0 for null / undefined / non-parseable", () => {
    expect(parseAmount(null)).toBe(0);
    expect(parseAmount(undefined)).toBe(0);
    expect(parseAmount("abc")).toBe(0);
  });
});

describe("fieldString", () => {
  it("returns string when value is a string", () => {
    expect(fieldString("hello")).toBe("hello");
  });
  it("unwraps {value: x} shape", () => {
    expect(fieldString({ value: "wrapped" })).toBe("wrapped");
  });
  it("returns undefined for null / undefined", () => {
    expect(fieldString(null)).toBeUndefined();
    expect(fieldString(undefined)).toBeUndefined();
  });
  it("coerces number to string", () => {
    expect(fieldString(42)).toBe("42");
  });
});

describe("computeInvoiceAmount", () => {
  it("prefers fields.total_amount over invoice_amount over total", () => {
    const r = { extraction: { fields: { total_amount: 100, invoice_amount: 200 } } };
    expect(computeInvoiceAmount(r as never)).toBe(100);
  });
  it("falls back to summing line_items when no header total", () => {
    const r = {
      extraction: {
        fields: {},
        line_items: [{ amount: 30 }, { amount: 70 }],
      },
    };
    expect(computeInvoiceAmount(r as never)).toBe(100);
  });
  it("returns 0 when nothing extractable", () => {
    expect(computeInvoiceAmount({ extraction: { fields: {} } } as never)).toBe(0);
  });
});

describe("formatDate", () => {
  it("formats ISO date as 'MMM D, YYYY'", () => {
    expect(formatDate("2026-04-22")).toBe("Apr 22, 2026");
  });
  it("returns undefined for null / empty", () => {
    expect(formatDate(null)).toBeUndefined();
    expect(formatDate("")).toBeUndefined();
  });
  it("returns undefined for unparseable input", () => {
    expect(formatDate("not-a-date")).toBeUndefined();
  });
});

describe("formatPaymentTerms", () => {
  it("returns the term string when present", () => {
    expect(formatPaymentTerms("Net 30")).toBe("Net 30");
  });
  it("normalizes whitespace", () => {
    expect(formatPaymentTerms("  Net  30  ")).toBe("Net 30");
  });
  it("returns undefined for null / empty", () => {
    expect(formatPaymentTerms(null)).toBeUndefined();
    expect(formatPaymentTerms("")).toBeUndefined();
  });
});

describe("partyFromFields", () => {
  const fields = {
    exporter_name: "Acme Test Exports SAS",
    exporter_address: "Calle 1 #2-3, Bogota",
    exporter_email: "test@example.com",
    exporter_phone: "+57 1 555 0000",
    exporter_tax_id: "NIT 000.000.000-0",
  };

  it("returns party object when name present", () => {
    expect(partyFromFields(fields, "exporter")).toEqual({
      name: "Acme Test Exports SAS",
      address: "Calle 1 #2-3, Bogota",
      email: "test@example.com",
      phone: "+57 1 555 0000",
      taxId: "NIT 000.000.000-0",
    });
  });

  it("returns null when name missing — graceful degradation per spec", () => {
    expect(partyFromFields({}, "exporter")).toBeNull();
  });

  it("preserves missing fields as undefined (not empty string)", () => {
    const sparse = { exporter_name: "Acme" };
    expect(partyFromFields(sparse, "exporter")).toEqual({
      name: "Acme",
      address: undefined,
      email: undefined,
      phone: undefined,
      taxId: undefined,
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend-app
npm test -- extraction-helpers
```

Expected: FAIL with "Cannot find module '../extraction-helpers'".

- [ ] **Step 3: Write the minimal implementation**

`frontend-app/src/lib/extraction-helpers.ts`:

```typescript
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
  const direct = fields
    ? parseAmount(fields["total_amount"] ?? fields["invoice_amount"] ?? fields["total"])
    : 0;
  if (direct > 0) return direct;
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
```

- [ ] **Step 4: Run test to verify all pass**

```bash
npm test -- extraction-helpers
```

Expected: all 18 tests PASS.

- [ ] **Step 5: Update AnalyzePage to import from new file**

In `frontend-app/src/pages/AnalyzePage.tsx`:

1. Add to existing imports near top of file:

```typescript
import { parseAmount, fieldString, computeInvoiceAmount } from "@/lib/extraction-helpers";
```

2. Delete the inline `parseAmount`, `fieldString`, `computeInvoiceAmount` functions (currently at lines 218–246).

- [ ] **Step 6: Run AnalyzePage's existing render to verify no regression**

```bash
npm test
```

Expected: all tests still pass (existing AnalyzePage usage of those helpers now resolves through the imported module — same behavior).

- [ ] **Step 7: Commit**

```bash
git add frontend-app/src/lib/extraction-helpers.ts \
        frontend-app/src/lib/__tests__/extraction-helpers.test.ts \
        frontend-app/src/pages/AnalyzePage.tsx
git commit -m "feat(analyze): factor extraction helpers into lib/extraction-helpers

Moves parseAmount, fieldString, computeInvoiceAmount out of
AnalyzePage so the upcoming Phase 1 dashboard section components
can import them. Adds formatDate, formatPaymentTerms, and
partyFromFields. Zero behavior change to existing helpers.

Refs: docs/superpowers/specs/2026-05-05-analyze-dashboard-phase-1-design.md §5
"
```

---

### Task 3: Synthetic-PII test fixtures

**Files:**
- Create: `frontend-app/src/test/fixtures/extraction-rich.ts`
- Create: `frontend-app/src/test/fixtures/extraction-sparse.ts`

Per spec §8 binding rules: NO real customer names, NO real EIN/NIT, RFC 2606 email domains only, sentinel-format identifiers.

- [ ] **Step 1: Create rich fixture**

`frontend-app/src/test/fixtures/extraction-rich.ts`:

```typescript
// Synthetic PII per spec §8 binding rules.
// All identifiers are deliberately fictional and fail public-registry lookup.

export const extractionRich = {
  fields: {
    invoice_id: "INV-TEST-0001",
    invoice_date: "2026-04-22",
    due_date: "2026-05-22",

    total_amount: 60462,
    net_amount: 56000,
    tax_amount: 1600,
    freight_charge: 2862,
    currency: "USD",

    exporter_name: "Acme Test Exports SAS",
    exporter_address: "Calle Test #1-2, Test City, Country",
    exporter_email: "ap@example.org",
    exporter_phone: "+1 555 555 0100",
    exporter_tax_id: "NIT 000.000.000-0",

    importer_name: "Liquidation Test Co",
    importer_address: "1 Test Way, Doral, FL 33172",
    importer_email: "ops@example.com",
    importer_tax_id: "EIN 00-0000000",

    shipping_recipient: "Test Warehouse #0",
    shipping_address: "1 Test Way Bay 0, Doral, FL 33172",

    purchase_order: "PO-TEST-2026-0001",
    payment_terms: "Net 30",
  },
  line_items: [
    { description: "Test Item A", quantity: 120, unit_price: 385.0, amount: 46200.0 },
    { description: "Test Item B", quantity: 40, unit_price: 245.0, amount: 9800.0 },
    { description: "Test Item C", quantity: 500, unit_price: 3.2, amount: 1600.0 },
    { description: "Test Item D — handling", quantity: null, unit_price: null, amount: 2862.0 },
  ],
};
```

- [ ] **Step 2: Create sparse fixture**

`frontend-app/src/test/fixtures/extraction-sparse.ts`:

```typescript
// Forces empty-state UX coverage. Only 3 fields populated.

export const extractionSparse = {
  fields: {
    total_amount: 60462,
    currency: "USD",
    exporter_name: "Acme Test Exports SAS",
  },
  line_items: [],
};
```

- [ ] **Step 3: Commit**

```bash
git add frontend-app/src/test/fixtures/extraction-rich.ts \
        frontend-app/src/test/fixtures/extraction-sparse.ts
git commit -m "test(analyze): add synthetic-PII fixtures for dashboard sections

Two fixtures (rich + sparse) for unit + integration tests of the
Phase 1 dashboard sections. All identifiers are fictional sentinels
per spec §8 — no real EIN, no real NIT, only RFC 2606 email domains.
"
```

---

### Task 4: Add i18n keys (EN + ES)

**Files:**
- Modify: `frontend-app/src/lib/i18n.tsx` — append ~30 keys to both EN and ES translation maps

- [ ] **Step 1: Locate the translation maps**

```bash
grep -n "^const messages" frontend-app/src/lib/i18n.tsx | head -5
grep -n '^\s*en:' frontend-app/src/lib/i18n.tsx | head -5
```

Expected: identifies the EN/ES dictionary entries. Read 30 lines around each before editing.

- [ ] **Step 2: Append new keys to EN translations**

Add to the EN translation block in `frontend-app/src/lib/i18n.tsx` (alphabetize within block to match existing style):

```typescript
// — Phase 1 dashboard expansion
sectionGoods: "Goods",
sectionCost: "Cost breakdown",
sectionParties: "Parties",
sectionDates: "Dates & terms",

goodsLineItems: "{count} line items",
goodsLineItem: "{count} line item",
goodsColDescription: "Description",
goodsColQty: "Qty",
goodsColUnit: "Unit",
goodsColAmount: "Amount",
goodsTotalLabel: "Total of line items",
goodsMatched: "Matched",
goodsDiscrepancy: "Discrepancy",

costNet: "Net amount",
costTax: "Tax",
costFreight: "Freight",
costDiscount: "Discount",
costCurrency: "Currency",
costInvoiceTotal: "Invoice total",

partyExporter: "Exporter",
partyImporter: "Importer",
partyShipTo: "Ship to",

datesInvoiceDate: "Invoice date",
datesDueDate: "Due date",
datesPaymentTerms: "Payment terms",
datesPurchaseOrder: "Purchase order",

fieldNotExtracted: "Not extracted",
sectionDividerLabel: "Invoice detail",
```

- [ ] **Step 3: Append matching ES translations**

Add the same keys to the ES translation block:

```typescript
// — Phase 1 dashboard expansion
sectionGoods: "Mercancía",
sectionCost: "Desglose de costos",
sectionParties: "Partes",
sectionDates: "Fechas y términos",

goodsLineItems: "{count} artículos",
goodsLineItem: "{count} artículo",
goodsColDescription: "Descripción",
goodsColQty: "Cantidad",
goodsColUnit: "Unitario",
goodsColAmount: "Monto",
goodsTotalLabel: "Total de artículos",
goodsMatched: "Coincide",
goodsDiscrepancy: "Discrepancia",

costNet: "Monto neto",
costTax: "Impuesto",
costFreight: "Flete",
costDiscount: "Descuento",
costCurrency: "Moneda",
costInvoiceTotal: "Total de factura",

partyExporter: "Exportador",
partyImporter: "Importador",
partyShipTo: "Enviar a",

datesInvoiceDate: "Fecha de factura",
datesDueDate: "Fecha de vencimiento",
datesPaymentTerms: "Términos de pago",
datesPurchaseOrder: "Orden de compra",

fieldNotExtracted: "No extraído",
sectionDividerLabel: "Detalle de factura",
```

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd frontend-app
npx tsc --noEmit -p tsconfig.app.json
```

Expected: zero errors. (If the i18n type definition is a string-literal union of keys, both EN and ES must have all the new keys for typecheck to pass.)

- [ ] **Step 5: Run test suite to confirm no regression**

```bash
npm test
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add frontend-app/src/lib/i18n.tsx
git commit -m "feat(analyze): add i18n keys for Phase 1 dashboard sections

~30 new EN+ES keys for Goods / Cost / Parties / Dates sections,
the empty-state hint, and the section divider label.
"
```

---

### Task 5: `<DashboardSection>` primitive (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/DashboardSection.tsx`
- Create: `frontend-app/src/components/analysis/__tests__/DashboardSection.test.tsx`

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/__tests__/DashboardSection.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Package } from "lucide-react";
import { DashboardSection } from "../DashboardSection";

describe("DashboardSection", () => {
  it("renders the title via children of label", () => {
    render(<DashboardSection title="Goods">body</DashboardSection>);
    expect(screen.getByText("Goods")).toBeInTheDocument();
  });

  it("renders children inside the body", () => {
    render(<DashboardSection title="Goods"><span data-testid="kid">x</span></DashboardSection>);
    expect(screen.getByTestId("kid")).toBeInTheDocument();
  });

  it("renders icon when provided", () => {
    render(<DashboardSection title="Goods" icon={Package}>body</DashboardSection>);
    expect(screen.getByTestId("dashboard-section-icon")).toBeInTheDocument();
  });

  it("works without an icon", () => {
    render(<DashboardSection title="Goods">body</DashboardSection>);
    expect(screen.queryByTestId("dashboard-section-icon")).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
cd frontend-app
npm test -- DashboardSection
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/DashboardSection.tsx`:

```typescript
import { ReactNode } from "react";
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

type Props = {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
};

export function DashboardSection({ title, icon: Icon, children }: Props) {
  return (
    <Card className="bg-gradient-card border-gold-subtle">
      <CardContent className="p-4 md:p-5">
        <div className="flex items-center gap-2 mb-3 md:mb-4">
          {Icon && <Icon data-testid="dashboard-section-icon" className="h-3.5 w-3.5 text-muted-foreground" />}
          <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
            {title}
          </p>
        </div>
        {children}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- DashboardSection
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/DashboardSection.tsx \
        frontend-app/src/components/analysis/__tests__/DashboardSection.test.tsx
git commit -m "feat(analyze): add DashboardSection primitive

Card shell + 11px uppercase tracking-wider label header + optional
Lucide icon. Reused by all 4 Phase 1 sections. No new design tokens.
"
```

---

### Task 6: `<FieldRow>` primitive (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/FieldRow.tsx`
- Create: `frontend-app/src/components/analysis/__tests__/FieldRow.test.tsx`

Critical: `value` prop must be typed `string | number | null | undefined` per security finding (NOT `ReactNode`).

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/__tests__/FieldRow.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { FieldRow } from "../FieldRow";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

describe("FieldRow", () => {
  it("renders label and value when present", () => {
    render(withI18n(<FieldRow label="Net amount" value="$56,000.00" />));
    expect(screen.getByText("Net amount")).toBeInTheDocument();
    expect(screen.getByText("$56,000.00")).toBeInTheDocument();
  });

  it("renders em-dash and 'Not extracted' hint when value is null", () => {
    render(withI18n(<FieldRow label="Discount" value={null} />));
    expect(screen.getByText("—")).toBeInTheDocument();
    expect(screen.getByText(/not extracted/i)).toBeInTheDocument();
  });

  it("treats undefined the same as null", () => {
    render(withI18n(<FieldRow label="Discount" value={undefined} />));
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("treats empty string the same as null", () => {
    render(withI18n(<FieldRow label="Discount" value="" />));
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("accepts number value", () => {
    render(withI18n(<FieldRow label="Qty" value={42} />));
    expect(screen.getByText("42")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- FieldRow
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/FieldRow.tsx`:

```typescript
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
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- FieldRow
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/FieldRow.tsx \
        frontend-app/src/components/analysis/__tests__/FieldRow.test.tsx
git commit -m "feat(analyze): add FieldRow primitive (single source of truth for empty-state)

Renders label/value pair. When value is null/undefined/empty, shows
em-dash + 'Not extracted' hint. value prop is constrained to
string|number|null|undefined per spec §5 security contract — NOT
ReactNode, to prevent future contributors from passing HTML through
the row primitive that touches every PII field.
"
```

---

### Task 7: `<LineItemsTable>` (TDD with reconciliation pill)

**Files:**
- Create: `frontend-app/src/components/analysis/LineItemsTable.tsx`
- Create: `frontend-app/src/components/analysis/__tests__/LineItemsTable.test.tsx`

The reconciliation threshold is 1% (provisional per spec §6 — flag for empirical validation against real invoices when KAN-22 lands).

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/__tests__/LineItemsTable.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { LineItemsTable } from "../LineItemsTable";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

const items = [
  { description: "Test A", quantity: 10, unit_price: 5, amount: 50 },
  { description: "Test B", quantity: 1, unit_price: 50, amount: 50 },
];

describe("LineItemsTable", () => {
  it("renders all items", () => {
    render(withI18n(<LineItemsTable items={items} invoiceAmount={100} />));
    expect(screen.getByText("Test A")).toBeInTheDocument();
    expect(screen.getByText("Test B")).toBeInTheDocument();
  });

  it("shows Matched pill when sum of items equals invoice (within 1%)", () => {
    render(withI18n(<LineItemsTable items={items} invoiceAmount={100} />));
    expect(screen.getByText(/matched/i)).toBeInTheDocument();
  });

  it("shows Discrepancy pill when sum of items differs by > 1%", () => {
    render(withI18n(<LineItemsTable items={items} invoiceAmount={200} />));
    expect(screen.getByText(/discrepancy/i)).toBeInTheDocument();
  });

  it("treats 1% boundary as matched (inclusive)", () => {
    // 100 vs 101 = 1% diff exactly → matched
    render(withI18n(<LineItemsTable items={items} invoiceAmount={101} />));
    expect(screen.getByText(/matched/i)).toBeInTheDocument();
  });

  it("renders nothing when items is empty", () => {
    const { container } = render(withI18n(<LineItemsTable items={[]} invoiceAmount={0} />));
    expect(container.querySelector("table")).toBeNull();
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- LineItemsTable
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/LineItemsTable.tsx`:

```typescript
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
    <>
      {/* Desktop: 4-col grid table */}
      <div className="hidden md:block border border-border rounded-lg overflow-hidden">
        <div className="grid grid-cols-[3fr_0.6fr_1fr_1.2fr] gap-2 px-4 py-2.5 bg-muted/50 text-[10px] font-semibold tracking-wider text-muted-foreground uppercase">
          <span>{t("goodsColDescription")}</span>
          <span className="text-right">{t("goodsColQty")}</span>
          <span className="text-right">{t("goodsColUnit")}</span>
          <span className="text-right">{t("goodsColAmount")}</span>
        </div>
        {items.map((li, i) => (
          <div
            key={i}
            className="grid grid-cols-[3fr_0.6fr_1fr_1.2fr] gap-2 px-4 py-2.5 border-t border-border/60 text-sm"
          >
            <span>{li.description ?? "—"}</span>
            <span className="text-right">{li.quantity ?? "—"}</span>
            <span className="text-right">{fmtCurrency(li.unit_price)}</span>
            <span className="text-right font-semibold">{fmtCurrency(li.amount)}</span>
          </div>
        ))}
      </div>

      {/* Mobile: stacked cards */}
      <div className="md:hidden space-y-2">
        {items.map((li, i) => (
          <div key={i} className="border border-border rounded-lg p-3 text-sm">
            <p className="font-medium mb-1.5">{li.description ?? "—"}</p>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{li.quantity ?? "—"} × {fmtCurrency(li.unit_price)}</span>
              <span className="font-semibold text-foreground">{fmtCurrency(li.amount)}</span>
            </div>
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
    </>
  );
}
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- LineItemsTable
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/LineItemsTable.tsx \
        frontend-app/src/components/analysis/__tests__/LineItemsTable.test.tsx
git commit -m "feat(analyze): add LineItemsTable with reconciliation pill

Responsive table (4-col desktop / stacked mobile). Free trust signal:
sum of line items vs invoice header total → green Matched pill within
1%, amber Discrepancy outside. Threshold is provisional per spec §6;
revisit empirically when real invoices land via KAN-22.
"
```

---

### Task 8: `<PartyCard>` (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/PartyCard.tsx`
- Create: `frontend-app/src/components/analysis/__tests__/PartyCard.test.tsx`

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/__tests__/PartyCard.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { PartyCard } from "../PartyCard";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

const fullParty = {
  name: "Acme Test Exports SAS",
  address: "Calle Test #1-2, Test City",
  email: "ap@example.org",
  phone: "+1 555 555 0100",
  taxId: "NIT 000.000.000-0",
};

describe("PartyCard", () => {
  it("renders all fields when present", () => {
    render(withI18n(<PartyCard label="Exporter" party={fullParty} />));
    expect(screen.getByText("Acme Test Exports SAS")).toBeInTheDocument();
    expect(screen.getByText("Calle Test #1-2, Test City")).toBeInTheDocument();
    expect(screen.getByText("ap@example.org")).toBeInTheDocument();
    expect(screen.getByText("+1 555 555 0100")).toBeInTheDocument();
    expect(screen.getByText("NIT 000.000.000-0")).toBeInTheDocument();
  });

  it("renders 'Not extracted' hint for partial fields", () => {
    const partial = { ...fullParty, phone: undefined };
    render(withI18n(<PartyCard label="Exporter" party={partial} />));
    // At least one "Not extracted" hint visible
    expect(screen.getAllByText(/not extracted/i).length).toBeGreaterThan(0);
  });

  it("returns null when party is null (graceful skip)", () => {
    const { container } = render(withI18n(<PartyCard label="Exporter" party={null} />));
    expect(container.firstChild).toBeNull();
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- PartyCard
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/PartyCard.tsx`:

```typescript
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
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- PartyCard
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/PartyCard.tsx \
        frontend-app/src/components/analysis/__tests__/PartyCard.test.tsx
git commit -m "feat(analyze): add PartyCard component

Vertical block: bold name → address → muted contact lines → tax-id
badge. Returns null when party is null (graceful per spec §5 — section
heading still renders when individual party is missing).
"
```

---

### Task 9: `<GoodsSection>` (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/sections/GoodsSection.tsx`
- Create: `frontend-app/src/components/analysis/sections/__tests__/GoodsSection.test.tsx`

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/sections/__tests__/GoodsSection.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { GoodsSection } from "../GoodsSection";
import { extractionRich } from "@/test/fixtures/extraction-rich";
import { extractionSparse } from "@/test/fixtures/extraction-sparse";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

describe("GoodsSection", () => {
  it("renders heading + line items count against rich fixture", () => {
    render(withI18n(<GoodsSection extraction={extractionRich} invoiceAmount={60462} />));
    expect(screen.getByText(/goods/i)).toBeInTheDocument();
    expect(screen.getByText("Test Item A")).toBeInTheDocument();
  });

  it("renders heading even with no line items (sparse fixture)", () => {
    render(withI18n(<GoodsSection extraction={extractionSparse} invoiceAmount={60462} />));
    expect(screen.getByText(/goods/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- GoodsSection
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/sections/GoodsSection.tsx`:

```typescript
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
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- GoodsSection
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/sections/GoodsSection.tsx \
        frontend-app/src/components/analysis/sections/__tests__/GoodsSection.test.tsx
git commit -m "feat(analyze): add GoodsSection composing DashboardSection + LineItemsTable"
```

---

### Task 10: `<CostBreakdownSection>` (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/sections/CostBreakdownSection.tsx`
- Create: `frontend-app/src/components/analysis/sections/__tests__/CostBreakdownSection.test.tsx`

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/sections/__tests__/CostBreakdownSection.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { CostBreakdownSection } from "../CostBreakdownSection";
import { extractionRich } from "@/test/fixtures/extraction-rich";
import { extractionSparse } from "@/test/fixtures/extraction-sparse";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

describe("CostBreakdownSection", () => {
  it("renders all cost rows from rich fixture", () => {
    render(withI18n(<CostBreakdownSection extraction={extractionRich} />));
    expect(screen.getByText(/cost breakdown/i)).toBeInTheDocument();
    expect(screen.getByText("$56,000.00")).toBeInTheDocument(); // net
    expect(screen.getByText("$60,462.00")).toBeInTheDocument(); // total
  });

  it("renders Not extracted hints from sparse fixture", () => {
    render(withI18n(<CostBreakdownSection extraction={extractionSparse} />));
    expect(screen.getAllByText(/not extracted/i).length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- CostBreakdownSection
```

Expected: FAIL.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/sections/CostBreakdownSection.tsx`:

```typescript
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
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- CostBreakdownSection
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/sections/CostBreakdownSection.tsx \
        frontend-app/src/components/analysis/sections/__tests__/CostBreakdownSection.test.tsx
git commit -m "feat(analyze): add CostBreakdownSection with two-column FieldRow grid"
```

---

### Task 11: `<PartiesSection>` (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/sections/PartiesSection.tsx`
- Create: `frontend-app/src/components/analysis/sections/__tests__/PartiesSection.test.tsx`

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/sections/__tests__/PartiesSection.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { PartiesSection } from "../PartiesSection";
import { extractionRich } from "@/test/fixtures/extraction-rich";
import { extractionSparse } from "@/test/fixtures/extraction-sparse";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

describe("PartiesSection", () => {
  it("renders all 3 parties when extracted (rich)", () => {
    render(withI18n(<PartiesSection extraction={extractionRich} />));
    expect(screen.getByText("Acme Test Exports SAS")).toBeInTheDocument();
    expect(screen.getByText("Liquidation Test Co")).toBeInTheDocument();
    expect(screen.getByText("Test Warehouse #0")).toBeInTheDocument();
  });

  it("renders only the present party (sparse — only exporter)", () => {
    render(withI18n(<PartiesSection extraction={extractionSparse} />));
    expect(screen.getByText("Acme Test Exports SAS")).toBeInTheDocument();
    expect(screen.queryByText("Liquidation Test Co")).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- PartiesSection
```

Expected: FAIL.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/sections/PartiesSection.tsx`:

```typescript
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

  return (
    <DashboardSection title={t("sectionParties")} icon={Building2}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <PartyCard label={t("partyExporter")} party={exporter} />
        <PartyCard label={t("partyImporter")} party={importer} />
        <PartyCard label={t("partyShipTo")} party={shipping} />
      </div>
    </DashboardSection>
  );
}
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- PartiesSection
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/sections/PartiesSection.tsx \
        frontend-app/src/components/analysis/sections/__tests__/PartiesSection.test.tsx
git commit -m "feat(analyze): add PartiesSection composing 3 PartyCards"
```

---

### Task 12: `<DatesSection>` (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/sections/DatesSection.tsx`
- Create: `frontend-app/src/components/analysis/sections/__tests__/DatesSection.test.tsx`

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/sections/__tests__/DatesSection.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { DatesSection } from "../DatesSection";
import { extractionRich } from "@/test/fixtures/extraction-rich";
import { extractionSparse } from "@/test/fixtures/extraction-sparse";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

describe("DatesSection", () => {
  it("renders formatted dates and terms (rich)", () => {
    render(withI18n(<DatesSection extraction={extractionRich} />));
    expect(screen.getByText(/dates & terms|fechas y términos/i)).toBeInTheDocument();
    expect(screen.getByText("Apr 22, 2026")).toBeInTheDocument();
    expect(screen.getByText("Net 30")).toBeInTheDocument();
    expect(screen.getByText("PO-TEST-2026-0001")).toBeInTheDocument();
  });

  it("renders Not extracted hints when missing (sparse)", () => {
    render(withI18n(<DatesSection extraction={extractionSparse} />));
    expect(screen.getAllByText(/not extracted/i).length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- DatesSection
```

Expected: FAIL.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/sections/DatesSection.tsx`:

```typescript
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
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- DatesSection
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/sections/DatesSection.tsx \
        frontend-app/src/components/analysis/sections/__tests__/DatesSection.test.tsx
git commit -m "feat(analyze): add DatesSection with formatted dates + payment terms"
```

---

### Task 13: `<InvoiceDetailSections>` wrapper + viewMode seam (TDD)

**Files:**
- Create: `frontend-app/src/components/analysis/InvoiceDetailSections.tsx`
- Create: `frontend-app/src/components/analysis/__tests__/InvoiceDetailSections.test.tsx`

The `viewMode="broker"` branch must throw — proves the forward-compat seam isn't accidentally live.

- [ ] **Step 1: Write failing test**

`frontend-app/src/components/analysis/__tests__/InvoiceDetailSections.test.tsx`:

```typescript
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider } from "@/lib/i18n";
import { InvoiceDetailSections } from "../InvoiceDetailSections";
import { extractionRich } from "@/test/fixtures/extraction-rich";

function withI18n(node: React.ReactNode) {
  return <I18nProvider>{node}</I18nProvider>;
}

describe("InvoiceDetailSections", () => {
  it("renders all 4 sections in order in operator mode (default)", () => {
    render(withI18n(<InvoiceDetailSections extraction={extractionRich} invoiceAmount={60462} />));
    expect(screen.getByText(/goods/i)).toBeInTheDocument();
    expect(screen.getByText(/cost breakdown/i)).toBeInTheDocument();
    expect(screen.getByText(/parties/i)).toBeInTheDocument();
    expect(screen.getByText(/dates/i)).toBeInTheDocument();
  });

  it("throws explicitly when viewMode='broker' (forward-compat seam, not implemented)", () => {
    // Suppress error logging in test output
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => {
      render(withI18n(
        <InvoiceDetailSections extraction={extractionRich} invoiceAmount={60462} viewMode="broker" />
      ));
    }).toThrow(/broker view unimplemented/i);
    spy.mockRestore();
  });
});
```

(Add `import { vi } from "vitest";` to the imports.)

- [ ] **Step 2: Run test — expect fail**

```bash
npm test -- InvoiceDetailSections
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

`frontend-app/src/components/analysis/InvoiceDetailSections.tsx`:

```typescript
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
```

- [ ] **Step 4: Run test — expect pass**

```bash
npm test -- InvoiceDetailSections
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend-app/src/components/analysis/InvoiceDetailSections.tsx \
        frontend-app/src/components/analysis/__tests__/InvoiceDetailSections.test.tsx
git commit -m "feat(analyze): add InvoiceDetailSections wrapper + viewMode seam

Composes the 4 Phase 1 sections in spec order (Goods → Cost →
Parties → Dates). Default viewMode='operator' implements Phase 1.
viewMode='broker' deliberately throws — forward-compat seam for the
future Carlos broker view, gated on KAN-22 customer interview signal.
A parked Jira ticket owns the un-throwing.
"
```

---

### Task 14: Wire into `AnalyzePage` `ResultsView`

**Files:**
- Modify: `frontend-app/src/pages/AnalyzePage.tsx` — add `<InvoiceDetailSections>` to the `ResultsView` return JSX, after the existing 3-card grid

- [ ] **Step 1: Read current ResultsView return**

```bash
grep -n "Three Result Cards\|<\\/div>\\s*\\)\\;" frontend-app/src/pages/AnalyzePage.tsx | head -5
```

Find the closing of the 3-card grid (`grid grid-cols-1 md:grid-cols-3 gap-4`) — its closing `</div>` is currently the last child before `ResultsView`'s outer `</div>`.

- [ ] **Step 2: Add the import at top of AnalyzePage.tsx**

```typescript
import { InvoiceDetailSections } from "@/components/analysis/InvoiceDetailSections";
```

- [ ] **Step 3: Render the new wrapper after the 3-card grid**

In `ResultsView`, after the existing closing `</div>` of the 3-card grid (the one wrapping Fraud + Compliance + Routing cards), insert:

```typescript
<InvoiceDetailSections
  extraction={analysis.extraction ?? {}}
  invoiceAmount={invoiceAmount}
/>
```

The full structure should look like:

```typescript
return (
  <div className="space-y-4 md:space-y-6">
    {/* Invoice Header */}
    <Card>...</Card>

    {/* Three Result Cards */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      ...existing 3 cards...
    </div>

    {/* Phase 1 detail sections */}
    <InvoiceDetailSections
      extraction={analysis.extraction ?? {}}
      invoiceAmount={invoiceAmount}
    />
  </div>
);
```

- [ ] **Step 4: Verify dev server renders**

```bash
cd frontend-app
npm run dev &
sleep 5
curl -sI http://localhost:8080/ | head -1
kill %1
```

Expected: 200 OK. (Manual visual verification happens in Task 16.)

- [ ] **Step 5: Run full test suite**

```bash
npm test
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add frontend-app/src/pages/AnalyzePage.tsx
git commit -m "feat(analyze): wire InvoiceDetailSections into ResultsView

One integration point: render the new sections after the existing
3-card verdict bar. Existing cards unchanged.
"
```

---

### Task 15: Playwright e2e specs

**Files:**
- Create: `frontend-app/e2e/analyze-detail-sections.spec.ts`
- Create: `frontend-app/e2e/analyze-empty-state.spec.ts`

Note: Playwright is configured via `lovable-agent-playwright-config`. The default test directory is `e2e/`. If the lib expects a different path, adjust accordingly.

- [ ] **Step 1: Create e2e directory + happy-path spec**

```bash
mkdir -p frontend-app/e2e
```

`frontend-app/e2e/analyze-detail-sections.spec.ts`:

```typescript
import { test, expect } from "@playwright/test";

test.describe("Analyze dashboard — Phase 1 detail sections", () => {
  test("renders all 4 new sections after analyzing the deterministic test invoice", async ({ page }) => {
    await page.goto("/analyze");

    // Upload the deterministic test invoice from PR #49
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles("docs/test-assets/commercial-invoice-dummy-filled-000090.pdf");

    // Wait for results to render (analyze + route together cap ~30s in dev)
    await expect(page.getByText(/goods/i)).toBeVisible({ timeout: 60_000 });
    await expect(page.getByText(/cost breakdown/i)).toBeVisible();
    await expect(page.getByText(/parties/i)).toBeVisible();
    await expect(page.getByText(/dates/i)).toBeVisible();

    // Reconciliation pill present (matched OR discrepancy — empirical)
    const matched = await page.getByText(/matched/i).isVisible().catch(() => false);
    const discrepancy = await page.getByText(/discrepancy/i).isVisible().catch(() => false);
    expect(matched || discrepancy).toBe(true);
  });
});
```

- [ ] **Step 2: Create empty-state spec**

`frontend-app/e2e/analyze-empty-state.spec.ts`:

```typescript
import { test, expect } from "@playwright/test";

test.describe("Analyze dashboard — empty-state coverage", () => {
  test("'Not extracted' hints render gracefully when fields are missing", async ({ page }) => {
    // This spec mocks the analyze response to force the sparse fixture state.
    await page.route("**/api/v1/analyze", async (route) => {
      const sparseFixture = {
        document_id: "test-doc",
        extraction: {
          fields: { total_amount: 60462, currency: "USD", exporter_name: "Acme Test" },
          line_items: [],
        },
        analysis: { fraud_assessment: { score: 0, flags: [] }, compliance_assessment: {} },
      };
      await route.fulfill({ status: 200, body: JSON.stringify(sparseFixture) });
    });

    await page.goto("/analyze");
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles("docs/test-assets/commercial-invoice-dummy-filled-000090.pdf");

    // Sections still render
    await expect(page.getByText(/cost breakdown/i)).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/parties/i)).toBeVisible();

    // At least one Not extracted hint visible
    await expect(page.getByText(/not extracted/i).first()).toBeVisible();

    // Sections don't crash — page is still interactive
    await expect(page.getByText(/Acme Test/)).toBeVisible();
  });
});
```

- [ ] **Step 3: Run Playwright specs**

```bash
cd frontend-app
npx playwright test
```

Expected: 2 specs PASS. If Playwright's first invocation needs browser binaries: `npx playwright install`.

- [ ] **Step 4: Commit**

```bash
git add frontend-app/e2e/analyze-detail-sections.spec.ts \
        frontend-app/e2e/analyze-empty-state.spec.ts
git commit -m "test(analyze): add Playwright e2e specs for Phase 1 sections

Two specs:
1. Happy path — upload deterministic test invoice, assert all 4
   sections render with reconciliation pill.
2. Empty-state — mock sparse extraction response, assert Not extracted
   hints render and sections don't crash on missing fields.
"
```

---

### Task 16: Verification (manual smoke tests)

**Files:** none — verification only

- [ ] **Step 1: Mobile viewport check (375px)**

```bash
cd frontend-app
npm run dev
```

In browser DevTools, switch viewport to iPhone SE (375×667) and:
1. Navigate to `/analyze`
2. Upload `docs/test-assets/commercial-invoice-dummy-filled-000090.pdf`
3. Confirm: line-items table collapses to per-item cards (NOT a horizontal scroll), all 4 sections stack cleanly, no overflow.

- [ ] **Step 2: i18n switch check**

In dev preview, toggle EN ↔ ES (the existing language toggle). Confirm: every label in the 4 new sections translates. No untranslated raw keys visible.

- [ ] **Step 3: Production-bundle audit**

```bash
cd frontend-app
npm run build
grep -r "Acme Test Exports SAS" dist/ 2>/dev/null
echo "exit=$?"
```

Expected: `exit=1` (no matches). If `exit=0`, a fixture is leaking into the production bundle — remove the unwanted import.

- [ ] **Step 4: Console-PII grep on the diff**

```bash
git diff main..HEAD -- frontend-app/src/components/analysis/ frontend-app/src/lib/extraction-helpers.ts \
  | grep -E "console\.(log|warn|error|info|debug)\(" \
  | grep -E "extraction|fields|line_items|party|exporter|importer"
echo "exit=$?"
```

Expected: `exit=1` (no matches). If `exit=0`, a logging call references PII data — remove it before merge per spec §5 binding rule.

- [ ] **Step 5: Take screenshots for PR description**

In dev preview, capture:
1. Rich fixture, EN, desktop viewport (1280px)
2. Rich fixture, ES, desktop viewport
3. Rich fixture, EN, mobile viewport (375px)
4. Sparse fixture (or a real partial-extraction invoice), EN, desktop — proves "Not extracted" pattern

Save to `frontend-app/.screenshots/phase-1/` (gitignored — for PR description only).

- [ ] **Step 6: No commit** (verification only)

---

### Task 17: File parked Jira ticket for `viewMode="broker"` owner

**Files:** none — Jira-only

This is a NON-CODE task. Required per spec §5 ("Owner-ship requirement") and §9 acceptance criteria.

- [ ] **Step 1: Create the ticket via Atlassian MCP**

Title: `Implement viewMode='broker' branch in InvoiceDetailSections`

Description (paste into Jira):

```
Forward-compat seam currently throws: backend/frontend-app/src/components/analysis/InvoiceDetailSections.tsx

Status: PARKED. Un-throw when KAN-22 customer interview signal lands AND
broker product surface is approved by ceo-scope. Implementation work:

1. Define `BrokerViewMode` section composition (likely: trade-document cut
   per spec §3 (ii) — Header / Parties / Goods / Charges / Terms).
2. Replace the `throw` with the broker section composition.
3. Update `InvoiceDetailSections.test.tsx` to remove the explicit-throw
   assertion.
4. Add new e2e spec for broker viewMode.

Source spec: docs/superpowers/specs/2026-05-05-analyze-dashboard-phase-1-design.md §5
```

Labels: `frontend`, `dashboard`, `parked`, `forward-compat`

Priority: Medium

- [ ] **Step 2: Note the ticket ID in the eventual PR description**

The PR description for this Phase 1 work must reference the parked ticket so the seam has a tracked owner.

- [ ] **Step 3: No commit** (Jira-only).

---

### Task 18: Open PR

**Files:** none — git/GitHub only

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/analyze-dashboard-phase-1
```

- [ ] **Step 2: Open PR via gh CLI**

```bash
gh pr create --title "feat(analyze): Phase 1 dashboard expansion (operator cut)" --body "$(cat <<'EOF'
## Summary

- Surfaces 4 new sections (Goods · Cost breakdown · Parties · Dates & terms) below the existing 3-card verdict bar on `AnalyzePage`
- Renders fields the backend already extracts; no new API surface
- Forward-compat seam: `viewMode='operator' | 'broker'` (broker branch throws, parked ticket KAN-XX tracks ownership)

Spec: `docs/superpowers/specs/2026-05-05-analyze-dashboard-phase-1-design.md`
Plan: `docs/superpowers/plans/2026-05-05-analyze-dashboard-phase-1.md`

## Acceptance criteria

(See spec §9 — copy from there into a checked list as items are verified.)

## Test plan

- [ ] `npm test` passes (12 new test files)
- [ ] `npx playwright test` passes (2 new e2e specs)
- [ ] Mobile viewport (375px) renders correctly — screenshot below
- [ ] EN ↔ ES translation toggle works for all 4 sections
- [ ] `npm run build` + grep confirms fixtures don't ship to prod

## Screenshots

[Attach 4 screenshots: rich/EN/desktop, rich/ES/desktop, rich/EN/mobile, sparse/EN/desktop]

## Follow-ups (non-blocking)

- Phase 2: extraction-quality summary, seller_country, BEC IBAN flag (gated on KAN-22 + extraction-upgrade ticket #56)
- Validate reconciliation threshold against ≥3 real invoices when KAN-22 lands
- KAN-XX (parked): implement viewMode='broker' branch
- KAN-46 backend dispatch (paused): brief updated by spec §11 to route remit_to_name + supplier_iban into field_mapping (not ignore-list)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 3: Verify CI green**

```bash
gh pr checks
```

Expected: all checks pass before requesting review.

---

## Self-Review

**Spec coverage:** Each spec section has a corresponding task:
- §1 Context — implicit, no work
- §2 Goals + non-goals — Tasks 5–13 cover goals; non-goals deliberately excluded
- §3 User goal & mental model — Task 13 wrapper composes in spec order
- §4 Layout — Task 14 wires into ResultsView
- §5 Architecture — Tasks 2 (helpers), 5–13 (components), with §5 type contract for FieldRow in Task 6 + viewMode throw in Task 13
- §6 Reconciliation pill — Task 7 with threshold constant + comment
- §7 Style fidelity — every component uses existing tokens; XSS discipline naturally satisfied (text-only `value` props, no `dangerouslySetInnerHTML`)
- §8 Test plan — Tasks 5–13 unit tests; Task 15 Playwright; Tasks 2–3 fixtures
- §9 Acceptance criteria — Task 16 manual verification covers screenshots / mobile / bundle / PII grep; Task 17 covers parked-ticket criterion; Task 18 covers PR description criteria
- §10 Follow-ups — Task 17 files the parked ticket
- §11 KAN-46 dependency — surfaced in Task 18 PR description; backend dispatch resumes after this PR
- §12 Open questions — icon choice resolved (Package/Receipt/Building2/Calendar in Tasks 9–12); PartyCard returns null when name missing (Task 8)

**Placeholder scan:** No "TBD"/"TODO"/"implement later" present. All test code complete; all implementation code complete.

**Type consistency:** `Party` type exported from `extraction-helpers.ts` (Task 2) is consumed by `PartyCard` (Task 8) and produced by `PartiesSection` (Task 11). `LineItem` shape used by `LineItemsTable` (Task 7) is satisfied by the rich fixture (Task 3). `ViewMode` type exported from `InvoiceDetailSections` (Task 13) — no other consumers in Phase 1.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-05-analyze-dashboard-phase-1.md`. Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh `frontend-engineer` subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints for review.

**Which approach?**
