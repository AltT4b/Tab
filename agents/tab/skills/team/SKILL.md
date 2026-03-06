---
name: team
description: "Multi-agent team orchestration. Use when the user asks a complex question needing multiple perspectives, says 'get the team on this', 'analyze from multiple angles', 'research this' (any depth), 'investigate', 'dig into', 'look into', or when a question clearly benefits from decomposition into distinct roles."
argument-hint: "[question or topic]"
---

## What This Skill Does

Orchestrates multiple AI agents working together on a complex question. Tab decomposes the problem into roles, dispatches agents in rounds, synthesizes between rounds, and delivers a unified output. This is a subagent skill.

## Workflow

### Phase 1: Plan

Analyze the user's question. Propose a plan with:

1. **Team roster** — 1-5 agents, each with a role name, archetype (or "custom"), and a one-line brief describing their angle
2. **Round structure** — what each round investigates (default 2 rounds, max 4)

Present the plan and wait for user approval. Adjust if they request changes.

**Lightweight mode:** If the question is simple and fact-finding only (e.g., "research X"), plan a single round with Researcher agents. Still present the plan, but keep it brief.

### Phase 2: Execute

After approval, run autonomously:

1. **Create run directory.** Generate a short run ID (topic slug + date, e.g., `crispr-ethics-20260305`). Create `.tab/team/<run-id>/`.

2. **For each round:**
   a. Spawn all agents in the round in parallel via the Agent tool.
   b. Each agent writes its output to `.tab/team/<run-id>/round-<n>/<role-name>.md`.
   c. Post a short status update to conversation: what was found, what gaps or conflicts emerged, what the next round will target.

3. **Between rounds — curate context for the next wave.**
   - Read the prior round's output files.
   - Extract only the findings relevant to each next-round agent's specific role.
   - Do NOT forward full reports. Each agent gets a brief (under 500 words) of prior context relevant to its assignment.

### Phase 3: Deliver

1. Read all output files from `.tab/team/<run-id>/`.
2. Write a final synthesis to `.tab/team/<run-id>/synthesis.md`.
3. Present the synthesis in conversation in Tab's voice.

## Agent Briefing Template

Every agent receives instructions in this format:

```
You are a [role name] on a research team. Your task: [one-line brief].

[If archetype has skills, inject skill instructions here.]

[If Round 2+, inject curated context from prior rounds here — max 500 words.]

Rules:
- Stay focused on your assigned angle. Do not drift into other agents' territory.
- Be specific. Use evidence, examples, and concrete details over generalities.
- If you cannot find sufficient information, say so clearly. Do not fabricate.

Output:
- Write your findings to: [file path]
- Structure as: key findings (bulleted), open questions, and (if applicable) a references section with URLs.
- Keep output under 1000 words.
```

The 1000-word output cap per agent keeps file sizes manageable and forces conciseness.

## Role Archetypes

Tab picks from these or invents custom roles. Each archetype has a fixed skill set.

### Researcher
**Skills:** research (Exa MCP)
**Purpose:** Evidence gathering with source evaluation and citations.
**Skill instructions injected into agent brief:**

> Use Exa MCP tools exclusively for all searches. Do not use WebSearch.
> Search iteratively — start broad, then refine. Run at least 2-3 searches.
> Evaluate every source for primacy (prefer primary sources), recency (flag anything older than 2 years), authority (academic/institutional > blogs), and cross-referencing (note single-sourced claims).
> Record full citations: title, author/org, URL, date.
> Do not fabricate any information.

**Prerequisite:** Before dispatching any Researcher agent, verify Exa MCP tools are available. If not, tell the user: "I need Exa MCP for research roles — it's not available right now. I can still run the team with non-research roles, or you can check your MCP config."

### Devil's Advocate
**Skills:** none
**Purpose:** Argues against the emerging consensus. Only used in Round 2+ since it needs prior findings to push back on.

### Technical Analyst
**Skills:** none
**Purpose:** Evaluates architecture, feasibility, tradeoffs, implementation complexity.

### User Advocate
**Skills:** none
**Purpose:** Considers end-user experience, needs, pain points, accessibility.

### Strategist
**Skills:** none
**Purpose:** Big-picture positioning, market dynamics, timing, competitive landscape.

### Critic
**Skills:** none
**Purpose:** Reviews prior round output for weak reasoning, unsupported claims, logical gaps. Only used in Round 2+.

## Constraints

- Default: 2 rounds. Hard cap: 4 rounds.
- Max 5 agents per round.
- Exa MCP required for Researcher archetype only.
- Agent output cap: 1000 words per agent.
- Between-round briefs: max 500 words per agent.
- All file output goes to `.tab/team/`. Never dump raw agent reports into conversation.
