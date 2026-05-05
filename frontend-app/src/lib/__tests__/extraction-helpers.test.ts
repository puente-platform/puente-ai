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
