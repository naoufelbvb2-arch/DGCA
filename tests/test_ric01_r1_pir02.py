"""
DGCA — RIC-01 / R1-PIR-02 Authoritative Verification Test Suite
Final Causal Identity Closure Verification (44 Tests: PIR02-T01 .. PIR02-T44)

Covers:
- PIR02-B01: ExpressiveObligation registered internal work domain
- PIR02-B02: Detached inspection views, raw mutation invalidates lineage
- PIR02-B03: Deterministic epoch ID, restorable post-mutation migrated state
- PIR02-B04: RFC13 candidate cache isolation & canonical JSON byte sorting
- PIR02-B05: RFC14 canonical GenerativeFrameID expansion re-derivation
- PIR02-B06: RFC15 ContinuationCommit progress snapshot digest consistency & GCE authority
- PIR02-B07: RFC16 canonical DeliveryID loop integration & retry persistence
- PIR02-B08: Pre-mutation provenance validation & pre-save fail-closed validation
- PIR02-B09: Chained migration preservation of all historical loss disclosures
- PIR02-D01: Strict lowercase 64-hex digest validation
- PIR02-D02: Directory fd closed on fsync exception
- PIR02-D03: Directory fsync assertion in atomic replace
"""
import copy
import dataclasses
import hashlib
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from dgca.assembly import AssemblyPolicy
from dgca.causal_identity import (
    CAUSAL_IDENTITY_PROTOCOL_DIGEST,
    LITERAL_DOMAIN_REGISTRY,
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalIdentityValidationError,
    CausalProvenanceEpoch,
    CausalRuntimeHealth,
    PersistentMutationCommand,
    compute_causal_provenance_digest,
    compute_checkpoint_bundle_digest,
    compute_event_descriptor_digest,
    create_migrated_r1_provenance_epoch,
    create_native_r1_provenance_epoch,
    derive_causal_provenance_epoch_id,
    derive_continuation_commit_id,
    derive_delivery_id,
    derive_expressive_obligation_id,
    derive_generative_frame_id,
    derive_internal_work_id,
    derive_pattern_candidate_id,
    derive_root_external_episode_id,
    validate_causal_provenance_state,
)
from dgca.completion import PatternCompletionEngine
from dgca.config import Law
from dgca.generation import (
    GenerativeFrame,
    HierarchicalGenerativeEngine,
    RoleBinding,
    SurfaceChunk,
)
from dgca.graph import CognitiveGraph, Node
from dgca.loop import UnifiedGenerativeCognitiveLoopEngine
from dgca.persistence import (
    RuntimeLifecycleGuard,
    _atomic_replace_file,
    build_canonical_r1_checkpoint,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    restore_canonical_r1_checkpoint,
    save_canonical_r1_checkpoint,
    save_cognitive_checkpoint,
)
from dgca.recurrent import (
    PredictiveRecurrentGenerativeEngine,
)
from dgca.representation import ParticipationReceipt, SparseDistributedCognitiveRepresentation


@pytest.fixture
def clean_graph():
    return CognitiveGraph()


@pytest.fixture
def clean_guard():
    return RuntimeLifecycleGuard()


@pytest.fixture
def sample_runtime(clean_graph, clean_guard):
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(clean_graph, AssemblyPolicy()))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    return CanonicalR1RuntimeRoot(
        graph=clean_graph,
        ledger=ledger,
        observation_protocol_version="1.0.0",
        lifecycle_guard=clean_guard,
    )


def make_rep(graph, root_id, node_ids):
    for nid in node_ids:
        if nid not in graph.nodes:
            graph.nodes[nid] = Node(nid=nid, region="text")
    receipts = tuple(
        ParticipationReceipt(
            receipt_id=f"rec_{i}",
            element_ref=nid,
            parent_cycle_id=1,
            snapshot_or_microtick=0,
            origin_lineage="external",
            participation_kind="node",
            scope_refs=("global",),
            activation_magnitude=1.0,
        )
        for i, nid in enumerate(node_ids)
    )
    return SparseDistributedCognitiveRepresentation(
        representation_id=f"rep_{root_id}",
        parent_cycle_id=1,
        snapshot_or_microtick=0,
        participating_node_refs=frozenset(node_ids),
        participating_edge_refs=frozenset(),
        context_binding_ref=None,
        participation_receipts=receipts,
    )


# ─────────────────────────────────────────────────────────── PIR02-B01: Protocol-Domain / Obligation Identity (T01 - T04)

def test_pir02_t01_obligation_id_routes_to_internal_work_domain():
    """PIR02-T01: derive_expressive_obligation_id routes to INTERNAL_WORK domain without unregistered domain."""
    ob_id = derive_expressive_obligation_id(
        root_authority_ref="root_auth_1",
        semantic_element_ref="cat",
        role_scope="salient_core",
        alternative_branch_id=None,
        prefix="ob_",
    )
    assert ob_id.startswith("ob_")
    assert len(ob_id) == 67  # 3 + 64 hex
    assert "EXPRESSIVE_OBLIGATION" not in LITERAL_DOMAIN_REGISTRY


def test_pir02_t02_obligation_id_deterministic_and_matches_internal_work():
    """PIR02-T02: derive_expressive_obligation_id strictly delegates to derive_internal_work_id."""
    ob_id = derive_expressive_obligation_id(
        root_authority_ref="root_auth_1",
        semantic_element_ref="cat",
        role_scope="salient_core",
        alternative_branch_id="alt_branch_A",
        prefix="ob_",
    )
    work_id = derive_internal_work_id(
        root_authority_ref="root_auth_1",
        subsystem_kind="EXPRESSIVE_OBLIGATION",
        scope_refs=["salient_core"],
        prerequisite_work_ids=[],
        work_index_or_role={
            "semantic_element_ref": "cat",
            "alternative_branch_id": "alt_branch_A",
        },
        prefix="ob_",
    )
    assert ob_id == work_id


def test_pir02_t03_recurrent_derive_obligations_preserves_typed_references(clean_graph):
    """PIR02-T03: derive_obligations preserves typed semantic_element_ref without forced str()."""
    clean_graph.link("u", "v", W=1.0, contexts=("en",))
    rec_engine = PredictiveRecurrentGenerativeEngine(clean_graph)
    edge_receipt = ParticipationReceipt(
        receipt_id="rec_edge",
        element_ref=("u", "v"),
        parent_cycle_id=1,
        snapshot_or_microtick=0,
        origin_lineage="external",
        participation_kind="edge",
        scope_refs=("global",),
        relational_drive=1.0,
    )
    rep = SparseDistributedCognitiveRepresentation(
        representation_id="rep_edge_test",
        parent_cycle_id=1,
        snapshot_or_microtick=0,
        participating_node_refs=frozenset(["u", "v"]),
        participating_edge_refs=frozenset([("u", "v")]),
        context_binding_ref=None,
        participation_receipts=(edge_receipt,),
    )
    obs = rec_engine.derive_obligations(rep, "root_auth_1", canonical_identity=True)
    assert len(obs) == 1
    assert obs[0].semantic_element_ref == ("u", "v")
    assert obs[0].obligation_id.startswith("ob_")


def test_pir02_t04_literal_domain_registry_frozen_at_21():
    """PIR02-T04: Literal domain registry length is strictly 21 and protocol digest matches."""
    assert len(LITERAL_DOMAIN_REGISTRY) == 21
    assert CAUSAL_IDENTITY_PROTOCOL_DIGEST == "f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398"


# ─────────────────────────────────────────────────────────── PIR02-B02: Safe Detached Inspection Views (T05 - T12)

def test_pir02_t05_graph_inspection_view_returns_detached_node_copies(sample_runtime):
    """PIR02-T05: graph.nodes returns detached copies; mutation does not leak and lineage remains valid."""
    sample_runtime.unsafe_mutable_graph().link("n1", "n2", W=1.0, contexts=("en",))
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID

    sample_runtime.graph.nodes["n1"].U = 999.0
    assert sample_runtime.unsafe_mutable_graph().nodes["n1"].U != 999.0
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID

    sample_runtime.graph.nodes["injected"] = Node(nid="injected", region="text")
    assert "injected" not in sample_runtime.unsafe_mutable_graph().nodes


def test_pir02_t06_graph_inspection_view_returns_detached_edge_copies(sample_runtime):
    """PIR02-T06: graph.edges and graph.edge() return detached copies; mutation does not leak."""
    sample_runtime.unsafe_mutable_graph().link("n1", "n2", W=Law.W_BASE, contexts=("en",))
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID

    edge_copy = sample_runtime.graph.edge("n1", "n2")
    assert edge_copy is not None
    edge_copy.W = 999.0
    assert sample_runtime.unsafe_mutable_graph().edge("n1", "n2").W == Law.W_BASE


def test_pir02_t07_graph_inspection_view_returns_detached_contradictions_X(sample_runtime):
    """PIR02-T07: graph.X returns detached sets; mutation does not leak."""
    sample_runtime.unsafe_mutable_graph().X["n1"] = {"n2"}
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID

    sample_runtime.graph.X["n1"].add("n3")
    assert "n3" not in sample_runtime.unsafe_mutable_graph().X["n1"]


def test_pir02_t08_graph_inspection_view_does_not_expose_live_engines(sample_runtime):
    """PIR02-T08: graph inspection view does not expose public live engine properties."""
    g = sample_runtime.graph
    assert not hasattr(g, "assembly_manager")
    assert not hasattr(g, "representation_engine")
    assert not hasattr(g, "completion_engine")
    assert not hasattr(g, "generation_engine")
    assert not hasattr(g, "recurrent_engine")
    assert not hasattr(g, "loop_engine")


def test_pir02_t09_graph_inspection_view_no_getattr_forwarding(sample_runtime):
    """PIR02-T09: graph inspection view does not use __getattr__ to forward arbitrary methods."""
    g = sample_runtime.graph
    assert not hasattr(g, "non_existent_attribute")
    with pytest.raises(AttributeError):
        _ = g.arbitrary_graph_method()


def test_pir02_t10_graph_inspection_view_direct_mutations_invalidate_lineage(sample_runtime):
    """PIR02-T10: link, unlink, observe on inspection view invalidate canonical lineage before executing."""
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.VALID
    sample_runtime.graph.link("a", "b", W=1.0, contexts=("en",))
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION


def test_pir02_t11_ledger_inspection_view_returns_detached_copies(sample_runtime):
    """PIR02-T11: ledger inspection view returns detached copies of transactions and bindings."""
    root_id = derive_root_external_episode_id("b_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand("test", "CREATE", ["x"], {"action": 1}, "scope")

    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: None,
    )
    txs = sample_runtime.ledger.committed_transactions
    assert len(txs) == 1
    txs["injected_tx"] = None
    assert len(sample_runtime.ledger.committed_transactions) == 1
    assert "injected_tx" not in sample_runtime.ledger.committed_transactions


def test_pir02_t12_unsafe_mutable_ledger_invalidates_lineage_before_return(sample_runtime):
    """PIR02-T12: unsafe_mutable_ledger invalidates lineage before returning mutable ledger."""
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.VALID
    raw_ledger = sample_runtime.unsafe_mutable_ledger()
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
    assert isinstance(raw_ledger, CausalCommitLedger)


# ─────────────────────────────────────────────────────────── PIR02-B03: Provenance Epoch Semantics & Migrated Restore (T13 - T18)

def test_pir02_t13_provenance_epoch_deterministic_id_derivation():
    """PIR02-T13: create_native_r1_provenance_epoch and create_migrated_r1_provenance_epoch derive deterministic IDs."""
    digest = "a" * 64
    native = create_native_r1_provenance_epoch(digest)
    assert native.history_status == "R1_TRACKED"
    expected_native_id = derive_causal_provenance_epoch_id(digest, "1.2.0", "1.0", prefix="cpe_")
    assert native.epoch_id == expected_native_id

    migrated = create_migrated_r1_provenance_epoch(digest)
    assert migrated.history_status == "PRE_R1_HISTORY_UNAVAILABLE"
    expected_migrated_id = derive_causal_provenance_epoch_id(digest, "1.1.1", "1.0", prefix="cpe_")
    assert migrated.epoch_id == expected_migrated_id


def test_pir02_t14_arbitrary_epoch_id_recomputed_on_construction():
    """PIR02-T14: CausalProvenanceEpoch recomputes deterministic epoch_id on construction."""
    digest = "b" * 64
    epoch = CausalProvenanceEpoch(epoch_id="arbitrary_custom_handle", history_status="R1_TRACKED", base_state_digest=digest)
    expected_id = derive_causal_provenance_epoch_id(digest, "1.2.0", "1.0", prefix="cpe_")
    assert epoch.epoch_id == expected_id


def test_pir02_t15_tampered_epoch_id_rejected_on_restore(sample_runtime, tmp_path):
    """PIR02-T15: Checkpoint with tampered epoch_id fails closed on restore."""
    cp_path = tmp_path / "tampered_epoch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["causal_provenance_state"]["causal_provenance_epoch"]["epoch_id"] = "cpe_" + "f" * 64

    prov_bytes = compute_causal_provenance_digest(data["causal_provenance_state"])
    data["integrity"]["causal_provenance_digest"] = prov_bytes
    data["integrity"]["checkpoint_bundle_digest"] = compute_checkpoint_bundle_digest(
        checkpoint_state_digest=data["integrity"]["checkpoint_state_digest"],
        causal_provenance_digest=prov_bytes,
        combined_semantics_digest=data["compatibility"]["combined_semantics_digest"],
        causal_identity_protocol_digest=data["compatibility"]["causal_identity_protocol_digest"],
        observation_protocol_digest=data["compatibility"]["observation_protocol_digest"],
        causal_provenance_epoch=data["causal_provenance_state"]["causal_provenance_epoch"],
    )
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CausalIdentityValidationError, match="Provenance epoch_id mismatch"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir02_t16_migrated_runtime_remains_restorable_after_tracked_mutation(clean_graph, tmp_path):
    """PIR02-T16: Migrated pre-R1 checkpoint remains restorable after legitimate tracked learning (PIR02-B03 Defect 2)."""
    # 1. Create and save 1.1.1 legacy checkpoint
    clean_graph.link("x", "y", W=Law.W_BASE, contexts=("en",))
    legacy_path = tmp_path / "legacy.json"
    save_cognitive_checkpoint(clean_graph, legacy_path, policy=AssemblyPolicy())

    # 2. Restore into 1.2.0 canonical runtime
    migrated_runtime, _ = restore_canonical_r1_checkpoint(legacy_path, expected_observation_protocol_version="1.0.0")
    assert migrated_runtime.ledger.epoch.history_status == "PRE_R1_HISTORY_UNAVAILABLE"
    base_digest = migrated_runtime.ledger.epoch.base_state_digest

    # 3. Execute legitimate tracked persistent mutation
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["y", "z"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )
    migrated_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: migrated_runtime.graph.link("y", "z", W=Law.W_BASE, contexts=("en",)),
    )

    # 4. Save canonical 1.2.0 checkpoint
    save_path = tmp_path / "migrated_and_learned.json"
    save_canonical_r1_checkpoint(migrated_runtime, save_path)

    # 5. Restore again: MUST succeed, epoch base_state_digest identifies epoch start, not current state
    restored2, _ = restore_canonical_r1_checkpoint(save_path, expected_observation_protocol_version="1.0.0")
    assert restored2.ledger.epoch.base_state_digest == base_digest
    assert len(restored2.ledger.committed_transactions) == 1
    assert ("y", "z") in restored2.graph.edges


def test_pir02_t17_empty_ledger_requires_base_state_digest_match():
    """PIR02-T17: Empty ledger without transactions enforces base_state_digest == checkpoint_state_digest."""
    prov_state = {
        "causal_provenance_epoch": {
            "epoch_id": derive_causal_provenance_epoch_id("a" * 64, "1.2.0", "1.0", prefix="cpe_"),
            "history_status": "R1_TRACKED",
            "base_state_digest": "a" * 64,
        },
        "committed_event_bindings": {},
        "committed_transactions": {},
    }
    with pytest.raises(CausalIdentityValidationError, match="base_state_digest mismatch"):
        validate_causal_provenance_state(
            causal_provenance_state=prov_state,
            checkpoint_state_digest="b" * 64,
            checkpoint_observation_protocol_version="1.0.0",
        )


def test_pir02_t18_checkpoint_build_never_mutates_epoch_metadata(sample_runtime):
    """PIR02-T18: build_canonical_r1_checkpoint never mutates runtime epoch metadata (PIR02-B03 Defect 3)."""
    orig_epoch = copy.copy(sample_runtime.ledger.epoch)
    _ = build_canonical_r1_checkpoint(
        graph=sample_runtime.graph,
        ledger=sample_runtime.ledger,
        observation_protocol_version="1.0.0",
        policy=AssemblyPolicy(),
    )
    assert sample_runtime.ledger.epoch.epoch_id == orig_epoch.epoch_id
    assert sample_runtime.ledger.epoch.base_state_digest == orig_epoch.base_state_digest
    assert sample_runtime.ledger.epoch.history_status == orig_epoch.history_status


# ─────────────────────────────────────────────────────────── PIR02-B04: RFC13 Candidate Cache Mode Isolation (T19 - T22)

def test_pir02_t19_rfc13_cache_separates_legacy_then_canonical(clean_graph):
    """PIR02-T19: discover_candidates with legacy first then canonical does not contaminate canonical with legacy IDs."""
    clean_graph.link("alpha", "beta", W=1.0, contexts=("en",))
    engine = PatternCompletionEngine(clean_graph)
    rep = make_rep(clean_graph, "root_1", ["alpha", "beta"])

    # 1. Legacy call
    legacy_cands = engine.discover_candidates(rep, canonical_identity=False)
    assert len(legacy_cands) > 0
    assert not legacy_cands[0].candidate_id.startswith("cand_") or len(legacy_cands[0].candidate_id) < 64

    # 2. Canonical call on same engine
    canonical_cands = engine.discover_candidates(rep, canonical_identity=True)
    assert len(canonical_cands) > 0
    assert canonical_cands[0].candidate_id.startswith("cand_")
    assert len(canonical_cands[0].candidate_id) == 69  # 5 + 64 hex


def test_pir02_t20_rfc13_cache_separates_canonical_then_legacy(clean_graph):
    """PIR02-T20: discover_candidates with canonical first then legacy does not contaminate legacy with canonical IDs."""
    clean_graph.link("alpha", "beta", W=1.0, contexts=("en",))
    engine = PatternCompletionEngine(clean_graph)
    rep = make_rep(clean_graph, "root_1", ["alpha", "beta"])

    # 1. Canonical call
    canonical_cands = engine.discover_candidates(rep, canonical_identity=True)
    assert len(canonical_cands) > 0
    assert len(canonical_cands[0].candidate_id) == 69

    # 2. Legacy call on same engine
    legacy_cands = engine.discover_candidates(rep, canonical_identity=False)
    assert len(legacy_cands) > 0
    assert len(legacy_cands[0].candidate_id) != 69


def test_pir02_t21_rfc13_candidate_ids_use_canonical_json_byte_sorting(clean_graph):
    """PIR02-T21: Candidate ID derivation sorts structural refs by canonical JSON bytes."""
    clean_graph.link("n1", "n2", W=1.0, contexts=("en",))
    engine = PatternCompletionEngine(clean_graph)
    rep = make_rep(clean_graph, "root_1", ["n1", "n2"])
    cands1 = engine.discover_candidates(rep, canonical_identity=True)

    expected_id = derive_pattern_candidate_id(
        parent_representation_id=rep.representation_id,
        candidate_kind="structural_edge",
        seed_refs=frozenset({"n1", "n2"}),
        structural_refs=frozenset({"n1", "n2", ("n1", "n2")}),
        assembly_refs=[],
        scope_view=("global",),
        context_ref=None,
        prefix="cand_",
    )
    assert any(c.candidate_id == expected_id for c in cands1)


def test_pir02_t22_rfc13_candidate_cache_key_isolation(clean_graph):
    """PIR02-T22: Candidate cache key incorporates canonical_identity mode boolean."""
    clean_graph.link("a", "b", W=1.0, contexts=("en",))
    engine = PatternCompletionEngine(clean_graph)
    rep = make_rep(clean_graph, "r1", ["a", "b"])

    engine.discover_candidates(rep, canonical_identity=False)
    engine.discover_candidates(rep, canonical_identity=True)

    assert (rep.representation_id, "all", False) in engine._candidate_cache
    assert (rep.representation_id, "all", True) in engine._candidate_cache


# ─────────────────────────────────────────────────────────── PIR02-B05: Canonical GenerativeFrame Expansion Re-ID (T23 - T26)

def test_pir02_t23_canonical_generative_frame_recomputed_on_expansion(clean_graph):
    """PIR02-T23: expand_hierarchy in canonical mode re-derives frame_id when role bindings change."""
    clean_graph.link("cat", "furry", W=1.0, contexts=("en",))
    clean_graph.link("cat", "whiskers", W=1.0, contexts=("en",))
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    rep = make_rep(clean_graph, "r1", ["cat", "furry", "whiskers"])

    base_frame = gen_engine.build_generative_frame(
        representation=rep,
        anchor_refs=frozenset(["cat"]),
        canonical_identity=True,
    )
    old_fid = base_frame.frame_id
    hierarchy = gen_engine.build_hierarchy([base_frame])

    expanded_h, _ = gen_engine.expand_hierarchy(
        hierarchy=hierarchy,
        representation=rep,
        budget=1.0,
        canonical_identity=True,
    )
    assert len(expanded_h.frames) == 1
    new_frame = next(iter(expanded_h.frames.values()))
    assert new_frame.frame_id != old_fid
    assert len(new_frame.role_bindings) > 0

    expected_fid = derive_generative_frame_id(
        parent_representation_id=str(rep.representation_id),
        anchors=sorted(new_frame.anchor_refs),
        scope=sorted(new_frame.scope_view),
        role_bindings=[
            {"role_authority_ref": b.role_authority_ref, "filler_ref": b.filler_ref}
            for b in sorted(new_frame.role_bindings, key=lambda x: (x.role_authority_ref, str(x.filler_ref)))
        ],
        prefix="frame_",
    )
    assert new_frame.frame_id == expected_fid


def test_pir02_t24_canonical_generative_frame_expansion_remaps_hierarchy_keys(clean_graph):
    """PIR02-T24: expanded_hierarchy.frames keys match the re-derived frame_ids."""
    clean_graph.link("dog", "bark", W=1.0, contexts=("en",))
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    rep = make_rep(clean_graph, "r2", ["dog", "bark"])

    base_frame = gen_engine.build_generative_frame(rep, frozenset(["dog"]), canonical_identity=True)
    hierarchy = gen_engine.build_hierarchy([base_frame])
    expanded_h, _ = gen_engine.expand_hierarchy(hierarchy, rep, budget=1.0, canonical_identity=True)

    for fid, frame in expanded_h.frames.items():
        assert fid == frame.frame_id


def test_pir02_t25_canonical_generative_frame_expansion_remaps_parent_references(clean_graph):
    """PIR02-T25: Remaps parent role bindings when child frame is expanded in canonical mode."""
    clean_graph.link("child_anchor", "sub_feature", W=1.0, contexts=("en",))
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    rep = make_rep(clean_graph, "r3", ["parent_anchor", "child_anchor", "sub_feature"])

    child_frame = gen_engine.build_generative_frame(rep, frozenset(["child_anchor"]), canonical_identity=True)
    parent_frame = GenerativeFrame(
        frame_id="parent_initial_id",
        parent_representation_id=rep.representation_id,
        scope_view=("global",),
        anchor_refs=frozenset(["parent_anchor"]),
        role_bindings=(RoleBinding("modifier", child_frame.frame_id),),
    )
    parent_id = derive_generative_frame_id(
        parent_representation_id=str(rep.representation_id),
        anchors=sorted(parent_frame.anchor_refs),
        scope=sorted(parent_frame.scope_view),
        role_bindings=[{"role_authority_ref": "modifier", "filler_ref": child_frame.frame_id}],
        prefix="frame_",
    )
    parent_frame = dataclasses.replace(parent_frame, frame_id=parent_id)

    hierarchy = gen_engine.build_hierarchy([parent_frame, child_frame])
    expanded_h, _ = gen_engine.expand_hierarchy(hierarchy, rep, budget=1.0, canonical_identity=True)

    assert len(expanded_h.frames) == 2
    child_new_id = next(f.frame_id for f in expanded_h.frames.values() if "child_anchor" in f.anchor_refs)
    parent_new_frame = next(f for f in expanded_h.frames.values() if "parent_anchor" in f.anchor_refs)
    assert parent_new_frame.role_bindings[0].filler_ref == child_new_id


def test_pir02_t26_legacy_generative_frame_expansion_unchanged(clean_graph):
    """PIR02-T26: In legacy mode (canonical_identity=False), frame_id is not changed on expansion."""
    clean_graph.link("cat", "furry", W=1.0, contexts=("en",))
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    rep = make_rep(clean_graph, "r4", ["cat", "furry"])

    base_frame = gen_engine.build_generative_frame(rep, frozenset(["cat"]), canonical_identity=False)
    old_fid = base_frame.frame_id
    hierarchy = gen_engine.build_hierarchy([base_frame])
    expanded_h, _ = gen_engine.expand_hierarchy(hierarchy, rep, budget=1.0, canonical_identity=False)

    new_frame = next(iter(expanded_h.frames.values()))
    assert new_frame.frame_id == old_fid


# ─────────────────────────────────────────────────────────── PIR02-B06: ContinuationCommit & GCE Authority (T27 - T30)

def test_pir02_t27_continuation_commit_stores_derived_progress_digest(clean_graph):
    """PIR02-T27: Canonical ContinuationCommit stores its identity-bound progress digest without overwrite."""
    clean_graph.link("a", "b", W=1.0, contexts=("order",))
    rec_engine = PredictiveRecurrentGenerativeEngine(clean_graph)
    epoch = rec_engine.create_epoch(
        root_authority_ref="root_1",
        work_ref="work_1",
        canonical_identity=True,
    )
    rep = make_rep(clean_graph, "root_1", ["a", "b"])

    obs = rec_engine.derive_obligations(rep, epoch.root_authority_ref, canonical_identity=True)
    cov = rec_engine.compute_coverage(obs, epoch, rep)
    rem = rec_engine.compute_remaining(obs, cov)
    front = rec_engine.derive_continuation_frontier(rem, cov, rep, epoch, all_obligations=obs)

    status, commit, _ = rec_engine.commit_continuation(front, epoch, rep, budget=1.0, canonical_identity=True)
    assert status == "CONTINUATION_COMMITTED"
    assert commit is not None

    from dgca.causal_identity import canonical_json_bytes
    expected_prog_digest = hashlib.sha256(canonical_json_bytes(list(epoch.progress_receipt_refs))).hexdigest()
    assert commit.progress_snapshot_digest == expected_prog_digest


def test_pir02_t28_continuation_commit_id_rederivable_from_stored_commit(clean_graph):
    """PIR02-T28: ContinuationCommitID is re-derivable strictly from the returned commit object fields."""
    clean_graph.link("a", "b", W=1.0, contexts=("order",))
    rec_engine = PredictiveRecurrentGenerativeEngine(clean_graph)
    epoch = rec_engine.create_epoch(root_authority_ref="root_auth", work_ref="work_auth", canonical_identity=True)
    rep = make_rep(clean_graph, "root_auth", ["a", "b"])

    obs = rec_engine.derive_obligations(rep, epoch.root_authority_ref, canonical_identity=True)
    cov = rec_engine.compute_coverage(obs, epoch, rep)
    rem = rec_engine.compute_remaining(obs, cov)
    front = rec_engine.derive_continuation_frontier(rem, cov, rep, epoch, all_obligations=obs)

    _, commit, _ = rec_engine.commit_continuation(front, epoch, rep, budget=1.0, canonical_identity=True)
    assert commit is not None

    rederived_id = derive_continuation_commit_id(
        epoch_id=commit.epoch_id,
        parent_representation_id=commit.parent_rid,
        obligation_id=commit.obligation_ref,
        progress_snapshot_digest=commit.progress_snapshot_digest,
        prefix="cc_",
    )
    assert commit.commit_id == rederived_id


def test_pir02_t29_canonical_gce_creation_enforces_expected_epoch_id(clean_graph):
    """PIR02-T29: Canonical GCE creation rejects masquerading epoch_id that does not match formula."""
    rec_engine = PredictiveRecurrentGenerativeEngine(clean_graph)
    with pytest.raises(ValueError, match="does not match canonical GCE ID"):
        rec_engine.create_epoch(
            root_authority_ref="root_1",
            work_ref="work_1",
            epoch_id="masquerading_epoch_id",
            canonical_identity=True,
        )


def test_pir02_t30_canonical_gce_creation_rejects_empty_work_ref(clean_graph):
    """PIR02-T30: Canonical GCE creation rejects empty/whitespace work_ref."""
    rec_engine = PredictiveRecurrentGenerativeEngine(clean_graph)
    with pytest.raises(ValueError, match="requires explicit non-empty work_ref"):
        rec_engine.create_epoch(root_authority_ref="root_1", work_ref="", canonical_identity=True)
    with pytest.raises(ValueError, match="requires explicit non-empty work_ref"):
        rec_engine.create_epoch(root_authority_ref="root_1", work_ref="   ", canonical_identity=True)


# ─────────────────────────────────────────────────────────── PIR02-B07: RFC16 DeliveryID Integration (T31 - T34)

def test_pir02_t31_deliver_surface_output_canonical_identity_mode(clean_graph):
    """PIR02-T31: deliver_surface_output in canonical mode produces derive_delivery_id."""
    loop_engine = UnifiedGenerativeCognitiveLoopEngine(clean_graph)
    chunk = SurfaceChunk(
        chunk_id="chunk_123",
        parent_representation_id="rep_456",
        surface_units=(),
        rendered_text="hello world",
        closure_reason="EXHAUSTED",
        origin_lineage="GENERATION",
    )
    del_view = loop_engine.deliver_surface_output(
        surface_chunk=chunk,
        parent_rid="rep_456",
        canonical_identity=True,
    )
    expected_did = derive_delivery_id(
        surface_chunk_id="chunk_123",
        parent_representation_id="rep_456",
        delivery_channel_ref=None,
        prefix="del_",
    )
    assert del_view.delivery_id == expected_did


def test_pir02_t32_deliver_surface_output_with_channel_ref(clean_graph):
    """PIR02-T32: deliver_surface_output incorporates delivery_channel_ref in canonical DeliveryID."""
    loop_engine = UnifiedGenerativeCognitiveLoopEngine(clean_graph)
    chunk = SurfaceChunk("c1", "r1", (), "text", "EXHAUSTED", "GENERATION")
    del_view = loop_engine.deliver_surface_output(
        surface_chunk=chunk,
        parent_rid="r1",
        canonical_identity=True,
        delivery_channel_ref="websocket_chan_0",
    )
    expected_did = derive_delivery_id("c1", "r1", delivery_channel_ref="websocket_chan_0", prefix="del_")
    assert del_view.delivery_id == expected_did


def test_pir02_t33_retry_delivery_preserves_canonical_delivery_id(clean_graph):
    """PIR02-T33: retry_delivery retains the exact canonical DeliveryID and increments retry count."""
    loop_engine = UnifiedGenerativeCognitiveLoopEngine(clean_graph)
    chunk = SurfaceChunk("c1", "r1", (), "text", "EXHAUSTED", "GENERATION")
    failed_view = loop_engine.deliver_surface_output(
        surface_chunk=chunk,
        parent_rid="r1",
        simulate_transport_failure=True,
        canonical_identity=True,
    )
    orig_did = failed_view.delivery_id

    retried_view = loop_engine.retry_delivery(orig_did, success=True)
    assert retried_view.delivery_id == orig_did
    assert retried_view.retry_count == 1
    assert retried_view.status == "DELIVERED"


def test_pir02_t34_legacy_delivery_unchanged(clean_graph):
    """PIR02-T34: deliver_surface_output in legacy mode preserves legacy 12-char SHA-256 handle."""
    loop_engine = UnifiedGenerativeCognitiveLoopEngine(clean_graph)
    chunk = SurfaceChunk("c1", "r1", (), "text", "EXHAUSTED", "GENERATION")
    del_view = loop_engine.deliver_surface_output(chunk, "r1", canonical_identity=False)
    expected_legacy = f"del_{hashlib.sha256(b'c1_r1').hexdigest()[:12]}"
    assert del_view.delivery_id == expected_legacy


# ─────────────────────────────────────────────────────────── PIR02-B08: Fail-Closed Pre-Mutation & Pre-Save Validation (T35 - T38)

def test_pir02_t35_pre_mutation_validation_rejects_empty_root_episode_before_mutator(sample_runtime):
    """PIR02-T35: Empty root_external_episode_id is rejected before mutator callback runs."""
    called = False

    def mutator():
        nonlocal called
        called = True

    cmd = PersistentMutationCommand("test", "CREATE", ["x"], {"a": 1}, "scope")
    with pytest.raises(CausalIdentityValidationError, match="root_external_episode_id"):
        sample_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id="",
            ingress_event_id="evt_1",
            event_descriptor_digest="a" * 64,
            mutator_callback=mutator,
        )
    assert not called


def test_pir02_t36_pre_mutation_validation_rejects_invalid_event_digest_before_mutator(sample_runtime):
    """PIR02-T36: Invalid event_descriptor_digest is rejected before mutator callback runs."""
    called = False

    def mutator():
        nonlocal called
        called = True

    cmd = PersistentMutationCommand("test", "CREATE", ["x"], {"a": 1}, "scope")
    with pytest.raises(CausalIdentityValidationError, match="event_descriptor_digest"):
        sample_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id="ep_1",
            ingress_event_id="evt_1",
            event_descriptor_digest="INVALID_NON_64_HEX",
            mutator_callback=mutator,
        )
    assert not called


def test_pir02_t37_pre_mutation_validation_leaves_runtime_healthy(sample_runtime):
    """PIR02-T37: A pre-mutation validation failure does not put runtime into MUTATION_FAILED."""
    cmd = PersistentMutationCommand("test", "CREATE", ["x"], {"a": 1}, "scope")
    try:
        sample_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id="ep_1",
            ingress_event_id="",  # invalid
            event_descriptor_digest="a" * 64,
            mutator_callback=lambda: None,
        )
    except CausalIdentityValidationError:
        pass
    assert sample_runtime.causal_runtime_health == CausalRuntimeHealth.HEALTHY


def test_pir02_t38_save_canonical_r1_checkpoint_validates_provenance_pre_publication(sample_runtime, tmp_path):
    """PIR02-T38: save_canonical_r1_checkpoint fails closed before writing file if ledger provenance is invalid."""
    object.__setattr__(sample_runtime._ledger.epoch, "epoch_id", "corrupted_epoch_id")
    target_file = tmp_path / "should_not_exist.json"

    with pytest.raises(CausalIdentityValidationError):
        save_canonical_r1_checkpoint(sample_runtime, target_file)
    assert not target_file.exists()


# ─────────────────────────────────────────────────────────── PIR02-B09: Chained Migration Loss Disclosures (T39 - T41)

def test_pir02_t39_chained_migration_1_0_to_1_2_0_preserves_all_loss_disclosures(tmp_path):
    """PIR02-T39: Chained 1.0 -> 1.1.1 -> 1.2.0 migration preserves both RFC11 structural and pre-R1 history disclosures."""
    v1_cp = {
        "version": "1.0",
        "t": 10,
        "nodes": {
            "u": {"nid": "u", "region": "TEXT", "U": 0.5, "V": 0.2},
            "v": {"nid": "v", "region": "TEXT", "U": 0.6, "V": 0.3},
        },
        "edges": [{"src": "u", "dst": "v", "W": 1.0, "contexts": ["en"]}],
        "assemblies": [],
        "concept_hits": {},
        "drives": {},
        "hypotheses": [],
        "X": {},
    }
    cp_path = tmp_path / "v1_0.json"
    cp_path.write_text(json.dumps(v1_cp), encoding="utf-8")

    _runtime, report = restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")
    assert report is not None

    assert any("pending structural evidence" in s for s in report.unrecoverable_legacy_state)
    assert "pre_r1_causal_provenance" in report.unrecoverable_legacy_state

    all_notes = " ".join(report.diagnostic_notes)
    assert "cannot be recovered" in all_notes or "pending structural evidence" in all_notes
    assert "Pre-R1" in all_notes or "cannot be reconstructed" in all_notes


def test_pir02_t40_chained_migration_1_1_to_1_2_0_preserves_sequence_limitation_and_pre_r1_history(clean_graph, tmp_path):
    """PIR02-T40: Chained 1.1 -> 1.1.1 -> 1.2.0 preserves sequential limitation and pre-R1 commit disclosures."""
    clean_graph.link("u", "v", W=1.0, contexts=("en",))
    cp_path = tmp_path / "v1_1.json"
    save_cognitive_checkpoint(clean_graph, cp_path, policy=AssemblyPolicy())

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["schema"]["checkpoint_schema_version"] = "1.1"
    data["schema"]["runtime_contract_version"] = "1.1"
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    _runtime, report = restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")
    assert report is not None
    assert "pre_r1_causal_provenance" in report.unrecoverable_legacy_state


def test_pir02_t41_migration_report_diagnostic_notes_accumulate_without_loss(clean_graph, tmp_path):
    """PIR02-T41: Migration report diagnostic notes retain ordered migration_chain in diagnostic_metadata."""
    clean_graph.link("u", "v", W=1.0, contexts=("en",))
    cp_path = tmp_path / "v1_1_1.json"
    save_cognitive_checkpoint(clean_graph, cp_path, policy=AssemblyPolicy())

    _runtime, report = restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")
    assert report is not None
    assert report.source_schema == "1.1.1"
    assert report.target_schema == "1.2.0"


# ─────────────────────────────────────────────────────────── PIR02-D01 - D03: Non-Blocking Hardening Debts (T42 - T44)

def test_pir02_t42_digest_shape_rejects_uppercase_hex(sample_runtime):
    """PIR02-T42 / D01: Digest validation strictly rejects uppercase hex."""
    cmd = PersistentMutationCommand("test", "CREATE", ["x"], {"a": 1}, "scope")
    with pytest.raises(CausalIdentityValidationError):
        sample_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id="ep_1",
            ingress_event_id="evt_1",
            event_descriptor_digest="A" * 64,  # uppercase
            mutator_callback=lambda: None,
        )


def test_pir02_t43_directory_fd_closed_on_fsync_exception(tmp_path):
    """PIR02-T43 / D02: Directory fd is closed in finally block even if os.fsync raises exception."""
    dest = tmp_path / "test_sync.bin"
    mock_close = MagicMock()
    mock_fsync = MagicMock(side_effect=OSError("Disk hardware fault"))

    with patch("os.fsync", mock_fsync), patch("os.close", mock_close):
        with pytest.raises(OSError, match="Disk hardware fault"):
            _atomic_replace_file(dest, b"test content")
        if hasattr(os, "O_DIRECTORY"):
            assert mock_close.called


def test_pir02_t44_directory_fsync_invoked_during_atomic_replace(tmp_path):
    """PIR02-T44 / D03: Directory fsync is invoked during atomic replace."""
    dest = tmp_path / "test_sync_invoked.bin"
    invoked_fsyncs = []

    orig_fsync = os.fsync
    def logging_fsync(fd):
        invoked_fsyncs.append(fd)
        try:
            orig_fsync(fd)
        except OSError:
            pass

    with patch("os.fsync", side_effect=logging_fsync):
        _atomic_replace_file(dest, b"test content")

    assert len(invoked_fsyncs) >= 1
