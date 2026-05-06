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

  it("renders a 'Not extracted' fallback — not an empty grid — when all parties are absent (I4 regression guard)", () => {
    // Sparse extraction with no party fields at all should show the fallback
    // line, not an empty grid of invisible PartyCard placeholders.
    const noParties = { fields: { total_amount: 100, currency: "USD" } };
    render(withI18n(<PartiesSection extraction={noParties} />));
    expect(screen.getByText(/not extracted/i)).toBeInTheDocument();
    // No party names should appear
    expect(screen.queryByText("Acme Test Exports SAS")).not.toBeInTheDocument();
  });
});
