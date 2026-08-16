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

**Portable by design:** this file is plain agent instructions plus two CLI scripts
(`scripts/build_deck.py`, `scripts/deck_engine.js`). Any agentic IDE or assistant that can read a
Markdown instruction file and run shell commands can drive this skill, not just Claude Code/Desktop
— see `README.md` → "Using this skill in other agentic IDEs" for Cursor, Kiro, VS Code
(Copilot Chat/Continue/Cline), PyCharm AI Assistant, and similar tools.

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

Use a structured prompt with pre-defined dropdown-style options so the user can choose quickly:

1. **Cloud provider** — AWS / GCP / Azure / Multi-cloud / Kubernetes & CNCF / Agentic AI / GenAI / Other
2. **Target audience or meetup context** — AWS Community Day / AWS re:Invent / KCD / CNCF / GDG / Internal tech share / Conference keynote / Executive briefing / Other
3. **Slide count** — 10 / 15 / 20 / 30 / 40 / 50 (default 15 if unanswered after one nudge)
4. **Diagram style** — Architecture diagram / Workflow diagram / Pipeline diagram / Mixed / No diagram
5. **Difficulty level** — Fundamentals / Intermediate / Advanced
6. **Output format** — PPTX / PDF / Both
7. **Speaker info for the `Speaker` slide** — a LinkedIn profile URL (preferred), or "skip". If the
   user gives no answer after one nudge, skip the `Speaker` slide entirely rather than blocking.

If the topic name alone makes an answer obvious (e.g. "AWS Bedrock AgentCore" implies AWS), infer
it and only ask about the remaining unknowns — state the inferred value rather than asking about
it. Never block indefinitely: if the user gives a vague or partial answer, pick sensible defaults
(15 slides, Intermediate, PPTX, mixed diagram style) and proceed rather than re-prompting more than once.

### Step 1a — Sourcing the Speaker slide from LinkedIn

If the user gave a LinkedIn URL, use available web tools (`WebFetch`/`WebSearch`) to pull the
public profile's name, current headline/role, and About summary. LinkedIn frequently blocks
unauthenticated scraping — if the fetch is empty, blocked, or returns a login wall, do not guess
or fabricate a bio: fall back to asking the user directly for name, role, and a 2-3 sentence bio,
or ask them to paste the profile text. Never invent job titles, employers, or accomplishments.
Paraphrase whatever source text you do get — don't copy a LinkedIn About section verbatim onto a
slide. Only use a headshot image if the user supplies one directly (as a local file path); never
hotlink or scrape a LinkedIn CDN photo URL.

## Step 2 — Resolve theme and content plan

1. Map the topic and chosen provider(s) to a theme from `references/themes.md`. Multi-cloud topics
   use the `multi-cloud` theme (neutral base with accent chips per provider mentioned).
2. Map the topic to the closest ecosystem profile(s) in `references/ecosystem-profiles.md` to set
   vocabulary and technical depth.
3. Pull starting resource links from `data/topics.json`. If the topic isn't in that file, or the
   entries look stale, run web searches for: (a) the current official documentation landing page,
   (b) 2-3 actively maintained GitHub repos, (c) one recent (last 12 months) real-world case study
   or benchmark. Never fabricate a URL — omit a resource category rather than invent a link.
4. Identify the 2-3 real competing tools/services/approaches for the `Comparison` slide's scenario
   (e.g. topic "kagent" → compare against k8sgpt and a plain kubectl+LLM copilot workflow; topic
   "Bedrock AgentCore" → compare against self-managed LangGraph-on-ECS). Web-search each
   competitor's current docs/changelog to source the comparison rows accurately — do not compare
   against a strawman or an outdated feature set.
5. Break multi-part or vague topics (e.g. "Agentic AI on AWS") into sub-sections that map cleanly
   onto slides — don't try to cover everything shallowly.
6. Draft a slide-by-slide outline before writing content: title → agenda → [speaker, if provided]
   → **problem statement (`ProblemFriction`, always slide 3 — never skip, never lead with
   "what is X" instead)** → key concepts (2-4 slides) → architecture (1-3 slides, varying diagram
   type, each sourced per `references/diagram-guide.md`) → demo/workflow → **comparison (always
   included, scenario-based — see point 4)** → best practices/production gotchas → benchmark
   (Advanced only, optional at other levels) → resources → Q&A/CTA. Scale the middle sections to
   hit the requested slide count — never pad with filler slides or repeat a layout back-to-back.
   See `references/slide-archetypes.md` → "Mandatory slides" for the full rule.

## Step 3 — Generate architecture diagrams

Before drawing anything, **web-search the official architecture diagram** for the topic (AWS
Architecture Center, GCP Architecture Center, Azure Architecture Center, or the project's own docs
— see `references/diagram-guide.md` → "Source every topology from the web before drawing it",
which is a required step, not optional). Then produce one Mermaid diagram per architecture slide
describing that real service/flow topology (not a generic box-and-arrow placeholder), using the
per-provider node vocabulary and layout conventions in the same reference (flowchart for
request/data flow, sequence diagram for multi-agent or API call ordering). Cite the source URL in
the slide's speaker notes. Render each Mermaid diagram to a transparent-background PNG using
`scripts/render_mermaid.py` before placing it — pptxgenjs cannot render Mermaid source directly,
and diagrams belong on the slide as clean vector-quality images, not as a rendering of the Mermaid
code block.

## Step 4 — Build the deck

Before the first build in a fresh checkout, confirm dependencies are installed — `deck_engine.js`
requires `pptxgenjs` (`npm install` if `node_modules/` is missing) and `build_deck.py` requires the
packages in `requirements.txt` (`pip install -r requirements.txt`). Skip this check if `node_modules/`
already exists.

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
/deck-architect kagent for Kubernetes troubleshooting (speaker: linkedin.com/in/yourprofile)
```

## Troubleshooting

See `references/troubleshooting.md` for font-rendering fallbacks, GitHub API rate-limit handling,
Mermaid render failures, and offline-mode behavior.
