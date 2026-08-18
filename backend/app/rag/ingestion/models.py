from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Any, Dict, List, Literal
from datetime import date, datetime

class DocumentMetadata(BaseModel):
    title: str
    type: Literal['constitution', 'act', 'rule', 'regulation', 'judgment', 'government_procedure', 'legal_aid', 'official_guidance', 'form']
    authority: Optional[str] = None
    jurisdiction: Optional[Dict[str, Any]] = None
    effective_date: Optional[date] = None
    source_version: Optional[str] = None
    status: Optional[str] = None
    source_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None

class ChunkMetadata(BaseModel):
    chunk_text: str
    page_number: Optional[int] = None
    section: Optional[str] = None

class LegalChunk(BaseModel):
    metadata: ChunkMetadata
    embedding: List[float]
