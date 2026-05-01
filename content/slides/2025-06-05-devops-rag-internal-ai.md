---
title: "Workshop: RAG打造企業AI知識庫：把一甲子功力傳給新人"
date: "2025-06-05"
event: "DevOpsDay Taiwan 2025"
event_url: "https://devopsdays.tw/2025/workshop-page/3788"
source_repo: "https://github.com/chechiachang/chechiachang.github.io-src/tree/master/content/slides/2025-06-05-devops-rag-internal-ai"
tags: ["rag", "devops", "openai", "langchain", "qdrant", "azure"]
wiki_pages:
  - "../../docs/02-rag/introduction.md"
  - "../../docs/02-rag/vector-databases.md"
  - "../../docs/02-rag/evaluation.md"
  - "../../docs/06-devops-ai/internal-knowledge-base.md"
---

# RAG Workshop: 企業AI知識庫 — DevOpsDay 2025

**Event**: DevOpsDay Taiwan 2025  
**Date**: 2025-06-05  
**Slides source**: [GitHub](https://github.com/chechiachang/chechiachang.github.io-src/tree/master/content/slides/2025-06-05-devops-rag-internal-ai)  
**Published**: <https://chechia.net/zh-hant/slides/2025-06-05-devops-rag-internal-ai/>

## Slide Summary

### Setup (Environment)
- Option 1: Local Docker + Jupyter Notebook
- Option 2: Remote VM via ngrok / Azure Bastion
- Workshop repo: `git clone https://github.com/chechiachang/rag-workshop.git`

### Why RAG?
- Knowledge is scattered (Confluence, Google Drive, Slack)
- Traditional search requires exact keywords — new engineers don't know the vocabulary
- LLMs reduce language barrier and help comprehension but hallucinate without grounding
- RAG = retrieval (find relevant facts) + generation (answer in natural language)

### RAG Architecture
1. Documents → Chunks → Embeddings → Vector DB
2. Query → Embed → ANN Search → Retrieve Top-k → Prompt + LLM → Answer

### Embeddings and Vector DB
- `text-embedding-3-large` / `text-embedding-ada-002`
- Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
- Cosine similarity for semantic search

### Evaluation (RAGAS)
- Context Precision, Context Recall, Faithfulness, Answer Relevance
- LLM-as-a-judge for scalable scoring

### Key Quote

> "DevOps AI Copilot 不應該像圖書館守門員等人來借書，
> 而應該像導航系統，在你開車時主動告訴你：前方有彎道。"

## Related Wiki Pages

- [RAG Introduction](../../docs/02-rag/introduction.md)
- [Vector Databases](../../docs/02-rag/vector-databases.md)
- [RAG Evaluation](../../docs/02-rag/evaluation.md)
- [Internal Knowledge Base](../../docs/06-devops-ai/internal-knowledge-base.md)
