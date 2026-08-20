from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
class Jurisdiction(BaseModel):
    country: str = Field(default="India")
    state: Optional[str] = None
    district: Optional[str] = None

class UrgencyIndicator(BaseModel):
    level: str = Field(default="Low", description="Low, Medium, High, Critical")
    reasons: List[str] = Field(default_factory=list)
    indicators: List[str] = Field(default_factory=list)

class DocumentClaim(BaseModel):
    claim_id: str
    document_id: str
    claim_type: str
    field: str
    value: str
    page_number: Optional[int] = None
    source_text: Optional[str] = None
    confidence: str = "High"

class Conflict(BaseModel):
    field: str
    user_value: str
    document_value: str
    document_source: str
    resolution_status: str = "Unresolved"

class Situation(BaseModel):
    category: str
    subcategory: str
    jurisdiction: Optional[Jurisdiction] = None
    facts: List[str]
    parties: List[str]
    dates: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)
    documents_mentioned: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    conflicts: List[Conflict] = Field(default_factory=list)
    uncertainty: List[str] = Field(default_factory=list)
    urgency: UrgencyIndicator = Field(default_factory=UrgencyIndicator)

class SourceCitation(BaseModel):
    title: str
    chunk_id: Optional[str] = None
    section: Optional[str] = None
    url: Optional[str] = None

class EvidenceItem(BaseModel):
    type: str
    description: str
    is_provided: bool = False

class ActionStep(BaseModel):
    step: int
    description: str
    basis_source_ids: List[str] = Field(default_factory=list)
    action_type: str = "General"
    limitation: Optional[str] = None

class LegalAidStatus(str, Enum):
    POTENTIALLY_ELIGIBLE = "POTENTIALLY_ELIGIBLE"
    NOT_ENOUGH_INFORMATION = "NOT_ENOUGH_INFORMATION"
    NOT_IDENTIFIED_AS_ELIGIBLE = "NOT_IDENTIFIED_AS_ELIGIBLE"
    NOT_RELEVANT = "NOT_RELEVANT"

class LegalAidResource(BaseModel):
    name: str
    level: str
    description: str
    official_url: str
    contact_info: str
    jurisdiction: Optional[Jurisdiction] = None
    source_url: str
    last_verified_at: str

class GeminiOutputResponse(BaseModel):
    situation_summary: str
    clarification_questions: List[str] = Field(default_factory=list)
    verified_information: List[str] = Field(default_factory=list)
    source_citations: List[SourceCitation] = Field(default_factory=list)
    evidence_checklist: List[EvidenceItem] = Field(default_factory=list)
    action_plan: List[ActionStep] = Field(default_factory=list)

class OutputResponse(GeminiOutputResponse):
    legal_aid_resources: List[LegalAidResource] = Field(default_factory=list)
    legal_aid_status: LegalAidStatus = LegalAidStatus.NOT_RELEVANT
    disclaimer: str = "Legal information, not legal advice."

class IntakeField(BaseModel):
    id: str
    label: str
    type: str = Field(description="text, select, radio, checkbox, date, number")
    options: List[str] = Field(default_factory=list)
    required: bool = True
    placeholder: Optional[str] = None

class IntakeForm(BaseModel):
    title: str = "Please provide a few more details"
    fields: List[IntakeField] = Field(default_factory=list)

class IntakeResponse(BaseModel):
    values: Dict[str, str] = Field(default_factory=dict)

