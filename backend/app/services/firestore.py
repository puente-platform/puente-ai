import asyncio
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from threading import Lock
from typing import Any

from google.cloud import firestore

logger = logging.getLogger(__name__)

# Module-level singleton — created once, reused across requests
_db: firestore.Client | None = None
_db_lock = Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_document_ref(
    user_id: str,
    document_id: str,
) -> firestore.DocumentReference:
    """
    Return a DocumentReference scoped to the authenticated user's subcollection.

    Path: transactions/{user_id}/docs/{document_id}

    Enforces tenant isolation by path structure — it is impossible to accidentally
    access another user's document without explicitly supplying their user_id.
    """
    if not user_id:
        raise ValueError("user_id is required.")
    if not document_id:
        raise ValueError("document_id is required.")
    return (
        get_firestore_client()
        .collection("transactions")
        .document(user_id)
        .collection("docs")
        .document(document_id)
    )


def get_firestore_client() -> firestore.Client:
    global _db

    if _db is not None:
        return _db

    with _db_lock:
        if _db is not None:
            return _db

        project = os.getenv("GCP_PROJECT_ID")
        if not project:
            raise ValueError(
                "GCP_PROJECT_ID environment variable not set."
            )
        _db = firestore.Client(project=project)
        logger.info("Firestore client initialized.")
    return _db


async def create_transaction_record(
    document_id: str,
    filename: str,
    blob_name: str,
    file_size: int,
    *,
    user_id: str,
) -> dict:

    if file_size < 0:
        raise ValueError("file_size must be non-negative.")

    now = _utc_now_iso()

    transaction_data = {
        "document_id": document_id,
        "user_id": user_id,
        "filename": filename,
        "blob_name": blob_name,
        "file_size_bytes": file_size,
        "status": "uploaded",
        "uploaded_at": now,
        "updated_at": now,
        "analysis": {
            "fraud_score": None,
            "fraud_flags": None,
            "compliance_level": None,
            "missing_documents": None,
            "routing_recommendation": None,
            "summary": None
        },
        "extraction": None,
        "extracted_at": None,
        "analyzed_at": None,
        "error": None
    }

    await asyncio.to_thread(
        _get_document_ref(user_id, document_id).set,
        transaction_data
    )
    return transaction_data


async def get_transaction(
    document_id: str,
    *,
    user_id: str,
) -> dict | None:
    doc = await asyncio.to_thread(
        _get_document_ref(user_id, document_id).get
    )

    if doc.exists:
        return doc.to_dict()
    return None


async def update_transaction_status(
    document_id: str,
    status: str,
    *,
    error: str | None = None,
    user_id: str,
) -> None:
    now = _utc_now_iso()

    update_data = {
        "status": status,
        "updated_at": now
    }

    if error:
        update_data["error"] = error
    else:
        # Fix: explicitly clear error on non-failure status
        # so a retried document doesn't show stale error
        update_data["error"] = None

    # Note: merge=True is intentional here — status updates
    # should succeed even in recovery flows.
    # Important: _get_document_ref() raises ValueError on a falsy
    # document_id. Callers (including failure/recovery paths) must
    # ensure document_id is valid before calling this function.
    await asyncio.to_thread(
        _get_document_ref(user_id, document_id).set,
        update_data,
        merge=True
    )


async def save_extraction(
    document_id: str,
    extraction: dict[str, Any],
    *,
    user_id: str,
) -> None:
    """
    Centralized extraction save.
    Clears any previous error field on success.
    Sets updated_at for consistent last-touch tracking.
    """
    if not isinstance(extraction, dict):
        raise ValueError("extraction must be a dictionary.")

    now = _utc_now_iso()

    await asyncio.to_thread(
        _get_document_ref(user_id, document_id).set,
        {
            "status": "extracted",
            "extraction": extraction,
            "extracted_at": extraction.get("extracted_at") or now,
            "updated_at": now,
            "error": None  # Fix: clear stale errors on success
        },
        merge=True
    )
    logger.info("Extraction saved for document: %s", document_id)


async def save_analysis(
    document_id: str,
    analysis: dict[str, Any],
    *,
    user_id: str,
) -> None:
    """
    Save Gemini analysis results to Firestore.
    Updates the analysis fields and marks document as analyzed.
    """
    if not isinstance(analysis, dict):
        raise ValueError("analysis must be a dictionary.")

    now = _utc_now_iso()
    fraud_assessment = analysis.get("fraud_assessment")
    compliance_assessment = analysis.get("compliance_assessment")
    routing_recommendation = analysis.get("routing_recommendation")

    if not isinstance(fraud_assessment, dict):
        fraud_assessment = {}
    if not isinstance(compliance_assessment, dict):
        compliance_assessment = {}
    if not isinstance(routing_recommendation, dict):
        routing_recommendation = {}

    await asyncio.to_thread(
        _get_document_ref(user_id, document_id).set,
        {
            "status": "analyzed",
            "analysis": {
                "fraud_score": fraud_assessment.get("score"),
                "fraud_flags": fraud_assessment.get("flags"),
                "compliance_level": compliance_assessment.get("level"),
                "missing_documents": compliance_assessment.get(
                    "missing_documents"
                ),
                "routing_recommendation": routing_recommendation.get(
                    "recommended_method"
                ),
                "summary": fraud_assessment.get("explanation"),
            },
            "full_analysis": analysis,
            "analyzed_at": analysis.get(
                "analyzed_at"
            ) or now,
            "updated_at": now,
            "error": None
        },
        merge=True
    )
    logger.info("Analysis saved for document: %s", document_id)


async def save_compliance_result(
    document_id: str,
    compliance: dict[str, Any],
    *,
    user_id: str,
) -> None:
    """
    Save rule-based compliance output without mutating full_analysis.

    This endpoint is used by /compliance and should only update:
    - top-level compliance payload
    - flattened analysis compliance summary fields
    """
    if not isinstance(compliance, dict):
        raise ValueError("compliance must be a dictionary.")

    now = _utc_now_iso()

    await asyncio.to_thread(
        _get_document_ref(user_id, document_id).set,
        {
            "status": "compliance_checked",
            "compliance": compliance,
            "analysis": {
                "compliance_level": compliance.get("compliance_level"),
                "missing_documents": compliance.get("missing_documents"),
            },
            "compliance_checked_at": now,
            "updated_at": now,
            "error": None,
        },
        merge=True,
    )
    logger.info("Compliance saved for document: %s", document_id)


async def save_analysis_snapshot(
    document_id: str,
    analysis: dict[str, Any],
    *,
    user_id: str,
) -> None:
    """
    Backward-compatible alias for any earlier call sites or docs.
    """
    await save_analysis(document_id, analysis, user_id=user_id)


async def save_routing_result(
    document_id: str,
    routing: dict[str, Any],
    *,
    user_id: str,
) -> None:
    """
    Save payment routing recommendation to Firestore.
    Uses merge=True so existing analysis and compliance fields
    are not overwritten.
    """
    if not isinstance(routing, dict):
        raise ValueError("routing must be a dictionary.")

    now = _utc_now_iso()

    # Normalize savings to Decimal then quantize before stringifying.
    # Firestore has no native Decimal type — string preserves exact value
    # with no binary drift and round-trips cleanly via Decimal(stored_string).
    # None → "0.00". Invalid string → raises ValueError (fail-fast policy).
    raw_savings = routing.get("total_savings_usd")
    if raw_savings is None:
        savings_str = "0.00"
    else:
        try:
            savings_str = str(
                Decimal(str(raw_savings)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError(
                "total_savings_usd must be a valid numeric value."
            ) from exc

    # Normalize the nested total_savings_usd in the routing dict so the
    # persisted doc satisfies the Money Math policy (all authoritative
    # money values as normalized strings, no raw Decimal objects).
    # Shallow-copy + overwrite the single money field — avoids mutating
    # the caller's dict.
    normalized_routing = {**routing, "total_savings_usd": savings_str}

    await asyncio.to_thread(
        _get_document_ref(user_id, document_id).set,
        {
            "status": "routed",
            "routing": normalized_routing,
            "routing_recommended_method": routing.get(
                "recommended_method"
            ),
            "routing_total_savings_usd": savings_str,
            "routed_at": now,
            "updated_at": now,
            "error": None,
        },
        merge=True
    )
    logger.info("Routing result saved for document: %s", document_id)
