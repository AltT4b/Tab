# Evals

Evaluation framework for Tab's team skill archetypes. All markdown, no code — mirrors the rest of Tab's architecture.

## Purpose

1. **Identify archetypes** — run diverse scenarios, observe which roles Tab keeps inventing, grade their output, and codify the ones that earn it.
2. **Grade archetype quality** — measure whether codified archetype instructions produce meaningfully better output than bare one-line briefs.
3. **Iterate on instructions** — change an archetype's skill instructions, rerun the same scenario, compare grades.

## Structure

```
evals/
├── README.md              # This file
├── scenarios/             # Test scenarios to run through the team skill
│   └── <scenario>.md      # One file per scenario
└── runs/                  # Output from eval runs (gitignored)
    └── <run-id>/          # Matches .tab/team/<run-id>/ structure
```

The grading rubric (`rubric.md`) and Grader (`grader.md`) both live here — they're development tools for iterating on archetypes, not user-facing.

## How It Works

### Scenarios

Each scenario file defines:
- **Question** — the prompt to give the team skill
- **Expected roles** — what kinds of roles should appear (not exact names, but categories)
- **Role rubric overrides** — any scenario-specific grading criteria beyond the shared rubric

Scenarios should span diverse problem types: decision-making, research, creative, technical analysis, strategic planning. The goal is coverage — if an archetype only helps on one kind of problem, it's not an archetype.

### Grading

Two modes:

1. **Self-grading** — after a team run, dispatch a Grader agent (archetype) that reads the output files in `.tab/team/<run-id>/` and scores each role's contribution against the rubric. The Grader writes its scores to `evals/runs/<run-id>/grades.md`.

2. **Manual grading** — use the rubric as a checklist and score by hand. Useful for calibrating the Grader itself.

### The Grading Process

1. Pick a scenario from `scenarios/`.
2. Run it through the team skill ("Hey Tab, get the team on this: [question]").
3. After the run completes, dispatch the Grader against the output.
4. Review grades. If a role type consistently scores high across unrelated scenarios, it's an archetype candidate.

## Archetype Graduation

A role earns archetype status when:
- It appears in 3+ runs across unrelated scenarios
- Its graded output is consistently stronger than what a bare one-line brief produces
- The skill instructions encode non-obvious methodology (not just "be good at X")

The Grader is the first codified archetype — it's needed to run this framework.
