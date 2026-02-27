# Tab

Tab is a monorepo framework for defining and composing Claude-based AI agents. It treats the **agent** as a first-class, file-system primitive: everything an agent needs — its identity, tool permissions, behavioral rules, output format, and position in an orchestration hierarchy — lives in a single directory bundle.

The core artifact is `AGENT.md`: a file combining YAML frontmatter (configuration) with a markdown body (behavioral instructions that become the system prompt). This file-first approach keeps agents self-describing, diff-friendly, and composable without runtime configuration overhead.

Agents can extend one another through an `extends` field, inheriting and overriding settings from parent definitions. Abstract base agents (prefixed `_`) establish shared defaults; concrete agents like `researcher`, `writer`, `coder`, and `orchestrator` build on top of them.

Orchestration is declared, not hardwired. Each agent specifies its role — `orchestrator`, `worker`, or `peer` — and the relationships between agents are resolved at dispatch time via the `/run-agent` Claude Code skill.

Tab is designed for developers who want a structured, auditable way to build multi-agent Claude workflows without reaching for a full orchestration framework.

---

## Repository Structure

```
Tab/
├── agents/                 # All agent definitions
│   ├── _base/              # Abstract base agents (not directly runnable)
│   │   ├── agent/          # Root base: safe defaults for all agents
│   │   └── analyst/        # Extends agent: read-heavy research defaults
│   ├── researcher/         # Concrete worker: web research specialist
│   ├── writer/             # Concrete worker: content drafting
│   ├── coder/              # Concrete worker: software development
│   └── orchestrator/       # Concrete orchestrator: task coordination
└── docs/
    └── plans/              # Design and implementation docs
```

---

## Defining an Agent

Every agent is a directory inside `agents/`. The only required file is `AGENT.md`.

```
agents/my-agent/
├── AGENT.md              # Required: frontmatter config + behavioral instructions
├── skills/               # Bundled Claude Code skills
├── hooks/                # Claude hook scripts
├── commands/             # Custom slash commands
├── rules/                # Guardrail markdown files
└── output_schema.json    # Optional output validation schema
```

### AGENT.md structure

AGENT.md has two parts: a YAML frontmatter block for machine-readable config, and a markdown body that serves as the agent's behavioral instructions.

```markdown
---
name: my-agent
description: "One sentence: what this agent does and when to use it."
---

## Identity

You are MyAgent, [brief persona statement].

## Process

1. [Step 1]
2. [Step 2]

## Rules

- [Behavioral constraint]

## Output Format

[How to structure and deliver output]
```

### Frontmatter fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | `^[a-z0-9_-]+$` |
| `description` | Yes | When to load this agent |

See [Inheritance](#inheritance) and [Orchestration](#orchestration) for additional frontmatter fields.

---

## Inheritance

Base Agent: _base/agent/AGENT.md
