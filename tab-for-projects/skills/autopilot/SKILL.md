---
name: autopilot
description: "Autonomous project coordination — assess the backlog, plan unplanned tasks, implement ready work, validate results, and document findings without checking in at each step."
argument-hint: "[project-name]"
---

# Autopilot

The user is opting out of the conversation loop. They want the system to assess the project, identify what needs doing, and do it — without asking for permission at each step.

## Protocol

1. **Resolve the project.** If the user passed an argument, match it against `list_projects`. Otherwise follow standard resolution (check `list_projects`, check `CLAUDE.md`, ask if ambiguous).

2. **Load project context.** Call `get_project` for the goal, requirements, and design. Call `list_documents` for all knowledgebase document IDs.

3. **Phase 1: Assessment.** Spawn the coordinator (`subagent_type: "tab-for-projects:coordinator"`) with scope `"full"`, mode `"coordinate"`, project context, and all knowledgebase document IDs. Run in the background.

   The coordinator assesses backlog health, does direct MCP work (fix statuses, archive duplicates, create gap tasks), and returns **dispatch instructions**: which task IDs need planning, QA, documentation, or implementation.

   Tell the user: "Running autopilot — coordinator is assessing the project."

4. **Phase 2: Dispatch specialists.** Read the coordinator's dispatch instructions and spawn agents in parallel for whatever work exists:
   - **Planner** — tasks needing plans or decomposition
   - **QA** — completed tasks needing validation
   - **Documenter** — completed work needing knowledge capture

   Only spawn agents that have work. All run in the background. Update the user on what was dispatched.

5. **Phase 3: Implementation.** After Phase 2 completes, identify tasks ready for implementation — from the coordinator's `implement` dispatch and from newly-planned tasks (status `todo` with `plan` and `acceptance_criteria`). If none, skip to step 7.

   Spawn implementer agents (`subagent_type: "tab-for-projects:implementer"`) in dependency-ordered waves with worktree isolation (`isolation: "worktree"`). Cap at 3-5 concurrent agents per wave. Merge branches between waves. Update the user after each wave.

6. **Phase 4: Post-implementation QA.** Spawn QA on tasks that implementers completed successfully. No retry loops — failures go to the summary.

7. **Results summary.** Present the full picture:
   - Coordinator: assessment, direct actions taken (status fixes, new tasks, archives)
   - Planner: plans produced, tasks decomposed
   - QA (Phase 2): verdicts on pre-existing completed work
   - Documenter: documents created or updated
   - Implementation: tasks completed, failed, or skipped (with reasons)
   - QA (Phase 4): verdicts on newly implemented work
   - Items needing the user's judgment
