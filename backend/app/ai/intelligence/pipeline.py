from typing import Optional
from app.schemas.contracts import Situation
from app.ai.intelligence.parser import SituationParser
from app.ai.intelligence.normalizer import DeterministicNormalizer
from app.ai.intelligence.conflict_detector import ConflictDetector

class SituationIntelligencePipeline:
    def __init__(self):
        self.parser = SituationParser()

    def process(self, user_input: str, existing_situation: Optional[Situation] = None) -> Situation:
        new_situation = self.parser.parse(user_input)
        
        new_situation.jurisdiction = DeterministicNormalizer.normalize_jurisdiction(new_situation.jurisdiction)
        new_situation = DeterministicNormalizer.evaluate_urgency(user_input, new_situation)
        
        if existing_situation:
            final_situation = ConflictDetector.merge_and_detect(existing_situation, new_situation)
        else:
            final_situation = new_situation
            if not final_situation.jurisdiction or not final_situation.jurisdiction.state:
                if "State/Jurisdiction" not in final_situation.missing_information:
                    final_situation.missing_information.append("State/Jurisdiction")
                    
        return final_situation
