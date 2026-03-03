# Summon-Tab Redesign — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor `summon-tab` from a hardcoded single-agent loader into a thin dispatcher that discovers agents, routes by context, and loads persona layers additively.

**Architecture:** `summon-tab` SKILL.md becomes a four-step dispatcher (discover, route, load, become). Base agent always loads. Variant agents live as sibling directories under `agents/` and use an additions-only AGENT.md format with `extends: base` in frontmatter. No variants exist yet — the framework is scaffolded and ready.

**Tech Stack:** Markdown only (no code, no tests, no build)

---

## Task 1: Rewrite summon-tab SKILL.md as thin dispatcher

**Files:**
- Modify: `skills/summon-tab/SKILL.md:1-32` (full file replacement)

**Step 1: Replace the SKILL.md content**

Replace the entire file with this:

```markdown
---
name: summon-tab
description: Summon the Tab agent. Use this skill whenever the user wants to talk to Tab, summon Tab, invoke Tab, run the Tab agent, or delegate work to the base agent. Also trigger when the user says "Hey Tab", "Tab,", "I need Tab", "Ask Tab", or refers to the Tab agent in any way. Only trigger this skill if the user is asking for Tab as if it were its name.
---

## What This Skill Does

Activates the Tab agent by loading the base persona and optionally layering on a role-specific variant. This skill is a thin dispatcher — all persona content lives in agent files under `agents/`.

## Step 1: Discover Available Agents

Scan `agents/*/AGENT.md` to build a list of available agents.

- `agents/base/AGENT.md` is the **base agent** — always loaded.
- Any other `agents/<name>/AGENT.md` with `extends: base` in its frontmatter is a **variant agent**.

If only `base/` exists, skip to Step 3.

## Step 2: Route to Variant

If variant agents were discovered:

1. Read each variant's AGENT.md frontmatter (just the `description` field — do not read the full file yet).
2. Evaluate the user's request and conversation context against each variant's description.
3. Select the best-matching variant, or select none if no variant clearly fits.

If no variant matches, proceed with base only.

## Step 3: Load Context

1. **Always** read `agents/base/AGENT.md` fresh. This contains Tab's core identity, rules, skills, and output format.
2. **If a variant was selected**, read its `agents/<name>/AGENT.md` next. Variant files use an additions-only format — their "Additional X" sections append to the corresponding base sections. Never replace base content.
3. If the selected variant has a `skills/` directory, those skills become available alongside the base agent's skills.

## Step 4: Become Tab

1. **Become Tab.** VERY IMPORTANT - ALWAYS FOLLOW THIS RULE: Take on Tab's identity, personality, and rules from the loaded context. Respond as Tab from this point forward — not as a narrator describing what Tab would do, but *as* Tab itself.
2. **Follow the workflow.** If the loaded context includes a workflow, execute each step in order, producing real output.
3. **Handle the user's request.** If the user included a task or question, weave it into your response naturally as Tab would.
4. **Stay in character.** VERY IMPORTANT - ALWAYS FOLLOW THIS RULE: Continue responding as Tab for the remainder of the conversation, or until the user indicates they're done talking to Tab.
```

**Step 2: Verify the file**

Read `skills/summon-tab/SKILL.md` and confirm:
- Frontmatter has `name` and `description`
- Description field typo fixed ("it's" → "its")
- Four steps: Discover, Route, Load, Become
- No hardcoded reference to `agents/base/AGENT.md` as the only agent
- Persona adoption rules preserved from original Step 2

**Step 3: Commit**

```bash
git add skills/summon-tab/SKILL.md
git commit -m "refactor: rewrite summon-tab as extensible agent dispatcher"
```

---

## Task 2: Update CLAUDE.md to reflect new architecture

**Files:**
- Modify: `CLAUDE.md:9-35`

**Step 1: Update the Repository Structure section**

Replace the tree diagram (lines 11-21) with:

```
Tab/
├── .claude-plugin/plugin.json       # Plugin manifest (entry point)
├── agents/
│   ├── base/
│   │   ├── AGENT.md                 # Tab's core persona (always loaded)
│   │   └── skills/
│   │       └── draw-dino/SKILL.md   # Agent-local skill
│   └── <variant>/                   # Future: role-specific variants
│       ├── AGENT.md                 # Additions-only (extends: base)
│       └── skills/                  # Variant-local skills
└── skills/
    └── summon-tab/SKILL.md          # Shared skill: agent dispatcher
```

**Step 2: Update the Architecture section**

Update the **Agents** paragraph (line 27) to mention the variant format:

> **Agents** (`agents/<name>/AGENT.md`): Define an AI persona. The base agent (`agents/base/`) uses YAML frontmatter (`name`, `description`) and markdown body sections: `## Identity`, `## Additional Rules`, `## Additional Skills`, `## Output`. Variant agents add `extends: base` to frontmatter and use additions-only sections (`## Additional Identity`, `## Additional Rules`, `## Additional Skills`) that layer on top of the base.

**Step 3: Update the How Tab Gets Activated section**

Replace line 35 with:

> The `summon-tab` shared skill triggers on phrases like "Hey Tab", "@Tab", etc. It scans `agents/` to discover available agents, always loads `agents/base/AGENT.md`, and optionally layers on a variant agent matched by conversation context. Claude then adopts the merged persona for the rest of the conversation.

**Step 4: Add variant frontmatter convention**

Add to the Conventions section (after line 41):

> - **Variant agents**: variant AGENT.md files declare `extends: base` in frontmatter and use only "Additional X" sections (additive, never replace)

**Step 5: Verify the file**

Read `CLAUDE.md` and confirm all sections are coherent and the tree diagram renders correctly.

**Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for extensible agent architecture"
```

---

## Task 3: Smoke test the dispatcher

**Step 1: Invoke Tab**

Use the `summon-tab` skill (say "Hey Tab") and have a short exchange. Verify:
- Tab's persona loads correctly (warm, witty voice)
- No errors from the discovery/routing steps
- With no variants present, it gracefully loads base only
- Tab stays in character

**Step 2: Note any adjustments needed**

If the dispatcher instructions cause unexpected behavior, make targeted edits to the SKILL.md.
