from app.ai.intelligence.pipeline import SituationIntelligencePipeline
from app.rag.retrieval.search import HybridSearcher
from app.rag.retrieval.query_builder import QueryBuilder
from app.rag.retrieval.reranker import LightweightReranker
from app.rag.retrieval.sufficiency import EvidenceEvaluator
from app.ai.policy.action_policy import ActionPolicyEngine
from app.ai.policy.legal_aid_router import LegalAidEligibilityEngine, LegalAidRouter
from app.ai.reasoning.generator import ResponseGenerator
from app.ai.reasoning.validator import OutputValidator
from app.schemas.contracts import OutputResponse, Situation, IntakeForm
from app.ai.intelligence.intake_builder import IntakeBuilder
from app.rag.retrieval.models import EvidencePack
from typing import Optional, Tuple
import re

def _has_material_facts(text: str) -> bool:
    if not text or not text.strip():
        return False
        
    text_lower = text.lower()
    
    # 1. Simple acknowledgement/continuation check
    conversational = {"yes", "no", "okay", "ok", "continue", "that's correct", "correct", "right", "thanks", "thank you", "sure"}
    cleaned_text = re.sub(r'[^\w\s]', '', text_lower).strip()
    if cleaned_text in conversational:
        return False
        
    # 2. Check for numbers (amounts, dates, sections, etc)
    if re.search(r'\d', text):
        return True
        
    # 3. Check for specific keywords that indicate corrections or new entities
    material_keywords = [
        "not", "instead", "correction", "actually", "wrong", # Corrections
        "₹", "$", "rupee", "rs", "dollar", # Currency
        "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "month", "year", "day", # Dates
        "mumbai", "pune", "delhi", "bangalore", "chennai", "kolkata", "hyderabad", "state", "city", "district", # Locations
        "contract", "lease", "agreement", "notice", "court", "police", "fir", "lawyer", "tenant", "landlord", "employer", "employee", "company" # Legal/Entities
    ]
    
    for kw in material_keywords:
        if kw in text_lower:
            return True
            
    # 4. Length check - if it's over 8 words, assume it might have new facts
    if len(text.split()) > 8:
        return True
        
    # If uncertain, err on the side of reparsing
    return True

class ChatWorkflow:
    def __init__(self):
        self.intelligence = SituationIntelligencePipeline()
        self.searcher = HybridSearcher()
        self.reranker = LightweightReranker()
        self.generator = ResponseGenerator()

    def run(self, user_input: str, existing_situation: Optional[Situation] = None, existing_evidence_pack: Optional[EvidencePack] = None) -> Tuple[Situation, EvidencePack, OutputResponse, Optional[IntakeForm]]:
        reused_situation = False
        if existing_situation and not _has_material_facts(user_input):
            # Fast-path for simple conversational turns
            situation = existing_situation
            reused_situation = True
        else:
            situation = self.intelligence.process(user_input, existing_situation)
        
        if situation.missing_information:
            form = IntakeBuilder.build(situation)
            if form:
                return situation, existing_evidence_pack, OutputResponse(
                    situation_summary="I need a few more details to find the correct legal pathway.",
                    clarification_questions=[],
                    verified_information=[], source_citations=[], evidence_checklist=[], action_plan=[]
                ), form
            
        if situation.conflicts:
            unresolved = [c for c in situation.conflicts if c.resolution_status == "Unresolved"]
            if unresolved:
                questions = []
                for c in unresolved:
                    questions.append(f"Conflict regarding {c.field}: You stated '{c.user_value}', but {c.document_source} indicates '{c.document_value}'. Which is correct?")
                
                return situation, existing_evidence_pack, OutputResponse(
                    situation_summary="There seems to be some conflicting information that needs clarification.",
                    clarification_questions=questions,
                    verified_information=[], source_citations=[], evidence_checklist=[], action_plan=[]
                ), None
            
        if reused_situation and existing_evidence_pack:
            evidence_pack = existing_evidence_pack
        else:
            query = QueryBuilder.build_query(situation)
            
            # Tier 1: Primary retrieval (Local in demo, Supabase in production)
            raw_chunks = self.searcher.search(query)
            ranked_chunks = self.reranker.rerank(raw_chunks, query.exact_keywords)
            evidence_pack = EvidenceEvaluator.evaluate(situation, ranked_chunks)
            
            # Tier 2: If insufficient and in production mode, try OfficialWebRetriever
            if evidence_pack.sufficiency_state.value == "INSUFFICIENT":
                from app.rag.retrieval.models import SufficiencyState
                augmented_chunks = self.searcher.search_with_web_fallback(
                    query, evidence_pack.sufficiency_state
                )
                if len(augmented_chunks) > len(raw_chunks):
                    ranked_chunks = self.reranker.rerank(augmented_chunks, query.exact_keywords)
                    evidence_pack = EvidenceEvaluator.evaluate(situation, ranked_chunks)
        
        policy = ActionPolicyEngine.evaluate_policy(situation, evidence_pack)
        raw_response = self.generator.generate(situation, evidence_pack, policy)
        final_response = OutputValidator.validate(raw_response, evidence_pack, policy)
        
        legal_aid_status = LegalAidEligibilityEngine.evaluate(situation)
        legal_aid_resources = []
        if legal_aid_status in ["POTENTIALLY_ELIGIBLE", "NOT_ENOUGH_INFORMATION"] or "NOT_IDENTIFIED" in legal_aid_status:
            # We route even if NOT_IDENTIFIED to give them an official source, 
            # though we could restrict it. The prompt says "If appropriate, provide a potentially applicable official legal-aid pathway."
            # We'll just provide it if they might be eligible or we lack info.
            if legal_aid_status != "NOT_RELEVANT":
                legal_aid_resources = LegalAidRouter.route(situation)
                
        final_response.legal_aid_status = legal_aid_status
        final_response.legal_aid_resources = legal_aid_resources
        
        return situation, evidence_pack, final_response, None
