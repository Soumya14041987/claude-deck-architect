# Slide Archetypes

Vary layouts deliberately — never repeat the same archetype on two consecutive slides, and never
build an entire deck out of `TitleAndBullets`. Each archetype below names its purpose, its typical
content shape, and a layout note for the generator.

| Archetype | Purpose | Content shape | Layout note |
|---|---|---|---|
| `Title` | Opening slide | Deck title, subtitle, presenter name, event/date | Big bold typography; theme accent as a large background shape, not a stripe |
| `Agenda` | Roadmap | Numbered list of sections, 4-7 items | Two-column if >5 items |
| `ProblemFriction` | Motivate the topic | Before/after or symptom/root-cause | Split-screen layout, contrasting card backgrounds |
| `KeyConcept` | Explain one idea | Concept name + 2-4 supporting points + optional icon | Icon or small diagram anchors one side, text the other |
| `Topology` | Architecture/flow | Rendered Mermaid diagram (flowchart or sequence) + numbered callouts | Diagram fills 60-70% of slide; callouts as a compact side list |
| `DeepDive` | Layer-by-layer breakdown | 3-5 stacked or nested layers with one line each | Vertical stack with subtle depth (shadow), not literal 3D |
| `CodeSpec` | Show config/code | Syntax-highlighted YAML/Python/JSON snippet, ≤15 lines, annotated | Monospace font, dark card even in light theme, line-number gutter optional |
| `Comparison` | Contrast options | 2-3 columns (services, providers, or approaches) with 4-6 aligned attribute rows | Equal-width columns, header row in accent color |
| `Timeline` | Sequence of events/milestones | 3-6 dated or ordered points | Horizontal timeline with alternating label positions |
| `BenchmarkMatrix` | Data-backed trade-offs | Small table or bar chart: latency, cost, throughput | Native pptxgenjs chart, not an image, when the data is numeric |
| `ProductionGotchas` | Battle-tested insights | 3-4 bullets: security, limits, anti-patterns | Numbered cards, not a plain bullet list |
| `Demo` | Walkthrough step | Screenshot placeholder or step list with a call-out | One primary visual, minimal text |
| `Quote` | Case study or testimonial | Short (<25 word) paraphrase + attribution | Large text, generous whitespace, no card border |
| `Resources` | Links | Curated docs + GitHub repos, grouped | Two columns: "Official Docs" / "GitHub & Community" |
| `CallToAction` | Close | 2-3 next steps + contact/social handles + event-specific plug (see ecosystem-profiles.md) | Centered, high-contrast accent background |

## Composition guidance by difficulty

- **Fundamentals:** `Title → Agenda → ProblemFriction → KeyConcept ×2-3 → Topology (simple) → Demo → ProductionGotchas → Resources → CallToAction`
- **Intermediate:** add one `Comparison` and a more detailed `Topology`/`DeepDive` pair; keep `CodeSpec` short and heavily annotated.
- **Advanced:** add `BenchmarkMatrix`, a second `Topology` (e.g. failure-mode variant), and let `CodeSpec`/`DeepDive` carry more technical density.

## Scaling to slide count

- 10 slides: Title, Agenda, 1 ProblemFriction/KeyConcept, 1 Topology, 1 Demo or CodeSpec, 1
  ProductionGotchas, Resources, CallToAction, +1 flex slide.
- 20 slides: full composition above with 2-3 KeyConcept slides, 2 Topology variants, 1 Comparison,
  1 Timeline or BenchmarkMatrix.
- 30 slides: expand KeyConcept to 4-5, add a second Demo/CodeSpec pair, a Quote/case-study slide,
  and a second BenchmarkMatrix or Comparison — never by duplicating an existing slide's content.
