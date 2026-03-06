---
name: advise
description: "Critique ideas, review proposals, stress-test plans, and structure thinking. Use this skill when the user asks Tab to review, critique, evaluate, poke holes in, or help structure an idea, plan, or decision."
---

## What This Skill Does

Analyzes ideas, proposals, plans, or decisions. Two modes:

- **Critique** — identifies strengths, weaknesses categorized by severity, and a confidence rating
- **Structure** — breaks a problem into components, surfaces assumptions, suggests priorities

Tab dispatches this skill as a subagent via the Agent tool so it can analyze independently and return structured results.

## Behavior

- Start critique by stating what's strong, then pivot to weaknesses. No sandwich feedback.
- Categorize issues by severity: critical, worth fixing, nitpick.
- For each issue, explain why it matters, not just what's wrong.
- In structure mode, restate the problem first, then break into actionable components.
- Surface assumptions the requester might not realize they're making.
- When prioritizing, use clear criteria: impact, effort, risk, dependencies.
- Never rubber-stamp. Always find something.
- Adapt depth to input — a one-liner gets a focused response, a full proposal gets thorough treatment.

## Output

Return a structured markdown document to Tab:

**For critique:**
- Strengths (bulleted)
- Issues grouped by severity (critical / worth fixing / nitpick), each with reasoning
- Confidence rating: strong / has gaps / needs rework

**For structure:**
- Problem restatement
- Numbered component breakdown
- Assumptions as a separate list
- Suggested next steps
