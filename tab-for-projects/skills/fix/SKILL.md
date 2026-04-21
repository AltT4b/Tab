---
name: fix
description: Capture a single task on the backlog from the current conversation. Pulls title, summary, acceptance signal, and scoring fields from what's already been said — minimal research, no interview beyond one clarifying question if truly needed. Use when the user wants to file a small, well-understood piece of work without leaving the conversation. Triggers on `/fix` and phrases like "add a task for that", "file this as a task", "capture that as a todo".
argument-hint: "[optional one-line hint]"
---

The "I just noticed something, write it down" skill. The user is mid-conversation, something surfaced that needs filing, and they don't want a planning session to capture it. This skill reads the conversation, synthesizes a single task that starts above the readiness bar, confirms once, and writes.

## Trigger

**When to activate:**
- User invokes `/fix` optionally followed by a one-line hint.
- User says "add a task for that", "file this as a task", "capture that as a todo", "make a task to fix X".
- User is closing a thread and wants the leftover filed before moving on.

**When NOT to activate:**
- User wants many tasks across a scope, or wants to open a planning session — use `/project`.
- User wants to start executing — use `/work`.
- User wants to edit an existing task — use the MCP `update_task` directly or `/backlog`.
- The conversation has no concrete thing to file (user is still thinking) — offer `/think` instead.

## Requires

- **MCP:** `tab-for-projects` — for project resolution and task creation.

## Behavior

### 1. Resolve the project

Resolve which project this run targets:

1. Explicit `project:<id or title>` argument wins.
2. Read `.tab-project` at repo root if present.
3. Parse git remote `origin`; exact repo-name match is high confidence.
4. Match cwd basename and parent segments against project titles.
5. Fall back to most recently updated plausible project. Never sole signal.

Below **confident**, ask. No writes below confident.

### 2. Synthesize the task from conversation

Scan the recent conversation for the concrete thing being filed. Build:

- **Title** — verb-led, specific. "Fix stale badge in README" beats "README issue".
- **Summary** — 1–3 sentences capturing why + what. Pulled from the conversation, not invented.
- **Acceptance signal** — a concrete test, behavior change, or artifact. If the conversation made clear what "done" looks like, use it. If not, this is the most common gap — ask.
- **Effort** — estimate from what was discussed. `trivial` / `low` / `medium` / `high` / `extreme`.
- **Impact** — estimate. Default `low` unless the conversation indicated otherwise.
- **Category** — `feature` / `bugfix` / `refactor` / `test` / `perf` / `infra` / `docs` / `security` / `design` / `chore`.
- **`group_key`** — only set if the task obviously belongs to an in-flight group. Don't invent groups for single tasks.

### 3. Ask at most one question

If exactly one required field can't be inferred confidently from the conversation, ask **one specific question** to close the gap. Examples:

- "What's the acceptance signal — a passing test, or just that the error stops appearing?"
- "Is this `low` or `medium` effort? Ballpark."

If two or more fields are ambiguous, the conversation doesn't actually contain enough to file a ready task — tell the user and suggest `/project` (which can run a short interview inside a planning session) or a bit more discussion first. Don't file a below-bar task.

### 4. Confirm, then write

Show the proposed task in compact form:

```
[title] — effort/impact/category
Summary: [1–3 sentences]
Acceptance: [one line]
```

Ask: "File this?" Accept inline edits. Once confirmed, continue to the design-ancestry check (§5) if the task's category isn't `design`, then create the task.

### 5. Design-ancestry check (non-design tasks only)

Implementation work often trails a design decision that hasn't been made yet. Before firing `create_task` on any task whose category is not `design`, surface one short prompt:

```
Before filing — is this blocked by a design decision you haven't made yet?

  - Name an existing design task (01K…) and I'll wire a `blocks` edge.
  - Say `file design` and I'll file a design task inline and wire the edge.
  - Say `no` to proceed as-is.
```

Three responses:

- **`no`** (or a no-shaped phrase like `nope`, `already decided`, `n/a`) — proceed to `create_task` with no extra wiring.
- **An existing task ULID** — `get_task` to verify it exists and is `design`-category. If it isn't design or doesn't exist, say so and re-prompt; don't silently wire the wrong thing. On verify, file the new task, then add a `blocks` dependency from the design task to the new task (`update_task` on the new task with `add_dependencies: [{ task_id: <design-id>, type: "blocks" }]`).
- **`file design`** — run a compact inline design-task proposal: title (verb-led, e.g. `Decide <X>`), 1–3 sentence summary (usually pulled from the same conversation), acceptance signal (almost always `a KB doc at folder X capturing decision Y` — point at the `/design` skill at `tab-for-projects/skills/design/SKILL.md` for how the decision will eventually land). Confirm the design task in one compact block, then file it with `category: design`. Once it's filed, file the original task and wire the `blocks` edge from the design task to it. Report both IDs.

Skip §5 entirely when the task's category is `design` — design tasks don't need a design ancestor.

## Output

A single task in the MCP, above the readiness bar. When the design-ancestry check fired and the user pointed at or filed a design task, also a `blocks` edge between the two (and, in the `file design` case, a second filed design task). Skill closes with a one-line acknowledgement:

```
Filed 01KX… in Tab.
```

When a design ancestor was filed or wired:

```
Filed 01KX… (blocked by design task 01KY…).
```

No fanfare. The user was in the middle of something else.

## Principles

- **Conversation is the source.** The user just explained the thing. Don't re-elicit it.
- **One question, max.** Two means the conversation wasn't ready to file. Say so.
- **Small is a feature.** `/fix` is for the leftover thought, the drive-by observation, the "while I'm here." Don't grow it into planning.
- **Confirm, but quickly.** One glance, one yes. Not a review.

## Constraints

- **No writes below confident project inference.** Ask or stop.
- **Readiness bar is non-negotiable.** Even for `/fix`. A trivial task still needs a title, summary, and acceptance signal.
- **No multi-task filing.** If the conversation surfaced several things, hand off to `/project` rather than batching.
- **Don't edit existing tasks.** This skill creates. Pointing out a duplicate is fine; merging is not.
