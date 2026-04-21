---
name: develop
description: Conversational pair-programming mode. Takes prose intent and does the heavy lifting — surveys the codebase, pulls overlapping backlog tasks, shapes a lightweight plan, then iterates test-first through the pieces on the user's working tree. Dispatches `bug-hunter` once during ground when the survey warrants it; dispatches `developer` in a worktree on the user's call for bounded sub-scopes. Writes task state as work lands. Does not commit. Triggers on `/develop` and phrases like "let's build X", "pair on Y", "methodically work through Z", "start on the W implementation".
argument-hint: "<what you're building, in prose>"
---

The "pair programming" skill. `/develop` takes a prose description of what the user wants to build and does the heavy lifting: searches the code space, loads overlapping backlog tasks, surfaces KB constraints, shapes a lightweight plan, then iterates test-first on the working tree. Unlike `/work`, it is conversational and inline — the main thread stays in the loop, edits land where the user is sitting, and each piece gets a confirm. Unlike `/plan`, it produces code. Unlike `/design`, it implements.

## Trigger

**When to activate:**
- User invokes `/develop <intent>`.
- User says "let's build X", "pair on Y", "methodically work through Z", "start on the W implementation".
- User has a feature or improvement in mind and wants to work through it slowly with Claude doing the search, test writing, and subagent plumbing.

**When NOT to activate:**
- User wants a bug found and fixed — use `/debug`.
- User wants tasks filed on the backlog without execution — use `/plan` or `/capture`.
- User wants ready backlog tasks executed autonomously — use `/work`.
- User wants a design decision captured as a KB doc — use `/design`.
- User wants a single drop-in change they already know how to make — edit directly; `/develop` adds ceremony for trivial cases.
- The scope sprawls across many surfaces with real decomposition needed — hand off to `/plan`. `/develop` surfaces this during Ground and suggests the switch.

## Requires

- **MCP:** `tab-for-projects` — project resolution, task lookups, task writes (state transitions and new task filings), KB reads.
- **Subagent:** `tab-for-projects:bug-hunter` — optional, single-shot during Ground when a codebase survey warrants it.
- **Subagent:** `tab-for-projects:developer` — optional, opt-in per sub-scope for bounded work delegated to a worktree.
- **Tools:** `Read`, `Grep`, `Glob`, `Bash` — codebase survey, running tests, checking git state.
- **Tools:** `Edit`, `Write` — inline implementation on the working tree. The skill edits directly; it does not route all code through `developer`.

## Behavior

Four phases: **Ground** (understand the problem), **Shape** (plan with the user), **Build** (iterate), **Wrap** (summarize and hand back). Delegation to `developer` is a sub-path of Build, not a separate phase.

### 1. Ground — understand what's being asked and what exists

1. **Read the intent.** If the description is genuinely vague — two-word hand-wave with no anchor — ask one clarifying question. Otherwise proceed.
2. **Resolve the project.** Shared Project Inference convention (`.tab-project` → git remote → cwd → recent activity). Below confident, ask. Needed for backlog and KB lookups.
3. **Pull overlapping backlog tasks.** Search by group_key, tags, and text for tasks that plausibly cover the intent. If one or more exist, show the user:

```
Backlog overlap:
  01KX… "Add MFA enrollment"       — todo, ready
  01KY… "Rework auth middleware"   — todo, below-bar

Load one as the session anchor? (id / none / skip)
```

If the user picks an ID, that task becomes the anchor — transitions to `in_progress` at Build start, closes to `done` when its acceptance signal passes. `none` proceeds without an anchor; `skip` suppresses the backlog check this session.

4. **KB pass.** Quick `list_documents` / `search_documents` for conventions, prior decisions, or architecture docs that constrain the work. Read the substance of anything load-bearing and surface it before planning — the user shouldn't discover a constraint halfway through Build.
5. **Codebase survey.** Start inline with `Read`, `Grep`, `Glob` to understand the relevant files, existing patterns, and integration points. For non-trivial scopes (multiple modules, unclear boundaries, unfamiliar subsystems), dispatch `bug-hunter` once with a tailored concern: "Survey the current shape of `<target>`. Identify entry points, patterns, coupling, and what tests exist." Single dispatch — not a loop.
6. **Surface findings.** Render the landscape before the plan: what exists, what the conventions are, what the tests look like, what the anchor task (if any) references.

**Escalation check.** If the survey shows the work sprawls beyond a pair-programming session — many surfaces, needs real decomposition, several unmade design calls — say so:

```
This is a /plan-shaped scope — <N> surfaces, <M> unmade decisions.
  Proceed with /develop on a narrowed slice, or hand off to /plan?
```

The user picks. `/develop` does not force itself onto work that wants a real plan.

**Anchor readiness check.** If the user loaded an anchor task and it's below the readiness bar, surface the gap and point at `/plan groom <task-id>`. Do not reshape the task inline — grooming lives in `/plan`.

### 2. Shape — lightweight plan with the user

Not `/plan` territory. No fan-out, no parallel planners, no backlog writes. Just:

1. **Name the pieces.** Break the intent into ordered chunks — each a natural test-and-implement cycle (a function, a small module, a refactor step, a new component).
2. **Name the test approach.** For each piece: what test pins it? New file or existing one? Match the area's conventions — follow the framework and style already in use. If the area has no tests, start one capturing the behavior of the first piece.
3. **Mark delegation candidates.** Flag any piece that's bounded and self-contained enough to dispatch to `developer` in a worktree if the user wants parallelism. Default is inline.
4. **Confirm:**

```
/develop — <Project>, <intent summary>
Anchor: 01KX… "<title>"  (or: no anchor)

Plan:
  1. <piece> — test: <approach>                  — inline
  2. <piece> — test: <approach>                  — inline
  3. <piece> — test: <approach>                  — delegation candidate
  4. <piece> — test: <approach>                  — inline

Constraints surfaced:
  - <KB doc or convention that shapes this>
  - <existing pattern in the code>

Proceed? (y / edit / cancel)
```

`edit` accepts inline adjustments — add/remove pieces, reorder, change test approach, toggle delegation candidates. `cancel` exits cleanly.

### 3. Build — iterate piece by piece

The core loop. For each piece in order, pick the venue: inline (default) or delegate (if marked as a candidate and the user opts in this round).

**Inline path (default).**

1. **Write or update the test first.** Pin behavior before changing it. New behavior → write the test, confirm it fails. Refactor → pin the existing behavior, confirm the test passes before edits. If the area has no tests, the first test for the piece becomes the first test for the area.
2. **Implement.** Narrow scope — only the files this piece needs. Match surrounding style.
3. **Run the test.** Green means done; red means iterate. **Three iterations is the ceiling.** If a piece doesn't converge in three red-green cycles, stop and discuss — something structural is off.
4. **Brief check-in.** One-line summary of what landed ("piece 2/5: added TOTP provider, test passing"). Proceed to the next piece unless the user interrupts.

**Delegate path (opt-in per piece).**

1. **Confirm the dispatch:**

```
Dispatch developer for piece <n> — "<piece summary>"?
  Scope: <files, boundaries>
  Test: <approach>
  Worktree: isolated (via Agent)

Proceed? (y / inline instead / skip this piece)
```

2. **Dispatch `developer`** with `isolation: "worktree"`. If the piece has a backlog task ID, pass `{ task_id }`; if not, file a short task first via `create_task` so the dispatch stays ID-shaped (matches the `/work` → `developer` contract).
3. **When the dev returns**, report the worktree path, commit hash, and test result. The dev's commit stays in the worktree — `/develop` does not merge.
4. **Parallel dispatches** are possible when multiple pieces are delegation candidates with no shared files — same rule as `/work --parallel`. Single-message, multiple `Agent` calls.

**Design forks pause the flow.** If a real trade-off surfaces mid-build that only the user can make:

```
Design call needed: <question>
  Options: <A> / <B> / <C>

Handle as:
  decide inline — you answer now, we continue
  file design   — file a design ticket; /develop pauses until you run /design
  defer         — file as follow-up task, skip this piece, continue on the rest
```

No default. The skill does not pick a winner.

**Task state along the way.**
- Anchor task → `in_progress` on first piece start (if not already).
- Per-piece progress tracked in conversation state, not the MCP. Tasks aren't per-piece.
- New tasks filed mid-session (for deferred pieces, surfaced follow-ups, or design forks) go to the backlog at the readiness bar. Design-category forks file as `category: design`.
- Anchor task closes to `done` during Wrap, not here — closure requires the full acceptance signal.

### 4. Wrap — summarize and hand back

When the last piece lands (or the user closes the session):

1. **Verify.** Run the full relevant test suite one last time. All green is the bar for closing the anchor.
2. **Task writes.**
   - Anchor → `done` if acceptance passed. `todo` with a progress note if the user stopped mid-way.
   - Follow-ups filed mid-session stay `todo`.
3. **Doc drift check.** Note any README / CLAUDE.md / CHANGELOG drift implied by the work. Do not edit — `/ship` owns those sweeps.
4. **Do not commit.** The working tree is staged or unstaged per the user's preference. The user owns the commit.
5. **Summary:**

```
/develop complete — <Project>, <intent>
Anchor: 01KX… "<title>" → done   (or: in_progress, progress noted)

Pieces landed (5):
  ✓ <piece> — inline — test: src/auth/mfa.test.ts
  ✓ <piece> — inline — test: src/auth/mfa.test.ts
  ✓ <piece> — delegated → /tmp/wt-01KZ… (1 commit)
  ✓ <piece> — inline — test: src/auth/totp.test.ts
  ✓ <piece> — inline — test: src/auth/mfa.test.ts

Working tree (uncommitted):
  src/auth/mfa.ts
  src/auth/mfa.test.ts
  src/auth/totp.ts
  src/auth/totp.test.ts

Worktrees (merge when ready):
  /tmp/wt-01KZ… → 1 commit

Follow-ups filed:
  01KW… "Extend MFA to SSO users"          (deferred)
  01KV… "Decide: recovery code format"     (design fork)

Doc drift for /ship:
  README.md — "Auth" section likely stale

Next: review the diff, commit when ready. /ship when you're ready to push.
```

## Output

- Code + tests on the user's working tree, uncommitted.
- Zero or more commits in worktrees from delegated `developer` dispatches.
- Task state writes: anchor task transitions, any new tasks filed mid-session.
- No source code outside the working tree and dispatched worktrees. No KB writes. No changelog / README / CLAUDE.md edits. No commits on the working tree. No pushes.
- A structured wrap report with the shape above.

## Principles

- **Pair programming, not handoff.** The user stays in the loop — each piece gets a confirm, each delegation is opt-in, each design fork pauses the flow. If the user wanted hand-off, they'd run `/work`.
- **Survey before shape; shape before build.** The cheapest place to catch a wrong direction is before the first test is written. `/develop` invests in Ground.
- **Test-first where tests exist; test-along where they don't.** A piece without a test has no acceptance signal, which means no way to declare it done.
- **Inline is the default venue.** Worktrees are for bounded self-contained chunks the user opts into. The whole point of `/develop` is that edits land where the user is sitting.
- **Escalate when the scope wants real decomposition.** `/develop` is a pair-programming session, not a replacement for `/plan`. If the survey shows sprawl, say so.
- **Design forks pause; they don't get guessed.** Real trade-offs route to `/design` or file as design tickets. `/develop` implements; it does not decide.
- **Three iterations is the ceiling on any one piece.** If a piece doesn't converge in three red-green cycles, something structural is off — stop and discuss.
- **No auto-commit, ever.** The working tree is the user's. `/develop` leaves it ready for review.

## Constraints

- **No writes below confident project inference.** Ask or stop.
- **No commits on the working tree.** The user commits.
- **No pushes or merges.** Ever.
- **No KB writes.** Design forks become design tickets or a `/design` invocation; `/develop` does not author KB docs.
- **No changelog, README, or CLAUDE.md edits.** Doc drift gets noted in the wrap summary for `/ship`.
- **No silent resolution of design forks.** If a fork surfaces, the decision block fires — never papered over.
- **No worktree merges.** Delegated work lands as commits in worktrees; the user integrates.
- **No unbounded survey.** One `bug-hunter` dispatch during Ground, max. Further investigation is conversational reads, not more subagent hops.
- **No grooming of loaded tasks.** If the anchor is below-bar, surface the gap and point at `/plan groom` — don't reshape it mid-`/develop`.
- **No mid-session decomposition via `project-planner`.** If the work wants a plan, hand off to `/plan`. Don't bolt a mini-planner into `/develop`.
- **No executing design-category tasks as anchors.** If the user picks a design task, redirect to `/design`.
- **No passing prose to delegated `developer` dispatches.** IDs only — file a task first if the piece doesn't have one.
