# Skills Refactor Design

## Goal

Collapse sub-agent AGENT.md files (researcher, advisor) into Tab-owned skills. Tab becomes the only agent; everything else is his toolbox. Skills that need isolation can still dispatch via the Agent tool — that's an implementation detail, not an architectural distinction.

## File Changes

| Action | From | To |
|--------|------|----|
| Convert | `agents/researcher/AGENT.md` | `agents/tab/skills/research/SKILL.md` |
| Move | `agents/researcher/skills/deep-research/SKILL.md` | `agents/tab/skills/deep-research/SKILL.md` |
| Convert | `agents/advisor/AGENT.md` | `agents/tab/skills/advise/SKILL.md` |
| Delete | `agents/researcher/` directory | — |
| Delete | `agents/advisor/` directory | — |
| Edit | `agents/tab/AGENT.md` | Remove `## Sub-Agents`, add new skills to `## Skills` |
| Edit | `CLAUDE.md` | Update structure and architecture sections |

## Skill Format

Converted skills use standard SKILL.md frontmatter (`name`, `description`). The body contains the capability/behavior/output spec adapted from the original AGENT.md, plus prose indicating the skill should run as a subagent when appropriate.

## Final Structure

```
Tab/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── tab/
│       ├── AGENT.md
│       └── skills/
│           ├── advise/SKILL.md
│           ├── deep-research/SKILL.md
│           ├── draw-dino/SKILL.md
│           ├── research/SKILL.md
│           └── writing/SKILL.md
├── skills/
│   └── summon-tab/SKILL.md
└── CLAUDE.md
```

## What Stays the Same

- `skills/summon-tab/SKILL.md` — unchanged entry point
- `agents/tab/skills/draw-dino/` and `writing/` — unchanged
- Tab's identity, voice, rules — unchanged
- Agent tool still used at runtime for subagent dispatch
