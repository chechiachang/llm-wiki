# Vector Databases

> **TL;DR** — A vector database stores embedding vectors with metadata and enables fast Approximate Nearest Neighbour (ANN) search; Qdrant is a strong open-source choice for RAG workloads.

## Overview

Vector databases are purpose-built to store, index, and query high-dimensional vectors. Unlike relational databases that filter on exact values, vector databases retrieve items by **semantic similarity** — finding the stored vectors geometrically closest to a query vector.

## Popular Options

| Database | Type | Notes |
|---|---|---|
| **Qdrant** | Open-source, self-hosted or cloud | Written in Rust; great performance; native filtering; used in workshop examples |
| **pgvector** | PostgreSQL extension | Easy to add to existing Postgres infra; good for moderate scale |
| **Azure AI Search** | Managed cloud (Azure) | Integrated with Azure OpenAI; hybrid BM25 + vector search |
| **Pinecone** | Managed cloud | Fully hosted, simple API |
| **Weaviate** | Open-source / cloud | GraphQL API; built-in module ecosystem |
| **Chroma** | Open-source, embedded | Great for local development and notebooks |
| **Milvus** | Open-source, cloud | High-scale, cloud-native |

## Qdrant — Quickstart

### Run locally with Docker

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### Create a collection and upsert vectors

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url="http://localhost:6333")

# Create collection
client.create_collection(
    collection_name="wiki",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# Upsert a point
client.upsert(
    collection_name="wiki",
    points=[
        PointStruct(
            id=1,
            vector=[0.1] * 1536,   # replace with real embedding
            payload={"source": "k8s-docs", "text": "A Pod is the smallest..."},
        )
    ],
)
```

### Search

```python
results = client.search(
    collection_name="wiki",
    query_vector=[0.1] * 1536,   # replace with real query embedding
    limit=5,
    with_payload=True,
)
for r in results:
    print(r.score, r.payload["text"])
```

## Filtering

Qdrant supports payload filtering alongside vector search (hybrid filtering):

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="wiki",
    query_vector=query_vec,
    query_filter=Filter(
        must=[FieldCondition(key="source", match=MatchValue(value="k8s-docs"))]
    ),
    limit=5,
)
```

## Choosing the Right Database

| Factor | Recommendation |
|---|---|
| Local dev / notebooks | Chroma (in-memory) |
| Small production (<1M vectors) | Qdrant or pgvector |
| Azure-native workloads | Azure AI Search |
| Large scale (>10M vectors) | Qdrant cluster or Milvus |
| Existing Postgres infra | pgvector extension |

## Trade-offs / Considerations

- **ANN vs. exact search**: ANN is fast but may miss some neighbours. For high-precision use cases, consider exact KNN at smaller scale.
- **Metadata filtering**: Always store rich metadata (source, date, category) to enable filtered retrieval and citations.
- **Index persistence**: Ensure your Docker volume or cloud storage is persisted; re-indexing large corpora is expensive.
- **Dimension mismatch**: The collection dimension must match the embedding model's output. Cannot be changed after creation — create a new collection.

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain Qdrant Integration](https://python.langchain.com/docs/integrations/vectorstores/qdrant/)
- [pgvector on GitHub](https://github.com/pgvector/pgvector)
- Source: [RAG Workshop Slides](../../content/slides/2025-06-05-devops-rag-internal-ai.md)
