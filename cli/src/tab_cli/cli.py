"""Typer entry point for the Tab CLI.

Subcommands and agent wiring land in their own tickets. This module
exposes a Typer ``app`` so ``tab --help`` works, plus the ``tab ask``
one-shot subcommand and the ``tab chat`` REPL. ``tab`` invoked without
a subcommand defaults to ``tab chat``.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="tab",
    help="Tab — a verb-shaped CLI agent for the Tab plugin ecosystem.",
    # Bare ``tab`` defaults to ``tab chat`` (per the CLI decision doc),
    # so we don't auto-render help in that case. ``tab --help`` still
    # works because Click handles ``--help`` before dispatch.
    no_args_is_help=False,
    invoke_without_command=True,
    add_completion=False,
)


@app.callback()
def _root(
    ctx: typer.Context,
    model: str | None = typer.Option(
        None,
        "--model",
        help=(
            "pydantic-ai model name in <provider:model> form "
            "(e.g. anthropic:claude-sonnet-4). Used by the default "
            "chat REPL when no subcommand is given."
        ),
        show_default=False,
    ),
) -> None:
    """Root callback. Dispatches bare ``tab`` to the chat REPL.

    The ``--model`` option lives here too so ``tab --model X`` works
    the same as ``tab chat --model X`` — the bare-``tab``-equals-chat
    shortcut needs the same flag surface as the explicit subcommand.
    """
    if ctx.invoked_subcommand is not None:
        return

    # Imported lazily so ``tab --help`` and unrelated subcommands don't
    # pay for the agent stack's import cost.
    from tab_cli.chat import run_chat

    try:
        run_chat(model=model)
    except Exception as exc:  # noqa: BLE001 — collapse to readable error
        typer.echo(f"tab: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command("ask")
def ask(
    prompt: str = typer.Argument(
        ...,
        help="The prompt to send to Tab as a single-turn question.",
        show_default=False,
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        help=(
            "pydantic-ai model name in <provider:model> form "
            "(e.g. anthropic:claude-sonnet-4)."
        ),
        show_default=False,
    ),
) -> None:
    """Send a one-shot prompt to Tab and print the response.

    No history, no REPL, no skill routing. One question, one answer.
    Errors (missing API key, network failure, model misconfiguration)
    surface a readable message on stderr and exit non-zero.
    """
    # Imported lazily so `tab --help` and unrelated subcommands don't pay
    # for pydantic-ai's import cost (and don't fail in environments where
    # the personality file isn't reachable from cwd).
    from tab_cli.personality import compile_tab_agent

    try:
        agent = compile_tab_agent(model=model)
        result = agent.run_sync(prompt)
    except Exception as exc:  # noqa: BLE001 — surface anything as a readable error
        # Typer's default behavior on uncaught exceptions is a traceback
        # dump, which is hostile in a shell-out / CI context. We collapse
        # to a one-line stderr message and a non-zero exit so callers can
        # do the usual `|| handle` shell idiom.
        typer.echo(f"tab: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    # `result.output` is the final message text for a string output type
    # — which is the default when no `output_type` is configured on the
    # agent (the personality compiler doesn't set one).
    typer.echo(result.output)


@app.command("chat")
def chat(
    model: str | None = typer.Option(
        None,
        "--model",
        help=(
            "pydantic-ai model name in <provider:model> form "
            "(e.g. anthropic:claude-sonnet-4)."
        ),
        show_default=False,
    ),
) -> None:
    """Start an interactive REPL with the Tab persona.

    Each turn: read input, route through the grimoire skill registry,
    dispatch a matched skill or stream an agent response. ``Ctrl-D``,
    ``/exit``, and ``/quit`` end the session cleanly. Personality
    settings can be adjusted mid-session (e.g. "set humor to 90%").

    Errors loading the agent or registry collapse to a readable stderr
    line plus exit code 1, matching ``tab ask``.
    """
    from tab_cli.chat import run_chat

    try:
        run_chat(model=model)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"tab: {exc}", err=True)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
