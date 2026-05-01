# KAN ticket draft — Document AI extraction-upgrade

**Title:** Document AI extraction-upgrade — extract seller_country + plumb to routing engine

**Type:** Story
**Priority:** High (most production invoices currently get $0 routing recommendations because of this gap)
**Labels:** backend, extraction, gemini, document-ai

---

## Bug

Real production invoice ($60,462 from Exportaciones Andinas S.A.S., founder upload 2026-04-30) returned "$0 You save" because the routing engine received `seller_country=None` and fell to `_DEFAULT_CORRIDOR`, which has no real savings model.

PR #55 ([merged 2026-05-01 a3aa80f](https://github.com/puente-platform/puente-ai/commit/a3aa80f)) ships a frontend band-aid that displays "Routing data unavailable" instead of the misleading $0 + RECOMMENDED card, but the underlying extraction gap remains: most invoices currently can't get a routing recommendation.

## Root cause

`backend/app/routes/routing.py:91-96` reads `extraction.fields.seller_country`, but Document AI's prebuilt Invoice Parser (processor `2d45b8ceac15def2`, region `us`) does NOT extract a `seller_country` field. It extracts entities like `vendor_address`, `supplier_address`, etc. The `field_mapping` dict in `services/document_ai.py` doesn't translate either of those into a 2-letter ISO country code. Gemini's analysis pass also doesn't write a `seller_country` back into `extraction.fields`.

Net: every real invoice currently hits the `_DEFAULT_CORRIDOR` branch and returns 0 savings.

## Fix (in order — diagnostic-first)

### Task 1 — Diagnostic (15 min, no code)

`scripts/debug_extraction.py` (throwaway, do NOT commit):

- Upload a real commercial invoice PDF (use one of the Exportaciones Andinas / Doral interview test invoices — NOT a synthetic generated one; the synthetic generator misses real-world entity diversity)
- Process via `documentai_v1.DocumentProcessorServiceClient.process_document`
- Print every entity type + mention_text + confidence
- Print first 2000 chars of `doc.text` (the raw_text Gemini receives)
- Save full output to a Jira comment for evidence

**The output answers:**
- Which fields ARE we already extracting that we're ignoring?
- Which fields are NOT extracted but appear in raw_text?

### Task 2 — Expand `field_mapping` (30 min)

Based on diagnostic output, expand `field_mapping` in `services/document_ai.py` to include the entity types that actually appear. Likely candidates (verify exact names from Task 1 — DO NOT guess):

- `VendorAddress` / `SupplierAddress` → `vendor_address` (preserve raw)
- `ShipFromAddress` / `ShipFromName` → `ship_from_*`
- `ShipToAddress` / `ShipToName` → `ship_to_*`
- `VendorTaxId` / `CustomerTaxId` → for sanctions screening
- `DeliveryDate` → for SLA modeling

### Task 3 — Gemini reasons `seller_country` from raw_text (45 min)

`services/gemini.py` analysis prompt currently asks for fraud + compliance + routing assessments. Add explicit ask:

> Identify the seller's country of origin as a 2-letter ISO 3166-1 alpha-2 code (e.g., "CO" for Colombia, "MX" for Mexico). Look at: the supplier/vendor address, explicit "country of origin" mentions, port of loading/dispatch, currency code patterns. If multiple candidates conflict, pick highest-confidence and note the alternates. Format:
>
> ```json
> { "seller_country": "CO", "confidence": "high|medium|low", "evidence": "<one-line excerpt from raw_text>" }
> ```

Plumb the response back into `extraction.fields.seller_country` (write to Firestore alongside the Document AI fields) so `backend/app/routes/routing.py` can read it.

### Task 4 — Extraction quality summary (20 min)

Add `extraction.extraction_quality` summary block:

- `coverage_pct`: fraction of `field_mapping` keys actually present
- `line_items_found`: count
- `low_confidence_fields`: list of fields where `confidence < 0.5`
- `missing_critical`: which of `[vendor_name, buyer_name, invoice_amount, currency, seller_country]` are absent
- `gemini_inferred_fields`: which fields came from Gemini reasoning vs Document AI extraction (provenance for trust)

Surfaces on the frontend per the planned `ResultsView` expansion (drafted in chat 2026-04-30, will land as a follow-up frontend ticket).

## NOT in scope (separate tickets)

- WhatsApp Business API webhook scaffold
- Custom Document Extractor (CDE) processor — premature optimization
- Banking detail extraction (BEC fraud + money transmission risk)
- HS code classification beyond what Gemini already produces
- Frontend ResultsView expansion — should wait until this ticket has expanded the field set so the frontend has something to render

## Acceptance criteria

- [ ] Diagnostic output committed to ticket as comment
- [ ] field_mapping `coverage_pct` increases measurably with the same Exportaciones Andinas test invoice (target: >70% of available fields)
- [ ] Gemini analysis returns `seller_country` for the same invoice with confidence=high|medium and evidence excerpt
- [ ] `/api/v1/routing` on the same invoice returns `total_savings_usd > 0` (verifies seller_country plumbing)
- [ ] Frontend AnalyzePage shows a real recommended route + non-zero savings (verifies end-to-end)
- [ ] Cloud Run logs do NOT contain seller name / company in plaintext (PII contract from Security Constraint #6 still holds)
- [ ] Backend regression test: 0 existing tests broken; new test for `seller_country` extraction on a fixture invoice

## Depends on

- A real test invoice from a Doral interview (Founder execution prereq)
- PR #55 merged ✓ (frontend "data unavailable" band-aid removes urgency pressure)

## Owner

`backend-builder` agent (route + service changes), with primary agent or `frontend-engineer` agent doing the small frontend follow-up to render the new fields.

## Engineering brief reference

This ticket implements Tasks 1–4 from the founder's 2026-04-30 engineering brief titled "Puente AI — Engineering Brief for Cursor Session." Task 5 from that brief (WhatsApp scaffold) is intentionally split into a separate ticket per the diagnostic-first discipline established here.
