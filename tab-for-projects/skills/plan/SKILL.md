---
name: plan
description: "Design and decompose a feature into implementation tasks within an existing project. Use when the user wants to plan a feature, break down work, or invokes /plan."
argument-hint: "<feature description> for <project ID or title>"
---

# Plan — Feature Decomposition

The strategy play. Takes a feature idea within an existing project, designs it grounded in the project's existing architecture and conventions, decomposes it into implementable tasks, then health-checks everything before presenting the result. Use this when you know what you want to build next but need it broken into implementable pieces with full context.

## Trigger

**When to activate:**
- The user runs `/plan`
- The user says "break down [feature]" or "plan [feature] for [project]"

**When NOT to activate:**
- The user wants to start a brand new project (that's `/kickoff`)
- The user wants to build existing tasks (that's `/build`)
- The user wants a project status check (that's `/status`)

## Arguments

- Requires two pieces: a **feature description** and a **project reference** (ID or title).
- If the feature description is provided but the project is omitted, list projects and ask.
- If neither is provided, ask what they want to plan and for which project.
- The feature description can be brief ("add authentication") or detailed ("add OAuth2 with Google and GitHub providers, JWT session tokens, middleware for protected routes").

## Sequence

1. **Load project context.** Gather everything needed to design with full awareness:
   - `get_project` — goal, requirements, design
   - `list_documents` — architecture, conventions, prior design docs. Read any that are directly relevant to the feature being planned (especially architecture and conventions docs) via `get_document`
   - `list_tasks` — current task landscape: what already exists, what's in progress, what's done

2. **Write a design document.** Create via `create_document`:
   - **Title:** Type-prefixed (e.g., "Design: OAuth2 Authentication")
   - **Summary:** ≤500 characters capturing what this design covers
   - **Content:** The full design covering:
     - **Approach** — how the feature fits into the existing architecture, which patterns and conventions it follows, where it lives in the codebase
     - **Trade-offs** — alternatives considered and why this approach wins
     - **Key decisions** — choices that shape implementation (data model, API surface, integration points, error handling strategy)
   - Attach to the project via `update_project` (attach_documents)

   Ground everything in what the project already has. Reference existing architecture docs and conventions by name. The design should feel like a natural extension of the project, not a greenfield proposal.

3. **Decompose into tasks.** Create each task via `create_task`:
   - **Description** — answers "what and why": what the task produces and why it matters for the feature
   - **Plan** — answers "where and how": which files, which patterns, which existing code to follow. Reference the design doc so the developer has full context
   - **Acceptance criteria** — testable conditions. A developer should be able to read these and know exactly when the task is done
   - **Effort** — calibrated on the scale: trivial (one file touch) → low → medium → high (cross-cutting) → extreme
   - **Impact** — how much of the feature this task unlocks
   - **Dependencies** — real ordering constraints only: task B literally cannot start until task A is done. No soft preferences, no circular chains
   - **Group key** — logical grouping for related tasks (e.g., "auth-backend", "auth-frontend")

   Each task should be implementable by a developer with no additional context beyond the task itself and KB documents. If a task requires reading another task to make sense, it needs a better description.

   KB discipline: search existing documents before creating. Target 10 documents per project, hard limit 13.

4. **Health-check the tasks.** Review every task just created and fix problems inline via `update_task`:
   - **Descriptions** — clear enough to start work without asking questions?
   - **Acceptance criteria** — actually testable, not vague aspirations?
   - **Dependencies** — acyclic? Use `get_dependency_graph` to verify. No circular chains
   - **Effort calibration** — consistent across tasks? A "low" in one group shouldn't be a "medium" in another
   - **Completeness** — does the full set of tasks cover the entire feature? Any gaps?

   Fix anything found. Don't flag it for later — fix it now.

## Output

Present the plan:

**Design summary** — Approach, key decisions, trade-offs. Reference the design doc by title for the user to review in full.

**Task breakdown** — Table of tasks created, with titles, effort, impact, and group. Ordered by dependency (what can start first).

**Dependency graph** — Which tasks block which. Keep it visual if the chain is simple, or describe it if complex.

**Scope estimate** — Total effort across all tasks. Ballpark of how much work this represents.

**Open items** — Design questions that couldn't be resolved, or anything needing human decision.

## Edge Cases

- **Feature overlaps with existing tasks:** Note overlaps during decomposition. Avoid creating duplicates. If significant overlap exists, surface it — the user may want to revise existing tasks rather than create new ones.
- **Project has no goal or requirements:** Without clear project-level context, task decomposition may be vague. Suggest the user flesh out the project first or use `/kickoff` to restructure.
- **Decomposition produces too many tasks:** If decomposition yields 15+ tasks for a single feature, that may signal the feature is actually multiple features. Surface this observation and suggest splitting.
