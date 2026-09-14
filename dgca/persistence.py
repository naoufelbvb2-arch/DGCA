"""
DGCA — RIC-01 / R0-C01: Persistent Cognitive State & Runtime Lifecycle Contract
Formal Architecture Specification v1.1.1 — FROZEN

Constitutional Principles:
1. PersistentState ∩ TransientWorkingState = ∅
2. ReconstructibleState ∉ PersistentState
3. Checkpoint Type: COGNITIVE_CHECKPOINT (not LIVE_PROCESS_SUSPEND)
4. Canonical Restore: New CognitiveGraph, rebuilt indexes, fresh engines, atomic swap while RESTORING.
"""
from __future__ import annotations

import copy
import enum
import hashlib
import json
import math
import os
import pathlib
import uuid
from dataclasses import dataclass, field
from typing import Any

from .assembly import (
    AssemblyManager,
    AssemblyPolicy,
    FormationCandidate,
    StructuralAssembly,
    canonical_assembly_id,
)
from .causal_identity import (
    CAUSAL_IDENTITY_PROTOCOL_DIGEST,
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalIdentityValidationError,
    CausalLineageInvalidatedError,
    CausalRuntimeFailStopError,
    CausalRuntimeHealth,
    compute_causal_provenance_digest,
    compute_checkpoint_bundle_digest,
    compute_observation_protocol_digest,
    validate_causal_provenance_state,
)
from .config import REGIONS, Law
from .graph import CognitiveGraph, Edge, Node


# ─────────────────────────────────────────────────────────── 1. Exceptions
class CheckpointValidationError(Exception):
    """Base exception for all checkpoint validation and integrity failures."""


class CheckpointSchemaError(CheckpointValidationError):
    """Raised when checkpoint schema version is missing, unsupported, or malformed."""


class CheckpointIntegrityError(CheckpointValidationError):
    """Raised when checkpoint digest does not match the recomputed state digest."""


class CheckpointCompatibilityError(CheckpointValidationError):
    """Raised when checkpoint semantic fingerprint does not match host runtime."""


class StructuralReferentialIntegrityError(CheckpointValidationError):
    """Raised when structural or graph references are stale, missing, or malformed."""


class IllegalLifecycleTransitionError(Exception):
    """Raised when an illegal runtime lifecycle transition or concurrency overlap is attempted."""


class LegacyMigrationError(Exception):
    """Raised when checkpoint migration fails."""


# ─────────────────────────────────────────────────────────── 2. Runtime Lifecycle Guard
class RuntimeLifecycleState(enum.Enum):
    """Non-cognitive host engineering lifecycle states."""
    IDLE = "IDLE"
    MUTATING = "MUTATING"
    CHECKPOINTING = "CHECKPOINTING"
    RESTORING = "RESTORING"


class RuntimeLifecycleGuard:
    """Engineering concurrency and lifecycle guard. Owns no cognition or learning."""

    def __init__(self, initial_state: RuntimeLifecycleState = RuntimeLifecycleState.IDLE) -> None:
        self._state = initial_state

    @property
    def state(self) -> RuntimeLifecycleState:
        return self._state

    def transition_to(self, new_state: RuntimeLifecycleState) -> None:
        """Transitions state or raises IllegalLifecycleTransitionError."""
        current = self._state

        # Allowed transitions:
        # IDLE -> MUTATING -> IDLE
        # IDLE -> CHECKPOINTING -> IDLE
        # IDLE -> RESTORING -> IDLE
        # Same-state nesting (e.g. RESTORING -> RESTORING) is strictly prohibited (C03-07 / C03-I14).
        if current == RuntimeLifecycleState.IDLE:
            if new_state in (
                RuntimeLifecycleState.MUTATING,
                RuntimeLifecycleState.CHECKPOINTING,
                RuntimeLifecycleState.RESTORING,
            ):
                self._state = new_state
                return
        elif current in (
            RuntimeLifecycleState.MUTATING,
            RuntimeLifecycleState.CHECKPOINTING,
            RuntimeLifecycleState.RESTORING,
        ) and new_state == RuntimeLifecycleState.IDLE:
            self._state = new_state
            return

        raise IllegalLifecycleTransitionError(
            f"Illegal lifecycle transition: cannot transition from {current.value} to {new_state.value}"
        )

    def checkpointing(self):
        """Context manager for CHECKPOINTING state."""
        return _LifecycleContext(self, RuntimeLifecycleState.CHECKPOINTING)

    def restoring(self):
        """Context manager for RESTORING state."""
        return _LifecycleContext(self, RuntimeLifecycleState.RESTORING)

    def mutating(self):
        """Context manager for MUTATING state."""
        return _LifecycleContext(self, RuntimeLifecycleState.MUTATING)


class _LifecycleContext:
    def __init__(self, guard: RuntimeLifecycleGuard, target_state: RuntimeLifecycleState) -> None:
        self.guard = guard
        self.target_state = target_state
        self._entered = False

    def __enter__(self):
        self.guard.transition_to(self.target_state)
        self._entered = True
        return self.guard

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._entered:
            self.guard.transition_to(RuntimeLifecycleState.IDLE)


# ─────────────────────────────────────────────────────────── 3. Diagnostic Migration Report
@dataclass
class MigrationReport:
    """Developer-only diagnostic migration report (DIAGNOSTIC_STATE). Never cognitive state."""
    source_schema: str
    target_schema: str
    restored_durable_fields: list[str]
    reset_transient_fields: list[str]
    ignored_runtime_configuration: list[str]
    unrecoverable_legacy_state: list[str]
    compatibility_result: str
    migration_result: str
    diagnostic_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_schema": self.source_schema,
            "target_schema": self.target_schema,
            "restored_durable_fields": self.restored_durable_fields,
            "reset_transient_fields": self.reset_transient_fields,
            "ignored_runtime_configuration": self.ignored_runtime_configuration,
            "unrecoverable_legacy_state": self.unrecoverable_legacy_state,
            "compatibility_result": self.compatibility_result,
            "migration_result": self.migration_result,
            "diagnostic_notes": self.diagnostic_notes,
        }


# ─────────────────────────────────────────────────────────── 4. Policy Utilities & Semantic Fingerprints
def policies_semantically_equal(p1: AssemblyPolicy, p2: AssemblyPolicy) -> bool:
    """Compares policies across the complete authoritative policy payload."""
    return (
        p1.policy_version == p2.policy_version
        and p1.K_ASM_MIN == p2.K_ASM_MIN
        and p1.N_ASM_CONFIRM == p2.N_ASM_CONFIRM
        and p1.A_MAX == p2.A_MAX
        and p1.K_ASM_MEM == p2.K_ASM_MEM
        and p1.K_ASM_ACTIVE == p2.K_ASM_ACTIVE
        and p1.K_STRUCT_PENDING == p2.K_STRUCT_PENDING
    )


def resolve_effective_policy(
    graph: CognitiveGraph,
    explicit_policy: AssemblyPolicy | None = None,
) -> AssemblyPolicy:
    """Resolves authoritative effective policy per Section 8."""
    if graph._assembly_manager is not None:
        mgr_policy = graph._assembly_manager.policy
        if explicit_policy is not None and not policies_semantically_equal(mgr_policy, explicit_policy):
            raise CheckpointCompatibilityError(
                "Policy mismatch: explicit policy does not match graph AssemblyManager policy"
            )
        return mgr_policy
    elif explicit_policy is not None:
        return explicit_policy
    else:
        return AssemblyPolicy()


def compute_region_schema_digest() -> str:
    """SHA-256 digest over the canonical sorted region namespace."""
    sorted_regions = sorted(REGIONS)
    payload = json.dumps({"regions": sorted_regions}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_active_law_digest() -> str:
    """SHA-256 digest over all active public Law constants, excluding reserved Law 3 constants."""
    excluded = {"LAMBDA_DECAY", "LAMBDA_TRANSIENT", "THETA_PRUNE"}
    law_dict = {}
    for attr in sorted(dir(Law)):
        if attr.isupper() and not attr.startswith("_") and attr not in excluded:
            val = getattr(Law, attr)
            if isinstance(val, (int, float, str, bool)):
                law_dict[attr] = val
    payload = json.dumps(law_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_assembly_policy_digest(policy: AssemblyPolicy | None = None) -> str:
    """SHA-256 digest over the authoritative AssemblyPolicy parameters."""
    pol = policy or AssemblyPolicy()
    policy_dict = {
        "A_MAX": pol.A_MAX,
        "K_ASM_ACTIVE": pol.K_ASM_ACTIVE,
        "K_ASM_MEM": pol.K_ASM_MEM,
        "K_ASM_MIN": pol.K_ASM_MIN,
        "K_STRUCT_PENDING": pol.K_STRUCT_PENDING,
        "N_ASM_CONFIRM": pol.N_ASM_CONFIRM,
        "policy_version": pol.policy_version,
    }
    payload = json.dumps(policy_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_combined_semantics_digest(
    region_digest: str,
    law_digest: str,
    policy_digest: str,
    cognitive_semantics_version: str = "1.0",
) -> str:
    """Combined deterministic semantic compatibility digest D_sem."""
    combined = {
        "active_law_digest": law_digest,
        "assembly_policy_digest": policy_digest,
        "cognitive_semantics_version": cognitive_semantics_version,
        "region_schema_digest": region_digest,
    }
    payload = json.dumps(combined, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────── 4.1 Strict JSON Loader & Shape Validation
def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Rejects duplicate JSON object keys instead of last-key-wins behavior (C03-03 / C03-I04)."""
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise CheckpointSchemaError(f"Duplicate JSON object key detected: '{key}'")
        obj[key] = value
    return obj


def load_checkpoint_json(content_or_path: str | pathlib.Path | bytes) -> dict[str, Any]:
    """Loads JSON data for checkpoint operations, strictly rejecting duplicate keys at any depth."""
    try:
        if isinstance(content_or_path, pathlib.Path):
            with open(content_or_path, "r", encoding="utf-8") as f:
                return json.load(f, object_pairs_hook=_reject_duplicate_json_keys)
        elif isinstance(content_or_path, bytes):
            return json.loads(content_or_path.decode("utf-8"), object_pairs_hook=_reject_duplicate_json_keys)
        elif isinstance(content_or_path, str):
            is_file = False
            try:
                p = pathlib.Path(content_or_path)
                if p.is_file():
                    is_file = True
            except OSError:
                is_file = False
            if is_file:
                with open(content_or_path, "r", encoding="utf-8") as f:
                    return json.load(f, object_pairs_hook=_reject_duplicate_json_keys)
            return json.loads(content_or_path, object_pairs_hook=_reject_duplicate_json_keys)
        else:
            raise CheckpointSchemaError(f"Unsupported input type for load_checkpoint_json: {type(content_or_path)}")
    except json.JSONDecodeError as err:
        raise CheckpointSchemaError(f"Malformed JSON checkpoint: {err}")


def validate_canonical_persistent_shape(
    data: dict[str, Any],
    schema_label: str = "1.1.1",
) -> None:
    """Validates top-level sections and all frozen durable persistent fields without defaulting (C03-04 / C03-I05 / R1-061)."""
    if not isinstance(data, dict):
        raise CheckpointSchemaError(f"{schema_label} checkpoint must be a JSON object (dict)")

    if schema_label == "1.2.0":
        top_level_keys = ["schema", "compatibility", "integrity", "persistent_state", "causal_provenance_state"]
    else:
        top_level_keys = ["schema", "compatibility", "integrity", "persistent_state"]

    for k in top_level_keys:
        if k not in data or not isinstance(data[k], dict):
            raise CheckpointSchemaError(
                f"Missing or invalid top-level section '{k}' in {schema_label} checkpoint"
            )

    if schema_label == "1.2.0":
        prov_state = data["causal_provenance_state"]
        required_prov = ["causal_provenance_epoch", "committed_event_bindings", "committed_transactions"]
        for pk in required_prov:
            if pk not in prov_state or not isinstance(prov_state[pk], dict):
                raise CheckpointSchemaError(
                    f"Missing or invalid causal_provenance_state section '{pk}' in 1.2.0 checkpoint"
                )
        epoch_data = prov_state["causal_provenance_epoch"]
        for ek in ["epoch_id", "history_status", "base_state_digest"]:
            if ek not in epoch_data or not isinstance(epoch_data[ek], str) or not epoch_data[ek].strip():
                raise CheckpointSchemaError(
                    f"Missing or invalid field '{ek}' in causal_provenance_epoch"
                )
        integrity = data["integrity"]
        for ik in ["checkpoint_state_digest", "causal_provenance_digest", "checkpoint_bundle_digest"]:
            if ik not in integrity or not isinstance(integrity[ik], str) or not integrity[ik].strip():
                raise CheckpointIntegrityError(
                    f"Missing or invalid integrity field '{ik}' in 1.2.0 checkpoint"
                )

    pstate = data["persistent_state"]
    required_pstate: dict[str, tuple[type, ...]] = {
        "logical_time": (int,),
        "nodes": (list,),
        "edges": (list,),
        "contradictions": (dict,),
        "concept_hits": (dict,),
        "drives": (dict,),
        "hypotheses": (list,),
        "assemblies": (list,),
        "pending_structural_evidence": (dict,),
    }

    for fname, exp_types in required_pstate.items():
        if fname not in pstate:
            raise CheckpointSchemaError(
                f"Missing durable persistent section '{fname}' in {schema_label} checkpoint"
            )
        val = pstate[fname]
        if fname == "logical_time":
            if not isinstance(val, int) or isinstance(val, bool):
                raise CheckpointSchemaError(
                    f"Invalid type for 'logical_time': expected int, got {type(val).__name__}"
                )
        elif not isinstance(val, exp_types):
            raise CheckpointSchemaError(
                f"Invalid type for '{fname}': expected {exp_types[0].__name__}, got {type(val).__name__}"
            )

    pending_ev = pstate["pending_structural_evidence"]
    for sub in ["pending_candidates", "pending_growth", "pending_merge"]:
        if sub not in pending_ev or not isinstance(pending_ev[sub], list):
            raise CheckpointSchemaError(
                f"Missing or invalid pending structural evidence sub-section '{sub}' in {schema_label} checkpoint"
            )


def validate_legacy_v1_source(legacy_data: dict[str, Any]) -> None:
    """Validates that legacy data conforms strictly to DGCA legacy v1.0 structure (C03-02 / C03-I02 / C03-I03)."""
    if not isinstance(legacy_data, dict):
        raise CheckpointSchemaError("Legacy checkpoint must be a JSON object (dict)")

    if legacy_data.get("version") != "1.0":
        raise CheckpointSchemaError(
            f"Unsupported or missing legacy version: '{legacy_data.get('version')}', expected '1.0'"
        )

    if "schema" in legacy_data:
        raise CheckpointSchemaError(
            "Ambiguous checkpoint: legacy format must not define a canonical 'schema' section"
        )

    required_sections: dict[str, tuple[type, ...]] = {
        "t": (int,),
        "concept_hits": (dict,),
        "drives": (dict,),
        "hypotheses": (list,),
        "X": (dict,),
        "nodes": (dict,),
        "edges": (list,),
        "assemblies": (list,),
    }

    for sec_name, expected_types in required_sections.items():
        if sec_name not in legacy_data:
            raise CheckpointSchemaError(f"Missing durable legacy section: '{sec_name}'")
        val = legacy_data[sec_name]
        if sec_name == "t":
            if not isinstance(val, int) or isinstance(val, bool):
                raise CheckpointSchemaError(
                    f"Invalid type for legacy section 't': expected int, got {type(val).__name__}"
                )
        elif not isinstance(val, expected_types):
            raise CheckpointSchemaError(
                f"Invalid type for legacy section '{sec_name}': expected {expected_types[0].__name__}, got {type(val).__name__}"
            )

    assert_finite_numbers(legacy_data, "legacy_v1_source")


# ─────────────────────────────────────────────────────────── 5. Numeric Validation
def assert_finite_numbers(obj: Any, path: str = "root") -> None:
    """Recursively validates that all numeric values in a structure are finite (no NaN, +Inf, -Inf)."""
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise CheckpointValidationError(f"Non-finite numeric value '{obj}' detected at {path}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            assert_finite_numbers(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for idx, item in enumerate(obj):
            assert_finite_numbers(item, f"{path}[{idx}]")


# ─────────────────────────────────────────────────────────── 6. Canonical State Extraction & Digest
def extract_canonical_persistent_payload(
    graph: CognitiveGraph,
    policy: AssemblyPolicy | None = None,
) -> dict[str, Any]:
    """Extracts the exact, canonically ordered persistent payload from CognitiveGraph."""
    # 1. Nodes (sorted by nid)
    nodes_list = []
    for nid in sorted(graph.nodes.keys()):
        n = graph.nodes[nid]
        nodes_list.append({
            "N_total": n.N_total,
            "U": float(n.U),
            "V": float(n.V),
            "head": n.head,
            "is_concept": bool(n.is_concept),
            "is_intrinsic": bool(n.is_intrinsic),
            "members": sorted(n.members),
            "nid": str(n.nid),
            "region": str(n.region),
        })

    # 2. Edges (sorted by (src, dst))
    edges_list = []
    for pair in sorted(graph.edges.keys()):
        e = graph.edges[pair]
        sorted_ctx_hits = {k: e.ctx_hits[k] for k in sorted(e.ctx_hits.keys())}
        edges_list.append({
            "M_max": float(e.M_max),
            "S": float(e.S),
            "W": float(e.W),
            "contexts": sorted(e.contexts),
            "ctx_hits": sorted_ctx_hits,
            "dst": str(e.dst),
            "fwd": bool(e.fwd),
            "g": e.g,
            "is_intrinsic": bool(e.is_intrinsic),
            "k_fail": int(e.k_fail),
            "kind": str(e.kind),
            "lag": float(e.lag),
            "n": int(e.n),
            "origin": str(e.origin),
            "src": str(e.src),
            "t_created": int(e.t_created),
            "t_last_update": int(e.t_last_update),
            "tagged": bool(e.tagged),
            "valence": float(e.valence),
        })

    # 3. Contradictions X (sorted keys and sorted values)
    sorted_x = {k: sorted(graph.X[k]) for k in sorted(graph.X.keys())}

    # 4. Concept hits (sorted keys)
    sorted_concept_hits = {k: int(graph.concept_hits[k]) for k in sorted(graph.concept_hits.keys())}

    # 5. Drives (exact durable internal state)
    sorted_drives = {}
    for drive_key in sorted(graph.drives.keys()):
        d_val = graph.drives[drive_key]
        if isinstance(d_val, dict):
            sorted_drives[drive_key] = {k: d_val[k] for k in sorted(d_val.keys())}
        else:
            sorted_drives[drive_key] = d_val

    # 6. Hypotheses (isolated hypothesis state)
    # Order is durable per C01-05; do NOT sort.
    hypotheses_list = copy.deepcopy(graph.hypotheses)

    # 7. Assemblies (sorted by assembly_id then version)
    assemblies_list = []
    mgr = graph._assembly_manager
    if mgr is not None:
        for aid in sorted(mgr.assemblies.keys()):
            for asm in sorted(mgr.assemblies[aid], key=lambda a: a.version):
                member_edges_sorted = sorted([[u, v] for u, v in asm.member_edges])
                # parent_assemblies is an ordered tuple; order is durable per C01-05; do NOT sort.
                assemblies_list.append({
                    "assembly_id": asm.assembly_id,
                    "is_retired": bool(asm.is_retired),
                    "member_edges": member_edges_sorted,
                    "origin_signature": str(asm.origin_signature),
                    "parent_assemblies": list(asm.parent_assemblies),
                    "predecessor_version": asm.predecessor_version,
                    "version": int(asm.version),
                })

    # 8. Pending Structural Evidence
    pending_candidates_list = []
    pending_growth_list = []
    pending_merge_list = []

    if mgr is not None:
        # Formation candidates (sorted by storage_key)
        for storage_key in sorted(mgr.pending_candidates.keys()):
            cand = mgr.pending_candidates[storage_key]
            expected_key = f"{cand.candidate_id}:ctx_{cand.context_signature or 'default'}"
            if storage_key != expected_key:
                raise StructuralReferentialIntegrityError(
                    f"Formation candidate storage_key '{storage_key}' does not match expected_key '{expected_key}'"
                )
            pending_candidates_list.append({
                "candidate_id": cand.candidate_id,
                "context_signature": cand.context_signature,
                "created_t": int(cand.created_t),
                "edges": sorted([[u, v] for u, v in cand.edges]),
                "root_votes": sorted(cand.root_votes),
                "storage_key": storage_key,
            })

        # Growth candidates
        for g_key in sorted(
            mgr.pending_growth.keys(),
            key=lambda k: (k[0], k[1][0], k[1][1], k[2] or ""),
        ):
            aid, (u, v), ctx = g_key
            votes = mgr.pending_growth[g_key]
            pending_growth_list.append({
                "assembly_id": str(aid),
                "context": ctx,
                "new_edge": [str(u), str(v)],
                "root_votes": sorted(votes),
            })

        # Merge candidates
        for m_key in sorted(
            mgr.pending_merge.keys(),
            key=lambda k: (tuple(sorted(k[0])), k[1] or ""),
        ):
            parents_set, ctx = m_key
            votes = mgr.pending_merge[m_key]
            pending_merge_list.append({
                "context": ctx,
                "parent_assembly_ids": sorted(parents_set),
                "root_votes": sorted(votes),
            })

    pending_evidence = {
        "pending_candidates": pending_candidates_list,
        "pending_growth": pending_growth_list,
        "pending_merge": pending_merge_list,
    }

    payload = {
        "assemblies": assemblies_list,
        "concept_hits": sorted_concept_hits,
        "contradictions": sorted_x,
        "drives": sorted_drives,
        "edges": edges_list,
        "hypotheses": hypotheses_list,
        "logical_time": int(graph.t),
        "nodes": nodes_list,
        "pending_structural_evidence": pending_evidence,
    }

    assert_finite_numbers(payload, "persistent_state")
    return payload


def compute_checkpoint_state_digest(persistent_payload: dict[str, Any]) -> str:
    """Computes SHA-256 state digest D_state over the canonical persistent payload."""
    canonical_json = json.dumps(
        persistent_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────── 7. Structural Referential Integrity
def validate_structural_referential_integrity(
    graph: CognitiveGraph,
    mgr: AssemblyManager | None = None,
) -> None:
    """Validates structural referential integrity. Fails closed on any violation."""
    # 1. Edge endpoints must exist in graph.nodes
    for (src, dst) in graph.edges:
        if src not in graph.nodes:
            raise StructuralReferentialIntegrityError(
                f"Referential integrity failure: edge source '{src}' missing from graph.nodes"
            )
        if dst not in graph.nodes:
            raise StructuralReferentialIntegrityError(
                f"Referential integrity failure: edge destination '{dst}' missing from graph.nodes"
            )

    if mgr is None:
        mgr = graph._assembly_manager

    if mgr is not None:
        # 2. Live assembly member edges must exist in graph.edges
        for aid, versions in mgr.assemblies.items():
            if not versions:
                continue
            for i in range(len(versions) - 1):
                if versions[i].version >= versions[i + 1].version:
                    raise StructuralReferentialIntegrityError(
                        f"Assembly version ordering violation for '{aid}': version {versions[i].version} >= {versions[i+1].version}"
                    )
            latest = versions[-1]
            if not latest.is_retired:
                for u, v in latest.member_edges:
                    if (u, v) not in graph.edges:
                        raise StructuralReferentialIntegrityError(
                            f"Live assembly member edge ({u}, {v}) of '{aid}' missing from graph.edges"
                        )

        # 3. Pending Formation Candidates referential integrity & RFC-11 validation (C03-06)
        for storage_key, cand in mgr.pending_candidates.items():
            expected_key = f"{cand.candidate_id}:ctx_{cand.context_signature or 'default'}"
            if storage_key != expected_key:
                raise CheckpointValidationError(
                    f"Formation candidate storage_key '{storage_key}' does not match expected_key '{expected_key}'"
                )
            expected_cid = canonical_assembly_id([(u, v) for u, v in cand.edges])
            if cand.candidate_id != expected_cid:
                raise CheckpointValidationError(
                    f"Formation candidate_id '{cand.candidate_id}' does not match canonical_assembly_id '{expected_cid}'"
                )
            k_min = mgr.policy.K_ASM_MIN
            k_max = mgr.policy.K_ASM_MEM
            if not (k_min <= len(cand.edges) <= k_max):
                raise CheckpointValidationError(
                    f"Formation candidate edge count {len(cand.edges)} outside bounds [{k_min}, {k_max}]"
                )
            for u, v in cand.edges:
                if (u, v) not in graph.edges:
                    raise StructuralReferentialIntegrityError(
                        f"Formation candidate '{storage_key}' references edge ({u}, {v}) which is not in live graph.edges"
                    )

        # 4. Pending Growth referential integrity & RFC-11 validation (C03-06)
        for (aid, (u, v), ctx) in mgr.pending_growth:
            if aid not in mgr.assemblies:
                raise StructuralReferentialIntegrityError(
                    f"Pending growth references non-existent parent assembly '{aid}'"
                )
            latest = mgr.assemblies[aid][-1]
            if latest.is_retired:
                raise StructuralReferentialIntegrityError(
                    f"Pending growth references retired parent assembly '{aid}'"
                )
            if (u, v) in latest.member_edges:
                raise CheckpointValidationError(
                    f"Growth candidate new_edge {(u, v)} is already a member of parent assembly '{aid}'"
                )
            if (u, v) not in graph.edges:
                raise StructuralReferentialIntegrityError(
                    f"Pending growth references new_edge ({u}, {v}) missing from live graph.edges"
                )

        # 5. Pending Merge referential integrity & RFC-11 validation (C03-06)
        for (parents_set, ctx) in mgr.pending_merge:
            if len(parents_set) != 2:
                raise CheckpointValidationError(
                    f"Merge candidate must have exactly two distinct parents, got {len(parents_set)}"
                )
            for pid in parents_set:
                if pid not in mgr.assemblies:
                    raise StructuralReferentialIntegrityError(
                        f"Pending merge references non-existent parent assembly '{pid}'"
                    )
                latest = mgr.assemblies[pid][-1]
                if latest.is_retired:
                    raise StructuralReferentialIntegrityError(
                        f"Pending merge references retired parent assembly '{pid}'"
                    )


# ─────────────────────────────────────────────────────────── 8. Canonical Checkpoint Construction
def build_canonical_checkpoint(
    graph: CognitiveGraph,
    policy: AssemblyPolicy | None = None,
    diagnostic_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Constructs the canonical top-level DGCA_COGNITIVE_CHECKPOINT v1.1.1 structure."""
    pol = resolve_effective_policy(graph, policy)

    # 1. Validate referential integrity before checkpoint construction
    validate_structural_referential_integrity(graph, graph._assembly_manager)

    # 2. Extract canonical persistent payload
    persistent_payload = extract_canonical_persistent_payload(graph, pol)

    # 3. Compute digests
    state_digest = compute_checkpoint_state_digest(persistent_payload)
    region_digest = compute_region_schema_digest()
    law_digest = compute_active_law_digest()
    policy_digest = compute_assembly_policy_digest(pol)
    combined_digest = compute_combined_semantics_digest(region_digest, law_digest, policy_digest, "1.0")

    metadata = {
        "provenance": "DGCA_R0_CANONICAL",
        "source_schema": "1.1.1",
    }
    if diagnostic_metadata:
        metadata.update(diagnostic_metadata)

    checkpoint = {
        "compatibility": {
            "active_law_digest": law_digest,
            "assembly_policy_digest": policy_digest,
            "combined_semantics_digest": combined_digest,
            "region_schema_digest": region_digest,
        },
        "diagnostic_metadata": metadata,
        "integrity": {
            "checkpoint_state_digest": state_digest,
        },
        "persistent_state": persistent_payload,
        "schema": {
            "checkpoint_schema_version": "1.1.1",
            "cognitive_semantics_version": "1.0",
            "runtime_contract_version": "1.1.1",
        },
    }
    return checkpoint



# ─────────────────────────────────────────────────────────── Shared File Durability & Semantic Validator
def _atomic_replace_file(dest_path: pathlib.Path, content_bytes: bytes) -> None:
    """Atomically writes content_bytes to dest_path via same-directory temp file with directory fsync (PIR01-B06)."""
    dest_dir = dest_path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    temp_file = dest_dir / f".tmp_{dest_path.name}_{uuid.uuid4().hex}"
    try:
        with open(temp_file, "wb") as f:
            f.write(content_bytes)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_file, dest_path)

        try:
            if hasattr(os, "O_DIRECTORY"):
                dir_fd = os.open(str(dest_dir), os.O_DIRECTORY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        except (OSError, AttributeError):
            pass
    except Exception:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass
        raise


def validate_semantic_compatibility(
    checkpoint_data: dict[str, Any],
    policy: AssemblyPolicy | None = None,
    expected_schema_version: str = "1.2.0",
    expected_contract_version: str = "1.2.0",
    expected_observation_protocol_version: str | None = None,
) -> None:
    """Authoritative semantic compatibility validator for R0, R1, and migration paths (PIR01-B01)."""
    schema_sec = checkpoint_data.get("schema", {})
    if not isinstance(schema_sec, dict):
        raise CheckpointSchemaError("Missing or invalid 'schema' section")

    schema_ver = schema_sec.get("checkpoint_schema_version")
    if schema_ver != expected_schema_version:
        raise CheckpointSchemaError(
            f"Checkpoint schema version mismatch: recorded '{schema_ver}' != expected '{expected_schema_version}'"
        )

    contract_ver = schema_sec.get("runtime_contract_version")
    if contract_ver != expected_contract_version:
        raise CheckpointCompatibilityError(
            f"Runtime contract version mismatch: recorded '{contract_ver}' != expected '{expected_contract_version}'"
        )

    cog_sem_ver = schema_sec.get("cognitive_semantics_version")
    if cog_sem_ver != "1.0":
        raise CheckpointCompatibilityError(
            f"Cognitive semantics version mismatch: recorded '{cog_sem_ver}' != expected '1.0'"
        )

    # Recompute R0 semantic compatibility digests
    current_region_digest = compute_region_schema_digest()
    current_law_digest = compute_active_law_digest()
    current_policy_digest = compute_assembly_policy_digest(policy)
    current_combined_digest = compute_combined_semantics_digest(
        current_region_digest, current_law_digest, current_policy_digest, "1.0"
    )

    compat_sec = checkpoint_data.get("compatibility", {})
    if not isinstance(compat_sec, dict):
        raise CheckpointSchemaError("Missing or invalid 'compatibility' section")

    if compat_sec.get("region_schema_digest") != current_region_digest:
        raise CheckpointCompatibilityError(
            f"Region schema digest mismatch: recorded '{compat_sec.get('region_schema_digest')}' != computed '{current_region_digest}'"
        )
    if compat_sec.get("active_law_digest") != current_law_digest:
        raise CheckpointCompatibilityError(
            f"Active law digest mismatch: recorded '{compat_sec.get('active_law_digest')}' != computed '{current_law_digest}'"
        )
    if compat_sec.get("assembly_policy_digest") != current_policy_digest:
        raise CheckpointCompatibilityError(
            f"Assembly policy digest mismatch: recorded '{compat_sec.get('assembly_policy_digest')}' != computed '{current_policy_digest}'"
        )
    if compat_sec.get("combined_semantics_digest") != current_combined_digest:
        raise CheckpointCompatibilityError(
            f"Combined semantics digest mismatch: recorded '{compat_sec.get('combined_semantics_digest')}' != computed '{current_combined_digest}'"
        )

    if expected_schema_version == "1.2.0":
        causal_ver = schema_sec.get("causal_identity_protocol_version")
        if causal_ver != "1.0":
            raise CheckpointCompatibilityError(
                f"Causal identity protocol version mismatch: recorded '{causal_ver}' != expected '1.0'"
            )
        if compat_sec.get("causal_identity_protocol_digest") != CAUSAL_IDENTITY_PROTOCOL_DIGEST:
            raise CheckpointCompatibilityError(
                f"Causal identity protocol digest mismatch: recorded '{compat_sec.get('causal_identity_protocol_digest')}' != expected '{CAUSAL_IDENTITY_PROTOCOL_DIGEST}'"
            )
        obs_ver = schema_sec.get("observation_protocol_version")
        if not obs_ver or not isinstance(obs_ver, str) or not obs_ver.strip():
            raise CausalIdentityValidationError("Missing or empty observation_protocol_version in 1.2.0 schema")
        if expected_observation_protocol_version is not None and obs_ver != expected_observation_protocol_version:
            raise CheckpointCompatibilityError(
                f"Observation protocol version mismatch: recorded '{obs_ver}' != expected '{expected_observation_protocol_version}'"
            )
        expected_obs_digest = compute_observation_protocol_digest(obs_ver)
        if compat_sec.get("observation_protocol_digest") != expected_obs_digest:
            raise CheckpointCompatibilityError(
                f"Observation protocol digest mismatch: recorded '{compat_sec.get('observation_protocol_digest')}' != computed '{expected_obs_digest}'"
            )


# ─────────────────────────────────────────────────────────── 9. Atomic Save Protocol
def save_cognitive_checkpoint(
    graph: CognitiveGraph,
    filepath: str | pathlib.Path,
    policy: AssemblyPolicy | None = None,
    guard: RuntimeLifecycleGuard | None = None,
    diagnostic_metadata: dict[str, Any] | None = None,
) -> str:
    """Saves a canonical cognitive checkpoint using same-directory temporary file atomic replace.

    Returns the state digest D_state of the saved checkpoint.
    """
    effective_policy = resolve_effective_policy(graph, policy)

    dest_path = pathlib.Path(filepath).resolve()
    dest_dir = dest_path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    active_guard = guard or RuntimeLifecycleGuard()
    with active_guard.checkpointing():
        checkpoint_data = build_canonical_checkpoint(graph, effective_policy, diagnostic_metadata)
        canonical_json_bytes = json.dumps(
            checkpoint_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        _atomic_replace_file(dest_path, canonical_json_bytes)
        return checkpoint_data["integrity"]["checkpoint_state_digest"]


# ─────────────────────────────────────────────────────────── 10. Schema Migrations
def validate_schema_1_1_source(
    source: dict[str, Any],
    policy: AssemblyPolicy | None = None,
) -> None:
    """Validates that a checkpoint is an authentic, untampered, compatible schema-1.1 checkpoint.

    Required source checks (R0-C02 Sections 3 & 4):
    - checkpoint_schema_version == '1.1'
    - runtime_contract_version == '1.1'
    - cognitive_semantics_version == '1.0'
    - persistent_state exists and is structurally valid dict
    - all numeric values in persistent_state are finite
    - recorded checkpoint_state_digest exists and is non-empty
    - SHA256(canonical source persistent_state) == recorded checkpoint_state_digest
    - semantic compatibility digests match current runtime
    """
    if not isinstance(source, dict):
        raise CheckpointSchemaError("Source checkpoint must be a JSON object (dict)")

    validate_canonical_persistent_shape(source, schema_label="1.1")

    schema_sec = source.get("schema")
    if not isinstance(schema_sec, dict):
        raise CheckpointSchemaError("Missing or invalid 'schema' section in schema 1.1 source")

    schema_ver = schema_sec.get("checkpoint_schema_version")
    if schema_ver != "1.1":
        raise CheckpointSchemaError(
            f"Unsupported source checkpoint_schema_version: '{schema_ver}', expected '1.1'"
        )

    contract_ver = schema_sec.get("runtime_contract_version")
    if contract_ver != "1.1":
        raise CheckpointCompatibilityError(
            f"Incompatible or missing source runtime_contract_version: '{contract_ver}', expected '1.1'"
        )

    cog_sem_ver = schema_sec.get("cognitive_semantics_version")
    if cog_sem_ver != "1.0":
        raise CheckpointCompatibilityError(
            f"Incompatible or missing source cognitive_semantics_version: '{cog_sem_ver}', expected '1.0'"
        )

    persistent_state = source.get("persistent_state")
    if not isinstance(persistent_state, dict):
        raise CheckpointSchemaError("Missing or invalid 'persistent_state' in schema 1.1 source")

    assert_finite_numbers(persistent_state, "schema_1_1_source_persistent_state")

    integrity_sec = source.get("integrity")
    if not isinstance(integrity_sec, dict) or "checkpoint_state_digest" not in integrity_sec:
        raise CheckpointIntegrityError(
            "Missing 'checkpoint_state_digest' in schema 1.1 source integrity section"
        )

    recorded_state_digest = integrity_sec["checkpoint_state_digest"]
    if not isinstance(recorded_state_digest, str) or not recorded_state_digest:
        raise CheckpointIntegrityError(
            "Invalid or empty 'checkpoint_state_digest' in schema 1.1 source integrity section"
        )

    expected_source_digest = compute_checkpoint_state_digest(persistent_state)
    if recorded_state_digest != expected_source_digest:
        raise CheckpointIntegrityError(
            f"Schema 1.1 source state digest mismatch: recorded '{recorded_state_digest}' != computed '{expected_source_digest}'"
        )

    compat_sec = source.get("compatibility")
    if not isinstance(compat_sec, dict):
        raise CheckpointCompatibilityError("Missing 'compatibility' section in schema 1.1 source")

    current_region_digest = compute_region_schema_digest()
    current_law_digest = compute_active_law_digest()
    current_policy_digest = compute_assembly_policy_digest(policy)
    current_combined_digest = compute_combined_semantics_digest(
        region_digest=current_region_digest,
        law_digest=current_law_digest,
        policy_digest=current_policy_digest,
        cognitive_semantics_version=cog_sem_ver,
    )

    if compat_sec.get("region_schema_digest") != current_region_digest:
        raise CheckpointCompatibilityError(
            f"Source region schema digest mismatch: {compat_sec.get('region_schema_digest')} != {current_region_digest}"
        )
    if compat_sec.get("active_law_digest") != current_law_digest:
        raise CheckpointCompatibilityError(
            f"Source active law digest mismatch: {compat_sec.get('active_law_digest')} != {current_law_digest}"
        )
    if compat_sec.get("assembly_policy_digest") != current_policy_digest:
        raise CheckpointCompatibilityError(
            f"Source assembly policy digest mismatch: {compat_sec.get('assembly_policy_digest')} != {current_policy_digest}"
        )
    if compat_sec.get("combined_semantics_digest") != current_combined_digest:
        raise CheckpointCompatibilityError(
            f"Source combined semantics digest mismatch: recorded {compat_sec.get('combined_semantics_digest')} != computed {current_combined_digest}"
        )


def migrate_schema_1_1_to_1_1_1(
    old_checkpoint: dict[str, Any],
    policy: AssemblyPolicy | None = None,
) -> tuple[dict[str, Any], MigrationReport]:
    """Migrates a canonical v1.1 checkpoint to v1.1.1 by reconstructing formation candidate storage keys.

    Validates source integrity and source contract BEFORE any mutation or transformation (R0-C02).
    """
    # Source validation MUST PASS before any transformation (R0-C02 Governing Rule)
    validate_schema_1_1_source(old_checkpoint, policy=policy)

    checkpoint = copy.deepcopy(old_checkpoint)
    pending_ev = checkpoint.get("persistent_state", {}).get("pending_structural_evidence", {})
    old_candidates = pending_ev.get("pending_candidates", [])

    seen_keys: dict[str, dict[str, Any]] = {}
    migrated_candidates = []

    for cand in old_candidates:
        cid = cand.get("candidate_id")
        ctx = cand.get("context_signature")
        derived_key = f"{cid}:ctx_{ctx or 'default'}"

        if derived_key in seen_keys:
            existing = seen_keys[derived_key]
            c1 = {k: v for k, v in cand.items() if k != "storage_key"}
            c2 = {k: v for k, v in existing.items() if k != "storage_key"}
            if c1 != c2:
                raise LegacyMigrationError(
                    f"Conflict migrating schema 1.1 formation candidate: multiple records derived storage_key '{derived_key}' with conflicting payloads"
                )
            continue

        cand_with_key = dict(cand)
        cand_with_key["storage_key"] = derived_key
        seen_keys[derived_key] = cand_with_key
        migrated_candidates.append(cand_with_key)

    migrated_candidates.sort(key=lambda c: c["storage_key"])
    pending_ev["pending_candidates"] = migrated_candidates

    checkpoint["schema"]["checkpoint_schema_version"] = "1.1.1"
    checkpoint["schema"]["runtime_contract_version"] = "1.1.1"

    persistent_payload = checkpoint["persistent_state"]
    new_state_digest = compute_checkpoint_state_digest(persistent_payload)
    checkpoint["integrity"]["checkpoint_state_digest"] = new_state_digest

    report = MigrationReport(
        source_schema="1.1",
        target_schema="1.1.1",
        restored_durable_fields=["all_durable_cognition", "pending_structural_evidence"],
        reset_transient_fields=[],
        ignored_runtime_configuration=[],
        unrecoverable_legacy_state=[],
        compatibility_result="COMPATIBLE",
        migration_result="SUCCESS",
        diagnostic_notes=[
            "source integrity: VERIFIED",
            "source runtime contract: 1.1",
            "target runtime contract: 1.1.1",
            "formation storage keys: reconstructed deterministically from candidate_id and context_signature.",
            "historical ordered-sequence limitation: pre-serialization ordering lost under schema 1.1 cannot be reconstructed; serialized sequence order is authoritative source data.",
        ],
    )
    if "diagnostic_metadata" not in checkpoint:
        checkpoint["diagnostic_metadata"] = {}
    checkpoint["diagnostic_metadata"]["migration_report"] = report.to_dict()
    checkpoint["diagnostic_metadata"]["provenance"] = "MIGRATED_FROM_V1.1"
    checkpoint["diagnostic_metadata"]["source_schema"] = "1.1"

    return checkpoint, report


def migrate_legacy_v1_checkpoint(
    legacy_data: dict[str, Any],
    runtime_enable_prediction: bool = False,
) -> tuple[dict[str, Any], MigrationReport]:
    """Migrates a legacy v1.0 checkpoint to canonical v1.1.1 persistent state."""
    validate_legacy_v1_source(legacy_data)

    restored_durable = [
        "logical_time", "durable_node_fields", "durable_edge_fields",
        "contradictions", "concept_hits", "drives", "hypotheses",
        "structural_assemblies",
    ]
    reset_transient = [
        "node_activation_A", "node_t_spawn", "node_episode",
        "dmg", "goal", "outcome", "prediction_pool", "prediction_sources",
    ]
    ignored_config = [
        "enable_prediction (caller runtime configuration retained)",
    ]
    unrecoverable_state = [
        "RFC11 pending structural evidence was not serialized by the legacy format and cannot be recovered.",
    ]

    nodes_list = []
    for nid in sorted(legacy_data.get("nodes", {}).keys()):
        ndata = legacy_data["nodes"][nid]
        nodes_list.append({
            "N_total": ndata.get("N_total", 0),
            "U": float(ndata.get("U", 0.0)),
            "V": float(ndata.get("V", 0.0)),
            "head": ndata.get("head"),
            "is_concept": bool(ndata.get("is_concept", False)),
            "is_intrinsic": bool(ndata.get("is_intrinsic", False)),
            "members": sorted(ndata.get("members", [])),
            "nid": str(ndata["nid"]),
            "region": str(ndata["region"]),
        })

    edges_list = []
    for edata in legacy_data.get("edges", []):
        ctx_hits = edata.get("ctx_hits", {})
        sorted_ctx_hits = {k: ctx_hits[k] for k in sorted(ctx_hits.keys())}
        edges_list.append({
            "M_max": float(edata.get("M_max", 1.0)),
            "S": float(edata.get("S", 0.0)),
            "W": float(edata.get("W", 0.0)),
            "contexts": sorted(edata.get("contexts", [])),
            "ctx_hits": sorted_ctx_hits,
            "dst": str(edata["dst"]),
            "fwd": bool(edata.get("fwd", False)),
            "g": edata.get("g"),
            "is_intrinsic": bool(edata.get("is_intrinsic", False)),
            "k_fail": int(edata.get("k_fail", 0)),
            "kind": str(edata.get("kind", "assoc")),
            "lag": float(edata.get("lag", 0.0)),
            "n": int(edata.get("n", 0)),
            "origin": str(edata.get("origin", "")),
            "src": str(edata["src"]),
            "t_created": int(edata.get("t_created", 0)),
            "t_last_update": int(edata.get("t_last_update", 0)),
            "tagged": bool(edata.get("tagged", False)),
            "valence": float(edata.get("valence", 0.0)),
        })
    edges_list.sort(key=lambda e: (e["src"], e["dst"]))

    sorted_x = {k: sorted(legacy_data.get("X", {}).get(k, [])) for k in sorted(legacy_data.get("X", {}).keys())}
    sorted_concept_hits = {k: int(legacy_data.get("concept_hits", {}).get(k, 0)) for k in sorted(legacy_data.get("concept_hits", {}).keys())}
    sorted_drives = {k: legacy_data.get("drives", {}).get(k) for k in sorted(legacy_data.get("drives", {}).keys())}
    hypotheses = copy.deepcopy(legacy_data.get("hypotheses", []))

    assemblies_list = []
    for adata in legacy_data.get("assemblies", []):
        member_edges_sorted = sorted([[pair[0], pair[1]] for pair in adata.get("member_edges", [])])
        # parent_assemblies order is preserved per C01-05
        assemblies_list.append({
            "assembly_id": adata["assembly_id"],
            "is_retired": bool(adata.get("is_retired", False)),
            "member_edges": member_edges_sorted,
            "origin_signature": str(adata.get("origin_signature", "")),
            "parent_assemblies": list(adata.get("parent_assemblies", ())),
            "predecessor_version": adata.get("predecessor_version"),
            "version": int(adata["version"]),
        })
    assemblies_list.sort(key=lambda a: (a["assembly_id"], a["version"]))

    pending_evidence = {
        "pending_candidates": [],
        "pending_growth": [],
        "pending_merge": [],
    }

    persistent_payload = {
        "assemblies": assemblies_list,
        "concept_hits": sorted_concept_hits,
        "contradictions": sorted_x,
        "drives": sorted_drives,
        "edges": edges_list,
        "hypotheses": hypotheses,
        "logical_time": int(legacy_data.get("t", 0)),
        "nodes": nodes_list,
        "pending_structural_evidence": pending_evidence,
    }

    assert_finite_numbers(persistent_payload, "migrated_persistent_state")
    state_digest = compute_checkpoint_state_digest(persistent_payload)

    report = MigrationReport(
        source_schema="1.0",
        target_schema="1.1.1",
        restored_durable_fields=restored_durable,
        reset_transient_fields=reset_transient,
        ignored_runtime_configuration=ignored_config,
        unrecoverable_legacy_state=unrecoverable_state,
        compatibility_result="COMPATIBLE",
        migration_result="SUCCESS",
        diagnostic_notes=["RFC11 pending structural evidence was not serialized by v1.0."],
    )

    region_digest = compute_region_schema_digest()
    law_digest = compute_active_law_digest()
    policy_digest = compute_assembly_policy_digest()
    combined_digest = compute_combined_semantics_digest(region_digest, law_digest, policy_digest, "1.0")

    migrated_checkpoint = {
        "compatibility": {
            "active_law_digest": law_digest,
            "assembly_policy_digest": policy_digest,
            "combined_semantics_digest": combined_digest,
            "region_schema_digest": region_digest,
        },
        "diagnostic_metadata": {
            "migration_report": report.to_dict(),
            "provenance": "MIGRATED_FROM_V1.0",
            "source_schema": "1.0",
        },
        "integrity": {
            "checkpoint_state_digest": state_digest,
        },
        "persistent_state": persistent_payload,
        "schema": {
            "checkpoint_schema_version": "1.1.1",
            "cognitive_semantics_version": "1.0",
            "runtime_contract_version": "1.1.1",
        },
    }
    return migrated_checkpoint, report


# ─────────────────────────────────────────────────────────── 11. Canonical Two-Phase Restore
def _restore_graph_from_persistent_payload(
    persistent_payload: dict[str, Any],
    policy: AssemblyPolicy | None = None,
    enable_prediction: bool = False,
) -> tuple[CognitiveGraph, AssemblyManager]:
    """Constructs a fresh CognitiveGraph and AssemblyManager from persistent payload."""
    new_graph = CognitiveGraph(
        t=persistent_payload.get("logical_time", 0),
        enable_prediction=enable_prediction,
        concept_hits=dict(persistent_payload.get("concept_hits", {})),
        drives=dict(persistent_payload.get("drives", {})),
        hypotheses=copy.deepcopy(persistent_payload.get("hypotheses", [])),
        dmg=0.0,
        goal=None,
        outcome=0.0,
        log=[],
        prediction_pool={},
        prediction_sources={},
    )

    # Restore contradictions
    for k, v in persistent_payload["contradictions"].items():
        new_graph.X[k] = set(v)

    # Restore Nodes (Duplicate Node rejection C03-05 / C03-I06)
    seen_nids: set[str] = set()
    for ndata in persistent_payload["nodes"]:
        nid = ndata["nid"]
        if nid in seen_nids:
            raise CheckpointValidationError(f"Duplicate Node ID detected during restore: '{nid}'")
        seen_nids.add(nid)
        node = Node(
            nid=nid,
            region=ndata["region"],
            is_concept=ndata.get("is_concept", False),
            members=set(ndata.get("members", [])),
            U=float(ndata.get("U", 0.0)),
            V=float(ndata.get("V", 0.0)),
            head=ndata.get("head"),
            is_intrinsic=bool(ndata.get("is_intrinsic", False)),
            N_total=int(ndata.get("N_total", 0)),
            A=0.0,
            t_spawn=-999,
            episode=None,
        )
        new_graph.nodes[node.nid] = node

    # Restore Edges (Duplicate Edge rejection C03-05 / C03-I07)
    seen_edges: set[tuple[str, str]] = set()
    for edata in persistent_payload["edges"]:
        pair = (edata["src"], edata["dst"])
        if pair in seen_edges:
            raise CheckpointValidationError(f"Duplicate Edge ID detected during restore: {pair}")
        seen_edges.add(pair)
        edge = Edge(
            src=edata["src"],
            dst=edata["dst"],
            W=float(edata.get("W", 0.0)),
            kind=edata.get("kind", "assoc"),
            origin=edata.get("origin", ""),
            t_created=int(edata.get("t_created", 0)),
            t_last_update=int(edata.get("t_last_update", 0)),
            n=int(edata.get("n", 0)),
            M_max=float(edata.get("M_max", 1.0)),
            S=float(edata.get("S", 0.0)),
            tagged=bool(edata.get("tagged", False)),
            valence=float(edata.get("valence", 0.0)),
            lag=float(edata.get("lag", 0.0)),
            fwd=bool(edata.get("fwd", False)),
            g=edata.get("g"),
            contexts=set(edata.get("contexts", [])),
            ctx_hits=dict(edata.get("ctx_hits", {})),
            is_intrinsic=bool(edata.get("is_intrinsic", False)),
            k_fail=int(edata.get("k_fail", 0)),
        )
        new_graph.edges[(edge.src, edge.dst)] = edge
        new_graph.out_adj.setdefault(edge.src, {})[edge.dst] = edge
        new_graph.in_adj.setdefault(edge.dst, {})[edge.src] = edge

    # Construct NEW AssemblyManager
    effective_policy = policy or AssemblyPolicy()
    new_mgr = AssemblyManager(new_graph, effective_policy)

    # Restore Assemblies (Duplicate Assembly version rejection C03-05 / C03-I08)
    seen_assemblies: set[tuple[str, int]] = set()
    for adata in persistent_payload["assemblies"]:
        asm_ver_key = (adata["assembly_id"], adata["version"])
        if asm_ver_key in seen_assemblies:
            raise CheckpointValidationError(
                f"Duplicate Assembly version detected during restore: {asm_ver_key}"
            )
        seen_assemblies.add(asm_ver_key)
        asm = StructuralAssembly(
            assembly_id=adata["assembly_id"],
            version=adata["version"],
            member_edges=frozenset((pair[0], pair[1]) for pair in adata["member_edges"]),
            origin_signature=adata["origin_signature"],
            predecessor_version=adata.get("predecessor_version"),
            parent_assemblies=tuple(adata.get("parent_assemblies", ())),
            is_retired=adata.get("is_retired", False),
        )
        new_mgr.assemblies.setdefault(asm.assembly_id, []).append(asm)

    # Restore Pending Evidence
    pending_ev = persistent_payload["pending_structural_evidence"]

    # Formation candidates (C03-05 / C03-06)
    seen_formation_keys: set[str] = set()
    for cdata in pending_ev["pending_candidates"]:
        storage_key = cdata.get("storage_key")
        candidate_id = cdata.get("candidate_id")
        context_signature = cdata.get("context_signature")
        expected_key = f"{candidate_id}:ctx_{context_signature or 'default'}"
        if storage_key != expected_key:
            raise CheckpointValidationError(
                f"Invalid formation candidate storage_key: recorded '{storage_key}' != expected '{expected_key}'"
            )
        if storage_key in seen_formation_keys:
            raise CheckpointValidationError(
                f"Duplicate formation candidate storage_key detected during restore: '{storage_key}'"
            )
        seen_formation_keys.add(storage_key)

        raw_edges = cdata.get("edges", [])
        edge_pairs = [(pair[0], pair[1]) for pair in raw_edges]
        expected_cid = canonical_assembly_id(edge_pairs)
        if candidate_id != expected_cid:
            raise CheckpointValidationError(
                f"Formation candidate_id '{candidate_id}' does not match canonical_assembly_id '{expected_cid}'"
            )
        k_min = effective_policy.K_ASM_MIN
        k_max = effective_policy.K_ASM_MEM
        if not (k_min <= len(edge_pairs) <= k_max):
            raise CheckpointValidationError(
                f"Formation candidate edge count {len(edge_pairs)} outside bounds [{k_min}, {k_max}]"
            )
        for pair in edge_pairs:
            if pair not in new_graph.edges:
                raise StructuralReferentialIntegrityError(
                    f"Formation candidate '{storage_key}' references edge {pair} missing from live graph.edges"
                )

        cand_votes = set(cdata.get("root_votes", []))
        cand = FormationCandidate(
            candidate_id=candidate_id,
            edges=frozenset(edge_pairs),
            context_signature=context_signature,
            root_votes=cand_votes,
            created_t=cdata.get("created_t", 0),
        )
        new_mgr.pending_candidates[storage_key] = cand

    # Growth candidates (C03-05 / C03-06)
    seen_growth_keys: set[tuple[str, tuple[str, str], str | None]] = set()
    for gdata in pending_ev["pending_growth"]:
        aid = gdata.get("assembly_id")
        raw_edge = gdata.get("new_edge")
        if not isinstance(raw_edge, (list, tuple)) or len(raw_edge) != 2:
            raise CheckpointValidationError("Growth candidate new_edge must be a 2-element list/tuple")
        pair = (raw_edge[0], raw_edge[1])
        growth_key = (aid, pair, gdata.get("context"))
        if growth_key in seen_growth_keys:
            raise CheckpointValidationError(
                f"Duplicate growth candidate key detected during restore: {growth_key}"
            )
        seen_growth_keys.add(growth_key)

        if aid not in new_mgr.assemblies:
            raise StructuralReferentialIntegrityError(
                f"Pending growth references non-existent parent assembly '{aid}'"
            )
        latest = new_mgr.assemblies[aid][-1]
        if latest.is_retired:
            raise StructuralReferentialIntegrityError(
                f"Pending growth references retired parent assembly '{aid}'"
            )
        if pair in latest.member_edges:
            raise CheckpointValidationError(
                f"Growth candidate new_edge {pair} is already a member of parent assembly '{aid}'"
            )
        if pair not in new_graph.edges:
            raise StructuralReferentialIntegrityError(
                f"Pending growth references new_edge {pair} missing from live graph.edges"
            )

        g_votes = set(gdata.get("root_votes", []))
        new_mgr.pending_growth[growth_key] = g_votes

    # Merge candidates (C03-05 / C03-06)
    seen_merge_keys: set[tuple[frozenset[str], str | None]] = set()
    for mdata in pending_ev["pending_merge"]:
        raw_parents = mdata.get("parent_assembly_ids", [])
        if not isinstance(raw_parents, (list, tuple)) or len(raw_parents) != 2 or len(set(raw_parents)) != 2:
            raise CheckpointValidationError(
                f"Merge candidate must have exactly two distinct parent assemblies, got {raw_parents}"
            )
        parents = frozenset(raw_parents)
        merge_key = (parents, mdata.get("context"))
        if merge_key in seen_merge_keys:
            raise CheckpointValidationError(
                f"Duplicate merge candidate key detected during restore: {merge_key}"
            )
        seen_merge_keys.add(merge_key)

        for pid in parents:
            if pid not in new_mgr.assemblies:
                raise StructuralReferentialIntegrityError(
                    f"Pending merge references non-existent parent assembly '{pid}'"
                )
            latest = new_mgr.assemblies[pid][-1]
            if latest.is_retired:
                raise StructuralReferentialIntegrityError(
                    f"Pending merge references retired parent assembly '{pid}'"
                )

        m_votes = set(mdata.get("root_votes", []))
        new_mgr.pending_merge[merge_key] = m_votes

    new_mgr.rebuild_indexes()
    new_graph._assembly_manager = new_mgr

    validate_structural_referential_integrity(new_graph, new_mgr)

    # Assert Phase-II engines are None
    assert new_graph._representation_engine is None
    assert new_graph._completion_engine is None
    assert new_graph._generation_engine is None
    assert new_graph._recurrent_engine is None
    assert new_graph._loop_engine is None

    # Assert AssemblyManager bound to new graph
    assert new_mgr.graph is new_graph

    return new_graph, new_mgr



def _prepare_restored_cognitive_graph(
    filepath: str | pathlib.Path,
    policy: AssemblyPolicy | None = None,
    enable_prediction: bool | None = None,
) -> tuple[CognitiveGraph, MigrationReport | None]:
    """Phase A: Internal isolated restore into a NEW CognitiveGraph.

    Constructs a fresh graph and validates all schema, digests, compatibility, and referential constraints.
    Does NOT transition or manipulate lifecycle guards (caller manages guard).
    """
    path = pathlib.Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {path}")

    raw_data = load_checkpoint_json(path)

    # Strict Source-Family Recognition (C03-01 / C03-I01)
    if not isinstance(raw_data, dict):
        raise CheckpointSchemaError("Checkpoint root must be a JSON object (dict)")

    has_schema = "schema" in raw_data
    schema_val = raw_data.get("schema")

    migration_report: MigrationReport | None = None
    if raw_data.get("version") == "1.0" and not has_schema:
        pred_setting = False if enable_prediction is None else enable_prediction
        checkpoint_data, migration_report = migrate_legacy_v1_checkpoint(raw_data, pred_setting)
    elif has_schema and isinstance(schema_val, dict) and schema_val.get("checkpoint_schema_version") == "1.1":
        checkpoint_data, migration_report = migrate_schema_1_1_to_1_1_1(raw_data, policy=policy)
    elif has_schema and isinstance(schema_val, dict) and schema_val.get("checkpoint_schema_version") in ("1.1.1", "1.2.0"):
        checkpoint_data = raw_data
    else:
        raise CheckpointSchemaError(
            "Unrecognized checkpoint family. Expected schema.checkpoint_schema_version in ('1.2.0', '1.1.1', '1.1') "
            "or explicit legacy version == '1.0' without schema."
        )

    cur_schema_label = schema_val.get("checkpoint_schema_version") if (has_schema and isinstance(schema_val, dict)) else "1.1.1"
    validate_canonical_persistent_shape(checkpoint_data, schema_label=cur_schema_label)

    # Validate schema header
    schema_sec = checkpoint_data["schema"]
    schema_ver = schema_sec.get("checkpoint_schema_version")
    contract_ver = schema_sec.get("runtime_contract_version")
    cog_sem_ver = schema_sec.get("cognitive_semantics_version")

    if schema_ver not in ("1.1.1", "1.2.0"):
        raise CheckpointSchemaError(
            f"Unsupported checkpoint_schema_version: '{schema_ver}'"
        )
    if contract_ver != schema_ver:
        raise CheckpointCompatibilityError(
            f"Incompatible runtime_contract_version: '{contract_ver}'"
        )
    if cog_sem_ver != "1.0":
        raise CheckpointCompatibilityError(
            f"Incompatible cognitive_semantics_version: '{cog_sem_ver}'"
        )

    # Validate numeric finiteness
    assert_finite_numbers(checkpoint_data, "checkpoint_root")

    # Validate semantic compatibility
    compat_sec = checkpoint_data.get("compatibility", {})
    current_region_digest = compute_region_schema_digest()
    current_law_digest = compute_active_law_digest()
    current_policy_digest = compute_assembly_policy_digest(policy)
    current_combined_digest = compute_combined_semantics_digest(
        region_digest=current_region_digest,
        law_digest=current_law_digest,
        policy_digest=current_policy_digest,
        cognitive_semantics_version=cog_sem_ver or "1.0",
    )

    if compat_sec.get("region_schema_digest") != current_region_digest:
        raise CheckpointCompatibilityError(
            f"Region schema digest mismatch: {compat_sec.get('region_schema_digest')} != {current_region_digest}"
        )
    if compat_sec.get("active_law_digest") != current_law_digest:
        raise CheckpointCompatibilityError(
            f"Active law digest mismatch: {compat_sec.get('active_law_digest')} != {current_law_digest}"
        )
    if compat_sec.get("assembly_policy_digest") != current_policy_digest:
        raise CheckpointCompatibilityError(
            f"Assembly policy digest mismatch: {compat_sec.get('assembly_policy_digest')} != {current_policy_digest}"
        )
    # Explicit validation of recomputed combined_semantics_digest (C01-04)
    if compat_sec.get("combined_semantics_digest") != current_combined_digest:
        raise CheckpointCompatibilityError(
            f"Combined semantics digest mismatch: recorded {compat_sec.get('combined_semantics_digest')} != computed {current_combined_digest}"
        )

    # Validate state integrity digest
    persistent_payload = checkpoint_data.get("persistent_state", {})
    expected_state_digest = compute_checkpoint_state_digest(persistent_payload)
    recorded_state_digest = checkpoint_data.get("integrity", {}).get("checkpoint_state_digest")
    if recorded_state_digest != expected_state_digest:
        raise CheckpointIntegrityError(
            f"Checkpoint state digest mismatch: recorded {recorded_state_digest} != computed {expected_state_digest}"
        )

    # ──────────────── Phase A: Construct NEW CognitiveGraph
    pred_config = False if enable_prediction is None else enable_prediction
    new_graph, _ = _restore_graph_from_persistent_payload(
        persistent_payload=persistent_payload,
        policy=policy,
        enable_prediction=pred_config,
    )
    return new_graph, migration_report


def restore_cognitive_checkpoint(
    filepath: str | pathlib.Path,
    policy: AssemblyPolicy | None = None,
    enable_prediction: bool | None = None,
    guard: RuntimeLifecycleGuard | None = None,
) -> tuple[CognitiveGraph, MigrationReport | None]:
    """Standalone restore into a NEW CognitiveGraph under lifecycle guard."""
    active_guard = guard or RuntimeLifecycleGuard()
    with active_guard.restoring():
        return _prepare_restored_cognitive_graph(
            filepath=filepath,
            policy=policy,
            enable_prediction=enable_prediction,
        )


# ─────────────────────────────────────────────────────────── 12. Runtime Root Container
class RuntimeRoot:
    """Minimal host-side engineering container for the authoritative runtime graph.

    Owns no cognition, no learning, no prompt classification, no agent behavior.
    Enforces atomic two-phase restore and lifecycle state guarding.
    """

    def __init__(
        self,
        graph: CognitiveGraph,
        policy: AssemblyPolicy | None = None,
        enable_prediction: bool = False,
        guard: RuntimeLifecycleGuard | None = None,
    ) -> None:
        self.graph = graph
        self.enable_prediction = enable_prediction
        self.guard = guard or RuntimeLifecycleGuard()

        # Policy Provenance Rule (Section 9)
        if policy is not None:
            if graph._assembly_manager is not None and not policies_semantically_equal(graph._assembly_manager.policy, policy):
                raise CheckpointCompatibilityError(
                    "Explicit policy differs from graph AssemblyManager policy"
                )
            self.policy = policy
        elif graph._assembly_manager is not None:
            self.policy = graph._assembly_manager.policy
        else:
            self.policy = AssemblyPolicy()

    def save_checkpoint(
        self,
        filepath: str | pathlib.Path,
        diagnostic_metadata: dict[str, Any] | None = None,
    ) -> str:
        """Saves a canonical cognitive checkpoint under the lifecycle guard."""
        return save_cognitive_checkpoint(
            graph=self.graph,
            filepath=filepath,
            policy=self.policy,
            guard=self.guard,
            diagnostic_metadata=diagnostic_metadata,
        )

    def restore_checkpoint(
        self,
        filepath: str | pathlib.Path,
        _on_pre_swap: Any | None = None,
    ) -> tuple[CognitiveGraph, MigrationReport | None]:
        """Atomic two-phase restore.

        Phase A: Prepares and validates a new CognitiveGraph in isolation.
        Phase B: Commits by swapping self.graph to the new graph while still RESTORING.
        If Phase A fails, self.graph remains object-identical and guard returns to IDLE.
        """
        with self.guard.restoring():
            new_graph, report = _prepare_restored_cognitive_graph(
                filepath=filepath,
                policy=self.policy,
                enable_prediction=self.enable_prediction,
            )
            if _on_pre_swap is not None:
                _on_pre_swap(self.guard.state)
            # Root swap occurs strictly while guard.state is RESTORING (C01-03 / C01-I08)
            assert self.guard.state == RuntimeLifecycleState.RESTORING
            self.graph = new_graph
            return self.graph, report


# ─────────────────────────────────────────────────────────── R1 Checkpoint 1.2.0 Functions
def build_canonical_r1_checkpoint(
    graph: CognitiveGraph,
    ledger: CausalCommitLedger,
    observation_protocol_version: str,
    policy: AssemblyPolicy | None = None,
    diagnostic_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Constructs the canonical top-level DGCA_COGNITIVE_CHECKPOINT v1.2.0 structure (Section 61)."""
    if not isinstance(observation_protocol_version, str) or not observation_protocol_version.strip():
        raise CausalIdentityValidationError(
            "Canonical R1 checkpoint requires an explicit non-empty observation_protocol_version"
        )
    pol = resolve_effective_policy(graph, policy)

    # 1. Referential integrity check
    validate_structural_referential_integrity(graph, graph._assembly_manager)

    # 2. Extract canonical persistent payload (exact R0 persistent payload unchanged)
    persistent_payload = extract_canonical_persistent_payload(graph, pol)

    # 3. Compute digests
    state_digest = compute_checkpoint_state_digest(persistent_payload)
    region_digest = compute_region_schema_digest()
    law_digest = compute_active_law_digest()
    policy_digest = compute_assembly_policy_digest(pol)
    combined_digest = compute_combined_semantics_digest(region_digest, law_digest, policy_digest, "1.0")

    # 4. R1 Protocol digests
    identity_protocol_digest = CAUSAL_IDENTITY_PROTOCOL_DIGEST
    obs_protocol_digest = compute_observation_protocol_digest(observation_protocol_version)

    # 5. Causal provenance payload & validation (PIR02-B03, PIR02-B08)
    causal_provenance_payload = ledger.to_dict()
    from .causal_identity import validate_causal_provenance_state
    validate_causal_provenance_state(
        causal_provenance_state=causal_provenance_payload,
        checkpoint_state_digest=state_digest,
        checkpoint_observation_protocol_version=observation_protocol_version,
    )
    provenance_digest = compute_causal_provenance_digest(causal_provenance_payload)

    # 6. Structured bundle digest
    bundle_digest = compute_checkpoint_bundle_digest(
        checkpoint_state_digest=state_digest,
        causal_provenance_digest=provenance_digest,
        combined_semantics_digest=combined_digest,
        causal_identity_protocol_digest=identity_protocol_digest,
        observation_protocol_digest=obs_protocol_digest,
        causal_provenance_epoch=causal_provenance_payload["causal_provenance_epoch"],
    )

    metadata = {
        "provenance": "DGCA_R1_CANONICAL",
        "source_schema": "1.2.0",
    }
    if diagnostic_metadata:
        metadata.update(diagnostic_metadata)

    return {
        "checkpoint_type": "DGCA_COGNITIVE_CHECKPOINT",
        "compatibility": {
            "active_law_digest": law_digest,
            "assembly_policy_digest": policy_digest,
            "causal_identity_protocol_digest": identity_protocol_digest,
            "combined_semantics_digest": combined_digest,
            "observation_protocol_digest": obs_protocol_digest,
            "region_schema_digest": region_digest,
        },
        "diagnostic_metadata": metadata,
        "integrity": {
            "causal_provenance_digest": provenance_digest,
            "checkpoint_bundle_digest": bundle_digest,
            "checkpoint_state_digest": state_digest,
        },
        "persistent_state": persistent_payload,
        "causal_provenance_state": causal_provenance_payload,
        "schema": {
            "causal_identity_protocol_version": "1.0",
            "checkpoint_schema_version": "1.2.0",
            "cognitive_semantics_version": "1.0",
            "observation_protocol_version": observation_protocol_version,
            "runtime_contract_version": "1.2.0",
        },
    }


def save_canonical_r1_checkpoint(
    runtime_root: CanonicalR1RuntimeRoot,
    filepath: str | pathlib.Path,
    diagnostic_metadata: dict[str, Any] | None = None,
) -> str:
    """Saves a canonical schema 1.2.0 cognitive checkpoint bundle using atomic file replace.

    Returns the bundle digest of the saved checkpoint.
    """
    if runtime_root.causal_runtime_health != CausalRuntimeHealth.HEALTHY:
        raise CausalRuntimeFailStopError(
            "Runtime is in MUTATION_FAILED fail-stop state. Canonical save is forbidden."
        )
    if runtime_root.canonical_lineage_state != CanonicalLineageState.VALID:
        raise CausalLineageInvalidatedError(
            "Canonical lineage is invalidated by untracked persistent mutation. Canonical save is forbidden."
        )

    dest_path = pathlib.Path(filepath).resolve()
    dest_dir = dest_path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    active_guard = runtime_root.guard
    with active_guard.checkpointing():
        checkpoint_data = build_canonical_r1_checkpoint(
            graph=runtime_root.graph,
            ledger=runtime_root.ledger,
            observation_protocol_version=runtime_root.observation_protocol_version,
            policy=runtime_root.assembly_policy,
            diagnostic_metadata=diagnostic_metadata,
        )
        canonical_bytes = json.dumps(
            checkpoint_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        _atomic_replace_file(dest_path, canonical_bytes)

    return checkpoint_data["integrity"]["checkpoint_bundle_digest"]


def migrate_schema_1_1_1_to_1_2_0(
    old_checkpoint: dict[str, Any],
    target_observation_protocol_version: str,
    policy: AssemblyPolicy | None = None,
) -> tuple[dict[str, Any], MigrationReport]:
    """Migrates a canonical v1.1.1 checkpoint to v1.2.0 by binding empty causal provenance (Section 68)."""
    if not isinstance(target_observation_protocol_version, str) or not target_observation_protocol_version.strip():
        raise CausalIdentityValidationError(
            "Migrating checkpoint to 1.2.0 requires an explicit target observation_protocol_version"
        )

    # 1. Source verification
    validate_canonical_persistent_shape(old_checkpoint, schema_label="1.1.1")
    validate_semantic_compatibility(
        old_checkpoint,
        policy=policy,
        expected_schema_version="1.1.1",
        expected_contract_version="1.1.1",
    )

    persistent_payload = old_checkpoint["persistent_state"]
    assert_finite_numbers(persistent_payload, "migration_source_persistent_state")
    state_digest = compute_checkpoint_state_digest(persistent_payload)
    if old_checkpoint["integrity"]["checkpoint_state_digest"] != state_digest:
        raise CheckpointIntegrityError("Source checkpoint_state_digest does not match persistent_state")

    # 2. Construct 1.2.0 metadata and compatibility
    checkpoint = copy.deepcopy(old_checkpoint)
    combined_digest = checkpoint["compatibility"]["combined_semantics_digest"]

    identity_protocol_digest = CAUSAL_IDENTITY_PROTOCOL_DIGEST
    obs_protocol_digest = compute_observation_protocol_digest(target_observation_protocol_version)

    from .causal_identity import create_migrated_r1_provenance_epoch
    causal_provenance_epoch = create_migrated_r1_provenance_epoch(state_digest).to_dict()
    causal_provenance_state = {
        "causal_provenance_epoch": causal_provenance_epoch,
        "committed_event_bindings": {},
        "committed_transactions": {},
    }
    provenance_digest = compute_causal_provenance_digest(causal_provenance_state)

    bundle_digest = compute_checkpoint_bundle_digest(
        checkpoint_state_digest=state_digest,
        causal_provenance_digest=provenance_digest,
        combined_semantics_digest=combined_digest,
        causal_identity_protocol_digest=identity_protocol_digest,
        observation_protocol_digest=obs_protocol_digest,
        causal_provenance_epoch=causal_provenance_epoch,
    )

    report = MigrationReport(
        source_schema="1.1.1",
        target_schema="1.2.0",
        restored_durable_fields=["persistent_state"],
        reset_transient_fields=[],
        ignored_runtime_configuration=[],
        unrecoverable_legacy_state=["pre_r1_causal_provenance"],
        compatibility_result="COMPATIBLE",
        migration_result="SUCCESS",
        diagnostic_notes=[
            "source integrity: VERIFIED",
            "source schema: 1.1.1",
            "target schema: 1.2.0",
            "target observation_protocol_version: " + target_observation_protocol_version,
            "Pre-R1 persistent mutation causal commit history was not recorded and cannot be reconstructed.",
        ],
    )

    checkpoint["checkpoint_type"] = "DGCA_COGNITIVE_CHECKPOINT"
    checkpoint["schema"] = {
        "causal_identity_protocol_version": "1.0",
        "checkpoint_schema_version": "1.2.0",
        "cognitive_semantics_version": "1.0",
        "observation_protocol_version": target_observation_protocol_version,
        "runtime_contract_version": "1.2.0",
    }
    checkpoint["compatibility"]["causal_identity_protocol_digest"] = identity_protocol_digest
    checkpoint["compatibility"]["observation_protocol_digest"] = obs_protocol_digest
    checkpoint["causal_provenance_state"] = causal_provenance_state
    checkpoint["integrity"]["causal_provenance_digest"] = provenance_digest
    checkpoint["integrity"]["checkpoint_bundle_digest"] = bundle_digest
    if "diagnostic_metadata" not in checkpoint:
        checkpoint["diagnostic_metadata"] = {}
    checkpoint["diagnostic_metadata"]["migration_report"] = report.to_dict()
    existing_chain = checkpoint["diagnostic_metadata"].get("migration_chain")
    if existing_chain and isinstance(existing_chain, list):
        checkpoint["diagnostic_metadata"]["migration_chain"] = existing_chain + [report.to_dict()]
    else:
        checkpoint["diagnostic_metadata"]["migration_chain"] = [report.to_dict()]
    checkpoint["diagnostic_metadata"]["provenance"] = "MIGRATED_TO_1.2.0"

    return checkpoint, report


def restore_canonical_r1_checkpoint(
    filepath: str | pathlib.Path,
    expected_observation_protocol_version: str | None = None,
    policy: AssemblyPolicy | None = None,
    enable_prediction: bool | None = None,
    guard: RuntimeLifecycleGuard | None = None,
    _on_pre_swap: Any | None = None,
) -> tuple[CanonicalR1RuntimeRoot, MigrationReport | None]:
    """Atomic restore into a NEW CanonicalR1RuntimeRoot under lifecycle guard (Section 67)."""
    active_guard = guard or RuntimeLifecycleGuard()
    with active_guard.restoring():
        path = pathlib.Path(filepath).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {path}")

        raw_data = load_checkpoint_json(path)
        if not isinstance(raw_data, dict):
            raise CheckpointSchemaError("Checkpoint root must be a JSON object (dict)")

        has_schema = "schema" in raw_data
        schema_val = raw_data.get("schema")
        migration_report: MigrationReport | None = None

        if raw_data.get("version") == "1.0" and not has_schema:
            if not expected_observation_protocol_version or not expected_observation_protocol_version.strip():
                raise CausalIdentityValidationError(
                    "Migrating pre-R1 v1.0 checkpoint to 1.2.0 requires an explicit target observation_protocol_version"
                )
            pred_setting = False if enable_prediction is None else enable_prediction
            mid_111, rep1 = migrate_legacy_v1_checkpoint(raw_data, pred_setting)
            checkpoint_data, rep2 = migrate_schema_1_1_1_to_1_2_0(
                mid_111,
                target_observation_protocol_version=expected_observation_protocol_version,
                policy=policy,
            )
            # PIR02-B09: Preserve chained migration reports and all accumulated loss disclosures
            combined_notes = list(rep1.diagnostic_notes) + list(rep2.diagnostic_notes)
            combined_unrec = list(rep1.unrecoverable_legacy_state) + list(rep2.unrecoverable_legacy_state)
            combined_report = MigrationReport(
                source_schema="1.0",
                target_schema="1.2.0",
                restored_durable_fields=["persistent_state"],
                reset_transient_fields=list(rep1.reset_transient_fields) + list(rep2.reset_transient_fields),
                ignored_runtime_configuration=list(rep1.ignored_runtime_configuration) + list(rep2.ignored_runtime_configuration),
                unrecoverable_legacy_state=combined_unrec,
                compatibility_result="COMPATIBLE",
                migration_result="SUCCESS",
                diagnostic_notes=combined_notes,
            )
            migration_report = combined_report
            checkpoint_data["diagnostic_metadata"]["migration_chain"] = [rep1.to_dict(), rep2.to_dict()]
            checkpoint_data["diagnostic_metadata"]["migration_report"] = combined_report.to_dict()
        elif has_schema and isinstance(schema_val, dict) and schema_val.get("checkpoint_schema_version") == "1.1":
            if not expected_observation_protocol_version or not expected_observation_protocol_version.strip():
                raise CausalIdentityValidationError(
                    "Migrating pre-R1 v1.1 checkpoint to 1.2.0 requires an explicit target observation_protocol_version"
                )
            mid_111, rep1 = migrate_schema_1_1_to_1_1_1(raw_data, policy=policy)
            checkpoint_data, rep2 = migrate_schema_1_1_1_to_1_2_0(
                mid_111,
                target_observation_protocol_version=expected_observation_protocol_version,
                policy=policy,
            )
            combined_notes = list(rep1.diagnostic_notes) + list(rep2.diagnostic_notes)
            combined_unrec = list(rep1.unrecoverable_legacy_state) + list(rep2.unrecoverable_legacy_state)
            combined_report = MigrationReport(
                source_schema="1.1",
                target_schema="1.2.0",
                restored_durable_fields=["persistent_state"],
                reset_transient_fields=list(rep1.reset_transient_fields) + list(rep2.reset_transient_fields),
                ignored_runtime_configuration=list(rep1.ignored_runtime_configuration) + list(rep2.ignored_runtime_configuration),
                unrecoverable_legacy_state=combined_unrec,
                compatibility_result="COMPATIBLE",
                migration_result="SUCCESS",
                diagnostic_notes=combined_notes,
            )
            migration_report = combined_report
            checkpoint_data["diagnostic_metadata"]["migration_chain"] = [rep1.to_dict(), rep2.to_dict()]
            checkpoint_data["diagnostic_metadata"]["migration_report"] = combined_report.to_dict()
        elif has_schema and isinstance(schema_val, dict) and schema_val.get("checkpoint_schema_version") == "1.1.1":
            if not expected_observation_protocol_version or not expected_observation_protocol_version.strip():
                raise CausalIdentityValidationError(
                    "Migrating pre-R1 v1.1.1 checkpoint to 1.2.0 requires an explicit target observation_protocol_version"
                )
            checkpoint_data, migration_report = migrate_schema_1_1_1_to_1_2_0(
                raw_data,
                target_observation_protocol_version=expected_observation_protocol_version,
                policy=policy,
            )
            checkpoint_data["diagnostic_metadata"]["migration_chain"] = [migration_report.to_dict()]
        elif has_schema and isinstance(schema_val, dict) and schema_val.get("checkpoint_schema_version") == "1.2.0":
            checkpoint_data = raw_data
        else:
            raise CheckpointSchemaError(
                "Unrecognized checkpoint family for R1 restore. Expected 1.2.0, 1.1.1, 1.1, or 1.0."
            )

        validate_canonical_persistent_shape(checkpoint_data, schema_label="1.2.0")
        validate_semantic_compatibility(
            checkpoint_data,
            policy=policy,
            expected_schema_version="1.2.0",
            expected_contract_version="1.2.0",
            expected_observation_protocol_version=expected_observation_protocol_version,
        )

        obs_version = checkpoint_data["schema"]["observation_protocol_version"]
        compat = checkpoint_data["compatibility"]
        expected_obs_digest = compute_observation_protocol_digest(obs_version)

        pstate = checkpoint_data["persistent_state"]
        exp_state_digest = compute_checkpoint_state_digest(pstate)
        rec_state_digest = checkpoint_data["integrity"]["checkpoint_state_digest"]
        if rec_state_digest != exp_state_digest:
            raise CheckpointIntegrityError(
                f"State digest mismatch: recorded '{rec_state_digest}' != computed '{exp_state_digest}'"
            )

        prov_state = checkpoint_data["causal_provenance_state"]
        exp_prov_digest = compute_causal_provenance_digest(prov_state)
        rec_prov_digest = checkpoint_data["integrity"]["causal_provenance_digest"]
        if rec_prov_digest != exp_prov_digest:
            raise CheckpointIntegrityError(
                f"Causal provenance digest mismatch: recorded '{rec_prov_digest}' != computed '{exp_prov_digest}'"
            )

        exp_bundle_digest = compute_checkpoint_bundle_digest(
            checkpoint_state_digest=exp_state_digest,
            causal_provenance_digest=exp_prov_digest,
            combined_semantics_digest=compat["combined_semantics_digest"],
            causal_identity_protocol_digest=CAUSAL_IDENTITY_PROTOCOL_DIGEST,
            observation_protocol_digest=expected_obs_digest,
            causal_provenance_epoch=prov_state["causal_provenance_epoch"],
        )
        rec_bundle_digest = checkpoint_data["integrity"]["checkpoint_bundle_digest"]
        if rec_bundle_digest != exp_bundle_digest:
            raise CheckpointIntegrityError(
                f"Checkpoint bundle digest mismatch: recorded '{rec_bundle_digest}' != computed '{exp_bundle_digest}'"
            )

        # Restore graph
        pred_config = False if enable_prediction is None else enable_prediction
        new_graph, _ = _restore_graph_from_persistent_payload(
            persistent_payload=pstate,
            policy=policy,
            enable_prediction=pred_config,
        )

        validate_causal_provenance_state(
            causal_provenance_state=prov_state,
            checkpoint_state_digest=exp_state_digest,
            checkpoint_observation_protocol_version=obs_version,
        )
        new_ledger = CausalCommitLedger.from_dict(prov_state)

        runtime_root = CanonicalR1RuntimeRoot(
            graph=new_graph,
            ledger=new_ledger,
            observation_protocol_version=obs_version,
            assembly_policy=new_graph._assembly_manager.policy if new_graph._assembly_manager else policy,
            lifecycle_guard=active_guard,
        )

        if _on_pre_swap is not None:
            _on_pre_swap(active_guard.state)

        assert active_guard.state == RuntimeLifecycleState.RESTORING
        return runtime_root, migration_report
