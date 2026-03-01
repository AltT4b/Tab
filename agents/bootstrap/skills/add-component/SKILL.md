---
name: add-component
description: "Use when bootstrap's plan calls for creating a new Tab plugin component (agent, skill, or rule). Receives a component spec and scaffolds the correct file structure."
---

# Add Component

## Overview

Scaffolds a new Tab plugin component as part of bootstrap's execution workflow. Receives a component spec from a bootstrap plan and creates the correct file structure, frontmatter, and placement.

This skill handles three component types: **agent**, **skill**, and **rule**. Each type section below is self-contained with its own validation, placement rules, and template.

## Workflow

1. **Receive component spec** from the bootstrap plan. The spec includes: type, name, and behavioral description. Scope (shared vs agent-local) may also be specified.
2. **Route to the correct type section** below.
3. **Follow that section's steps** — validation, placement, file creation.
4. **Confirm** the file exists and follows Tab conventions.

---

## Agent

**Validation:**
- Name must be lowercase, hyphenated.
- Abstract agents must be prefixed with `_`.
- Name must not collide with an existing directory in `agents/`.
- Description must be one sentence.
- If extending a parent, the parent must exist and inheritance depth must not exceed two levels.

**Placement:** `agents/<name>/AGENT.md` — agents are always shared.

**Directory structure:**
```
agents/<name>/
├── AGENT.md              # Required
├── skills/               # Optional: agent-specific skills
└── rules/                # Optional: agent-specific rules
```

**Steps:**
1. Validate name and check for collisions in `agents/`.
2. Create directory: `agents/<name>/`.
3. Write `agents/<name>/AGENT.md` using the template below.
4. Verify the file exists: `ls agents/<name>/AGENT.md`.

**Template:**
```
---
name: <name>
description: "<One sentence: what this agent does and when to use it.>"
extends: <parent-path>   # Remove if not extending
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

**Validation:**
- Name must be lowercase, hyphenated.
- Name must not collide with an existing skill at the target scope.
- Description must be one sentence describing when Claude should invoke this skill.

**Placement:**
- **Shared:** `skills/<name>/SKILL.md`
- **Agent-local:** `agents/<agent>/skills/<name>/SKILL.md`

Default to shared unless the bootstrap plan specifies agent-local scope. Agent-local skills take precedence over shared skills with the same name.

**Steps:**
1. Validate name and determine scope (shared or agent-local).
2. Check for naming collisions at the target path.
3. Create directory at the resolved path.
4. Write `SKILL.md` using the template below.
5. Verify the file exists.

**Template:**
```
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

## Rule

**Validation:**
- Name must be lowercase, hyphenated.
- Name must not collide with an existing rule at the target scope.

**Placement:**
- **Shared:** `rules/<name>/<name>.md`
- **Agent-local:** `agents/<agent>/rules/<name>/<name>.md`

Default to shared unless the bootstrap plan specifies agent-local scope.

**Steps:**
1. Validate name and determine scope.
2. Check for naming collisions at the target path.
3. Create directory at the resolved path.
4. Write `<name>.md` using the template below.
5. **Registration (shared rules only):** Add the file path to the `instructions` array in `settings.json`.
6. Verify the file exists and (if shared) that `settings.json` was updated.

**Template:**
```
# <Rule Name>

[One or two sentences stating the guardrail as a direct behavioral constraint.]

- [Specific constraint]
- [Specific constraint]
```
