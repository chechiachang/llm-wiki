---
title: "Observe and evaluate LLM applications with Langfuse"
date: "2026-07-01"
source: "https://chechia.net/posts/2026-07-01-langfuse-ai-ent/"
source_repo: "https://github.com/chechiachang/chechiachang.github.io-src/tree/master/content/posts/2026-07-01-langfuse-ai-ent"
tags: ["kubernetes", "openai", "aiops", "devops", "observability", "langfuse"]
event: "K8s Summit / Cloud Summit 2026"
event_url: "https://k8s.ithome.com.tw/2025/session-page/4081"
demo_repo: "https://github.com/chechiachang/llm-o11y"
wiki_pages:
  - "../../docs/04-observability/langfuse.md"
  - "../../docs/04-observability/llm-as-a-judge.md"
  - "../../docs/04-observability/evaluation.md"
---

# LLM O11y：從 Observability 到 Decision System

**Event**: K8s Summit / Cloud Summit 2026  
**Date**: 2026-07-01  
**Type**: Conference talk (40 min)  
**Source**: <https://chechia.net/posts/2026-07-01-langfuse-ai-ent/>

## Abstract

LLM（大型語言模型）應用的興起帶來了新的挑戰，尤其是在觀察性（observability）方面。本分享介紹如何在 AI Agent 開發流程中結合 Langfuse 與 LLM-as-a-judge，建立自動化的驗證與 feedback loop。

## Outline

1. 用 impression 做 model/framework 選擇決策的問題
2. 從 observability 開始: bifrost + langfuse
3. Observability 還不夠：Observability != Decision System
4. LLM-as-a-judge 的價值與限制
5. 從 observability 到 closed-loop feedback system
6. evaluation / dataset / regression / decision gate
7. llm-o11y PoC：decision layer 最小可行實作
8. 把 LLM framework 選擇，從 gambling 變成可驗證決策

## Key Insight

> "Observability is not enough — you need a decision system."

## Demo

<https://github.com/chechiachang/llm-o11y>

1. Trace and observe local LLM coding agent
2. Use LLM-as-a-judge to generate evaluations
3. Extract dataset from daily coding agent observations
4. Run regression tests across LLM frameworks

## Author

Che-Chia Chang — SRE, Microsoft MVP  
<https://chechia.net>
