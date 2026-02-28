---
name: add-agent
description: Create a new agent for the Tab plugin.
---

Create a new **agent** component.

## Input

1. Parse the argument as the agent name. If no argument was provided, ask: "What should the agent be named?"
2. Validate: the name must be lowercase-hyphenated (e.g., `my-agent`). If invalid, explain the constraint and ask again.

Agents are always shared — they live in `agents/<name>/`. No scope question needed.

## Handoff

Invoke the `add-component` skill with these inputs locked in:
- **Type:** agent
- **Name:** (from step 1)
- **Scope:** shared (always)

Do not allow the skill to re-ask for type, name, or scope.
