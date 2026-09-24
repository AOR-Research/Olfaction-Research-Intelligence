"""
Olfaction Research Intelligence
PubMed Collector

Searches PubMed for recent olfaction-related research spanning the
Association for Olfaction Research's five pillars (Smell, Sensors,
Signal, Simulation, Systems), and fetches article details.
"""

import time
import xml.etree.ElementTree as ET

import requests

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

SEARCH_QUERY = (
    # Block A - core smell / olfaction science (the "Smell" pillar)
    '(olfaction[Title/Abstract] OR olfactory[Title/Abstract] OR '
    'smell[Title/Abstract] OR odor[Title/Abstract] OR odour[Title/Abstract] OR '
    'chemosensation[Title/Abstract] OR '
    '"volatile organic compound"[Title/Abstract] OR '
    '"volatile organic compounds"[Title/Abstract]) '
    'AND '
    # Block B - olfaction-specific tech/computation (Sensors, Signal,
    # Simulation, Systems pillars). Deliberately excludes bare
    # "machine learning" / "artificial intelligence" / "deep learning",
    # which matched too many unrelated papers that only mention smell
    # in passing (e.g. a genomics paper naming an olfactory receptor
    # gene). Every term here ties the technology directly to olfaction.
    '(sensor[Title/Abstract] OR biosensor[Title/Abstract] OR '
    '"electronic nose"[Title/Abstract] OR "e-nose"[Title/Abstract] OR '
    '"gas sensor"[Title/Abstract] OR "gas sensors"[Title/Abstract] OR '
    '"artificial olfaction"[Title/Abstract] OR '
    '"digital olfaction"[Title/Abstract] OR '
    '"computational olfaction"[Title/Abstract] OR '
    '"machine olfaction"[Title/Abstract] OR '
    '"odor recognition"[Title/Abstract] OR "odour recognition"[Title/Abstract] OR '
    '"odor prediction"[Title/Abstract] OR "odour prediction"[Title/Abstract] OR '
    '"scent detection"[Title/Abstract] OR "olfactory receptor"[Title/Abstract] OR '
    '"chemical sensor"[Title/Abstract] OR "chemical sensor array"[Title/Abstract] OR '
    '"signal processing"[Title/Abstract])'
)

MAX_RESULTS = 100


def search_pubmed(query: str = SEARCH_QUERY, max_results: int = MAX_RESULTS):
    """Return a list of PMIDs matching the query, most recent first."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "most+recent",
        "retmode": "json",
    }
    resp = requests.get(f"{EUTILS_BASE}/esearch.fcgi", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def _text(elem, path, default=""):
    node = elem.find(path)
    if node is not None and node.text:
        return node.text.strip()
    return default


def fetch_articles(pmids):
    """Fetch title/abstract/journal/date/authors for a list of PMIDs."""
    if not pmids:
        return []

    articles = []
    batch_size = 50

    for i in range(0, len(pmids), batch_size):
        batch = pmids[i : i + batch_size]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml",
        }
        resp = requests.get(f"{EUTILS_BASE}/efetch.fcgi", params=params, timeout=60)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        for article_elem in root.findall(".//PubmedArticle"):
            pmid = _text(article_elem, ".//PMID")
            title = _text(article_elem, ".//ArticleTitle")

            abstract_parts = [
                (node.text or "").strip()
                for node in article_elem.findall(".//AbstractText")
            ]
            abstract = " ".join(p for p in abstract_parts if p)

            journal = _text(article_elem, ".//Journal/Title")

            year = _text(article_elem, ".//JournalIssue/PubDate/Year")
            month = _text(article_elem, ".//JournalIssue/PubDate/MonthName") or _text(
                article_elem, ".//JournalIssue/PubDate/Month"
            )
            day = _text(article_elem, ".//JournalIssue/PubDate/Day")
            pub_date_parts = [p for p in [year, month, day] if p]
            publication_date = " ".join(pub_date_parts)

            authors = []
            for author in article_elem.findall(".//AuthorList/Author"):
                last = _text(author, "LastName")
                initials = _text(author, "Initials")
                if last:
                    authors.append(f"{last} {initials}".strip())
            authors_str = ", ".join(authors[:5])
            if len(authors) > 5:
                authors_str += " et al."

            doi = ""
            for eid in article_elem.findall(".//ArticleIdList/ArticleId"):
                if eid.attrib.get("IdType") == "doi":
                    doi = (eid.text or "").strip()

            articles.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "publication_date": publication_date,
                    "authors": authors_str,
                    "doi": doi,
                    "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                }
            )

        time.sleep(0.4)  # be polite to NCBI's rate limits

    return articles
