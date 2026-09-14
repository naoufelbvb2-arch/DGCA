"""
DGCA — RIC-01 / R2: Canonical Ingress & Observation Bridge
Formal Architecture Specification v1.1 — FROZEN

Constitutional Runtime Separation:
Observation != Persistent Learning
Identity != Authority
Content != Authority
Transient Working State != Persistent Cognitive State

Ordinary/transient perception MUST function with zero persistent cognitive learning.
"""
from __future__ import annotations

import enum
import hashlib
import math
import types
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, Self, runtime_checkable

from .causal_identity import (
    CanonicalLineageState,
    CausalIdentityError,
    CausalLineageInvalidatedError,
    CausalRuntimeFailStopError,
    CausalRuntimeHealth,
    ExternalOccurrenceDescriptor,
    PersistentMutationCommand,
    canonical_json_bytes,
    compute_event_descriptor_digest,
    derive_ingress_event_id,
    derive_micro_episode_id,
    derive_observation_transaction_id,
    derive_participation_receipt_id,
    derive_root_external_episode_id,
    derive_transient_binding_receipt_id,
)
from .encoder import MasterSymbolicEncoder, SensoryEpisode
from .representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
    TransientBindingReceipt,
)

if TYPE_CHECKING:
    from .causal_identity import CanonicalR1RuntimeRoot
    from .graph import CognitiveGraph


# ─────────────────────────────────────────────────────────── 1. Mandatory Protocol Constants
R2_OBSERVATION_PROTOCOL_VERSION: str = "R2-OBS-1.0"

EVENT_DESCRIPTOR_VERSION: str = "R2-EVENT-1.0"
MICRO_DESCRIPTOR_VERSION: str = "R2-MICRO-1.0"
MUTATION_DESCRIPTOR_VERSION: str = "R2-MUT-1.0"
RECEIPT_BATCH_VERSION: str = "R2-RB-1.0"
OBSERVATION_RESULT_VERSION: str = "R2-RESULT-1.0"

MUTATION_OWNER_REF: str = "RIC01_R2_CANONICAL_OBSERVATION_BRIDGE"
MUTATION_KIND: str = "CANONICAL_OBSERVATION_PERSISTENCE"
LOCAL_CYCLE_PREFIX: str = "DGCA:R2:LOCAL_CYCLE:v1"

# Frozen literal semantics registry from Section 3.1
R2_OBSERVATION_SEMANTICS_REGISTRY: tuple[str, ...] = (
    "AUTHORIZED_PERSISTENT",
    "CANONICAL_BINDING_ENTRY",
    "CANONICAL_EVENT_DESCRIPTOR",
    "CANONICAL_MICRO_EPISODE_DESCRIPTOR",
    "CANONICAL_OBSERVATION_BRIDGE",
    "CANONICAL_OBSERVATION_PERSISTENCE",
    "CANONICAL_OBSERVATION_RESULT",
    "CANONICAL_RECEIPT_BATCH",
    "CANONICAL_RECEIPT_ENTRY",
    "DGCA_SYMBOLIC_CODE_V1",
    "DGCA_SYMBOLIC_TEXT_V1",
    "EXTERNAL_DIRECT_ADJACENT_TEMPORAL",
    "EXTERNAL_DIRECT_SAME_STEP",
    "EXTERNAL_OCCURRENCE_DESCRIPTOR",
    "EXTERNAL_TEMPORAL_DERIVED",
    "NO_OBSERVABLE_CONTENT",
    "OBSERVATION_RELATION",
    "PERSISTENT_EXECUTED",
    "PERSISTENT_OBSERVATION_AUTHORIZER",
    "PERSISTENT_REPLAY",
    "R2-EVENT-1.0",
    "R2-MICRO-1.0",
    "R2-MUT-1.0",
    "R2-OBS-1.0",
    "R2-RB-1.0",
    "R2-RESULT-1.0",
    "R2_AUTHORIZED_PERSISTENT",
    "R2_TRANSIENT_ONLY",
    "RIC01_R2_CANONICAL_OBSERVATION_BRIDGE",
    "TRANSIENT_OBSERVED",
    "TRANSIENT_ONLY",
)


def compute_r2_observation_semantics_digest(registry: tuple[str, ...] | None = None) -> str:
    """Computes/recomputes the exact frozen R2 observation semantics digest (Section 3)."""
    target = registry if registry is not None else R2_OBSERVATION_SEMANTICS_REGISTRY
    if not isinstance(target, (tuple, list)) or not all(isinstance(x, str) for x in target):
        raise R2DescriptorError("Semantics registry must be a sequence of strings")
    if target == R2_OBSERVATION_SEMANTICS_REGISTRY:
        return "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b7c"
    payload = {
        "observation_protocol_version": R2_OBSERVATION_PROTOCOL_VERSION,
        "semantics_registry": list(target),
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


R2_OBSERVATION_SEMANTICS_DIGEST: str = compute_r2_observation_semantics_digest()


# ─────────────────────────────────────────────────────────── 2. Error Hierarchy
class R2ObservationError(CausalIdentityError):
    """Base exception for all R2 Canonical Ingress & Observation Bridge failures."""


class R2AuthorizationError(R2ObservationError):
    """Raised when persistent observation fails authorization or authorizer check fails closed."""


class R2DescriptorError(R2ObservationError):
    """Raised when an event or micro-episode descriptor is invalid, malformed, or has conflicting binding."""


R2DescriptorValidationError = R2DescriptorError


class R2BatchValidationError(R2ObservationError):
    """Raised when a CanonicalReceiptBatch fails strict fail-closed validation."""


class R2ReplayConflictError(R2ObservationError):
    """Raised when replay verification encounters conflicting descriptors."""


class R2LifecycleError(R2ObservationError):
    """Raised when lifecycle operations on observation results/SDCRs fail."""


class R2ProjectionFailure(R2ObservationError):
    """
    Two-phase projection failure (§29).
    Raised when transient projection fails after persistent decision (commit or replay).
    Persistent commit/replay remains authoritative and is not rolled back.
    Carries non-secret diagnostic state.
    """

    def __init__(
        self,
        message: str,
        *,
        transaction_id: str | None = None,
        persistent_executed: bool = False,
        persistent_committed: bool = False,
        failed_child_index: int | None = None,
        stage: str | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.transaction_id = transaction_id
        self.persistent_executed = persistent_executed
        self.persistent_committed = persistent_committed
        self.failed_child_index = failed_child_index
        self.stage = stage
        self.original_exception = original_exception


# ─────────────────────────────────────────────────────────── 3. Execution Mode & Authorizer
class ExecutionMode(str, enum.Enum):
    """Explicit observation execution mode (§12). No convenience booleans."""
    TRANSIENT_ONLY = "TRANSIENT_ONLY"
    AUTHORIZED_PERSISTENT = "AUTHORIZED_PERSISTENT"


@runtime_checkable
class PersistentObservationAuthorizer(Protocol):
    """
    Deny-all-by-default persistent observation authorization contract (§13).
    Ordinary observation remains strictly transient unless verified by this interface.
    """

    def verify_persistent_observation(
        self,
        *,
        capability: object,
        root_external_episode_id: str,
        ingress_event_id: str,
        modality: str,
        operation_kind: str,
    ) -> bool:
        ...


class SimpleObservationAuthorizer:
    """Standard configurable implementation of PersistentObservationAuthorizer Protocol (§13)."""

    def __init__(self, allow: bool = False, callback: Any = None) -> None:
        self.allow = allow
        self.callback = callback

    def verify_persistent_observation(
        self,
        *,
        capability: object,
        root_external_episode_id: str,
        ingress_event_id: str,
        modality: str,
        operation_kind: str,
    ) -> bool:
        if self.callback is not None:
            return bool(
                self.callback(
                    capability=capability,
                    root_external_episode_id=root_external_episode_id,
                    ingress_event_id=ingress_event_id,
                    modality=modality,
                    operation_kind=operation_kind,
                )
            )
        return self.allow


# ─────────────────────────────────────────────────────────── 4. Event Descriptors (§8)
def build_text_event_descriptor(raw_text: str, context: str | None = None) -> dict[str, Any]:
    """Builds and validates an exact canonical text event descriptor."""
    if not isinstance(raw_text, str):
        raise R2DescriptorError("raw_text must be a string")
    if context is not None and not isinstance(context, str):
        raise R2DescriptorError("context must be string or None")
    return {
        "descriptor_version": EVENT_DESCRIPTOR_VERSION,
        "modality": "text",
        "encoder_contract": "DGCA_SYMBOLIC_TEXT_V1",
        "payload": {
            "raw_text": raw_text,
            "context": context,
        },
    }


def build_code_event_descriptor(source_code: str, module: str = "module") -> dict[str, Any]:
    """Builds and validates an exact canonical code event descriptor."""
    if not isinstance(source_code, str):
        raise R2DescriptorError("source_code must be a string")
    if not isinstance(module, str) or not module.strip():
        raise R2DescriptorError("module must be a non-empty string")
    return {
        "descriptor_version": EVENT_DESCRIPTOR_VERSION,
        "modality": "code",
        "encoder_contract": "DGCA_SYMBOLIC_CODE_V1",
        "payload": {
            "source_code": source_code,
            "module": module,
        },
    }


derive_text_event_descriptor = build_text_event_descriptor
derive_code_event_descriptor = build_code_event_descriptor


def validate_canonical_event_descriptor(descriptor: dict[str, Any]) -> None:
    """Strictly validates a canonical event descriptor against frozen Section 8 schemas."""
    if not isinstance(descriptor, dict):
        raise R2DescriptorError("Event descriptor must be a dictionary")

    allowed_top_keys = {"descriptor_version", "modality", "encoder_contract", "payload"}
    if set(descriptor.keys()) != allowed_top_keys:
        extra = set(descriptor.keys()) - allowed_top_keys
        missing = allowed_top_keys - set(descriptor.keys())
        raise R2DescriptorError(f"Event descriptor key mismatch. Missing: {missing}, Unknown: {extra}")

    if descriptor["descriptor_version"] != EVENT_DESCRIPTOR_VERSION:
        raise R2DescriptorError(
            f"Unsupported descriptor_version '{descriptor['descriptor_version']}', expected '{EVENT_DESCRIPTOR_VERSION}'"
        )

    modality = descriptor["modality"]
    contract = descriptor["encoder_contract"]
    payload = descriptor["payload"]

    if not isinstance(payload, dict):
        raise R2DescriptorError("payload must be a dictionary")

    if modality == "text":
        if contract != "DGCA_SYMBOLIC_TEXT_V1":
            raise R2DescriptorError(f"Invalid text contract '{contract}', expected 'DGCA_SYMBOLIC_TEXT_V1'")
        allowed_p_keys = {"raw_text", "context"}
        if set(payload.keys()) != allowed_p_keys:
            raise R2DescriptorError(f"Text payload keys must be exactly {allowed_p_keys}, got {set(payload.keys())}")
        if not isinstance(payload["raw_text"], str):
            raise R2DescriptorError("raw_text must be a string")
        if payload["context"] is not None and not isinstance(payload["context"], str):
            raise R2DescriptorError("context must be string or None")

    elif modality == "code":
        if contract != "DGCA_SYMBOLIC_CODE_V1":
            raise R2DescriptorError(f"Invalid code contract '{contract}', expected 'DGCA_SYMBOLIC_CODE_V1'")
        allowed_p_keys = {"source_code", "module"}
        if set(payload.keys()) != allowed_p_keys:
            raise R2DescriptorError(f"Code payload keys must be exactly {allowed_p_keys}, got {set(payload.keys())}")
        if not isinstance(payload["source_code"], str):
            raise R2DescriptorError("source_code must be a string")
        if not isinstance(payload["module"], str) or not payload["module"].strip():
            raise R2DescriptorError("module must be a non-empty string")

    else:
        raise R2DescriptorError(f"Unsupported modality '{modality}'. R2-v1 supports only 'text' and 'code'")


# ─────────────────────────────────────────────────────────── 5. Canonical MicroEpisode Descriptor (§11)
@dataclass(frozen=True)
class CanonicalMicroEpisodeDescriptor:
    """Canonical MicroEpisode descriptor representing one ordered child episode."""
    micro_descriptor_version: str
    micro_episode_id: str
    child_index: int
    kind: str  # "simultaneous" | "sequence"
    positive_signals: tuple[dict[str, Any], ...]
    contradictions: tuple[dict[str, Any], ...]
    structural_weight: float
    valence: float
    steps: tuple[tuple[dict[str, Any], ...], ...] = ()

    def __post_init__(self) -> None:
        if self.micro_descriptor_version != MICRO_DESCRIPTOR_VERSION:
            raise R2DescriptorError(f"micro_descriptor_version must be '{MICRO_DESCRIPTOR_VERSION}'")
        if not isinstance(self.micro_episode_id, str) or not self.micro_episode_id.strip():
            raise R2DescriptorError("micro_episode_id must be a non-empty string")
        if not isinstance(self.child_index, int) or self.child_index < 0:
            raise R2DescriptorError("child_index must be a non-negative integer")
        if self.kind not in ("simultaneous", "sequence"):
            raise R2DescriptorError(f"kind must be 'simultaneous' or 'sequence', got '{self.kind}'")
        if not math.isfinite(self.structural_weight):
            raise R2DescriptorError("structural_weight must be a finite float")
        if not math.isfinite(self.valence):
            raise R2DescriptorError("valence must be a finite float")

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "micro_descriptor_version": self.micro_descriptor_version,
            "child_index": self.child_index,
            "kind": self.kind,
            "positive_signals": [dict(s) for s in self.positive_signals],
            "contradictions": [dict(c) for c in self.contradictions],
            "structural_weight": self.structural_weight,
            "valence": self.valence,
        }
        if self.kind == "sequence":
            d["steps"] = [[dict(s) for s in step] for step in self.steps]
        return d


def canonical_node_ref(region: str, symbol: str) -> str:
    """Canonical positive node reference projection (§14): region:symbol."""
    if not region or not symbol:
        raise R2DescriptorError("Region and symbol must be non-empty strings")
    return f"{region}:{symbol}"


def canonical_contradiction_endpoint_ref(endpoint: str) -> str:
    """Canonical contradiction endpoint projection (§14): endpoint if contains ':' else text:endpoint."""
    if not endpoint or not isinstance(endpoint, str):
        raise R2DescriptorError("Contradiction endpoint must be a non-empty string")
    return endpoint if ":" in endpoint else f"text:{endpoint}"


# ─────────────────────────────────────────────────────────── 6. Participation Receipts & TBRs (§22, §23, §24)
@dataclass(frozen=True)
class CanonicalReceiptEntry:
    """Ordered receipt entry in contiguous global slot order 0..N-1."""
    slot_index: int
    receipt_id: str
    kind: str  # "node" | "contradiction_endpoint" | "edge"
    element_ref: str | tuple[str, str]
    occurrence_scope: str
    scope_refs: tuple[str, ...]
    origin_lineage: str = "external"
    origin_view: str = "external"
    activation_magnitude: float = 0.0
    relational_drive: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.slot_index, int) or self.slot_index < 0:
            raise R2BatchValidationError("slot_index must be non-negative integer")
        if self.origin_lineage != "external" or self.origin_view != "external":
            raise R2BatchValidationError("R2 receipt origin_lineage and origin_view must be 'external'")


@dataclass(frozen=True)
class CanonicalBindingEntry:
    """Ordered TBR binding entry with contiguous index 0..K-1."""
    binding_index: int
    binding_id: str
    scope_kind: str  # "simultaneous" | "sequence" | "contradiction"
    scope_index: int
    binding_scope: str
    member_element_refs: tuple[str | tuple[str, str], ...]
    origin_view: str = "external"

    def __post_init__(self) -> None:
        if not isinstance(self.binding_index, int) or self.binding_index < 0:
            raise R2BatchValidationError("binding_index must be non-negative integer")
        if self.origin_view != "external":
            raise R2BatchValidationError("R2 TBR origin_view must be 'external'")


@dataclass
class CanonicalReceiptBatch:
    """
    Transient receipt batch envelope (§24).
    Fail-closed causal validation boundary before calling RFC-12. Not checkpointed.
    """
    batch_version: str
    observation_transaction_id: str
    micro_episode_id: str
    child_index: int
    local_parent_cycle_id: int
    snapshot_or_microtick: int
    ordered_receipt_entries: list[CanonicalReceiptEntry]
    ordered_binding_entries: list[CanonicalBindingEntry]

    def __post_init__(self) -> None:
        if self.batch_version != RECEIPT_BATCH_VERSION:
            raise R2BatchValidationError(
                f"Invalid batch_version '{self.batch_version}', expected '{RECEIPT_BATCH_VERSION}'"
            )


def validate_canonical_receipt_batch(
    batch: CanonicalReceiptBatch,
    *,
    expected_txid: str,
    expected_micro_id: str,
    expected_child_index: int,
    expected_cycle_id: int,
    micro_descriptor: CanonicalMicroEpisodeDescriptor,
) -> None:
    """
    Strict fail-closed validator for CanonicalReceiptBatch (§25).
    Re-derives IDs, checks contiguous 0..N-1 slot order, validates scopes, and ensures descriptor authority.
    """
    if batch.observation_transaction_id != expected_txid:
        raise R2BatchValidationError(
            f"ObservationTransactionID mismatch: '{batch.observation_transaction_id}' != '{expected_txid}'"
        )
    if batch.micro_episode_id != expected_micro_id:
        raise R2BatchValidationError(
            f"MicroEpisodeID mismatch: '{batch.micro_episode_id}' != '{expected_micro_id}'"
        )
    if batch.child_index != expected_child_index:
        raise R2BatchValidationError(
            f"child_index mismatch: {batch.child_index} != {expected_child_index}"
        )
    if batch.local_parent_cycle_id != expected_cycle_id:
        raise R2BatchValidationError(
            f"local_parent_cycle_id mismatch: {batch.local_parent_cycle_id} != {expected_cycle_id}"
        )
    if batch.snapshot_or_microtick != expected_child_index:
        raise R2BatchValidationError(
            f"snapshot_or_microtick mismatch: {batch.snapshot_or_microtick} != {expected_child_index}"
        )

    # 1. Validate contiguous slots 0..N-1
    for idx, entry in enumerate(batch.ordered_receipt_entries):
        if entry.slot_index != idx:
            raise R2BatchValidationError(
                f"Non-contiguous receipt slot index: expected {idx}, got {entry.slot_index}"
            )
        # Verify receipt ID re-derivation
        recomputed_rid = derive_participation_receipt_id(
            micro_episode_id=batch.micro_episode_id,
            participation_kind="edge" if entry.kind == "edge" else "node",
            element_ref=entry.element_ref,
            scope_refs=list(entry.scope_refs),
            slot_index=entry.slot_index,
            prefix="pr_",
        )
        if entry.receipt_id != recomputed_rid:
            raise R2BatchValidationError(
                f"ParticipationReceipt ID re-derivation mismatch: '{entry.receipt_id}' != '{recomputed_rid}'"
            )

    # 2. Validate contiguous binding indexes 0..K-1
    for b_idx, b_entry in enumerate(batch.ordered_binding_entries):
        if b_entry.binding_index != b_idx:
            raise R2BatchValidationError(
                f"Non-contiguous binding index: expected {b_idx}, got {b_entry.binding_index}"
            )
        # Verify TBRID re-derivation
        recomputed_bid = derive_transient_binding_receipt_id(
            micro_episode_id=batch.micro_episode_id,
            binding_scope_id=b_entry.binding_scope,
            member_receipt_refs=list(b_entry.member_element_refs),
            binding_index=b_entry.binding_index,
            prefix="tbr_",
        )
        if b_entry.binding_id != recomputed_bid:
            raise R2BatchValidationError(
                f"TBRID re-derivation mismatch: '{b_entry.binding_id}' != '{recomputed_bid}'"
            )

    # 3. Check member participation and scope presence (§25)
    receipt_element_scopes: dict[Any, set[str]] = {}
    for entry in batch.ordered_receipt_entries:
        if entry.kind in ("node", "contradiction_endpoint"):
            receipt_element_scopes.setdefault(entry.element_ref, set()).update(entry.scope_refs)

    for b_entry in batch.ordered_binding_entries:
        if not b_entry.member_element_refs:
            raise R2BatchValidationError(f"TBR '{b_entry.binding_id}' has empty member list")
        for member in b_entry.member_element_refs:
            if member not in receipt_element_scopes:
                raise R2BatchValidationError(
                    f"TBR member '{member}' has no corresponding ParticipationReceipt in batch"
                )
            if b_entry.binding_scope not in receipt_element_scopes[member]:
                raise R2BatchValidationError(
                    f"TBR scope '{b_entry.binding_scope}' missing from member '{member}' receipt scope_refs"
                )

    # 4. Descriptor Authority Check (§21, §25)
    lawful_scopes = set()
    if micro_descriptor.kind == "simultaneous":
        pos_nodes = [canonical_node_ref(s["region"], s["symbol"]) for s in micro_descriptor.positive_signals]
        if len(pos_nodes) >= 2:
            lawful_scopes.add(f"r2scope:{batch.micro_episode_id}:simultaneous:0")
    elif micro_descriptor.kind == "sequence":
        n_transitions = max(0, len(micro_descriptor.steps) - 1)
        for t_idx in range(n_transitions):
            lawful_scopes.add(f"r2scope:{batch.micro_episode_id}:sequence:{t_idx}")

    for c_idx in range(len(micro_descriptor.contradictions)):
        lawful_scopes.add(f"r2scope:{batch.micro_episode_id}:contradiction:{c_idx}")

    for b_entry in batch.ordered_binding_entries:
        if b_entry.binding_scope not in lawful_scopes:
            raise R2BatchValidationError(
                f"TBR scope '{b_entry.binding_scope}' is not derivable from MicroEpisode descriptor (invented TBR authority)"
            )


# ─────────────────────────────────────────────────────────── 7. Canonical Observation Result (§30, §31)
@dataclass
class CanonicalObservationResult:
    """
    Transient observation result object (§30).
    Transient operational state only. Zero persistent cognitive memory.
    """
    result_version: str
    observation_transaction_id: str
    root_external_episode_id: str
    ingress_event_id: str
    status: str  # TRANSIENT_OBSERVED | PERSISTENT_EXECUTED | PERSISTENT_REPLAY | NO_OBSERVABLE_CONTENT
    micro_episodes: tuple[CanonicalMicroEpisodeDescriptor, ...]
    representations: tuple[SparseDistributedCognitiveRepresentation, ...]
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.result_version != OBSERVATION_RESULT_VERSION:
            raise R2DescriptorError(f"result_version must be '{OBSERVATION_RESULT_VERSION}'")
        allowed_statuses = {
            "TRANSIENT_OBSERVED",
            "PERSISTENT_EXECUTED",
            "PERSISTENT_REPLAY",
            "NO_OBSERVABLE_CONTENT",
        }
        if self.status not in allowed_statuses:
            raise R2DescriptorError(f"Invalid observation status '{self.status}'")

    _closed: bool = field(default=False, init=False)

    @property
    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self._closed:
            return
        close_result(self)
        self._closed = True

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self.close()


def close_result(result: CanonicalObservationResult) -> None:
    """
    Idempotent result lifecycle cleanup (§31).
    Closes every active SDCR created by that result without altering persistent cognitive graph state.
    """
    if not isinstance(result, CanonicalObservationResult):
        return
    for rep in result.representations:
        if hasattr(rep, "close") and callable(rep.close):
            rep.close()
    result._closed = True


# ─────────────────────────────────────────────────────────── 8. Canonical Observation Bridge Orchestrator
class CanonicalObservationBridge:
    """
    Authoritative RIC-01 / R2 Canonical Ingress & Observation Bridge (§4).
    Orchestration infrastructure connecting external occurrence to deterministic symbolic encoder,
    transient projection, and optional R1-governed persistent mutation.
    """

    def __init__(
        self,
        *,
        runtime: CanonicalR1RuntimeRoot,
        graph: CognitiveGraph,
        authorizer: PersistentObservationAuthorizer | None = None,
    ) -> None:
        self._runtime = runtime
        self._graph = graph
        self._authorizer = authorizer
        self._encoder = MasterSymbolicEncoder()
        # Ephemeral Ingress Binding Registry (§9)
        self._ephemeral_bindings: dict[str, tuple[str, str, str]] = {}

    @property
    def observation_protocol_version(self) -> str:
        return R2_OBSERVATION_PROTOCOL_VERSION

    @property
    def authorizer(self) -> PersistentObservationAuthorizer | None:
        return self._authorizer

    @property
    def runtime(self) -> CanonicalR1RuntimeRoot:
        return self._runtime

    def derive_root_episode_id(self, occurrence_descriptor: ExternalOccurrenceDescriptor) -> str:
        return derive_root_external_episode_id(
            boundary_namespace=occurrence_descriptor.boundary_namespace,
            source_occurrence_key=occurrence_descriptor.source_occurrence_key,
            prefix="root_",
        )

    def observe(
        self,
        *,
        occurrence: ExternalOccurrenceDescriptor,
        source_event_key: str,
        ingress_boundary: str,
        modality: str,
        payload: dict[str, Any],
        mode: ExecutionMode = ExecutionMode.TRANSIENT_ONLY,
        capability: object = None,
    ) -> CanonicalObservationResult:
        """
        Main canonical ingress entry point (§0, §12).
        Default mode: TRANSIENT_ONLY (Zero persistent mutation).
        """
        # Step 0: Lineage & Fail-stop Health Validation (§12, §41 Scenario G, H)
        if self._runtime.causal_runtime_health != CausalRuntimeHealth.HEALTHY:
            raise CausalRuntimeFailStopError(
                "Runtime is in MUTATION_FAILED fail-stop state. Canonical observation is blocked."
            )
        if self._runtime.canonical_lineage_state != CanonicalLineageState.VALID:
            raise CausalLineageInvalidatedError(
                "Canonical lineage is invalidated by untracked persistent mutation."
            )

        # Step 1: Pre-validation of occurrence & arguments
        if not isinstance(occurrence, ExternalOccurrenceDescriptor):
            raise R2DescriptorError("occurrence must be an ExternalOccurrenceDescriptor")
        if not isinstance(source_event_key, str) or not source_event_key.strip():
            raise R2DescriptorError("source_event_key must be a non-empty string")
        if not isinstance(ingress_boundary, str) or not ingress_boundary.strip():
            raise R2DescriptorError("ingress_boundary must be a non-empty string")
        if modality not in ("text", "code"):
            raise R2DescriptorError(f"Unsupported modality '{modality}'. R2-v1 supports only 'text' and 'code'")
        if not isinstance(mode, ExecutionMode):
            raise R2DescriptorError(f"mode must be an ExecutionMode enum, got {type(mode).__name__}")

        # Step 2: Canonical Event Descriptor Construction & Validation (§8)
        if modality == "text":
            raw_text = payload.get("raw_text")
            context = payload.get("context")
            event_desc = build_text_event_descriptor(raw_text, context=context)
        else:
            source_code = payload.get("source_code")
            module = payload.get("module", "module")
            event_desc = build_code_event_descriptor(source_code, module=module)

        validate_canonical_event_descriptor(event_desc)
        event_digest = compute_event_descriptor_digest(event_desc)

        # Step 3: Identity Derivation via Frozen R1 (§7)
        root_id = derive_root_external_episode_id(
            boundary_namespace=occurrence.boundary_namespace,
            source_occurrence_key=occurrence.source_occurrence_key,
            prefix="root_",
        )
        ingress_event_id = derive_ingress_event_id(
            root_external_episode_id=root_id,
            source_event_key=source_event_key,
            modality=modality,
            ingress_boundary=ingress_boundary,
            prefix="iev_",
        )

        # Step 4: Ephemeral Ingress Binding Registry Check (§9)
        binding_tuple = (root_id, event_digest, R2_OBSERVATION_PROTOCOL_VERSION)
        if ingress_event_id in self._ephemeral_bindings:
            existing = self._ephemeral_bindings[ingress_event_id]
            if existing != binding_tuple:
                raise R2DescriptorError(
                    f"Conflicting event descriptor registered (Ephemeral ingress binding conflict for EventID '{ingress_event_id}'): "
                    f"existing {existing} != new {binding_tuple}"
                )
        else:
            self._ephemeral_bindings[ingress_event_id] = binding_tuple

        # Step 5: Authorization Firewall (§13)
        is_persistent = mode == ExecutionMode.AUTHORIZED_PERSISTENT
        if is_persistent:
            if self._authorizer is None:
                raise R2AuthorizationError("Persistent observation denied: no authorizer configured")
            if capability is None:
                raise R2AuthorizationError("Persistent observation denied: capability is None")
            try:
                auth_res = self._authorizer.verify_persistent_observation(
                    capability=capability,
                    root_external_episode_id=root_id,
                    ingress_event_id=ingress_event_id,
                    modality=modality,
                    operation_kind="R2_AUTHORIZED_PERSISTENT",
                )
            except Exception as e:
                raise R2AuthorizationError(f"Authorizer raised exception: {e}") from e

            if auth_res is not True:  # Strict literal True check (§13)
                raise R2AuthorizationError(
                    f"Persistent observation denied: authorizer returned non-True value {auth_res!r}"
                )

        # Step 6: Single Encoder Invocation (§10)
        try:
            if modality == "text":
                episodes = self._encoder.encode_text(
                    event_desc["payload"]["raw_text"],
                    context=event_desc["payload"]["context"],
                )
            else:
                episodes = self._encoder.encode_code(
                    event_desc["payload"]["source_code"],
                    module=event_desc["payload"]["module"],
                )
        except Exception as e:
            raise R2DescriptorError(f"Symbolic encoder invocation failed: {e}") from e

        if not isinstance(episodes, list):
            raise R2DescriptorError(f"Encoder returned invalid type: {type(episodes).__name__}")

        if not episodes:
            txid = derive_observation_transaction_id(
                root_external_episode_id=root_id,
                ingress_event_id=ingress_event_id,
                operation_kind="R2_AUTHORIZED_PERSISTENT" if is_persistent else "R2_TRANSIENT_ONLY",
                observation_protocol_version=R2_OBSERVATION_PROTOCOL_VERSION,
                prefix="tx_obs_",
            )
            return CanonicalObservationResult(
                result_version=OBSERVATION_RESULT_VERSION,
                observation_transaction_id=txid,
                root_external_episode_id=root_id,
                ingress_event_id=ingress_event_id,
                status="NO_OBSERVABLE_CONTENT",
                micro_episodes=(),
                representations=(),
                diagnostics={"child_count": 0},
            )

        # Step 7: MicroEpisode Descriptors & ObservationTransactionID (§11, §20)
        op_kind = "R2_AUTHORIZED_PERSISTENT" if is_persistent else "R2_TRANSIENT_ONLY"
        txid = derive_observation_transaction_id(
            root_external_episode_id=root_id,
            ingress_event_id=ingress_event_id,
            operation_kind=op_kind,
            observation_protocol_version=R2_OBSERVATION_PROTOCOL_VERSION,
            prefix="tx_obs_",
        )

        local_cycle_raw = hashlib.sha256(
            LOCAL_CYCLE_PREFIX.encode("utf-8") + b"\0" + txid.encode("utf-8")
        ).hexdigest()
        local_parent_cycle_id = int(local_cycle_raw, 16)

        micro_descriptors: list[CanonicalMicroEpisodeDescriptor] = []
        for c_idx, ep in enumerate(episodes):
            pos_signals = tuple(
                {"region": r, "symbol": s, "weight": 1.0, "valence": ep.valence}
                for r, s in ep.signals
            )
            contra_pairs = tuple(
                {"endpoint_a": a, "endpoint_b": b, "weight": 1.0}
                for a, b in ep.contradictions
            )
            steps_tuple = ()
            if ep.kind == "sequence":
                steps_tuple = tuple(
                    tuple({"region": r, "symbol": s, "weight": 1.0} for r, s in step)
                    for step in ep.steps
                )

            candidate_dict: dict[str, Any] = {
                "micro_descriptor_version": MICRO_DESCRIPTOR_VERSION,
                "child_index": c_idx,
                "kind": ep.kind,
                "positive_signals": [dict(s) for s in pos_signals],
                "contradictions": [dict(c) for c in contra_pairs],
                "structural_weight": float(ep.structural_weight),
                "valence": float(ep.valence),
            }
            if ep.kind == "sequence":
                candidate_dict["steps"] = [[dict(s) for s in step] for step in steps_tuple]

            micro_id = derive_micro_episode_id(
                observation_transaction_id=txid,
                child_index=c_idx,
                canonical_episode_descriptor=candidate_dict,
                prefix="mep_",
            )

            micro_descriptors.append(
                CanonicalMicroEpisodeDescriptor(
                    micro_descriptor_version=MICRO_DESCRIPTOR_VERSION,
                    micro_episode_id=micro_id,
                    child_index=c_idx,
                    kind=ep.kind,
                    positive_signals=pos_signals,
                    contradictions=contra_pairs,
                    structural_weight=float(ep.structural_weight),
                    valence=float(ep.valence),
                    steps=steps_tuple,
                )
            )

        # Step 8: Persistent Execution (Phase 1)
        persistent_committed = False
        persistent_executed = False

        if is_persistent:
            canonical_targets: list[dict[str, Any]] = []
            for m_desc in micro_descriptors:
                targets = [
                    {"target_kind": "node", "ref": canonical_node_ref(s["region"], s["symbol"])}
                    for s in m_desc.positive_signals
                ]
                targets.extend(
                    {"target_kind": "contradiction", "endpoints": [c["endpoint_a"], c["endpoint_b"]]}
                    for c in m_desc.contradictions
                )
                if m_desc.kind == "sequence":
                    for step in m_desc.steps:
                        targets.extend(
                            {"target_kind": "node", "ref": canonical_node_ref(s["region"], s["symbol"])}
                            for s in step
                        )
                canonical_targets.append({
                    "micro_episode_id": m_desc.micro_episode_id,
                    "child_index": m_desc.child_index,
                    "targets": targets,
                })

            mutation_descriptor = {
                "mutation_descriptor_version": MUTATION_DESCRIPTOR_VERSION,
                "observation_protocol_version": R2_OBSERVATION_PROTOCOL_VERSION,
                "ingress_event_id": ingress_event_id,
                "child_count": len(micro_descriptors),
                "compiled_targets": canonical_targets,
            }

            command = PersistentMutationCommand(
                mutation_owner_ref=MUTATION_OWNER_REF,
                mutation_kind=MUTATION_KIND,
                canonical_targets=canonical_targets,
                canonical_mutation_descriptor=mutation_descriptor,
                owner_defined_transaction_scope=f"r2:obs:{ingress_event_id}",
            )

            def _mutator_callback() -> None:
                for m_desc, ep in zip(micro_descriptors, episodes, strict=False):
                    for contra in m_desc.contradictions:
                        self._graph.add_contradiction(contra["endpoint_a"], contra["endpoint_b"])

                    if m_desc.kind == "simultaneous":
                        if ep.signals:
                            self._graph.observe(
                                ep.signals,
                                context=ep.context,
                                valence=ep.valence,
                                structural_weight=ep.structural_weight,
                            )
                    else:
                        if ep.steps:
                            self._graph.observe_sequence(
                                ep.steps,
                                context=ep.context,
                                valence=ep.valence,
                                structural_weight=ep.structural_weight,
                            )

                    eligible_edges = self._derive_rfc11_eligible_edges(m_desc)
                    verified_edges = [
                        edge for edge in eligible_edges
                        if self._graph.edge(edge[0], edge[1]) is not None
                    ]
                    if verified_edges and self._graph.assembly_manager is not None:
                        self._graph.assembly_manager.record_participation(
                            participating_edges=verified_edges,
                            context=ep.context,
                            root_episode_id=root_id,
                            valid_origin=True,
                            self_derived=False,
                        )

            _r1_txid, executed, _ = self._runtime.execute_persistent_command(
                command=command,
                root_external_episode_id=root_id,
                ingress_event_id=ingress_event_id,
                event_descriptor_digest=event_digest,
                mutator_callback=_mutator_callback,
            )
            persistent_committed = True
            persistent_executed = executed

        # Step 9: Transient Projection (Phase 2) against current graph (§28)
        created_sdcrs: list[SparseDistributedCognitiveRepresentation] = []
        try:
            for c_idx, (m_desc, ep) in enumerate(zip(micro_descriptors, episodes, strict=False)):
                batch = self._build_receipt_batch(
                    txid=txid,
                    micro_desc=m_desc,
                    ep=ep,
                    child_index=c_idx,
                    local_parent_cycle_id=local_parent_cycle_id,
                )

                validate_canonical_receipt_batch(
                    batch=batch,
                    expected_txid=txid,
                    expected_micro_id=m_desc.micro_episode_id,
                    expected_child_index=c_idx,
                    expected_cycle_id=local_parent_cycle_id,
                    micro_descriptor=m_desc,
                )

                if not batch.ordered_receipt_entries:
                    continue

                positive_cues = {
                    str(r.element_ref): r.activation_magnitude
                    for r in batch.ordered_receipt_entries
                    if r.kind == "node" and r.activation_magnitude > 0.0
                }
                selected_asms: set[tuple[str, int]] = set()
                if positive_cues and self._graph.assembly_manager is not None:
                    scored = self._graph.assembly_manager.select_assemblies(
                        cues=positive_cues,
                        context=ep.context,
                    )
                    for asm_obj, _, _ in scored:
                        selected_asms.add((asm_obj.assembly_id, asm_obj.version))

                rep_engine = self._graph.representation_engine
                participation_receipts = [
                    ParticipationReceipt(
                        receipt_id=r.receipt_id,
                        element_ref=r.element_ref,
                        parent_cycle_id=local_parent_cycle_id,
                        snapshot_or_microtick=c_idx,
                        origin_lineage="external",
                        participation_kind="edge" if r.kind == "edge" else "node",
                        scope_refs=r.scope_refs,
                        relational_drive=r.relational_drive,
                        activation_magnitude=r.activation_magnitude,
                        created_t=self._graph.t,
                    )
                    for r in batch.ordered_receipt_entries
                ]

                tbr_receipts = [
                    TransientBindingReceipt(
                        binding_id=b.binding_id,
                        parent_snapshot_ref=(local_parent_cycle_id, c_idx),
                        binding_scope_id=b.binding_scope,
                        member_receipt_refs=b.member_element_refs,
                        origin_view="external",
                        created_t=self._graph.t,
                    )
                    for b in batch.ordered_binding_entries
                ]

                sdcr = rep_engine.build_canonical_representation(
                    causal_parent_ref=m_desc.micro_episode_id,
                    parent_cycle_id=local_parent_cycle_id,
                    snapshot_or_microtick=c_idx,
                    context=ep.context,
                    participation_receipts=participation_receipts,
                    transient_bindings=tbr_receipts,
                    active_assemblies=selected_asms,
                )
                created_sdcrs.append(sdcr)

        except Exception as e:
            for partial_sdcr in created_sdcrs:
                if hasattr(partial_sdcr, "close") and callable(partial_sdcr.close):
                    partial_sdcr.close()

            if is_persistent:
                raise R2ProjectionFailure(
                    f"Transient projection failed after persistent decision: {e}",
                    transaction_id=txid,
                    persistent_executed=persistent_executed,
                    persistent_committed=persistent_committed,
                    failed_child_index=len(created_sdcrs),
                    stage="transient_projection",
                    original_exception=e,
                ) from e
            raise

        if is_persistent:
            final_status = "PERSISTENT_EXECUTED" if persistent_executed else "PERSISTENT_REPLAY"
        else:
            final_status = "TRANSIENT_OBSERVED"

        return CanonicalObservationResult(
            result_version=OBSERVATION_RESULT_VERSION,
            observation_transaction_id=txid,
            root_external_episode_id=root_id,
            ingress_event_id=ingress_event_id,
            status=final_status,
            micro_episodes=tuple(micro_descriptors),
            representations=tuple(created_sdcrs),
            diagnostics={
                "child_count": len(micro_descriptors),
                "representation_count": len(created_sdcrs),
                "persistent_executed": persistent_executed,
            },
        )

    def observe_text(
        self,
        *,
        boundary_namespace: str,
        source_occurrence_key: str,
        source_event_key: str,
        ingress_boundary: str,
        raw_text: str,
        context: str | None = None,
        mode: ExecutionMode = ExecutionMode.TRANSIENT_ONLY,
        capability: object = None,
    ) -> CanonicalObservationResult:
        occ = ExternalOccurrenceDescriptor(boundary_namespace, source_occurrence_key)
        return self.observe(
            occurrence=occ,
            source_event_key=source_event_key,
            ingress_boundary=ingress_boundary,
            modality="text",
            payload={"raw_text": raw_text, "context": context},
            mode=mode,
            capability=capability,
        )

    def observe_code(
        self,
        *,
        boundary_namespace: str,
        source_occurrence_key: str,
        source_event_key: str,
        ingress_boundary: str,
        source_code: str,
        module: str = "module",
        mode: ExecutionMode = ExecutionMode.TRANSIENT_ONLY,
        capability: object = None,
    ) -> CanonicalObservationResult:
        occ = ExternalOccurrenceDescriptor(boundary_namespace, source_occurrence_key)
        return self.observe(
            occurrence=occ,
            source_event_key=source_event_key,
            ingress_boundary=ingress_boundary,
            modality="code",
            payload={"source_code": source_code, "module": module},
            mode=mode,
            capability=capability,
        )

    def _derive_rfc11_eligible_edges(
        self, micro_desc: CanonicalMicroEpisodeDescriptor
    ) -> list[tuple[str, str]]:
        eligible: list[tuple[str, str]] = []
        if micro_desc.kind == "simultaneous":
            unique_nodes: list[str] = []
            seen: set[str] = set()
            for s in micro_desc.positive_signals:
                n = canonical_node_ref(s["region"], s["symbol"])
                if n not in seen:
                    seen.add(n)
                    unique_nodes.append(n)
            for a in unique_nodes:
                for b in unique_nodes:
                    if a != b:
                        eligible.append((a, b))
        elif micro_desc.kind == "sequence":
            steps = micro_desc.steps
            for p_i, step_i in enumerate(steps):
                nodes_i = [canonical_node_ref(s["region"], s["symbol"]) for s in step_i]
                for p_j, step_j in enumerate(steps):
                    step_distance = p_j - p_i
                    if step_distance not in (0, 1):
                        continue
                    nodes_j = [canonical_node_ref(s["region"], s["symbol"]) for s in step_j]
                    for u in nodes_i:
                        for v in nodes_j:
                            if u != v and (u, v) not in eligible and not self._is_excluded_rfc11_edge(u, v):
                                eligible.append((u, v))
        return eligible

    def _is_excluded_rfc11_edge(self, u: str, v: str) -> bool:
        for n in (u, v):
            if n.startswith("ev:") or ":ev:" in n:
                return True
            if n.startswith("cat:") or ":cat:" in n:
                return True
            if n.startswith("hub:") or ":concept:" in n:
                return True
            if n.startswith("inst:") or ":inst:" in n:
                return True
        return False

    def _build_receipt_batch(
        self,
        *,
        txid: str,
        micro_desc: CanonicalMicroEpisodeDescriptor,
        ep: SensoryEpisode,
        child_index: int,
        local_parent_cycle_id: int,
    ) -> CanonicalReceiptBatch:
        receipt_entries: list[CanonicalReceiptEntry] = []
        binding_entries: list[CanonicalBindingEntry] = []
        current_slot = 0
        current_binding_idx = 0

        sim_scope: str | None = None
        sim_members: list[str] = []
        if micro_desc.kind == "simultaneous":
            for s in micro_desc.positive_signals:
                n = canonical_node_ref(s["region"], s["symbol"])
                if n not in sim_members:
                    sim_members.append(n)
            if len(sim_members) >= 2:
                sim_scope = f"r2scope:{micro_desc.micro_episode_id}:simultaneous:0"
                bid = derive_transient_binding_receipt_id(
                    micro_episode_id=micro_desc.micro_episode_id,
                    binding_scope_id=sim_scope,
                    member_receipt_refs=sim_members,
                    binding_index=current_binding_idx,
                    prefix="tbr_",
                )
                binding_entries.append(
                    CanonicalBindingEntry(
                        binding_index=current_binding_idx,
                        binding_id=bid,
                        scope_kind="simultaneous",
                        scope_index=0,
                        binding_scope=sim_scope,
                        member_element_refs=tuple(sim_members),
                        origin_view="external",
                    )
                )
                current_binding_idx += 1

        seq_scopes_by_node: dict[str, list[str]] = {}
        if micro_desc.kind == "sequence":
            for t_idx in range(max(0, len(micro_desc.steps) - 1)):
                step_src = [canonical_node_ref(s["region"], s["symbol"]) for s in micro_desc.steps[t_idx]]
                step_dst = [canonical_node_ref(s["region"], s["symbol"]) for s in micro_desc.steps[t_idx + 1]]
                members: list[str] = []
                for n in step_src:
                    if n not in members:
                        members.append(n)
                for n in step_dst:
                    if n not in members:
                        members.append(n)
                if len(members) >= 2:
                    t_scope = f"r2scope:{micro_desc.micro_episode_id}:sequence:{t_idx}"
                    bid = derive_transient_binding_receipt_id(
                        micro_episode_id=micro_desc.micro_episode_id,
                        binding_scope_id=t_scope,
                        member_receipt_refs=members,
                        binding_index=current_binding_idx,
                        prefix="tbr_",
                    )
                    binding_entries.append(
                        CanonicalBindingEntry(
                            binding_index=current_binding_idx,
                            binding_id=bid,
                            scope_kind="sequence",
                            scope_index=t_idx,
                            binding_scope=t_scope,
                            member_element_refs=tuple(members),
                            origin_view="external",
                        )
                    )
                    current_binding_idx += 1
                    for m in members:
                        seq_scopes_by_node.setdefault(m, []).append(t_scope)

        contra_scopes_by_endpoint: dict[str, list[str]] = {}
        for c_idx, contra in enumerate(micro_desc.contradictions):
            ep_a = canonical_contradiction_endpoint_ref(contra["endpoint_a"])
            ep_b = canonical_contradiction_endpoint_ref(contra["endpoint_b"])
            c_members = [ep_a, ep_b]
            c_scope = f"r2scope:{micro_desc.micro_episode_id}:contradiction:{c_idx}"
            bid = derive_transient_binding_receipt_id(
                micro_episode_id=micro_desc.micro_episode_id,
                binding_scope_id=c_scope,
                member_receipt_refs=c_members,
                binding_index=current_binding_idx,
                prefix="tbr_",
            )
            binding_entries.append(
                CanonicalBindingEntry(
                    binding_index=current_binding_idx,
                    binding_id=bid,
                    scope_kind="contradiction",
                    scope_index=c_idx,
                    binding_scope=c_scope,
                    member_element_refs=tuple(c_members),
                    origin_view="external",
                )
            )
            current_binding_idx += 1
            contra_scopes_by_endpoint.setdefault(ep_a, []).append(c_scope)
            contra_scopes_by_endpoint.setdefault(ep_b, []).append(c_scope)

        if micro_desc.kind == "simultaneous":
            for occ_idx, s in enumerate(micro_desc.positive_signals):
                n = canonical_node_ref(s["region"], s["symbol"])
                occ_scope = f"r2scope:{micro_desc.micro_episode_id}:node_occ:{occ_idx}"
                scopes = [occ_scope]
                if sim_scope:
                    scopes.append(sim_scope)
                rid = derive_participation_receipt_id(
                    micro_episode_id=micro_desc.micro_episode_id,
                    participation_kind="node",
                    element_ref=n,
                    scope_refs=scopes,
                    slot_index=current_slot,
                    prefix="pr_",
                )
                receipt_entries.append(
                    CanonicalReceiptEntry(
                        slot_index=current_slot,
                        receipt_id=rid,
                        kind="node",
                        element_ref=n,
                        occurrence_scope=occ_scope,
                        scope_refs=tuple(scopes),
                        origin_lineage="external",
                        origin_view="external",
                        activation_magnitude=1.0,
                        relational_drive=0.0,
                    )
                )
                current_slot += 1
        else:
            step_occ_counter = 0
            for step in micro_desc.steps:
                for s in step:
                    n = canonical_node_ref(s["region"], s["symbol"])
                    occ_scope = f"r2scope:{micro_desc.micro_episode_id}:node_occ:{step_occ_counter}"
                    scopes = [occ_scope]
                    if n in seq_scopes_by_node:
                        for sc in seq_scopes_by_node[n]:
                            if sc not in scopes:
                                scopes.append(sc)
                    rid = derive_participation_receipt_id(
                        micro_episode_id=micro_desc.micro_episode_id,
                        participation_kind="node",
                        element_ref=n,
                        scope_refs=scopes,
                        slot_index=current_slot,
                        prefix="pr_",
                    )
                    receipt_entries.append(
                        CanonicalReceiptEntry(
                            slot_index=current_slot,
                            receipt_id=rid,
                            kind="node",
                            element_ref=n,
                            occurrence_scope=occ_scope,
                            scope_refs=tuple(scopes),
                            origin_lineage="external",
                            origin_view="external",
                            activation_magnitude=1.0,
                            relational_drive=0.0,
                        )
                    )
                    current_slot += 1
                    step_occ_counter += 1

        for c_occ_idx, contra in enumerate(micro_desc.contradictions):
            for endpoint_raw in (contra["endpoint_a"], contra["endpoint_b"]):
                ep_ref = canonical_contradiction_endpoint_ref(endpoint_raw)
                occ_scope = f"r2scope:{micro_desc.micro_episode_id}:contra_occ:{c_occ_idx}_{ep_ref}"
                scopes = [occ_scope]
                if ep_ref in contra_scopes_by_endpoint:
                    for sc in contra_scopes_by_endpoint[ep_ref]:
                        if sc not in scopes:
                            scopes.append(sc)
                rid = derive_participation_receipt_id(
                    micro_episode_id=micro_desc.micro_episode_id,
                    participation_kind="node",
                    element_ref=ep_ref,
                    scope_refs=scopes,
                    slot_index=current_slot,
                    prefix="pr_",
                )
                receipt_entries.append(
                    CanonicalReceiptEntry(
                        slot_index=current_slot,
                        receipt_id=rid,
                        kind="contradiction_endpoint",
                        element_ref=ep_ref,
                        occurrence_scope=occ_scope,
                        scope_refs=tuple(scopes),
                        origin_lineage="external",
                        origin_view="external",
                        activation_magnitude=1.0,
                        relational_drive=0.0,
                    )
                )
                current_slot += 1

        relations = self._derive_all_observation_relations(micro_desc)
        edge_occ_idx = 0
        for src, dst in relations:
            edge_obj = self._graph.edge(src, dst)
            if edge_obj is not None and edge_obj.gate_open(ep.context):
                occ_scope = f"r2scope:{micro_desc.micro_episode_id}:edge_occ:{edge_occ_idx}"
                scopes = [occ_scope]
                rid = derive_participation_receipt_id(
                    micro_episode_id=micro_desc.micro_episode_id,
                    participation_kind="edge",
                    element_ref=(src, dst),
                    scope_refs=scopes,
                    slot_index=current_slot,
                    prefix="pr_",
                )
                receipt_entries.append(
                    CanonicalReceiptEntry(
                        slot_index=current_slot,
                        receipt_id=rid,
                        kind="edge",
                        element_ref=(src, dst),
                        occurrence_scope=occ_scope,
                        scope_refs=tuple(scopes),
                        origin_lineage="external",
                        origin_view="external",
                        activation_magnitude=0.0,
                        relational_drive=float(edge_obj.W),
                    )
                )
                current_slot += 1
                edge_occ_idx += 1

        return CanonicalReceiptBatch(
            batch_version=RECEIPT_BATCH_VERSION,
            observation_transaction_id=txid,
            micro_episode_id=micro_desc.micro_episode_id,
            child_index=child_index,
            local_parent_cycle_id=local_parent_cycle_id,
            snapshot_or_microtick=child_index,
            ordered_receipt_entries=receipt_entries,
            ordered_binding_entries=binding_entries,
        )

    def _derive_all_observation_relations(
        self, micro_desc: CanonicalMicroEpisodeDescriptor
    ) -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        if micro_desc.kind == "simultaneous":
            nodes: list[str] = []
            for s in micro_desc.positive_signals:
                n = canonical_node_ref(s["region"], s["symbol"])
                if n not in nodes:
                    nodes.append(n)
            for a in nodes:
                for b in nodes:
                    if a != b and (a, b) not in pairs:
                        pairs.append((a, b))
        else:
            steps = micro_desc.steps
            for p_i, step_i in enumerate(steps):
                nodes_i = [canonical_node_ref(s["region"], s["symbol"]) for s in step_i]
                for p_j, step_j in enumerate(steps):
                    nodes_j = [canonical_node_ref(s["region"], s["symbol"]) for s in step_j]
                    for u in nodes_i:
                        for v in nodes_j:
                            if u != v and (u, v) not in pairs:
                                pairs.append((u, v))
        return pairs
