# Output Format Templates

Use these exact templates when producing structured output. Select based on task type.

---

## Code Review

```
## Review: <file or function name>

**Must Fix**
- [ISSUE]: What it is, why it matters
  → Fix: code snippet or description

**Should Fix**
- [ISSUE]: What it is, why it matters
  → Fix: code snippet or description

**Looks Good**
- Brief note on what's well done (optional, only if genuinely noteworthy)
```

---

## Architecture Proposal

```
## Proposal: <feature name>

**Context**: What I understand about the requirement and constraints

**Option A: <name>**
- How it works (2-3 sentences)
- Trade-offs: pros / cons

**Option B: <name>**
- How it works (2-3 sentences)
- Trade-offs: pros / cons

**Recommendation**: Option X because <one clear reason>

**Next step**: What to build/decide first
```

---

## Debugging

```
## Debug: <issue summary>

**Root cause hypothesis**: What I think is causing this and why

**Verification**: How to confirm (log line, assertion, print statement)

**Fix**:
[code snippet]

**Why this works**: One sentence explanation
```
