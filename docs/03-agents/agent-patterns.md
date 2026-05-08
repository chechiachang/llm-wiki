# Agent Patterns

> **TL;DR** — Common agent architectural patterns include ReAct (single agent), Planner-Executor, Critic-Revisor, and Multi-Agent; choose based on task complexity and reliability requirements.

## Overview

As agent tasks grow in complexity, simple single-loop agents become unreliable. Architectural patterns provide structure that improves quality, debuggability, and cost efficiency.

## Pattern 1 — ReAct (Single Agent)

The simplest pattern. One LLM reasons and acts in a loop.

```
User → [Think → Act → Observe] × N → Answer
```

**Best for**: Simple, linear tasks with 2–5 tool calls.  
**Weakness**: Unreliable on tasks requiring complex planning.

> See: [Agent Basics](agent-basics.md)

---

## Pattern 2 — Planner / Executor

A **planner** LLM breaks the task into a list of steps. An **executor** LLM carries out each step using tools.

```
User → Planner → [Step 1, Step 2, Step 3]
                       │
                  Executor (per step)
                       │
                  Final Synthesis
```

**Best for**: Multi-step research tasks, code generation pipelines.  
**Trade-off**: Two LLM calls per task minimum; planner errors propagate.

---

## Pattern 3 — Critic / Revisor

After the primary agent produces an answer, a **critic** LLM evaluates it and requests revisions.

```
User → Agent → Draft Answer → Critic → [Pass / Revise]
                    ↑                          │
                    └──────── Revision ←───────┘
```

**Best for**: Code review, content generation, structured output validation.  
**Trade-off**: Increases cost and latency; diminishing returns after 2–3 revision cycles.

---

## Pattern 4 — Multi-Agent (Orchestrator + Specialists)

An **orchestrator** agent delegates sub-tasks to specialised agents, then aggregates results.

```
User → Orchestrator
         ├─► Research Agent (web search, docs)
         ├─► Code Agent (write/test code)
         └─► Writer Agent (format final output)
              └─► Final Answer
```

**Best for**: Complex workflows requiring distinct skill sets (research + code + writing).  
**Trade-off**: Coordination overhead; difficult to debug; cost multiplies with number of agents.

---

## Pattern 5 — RAG Agent (Tool-Augmented Retrieval)

Standard RAG wrapped in an agent loop, allowing the agent to issue multiple retrieval queries and synthesise a grounded answer.

```
User → Agent
         ├─► search_wiki("embeddings")     → chunks
         ├─► search_wiki("vector database") → chunks
         └─► synthesise(all_chunks) → Grounded Answer
```

**Best for**: Knowledge-intensive Q&A where one retrieval pass may miss key context.

---

## Choosing a Pattern

| Complexity | Reliability Needed | Recommended Pattern |
|---|---|---|
| Low (1–3 steps) | Medium | ReAct |
| Medium (3–8 steps) | High | Planner/Executor |
| Output quality critical | High | + Critic/Revisor |
| Heterogeneous sub-tasks | Medium | Multi-Agent |
| Knowledge Q&A | High | RAG Agent |

## Observability Requirements

Any agent beyond single-turn ReAct **must** have structured tracing. Log:
- Each tool call (name, input, output, duration)
- Each LLM call (model, token count, latency)
- Final answer + reasoning chain

> See: [Tracing](../04-observability/tracing.md) | [Langfuse](../04-observability/langfuse.md)

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AutoGen (Microsoft)](https://microsoft.github.io/autogen/)
- [CrewAI](https://docs.crewai.com/)
- Related: [Agent Basics](agent-basics.md) | [MCP Protocol](mcp-protocol.md)
