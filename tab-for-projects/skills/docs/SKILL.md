---
name: docs
description: "Write generic knowledgebase documents — conventions, guides, references, and decisions that apply across any project."
argument-hint: "[topic or focus area]"
---

# Docs

Write knowledgebase documents that are **project-agnostic by design**. The user is creating reusable knowledge artifacts — conventions, architectural patterns, guides, reference material — meant to travel across codebases. The current codebase is a source of understanding and inspiration, never the subject.

## Trigger

**When to activate:**
- User invokes `/docs`
- User says "let's write docs," "help me document," "I want to capture this pattern"

**When NOT to activate:**
- User wants to document a specific codebase's decisions or patterns → that's `/document`
- User wants to implement code → that's `/dev`
- User wants a quick explanation → just answer directly

## Requires

- **MCP:** tab-for-projects — for creating, searching, and updating KB documents.

## Behavior

### The Core Imperative

**Documentation produced by this skill is NEVER specific to the current codebase.** Every document must be useful to someone who has never seen this repo. If a document references a specific file path, class name, or project-specific convention, it has failed.

The codebase is a lens, not the subject. Read it to understand *how* a pattern works in practice, then write about the pattern itself.

### 1. Understand the Topic

Before writing, build understanding from two directions:

**From the user:** What do they want to document? What's the scope? Who's the audience — future agents, human developers, both?

**From the codebase (when relevant):** If the user is documenting a pattern they use, read the code to understand it concretely. Follow imports, read implementations, trace the flow. This grounds your writing in reality rather than abstraction.

**From the KB:** Search existing documents before writing. Check for overlap, related material, or documents that should be updated rather than duplicated.

```
list_documents({ search: "topic keywords" })
list_documents({ tag: "conventions" })
list_documents({ tag: "guide" })
list_documents({ favorite: true })
```

### 2. Shape the Document

Talk through the document's shape with the user before writing:

- **What type of document is this?** (See Document Formats below)
- **What tags apply?** (See Tag Map below)
- **What folder does it belong in?** (See Folder Map below)
- **Does an existing document cover this?** If so, propose updating it instead.

For straightforward requests, skip the discussion and draft directly — judgment over ceremony.

### 3. Write It

Every document must meet these criteria:

- **Generic.** No project-specific file paths, class names, or implementation details. Use illustrative examples instead of real ones when concrete references would tie the doc to a codebase.
- **Self-contained.** A reader with no context about the current project can understand and apply this document.
- **Actionable.** The reader should know what to *do* after reading, not just what to *think*.
- **Tagged.** Every document gets 1-3 tags from the closed enum. Non-negotiable.

Write the content, then call `create_document` or `update_document`:

```
create_document({ items: [{
  title: "...",
  summary: "...",       // max 500 chars — this is what appears in list views
  content: "...",       // the full document, markdown, max 50k chars
  tags: ["..."],        // 1-3 tags from the closed enum
  favorite: false       // true only for high-value references
}] })
```

After creating, ask the user if they want to attach it to a project:

```
update_project({ items: [{ id: "...", attach_documents: ["new-doc-id"] }] })
```

### 4. Review and Refine

After writing, review with the user:

- Does this read well to someone outside this project?
- Are there project-specific details that leaked in?
- Is the scope right — not too broad (encyclopedia entry) or too narrow (commit message)?

## Output

### Document Formats

Use the format that fits the content. Don't force a template where it doesn't belong.

#### Convention Document

For established patterns, naming rules, code style norms, or structural decisions that should be followed consistently.

```markdown
## [Convention Name]

[1-2 sentence summary of what this convention is and why it exists.]

### The Rule

[Clear, unambiguous statement of what to do.]

### Examples

[Show the convention applied — good and bad examples if helpful.]

### Rationale

[Why this convention over alternatives. What problem does it solve?]

### Exceptions

[When it's OK to break this rule, if ever.]
```

Tags: `conventions`, plus a domain or concern tag.

#### Guide

For how-to knowledge — walkthroughs, workflows, setup procedures, or techniques.

```markdown
## [Guide Title]

[What this guide covers and who it's for.]

### Prerequisites

[What the reader needs to know or have in place.]

### Steps

[Numbered or sectioned walkthrough. Concrete enough to follow, generic enough to apply anywhere.]

### Common Pitfalls

[What goes wrong and how to avoid it.]
```

Tags: `guide`, plus a domain or concern tag.

#### Architecture Pattern

For structural decisions, component relationships, and system design approaches.

```markdown
## [Pattern Name]

[1-2 sentence summary.]

### When to Use

[The problem this pattern solves. What conditions make it the right choice?]

### How It Works

[Description of the pattern's structure and mechanics.]

### Trade-offs

[What you gain, what you give up, when to reconsider.]

### Variations

[Common variations or adaptations of this pattern.]
```

Tags: `architecture`, plus relevant domain or concern tags.

#### Decision Record

For recording the reasoning behind a choice that applies broadly — not project-specific decisions, but general technical positions.

```markdown
## Decision: [What Was Decided]

**Context:** [The problem or question that prompted a decision.]
**Decision:** [What was chosen.]
**Alternatives:** [What else was considered.]
**Trade-offs:** [What was gained and lost.]
**Applies when:** [Conditions where this decision is relevant.]
**Revisit when:** [What would change this decision.]
```

Tags: `decision`, plus relevant domain or concern tags.

#### Reference Document

For lookup material — API patterns, configuration shapes, enum definitions, or taxonomy tables.

```markdown
## [Topic] Reference

[What this reference covers.]

### [Section]

[Tables, lists, or structured data. Optimize for scanning, not reading.]
```

Tags: `reference`, plus relevant domain or concern tags.

#### Troubleshooting Guide

For recurring problems, non-obvious failure modes, or diagnostic procedures.

```markdown
## Troubleshooting: [Area]

### [Symptom]

**Cause:** [What's actually happening.]
**Diagnosis:** [How to confirm this is the issue.]
**Fix:** [What to do.]
**Prevention:** [How to avoid it in the future.]
```

Tags: `troubleshooting`, plus relevant domain or concern tags.

### Tag Map

Tags are a **closed enum** — only these 15 values are valid. Every document gets 1-3 tags.

#### Domain Tags

What area of a system the document relates to.

| Tag | Use for |
|-----|---------|
| `ui` | Frontend, user interface, components, layouts, interaction patterns |
| `data` | Data models, schemas, storage, serialization, validation |
| `integration` | How components connect — APIs, contracts, boundaries, protocols |
| `infra` | Infrastructure, deployment, CI/CD, environments, tooling |
| `domain` | Business logic, domain modeling, rules, workflows |

#### Content Type Tags

What kind of document this is.

| Tag | Use for |
|-----|---------|
| `architecture` | Structural patterns, system design, component relationships |
| `conventions` | Naming rules, file organization, code style, established norms |
| `guide` | How-to walkthroughs, techniques, procedures |
| `reference` | Lookup tables, API shapes, config formats, enums |
| `decision` | Decision records with rationale and trade-offs |
| `troubleshooting` | Failure modes, diagnostic procedures, gotchas |

#### Concern Tags

Cross-cutting concerns the document addresses.

| Tag | Use for |
|-----|---------|
| `security` | Auth, authorization, secrets, vulnerability patterns |
| `performance` | Optimization, profiling, caching, resource management |
| `testing` | Test strategy, patterns, coverage, fixtures, mocking |
| `accessibility` | A11y patterns, screen readers, keyboard navigation, ARIA |

#### Tagging Heuristic

Pick tags in this order:

1. **One content type tag** — what kind of document is this? Almost always applies.
2. **One domain tag** — what area does it cover? Skip if it genuinely spans all domains.
3. **One concern tag** — does it address a cross-cutting concern? Only if relevant.

### Folder Map

Folders are flat, lowercase, alphanumeric with hyphens, max 64 chars. They organize documents by broad topic area — not by project.

| Folder | What goes here |
|--------|---------------|
| `conventions` | Code style, naming, file structure, commit conventions |
| `patterns` | Architectural and design patterns, structural approaches |
| `guides` | How-to documents, workflows, techniques |
| `references` | Lookup tables, API patterns, config shapes |
| `decisions` | Decision records, technical positions |
| `troubleshooting` | Diagnostic guides, failure modes, gotchas |
| `security` | Security patterns, auth approaches, threat models |
| `testing` | Test strategy, patterns, fixtures, coverage approaches |
| `infrastructure` | CI/CD, deployment, environment management |
| `lore` | Hard-won insights, war stories, tribal knowledge — things you only learn by getting burned |

Create new folders when an existing one doesn't fit. Follow the same naming convention — lowercase, descriptive, singular-or-plural matching the existing set.

When setting a folder:

```
create_document({ items: [{ title: "...", folder: "conventions", ... }] })
```

## Constraints

- **Never project-specific.** This is the load-bearing rule. Every document must be useful outside the current codebase. If you catch yourself writing a file path or class name from the current project, stop and generalize.
- **Update before create.** If an existing document covers the same ground, update it. The KB should grow in depth, not just breadth.
- **The user decides scope.** You bring knowledge and opinions about what's worth documenting. They decide what to write and how much.
- **Tag everything.** A document without tags is invisible to future searches. Non-negotiable.
- **Read the code, write the principle.** The codebase informs your understanding. The document captures the transferable insight.
