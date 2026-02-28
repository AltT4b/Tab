---
name: research
description: "Use when gathering, comparing, or synthesizing information from any source — web, codebase, or documentation — on any topic."
---

# Research

## Overview

Research is a general-purpose knowledge-gathering skill. It classifies each research request by complexity, routes to the right tools, and delivers findings with cited sources.

Research categories:
- **External** — web search for tools, trends, entities, facts
- **Internal** — codebase archaeology, pattern discovery, architecture understanding
- **Hybrid** — comparing internal implementation against external best practices
- **Documentation** — synthesizing local or remote docs into actionable understanding

Do not trigger for questions answerable from existing knowledge without verification, or for simple file reads that don't require synthesis. Do not trigger for Tab-specific improvement research — the `bootstrap` skill handles that.

## Classification

Before executing any research, classify the request into a tier:

| Signal | Tier | Tools |
|--------|------|-------|
| Simple factual question, single-source answer likely | **Quick** | WebSearch (external) or Grep/Read (internal) |
| Comparison, multiple options, "what are the approaches" | **Explore** | Multi-query WebSearch + WebFetch, or multi-file Grep/Read |
| Entity discovery, landscape mapping, deep multi-source synthesis | **Deep** | Exa websets (if available) + WebSearch + codebase tools |

**How to classify:**
- If the answer fits in a paragraph and one source suffices → Quick
- If the user asks to compare, evaluate, or survey options → Explore
- If the question requires discovering entities, mapping a landscape, or synthesizing 5+ sources → Deep

State the chosen tier before proceeding. Example: "This is an **Explore**-tier question — I'll compare options from multiple sources."

## Workflow

### Step 1: Understand the question

Restate the research question in one sentence. Identify:
- What is being asked
- What kind of answer is expected (fact, comparison, landscape, recommendation)
- Whether sources are internal, external, or both

If the question is ambiguous, ask one clarifying question before proceeding. Do not ask multiple questions.

### Step 2: Classify tier

Apply the classification table above. State the tier.

### Step 3: Execute research

#### Quick tier

- **External:** Run a single WebSearch query. Optionally WebFetch one result for detail.
- **Internal:** Grep or Glob for relevant code. Read key files.
- Respond conversationally with the answer and its source.

#### Explore tier

- **External:** Run 2-4 WebSearch queries from different angles. WebFetch the top 2-3 results for depth.
- **Internal:** Grep across the codebase with multiple patterns. Read files that surface across queries.
- **Hybrid:** Run both external and internal searches, then cross-reference.
- Note contradictions or disagreements between sources.
- Respond conversationally with a structured comparison and sources.

#### Deep tier

1. **Check Exa availability.** Attempt to call `list_websets`. If the tool exists and responds, Exa is available.

2. **If Exa is available:**
   - Create a webset with a descriptive name and the research query.
   - Add search criteria that match the research constraints.
   - Add enrichments for the specific data points needed (e.g., "founding year", "primary technology", "employee count").
   - Wait for the search to complete (poll with `get_search`).
   - Retrieve items with `list_webset_items`.
   - Supplement with WebSearch/WebFetch for context the webset doesn't capture.

3. **If Exa is not available:**
   - Fan out 4-6 WebSearch queries covering different facets of the question.
   - WebFetch the most relevant results (up to 5-6 pages).
   - Use the Agent tool to parallelize exploration where queries are independent.

4. **Internal component:** If the question has a codebase dimension, run Grep/Glob/Read in parallel with web research.

5. **Save a report** to `docs/research/YYYY-MM-DD-<topic>.md`. Create the directory if it does not exist.

### Step 4: Synthesize

- **Quick/Explore:** Respond in-chat. Organize findings by theme, not by source.
- **Deep:** Write a structured report (see Output Format below). Also provide a brief in-chat summary.

### Step 5: Cite sources

Every factual claim must reference its source:
- External: URL
- Internal: file path with line reference (e.g., `src/auth.ts:45`)
- Never fabricate references. If a claim cannot be sourced, state that explicitly.

## Output Format

For **Deep** tier research, save a report to `docs/research/YYYY-MM-DD-<topic>.md` using this structure:

    # Research: <Topic>

    **Date:** YYYY-MM-DD
    **Tier:** Deep
    **Tools used:** [List of tools used — e.g., Exa websets, WebSearch, WebFetch, Grep]

    ## Question

    [The research question, restated clearly]

    ## Methodology

    [What was searched, which tools, how many queries, what criteria]

    ## Findings

    ### [Theme 1]

    [Findings organized by theme, not by source]

    ### [Theme 2]

    ...

    ## Sources

    - [Source 1 title](URL) — [one-line note on what it contributed]
    - `path/to/file.ts:line` — [one-line note]

    ## Recommendations

    [If applicable — actionable next steps based on findings]

For **Quick** and **Explore** tiers, respond conversationally. Include a "Sources:" section at the end with links or file paths.

## Error Handling

- **Exa unavailable:** Fall back to multi-query WebSearch + WebFetch. Do not show an error to the user. Note in methodology which tools were actually used.
- **No results found:** Report what was searched and that nothing matched. Suggest 2-3 reformulated queries the user could try.
- **Ambiguous question:** Ask exactly one clarifying question before starting research. Do not ask multiple questions at once.
- **Scope creep:** If research uncovers a much larger topic than expected, summarize what was found so far and ask the user if they want to continue deeper. Do not spiral.
- **Webset cleanup:** For deep research, create fresh websets. Do not reuse existing websets from prior research sessions to avoid stale data.
