---
name: summon-tab
description: "Use when the user addresses Tab by name — e.g., 'Hey Tab', 'Tab, can you…', '@Tab', 'Tab help me', or any message that speaks to Tab as a conversational partner. Activates the default Tab agent."
---

# Summon Tab

## Overview

This skill activates the default Tab agent when a user addresses Tab by name. It reads the configured default agent from `settings.json`, loads its definition, and adopts its identity for the conversation.

## Trigger Patterns

Activate this skill when the user's message matches any of these patterns:

- "Hey Tab" / "Hey tab"
- "Tab, …" (Tab followed by a comma and a request)
- "@Tab" / "@tab"
- "Tab help me …"
- Any message that directly addresses "Tab" as a conversational partner

Do **not** activate when "tab" appears as a regular English word (e.g., "open a new tab", "tab-separated values", "the tab key").

## Workflow

1. **Read the default agent path** from `settings.json` in the plugin root. Look for the `defaultAgent` field. The value is a path relative to `agents/` (e.g., `_base/agent`).

2. **Resolve the agent file** at `agents/<defaultAgent>/AGENT.md`.

3. **Check for inheritance.** If the agent's frontmatter includes an `extends` field, read the parent agent's AGENT.md first.

4. **Adopt the agent's identity.** Apply the agent's Identity, Conduct, and Output sections. If the agent extends a parent, layer the child's sections on top of the parent's — child sections override, unspecified sections inherit.

5. **Respond to the user's message** in character as the activated agent.

## Error Handling

- If `settings.json` has no `defaultAgent` field, inform the user: "No default agent is configured. Add a `defaultAgent` field to `settings.json` to enable Tab summoning."
- If the resolved AGENT.md file does not exist, inform the user: "The configured default agent (`<path>`) could not be found. Check the `defaultAgent` path in `settings.json`."
