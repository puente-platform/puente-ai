# backend/app/routes/analyze.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.document_ai import extract_invoice_data
from app.services.firestore import (
    get_transaction,
    update_transaction_status,
    save_extraction
)
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    document_id: str


@router.post("/analyze")
async def analyze_document(request: AnalyzeRequest):
    """
    Analyze an uploaded document using Document AI.
    Extracts invoice fields and updates Firestore record.

    Status flow:
    uploaded → processing → extracted → (future) analyzed
    """
    try:
        # Step 1 — verify document exists in Firestore
        transaction = await get_transaction(request.document_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Document {request.document_id} not found"
            )

        # Step 2 — idempotency check
        current_status = transaction.get("status")
        if current_status == "extracted":
            return {
                "document_id": request.document_id,
                "status": "already_extracted",
                "message": "Document was already extracted. "
                           "Submit a new document to re-analyze.",
                "extraction": transaction.get("extraction")
            }

        if current_status == "processing":
            return {
                "document_id": request.document_id,
                "status": "processing",
                "message": "Document is currently being processed. "
                           "Try again in a few seconds."
            }

        # Step 3 — validate ALL config before setting processing
        # Fix: validate everything upfront so a config error
        # never leaves status stuck on "processing"
        bucket = os.getenv("GCS_BUCKET_NAME")
        blob_name = transaction.get("blob_name")
        processor_id = os.getenv("DOCUMENT_AI_PROCESSOR_ID")
        project_id = os.getenv("GCP_PROJECT_ID")

        if not bucket:
            raise ValueError(
                "GCS_BUCKET_NAME environment variable not set."
            )
        if not blob_name:
            raise ValueError(
                f"No blob_name found for document "
                f"{request.document_id}. "
                "The file may not have uploaded correctly."
            )
        if not processor_id:
            raise ValueError(
                "DOCUMENT_AI_PROCESSOR_ID not set. "
                "Create a processor in GCP Console first."
            )
        if not project_id:
            raise ValueError(
                "GCP_PROJECT_ID environment variable not set."
            )

        gcs_uri = f"gs://{bucket}/{blob_name}"

        # Step 4 — only set processing AFTER all validation passes
        await update_transaction_status(
            request.document_id,
            "processing"
        )

        logger.info(
            f"Starting Document AI analysis for: "
            f"{request.document_id}"
        )

        # Step 5 — call Document AI
        extraction = extract_invoice_data(gcs_uri)
        extraction["document_id"] = request.document_id

        # Step 6 — save extraction via centralized service
        await save_extraction(request.document_id, extraction)

        logger.info(
            f"Document AI extraction complete for: "
            f"{request.document_id}"
        )

        return {
            "document_id": request.document_id,
            "status": "extracted",
            "message": "Invoice data extracted successfully",
            "extraction": extraction
        }

    except HTTPException:
        raise

    except ValueError as e:
        # Configuration errors — never set processing before
        # these checks so status is never left stuck
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Server configuration error: {str(e)}"
        )

    except RuntimeError as e:
        # Document AI upstream failures → 502 Bad Gateway
        logger.error(
            f"Document AI error for {request.document_id}: {e}"
        )
        await update_transaction_status(
            request.document_id,
            "failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=502,
            detail=str(e)
        )

    except Exception as e:
        logger.error(
            f"Unexpected error analyzing "
            f"{request.document_id}: {e}"
        )
        await update_transaction_status(
            request.document_id,
            "failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Analysis failed due to an internal server error."
        )
