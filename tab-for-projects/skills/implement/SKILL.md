---
name: implement
description: "Execute task plans faithfully — load context, verify assumptions, implement changes, self-validate, and update MCP."
argument-hint: "[project-id task-ids...]"
inputs: "project-id (required), task-ids[] (required — each must have a plan field), knowledgebase-doc-ids[] (optional)"
mode: headless
agents:
  - implementer
requires-mcp: tab-for-projects
---

# Implement

## Research the Codebase

Before implementing, understand the area you're changing:

- **Read the files referenced in the plan.** The plan should point to specific paths. Open them. Understand the current state.
- **Understand the patterns in adjacent code.** How are similar things done elsewhere? What naming conventions, structural patterns, and integration approaches are used?
- **Verify the plan's assumptions.** Code may have changed since the plan was written. If the plan references files, functions, or structures that no longer exist or have changed significantly, stop and flag it rather than guessing.
- **Identify what touches the area.** Callers, consumers, tests, configs — anything that would be affected by your changes.

Spend the time here. An implementation built on stale assumptions creates problems that are harder to fix than the original task.

## Implement

This is the core work. Follow the plan.

- **Follow the plan's sequence and approach.** The plan defines the strategy, the files to touch, and the order of changes. It is the contract between the planner and you.
- **Follow established codebase conventions.** When the plan and codebase conventions align, good. When they conflict, follow the plan but note the discrepancy in your return.
- **Make targeted changes.** Don't rewrite entire files when targeted edits suffice. Don't reorganize code that the plan didn't ask you to reorganize.
- **Resolve ambiguity from the acceptance criteria.** If the plan is ambiguous on a specific point, check the acceptance criteria for guidance. If still ambiguous, make the simplest choice that satisfies the criteria and note the decision in your return.
- **Do not expand scope.** Adjacent improvements, refactors, and "while I'm here" changes are out of bounds. If you notice something worth doing, mention it in your return — don't do it.

When implementing multiple tasks, check for dependencies between them (one task's output is another's input) and sequence accordingly. If dependencies aren't clear, implement in the order received. When multiple tasks touch the same file, handle them sequentially.

## Self-Validate

Before reporting completion, verify against the acceptance criteria:

1. Go through each acceptance criterion for the task. For each one, verify concretely that your implementation satisfies it. Not "probably meets it" — actually check.
2. If tests exist for the changed code, run them. If the plan specified writing tests, verify you wrote them and they pass.
3. If any criterion is not met, either fix the implementation or flag it as incomplete with a specific reason.

This is a smoke check, not full QA. The QA agent does deep validation. You confirm the obvious criteria are met and flag anything you're uncertain about.

## Update MCP

Keep the task records current:

- At the start of implementation, call `mcp__tab-for-projects__update_task` to set `status: "in_progress"` if not already set.
- When implementation is complete, call `mcp__tab-for-projects__update_task` to set `status: "done"` and fill the `implementation` field.

The `implementation` field should describe what was actually done: files changed, approach taken, any deviations from the plan and why. Write for the QA agent and documenter who will read this next — they need to know what happened, not just that something happened.
