import pytest
from app.schemas.contracts import Situation, Jurisdiction, UrgencyIndicator
from app.ai.intelligence.pipeline import SituationIntelligencePipeline
from app.ai.intelligence.normalizer import DeterministicNormalizer
from app.ai.intelligence.conflict_detector import ConflictDetector

def test_normalization():
    j = Jurisdiction(country="India", district="mumbai")
    j2 = DeterministicNormalizer.normalize_jurisdiction(j)
    assert j2.state == "Maharashtra"
    
def test_urgency_detection():
    sit = Situation(category="Test", subcategory="Test", facts=[], parties=[])
    sit = DeterministicNormalizer.evaluate_urgency("my landlord locked me out today", sit)
    assert sit.urgency.level == "High"
    assert "imminent_eviction" in sit.urgency.indicators
    assert "urgent_deadline" in sit.urgency.indicators

def test_conflict_detection():
    old = Situation(category="Rent", subcategory="Deposit", amounts=["30000"], facts=[], parties=[])
    new = Situation(category="Rent", subcategory="Deposit", amounts=["40000"], facts=[], parties=[])
    merged = ConflictDetector.merge_and_detect(old, new)
    assert "40000" in merged.amounts
    assert "30000" in merged.amounts
    assert len(merged.conflicts) == 0 # User updates are naturally additive, no conflict triggered


def test_missing_jurisdiction():
    pipe = SituationIntelligencePipeline()
    # Provide 'MOCK' string to trigger local fallback in parser.py
    sit = pipe.process("MOCK data")
    assert "State/Jurisdiction" in sit.missing_information
