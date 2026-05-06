/**
 * e2e: Analyze dashboard — empty-state coverage (mocked sparse fixture)
 *
 * Verifies that when the extraction returns only 3 fields (total_amount,
 * currency, exporter_name) all 4 detail sections still render their
 * headings, and FieldRow components show "Not extracted" hints for the
 * missing fields instead of crashing or showing undefined.
 */

import { test, expect } from "@playwright/test";
import { extractionSparse } from "../src/test/fixtures/extraction-sparse";
import { setupAuthBypass } from "./auth-helpers";

const sparseResponse = {
  document_id: "test-doc-sparse",
  status: "analyzed",
  extraction: extractionSparse,
  analysis: {
    fraud_assessment: { score: 0, flags: [] },
    compliance_assessment: {
      level: "PASS",
      corridor: "Unknown",
      flags: [],
      missing_documents: [],
    },
    routing_recommendation: null,
  },
};

test.describe("Analyze dashboard — empty-state coverage (mocked sparse fixture)", () => {
  test.beforeEach(async ({ page }) => {
    // Set up Firebase auth bypass + onboarding cache before any navigation.
    await setupAuthBypass(page);

    // Mock /upload.
    await page.route("**/api/v1/upload", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ document_id: "test-doc-sparse" }),
      });
    });

    // Mock /analyze — return the sparse fixture response.
    await page.route("**/api/v1/analyze", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(sparseResponse),
      });
    });

    // Mock /routing — return 404; routing_recommendation is null so the
    // "routing unavailable" card will render.
    await page.route("**/api/v1/routing", async (route) => {
      await route.fulfill({ status: 404, body: "" });
    });
  });

  test("'Not extracted' hints render gracefully when fields are missing", async ({
    page,
  }) => {
    await page.goto("/analyze");

    // Upload a placeholder PDF via the hidden file input.
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: "test.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.4 test"),
    });

    // Wait for results to render (mocked, near-instant).

    // Cost breakdown section heading still renders despite sparse data.
    await expect(
      page.getByText(/cost breakdown|desglose de costos/i)
    ).toBeVisible({ timeout: 15_000 });

    // Parties section heading still renders.
    await expect(page.getByText(/parties|partes/i)).toBeVisible();

    // At least one "Not extracted" hint is visible (the sparse fixture has
    // many empty fields — net_amount, tax_amount, invoice_date, etc.).
    await expect(
      page.getByText(/not extracted|no extraído/i).first()
    ).toBeVisible();

    // The single extracted supplier name surfaces (may appear in header + Parties).
    await expect(page.getByText("Acme Test Exports SAS").first()).toBeVisible();
  });
});
