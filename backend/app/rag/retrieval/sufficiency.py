from typing import List
from app.schemas.contracts import Situation
from app.rag.retrieval.models import RetrievedChunk, EvidencePack, SufficiencyState

class EvidenceEvaluator:
    @staticmethod
    def evaluate(situation: Situation, chunks: List[RetrievedChunk]) -> EvidencePack:
        if not chunks:
            return EvidencePack(
                chunks=[],
                sufficiency_state=SufficiencyState.INSUFFICIENT,
                reason="No relevant legal sources found."
            )
            
        target_jurisdiction = situation.jurisdiction
        has_jurisdiction_mismatch = False
        
        # Check jurisdiction match
        for c in chunks:
            source_j = c.jurisdiction or {}
            if target_jurisdiction:
                # If target specifies a state, but source is only nationally applicable (no state) or a different state
                if target_jurisdiction.state:
                    if "state" not in source_j:
                        has_jurisdiction_mismatch = True
                    elif source_j.get("state") != target_jurisdiction.state:
                        has_jurisdiction_mismatch = True
        
        best_score = chunks[0].final_score
        
        # If the top semantic match + weights is extremely low, it's irrelevant
        if best_score < 0.2:
            return EvidencePack(
                chunks=chunks,
                sufficiency_state=SufficiencyState.INSUFFICIENT,
                reason="Retrieved evidence is not semantically relevant to the core issue."
            )
            
        if has_jurisdiction_mismatch:
            return EvidencePack(
                chunks=chunks,
                sufficiency_state=SufficiencyState.PARTIAL,
                reason="Relevant central/model laws found, but exact jurisdiction-specific applicability is unverified."
            )
            
        return EvidencePack(
            chunks=chunks,
            sufficiency_state=SufficiencyState.SUFFICIENT,
            reason="Relevant authoritative evidence with appropriate jurisdiction applicability found."
        )
