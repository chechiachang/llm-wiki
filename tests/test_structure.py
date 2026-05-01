"""
Structural tests for the LLM wiki.

Tests:
- Every docs/ chapter has a README.md
- Every page linked from a chapter README actually exists
- Every content/posts and content/slides file referenced in docs/ pages exists
- No broken relative links within docs/
"""

import os
import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
CONTENT_DIR = REPO_ROOT / "content"

CHAPTER_DIRS = sorted([d for d in DOCS_DIR.iterdir() if d.is_dir()])


# ─── Helpers ──────────────────────────────────────────────────────────────────

def extract_md_links(filepath: Path) -> list[tuple[str, str]]:
    """Return list of (link_text, link_target) for all markdown links in file."""
    content = filepath.read_text(encoding="utf-8")
    # Match [text](target) but not ![alt](image)
    return re.findall(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", content)


def resolve_link(source_file: Path, target: str) -> Path:
    """Resolve a relative markdown link from source_file to an absolute path."""
    # Strip fragment (#section)
    target = target.split("#")[0]
    if not target:
        return source_file  # self-link, always valid
    if target.startswith("http://") or target.startswith("https://"):
        return None  # external link, skip
    return (source_file.parent / target).resolve()


# ─── Tests ────────────────────────────────────────────────────────────────────

def test_each_chapter_has_readme():
    """Every numbered chapter directory under docs/ must have a README.md."""
    for chapter in CHAPTER_DIRS:
        readme = chapter / "README.md"
        assert readme.exists(), f"Missing README.md in {chapter.relative_to(REPO_ROOT)}"


def test_docs_files_are_markdown():
    """All files under docs/ must have .md extension (no stray files)."""
    for path in DOCS_DIR.rglob("*"):
        if path.is_file():
            assert path.suffix == ".md", (
                f"Non-markdown file found in docs/: {path.relative_to(REPO_ROOT)}"
            )


def test_content_posts_has_readme():
    """content/posts/ must have a README.md."""
    assert (CONTENT_DIR / "posts" / "README.md").exists()


def test_content_slides_has_readme():
    """content/slides/ must have a README.md."""
    assert (CONTENT_DIR / "slides" / "README.md").exists()


def test_top_level_readme_exists():
    """Top-level README.md must exist."""
    assert (REPO_ROOT / "README.md").exists()


def test_agents_md_exists():
    """AGENTS.md must exist at repo root."""
    assert (REPO_ROOT / "AGENTS.md").exists()


@pytest.mark.parametrize("chapter", CHAPTER_DIRS)
def test_chapter_readme_internal_links(chapter):
    """All relative links in a chapter README.md must resolve to existing files."""
    readme = chapter / "README.md"
    if not readme.exists():
        pytest.skip(f"No README.md in {chapter.name}")

    links = extract_md_links(readme)
    for text, target in links:
        resolved = resolve_link(readme, target)
        if resolved is None:
            continue  # external link
        assert resolved.exists(), (
            f"Broken link in {readme.relative_to(REPO_ROOT)}: "
            f"[{text}]({target}) → {resolved} does not exist"
        )


def test_all_docs_internal_links():
    """All relative links in every docs/ .md file must resolve to existing files."""
    broken = []
    for md_file in DOCS_DIR.rglob("*.md"):
        for text, target in extract_md_links(md_file):
            resolved = resolve_link(md_file, target)
            if resolved is None:
                continue  # external link
            if not resolved.exists():
                broken.append(
                    f"{md_file.relative_to(REPO_ROOT)}: [{text}]({target})"
                )
    assert not broken, "Broken internal links found:\n" + "\n".join(broken)


def test_page_template_sections():
    """
    Spot-check that concept pages (non-README) in docs/ have at least
    a top-level heading and an ## Overview or ## Key Concepts section.
    """
    missing = []
    for md_file in DOCS_DIR.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        content = md_file.read_text(encoding="utf-8")
        if not re.search(r"^# .+", content, re.MULTILINE):
            missing.append(f"{md_file.relative_to(REPO_ROOT)}: missing top-level heading")
        if not re.search(r"^## ", content, re.MULTILINE):
            missing.append(f"{md_file.relative_to(REPO_ROOT)}: missing ## section")
    assert not missing, "Pages missing required structure:\n" + "\n".join(missing)


def test_no_secrets_in_docs():
    """Docs must not contain hardcoded API keys or secrets."""
    secret_patterns = [
        r"sk-[A-Za-z0-9]{20,}",           # OpenAI key pattern
        r"[A-Za-z0-9]{32}==[A-Za-z0-9]",  # Base64 token
        r"password\s*=\s*['\"][^'\"]{8,}", # Hardcoded password
    ]
    violations = []
    for md_file in DOCS_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for pattern in secret_patterns:
            if re.search(pattern, content):
                violations.append(f"{md_file.relative_to(REPO_ROOT)}: matches pattern {pattern}")
    assert not violations, "Potential secrets found:\n" + "\n".join(violations)
