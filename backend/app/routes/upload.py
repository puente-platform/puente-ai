from fastapi import APIRouter, UploadFile, File, HTTPException
from google.cloud import storage
from app.services.firestore import create_transaction_record
import uuid
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def get_storage_client():
    project = os.getenv("GCP_PROJECT_ID")
    if not project:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")
    return storage.Client(project=project)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Validate file type
    # TODO Phase 2: Add image support (.jpg, .jpeg, .png)
    # when Document AI image handling is implemented in analyze.py
    if not file.filename or not file.filename.lower().endswith(".pdf"):
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
        document_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        blob_name = f"invoices/{timestamp}/{document_id}.pdf"

        # Upload to GCS first
        client = get_storage_client()
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not bucket_name:
            raise ValueError("GCS_BUCKET_NAME not set.")

        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_string(
            contents,
            content_type="application/pdf"
        )

        # Attempt Firestore write — if it fails, clean up GCS
        try:
            await create_transaction_record(
                document_id=document_id,
                filename=file.filename,
                blob_name=blob_name,
                file_size=len(contents)
            )
        except Exception as firestore_error:
            logger.error(
                f"Firestore write failed for {document_id}, "
                f"cleaning up GCS: {firestore_error}"
            )
            try:
                blob.delete()
                logger.info(f"Cleaned up orphaned GCS blob: {blob_name}")
            except Exception as cleanup_error:
                logger.error(
                    f"GCS cleanup also failed for {blob_name}: "
                    f"{cleanup_error}"
                )
            raise

        return {
            "document_id": document_id,
            "filename": file.filename,
            "blob_name": blob_name,
            "status": "uploaded",
            "message": "Document uploaded successfully. Analysis pending..."
        }

    except ValueError as e:
        logger.error(f"Configuration error in upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error."
        )

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Upload failed. Please try again."
        )

    finally:
        await file.close()
