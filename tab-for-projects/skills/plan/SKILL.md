---
name: plan
description: Intent-to-backlog. Point it at a scope or name an outcome; `/plan` dispatches `project-planner` (sometimes in parallel across sub-scopes) to survey the codebase, returns a synthesized batch of task proposals, and — on user confirm — writes them to the backlog. Four modes via menu: Intent (describe an outcome), Survey (audit a scope), Groom (shape below-bar tasks), Rewrite (plan a replacement). Does not execute; hand off to `/work`. Triggers on `/plan` and phrases like "plan X", "figure out what needs doing for Y", "decompose Z", "rewrite the W layer".
argument-hint: "[intent | survey | groom | rewrite] [<scope or description>]"
---

The "intent becomes backlog" skill. `/plan` is where the product is shaped into tasks — whether the user names an outcome, points at code to audit, hands over below-bar tasks to groom, or plans a rewrite. It dispatches `project-planner` in scope-mode (proposals, no writes), fans out parallel planners on split sub-scopes, synthesizes the batch, and writes tasks only after the user confirms.

## Trigger

**When to activate:**
- User invokes `/plan` with no args (opens menu), or `/plan <mode> <scope>` to skip the menu.
- User says "plan X", "figure out what needs doing for Y", "decompose Z", "survey the codebase for W", "rewrite the <layer>", "redo the <system>".
- User just finished `/design` and wants to turn the decision into implementation tickets.
- User has a pile of below-bar tasks that need shaping before `/work` can run.

**When NOT to activate:**
- User wants to file a single task from the current conversation — use `/capture`.
- User wants to execute ready tasks — use `/work`.
- User wants a decision captured as a KB doc — use `/design`.
- User wants a bug found and fixed — use `/debug`.

## Requires

- **MCP:** `tab-for-projects` — project resolution, KB lookups, task writes after confirm.
- **MCP:** `exa` — optional, used only in rewrite mode for best-practice research. Always available per project constraints.
- **Subagent:** `tab-for-projects:project-planner` — the workhorse. Dispatched in scope-mode (returns proposals) for intent/survey/rewrite, shape-1 (writes) for single-task groom.
- **Subagent:** `tab-for-projects:bug-hunter` — optional, used only in rewrite mode when a deep codebase survey is worth the round-trip.
- **Tool:** `Agent` — dispatches subagents, including parallel fan-out on split TODOs.
- **Tools:** `Read`, `Grep`, `Glob` — quick on-the-fly lookups while hosting the conversation. Planner does the deeper reading.

## Behavior

### 1. Resolve the project

Shared Project Inference convention:

1. Explicit `project:<id or title>` argument wins.
2. `.tab-project` at repo root if present.
3. Git remote `origin` — exact repo-name match is high confidence.
4. cwd basename and parent segments against project titles.
5. Most recently updated plausible project — never sole signal.

Below **confident**, ask. No writes below confident.

### 2. Pick the mode

If the argument named a mode (`/plan intent add MFA`, `/plan survey auth/`, `/plan groom 01K…`, `/plan rewrite repository layer`), skip the menu and go straight to that mode's flow.

If the argument is empty or doesn't match a mode, open the menu:

```
/plan — <Project Title>
What are we planning?
  intent    — describe an outcome; /plan decomposes into tasks
  survey    — point at a scope; /plan surveys and proposes tasks for what's worth doing
  groom     — shape below-bar tasks to the readiness bar
  rewrite   — plan a replacement of an existing chunk
```

No default. The user picks.

### 3. Mode-specific flow

Groom is the odd one out — it writes directly (the user's "groom these" IS the confirm). Intent, Survey, and Rewrite all go through scope-mode planner → synthesize → confirm → write.

#### 3a. Groom mode

Input: one or more below-bar task IDs, or a project-wide groom request.

1. Resolve the target tasks. Single ID: that task. `/plan groom` with no ID: pull below-bar tasks for the project and show the user the list, let them pick which to groom.
2. Dispatch `project-planner` shape 1 (`{ task_id }`) for each selected task. Parallel when multiple.
3. Planner writes updated tasks directly. If planner escalates to a design ticket (input too fuzzy for implementation), that write also goes through planner.
4. Report back: "Groomed N tasks. K escalated to design. Run `/work` when ready."

No synthesis step. Groom-mode writes happen at planner dispatch time because the user already confirmed at menu entry.

#### 3b. Intent mode

Input: a description of the outcome ("add MFA", "improve search performance", "instrument the auth flow").

1. **Clarify intent if needed.** If the description is two words or a hand-wave, ask one question to anchor it. Skip when the intent is specific enough.
2. **Single-shot planner.** Dispatch `project-planner` shape 4 (scope-mode) with `{ scope: <inferred from intent>, project_id, intent }`. Planner surveys the relevant code, proposes tasks, and returns typed TODOs.
3. **Handle the planner's return.** Three buckets:
   - `task_proposals` — the tasks planner could shape cleanly.
   - `split_todos` — sub-scopes planner decided were too big for one pass.
   - `decision_todos` — questions planner couldn't resolve without a user call.
4. **Fan out on split TODOs (one level).** Show the user the decomposition first:

```
Planner proposes <N> tasks and flagged <M> sub-scopes for deeper planning:
  1. <sub_scope A> — <reason>
  2. <sub_scope B> — <reason>

Fan out parallel planners on these? (y / skip / edit)
```

On `y`, dispatch one planner per sub-scope in parallel (single message, multiple `Agent` calls). On `skip`, the sub-scopes become hints in the final report ("consider running `/plan survey <sub_scope>` later"). On `edit`, user adjusts the decomposition before fan-out.

**No recursive fan-out.** If a second-level planner returns more split_todos, they surface as hints in the final report, not as further fan-out. A scope that needs three levels of splitting was too big to start.

5. **Handle decision TODOs.** Default: file as design tickets via `project-planner` (shape 3, freeform prompt that describes the fork). Offer a per-TODO override:

```
Planner flagged <K> decisions that need your call:
  1. <question> — forks: <A | B | C>
  2. <question> — forks: <A | B>

Handle as:
  file design — file all as design tickets (default; /design picks them up)
  ask inline  — answer each one here and fold into task proposals
  mix         — pick per question
```

6. **Synthesize and confirm.** See step 4 below.

#### 3c. Survey mode

Input: a scope descriptor (directory, file list, module name, or freeform scope like "auth surface").

Same flow as Intent mode from step 2 onward. The only difference: no `intent` passed to the planner — the scope speaks for itself. Planner returns proposals for what's worth doing in the surveyed area.

Use when the user is asking "what should we be doing here?" rather than "here's what I want done."

#### 3d. Rewrite mode

Absorbs the old `/rewrite` skill. Input: a description of what to replace ("rewrite the repository layer", "redo the component system").

1. **Scope interview.** A tight set of questions the description doesn't already answer:
   - What's wrong with the current version? (drives requirements)
   - What's the boundary? Which files, modules, surfaces?
   - What stays the same? (public API, migration path, non-negotiables)
   - What's the target shape? (even fuzzy is OK)

   If the description answers most of these, don't re-ask. If the target is under a single file, point the user at `/capture` instead.

2. **KB pull.** Search for conventions, prior decisions, and architecture docs that constrain the rewrite. Read the substance. Surface the ones that matter to the user before planning.

3. **Optional hunter dispatch.** When the rewrite touches a non-trivial slice and the user hasn't named the structure clearly, dispatch `bug-hunter` with a targeted concern: "Survey the current <target>. Identify structure, failure modes aligned with <stated problems>, coupling, tests." Single dispatch, not a loop. Skip when the user has already described the structure or the scope is self-contained.

4. **Optional exa research.** For target shapes with external analogues (repository layer, auth flow, queue contract), pull 2–4 best-practice sources. Summarize substance, not links. Skip when tightly project-specific.

5. **Consolidate the shape with the user.** With KB + hunter + exa in hand, iterate on the target shape: what the new version looks like, the migration path, what's decided vs. punted, what's out of scope. Push back on hand-waves. Iterate until the user signals the shape is set.

6. **Multi-target check.** If the rewrite resolved to more than one distinct target, surface the split and let the user pick `split` (separate `/plan rewrite` invocations), `narrow` (keep the primary, file others as follow-up), or `proceed` (emit tasks for all).

7. **Dispatch scope-mode planner with the consolidated shape as intent.** Same as Intent mode from step 2: planner returns proposals + TODOs, fan out on split_todos, handle decision_todos, synthesize, confirm.

### 4. Synthesize and confirm

After all planner dispatches return (including parallel fan-out), assemble the batch:

- Merge `task_proposals` from every planner into one list.
- Wire cross-batch dependencies — each planner named `dependencies_local` within its own output; `/plan` stitches edges between batches when the migration path or scope boundaries imply ordering.
- Resolved decision TODOs (inline-answered) become additional implementation proposals. Filed ones become design-task proposals.
- Accumulate unhandled split_todos as "consider `/plan survey <sub_scope>`" hints.

Show the user the full proposal:

```
/plan — <Project Title>, <mode>
Proposed: <N> implementation tasks · <M> design tasks

Implementation:
  "Update auth middleware for MFA"       — feature, medium, med, dep on: (none)
  "Add TOTP provider"                    — feature, medium, med, dep on: "Update auth middleware for MFA"
  "Add recovery codes table"             — feature, low, high
  ...

Design (user decisions):
  "Decide: MFA enforcement policy"       — 2 forks: opt-in vs mandatory
  "Decide: recovery code format"         — 3 forks: mnemonic / hex / base32
  ...

Hints (deferred sub-scopes — run /plan survey <...> later):
  auth/admin/ — planner flagged this as a separate surface
  auth/sso/   — not touched this pass

Apply? (y / edit / drop <n> / cancel)
```

- `y` — write everything as shown.
- `edit` — inline edits to titles, categories, or dependencies before writing.
- `drop <n>` — remove proposal n from the batch.
- `cancel` — write nothing, exit.

### 5. Write

On `y`:

1. `create_task` for each proposal in the batch. Capture returned ULIDs.
2. Wire cross-batch `blocks` / `blocked_by` edges using the captured ULIDs.
3. Report:

```
/plan complete — <Project Title>, <mode>
Filed: <N> implementation · <M> design tasks

Implementation:
  01KX… "Update auth middleware for MFA"
  01KY… "Add TOTP provider"
  ...

Design (resolve first via /design):
  01KZ… "Decide: MFA enforcement policy"
  ...

Next: /design the design tickets, then /work the implementation set.
```

## Output

- A batch of tasks on the backlog — a mix of implementation tickets (at the readiness bar) and design tickets (for punted forks).
- No source code. No KB documents. No git operations.
- A structured report listing what was filed, what was deferred, and the suggested order.

## Principles

- **One skill, one job: turn intent into a backlog.** `/plan` does not execute, does not write KB docs, does not commit. Execution is `/work`. KB authorship is `/design`. Commits are the user's.
- **Planner surveys; `/plan` synthesizes.** The codebase reading lives in the subagent, not the skill. The skill owns the menu, the confirm, and the fan-out decisions.
- **Show the decomposition before fan-out.** The cheapest place to catch a bad scope split is at the split_todos boundary, before parallel planners burn context on the wrong shape.
- **Confirm before writes.** Scope-mode proposals are data until the user says `y`. This is the rule that breaks the infinite-loop failure mode the old `/work`-with-grooming had.
- **One level of fan-out.** A scope that needs recursive splitting was too big to plan in one session — surface the deeper sub-scopes as hints and let the user decide whether to re-invoke.
- **Decisions file as design tickets by default.** When planner hits a fork, the default is "file it and move on." Inline answers are opt-in. Design is `/design`'s conversation to host, not `/plan`'s.
- **Groom writes directly.** The menu choice was the confirm. No preview step for single-task grooms.

## Constraints

- **No writes below confident project inference.** Ask or stop.
- **No source code, ever.** `/plan` produces tasks; `/work` + `developer` produce code.
- **No KB writes.** Design tickets are filed; `/design` writes the docs.
- **No auto-invocation of `/work` or `/design`.** The user picks timing.
- **No recursive fan-out.** Parallel planners on split_todos runs one level deep; further splits surface as hints.
- **No silent scope changes.** If the user's intent resolved to a broader or narrower scope than they asked for, surface it in the confirm block.
- **No filing below the readiness bar.** Every implementation proposal meets the bar. Anything that can't → design ticket.
- **No committing or pushing.** Ever.
