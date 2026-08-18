from typing import List
from app.core.config import settings
from app.rag.retrieval.models import RetrievedChunk

class LightweightReranker:
    def __init__(self):
        self.w_semantic = settings.weight_semantic
        self.w_keyword = settings.weight_keyword
        self.w_authority = settings.weight_authority
        self.w_freshness = settings.weight_freshness

    def rerank(self, chunks: List[RetrievedChunk], query_keywords: List[str]) -> List[RetrievedChunk]:
        # Simple authority map
        authority_hierarchy = {
            "act": 1.0, "constitution": 1.0, "judgment": 0.9,
            "rule": 0.8, "regulation": 0.8, "government_procedure": 0.7,
            "official_guidance": 0.6, "form": 0.5, "legal_aid": 0.5
        }
        
        for c in chunks:
            # Semantic score is usually 0-1 for inner product
            
            # Keyword score
            k_score = 0.0
            if query_keywords:
                text_lower = c.chunk_text.lower()
                hits = sum(1 for kw in query_keywords if kw in text_lower)
                k_score = min(1.0, hits / len(query_keywords))
            c.keyword_score = k_score
            
            # Authority score
            c.authority_score = authority_hierarchy.get(c.source_type, 0.1)
            
            # Freshness score
            c.freshness_score = 1.0
            
            c.final_score = (
                (c.similarity_score * self.w_semantic) +
                (c.keyword_score * self.w_keyword) +
                (c.authority_score * self.w_authority) +
                (c.freshness_score * self.w_freshness)
            )
            
        # Deduplicate
        seen = set()
        deduped = []
        chunks.sort(key=lambda x: x.final_score, reverse=True)
        for c in chunks:
            identifier = f"{c.source_id}_{c.section}"
            if identifier not in seen:
                seen.add(identifier)
                deduped.append(c)
                
        return deduped
