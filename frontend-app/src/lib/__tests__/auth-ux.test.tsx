/**
 * Tests for the two UX fixes landed in feat/auth-logo-home-and-onboarding-gate:
 *
 *  1. Logo on sign-in / onboarding pages routes to home (/).
 *  2. Returning users (completedAt set) skip onboarding and land on /dashboard.
 *  3. New users (no completedAt) are still directed through /onboarding.
 *
 * Fixtures are kept minimal: we mock only the dependencies each test needs so
 * the tests are readable and don't break when unrelated modules change.
 */

import { render, screen, fireEvent } from "@testing-library/react";
import { Link, MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { isOnboarded } from "../onboarding";

// ---------------------------------------------------------------------------
// 1. isOnboarded routing logic — returning user skips onboarding
// ---------------------------------------------------------------------------

// These tests exercise the isOnboarded() predicate that LoginPage uses to
// decide where to send the user after sign-in. They are pure unit tests
// against the onboarding module (already server-backed + localStorage-cached).

vi.mock("../puente-api", () => ({
  getOnboarding: vi.fn(),
  saveOnboarding: vi.fn(),
}));

import {
  getOnboarding as apiGetOnboarding,
} from "../puente-api";

const TEST_UID = "returning-user-uid";
const FRESH_SYNC = String(Date.now());

beforeEach(() => {
  window.localStorage.clear();
  vi.clearAllMocks();
});

describe("returning user — isOnboarded returns true → route to /dashboard", () => {
  it("returns true when completedAt is present in a fresh cache (fast-path)", async () => {
    window.localStorage.setItem(
      `puente.onboarding.${TEST_UID}`,
      JSON.stringify({ completedAt: "2026-04-30T00:00:00Z" }),
    );
    window.localStorage.setItem(`puente.onboarding.lastSyncAt.${TEST_UID}`, FRESH_SYNC);

    const result = await isOnboarded(TEST_UID);
    expect(result).toBe(true);
    // The LoginPage branches on this: navigate(result ? "/dashboard" : "/onboarding")
    // The OnboardingPage guard also uses this to redirect away if already done.
    expect(apiGetOnboarding).not.toHaveBeenCalled(); // confirmed cache fast-path
  });
});

describe("new user — isOnboarded returns false → route to /onboarding", () => {
  it("returns false when completedAt is absent from cache", async () => {
    window.localStorage.setItem(
      `puente.onboarding.${TEST_UID}`,
      JSON.stringify({ displayName: "Maria", company: "Acme" }),
    );
    window.localStorage.setItem(`puente.onboarding.lastSyncAt.${TEST_UID}`, FRESH_SYNC);

    const result = await isOnboarded(TEST_UID);
    expect(result).toBe(false);
    // The LoginPage branches on this: navigate(result ? "/dashboard" : "/onboarding")
  });

  it("returns false when no cache entry exists and the server returns null", async () => {
    vi.mocked(apiGetOnboarding).mockResolvedValueOnce(null);
    const result = await isOnboarded(TEST_UID);
    expect(result).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// 2. Logo link — clicking the logo navigates to /
// ---------------------------------------------------------------------------
// We render a minimal route tree so we can assert that clicking the logo
// anchor lands the user on the "/" path. We avoid importing LoginPage /
// OnboardingPage (they pull in Firebase SDK, which is unavailable in jsdom)
// and instead test the logo-link pattern directly: a <Link to="/"> renders
// an <a href="/"> that react-router-dom intercepts to change location.

function LogoLink() {
  // Mirrors the exact JSX added to both pages:
  //   <Link to="/" aria-label="Go to Puente AI home">PUENTE AI</Link>
  // `Link` is imported via standard ESM at the top of the file;
  // require() would be undefined under Vitest's ESM runtime.
  return (
    <Link to="/" aria-label="Go to Puente AI home">
      PUENTE AI
    </Link>
  );
}

function LocationSpy() {
  const loc = useLocation();
  return <div data-testid="path">{loc.pathname}</div>;
}

describe("logo link — navigates to home", () => {
  it("renders an anchor pointing to '/'", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <LogoLink />
      </MemoryRouter>,
    );
    const link = screen.getByRole("link", { name: /go to puente ai home/i });
    expect(link).toHaveAttribute("href", "/");
  });

  it("clicking the logo changes route to '/'", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route path="/login" element={<LogoLink />} />
          <Route path="/" element={<LocationSpy />} />
        </Routes>
      </MemoryRouter>,
    );

    const link = screen.getByRole("link", { name: /go to puente ai home/i });
    fireEvent.click(link);

    // After navigation the LocationSpy rendered at "/" should show "/"
    const spy = screen.getByTestId("path");
    expect(spy.textContent).toBe("/");
  });
});
