---
name: add-skill
description: Create a new skill for the Tab plugin.
---

Create a new **skill** component.

## Input

1. Parse the argument as the skill name. If no argument was provided, ask: "What should the skill be named?"
2. Validate: the name must be lowercase-hyphenated (e.g., `my-skill`). If invalid, explain the constraint and ask again.
3. Ask: "Should this be a shared skill or agent-local?" If agent-local, ask which agent.

## Handoff

Invoke the `add-component` skill with these inputs locked in:
- **Type:** skill
- **Name:** (from step 1)
- **Scope:** shared or agent-local with agent name (from step 3)

Do not allow the skill to re-ask for type, name, or scope.
