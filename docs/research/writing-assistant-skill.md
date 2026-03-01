# Research: Writing Assistant Skill for Tab

**Date:** 2026-03-01
**Tier:** Deep
**Tools used:** WebSearch, Glob, Read (codebase exploration of 7ab.net and Tab)

## Question

What should a Tab writing assistant skill look like -- one that helps proofread writing, tell compelling stories about the development process, and produce blog posts for an Astro-based personal site?

## Executive Summary

A great AI writing assistant for dev blogs does three things well: it catches surface errors without flattening voice, it helps structure raw experiences into readable narratives, and it knows the target publishing system well enough to produce publish-ready output. The worst AI writing assistants do the opposite -- they rewrite everything into the same lifeless corporate tone, ignore narrative structure, and produce content that needs manual reformatting before publishing.

The skill should be built around a staged workflow: **outline, draft, review, polish**. Each stage has different rules. Outlining is where narrative structure matters most. Drafting should preserve the author's raw voice. Reviewing checks structure, clarity, and readability. Polishing handles grammar, consistency, and SEO metadata -- and nothing else.

The 7ab.net site is early-stage: Astro 5, Lora serif font, warm earth-tone palette, content collections configured but empty. There is a generated blog schema (`title`, `date`, `description`, `draft`) but no blog content, no blog listing page, and no post layout yet. The writing assistant skill should produce markdown files that conform to this schema and work within Astro's content collection system.

---

## Analysis of 7ab.net Content Setup

### Current State

The site at `/Users/alttab-macbook/AltT4b/7ab.net` is a minimal Astro 5 personal site with:

| Component | Status | Location |
|-----------|--------|----------|
| Astro config | Minimal, site set to `https://7ab.net` | `astro.config.mjs` |
| Content config | Empty -- `collections = {}` | `src/content/config.ts` |
| Blog schema | Auto-generated, defines `title`, `date`, `description`, `draft` | `.astro/collections/blog.schema.json` |
| Blog content | None -- no `.md` or `.mdx` files in `src/content/` | `src/content/` |
| Blog pages | None -- no `blog/` route, no post layout | `src/pages/` |
| Existing pages | `index.astro` (About/hero + featured projects), `projects.astro` | `src/pages/` |
| Layout | `Base.astro` with OG tags, canonical URL, Lora font | `src/layouts/` |
| Design tokens | Warm palette (`#faf9f7` bg, `#c0673a` accent, `#1a1a1a` text), dark mode support, `--max-prose: 680px` | `src/styles/global.css` |
| Components | `Nav.astro` (About, Projects links), `ProjectCard.astro` | `src/components/` |

### What Needs to Exist Before Blog Posts Ship

1. **Content collection definition** -- Add a `blog` collection to `src/content/config.ts` using `glob()` loader pointed at `src/content/blog/`.
2. **Blog post layout** -- A `BlogPost.astro` layout extending `Base.astro` with post title, date, reading time, and prose styling.
3. **Blog listing page** -- `src/pages/blog/index.astro` that queries the blog collection and renders a list.
4. **Dynamic post route** -- `src/pages/blog/[...slug].astro` that renders individual posts.
5. **Nav update** -- Add "Blog" to the links array in `Nav.astro`.
6. **Optional: MDX integration** -- If posts need interactive components, add `@astrojs/mdx`.

### Blog Post Frontmatter Schema

Based on the auto-generated schema, posts should use:

```yaml
---
title: "Post Title"
date: 2026-03-01
description: "One-sentence summary for meta description and listing page."
draft: false
---
```

The writing assistant skill should produce files conforming to this schema. Consider proposing additional fields (`tags`, `heroImage`, `readingTime`) as the blog matures.

---

## Feature Proposals (Ranked by Value)

### Tier 1: Core (Build First)

#### 1. Review Mode -- Structural and Clarity Feedback

The highest-value feature. Given a draft (markdown file or pasted text), provide structured feedback on:

- **Narrative arc** -- Does the post have a clear beginning, tension/problem, and resolution? Or does it meander?
- **Lead quality** -- Does the opening paragraph hook the reader or waste time on preamble? (Michael Lynch's #1 rule: don't meander at the start.)
- **Paragraph-level clarity** -- Flag paragraphs that try to do too much or that lack a clear point.
- **Sentence-level readability** -- Flag sentences over 30 words, chains of 3+ prepositional phrases, and passive voice where active would be clearer.
- **Jargon audit** -- Identify terms that need definition or linking for the target audience.

Output format: A numbered list of observations, each with a location (paragraph number or quote) and a specific, actionable suggestion.

**Rule: Never rewrite prose. Only flag and suggest.**

#### 2. Polish Mode -- Surface-Level Proofreading

Lower-stakes but high-frequency. Given reviewed/revised text, fix:

- Spelling and grammar errors
- Punctuation consistency (Oxford comma, em-dash style, etc.)
- Repeated words and filler phrases ("actually", "basically", "just", "really", "very")
- Inconsistent capitalization of proper nouns and technical terms
- Broken markdown (unclosed links, missing alt text, heading level jumps)

Output format: Return the corrected text with a summary of changes made.

**Rule: Preserve the author's sentence structure and word choices. Only fix errors, never "improve" style.**

#### 3. Outline Mode -- Story Structure

Given a topic or rough notes, generate a structured outline using one of the narrative templates (see Storytelling Patterns below). Ask the author which template fits before generating.

Output: A markdown outline with section headers, one-sentence descriptions of what each section should accomplish, and placeholder hooks for narrative beats (the moment of confusion, the failed attempt, the breakthrough).

### Tier 2: Valuable (Build Second)

#### 4. SEO Metadata Generation

Given a finished post, generate:

- Title tag (under 60 characters, primary keyword near the front)
- Meta description (120-160 characters, includes a call to curiosity)
- Suggested `<h2>` restructuring if headers are too vague for search
- Internal link suggestions to existing posts (once more posts exist)

#### 5. Voice Profile

A reference document (stored alongside the skill) that captures the author's writing patterns. Built from samples of existing writing. Includes:

- Typical sentence length range
- Vocabulary preferences and avoidances
- Tone markers (casual/formal, humorous/earnest, first-person usage)
- Recurring stylistic choices (sentence fragments for emphasis, parenthetical asides, etc.)

The skill references this profile during Review and Polish to avoid flattening voice into generic AI prose.

#### 6. Readability Report

Compute and display:

- Estimated reading time (based on 230 WPM average)
- Average sentence length (target: 15-20 words for tech blogs)
- Longest sentence (flag if over 35 words)
- Passive voice percentage (flag if over 15%)
- Flesch-Kincaid grade level (target: 8-10 for dev blogs, per Yoast and readability research)
- Paragraph length distribution (flag any over 6 sentences)

### Tier 3: Nice-to-Have (Build Later)

#### 7. Publish Prep

Generate the complete blog post file with correct frontmatter, filename (`YYYY-MM-DD-slug.md`), and place it in `src/content/blog/`. Validate against the content collection schema.

#### 8. Series Management

For multi-part posts, manage cross-linking, consistent numbering, "previously in this series" blocks, and a series index page.

#### 9. Draft-to-Thread

Convert a blog post into a concise social media thread (5-10 posts) for sharing. Preserve key insights, strip detail, add hooks.

---

## Developer Blog Storytelling Patterns

The skill should offer these as selectable templates during Outline Mode.

### Pattern 1: The Build Log (Struggle-Discovery-Resolution)

Inspired by Julia Evans' advice to "blog about what you've struggled with." The post follows the actual chronological experience, including wrong turns and confusion.

```
1. THE ITCH      -- What I was trying to do, and why
2. FIRST ATTEMPT -- What I tried first (and why it seemed reasonable)
3. THE WALL      -- Where it broke, what confused me
4. THE HUNT      -- Debugging, reading docs, searching, asking
5. THE CLICK     -- The insight that unlocked the solution
6. THE FIX       -- What I actually did (code, config, architecture)
7. THE TAKEAWAY  -- What I know now that I didn't before
```

**Why it works:** Readers learn not just the solution but the diagnostic process. The struggle creates tension; the resolution provides payoff. Julia Evans' most popular posts follow this shape -- they're specific, honest about confusion, and generous with the "aha" moment.

**Best for:** Debugging stories, learning a new tool, solving an obscure problem.

### Pattern 2: The Story Spine (Problem-Journey-Solution)

Adapted from Pixar's story spine framework (used by Anvil's engineering team for technical posts):

```
1. ONCE UPON A TIME  -- Here's the system/project/context
2. EVERY DAY         -- Here's how things normally worked
3. ONE DAY           -- Something changed or broke
4. BECAUSE OF THAT   -- Here's what happened as a consequence
5. BECAUSE OF THAT   -- And then this happened (escalation)
6. UNTIL FINALLY     -- Here's how we solved it
7. AND EVER SINCE    -- Here's the new normal (and what we learned)
```

**Why it works:** It naturally creates rising action. The "because of that" chain forces the writer to show causation, not just sequence. Readers understand *why* decisions were made.

**Best for:** Project retrospectives, architecture decisions, migration stories.

### Pattern 3: The Explainer (Concept Made Concrete)

Inspired by Dan Abramov's style on Overreacted -- take an abstract concept and make it tangible through examples, analogies, and progressive disclosure.

```
1. THE HOOK          -- A surprising claim or question
2. THE INTUITION     -- Build the reader's mental model with analogy
3. THE MECHANISM     -- How it actually works (with code)
4. THE EDGE CASE     -- Where the intuition breaks down
5. THE REVISED MODEL -- The more complete understanding
6. THE IMPLICATION   -- Why this matters for their work
```

**Why it works:** It respects the reader's time by leading with value. The "revised model" step is key -- it shows the writer isn't oversimplifying, which builds trust.

**Best for:** Explaining a concept, library, pattern, or mental model.

### Pattern 4: The Decision Record (Options-Tradeoffs-Choice)

Hillel Wayne's style -- rigorous, evidence-based, shows the full decision space.

```
1. THE CONTEXT       -- What we were building and the constraints
2. THE OPTIONS       -- What approaches we considered (at least 3)
3. THE CRITERIA      -- How we evaluated them (performance, DX, maintenance)
4. THE ANALYSIS      -- Honest assessment of each option
5. THE DECISION      -- What we chose and why
6. THE AFTERMATH     -- How it played out in practice
```

**Why it works:** Developers respect thoroughness. Showing rejected options proves the decision was considered, not arbitrary.

**Best for:** Architecture decisions, tool selection, framework comparisons.

### Pattern 5: The Narrative TIL (Today I Learned, Extended)

Short-form. Xe Iaso's blog has over 400 articles because many are focused, digestible pieces.

```
1. THE THING         -- What I learned (stated plainly)
2. THE CONTEXT       -- When/why I encountered it
3. THE DETAIL        -- The interesting nuance or gotcha
4. THE CODE          -- Working example
5. THE NOTE          -- One sentence on when you'd use this
```

**Why it works:** Low barrier to write, high signal-to-noise for readers. Accumulates into a searchable knowledge base.

**Best for:** Small discoveries, gotchas, tips, "did you know" style posts.

---

## Proofreading Rules and Style Guidance

### Rules the Skill Should Enforce (Polish Mode)

These are mechanical, unambiguous corrections:

1. **Spelling** -- Fix typos. Use American English spelling unless the voice profile specifies otherwise.
2. **Grammar** -- Fix agreement errors, dangling modifiers, comma splices.
3. **Punctuation** -- Consistent Oxford comma usage (default: use it). Em-dashes with no surrounding spaces (`word--word` in markdown renders as `word--word`). Curly quotes are unnecessary in markdown.
4. **Markdown hygiene** -- Ensure heading levels don't skip (no jumping from `##` to `####`). Close all link brackets. Add alt text to images. Use fenced code blocks with language hints.
5. **Filler words** -- Flag (don't auto-remove) these: "just", "really", "very", "actually", "basically", "simply", "obviously", "clearly", "of course". These often weaken prose but sometimes serve a purpose.
6. **Repeated sentence openers** -- Flag 3+ consecutive sentences starting with the same word (especially "I", "The", "It", "This").
7. **Weasel words** -- Flag vague quantifiers: "some", "many", "most", "often", "sometimes", "usually" when used without evidence.
8. **Technical term consistency** -- If the post uses both "JavaScript" and "Javascript", or "frontend" and "front-end", flag the inconsistency.
9. **Code/prose mismatch** -- If a variable is named `getUserById` in code but referred to as "the get user function" in prose, flag it.

### Rules the Skill Should NOT Enforce

These are style choices that belong to the author:

1. **Sentence length** -- Report it, don't fix it. Some writers use long sentences effectively.
2. **Sentence fragments** -- Common in dev blogs for emphasis. Don't "fix" them.
3. **Contractions** -- Don't expand or contract. Match what the author wrote.
4. **First person** -- Dev blogs are personal. Don't suggest removing "I".
5. **Informal tone** -- Don't formalize casual phrasing like "it's kinda weird" into "it is somewhat unusual."
6. **Swearing** -- Some dev blogs use mild profanity for emphasis. Don't censor.
7. **Paragraph length** -- Report but don't restructure. The author controls pacing.

### Style Guidance for Review Mode

These are structural observations, not corrections:

1. **The Meandering Opening** -- If the post doesn't state its thesis or hook within the first 2-3 paragraphs, flag it. Per Michael Lynch (Refactoring English): "The biggest mistake software bloggers make is meandering, squandering the first several paragraphs on background history before sharing valuable insights."
2. **The Missing Stakes** -- If the post describes what was built but never says why it matters or what problem it solves, flag it.
3. **The Wall of Code** -- If there's a code block longer than 30 lines without surrounding explanation, suggest breaking it up or adding inline annotations.
4. **The Premature Solution** -- If the post reveals the answer before building any tension, suggest restructuring to show the problem first.
5. **The Missing Conclusion** -- If the post ends abruptly after the implementation without a takeaway, suggest adding one.
6. **The Passive Hero** -- If the post describes things "happening" without the author as an active agent ("the bug was found" vs "I found the bug"), suggest active voice.
7. **Show, Don't Tell** -- If the post says "this was really hard" without showing evidence of difficulty, suggest adding specifics.

---

## Voice Consistency Strategy

The skill should maintain a voice profile document. Here is how to bootstrap it:

### Step 1: Gather Samples

Collect 3-5 pieces of the author's existing writing -- commit messages, README sections, project descriptions, any informal writing. For Jake (the 7ab.net author), the homepage copy is a starting signal:

> "Hey! I'm Jake."
> "I like to build things, thanks for having a look."
> "Here's some of the stuff I've been working on."

This suggests: casual, direct, first-person, understated, no hype.

### Step 2: Extract Patterns

Document observed patterns:
- Sentence length tendency (short/medium/long)
- Formality level (casual/conversational/professional/academic)
- Use of humor (none/dry/playful)
- Technical depth default (surface/moderate/deep)
- Characteristic phrases or constructions

### Step 3: Create a Voice Card

A concise reference the skill consults during Review and Polish:

```yaml
voice:
  tone: casual, direct
  formality: low -- writes like talking to a friend
  person: first-person singular
  humor: understated, dry
  jargon: uses technical terms without apology but explains when helpful
  avoid:
    - corporate buzzwords ("leverage", "synergy", "utilize")
    - hedging language ("I think maybe", "it seems like perhaps")
    - performative enthusiasm ("super excited to announce")
  embrace:
    - sentence fragments for emphasis
    - contractions
    - direct address ("you", "your")
    - showing work (code, screenshots, terminal output)
```

### Step 4: Use During Editing

During Polish, if a correction would violate the voice card, don't make it. During Review, if feedback would push the writing toward a tone that contradicts the voice card, reframe the suggestion.

---

## Content Workflow Pipeline

The skill should support a four-stage pipeline, invocable by stage:

### Stage 1: Outline (`/write outline`)

**Input:** A topic, rough notes, or a brain dump.
**Process:**
1. Ask which storytelling pattern fits (or suggest one based on the content).
2. Generate a structured outline with section headers and beat descriptions.
3. Identify where the narrative tension lives.
4. Suggest a working title (can be refined later).

**Output:** A markdown outline file.

### Stage 2: Draft (`/write draft`)

**Input:** An outline (or freeform writing to be structured).
**Process:**
1. If working from an outline, the author writes the draft -- the skill does not generate prose.
2. If the author provides raw freeform text, the skill restructures it into the outline's shape without rewriting sentences.

**Output:** The author's draft, restructured if needed.

**Rule: The skill never writes prose on behalf of the author. It structures, it does not generate.**

### Stage 3: Review (`/write review`)

**Input:** A draft markdown file.
**Process:**
1. Run the structural and clarity checks (see Review Mode above).
2. Generate a readability report.
3. Check narrative arc completeness.
4. Flag voice inconsistencies against the voice profile.

**Output:** A numbered feedback list with locations and suggestions. No rewrites.

### Stage 4: Polish (`/write polish`)

**Input:** A revised draft (post-review).
**Process:**
1. Run the proofreading rules (see Polish Mode above).
2. Generate SEO metadata (title, description).
3. Validate frontmatter against the blog schema.
4. Output the final file with correct frontmatter and filename.

**Output:** A publish-ready markdown file placed in `src/content/blog/`.

---

## SEO Recommendations for Dev Blogs

Based on current best practices:

1. **Title tags** -- Under 60 characters. Put the primary topic near the front. Use concrete nouns, not vague abstractions. "How I Fixed a Memory Leak in Our WebSocket Server" beats "Lessons Learned About Performance."
2. **Meta descriptions** -- 120-160 characters. Tease the insight, don't summarize the whole post. Include the problem or result.
3. **Headers** -- Use one `<h1>` (the post title). Use `<h2>` for major sections with keyword-relevant phrasing. Use `<h3>` for subsections. Don't skip levels.
4. **Internal linking** -- Link to related posts using descriptive anchor text (not "click here"). As the blog grows, create topic clusters.
5. **URL slugs** -- Lowercase, hyphenated, descriptive. `/blog/fixing-websocket-memory-leak` not `/blog/post-3`.
6. **Code blocks** -- Use language hints for syntax highlighting. Search engines can surface code snippets.
7. **Images** -- Alt text is both accessibility and SEO. Describe what the image shows, not what it "means."
8. **Publishing cadence** -- Consistency matters more than frequency. One post per month is fine if it's quality.

---

## Skill Architecture within Tab

Based on the existing skill patterns in Tab (`research/SKILL.md`, `add-component/SKILL.md`), the writing assistant skill should follow this structure:

```
skills/
  write/
    SKILL.md              # Main skill definition
    voice-profile.yaml    # Author voice card (bootstrapped, then maintained)
    templates/            # Optional: story pattern templates
```

The `SKILL.md` frontmatter:

```yaml
---
name: write
description: "Use when drafting, reviewing, polishing, or outlining blog posts and written content. Supports staged workflow from outline to publish-ready markdown."
---
```

The skill should detect which stage the user wants from context:
- "review this post" or "give me feedback" -> Review Mode
- "proofread this" or "polish this" -> Polish Mode
- "help me outline" or "I want to write about X" -> Outline Mode
- "check the SEO" or "generate metadata" -> SEO Mode
- "how's the readability" -> Readability Report

---

## Sources

- [Julia Evans -- "Blog about what you've struggled with"](https://jvns.ca/blog/2021/05/24/blog-about-what-you-ve-struggled-with/) -- Core philosophy: write about specific struggles, not general topics
- [Anvil Engineering -- "Writing better technical blog posts with the story spine"](https://www.useanvil.com/blog/engineering/writing-technical-blog-posts-with-the-story-spine/) -- Story spine framework adapted for engineering posts
- [Michael Lynch -- "How to Write Blog Posts that Developers Read" (Refactoring English)](https://refactoringenglish.com/chapters/write-blog-posts-developers-read/) -- Inverted pyramid, don't meander, minimize reader strain
- [DevRel Bridge -- "Developer-Friendly Blog Post Structure"](https://devrelbridge.com/blog/developer-friendly-blog-post-structure) -- Hook, structure, formatting for developer audience
- [Dan Abramov -- Overreacted](https://overreacted.io/) -- Exemplar of concept-driven explainer posts
- [Xe Iaso](https://xeiaso.net/) -- Exemplar of prolific, short-form narrative technical writing (400+ posts)
- [Hillel Wayne](https://www.hillelwayne.com/) -- Exemplar of rigorous, evidence-based technical decision writing
- [Flesch-Kincaid readability tests (Wikipedia)](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests) -- Readability scoring methodology
- [Yoast -- "The Flesch reading ease score"](https://yoast.com/flesch-reading-ease-score/) -- Practical application of readability scores to web content
- [Astro Content Collections docs](https://docs.astro.build/en/guides/content-collections/) -- Content collection setup for blog posts
- [Astro MDX integration](https://docs.astro.build/en/guides/integrations-guide/mdx/) -- MDX support for interactive blog posts
- [BSWEN -- "How to maintain voice consistency when writing with AI"](https://docs.bswen.com/blog/2026-02-23-ai-voice-consistency/) -- Voice profile technique for long-form AI-assisted writing
- [The Transmitter -- "Keeping it personal: How to preserve your voice when using AI"](https://www.thetransmitter.org/from-bench-to-bot/keeping-it-personal-how-to-preserve-your-voice-when-using-ai/) -- Preserving author voice in AI-assisted editing
- [scalarly.com -- "Draft to Publish-Ready"](https://scalarly.com/marketing-book/draft-to-publish-ready-clarity-tone-and-the-modern-polish-pass/) -- Modern polish pass workflow
- [SalesHive -- "SEO Meta Data Best Practices"](https://saleshive.com/blog/seo-meta-data-best-practices-rankings-2025/) -- Title tag and meta description guidelines
- [Sheffield Hallam University -- "Proofreading with Generative AI"](https://libguides.shu.ac.uk/ai/proofreading) -- Limitations of AI proofreading, preserving disciplinary voice

---

## Recommendations

1. **Build the skill in this order:** Review Mode first, then Polish Mode, then Outline Mode. Review is where the most value lives -- it's the hardest thing to do well on your own.

2. **Bootstrap the voice profile early.** Even a rough voice card prevents the skill from flattening Jake's casual, direct tone into generic AI prose. Use the existing site copy as a starting sample.

3. **Set up the blog infrastructure in 7ab.net before writing the first post.** The content collection, layout, listing page, and routing are prerequisites. This is a separate task from the skill but should happen in parallel.

4. **Start with the Build Log pattern.** Jake is actively building Tab -- that's a natural first post. "How I'm building an agent framework as markdown files" writes itself with Pattern 1.

5. **Keep the skill's scope narrow.** It reviews, it proofreads, it outlines. It does not generate prose. This is the single most important design decision. AI writing assistants that generate text train the author to stop writing; AI writing assistants that give feedback train the author to write better.
