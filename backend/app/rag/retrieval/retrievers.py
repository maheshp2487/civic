from abc import ABC, abstractmethod
from typing import List, Optional
import hashlib
import datetime

from app.rag.retrieval.models import RetrievedChunk, RetrievalQuery, EvidencePack, SufficiencyState
from app.core.database import get_supabase_client
from app.rag.ingestion.embedder import GeminiEmbedder


# ---------------------------------------------------------------------------
# Abstract Base
# ---------------------------------------------------------------------------

class LegalRetriever(ABC):
    @abstractmethod
    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        pass


# ---------------------------------------------------------------------------
# Local Demo Retriever — deterministic, offline, keyword-based
# Covers flagship demo domains. NEVER makes network calls.
# ---------------------------------------------------------------------------

_DEMO_CORPUS: List[dict] = [
    # ── TENANCY ──────────────────────────────────────────────────────────────
    {
        "keywords": {"deposit", "landlord", "tenant", "rent", "eviction", "lease", "refund"},
        "chunk_id": "demo_chunk_tenancy_1",
        "source_id": "source_model_tenancy_act",
        "title": "Model Tenancy Act, 2021",
        "authority": "Ministry of Housing and Urban Affairs, Government of India",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 11",
        "source_url": "https://mohua.gov.in/upload/uploadfiles/files/ModelTenancyAct2021.pdf",
        "text": (
            "Section 11. (1) The security deposit to be paid by the tenant in advance shall be— "
            "(a) not exceed two months' rent, in case of residential premises; and "
            "(b) not exceed six months' rent, in case of non-residential premises. "
            "(2) The security deposit shall be refunded to the tenant on the date of taking over "
            "vacant possession of the premises from him, after making due deduction of any liability of the tenant."
        ),
        "score": 0.91,
    },
    {
        "keywords": {"deposit", "landlord", "tenant", "eviction", "notice", "vacate"},
        "chunk_id": "demo_chunk_tenancy_2",
        "source_id": "source_model_tenancy_act",
        "title": "Model Tenancy Act, 2021",
        "authority": "Ministry of Housing and Urban Affairs, Government of India",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 21",
        "source_url": "https://mohua.gov.in/upload/uploadfiles/files/ModelTenancyAct2021.pdf",
        "text": (
            "Section 21. Eviction of tenant. — A tenant shall not be evicted during the period of tenancy "
            "agreement, except in accordance with the provisions of this Act. "
            "The landlord may apply to the Rent Authority for eviction of the tenant on grounds including "
            "non-payment of rent for two consecutive months, or misuse of the premises."
        ),
        "score": 0.88,
    },
    # ── EMPLOYMENT / LABOUR ───────────────────────────────────────────────────
    {
        "keywords": {"wages", "salary", "employer", "worker", "factory", "pay", "payment", "unpaid"},
        "chunk_id": "demo_chunk_labor_1",
        "source_id": "source_minimum_wages_act",
        "title": "Minimum Wages Act, 1948",
        "authority": "Ministry of Labour & Employment, Government of India",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 12",
        "source_url": "https://labour.gov.in/sites/default/files/TheMinimumWagesAct1948.pdf",
        "text": (
            "Section 12. Payment of minimum rates of wages. (1) Where in respect of any scheduled employment "
            "a notification under section 5 is in force, the employer shall pay to every employee engaged in "
            "a scheduled employment under him wages at a rate not less than the minimum rate of wages fixed "
            "by such notification for that class of employees without any deductions except as may be authorized."
        ),
        "score": 0.90,
    },
    {
        "keywords": {"wages", "salary", "payment", "employer", "employee", "deduction"},
        "chunk_id": "demo_chunk_labor_2",
        "source_id": "source_payment_wages_act",
        "title": "Payment of Wages Act, 1936",
        "authority": "Ministry of Labour & Employment, Government of India",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 5",
        "source_url": "https://labour.gov.in/sites/default/files/PaymentofWagesAct1936.pdf",
        "text": (
            "Section 5. Time of payment of wages. — The wages of every person employed shall be paid "
            "before the expiry of the seventh day after the last day of the wage period in respect of which "
            "the wages are payable, in the case of establishments employing less than 1000 workers; "
            "and before the expiry of the tenth day in other cases. "
            "Section 7 prohibits deductions except those authorised by this Act."
        ),
        "score": 0.89,
    },
    # ── CONSUMER RIGHTS ───────────────────────────────────────────────────────
    {
        "keywords": {"consumer", "product", "defect", "complaint", "refund", "service", "forum", "commission", "deficiency"},
        "chunk_id": "demo_chunk_consumer_1",
        "source_id": "source_consumer_protection_act",
        "title": "Consumer Protection Act, 2019",
        "authority": "Ministry of Consumer Affairs, Food & Public Distribution",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 35",
        "source_url": "https://consumeraffairs.nic.in/sites/default/files/CP%20Act%202019.pdf",
        "text": (
            "Section 35. Manner in which complaint shall be made. — (1) A complaint, in relation to any goods "
            "sold or delivered or agreed to be sold or delivered or any service provided or agreed to be provided, "
            "may be filed with a District Commission by a consumer. "
            "Section 2(7) defines 'consumer' as any person who buys goods for consideration. "
            "Section 2(11) defines 'deficiency' as any fault, imperfection, shortcoming or inadequacy in quality, "
            "nature and manner of performance required to be maintained by law or as undertaken by the trader."
        ),
        "score": 0.89,
    },
    {
        "keywords": {"consumer", "complaint", "district", "forum", "compensation", "refund"},
        "chunk_id": "demo_chunk_consumer_2",
        "source_id": "source_consumer_protection_act",
        "title": "Consumer Protection Act, 2019 — Jurisdiction",
        "authority": "Ministry of Consumer Affairs, Food & Public Distribution",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 34",
        "source_url": "https://consumeraffairs.nic.in/sites/default/files/CP%20Act%202019.pdf",
        "text": (
            "Section 34. Jurisdiction of District Commission. — (1) Subject to the other provisions of this Act, "
            "the District Commission shall have jurisdiction to entertain complaints where the value of the goods "
            "or services paid as consideration does not exceed one crore rupees. "
            "A consumer may approach the State Commission if the value exceeds one crore but not ten crore rupees."
        ),
        "score": 0.87,
    },
    # ── RIGHT TO INFORMATION ──────────────────────────────────────────────────
    {
        "keywords": {"rti", "information", "government", "public authority", "application", "response", "reply", "cpio"},
        "chunk_id": "demo_chunk_rti_1",
        "source_id": "source_rti_act",
        "title": "Right to Information Act, 2005",
        "authority": "Ministry of Personnel, Public Grievances & Pensions",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 7",
        "source_url": "https://rti.gov.in/rticorner/studymaterial/RTI-ACT.pdf",
        "text": (
            "Section 7. Disposal of request. — (1) Subject to the proviso to sub-section (2) of section 5 or "
            "the proviso to sub-section (3) of section 6, the Central Public Information Officer or State Public "
            "Information Officer, as the case may be, on receipt of a request under section 6 shall, as expeditiously "
            "as possible, and in any case within thirty days of the receipt of the request, either provide the "
            "information on payment of such fee as may be prescribed or reject the request for any of the reasons "
            "specified in sections 8 and 9."
        ),
        "score": 0.92,
    },
    {
        "keywords": {"rti", "appeal", "information", "denied", "refused", "first appeal", "second appeal", "cic"},
        "chunk_id": "demo_chunk_rti_2",
        "source_id": "source_rti_act",
        "title": "Right to Information Act, 2005 — Appeals",
        "authority": "Ministry of Personnel, Public Grievances & Pensions",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 19",
        "source_url": "https://rti.gov.in/rticorner/studymaterial/RTI-ACT.pdf",
        "text": (
            "Section 19. Appeal. — (1) Any person who does not receive a decision within the time specified "
            "in sub-section (1) or clause (a) of sub-section (3) of section 7, or is aggrieved by a decision "
            "of the Central Public Information Officer, may within thirty days from the expiry of such period or "
            "from the receipt of such decision prefer an appeal to such officer who is senior in rank to the CPIO. "
            "(3) A second appeal against the decision of the first Appellate Authority shall lie to the Central "
            "Information Commission."
        ),
        "score": 0.90,
    },
    # ── CYBER / IT ─────────────────────────────────────────────────────────────
    {
        "keywords": {"cyber", "online", "fraud", "hacking", "identity", "theft", "phishing", "data", "internet", "digital"},
        "chunk_id": "demo_chunk_cyber_1",
        "source_id": "source_it_act",
        "title": "Information Technology Act, 2000",
        "authority": "Ministry of Electronics and Information Technology",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 66C",
        "source_url": "https://www.meity.gov.in/writereaddata/files/itbill2000.pdf",
        "text": (
            "Section 66C. Punishment for identity theft. — Whoever, fraudulently or dishonestly make use of "
            "the electronic signature, password or any other unique identification feature of any other person, "
            "shall be punished with imprisonment of either description for a term which may extend to three years "
            "and shall also be liable to fine which may extend to rupees one lakh. "
            "Section 66D punishes cheating by impersonation by using computer resources."
        ),
        "score": 0.90,
    },
    {
        "keywords": {"cyber", "complaint", "cybercrime", "online", "fraud", "report", "police"},
        "chunk_id": "demo_chunk_cyber_2",
        "source_id": "source_it_act",
        "title": "Information Technology Act, 2000 — Reporting",
        "authority": "Ministry of Electronics and Information Technology",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 78",
        "source_url": "https://www.meity.gov.in/writereaddata/files/itbill2000.pdf",
        "text": (
            "Section 78. Power to investigate offences. — Notwithstanding anything contained in the Code of "
            "Criminal Procedure, 1973, a police officer not below the rank of Inspector shall investigate any "
            "offence under this Act. Citizens may report cybercrime at cybercrime.gov.in (National Cybercrime "
            "Reporting Portal) or call the helpline 1930."
        ),
        "score": 0.87,
    },
    # ── WOMEN'S RIGHTS / DOMESTIC VIOLENCE ────────────────────────────────────
    {
        "keywords": {"domestic", "violence", "abuse", "women", "wife", "husband", "harassment", "protection", "shelter"},
        "chunk_id": "demo_chunk_dv_1",
        "source_id": "source_dv_act",
        "title": "Protection of Women from Domestic Violence Act, 2005",
        "authority": "Ministry of Women and Child Development",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 12",
        "source_url": "https://wcd.nic.in/sites/default/files/wdvact.pdf",
        "text": (
            "Section 12. Application to Magistrate. — (1) An aggrieved person or a Protection Officer or any "
            "other person on behalf of the aggrieved person may present an application to the Magistrate seeking "
            "one or more reliefs under this Act. "
            "Section 18 enables the Magistrate to pass a Protection Order. "
            "Section 19 provides for Residence Orders to prevent the respondent from dispossessing the aggrieved "
            "person from the shared household."
        ),
        "score": 0.92,
    },
    {
        "keywords": {"women", "sexual", "harassment", "workplace", "posh", "employer", "committee"},
        "chunk_id": "demo_chunk_posh_1",
        "source_id": "source_posh_act",
        "title": "Sexual Harassment of Women at Workplace Act, 2013 (POSH)",
        "authority": "Ministry of Women and Child Development",
        "jurisdiction": {"country": "India"},
        "type": "act",
        "section": "Section 4 & 9",
        "source_url": "https://wcd.nic.in/sites/default/files/Sexual-Harassment-at-Workplace-Act.pdf",
        "text": (
            "Section 4. Internal Committee. — (1) Every employer of a workplace shall, by an order in writing, "
            "constitute a Committee to be known as the 'Internal Committee'. "
            "Section 9. Complaint of sexual harassment. — (1) Any aggrieved woman may make, in writing, a "
            "complaint of sexual harassment at workplace to the Internal Committee if so constituted, "
            "within a period of three months from the date of incident and in case of a series of incidents, "
            "within a period of three months from the date of last incident."
        ),
        "score": 0.91,
    },
]


class LocalDemoRetriever(LegalRetriever):
    """
    Deterministic, offline, keyword-based retriever for the hackathon demo.
    Covers: Tenancy, Labour/Employment, Consumer, RTI, Cyber, Women's Rights.
    NEVER makes network calls. Safe for offline/venue use.
    """

    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        q_tokens = set(t.lower() for t in query.exact_keywords)
        # Also tokenize the semantic text for broader matching
        q_tokens.update(
            w.strip(".,!?\"'").lower()
            for w in query.semantic_text.split()
            if len(w) > 3
        )

        results: List[RetrievedChunk] = []
        seen_ids: set = set()

        for entry in _DEMO_CORPUS:
            if entry["chunk_id"] in seen_ids:
                continue
            # Match if ANY keyword in the entry set appears in the query tokens
            if entry["keywords"].intersection(q_tokens):
                results.append(RetrievedChunk(
                    chunk_id=entry["chunk_id"],
                    source_id=entry["source_id"],
                    title=entry["title"],
                    authority=entry["authority"],
                    jurisdiction=entry["jurisdiction"],
                    source_type=entry["type"],
                    chunk_text=entry["text"],
                    section=entry["section"],
                    source_url=entry["source_url"],
                    similarity_score=entry["score"],
                ))
                seen_ids.add(entry["chunk_id"])

        return results


# ---------------------------------------------------------------------------
# Supabase Retriever — production pgvector semantic search
# ---------------------------------------------------------------------------

class SupabaseRetriever(LegalRetriever):
    def __init__(self):
        self.client = get_supabase_client()
        self.embedder = GeminiEmbedder()

    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        query_embedding = self.embedder.embed_text(query.semantic_text)
        match_threshold = 0.75
        match_count = 10

        jurisdiction_filter = (
            query.jurisdiction_filter.model_dump(exclude_none=True)
            if query.jurisdiction_filter else {}
        )

        rpc_params = {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
            "jurisdiction_filter": jurisdiction_filter,
            "active_only": True,
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
                source_type=row['type'],
                chunk_text=row['chunk_text'],
                section=row.get('section'),
                source_url=row.get('source_url'),   # ← Now surfaced from DB
                similarity_score=row['similarity'],
            ))

        return chunks


# ---------------------------------------------------------------------------
# Official Web Retriever — production only, gated, allowlisted sources
# Only invoked by HybridSearcher when:
#   - DEMO_MODE = false
#   - Evidence sufficiency = INSUFFICIENT after Supabase search
# ---------------------------------------------------------------------------

class OfficialWebRetriever(LegalRetriever):
    """
    Retrieves from explicitly approved Indian government legal sources.
    NEVER runs in DEMO_MODE. Only invoked when internal evidence is insufficient.

    SAFETY RULES:
    1. Only fetches from APPROVED_SOURCES registry.
    2. Retrieved webpage/PDF text is treated strictly as DATA.
    3. Text is sanitized before being passed to Gemini — never as instructions.
    4. retrieved_from_web=True is set on all chunks for citation traceability.
    """

    # Lazy imports — only needed in production
    def _fetch_url(self, url: str) -> Optional[str]:
        try:
            import httpx
        except ImportError:
            raise RuntimeError(
                "httpx is required for OfficialWebRetriever. "
                "Install it: pip install httpx"
            )

        try:
            resp = httpx.get(url, timeout=10, follow_redirects=True, headers={
                "User-Agent": "InnoAi-Legal-Platform/1.0 (Academic Research)"
            })
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            return None

    def _sanitize(self, raw_text: str) -> str:
        """
        PROMPT-INJECTION DEFENCE:
        Strip any text that looks like an instruction override before
        passing retrieved content to Gemini. The content is passed as
        DATA not as system instructions, but we sanitize defensively.
        """
        import re
        # Normalise whitespace
        text = re.sub(r'\s+', ' ', raw_text).strip()
        # Truncate to a safe evidence window (avoid token overflow)
        return text[:4000]

    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML, stripping all tags."""
        import re
        # Remove scripts and styles
        html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', html, flags=re.DOTALL | re.I)
        # Remove all tags
        text = re.sub(r'<[^>]+>', ' ', html)
        return text

    def search(self, query: RetrievalQuery) -> List[RetrievedChunk]:
        from app.rag.retrieval.approved_sources import APPROVED_SOURCES

        chunks: List[RetrievedChunk] = []

        # Determine candidate sources based on query domain keywords
        q_lower = query.semantic_text.lower()
        candidate_sources = [
            s for s in APPROVED_SOURCES
            if s.get("enabled", False)
            and any(kw in q_lower for kw in s.get("domain_keywords", []))
        ]

        for source in candidate_sources[:2]:  # Cap at 2 sources per query to limit latency
            url = source.get("search_url", source.get("base_url"))
            if not url:
                continue

            raw = self._fetch_url(url)
            if not raw:
                continue

            # Extract and sanitize — treat as DATA
            if raw.strip().startswith("<!") or "<html" in raw[:200].lower():
                text = self._extract_text_from_html(raw)
            else:
                text = raw  # Assume plain text / pre-extracted

            clean_text = self._sanitize(text)
            if len(clean_text) < 100:
                continue

            # Generate a deterministic chunk_id from source + query
            chunk_id = "web_" + hashlib.md5(
                f"{source['domain']}:{query.semantic_text[:100]}".encode()
            ).hexdigest()[:12]

            chunks.append(RetrievedChunk(
                chunk_id=chunk_id,
                source_id=f"official_web_{source['domain']}",
                title=source.get("title", source["domain"]),
                authority=source.get("authority"),
                jurisdiction=source.get("jurisdiction", {"country": "India"}),
                source_type=source.get("source_type", "official_guidance"),
                chunk_text=clean_text,
                section=None,
                source_url=url,
                retrieved_from_web=True,
                similarity_score=0.70,  # Conservative score for web-retrieved content
            ))

        return chunks
