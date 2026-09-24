"""
DGCA — RIC-02 & RIC-03
Canonical Host-Side System Runtime (RIC-02 §3, §7-§10; RIC-03 §14-§16; RIC-03-C01 §2-§5)

Authoritative Specifications:
papers MD/RIC-02-Canonical-System-Runtime-and-Agent-Boundary-Architecture-v1.0-FROZEN.md
papers MD/RIC-03-Canonical-Learning-Runtime-and-Authority-Separation-v1.0-FROZEN.md
papers MD/RIC-03-C01-Authority-Surface-AUTO-Identity-and-Concurrency-Hardening-v1.0-FROZEN.md
Status: FROZEN / ADOPTED
"""
from __future__ import annotations

import enum
import pathlib
import threading
from typing import TYPE_CHECKING

from .causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    create_native_r1_provenance_epoch,
)
from .chat_runtime import CanonicalChatRuntime
from .graph import CognitiveGraph
from .learning_runtime import (
    CanonicalLearningAuthorizer,
    CanonicalLearningRuntime,
    LearningResult,
)
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


class SystemOperationState(str, enum.Enum):
    """Mutually exclusive canonical system operation states (RIC-03 §15)."""

    IDLE = "IDLE"
    CHATTING = "CHATTING"
    LEARNING = "LEARNING"
    CHECKPOINTING = "CHECKPOINTING"


class CanonicalSystemRuntime:
    """Host-side composition runtime for DGCA canonical system architecture (RIC-02 §3; RIC-03 §14).

    Owns no cognition and introduces no new cognitive state.
    Responsible for canonical fresh bootstrap, checkpoint restore, checkpoint save,
    lifecycle management, thread-safe operation serialization (RIC-03 §15, RIC-03-C01 §3), and holding
    CanonicalR1RuntimeRoot, CanonicalChatRuntime, and CanonicalLearningRuntime.
    """

    __slots__ = (
        "_chat_runtime",
        "_learning_runtime",
        "_lock",
        "_operation_state",
        "_runtime_root",
    )

    def __init__(
        self,
        *,
        runtime_root: CanonicalR1RuntimeRoot,
        chat_runtime: CanonicalChatRuntime,
        learning_runtime: CanonicalLearningRuntime | None = None,
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

        if learning_runtime is not None:
            if not isinstance(learning_runtime, CanonicalLearningRuntime):
                raise TypeError(
                    f"learning_runtime must be an instance of CanonicalLearningRuntime, got {type(learning_runtime).__name__}"
                )
            if learning_runtime._runtime_root is not runtime_root:
                raise ValueError(
                    "Runtime coherence error: learning_runtime._runtime_root is not runtime_root"
                )
        else:
            capability = object()
            authorizer = CanonicalLearningAuthorizer(
                runtime_root=runtime_root,
                capability=capability,
            )
            learning_runtime = CanonicalLearningRuntime(
                runtime_root=runtime_root,
                authorizer=authorizer,
                capability=capability,
            )

        self._runtime_root: CanonicalR1RuntimeRoot = runtime_root
        self._chat_runtime: CanonicalChatRuntime = chat_runtime
        self._learning_runtime: CanonicalLearningRuntime = learning_runtime
        self._operation_state: SystemOperationState = SystemOperationState.IDLE
        self._lock: threading.Lock = threading.Lock()

    @property
    def operation_state(self) -> SystemOperationState:
        """Current non-cognitive operation serialization state (RIC-03 §15)."""
        return self._operation_state

    @property
    def runtime_root(self) -> CanonicalR1RuntimeRoot:
        """Canonical R1 runtime root owned by this system runtime."""
        return self._runtime_root

    @property
    def chat_runtime(self) -> CanonicalChatRuntime:
        """Canonical chat runtime owned by this system runtime."""
        return self._chat_runtime

    def _acquire_operation(self, state: SystemOperationState) -> None:
        """Acquires exclusive system operation lock or fails closed (RIC-03 §15; RIC-03-C01 §3)."""
        if not self._lock.acquire(blocking=False):
            current = self._operation_state.value
            if state == SystemOperationState.CHATTING and self._operation_state == SystemOperationState.CHATTING:
                raise RuntimeError(
                    f"Cannot begin operation '{state.value}': runtime is currently in state '{current}' "
                    "(Single active turn violation: another turn is currently running)"
                )
            raise RuntimeError(
                f"Cannot begin operation '{state.value}': runtime is currently in state '{current}'"
            )
        self._operation_state = state

    def _release_operation(self) -> None:
        """Releases system operation lock, returning state to IDLE (RIC-03 §15; RIC-03-C01 §3)."""
        self._operation_state = SystemOperationState.IDLE
        if self._lock.locked():
            self._lock.release()

    @classmethod
    def fresh(
        cls,
        *,
        session_nonce: str | None = None,
    ) -> CanonicalSystemRuntime:
        """Executes fresh canonical bootstrap sequence (RIC-02 §7; RIC-03 §14; RIC-03-C01 §2).

        1. CognitiveGraph(enable_prediction=False)
        2. init_quantity_backbone(graph)
        3. extract canonical persistent payload
        4. compute canonical state digest
        5. create native R1 provenance epoch
        6. create CausalCommitLedger
        7. create RuntimeLifecycleGuard
        8. construct CanonicalR1RuntimeRoot with observation_protocol_version="R2-OBS-1.0"
        9. create CanonicalChatRuntime through root.create_chat_runtime()
        10. create fresh ephemeral learning capability, authorizer, and runtime with fresh nonce
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

        return cls(
            runtime_root=runtime_root,
            chat_runtime=chat_runtime,
        )

    @classmethod
    def from_checkpoint(
        cls,
        filepath: str | pathlib.Path,
        *,
        session_nonce: str | None = None,
    ) -> CanonicalSystemRuntime:
        """Restores a canonical R1 checkpoint into a new CanonicalSystemRuntime (RIC-02 §8; RIC-03 §16; RIC-03-C01 §2)."""
        runtime_root, _ = restore_canonical_r1_checkpoint(
            filepath=filepath,
            expected_observation_protocol_version="R2-OBS-1.0",
            enable_prediction=False,
        )
        chat_runtime = runtime_root.create_chat_runtime(session_nonce=session_nonce)

        return cls(
            runtime_root=runtime_root,
            chat_runtime=chat_runtime,
        )

    @classmethod
    def _for_test(
        cls,
        *,
        session_nonce: str,
        learning_session_nonce: str | None = None,
    ) -> CanonicalSystemRuntime:
        """Deterministic test constructor allowing fixed session nonce injection."""
        runtime = cls.fresh(session_nonce=session_nonce)
        if learning_session_nonce is not None:
            capability = object()
            authorizer = CanonicalLearningAuthorizer(
                runtime_root=runtime.runtime_root,
                capability=capability,
            )
            runtime._learning_runtime = CanonicalLearningRuntime(
                runtime_root=runtime.runtime_root,
                authorizer=authorizer,
                capability=capability,
                session_nonce=learning_session_nonce,
            )
        return runtime

    @classmethod
    def _from_checkpoint_for_test(
        cls,
        filepath: str | pathlib.Path,
        *,
        session_nonce: str,
        learning_session_nonce: str | None = None,
    ) -> CanonicalSystemRuntime:
        """Deterministic test constructor from checkpoint allowing fixed session nonce."""
        runtime = cls.from_checkpoint(filepath, session_nonce=session_nonce)
        if learning_session_nonce is not None:
            capability = object()
            authorizer = CanonicalLearningAuthorizer(
                runtime_root=runtime.runtime_root,
                capability=capability,
            )
            runtime._learning_runtime = CanonicalLearningRuntime(
                runtime_root=runtime.runtime_root,
                authorizer=authorizer,
                capability=capability,
                session_nonce=learning_session_nonce,
            )
        return runtime

    def chat(self, text: str) -> str:
        """Process one conversational turn through canonical chat runtime (RIC-02 §10).

        Delegates directly and exactly once to CanonicalChatRuntime.chat().
        Serialized under SystemOperationState.CHATTING (RIC-03 §15; RIC-03-C01 §3).
        """
        self._acquire_operation(SystemOperationState.CHATTING)
        try:
            return self._chat_runtime.chat(text)
        finally:
            self._release_operation()

    def learn(
        self,
        text: str,
        *,
        context: str | None = None,
        occurrence_key: str | None = None,
    ) -> LearningResult:
        """Executes authorized persistent learning observation (RIC-03 §14).

        Delegates directly to CanonicalLearningRuntime.learn_text().
        Serialized under SystemOperationState.LEARNING (RIC-03 §15; RIC-03-C01 §3).
        """
        self._acquire_operation(SystemOperationState.LEARNING)
        try:
            return self._learning_runtime.learn_text(
                text,
                context=context,
                occurrence_key=occurrence_key,
            )
        finally:
            self._release_operation()

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
        Serialized under SystemOperationState.CHECKPOINTING (RIC-03 §15; RIC-03-C01 §3).
        """
        self._acquire_operation(SystemOperationState.CHECKPOINTING)
        try:
            return save_canonical_r1_checkpoint(self._runtime_root, filepath)
        finally:
            self._release_operation()
