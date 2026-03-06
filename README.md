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

---

## Permissions

Tab reads its own files at runtime — persona definitions, skill instructions, and other plugin files. When you first summon Tab, Claude Code may prompt you to approve these file reads. This is normal. Tab is loading its own playbook, not poking around in your code.

You can approve these reads as they come up, or approve once and let Claude Code remember. Either way, Tab only ever reads from two places:

- **Its own plugin directory** — where Tab's persona and skills live
- **Your current working directory** — only when you ask Tab to work with your files
