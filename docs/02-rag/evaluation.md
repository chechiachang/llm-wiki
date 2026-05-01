# RAG Evaluation

> **TL;DR** — Evaluation is not optional for RAG systems; use RAGAS metrics (context precision, recall, faithfulness, answer relevance) to measure quality and drive iterative improvements.

## Overview

Anyone can write a RAG pipeline in an afternoon. Knowing whether it's actually *good* requires systematic evaluation. Without metrics, you cannot:
- Compare chunking strategies or retriever configurations
- Detect regressions when you update the index or model
- Set a production readiness gate
- Justify infrastructure investment

## Key Metrics (RAGAS Framework)

| Metric | Definition | Range |
|---|---|---|
| **Context Precision** | Fraction of retrieved chunks that are relevant to the query | 0–1 (higher = better) |
| **Context Recall** | Fraction of relevant information successfully retrieved | 0–1 (higher = better) |
| **Faithfulness** | Fraction of answer claims supported by retrieved context | 0–1 (higher = better) |
| **Answer Relevance** | How well the answer addresses the original question | 0–1 (higher = better) |
| **Answer Correctness** | Semantic + factual similarity to a ground-truth answer | 0–1 (higher = better) |

## Evaluation Dataset

A good evaluation dataset contains:
- **Question**: a realistic user query
- **Ground truth answer**: a reference answer written by a human
- **Ground truth contexts** (optional): which document chunks *should* be retrieved

Start with 20–50 examples covering edge cases and core use cases.

## Example: RAGAS Evaluation

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

# Collect Q&A pairs from your RAG pipeline
samples = [
    {
        "question": "What is a Kubernetes Deployment?",
        "answer": "A Deployment is a Kubernetes object that manages a set of identical Pods...",
        "contexts": ["A Deployment provides declarative updates for Pods..."],  # retrieved chunks
        "ground_truth": "A Deployment manages a ReplicaSet to maintain a desired number of Pods.",
    },
    # ... more samples
]

dataset = Dataset.from_list(samples)

result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)

print(result.to_pandas()[["faithfulness", "answer_relevancy", "context_precision", "context_recall"]])
```

## LLM-as-a-Judge

When you don't have ground-truth answers, use a second LLM call to judge quality:

```python
from openai import AzureOpenAI

JUDGE_PROMPT = """
You are an impartial judge evaluating a RAG system answer.

Question: {question}
Retrieved Context: {context}
Answer: {answer}

Rate the answer on these dimensions (0–5 each):
1. Faithfulness: Is every claim in the answer supported by the context?
2. Relevance: Does the answer address the question?
3. Completeness: Does the answer cover the key points from the context?

Respond in JSON: {{"faithfulness": X, "relevance": X, "completeness": X, "reasoning": "..."}}
"""

def judge_answer(question, context, answer):
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version="2024-02-01",
    )
    resp = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            question=question, context=context, answer=answer
        )}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    import json
    return json.loads(resp.choices[0].message.content)
```

> See also: [LLM-as-a-Judge](../04-observability/llm-as-a-judge.md) for a deeper dive.

## Iterative Improvement Cycle

```
Build → Evaluate → Identify worst-performing samples
     ↑                         ↓
     └──── Fix (chunking / retriever / prompt) ←──┘
```

Common fixes per metric:

| Low Metric | Likely Cause | Fix |
|---|---|---|
| Context Precision | Retrieving noisy/irrelevant chunks | Smaller chunk size, metadata filtering |
| Context Recall | Missing relevant chunks | Larger `k`, better chunking, query expansion |
| Faithfulness | Model ignores context | Stricter system prompt, lower temperature |
| Answer Relevance | Answer drifts off-topic | Tighter prompt, output validation |

## References

- [RAGAS Documentation](https://docs.ragas.io/)
- [RAGAS GitHub](https://github.com/explodinggradients/ragas)
- Source: [RAG Workshop — DevOpsDay 2025 (Evaluation section)](../../content/slides/2025-06-05-devops-rag-internal-ai.md)
- Related: [LLM-as-a-Judge](../04-observability/llm-as-a-judge.md)
