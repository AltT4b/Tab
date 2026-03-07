---
name: team
description: "Multi-agent team orchestration. Use when the user asks a complex question needing multiple perspectives, says 'get the team on this', 'analyze from multiple angles', 'research this' (any depth), 'investigate', 'dig into', 'look into', or when a question clearly benefits from decomposition into distinct roles."
argument-hint: "[question or topic]"
---

## What This Skill Does

Orchestrates multiple AI agents working together on a complex question. Tab decomposes the problem into roles, dispatches agents in rounds, synthesizes between rounds, and delivers a unified output.

## Workflow

### Phase 0: Scope

Before planning a team, Tab scopes the task interactively. The goal is to avoid wasting agents on a misunderstood problem.

1. **Read the request.** If the user's intent, success criteria, and constraints are all obvious, skip to Phase 1 — don't ask questions you already know the answer to.
2. **Ask 1-3 scoping questions**, one at a time:
   - What does success look like? (if unclear)
   - Are there constraints — timeline, format, audience, tools? (if relevant)
   - What's the scope — exhaustive analysis or quick directional take? (if ambiguous)
3. **Prefer multiple choice** when possible. Open-ended is fine for genuinely open questions.
4. **Move on as soon as you have enough.** Don't over-scope. Two good questions beat five thorough ones.

### Phase 1: Plan

Analyze the user's question. **Start by classifying the task type** — this shapes everything downstream.

#### Task-type heuristics

| Type | Signals | Team shape |
|------|---------|------------|
| **Research** | "research", "look into", "what's the state of", curiosity-driven | Search-heavy roles, citation requirements, 1-2 rounds |
| **Decision-making** | "should I", "compare", "which option", "trade-offs" | Advocates for each option + a critic/synthesizer, 2 rounds |
| **Analysis** | "why is", "how does", "break down", "audit" | Domain specialists + a generalist to check blind spots, 1-2 rounds |
| **Creative** | "brainstorm", "design", "come up with", "explore ideas" | Diverse perspectives, more latitude in briefs, 1-2 rounds |
| **Implementation** | "build", "write", "create", "set up" | Specialists by concern (architecture, edge cases, testing), 1-2 rounds |

Tasks often blend types. Pick the dominant one and let it guide composition, but don't force-fit.

#### Scale to complexity

- **Simple tasks** — single round, 1-3 roles, brief plan.
- **Complex tasks** — multiple rounds, more roles, detailed plan.

#### Propose the plan

1. **Task type** — one line stating what kind of task this is and why.
2. **Team roster** — 1-5 agents, each with a role name, a one-line brief describing their angle, and optionally a Skills field listing capabilities it needs (e.g., `web search`, `coding standards`). Roles without a Skills field work from reasoning alone.
3. **Round structure** — what each round investigates (default 2 rounds, max 4).

#### Example compositions

**"Should we use Postgres or SQLite for this project?"** (Decision-making)
- Round 1: Postgres Advocate, SQLite Advocate, Requirements Analyst
- Round 2: Devil's Advocate (stress-tests the emerging winner)

**"Research the current state of WebAssembly outside the browser"** (Research)
- Round 1: Industry Surveyor (`web search`), Technical Analyst, Use-Case Mapper

**"Design a notification system for our app"** (Creative + Implementation)
- Round 1: UX Designer, Systems Architect, Prior Art Researcher (`web search`)
- Round 2: Edge Case Analyst (informed by Round 1)

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
