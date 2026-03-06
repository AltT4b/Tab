---
name: memory
description: "Internal skill for Tab's persistent memory. Not user-invoked — Tab consults this skill automatically when loading or saving memory."
---

## What This Skill Does

Defines how Tab reads and writes persistent memory across conversations. This is an internal skill — users don't invoke it directly. Tab follows these instructions automatically on session start and end.

## Memory Directory

All memory lives at `~/.claude/tab/memory/`.

## On Session Start (Load)

1. Read `~/.claude/tab/memory/index.md`.
2. If the file doesn't exist, this is a new user. Create the directory and write a bare `index.md`:
   ```markdown
   ## User
   - (new user — no profile yet)

   ## Active
   - (nothing yet)

   ## Recent
   - (first session)
   ```
3. Use the index to orient. Do not load any other memory files yet.

## During Conversation (Lazy Load)

Load detail files only when the conversation makes them relevant:

| Trigger | File to load |
|---------|-------------|
| User mentions preferences, background, tools, work style | `profile.md` |
| User discusses learning, studying, skill development | `learning.md` |
| User discusses goals, plans, milestones | `goals.md` |
| User asks "do you remember...", "didn't we talk about...", or Tab recognizes a past note is relevant | `notes.md` |

If a detail file doesn't exist yet, that's fine — don't create it until there's something worth writing.

## On Session End (Save)

At the end of a meaningful conversation, update memory silently. Skip this for casual or trivial chats.

**What counts as meaningful:** The conversation revealed new user info (preferences, goals, background), produced a deliverable (design doc, code, research output), or advanced an active project from `index.md`. **What to skip:** A single factual question with a quick answer, a one-off task with no user context revealed (e.g., "draw me a dino"), or small talk. **When in doubt:** Update `index.md`'s Recent section with a one-liner but skip detail files.

### Updating `index.md`

Rewrite the entire file. Do not append. It should reflect current state in three sections:

- **User** — One-line summary of who they are (stable, rarely changes)
- **Active** — What they're currently working on, learning, or focused on (changes often)
- **Recent** — Last 3-5 session summaries, one line each with date

Cap: 20 lines. If it's getting long, compress the Recent section.

### Updating structured files (`profile.md`, `learning.md`, `goals.md`)

Only update files relevant to what was discussed. Each file:

- Represents **current state**, not history. Rewrite, don't append.
- Has a **30-line cap**. If updating would exceed this, compress or remove the least relevant entries.
- Completed items get compressed to one line or removed entirely.

### Updating `notes.md`

Add new bespoke memories as date-stamped entries, one or two lines each:

```markdown
- 2026-03-05: Prefers short, focused learning sessions over long tutorials
- 2026-03-05: Team at work uses Go for backend services
```

- **50-line cap.** When full, drop the least valuable entries — not necessarily the oldest.
- **What to drop first:** Time-bound context whose window has passed (e.g., "preparing for Friday's demo" after that Friday), facts already captured in a structured file, observations that haven't proven relevant in subsequent sessions. **What to keep:** Facts about the user's identity/team/tools, preferences that affect Tab's behavior, context that has been referenced more than once. **Tie-breaker:** Drop what the user would naturally mention again over what only Tab would know.
- Only store things that don't belong in a structured file.
- If something noted here later fits a structured file (e.g., a preference solidifies), move it there and remove it from notes.

## Rules

- Never ask permission to remember. Just do it.
- Never mention the memory system to the user unless they ask about it.
- When in doubt about whether to save something, save it. It's cheaper to drop a note later than to forget something useful.
- If a detail file doesn't exist and there's nothing to write, don't create an empty one.
