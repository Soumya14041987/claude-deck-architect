# Themes & Color Palettes

Each theme defines a **light** and **dark** variant. Pick dark by default for technical/meetup
decks; use light for executive/whitepaper-style requests, or when the user asks for "light mode."
All hex values are given WITHOUT the `#` prefix, matching pptxgenjs's requirement.

| Theme | Trigger | Background (dark) | Background (light) | Primary Accent | Secondary Accent | Code/Card BG (dark) | Font Family |
|---|---|---|---|---|---|---|---|
| `aws-orange` | AWS-only topics | `232F3E` | `FFFFFF` | `FF9900` (AWS Orange) | `1EC9E8` (Sky) | `141D2B` | `Amazon Ember`, fallback `Arial` |
| `gcp-multi` | GCP-only topics | `1A1C23` | `FFFFFF` | `4285F4` (Google Blue) | `34A853` (Google Green) | `24262E` | `Google Sans`, fallback `Arial` |
| `azure-electric` | Azure-only topics | `0B192C` | `FFFFFF` | `0078D4` (Azure Blue) | `50E6FF` (Ice) | `001122` | `Segoe UI`, fallback `Arial` |
| `cncf-teal` | Kubernetes/CNCF topics | `0F172A` | `FFFFFF` | `326CE5` (K8s Blue) | `00A7B5` (CNCF Teal) | `1E293B` | `Inter`, fallback `Arial` |
| `cyber-neon` | Agentic AI / LLM / MCP topics (no single cloud) | `0B132B` | `FFFFFF` | `00EBFF` (Cyan) | `7000FF` (Purple) | `030712` | `Inter`, fallback `Arial` |
| `multi-cloud` | Two or more providers named | `1A1B22` | `FFFFFF` | `8C8C8C` (Neutral) | *(provider accent chips, one per mentioned provider, used only on the comparison/architecture slides)* | `24252C` | `Inter`, fallback `Arial` |
| `light-editorial` | Explicit "light mode" / executive request | `FAFAFA` | `FAFAFA` | `0F172A` (Ink) | `2563EB` (Cobalt) | `F1F5F9` | `Inter`, fallback `Arial` |

Provider accent chips for `multi-cloud` comparison rows: AWS `FF9900`, GCP `4285F4`, Azure `0078D4`.

## Application rules

- Title/section-header text: primary accent on dark background, or ink (`0F172A`) on light background.
- Body text: `E6E6E6` on dark backgrounds, `1A1A1A` on light backgrounds — never pure white/black
  (harsh contrast reads as unfinished).
- Never default to warm-neutral/cream backgrounds (`F5F5DC`, `FAF0E6`, etc.) — use `FFFFFF` for
  light mode.
- Diagrams: render Mermaid with a transparent background and recolor nodes/edges to match the
  active theme's accent pair before embedding (see `scripts/render_mermaid.py --theme`).
- Keep one accent pair per deck — do not mix `aws-orange` accents into a `gcp-multi` deck even on
  a "vs." comparison slide; use the `multi-cloud` provider chips for that instead.
