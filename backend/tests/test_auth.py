# backend/tests/test_auth.py
import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.services import auth as auth_module


class AuthServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_current_user_missing_header_returns_401(self):
        with self.assertRaises(HTTPException) as ctx:
            await auth_module.get_current_user(None)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Missing Authorization header", ctx.exception.detail)

    async def test_get_current_user_malformed_header_returns_401(self):
        with self.assertRaises(HTTPException) as ctx:
            await auth_module.get_current_user("Token abc123")

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Invalid Authorization header format",
                      ctx.exception.detail)

    async def test_get_current_user_valid_bearer_calls_verify(self):
        with patch.object(
            auth_module,
            "verify_firebase_token",
            return_value={"uid": "user-123", "email": "maria@demo.com"},
        ) as verify_mock:
            result = await auth_module.get_current_user("Bearer good.token.value")

        verify_mock.assert_called_once_with("good.token.value")
        self.assertEqual(result["uid"], "user-123")
        self.assertEqual(result["email"], "maria@demo.com")

    def test_verify_firebase_token_invalid_token_returns_401(self):
        with patch.object(
            auth_module,
            "_get_firebase_app",
            return_value=object(),
        ), patch.object(
            auth_module.auth,
            "verify_id_token",
            side_effect=auth_module.auth.InvalidIdTokenError(
                "bad token", cause=None, http_response=None
            ),
        ):
            with self.assertRaises(HTTPException) as ctx:
                auth_module.verify_firebase_token("bad.token")

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Invalid or expired token", ctx.exception.detail)

    def test_verify_firebase_token_expired_token_returns_401(self):
        with patch.object(
            auth_module,
            "_get_firebase_app",
            return_value=object(),
        ), patch.object(
            auth_module.auth,
            "verify_id_token",
            side_effect=auth_module.auth.ExpiredIdTokenError(
                "expired token", cause=None
            ),
        ):
            with self.assertRaises(HTTPException) as ctx:
                auth_module.verify_firebase_token("expired.token")

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Invalid or expired token", ctx.exception.detail)

    def test_verify_firebase_token_service_unavailable_returns_503(self):
        with patch.object(
            auth_module,
            "_get_firebase_app",
            side_effect=RuntimeError("firebase init failed"),
        ):
            with self.assertRaises(HTTPException) as ctx:
                auth_module.verify_firebase_token("any.token")

        self.assertEqual(ctx.exception.status_code, 503)
        self.assertIn("Authentication service unavailable",
                      ctx.exception.detail)

    def test_get_project_id_prefers_firebase_project_id(self):
        with patch.dict(
            os.environ,
            {
                "FIREBASE_PROJECT_ID": "firebase-proj",
                "GCP_PROJECT_ID": "gcp-proj",
            },
            clear=True,
        ):
            project_id = auth_module._get_project_id()

        self.assertEqual(project_id, "firebase-proj")

    def test_get_project_id_falls_back_to_gcp_project_id(self):
        with patch.dict(
            os.environ,
            {
                "GCP_PROJECT_ID": "gcp-proj",
            },
            clear=True,
        ):
            project_id = auth_module._get_project_id()

        self.assertEqual(project_id, "gcp-proj")

    def test_get_project_id_raises_if_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                auth_module._get_project_id()

    # --- KAN-16: uid claim extraction contract ---

    async def test_get_current_user_returns_uid_from_valid_token(self):
        """Valid JWT with uid claim — uid is accessible on returned claims."""
        with patch.object(
            auth_module,
            "verify_firebase_token",
            return_value={"uid": "user-abc", "email": "test@example.com"},
        ):
            result = await auth_module.get_current_user("Bearer valid.token.here")

        self.assertEqual(result["uid"], "user-abc")
        self.assertEqual(result["email"], "test@example.com")

    async def test_get_current_user_missing_uid_claim_returns_400(self):
        """Token that verifies but lacks the uid claim → 400 Invalid token claims.

        Firebase Admin guarantees uid on a real verified token; absence means
        the token is not a genuine Firebase ID token.
        """
        with patch.object(
            auth_module,
            "verify_firebase_token",
            return_value={"email": "no-uid@example.com"},  # no "uid" key
        ):
            with self.assertRaises(Exception) as ctx:
                await auth_module.get_current_user("Bearer no.uid.token")

        from fastapi import HTTPException
        self.assertIsInstance(ctx.exception, HTTPException)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Invalid token claims", ctx.exception.detail)

    async def test_get_current_user_expired_token_returns_401(self):
        """Expired or malformed JWT → 401 (propagated from verify_firebase_token)."""
        with patch.object(
            auth_module,
            "verify_firebase_token",
            side_effect=__import__("fastapi").HTTPException(
                status_code=401, detail="Invalid or expired token."
            ),
        ):
            with self.assertRaises(Exception) as ctx:
                await auth_module.get_current_user("Bearer expired.token.value")

        from fastapi import HTTPException
        self.assertIsInstance(ctx.exception, HTTPException)
        self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
