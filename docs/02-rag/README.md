# Chapter 02 — RAG (Retrieval-Augmented Generation)

Build intelligent question-answering systems grounded in your own documents.

## Pages

| Page | Description |
|---|---|
| [Introduction](introduction.md) | What RAG is, when to use it, and how the pipeline works |
| [Vector Databases](vector-databases.md) | Qdrant, pgvector, Azure AI Search — choosing and using them |
| [LangChain](langchain.md) | Building RAG pipelines with LangChain |
| [Evaluation](evaluation.md) | RAGAS, LLM-as-a-judge, automated quality metrics |
| [Use Cases](use-cases.md) | Internal knowledge bases, DevOps runbooks, onboarding bots |

## Key Ideas

- RAG = **Retrieve** relevant chunks → **Augment** the prompt → **Generate** a grounded answer.
- Embeddings bridge natural language and vector search.
- Evaluation is not optional — measure faithfulness, context precision, and answer relevance.
- Chunking strategy significantly affects retrieval quality.

> See also: [Embeddings](../01-foundations/embeddings.md) | [Hallucination](../01-foundations/hallucination.md)
