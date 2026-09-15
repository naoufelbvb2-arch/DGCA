"""
DGCA — RIC-01 / R3 Minimal
Canonical CognitiveAgent Runtime Façade (R3 §27-§30)

Authoritative Specification:
RIC-01-R3-Minimal-Canonical-User-Runtime-Formal-Architecture-Specification-v1.1-FROZEN.md
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
from .graph import CognitiveGraph
from .numbers import init_quantity_backbone
from .persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    restore_canonical_r1_checkpoint,
)

if TYPE_CHECKING:
    from .chat_runtime import CanonicalChatRuntime, R3TurnResult


class CognitiveAgent:
    """Canonical minimal user-facing Cognitive Agent for DGCA (R3 §27).

    Exposes only chat(), __call__(), from_checkpoint(), and optional last_turn.
    Persistent learning, raw graph mutators, and legacy heuristics are strictly unexposed.
    """

    def __init__(self) -> None:
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
        self._runtime_root = CanonicalR1RuntimeRoot(
            graph=graph,
            ledger=ledger,
            observation_protocol_version="R2-OBS-1.0",
            lifecycle_guard=lifecycle_guard,
        )

        # Step 8 & 9: Create CanonicalChatRuntime with non-cognitive host session nonce
        self._runtime: CanonicalChatRuntime = self._runtime_root.create_chat_runtime()

    @classmethod
    def from_checkpoint(
        cls,
        filepath: str | pathlib.Path,
    ) -> CognitiveAgent:
        """Restores a canonical R1 checkpoint into a new CognitiveAgent instance (R3 §29)."""
        runtime_root, _ = restore_canonical_r1_checkpoint(
            filepath=filepath,
            expected_observation_protocol_version="R2-OBS-1.0",
            enable_prediction=False,
        )
        agent = cls.__new__(cls)
        agent._runtime_root = runtime_root
        agent._runtime = runtime_root.create_chat_runtime()
        return agent

    @classmethod
    def _for_test(
        cls,
        *,
        session_nonce: str,
    ) -> CognitiveAgent:
        """Private deterministic test constructor allowing fixed session nonce injection."""
        graph = CognitiveGraph(enable_prediction=False)
        init_quantity_backbone(graph)
        persistent_payload = extract_canonical_persistent_payload(graph)
        state_digest = compute_checkpoint_state_digest(persistent_payload)
        epoch = create_native_r1_provenance_epoch(state_digest)
        ledger = CausalCommitLedger(epoch=epoch)
        lifecycle_guard = RuntimeLifecycleGuard()
        root = CanonicalR1RuntimeRoot(
            graph=graph,
            ledger=ledger,
            observation_protocol_version="R2-OBS-1.0",
            lifecycle_guard=lifecycle_guard,
        )
        agent = cls.__new__(cls)
        agent._runtime_root = root
        agent._runtime = root.create_chat_runtime(session_nonce=session_nonce)
        return agent

    @classmethod
    def _from_checkpoint_for_test(
        cls,
        filepath: str | pathlib.Path,
        *,
        session_nonce: str,
    ) -> CognitiveAgent:
        """Private deterministic test constructor from checkpoint allowing fixed session nonce."""
        runtime_root, _ = restore_canonical_r1_checkpoint(
            filepath=filepath,
            expected_observation_protocol_version="R2-OBS-1.0",
            enable_prediction=False,
        )
        agent = cls.__new__(cls)
        agent._runtime_root = runtime_root
        agent._runtime = runtime_root.create_chat_runtime(session_nonce=session_nonce)
        return agent

    def chat(self, text: str) -> str:
        """Process one conversational turn through canonical R2 ingress, RFC13, and RFC14."""
        return self._runtime.chat(text)

    def __call__(self, text: str) -> str:
        """Callable shorthand delegating directly to chat()."""
        return self.chat(text)

    @property
    def last_turn(self) -> R3TurnResult | None:
        """Read-only transient diagnostic summary of the last executed turn."""
        return self._runtime.last_turn

    @property
    def _chat_runtime(self) -> CanonicalChatRuntime:
        """Internal private accessor for testing and verification."""
        return self._runtime

    @property
    def _root(self) -> CanonicalR1RuntimeRoot:
        """Internal private accessor for testing and verification."""
        return self._runtime_root
