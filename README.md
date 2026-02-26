# Tab

A monorepo framework for defining, composing, and running Claude-based AI agents. The central concept is the **role** — a self-describing directory bundle that encapsulates everything needed to instantiate an agent: identity, model config, tool permissions, memory strategy, autonomy limits, output contracts, and Claude-native artifacts.

---

## Repository Structure

```
Tab/
├── roles/                  # All role definitions
│   ├── _base/              # Abstract base roles (not directly runnable)
│   │   ├── agent/          # Root base: safe defaults for all roles
│   │   └── analyst/        # Extends agent: read-heavy research defaults
│   ├── researcher/         # Concrete worker: web research specialist
│   ├── writer/             # Concrete worker: content drafting
│   └── orchestrator/       # Concrete orchestrator: task coordination
├── schemas/
│   └── role.schema.json    # JSON Schema for role.yml validation
├── scripts/
│   └── validate_role.py    # CLI validator
├── src/                    # Future agent runner
└── docs/
    └── plans/              # Design and implementation docs
```

---

## Defining a Role

Every role is a directory inside `roles/`. The only required file is `role.yml`.

```
roles/my-role/
├── role.yml              # Required manifest
├── system_prompt.j2      # Jinja2 persona template (preferred)
├── skills/               # Bundled Claude Code skills
├── hooks/                # Claude hook scripts
├── commands/             # Custom slash commands
├── rules/                # Guardrail markdown files
└── output_schema.json    # Optional output validation schema
```

### Minimal role.yml

```yaml
name: my-role
version: "1.0.0"
description: "Does one thing well."

model:
  id: claude-sonnet-4-5-20250929

system_prompt: "You are a helpful assistant."
```

### Full role.yml reference

See [docs/plans/2026-02-25-tab-design.md](docs/plans/2026-02-25-tab-design.md) for the complete annotated schema, or inspect [schemas/role.schema.json](schemas/role.schema.json) directly.

---

## Inheritance

Roles can extend a parent with `extends:`:

```yaml
name: researcher
version: "1.0.0"
extends: _base/analyst
```

Merge rules:
- **Scalar fields** — child wins over parent.
- **List fields** (`tools.allow`, `rules`, `skills`, etc.) — union merged; child never loses parent guardrails.
- **Max depth** — 3 levels. The validator enforces this.
- **No circular inheritance** — detected at load time.
- **No multiple inheritance** — `extends` is a single string.

Abstract roles (prefixed `_`) cannot be instantiated directly.

---

## Orchestration

Set the `orchestration` block to define how a role participates in multi-agent graphs.

```yaml
orchestration:
  role: orchestrator        # orchestrator | worker | peer
  can_spawn: [researcher, writer]
  can_delegate_to: [researcher, writer]
  max_sub_agents: 5
  delegation_strategy: sequential  # parallel | sequential | conditional
```

**Role types:**
- `orchestrator` — coordinates the graph; spawns and delegates to sub-agents.
- `worker` — receives tasks, executes, returns output to `reports_to`.
- `peer` — lateral collaborator; can call and be called by sibling agents.

The runner enforces spawn/delegate permissions at runtime — unauthorized actions are blocked and logged.

---

## Secrets

All sensitive values live in `.env`. The runtime reads them via `os.getenv()` — never put raw secrets into role files.

```
EXA_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

---

## Validating Roles

Install dependencies:

```bash
poetry install
```

Validate a single role:

```bash
python scripts/validate_role.py roles/researcher
```

Validate all concrete roles:

```bash
python scripts/validate_role.py --all
```

Validate including abstract base roles:

```bash
python scripts/validate_role.py --all --allow-abstract
```

The validator checks:
1. `role.yml` is present and valid YAML.
2. All fields conform to `schemas/role.schema.json`.
3. Inheritance chain resolves with no cycles and within depth limits.
4. All referenced files (templates, hooks, rules, etc.) exist on disk.

---

## Available Models

| Model | ID |
|---|---|
| Claude Opus 4.5 | `claude-opus-4-5-20251101` |
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` |

---

## Design Docs

- [System Design](docs/plans/2026-02-25-tab-design.md)
- [Implementation Plan](docs/plans/2026-02-25-tab-implementation-plan.md)

---

## History

### `claude-agent.zip` — Tab's First Software

`claude-agent.zip` (committed 2026-02-26) is the first piece of software Tab ever wrote.

It doesn't quite work yet, but it's close — and that feels pretty neat.
