"""
DGCA — RIC-02
Canonical Host-Side System Runtime (RIC-02 §3, §7-§10)

Authoritative Specification:
papers MD/RIC-02-Canonical-System-Runtime-and-Agent-Boundary-Architecture-v1.0-FROZEN.md
Status: FROZEN / ADOPTED
"""
from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from .causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    create_native_r1_provenance_epoch,
)
from .chat_runtime import CanonicalChatRuntime
from .graph import CognitiveGraph
from .numbers import init_quantity_backbone
from .persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    restore_canonical_r1_checkpoint,
    save_canonical_r1_checkpoint,
)

if TYPE_CHECKING:
    from .chat_runtime import R3TurnResult


class CanonicalSystemRuntime:
    """Host-side composition runtime for DGCA canonical system architecture (RIC-02 §3).

    Owns no cognition and introduces no new cognitive state.
    Responsible for canonical fresh bootstrap, checkpoint restore, checkpoint save,
    lifecycle management, and holding CanonicalR1RuntimeRoot and CanonicalChatRuntime.
    """

    __slots__ = ("_chat_runtime", "_runtime_root")

    def __init__(
        self,
        *,
        runtime_root: CanonicalR1RuntimeRoot,
        chat_runtime: CanonicalChatRuntime,
    ) -> None:
        if not isinstance(runtime_root, CanonicalR1RuntimeRoot):
            raise TypeError(
                f"runtime_root must be an instance of CanonicalR1RuntimeRoot, got {type(runtime_root).__name__}"
            )
        if not isinstance(chat_runtime, CanonicalChatRuntime):
            raise TypeError(
                f"chat_runtime must be an instance of CanonicalChatRuntime, got {type(chat_runtime).__name__}"
            )
        if chat_runtime._runtime_root is not runtime_root:
            raise ValueError(
                "Runtime coherence error: chat_runtime._runtime_root is not runtime_root"
            )
        if chat_runtime._graph is not runtime_root._graph:
            raise ValueError(
                "Runtime coherence error: chat_runtime._graph is not runtime_root._graph"
            )
        self._runtime_root: CanonicalR1RuntimeRoot = runtime_root
        self._chat_runtime: CanonicalChatRuntime = chat_runtime

    @classmethod
    def fresh(
        cls,
        *,
        session_nonce: str | None = None,
    ) -> CanonicalSystemRuntime:
        """Executes fresh canonical bootstrap sequence (RIC-02 §7).

        1. CognitiveGraph(enable_prediction=False)
        2. init_quantity_backbone(graph)
        3. extract canonical persistent payload
        4. compute canonical state digest
        5. create native R1 provenance epoch
        6. create CausalCommitLedger
        7. create RuntimeLifecycleGuard
        8. construct CanonicalR1RuntimeRoot with observation_protocol_version="R2-OBS-1.0"
        9. create CanonicalChatRuntime through root.create_chat_runtime()
        """
        # Step 1: Initialize CognitiveGraph with prediction disabled (R3-I33)
        graph = CognitiveGraph(enable_prediction=False)

        # Step 2: Mandatory Quantity Backbone initialization before R1 provenance epoch
        init_quantity_backbone(graph)

        # Step 3 & 4: Extract canonical persistent payload and compute canonical state digest
        persistent_payload = extract_canonical_persistent_payload(graph)
        state_digest = compute_checkpoint_state_digest(persistent_payload)

        # Step 5: Create native R1 provenance epoch
        epoch = create_native_r1_provenance_epoch(state_digest)

        # Step 6: Create CausalCommitLedger bound to epoch
        ledger = CausalCommitLedger(epoch=epoch)

        # Step 7: Create CanonicalR1RuntimeRoot
        lifecycle_guard = RuntimeLifecycleGuard()
        runtime_root = CanonicalR1RuntimeRoot(
            graph=graph,
            ledger=ledger,
            observation_protocol_version="R2-OBS-1.0",
            lifecycle_guard=lifecycle_guard,
        )

        # Step 8 & 9: Create CanonicalChatRuntime through root
        chat_runtime = runtime_root.create_chat_runtime(session_nonce=session_nonce)

        return cls(runtime_root=runtime_root, chat_runtime=chat_runtime)

    @classmethod
    def from_checkpoint(
        cls,
        filepath: str | pathlib.Path,
        *,
        session_nonce: str | None = None,
    ) -> CanonicalSystemRuntime:
        """Restores a canonical R1 checkpoint into a new CanonicalSystemRuntime (RIC-02 §8)."""
        runtime_root, _ = restore_canonical_r1_checkpoint(
            filepath=filepath,
            expected_observation_protocol_version="R2-OBS-1.0",
            enable_prediction=False,
        )
        chat_runtime = runtime_root.create_chat_runtime(session_nonce=session_nonce)
        return cls(runtime_root=runtime_root, chat_runtime=chat_runtime)

    @classmethod
    def _for_test(
        cls,
        *,
        session_nonce: str,
    ) -> CanonicalSystemRuntime:
        """Deterministic test constructor allowing fixed session nonce injection."""
        return cls.fresh(session_nonce=session_nonce)

    @classmethod
    def _from_checkpoint_for_test(
        cls,
        filepath: str | pathlib.Path,
        *,
        session_nonce: str,
    ) -> CanonicalSystemRuntime:
        """Deterministic test constructor from checkpoint allowing fixed session nonce."""
        return cls.from_checkpoint(filepath, session_nonce=session_nonce)

    def chat(self, text: str) -> str:
        """Process one conversational turn through canonical chat runtime (RIC-02 §10).

        Delegates directly and exactly once to CanonicalChatRuntime.chat().
        """
        return self._chat_runtime.chat(text)

    def __call__(self, text: str) -> str:
        """Callable shorthand delegating directly to chat()."""
        return self.chat(text)

    @property
    def last_turn(self) -> R3TurnResult | None:
        """Read-only transient diagnostic summary of the last executed turn."""
        return self._chat_runtime.last_turn

    def save_checkpoint(self, filepath: str | pathlib.Path) -> str:
        """Saves canonical R1 checkpoint to target filepath (RIC-02 §9).

        Delegates directly to save_canonical_r1_checkpoint().
        """
        return save_canonical_r1_checkpoint(self._runtime_root, filepath)

    @property
    def runtime_root(self) -> CanonicalR1RuntimeRoot:
        """Canonical R1 runtime root owned by this system runtime."""
        return self._runtime_root

    @property
    def chat_runtime(self) -> CanonicalChatRuntime:
        """Canonical chat runtime owned by this system runtime."""
        return self._chat_runtime
