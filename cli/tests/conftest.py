"""Suite-wide fixtures for the Tab CLI.

The single autouse fixture here neuters ``_resolve_model_or_exit`` so the
bulk of the suite — which tests dials, output formatting, error contracts,
skill dispatch, etc. — doesn't have to wire a real model resolution path
on every invocation. Production behavior (error early when no flag and no
config) is tested directly:

- :func:`tab_cli.config.load_default_model_from_config` has its own test
  module (``test_config.py``).
- :func:`tab_cli.cli._resolve_model_or_exit` is exercised in
  ``test_resolver.py``.

Anything else that wants to test model-resolution behavior in
context should re-patch the resolver inside the test itself.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _stub_model_resolver(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default model resolver to passthrough-or-stub for the whole suite.

    ``tab_cli.cli._resolve_model_or_exit(flag_value)`` is the production
    hook that fails fast when no model is configured. Suite-wide we
    replace it with a thin stub: return ``flag_value`` if the test passed
    one explicitly (so flag-routing tests still see the flag value reach
    downstream callables), otherwise return a fixed identifier
    ``anthropic:test-stub`` that downstream callables (mocked
    ``compile_tab_agent``, mocked ``run_skill``) treat as opaque.

    The stub avoids re-implementing the production resolver in tests and
    keeps the test surface focused on what each test is actually
    exercising.
    """

    def _stub(flag_value: str | None) -> str:
        if flag_value is not None and flag_value.strip():
            return flag_value
        return "anthropic:test-stub"

    monkeypatch.setattr("tab_cli.cli._resolve_model_or_exit", _stub)
