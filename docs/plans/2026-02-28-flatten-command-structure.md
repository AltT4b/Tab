# Flatten Command Structure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Change commands from `commands/<name>/<name>.md` to `commands/<name>.md` so they register as `tab:<name>` instead of `tab:<name>:<name>`.

**Architecture:** Move four command files out of their subdirectories into flat files. Update all documentation and the add-component skill to reflect the new convention.

**Tech Stack:** Markdown files, git

---

### Task 1: Move command files to flat structure

**Files:**
- Move: `commands/add-agent/add-agent.md` -> `commands/add-agent.md`
- Move: `commands/add-command/add-command.md` -> `commands/add-command.md`
- Move: `commands/add-rule/add-rule.md` -> `commands/add-rule.md`
- Move: `commands/add-skill/add-skill.md` -> `commands/add-skill.md`
- Delete: `commands/add-agent/`, `commands/add-command/`, `commands/add-rule/`, `commands/add-skill/`

**Step 1: Move files out of subdirectories**

```bash
mv commands/add-agent/add-agent.md commands/add-agent.md
mv commands/add-command/add-command.md commands/add-command.md
mv commands/add-rule/add-rule.md commands/add-rule.md
mv commands/add-skill/add-skill.md commands/add-skill.md
```

**Step 2: Remove empty subdirectories**

```bash
rmdir commands/add-agent commands/add-command commands/add-rule commands/add-skill
```

**Step 3: Verify structure**

Run: `ls commands/`
Expected: `add-agent.md  add-command.md  add-rule.md  add-skill.md`

**Step 4: Commit**

```bash
git add -A commands/
git commit -m "refactor: flatten command files from commands/<name>/<name>.md to commands/<name>.md"
```

---

### Task 2: Update add-component skill

**Files:**
- Modify: `skills/add-component/SKILL.md:124-152`

**Step 1: Update command placement paths and naming note**

Change lines 128-134 from:

```markdown
**Placement:**
- **Shared:** `commands/<name>/<name>.md`
- **Agent-local:** `agents/<agent>/commands/<name>/<name>.md`

Agent-local commands take precedence over shared commands with the same name.

**Naming:** Lowercase, hyphenated. The directory and file share the same name.
```

To:

```markdown
**Placement:**
- **Shared:** `commands/<name>.md`
- **Agent-local:** `agents/<agent>/commands/<name>.md`

Agent-local commands take precedence over shared commands with the same name.

**Naming:** Lowercase, hyphenated. The file name matches the command name.
```

**Step 2: Update frontmatter table (line 140)**

Change:

```markdown
| `name` | Yes | Matches directory and file name |
```

To:

```markdown
| `name` | Yes | Matches file name (without .md extension) |
```

**Step 3: Commit**

```bash
git add skills/add-component/SKILL.md
git commit -m "docs: update add-component skill for flat command convention"
```

---

### Task 3: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md:17-20`

**Step 1: Update the component path references**

Change line 19 from:

```markdown
- **Commands** — user-invoked slash commands (`commands/<name>/<name>.md`)
```

To:

```markdown
- **Commands** — user-invoked slash commands (`commands/<name>.md`)
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for flat command convention"
```
