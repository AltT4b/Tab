# Skills

Skills are slash-command capabilities in the Claude Code plugin system. They are lighter than agents -- each skill is defined in a `SKILL.md` file and activated by typing its command in the chat. Skills give Tab (and its packages) specific, repeatable behaviors that users can invoke on demand.

A skill's `SKILL.md` declares its name, a description used for matching, and an argument hint showing what parameters it accepts. When a user types the corresponding slash command, Tab follows the instructions in that file.

---

## draw-dino

**Package:** tab
**Invocation:** `/draw-dino [species]`

Draws ASCII art dinosaurs. If the user names a specific species, Tab draws that one. If not, Tab picks one itself.

### How it works

1. Note the requested species or customization. If none is given, choose a classic dinosaur.
2. Freestyle draw the dinosaur as ASCII art inside a code block (so spacing is preserved).
3. After drawing, include a short fun fact related to the species.

### Customization

The species and style adapt to the user's request:

- **Cute / baby** -- draws a Baby Dino
- **Flying** -- draws a Pterodactyl
- **Scary / fierce** -- draws a T-Rex or Velociraptor
- **Big / gentle** -- draws a Brontosaurus

### Design principles

- Low stakes on purpose. The skill exists to be fun and lower the barrier to interaction.
- Always deliver. No clarifying questions, no refusals. Pick a dino and draw it.
- Personality over precision. A charming dinosaur with wobbly legs beats a technically perfect one with no character.

---

## listen

**Package:** tab
**Invocation:** `/listen [optional topic]`

A deliberate listening mode. Tab goes silent while the user thinks out loud -- dumping ideas, working through confusion, venting, brainstorming. When the user signals they are done, Tab synthesizes what it heard and hands back the structure that was hiding in the stream.

### Entering listen mode

When the user runs `/listen`:

1. Tab acknowledges with a single short line, something like: *"Listening. Say 'done' when you're ready for the synthesis."*
2. If a topic was passed (e.g. `/listen auth redesign`), Tab notes it internally as context but does not comment on it.
3. Tab goes silent.

### While listening

- **Say nothing.** No reactions, no clarifications, no encouragement, no emoji, no questions. Absolute silence.
- **Track everything.** Themes, contradictions, emotional weight, decisions made mid-thought, questions the user asked themselves, things they repeated (repetition signals importance).
- **Note what is unsaid.** If the user talks around something without naming it, that is signal too.

The only exception: if the user directly asks Tab a question (genuinely addressed to Tab, not rhetorical), Tab answers briefly and returns to silence.

### Ending listen mode

The user ends it by saying something like "done," "finished," "that's it," or any clear signal they are handing the floor back. If genuinely ambiguous whether they want synthesis or are just shifting topics, Tab asks.

### The synthesis

This is where Tab earns the silence. The synthesis covers:

1. **Structure.** Organize what the user said into coherent themes or threads. Show them the shape of their own thinking.
2. **Contradictions.** If the user said A early on and not-A later, name it without judgment.
3. **Energy.** What did they spend the most time on? What did they repeat? What made them change direction? That is where the real priority lives.
4. **Gaps.** If there is an obvious missing piece that their plan depends on, flag it.
5. **Mirror first, opinions second.** The synthesis reflects the user's thinking faithfully. If Tab has a strong reaction, it comes after the synthesis, clearly separated.

The synthesis is not a transcript, not a to-do list (unless the user was clearly listing tasks), and not advice. It is the user's thinking, organized.

After the synthesis, Tab returns to normal mode. The listening context stays available for the rest of the session.

---

## refinement

**Package:** tab-for-projects
**Invocation:** `/refinement [project-name]`

An interactive backlog refinement ceremony. Tab acts as a facilitator, walking through the project's active tasks with the user to make sure every task is understood, scoped, and actionable before implementation begins.

### Starting the session

1. **Resolve the project.** If the user provided an argument, match it against the project list. Otherwise follow the standard project resolution flow.
2. **Load project context.** Pull the goal, requirements, and design so Tab can evaluate whether tasks align with the project's intent.
3. **List the active backlog.** Filter for tasks with status `todo` or `in_progress`.
4. **Present the session overview:**
   - Project name and goal (one line)
   - Number of tasks in the backlog
   - A scannable list showing each task's title, effort, impact, category, and whether it has a plan
   - Call out tasks that look under-specified (no description, no plan, no effort estimate)

Then ask the user how they want to proceed -- walk through everything in order, focus on a specific group, or start with the tasks that need the most attention.

### Per-task refinement loop

For each task the user wants to refine:

1. **Present the task.** Show title, description, effort/impact estimates, category, group, plan, acceptance criteria, and what is missing or unclear.
2. **Discuss and research.** Work through the task with the user:
   - Clarify intent -- does the description capture *why* the task exists?
   - Validate scope -- is this one task or three?
   - Identify unknowns -- if the task touches unfamiliar parts of the codebase, spawn a background research agent to investigate rather than guessing.
   - Check assumptions -- verify that assumptions about the current state of the code are actually true.
   - Estimate effort -- discuss and calibrate using research findings.
   - Define "done" -- capture acceptance criteria if the user has opinions about what done looks like.
3. **Update the task.** Persist refined description, updated estimates, acceptance criteria, and notes immediately via the MCP. Updates happen as you go so nothing is lost if the session is interrupted.

### What a refined task looks like

- A description that someone with zero context would understand next week
- An effort estimate grounded in codebase research, not vibes
- Acceptance criteria that make "done" unambiguous (when the user has opinions)
- Enough understanding that planning would be straightforward
- No hidden unknowns -- uncertainty is flagged, not ignored

### Session flow

The session is conversational, not mechanical. Tab follows the user's energy:

- If they want to dive deep on one task, dive deep.
- If they want to skim and flag tasks that need work, skim.
- If they realize the backlog is missing something, help capture it.
- If they want to reorganize, regroup, or reprioritize, do it.

### Ending the session

When the user is done or the backlog is fully refined, Tab:

1. Summarizes what changed -- how many tasks were refined, what was added, what is still pending.
2. Calls out tasks that still need attention (under-specified, waiting on research, blocked).
3. Notes any background agents still running.
4. Optionally spawns a QA agent to check for missing work across the refined backlog, if the user wants it.
