# Tab

A monorepo framework for defining and composing Claude-based AI agents. The central concept is the **agent** — a self-describing directory bundle that encapsulates everything needed to instantiate one: identity, tool permissions, orchestration position, behavioral rules, and output format.

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
name: my-role
description: "One sentence: what this role does and when to use it."
extends: _base/agent
tools:
  allow: [read_file]
  deny: [write_file, delete_file]
orchestration:
  role: worker
  reports_to: orchestrator
---

## Identity

You are MyRole, [brief persona statement].

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
| `description` | Yes | When to load this role |
| `extends` | No | Path relative to `agents/`, e.g. `_base/agent` |
| `tools.allow` | No | Permitted tool names |
| `tools.deny` | No | Blocked tools; takes precedence over allow |
| `orchestration.role` | No | `orchestrator`, `worker`, or `peer` |
| `orchestration.reports_to` | No | Parent role name (workers) |
| `orchestration.can_spawn` | No | Spawnable role names (orchestrators) |

---

## Inheritance

Agents can extend a parent with `extends:`:

```yaml
extends: _base/analyst
```

Merge rules:
- **Scalar fields** — child wins over parent.
- **List fields** (`tools.allow`, `rules`, `skills`, etc.) — union merged; child never loses parent guardrails.
- **Max depth** — 3 levels.
- **No circular inheritance** — detected at load time.
- **No multiple inheritance** — `extends` is a single string.

Abstract agents (prefixed `_`) cannot be instantiated directly.

---

## Orchestration

Set the `orchestration` block in frontmatter to define how an agent participates in multi-agent graphs.

```yaml
orchestration:
  role: orchestrator        # orchestrator | worker | peer
  can_spawn: [researcher, writer]
  can_delegate_to: [researcher, writer]
  max_sub_agents: 5
  delegation_strategy: sequential  # parallel | sequential | conditional
```

**Position types:**
- `orchestrator` — coordinates the graph; spawns and delegates to sub-agents.
- `worker` — receives tasks, executes, returns output to `reports_to`.
- `peer` — lateral collaborator; can call and be called by sibling agents.

---

## Available Models

| Model | ID |
|---|---|
| Claude Opus 4.6 | `claude-opus-4-6` |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` |

---

## Design Docs

- [System Design](docs/plans/2026-02-25-tab-design.md)
- [Implementation Plan](docs/plans/2026-02-25-tab-implementation-plan.md)

---
