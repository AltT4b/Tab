"""Read personality settings and the default model from `~/.tab/config.toml`.

The flag-mergers live elsewhere; this module exposes:

- :func:`load_settings_from_config` — `[settings]` table for personality dials
- :func:`load_default_model_from_config` — `[model].default` for the default
  model identifier when no `--model` flag is passed

Both honor the same conventions: missing file is fine (returns nothing),
malformed file warns once to stderr and falls through, individual invalid
values warn and get dropped.

All Tab user state lives under ``~/.tab/``: this config plus the
grimoire-threshold overrides written by :mod:`tab_cli.grimoire_overrides`.
The XDG_CONFIG_HOME env var is intentionally not honored — Tab uses the
``~/.<app>/`` dotfile-style layout (like ``~/.gitconfig``, ``~/.npmrc``)
rather than the XDG ``$XDG_CONFIG_HOME/<app>/`` layout. One place, no
indirection.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

# Personality settings the Tab agent accepts. Keys outside this set in the
# config file are ignored silently — they may belong to a future setting
# or a typo we don't want to be noisy about.
_VALID_KEYS = ("humor", "directness", "warmth", "autonomy", "verbosity")


def _config_path() -> Path:
    """Resolve the config path: ``~/.tab/config.toml``."""
    return Path.home() / ".tab" / "config.toml"


def _warn(message: str) -> None:
    print(f"tab: {message}", file=sys.stderr)


def load_settings_from_config() -> dict[str, int]:
    """Load the `[settings]` table from the user's tab config.

    Returns a dict containing only keys that parsed and validated as
    ints in [0, 100]. Missing file → empty dict, no warning. Malformed
    TOML → empty dict with one stderr warning. Per-key validation
    failures emit one stderr warning each and drop only the offending
    key.
    """
    path = _config_path()

    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        _warn(f"could not read {path}: {exc}")
        return {}

    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        _warn(f"ignoring malformed config {path}: {exc}")
        return {}

    settings = data.get("settings")
    if not isinstance(settings, dict):
        return {}

    result: dict[str, int] = {}
    for key in _VALID_KEYS:
        if key not in settings:
            continue
        value = settings[key]
        # bool is a subclass of int — reject it explicitly so
        # `humor = true` doesn't sneak through as 1.
        if not isinstance(value, int) or isinstance(value, bool):
            _warn(
                f"ignoring invalid setting '{key}={value!r}' in {path} "
                "(must be int 0-100)"
            )
            continue
        if not 0 <= value <= 100:
            _warn(
                f"ignoring invalid setting '{key}={value}' in {path} "
                "(must be int 0-100)"
            )
            continue
        result[key] = value

    return result


def load_default_model_from_config() -> str | None:
    """Load `[model].default` from the user's tab config.

    Returns the configured model identifier (e.g. ``"anthropic:claude-sonnet-4-5"``
    or ``"ollama:gemma4:latest"``) if the file is present and the value parses
    as a non-empty string. Returns ``None`` if the file is missing, the section
    is absent, or the value is malformed (with a stderr warning in the latter
    two cases — silent only on missing file, the same convention
    :func:`load_settings_from_config` follows).

    The CLI's model-resolution layering puts ``--model`` ahead of this; an
    error fires only when neither source resolves a model.
    """
    path = _config_path()

    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        _warn(f"could not read {path}: {exc}")
        return None

    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        _warn(f"ignoring malformed config {path}: {exc}")
        return None

    model_section = data.get("model")
    if model_section is None:
        return None
    if not isinstance(model_section, dict):
        _warn(
            f"ignoring invalid [model] section in {path} "
            "(must be a TOML table)"
        )
        return None

    default = model_section.get("default")
    if default is None:
        return None
    if not isinstance(default, str) or not default.strip():
        _warn(
            f"ignoring invalid model.default={default!r} in {path} "
            "(must be a non-empty string like 'anthropic:claude-sonnet-4-5')"
        )
        return None

    return default.strip()
