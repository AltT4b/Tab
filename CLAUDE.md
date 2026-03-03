# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Tab is a Claude Code plugin that implements a personal AI assistant entirely in markdown. There is no compiled code, no runtime, no package dependencies, no build system, no tests, and no linting. All behavior is defined through text files that Claude Code reads and interprets.

## Repository Structure

```
Tab/
├── .claude-plugin/plugin.json       # Plugin manifest (entry point)
├── agents/
│   ├── base/
│   │   ├── AGENT.md                 # Tab's core persona (always loaded)
│   │   └── skills/
│   │       ├── draw-dino/SKILL.md   # Agent-local skill
│   │       └── writing/SKILL.md     # General-purpose writing skill
│   └── researcher/                  # Research-focused variant
│       ├── AGENT.md                 # Additions-only (extends base)
│       └── skills/
│           └── deep-research/SKILL.md
└── skills/
    └── summon-tab/SKILL.md          # Shared skill: agent dispatcher
```

## Architecture

**Plugin manifest** (`.claude-plugin/plugin.json`): Declares the plugin name, version, and the `skills` path (`./skills/`) that registers shared skills with Claude Code.

**Agents** (`agents/<name>/AGENT.md`): Define an AI persona. The base agent (`agents/base/`) uses YAML frontmatter (`name`, `description`) and markdown body sections: `## Identity`, `## Base Rules`, `## Output`. Variant agents add `extends: agents/base/AGENT.md` to frontmatter and use additions-only sections (`## Additional Identity`, `## Additional Rules`, `## Additional Skills`, `## Output`) that layer on top of the base.

**Shared skills** (`skills/<name>/SKILL.md`): Instruction sets registered with Claude Code via the plugin manifest. The frontmatter `description` field serves as the invocation trigger — Claude Code reads it to decide when to activate the skill.

**Agent-local skills** (`agents/<name>/skills/<name>/SKILL.md`): Skills scoped to a specific agent, referenced from that agent's `## Additional Skills` section.

## How Tab Gets Activated

The `summon-tab` shared skill triggers on phrases like "Hey Tab", "@Tab", etc. It scans `agents/` to discover available agents, always loads `agents/base/AGENT.md`, and optionally layers on a variant agent matched by conversation context. Claude then adopts the merged persona for the rest of the conversation.

## Conventions

- **Naming**: lowercase, hyphenated for all component directories (e.g., `draw-dino`, `summon-tab`)
- **Frontmatter**: all AGENT.md and SKILL.md files use YAML frontmatter with at minimum `name` and `description`
- **Skill triggers**: the `description` frontmatter field in SKILL.md doubles as the trigger condition
- **Variant agents**: variant AGENT.md files declare `extends: agents/base/AGENT.md` in frontmatter and use only "Additional X" sections (additive, never replace)
- **Git commits**: conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)
