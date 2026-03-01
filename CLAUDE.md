# Tab — Developer Guide

## Context

Tab is a toolkit of AI capabilities — skills, agents, and rules — that extend Claude Code into a personal assistant. It's implemented as a Claude Code plugin.

This is an active learning project. Conventions evolve as Claude Code best practices become clearer. The README is the user-facing reference; this file captures where we are and why decisions were made.

---

## Decisions

**Skills and rules serve distinct purposes.**
- **Skills** — AI-invoked instruction sets (`skills/<name>/SKILL.md`)
- **Rules** — always-on behavioral guardrails (`rules/<name>.md`, referenced from `settings.json`)

**Plugin structure follows Claude Code conventions.** `.claude-plugin/plugin.json` is the manifest. Component directories (`skills/`, `agents/`) live at the plugin root. Rules are wired through `settings.json` instructions.

**Tab has a summoning mechanism.** Users can address Tab by name ("Hey Tab", "Tab, …", "@Tab") to activate the default agent. The `defaultAgent` field in `settings.json` controls which agent activates. The `summon-tab` skill handles activation. This is a fundamental design tenet: Tab should always have a named, addressable identity that users can summon conversationally.

**Tab does not grow itself.** Tab is a pure runtime toolkit. The `personal-assistant-builder` plugin (a sibling repository) handles research, planning, and scaffolding of new Tab components. Tab has no bootstrap or meta-agent of its own.

---

## Repo Structure

```
Tab/
├── .claude-plugin/
│   └── plugin.json       # Plugin manifest
├── agents/               # Agent definitions
│   └── _base.md          # Default agent
├── skills/               # Skills
│   ├── research/         #   General-purpose research
│   └── summon-tab/       #   Agent routing and activation
├── rules/                # Behavioral guardrails
└── settings.json         # Plugin settings
```
