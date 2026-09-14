"""
DGCA — RIC-01 / R1-PIR-01: Post-Implementation Repair & Verification Test Suite
Authoritative spec: RIC-01-R1-Deterministic-Causal-Identity-Protocol-v1.3-FROZEN.md
Audit report: papers MD/RIC-01-R1-POST-IMPLEMENTATION-INDEPENDENT-AUDIT-v1.0.md
Tests: PIR01-T01 through PIR01-T27 covering PIR01-B01..B07 and PIR01-D01.
"""
from __future__ import annotations

import json

import pytest

from dgca.assembly import AssemblyPolicy
from dgca.causal_identity import (
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalIdentityValidationError,
    CausalLineageInvalidatedError,
    PersistentMutationCommand,
    canonicalize_payload,
    compute_causal_provenance_digest,
    compute_checkpoint_bundle_digest,
    create_native_r1_provenance_epoch,
    derive_surface_chunk_id,
)
from dgca.completion import (
    PatternCompletionEngine,
)
from dgca.config import TEXT
from dgca.generation import (
    HierarchicalGenerativeEngine,
    LinearizableOccurrence,
    LinearizationPrefix,
    RoleBinding,
)
from dgca.graph import CognitiveGraph
from dgca.persistence import (
    CheckpointCompatibilityError,
    RuntimeLifecycleGuard,
    _atomic_replace_file,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    restore_canonical_r1_checkpoint,
    save_canonical_r1_checkpoint,
    save_cognitive_checkpoint,
)
from dgca.recurrent import (
    PredictiveRecurrentGenerativeEngine,
)
from dgca.representation import (
    ParticipationReceipt,
)
from dgca.signature import behavioral_signature, build_reference_graph


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


def make_test_rep(graph, root_id, node_ids):
    for nid in node_ids:
        if nid not in graph.nodes:
            graph.node(nid, TEXT)
    receipts = [
        ParticipationReceipt(
            receipt_id=f"rcpt_{nid}",
            element_ref=nid,
            parent_cycle_id=1,
            snapshot_or_microtick=1,
            origin_lineage="EXTERNAL",
            participation_kind="node",
            activation_magnitude=0.8,
        )
        for nid in node_ids
    ]
    return graph.representation_engine.build_canonical_representation(
        causal_parent_ref=root_id,
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        context="en",
        participation_receipts=receipts,
    )


# ─────────────────────────────────────────────────────────── PIR01-B01: Compatibility Firewall (T01 - T04)

def test_pir01_t01_r1_restore_rejects_law_digest_mismatch(sample_runtime, tmp_path):
    """PIR01-T01: R1 restore rejects Law digest mismatch via semantic compatibility firewall."""
    cp_path = tmp_path / "law_mismatch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["compatibility"]["active_law_digest"] = "bad_law_digest_" + "0" * 48
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t02_r1_restore_rejects_policy_digest_mismatch(sample_runtime, tmp_path):
    """PIR01-T02: R1 restore rejects policy digest mismatch."""
    cp_path = tmp_path / "policy_mismatch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["compatibility"]["assembly_policy_digest"] = "bad_policy_digest_" + "0" * 45
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t03_r1_restore_rejects_region_combined_semantics_mismatch(sample_runtime, tmp_path):
    """PIR01-T03: R1 restore rejects region/combined semantics mismatch."""
    cp_path = tmp_path / "region_mismatch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["compatibility"]["region_schema_digest"] = "bad_region_digest_" + "0" * 45
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t04_r1_migration_rejects_incompatible_1_1_1_source(clean_graph, tmp_path):
    """PIR01-T04: R1 migration rejects incompatible 1.1.1 source."""
    cp_path = tmp_path / "incompatible_111.json"
    clean_graph.link("u", "v", W=1.0, contexts=("en",))
    save_cognitive_checkpoint(clean_graph, cp_path, policy=AssemblyPolicy())

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["compatibility"]["active_law_digest"] = "tampered_law_" + "0" * 50
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


# ─────────────────────────────────────────────────────────── PIR01-B02: RFC13 Canonical Settling Propagation (T05 - T08)

def test_pir01_t05_canonical_rfc13_edge_candidate_identity(clean_graph):
    """PIR01-T05: Canonical RFC13 edge candidate identity uses authoritative derive_pattern_candidate_id."""
    clean_graph.link("alpha", "beta", W=1.0, contexts=("en",))
    engine = PatternCompletionEngine(clean_graph)
    rep = make_test_rep(clean_graph, "root_1", ["alpha", "beta"])
    candidates = engine.discover_candidates(rep, canonical_identity=True)
    assert len(candidates) > 0
    cand = candidates[0]
    assert cand.candidate_id.startswith("cand_")
    assert len(cand.candidate_id) == 69


def test_pir01_t06_canonical_rfc13_proposal_identity(clean_graph):
    """PIR01-T06: Canonical RFC13 proposal identity is deterministic and parent-scoped."""
    clean_graph.link("alpha", "beta", W=1.0, contexts=("en",))
    engine = PatternCompletionEngine(clean_graph)
    rep = make_test_rep(clean_graph, "root_1", ["alpha"])
    candidates = engine.discover_candidates(rep, canonical_identity=True)
    assert len(candidates) > 0
    props = engine.evaluate_reinstatement_eligibility(candidates[0], rep, canonical_identity=True)
    assert len(props) > 0
    prop = props[0]
    assert prop.proposal_id.startswith("rp_")
    assert len(prop.proposal_id) == 67


def test_pir01_t07_canonical_multi_iteration_settling_rid_replay(clean_graph):
    """PIR01-T07: Canonical multi-iteration settling RID replay is 100% deterministic."""
    clean_graph.link("n1", "n2", W=1.0, contexts=("en",))
    clean_graph.link("n2", "n3", W=1.0, contexts=("en",))
    engine1 = PatternCompletionEngine(clean_graph)
    rep1 = make_test_rep(clean_graph, "root_test_7", ["n1", "n2"])
    rep_final1, outcome1 = engine1.run_settling_epoch(
        rep1, budget=1.0, canonical_identity=True, work_ref="settle_fixed_work"
    )

    engine2 = PatternCompletionEngine(clean_graph)
    rep2 = make_test_rep(clean_graph, "root_test_7", ["n1", "n2"])
    rep_final2, outcome2 = engine2.run_settling_epoch(
        rep2, budget=1.0, canonical_identity=True, work_ref="settle_fixed_work"
    )

    assert rep_final1.representation_id == rep_final2.representation_id
    assert outcome1.final_representation_id == outcome2.final_representation_id


def test_pir01_t08_canonical_settling_requires_lawful_work_ref(clean_graph):
    """PIR01-T08: Canonical settling requires explicit non-empty work_ref."""
    clean_graph.link("a", "b", W=1.0, contexts=("en",))
    engine = PatternCompletionEngine(clean_graph)
    rep = make_test_rep(clean_graph, "root_1", ["a", "b"])
    with pytest.raises(CausalIdentityValidationError, match="run_settling_epoch in canonical_identity mode requires an explicit non-empty work_ref"):
        engine.run_settling_epoch(rep, canonical_identity=True, work_ref=None)
    with pytest.raises(CausalIdentityValidationError, match="run_settling_epoch in canonical_identity mode requires an explicit non-empty work_ref"):
        engine.run_settling_epoch(rep, canonical_identity=True, work_ref="")


# ─────────────────────────────────────────────────────────── PIR01-B03: RFC14 Canonical Generation Integration (T09 - T12)

def test_pir01_t09_canonical_rfc14_frame_id_integration(clean_graph):
    """PIR01-T09: Canonical RFC14 GenerativeFrame derivation integration."""
    clean_graph.link("x", "y", W=1.0, contexts=("en",))
    rep = make_test_rep(clean_graph, "root_9", ["x", "y"])
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    frame = gen_engine.build_generative_frame(
        representation=rep,
        anchor_refs=frozenset(["x"]),
        role_bindings=(RoleBinding("subject", "x"),),
        canonical_identity=True,
    )
    assert frame.frame_id.startswith("frame_")
    assert len(frame.frame_id) == 70


def test_pir01_t10_canonical_rfc14_occurrence_id_integration(clean_graph):
    """PIR01-T10: Canonical RFC14 OccurrenceID integration in precedence graph."""
    clean_graph.link("x", "y", W=1.0, contexts=("en",))
    rep = make_test_rep(clean_graph, "root_10", ["x", "y"])
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    frame = gen_engine.build_generative_frame(
        representation=rep,
        anchor_refs=frozenset(["x"]),
        role_bindings=(RoleBinding("subject", "x"),),
        canonical_identity=True,
    )
    hierarchy = gen_engine.build_hierarchy([frame])
    prec = gen_engine.build_precedence_graph(hierarchy, canonical_identity=True)
    assert len(prec.occurrences) > 0
    for occ in prec.occurrences:
        assert occ.occurrence_id.startswith("occ_")
        assert len(occ.occurrence_id) == 68


def test_pir01_t11_chunk_identity_binds_actual_closure_reason(clean_graph):
    """PIR01-T11: SurfaceChunkID binds actual closure_reason and differentiates outcomes."""
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    occ1 = LinearizableOccurrence(
        occurrence_id="occ_1",
        frame_id="f1",
        role_authority_ref="anchor",
        filler_ref="word1",
        is_child_frame=False,
        scope_view=(),
    )
    occ2 = LinearizableOccurrence(
        occurrence_id="occ_2",
        frame_id="f1",
        role_authority_ref="subject",
        filler_ref="word2",
        is_child_frame=False,
        scope_view=(),
    )

    prefix_complete = LinearizationPrefix(
        committed_occurrences=(occ1, occ2),
        status="LINEARIZED",
        remaining_uncommitted_ids=frozenset(),
    )
    prefix_conflict = LinearizationPrefix(
        committed_occurrences=(occ1,),
        status="ORDER_CONFLICT",
        remaining_uncommitted_ids=frozenset(["occ_2"]),
    )

    chunk_complete = gen_engine.realize_surface_chunk(
        prefix_complete, "rep_test_11", canonical_identity=True
    )
    chunk_conflict = gen_engine.realize_surface_chunk(
        prefix_conflict, "rep_test_11", canonical_identity=True
    )

    assert chunk_complete.closure_reason == "COMPLETE"
    assert chunk_conflict.closure_reason == "CONFLICT"
    assert chunk_complete.chunk_id != chunk_conflict.chunk_id


def test_pir01_t12_chunk_identity_binds_actual_origin_lineage(clean_graph):
    """PIR01-T12: SurfaceChunkID binds uppercase origin_lineage GENERATION."""
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    occ = LinearizableOccurrence(
        occurrence_id="occ_1",
        frame_id="f1",
        role_authority_ref="anchor",
        filler_ref="test",
        is_child_frame=False,
        scope_view=(),
    )
    prefix = LinearizationPrefix(
        committed_occurrences=(occ,),
        status="LINEARIZED",
        remaining_uncommitted_ids=frozenset(),
    )
    chunk = gen_engine.realize_surface_chunk(prefix, "rep_test_12", canonical_identity=True)
    assert chunk.origin_lineage == "GENERATION"

    expected_chunk_id = derive_surface_chunk_id(
        parent_representation_id="rep_test_12",
        ordered_surface_unit_ids=[u.unit_id for u in chunk.surface_units],
        rendered_text=chunk.rendered_text,
        closure_reason="COMPLETE",
        origin_lineage="GENERATION",
        prefix="chunk_",
    )
    assert chunk.chunk_id == expected_chunk_id


# ─────────────────────────────────────────────────────────── PIR01-B04: RFC15 Recurrent Canonical Chain (T13 - T15)

def test_pir01_t13_canonical_recurrent_step_end_to_end_identity(clean_graph):
    """PIR01-T13: Recurrent step end-to-end derives canonical obligations, frames, chunks, and receipts."""
    clean_graph.link("w1", "w2", W=1.0, contexts=("en",))
    rep = make_test_rep(clean_graph, "root_13", ["w1", "w2"])
    rec_engine = PredictiveRecurrentGenerativeEngine(clean_graph)
    epoch = rec_engine.create_epoch(
        root_authority_ref="root_13",
        work_ref="rec_work_13",
        canonical_identity=True,
    )
    status, updated_epoch, receipt, _rem_budget = rec_engine.execute_recurrent_step(
        epoch_id=epoch.epoch_id,
        representation=rep,
        budget=5.0,
        canonical_identity=True,
    )
    assert status == "PROGRESS"
    assert receipt is not None
    assert receipt.receipt_id.startswith("er_")
    assert len(receipt.receipt_id) == 67
    assert len(updated_epoch.progress_receipt_refs) == 1


def test_pir01_t14_canonical_expression_receipt_integration(clean_graph):
    """PIR01-T14: Canonical ExpressionReceipt derivation integration."""
    rec_engine = PredictiveRecurrentGenerativeEngine(clean_graph)
    gen_engine = HierarchicalGenerativeEngine(clean_graph)
    occ = LinearizableOccurrence(
        occurrence_id="occ_14",
        frame_id="f14",
        role_authority_ref="anchor",
        filler_ref="word",
        is_child_frame=False,
        scope_view=(),
    )
    prefix = LinearizationPrefix(
        committed_occurrences=(occ,),
        status="LINEARIZED",
        remaining_uncommitted_ids=frozenset(),
    )
    chunk = gen_engine.realize_surface_chunk(prefix, "rep_14", canonical_identity=True)
    unit = chunk.surface_units[0]

    receipt = rec_engine.create_expression_receipt(
        surface_chunk=chunk,
        source_alignment=unit.source_alignment,
        parent_rid="rep_14",
        root_authority_ref="root_14",
        expressed_elements=("word",),
        canonical_identity=True,
    )
    assert receipt.receipt_id.startswith("er_")
    assert len(receipt.receipt_id) == 67


def test_pir01_t15_recurrent_replay_stable_across_fresh_engines(clean_graph):
    """PIR01-T15: Recurrent epoch execution is 100% deterministic across fresh engines."""
    clean_graph.link("k1", "k2", W=1.0, contexts=("en",))
    rep = make_test_rep(clean_graph, "root_15", ["k1", "k2"])

    rec1 = PredictiveRecurrentGenerativeEngine(clean_graph)
    epoch1 = rec1.create_epoch(
        root_authority_ref="root_15",
        work_ref="rec_fixed_work_15",
        canonical_identity=True,
    )
    closure1, handoff1 = rec1.execute_recurrent_epoch(
        epoch_id=epoch1.epoch_id,
        representation=rep,
        budget=10.0,
        canonical_identity=True,
    )

    rec2 = PredictiveRecurrentGenerativeEngine(clean_graph)
    epoch2 = rec2.create_epoch(
        root_authority_ref="root_15",
        work_ref="rec_fixed_work_15",
        canonical_identity=True,
    )
    closure2, handoff2 = rec2.execute_recurrent_epoch(
        epoch_id=epoch2.epoch_id,
        representation=rep,
        budget=10.0,
        canonical_identity=True,
    )

    assert closure1.closure_reason == closure2.closure_reason
    assert handoff1.final_progress_view == handoff2.final_progress_view
    assert epoch1.epoch_id == epoch2.epoch_id


# ─────────────────────────────────────────────────────────── PIR01-B05: Runtime Encapsulation & Lifecycle (T16 - T18)

def test_pir01_t16_mandatory_shared_lifecycle_guard(clean_graph):
    """PIR01-T16: Canonical runtime has mandatory shared lifecycle guard."""
    guard = RuntimeLifecycleGuard()
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(clean_graph, AssemblyPolicy()))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    runtime = CanonicalR1RuntimeRoot(
        graph=clean_graph,
        ledger=ledger,
        observation_protocol_version="1.0.0",
        lifecycle_guard=guard,
    )
    assert runtime.guard is guard

    runtime_auto = CanonicalR1RuntimeRoot(
        graph=clean_graph,
        ledger=ledger,
        observation_protocol_version="1.0.0",
    )
    assert isinstance(runtime_auto.guard, RuntimeLifecycleGuard)


def test_pir01_t17_unsafe_mutable_graph_access_invalidates_lineage(sample_runtime):
    """PIR01-T17: Unsafe mutable graph access or direct mutation invalidates lineage."""
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.VALID

    sample_runtime.graph.link("x", "y", W=1.0, contexts=("en",))
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION


def test_pir01_t18_canonical_save_mutation_blocked_after_lineage_invalidation(sample_runtime, tmp_path):
    """PIR01-T18: Canonical save and command mutation blocked after lineage invalidation."""
    sample_runtime.unsafe_mutable_graph()
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION

    cp_path = tmp_path / "blocked.json"
    with pytest.raises(CausalLineageInvalidatedError):
        save_canonical_r1_checkpoint(sample_runtime, cp_path)

    cmd = PersistentMutationCommand(
        mutation_owner_ref="test",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["x"],
        canonical_mutation_descriptor={"action": "test"},
        owner_defined_transaction_scope="test_scope",
    )
    with pytest.raises(CausalLineageInvalidatedError):
        sample_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id="root_18",
            ingress_event_id="evt_18",
            event_descriptor_digest="digest_18",
            mutator_callback=lambda: None,
        )


# ─────────────────────────────────────────────────────────── PIR01-B06: Atomic Save Durability (T19)

def test_pir01_t19_r1_save_directory_fsync_path(tmp_path):
    """PIR01-T19: Shared atomic save replaces file with durability and best-effort directory fsync."""
    dest = tmp_path / "atomic_test.json"
    content = b'{"test": "atomic_content"}'
    _atomic_replace_file(dest, content)
    assert dest.exists()
    assert dest.read_bytes() == content

    content2 = b'{"test": "updated_content"}'
    _atomic_replace_file(dest, content2)
    assert dest.read_bytes() == content2


# ─────────────────────────────────────────────────────────── PIR01-B07: Semantic Causal Ledger Validation (T20 - T25)

def test_pir01_t20_semantic_ledger_key_record_mismatch_rejection(sample_runtime, tmp_path):
    """PIR01-T20: Semantic ledger key/record mismatch fails closed."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="test",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["a"],
        canonical_mutation_descriptor={"a": "1"},
        owner_defined_transaction_scope="test_scope",
    )
    txid, _, _ = sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_20",
        ingress_event_id="evt_20",
        event_descriptor_digest="20" * 32,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "key_mismatch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    rec = data["causal_provenance_state"]["committed_transactions"].pop(txid)
    data["causal_provenance_state"]["committed_transactions"]["tx_different_key"] = rec

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

    with pytest.raises(CausalIdentityValidationError, match="record transaction_id"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t21_missing_event_binding_rejection(sample_runtime, tmp_path):
    """PIR01-T21: Transaction referencing nonexistent event binding fails closed."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="test",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["a"],
        canonical_mutation_descriptor={"a": "1"},
        owner_defined_transaction_scope="test_scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_21",
        ingress_event_id="evt_21",
        event_descriptor_digest="21" * 32,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "missing_binding.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["causal_provenance_state"]["committed_event_bindings"].clear()

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

    with pytest.raises(CausalIdentityValidationError, match="references missing ingress_event_id"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t22_transaction_binding_root_mismatch_rejection(sample_runtime, tmp_path):
    """PIR01-T22: Transaction/binding root mismatch fails closed."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="test",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["a"],
        canonical_mutation_descriptor={"a": "1"},
        owner_defined_transaction_scope="test_scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_22",
        ingress_event_id="evt_22",
        event_descriptor_digest="22" * 32,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "root_mismatch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["causal_provenance_state"]["committed_event_bindings"]["evt_22"]["root_external_episode_id"] = "different_root"

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

    with pytest.raises(CausalIdentityValidationError, match="!= binding root"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t23_protocol_mismatch_inside_ledger_rejection(sample_runtime, tmp_path):
    """PIR01-T23: Observation protocol mismatch inside ledger fails closed."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="test",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["a"],
        canonical_mutation_descriptor={"a": "1"},
        owner_defined_transaction_scope="test_scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_23",
        ingress_event_id="evt_23",
        event_descriptor_digest="23" * 32,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "protocol_ledger_mismatch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["causal_provenance_state"]["committed_event_bindings"]["evt_23"]["observation_protocol_version"] = "9.9.9"

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

    with pytest.raises(CausalIdentityValidationError, match="observation_protocol_version .* != checkpoint"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t24_provenance_epoch_state_digest_mismatch_rejection(sample_runtime, tmp_path):
    """PIR01-T24: Provenance epoch base_state_digest mismatch with checkpoint fails closed."""
    cp_path = tmp_path / "epoch_digest_mismatch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["causal_provenance_state"]["causal_provenance_epoch"]["base_state_digest"] = "tampered_base_digest_" + "0" * 43

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

    with pytest.raises(CausalIdentityValidationError, match="base_state_digest mismatch"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir01_t25_malformed_redigested_provenance_fails_closed(sample_runtime, tmp_path):
    """PIR01-T25: Semantically malformed ledger fails closed even when fully re-digested."""
    cp_path = tmp_path / "malformed_redigested.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["causal_provenance_state"]["committed_transactions"]["tx_bad"] = {"transaction_id": "tx_bad"}

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

    with pytest.raises(CausalIdentityValidationError):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


# ─────────────────────────────────────────────────────────── PIR01-D01: Mapping-Key Collision Hardening (T26)

def test_pir01_t26_mapping_non_string_key_rejected():
    """PIR01-T26: Non-string mapping keys and potential key collisions are strictly rejected."""
    with pytest.raises(CausalIdentityValidationError, match="Mapping keys in authoritative R1 payload must be strings"):
        canonicalize_payload({1: "a"})

    with pytest.raises(CausalIdentityValidationError, match="Mapping keys in authoritative R1 payload must be strings"):
        canonicalize_payload({1: "a", "1": "b"})

    with pytest.raises(CausalIdentityValidationError, match="Mapping keys in authoritative R1 payload must be strings"):
        canonicalize_payload({"outer": {True: "bool_val"}})

    valid_payload = {"z": 1, "a": 2, "m": [3, 4]}
    canonical = canonicalize_payload(valid_payload)
    assert canonical == {"z": 1, "a": 2, "m": [3, 4]}
    dumped = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    assert dumped == '{"a":2,"m":[3,4],"z":1}'


# ─────────────────────────────────────────────────────────── Baseline Signature Gate (T27)

def test_pir01_t27_no_cognitive_baseline_drift():
    """PIR01-T27: Cognitive baseline signature remains exact 915119d40643cb97 with zero bit drift."""
    sig = behavioral_signature(build_reference_graph())
    assert sig == "915119d40643cb97"
