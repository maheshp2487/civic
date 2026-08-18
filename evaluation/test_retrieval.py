import pytest
from app.schemas.contracts import Situation, Jurisdiction
from app.rag.retrieval.models import RetrievedChunk, SufficiencyState
from app.rag.retrieval.sufficiency import EvidenceEvaluator
from app.rag.retrieval.reranker import LightweightReranker
from app.rag.retrieval.query_builder import QueryBuilder

def test_query_builder():
    situation = Situation(
        category="Property Dispute",
        subcategory="Security Deposit Withheld",
        jurisdiction=Jurisdiction(country="India", state="Maharashtra"),
        facts=["Landlord kept my 30k"],
        parties=["Tenant"],
        missing_information=[],
        urgency_indicator="Low"
    )
    query = QueryBuilder.build_query(situation)
    assert "Property Dispute" in query.semantic_text
    assert "Maharashtra" == query.jurisdiction_filter.state

def test_evidence_sufficiency_missing():
    situation = Situation(
        category="Test", subcategory="Test",
        facts=["Test"], parties=[], missing_information=[], urgency_indicator="Low"
    )
    pack = EvidenceEvaluator.evaluate(situation, [])
    assert pack.sufficiency_state == SufficiencyState.INSUFFICIENT
    assert "No relevant" in pack.reason

def test_evidence_sufficiency_jurisdiction_partial():
    situation = Situation(
        category="Property", subcategory="Deposit",
        jurisdiction=Jurisdiction(country="India", state="Maharashtra"),
        facts=["Landlord"], parties=[], missing_information=[], urgency_indicator="Low"
    )
    # Mocking a retrieved chunk from a central act (jurisdiction is empty or India but no state)
    chunk = RetrievedChunk(
        chunk_id="1", source_id="2", title="Model Tenancy Act", chunk_text="test",
        similarity_score=0.9, final_score=0.9,
        jurisdiction={"country": "India"}
    )
    pack = EvidenceEvaluator.evaluate(situation, [chunk])
    # The evaluator should flag this as PARTIAL because target is Maharashtra but source is Central
    assert pack.sufficiency_state == SufficiencyState.PARTIAL

def test_evidence_sufficiency_jurisdiction_sufficient():
    situation = Situation(
        category="Property", subcategory="Deposit",
        jurisdiction=Jurisdiction(country="India", state="Maharashtra"),
        facts=["Landlord"], parties=[], missing_information=[], urgency_indicator="Low"
    )
    # Mocking a retrieved chunk from a Maharashtra specific act
    chunk = RetrievedChunk(
        chunk_id="1", source_id="2", title="Maharashtra Rent Control Act", chunk_text="test",
        similarity_score=0.9, final_score=0.9,
        jurisdiction={"country": "India", "state": "Maharashtra"}
    )
    pack = EvidenceEvaluator.evaluate(situation, [chunk])
    assert pack.sufficiency_state == SufficiencyState.SUFFICIENT

def test_reranker_logic():
    reranker = LightweightReranker()
    
    chunk_low_auth = RetrievedChunk(
        chunk_id="1", source_id="2", title="Some Guideline", chunk_text="security deposit",
        source_type="official_guidance", similarity_score=0.8
    )
    chunk_high_auth = RetrievedChunk(
        chunk_id="3", source_id="4", title="Model Tenancy Act", chunk_text="security deposit",
        source_type="act", similarity_score=0.8
    )
    
    # Both have the exact same similarity score and text (so keyword score is same)
    # The high authority one (act) should rank higher than guidance.
    ranked = reranker.rerank([chunk_low_auth, chunk_high_auth], query_keywords=["security deposit"])
    
    assert len(ranked) == 2
    assert ranked[0].chunk_id == "3" # High authority wins
