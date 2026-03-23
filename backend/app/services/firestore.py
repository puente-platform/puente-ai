import asyncio
import logging
import os
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from google.cloud import firestore

logger = logging.getLogger(__name__)

# Module-level singleton — created once, reused across requests
_db: firestore.Client | None = None
_db_lock = Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_transactions_collection() -> firestore.CollectionReference:
    return get_firestore_client().collection("transactions")


def _get_document_ref(
    document_id: str
) -> firestore.DocumentReference:
    if not document_id:
        raise ValueError("document_id is required.")
    return _get_transactions_collection().document(document_id)


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
    file_size: int
) -> dict:

    if file_size < 0:
        raise ValueError("file_size must be non-negative.")

    now = _utc_now_iso()

    transaction_data = {
        "document_id": document_id,
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
        _get_document_ref(document_id).set,
        transaction_data
    )
    return transaction_data


async def get_transaction(document_id: str) -> dict | None:
    doc = await asyncio.to_thread(
        _get_document_ref(document_id).get
    )

    if doc.exists:
        return doc.to_dict()
    return None


async def update_transaction_status(
    document_id: str,
    status: str,
    error: str | None = None
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
        _get_document_ref(document_id).set,
        update_data,
        merge=True
    )


async def save_extraction(
    document_id: str,
    extraction: dict[str, Any]
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
        _get_document_ref(document_id).set,
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
    analysis: dict[str, Any]
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
        _get_document_ref(document_id).set,
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
    compliance: dict[str, Any]
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
    doc_snapshot = await asyncio.to_thread(
        _get_document_ref(document_id).get
    )
    existing = doc_snapshot.to_dict() if doc_snapshot.exists else {}
    existing_analysis = existing.get("analysis")
    if not isinstance(existing_analysis, dict):
        existing_analysis = {}
    merged_analysis = dict(existing_analysis)
    compliance_update = {
        k: v
        for k, v in {
            "compliance_level": compliance.get("compliance_level"),
            "missing_documents": compliance.get("missing_documents"),
        }.items()
        if v is not None
    }
    merged_analysis.update(compliance_update)

    await asyncio.to_thread(
        _get_document_ref(document_id).set,
        {
            "compliance_status": "compliance_checked",
            "compliance": compliance,
            "analysis": merged_analysis,
            "compliance_checked_at": now,
            "updated_at": now,
            "error": None,
        },
        merge=True,
    )
    logger.info("Compliance saved for document: %s", document_id)


async def save_analysis_snapshot(
    document_id: str,
    analysis: dict[str, Any]
) -> None:
    """
    Backward-compatible alias for any earlier call sites or docs.
    """
    await save_analysis(document_id, analysis)
