---
name: add-rule
description: Create a new rule for the Tab plugin.
---

Create a new **rule** component.

## Input

1. Parse the argument as the rule name. If no argument was provided, ask: "What should the rule be named?"
2. Validate: the name must be lowercase-hyphenated (e.g., `my-rule`). If invalid, explain the constraint and ask again.
3. Ask: "Should this be a shared rule or agent-local?" If agent-local, ask which agent.

## Handoff

Invoke the `add-component` skill with these inputs locked in:
- **Type:** rule
- **Name:** (from step 1)
- **Scope:** shared or agent-local with agent name (from step 3)

Do not allow the skill to re-ask for type, name, or scope.
