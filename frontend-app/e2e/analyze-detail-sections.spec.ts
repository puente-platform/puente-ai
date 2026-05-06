/**
 * e2e: Analyze dashboard — Phase 1 detail sections (mocked rich fixture)
 *
 * Verifies that all 4 new InvoiceDetailSections (Goods, Cost breakdown,
 * Parties, Dates & terms) render after a successful analyze pipeline,
 * using a fully-mocked backend so the test is self-contained and CI-safe.
 */

import { test, expect } from "@playwright/test";
import { extractionRich } from "../src/test/fixtures/extraction-rich";
import { setupAuthBypass } from "./auth-helpers";

const richResponse = {
  document_id: "test-doc-rich",
  status: "analyzed",
  extraction: extractionRich,
  analysis: {
    fraud_assessment: { score: 12, flags: [] },
    compliance_assessment: {
      level: "PASS",
      corridor: "CO -> US",
      flags: [],
      missing_documents: [],
    },
    routing_recommendation: {
      recommended_method: "USDC",
      traditional_cost_usd: 487,
      puente_cost_usd: 0,
      savings_usd: 487,
      traditional_days: 3,
      puente_days: 1,
    },
  },
};

test.describe("Analyze dashboard — Phase 1 detail sections (mocked rich fixture)", () => {
  test.beforeEach(async ({ page }) => {
    // Set up Firebase auth bypass + onboarding cache before any navigation.
    await setupAuthBypass(page);

    // Mock /upload — return a document_id immediately.
    await page.route("**/api/v1/upload", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ document_id: "test-doc-rich" }),
      });
    });

    // Mock /analyze — return the rich fixture response.
    await page.route("**/api/v1/analyze", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(richResponse),
      });
    });

    // Mock /routing — return 404 so the frontend falls back to the
    // routing_recommendation embedded in the analyze response.
    await page.route("**/api/v1/routing", async (route) => {
      await route.fulfill({ status: 404, body: "" });
    });
  });

  test("renders all 4 new sections after analyzing", async ({ page }) => {
    await page.goto("/analyze");

    // Upload a placeholder PDF via the hidden file input.
    // The server is fully mocked, so file content does not matter.
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: "test.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.4 test"),
    });

    // --- Results must render within 15 s (mocked pipeline is near-instant) ---

    // Goods section heading is visible.
    await expect(page.getByText(/goods/i)).toBeVisible({ timeout: 15_000 });

    // Cost breakdown section heading.
    await expect(
      page.getByText(/cost breakdown|desglose de costos/i)
    ).toBeVisible();

    // Parties section heading.
    await expect(page.getByText(/parties|partes/i)).toBeVisible();

    // Dates & terms section heading.
    await expect(page.getByText(/dates|fechas/i)).toBeVisible();

    // Reconciliation pill: rich fixture line-item amounts sum to 60,462
    // which equals total_amount — should show "Matched".
    await expect(page.getByText(/matched|coincide/i)).toBeVisible();

    // Exporter name from rich fixture is surfaced (may appear in header + Parties).
    await expect(page.getByText("Acme Test Exports SAS").first()).toBeVisible();

    // Invoice total from rich fixture is shown in Cost breakdown.
    await expect(page.getByText(/\$60,462/).first()).toBeVisible();
  });
});
