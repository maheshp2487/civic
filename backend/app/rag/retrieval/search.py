from typing import List
from app.rag.retrieval.models import RetrievedChunk, RetrievalQuery
from app.core.config import settings
from app.rag.retrieval.retrievers import LocalDemoRetriever, SupabaseRetriever, LegalRetriever

class HybridSearcher:
    def __init__(self):
        self.retriever: LegalRetriever
        if settings.demo_mode:
            self.retriever = LocalDemoRetriever()
        else:
            self.retriever = SupabaseRetriever()

    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        return self.retriever.search(query)
