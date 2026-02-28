---
name: create-command
description: "Use when creating a new Tab command — writes the command markdown file with correct frontmatter, naming, and placement."
---

# Creating a Tab Command

## When to use this skill

Invoke this skill whenever you are about to create a new Tab slash command from scratch.

## Tab Command Conventions

**What commands are:** User-invoked slash commands. Commands are explicitly triggered by users (e.g., `/doot`), not automatically loaded like rules or AI-invoked like skills.

**Placement:**
- **Shared** (available to all agents): `commands/<name>.md`
- **Agent-local** (overrides shared for that agent): `agents/<agent>/commands/<name>.md`

Agent-local commands take precedence over shared commands with the same name.

**Naming:** Lowercase, hyphenated (e.g., `doot`). The name matches the file name.

**Frontmatter fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches file name (e.g., `doot`) |
| `description` | Yes | One sentence: what the command does |

## Workflow

1. Determine the command name.
2. Determine scope: shared (`commands/`) or agent-local (`agents/<agent>/commands/`)?
3. Create the path: `commands/<name>.md`
4. Write the command `.md` using the template below.
5. Confirm the file is complete before finishing.

## Template

```markdown
---
name: <command-name>
description: "<One sentence: what this command does.>"
---

[Instructions for what Claude should do when this command is invoked.]
```
