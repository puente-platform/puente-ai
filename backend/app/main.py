# backend/app/main.py
from app.routes import upload, analyze, compliance, routing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import re
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Puente AI",
    description="Trade intelligence platform for the Americas",
    version="0.1.0"
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
