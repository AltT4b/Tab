# Tab — Developer Guide

## Context

Tab is a framework for defining Claude-based AI agents as file-system primitives. Each agent is a self-contained directory bundle: an `AGENT.md` file provides YAML frontmatter for configuration and a markdown body for behavioral instructions, with optional local assets alongside it.

This is an active learning project. Conventions evolve as Claude Code best practices become clearer. The README is the user-facing reference; this file captures where we are, why decisions were made, and what the rules are right now.

---

## Decisions

**AGENT.md is the canonical agent definition.** Config in frontmatter, behavior in the markdown body. Self-describing, diff-friendly, no runtime config. Each agent is a directory in `agents/` containing an `AGENT.md` file.

**Abstract base agents are prefixed with `_`.** Not directly runnable — concrete agents extend them (e.g., `_base/agent`).

**Skills, commands, and rules serve distinct purposes.**
- **Skills** — AI-invoked instruction sets (`skills/<name>/SKILL.md`)
- **Commands** — user-invoked slash commands (`commands/<name>/<name>.md`)
- **Rules** — always-on behavioral guardrails (`rules/<name>/<name>.md`, referenced from `settings.json`)

**Shared assets live at the repo root; agent-local assets take precedence.**

**Plugin structure follows Claude Code conventions where possible.** `.claude-plugin/plugin.json` is the manifest. Component directories (`skills/`, `commands/`, `agents/`) live at the plugin root. Rules are wired through `settings.json` instructions. Agent directory bundles are a Tab-specific convention; Tab handles its own agent discovery.

**Tab has a summoning mechanism.** Users can address Tab by name ("Hey Tab", "Tab, …", "@Tab") to activate the default agent. The `defaultAgent` field in `settings.json` controls which agent activates — its value is a path relative to `agents/` (e.g., `_base/agent`). The `summon-tab` skill handles activation. To change the default agent, edit the `defaultAgent` value in `settings.json`. This is a fundamental design tenet: Tab should always have a named, addressable identity that users can summon conversationally.

---

## Conventions

Repo structure:
```
Tab/
├── .claude-plugin/
│   └── plugin.json       # Plugin manifest (name, version, paths)
├── agents/               # Agent directory bundles
│   └── _base/            # Abstract base agents (not directly runnable)
│       └── agent/        # Root base: safe defaults for all agents
│           └── AGENT.md
├── skills/               # Shared across all agents
├── commands/             # Shared slash commands
├── rules/                # Shared guardrails
└── settings.json         # Plugin settings (defaultAgent, rules)
```

Agent directory format (e.g., `agents/my-agent/`):

```
agents/my-agent/
├── AGENT.md              # Required
├── skills/               # Optional: agent-specific skills
├── commands/             # Optional: agent-specific commands
├── rules/                # Optional: agent-specific rules
└── output_schema.json    # Optional
```

AGENT.md frontmatter:

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches directory name |
| `description` | Yes | One sentence: what it does and when to use it |
| `extends` | No | Path to parent agent, relative to `agents/` |

Naming: lowercase, hyphenated. Inheritance: no more than two levels deep.

settings.json fields:

| Field | Required | Notes |
|-------|----------|-------|
| `defaultAgent` | Yes | Path to the default agent, relative to `agents/`. Activated by the `summon-tab` skill. |
| `instructions` | No | Array of rule file paths to load as always-on guardrails. |
