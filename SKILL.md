---
name: deck-architect
description: "Generates polished, editable slide decks (PPTX + PDF) on any cloud or agentic AI topic — AWS, GCP, Azure, multi-cloud, Kubernetes/CNCF, and agentic AI frameworks (LangGraph, CrewAI, AutoGen, MCP). Invoke with /deck-architect <topic>. Produces context-aware theming, accurate architecture diagrams, curated resources, and varied slide layouts comparable to a human-designed deck. Trigger whenever the user asks for a presentation, slide deck, talk deck, or conference/meetup deck on a cloud, DevOps, platform engineering, or GenAI/agentic-AI subject."
user-invocable: true
disable-model-invocation: false
license: MIT — see LICENSE
---

# Deck Architect

Deck Architect turns a one-line topic into a complete, presentation-ready slide deck: themed to the
cloud provider or ecosystem, backed by accurate architecture diagrams, structured into a sensible
agenda, and populated with curated official docs and GitHub repos — output as a fully editable
`.pptx` (and optionally a high-fidelity `.pdf`).

It is designed for cloud, DevOps, platform-engineering, and agentic-AI content: AWS re:Invent /
AWS Community Day talks, KCD and CNCF meetups, GDG events, and internal tech-share decks.

## When to use this skill

Use this skill whenever the user:
- Types `/deck-architect <topic>`
- Asks for a "slide deck", "presentation", "talk deck", or "PPTX" on a cloud, Kubernetes/CNCF,
  DevOps, platform engineering, or GenAI/agentic-AI topic
- Names a specific service or framework and asks for a deck about it (Bedrock AgentCore,
  LangGraph, Vertex AI, AKS, MCP, etc.)

Do **not** use this for general-purpose, non-technical presentations (e.g. a wedding slideshow,
a sales pitch deck with no technical content) — those are better served by the base `pptx` skill
without this skill's cloud/agentic-AI theming and diagram logic.

## Step 0 — Load supporting context first

Before generating anything, read in this order:

1. `references/themes.md` — the full theme/palette table (provider colors, fonts, dark/light variants)
2. `references/ecosystem-profiles.md` — technical depth and terminology per ecosystem
3. `references/slide-archetypes.md` — the layout palette to vary slides against
4. `data/topics.json` — curated resource links (official docs, GitHub repos) per topic, used as a
   starting point and supplemented with live web search for anything missing or possibly stale
5. The base `pptx` skill (`/mnt/skills/public/pptx/SKILL.md` on Claude Code/Desktop with the
   Anthropic-provided skills, or the vendored copy of that guidance in `references/pptx-notes.md`
   if unavailable) — it has the authoritative `pptxgenjs` gotchas, QA steps, and file-conversion
   commands. This skill's `scripts/build_deck.py` already encodes those gotchas, but re-check this
   reference if you hand-edit the generated deck.

## Step 1 — Interactive intake

When invoked as `/deck-architect <topic>` with no other parameters, ask the clarifying questions
below **in a single combined prompt** (not one at a time) unless the user's invocation already
answered some of them inline (e.g. `/deck-architect LangGraph + LangSmith (20 slides, advanced,
AWS+GCP, PPTX+PDF)` skips straight to Step 2).

1. **Slide count** — 10 / 20 / 30 (default 15 if unanswered after one nudge)
2. **Cloud provider(s)** — AWS / GCP / Azure / Multi-cloud / Not cloud-specific (CNCF, agentic AI
   frameworks, etc.)
3. **Difficulty level** — Fundamentals / Intermediate / Advanced
4. **Output format** — PPTX / PDF / Both

If the topic name alone makes an answer obvious (e.g. "AWS Bedrock AgentCore" implies AWS), infer
it and only ask about the remaining unknowns — state the inferred value rather than asking about
it. Never block indefinitely: if the user gives a vague or partial answer, pick sensible defaults
(15 slides, Intermediate, PPTX) and proceed rather than re-prompting more than once.

## Step 2 — Resolve theme and content plan

1. Map the topic and chosen provider(s) to a theme from `references/themes.md`. Multi-cloud topics
   use the `multi-cloud` theme (neutral base with accent chips per provider mentioned).
2. Map the topic to the closest ecosystem profile(s) in `references/ecosystem-profiles.md` to set
   vocabulary and technical depth.
3. Pull starting resource links from `data/topics.json`. If the topic isn't in that file, or the
   entries look stale, run web searches for: (a) the current official documentation landing page,
   (b) 2-3 actively maintained GitHub repos, (c) one recent (last 12 months) real-world case study
   or benchmark. Never fabricate a URL — omit a resource category rather than invent a link.
4. Break multi-part or vague topics (e.g. "Agentic AI on AWS") into sub-sections that map cleanly
   onto slides — don't try to cover everything shallowly.
5. Draft a slide-by-slide outline before writing content: title → agenda → intro/why-it-matters →
   key concepts (2-4 slides) → architecture (1-3 slides, varying diagram type) → demo/workflow →
   best practices/production gotchas → benchmark or comparison (Advanced only, optional at other
   levels) → resources → Q&A/CTA. Scale the middle sections to hit the requested slide count —
   never pad with filler slides or repeat a layout back-to-back.

## Step 3 — Generate architecture diagrams

Produce one Mermaid diagram per architecture slide describing the actual service/flow topology
(not a generic box-and-arrow placeholder) — see `references/diagram-guide.md` for the per-provider
node vocabulary and layout conventions (flowchart for request/data flow, sequence diagram for
multi-agent or API call ordering). Render each Mermaid diagram to a transparent-background PNG
using `scripts/render_mermaid.py` before placing it — pptxgenjs cannot render Mermaid source
directly, and diagrams belong on the slide as clean vector-quality images, not as a rendering of
the Mermaid code block.

## Step 4 — Build the deck

Run `scripts/build_deck.py` with a JSON content plan (schema in `references/content-plan-schema.md`)
rather than hand-writing pptxgenjs calls inline — the script already implements the theme engine,
archetype layouts, speaker-notes injection, and the `pptxgenjs` footguns documented in the base
`pptx` skill (EMU coordinate limits, hex-color rules, shadow offsets, chart label configuration).

```bash
python3 scripts/build_deck.py --plan /tmp/deck_plan.json --out /mnt/user-data/outputs/<slug>.pptx
```

The script also accepts `--pdf` to additionally emit a high-fidelity PDF via the LibreOffice
conversion path used by the base `pptx` skill.

If no network access is available when resolving resources or diagrams, fall back to the cached
theme/archetype/resource data already in `data/` and `references/` — do not block deck generation
on a failed web search; note in the resources slide that links should be verified.

## Step 5 — QA (required, do not skip)

1. Run `markitdown <deck>.pptx` and check for missing content, leftover placeholder text
   (`grep -iE "lorem|ipsum|TODO|\[insert"`), and wrong slide order.
2. Run the base `pptx` skill's `scripts/office/validate.py <deck>.pptx` for schema/relationship/
   chart validation.
3. Convert to images (`soffice.py --convert-to pdf` then `pdftoppm`) and visually inspect every
   slide for overflow, overlap, low-contrast text, and inconsistent spacing — see the base `pptx`
   skill's QA checklist for the full list of defects to check.
4. Fix issues in the content plan / generator, not by hand-editing the packed XML, and re-render
   only the slides that changed.

## Step 6 — Deliver

Copy the final `.pptx` (and `.pdf` if requested) to `/mnt/user-data/outputs/` and present both
files. Log the generated deck's topic, theme, and slide count to `data/history.jsonl` (one JSON
object per line) so repeat invocations on related topics can reuse prior resource research.

## Sample invocations

```
/deck-architect AWS Bedrock AgentCore
/deck-architect LangGraph + LangSmith (20 slides, advanced, AWS+GCP, PPTX+PDF)
/deck-architect Platform Engineering with CNCF tooling (fundamentals)
/deck-architect Azure OpenAI vs Amazon Bedrock (comparison, 15 slides)
```

## Troubleshooting

See `references/troubleshooting.md` for font-rendering fallbacks, GitHub API rate-limit handling,
Mermaid render failures, and offline-mode behavior.
