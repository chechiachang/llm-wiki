# Chapter 04 — LLM Observability

Monitor, trace, and evaluate LLM applications in production.

## Pages

| Page | Description |
|---|---|
| [Tracing](tracing.md) | Structured logging for LLM calls, chains, and agents |
| [Langfuse](langfuse.md) | Open-source LLM observability platform |
| [LLM-as-a-Judge](llm-as-a-judge.md) | Using LLMs to evaluate other LLM outputs |
| [Evaluation](evaluation.md) | Datasets, regression tests, and deployment gates |

## Key Ideas

- Traditional APM is insufficient for LLMs — you need **token counts**, **latency per step**, and **semantic quality** metrics.
- **Langfuse** provides tracing, prompt management, dataset collection, and evaluation dashboards.
- **LLM-as-a-judge** enables scalable automated quality assessment without human labellers.
- An **evaluation dataset** + regression gate prevents quality regressions during model/prompt updates.

> See also: [RAG Evaluation](../02-rag/evaluation.md) | [Agent Patterns](../03-agents/agent-patterns.md)
