---
name: add-component
description: "Use when creating a new Tab plugin component (agent, skill, command, or rule). Scaffolds the correct file structure, frontmatter, and placement."
---

# Add Component

## Overview

Scaffolds a new Tab plugin component. Supports four component types: **agent**, **skill**, **command**, and **rule**. Each type has its own conventions, placement rules, and template.

## Type Detection

Infer the component type from the user's message. Look for keywords: "agent", "skill", "command", "rule". If the type is ambiguous or missing, ask the user to choose one.

## Workflow

1. **Detect type** — infer from context, ask if ambiguous.
2. **Determine name** — lowercase-hyphenated. For abstract agents, prefix with `_`.
3. **Determine scope** — shared (root-level directory) or agent-local (inside `agents/<agent>/`)? Ask if unclear. Agents are always shared.
4. **Create directory** at the resolved path.
5. **Write the file** using the type-specific template below.
6. **Post-create** — for rules only: add the file path to the `instructions` array in `settings.json`.
7. **Confirm** the file is complete before finishing.

---

## Agent

**What agents are:** Self-contained directory bundles defining a Claude-based AI agent.

**Placement:** `agents/<name>/AGENT.md` (always shared — no agent-local agents).

```
agents/<name>/
├── AGENT.md              # Required
├── skills/               # Optional: agent-specific skills
├── commands/             # Optional: agent-specific commands
├── rules/                # Optional: agent-specific rules
└── output_schema.json    # Optional
```

**Naming:** Lowercase, hyphenated (e.g., `my-agent`). Abstract (non-runnable) agents are prefixed with `_` (e.g., `_base/agent`).

**Frontmatter:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Must match the directory name exactly |
| `description` | Yes | One sentence: what it does and when to use it |
| `extends` | No | Path to parent agent, relative to `agents/` |

**Inheritance:** Max two levels deep. Abstract agents (prefixed `_`) establish shared defaults and are not directly runnable.

**Body structure:** Three sections — `## Identity`, `## Conduct`, `## Output`.

**Template:**

```markdown
---
name: <name>
description: "<One sentence: what this agent does and when to use it.>"
extends: <parent-path>   # Remove this line if not extending
---

## Identity

You are <Name>, [brief persona statement].

## Conduct

- [Behavioral constraint]
- [Behavioral constraint]

## Output

[How to structure and deliver output]
```

---

## Skill

**What skills are:** AI-invoked instruction sets. Skills are not user-invoked slash commands — those are commands.

**Placement:**
- **Shared:** `skills/<name>/SKILL.md`
- **Agent-local:** `agents/<agent>/skills/<name>/SKILL.md`

Agent-local skills take precedence over shared skills with the same name.

**Naming:** Lowercase, hyphenated. The directory name matches the skill name.

**Frontmatter:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches directory name |
| `description` | Yes | One sentence: when Claude should invoke this skill |

**Template:**

```markdown
---
name: <skill-name>
description: "<One sentence: when Claude should invoke this skill.>"
---

# <Skill Title>

## Overview

[What this skill does and why.]

## Workflow

1. [Step]
2. [Step]
3. [Step]
```

---

## Command

**What commands are:** User-invoked slash commands. Explicitly triggered by users (e.g., `/greet`), not automatically loaded like rules or AI-invoked like skills.

**Placement:**
- **Shared:** `commands/<name>.md`
- **Agent-local:** `agents/<agent>/commands/<name>.md`

Agent-local commands take precedence over shared commands with the same name.

**Naming:** Lowercase, hyphenated. The file name matches the command name.

**Frontmatter:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches file name (without .md extension) |
| `description` | Yes | One sentence: what the command does |

**Template:**

```markdown
---
name: <command-name>
description: "<One sentence: what this command does.>"
---

[Instructions for what Claude should do when this command is invoked.]
```

---

## Rule

**What rules are:** Always-on behavioral guardrails. Loaded automatically — never explicitly invoked.

**Placement:**
- **Shared:** `rules/<name>/<name>.md`
- **Agent-local:** `agents/<agent>/rules/<name>/<name>.md`

**Registration:** After creating the file, add its path to the `instructions` array in `settings.json`:

```json
{
  "instructions": [
    "rules/<name>/<name>.md"
  ]
}
```

**Naming:** Lowercase, hyphenated. The directory and file share the same name.

**Template:**

```markdown
# <Rule Name>

[One or two sentences stating the guardrail as a direct behavioral constraint.]

- [Specific constraint]
- [Specific constraint]
```
