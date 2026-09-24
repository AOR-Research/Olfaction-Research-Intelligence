"""
Olfaction Research Intelligence
Static Page Builder

Renders data/papers.json into a clean, self-contained, iframe-embeddable
HTML page (docs/index.html) for GitHub Pages. Always uses a light theme
(rather than auto-switching with the OS) so it blends consistently into
whatever page it's embedded in (e.g. a WordPress page on aor.social).
"""

import html
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "papers.json"
OUTPUT_FILE = BASE_DIR / "docs" / "index.html"

MAX_ABSTRACT_CHARS = 280
MAX_DISPLAYED = 25  # keep the embedded widget compact; full history stays in data/papers.json

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Olfaction Research Intelligence</title>
<style>
  :root {{
    --bg: #ffffff;
    --card-bg: #ffffff;
    --border: #e5e9ee;
    --text: #1f2937;
    --text-muted: #6b7280;
    --accent: #0f766e;
    --accent-light: #e6f6f4;
    --pillar-bg: #f3f6f9;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 18px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
      Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
  }}
  .ori-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 12px;
    margin-bottom: 14px;
    border-bottom: 2px solid var(--pillar-bg);
  }}
  .ori-header h1 {{
    font-size: 1.15rem;
    margin: 0;
    font-weight: 700;
    color: var(--text);
  }}
  .ori-header .ori-updated {{
    font-size: 0.75rem;
    color: var(--text-muted);
  }}
  .ori-list {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .ori-card {{
    border: 1px solid var(--border);
    background: var(--card-bg);
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  }}
  .ori-card h2 {{
    font-size: 0.98rem;
    margin: 0 0 6px 0;
    font-weight: 600;
    line-height: 1.4;
  }}
  .ori-card h2 a {{
    color: var(--text);
    text-decoration: none;
  }}
  .ori-card h2 a:hover {{
    color: var(--accent);
    text-decoration: underline;
  }}
  .ori-meta {{
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 8px;
  }}
  .ori-abstract {{
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.5;
    margin: 0 0 10px 0;
  }}
  .ori-footer-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .ori-discovered {{
    font-size: 0.72rem;
    color: var(--accent);
    background: var(--accent-light);
    padding: 2px 8px;
    border-radius: 999px;
    display: inline-block;
  }}
  .ori-link {{
    font-size: 0.78rem;
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
  }}
  .ori-link:hover {{ text-decoration: underline; }}
  .ori-empty {{
    text-align: center;
    color: var(--text-muted);
    padding: 40px 0;
    font-size: 0.9rem;
  }}
  .ori-poweredby {{
    text-align: center;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 18px;
  }}
</style>
</head>
<body>
  <div class="ori-header">
    <h1>🔬 Olfaction Research Intelligence</h1>
    <span class="ori-updated">Last updated: {last_updated}</span>
  </div>
  <div class="ori-list">
    {cards}
  </div>
  <div class="ori-poweredby">
    Auto-updated from PubMed &middot; Association for Olfaction Research
  </div>
</body>
</html>
"""

CARD_TEMPLATE = """<div class="ori-card">
  <h2><a href="{pubmed_url}" target="_blank" rel="noopener">{title}</a></h2>
  <div class="ori-meta">{journal} &middot; {publication_date} &middot; PMID {pmid}</div>
  <p class="ori-abstract">{abstract}</p>
  <div class="ori-footer-row">
    <span class="ori-discovered">🕒 Discovered: {discovered_at}</span>
    <a class="ori-link" href="{pubmed_url}" target="_blank" rel="noopener">Read on PubMed &rarr;</a>
  </div>
</div>"""


def _truncate(text: str, limit: int = MAX_ABSTRACT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def build():
    if DATA_FILE.exists():
        papers = json.loads(DATA_FILE.read_text())
    else:
        papers = []

    displayed_papers = papers[:MAX_DISPLAYED]

    if displayed_papers:
        cards_html = "\n    ".join(
            CARD_TEMPLATE.format(
                pubmed_url=html.escape(p.get("pubmed_url", "")),
                title=html.escape(p.get("title", "Untitled")),
                journal=html.escape(p.get("journal", "")),
                publication_date=html.escape(p.get("publication_date", "")),
                pmid=html.escape(str(p.get("pmid", ""))),
                abstract=html.escape(_truncate(p.get("abstract", ""))),
                discovered_at=html.escape(p.get("discovered_at_display", "")),
            )
            for p in displayed_papers
        )
    else:
        cards_html = '<div class="ori-empty">No papers discovered yet. Check back soon.</div>'

    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    now_ist = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Kolkata"))
    last_updated = now_ist.strftime("%d %b %Y, %I:%M %p IST")

    page_html = PAGE_TEMPLATE.format(cards=cards_html, last_updated=last_updated)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(page_html)
    print(
        f"Built {OUTPUT_FILE} showing {len(displayed_papers)} of "
        f"{len(papers)} tracked paper(s)."
    )


if __name__ == "__main__":
    build()
