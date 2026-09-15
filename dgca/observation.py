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

# Frozen literal structured semantics registry from Section 3.1 & Erratum v1.1.1 (§3.1, B01)
R2_OBSERVATION_SEMANTICS_REGISTRY: dict[str, Any] = {
    "protocol_version": "R2-OBS-1.0",
    "event_descriptor_version": "R2-EVENT-1.0",
    "micro_descriptor_version": "R2-MICRO-1.0",
    "mutation_descriptor_version": "R2-MUT-1.0",
    "receipt_batch_version": "R2-RB-1.0",
    "result_version": "R2-RESULT-1.0",
    "supported_modalities": ["text", "code"],
    "operation_kinds": [
        "R2_TRANSIENT_ONLY",
        "R2_AUTHORIZED_PERSISTENT",
    ],
    "persistent_transaction_granularity": "ONE_ENCODED_INGRESS_EVENT",
    "observation_relation_policy": {
        "simultaneous": "ALL_ORDERED_PAIRS",
        "sequence_same_step": "ALL_ORDERED_PAIRS",
        "sequence_cross_step": "ALL_ORDERED_CROSS_PAIRS",
        "self_ref": "EXCLUDED",
    },
    "rfc11_evidence_policy": {
        "simultaneous": "ALL_ORDERED_PAIRS",
        "sequence_same_step": "ALL_ORDERED_PAIRS",
        "sequence_adjacent_step": "ALL_ORDERED_CROSS_PAIRS",
        "sequence_nonadjacent_step": "EXCLUDED_TEMPORAL_DERIVED",
        "synthetic_event_role": "EXCLUDED_DERIVED",
        "concept_generalization_generated": "EXCLUDED_INTERNAL_DERIVED",
    },
    "tbr_policy": {
        "authority": "EXPLICIT_CANONICAL_MICROEPISODE_STRUCTURE_ONLY",
        "simultaneous": "ONE_BINDING_IF_AT_LEAST_TWO_POSITIVE_OCCURRENCES",
        "sequence": "ONE_BINDING_PER_ADJACENT_TRANSITION",
        "contradiction": "ONE_BINDING_PER_EXPLICIT_PAIR",
        "coactivation_only": "FORBIDDEN",
        "member_scope_validation": "REQUIRED",
    },
    "receipt_order": [
        "POSITIVE_NODE_OCCURRENCES",
        "CONTRADICTION_ENDPOINT_OCCURRENCES",
        "LIVE_GATE_OPEN_OBSERVATION_RELATION_EDGE_RECEIPTS",
    ],
    "sdcr_cardinality": "ONE_PER_OBSERVABLE_MICROEPISODE",
    "projection_timing": "AFTER_PERSISTENT_COMMIT_OR_REPLAY_DECISION",
    "projection_failure": "PERSISTENT_COMMIT_REMAINS_AUTHORITATIVE_CLOSE_PARTIAL_SDCRS",
    "transient_replay": "CURRENT_STATE_RECONSTRUCTION",
    "authorization_default": "DENY_ALL",
}


def validate_r2_observation_semantics_registry(registry: dict[str, Any] | None = None) -> None:
    """Validates that registry contains all 18 frozen policy literals (§3.1, Erratum v1.1.1, B01)."""
    target = registry if registry is not None else R2_OBSERVATION_SEMANTICS_REGISTRY
    if not isinstance(target, dict):
        raise R2DescriptorError("R2 observation semantics registry must be a dictionary")
    required_keys = {
        "protocol_version",
        "event_descriptor_version",
        "micro_descriptor_version",
        "mutation_descriptor_version",
        "receipt_batch_version",
        "result_version",
        "supported_modalities",
        "operation_kinds",
        "persistent_transaction_granularity",
        "observation_relation_policy",
        "rfc11_evidence_policy",
        "tbr_policy",
        "receipt_order",
        "sdcr_cardinality",
        "projection_timing",
        "projection_failure",
        "transient_replay",
        "authorization_default",
    }
    if set(target.keys()) != required_keys:
        missing = required_keys - set(target.keys())
        extra = set(target.keys()) - required_keys
        raise R2DescriptorError(f"Semantics registry keys mismatch. Missing: {missing}, Extra: {extra}")


def compute_r2_observation_semantics_digest(registry: dict[str, Any] | None = None) -> str:
    """Computes/recomputes the exact frozen R2 observation semantics digest via direct canonical SHA-256 (§3, Erratum v1.1.1, B01)."""
    target = registry if registry is not None else R2_OBSERVATION_SEMANTICS_REGISTRY
    validate_r2_observation_semantics_registry(target)
    return hashlib.sha256(canonical_json_bytes(target)).hexdigest()


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


# ─────────────────────────────────────────────────────────── 5. Canonical MicroEpisode Descriptor (§11, B02)
@dataclass(frozen=True)
class CanonicalMicroEpisodeDescriptor:
    """Canonical MicroEpisode descriptor representing one ordered child episode (§11, B02)."""
    descriptor_version: str = MICRO_DESCRIPTOR_VERSION
    kind: str = "simultaneous"  # "simultaneous" | "sequence"
    context: str | None = None
    signals: tuple[tuple[str, str], ...] = ()
    steps: tuple[tuple[tuple[str, str], ...], ...] = ()
    structural_weight: float = 1.0
    valence: float = 0.0
    contradictions: tuple[tuple[str, str], ...] = ()
    micro_episode_id: str | None = None
    child_index: int | None = None

    def __post_init__(self) -> None:
        if self.descriptor_version != MICRO_DESCRIPTOR_VERSION:
            raise R2DescriptorError(f"descriptor_version must be '{MICRO_DESCRIPTOR_VERSION}'")
        if self.kind not in ("simultaneous", "sequence"):
            raise R2DescriptorError(f"kind must be 'simultaneous' or 'sequence', got '{self.kind}'")
        if self.context is not None and not isinstance(self.context, str):
            raise R2DescriptorError("context must be string or None")
        if not math.isfinite(self.structural_weight):
            raise R2DescriptorError("structural_weight must be a finite float")
        if not math.isfinite(self.valence):
            raise R2DescriptorError("valence must be a finite float")

        # Validate signals
        for s in self.signals:
            if not isinstance(s, (tuple, list)) or len(s) != 2:
                raise R2DescriptorError(f"signal must be (region, symbol) pair, got {s!r}")
            r, sym = s
            if not isinstance(r, str) or not r.strip() or not isinstance(sym, str) or not sym.strip():
                raise R2DescriptorError(f"region and symbol must be non-empty strings, got {s!r}")

        # Validate contradictions
        for c in self.contradictions:
            if not isinstance(c, (tuple, list)) or len(c) != 2:
                raise R2DescriptorError(f"contradiction must be (endpoint_a, endpoint_b) pair, got {c!r}")
            a, b = c
            if not isinstance(a, str) or not a.strip() or not isinstance(b, str) or not b.strip():
                raise R2DescriptorError(f"contradiction endpoints must be non-empty strings, got {c!r}")

        # Kind-specific shape validation (§11, B02)
        if self.kind == "simultaneous":
            if self.steps:
                raise R2DescriptorError("simultaneous micro-episode must have empty steps")
            if not self.signals and not self.contradictions:
                raise R2DescriptorError("simultaneous micro-episode must have non-empty signals or contradictions")
        elif self.kind == "sequence":
            if self.signals:
                raise R2DescriptorError("sequence micro-episode must have empty signals")
            if len(self.steps) < 2:
                raise R2DescriptorError("sequence micro-episode must have at least 2 steps")
            for step in self.steps:
                if not step:
                    raise R2DescriptorError("sequence steps must not be empty")
                for s in step:
                    if not isinstance(s, (tuple, list)) or len(s) != 2:
                        raise R2DescriptorError(f"step signal must be (region, symbol) pair, got {s!r}")
                    r, sym = s
                    if not isinstance(r, str) or not r.strip() or not isinstance(sym, str) or not sym.strip():
                        raise R2DescriptorError(f"step region and symbol must be non-empty strings, got {s!r}")

    @property
    def positive_signals(self) -> tuple[dict[str, Any], ...]:
        return tuple({"region": r, "symbol": s, "weight": 1.0, "valence": self.valence} for r, s in self.signals)

    @property
    def micro_descriptor_version(self) -> str:
        return self.descriptor_version

    def to_dict(self) -> dict[str, Any]:
        """Exact canonical MicroEpisode descriptor dictionary (§11, B02)."""
        return {
            "descriptor_version": self.descriptor_version,
            "kind": self.kind,
            "context": self.context,
            "signals": [list(s) for s in self.signals],
            "steps": [[list(s) for s in step] for step in self.steps],
            "structural_weight": float(self.structural_weight),
            "valence": float(self.valence),
            "contradictions": [list(c) for c in self.contradictions],
        }


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


# ─────────────────────────────────────────────────────────── 6. Participation Receipts & TBRs (§22, §23, §24, B05)
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


def derive_all_observation_relations(
    micro_desc: CanonicalMicroEpisodeDescriptor,
) -> list[tuple[str, str]]:
    """
    Derives ordered observation relation candidates (§15, D03).
    Preserves first-occurrence order while using a seen-set for O(1) duplicate checks.
    """
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    if micro_desc.kind == "simultaneous":
        nodes: list[str] = []
        node_seen: set[str] = set()
        for r, s in micro_desc.signals:
            n = canonical_node_ref(r, s)
            if n not in node_seen:
                node_seen.add(n)
                nodes.append(n)
        for a in nodes:
            for b in nodes:
                if a != b:
                    pair = (a, b)
                    if pair not in seen:
                        seen.add(pair)
                        pairs.append(pair)
    else:
        steps = micro_desc.steps
        for step_i in steps:
            nodes_i = [canonical_node_ref(r, s) for r, s in step_i]
            for step_j in steps:
                nodes_j = [canonical_node_ref(r, s) for r, s in step_j]
                for u in nodes_i:
                    for v in nodes_j:
                        if u != v:
                            pair = (u, v)
                            if pair not in seen:
                                seen.add(pair)
                                pairs.append(pair)
    return pairs


@dataclass(frozen=True)
class ExpectedReceiptEntry:
    """Exact expected receipt metadata derived before receipt comparison (§22, §25, PIR02-B02)."""
    slot_index: int
    slot_class: str  # "POSITIVE_NODE_OCCURRENCES" | "CONTRADICTION_ENDPOINT_OCCURRENCES" | "LIVE_GATE_OPEN_OBSERVATION_RELATION_EDGE_RECEIPTS"
    kind: str  # "node" | "contradiction_endpoint" | "edge"
    element_ref: str | tuple[str, str]
    occurrence_scope: str
    scope_refs: tuple[str, ...]
    activation_magnitude: float
    relational_drive: float
    receipt_id: str


def derive_expected_receipt_plan(
    micro_descriptor: CanonicalMicroEpisodeDescriptor,
    micro_episode_id: str,
    current_relation_view: Any = None,
) -> list[ExpectedReceiptEntry]:
    """
    Pure deterministic helper deriving exact expected ordered receipt metadata (§22, §25, PIR02-B02).
    Derives slot class, kind, element_ref, exact occurrence scope, ordered scope_refs,
    activation_magnitude, relational_drive, and ReceiptID before ID comparison.
    """
    mid = micro_episode_id
    expected: list[ExpectedReceiptEntry] = []
    slot = 0

    # 1. Expected binding scopes
    sim_scope: str | None = None
    seq_scopes: list[str] = []
    contra_scopes: list[str] = []

    if micro_descriptor.kind == "simultaneous":
        if len(micro_descriptor.signals) >= 2:
            sim_scope = f"r2scope:{mid}:simultaneous:0"
    elif micro_descriptor.kind == "sequence":
        for t_idx in range(max(0, len(micro_descriptor.steps) - 1)):
            seq_scopes.append(f"r2scope:{mid}:sequence:{t_idx}")

    for c_idx in range(len(micro_descriptor.contradictions)):
        contra_scopes.append(f"r2scope:{mid}:contradiction:{c_idx}")

    # 2. Positive node occurrences (Global Slot Order 1)
    if micro_descriptor.kind == "simultaneous":
        for occ_idx, (r, s) in enumerate(micro_descriptor.signals):
            n = canonical_node_ref(r, s)
            occ_scope = f"r2occ:{mid}:simultaneous:{occ_idx}"
            scopes = [mid, occ_scope]
            if sim_scope is not None:
                scopes.append(sim_scope)
            rid = derive_participation_receipt_id(
                micro_episode_id=mid,
                participation_kind="node",
                element_ref=n,
                scope_refs=scopes,
                slot_index=slot,
                prefix="pr_",
            )
            expected.append(
                ExpectedReceiptEntry(
                    slot_index=slot,
                    slot_class="POSITIVE_NODE_OCCURRENCES",
                    kind="node",
                    element_ref=n,
                    occurrence_scope=occ_scope,
                    scope_refs=tuple(scopes),
                    activation_magnitude=1.0,
                    relational_drive=0.0,
                    receipt_id=rid,
                )
            )
            slot += 1
    else:
        num_transitions = max(0, len(micro_descriptor.steps) - 1)
        for step_idx, step in enumerate(micro_descriptor.steps):
            for step_occ_idx, (r, s) in enumerate(step):
                n = canonical_node_ref(r, s)
                occ_scope = f"r2occ:{mid}:step:{step_idx}:{step_occ_idx}"
                scopes = [mid, occ_scope]
                if step_idx > 0 and (step_idx - 1) < num_transitions:
                    scopes.append(seq_scopes[step_idx - 1])
                if step_idx < num_transitions:
                    scopes.append(seq_scopes[step_idx])
                rid = derive_participation_receipt_id(
                    micro_episode_id=mid,
                    participation_kind="node",
                    element_ref=n,
                    scope_refs=scopes,
                    slot_index=slot,
                    prefix="pr_",
                )
                expected.append(
                    ExpectedReceiptEntry(
                        slot_index=slot,
                        slot_class="POSITIVE_NODE_OCCURRENCES",
                        kind="node",
                        element_ref=n,
                        occurrence_scope=occ_scope,
                        scope_refs=tuple(scopes),
                        activation_magnitude=1.0,
                        relational_drive=0.0,
                        receipt_id=rid,
                    )
                )
                slot += 1

    # 3. Contradiction endpoint occurrences (Global Slot Order 2)
    for c_idx, (a, b) in enumerate(micro_descriptor.contradictions):
        c_scope = contra_scopes[c_idx]
        for ep_idx, ep_raw in enumerate([a, b]):
            ep_ref = canonical_contradiction_endpoint_ref(ep_raw)
            occ_scope = f"r2occ:{mid}:contradiction:{c_idx}:{ep_idx}"
            scopes = [mid, occ_scope, c_scope]
            rid = derive_participation_receipt_id(
                micro_episode_id=mid,
                participation_kind="node",
                element_ref=ep_ref,
                scope_refs=scopes,
                slot_index=slot,
                prefix="pr_",
            )
            expected.append(
                ExpectedReceiptEntry(
                    slot_index=slot,
                    slot_class="CONTRADICTION_ENDPOINT_OCCURRENCES",
                    kind="contradiction_endpoint",
                    element_ref=ep_ref,
                    occurrence_scope=occ_scope,
                    scope_refs=tuple(scopes),
                    activation_magnitude=1.0,
                    relational_drive=0.0,
                    receipt_id=rid,
                )
            )
            slot += 1

    # 4. Live gate-open observation relation edges (Global Slot Order 3)
    relations = derive_all_observation_relations(micro_descriptor)
    if current_relation_view is not None:
        for rel_idx, (src, dst) in enumerate(relations):
            edge_obj = None
            if hasattr(current_relation_view, "edge") and callable(current_relation_view.edge):
                edge_obj = current_relation_view.edge(src, dst)
            elif isinstance(current_relation_view, dict):
                edge_obj = current_relation_view.get((src, dst))

            if edge_obj is not None:
                is_open = True
                if hasattr(edge_obj, "gate_open") and callable(edge_obj.gate_open):
                    is_open = edge_obj.gate_open(micro_descriptor.context)
                if is_open:
                    occ_scope = f"r2relation:{mid}:{rel_idx}"
                    scopes = [mid, occ_scope]
                    rid = derive_participation_receipt_id(
                        micro_episode_id=mid,
                        participation_kind="edge",
                        element_ref=(src, dst),
                        scope_refs=scopes,
                        slot_index=slot,
                        prefix="pr_",
                    )
                    expected.append(
                        ExpectedReceiptEntry(
                            slot_index=slot,
                            slot_class="LIVE_GATE_OPEN_OBSERVATION_RELATION_EDGE_RECEIPTS",
                            kind="edge",
                            element_ref=(src, dst),
                            occurrence_scope=occ_scope,
                            scope_refs=tuple(scopes),
                            activation_magnitude=0.0,
                            relational_drive=float(getattr(edge_obj, "W", 1.0)),
                            receipt_id=rid,
                        )
                    )
                    slot += 1

    return expected


def validate_canonical_receipt_batch(
    batch: CanonicalReceiptBatch,
    *,
    expected_txid: str,
    expected_micro_id: str,
    expected_child_index: int,
    expected_cycle_id: int,
    micro_descriptor: CanonicalMicroEpisodeDescriptor,
    graph: CognitiveGraph | None = None,
) -> None:
    """
    Strict fail-closed validator for CanonicalReceiptBatch (§25, B05, PIR02-B02).
    Rederives the exact expected receipt plan and binding plan occurrence-by-occurrence,
    checks contiguous 0..N-1 slot order, validates scopes, and ensures exact descriptor authority.
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

    # 0. Validate contiguous slots 0..N-1 across all receipt entries (§25)
    for idx, entry in enumerate(batch.ordered_receipt_entries):
        if entry.slot_index != idx:
            raise R2BatchValidationError(
                f"Non-contiguous receipt slot index: expected {idx}, got {entry.slot_index}"
            )

    mid = expected_micro_id

    # 1. Derive expected binding plan directly from descriptor (§21, §25, B05)
    expected_bindings: list[dict[str, Any]] = []

    if micro_descriptor.kind == "simultaneous":
        pos_nodes = [canonical_node_ref(r, s) for r, s in micro_descriptor.signals]
        if len(pos_nodes) >= 2:
            sim_scope = f"r2scope:{mid}:simultaneous:0"
            expected_bindings.append({
                "scope_kind": "simultaneous",
                "scope_index": 0,
                "binding_scope": sim_scope,
                "member_element_refs": tuple(pos_nodes),
            })
    elif micro_descriptor.kind == "sequence":
        for t_idx in range(max(0, len(micro_descriptor.steps) - 1)):
            src_nodes = [canonical_node_ref(r, s) for r, s in micro_descriptor.steps[t_idx]]
            dst_nodes = [canonical_node_ref(r, s) for r, s in micro_descriptor.steps[t_idx + 1]]
            scope = f"r2scope:{mid}:sequence:{t_idx}"
            expected_bindings.append({
                "scope_kind": "sequence",
                "scope_index": t_idx,
                "binding_scope": scope,
                "member_element_refs": tuple(src_nodes + dst_nodes),
            })

    for c_idx, (a, b) in enumerate(micro_descriptor.contradictions):
        scope = f"r2scope:{mid}:contradiction:{c_idx}"
        members = (canonical_contradiction_endpoint_ref(a), canonical_contradiction_endpoint_ref(b))
        expected_bindings.append({
            "scope_kind": "contradiction",
            "scope_index": c_idx,
            "binding_scope": scope,
            "member_element_refs": members,
        })

    if len(batch.ordered_binding_entries) != len(expected_bindings):
        raise R2BatchValidationError(
            f"Binding entry count mismatch: expected {len(expected_bindings)}, got {len(batch.ordered_binding_entries)}"
        )

    # Validate contiguous binding indexes 0..K-1, exact descriptor derivation, and TBRID re-derivation
    for b_idx, (b_entry, exp) in enumerate(zip(batch.ordered_binding_entries, expected_bindings, strict=True)):
        if b_entry.binding_index != b_idx:
            raise R2BatchValidationError(
                f"Non-contiguous binding index: expected {b_idx}, got {b_entry.binding_index}"
            )
        if b_entry.scope_kind != exp["scope_kind"]:
            raise R2BatchValidationError(
                f"TBR scope_kind mismatch at index {b_idx}: '{b_entry.scope_kind}' != '{exp['scope_kind']}'"
            )
        if b_entry.scope_index != exp["scope_index"]:
            raise R2BatchValidationError(
                f"TBR scope_index mismatch at index {b_idx}: {b_entry.scope_index} != {exp['scope_index']}"
            )
        if b_entry.binding_scope != exp["binding_scope"]:
            raise R2BatchValidationError(
                f"TBR binding_scope mismatch at index {b_idx}: '{b_entry.binding_scope}' != '{exp['binding_scope']}'"
            )
        if b_entry.member_element_refs != exp["member_element_refs"]:
            raise R2BatchValidationError(
                f"TBR members mismatch at index {b_idx}: {b_entry.member_element_refs} != {exp['member_element_refs']}"
            )

        recomputed_bid = derive_transient_binding_receipt_id(
            micro_episode_id=mid,
            binding_scope_id=b_entry.binding_scope,
            member_receipt_refs=list(b_entry.member_element_refs),
            binding_index=b_entry.binding_index,
            prefix="tbr_",
        )
        if b_entry.binding_id != recomputed_bid:
            raise R2BatchValidationError(
                f"TBRID re-derivation mismatch: '{b_entry.binding_id}' != '{recomputed_bid}'"
            )

    # 2. Rederive expected receipt plan occurrence-by-occurrence using derive_expected_receipt_plan
    expected_receipts = derive_expected_receipt_plan(
        micro_descriptor=micro_descriptor,
        micro_episode_id=mid,
        current_relation_view=graph,
    )

    if graph is not None:
        if len(batch.ordered_receipt_entries) != len(expected_receipts):
            raise R2BatchValidationError(
                f"Receipt entry count mismatch: expected {len(expected_receipts)}, got {len(batch.ordered_receipt_entries)}"
            )
    else:
        num_node_contra = len(expected_receipts)
        if len(batch.ordered_receipt_entries) < num_node_contra:
            raise R2BatchValidationError(
                f"Receipt entry count mismatch: expected at least {num_node_contra} receipts, got {len(batch.ordered_receipt_entries)}"
            )

    # 3. Compare actual receipt entries slot-by-slot against expected receipt plan
    num_to_compare = len(expected_receipts)
    for idx in range(num_to_compare):
        entry = batch.ordered_receipt_entries[idx]
        exp = expected_receipts[idx]
        if entry.kind != exp.kind:
            raise R2BatchValidationError(
                f"Receipt kind mismatch at slot {idx}: expected '{exp.kind}', got '{entry.kind}'"
            )
        if entry.element_ref != exp.element_ref:
            raise R2BatchValidationError(
                f"Receipt element_ref mismatch at slot {idx}: expected '{exp.element_ref}', got '{entry.element_ref}'"
            )
        if entry.occurrence_scope != exp.occurrence_scope:
            raise R2BatchValidationError(
                f"Receipt occurrence_scope mismatch at slot {idx}: expected '{exp.occurrence_scope}', got '{entry.occurrence_scope}'"
            )
        if entry.scope_refs != exp.scope_refs:
            raise R2BatchValidationError(
                f"Receipt scope_refs mismatch at slot {idx}: expected {exp.scope_refs}, got {entry.scope_refs}"
            )
        if entry.receipt_id != exp.receipt_id:
            raise R2BatchValidationError(
                f"ParticipationReceipt ID re-derivation mismatch at slot {idx}: '{entry.receipt_id}' != '{exp.receipt_id}'"
            )
        if abs(entry.activation_magnitude - exp.activation_magnitude) > 1e-6:
            raise R2BatchValidationError(
                f"Receipt activation_magnitude mismatch at slot {idx}: expected {exp.activation_magnitude}, got {entry.activation_magnitude}"
            )
        if abs(entry.relational_drive - exp.relational_drive) > 1e-6:
            raise R2BatchValidationError(
                f"Receipt relational_drive mismatch at slot {idx}: expected {exp.relational_drive}, got {entry.relational_drive}"
            )

    # If graph is None, validate any remaining edge receipts beyond num_node_contra
    relations = derive_all_observation_relations(micro_descriptor)
    if graph is None:
        rel_set = set(relations)
        for idx in range(num_node_contra, len(batch.ordered_receipt_entries)):
            entry = batch.ordered_receipt_entries[idx]
            if entry.kind != "edge":
                raise R2BatchValidationError(
                    f"Unexpected non-edge receipt at slot {idx}: kind='{entry.kind}'"
                )
            if entry.element_ref not in rel_set:
                raise R2BatchValidationError(
                    f"Edge element_ref {entry.element_ref} at slot {idx} is not in canonical observation relations"
                )
            if not entry.occurrence_scope.startswith(f"r2relation:{mid}:"):
                raise R2BatchValidationError(
                    f"Receipt at slot {idx} has non-canonical occurrence scope '{entry.occurrence_scope}'"
                )
            rel_idx_str = entry.occurrence_scope.split(":")[-1]
            try:
                rel_idx = int(rel_idx_str)
                if rel_idx < 0 or rel_idx >= len(relations) or relations[rel_idx] != entry.element_ref:
                    raise R2BatchValidationError(
                        f"Receipt at slot {idx} has incorrect relation index {rel_idx} for element {entry.element_ref}"
                    )
            except ValueError:
                raise R2BatchValidationError(
                    f"Receipt at slot {idx} has invalid relation index '{rel_idx_str}'"
                )

            if entry.scope_refs != (mid, entry.occurrence_scope):
                raise R2BatchValidationError(
                    f"Receipt at slot {idx} scope_refs must be ({mid}, {entry.occurrence_scope}), got {entry.scope_refs}"
                )
            recomputed_rid = derive_participation_receipt_id(
                micro_episode_id=mid,
                participation_kind="edge",
                element_ref=entry.element_ref,
                scope_refs=list(entry.scope_refs),
                slot_index=idx,
                prefix="pr_",
            )
            if entry.receipt_id != recomputed_rid:
                raise R2BatchValidationError(
                    f"ParticipationReceipt ID re-derivation mismatch at slot {idx}: '{entry.receipt_id}' != '{recomputed_rid}'"
                )

    # 4. Validate TBR member scopes occurrence-by-occurrence without element collapsing (PIR02-B02)
    step_slot_ranges: list[tuple[int, int]] = []
    contra_slot_ranges: list[tuple[int, int]] = []
    slot_cursor = 0
    if micro_descriptor.kind == "simultaneous":
        pass
    else:
        for step in micro_descriptor.steps:
            start_s = slot_cursor
            slot_cursor += len(step)
            step_slot_ranges.append((start_s, slot_cursor))

    c_cursor = len(micro_descriptor.signals) if micro_descriptor.kind == "simultaneous" else slot_cursor
    for _ in micro_descriptor.contradictions:
        c_start = c_cursor
        c_cursor += 2
        contra_slot_ranges.append((c_start, c_cursor))

    for b_entry in batch.ordered_binding_entries:
        if b_entry.scope_kind == "simultaneous":
            for occ_idx in range(len(micro_descriptor.signals)):
                entry = batch.ordered_receipt_entries[occ_idx]
                if b_entry.binding_scope not in entry.scope_refs:
                    raise R2BatchValidationError(
                        f"TBR scope '{b_entry.binding_scope}' missing from occurrence {occ_idx} receipt scope_refs"
                    )
        elif b_entry.scope_kind == "sequence":
            t_idx = b_entry.scope_index
            if t_idx < len(step_slot_ranges) - 1:
                for s_idx in (t_idx, t_idx + 1):
                    start_s, end_s = step_slot_ranges[s_idx]
                    for s_slot in range(start_s, end_s):
                        entry = batch.ordered_receipt_entries[s_slot]
                        if b_entry.binding_scope not in entry.scope_refs:
                            raise R2BatchValidationError(
                                f"TBR scope '{b_entry.binding_scope}' missing from step {s_idx} occurrence slot {s_slot} receipt scope_refs"
                            )
        elif b_entry.scope_kind == "contradiction":
            c_idx = b_entry.scope_index
            if c_idx < len(contra_slot_ranges):
                c_start, c_end = contra_slot_ranges[c_idx]
                for c_slot in range(c_start, c_end):
                    entry = batch.ordered_receipt_entries[c_slot]
                    if b_entry.binding_scope not in entry.scope_refs:
                        raise R2BatchValidationError(
                            f"TBR scope '{b_entry.binding_scope}' missing from contradiction {c_idx} endpoint slot {c_slot} receipt scope_refs"
                        )


# ─────────────────────────────────────────────────────────── 7. Canonical Observation Result (§30, §31, B07)
@dataclass(frozen=True)
class CanonicalMicroEpisodeRecord:
    """Per-MicroEpisode record in CanonicalObservationResult (§30, B07)."""
    descriptor: CanonicalMicroEpisodeDescriptor
    receipt_batch: CanonicalReceiptBatch | None
    selected_assembly_refs: tuple[tuple[str, int], ...]
    representation_id: str | None
    child_index: int
    micro_episode_id: str

    @property
    def kind(self) -> str:
        return self.descriptor.kind

    @property
    def descriptor_version(self) -> str:
        return self.descriptor.descriptor_version

    @property
    def micro_descriptor_version(self) -> str:
        return self.descriptor.descriptor_version

    def to_dict(self) -> dict[str, Any]:
        return self.descriptor.to_dict()


@dataclass
class CanonicalObservationResult:
    """
    Transient observation result object (§30, B07).
    Transient operational state only. Zero persistent cognitive memory.
    """
    result_version: str
    status: str  # TRANSIENT_OBSERVED | PERSISTENT_EXECUTED | PERSISTENT_REPLAY | NO_OBSERVABLE_CONTENT
    mode: ExecutionMode
    root_external_episode_id: str
    ingress_event_id: str
    event_descriptor_digest: str
    observation_transaction_id: str
    persistent_phase: str  # NOT_REQUESTED | COMMITTED | REPLAY
    persistent_transaction_id: str | None
    persistent_executed: bool
    micro_episodes: tuple[CanonicalMicroEpisodeRecord, ...]
    representations: tuple[SparseDistributedCognitiveRepresentation, ...]
    diagnostics: dict[str, Any] = field(default_factory=dict)
    _engine: Any = field(default=None, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

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

    @property
    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self._closed:
            return
        close_result(self, engine=self._engine)
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


def close_result(result: CanonicalObservationResult, *, engine: Any = None) -> None:
    """
    Idempotent result lifecycle cleanup (§31, B07, PIR02-B03).
    Closes every active SDCR created by that result through the owning RepresentationEngine
    without altering persistent cognitive graph state.
    """
    if not isinstance(result, CanonicalObservationResult):
        return
    if result._closed:
        return
    eng = engine if engine is not None else getattr(result, "_engine", None)
    for rep in result.representations:
        if eng is not None and hasattr(eng, "close_representation") and callable(eng.close_representation):
            eng.close_representation(rep)
        elif hasattr(rep, "close") and callable(rep.close):
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

    def _build_micro_descriptors(
        self, episodes: list[SensoryEpisode], txid: str
    ) -> list[CanonicalMicroEpisodeDescriptor]:
        micro_descriptors: list[CanonicalMicroEpisodeDescriptor] = []
        for c_idx, ep in enumerate(episodes):
            signals_tuple = tuple((r, s) for r, s in ep.signals) if ep.kind == "simultaneous" else ()
            contra_tuple = tuple((a, b) for a, b in ep.contradictions)
            steps_tuple = ()
            if ep.kind == "sequence":
                steps_tuple = tuple(tuple((r, s) for r, s in step) for step in ep.steps)

            # Pre-construct and validate exact canonical descriptor (§11, B02)
            desc = CanonicalMicroEpisodeDescriptor(
                descriptor_version=MICRO_DESCRIPTOR_VERSION,
                kind=ep.kind,
                context=ep.context,
                signals=signals_tuple,
                steps=steps_tuple,
                structural_weight=float(ep.structural_weight),
                valence=float(ep.valence),
                contradictions=contra_tuple,
                child_index=c_idx,
            )

            micro_id = derive_micro_episode_id(
                observation_transaction_id=txid,
                child_index=c_idx,
                canonical_episode_descriptor=desc.to_dict(),
                prefix="mep_",
            )

            # Re-bind with derived micro_episode_id
            desc_with_id = CanonicalMicroEpisodeDescriptor(
                descriptor_version=MICRO_DESCRIPTOR_VERSION,
                kind=ep.kind,
                context=ep.context,
                signals=signals_tuple,
                steps=steps_tuple,
                structural_weight=float(ep.structural_weight),
                valence=float(ep.valence),
                contradictions=contra_tuple,
                micro_episode_id=micro_id,
                child_index=c_idx,
            )
            micro_descriptors.append(desc_with_id)
        return micro_descriptors

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

        # Step 1: Pre-validation of occurrence & arguments (D01)
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
        if not isinstance(payload, dict):
            raise R2DescriptorError("payload must be a dictionary")

        # D01: Validate generic raw payload shape exactly before event descriptor construction
        if modality == "text":
            allowed_payload_keys = {"raw_text", "context"}
            unknown_keys = set(payload.keys()) - allowed_payload_keys
            if unknown_keys:
                raise R2DescriptorError(f"Unknown text payload keys: {unknown_keys}")
            raw_text = payload.get("raw_text")
            context = payload.get("context")
            event_desc = build_text_event_descriptor(raw_text, context=context)
        else:
            allowed_payload_keys = {"source_code", "module"}
            unknown_keys = set(payload.keys()) - allowed_payload_keys
            if unknown_keys:
                raise R2DescriptorError(f"Unknown code payload keys: {unknown_keys}")
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

        # Step 5: Authorization Firewall (§13, B04)
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

            # B04: Strict literal boolean check. Truthy non-bools fail closed.
            if type(auth_res) is not bool or auth_res is not True:
                raise R2AuthorizationError(
                    f"Persistent observation denied: authorizer returned non-bool or False: {auth_res!r}"
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
                status="NO_OBSERVABLE_CONTENT",
                mode=mode,
                root_external_episode_id=root_id,
                ingress_event_id=ingress_event_id,
                event_descriptor_digest=event_digest,
                observation_transaction_id=txid,
                persistent_phase="NOT_REQUESTED",
                persistent_transaction_id=None,
                persistent_executed=False,
                micro_episodes=(),
                representations=(),
                diagnostics={"child_count": 0},
                _engine=self._graph.representation_engine,
            )

        # Step 7: MicroEpisode Descriptors & ObservationTransactionID (§11, §20, B02)
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

        micro_descriptors = self._build_micro_descriptors(episodes, txid)

        # D02: Explicit length equality
        if len(episodes) != len(micro_descriptors):
            raise R2DescriptorError("Episode count does not equal micro_descriptor count")

        # Step 8: Persistent Execution (Phase 1, B03)
        persistent_committed = False
        persistent_executed = False
        persistent_phase = "NOT_REQUESTED"
        persistent_txid: str | None = None

        if is_persistent:
            pos_refs: set[str] = set()
            contra_refs: set[str] = set()
            for m_desc in micro_descriptors:
                if m_desc.kind == "simultaneous":
                    for r, s in m_desc.signals:
                        pos_refs.add(canonical_node_ref(r, s))
                else:
                    for step in m_desc.steps:
                        for r, s in step:
                            pos_refs.add(canonical_node_ref(r, s))
                for a, b in m_desc.contradictions:
                    contra_refs.add(canonical_contradiction_endpoint_ref(a))
                    contra_refs.add(canonical_contradiction_endpoint_ref(b))

            canonical_targets = {
                "positive_node_refs": sorted(pos_refs),
                "contradiction_node_refs": sorted(contra_refs),
            }

            canonical_mutation_descriptor = {
                "descriptor_version": MUTATION_DESCRIPTOR_VERSION,
                "observation_protocol_version": R2_OBSERVATION_PROTOCOL_VERSION,
                "microepisodes": [m_desc.to_dict() for m_desc in micro_descriptors],
                "persistent_effect_policy": {
                    "graph_observation": "EXISTING_DGCA_LAWS",
                    "contradictions": "PERSIST_EXPLICIT",
                    "rfc11_evidence": "EXTERNAL_DIRECT_ONLY",
                    "synthetic_event_role_vote": "FORBIDDEN",
                },
            }

            owner_defined_transaction_scope = {
                "scope_kind": "ROOT_EQUIVALENT_ENCODED_OBSERVATION",
                "observation_protocol_version": R2_OBSERVATION_PROTOCOL_VERSION,
            }

            command = PersistentMutationCommand(
                mutation_owner_ref=MUTATION_OWNER_REF,
                mutation_kind=MUTATION_KIND,
                canonical_targets=canonical_targets,
                canonical_mutation_descriptor=canonical_mutation_descriptor,
                owner_defined_transaction_scope=owner_defined_transaction_scope,
            )

            def _mutator_callback() -> None:
                for m_desc, ep in zip(micro_descriptors, episodes, strict=True):
                    for a, b in m_desc.contradictions:
                        self._graph.add_contradiction(a, b)

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

            persistent_txid, executed, _ = self._runtime.execute_persistent_command(
                command=command,
                root_external_episode_id=root_id,
                ingress_event_id=ingress_event_id,
                event_descriptor_digest=event_digest,
                mutator_callback=_mutator_callback,
            )
            persistent_committed = True
            persistent_executed = executed
            persistent_phase = "COMMITTED" if executed else "REPLAY"

        # Step 9: Transient Projection (Phase 2) against current graph (§28, B07)
        created_sdcrs: list[SparseDistributedCognitiveRepresentation] = []
        micro_records: list[CanonicalMicroEpisodeRecord] = []
        current_child_idx = 0

        try:
            for c_idx, (m_desc, ep) in enumerate(zip(micro_descriptors, episodes, strict=True)):
                current_child_idx = c_idx
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
                    expected_micro_id=m_desc.micro_episode_id,  # type: ignore[arg-type]
                    expected_child_index=c_idx,
                    expected_cycle_id=local_parent_cycle_id,
                    micro_descriptor=m_desc,
                    graph=self._graph,
                )

                if not batch.ordered_receipt_entries:
                    micro_records.append(
                        CanonicalMicroEpisodeRecord(
                            descriptor=m_desc,
                            receipt_batch=batch,
                            selected_assembly_refs=(),
                            representation_id=None,
                            child_index=c_idx,
                            micro_episode_id=m_desc.micro_episode_id,  # type: ignore[arg-type]
                        )
                    )
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
                    causal_parent_ref=m_desc.micro_episode_id,  # type: ignore[arg-type]
                    parent_cycle_id=local_parent_cycle_id,
                    snapshot_or_microtick=c_idx,
                    context=ep.context,
                    participation_receipts=participation_receipts,
                    transient_bindings=tbr_receipts,
                    active_assemblies=selected_asms,
                )
                created_sdcrs.append(sdcr)
                micro_records.append(
                    CanonicalMicroEpisodeRecord(
                        descriptor=m_desc,
                        receipt_batch=batch,
                        selected_assembly_refs=tuple(sorted(selected_asms)),
                        representation_id=sdcr.representation_id,
                        child_index=c_idx,
                        micro_episode_id=m_desc.micro_episode_id,  # type: ignore[arg-type]
                    )
                )

        except Exception as e:
            # B07: Proper RFC12 cleanup through RepresentationEngine.close_representation
            rep_engine = self._graph.representation_engine
            for partial_sdcr in created_sdcrs:
                if rep_engine is not None and hasattr(rep_engine, "close_representation"):
                    rep_engine.close_representation(partial_sdcr)
                elif hasattr(partial_sdcr, "close") and callable(partial_sdcr.close):
                    partial_sdcr.close()

            if is_persistent:
                raise R2ProjectionFailure(
                    f"Transient projection failed after persistent decision: {e}",
                    transaction_id=persistent_txid,
                    persistent_executed=persistent_executed,
                    persistent_committed=persistent_committed,
                    failed_child_index=current_child_idx,
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
            status=final_status,
            mode=mode,
            root_external_episode_id=root_id,
            ingress_event_id=ingress_event_id,
            event_descriptor_digest=event_digest,
            observation_transaction_id=txid,
            persistent_phase=persistent_phase,
            persistent_transaction_id=persistent_txid,
            persistent_executed=persistent_executed,
            micro_episodes=tuple(micro_records),
            representations=tuple(created_sdcrs),
            diagnostics={
                "child_count": len(micro_descriptors),
                "representation_count": len(created_sdcrs),
                "persistent_executed": persistent_executed,
            },
            _engine=self._graph.representation_engine,
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
        """
        Derives direct external RFC-11 eligible edges (§16, B06).
        Simultaneous: all ordered non-self pairs.
        Sequence: same-step and adjacent-step (distance 0 or 1) in BOTH temporal directions.
        """
        eligible: list[tuple[str, str]] = []
        if micro_desc.kind == "simultaneous":
            unique_nodes: list[str] = []
            seen: set[str] = set()
            for r, s in micro_desc.signals:
                n = canonical_node_ref(r, s)
                if n not in seen:
                    seen.add(n)
                    unique_nodes.append(n)
            for a in unique_nodes:
                for b in unique_nodes:
                    if a != b and not self._is_excluded_rfc11_edge(a, b):
                        eligible.append((a, b))
        elif micro_desc.kind == "sequence":
            steps = micro_desc.steps
            for p_i, step_i in enumerate(steps):
                nodes_i = [canonical_node_ref(r, s) for r, s in step_i]
                for p_j, step_j in enumerate(steps):
                    # B06: Minimum absolute step distance. Both forward and reverse adjacent steps are eligible.
                    step_distance = abs(p_j - p_i)
                    if step_distance not in (0, 1):
                        continue
                    nodes_j = [canonical_node_ref(r, s) for r, s in step_j]
                    for u in nodes_i:
                        for v in nodes_j:
                            if u != v and (u, v) not in eligible and not self._is_excluded_rfc11_edge(u, v):
                                eligible.append((u, v))
        return eligible

    def _is_excluded_rfc11_edge(self, u: str, v: str) -> bool:
        """Filters out non-direct external synthetic/category/concept edges (§16)."""
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
        """
        Constructs exact transient receipt batch envelope (§22, §23, §24, B05).
        Enforces occurrence-indexed scopes, preserves duplicate occurrences in TBR members,
        and uses exact canonical relation-list indices for edge receipts.
        """
        receipt_entries: list[CanonicalReceiptEntry] = []
        binding_entries: list[CanonicalBindingEntry] = []
        current_slot = 0
        current_binding_idx = 0
        mid = micro_desc.micro_episode_id
        assert mid is not None

        # 1. Derive Binding Entries (TBRs) (§23, B05)
        sim_scope: str | None = None
        if micro_desc.kind == "simultaneous":
            # Preserve duplicate occurrences in occurrence order (§23, B05)
            sim_members = [canonical_node_ref(r, s) for r, s in micro_desc.signals]
            if len(sim_members) >= 2:
                sim_scope = f"r2scope:{mid}:simultaneous:0"
                bid = derive_transient_binding_receipt_id(
                    micro_episode_id=mid,
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

        seq_scopes_by_transition: list[str] = []
        if micro_desc.kind == "sequence":
            for t_idx in range(max(0, len(micro_desc.steps) - 1)):
                src_members = [canonical_node_ref(r, s) for r, s in micro_desc.steps[t_idx]]
                dst_members = [canonical_node_ref(r, s) for r, s in micro_desc.steps[t_idx + 1]]
                members = src_members + dst_members
                t_scope = f"r2scope:{mid}:sequence:{t_idx}"
                bid = derive_transient_binding_receipt_id(
                    micro_episode_id=mid,
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
                seq_scopes_by_transition.append(t_scope)

        contra_scopes: list[str] = []
        for c_idx, (a, b) in enumerate(micro_desc.contradictions):
            ep_a = canonical_contradiction_endpoint_ref(a)
            ep_b = canonical_contradiction_endpoint_ref(b)
            c_members = [ep_a, ep_b]
            c_scope = f"r2scope:{mid}:contradiction:{c_idx}"
            bid = derive_transient_binding_receipt_id(
                micro_episode_id=mid,
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
            contra_scopes.append(c_scope)

        # 2. Derive Node Receipts (Global Slot Order 1: positive node occurrences) (§22, B05)
        if micro_desc.kind == "simultaneous":
            for occ_idx, (r, s) in enumerate(micro_desc.signals):
                n = canonical_node_ref(r, s)
                occ_scope = f"r2occ:{mid}:simultaneous:{occ_idx}"
                scopes = [mid, occ_scope]
                if sim_scope is not None:
                    scopes.append(sim_scope)
                rid = derive_participation_receipt_id(
                    micro_episode_id=mid,
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
            for step_idx, step in enumerate(micro_desc.steps):
                for step_occ_idx, (r, s) in enumerate(step):
                    n = canonical_node_ref(r, s)
                    occ_scope = f"r2occ:{mid}:step:{step_idx}:{step_occ_idx}"
                    scopes = [mid, occ_scope]
                    # Occurrence-indexed binding scope assignment (§22, B05)
                    if step_idx > 0 and (step_idx - 1) < len(seq_scopes_by_transition):
                        scopes.append(seq_scopes_by_transition[step_idx - 1])
                    if step_idx < len(seq_scopes_by_transition):
                        scopes.append(seq_scopes_by_transition[step_idx])
                    rid = derive_participation_receipt_id(
                        micro_episode_id=mid,
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

        # 3. Derive Contradiction Endpoint Receipts (Global Slot Order 2) (§22, B05)
        for c_idx, (a, b) in enumerate(micro_desc.contradictions):
            c_scope = contra_scopes[c_idx]
            for ep_idx, ep_raw in enumerate([a, b]):
                ep_ref = canonical_contradiction_endpoint_ref(ep_raw)
                occ_scope = f"r2occ:{mid}:contradiction:{c_idx}:{ep_idx}"
                scopes = [mid, occ_scope, c_scope]
                rid = derive_participation_receipt_id(
                    micro_episode_id=mid,
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

        # 4. Derive Edge Receipts (Global Slot Order 3: live gate-open edges) (§22, B05)
        relations = self._derive_all_observation_relations(micro_desc)
        for rel_idx, (src, dst) in enumerate(relations):
            edge_obj = self._graph.edge(src, dst)
            if edge_obj is not None and edge_obj.gate_open(ep.context):
                occ_scope = f"r2relation:{mid}:{rel_idx}"
                scopes = [mid, occ_scope]
                rid = derive_participation_receipt_id(
                    micro_episode_id=mid,
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

        return CanonicalReceiptBatch(
            batch_version=RECEIPT_BATCH_VERSION,
            observation_transaction_id=txid,
            micro_episode_id=mid,
            child_index=child_index,
            local_parent_cycle_id=local_parent_cycle_id,
            snapshot_or_microtick=child_index,
            ordered_receipt_entries=receipt_entries,
            ordered_binding_entries=binding_entries,
        )

    def _derive_all_observation_relations(
        self, micro_desc: CanonicalMicroEpisodeDescriptor
    ) -> list[tuple[str, str]]:
        return derive_all_observation_relations(micro_desc)
