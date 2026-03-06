# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Tab is a Claude Code plugin that implements a personal AI assistant entirely in markdown. There is no compiled code, no runtime, no package dependencies, no build system, no tests, and no linting. All behavior is defined through text files that Claude Code reads and interprets.

## Entry Points

- **Plugin manifest**: `.claude-plugin/plugin.json` — registers shared skills with Claude Code.
- **Agent persona**: `agents/tab/AGENT.md` — Tab's identity, voice, rules, and skills registry.
- **Shared skills**: `skills/` — skills registered via the plugin manifest (e.g., `summon-tab`).
- **Tab-local skills**: `agents/tab/skills/` — skills only available to Tab (brainstorm, draw-dino, memory, team).

Tab is activated by the `summon-tab` shared skill, which loads `agents/tab/AGENT.md`. The persona and skill files are the source of truth for all behavior.

## Conventions

- **Naming**: lowercase, hyphenated for all component directories (e.g., `draw-dino`, `summon-tab`)
- **Frontmatter**: SKILL.md files use YAML frontmatter with `name`, `description`, and optionally `argument-hint`. AGENT.md files use `name` and `description` at minimum.
- **Skill triggers**: the `description` frontmatter field in SKILL.md doubles as the trigger condition. Descriptions should be reactive — they describe *when* the skill activates based on user intent, not directives commanding the model to use the skill.
- **Subagent skills**: some skills include prose indicating they should run as a subagent via the Agent tool. This is a convention, not a frontmatter field.
- **Git commits**: conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)
