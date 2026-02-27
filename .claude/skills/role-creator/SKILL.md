---
name: role-creator
description: This skill should be used when the user wants to create a new role, scaffold a new agent, add a role config, or set up a new worker/orchestrator/peer in the Tab directory. Activates on phrases like "create a role", "new role", "add a role config", "scaffold an agent", "new agent role", or when describing a new specialized agent to build.
---

# Tab Role Creator

Guides creation of new role configurations for the Tab multi-agent framework at `/Users/alttab-macbook/AltT4b/Tab`.

## Role Directory Structure

```
roles/
├── _base/
│   ├── agent/          ← minimal safe defaults (extend for most roles)
│   └── analyst/        ← read-heavy + summarize (extend for research/review roles)
├── researcher/         ← example worker
├── writer/             ← example worker
├── coder/              ← example worker
└── orchestrator/       ← top-level coordinator
```

## Files to Create for a New Role

```
roles/<role-name>/
├── SKILL.md            ← required: frontmatter config + behavioral instructions
├── rules/              ← optional: guardrail markdown files
│   └── <rule>.md
└── output_schema.json  ← optional: for validated structured output
```

## Step-by-Step Creation Process

1. **Name**: lowercase, alphanumeric + hyphens/underscores (`^[a-z0-9_-]+$`)
2. **Base role** — choose the right parent:
   - `_base/agent` — general default, minimal tools
   - `_base/analyst` — pre-configured for read + web + summarize
3. **Orchestration role**:
   - `orchestrator` — top-level coordinator, spawns sub-agents
   - `worker` — executes focused tasks, reports to orchestrator
   - `peer` — collaborates laterally with other agents
4. **Draft SKILL.md** using templates in `references/templates.md`

## SKILL.md Frontmatter Fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | `^[a-z0-9_-]+$` |
| `description` | Yes | When to load this role; activation trigger |
| `extends` | No | Path relative to `roles/`, e.g. `_base/agent` |
| `tools.allow` | No | List of permitted tool names |
| `tools.deny` | No | Takes precedence over `tools.allow` |
| `orchestration.role` | No | `orchestrator`, `worker`, or `peer` |
| `orchestration.reports_to` | No | Parent role name (for workers) |
| `orchestration.can_spawn` | No | List of role names (for orchestrators) |

## SKILL.md Body Sections

Every SKILL.md body should include:

| Section | Purpose |
|---------|---------|
| `## Identity` | Persona statement — who the agent is |
| `## Process` | Ordered steps for how to approach tasks |
| `## Rules` | Behavioral constraints and guardrails |
| `## Output Format` | How to structure and deliver output |

Optional: `## Responsibilities`, `## Stack`, `## Available Agents`

## Tool Access Patterns

| Role type | Typical `allow` | Typical `deny` |
|-----------|-----------------|----------------|
| Read-only analyst | `[read_file, web_fetch, bash]` | `[write_file, delete_file]` |
| Writer | `[read_file, write_file, bash]` | `[web_fetch, delete_file]` |
| Orchestrator | `[bash, read_file, write_file]` | `[delete_file]` |
| Minimal / safe | `[read_file]` | `[]` |

See `references/templates.md` for complete copy-paste templates.
