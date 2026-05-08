# Embeddings

> **TL;DR** — An embedding is a dense numeric vector that encodes the semantic meaning of a piece of text; similar texts produce vectors that are close in the embedding space.

## Overview

Embeddings are the mathematical backbone of semantic search and RAG systems. An embedding model (e.g., `text-embedding-3-large`, `text-embedding-ada-002`) converts a string of text into a fixed-length vector of floats (e.g., 1536 dimensions for `text-embedding-ada-002`). The geometric distance between two vectors reflects their semantic similarity.

## Key Concepts

- **Embedding model**: A neural network trained to map text to vectors. Distinct from the chat/completion model.
- **Dimensionality**: Number of floats in the vector. Higher dimensions can capture more nuance but use more memory and compute.
- **Cosine similarity**: The standard distance metric. Values range from -1 (opposite) to +1 (identical). `similarity = dot(a, b) / (|a| * |b|)`.
- **Semantic search**: Retrieve documents whose embeddings are closest to the query embedding — no keyword matching needed.
- **Chunking**: Before embedding long documents, they are split into smaller chunks so each chunk has a focused meaning.

## How It Works

```
Text Input
    │
    ▼
Tokenizer (e.g. tiktoken)
    │
    ▼
Embedding Model (e.g. text-embedding-3-large)
    │
    ▼
Vector [0.023, -0.154, 0.891, ...]  ← length = 1536 or 3072
    │
    ▼
Stored in Vector Database (e.g. Qdrant, pgvector, Azure AI Search)
```

At query time the same model embeds the user's question and the vector DB returns the nearest neighbours.

## Example: Generating Embeddings with Azure OpenAI

```python
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)

def embed(text: str) -> list[float]:
    resp = client.embeddings.create(
        input=text,
        model="text-embedding-3-large",  # deployment name
    )
    return resp.data[0].embedding

# Compare two sentences
v1 = embed("How do I scale a Kubernetes deployment?")
v2 = embed("What is the kubectl command to increase replicas?")

import numpy as np
cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
print(f"Cosine similarity: {cos_sim:.4f}")  # expect > 0.9
```

## Chunking Strategies

| Strategy | Description | Best For |
|---|---|---|
| Fixed-size | Split every N characters/tokens | Simple pipelines, uniform documents |
| Sentence | Split at sentence boundaries | Prose, blog posts |
| Paragraph | Split at blank lines | Documentation |
| Semantic | Split at topic change (model-based) | Complex mixed-content docs |
| Recursive character | LangChain default; tries `\n\n`, `\n`, ` ` | General purpose |

> See also: [RAG Introduction](../02-rag/introduction.md) for how embeddings fit into a full RAG pipeline.

## Trade-offs / Considerations

- **Chunk size vs. context**: Small chunks = precise retrieval; large chunks = more context per retrieved piece.
- **Overlap**: Adding a sliding overlap (e.g., 100-token overlap) reduces information loss at boundaries.
- **Model mismatch**: Always use the same embedding model for indexing and querying.
- **Cost**: Each embed call costs tokens. Cache embeddings; do not re-embed unchanged documents.
- **Multilingual**: `text-embedding-3-large` handles many languages reasonably well; for production Chinese content, evaluate dedicated multilingual models.

## References

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Azure OpenAI Embeddings](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/understand-embeddings)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- Source: [RAG Workshop Slides](../../content/slides/2025-06-05-devops-rag-internal-ai.md)
