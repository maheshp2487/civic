from app.schemas.contracts import OutputResponse
from app.rag.retrieval.models import EvidencePack
from app.ai.policy.action_policy import PolicyDirectives

class OutputValidator:
    @staticmethod
    def validate(response: OutputResponse, evidence_pack: EvidencePack, policy: PolicyDirectives) -> OutputResponse:
        valid_chunk_ids = {c.chunk_id for c in evidence_pack.chunks}
        
        # Validate citations
        valid_citations = []
        for cite in response.source_citations:
            if cite.chunk_id in valid_chunk_ids:
                valid_citations.append(cite)
        response.source_citations = valid_citations
        
        # Validate actions
        if not policy.allow_specific_actions:
            response.action_plan = []
        else:
            valid_actions = []
            for action in response.action_plan:
                if action.basis_source_ids:
                    # Strip out invalid IDs, keep action if at least one valid ID exists, or drop entirely
                    valid_ids = [sid for sid in action.basis_source_ids if sid in valid_chunk_ids]
                    if valid_ids:
                        action.basis_source_ids = valid_ids
                        valid_actions.append(action)
                else:
                    # Action without explicit chunk citations is allowed but discouraged
                    valid_actions.append(action)
            response.action_plan = valid_actions
            
        return response
