# Research Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a general-purpose `research` skill to Tab that auto-classifies research requests into tiers and routes to the appropriate toolchain (Exa websets for deep research, WebSearch/WebFetch for lighter queries, Grep/Read for internal codebase work).

**Architecture:** Single SKILL.md file at `skills/research/SKILL.md`. No code — pure instruction-based skill following Tab's file-system-primitive convention. The skill teaches the agent a 5-step research workflow with tier-based tool routing and adaptive output (conversational for quick/explore, saved report for deep).

**Tech Stack:** Markdown (SKILL.md), YAML frontmatter. References Exa MCP tools, WebSearch, WebFetch, Grep, Glob, Read, Agent tools.

**Design doc:** `docs/plans/2026-02-28-research-skill-design.md`

---

### Task 1: Create the skill directory

**Files:**
- Create: `skills/research/` (directory)

**Step 1: Create the directory**

Run: `mkdir -p skills/research`

**Step 2: Verify**

Run: `ls skills/`
Expected: `add-component/  bootstrap/  research/  summon-tab/`

---

### Task 2: Write SKILL.md frontmatter and overview

**Files:**
- Create: `skills/research/SKILL.md`

**Step 1: Write the frontmatter, title, and overview section**

Write exactly this to `skills/research/SKILL.md`:

```markdown
---
name: research
description: "Use when gathering, comparing, or synthesizing information from any source — web, codebase, or documentation — on any topic."
---

# Research

## Overview

Research is a general-purpose knowledge-gathering skill. It classifies each research request by complexity, routes to the right tools, and delivers findings with cited sources.

Research categories:
- **External** — web search for tools, trends, entities, facts
- **Internal** — codebase archaeology, pattern discovery, architecture understanding
- **Hybrid** — comparing internal implementation against external best practices
- **Documentation** — synthesizing local or remote docs into actionable understanding

Do not trigger for questions answerable from existing knowledge without verification, or for simple file reads that don't require synthesis.
```

**Step 2: Verify the file exists and frontmatter is valid**

Run: `head -5 skills/research/SKILL.md`
Expected: YAML frontmatter with `name: research` and `description` field.

**Step 3: Commit**

```bash
git add skills/research/SKILL.md
git commit -m "feat(research): add skill frontmatter and overview"
```

---

### Task 3: Write the classification section

**Files:**
- Modify: `skills/research/SKILL.md`

**Step 1: Append the classification section after the overview**

Add this after the Overview section:

```markdown

## Classification

Before executing any research, classify the request into a tier:

| Signal | Tier | Tools |
|--------|------|-------|
| Simple factual question, single-source answer likely | **Quick** | WebSearch (external) or Grep/Read (internal) |
| Comparison, multiple options, "what are the approaches" | **Explore** | Multi-query WebSearch + WebFetch, or multi-file Grep/Read |
| Entity discovery, landscape mapping, deep multi-source synthesis | **Deep** | Exa websets (if available) + WebSearch + codebase tools |

**How to classify:**
- If the answer fits in a paragraph and one source suffices → Quick
- If the user asks to compare, evaluate, or survey options → Explore
- If the question requires discovering entities, mapping a landscape, or synthesizing 5+ sources → Deep

State the chosen tier before proceeding. Example: "This is an **Explore**-tier question — I'll compare options from multiple sources."
```

**Step 2: Verify the section was appended correctly**

Run: `grep -c "## Classification" skills/research/SKILL.md`
Expected: `1`

**Step 3: Commit**

```bash
git add skills/research/SKILL.md
git commit -m "feat(research): add classification tier logic"
```

---

### Task 4: Write the workflow section

**Files:**
- Modify: `skills/research/SKILL.md`

**Step 1: Append the workflow section**

Add this after the Classification section:

```markdown

## Workflow

### Step 1: Understand the question

Restate the research question in one sentence. Identify:
- What is being asked
- What kind of answer is expected (fact, comparison, landscape, recommendation)
- Whether sources are internal, external, or both

If the question is ambiguous, ask one clarifying question before proceeding. Do not ask multiple questions.

### Step 2: Classify tier

Apply the classification table above. State the tier.

### Step 3: Execute research

#### Quick tier

- **External:** Run a single WebSearch query. Optionally WebFetch one result for detail.
- **Internal:** Grep or Glob for relevant code. Read key files.
- Respond conversationally with the answer and its source.

#### Explore tier

- **External:** Run 2-4 WebSearch queries from different angles. WebFetch the top 2-3 results for depth.
- **Internal:** Grep across the codebase with multiple patterns. Read files that surface across queries.
- **Hybrid:** Run both external and internal searches, then cross-reference.
- Note contradictions or disagreements between sources.
- Respond conversationally with a structured comparison and sources.

#### Deep tier

1. **Check Exa availability.** Attempt to call `list_websets`. If the tool exists and responds, Exa is available.

2. **If Exa is available:**
   - Create a webset with a descriptive name and the research query.
   - Add search criteria that match the research constraints.
   - Add enrichments for the specific data points needed (e.g., "founding year", "primary technology", "employee count").
   - Wait for the search to complete (poll with `get_search`).
   - Retrieve items with `list_webset_items`.
   - Supplement with WebSearch/WebFetch for context the webset doesn't capture.

3. **If Exa is not available:**
   - Fan out 4-6 WebSearch queries covering different facets of the question.
   - WebFetch the most relevant results (up to 5-6 pages).
   - Use the Agent tool to parallelize exploration where queries are independent.

4. **Internal component:** If the question has a codebase dimension, run Grep/Glob/Read in parallel with web research.

5. **Save a report** to `docs/research/YYYY-MM-DD-<topic>.md`.

### Step 4: Synthesize

- **Quick/Explore:** Respond in-chat. Organize findings by theme, not by source.
- **Deep:** Write a structured report (see Output Format below). Also provide a brief in-chat summary.

### Step 5: Cite sources

Every factual claim must reference its source:
- External: URL
- Internal: file path with line reference (e.g., `src/auth.ts:45`)
- Never fabricate references. If a claim cannot be sourced, state that explicitly.
```

**Step 2: Verify the workflow section exists and has all 5 steps**

Run: `grep -c "### Step" skills/research/SKILL.md`
Expected: `5`

**Step 3: Commit**

```bash
git add skills/research/SKILL.md
git commit -m "feat(research): add 5-step workflow with tier-specific execution"
```

---

### Task 5: Write the output format and error handling sections

**Files:**
- Modify: `skills/research/SKILL.md`

**Step 1: Append the output format section**

Add this after the Workflow section:

```markdown

## Output Format

For **Deep** tier research, save a report to `docs/research/YYYY-MM-DD-<topic>.md` using this structure:

```markdown
# Research: <Topic>

**Date:** YYYY-MM-DD
**Tier:** Deep
**Tools used:** [List of tools used — e.g., Exa websets, WebSearch, WebFetch, Grep]

## Question

[The research question, restated clearly]

## Methodology

[What was searched, which tools, how many queries, what criteria]

## Findings

### [Theme 1]

[Findings organized by theme, not by source]

### [Theme 2]

...

## Sources

- [Source 1 title](URL) — [one-line note on what it contributed]
- `path/to/file.ts:line` — [one-line note]

## Recommendations

[If applicable — actionable next steps based on findings]
```

For **Quick** and **Explore** tiers, respond conversationally. Include a "Sources:" section at the end with links or file paths.

## Error Handling

- **Exa unavailable:** Fall back to multi-query WebSearch + WebFetch. Do not show an error to the user. Note in methodology which tools were actually used.
- **No results found:** Report what was searched and that nothing matched. Suggest 2-3 reformulated queries the user could try.
- **Ambiguous question:** Ask exactly one clarifying question before starting research. Do not ask multiple questions at once.
- **Scope creep:** If research uncovers a much larger topic than expected, summarize what was found so far and ask the user if they want to continue deeper. Do not spiral.
- **Webset cleanup:** For deep research, create fresh websets. Do not reuse existing websets from prior research sessions to avoid stale data.
```

Note: The inner markdown code block in the output format template should use four backticks or be indented. When writing, use an indented code block or adjust the fencing to avoid breaking the outer block.

**Step 2: Verify both sections exist**

Run: `grep -c "## Output Format\|## Error Handling" skills/research/SKILL.md`
Expected: `2`

**Step 3: Commit**

```bash
git add skills/research/SKILL.md
git commit -m "feat(research): add output format template and error handling"
```

---

### Task 6: Create docs/research directory

**Files:**
- Create: `docs/research/` (directory)
- Create: `docs/research/.gitkeep`

**Step 1: Create the directory with a gitkeep**

```bash
mkdir -p docs/research
touch docs/research/.gitkeep
```

**Step 2: Commit**

```bash
git add docs/research/.gitkeep
git commit -m "chore: add docs/research directory for research reports"
```

---

### Task 7: Verify skill is discoverable

**Step 1: Check plugin.json points to skills directory**

Run: `cat .claude-plugin/plugin.json`
Expected: `"skills": "./skills/"` — this means any skill in `skills/` is auto-discovered. No registration needed.

**Step 2: Verify the complete SKILL.md is well-formed**

Read `skills/research/SKILL.md` from top to bottom. Verify:
- YAML frontmatter has `name` and `description`
- Sections exist: Overview, Classification, Workflow (5 steps), Output Format, Error Handling
- No broken markdown (unclosed code blocks, bad tables)

**Step 3: Final commit if any fixes needed**

Only if corrections were made:
```bash
git add skills/research/SKILL.md
git commit -m "fix(research): correct markdown formatting"
```

---

### Task 8: Smoke test the skill

**Step 1: Test Quick tier**

Ask the research skill a simple factual question, e.g., "What is the latest version of TypeScript?" Verify it:
- Classifies as Quick
- Uses WebSearch
- Responds conversationally with a source

**Step 2: Test Explore tier**

Ask a comparison question, e.g., "Compare Bun vs Deno for CLI tooling." Verify it:
- Classifies as Explore
- Runs multiple WebSearch queries
- Provides a structured comparison with sources

**Step 3: Test Deep tier with Exa fallback**

Ask a landscape question, e.g., "Find AI agent frameworks for building personal assistants." Verify it:
- Classifies as Deep
- Attempts Exa (or falls back gracefully)
- Produces a report or comprehensive answer
- Cites all sources

**Step 4: Test Internal research**

Ask a codebase question, e.g., "How does Tab handle agent inheritance?" Verify it:
- Uses Grep/Read instead of web tools
- References specific file paths

**Step 5: Commit any fixes from smoke testing**

```bash
git add skills/research/SKILL.md
git commit -m "fix(research): refinements from smoke testing"
```
