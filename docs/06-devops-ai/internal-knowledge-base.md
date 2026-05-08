# Internal Knowledge Base with RAG

> **TL;DR** — A RAG-powered internal knowledge base indexes your team's documents (Confluence, Notion, Runbooks, ADRs) and lets engineers ask questions in natural language, reducing time-to-answer from hours to seconds.

## The Problem

Engineering teams accumulate knowledge in many places:
- **Confluence / Notion** — architecture docs, how-to guides, ADRs
- **GitHub** — README files, PR descriptions, code comments
- **Slack / Teams** — tribal knowledge in conversations
- **Runbooks** — incident response procedures
- **Post-mortems** — failure analysis and lessons learned

Traditional keyword search:
- Requires knowing the right terms (a junior engineer doesn't know to search "Dynamic PVC Resizing")
- Returns documents, not answers
- Cannot synthesise information from multiple sources
- Is not conversational

## Solution Architecture

```
Document Sources                    Indexing Pipeline
─────────────────          ─────────────────────────────────
Confluence    ──────────►  Load → Chunk → Embed → Qdrant
Google Drive  ──────────►
GitHub (MDs)  ──────────►
Slack export  ──────────►
Runbooks      ──────────►

                            Query Pipeline
                    ────────────────────────────────────────
User (Slack bot      User Query → Embed → Retrieve (k=5)
or web UI)      ──►          → Prompt → Azure OpenAI → Answer
                                              │
                                         Langfuse (trace)
```

## Implementation Checklist

### Phase 1 — Proof of Concept

- [ ] Pick one high-value source (e.g., Confluence space or GitHub `docs/` folder)
- [ ] Load and chunk documents with LangChain
- [ ] Embed with `text-embedding-3-large`
- [ ] Store in Qdrant (local Docker)
- [ ] Build a simple query script
- [ ] Manually test 20 representative questions

### Phase 2 — Evaluation

- [ ] Create a 50-question evaluation dataset
- [ ] Run RAGAS metrics (faithfulness, context precision)
- [ ] Tune chunking strategy and retriever `k`
- [ ] Set quality threshold for production gate

### Phase 3 — Production

- [ ] Deploy Qdrant on Kubernetes with persistent volume
- [ ] Deploy RAG API service
- [ ] Integrate Langfuse for tracing
- [ ] Add Slack bot or web UI
- [ ] Set up automated re-indexing on document changes (GitHub Action or webhook)
- [ ] Monitor quality dashboard weekly

## Indexing Confluence

```python
from langchain_community.document_loaders import ConfluenceLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = ConfluenceLoader(
    url=os.environ["CONFLUENCE_URL"],
    username=os.environ["CONFLUENCE_USER"],
    api_key=os.environ["CONFLUENCE_API_KEY"],
    space_key="ENG",
    include_attachments=False,
    limit=50,
)
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
chunks = splitter.split_documents(docs)
```

## Slack Bot Integration

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def handle_mention(event, say):
    question = event["text"].replace(f"<@{app.client.auth_test()['user_id']}>", "").strip()
    result = qa_chain.invoke({"query": question})
    sources = set(d.metadata.get("source", "") for d in result["source_documents"])
    reply = f"{result['result']}\n\nSources: {', '.join(sources)}"
    say(reply, thread_ts=event["ts"])

SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

## Keeping the Index Fresh

Use a GitHub Action to re-index when documentation changes:

```yaml
on:
  push:
    paths:
      - 'docs/**'
      - 'runbooks/**'
jobs:
  reindex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/reindex.py --source docs/ runbooks/
        env:
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
          AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
```

## Lessons Learned (from Workshops)

Based on the RAG workshops taught at DevOpsDay 2025, Hello World Dev Conf 2025, and Cloud Summit 2026:

1. **Start small**: One Confluence space is better than everything at once.
2. **Metadata matters**: Store `source`, `last_updated`, `author` in every chunk's payload.
3. **Chunking is the most impactful parameter**: Spend time testing different strategies.
4. **Answer length calibration**: Instruct the model on desired answer format (short answer, bullet points, code examples).
5. **Graceful "I don't know"**: Critical for trust. Engineers will stop using the bot if it confidently gives wrong answers.
6. **Feedback loop**: Add a 👍/👎 reaction in Slack; feed negatives back into the evaluation dataset.

## References

- Source: [RAG Workshop — DevOpsDay 2025](../../content/posts/2025-06-06-devops-rag-internal-ai.md)
- Source: [RAG Workshop — Hello World Dev Conf 2025](../../content/posts/2025-10-15-hwdc-rag.md)
- Source: [Cloud Summit RAG Workshop 2026](../../content/posts/2026-07-01-rag-cloud-summit.md)
- [chechiachang/rag-workshop (GitHub)](https://github.com/chechiachang/rag-workshop)
