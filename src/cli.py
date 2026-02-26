#!/usr/bin/env python3
"""
Tab CLI.

Usage:
    tab run "Research the Claude Agent SDK and write a summary"
    tab run "Write a blog post about AI agents" --role writer
    tab run "Research X" --role researcher --run-id my-run-001
    tab run --prompt-file task.txt --role writer
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(
    name="tab",
    help="Tab — run Claude-based agents from role definitions",
    add_completion=False,
)


@app.command()
def run(
    prompt: Optional[str] = typer.Argument(None, help="The task or prompt to run"),
    role: str = typer.Option("orchestrator", help="Role name to run"),
    run_id: Optional[str] = typer.Option(None, help="Run ID for output paths (auto-generated if omitted)"),
    prompt_file: Optional[Path] = typer.Option(None, "--prompt-file", help="Path to a file containing the prompt"),
    debug: bool = typer.Option(False, help="Re-raise unexpected exceptions (shows full traceback)"),
) -> None:
    """Run a task through an agent role."""
    if prompt and prompt_file:
        typer.echo("ERROR: Provide either a prompt argument or --prompt-file, not both.", err=True)
        raise typer.Exit(1)

    if prompt_file:
        if not prompt_file.exists():
            typer.echo(f"ERROR: Prompt file not found: {prompt_file}", err=True)
            raise typer.Exit(1)
        prompt = prompt_file.read_text()

    if not prompt:
        typer.echo("ERROR: A prompt is required — pass it as an argument or via --prompt-file.", err=True)
        raise typer.Exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        typer.echo(
            "ERROR: ANTHROPIC_API_KEY environment variable is not set.\n"
            "       Export it before running: export ANTHROPIC_API_KEY=sk-ant-...",
            err=True,
        )
        raise typer.Exit(1)

    from src.loader import load_role, RoleError
    from src.runner import AgentRunner, AutonomyLimitError

    resolved_run_id = run_id or f"run-{uuid.uuid4().hex[:8]}"

    typer.echo(f"[Tab] run_id={resolved_run_id}  role={role}")
    typer.echo(f"[Tab] task: {prompt[:120]}")  # type: ignore[index]
    typer.echo("─" * 60)

    try:
        loaded_role = load_role(role, resolved_run_id)
    except RoleError as e:
        typer.echo(f"ERROR loading role '{role}': {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error loading role '{role}': {e}", err=True)
        raise typer.Exit(1)

    runner = AgentRunner(loaded_role, resolved_run_id, depth=0)

    try:
        runner.run(prompt)
    except AutonomyLimitError as e:
        typer.echo(f"\n[Tab] Run halted: {e}", err=True)
        raise typer.Exit(2)
    except KeyboardInterrupt:
        typer.echo("\n[Tab] Interrupted.", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"\n[Tab] Unexpected error: {e}", err=True)
        if debug:
            raise
        raise typer.Exit(1)

    typer.echo(f"\n[Tab] Done. run_id={resolved_run_id}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
