# Plan — KAN-21: Export Corridor Compliance Rules (US→LATAM)

> **Regulatory framing (locked per PRD v0.3):** Puente AI flags
> compliance signals and surfaces broker-actionable recommendations.
> ECCN classification, export-license determination, OFAC adjudication,
> and DR-CAFTA Certificate of Origin sign-off remain the licensed
> customs broker's responsibility. The system recommends; the broker
> decides.

## Context

- **KAN ticket:** KAN-21
- **Phase:** Phase 2.5 (extension to invoice intelligence v1, gated on customer interviews)
- **Owning agent:** backend-builder
- **Status:** Un-parked 2026-04-29 (previous parking rationale "imports are the wedge" invalidated by PRD v0.3 direction-agnostic corridor reframe)
- **ADR references:** None yet; this work will follow existing patterns in `backend/app/services/compliance.py`
- **Depends on:** KAN-22 (Miami importer interviews — required to validate rule thresholds and ECCN handling priorities)
- **Related features:** KAN-4 (compliance gap detection — shares `services/compliance.py`), KAN-23 (payment routing)

## Overview

Maria (SME operator) and Carlos (licensed customs broker) are co-equal personas on every transaction per PRD v0.3. Maria's founding-wedge profile is a US-based liquidation trader shipping to LATAM resellers (e.g., goTRG → Bogotá). In US customs terms, she is an **exporter**, not an importer. Carlos clears the shipment and signs off on the regulated determinations. KAN-21 extends the existing import-focused compliance rules (India Form 15CA, agricultural phyto certs, US CBP entry) with the five export-specific compliance flags needed for the US→LATAM corridor:

1. **EAR entity-list screening** — deny-party check on consignee
2. **BIS export-license flags** — ECCN classification and license-required signal
3. **DR-CAFTA Certificate of Origin** — origin claim parsing for duty-free preference
4. **Dual-use goods detection** — flag items requiring license review (subset of EAR scope)
5. **Routed-export-transaction (RET) indicators** — Foreign Principal Party in Interest (FPPI) vs US Principal Party in Interest (USPPI) routing on commercial invoices

These rules are conditional on the export direction (`seller_country="US"`) and will land in the existing `services/compliance.py` checker, keyed alongside the import-side rules.

## Engineering Scope vs Research Scope

**This plan covers mechanical infrastructure only.** Rule thresholds, ECCN category mappings, and CAFTA-DR member validation depend on KAN-22 customer interviews. Steps marked "needs interview data" will unblock once the interviews happen.

- **Mechanical:** BIS Entity List API integration, DR-CAFTA member country list seeding, RET indicator logic
- **Interview-dependent:** Which ECCN categories to flag, license-required thresholds, consignee-screening strictness, CAFTA-eligible origin thresholds

## Steps

1. [ ] **Add export direction constants and entity-screening infrastructure to `services/compliance.py`** — owner: backend-builder — parallel_safe: yes — depends_on: none
   - Add `_EXPORT_DIRECTION_ORIGINS = {"US"}` constant for US→LATAM flows
   - Add `_DR_CAFTA_MEMBERS = {"CR", "DO", "SV", "GT", "HN", "NI"}` (the six non-US DR-CAFTA parties: Costa Rica, Dominican Republic, El Salvador, Guatemala, Honduras, Nicaragua)
   - Add `_USMCA_MEMBERS = {"MX", "CA"}` separately — USMCA is a distinct treaty tier (not bundled into CAFTA logic). Out of MVP scope; reserved for Phase 2.5+ extension if Maria ships to Mexico.
   - Note: Colombia (US-Colombia TPA), Peru (US-Peru TPA), Chile (US-Chile FTA), and Panama (US-Panama TPA) have separate bilateral FTAs. Out of MVP scope; treat as non-preferential corridors for KAN-21 (no CoO gap fired).
   - Add `_DENIED_PARTY_SOURCES` enum documenting supported feeds: `BIS_ENTITY_LIST`, `OFAC_SDN` (future)
   - Add helper function `_is_export_transaction(seller_country: str) -> bool` for direction detection
   - Add placeholder `_check_denied_party(buyer_name: str, buyer_country: str, source: str) -> tuple[bool, str | None]` that returns `(is_denied, denial_reason)` — initially returns `(False, None)` pending API integration
   - **Commit message:** `feat(KAN-21): add export-direction constants and denied-party stub`

2. [ ] **Integrate BIS Entity List feed via static seed data (not API yet)** — owner: backend-builder — parallel_safe: yes — depends_on: step 1
   - Download BIS Entity List JSON from https://www.bis.doc.gov/index.php/bisdatacenter (free, public)
   - Create `backend/data/bis_entity_list.json` with envelope schema (snapshot metadata is mandatory, not optional — denied-party data without provenance is a compliance footgun):
     ```json
     {
       "source": "https://www.bis.doc.gov/index.php/bisdatacenter",
       "snapshot_date": "YYYY-MM-DD",
       "snapshot_sha256": "<sha256 of entries[] serialized canonically>",
       "entries": [{"name": "...", "country": "...", "type": "...", "reason": "..."}]
     }
     ```
     (seed with ~50–100 known entities for smoke testing)
   - Add `_load_bis_entity_list() -> set[str]` in `services/compliance.py` that loads on startup AND verifies `snapshot_sha256` against `entries`; mismatch raises a startup error (corrupted/tampered file)
   - Add `_bis_entity_list_age_days() -> int` computed from `snapshot_date`
   - Implement `_check_denied_party()` to do case-insensitive substring match against loaded list. If `_bis_entity_list_age_days() > 30`, also emit a `STALE_DENIED_PARTY_DATA` compliance gap (HIGH severity) on every export call so staleness can't be silently bypassed.
   - **Refresh cadence + ownership:** every 30 days, owned by backend-builder. Captured as a recurring scheduled-agent routine; refresh PR commit message: `feat(KAN-21): refresh BIS Entity List snapshot YYYY-MM-DD`. Source-page changelog: https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern.
   - **Clarification needed:** Does Maria need OFAC SDN screening too (Venezuela, Cuba), or just BIS? (See Clarifications Needed)
   - **Commit message:** `feat(KAN-21): load BIS Entity List from static seed (snapshot_date + sha256 + 30-day staleness gap); implement denied-party screening`

3. [ ] **Add ECCN classification and dual-use goods detection** — owner: backend-builder — parallel_safe: yes — depends_on: none
   - Add `_DUAL_USE_ECCN_CATEGORIES = {}` placeholder dict mapping ECCN codes to metadata (e.g., `{"3A001": {"description": "Semiconductor equipment", "license_required": True}}`)
   - Add helper function `_extract_eccn_from_hs_code(hs_code: str) -> list[str] | None` that attempts to parse or cross-reference ECCN from product description (MVP: return `None`, pending ECCN database integration)
   - Add helper `_flag_dual_use_items(extraction: dict) -> list[dict]` that returns list of flagged SKUs with suspicious keywords: `["semiconductor", "electronics", "encryption", "defense", "aerospace", "chemical"]` (reuse existing `_DUAL_USE` token set)
   - Do NOT emit gaps yet; flag structure: `{"sku": "...", "description": "...", "eccn_suspicion_level": "low|medium|high", "action": "..."}` (for informational display in frontend, not compliance blocking)
   - **Clarification needed:** Which ECCN categories trigger mandatory license review vs warning-only? (See Clarifications Needed)
   - **Commit message:** `feat(KAN-21): add ECCN and dual-use goods detection stubs`

4. [ ] **Add DR-CAFTA Certificate of Origin parser and origin-claim validation** — owner: backend-builder — parallel_safe: yes — depends_on: step 1
   - Add `_COO_CAFTA_FIELDS = ["origin_country", "certifier_name", "certifier_email", "claim_percentage_us"]` constants for expected fields in a CAFTA-compliant CoO
   - Add helper `_parse_coo_cafta(extraction: dict) -> dict | None` that looks for `has_certificate_of_origin`, `certificate_origin_country`, and `certificate_us_content_percentage` in extraction
   - Add helper `_is_cafta_eligible_origin(origin_country: str) -> bool` that checks membership in `_DR_CAFTA_MEMBERS` constant
   - Generate a `ComplianceGap` (code `EXPORT_COO_INELIGIBLE_ORIGIN`) if `has_certificate_of_origin=True` but `origin_country` is not CAFTA-eligible
   - Generate a `ComplianceGap` (code `EXPORT_MISSING_COO_CAFTA`) if exporting to a CAFTA-DR member and `has_certificate_of_origin=False` (MEDIUM severity — CoO is duty-savings preferred, not regulatory blocking for liquidation goods)
   - **Interview-dependent:** Is 0% US content acceptable for liquidation goods? Or must US content exceed a threshold (e.g., 35% value-added)? (See Clarifications Needed)
   - **Commit message:** `feat(KAN-21): add DR-CAFTA CoO parsing and eligibility checking`

5. [ ] **Add routed-export-transaction (RET) detection logic** — owner: backend-builder — parallel_safe: yes — depends_on: none
   - Add `_RET_FPPI_KEYWORDS = ["foreign principal", "consignee", "end-use"]` constants
   - Add helper `_infer_ret_indicator(extraction: dict) -> str | None` that attempts to classify transaction as FPPI (Foreign Principal Party In Interest) vs USPPI (US Principal Party In Interest) based on:
     - `has_export_license` field (FPPI often requires explicit license, USPPI can be EAR99)
     - `seller_name`/`buyer_name` address fields (FPPI = foreign address, USPPI = US address)
     - Return value: `"FPPI"`, `"USPPI"`, or `None` (unknown)
   - Log the inferred RET indicator to transaction (not persisted to compliance result yet, just informational for routing and customs staging)
   - **Interview-dependent:** Does commercial invoice extraction capture address fields cleanly? (See Clarifications Needed)
   - **Commit message:** `feat(KAN-21): add RET indicator detection for export transactions`

6. [ ] **Integrate export-compliance checks into main `check_compliance()` function** — owner: backend-builder — parallel_safe: yes — depends_on: steps 1–5
   - Modify `check_compliance(extraction: dict) -> ComplianceResult` to detect export direction: `seller_country == "US"` (assuming US-based exporter)
   - If export direction detected:
     - Call `_check_denied_party(buyer_name, buyer_country)` and generate gap `EXPORT_DENIED_PARTY_CONSIGNEE` (CRITICAL) if match found
     - Call `_flag_dual_use_items(extraction)` and store results in transaction (do NOT block compliance; this is informational)
     - Call `_parse_coo_cafta()` and generate CAFTA-eligibility gaps per step 4
     - Call `_infer_ret_indicator()` and store in transaction for routing layer
   - Import-side checks (India Form 15CA, ISF, CBP, ag phyto) continue to fire on their existing trigger conditions (e.g., `buyer_country == "US"` for US-import flows). Export-side checks are **additive**, not replacement — there is no "skip imports when exporting" branching. A given transaction is either inbound (import triggers fire), outbound (export triggers fire), or — rarely — both (e.g., a US re-export); both sets fire independently with no double-firing because trigger conditions are mutually scoped.
   - Export compliance gaps span severities `"critical"`, `"high"`, and `"medium"`; `"medium"` is reserved for duty-savings/preferential-treaty signals (e.g., DR-CAFTA CoO) that are recommendations rather than regulatory blockers. `"low"` is not used on the export side (regulatory risk floor).
   - **Commit message:** `feat(KAN-21): integrate export-compliance checks into main checker`

7. [ ] **Add export-compliance tests to `test_compliance.py`** — owner: backend-builder — parallel_safe: yes — depends_on: step 6
   - Test scenario: US→Honduras liquidation (seller="US", buyer="HN", amount=$50k, has_coo=False) — Honduras is a DR-CAFTA party
     - Expected: `EXPORT_MISSING_COO_CAFTA` gap (MEDIUM)
   - Test scenario: US→Colombia liquidation (seller="US", buyer="CO", has_coo=False) — Colombia uses US-Colombia TPA, NOT DR-CAFTA
     - Expected: NO `EXPORT_MISSING_COO_CAFTA` gap (Colombia not in `_DR_CAFTA_MEMBERS`); negative-case test that guards against the bug Copilot flagged in plan review
   - Test scenario: US→Venezuela (seller="US", buyer="VE", has_denied_consignee=True)
     - Expected: `EXPORT_DENIED_PARTY_CONSIGNEE` gap (CRITICAL) — if consignee in denied list
   - Test scenario: US→Guatemala dual-use electronics (seller="US", buyer="GT", industry="electronics", has_export_license=False)
     - Expected: dual-use flag (non-blocking, informational) + possibly `EXPORT_LICENSE_REQUIRED` (MEDIUM/HIGH) — **pending interview data on which ECCN categories block**
   - Test scenario: Import (seller="IN", buyer="US") should NOT trigger any export gaps, only import gaps
   - Test scenario: RET detection on US→DR (Dominican Republic) export, FPPI vs USPPI classification
   - Add 5–8 new test cases covering the above scenarios
   - **Commit message:** `test(KAN-21): add export-compliance test scenarios`

8. [ ] **Create feature flag for export-compliance checks (ship behind toggle)** — owner: backend-builder — parallel_safe: yes — depends_on: step 6
   - Add environment variable `EXPORT_COMPLIANCE_ENABLED=false` (default off)
   - In `check_compliance()`, wrap all export-specific checks in `if os.getenv("EXPORT_COMPLIANCE_ENABLED") == "true"`
   - When flag is off, export-direction transactions still run import-side checks (for compat); no export gaps are generated
   - When flag is on, export gaps are generated alongside any applicable import gaps (e.g., a "US→India" transaction would fire India Form 15CA *and* export checks)
   - Set flag to `true` on Cloud Run only after KAN-22 interviews validate rule priorities
   - **Rationale:** KAN-21 is gated on KAN-22; code lands on main behind the toggle to keep PR small and allow parallel work on other features; toggle flips once validation happens
   - **Commit message:** `feat(KAN-21): add feature flag for export-compliance checks`

9. [ ] **Document export-compliance API contract in `/docs/compliance-rules.md`** — owner: backend-builder — parallel_safe: yes — depends_on: step 6
   - Add section "Export Corridor Compliance Rules (US→LATAM)"
   - Enumerate the five rule categories (denied party, ECCN, DR-CAFTA CoO, dual-use, RET)
   - Document each gap code: `EXPORT_DENIED_PARTY_CONSIGNEE`, `EXPORT_MISSING_COO_CAFTA`, `EXPORT_COO_INELIGIBLE_ORIGIN`, etc.
   - Document feature flag: `EXPORT_COMPLIANCE_ENABLED` and when it becomes default true
   - Link to BIS Entity List source data
   - Link to DR-CAFTA member country list (state-maintained, immutable)
   - Note which rules are interview-dependent (placeholder values) vs production-ready
   - **Commit message:** `docs(KAN-21): document export-compliance rules and gap codes`

10. [ ] **Update CLAUDE.md with KAN-21 completion notes** — owner: backend-builder — parallel_safe: yes — depends_on: step 9
    - Add KAN-21 to the DONE list in `docs/CLAUDE.md` once all steps are merged
    - Note: "Export-compliance checks for US→LATAM corridor added behind feature flag. Production flag `EXPORT_COMPLIANCE_ENABLED=true` after KAN-22 customer interviews validate rule thresholds."
    - Add to test coverage: "export-compliance: 8 tests covering denied-party, CAFTA-CoO, dual-use, RET detection, and direction-agnostic validation"
    - **Commit message:** `docs(KAN-21): update build status`

## Test Plan

**Unit tests** (in `test_compliance.py`):
- Denied-party screening: US exporter with consignee in BIS list → `EXPORT_DENIED_PARTY_CONSIGNEE` gap
- DR-CAFTA CoO validation (positive): US→Honduras without CoO → `EXPORT_MISSING_COO_CAFTA` gap; with non-CAFTA origin → `EXPORT_COO_INELIGIBLE_ORIGIN` gap
- DR-CAFTA CoO validation (negative): US→Colombia without CoO → NO CAFTA gap (Colombia not in `_DR_CAFTA_MEMBERS`)
- Dual-use flagging: US→Guatemala semiconductor export → informational flag (non-blocking)
- RET detection: FPPI vs USPPI classification on US export
- Direction isolation: non-US exporter (e.g., seller="IN", buyer="US") skips all export checks; import-side checks fire independently
- Feature flag: with `EXPORT_COMPLIANCE_ENABLED=false`, export gaps should not appear; import-side gaps still fire

**Integration tests** (smoke):
- Upload a real US→LATAM invoice image
- Run `/api/v1/compliance` with the new feature flag enabled
- Verify export gaps appear alongside (or instead of) import gaps
- Verify denied-party and CAFTA checks fire correctly

**Manual verification** (after KAN-22):
- Maria's liquidation-goods shipment to a DR-CAFTA destination (e.g., Honduras / San Pedro Sula reseller): confirm CAFTA-CoO recommendation appears
- Maria's liquidation-goods shipment to Bogotá, Colombia: confirm NO CAFTA-CoO gap fires (Colombia is US-Colombia TPA, out of MVP scope) — only dual-use / RET / denied-party signals
- Carlos (broker) testing: confirm he can toggle export-compliance rules on/off per client

## The Maria Test

Maria (SME operator) and Carlos (her licensed customs broker) work the same shipment together. Maria buys a liquidation truckload of refurbished electronics (keyboards, monitors, hard drives) from goTRG and consolidates it in a Miami warehouse. She sells to a reseller in Bogotá, Colombia for $45,000 USD. Carlos files the entry and signs off on the export-license determination.

**Before KAN-21:** Puente AI would flag missing phyto cert and agriculture-sector checks (irrelevant for electronics liquidation). Compliance score might be artificially LOW. Export license question unanswered.

**After KAN-21:** Puente AI detects `seller_country="US"` (Maria's sales address) and `buyer_country="CO"` (Bogotá reseller). It:
- Screens the buyer against BIS Entity List (they're clean)
- Skips DR-CAFTA CoO logic — Colombia is **not** a DR-CAFTA party; it uses the US-Colombia TPA (separate bilateral FTA), which is out of MVP scope for KAN-21. No CAFTA gap fires.
- Flags SKUs with "semiconductor" / "electronics" keywords as dual-use (informational; explains potential license requirements for certain items)
- Infers RET indicator (USPPI = Maria / US exporter)
- Compliance score: HIGH (no critical gaps); no CAFTA-related gap because Colombia is non-CAFTA

Maria sees: "Your shipment to Bogotá: buyer cleared against BIS Entity List. Three electronics SKUs flagged for potential export control review — consult a customs broker if unsure. Note: Colombia uses the US-Colombia Trade Promotion Agreement, not DR-CAFTA; preferential-origin handling for that corridor is out of scope for this release."

(For comparison: if Maria were shipping the same load to a DR-CAFTA destination like San Pedro Sula, Honduras, the CAFTA CoO recommendation **would** fire — "Your shipment to Honduras can benefit from DR-CAFTA duty savings. Request a Certificate of Origin showing US origin." This is the positive-case path covered by the test scenarios in step 7.)

Result: Maria wins (clear, directional guidance); Carlos the broker wins (Puente handles the routine CAFTA check; Carlos focuses on edge-case ECCN review).

## Clarifications Needed

1. **OFAC screening scope:** Does Maria need Specially Designated Nationals (SDN) screening for Venezuela, Cuba, and Iran? Or is BIS Entity List (dual-use / denials) sufficient for the founding wedge? 
   - _Impact:_ Affects step 2 scope. If yes, add `_OFAC_SDN` feed integration; if no, BIS-only for now, OFAC deferred to Phase 3.

2. **ECCN licensing thresholds:** Which ECCN categories trigger a mandatory "license required" gap (MEDIUM/HIGH severity) vs a "flag for review" advisory (informational)?
   - _Examples:_ 3A001 (semiconductor equipment) — always license-required? Or only if value > $X?
   - _Impact:_ Affects step 3 and step 6 severity logic. Interview-dependent.

3. **DR-CAFTA origin content requirement:** Is 0% US content acceptable for liquidation goods claiming CAFTA preference, or must origin include a minimum US value-add threshold (e.g., 35%)?
   - _Impact:_ Affects step 4 gap severity and messaging. Interview-dependent.

4. **Commercial invoice extraction fidelity:** Do Document AI invoices capture buyer/seller **addresses** cleanly, or just names and countries?
   - _Why:_ RET detection (step 5) relies on address fields to infer FPPI vs USPPI. If addresses are missing, RET classification becomes unreliable.
   - _Impact:_ Affects step 5 implementation. May require Gemini re-parsing or accept limited RET accuracy in MVP.

5. **Feature flag timing:** Should export-compliance ship merged but disabled on Cloud Run, or unmerged pending interviews?
   - _Risk:_ If merged-but-disabled, code is live but toggles off; easier rollback. If unmerged, KAN-21 branch stays open until KAN-22 closes, risking rebase conflicts.
   - _Recommendation:_ Merge with flag disabled. Flip flag to true once interviews happen (ops change, no PR).

6. **Mexico vs DR-CAFTA framing:** Maria also ships to Mexico (USMCA member). Should Mexico be included in the CAFTA-eligible list for CoO checks, or is USMCA a separate rule tier?
   - _Impact:_ Affects step 1 `_DR_CAFTA_MEMBERS` constant. If USMCA is out-of-scope for founding wedge (focus on Caribbean / Colombia / Peru), exclude Mexico. If in-scope, add it.

## Definition of Done

- [ ] BIS Entity List feed seeded in `backend/data/bis_entity_list.json` (envelope with `snapshot_date`, `snapshot_sha256`, `entries`) and integrated into `_check_denied_party()`; checksum verified at startup; >30-day staleness emits `STALE_DENIED_PARTY_DATA` HIGH gap; 30-day refresh routine documented and scheduled
- [ ] DR-CAFTA member country list hardcoded in compliance module
- [ ] `check_compliance()` detects export direction and runs export-specific checks (denied party, CAFTA CoO, dual-use flagging, RET detection)
- [ ] Export gaps properly categorized: `EXPORT_DENIED_PARTY_CONSIGNEE`, `EXPORT_MISSING_COO_CAFTA`, `EXPORT_COO_INELIGIBLE_ORIGIN`, `EXPORT_LICENSE_REQUIRED` (placeholder until KAN-22)
- [ ] Dual-use goods detection runs (non-blocking, informational flagging only)
- [ ] RET indicator inferred and logged
- [ ] Feature flag `EXPORT_COMPLIANCE_ENABLED` implemented and defaults to `false`
- [ ] 8 new test cases pass, covering all five rule categories and direction-agnostic validation
- [ ] Integration test: real US→LATAM invoice upload triggers export compliance checks (with flag on)
- [ ] `/docs/compliance-rules.md` created with export-corridor rule documentation
- [ ] `docs/CLAUDE.md` updated with KAN-21 completion notes
- [ ] All 113 existing tests continue to pass; no regressions in import-side compliance checks
- [ ] Commit history shows 10 atomic, testable commits following `feat(KAN-21):` / `test(KAN-21):` / `docs(KAN-21):` pattern

## Architecture Decision: Single Module vs Separate

**Decision: Extend `services/compliance.py`, do not create separate `services/export_compliance.py`.**

**Rationale:**
- Both import and export compliance are part of the same decision gate: "Is this transaction safe?" The `ComplianceResult` enum and gap reporting are shared.
- Direction detection (`seller_country == "US"`) is a simple conditional; it does not justify a separate module.
- Future phases (Phase 3: "Customs Intelligence") may add automated customs document prep that cuts across both directions; a unified compliance module makes that refactor easier.
- `services/compliance.py` is already 364 lines; adding 200–300 lines of export logic keeps it digestible.
- Tests remain in `test_compliance.py`; no new test file needed.

**Caveat:** If export rules grow to rival or exceed import rules in complexity (e.g., Brazil SISCOMEX, Argentina AFIP requirements in Phase 5+), revisit and split into `services/export_compliance.py` and `services/import_compliance.py`.

---

**Plan Status:** Ready for backend-builder review and work assignment.
**Expected duration:** 3–5 working days for steps 1–9 (pending clarifications on interview-dependent rule thresholds from KAN-22).
**Blocking dependency:** KAN-22 customer interviews (rule validation, ECCN priorities, OFAC scope).
