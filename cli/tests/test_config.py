"""Tests for `tab_cli.config` loaders.

Two loaders share file location and warning conventions:
:func:`load_settings_from_config` (personality dials) and
:func:`load_default_model_from_config` (the default model identifier).
Both honor missing-file silence, malformed-file single-warning,
per-value drops with a warning.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tab_cli.config import (
    load_default_model_from_config,
    load_settings_from_config,
)


@pytest.fixture
def fake_xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Sandbox ``Path.home()`` and return the ``.tab/`` subdir.

    Name is a holdover from when the loader honored ``XDG_CONFIG_HOME``;
    Tab now uses the dotfile-style ``~/.tab/`` layout, so the fixture
    patches ``Path.home()`` to a tmp directory and returns ``<tmp>/.tab/``.
    Tests keep their existing shape:
    ``(fake_xdg / "config.toml").write_text(...)``.
    """
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    tab_dir = tmp_path / ".tab"
    tab_dir.mkdir()
    return tab_dir


def test_missing_file_returns_empty_dict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    # No .tab/config.toml created.
    result = load_settings_from_config()
    assert result == {}
    # Missing file is a silent no-op.
    captured = capsys.readouterr()
    assert captured.err == ""


def test_valid_full_config(fake_xdg: Path) -> None:
    (fake_xdg / "config.toml").write_text(
        "[settings]\n"
        "humor = 65\n"
        "directness = 80\n"
        "warmth = 70\n"
        "autonomy = 50\n"
        "verbosity = 35\n"
    )
    assert load_settings_from_config() == {
        "humor": 65,
        "directness": 80,
        "warmth": 70,
        "autonomy": 50,
        "verbosity": 35,
    }


def test_partial_config_returns_only_present_keys(fake_xdg: Path) -> None:
    (fake_xdg / "config.toml").write_text("[settings]\nhumor = 10\nwarmth = 0\n")
    assert load_settings_from_config() == {"humor": 10, "warmth": 0}


def test_boundary_values_are_accepted(fake_xdg: Path) -> None:
    (fake_xdg / "config.toml").write_text(
        "[settings]\nhumor = 0\ndirectness = 100\n"
    )
    assert load_settings_from_config() == {"humor": 0, "directness": 100}


def test_malformed_toml_warns_and_returns_empty(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fake_xdg / "config.toml").write_text("[settings\nhumor = 65\n")
    result = load_settings_from_config()
    assert result == {}
    captured = capsys.readouterr()
    assert "tab:" in captured.err
    assert "malformed" in captured.err
    assert "config.toml" in captured.err


def test_out_of_range_drops_key_and_warns(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fake_xdg / "config.toml").write_text(
        "[settings]\nhumor = 150\ndirectness = 80\n"
    )
    result = load_settings_from_config()
    assert result == {"directness": 80}
    captured = capsys.readouterr()
    assert "tab:" in captured.err
    assert "humor" in captured.err
    assert "150" in captured.err


def test_negative_value_drops_key_and_warns(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fake_xdg / "config.toml").write_text(
        "[settings]\nhumor = -1\nwarmth = 70\n"
    )
    result = load_settings_from_config()
    assert result == {"warmth": 70}
    assert "humor" in capsys.readouterr().err


def test_wrong_type_drops_key_and_warns(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fake_xdg / "config.toml").write_text(
        '[settings]\nhumor = "loud"\nverbosity = 25\n'
    )
    result = load_settings_from_config()
    assert result == {"verbosity": 25}
    captured = capsys.readouterr()
    assert "humor" in captured.err


def test_bool_is_rejected(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # bool is an int subclass in Python; make sure we don't silently
    # coerce `humor = true` to 1.
    (fake_xdg / "config.toml").write_text(
        "[settings]\nhumor = true\nautonomy = 40\n"
    )
    result = load_settings_from_config()
    assert result == {"autonomy": 40}
    assert "humor" in capsys.readouterr().err


def test_unknown_keys_are_ignored_silently(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fake_xdg / "config.toml").write_text(
        "[settings]\nhumor = 65\nmysterious = 999\n"
    )
    assert load_settings_from_config() == {"humor": 65}
    # Unknown keys don't warn — they may be from a future version.
    assert capsys.readouterr().err == ""


def test_missing_settings_table(fake_xdg: Path) -> None:
    (fake_xdg / "config.toml").write_text("[other]\nfoo = 1\n")
    assert load_settings_from_config() == {}


def test_config_path_resolves_under_home_dot_tab(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Config path is ``~/.tab/config.toml``, derived from ``Path.home()``.

    Before the move, the loader honored ``XDG_CONFIG_HOME`` and fell back
    to ``~/.config/tab/`` — there were two tests exercising both legs of
    that. Tab now uses dotfile-style ``~/.tab/`` exclusively, so this
    one test pins the canonical resolution: patch ``Path.home()``, write
    ``<home>/.tab/config.toml``, confirm the loader reads it. The
    ``XDG_CONFIG_HOME`` env var is intentionally not honored — that
    behavior is gone.
    """
    fake_home = tmp_path / "home"
    (fake_home / ".tab").mkdir(parents=True)
    (fake_home / ".tab" / "config.toml").write_text(
        "[settings]\nautonomy = 55\n"
    )
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    assert load_settings_from_config() == {"autonomy": 55}


def test_xdg_config_home_is_not_honored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``XDG_CONFIG_HOME`` must NOT redirect the lookup any more.

    Pin this so a future refactor doesn't accidentally restore XDG
    support without a deliberate decision. The user's home is the only
    thing that determines the config path now.
    """
    # Set XDG to a path that has a config.toml under tab/.
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / "tab").mkdir(parents=True)
    (elsewhere / "tab" / "config.toml").write_text(
        "[settings]\nhumor = 42\n"
    )
    monkeypatch.setenv("XDG_CONFIG_HOME", str(elsewhere))

    # Point Path.home() at a separate empty dir — the loader must read
    # from there (and find nothing) rather than honoring the XDG env
    # var.
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    assert load_settings_from_config() == {}


# --------------------------------------------------------------- model.default


def test_default_model_missing_file_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """No config file at all → ``None``, silently. No warning."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert load_default_model_from_config() is None
    assert capsys.readouterr().err == ""


def test_default_model_missing_section_returns_none(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """File exists but has no ``[model]`` section → ``None``, silently."""
    (fake_xdg / "config.toml").write_text("[settings]\nhumor = 65\n")
    assert load_default_model_from_config() is None
    assert capsys.readouterr().err == ""


def test_default_model_returns_configured_value(fake_xdg: Path) -> None:
    """Standard happy path."""
    (fake_xdg / "config.toml").write_text(
        '[model]\ndefault = "anthropic:claude-sonnet-4-5"\n'
    )
    assert load_default_model_from_config() == "anthropic:claude-sonnet-4-5"


def test_default_model_strips_whitespace(fake_xdg: Path) -> None:
    """Leading/trailing whitespace gets stripped — copy-paste from a
    setup doc shouldn't fail with a confusing 'model not found' later."""
    (fake_xdg / "config.toml").write_text(
        '[model]\ndefault = "  ollama:gemma4:latest  "\n'
    )
    assert load_default_model_from_config() == "ollama:gemma4:latest"


def test_default_model_empty_string_warns_and_returns_none(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Empty string is invalid — warn so the user knows the config
    didn't take effect, return ``None`` so the resolver falls through."""
    (fake_xdg / "config.toml").write_text('[model]\ndefault = ""\n')
    assert load_default_model_from_config() is None
    assert "ignoring invalid model.default" in capsys.readouterr().err


def test_default_model_non_string_warns_and_returns_none(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A non-string ``default`` (int, bool, etc.) is malformed — warn,
    return ``None``."""
    (fake_xdg / "config.toml").write_text("[model]\ndefault = 42\n")
    assert load_default_model_from_config() is None
    assert "ignoring invalid model.default" in capsys.readouterr().err


def test_default_model_section_must_be_table(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``model = "..."`` (not a table) is malformed at the section level.
    Warn rather than guessing the user's intent."""
    (fake_xdg / "config.toml").write_text('model = "anthropic:claude-sonnet-4-5"\n')
    assert load_default_model_from_config() is None
    assert "must be a TOML table" in capsys.readouterr().err


def test_default_model_malformed_toml_warns_once(
    fake_xdg: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Malformed TOML → one stderr warning, return ``None``."""
    (fake_xdg / "config.toml").write_text("[model\ndefault = oops\n")
    assert load_default_model_from_config() is None
    assert "ignoring malformed config" in capsys.readouterr().err


def test_default_model_path_resolves_under_home_dot_tab(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The default-model loader uses the same ``~/.tab/config.toml`` path
    as the settings loader. Pin both ends of the contract."""
    fake_home = tmp_path / "home"
    (fake_home / ".tab").mkdir(parents=True)
    (fake_home / ".tab" / "config.toml").write_text(
        '[model]\ndefault = "anthropic:claude-haiku"\n'
    )
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    assert load_default_model_from_config() == "anthropic:claude-haiku"
