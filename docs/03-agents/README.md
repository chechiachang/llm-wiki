# Chapter 03 — LLM Agents

Build autonomous agents that use tools, plan multi-step tasks, and coordinate via the Model Context Protocol.

## Pages

| Page | Description |
|---|---|
| [Agent Basics](agent-basics.md) | What agents are, the ReAct loop, tool use |
| [MCP Protocol](mcp-protocol.md) | Model Context Protocol — standardised tool interfaces |
| [Agent Patterns](agent-patterns.md) | Common patterns: planner, critic, multi-agent |

## Key Ideas

- An agent is an LLM equipped with **tools** (functions it can call) and a **loop** (plan → act → observe → repeat).
- The **ReAct** pattern (Reason + Act) is the dominant single-agent framework.
- **MCP (Model Context Protocol)** standardises how tools are described and invoked, enabling interoperability.
- Multi-agent systems decompose complex tasks into specialised sub-agents.

> See also: [Observability — Tracing Agents](../04-observability/tracing.md)
