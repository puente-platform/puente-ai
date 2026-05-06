# backend/app/routes/routing.py
import logging
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.services.auth import get_current_user
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


def _is_blank(v: object) -> bool:
    """Return True if v is None or a whitespace-only string."""
    return v is None or (isinstance(v, str) and v.strip() == "")


@router.post("/routing")
async def create_routing_recommendation(
    request: RoutingRequest,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
):
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

    Required-field contract (extraction fields read from Firestore):
        Required:
            amount         — invoice amount (from field key "invoice_amount" or
                             legacy "InvoiceTotal"/"amount"). None, empty
                             string, or whitespace-only raises 422 with
                             {"missing_fields": ["amount"]} BEFORE the routing
                             engine is called.

        Defaulted:
            currency       — defaults to "USD" when absent or unparseable.
                             Silent fallback, no warning logged.
            buyer_country  — ISO-3166 alpha-2 buyer country; defaults to "US"
                             when absent or not a valid 2-char ISO code.
                             Logged as WARNING.
            seller_country — ISO-3166 alpha-2 seller country; defaults to "US"
                             with the same warning behaviour.

    The routing engine (_normalize_extraction in payment_routing.py) applies
    the defaults for country codes so routing still returns a result for
    documents where Document AI did not emit those fields. A missing/blank
    amount is the only extraction-level hard failure.
    """
    user_id: str = current_user["uid"]

    # Step 1 — verify document exists
    transaction = await get_transaction(request.document_id, user_id=user_id)
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

    # Step 3b — preflight: amount is the only hard-required extraction field.
    # Treats None, "", and whitespace-only strings as missing (per _is_blank)
    # so a blank Firestore value bypasses neither the preflight nor the
    # ValueError catch in the threadpool. Produces a structured 422 with a
    # machine-readable missing_fields list — more actionable than the generic
    # "Could not generate routing recommendation: Transaction amount is required"
    # that would otherwise bubble up from _normalize_extraction.
    if _is_blank(routing_input["amount"]):
        logger.warning(
            "Routing preflight failed for %s: amount is missing or blank",
            request.document_id,
        )
        raise HTTPException(
            status_code=422,
            detail={
                "missing_fields": ["amount"],
                "message": (
                    "Required field 'amount' is missing or blank in the "
                    "document extraction. Re-run POST /api/v1/analyze or "
                    "supply the amount manually."
                ),
            },
        )

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
        logger.warning(
            "Routing recommendation failed for %s: %s",
            request.document_id,
            e,
        )
        raise HTTPException(
            status_code=422,
            detail=f"Could not generate routing recommendation: {str(e)}"
        )

    # Step 5 — persist result to Firestore
    routing_dict = result.to_dict()

    # Normalize total_savings_usd once so the API response echoes the
    # same string that Firestore stores (Money Math: all authoritative
    # money values are normalized Decimal strings; raw Decimal in the
    # response would diverge from the persisted form).
    raw_savings = routing_dict.get("total_savings_usd")
    if raw_savings is None:
        routing_dict["total_savings_usd"] = "0.00"
    else:
        try:
            routing_dict["total_savings_usd"] = str(
                Decimal(str(raw_savings)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Could not normalize total_savings_usd: "
                    f"{exc}"
                ),
            )

    routing_saved = True
    try:
        await save_routing_result(request.document_id, routing_dict, user_id=user_id)
    except Exception as e:
        routing_saved = False
        logger.error(
            "Failed to persist routing result for %s: %s",
            request.document_id,
            e,
            exc_info=True,
        )

    return {
        "document_id": request.document_id,
        "status": "routed",
        "routing_saved": routing_saved,
        "routing": routing_dict,
    }
