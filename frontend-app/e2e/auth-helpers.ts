/**
 * Playwright auth bypass helpers for Puente AI e2e specs.
 *
 * Firebase Auth uses IndexedDB (db: "firebaseLocalStorageDb", store:
 * "firebaseLocalStorage", keyPath: "fbase_key") to persist the signed-in
 * user across page loads.  The auth key format is:
 *   firebase:authUser:{apiKey}:[DEFAULT]
 *
 * Strategy:
 * 1. page.addInitScript injects a script that opens / creates the
 *    IndexedDB before the Vite bundle runs and inserts a synthetic user
 *    record.  Because addInitScript fires before any page JS, the Firebase
 *    SDK reads the pre-seeded user on init and calls onAuthStateChanged
 *    with it — no real Firebase network call needed.
 * 2. page.route intercepts the Firebase token-refresh request so
 *    user.getIdToken() resolves instantly with a fake token string.
 * 3. page.route intercepts the onboarding endpoint so isOnboarded()
 *    returns a completed profile — satisfying RequireOnboarded.
 * 4. Callers add their own page.route mocks for /upload, /analyze,
 *    /routing after calling setupAuthBypass.
 */

import { Page } from "@playwright/test";

// Public Firebase config values (not secrets — these are embedded in the
// production frontend bundle and safe to reference in tests).
const FIREBASE_API_KEY = "AIzaSyDz4rbfSyDsrPxR4ySD3-KXxAKl-2rCGlo";
const FAKE_UID = "pw-test-user-0001";
const FAKE_EMAIL = "pwtest@example.com";
const FAKE_TOKEN = "fake-id-token-for-playwright";

// Firebase IndexedDB persistence constants (from @firebase/auth source).
const DB_NAME = "firebaseLocalStorageDb";
const DB_VERSION = 1;
const DB_STORE = "firebaseLocalStorage";
const DB_KEYPATH = "fbase_key";

// The auth user key Firebase looks up during init.
const AUTH_KEY = `firebase:authUser:${FIREBASE_API_KEY}:[DEFAULT]`;

// Onboarding localStorage keys (must match src/lib/onboarding.ts).
const ONBOARDING_STORAGE_KEY = `puente.onboarding.${FAKE_UID}`;
const ONBOARDING_SYNC_KEY = `puente.onboarding.lastSyncAt.${FAKE_UID}`;

/**
 * Synthetic Firebase user object shape that the SDK deserialises from
 * IndexedDB.  Fields mirror what @firebase/auth UserImpl.toJSON() writes.
 * The accessToken value is arbitrary — authedFetch never sends it to a real
 * backend in these tests (all API routes are mocked via page.route).
 */
function fakeFbUser() {
  const now = Date.now();
  const expirationTime = now + 3_600_000; // 1 h from now
  return {
    uid: FAKE_UID,
    email: FAKE_EMAIL,
    emailVerified: true,
    isAnonymous: false,
    displayName: "PW Test User",
    photoURL: null,
    phoneNumber: null,
    tenantId: null,
    providerData: [
      {
        providerId: "password",
        uid: FAKE_EMAIL,
        displayName: "PW Test User",
        email: FAKE_EMAIL,
        phoneNumber: null,
        photoURL: null,
      },
    ],
    stsTokenManager: {
      refreshToken: "fake-refresh-token",
      accessToken: FAKE_TOKEN,
      expirationTime,
    },
    createdAt: String(now - 86_400_000),
    lastLoginAt: String(now),
    apiKey: FIREBASE_API_KEY,
    appName: "[DEFAULT]",
  };
}

/**
 * Inject the Firebase auth bypass + onboarding cache into the page.
 * Must be called BEFORE page.goto().
 */
export async function setupAuthBypass(page: Page): Promise<void> {
  const user = fakeFbUser();
  const onboardingProfile = {
    displayName: "PW Test User",
    company: "Test Corp",
    corridors: ["mia-bog"],
    completedAt: new Date(Date.now() - 86_400_000).toISOString(),
  };

  // --- 1. Pre-seed Firebase IndexedDB ---
  await page.addInitScript(
    ({ dbName, dbVersion, dbStore, dbKeypath, authKey, userData }) => {
      // Open (or create) the Firebase auth IndexedDB and insert the fake user
      // record BEFORE the app bundle initialises.
      const req = indexedDB.open(dbName, dbVersion);
      req.onupgradeneeded = (ev) => {
        const db = (ev.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(dbStore)) {
          db.createObjectStore(dbStore, { keyPath: dbKeypath });
        }
      };
      req.onsuccess = (ev) => {
        const db = (ev.target as IDBOpenDBRequest).result;
        const tx = db.transaction(dbStore, "readwrite");
        const store = tx.objectStore(dbStore);
        store.put({ [dbKeypath]: authKey, value: userData });
      };
    },
    {
      dbName: DB_NAME,
      dbVersion: DB_VERSION,
      dbStore: DB_STORE,
      dbKeypath: DB_KEYPATH,
      authKey: AUTH_KEY,
      userData: user,
    }
  );

  // --- 2. Pre-seed onboarding localStorage (sets cache + fresh sync ts) ---
  await page.addInitScript(
    ({ storageKey, syncKey, profile }) => {
      // localStorage is available in initScript context.
      localStorage.setItem(storageKey, JSON.stringify(profile));
      localStorage.setItem(syncKey, String(Date.now()));
    },
    {
      storageKey: ONBOARDING_STORAGE_KEY,
      syncKey: ONBOARDING_SYNC_KEY,
      profile: onboardingProfile,
    }
  );

  // --- 3. Mock Firebase token-refresh so getIdToken() resolves immediately ---
  // Firebase calls https://securetoken.googleapis.com/v1/token?key=... when
  // the cached token is expired or not present. Intercept + return a minimal
  // valid response so authedFetch can get a token without a real network call.
  await page.route(
    "**/securetoken.googleapis.com/v1/token**",
    async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: FAKE_TOKEN,
          expires_in: "3600",
          token_type: "Bearer",
          refresh_token: "fake-refresh-token",
          id_token: FAKE_TOKEN,
        }),
      });
    }
  );

  // Also intercept identitytoolkit getAccountInfo (user validation on init)
  await page.route(
    "**/identitytoolkit.googleapis.com/**",
    async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          kind: "identitytoolkit#GetAccountInfoResponse",
          users: [
            {
              localId: FAKE_UID,
              email: FAKE_EMAIL,
              emailVerified: true,
              displayName: "PW Test User",
              providerUserInfo: [{ providerId: "password", email: FAKE_EMAIL }],
              validSince: "1000000",
              lastLoginAt: String(Date.now()),
              createdAt: String(Date.now() - 86_400_000),
            },
          ],
        }),
      });
    }
  );

  // --- 4. Mock the onboarding endpoint (backend call inside isOnboarded) ---
  await page.route("**/api/v1/onboarding**", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          displayName: "PW Test User",
          company: "Test Corp",
          corridors: ["mia-bog"],
          completedAt: new Date(Date.now() - 86_400_000).toISOString(),
          createdAt: new Date(Date.now() - 86_400_000).toISOString(),
          updatedAt: new Date(Date.now() - 86_400_000).toISOString(),
        }),
      });
    } else {
      // POST — return same shape
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          displayName: "PW Test User",
          company: "Test Corp",
          corridors: ["mia-bog"],
          completedAt: new Date(Date.now() - 86_400_000).toISOString(),
          createdAt: new Date(Date.now() - 86_400_000).toISOString(),
          updatedAt: new Date(Date.now() - 86_400_000).toISOString(),
        }),
      });
    }
  });
}
