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
