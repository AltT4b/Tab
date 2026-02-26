"""
Tool definitions and implementations for 4gents.

Maps tool names (as declared in role.yml tools.allow) to:
  - Anthropic tool definition dicts (for the API)
  - Python implementations (called when the model invokes a tool)
"""

from __future__ import annotations

import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Callable, Any

from src.loader import ResolvedRole

REPO_ROOT = Path(__file__).parent.parent

# ── Exceptions ────────────────────────────────────────────────────────────────

class ToolDeniedError(Exception):
    pass

class PathNotAllowedError(Exception):
    pass

class ForbiddenPatternError(Exception):
    pass

class SpawnNotAllowedError(Exception):
    pass


# ── Anthropic tool definition schemas ─────────────────────────────────────────

_TOOL_SCHEMAS: dict[str, dict] = {
    "bash": {
        "name": "bash",
        "description": (
            "Execute a bash command in a subprocess. "
            "Returns stdout, stderr, and exit code. "
            "Commands containing forbidden patterns are blocked."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30).",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
    },
    "read_file": {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                },
            },
            "required": ["path"],
        },
    },
    "write_file": {
        "name": "write_file",
        "description": (
            "Write content to a file. "
            "Creates parent directories as needed. "
            "Overwrites if the file already exists."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to write to.",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write.",
                },
            },
            "required": ["path", "content"],
        },
    },
    "web_fetch": {
        "name": "web_fetch",
        "description": (
            "Fetch the content of a URL via HTTP GET. "
            "Returns the response body as text (truncated at 200 KB)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 15).",
                    "default": 15,
                },
            },
            "required": ["url"],
        },
    },
    "exa_search": {
        "name": "exa_search",
        "description": (
            "Search the web using EXA AI's semantic search engine. "
            "Returns a ranked list of relevant URLs with titles and published dates. "
            "Use this to discover authoritative sources before fetching full content with web_fetch. "
            "Requires EXA_API_KEY to be set in the environment."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language search query (max 500 characters).",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (1–10, default 5).",
                    "default": 5,
                },
                "include_text": {
                    "type": "boolean",
                    "description": (
                        "If true, include a short text excerpt from each result page. "
                        "Default false. Set to true when you need a quick content preview "
                        "without a separate web_fetch call."
                    ),
                    "default": False,
                },
            },
            "required": ["query"],
        },
    },
    "spawn_agent": {
        "name": "spawn_agent",
        "description": (
            "Spawn a sub-agent with a specified role to complete a delegated task. "
            "The sub-agent runs independently and returns its final output. "
            "Use this to delegate research, writing, or other specialist work."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "Role name to instantiate (e.g. 'researcher', 'writer').",
                },
                "task": {
                    "type": "string",
                    "description": "Full task description for the sub-agent. Be specific.",
                },
                "vars": {
                    "type": "object",
                    "description": (
                        "Optional extra template vars injected into the sub-agent's "
                        "system prompt (e.g. domain, tone, audience)."
                    ),
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["role", "task"],
        },
    },
}


# ── ToolExecutor ──────────────────────────────────────────────────────────────

class ToolExecutor:
    """
    Builds tool definitions and dispatches tool calls for a resolved role.

    spawn_callback: called when spawn_agent is invoked.
        Signature: (role_name: str, task: str, extra_vars: dict) -> str
    """

    def __init__(
        self,
        role: ResolvedRole,
        run_id: str,
        spawn_callback: Callable[[str, str, dict], str] | None = None,
    ) -> None:
        self._role = role
        self._run_id = run_id
        self._spawn_callback = spawn_callback

    # ── Public ────────────────────────────────────────────────────────────────

    def get_tool_definitions(self) -> list[dict]:
        """
        Return Anthropic-formatted tool definitions for the effective tool set.
        Effective = (tools_allow - tools_deny).
        Orchestrator roles automatically receive spawn_agent.
        """
        effective = [
            t for t in self._role.tools_allow
            if t not in self._role.tools_deny
        ]

        is_orchestrator = (
            self._role.orchestration is not None
            and self._role.orchestration.role == "orchestrator"
        )
        if is_orchestrator and "spawn_agent" not in effective:
            effective.append("spawn_agent")

        definitions = []
        for name in effective:
            if name in _TOOL_SCHEMAS:
                definitions.append(_TOOL_SCHEMAS[name])
            # Unknown tool names are silently omitted from API definitions
            # but would fail at execute() time if the model somehow calls them.

        return definitions

    def execute(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        """
        Dispatch a tool call. Always returns a string — errors are returned as
        "ERROR: ..." strings rather than raised, so the conversation loop can
        continue and let the model handle the failure gracefully.
        """
        try:
            if tool_name in self._role.tools_deny:
                raise ToolDeniedError(
                    f"Tool '{tool_name}' is denied for role '{self._role.name}'"
                )

            dispatch = {
                "bash":        self._execute_bash,
                "read_file":   self._execute_read_file,
                "write_file":  self._execute_write_file,
                "web_fetch":   self._execute_web_fetch,
                "exa_search":  self._execute_exa_search,
                "spawn_agent": self._execute_spawn_agent,
            }

            fn = dispatch.get(tool_name)
            if fn is None:
                return f"ERROR: Unknown tool '{tool_name}'"

            return fn(**tool_input)
        except (PathNotAllowedError, ForbiddenPatternError, SpawnNotAllowedError, ToolDeniedError) as e:
            return f"ERROR: {e}"
        except Exception as e:
            return f"ERROR: Unexpected error in tool '{tool_name}': {e}"

    # ── Path / pattern guards ─────────────────────────────────────────────────

    def _resolve_path(self, path: str) -> Path:
        """Resolve a path to absolute. Relative paths are anchored to REPO_ROOT,
        not the process CWD, so behaviour is consistent regardless of where the
        CLI is invoked from."""
        p = Path(path)
        if p.is_absolute():
            return p.resolve()
        return (REPO_ROOT / p).resolve()

    def _check_path_allowed(self, path: str) -> None:
        abs_path = self._resolve_path(path)
        for pattern in self._role.autonomy.allowed_paths:
            if pattern.endswith("/**"):
                prefix = (REPO_ROOT / pattern[:-3]).resolve()
                if str(abs_path).startswith(str(prefix)):
                    return
            else:
                abs_pattern = (REPO_ROOT / pattern).resolve()
                if abs_path.match(str(abs_pattern)):
                    return
        raise PathNotAllowedError(
            f"Path '{path}' is outside allowed_paths: {self._role.autonomy.allowed_paths}"
        )

    def _check_forbidden_patterns(self, command: str) -> None:
        for pattern in self._role.autonomy.forbidden_patterns:
            if pattern in command:
                raise ForbiddenPatternError(
                    f"Command contains forbidden pattern '{pattern}'"
                )

    # ── Tool implementations ──────────────────────────────────────────────────

    def _execute_bash(self, command: str, timeout: int = 30) -> str:
        self._check_forbidden_patterns(command)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            parts = []
            if result.stdout:
                parts.append(f"STDOUT:\n{result.stdout.rstrip()}")
            if result.stderr:
                parts.append(f"STDERR:\n{result.stderr.rstrip()}")
            parts.append(f"EXIT CODE: {result.returncode}")
            return "\n".join(parts)
        except subprocess.TimeoutExpired:
            return f"ERROR: Command timed out after {timeout}s"
        except Exception as e:
            return f"ERROR: {e}"

    def _execute_read_file(self, path: str) -> str:
        self._check_path_allowed(path)
        limit = 100 * 1024  # 100 KB
        try:
            p = self._resolve_path(path)
            if not p.exists():
                return f"ERROR: File not found: {path}"
            size = p.stat().st_size
            content = p.read_text(errors="replace")
            if size > limit:
                content = content[:limit]
                return content + f"\n\n[truncated — file is {size} bytes, showing first {limit}]"
            return content
        except PermissionError:
            return f"ERROR: Permission denied: {path}"
        except Exception as e:
            return f"ERROR: {e}"

    def _execute_write_file(self, path: str, content: str) -> str:
        self._check_path_allowed(path)
        try:
            p = self._resolve_path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return f"OK: Written {len(content)} bytes to {path}"
        except PermissionError:
            return f"ERROR: Permission denied: {path}"
        except Exception as e:
            return f"ERROR: {e}"

    def _execute_web_fetch(self, url: str, timeout: int = 15) -> str:
        limit = 200 * 1024  # 200 KB
        headers = {"User-Agent": "4gents/0.1 (claude-agent-runner)"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(limit + 1)
                text = raw.decode("utf-8", errors="replace")
                if len(raw) > limit:
                    text = text[:limit]
                    return text + f"\n\n[truncated at {limit // 1024} KB]"
                return text
        except urllib.error.HTTPError as e:
            return f"ERROR: HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return f"ERROR: URL error: {e.reason}"
        except TimeoutError:
            return f"ERROR: Request timed out after {timeout}s"
        except Exception as e:
            return f"ERROR: {e}"

    def _execute_exa_search(
        self,
        query: str,
        num_results: int = 5,
        include_text: bool = False,
    ) -> str:
        # ── Security: API key comes from env only, never from model input ──────
        api_key = os.getenv("EXA_API_KEY", "").strip()
        if not api_key:
            return "ERROR: EXA_API_KEY is not set. Add it to your .env file."

        # ── Input validation ───────────────────────────────────────────────────
        query = query.strip()
        if not query:
            return "ERROR: query cannot be empty."
        if len(query) > 500:
            return "ERROR: query exceeds 500-character limit."
        # Clamp num_results regardless of what the model requested
        num_results = max(1, min(int(num_results), 10))

        # ── Call EXA via SDK (lazy import so missing dep gives a clear message) ─
        try:
            from exa_py import Exa  # type: ignore[import]
        except ImportError:
            return "ERROR: exa-py not installed. Run: poetry add exa-py"

        try:
            exa = Exa(api_key)
            kwargs: dict = {"num_results": num_results, "type": "auto"}
            if include_text:
                kwargs["contents"] = {"text": True}
            results = exa.search(query, **kwargs)
        except Exception as exc:
            # Never expose the raw exception (may contain API key fragments in some SDKs)
            return f"ERROR: EXA search failed: {type(exc).__name__}: {exc}"

        # ── Format results ─────────────────────────────────────────────────────
        limit = 200 * 1024  # 200 KB — consistent with web_fetch
        lines: list[str] = [f"EXA search results for: {query!r}\n"]
        for i, r in enumerate(results.results, start=1):
            block = f"{i}. {r.title or '(no title)'}\n   URL: {r.url}"
            if getattr(r, "published_date", None):
                block += f"\n   Published: {r.published_date}"
            if include_text and getattr(r, "text", None):
                snippet = (r.text or "")[:500]
                block += f"\n   Excerpt: {snippet}"
            lines.append(block)

        output = "\n\n".join(lines)
        if len(output.encode()) > limit:
            output = output[:limit] + f"\n\n[truncated at {limit // 1024} KB]"
        return output

    def _execute_spawn_agent(
        self,
        role: str,
        task: str,
        vars: dict[str, str] | None = None,
    ) -> str:
        orch = self._role.orchestration
        if orch and role not in orch.can_spawn:
            raise SpawnNotAllowedError(
                f"Role '{self._role.name}' is not permitted to spawn '{role}'. "
                f"Allowed: {orch.can_spawn}"
            )

        if self._spawn_callback is None:
            return f"ERROR: spawn_agent not available (no spawn callback configured)"

        return self._spawn_callback(role, task, vars or {})
