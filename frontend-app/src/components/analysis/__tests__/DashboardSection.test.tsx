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
