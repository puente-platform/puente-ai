// Lightweight onboarding state, stored locally per-user.
// No backend persistence — Lovable Cloud is not enabled for this flow.

const KEY_PREFIX = "puente.onboarding";

export interface OnboardingProfile {
  displayName?: string;
  company?: string;
  corridors?: string[]; // e.g. ["mia-bog", "mia-sdq"]
  completedAt?: string; // ISO timestamp
}

export const CORRIDOR_OPTIONS: { id: string; label: { en: string; es: string } }[] = [
  { id: "mia-bog", label: { en: "Miami ↔ Bogotá", es: "Miami ↔ Bogotá" } },
  { id: "mia-sdq", label: { en: "Miami ↔ Santo Domingo", es: "Miami ↔ Santo Domingo" } },
  { id: "mia-sao", label: { en: "Miami ↔ São Paulo", es: "Miami ↔ São Paulo" } },
  { id: "mia-mex", label: { en: "Miami ↔ Mexico City", es: "Miami ↔ Ciudad de México" } },
  { id: "mia-lim", label: { en: "Miami ↔ Lima", es: "Miami ↔ Lima" } },
  { id: "mia-scl", label: { en: "Miami ↔ Santiago", es: "Miami ↔ Santiago" } },
];

function storageKey(uid: string) {
  return `${KEY_PREFIX}.${uid}`;
}

export function getOnboarding(uid: string | null | undefined): OnboardingProfile | null {
  if (!uid || typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(storageKey(uid));
    return raw ? (JSON.parse(raw) as OnboardingProfile) : null;
  } catch {
    return null;
  }
}

export function saveOnboarding(uid: string, data: OnboardingProfile) {
  if (typeof window === "undefined") return;
  try {
    const existing = getOnboarding(uid) ?? {};
    window.localStorage.setItem(
      storageKey(uid),
      JSON.stringify({ ...existing, ...data }),
    );
  } catch {
    // Ignore — storage may be unavailable (private mode, quota)
  }
}

export function isOnboarded(uid: string | null | undefined): boolean {
  const data = getOnboarding(uid);
  return Boolean(data?.completedAt);
}

export function markOnboarded(uid: string) {
  saveOnboarding(uid, { completedAt: new Date().toISOString() });
}
