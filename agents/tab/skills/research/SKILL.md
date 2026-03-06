---
name: research
description: "Multi-agent research skill. Use when the user asks to research a topic, investigate something, find information, look something up, needs facts or evidence on a subject, or says things like 'research this', 'dig into', 'find out about', 'what do we know about', or 'look into'."
argument-hint: "[detail:brief|detailed] [topic]"
---

## What This Skill Does

Spawns one or more researcher subagents to investigate a topic using Exa MCP. Each agent explores a different facet of the query, evaluates source quality, and returns cited findings. Tab then synthesizes everything into a unified research brief.

This is a subagent skill — Tab dispatches researcher agents via the Agent tool and synthesizes their results in his own voice.

## Prerequisites

**Exa MCP is required.** Before spawning any researcher agents, verify that Exa MCP tools are available. If Exa is not available, stop immediately and tell the user:

> "I need Exa MCP to run research — it's not available in your environment right now. Check your MCP server config and try again."

Do not fall back to WebSearch. Do not proceed without Exa.

## Inputs

- **Topic**: The subject to research (required). Taken from `$ARGUMENTS`.
- **Detail level**: `brief` or `detailed` (optional, defaults to `detailed`).
  - `brief`: Narrative summary + up to 3 conclusions. Aim for ~300-500 words.
  - `detailed`: Full narrative + as many conclusions as the evidence supports. No hard cap — let the research dictate length.

## Workflow

### Step 1: Decompose the Query

Analyze the user's topic. Break it into distinct subtopics or research angles. Decide how many researcher agents to spawn based on complexity:

- **Simple/focused query** (e.g., "What is CRISPR?"): 1 agent
- **Moderate query** (e.g., "How is CRISPR being used in agriculture?"): 2-3 agents, each covering a different angle
- **Complex/multi-faceted query** (e.g., "Compare CRISPR approaches across agriculture, medicine, and ethics"): 3-5 agents, one per facet

State your decomposition plan before dispatching.

### Step 2: Dispatch Researcher Agents

Spawn each researcher agent via the Agent tool. All agents run in parallel when possible. Each agent receives these instructions:

---

**You are a research agent. Your task is to investigate a specific angle of a broader topic.**

**Your assigned angle:** [specific subtopic]

**Rules:**
1. **Use Exa MCP tools exclusively** for all searches. Do not use WebSearch.
2. **Search iteratively.** Start broad, then refine based on what you find. Run at least 2-3 searches per angle.
3. **Evaluate every source** using these criteria:
   - **Primacy**: Prefer primary sources (studies, official docs, direct reporting) over aggregators and summaries.
   - **Recency**: Prefer newer information. Flag anything older than 2 years as potentially outdated.
   - **Authority**: Weight domain expertise — academic papers, established institutions, recognized experts rank higher than blog posts or forums.
   - **Cross-referencing**: A claim supported by 2+ independent sources is stronger than a single-source claim. Note when a finding is single-sourced.
4. **Record full citations** for every fact: title, author/org (if available), URL, and publication date (if available).
5. **Do not fabricate** any information. If you can't find evidence, say so.

**Output format:**
Return your findings as a structured list:
- **Key findings**: Each finding as a bullet with inline citation markers `[n]`.
- **Source quality notes**: Flag any weak, outdated, or single-sourced claims.
- **References**: Numbered list with full citation details.

---

### Step 3: Synthesize Results

Once all agents return, combine their findings:

1. **Deduplicate**: Merge overlapping findings across agents.
2. **Cross-reference**: Strengthen claims that multiple agents found independently. Downgrade single-source claims.
3. **Resolve conflicts**: If agents found contradictory information, note the disagreement and present both sides.
4. **Unify the reference list**: Merge all citations into a single numbered list. Re-number inline markers to match.

### Step 4: Produce Output

Structure the final output as follows:

```
## Research: [Topic]

[Narrative summary — a flowing, readable overview of what was found. Uses inline citation markers like [1], [2]. Length scales with detail level.]

### Conclusions

**1. [Conclusion statement]** `confidence: high|medium|low`
- [Supporting fact with citation marker] [1]
- [Supporting fact with citation marker] [2]
- [Quality note if applicable — e.g., "Single-sourced" or "Sources disagree on exact figures"]

**2. [Conclusion statement]** `confidence: high|medium|low`
- ...

[Repeat as needed]

### References

[1] [Author/Org]. "[Title]." *[Source]*. [Date]. [URL]
[2] ...
```

**Confidence tagging rules:**
- **High**: Claim supported by 2+ independent, authoritative, recent sources.
- **Medium**: Supported by one strong source, or multiple weaker sources. Note why.
- **Low**: Single-sourced, outdated, or from a low-authority source. Explain the limitation.

When sources disagree or evidence is thin, say so directly in the conclusion's supporting facts. Don't hide uncertainty.
