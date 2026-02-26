"""
AgentRunner — drives a single agent's conversation loop against the Anthropic API.

Handles:
- Streaming responses with real-time stdout output
- Tool call dispatch (via ToolExecutor)
- Multi-agent orchestration via spawn_agent
- Autonomy limit enforcement (max_tool_calls, max_cost_usd, checkpoint_every)
- Output delivery to configured destinations
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import anthropic
import jinja2

from src.loader import ResolvedRole, load_role
from src.tools import ToolExecutor

REPO_ROOT = Path(__file__).parent.parent

# Approximate cost per million tokens (USD) by model ID.
# Used for max_cost_usd enforcement. Falls back to Opus rates for unknown models.
_COST_PER_MTK: dict[str, dict[str, float]] = {
    "claude-opus-4-5-20251101":   {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-5-20250929": {"input": 3.0,  "output": 15.0},
    "claude-haiku-4-5-20251001":  {"input": 0.25, "output": 1.25},
    # Current generation fallbacks
    "claude-opus-4-6":            {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-6":          {"input": 3.0,  "output": 15.0},
}
_FALLBACK_COST = {"input": 15.0, "output": 75.0}  # Opus — conservative


class AutonomyLimitError(Exception):
    pass


class AgentRunner:
    """
    Runs a single agent role against the Anthropic Messages API.

    depth: 0 = top-level (orchestrator), 1 = first spawn, 2 = max.
    """

    def __init__(
        self,
        role: ResolvedRole,
        run_id: str,
        depth: int = 0,
    ) -> None:
        self._role = role
        self._run_id = run_id
        self._depth = depth

        self._tool_call_count: int = 0
        self._total_cost_usd: float = 0.0
        self._messages: list[dict[str, Any]] = []

        self._client = anthropic.Anthropic()

        self._executor = ToolExecutor(
            role=role,
            run_id=run_id,
            spawn_callback=self._spawn_agent,
        )

    # ── Public ────────────────────────────────────────────────────────────────

    def run(self, task: str) -> str:
        """
        Run the agent on a task. Returns the final text response.
        Raises AutonomyLimitError if limits are exceeded.
        """
        self._print_header()
        self._messages = [{"role": "user", "content": task}]
        final_text = ""

        while True:
            text, tool_use_blocks, stop_reason = self._stream_turn()
            if text:
                final_text = text

            # Handle max_tokens truncation: the model's output was cut off.
            # Any tool_use blocks were discarded in _stream_turn because their
            # inputs are incomplete. Record what text was produced, then inject
            # a recovery prompt so the model can try a different approach.
            if stop_reason == "max_tokens":
                assistant_content: list[dict] = []
                if text:
                    assistant_content.append({"type": "text", "text": text})
                if assistant_content:
                    self._messages.append({"role": "assistant", "content": assistant_content})
                self._messages.append({
                    "role": "user",
                    "content": (
                        "Your response was cut off because it exceeded the max_tokens limit. "
                        "Any tool call in that response was not executed. "
                        "For large files, use the bash tool instead of write_file — "
                        "for example: python3 -c \"open('path','w').write('''content''')\" "
                        "or write the content in smaller sections."
                    ),
                })
                self._check_cost_limit()
                continue

            # Build assistant message content list
            assistant_content = []
            if text:
                assistant_content.append({"type": "text", "text": text})
            for tb in tool_use_blocks:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tb["id"],
                    "name": tb["name"],
                    "input": tb["input"],
                })
            self._messages.append({"role": "assistant", "content": assistant_content})

            if not tool_use_blocks:
                break  # Model is done

            # Execute tool calls and collect results
            tool_results = self._execute_tool_calls(tool_use_blocks)
            self._messages.append({"role": "user", "content": tool_results})

            self._check_cost_limit()

        self._write_outputs(final_text)
        self._print_footer()
        return final_text

    # ── Streaming ─────────────────────────────────────────────────────────────

    def _stream_turn(self) -> tuple[str, list[dict], str]:
        """
        Make one API call (streaming). Returns (text, tool_use_blocks, stop_reason).
        tool_use_blocks: list of {"id": ..., "name": ..., "input": ...}
        stop_reason: the API stop_reason string (e.g. "end_turn", "tool_use", "max_tokens")
        """
        tool_defs = self._executor.get_tool_definitions()

        kwargs: dict[str, Any] = dict(
            model=self._role.model.id,
            max_tokens=self._role.model.max_tokens,
            system=self._role.system_prompt,
            messages=self._messages,
        )
        # temperature is not supported on some extended thinking models;
        # only pass if explicitly set in the role
        if self._role.model.temperature is not None:
            kwargs["temperature"] = self._role.model.temperature
        if tool_defs:
            kwargs["tools"] = tool_defs

        collected_text = ""

        with self._client.messages.stream(**kwargs) as stream:
            for chunk in stream.text_stream:
                self._print_stream(chunk)
                collected_text += chunk
            final = stream.get_final_message()

        self._update_cost(final.usage)

        stop_reason = final.stop_reason or "end_turn"

        # Newline after streamed text (if any was printed)
        if collected_text and not collected_text.endswith("\n"):
            print()

        if stop_reason == "max_tokens":
            # Response was truncated. Any tool_use blocks have incomplete inputs
            # and must not be executed — doing so causes infinite retry loops.
            self._print_indent(
                "[warn] Response truncated (max_tokens limit hit). "
                "Tool calls discarded. Injecting recovery guidance."
            )
            return collected_text, [], stop_reason

        tool_use_blocks = [
            {"id": block.id, "name": block.name, "input": block.input}
            for block in final.content
            if block.type == "tool_use"
        ]

        return collected_text, tool_use_blocks, stop_reason

    # ── Tool execution ────────────────────────────────────────────────────────

    def _execute_tool_calls(self, tool_use_blocks: list[dict]) -> list[dict]:
        """Execute all tool calls and return tool_result content blocks."""
        results = []
        for tb in tool_use_blocks:
            self._check_tool_limit()
            self._tool_call_count += 1

            self._print_tool_call(tb["name"], tb["input"])

            result_text = self._executor.execute(tb["name"], tb["input"])

            results.append({
                "type": "tool_result",
                "tool_use_id": tb["id"],
                "content": result_text,
            })

            self._maybe_checkpoint()

        return results

    def _spawn_agent(self, role_name: str, task: str, extra_vars: dict) -> str:
        """Callback invoked by ToolExecutor when spawn_agent is called."""
        if self._depth >= 2:
            raise AutonomyLimitError(
                f"Maximum spawn depth (2) reached — cannot spawn '{role_name}'"
            )

        self._print_spawn(role_name, task)

        sub_role = load_role(role_name, self._run_id, extra_vars or None)
        sub_runner = AgentRunner(sub_role, self._run_id, depth=self._depth + 1)
        return sub_runner.run(task)

    # ── Autonomy ──────────────────────────────────────────────────────────────

    def _check_tool_limit(self) -> None:
        if self._tool_call_count >= self._role.autonomy.max_tool_calls:
            raise AutonomyLimitError(
                f"Tool call limit reached: "
                f"{self._tool_call_count}/{self._role.autonomy.max_tool_calls}"
            )

    def _check_cost_limit(self) -> None:
        if self._total_cost_usd > self._role.autonomy.max_cost_usd:
            raise AutonomyLimitError(
                f"Cost limit exceeded: "
                f"${self._total_cost_usd:.4f} > ${self._role.autonomy.max_cost_usd:.2f}"
            )

    def _update_cost(self, usage: Any) -> None:
        rates = _COST_PER_MTK.get(self._role.model.id, _FALLBACK_COST)
        cost = (
            usage.input_tokens * rates["input"] / 1_000_000
            + usage.output_tokens * rates["output"] / 1_000_000
        )
        self._total_cost_usd += cost

    def _maybe_checkpoint(self) -> None:
        every = self._role.autonomy.checkpoint_every
        if every and self._tool_call_count > 0 and self._tool_call_count % every == 0:
            self._print_indent(
                f"[checkpoint] {self._tool_call_count} tool calls | "
                f"${self._total_cost_usd:.4f} spent"
            )
            if sys.stdin.isatty():
                try:
                    input(self._indent("  Press Enter to continue (Ctrl+C to abort)... "))
                except (EOFError, KeyboardInterrupt):
                    raise KeyboardInterrupt
            else:
                self._print_indent("  [non-interactive — auto-continuing]")

    # ── Output writing ────────────────────────────────────────────────────────

    def _write_outputs(self, result: str) -> None:
        if not result:
            return

        for dest in self._role.output.destinations:
            if dest.get("type") == "stdout":
                continue  # already streamed

            if dest.get("type") == "file":
                path_template = dest.get("path", "")
                if not path_template:
                    continue

                # Render Jinja2 in the path template (e.g. {{ run_id }})
                env = jinja2.Environment(undefined=jinja2.Undefined)
                rendered_path = env.from_string(path_template).render(run_id=self._run_id)

                out_path = Path(rendered_path)
                if not out_path.is_absolute():
                    out_path = REPO_ROOT / out_path

                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(result)
                self._print_indent(f"[output] Written to {out_path.relative_to(REPO_ROOT)}")

        # Optional: validate structured output against schema
        if (
            self._role.output.schema_path
            and self._role.output.format in ("json", "structured")
        ):
            self._validate_output_schema(result)

    def _validate_output_schema(self, result: str) -> None:
        import jsonschema
        try:
            data = json.loads(result)
            schema = json.loads(self._role.output.schema_path.read_text())
            jsonschema.validate(data, schema)
            self._print_indent("[output] Schema validation passed")
        except json.JSONDecodeError:
            self._print_indent("[output] WARNING: Output is not valid JSON — skipping schema validation")
        except jsonschema.ValidationError as e:
            self._print_indent(f"[output] WARNING: Schema validation failed: {e.message}")

    # ── Print helpers ─────────────────────────────────────────────────────────

    def _indent(self, s: str = "") -> str:
        return "  " * self._depth + s

    def _print_indent(self, msg: str) -> None:
        print(self._indent(msg))

    def _print_stream(self, text: str) -> None:
        """Print streaming text with depth-based indentation on newlines."""
        if self._depth == 0:
            print(text, end="", flush=True)
        else:
            indent = "  " * self._depth
            # Replace newlines to apply indent to continuation lines
            indented = text.replace("\n", "\n" + indent)
            print(indented, end="", flush=True)

    def _print_tool_call(self, name: str, tool_input: dict) -> None:
        summary = str(tool_input)
        if len(summary) > 80:
            summary = summary[:77] + "..."
        print(self._indent(f"\n[tool: {name}({summary})]"))

    def _print_spawn(self, role_name: str, task: str) -> None:
        task_preview = task[:100] + ("..." if len(task) > 100 else "")
        print(self._indent(f"\n[spawning: {role_name}]"))
        print(self._indent(f"  task: {task_preview}"))
        print(self._indent(f"  {'─' * 50}"))

    def _print_header(self) -> None:
        if self._depth == 0:
            return
        role_label = f"{self._role.name} (depth {self._depth})"
        print(self._indent(f"[agent: {role_label}]"))

    def _print_footer(self) -> None:
        if self._depth > 0:
            print(self._indent(
                f"[agent: {self._role.name} done | "
                f"{self._tool_call_count} tool calls | "
                f"${self._total_cost_usd:.4f}]"
            ))
            print(self._indent(f"  {'─' * 50}"))
