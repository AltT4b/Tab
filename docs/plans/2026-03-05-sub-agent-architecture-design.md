# Sub-Agent Architecture Design

**Date:** 2026-03-05
**Status:** Approved

## Problem

Tab's variant agents (researcher, advisor) are currently personality overlays the user triggers directly. This creates a fragmented experience — the user has to know which variant to ask for, and Tab's identity shifts depending on the variant.

## Decision

Redesign variants as internal sub-agents that Tab dispatches autonomously. Tab is the sole user-facing personality. Sub-agents are invisible capabilities Tab uses via Claude Code's Agent tool.

## Design

### Tab's base AGENT.md gets a `## Sub-Agents` section

A registry table listing each sub-agent's name, path, and one-line capability description. Tab reads this to know what he can dispatch. The section is self-contained so it can be extracted to a separate manifest file later.

### Sub-agent AGENT.md files become capability specs

Each sub-agent definition includes:

- **Capability** — what this agent does
- **Behavior** — how it operates (rules, constraints)
- **Output** — what it returns to Tab (structured data/findings, not user-facing prose)

No personality, no identity, no `extends:` field, no Additional Identity/Output sections. These are tools, not personas.

### summon-tab skill simplifies

Remove the variant matching table and variant-loading steps. The skill loads the base agent and becomes Tab. Tab handles all dispatch decisions internally.

### Sub-agent dispatch via Agent tool

Tab uses Claude Code's Agent tool to spawn sub-agents as real sub-processes. Tab synthesizes results and presents them in his own voice. The user never interacts with or sees sub-agents directly.

### Tab decides when to dispatch

No explicit trigger rules. Tab autonomously judges whether a request benefits from a sub-agent based on his knowledge of their capabilities.

## File Changes

| File | Action |
|------|--------|
| `agents/base/AGENT.md` | Add `## Sub-Agents` registry section |
| `agents/advisor/AGENT.md` | Rewrite as capability spec |
| `agents/researcher/AGENT.md` | Rewrite as capability spec |
| `skills/summon-tab/SKILL.md` | Remove variant matching, simplify to base-only |

## Future: Extract to Manifest (Approach 2)

When the registry outgrows the base AGENT.md:

1. Cut the `## Sub-Agents` section into `agents/REGISTRY.md`
2. Replace it with a one-liner reference to the registry file
3. Nothing else changes

The registry section is written to be self-contained specifically to make this extraction trivial.
