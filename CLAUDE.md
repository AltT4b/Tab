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

**Agents** (`agents/<name>/AGENT.md`): Define an AI persona. The base agent (`agents/base/`) uses YAML frontmatter (`name`, `description`) and `## Base *` sections (`Base Identity`, `Base Rules`, `Base Skills`, `Base Output`). These sections define Tab's core persona and can be extended by variants but never overwritten. Variant agents declare `extends: agents/base/AGENT.md` in frontmatter and use `## Additional *` sections (`Additional Identity`, `Additional Rules`, `Additional Skills`, `Additional Output`) that append to the corresponding base sections.

**Skills** (`skills/<name>/SKILL.md` or `agents/<name>/skills/<name>/SKILL.md`): Instruction sets with YAML frontmatter whose `description` field doubles as the invocation trigger. Shared skills live under the top-level `skills/` directory and are registered via the plugin manifest. Agent-local skills live under an agent's `skills/` directory and are scoped to that agent.

## How Tab Gets Activated

The `summon-tab` shared skill triggers on phrases like "Hey Tab", "@Tab", etc. It scans `agents/` to discover available agents, always loads `agents/base/AGENT.md`, and optionally layers on a variant agent matched by conversation context. Claude then adopts the merged persona for the rest of the conversation.

## Conventions

- **Naming**: lowercase, hyphenated for all component directories (e.g., `draw-dino`, `summon-tab`)
- **Frontmatter**: all AGENT.md and SKILL.md files use YAML frontmatter with at minimum `name` and `description`
- **Skill triggers**: the `description` frontmatter field in SKILL.md doubles as the trigger condition
- **Variant agents**: variant AGENT.md files declare `extends: agents/base/AGENT.md` in frontmatter and use only "Additional X" sections (additive, never replace)
- **Git commits**: conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)
