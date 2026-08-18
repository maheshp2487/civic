from google import genai
import json
from app.schemas.contracts import OutputResponse, Situation
from app.rag.retrieval.models import EvidencePack
from app.ai.policy.action_policy import PolicyDirectives
from app.core.config import settings
from app.ai.reasoning.prompts import GROUNDED_REASONING_PROMPT

class ResponseGenerator:
    def __init__(self):
        self.api_key = settings.gemini_api_key or "DUMMY_KEY"
        self.model = "gemini-3.6-flash"

    def generate(self, situation: Situation, evidence_pack: EvidencePack, policy: PolicyDirectives) -> OutputResponse:
        if self.api_key == "DUMMY_KEY":
            return OutputResponse(
                situation_summary="Mock summary. " + policy.mandatory_caveat,
                clarification_questions=[],
                verified_information=[],
                source_citations=[],
                evidence_checklist=[],
                action_plan=[]
            )
            
        client = genai.Client(api_key=self.api_key)
        
        evidence_json = json.dumps([c.model_dump() for c in evidence_pack.chunks])
        situation_json = situation.model_dump_json()
        
        policy_text = f"ALLOW ACTIONS: {policy.allow_specific_actions}\nALLOW DEFINITIVE CLAIMS: {policy.allow_definitive_claims}\nCAVEAT: {policy.mandatory_caveat}"
        
        prompt = GROUNDED_REASONING_PROMPT + f"\n\nSITUATION:\n{situation_json}\n\nEVIDENCE PACK:\n{evidence_json}\n\nPOLICY DIRECTIVES:\n{policy_text}"
        
        try:
            response = client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=OutputResponse,
                    temperature=0.0
                )
            )
            
            if hasattr(response, "parsed") and response.parsed:
                 return response.parsed
                 
            data = json.loads(response.text)
            return OutputResponse(**data)
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")
