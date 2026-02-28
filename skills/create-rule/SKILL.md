---
name: create-rule
description: "Use when creating a new Tab rule — writes the rule markdown file with correct structure and placement."
---

# Creating a Tab Rule

## When to use this skill

Invoke this skill whenever you are about to create a new Tab rule from scratch.

## Tab Rule Conventions

**What rules are:** Always-on behavioral guardrails. Rules are loaded automatically — they are never explicitly invoked by users or agents.

**Placement:** `rules/<name>/<name>.md`

**Registration:** After creating the rule file, add its path to the `instructions` array in `settings.json` so Claude Code loads it automatically:

```json
{
  "instructions": [
    "rules/<name>/<name>.md"
  ]
}
```

**Structure:** A directory named after the rule, containing a single `.md` file of the same name.

**Naming:** Lowercase, hyphenated (e.g., `no-pii`). The directory and file share the same name.

## Workflow

1. Determine the rule name (lowercase-hyphenated).
2. Determine scope: shared (`rules/`) or agent-local (`agents/<agent>/rules/`)?
3. Create the directory and file: `rules/<name>/<name>.md`
4. Keep the rule focused and specific — one guardrail per file.
5. Add the file path to `settings.json` → `instructions` array.
6. Confirm the file is complete before finishing.

## Template

```markdown
# <Rule Name>

[One or two sentences stating the guardrail as a direct behavioral constraint.]

- [Specific constraint]
- [Specific constraint]
```
