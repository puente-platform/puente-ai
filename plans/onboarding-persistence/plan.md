# Plan — Firestore-backed onboarding persistence

## Context

- **Bug report**: 2026-04-30 production
  - Existing clients see onboarding flow on new devices (should skip)
  - New clients' onboarding data lost across devices/browsers
- **Root cause**: `frontend-app/src/lib/onboarding.ts` is localStorage-only; no server source-of-truth
- **Owner**: Jay Alexander (primary agent, frontend-only because `frontend-engineer` is scoped to Phase 3 Next.js portal; backend changes use `backend-builder`)
- **Depends on**: None (onboarding feature is self-contained)
- **Jira reference**: Not yet filed; this is a production bug raised by user report, not a KAN ticket

## Architecture Decision: Backend as Source of Truth

**Choice: (b) Server-side persistence via FastAPI endpoint with Firebase ID token validation**

**Rationale:**
- The rest of the app already routes through FastAPI (`authedFetch` in `puente-api.ts`)
- Single auth surface: Firebase ID token verification already live in `backend/app/services/auth.py`
- Security: Server validates the token before writing/reading; client-side Firestore rules would require additional OAuth setup
- Simplicity: OneOnboarding profile per user, no complex ACLs
- Consistency: Treats onboarding state like other app state (transaction records, compliance checks) — all server-backed

**Tradeoff:** +1 network round-trip on cold auth check, mitigated by localStorage cache (fast-path on route guard).

## Security Constraints (from fintech-security audit, 2026-04-30)

These are **required** invariants for every step below. Any code review that finds a violation is a blocker.

1. **uid from verified token only** — `uid = claims["uid"]` from `Depends(get_current_user)`. The handler MUST reject any request body that contains a field named `uid`, `userId`, or `sub` (return 400). Doc path is always `users/{claims['uid']}`. Threat: OWASP API1 (BOLA).
2. **All timestamps are server-set** — `OnboardingProfileIn` does NOT include `completedAt`, `createdAt`, or `updatedAt`. The client signals completion via an explicit `markComplete: bool = False` flag. Server sets:
   - `createdAt = SERVER_TIMESTAMP` only on first write (doc-doesn't-exist branch)
   - `updatedAt = SERVER_TIMESTAMP` on every write
   - `completedAt = SERVER_TIMESTAMP` only when `markComplete=True` AND existing doc has no `completedAt` (one-shot, immutable). Subsequent `markComplete=True` requests are no-ops on `completedAt`.
   Threat: STRIDE-Tampering, Repudiation.
3. **firestore.rules committed in this PR with emulator tests** — see new step 4. Repo currently has no `firestore.rules` file (confirmed). Block deploy if rules tests fail.
4. **Strict PII validation** — `displayName: constr(strip_whitespace=True, min_length=1, max_length=80)`, `company: constr(strip_whitespace=True, min_length=1, max_length=120)`, both NFKC-normalized, reject any character matching `[\x00-\x1f\x7f]` (control chars). `corridors: list[Literal[...]]` enumerated against the seven IDs in `frontend-app/src/lib/onboarding.ts:13-20`, max length 7. Reject (don't truncate). Validation errors echo field name only, never the offending value. Threat: OWASP API3, API8.
5. **Null-vs-missing merge semantics** — Missing key = no change to existing field. Explicit `null` (JSON `null`, Pydantic `None` distinguishable from unset via `model_fields_set`) = clear field via Firestore `DELETE_FIELD` sentinel. Tests: `test_post_omitted_field_preserves_existing` and `test_post_null_field_clears_existing`.
6. **PII-safe logging** — Route handler MUST NOT log request body. Allowed log fields per request: `uid`, HTTP status, latency_ms, `corridor_count`, `markComplete`. Exception messages must NOT include `displayName` or `company`. Add `# noqa: do-not-log-pii` marker comment in the handler. Threat: OWASP API9, GDPR.
7. **Migration circuit breaker** — `migrateLocalStorageToServer` fires at most once per browser session via a localStorage sentinel key (`puente.onboarding.migrated.{uid}`). Set the sentinel BEFORE the POST so a network failure doesn't cause unbounded retries on every page load. Per-uid server-side rate limit deferred to follow-up KAN ticket (no rate-limit middleware exists in the backend today).
8. **Migration trust boundary (Option A — chosen)** — The migration utility POSTs `{displayName, company, corridors, markComplete: true}` ONLY. It does NOT send any timestamp. The server re-stamps `completedAt = now()`. Original onboarding date is lost; this eliminates the timestamp-forgery surface entirely. Threat: STRIDE-Tampering.
9. **Logout invalidation** — `auth.tsx` `logout()` clears `puente.onboarding.{uid}`, `puente.onboarding.{uid}.lastSyncAt`, and `puente.onboarding.migrated.{uid}` from localStorage. Prevents PII residue on shared devices.

### Out-of-scope security items (file as separate KAN tickets)

- **OFAC screening on `company`** at onboarding write — async sanctions check, flag suspicious entries before payment-route initiation. Aligns with the "KYC at first transaction" design.
- **GDPR/CCPA right-to-delete runbook** — add `users/{uid}` (and any future `audit/{uid}/**` subcollections) to the account-deletion sweep. Document the collection as PII-bearing in `docs/CLAUDE.md` data-handling section.
- **Per-uid server-side rate limit** — onboarding writes capped at e.g. 10/min per uid via Firestore-backed token bucket. Currently mitigated client-side by the migration sentinel; server-side limit is defense-in-depth.
- **Audit subcollection** — `audit/{uid}/onboarding/{timestamp}` capturing `{action, ip, user_agent_hash}` for repudiation defense. Cheap insurance, aligns with future KYC posture.

## Firestore Data Model

**Collection:** `users` (top-level, new)  
**Document:** `{uid}` (Firebase UID)  
**Fields:**
```json
{
  "displayName": "Maria Garcia",
  "company": "Liquidation Traders Inc",
  "corridors": ["mia-bog", "mia-sdq"],
  "completedAt": "2026-04-30T14:23:45.123Z",
  "createdAt": "2026-04-30T14:20:12.456Z",
  "updatedAt": "2026-04-30T14:23:45.123Z"
}
```

**Security Rules** (to be added to `firestore.rules` or equivalent):
- `match /users/{uid}` — read/write only if `request.auth.uid == uid`
- Prevent cross-tenant access; return 403 on violation (or 404 if paranoid)

**Indexes:** None required (single-document lookup, no range queries)

## Backend Endpoint Contract

**Route:** `POST /api/v1/onboarding` (new)
**Auth:** Requires Firebase ID token in `Authorization: Bearer <token>` header (via `Depends(get_current_user)`). uid is derived ONLY from the verified token, never from the body. Handler rejects bodies containing `uid`, `userId`, or `sub` keys (400).

**Request (security-hardened — see Security Constraints above):**
```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, StringConstraints, model_validator

# Must match frontend CORRIDOR_OPTIONS in onboarding.ts
CorridorId = Literal["mia-bog", "mia-sdq", "mia-sao", "mia-mex", "mia-lim", "mia-scl"]

DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
Company     = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]

class OnboardingProfileIn(BaseModel):
    # All three fields are Optional — `None` (explicit null) clears the field;
    # missing key (use model_fields_set in handler) leaves existing value untouched.
    displayName: DisplayName | None = None
    company:     Company     | None = None
    corridors:   list[CorridorId] | None = Field(default=None, max_length=7)
    # Server sets completedAt = SERVER_TIMESTAMP only when this is True AND
    # the existing doc has no completedAt (one-shot, immutable thereafter).
    markComplete: bool = False

    @model_validator(mode="before")
    @classmethod
    def reject_uid_fields(cls, data):
        if isinstance(data, dict):
            for forbidden in ("uid", "userId", "sub"):
                if forbidden in data:
                    raise ValueError(f"Field '{forbidden}' is not allowed in request body")
        return data

    # NFKC normalize + reject control chars in displayName/company —
    # implementation detail in handler or a custom validator.
```

**Response (201 Created on first write, 200 OK on subsequent updates):**
```python
class OnboardingProfileOut(BaseModel):
    displayName: str | None = None
    company:     str | None = None
    corridors:   list[str] | None = None
    completedAt: str | None = None  # ISO 8601, server-set
    createdAt:   str                # ISO 8601, server-set
    updatedAt:   str                # ISO 8601, server-set
```

**Error responses:**
- `400 Bad Request` — invalid corridor ID, forbidden body field (uid/userId/sub), validation failure (length/charset). Error body echoes field name only, never the offending value.
- `401 Unauthorized` — missing/invalid/expired Firebase token
- `500 Internal Server Error` — Firestore write failure (no PII in error message)

**Additional route (helper):** `GET /api/v1/onboarding` (new)
- Fetch the user's onboarding profile from Firestore (for cold-load after browser cache clear)
- Same auth as POST; uid from token claims only
- Response: `OnboardingProfileOut` or `404 Not Found` if never onboarded (own uid only — not an enumeration oracle)

## Frontend Changes

### 1. `frontend-app/src/lib/onboarding.ts` (refactored)

Transform from localStorage-only to **Firestore-backed with localStorage cache**:

- `getOnboarding(uid)` → tries cache first, then fetches from server (on cache miss or validation)
- `saveOnboarding(uid, data)` → writes to both localStorage AND server via `POST /api/v1/onboarding`
- `isOnboarded(uid)` → checks cache first; if missing/expired, fetches from server
- Add `validateCorridors()` to reject corridor IDs not in `CORRIDOR_OPTIONS`
- Cache-invalidation logic: TTL or explicit invalidation on logout

**Pseudo-code structure:**
```typescript
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 min; localStorage saves `lastSyncAt`

export async function getOnboarding(uid: string | null | undefined): Promise<OnboardingProfile | null> {
  if (!uid) return null;
  
  const cached = tryGetCachedOnboarding(uid);
  if (cached && !isCacheExpired(cached)) return cached;
  
  // Cache miss or expired — fetch from server
  try {
    const profile = await apiClient.getOnboarding(); // GET /api/v1/onboarding
    cacheOnboarding(uid, profile);
    return profile;
  } catch {
    // Fall back to stale cache if available, else null
    return cached?.data ?? null;
  }
}

export async function saveOnboarding(uid: string, data: OnboardingProfile) {
  // Validation
  validateCorridors(data.corridors);
  
  // Write to server (source of truth)
  const saved = await apiClient.saveOnboarding(data); // POST /api/v1/onboarding
  
  // Update local cache
  cacheOnboarding(uid, saved);
}

export async function markOnboarded(uid: string) {
  await saveOnboarding(uid, { completedAt: new Date().toISOString() });
}
```

### 2. `frontend-app/src/lib/puente-api.ts` (extended)

Add two new functions (parallel to existing `uploadDocument`, `analyzeDocument`, etc.):

```typescript
export async function getOnboarding(): Promise<OnboardingProfile> {
  return authedFetch("/onboarding", { method: "GET" });
}

export async function saveOnboarding(data: OnboardingProfile): Promise<OnboardingProfile> {
  return authedFetch("/onboarding", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
```

### 3. `frontend-app/src/pages/LoginPage.tsx` (updated routing logic)

Lines 40–42 and 60–61: Replace synchronous `isOnboarded(uid)` check with **async await + error boundary**:

```typescript
// OLD (lines 40–42):
// const uid = auth.currentUser?.uid;
// navigate(isOnboarded(uid) ? "/dashboard" : "/onboarding");

// NEW:
const uid = auth.currentUser?.uid;
if (!uid) { navigate("/"); return; }
try {
  const isComplete = await isOnboarded(uid); // Now async
  navigate(isComplete ? "/dashboard" : "/onboarding");
} catch {
  // On network error, fall back to pessimistic routing (show onboarding)
  // but let user skip if they know they've already done it
  navigate("/onboarding", { state: { retryMessage: "..." } });
}
```

*Note: This is a blocking change — `handleSubmit` and `handleSocial` must become async or wrap in `useEffect`.*

### 4. `frontend-app/src/pages/OnboardingPage.tsx` (no breaking changes)

Existing code already calls `saveOnboarding()` at line 44 and `markOnboarded()` at line 63. These will transparently start calling the server versions. No UI changes needed.

## Migration: Existing localStorage → Firestore (Option A — server re-stamps)

**Scenario:** Users who completed onboarding before this change have `puente.onboarding.{uid}` entries in localStorage with `completedAt` timestamps. **The original `completedAt` is intentionally discarded** to eliminate the timestamp-forgery surface (see Security Constraint #8). On migration the server re-stamps `completedAt = now()`. The migration population is small because the original bug is recent.

**Strategy:** Frontend utility on auth state change, with one-shot circuit breaker.

**New function in `frontend-app/src/lib/onboarding.ts`:**

```typescript
const MIGRATED_KEY_PREFIX = "puente.onboarding.migrated";
function migratedSentinelKey(uid: string) { return `${MIGRATED_KEY_PREFIX}.${uid}`; }

export async function migrateLocalStorageToServer(uid: string): Promise<void> {
  if (typeof window === "undefined") return;

  // Circuit breaker: only run once per browser per uid, EVER.
  // Set sentinel BEFORE the network call — if it fails we don't retry on every page load.
  if (window.localStorage.getItem(migratedSentinelKey(uid))) return;
  window.localStorage.setItem(migratedSentinelKey(uid), new Date().toISOString());

  const old = getOnboardingFromLocalStorage(uid); // direct read, no cache
  if (!old) return;

  // Server is source of truth — if it already has a record, do nothing.
  try {
    const server = await apiClient.getOnboarding();
    if (server?.completedAt) return;
  } catch {
    // 404 is expected (no server record yet); other errors silently fall through
  }

  // Push the old data up — completedAt is NOT sent; server re-stamps via markComplete:true.
  try {
    await apiClient.saveOnboarding({
      displayName: old.displayName,
      company: old.company,
      corridors: old.corridors,
      markComplete: Boolean(old.completedAt), // preserve "is onboarded" bit, drop the timestamp
    });
  } catch (err) {
    console.warn("Onboarding migration failed; user can re-enter via /onboarding");
    // Sentinel stays set — retrying on every page load is the bigger risk.
  }
}
```

Call from `AuthProvider` `useEffect` after user becomes authenticated:
```typescript
useEffect(() => {
  if (user?.uid) {
    migrateLocalStorageToServer(user.uid).catch(() => {});
  }
}, [user?.uid]);
```

**Logout invalidation** (`auth.tsx` `logout()`):
```typescript
const logout = async () => {
  const uid = auth.currentUser?.uid;
  if (uid) {
    window.localStorage.removeItem(`puente.onboarding.${uid}`);
    window.localStorage.removeItem(`puente.onboarding.${uid}.lastSyncAt`);
    window.localStorage.removeItem(migratedSentinelKey(uid));
  }
  await signOut(auth);
};
```

## Test Plan

### Backend Tests (pytest, `backend/tests/test_onboarding.py`)

- ✓ `test_post_onboarding_creates_record` — POST with valid data → 201, Firestore write
- ✓ `test_post_onboarding_idempotent` — POST same data twice → second overwrites, no error
- ✓ `test_post_onboarding_invalid_corridor` — POST with unknown corridor → 400
- ✓ `test_get_onboarding_returns_record` — GET returns what was POSTed
- ✓ `test_get_onboarding_404_when_empty` — GET before any POST → 404
- ✓ `test_onboarding_cross_tenant` — User A cannot read/write User B's onboarding → 403/404
- ✓ `test_post_onboarding_missing_auth` — POST without Bearer token → 401
- ✓ `test_post_onboarding_partial_update` — POST `{ displayName: "..." }` merges with existing (does not clear corridors)
- ✓ `test_post_onboarding_sets_completedAt` — POST with `completedAt` persists timestamp unchanged

**Fixtures:**
- Mock Firestore client (use existing `test_firestore.py` patterns)
- Sample user UID: `test-uid-001`
- Sample corridors: `["mia-bog", "mia-sdq"]`

### Frontend Tests (vitest, `frontend-app/src/lib/__tests__/onboarding.test.ts`)

- ✓ `test_getOnboarding_returns_cached_if_fresh` — Hit cache if <5min old
- ✓ `test_getOnboarding_fetches_from_server_if_expired` — Stale cache → call API
- ✓ `test_saveOnboarding_calls_api_and_caches` — POST succeeds, localStorage + memory cache updated
- ✓ `test_validateCorridors_rejects_unknown` — Invalid corridor throws error
- ✓ `test_isOnboarded_checks_completedAt` — True if `completedAt` present, false otherwise
- ✓ `test_markOnboarded_sets_timestamp` — Calls saveOnboarding with ISO date
- ✓ `test_migrateLocalStorageToServer_skips_if_server_has_data` — Don't overwrite
- ✓ `test_migrateLocalStorageToServer_pushes_old_data_up` — Writes old entry to server

**E2E (Playwright, `frontend-app/e2e/onboarding.spec.ts`)**
- ✓ New user signs up → sees onboarding flow
- ✓ User completes onboarding → data persists in Firestore
- ✓ User logs out, clears browser cache, logs back in → skips onboarding flow, lands on dashboard
- ✓ Migration: user had old localStorage entry → on next signin, data synced to server

## The Maria Test

**Scenario:** Maria signs up for Puente AI on her desktop, completes onboarding (enters name "Maria Garcia", company "LT Inc", selects corridors), and clicks Finish.

**Before this change:**
- Data stored only in `localStorage` under `puente.onboarding.{uid}`
- 3 days later, Maria opens Puente on her iPhone (new browser, no shared cache)
- Onboarding screen reappears → she is confused and annoyed → abandoned session

**After this change:**
- Desktop onboarding writes to Firestore (server) + localStorage (fast-path cache)
- iPhone signin: LoginPage calls async `isOnboarded()` → queries Firestore → returns true → skips to dashboard
- Maria sees her data already there, continues working
- **Result:** Maria's workflow is seamless across devices. Her onboarding is remembered forever.

## Clarifications Resolved (2026-04-30, user sign-off)

- ✅ **Firestore security rules**: deployed in this PR with emulator tests (security audit elevated this from "documented" to "tested"). See new step 4.
- ✅ **Cache TTL**: 5 minutes, plus invalidation on logout (Security Constraint #9).
- ✅ **Partial updates**: missing key = no change; explicit `null` = clear field (Security Constraint #5).
- ✅ **Jira ticket**: file as new KAN-XX for tracking.
- ✅ **Migration timestamp policy**: Option A — server re-stamps `completedAt = now()`, original timestamp discarded (Security Constraint #8).

## Definition of Done

- [ ] Backend: `OnboardingProfileIn` rejects body fields `uid`/`userId`/`sub`, enforces NFKC + length + charset, no client-supplied timestamps
- [ ] Backend: `POST /api/v1/onboarding` endpoint created, tests passing (10+ tests including null-vs-missing semantics)
- [ ] Backend: `GET /api/v1/onboarding` endpoint created, tests passing
- [ ] Backend: `firestore.rules` committed with `match /users/{uid}` rule + `@firebase/rules-unit-testing` emulator tests (self-read OK, cross-tenant denied, unauthenticated denied)
- [ ] Backend: Route handler does not log request body; PII never appears in exception messages
- [ ] Frontend: `onboarding.ts` refactored to cache + async server fetches, migration uses one-shot localStorage sentinel
- [ ] Frontend: `puente-api.ts` extended with `getOnboarding()` and `saveOnboarding()` functions
- [ ] Frontend: `LoginPage.tsx` updated to handle async `isOnboarded()` check post-signin
- [ ] Frontend: Migration utility added with circuit breaker (sentinel set BEFORE network call)
- [ ] Frontend: `auth.tsx` `logout()` clears all `puente.onboarding.*.{uid}` keys
- [ ] Frontend: `OnboardingPage.tsx` continues to work without changes (transparent to it)
- [ ] Tests: 10+ pytest tests, 3+ rules emulator tests, 8+ vitest tests, 4+ Playwright e2e tests
- [ ] Migration: Existing localStorage entries successfully synced on next signin; sentinel prevents retry storms
- [ ] Verification: Test user signs up → completes onboarding → logs out on Device A → logs in on Device B → onboarding skipped, data intact
- [ ] Verification: Cross-tenant Firestore access denied at the rules layer (emulator test passes)
- [ ] Documentation: `CLAUDE.md` updated with new `/api/v1/onboarding` endpoints, `users` collection (PII-bearing), and the four follow-up KAN tickets filed
- [ ] Commit messages follow Conventional Commits: `feat(onboarding): ...`, `test(onboarding): ...`, etc.

## Steps

1. [ ] **Backend: Pydantic models + database schema** — `feat(onboarding): Define OnboardingProfile data model + Firestore schema`
   - Create `backend/app/models/onboarding.py` with `OnboardingProfileIn` and `OnboardingProfileOut` exactly as specified in the "Backend Endpoint Contract" section above (NFKC, length limits, control-char rejection, `markComplete` flag, `model_validator` rejecting `uid`/`userId`/`sub`).
   - `CorridorId` literal must enumerate the seven IDs from `frontend-app/src/lib/onboarding.ts:13-20`.
   - Document Firestore path `users/{uid}` and field names in code comments.
   - Owner: backend-builder
   - Parallel-safe: yes
   - Depends on: none

2. [ ] **Backend: POST /api/v1/onboarding endpoint** — `feat(onboarding): Implement POST /api/v1/onboarding with Firestore write`
   - New route file `backend/app/routes/onboarding.py`.
   - Handler: extract `uid` from `Depends(get_current_user)` claims ONLY. Read existing doc to determine first-write vs update.
   - Firestore write: explicit field map, NOT `dict(model)` (avoids accidentally writing `markComplete` to the doc). Use `model_fields_set` to distinguish missing keys (no change) from explicit `null` (write `firestore.DELETE_FIELD` sentinel).
   - Server-set timestamps: `createdAt = SERVER_TIMESTAMP` only when doc-doesn't-exist; `updatedAt = SERVER_TIMESTAMP` always; `completedAt = SERVER_TIMESTAMP` only when `markComplete=True` AND existing doc has no `completedAt` (one-shot, immutable).
   - Status: 201 on first write (doc didn't exist), 200 on update.
   - Logging: per Security Constraint #6 — never log the request body. Allowed log fields: `uid`, status, latency_ms, `corridor_count`, `markComplete`. Add `# noqa: do-not-log-pii` comment marker.
   - Error handling: 400 on validation/forbidden-uid-field, 401 on auth fail, 500 on Firestore error (no PII in error body).
   - Register router in `backend/app/main.py`.
   - Owner: backend-builder
   - Parallel-safe: yes
   - Depends on: step 1

3. [ ] **Backend: GET /api/v1/onboarding endpoint** — `feat(onboarding): Implement GET /api/v1/onboarding with Firestore read`
   - Same route file, new handler. uid from token claims only.
   - Fetch `users/{uid}`, return 200 + `OnboardingProfileOut` or 404 if not found.
   - Owner: backend-builder
   - Parallel-safe: yes
   - Depends on: step 1

4. [ ] **Backend: firestore.rules + emulator tests** — `feat(onboarding): Add Firestore security rules for users collection`
   - Create `firestore.rules` at repo root (file does not exist today; only `firestore.indexes.json` is checked in).
   - Rule: `match /users/{uid} { allow read, write: if request.auth != null && request.auth.uid == uid; }`. Default-deny everything else.
   - Wire `firebase.json` so `firebase deploy --only firestore:rules` picks it up; document the deploy command in the route module's docstring.
   - Add `@firebase/rules-unit-testing` dev-dep + tests in `backend/tests/test_firestore_rules.py` (or a new `firebase-emulator/` directory if pytest can't run JS rules tests — backend-builder picks the layout).
   - Three required tests: (a) authenticated user reads/writes own `users/{uid}` ✓, (b) authenticated user A reading/writing `users/{uid_B}` is denied, (c) unauthenticated request is denied.
   - CI must run the emulator tests and block merge on failure.
   - Owner: backend-builder
   - Parallel-safe: yes
   - Depends on: none (independent of steps 1–3, but logically same PR)

5. [ ] **Backend: Unit tests (POST + GET handlers)** — `test(onboarding): Add 10 unit tests for POST/GET endpoints`
   - Test file: `backend/tests/test_onboarding.py`. Use existing Firestore fixtures.
   - Required tests:
     - `test_post_onboarding_creates_record` (201 on first write)
     - `test_post_onboarding_updates_existing` (200 on second write)
     - `test_post_onboarding_invalid_corridor` (400)
     - `test_post_onboarding_rejects_uid_in_body` (400 — uid/userId/sub)
     - `test_post_onboarding_ignores_client_completedAt` (no `completedAt` field accepted; verifies the field is dropped at the Pydantic boundary)
     - `test_post_onboarding_markComplete_sets_completedAt_once` (server-stamped, immutable on second markComplete)
     - `test_post_omitted_field_preserves_existing` (missing key in body = no change to Firestore field)
     - `test_post_null_field_clears_existing` (explicit `null` = `DELETE_FIELD`)
     - `test_post_onboarding_validates_displayName_charset` (control chars rejected; max length enforced; NFKC normalized)
     - `test_post_onboarding_missing_auth` (401)
     - `test_get_onboarding_returns_record` (200)
     - `test_get_onboarding_404_when_empty`
     - `test_get_onboarding_cross_tenant_isolated` (uid from token, not URL — handler can't be tricked into reading another uid)
   - Owner: backend-builder
   - Parallel-safe: yes
   - Depends on: steps 1–3

6. [ ] **Frontend: Extend puente-api.ts with POST/GET onboarding** — `feat(onboarding): Add getOnboarding + saveOnboarding to API client`
   - Two new functions: `getOnboarding(): Promise<OnboardingProfile | null>` (returns null on 404), `saveOnboarding(data: OnboardingProfileIn): Promise<OnboardingProfile>`.
   - `OnboardingProfileIn` type shape: `{ displayName?: string | null; company?: string | null; corridors?: string[] | null; markComplete?: boolean }`.
   - Both use `authedFetch()`, reuse existing Bearer token attachment.
   - Owner: jay (primary agent — `frontend-engineer` is wrong scope)
   - Parallel-safe: yes
   - Depends on: backend endpoints live (steps 2–3)

7. [ ] **Frontend: Refactor onboarding.ts for server-backed persistence** — `feat(onboarding): Add async Firestore persistence + localStorage cache`
   - Refactor `getOnboarding()` to async with 5-min cache + server fallback (per pseudo-code in "Frontend Changes" section).
   - `saveOnboarding()` calls `apiClient.saveOnboarding()`, then caches the server response.
   - `isOnboarded()` becomes async; checks `completedAt`.
   - `markOnboarded()` becomes async; calls `saveOnboarding({ markComplete: true })` (no client timestamp).
   - Add helpers: `getOnboardingFromLocalStorage()` (direct read, no cache), `cacheOnboarding()`, `isCacheExpired()`, `migrateLocalStorageToServer()` (with the one-shot sentinel from the Migration section above), `validateCorridorsClient()` (matches backend literal).
   - Owner: jay
   - Parallel-safe: no
   - Depends on: step 6

8. [ ] **Frontend: Update LoginPage routing logic** — `feat(onboarding): Make post-signin routing async + server-backed`
   - Refactor `LoginPage.tsx:30-53` (`handleSubmit`) and `:55-69` (`handleSocial`).
   - Replace synchronous `isOnboarded(uid)` calls with `await isOnboarded(uid)`.
   - Error boundary: on network error, pessimistically navigate to `/onboarding` (user can skip if already onboarded; server-side check on `/onboarding` mount can short-circuit).
   - Owner: jay
   - Parallel-safe: no
   - Depends on: step 7

9. [ ] **Frontend: AuthProvider migration hook + logout invalidation** — `feat(onboarding): Migrate localStorage on signin, clear on logout`
   - Add `useEffect` in `auth.tsx` `AuthProvider` that fires when `user.uid` becomes available; call `migrateLocalStorageToServer(user.uid)` (one-shot via sentinel).
   - Update `logout()` to clear `puente.onboarding.{uid}`, `puente.onboarding.{uid}.lastSyncAt`, and `puente.onboarding.migrated.{uid}` BEFORE calling Firebase `signOut`.
   - Owner: jay
   - Parallel-safe: yes
   - Depends on: step 7

10. [ ] **Frontend: Unit tests for onboarding.ts** — `test(onboarding): Add 8 vitest tests for cache + server sync`
    - Test file: `frontend-app/src/lib/__tests__/onboarding.test.ts`
    - Mock `puente-api.ts` via `vi.mock()`.
    - Cover: cache-hit (fresh), cache-miss → server fetch, server-fetch-error → stale-cache fallback, `markOnboarded()` sends `markComplete: true` (NO client timestamp), migration sentinel prevents second run, migration skips when server already has data, logout clears all three localStorage keys.
    - Owner: jay
    - Parallel-safe: yes
    - Depends on: step 7

11. [ ] **Frontend: E2E tests (Playwright)** — `test(onboarding): Add 4 Playwright e2e tests for full flow`
    - Test file: `frontend-app/e2e/onboarding.spec.ts`
    - Scenarios:
      - New user signs up → completes onboarding → data in Firestore (verified via GET endpoint)
      - User logs out → clears browser cache → logs back in → skips onboarding (lands on dashboard)
      - Migration: localStorage seeded with old entry → on next signin, server has the data and `migrated.{uid}` sentinel is set
      - Cross-tenant: User B can't access User A's Firestore record (rules-layer denial)
    - Requires test Firebase project or mock server.
    - Owner: jay
    - Parallel-safe: yes
    - Depends on: steps 7–9

12. [ ] **Documentation + follow-up KAN tickets** — `docs: Add onboarding endpoints + file 4 follow-up tickets`
    - Add `POST /api/v1/onboarding` and `GET /api/v1/onboarding` to `docs/CLAUDE.md` "Endpoints (live)" section.
    - Note the new Firestore `users` collection (PII-bearing) in the data-handling section.
    - File four follow-up KAN tickets per the security audit's out-of-scope items: (a) OFAC screening on `company` field, (b) GDPR/CCPA delete-runbook entry for `users/{uid}`, (c) per-uid server-side rate limit on onboarding writes, (d) `audit/{uid}/onboarding` subcollection for repudiation defense.
    - Owner: jay
    - Parallel-safe: yes
    - Depends on: steps 1–9

13. [ ] **Rollout & Verification** — `chore(onboarding): Deploy + verify on staging, then production`
    - Merge PR with all above steps.
    - Deploy `firestore.rules` first (`firebase deploy --only firestore:rules`) — backend write attempts will fail until the rule is live. CI ordering matters.
    - Deploy backend (Cloud Run via GitHub Actions on push to main).
    - Deploy frontend (Cloud Run via GitHub Actions on push to main).
    - Smoke tests:
      1. Sign up new user on staging, complete onboarding, verify Firestore write via Console.
      2. Old test user with localStorage entry, signin on staging, verify migration to Firestore + sentinel set.
      3. Different browser / incognito, signin as same user, verify onboarding skipped.
      4. Cross-tenant attempt (use Firestore Console as another uid) — verify rules deny.
    - Monitor Cloud Run logs for 401/500 errors during rollout. Confirm logs do NOT contain `displayName`/`company` strings.
    - Owner: jay
    - Parallel-safe: no
    - Depends on: steps 1–12

---

## Summary

This plan transforms onboarding from a client-only (localStorage) system to a **server-backed** system with **client-side caching for performance**. The backend uses Firestore as the authoritative store, keyed by Firebase UID, with security rules ensuring cross-tenant isolation. The frontend fetches from the server on cold-start, caches for 5 minutes, and transparently migrates any old localStorage entries on the user's next signin. LoginPage routing becomes async to check the server before deciding between onboarding and dashboard. Tests cover both backend (9 pytest tests) and frontend (8 vitest + 4 Playwright e2e). The result: Maria's onboarding state persists across devices, browsers, and cache clears — the core user experience fix this bug report requires.
