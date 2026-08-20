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
        
        valid_chunks = []
        has_jurisdiction_mismatch = False
        
        # Generic words that cannot independently justify a match
        generic_keywords = {"police", "person", "amount", "document", "complaint", "report", "online", "information", "notice", "deposit", "law", "act"}
        
        # Combine user context for intersection checking
        user_text = ""
        if situation.facts:
            user_text += " ".join(situation.facts).lower()
        if situation.category:
            user_text += " " + situation.category.lower()

        for c in chunks:
            # 1. Jurisdiction Match
            source_j = c.jurisdiction or {}
            chunk_jurisdiction_valid = True
            
            if target_jurisdiction and target_jurisdiction.state:
                # If target has state, and source has state, they must match.
                # If source is national (no state), it's acceptable (tier 1/central law).
                if "state" in source_j and source_j["state"] != target_jurisdiction.state:
                    chunk_jurisdiction_valid = False
                    has_jurisdiction_mismatch = True
            elif "state" in source_j:
                # Target has NO state specified. If source HAS a specific state, it is INVALID.
                # We cannot assume a random state's laws apply nationally.
                chunk_jurisdiction_valid = False
                has_jurisdiction_mismatch = True

            if not chunk_jurisdiction_valid:
                continue # Discard chunk completely if it's the wrong state's law
                
            # 2. Generic Keyword Filter (only for mock/keyword based chunks)
            # For semantic (pgvector) or web chunks, this is less critical, but we can do a basic check
            # if we have exact keywords in the chunk metadata
            
            # 3. Minimum Score Threshold
            score = c.similarity_score
            if c.retrieved_from_web:
                score *= c.authority_score  # Discount web results by authority
            else:
                score = c.final_score if c.final_score > 0 else c.similarity_score
                
            if score >= 0.35: # Threshold for sufficiency
                valid_chunks.append(c)
                
        if not valid_chunks:
            return EvidencePack(
                chunks=[],
                sufficiency_state=SufficiencyState.INSUFFICIENT,
                reason="Found initial sources, but they did not meet strict relevance/jurisdiction thresholds."
            )
            
        if has_jurisdiction_mismatch and len(valid_chunks) == 0:
            return EvidencePack(
                chunks=[],
                sufficiency_state=SufficiencyState.INSUFFICIENT,
                reason="Sources found, but none applied to the user's specific jurisdiction."
            )
            
        return EvidencePack(
            chunks=valid_chunks,
            sufficiency_state=SufficiencyState.SUFFICIENT,
            reason="Relevant authoritative evidence with appropriate jurisdiction applicability found."
        )
