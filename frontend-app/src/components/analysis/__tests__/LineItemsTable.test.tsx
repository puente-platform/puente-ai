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
