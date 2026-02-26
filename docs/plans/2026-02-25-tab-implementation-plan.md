# Tab — Implementation Plan

**Date:** 2026-02-25
**Status:** Active

---

## Goal

Scaffold the Tab monorepo with a validated role schema, a set of abstract base roles, three concrete example roles, and a CLI validation utility. The runner (`src/`) is out of scope for this phase.

---

## Phases

### Phase 1 — Monorepo Scaffold
Create the full directory skeleton: `roles/`, `schemas/`, `src/`, `scripts/`, `docs/`.
Add `.gitignore` (ignores `.env`, `*.secrets.yml`, `__pycache__`, `.DS_Store`).

### Phase 2 — JSON Schema (`schemas/role.schema.json`)
Write the authoritative JSON Schema for `role.yml`. Covers all top-level sections:
identity, model, system_prompt, tools, memory, autonomy, output, orchestration, claude, metadata.
This schema drives both validation and IDE autocompletion.

### Phase 3 — Abstract Base Roles
- `roles/_base/agent/` — minimal base: model defaults, conservative autonomy limits, ephemeral memory
- `roles/_base/analyst/` — extends `_base/agent`; adds read-only tool defaults, summarize context strategy

### Phase 4 — Concrete Example Roles
- `roles/researcher/` — worker; extends `_base/analyst`; web fetch + bash; persistent memory; parallel delegation
- `roles/writer/` — worker; extends `_base/agent`; write-focused tools; structured output contract
- `roles/orchestrator/` — orchestrator; extends `_base/agent`; can spawn researcher + writer; sequential delegation

Each concrete role includes a `system_prompt.j2` template.

### Phase 5 — Validation Utility (`scripts/validate_role.py`)
CLI script: `python scripts/validate_role.py roles/researcher`
- Loads `role.yml`, validates against `schemas/role.schema.json`
- Checks inheritance chain resolves without cycles or depth violations
- Reports errors with clear messages; exits non-zero on failure
- Accepts `--all` flag to validate every role in `roles/`

### Phase 6 — README
Top-level `README.md` covering: what Tab is, repo structure, how to define a role, inheritance rules, orchestration model, how to run the validator.

---

## Deliverables

```
Tab/
├── .gitignore
├── README.md
├── roles/
│   ├── _base/
│   │   ├── agent/
│   │   │   ├── role.yml
│   │   │   └── system_prompt.j2
│   │   └── analyst/
│   │       ├── role.yml
│   │       └── system_prompt.j2
│   ├── researcher/
│   │   ├── role.yml
│   │   ├── system_prompt.j2
│   │   └── rules/
│   │       └── no_pii.md
│   ├── writer/
│   │   ├── role.yml
│   │   ├── system_prompt.j2
│   │   └── output_schema.json
│   └── orchestrator/
│       ├── role.yml
│       └── system_prompt.j2
├── schemas/
│   └── role.schema.json
├── scripts/
│   └── validate_role.py
├── src/
│   └── .gitkeep
└── docs/
    └── plans/
        ├── 2026-02-25-Tab-design.md
        └── 2026-02-25-Tab-implementation-plan.md
```
