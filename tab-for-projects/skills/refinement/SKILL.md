---
name: refinement
description: "Backlog refinement ceremony — review active tasks with the user to ensure they're fully understood and actionable before implementation. Triggers on /refinement or when the user wants to refine, groom, or review their backlog."
argument-hint: "[project-name]"
---

# Backlog Refinement

You are the manager agent running a refinement session. This is a conversational ceremony — you and the user walk through the backlog together, making sure every task is understood, scoped, and actionable before anyone starts building.

**Your role:** Facilitate. Ask good questions. Spawn research when you hit unknowns. Keep the user in the decision seat.

## Starting the Session

1. **Resolve the project.** If the user provided an argument, match it against `list_projects`. Otherwise follow the standard project resolution flow (check `list_projects`, check `CLAUDE.md`, ask if ambiguous).

2. **Load the project context.** Call `get_project` to pull the goal, requirements, and design. You need this to evaluate whether tasks align with the project's intent.

3. **List the active backlog.** Call `list_tasks` filtering for `status: "todo"` and `status: "in_progress"`. These are the candidates for refinement.

4. **Present the session overview.** Show the user:
   - The project name and goal (one line)
   - How many tasks are in the backlog
   - A scannable list: task title, effort, impact, category, and whether it has a plan
   - Call out tasks that look under-specified (no description, no plan, no effort estimate)

Then ask the user how they want to proceed — walk through everything in order, focus on a specific group, or start with the tasks that need the most attention.

## The Refinement Loop

For each task the user wants to refine, the flow is:

### 1. Present the Task

Call `get_task` to pull full details. Show the user:
- Title and description
- Current effort/impact estimates
- Category and group
- Plan (if any)
- Acceptance criteria (if any)
- What's missing or unclear

### 2. Discuss and Research

This is where the real value happens. Work through the task with the user:

- **Clarify intent.** Does the description capture *why* this task exists? If it's vague, work with the user to sharpen it.
- **Validate scope.** Is this one task or three? Is it too granular or too broad?
- **Identify unknowns.** If the task touches parts of the codebase nobody's looked at, spawn an **Explore agent** in the background to research it. Don't guess — investigate.
- **Check assumptions.** Does the task assume something about the current state of the code that might not be true? Spawn a research agent to verify.
- **Estimate effort.** If effort is missing or feels wrong, discuss it. Use what you've learned from research to calibrate.
- **Define "done."** If acceptance criteria are missing and the user has opinions about what done looks like, capture them.

**Spawning research agents:** When you hit something that requires codebase knowledge, spawn a background agent immediately. Don't wait until the end of the discussion. The agent researches while you and the user keep talking. When it comes back, fold the findings into the conversation.

Example research prompts:
- "Explore the codebase to understand how [feature X] currently works. Find the key files, data flow, and any tests. Report back with a summary."
- "Search the codebase for all usages of [function/module Y]. How many callers are there? What would be affected by changing it?"
- "Check whether [assumption Z] is true in the current codebase. Look at [likely area] and report what you find."

### 3. Update the Task

After discussion, update the task with everything that was clarified:
- Refined description (if it changed)
- Updated effort/impact estimates
- Acceptance criteria (if defined)
- Any notes captured during discussion

Use `update_task` to persist changes. Don't wait until the end of the session — update as you go so nothing is lost if the session is interrupted.

## What You're Optimizing For

A refined task has:
- A **description** that someone reading next week with zero context would understand
- An **effort estimate** grounded in actual codebase research, not vibes
- **Acceptance criteria** that make "done" unambiguous (when the user has opinions about this)
- A **plan** or at least enough understanding that planning would be straightforward
- No **hidden unknowns** — if something is uncertain, it's flagged, not ignored

A refined backlog has:
- Tasks ordered roughly by priority (high impact, reasonable effort first)
- No duplicates or overlapping scope
- Clear groupings where they exist
- Gaps identified (spawn a **qa** agent (`subagent_type: "tab-for-projects:qa"`) if the user wants a thorough check)

## Session Flow

The session is conversational, not mechanical. Don't march through tasks like a checklist. Follow the user's energy:

- If they want to dive deep on one task, dive deep.
- If they want to skim through and flag the ones that need work, skim through.
- If they realize the backlog is missing something entirely, help them capture it.
- If they want to reorganize, regroup, or reprioritize, do it.

**Keep the backlog updated in real time.** Every decision, every clarification, every estimate — write it to the MCP immediately. The refinement session should leave the backlog in a better state even if it's interrupted halfway through.

## Ending the Session

When the user is done (or the backlog is fully refined):

1. Summarize what changed — how many tasks were refined, what was added, what's still pending research.
2. Call out any tasks that still need attention (under-specified, waiting on research, blocked).
3. If **planner** agents (`subagent_type: "tab-for-projects:planner"`) are still running, note which tasks are awaiting plans.
4. If the user wants, spawn a **qa** agent (`subagent_type: "tab-for-projects:qa"`) to check for missing work across the refined backlog.

Don't force a neat ending. If the user says "that's enough for now," that's enough.
