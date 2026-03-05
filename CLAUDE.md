# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Tab is a Claude Code plugin that implements a personal AI assistant entirely in markdown. There is no compiled code, no runtime, no package dependencies, no build system, no tests, and no linting. All behavior is defined through text files that Claude Code reads and interprets.

## Repository Structure

```
Tab/
├── .claude-plugin/
│   └── plugin.json                  # Plugin manifest (entry point)
├── agents/
│   ├── base/
│   │   ├── AGENT.md                 # Tab's core persona (always loaded)
│   │   └── skills/
│   │       ├── draw-dino/SKILL.md   # ASCII art dinosaur skill
│   │       └── writing/SKILL.md     # General-purpose writing skill
│   ├── advisor/                     # Advisory/critique variant
│   │   └── AGENT.md                 # Additions-only (extends base)
│   └── researcher/                  # Research-focused variant
│       ├── AGENT.md                 # Additions-only (extends base)
│       └── skills/
│           └── deep-research/SKILL.md  # Structured research skill
└── skills/
    └── summon-tab/SKILL.md          # Shared skill: agent dispatcher
```

## Architecture

**Plugin manifest** (`.claude-plugin/plugin.json`): Declares the plugin name, version, and the `skills` path (`./skills/`) that registers shared skills with Claude Code.

**Agents** (`agents/<name>/AGENT.md`): Define an AI persona. The base agent (`agents/base/`) uses YAML frontmatter (`name`, `description`) and `## Base *` sections (`Base Identity`, `Base Rules`, `Base Skills`, `Base Output`). These sections define Tab's core persona and can be extended by variants but never overwritten. Variant agents declare `extends: agents/base/AGENT.md` in frontmatter and use `## Additional *` sections (`Additional Identity`, `Additional Rules`, `Additional Skills`, `Additional Output`) that append to the corresponding base sections.

**Skills** (`skills/<name>/SKILL.md` or `agents/<name>/skills/<name>/SKILL.md`): Instruction sets with YAML frontmatter whose `description` field doubles as the invocation trigger. Shared skills live under the top-level `skills/` directory and are registered via the plugin manifest. Agent-local skills live under an agent's `skills/` directory and are scoped to that agent.

## How Tab Gets Activated

The `summon-tab` shared skill triggers on phrases like "Hey Tab", "@Tab", etc. It embeds `agents/base/AGENT.md` via an `@` file reference (always loaded) and contains a hardcoded variant table mapping intent patterns to variant agent paths. When a variant matches, it loads the variant's `AGENT.md` via Read and merges its `Additional *` sections additively with the base. Claude then adopts the merged persona for the rest of the conversation. New variant agents must be manually added to the table in `skills/summon-tab/SKILL.md`.

## Skill Frontmatter

Skills use these optional frontmatter fields beyond `name` and `description`:

| Field | Purpose | Example |
|-------|---------|---------|
| `argument-hint` | Autocomplete hint shown in `/` menu | `"[topic]"`, `"[format] [topic]"` |
| `$ARGUMENTS` | In skill body, replaced with user's slash command arguments | `/deep-research quantum computing` |

## MCP Servers

No MCP servers are currently bundled. The researcher variant's deep-research skill can use any MCP search tools available in the user's environment (e.g., Exa), but none are shipped with the plugin.

## Conventions

- **Naming**: lowercase, hyphenated for all component directories (e.g., `draw-dino`, `summon-tab`)
- **Frontmatter**: SKILL.md files use YAML frontmatter with `name`, `description`, and optionally `argument-hint`. AGENT.md files use `name` and `description` at minimum.
- **Skill triggers**: the `description` frontmatter field in SKILL.md doubles as the trigger condition
- **Variant agents**: variant AGENT.md files declare `extends: agents/base/AGENT.md` in frontmatter and use only "Additional X" sections (additive, never replace)
- **Git commits**: conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)

## Upgrade Plan

Active implementation plan lives at `.tab/upgrades-for-tab/p3-p7-implementation-plan.md`. Phases 3-5 (variant agents, hooks, auto-activation) are pending.
