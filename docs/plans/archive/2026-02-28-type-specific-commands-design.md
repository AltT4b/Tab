# Design: Type-Specific Commands

## Problem

The single `/add-component` command is a blank check — it accepts no structured input and relies on the `add-component` skill to infer type, name, and scope from free-form conversation. This creates unnecessary ambiguity and makes it easy for users to provide incomplete or malformed input.

## Solution

Replace `/add-component` with four type-specific commands that act as rigid input funnels before handing off to the `add-component` skill:

- `/add-agent <name>` — creates an agent
- `/add-skill <name>` — creates a skill
- `/add-command <name>` — creates a command
- `/add-rule <name>` — creates a rule

Each command locks the component type, validates the name, resolves scope, and then invokes the `add-component` skill with all inputs pre-determined.

## Changes

| Action | Path |
|--------|------|
| Delete | `commands/add-component/add-component.md` |
| Create | `commands/add-agent/add-agent.md` |
| Create | `commands/add-skill/add-skill.md` |
| Create | `commands/add-command/add-command.md` |
| Create | `commands/add-rule/add-rule.md` |
| Keep   | `skills/add-component/SKILL.md` (unchanged) |

## Command Behavior

All four commands follow the same rigid flow:

1. **Type is locked** — hardcoded in the command body, never inferred.
2. **Parse name from argument** — e.g., `/add-skill my-skill` extracts `my-skill`. If no argument provided, ask for it.
3. **Validate name** — must be lowercase-hyphenated. Reject and re-prompt if invalid.
4. **Ask scope** (skill, command, rule only) — "Shared or agent-local?" If agent-local, ask which agent. Agents skip this step (always shared).
5. **Invoke the `add-component` skill** with type, name, and scope locked in. The skill must not re-ask for any of these.

## Namespacing

Commands resolve to `tab:add-agent:add-agent`, `tab:add-skill:add-skill`, etc. The `tab:` prefix is automatic from the plugin system and prevents collisions with other plugins.

## What stays the same

The `add-component` skill remains the single source of truth for templates, placement rules, and conventions. Commands are just structured entry points — they don't duplicate the skill's content.
