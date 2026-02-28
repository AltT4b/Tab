# Flatten Command Structure

## Problem

Commands at `commands/<name>/<name>.md` register with Claude Code as `tab:<name>:<name>` — the directory and file name both contribute a namespace segment, doubling the name.

## Solution

Move command files to `commands/<name>.md` (flat files, no subdirectories). This produces clean `tab:<name>` registration.

## Changes

1. **Move files** — relocate each command from its subdirectory to a flat file:
   - `commands/add-agent/add-agent.md` -> `commands/add-agent.md`
   - `commands/add-command/add-command.md` -> `commands/add-command.md`
   - `commands/add-rule/add-rule.md` -> `commands/add-rule.md`
   - `commands/add-skill/add-skill.md` -> `commands/add-skill.md`
   - Delete the now-empty subdirectories

2. **Update CLAUDE.md** — change command convention from `commands/<name>/<name>.md` to `commands/<name>.md` in all references (repo structure, conventions, placement notes).

3. **Update `add-component` skill** — update command placement paths:
   - Shared: `commands/<name>/<name>.md` -> `commands/<name>.md`
   - Agent-local: `agents/<agent>/commands/<name>/<name>.md` -> `agents/<agent>/commands/<name>.md`

4. **No changes needed to `plugin.json`** — it already points to `./commands/` and Claude Code will discover flat `.md` files there.
