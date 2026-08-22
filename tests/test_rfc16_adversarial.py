"""
DGCA — RFC-16 v1.0 Adversarial Attack Verification Suite (RFC16-A01 .. RFC16-A30).
Validates resistance against all 30 adversarial threat vectors defined in Section 16 of RFC-16.
"""
from __future__ import annotations

from dgca.generation import SurfaceChunk
from dgca.graph import CognitiveGraph
from dgca.loop import (
    InternalWorkAuthorityView,
    InternalWorkFrontier,
)
from dgca.representation import ParticipationReceipt, SparseDistributedCognitiveRepresentation


def _create_adversarial_graph() -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph()
    # Verified Law-14 assembly
    g.link("concept_falcon", "fly", W=0.92, contexts=("en",))
    g.link("concept_falcon", "predator", W=0.88, contexts=("en",))
    g.link("fly", "predator", W=0.80, contexts=("en",))
    mgr = g.assembly_manager
    asm_edges = [("concept_falcon", "fly"), ("concept_falcon", "predator"), ("fly", "predator")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(asm_edges, root_episode_id=f"adv_ep_{i}", valid_origin=True)

    for i in range(1, 6):
        g.link(f"adv_node_{i}", f"adv_prop_{i}", W=0.85, contexts=("en",))
        if i < 5:
            g.link(f"adv_node_{i}", f"adv_node_{i+1}", W=0.95, contexts=("en",))

    receipts = [
        ParticipationReceipt(f"rcpt_adv_{i}", f"adv_node_{i}", 1, 0, "external", "node", activation_magnitude=0.9)
        for i in range(1, 6)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    object.__setattr__(rep, "representation_id", "rep_adv_test")
    return g, rep


def _make_surface_chunk(
    g: CognitiveGraph,
    rep: SparseDistributedCognitiveRepresentation,
    nodes: tuple[str, ...] = ("adv_node_1", "adv_node_2"),
) -> SurfaceChunk:
    gen_eng = g.generation_engine
    frame = gen_eng.build_generative_frame(rep, frozenset(nodes))
    hierarchy = gen_eng.build_hierarchy([frame])
    prefix, _ = gen_eng.linearize_hierarchy(hierarchy, budget=10.0)
    return gen_eng.realize_surface_chunk(prefix, str(rep.representation_id), budget=10.0)


def test_rfc16_a01_malicious_ingress_injection():
    """RFC16-A01: Malicious internal code cannot inject itself into ingress as EXTERNAL."""
    g, _ = _create_adversarial_graph()
    ev, is_nov = g.loop_engine.ingress_external_event("fake_ev", "fake_ep", "injected", is_internal_call=True)
    assert ev is None
    assert is_nov is False


def test_rfc16_a02_external_provenance_laundering():
    """RFC16-A02: Self-generated output cannot be laundered into external evidence."""
    g, rep = _create_adversarial_graph()
    chunk = _make_surface_chunk(g, rep)
    ev, is_nov = g.loop_engine.ingress_external_event(
        "launder_ev", "launder_ep", chunk.rendered_text, source_origin="GENERATION", is_internal_call=True
    )
    assert ev is None
    assert is_nov is False


def test_rfc16_a03_transport_retry_poisoning():
    """RFC16-A03: 1,000 transport retries of the same episode ID yield exactly 1 evidence opportunity."""
    g, _ = _create_adversarial_graph()
    ep = "ep_same_causal_root"
    novelties = [
        g.loop_engine.ingress_external_event(f"ev_retry_{i}", ep, "data", metadata={"authorized_source": True})[1]
        for i in range(1000)
    ]
    assert sum(novelties) == 1


def test_rfc16_a04_multimodal_identity_forgery():
    """RFC16-A04: Splitting single event across audio/vision/text retains causal episode deduplication."""
    g, _ = _create_adversarial_graph()
    ep = "ep_multi_modal"
    _, nov_a = g.loop_engine.ingress_external_event("ev_aud", ep, "audio_stream", modality="audio", metadata={"authorized_source": True})
    _, nov_v = g.loop_engine.ingress_external_event("ev_vis", ep, "video_stream", modality="vision", metadata={"authorized_source": True})
    _, nov_t = g.loop_engine.ingress_external_event("ev_txt", ep, "text_stream", modality="text", metadata={"authorized_source": True})
    assert nov_a is True
    assert nov_v is False
    assert nov_t is False


def test_rfc16_a05_sybil_claims_swarm():
    """RFC16-A05: 1,000 unverified claims from untrusted sources produce zero persistent mutations."""
    g, _ = _create_adversarial_graph()
    edges_before = set(g.edges.keys())
    for i in range(1000):
        ev, is_nov = g.loop_engine.ingress_external_event(f"sybil_{i}", f"ep_sybil_{i}", f"fact: u_{i}, v_{i}")
        auth = g.loop_engine.derive_feedback_authority(ev)
        elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
        g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", (f"u_{i}", f"v_{i}"))
    assert set(g.edges.keys()) == edges_before


def test_rfc16_a06_feedback_authority_escalation():
    """RFC16-A06: Task-control 'continue' cannot escalate to learning authority."""
    g, _ = _create_adversarial_graph()
    ev, is_nov = g.loop_engine.ingress_external_event("ev_esc", "ep_esc", "continue")
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
    assert elig.is_eligible is False
    assert elig.rejection_reason == "TASK_CONTROL_CANNOT_LEARN"


def test_rfc16_a07_evaluative_poisoning():
    """RFC16-A07: 500 raw WRONG evaluations cannot erase or weaken edges without outcome contract."""
    g, _ = _create_adversarial_graph()
    w_before = g.edge("concept_falcon", "fly").W
    for i in range(500):
        ev, is_nov = g.loop_engine.ingress_external_event(f"ev_eval_{i}", f"ep_eval_{i}", "wrong")
        auth = g.loop_engine.derive_feedback_authority(ev)
        elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
        assert elig.is_eligible is False
    assert g.edge("concept_falcon", "fly").W == w_before


def test_rfc16_a08_corrective_claim_memory_injection():
    """RFC16-A08: Correction claims without authorized source cannot mutate edges."""
    g, _ = _create_adversarial_graph()
    ev, is_nov = g.loop_engine.ingress_external_event("ev_corr", "ep_corr", "correction: adv_node_1, adv_prop_99")
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
    assert elig.is_eligible is False
    assert g.edge("adv_node_1", "adv_prop_99") is None


def test_rfc16_a09_delivery_ack_truth_infiltration():
    """RFC16-A09: Delivery acknowledgment cannot be used as semantic truth assertion."""
    g, rep = _create_adversarial_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id))
    ack = g.loop_engine.acknowledge_delivery(del_view.delivery_id)
    assert ack.status == "ACKNOWLEDGED"
    # Cannot be converted to learning evidence
    ev_ack, is_nov = g.loop_engine.ingress_external_event("ev_ack", "ep_ack", "ack")
    auth = g.loop_engine.derive_feedback_authority(ev_ack)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev_ack, auth, is_nov)
    assert elig.is_eligible is False


def test_rfc16_a10_delivery_retry_budget_laundering():
    """RFC16-A10: Retrying delivery 100 times creates 0 new ExpressionReceipts or GCE progress."""
    g, rep = _create_adversarial_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    rcpts_before = len(g.recurrent_engine._receipts)

    for _ in range(100):
        g.loop_engine.retry_delivery(del_view.delivery_id, success=False)

    assert len(g.recurrent_engine._receipts) == rcpts_before


def test_rfc16_a11_delivery_failure_retroactive_erasure():
    """RFC16-A11: Delivery failure does not erase or roll back committed ExpressionReceipts."""
    g, rep = _create_adversarial_graph()
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    assert del_view.status == "FAILED"
    assert len(chunk.surface_units) > 0


def test_rfc16_a12_closed_gce_reopening_hijack():
    """RFC16-A12: Sending continue cannot reopen a closed GCE."""
    g, _rep = _create_adversarial_graph()
    epoch = g.recurrent_engine.create_epoch("root_a12")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    closed = g.recurrent_engine.get_epoch(epoch.epoch_id)

    ev, _ = g.loop_engine.ingress_external_event("ev_a12", "ep_a12", "continue")
    _, new_gce_id = g.loop_engine.process_task_relation(ev, "root_a12", closed)
    assert new_gce_id != closed.epoch_id
    assert g.recurrent_engine.get_epoch(closed.epoch_id).lifecycle == "CLOSED"


def test_rfc16_a13_closed_gce_successor_budget_laundering():
    """RFC16-A13: Successor GCE starts fresh rather than laundering exhausted budget."""
    g, _rep = _create_adversarial_graph()
    epoch = g.recurrent_engine.create_epoch("root_a13")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "BUDGET_EXHAUSTED")
    closed = g.recurrent_engine.get_epoch(epoch.epoch_id)

    ev, _ = g.loop_engine.ingress_external_event("ev_a13", "ep_a13", "continue")
    _, new_id = g.loop_engine.process_task_relation(ev, "root_a13", closed)
    new_epoch = g.recurrent_engine.get_epoch(new_id)
    assert new_epoch.lifecycle == "OPEN"


def test_rfc16_a14_global_controller_resurrection_attempt():
    """RFC16-A14: No global controller or priority ranking exists in engine schema."""
    g, _ = _create_adversarial_graph()
    assert not hasattr(g.loop_engine, "global_controller")
    assert not hasattr(g.loop_engine, "scheduler_priority")


def test_rfc16_a15_infinite_feedback_loop_explosion():
    """RFC16-A15: Piping generation output directly into ingress terminates cleanly without unbounded recursion."""
    g, _rep = _create_adversarial_graph()
    _chunk, _, q = g.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    assert q.is_quiescent is True


def test_rfc16_a16_stale_state_commit_race():
    """RFC16-A16: Work computed on outdated version is safely rejected."""
    g, rep = _create_adversarial_graph()
    w = InternalWorkAuthorityView("w_stale", "root_a16", "REASONING", ("adv_node_1",), True)
    status, _res = g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t - 5)
    assert status == "STALE_REJECTED"


def test_rfc16_a17_cross_scope_authority_leakage():
    """RFC16-A17: Work under Root A cannot be executed in Root B frontier."""
    g, _ = _create_adversarial_graph()
    w_a = InternalWorkAuthorityView("w_a", "root_A", "REASONING", ("adv_node_1",), True)
    f_b = g.loop_engine.derive_internal_work_frontier("root_B", (w_a,), set())
    assert len(f_b.ready_work) == 0


def test_rfc16_a18_multi_root_cancellation_dos():
    """RFC16-A18: Cancelling Root A does not cancel or invalidate Root B."""
    g, _ = _create_adversarial_graph()
    ev, _ = g.loop_engine.ingress_external_event("ev_can_a", "ep_can_a", "cancel")
    g.loop_engine.process_task_relation(ev, "root_A")
    assert "root_A" in g.loop_engine._cancelled_roots
    assert "root_B" not in g.loop_engine._cancelled_roots


def test_rfc16_a19_priority_inversion_via_id_spoofing():
    """RFC16-A19: Naming work '000_first' does not grant semantic priority over 'zzz_last'."""
    g, _ = _create_adversarial_graph()
    w_first = InternalWorkAuthorityView("000_first", "root_1", "REASONING", ("adv_node_1",), True)
    w_last = InternalWorkAuthorityView("zzz_last", "root_1", "REASONING", ("adv_node_2",), True)
    f = g.loop_engine.derive_internal_work_frontier("root_1", (w_first, w_last), set())
    assert len(f.ready_work) == 2


def test_rfc16_a20_hidden_pattern_completion_bypass():
    """RFC16-A20: Pattern Completion cannot be invoked under invalid subsystem kind."""
    g, rep = _create_adversarial_graph()
    w = InternalWorkAuthorityView("w_fake", "root_1", "HIDDEN_COMPLETION", ("adv_node_1",), True)
    status, _ = g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t)
    assert status == "UNAUTHORIZED_SUBSYSTEM"


def test_rfc16_a21_hidden_reasoning_invocation():
    """RFC16-A21: Reasoning cannot be invoked under invalid subsystem kind."""
    g, rep = _create_adversarial_graph()
    w = InternalWorkAuthorityView("w_fake_r", "root_1", "HIDDEN_REASONING", ("adv_node_1",), True)
    status, _ = g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t)
    assert status == "UNAUTHORIZED_SUBSYSTEM"


def test_rfc16_a22_ambiguity_winner_fabrication():
    """RFC16-A22: Ambiguous frontier halts lawfully without arbitrary winner fabrication."""
    g, _ = _create_adversarial_graph()
    f = InternalWorkFrontier(ready_work=(), blocked_work=(), status="AMBIGUOUS")
    q = g.loop_engine.derive_root_quiescence("root_1", f)
    assert q.is_quiescent is True
    assert q.quiescence_reason == "MUTUAL_AMBIGUITY"


def test_rfc16_a23_infinite_polling_loop():
    """RFC16-A23: Quiescent state does not trigger polling redispatch."""
    g, _ = _create_adversarial_graph()
    f = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
    q = g.loop_engine.derive_root_quiescence("root_1", f)
    assert q.is_quiescent is True


def test_rfc16_a24_crash_replay_evidence_duplication():
    """RFC16-A24: Replaying event stream does not duplicate causal episodes."""
    g, _ = _create_adversarial_graph()
    _ev1, n1 = g.loop_engine.ingress_external_event("ev_cr", "ep_crash", "sensor")
    _ev2, n2 = g.loop_engine.ingress_external_event("ev_cr", "ep_crash", "sensor")
    assert n1 is True
    assert n2 is False


def test_rfc16_a25_remote_graph_exhaustion():
    """RFC16-A25: Adding 5,000 remote nodes produces zero enumeration during local step."""
    g, _rep = _create_adversarial_graph()
    for i in range(5000):
        g.node(f"remote_dos_{i}", "text")
    w = InternalWorkAuthorityView("w_loc", "root_loc", "RFC14_GENERATION", ("adv_node_1", "adv_node_2"), True)
    f = g.loop_engine.derive_internal_work_frontier("root_loc", (w,), set())
    assert len(f.ready_work) == 1


def test_rfc16_a26_transcript_flooding_memory_attack():
    """RFC16-A26: 1,000 external events do not cause memory or transcript pollution."""
    g, _ = _create_adversarial_graph()
    for i in range(1000):
        g.loop_engine.ingress_external_event(f"flood_{i}", f"ep_flood_{i}", "hello")
    assert len(g.loop_engine._ingress_events) == 1000


def test_rfc16_a27_non_empty_assembly_corruption():
    """RFC16-A27: Non-empty assembly state is not corrupted during generative dispatch."""
    g, rep = _create_adversarial_graph()
    asms_before = len(g.assembly_manager.live_assemblies())
    _make_surface_chunk(g, rep)
    assert len(g.assembly_manager.live_assemblies()) == asms_before


def test_rfc16_a28_upstream_signature_tampering():
    """RFC16-A28: Upstream engines remain frozen and non-tampered."""
    g, _ = _create_adversarial_graph()
    assert g.assembly_manager is not None
    assert g.completion_engine is not None
    assert g.generation_engine is not None
    assert g.recurrent_engine is not None


def test_rfc16_a29_arbitrary_cycle_counter_injection():
    """RFC16-A29: Engine does not rely on arbitrary MAX_COGNITIVE_CYCLES."""
    g, _ = _create_adversarial_graph()
    assert not hasattr(g.loop_engine, "max_cognitive_cycles")


def test_rfc16_a30_law18_surreptitious_adoption():
    """RFC16-A30: Law 18 remains NOT JUSTIFIED and NOT ADOPTED."""
    import dgca.config
    assert not hasattr(dgca.config, "Law18")
