# Langfuse

> **TL;DR** — Langfuse is an open-source LLM observability platform providing tracing, prompt management, dataset management, and evaluation dashboards; it can be self-hosted on Kubernetes or used as a managed cloud service.

## Overview

Langfuse fills the gap between generic APM tools (which don't understand LLM concepts) and the need to monitor LLM quality, cost, and reliability. It provides:

- **Tracing** — Capture every LLM call, retrieval, and tool invocation with full I/O.
- **Prompt Management** — Version and A/B test prompts without code deploys.
- **Datasets** — Collect production examples to build evaluation datasets.
- **Evaluations** — Run LLM-as-a-judge or human scores linked to traces.
- **Dashboards** — Token cost, latency, error rate, quality scores over time.

## Architecture

```
Your Application
     │
     │  SDK (Python / TS / OTel)
     ▼
Langfuse Server  ──► PostgreSQL (traces, prompts, datasets)
     │           ──► ClickHouse (analytics)
     ▼
Langfuse UI (web dashboard)
```

Self-host on Kubernetes with the official Helm chart, or use <https://cloud.langfuse.com>.

## Self-Hosting with Docker Compose

```yaml
# docker-compose.yaml (minimal)
services:
  langfuse-server:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://langfuse:secret@db:5432/langfuse
      NEXTAUTH_SECRET: change-me-32-chars
      SALT: change-me-32-chars
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: langfuse
```

## Python SDK Integration

```bash
pip install langfuse
```

```python
import os
from langfuse import Langfuse
from langfuse.openai import openai  # drop-in replacement that auto-traces

# Configure via env vars
# LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

response = openai.chat.completions.create(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    messages=[{"role": "user", "content": "Explain Kubernetes namespaces"}],
)
# ↑ Automatically traced in Langfuse — no other code needed
```

## Prompt Management

```python
langfuse = Langfuse()

# Fetch the production prompt (cached locally)
prompt = langfuse.get_prompt("wiki-qa-system")
compiled = prompt.compile(context="...", question="...")

response = openai.chat.completions.create(
    model=...,
    messages=[{"role": "system", "content": compiled}],
    langfuse_prompt=prompt,  # links trace to prompt version
)
```

Update the prompt in the Langfuse UI → instant rollout to all running instances, no code deploy.

## Building an Evaluation Dataset from Production Traces

1. In the Langfuse UI, filter traces by low quality scores or manual flags.
2. Add selected traces to a **dataset** (input + expected output).
3. Run automated evaluations against the dataset on each code change.
4. Block deployments that degrade scores below threshold.

## Key Metrics Dashboard

| Metric | Source |
|---|---|
| Token cost by model | Generation spans |
| P50/P95 latency | Trace duration |
| Error rate | Span status |
| Faithfulness score | Evaluation runs |
| User satisfaction | Human feedback events |

## LLM O11y Architecture (from Talk)

The progression described in the [LLM O11y talk](../../content/posts/2026-07-01-langfuse-ai-ent.md):

1. **Observability** (Langfuse tracing) — see what's happening
2. **Evaluation** (LLM-as-a-judge, RAGAS) — measure quality
3. **Dataset** — collect representative examples from production
4. **Regression tests** — run on every PR
5. **Decision gate** — block deploy if quality drops

> "Observability is not enough — you need a decision system." — [LLM O11y talk](../../content/posts/2026-07-01-langfuse-ai-ent.md)

## References

- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse GitHub](https://github.com/langfuse/langfuse)
- [Langfuse Helm Chart](https://langfuse.com/docs/deployment/self-host)
- Source: [LLM O11y: From Observability to Decision System](../../content/posts/2026-07-01-langfuse-ai-ent.md)
