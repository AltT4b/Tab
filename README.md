# Tab

Tab is a toolkit of AI capabilities — skills, agents, and rules — that extend Claude Code into a personal assistant. Implemented as a Claude Code plugin.

---

## Structure

```
Tab/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── agents/
│   ├── base/
│   │   ├── AGENT.md             # Core persona (always loaded)
│   │   └── skills/
│   │       ├── draw-dino/       # ASCII art dinosaur skill
│   │       └── writing/         # General-purpose writing skill
│   ├── advisor/
│   │   └── AGENT.md             # Advisory/critique variant (extends base)
│   └── researcher/
│       ├── AGENT.md             # Research variant (extends base)
│       └── skills/
│           └── deep-research/   # Structured research skill
├── skills/
│   └── summon-tab/SKILL.md      # Agent dispatcher
├── CLAUDE.md
└── README.md
```
