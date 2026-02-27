# Tab — Implementation Plan

**Date:** 2026-02-25
**Status:** Active

---

## Goal

Scaffold the Tab monorepo with a set of abstract base agents and concrete example agents. The focus is on the agent definition system — no runner or processing layer.

---

## Phases

### Phase 1 — Monorepo Scaffold
Create the full directory skeleton: `agents/`, `docs/`.
Add `.gitignore` (ignores `.env`, `*.secrets.yml`, `__pycache__`, `.DS_Store`).

### Phase 2 — JSON Schema (`schemas/role.schema.json`)
Write the authoritative JSON Schema for `role.yml`. Covers all top-level sections:
identity, model, system_prompt, tools, memory, autonomy, output, orchestration, claude, metadata.
This schema drives both validation and IDE autocompletion.

### Phase 3 — Abstract Base Agents
- `agents/_base/agent/` — minimal base: model defaults, conservative autonomy limits, ephemeral memory
- `agents/_base/analyst/` — extends `_base/agent`; adds read-only tool defaults, summarize context strategy

### Phase 4 — Concrete Example Agents
- `agents/researcher/` — worker; extends `_base/analyst`; web fetch + bash; persistent memory; parallel delegation
- `agents/writer/` — worker; extends `_base/agent`; write-focused tools; structured output contract
- `agents/orchestrator/` — orchestrator; extends `_base/agent`; can spawn researcher + writer; sequential delegation

Each concrete agent has an `AGENT.md` with frontmatter + behavioral instructions.

### Phase 5 — README
Top-level `README.md` covering: what Tab is, repo structure, how to define an agent, inheritance rules, orchestration model.

---

## Deliverables

```
Tab/
├── .gitignore
├── README.md
├── agents/
│   ├── _base/
│   │   ├── agent/
│   │   │   └── AGENT.md
│   │   └── analyst/
│   │       └── AGENT.md
│   ├── researcher/
│   │   ├── AGENT.md
│   │   └── rules/
│   │       └── no_pii.md
│   ├── writer/
│   │   ├── AGENT.md
│   │   └── output_schema.json
│   └── orchestrator/
│       └── AGENT.md
└── docs/
    └── plans/
        ├── 2026-02-25-tab-design.md
        └── 2026-02-25-tab-implementation-plan.md
```
