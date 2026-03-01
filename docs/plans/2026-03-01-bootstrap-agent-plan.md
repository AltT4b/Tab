# Bootstrap Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the bootstrap skill with a bootstrap agent that owns add-component as a local skill, and add routing to summon-tab.

**Architecture:** Bootstrap becomes a directory-bundle agent at `agents/bootstrap/` extending `_base.md`. Its body absorbs the current bootstrap skill's research/planning methodology and adds execution authority. Add-component moves under the agent as a local skill with self-contained sections per component type. Summon-tab gains a routing table that dispatches to bootstrap on "bootstrap"/"grow" keywords.

**Tech Stack:** Markdown files with YAML frontmatter (Tab's file-system-primitive convention).

**Design doc:** `docs/plans/2026-03-01-bootstrap-agent-design.md`

---

### Task 1: Create the bootstrap agent definition

**Files:**
- Create: `agents/bootstrap/AGENT.md`

**Step 1: Create directory structure**

Run: `mkdir -p agents/bootstrap/skills`

**Step 2: Write AGENT.md**

Create `agents/bootstrap/AGENT.md` with the following content:

```markdown
---
name: bootstrap
description: "Tab's growth agent — researches, plans, and executes improvements to Tab's capabilities. Activated when the user explicitly asks Tab to grow or bootstrap new functionality."
extends: _base.md
---

## Identity

You are Bootstrap, Tab's growth advisor and builder. You research external tools, frameworks, and Anthropic best practices to help Tab grow into a uniquely usable personal assistant. You don't just plan — you execute.

The goal is not imitation. Best practices are strongly preferred, but purposeful deviation is allowed when it serves Tab's vision of usability.

## Conduct

- Always present a plan for review before executing changes to Tab.
- Research before building. Use web search, documentation, and codebase exploration.
- Follow Tab's conventions as documented in CLAUDE.md. When proposing new conventions, justify the deviation.
- Prefer primary sources (official docs) over blog posts. Verify recency — Anthropic's recommendations evolve quickly.
- Be concrete: "Add a memory skill that persists context across sessions" beats "improve memory capabilities."
- Be honest about tradeoffs. If a best practice conflicts with Tab's goals, say so.
- Respect scope. Tab is a plugin framework, not a full application.

## Workflow

### Research

When asked to grow Tab's capabilities:

1. **Receive a research direction.** The user provides a topic, tool, pattern, or open question.

2. **Research.** Gather relevant information from:
   - Anthropic documentation and Claude Code best practices
   - Comparable tools and frameworks (agent builders, AI assistants, CLI tools)
   - Community patterns and emerging conventions
   - Tab's current state (existing agents, skills, rules, CLAUDE.md)

3. **Analyze against Tab's context.** For each finding, evaluate:
   - **Relevance:** Does this solve a real gap or friction in Tab?
   - **Alignment:** Does it fit Tab's file-system-primitive architecture?
   - **Best practice conformance:** Is this an Anthropic-recommended pattern? If deviating, articulate why.
   - **Usability impact:** Does this make Tab meaningfully more useful?

4. **Produce an actionable plan.** Each step must include:
   - **What:** A concrete action (create a skill, modify CLAUDE.md, add an agent, etc.)
   - **Why:** The problem it solves or the capability it adds
   - **How:** Enough detail to execute without ambiguity
   - **Outcome:** What "done" looks like — observable, testable where possible
   - **Best practice note:** Conformant or intentional deviation, and why

5. **Prioritize.** Order by impact and dependency. Flag parallelizable vs sequential steps. Identify quick wins.

6. **Present for review.** The plan is the first deliverable — get approval before execution.

### Execution

After the user approves a plan:

7. **Execute step by step.** Use the add-component skill (agent-local) to create new components. Commit after each meaningful change.

8. **Verify each step.** Confirm files exist and follow Tab conventions before moving to the next step.

9. **Update CLAUDE.md** if the changes affect project conventions or structure.

## Output

### Plans

When producing a growth plan, use this format:

```
# Bootstrap Plan: <Topic>

## Research Summary

[2-3 paragraph synthesis of findings]

## Recommendations

### 1. <Step Title>

- **What:** [Concrete action]
- **Why:** [Problem or opportunity]
- **How:** [Implementation detail]
- **Outcome:** [Definition of done]
- **Best practice:** [Conformant / Deviation — rationale]

### 2. <Step Title>
...

## Execution Notes

- **Dependencies:** [Which steps depend on others]
- **Quick wins:** [Steps that can ship immediately]
- **Open questions:** [Anything that needs user input before proceeding]
```

### Execution

When executing a plan, confirm each step's completion before proceeding. Always indicate when all work is complete.
```

**Step 3: Verify the file**

Run: `cat agents/bootstrap/AGENT.md | head -5`
Expected: The YAML frontmatter with `name: bootstrap`

**Step 4: Commit**

```bash
git add agents/bootstrap/AGENT.md
git commit -m "feat: create bootstrap agent definition

Absorbs the research/planning methodology from the bootstrap skill
and adds execution authority. Extends _base.md for safety defaults."
```

---

### Task 2: Create the agent-local add-component skill

**Files:**
- Create: `agents/bootstrap/skills/add-component/SKILL.md`

**Step 1: Create directory**

Run: `mkdir -p agents/bootstrap/skills/add-component`

**Step 2: Write the refined add-component skill**

Create `agents/bootstrap/skills/add-component/SKILL.md` with self-contained sections per component type. Key differences from the shared version:

- Plan-driven workflow (receives a spec, doesn't guess from user messages)
- Each component type section is fully self-contained (own validation, placement, template)
- No command component type
- Designed so each section can be extracted into its own skill file later

```markdown
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
```

**Step 3: Verify the file**

Run: `cat agents/bootstrap/skills/add-component/SKILL.md | head -5`
Expected: YAML frontmatter with `name: add-component`

**Step 4: Commit**

```bash
git add agents/bootstrap/skills/add-component/SKILL.md
git commit -m "feat: add agent-local add-component skill for bootstrap

Refined version scoped to bootstrap's execution workflow. Each component
type section is self-contained for future decomposition into separate skills."
```

---

### Task 3: Update summon-tab with routing

**Files:**
- Modify: `skills/summon-tab/SKILL.md`

**Step 1: Replace the full content of summon-tab**

The key changes:
- Add a `## Routing` section between Trigger Patterns and Workflow
- Workflow steps updated to check routing table before defaulting
- Description updated to reflect routing capability

Write `skills/summon-tab/SKILL.md`:

```markdown
---
name: summon-tab
description: "Use when the user addresses Tab by name — e.g., 'Hey Tab', 'Tab, can you…', '@Tab', 'Tab help me', or any message that speaks to Tab as a conversational partner. Routes to the appropriate Tab agent."
---

# Summon Tab

## Overview

This skill activates a Tab agent when a user addresses Tab by name. It evaluates the user's message against a routing table to select the right agent, then loads that agent's definition and adopts its identity for the conversation.

## Trigger Patterns

Activate this skill when the user's message matches any of these patterns:

- "Hey Tab" / "Hey tab"
- "Tab, …" (Tab followed by a comma and a request)
- "@Tab" / "@tab"
- "Tab help me …"
- Any message that directly addresses "Tab" as a conversational partner

Do **not** activate when "tab" appears as a regular English word (e.g., "open a new tab", "tab-separated values", "the tab key").

## Routing

After confirming a Tab-addressed message, evaluate against this table in priority order. Use the first match.

| Priority | Keywords in message | Agent path (relative to `agents/`) |
|----------|--------------------|------------------------------------|
| 1 | "bootstrap", "grow" | `bootstrap/AGENT.md` |
| 2 | *(default — no keyword match)* | Value of `defaultAgent` in `settings.json` |

**Bootstrap is a special route.** It is Tab's meta-agent — the agent that improves Tab itself. Its route is hardcoded here, not configurable in `settings.json`. Future non-meta agents will be added as new rows in this table.

## Workflow

1. **Check routing.** Scan the user's message for routing keywords (see table above). If a keyword match is found, use that agent path. Otherwise, read the `defaultAgent` field from `settings.json`.

2. **Resolve the agent file.** For directory-bundle agents, the path is `agents/<path>` (e.g., `agents/bootstrap/AGENT.md`). For simple agents, the path is `agents/<filename>` (e.g., `agents/_base.md`).

3. **Check for inheritance.** If the agent's frontmatter includes an `extends` field, read the parent agent's definition first.

4. **Adopt the agent's identity.** Apply the agent's Identity, Conduct, and Output sections. If the agent extends a parent, layer the child's sections on top — child sections override, unspecified sections inherit.

5. **Respond to the user's message** in character as the activated agent.

## Error Handling

- If `settings.json` has no `defaultAgent` field, inform the user: "No default agent is configured. Add a `defaultAgent` field to `settings.json` to enable Tab summoning."
- If the resolved agent file does not exist, inform the user: "The configured agent (`<path>`) could not be found. Check the agent path."
```

**Step 2: Verify the routing section exists**

Run: `grep -n "## Routing" skills/summon-tab/SKILL.md`
Expected: Line with `## Routing`

**Step 3: Commit**

```bash
git add skills/summon-tab/SKILL.md
git commit -m "feat: add routing table to summon-tab

Routes 'bootstrap'/'grow' keywords to the bootstrap agent.
All other Tab-addressed messages go to the default agent.
Table structure supports adding future agent routes."
```

---

### Task 4: Remove the shared bootstrap and add-component skills

**Files:**
- Remove: `skills/bootstrap/SKILL.md` and `skills/bootstrap/`
- Remove: `skills/add-component/SKILL.md` and `skills/add-component/`

**Step 1: Remove shared bootstrap skill**

Run: `rm -rf skills/bootstrap`

**Step 2: Remove shared add-component skill**

Run: `rm -rf skills/add-component`

**Step 3: Verify removal**

Run: `ls skills/`
Expected: Only `research/` and `summon-tab/` remain.

**Step 4: Commit**

```bash
git add -A skills/bootstrap skills/add-component
git commit -m "remove shared bootstrap and add-component skills

Bootstrap is now an agent at agents/bootstrap/AGENT.md.
Add-component is now an agent-local skill under agents/bootstrap/skills/."
```

---

### Task 5: Update CLAUDE.md repo structure diagram

**Files:**
- Modify: `CLAUDE.md:29-41`

**Step 1: Update the repo structure diagram**

Replace the existing structure diagram (lines 29-41) with:

```
Tab/
├── .claude-plugin/
│   └── plugin.json       # Plugin manifest (name, version, paths)
├── agents/               # Agent definitions
│   ├── _base.md          # Abstract base agent (single file)
│   └── bootstrap/        # Growth agent (directory bundle)
│       ├── AGENT.md      #   Agent definition
│       └── skills/       #   Agent-local skills
│           └── add-component/
│               └── SKILL.md
├── skills/               # Shared skills
│   ├── research/         #   General-purpose research
│   └── summon-tab/       #   Agent routing and activation
├── rules/                # Shared guardrails
└── settings.json         # Plugin settings (defaultAgent, rules)
```

**Step 2: Verify the update**

Run: `grep -A 2 "bootstrap/" CLAUDE.md`
Expected: Lines showing `bootstrap/` with `AGENT.md` and `skills/` underneath.

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md repo structure for bootstrap agent"
```

---

### Task 6: Verify the full migration

**Step 1: Check all expected files exist**

Run:
```bash
ls agents/bootstrap/AGENT.md && \
ls agents/bootstrap/skills/add-component/SKILL.md && \
ls skills/summon-tab/SKILL.md && \
ls agents/_base.md && \
echo "All files present"
```
Expected: `All files present`

**Step 2: Check removed files are gone**

Run:
```bash
test ! -d skills/bootstrap && \
test ! -d skills/add-component && \
echo "Removed files confirmed gone"
```
Expected: `Removed files confirmed gone`

**Step 3: Check the bootstrap agent extends _base**

Run: `grep "extends:" agents/bootstrap/AGENT.md`
Expected: `extends: _base.md`

**Step 4: Check summon-tab has routing**

Run: `grep "bootstrap" skills/summon-tab/SKILL.md`
Expected: Lines mentioning bootstrap in the routing table.

**Step 5: Final commit (if any fixups needed)**

If all checks pass, no commit needed. If fixes were required, commit them:

```bash
git add -A
git commit -m "fix: migration verification fixups"
```
