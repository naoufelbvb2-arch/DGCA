"""
DGCA — RIC-01 / R1: Deterministic Causal Identity Protocol
Formal Architecture Specification v1.3 — FROZEN

Constitutional Separation:
SemanticIdentity != CausalOccurrenceIdentity != PersistentMutationTransactionIdentity != ContentSignature != LocalEphemeralHandle
DeterministicIdentity does not imply PersistentCognition.
"""
from __future__ import annotations

import enum
import hashlib
import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# ─────────────────────────────────────────────────────────── 1. Protocol Constants & Registry
PROTOCOL_VERSION: str = "1.0"
PROTOCOL_PREFIX: str = "DGCA:R1:ID:v1"
AUTHORITATIVE_DIGEST_HEX_CHARS: int = 64

LITERAL_DOMAIN_REGISTRY: tuple[str, ...] = (
    "CAUSAL_PROVENANCE_EPOCH",
    "CONTINUATION_COMMIT",
    "DELIVERY",
    "EXPRESSION_RECEIPT",
    "GCE",
    "GENERATIVE_FRAME",
    "INGRESS_EVENT",
    "INTERNAL_WORK",
    "LINEARIZABLE_OCCURRENCE",
    "MICRO_EPISODE",
    "OBSERVATION_TRANSACTION",
    "PARTICIPATION_RECEIPT",
    "PATTERN_CANDIDATE",
    "PERSISTENT_MUTATION",
    "REINSTATEMENT_PROPOSAL",
    "REPRESENTATION",
    "ROOT_EXTERNAL_EPISODE",
    "SETTLING_EPOCH",
    "SURFACE_CHUNK",
    "SURFACE_UNIT",
    "TRANSIENT_BINDING",
)

CANONICALIZATION_PROFILE: dict[str, str] = {
    "mappings": "recursive-json-object",
    "sets_frozensets": "canonical-sorted-list",
    "unordered_edge_sets": "canonical-sorted-[src,dst]-list",
    "ordered_list_tuple": "preserve-order",
    "strings": "exact-unicode-codepoint-sequence-no-implicit-normalization",
    "none": "json-null",
    "floats": "finite-json-number-only",
}

CANONICAL_R1_IDENTITY_MODE: str = "CANONICAL_R1"
LEGACY_NON_CANONICAL_IDENTITY_MODE: str = "LEGACY_NON_CANONICAL"


# ─────────────────────────────────────────────────────────── 2. Exceptions
class CausalIdentityError(Exception):
    """Base exception for all causal identity and provenance failures."""


class CausalIdentityValidationError(CausalIdentityError):
    """Raised when an identity payload, descriptor, or argument fails validation."""


class CausalDomainError(CausalIdentityError):
    """Raised when an invalid or unverified identity domain is accessed."""


class CausalLineageError(CausalIdentityError):
    """Raised when causal parentage, lineage, or event binding violates causal protocol rules."""


class CausalCommitCollisionError(CausalIdentityError):
    """Raised when a TxID or EventID collides with conflicting descriptors."""


class CausalProtocolMismatchError(CausalIdentityError):
    """Raised when identity protocol or observation protocol version/digest mismatches."""


class CausalRuntimeFailStopError(CausalIdentityError):
    """Raised when attempting an operation on a runtime in MUTATION_FAILED fail-stop state."""


class CausalLineageInvalidatedError(CausalIdentityError):
    """Raised when attempting canonical save or persistent command on an invalidated lineage runtime."""


# ─────────────────────────────────────────────────────────── 3. Canonicalization & Hash Primitive
def canonicalize_payload(obj: Any) -> Any:
    """Recursively converts a payload into its deterministic canonical representation."""
    if obj is None or isinstance(obj, (bool, int, str)):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise CausalIdentityValidationError(f"Non-finite float {obj} rejected in canonical payload")
        return obj
    if isinstance(obj, enum.Enum):
        return canonicalize_payload(obj.value)
    if isinstance(obj, (set, frozenset)):
        canonical_members = [canonicalize_payload(item) for item in obj]
        dumped_members = [
            json.dumps(m, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
            for m in canonical_members
        ]
        dumped_members.sort(key=lambda s: s.encode("utf-8"))
        return [json.loads(s) for s in dumped_members]
    if isinstance(obj, (list, tuple)):
        return [canonicalize_payload(item) for item in obj]
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if not isinstance(k, str):
                raise CausalIdentityValidationError(
                    f"Mapping keys in authoritative R1 payload must be strings, got {type(k).__name__}: {k}"
                )
            if k in result:
                raise CausalIdentityValidationError(f"Duplicate mapping key collision detected: {k}")
            result[k] = canonicalize_payload(v)
        return result
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return canonicalize_payload(obj.to_dict())
    raise CausalIdentityValidationError(f"Unsupported type for canonical payload: {type(obj)}")


def canonical_json_str(payload: Any) -> str:
    """Serialize a payload to a canonical JSON string."""
    canonical = canonicalize_payload(payload)
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize a payload to canonical UTF-8 JSON bytes."""
    return canonical_json_str(payload).encode("utf-8")


def dgca_id(domain: str, payload: Any, prefix: str = "") -> str:
    """Authoritative DGCA R1 canonical identity derivation:

    DGCA_ID(domain, payload) = SHA256(UTF8('DGCA:R1:ID:v1') || 0x00 || UTF8(domain) || 0x00 || UTF8(canonical_json))
    """
    if domain not in LITERAL_DOMAIN_REGISTRY:
        raise CausalDomainError(f"Domain '{domain}' is not in LITERAL_DOMAIN_REGISTRY")
    payload_bytes = canonical_json_bytes(payload)
    hasher = hashlib.sha256()
    hasher.update(PROTOCOL_PREFIX.encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(domain.encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(payload_bytes)
    digest = hasher.hexdigest()
    if len(digest) != AUTHORITATIVE_DIGEST_HEX_CHARS:
        raise CausalIdentityError(f"Digest length mismatch: expected {AUTHORITATIVE_DIGEST_HEX_CHARS}, got {len(digest)}")
    return f"{prefix}{digest}"


def compute_causal_identity_protocol_digest() -> str:
    """Computes the exact frozen causal identity protocol digest (Section 70)."""
    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "protocol_prefix": PROTOCOL_PREFIX,
        "hash_algorithm": "SHA-256",
        "authoritative_digest_hex_chars": AUTHORITATIVE_DIGEST_HEX_CHARS,
        "canonical_json": {
            "sort_keys": True,
            "separators": [",", ":"],
            "ensure_ascii": False,
            "allow_nan": False,
        },
        "domain_registry": list(LITERAL_DOMAIN_REGISTRY),
        "canonicalization_profile": CANONICALIZATION_PROFILE,
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


CAUSAL_IDENTITY_PROTOCOL_DIGEST: str = compute_causal_identity_protocol_digest()


def compute_observation_protocol_digest(observation_protocol_version: str) -> str:
    """Computes the exact observation protocol digest (Section 71)."""
    if not isinstance(observation_protocol_version, str) or not observation_protocol_version.strip():
        raise CausalIdentityValidationError("observation_protocol_version must be a non-empty string")
    payload = {
        "observation_protocol_version": observation_protocol_version,
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def compute_event_descriptor_digest(canonical_event_descriptor: Any) -> str:
    """Computes the exact event descriptor digest (Section 13)."""
    return hashlib.sha256(canonical_json_bytes(canonical_event_descriptor)).hexdigest()


def compute_mutation_descriptor_digest(canonical_mutation_descriptor: Any) -> str:
    """Computes the exact mutation descriptor digest (Section 43)."""
    return hashlib.sha256(canonical_json_bytes(canonical_mutation_descriptor)).hexdigest()


def compute_causal_provenance_digest(causal_provenance_state: Any) -> str:
    """Computes the exact causal provenance digest (Section 63)."""
    return hashlib.sha256(canonical_json_bytes(causal_provenance_state)).hexdigest()


def compute_checkpoint_bundle_digest(
    checkpoint_state_digest: str,
    causal_provenance_digest: str,
    combined_semantics_digest: str,
    causal_identity_protocol_digest: str,
    observation_protocol_digest: str,
    causal_provenance_epoch: Any,
) -> str:
    """Computes the structured checkpoint bundle digest (Section 64, R1-A07)."""
    bundle_payload = {
        "checkpoint_state_digest": checkpoint_state_digest,
        "causal_provenance_digest": causal_provenance_digest,
        "combined_semantics_digest": combined_semantics_digest,
        "causal_identity_protocol_digest": causal_identity_protocol_digest,
        "observation_protocol_digest": observation_protocol_digest,
        "causal_provenance_epoch": causal_provenance_epoch,
    }
    return hashlib.sha256(canonical_json_bytes(bundle_payload)).hexdigest()


# ─────────────────────────────────────────────────────────── 4. External Occurrence & Ingress Descriptors
@dataclass(frozen=True)
class ExternalOccurrenceDescriptor:
    """Host-supplied trusted occurrence descriptor (Section 5)."""
    boundary_namespace: str
    source_occurrence_key: str

    def __post_init__(self) -> None:
        if not isinstance(self.boundary_namespace, str) or not self.boundary_namespace.strip():
            raise CausalIdentityValidationError("boundary_namespace must be a non-empty string")
        if not isinstance(self.source_occurrence_key, str) or not self.source_occurrence_key.strip():
            raise CausalIdentityValidationError("source_occurrence_key must be a non-empty string")

    def to_dict(self) -> dict[str, str]:
        return {
            "boundary_namespace": self.boundary_namespace,
            "source_occurrence_key": self.source_occurrence_key,
        }


def derive_root_external_episode_id(
    boundary_namespace: str,
    source_occurrence_key: str,
    prefix: str = "",
) -> str:
    """Derives canonical RootExternalEpisodeID from trusted host occurrence descriptor."""
    desc = ExternalOccurrenceDescriptor(boundary_namespace, source_occurrence_key)
    return dgca_id("ROOT_EXTERNAL_EPISODE", desc.to_dict(), prefix=prefix)


@dataclass(frozen=True)
class IngressEventDescriptor:
    """Immutable ingress sub-event descriptor (Section 12)."""
    root_external_episode_id: str
    source_event_key: str
    modality: str
    ingress_boundary: str

    def __post_init__(self) -> None:
        if not isinstance(self.root_external_episode_id, str) or not self.root_external_episode_id.strip():
            raise CausalIdentityValidationError("root_external_episode_id must be a non-empty string")
        if not isinstance(self.source_event_key, str) or not self.source_event_key.strip():
            raise CausalIdentityValidationError("source_event_key must be a non-empty string")
        if not isinstance(self.modality, str) or not self.modality.strip():
            raise CausalIdentityValidationError("modality must be a non-empty string")
        if not isinstance(self.ingress_boundary, str) or not self.ingress_boundary.strip():
            raise CausalIdentityValidationError("ingress_boundary must be a non-empty string")

    def to_dict(self) -> dict[str, str]:
        return {
            "root_external_episode_id": self.root_external_episode_id,
            "source_event_key": self.source_event_key,
            "modality": self.modality,
            "ingress_boundary": self.ingress_boundary,
        }


def derive_ingress_event_id(
    root_external_episode_id: str,
    source_event_key: str,
    modality: str,
    ingress_boundary: str,
    prefix: str = "",
) -> str:
    """Derives canonical IngressEventID (Section 12)."""
    desc = IngressEventDescriptor(
        root_external_episode_id=root_external_episode_id,
        source_event_key=source_event_key,
        modality=modality,
        ingress_boundary=ingress_boundary,
    )
    return dgca_id("INGRESS_EVENT", desc.to_dict(), prefix=prefix)


# ─────────────────────────────────────────────────────────── 5. Operational & Child Identity Derivations
def derive_observation_transaction_id(
    root_external_episode_id: str,
    ingress_event_id: str,
    operation_kind: str,
    observation_protocol_version: str,
    prefix: str = "",
) -> str:
    """Derives canonical ObservationTransactionID (Section 15)."""
    if not observation_protocol_version or not observation_protocol_version.strip():
        raise CausalIdentityValidationError("observation_protocol_version must be non-empty")
    payload = {
        "root_external_episode_id": root_external_episode_id,
        "ingress_event_id": ingress_event_id,
        "operation_kind": operation_kind,
        "observation_protocol_version": observation_protocol_version,
    }
    return dgca_id("OBSERVATION_TRANSACTION", payload, prefix=prefix)


def derive_micro_episode_id(
    observation_transaction_id: str,
    child_index: int,
    canonical_episode_descriptor: Any,
    prefix: str = "",
) -> str:
    """Derives canonical MicroEpisodeID (Section 16)."""
    payload = {
        "observation_transaction_id": observation_transaction_id,
        "child_index": child_index,
        "canonical_episode_descriptor": canonical_episode_descriptor,
    }
    return dgca_id("MICRO_EPISODE", payload, prefix=prefix)


def derive_participation_receipt_id(
    micro_episode_id: str,
    participation_kind: str,
    element_ref: str | tuple[str, str],
    scope_refs: tuple[str, ...] | list[str],
    slot_index: int,
    prefix: str = "",
) -> str:
    """Derives canonical ParticipationReceiptID (Section 18)."""
    payload = {
        "micro_episode_id": micro_episode_id,
        "participation_kind": participation_kind,
        "element_ref": element_ref,
        "scope_refs": scope_refs,
        "slot_index": slot_index,
    }
    return dgca_id("PARTICIPATION_RECEIPT", payload, prefix=prefix)


def derive_transient_binding_receipt_id(
    micro_episode_id: str,
    binding_scope_id: str,
    member_receipt_refs: tuple[Any, ...] | list[Any],
    binding_index: int,
    prefix: str = "",
) -> str:
    """Derives canonical TransientBindingReceiptID / TBRID (Section 19)."""
    payload = {
        "micro_episode_id": micro_episode_id,
        "binding_scope_id": binding_scope_id,
        "member_receipt_refs": member_receipt_refs,
        "binding_index": binding_index,
    }
    return dgca_id("TRANSIENT_BINDING", payload, prefix=prefix)


def derive_operational_representation_digest(
    context_binding: Any,
    active_assembly_refs: Any,
    canonical_accepted_receipt_descriptors: Any,
    canonical_accepted_tbr_descriptors: Any,
    participating_refs: Any,
    snapshot_coordinate: Any,
    support_or_activation_values: Any,
) -> str:
    """Derives deterministic OperationalRepresentationDigest (Section 21)."""
    payload = {
        "context_binding": context_binding,
        "active_assembly_refs": active_assembly_refs,
        "canonical_accepted_receipt_descriptors": canonical_accepted_receipt_descriptors,
        "canonical_accepted_tbr_descriptors": canonical_accepted_tbr_descriptors,
        "participating_refs": participating_refs,
        "snapshot_coordinate": snapshot_coordinate,
        "support_or_activation_values": support_or_activation_values,
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def derive_representation_id(
    causal_parent_ref: str,
    snapshot_or_microtick: int,
    operational_representation_digest: str,
    prefix: str = "",
) -> str:
    """Derives canonical RepresentationID / RID (Section 22)."""
    if not isinstance(causal_parent_ref, str) or not causal_parent_ref.strip():
        raise CausalLineageError("causal_parent_ref is mandatory on canonical path")
    payload = {
        "causal_parent_ref": causal_parent_ref,
        "snapshot_or_microtick": snapshot_or_microtick,
        "operational_representation_digest": operational_representation_digest,
    }
    return dgca_id("REPRESENTATION", payload, prefix=prefix)


def derive_pattern_candidate_id(
    parent_representation_id: str,
    candidate_kind: str,
    seed_refs: Any,
    structural_refs: Any,
    assembly_refs: Any,
    scope_view: Any,
    context_ref: Any,
    prefix: str = "",
) -> str:
    """Derives canonical PatternCandidateID (Section 25)."""
    payload = {
        "parent_representation_id": parent_representation_id,
        "candidate_kind": candidate_kind,
        "seed_refs": seed_refs,
        "structural_refs": structural_refs,
        "assembly_refs": assembly_refs,
        "scope_view": scope_view,
        "context_ref": context_ref,
    }
    return dgca_id("PATTERN_CANDIDATE", payload, prefix=prefix)


def derive_reinstatement_proposal_id(
    settling_epoch_id: str | None,
    parent_representation_id: str,
    candidate_id: str,
    target_ref: str,
    scope_view: Any,
    role_ref: Any,
    prefix: str = "",
) -> str:
    """Derives canonical ReinstatementProposalID (Section 26)."""
    payload = {
        "settling_epoch_id": settling_epoch_id,
        "parent_representation_id": parent_representation_id,
        "candidate_id": candidate_id,
        "target_ref": target_ref,
        "scope_view": scope_view,
        "role_ref": role_ref,
    }
    return dgca_id("REINSTATEMENT_PROPOSAL", payload, prefix=prefix)


def derive_settling_epoch_id(
    root_representation_id: str,
    root_causal_authority_ref: str,
    memory_snapshot_ref: Any,
    work_ref: Any,
    prefix: str = "",
) -> str:
    """Derives canonical SettlingEpochID (Section 27)."""
    payload = {
        "root_representation_id": root_representation_id,
        "root_causal_authority_ref": root_causal_authority_ref,
        "memory_snapshot_ref": memory_snapshot_ref,
        "work_ref": work_ref,
    }
    return dgca_id("SETTLING_EPOCH", payload, prefix=prefix)


def derive_generative_frame_id(
    parent_representation_id: str,
    anchors: Any,
    scope: Any,
    role_bindings: Any,
    prefix: str = "",
) -> str:
    """Derives canonical GenerativeFrameID (Section 28)."""
    payload = {
        "parent_representation_id": parent_representation_id,
        "anchors": anchors,
        "scope": scope,
        "role_bindings": role_bindings,
    }
    return dgca_id("GENERATIVE_FRAME", payload, prefix=prefix)


def derive_linearizable_occurrence_id(
    frame_id: str,
    role_authority_ref: str,
    filler_ref: Any,
    occurrence_kind: str,
    occurrence_index: int = 0,
    prefix: str = "",
) -> str:
    """Derives canonical LinearizableOccurrenceID (Section 29)."""
    payload = {
        "frame_id": frame_id,
        "role_authority_ref": role_authority_ref,
        "filler_ref": filler_ref,
        "occurrence_kind": occurrence_kind,
        "occurrence_index": occurrence_index,
    }
    return dgca_id("LINEARIZABLE_OCCURRENCE", payload, prefix=prefix)


def derive_surface_unit_id(
    parent_representation_id: str,
    source_occurrence_ref: str,
    unit_index: int,
    surface_form: str,
    prefix: str = "",
) -> str:
    """Derives canonical SurfaceUnitID using full parent representation ID (Section 30)."""
    payload = {
        "parent_representation_id": parent_representation_id,
        "source_occurrence_ref": source_occurrence_ref,
        "unit_index": unit_index,
        "surface_form": surface_form,
    }
    return dgca_id("SURFACE_UNIT", payload, prefix=prefix)


def derive_surface_chunk_id(
    parent_representation_id: str,
    ordered_surface_unit_ids: list[str] | tuple[str, ...],
    rendered_text: str,
    closure_reason: str,
    origin_lineage: str = "generation",
    prefix: str = "",
) -> str:
    """Derives canonical SurfaceChunkID (Section 31)."""
    payload = {
        "parent_representation_id": parent_representation_id,
        "ordered_surface_unit_ids": ordered_surface_unit_ids,
        "rendered_text": rendered_text,
        "closure_reason": closure_reason,
        "origin_lineage": origin_lineage,
    }
    return dgca_id("SURFACE_CHUNK", payload, prefix=prefix)


def derive_gce_id(
    root_authority_ref: str,
    work_ref: Any,
    continuation_event_ref: Any = None,
    prefix: str = "",
) -> str:
    """Derives canonical GCE ID independent of global epoch count (Section 32)."""
    payload = {
        "root_authority_ref": root_authority_ref,
        "work_ref": work_ref,
        "continuation_event_ref": continuation_event_ref,
    }
    return dgca_id("GCE", payload, prefix=prefix)


def derive_expressive_obligation_id(
    root_authority_ref: str,
    semantic_element_ref: str,
    role_scope: str,
    alternative_branch_id: str | None = None,
    prefix: str = "",
) -> str:
    """Derives canonical ExpressiveObligationID (Section 33)."""
    payload = {
        "root_authority_ref": root_authority_ref,
        "semantic_element_ref": semantic_element_ref,
        "role_scope": role_scope,
        "alternative_branch_id": alternative_branch_id,
    }
    hasher = hashlib.sha256()
    hasher.update(PROTOCOL_PREFIX.encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(b"EXPRESSIVE_OBLIGATION\0")
    hasher.update(canonical_json_bytes(payload))
    return f"{prefix}{hasher.hexdigest()}"



def derive_continuation_commit_id(
    epoch_id: str,
    parent_representation_id: str,
    obligation_id: str,
    progress_snapshot_digest: str,
    prefix: str = "",
) -> str:
    """Derives canonical ContinuationCommitID (Section 34)."""
    payload = {
        "epoch_id": epoch_id,
        "parent_representation_id": parent_representation_id,
        "obligation_id": obligation_id,
        "progress_snapshot_digest": progress_snapshot_digest,
    }
    return dgca_id("CONTINUATION_COMMIT", payload, prefix=prefix)


def derive_expression_receipt_id(
    root_authority_ref: str,
    parent_representation_id: str,
    chunk_id: str,
    source_occurrence_ref: str,
    expressed_elements: Any,
    prefix: str = "",
) -> str:
    """Derives canonical ExpressionReceiptID (Section 35)."""
    payload = {
        "root_authority_ref": root_authority_ref,
        "parent_representation_id": parent_representation_id,
        "chunk_id": chunk_id,
        "source_occurrence_ref": source_occurrence_ref,
        "expressed_elements": expressed_elements,
    }
    return dgca_id("EXPRESSION_RECEIPT", payload, prefix=prefix)


def derive_internal_work_id(
    root_authority_ref: str,
    subsystem_kind: str,
    scope_refs: Any,
    prerequisite_work_ids: Any,
    work_index_or_role: Any,
    prefix: str = "",
) -> str:
    """Derives canonical InternalWorkID (Section 36)."""
    payload = {
        "root_authority_ref": root_authority_ref,
        "subsystem_kind": subsystem_kind,
        "scope_refs": scope_refs,
        "prerequisite_work_ids": prerequisite_work_ids,
        "work_index_or_role": work_index_or_role,
    }
    return dgca_id("INTERNAL_WORK", payload, prefix=prefix)


def derive_delivery_id(
    surface_chunk_id: str,
    parent_representation_id: str,
    delivery_channel_ref: str | None = None,
    prefix: str = "",
) -> str:
    """Derives canonical DeliveryID (Section 37)."""
    payload = {
        "surface_chunk_id": surface_chunk_id,
        "parent_representation_id": parent_representation_id,
        "delivery_channel_ref": delivery_channel_ref,
    }
    return dgca_id("DELIVERY", payload, prefix=prefix)


def derive_causal_provenance_epoch_id(
    base_state_digest: str,
    source_schema: str,
    causal_identity_protocol_version: str = "1.0",
    prefix: str = "",
) -> str:
    """Derives deterministic CausalProvenanceEpoch ID (Section 59)."""
    payload = {
        "base_state_digest": base_state_digest,
        "source_schema": source_schema,
        "causal_identity_protocol_version": causal_identity_protocol_version,
    }
    return dgca_id("CAUSAL_PROVENANCE_EPOCH", payload, prefix=prefix)


# ─────────────────────────────────────────────────────────── 6. Persistent Mutation & Causal Commit Ledger
@dataclass(frozen=True)
class PersistentMutationCommand:
    """Wrapper for one already-authorized persistent mutation command (Section 40)."""
    mutation_owner_ref: str
    mutation_kind: str
    canonical_targets: Any
    canonical_mutation_descriptor: Any
    owner_defined_transaction_scope: Any

    def __post_init__(self) -> None:
        if not isinstance(self.mutation_owner_ref, str) or not self.mutation_owner_ref.strip():
            raise CausalIdentityValidationError("mutation_owner_ref must be a non-empty string")
        if not isinstance(self.mutation_kind, str) or not self.mutation_kind.strip():
            raise CausalIdentityValidationError("mutation_kind must be a non-empty string")


def derive_persistent_mutation_txid(
    root_external_episode_id: str,
    command: PersistentMutationCommand,
    prefix: str = "",
) -> str:
    """Derives root-scoped PersistentMutationTransactionID (Section 41, R1-A01)."""
    if not isinstance(root_external_episode_id, str) or not root_external_episode_id.strip():
        raise CausalIdentityValidationError("root_external_episode_id must be a non-empty string")
    payload = {
        "root_external_episode_id": root_external_episode_id,
        "mutation_owner_ref": command.mutation_owner_ref,
        "mutation_kind": command.mutation_kind,
        "canonical_targets": command.canonical_targets,
        "canonical_mutation_descriptor": command.canonical_mutation_descriptor,
        "owner_defined_transaction_scope": command.owner_defined_transaction_scope,
    }
    return dgca_id("PERSISTENT_MUTATION", payload, prefix=prefix)


@dataclass(frozen=True)
class EventBindingRecord:
    """Durable binding of an ingress event that produced persistent mutation (Section 47)."""
    ingress_event_id: str
    root_external_episode_id: str
    event_descriptor_digest: str
    observation_protocol_version: str

    def to_dict(self) -> dict[str, str]:
        return {
            "ingress_event_id": self.ingress_event_id,
            "root_external_episode_id": self.root_external_episode_id,
            "event_descriptor_digest": self.event_descriptor_digest,
            "observation_protocol_version": self.observation_protocol_version,
        }


@dataclass(frozen=True)
class CausalCommitRecord:
    """Durable record of a successfully committed persistent mutation (Section 48)."""
    transaction_id: str
    root_external_episode_id: str
    ingress_event_id: str
    event_descriptor_digest: str
    mutation_owner_ref: str
    mutation_kind: str
    mutation_descriptor_digest: str
    owner_defined_transaction_scope: Any
    observation_protocol_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "root_external_episode_id": self.root_external_episode_id,
            "ingress_event_id": self.ingress_event_id,
            "event_descriptor_digest": self.event_descriptor_digest,
            "mutation_owner_ref": self.mutation_owner_ref,
            "mutation_kind": self.mutation_kind,
            "mutation_descriptor_digest": self.mutation_descriptor_digest,
            "owner_defined_transaction_scope": self.owner_defined_transaction_scope,
            "observation_protocol_version": self.observation_protocol_version,
        }


@dataclass(frozen=True)
class CausalProvenanceEpoch:
    """Durable causal provenance epoch coverage metadata (Section 58)."""
    epoch_id: str
    history_status: str  # R1_TRACKED or PRE_R1_HISTORY_UNAVAILABLE
    base_state_digest: str

    def __post_init__(self) -> None:
        if self.history_status not in ("R1_TRACKED", "PRE_R1_HISTORY_UNAVAILABLE"):
            raise CausalIdentityValidationError(f"Unknown history_status '{self.history_status}'")

    def to_dict(self) -> dict[str, str]:
        return {
            "epoch_id": self.epoch_id,
            "history_status": self.history_status,
            "base_state_digest": self.base_state_digest,
        }


class CausalRuntimeHealth(enum.Enum):
    """Transient non-cognitive runtime health state (Section 52)."""
    HEALTHY = "HEALTHY"
    MUTATION_FAILED = "MUTATION_FAILED"


class CanonicalLineageState(enum.Enum):
    """Transient non-cognitive lineage validity state (Section 55)."""
    VALID = "VALID"
    INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION = "INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION"


class CausalCommitLedger:
    """Durable causal provenance ledger owning replay/idempotency tracking (Section 45)."""

    def __init__(
        self,
        epoch: CausalProvenanceEpoch,
        committed_transactions: dict[str, CausalCommitRecord] | None = None,
        committed_event_bindings: dict[str, EventBindingRecord] | None = None,
    ) -> None:
        self.epoch = epoch
        self.committed_transactions: dict[str, CausalCommitRecord] = (
            dict(committed_transactions) if committed_transactions else {}
        )
        self.committed_event_bindings: dict[str, EventBindingRecord] = (
            dict(committed_event_bindings) if committed_event_bindings else {}
        )

    def validate_or_stage_event_binding(
        self,
        ingress_event_id: str,
        root_external_episode_id: str,
        event_descriptor_digest: str,
        observation_protocol_version: str,
    ) -> EventBindingRecord:
        """Validates replay compatibility or stages new binding (Section 47, 72)."""
        if ingress_event_id in self.committed_event_bindings:
            existing = self.committed_event_bindings[ingress_event_id]
            if (
                existing.event_descriptor_digest != event_descriptor_digest
                or existing.root_external_episode_id != root_external_episode_id
                or existing.observation_protocol_version != observation_protocol_version
            ):
                raise CausalCommitCollisionError(
                    f"Conflicting reuse of IngressEventID '{ingress_event_id}' with different descriptor or provenance"
                )
            return existing

        return EventBindingRecord(
            ingress_event_id=ingress_event_id,
            root_external_episode_id=root_external_episode_id,
            event_descriptor_digest=event_descriptor_digest,
            observation_protocol_version=observation_protocol_version,
        )

    def has_transaction(self, transaction_id: str) -> bool:
        """Check if transaction is committed."""
        return transaction_id in self.committed_transactions

    def check_transaction_replay(
        self,
        transaction_id: str,
        mutation_descriptor_digest: str,
        root_external_episode_id: str,
    ) -> bool:
        """Validates transaction replay compatibility (Section 49)."""
        if transaction_id not in self.committed_transactions:
            return False
        existing = self.committed_transactions[transaction_id]
        if (
            existing.mutation_descriptor_digest != mutation_descriptor_digest
            or existing.root_external_episode_id != root_external_episode_id
        ):
            raise CausalCommitCollisionError(
                f"TxID collision '{transaction_id}' with conflicting descriptor or root provenance"
            )
        return True

    def commit_transaction(
        self,
        record: CausalCommitRecord,
        binding: EventBindingRecord | None = None,
    ) -> None:
        """Commits a transaction and its staged binding atomically (Section 48, 50)."""
        if record.transaction_id in self.committed_transactions:
            self.check_transaction_replay(
                record.transaction_id,
                record.mutation_descriptor_digest,
                record.root_external_episode_id,
            )
            return

        if binding:
            if binding.ingress_event_id in self.committed_event_bindings:
                existing_b = self.committed_event_bindings[binding.ingress_event_id]
                if existing_b.event_descriptor_digest != binding.event_descriptor_digest:
                    raise CausalCommitCollisionError(
                        f"Conflicting binding for event '{binding.ingress_event_id}'"
                    )
            self.committed_event_bindings[binding.ingress_event_id] = binding

        self.committed_transactions[record.transaction_id] = record

    def to_dict(self) -> dict[str, Any]:
        """Serialize ledger state sorted by authoritative keys."""
        return {
            "causal_provenance_epoch": self.epoch.to_dict(),
            "committed_event_bindings": {
                k: self.committed_event_bindings[k].to_dict()
                for k in sorted(self.committed_event_bindings.keys())
            },
            "committed_transactions": {
                k: self.committed_transactions[k].to_dict()
                for k in sorted(self.committed_transactions.keys())
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CausalCommitLedger:
        """Restore ledger from serialized dict."""
        epoch_data = data.get("causal_provenance_epoch")
        if not epoch_data:
            raise CausalIdentityValidationError("Missing causal_provenance_epoch in ledger state")
        epoch = CausalProvenanceEpoch(
            epoch_id=epoch_data["epoch_id"],
            history_status=epoch_data["history_status"],
            base_state_digest=epoch_data["base_state_digest"],
        )
        bindings = {
            k: EventBindingRecord(
                ingress_event_id=v["ingress_event_id"],
                root_external_episode_id=v["root_external_episode_id"],
                event_descriptor_digest=v["event_descriptor_digest"],
                observation_protocol_version=v["observation_protocol_version"],
            )
            for k, v in data.get("committed_event_bindings", {}).items()
        }
        transactions = {
            k: CausalCommitRecord(
                transaction_id=v["transaction_id"],
                root_external_episode_id=v["root_external_episode_id"],
                ingress_event_id=v["ingress_event_id"],
                event_descriptor_digest=v["event_descriptor_digest"],
                mutation_owner_ref=v["mutation_owner_ref"],
                mutation_kind=v["mutation_kind"],
                mutation_descriptor_digest=v["mutation_descriptor_digest"],
                owner_defined_transaction_scope=v["owner_defined_transaction_scope"],
                observation_protocol_version=v["observation_protocol_version"],
            )
            for k, v in data.get("committed_transactions", {}).items()
        }
        return cls(
            epoch=epoch,
            committed_transactions=transactions,
            committed_event_bindings=bindings,
        )




# ─────────────────────────────────────────────────────────── Semantic Ledger Validator (PIR01-B07)
def validate_causal_provenance_state(
    causal_provenance_state: dict[str, Any],
    checkpoint_state_digest: str,
    checkpoint_observation_protocol_version: str,
) -> None:
    """Strict semantic validation of causal provenance records before ledger construction (Section 10 / PIR01-B07)."""
    if not isinstance(causal_provenance_state, dict):
        raise CausalIdentityValidationError("causal_provenance_state must be a dict")

    # 1. Provenance epoch validation
    epoch_data = causal_provenance_state.get("causal_provenance_epoch")
    if not isinstance(epoch_data, dict):
        raise CausalIdentityValidationError("Missing or invalid causal_provenance_epoch in provenance state")
    for ek in ("epoch_id", "history_status", "base_state_digest"):
        if ek not in epoch_data or not isinstance(epoch_data[ek], str) or not epoch_data[ek].strip():
            raise CausalIdentityValidationError(f"Missing or invalid field '{ek}' in causal_provenance_epoch")

    if epoch_data["history_status"] not in ("R1_TRACKED", "PRE_R1_HISTORY_UNAVAILABLE"):
        raise CausalIdentityValidationError(f"Unknown history_status '{epoch_data['history_status']}'")

    has_transactions = bool(causal_provenance_state.get("committed_transactions"))
    if (
        epoch_data["history_status"] == "PRE_R1_HISTORY_UNAVAILABLE" or not has_transactions
    ) and epoch_data["base_state_digest"] != checkpoint_state_digest:
        raise CausalIdentityValidationError(
            f"Provenance epoch base_state_digest mismatch: recorded '{epoch_data['base_state_digest']}' != checkpoint '{checkpoint_state_digest}'"
        )

    # 2. Event bindings validation
    bindings = causal_provenance_state.get("committed_event_bindings")
    if not isinstance(bindings, dict):
        raise CausalIdentityValidationError("committed_event_bindings must be a dict")

    for k, b in bindings.items():
        if not isinstance(b, dict):
            raise CausalIdentityValidationError(f"Invalid event binding record for key '{k}'")
        for bk in ("ingress_event_id", "root_external_episode_id", "event_descriptor_digest", "observation_protocol_version"):
            if bk not in b or not isinstance(b[bk], str) or not b[bk].strip():
                raise CausalIdentityValidationError(f"Event binding '{k}' missing or invalid field '{bk}'")
        if k != b["ingress_event_id"]:
            raise CausalIdentityValidationError(
                f"Event binding dictionary key '{k}' != record ingress_event_id '{b['ingress_event_id']}'"
            )
        if len(b["event_descriptor_digest"]) != 64 or not all(c in "0123456789abcdefABCDEF" for c in b["event_descriptor_digest"]):
            raise CausalIdentityValidationError(
                f"Event binding '{k}' has invalid event_descriptor_digest shape: '{b['event_descriptor_digest']}'"
            )
        if b["observation_protocol_version"] != checkpoint_observation_protocol_version:
            raise CausalIdentityValidationError(
                f"Event binding '{k}' observation_protocol_version '{b['observation_protocol_version']}' != checkpoint '{checkpoint_observation_protocol_version}'"
            )

    # 3. Committed transactions validation
    transactions = causal_provenance_state.get("committed_transactions")
    if not isinstance(transactions, dict):
        raise CausalIdentityValidationError("committed_transactions must be a dict")

    for k, tx in transactions.items():
        if not isinstance(tx, dict):
            raise CausalIdentityValidationError(f"Invalid transaction record for key '{k}'")
        required_tx = (
            "transaction_id",
            "root_external_episode_id",
            "ingress_event_id",
            "event_descriptor_digest",
            "mutation_owner_ref",
            "mutation_kind",
            "mutation_descriptor_digest",
            "owner_defined_transaction_scope",
            "observation_protocol_version",
        )
        for rk in required_tx:
            if rk not in tx:
                raise CausalIdentityValidationError(f"Transaction '{k}' missing required field '{rk}'")

        if k != tx["transaction_id"]:
            raise CausalIdentityValidationError(
                f"Transaction dictionary key '{k}' != record transaction_id '{tx['transaction_id']}'"
            )

        # Authoritative digest shape check: len 64 hex or standard prefix + 64 hex
        raw_tx_hex = tx["transaction_id"].split("_", 1)[-1] if "_" in tx["transaction_id"] else tx["transaction_id"]
        if len(raw_tx_hex) != 64 or not all(c in "0123456789abcdefABCDEF" for c in raw_tx_hex):
            raise CausalIdentityValidationError(
                f"Transaction '{k}' has invalid authoritative TxID digest shape: '{tx['transaction_id']}'"
            )

        if not tx["root_external_episode_id"] or not isinstance(tx["root_external_episode_id"], str):
            raise CausalIdentityValidationError(f"Transaction '{k}' has empty root_external_episode_id")

        if not tx["mutation_owner_ref"] or not isinstance(tx["mutation_owner_ref"], str):
            raise CausalIdentityValidationError(f"Transaction '{k}' has empty mutation_owner_ref")

        if not tx["mutation_kind"] or not isinstance(tx["mutation_kind"], str):
            raise CausalIdentityValidationError(f"Transaction '{k}' has empty mutation_kind")

        if len(tx["mutation_descriptor_digest"]) != 64 or not all(c in "0123456789abcdefABCDEF" for c in tx["mutation_descriptor_digest"]):
            raise CausalIdentityValidationError(
                f"Transaction '{k}' has invalid mutation_descriptor_digest shape: '{tx['mutation_descriptor_digest']}'"
            )

        # Reference to existing event binding
        ref_event_id = tx["ingress_event_id"]
        if ref_event_id not in bindings:
            raise CausalIdentityValidationError(
                f"Transaction '{k}' references missing ingress_event_id '{ref_event_id}'"
            )

        binding = bindings[ref_event_id]
        if tx["root_external_episode_id"] != binding["root_external_episode_id"]:
            raise CausalIdentityValidationError(
                f"Transaction '{k}' root '{tx['root_external_episode_id']}' != binding root '{binding['root_external_episode_id']}'"
            )

        if tx["event_descriptor_digest"] != binding["event_descriptor_digest"]:
            raise CausalIdentityValidationError(
                f"Transaction '{k}' event digest '{tx['event_descriptor_digest']}' != binding event digest '{binding['event_descriptor_digest']}'"
            )

        if tx["observation_protocol_version"] != binding["observation_protocol_version"]:
            raise CausalIdentityValidationError(
                f"Transaction '{k}' observation protocol '{tx['observation_protocol_version']}' != binding protocol '{binding['observation_protocol_version']}'"
            )

        if tx["observation_protocol_version"] != checkpoint_observation_protocol_version:
            raise CausalIdentityValidationError(
                f"Transaction '{k}' observation protocol '{tx['observation_protocol_version']}' != checkpoint protocol '{checkpoint_observation_protocol_version}'"
            )


class CognitiveGraphInspectionView:
    """Read-only inspection proxy for CognitiveGraph (Section 8 / PIR01-B05)."""

    def __init__(self, graph: Any, runtime: Any = None) -> None:
        self._graph = graph
        self._runtime = runtime

    @property
    def nodes(self) -> Any:
        return self._graph.nodes

    @property
    def edges(self) -> Any:
        return self._graph.edges

    @property
    def t(self) -> int:
        return self._graph.t

    @property
    def X(self) -> Any:
        return self._graph.X

    @property
    def assembly_manager(self) -> Any:
        return self._graph.assembly_manager

    @property
    def representation_engine(self) -> Any:
        return self._graph.representation_engine

    @property
    def completion_engine(self) -> Any:
        return self._graph.completion_engine

    @property
    def generation_engine(self) -> Any:
        return self._graph.generation_engine

    @property
    def recurrent_engine(self) -> Any:
        return self._graph.recurrent_engine

    @property
    def loop_engine(self) -> Any:
        return self._graph.loop_engine

    def edge(self, u: str, v: str) -> Any:
        return self._graph.edge(u, v)

    def node(self, nid: str, region: str | None = None) -> Any:
        if nid in self._graph.nodes:
            return self._graph.nodes[nid]
        raise CausalLineageError(
            "Direct node creation via CanonicalR1RuntimeRoot.graph is prohibited. "
            "Use runtime.execute_persistent_command() or runtime.unsafe_mutable_graph()."
        )

    def out_edges(self, u: str) -> Any:
        return self._graph.out_edges(u)

    def link(self, *args: Any, **kwargs: Any) -> Any:
        if self._runtime is not None:
            self._runtime.canonical_lineage_state = CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
        return self._graph.link(*args, **kwargs)

    def unlink(self, *args: Any, **kwargs: Any) -> Any:
        if self._runtime is not None:
            self._runtime.canonical_lineage_state = CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
        return self._graph.unlink(*args, **kwargs)

    def observe(self, *args: Any, **kwargs: Any) -> Any:
        if self._runtime is not None:
            self._runtime.canonical_lineage_state = CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
        return self._graph.observe(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._graph, name)


# ─────────────────────────────────────────────────────────── 7. Canonical R1 Runtime Root
class CanonicalR1RuntimeRoot:
    """Canonical R1 Runtime Root binding cognitive graph, ledger, health, and lifecycle (Section 54, PIR01-B05)."""

    def __init__(
        self,
        graph: Any,
        ledger: CausalCommitLedger,
        observation_protocol_version: str,
        assembly_policy: Any = None,
        lifecycle_guard: Any = None,
    ) -> None:
        if not isinstance(observation_protocol_version, str) or not observation_protocol_version.strip():
            raise CausalIdentityValidationError(
                "CanonicalR1RuntimeRoot requires an explicit non-empty observation_protocol_version"
            )
        self._graph = graph
        self.ledger = ledger
        self.observation_protocol_version = observation_protocol_version
        self.assembly_policy = assembly_policy

        from .persistence import RuntimeLifecycleGuard
        self.guard = lifecycle_guard if lifecycle_guard is not None else RuntimeLifecycleGuard()

        self.causal_runtime_health = CausalRuntimeHealth.HEALTHY
        self.canonical_lineage_state = CanonicalLineageState.VALID
        self._in_command: bool = False
        self._inspection_view = CognitiveGraphInspectionView(self._graph, runtime=self)

    @property
    def graph(self) -> Any:
        """Returns live mutable graph inside execute_persistent_command, or read-only inspection view outside."""
        if self._in_command:
            return self._graph
        return self._inspection_view

    def unsafe_mutable_graph(self) -> Any:
        """Explicitly unsafe raw mutable graph access (Section 8 / PIR01-B05).

        Invalidates canonical_lineage_state BEFORE returning mutable graph.
        """
        self.canonical_lineage_state = CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
        return self._graph

    def execute_persistent_command(
        self,
        command: PersistentMutationCommand,
        root_external_episode_id: str,
        ingress_event_id: str,
        event_descriptor_digest: str,
        mutator_callback: Callable[[], Any],
    ) -> tuple[str, bool, Any]:
        """Executes an authorized persistent mutation under exactly-once idempotent replay (Section 50).

        Returns (transaction_id, executed_flag, mutator_result).
        """
        # Step 1: Health check
        if self.causal_runtime_health != CausalRuntimeHealth.HEALTHY:
            raise CausalRuntimeFailStopError(
                "Runtime is in MUTATION_FAILED fail-stop state. Canonical mutations are blocked."
            )

        # Step 2: Lineage validity check
        if self.canonical_lineage_state != CanonicalLineageState.VALID:
            raise CausalLineageInvalidatedError(
                "Canonical lineage is invalidated by untracked persistent mutation."
            )

        # Step 3: Event binding validation
        staged_binding = self.ledger.validate_or_stage_event_binding(
            ingress_event_id=ingress_event_id,
            root_external_episode_id=root_external_episode_id,
            event_descriptor_digest=event_descriptor_digest,
            observation_protocol_version=self.observation_protocol_version,
        )

        # Step 4: Derive canonical TxID and mutation descriptor digest
        txid = derive_persistent_mutation_txid(root_external_episode_id, command)
        mutation_digest = compute_mutation_descriptor_digest(command.canonical_mutation_descriptor)

        # Step 5: Check ledger for committed replay
        if self.ledger.has_transaction(txid):
            self.ledger.check_transaction_replay(txid, mutation_digest, root_external_episode_id)
            return txid, False, None

        # Step 6: Execute mutator under MUTATING lifecycle using authoritative guard
        try:
            self._in_command = True
            with self.guard.mutating():
                result = mutator_callback()
        except Exception:
            self.causal_runtime_health = CausalRuntimeHealth.MUTATION_FAILED
            raise
        finally:
            self._in_command = False

        # Step 7: Commit transaction record to ledger
        try:
            record = CausalCommitRecord(
                transaction_id=txid,
                root_external_episode_id=root_external_episode_id,
                ingress_event_id=ingress_event_id,
                event_descriptor_digest=event_descriptor_digest,
                mutation_owner_ref=command.mutation_owner_ref,
                mutation_kind=command.mutation_kind,
                mutation_descriptor_digest=mutation_digest,
                owner_defined_transaction_scope=command.owner_defined_transaction_scope,
                observation_protocol_version=self.observation_protocol_version,
            )
            self.ledger.commit_transaction(record, staged_binding)
        except Exception:
            self.causal_runtime_health = CausalRuntimeHealth.MUTATION_FAILED
            raise

        return txid, True, result

    def unsafe_legacy_mutation_escape_hatch(self, mutator_callback: Callable[[], Any]) -> Any:
        """Explicit escape hatch for untracked persistent mutation (Section 55).

        Marks canonical_lineage_state as INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION.
        """
        self.canonical_lineage_state = CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
        return mutator_callback()
