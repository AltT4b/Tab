# Tab Create Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create four skills in `skills/tab/` that guide humans and agents through authoring Tab artifacts (agents, skills, rules, commands) from scratch.

**Architecture:** Four independent `SKILL.md` files, each in its own directory under `skills/tab/`. No dispatcher — each skill is self-contained with its own trigger context, Tab conventions, workflow, and embedded template.

**Tech Stack:** Markdown, YAML frontmatter.

---

### Task 1: `create-agent` skill

**Files:**
- Create: `skills/tab/create-agent/SKILL.md`

**Step 1: Create the directory and write the skill**

```markdown
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
```

**Step 2: Verify structure**

Confirm the file exists and has valid YAML frontmatter:

```bash
ls skills/tab/create-agent/
# Expected: SKILL.md
head -5 skills/tab/create-agent/SKILL.md
# Expected: ---\nname: tab:create-agent\n...
```

**Step 3: Commit**

```bash
git add skills/tab/create-agent/SKILL.md
git commit -m "feat: add tab/create-agent skill"
```

---

### Task 2: `create-skill` skill

**Files:**
- Create: `skills/tab/create-skill/SKILL.md`

**Step 1: Create the directory and write the skill**

```markdown
---
name: tab:create-skill
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

**Naming:** Lowercase, hyphenated (e.g., `create-agent`). For namespaced skills, use a directory prefix (e.g., `tab/create-agent`).

**Frontmatter fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches directory path (e.g., `tab:create-agent`) |
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
name: <namespace>:<skill-name>
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
```

**Step 2: Verify structure**

```bash
ls skills/tab/create-skill/
# Expected: SKILL.md
head -5 skills/tab/create-skill/SKILL.md
# Expected: ---\nname: tab:create-skill\n...
```

**Step 3: Commit**

```bash
git add skills/tab/create-skill/SKILL.md
git commit -m "feat: add tab/create-skill skill"
```

---

### Task 3: `create-rule` skill

**Files:**
- Create: `skills/tab/create-rule/SKILL.md`

**Step 1: Create the directory and write the skill**

```markdown
---
name: tab:create-rule
description: "Use when creating a new Tab rule — writes the rule markdown file with correct structure and placement."
---

# Creating a Tab Rule

## When to use this skill

Invoke this skill whenever you are about to create a new Tab rule from scratch.

## Tab Rule Conventions

**What rules are:** Always-on behavioral guardrails. Rules are loaded automatically — they are never explicitly invoked by users or agents.

**Placement:**
- **Shared** (applies to all agents): `rules/<name>.md`
- **Agent-local** (overrides shared for that agent): `agents/<agent>/rules/<name>.md`

Agent-local rules take precedence over shared rules with the same name.

**Structure:** A single `.md` file (no wrapping directory, unlike skills).

**Naming:** Lowercase, hyphenated (e.g., `no-pii`).

## Workflow

1. Determine the rule name (lowercase-hyphenated).
2. Determine scope: shared (`rules/`) or agent-local (`agents/<agent>/rules/`)?
3. Write the rule `.md` file at the chosen path using the template below.
4. Keep the rule focused and specific — one guardrail per file.
5. Confirm the file is complete before finishing.

## Template

```markdown
# <Rule Name>

[One or two sentences stating the guardrail as a direct behavioral constraint.]

- [Specific constraint]
- [Specific constraint]
```
```

**Step 2: Verify structure**

```bash
ls rules/
# Should include no-pii.md as reference
head -5 skills/tab/create-rule/SKILL.md
# Expected: ---\nname: tab:create-rule\n...
```

**Step 3: Commit**

```bash
git add skills/tab/create-rule/SKILL.md
git commit -m "feat: add tab/create-rule skill"
```

---

### Task 4: `create-command` skill

**Files:**
- Create: `skills/tab/create-command/SKILL.md`

**Step 1: Create the directory and write the skill**

```markdown
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
```

**Step 2: Verify structure**

```bash
ls commands/tab/
# Should include doot.md as reference
head -5 skills/tab/create-command/SKILL.md
# Expected: ---\nname: tab:create-command\n...
```

**Step 3: Commit**

```bash
git add skills/tab/create-command/SKILL.md
git commit -m "feat: add tab/create-command skill"
```
