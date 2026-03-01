# Design: Consolidate create-* Skills into add-component

## Problem

Four separate skills (`create-agent`, `create-skill`, `create-command`, `create-rule`) and four corresponding commands share the same pattern: conventions, workflow, template. This duplication increases maintenance surface and clutters the skill/command namespace.

## Decision

Consolidate into a single `add-component` skill and a single `/add-component` command. Delete the four originals.

## Skill: add-component

**Location:** `skills/add-component/SKILL.md`

**Description:** "Use when creating a new Tab plugin component (agent, skill, command, or rule). Scaffolds the correct file structure, frontmatter, and placement."

**Structure:** Single file, all component types inline in clearly separated sections (~200 lines).

### Type Detection

The skill infers the component type from the user's message context (keywords: "agent", "skill", "command", "rule"). If ambiguous or missing, it asks the user to choose.

### Scope

Only operates on plugin-declared directories: `agents/`, `skills/`, `commands/`, `rules/`. Agent-local placement is supported for skills, commands, and rules.

### Shared Workflow

1. Detect component type from context; ask if ambiguous
2. Determine name (lowercase-hyphenated; `_` prefix for abstract agents)
3. Determine scope — shared or agent-local
4. Create directory at resolved path
5. Write file using type-specific template
6. Post-create: for rules, register in `settings.json` instructions array
7. Confirm file is complete

### Component Sections

Each section contains conventions, placement rules, frontmatter spec, and an embedded template. Content is carried over from the existing create-* skills with no new conventions.

- **Agent** — `agents/<name>/AGENT.md`, frontmatter: name/description/extends, body: Identity/Conduct/Output
- **Skill** — `skills/<name>/SKILL.md`, frontmatter: name/description, body: Overview/Workflow
- **Command** — `commands/<name>/<name>.md`, frontmatter: name/description
- **Rule** — `rules/<name>/<name>.md`, no frontmatter, register in settings.json

## Command: /add-component

**Location:** `commands/add-component/add-component.md`

Thin entry point: "Use the add-component skill."

## Deletions

Skills to remove:
- `skills/create-agent/`
- `skills/create-skill/`
- `skills/create-command/`
- `skills/create-rule/`

Commands to remove:
- `commands/create-agent/`
- `commands/create-skill/`
- `commands/create-command/`
- `commands/create-rule/`
