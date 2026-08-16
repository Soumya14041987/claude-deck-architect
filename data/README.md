# data/

- `themes.json` — machine-readable palette data consumed by `scripts/deck_engine.js` and `scripts/render_mermaid.py`.
- `topics.json` — curated, verified official-docs and GitHub-repo links per topic, used as a starting point during deck generation (supplemented with live search for anything missing or possibly stale). Refresh with `scripts/fetch_resources.py`.
- `history.jsonl` — append-only log of generated decks (title, theme, level, slide count, output path), written by `scripts/build_deck.py`. Starts empty.
