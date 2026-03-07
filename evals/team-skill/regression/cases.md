# Regression Cases — Team Skill

Cases that MUST pass ~100% of the time. Guards against breaking changes. Run on every skill edit.

---

## Negative Cases (Should NOT Trigger Team)

### TC-06: Trivial Question

- **Prompt:** "What's the capital of France?"
- **Why it's here:** Trivial factual question. No ambiguity, no complexity, no multi-perspective value.
- **What to observe:**
  - [ ] Tab does NOT propose a team plan
  - [ ] Tab does NOT spawn any agents
  - [ ] Tab answers directly (Paris)
  - [ ] No run directory created in `.tab/team/`

---

### TC-11: Simple Coding Question

- **Prompt:** "How do I reverse a string in Python?"
- **Why it's here:** Simple technical question with a known answer. Team orchestration adds no value.
- **What to observe:**
  - [ ] Tab answers directly with code
  - [ ] No team plan proposed
  - [ ] No agents spawned
  - [ ] No run directory created

---

### TC-12: Personal Opinion

- **Prompt:** "What do you think about pineapple on pizza?"
- **Why it's here:** Subjective preference question. Not a task, not researchable, not multi-perspective.
- **What to observe:**
  - [ ] Tab responds conversationally in its own voice
  - [ ] No team plan proposed
  - [ ] No agents spawned
  - [ ] No run directory created

---

### TC-13: Simple Debugging

- **Prompt:** "What does this error mean? TypeError: cannot read property 'map' of undefined"
- **Why it's here:** Straightforward debugging question. One answer, no team needed.
- **What to observe:**
  - [ ] Tab explains the error directly
  - [ ] No team plan proposed
  - [ ] No agents spawned
  - [ ] No run directory created

---

### TC-14: Memory/Reminder Task

- **Prompt:** "Remind me to take out the trash tomorrow."
- **Why it's here:** Personal task that routes to memory, not team orchestration.
- **What to observe:**
  - [ ] Tab acknowledges the reminder (via memory skill or conversationally)
  - [ ] No team plan proposed
  - [ ] No agents spawned
  - [ ] No run directory created

---

## Behavioral Guardrails

### TC-07: Ambiguous Request — Scoping Required

- **Prompt:** "Look into databases for me."
- **Variant:** "Get the team on this."
- **Why it's here:** Vague requests MUST trigger scoping questions, not assumptions.
- **What to observe:**
  - [ ] Tab asks 1-2 clarifying questions before proposing a plan
  - [ ] At least one question uses multiple-choice when options are finite
  - [ ] Tab stops asking once it has enough information
  - [ ] For the zero-context variant: first question establishes the basic topic
  - [ ] Task type and team shape depend on the user's answers, not assumptions

---

## Structural Constraints (Applied to Any Team Run)

These assertions apply to every capability case that produces a team run. They are regression-grade — should never fail.

| Constraint | Check | Type |
|------------|-------|------|
| C1: Round cap | No more than 4 rounds | script |
| C2: Agent output cap | Each agent file under 1000 words | script |
| P2a: File output | Files at `.tab/team/<run-id>/round-N/<role>.md` | script |
| P3a: Synthesis exists | `synthesis.md` exists with >50 words | script |

These are verified by `check-run.sh` and should pass^3 = 100%.
