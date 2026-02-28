# Tab — Developer Guide

## Context

Tab is a framework for defining Claude-based AI agents as file-system primitives. Each agent lives in a self-contained directory bundle: `AGENT.md` provides YAML frontmatter for configuration and a markdown body for behavioral instructions.

This is an active learning project. Conventions evolve as Claude Code best practices become clearer. The README is the user-facing reference; this file captures where we are, why decisions were made, and what the rules are right now.

---

## Decisions

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
    └── _base/            # Abstract base agents (not runnable)
        └── agent/        # Root base: safe defaults for all agents
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
