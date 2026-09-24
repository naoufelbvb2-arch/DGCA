"""
DGCA — RIC-02 / Boundary Refactor
Thin External Façade for CognitiveAgent (RIC-02 §4)

Authoritative Specification:
papers MD/RIC-02-Canonical-System-Runtime-and-Agent-Boundary-Architecture-v1.0-FROZEN.md
Status: FROZEN / ADOPTED
"""
from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from .system_runtime import CanonicalSystemRuntime

if TYPE_CHECKING:
    from .chat_runtime import R3TurnResult


class CognitiveAgent:
    """Canonical minimal user-facing Cognitive Agent façade for DGCA (RIC-02 §4).

    Exposes strictly:
    - CognitiveAgent()
    - CognitiveAgent.from_checkpoint(path)
    - agent.chat(text)
    - agent(text)
    - agent.last_turn

    All system composition, bootstrap, checkpoint mechanics, R1 root ownership,
    and chat execution are delegated exclusively to CanonicalSystemRuntime.
    Persistent learning, graph mutation, and internal host infrastructure
    are strictly unexposed.
    """

    __slots__ = ("_runtime",)

    def __init__(self) -> None:
        self._runtime: CanonicalSystemRuntime = CanonicalSystemRuntime.fresh()

    @classmethod
    def from_checkpoint(
        cls,
        filepath: str | pathlib.Path,
    ) -> CognitiveAgent:
        """Restores a canonical checkpoint into a new CognitiveAgent instance via CanonicalSystemRuntime."""
        agent = cls.__new__(cls)
        agent._runtime = CanonicalSystemRuntime.from_checkpoint(filepath)
        return agent

    def chat(self, text: str) -> str:
        """Process one conversational turn through canonical system runtime."""
        return self._runtime.chat(text)

    def __call__(self, text: str) -> str:
        """Callable shorthand delegating directly to chat()."""
        return self.chat(text)

    @property
    def last_turn(self) -> R3TurnResult | None:
        """Read-only transient diagnostic summary of the last executed turn."""
        return self._runtime.last_turn
