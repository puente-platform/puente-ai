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
