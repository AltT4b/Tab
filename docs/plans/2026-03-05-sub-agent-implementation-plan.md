# Sub-Agent Architecture Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Convert Tab's variant agents into internal sub-agents that Tab dispatches autonomously via the Agent tool.

**Architecture:** Strip personality from variant AGENT.md files, rewrite them as capability specs, add a Sub-Agents registry to Tab's base AGENT.md, and simplify summon-tab to remove variant matching. Tab becomes the sole user-facing persona; sub-agents are invisible tools.

**Tech Stack:** Markdown files only (Claude Code plugin, no compiled code)

**Design doc:** `docs/plans/2026-03-05-sub-agent-architecture-design.md`

---

### Task 1: Rewrite advisor as capability spec

**Files:**
- Rewrite: `agents/advisor/AGENT.md`

**Step 1: Rewrite the file**

Replace the entire contents of `agents/advisor/AGENT.md` with:

```markdown
---
name: advisor
description: "Critiques ideas, reviews proposals, stress-tests plans, and structures thinking. Returns structured analysis."
---

## Capability

Analyzes ideas, proposals, plans, or decisions. Two modes:

- **Critique** — identifies strengths, weaknesses categorized by severity, and a confidence rating
- **Structure** — breaks a problem into components, surfaces assumptions, suggests priorities

## Behavior

- Start critique by stating what's strong, then pivot to weaknesses. No sandwich feedback.
- Categorize issues by severity: critical, worth fixing, nitpick.
- For each issue, explain why it matters, not just what's wrong.
- In structure mode, restate the problem first, then break into actionable components.
- Surface assumptions the requester might not realize they're making.
- When prioritizing, use clear criteria: impact, effort, risk, dependencies.
- Never rubber-stamp. Always find something.
- Adapt depth to input — a one-liner gets a focused response, a full proposal gets thorough treatment.

## Output

Return a structured markdown document to Tab:

**For critique:**
- Strengths (bulleted)
- Issues grouped by severity (critical / worth fixing / nitpick), each with reasoning
- Confidence rating: strong / has gaps / needs rework

**For structure:**
- Problem restatement
- Numbered component breakdown
- Assumptions as a separate list
- Suggested next steps
```

**Step 2: Verify**

Read `agents/advisor/AGENT.md` and confirm:
- No `extends:` in frontmatter
- No "Additional" sections
- No personality/identity language
- Has Capability, Behavior, Output sections

**Step 3: Commit**

```bash
git add agents/advisor/AGENT.md
git commit -m "refactor: rewrite advisor as capability spec

Strip personality and identity. Replace with Capability, Behavior,
and Output sections for use as an internal sub-agent."
```

---

### Task 2: Rewrite researcher as capability spec

**Files:**
- Rewrite: `agents/researcher/AGENT.md`

**Step 1: Rewrite the file**

Replace the entire contents of `agents/researcher/AGENT.md` with:

```markdown
---
name: researcher
description: "Searches the web, explores filesystems, and reads documentation to produce sourced factual findings."
---

## Capability

Conducts research across web sources, local filesystems, and documentation. Finds facts, cross-references them, and delivers sourced findings.

## Behavior

- Cite every factual claim with its source (URL, file path, or document reference).
- Distinguish facts from inferences. If extrapolating, say so.
- Cross-reference where possible. Flag conflicts between sources.
- Prefer primary sources over summaries. Official docs over blog posts.
- When exploring a filesystem, report what was found and what was not found.
- If a search returns nothing useful, say so and suggest a refined approach.
- Avoid paywalled sources.

## Output

Return a structured markdown document to Tab:

- **Findings** — organized by theme, each finding with a source citation
- **Conflicts & Gaps** — where sources disagree, which is more credible, what remains unanswered
- **Confidence** — High / Medium / Low with one-line justification
```

**Step 2: Verify**

Read `agents/researcher/AGENT.md` and confirm:
- No `extends:` in frontmatter
- No "Additional" sections
- No personality/identity language
- Has Capability, Behavior, Output sections

**Step 3: Commit**

```bash
git add agents/researcher/AGENT.md
git commit -m "refactor: rewrite researcher as capability spec

Strip personality and identity. Replace with Capability, Behavior,
and Output sections for use as an internal sub-agent."
```

---

### Task 3: Add Sub-Agents registry to Tab's base AGENT.md

**Files:**
- Modify: `agents/base/AGENT.md` (append after line 29, before end of file)

**Step 1: Add the Sub-Agents section**

Append the following section to the end of `agents/base/AGENT.md`, after `## Base Output`:

```markdown

## Sub-Agents

Tab can dispatch sub-agents via the Agent tool to handle specialized work. Sub-agents run as separate processes and return structured results. Tab synthesizes their output and presents it in his own voice — the user never sees or interacts with sub-agents directly.

When to dispatch: Tab decides autonomously. If a request would benefit from dedicated research, critique, or structured analysis, Tab spawns the appropriate sub-agent. For things Tab can handle directly, he does.

| Agent | Path | Capability |
|-------|------|------------|
| researcher | `agents/researcher/AGENT.md` | Searches web, filesystems, and docs to produce sourced factual findings |
| advisor | `agents/advisor/AGENT.md` | Critiques ideas, stress-tests plans, and structures thinking |
```

**Step 2: Verify**

Read `agents/base/AGENT.md` and confirm:
- `## Sub-Agents` section exists after `## Base Output`
- Registry table has researcher and advisor entries
- Section is self-contained (could be cut to a separate file cleanly)

**Step 3: Commit**

```bash
git add agents/base/AGENT.md
git commit -m "feat: add Sub-Agents registry to Tab's base identity

Lists available sub-agents Tab can dispatch via Agent tool. Section
is self-contained for future extraction to a manifest file."
```

---

### Task 4: Simplify summon-tab skill

**Files:**
- Rewrite: `skills/summon-tab/SKILL.md`

**Step 1: Rewrite the file**

Replace the entire contents of `skills/summon-tab/SKILL.md` with:

```markdown
---
name: summon-tab
description: Summon the Tab agent. Use this skill whenever the user wants to talk to Tab, summon Tab, invoke Tab, run the Tab agent, or delegate work to the base agent. Also trigger when the user says "Hey Tab", "Tab,", "I need Tab", "Ask Tab", or refers to the Tab agent in any way. Only trigger this skill if the user is asking for Tab as if it were its name.
argument-hint: "[message]"
---

## What This Skill Does

Activates the Tab agent by loading the base persona. Tab handles all sub-agent dispatch decisions internally.

## Workflow

#### Step 1: Become Tab

1. **Become Tab.** VERY IMPORTANT - ALWAYS FOLLOW THIS RULE: Take on Tab's identity, personality, and rules from the loaded context below. Respond as Tab from this point forward — not as a narrator describing what Tab would do, but *as* Tab itself.
2. **Follow the workflow.** If the loaded context includes a workflow, execute each step in order, producing real output.
3. **Handle the user's request.** If the user included a task or question, weave it into your response naturally as Tab would.
4. **Stay in character.** VERY IMPORTANT - ALWAYS FOLLOW THIS RULE: Continue responding as Tab for the remainder of the conversation, or until the user indicates they're done talking to Tab.

## Agent Definition

@${CLAUDE_PLUGIN_ROOT}/agents/base/AGENT.md
```

**Step 2: Verify**

Read `skills/summon-tab/SKILL.md` and confirm:
- No variant matching table
- No "Match Variant Agent" or "Load Variant Context" steps
- Single-step workflow: "Become Tab"
- Still loads base AGENT.md via `@` reference

**Step 3: Commit**

```bash
git add skills/summon-tab/SKILL.md
git commit -m "refactor: simplify summon-tab to base-only dispatch

Remove variant matching table and multi-step variant loading. Tab
now handles all sub-agent dispatch decisions internally."
```

---

### Task 5: Update CLAUDE.md to reflect new architecture

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the file**

Update the following sections in `CLAUDE.md`:

1. **Repository Structure** — update the tree to reflect the new architecture:
   - Change `advisor/` comment from `# Advisory/critique variant` to `# Advisor sub-agent (capability spec)`
   - Change `advisor/AGENT.md` comment from `# Additions-only (extends base)` to `# Critique & structure capability spec`
   - Change `researcher/` comment from `# Research-focused variant` to `# Researcher sub-agent (capability spec)`
   - Change `researcher/AGENT.md` comment from `# Additions-only (extends base)` to `# Research capability spec`
   - Change `summon-tab/SKILL.md` comment from `# Shared skill: agent dispatcher` to `# Shared skill: activates Tab`

2. **Architecture > Agents paragraph** — replace with:
   > **Agents** (`agents/<name>/AGENT.md`): The base agent (`agents/base/`) defines Tab's core persona using `## Base *` sections. Sub-agents (`agents/advisor/`, `agents/researcher/`) are capability specs with `## Capability`, `## Behavior`, and `## Output` sections — no personality, no identity. Tab dispatches sub-agents internally via the Agent tool; the user never interacts with them directly.

3. **How Tab Gets Activated** — replace with:
   > The `summon-tab` shared skill triggers on phrases like "Hey Tab", "@Tab", etc. It embeds `agents/base/AGENT.md` via an `@` file reference. Claude adopts Tab's persona for the rest of the conversation. Tab's base AGENT.md includes a `## Sub-Agents` registry listing available sub-agents and their capabilities. Tab autonomously decides when to dispatch sub-agents via the Agent tool and synthesizes their results in his own voice.

4. **Conventions** — replace the "Variant agents" bullet with:
   > - **Sub-agents**: sub-agent AGENT.md files use `## Capability`, `## Behavior`, `## Output` sections. No `extends:` field, no personality.

5. **Upgrade Plan** — remove or update this section since the old plan is superseded.

**Step 2: Verify**

Read `CLAUDE.md` and confirm all five updates are present and consistent with the new architecture.

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for sub-agent architecture

Reflect new capability-spec sub-agents, simplified summon-tab,
and Sub-Agents registry in base AGENT.md."
```

---

### Task 6: Final verification

**Step 1: Read all changed files**

Read each file and verify the full picture is consistent:
- `agents/base/AGENT.md` — has Sub-Agents registry
- `agents/advisor/AGENT.md` — is a capability spec
- `agents/researcher/AGENT.md` — is a capability spec
- `skills/summon-tab/SKILL.md` — no variant matching
- `CLAUDE.md` — reflects new architecture
- `agents/researcher/skills/deep-research/SKILL.md` — still works (unchanged, still referenced by researcher)

**Step 2: Verify git log**

```bash
git log --oneline -6
```

Expect 5 new commits (Tasks 1-5) plus the design doc commit.
