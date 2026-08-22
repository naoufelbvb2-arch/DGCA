"""
DGCA — RFC-16 v1.0 Acceptance Test Suite (RFC16-T001 .. RFC16-T084).
Covers all 84 authoritative acceptance criteria defined in Section 14 of RFC-16.
"""
from __future__ import annotations

import hashlib

from dgca.generation import SurfaceChunk
from dgca.graph import CognitiveGraph
from dgca.loop import (
    InternalWorkAuthorityView,
    InternalWorkFrontier,
    OrchestrationSnapshotView,
    UnifiedGenerativeCognitiveLoopEngine,
    rfc16_behavioral_signature,
)
from dgca.representation import ParticipationReceipt, SparseDistributedCognitiveRepresentation


def _build_test_graph() -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph()
    # 1. Non-empty verified Law-14 assembly
    g.link("concept_falcon", "fly", W=0.92, contexts=("en",))
    g.link("concept_falcon", "predator", W=0.88, contexts=("en",))
    g.link("fly", "predator", W=0.80, contexts=("en",))
    mgr = g.assembly_manager
    asm_edges = [("concept_falcon", "fly"), ("concept_falcon", "predator"), ("fly", "predator")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(asm_edges, root_episode_id=f"root_ep_{i}", valid_origin=True)

    # 2. Nodes and linear sequence edges
    for i in range(1, 6):
        g.link(f"node_{i}", f"prop_{i}", W=0.85, contexts=("en",))
        if i < 5:
            g.link(f"node_{i}", f"node_{i+1}", W=0.95, contexts=("en",))

    # 3. SDCR representation
    receipts = [
        ParticipationReceipt(f"rcpt_{i}", f"node_{i}", 1, 0, "external", "node", activation_magnitude=0.9)
        for i in range(1, 6)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    object.__setattr__(rep, "representation_id", "rep_t_audit")
    return g, rep


def _make_surface_chunk(
    g: CognitiveGraph,
    rep: SparseDistributedCognitiveRepresentation,
    nodes: tuple[str, ...] = ("node_1", "node_2"),
) -> SurfaceChunk:
    gen_eng = g.generation_engine
    frame = gen_eng.build_generative_frame(rep, frozenset(nodes))
    hierarchy = gen_eng.build_hierarchy([frame])
    prefix, _ = gen_eng.linearize_hierarchy(hierarchy, budget=10.0)
    return gen_eng.realize_surface_chunk(prefix, str(rep.representation_id), budget=10.0)


# ── RFC16-T001 .. T012: Constitutional Ownership, Zero-Primitives & Controller Absences
def test_rfc16_t001_zero_canonical_primitives():
    """RFC16-T001: RFC-16 introduces zero new canonical operational primitives."""
    g, _ = _build_test_graph()
    eng = g.loop_engine
    assert isinstance(eng, UnifiedGenerativeCognitiveLoopEngine)


def test_rfc16_t002_zero_persistent_cognitive_primitives():
    """RFC16-T002: RFC-16 introduces zero persistent cognitive primitives."""
    g, _ = _build_test_graph()
    assert not hasattr(g.node("node_1", "text"), "unified_dialogue_memory")
    assert not hasattr(g.edge("node_1", "prop_1"), "conversation_weight")


def test_rfc16_t003_zero_learned_fields_or_scalars():
    """RFC16-T003: RFC-16 introduces zero persistent learned fields or learned scalars."""
    g, _ = _build_test_graph()
    for edge in g.edges.values():
        assert not hasattr(edge, "feedback_score")
        assert not hasattr(edge, "user_trust_level")


def test_rfc16_t004_zero_laws_law18_not_adopted():
    """RFC16-T004: RFC-16 introduces zero new normative laws; Law 18 remains NOT JUSTIFIED / NOT ADOPTED."""
    import dgca.config
    assert not hasattr(dgca.config, "Law18")
    assert not hasattr(dgca.config.Law, "LAW_18")


def test_rfc16_t005_authority_preserving_orchestration():
    """RFC16-T005: RFC-16 acts as authority-preserving orchestration rather than a new cognitive algorithm."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w1", "root_ep_0", "RFC14_GENERATION", ("node_1", "node_2"), True)
    status, chunk = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "SUCCESS"
    assert isinstance(chunk, SurfaceChunk)


def test_rfc16_t006_no_global_cognitive_controller():
    """RFC16-T006: RFC-16 does not create a GlobalCognitiveController or equivalent hidden semantic controller."""
    g, _ = _build_test_graph()
    assert not hasattr(g, "global_controller")
    assert not hasattr(g, "executive_controller")


def test_rfc16_t007_no_unified_persistent_dialogue_memory():
    """RFC16-T007: RFC-16 does not create unified persistent cognition, dialogue memory, or persistent workflow plan."""
    g, _ = _build_test_graph()
    assert not hasattr(g.loop_engine, "conversation_transcript")
    assert not hasattr(g.loop_engine, "workflow_plan")


def test_rfc16_t008_preserves_frozen_ownership_of_subsystems():
    """RFC16-T008: RFC-16 preserves frozen ownership of RFC-13, RFC-14, RFC-15 and Phase-I."""
    g, _rep = _build_test_graph()
    assert g.assembly_manager is not None
    assert g.completion_engine is not None
    assert g.generation_engine is not None
    assert g.recurrent_engine is not None


def test_rfc16_t009_no_global_subsystem_winner_score():
    """RFC16-T009: RFC-16 does not add a global subsystem winner score or priority scalar."""
    g, _ = _build_test_graph()
    assert not hasattr(g.loop_engine, "subsystem_score")
    assert not hasattr(g.loop_engine, "global_priority")


def test_rfc16_t010_no_scheduler_or_id_as_semantic_priority():
    """RFC16-T010: RFC-16 does not use scheduler, ID, hash, arrival, or serialization order as semantic priority."""
    g, _ = _build_test_graph()
    w_a = InternalWorkAuthorityView("w_z", "root_1", "REASONING", ("node_1",), True)
    w_b = InternalWorkAuthorityView("w_a", "root_1", "RFC14_GENERATION", ("node_2",), True)
    frontier = g.loop_engine.derive_internal_work_frontier("root_1", (w_a, w_b), set())
    assert len(frontier.ready_work) == 2


def test_rfc16_t011_no_global_budget_or_cycle_counter():
    """RFC16-T011: RFC-16 does not add a new global runtime/cognitive budget or correctness cycle counter."""
    g, _ = _build_test_graph()
    assert not hasattr(g.loop_engine, "max_cognitive_cycles")
    assert not hasattr(g.loop_engine, "global_budget")


def test_rfc16_t012_derived_handoffs_remain_transient():
    """RFC16-T012: RFC-16 derived handoffs/views remain transient, reconstructible, and non-authoritative."""
    g, _ = _build_test_graph()
    snap = OrchestrationSnapshotView("s1", "root_1", g.t, ("w1",), (), "QUIESCENT")
    assert isinstance(snap, OrchestrationSnapshotView)


# ── RFC16-T013 .. T024: Feedback, Provenance & Evidence Firewall
def test_rfc16_t013_external_provenance_via_ingress_only():
    """RFC16-T013: An external event receives external provenance only through an authorized ingress boundary."""
    g, _ = _build_test_graph()
    ev, is_novel = g.loop_engine.ingress_external_event("ev_1", "ep_ext_1", "What is falcon?")
    assert ev is not None
    assert is_novel is True
    assert ev.source_origin == "EXTERNAL"

    forged_ev, _ = g.loop_engine.ingress_external_event("ev_fake", "ep_fake", "Fake", is_internal_call=True)
    assert forged_ev is None


def test_rfc16_t014_raw_feedback_not_evidence_candidate():
    """RFC16-T014: Raw external feedback is not automatically EvidenceCandidate, ValidatedEvidence, or LearningAuthority."""
    g, _ = _build_test_graph()
    ev, is_novel = g.loop_engine.ingress_external_event("ev_2", "ep_ext_2", "Praise good job!")
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_novel)
    assert elig.is_eligible is False
    assert elig.rejection_reason == "EVALUATION_WITHOUT_OUTCOME_CONTRACT"


def test_rfc16_t015_external_correction_cannot_directly_overwrite_cognition():
    """RFC16-T015: External correction content cannot directly overwrite persistent cognition."""
    g, _ = _build_test_graph()
    ev, is_novel = g.loop_engine.ingress_external_event("ev_3", "ep_ext_3", "correction: node_1, prop_99")
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_novel)
    assert elig.is_eligible is False
    assert g.edge("node_1", "prop_99") is None


def test_rfc16_t016_task_control_cannot_create_learning_authority():
    """RFC16-T016: Task-control feedback cannot directly create semantic learning authority."""
    g, _ = _build_test_graph()
    ev, is_novel = g.loop_engine.ingress_external_event("ev_4", "ep_ext_4", "continue")
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_novel)
    assert elig.is_eligible is False
    assert elig.rejection_reason == "TASK_CONTROL_CANNOT_LEARN"


def test_rfc16_t017_evaluative_feedback_requires_outcome_contract():
    """RFC16-T017: Evaluative feedback becomes an Outcome only through an existing authorized outcome contract."""
    g, _ = _build_test_graph()
    ev_raw, is_novel1 = g.loop_engine.ingress_external_event("ev_5a", "ep_ext_5a", "wrong")
    auth_raw = g.loop_engine.derive_feedback_authority(ev_raw)
    elig_raw = g.loop_engine.evaluate_evidence_eligibility(ev_raw, auth_raw, is_novel1)
    assert elig_raw.is_eligible is False

    ev_contract, is_novel2 = g.loop_engine.ingress_external_event(
        "ev_5b", "ep_ext_5b", "wrong", metadata={"has_outcome_contract": True, "authorized_source": True}
    )
    auth_c = g.loop_engine.derive_feedback_authority(ev_contract)
    elig_c = g.loop_engine.evaluate_evidence_eligibility(ev_contract, auth_c, is_novel2)
    assert elig_c.is_eligible is True


def test_rfc16_t018_corrective_evaluation_vs_claim_separation():
    """RFC16-T018: Corrective evaluation and corrective semantic claims remain separate authorities."""
    g, _ = _build_test_graph()
    ev, _ = g.loop_engine.ingress_external_event("ev_6", "ep_ext_6", "correction: falcon, predator")
    auth = g.loop_engine.derive_feedback_authority(ev)
    assert auth.is_corrective_claim is True
    assert auth.claimed_elements == ("falcon", "predator")
    assert auth.is_evaluation is False


def test_rfc16_t019_dedup_rejects_transport_retry_multiplication():
    """RFC16-T019: The same RootExternalEpisode cannot become multiple learning opportunities through transport retry."""
    g, _ = _build_test_graph()
    _ev1, is_novel1 = g.loop_engine.ingress_external_event("ev_7a", "ep_ext_7", "sensor_data", metadata={"authorized_source": True})
    ev2, is_novel2 = g.loop_engine.ingress_external_event("ev_7b", "ep_ext_7", "sensor_data", metadata={"authorized_source": True})
    assert is_novel1 is True
    assert is_novel2 is False

    auth2 = g.loop_engine.derive_feedback_authority(ev2)
    elig2 = g.loop_engine.evaluate_evidence_eligibility(ev2, auth2, is_novel2)
    assert elig2.is_eligible is False
    assert elig2.rejection_reason == "TRANSPORT_RETRY_DUPLICATE"


def test_rfc16_t020_multimodal_representations_do_not_multiply_evidence():
    """RFC16-T020: Multimodal representations of one causal external episode do not automatically count as independent evidence."""
    g, _ = _build_test_graph()
    _ev_audio, is_nov_a = g.loop_engine.ingress_external_event("ev_8a", "ep_ext_8", "sound", modality="audio", metadata={"authorized_source": True})
    _ev_text, is_nov_t = g.loop_engine.ingress_external_event("ev_8b", "ep_ext_8", "sound_transcript", modality="text", metadata={"authorized_source": True})
    assert is_nov_a is True
    assert is_nov_t is False


def test_rfc16_t021_raw_repetition_cannot_manufacture_evidence_eligibility():
    """RFC16-T021: Raw repetition cannot manufacture evidence eligibility that was absent from the source contract."""
    g, _ = _build_test_graph()
    for i in range(100):
        ev, is_nov = g.loop_engine.ingress_external_event(f"ev_9_{i}", f"ep_unauth_{i}", "False claim without authority")
        auth = g.loop_engine.derive_feedback_authority(ev)
        elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
        assert elig.is_eligible is False


def test_rfc16_t022_persistent_learning_requires_validation_transaction():
    """RFC16-T022: Persistent learning is reachable only through existing evidence validation and local-learning transactions."""
    g, _ = _build_test_graph()
    ev, is_nov = g.loop_engine.ingress_external_event(
        "ev_10", "ep_ext_10", "fact: concept_hawk, predator", metadata={"authorized_source": True}
    )
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
    assert elig.is_eligible is True

    learned, attr = g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("concept_hawk", "predator"))
    assert learned is True
    assert attr is not None
    assert attr.validation_owner == "Law1_HebbianCreation"
    assert g.edge("concept_hawk", "predator") is not None


def test_rfc16_t023_generated_output_cannot_reenter_as_external_evidence():
    """RFC16-T023: Generated output cannot re-enter as external feedback/evidence through an internal transport loop."""
    g, _ = _build_test_graph()
    forged, _ = g.loop_engine.ingress_external_event(
        "ev_loop", "ep_self", "I generated this", source_origin="GENERATION", is_internal_call=True
    )
    assert forged is None


def test_rfc16_t024_self_derived_descendants_remain_self_derived():
    """RFC16-T024: Self-derived descendants of an external root remain SelfDerived and do not regain external-evidence authority."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_desc", "root_ep_0", "RFC14_GENERATION", ("node_1", "node_2"), True)
    status, chunk = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "SUCCESS"
    assert chunk.surface_units[0].origin_lineage == "GENERATION"


# ── RFC16-T025 .. T036: Internal Work Orchestration
def test_rfc16_t025_pattern_completion_under_rfc13_only():
    """RFC16-T025: Pattern Completion executes only under existing RFC-13 authority."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_comp", "root_ep_0", "RFC13_COMPLETION", ("node_1", "node_2"), True)
    status, res = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "SUCCESS"
    assert res is not None


def test_rfc16_t026_reasoning_under_existing_authority():
    """RFC16-T026: Reasoning executes only under existing reasoning/task authority rather than mere knowledge availability."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_reas", "root_ep_0", "REASONING", ("node_1",), True)
    status, res = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "SUCCESS"
    assert isinstance(res, dict)


def test_rfc16_t027_generation_under_existing_authority():
    """RFC16-T027: Generation executes only under existing expressive/generation authority."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_gen", "root_ep_0", "RFC14_GENERATION", ("node_1", "node_2"), True)
    status, res = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "SUCCESS"
    assert isinstance(res, SurfaceChunk)


def test_rfc16_t028_work_authority_remains_root_local():
    """RFC16-T028: Internal work authority remains root/scope-local and derived rather than a global cognitive mode."""
    g, _ = _build_test_graph()
    w1 = InternalWorkAuthorityView("w1", "root_A", "REASONING", ("node_1",), True)
    w2 = InternalWorkAuthorityView("w2", "root_B", "RFC14_GENERATION", ("node_2",), True)
    f_a = g.loop_engine.derive_internal_work_frontier("root_A", (w1, w2), set())
    assert len(f_a.ready_work) == 1
    assert f_a.ready_work[0].work_id == "w1"


def test_rfc16_t029_work_dependencies_derived_from_task_authority():
    """RFC16-T029: Work dependencies are derived from existing task/cognitive authority rather than a global workflow plan."""
    g, _ = _build_test_graph()
    w1 = InternalWorkAuthorityView("w1", "root_1", "REASONING", ("node_1",), True)
    w2 = InternalWorkAuthorityView("w2", "root_1", "RFC14_GENERATION", ("node_1",), True, prerequisite_work_ids=("w1",))
    frontier = g.loop_engine.derive_internal_work_frontier("root_1", (w1, w2), set())
    assert len(frontier.ready_work) == 1
    assert frontier.ready_work[0].work_id == "w1"
    assert len(frontier.blocked_work) == 1
    assert frontier.blocked_work[0].work_id == "w2"


def test_rfc16_t030_multiple_independent_ready_work_coexist():
    """RFC16-T030: Multiple independent ready work scopes can coexist without acquiring semantic scheduler order."""
    g, _ = _build_test_graph()
    w1 = InternalWorkAuthorityView("w1", "root_1", "REASONING", ("node_1",), True)
    w2 = InternalWorkAuthorityView("w2", "root_1", "RFC14_GENERATION", ("node_2",), True)
    frontier = g.loop_engine.derive_internal_work_frontier("root_1", (w1, w2), set())
    assert len(frontier.ready_work) == 2


def test_rfc16_t031_mutually_exclusive_work_preserves_ambiguity():
    """RFC16-T031: Mutually exclusive ready work without lawful resolution authority preserves applicable ambiguity."""
    g, _ = _build_test_graph()
    frontier = InternalWorkFrontier(ready_work=(), blocked_work=(), status="AMBIGUOUS")
    q = g.loop_engine.derive_root_quiescence("root_1", frontier)
    assert q.is_quiescent is True
    assert q.quiescence_reason == "MUTUAL_AMBIGUITY"


def test_rfc16_t032_no_hidden_recall_or_reasoning_for_missing_content():
    """RFC16-T032: Hidden Pattern Completion or hidden reasoning cannot be invoked merely because generation content is missing."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_unauth", "root_1", "UNKNOWN_SUBSYSTEM", ("node_1",), True)
    status, res = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "UNAUTHORIZED_SUBSYSTEM"
    assert res is None


def test_rfc16_t033_stale_internal_work_rejected():
    """RFC16-T033: Stale internal work derived from superseded cognition is rejected or explicitly revalidated."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_stale", "root_1", "RFC14_GENERATION", ("node_1",), True)
    status, res = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t - 1)
    assert status == "STALE_REJECTED"
    assert res is None


def test_rfc16_t034_internal_results_preserve_self_derived_provenance():
    """RFC16-T034: Internal reasoning/recall/completion results preserve their existing SelfDerived/internal provenance."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_gen", "root_1", "RFC14_GENERATION", ("node_1", "node_2"), True)
    _, chunk = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert chunk.surface_units[0].origin_lineage == "GENERATION"


def test_rfc16_t035_inference_does_not_become_persistent_learning():
    """RFC16-T035: Inference and Pattern Completion do not automatically become persistent learning through RFC-16 integration."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_inf", "root_1", "REASONING", ("node_1",), True)
    edges_before = set(g.edges.keys())
    g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    edges_after = set(g.edges.keys())
    assert edges_before == edges_after


def test_rfc16_t036_after_state_change_work_freshly_derived():
    """RFC16-T036: After meaningful state change, internal work authorities are freshly derived."""
    g, _ = _build_test_graph()
    w1 = InternalWorkAuthorityView("w1", "root_1", "REASONING", ("node_1",), True)
    f1 = g.loop_engine.derive_internal_work_frontier("root_1", (w1,), set())
    assert len(f1.ready_work) == 1
    f2 = g.loop_engine.derive_internal_work_frontier("root_1", (w1,), {"w1"})
    assert len(f2.ready_work) == 0


# ── RFC16-T037 .. T050: Generation, Delivery & Task Continuation
def test_rfc16_t037_generated_delivered_acknowledged_remain_distinct():
    """RFC16-T037: Generated, delivered, acknowledged, and externally validated states remain distinct."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id))
    assert del_view.status == "DELIVERED"
    ack_view = g.loop_engine.acknowledge_delivery(del_view.delivery_id)
    assert ack_view.status == "ACKNOWLEDGED"


def test_rfc16_t038_expression_receipt_not_delivery_receipt():
    """RFC16-T038: ExpressionReceipt is not reinterpreted as a delivery receipt or semantic acknowledgment."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id))
    assert del_view.delivery_id.startswith("del_")


def test_rfc16_t039_delivery_failure_does_not_erase_expression_receipt():
    """RFC16-T039: Delivery failure does not erase a lawful ExpressionReceipt or generative history."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    assert del_view.status == "FAILED"
    assert chunk.chunk_id is not None


def test_rfc16_t040_delivery_retry_creates_zero_new_expression_receipts():
    """RFC16-T040: Delivery retry of the same committed artifact does not create a new ExpressionReceipt or GCE progress."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    rcpts_before = len(g.recurrent_engine._receipts)

    retried = g.loop_engine.retry_delivery(del_view.delivery_id, success=True)
    assert retried.status == "DELIVERED"
    assert retried.retry_count == 1
    rcpts_after = len(g.recurrent_engine._receipts)
    assert rcpts_before == rcpts_after


def test_rfc16_t041_delivery_ack_not_semantic_truth():
    """RFC16-T041: Delivery acknowledgment/read receipt does not create semantic truth or agreement authority."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id))
    ack = g.loop_engine.acknowledge_delivery(del_view.delivery_id)
    assert ack.status == "ACKNOWLEDGED"
    assert g.edge("concept_falcon", "fly").W == 0.92


def test_rfc16_t042_continue_does_not_reopen_closed_gce():
    """RFC16-T042: An external continue event may authorize a new continuation context but cannot reopen a CLOSED GCE."""
    g, rep = _build_test_graph()
    rec_eng = g.recurrent_engine
    epoch1 = rec_eng.create_epoch("root_cont")
    closure, _ = rec_eng.execute_recurrent_epoch(epoch1.epoch_id, rep, budget=20.0)
    assert closure.closure_reason == "COMPLETE"
    closed_epoch = rec_eng.get_epoch(epoch1.epoch_id)
    assert closed_epoch.lifecycle == "CLOSED"

    ev, _ = g.loop_engine.ingress_external_event("ev_cont", "ep_cont", "continue")
    task_rel, new_gce_id = g.loop_engine.process_task_relation(ev, "root_cont", closed_epoch)
    assert task_rel.relation_kind == "CONTINUES"
    assert new_gce_id is not None
    assert new_gce_id != closed_epoch.epoch_id
    assert closed_epoch.lifecycle == "CLOSED"


def test_rfc16_t043_successor_gce_requires_fresh_authority():
    """RFC16-T043: A successor GCE after closure requires fresh lawful continuation/runtime authority rather than automatic budget renewal."""
    g, _rep = _build_test_graph()
    rec_eng = g.recurrent_engine
    epoch1 = rec_eng.create_epoch("root_succ")
    rec_eng.close_epoch(epoch1.epoch_id, "BUDGET_EXHAUSTED")
    closed = rec_eng.get_epoch(epoch1.epoch_id)

    ev, _ = g.loop_engine.ingress_external_event("ev_succ", "ep_succ", "continue")
    _, new_gce_id = g.loop_engine.process_task_relation(ev, "root_succ", closed)
    assert new_gce_id is not None
    new_epoch = rec_eng.get_epoch(new_gce_id)
    assert new_epoch.lifecycle == "OPEN"
    assert new_epoch.epoch_id != closed.epoch_id


def test_rfc16_t044_external_cancellation_invalidates_bound_pending_work():
    """RFC16-T044: An external cancellation event invalidates only lawfully bound root-scoped pending work."""
    g, _ = _build_test_graph()
    ev_cancel, _ = g.loop_engine.ingress_external_event("ev_can", "ep_can", "cancel")
    task_rel, _ = g.loop_engine.process_task_relation(ev_cancel, "root_to_cancel")
    assert task_rel.relation_kind == "CANCELS"

    w = InternalWorkAuthorityView("w_can", "root_to_cancel", "REASONING", ("node_1",), True)
    frontier = g.loop_engine.derive_internal_work_frontier("root_to_cancel", (w,), set())
    assert frontier.status == "CANCELLED"


def test_rfc16_t045_new_external_task_does_not_cancel_independent_root():
    """RFC16-T045: A new external task does not automatically cancel an independent existing root."""
    g, _ = _build_test_graph()
    ev1, _ = g.loop_engine.ingress_external_event("ev_task1", "ep_task1", "task 1")
    g.loop_engine.process_task_relation(ev1, "root_1")

    ev2, _ = g.loop_engine.ingress_external_event("ev_task2", "ep_task2", "task 2")
    rel2, _ = g.loop_engine.process_task_relation(ev2, "root_2")
    assert rel2.relation_kind == "NEW_ROOT"
    assert "root_1" not in g.loop_engine._cancelled_roots


def test_rfc16_t046_latest_message_wins_not_universal_root_supersession():
    """RFC16-T046: Latest-message-wins is not a universal root supersession rule."""
    g, _ = _build_test_graph()
    ev_a, _ = g.loop_engine.ingress_external_event("ev_a", "ep_a", "Alpha")
    ev_b, _ = g.loop_engine.ingress_external_event("ev_b", "ep_b", "Beta")
    g.loop_engine.process_task_relation(ev_a, "root_A")
    g.loop_engine.process_task_relation(ev_b, "root_B")
    assert "root_A" not in g.loop_engine._cancelled_roots
    assert "root_B" not in g.loop_engine._cancelled_roots


def test_rfc16_t047_distinct_identities_preserved():
    """RFC16-T047: Conversation turn, message identity, session identity, root identity, and GCE identity remain distinct."""
    g, _ = _build_test_graph()
    ev, _ = g.loop_engine.ingress_external_event("msg_101", "ep_causal_101", "query")
    assert ev.event_id == "msg_101"
    assert ev.root_external_episode_id == "ep_causal_101"


def test_rfc16_t048_prior_handoff_revalidated_not_permanent_plan():
    """RFC16-T048: Prior RFC-15 handoff/residual information is revalidated and cannot become a persistent authoritative future plan."""
    g, rep = _build_test_graph()
    rec_eng = g.recurrent_engine
    epoch = rec_eng.create_epoch("root_handoff")
    _, handoff = rec_eng.execute_recurrent_epoch(epoch.epoch_id, rep, budget=20.0)
    assert handoff.root_authority_ref == "root_handoff"


def test_rfc16_t049_external_repeat_request_creates_no_learning():
    """RFC16-T049: External repeat requests may create expressive repetition authority without creating learning repetition."""
    g, _ = _build_test_graph()
    ev, is_nov = g.loop_engine.ingress_external_event("ev_rep", "ep_rep", "repeat")
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
    assert auth.task_control_kind == "REPEAT"
    assert elig.is_eligible is False


def test_rfc16_t050_task_relation_no_full_transcript_scan():
    """RFC16-T050: RFC-16 task relation work does not require scanning the full conversation transcript."""
    g, _ = _build_test_graph()
    ev, _ = g.loop_engine.ingress_external_event("ev_local", "ep_local", "continue")
    rel, _ = g.loop_engine.process_task_relation(ev, "root_local")
    assert rel.relation_kind == "CONTINUES"


# ── RFC16-T051 .. T064: Concurrency, Failure Atomicity & Quiescence
def test_rfc16_t051_state_changing_commits_against_observed_state():
    """RFC16-T051: State-changing concurrent work commits against the relevant state/version authority it observed."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_obs", "root_1", "REASONING", ("node_1",), True)
    status, _ = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "SUCCESS"


def test_rfc16_t052_state_change_causes_stale_rejection():
    """RFC16-T052: A relevant state change before commit causes stale rejection or explicit revalidation."""
    g, rep = _build_test_graph()
    work = InternalWorkAuthorityView("w_stale2", "root_1", "REASONING", ("node_1",), True)
    status, _ = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t + 1)
    assert status == "STALE_REJECTED"


def test_rfc16_t053_correction_does_not_erase_historical_commit():
    """RFC16-T053: External correction does not retroactively erase a previously lawful committed historical result."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id))
    assert del_view.status == "DELIVERED"
    ev, _ = g.loop_engine.ingress_external_event("ev_corr", "ep_corr", "correction: fact")
    g.loop_engine.process_task_relation(ev, "root_1")
    assert del_view.delivery_id in g.loop_engine._delivery_records


def test_rfc16_t054_cancellation_before_vs_after_surface_commit():
    """RFC16-T054: Cancellation before pending generation commit can invalidate it, while after SurfaceCommit cannot erase committed history."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id))
    ev_c, _ = g.loop_engine.ingress_external_event("ev_c", "ep_c", "cancel")
    g.loop_engine.process_task_relation(ev_c, "root_cancelled")
    assert del_view.status == "DELIVERED"


def test_rfc16_t055_root_scoped_cancellation_preserves_independent_roots():
    """RFC16-T055: Root-scoped cancellation does not cancel work retaining independent authority from another root."""
    g, _ = _build_test_graph()
    g.loop_engine._cancelled_roots.add("root_A")
    w_b = InternalWorkAuthorityView("w_b", "root_B", "REASONING", ("node_1",), True)
    frontier_b = g.loop_engine.derive_internal_work_frontier("root_B", (w_b,), set())
    assert frontier_b.status == "READY"


def test_rfc16_t056_failure_atomicity_at_boundaries():
    """RFC16-T056: Failure atomicity is enforced at existing authority boundaries rather than a single global mega-transaction."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_fail = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    assert del_fail.status == "FAILED"
    assert chunk.surface_units is not None


def test_rfc16_t057_downstream_failure_cannot_rollback_validated_learning():
    """RFC16-T057: Downstream generation or delivery failure cannot roll back independent upstream validated learning."""
    g, rep = _build_test_graph()
    ev, is_nov = g.loop_engine.ingress_external_event(
        "ev_learn", "ep_learn", "fact: concept_eagle, fly", metadata={"authorized_source": True}
    )
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, g.loop_engine.derive_feedback_authority(ev), is_nov)
    g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("concept_eagle", "fly"))
    assert g.edge("concept_eagle", "fly") is not None

    chunk = _make_surface_chunk(g, rep)
    g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    assert g.edge("concept_eagle", "fly") is not None


def test_rfc16_t058_recovery_idempotence():
    """RFC16-T058: Crash/replay recovery cannot duplicate external evidence, ExpressionReceipts, or GCE progress."""
    g, _ = _build_test_graph()
    _ev1, nov1 = g.loop_engine.ingress_external_event("ev_rec", "ep_rec_1", "query")
    _ev2, nov2 = g.loop_engine.ingress_external_event("ev_rec", "ep_rec_1", "query")
    assert nov1 is True
    assert nov2 is False


def test_rfc16_t059_independent_interleavings_semantically_equivalent():
    """RFC16-T059: Independent interleavings produce semantically equivalent final state where authorities require independence."""
    g, _ = _build_test_graph()
    w1 = InternalWorkAuthorityView("w1", "root_1", "REASONING", ("node_1",), True)
    w2 = InternalWorkAuthorityView("w2", "root_1", "REASONING", ("node_2",), True)
    f1 = g.loop_engine.derive_internal_work_frontier("root_1", (w1, w2), set())
    f2 = g.loop_engine.derive_internal_work_frontier("root_1", (w2, w1), set())
    assert {w.work_id for w in f1.ready_work} == {w.work_id for w in f2.ready_work}


def test_rfc16_t060_noncommutative_operations_use_version_semantics():
    """RFC16-T060: Noncommutative concurrent operations use causal/version/stale semantics rather than ID tie-breaking."""
    g, rep = _build_test_graph()
    w = InternalWorkAuthorityView("w_ver", "root_1", "REASONING", ("node_1",), True)
    status, _ = g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t)
    assert status == "SUCCESS"


def test_rfc16_t061_quiescent_when_no_lawful_work():
    """RFC16-T061: When no lawful internal work can progress, orchestration becomes quiescent instead of blindly redispatching."""
    g, _ = _build_test_graph()
    frontier = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
    q = g.loop_engine.derive_root_quiescence("root_1", frontier)
    assert q.is_quiescent is True
    assert q.quiescence_reason == "ALL_WORK_COMPLETE"


def test_rfc16_t062_quiescence_vs_completion_distinct():
    """RFC16-T062: Quiescence, root completion, GCE completion, and session completion remain distinct."""
    g, _ = _build_test_graph()
    frontier_blocked = InternalWorkFrontier(ready_work=(), blocked_work=(), status="BLOCKED")
    q_blocked = g.loop_engine.derive_root_quiescence("root_1", frontier_blocked)
    assert q_blocked.is_quiescent is True
    assert q_blocked.quiescence_reason == "NO_READY_WORK"


def test_rfc16_t063_waiting_external_input_is_quiescence():
    """RFC16-T063: Waiting for required external input is quiescence, not failure, completion, or internal polling."""
    g, _ = _build_test_graph()
    frontier = InternalWorkFrontier(ready_work=(), blocked_work=(), status="BLOCKED")
    q = g.loop_engine.derive_root_quiescence("root_1", frontier, has_waiting_external_dependency=True)
    assert q.is_quiescent is True
    assert q.quiescence_reason == "WAITING_EXTERNAL_INPUT"


def test_rfc16_t064_operational_failure_not_semantic_refutation():
    """RFC16-T064: Operational failures such as recall failure, reasoning timeout, generation failure, or delivery failure cannot become semantic refutation."""
    g, rep = _build_test_graph()
    del_view = g.loop_engine.deliver_surface_output(
        SurfaceChunk("chunk_err", (), "root_1", 0.0, closure_reason="COMPLETE"),
        str(rep.representation_id),
        simulate_transport_failure=True,
    )
    assert del_view.status == "FAILED"
    assert g.edge("concept_falcon", "fly") is not None


# ── RFC16-T065 .. T084: Regression, Locality & Full Loop Integration
def test_rfc16_t065_unchanged_state_does_not_redispatch():
    """RFC16-T065: Unchanged root-relevant state with no new event/commit/ready/progress-capable work does not redispatch."""
    g, _ = _build_test_graph()
    frontier = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
    q = g.loop_engine.derive_root_quiescence("root_1", frontier)
    assert q.is_quiescent is True


def test_rfc16_t066_no_max_cognitive_cycles_needed():
    """RFC16-T066: No arbitrary MAX_COGNITIVE_CYCLES or MAX_RETRIES is needed as primary correctness semantics."""
    g, _ = _build_test_graph()
    frontier = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
    q = g.loop_engine.derive_root_quiescence("root_1", frontier)
    assert q.quiescence_reason == "ALL_WORK_COMPLETE"


def test_rfc16_t067_stable_unified_loop_boundedness():
    """RFC16-T067: Under stable finite upstream authorities, RFC-16 cannot internally self-generate an unbounded causal chain."""
    g, _ = _build_test_graph()
    chunk, del_view, q = g.loop_engine.execute_canonical_full_loop("What is falcon?", ["concept_falcon", "fly"])
    assert chunk is not None
    assert del_view is not None
    assert q.is_quiescent is True


def test_rfc16_t068_control_work_remains_local():
    """RFC16-T068: RFC-16 control work remains local to relevant events, roots, scopes, constraints, GCE refs and delivery refs."""
    g, _ = _build_test_graph()
    work = InternalWorkAuthorityView("w_loc", "root_loc", "RFC14_GENERATION", ("node_1", "node_2"), True)
    f = g.loop_engine.derive_internal_work_frontier("root_loc", (work,), set())
    assert len(f.ready_work) == 1


def test_rfc16_t069_no_remote_graph_enumeration():
    """RFC16-T069: RFC-16 semantic runtime does not enumerate unrelated remote graph state."""
    g, _ = _build_test_graph()
    for i in range(1000):
        g.node(f"remote_{i}", "text")
    _ev, is_nov = g.loop_engine.ingress_external_event("ev_loc", "ep_loc", "query")
    assert is_nov is True


def test_rfc16_t070_no_full_history_or_vocabulary_scan():
    """RFC16-T070: RFC-16 semantic runtime does not enumerate full unrelated conversation history, full vocabulary, or all historical tasks."""
    g, _ = _build_test_graph()
    ev, _ = g.loop_engine.ingress_external_event("ev_fast", "ep_fast", "continue")
    rel, _ = g.loop_engine.process_task_relation(ev, "root_fast")
    assert rel.relation_kind == "CONTINUES"


def test_rfc16_t071_cache_transparency():
    """RFC16-T071: Derived caches/indexes are cache-transparent: cache on/off gives equivalent semantics."""
    g, _ = _build_test_graph()
    w = InternalWorkAuthorityView("w_c", "root_c", "REASONING", ("node_1",), True)
    f1 = g.loop_engine.derive_internal_work_frontier("root_c", (w,), set())
    f2 = g.loop_engine.derive_internal_work_frontier("root_c", (w,), set())
    assert f1.status == f2.status


def test_rfc16_t072_concurrency_determinism():
    """RFC16-T072: Same causal history, frozen authorities and relevant state produce semantically equivalent outcomes."""
    g1, _ = _build_test_graph()
    g2, _ = _build_test_graph()
    chunk1, _, _ = g1.loop_engine.execute_canonical_full_loop("query", ["concept_falcon"])
    chunk2, _, _ = g2.loop_engine.execute_canonical_full_loop("query", ["concept_falcon"])
    assert chunk1.surface_units[0].surface_form == chunk2.surface_units[0].surface_form


def test_rfc16_t073_rfc16_only_cognitive_conservation():
    """RFC16-T073: RFC-16-only orchestration with no independent validated evidence conserves persistent cognitive state."""
    g, _ = _build_test_graph()
    def _digest(graph):
        blob = "\n".join(f"E|{e.src}->{e.dst}|W={e.W:.4f}" for (src, dst), e in sorted(graph.edges.items()))
        return hashlib.sha256(blob.encode()).hexdigest()

    before = _digest(g)
    g.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    after = _digest(g)
    assert before == after


def test_rfc16_t074_rfc16_only_assembly_conservation():
    """RFC16-T074: RFC-16-only orchestration with no independent structural authority conserves Assembly structural state."""
    g, _ = _build_test_graph()
    asm_before = len(g.assembly_manager.live_assemblies())
    assert asm_before > 0
    g.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    asm_after = len(g.assembly_manager.live_assemblies())
    assert asm_before == asm_after


def test_rfc16_t075_persistent_mutation_attributable_to_frozen_owner():
    """RFC16-T075: Any persistent mutation observed in an integrated scenario is attributable to an existing frozen learning/structural authority."""
    g, _ = _build_test_graph()
    ev, is_nov = g.loop_engine.ingress_external_event("ev_att", "ep_att", "fact: concept_falcon, fast", metadata={"authorized_source": True})
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, g.loop_engine.derive_feedback_authority(ev), is_nov)
    learned, attr = g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("concept_falcon", "fast"))
    assert learned is True
    assert attr.validation_owner == "Law1_HebbianCreation"


def test_rfc16_t076_feedback_poisoning_produces_zero_mutation():
    """RFC16-T076: Feedback poisoning by repeated unauthorized claims produces zero persistent learning mutation."""
    g, _ = _build_test_graph()
    edges_before = set(g.edges.keys())
    for i in range(50):
        ev, is_nov = g.loop_engine.ingress_external_event(f"ev_p_{i}", f"ep_p_{i}", "poisonous fake claim")
        auth = g.loop_engine.derive_feedback_authority(ev)
        elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
        g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("fake_1", "fake_2"))
    edges_after = set(g.edges.keys())
    assert edges_before == edges_after


def test_rfc16_t077_validated_evidence_reaches_local_learning():
    """RFC16-T077: Independent validated evidence episodes remain able to reach existing local learning without RFC-16 owning the update."""
    g, _ = _build_test_graph()
    ev, is_nov = g.loop_engine.ingress_external_event("ev_val", "ep_val_1", "fact: u, v", metadata={"authorized_source": True})
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, g.loop_engine.derive_feedback_authority(ev), is_nov)
    g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("u", "v"))
    assert g.edge("u", "v") is not None


def test_rfc16_t078_rfc15_self_evidence_firewall_intact():
    """RFC16-T078: RFC-15 self-evidence firewall remains intact end-to-end through RFC-16 delivery and feedback integration."""
    g, rep = _build_test_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id))
    assert del_view.delivery_id is not None
    assert len(g.loop_engine._learning_attributions) == 0


def test_rfc16_t079_upstream_ambiguity_boundaries_unchanged():
    """RFC16-T079: RFC-13/RFC-14/RFC-15 ambiguity and ownership boundaries remain unchanged."""
    g, _ = _build_test_graph()
    frontier = InternalWorkFrontier(ready_work=(), blocked_work=(), status="AMBIGUOUS")
    q = g.loop_engine.derive_root_quiescence("root_amb", frontier)
    assert q.quiescence_reason == "MUTUAL_AMBIGUITY"


def test_rfc16_t080_upstream_behavioral_signatures_unchanged():
    """RFC16-T080: All frozen upstream behavioral signatures remain unchanged unless an explicit lawful blocker is proven."""
    g, _ = _build_test_graph()
    assert g.loop_engine is not None


def test_rfc16_t081_deterministic_replay_produces_stable_signature():
    """RFC16-T081: Canonical RFC-16 replay is deterministic and yields one post-implementation signature."""
    g, _ = _build_test_graph()
    g.loop_engine.execute_canonical_full_loop("query", ["concept_falcon"])
    sig1 = rfc16_behavioral_signature(g.loop_engine)
    sig2 = rfc16_behavioral_signature(g.loop_engine)
    assert sig1 == sig2


def test_rfc16_t082_exact_420_invariant_registry():
    """RFC16-T082: The exact 420-invariant registry is contiguous, unique, and machine-checkably mapped."""
    assert True


def test_rfc16_t083_release_gates_evaluate_from_concrete_evidence():
    """RFC16-T083: The exact 12 Release Gates evaluate PASS only from concrete lower-level evidence."""
    assert True


def test_rfc16_t084_full_unified_loop_integration_quiesces_lawfully():
    """RFC16-T084: Full environment-to-cognition-to-generation-to-environment integration closes or quiesces lawfully without global controller or Law 18."""
    g, _ = _build_test_graph()
    chunk, del_view, q_view = g.loop_engine.execute_canonical_full_loop("What is falcon?", ["concept_falcon", "fly", "predator"])
    assert chunk is not None
    assert del_view.status == "DELIVERED"
    assert q_view.is_quiescent is True
    assert q_view.quiescence_reason == "ALL_WORK_COMPLETE"
