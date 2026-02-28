---
name: research
description: "Use when gathering, comparing, or synthesizing information from any source — web, codebase, or documentation — on any topic."
---

# Research

## Overview

Research is a general-purpose knowledge-gathering skill. It classifies each research request by complexity, routes to the right tools, and delivers findings with cited sources.

Research categories:
- **External** — web search for tools, trends, entities, facts
- **Internal** — codebase archaeology, pattern discovery, architecture understanding
- **Hybrid** — comparing internal implementation against external best practices
- **Documentation** — synthesizing local or remote docs into actionable understanding

Do not trigger for questions answerable from existing knowledge without verification, or for simple file reads that don't require synthesis.

## Classification

Before executing any research, classify the request into a tier:

| Signal | Tier | Tools |
|--------|------|-------|
| Simple factual question, single-source answer likely | **Quick** | WebSearch (external) or Grep/Read (internal) |
| Comparison, multiple options, "what are the approaches" | **Explore** | Multi-query WebSearch + WebFetch, or multi-file Grep/Read |
| Entity discovery, landscape mapping, deep multi-source synthesis | **Deep** | Exa websets (if available) + WebSearch + codebase tools |

**How to classify:**
- If the answer fits in a paragraph and one source suffices → Quick
- If the user asks to compare, evaluate, or survey options → Explore
- If the question requires discovering entities, mapping a landscape, or synthesizing 5+ sources → Deep

State the chosen tier before proceeding. Example: "This is an **Explore**-tier question — I'll compare options from multiple sources."
