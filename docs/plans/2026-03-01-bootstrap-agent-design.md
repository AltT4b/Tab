# Bootstrap Agent Design

**Date:** 2026-03-01

## Problem

Bootstrap is currently a skill that researches and produces growth plans for Tab. Add-component is a separate shared skill that scaffolds new components. This creates two issues:

1. Bootstrap can plan but not execute — it proposes components but can't create them.
2. Add-component is a general-purpose scaffolding tool available to any workflow, when it should be scoped to deliberate growth decisions.

## Design

### Bootstrap becomes a directory-bundle agent

```
agents/
├── _base.md
└── bootstrap/
    ├── AGENT.md
    └── skills/
        └── add-component/
            └── SKILL.md
```

**AGENT.md** defines bootstrap's identity as Tab's growth agent — it researches, plans, and executes improvements to Tab's capabilities. It extends `_base.md` for safety defaults.

Frontmatter:
```yaml
name: bootstrap
description: "Tab's growth agent — researches, plans, and executes improvements to Tab's capabilities. Activated when the user explicitly asks Tab to grow or bootstrap new functionality."
extends: _base.md
```

The agent body absorbs the current bootstrap skill content (research methodology, plan format, principles) as behavioral instructions.

### Summon-tab gains routing

Summon-tab adds a routing table evaluated before the default agent:

| Priority | Keywords | Agent |
|----------|----------|-------|
| 1 | "bootstrap", "grow" | `bootstrap/AGENT.md` |
| 2 | (default) | `settings.json → defaultAgent` |

Detection is simple: if a Tab-addressed message contains "bootstrap" or "grow", route to the bootstrap agent. Everything else goes to the default agent.

The routing table structure is designed so future agents can be added as new rows. Bootstrap's route is hardcoded in the skill (not in settings.json) because it's the meta-agent — it has a special relationship with Tab's evolution.

### Add-component is refined and scoped

Add-component moves from shared (`skills/add-component/`) to agent-local (`agents/bootstrap/skills/add-component/`). Refinements:

1. **Plan-driven workflow.** Instead of guessing component type from user messages, the skill receives a spec from bootstrap's plan (type, name, scope, behavior).

2. **Self-contained sections.** Each component type (agent, skill, rule) has fully self-contained validation and placement logic — no shared steps between types. This makes future decomposition into `add-agent`, `add-skill`, `add-rule` as separate skills trivial (extract each section into its own file).

3. **No commands.** The command component type is excluded from this design.

## Migration

### Create
- `agents/bootstrap/AGENT.md`
- `agents/bootstrap/skills/add-component/SKILL.md`

### Modify
- `skills/summon-tab/SKILL.md` — add routing table
- `CLAUDE.md` — update repo structure diagram

### Remove
- `skills/bootstrap/SKILL.md` — replaced by agent
- `skills/add-component/SKILL.md` — moved to agent-local

### No change
- `agents/_base.md`
- `settings.json`
- `skills/research/SKILL.md`
- `rules/no-pii/`

## Future path

- **Decompose add-component** into `add-agent`, `add-skill`, `add-rule` as separate agent-local skills once the templates are battle-tested in bootstrap's workflow.
- **Identity continuity** (memory across sessions, growth history) is a broader Tab feature that will get its own design when ready.
- **More agents** can be added to summon-tab's routing table as Tab grows. Each gets its own row with intent keywords.
