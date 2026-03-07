# Team Skill Eval Results

**Suite version:** 2.0
**Rubric:** See `rubric.md` (20-point scale, pass threshold: 16)
**Conventions:** See `evals/CONVENTIONS.md`

## Regression Results

| Run | Date | Model | Case | Trial | All Assertions Pass? | Failed Assertions | Notes |
|-----|------|-------|------|-------|---------------------|-------------------|-------|
| R1 | 2026-03-06 | Opus 4.6 | TC-06 | 1/1 | YES | — | "Paris." Direct, no ceremony. |
| R1 | 2026-03-06 | Opus 4.6 | TC-07 | 1/1 | YES | — | Asked 2 clarifying questions with multiple-choice. No premature plan. |
| R1 | 2026-03-06 | Opus 4.6 | TC-11 | 1/1 | YES | — | Provided `[::-1]` and `reversed()`. No team. |
| R1 | 2026-03-06 | Opus 4.6 | TC-12 | 1/1 | YES | — | Conversational, opinionated response. No team. |
| R1 | 2026-03-06 | Opus 4.6 | TC-13 | 1/1 | YES | — | Correct explanation of undefined + .map(). No team. |
| R1 | 2026-03-06 | Opus 4.6 | TC-14 | 1/1 | YES | — | Acknowledged limitation, offered memory. No team. |

### Regression Summary

| Run | Date | Cases | pass@1 | Regressions? |
|-----|------|-------|--------|--------------|
| R1 | 2026-03-06 | 6 | 6/6 (100%) | None |

---

## Capability Results

| Run | Date | Model | Case | Trial | P0 | P1a | P1b | P1c | P2a | P2b | P3a | P3b | C1 | C2 | Total | Pass? | Notes |
|-----|------|-------|------|-------|----|-----|-----|-----|-----|-----|-----|-----|----|----|-------|-------|-------|
| R1 | 2026-03-06 | Opus 4.6 | TC-01 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 20/20 | YES | Research. 2 rounds, 4 agents. Concrete citations (Electric SQL, Automerge 3.0, Yjs, PGlite, Linear, Figma, Anytype). |
| R1 | 2026-03-06 | Opus 4.6 | TC-02 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 19/20 | YES | Decision. 2 rounds, 4 agents. Clear recommendation. C2 warn: devils-advocate 1086w. |
| R1 | 2026-03-06 | Opus 4.6 | TC-03 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 20/20 | YES | Analysis. 2 rounds, 4 agents. Structured by 4 stack layers. |
| R1 | 2026-03-06 | Opus 4.6 | TC-04 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 19/20 | YES | Creative. 2 rounds, 4 agents. Genuinely diverse roles (psychologist, UX, critic). C2 warn: refinement-synthesizer 1099w. |
| R1 | 2026-03-06 | Opus 4.6 | TC-05 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 18/20 | YES | Implementation. 2 rounds, 4 agents. Concrete design. C2 FAIL: implementer 1293w. |
| R1 | 2026-03-06 | Opus 4.6 | TC-08 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 20/20 | YES | Blended (Decision+Research). 2 rounds, 5 agents. R1 advocacy, R2 decision+design pivot. |
| R1 | 2026-03-06 | Opus 4.6 | TC-09 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 20/20 | YES | Analysis. 2 rounds, 6 agents (5+1 synthesizer). Consolidated 7 angles into 5 composite roles. All 7 covered. |
| R1 | 2026-03-06 | Opus 4.6 | TC-10 | 1/1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 20/20 | YES | Research (narrow). 1 round, 2 agents. Appropriately small team. Stayed focused on numpy+JIT. |

### Capability Summary

| Run | Date | Cases | Mean Score | All Pass (16+)? | Min Score | Max Score | Notes |
|-----|------|-------|------------|-----------------|-----------|-----------|-------|
| R1 | 2026-03-06 | 8 | 19.5/20 | 8/8 (100%) | 18 (TC-05) | 20 (TC-01,03,08,09,10) | C2 (word cap) is the weakest dimension — 3 cases had agents over 1000w. |

---

## Key Findings — Run R1

### Strengths
- **Task classification**: Correct on all 8 cases. Blended task (TC-08) was recognized as blended.
- **Role design**: Every case had distinct, relevant roles — no generic "Researcher 1/2" patterns.
- **Scoping discipline**: Skipped scoping appropriately on specific prompts, engaged on vague ones (TC-07).
- **Synthesis quality**: All syntheses were substantive, in-voice, and opinionated. No "see the file" cop-outs.
- **Constraint consolidation**: TC-09 correctly merged 7 angles into 5 composite roles without dropping coverage.
- **Scaling**: TC-10 correctly used a small team (1 round, 2 agents) for a narrow question.

### Issues
- **C2 word cap violations**: 3/8 cases had at least one agent file over 1000 words. TC-05 (implementer, 1293w) was grossly over. TC-02 (1086w) and TC-04 (1099w) were slightly over. Round 2 synthesizer/implementer roles are the primary offenders — they tend to over-elaborate when integrating prior context.
- **Single-trial limitation**: This run used 1 trial per case. Consistency (pass^3) is unknown.

### Recommendations
1. Strengthen the 1000-word cap instruction in agent briefings — especially for Round 2 roles that receive prior context.
2. Run a full 3-trial session to measure consistency before the next SKILL.md change.

---

## Saturation Tracker

Cases that have hit pass^3 = 100% (capability) or pass@3 = 100% (regression) for 3+ consecutive sessions. Candidates for graduation or harder variants.

| Case | Consecutive 100% Sessions | Action |
|------|--------------------------|--------|
| — | — | First run — no saturation data yet |

---

## Grader Calibration Log

Track disagreements between model-based graders and human judgment. Review after every eval session.

| Date | Case | Dimension | Model Score | Human Score | Resolution |
|------|------|-----------|-------------|-------------|------------|
| — | — | — | — | — | First run — no calibration data yet |
