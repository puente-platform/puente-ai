# backend/app/routes/routing.py
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.services.firestore import get_transaction, save_routing_result
from app.services.payment_routing import recommend_payment_route

logger = logging.getLogger(__name__)
router = APIRouter()


class RoutingRequest(BaseModel):
    document_id: str


def _extract_field_value(fields: dict, *keys: str):
    """Try multiple field name variants, return first match."""
    for key in keys:
        field = fields.get(key)
        if field is None:
            continue
        if isinstance(field, dict):
            value = field.get("value")
        else:
            value = field
        if value is not None:
            return value
    return None


@router.post("/routing")
async def get_routing_recommendation(request: RoutingRequest):
    """
    Generate a payment routing recommendation for a processed document.

    Status flow:
        uploaded -> extracted -> analyzed -> compliance_checked -> routed

    Prerequisites:
        - Primary: document must have been analyzed (status "analyzed").
        - This endpoint also accepts documents with status "compliance_checked"
          or "routed" to allow routing after compliance checks and to support
          rerunning routing on already-routed documents.

    Run POST /api/v1/analyze first (and any required compliance checks) before
    requesting routing.
    """
    # Step 1 — verify document exists
    transaction = await get_transaction(request.document_id)
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail=f"Document {request.document_id} not found."
        )

    # Step 2 — verify document has been analyzed
    current_status = transaction.get("status")
    if current_status not in ("analyzed", "compliance_checked", "routed"):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Document status is '{current_status}'. "
                "Document must be analyzed before routing. "
                "Run POST /api/v1/analyze first."
            )
        )

    # Step 3 — extract routing inputs from stored extraction
    extraction = transaction.get("extraction", {})
    fields = extraction.get("fields", {}) if isinstance(
        extraction, dict) else {}

    routing_input = {
        "amount": _extract_field_value(
            fields, "invoice_amount", "InvoiceTotal", "amount"
        ),
        "currency": _extract_field_value(
            fields, "currency", "CurrencyCode"
        ) or "USD",
        "buyer_country": _extract_field_value(
            fields, "buyer_country"
        ) or "US",
        "seller_country": _extract_field_value(
            fields, "seller_country"
        ),
    }

    logger.info(
        "Routing request for document %s: corridor=%s->%s amount=%s",
        request.document_id,
        routing_input.get("buyer_country"),
        routing_input.get("seller_country"),
        routing_input.get("amount"),
    )

    # Step 4 — run routing engine in threadpool
    # recommend_payment_route is synchronous CPU work —
    # run_in_threadpool prevents blocking the async event loop
    try:
        result = await run_in_threadpool(
            recommend_payment_route, routing_input
        )
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not generate routing recommendation: {str(e)}"
        )

    # Step 5 — persist result to Firestore
    routing_saved = True
    try:
        await save_routing_result(request.document_id, result.to_dict())
    except Exception as e:
        routing_saved = False
        logger.error(
            "Failed to persist routing result for %s: %s",
            request.document_id,
            e,
        )

    return {
        "document_id": request.document_id,
        "status": "routed",
        "routing_saved": routing_saved,
        "routing": result.to_dict(),
    }
