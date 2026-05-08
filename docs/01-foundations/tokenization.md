# Tokenization

> **TL;DR** — Tokenization splits raw text into sub-word units called tokens; understanding it helps predict cost, context-window usage, and model behaviour on non-English text.

## Overview

Before text enters an LLM it must be converted into a sequence of integer IDs. A **tokenizer** performs this split using a learned vocabulary (e.g., 100k entries for GPT-4). Because the vocabulary is sub-word based, a single English word may become 1–3 tokens, while rare or non-English words can become many more.

## Key Concepts

- **BPE (Byte-Pair Encoding)**: The algorithm used by OpenAI's `tiktoken`. Iteratively merges the most frequent adjacent byte pairs to build a vocabulary.
- **Token ID**: Integer index into the model's vocabulary.
- **Context length**: Measured in tokens, not characters. `gpt-4o` supports up to 128k tokens.
- **Token cost**: API pricing is per 1,000 tokens (input + output separately).

## Token Counts by Language (approximate)

| Language | Tokens per word |
|---|---|
| English | ~1.3 |
| Chinese (simplified) | ~1.5–2 per character |
| Traditional Chinese | ~1.5–2 per character |
| Code (Python) | ~1.5 |
| JSON | ~2–4 |

> Chinese text is generally 2–3× more expensive per word than English.

## Example: Count Tokens with tiktoken

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "How do I configure a Kubernetes HorizontalPodAutoscaler?"
tokens = enc.encode(text)
print(f"Token count: {len(tokens)}")   # 11
print(f"Tokens: {tokens}")

# Decode back to check
decoded = enc.decode(tokens)
print(decoded)
```

## Trade-offs / Considerations

- **Context window planning**: If you pass a 50-page PDF as context, estimate token count first. Exceeding the limit truncates silently in some frameworks.
- **Prompt compression**: Techniques like LLMLingua can compress prompts 2–4× with minimal quality loss.
- **Special tokens**: Models reserve tokens for role delimiters (`<|im_start|>`), stop sequences, and function-call syntax. These count against the context limit.

## References

- [tiktoken (OpenAI)](https://github.com/openai/tiktoken)
- [OpenAI Tokenizer Playground](https://platform.openai.com/tokenizer)
