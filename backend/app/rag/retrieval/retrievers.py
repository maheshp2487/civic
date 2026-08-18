from abc import ABC, abstractmethod
from typing import List
from app.rag.retrieval.models import RetrievedChunk, RetrievalQuery
from app.core.database import get_supabase_client
from app.rag.ingestion.embedder import GeminiEmbedder

class LegalRetriever(ABC):
    @abstractmethod
    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        pass

class LocalDemoRetriever(LegalRetriever):
    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        chunks = []
        q_str = " ".join(query.exact_keywords).lower()
        if "deposit" in q_str or "landlord" in q_str or "tenant" in q_str or "rent" in q_str or "eviction" in q_str:
            chunks.append(RetrievedChunk(
                chunk_id="demo_chunk_tenancy_1",
                source_id="source_model_tenancy_act",
                title="Model Tenancy Act, 2021",
                authority="Ministry of Housing and Urban Affairs",
                jurisdiction={"country": "India"},
                type="act",
                source_type="act",
                chunk_text="Section 11. (1) The security deposit to be paid by the tenant in advance shall be— (a) not exceed two months’ rent, in case of residential premises; and (b) not exceed six months’ rent, in case of non-residential premises. (2) The security deposit shall be refunded to the tenant on the date of taking over vacant possession of the premises from him, after making due deduction of any liability of the tenant.",
                section="Section 11",
                similarity_score=0.89
            ))
            
        if "worker" in q_str or "factory" in q_str or "wages" in q_str or "salary" in q_str:
             chunks.append(RetrievedChunk(
                chunk_id="demo_chunk_labor_1",
                source_id="source_minimum_wages_act",
                title="Minimum Wages Act, 1948",
                authority="Ministry of Labour & Employment",
                jurisdiction={"country": "India"},
                type="act",
                source_type="act",
                chunk_text="Section 12. Payment of minimum rates of wages. (1) Where in respect of any scheduled employment a notification under section 5 is in force, the employer shall pay to every employee engaged in a scheduled employment under him wages at a rate not less than the minimum rate of wages fixed by such notification for that class of employees in that employment without any deductions except as may be authorized within such time and subject to such conditions as may be prescribed.",
                section="Section 12",
                similarity_score=0.88
            ))

        return chunks

class SupabaseRetriever(LegalRetriever):
    def __init__(self):
        self.client = get_supabase_client()
        self.embedder = GeminiEmbedder()

    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        query_embedding = self.embedder.embed_text(query.semantic_text)
        match_threshold = 0.75
        match_count = 10
        
        jurisdiction_filter = query.jurisdiction_filter.model_dump(exclude_none=True) if query.jurisdiction_filter else {}
        
        rpc_params = {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
            "jurisdiction_filter": jurisdiction_filter,
            "active_only": True
        }
        
        response = self.client.rpc('match_legal_chunks', rpc_params).execute()
        
        chunks = []
        for row in response.data:
            chunks.append(RetrievedChunk(
                chunk_id=row['id'],
                source_id=row['source_id'],
                title=row['title'],
                authority=row.get('authority'),
                jurisdiction=row.get('jurisdiction', {}),
                type=row['type'],
                source_type=row['type'],
                chunk_text=row['chunk_text'],
                section=row.get('section'),
                similarity_score=row['similarity']
            ))
            
        return chunks
