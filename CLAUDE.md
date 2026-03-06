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
│   └── tab/
│       ├── AGENT.md                 # Tab's persona (always loaded)
│       └── skills/
│           ├── brainstorming/SKILL.md  # Brainstorming skill
│           ├── draw-dino/SKILL.md      # ASCII art dinosaur skill
│           ├── memory/SKILL.md         # Internal memory system (not user-invoked)
│           └── team/SKILL.md           # Multi-agent team orchestration (subagent)
├── docs/
│   └── plans/                       # Design documents
├── skills/
│   └── summon-tab/SKILL.md          # Shared skill: activates Tab
```

## Architecture

**Plugin manifest** (`.claude-plugin/plugin.json`): Declares the plugin name, version, and the `skills` path (`./skills/`) that registers shared skills with Claude Code.

**Agent** (`agents/tab/AGENT.md`): Tab is the only agent. His persona defines identity, voice, rules, and a skills registry. Tab is conversational; everything else is his toolbox.

**Skills** (`skills/<name>/SKILL.md` or `agents/tab/skills/<name>/SKILL.md`): Instruction sets with YAML frontmatter whose `description` field doubles as the invocation trigger. Shared skills live under the top-level `skills/` directory and are registered via the plugin manifest. Tab-local skills live under `agents/tab/skills/`. Some skills are marked as subagent skills — Tab dispatches these via the Agent tool for independent execution, then synthesizes their results in his own voice.

## How Tab Gets Activated

The `summon-tab` shared skill triggers on phrases like "Hey Tab", "@Tab", etc. It embeds `agents/tab/AGENT.md` via an `@` file reference. Claude adopts Tab's persona for the rest of the conversation. Tab's AGENT.md includes a skills registry. Some skills are subagent skills — Tab autonomously decides when to dispatch them via the Agent tool and synthesizes their results in his own voice.

## Skill Frontmatter

Skills use these optional frontmatter fields beyond `name` and `description`:

| Field | Purpose | Example |
|-------|---------|---------|
| `argument-hint` | Autocomplete hint shown in `/` menu | `"[topic]"`, `"[format] [topic]"` |
| `$ARGUMENTS` | In skill body, replaced with user's slash command arguments | `/deep-research quantum computing` |

## MCP Servers

No MCP servers are bundled. The team skill can use search tools available in the user's environment (e.g., Exa MCP, WebSearch) — Tab checks what's available and passes tools to subagents at dispatch time. See the team skill's "How Skills works" section and `docs/plans/2026-03-05-team-skill-design.md` for the capability resolution model.

## Conventions

- **Naming**: lowercase, hyphenated for all component directories (e.g., `draw-dino`, `summon-tab`)
- **Frontmatter**: SKILL.md files use YAML frontmatter with `name`, `description`, and optionally `argument-hint`. AGENT.md files use `name` and `description` at minimum.
- **Skill triggers**: the `description` frontmatter field in SKILL.md doubles as the trigger condition
- **Subagent skills**: some skills include prose indicating they should run as a subagent via the Agent tool. This is a convention, not a frontmatter field.
- **Git commits**: conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)

