---
name: team
description: "Multi-agent team orchestration. Use when the user asks a complex question needing multiple perspectives, says 'get the team on this', 'analyze from multiple angles', 'research this' (any depth), 'investigate', 'dig into', 'look into', or when a question clearly benefits from decomposition into distinct roles."
argument-hint: "[question or topic]"
---

## What This Skill Does

Orchestrates multiple AI agents working together on a complex question. Tab decomposes the problem into roles, dispatches agents in rounds, synthesizes between rounds, and delivers a unified output.

## Workflow

### Phase 1: Plan

Analyze the user's question. Scale the plan to match the complexity:

- **Simple questions** (e.g., "research X") — single round, fewer roles, brief plan.
- **Complex questions** (e.g., multi-faceted analysis, decision-making) — multiple rounds, more roles, detailed plan.

Propose:

1. **Team roster** — 1-5 agents, each with a role name, a one-line brief describing their angle, and optionally a Skills field listing capabilities it needs (e.g., `web search`, `coding standards`). Roles without a Skills field work from reasoning alone.
2. **Round structure** — what each round investigates (default 2 rounds, max 4)

Present the plan and wait for user approval. Adjust if they request changes.

### Phase 2: Execute

After approval, run autonomously:

1. **Check available tools.** If any roles declare capabilities in their Skills field, check the environment for tools that satisfy them. If a required capability can't be resolved, tell the user — offer to adjust the plan or ask them to check their tool config.

2. **Load archetypes.** Read `./archetypes/registry.md` for the list of available archetypes. If any match planned roles, load their definition files and use their skill instructions when briefing those agents. If none match, all roles are custom — Tab briefs them from scratch.

3. **Create run directory.** Generate a short run ID (topic slug + date, e.g., `crispr-ethics-20260305`). Create `.tab/team/<run-id>/`.

4. **For each round:**
   a. Spawn all agents in the round in parallel.
   b. Each agent writes its output to `.tab/team/<run-id>/round-<n>/<role-name>.md`.
   c. Post a short status update to conversation: what was found, what gaps or conflicts emerged, what the next round will target.

5. **Between rounds — curate context for the next wave.**
   - Read the prior round's output files.
   - Extract only the findings relevant to each next-round agent's specific role.
   - Do NOT forward full reports. Each agent gets a brief (under 500 words) of prior context relevant to its assignment.

### Phase 3: Deliver

1. Read all output files from `.tab/team/<run-id>/`.
2. Write a final synthesis to `.tab/team/<run-id>/synthesis.md`.
3. Present the synthesis in conversation in Tab's voice.

## Agent Briefing

Every agent receives:

1. **Identity and task** — role name and one-line brief.
2. **Skills** (if any) — resolved tool access and/or context instructions.
3. **Prior context** (if Round 2+) — curated findings from earlier rounds, max 500 words.
4. **Rules** — stay focused on your angle, be specific, don't fabricate.
5. **Output instructions** — file path, structure guidance, and a 1000-word cap.

Tab adapts the structure and tone of each brief to the task. Research agents get citation requirements. Creative agents get more latitude. Analytical agents get structured output formats. The constants are: one role per agent, output to file, max 1000 words.

## Constraints

- Hard cap: 4 rounds.
- Never dump raw agent reports into conversation. All output goes to `.tab/team/`.
