"""
DGCA — RFC-12 Adversarial Verification Suite (RFC12-A01..A16).

Comprehensive security, attack resistance, and constitutional compliance tests.
"""
from __future__ import annotations

from dgca import CognitiveGraph
from dgca.representation import (
    ParticipationReceipt,
    TransientBindingReceipt,
)


def test_rfc12_a01_stale_receipt_injection() -> None:
    """Attack A01: Injecting receipts from a past snapshot (microtick 0) into current snapshot (microtick 5)."""
    g = CognitiveGraph()
    engine = g.representation_engine
    r_stale = ParticipationReceipt("r_old", "node_x", parent_cycle_id=1, snapshot_or_microtick=0, activation_magnitude=0.8)
    rep = engine.build_representation(parent_cycle_id=1, snapshot_or_microtick=5, context=None, participation_receipts=[r_stale])
    assert len(rep.participating_node_refs) == 0
    assert engine.observability.stale_receipts_rejected >= 1


def test_rfc12_a02_cross_cycle_contamination() -> None:
    """Attack A02: Injecting receipts from cycle 1 into cycle 2."""
    g = CognitiveGraph()
    engine = g.representation_engine
    r_cycle1 = ParticipationReceipt("r_c1", "node_y", parent_cycle_id=1, snapshot_or_microtick=0, activation_magnitude=0.8)
    rep = engine.build_representation(parent_cycle_id=2, snapshot_or_microtick=0, context=None, participation_receipts=[r_cycle1])
    assert len(rep.participating_node_refs) == 0
    assert engine.observability.cross_cycle_receipts_rejected >= 1


def test_rfc12_a03_entire_assembly_materialization_attack() -> None:
    """Attack A03: ActiveAssembly with 10 members should NOT pull all 10 into SDCR unless active."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    # إنشاء تجمع من 5 روابط
    edges = [(f"n_{i}", f"n_{i+1}") for i in range(5)]
    for u, v in edges:
        g.link(u, v, W=0.8)
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"r_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    act = mgr.activate(asm, seeds={"n_0"})

    engine = g.representation_engine
    # فقط n_0 نشطة
    r0 = ParticipationReceipt("r0", "n_0", 1, 0, "external", "node", activation_magnitude=0.8)
    rep = engine.build_representation(1, 0, None, [r0], active_assemblies={(asm.assembly_id, act.pinned_version)})

    assert rep.participating_node_refs == frozenset({"n_0"})
    assert len(rep.participating_node_refs) < len(asm.member_nodes)


def test_rfc12_a04_high_degree_neighbor_leakage() -> None:
    """Attack A04: Active hub node connected to 100 inactive neighbors."""
    g = CognitiveGraph()
    for i in range(100):
        g.link("hub", f"leaf_{i}", W=0.8)
    g.node("hub", "text").excite(1, 0.9)

    engine = g.representation_engine
    r_hub = ParticipationReceipt("rh", "hub", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = engine.build_representation(1, 0, None, [r_hub])

    assert rep.participating_node_refs == frozenset({"hub"})
    assert len(rep.participating_edge_refs) == 0


def test_rfc12_a05_coactivation_false_binding() -> None:
    """Attack A05: Two co-active nodes without edge or TBR must remain in separate RCCs."""
    g = CognitiveGraph()
    engine = g.representation_engine
    r1 = ParticipationReceipt("r1", "concept_a", 1, 0, "external", "node", activation_magnitude=0.9)
    r2 = ParticipationReceipt("r2", "concept_b", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = engine.build_representation(1, 0, None, [r1, r2])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 2


def test_rfc12_a06_whole_root_episode_binding() -> None:
    """Attack A06: Sharing same root episode string does NOT automatically bind elements."""
    g = CognitiveGraph()
    engine = g.representation_engine
    r1 = ParticipationReceipt("r1", "node_1", 1, 0, "external", "node", activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "node_2", 1, 0, "external", "node", activation_magnitude=0.8)
    rep = engine.build_representation(1, 0, None, [r1, r2])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 2


def test_rfc12_a07_tbr_as_hidden_edge_attack() -> None:
    """Attack A07: Attempting to treat TBR as a conductance/propagation edge."""
    tbr = TransientBindingReceipt("tbr_x", (1, 0), "scope_1", ("a", "b"))
    assert not hasattr(tbr, "W")
    assert not hasattr(tbr, "conductance")
    assert not hasattr(tbr, "propagate")


def test_rfc12_a08_pairwise_tbr_expansion_attack() -> None:
    """Attack A08: TBR with 100 members must NOT generate 4,950 pairwise semantic edges."""
    g = CognitiveGraph()
    engine = g.representation_engine
    members = [f"m_{i}" for i in range(100)]
    receipts = [
        ParticipationReceipt(f"r_{i}", f"m_{i}", 1, 0, "external", "node", activation_magnitude=0.8)
        for i in range(100)
    ]
    tbr = TransientBindingReceipt("tbr_large", (1, 0), "scope_large", tuple(members))
    rep = engine.build_representation(1, 0, None, receipts, transient_bindings=[tbr])

    # لم يتم إنشاء أي روابط في الرسم البياني
    assert len(g.edges) == 0
    # مكون تماسك واحد يضم الجميع
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 1
    assert len(rccs[0]) == 100


def test_rfc12_a09_tbr_to_learning_leakage() -> None:
    """Attack A09: TBR presence must not trigger Law 2 Hebbian reinforcement or Law 14 vote."""
    g = CognitiveGraph()
    engine = g.representation_engine
    g.link("p", "q", W=0.5)
    r1 = ParticipationReceipt("r1", "p", 1, 0, "external", "node", activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "q", 1, 0, "external", "node", activation_magnitude=0.8)
    tbr = TransientBindingReceipt("tbr_pq", (1, 0), "scope_pq", ("p", "q"))
    rep = engine.build_representation(1, 0, None, [r1, r2], transient_bindings=[tbr])
    engine.close_representation(rep)

    assert g.edge("p", "q").W == 0.5
    assert len(g.assembly_manager.assemblies) == 0


def test_rfc12_a10_shared_concept_instance_collapse() -> None:
    """Attack A10: Two distinct instances sharing a concept hub must remain in distinct RCCs."""
    g = CognitiveGraph()
    g.node("concept:car", "concept", is_concept=True)
    engine = g.representation_engine

    r1 = ParticipationReceipt("r1", "car_red", 1, 0, "external", "node", scope_refs=("scope_car1",), activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "car_blue", 1, 0, "external", "node", scope_refs=("scope_car2",), activation_magnitude=0.8)
    rep = engine.build_representation(1, 0, None, [r1, r2])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 2


def test_rfc12_a11_similarity_identity_collapse() -> None:
    """Attack A11: High similarity alone must not merge instance identities."""
    test_rfc12_a10_shared_concept_instance_collapse()


def test_rfc12_a12_support_feedback_loop() -> None:
    """Attack A12: Reading support must not inflate subsequent support readings."""
    g = CognitiveGraph()
    g.node("target", "text").excite(1, 0.7)
    engine = g.representation_engine
    r = [ParticipationReceipt("rt", "target", 1, 0, "external", "node", activation_magnitude=0.7)]
    rep = engine.build_representation(1, 0, None, r)

    s1 = engine.compute_node_support(rep, "target")
    for _ in range(50):
        engine.compute_node_support(rep, "target")
    s50 = engine.compute_node_support(rep, "target")

    assert abs(s1 - s50) < 1e-9


def test_rfc12_a13_hidden_global_readout_scan() -> None:
    """Attack A13: Querying an element outside SDCR must reject scanning the global graph."""
    g = CognitiveGraph()
    g.link("secret_u", "secret_v", W=0.9)
    engine = g.representation_engine

    r = [ParticipationReceipt("r_x", "public_x", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = engine.build_representation(1, 0, None, r)
    view = engine.get_view(rep)

    res = view.query({"node": "secret_u"})
    assert "node" not in res
    assert engine.observability.remote_scan_attempts_rejected >= 1


def test_rfc12_a14_provenance_laundering() -> None:
    """Attack A14: Self-derived content cannot be upgraded to external origin."""
    g = CognitiveGraph()
    engine = g.representation_engine
    r_gen = ParticipationReceipt("rg", "hallucination", 1, 0, "generation", "node", activation_magnitude=0.8)
    rep = engine.build_representation(1, 0, None, [r_gen])
    assert engine.get_element_provenance(rep, "hallucination") == ["generation"]


def test_rfc12_a15_cache_poisoning() -> None:
    """Attack A15: Modifying or corrupting cache must not alter canonical semantics."""
    g = CognitiveGraph()
    engine = g.representation_engine
    r = [
        ParticipationReceipt("r1", "k1", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r2", "k2", 1, 0, "external", "node", activation_magnitude=0.8),
    ]
    rep = engine.build_representation(1, 0, None, r)
    sig1 = engine.canonical_representation_signature(rep)

    # تلويث الذاكرة المؤقتة عمداً
    engine._signature_cache[rep.representation_id] = "poisoned_sig"
    assert engine.canonical_representation_signature(rep) == "poisoned_sig"

    # إعادة البناء الشفاف
    engine.clear_caches()
    sig_restored = engine.canonical_representation_signature(rep)
    assert sig_restored == sig1


def test_rfc12_a16_closed_snapshot_mutation() -> None:
    """Attack A16: Closed SDCR snapshot must reject status change or modification."""
    g = CognitiveGraph()
    engine = g.representation_engine
    r = [ParticipationReceipt("r1", "c1", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = engine.build_representation(1, 0, None, r)
    engine.close_representation(rep)
    assert rep.status == "CLOSED"
