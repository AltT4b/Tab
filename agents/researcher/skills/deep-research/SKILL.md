---
name: deep-research
description: "Conduct structured research across web sources, local filesystems, and documentation. Use this skill when the user asks to research a topic, find information, look something up, investigate, or needs factual data gathered from multiple sources."
context: fork
agent: Explore
argument-hint: "[topic]"
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, mcp__exa__web_search_exa, mcp__exa__get_code_context_exa
---

## What This Skill Does

Runs a structured research workflow that combines web search (via Exa MCP), filesystem exploration, and documentation reading to produce concise, sourced findings.

## Research Workflow

### Phase 1: Scope

Research topic: $ARGUMENTS

Before searching anything, clarify the research question:

1. Identify the core question from the topic above (or the user's most recent message if no topic was provided).
2. Break it into 2-4 sub-questions that, answered together, would fully address the request.
3. Determine which source types are relevant:
   - **Web** — for external information, current data, public documentation
   - **Filesystem** — for local code, configs, project structure, internal docs
   - **Both** — most research benefits from checking both

State the sub-questions before proceeding.

### Phase 2: Gather

Execute searches in parallel where possible.

**Web search (Exa MCP):**
- Use the Exa MCP tools to search for relevant web content.
- Start broad, then narrow based on initial results.
- For each useful result, extract the specific relevant data — don't just list URLs.
- If Exa returns thin results, reformulate the query and try again (max 2 refinements).

**Filesystem exploration:**
- Use Glob to find relevant files by pattern.
- Use Grep to search file contents for keywords and patterns.
- Use Read to examine specific files for detailed information.
- Check READMEs, docs directories, config files, and code comments.

**Documentation reading:**
- Use WebFetch to pull and read specific documentation pages.
- Focus on official docs, API references, and specs.

### Phase 3: Analyze

Once data is gathered:

1. **Deduplicate** — merge overlapping findings from different sources.
2. **Cross-reference** — note where sources agree or conflict.
3. **Assess reliability** — primary/official sources outweigh secondhand ones.
4. **Identify gaps** — what sub-questions remain unanswered?

If critical gaps exist and more searching could help, run one more targeted gather pass.

### Phase 4: Deliver

<!-- TODO: Need to refine a format/template research output. -->

Deliver the research in raw form include summaries with section headers so it's clear.

Things to be particularly interested in:

- **Findings**: Bulleted facts with source citations
- **Gaps**: What's missing or uncertain
- **Confidence**: Overall assessment (High/Medium/Low)

Keep it tight. The user asked for facts, not a narrative.
