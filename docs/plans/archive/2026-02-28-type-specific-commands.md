# Type-Specific Commands Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the single `/add-component` command with four type-specific commands (`/add-agent`, `/add-skill`, `/add-command`, `/add-rule`) that constrain inputs before invoking the `add-component` skill.

**Architecture:** Each command is a thin markdown file that locks the component type, parses/validates the name from the inline argument, resolves scope, and hands off to the `add-component` skill. The skill remains the single source of truth for templates and conventions.

**Tech Stack:** Markdown command files following Claude Code plugin conventions.

---

### Task 1: Create /add-agent command

**Files:**
- Create: `commands/add-agent/add-agent.md`

**Step 1: Create the command directory**

```bash
mkdir -p commands/add-agent
```

**Step 2: Write the command file**

Create `commands/add-agent/add-agent.md` with this exact content:

```markdown
---
name: add-agent
description: Create a new agent for the Tab plugin.
---

Create a new **agent** component.

## Input

1. Parse the argument as the agent name. If no argument was provided, ask: "What should the agent be named?"
2. Validate: the name must be lowercase-hyphenated (e.g., `my-agent`). If invalid, explain the constraint and ask again.

Agents are always shared — they live in `agents/<name>/`. No scope question needed.

## Handoff

Invoke the `add-component` skill with these inputs locked in:
- **Type:** agent
- **Name:** (from step 1)
- **Scope:** shared (always)

Do not allow the skill to re-ask for type, name, or scope.
```

**Step 3: Verify the file exists and reads correctly**

Run: `cat commands/add-agent/add-agent.md`
Expected: File contents match the above.

**Step 4: Commit**

```bash
git add commands/add-agent/add-agent.md
git commit -m "feat: add /add-agent command"
```

---

### Task 2: Create /add-skill command

**Files:**
- Create: `commands/add-skill/add-skill.md`

**Step 1: Create the command directory**

```bash
mkdir -p commands/add-skill
```

**Step 2: Write the command file**

Create `commands/add-skill/add-skill.md` with this exact content:

```markdown
---
name: add-skill
description: Create a new skill for the Tab plugin.
---

Create a new **skill** component.

## Input

1. Parse the argument as the skill name. If no argument was provided, ask: "What should the skill be named?"
2. Validate: the name must be lowercase-hyphenated (e.g., `my-skill`). If invalid, explain the constraint and ask again.
3. Ask: "Should this be a shared skill or agent-local?" If agent-local, ask which agent.

## Handoff

Invoke the `add-component` skill with these inputs locked in:
- **Type:** skill
- **Name:** (from step 1)
- **Scope:** shared or agent-local with agent name (from step 3)

Do not allow the skill to re-ask for type, name, or scope.
```

**Step 3: Verify the file exists and reads correctly**

Run: `cat commands/add-skill/add-skill.md`
Expected: File contents match the above.

**Step 4: Commit**

```bash
git add commands/add-skill/add-skill.md
git commit -m "feat: add /add-skill command"
```

---

### Task 3: Create /add-command command

**Files:**
- Create: `commands/add-command/add-command.md`

**Step 1: Create the command directory**

```bash
mkdir -p commands/add-command
```

**Step 2: Write the command file**

Create `commands/add-command/add-command.md` with this exact content:

```markdown
---
name: add-command
description: Create a new command for the Tab plugin.
---

Create a new **command** component.

## Input

1. Parse the argument as the command name. If no argument was provided, ask: "What should the command be named?"
2. Validate: the name must be lowercase-hyphenated (e.g., `my-command`). If invalid, explain the constraint and ask again.
3. Ask: "Should this be a shared command or agent-local?" If agent-local, ask which agent.

## Handoff

Invoke the `add-component` skill with these inputs locked in:
- **Type:** command
- **Name:** (from step 1)
- **Scope:** shared or agent-local with agent name (from step 3)

Do not allow the skill to re-ask for type, name, or scope.
```

**Step 3: Verify the file exists and reads correctly**

Run: `cat commands/add-command/add-command.md`
Expected: File contents match the above.

**Step 4: Commit**

```bash
git add commands/add-command/add-command.md
git commit -m "feat: add /add-command command"
```

---

### Task 4: Create /add-rule command

**Files:**
- Create: `commands/add-rule/add-rule.md`

**Step 1: Create the command directory**

```bash
mkdir -p commands/add-rule
```

**Step 2: Write the command file**

Create `commands/add-rule/add-rule.md` with this exact content:

```markdown
---
name: add-rule
description: Create a new rule for the Tab plugin.
---

Create a new **rule** component.

## Input

1. Parse the argument as the rule name. If no argument was provided, ask: "What should the rule be named?"
2. Validate: the name must be lowercase-hyphenated (e.g., `my-rule`). If invalid, explain the constraint and ask again.
3. Ask: "Should this be a shared rule or agent-local?" If agent-local, ask which agent.

## Handoff

Invoke the `add-component` skill with these inputs locked in:
- **Type:** rule
- **Name:** (from step 1)
- **Scope:** shared or agent-local with agent name (from step 3)

Do not allow the skill to re-ask for type, name, or scope.
```

**Step 3: Verify the file exists and reads correctly**

Run: `cat commands/add-rule/add-rule.md`
Expected: File contents match the above.

**Step 4: Commit**

```bash
git add commands/add-rule/add-rule.md
git commit -m "feat: add /add-rule command"
```

---

### Task 5: Delete old /add-component command

**Files:**
- Delete: `commands/add-component/add-component.md`
- Delete: `commands/add-component/` (directory)

**Step 1: Remove the old command**

```bash
rm -rf commands/add-component
```

**Step 2: Verify it's gone**

Run: `ls commands/`
Expected: Shows `add-agent`, `add-skill`, `add-command`, `add-rule` — no `add-component`.

**Step 3: Commit**

```bash
git add -A commands/add-component
git commit -m "refactor: remove old /add-component command"
```

---

### Task 6: Final verification

**Step 1: Verify all command files exist**

Run: `find commands -name "*.md" | sort`
Expected:
```
commands/add-agent/add-agent.md
commands/add-command/add-command.md
commands/add-rule/add-rule.md
commands/add-skill/add-skill.md
```

**Step 2: Verify the add-component skill is untouched**

Run: `git diff skills/add-component/SKILL.md`
Expected: No output (no changes).

**Step 3: Verify git log shows all commits**

Run: `git log --oneline -6`
Expected: 5 new commits (4 creates + 1 delete) on top of the design doc commit.
