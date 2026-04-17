---
name: hey-tab
description: "Print setup instructions for MCPs that Tab uses. Use when the user invokes /hey-tab."
---

# Hey Tab

Prints the exact commands a user needs to run to configure MCPs that Tab works well with. No magic — just copy-paste-ready `claude mcp add` one-liners.

## Trigger

**When to activate:**
- User invokes `/hey-tab`

**When NOT to activate:**
- User asks about Tab's capabilities or features → just answer directly
- User asks how to configure MCPs in general → that's a different conversation

## Behavior

When the user runs `/hey-tab`, print the following block exactly:

---

**MCPs that Tab likes to use:**

These are optional — Tab works fine without them. But they unlock web search, research, and fetching capabilities that make several skills (like `/teach`) significantly better.

### Exa

Web search and content fetching.

```bash
claude mcp add --scope user --transport http exa https://mcp.exa.ai/mcp
```

---

That's it. Print the block above and nothing else. Don't paraphrase, don't add commentary, don't offer to run the commands.

## Constraints

- **Print exactly.** No rewording, no additional context, no offers to help.
- **One and done.** The skill completes after printing the block. No follow-up.
