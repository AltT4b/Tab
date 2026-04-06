---
name: plan
description: "Quick-reference card for task decomposition — enums, principles, and dependency wiring."
argument-hint: "<scope description>"
---

# Plan

Quick-reference for decomposing work into tasks. Load via `/plan` when the tech lead needs to create a task graph.

For the full MCP data model and tool signatures, load `/user-manual mcp`.

## Task Enums

| Field | Values |
|-------|--------|
| **status** | `todo`, `in_progress`, `done`, `archived` |
| **effort** | `trivial`, `low`, `medium`, `high`, `extreme` |
| **impact** | `trivial`, `low`, `medium`, `high`, `extreme` |
| **category** | `feature`, `bugfix`, `refactor`, `test`, `perf`, `infra`, `docs`, `security`, `design`, `chore` |

## Decomposition Principles

- **One agent session per task.** If it requires context-switching between unrelated areas, split it. If it's a one-line change, group it with related work.
- **Each task targets one role.** `feature`/`bugfix`/`refactor`/`chore`/`test`/`infra` route to developers. `design`/`docs` route to the tech lead.
- **Effort reflects scope, not difficulty.** `trivial` = minutes. `low` = single file. `medium` = multiple files. `high` = cross-cutting. `extreme` = system-level.
- **Group related tasks.** Use `group_key` (max 32 chars) to cluster tasks in the same logical unit: `auth`, `csv-export`, `plugin-api`.
- **Tasks are self-contained.** Every task must make sense to someone who reads only that task plus the documents it references.

## Dependency Wiring

Create all tasks first, then wire dependencies in a batch `update_task` call.

```
update_task({ items: [{
  id: "<downstream-task-id>",
  add_dependencies: [{ task_id: "<upstream-task-id>", type: "blocks" }]
}]})
```

- `blocks` — upstream must be `done` before downstream appears in `get_ready_tasks`.
- `relates_to` — shared context, no ordering constraint.

**Ordering rules:** design blocks implementation. Requirements clarification blocks dependent work. Infrastructure blocks tasks needing it to verify. Within a feature: data model, then service, then API, then UI.

## Task Fields

For each task, write three fields that make it actionable:

- **`description`** — What and why, where in the codebase, relevant KB document names, constraints.
- **`plan`** — Strategy: what to look at first, which patterns to follow, key decisions, edge cases.
- **`acceptance_criteria`** — Testable, specific, scoped to this task alone.
