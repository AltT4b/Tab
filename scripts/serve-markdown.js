#!/usr/bin/env node
// Lightweight markdown preview server — no dependencies beyond Node built-ins.
// Renders .md files as styled HTML, serves everything else as static files,
// and shows a clickable file listing for directories.

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 3900;
const ROOT = path.resolve(__dirname, "..");

// ── Minimal Markdown → HTML (covers what this repo needs) ───────────────

function md(src) {
  let html = src
    // fenced code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="language-${lang}">${esc(code.trimEnd())}</code></pre>`
    )
    // inline code
    .replace(/`([^`]+)`/g, (_, c) => `<code>${esc(c)}</code>`)
    // headings
    .replace(/^######\s+(.+)$/gm, "<h6>$1</h6>")
    .replace(/^#####\s+(.+)$/gm, "<h5>$1</h5>")
    .replace(/^####\s+(.+)$/gm, "<h4>$1</h4>")
    .replace(/^###\s+(.+)$/gm, "<h3>$1</h3>")
    .replace(/^##\s+(.+)$/gm, "<h2>$1</h2>")
    .replace(/^#\s+(.+)$/gm, "<h1>$1</h1>")
    // bold / italic
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
    // horizontal rules
    .replace(/^---+$/gm, "<hr>")
    // tables (simple)
    .replace(/^(\|.+\|)\n\|[\s:|-]+\|\n((?:\|.+\|\n?)+)/gm, (_, hdr, body) => {
      const th = hdr.split("|").filter(Boolean).map(c => `<th>${c.trim()}</th>`).join("");
      const rows = body.trim().split("\n").map(r => {
        const cells = r.split("|").filter(Boolean).map(c => `<td>${c.trim()}</td>`).join("");
        return `<tr>${cells}</tr>`;
      }).join("");
      return `<table><thead><tr>${th}</tr></thead><tbody>${rows}</tbody></table>`;
    })
    // unordered lists (one level)
    .replace(/^[-*]\s+(.+)$/gm, "<li>$1</li>")
    // paragraphs: wrap loose lines
    .replace(/^(?!<[a-z])((?!<\/?(h[1-6]|pre|code|ul|ol|li|table|thead|tbody|tr|th|td|hr|blockquote)[ >/]).+)$/gm, "<p>$1</p>");

  // wrap consecutive <li> in <ul>
  html = html.replace(/((?:<li>.*<\/li>\s*)+)/g, "<ul>$1</ul>");
  return html;
}

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ── HTML shell ──────────────────────────────────────────────────────────

function page(title, body) {
  return `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<style>
  *, *::before, *::after { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
         max-width: 820px; margin: 2rem auto; padding: 0 1.5rem; line-height: 1.6;
         color: #e0e0e0; background: #161618; }
  a { color: #58a6ff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  pre { background: #1e1e22; padding: 1rem; border-radius: 6px; overflow-x: auto; }
  code { background: #2a2a2e; padding: 0.15em 0.35em; border-radius: 3px; font-size: 0.9em; }
  pre code { background: none; padding: 0; }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
  th, td { border: 1px solid #333; padding: 0.5rem 0.75rem; text-align: left; }
  th { background: #1e1e22; }
  hr { border: none; border-top: 1px solid #333; margin: 2rem 0; }
  .breadcrumb { font-size: 0.85rem; color: #888; margin-bottom: 1rem; }
  .breadcrumb a { color: #58a6ff; }
  .listing { list-style: none; padding: 0; }
  .listing li { padding: 0.35rem 0; }
  .listing li::before { content: "📄 "; }
  .listing li.dir::before { content: "📁 "; }
</style></head><body>${body}</body></html>`;
}

// ── Directory listing ───────────────────────────────────────────────────

function listing(urlPath, dirPath) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true })
    .filter(e => !e.name.startsWith("."))
    .sort((a, b) => (b.isDirectory() - a.isDirectory()) || a.name.localeCompare(b.name));

  const crumbs = breadcrumb(urlPath);
  const items = entries.map(e => {
    const href = path.posix.join(urlPath, e.name) + (e.isDirectory() ? "/" : "");
    const cls = e.isDirectory() ? ' class="dir"' : "";
    return `<li${cls}><a href="${href}">${esc(e.name)}</a></li>`;
  }).join("\n");

  return page(urlPath || "/", `${crumbs}<h1>${esc(urlPath || "/")}</h1><ul class="listing">${items}</ul>`);
}

function breadcrumb(urlPath) {
  if (!urlPath || urlPath === "/") return "";
  const parts = urlPath.replace(/^\/|\/$/g, "").split("/");
  let href = "/";
  const links = [`<a href="/">root</a>`];
  for (const p of parts) {
    href += p + "/";
    links.push(`<a href="${href}">${esc(p)}</a>`);
  }
  return `<div class="breadcrumb">${links.join(" / ")}</div>`;
}

// ── MIME types ───────────────────────────────────────────────────────────

const MIME = {
  ".html": "text/html", ".css": "text/css", ".js": "text/javascript",
  ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg",
  ".svg": "image/svg+xml", ".txt": "text/plain", ".sh": "text/plain",
};

// ── Server ──────────────────────────────────────────────────────────────

http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split("?")[0]);
  const filePath = path.join(ROOT, urlPath);

  // safety: stay inside ROOT
  if (!filePath.startsWith(ROOT)) { res.writeHead(403); res.end("Forbidden"); return; }

  try {
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // check for index.md
      const idx = path.join(filePath, "index.md");
      if (fs.existsSync(idx)) {
        const src = fs.readFileSync(idx, "utf8");
        res.writeHead(200, { "Content-Type": "text/html" });
        res.end(page(urlPath, breadcrumb(urlPath) + md(src)));
      } else {
        res.writeHead(200, { "Content-Type": "text/html" });
        res.end(listing(urlPath, filePath));
      }
      return;
    }

    if (path.extname(filePath) === ".md") {
      const src = fs.readFileSync(filePath, "utf8");
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(page(urlPath, breadcrumb(urlPath) + md(src)));
      return;
    }

    // static file
    const mime = MIME[path.extname(filePath)] || "application/octet-stream";
    res.writeHead(200, { "Content-Type": mime });
    fs.createReadStream(filePath).pipe(res);
  } catch {
    res.writeHead(404, { "Content-Type": "text/html" });
    res.end(page("404", `<h1>Not found</h1><p>${esc(urlPath)}</p><p><a href="/">← root</a></p>`));
  }
}).listen(PORT, () => {
  console.log(`Markdown preview → http://localhost:${PORT}`);
});
