# Tab — Developer Guide

## Context

Tab is a framework for defining Claude-based AI agents as file-system primitives. Each agent is a markdown file in `agents/` with YAML frontmatter for configuration and a markdown body for behavioral instructions.

This is an active learning project. Conventions evolve as Claude Code best practices become clearer. The README is the user-facing reference; this file captures where we are, why decisions were made, and what the rules are right now.

---

## Decisions

**Each agent is a single markdown file in `agents/`.** Config in frontmatter, behavior in the markdown body. Self-describing, diff-friendly, no runtime config. Named `<agent-name>.md`.

**Abstract agents are prefixed with `_`.** Not directly runnable — concrete agents extend them (e.g., `_base`).

**Skills and rules serve distinct purposes.**
- **Skills** — AI-invoked instruction sets (`skills/<name>/SKILL.md`)
- **Rules** — always-on behavioral guardrails (`rules/<name>/<name>.md`, referenced from `settings.json`)

**Plugin structure follows Claude Code conventions where possible.** `.claude-plugin/plugin.json` is the manifest. Component directories (`skills/`, `agents/`) live at the plugin root. Rules are wired through `settings.json` instructions.

**Tab has a summoning mechanism.** Users can address Tab by name ("Hey Tab", "Tab, …", "@Tab") to activate the default agent. The `defaultAgent` field in `settings.json` controls which agent activates — its value is a path relative to `agents/` (e.g., `_base.md` or `my-agent/AGENT.md`). The `summon-tab` skill handles activation. To change the default agent, edit the `defaultAgent` value in `settings.json`. This is a fundamental design tenet: Tab should always have a named, addressable identity that users can summon conversationally.

---

## Conventions

Repo structure:
```
Tab/
├── .claude-plugin/
│   └── plugin.json       # Plugin manifest (name, version, paths)
├── agents/               # Agent definitions
│   ├── _base.md          # Simple agent (single file)
│   └── my-agent/         # Complex agent (directory bundle)
│       ├── AGENT.md      #   Agent definition
│       └── skills/       #   Agent-local skills
├── skills/               # Shared across all agents
├── rules/                # Shared guardrails
└── settings.json         # Plugin settings (defaultAgent, rules)
```

Agents come in two forms:

- **Simple** — a single file: `agents/my-agent.md`
- **Directory bundle** — a directory with local assets: `agents/my-agent/AGENT.md` + siblings (skills, rules, etc.)

Frontmatter (in the agent `.md` file):

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Matches filename or directory name |
| `description` | Yes | One sentence: what it does and when to use it |
| `extends` | No | Path to parent agent, relative to `agents/` (e.g., `_base.md`) |

Naming: lowercase, hyphenated. Inheritance: no more than two levels deep.

settings.json fields:

| Field | Required | Notes |
|-------|----------|-------|
| `defaultAgent` | Yes | Path to agent file, relative to `agents/` (e.g., `_base.md`). Activated by the `summon-tab` skill. |
| `instructions` | No | Array of rule file paths to load as always-on guardrails. |
