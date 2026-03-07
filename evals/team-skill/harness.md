# Trial Harness — Team Skill

How to run team skill evals with proper isolation, multi-trial support, and transcript capture.

## Prerequisites

- Clean working directory (no uncommitted changes that could interfere)
- Note which model is being used (include in results)

## Pre-Trial Reset

Before each trial, run this checklist:

1. **Clear prior run artifacts**: `rm -rf .tab/team/` (or move to `.tab/eval-archive/` if you want to keep them)
2. **Start a fresh conversation**: New Claude Code session — no context carryover
3. **Summon Tab**: Send "Hey Tab" to load the persona
4. **Document memory state**: Note whether Tab's memory is fresh or seeded. For regression evals, prefer fresh memory to reduce variables. For capability evals, seeded memory is acceptable if documented.

## Running a Trial

1. Copy the exact prompt from `cases.json` (not paraphrased)
2. Let Tab run to completion — do not interrupt unless it's stuck in a loop
3. Score code-based assertions: `./check-run.sh <run-id>`
4. Score manual/model assertions against `rubric.md`
5. Save the transcript (copy full conversation to `.tab/eval-transcripts/team-skill/<case-id>-trial-<n>.md`)
6. Record scores in `results.md`

## Multi-Trial Protocol

Run each case **3 trials minimum**. For cases with inconsistent results, run up to 5.

### Metrics

| Metric | Formula | What It Tells You |
|--------|---------|-------------------|
| pass@k | Passed at least 1 of k trials | Can it do this at all? |
| pass^k | Passed all k trials | Can it do this reliably? |
| mean score | Average rubric score across trials | Quality trend |
| score variance | Spread across trials | Consistency |

### When to Investigate

- pass@3 = 0 → Likely a broken case or missing capability. Verify the case is solvable before blaming the agent.
- pass@3 > 0 but pass^3 = 0 → Flaky. Read transcripts to find what differs between passing and failing trials.
- Score variance > 4 points across trials → Inconsistent behavior. Prioritize for skill improvements.

## Transcript Review

Schedule transcript review after every eval session. Focus on:

1. **Failing trials** — Is the failure fair? Is it a grader issue or an agent issue?
2. **Barely passing trials** — Where is it losing points? Are those the right dimensions to lose on?
3. **Perfect scores** — Is the grader too lenient? Is the case too easy (saturation)?

## Regression vs Capability Workflow

### Regression Suite

- Run on every skill change (SKILL.md edits, archetype changes)
- All cases should pass^3 = 100%
- Any regression = block the change until fixed or case is reclassified
- Quick to run: mostly negative cases with code-based grading

### Capability Suite

- Run on a regular cadence (weekly or per-milestone)
- Track score trends over time
- No blocking threshold — these track improvement, not gatekeep
- Cases that hit pass^3 = 100% for 3 consecutive sessions → graduate to regression
