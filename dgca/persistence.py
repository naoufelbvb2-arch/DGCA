"""
DGCA — RIC-01 / R0: Persistent Cognitive State & Runtime Lifecycle Contract
Formal Architecture Specification v1.1 — FROZEN

Constitutional Principles:
1. PersistentState ∩ TransientWorkingState = ∅
2. ReconstructibleState ∉ PersistentState
3. Checkpoint Type: COGNITIVE_CHECKPOINT (not LIVE_PROCESS_SUSPEND)
4. Canonical Restore: New CognitiveGraph, rebuilt indexes, fresh engines, atomic swap.
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
from dataclasses import dataclass
from typing import Any

from .assembly import (
    AssemblyManager,
    AssemblyPolicy,
    FormationCandidate,
    StructuralAssembly,
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
    """Raised when legacy v1.0 checkpoint migration fails."""


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
        if current == new_state:
            return

        # Allowed transitions:
        # IDLE -> MUTATING -> IDLE
        # IDLE -> CHECKPOINTING -> IDLE
        # IDLE -> RESTORING -> IDLE
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

    def __enter__(self):
        self.guard.transition_to(self.target_state)
        return self.guard

    def __exit__(self, exc_type, exc_val, exc_tb):
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
        }


# ─────────────────────────────────────────────────────────── 4. Semantic Fingerprints
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
    # Persist durable fields only: nid, region, is_concept, members (sorted), U, V, head, is_intrinsic, N_total
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
        # Sort ctx_hits keys
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
    hypotheses_list = copy.deepcopy(graph.hypotheses)
    # Sort hypotheses by their canonical JSON representation for determinism
    hypotheses_list.sort(key=lambda h: json.dumps(h, sort_keys=True, separators=(",", ":")))

    # 7. Assemblies (sorted by assembly_id then version)
    assemblies_list = []
    mgr = graph._assembly_manager
    if mgr is not None:
        for aid in sorted(mgr.assemblies.keys()):
            for asm in sorted(mgr.assemblies[aid], key=lambda a: a.version):
                member_edges_sorted = sorted([[u, v] for u, v in asm.member_edges])
                assemblies_list.append({
                    "assembly_id": asm.assembly_id,
                    "is_retired": bool(asm.is_retired),
                    "member_edges": member_edges_sorted,
                    "origin_signature": str(asm.origin_signature),
                    "parent_assemblies": sorted(asm.parent_assemblies),
                    "predecessor_version": asm.predecessor_version,
                    "version": int(asm.version),
                })

    # 8. Pending Structural Evidence
    pending_candidates_list = []
    pending_growth_list = []
    pending_merge_list = []

    if mgr is not None:
        # Formation candidates (sorted by candidate_id)
        for cid in sorted(mgr.pending_candidates.keys()):
            cand = mgr.pending_candidates[cid]
            pending_candidates_list.append({
                "candidate_id": cand.candidate_id,
                "context_signature": cand.context_signature,
                "created_t": int(cand.created_t),
                "edges": sorted([[u, v] for u, v in cand.edges]),
                "root_votes": sorted(cand.root_votes),
            })

        # Growth candidates
        # key is (assembly_id, (u, v), context)
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
        # key is (frozenset[parent_ids], context)
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

    # Validate finite numbers across entire persistent payload
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
            # Validate version ordering
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

        # 3. Pending Formation Candidates referential integrity
        for cid, cand in mgr.pending_candidates.items():
            for u, v in cand.edges:
                if (u, v) not in graph.edges:
                    raise StructuralReferentialIntegrityError(
                        f"Formation candidate '{cid}' references edge ({u}, {v}) which is not in live graph.edges"
                    )

        # 4. Pending Growth referential integrity
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
            if (u, v) not in graph.edges:
                raise StructuralReferentialIntegrityError(
                    f"Pending growth references new_edge ({u}, {v}) missing from live graph.edges"
                )

        # 5. Pending Merge referential integrity
        for (parents_set, ctx) in mgr.pending_merge:
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
    """Constructs the canonical top-level DGCA_COGNITIVE_CHECKPOINT v1.1 structure."""
    pol = policy or (graph._assembly_manager.policy if graph._assembly_manager else AssemblyPolicy())

    # 1. Validate referential integrity before checkpoint construction
    validate_structural_referential_integrity(graph)

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
        "source_schema": "1.1",
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
            "checkpoint_schema_version": "1.1",
            "cognitive_semantics_version": "1.0",
            "runtime_contract_version": "1.1",
        },
    }
    return checkpoint


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
    dest_path = pathlib.Path(filepath).resolve()
    dest_dir = dest_path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Enforce lifecycle guard
    active_guard = guard or RuntimeLifecycleGuard()
    with active_guard.checkpointing():
        checkpoint_data = build_canonical_checkpoint(graph, policy, diagnostic_metadata)
        canonical_json_bytes = json.dumps(
            checkpoint_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

        temp_file = dest_dir / f".tmp_{dest_path.name}_{uuid.uuid4().hex}"
        try:
            with open(temp_file, "wb") as f:
                f.write(canonical_json_bytes)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_file, dest_path)

            # Best effort directory fsync where supported
            try:
                if hasattr(os, "O_DIRECTORY"):
                    dir_fd = os.open(str(dest_dir), os.O_DIRECTORY)
                    os.fsync(dir_fd)
                    os.close(dir_fd)
            except (OSError, AttributeError):
                pass

            return checkpoint_data["integrity"]["checkpoint_state_digest"]
        except Exception:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            raise


# ─────────────────────────────────────────────────────────── 10. Legacy Migration (v1.0 -> v1.1)
def migrate_legacy_v1_checkpoint(
    legacy_data: dict[str, Any],
    runtime_enable_prediction: bool = False,
) -> tuple[dict[str, Any], MigrationReport]:
    """Migrates a legacy v1.0 checkpoint to canonical v1.1 persistent state."""
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

    # Convert nodes
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

    # Convert edges
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
        assemblies_list.append({
            "assembly_id": adata["assembly_id"],
            "is_retired": bool(adata.get("is_retired", False)),
            "member_edges": member_edges_sorted,
            "origin_signature": str(adata.get("origin_signature", "")),
            "parent_assemblies": sorted(adata.get("parent_assemblies", [])),
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
        target_schema="1.1",
        restored_durable_fields=restored_durable,
        reset_transient_fields=reset_transient,
        ignored_runtime_configuration=ignored_config,
        unrecoverable_legacy_state=unrecoverable_state,
        compatibility_result="COMPATIBLE",
        migration_result="SUCCESS",
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
            "checkpoint_schema_version": "1.1",
            "cognitive_semantics_version": "1.0",
            "runtime_contract_version": "1.1",
        },
    }
    return migrated_checkpoint, report


# ─────────────────────────────────────────────────────────── 11. Canonical Two-Phase Restore
def restore_cognitive_checkpoint(
    filepath: str | pathlib.Path,
    policy: AssemblyPolicy | None = None,
    enable_prediction: bool | None = None,
    guard: RuntimeLifecycleGuard | None = None,
) -> tuple[CognitiveGraph, MigrationReport | None]:
    """Phase A: Two-phase restore into a NEW CognitiveGraph.

    Constructs a fresh graph and fresh runtime root.
    Validates all schema, digests, compatibility, and referential constraints.
    Returns (restored_graph, migration_report).
    """
    path = pathlib.Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {path}")

    active_guard = guard or RuntimeLifecycleGuard()
    with active_guard.restoring():
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except json.JSONDecodeError as err:
            raise CheckpointSchemaError(f"Malformed JSON checkpoint: {err}")

        # Detect schema version
        migration_report: MigrationReport | None = None
        if raw_data.get("version") == "1.0" or "schema" not in raw_data:
            # Legacy v1.0 migration
            pred_setting = False if enable_prediction is None else enable_prediction
            checkpoint_data, migration_report = migrate_legacy_v1_checkpoint(raw_data, pred_setting)
        else:
            checkpoint_data = raw_data

        # Validate schema header
        schema_sec = checkpoint_data.get("schema", {})
        if schema_sec.get("checkpoint_schema_version") != "1.1":
            raise CheckpointSchemaError(
                f"Unsupported checkpoint_schema_version: {schema_sec.get('checkpoint_schema_version')}"
            )
        if schema_sec.get("cognitive_semantics_version") != "1.0":
            raise CheckpointCompatibilityError(
                f"Incompatible cognitive_semantics_version: {schema_sec.get('cognitive_semantics_version')}"
            )

        # Validate numeric finiteness
        assert_finite_numbers(checkpoint_data, "checkpoint_root")

        # Validate semantic compatibility
        compat_sec = checkpoint_data.get("compatibility", {})
        current_region_digest = compute_region_schema_digest()
        current_law_digest = compute_active_law_digest()
        current_policy_digest = compute_assembly_policy_digest(policy)

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
        new_graph = CognitiveGraph(
            t=persistent_payload.get("logical_time", 0),
            enable_prediction=pred_config,
            concept_hits=dict(persistent_payload.get("concept_hits", {})),
            drives=dict(persistent_payload.get("drives", {})),
            hypotheses=copy.deepcopy(persistent_payload.get("hypotheses", [])),
            # Transient operational state strictly initialized quiescent:
            dmg=0.0,
            goal=None,
            outcome=0.0,
            log=[],
            prediction_pool={},
            prediction_sources={},
        )

        # Restore contradictions
        for k, v in persistent_payload.get("contradictions", {}).items():
            new_graph.X[k] = set(v)

        # Restore Nodes
        for ndata in persistent_payload.get("nodes", []):
            node = Node(
                nid=ndata["nid"],
                region=ndata["region"],
                is_concept=ndata.get("is_concept", False),
                members=set(ndata.get("members", [])),
                U=float(ndata.get("U", 0.0)),
                V=float(ndata.get("V", 0.0)),
                head=ndata.get("head"),
                is_intrinsic=bool(ndata.get("is_intrinsic", False)),
                N_total=int(ndata.get("N_total", 0)),
                # Node transient activation strictly reset:
                A=0.0,
                t_spawn=-999,
                episode=None,
            )
            new_graph.nodes[node.nid] = node

        # Restore Edges
        for edata in persistent_payload.get("edges", []):
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
            # Reconstructible indexes rebuilt
            new_graph.out_adj.setdefault(edge.src, {})[edge.dst] = edge
            new_graph.in_adj.setdefault(edge.dst, {})[edge.src] = edge

        # Construct NEW AssemblyManager
        new_mgr = AssemblyManager(new_graph, policy or AssemblyPolicy())

        # Restore Assemblies
        for adata in persistent_payload.get("assemblies", []):
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
        pending_ev = persistent_payload.get("pending_structural_evidence", {})

        # Formation candidates
        for cdata in pending_ev.get("pending_candidates", []):
            cand_votes = set(cdata.get("root_votes", []))
            cand = FormationCandidate(
                candidate_id=cdata["candidate_id"],
                edges=frozenset((pair[0], pair[1]) for pair in cdata["edges"]),
                context_signature=cdata.get("context_signature"),
                root_votes=cand_votes,
                created_t=cdata.get("created_t", 0),
            )
            new_mgr.pending_candidates[cand.candidate_id] = cand

        # Growth candidates
        for gdata in pending_ev.get("pending_growth", []):
            g_votes = set(gdata.get("root_votes", []))
            pair = (gdata["new_edge"][0], gdata["new_edge"][1])
            growth_key = (gdata["assembly_id"], pair, gdata.get("context"))
            new_mgr.pending_growth[growth_key] = g_votes

        # Merge candidates
        for mdata in pending_ev.get("pending_merge", []):
            m_votes = set(mdata.get("root_votes", []))
            merge_key = (frozenset(mdata["parent_assembly_ids"]), mdata.get("context"))
            new_mgr.pending_merge[merge_key] = m_votes

        # Rebuild AssemblyManager derived indexes
        new_mgr.rebuild_indexes()
        new_graph._assembly_manager = new_mgr

        # Validate structural referential integrity on the newly constructed graph
        validate_structural_referential_integrity(new_graph, new_mgr)

        # Fresh Engine Postcondition (Section 15):
        # All Phase-II engines must be None immediately after restore
        assert new_graph._representation_engine is None
        assert new_graph._completion_engine is None
        assert new_graph._generation_engine is None
        assert new_graph._recurrent_engine is None
        assert new_graph._loop_engine is None

        # Verify AssemblyManager graph binding
        assert new_mgr.graph is new_graph

        return new_graph, migration_report


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
        self.policy = policy or AssemblyPolicy()
        self.enable_prediction = enable_prediction
        self.guard = guard or RuntimeLifecycleGuard()

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
    ) -> tuple[CognitiveGraph, MigrationReport | None]:
        """Atomic two-phase restore.

        Phase A: Prepares and validates a new CognitiveGraph in isolation.
        Phase B: Commits by swapping self.graph to the new graph.
        If Phase A fails, self.graph remains object-identical and authoritative.
        """
        # Phase A: Construct and validate new graph in isolation
        new_graph, report = restore_cognitive_checkpoint(
            filepath=filepath,
            policy=self.policy,
            enable_prediction=self.enable_prediction,
            guard=self.guard,
        )

        # Phase B: Atomic Root Swap
        self.graph = new_graph
        return self.graph, report
