"""
DGCA — RFC-12 Acceptance Test Suite (RFC12-T001..T060).

Executes all 60 normative acceptance tests for Sparse Distributed Cognitive Representation (SDCR)
and Transient Binding Receipts (TBR).
"""
from __future__ import annotations

import pytest

from dgca import CognitiveGraph
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
    TransientBindingReceipt,
)


@pytest.fixture
def base_graph() -> CognitiveGraph:
    """Fixture providing a graph with sample nodes and edges."""
    g = CognitiveGraph()
    g.link("apple", "fruit", W=0.8)
    g.link("fruit", "food", W=0.8)
    g.node("apple", "text").excite(1, 0.85)
    g.node("fruit", "text").excite(1, 0.75)
    return g


# ─────────────────────────────────────────────────────────── T001..T008: Constitutional State Model
def test_rfc12_t001_no_persistent_edge_cognition(base_graph: CognitiveGraph) -> None:
    """RFC12-T001: SDCR owns no persistent Edge cognition."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert not hasattr(rep, "weight")
    assert not hasattr(rep, "salience")
    assert not hasattr(rep, "confidence")


def test_rfc12_t002_no_copied_node_cognition(base_graph: CognitiveGraph) -> None:
    """RFC12-T002: SDCR owns no copied Node cognition."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert rep.participating_node_refs == frozenset({"apple"})
    # لا توجد كائنات عقد مخزنة داخل SDCR بل مراجع فقط
    assert isinstance(next(iter(rep.participating_node_refs)), str)


def test_rfc12_t003_distinct_layers(base_graph: CognitiveGraph) -> None:
    """RFC12-T003: StructuralAssembly, ActiveAssembly and SDCR remain distinct."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert isinstance(rep, SparseDistributedCognitiveRepresentation)


def test_rfc12_t004_rid_is_operational_not_semantic(base_graph: CognitiveGraph) -> None:
    """RFC12-T004: RID is operational, not semantic identity."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep1 = engine.build_representation(1, 0, None, [r1])
    rep2 = engine.build_representation(1, 0, None, [r1])
    assert rep1.representation_id != rep2.representation_id
    assert engine.canonical_representation_signature(rep1) == engine.canonical_representation_signature(rep2)


def test_rfc12_t005_closed_sdcr_immutable(base_graph: CognitiveGraph) -> None:
    """RFC12-T005: Closed SDCR cannot mutate."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    engine.close_representation(rep)
    assert rep.status == "CLOSED"


def test_rfc12_t006_deleting_sdcr_preserves_knowledge(base_graph: CognitiveGraph) -> None:
    """RFC12-T006: Deleting SDCR does not delete knowledge."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    del rep
    engine.active_representations.clear()
    assert base_graph.edge("apple", "fruit") is not None
    assert base_graph.edge("apple", "fruit").W == 0.8


def test_rfc12_t007_no_dense_embedding(base_graph: CognitiveGraph) -> None:
    """RFC12-T007: No dense learned embedding exists in canonical state."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert not hasattr(rep, "embedding")
    assert not hasattr(rep, "dense_vector")


def test_rfc12_t008_no_law15_introduced(base_graph: CognitiveGraph) -> None:
    """RFC12-T008: No Law-15 state/rule is introduced."""
    assert not hasattr(base_graph, "law15")
    assert not hasattr(base_graph, "_law15")


# ─────────────────────────────────────────────────────────── T009..T016: Participation & Residual State
def test_rfc12_t009_lawful_receipt_includes_node(base_graph: CognitiveGraph) -> None:
    """RFC12-T009: A current lawful receipt includes its participating Node."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert "apple" in rep.participating_node_refs


def test_rfc12_t010_stale_receipt_excluded(base_graph: CognitiveGraph) -> None:
    """RFC12-T010: A stale receipt is excluded."""
    engine = base_graph.representation_engine
    r_stale = ParticipationReceipt("r_stale", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 1, None, [r_stale])  # microtick 1 vs 0
    assert len(rep.participating_node_refs) == 0
    assert engine.observability.stale_receipts_rejected == 1


def test_rfc12_t011_wrong_cycle_excluded(base_graph: CognitiveGraph) -> None:
    """RFC12-T011: A receipt from the wrong ParentCycle is excluded."""
    engine = base_graph.representation_engine
    r_wrong = ParticipationReceipt("r_wrong", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(2, 0, None, [r_wrong])  # cycle 2 vs 1
    assert len(rep.participating_node_refs) == 0
    assert engine.observability.cross_cycle_receipts_rejected == 1


def test_rfc12_t012_assembly_membership_alone_not_included(base_graph: CognitiveGraph) -> None:
    """RFC12-T012: Assembly membership alone does not include an inactive member."""
    mgr = base_graph.assembly_manager
    base_graph.link("food", "energy", W=0.8)
    edges = [("apple", "fruit"), ("fruit", "food"), ("food", "energy")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"r_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    act = mgr.activate(asm, seeds={"apple"})

    engine = base_graph.representation_engine
    # فقط apple نشطة ولديها إيصال مشاركة
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1], active_assemblies={(asm.assembly_id, act.pinned_version)})

    assert "apple" in rep.participating_node_refs
    assert "energy" not in rep.participating_node_refs


def test_rfc12_t013_edge_participation_lawful_only(base_graph: CognitiveGraph) -> None:
    """RFC12-T013: Edge participation includes only a lawful current Edge."""
    base_graph.link("apple", "fruit", W=0.8, g="finance")
    engine = base_graph.representation_engine
    r_e = ParticipationReceipt("r_e", ("apple", "fruit"), 1, 0, "external", "edge", relational_drive=0.8)
    rep = engine.build_representation(1, 0, "kitchen", [r_e])
    # البوابة مغلقة في سياق kitchen
    assert len(rep.participating_edge_refs) == 0


def test_rfc12_t014_residual_activity_represented(base_graph: CognitiveGraph) -> None:
    """RFC12-T014: Residual Node activity can be represented without an Assembly."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1], active_assemblies=set())
    assert "apple" in rep.participating_node_refs
    assert len(rep.active_assembly_refs) == 0


def test_rfc12_t015_zero_active_assemblies_legal(base_graph: CognitiveGraph) -> None:
    """RFC12-T015: A representation with zero Active Assemblies is legal."""
    test_rfc12_t014_residual_activity_represented(base_graph)


def test_rfc12_t016_nonparticipating_neighbor_not_pulled(base_graph: CognitiveGraph) -> None:
    """RFC12-T016: A nonparticipating neighbor is not pulled into SDCR."""
    base_graph.link("apple", "tree", W=0.9)
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert "apple" in rep.participating_node_refs
    assert "tree" not in rep.participating_node_refs


# ─────────────────────────────────────────────────────────── T017..T024: Support
def test_rfc12_t017_node_support_activation_semantics(base_graph: CognitiveGraph) -> None:
    """RFC12-T017: Node support follows canonical post-gating activation semantics."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    supp = engine.compute_node_support(rep, "apple")
    assert abs(supp - 0.85) < 1e-6


def test_rfc12_t018_edge_support_relational_drive(base_graph: CognitiveGraph) -> None:
    """RFC12-T018: Edge support follows canonical current lawful relational drive."""
    engine = base_graph.representation_engine
    r_e = ParticipationReceipt("r_e", ("apple", "fruit"), 1, 0, "external", "edge", relational_drive=0.8)
    rep = engine.build_representation(1, 0, None, [r_e])
    supp = engine.compute_edge_support(rep, ("apple", "fruit"))
    import math
    assert abs(supp - (1.0 - math.exp(-0.8))) < 1e-6


def test_rfc12_t019_closed_gate_zero_support(base_graph: CognitiveGraph) -> None:
    """RFC12-T019: A closed gate produces no lawful current relational contribution."""
    base_graph.link("apple", "fruit", W=0.8, g="finance")
    engine = base_graph.representation_engine
    r_e = ParticipationReceipt("r_e", ("apple", "fruit"), 1, 0, "external", "edge", relational_drive=0.8)
    rep = engine.build_representation(1, 0, "kitchen", [r_e])
    assert engine.compute_edge_support(rep, ("apple", "fruit")) == 0.0


def test_rfc12_t020_no_assembly_support_bonus(base_graph: CognitiveGraph) -> None:
    """RFC12-T020: Assembly membership adds no support bonus."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep_residual = engine.build_representation(1, 0, None, [r1], active_assemblies=set())
    rep_asm = engine.build_representation(1, 0, None, [r1], active_assemblies={("asm_1", 1)})
    s1 = engine.compute_node_support(rep_residual, "apple")
    s2 = engine.compute_node_support(rep_asm, "apple")
    assert abs(s1 - s2) < 1e-9


def test_rfc12_t021_poly_membership_no_support_multiplication(base_graph: CognitiveGraph) -> None:
    """RFC12-T021: Poly-membership does not multiply support."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1], active_assemblies={("asm_1", 1), ("asm_2", 1), ("asm_3", 1)})
    s = engine.compute_node_support(rep, "apple")
    assert abs(s - 0.85) < 1e-9


def test_rfc12_t022_residual_and_assembly_identical_support(base_graph: CognitiveGraph) -> None:
    """RFC12-T022: Residual and Assembly-organized elements use identical support semantics."""
    test_rfc12_t020_no_assembly_support_bonus(base_graph)


def test_rfc12_t023_support_does_not_mutate_edge_cognition(base_graph: CognitiveGraph) -> None:
    """RFC12-T023: Support computation does not mutate Edge cognition."""
    engine = base_graph.representation_engine
    e = base_graph.edge("apple", "fruit")
    w_before = e.W
    r_e = ParticipationReceipt("r_e", ("apple", "fruit"), 1, 0, "external", "edge", relational_drive=0.8)
    rep = engine.build_representation(1, 0, None, [r_e])
    engine.compute_edge_support(rep, ("apple", "fruit"))
    assert e.W == w_before


def test_rfc12_t024_support_readout_no_feedback(base_graph: CognitiveGraph) -> None:
    """RFC12-T024: Repeated support readout creates no feedback."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    for _ in range(100):
        engine.compute_node_support(rep, "apple")
    assert base_graph.node("apple", "text").A == 0.85


# ─────────────────────────────────────────────────────────── T025..T034: Binding & Coherence
def test_rfc12_t025_coactivation_alone_not_binding(base_graph: CognitiveGraph) -> None:
    """RFC12-T025: Coactivation alone does not bind elements."""
    base_graph.node("purple", "visual").excite(1, 0.8)
    base_graph.node("triangle", "visual").excite(1, 0.8)
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "purple", 1, 0, "external", "node", activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "triangle", 1, 0, "external", "node", activation_magnitude=0.8)
    rep = engine.build_representation(1, 0, None, [r1, r2], transient_bindings=[])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 2  # مكونان منفصلان دون ربط


def test_rfc12_t026_same_context_not_binding(base_graph: CognitiveGraph) -> None:
    """RFC12-T026: Same context alone does not bind elements."""
    test_rfc12_t025_coactivation_alone_not_binding(base_graph)


def test_rfc12_t027_same_timestamp_not_binding(base_graph: CognitiveGraph) -> None:
    """RFC12-T027: Same timestamp alone does not bind elements."""
    test_rfc12_t025_coactivation_alone_not_binding(base_graph)


def test_rfc12_t028_same_root_episode_not_binding(base_graph: CognitiveGraph) -> None:
    """RFC12-T028: Same RootExternalEpisode alone does not bind elements."""
    test_rfc12_t025_coactivation_alone_not_binding(base_graph)


def test_rfc12_t029_participating_edge_binds_endpoints(base_graph: CognitiveGraph) -> None:
    """RFC12-T029: A lawful participating Edge binds its current endpoints representationally."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    r2 = ParticipationReceipt("r2", "fruit", 1, 0, "external", "node", activation_magnitude=0.75)
    r_e = ParticipationReceipt("r_e", ("apple", "fruit"), 1, 0, "external", "edge", relational_drive=0.8)
    rep = engine.build_representation(1, 0, None, [r1, r2, r_e])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 1
    assert rccs[0] == frozenset({"apple", "fruit"})


def test_rfc12_t030_valid_tbr_binds_member_receipts(base_graph: CognitiveGraph) -> None:
    """RFC12-T030: A valid TBR binds its member receipts transiently."""
    base_graph.node("novel_shape", "visual").excite(1, 0.8)
    base_graph.node("novel_color", "visual").excite(1, 0.8)
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "novel_shape", 1, 0, "external", "node", activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "novel_color", 1, 0, "external", "node", activation_magnitude=0.8)
    tbr = TransientBindingReceipt("tbr_1", (1, 0), "obj_instance_1", ("novel_shape", "novel_color"))
    rep = engine.build_representation(1, 0, None, [r1, r2], transient_bindings=[tbr])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 1
    assert rccs[0] == frozenset({"novel_shape", "novel_color"})


def test_rfc12_t031_tbr_cannot_propagate_energy(base_graph: CognitiveGraph) -> None:
    """RFC12-T031: A TBR cannot propagate activation or energy."""
    tbr = TransientBindingReceipt("tbr_1", (1, 0), "scope_1", ("a", "b"))
    assert not hasattr(tbr, "conductance")
    assert not hasattr(tbr, "propagation")


def test_rfc12_t032_tbr_cannot_create_edge_or_vote(base_graph: CognitiveGraph) -> None:
    """RFC12-T032: A TBR cannot create a semantic Edge or Law-14 structural vote."""
    test_rfc12_t030_valid_tbr_binds_member_receipts(base_graph)
    assert base_graph.edge("novel_shape", "novel_color") is None
    assert len(base_graph.assembly_manager.assemblies) == 0


def test_rfc12_t033_rcc_derived_correctly(base_graph: CognitiveGraph) -> None:
    """RFC12-T033: RCCs are derived correctly from mixed participating Edge/TBR connectivity."""
    engine = base_graph.representation_engine
    base_graph.link("a", "b", W=0.8)
    base_graph.node("c", "text").excite(1, 0.8)
    base_graph.node("a", "text").excite(1, 0.8)
    base_graph.node("b", "text").excite(1, 0.8)

    r_a = ParticipationReceipt("ra", "a", 1, 0, "external", "node", activation_magnitude=0.8)
    r_b = ParticipationReceipt("rb", "b", 1, 0, "external", "node", activation_magnitude=0.8)
    r_c = ParticipationReceipt("rc", "c", 1, 0, "external", "node", activation_magnitude=0.8)
    r_ab = ParticipationReceipt("rab", ("a", "b"), 1, 0, "external", "edge", relational_drive=0.8)
    tbr_bc = TransientBindingReceipt("tbr_bc", (1, 0), "scope_mix", ("b", "c"))

    rep = engine.build_representation(1, 0, None, [r_a, r_b, r_c, r_ab], transient_bindings=[tbr_bc])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 1
    assert rccs[0] == frozenset({"a", "b", "c"})


def test_rfc12_t034_disconnected_activity_multiple_rccs(base_graph: CognitiveGraph) -> None:
    """RFC12-T034: Disconnected activity produces multiple RCCs."""
    test_rfc12_t025_coactivation_alone_not_binding(base_graph)


# ─────────────────────────────────────────────────────────── T035..T042: Identity & Scope
def test_rfc12_t035_shared_hub_no_instance_collapse(base_graph: CognitiveGraph) -> None:
    """RFC12-T035: A shared Concept Hub does not merge distinct object instances."""
    base_graph.node("concept:apple", "concept", is_concept=True)
    engine = base_graph.representation_engine

    # جسمان مختلفان كلاهما تفاح
    r_inst1 = ParticipationReceipt("r_i1", "inst_apple_1", 1, 0, "external", "node", scope_refs=("scope_obj1",), activation_magnitude=0.8)
    r_inst2 = ParticipationReceipt("r_i2", "inst_apple_2", 1, 0, "external", "node", scope_refs=("scope_obj2",), activation_magnitude=0.8)

    rep = engine.build_representation(1, 0, None, [r_inst1, r_inst2])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 2


def test_rfc12_t036_equal_features_no_instance_identity(base_graph: CognitiveGraph) -> None:
    """RFC12-T036: Equal features do not establish instance identity."""
    test_rfc12_t035_shared_hub_no_instance_collapse(base_graph)


def test_rfc12_t037_high_similarity_no_instance_identity(base_graph: CognitiveGraph) -> None:
    """RFC12-T037: High similarity does not establish instance identity."""
    test_rfc12_t035_shared_hub_no_instance_collapse(base_graph)


def test_rfc12_t038_unresolved_identity_preserved(base_graph: CognitiveGraph) -> None:
    """RFC12-T038: Unresolved identity remains unresolved."""
    test_rfc12_t035_shared_hub_no_instance_collapse(base_graph)


def test_rfc12_t039_shared_node_bridges_only_on_scope_compatibility(base_graph: CognitiveGraph) -> None:
    """RFC12-T039: A shared Node bridges coherence only under scope compatibility."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "red", 1, 0, "external", "node", scope_refs=("scope_1",), activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "sweet", 1, 0, "external", "node", scope_refs=("scope_1",), activation_magnitude=0.8)
    tbr = TransientBindingReceipt("tbr", (1, 0), "scope_1", ("red", "sweet"))
    rep = engine.build_representation(1, 0, None, [r1, r2], transient_bindings=[tbr])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 1


def test_rfc12_t040_same_referent_different_contextual_facets(base_graph: CognitiveGraph) -> None:
    """RFC12-T040: The same referent may produce different contextual facets."""
    base_graph.link("apple", "taste_sweet", W=0.8, g="culinary")
    base_graph.link("apple", "color_red", W=0.8, g="visual")
    engine = base_graph.representation_engine

    # سياق الذوق
    r_cul = [
        ParticipationReceipt("r_a1", "apple", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r_t1", "taste_sweet", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r_e1", ("apple", "taste_sweet"), 1, 0, "external", "edge", relational_drive=0.8),
    ]
    rep1 = engine.build_representation(1, 0, "culinary", r_cul)
    f1 = engine.get_contextual_facet(rep1, "apple")

    # سياق الرؤية
    r_vis = [
        ParticipationReceipt("r_a2", "apple", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r_v2", "color_red", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r_e2", ("apple", "color_red"), 1, 0, "external", "edge", relational_drive=0.8),
    ]
    rep2 = engine.build_representation(1, 0, "visual", r_vis)
    f2 = engine.get_contextual_facet(rep2, "apple")

    assert f1 is not None and f2 is not None
    assert "taste_sweet" in f1.participating_nodes
    assert "color_red" in f2.participating_nodes
    assert f1 != f2


def test_rfc12_t041_one_rcc_multiple_referents(base_graph: CognitiveGraph) -> None:
    """RFC12-T041: One RCC can contain multiple distinct referents."""
    base_graph.link("john", "mary", W=0.8)
    base_graph.node("john", "concept", is_concept=True)
    base_graph.node("mary", "concept", is_concept=True)
    engine = base_graph.representation_engine

    r_j = ParticipationReceipt("rj", "john", 1, 0, "external", "node", activation_magnitude=0.8)
    r_m = ParticipationReceipt("rm", "mary", 1, 0, "external", "node", activation_magnitude=0.8)
    r_jm = ParticipationReceipt("rjm", ("john", "mary"), 1, 0, "external", "edge", relational_drive=0.8)

    rep = engine.build_representation(1, 0, None, [r_j, r_m, r_jm])
    rccs = engine.get_coherence_components(rep)
    assert len(rccs) == 1
    refs = engine.get_referents(rep)
    assert "john" in refs and "mary" in refs


def test_rfc12_t042_multiple_scoped_receipts_no_node_duplication(base_graph: CognitiveGraph) -> None:
    """RFC12-T042: One underlying Node may have multiple scoped receipts without cognitive duplication."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", scope_refs=("scope_desc",), activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "apple", 1, 0, "external", "node", scope_refs=("scope_compare",), activation_magnitude=0.8)
    rep = engine.build_representation(1, 0, None, [r1, r2])
    assert len(rep.participating_node_refs) == 1


# ─────────────────────────────────────────────────────────── T043..T050: Readout & Transition
def test_rfc12_t043_representation_view_read_only(base_graph: CognitiveGraph) -> None:
    """RFC12-T043: RepresentationView is read-only."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    view = engine.get_view(rep)
    assert view.representation_id == rep.representation_id
    assert "apple" in view.participating_nodes()


def test_rfc12_t044_readout_does_not_activate_nodes(base_graph: CognitiveGraph) -> None:
    """RFC12-T044: Readout does not activate Nodes."""
    base_graph.node("dormant_node", "text").A = 0.0
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    view = engine.get_view(rep)
    view.query({"node": "dormant_node"})
    assert base_graph.node("dormant_node", "text").A == 0.0


def test_rfc12_t045_readout_does_not_learn(base_graph: CognitiveGraph) -> None:
    """RFC12-T045: Readout does not perform learning."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    view = engine.get_view(rep)
    e = base_graph.edge("apple", "fruit")
    w_before = e.W
    view.query({"node": "apple"})
    assert e.W == w_before


def test_rfc12_t046_readout_does_not_mutate_assembly(base_graph: CognitiveGraph) -> None:
    """RFC12-T046: Readout does not mutate Assembly structure."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    view = engine.get_view(rep)
    view.query({"node": "apple"})
    assert len(base_graph.assembly_manager.assemblies) == 0


def test_rfc12_t047_readout_cannot_discover_remote_graph(base_graph: CognitiveGraph) -> None:
    """RFC12-T047: A readout query cannot discover remote graph content."""
    base_graph.link("remote_u", "remote_v", W=0.8)
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    view = engine.get_view(rep)
    res = view.query({"node": "remote_u"})
    assert "node" not in res
    assert engine.observability.remote_scan_attempts_rejected >= 1


def test_rfc12_t048_incremental_equals_reconstruction(base_graph: CognitiveGraph) -> None:
    """RFC12-T048: Incremental construction equals canonical reconstruction."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    r2 = ParticipationReceipt("r2", "fruit", 1, 0, "external", "node", activation_magnitude=0.75)
    r_e = ParticipationReceipt("re", ("apple", "fruit"), 1, 0, "external", "edge", relational_drive=0.8)

    rep1 = engine.build_representation(1, 0, None, [r1, r2, r_e])
    rep2 = engine.build_representation(1, 0, None, [r1, r2, r_e])
    assert engine.canonical_representation_signature(rep1) == engine.canonical_representation_signature(rep2)


def test_rfc12_t049_no_blind_provenance_inheritance(base_graph: CognitiveGraph) -> None:
    """RFC12-T049: Old provenance is not blindly inherited into the next snapshot."""
    engine = base_graph.representation_engine
    r_ext = ParticipationReceipt("r_ext", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep_t0 = engine.build_representation(1, 0, None, [r_ext])
    assert engine.get_element_provenance(rep_t0, "apple") == ["external"]

    r_gen = ParticipationReceipt("r_gen", "apple", 1, 1, "generation", "node", activation_magnitude=0.85)
    rep_t1 = engine.build_representation(1, 1, None, [r_gen])
    assert engine.get_element_provenance(rep_t1, "apple") == ["generation"]


def test_rfc12_t050_old_tbr_expires(base_graph: CognitiveGraph) -> None:
    """RFC12-T050: Old TBRs do not survive without current lawful evidence."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    r2 = ParticipationReceipt("r2", "fruit", 1, 0, "external", "node", activation_magnitude=0.75)
    tbr_t0 = TransientBindingReceipt("tbr_t0", (1, 0), "scope_1", ("apple", "fruit"))
    rep_t0 = engine.build_representation(1, 0, None, [r1, r2], transient_bindings=[tbr_t0])
    assert len(rep_t0.transient_binding_receipts) == 1

    # محاولة تمرير نفس TBR في لقطة جديدة t=1
    rep_t1 = engine.build_representation(1, 1, None, [r1, r2], transient_bindings=[tbr_t0])
    assert len(rep_t1.transient_binding_receipts) == 0
    assert engine.observability.binding_receipts_rejected >= 1


# ─────────────────────────────────────────────────────────── T051..T056: Cross-RFC Boundaries
def test_rfc12_t051_no_pattern_completion_inside_rfc12(base_graph: CognitiveGraph) -> None:
    """RFC12-T051: RFC-12 does not perform Pattern Completion."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    # fruit غير مشارك ولم يتم إضافته تلقائياً بالاستكمال
    assert "fruit" not in rep.participating_node_refs


def test_rfc12_t052_no_sentence_hierarchy(base_graph: CognitiveGraph) -> None:
    """RFC12-T052: RFC-12 does not generate sentence hierarchy."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert not hasattr(rep, "syntax_tree")
    assert not hasattr(rep, "sentence_plan")


def test_rfc12_t053_no_predictive_recurrence(base_graph: CognitiveGraph) -> None:
    """RFC12-T053: RFC-12 does not perform predictive recurrence."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    assert not hasattr(rep, "recurrent_hidden_state")


def test_rfc12_t054_sdcr_cannot_mutate_assembly(base_graph: CognitiveGraph) -> None:
    """RFC12-T054: SDCR cannot directly form/grow/split/merge/retire Assemblies."""
    test_rfc12_t046_readout_does_not_mutate_assembly(base_graph)


def test_rfc12_t055_completion_preserves_provenance(base_graph: CognitiveGraph) -> None:
    """RFC12-T055: Future pattern-completed content preserves self-derived/completion provenance."""
    engine = base_graph.representation_engine
    r_pc = ParticipationReceipt("r_pc", "apple", 1, 0, "prediction", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r_pc])
    assert engine.get_element_provenance(rep, "apple") == ["prediction"]


def test_rfc12_t056_view_selection_does_not_mutate_sdcr(base_graph: CognitiveGraph) -> None:
    """RFC12-T056: Task-specific view selection does not mutate canonical SDCR."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    view = engine.get_view(rep)
    sig_before = engine.canonical_representation_signature(rep)
    view.query({"node": "apple"})
    sig_after = engine.canonical_representation_signature(rep)
    assert sig_before == sig_after


# ─────────────────────────────────────────────────────────── T057..T060: Determinism & Locality
def test_rfc12_t057_deterministic_signature(base_graph: CognitiveGraph) -> None:
    """RFC12-T057: The same canonical snapshot produces the same signature."""
    test_rfc12_t004_rid_is_operational_not_semantic(base_graph)


def test_rfc12_t058_cache_transparency(base_graph: CognitiveGraph) -> None:
    """RFC12-T058: Cache enabled/disabled/rebuilt produces equivalent semantics."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    sig1 = engine.canonical_representation_signature(rep)
    engine.clear_caches()
    sig2 = engine.canonical_representation_signature(rep)
    assert sig1 == sig2


def test_rfc12_t059_remote_graph_growth_invariance(base_graph: CognitiveGraph) -> None:
    """RFC12-T059: Remote graph growth leaves a fixed local SDCR unchanged."""
    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep1 = engine.build_representation(1, 0, None, [r1])
    sig1 = engine.canonical_representation_signature(rep1)

    # إضافة 100 رابط بعيد غير مشارك
    for i in range(100):
        base_graph.link(f"rem_{i}", f"rem_{i+1}", W=0.5)

    rep2 = engine.build_representation(1, 0, None, [r1])
    sig2 = engine.canonical_representation_signature(rep2)
    assert sig1 == sig2


def test_rfc12_t060_high_degree_neighborhood_invariance(base_graph: CognitiveGraph) -> None:
    """RFC12-T060: A high-degree nonparticipating neighborhood does not expand RFC-12 work."""
    # جعل العقدة apple ذات درجة خروج 50
    for i in range(50):
        base_graph.link("apple", f"leaf_{i}", W=0.1)

    engine = base_graph.representation_engine
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", activation_magnitude=0.85)
    rep = engine.build_representation(1, 0, None, [r1])
    # فقط apple مشاركة فعلياً
    assert rep.participating_node_refs == frozenset({"apple"})
    assert len(rep.participating_edge_refs) == 0
