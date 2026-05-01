"""
LLM quality verification tests using Azure OpenAI.

These tests query the wiki's key topics using an LLM and verify that:
1. The LLM can find relevant information from the wiki content.
2. Answers are grounded (faithfulness > threshold).
3. Core concepts are covered in the wiki.

Requires environment variables:
  AZURE_OPENAI_API_KEY
  AZURE_OPENAI_ENDPOINT
  AZURE_OPENAI_DEPLOYMENT

Run with: pytest tests/test_llm_verify.py -v
Skip with: pytest tests/ --ignore=tests/test_llm_verify.py
"""

import json
import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Skip entire module if Azure OpenAI env vars are not set
pytestmark = pytest.mark.skipif(
    not all([
        os.environ.get("AZURE_OPENAI_API_KEY"),
        os.environ.get("AZURE_OPENAI_ENDPOINT"),
        os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    ]),
    reason="Azure OpenAI environment variables not set",
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_openai_client():
    from openai import AzureOpenAI
    return AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version="2024-02-01",
    )


def load_wiki_context(topic_keywords: list[str], max_chars: int = 4000) -> str:
    """Load relevant wiki content by keyword matching across docs/."""
    chunks = []
    for md_file in DOCS_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        # Check if file mentions any of the keywords
        if any(kw.lower() in content.lower() for kw in topic_keywords):
            # Take first 800 chars as a representative chunk
            excerpt = content[:800].strip()
            rel_path = md_file.relative_to(REPO_ROOT)
            chunks.append(f"[{rel_path}]\n{excerpt}")
        if sum(len(c) for c in chunks) > max_chars:
            break
    return "\n\n---\n\n".join(chunks)


def ask_llm(question: str, context: str) -> str:
    """Ask the LLM a question with the provided context."""
    client = get_openai_client()
    system = (
        "You are an assistant that answers questions based ONLY on the provided wiki context. "
        "If the answer is not in the context, say 'NOT_FOUND'. "
        "Be concise (2-3 sentences max)."
    )
    user = f"Context:\n{context}\n\nQuestion: {question}"
    resp = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,
        max_tokens=256,
    )
    return resp.choices[0].message.content.strip()


def judge_answer(question: str, context: str, answer: str) -> dict:
    """Use LLM-as-a-judge to score an answer."""
    client = get_openai_client()
    prompt = f"""
You are an impartial judge. Score this answer:

Question: {question}
Context (excerpt): {context[:1000]}
Answer: {answer}

Score faithfulness (0-5): Is every claim supported by the context?
Score relevance (0-5): Does the answer address the question?

Respond in JSON only: {{"faithfulness": X, "relevance": X, "reasoning": "..."}}
"""
    resp = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=200,
    )
    return json.loads(resp.choices[0].message.content)


# ─── Test Cases ───────────────────────────────────────────────────────────────

WIKI_QA_CASES = [
    {
        "id": "rag_definition",
        "question": "What is RAG (Retrieval-Augmented Generation) and what problem does it solve?",
        "keywords": ["rag", "retrieval", "augmented", "generation"],
        "must_contain": ["retriev"],
        "min_faithfulness": 4,
    },
    {
        "id": "embedding_definition",
        "question": "What is an embedding in the context of LLMs?",
        "keywords": ["embedding", "vector", "semantic"],
        "must_contain": ["vector"],
        "min_faithfulness": 4,
    },
    {
        "id": "hallucination_mitigation",
        "question": "How does RAG help reduce LLM hallucination?",
        "keywords": ["hallucination", "rag", "grounding"],
        "must_contain": ["context", "retriev", "ground"],
        "min_faithfulness": 3,
    },
    {
        "id": "langfuse_purpose",
        "question": "What is Langfuse and what does it provide for LLM applications?",
        "keywords": ["langfuse", "observability", "tracing"],
        "must_contain": ["trac"],
        "min_faithfulness": 4,
    },
    {
        "id": "mcp_protocol",
        "question": "What is the Model Context Protocol (MCP)?",
        "keywords": ["mcp", "model context protocol", "tool"],
        "must_contain": ["tool"],
        "min_faithfulness": 3,
    },
    {
        "id": "azure_openai_advantage",
        "question": "What are the advantages of using Azure OpenAI over OpenAI directly?",
        "keywords": ["azure", "openai", "enterprise", "private"],
        "must_contain": ["azure"],
        "min_faithfulness": 3,
    },
]


@pytest.mark.parametrize("case", WIKI_QA_CASES, ids=[c["id"] for c in WIKI_QA_CASES])
def test_wiki_coverage(case):
    """Verify the wiki covers key topics and LLM answers are grounded."""
    context = load_wiki_context(case["keywords"])
    assert context, f"No wiki content found for keywords: {case['keywords']}"

    answer = ask_llm(case["question"], context)
    assert "NOT_FOUND" not in answer, (
        f"Wiki does not contain enough information for: {case['question']}"
    )

    # Check that answer contains expected terms
    answer_lower = answer.lower()
    for term in case["must_contain"]:
        assert term.lower() in answer_lower, (
            f"Answer for '{case['id']}' missing expected term '{term}'.\n"
            f"Answer: {answer}"
        )

    # LLM-as-a-judge faithfulness check
    scores = judge_answer(case["question"], context, answer)
    assert scores["faithfulness"] >= case["min_faithfulness"], (
        f"Low faithfulness ({scores['faithfulness']}/5) for '{case['id']}'.\n"
        f"Reasoning: {scores.get('reasoning', 'n/a')}\n"
        f"Answer: {answer}"
    )


def test_wiki_structure_summary():
    """
    Ask the LLM to summarise the wiki's top-level structure and verify
    it mentions the expected chapters.
    """
    # Load all chapter READMEs
    context_parts = []
    for chapter_dir in sorted(DOCS_DIR.iterdir()):
        readme = chapter_dir / "README.md"
        if readme.exists():
            context_parts.append(readme.read_text(encoding="utf-8")[:400])
    context = "\n\n---\n\n".join(context_parts)

    answer = ask_llm(
        "List the main topics covered in this LLM wiki.",
        context,
    )
    assert "NOT_FOUND" not in answer

    expected_topics = ["rag", "agent", "observ", "deploy", "foundation"]
    answer_lower = answer.lower()
    missing = [t for t in expected_topics if t not in answer_lower]
    assert not missing, (
        f"Wiki summary missing topics: {missing}\nAnswer: {answer}"
    )
