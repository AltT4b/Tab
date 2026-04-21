---
name: ship
description: Pre-push sweep — synthesize a changelog from git commits since the last version tag, surface likely-stale docs (README, CLAUDE.md) for confirmation, apply a version bump, and update the changelog if one exists. Does not push, does not create a changelog from scratch. Use when work is committed and the branch is ready to go out. Triggers on `/ship` and phrases like "cut a version", "get this ready to push", "run the ship sweep".
argument-hint: "[--patch | --minor | --major] [--dry-run]"
---

A pre-push checkpoint. `/ship` reads the commits since the last version tag, drafts a changelog entry from them, surfaces documentation that looks stale against the diff, and — on user confirmation — applies a version bump plus the changelog update. It never pushes. The user ships.

## Trigger

**When to activate:**
- User invokes `/ship`, optionally with a bump hint (`--patch`, `--minor`, `--major`).
- User says "cut a version", "get this ready to push", "run the ship sweep", "prep for release".
- Work just completed via `/work` and the user wants to package it.

**When NOT to activate:**
- No commits since the last version tag — there's nothing to ship. Say so and stop.
- User is mid-work and hasn't committed — the sweep needs commits to read. Point them back to `/work` or direct commits.
- User wants to push — this skill stops at the commit. Pushing is the user's call.

## Requires

- **Tool:** `Bash` — for `git log`, `git diff`, tag queries, and applying the version bump commit.
- **Tool:** `Read`, `Edit`, `Grep`, `Glob` — for finding and touching README, CHANGELOG, and nested CLAUDE.md files.
- **Environment:** a git repo with at least one commit since the last version tag (or since initial commit if no tag exists).

## Behavior

The skill flows in five phases: **Scan** (find the commit range), **Draft** (synthesize the changelog entry), **Sweep** (surface stale docs), **Confirm** (one approval gate), **Apply** (write the bump + changelog + doc updates in a single commit).

### 1. Scan — determine the commit range

1. Find the last version tag. Priority: nearest tag on current branch matching a semver-ish pattern (`v1.2.3`, `1.2.3`, or plugin-prefixed like `tab-for-projects-2.3.0`). Fall back to initial commit if no tag exists.
2. Read commits since the tag with `git log <tag>..HEAD --oneline --no-merges`.
3. If the range is empty, say so and stop. Nothing to ship.
4. Read the full diff with `git diff <tag>..HEAD --stat` to get the file list for the doc sweep.

### 2. Draft — synthesize the changelog entry

Group commits by conventional-commit type, mapping to Keep-a-Changelog sections:

- `feat:` / `add:` → **Added**
- `fix:` / `bugfix:` → **Fixed**
- `change:` / `refactor:` / `chore:` / anything else substantive → **Changed**
- `remove:` / `breaking:` / anything marking removal → **Removed**

For commits that don't follow conventional style, infer the section from the commit subject. When in doubt, ask — don't guess across sections.

Produce **bullets**, not prose. Each bullet:

- Describes the user-visible change, not the implementation detail.
- Quotes the file or feature area if it matters.
- Stays to one sentence.

Example (drawn from commit history, not fabricated):

```
### Added
- `/rewrite` skill — freeform "rewrite the repository layer" → tasks on the backlog.

### Changed
- `/work` no longer routes design-category tasks; they surface to the user for `/design`.

### Fixed
- `/search` ladder no longer stops on a weak single hit when rung 3 would return a clean five.
```

### 3. Sweep — surface likely-stale docs

From the diff's file list, identify docs that plausibly need updating:

- **README.md** (at any depth) is stale if: user-facing features were added/removed, CLI invocations changed, installation steps changed, or the file is named in the diff. Scan commit subjects for these signals.
- **CLAUDE.md** (at any depth) is stale if: a new module was added, an agent/skill was added or renamed, conventions changed, or the structure-tree portion doesn't match the filesystem.
- **CHANGELOG.md** is handled separately (see step 5).

For each doc the sweep flags, Read it and propose a targeted edit — not a rewrite. The user confirms, edits, or skips per-doc.

If no docs look stale, say so — "No README / CLAUDE.md drift detected." The sweep is allowed to find nothing.

### 4. Confirm — one approval gate

Present the complete package before writing:

```
/ship — <project or package name>
Commits since <tag>: <N> (range: <tag>..HEAD)

Proposed bump: <patch | minor | major>   (inferred from changelog — override with --patch/--minor/--major)
New version:   <new-version>

Changelog entry (<path>):
  ### Added
    - …
  ### Changed
    - …
  ### Fixed
    - …

Doc updates:
  README.md          — <one-line change description>
  tab/CLAUDE.md      — <one-line change description>
  (or "no doc drift detected")

Apply? (y / edit changelog / edit docs / skip docs / cancel)
```

Responses:
- `y` — proceed with everything as shown.
- `edit changelog` — inline edits to the changelog draft before proceeding.
- `edit docs` — inline edits to the proposed doc changes.
- `skip docs` — apply version + changelog only; leave docs untouched.
- `cancel` — write nothing, exit.

### 5. Apply — write the bump, the changelog, and the docs

On confirm:

1. **Version bump.** Update the version file(s) the project uses. For this marketplace, that means **both** `.claude-plugin/marketplace.json` (the relevant plugin entry) **and** `<plugin>/.claude-plugin/plugin.json`. For other projects, update whatever file holds the version (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.). Bump all of them in lockstep.
2. **Changelog update.** If `CHANGELOG.md` exists at the project / package root, prepend a new `## [<new-version>] — <YYYY-MM-DD>` section with the drafted entry. If no `CHANGELOG.md` exists, **do not create one** — state that it was skipped and move on.
3. **Doc updates.** Apply the confirmed doc edits (or skip if the user said `skip docs`).
4. **Commit.** One commit containing the version bump, the changelog entry, and the doc edits. Conventional style, e.g.: `chore: release <new-version>`. Body lists the included sections.
5. **Report.** Print the new version, the commit hash, and a one-line "ready to push" acknowledgement. The skill does not push.

### 6. Dry run

`--dry-run` stops before step 5. Prints the plan and the diff of what would be written, does not commit.

## Output

- One commit on the current branch: version bump + changelog entry + any confirmed doc edits.
- No push. No tag (tagging is the user's call unless project conventions require otherwise — if they do, name it in the report as the next step).
- A short report: new version, commit hash, any docs that were skipped.

## Principles

- **One approval gate.** Everything the sweep found surfaces in a single confirm block. No staccato "can I edit this doc?" interruptions.
- **Commits are the truth.** The changelog is synthesized from `git log`, not from memory. If the commits are sparse or cryptic, the entry will show it — that's a signal to the user, not a reason to embellish.
- **Never create a changelog that doesn't exist.** If the project opted out of changelogs, `/ship` doesn't force one.
- **Doc drift detection is heuristic.** The sweep flags candidates; the user approves. A missed doc is the user's call, not a silent failure.
- **The user ships.** This skill stops at a clean commit. Pushing, tagging, merging — user's job.

## Constraints

- **No push. No force-push.** Ever.
- **No tag creation unless the project's convention requires it** (and even then, only on explicit user confirm).
- **No changelog creation from scratch.** If `CHANGELOG.md` doesn't exist, skip the changelog step.
- **No silent doc edits.** Every doc change passes through the confirm block.
- **Version sync is atomic.** If a project has multiple files holding the version (e.g., marketplace + plugin manifests), bump all or none. A mismatch is worse than not shipping.
- **Stop if the working tree is dirty.** Uncommitted changes mean the sweep can't produce a clean result. Report the dirty state and stop.
- **No commit rewriting.** `/ship` adds a single new commit. It does not amend, squash, or rebase existing history.
