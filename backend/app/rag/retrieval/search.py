from typing import List
from app.rag.retrieval.models import RetrievedChunk, RetrievalQuery, SufficiencyState
from app.core.config import settings
from app.rag.retrieval.retrievers import (
    LocalDemoRetriever,
    SupabaseRetriever,
    OfficialWebRetriever,
    LegalRetriever,
)


class HybridSearcher:
    """
    Routes retrieval requests based on DEMO_MODE and evidence sufficiency.

    DEMO_MODE=true  → LocalDemoRetriever only (offline, deterministic)
    DEMO_MODE=false → SupabaseRetriever primary
                      OfficialWebRetriever fallback (when evidence INSUFFICIENT)
    """

    def __init__(self):
        if settings.demo_mode:
            self._primary: LegalRetriever = LocalDemoRetriever()
            self._web_retriever = None  # Never used in demo mode
        else:
            self._primary: LegalRetriever = SupabaseRetriever()
            self._web_retriever = OfficialWebRetriever()

    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        """Primary search — always used."""
        return self._primary.search(query)

    def search_with_web_fallback(
        self,
        query: RetrievalQuery,
        primary_sufficiency: SufficiencyState,
    ) -> List[RetrievedChunk]:
        """
        Extended search that adds OfficialWebRetriever results when:
          - We are NOT in DEMO_MODE
          - Primary evidence is INSUFFICIENT
          - A web retriever is configured

        The caller (ChatWorkflow) decides whether to invoke this based on
        the EvidencePack returned from the primary search.
        """
        primary_chunks = self._primary.search(query)

        if (
            self._web_retriever is not None
            and not settings.demo_mode
            and primary_sufficiency == SufficiencyState.INSUFFICIENT
        ):
            try:
                web_chunks = self._web_retriever.search(query)
                # Merge: primary chunks first (higher trust), then web
                combined = primary_chunks + web_chunks
                return combined
            except Exception as e:
                # Web retrieval failure must never crash the primary flow
                import logging
                logging.getLogger(__name__).warning(
                    f"OfficialWebRetriever failed silently: {e}"
                )
                return primary_chunks

        return primary_chunks
