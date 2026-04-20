# backend/app/routes/compliance.py
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.auth import get_current_user
from app.services.compliance import check_compliance
from app.services.firestore import (
    get_transaction,
    save_compliance_result,
)

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(get_current_user)])


class ComplianceRequest(BaseModel):
    document_id: str


@router.post("/compliance")
async def run_compliance_check(request: ComplianceRequest):
    """
    Run compliance gap detection on an already-analyzed document.

    Expects the document to exist in Firestore with an extraction field.
    Returns compliance_level (LOW/MEDIUM/HIGH) and missing_documents.
    """
    # Step 1 — fetch the document from Firestore
    transaction = await get_transaction(request.document_id)
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail=f"Document {request.document_id} not found",
        )

    # Step 2 — idempotent short-circuit: don't re-run compliance or downgrade
    # the status if the doc has already progressed past this stage AND
    # actually has a stored compliance payload. Docs that reached "routed"
    # without ever calling /compliance (a legal pipeline path — /routing
    # accepts status="analyzed") must still be allowed to run compliance.
    current_status = transaction.get("status")
    stored_compliance = transaction.get("compliance")
    if (
        current_status in ("compliance_checked", "routed")
        and isinstance(stored_compliance, dict)
        and stored_compliance
    ):
        return {
            "document_id": request.document_id,
            "status": "already_checked",
            "message": "Compliance check already completed.",
            **stored_compliance,
        }

    # Step 3 — make sure we have extraction data to work with
    extraction = transaction.get("extraction")
    if not isinstance(extraction, dict) or not extraction:
        raise HTTPException(
            status_code=422,
            detail=(
                "Document has not been extracted yet. "
                "Call /analyze first."
            ),
        )

    # Step 4 — run the compliance checker (pure Python, no I/O)
    try:
        result = check_compliance(extraction)
    except Exception as e:
        logger.error(
            "Compliance check failed for %s: %s",
            request.document_id,
            e,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Compliance check failed due to an internal error.",
        )

    compliance_dict = result.to_dict()
    try:
        # Step 5 — persist compliance-specific fields only
        await save_compliance_result(
            request.document_id,
            compliance_dict,
        )
    except Exception as e:
        logger.error(
            "Compliance persistence failed for %s: %s",
            request.document_id,
            e,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Compliance result could not be saved.",
        )

    logger.info(
        "Compliance complete for %s: level=%s gaps=%d",
        request.document_id,
        result.compliance_level.value,
        len(result.missing_documents),
    )

    return {
        "document_id": request.document_id,
        "status": "compliance_checked",
        **compliance_dict,
    }
