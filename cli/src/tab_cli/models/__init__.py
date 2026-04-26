"""Custom pydantic-ai `Model` implementations for Tab.

The CLI drives only two providers in production: Anthropic (via pydantic-ai's
stock ``AnthropicModel``) and Ollama (via the ``OllamaNativeModel`` defined in
this package). Anthropic stays first-party — pydantic-ai ships it natively.
Ollama is the in-house path because pydantic-ai's stock ``OllamaModel``
extends ``OpenAIChatModel`` and routes through Ollama's ``/v1`` OpenAI-compat
endpoint, which has model-registration drift on some installs.
"""

from tab_cli.models.ollama_native import OllamaNativeModel

__all__ = ("OllamaNativeModel",)
