---
name: create-rule
description: "Use when creating a new Tab rule — writes the rule markdown file with correct structure and placement."
---

# Creating a Tab Rule

## When to use this skill

Invoke this skill whenever you are about to create a new Tab rule from scratch.

## Tab Rule Conventions

**What rules are:** Always-on behavioral guardrails. Rules are loaded automatically — they are never explicitly invoked by users or agents.

**Placement:**
- **Shared** (applies to all agents): `rules/<name>.md`
- **Agent-local** (overrides shared for that agent): `agents/<agent>/rules/<name>.md`

Agent-local rules take precedence over shared rules with the same name.

**Structure:** A single `.md` file (no wrapping directory, unlike skills).

**Naming:** Lowercase, hyphenated (e.g., `no-pii`).

## Workflow

1. Determine the rule name (lowercase-hyphenated).
2. Determine scope: shared (`rules/`) or agent-local (`agents/<agent>/rules/`)?
3. Write the rule `.md` file at the chosen path using the template below.
4. Keep the rule focused and specific — one guardrail per file.
5. Confirm the file is complete before finishing.

## Template

```markdown
# <Rule Name>

[One or two sentences stating the guardrail as a direct behavioral constraint.]

- [Specific constraint]
- [Specific constraint]
```
