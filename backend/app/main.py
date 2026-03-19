# backend/app/main.py
from app.routes import upload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Puente AI",
    description="Trade intelligence platform for the Americas",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1")


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
