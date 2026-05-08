# Tracing LLM Applications

> **TL;DR** — Tracing records the full execution tree of an LLM application (every LLM call, tool call, retrieval step) with inputs, outputs, latency, and token counts; it is essential for debugging and cost analysis.

## Overview

An LLM application is a distributed system with non-deterministic components. A single user request may trigger dozens of LLM and tool calls. Without structured tracing, debugging a bad answer requires guessing which step went wrong.

Good tracing gives you:
- **Input/output** at every step
- **Latency** breakdown (where is the time going?)
- **Token costs** per call and per session
- **Error rates** and retry counts
- **Semantic quality scores** linked to specific traces

## Trace Concepts

| Concept | Description |
|---|---|
| **Trace** | The full record of processing a single user request |
| **Span** | A single operation within a trace (one LLM call, one tool call) |
| **Parent/child spans** | Hierarchical structure showing which call triggered which |
| **Attributes** | Key-value metadata attached to a span (model name, token count, user ID) |

## OpenTelemetry for LLMs

The emerging standard is to emit OpenTelemetry (OTel) spans from LLM SDKs. Several projects support this:

- **OpenLLMetry** — OTel instrumentation for LangChain, OpenAI, Qdrant, etc.
- **Langfuse** — Accepts OTel traces via its collector endpoint.
- **Azure Monitor** — Native OTel ingestion.

## LangChain Tracing with Langfuse

```python
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

# Pass handler to any LangChain chain/agent
result = qa_chain.invoke(
    {"query": "What is a Kubernetes Pod?"},
    config={"callbacks": [langfuse_handler]},
)
```

Every LLM call, retrieval step, and tool call inside the chain will be recorded as a span in Langfuse.

## Manual Tracing with Langfuse SDK

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
)

trace = langfuse.trace(name="wiki-qa", user_id="user-123", input={"question": "..."})

span = trace.span(name="retrieve", input={"query": "..."})
docs = retriever.get_relevant_documents("...")
span.end(output={"doc_count": len(docs)})

generation = trace.generation(
    name="generate",
    model="gpt-4.1",
    input=messages,
    output={"answer": "..."},
    usage={"input": 120, "output": 45},
)
trace.update(output={"answer": "..."})
langfuse.flush()
```

## What to Log in Every Span

| Field | Why |
|---|---|
| `model` | Compare models; track migrations |
| `input_tokens` / `output_tokens` | Cost attribution |
| `latency_ms` | Performance baseline |
| `temperature` | Reproducibility |
| `user_id` | Per-user cost and quality analysis |
| `session_id` | Group related turns |
| `error` | Failure analysis |

## References

- [Langfuse Tracing Docs](https://langfuse.com/docs/tracing)
- [OpenLLMetry](https://github.com/traceloop/openllmetry)
- Source: [Langfuse Talk — LLM O11y](../../content/posts/2026-07-01-langfuse-ai-ent.md)
