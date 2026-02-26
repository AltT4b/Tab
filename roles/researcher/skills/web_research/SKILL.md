# Skill: Web Research

Use this skill when gathering information from the web using `web_fetch`.

## How to fetch

Call `web_fetch` with the target URL. Prefer authoritative sources (official docs, peer-reviewed papers, primary sources) over aggregator sites.

```
web_fetch(url="https://example.com/page", timeout=15)
```

- Fetch the primary source first; fall back to secondary sources only if the primary is unavailable or paywalled.
- Fetch multiple independent sources for any claim that will appear in the final report.

## Evaluating sources

Before citing a source, verify:

1. **Authority** — Is the author or organisation a recognised expert in the domain?
2. **Recency** — Is the publication date appropriate for the topic (e.g. within 12 months for fast-moving fields)?
3. **Corroboration** — Does at least one other independent source support the same claim?

Discard sources that fail two or more of these checks.

## Structuring results

Return fetched evidence as structured notes before synthesising:

```
### Source: <title> (<url>)
**Date:** <publication date or "unknown">
**Key claims:**
- …
**Reliability:** high / medium / low — <one-sentence rationale>
```

After gathering all sources, synthesise findings into the final report. Never copy-paste raw fetch output directly into the report.

## Rate limiting and errors

- If `web_fetch` returns an HTTP error (4xx / 5xx), try an alternative URL for the same source before abandoning.
- Wait at least 1 second between consecutive fetches to the same domain.
- If a URL is unreachable after two attempts, note it as "source unavailable" and continue with remaining sources.
