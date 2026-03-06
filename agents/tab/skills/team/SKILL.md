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

1. **Team roster** — 1-5 agents, each with a role name, a one-line brief describing their angle, and optionally a Skills field
2. **Round structure** — what each round investigates (default 2 rounds, max 4)

Present the plan and wait for user approval. Adjust if they request changes.

**Lightweight mode:** If the question is simple and fact-finding only (e.g., "research X"), plan a single round with research-focused roles. Still present the plan, but keep it brief.

### Phase 2: Execute

After approval, run autonomously:

1. **Check available tools.** If any roles declare capabilities in their Skills field, check the environment for tools that satisfy them. If a required capability can't be resolved, tell the user — offer to adjust the plan or ask them to check their tool config.

2. **Create run directory.** Generate a short run ID (topic slug + date, e.g., `crispr-ethics-20260305`). Create `.tab/team/<run-id>/`.

3. **For each round:**
   a. Spawn all agents in the round in parallel via the Agent tool.
   b. Each agent writes its output to `.tab/team/<run-id>/round-<n>/<role-name>.md`.
   c. Post a short status update to conversation: what was found, what gaps or conflicts emerged, what the next round will target.

4. **Between rounds — curate context for the next wave.**
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

[If role has skills, inject resolved tool/context instructions here.]

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

## Roles

Tab invents roles at planning time based on the question. Each role gets a name, a one-line purpose, and optionally a **Skills** field declaring capabilities it needs.

**How Skills works:** The Skills field describes *capabilities* the role needs, not specific tools. Skills resolve to two things:

- **Tools** (e.g., `web search`) — Tab checks the environment, finds available tools, passes them to the agent.
- **Context** (e.g., `coding standards`) — Tab loads a skill file and injects its instructions into the agent brief.

When a role has no Skills field, the agent works from reasoning alone. See the team skill design doc for full details on archetypes, when to codify them, and the capability/standards distinction.

**No predefined archetypes yet.** Tab creates custom roles for each task. Archetypes will be codified when specific roles prove themselves through repeated use.

## Constraints

- Default: 2 rounds. Hard cap: 4 rounds.
- Max 5 agents per round.
- Any role declaring a capability in its Skills field requires Tab to verify the tools are available before dispatch.
- Agent output cap: 1000 words per agent.
- Between-round briefs: max 500 words per agent.
- All file output goes to `.tab/team/`. Never dump raw agent reports into conversation.
