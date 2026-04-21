---
name: work
description: Autonomously execute ready tasks from the project backlog. Walks the dependency graph as a persistent loop, dispatches each above-bar non-design task to the `developer` subagent inside a git worktree, surfaces below-bar and design-category tasks for the user to handle via `/plan groom` or `/design`, batches halts and new design forks into a single end-of-run report, and manages parallelism across worktrees. Strictly above-bar — below-bar tasks are never groomed mid-run. Use when the backlog is ready and the user wants to hand off execution. Triggers on `/work` and phrases like "finish the backlog", "execute the ready tasks", "work through the todo list".
argument-hint: "[optional: group_key, --max=N, --dry-run, --parallel=N]"
---

Hand over execution. `/work` reads the ready portion of the backlog, dispatches each execution-ready task to `developer` in an isolated git worktree, walks the dependency graph as work completes, and produces a single end-of-run report covering what shipped, what got flagged, and what needs a user decision. It never runs below-bar tasks, never executes design-category tasks, never grooms mid-run, and never sets task state on a subagent's behalf.

## Trigger

**When to activate:**
- User invokes `/work`, optionally scoped to a `group_key` or limited by `--max=N`.
- User says "finish the backlog", "execute the ready tasks", "work through the todo list", "run the groomed tasks".
- User just finished a `/plan` or `/design` pass and wants to cash in the emitted implementation tickets.

**When NOT to activate:**
- User wants to file new work — use `/capture` or `/plan`.
- User wants to shape below-bar tasks — use `/plan groom`. Grooming never happens inside `/work`.
- User wants to execute a single specific task with tight oversight — direct conversation is better than autonomous mode.
- Working tree is dirty — the skill will refuse; commit or stash first.

## Requires

- **MCP:** `tab-for-projects` — for project resolution, task reads, dependency-graph reads. `/work` reads task state after a subagent returns; it never writes task state itself.
- **Subagent:** `tab-for-projects:developer` — executes tasks inside worktrees.
- **Tool:** `Agent` — dispatches `developer` with `isolation: "worktree"`.
- **Tool:** `Bash`, `Read`, `Grep`, `Glob` — for working-tree inspection, git state, and validation. `/work` does not write code; `developer` does.
- **Environment:** a git repo with a clean working tree. Uncommitted changes abort before start.

## Behavior

### 1. Resolve the project

Shared Project Inference convention:

1. Explicit `project:<id or title>` argument wins.
2. `.tab-project` at repo root if present.
3. Git remote `origin` — exact repo-name match is high confidence.
4. cwd basename and parent segments against project titles.
5. Most recently updated plausible project — never sole signal.

Below **confident**, ask. No writes below confident.

### 2. Build the initial plan

1. Pull all `todo` tasks for the project. Apply filters (`group_key` if passed).
2. Pull the dependency graph.
3. For each task, classify into one of two buckets:
   - **Ready** — above the readiness bar (verb-led title, 1–3 sentence summary, `effort` / `impact` / `category` set, concrete acceptance signal, no unmet blockers), category is **not** `design`. Enters the eligible set.
   - **Skipped** — won't run this pass. Sub-reasons:
     - *design* — category is `design`; needs `/design` to resolve.
     - *below-bar* — missing one or more readiness fields; needs `/plan groom` to shape.
     - *blocked* — blocked by unready tasks (design or below-bar) further up the chain.
4. Topologically order the ready set by dependency edges.
5. Respect `--max=N` if given. **No default cap** — `/work` is persistent and runs until the eligible set is empty, the user interrupts, or three consecutive task failures abort the run.
6. Show the plan:

```
/work — <Project Title>
Ready: 6 tasks (persistent loop; no max cap)
Skipped: 6 tasks (won't execute this run)
  2 design        — run /design <id> to resolve each
  3 below-bar     — run /plan groom to shape them
  1 blocked       — waiting on above

Plan (first 5 shown; loop continues until eligible set empty):
  1. 01KX… "Update README badges"       → developer (worktree)
  2. 01KY… "Refactor session store"     → developer (worktree)
  3. 01KZa… "MFA enrollment"            → developer (worktree, group auth-mfa)
  4. 01KZb… "MFA verification"          → developer (worktree, group auth-mfa)
  5. 01KQ… "Improve search performance" → developer (worktree)
  ...

Proceed? (y / edit / dry-run)
```

Accept `edit` (user reorders or drops tasks), `dry-run` (prints plan only, no execution), or `--max=N` / `--parallel=N` flags.

### 3. Dispatch

For each eligible (ready) task:

1. **Dispatch `developer`** with `isolation: "worktree"` and `{ task_id, parent_task_id? }`. The worktree is created by the Agent tool; the dev asserts it on entry.

The dispatch payload is **IDs only**. `/work` never passes task prose to a subagent. Subagents fetch their own context via the MCP. This is the mechanism that keeps the main thread's context window small across long persistent runs.

No grooming. If a task reads below-bar once `developer` loads it, the dev flags it back to `todo` with a specific gap note — the task surfaces in the end-of-run report, not in a groom loop.

### 4. Design-category tasks are terminal

`/work` never dispatches for a task with `category: design`. Design decisions encode trade-offs only the user can supply. When the walk encounters a design task:

- Does **not** dispatch any subagent.
- Does **not** set task state — the task stays in `todo`.
- Records the task ID in the "awaiting human" bucket for the end-of-run report.
- Advances to the next task.

New design tasks filed by `developer` mid-run (forks surfaced during implementation) flow into the same bucket.

### 5. Status ceremony belongs to the subagent

`/work` does not call `update_task` on dispatched tasks. `developer` owns every transition:

- `in_progress` on claim.
- `done` on verified completion.
- `todo` with a specific note on failure, halt, or below-bar flag.

After a dev returns, `/work` re-reads task state to determine outcome:

| Dev-returned state       | `/work` response                                                             |
| ------------------------ | ---------------------------------------------------------------------------- |
| `done`                   | Record the commit + worktree path. Advance.                                  |
| `flagged` (back to `todo` with a bar-gap note) | Move to the skipped bucket. Advance.                          |
| `todo` with "halt" note  | Collect for end-of-run "needs your call" section. Advance.                   |
| `todo` with "failed"     | Counts against the three-strikes abort threshold. Advance.                   |

**On every dev return, re-evaluate the dependency graph.** New tasks filed by the dev or completions that unblocked existing tasks may expand the eligible set. Pull the graph again before picking the next task. Re-evaluation re-classifies everything against the ready / skipped buckets — below-bar tasks stay skipped, they do not get shaped.

### 6. Worktree reconciliation

`developer` commits **inside the worktree**. The skill does not merge or push. At the end of the run (or after each completion when serial), `/work` reports the worktree paths for the user to reconcile — typically a rebase or merge into the working branch, or a review pass before merging.

The skill provides the commit hashes and worktree paths; the user decides when to integrate.

### 7. Parallelism

Default: **serial**. Each task runs start-to-finish before the next claims.

`--parallel=N` (N ≥ 2) allows concurrent `developer` dispatches when **all** of:

- Tasks share no dependency edges.
- Tasks are in the eligible set simultaneously (after topological ordering).
- Each dispatch gets its own worktree (Agent tool's `isolation: "worktree"` handles this).

Parallel dispatch spawns subagents via a single message with multiple `Agent` tool calls. On any return, re-evaluate the graph before selecting the next batch.

Parallelism is safe across worktrees — each dev works on an isolated tree. Shared-doc files (CLAUDE.md, README, CHANGELOG) are off-limits to `developer` exactly so parallel runs can't collide; `/ship` handles those centrally.

### 8. Halts and design tasks are batched

`/work` does not interrupt the user mid-run. Throughout the loop:

- Halt notes accumulate in a queue.
- Design-category tasks (existing or newly filed) accumulate in an "awaiting human" queue.
- Below-bar flags from dev returns accumulate in a skipped-at-runtime queue.
- All other status changes and new tasks flow without pause.

At end-of-run, these queues surface in the single "needs your call" section of the report.

### 9. Handle failure

If a task fails — acceptance signal doesn't pass, dev returns `todo` with a failed note:

- Dev owns the failure note on the task.
- `/work` counts the failure against the three-strikes abort threshold.
- Advance.

**Abort conditions** (stop the whole run):

- Git working tree (outside worktrees) ends up in a dirty state `/work` can't clean up safely.
- Three consecutive task failures — something's wrong with the environment or the backlog.
- User interrupts.

When abort fires, skip directly to end-of-run reporting for whatever completed successfully.

### 10. End-of-run report

```
/work complete — <Project Title>

Executed: 5 tasks · 5 worktrees with commits · 2 new tasks filed by subagents

  ✓ 01KX… Update README badges                   → developer (worktree /tmp/wt-01KX…)
  ✓ 01KY… Refactor session store                 → developer (worktree /tmp/wt-01KY…)
  ✓ 01KZa… MFA enrollment                        → developer (worktree /tmp/wt-01KZa…)
  ✓ 01KZb… MFA verification                      → developer (worktree /tmp/wt-01KZb…)
  ✗ 01KZc… MFA recovery                          → developer (halt — spec unclear)

Skipped (6 tasks — won't run until shaped or decided):
  2 design       — run /design <id>:
    01KU "Choose MFA vendor"
    01KT "Session-store boundary"  (new — filed by dev during 01KY)
  3 below-bar    — run /plan groom:
    01K1 "Improve search performance" — no acceptance signal
    01K3 "Rethink Y" — no summary
    01KZc "MFA recovery" — halted mid-run; spec ambiguity
  1 blocked      — waiting on above:
    01K2 "Investigate X" — blocked by 01K3

Worktrees (4 — merge/rebase into your working branch when ready):
  /tmp/wt-01KX…  → 1 commit
  /tmp/wt-01KY…  → 1 commit
  /tmp/wt-01KZa… → 1 commit
  /tmp/wt-01KZb… → 1 commit

Doc drift surfaced by devs (for /ship on next pre-push):
  README.md — "MFA setup" section likely stale
  tab-for-projects/CLAUDE.md — routing table mentions old categories

Suggest: reconcile the worktrees, then /plan groom to shape the below-bar set, /design the design tickets, then /ship when ready.
```

## Output

- One worktree per completed `developer` dispatch, each with one commit. `/work` does not merge or push.
- MCP state: `developer` sets completed tasks to `done`, failed/halted/flagged tasks to `todo` with notes. `/work` itself writes nothing to task records.
- New tasks filed by `developer` appear in the backlog (at the bar for implementation; as `category: design` for forks).
- A single end-of-run report with the structure above, including doc-drift hints for `/ship`.

## Principles

- **The readiness bar is absolute — and `/work` never shapes it.** A below-bar task is surfaced in the skipped bucket; `/plan groom` is the only path to shape it. Grooming-during-execution was the infinite-loop shape the old version had; this version eliminates the path entirely.
- **Verify, don't declare.** "Done" requires the acceptance signal to pass — and the `developer` that did the work is the one that declares it.
- **IDs, not prose.** Every byte of task context that flows through the main thread is a byte the main thread has to carry. Subagents fetch.
- **One task = one commit, inside a worktree.** `developer` enforces this. Worktrees mean parallel dispatch is safe.
- **Skipping is a feature, not a failure.** A run that executes 5 of 11 tasks and surfaces the other 6 with specific reasons is better than one that silently grooms and ships 11 half-shaped changes.
- **Halts, design tasks, and below-bar flags are batched.** The user ran `/work` to hand off execution; breaking in for every exception defeats the handoff.
- **Design is the user's job; planning is `/plan`'s.** `/work` surfaces both and gets out of the way.
- **The skill stops at the worktree.** Reconciling into the working branch is the user's call; so is pushing, so is shipping.

## Constraints

- **No writes below confident project inference.** Ask or stop.
- **No work on a dirty working tree.** The skill stops and asks before starting.
- **No setting task state on a subagent's behalf.** Status ceremony is the subagent's job.
- **No passing task prose to subagents.** IDs only — `task_id`, `parent_task_id`.
- **No grooming.** `project-planner` is not dispatched from `/work`, period. Below-bar tasks skip; the user runs `/plan groom` separately.
- **No mid-run interruption for halts, design forks, or below-bar flags.** Batch to end-of-run.
- **No force-push, no destructive git, no rewriting shared history.** Ever.
- **No executing below-bar tasks.** Skip, don't shape.
- **No executing design-category tasks.** Surface with a pointer to `/design`.
- **No merging worktrees.** The user integrates.
- **Never skip acceptance-signal verification.** A task without verification is not done.
- **Three-strikes abort is non-negotiable.** Three consecutive failures mean something structural is wrong — stop the run and hand back.
