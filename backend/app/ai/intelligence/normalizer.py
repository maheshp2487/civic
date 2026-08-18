from typing import Optional
from app.schemas.contracts import Jurisdiction, Situation

class DeterministicNormalizer:
    CITY_TO_STATE_MAP = {
        "mumbai": "Maharashtra",
        "pune": "Maharashtra",
        "nagpur": "Maharashtra",
        "delhi": "Delhi",
        "new delhi": "Delhi",
        "bangalore": "Karnataka",
        "bengaluru": "Karnataka",
        "chennai": "Tamil Nadu",
        "kolkata": "West Bengal",
        "hyderabad": "Telangana"
    }

    @staticmethod
    def normalize_jurisdiction(jurisdiction: Optional[Jurisdiction]) -> Optional[Jurisdiction]:
        if not jurisdiction:
            return None
            
        if not jurisdiction.state and jurisdiction.district:
            city_lower = jurisdiction.district.lower().strip()
            if city_lower in DeterministicNormalizer.CITY_TO_STATE_MAP:
                jurisdiction.state = DeterministicNormalizer.CITY_TO_STATE_MAP[city_lower]
                
        return jurisdiction

    @staticmethod
    def evaluate_urgency(text: str, situation: Situation) -> Situation:
        text_lower = text.lower()
        reasons = []
        indicators = []
        level = "Low"
        
        if "arrest" in text_lower or "police" in text_lower or "jail" in text_lower:
            level = "High"
            reasons.append("Potential involvement of law enforcement or arrest mentioned.")
            indicators.append("arrest_or_police")
            
        if any(word in text_lower for word in ["lock out", "locked out", "locked me out", "throw out", "kicked out", "kick me out"]):
            level = "High"
            reasons.append("Potential imminent or recent physical eviction.")
            indicators.append("imminent_eviction")
            
        if "harm" in text_lower or "threat" in text_lower or "hit me" in text_lower:
            level = "Critical"
            reasons.append("Potential physical safety concern.")
            indicators.append("physical_safety")
            
        if "deadline" in text_lower or "tomorrow" in text_lower or "today" in text_lower:
            if level == "Low":
                level = "Medium"
            reasons.append("Urgent time constraint mentioned.")
            indicators.append("urgent_deadline")
            
        situation.urgency.level = level
        situation.urgency.reasons = reasons
        situation.urgency.indicators = indicators
        
        return situation
