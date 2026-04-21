---
name: debug
description: Bug-find-and-fix. Dispatches the `bug-hunter` subagent to investigate a concern, presents the findings, and — on user confirmation — either fixes the bug inline in the current working tree (with a test) or escalates the investigation to `project-planner` to land on the backlog. Bugs either get fixed now or filed as a well-formed task; they don't rot as orphan reports. Triggers on `/debug` and phrases like "find the bug in X", "why is Y broken", "debug Z".
argument-hint: "<concern in a sentence or two>"
---

A bug skill built around the observation that bugs get fixed inline or not at all. `/debug` runs the hunt, surfaces the findings while the context is hot, and lets the user pick between "fix it now" (Claude edits the current working tree directly, with a test) or "too big — escalate" (hunter's report becomes input to `project-planner`, which lands a task the user picks up via `/work` when ready). There is no middle state where a report sits waiting.

## Trigger

**When to activate:**
- User invokes `/debug <concern>`.
- User says "find the bug in X", "why is Y broken", "what's going wrong with Z", "debug the <feature>".
- A hunch needs investigation before a decision is possible.

**When NOT to activate:**
- The concern is really a design fork, not a bug — route to `/design`.
- The user knows the bug and wants it filed as a task — use `/capture`.
- The user knows the bug and wants it fixed right now without investigation — just fix it directly; `/debug` adds friction for simple cases.
- The hunt needs to cover a large chunk of the codebase for a rewrite — use `/rewrite` instead; it runs the hunter as part of its own flow.

## Requires

- **Subagent:** `tab-for-projects:bug-hunter` — investigator.
- **Subagent:** `tab-for-projects:project-planner` — turns the hunter's report into a backlog task when the fix escalates.
- **MCP:** `tab-for-projects` — for the planner to write and for the skill to resolve the project on escalation.
- **Tools:** `Read`, `Edit`, `Write`, `Grep`, `Glob`, `Bash` — for the inline-fix path. The skill edits the current working tree directly when the user picks "fix now."

## Behavior

Four phases: **Hunt** (dispatch hunter, present findings), **Decide** (user picks inline vs. escalate), **Inline fix** (if chosen, Claude edits + tests in the current tree) or **Escalate** (if chosen, report → planner → task).

### 1. Hunt — dispatch the `bug-hunter`

1. Read the user's concern. If it's genuinely ambiguous — two-word hand-wave, no anchor — ask one clarifying question. Otherwise proceed.
2. Resolve the project (shared Project Inference convention: `.tab-project` file → git remote → cwd). Used only for the escalation path; not required to start the hunt.
3. Dispatch the `bug-hunter` subagent with `{ concern, project_id? }`. Optional: `scope` if the user pointed at a specific file/module, `hypothesis` if they named one.
4. When the hunter returns, render the report inline for the user. Don't paraphrase — show it.

If the hunter returns `inconclusive` or `underspecified`, surface the gap and ask the user to refine. Don't invent findings to fill the silence.

If the hunter's report names a root cause as **confirmed** or **likely**, present the decision block (step 2). If everything is only **suspected**, say so and ask whether the user wants to investigate further, escalate anyway, or drop it.

### 2. Decide — inline fix or escalate

Present a single decision block:

```
Hunter found: <1-line root-cause summary, confidence level>
  Primary: <file:line> — <mechanism>
  Adjacent: <count> other findings (see report)

Fix inline now, or escalate to a task?
  fix inline   — Claude edits this working tree and adds/updates a test
  escalate     — Hunter's report becomes input to project-planner → task on the backlog
  more info    — Ask the hunter a follow-up or investigate further
  drop         — Close without action
```

No default. The user picks.

**Recommend inline** when: the fix is small (one or two files, no migration), the mechanism is **confirmed**, and the test signal is obvious. Say so in one line.

**Recommend escalate** when: the fix crosses many files, requires a migration or coordinated change, needs a design call, or the hunter's confidence is only **likely** or **suspected**. Say so in one line.

### 3a. Inline fix — Claude edits the current tree

Chosen only when the user explicitly picks `fix inline`. This path breaks the worktree rule that `developer` enforces — `/debug` is synchronous and single-threaded; the worktree rule exists for parallel execution under `/work`, not here.

1. **Pin current behavior with a test first if tests exist for the area.** Run the suite; a failing test is the anchor. If the area has no tests, write the first one — capturing the bug's repro — before the fix.
2. **Make the fix.** Match the surrounding style. Narrow scope — only the files the hunter's report named as causal.
3. **Verify.** Run the test(s). Green passes, red means the fix is wrong; iterate or escalate.
4. **Do not touch CLAUDE.md, README, or CHANGELOG.** If doc drift is obvious, note it in the final summary — `/ship` will pick it up on the next pre-push sweep.
5. **Do not commit.** Leave the change staged for the user to review and commit themselves. A `/debug` fix is worth a user-authored commit, not a silent one.
6. **Summarize.** Print the files changed, the test that now pins the behavior, and any adjacent findings from the hunter that were *not* fixed — the user may want to `/capture` those or leave them.

### 3b. Escalate — hunter report → planner → task

Chosen when the user picks `escalate`, or when the hunter's report is too suspect / too large for an inline fix.

1. Dispatch `project-planner` with `{ hunter_report, project_id }` as shape 2 (see planner agent).
2. Planner produces one or more tasks on the backlog. Adjacent findings from the hunter may become separate tasks or may be mentioned in the primary task's body — planner decides.
3. Report back: "Filed task 01K… '<title>'. Run `/work` when ready to execute, or leave it in the backlog." Do not auto-invoke `/work`.

### 4. More info — extend the hunt

If the user picks `more info`:

- A follow-up concern gets dispatched to `bug-hunter` as a new hunt with the prior report as `hypothesis` context.
- When the follow-up returns, loop back to the decision block.

Bounded to **two follow-up rounds**. After the second, the skill insists on a decision — continued investigation with no verdict is how bugs rot.

### 5. Drop — close without action

If the user picks `drop`, the skill closes with a one-line acknowledgement and does nothing. No silent task filing, no background note.

## Output

- **Inline fix:** code + test changes in the current working tree, unstaged or staged (user's preference). No commit.
- **Escalate:** one or more tasks on the backlog via `project-planner`.
- **Drop:** nothing.
- **More info:** another round of investigation, same decision block.

## Principles

- **Bugs get fixed inline or filed as tasks. No middle state.** A hunter report that sits in the conversation and never becomes a fix or a task is the failure mode this skill is designed against.
- **Inline means inline.** When fixing now, Claude edits the current tree directly. Not a worktree, not a subagent. The worktree rule is for `/work`'s parallelism, not for a single synchronous bug fix.
- **Always pin behavior with a test.** Even for an inline fix. The test is the acceptance signal for the change.
- **The user picks.** The skill can recommend, but "fix inline vs. escalate" is a judgment call with the user's priorities baked in.
- **Two follow-up rounds max.** Bounded investigation. The third round means something structural is wrong; escalate or drop.
- **No silent drift.** If the fix implies doc drift, name it in the summary so `/ship` catches it.

## Constraints

- **No KB writes.** `/debug` never writes documents. If the hunt reveals an architectural question, escalate to a task with `category: design`; `/design` will write the doc.
- **No changelog or README edits in the inline-fix path.** `/ship` owns doc sweeps across shared files.
- **No auto-commit on inline fix.** The user commits. The skill leaves the change staged or unstaged per their preference.
- **No silent escalation.** Escalating to the planner is an explicit user choice, not a fallback when the hunter is uncertain.
- **No unbounded investigation.** Two follow-up rounds, then commit to a decision.
- **No pushing or merging.** Ever.
