# Analyze Dashboard — Phase 1 Expansion (Operator Cut)

**Date:** 2026-05-05
**Status:** Design — plan written; implementation in progress
**Owner:** Jay Alexander (primary agent + frontend execution)
**Scope:** Frontend-only, surfaces fields the backend already extracts
**Depends on:** None (independent of KAN-22, extraction-upgrade, KAN-46)
**Phase 2/3 follow-ups:** Tracked separately; this spec only covers Phase 1

---

## 1. Context

The current `AnalyzePage` (`frontend-app/src/pages/AnalyzePage.tsx`) renders three verdict cards after analysis completes: **Fraud Risk**, **Compliance**, **Payment Routing**. The backend's `extraction.fields` payload contains roughly 14 additional fields plus a `line_items` array — none of which surface in the UI today. Maria (founding-wedge persona, Miami liquidation operator) currently has no way to verify what the AI extracted from her invoice or to scan goods/cost/parties/dates without re-opening the source PDF.

**Why now (and why not later):** Phase 1 ships the no-regret slice — fields the backend already emits — independent of the gated work (KAN-22 customer interviews, extraction-upgrade backend ticket #56, KAN-46 routing audit). Phase 2 dashboard work (extraction confidence %, `seller_country` provenance, BEC IBAN flag) depends on the upgrade ticket landing and is intentionally deferred.

**Strategic constraints honored:**
- PRD v0.3 broker-augmentation positioning — Carlos persona is co-equal but downstream of KAN-22 signal. This spec leaves a forward-compat seam (`viewMode` prop) without building any Carlos UI.
- "No churn" engineering value — the existing 3 verdict cards are untouched. New work in new files, wired in at one integration point.
- Mobile-first — Maria likely uploads from her phone after meeting a supplier.

## 2. Goal & Non-Goals

### Goal

Render the currently-extracted invoice detail in four new dashboard sections beneath the existing 3-card verdict bar, using only existing design tokens and component primitives, fully bilingual (EN + ES), mobile-first, ~5 days of frontend work.

### Non-goals (Phase 1 explicitly excludes)

| Out of scope | Why deferred | Where it lives |
|---|---|---|
| Extraction confidence / coverage % | Requires `extraction.extraction_quality` field from backend | Phase 2, after extraction-upgrade ticket |
| `seller_country` provenance badge | Requires Gemini-inferred field from upgrade | Phase 2 |
| BEC fraud signal (`remit_to_name` ≠ `supplier_name`, IBAN substitution flag) | Requires both fields routed into `field_mapping` (KAN-46 decision point) + analysis pass | Phase 2 |
| Tariff exposure / landed cost | Requires HS code classification | Phase 3 (KlearNow integration territory) |
| Counterparty intel / prior-transaction history | Requires audit subcollection | Filed as separate KAN ticket |
| Carlos-broker view | Persona gated on KAN-22 signal | Architecture leaves seam, implementation deferred |
| Accessibility audit (axe-core) | Not blocker for Phase 1 | Filed as separate ticket |
| Visual regression snapshots | Too brittle for Phase 1 churn | Skipped |

## 3. User Goal & Mental Model

Maria opens the dashboard after analysis completes and is asking herself a comprehensive set of questions: *Did the AI read this correctly? What am I buying? What does this break into? Who am I paying, and where is it going? When is it due?* Phase 1 answers the second–fifth questions with currently-extracted data. The first question (extraction confidence) is Phase 2.

The four new sections map 1:1 to those questions:

| # | Section | Maria's question | Maps to fields |
|---|---|---|---|
| 1 | Goods | "What am I buying?" | `extraction.line_items[]` |
| 2 | Cost breakdown | "What does this break into?" | `net_amount`, `tax_amount`, `freight_charge`, `invoice_amount`, `currency` |
| 3 | Parties | "Who am I paying, and where is it going?" | `exporter_*`, `importer_*`, `shipping_*` |
| 4 | Dates & terms | "When is this due?" | `invoice_date`, `due_date`, `payment_terms`, `purchase_order` |

## 4. Layout

**Stacked sections, single-page mobile-first scroll.** The existing 3-card verdict bar (lines 322–504 in `AnalyzePage.tsx`) stays in place. New sections render beneath it as a single composed component (`<InvoiceDetailSections>`), in the order above. Visual divider (label-only, no horizontal rule) separates the verdict bar from the detail sections.

Rejected alternatives:
- **Tabs** — hides content, breaks the "Maria scans the page in 10 seconds" mental model, +2 days build.
- **Two-column split** — collapses badly on mobile, +3 days build for clean responsive fallback.

## 5. Architecture

### File layout (all new)

```
frontend-app/src/components/analysis/
  DashboardSection.tsx        # generic shell: title + icon + slot
  FieldRow.tsx                # generic label+value row, single source of truth for "Not extracted" empty state
  LineItemsTable.tsx          # responsive table; reconciliation pill (Matched/Discrepancy)
  PartyCard.tsx               # one-party block: name + address + contact + tax_id
  InvoiceDetailSections.tsx   # wrapper composing the 4 sections; takes viewMode prop
  sections/
    GoodsSection.tsx
    CostBreakdownSection.tsx
    PartiesSection.tsx
    DatesSection.tsx

frontend-app/src/lib/
  extraction-helpers.ts       # factored from AnalyzePage.tsx:218-246
                              # exports: parseAmount, fieldString, computeInvoiceAmount,
                              # plus new: formatDate, formatPaymentTerms, partyFromFields
```

### Component responsibilities

- **`<DashboardSection title icon>`** — `Card` shell with `bg-gradient-card` + `border-gold-subtle`, the existing 11px uppercase-tracking label header, optional Lucide icon. Children fill the body. **Not used to replace the existing 3 verdict cards** — those stay verbatim to avoid churn. Used only for the 4 new sections.

- **`<FieldRow label value hint?>`** — when `value` is `null` / `undefined` / `""`, renders `—` plus a muted "Not extracted" hint. Single source of truth for empty-state UX. Phase 2 fields will inherit this for free. **Type contract:** `value: string | number | null | undefined` (deliberately NOT `ReactNode`) — prevents any future contributor from passing an HTML-bearing element through the row primitive that touches every PII field.

- **`<LineItemsTable items invoiceAmount>`** — desktop: 4-column grid (Description / Qty / Unit / Amount). Mobile: stacked card-per-item. Footer row computes `Σ(items.amount)` and renders a `<Pill>` against `invoiceAmount` (see section 6 below for threshold).

- **`<PartyCard label fields>`** — vertical block: bold name → address → muted contact lines (email, phone) → muted tax-id badge. Rendered three times in `PartiesSection` (exporter, importer, ship-to). Returns `null` when `name` is missing (graceful degradation when only some parties extract).

### Data flow

```
AnalyzePage (existing state)
  └─ analysisData: AnalyzeResponse
       └─ extraction.fields, extraction.line_items
            ↓ (one prop)
            <InvoiceDetailSections extraction={extraction} viewMode="operator">
                 ├─ <GoodsSection />          # reads extraction.line_items + invoice_amount
                 ├─ <CostBreakdownSection />  # reads net/tax/freight/invoice/currency
                 ├─ <PartiesSection />        # reads exporter_*, importer_*, shipping_*
                 └─ <DatesSection />          # reads invoice_date, due_date, payment_terms, purchase_order
```

No new state, no new fetches, no new context. New components are pure functions of `analysisData.extraction`.

**Logging discipline (binding rule):** No `console.log` / `console.warn` / `console.error` / `console.info` / `console.debug` call in any new file may receive a value derived from `extraction.fields` or `extraction.line_items`. Error objects from API failures may be logged. Inherits the `# noqa: do-not-log-pii` discipline established in the onboarding-persistence PR. Reviewer greps the diff to confirm.

### Forward-compat seam (deliberate, minimal)

`<InvoiceDetailSections>` accepts `viewMode: 'operator' | 'broker' = 'operator'`. Phase 1 implements only `'operator'`. The `'broker'` branch **explicitly throws** `new Error("Broker view unimplemented")` — proves we haven't accidentally shipped a half-baked Carlos UI.

**Owner-ship requirement (per mentor stress-test #2):** A parked Jira ticket "Implement viewMode='broker' branch in InvoiceDetailSections" is filed before this spec ships. Without a tracked owner, the seam becomes invisible debt. Ticket is parked (PARKED bucket) until KAN-22 interview signal lands.

### Helper factoring

The existing `parseAmount`, `fieldString`, `computeInvoiceAmount` helpers (`AnalyzePage.tsx:218-246`) move to `lib/extraction-helpers.ts` so the new section components can import them. AnalyzePage imports them back. **Zero behavior change to the helpers.** New helpers (`formatDate`, `formatPaymentTerms`, `partyFromFields`) added in the same file.

## 6. Reconciliation Pill — Threshold Validation

The Goods section computes `Σ(line_items.amount)` and compares against `invoice_amount`. Within tolerance → green "✓ Matched" pill. Outside → amber "⚠ Discrepancy" pill.

**Phase 1 threshold:** 1% absolute relative difference, i.e. `abs(sum - total) / total < 0.01`.

**Validation requirement (per mentor stress-test #1):** "1% feels right" is not a measurement. Before merging, run the threshold against:
- The deterministic test invoice from PR #49 (synthetic, should always match exactly)
- ≥ 3 real invoices when KAN-22 interviews land (validate against actual Document AI rounding behavior)

If real-invoice testing reveals false discrepancies on clean invoices, raise the threshold to 2% with a comment explaining the empirical basis. Acceptance criterion includes documenting which invoices were tested.

**Why this matters:** A false "Discrepancy" pill on a clean invoice destroys the trust signal. Better to ship at 2% and tune down than to ship at 1% and have Maria see false alarms on her first real invoice.

## 7. Style Fidelity Contract

No new design tokens. No new component primitives. Specifically:

- **Shells** — `Card`, `CardContent` from `@/components/ui/*`. Same `bg-gradient-card` + `border-gold-subtle`, same `rounded-xl` + `p-4 md:p-5` rhythm.
- **Color tokens** — only existing: `emerald`, `warm-amber`, `danger-red`, `ocean`, `primary`, `gold-subtle`, `muted-foreground`.
- **Typography** — `font-display font-bold` for section titles, the existing `text-[11px] font-semibold tracking-wider uppercase` label style for every label.
- **Icons** — Lucide only. New icons added: `Package`, `Receipt`, `Building2`, `Calendar` (all in the existing bundle, zero new deps).
- **Responsive** — same `md:` breakpoint pattern. Mobile-first.
- **i18n** — every visible string through `t()` in `lib/i18n.tsx`. EN + ES from day one. ~30 new keys.
- **Empty states** — match the "data unavailable" pattern from PR #55 (the routing fallback). One pattern, applied consistently.

**XSS discipline:** No `dangerouslySetInnerHTML`, no `innerHTML`, no `eval`. Extraction values render only as text children of React elements (`{value}` / `{t('key')}`). All ~30 new i18n keys must return plain strings — no HTML tags inside translation values. The shadcn `chart.tsx` primitive does use `dangerouslySetInnerHTML` for CSS variable injection; do not "follow the existing pattern" — that's CSS, this is PII text.

**Definition of done — visual:** A reviewer pulling the branch should not be able to tell which sections were original and which were Phase 1.

## 8. Test Plan

### Unit tests (vitest)

| File | Coverage |
|---|---|
| `extraction-helpers.test.ts` | `parseAmount` shapes (number / string / `{value}`); `formatDate` ISO + null; `partyFromFields` returns `null` when name missing |
| `DashboardSection.test.tsx` | Renders title + icon + children; gold-subtle border applied |
| `FieldRow.test.tsx` | Value renders when present; "—" + "Not extracted" hint when value `null`/`undefined`/`""` |
| `LineItemsTable.test.tsx` | Rows render from items; Matched pill within threshold; Discrepancy pill outside; empty state |
| `PartyCard.test.tsx` | All fields present; partial party (name only); returns `null` when name missing |
| `sections/*.test.tsx` (×4) | Each section against `extraction-rich` and `extraction-sparse` fixtures |

### Integration test (vitest)

`InvoiceDetailSections.test.tsx` — renders 4 sections in order against rich fixture; default `viewMode="operator"`; explicit `viewMode="broker"` throws (asserts forward-compat seam isn't accidentally live).

### E2E (Playwright)

- `analyze-detail-sections.spec.ts` — upload deterministic test invoice (PR #49 generator) → assert all 4 section headings visible → assert ≥1 line-item row + Matched pill
- `analyze-empty-state.spec.ts` — upload sparse fixture → assert "Not extracted" hint appears in expected fields → no crashes

### Test fixtures (new under `frontend-app/src/test/fixtures/`)

- `extraction-rich.ts` — all 14 fields + 4 line items
- `extraction-sparse.ts` — only `invoice_amount` + `currency` + `exporter_name`; everything else missing/null

**Synthetic-PII rules (binding for all fixtures):** Real customer names, real EIN/NIT/CUIT/RFC values, and real email domains MUST NOT appear in fixtures. The brainstorming-session mockup used a real customer supplier name with its corresponding NIT (intentionally excluded from this spec to avoid committing PII to repo history) — that name is a real company from a real founder-uploaded invoice referenced in the extraction-upgrade ticket draft and MUST NOT be copied into fixtures.

Fixture identifiers must satisfy:
- **Supplier / importer names** — obviously fictional sentinels (e.g., `"Acme Test Exports SAS"`, `"Liquidation Test Co"`, `"Sample Trading Inc"`).
- **EIN** — `"00-0000000"`-style sentinel or IRS-reserved test range.
- **Colombian NIT / Mexican RFC / Argentine CUIT** — fictional values that fail public-registry lookup (e.g., `"NIT 000.000.000-0"`).
- **Email domains** — RFC 2606 reserved only: `example.com`, `example.org`, `example.net`, `test.localhost`. Never `gmail.com` / real corporate domains.
- **Addresses** — fictional or generic city + ZIP (e.g., `"123 Test St, Doral, FL 33172"`); avoid real warehouses or known goTRG-adjacent addresses.
- **Phone numbers** — North American Numbering Plan reserved (555-prefix) or country-code-equivalent reserved ranges.
- **Bank account / IBAN** — Phase 2 concern; flagged here so fixture authors know not to use real IBAN format checksums when fields land.

## 9. Acceptance Criteria

- [ ] All 4 sections render below the existing 3-card verdict bar
- [ ] Card shells, label typography, color tokens match existing 3 cards 1:1 (no new design tokens)
- [ ] Empty fields render `—` + "Not extracted" hint via `<FieldRow>` (never silent-hide)
- [ ] Reconciliation pill correct against PR #49 test invoice; threshold value documented with empirical basis
- [ ] EN + ES i18n complete for all ~30 new label keys
- [ ] Mobile viewport (375px) passes: line items collapse to per-item cards, sections stack
- [ ] Bundle size delta < 10KB
- [ ] No new npm deps
- [ ] All existing AnalyzePage tests pass (factored helpers preserve behavior)
- [ ] All new vitest tests pass
- [ ] Both Playwright specs pass against `npm run dev`
- [ ] PR description includes screenshots: rich + sparse fixture, EN + ES, mobile + desktop
- [ ] Parked Jira ticket filed for `viewMode="broker"` implementation owner
- [ ] No `console.*` call in any new file passes a value derived from `extraction.fields` or `extraction.line_items` (reviewer greps the diff to confirm)
- [ ] No new use of `dangerouslySetInnerHTML`, `innerHTML`, or `eval` in any Phase 1 file
- [ ] `<FieldRow>` `value` prop typed `string | number | null | undefined` (not `ReactNode`)
- [ ] All ~30 new i18n keys return plain strings; no key value contains HTML tags
- [ ] Fixtures conform to synthetic-PII rules (§8): no real customer names, RFC 2606 email domains only, sentinel-format identifiers
- [ ] Production-bundle audit: `npm run build` then `grep -r "<synthetic-supplier-marker>" dist/` returns zero hits (proves fixtures don't ship to prod)

## 10. Follow-ups Filed (Not in Phase 1)

The following Jira tickets are filed as part of this spec landing — none block Phase 1:

1. **viewMode="broker" implementation** (parked, gated on KAN-22 signal) — owns the explicit `throw` removal
2. **Phase 2 dashboard fields** — extraction quality summary, seller_country provenance, BEC IBAN flag — gated on extraction-upgrade ticket #56 landing
3. **Accessibility audit (axe-core integration)** — Phase 1 hits a11y minimums by inheriting existing patterns; full audit deferred
4. **Visual regression / Percy snapshots** — too brittle for Phase 1; revisit after layout settles
5. **Error-reporting redaction layer (Phase-2-or-later)** — no analytics / error-reporting tooling is wired today (no Sentry / LogRocket / Datadog / PostHog / GA per fintech-security audit). If any error-reporting integration is proposed in a future phase, it MUST land in its own PR with an explicit redaction layer that strips `extraction.fields` and `extraction.line_items` from any error context before transmission.

## 11. Connection to KAN-46 (Backend Decision Point)

The Phase 2 BEC fraud signal depends on Document AI v2's `remit_to_name` and `supplier_iban` entities being routed into `field_mapping` (surfacable to frontend) instead of `_ignored_entity_types` (silent). When the paused KAN-46 backend-builder dispatch resumes, the agent brief must include this decision: **route those two entities into `field_mapping` rather than ignore-list**, otherwise Phase 2 dashboard work has no path forward without a separate backend ticket.

This spec does not implement that backend change. It documents the dependency so the KAN-46 brief can be updated before dispatch.

## 12. Open Questions / Stress-Tests

Resolved in this spec via mentor agent's stress-tests:

1. ✅ **Reconciliation threshold** — flagged for empirical validation (section 6); 1% is provisional, requires real-invoice testing.
2. ✅ **`viewMode="broker"` ownership** — parked Jira ticket filed before implementation begins (section 5).

Resolved via fintech-security review (2026-05-05, verdict: APPROVED-WITH-CONDITIONS, 2 REQUIRED + 3 RECOMMENDED, all applied):

3. ✅ **Logging discipline** — explicit binding rule added to §5 + acceptance criterion in §9.
4. ✅ **Synthetic-PII rules for fixtures** — pinned in §8 with concrete sentinels per identifier type. The real founder-uploaded invoice supplier name (intentionally excluded from this spec) is explicitly forbidden in fixtures.
5. ✅ **XSS discipline** — added to §7 + acceptance criterion in §9.
6. ✅ **`<FieldRow>` value prop type** — constrained to `string | number | null | undefined` in §5 + acceptance criterion in §9.
7. ✅ **Production-bundle audit** — added as acceptance criterion in §9.
8. ✅ **Error-reporting redaction follow-up** — added to §10 (#5) for future Sentry/etc. integration.

OUT OF SCOPE confirmations (no action needed): empty-state info-leak, cross-tenant rendering risk, screenshot/clipboard exposure, analytics auto-attach (no analytics wired today).

Open for review:

3. **Section icon choice** — `Package` / `Receipt` / `Building2` / `Calendar` is one cut. Alternative: omit section icons entirely (label typography is strong enough). Decision deferred to implementation; either path satisfies the style fidelity contract.
4. **`<PartyCard>` returns null vs renders skeleton** — when an entire party (e.g., importer) has no extracted fields, do we hide the card or show a labeled skeleton? Current spec: returns `null` for individual party when name missing, but `<PartiesSection>` always renders the section heading. Open to the alternative if the founder prefers parties always visible as labeled empty states.

---

## Appendix A — Visual Preview

Full dashboard preview rendered during brainstorming session — see `.superpowers/brainstorm/82521-1777953613/content/06-full-preview.html` (gitignored, regenerable from this spec).
