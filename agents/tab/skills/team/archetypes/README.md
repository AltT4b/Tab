# Archetypes

Archetypes are reusable role definitions that have earned codification through repeated use. Each archetype lives in its own file in this directory (e.g., `researcher.md`).

## When to Create an Archetype

- Tab keeps reinventing the same role with the same skills across multiple unrelated tasks.
- The instructions are non-obvious — a methodology that benefits from being written down once (e.g., "search iteratively, evaluate source primacy, cross-reference claims, cite everything").
- Getting it wrong degrades the whole team's output.

Don't create an archetype when the role has only come up once, the instructions are just "be good at X," or you're guessing at what might be useful someday.

## Archetype Format

Each archetype file has three parts:

1. **Purpose** — one line. What this role does on a team.
2. **Skills** — capabilities it needs. Tab resolves these before dispatch.
3. **Skill instructions** — concise imperative instructions (under 10 lines) injected into the agent brief. These are the soul of the archetype — they answer *what does this agent do differently from one that just got a one-line brief?* If the instructions are getting long, the role is probably too broad — split it.

## Skills Resolution

The Skills field describes *what* a role needs, not *which tool* provides it. This keeps archetypes portable across environments. Skills resolve to two distinct things:

1. **Capabilities** (e.g., `web search`, `coding`) — resolve to **tools**. Tab checks the environment for available tools that satisfy the capability and passes them to the agent.
2. **Standards** (e.g., `coding standards`) — resolve to **context**. Tab loads a skill file containing preferences, conventions, and guardrails, then injects those instructions into the agent brief.

Both flow through the same Skills field. Tab distinguishes them at resolution time. A role can require both — e.g., a Developer role might need `coding` (tools) and `coding standards` (context).

## How Archetypes Are Used

When briefing an agent using an archetype, Tab appends the archetype's skill instructions to the standard briefing template. The archetype instructions replace the generic rules section — they are the role's methodology.
