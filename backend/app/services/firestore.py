# backend/app/services/firestore.py
from google.cloud import firestore
from datetime import datetime, timezone
import os


def get_firestore_client():
    return firestore.Client(project=os.getenv("GCP_PROJECT_ID"))


async def create_transaction_record(
    document_id: str,
    filename: str,
    blob_name: str,
    file_size: int
) -> dict:

    db = get_firestore_client()

    transaction_data = {
        "document_id": document_id,
        "filename": filename,
        "blob_name": blob_name,
        "file_size_bytes": file_size,
        "status": "uploaded",
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "analysis": {
            "fraud_score": None,
            "fraud_flags": None,
            "compliance_level": None,
            "missing_documents": None,
            "routing_recommendation": None,
            "summary": None
        },
        "analyzed_at": None,
        "error": None
    }

    db.collection("transactions").document(document_id).set(transaction_data)

    return transaction_data


async def get_transaction(document_id: str) -> dict | None:

    db = get_firestore_client()
    doc = db.collection("transactions").document(document_id).get()

    if doc.exists:
        return doc.to_dict()
    return None


async def update_transaction_status(
    document_id: str,
    status: str,
    error: str = None
) -> None:

    db = get_firestore_client()

    update_data = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    if error:
        update_data["error"] = error

    db.collection("transactions").document(document_id).update(update_data)
