import pytest
from app.schemas.contracts import Situation, DocumentClaim
from app.ai.intelligence.situation_merger import SituationMerger
from app.ai.intelligence.document_parser import MultimodalDocumentParser

def test_document_merger_conflict():
    sit = Situation(category="test", subcategory="test", facts=[], amounts=["30000"], parties=[])
    claims = [
        DocumentClaim(claim_id="1", document_id="doc1", claim_type="Amount", field="Deposit", value="40000", page_number=2)
    ]
    
    merged = SituationMerger.merge(sit, claims)
    
    assert len(merged.conflicts) == 1
    assert merged.conflicts[0].field == "Amount"
    assert merged.conflicts[0].user_value == "30000"
    assert merged.conflicts[0].document_value == "40000"
    assert "Page 2" in merged.conflicts[0].document_source

def test_document_parser_mock():
    parser = MultimodalDocumentParser()
    claims = parser._extract_with_gemini("MOCK text", document_id="doc1", is_image=False)
    assert len(claims) > 0
    assert claims[0].claim_type == "Amount"
    assert claims[0].value == "40000"
    assert claims[0].page_number == 2
