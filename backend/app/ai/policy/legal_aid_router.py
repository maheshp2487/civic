from typing import Optional, List, Dict
from datetime import datetime
from app.schemas.contracts import Situation, LegalAidResource, LegalAidStatus

# Official NALSA/SLSA Mock Data for Demo
OFFICIAL_RESOURCES = [
    {
        "name": "Maharashtra State Legal Services Authority (MSLSA)",
        "level": "State",
        "description": "Provides free legal services to eligible citizens in Maharashtra, including mediation and representation.",
        "official_url": "https://legalservices.maharashtra.gov.in/",
        "contact_info": "Toll Free: 15100",
        "jurisdiction": {"state": "Maharashtra"},
        "source_url": "https://nalsa.gov.in/state-legal-services-authorities",
        "last_verified_at": "2026-08-18"
    },
    {
        "name": "Pune District Legal Services Authority",
        "level": "District",
        "description": "District-level authority providing immediate free legal aid and mediation in Pune courts.",
        "official_url": "https://pune.dcourts.gov.in/legal-services/",
        "contact_info": "Email: dlsa.pune@mah.gov.in",
        "jurisdiction": {"state": "Maharashtra", "district": "Pune"},
        "source_url": "https://pune.dcourts.gov.in/",
        "last_verified_at": "2026-08-18"
    },
    {
        "name": "Delhi State Legal Services Authority (DSLSA)",
        "level": "State",
        "description": "Free and competent legal services to the weaker sections of society in Delhi.",
        "official_url": "http://dslsa.org/",
        "contact_info": "Toll Free: 1516",
        "jurisdiction": {"state": "Delhi"},
        "source_url": "http://dslsa.org/",
        "last_verified_at": "2026-08-18"
    }
]

class LegalAidEligibilityEngine:
    @staticmethod
    def evaluate(situation: Situation) -> LegalAidStatus:
        # Check basic eligibility signals: women, children, SC/ST, low income.
        # This is a deterministic mock representation of Section 12 of the Legal Services Authorities Act, 1987.
        
        # If jurisdiction is missing, we cannot properly assess or route
        if not situation.jurisdiction or not situation.jurisdiction.state:
            return LegalAidStatus.NOT_ENOUGH_INFORMATION
            
        facts_str = " ".join(situation.facts).lower()
        parties_str = " ".join(situation.parties).lower()
        
        # Section 12 criteria keywords
        eligibility_keywords = ["woman", "child", "sc", "st", "dalit", "low income", "poor", "factory worker", "custody", "disabled"]
        
        for kw in eligibility_keywords:
            if kw in facts_str or kw in parties_str:
                return LegalAidStatus.POTENTIALLY_ELIGIBLE
                
        # If no explicit markers found, we don't assume eligible, but we also don't hard deny.
        # We assume not enough income info has been given.
        if "income" not in facts_str:
             return LegalAidStatus.NOT_ENOUGH_INFORMATION
             
        return LegalAidStatus.NOT_IDENTIFIED_AS_ELIGIBLE

class LegalAidRouter:
    @staticmethod
    def route(situation: Situation) -> List[LegalAidResource]:
        if not situation.jurisdiction or not situation.jurisdiction.state:
            return []
            
        target_state = situation.jurisdiction.state.lower()
        target_district = (situation.jurisdiction.district or "").lower()
        
        matches = []
        for res in OFFICIAL_RESOURCES:
            res_state = res["jurisdiction"].get("state", "").lower()
            res_district = res["jurisdiction"].get("district", "").lower()
            
            if res_state == target_state:
                if target_district and res_district == target_district:
                    matches.append(LegalAidResource(**res))
                elif not res_district:
                    # State-level fallback
                    matches.append(LegalAidResource(**res))
                    
        # Sort so District level is preferred over State if both match
        matches.sort(key=lambda x: 0 if x.level == "District" else 1)
        return matches
