# backend/app/services/auth.py
import logging
import os
from threading import Lock
from typing import Any
from starlette.concurrency import run_in_threadpool
import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth, credentials, exceptions as firebase_exceptions

logger = logging.getLogger(__name__)

# Singleton Firebase app instance (initialize once, reuse everywhere)
_firebase_app: firebase_admin.App | None = None
_firebase_lock = Lock()


def _get_project_id() -> str:
    """
    Resolve project id with fallback:
    FIREBASE_PROJECT_ID -> GCP_PROJECT_ID
    """
    project_id = (
        os.getenv("FIREBASE_PROJECT_ID")
        or os.getenv("GCP_PROJECT_ID")
    )
    if not project_id:
        raise RuntimeError(
            "Missing project id. Set FIREBASE_PROJECT_ID or GCP_PROJECT_ID."
        )
    return project_id


def _get_firebase_app() -> firebase_admin.App:
    """
    Initialize Firebase Admin SDK once using ADC.
    - Local: gcloud application-default credentials
    - Cloud Run: attached service account
    """
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    with _firebase_lock:
        if _firebase_app is not None:
            return _firebase_app

        project_id = _get_project_id()
        cred = credentials.ApplicationDefault()
        _firebase_app = firebase_admin.initialize_app(
            cred,
            {"projectId": project_id},
        )
        logger.info("Firebase Admin initialized for project=%s", project_id)
        return _firebase_app


def verify_firebase_token(token: str) -> dict[str, Any]:
    """
    Verify Firebase ID token and return decoded claims.
    Raises:
        - HTTP 401 for invalid/expired/revoked token
        - HTTP 503 for auth service/internal failures
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    try:
        _get_firebase_app()
        decoded = auth.verify_id_token(token, check_revoked=True)
        return decoded

    # User/token problems -> 401
    except (
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.UserDisabledError,
    ) as exc:
        logger.warning("Token rejected: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        ) from exc

    # Firebase service/backend issues -> 503
    except (
        auth.CertificateFetchError,
        firebase_exceptions.FirebaseError,
        RuntimeError,
    ) as exc:
        logger.error("Firebase auth backend unavailable: %s",
                     exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable.",
        ) from exc


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """
    FastAPI dependency to extract and verify:
    Authorization: Bearer <firebase_id_token>
    """
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: Bearer <token>.",
        )

    token = parts[1]
    claims = await run_in_threadpool(verify_firebase_token, token)

    # Firebase Admin guarantees `uid` on a successfully verified token.
    # Absence indicates a malformed or non-Firebase token — fail fast.
    if not claims.get("uid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token claims.",
        )

    return claims
