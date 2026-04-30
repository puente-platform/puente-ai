// Onboarding profile state, server-backed (Firestore via FastAPI) with a
// localStorage cache for fast route guards. The server is the source of
// truth — see backend/app/routes/onboarding.py.

import {
  getOnboarding as apiGetOnboarding,
  saveOnboarding as apiSaveOnboarding,
  type OnboardingProfileIn,
  type OnboardingProfileOut,
} from "./puente-api";

const KEY_PREFIX = "puente.onboarding";
const SYNC_KEY_PREFIX = "puente.onboarding.lastSyncAt";
const MIGRATED_KEY_PREFIX = "puente.onboarding.migrated";
const CACHE_TTL_MS = 5 * 60 * 1000;

export interface OnboardingProfile {
  displayName?: string;
  company?: string;
  corridors?: string[];
  completedAt?: string;
}

export const CORRIDOR_OPTIONS: { id: string; label: { en: string; es: string } }[] = [
  { id: "mia-bog", label: { en: "Miami ↔ Bogotá", es: "Miami ↔ Bogotá" } },
  { id: "mia-sdq", label: { en: "Miami ↔ Santo Domingo", es: "Miami ↔ Santo Domingo" } },
  { id: "mia-sao", label: { en: "Miami ↔ São Paulo", es: "Miami ↔ São Paulo" } },
  { id: "mia-mex", label: { en: "Miami ↔ Mexico City", es: "Miami ↔ Ciudad de México" } },
  { id: "mia-lim", label: { en: "Miami ↔ Lima", es: "Miami ↔ Lima" } },
  { id: "mia-scl", label: { en: "Miami ↔ Santiago", es: "Miami ↔ Santiago" } },
];

const VALID_CORRIDOR_IDS = new Set(CORRIDOR_OPTIONS.map((c) => c.id));

function storageKey(uid: string) { return `${KEY_PREFIX}.${uid}`; }
function syncKey(uid: string) { return `${SYNC_KEY_PREFIX}.${uid}`; }
function migratedKey(uid: string) { return `${MIGRATED_KEY_PREFIX}.${uid}`; }

function profileFromOut(out: OnboardingProfileOut): OnboardingProfile {
  return {
    displayName: out.displayName ?? undefined,
    company: out.company ?? undefined,
    corridors: out.corridors ?? undefined,
    completedAt: out.completedAt ?? undefined,
  };
}

export function getOnboardingFromLocalStorage(
  uid: string | null | undefined,
): OnboardingProfile | null {
  if (!uid || typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(storageKey(uid));
    return raw ? (JSON.parse(raw) as OnboardingProfile) : null;
  } catch {
    return null;
  }
}

function cacheOnboarding(uid: string, data: OnboardingProfile) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(storageKey(uid), JSON.stringify(data));
    window.localStorage.setItem(syncKey(uid), String(Date.now()));
  } catch {
    // localStorage may be unavailable (private mode, quota) — non-fatal
  }
}

function isCacheFresh(uid: string): boolean {
  if (typeof window === "undefined") return false;
  try {
    const ts = window.localStorage.getItem(syncKey(uid));
    if (!ts) return false;
    return Date.now() - Number(ts) < CACHE_TTL_MS;
  } catch {
    return false;
  }
}

export function validateCorridors(ids: readonly string[]): string[] {
  const filtered = ids.filter((id) => VALID_CORRIDOR_IDS.has(id));
  if (filtered.length !== ids.length) {
    const bad = ids.filter((id) => !VALID_CORRIDOR_IDS.has(id));
    throw new Error(`Invalid corridor id(s): ${bad.join(", ")}`);
  }
  return filtered;
}

export async function getOnboarding(
  uid: string | null | undefined,
): Promise<OnboardingProfile | null> {
  if (!uid) return null;

  if (isCacheFresh(uid)) {
    const cached = getOnboardingFromLocalStorage(uid);
    if (cached) return cached;
  }

  try {
    const out = await apiGetOnboarding();
    if (!out) return null;
    const profile = profileFromOut(out);
    cacheOnboarding(uid, profile);
    return profile;
  } catch {
    // Network failure — fall back to stale cache if any
    return getOnboardingFromLocalStorage(uid);
  }
}

export async function saveOnboarding(
  uid: string,
  data: OnboardingProfile,
): Promise<OnboardingProfile> {
  if (data.corridors) validateCorridors(data.corridors);

  const payload: OnboardingProfileIn = {
    displayName: data.displayName ?? undefined,
    company: data.company ?? undefined,
    corridors: data.corridors ?? undefined,
  };

  // Optimistic local write (merged with existing) so a refresh mid-flow
  // doesn't lose user input on a transient network failure. Will be
  // overwritten with the canonical server response on API success.
  // Copilot flagged the original "localStorage only after API success" path
  // as a UX risk — typed values vanish on a failed save with no recovery.
  const existing = getOnboardingFromLocalStorage(uid) ?? {};
  cacheOnboarding(uid, { ...existing, ...data });

  const out = await apiSaveOnboarding(payload);
  const profile = profileFromOut(out);
  cacheOnboarding(uid, profile);
  return profile;
}

// markOnboarded sets completedAt server-side via markComplete:true.
// The server stamps the timestamp; we never send it from the client.
export async function markOnboarded(uid: string): Promise<OnboardingProfile> {
  const out = await apiSaveOnboarding({ markComplete: true });
  const profile = profileFromOut(out);
  cacheOnboarding(uid, profile);
  return profile;
}

export async function isOnboarded(
  uid: string | null | undefined,
): Promise<boolean> {
  const profile = await getOnboarding(uid);
  return Boolean(profile?.completedAt);
}

// One-shot migration of pre-existing localStorage entries to Firestore.
// The sentinel is set BEFORE the network call so that a network failure
// does not cause unbounded retries on every page load (Security Constraint #7).
// completedAt is intentionally NOT sent — the server re-stamps via markComplete
// (Security Constraint #8 / Option A).
export async function migrateLocalStorageToServer(uid: string): Promise<void> {
  if (typeof window === "undefined") return;

  if (window.localStorage.getItem(migratedKey(uid))) return;
  window.localStorage.setItem(migratedKey(uid), new Date().toISOString());

  const old = getOnboardingFromLocalStorage(uid);
  if (!old) return;

  // Warm the cache from the legacy entry BEFORE any network call. Without
  // this, a concurrent `await isOnboarded(uid)` on the same signin would see
  // an unset `lastSyncAt` (new key in this PR) → fall through to the API →
  // get 404 (server doc not yet created) → return null → route the user to
  // /onboarding even though they completed it pre-deploy. cacheOnboarding
  // writes both storageKey and syncKey, so isCacheFresh returns true on the
  // next read in this session and the existing `getOnboarding` cache fast-
  // path returns the legacy profile. The migration POST below then runs
  // async to canonicalize the server record. (bug_009 from ultrareview)
  cacheOnboarding(uid, old);

  try {
    const server = await apiGetOnboarding();
    if (server?.completedAt) return;
  } catch {
    // 404 expected when no server record exists yet; other errors fall through
  }

  try {
    await apiSaveOnboarding({
      displayName: old.displayName,
      company: old.company,
      corridors: old.corridors,
      markComplete: Boolean(old.completedAt),
    });
  } catch {
    // Sentinel stays set — retrying every page load is the bigger risk.
    // Users can always re-enter onboarding via /onboarding if needed.
  }
}

// Clear all onboarding-related localStorage keys for a uid.
// Called from auth.tsx logout() to prevent PII residue on shared devices
// (Security Constraint #9).
export function clearOnboardingCache(uid: string): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(storageKey(uid));
    window.localStorage.removeItem(syncKey(uid));
    window.localStorage.removeItem(migratedKey(uid));
  } catch {
    // Non-fatal
  }
}
