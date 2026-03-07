# Memory Skill Scoring Rubric

Score each dimension **0**, **1**, or **2** per the criteria below.

| Dimension | What it measures | 0 | 1 | 2 |
|-----------|-----------------|---|---|---|
| **S1: Index structure** | `index.md` has User/Active/Recent sections | Missing or wrong sections | Sections exist but malformed | Correct 3-section structure |
| **S2: Index cap** | `index.md` stays within 20 lines | Over 25 lines | 21-25 lines | 20 lines or under |
| **S3: Notes cap** | `notes.md` stays within 50 lines | Over 60 lines | 51-60 lines | 50 lines or under |
| **S4: Structured file cap** | `profile.md`, `goals.md`, `learning.md` each within 30 lines | Over 35 lines | 31-35 lines | 30 lines or under |
| **S5: Recent cap** | Recent section has 3-5 entries | More than 7 or 0 entries | 6-7 entries | 3-5 entries |
| **B1: Immediate save** | "Remember X" writes to disk now, not deferred | Not written at all | Written but to wrong file | Written immediately to correct file |
| **B2: Forget** | "Forget X" removes the target entry | Entry still present | Entry partially removed or commented | Entry fully removed |
| **B3: Lazy load** | Detail files load only when conversation triggers them | All files loaded on startup | Some unnecessary files loaded | Only triggered files loaded |
| **B4: Invisibility** | Memory system not mentioned unless asked | Explains memory system unprompted | Hints at memory mechanics | System is invisible to user |
| **B5: Trivial skip** | Trivial conversations don't update detail files | Detail files updated for trivial chat | Index updated but detail files also touched | No detail file writes (index-only or nothing) |
| **B6: Rewrite not append** | Session-end saves rewrite `index.md`, not append | Appended to existing content | Partial rewrite with remnants | Clean full rewrite |

## Score Totals

**Maximum: 22 points** (11 dimensions x 2 points each)

| Range | Verdict |
|-------|---------|
| 18-22 | **Pass** |
| 14-17 | **Marginal** — review failures, may need targeted fixes |
| 0-13  | **Fail** — significant behavioral gaps |

## Scoring Notes

- **S2-S5** are deterministic — use `check-run.sh` for automated checking.
- **B3** requires transcript review to verify which files were read during the session.
- **B4** is only testable when the user does NOT ask about memory. Score 2 if memory isn't discussed.
- **B5** requires checking the filesystem after a trivial conversation ends.
- **B6** requires comparing `index.md` before and after a session-end save.