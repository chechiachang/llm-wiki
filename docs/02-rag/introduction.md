# RAG Introduction

> **TL;DR** — RAG (Retrieval-Augmented Generation) combines a vector search step with an LLM generation step to produce answers grounded in your own documents, dramatically reducing hallucination on domain-specific questions.

## Overview

Traditional LLMs have a fixed knowledge cutoff and no access to private data. RAG solves both problems by retrieving relevant document chunks at query time and injecting them into the LLM's prompt as context.

This technique is particularly valuable for:

- **Internal knowledge bases** — Confluence, Notion, Google Drive, Slack archives
- **Technical documentation** — Kubernetes docs, runbooks, API references
- **Customer-facing Q&A bots** — grounded in product documentation
- **Onboarding assistants** — new engineers querying institutional knowledge

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  INDEXING (offline)                  │
│                                                      │
│  Documents → Chunker → Embedding Model → Vector DB  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  QUERYING (online)                   │
│                                                      │
│  User Query → Embed Query → Vector Search            │
│       ↓                          ↓                   │
│  Top-k Chunks ←──────────────────┘                  │
│       ↓                                              │
│  Prompt = System + Chunks + User Query               │
│       ↓                                              │
│  LLM → Answer (grounded in retrieved chunks)        │
└─────────────────────────────────────────────────────┘
```

## Step-by-Step Pipeline

### Phase 1 — Index

1. **Load documents** — PDFs, Markdown, HTML, Confluence pages.
2. **Chunk** — Split into overlapping segments (e.g., 512 tokens, 50-token overlap).
3. **Embed** — Convert each chunk to a vector using an embedding model.
4. **Store** — Upsert vectors + metadata into a vector database (Qdrant, pgvector, etc.).

### Phase 2 — Query

1. **Embed the query** — Same model as indexing.
2. **Retrieve top-k** — Run ANN (Approximate Nearest Neighbour) search. Typically `k=5–10`.
3. **Rerank** (optional) — Use a cross-encoder to reorder results by relevance.
4. **Build prompt** — Inject retrieved chunks as context.
5. **Generate** — Call the LLM with the augmented prompt.
6. **Post-process** — Extract structured fields, add citations, run evaluation.

## When to Use RAG vs. Other Approaches

| Situation | Recommended Approach |
|---|---|
| Private/internal documents | **RAG** |
| Knowledge changes frequently | **RAG** (re-index on update) |
| Need source citations | **RAG** |
| Small, stable FAQ | Fine-tuning or prompt stuffing |
| Pure reasoning tasks | Prompt engineering alone |
| Highly structured queries | Traditional search + LLM formatting |

## Minimal Python Example (LangChain + Qdrant + Azure OpenAI)

```python
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_qdrant import QdrantVectorStore
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient

# Embeddings
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

# Vector store (assumes documents already indexed)
client = QdrantClient(url="http://localhost:6333")
vectorstore = QdrantVectorStore(client=client, collection_name="wiki", embedding=embeddings)

# LLM
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01",
    temperature=0,
)

# Chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
)

print(qa.invoke("What is the kubectl command to scale a deployment?"))
```

## Key Metrics to Monitor

| Metric | What It Measures |
|---|---|
| **Context Precision** | Are the retrieved chunks relevant to the query? |
| **Context Recall** | Are all relevant chunks being retrieved? |
| **Faithfulness** | Is the answer supported by the retrieved context? |
| **Answer Relevance** | Does the answer address the user's question? |

> See: [Evaluation](evaluation.md) for how to measure these with RAGAS.

## References

- Source: [RAG Workshop — DevOpsDay 2025](../../content/posts/2025-06-06-devops-rag-internal-ai.md)
- Source: [RAG Workshop — Hello World Dev Conf 2025](../../content/posts/2025-10-15-hwdc-rag.md)
- Source: [Cloud Summit RAG Workshop 2026](../../content/posts/2026-07-01-rag-cloud-summit.md)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [OpenAI RAG Cookbook](https://cookbook.openai.com/examples/question_answering_using_embeddings)
