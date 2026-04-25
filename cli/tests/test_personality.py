"""Tests for `tab_cli.personality.compile_tab_agent` and `TabSettings`."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_ai import Agent

from tab_cli.personality import (
    TabSettings,
    build_system_prompt,
    compile_tab_agent,
)


# ---- TabSettings ----------------------------------------------------------


def test_tab_settings_defaults_match_tab_md_table() -> None:
    """The pydantic defaults must mirror the Settings table in tab.md.

    Humor 65, Directness 80, Warmth 70, Autonomy 50, Verbosity 35.
    """
    s = TabSettings()
    assert s.humor == 65
    assert s.directness == 80
    assert s.warmth == 70
    assert s.autonomy == 50
    assert s.verbosity == 35


def test_tab_settings_accepts_boundary_values() -> None:
    s = TabSettings(humor=0, directness=100, warmth=0, autonomy=100, verbosity=0)
    assert s.humor == 0
    assert s.directness == 100


def test_tab_settings_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        TabSettings(humor=101)
    with pytest.raises(ValidationError):
        TabSettings(directness=-1)


# ---- build_system_prompt --------------------------------------------------


def test_build_system_prompt_uses_actual_tab_md(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The compiler must read the real plugins/tab/agents/tab.md file."""
    prompt = build_system_prompt()
    # Non-empty.
    assert prompt.strip()
    # Frontmatter is stripped — no leading `---` block, no `name: Tab` line.
    assert not prompt.lstrip().startswith("---")
    assert "name: Tab" not in prompt
    # Body markers from the real file are present.
    assert "## Identity" in prompt
    assert "## Voice" in prompt
    assert "## Constraints" in prompt


def test_build_system_prompt_default_values_appear() -> None:
    """With no overrides, the preamble names the table defaults."""
    prompt = build_system_prompt()
    assert "Humor 65%" in prompt
    assert "Directness 80%" in prompt
    assert "Warmth 70%" in prompt
    assert "Autonomy 50%" in prompt
    assert "Verbosity 35%" in prompt


def test_build_system_prompt_reflects_overrides() -> None:
    """Overridden settings must appear in the preamble verbatim."""
    s = TabSettings(humor=10, directness=5, warmth=99, autonomy=88, verbosity=77)
    prompt = build_system_prompt(s)
    assert "Humor 10%" in prompt
    assert "Directness 5%" in prompt
    assert "Warmth 99%" in prompt
    assert "Autonomy 88%" in prompt
    assert "Verbosity 77%" in prompt
    # And the old defaults must not slip through.
    assert "Humor 65%" not in prompt
    assert "Directness 80%" not in prompt


def test_build_system_prompt_settings_precede_body() -> None:
    """The settings preamble appears before the markdown body."""
    prompt = build_system_prompt()
    preamble_idx = prompt.find("Humor")
    identity_idx = prompt.find("## Identity")
    assert preamble_idx >= 0
    assert identity_idx >= 0
    assert preamble_idx < identity_idx


# ---- compile_tab_agent ----------------------------------------------------


def test_compile_tab_agent_returns_pydantic_ai_agent() -> None:
    agent = compile_tab_agent()
    assert isinstance(agent, Agent)


def test_compile_tab_agent_accepts_overrides_and_model() -> None:
    s = TabSettings(humor=20, verbosity=90)
    agent = compile_tab_agent(settings=s, model=None)
    assert isinstance(agent, Agent)


def test_compile_tab_agent_embeds_system_prompt() -> None:
    """The agent's system prompt must be the same string `build_system_prompt` returns."""
    s = TabSettings(humor=12, directness=34, warmth=56, autonomy=78, verbosity=90)
    agent = compile_tab_agent(settings=s)
    expected = build_system_prompt(s)
    # pydantic-ai stores static system prompts on `_system_prompts` as a tuple.
    assert expected in agent._system_prompts


def test_real_tab_md_file_exists_at_expected_path() -> None:
    """Sanity check: the path the compiler resolves to actually exists."""
    # cli/tests/test_personality.py → parents[2] is the repo root.
    repo_root = Path(__file__).resolve().parents[2]
    tab_md = repo_root / "plugins" / "tab" / "agents" / "tab.md"
    assert tab_md.is_file()
