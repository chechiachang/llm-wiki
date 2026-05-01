# DevOps AI Patterns

> **TL;DR** — LLMs augment DevOps workflows via alert triage, runbook Q&A, automated PR review, and infrastructure query bots; always pair with evaluation and human oversight.

## Pattern 1 — Intelligent Alert Triage

**Problem**: On-call engineers receive noisy alerts and must manually correlate them with runbooks.

**Solution**: 
1. Capture the alert (PagerDuty webhook / Slack).
2. Retrieve relevant runbook sections from the vector store.
3. LLM synthesises a first-response recommendation.
4. Post recommendation to the incident Slack channel with source links.

```python
def triage_alert(alert_title: str, alert_body: str) -> str:
    query = f"{alert_title}: {alert_body}"
    result = qa_chain.invoke({"query": query})
    sources = [d.metadata["source"] for d in result["source_documents"]]
    return f"""
**Suggested Response:**
{result["result"]}

**Relevant Runbooks:**
{chr(10).join(f"- {s}" for s in set(sources))}
"""
```

---

## Pattern 2 — Post-Mortem Knowledge Extraction

**Problem**: Post-mortem documents contain valuable debugging patterns but are never consulted again.

**Solution**:
1. Index all post-mortems with structured metadata (`service`, `severity`, `date`, `root_cause_category`).
2. Enable semantic search: *"How did we handle OOMKilled issues in the payments service before?"*
3. Surface related post-mortems when a new incident is opened.

---

## Pattern 3 — PR Code Review Assistant

**Problem**: Internal coding standards and architectural patterns exist as documents but are not enforced in reviews.

**Solution**:
1. Index RFCs, ADRs, and style guides.
2. On PR open (GitHub Action), retrieve relevant standards for the changed files.
3. LLM generates review comments as a GitHub Check.

```yaml
# .github/workflows/ai-review.yml
on: [pull_request]
jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: AI code review
        run: python scripts/ai_review.py --pr ${{ github.event.pull_request.number }}
```

---

## Pattern 4 — Infrastructure Q&A Bot

**Problem**: New engineers don't know the current state of infrastructure (which clusters exist, what namespaces are used for, how to connect to staging).

**Solution**:
1. Index infra documentation, terraform module READMEs, and architecture diagrams' alt-text.
2. Provide a Slack bot or CLI tool for natural language queries.
3. Include auto-generated context: pull live cluster list from Kubernetes API at query time.

```python
def get_clusters() -> str:
    """Tool: returns list of available Kubernetes clusters."""
    # Could call kubectl, cloud API, CMDB
    return "staging-eastus, prod-eastus, prod-westus"
```

---

## Pattern 5 — Onboarding Accelerator

**Problem**: Onboarding documentation is outdated. Senior engineers spend 4–8 hours per new hire on repeated questions.

**Solution**:
1. Index onboarding guides, architecture overview, team conventions.
2. Deploy an "onboarding bot" with a system prompt scoped to onboarding context.
3. Track which questions the bot cannot answer → feed back to documentation owners.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails |
|---|---|
| Using LLM for access control decisions | Non-deterministic; security risk |
| Using LLM for financial calculations | Arithmetic errors; use code execution |
| Deploying without evaluation | No visibility into answer quality |
| Indexing everything without curation | Noisy retrieval; contradictory chunks |
| No feedback loop | Quality drifts without detection |

---

## The DevOps AI Copilot Vision

> "DevOps AI Copilot 不應該像圖書館守門員等人來借書，
>  而應該像導航系統，在你開車時主動告訴你：前方有彎道。"
>
> — [RAG Workshop, DevOpsDay 2025](../../content/slides/2025-06-05-devops-rag-internal-ai.md)

The goal is a **context-aware knowledge copilot** that surfaces relevant information proactively within the engineer's workflow — not a passive search engine.

## References

- Source: [RAG Workshop — DevOpsDay 2025](../../content/posts/2025-06-06-devops-rag-internal-ai.md)
- Source: [LLM O11y Talk](../../content/posts/2026-07-01-langfuse-ai-ent.md)
- Related: [Internal Knowledge Base](internal-knowledge-base.md) | [Agent Patterns](../03-agents/agent-patterns.md)
