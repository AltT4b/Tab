# Tab Create Skills Design

**Date:** 2026-02-27
**Topic:** `tab/create-*` skills for authoring Tab artifacts

---

## Goal

Add four skills to `skills/tab/` that guide humans and agents through creating Tab artifacts from scratch. Each skill is self-contained: it knows the relevant conventions, provides a workflow, and embeds a canonical template.

---

## Structure

```
skills/tab/
├── create-agent/
│   └── SKILL.md
├── create-skill/
│   └── SKILL.md
├── create-rule/
│   └── SKILL.md
└── create-command/
    └── SKILL.md
```

Each skill is a directory named after the skill, containing a `SKILL.md`. This matches the Tab and superpowers plugin conventions.

---

## Skills

### `create-agent`

**Trigger:** Creating a new Tab agent.

**Covers:**
- Naming: lowercase-hyphenated; `_`-prefix for abstract (non-runnable) agents
- Placement: `agents/<name>/` directory
- Required frontmatter: `name` (matches directory), `description` (one sentence)
- Optional frontmatter: `extends` (path relative to `agents/`, max 2 levels deep)
- Body structure: `## Identity`, `## Conduct`, `## Output` sections
- Abstract agents: prefixed `_`, not directly runnable, exist to be extended

**Template:** `AGENT.md` stub with frontmatter + Identity/Conduct/Output.

---

### `create-skill`

**Trigger:** Creating a new Tab skill.

**Covers:**
- Skills are AI-invoked instruction sets (not user-invoked)
- Placement: `skills/<name>/SKILL.md` (shared) or `agents/<agent>/skills/<name>/SKILL.md` (agent-local)
- Agent-local skills override shared skills of the same name
- Directory named after the skill, `SKILL.md` inside
- Naming: lowercase-hyphenated

**Template:** `SKILL.md` stub with frontmatter (`name`, `description`) + body.

---

### `create-rule`

**Trigger:** Creating a new Tab rule.

**Covers:**
- Rules are always-on behavioral guardrails — not explicitly invoked
- Placement: `rules/<name>.md` (shared) or `agents/<agent>/rules/<name>.md` (agent-local)
- Agent-local rules override shared rules of the same name
- Naming: lowercase-hyphenated

**Template:** Rule `.md` stub.

---

### `create-command`

**Trigger:** Creating a new Tab command.

**Covers:**
- Commands are user-invoked slash commands
- Placement: `commands/<namespace>/<name>.md` (shared) or `agents/<agent>/commands/<namespace>/<name>.md` (agent-local)
- Naming: `namespace:command-name` (e.g., `tab:doot`)
- Frontmatter: `name`, `description`

**Template:** Command `.md` stub with frontmatter + body.

---

## Decisions

- No dispatcher skill — each skill is triggered directly by name, keeping them independent and composable.
- Shared vs agent-local placement is covered in each skill so the invoker can make an informed choice.
- Templates are embedded in the skill body, not separate files.
