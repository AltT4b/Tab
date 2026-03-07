# Regression Cases — Memory Skill

Cases that MUST pass ~100% of the time. Guards against bloat and breaking changes. Run on every skill edit.

---

## Structural Cases

### MC-01: New User — Index Creation

- **Memory state:** Fresh
- **Prompt:** "Hey Tab"
- **Why it's here:** First-ever session must create a valid `index.md` with the correct 3-section structure.
- **What to observe:**
  - [ ] `~/.claude/tab/memory/index.md` is created
  - [ ] File contains `## User`, `## Active`, and `## Recent` sections
  - [ ] File is under 20 lines
  - [ ] Tab gives a brief intro (not a wall of text)

---

### MC-02: Index Cap — 20 Lines

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, I've been working on a bunch of new things. I started learning Rust, picked up a new side project building a game engine, joined a book club reading DDIA, started mentoring a junior dev, and I'm also prepping for a system design interview next month."
- **Context:** This prompt dumps a lot of new active items. After the conversation, end the session to trigger a save.
- **Why it's here:** `index.md` must stay at or under 20 lines even when there's a lot to track.
- **What to observe:**
  - [ ] `index.md` is at most 20 lines after session-end save
  - [ ] All three sections still present
  - [ ] Information is compressed, not truncated mid-sentence

---

### MC-03: Notes Cap — 50 Lines

- **Memory state:** Seeded (with a `notes.md` already at 45 lines — extend the seed with 41 additional filler entries)
- **Context:** Seed `notes.md` with 45 date-stamped entries. Then have a conversation that should add 10+ new notes.
- **Prompt:** "Hey Tab, remember all of these: I prefer dark mode everywhere, my cat's name is Pixel, I use Fish shell, my team standup is at 9:30am, I'm allergic to shellfish, my work laptop is a ThinkPad, I use Todoist for task management, my favorite font is JetBrains Mono, I deploy with GitHub Actions, and I prefer rebasing over merging."
- **Why it's here:** `notes.md` must not exceed 50 lines, even when flooded with new entries.
- **What to observe:**
  - [ ] `notes.md` is at most 50 lines after writes
  - [ ] Lower-value entries were dropped to make room
  - [ ] New entries are present (at least the durable ones like preferences)

---

### MC-04: Structured File Cap — 30 Lines

- **Memory state:** Seeded (with `profile.md` already at 25 lines — extend seed with additional sections)
- **Prompt:** "Hey Tab, some updates on me: I switched to Neovim, started using Nix for package management, moved to Arch Linux, picked up Zig as a hobby language, started contributing to an open source project called Turso, joined a remote-first company, my new team uses Grafana and Prometheus for observability, and we do trunk-based development."
- **Why it's here:** `profile.md` must stay at or under 30 lines.
- **What to observe:**
  - [ ] `profile.md` is at most 30 lines after save
  - [ ] Outdated entries compressed or removed to make room
  - [ ] New info integrated, not just appended

---

### MC-05: Recent Section — 3 to 5 Entries

- **Memory state:** Seeded (with exactly 5 Recent entries in `index.md`)
- **Context:** Extend the seed `index.md` Recent section to 5 entries. Run a meaningful conversation, then end session.
- **Prompt:** "Hey Tab, let's design an event sourcing system for the finance app. I want to use CQRS with separate read and write models."
- **Why it's here:** The Recent section must not grow beyond 5 entries — oldest should be dropped.
- **What to observe:**
  - [ ] Recent section has 3-5 entries after save
  - [ ] Newest session is present
  - [ ] Oldest entry was dropped to stay within cap

---

## Behavioral Cases

### MC-06: Immediate Save — "Remember This"

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, remember that my deploy target is always us-east-1."
- **Why it's here:** Explicit "remember" requests must write to disk immediately, not defer to session end.
- **What to observe:**
  - [ ] Entry appears in a memory file immediately after Tab responds (before session ends)
  - [ ] Written to `notes.md` or `profile.md` (either is acceptable)
  - [ ] Tab acknowledges naturally without explaining the memory system

---

### MC-07: Forget — Entry Removal

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, forget that I have a demo next Friday."
- **Why it's here:** Explicit "forget" requests must remove the entry from disk.
- **What to observe:**
  - [ ] The demo entry (`2026-03-02: Has a demo for the finance app next Friday`) is gone from `notes.md`
  - [ ] No trace of the entry (not commented out, not moved)
  - [ ] Other entries in `notes.md` are untouched

---

### MC-08: Lazy Load — No Eager File Loading

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, what's 2 + 2?"
- **Why it's here:** A trivial question should not cause Tab to read `profile.md`, `notes.md`, `goals.md`, or `learning.md`.
- **What to observe:**
  - [ ] Only `index.md` is read on session start
  - [ ] No other memory files are read during the conversation
  - [ ] Tab answers the question directly
  - [ ] (Verify via transcript — check for Read tool calls to memory files)

---

### MC-09: Invisibility — Don't Mention Memory

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, what's a good approach for database migrations in Go?"
- **Why it's here:** Tab must never mention its memory system, file structure, or storage mechanics unless the user asks.
- **What to observe:**
  - [ ] Tab answers the question helpfully
  - [ ] No mention of "memory", "saving", "notes", "index.md", or memory internals
  - [ ] No phrases like "I'll remember that" or "I have that in my notes" unless the user said something worth remembering

---

### MC-10: Trivial Skip — No Detail File Writes

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, what's the capital of France?"
- **Context:** End the session after Tab answers. Check filesystem.
- **Why it's here:** Trivial conversations must not trigger writes to detail files.
- **What to observe:**
  - [ ] `profile.md`, `notes.md`, `goals.md`, `learning.md` are unchanged (diff against seed)
  - [ ] `index.md` is either unchanged or has at most a minor Recent update
  - [ ] No new memory files created

---

### MC-11: Rewrite Not Append — Index Integrity

- **Memory state:** Seeded
- **Prompt:** "Hey Tab, I've decided to pivot the finance app to a budgeting focus instead of full personal finance. Also, I'm dropping event sourcing — going with plain CRUD."
- **Context:** This changes Active items. End the session to trigger save.
- **Why it's here:** Session-end saves must rewrite `index.md` entirely, not append new content below old content.
- **What to observe:**
  - [ ] `index.md` has exactly one `## User` section, one `## Active` section, one `## Recent` section
  - [ ] No duplicate section headers
  - [ ] Old Active items (event sourcing) are gone or updated, not duplicated
  - [ ] File is under 20 lines
