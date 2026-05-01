# Agent Basics

> **TL;DR** — An LLM agent is a language model that can invoke external tools (functions, APIs, databases) in a loop until it completes a task; the ReAct pattern (Reason → Act → Observe) is the standard loop.

## Overview

A bare LLM only produces text. An **agent** wraps that LLM with:
1. A set of **tools** (functions with typed inputs/outputs).
2. A **loop**: the LLM reasons about what to do, calls a tool, observes the result, and repeats until done.
3. A **stopping condition**: the LLM produces a final answer or calls a special "finish" tool.

## The ReAct Loop

```
User Prompt
    │
    ▼
┌──────────────────────────────┐
│  LLM (Thought + Action)      │  ← "I need to search for X. Action: search('X')"
└──────────────┬───────────────┘
               │ tool call
               ▼
┌──────────────────────────────┐
│  Tool Execution              │  ← Returns observation
└──────────────┬───────────────┘
               │ observation
               ▼
┌──────────────────────────────┐
│  LLM (Thought + Next Action) │  ← "The search returned Y. I should now..."
└──────────────┬───────────────┘
               │  (loop until done)
               ▼
          Final Answer
```

## Tool Definition (OpenAI Function Calling)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the internal knowledge base for relevant documentation",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    }
                },
                "required": ["query"],
            },
        },
    }
]
```

## Minimal Agent Loop

```python
import json
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)

def search_docs(query: str) -> str:
    # Your actual implementation here
    return f"Results for '{query}': ..."

def run_agent(user_message: str, max_turns: int = 10):
    messages = [
        {"role": "system", "content": "You are a helpful DevOps assistant. Use tools when needed."},
        {"role": "user", "content": user_message},
    ]
    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content  # Final answer

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)
            if fn_name == "search_docs":
                result = search_docs(**fn_args)
            else:
                result = f"Unknown tool: {fn_name}"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
    return "Max turns reached."

print(run_agent("How do I configure pod resource limits in Kubernetes?"))
```

## Agent vs. Chain

| | Chain | Agent |
|---|---|---|
| Control flow | Fixed, pre-determined | Dynamic, LLM decides |
| Tool use | Optional | Central |
| Predictability | High | Lower |
| Use case | Well-defined pipelines | Open-ended tasks |

## Trade-offs / Considerations

- **Cost**: Each loop iteration makes multiple LLM calls. Budget for 3–10× more tokens than a single-call pipeline.
- **Latency**: Each tool call adds round-trip time. Parallelise tool calls where possible.
- **Safety**: Agents with write access (file system, APIs, databases) can cause irreversible damage. Use confirmation gates or dry-run modes.
- **Observability**: Log every tool call and observation. See [Tracing](../04-observability/tracing.md).

## References

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [ReAct Paper (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- Related: [MCP Protocol](mcp-protocol.md) | [Agent Patterns](agent-patterns.md)
