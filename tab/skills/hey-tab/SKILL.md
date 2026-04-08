---
name: hey-tab
description: "Print setup instructions for MCPs that Tab uses. Use when the user invokes /hey-tab."
---

## What This Is

Prints the exact commands a user needs to run to configure MCPs that Tab works well with. No magic — just copy-paste-ready `claude mcp add` one-liners.

This skill activates **only** when the user runs `/hey-tab`.

## Instructions

When the user runs `/hey-tab`, print the following exactly:

---

**MCPs that Tab likes to use:**

These are optional — Tab works fine without them. But they unlock web search, research, and fetching capabilities that make several skills (like `/teach`) significantly better.

### Exa

Web search and content fetching.

```bash
claude mcp add --transport http exa https://mcp.exa.ai/mcp
```

---

That's it. Print the block above and nothing else. Don't paraphrase, don't add commentary, don't offer to run the commands.
