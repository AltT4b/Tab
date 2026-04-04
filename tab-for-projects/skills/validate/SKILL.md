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

Not every task arrives with a plan or acceptance criteria. That doesn't mean you skip validation — it means you adapt what you validate against.

- **Use the task title and description as the baseline.** If a task says "Add retry logic to the webhook handler," that's your spec. Verify the codebase reflects what the title and description promise.
- **Inspect the codebase anyway.** Read the relevant code. Check that the described functionality exists, works correctly, and doesn't introduce obvious problems. Apply the same rigor you would to a task with a full plan — you just have less to compare against.
- **Flag the missing structure as a finding.** Create a task under `group_key: "qa-findings"` noting which tasks lack a plan, acceptance criteria, or both. This is not a failure of the work — it's a process gap that should be tracked and addressed.
- **Issue a pass-with-notes verdict** if the code fulfills what the title and description describe and no other issues are found. The notes should state that validation was performed against the description only due to missing plan/acceptance criteria, and reference the qa-findings task you created. If the code has actual problems beyond the missing structure, use fail-with-reasons as you normally would.

## Assess Coverage

When reviewing a group of tasks or a full project, go beyond individual task correctness:

- **Integration gaps** — do the tasks fit together? Are there seams between them that nothing covers?
- **Missing prerequisites** — does completed work depend on something that isn't done yet and isn't tracked?
- **Untested paths** — are there user flows, error paths, or edge cases that no task covers?
- **Dependency risks** — do changes in one task invalidate assumptions in another?
- **Systemic issues** — patterns of problems across multiple tasks (e.g., no tasks handle error cases, no tasks have tests)

## Persist to MCP

Findings without actions are just complaints. Make your output useful.

**For tasks that fail:** call `mcp__tab-for-projects__update_task` to set the status back to `todo` and add your findings — be specific about what failed and what needs to change. Don't rewrite the plan; describe the delta.

**For gaps you discover:** create new tasks with `mcp__tab-for-projects__create_task`:

```
items: [{
  project_id: "<project_id>",
  title: "Add input validation for webhook URL parameter",
  description: "Explain what's missing, why it matters, and what happens if it's not addressed. Reference the tasks or work that revealed the gap.",
  effort: "<honest estimate based on what you found>",
  impact: "<how much does this gap matter>",
  category: "<most accurate category>",
  group_key: "qa-findings"
}]
```

Batch task creations into a single call. Always use `group_key: "qa-findings"` so your output is easily identifiable and reviewable.
