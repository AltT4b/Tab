---
name: tab:create-agent
description: "Use when creating a new Tab agent — writes the AGENT.md file with correct frontmatter, structure, and placement."
---

# Creating a Tab Agent

## When to use this skill

Invoke this skill whenever you are about to create a new Tab agent from scratch.

## Tab Agent Conventions

**Placement:** Every agent lives in its own directory inside `agents/`.

```
agents/my-agent/
├── AGENT.md              # Required
├── skills/               # Optional: agent-specific skills
├── commands/             # Optional: agent-specific commands
├── rules/                # Optional: agent-specific rules
└── output_schema.json    # Optional
```

**Naming:** Lowercase, hyphenated (e.g., `my-agent`). Abstract (non-runnable) agents are prefixed with `_` (e.g., `_base/agent`).

**Frontmatter fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Must match the directory name exactly |
| `description` | Yes | One sentence: what it does and when to use it |
| `extends` | No | Path to parent agent, relative to `agents/` |

**Inheritance:** Max two levels deep. Abstract agents (prefixed `_`) establish shared defaults and are not directly runnable.

**Body structure:** Three sections — `## Identity`, `## Conduct`, `## Output`.

## Workflow

1. Determine the agent name (lowercase-hyphenated). Is it abstract? Prefix with `_`.
2. Determine if it extends a parent. If so, identify the parent path relative to `agents/`.
3. Create the directory: `agents/<name>/`
4. Write `AGENT.md` using the template below.
5. Fill in the frontmatter and each body section.
6. Confirm the file is complete before finishing.

## Template

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
