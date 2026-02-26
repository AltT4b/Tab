# Tab — System Design

**Date:** 2026-02-25
**Author:** T4b
**Status:** Approved

---

## Overview

Tab is a monorepo framework for defining, composing, and eventually executing Claude-based agents. The central concept is the **role** — a self-describing directory bundle that encapsulates everything needed to instantiate and run an agent: its identity, model configuration, tool permissions, memory strategy, autonomy limits, output contracts, orchestration position, and bundled Claude artifacts.

The `roles/` directory is the core of the project. A custom agent runner (to be built in `src/`) reads these role definitions at runtime and uses them to spin up Claude-based agents.

---

## Repository Structure

```
Tab/
├── roles/
│   ├── _base/                    # Abstract base roles (not directly runnable)
│   │   ├── role.yml
│   │   └── system_prompt.j2
│   ├── researcher/
│   │   ├── role.yml
│   │   ├── system_prompt.j2
│   │   ├── skills/
│   │   ├── hooks/
│   │   ├── commands/
│   │   └── rules/
│   └── orchestrator/
│       ├── role.yml
│       └── system_prompt.j2
├── schemas/
│   └── role.schema.json          # JSON Schema — single source of truth for role.yml
├── src/                          # Future runner
├── docs/
│   └── plans/
└── README.md
```

Roles prefixed with `_` are abstract and exist for inheritance only. The runner refuses to instantiate them directly.

---

## Role Directory Bundle Anatomy

Only `role.yml` is required. All other files and directories are optional and discovered by convention.

```
roles/<name>/
├── role.yml              # Manifest — required
├── system_prompt.j2      # Jinja2 persona template — preferred over inline string
├── skills/               # Bundled Claude Code skills (SKILL.md folders)
├── hooks/                # Scripts wired to Claude hook events
│   ├── pre_tool_call.py
│   └── post_tool_call.py
├── commands/             # Custom slash commands
│   └── summarize.py
├── rules/                # Guardrail documents always injected into context
│   └── no_pii.md
└── output_schema.json    # Optional JSON Schema for output validation
```

The runner translates bundled Claude artifacts (skills, hooks, commands, rules) into the equivalent Claude Code session configuration at startup.

---

## The `role.yml` Schema

```yaml
# ── Identity ────────────────────────────────────────────────────────────────
name: researcher
version: "1.0.0"
extends: _base/analyst          # optional; deep merge, child wins conflicts
description: "Web research specialist focused on technical topics."

# ── Model ───────────────────────────────────────────────────────────────────
model:
  id: claude-opus-4-5-20251101
  temperature: 0.5
  max_tokens: 8096

# ── Persona ─────────────────────────────────────────────────────────────────
system_prompt:
  template: system_prompt.j2    # rendered with vars below at load time
  vars:
    domain: "software engineering"
    tone: "precise and analytical"
    expertise_level: "expert"

# ── Tool Access ─────────────────────────────────────────────────────────────
tools:
  allow: [bash, web_fetch, read_file]
  deny: [write_file, delete_file]
  mcp_servers:
    - name: exa

# ── Memory & Context ────────────────────────────────────────────────────────
memory:
  type: persistent              # ephemeral | persistent | shared
  backend: sqlite               # file | sqlite
  scratchpad: true
  context_strategy: summarize   # summarize | truncate | full

# ── Autonomy Limits ─────────────────────────────────────────────────────────
autonomy:
  max_tool_calls: 50
  max_cost_usd: 2.00
  checkpoint_every: 10          # require human check-in every N tool calls
  allowed_paths: ["./workspace/**"]
  forbidden_patterns: ["rm -rf", "DROP TABLE"]

# ── Output Contract ─────────────────────────────────────────────────────────
output:
  format: markdown              # markdown | json | structured
  schema: ./output_schema.json  # optional; runner validates output against this
  destinations:
    - type: file
      path: ./outputs/{{ run_id }}.md
    - type: stdout

# ── Orchestration ───────────────────────────────────────────────────────────
orchestration:
  role: worker                  # orchestrator | worker | peer
  reports_to: manager
  can_spawn: [writer, reviewer]
  can_delegate_to: [researcher]
  max_sub_agents: 3
  delegation_strategy: parallel # parallel | sequential | conditional

# ── Claude Artifacts ────────────────────────────────────────────────────────
claude:
  skills: [./skills/web-research]
  hooks:
    - event: pre_tool_call
      script: ./hooks/pre_tool_call.py
    - event: post_tool_call
      script: ./hooks/post_tool_call.py
  commands: [./commands/summarize.py]
  rules: [./rules/no_pii.md]

# ── Metadata ────────────────────────────────────────────────────────────────
metadata:
  tags: [research, web, technical]
  author: T4b
  created: 2026-02-25
```

All top-level sections except `name` and `version` are optional. `schemas/role.schema.json` enforces validity at load time.

Secrets are always referenced as `${ENV_VAR}` — raw values are never written into role files.

---

## Inheritance Model

When a role declares `extends:`, the runner performs a deep merge at load time.

**Merge rules:**
- Scalar fields: child wins
- List fields (`tools.allow`, `rules`, `skills`, etc.): union merge — child never loses parent guardrails
- Max inheritance depth: 3 levels
- No circular `extends` — detected at load time, fails fast
- No multiple inheritance — `extends` is a single string
- Abstract roles (prefixed `_`) cannot be instantiated directly

```
_base/analyst               researcher
──────────────              ──────────────────────
autonomy:                   autonomy:
  max_cost_usd: 1.00    →     max_cost_usd: 2.00   (child wins)
  checkpoint_every: 5   →     checkpoint_every: 5  (inherited)

tools:                      tools:
  allow: [read_file]    →     allow: [read_file, web_fetch]  (union)

rules:                      rules:
  - no_pii.md           →     [no_pii.md, no_credentials.md] (union)
```

---

## Multi-Agent Orchestration

The `orchestration` block defines each agent's position and permissions within a graph.

**Role types:**

- **`orchestrator`** — top-level coordinator; spawns and delegates to sub-agents; higher autonomy limits
- **`worker`** — receives tasks, executes, returns output to `reports_to` target
- **`peer`** — lateral collaboration; can call and be called by sibling agents without strict hierarchy

**Example graph:**

```
orchestrator (manager)
├── spawns → researcher   (worker, reports_to: manager)
├── spawns → writer       (worker, reports_to: manager)
└── spawns → reviewer     (peer with writer)
```

The runner enforces the graph at runtime — if an agent attempts to spawn a role not in its `can_spawn` list, the action is blocked and logged.

**Delegation strategies:**

- `parallel` — all sub-agents run concurrently; orchestrator collects results
- `sequential` — sub-agents run one at a time; each receives previous output
- `conditional` — orchestrator evaluates output after each step and routes dynamically

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| LLM scope | Claude-only | Deep native integration; no abstraction overhead |
| Role format | Directory bundle | Mirrors skills library pattern; scales from simple to complex |
| Secrets | Env var refs only | Safe to commit; `${VAR}` syntax throughout |
| Persona | Jinja2 template | Composable, testable, version-controllable |
| Inheritance | Single extends, deep merge | Predictable; list union prevents guardrail loss |
| Multiple inheritance | Excluded | Keeps merge semantics simple and auditable |
| Schema validation | JSON Schema at load time | Loud failures at startup, not mid-run |
