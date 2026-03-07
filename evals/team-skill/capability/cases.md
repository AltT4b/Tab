# Capability Cases — Team Skill

Cases that track quality improvement over time. Lower pass rates expected initially. Run on a regular cadence.

Score all cases against `rubric.md` for the full 10-dimension evaluation. Case-specific observations are listed below.

---

## Task-Type Coverage

### TC-01: Research — Local-First Software

- **Prompt:** "Research the current state of local-first software — who's building what, what patterns are emerging, and where the gaps are."
- **Expected task type:** Research
- **Expected complexity:** Complex (2 rounds, 3-4 agents)
- **What to observe:**
  - [ ] Phase 0 skips or asks at most 1 question (request is specific)
  - [ ] Roles include search-heavy archetypes (e.g., Industry Surveyor, Technical Analyst)
  - [ ] Tab checks whether web search tool is available for search-oriented roles
  - [ ] Tab reads archetypes/registry.md during execution
  - [ ] Agents produce citations or concrete examples, not vague summaries

---

### TC-02: Decision-Making — Postgres vs SQLite

- **Prompt:** "Should I use Postgres or SQLite for a side project that starts single-user but might grow to multi-tenant?"
- **Expected task type:** Decision-making
- **Expected complexity:** Complex (2 rounds, 3 agents)
- **What to observe:**
  - [ ] Phase 0 skips or asks at most 1 constraint question
  - [ ] Team includes advocates for each option plus a critic or synthesizer
  - [ ] 2 rounds: Round 1 advocacy, Round 2 stress-tests the recommendation
  - [ ] Synthesis delivers a clear recommendation with reasoning

---

### TC-03: Analysis — LLM Tail Latency

- **Prompt:** "Why do LLM apps have such high tail latency? Break down every layer of the stack that contributes."
- **Expected task type:** Analysis
- **Expected complexity:** Complex (1-2 rounds, 3-4 agents)
- **What to observe:**
  - [ ] Phase 0 skips — request is clear and scoped
  - [ ] Roles include domain specialists (Inference, Network/IO, Application-Layer) plus a generalist
  - [ ] Output is structured by layer, not a wall of prose
  - [ ] Covers tokenization, batching, network, decoding strategy

---

### TC-04: Creative — Gamification for Haters

- **Prompt:** "Design a gamification system for a habit-tracking app aimed at adults who hate gamification."
- **Expected task type:** Creative
- **Expected complexity:** Simple-to-complex (1-2 rounds, 2-3 agents)
- **What to observe:**
  - [ ] Phase 0 skips or asks one light question (prompt is specific enough)
  - [ ] Roles bring diverse perspectives (e.g., Behavioral Psychologist, UX Designer, Skeptic)
  - [ ] Briefs give agents creative latitude, not rigid structure
  - [ ] Agent outputs are meaningfully different from each other
  - [ ] At least one role challenges or pressure-tests ideas

---

### TC-05: Implementation — CLI Static Site Generator

- **Prompt:** "Build a CLI tool in Python that takes a directory of markdown files and generates a static site with a table of contents."
- **Expected task type:** Implementation
- **Expected complexity:** Simple-to-complex (1-2 rounds, 2-3 agents)
- **What to observe:**
  - [ ] Phase 0 skips — request is concrete
  - [ ] Roles split by concern (Architect, Edge Case Analyst, Testing/Quality)
  - [ ] Tab reads archetypes/registry.md for matching roles
  - [ ] Output includes design decisions (file structure, libraries, CLI args), not just abstract patterns
  - [ ] Edge cases addressed (empty dirs, nested folders, malformed markdown)

---

## Stress Tests

### TC-08: Blended Task Type — Auth Build vs Buy

- **Prompt:** "Should I build my own auth system or use a third-party service? Research the options and then design whichever approach is better."
- **Expected task type:** Decision-making + Research (blended)
- **Expected complexity:** Complex (2+ rounds, 3-5 agents)
- **What to observe:**
  - [ ] Plan acknowledges the blend of task types
  - [ ] Round 1 includes research/advocacy roles for both options
  - [ ] Round 2 pivots to design for the winning approach
  - [ ] Status update posted after Round 1 summarizing findings and gaps
  - [ ] Round 2 agents receive curated briefs under 500 words
  - [ ] Agents within the same round run in parallel

---

### TC-09: Pressures Agent Cap — 7 Angles, 5-Agent Limit

- **Prompt:** "Analyze the impact of remote work from every angle — technical infrastructure, HR policy, legal compliance, employee wellbeing, company culture, real estate costs, and environmental effects."
- **Expected task type:** Analysis
- **Expected complexity:** Complex (2 rounds, 5 agents max)
- **What to observe:**
  - [ ] Tab consolidates 7 angles into 5 or fewer composite roles
  - [ ] All 7 angles are addressed across the output (none silently dropped)
  - [ ] May use 2 rounds to cover ground without exceeding per-round agent limit
  - [ ] Status update after each round
  - [ ] Inter-round context curated and under 500 words per agent

---

### TC-10: Very Narrow, Specific Request

- **Prompt:** "Research whether Python 3.13's JIT compiler actually improves performance for typical numpy-heavy data science workloads."
- **Expected task type:** Research
- **Expected complexity:** Simple (1 round, 1-2 agents)
- **What to observe:**
  - [ ] Phase 0 skips — request is precise
  - [ ] Small team: 1-2 agents, 1 round
  - [ ] Roles are focused (e.g., Benchmarking Analyst, CPython Internals Specialist)
  - [ ] Output addresses the specific claim about numpy workloads
  - [ ] Does not drift into general Python performance topics
