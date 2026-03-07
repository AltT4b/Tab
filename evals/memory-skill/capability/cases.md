# Capability Cases — Memory Skill

Cases that track quality improvement over time. Lower pass rates expected initially. Run on a regular cadence.

Score all cases against `rubric.md` for the full 11-dimension evaluation. Case-specific observations are listed below.

---

## Continuity & Greeting

### MC-C01: Natural Continuity Greeting

- **Memory state:** Seeded
- **Prompt:** "Hey Tab"
- **Why it's here:** The first thing a returning user sees. Tab should reference the last session naturally — a quick continuity beat, not a status dump.
- **What to observe:**
  - [ ] Tab references the most recent session from the Recent section ("Last time we were looking at rate limiting" or similar)
  - [ ] Reference is brief — one sentence, woven into the greeting
  - [ ] Doesn't read back the entire index like a report
  - [ ] Doesn't recap all active projects — just the most recent touchpoint
  - [ ] Tone matches Tab's persona (warm, quick, not formal)

---

## Lazy Load Accuracy

### MC-C02: Trigger Accuracy — Preferences Cue

- **Memory state:** Seeded (with `profile.md`)
- **Prompt:** "Hey Tab, I'm setting up a new dev machine. What were my editor and tooling preferences again?"
- **Why it's here:** User is asking about preferences — Tab should load `profile.md` (and only `profile.md`) to answer.
- **What to observe:**
  - [ ] Tab loads `profile.md` in response to the preferences cue
  - [ ] Tab does NOT load `goals.md`, `learning.md`, or `notes.md`
  - [ ] Answer draws on profile contents (editor, languages, etc.)
  - [ ] Tab responds naturally, not like it's reading a file aloud

---

### MC-C03: Trigger Accuracy — Learning Cue

- **Memory state:** Seeded (with `learning.md` containing study topics)
- **Context:** Extend seed with `learning.md`:
  ```markdown
  ## Current
  - Event sourcing — working through practical examples with the finance app
  - Go concurrency patterns — goroutines, channels, select

  ## Completed
  - REST API design basics
  ```
- **Prompt:** "Hey Tab, I want to pick up where I left off studying. What was I working on?"
- **Why it's here:** User is asking about learning — Tab should load `learning.md`.
- **What to observe:**
  - [ ] Tab loads `learning.md` in response to the learning cue
  - [ ] Tab does NOT load `profile.md` or `goals.md`
  - [ ] Answer references current learning topics from the file
  - [ ] Tab distinguishes current from completed — focuses on current

---

### MC-C04: Trigger Accuracy — No False Positive

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, explain how garbage collection works in Go."
- **Why it's here:** Technical question that mentions Go (which is in the profile) but doesn't warrant loading any detail files. Tab should answer from general knowledge.
- **What to observe:**
  - [ ] Tab does NOT load `profile.md` despite Go being mentioned
  - [ ] Tab does NOT load any detail files
  - [ ] Tab answers the technical question directly
  - [ ] No unnecessary memory file reads in the transcript

---

## Session-End Judgment

### MC-C05: Meaningful Conversation — Correct Save

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, I've decided to switch from REST to GraphQL for the finance app. The main reason is that the mobile client needs to fetch deeply nested transaction data and REST is getting chatty."
- **Context:** Have a 3-4 exchange conversation about the GraphQL decision. Then end the session.
- **Why it's here:** This reveals a meaningful project decision. Tab should update Active in `index.md` and possibly `notes.md`.
- **What to observe:**
  - [ ] `index.md` Active section updated to reflect GraphQL decision
  - [ ] Recent section has a new entry for this session
  - [ ] The *reason* for the switch is captured somewhere (not just "switched to GraphQL")
  - [ ] Old REST-related Active items are updated or removed, not left alongside GraphQL
  - [ ] Detail files only updated if relevant (notes.md might get the reasoning)

---

### MC-C06: Borderline Conversation — Good Judgment Call

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, quick question — should I use `sync.Mutex` or `sync.RWMutex` for a read-heavy cache in Go?"
- **Context:** Tab answers. User says "thanks, that's helpful." End session.
- **Why it's here:** This is a quick technical question — borderline between trivial and meaningful. The right call is either no save or a minimal Recent-only update.
- **What to observe:**
  - [ ] No changes to `profile.md`, `notes.md`, `goals.md`, or `learning.md`
  - [ ] `index.md` is either unchanged or has at most a one-line Recent entry
  - [ ] Tab does not over-index on the Go/cache detail as a project update

---

## Cross-File Organization

### MC-C07: Route to Correct File — Mixed Input

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, remember these things: I always use 2-space indentation, my current goal is to launch the finance app MVP by end of March, and my coworker Dave is great at system design so I should loop him in for the architecture review."
- **Why it's here:** Three items that belong in three different places: preference → `profile.md`, goal → `goals.md`, bespoke fact → `notes.md`.
- **What to observe:**
  - [ ] Indentation preference written to `profile.md` (or a structured file about preferences)
  - [ ] MVP goal written to `goals.md`
  - [ ] Dave note written to `notes.md`
  - [ ] No single file gets all three dumped into it
  - [ ] Each file remains within its cap after the writes

---

### MC-C08: Notes-to-Structured Migration

- **Memory state:** Seeded (with `notes.md` containing repeated preference-like entries)
- **Context:** Extend seed `notes.md` with:
  ```
  - 2026-02-28: Mentioned preferring dark mode in editors
  - 2026-03-01: Asked for dark theme in brainstorm output
  - 2026-03-03: Set terminal theme to Catppuccin (dark)
  ```
  No `profile.md` Preferences section mentions dark mode.
- **Prompt:** "Hey Tab, yeah I'm definitely a dark mode person across the board. Add that to whatever you know about me."
- **Why it's here:** A pattern in `notes.md` has solidified into a stable preference. Tab should move it to `profile.md` and clean up the redundant notes entries.
- **What to observe:**
  - [ ] Dark mode preference appears in `profile.md`
  - [ ] Redundant notes entries about dark mode are removed or consolidated from `notes.md`
  - [ ] `notes.md` doesn't retain all three historical entries alongside the profile entry
  - [ ] Both files remain within caps

---

## Recall Quality

### MC-C09: Recall — Specific Request

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, do you remember what database setup I use?"
- **Why it's here:** User is testing recall. Tab should load the relevant file and answer accurately from stored memory.
- **What to observe:**
  - [ ] Tab loads `notes.md` or `profile.md` (wherever database info lives)
  - [ ] Answer is accurate: PostgreSQL in production, SQLite for local dev
  - [ ] Tab presents the info naturally, not as a file readback
  - [ ] Tab doesn't fabricate additional database details not in memory

---

### MC-C10: Recall — Broad Request

- **Memory state:** Seeded (with all detail files populated)
- **Context:** Extend seed with `goals.md`:
  ```markdown
  ## Active
  - Launch finance app MVP by end of Q1 2026
  - Get comfortable with event sourcing patterns

  ## Completed
  - Set up Go project scaffolding
  ```
- **Prompt:** "Hey Tab, give me a quick summary of everything you know about me."
- **Why it's here:** Broad recall request. Tab should load all relevant files and synthesize a coherent summary — not just dump file contents.
- **What to observe:**
  - [ ] Tab loads multiple memory files to build the summary
  - [ ] Summary covers identity, active work, goals, preferences, and notable details
  - [ ] Information is synthesized into a natural narrative, not a file-by-file readback
  - [ ] Nothing fabricated — everything stated is grounded in stored memory
  - [ ] Summary is concise (not a wall of text)
