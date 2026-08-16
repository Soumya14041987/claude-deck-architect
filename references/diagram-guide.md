# Architecture Diagram Guide

Diagrams are authored in Mermaid, then rasterized to a themed transparent PNG via
`scripts/render_mermaid.py` before being placed on a slide — `pptxgenjs` cannot render Mermaid
source natively, and a diagram screenshot of raw code is not an acceptable substitute for a real
architecture visual.

## Source every topology from the web before drawing it (required, do not skip)

Never draw an architecture diagram from memory alone. Before writing the Mermaid source for any
`Topology` slide:

1. Run a web search for the **official** reference architecture: AWS → the AWS Architecture
   Center / service doc "how it works" diagram on `docs.aws.amazon.com` or `aws.amazon.com/architecture`;
   GCP → the Google Cloud Architecture Center on `cloud.google.com/architecture`; Azure → the
   Azure Architecture Center on `learn.microsoft.com/azure/architecture`; Kubernetes/CNCF/agentic
   frameworks → the project's own docs or GitHub README architecture section.
2. Reproduce that topology's real components, direction of data flow, and trust boundaries in
   Mermaid — component names must match the vendor's current naming (services get renamed; verify
   rather than reuse a name from training data).
3. Note the source URL in the slide's `notes` field (speaker notes), so the deck is defensible in
   Q&A and the audience can verify it themselves.
4. If no official diagram exists for a niche or very new topic, compose the topology from the
   product's documented API/service list instead of inventing boxes, and say so in speaker notes
   ("no official reference architecture published as of <date>; composed from service docs").

This applies to every `Topology` slide, not just the first — an "AgentCore reference architecture"
slide and a later "AgentCore failure-mode" slide each need their own accuracy pass.

## Diagram type by content

- **Request/data flow between services** → `flowchart LR` (left-to-right) or `flowchart TD`
  (top-down) for layered architectures.
- **Multi-agent or multi-step API call ordering** → `sequenceDiagram`.
- **State machines (agent loops, CI/CD pipeline stages)** → `stateDiagram-v2`.
- **Service comparison / decision trees** → `flowchart` with diamond decision nodes.

## Node vocabulary by provider (keep icon/label accurate — do not invent services)

- **AWS:** label nodes with the exact service name (e.g. "Amazon Bedrock AgentCore", "AWS Lambda",
  "Amazon S3", "Amazon ECS/Fargate") — never abbreviate below what a re:Invent audience would
  recognize instantly.
- **GCP:** "Vertex AI Agent Builder", "Cloud Run", "GKE Autopilot", "BigQuery", "Pub/Sub".
- **Azure:** "Azure OpenAI Service", "Azure Kubernetes Service (AKS)", "Azure Functions", "Azure
  API Management".
- **Kubernetes/CNCF:** actual object kinds (Deployment, CRD, Controller, Ingress) and real project
  names (Argo CD, Cilium, Istio) — never a generic "Service A/B/C" placeholder.
- **Agentic AI:** name the actual framework primitive (LangGraph `StateGraph`, CrewAI `Crew`/`Agent`,
  AutoGen `GroupChat`, MCP `Server`/`Client`/`Tool`) rather than a generic "Agent" box when the
  topic is framework-specific.

## Styling

`render_mermaid.py --theme <theme-name>` applies the active theme's accent pair to node fills and
edge strokes, sets a transparent background, and exports at 2x scale for crisp placement at up to
half-slide width. Always pass the theme resolved in Step 2 of `SKILL.md` so diagrams match the
rest of the deck.

## Fallback

If `mmdc` (Mermaid CLI) is unavailable or a render fails, fall back to a manually composed SVG
using the shape/arrow primitives in `scripts/render_mermaid.py --fallback-svg`, which draws a
simplified box-and-arrow version of the same node list — better than omitting the diagram or
leaving raw Mermaid text on a slide.
