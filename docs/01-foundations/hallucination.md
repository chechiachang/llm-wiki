# Hallucination

> **TL;DR** — LLM hallucination is when a model generates plausible-sounding but factually incorrect content; the primary mitigation is grounding the model with retrieved, verified sources (RAG).

## Overview

LLMs are trained to produce fluent, coherent text — not to be accurate. When asked a question outside their training data, or when context is ambiguous, they will often invent facts, citations, or code that looks correct but isn't. This is called **hallucination**.

## Why It Happens

1. **Statistical prediction**: The model predicts the most probable next token, not the most truthful one.
2. **No internal knowledge store**: There is no database of facts — only learned weights encoding statistical associations.
3. **Confidence calibration**: Models often sound equally confident whether correct or wrong.
4. **Training data gaps**: Events after the training cutoff, niche domains, and low-resource languages are especially prone.

## Types of Hallucination

| Type | Example |
|---|---|
| Factual fabrication | Inventing a paper citation with a real-sounding DOI |
| Logical inconsistency | Stating contradictory facts in the same response |
| Code hallucination | Calling a method that does not exist in a library |
| Entity confusion | Mixing up two people with similar names |

## Mitigation Strategies

### 1. RAG (Retrieval-Augmented Generation)

Supply verified documents as context. The model is instructed to answer only from provided sources.

> See: [RAG Introduction](../02-rag/introduction.md)

### 2. Grounding Instructions

In the system prompt, explicitly instruct: *"Answer only using the provided context. If the answer is not in the context, say 'I don't know'."*

### 3. LLM-as-a-Judge / Evaluation

Use a second LLM call to verify whether the answer is supported by the cited sources.

> See: [Observability — LLM-as-a-Judge](../04-observability/llm-as-a-judge.md)

### 4. Citations and Source Linking

Require the model to output source references. Humans or automated checks can verify them.

### 5. Structured Output + Validation

Use JSON mode or function calling to constrain outputs to a known schema. Validate fields programmatically.

## Example: Anti-Hallucination System Prompt

```python
SYSTEM_PROMPT = """
You are a helpful assistant. Answer the user's question using ONLY the context
provided below. Do not use prior knowledge.

If the answer cannot be found in the context, respond exactly with:
"I don't have enough information to answer that."

Context:
{context}
"""
```

## Trade-offs / Considerations

- RAG reduces hallucination on factual questions but adds retrieval latency and infrastructure cost.
- Higher temperature increases hallucination risk; lower temperature reduces creativity.
- No technique eliminates hallucination entirely; always pair LLM outputs with human or automated review in high-stakes applications.

## References

- [OpenAI — How to reduce hallucinations](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api)
- Source: [RAG Workshop — LLM Hallucination slide](../../content/slides/2025-06-05-devops-rag-internal-ai.md)
- Related: [RAG Introduction](../02-rag/introduction.md) | [Evaluation](../04-observability/evaluation.md)
