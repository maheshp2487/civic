from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.contracts import OutputResponse, SourceCitation, EvidenceItem, ActionStep

app = FastAPI(
    title="InnoAi Legal Navigation API",
    description="Backend API for the Constitutional Awareness and Legal Aid Chatbot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.config import settings, validate_config

# Validate configuration on startup
validate_config()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "InnoAi API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/ready")
def health_ready():
    return {
        "status": "ready",
        "mode": "demo" if settings.demo_mode else "production",
        "retrieval_backend": "local_demo" if settings.demo_mode else "supabase_pgvector",
        "dependencies": {
            "gemini": "configured" if settings.gemini_api_key else "missing",
            "database": "configured" if settings.supabase_url or settings.demo_mode else "missing"
        }
    }

from app.api.endpoints import documents, cases

app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
