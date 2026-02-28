# Summon Tab — Design

**Date:** 2026-02-28
**Status:** Approved

---

## Problem

There is no way to activate a Tab agent through natural language. Users should be able to say "Hey Tab", "Tab, help me…", "@Tab", or similar phrases and have a default agent take over the conversation.

This is a fundamental design tenet of Tab: the framework should have a named, addressable identity that users can summon conversationally.

## Design

The summon mechanism has three parts: a configuration key, a skill, and documentation.

### 1. Configuration — `settings.json`

Add a `defaultAgent` field to `settings.json`. This is the single source of truth for which agent activates when Tab is summoned.

```json
{
  "defaultAgent": "_base/agent",
  "instructions": [
    "rules/no-pii/no-pii.md"
  ]
}
```

The value is a path relative to `agents/`, matching the existing convention for agent references (e.g., the `extends` field in AGENT.md frontmatter). To change the default agent in the future, edit this one line.

### 2. Skill — `skills/summon-tab/SKILL.md`

A new shared skill with a broad trigger description that matches conversational summons: "Hey Tab", "Tab, …", "@Tab", and similar patterns.

The skill's body instructs Claude to:

1. Read `settings.json` to find the `defaultAgent` path.
2. Resolve that path to `agents/<defaultAgent>/AGENT.md`.
3. Read the agent's AGENT.md file.
4. Adopt the agent's Identity, Conduct, and Output sections for the remainder of the conversation.
5. If the agent extends a parent, read the parent first and layer the child's overrides on top.
6. Respond to the user's message in character.

### 3. Documentation — `CLAUDE.md`

Add a new decision entry and update the conventions section to document:

- The `defaultAgent` key in `settings.json` and what it does.
- How to change the default agent.
- That `summon-tab` is the skill responsible for activation.

## Files Changed

| File | Change |
|------|--------|
| `settings.json` | Add `defaultAgent` field |
| `skills/summon-tab/SKILL.md` | New file |
| `CLAUDE.md` | New decision + conventions update |

## Decisions

**Why a skill, not a rule.** Rules are always-on and consume context on every message. A skill only activates when Claude recognizes the trigger pattern, which is the right weight for a conversational summon.

**Why `settings.json`, not plugin.json or CLAUDE.md.** `settings.json` is already the home for runtime configuration (the `instructions` array). The default agent is a configurable behavior, not plugin identity (`plugin.json`) or developer guidance (`CLAUDE.md`). CLAUDE.md documents the decision; settings.json is the source of truth.

**Why a path, not a frontmatter flag.** A `default: true` flag on an agent's frontmatter would require scanning all agents to find the default. A direct path in settings.json is simpler, explicit, and O(1).
