import re
from typing import List
from app.schemas.contracts import Situation
from app.rag.retrieval.models import RetrievalQuery

# High-signal legal terms to extract from facts — stopwords excluded
_STOP_WORDS = {
    "i", "my", "me", "he", "she", "we", "they", "it", "a", "an", "the",
    "is", "was", "are", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "not", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "that", "this", "which", "who",
    "what", "when", "where", "how", "no", "so", "if", "as", "up", "out",
    "about", "them", "their", "his", "her", "our", "your", "its",
    "also", "than", "then", "into", "over", "after", "before", "between",
    "more", "some", "any", "all", "each", "other", "such", "these", "those",
    "been", "same", "just", "will", "would", "could", "should", "may",
    "might", "shall", "can", "per", "said",
}

_MIN_KEYWORD_LENGTH = 4


def _extract_keywords_from_text(text: str) -> List[str]:
    """
    Extract meaningful, non-trivial keywords from a piece of text.
    Strips punctuation, lowercases, removes stopwords, deduplicates.
    """
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    seen = set()
    keywords = []
    for tok in tokens:
        tok = tok.strip("'")
        if (
            tok not in _STOP_WORDS
            and len(tok) >= _MIN_KEYWORD_LENGTH
            and tok not in seen
        ):
            seen.add(tok)
            keywords.append(tok)
    return keywords


class QueryBuilder:
    @staticmethod
    def build_query(situation: Situation) -> RetrievalQuery:
        # Base: category + subcategory for semantic context
        semantic_parts = []
        if situation.category:
            semantic_parts.append(f"Category: {situation.category}.")
        if situation.subcategory:
            semantic_parts.append(f"Subcategory: {situation.subcategory}.")
        if situation.facts:
            semantic_parts.append("Facts: " + " ".join(situation.facts))
        if situation.parties:
            semantic_parts.append("Parties: " + ", ".join(situation.parties))

        semantic_text = " ".join(semantic_parts)

        # Build keyword set from category, subcategory, AND facts
        keywords: List[str] = []
        seen_kw: set = set()

        def add_kws(source: str):
            for kw in _extract_keywords_from_text(source):
                if kw not in seen_kw:
                    seen_kw.add(kw)
                    keywords.append(kw)

        if situation.category:
            add_kws(situation.category)
        if situation.subcategory:
            add_kws(situation.subcategory)
        for fact in situation.facts:
            add_kws(fact)
        for party in situation.parties:
            add_kws(party)

        return RetrievalQuery(
            semantic_text=semantic_text,
            exact_keywords=keywords,
            jurisdiction_filter=situation.jurisdiction,
            active_only=True,
        )
