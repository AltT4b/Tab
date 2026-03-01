# add-component Consolidation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace four create-* skills and four create-* commands with a single `add-component` skill and command.

**Architecture:** One consolidated SKILL.md contains all four component types' conventions, workflows, and templates in clearly separated sections. One thin command delegates to it. The eight old files are deleted.

**Tech Stack:** Markdown (SKILL.md, command .md)

---

### Task 1: Create the add-component skill

**Files:**
- Create: `skills/add-component/SKILL.md`

**Step 1: Create the directory**

```bash
mkdir -p skills/add-component
```

**Step 2: Write the consolidated SKILL.md**

Create `skills/add-component/SKILL.md` with the following exact content:

````markdown
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
- **Shared:** `commands/<name>/<name>.md`
- **Agent-local:** `agents/<agent>/commands/<name>/<name>.md`

Agent-local commands take precedence over shared commands with the same name.

**Naming:** Lowercase, hyphenated. The directory and file share the same name.

**Frontmatter:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches directory and file name |
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
````

**Step 3: Commit**

```bash
git add skills/add-component/SKILL.md
git commit -m "feat: add consolidated add-component skill"
```

---

### Task 2: Create the /add-component command

**Files:**
- Create: `commands/add-component/add-component.md`

**Step 1: Create the directory**

```bash
mkdir -p commands/add-component
```

**Step 2: Write the command file**

Create `commands/add-component/add-component.md` with the following exact content:

```markdown
---
name: add-component
description: Add a new component (agent, skill, command, or rule) to the Tab plugin.
---

Use the add-component skill.
```

**Step 3: Commit**

```bash
git add commands/add-component/add-component.md
git commit -m "feat: add /add-component command"
```

---

### Task 3: Delete old create-* skills

**Files:**
- Delete: `skills/create-agent/SKILL.md`
- Delete: `skills/create-skill/SKILL.md`
- Delete: `skills/create-command/SKILL.md`
- Delete: `skills/create-rule/SKILL.md`

**Step 1: Remove skill directories**

```bash
rm -rf skills/create-agent skills/create-skill skills/create-command skills/create-rule
```

**Step 2: Commit**

```bash
git add -A skills/create-agent skills/create-skill skills/create-command skills/create-rule
git commit -m "refactor: remove old create-* skills"
```

---

### Task 4: Delete old create-* commands

**Files:**
- Delete: `commands/create-agent/create-agent.md`
- Delete: `commands/create-skill/create-skill.md`
- Delete: `commands/create-command/create-command.md`
- Delete: `commands/create-rule/create-rule.md`

**Step 1: Remove command directories**

```bash
rm -rf commands/create-agent commands/create-skill commands/create-command commands/create-rule
```

**Step 2: Commit**

```bash
git add -A commands/create-agent commands/create-skill commands/create-command commands/create-rule
git commit -m "refactor: remove old create-* commands"
```

---

### Task 5: Verify final state

**Step 1: Check skill directory**

```bash
ls skills/
```

Expected: `add-component/` present, no `create-*` directories.

**Step 2: Check command directory**

```bash
ls commands/
```

Expected: `add-component/` present, no `create-*` directories.

**Step 3: Read the new skill to confirm content**

Read `skills/add-component/SKILL.md` and verify all four component types are documented with conventions, workflow, and templates.

**Step 4: Read the new command to confirm content**

Read `commands/add-component/add-component.md` and verify it delegates to the skill.
