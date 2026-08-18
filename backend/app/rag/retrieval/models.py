from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.contracts import Jurisdiction, Situation

class SufficiencyState(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"

class RetrievalQuery(BaseModel):
    semantic_text: str
    exact_keywords: List[str] = Field(default_factory=list)
    jurisdiction_filter: Optional[Jurisdiction] = None
    source_type_filter: Optional[List[str]] = None
    active_only: bool = True

class RetrievedChunk(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    authority: Optional[str] = None
    jurisdiction: Optional[Dict[str, Any]] = None
    source_type: Optional[str] = None
    chunk_text: str
    section: Optional[str] = None
    similarity_score: float
    keyword_score: float = 0.0
    authority_score: float = 0.0
    freshness_score: float = 0.0
    final_score: float = 0.0

class EvidencePack(BaseModel):
    chunks: List[RetrievedChunk]
    sufficiency_state: SufficiencyState
    reason: str
