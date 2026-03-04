---
name: writing
description: General-purpose writing skill. Use this skill when the user asks Tab to write, draft, compose, or edit text — social media posts, tweets, blog entries, documentation, emails, announcements, READMEs, changelogs, marketing copy, or any other written content.
argument-hint: "[format] [topic]"
---

## What This Skill Does

Produces written content across formats — from tweets to docs — in Tab's voice, tuned to the target audience and medium.

## Workflow

1. **Clarify the format** — identify what kind of writing is needed from the provided arguments (`$ARGUMENTS`) or conversation context. If ambiguous, ask.
2. **Assess audience and tone** — match voice to the target. Casual for social, precise for docs, persuasive for copy. Always filtered through Tab's own voice — never generic, never corporate-bland.
3. **Draft** — produce the content in full.
4. **Refine** — tighten sentences, cut fluff, verify the structure fits the format. Read it back as if you're the audience.

## Format Guide

### Social media
- Short, punchy, one idea per post.
- Platform-aware: tweets are tight and hook-driven, LinkedIn leans professional but not stiff.
- Use line breaks for rhythm. No hashtag spam — one or two if they earn their spot.

### Blog posts
- Open with a hook — a question, a bold claim, a surprising fact. Not "In this post, I will..."
- Substance in the middle: clear sections, concrete examples, no padding.
- End with a takeaway the reader walks away with, not a summary of what they just read.

### Documentation
- Scannable: headers, bullet points, short paragraphs.
- Precise: say exactly what something does, not what it "helps" do.
- Task-oriented: lead with what the reader needs to *do*, not background theory.
- Code examples where they'd help. Keep them minimal and correct.

### General / other
- Match the conventions of whatever format is requested (email, changelog, README, announcement, etc.).
- When in doubt: clear over clever, short over long, specific over vague.
