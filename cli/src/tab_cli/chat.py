"""Interactive REPL loop for ``tab chat`` (and bare ``tab``).

A turn is: read a line of user input, classify it, react.

- ``/exit`` / ``/quit`` / EOF (Ctrl-D) end the session cleanly.
- A "set <setting> to NN%" / "be more <adjective>" phrase mutates the
  active :class:`TabSettings`, recompiles the agent, prints a one-line
  acknowledgement, and continues.
- Anything else goes through the grimoire registry: an above-threshold
  hit prints a one-line acknowledgement that names the matched skill
  (individual skill dispatch lives in per-skill port tickets); a miss
  is routed to the agent and the response is streamed back.

History persists across turns within the session by passing
:meth:`AgentRunResult.all_messages` (or its streamed equivalent) into
the next ``run_stream_sync`` call as ``message_history=``. Recompiling
the agent for a settings change does **not** reset history — the
conversation continues with the new system prompt in effect.

The chat module deliberately holds no provider state of its own; the
agent does. ``--model`` passes through to :func:`compile_tab_agent`,
and recompilation on a settings change re-uses whatever model name was
captured at session start.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from typing import IO, TYPE_CHECKING

from tab_cli.personality import TabSettings, compile_tab_agent

if TYPE_CHECKING:
    from pydantic_ai import Agent
    from pydantic_ai.messages import ModelMessage

    from tab_cli.registry import SkillRegistry


# v0 greeting. Short, no banner art — the REPL is a tool, not a stage.
_GREETING = "tab — say something, or /exit to leave."


# Setting-adjustment patterns. tab.md documents two flavors:
#
#   1. "set humor to 90%"          — explicit numeric value
#   2. "be more direct" / "be terse" — adjective comparatives that map
#                                       onto a dial (direct ↔ directness,
#                                       terse ↔ low verbosity, etc.)
#
# v0 implements (1) only. The adjective→dial mapping is bigger than it
# looks — "terse" inverts onto verbosity, "blunt" maps to directness
# but not to humor, "warm" is itself the dial name — and the deferred
# settings-UX ticket (01KQ2YXEDHVD2YG1DPD9HEVR2S) is where that mapping
# gets defended. Catching adjective phrases here without that mapping
# would either over-route innocuous chat ("I want to be more careful")
# or quietly miss the half the user expects to work.
_SETTING_NAMES = ("humor", "directness", "warmth", "autonomy", "verbosity")

_NUMERIC_PATTERN = re.compile(
    rf"\bset\s+(?P<name>{'|'.join(_SETTING_NAMES)})\s+to\s+(?P<value>\d{{1,3}})%?\b",
    re.IGNORECASE,
)


@dataclass
class _Session:
    """Mutable per-session state for the REPL.

    Held as a dataclass rather than passed around as scalars so the
    settings-adjustment path has a single object to mutate — recompiling
    the agent in three different places would drift.
    """

    agent: Agent
    settings: TabSettings
    model: str | None
    registry: SkillRegistry | None
    history: list[ModelMessage] = field(default_factory=list)


def _detect_setting_change(text: str, current: TabSettings) -> TabSettings | None:
    """Return updated :class:`TabSettings` if ``text`` is a settings nudge.

    Matches "set <name> to <int>%?" against the five known dials. Out-of-range
    values (e.g. "set humor to 250") clamp to [0, 100] rather than reject —
    the user's intent is unambiguous and refusing the nudge would be pedantic
    for an interactive prompt.

    Returns ``None`` for everything else, including comparative phrases like
    "be more direct" — those need an adjective→dial mapping owned by the
    deferred settings-UX ticket. Until that lands, the agent fields them as
    free-form chat (which mostly does the right thing — the model knows
    what "be more direct" means; it just can't move the dial itself).
    """
    numeric = _NUMERIC_PATTERN.search(text)
    if numeric is None:
        return None

    name = numeric.group("name").lower()
    value = max(0, min(100, int(numeric.group("value"))))
    return current.model_copy(update={name: value})


def _read_input(stdin: IO[str], stdout: IO[str]) -> str | None:
    """Print the prompt and read one line, or return ``None`` on EOF.

    EOF (Ctrl-D on a terminal, end-of-stream in piped input) is the
    canonical "I'm done" signal for a Unix REPL — we collapse it to
    ``None`` so the caller's loop has a single sentinel to check
    alongside the textual ``/exit`` and ``/quit`` commands.
    """
    stdout.write("> ")
    stdout.flush()
    line = stdin.readline()
    if line == "":  # EOF — readline returns "" only at end-of-stream
        return None
    return line.rstrip("\n")


def _stream_agent_turn(session: _Session, prompt: str, stdout: IO[str]) -> None:
    """Run one agent turn with streaming and persist messages to history.

    We use ``run_stream_sync`` + ``stream_text(delta=True)`` so the
    response appears character-by-character as the model emits it. The
    final message list comes back via ``all_messages()`` once the
    stream is fully drained — appending those to the session's history
    preserves cross-turn context for the next call.
    """
    with session.agent.run_stream_sync(
        prompt,
        message_history=session.history,
    ) as result:
        for chunk in result.stream_text(delta=True):
            stdout.write(chunk)
            stdout.flush()
        stdout.write("\n")
        stdout.flush()
        # Replace history wholesale: ``all_messages()`` returns the
        # complete conversation including this turn's user prompt and
        # model response. Appending ``new_messages()`` to ``history``
        # would also work but ``all_messages`` is the documented "this
        # is the canonical history" accessor and matches what tests can
        # assert on.
        session.history = list(result.all_messages())


def _handle_skill_match(name: str, stdout: IO[str]) -> None:
    """Report that a skill matched without dispatching it.

    v0 boundary: per-skill dispatch logic lives in each skill's own
    port ticket (e.g. ``01KQ2YXEDEKEGSNNW424JH763B`` for draw-dino).
    The chat REPL's job here is to demonstrate the routing edge — that
    grimoire fired and the agent was bypassed — not to fake a behavior
    a port ticket will own. When a port lands, this function becomes
    a real dispatcher that hands ``name`` off to the registered skill
    runner.
    """
    stdout.write(f"[skill match: {name} — port ticket pending]\n")
    stdout.flush()


def run_chat(
    *,
    model: str | None = None,
    settings: TabSettings | None = None,
    registry: SkillRegistry | None = None,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
) -> None:
    """Run the interactive REPL until EOF / ``/exit`` / ``/quit``.

    Args:
        model: pydantic-ai model name in ``provider:name`` form, or
            ``None`` to defer to pydantic-ai's env-driven default.
        settings: Initial :class:`TabSettings`; ``None`` uses tab.md's
            defaults.
        registry: Pre-built :class:`SkillRegistry`. ``None`` triggers
            a default load from ``plugins/`` next to the package — the
            production code path. Tests inject a stub to skip the
            grimoire/Ollama runtime requirement.
        stdin / stdout: Streams to read user input from and stream
            responses to. Default to ``sys.stdin`` / ``sys.stdout`` so
            tests can substitute :class:`io.StringIO`.

    Errors loading the agent or registry surface as ``RuntimeError``-shaped
    exceptions for the Typer wrapper to collapse into a readable
    one-liner — same contract as ``tab ask``.
    """
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout

    if registry is None:
        # Lazy-imported so importing ``tab_cli.chat`` doesn't pull in
        # grimoire's Postgres/Ollama runtime requirements; tests that
        # pass an injected registry never reach this branch.
        from pathlib import Path

        from tab_cli.registry import load_skill_registry

        plugins_dir = Path(__file__).resolve().parents[3] / "plugins"
        registry = load_skill_registry(plugins_dir)

    active_settings = settings if settings is not None else TabSettings()
    agent = compile_tab_agent(settings=active_settings, model=model)
    session = _Session(
        agent=agent,
        settings=active_settings,
        model=model,
        registry=registry,
    )

    stdout.write(f"{_GREETING}\n")
    stdout.flush()

    while True:
        line = _read_input(stdin, stdout)
        if line is None:
            stdout.write("\n")  # newline after the inline prompt for tidy exit
            stdout.flush()
            return

        stripped = line.strip()
        if not stripped:
            continue

        if stripped in ("/exit", "/quit"):
            return

        # Settings nudge — handled before routing because phrases like
        # "be more direct" should never accidentally trip a skill match.
        updated = _detect_setting_change(stripped, session.settings)
        if updated is not None:
            session.settings = updated
            session.agent = compile_tab_agent(
                settings=session.settings, model=session.model
            )
            stdout.write(
                f"[settings: humor {session.settings.humor}%, "
                f"directness {session.settings.directness}%, "
                f"warmth {session.settings.warmth}%, "
                f"autonomy {session.settings.autonomy}%, "
                f"verbosity {session.settings.verbosity}%]\n"
            )
            stdout.flush()
            continue

        # Skill match check. The registry can be empty (no records seeded)
        # — in that case ``match`` returns ``None`` and we fall through.
        hit = session.registry.match(stripped) if session.registry else None
        if hit is not None and hit.passed:
            _handle_skill_match(hit.name, stdout)
            continue

        # Default: route to the agent and stream the response back.
        _stream_agent_turn(session, stripped, stdout)
