# Team Skill Design

## Summary

A skill that orchestrates multiple AI agents working together on a complex question. Tab acts as coordinator — decomposing the problem into roles, dispatching agents in rounds, synthesizing between rounds, and delivering a final unified output.

## Use case

General-purpose. Works for decision-making, deep analysis, creative work, or any problem that benefits from multiple perspectives.

## Workflow

### Phase 1: Plan (requires user approval)

1. Analyze the question
2. Propose a team roster — each agent gets a role name, archetype (or custom), and a one-line brief
3. Propose round structure — what each round aims to accomplish
4. Present plan, wait for approval or adjustments

### Phase 2: Execute (autonomous after approval)

1. Spawn each round's agents in parallel
2. Write each agent's raw output to `.tab/team/<run-id>/round-<n>/<role-name>.md`
3. Between rounds: read results, synthesize, identify gaps/conflicts, brief next-round agents with only the relevant context from prior rounds
4. Post short status updates to conversation between rounds

### Phase 3: Deliver

1. Write final synthesis to `.tab/team/<run-id>/synthesis.md`
2. Present synthesis in conversation in Tab's voice

## Context window efficiency

This skill is designed to keep context windows small:

- **Raw agent output goes to files, not conversation.** Agent reports are written to `.tab/team/` and only selectively referenced. The conversation carries status updates and the final synthesis.
- **Between-round briefs are curated, not dumped.** When briefing Round 2 agents with Round 1 context, Tab extracts only the relevant findings — not the full reports. Each agent gets only what it needs for its specific role.
- **Agents are stateless.** Each agent starts fresh with a focused brief. No agent carries the full history of all prior rounds.
- **Final synthesis reads from files.** Tab reads the `.tab/team/` files to produce the synthesis, keeping the source material out of conversation context.

## Role archetypes

Archetypes are a starter library of reusable roles. Tab picks from these based on the question, or invents custom roles when needed.

Each archetype has a hardcoded `skills` list — skill files whose instructions are injected into the agent's prompt. This makes agent behavior predictable and repeatable.

| Archetype | Skills | Purpose |
|-----------|--------|---------|
| Researcher | `research` | Evidence gathering via Exa, iterative search, source evaluation, citations |
| Devil's Advocate | *(none)* | Argues against the emerging consensus |
| Technical Analyst | *(none)* | Evaluates architecture, feasibility, tradeoffs |
| User Advocate | *(none)* | Considers UX, user needs, accessibility |
| Strategist | *(none)* | Big-picture positioning, market, timing |
| Critic | *(none)* | Reviews prior round output for weak reasoning |

Skills attach to archetypes in the archetype definition. Tab cannot add or swap skills at runtime.

> **Decision: hardcoded skill binding (option A).** We chose fixed skill-to-archetype binding over flexible or required+optional models. This keeps agent behavior predictable and debuggable. If this becomes limiting, evolve to a required + optional model — but only when a concrete case demands it.

## Constraints

- **Rounds:** default 2, hard cap 4
- **Agents per round:** max 5
- **Exa MCP:** required for Researcher archetype (check before dispatching, warn if unavailable)

## Replaces

The standalone `research` skill is removed. "Researcher" becomes an archetype within the team skill. When someone just says "research X," Tab runs a lightweight team — one round, Researcher roles only.

## User control model

Plan-and-approve. Tab proposes the team roster and round plan. User approves or adjusts. Execution is autonomous after approval.

> **Decision: plan-and-approve (option B).** Fully autonomous risks bad decompositions the user can't correct. Interactive-throughout is tedious. Plan-and-approve gives the user the steering wheel at the moment it matters most.

## Output destination

File-based. Raw agent reports go to `.tab/team/`. Status updates go to conversation. Final synthesis goes to both.

> **Decision: file output (option B).** Keeps conversation context small. Raw reports are reference material — available in files if the user wants to dig in, but not cluttering the conversation.
