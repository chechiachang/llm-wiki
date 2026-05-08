# Chapter 05 — Deployment

Running LLM applications reliably in production on Azure and Kubernetes.

## Pages

| Page | Description |
|---|---|
| [Azure OpenAI](azure-openai.md) | Provisioning, rate limits, private endpoints, deployments |
| [Kubernetes](kubernetes.md) | Deploying RAG/agent workloads on K8s; Qdrant on K8s |

## Key Ideas

- Azure OpenAI provides enterprise-grade data privacy (your data does not train OpenAI models).
- **Quotas and rate limits** are the most common production pain point — plan ahead.
- Qdrant and other vector stores run well on Kubernetes with persistent volumes.
- Use Kubernetes `HorizontalPodAutoscaler` + queue-based scaling for bursty LLM workloads.

> See also: [Tracing](../04-observability/tracing.md) | [RAG Introduction](../02-rag/introduction.md)
