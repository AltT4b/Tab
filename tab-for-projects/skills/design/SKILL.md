---
name: design
description: Conversational KB authorship for project-shape work and design-category tasks. Either loads a design task and hosts the decision, or opens on a freeform topic for broader architectural / convention work. Dispatches `bug-hunter` for targeted codebase research, uses `exa` for web best-practices, and iterates with the user until the design is settled. Produces a KB document, links it to the project, and files follow-up tasks via `project-planner`. Triggers on `/design` and phrases like "let's design X", "work through this design task", "document our approach to Y".
argument-hint: "[<design-task-id> | <topic>] [--no-brief | --brief]"
---

The "design is a conversation, not an autopilot" skill. `/design` hosts the conversation where the user makes decisions only they can make, then captures the result in the KB. It is the sole entry point for KB authorship — decisions, architecture, conventions, references — and for project-shape work that doesn't fit a single backlog task.

Two entry modes:

- **Task mode** — `/design <task-id>` — load a design-category task from the backlog, host the conversation around its question, close when the user's happy.
- **Free mode** — `/design` or `/design <topic>` — open without a pre-filed task; shape the conversation around the topic, capture the KB doc, file follow-up tasks that emerge.

Both modes run the same four phases: **Load**, **Research** (KB + hunter + exa), **Converse**, **Capture**.

## Trigger

**When to activate:**
- User invokes `/design` with a task ID or a freeform topic.
- User says "let's design X", "work through the design task on Y", "document our approach to Z", "decide how we handle W", "figure out the shape of V".
- `/work`'s end-of-run report surfaced a design-category task in the "awaiting human" section and the user's ready to resolve it.
- `/plan`, `/debug`, or `project-planner` filed a design ticket and the user wants to open it.

**When NOT to activate:**
- User wants to file a new implementation task — use `/capture`.
- User wants to execute existing tasks — use `/work`.
- User wants a bug found and fixed — use `/debug`.
- User wants a rewrite planned — use `/plan rewrite` (which files design tickets of its own that `/design` later picks up).
- User wants to shape existing below-bar tasks — use `/plan groom`.

## Requires

- **MCP:** `tab-for-projects` — `get_task`, `get_document`, `get_project`, `get_project_context`, `list_documents`, `search_documents`, `create_document`, `update_document`, `update_project`, `update_task`, `create_task`.
- **MCP:** `exa` — web research for best-practices, common patterns, anti-patterns. Always available per project constraints.
- **Subagent:** `tab-for-projects:bug-hunter` — targeted codebase research when the conversation needs code anchors.
- **Subagent:** `tab-for-projects:project-planner` — files follow-up tasks at the readiness bar from the design's outcome.
- **Tools:** `Read`, `Grep`, `Glob` — for quick on-the-fly lookups when a full hunter survey would be overkill.

## Behavior

### 1. Load — resolve the entry mode

**Task mode** (argument is a ULID-shaped task ID):

1. `get_task(task_id)`. If missing, report and stop.
2. **Category check.** If the task isn't `category: design`, ask whether to proceed anyway (sometimes an implementation task reveals a design question worth capturing) or route elsewhere.
3. **Readiness check.** A design task is ready when its title is verb-led and concrete, its summary explains why + what, and its acceptance signal names a concrete output (typically a KB doc). If the task's below bar, surface the gap and ask the user to groom it inline or via `/plan groom <task-id>` before continuing.
4. **Status.** If `todo`, transition to `in_progress`. If already `in_progress`, assume resume. If `done`/`archived`, ask whether to open a new design task.
5. Read every KB doc the task references — those are the constraints the decision must respect.
6. Resolve the project: use the task's `project_id`; sanity-check against the cwd; ask if there's a mismatch.

**Free mode** (argument is a topic, or empty):

1. Resolve the project via the shared Project Inference convention (`.tab-project` → git remote → cwd → recent activity). Below confident, ask.
2. No task is loaded. The topic the user named drives the conversation from the start.
3. If during the conversation a filed task would help anchor the work (e.g., the design has a clear owner or a specific question), offer to file a design task via `/capture` + `project-planner` before continuing. Otherwise proceed without a task.

### 2. Research — KB + hunter + exa

Three inputs shape the conversation. Run them up front so the main thread isn't burning context mid-discussion.

**KB pass.**

- `list_documents` and `search_documents` for relevant conventions, prior decisions, architecture docs. Read the substance of anything that constrains the current design. Surface these to the user early — the user shouldn't have to discover a constraint halfway through weighing options.

**Hunter dispatch.**

- When the design touches a non-trivial slice of the codebase, dispatch `bug-hunter` with a tailored concern: "Survey the current shape of <target>. Identify entry points, boundaries, coupling, and any patterns the design will need to respect or change." Single dispatch; not a loop.
- Skip the hunter when: `--no-brief` was passed, the design is self-contained (greenfield or pure convention), the conversation already has the context, or the subagent isn't available.
- Force a hunter pass with `--brief` even on small designs.

**Exa research.**

- For any design whose shape has external analogues (a caching strategy, an auth flow, an API shape, a queue contract), pull 2–4 best-practice / anti-pattern sources via `exa`. Summarize the substance, not the links.
- Skip when the design is tightly project-specific. Say so.

Render everything found inline before the conversation proper starts. The user should see the full landscape before choosing a direction.

### 3. Converse — host the design

The skill's core. The conversation's shape varies — design decisions aren't one template. A few rules of thumb:

- **Start from the question, not a blank page.** In task mode, quote the task's summary back. In free mode, restate the user's topic and what surfaced in the research pass.
- **Surface constraints before options.** Prior decisions, conventions, and code realities come first. The user shouldn't discover mid-decision that an option is already ruled out.
- **Name options explicitly.** List the candidate shapes before arguing between them. A decision without named alternatives is a decision without evidence.
- **Push back on hand-waves.** "We'll figure that out later" is a fork, not an answer. Offer to file it as a follow-up design task and keep going on what's decidable now.
- **Stay out of the user's taste calls.** When the user has a preference grounded in priorities the skill can't see, capture it cleanly — don't litigate it.
- **Depth scales with stakes.** A small convention call is a short exchange; an architectural decision that constrains months of work earns a longer conversation.
- **Do not close until the user closes.** This is the core of /design's contract: the task stays `in_progress` (or the free-mode conversation stays open) until the user signals the decision is made. Explicit phrases — "okay let's go with X", "decision's made", "capture that", "that's it" — or a natural landing where the last N turns restated the same conclusion.

If the conversation sprawls into multiple decisions, offer to close the current one and open another `/design` pass rather than stuffing everything into one doc.

### 4. Capture — propose the doc, confirm, write, file follow-ups

Once the decision is in hand, synthesize the KB doc and produce the follow-up tickets.

**Decide the doc type.**

- **Decision** — a single resolved trade-off. Folder: `decisions` (or `architecture` if architectural). Tags: `decision`, plus domain if obvious.
- **Architecture** — a shape multiple decisions or features will reference. Folder: `architecture`. Tags: `architecture`, `reference`.
- **Convention** — a rule the project applies consistently from here on. Folder: `conventions`. Tags: `conventions`, `reference`.

Default to matching what the project already uses (`list_documents({ project_id })` to see folders and tags in play). Introduce new folders sparingly.

**Build the doc.**

- **Title** — `Decision: <phrase>`, `Architecture: <phrase>`, `Conventions: <phrase>`. Match the pattern for the type.
- **Summary** — 1–3 sentences, max 500 chars. What this locks down and who it's for. Load-bearing — `/search` indexes on this.
- **Content** — structured markdown. Decision docs typically: **Decision** (the resolved answer), **Why** (reasoning + alternatives considered), **Consequences** (what this locks in, known follow-ups), **Related** (linked tasks, sibling docs, group keys). Architecture and convention docs: match neighboring docs in the same folder.
- **Folder / Tags** — from the type classification.

**Propose before writing.**

```
Save as: "Decision: <phrase>"
  Folder: decisions
  Tags: decision, architecture
  Attach to: <Project Title> (<project-id-prefix…>)
  Close task: 01K…  (task mode only — "y" closes the originating task)
  Summary: [1–3 sentences]

Content preview (first ~20 lines):
  [render first chunk]

Follow-up tasks (via project-planner):
  - implementation: <N> tickets  (shape clear from the decision)
  - design: <M> tickets           (forks the user punted)

Save? (y / edit / skip attach / skip task-close / skip follow-ups)
```

Accept inline edits on any field. `skip attach` keeps the doc unlinked (rare — design docs are almost always project-scoped). `skip task-close` writes the doc but leaves the task in `in_progress` (useful when the decision landed but more work under the same task is pending). `skip follow-ups` suppresses the planner dispatch (the user will file tasks manually later).

**On confirm:**

1. `create_document({ title, summary, content, folder, tags })`. Capture the returned doc ID.
2. `update_project({ id: project_id, documents: { <doc_id>: true } })` — unless the user said `skip attach`.
3. **Follow-up tasks.** Unless the user said `skip follow-ups`, dispatch `project-planner` with a freeform prompt (shape 3) containing the decision, the inlined doc substance, and the forks the user punted. Planner returns with implementation tickets for decided pieces and design tickets for punted forks. Surface the emitted task IDs in the close report.
4. **Task close (task mode only).** If the user confirmed, `update_task({ id: task_id, status: "done" })` with a note referencing the doc ID.

### 5. Close

One-line acknowledgement plus the emitted follow-ups.

```
Saved <doc_id> "<Title>" in <folder>, linked to <Project>. Task 01K… marked done.
Follow-ups: 3 implementation tickets, 1 design ticket (see /work, /design).
```

Or, when attachment, task-close, or follow-ups were skipped:

```
Saved <doc_id> "<Title>" in <folder>. Task left in_progress — close when ready.
```

## Output

- A KB document, linked to the project.
- (Task mode) Optionally, the originating task transitioned to `done` with an implementation note referencing the doc.
- (Both modes) Follow-up tasks filed by `project-planner` — a mix of implementation tickets (for decided pieces) and design tickets (for punted forks) — unless the user opted out.
- No source code. No changelog edits. No docs outside the KB.

## Principles

- **Design decisions are the user's to make.** The skill loads context, runs research, hosts the conversation, captures the result. It does not pick a winner between real alternatives.
- **Research before the conversation, not during.** The hunter and exa passes exist so the main thread isn't burning context on surveys mid-conversation. Run them up front, or skip cleanly.
- **Capture at the moment of crystallization.** A decision that sits in a thread for a week rots. The skill's value is moving the decision into the KB the same turn it lands.
- **Match the KB, don't reinvent it.** Existing folders, tags, and title patterns are the right defaults.
- **Do not close until the user closes.** The task stays `in_progress` as long as the conversation needs it. No rushing to `done` on the first plausible stopping point.
- **Forks become design tickets, not hope.** If the user punts on a fork, planner files a design ticket for it; the doc reflects what was decided, not what was wished.

## Constraints

- **KB authorship lives here.** No other skill or agent writes KB docs. `/design` is the single entry point.
- **No writes before confirm.** The doc, the project link, the task-close, and the follow-up dispatch all pass through the single confirm block.
- **No source code.** Ever. If the decision implies code changes, they become follow-up implementation tickets via `project-planner`.
- **No autonomous fork resolution.** Punted forks file as design tickets.
- **Readiness bar applies in task mode.** A below-bar design task gets groomed (via `/plan groom`) before the conversation starts.
- **Hunter dispatches are single-shot.** One `task_id` or one tailored concern in, one brief out. The skill does not loop on the hunter mid-conversation.
- **Exa is a research tool, not a source of truth.** Summarize the substance; don't treat web snippets as authoritative without checking against the project's own context.
