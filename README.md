# LLM Wiki

A knowledge base for Large Language Models, RAG systems, agents, observability, and DevOps AI — maintained by [Che-Chia Chang](https://chechia.net).

## Navigation

| Chapter | Topic |
|---|---|
| [01 Foundations](docs/01-foundations/README.md) | LLM basics, embeddings, tokenization, hallucination |
| [02 RAG](docs/02-rag/README.md) | Retrieval-Augmented Generation, vector databases, evaluation |
| [03 Agents](docs/03-agents/README.md) | LLM agents, MCP protocol, agent patterns |
| [04 Observability](docs/04-observability/README.md) | Tracing, Langfuse, LLM-as-a-judge, evaluation loops |
| [05 Deployment](docs/05-deployment/README.md) | Azure OpenAI, Kubernetes, production considerations |
| [06 DevOps AI](docs/06-devops-ai/README.md) | AI-assisted DevOps, internal knowledge bases, automation |

## Content Sources

- **Blog Posts**: [`content/posts/`](content/posts/) — extracted from [chechia.net](https://chechia.net)
- **Slides**: [`content/slides/`](content/slides/) — presentation slide decks

## Agent Instructions

See [`AGENTS.md`](AGENTS.md) for instructions on how an LLM should maintain and update this wiki.

## Contributing

1. Follow the structure in each chapter's `README.md`.
2. Place new concept pages in the appropriate chapter under `docs/`.
3. Source material (blog posts, slides) lives under `content/` and should not be modified directly.
4. Run `tests/` to validate structure before opening a PR.

## Author

**Che-Chia Chang** — SRE, Microsoft MVP, DevOps practitioner and speaker.  
Blog: <https://chechia.net> | GitHub: [@chechiachang](https://github.com/chechiachang)