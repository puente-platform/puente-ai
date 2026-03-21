# backend/app/services/firestore.py
from google.cloud import firestore
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)

# Module-level singleton — created once, reused across requests
_db = None


def get_firestore_client() -> firestore.Client:
    global _db
    if _db is None:
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

    db = get_firestore_client()
    now = datetime.now(timezone.utc).isoformat()

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

    db.collection("transactions").document(document_id).set(
        transaction_data
    )
    return transaction_data


async def get_transaction(document_id: str) -> dict | None:
    db = get_firestore_client()
    doc = db.collection("transactions").document(
        document_id
    ).get()

    if doc.exists:
        return doc.to_dict()
    return None


async def update_transaction_status(
    document_id: str,
    status: str,
    error: str | None = None
) -> None:

    db = get_firestore_client()
    now = datetime.now(timezone.utc).isoformat()

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
    # should always succeed even in recovery flows.
    # Trade-off: a bad document_id creates a thin document
    # rather than failing loudly. Acceptable for Phase 2.
    db.collection("transactions").document(document_id).set(
        update_data,
        merge=True
    )


async def save_extraction(
    document_id: str,
    extraction: dict
) -> None:
    """
    Centralized extraction save.
    Clears any previous error field on success.
    Sets updated_at for consistent last-touch tracking.
    """
    db = get_firestore_client()
    now = datetime.now(timezone.utc).isoformat()

    db.collection("transactions").document(document_id).set(
        {
            "status": "extracted",
            "extraction": extraction,
            "extracted_at": extraction.get("extracted_at"),
            "updated_at": now,
            "error": None  # Fix: clear stale errors on success
        },
        merge=True
    )
    logger.info(f"Extraction saved for document: {document_id}")