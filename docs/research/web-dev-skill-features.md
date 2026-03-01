# Research: Web-Dev Skill Features for Tab

**Date:** 2026-03-01
**Tier:** Deep
**Tools used:** WebSearch (12 queries), codebase analysis (Glob, Read, Bash)

## Question

What features should a Tab web-dev skill provide for AI-assisted development of the 7ab.net Astro site, and in what order should they be built?

---

## Executive Summary

The 7ab.net project is an early-stage personal site built on Astro 5 with vanilla CSS design tokens, Google Fonts (Lora), dark mode via `prefers-color-scheme`, and GitHub Pages hosting. The codebase is small (8 source files), statically generated, and has no JavaScript framework dependencies -- a clean foundation with significant room to grow.

A web-dev skill should focus on **five high-impact capabilities in this order**:

1. **Component & page scaffolding** -- the single highest-leverage feature. Generates Astro components, pages, and layouts that follow the project's existing conventions (design tokens, typed props, scoped styles).
2. **Content system setup** -- wire up Astro Content Collections + MDX for a blog. The `src/content/config.ts` is already present but empty, signaling intent.
3. **SEO & meta enrichment** -- structured data (JSON-LD), Open Graph images, sitemap, RSS feed. The Base layout already has basic OG tags; the skill extends this.
4. **Design system expansion** -- dark mode toggle, spacing/typography audit, responsive utilities, new token categories (shadows, radii, z-indices).
5. **Performance & accessibility guardrails** -- image optimization via `astro:assets`, a11y checklist enforcement, Lighthouse score guidance.

Build 1-2 first. They unlock the most new functionality. Build 3-5 as the site grows. Testing, deployment, and view transitions are lower priority given the current project size and existing GitHub Actions pipeline.

---

## Analysis of the 7ab.net Project Stack

### Tech Stack Summary

| Layer | Choice | Notes |
|-------|--------|-------|
| Framework | Astro 5.17+ | Static output (`astro build`), no SSR adapter |
| Styling | Vanilla CSS | Custom properties as design tokens, scoped `<style>` blocks per component |
| Typography | Lora (Google Fonts) + system-ui sans | Serif headings, sans body |
| Dark mode | `prefers-color-scheme` media query | No JS toggle, no `data-theme` attribute |
| Content | TypeScript data file (`src/data/projects.ts`) | Content Collections config exists but is empty |
| Deployment | GitHub Pages | CNAME file for `7ab.net`, GitHub Actions CI |
| TypeScript | Strict mode (`astro/tsconfigs/strict`) | Typed component props via `interface Props` |

### Architecture Observations

**Strengths:**
- Clean design token system with 5 color tokens, 4 spacing tokens, 2 max-width tokens, and 2 font stacks. All components reference tokens exclusively -- no magic numbers.
- Good a11y baseline: `aria-label`, `aria-current`, `role="list"`, skip-link utility class (`.sr-only`), semantic HTML.
- TypeScript interfaces for component props (`Base.astro`, `ProjectCard.astro`) and data models (`Project` interface).
- Scoped styles per component -- no CSS leakage.

**Gaps to address:**
- No blog/content pages. The `src/content/config.ts` exports an empty `collections` object.
- No `<Image>` component usage (Astro's built-in image optimization). Images are not yet part of the site.
- No sitemap, RSS feed, or robots.txt.
- No structured data (JSON-LD).
- No view transitions.
- Dark mode is automatic-only (no user toggle).
- No testing of any kind.
- No MDX integration.

### File-by-File Reference

| File | Role |
|------|------|
| `src/layouts/Base.astro` | HTML shell, `<head>` meta, Nav, footer. Accepts `title` and `description` props. |
| `src/components/Nav.astro` | Header nav with active-link detection. Links array is hardcoded. |
| `src/components/ProjectCard.astro` | Card component consuming `Project` type. Tags, optional GitHub/URL links. |
| `src/pages/index.astro` | Home page. Hero section + featured project grid. |
| `src/pages/projects.astro` | All projects grid. |
| `src/data/projects.ts` | Typed project data. Currently has 1 entry (Tab). |
| `src/content/config.ts` | Empty Content Collections config -- placeholder. |
| `src/styles/global.css` | Design tokens, reset, base typography, layout helpers, utilities. |

---

## Feature Categories Ranked by Impact and Effort

The ranking considers: (a) how much new capability it unlocks, (b) how well it fits the current project stage, (c) effort to build as a Tab skill.

| Rank | Feature | Impact | Effort | Priority |
|------|---------|--------|--------|----------|
| 1 | Component & page scaffolding | High | Medium | **Build first** |
| 2 | Content system (blog/MDX) | High | Medium | **Build first** |
| 3 | SEO & meta enrichment | High | Low | **Build second** |
| 4 | Design system expansion | Medium | Low | **Build second** |
| 5 | Accessibility checking | Medium | Low | Build third |
| 6 | Performance optimization | Medium | Low | Build third |
| 7 | View transitions | Medium | Low | Build when adding more pages |
| 8 | Deployment workflows | Low | Low | Already handled by GitHub Actions |
| 9 | Testing setup | Low | Medium | Build when codebase grows |
| 10 | Design-to-code | Low | High | Aspirational / future |

---

## Feature Proposals

### 1. Component & Page Scaffolding

**What it does:** Generates new Astro components, pages, and layouts from a natural-language description, following the project's existing conventions automatically.

**Why it matters:** This is the most frequently needed capability during active development. Every new feature starts with "create a component." An AI skill that gets the boilerplate right (design tokens, typed props, scoped styles, semantic HTML) saves the most cumulative time.

**Skill behavior:**

1. Detect what is being requested: component, page, or layout.
2. Infer the name (lowercase-hyphenated, matching Astro conventions).
3. Generate the file with:
   - Frontmatter with typed `Props` interface (when the component accepts props).
   - HTML using semantic elements and existing CSS custom properties.
   - Scoped `<style>` block referencing design tokens from `global.css`.
   - Proper imports (layout, sibling components).
4. For pages: wrap content in the `Base` layout, add the route to `Nav.astro`'s links array.
5. For components with data: create or extend a TypeScript data file in `src/data/`.

**Example invocations:**

```
"Create a blog post page that shows a single markdown post with a title, date, and reading time"

"Add a Footer component with social links and a copyright notice"

"Create an /about page with a bio section and a skills list"
```

**Example generated output (component):**

```astro
---
interface Props {
  name: string;
  role: string;
  avatarUrl?: string;
}

const { name, role, avatarUrl } = Astro.props;
---

<div class="bio">
  {avatarUrl && <img src={avatarUrl} alt={`Photo of ${name}`} class="bio__avatar" />}
  <div class="bio__text">
    <h2 class="bio__name">{name}</h2>
    <p class="bio__role">{role}</p>
  </div>
</div>

<style>
  .bio {
    display: flex;
    align-items: center;
    gap: var(--space-m);
  }

  .bio__avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
  }

  .bio__name {
    font-size: 1.25rem;
    margin-bottom: 0.25rem;
  }

  .bio__role {
    font-size: 0.9375rem;
    color: var(--color-muted);
  }
</style>
```

**Conventions the skill must enforce:**
- CSS class naming: BEM-like (`block__element`, `block--modifier`), matching `Nav.astro` and `ProjectCard.astro` patterns.
- Design tokens: only `var(--color-*)`, `var(--space-*)`, `var(--font-*)`, `var(--max-*)` -- never raw values.
- Container widths: `var(--max-prose)` for content, `var(--max-wide)` for grids.
- Typography: serif font for headings (inherited from `global.css`), sans for body.
- Accessibility: `aria-label` on icon-only links, semantic HTML elements, color contrast awareness.

**References:**
- [Agiflow scaffolding approach](https://agiflow.io/blog/toward-scalable-coding-with-ai-agent-better-scaffolding-approach/) -- template-based AI scaffolding over freeform generation.
- [Claude Code skills guide](https://code.claude.com/docs/en/skills) -- skill structure and SKILL.md format.
- Existing Tab skill: `/Users/alttab-macbook/AltT4b/Tab/skills/add-component/SKILL.md` -- pattern to follow for Tab-native component creation.

---

### 2. Content System Setup (Blog/MDX)

**What it does:** Scaffolds a blog using Astro Content Collections and MDX, with typed schemas, listing pages, individual post pages, and RSS feed.

**Why it matters:** The empty `src/content/config.ts` signals that a content system is planned. A blog is the natural next expansion for a personal site. Content Collections provide type-safe frontmatter validation, and MDX allows embedding Astro components in prose.

**Skill behavior:**

1. Install `@astrojs/mdx` integration and configure in `astro.config.mjs`.
2. Define a `blog` collection in `src/content/config.ts` with a Zod schema:
   - `title` (string, required)
   - `description` (string, required)
   - `pubDate` (date, required)
   - `updatedDate` (date, optional)
   - `tags` (string array, optional)
   - `draft` (boolean, default false)
3. Create `src/content/blog/` directory with a sample post.
4. Create `src/pages/blog/index.astro` -- listing page with date-sorted posts.
5. Create `src/pages/blog/[...slug].astro` -- dynamic post page.
6. Create a `PostCard.astro` component for the listing.
7. Create a `Prose.astro` wrapper component for markdown content styling.
8. Add "Blog" link to `Nav.astro`.
9. Optionally: install `@astrojs/rss` and create `src/pages/rss.xml.ts`.

**Example schema:**

```typescript
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

**References:**
- [Astro Content Collections docs](https://docs.astro.build/en/guides/markdown-content/)
- [Astro MDX integration](https://docs.astro.build/en/guides/integrations-guide/mdx/)
- [MDX blog guide with Astro](https://www.kozhuhds.com/blog/how-to-build-a-static-lightweight-mdx-blog-with-astro-step-by-step-guide/)
- [Astro advanced markdown tips](https://eastondev.com/blog/en/posts/dev/20251202-astro-mdx-advanced-guide/)

---

### 3. SEO & Meta Enrichment

**What it does:** Extends the existing Base layout with structured data, OG images, sitemap, robots.txt, and RSS metadata.

**Why it matters:** The site already has basic OG tags and a canonical URL, which is a solid start. But it lacks structured data (which enables rich search results), a sitemap (which aids indexing), and an OG image (which controls social sharing previews). These are low-effort, high-visibility improvements.

**Skill behavior:**

1. **Structured data:** Add JSON-LD `<script>` blocks to `Base.astro` for `WebSite`, `Person`, and (for blog posts) `Article` schemas.
2. **Sitemap:** Install `@astrojs/sitemap`, add to `astro.config.mjs` (site URL already configured).
3. **Robots.txt:** Create `public/robots.txt` pointing to the sitemap.
4. **OG image support:** Add an `ogImage` prop to `Base.astro` for per-page social images. Default to a site-wide fallback.
5. **Twitter card meta:** Add `twitter:card`, `twitter:title`, `twitter:description` tags.
6. **RSS discovery:** Add `<link rel="alternate" type="application/rss+xml">` to `<head>` when RSS is available.

**Example JSON-LD for homepage:**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "7ab",
  "url": "https://7ab.net",
  "author": {
    "@type": "Person",
    "name": "Jake",
    "url": "https://7ab.net"
  }
}
</script>
```

**References:**
- [Complete Astro SEO guide](https://eastondev.com/blog/en/posts/dev/20251202-astro-seo-complete-guide/) -- meta tags, structured data, sitemap
- [Astro SEO optimization guide](https://astrojs.dev/articles/astro-seo-optimization/)
- [Astro sitemap integration](https://docs.astro.build/en/guides/integrations-guide/sitemap/) (official docs link from search results)
- `src/layouts/Base.astro` (lines 18-29) -- existing OG/meta implementation

---

### 4. Design System Expansion

**What it does:** Extends the existing design token system with new token categories, a user-controlled dark mode toggle, and responsive utility patterns.

**Why it matters:** The current design token system is well-structured but minimal. As the site grows, more tokens are needed. The dark-mode implementation is automatic-only, which frustrates users who want manual control. Both are low-effort extensions of what already exists.

**Skill behavior:**

1. **New token categories:** Add to `global.css`:
   - `--radius-*` (small, medium, large) -- currently hardcoded as `8px` and `3px`
   - `--shadow-*` (subtle, medium) -- for card hover states
   - `--z-*` (nav, modal, toast) -- z-index scale
   - `--transition-*` (fast, normal) -- currently hardcoded as `0.15s ease`
   - `--color-surface` -- for card backgrounds distinct from page bg

2. **Dark mode toggle:** Add a `ThemeToggle.astro` component that:
   - Reads `localStorage` for saved preference
   - Falls back to `prefers-color-scheme`
   - Sets a `data-theme="dark|light"` attribute on `<html>`
   - Refactor `@media (prefers-color-scheme: dark)` block to also respond to `[data-theme="dark"]`
   - Inline the initialization script in `<head>` to prevent flash of wrong theme (FOWT)

3. **Responsive utilities:** Formalize breakpoints as documented conventions:
   - `480px` (already used in `Nav.astro`)
   - `768px` (tablet)
   - `1024px` (desktop)

4. **Token audit command:** The skill can audit existing components for hardcoded values and suggest token replacements.

**Example dark mode toggle pattern:**

```astro
<button class="theme-toggle" aria-label="Toggle dark mode" type="button">
  <span class="theme-toggle__icon" aria-hidden="true"></span>
</button>

<script>
  const toggle = document.querySelector('.theme-toggle');
  const getTheme = () => localStorage.getItem('theme')
    || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  document.documentElement.dataset.theme = getTheme();

  toggle?.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('theme', next);
  });
</script>
```

**References:**
- [CSS custom properties complete guide 2026](https://devtoolbox.dedyn.io/blog/css-custom-properties-complete-guide)
- [Dark mode implementation guide 2025](https://medium.com/design-bootcamp/the-ultimate-guide-to-implementing-dark-mode-in-2025-bbf2938d2526)
- `src/styles/global.css` (lines 1-28) -- existing token system and dark mode block

---

### 5. Accessibility Checking

**What it does:** Provides an a11y audit checklist and automated checking guidance specific to the project's component patterns.

**Why it matters:** The site already has good a11y practices (aria attributes, semantic HTML, skip-link class). A skill that enforces these consistently across new components prevents regression as the site grows. Automated tools like Pa11y CI can run in the existing GitHub Actions pipeline.

**Skill behavior:**

1. **Component audit:** When generating or reviewing components, check for:
   - Images: `alt` text present and descriptive
   - Links: distinguish between decorative and navigational, add `aria-label` when text is not descriptive
   - Color contrast: warn if custom colors are used outside the token system
   - Focus indicators: verify `:focus-visible` outlines on interactive elements
   - Heading hierarchy: no skipped levels
   - Form inputs: associated `<label>` elements

2. **Automated testing setup:** Guide the user to add Pa11y CI to their GitHub Actions workflow:
   - Install `pa11y-ci` as a dev dependency
   - Create `.pa11yci.json` config
   - Add a CI step that builds, previews, and runs Pa11y against all routes

3. **Checklist output:** When asked "check accessibility," audit all pages and components against WCAG 2.2 AA criteria and output findings as a checklist.

**References:**
- [Automated a11y testing in Astro with Pa11y CI](https://www.jmejia.com/blog/post/09-15-2025-astro-a11y/)
- [Accessible Astro documentation](https://accessible-astro.incluud.dev/getting-started/accessibility/)
- [Accessible Astro accessibility testing](https://accessible-astro.incluud.dev/getting-started/accessibility-testing/)
- `src/components/Nav.astro` (lines 13-15) -- existing aria-label and aria-current usage

---

### 6. Performance Optimization

**What it does:** Guides image optimization, font loading strategy, and build output analysis.

**Why it matters:** Astro sites are fast by default, but images (once added) and fonts are the main performance risks. The site currently loads Google Fonts via a render-blocking `<link>` -- this can be optimized. As images are added to project cards or blog posts, the `astro:assets` Image component should be used from the start.

**Skill behavior:**

1. **Image optimization:** When adding images to any component or page:
   - Use `import { Image } from 'astro:assets'` instead of raw `<img>` tags
   - Specify `width` and `height` to prevent layout shift
   - Use `loading="lazy"` for below-the-fold images (Astro's default)
   - Prefer `.webp` or `.avif` source formats

2. **Font optimization:** Suggest self-hosting Lora instead of Google Fonts CDN:
   - Download font files, place in `public/fonts/`
   - Replace `<link>` tags with `@font-face` declarations using `font-display: swap`
   - Add `preload` hints for the primary weight

3. **Build analysis:** After `astro build`, report on:
   - Total output size
   - Largest files
   - Any JavaScript bundles (should be zero or minimal for a static site)

**References:**
- [Astro image optimization guide](https://eastondev.com/blog/en/posts/dev/20251203-astro-image-optimization-guide/)
- [Astro build performance optimization](https://markaicode.com/optimize-astro-build-performance/)
- `src/layouts/Base.astro` (lines 36-41) -- current Google Fonts loading

---

### 7. View Transitions

**What it does:** Adds smooth page-to-page transitions using Astro's built-in View Transitions support.

**Why it matters:** View transitions make a multi-page Astro site feel like a single-page app with minimal code. Browser support exceeded 85% in 2025. However, this is lower priority for a small site with only 2 pages.

**Skill behavior:**

1. Import `ViewTransitions` from `astro:transitions` in `Base.astro`.
2. Add `<ViewTransitions />` to the `<head>`.
3. Add `transition:name` to key elements that should animate between pages (e.g., the nav logo, page title).
4. Choose an animation: `fade` (default, recommended), `slide`, or custom.
5. Add `transition:persist` to elements that should survive navigation (e.g., a future audio player or theme toggle).

**Example (2 lines added to Base.astro):**

```astro
---
import { ViewTransitions } from 'astro:transitions';
// ... existing imports
---
<head>
  <!-- existing meta tags -->
  <ViewTransitions />
</head>
```

**References:**
- [Astro view transitions docs](https://docs.astro.build/en/guides/view-transitions/)
- [Astro view transitions guide](https://eastondev.com/blog/en/posts/dev/20251202-astro-view-transitions-guide/) -- performance tips and pitfalls
- [Chrome View Transitions blog post](https://developer.chrome.com/blog/astro-view-transitions)

---

### 8. Deployment Workflows

**What it does:** Provides commands for build, preview, and deploy operations.

**Why it matters:** The site already deploys via GitHub Actions on push to `main`. This is already working. A skill here adds marginal value -- mostly convenience wrappers around `npm run build` and `npm run preview`.

**Skill behavior:**

1. `build` -- run `npm run build`, report output size and any warnings.
2. `preview` -- run `npm run preview`, open browser.
3. `deploy` -- verify branch, run build, push to trigger GitHub Actions.
4. If no GitHub Actions workflow exists, scaffold `.github/workflows/deploy.yml` using the official `withastro/action`.

**Recommendation:** Deprioritize. The existing setup works. Only build this if the user asks for deployment help.

**References:**
- [Astro GitHub Pages deployment](https://docs.astro.build/en/guides/deploy/github/)
- [withastro/action GitHub Action](https://github.com/withastro/action)

---

### 9. Testing Setup

**What it does:** Configures Vitest for component testing and optionally Playwright for end-to-end testing.

**Why it matters:** The site has no tests. For a personal site with 8 source files, this is not urgent. But as the codebase grows (especially with a blog), basic smoke tests prevent regressions.

**Skill behavior:**

1. Install Vitest and configure with `getViteConfig` for Astro.
2. Create a sample component test using the Astro container API.
3. Optionally add Playwright for e2e tests (navigation, dark mode toggle).
4. Optionally add Vitest 4.0 visual regression testing.

**Recommendation:** Build when the site has 5+ pages or dynamic behavior. Not needed yet.

**References:**
- [Astro testing docs](https://docs.astro.build/en/guides/testing/)
- [Vitest Browser Astro plugin](https://github.com/ascorbic/vitest-browser-astro/)
- [Astro component unit tests guide](https://angelika.me/2025/02/01/astro-component-unit-tests/)
- [Vitest 4.0 visual regression](https://main.vitest.dev/guide/browser/visual-regression-testing)

---

### 10. Design-to-Code (Aspirational)

**What it does:** Takes a design description (or screenshot) and generates matching Astro components using the project's design tokens.

**Why it matters:** This is the highest-leverage long-term capability for AI-assisted web development, but it requires the most sophisticated prompting and is hardest to get right consistently. Better as a future enhancement once the foundational skill capabilities are proven.

**References:**
- [AI in frontend development workflows](https://blog.logrocket.com/frontend-ai-tools-for-developers/)
- [AI-assisted development best practices 2026](https://dev.to/austinwdigital/ai-assisted-development-in-2026-best-practices-real-risks-and-the-new-bar-for-engineers-3fom)

---

## Competitive Landscape: What AI Coding Tools Offer for Web Dev

| Feature | Cursor | Copilot | Windsurf | Claude Code |
|---------|--------|---------|----------|-------------|
| Inline completions | Yes | Yes | Yes | No (terminal-based) |
| Multi-file edits | Yes (Composer) | Yes (Edits) | Yes (Cascade) | Yes (native) |
| Codebase indexing | Full project | Repo-level | Auto-context | 200K token window |
| Component generation | Prompt-driven | Tab completion | Agent-driven | Prompt-driven |
| Framework awareness | Via context | Trained on public code | Via context | Via CLAUDE.md + skills |
| Custom workflows | Rules files | `.github/copilot-instructions.md` | Cascade rules | Skills (SKILL.md) |
| Scaffolding | Manual prompts | Manual prompts | Turbo mode | Skills + slash commands |

**Key insight:** Claude Code's unique advantage is the **skill system** -- persistent, project-specific instructions that encode domain knowledge. A web-dev skill in Tab can carry project conventions (design tokens, component patterns, file structure) that other tools rediscover on every prompt. This is the "intelligent scaffolding" approach described by Agiflow: teach the AI templates, not just code generation.

**What to adopt from competitors:**
- **Cursor's Composer:** The concept of planning then executing across multiple files. The web-dev skill should think in terms of "feature scaffolding" (create component + page + data + styles + nav update) rather than single-file generation.
- **Windsurf's Cascade:** Autonomous multi-step execution. The skill should chain steps (e.g., "create blog" triggers collection config + sample post + listing page + RSS + nav update) without requiring the user to invoke each step separately.
- **Copilot's framework training:** The skill compensates for this by embedding Astro-specific knowledge (island architecture rules, content collection patterns, `client:*` directive guidance) directly in the skill instructions.

---

## Recommended Skill Structure

Based on Tab's skill conventions and the features above, the web-dev skill should be structured as:

```
skills/
└── web-dev/
    └── SKILL.md
```

The `SKILL.md` should cover all feature categories in a single skill file, using workflow sections. This keeps it discoverable (one skill to invoke) while being comprehensive. Claude loads the full skill content at under 5K tokens, which is well within budget.

**Alternative:** Split into multiple skills (`scaffold-component`, `add-blog`, `seo-audit`, `a11y-check`). This is more modular but increases discovery overhead. Recommendation: start with one unified `web-dev` skill and split later if it grows beyond ~4K tokens of instruction content.

### Frontmatter

```yaml
---
name: web-dev
description: "Use when creating, modifying, or auditing web pages, components, styles, or content for an Astro site. Covers scaffolding, SEO, accessibility, performance, and content management."
---
```

### Key Sections to Include

1. **Project context** -- reference the target project's design tokens, conventions, file structure.
2. **Scaffolding workflow** -- step-by-step for components, pages, layouts.
3. **Content workflow** -- Content Collections setup, blog post creation, MDX configuration.
4. **SEO checklist** -- structured data, meta tags, sitemap, RSS.
5. **Accessibility checklist** -- per-component audit criteria.
6. **Performance rules** -- image handling, font loading, bundle size awareness.

---

## Sources

- [Islands Architecture -- Astro Docs](https://docs.astro.build/en/concepts/islands/) -- Astro island architecture fundamentals
- [Astro Framework Guide: Performance, Islands & SSR (2026)](https://alexbobes.com/programming/a-deep-dive-into-astro-build/) -- Astro 5 deep dive
- [View Transitions -- Astro Docs](https://docs.astro.build/en/guides/view-transitions/) -- official view transitions guide
- [Astro View Transitions Guide](https://eastondev.com/blog/en/posts/dev/20251202-astro-view-transitions-guide/) -- practical tips and pitfalls
- [Best AI Coding Assistants 2026](https://playcode.io/blog/best-ai-coding-assistants-2026) -- tool comparison
- [Top 10 Vibe Coding Tools in 2026](https://www.nucamp.co/blog/top-10-vibe-coding-tools-in-2026-cursor-copilot-claude-code-more) -- Claude Code vs competitors
- [Best AI Coding Agents for 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026) -- agent capabilities review
- [Scaling AI-Assisted Development: The Intelligent Scaffolding Approach](https://agiflow.io/blog/toward-scalable-coding-with-ai-agent-better-scaffolding-approach/) -- template-based AI scaffolding methodology
- [AI-Assisted Development in 2026: Best Practices](https://dev.to/austinwdigital/ai-assisted-development-in-2026-best-practices-real-risks-and-the-new-bar-for-engineers-3fom) -- engineering discipline with AI tools
- [Complete Guide to Astro Website SEO](https://eastondev.com/blog/en/posts/dev/20251202-astro-seo-complete-guide/) -- Astro SEO comprehensive guide
- [Astro SEO Optimization](https://astrojs.dev/articles/astro-seo-optimization/) -- SEO checklist for Astro
- [Automated Accessibility Testing in Astro with Pa11y CI](https://www.jmejia.com/blog/post/09-15-2025-astro-a11y/) -- a11y testing in CI
- [Accessible Astro Documentation](https://accessible-astro.incluud.dev/getting-started/accessibility/) -- accessible component patterns
- [Astro Image Optimization Guide](https://eastondev.com/blog/en/posts/dev/20251203-astro-image-optimization-guide/) -- image optimization techniques
- [Astro Testing Docs](https://docs.astro.build/en/guides/testing/) -- official testing guide
- [Vitest Browser Astro](https://github.com/ascorbic/vitest-browser-astro/) -- component testing in real browsers
- [Astro MDX Integration](https://docs.astro.build/en/guides/integrations-guide/mdx/) -- official MDX guide
- [MDX Blog with Astro Guide](https://www.kozhuhds.com/blog/how-to-build-a-static-lightweight-mdx-blog-with-astro-step-by-step-guide/) -- step-by-step blog setup
- [CSS Custom Properties Guide 2026](https://devtoolbox.dedyn.io/blog/css-custom-properties-complete-guide) -- modern CSS tokens
- [Dark Mode Implementation Guide 2025](https://medium.com/design-bootcamp/the-ultimate-guide-to-implementing-dark-mode-in-2025-bbf2938d2526) -- toggle + prefers-color-scheme approach
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) -- official skill authoring guide
- [Claude Code Plugins Documentation](https://code.claude.com/docs/en/plugins) -- plugin structure
- [Astro GitHub Pages Deployment](https://docs.astro.build/en/guides/deploy/github/) -- deployment workflow
- `src/layouts/Base.astro` -- existing layout and meta tag implementation
- `src/styles/global.css` -- existing design token system
- `src/components/Nav.astro` -- existing component patterns and a11y practices
- `src/components/ProjectCard.astro` -- existing typed component with scoped styles
- `src/content/config.ts` -- empty Content Collections config (indicates planned expansion)
- `src/data/projects.ts` -- existing typed data pattern

## Recommendations

1. **Start building the `web-dev` skill immediately** with scaffolding (Feature 1) and content system (Feature 2) as the core workflows. These two capabilities unlock the most new functionality for the site.

2. **Embed the project's design conventions directly in the skill** -- design tokens, BEM-like class naming, TypeScript prop interfaces, scoped style patterns. This is the key differentiator over generic AI code generation.

3. **Use a single `SKILL.md` file** rather than splitting into multiple skills. The total instruction content will be under 4K tokens, well within Claude's skill loading budget. Split later if the skill grows significantly.

4. **Add SEO and design system features (Features 3-4) in the second iteration.** These are low-effort additions that improve the skill's utility without requiring major new workflows.

5. **Defer testing, deployment, and view transitions** until the site has more pages and dynamic behavior. The current project size does not justify the setup cost.

6. **Wire the skill as a shared skill in the Tab plugin** at `skills/web-dev/SKILL.md`, not as an agent-local skill. It should be available to any agent that works on web projects.
