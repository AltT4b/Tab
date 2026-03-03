# Summon-Tab Redesign — Extensible Agent Loader

## Goal

Refactor `summon-tab` from a hardcoded single-agent skill into a thin dispatcher that supports multiple Tab variants through additive context layering. Base persona always loads; role-specific variants layer on top when matched.

## Design Principles

- **Context efficiency**: skill body stays small (layer 2), agent content loads on-demand (layer 3)
- **Additive only**: variants append to base sections, never replace them
- **Graceful degradation**: with zero variants, behaves identically to today's skill
- **Single invocation**: user always says "Hey Tab" — routing is automatic

## Architecture

### Directory Structure

```
agents/
├── base/
│   ├── AGENT.md              # Always loaded (identity, rules, output)
│   └── skills/               # Base-level skills
│       └── draw-dino/SKILL.md
├── <variant>/                 # Future role-specific variants
│   ├── AGENT.md              # Additions-only format
│   └── skills/               # Variant-specific skills
```

Variants live as sibling directories to `base/` under `agents/`.

### Variant AGENT.md Format

Variants use an additions-only format with `extends: base` in frontmatter:

```yaml
---
name: Tab (<Role>)
description: "<Role>-focused additions to Tab's base persona"
extends: base
---

## Additional Identity

[Extra personality traits or context for this role]

## Additional Rules

[Role-specific rules appended to base rules]

## Additional Skills

[Role-specific skills or references to local skills/]
```

Sections are prefixed with "Additional" — the loader appends them to the corresponding base sections. Base sections are never redefined in variant files.

### Routing Logic

1. **Scan** `agents/*/AGENT.md` for directories with AGENT.md files (excluding `base/`)
2. **If no variants exist** — load base only, skip routing
3. **If variants exist** — evaluate conversation context against each variant's `description` frontmatter to pick the best match
4. **If no variant is a clear match** — load base only (safe default)
5. **Load order** — `agents/base/AGENT.md` first, then selected variant's AGENT.md
6. **Merge** — variant's "Additional X" sections append to base's corresponding sections

### Refactored SKILL.md

`summon-tab` becomes a four-step dispatcher:

1. **Discover** — scan `agents/*/AGENT.md`, separate base from variants
2. **Route** — if variants exist, match conversation context against variant descriptions
3. **Load** — read base AGENT.md, then variant AGENT.md if selected, merge additively
4. **Become Tab** — adopt the merged persona, stay in character

The skill contains only orchestration logic. All persona content lives in agent files.

## What Changes Now

- Refactor `skills/summon-tab/SKILL.md` into the thin dispatcher format
- No new agent variants created yet — framework is ready for them to drop in

## What Changes Later (When Variants Are Added)

- Create `agents/<variant>/AGENT.md` with additions-only format
- Optionally add `agents/<variant>/skills/` for variant-specific skills
- No changes to `summon-tab` needed — discovery is automatic
