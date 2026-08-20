"""
APPROVED_SOURCES — Explicit allowlist for OfficialWebRetriever.

RULES:
- Only add official Government of India, State Government, or statutory body sources.
- Do NOT add third-party legal aggregators, law firms, or unofficial websites.
- Every entry must have a verifiable `base_url` linking to an official domain.
- Set `enabled: False` for sources that are not yet validated for production use.
- `domain_keywords` are used to match which sources are relevant to a query.

This registry is the ONLY place where web retrieval targets are defined.
It is intentionally explicit and auditable.
"""

from typing import List, Dict, Any

APPROVED_SOURCES: List[Dict[str, Any]] = [
    # ── LEGISLATION / ACTS ────────────────────────────────────────────────────
    {
        "domain": "indiacode.nic.in",
        "title": "India Code — Official Repository of Indian Legislation",
        "authority": "Ministry of Law and Justice, Government of India",
        "jurisdiction": {"country": "India"},
        "source_type": "act",
        "base_url": "https://www.indiacode.nic.in",
        "search_url": "https://www.indiacode.nic.in/handle/123456789/1362",  # Acts listing
        "domain_keywords": [
            "act", "law", "legislation", "section", "statute", "code",
            "rights", "legal", "amendment"
        ],
        "enabled": True,
    },
    # ── SUPREME COURT ─────────────────────────────────────────────────────────
    {
        "domain": "main.sci.gov.in",
        "title": "Supreme Court of India — Official Website",
        "authority": "Supreme Court of India",
        "jurisdiction": {"country": "India"},
        "source_type": "judgment",
        "base_url": "https://main.sci.gov.in",
        "search_url": "https://main.sci.gov.in/judgments",
        "domain_keywords": [
            "supreme court", "judgment", "constitution", "fundamental rights",
            "article", "writ", "petition", "bench"
        ],
        "enabled": True,
    },
    # ── NALSA — LEGAL AID ─────────────────────────────────────────────────────
    {
        "domain": "nalsa.gov.in",
        "title": "NALSA — National Legal Services Authority",
        "authority": "National Legal Services Authority",
        "jurisdiction": {"country": "India"},
        "source_type": "legal_aid",
        "base_url": "https://nalsa.gov.in",
        "search_url": "https://nalsa.gov.in/services",
        "domain_keywords": [
            "legal aid", "free legal", "slsa", "dlsa", "lok adalat",
            "legal services", "poor", "marginalised"
        ],
        "enabled": True,
    },
    # ── CONSUMER AFFAIRS ──────────────────────────────────────────────────────
    {
        "domain": "consumerhelpline.gov.in",
        "title": "National Consumer Helpline",
        "authority": "Ministry of Consumer Affairs, Food & Public Distribution",
        "jurisdiction": {"country": "India"},
        "source_type": "government_procedure",
        "base_url": "https://consumerhelpline.gov.in",
        "search_url": "https://consumerhelpline.gov.in/public/index.php",
        "domain_keywords": [
            "consumer", "complaint", "product", "defect", "refund",
            "service", "deficiency", "forum", "commission"
        ],
        "enabled": True,
    },
    # ── RTI ───────────────────────────────────────────────────────────────────
    {
        "domain": "rtionline.gov.in",
        "title": "RTI Online — Central Government RTI Portal",
        "authority": "Ministry of Personnel, Public Grievances & Pensions",
        "jurisdiction": {"country": "India"},
        "source_type": "government_procedure",
        "base_url": "https://rtionline.gov.in",
        "search_url": "https://rtionline.gov.in/request/request.php",
        "domain_keywords": [
            "rti", "right to information", "information", "public authority",
            "cpio", "appeal", "cic", "information commission"
        ],
        "enabled": True,
    },
    # ── CYBER CRIME ───────────────────────────────────────────────────────────
    {
        "domain": "cybercrime.gov.in",
        "title": "National Cybercrime Reporting Portal",
        "authority": "Ministry of Home Affairs, Government of India",
        "jurisdiction": {"country": "India"},
        "source_type": "government_procedure",
        "base_url": "https://cybercrime.gov.in",
        "search_url": "https://cybercrime.gov.in",
        "domain_keywords": [
            "cyber", "cybercrime", "online fraud", "hacking", "identity theft",
            "phishing", "social media", "digital fraud", "cyber stalking"
        ],
        "enabled": True,
    },
    # ── LABOUR / EMPLOYMENT ───────────────────────────────────────────────────
    {
        "domain": "labour.gov.in",
        "title": "Ministry of Labour & Employment",
        "authority": "Ministry of Labour & Employment, Government of India",
        "jurisdiction": {"country": "India"},
        "source_type": "act",
        "base_url": "https://labour.gov.in",
        "search_url": "https://labour.gov.in/acts-rules",
        "domain_keywords": [
            "wages", "salary", "employer", "employee", "worker",
            "factory", "labour", "employment", "termination", "provident fund"
        ],
        "enabled": True,
    },
    # ── WOMEN & CHILD DEVELOPMENT ─────────────────────────────────────────────
    {
        "domain": "wcd.nic.in",
        "title": "Ministry of Women & Child Development",
        "authority": "Ministry of Women & Child Development, Government of India",
        "jurisdiction": {"country": "India"},
        "source_type": "act",
        "base_url": "https://wcd.nic.in",
        "search_url": "https://wcd.nic.in/acts-rules-and-policies",
        "domain_keywords": [
            "domestic violence", "women", "sexual harassment", "posh",
            "child", "dowry", "maintenance", "protection"
        ],
        "enabled": True,
    },
    # ── HOUSING / TENANCY ─────────────────────────────────────────────────────
    {
        "domain": "mohua.gov.in",
        "title": "Ministry of Housing and Urban Affairs",
        "authority": "Ministry of Housing and Urban Affairs, Government of India",
        "jurisdiction": {"country": "India"},
        "source_type": "act",
        "base_url": "https://mohua.gov.in",
        "search_url": "https://mohua.gov.in/cms/acts-rules.php",
        "domain_keywords": [
            "tenant", "landlord", "rent", "deposit", "eviction",
            "housing", "tenancy", "lease", "rental"
        ],
        "enabled": True,
    },
    # ── DISABLED / NOT YET VALIDATED ─────────────────────────────────────────
    {
        "domain": "ecourts.gov.in",
        "title": "eCourts — District and High Court Case Status",
        "authority": "Supreme Court of India / e-Committee",
        "jurisdiction": {"country": "India"},
        "source_type": "judgment",
        "base_url": "https://ecourts.gov.in",
        "search_url": "https://ecourts.gov.in/ecourts_home/",
        "domain_keywords": ["court", "case status", "hearing", "district court", "high court"],
        "enabled": False,  # Requires structured API; plain fetch not useful
    },
]


def get_enabled_sources() -> List[Dict[str, Any]]:
    """Return only sources marked as enabled."""
    return [s for s in APPROVED_SOURCES if s.get("enabled", False)]


def is_approved_domain(url: str) -> bool:
    """Check if a URL belongs to an approved source domain."""
    enabled = get_enabled_sources()
    for s in enabled:
        if s["domain"] in url:
            return True
    return False
