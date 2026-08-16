# Content Plan Schema

`scripts/build_deck.py` consumes a single JSON file describing the whole deck. Build this plan in
Step 2-3 of `SKILL.md` before calling the script — do not hand-write pptxgenjs calls inline.

```json
{
  "title": "Amazon Bedrock AgentCore: From Zero to Production",
  "subtitle": "Building governed, observable agentic workflows on AWS",
  "presenter": "Soumya",
  "event": "AWS Community Day Kolkata 2026",
  "theme": "aws-orange",
  "mode": "dark",
  "level": "intermediate",
  "format": ["pptx", "pdf"],
  "slides": [
    {
      "archetype": "Title",
      "title": "Amazon Bedrock AgentCore",
      "subtitle": "From Zero to Production",
      "notes": "Speaker note text for this slide."
    },
    {
      "archetype": "Agenda",
      "title": "Agenda",
      "items": ["Why agentic AI on AWS", "AgentCore architecture", "Live workflow", "Production guardrails", "Resources"]
    },
    {
      "archetype": "Topology",
      "title": "AgentCore Reference Architecture",
      "mermaid": "flowchart LR\n  A[Amazon Bedrock AgentCore] --> B[AWS Lambda Tooling]\n  B --> C[Amazon S3]\n  A --> D[Amazon Bedrock Guardrails]",
      "callouts": ["Guardrails enforce policy before tool execution", "Lambda tools are least-privilege scoped per agent"],
      "notes": "..."
    },
    {
      "archetype": "Comparison",
      "title": "AgentCore vs. Self-Managed Orchestration",
      "columns": [
        {"name": "Bedrock AgentCore", "rows": ["Managed", "Built-in guardrails", "AWS-native IAM"]},
        {"name": "Self-managed (LangGraph on ECS)", "rows": ["Full control", "Manual guardrail wiring", "Custom IAM policies"]}
      ]
    },
    {
      "archetype": "Resources",
      "title": "Go Deeper",
      "docs": [{"label": "Bedrock AgentCore Docs", "url": "https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html"}],
      "repos": [{"label": "aws-samples/bedrock-agentcore-examples", "url": "https://github.com/aws-samples"}]
    }
  ]
}
```

## Field notes

- `theme` — one of the theme keys in `references/themes.md`; `mode` is `dark` or `light`.
- Every slide object needs `archetype` and `title`. Archetype-specific fields:
  - `Agenda`/`ProductionGotchas`: `items` (string array)
  - `Topology`: `mermaid` (raw Mermaid source, rendered by `render_mermaid.py` before build) and
    optional `callouts`
  - `Comparison`: `columns` (array of `{name, rows}`, same row count per column)
  - `CodeSpec`: `language`, `code` (string, ≤15 lines)
  - `BenchmarkMatrix`: `chart_type` (`bar`/`line`/`table`), `categories`, `series`
  - `Timeline`: `items` (array of `{label, date}`)
  - `Resources`: `docs`, `repos` (arrays of `{label, url}`) — every `url` must be a real link found
    via `data/topics.json` or a live search; never fabricated
  - `Quote`: `text` (≤25 words, paraphrased — never a verbatim copyrighted quote), `attribution`
  - `CallToAction`: `items` (next steps), `handles` (social/contact array)
- `notes` (optional on any slide) becomes the PPTX speaker note via `addNotes()`.
