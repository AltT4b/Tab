# Tab

Tab is a toolkit of AI capabilities — skills, agents, and rules — that extend Claude Code into a personal assistant. Implemented as a Claude Code plugin.

---

## Capabilities

### Summon Tab

Address Tab by name to activate the assistant.

> "Hey Tab, what's the best way to handle auth tokens?"

Trigger phrases: "Hey Tab", "Tab, ...", "@Tab", or any message that speaks to Tab directly. Tab activates its default agent and responds in character.

### Research

General-purpose knowledge gathering across web, codebase, and documentation.

Tab classifies each request by complexity and routes accordingly:

- **Quick** — single-source factual lookups
- **Explore** — multi-source comparisons, option surveys
- **Deep** — entity discovery, landscape mapping, structured reports (uses Exa websets when available)

All findings are cited with sources.

### Rules

Always-on behavioral guardrails applied across all interactions.

- **no-pii** — prevents collection, storage, or transmission of personally identifiable information unless explicitly authorized

---

## Structure

```
Tab/
├── .claude-plugin/plugin.json   # Plugin manifest
├── agents/_base.md              # Default agent
├── skills/
│   ├── research/SKILL.md        # Knowledge gathering
│   └── summon-tab/SKILL.md      # Agent activation
├── rules/no-pii.md              # PII guardrail
└── settings.json                # Plugin settings
```
