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
