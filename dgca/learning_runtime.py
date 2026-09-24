"""
DGCA — RIC-03
Canonical Learning Runtime & Authority Separation (RIC-03)

Authoritative Specification:
papers MD/RIC-03-Canonical-Learning-Runtime-and-Authority-Separation-v1.0-FROZEN.md
Status: FROZEN / ADOPTED
"""
from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .causal_identity import CanonicalLineageState, CausalRuntimeHealth
from .observation import ExecutionMode

if TYPE_CHECKING:
    from .causal_identity import CanonicalR1RuntimeRoot
    from .observation import (
        CanonicalObservationBridge,
        CanonicalObservationResult,
    )

__all__ = [
    "LEARNING_BOUNDARY_NAMESPACE",
    "LEARNING_INGRESS_BOUNDARY",
    "LEARNING_SOURCE_EVENT_KEY",
    "RIC03_LEARNING_PROTOCOL_VERSION",
    "RIC03_LEARNING_SEMANTICS_DIGEST",
    "RIC03_LEARNING_SEMANTICS_REGISTRY",
    "CanonicalLearningAuthorizer",
    "CanonicalLearningRuntime",
    "LearningResult",
    "compute_ric03_learning_semantics_digest",
]

# ─────────────────────────────────────────────────────────── Protocol Constants
RIC03_LEARNING_PROTOCOL_VERSION: str = "RIC03-LEARN-1.0"
LEARNING_BOUNDARY_NAMESPACE: str = "DGCA:RIC03:LEARN:v1"
LEARNING_SOURCE_EVENT_KEY: str = "learning_observation"
LEARNING_INGRESS_BOUNDARY: str = "RIC03_LEARNING_TEXT"

# ─────────────────────────────────────────────────────────── Exact Semantics Registry
RIC03_LEARNING_SEMANTICS_REGISTRY: dict[str, Any] = {
    "authorization_default": "DENY_ALL",
    "authorization_owner": "CanonicalLearningAuthorizer",
    "auto_identity_policy": "SESSION_NONCE_PLUS_MONOTONIC_INDEX",
    "capability_lifetime": "HOST_EPHEMERAL_PER_RUNTIME_INSTANCE",
    "capability_persistence": "NEVER_SERIALIZED_OR_CHECKPOINTED",
    "chat_learning_policy": "STRICTLY_TRANSIENT_NO_LEARNING_AUTHORITY",
    "checkpoint_policy": "CANONICAL_R1_SCHEMA_1_2_0_CONSERVED",
    "external_identity_policy": "EXTERNAL_PREFIXED_STABLE_IDENTIFIER",
    "generation_policy": "ZERO_GENERATION_INGRESS_PERSISTENCE_ONLY",
    "identity_policy": "CONTENT_INDEPENDENT_OCCURRENCE_KEY",
    "learning_semantics_owner": "CognitiveGraph",
    "mutation_authority": "CanonicalR1RuntimeRoot",
    "observation_mode": "AUTHORIZED_PERSISTENT",
    "observation_owner": "CanonicalObservationBridge",
    "operation_concurrency_policy": "SYSTEM_OPERATION_MUTUAL_EXCLUSION_FAIL_CLOSED",
    "protocol_version": "RIC03-LEARN-1.0",
    "request_owner": "CanonicalLearningRuntime",
    "result_lifecycle": "IMMUTABLE_LEARNING_RESULT_OBSERVATION_CLOSED_FINALLY",
    "same_occurrence_conflict_policy": "FAIL_CLOSED_CAUSAL_VIOLATION",
    "same_occurrence_same_descriptor_policy": "PERSISTENT_REPLAY_NOOP",
    "supported_modalities": ["text"],
}


def compute_ric03_learning_semantics_digest() -> str:
    """Computes the direct SHA-256 digest of the canonical JSON representation of RIC-03 learning semantics registry."""
    payload = json.dumps(
        RIC03_LEARNING_SEMANTICS_REGISTRY,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


RIC03_LEARNING_SEMANTICS_DIGEST: str = compute_ric03_learning_semantics_digest()


# ─────────────────────────────────────────────────────────── Learning Result
@dataclass(frozen=True)
class LearningResult:
    """Immutable external representation of a persistent learning operation result (RIC-03 §12)."""

    protocol_version: str
    learning_index: int
    identity_mode: str  # "AUTO" | "EXTERNAL"
    source_occurrence_key: str
    root_external_episode_id: str
    ingress_event_id: str
    observation_transaction_id: str
    persistent_transaction_id: str | None
    status: str
    persistent_phase: str
    persistent_executed: bool
    replayed: bool
    observable_child_count: int


# ─────────────────────────────────────────────────────────── Canonical Learning Authorizer
class CanonicalLearningAuthorizer:
    """Learning authorization owner implementing PersistentObservationAuthorizer (RIC-03 §7).

    Validates capability identity, modality, operation kind, and R1 root health/lineage.
    Performs zero text or content inspection. Default is DENY ALL.
    """

    def __init__(
        self,
        *,
        runtime_root: CanonicalR1RuntimeRoot,
        capability: object,
    ) -> None:
        self._runtime_root = runtime_root
        self._capability = capability

    def verify_persistent_observation(
        self,
        *,
        capability: object,
        root_external_episode_id: str,
        ingress_event_id: str,
        modality: str,
        operation_kind: str,
    ) -> bool:
        if capability is None or capability is not self._capability:
            return False
        if modality != "text":
            return False
        if operation_kind != "R2_AUTHORIZED_PERSISTENT":
            return False
        if self._runtime_root.causal_runtime_health != CausalRuntimeHealth.HEALTHY:
            return False
        return bool(self._runtime_root.canonical_lineage_state == CanonicalLineageState.VALID)


# ─────────────────────────────────────────────────────────── Canonical Learning Runtime
class CanonicalLearningRuntime:
    """Host-side learning request owner (RIC-03 §9).

    Manages learning session nonce, monotonic learning index, occurrence key derivation,
    bridge delegation, and observation result lifecycle.
    """

    def __init__(
        self,
        *,
        runtime_root: CanonicalR1RuntimeRoot,
        authorizer: CanonicalLearningAuthorizer,
        capability: object,
        session_nonce: str | None = None,
    ) -> None:
        from .causal_identity import CanonicalR1RuntimeRoot

        if not isinstance(runtime_root, CanonicalR1RuntimeRoot):
            raise TypeError(
                f"runtime_root must be an instance of CanonicalR1RuntimeRoot, got {type(runtime_root).__name__}"
            )
        if not isinstance(authorizer, CanonicalLearningAuthorizer):
            raise TypeError(
                f"authorizer must be an instance of CanonicalLearningAuthorizer, got {type(authorizer).__name__}"
            )
        if capability is None or capability is not authorizer._capability:
            raise ValueError("capability must match authorizer._capability")
        if authorizer._runtime_root is not runtime_root:
            raise ValueError("authorizer._runtime_root must match runtime_root")

        self._runtime_root: CanonicalR1RuntimeRoot = runtime_root
        self._authorizer: CanonicalLearningAuthorizer = authorizer
        self._capability: object = capability
        self._session_nonce: str = session_nonce if session_nonce is not None else secrets.token_hex(6)
        self._learning_index: int = 0
        self._bridge: CanonicalObservationBridge = runtime_root.create_observation_bridge(
            authorizer=authorizer
        )

    @property
    def session_nonce(self) -> str:
        return self._session_nonce

    @property
    def learning_index(self) -> int:
        return self._learning_index

    @property
    def runtime_root(self) -> CanonicalR1RuntimeRoot:
        return self._runtime_root

    @property
    def authorizer(self) -> CanonicalLearningAuthorizer:
        return self._authorizer

    def learn_text(
        self,
        text: str,
        *,
        context: str | None = None,
        occurrence_key: str | None = None,
    ) -> LearningResult:
        """Executes authorized persistent text learning observation (RIC-03 §9)."""
        # Step 1: Pre-flight argument validation (no index increment on validation failure)
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, got {type(text).__name__}")
        if not text.strip():
            raise ValueError("text must not be empty or whitespace only")
        if context is not None and not isinstance(context, str):
            raise TypeError(f"context must be a string or None, got {type(context).__name__}")
        if occurrence_key is not None and (not isinstance(occurrence_key, str) or not occurrence_key.strip()):
            raise ValueError("occurrence_key must be a non-empty string if provided")

        # Step 2: Allocate monotonic index (once allocated, never reused on downstream failure)
        self._learning_index += 1
        current_index = self._learning_index

        # Step 3: Determine identity mode and occurrence key
        if occurrence_key is None:
            identity_mode = "AUTO"
            source_occurrence_key = f"auto:{self._session_nonce}:{current_index}"
        else:
            identity_mode = "EXTERNAL"
            source_occurrence_key = f"external:{occurrence_key}"

        # Step 4: Bridge ingress invocation with ExecutionMode.AUTHORIZED_PERSISTENT
        obs_result: CanonicalObservationResult | None = None
        try:
            obs_result = self._bridge.observe_text(
                boundary_namespace=LEARNING_BOUNDARY_NAMESPACE,
                source_occurrence_key=source_occurrence_key,
                source_event_key=LEARNING_SOURCE_EVENT_KEY,
                ingress_boundary=LEARNING_INGRESS_BOUNDARY,
                raw_text=text,
                context=context,
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability=self._capability,
            )
            return LearningResult(
                protocol_version=RIC03_LEARNING_PROTOCOL_VERSION,
                learning_index=current_index,
                identity_mode=identity_mode,
                source_occurrence_key=source_occurrence_key,
                root_external_episode_id=obs_result.root_external_episode_id,
                ingress_event_id=obs_result.ingress_event_id,
                observation_transaction_id=obs_result.observation_transaction_id,
                persistent_transaction_id=obs_result.persistent_transaction_id,
                status=obs_result.status,
                persistent_phase=obs_result.persistent_phase,
                persistent_executed=obs_result.persistent_executed,
                replayed=(obs_result.status == "PERSISTENT_REPLAY"),
                observable_child_count=len(obs_result.micro_episodes),
            )
        finally:
            if obs_result is not None:
                obs_result.close()
