import pytest
from app.schemas.contracts import Situation, OutputResponse, SourceCitation, ActionStep
from app.rag.retrieval.models import EvidencePack, SufficiencyState, RetrievedChunk
from app.ai.policy.action_policy import ActionPolicyEngine
from app.ai.reasoning.validator import OutputValidator

def test_action_policy_insufficient():
    sit = Situation(category="test", subcategory="test", facts=[], parties=[])
    pack = EvidencePack(chunks=[], sufficiency_state=SufficiencyState.INSUFFICIENT, reason="")
    
    policy = ActionPolicyEngine.evaluate_policy(sit, pack)
    assert not policy.allow_specific_actions
    assert not policy.allow_definitive_claims
    assert "insufficient verified evidence" in policy.mandatory_caveat

def test_action_policy_partial():
    sit = Situation(category="test", subcategory="test", facts=[], parties=[])
    pack = EvidencePack(chunks=[], sufficiency_state=SufficiencyState.PARTIAL, reason="")
    
    policy = ActionPolicyEngine.evaluate_policy(sit, pack)
    assert not policy.allow_specific_actions
    assert "different jurisdiction" in policy.mandatory_caveat

def test_citation_integrity_validator():
    sit = Situation(category="test", subcategory="test", facts=[], parties=[])
    pack = EvidencePack(chunks=[
        RetrievedChunk(chunk_id="valid-1", source_id="s1", title="Act", chunk_text="test", similarity_score=0.9, final_score=0.9)
    ], sufficiency_state=SufficiencyState.SUFFICIENT, reason="")
    
    policy = ActionPolicyEngine.evaluate_policy(sit, pack)
    
    # LLM hallucinates a fake citation ID "fake-99" and a valid one "valid-1"
    response = OutputResponse(
        situation_summary="Test",
        source_citations=[
            SourceCitation(title="Real", chunk_id="valid-1"),
            SourceCitation(title="Fake", chunk_id="fake-99")
        ],
        action_plan=[
            ActionStep(step=1, description="Do this", basis_source_ids=["valid-1"]),
            ActionStep(step=2, description="Do that", basis_source_ids=["fake-99"])
        ]
    )
    
    validated = OutputValidator.validate(response, pack, policy)
    
    # Fake citation should be stripped
    assert len(validated.source_citations) == 1
    assert validated.source_citations[0].chunk_id == "valid-1"
    
    # Action step 2 should be stripped because its ONLY basis is fake
    assert len(validated.action_plan) == 1
    assert validated.action_plan[0].step == 1
