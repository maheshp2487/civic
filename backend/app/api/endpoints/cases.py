from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any, Optional
import uuid
from pydantic import BaseModel
from app.workflows.chat_workflow import ChatWorkflow
from app.ai.intelligence.document_parser import MultimodalDocumentParser
from app.ai.intelligence.situation_merger import SituationMerger
from app.schemas.contracts import Situation, OutputResponse, IntakeForm, IntakeResponse

router = APIRouter()
chat_workflow = ChatWorkflow()
doc_parser = MultimodalDocumentParser()

cases_db: Dict[str, Dict[str, Any]] = {}

class MessageRequest(BaseModel):
    content: str
    
class CaseResponse(BaseModel):
    case_id: str
    situation: Situation
    output: Optional[OutputResponse] = None
    workflow_state: str
    intake_form: Optional[IntakeForm] = None

@router.post("/reset")
async def reset_demo():
    cases_db.clear()
    return {"status": "ok", "message": "Demo state reset successfully."}

@router.post("/{case_id}/messages", response_model=CaseResponse)
async def post_message(case_id: str, req: MessageRequest):
    if case_id not in cases_db:
        cases_db[case_id] = {"situation": None, "evidence_pack": None, "output": None}
        
    existing_situation = cases_db[case_id]["situation"]
    existing_evidence_pack = cases_db[case_id].get("evidence_pack")
    
    if existing_situation and existing_situation.conflicts:
        unresolved = [c for c in existing_situation.conflicts if c.resolution_status == "Unresolved"]
        if unresolved:
            for c in unresolved:
                if req.content in [c.user_value, c.document_value, "Neither"]:
                    c.resolution_status = "Resolved"
                    if req.content != "Neither":
                        if c.field == "Amount":
                            existing_situation.amounts = [req.content]
                        elif c.field == "Date":
                            existing_situation.dates = [req.content]
                            
            new_sit, new_ev, output = chat_workflow.run("", existing_situation, existing_evidence_pack)
            cases_db[case_id]["situation"] = new_sit
            cases_db[case_id]["evidence_pack"] = new_ev
            cases_db[case_id]["output"] = output
            
            workflow_state = "READY"
            if intake:
                workflow_state = "NEEDS_INTAKE"
            elif [c for c in new_sit.conflicts if c.resolution_status == "Unresolved"]:
                workflow_state = "NEEDS_CLARIFICATION"
                
            return CaseResponse(
                case_id=case_id,
                situation=new_sit,
                output=output,
                workflow_state=workflow_state,
                intake_form=intake
            )
            
    try:
        new_sit, new_ev, output, intake = chat_workflow.run(req.content, existing_situation, existing_evidence_pack)
    except Exception as e:
        from app.core.exceptions import QuotaExhaustedError
        if isinstance(e, QuotaExhaustedError):
            raise HTTPException(status_code=429, detail=str(e))
        raise
        
    cases_db[case_id]["situation"] = new_sit
    cases_db[case_id]["evidence_pack"] = new_ev
    cases_db[case_id]["output"] = output
    
    workflow_state = "READY"
    if intake:
        workflow_state = "NEEDS_INTAKE"
    elif [c for c in new_sit.conflicts if c.resolution_status == "Unresolved"]:
        workflow_state = "NEEDS_CLARIFICATION"
        
    return CaseResponse(
        case_id=case_id,
        situation=new_sit,
        output=output,
        workflow_state=workflow_state,
        intake_form=intake
    )

@router.post("/{case_id}/intake", response_model=CaseResponse)
async def submit_intake(case_id: str, intake: IntakeResponse):
    if case_id not in cases_db or not cases_db[case_id]["situation"]:
        raise HTTPException(status_code=400, detail="Case not found or no existing situation.")
        
    existing_situation = cases_db[case_id]["situation"]
    existing_evidence_pack = cases_db[case_id].get("evidence_pack")
    
    from app.ai.intelligence.intake_builder import IntakeBuilder
    expected_form = IntakeBuilder.build(existing_situation)
    if expected_form:
        for field in expected_form.fields:
            if field.required:
                val = intake.values.get(field.id)
                if not val or not val.strip():
                    raise HTTPException(status_code=422, detail=f"Validation Error: '{field.label}' is required but was empty.")
                    
    updated_situation, invalidate_evidence = SituationMerger.merge_intake(existing_situation, intake)
    
    if invalidate_evidence:
        existing_evidence_pack = None
        
    # Now run the workflow but with an empty user input, relying entirely on the fully merged situation
    try:
        new_sit, new_ev, output, intake_form = chat_workflow.run("", updated_situation, existing_evidence_pack)
    except Exception as e:
        from app.core.exceptions import QuotaExhaustedError
        if isinstance(e, QuotaExhaustedError):
            raise HTTPException(status_code=429, detail=str(e))
        raise
        
    cases_db[case_id]["situation"] = new_sit
    cases_db[case_id]["evidence_pack"] = new_ev
    cases_db[case_id]["output"] = output
    
    workflow_state = "READY"
    if intake_form:
        workflow_state = "NEEDS_INTAKE"
    elif [c for c in new_sit.conflicts if c.resolution_status == "Unresolved"]:
        workflow_state = "NEEDS_CLARIFICATION"
        
    return CaseResponse(
        case_id=case_id,
        situation=new_sit,
        output=output,
        workflow_state=workflow_state,
        intake_form=intake_form
    )

@router.post("/{case_id}/documents", response_model=CaseResponse)
async def upload_document(case_id: str, file: UploadFile = File(...)):
    if case_id not in cases_db or not cases_db[case_id]["situation"]:
        raise HTTPException(status_code=400, detail="Case not found or no existing situation.")
        
    contents = await file.read()
    doc_id = str(uuid.uuid4())
    mime_type = file.content_type
    
    if mime_type == "application/pdf":
        claims = doc_parser.parse_pdf_text(contents, doc_id)
    elif mime_type in ["image/jpeg", "image/png"]:
        claims = doc_parser.parse_image(contents, mime_type, doc_id)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
        
    existing_situation = cases_db[case_id]["situation"]
    updated_situation = SituationMerger.merge(existing_situation, claims)
    cases_db[case_id]["situation"] = updated_situation
    
    unresolved = [c for c in updated_situation.conflicts if c.resolution_status == "Unresolved"]
    if unresolved:
        try:
            new_sit, new_ev, output, intake = chat_workflow.run("", updated_situation)
        except Exception as e:
            from app.core.exceptions import QuotaExhaustedError
            if isinstance(e, QuotaExhaustedError):
                raise HTTPException(status_code=429, detail=str(e))
            raise
            
        return CaseResponse(
            case_id=case_id,
            situation=new_sit,
            output=output,
            workflow_state="CONFLICT_DETECTED"
        )
        
    try:
        new_sit, new_ev, output, intake = chat_workflow.run("", updated_situation)
    except Exception as e:
        from app.core.exceptions import QuotaExhaustedError
        if isinstance(e, QuotaExhaustedError):
            raise HTTPException(status_code=429, detail=str(e))
        raise
        
    cases_db[case_id]["situation"] = new_sit
    cases_db[case_id]["evidence_pack"] = new_ev
    cases_db[case_id]["output"] = output
    
    workflow_state = "READY"
    if intake:
        workflow_state = "NEEDS_INTAKE"
        
    return CaseResponse(
        case_id=case_id,
        situation=new_sit,
        output=output,
        workflow_state=workflow_state,
        intake_form=intake
    )
