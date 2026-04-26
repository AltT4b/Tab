"""Tests for ``tab_cli.cli._resolve_model_or_exit``.

The resolver is the early-validation hook every command-with-an-agent
calls before doing real work. It enforces the production contract:
``--model`` flag wins; falls through to ``[model].default`` from
``~/.config/tab/config.toml``; exits non-zero with a readable hint when
neither resolves.

The suite-wide ``conftest.py`` autouse fixture stubs this function out
for the rest of the suite. These tests reach for the real
implementation by reaching past the patch — see ``_unstub_resolver``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import typer

from tab_cli.cli import _resolve_model_or_exit


@pytest.fixture
def _unstub_resolver(monkeypatch: pytest.MonkeyPatch) -> None:
    """Restore the real ``_resolve_model_or_exit`` implementation.

    The autouse ``_stub_model_resolver`` from ``conftest.py`` replaces
    the function for every test in the suite. These resolver tests want
    to exercise the real thing, so we reimport and re-patch with the
    actual definition.
    """
    # Reload the module to recover the un-patched callable. Importing
    # ``_resolve_model_or_exit`` at the top of this file already binds
    # the real one (the conftest fixture runs *during* the test, after
    # imports), so the binding here is fine — but we also need to undo
    # the conftest patch on the module attribute so any callers via
    # ``tab_cli.cli._resolve_model_or_exit`` see the real thing too.
    monkeypatch.setattr(
        "tab_cli.cli._resolve_model_or_exit", _resolve_model_or_exit
    )


@pytest.fixture
def fake_xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Sandbox ``Path.home()`` for resolver tests; return the ``.tab/``
    subdir.

    Name is a holdover from XDG_CONFIG_HOME days; Tab now uses
    dotfile-style ``~/.tab/`` exclusively. Tests that write a config
    file keep the same shape: ``(fake_xdg / "config.toml").write_text(...)``.
    """
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    tab_dir = tmp_path / ".tab"
    tab_dir.mkdir()
    return tab_dir


def test_resolver_returns_flag_value_when_set(
    _unstub_resolver: None, fake_xdg: Path
) -> None:
    """An explicit ``--model`` flag wins over everything else.

    The fake xdg has no config file, so any fallthrough to config would
    surface as the wrong return value (``None`` would mean we read
    config; an empty string would mean validation didn't fire). The flag
    value comes back verbatim.
    """
    assert _resolve_model_or_exit("anthropic:claude-sonnet-4-5") == (
        "anthropic:claude-sonnet-4-5"
    )


def test_resolver_falls_through_to_config_default(
    _unstub_resolver: None, fake_xdg: Path
) -> None:
    """No ``--model`` flag → read ``[model].default`` from config."""
    (fake_xdg / "config.toml").write_text(
        '[model]\ndefault = "ollama:gemma4:latest"\n'
    )
    assert _resolve_model_or_exit(None) == "ollama:gemma4:latest"


def test_resolver_flag_wins_over_config(
    _unstub_resolver: None, fake_xdg: Path
) -> None:
    """When both are set, the flag wins — config is the lower layer."""
    (fake_xdg / "config.toml").write_text(
        '[model]\ndefault = "anthropic:claude-haiku"\n'
    )
    assert _resolve_model_or_exit("ollama:gemma4:latest") == (
        "ollama:gemma4:latest"
    )


def test_resolver_empty_flag_falls_through_to_config(
    _unstub_resolver: None, fake_xdg: Path
) -> None:
    """An empty/whitespace flag value is treated as 'unset'.

    Typer can deliver ``--model ""`` as an empty string. We treat that
    the same as not passing the flag — falls through to config — rather
    than letting it become an invalid model identifier downstream.
    """
    (fake_xdg / "config.toml").write_text(
        '[model]\ndefault = "anthropic:claude-sonnet-4-5"\n'
    )
    assert _resolve_model_or_exit("   ") == "anthropic:claude-sonnet-4-5"


def test_resolver_exits_when_neither_set(
    _unstub_resolver: None,
    fake_xdg: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No flag, no config → exit 1 with a readable hint on stderr."""
    with pytest.raises(typer.Exit) as exc_info:
        _resolve_model_or_exit(None)

    assert exc_info.value.exit_code == 1
    err = capsys.readouterr().err
    # The contract: error message tells the user how to fix it. Pin
    # the key phrases rather than the full string to keep this robust
    # against minor wording tweaks.
    assert "no model configured" in err
    assert "--model" in err
    assert "[model].default" in err
    assert "config.toml" in err
    # The example payload is part of the contract — users copy-paste
    # it. Pin both backend mentions.
    assert "anthropic:" in err
    assert "ollama:" in err


def test_resolver_does_not_exit_when_flag_supplied(
    _unstub_resolver: None,
    fake_xdg: Path,
) -> None:
    """A bare ``--model`` flag should resolve without consulting config
    or invoking the error path. Pin this so a future refactor doesn't
    accidentally make the flag-only path read config too (and warn on
    a missing file, e.g.)."""
    # No config.toml in fake_xdg.
    result = _resolve_model_or_exit("anthropic:claude-sonnet-4-5")
    assert result == "anthropic:claude-sonnet-4-5"


def test_resolver_silent_on_missing_config_when_flag_supplied(
    _unstub_resolver: None,
    fake_xdg: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The flag-supplied happy path must be quiet — no spurious warnings
    about missing config files when the user explicitly chose a model."""
    _ = _resolve_model_or_exit("anthropic:claude-sonnet-4-5")
    assert capsys.readouterr().err == ""
