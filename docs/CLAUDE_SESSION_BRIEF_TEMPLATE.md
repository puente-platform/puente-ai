# Claude Session Brief Template — Puente AI

Copy this into a new Claude chat at the start of every session.

---

## Session Objective

- Date:
- Owner:
- Goal for this session (one concrete outcome):
- Why this matters now:

---

## Current State Snapshot

- Branch:
- Environment (local/staging/prod):
- What is already done (3-5 bullets):
  - 
  - 
  - 
- What is not done yet (3-5 bullets):
  - 
  - 
  - 
- Current blocker (if any):

---

## Scope for This Session

- In scope:
  1.
  2.
  3.
- Out of scope:
  - 
  - 

---

## Constraints (Non-Negotiable)

- Use legal-safe language:
  - "AI-powered indicators", "compliance flags", "requires operator review"
- Protected backend routes require Firebase auth.
- No secrets or keys in code or docs.
- No provider lock-in in business logic (keep adapter boundaries).

---

## Definition of Done

- Functional outcome:
- Technical acceptance criteria:
  - [ ] Tests pass
  - [ ] Lints pass
  - [ ] Error handling verified
  - [ ] Docs updated (if behavior changed)
- Evidence to return:
  - Changed files
  - Test command + result
  - Any follow-up tickets needed

---

## Files Likely Touched

- `backend/app/...`
- `backend/tests/...`
- `docs/...`

---

## Commands

- Run tests:
  - `cd backend && ./venv/bin/python -m pytest tests/ -v`
- Optional targeted test:
  - `cd backend && ./venv/bin/python -m pytest tests/test_auth.py -v`

---

## Jira Mapping

- Related tickets (KAN IDs):
  - 
  - 
- New tickets to create if needed:
  - 

---

## Output Format Requested from Claude

Please return:
1. What changed and why
2. Files modified
3. Test/lint results
4. Risks or follow-up items
5. Suggested commit message (Conventional Commit + KAN ID)

---

## Quick Fill Example

- Goal: "Wire live transaction details page to backend response ID."
- Done means:
  - `View details` routes to `/transactions/:id`
  - frontend calls `GET /api/v1/transactions/{id}`
  - demo fallback disabled for this path
  - errors shown instead of sample cards
