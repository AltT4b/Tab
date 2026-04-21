---
name: rewrite
description: Plan-focused targeted rewrite. Takes a freeform description like "rewrite the repository layer" or "redo the component system", runs the KB for relevant prior decisions, dispatches `bug-hunter` to survey the current state, uses exa for best-practice research, iterates with the user to consolidate the shape, flags multi-target rewrites, and emits backlog tasks via `project-planner` — a mix of implementation tickets and design tickets depending on what's decided. Does not write code, does not write KB docs, does not auto-execute. Triggers on `/rewrite` and phrases like "let's rewrite X", "redo the Y layer", "replace the Z system".
argument-hint: "<freeform description of what to rewrite>"
---

A planning skill for "rewrite the <chunk>" work. The user brings a description of what they want to replace; the skill pulls relevant KB context, surveys the current state via the hunter, researches best-practices for the shape being built, iterates with the user to lock the approach, and produces backlog tasks — implementation tickets where the shape is clear, design tickets where architecture still needs decision. It never codes, never writes docs, and never auto-executes. The user runs `/work` and `/design` on their own timing.

## Trigger

**When to activate:**
- User invokes `/rewrite <description>`.
- User says "let's rewrite the <layer>", "redo the <system>", "replace the <component>", "I want to rethink the <module>", "rewrite how X works".
- A chunk of the application has accumulated enough problems that replacement is on the table and the user wants a plan.

**When NOT to activate:**
- User wants to fix a specific bug — use `/debug`.
- User wants to capture a single task — use `/capture`.
- User is deciding project-level shape or writing a KB doc — use `/design`.
- User wants to execute an existing plan — use `/work`.
- The "rewrite" is really a single-file refactor — just `/capture` it; a whole skill is overkill.

## Requires

- **Subagent:** `tab-for-projects:bug-hunter` — surveys the current state of the target chunk.
- **Subagent:** `tab-for-projects:project-planner` — turns the consolidated plan into backlog tasks.
- **MCP:** `tab-for-projects` — for `list_documents`, `search_documents`, `get_document`, `get_project_context`.
- **MCP:** `exa` — web research for best practices, common patterns, and anti-patterns relevant to the shape being built. Always available per project constraints.
- **Tools:** `Read`, `Grep`, `Glob` — for on-the-fly context lookups during the interview. Deeper codebase reading is the hunter's job.

## Behavior

Seven phases: **Scope**, **KB**, **Survey**, **Research**, **Consolidate**, **Multi-target check**, **Emit**. The first five are conversational; the last two are the output gate.

### 1. Scope — interview the user

Open with a tight set of questions about the rewrite's boundary and goals. Not a script — the questions that actually apply to this target. Common shape:

- **What's wrong with the current version?** The failure modes drive the requirements. Without them, the rewrite replicates the same mistakes.
- **What's the boundary?** Which files, modules, surfaces? Where does the rewrite stop?
- **What stays the same?** Public API, behavior, migration path — what's non-negotiable.
- **What's the target shape?** The user's current best guess — even if fuzzy.
- **What's the urgency?** Drives how aggressively to split into shippable chunks vs. one big swing.

If the description already answers most of these, don't re-ask. Acknowledge what's clear and drill into what isn't.

Stop if the target is under a single file or the answers reveal a simple refactor — point the user at `/capture` instead.

### 2. KB — pull relevant prior decisions

Search the KB for anything that shapes the rewrite:

- Conventions that constrain the new version (`list_documents({ project_id, folder: "conventions" })`).
- Prior decisions on the same or adjacent surface (`list_documents({ project_id, folder: "decisions" })`, `search_documents({ query: <target> })`).
- Architecture docs that name the existing contract.

Read the substance of the relevant ones. These become context for the hunter and the planner — every tangible constraint should be visible before the plan is shaped.

If the KB has nothing relevant, say so. A greenfield rewrite is different from one constrained by prior decisions.

### 3. Survey — dispatch the `bug-hunter`

Dispatch the hunter with a tailored concern:

```
Survey the current <target>. Identify:
  - Structure (entry points, key files, module boundaries)
  - Failure modes aligned with <user's stated problems>
  - Coupling with surrounding code
  - Tests (coverage, shape, gaps)
  - Any adjacent issues that would otherwise hide inside the rewrite
```

Pass KB context that matters as scope / hypothesis input. When the hunter returns, render the report. This is the anchor for everything that follows — the plan is built on top of observed reality, not assumed reality.

Single dispatch, not a loop. If the user needs another angle after seeing the report, that's a follow-up hunter dispatch with a narrower concern — not a new survey.

### 4. Research — exa for best practices

For the target shape the user named (a repository layer, a component system, an auth flow, a queue), use `exa` to pull 2–4 relevant sources on common patterns and anti-patterns. Summarize the substance, not the links. The goal: inform the consolidated shape with approaches the user may not have considered.

Skip this step when the rewrite is tightly project-specific (e.g., "rewrite our custom business-logic X") and external patterns don't apply. Say so and move on.

### 5. Consolidate — iterate the shape with the user

This is the conversation's core. With the KB context, the hunter's report, and the research in hand, work with the user to lock:

- **The target shape.** What the new version looks like, at the level of "these components, these responsibilities, these boundaries." Not line-by-line.
- **The migration path.** Big bang or incremental. If incremental, which seams to cut first.
- **What's decided vs. what's a fork.** Every decision that gets made here becomes an implementation ticket; every unresolved fork becomes a design ticket.
- **What stays out of scope.** The rewrite should have a ceiling — what's *not* being replaced this round.

Push back when the user hand-waves a fork. "We'll figure that out later" is a design ticket, not an answer.

Iterate until the user signals the shape is set — "this is it," "yes let's go," "file it."

### 6. Multi-target check

Before emitting, re-read the consolidated shape. If it resolved to more than one distinct rewrite — say, "rewrite the repository layer" expanded to "also the data-access conventions and the caching strategy" — surface that:

```
This rewrite has resolved to <N> distinct targets:
  1. <target A> — <one-line summary>
  2. <target B> — <one-line summary>
  3. <target C> — <one-line summary>

Options:
  split    — file each as a separate /rewrite invocation; emit tasks per target
  narrow   — keep only <primary target> for this run; file the others as follow-up /rewrite tasks
  proceed  — emit tasks for all N as one set; accept the broader scope
```

The user picks. `split` is the gentlest; `proceed` is the biggest swing. `narrow` is the usual middle path.

### 7. Emit — dispatch `project-planner`

Hand the consolidated plan to the planner as a freeform prompt (shape 3), broken into one dispatch per target (if the user split) or a single dispatch with a structured body (if the user proceeded).

The dispatch body includes:

- The rewrite's goals and non-negotiables.
- The target shape the user locked.
- The migration path.
- The hunter's report (inlined substance — not just a reference).
- The KB conventions and decisions that apply (inlined substance).
- The research findings that matter.
- The forks the user explicitly punted — planner will file these as design tickets.

The planner emits:

- **Implementation tickets** for the decided pieces — code-ready, at the readiness bar, with concrete acceptance signals.
- **Design tickets** for the forks — each describing the decision that needs making, so `/design` can pick them up.
- **Dependency edges** between the tickets when the migration path implies ordering.

### 8. Report

Print the emitted tasks:

```
/rewrite complete — <target>
Emitted: <N> implementation tickets · <M> design tickets

Implementation:
  01KX… "<title>" — <category>, <effort>, dep on: 01KY…
  01KY… "<title>" — <category>, <effort>
  ...

Design (resolve first via /design):
  01KZ… "Decide: <question>"
  ...

Next: /design the design tickets, then /work for the implementation set.
```

The skill closes. It does not invoke `/work` or `/design`.

## Output

- Implementation and design tickets on the backlog, authored via `project-planner`.
- No code changes. No KB documents. No git commits.
- A report naming what was emitted and the suggested order.

## Principles

- **The plan is the deliverable.** `/rewrite` doesn't rewrite code — it produces the plan that lets `/work` do the rewrite one task at a time.
- **Decide what's decided; punt what isn't.** Implementation tickets for the decided pieces; design tickets for the forks. No task leaves the skill with a hidden assumption.
- **Survey before planning.** The hunter's report anchors the plan in what the code actually is, not what the user remembers it is.
- **Match what exists.** KB conventions and prior decisions come first. A rewrite that re-litigates settled questions burns time.
- **Flag scope creep early.** A rewrite that resolved to three things should be three plans — or an explicit choice to handle them as one.
- **The user drives the timing.** The skill emits tasks and stops. `/work` runs when the user says so.

## Constraints

- **No source code.** Ever. The skill produces tasks, not edits.
- **No KB writes.** Design decisions that emerge land as design tickets; `/design` writes the docs.
- **No auto-invocation of `/work` or `/design`.** The user picks their timing.
- **No bypassing the planner.** Tasks land via `project-planner`, which enforces the readiness bar on implementation tickets.
- **No infinite loops.** Hunter dispatches are targeted and bounded — one survey, optional one follow-up. If more investigation is needed, split the rewrite.
- **No pushing or committing.** Ever.
