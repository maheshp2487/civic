from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from app.ai.intelligence.document_parser import MultimodalDocumentParser

router = APIRouter()
parser = MultimodalDocumentParser()

@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")
        
    doc_id = str(uuid.uuid4())
    mime_type = file.content_type
    
    if mime_type == "application/pdf":
        claims = parser.parse_pdf_text(contents, doc_id)
    elif mime_type in ["image/jpeg", "image/png"]:
        claims = parser.parse_image(contents, mime_type, doc_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime_type}")
        
    return {"document_id": doc_id, "claims": [c.model_dump() for c in claims]}
