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
