"""
Olfaction Research Intelligence
Main orchestrator

Run by GitHub Actions on a schedule (and locally for testing):
1. Load previously discovered papers from data/papers.json
2. Search PubMed for the current query, find genuinely new papers
3. Fetch details for new papers, tag them with a discovery timestamp
4. Merge + sort (newest discovered first), save back to data/papers.json
5. Rebuild docs/index.html (the embeddable static page)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from pipeline.build_page import build as build_page
from pipeline.pubmed_collector import fetch_articles, search_pubmed

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "papers.json"


def load_existing():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def save(papers):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(papers, indent=2, ensure_ascii=False))


def main():
    print("=" * 70)
    print("Checking PubMed for new olfaction research...")
    print("=" * 70)

    existing_papers = load_existing()
    existing_pmids = {str(p["pmid"]) for p in existing_papers}
    print(f"Already discovered: {len(existing_papers)}")

    found_pmids = search_pubmed()
    print(f"PubMed search returned: {len(found_pmids)} papers")

    genuinely_new_pmids = [
        pmid for pmid in found_pmids if str(pmid) not in existing_pmids
    ]
    print(f"Genuinely new papers this check: {len(genuinely_new_pmids)}")

    if genuinely_new_pmids:
        new_articles = fetch_articles(genuinely_new_pmids)

        discovered_at_utc = datetime.now(timezone.utc).isoformat()
        discovered_at_display = (
            datetime.now(timezone.utc)
            .astimezone(ZoneInfo("Asia/Kolkata"))
            .strftime("%d %b %Y, %I:%M %p IST")
        )

        for article in new_articles:
            article["pmid"] = str(article["pmid"])
            article["discovered_at"] = discovered_at_utc
            article["discovered_at_display"] = discovered_at_display

        all_papers = new_articles + existing_papers
        print(f"Added {len(new_articles)} new paper(s).")
    else:
        all_papers = existing_papers
        print("No genuinely new papers this check.")

    # Newest-discovered-first
    all_papers.sort(key=lambda p: p.get("discovered_at", ""), reverse=True)

    save(all_papers)
    print(f"\nTotal papers tracked: {len(all_papers)}")

    build_page()


if __name__ == "__main__":
    main()
