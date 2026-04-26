"""A pydantic-ai ``Model`` backed by ``ollama-python``'s ``/api/chat``.

Why this exists: pydantic-ai's stock ``OllamaModel`` extends ``OpenAIChatModel``
and routes through Ollama's ``/v1`` OpenAI-compat endpoint. That layer has
known model-registration drift on some installs — local Ollama daemons can
have chat models pulled and runnable via ``ollama run`` while ``/v1/models``
and ``/v1/chat/completions`` return 404 for the same names. ``/api/chat`` is
the canonical Ollama surface and works regardless.

Rather than special-case Ollama in callers (which would mean "is this an
ollama model?" branches scattered across ``tab ask``, ``tab chat``, the four
skill ports, and ``tab mcp``), we present a normal pydantic-ai ``Model`` that
talks to Ollama natively. Callers stay uniform: every backend looks like
``Agent(model, system_prompt=...)`` and ``agent.run_sync(...)`` /
``agent.run_stream_sync(...)``.

Tools, message-history threading, and structured output ride on pydantic-ai's
abstractions — Ollama's ``/api/chat`` supports tool calls in the same shape,
so the translation layer here is mechanical rather than inventive.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, cast

from ollama import AsyncClient as _OllamaAsyncClient
from ollama import ChatResponse as _OllamaChatResponse
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelResponseStreamEvent,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models import Model, ModelRequestParameters, StreamedResponse
from pydantic_ai.profiles import ModelProfileSpec
from pydantic_ai.settings import ModelSettings
from pydantic_ai.tools import ToolDefinition


class OllamaNativeModel(Model):
    """A pydantic-ai ``Model`` that talks to Ollama via the official client.

    Construct with the bare model name (no ``ollama:`` prefix) — the prefix
    is the public model-string convention; this class works on the resolved
    name.

    >>> model = OllamaNativeModel("gemma3:latest")
    >>> agent = Agent(model, system_prompt="...")
    >>> result = agent.run_sync("hello")  # hits localhost:11434/api/chat

    The ``host`` argument lets callers point at a non-default Ollama daemon;
    when ``None`` (the default), ``ollama-python`` resolves the host from
    its environment-aware logic (``OLLAMA_HOST``, then ``localhost:11434``).
    """

    def __init__(
        self,
        model_name: str,
        *,
        host: str | None = None,
        settings: ModelSettings | None = None,
        profile: ModelProfileSpec | None = None,
    ) -> None:
        super().__init__(settings=settings, profile=profile)
        self._model_name = model_name
        self._host = host
        # ``ollama-python`` constructs an ``httpx.AsyncClient`` lazily and
        # honors ``OLLAMA_HOST`` when ``host=None``. We keep one instance
        # per model — pydantic-ai's ``Agent`` holds the model for the
        # session, so the client lifetime matches.
        self._client = _OllamaAsyncClient(host=host)

    # --- pydantic-ai Model abstract surface ---

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def system(self) -> str:
        return "ollama"

    @property
    def base_url(self) -> str | None:
        # ``host`` may be ``None`` (default to localhost). Reporting the
        # canonical default here rather than ``None`` makes diagnostics
        # ("which Ollama did this hit?") less ambiguous.
        return self._host or "http://localhost:11434"

    @property
    def provider(self) -> None:
        # We hold our own ``ollama.AsyncClient``; we don't sit on top of a
        # pydantic-ai ``Provider``. Returning ``None`` makes the base
        # class's ``__aenter__/__aexit__`` no-op cleanly.
        return None

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        ollama_messages = self._translate_messages(messages)
        ollama_tools = self._translate_tools(model_request_parameters.function_tools)

        response = await self._client.chat(
            model=self._model_name,
            messages=ollama_messages,
            tools=ollama_tools,
            stream=False,
        )
        return self._translate_response(response)

    @asynccontextmanager
    async def request_stream(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
        run_context: Any | None = None,
    ) -> AsyncIterator[StreamedResponse]:
        """Stream responses from Ollama via ``ollama-python``'s ``stream=True``.

        ``ollama-python``'s ``AsyncClient.chat(stream=True)`` returns an
        ``AsyncIterator[ChatResponse]`` — one chunk per partial message
        fragment, with the final chunk carrying ``done=True`` and usage
        metadata. We hand that iterator to :class:`_OllamaStreamedResponse`,
        which translates each chunk into pydantic-ai's
        ``ModelResponseStreamEvent`` shape via the parts manager.

        The ``run_context`` parameter mirrors pydantic-ai's signature but
        isn't used here — Ollama doesn't accept a run context, and the
        per-call overrides we'd need it for (model-settings tweaks,
        cancellation tokens) aren't wired through yet. Tracking as
        deliberate: when a caller surfaces a real need for run-context
        plumbing on the Ollama path, it lands here.
        """
        ollama_messages = self._translate_messages(messages)
        ollama_tools = self._translate_tools(model_request_parameters.function_tools)

        # ``ollama-python`` returns the iterator directly when
        # ``stream=True``; the await is for the request setup, not for
        # the full response body.
        response_iter = await self._client.chat(
            model=self._model_name,
            messages=ollama_messages,
            tools=ollama_tools,
            stream=True,
        )

        yield _OllamaStreamedResponse(
            model_request_parameters=model_request_parameters,
            _model_name=self._model_name,
            _provider_url=self.base_url,
            _response=response_iter,
        )

    # --- translation helpers (all stateless, exposed for tests) ---

    @staticmethod
    def _translate_messages(messages: list[ModelMessage]) -> list[dict[str, Any]]:
        """Convert pydantic-ai messages to Ollama's chat message shape.

        pydantic-ai uses tagged parts (``SystemPromptPart``, ``UserPromptPart``,
        ``TextPart``, ``ToolCallPart``, ``ToolReturnPart``); Ollama uses a
        flat ``{role, content}`` shape with optional ``tool_calls`` and
        ``tool_name``. We collapse multi-part responses into a single
        assistant message because that's what Ollama expects on the wire.
        """
        out: list[dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ModelRequest):
                for part in msg.parts:
                    if isinstance(part, SystemPromptPart):
                        out.append({"role": "system", "content": part.content})
                    elif isinstance(part, UserPromptPart):
                        # ``content`` is ``str | Sequence[UserContent]``;
                        # multi-modal support is out of scope for v0, so we
                        # flatten any sequence by stringifying parts. Real
                        # multi-modal handling lands when Tab grows image
                        # support.
                        if isinstance(part.content, str):
                            text = part.content
                        else:
                            text = "".join(
                                p if isinstance(p, str) else "" for p in part.content
                            )
                        out.append({"role": "user", "content": text})
                    elif isinstance(part, ToolReturnPart):
                        out.append(
                            {
                                "role": "tool",
                                "content": part.model_response_str(),
                                "tool_name": part.tool_name,
                            }
                        )
                    # Other request-side parts (e.g. RetryPromptPart) are
                    # dropped here — Ollama doesn't have a representation
                    # for retry-context, so the agent loop has to surface
                    # those issues via the user-content path. Tracking
                    # this as an explicit limitation rather than silently
                    # carrying potentially-misleading data.
            elif isinstance(msg, ModelResponse):
                # Reconstruct the assistant turn from pydantic-ai's parts.
                content_segments: list[str] = []
                tool_calls: list[dict[str, Any]] = []
                for part in msg.parts:
                    if isinstance(part, TextPart):
                        content_segments.append(part.content)
                    elif isinstance(part, ToolCallPart):
                        tool_calls.append(
                            {
                                "function": {
                                    "name": part.tool_name,
                                    "arguments": part.args_as_dict(),
                                }
                            }
                        )
                    # ThinkingPart, FilePart, etc. are dropped — Ollama
                    # doesn't roundtrip them. If a model emitted thinking
                    # in a previous turn, Ollama will regenerate its own
                    # for the next turn anyway.
                msg_dict: dict[str, Any] = {
                    "role": "assistant",
                    "content": "".join(content_segments),
                }
                if tool_calls:
                    msg_dict["tool_calls"] = tool_calls
                out.append(msg_dict)
        return out

    @staticmethod
    def _translate_tools(
        tools: list[ToolDefinition] | None,
    ) -> list[dict[str, Any]] | None:
        """Convert pydantic-ai ``ToolDefinition`` list to Ollama's tool spec.

        Ollama's tool format is the OpenAI-shaped JSON: ``{type: 'function',
        function: {name, description, parameters: <json-schema>}}``. The
        underlying parameters JSON schema comes from pydantic-ai's per-tool
        introspection and is already OpenAI-compatible.
        """
        if not tools:
            return None
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.parameters_json_schema,
                },
            }
            for tool in tools
        ]

    def _translate_response(self, response: _OllamaChatResponse) -> ModelResponse:
        """Convert an Ollama ``ChatResponse`` back into a pydantic-ai
        ``ModelResponse`` so the agent loop can consume it normally.

        Token-usage accounting is intentionally minimal here — Ollama
        returns ``prompt_eval_count`` and ``eval_count`` on the response,
        but pydantic-ai's ``RequestUsage`` shape includes more fields than
        Ollama exposes. We leave usage at the default zero values; if a
        caller starts depending on token-usage telemetry, this is the spot
        to wire it in.
        """
        parts: list[Any] = []
        msg = response.message
        if msg.content:
            parts.append(TextPart(content=msg.content))
        if msg.tool_calls:
            for call in msg.tool_calls:
                # ``call.function.arguments`` is a ``Mapping[str, Any]`` per
                # ollama-python's typed response shape; cast to plain
                # ``dict`` for pydantic-ai's stricter ``args`` typing.
                args: dict[str, Any] = (
                    dict(call.function.arguments) if call.function.arguments else {}
                )
                parts.append(
                    ToolCallPart(
                        tool_name=call.function.name,
                        args=cast(dict[str, Any], args),
                    )
                )
        return ModelResponse(
            parts=parts,
            model_name=self._model_name,
            provider_name="ollama",
        )


@dataclass
class _OllamaStreamedResponse(StreamedResponse):
    """pydantic-ai ``StreamedResponse`` adapter for ``ollama-python`` streams.

    Consumes the ``AsyncIterator[ChatResponse]`` from
    ``AsyncClient.chat(stream=True)`` and emits the pydantic-ai
    ``ModelResponseStreamEvent`` shape via the inherited parts manager.
    The parts manager handles the bookkeeping (creating new parts when
    the part-kind changes, appending deltas to the latest matching part);
    this class just translates ollama chunks into the right
    ``handle_*_delta`` calls.

    Tool-call streaming on Ollama is coarse-grained: ``/api/chat`` typically
    emits the full tool-call block as a single chunk after the text portion
    finishes, rather than streaming arguments token by token. We surface
    that as a single ``handle_tool_call_delta`` per call, with a
    ``vendor_part_id`` keyed by an internal counter so multiple tool calls
    in one response stay distinct.
    """

    _model_name: str = ""
    _provider_url: str | None = None
    _response: AsyncIterable[_OllamaChatResponse] | None = None
    _timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    async def _get_event_iterator(self) -> AsyncIterator[ModelResponseStreamEvent]:
        if self._response is None:
            return

        # Counter for tool-call vendor IDs. Ollama's tool-call shape
        # doesn't include per-call IDs, but pydantic-ai's parts manager
        # uses ``vendor_part_id`` to decide whether a delta belongs to
        # an existing part or starts a new one. A counter keeps multiple
        # tool calls in a single response distinct without inventing
        # semantics ollama doesn't have.
        tool_call_index = 0

        async for chunk in self._response:
            msg = chunk.message
            if msg.content:
                # ``vendor_part_id=None`` tells the parts manager to
                # append to the latest TextPart if there is one, or
                # start a new TextPart otherwise. That matches Ollama's
                # streaming shape — text comes as a continuous run of
                # content fragments, no interleaving with tool calls
                # mid-text.
                for event in self._parts_manager.handle_text_delta(
                    vendor_part_id=None,
                    content=msg.content,
                ):
                    yield event

            if msg.tool_calls:
                for call in msg.tool_calls:
                    # ``ollama-python`` types ``arguments`` as a
                    # ``Mapping[str, Any]``; cast to ``dict`` for
                    # pydantic-ai's stricter typing. Empty/missing
                    # arguments collapse to ``{}``.
                    args: dict[str, Any] = (
                        dict(call.function.arguments)
                        if call.function.arguments
                        else {}
                    )
                    vendor_id = f"tc_{tool_call_index}"
                    tool_call_index += 1

                    event = self._parts_manager.handle_tool_call_delta(
                        vendor_part_id=vendor_id,
                        tool_name=call.function.name,
                        args=cast(dict[str, Any], args),
                        tool_call_id=vendor_id,
                    )
                    if event is not None:
                        yield event

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def provider_url(self) -> str | None:
        return self._provider_url

    @property
    def timestamp(self) -> datetime:
        return self._timestamp
