# Troubleshooting

## Font rendering
- **Symptom:** Theme font (e.g. "Amazon Ember", "Google Sans", "Segoe UI") doesn't render as
  expected in preview or on a machine without that font installed.
- **Fix:** Every theme's font declaration includes a fallback (`Arial`) in `references/themes.md`.
  `build_deck.py` always sets both the primary and fallback via pptxgenjs's font list — PowerPoint
  substitutes automatically if the primary isn't installed. Don't hand-edit slide XML to force a
  font; fix the theme mapping instead.

## GitHub API rate limits
- **Symptom:** `scripts/fetch_resources.py` (used to refresh `data/topics.json`) returns 403 with
  `X-RateLimit-Remaining: 0`.
- **Fix:** The script backs off using the `Retry-After`/`X-RateLimit-Reset` header automatically.
  For repeated local runs, set a `GITHUB_TOKEN` environment variable to raise the unauthenticated
  60/hour limit to 5,000/hour. If no token is available, fall back to the cached `data/topics.json`
  entries — do not block deck generation on a live fetch.

## Mermaid render failures
- **Symptom:** `scripts/render_mermaid.py` fails because `mmdc` (Mermaid CLI) isn't installed or
  headless Chromium can't launch in the sandbox.
- **Fix:** Run `npm install -g @mermaid-js/mermaid-cli` once, or let the script fall back to
  `--fallback-svg`, which draws a simplified box-and-arrow version of the same node list using
  Pillow/SVG primitives — still themed and clean, just less automatically laid out.

## Offline usage
- All theme, archetype, and profile data needed for generation lives in `references/` and `data/`
  as static files — no network call is required to build a deck. Network is only used to refresh
  `data/topics.json` resource links or fetch a fresh benchmark stat; both fail gracefully to the
  cached data.

## PPTX won't open / reports corrupt
- Run `python scripts/office/validate.py <deck>.pptx` from the base `pptx` skill — every failure
  it reports names its fix (most commonly a chart's `dataLabelPosition` on a stacked chart, or a
  missing `valAxes`/`catAxes` pair on a combo chart). Fix it in `build_deck.py`'s chart-building
  function and regenerate; never hand-patch the packed XML.

## Text overflow on generated slides
- `build_deck.py` auto-shrinks body text one step (e.g. 18pt → 16pt) if the content plan's text
  exceeds the archetype's expected line count, but very long `CodeSpec` snippets or `Comparison`
  rows can still overflow. Split the offending slide's content plan entry across two slides rather
  than shrinking further — below 12pt is illegible on a projector.
