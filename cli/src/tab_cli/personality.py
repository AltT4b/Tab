"""Compile `plugins/tab/agents/tab.md` into a pydantic-ai `Agent`.

The `tab.md` file ships the canonical Tab personality: identity, voice,
constraints, and a Settings table (Humor, Directness, Warmth, Autonomy,
Verbosity, each 0-100). This module reads that file, strips the YAML
frontmatter, and builds an `Agent` whose system prompt is the markdown
body prefixed with a short paragraph that names the current setting
values — so the model sees the levels actually in effect, not just the
defaults baked into the table.

`TabSettings` is a pydantic model with the five 0-100 ints. Defaults
match the Settings table in `tab.md`. Overrides happen at compile time:
to change a setting mid-session, recompile the agent.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent


class TabSettings(BaseModel):
    """Personality dials for the Tab agent.

    Each field is an int in [0, 100]. Defaults mirror the Settings
    table in `plugins/tab/agents/tab.md`.
    """

    humor: int = Field(default=65, ge=0, le=100)
    directness: int = Field(default=80, ge=0, le=100)
    warmth: int = Field(default=70, ge=0, le=100)
    autonomy: int = Field(default=50, ge=0, le=100)
    verbosity: int = Field(default=35, ge=0, le=100)


def _repo_root() -> Path:
    """Return the repo root, derived from this file's location.

    Layout: `<repo>/cli/src/tab_cli/personality.py` → parents[3] is the
    repo root. The personality compiler reads `plugins/tab/agents/tab.md`
    from there.
    """
    return Path(__file__).resolve().parents[3]


def _tab_md_path() -> Path:
    return _repo_root() / "plugins" / "tab" / "agents" / "tab.md"


def _strip_frontmatter(text: str) -> str:
    """Strip a leading YAML frontmatter block (--- ... ---) if present.

    Returns the body with leading blank lines trimmed. If the file has
    no frontmatter, returns the text unchanged.
    """
    if not text.startswith("---"):
        return text

    # Find the closing `---` after the opening one.
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return text

    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r\n") == "---":
            body = "".join(lines[idx + 1 :])
            return body.lstrip("\n")

    # No closing delimiter — treat the whole file as body.
    return text


def _load_tab_md_body() -> str:
    """Read `plugins/tab/agents/tab.md` and return the body sans frontmatter."""
    return _strip_frontmatter(_tab_md_path().read_text(encoding="utf-8"))


def _settings_preamble(settings: TabSettings) -> str:
    """Build the leading paragraph that injects current setting values."""
    return (
        "Your active personality settings (each on a 0-100 scale, where the "
        "Settings table below describes what each one controls) are: "
        f"Humor {settings.humor}%, Directness {settings.directness}%, "
        f"Warmth {settings.warmth}%, Autonomy {settings.autonomy}%, "
        f"Verbosity {settings.verbosity}%. "
        "These are the levels in effect right now — they override the "
        "defaults shown in the Settings table."
    )


def build_system_prompt(settings: TabSettings | None = None) -> str:
    """Compose the full system prompt: settings preamble + tab.md body.

    Exposed for tests and for callers that want the prompt string
    without instantiating an `Agent`.
    """
    s = settings if settings is not None else TabSettings()
    return f"{_settings_preamble(s)}\n\n{_load_tab_md_body()}"


def compile_tab_agent(
    settings: TabSettings | None = None,
    model: str | None = None,
) -> Agent:
    """Compile `tab.md` and the given settings into a pydantic-ai `Agent`.

    Args:
        settings: Personality dial values. ``None`` uses defaults from
            the Settings table in `tab.md`.
        model: pydantic-ai model name (e.g. ``"anthropic:claude-sonnet-4"``).
            ``None`` defers model resolution; downstream callers wire it
            up before running the agent.

    Returns:
        A ready-to-run pydantic-ai `Agent`. Recompile to change settings.
    """
    prompt = build_system_prompt(settings)
    return Agent(
        model=model,
        system_prompt=prompt,
        defer_model_check=True,
    )
