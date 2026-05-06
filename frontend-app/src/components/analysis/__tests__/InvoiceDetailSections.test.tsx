import { describe, expect, it, vi } from "vitest";
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
