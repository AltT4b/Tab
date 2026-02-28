---
name: create-skill
description: "Use when creating a new Tab skill — writes the SKILL.md file with correct frontmatter, structure, and placement."
---

# Creating a Tab Skill

## When to use this skill

Invoke this skill whenever you are about to create a new Tab skill from scratch.

## Tab Skill Conventions

**What skills are:** AI-invoked instruction sets. Skills are not user-invoked slash commands — those are commands.

**Placement:**
- **Shared** (available to all agents): `skills/<name>/SKILL.md`
- **Agent-local** (overrides shared for that agent): `agents/<agent>/skills/<name>/SKILL.md`

Agent-local skills take precedence over shared skills with the same name.

**Structure:** Each skill is a directory named after the skill, containing a single `SKILL.md` file.

**Naming:** Lowercase, hyphenated (e.g., `create-agent`). The name matches the directory name.

**Frontmatter fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches directory name (e.g., `create-agent`) |
| `description` | Yes | One sentence describing when Claude should invoke this skill |

## Workflow

1. Determine the skill name (lowercase-hyphenated).
2. Determine scope: shared (`skills/`) or agent-local (`agents/<agent>/skills/`)?
3. Create the directory at the chosen path.
4. Write `SKILL.md` using the template below.
5. Fill in the frontmatter and body.
6. Confirm the file is complete before finishing.

## Template

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
