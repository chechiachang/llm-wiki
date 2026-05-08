# RAG Use Cases

> **TL;DR** — RAG is most impactful for private knowledge bases, technical documentation Q&A, onboarding assistants, and DevOps runbook automation.

## Internal Enterprise Knowledge Base

**Problem**: Knowledge is scattered across Confluence, Notion, Google Drive, and Slack. Keyword search misses semantically similar documents. New engineers spend days finding the right information.

**Solution**: Index all internal documents into a vector store. Provide a chat interface where engineers ask questions in natural language.

**Stack**: Document loaders (Confluence API, Google Drive) → LangChain text splitting → Azure OpenAI embeddings → Qdrant → AzureChatOpenAI → Slack bot / web UI.

**Demonstrated at**: [DevOpsDay 2025 RAG Workshop](../../content/posts/2025-06-06-devops-rag-internal-ai.md)

---

## Kubernetes Documentation Assistant

**Problem**: Kubernetes has 1000+ pages of documentation. Finding the right kubectl flag or API field requires knowing the right search terms.

**Solution**: Index the official Kubernetes docs. Answer questions like *"How do I configure a liveness probe with a custom HTTP header?"* with source links.

**Key insight from workshop**: Traditional search requires keywords (e.g., "Dynamic Persistent Volume Resizing"); RAG understands intent even with vague phrasing.

---

## DevOps Runbook Automation

**Problem**: Incident runbooks exist but engineers don't read them during high-stress outages. Slack queries to senior engineers interrupt their work.

**Solution**: Index runbooks, post-mortems, and architecture docs. Deploy a bot that:
1. Detects error messages from PagerDuty/Slack
2. Retrieves relevant runbook steps
3. Presents a step-by-step response with source links

---

## New Employee Onboarding Bot

**Problem**: Onboarding docs are outdated or impossible to navigate. Senior engineers spend hours answering the same questions.

**Solution**: Index onboarding docs, architecture decision records (ADRs), and FAQs. New employees ask questions; the bot answers with cited sources and flags outdated content.

---

## Code Review Assistant

**Problem**: Tribal knowledge about internal coding standards and architectural patterns is not encoded in linters.

**Solution**: Index internal RFCs, style guides, and code review comments. When a PR is opened, retrieve relevant standards and suggest review comments.

---

## When NOT to Use RAG

| Situation | Better Approach |
|---|---|
| Simple structured data lookup | SQL / traditional API |
| High-frequency, low-latency queries | Cache + deterministic logic |
| Safety-critical decisions (medical, financial) | Human review required; LLM as advisory only |
| Tasks requiring precise arithmetic | Code execution (tool use) |

## References

- Source: [RAG Workshop — DevOpsDay 2025](../../content/posts/2025-06-06-devops-rag-internal-ai.md)
- Source: [RAG Workshop — Hello World Dev Conf 2025](../../content/posts/2025-10-15-hwdc-rag.md)
- Source: [Cloud Summit RAG Workshop 2026](../../content/posts/2026-07-01-rag-cloud-summit.md)
- Related: [RAG Introduction](introduction.md) | [Evaluation](evaluation.md)
