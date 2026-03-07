# Trial Harness — Memory Skill

How to run memory skill evals with proper isolation, multi-trial support, and transcript capture.

## Prerequisites

- Clean working directory (no uncommitted changes that could interfere)
- Note which model is being used (include in results)

## Memory States

Memory evals require two distinct starting states. Each case specifies which one to use.

### Fresh State

No memory directory exists. Tests new-user flows.

```bash
rm -rf ~/.claude/tab/memory/
```

### Seeded State

Pre-populated memory files that simulate a returning user. Seed files are provided below.

```bash
rm -rf ~/.claude/tab/memory/
mkdir -p ~/.claude/tab/memory/
# Copy seed files (see Seed Data section)
```

## Seed Data

### `index.md` (seeded)

```markdown
## User
- Name: Alex
- Backend engineer, works mostly in Go and Python

## Active
- Building a REST API for a personal finance app
- Learning about event sourcing

## Recent
- 2026-03-04: Discussed API rate limiting strategies
- 2026-03-03: Brainstormed database schema for transactions
- 2026-03-01: Set up project scaffolding with Go modules
```

### `notes.md` (seeded)

```markdown
- 2026-03-04: Prefers token bucket over sliding window for rate limiting
- 2026-03-03: Team uses PostgreSQL in production, SQLite for local dev
- 2026-03-02: Has a demo for the finance app next Friday (2026-03-07)
- 2026-03-01: Likes short, focused sessions — prefers 30-min blocks
```

### `profile.md` (seeded)

```markdown
## Background
- Backend engineer, 4 years experience
- Primary languages: Go, Python
- Editor: VS Code with vim keybindings

## Preferences
- Concise answers, skip the basics
- Prefers examples over explanations
- Uses conventional commits
```

## Backup & Restore

Evals destroy real memory. Always back up before running and restore after.

### Before starting any eval session

```bash
# Back up real memory (skip if no memory exists yet)
if [[ -d ~/.claude/tab/memory ]]; then
  cp -r ~/.claude/tab/memory ~/.claude/tab/memory.bak
fi
```

### After finishing all eval trials

```bash
# Restore real memory
rm -rf ~/.claude/tab/memory
if [[ -d ~/.claude/tab/memory.bak ]]; then
  mv ~/.claude/tab/memory.bak ~/.claude/tab/memory
fi
```

## Pre-Trial Reset

Before each trial:

1. **Set memory state**: Fresh or seeded per the case spec
2. **Clear prior run artifacts**: `rm -rf .tab/`
3. **Start a fresh conversation**: New Claude Code session — no context carryover
4. **Summon Tab**: Send "Hey Tab" to load the persona
5. **Document memory state**: Record whether fresh or seeded in the results log

## Running a Trial

1. Set up memory state per the case spec
2. Copy the exact prompt from `cases.json` (not paraphrased)
3. Let Tab run to completion — do not interrupt
4. Run `./check-run.sh` for script assertions
5. Score model/manual assertions against `rubric.md`
6. Save the transcript to `.tab/eval-transcripts/memory-skill/<case-id>-trial-<n>.md`
7. Record scores in `results.md`

## Multi-Trial Protocol

Run each case **3 trials minimum**. For cases with inconsistent results, run up to 5.

| Metric | Formula | What It Tells You |
|--------|---------|-------------------|
| pass@k | Passed at least 1 of k trials | Can it do this at all? |
| pass^k | Passed all k trials | Can it do this reliably? |

## Post-Trial Checks

After each trial, before resetting state:

1. Snapshot `~/.claude/tab/memory/` contents for comparison
2. Run `wc -l` on all memory files to check caps
3. Diff seeded files against post-trial files to verify rewrite-not-append behavior