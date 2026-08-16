# Ecosystem Profiles

Use these to set vocabulary, example services, and technical depth per difficulty level.

## AWS
- **Core services to reference:** Amazon Bedrock (AgentCore, Agents, Knowledge Bases, Guardrails),
  SageMaker, Lambda, ECS/EKS, S3, IAM, Step Functions, API Gateway, CloudWatch.
- **Fundamentals:** what the service is, the managed-vs-self-run trade-off, a single-service demo.
- **Intermediate:** multi-service integration patterns, IAM least-privilege examples, cost levers.
- **Advanced:** Well-Architected Framework trade-offs, multi-region/multi-account patterns,
  event-driven architectures, benchmark numbers (latency, cost per token/invocation).

## GCP
- **Core services:** Vertex AI (Agent Builder, Model Garden), Cloud Run, GKE, BigQuery, Pub/Sub,
  Cloud Functions, IAM.
- **Fundamentals:** managed AI platform basics, serverless-first framing.
- **Intermediate:** Vertex AI pipelines, GKE Autopilot vs Standard, BigQuery ML integration.
- **Advanced:** multi-region Vertex deployments, custom training vs Model Garden trade-offs,
  cost/latency benchmarks vs comparable AWS/Azure services.

## Azure
- **Core services:** Azure OpenAI Service, AKS, Azure Functions, Azure AI Foundry, Cosmos DB,
  Azure API Management.
- **Fundamentals:** Azure OpenAI basics, resource/region availability caveats.
- **Intermediate:** AKS + Azure Functions event-driven patterns, RBAC and Managed Identity.
- **Advanced:** enterprise landing zones, hybrid (Azure Arc) patterns, cost governance at scale.

## Kubernetes / CNCF
- **Core concepts:** CRDs, controllers, reconciliation loops, RBAC, Helm/Kustomize, eBPF (Cilium),
  service mesh (Istio/Linkerd), GitOps (Argo CD/Flux), OpenTelemetry.
- **Fundamentals:** what a controller loop is, basic manifest walkthroughs.
- **Intermediate:** custom controllers/operators, policy engines (Kyverno/OPA), progressive delivery.
- **Advanced:** kernel-level eBPF mechanics, multi-cluster federation, platform-engineering internal
  developer platforms (IDPs), SLO-driven autoscaling.

## Agentic AI & LLM Frameworks
- **Core frameworks:** LangGraph, LangSmith, LangFuse, CrewAI, AutoGen, Model Context Protocol (MCP),
  Strands Agents, Bedrock AgentCore.
- **Fundamentals:** what an "agent loop" is (plan → tool call → observe → repeat), single-agent demo.
- **Intermediate:** multi-agent orchestration patterns, tool/function calling, state graphs, memory.
- **Advanced:** evaluation loops and tracing (LangSmith/LangFuse), context compaction, dynamic tool
  selection, guardrails and human-in-the-loop checkpoints, production failure modes.

## Platform Engineering / DevSecOps
- **Core concepts:** internal developer platforms, golden paths, policy-as-code, supply-chain
  security (SBOM, Sigstore), CI/CD pipeline design.
- **Fundamentals:** why platform engineering exists (cognitive load reduction).
- **Intermediate:** golden-path template design, self-service infra via Terraform/Crossplane.
- **Advanced:** platform metrics (DORA), org-scale adoption strategy, security-shift-left tooling.

## Community/Event Context (for talk decks)
When the deck is explicitly for a community event, adjust framing and the closing CTA slide:
- **AWS re:Invent / AWS Community Day** — CTA slide should reference AWS Builder Center, re:Post,
  and local AWS User Group.
- **KCD (Kubernetes Community Days) / CNCF events** — CTA slide should reference the CNCF Slack,
  the project's own Slack channel, and local CNCF chapter.
- **GDG (Google Developer Groups)** — CTA slide should reference the GDG chapter and Google
  Developer program.
- Generic/internal tech share — CTA slide references the team's own resources instead.
