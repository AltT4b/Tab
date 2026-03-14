---
name: workshop
description: "Use when the user runs /workshop or explicitly asks to workshop, brainstorm, or plan an idea before committing to an approach."
argument-hint: "[idea or problem to workshop]"
---

## What This Skill Does

A continuous planning session that shapes a raw idea into an in-depth implementation plan. The conversation drives the process — not a rigid set of steps. Actively researches (web search, codebase exploration) to ground the discussion in reality, and maintains a living document that evolves as the plan takes shape.

Not for quick answers or direct implementation — this is for problems that benefit from exploration before committing to an approach.

**Project context:** Load CLAUDE.md at the start of every workshop session. Workshop is where design decisions happen — it needs the project architecture.

## How It Works

### Starting the Session

1. Read the idea. Restate it back in one or two sentences to confirm understanding.
2. Do initial research — scan relevant files in the project and run a few web searches to understand the landscape. Share what you find before asking anything.
3. Lay down a **rough sketch** — a short, informal outline of the plan as you currently understand it. This is the seed. It will be wrong and incomplete. That's the point.

### The Loop

This is the core of the skill. There is no fixed number of iterations — the session continues until the user is satisfied. Drive toward one decision at a time — surface multiple findings, but don't pile up five questions in a message.

Each pass through the loop:

- **React to what the user said.** They might challenge an assumption, ask to zoom into a section, redirect entirely, or confirm something is solid. Follow their lead.
- **Research before proposing.** Do not propose an approach without first checking whether an existing solution already handles it. If a question comes up that you can't answer confidently, search for it — existing solutions, libraries, patterns, prior art, project files for constraints and conventions. Share findings conversationally — synthesize, don't dump links. "Looks like X library handles this, but Y might be a better fit because..."
- **Update the plan.** When the conversation *lands* — a decision is made, an open question gets resolved, the approach shifts — update the running plan inline. Don't update during exploratory back-and-forth that hasn't settled yet. If you're not sure whether something has landed, it probably hasn't.
- **Name it when it stalls.** If the conversation isn't converging after several passes, say so. Name the block and ask whether to narrow scope or pivot.
- **Name it when it sprawls.** If the scope is growing beyond what one session can resolve, say so. Suggest breaking into focused sessions rather than producing a plan too broad to implement from.

### The Plan

The plan lives in the conversation. Tab maintains it as a running summary — structured however makes sense for the topic, but generally:

- **Goal** — what we're building and why
- **Approach** — how we're building it, concrete enough to implement from
- **Decisions** — what's been decided and why
- **Open questions** — things still unresolved

The plan gains resolution over time. Sections grow, shrink, merge, or get cut as the thinking evolves.

### Ending the Session

The session ends when the user says it does. When they're ready:

**Produce the final plan.** The exploration followed the conversation's path, which meanders. The final plan should follow the *problem's* logic — someone reading it without the conversation context should understand what's being built, how, and why. The approach should be concrete enough to implement from: specific steps, file paths, data flows, APIs — whatever resolution the conversation reached. If the user wants it saved as a file, ask where it should go.

## Principles

- **Stay practical.** This produces implementation plans, not academic papers. Every section should help someone build the thing.
- **Cut useless detail.** If it's not needed for the core plan, it's a distraction.
