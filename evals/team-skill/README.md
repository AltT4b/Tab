# Team Skill Eval Suite

Evaluates Tab's multi-agent team orchestration skill. See `evals/CONVENTIONS.md` for structural standards.

## Suite Overview

| Category | Cases | Purpose | Expected Pass Rate |
|----------|-------|---------|-------------------|
| Regression | TC-06, TC-07, TC-11–TC-14 | Guard against breaking changes | ~100% |
| Capability | TC-01–TC-05, TC-08–TC-10 | Track quality improvement | Varies |

**Total: 14 cases** (6 regression, 8 capability)

## Contents

```
team-skill/
  README.md           # This file
  rubric.md           # 10-dimension scoring rubric (20-point scale)
  harness.md          # Trial protocol: state reset, multi-trial, transcripts
  check-run.sh        # Code-based grader for deterministic checks
  results.md          # Results log with multi-trial support
  regression/
    cases.md          # Human-readable regression case descriptions
    cases.json        # Machine-readable assertions with model grader prompts
  capability/
    cases.md          # Human-readable capability case descriptions
    cases.json        # Machine-readable assertions with model grader prompts
```

## How to Run

### Quick Regression Check (~15 min)

1. Read `harness.md` for the pre-trial reset checklist
2. Run each case in `regression/cases.json` — 3 trials each
3. Score with `check-run.sh` (for script assertions) and model/manual grading
4. Record in `results.md`
5. All cases should pass^3 = 100%

### Full Capability Eval (~90 min)

1. Complete the regression suite first
2. Run each case in `capability/cases.json` — 3 trials each
3. Score all 10 rubric dimensions per `rubric.md`
4. Run `check-run.sh <run-id>` for code-based dimensions
5. Record in `results.md` with per-trial breakdowns
6. Save transcripts to `.tab/eval-transcripts/team-skill/`

## Pass Thresholds

| Category | Threshold |
|----------|-----------|
| Regression | pass^3 = 100% (all trials pass) |
| Capability | 16/20 per case on rubric (mean across trials) |

## Grader Types

| Type | Dimensions | How |
|------|-----------|-----|
| Script | P2a, P3a, C1, C2 | `check-run.sh` — deterministic file/word checks |
| Model | P0, P1a, P1b, P1c, P2b, P3b, quality-specific | LLM grader with structured rubric prompts in `cases.json` |
| Manual | Any dimension where model grader disagrees with human | Human evaluator scores against `rubric.md` |

## Claim Coverage

All 26 behavioral claims are covered. See the coverage matrix in `capability/cases.md` (task-type cases) and `regression/cases.md` (negative + guardrail cases).
