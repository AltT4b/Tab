---
name: tab:create-command
description: "Use when creating a new Tab command — writes the command markdown file with correct frontmatter, naming, and placement."
---

# Creating a Tab Command

## When to use this skill

Invoke this skill whenever you are about to create a new Tab slash command from scratch.

## Tab Command Conventions

**What commands are:** User-invoked slash commands. Commands are explicitly triggered by users (e.g., `/tab:doot`), not automatically loaded like rules or AI-invoked like skills.

**Placement:**
- **Shared** (available to all agents): `commands/<namespace>/<name>.md`
- **Agent-local** (overrides shared for that agent): `agents/<agent>/commands/<namespace>/<name>.md`

Agent-local commands take precedence over shared commands with the same name.

**Naming:** `namespace:command-name` (e.g., `tab:doot`). The namespace matches the directory, the command name matches the file.

**Frontmatter fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | `namespace:command-name` format |
| `description` | Yes | One sentence: what the command does |

## Workflow

1. Determine the command name and namespace.
2. Determine scope: shared (`commands/`) or agent-local (`agents/<agent>/commands/`)?
3. Create the path: `commands/<namespace>/<name>.md`
4. Write the command `.md` using the template below.
5. Confirm the file is complete before finishing.

## Template

```markdown
---
name: <namespace>:<command-name>
description: "<One sentence: what this command does.>"
---

[Instructions for what Claude should do when this command is invoked.]
```
