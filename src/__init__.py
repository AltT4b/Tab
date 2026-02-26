"""Tab — Claude-based agent runner."""

__version__ = "0.1.0"
__all__ = ["AgentRunner", "load_role"]

from src.loader import load_role
from src.runner import AgentRunner
