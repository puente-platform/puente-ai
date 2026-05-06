# backend/app/services/document_ai.py
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.api_core import exceptions as gcp_exceptions
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def get_document_ai_client():
    location = os.getenv("VERTEX_AI_LOCATION", "us")
    opts = ClientOptions(
        api_endpoint=f"{location}-documentai.googleapis.com"
    )
    return documentai.DocumentProcessorServiceClient(
        client_options=opts
    )


def extract_invoice_data(gcs_uri: str) -> dict:
    """
    Extract structured data from an invoice PDF stored in GCS.
    Uses Document AI prebuilt invoice processor.

    Args:
        gcs_uri: GCS path like gs://puente-documents-dev/invoices/...

    Returns:
        Structured dict with extracted invoice fields

    Raises:
        ValueError: if processor ID not configured
        RuntimeError: if Document AI call fails
    """
    client = None

    try:
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("VERTEX_AI_LOCATION", "us")
        processor_id = os.getenv("DOCUMENT_AI_PROCESSOR_ID")

        if not processor_id:
            raise ValueError(
                "DOCUMENT_AI_PROCESSOR_ID not set. "
                "Create a processor in GCP Console first."
            )

        if not project_id:
            raise ValueError(
                "GCP_PROJECT_ID environment variable not set."
            )

        client = get_document_ai_client()
        name = client.processor_path(project_id, location, processor_id)

        gcs_document = documentai.GcsDocument(
            gcs_uri=gcs_uri,
            mime_type="application/pdf"
        )

        request = documentai.ProcessRequest(
            name=name,
            gcs_document=gcs_document
        )

        logger.info(f"Sending document to Document AI: {gcs_uri}")
        result = client.process_document(request=request)
        document = result.document
        logger.info(f"Document AI processing complete for: {gcs_uri}")

        extracted = {
            "document_id": None,
            "document_type": "commercial_invoice",
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "raw_text": document.text[:4000] if document.text else None,
            "fields": {}
        }

        # Entity types emitted by Document AI prebuilt Invoice Parser v2
        # (pretrained-invoice-v2.0-*). The v2 processor uses snake_case
        # entity types; v1 used PascalCase. Keys below MUST match the
        # current processor version's `entity.type_` strings exactly.
        #
        # Processor-version drift detection below compares every
        # observed top-level entity type against `field_mapping ∪
        # _ignored_entity_types` and warns on anything unknown — so a
        # single renamed key (e.g. `total_amount` → `totalAmount`) is
        # caught even when other fields still map, not just the
        # catastrophic all-fields-missing case.
        #
        # Incoterms, country_of_origin and hs_code are NOT emitted by
        # the invoice parser and are intentionally not populated here.
        # If the pipeline ever needs them, Gemini (or a dedicated
        # processor) would have to infer them from `raw_text` +
        # `line_items`; note that `raw_text` is currently stored on
        # the extraction record but not fed into Gemini's prompt, so
        # this inference is aspirational — do not assume these keys
        # will appear downstream without wiring that path first.
        field_mapping = {
            # Core invoice identity
            "invoice_id": "invoice_id",
            "invoice_date": "invoice_date",
            "due_date": "due_date",

            # Financial
            "total_amount": "invoice_amount",
            "net_amount": "net_amount",
            "total_tax_amount": "tax_amount",
            "currency": "currency",
            "freight_amount": "freight_charge",

            # Parties — using trade terminology internally
            "supplier_name": "exporter_name",
            "supplier_address": "exporter_address",
            "supplier_email": "exporter_email",
            "supplier_phone": "exporter_phone",
            "supplier_tax_id": "exporter_tax_id",
            "receiver_name": "importer_name",
            "receiver_address": "importer_address",
            "receiver_email": "importer_email",
            "receiver_tax_id": "importer_tax_id",
            "ship_to_name": "shipping_recipient",
            "ship_to_address": "shipping_address",

            # Commercial terms
            "purchase_order": "purchase_order",
            "payment_terms": "payment_terms",

            # BEC fraud signals — surfacable for downstream consumers.
            # Phase 2 dashboard uses these for remit-to vs. supplier
            # mismatch detection and IBAN substitution flagging.
            # DO NOT move to _ignored_entity_types without explicit
            # approval — see spec §11 (docs/superpowers/specs/
            # 2026-05-05-analyze-dashboard-phase-1-design.md) and KAN-46.
            "remit_to_name": "remit_to_name",   # third-party remit-to (BEC mismatch signal)
            "supplier_iban": "supplier_iban",   # settlement IBAN (BEC substitution signal)

            # Shipment + supplier metadata (KAN-48 diagnostic on
            # DISTRIBUIDORA ANDINA $91K invoice showed Document AI
            # emits these top-level entities; previously dropped on
            # the floor as "unknown").
            "carrier": "carrier",                       # e.g. "Ocean Freight (FCL 20')" — feeds shipment-mode inference for ISF
            "supplier_website": "supplier_website",     # e.g. "www.distribuidoraandina.co"
        }

        # Entity types the v2 processor is known to emit but that we
        # intentionally discard (no downstream consumer). Listing them
        # here keeps the drift warning below quiet for expected noise
        # while still firing on genuinely-new types. If a value below
        # ever gains a consumer, move it into `field_mapping` instead
        # of leaving it here.
        _ignored_entity_types = {
            "line_item",       # extracted via the separate loop below
            "invoice_type",    # processor emits it; no consumer today
        }

        # TODO Phase 3 — requires separate processors:
        # Bill of Lading  → bill_of_lading_number,
        #                    container_number,
        #                    port_of_loading,
        #                    port_of_discharge,
        #                    carrier_name
        # Packing List    → weights, dimensions,
        #                    package_count
        # Customs Decl.   → customs_declaration_number,
        #                    duty_amount, customs_value
        # Cert of Origin  → treaty benefits
        #                    (DR-CAFTA, EU-EPA)

        # Extract top-level fields keeps highest confidence when duplicates exist:

        top_level_entity_types: set[str] = set()
        for entity in document.entities:
            top_level_entity_types.add(entity.type_)
            field_key = field_mapping.get(entity.type_)
            if field_key:
                existing = extracted["fields"].get(field_key)
                new_confidence = round(entity.confidence, 3)
                if existing is None or new_confidence > existing["confidence"]:
                    extracted["fields"][field_key] = {
                        "value": entity.mention_text,
                        "confidence": new_confidence
                    }

        # Processor-version drift detection. We warn on ANY top-level
        # entity type that is neither in `field_mapping` nor in the
        # explicit ignore set. This catches partial drift — e.g. if a
        # future processor version renames `total_amount` → `totalAmount`
        # while leaving other keys intact, the old all-fields-missing
        # signal would stay silent because 14 fields still map, but
        # downstream routing would 422 on the missing invoice_amount.
        # Surfacing unknown types as soon as they appear gives us one
        # log-read to diagnose, instead of an outage.
        known_entity_types = (
            set(field_mapping.keys()) | _ignored_entity_types
        )
        unknown_entity_types = top_level_entity_types - known_entity_types
        if unknown_entity_types:
            logger.warning(
                "Document AI returned %d unknown top-level entity "
                "type(s) for %s. Possible processor-version drift — "
                "update field_mapping or _ignored_entity_types in "
                "document_ai.py. Unknown types: %s",
                len(unknown_entity_types),
                gcs_uri,
                sorted(unknown_entity_types),
            )

        # Extract line items — enhanced for trade compliance
        line_items = []
        for entity in document.entities:
            if entity.type_ == "line_item":
                item = {}
                for prop in entity.properties:
                    if prop.type_ == "line_item/description":
                        item["description"] = prop.mention_text
                    elif prop.type_ == "line_item/quantity":
                        item["quantity"] = prop.mention_text
                    elif prop.type_ == "line_item/unit":
                        item["unit_of_measure"] = prop.mention_text
                    elif prop.type_ == "line_item/unit_price":
                        item["unit_price"] = prop.mention_text
                    elif prop.type_ == "line_item/amount":
                        item["amount"] = prop.mention_text
                    elif prop.type_ == "line_item/product_code":
                        item["hs_code_candidate"] = prop.mention_text
                    elif prop.type_ == "line_item/purchase_order":
                        item["po_reference"] = prop.mention_text
                if item:
                    # Flag items without HS codes for
                    # Gemini to classify automatically
                    item["needs_hs_classification"] = (
                        "hs_code_candidate" not in item
                    )
                    line_items.append(item)

        extracted["line_items"] = line_items
        extracted["line_item_count"] = len(line_items)

        # Summary flags for downstream analysis. `has_hs_code` reflects
        # per-line `line_item/product_code` presence rather than the
        # never-emitted top-level `hs_code` entity (KAN-48): the prebuilt
        # Invoice Parser only ever surfaces HS codes inside line items,
        # so the old top-level check was always False and produced a
        # spurious "HS Codes not provided" compliance flag for invoices
        # that *did* carry HS codes.
        extracted["extraction_summary"] = {
            "has_incoterms": "incoterms" in extracted["fields"],
            "has_hs_code": any(
                "hs_code_candidate" in item for item in line_items
            ),
            "has_country_of_origin": (
                "country_of_origin" in extracted["fields"]
            ),
            "items_needing_hs_classification": sum(
                1 for item in line_items
                if item.get("needs_hs_classification")
            )
        }

        return extracted

    except ValueError:
        raise

    except gcp_exceptions.PermissionDenied as e:
        logger.error(
            f"Document AI permission denied for {gcs_uri}: {e}"
        )
        raise RuntimeError(
            "Document AI permission denied. "
            "Check service account roles."
        ) from e

    except gcp_exceptions.NotFound as e:
        logger.error(f"Document AI processor not found: {e}")
        raise RuntimeError(
            "Document AI processor not found. "
            "Verify DOCUMENT_AI_PROCESSOR_ID is correct."
        ) from e

    except gcp_exceptions.ResourceExhausted as e:
        logger.error(f"Document AI quota exceeded: {e}")
        raise RuntimeError(
            "Document AI quota exceeded. "
            "Try again in a few minutes."
        ) from e

    except gcp_exceptions.DeadlineExceeded as e:
        logger.error(f"Document AI timeout for {gcs_uri}: {e}")
        raise RuntimeError(
            "Document AI request timed out. "
            "Document may be too large or complex."
        ) from e

    except Exception as e:
        logger.error(
            f"Unexpected Document AI error for {gcs_uri}: "
            f"{type(e).__name__}: {e}",
            exc_info=True,
        )
        raise RuntimeError(
            "Document AI processing failed due to an unexpected error."
        ) from e

    finally:
        logger.info(
            f"Document AI extraction attempt completed for: {gcs_uri}"
        )
