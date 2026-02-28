# Research Skill Design

## Problem

Tab has no general-purpose research capability. The `bootstrap` skill handles Tab-specific improvement research, but there's no skill for gathering, comparing, or synthesizing information from external or internal sources on arbitrary topics.

## Decision

Build a **tiered research skill** that auto-classifies research requests by complexity and routes to the appropriate toolchain. Uses Exa.ai websets for deep structured research when available, falls back gracefully to WebSearch/WebFetch when not.

## Design

### Trigger & Scope

**Name:** `research`
**Location:** `skills/research/SKILL.md`

Triggered when the agent needs to gather, compare, or synthesize information from any source.

Research categories:
- **External** — web search for tools, trends, entities, facts
- **Internal** — codebase archaeology, pattern discovery, architecture understanding
- **Hybrid** — comparing internal implementation against external best practices
- **Documentation** — synthesizing local/remote docs into actionable understanding

Not triggered for questions answerable from the agent's existing knowledge without verification.

### Classification & Routing

The skill classifies every request into a tier before executing:

| Signal | Tier | Toolchain |
|--------|------|-----------|
| Simple factual question, single-source answer expected | Quick | WebSearch or Grep/Read (internal) |
| Comparison, multiple options, "what are the approaches" | Explore | Multi-query WebSearch + WebFetch, or multi-file Grep/Read |
| Entity discovery, landscape mapping, deep synthesis | Deep | Exa websets (if available) + WebSearch + codebase tools |

Exa availability is checked by attempting `list_websets` before deep-tier work. If unavailable, degrades to multi-query WebSearch + WebFetch.

Internal vs external routing: codebase questions use Glob/Grep/Read. External questions use web tools. Hybrid uses both.

### Workflow

1. **Understand the question.** Restate in one sentence. Identify what's being asked, what kind of answer is expected, whether sources are internal/external/both.

2. **Classify tier.** Assign Quick / Explore / Deep based on complexity and scope.

3. **Execute research.**
   - **Quick:** Single WebSearch or Grep/Read. Respond conversationally with answer + source.
   - **Explore:** 2-4 WebSearch queries from different angles, WebFetch top results, or multi-file Grep/Read. Cross-reference findings. Respond conversationally with structured comparison + sources.
   - **Deep:** Check Exa availability. If available, create webset with tailored search criteria and enrichments, poll status, retrieve and synthesize items. If unavailable, fan out 4-6 WebSearch queries + WebFetch + parallel Agent exploration. Save report to `docs/research/YYYY-MM-DD-<topic>.md`.

4. **Synthesize.** Quick/Explore: respond in-chat. Deep: produce structured report with research question, methodology, findings (by theme), sources, and recommendations.

5. **Cite sources.** Every claim backed by a URL or file path. No fabricated references.

### Output

- **Quick/Explore tiers:** Conversational response with inline sources
- **Deep tier:** Saved markdown report at `docs/research/YYYY-MM-DD-<topic>.md` with sections: Research Question, Methodology, Findings, Sources, Recommendations

### Error Handling

- **Exa unavailable:** Graceful fallback to WebSearch/WebFetch. No error to user. Methodology notes which tools were used.
- **No results:** Report what was searched, suggest reformulated queries.
- **Ambiguous question:** Ask one clarifying question before starting.
- **Scope creep:** Summarize what was found, ask if user wants to go deeper.
- **Stale websets:** Create fresh websets for each deep research task.

### Relationship to Bootstrap

- `bootstrap` = research + actionable growth plan for Tab specifically
- `research` = general-purpose knowledge gathering on any topic
- No overlap conflict. `bootstrap` could invoke `research` internally in the future.
