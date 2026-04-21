---
name: capture
description: Zero-friction task drop. Captures a single task from the current conversation — pulls title and summary from what's already been said, asks one clarifying question only if truly needed, and files it raw. No grooming, no scoring, no interview. `project-planner` grooms the task later when `/work` picks it up. Triggers on `/capture` and phrases like "file this as a task", "add a todo", "drop that on the backlog", "capture this".
argument-hint: "[optional: one-line hint]"
---

The lightest possible path from "that should be a task" to a backlog entry. `/capture` reads the conversation, writes a raw task, and exits. Grooming is `project-planner`'s job and happens downstream when `/work` picks the task up. The reason this skill exists: a thought worth capturing is often not worth interrupting the current work to groom.

## Trigger

**When to activate:**
- User invokes `/capture`, optionally with a one-line hint describing what to file.
- User says "file this as a task", "add a todo for that", "drop that on the backlog", "capture this", "make a task".
- A task-worthy item came up in the current turn and the user wants to park it.

**When NOT to activate:**
- User wants to plan a rewrite or a chunk of work — use `/rewrite`.
- User wants to file a design question — `/capture` is fine, but `/design` (on the captured task) is where the decision happens.
- User wants to groom several tasks at once — dispatch `project-planner` directly or let `/work` handle grooming downstream.
- User wants to execute immediately — go straight to `/work` or direct conversation.

## Requires

- **MCP:** `tab-for-projects` — for `create_task`, `get_project_context` (to name a project if one is resolvable).

## Behavior

Three phases: **Read**, **Confirm** (once, only if needed), **Write**.

### 1. Read — pull title and summary from context

Infer from:

- The user's last turn — often the title is sitting right there.
- The surrounding conversation (last ~5 turns) — enough signal for a summary.
- The optional one-line argument, if provided.

Shape:

- **Title** — verb-led, specific, under ~80 chars. "Fix the stale README badge" — not "README badge issue."
- **Summary** — 1–2 sentences describing what and why. If the conversation doesn't give enough to write a summary, leave it blank rather than fabricate.
- **Category** — infer when obvious (`bugfix` for bugs, `feature` for new behavior, `docs` for docs, `refactor` for cleanup, `chore` for housekeeping). If unclear, leave it unset; planner will set it.
- **Project** — resolve via the shared Project Inference convention: `.tab-project` → git remote → cwd basename → recent activity. If the resolution is uncertain, surface the options in the confirm block.

Do **not** set effort, impact, acceptance signal, or dependencies. That's grooming — planner's job. A raw task is allowed to be raw; the readiness bar applies at `/work` time, not at capture time.

### 2. Confirm — only if truly needed

The confirm is conditional. Skip it when:

- Title is clear from context (the last turn says exactly what to file).
- Project resolves with confidence.
- No ambiguity worth clarifying.

Ask one question when:

- Title is ambiguous — the conversation touched two things and it's unclear which to file. ("Capture which — the session store refactor, or the stale test?")
- Project resolution has two plausible candidates and writing the task to the wrong project is a real cost.

**Never ask more than one question.** If more clarification would be needed, capture a minimal task (title + note of ambiguity in summary) and let planner groom it later. The whole point of `/capture` is non-interruption.

### 3. Write — file the task

`create_task({ title, summary?, category?, project_id, status: "todo" })`. Capture the returned task ULID.

Report back in one line:

```
Filed 01K… "<title>" on <Project Name>. Planner will groom it when /work picks it up.
```

## Output

- One task on the backlog — raw, possibly under-specified. That's fine.
- A one-line confirmation with the task ULID.
- No scoring, no acceptance signal, no dependency wiring at this stage.

## Principles

- **Zero friction is the feature.** A capture that takes 30 seconds is a capture that happens. A capture that takes five minutes is a capture that doesn't.
- **Raw is allowed.** Grooming happens downstream. The backlog tolerates below-bar tasks as long as they get groomed before execution.
- **One question, max.** If it takes more, the task is too complex for `/capture` — planner will handle it at `/work` time.
- **Trust planner.** The design is: `/capture` drops, `/work` → `project-planner` grooms, `developer` executes. Each stage does one thing.

## Constraints

- **One task per invocation.** If the user wants to file multiple tasks, call `/capture` multiple times. The skill's job is a single drop.
- **Never groom.** No effort, no impact, no acceptance signal, no dependencies at capture time.
- **Never write KB docs.** Ever.
- **Never interrupt the conversation for more than one clarifying question.** Under-specified captures are fine; interruptions aren't.
- **Project resolution below confident → surface options.** Don't silently pick a project when two are plausible and the choice matters.
