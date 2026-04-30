

## Auth hardening + remove silent demo fallback

Wire authenticated requests to the Cloud Run backend, gate the app behind login, surface real API errors instead of silently swapping in demo data, add a working password-reset page, and document the env var.

### Files to modify

1. **`src/lib/puente-api.ts`** — env-driven base URL, new `authedFetch` helper, route all calls through it, add `complianceDocument`, delete `DEMO_ANALYSIS` / `DEMO_ROUTING`.
2. **`src/pages/AnalyzePage.tsx`** — replace silent demo fallback with explicit error UI (HTTP status + body) and a Retry button. Drop `isDemo` state and the demo badge. Remove `DEMO_ROUTING` reference (use `routing.routes ?? []`).
3. **`src/App.tsx`** — add `RequireAuth` (loader while `loading`, redirect to `/login` if no user) and wrap every `AppLayout` child route.
4. **`src/components/layout/TopBar.tsx`** — bind avatar label to `useAuth().user`; add a dropdown with **Sign out** that calls `logout()` then navigates to `/`.
5. **`src/pages/ResetPasswordPage.tsx`** (new) — reads `oobCode` from query string, single password input + confirm button calling `confirmPasswordReset(auth, oobCode, newPassword)`, success state with link back to `/login`. Public route.
6. **`src/App.tsx`** — register `/reset-password` as a public route (outside `RequireAuth`).
7. **`README.md`** — project description, local dev steps, document `VITE_API_URL`.

### Technical details

**`authedFetch` signature**

```ts
export async function authedFetch(path: string, init: RequestInit = {}) {
  const user = auth.currentUser;
  if (!user) throw new Error("Not authenticated");
  const token = await user.getIdToken();
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${body || res.statusText}`);
  }
  return res.json();
}
```

- `uploadDocument` → `authedFetch("/upload", { method: "POST", body: formData })`
- `analyzeDocument` / `routeDocument` / `complianceDocument` → JSON POST with `{ document_id }`.
- Imports `auth` from `@/lib/firebase`.

**`RequireAuth`** lives in `App.tsx`:

```tsx
function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen grid place-items-center"><Loader2 className="h-6 w-6 animate-spin" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
```

Wrap the `AppLayout` route element: `<Route element={<RequireAuth><AppLayout /></RequireAuth>}>`.

**AnalyzePage error state** — new `error: string | null` state. On catch: `setError(err.message)`, `setStep(1)` (or dedicated error view). Render an error card with the message and a "Retry" button that re-opens the file picker.

**TopBar dropdown** — uses existing `@/components/ui/dropdown-menu`, trigger is the avatar block, items: display name (label), separator, Sign out. Sign out: `await logout(); navigate("/")`.

**ResetPasswordPage** — uses `confirmPasswordReset` from `firebase/auth` with `auth` from `@/lib/firebase`. Reads `oobCode` from `useSearchParams`. Errors shown inline; success swaps to a "Password updated" panel with a button to `/login`.

### Out of scope (per instructions)

- No changes to mock data on `/explorer`, `/insights`, `/dashboard`, `/transactions`.
- No env file creation — only documenting `VITE_API_URL` in README and consuming it in `puente-api.ts`.

### Deliverable after implementation

A list of every modified file plus the final contents of `src/lib/puente-api.ts` and `src/App.tsx` pasted in the response.

