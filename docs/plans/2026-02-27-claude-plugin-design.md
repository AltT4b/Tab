# Tab Claude Plugin Design

## Goal

Make Tab installable as a Claude Code plugin by adding the required `.claude-plugin/plugin.json` metadata file.

## Decision

Tab is a single plugin (not a marketplace). Installing it gives users the full repo contents: `agents/`, `skills/`, `commands/`, and `rules/`. The existing directory layout already matches the Claude Code plugin spec.

## Change

Add one file: `.claude-plugin/plugin.json`

```json
{
  "name": "tab",
  "description": "A framework for defining Claude-based AI agents as file-system primitives, using AGENT.md for configuration and behavioral instructions.",
  "version": "0.1.0",
  "author": {
    "name": "AltT4b"
  },
  "homepage": "https://github.com/AltT4b/Tab",
  "repository": "https://github.com/AltT4b/Tab",
  "license": "MIT",
  "keywords": ["agents", "framework", "claude-code"]
}
```

## Out of Scope

- Marketplace listing (can submit to superpowers-marketplace or Anthropic's official directory later)
- A `tab` skill explaining framework conventions (good follow-on)
