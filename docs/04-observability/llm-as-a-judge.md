# LLM-as-a-Judge

> **TL;DR** — LLM-as-a-judge uses a strong LLM (often GPT-4) to evaluate the output of another LLM call, enabling scalable automated quality scoring without human labellers.

## Overview

Human evaluation is the gold standard but doesn't scale. LLM-as-a-judge leverages a capable model to score outputs against defined rubrics — often achieving 0.8+ correlation with human judgements on well-defined criteria.

It is the backbone of:
- Automated RAG evaluation (faithfulness, relevance)
- Regression test suites for prompt changes
- A/B testing between models or configurations
- Production monitoring (random-sample scoring)

## Design Principles

1. **Clear rubric** — Define exactly what you are measuring. Vague instructions produce inconsistent scores.
2. **Reference-based vs. reference-free** — With a ground truth, score against it. Without, use the judge's own knowledge.
3. **Structured output** — Use JSON mode to get numeric scores + reasoning. Easier to aggregate and threshold.
4. **Chain-of-thought** — Ask the judge to reason before scoring. Improves consistency.
5. **Separate judge from generator** — Never use the same model instance/call to both generate and judge.

## Judge Prompt Template

```python
JUDGE_PROMPT = """
You are an expert evaluator for a RAG question-answering system.

## Task
Evaluate the given answer based on the provided context and question.

## Scoring Rubric
- **faithfulness** (0–5): Every claim in the answer is explicitly supported by the context.
  0 = answer contradicts or ignores the context
  5 = all claims are directly supported by the context
- **relevance** (0–5): The answer directly addresses the question asked.
  0 = completely off-topic
  5 = perfectly on-topic and complete
- **completeness** (0–5): The answer covers all key points available in the context.
  0 = important information missing
  5 = comprehensive coverage

## Input
Question: {question}
Context: {context}
Answer: {answer}

## Output
Think step-by-step, then respond in JSON:
{{
  "faithfulness": <0-5>,
  "relevance": <0-5>,
  "completeness": <0-5>,
  "reasoning": "<brief explanation>"
}}
"""
```

## Implementation

```python
import json
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)

def judge(question: str, context: str, answer: str, model: str = None) -> dict:
    model = model or os.environ["AZURE_OPENAI_DEPLOYMENT"]
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": JUDGE_PROMPT.format(
                question=question, context=context, answer=answer
            )}
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)

# Example
scores = judge(
    question="What is a Kubernetes Deployment?",
    context="A Deployment manages a ReplicaSet to maintain a desired number of Pods...",
    answer="A Deployment is a Kubernetes object that ensures a specified number of Pod replicas are running.",
)
print(scores)
# {"faithfulness": 5, "relevance": 5, "completeness": 4, "reasoning": "..."}
```

## Pairwise Comparison

For A/B testing two models or prompts:

```python
PAIRWISE_PROMPT = """
Compare Answer A and Answer B for the following question. Which is better?
Question: {question}
Context: {context}
Answer A: {answer_a}
Answer B: {answer_b}
Respond in JSON: {{"winner": "A" or "B" or "tie", "reasoning": "..."}}
"""
```

## Limitations

| Limitation | Mitigation |
|---|---|
| Position bias — judge prefers first answer | Randomise order; average forward/reverse runs |
| Length bias — judge prefers longer answers | Explicitly penalise padding in rubric |
| Self-bias — judge prefers its own style | Use a different model family as judge |
| Cost | Sample 5–10% of production traffic; full eval on dataset only |
| Inconsistency at low temps | Run 3× and take majority vote |

## References

- [Judging LLM-as-a-Judge (LMSYS, 2023)](https://arxiv.org/abs/2306.05685)
- [RAGAS](https://docs.ragas.io/)
- Source: [LLM O11y: From Observability to Decision System](../../content/posts/2026-07-01-langfuse-ai-ent.md)
- Related: [RAG Evaluation](../02-rag/evaluation.md) | [Langfuse](langfuse.md)
