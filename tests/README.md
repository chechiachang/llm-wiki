# Tests for the LLM Wiki

This directory contains tests that validate wiki structure and content quality.

## Test Files

| File | Description | Requires Azure OpenAI |
|---|---|---|
| `test_structure.py` | Validates markdown structure, internal links, and page format | No |
| `test_llm_verify.py` | Verifies wiki coverage using Azure OpenAI as a judge | Yes |

## Running Tests

### Structure tests only (no API keys needed)

```bash
pip install pytest
pytest tests/test_structure.py -v
```

### All tests (including LLM verification)

```bash
pip install pytest openai
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4.1"

pytest tests/ -v
```

### Skip LLM tests

```bash
pytest tests/ --ignore=tests/test_llm_verify.py -v
```

## CI

- `test_structure.py` runs on every push and PR (`.github/workflows/ci.yml`).
- `test_llm_verify.py` runs on a nightly schedule and on `main` branch pushes (`.github/workflows/llm-verify.yml`).
