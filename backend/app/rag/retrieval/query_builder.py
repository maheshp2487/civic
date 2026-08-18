from app.schemas.contracts import Situation
from app.rag.retrieval.models import RetrievalQuery

class QueryBuilder:
    @staticmethod
    def build_query(situation: Situation) -> RetrievalQuery:
        semantic_text = f"Category: {situation.category}. Subcategory: {situation.subcategory}. Facts: " + " ".join(situation.facts)
        
        keywords = [situation.category.lower(), situation.subcategory.lower()]
        
        return RetrievalQuery(
            semantic_text=semantic_text,
            exact_keywords=keywords,
            jurisdiction_filter=situation.jurisdiction,
            active_only=True
        )
