# Grading Rubric

Shared criteria for evaluating agent output from team runs. The Grader agent uses this rubric. Humans can use it too.

## Per-Role Criteria

Each agent's output is scored on five dimensions. Each dimension is graded Pass / Partial / Fail.

### 1. Focus

Did the agent stay on its assigned angle?

- **Pass**: Output is tightly scoped to the role's brief. No drift into other agents' territory.
- **Partial**: Mostly focused but includes tangential material that belongs to another role.
- **Fail**: Unfocused. Covers ground that overlaps significantly with other agents or wanders off-brief.

### 2. Specificity

Is the output concrete and evidence-based?

- **Pass**: Claims are supported with specific examples, data, evidence, or citations. No hand-waving.
- **Partial**: Mix of specific and vague. Some claims are supported, others are general assertions.
- **Fail**: Mostly generalities. "This is important because..." without saying why specifically.

### 3. Honesty

Does the agent acknowledge limits and avoid fabrication?

- **Pass**: Gaps are stated clearly. No invented facts, fake citations, or false confidence.
- **Partial**: Mostly honest but overstates confidence on thin evidence in places.
- **Fail**: Contains fabricated claims, fake URLs, or presents speculation as fact.

### 4. Structure

Is the output well-organized and scannable?

- **Pass**: Clear sections, bulleted findings, easy to extract key points. Follows the output format from the briefing template.
- **Partial**: Readable but could be better organized. Some key points buried in prose.
- **Fail**: Wall of text. Hard to find the actual findings.

### 5. Additive Value

Did this agent contribute something the team wouldn't have without it?

- **Pass**: The output contains insights, findings, or perspectives that no other agent in the run produced. Removing this agent would leave a visible gap.
- **Partial**: Some unique contribution, but significant overlap with other agents' output.
- **Fail**: Redundant. Another agent already covered this ground as well or better.

## Skill-Specific Criteria

When a role has codified skill instructions (i.e., it's an archetype), the Grader also checks compliance with those instructions. This is a simple checklist: for each instruction line in the archetype, did the agent follow it?

Format: list each instruction, mark Yes / No / N/A.

## Overall Assessment

After scoring all roles:
- **Strongest role** — which agent contributed the most?
- **Weakest role** — which agent contributed the least? Why?
- **Missing perspective** — was there a viewpoint the team lacked?
- **Archetype signal** — did any role demonstrate methodology worth codifying?

## Comparative Mode

When grading the same scenario run twice (e.g., with vs. without archetype instructions):
- Score both runs independently using the criteria above.
- Then compare: which run produced better output on each dimension?
- Note specifically where the archetype instructions made a difference vs. where they didn't matter.
