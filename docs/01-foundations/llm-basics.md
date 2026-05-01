# LLM Basics

> **TL;DR** — A Large Language Model (LLM) is a neural network trained to predict the next token in a sequence; it generates fluent text but has no inherent understanding of truth.

## Overview

Large Language Models such as GPT-4, Claude, and Gemini are transformer-based neural networks trained on internet-scale text corpora. Given a sequence of tokens (words or sub-words), the model predicts the most probable next token. Repeating this process produces coherent paragraphs, code, or structured data.

## Key Concepts

- **Token**: The smallest unit an LLM processes. A token is roughly 3–4 characters in English.
- **Context window**: The maximum number of tokens the model can attend to in a single call. Longer windows allow more history but cost more.
- **Temperature**: Controls randomness of sampling. `0` = deterministic, `1` = creative/random.
- **Top-p (nucleus sampling)**: Limits the token pool to the smallest set whose cumulative probability exceeds `p`.
- **System prompt**: Instructions prepended to every conversation to steer the model's behaviour and persona.
- **Completion vs Chat API**: Completion generates raw continuations; Chat API enforces a `system / user / assistant` turn structure.

## How It Works

1. Input text is split into tokens by a tokenizer (e.g., tiktoken for OpenAI models).
2. Tokens are converted to embedding vectors.
3. The transformer applies self-attention across all tokens to build contextual representations.
4. A linear head over the final hidden states produces a probability distribution over the vocabulary.
5. One token is sampled from that distribution and appended to the sequence.
6. Steps 3–5 repeat until a stop condition (stop token, max tokens).

## Capabilities and Limits

| Capability | Notes |
|---|---|
| Text generation | High quality for English; degrades for low-resource languages |
| Summarisation | Effective; may lose detail in very long documents |
| Code generation | Strong for popular languages (Python, TypeScript, Go) |
| Reasoning | Improved with chain-of-thought prompting; still error-prone on multi-step math |
| Factual recall | Unreliable — models can hallucinate plausible-sounding facts |
| Long-term memory | None by default; must be supplied via context or external store |

## Example: Calling Azure OpenAI

```python
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)

response = client.chat.completions.create(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],  # e.g. "gpt-4.1"
    messages=[
        {"role": "system", "content": "You are a helpful DevOps assistant."},
        {"role": "user", "content": "Explain Kubernetes resource limits in one paragraph."},
    ],
    temperature=0.2,
    max_tokens=256,
)

print(response.choices[0].message.content)
```

## Trade-offs / Considerations

- **Cost**: Charged per token (input + output). Long contexts are expensive.
- **Latency**: First-token latency can be 1–3 s; total time scales with output length.
- **Non-determinism**: Even at `temperature=0` results can vary across API versions.
- **Data privacy**: Do not send sensitive PII or secrets to third-party APIs. Use Azure OpenAI private endpoints for enterprise workloads.

## References

- [OpenAI Platform Docs](https://platform.openai.com/docs)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- Related: [Embeddings](embeddings.md) | [Hallucination](hallucination.md)
