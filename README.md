# Olfaction Research Intelligence

An auto-updating PubMed literature tracker for olfaction research, built
for the [Association for Olfaction Research](https://aor.social) — spanning
its five pillars: **Smell, Sensors, Signal, Simulation, Systems**.

## How it works

- A GitHub Actions workflow (`.github/workflows/update.yml`) runs every 6
  hours, searching PubMed for new papers matching an olfaction + sensing/
  computation query.
- Genuinely new papers are appended to `data/papers.json` (the full,
  accumulating history) with a discovery timestamp.
- A clean, self-contained static page is rebuilt at `docs/index.html`,
  showing the latest 25 discoveries.
- GitHub Pages serves `docs/index.html`, which can be embedded anywhere via
  `<iframe>`.

## Local development

```bash
pip install -r requirements.txt
python main.py                       # run a check + rebuild the page
python3 -m http.server 8600 --directory docs   # preview locally
```

## Files

- `pipeline/pubmed_collector.py` — PubMed search + article fetch
- `pipeline/build_page.py` — renders `docs/index.html` from `data/papers.json`
- `main.py` — orchestrates a check-and-build run
- `data/papers.json` — accumulating discovery log (source of truth)
- `docs/index.html` — the embeddable static page (served via GitHub Pages)
