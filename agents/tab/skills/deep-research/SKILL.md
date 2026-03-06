---
name: deep-research
description: "Conduct structured deep research across web sources, local filesystems, and documentation. Use this skill when the user asks to research a topic in depth, investigate thoroughly, or needs comprehensive factual data gathered from multiple sources."
argument-hint: "[topic]"
---

## What This Skill Does

Runs a structured research workflow that combines web search (via Exa MCP), filesystem exploration, and documentation reading to produce concise, sourced findings.

Tab dispatches this skill as a subagent via the Agent tool so it can run an extended research process independently.

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

Structure the output as follows:

### Findings

Organize by sub-question or theme. For each section:
- Use a descriptive header
- Bulleted facts, each with a source citation (URL, file path, or document reference)
- Add brief context for why each finding matters to the research topic

### Conflicts & Gaps

- Note where sources disagree and which source is more credible
- List sub-questions that remain unanswered or partially answered

### Confidence

Rate overall confidence: **High** / **Medium** / **Low**, with a one-line justification.

Keep it tight. The user asked for facts, not a narrative.
