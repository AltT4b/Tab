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

Archetypes are reusable role templates with predefined skills and instructions. Tab can use archetypes or invent custom roles at planning time. **No archetypes are predefined yet.** They should emerge from repeated use, not speculation.

### When to create an archetype

Codify a role as an archetype when:

- **Tab keeps reinventing it.** If the same role with the same skills and similar instructions shows up across multiple unrelated tasks, it's earned a spot. One-off or domain-specific roles should stay custom.
- **The instructions are non-obvious.** "Argue against the consensus" is simple enough that Tab can invent it on the fly. "Search iteratively, evaluate source primacy, cross-reference claims, cite everything" is a methodology — that benefits from being written down once and reused.
- **Getting it wrong has a cost.** If sloppy execution of the role degrades the whole team's output (e.g., a researcher returning uncited claims), the guardrails deserve codification.

Don't create an archetype when:

- The role has only come up once
- The instructions are just "be good at X" — Tab already knows how to brief an agent for that
- You're guessing at what might be useful someday

### What makes a good archetype

An archetype definition has three parts:

1. **Purpose** — one line. What this role does on a team.
2. **Skills** — capabilities the role needs. Tab resolves these before dispatch.
3. **Skill instructions** — the imperative instructions injected into the agent's brief. These should be concise (under 10 lines), specific, and actionable. If the instructions are getting long, the role is probably too broad — split it.

The skill instructions are the soul of the archetype. They turn a generic agent into a specialist. They should answer: *what does this agent do differently from an agent that just got a one-line brief?*

### Two kinds of skills

The Skills field resolves to two distinct things depending on what it references:

1. **Capabilities** (e.g., `web search`, `coding`) — Tab resolves these to **tools**. Checks the environment for available tools that satisfy the capability, passes them to the agent. The agent gets access to do things.

2. **Standards** (e.g., `coding standards`) — Tab resolves these to **context**. Loads a skill file containing preferences, conventions, and guardrails, then injects those instructions into the agent brief. The agent gets informed about *how* to do things.

Both flow through the same Skills field. Tab distinguishes them at resolution time. An archetype can require both — e.g., a Developer role might need `coding` (tools) and `coding standards` (context).

> **Decision: skills as capabilities, not tools.** Archetypes declare *what* they need (e.g., `web search`), not *which tool* provides it. Tab checks the environment, resolves capabilities to available tools (Exa MCP, WebSearch, etc.), and passes them to the agent. This keeps archetypes portable — they work regardless of which specific MCP servers are configured. If no tool satisfies a required capability, Tab tells the user before dispatching.

### Archetype registry

*(Empty. Add archetypes here as they earn their place through repeated use.)*

## Constraints

- **Rounds:** default 2, hard cap 4
- **Agents per round:** max 5
- **Search tools:** Researcher archetype requires at least one search tool. Tab checks availability before dispatch.

## Memory and subagents

Memory is Tab's. Subagents never write to `~/.claude/tab/memory/` — Tab handles all memory updates during synthesis.

Tab *does* use his memory to write better agent briefs. User background, preferences, active goals — this context flows through the briefing template, not through granting agents memory access.

> **Future consideration: read-only memory access.** Some roles (e.g., Strategist on a personal goal, User Advocate on preferences) could benefit from reading memory files directly rather than relying on Tab to pre-digest context. If added, this would be a new capability keyword (e.g., `user context`) that Tab resolves by granting read access to specific memory files — never the whole directory. Build this when Tab's briefs are consistently missing context that agents need.

## Replaces

The standalone `research` skill is removed. "Researcher" becomes an archetype within the team skill. When someone just says "research X," Tab runs a lightweight team — one round, Researcher roles only.

## User control model

Plan-and-approve. Tab proposes the team roster and round plan. User approves or adjusts. Execution is autonomous after approval.

> **Decision: plan-and-approve (option B).** Fully autonomous risks bad decompositions the user can't correct. Interactive-throughout is tedious. Plan-and-approve gives the user the steering wheel at the moment it matters most.

## Output destination

File-based. Raw agent reports go to `.tab/team/`. Status updates go to conversation. Final synthesis goes to both.

> **Decision: file output (option B).** Keeps conversation context small. Raw reports are reference material — available in files if the user wants to dig in, but not cluttering the conversation.
