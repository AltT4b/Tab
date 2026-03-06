# Tab

Tab is a toolkit of AI capabilities — skills, agents, and rules — that extend Claude Code into a personal assistant. Implemented as a Claude Code plugin.

---

## Structure

```
Tab/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── agents/
│   ├── tab/
│   │   ├── AGENT.md             # Tab's persona (always loaded)
│   │   └── skills/
│   │       ├── draw-dino/       # ASCII art dinosaur skill
│   │       └── writing/         # General-purpose writing skill
│   ├── advisor/
│   │   └── AGENT.md             # Critique & structure capability spec
│   └── researcher/
│       ├── AGENT.md             # Research capability spec
│       └── skills/
│           └── deep-research/   # Structured research skill
├── skills/
│   └── summon-tab/SKILL.md      # Agent dispatcher
├── CLAUDE.md
└── README.md
```
