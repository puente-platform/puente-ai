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
