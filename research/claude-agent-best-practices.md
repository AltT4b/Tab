# Claude-Powered Personal Assistant Agents

Research compiled March 2, 2026. Covers Anthropic's official guidance, industry architectural patterns, and a comparison against Tab's current implementation.

---

## Table of Contents

- [Agent Architecture Patterns](#agent-architecture-patterns)
- [Tool Design](#tool-design)
- [Context Engineering](#context-engineering)
- [Persona Design](#persona-design)
- [Memory Systems](#memory-systems)
- [Multi-Agent Orchestration](#multi-agent-orchestration)
- [Declarative vs. Code-Driven Approaches](#declarative-vs-code-driven-approaches)
- [Tab Comparison](#tab-comparison)
- [Sources](#sources)

---

## Agent Architecture Patterns

Anthropic's "Building Effective Agents" (Dec 2024) defines a complexity ladder. The rule: **start at the bottom and climb only when the simpler approach fails.**

| Level | Pattern | Use When |
|---|---|---|
| 0 | Single LLM call + retrieval + examples | Most tasks — this is enough more often than people think |
| 1 | Prompt chaining | Task decomposes into fixed sequential steps with validation gates |
| 2 | Routing | Distinct input categories need fundamentally different handling |
| 3 | Parallelization | Independent subtasks (sectioning) or consensus (voting) |
| 4 | Orchestrator-workers | Subtasks aren't known in advance — the orchestrator decides at runtime |
| 5 | Evaluator-optimizer | Clear eval criteria exist and iterative refinement adds measurable value |
| 6 | Autonomous agent | Open-ended problems requiring tool-driven loops |
| 7 | Multi-agent | Parallel exploration that exceeds a single context window |

### The Core Agent Loop

Every autonomous agent runs the same cycle:

```
Gather context → Take action → Verify work → Repeat
```

The verification step is non-negotiable. Without it, errors compound across turns and long trajectories collapse.

### Workflows vs. Agents

Anthropic draws a hard line:

- **Workflows** — LLMs orchestrated through predefined code paths. Predictable, consistent, best for well-defined tasks.
- **Agents** — LLMs dynamically direct their own processes and tool usage. Flexible, best when decision-making must happen at runtime.

Most personal assistant tasks are workflows. Agents should be reserved for genuinely open-ended problems.

---

## Tool Design

Anthropic's September 2025 engineering post reframes tools as a new class of software — contracts between deterministic systems and non-deterministic agents.

### Principles

**Fewer, smarter tools.** Performance degrades past 10-15 tools per agent. Consolidate related operations into single tools that return complete context.

| Instead of | Build |
|---|---|
| `get_customer_by_id` + `list_transactions` + `list_notes` | `get_customer_context` (returns everything relevant) |
| `read_logs` | `search_logs` (returns relevant lines + surrounding context) |
| `list_users` + `list_events` + `create_event` | `schedule_event` (finds availability and books it) |

**Primitives over integrations.** Claude Code ships 14 built-in tools (Read, Write, Bash, Grep, Glob, etc.) and composes any workflow from them. A small composable set beats hundreds of specialized wrappers.

**Tool descriptions are prompts.** The description field drives the LLM's decision about when and how to use a tool. Small improvements in clarity yield disproportionate performance gains.

**Namespace related tools.** Group under common prefixes (`asana_search`, `jira_search`) to help agents navigate crowded tool environments.

**Optimize for token efficiency.** Return only relevant data. Implement pagination, truncation, filtering. Enrich responses with context to prevent multi-call chains.

---

## Context Engineering

Anthropic's September 2025 guide marks a shift from prompt engineering to context engineering — curating the right tokens at the right time.

### Key Findings

- **Context rot is real.** As token count grows, recall degrades. Context is a finite resource with diminishing returns.
- **Organize prompts into sections.** Use markdown headers or XML tags to create clear regions: instructions, context, tool guidance, output description.
- **Hit the Goldilocks zone.** Too specific = brittle if/else logic. Too vague = no concrete signals. Aim for the minimal set of information that fully outlines expected behavior.
- **Examples outperform rule lists.** A handful of well-crafted few-shot examples dramatically improve accuracy and consistency. Anthropic calls examples "the pictures worth a thousand words."
- **Explain the why.** Telling Claude *why* a behavior matters (not just what to do) helps it generalize to novel situations.

### Production Context Management

Claude Code implements auto-compaction at ~92% context utilization — pruning history while preserving critical tokens, then re-reading instruction files (CLAUDE.md) to prevent amnesia.

For long-running agents, Anthropic recommends progress artifacts: a `claude-progress.txt` file + git history that new sessions read to understand current state.

---

## Persona Design

Persona isn't cosmetic. It directly impacts trust, safety, predictability, and output quality.

### Four Layers of Effective Persona

1. **Identity** — Name, role, expertise domain, perspective
2. **Behavior** — Communication style, reasoning approach, format defaults, uncertainty handling
3. **Boundaries** — What the agent will and won't do, escalation triggers, safety constraints
4. **Process** — How the agent approaches tasks (ask clarifying questions? provide options? step-by-step?)

### Best Practices

- **Modular composition.** Base persona + role overlays + task-specific adjustments. Maintain consistency while allowing specialization.
- **Avoid the generic trap.** "You are a helpful AI assistant" defines no expertise, no process, no output format, no constraints. It produces interchangeable, unreliable output.
- **Never sycophantic.** Hollow affirmations ("Great question!") erode trust.
- **The SOUL.md pattern.** A single file as source of truth for personality, tone, boundaries, and defaults — easy to audit, version, and ship.

---

## Memory Systems

Memory is the defining layer that separates chatbots from assistants. Every major source — Anthropic's own docs, academic research, practitioner guides — converges on this.

### Three Cognitive Types

| Type | Stores | Example |
|---|---|---|
| **Semantic** | Facts, preferences, domain knowledge | "User prefers Python over JavaScript" |
| **Episodic** | Past interactions, events, outcomes | "Last week we debugged a memory leak in their Node app" |
| **Procedural** | Learned workflows, successful strategies | "When deploying to prod, always run smoke tests first" |

### Tiered Architecture

1. **Working memory** — The LLM's context window. Active, limited, must be actively managed.
2. **Session memory** — Spans one conversation. Buffer, sliding window, or summary-based.
3. **Long-term memory** — Persists across sessions. Vector stores + structured databases.

### Retrieval Strategy

Production systems combine multiple retrieval methods:

- Keyword search for exact matches
- Semantic/vector search for conceptual relevance
- Recency weighting for fresh context
- Importance scoring for high-impact memories
- Graph-based retrieval for relationship-aware recall

The write pipeline matters equally: what gets stored, how it's chunked, and what metadata attaches to it determines retrieval quality downstream.

### Anthropic's Approach

The memory tool operates client-side via a file directory. Claude checks its memory before starting tasks and performs CRUD operations on memory files. This enables just-in-time context retrieval rather than loading everything upfront.

---

## Multi-Agent Orchestration

### Anthropic's Production Numbers

From the Research feature (June 2025):

- Multi-agent (Opus 4 lead + Sonnet 4 subagents) outperformed single-agent Opus 4 by **90.2%** on research tasks
- Token usage explains **80% of performance variance**
- Multi-agent runs consume ~**15x more tokens** than standard chat
- Parallel tool calling cuts research time by up to **90%**

### Topology Patterns

| Pattern | Strength | Weakness |
|---|---|---|
| Hierarchical (supervisor) | Clear chain of command | Bottleneck at supervisor |
| Peer-to-peer / swarm | Resilient, no single point of failure | Hard to debug and coordinate |
| Pipeline / sequential | Predictable execution | Inflexible to dynamic tasks |
| Agents-as-tools | Clean hierarchy, composable | More complex initial setup |

### Claude Code's Two Systems

**Subagents** (Task tool) — Spawned within one session with isolated context windows. Return only summaries. Cheaper. Best for delegating focused work.

**Agent Teams** — Separate Claude Code instances coordinating through shared JSON files on disk. No database, no message broker — purely file-based coordination. More expensive, more capable for truly parallel work.

### Prompt Engineering for Multi-Agent

1. Parallelize aggressively — 3-5 subagents, each using 3+ tools in parallel
2. Guide thinking — extended thinking mode as a controllable scratchpad
3. Start wide, then narrow — broad queries first, progressively focused
4. Structured output from subagents — clear schemas for efficient synthesis
5. Limit subagent scope — one focused task per subagent
6. Track citations — dedicated citation processing for source attribution

---

## Declarative vs. Code-Driven Approaches

### The Spectrum

| Level | Approach | Example |
|---|---|---|
| 0 | Raw code | Direct API calls, while loops |
| 1 | Light framework | Smolagents, PydanticAI |
| 2 | Full framework | LangGraph, CrewAI |
| 3 | Declarative/config | YAML/JSON agent definitions |
| 4 | No-code platforms | Visual builders |
| 5 | Pure text, LLM-as-runtime | Tab |

### The Practitioner Consensus

Use declarative for **what the agent is** (identity, persona, tool declarations, constraints). Use code for **how the agent executes** (complex orchestration, error handling, dynamic routing).

### Trade-offs at Level 5 (Tab's Position)

| Advantage | Disadvantage |
|---|---|
| Maximum simplicity | No programmatic control flow |
| Zero dependencies | Limited error handling |
| No build/deploy pipeline | Dependent on LLM correctly interpreting instructions |
| Any text editor can modify behavior | No type safety or schema validation |
| Entirely human-readable | Harder to test systematically |
| Instantly versionable in git | No evaluation framework |

### Notable Frameworks for Reference

| Framework | Stars | Key Differentiator |
|---|---|---|
| **AutoGPT** | 170K+ | Pioneered autonomous goal-driven loops |
| **LangGraph** | 12K+ | Graph-based stateful workflows, strongest observability |
| **CrewAI** | 25K+ | Role-based agent teams, fastest-growing, easiest learning curve |
| **AutoGen** | 40K+ | Multi-agent conversation orchestration (Microsoft) |
| **Smolagents** | 24K+ | Radical simplicity (~1K lines), code-generation approach |
| **Claude Agent SDK** | 15K+ | Claude Code's engine extracted as a library |

---

## Tab Comparison

### Where Tab Aligns

| Best Practice | Tab's Implementation |
|---|---|
| Start simple | Markdown-only, zero dependencies — can't get simpler |
| Modular persona | Base agent + variant overlays via `extends` |
| Anti-sycophancy | Explicit voice rules against hollow affirmations |
| Structured prompt sections | YAML frontmatter + markdown headers |
| Skill-as-tool pattern | Skills with description-based triggers |
| Composable architecture | Plugin manifest + agent discovery |
| Explain the why | Voice guidelines include reasoning, not just rules |

### Where Tab Drifts

| Gap | What Research Says | Tab's State | Severity |
|---|---|---|---|
| **No memory** | Memory is the critical differentiator between chatbot and assistant. Tiered (working → session → long-term) is the standard. | Zero memory. No session persistence, no long-term recall. | **High** |
| **No verification loop** | Every action should include a verification step. Gather → Act → Verify → Repeat. | No built-in verification. No self-check, no quality gate. | **Medium-High** |
| **No few-shot examples** | Examples dramatically improve consistency. "Pictures worth a thousand words." | AGENT.md describes voice abstractly but provides zero examples of target output. | **Medium** |
| **No evaluation framework** | Build evals early — they compound in value and prevent reactive loops. | No eval tasks, no graders, no way to measure if changes improve Tab. | **Medium** |
| **Stubbed base skills** | Tools are prominent in context and shape what actions the agent considers. | Base Skills section reads "STUBBED." Core persona has no default capabilities. | **Medium** |
| **No process layer in base** | Effective personas define how the agent approaches tasks. | Base AGENT.md defines voice and rules but no default workflow. Researcher has one; base doesn't. | **Medium** |
| **No structured error handling** | Agents need fallback patterns, escalation paths, graceful degradation. | Single rule: "don't fabricate." No escalation, no fallback strategies. | **Low-Medium** |
| **No context management** | Production agents implement compaction, selective retrieval, progress artifacts. | Relies entirely on Claude Code to manage context. | **Low** |
| **No continuation strategy** | Long-running tasks need progress files and incremental work patterns. | Session-scoped only. No progress artifacts. | **Low** |

---

## Sources

### Anthropic Official

- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — Dec 2024
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Sep 2025
- [Writing Effective Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Sep 2025
- [How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) — Jun 2025
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Nov 2025
- [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — Sep 2025
- [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Jan 2026
- [Framework for Safe and Trustworthy Agents](https://anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents) — Aug 2025
- [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) — Current
- [Memory Tool Docs](https://console.anthropic.com/docs/en/agents-and-tools/tool-use/memory-tool) — Current

### Architecture and Patterns

- [Claude Code Architecture (Reverse Engineered)](https://vrungta.substack.com/p/claude-code-architecture-reverse)
- [Inside Claude Code: Deep-Dive Reverse Engineering Report](https://www.blog.brightcoding.dev/2025/07/17/inside-claude-code-a-deep-dive-reverse-engineering-report)
- [Claude Code Agent Teams Reverse Engineered](https://nwyin.com/blogs/claude-code-agent-teams-reverse-engineered)
- [Claude Agent SDK Python (GitHub)](https://github.com/anthropics/claude-agent-sdk-python)
- [Redis: AI Agent Architecture Patterns](https://redis.io/blog/ai-agent-architecture-patterns/)

### Persona and Identity

- [SOUL.md Pattern](https://amirbrooks.com.au/guides/soul-md-pattern-ai-agent-personality)
- [Designing Agent Personas](https://agenticthinking.ai/blog/agent-personas/)
- [The Persona Pattern](https://pub.towardsai.net/the-persona-pattern-unlocking-modular-intelligence-in-ai-agents-35061513da94)

### Memory

- [3 Types of Long-term Memory AI Agents Need](https://machinelearningmastery.com/beyond-short-term-memory-the-3-types-of-long-term-memory-ai-agents-need/)
- [Tiered Agentic Memory for LLMs](https://medium.com/google-cloud/mastering-ais-mind-designing-tiered-agentic-memory-for-llms-4b747afb62c9)

### Frameworks

- [Agent Frameworks Landscape](https://arunbaby.com/ai-agents/0006-agent-frameworks-landscape/)
- [OpenAI Agents SDK vs Claude Agent SDK](https://agentpatch.ai/blog/openai-agents-sdk-vs-claude-agent-sdk)
- [Langfuse: Open-Source AI Agent Frameworks](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)
