# backend/app/main.py
from app.routes import upload, analyze, compliance, routing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os
import re
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Puente AI",
    description="Trade intelligence platform for the Americas",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Build allowed origins — env var lets us add more without redeploying
# Validate each extra origin is a well-formed https:// URL (blocks wildcards like *)
_EXTRA_ORIGINS = os.getenv("EXTRA_ALLOWED_ORIGINS", "")
_extra = [
    o.strip() for o in _EXTRA_ORIGINS.split(",")
    if o.strip() and re.match(
        r"^https?://[a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(:\d+)?$",
        o.strip()
    )
]

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://id-preview--11330f28-95e3-48bf-8f58-776e62b33067.lovable.app",
    "https://11330f28-95e3-48bf-8f58-776e62b33067.lovable.app",
    "https://puenteai.ai",
    "https://www.puenteai.ai",
] + _extra

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https://.*\.(lovable\.app|lovableproject\.com)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1")
app.include_router(routing.router, prefix="/api/v1", tags=["routing"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "project": os.getenv("GCP_PROJECT_ID"),
        "environment": os.getenv("ENVIRONMENT")
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to Puente AI",
        "version": "0.1.0"
    }


# ---------------------------------------------------------------------------
# Custom OpenAPI schema — inject Bearer security scheme so Swagger UI shows
# the "Authorize" button and pilot brokers know they need a JWT.
# All four authenticated routes (/api/v1/upload, /api/v1/analyze,
# /api/v1/compliance, /api/v1/routing) are marked with the HTTPBearer scheme.
# ---------------------------------------------------------------------------

_AUTHENTICATED_PATHS = {
    "/api/v1/upload",
    "/api/v1/analyze",
    "/api/v1/compliance",
    "/api/v1/routing",
}


def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Inject the HTTPBearer security scheme definition.
    schema.setdefault("components", {})
    schema["components"].setdefault("securitySchemes", {})
    schema["components"]["securitySchemes"]["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "Firebase JWT",
    }

    # Apply the security requirement to every operation on each authenticated path.
    for path, path_item in schema.get("paths", {}).items():
        if path in _AUTHENTICATED_PATHS:
            for _method, operation in path_item.items():
                if isinstance(operation, dict):
                    operation.setdefault("security", [])
                    bearer_entry = {"HTTPBearer": []}
                    if bearer_entry not in operation["security"]:
                        operation["security"].append(bearer_entry)

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi
