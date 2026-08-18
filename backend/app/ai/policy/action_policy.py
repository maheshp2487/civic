from typing import List, Dict, Any
from app.schemas.contracts import Situation
from app.rag.retrieval.models import EvidencePack, SufficiencyState

class PolicyDirectives:
    def __init__(self):
        self.allow_specific_actions = False
        self.allow_definitive_claims = False
        self.mandatory_caveat = ""
        self.official_resource_fallback = False

class ActionPolicyEngine:
    @staticmethod
    def evaluate_policy(situation: Situation, evidence_pack: EvidencePack) -> PolicyDirectives:
        directives = PolicyDirectives()
        
        if evidence_pack.sufficiency_state == SufficiencyState.SUFFICIENT:
            directives.allow_specific_actions = True
            directives.allow_definitive_claims = True
            directives.mandatory_caveat = ""
            directives.official_resource_fallback = False
            
        elif evidence_pack.sufficiency_state == SufficiencyState.PARTIAL:
            directives.allow_specific_actions = False
            directives.allow_definitive_claims = False
            directives.mandatory_caveat = "LIMITATION: The provided evidence is general or from a different jurisdiction. Do not assert these rules apply strictly to the user's local jurisdiction."
            directives.official_resource_fallback = True
            
        else: # INSUFFICIENT
            directives.allow_specific_actions = False
            directives.allow_definitive_claims = False
            directives.mandatory_caveat = "LIMITATION: There is insufficient verified evidence to answer this. Do NOT invent legal actions. Do NOT invent claims."
            directives.official_resource_fallback = True
            
        if situation.conflicts:
            directives.allow_specific_actions = False
            directives.mandatory_caveat += " IMPORTANT: The user provided conflicting facts. Ask for clarification before proposing any action."
            
        return directives
