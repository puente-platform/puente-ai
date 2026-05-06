import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config — direct @playwright/test config replacing the missing
 * `lovable-agent-playwright-config` package (stub package never published
 * to npm; using inline config instead).
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: "http://localhost:8080",
    trace: "on-first-retry",
    // Headed mode off by default; set PWDEBUG=1 or --headed to see the browser.
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // Start the Vite dev server before running tests.
  webServer: {
    command: "npm run dev",
    url: "http://localhost:8080",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
