---
name: recall
description: "Store and retrieve semantic memories using the recall CLI. Use when you want to remember something for later, or find relevant context from past decisions, conventions, or knowledge."
argument-hint: "[store|search] <text>"
---

# recall — Semantic Memory

You have access to a vector database via the `recall` CLI. This gives you persistent, semantic memory — you can store information and retrieve it by meaning, not just keywords.

## When to Use

**Store** when you encounter something worth remembering across sessions:
- Architectural decisions and their rationale
- Project conventions and patterns
- Bug investigations and root causes
- User preferences and working style
- Important context that would be lost between sessions

**Search** when you need context that might exist from a prior session:
- Before making a design decision, check if one was already made
- When working on a subsystem, search for related conventions or past issues
- When the user asks "didn't we already discuss X?" — search for it

## Commands

### Store a memory

```bash
vector-memes store "the thing you want to remember" --meta '{"type": "decision", "topic": "auth"}'
```

Always include metadata. Useful keys:
- `type`: decision, convention, bug, context, preference
- `topic`: the area it relates to (auth, database, api, testing, etc.)
- `source`: where this came from (conversation, code-review, debugging)

### Search for memories

```bash
vector-memes search "what you're looking for" --limit 5
```

Use `--threshold 0.7` to filter out weak matches.

### Check what's stored

```bash
vector-memes count
```

## Principles

- **Store decisions, not facts.** "We chose X because Y" is valuable. "X exists" is not — that's what code search is for.
- **Search before you assume.** If there might be prior context, check. It takes milliseconds.
- **Be specific in queries.** "How does auth work" retrieves better than "auth."
- **Don't over-store.** Not every conversation turn is worth remembering. Store what would change behavior in a future session.
