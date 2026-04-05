---
name: prompt-review
description: "Review MCP content for prompt quality — checks task descriptions, plans, acceptance criteria, and KB documents for clarity, actionability, and agent-consumability."
argument-hint: "<project-name> [--tasks | --docs | --routing | <task-id> | <doc-id>]"
inputs:
  project: required
  scope: optional (--tasks, --docs, --routing, or specific ID)
mode: conversational
agents: manager
requires-mcp: tab-for-projects
---

# Prompt Review

A structured review of MCP content quality — task descriptions, plans, acceptance criteria, and KB documents — evaluated as prompts that agents consume. The manager runs the review; the user decides what to fix.

## Trigger Rules

This skill activates **only** on explicit `/prompt-review` invocation. Do NOT trigger on casual mentions of "review," "quality," "prompt," or "improve tasks." The skill modifies project content — implicit activation would be surprising and destructive.

## Protocol

### Phase 1: Setup

1. **Resolve the project.** If the user provided an argument, match it against `list_projects`. Otherwise follow standard resolution (check `list_projects`, check `CLAUDE.md`, ask if ambiguous).

2. **Load project context.** Call `get_project` to pull the goal, requirements, and design.

3. **Fetch the Prompt Quality Conventions document.** Call `list_documents` and search for the document by title containing "Prompt Quality Conventions" or tagged `conventions`. Do NOT hardcode the document ID — it varies across projects. If no conventions document is found, proceed with the six built-in rules (Phase 2) and note the absence to the user.

4. **Load review targets based on scope.**

   | Argument | What loads |
   |----------|-----------|
   | (none) | All todo/in_progress tasks + all documents + routing analysis |
   | `--tasks` | All todo/in_progress tasks only |
   | `--docs` | All project documents only |
   | `--routing` | Tasks and documents for routing analysis only |
   | `<task-id>` | Single task by ID |
   | `<doc-id>` | Single document by ID |

   For large backlogs (>15 tasks), prioritize high and extreme effort tasks first. Present the overview and offer to continue with medium/low effort tasks afterward.

5. **Present the session overview.** Show the user:
   - Project name and goal (one line)
   - What will be reviewed: task count, document count, scope
   - Whether the Prompt Quality Conventions document was found

### Phase 2: Task Review

For each task in scope, call `get_task` for full details. Evaluate against three layers:

**Layer 1: Convention Checklist.** Apply each rule as a mechanical yes/no check:

| # | Rule | What it catches | Test |
|---|------|----------------|------|
| 1 | Unenforceable constraints | Plans that restate sandbox or runtime constraints the agent cannot violate anyway | If the agent ignores this instruction, does something different actually happen? If not, the constraint is noise. |
| 2 | Ambiguous either/or | Plans with unresolved alternatives that force the implementer to guess | Search for "either...or", "you can...or you can", "optionally", "consider" without resolution. Every alternative must be resolved to a single approach. |
| 3 | Enum/tag accuracy | Plans referencing wrong status values, tag names, or categories | Verify every enum value against the MCP schema. Common errors: invented statuses, nonexistent tags, wrong category names. |
| 4 | Scope-dependent accuracy | Descriptions that misrepresent what the implementing agent will encounter | Cross-check the description against what the agent actually has access to — its tools, the codebase state, the MCP data available. |
| 5 | Phantom references | Plans referencing files, APIs, tools, or agents that don't exist | Every named reference (file path, function name, tool name, agent name) should be verifiable. Flag suspicious references — the skill flags them; a future agent verifies them against the codebase. |
| 6 | Blanket bans vs. precise guidance | Prohibitions that catch legitimate uses | Check if any "never" or "do not" instruction has legitimate exceptions. Replace blanket bans with precise guidance that names the specific cases to avoid. |

**Layer 2: Clarity Assessment.** Evaluate with judgment:

- **Description clarity:** Would a developer agent with no prior context understand what to build and why?
- **Plan concreteness:** Does the plan name specific files, functions, and patterns? Or is it vague ("update the API," "add tests")?
- **Acceptance criteria testability:** Could QA verify each criterion mechanically without judgment calls?
- **Missing fields:** Are description, plan, and acceptance_criteria all populated? A task with effort "high" but no plan is a red flag.
- **Effort alignment:** Does the effort estimate match the apparent scope of the plan?

**Layer 3: Severity Classification.** Group each finding into one of three severities:

| Severity | Meaning | Example |
|----------|---------|---------|
| **Blocking** | Will cause the implementing agent to fail or produce wrong output | Phantom file reference in plan; unresolved either/or in a critical step |
| **Improvement** | Won't cause failure but reduces implementation quality | Vague description that requires inference; missing acceptance criteria on a medium-effort task |
| **Clean** | No issues found | Task is well-specified and ready for implementation |

### Phase 3: Document Review

For each KB document in scope, call `get_document` for full content. Evaluate:

- **Scanability:** Can an agent find what it needs from headings alone? Are headings descriptive (good: "Error Response Shape") or generic (bad: "Notes")?
- **Instruction concreteness:** Are practices stated as concrete instructions with examples, not abstract principles?
- **Example quality:** Do examples show input/output pairs, not just describe behavior in prose?
- **Structure:** Is structured data in tables rather than buried in paragraphs?
- **Convention checks:** Apply Rules 3 (enum accuracy), 5 (phantom references), and 6 (blanket bans) to document content.

Group document findings by the same severity scale: blocking, improvement, clean.

### Phase 4: Document Routing

Match tasks to documents — what domain knowledge does each task need, and is it available?

For each task in scope:

1. **Identify knowledge needs.** What conventions, architecture decisions, API specs, or reference material would the implementing agent need?
2. **Check available documents.** Which project documents cover those topics?
3. **Classify coverage:**

   | Status | Meaning |
   |--------|---------|
   | **Attached and relevant** | Document is attached to the project and covers the task's knowledge needs |
   | **Available but unattached** | Document exists in the project but isn't referenced in the task's plan |
   | **Missing** | No document covers this topic — gap for the knowledge-writer |

4. **Report gaps.** For missing documents, describe what the document should cover and which tasks it would serve. Do NOT create documents — report the gap for the knowledge-writer to fill.

### Phase 5: Apply Fixes

Present the full findings report (see Output Format below), then offer three paths:

| Option | Behavior |
|--------|----------|
| **Fix all** | Rewrite all flagged content via `update_task` and `update_document` calls. Show a summary of changes after. |
| **Walk through** | Present each finding one at a time. The user approves, modifies, or skips each fix before it's applied. |
| **Report only** | No modifications. The user takes the report and acts on it manually. |

**Content boundaries when applying fixes:**

- Only modify `description`, `plan`, and `acceptance_criteria` fields on tasks.
- Only modify `content` and `title` fields on documents.
- NEVER modify `status`, `effort`, `impact`, or `category` on tasks. These are the user's judgment calls, not prompt quality issues.
- Preserve the original author's intent. Changes are structural and clarity improvements — not semantic rewrites. If a plan is fundamentally wrong (not just poorly expressed), flag it to the user rather than rewriting it.
- Persist each fix immediately via MCP. If the session is interrupted, every applied fix is already saved.

## Output Format

Present the findings report in this structure:

```
## Prompt Review: [Project Name]

### Task Findings

#### Blocking
| Task | Title | Rule | Finding | Suggested Fix |
|------|-------|------|---------|---------------|
| [ID] | ... | Rule 5: phantom reference | Plan references `src/api/handler.ts` — verify this file exists | Remove or correct the file path |

#### Improvement
| Task | Title | Finding | Suggested Fix |
|------|-------|---------|---------------|
| [ID] | ... | No acceptance criteria on high-effort task | Add testable criteria derived from the plan |

#### Clean
[N] tasks passed all checks.

### Document Findings

#### Blocking
| Doc | Title | Finding | Suggested Fix |
|-----|-------|---------|---------------|
| [ID] | ... | Generic headings — agent cannot scan for relevant section | Rewrite headings to name the specific topic covered |

#### Improvement
| Doc | Title | Finding | Suggested Fix |
|-----|-------|---------|---------------|
| [ID] | ... | Examples describe behavior in prose instead of showing input/output | Add concrete input/output examples |

#### Clean
[N] documents passed all checks.

### Document Routing

| Task | Title | Needs | Available Doc | Action |
|------|-------|-------|---------------|--------|
| [ID] | ... | Deployment conventions | [doc ID]: Deploy Guide | Already covered |
| [ID] | ... | API error handling patterns | (none) | Gap — knowledge-writer should create |
| [ID] | ... | Database migration patterns | [doc ID]: DB Conventions | Reference in task plan |

### Summary
- Tasks reviewed: [N]
- Blocking findings: [N]
- Improvements suggested: [N]
- Clean tasks: [N]
- Documents reviewed: [N]
- Routing gaps identified: [N]
```

Adapt the table columns to fit the actual findings — don't force empty columns. If a severity category has zero findings, omit it rather than showing an empty table.

## What Makes This a Skill

Prompt review is a **quality audit** that the user explicitly requests. It reads MCP content as an agent would, finds where that content would cause confusion or failure, and offers to fix it. The user sees the reasoning, builds trust in the review quality, and controls what gets changed.

This is the lightweight experiment before a full prompt-engineer agent. Conversational mode means the user observes accuracy and judgment firsthand. If the skill consistently produces meaningful improvements across 3+ projects and users default to "fix all," that's the signal to promote to a headless agent with autopilot integration.

The skill complements `/refinement` — refinement negotiates scope and priority with the user; prompt review audits how that scope is expressed for agent consumption. Run refinement to decide what to build, then prompt review to make sure it's expressed well enough for agents to build it right.
