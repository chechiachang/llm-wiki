# Azure OpenAI

> **TL;DR** — Azure OpenAI provides OpenAI models (GPT-4, embeddings) through Azure's infrastructure with enterprise SLAs, private networking, data residency guarantees, and no data-training by default.

## Overview

Azure OpenAI Service is an Azure-managed API gateway for OpenAI models. It is the recommended choice for enterprise LLM workloads because:

- Data sent to Azure OpenAI **does not** train or improve OpenAI models.
- Supports **private endpoints** (models accessible only within your VNet).
- Azure RBAC and Entra ID (AAD) authentication.
- Predictable billing in your Azure subscription.
- Regional deployment for data residency compliance.

## Key Concepts

| Concept | Description |
|---|---|
| **Azure OpenAI Resource** | An Azure resource in your subscription (like a managed API gateway) |
| **Deployment** | A specific model version you have provisioned (e.g., `gpt-4.1`) |
| **Endpoint** | Your resource's HTTPS URL: `https://<name>.openai.azure.com/` |
| **API Key** | Secret for key-based auth; prefer Managed Identity for production |
| **Quota** | Tokens-per-minute (TPM) limit per deployment, per region |
| **PTU (Provisioned Throughput Unit)** | Reserved capacity; predictable latency, no throttling |

## Available Models

| Model | Use Case |
|---|---|
| `gpt-4.1` / `gpt-4o` | Chat, agents, RAG generation |
| `gpt-4.1-mini` / `gpt-4o-mini` | Cost-efficient generation |
| `text-embedding-3-large` | High-quality embeddings (3072 dims) |
| `text-embedding-3-small` | Balanced embeddings (1536 dims) |
| `text-embedding-ada-002` | Legacy; still widely used |
| `o3`, `o4-mini` | Complex reasoning tasks |

## Python SDK Setup

```python
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],     # https://<name>.openai.azure.com/
    api_version="2024-02-01",
)

# Chat completion
response = client.chat.completions.create(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],  # deployment name, not model name
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Managed Identity (no API key)

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

client = AzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)
```

## Handling Rate Limits and Retries

```python
import time
from openai import RateLimitError

def chat_with_retry(client, model, messages, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(model=model, messages=messages)
        except RateLimitError as e:
            wait = 2 ** attempt
            print(f"Rate limited. Retrying in {wait}s…")
            time.sleep(wait)
    raise RuntimeError("Max retries exceeded")
```

Or use the built-in retry configuration:

```python
from openai import AzureOpenAI
import httpx

client = AzureOpenAI(
    ...,
    max_retries=5,
    timeout=httpx.Timeout(60.0, connect=5.0),
)
```

## Quota Management

- Check quotas in Azure Portal → Azure OpenAI → Quotas.
- Request quota increases via the portal (may take 1–3 business days).
- For predictable throughput, use **PTU** (Provisioned Throughput Units).
- Distribute requests across multiple regions if global quota is insufficient.

## Private Endpoint Setup

1. Create an Azure OpenAI resource with Public network access: **Disabled**.
2. Create a Private Endpoint in your VNet pointing to the OpenAI resource.
3. Create a Private DNS Zone `privatelink.openai.azure.com`.
4. Your services access the endpoint via private IP — no public internet.

> Used in the RAG Workshop: [DevOpsDay 2025 — Azure Bastion setup](../../content/slides/2025-06-05-devops-rag-internal-ai.md)

## References

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)
- [Quota and Limits](https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits)
- [Private Endpoints for Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/cognitive-services-virtual-networks)
