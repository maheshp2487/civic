import pytest
import os
from app.ai.intelligence.pipeline import SituationIntelligencePipeline
from app.core.config import settings

@pytest.mark.skipif(not settings.gemini_api_key, reason="No Gemini API Key found")
def test_real_gemini_extraction():
    pipe = SituationIntelligencePipeline()
    
    # 1. Messy landlord scenario
    sit1 = pipe.process("My landlord in Pune refused to return my 30000 rupees deposit last week.")
    assert "Maharashtra" == sit1.jurisdiction.state
    assert any("30000" in str(amt) for amt in sit1.amounts)
    
    # 2. Conflicting update
    sit2 = pipe.process("Wait, the deposit was actually 40000 rupees.", existing_situation=sit1)
    assert any("40000" in str(amt) for amt in sit2.amounts)
    assert len(sit2.conflicts) > 0
    assert sit2.conflicts[0].field == "Amount"
