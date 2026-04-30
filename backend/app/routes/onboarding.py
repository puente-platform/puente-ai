# backend/app/routes/onboarding.py
"""
POST /api/v1/onboarding — create or update the authenticated user's onboarding profile.
GET  /api/v1/onboarding — fetch the authenticated user's onboarding profile.

Firestore path: users/{uid}  (top-level collection, one doc per Firebase UID)

Deploy Firestore security rules before this endpoint is live:
    firebase deploy --only firestore:rules

Security invariants enforced here (see plans/onboarding-persistence/plan.md):
  1. uid is ALWAYS from the verified Firebase token (Depends(get_current_user)).
     Any request body containing uid/userId/sub is rejected by the Pydantic model.
  2. All timestamps (createdAt, updatedAt, completedAt) are server-set.
  3. PII-safe logging: request body is NEVER logged.
  4. Exception messages do not include displayName or company values.
"""

import asyncio
import logging
import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from google.cloud import firestore as fs

from app.models.onboarding import OnboardingProfileIn, OnboardingProfileOut
from app.services.auth import get_current_user
from app.services.firestore import get_firestore_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["onboarding"])

_USERS_COLLECTION = "users"


def _doc_to_profile_out(data: dict[str, Any]) -> OnboardingProfileOut:
    """Convert a Firestore document dict to OnboardingProfileOut.
    Firestore SERVER_TIMESTAMP fields arrive as datetime objects; convert to ISO 8601."""

    def _to_iso(val: Any) -> str | None:
        if val is None:
            return None
        if hasattr(val, "isoformat"):
            return val.isoformat()
        return str(val)

    created = _to_iso(data.get("createdAt"))
    updated = _to_iso(data.get("updatedAt"))

    if not created or not updated:
        raise ValueError("Firestore document missing required timestamp fields.")

    return OnboardingProfileOut(
        displayName=data.get("displayName"),
        company=data.get("company"),
        corridors=data.get("corridors"),
        completedAt=_to_iso(data.get("completedAt")),
        createdAt=created,
        updatedAt=updated,
    )


@router.post("/onboarding", status_code=status.HTTP_201_CREATED)
async def upsert_onboarding_profile(
    body: OnboardingProfileIn,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    response: Response,
) -> OnboardingProfileOut:
    """
    Create (201) or update (200) the authenticated user's onboarding profile.

    - uid is derived from the verified Firebase token only; never from the body.
    - Missing keys in the body preserve existing Firestore values.
    - Explicit null in the body clears the corresponding Firestore field.
    - completedAt is stamped exactly once (when markComplete=True and no prior completedAt).
    """
    uid: str = current_user["uid"]
    t_start = time.monotonic()

    db = get_firestore_client()
    doc_ref = db.collection(_USERS_COLLECTION).document(uid)

    try:
        existing_snap = await asyncio.to_thread(doc_ref.get)
    except Exception:
        logger.exception("Firestore read error for uid=%s", uid)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read profile.",
        )

    is_first_write = not existing_snap.exists
    existing_data: dict[str, Any] = existing_snap.to_dict() if not is_first_write else {}

    # ------------------------------------------------------------------
    # Build the Firestore write payload field-by-field.
    # We use model_fields_set to distinguish:
    #   - key absent  → do not include in payload (Firestore merge preserves existing)
    #   - key present, value None → write DELETE_FIELD (clears the field)
    #   - key present, value set  → write the new value
    # We never write markComplete to Firestore.
    # ------------------------------------------------------------------
    update_payload: dict[str, Any] = {}

    for field in ("displayName", "company", "corridors"):
        if field in body.model_fields_set:
            val = getattr(body, field)
            update_payload[field] = fs.DELETE_FIELD if val is None else val

    # Server-set timestamps
    if is_first_write:
        update_payload["createdAt"] = fs.SERVER_TIMESTAMP

    update_payload["updatedAt"] = fs.SERVER_TIMESTAMP

    # completedAt: server-stamped once, immutable thereafter (Security Constraint #2)
    if body.markComplete:
        already_complete = bool(existing_data.get("completedAt"))
        if not already_complete:
            update_payload["completedAt"] = fs.SERVER_TIMESTAMP

    try:
        await asyncio.to_thread(doc_ref.set, update_payload, merge=True)
    except Exception:
        logger.exception("Firestore write error for uid=%s", uid)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save profile.",
        )

    # Re-fetch to get server-resolved timestamp values for the response
    try:
        updated_snap = await asyncio.to_thread(doc_ref.get)
        result_data = updated_snap.to_dict() or {}
    except Exception:
        logger.exception("Firestore re-read error for uid=%s", uid)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve saved profile.",
        )

    latency_ms = int((time.monotonic() - t_start) * 1000)

    # PII-safe structured log — only safe fields, never request body.  # noqa: do-not-log-pii
    logger.info(
        "onboarding_upsert uid=%s status=%d latency_ms=%d corridor_count=%d markComplete=%s",
        uid,
        status.HTTP_201_CREATED if is_first_write else status.HTTP_200_OK,
        latency_ms,
        len(body.corridors) if body.corridors is not None else 0,
        body.markComplete,
    )

    try:
        profile = _doc_to_profile_out(result_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile saved but response serialization failed.",
        )

    if not is_first_write:
        # Decorator defaults to 201 for first write.
        # For updates (existing doc) override to 200.
        response.status_code = status.HTTP_200_OK

    return profile


@router.get("/onboarding", status_code=status.HTTP_200_OK)
async def get_onboarding_profile(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> OnboardingProfileOut:
    """
    Fetch the authenticated user's onboarding profile.

    Returns 200 + OnboardingProfileOut, or 404 if never onboarded.
    uid is always from the verified token — this endpoint is not an enumeration oracle.
    """
    uid: str = current_user["uid"]

    db = get_firestore_client()
    doc_ref = db.collection(_USERS_COLLECTION).document(uid)

    try:
        snap = await asyncio.to_thread(doc_ref.get)
    except Exception:
        logger.exception("Firestore read error for uid=%s", uid)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read profile.",
        )

    if not snap.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding profile not found.",
        )

    data = snap.to_dict() or {}

    try:
        profile = _doc_to_profile_out(data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile data is malformed.",
        )

    return profile
