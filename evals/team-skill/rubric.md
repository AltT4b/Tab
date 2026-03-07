# Team Skill Scoring Rubric

Score each dimension **0**, **1**, or **2** per the criteria below.

| Dimension | What it measures | 0 | 1 | 2 |
|-----------|-----------------|---|---|---|
| **P0: Scoping** | Phase 0 question behavior | Asked when unnecessary OR skipped when needed | Asked but too many (4+) or wrong questions | Appropriate: asked when needed, skipped when clear |
| **P1a: Task classification** | Correct task-type label | Wrong type or not stated | Reasonable but imprecise | Correct type with brief justification |
| **P1b: Team composition** | Roles match the task type | Roles don't match the task | Partial fit, gaps or redundancy | Distinct, relevant, match expected shape |
| **P1c: Complexity scaling** | Agent count and round count fit the task | Grossly over/under-scaled | Slightly off but defensible | Appropriate for the task |
| **P2a: File output** | Correct directory and file structure | No files or wrong paths | Files exist but structure wrong | All output at `.tab/team/<run-id>/round-N/<role>.md` |
| **P2b: Context curation** | Inter-round briefs are curated | Full reports forwarded or no context | Some curation but over 500 words or not role-targeted | Under 500 words per agent, tailored to role |
| **P3a: Synthesis file** | `synthesis.md` exists and integrates findings | No synthesis.md | Exists but just concatenated outputs | Unified narrative integrating all findings |
| **P3b: Synthesis delivery** | Synthesis presented in conversation | Not presented | "See the file" with no substance | Substantive summary in Tab's voice |
| **C1: Round cap** | Never exceeds 4 rounds | Exceeded 4 rounds | N/A (binary) | Within 4 rounds |
| **C2: Agent output cap** | Agent files stay under 1000 words | Grossly over 1000 words | Slightly over | Within 1000 words |

## Score Totals

**Maximum: 20 points** (10 dimensions x 2 points each)

| Range | Verdict |
|-------|---------|
| 16-20 | **Pass** |
| 12-15 | **Marginal** — review failures, may need targeted fixes |
| 0-11  | **Fail** — significant behavioral gaps |

## Scoring Notes

- **P2b** is only scorable on multi-round test cases. For single-round cases, score P2b as 2 (not applicable = no violation).
- **C1** is binary: score 0 or 2. There is no partial credit.
- When scoring **P3b**, listen for Tab's persona voice (per AGENT.md), not generic assistant tone.
- Record specific failure modes in the Notes column of the results log for regression tracking.
