"""Tests for the ``tab draw-dino`` Typer subcommand.

The wiring under test is shallow: positional words concatenate into a
prompt, ``--model`` and the dial flags round-trip into ``run_skill``,
the skill's text reaches stdout, and any exception collapses to the
shared ``tab: <reason>`` / non-zero-exit contract. We stub ``run_skill``
so the test never touches a real model — the contract being pinned is
the CLI surface, not the runner internals (those have their own
``test_skills.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from tab_cli.cli import app


@dataclass
class _RunSkillRecorder:
    """Capture every ``run_skill`` call and return a fixed string."""

    response: str = "    /\\__/\\\n   ( o.o )"
    raise_on_call: BaseException | None = None
    calls: list[dict[str, Any]] = field(default_factory=list)

    def __call__(
        self, skill_name: str, user_input: str, **kwargs: Any
    ) -> str:
        self.calls.append(
            {"skill_name": skill_name, "user_input": user_input, **kwargs}
        )
        if self.raise_on_call is not None:
            raise self.raise_on_call
        return self.response


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def isolated_xdg(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> Any:
    """Empty ``XDG_CONFIG_HOME`` so config lookups don't read a real file."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    tab_dir = tmp_path / "tab"
    tab_dir.mkdir()
    return tab_dir


def test_draw_dino_prints_skill_output(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    recorder = _RunSkillRecorder(response="dino-art-here")

    with patch("tab_cli.skills.run_skill", recorder):
        result = runner.invoke(app, ["draw-dino"])

    assert result.exit_code == 0, result.stderr
    assert "dino-art-here" in result.stdout
    assert recorder.calls[0]["skill_name"] == "draw-dino"
    # No positional args -> empty user input.
    assert recorder.calls[0]["user_input"] == ""


def test_draw_dino_joins_positional_args_into_user_input(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    recorder = _RunSkillRecorder()

    with patch("tab_cli.skills.run_skill", recorder):
        result = runner.invoke(
            app, ["draw-dino", "a", "cute", "baby", "pterodactyl"]
        )

    assert result.exit_code == 0, result.stderr
    assert recorder.calls[0]["user_input"] == "a cute baby pterodactyl"


def test_draw_dino_passes_model_flag_to_run_skill(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    recorder = _RunSkillRecorder()

    with patch("tab_cli.skills.run_skill", recorder):
        result = runner.invoke(
            app,
            ["draw-dino", "--model", "anthropic:claude-sonnet-4-7", "a t-rex"],
        )

    assert result.exit_code == 0, result.stderr
    assert recorder.calls[0]["model"] == "anthropic:claude-sonnet-4-7"


def test_draw_dino_dial_flags_round_trip_to_run_skill(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    recorder = _RunSkillRecorder()

    with patch("tab_cli.skills.run_skill", recorder):
        result = runner.invoke(
            app,
            [
                "draw-dino",
                "--humor", "10",
                "--directness", "20",
                "--warmth", "30",
                "--autonomy", "40",
                "--verbosity", "50",
            ],
        )

    assert result.exit_code == 0, result.stderr
    settings = recorder.calls[0]["settings"]
    assert settings.humor == 10
    assert settings.directness == 20
    assert settings.warmth == 30
    assert settings.autonomy == 40
    assert settings.verbosity == 50


def test_draw_dino_out_of_range_dial_exits_non_zero(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    """Same readable-error contract as ``tab ask``."""

    def _boom(*_: Any, **__: Any) -> Any:
        raise AssertionError("run_skill should not run on out-of-range input")

    with patch("tab_cli.skills.run_skill", _boom):
        result = runner.invoke(app, ["draw-dino", "--humor", "150"])

    assert result.exit_code != 0
    assert "humor must be 0-100, got 150" in result.stderr


def test_draw_dino_surfaces_runtime_errors_as_readable_message(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    """Skill-runner exceptions collapse to ``tab: <reason>`` and exit non-zero."""
    recorder = _RunSkillRecorder(
        raise_on_call=RuntimeError("API key missing")
    )

    with patch("tab_cli.skills.run_skill", recorder):
        result = runner.invoke(app, ["draw-dino", "a t-rex"])

    assert result.exit_code != 0
    assert "tab:" in result.stderr
    assert "API key missing" in result.stderr
    # No half-printed ASCII art.
    assert result.stdout.strip() == ""


def test_draw_dino_help_lists_the_subcommand_and_flags(
    runner: CliRunner,
) -> None:
    top = runner.invoke(app, ["--help"])
    assert top.exit_code == 0
    assert "draw-dino" in top.stdout

    sub = runner.invoke(app, ["draw-dino", "--help"])
    assert sub.exit_code == 0
    for dial in ("--humor", "--directness", "--warmth", "--autonomy", "--verbosity"):
        assert dial in sub.stdout, f"{dial} missing from `tab draw-dino --help`"
    assert "--model" in sub.stdout


def test_draw_dino_unset_flags_fall_through_to_tab_md_defaults(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    """No flags + no config → ``TabSettings`` defaults reach the runner."""
    recorder = _RunSkillRecorder()

    with patch("tab_cli.skills.run_skill", recorder):
        result = runner.invoke(app, ["draw-dino"])

    assert result.exit_code == 0, result.stderr
    settings = recorder.calls[0]["settings"]
    assert settings.humor == 65
    assert settings.directness == 80
    assert settings.warmth == 70
    assert settings.autonomy == 50
    assert settings.verbosity == 35


def test_draw_dino_unset_flags_fall_through_to_config_file(
    runner: CliRunner, isolated_xdg: Any
) -> None:
    """flag > config file > tab.md defaults — same precedence as other commands."""
    (isolated_xdg / "config.toml").write_text("[settings]\nhumor = 42\n")

    recorder = _RunSkillRecorder()

    with patch("tab_cli.skills.run_skill", recorder):
        result = runner.invoke(app, ["draw-dino"])

    assert result.exit_code == 0, result.stderr
    settings = recorder.calls[0]["settings"]
    assert settings.humor == 42        # config-file fallthrough
    assert settings.directness == 80   # tab.md default fallthrough
