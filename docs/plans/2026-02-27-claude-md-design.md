# CLAUDE.md Design

**Date:** 2026-02-27
**Topic:** CLAUDE.md — human developer onboarding guide

---

## Context

Tab is a Claude Code plugin that provides a ready-to-use multi-agent system. When installed, users get an orchestrator that decomposes tasks and dispatches specialist sub-agents — researcher, writer, coder — via the Task tool. Each agent is defined as an `AGENT.md` file: YAML frontmatter for config, markdown body for behavioral instructions.

This is an active learning project. Conventions evolve as Claude Code best practices become clearer. The README is the user-facing reference; CLAUDE.md captures where we are, why decisions were made, and what the rules are right now.

---

## Decisions

**Orchestrators dispatch; workers execute.** The orchestrator is the user-facing entry point. It decomposes tasks and dispatches workers as sub-agents via the Task tool. Workers never spawn further agents. This distinction is enforced by tool permissions: orchestrators have `Task`; workers do not.

**AGENT.md is the canonical agent definition.** Config in frontmatter, behavior in the markdown body. Self-describing, diff-friendly, no runtime config.

**Abstract base agents are prefixed with `_`.** Not directly runnable — concrete agents extend them.

**Skills, commands, and rules serve distinct purposes.**
- **Skills** — AI-invoked instruction sets
- **Commands** — user-invoked slash commands
- **Rules** — always-on behavioral guardrails

**Shared assets live at the repo root; agent-local assets take precedence.**

---

## Conventions

Repo structure:
```
Tab/
├── skills/               # Shared across all agents
├── rules/                # Shared guardrails
├── commands/             # Shared slash commands
└── agents/
    ├── _base/            # Abstract base agents (not runnable)
    │   ├── agent/
    │   └── analyst/
    ├── orchestrator/     # User-facing entry point
    ├── researcher/       # Worker: web research
    ├── writer/           # Worker: drafting and editing
    └── coder/            # Worker: software development
```

Agent directory:
```
agents/my-agent/
├── AGENT.md              # Required
├── skills/               # Agent-specific (overrides shared)
├── commands/             # Agent-specific (overrides shared)
├── rules/                # Agent-specific (overrides shared)
└── output_schema.json    # Optional
```

AGENT.md frontmatter:

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches directory name |
| `description` | Yes | One sentence: what it does and when to use it |
| `extends` | No | Path to parent agent, relative to `agents/` |

Naming: lowercase, hyphenated. Inheritance: no more than two levels deep.

---

## Approach Selected

**Option C: Layered (Context → Decisions → Conventions)**

Opens with project context and direction. Then a Decisions section capturing key architectural choices and rationale. Then a Conventions section with practical rules. Grows naturally as the project evolves.

Shared assets use **Option A: Central shared directories** — `skills/`, `rules/`, `commands/` at repo root, with agent-local overrides taking precedence.
