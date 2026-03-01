# Tab

Tab is a framework for defining Claude-based AI agents as file-system primitives. Each agent lives in a self-contained directory bundle: an `AGENT.md` file combines YAML frontmatter (configuration) with a markdown body (behavioral instructions that become the system prompt).

This file-first approach keeps agents self-describing, diff-friendly, and composable without runtime configuration overhead.

---

## Repository Structure

```
Tab/
├── .claude-plugin/
│   └── plugin.json         # Plugin manifest
├── agents/                 # Agent directory bundles
│   └── _base/              # Abstract base agents (not directly runnable)
│       └── agent/          # Root base: safe defaults for all agents
├── skills/                 # Shared Claude Code skills
├── rules/                  # Shared guardrails (referenced from settings.json)
└── settings.json           # Plugin settings, including rule references
```

---

## Defining an Agent

Every agent is a directory inside `agents/`. The only required file is `AGENT.md`.

```
agents/my-agent/
├── AGENT.md              # Required: frontmatter config + behavioral instructions
├── skills/               # Bundled Claude Code skills
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

## Conduct

- [Behavioral constraint]

## Output

[How to structure and deliver output]
```

### Frontmatter fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | `^[a-z0-9_-]+$`, matches directory name |
| `description` | Yes | One sentence: what it does and when to use it |
| `extends` | No | Path to parent agent, relative to `agents/` |

---

## Inheritance

Agents can extend a parent via `extends`. The child inherits all parent settings and overrides what it redefines.

Abstract base agents (prefixed `_`) establish shared defaults and are not directly runnable. Concrete agents extend them.

```markdown
---
name: researcher
description: "Web research specialist."
extends: _base/agent
---

## Identity

You are Researcher, a specialist in gathering information from the web.
```

Inheritance is limited to two levels deep.

---

## Shared vs. Agent-Local Assets

Skills and rules can live at the repo root (shared across all agents) or inside an agent directory (agent-specific). Agent-local assets take precedence over shared ones.

| Asset | Purpose |
|-------|---------|
| `skills/` | AI-invoked instruction sets |
| `rules/` | Always-on behavioral guardrails |
