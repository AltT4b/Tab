# Eval Conventions

Standards for all eval suites in this project. Based on [Anthropic's agent eval guide](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

## Directory Structure

```
evals/
  CONVENTIONS.md              # This file
  <skill-name>/
    README.md                 # Suite overview, how to run, pass thresholds
    rubric.md                 # Scoring dimensions (if using rubric-based grading)
    harness.md                # Trial infrastructure: state reset, multi-trial, transcript capture
    check-run.sh              # Code-based grader (deterministic checks)
    results.md                # Results log with multi-trial support
    regression/
      cases.md                # Human-readable case descriptions
      cases.json              # Machine-readable assertions
    capability/
      cases.md                # Human-readable case descriptions
      cases.json              # Machine-readable assertions
    references/               # Reference solutions (optional, proves feasibility)
      <case-id>.md
```

## Regression vs Capability

Every eval case belongs to exactly one category:

- **Regression**: Guards against breaking changes. Expected pass rate ~100%. Binary or near-binary assertions. Run these on every change. Examples: negative cases (should NOT trigger), structural constraints (file output, caps), fundamental behaviors (scoping).
- **Capability**: Tracks improvement over time. Lower pass rates expected initially. Quality-oriented, often requires model-based or human grading. Examples: team composition quality, synthesis depth, creative output diversity.

## Case Format (cases.json)

```json
{
  "suite": "<skill-name>",
  "category": "regression|capability",
  "cases": [
    {
      "id": "TC-XX",
      "prompt": "The exact prompt to send",
      "context": "Setup instructions or preconditions (optional)",
      "expected": "What a correct outcome looks like",
      "assertions": [
        {
          "name": "Short assertion name",
          "check": "What to verify",
          "type": "script|model|manual",
          "grader_prompt": "LLM grader prompt (for type: model only)"
        }
      ],
      "tags": ["negative", "edge-case", "stress-test"]
    }
  ]
}
```

### Assertion Types

| Type | When to Use | Properties |
|------|-------------|------------|
| `script` | Deterministic, verifiable by code | Checked by `check-run.sh` or equivalent |
| `model` | Subjective but automatable with LLM | Must include `grader_prompt`. Calibrate against human judgment regularly |
| `manual` | Requires human observation during the trial | Scored by evaluator using rubric |

### Model-Based Grader Rules

- Always include a structured rubric in `grader_prompt` (not vague instructions)
- Include an "Unknown/Unable to determine" escape hatch — never force a score
- Grade individual dimensions separately, not holistically
- Calibrate against human scores at least every 5 eval sessions
- Log disagreements between model and human graders for review

## Trial Protocol

### State Isolation

Each trial MUST start from a clean state:
- No leftover `.tab/` directories from prior runs
- Memory state documented (fresh or seeded — specify which)
- No conversation context carried over between trials

### Multi-Trial Runs

Run each case at least 3 trials to account for model variability. Track:
- **pass@k**: Did it pass at least once in k trials?
- **pass^k**: Did it pass every time in k trials? (consistency metric)

Report both metrics. A case that passes 1/3 trials is very different from 3/3.

### Transcript Capture

Save the full conversation transcript for every trial:
- Location: `.tab/eval-transcripts/<suite>/<case-id>-trial-<n>.md`
- Include all tool calls, agent outputs, and Tab's responses
- Review transcripts when scores are surprising (high or low)

## Saturation Protocol

After each eval session:
1. Check if all regression cases pass at 100% across 3+ trials
2. Check if any capability case has hit pass@3 = 100% for 3+ consecutive sessions
3. Saturated cases need harder variants or should graduate to regression

## Maintenance

- Review and update cases when the skill's behavior spec changes
- Add new cases from real failures observed in production use
- Remove or archive cases that no longer test meaningful behavior
- Log the eval suite version in results.md; bump on structural changes
