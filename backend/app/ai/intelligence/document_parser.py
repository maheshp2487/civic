import fitz
import json
from google import genai
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.contracts import DocumentClaim
from app.core.config import settings

DOCUMENT_EXTRACTION_PROMPT = """
You are a highly accurate legal document extractor. Extract factual information strictly from the provided document.
DO NOT provide legal advice. DO NOT infer unstated facts.
Identify the document type, any parties mentioned, exact dates, and monetary amounts.
Preserve the page number of the source text.
Return a list of DocumentClaim objects.
"""

class DocumentExtractionResult(BaseModel):
    claims: List[DocumentClaim] = Field(default_factory=list)

class MultimodalDocumentParser:
    def __init__(self):
        self.api_key = settings.gemini_api_key or "DUMMY_KEY"
        self.model = "gemini-3.6-flash"

    def parse_pdf_text(self, file_bytes: bytes, document_id: str) -> List[DocumentClaim]:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_content = ""
            for i, page in enumerate(doc):
                text_content += f"--- PAGE {i+1} ---\n{page.get_text()}\n"
                
            if not text_content.strip():
                return []
                
            return self._extract_with_gemini(text_content, document_id, is_image=False)
        except Exception as e:
            # If PyMuPDF fails, it might be corrupt
            raise RuntimeError(f"PDF Parsing failed: {str(e)}")
        
    def parse_image(self, file_bytes: bytes, mime_type: str, document_id: str) -> List[DocumentClaim]:
        return self._extract_with_gemini(file_bytes, document_id, is_image=True, mime_type=mime_type)

    def _extract_with_gemini(self, content, document_id: str, is_image: bool, mime_type: str = None) -> List[DocumentClaim]:
        if self.api_key == "DUMMY_KEY" or (not is_image and "MOCK" in content):
            return [
                DocumentClaim(claim_id="mock_c1", document_id=document_id, claim_type="Amount", field="Deposit", value="40000", page_number=2, source_text="Deposit: 40000", confidence="High")
            ]
            
        client = genai.Client(api_key=self.api_key)
        
        if is_image:
            parts = [
                {"mime_type": mime_type, "data": content},
                DOCUMENT_EXTRACTION_PROMPT
            ]
        else:
            parts = [
                f"DOCUMENT TEXT:\n{content}\n\n",
                DOCUMENT_EXTRACTION_PROMPT
            ]
            
        try:
            response = client.models.generate_content(
                model=self.model,
                contents=parts,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DocumentExtractionResult,
                    temperature=0.0
                )
            )
            
            if hasattr(response, "parsed") and response.parsed:
                 result = response.parsed
            else:
                 data = json.loads(response.text)
                 result = DocumentExtractionResult(**data)
                 
            for claim in result.claims:
                claim.document_id = document_id
                
            return result.claims
        except Exception as e:
            raise RuntimeError(f"Document extraction failed: {str(e)}")
