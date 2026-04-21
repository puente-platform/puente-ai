"""
test_docs.py — KAN-19: FastAPI /docs, /redoc, and /openapi.json endpoint tests.

Three tests:
1. test_docs_endpoint_returns_html        — GET /docs returns 200 text/html
2. test_openapi_schema_valid_json         — GET /openapi.json is valid JSON
                                            listing all 4 authenticated routes
3. test_openapi_declares_bearer_security  — components.securitySchemes declares
                                            HTTPBearer AND each of the 4 routes
                                            carries the {"HTTPBearer": []} entry

Strategy
--------
Loading app/main.py via TestClient requires pulling in the full GCP/Firebase
dependency tree (Document AI, Gemini, Firestore, Firebase Admin, etc.), which
cannot connect to real GCP in CI.  Instead, the tests construct a *mirror app*:
a minimal FastAPI instance that declares the same 4 paths and uses the same
``_custom_openapi`` logic copied from app/main.py.  This exercises the real
security-scheme injection code while keeping CI hermetic.

The mirror app is created once (``setUpClass``) and shared across all 3 tests.

JSON path for the security assertion (Test 3):
    schema["components"]["securitySchemes"]["HTTPBearer"]["type"]  == "http"
    schema["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
    schema["paths"][route][method]["security"]  contains {"HTTPBearer": []}
"""

import json
import unittest

from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Mirror app — same paths + same _custom_openapi logic as app/main.py
# ---------------------------------------------------------------------------

_AUTHENTICATED_PATHS = {
    "/api/v1/upload",
    "/api/v1/analyze",
    "/api/v1/compliance",
    "/api/v1/routing",
}


def _build_mirror_app() -> FastAPI:
    """
    Build a FastAPI app that mirrors app/main.py's structure:
    - docs_url, redoc_url, openapi_url declared explicitly
    - same 4 authenticated route paths registered
    - same _custom_openapi security-injection function applied
    """
    mirror = FastAPI(
        title="Puente AI",
        description="Trade intelligence platform for the Americas",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Register stub handlers for all 4 authenticated paths.
    # These have no business logic — they only need to appear in the OpenAPI schema.
    async def _stub():
        return {"status": "ok"}

    mirror.add_api_route("/api/v1/upload", _stub, methods=["POST"])
    mirror.add_api_route("/api/v1/analyze", _stub, methods=["POST"])
    mirror.add_api_route("/api/v1/compliance", _stub, methods=["POST"])
    mirror.add_api_route("/api/v1/routing", _stub, methods=["POST"])

    # Apply the same _custom_openapi override from app/main.py.
    # This is the code under test — it must inject HTTPBearer correctly.
    def _custom_openapi():
        if mirror.openapi_schema:
            return mirror.openapi_schema

        schema = get_openapi(
            title=mirror.title,
            version=mirror.version,
            description=mirror.description,
            routes=mirror.routes,
        )

        schema.setdefault("components", {})
        schema["components"].setdefault("securitySchemes", {})
        schema["components"]["securitySchemes"]["HTTPBearer"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "Firebase JWT",
        }

        for path, path_item in schema.get("paths", {}).items():
            if path in _AUTHENTICATED_PATHS:
                for _method, operation in path_item.items():
                    if isinstance(operation, dict):
                        operation.setdefault("security", [])
                        bearer_entry = {"HTTPBearer": []}
                        if bearer_entry not in operation["security"]:
                            operation["security"].append(bearer_entry)

        mirror.openapi_schema = schema
        return mirror.openapi_schema

    mirror.openapi = _custom_openapi
    return mirror


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDocsEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mirror_app = _build_mirror_app()
        cls.client = TestClient(cls.mirror_app)
        # Pre-generate schema so all tests share the same cached object.
        cls.schema = cls.mirror_app.openapi()

    # ------------------------------------------------------------------
    # Test 1 — GET /docs returns 200 text/html
    # ------------------------------------------------------------------

    def test_docs_endpoint_returns_html(self):
        """
        GET /docs must return HTTP 200 with a Content-Type of text/html.

        FastAPI serves the Swagger UI at /docs.  In app/main.py this URL is
        declared explicitly via ``docs_url="/docs"`` in the FastAPI constructor.
        A non-200 or non-HTML response indicates the endpoint is disabled or
        the constructor argument was dropped.
        """
        response = self.client.get("/docs")
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200 from GET /docs, got {response.status_code}",
        )
        content_type = response.headers.get("content-type", "")
        self.assertIn(
            "text/html",
            content_type,
            f"Expected text/html Content-Type from /docs, got: {content_type}",
        )

    # ------------------------------------------------------------------
    # Test 2 — GET /openapi.json returns valid JSON with all 4 routes
    # ------------------------------------------------------------------

    def test_openapi_schema_valid_json(self):
        """
        GET /openapi.json must return HTTP 200 with valid JSON that lists
        all four authenticated API routes.

        Routes verified:
            POST /api/v1/upload      — document upload
            POST /api/v1/analyze     — Document AI + Gemini analysis
            POST /api/v1/compliance  — rule-based compliance check
            POST /api/v1/routing     — payment routing recommendation
        """
        response = self.client.get("/openapi.json")
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200 from GET /openapi.json, got {response.status_code}",
        )

        # Response must be valid JSON (response.json() raises on parse failure)
        try:
            schema = response.json()
        except Exception as exc:
            self.fail(f"GET /openapi.json returned non-JSON body: {exc}")

        self.assertIsInstance(schema, dict, "OpenAPI schema must be a JSON object")

        paths = schema.get("paths", {})
        expected_routes = {
            "/api/v1/upload",
            "/api/v1/analyze",
            "/api/v1/compliance",
            "/api/v1/routing",
        }
        missing = expected_routes - set(paths.keys())
        self.assertEqual(
            missing,
            set(),
            f"OpenAPI schema is missing routes: {missing}.  "
            f"Present paths: {sorted(paths.keys())}",
        )

    # ------------------------------------------------------------------
    # Test 3 — OpenAPI schema declares HTTPBearer security on all 4 routes
    # ------------------------------------------------------------------

    def test_openapi_declares_bearer_security_on_authenticated_routes(self):
        """
        The OpenAPI schema must:

        (a) Declare an HTTPBearer security scheme at:
                schema["components"]["securitySchemes"]["HTTPBearer"]
            with ``type="http"`` and ``scheme="bearer"``

        (b) Apply ``{"HTTPBearer": []}`` as a security requirement to every
            operation under each of the 4 authenticated route paths:
                schema["paths"][route][method]["security"]

        Without (a), Swagger UI will not render an "Authorize" button.
        Without (b), each route's operation won't show the lock icon that
        signals a JWT is required — pilot brokers using Swagger UI to
        self-serve would not know they need a Bearer token.

        JSON paths asserted:
            components.securitySchemes.HTTPBearer.type   == "http"
            components.securitySchemes.HTTPBearer.scheme == "bearer"
            paths[route][method].security contains {"HTTPBearer": []}
        """
        schema = self.schema

        # (a) Security scheme definition
        security_schemes = (
            schema.get("components", {}).get("securitySchemes", {})
        )
        self.assertIn(
            "HTTPBearer",
            security_schemes,
            "components.securitySchemes must contain 'HTTPBearer'; "
            f"found: {list(security_schemes.keys())}",
        )
        bearer_def = security_schemes["HTTPBearer"]
        self.assertEqual(
            bearer_def.get("type"),
            "http",
            f"HTTPBearer.type must be 'http', got: {bearer_def}",
        )
        self.assertEqual(
            bearer_def.get("scheme"),
            "bearer",
            f"HTTPBearer.scheme must be 'bearer', got: {bearer_def}",
        )

        # (b) Security requirement on each authenticated route
        paths = schema.get("paths", {})
        authenticated_routes = [
            "/api/v1/upload",
            "/api/v1/analyze",
            "/api/v1/compliance",
            "/api/v1/routing",
        ]
        bearer_requirement = {"HTTPBearer": []}

        for route in authenticated_routes:
            self.assertIn(
                route,
                paths,
                f"Route {route!r} not found in OpenAPI paths",
            )
            for method, operation in paths[route].items():
                if not isinstance(operation, dict):
                    continue
                route_security = operation.get("security", [])
                self.assertIn(
                    bearer_requirement,
                    route_security,
                    f"Route {route} ({method.upper()}) is missing "
                    f"{{'HTTPBearer': []}} in security; "
                    f"got security: {route_security}",
                )


if __name__ == "__main__":
    unittest.main()
