# Evaluation Pipeline

> **TL;DR** — An evaluation pipeline turns an ad-hoc dataset of Q&A examples into a repeatable regression test that runs on every PR, blocking deployments that degrade quality below a defined threshold.

## Overview

Evaluation is a continuous practice, not a one-time activity. The goal is a **closed-loop feedback system**:

```
Observe (tracing) → Evaluate (scores) → Dataset (collect) → Regress (test) → Gate (block/allow)
      ▲                                                                             │
      └─────────────────────── Deploy (if pass) ────────────────────────────────────┘
```

This transforms LLM framework selection from gambling into a **verifiable decision**.

## Building an Evaluation Dataset

### From Production Traces (recommended)

1. Enable tracing (Langfuse).
2. Filter for traces with low quality scores or user negative feedback.
3. Add representative examples to a dataset: `{input, expected_output}`.
4. Target 50–200 examples covering:
   - Happy path (common queries)
   - Edge cases (ambiguous, multilingual, out-of-scope)
   - Regressions (previously broken queries)

### Synthetically Generated

Use an LLM to generate Q&A pairs from your document corpus:

```python
GENERATE_QA_PROMPT = """
Based on the following document chunk, generate 3 realistic question-answer pairs
that a user might ask about this content.

Document:
{document}

Respond in JSON:
{{"pairs": [{{"question": "...", "answer": "..."}}]}}
"""
```

## Running Evaluations in CI

```python
# tests/test_rag_quality.py
import pytest
from my_rag_pipeline import answer_question
from evaluation import judge

QUALITY_THRESHOLD = 4.0  # out of 5

QA_DATASET = [
    {
        "question": "What is a Kubernetes Deployment?",
        "context_hint": "kubernetes deployment",
        "ground_truth": "A Deployment manages a ReplicaSet to maintain a desired number of Pods.",
    },
    {
        "question": "How does RAG reduce hallucination?",
        "context_hint": "rag hallucination",
        "ground_truth": "RAG supplies retrieved, verified documents as context so the LLM is grounded in facts.",
    },
]

@pytest.mark.parametrize("sample", QA_DATASET)
def test_rag_quality(sample):
    result = answer_question(sample["question"])
    scores = judge(
        question=sample["question"],
        context=result["context"],
        answer=result["answer"],
    )
    avg_score = (scores["faithfulness"] + scores["relevance"] + scores["completeness"]) / 3
    assert avg_score >= QUALITY_THRESHOLD, (
        f"Quality {avg_score:.2f} < threshold {QUALITY_THRESHOLD}. "
        f"Reasoning: {scores['reasoning']}"
    )
```

## Deployment Gate Pattern

In your CI pipeline, run evaluation tests and block the merge/deploy if they fail:

```yaml
# .github/workflows/llm-quality-gate.yml
- name: Run LLM quality evaluation
  run: python -m pytest tests/test_rag_quality.py -v
  env:
    AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
    AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
    AZURE_OPENAI_DEPLOYMENT: ${{ secrets.AZURE_OPENAI_DEPLOYMENT }}
```

## Metrics to Track Over Time

| Metric | Regression Signal |
|---|---|
| Mean faithfulness score | Drop after prompt change |
| P95 latency | Spike after adding tool calls |
| Token cost per query | Increase after retriever `k` increase |
| % answers below threshold | Drift from data distribution shift |

## Trade-offs / Considerations

- **LLM judge cost**: Full dataset eval on every PR can be expensive. Tiered strategy: fast structural tests on every PR, full LLM eval only on release branches.
- **Dataset staleness**: Refresh the dataset quarterly or after major knowledge base updates.
- **Threshold calibration**: Start with a low threshold and tighten as baseline improves.

## References

- Source: [LLM O11y Talk — evaluation / dataset / regression / decision gate](../../content/posts/2026-07-01-langfuse-ai-ent.md)
- [RAGAS Evaluation](https://docs.ragas.io/en/stable/concepts/evaluation/)
- [Langfuse Datasets](https://langfuse.com/docs/datasets/overview)
- Related: [LLM-as-a-Judge](llm-as-a-judge.md) | [Langfuse](langfuse.md) | [RAG Evaluation](../02-rag/evaluation.md)
