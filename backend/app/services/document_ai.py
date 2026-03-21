# backend/app/services/document_ai.py
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.api_core import exceptions as gcp_exceptions
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def get_document_ai_client():
    location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
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
        location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
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
            "raw_text": document.text[:500] if document.text else None,
            "fields": {}
        }

        # Fields confirmed supported by Document AI
        # prebuilt invoice processor
        field_mapping = {
            # Core invoice identity
            "InvoiceId": "invoice_id",
            "InvoiceDate": "invoice_date",
            "DueDate": "due_date",

            # Financial
            "InvoiceTotal": "invoice_amount",
            "TotalTaxAmount": "tax_amount",
            "CurrencyCode": "currency",
            "FreightAmount": "freight_charge",

            # Parties — using trade terminology
            "VendorName": "exporter_name",
            "VendorAddress": "exporter_address",
            "CustomerName": "importer_name",
            "CustomerAddress": "importer_address",
            "ShipToName": "shipping_recipient",
            "ShipToAddress": "shipping_address",

            # Commercial terms
            "PurchaseOrder": "purchase_order",
            "PaymentTerms": "payment_terms",
            "Incoterms": "incoterms",

            # Tax identifiers
            "SupplierTaxId": "exporter_tax_id",
            "CustomerTaxId": "importer_tax_id",

            # Compliance — extracted if present on invoice
            "CountryOfOrigin": "country_of_origin",
            "HSCode": "hs_code",
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

        for entity in document.entities:
            field_key = field_mapping.get(entity.type_)
            if field_key:
                existing = extracted["fields"].get(field_key)
                new_confidence = round(entity.confidence, 3)
                if existing is None or new_confidence > existing["confidence"]:
                    extracted["fields"][field_key] = {
                        "value": entity.mention_text,
                        "confidence": new_confidence
                    }

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

        # Summary flags for downstream analysis
        extracted["extraction_summary"] = {
            "has_incoterms": "incoterms" in extracted["fields"],
            "has_hs_code": "hs_code" in extracted["fields"],
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
            f"{type(e).__name__}: {e}"
        )
        raise RuntimeError(
            f"Document AI processing failed: {str(e)}"
        ) from e

    finally:
        logger.info(
            f"Document AI extraction attempt completed for: {gcs_uri}"
        )
