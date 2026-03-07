# Memory Skill Eval Suite

Evaluates Tab's persistent memory system — loading, saving, caps, lazy loading, and explicit memory commands. See `evals/CONVENTIONS.md` for structural standards.

## Suite Overview

| Category | Cases | Purpose | Expected Pass Rate |
|----------|-------|---------|-------------------|
| Regression | MC-01–MC-11 | Guard against bloat and breaking changes | ~100% |
| Capability | MC-C01–MC-C10 | Track quality of memory judgment | Varies |

**Total: 21 cases** (11 regression, 10 capability)

## Contents

```
memory-skill/
  README.md           # This file
  rubric.md           # Scoring dimensions for memory behavior
  harness.md          # Trial protocol: state reset, memory seeding, transcripts
  check-run.sh        # Code-based grader for deterministic checks (caps, structure)
  results.md          # Results log with multi-trial support
  regression/
    cases.md          # Human-readable regression case descriptions
    cases.json        # Machine-readable assertions with grader prompts
  capability/
    cases.md          # Human-readable capability case descriptions
    cases.json        # Machine-readable assertions with model grader prompts
```

## How to Run

### Quick Regression Check

1. Read `harness.md` for the pre-trial reset checklist
2. Run each case in `regression/cases.json` — 3 trials each
3. Score with `check-run.sh` (for script assertions) and model/manual grading
4. Record in `results.md`
5. All cases should pass^3 = 100%

### Full Capability Eval

1. Complete the regression suite first
2. Run each case in `capability/cases.json` — 3 trials each
3. Score all 11 rubric dimensions per `rubric.md`
4. Run `check-run.sh` for code-based dimensions
5. Record in `results.md` with per-trial breakdowns
6. Save transcripts to `.tab/eval-transcripts/memory-skill/`

## Pass Thresholds

| Category | Threshold |
|----------|-----------|
| Regression | pass^3 = 100% (all trials pass) |
| Capability | 18/22 per case on rubric (mean across trials) |

## Grader Types

| Type | Cases | How |
|------|-------|-----|
| Script | MC-02–MC-06, MC-11, MC-C05, MC-C07 | `check-run.sh` — deterministic file/line checks |
| Model | MC-01, MC-07–MC-10, MC-C01–MC-C10 | LLM grader with structured rubric prompts in `cases.json` |
| Manual | MC-08, MC-C02–MC-C04 | Human transcript review for file read verification |

## Claim Coverage

All 11 regression claims and 7 capability claims are covered. See `regression/cases.md` and `capability/cases.md` for the full mapping.