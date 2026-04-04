# Agent Conventions

Shared rules at the seams. Everything in the middle is agent-specific.

## Agent Types

Two types, different interaction models:

- **Conversational** (manager, bugfixer) — talk to the user. Manager orchestrates via MCP and the Agent tool; bugfixer pair-programs in the foreground.
- **Headless** (planner, qa, documenter, implementer, coordinator) — run in background via `run_in_background: true`. Never talk to the user. Receive context from the caller, do work, return structured results.

Both types use the Tab for Projects MCP. Both follow the conventions below.

## Shared Vocabulary

| Term | Meaning | Applies to |
|---|---|---|
| **Load Context** | MCP-reading phase — pull project, tasks, and documents before doing work. | All agents |
| **Return** | Structured output sent back to the caller. | Headless agents |

Agent-specific operations use agent-specific names. The planner's "Research the Codebase" is exploration; QA's "Inspect the Actual Work" is verification. Don't flatten them.

## Boundaries

Every agent declares what it does NOT do.

- Headless agents: explicit `## Boundaries` section at the end.
- Conversational agents: boundaries woven into the prompt where they carry the most weight (e.g., manager's hard rule at the top).

Boundaries are short, declarative, and unnegotiated. If the agent is tempted to do X, the answer is no — hand it off.

## MCP Integration

All agents share the same MCP tools: `list_projects`, `get_project`, `create_project`, `update_project`, `list_tasks`, `get_task`, `create_task`, `update_task`, `list_documents`, `get_document`, `create_document`, `update_document`. Batch when creating or updating multiple items. Default listing: `todo` and `in_progress` only unless the user asks otherwise. Documents are independent entities linked to projects via `attach_documents` on `update_project`.

## Skill Frontmatter

Skills live in `skills/<skill-name>/SKILL.md`. YAML frontmatter fields:

| Field | Required | Description |
|---|---|---|
| `name` | yes | Slash-command name (e.g., `refinement`) |
| `description` | yes | One-line summary shown in skill listings |
| `argument-hint` | yes | Placeholder shown after the command (e.g., `[project-name]`) |
