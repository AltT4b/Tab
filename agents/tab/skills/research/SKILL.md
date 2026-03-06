---
name: research
description: "Research a topic across web sources, local filesystems, and documentation. Use this skill when the user asks Tab to look something up, find information, investigate a question, or gather facts from multiple sources."
---

## What This Skill Does

Conducts research across web sources, local filesystems, and documentation. Finds facts, cross-references them, and delivers sourced findings.

Tab dispatches this skill as a subagent via the Agent tool so it can search independently and return structured results.

## Behavior

- Cite every factual claim with its source (URL, file path, or document reference).
- Distinguish facts from inferences. If extrapolating, say so.
- Cross-reference where possible. Flag conflicts between sources.
- Prefer primary sources over summaries. Official docs over blog posts.
- When exploring a filesystem, report what was found and what was not found.
- If a search returns nothing useful, say so and suggest a refined approach.
- Avoid paywalled sources.

## Output

Return a structured markdown document to Tab:

- **Findings** — organized by theme, each finding with a source citation
- **Conflicts & Gaps** — where sources disagree, which is more credible, what remains unanswered
- **Confidence** — High / Medium / Low with one-line justification
