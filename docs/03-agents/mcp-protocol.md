# MCP Protocol (Model Context Protocol)

> **TL;DR** — MCP is an open standard (by Anthropic) that defines how LLM hosts (Claude Desktop, IDEs, agents) discover and call tools from MCP servers, enabling a plugin-like ecosystem for AI agents.

## Overview

Before MCP, every LLM framework defined its own tool format. A tool written for LangChain couldn't be used directly by Claude or a custom OpenAI agent. MCP solves this by specifying:

1. A **JSON-RPC 2.0** transport (stdio or HTTP/SSE).
2. A standard schema for **tool definitions** (name, description, input schema).
3. Standard lifecycle messages (`initialize`, `tools/list`, `tools/call`).
4. **Resources** (file-like context items) and **Prompts** (parametrised prompt templates) as first-class concepts.

## Architecture

```
┌─────────────────────────────────┐
│         MCP Host                │
│  (Claude Desktop, VS Code, etc.)│
│                                 │
│  ┌────────────┐                 │
│  │  MCP Client├──────────────── │──────► MCP Server A (Filesystem)
│  └────────────┘                 │──────► MCP Server B (GitHub)
│        │                        │──────► MCP Server C (Qdrant)
│        │ tool results           │
│        ▼                        │
│    LLM (GPT-4, Claude, etc.)    │
└─────────────────────────────────┘
```

## Key Concepts

- **MCP Host**: The application that runs the LLM and connects to MCP servers (e.g., Claude Desktop, GitHub Copilot, a custom agent).
- **MCP Client**: A library embedded in the host that speaks the MCP protocol.
- **MCP Server**: A process that exposes tools, resources, and prompts via MCP.
- **Tool**: A callable function with a JSON Schema input definition.
- **Resource**: A file or data item the server can expose (read-only).
- **Prompt**: A parametrised template the server provides.

## Minimal MCP Server (Python)

```python
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio

app = Server("wiki-search")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_wiki",
            description="Search the LLM wiki for a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_wiki":
        query = arguments["query"]
        # Your search implementation
        result = f"Found 3 results for '{query}'"
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (r, w):
        await app.run(r, w, InitializationOptions(
            server_name="wiki-search",
            server_version="0.1.0",
        ))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## MCP Config in Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wiki-search": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

## Available MCP Servers (Community)

| Server | Function |
|---|---|
| `mcp-server-filesystem` | Read/write local files |
| `mcp-server-github` | GitHub issues, PRs, code |
| `mcp-server-qdrant` | Qdrant vector search |
| `mcp-server-postgres` | PostgreSQL queries |
| `mcp-server-brave-search` | Web search |

Browse: <https://github.com/modelcontextprotocol/servers>

## Trade-offs / Considerations

- **Security**: MCP servers can execute arbitrary code. Sandbox servers handling untrusted input.
- **Authentication**: MCP 1.x has limited auth support. For production, use HTTP+OAuth transport.
- **Discoverability**: The host must be configured with server endpoints; there is no automatic registry.
- **Version compatibility**: The spec is evolving. Pin MCP SDK versions.

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- Source: [COSCUP 2025 — MCP Agent slide deck](../../content/slides/2025-08-09-coscup-mcp-agent.md)
