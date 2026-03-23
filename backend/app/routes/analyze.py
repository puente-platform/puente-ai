# backend/app/routes/analyze.py
import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.services.document_ai import extract_invoice_data
from app.services.firestore import (
    get_transaction,
    save_analysis,
    save_extraction,
    update_transaction_status,
)
from app.services.gemini import analyze_trade_document

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    document_id: str


def _validate_extraction_inputs(transaction: dict[str, Any]) -> str:
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
            "No blob_name found for document. "
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

    return f"gs://{bucket}/{blob_name}"


def _get_saved_extraction(
    transaction: dict[str, Any]
) -> dict[str, Any] | None:
    extraction = transaction.get("extraction")
    if isinstance(extraction, dict) and extraction:
        return extraction
    return None


@router.post("/analyze")
async def analyze_document(request: AnalyzeRequest):
    """
    Analyze an uploaded document using Document AI then Gemini.

    Status flow:
        uploaded -> processing -> extracted -> analyzed
    """
    try:
        # Step 1 - verify document exists in Firestore
        transaction = await get_transaction(request.document_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Document {request.document_id} not found"
            )

        # Step 2 - idempotency check
        current_status = transaction.get("status")
        if current_status == "analyzed":
            return {
                "document_id": request.document_id,
                "status": "already_analyzed",
                "message": "Document was already analyzed. "
                "Submit a new document to re-analyze.",
                "extraction": transaction.get("extraction"),
                "analysis": transaction.get("full_analysis")
            }

        if current_status == "processing":
            return {
                "document_id": request.document_id,
                "status": "processing",
                "message": "Document is currently being processed. "
                "Try again in a few seconds."
            }

        extraction = _get_saved_extraction(transaction)
        if extraction:
            logger.info(
                "Reusing saved extraction for document: %s",
                request.document_id,
            )
            extraction = dict(extraction)
            extraction["document_id"] = request.document_id
        else:
            gcs_uri = _validate_extraction_inputs(transaction)

            # Step 3 - set status to processing after validation
            await update_transaction_status(
                request.document_id,
                "processing"
            )

            logger.info(
                "Starting Document AI extraction for: %s",
                request.document_id,
            )
            extraction = await run_in_threadpool(
                extract_invoice_data,
                gcs_uri,
            )
            extraction["document_id"] = request.document_id

            # Step 5 - save extraction to Firestore
            await save_extraction(request.document_id, extraction)
            logger.info(
                "Document AI extraction complete for: %s",
                request.document_id,
            )

        # Step 6 - run Gemini analysis on extracted data
        logger.info(
            "Starting Gemini analysis for: %s",
            request.document_id,
        )
        analysis = await run_in_threadpool(
            analyze_trade_document,
            extraction,
        )

        # Step 7 - save analysis to Firestore
        await save_analysis(request.document_id, analysis)
        logger.info(
            "Gemini analysis complete for: %s",
            request.document_id,
        )

        return {
            "document_id": request.document_id,
            "status": "analyzed",
            "message": "Invoice analyzed successfully",
            "extraction": extraction,
            "analysis": analysis
        }

    except HTTPException:
        raise

    except ValueError as e:
        # Fix: ValueError from analyze_trade_document (malformed extraction
        # fields) previously returned HTTP 500 without updating status,
        # leaving the document stuck in "processing". Now always sets "failed".
        logger.error(
            "Configuration or validation error for %s: %s",
            request.document_id,
            e,
        )
        await update_transaction_status(
            request.document_id,
            "failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Server configuration error."
        )

    except RuntimeError as e:
        logger.error(
            "Analysis error for %s: %s",
            request.document_id,
            e,
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
            "Unexpected error analyzing %s: %s",
            request.document_id,
            e,
            exc_info=True,
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
