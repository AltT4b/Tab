---
name: role-creator
description: This skill should be used when the user wants to create a new role, scaffold a new agent, add a role config, or set up a new worker/orchestrator/peer in the Tab directory. Activates on phrases like "create a role", "new role", "add a role config", "scaffold an agent", "new agent role", or when describing a new specialized agent to build.
---

# Tab Role Creator

Guides creation of new role configurations for the Tab multi-agent framework at `/Users/alttab-macbook/AltT4b/Tab`.

## Role Directory Structure

```
roles/
├── _base/
│   ├── agent/          ← minimal safe defaults (extend for most roles)
│   └── analyst/        ← read-heavy + summarize (extend for research/review roles)
├── researcher/         ← example worker
├── writer/             ← example worker
└── orchestrator/       ← top-level coordinator
```

## Files to Create for a New Role

```
roles/<role-name>/
├── role.yml            ← required: config manifest
├── system_prompt.j2    ← required: Jinja2 persona template
├── rules/              ← optional: guardrail markdown files
│   └── <rule>.md
└── output_schema.json  ← optional: for validated structured output
```

## Step-by-Step Creation Process

1. **Name**: lowercase, alphanumeric + hyphens/underscores (`^[a-z0-9_-]+$`)
2. **Base role** — choose the right parent:
   - `_base/agent` — general default, minimal tools
   - `_base/analyst` — pre-configured for read + web + summarize
4. **Orchestration role**:
   - `orchestrator` — top-level coordinator, spawns sub-agents
   - `worker` — executes focused tasks, reports to orchestrator
   - `peer` — collaborates laterally with other agents
5. **Draft files** using templates in `references/templates.md`
6. **Validate**: `python scripts/validate_role.py roles/<role-name>/role.yml`

## Key Schema Rules

| Field | Constraint |
|-------|-----------|
| `name` | `^[a-z0-9_-]+$` |
| `version` | Semver string `"1.0.0"` (must be quoted) |
| `extends` | Path relative to `roles/`, e.g. `_base/agent` |
| `model.id` | Enum — must be one of three allowed values |
| `model.temperature` | Float 0–1 |
| `model.max_tokens` | Integer 1–32768 |
| `system_prompt.template` | Must end in `.j2` |
| `autonomy.forbidden_patterns` | Always include `"rm -rf"` and `"DROP TABLE"` |
| `tools.deny` | Takes precedence over `tools.allow` |

## Tool Access Patterns

| Role type | Typical `allow` | Typical `deny` |
|-----------|-----------------|----------------|
| Read-only analyst | `[read_file, web_fetch, bash]` | `[write_file, delete_file]` |
| Writer | `[read_file, write_file, bash]` | `[web_fetch, delete_file]` |
| Orchestrator | `[bash, read_file, write_file]` | `[delete_file]` |
| Minimal / safe | `[read_file]` | `[]` |

## Validation

Always run after creating or modifying a role:

```bash
cd /Users/alttab-macbook/AltT4b/Tab
python scripts/validate_role.py roles/<role-name>/role.yml
```

See `references/templates.md` for complete copy-paste templates for `role.yml` and `system_prompt.j2`.
