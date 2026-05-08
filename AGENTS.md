# AGENTS.md — LLM Agent Instructions for Maintaining this Wiki

This file tells an LLM agent (GitHub Copilot, Claude, GPT-4, etc.) how to maintain and extend the `llm-wiki` repository.

---

## Role

You are a **wiki maintainer agent**. Your job is to keep this knowledge base accurate, well-structured, and up-to-date. You write clear technical documentation in Markdown.

---

## Repository Layout

```
llm-wiki/
├── README.md                  # Top-level navigation
├── AGENTS.md                  # This file
├── docs/
│   ├── 01-foundations/        # LLM basics
│   ├── 02-rag/                # RAG systems
│   ├── 03-agents/             # LLM agents & MCP
│   ├── 04-observability/      # Tracing, Langfuse, evaluation
│   ├── 05-deployment/         # Azure OpenAI, Kubernetes
│   └── 06-devops-ai/          # DevOps AI patterns
├── content/
│   ├── posts/                 # Extracted blog posts (read-only source)
│   └── slides/                # Extracted slide decks (read-only source)
└── tests/                     # Structural validation tests
```

---

## Tasks You May Be Asked to Do

### 1. Add a New Concept Page

- Decide which chapter under `docs/` best fits the topic.
- Create a new `.md` file with a kebab-case name (e.g., `chunking-strategies.md`).
- Use the page template below.
- Update the chapter's `README.md` to link the new page.

### 2. Update an Existing Page

- Correct factual errors or add new information.
- Keep the existing heading structure.
- Cite sources using inline links or a `## References` section.

### 3. Extract Content from Source Files

- Source material lives in `content/posts/` and `content/slides/`.
- Do **not** modify those files.
- Summarise or adapt content into the appropriate `docs/` page.
- Link back to the original source file.

### 4. Add a New Chapter

- Create a new numbered directory under `docs/` (e.g., `docs/07-fine-tuning/`).
- Add a `README.md` with a chapter overview and a table linking all pages.
- Update the top-level `README.md` navigation table.

### 5. Cross-Link Pages

- Where a concept in one chapter is relevant to another, add a `> See also:` callout.

---

## Page Template

Every concept page should follow this structure:

```markdown
# <Title>

> **TL;DR** — One sentence summary.

## Overview

Brief introduction (2–4 sentences).

## Key Concepts

- **Term**: definition
- **Term**: definition

## How It Works

Step-by-step explanation or diagram description.

## Example

Concrete code snippet or worked example.

## Trade-offs / Considerations

What to watch out for.

## References

- [Source Title](URL)
- Related page: [Page Name](../path/to/page.md)
```

---

## Style Guide

- **Language**: English by default. Add Traditional Chinese (`zh-hant`) content when the source is in Chinese.
- **Tone**: Technical but approachable. Assume the reader is a software engineer or SRE with basic cloud knowledge.
- **Code blocks**: Always specify a language (` ```python `, ` ```bash `, etc.).
- **Links**: Prefer relative links within the repo. Use absolute links for external resources.
- **Headings**: Use `##` for top-level sections, `###` for subsections. Never skip levels.
- **Lists**: Use `-` for unordered, `1.` for ordered.
- **Callouts**: Use `>` blockquotes for tips, warnings, and "see also" references.

---

## What NOT to Do

- Do **not** modify files under `content/` — they are read-only source material.
- Do **not** delete existing pages without replacing their content or redirecting links.
- Do **not** add personal opinions or unverified claims without citing a source.
- Do **not** commit secrets, API keys, or credentials.
- Do **not** change the `tests/` directory structure without updating the CI workflow.

---

## Validation

Before opening a pull request, the agent should confirm:

1. `tests/test_structure.py` passes (run `python -m pytest tests/`).
2. All internal links in new/modified pages resolve to existing files.
3. The chapter `README.md` has been updated if a new page was added.
4. The top-level `README.md` navigation table is current.

---

## Automated Verification

A GitHub Actions workflow (`.github/workflows/llm-verify.yml`) uses Azure OpenAI to:

- Query the wiki for key topics and verify that answers are grounded in the wiki content.
- Report hallucination risk for pages with low source citation density.

The workflow requires the following repository secrets:

| Secret | Description |
|---|---|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI service API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL (e.g. `https://<resource>.openai.azure.com/`) |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name (e.g. `gpt-4.1`) |

---

## Helpful Prompts for Common Tasks

### Add a page about a new RAG concept

```
You are a wiki maintainer. Add a new page docs/02-rag/<topic>.md following
the page template in AGENTS.md. The topic is: <description>.
Cross-link to docs/02-rag/README.md. Do not modify content/.
```

### Summarise a blog post into the wiki

```
Summarise the key technical points from content/posts/<post>/index.md
and add them to the appropriate docs/ page. Cite the source post.
```

### Check for broken links

```
List all internal markdown links in docs/ and verify each target file exists.
```
