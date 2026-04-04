---
name: validate
description: "Validate completed work against plans and acceptance criteria — inspect code, assess tasks, find gaps, and persist findings."
argument-hint: "[project-id task-ids... or scope]"
inputs: "project-id (required), task-ids[] (optional — validate specific tasks), scope (optional — 'full' or group_key for systemic review), focus (optional — e.g. 'test coverage', 'error handling')"
mode: headless
agents:
  - qa
requires-mcp: tab-for-projects
---

# Validate

## Inspect the Actual Work

This is where you go beyond MCP records. The plan says what should have happened. The codebase says what actually happened. Your job is to compare the two.

- **Read the code.** Don't trust summaries. Open the files that were supposed to change. Verify the changes exist and do what the plan described.
- **Check the acceptance criteria.** Go through each criterion and determine whether it's met. Not "probably met" — actually met. Look at the code.
- **Run what you can.** If there are tests, check that they exist and cover the right things. If there are type checks or lint configs, verify the code would pass. If a task says "add error handling," find the error handling.
- **Look at the seams.** Where does the changed code meet unchanged code? Are the interfaces clean? Are there implicit assumptions that could break?
- **Check what wasn't said.** Plans don't always cover everything. Look for obvious things that should exist but don't — missing error handling, missing validation, missing edge cases that the plan didn't mention but the code needs.

## Assess Each Task

For every task in scope, reach a verdict:

- **pass** — the work meets its plan and acceptance criteria. No issues found.
- **pass-with-notes** — the work is fundamentally correct but has minor issues, suggestions, or observations worth recording. Nothing blocks shipping.
- **fail-with-reasons** — the work does not meet its plan or acceptance criteria, or introduces problems that need to be fixed. Each reason should be specific and traceable to something you found in the code.

## Tasks Without Plans or Acceptance Criteria

When a task lacks a plan or acceptance criteria, validate against the title and description instead. Apply the same rigor — read the code, verify the described functionality exists and works. Flag missing plan/criteria as a qa-findings task. Issue **pass-with-notes** if the code fulfills the description (noting limited validation basis), or **fail-with-reasons** if actual problems exist.

## Assess Coverage

When reviewing a group of tasks or a full project, go beyond individual task correctness:

- **Integration gaps** — do the tasks fit together? Are there seams between them that nothing covers?
- **Missing prerequisites** — does completed work depend on something that isn't done yet and isn't tracked?
- **Untested paths** — are there user flows, error paths, or edge cases that no task covers?
- **Dependency risks** — do changes in one task invalidate assumptions in another?
- **Systemic issues** — patterns of problems across multiple tasks (e.g., no tasks handle error cases, no tasks have tests)

## Persist to MCP

**For tasks that fail:** call `update_task` to set status back to `todo` with specific findings describing what failed and what needs to change. Don't rewrite the plan; describe the delta.

**For gaps you discover:** call `create_task` with descriptive title, explanation of the gap, appropriate effort/impact/category, and `group_key: "qa-findings"`. Batch creations into a single call.
