---
name: autopilot
description: "Autonomous project coordination — assess the backlog, plan unplanned tasks, validate completed work, and document findings without checking in at each step."
argument-hint: "[project-name]"
---

# Autopilot

The user is opting out of the conversation loop. They want the system to assess the project, identify what needs doing, and do it — without asking for permission at each step.

## Protocol

1. **Resolve the project.** If the user passed an argument, match it against `list_projects`. Otherwise follow standard resolution (check `list_projects`, check `CLAUDE.md`, ask if ambiguous).

2. **Load project context.** Call `get_project` for the goal, requirements, and design.

3. **Gather knowledgebase context.** Call `list_documents` for the project. Collect all document IDs.

4. **Phase 1: Assessment.** Spawn the coordinator in coordinate mode (`subagent_type: "tab-for-projects:coordinator"`) with:
   - Project ID, goal, requirements, design
   - Scope: `"full"`
   - Mode: `"coordinate"`
   - All knowledgebase document IDs

   Run in the background. The coordinator will:
   - Assess backlog health and alignment with project goals
   - Do direct MCP work: fix task statuses, archive duplicates, create tasks for gaps it identifies
   - Return a structured assessment with **dispatch instructions**: which task IDs need planning, which need QA validation, which need documentation, and any focus areas for each

5. **Tell the user what's running.** Brief status: "Running autopilot — coordinator is assessing the project. I'll dispatch the team once it reports back."

6. **Phase 2: Dispatch.** When the coordinator completes, read its dispatch instructions and spawn agents in parallel:
   - **Planner** (`subagent_type: "tab-for-projects:planner"`) — for tasks the coordinator flagged as needing plans or decomposition. Pass the specific task IDs and any context the coordinator provided about what needs planning.
   - **QA** (`subagent_type: "tab-for-projects:qa"`) — for completed tasks the coordinator flagged as needing validation. Pass task IDs and any focus areas.
   - **Documenter** (`subagent_type: "tab-for-projects:documenter"`) — for completed work the coordinator flagged as needing knowledge capture. Pass task IDs and existing document IDs to avoid duplication.

   Only spawn agents that have work to do. If the coordinator found nothing for QA, don't spawn QA. All spawned agents run in the background, in parallel.

7. **Update the user.** Brief status on what was dispatched: "Coordinator found 8 tasks needing plans, 3 needing QA, and 2 worth documenting. Planner, QA, and documenter are running now."

8. **Collect and present results.** As agents complete, collect their results. When all are done, present the full summary:
   - What the coordinator assessed and what direct actions it took (status fixes, new tasks, archives)
   - What the planner produced (plans, acceptance criteria, new tasks from decomposition)
   - What QA found (pass/fail verdicts, qa-findings tasks created)
   - What the documenter captured (documents created or updated)
   - What the coordinator chose NOT to act on and why
   - Items that need the user's judgment

## What Makes This a Skill

Autopilot is a **permission structure**. Without it, the manager asks before it acts — that's its nature as a thinking partner. Autopilot explicitly says: "I trust the system to make good calls. Go."

The two-phase design makes the manager a team lead, not a delegator. Phase 1 sends the coordinator as an analyst — it reads the full project state, does what it can directly (status fixes, gap tasks, duplicate cleanup), and returns structured dispatch instructions for specialist work. Phase 2 has the manager spawn planner, QA, and documenter in parallel with the specific scoped work from the coordinator's findings. The coordinator doesn't need to hold the spawn button; the manager does that based on precise instructions about what needs doing and why.

The user should be able to type `/autopilot`, walk away, and come back to a project that's been triaged, planned, validated, and documented — with a clear summary of everything that happened.
