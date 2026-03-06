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
│   ├── advisor/                     # Advisor sub-agent (capability spec)
│   │   └── AGENT.md                 # Critique & structure capability spec
│   └── researcher/                  # Researcher sub-agent (capability spec)
│       ├── AGENT.md                 # Research capability spec
│       └── skills/
│           └── deep-research/SKILL.md  # Structured research skill
└── skills/
    └── summon-tab/SKILL.md          # Shared skill: activates Tab
```

## Architecture

**Plugin manifest** (`.claude-plugin/plugin.json`): Declares the plugin name, version, and the `skills` path (`./skills/`) that registers shared skills with Claude Code.

**Agents** (`agents/<name>/AGENT.md`): The base agent (`agents/base/`) defines Tab's core persona using `## Base *` sections. Sub-agents (`agents/advisor/`, `agents/researcher/`) are capability specs with `## Capability`, `## Behavior`, and `## Output` sections — no personality, no identity. Tab dispatches sub-agents internally via the Agent tool; the user never interacts with them directly.

**Skills** (`skills/<name>/SKILL.md` or `agents/<name>/skills/<name>/SKILL.md`): Instruction sets with YAML frontmatter whose `description` field doubles as the invocation trigger. Shared skills live under the top-level `skills/` directory and are registered via the plugin manifest. Agent-local skills live under an agent's `skills/` directory and are scoped to that agent.

## How Tab Gets Activated

The `summon-tab` shared skill triggers on phrases like "Hey Tab", "@Tab", etc. It embeds `agents/base/AGENT.md` via an `@` file reference. Claude adopts Tab's persona for the rest of the conversation. Tab's base AGENT.md includes a `## Sub-Agents` registry listing available sub-agents and their capabilities. Tab autonomously decides when to dispatch sub-agents via the Agent tool and synthesizes their results in his own voice.

## Skill Frontmatter

Skills use these optional frontmatter fields beyond `name` and `description`:

| Field | Purpose | Example |
|-------|---------|---------|
| `argument-hint` | Autocomplete hint shown in `/` menu | `"[topic]"`, `"[format] [topic]"` |
| `$ARGUMENTS` | In skill body, replaced with user's slash command arguments | `/deep-research quantum computing` |

## MCP Servers

No MCP servers are currently bundled. The researcher sub-agent's deep-research skill can use any MCP search tools available in the user's environment (e.g., Exa), but none are shipped with the plugin.

## Conventions

- **Naming**: lowercase, hyphenated for all component directories (e.g., `draw-dino`, `summon-tab`)
- **Frontmatter**: SKILL.md files use YAML frontmatter with `name`, `description`, and optionally `argument-hint`. AGENT.md files use `name` and `description` at minimum.
- **Skill triggers**: the `description` frontmatter field in SKILL.md doubles as the trigger condition
- **Sub-agents**: sub-agent AGENT.md files use `## Capability`, `## Behavior`, `## Output` sections. No `extends:` field, no personality.
- **Git commits**: conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)

