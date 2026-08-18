from app.ai.intelligence.pipeline import SituationIntelligencePipeline
from app.rag.retrieval.search import HybridSearcher
from app.rag.retrieval.query_builder import QueryBuilder
from app.rag.retrieval.reranker import LightweightReranker
from app.rag.retrieval.sufficiency import EvidenceEvaluator
from app.ai.policy.action_policy import ActionPolicyEngine
from app.ai.policy.legal_aid_router import LegalAidEligibilityEngine, LegalAidRouter
from app.ai.reasoning.generator import ResponseGenerator
from app.ai.reasoning.validator import OutputValidator
from app.schemas.contracts import OutputResponse, Situation
from typing import Optional, Tuple

class ChatWorkflow:
    def __init__(self):
        self.intelligence = SituationIntelligencePipeline()
        self.searcher = HybridSearcher()
        self.reranker = LightweightReranker()
        self.generator = ResponseGenerator()

    def run(self, user_input: str, existing_situation: Optional[Situation] = None) -> Tuple[Situation, OutputResponse]:
        if user_input.strip() == "" and existing_situation:
            situation = existing_situation
        else:
            situation = self.intelligence.process(user_input, existing_situation)
        
        if "State/Jurisdiction" in situation.missing_information:
            return situation, OutputResponse(
                situation_summary="I need a bit more information to find the right laws.",
                clarification_questions=["Which state or city did this occur in?"],
                verified_information=[], source_citations=[], evidence_checklist=[], action_plan=[]
            )
            
        if situation.conflicts:
            unresolved = [c for c in situation.conflicts if c.resolution_status == "Unresolved"]
            if unresolved:
                questions = []
                for c in unresolved:
                    questions.append(f"Conflict regarding {c.field}: You stated '{c.user_value}', but {c.document_source} indicates '{c.document_value}'. Which is correct?")
                
                return situation, OutputResponse(
                    situation_summary="There seems to be some conflicting information that needs clarification.",
                    clarification_questions=questions,
                    verified_information=[], source_citations=[], evidence_checklist=[], action_plan=[]
                )
            
        query = QueryBuilder.build_query(situation)
        raw_chunks = self.searcher.search(query)
        ranked_chunks = self.reranker.rerank(raw_chunks, query.exact_keywords)
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
        
        return situation, final_response
