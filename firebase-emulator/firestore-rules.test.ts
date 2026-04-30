/**
 * Firestore security rules unit tests.
 *
 * Tests (a) authenticated user reads/writes own doc — ALLOWED
 *        (b) authenticated user A reads/writes user B's doc — DENIED
 *        (c) unauthenticated request — DENIED
 *
 * Requires the Firestore emulator to be running on port 8080.
 * In CI, start it with:
 *   firebase emulators:start --only firestore --project demo-test &
 *   npx wait-on tcp:8080
 *
 * Then run:
 *   npm test
 */

import {
  assertFails,
  assertSucceeds,
  initializeTestEnvironment,
  RulesTestEnvironment,
} from "@firebase/rules-unit-testing";
import { doc, getDoc, setDoc } from "firebase/firestore";
import * as fs from "fs";
import * as path from "path";

const PROJECT_ID = "demo-test";
const RULES_PATH = path.resolve(__dirname, "../firestore.rules");

let testEnv: RulesTestEnvironment;

beforeAll(async () => {
  const rules = fs.readFileSync(RULES_PATH, "utf8");
  testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: {
      host: "localhost",
      port: 8080,
      rules,
    },
  });
});

afterAll(async () => {
  await testEnv.cleanup();
});

afterEach(async () => {
  await testEnv.clearFirestore();
});

// ---------------------------------------------------------------------------
// Test (a): Authenticated user reads and writes their own document — ALLOWED
// ---------------------------------------------------------------------------
describe("own-document access", () => {
  it("allows authenticated user to write their own users/{uid} doc", async () => {
    const uid = "user-alice";
    const ctx = testEnv.authenticatedContext(uid);
    const docRef = doc(ctx.firestore(), "users", uid);

    await assertSucceeds(
      setDoc(docRef, {
        displayName: "Alice",
        company: "Acme Corp",
        corridors: ["mia-bog"],
      })
    );
  });

  it("allows authenticated user to read their own users/{uid} doc", async () => {
    const uid = "user-alice";

    // Seed the document via admin SDK (bypasses rules)
    await testEnv.withSecurityRulesDisabled(async (adminCtx) => {
      await setDoc(doc(adminCtx.firestore(), "users", uid), {
        displayName: "Alice",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    });

    const ctx = testEnv.authenticatedContext(uid);
    const docRef = doc(ctx.firestore(), "users", uid);

    await assertSucceeds(getDoc(docRef));
  });
});

// ---------------------------------------------------------------------------
// Test (b): Authenticated user A cannot read or write user B's document — DENIED
// ---------------------------------------------------------------------------
describe("cross-tenant isolation", () => {
  it("denies authenticated user A writing user B's users/{uid} doc", async () => {
    const uidA = "user-alice";
    const uidB = "user-bob";
    const ctxA = testEnv.authenticatedContext(uidA);
    const bobDocRef = doc(ctxA.firestore(), "users", uidB);

    await assertFails(
      setDoc(bobDocRef, { displayName: "Eve pretending to be Bob" })
    );
  });

  it("denies authenticated user A reading user B's users/{uid} doc", async () => {
    const uidA = "user-alice";
    const uidB = "user-bob";

    // Seed Bob's document
    await testEnv.withSecurityRulesDisabled(async (adminCtx) => {
      await setDoc(doc(adminCtx.firestore(), "users", uidB), {
        displayName: "Bob",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    });

    const ctxA = testEnv.authenticatedContext(uidA);
    const bobDocRef = doc(ctxA.firestore(), "users", uidB);

    await assertFails(getDoc(bobDocRef));
  });
});

// ---------------------------------------------------------------------------
// Test (c): Unauthenticated requests — DENIED
// ---------------------------------------------------------------------------
describe("unauthenticated access", () => {
  it("denies unauthenticated write to any users/{uid} doc", async () => {
    const uid = "user-alice";
    const ctx = testEnv.unauthenticatedContext();
    const docRef = doc(ctx.firestore(), "users", uid);

    await assertFails(setDoc(docRef, { displayName: "Attacker" }));
  });

  it("denies unauthenticated read of any users/{uid} doc", async () => {
    const uid = "user-alice";

    // Seed the document
    await testEnv.withSecurityRulesDisabled(async (adminCtx) => {
      await setDoc(doc(adminCtx.firestore(), "users", uid), {
        displayName: "Alice",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    });

    const ctx = testEnv.unauthenticatedContext();
    const docRef = doc(ctx.firestore(), "users", uid);

    await assertFails(getDoc(docRef));
  });
});
