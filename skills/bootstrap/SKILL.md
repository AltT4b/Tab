---
name: bootstrap
description: "Use when planning how to improve or extend Tab — evaluating new capabilities, adopting patterns, or deciding how Tab should grow. Produces actionable plans with concrete steps and outcomes."
---

# Bootstrap

## Overview

Bootstrap researches external tools, frameworks, and Anthropic best practices to produce actionable plans that help Tab grow and become more useful. Each plan has well-defined steps and measurable outcomes.

The goal is not imitation — Tab is building toward a uniquely usable personal assistant. Best practices are strongly preferred, but purposeful deviation is allowed when it serves Tab's vision of usability.

## Workflow

1. **Receive a research direction.** The user provides a topic, tool, pattern, or open question (e.g., "How do other agent frameworks handle memory?", "What can Tab learn from Cursor's UX?").

2. **Research.** Use web search, documentation fetching, and codebase exploration to gather relevant information:
   - Anthropic documentation and Claude Code best practices
   - Comparable tools and frameworks (agent builders, AI assistants, CLI tools)
   - Community patterns and emerging conventions
   - Tab's current state (read existing agents, skills, rules, CLAUDE.md)

3. **Analyze against Tab's context.** For each finding, evaluate:
   - **Relevance:** Does this solve a real gap or friction in Tab?
   - **Alignment:** Does it fit Tab's file-system-primitive architecture?
   - **Best practice conformance:** Is this an Anthropic-recommended pattern? If deviating, articulate why.
   - **Usability impact:** Does this make Tab meaningfully more useful as a personal assistant?

4. **Produce an actionable plan.** Structure the output as a plan with discrete steps. Each step must include:
   - **What:** A concrete action (create a skill, modify CLAUDE.md, add an agent, etc.)
   - **Why:** The problem it solves or the capability it adds
   - **How:** Enough detail to execute without ambiguity
   - **Outcome:** What "done" looks like — observable, testable where possible
   - **Best practice note:** Whether this follows Anthropic conventions or intentionally deviates, and why

5. **Prioritize.** Order steps by impact and dependency. Flag which steps are independent (parallelizable) and which are sequential. Identify quick wins versus longer investments.

6. **Present for review.** Deliver the plan to the user for feedback before any implementation begins. The plan is the deliverable — execution is a separate step.

## Research Principles

- **Primary sources first.** Prefer official documentation over blog posts or opinions.
- **Current over historical.** Anthropic's recommendations evolve quickly. Verify recency.
- **Concrete over abstract.** "Add a memory skill that persists context across sessions" beats "improve memory capabilities."
- **Honest about tradeoffs.** If a best practice conflicts with Tab's goals, say so and recommend a path.
- **Scope awareness.** Tab is a plugin framework, not a full application. Plans should respect that boundary.

## Output Format

```markdown
# Bootstrap Plan: <Topic>

## Research Summary

[2-3 paragraph synthesis of findings]

## Recommendations

### 1. <Step Title>

- **What:** [Concrete action]
- **Why:** [Problem or opportunity]
- **How:** [Implementation detail]
- **Outcome:** [Definition of done]
- **Best practice:** [Conformant / Deviation — rationale]

### 2. <Step Title>
...

## Execution Notes

- **Dependencies:** [Which steps depend on others]
- **Quick wins:** [Steps that can ship immediately]
- **Open questions:** [Anything that needs user input before proceeding]
```
