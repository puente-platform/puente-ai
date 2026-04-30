import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearOnboardingCache,
  getOnboarding,
  getOnboardingFromLocalStorage,
  isOnboarded,
  markOnboarded,
  migrateLocalStorageToServer,
  saveOnboarding,
  validateCorridors,
} from "../onboarding";

vi.mock("../puente-api", () => ({
  getOnboarding: vi.fn(),
  saveOnboarding: vi.fn(),
}));

import {
  getOnboarding as apiGetOnboarding,
  saveOnboarding as apiSaveOnboarding,
} from "../puente-api";

const TEST_UID = "test-uid-001";
const KEY = `puente.onboarding.${TEST_UID}`;
const SYNC_KEY = `puente.onboarding.lastSyncAt.${TEST_UID}`;
const MIGRATED_KEY = `puente.onboarding.migrated.${TEST_UID}`;

beforeEach(() => {
  window.localStorage.clear();
  vi.clearAllMocks();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("validateCorridors", () => {
  it("accepts known corridor IDs", () => {
    expect(validateCorridors(["mia-bog", "mia-sdq"])).toEqual(["mia-bog", "mia-sdq"]);
  });

  it("rejects unknown corridor IDs", () => {
    expect(() => validateCorridors(["mia-bog", "atl-mia"])).toThrow(/atl-mia/);
  });
});

describe("getOnboarding cache behavior", () => {
  it("returns cached value when fresh (within 5 min)", async () => {
    window.localStorage.setItem(KEY, JSON.stringify({ displayName: "Cached" }));
    window.localStorage.setItem(SYNC_KEY, String(Date.now()));

    const result = await getOnboarding(TEST_UID);
    expect(result).toEqual({ displayName: "Cached" });
    expect(apiGetOnboarding).not.toHaveBeenCalled();
  });

  it("fetches from server when cache is stale", async () => {
    window.localStorage.setItem(KEY, JSON.stringify({ displayName: "Stale" }));
    window.localStorage.setItem(SYNC_KEY, String(Date.now() - 6 * 60 * 1000));

    vi.mocked(apiGetOnboarding).mockResolvedValueOnce({
      displayName: "Fresh",
      company: "Co",
      corridors: ["mia-bog"],
      completedAt: null,
      createdAt: "2026-04-30T00:00:00Z",
      updatedAt: "2026-04-30T00:00:00Z",
    });

    const result = await getOnboarding(TEST_UID);
    expect(apiGetOnboarding).toHaveBeenCalledOnce();
    expect(result?.displayName).toBe("Fresh");

    // Cache updated to fresh server response
    expect(getOnboardingFromLocalStorage(TEST_UID)?.displayName).toBe("Fresh");
  });

  it("falls back to stale cache when server fetch fails", async () => {
    window.localStorage.setItem(KEY, JSON.stringify({ displayName: "Stale" }));
    window.localStorage.setItem(SYNC_KEY, String(Date.now() - 10 * 60 * 1000));

    vi.mocked(apiGetOnboarding).mockRejectedValueOnce(new Error("network down"));

    const result = await getOnboarding(TEST_UID);
    expect(result?.displayName).toBe("Stale");
  });

  it("returns null when uid is missing", async () => {
    expect(await getOnboarding(null)).toBeNull();
    expect(await getOnboarding(undefined)).toBeNull();
  });
});

describe("saveOnboarding", () => {
  it("calls API and updates cache", async () => {
    vi.mocked(apiSaveOnboarding).mockResolvedValueOnce({
      displayName: "Maria",
      company: "LT Inc",
      corridors: ["mia-bog"],
      completedAt: null,
      createdAt: "2026-04-30T00:00:00Z",
      updatedAt: "2026-04-30T00:00:00Z",
    });

    await saveOnboarding(TEST_UID, {
      displayName: "Maria",
      company: "LT Inc",
      corridors: ["mia-bog"],
    });

    expect(apiSaveOnboarding).toHaveBeenCalledWith({
      displayName: "Maria",
      company: "LT Inc",
      corridors: ["mia-bog"],
    });

    const cached = getOnboardingFromLocalStorage(TEST_UID);
    expect(cached?.displayName).toBe("Maria");
  });

  it("rejects unknown corridor IDs without calling API", async () => {
    await expect(
      saveOnboarding(TEST_UID, { corridors: ["bogus-corridor"] }),
    ).rejects.toThrow(/bogus-corridor/);
    expect(apiSaveOnboarding).not.toHaveBeenCalled();
  });
});

describe("markOnboarded", () => {
  it("sends only markComplete:true — NEVER a client-supplied completedAt", async () => {
    vi.mocked(apiSaveOnboarding).mockResolvedValueOnce({
      displayName: null,
      company: null,
      corridors: null,
      completedAt: "2026-04-30T12:00:00Z",
      createdAt: "2026-04-30T11:00:00Z",
      updatedAt: "2026-04-30T12:00:00Z",
    });

    await markOnboarded(TEST_UID);

    expect(apiSaveOnboarding).toHaveBeenCalledWith({ markComplete: true });
    const payload = vi.mocked(apiSaveOnboarding).mock.calls[0][0] as Record<string, unknown>;
    expect(payload).not.toHaveProperty("completedAt");
  });
});

describe("isOnboarded", () => {
  it("returns true when completedAt is present in cached profile", async () => {
    window.localStorage.setItem(
      KEY,
      JSON.stringify({ completedAt: "2026-04-30T00:00:00Z" }),
    );
    window.localStorage.setItem(SYNC_KEY, String(Date.now()));

    expect(await isOnboarded(TEST_UID)).toBe(true);
  });

  it("returns false when completedAt is absent", async () => {
    window.localStorage.setItem(KEY, JSON.stringify({ displayName: "Maria" }));
    window.localStorage.setItem(SYNC_KEY, String(Date.now()));

    expect(await isOnboarded(TEST_UID)).toBe(false);
  });
});

describe("migrateLocalStorageToServer", () => {
  it("sets sentinel BEFORE network call (Security Constraint #7)", async () => {
    window.localStorage.setItem(KEY, JSON.stringify({ displayName: "Old" }));
    let sentinelAtCallTime: string | null = null;
    vi.mocked(apiGetOnboarding).mockImplementation(async () => {
      sentinelAtCallTime = window.localStorage.getItem(MIGRATED_KEY);
      return null;
    });
    vi.mocked(apiSaveOnboarding).mockResolvedValueOnce({
      displayName: "Old",
      company: null,
      corridors: null,
      completedAt: null,
      createdAt: "2026-04-30T00:00:00Z",
      updatedAt: "2026-04-30T00:00:00Z",
    });

    await migrateLocalStorageToServer(TEST_UID);

    expect(sentinelAtCallTime).not.toBeNull();
  });

  it("is a no-op when sentinel is already set", async () => {
    window.localStorage.setItem(MIGRATED_KEY, new Date().toISOString());
    window.localStorage.setItem(KEY, JSON.stringify({ displayName: "Old" }));

    await migrateLocalStorageToServer(TEST_UID);

    expect(apiGetOnboarding).not.toHaveBeenCalled();
    expect(apiSaveOnboarding).not.toHaveBeenCalled();
  });

  it("skips when server already has completedAt", async () => {
    window.localStorage.setItem(KEY, JSON.stringify({ displayName: "Old" }));
    vi.mocked(apiGetOnboarding).mockResolvedValueOnce({
      displayName: "ServerVer",
      company: null,
      corridors: null,
      completedAt: "2026-04-29T00:00:00Z",
      createdAt: "2026-04-29T00:00:00Z",
      updatedAt: "2026-04-29T00:00:00Z",
    });

    await migrateLocalStorageToServer(TEST_UID);

    expect(apiSaveOnboarding).not.toHaveBeenCalled();
  });

  it("does NOT send client completedAt — sends markComplete instead", async () => {
    window.localStorage.setItem(
      KEY,
      JSON.stringify({
        displayName: "Old",
        company: "OldCo",
        corridors: ["mia-bog"],
        completedAt: "2025-01-01T00:00:00Z", // Forged / legacy timestamp
      }),
    );
    vi.mocked(apiGetOnboarding).mockResolvedValueOnce(null);
    vi.mocked(apiSaveOnboarding).mockResolvedValueOnce({
      displayName: "Old",
      company: "OldCo",
      corridors: ["mia-bog"],
      completedAt: "2026-04-30T00:00:00Z", // Server re-stamped
      createdAt: "2026-04-30T00:00:00Z",
      updatedAt: "2026-04-30T00:00:00Z",
    });

    await migrateLocalStorageToServer(TEST_UID);

    const payload = vi.mocked(apiSaveOnboarding).mock.calls[0][0] as Record<string, unknown>;
    expect(payload).not.toHaveProperty("completedAt");
    expect(payload.markComplete).toBe(true);
  });
});

describe("clearOnboardingCache", () => {
  it("removes all three localStorage keys for the uid", () => {
    window.localStorage.setItem(KEY, "x");
    window.localStorage.setItem(SYNC_KEY, "x");
    window.localStorage.setItem(MIGRATED_KEY, "x");

    clearOnboardingCache(TEST_UID);

    expect(window.localStorage.getItem(KEY)).toBeNull();
    expect(window.localStorage.getItem(SYNC_KEY)).toBeNull();
    expect(window.localStorage.getItem(MIGRATED_KEY)).toBeNull();
  });
});
