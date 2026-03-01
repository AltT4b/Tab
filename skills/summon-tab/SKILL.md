---
name: summon-tab
description: "Use when the user addresses Tab by name — e.g., 'Hey Tab', 'Tab, can you…', '@Tab', 'Tab help me', or any message that speaks to Tab as a conversational partner. Routes to the appropriate Tab agent."
---

# Summon Tab

## Overview

This skill activates a Tab agent when a user addresses Tab by name. It evaluates the user's message against a routing table to select the right agent, then loads that agent's definition and adopts its identity for the conversation.

## Trigger Patterns

Activate this skill when the user's message matches any of these patterns:

- "Hey Tab" / "Hey tab"
- "Tab, …" (Tab followed by a comma and a request)
- "@Tab" / "@tab"
- "Tab help me …"
- Any message that directly addresses "Tab" as a conversational partner

Do **not** activate when "tab" appears as a regular English word (e.g., "open a new tab", "tab-separated values", "the tab key").

## Routing

After confirming a Tab-addressed message, evaluate against this table in priority order. Use the first match.

| Priority | Keywords in message | Agent path (relative to `agents/`) |
|----------|--------------------|------------------------------------|
| 1 | *(default — no keyword match)* | Value of `defaultAgent` in `settings.json` |

Future agents will be added as new rows in this table before the default row.

## Workflow

1. **Check routing.** Scan the user's message for routing keywords (see table above). If a keyword match is found, use that agent path. Otherwise, read the `defaultAgent` field from `settings.json`. If no keyword matches, use `defaultAgent`.

2. **Resolve the agent file.** For directory-bundle agents, the path is `agents/<path>` (e.g., `agents/bootstrap/AGENT.md`). For simple agents, the path is `agents/<filename>` (e.g., `agents/_base.md`).

3. **Check for inheritance.** If the agent's frontmatter includes an `extends` field, read the parent agent's definition first.

4. **Adopt the agent's identity.** Apply the agent's Identity, Conduct, and Output sections. If the agent extends a parent, layer the child's sections on top — child sections override, unspecified sections inherit.

5. **Respond to the user's message** in character as the activated agent.

## Error Handling

- If `settings.json` has no `defaultAgent` field, inform the user: "No default agent is configured. Add a `defaultAgent` field to `settings.json` to enable Tab summoning."
- If the resolved agent file does not exist, inform the user: "The configured agent (`<path>`) could not be found. Check the agent path."
