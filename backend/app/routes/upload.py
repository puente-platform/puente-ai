from fastapi import APIRouter, UploadFile, File, HTTPException
from google.cloud import storage
import uuid
import os
from datetime import datetime, timezone
router = APIRouter()


def get_storage_client():
    return storage.Client(project=os.getenv("GCP_PROJECT_ID"))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Validate file type
    # TODO Phase 2: Add image support (.jpg, .jpeg, .png)
    # when Document AI image handling is implemented in analyze.py
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # Validate file size (10MB max)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB"
        )

    try:
        # Generate a unique Document ID
        document_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        blob_name = f"invoices/{timestamp}/{document_id}.pdf"

        # Upload the file to GCS
        client = get_storage_client()
        bucket = client.bucket(os.getenv("GCS_BUCKET_NAME"))
        blob = bucket.blob(blob_name)

        blob.upload_from_string(
            contents,
            content_type="application/pdf"
        )

        return {
            "document_id": document_id,
            "filename": file.filename,
            "blob_name": blob_name,
            "status": "uploaded",
            "message": "Document uploaded successfully. Analysis pending..."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

    finally:
        await file.close()
