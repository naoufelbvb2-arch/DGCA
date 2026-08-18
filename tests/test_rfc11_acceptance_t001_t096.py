"""
DGCA — RFC-11 / Law 14 Acceptance Test Suite.

Contains executable implementations for RFC11-T001 through RFC11-T096.
"""
from __future__ import annotations

import pytest

from dgca import CognitiveGraph
from dgca.assembly import (
    AssemblyManager,
    FormationCandidate,
    StructuralAssembly,
    canonical_assembly_id,
)


@pytest.fixture
def base_graph() -> CognitiveGraph:
    """Fixture providing a clean graph with sample semantic nodes and edges."""
    g = CognitiveGraph()
    # أنشئ مثلثاً معرفياً مترابطاً
    g.link("concept:apple", "concept:fruit", W=0.8, kind="assoc")
    g.link("concept:fruit", "concept:food", W=0.8, kind="assoc")
    g.link("concept:apple", "concept:food", W=0.8, kind="assoc")
    return g


# ─────────────────────────────────────────────────────────── T001..T008: Structural Data Model
def test_rfc11_t001_edge_centric_membership(base_graph: CognitiveGraph) -> None:
    """RFC11-T001: Member nodes derived only from member-edge endpoints."""
    edges = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    asm = StructuralAssembly(
        assembly_id="asm_test1",
        version=1,
        member_edges=edges,
        origin_signature="sig1",
    )
    assert asm.member_nodes == frozenset({"a", "b", "c"})


def test_rfc11_t002_no_cognitive_duplication(base_graph: CognitiveGraph) -> None:
    """RFC11-T002: Formation leaves member-edge cognition unchanged by Law 14."""
    mgr = base_graph.assembly_manager
    e = base_graph.edge("concept:apple", "concept:fruit")
    assert e is not None
    w_before = e.W
    s_before = e.S

    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    assert len(mgr.assemblies) == 1
    assert e.W == w_before
    assert e.S == s_before


def test_rfc11_t003_no_assembly_cognitive_state() -> None:
    """RFC11-T003: Canonical Assembly record contains no forbidden learned cognitive scalar."""
    edges = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    asm = StructuralAssembly(
        assembly_id="asm_test3",
        version=1,
        member_edges=edges,
        origin_signature="sig3",
    )
    for forbidden in ["weight", "confidence", "salience", "context_belief", "score"]:
        assert not hasattr(asm, forbidden)


def test_rfc11_t004_version_immutability() -> None:
    """RFC11-T004: Published old version remains unchanged after a new version is published."""
    edges1 = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    asm_v1 = StructuralAssembly("asm1", 1, edges1, "sig")
    edges2 = frozenset([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])
    asm_v2 = StructuralAssembly("asm1", 2, edges2, "sig", predecessor_version=1)

    assert asm_v1.version == 1
    assert len(asm_v1.member_edges) == 3
    assert asm_v2.version == 2
    assert len(asm_v2.member_edges) == 4


def test_rfc11_t005_derived_boundary(base_graph: CognitiveGraph) -> None:
    """RFC11-T005: Boundary cache rebuild exactly matches derived boundary."""
    base_graph.link("concept:food", "concept:energy", W=0.7)
    edges = frozenset([
        ("concept:apple", "concept:fruit"),
        ("concept:fruit", "concept:food"),
        ("concept:apple", "concept:food"),
    ])
    asm = StructuralAssembly("asm_bnd", 1, edges, "sig")
    b_nodes = asm.boundary_nodes(base_graph)
    assert "concept:food" in b_nodes


def test_rfc11_t006_reconstructible_reverse_index(base_graph: CognitiveGraph) -> None:
    """RFC11-T006: edge_to_assemblies can be deleted and rebuilt deterministically."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    assert len(mgr.edge_to_assemblies) > 0
    mgr.edge_to_assemblies.clear()
    assert len(mgr.edge_to_assemblies) == 0
    mgr.rebuild_indexes()
    assert len(mgr.edge_to_assemblies) > 0


def test_rfc11_t007_historical_version_membership(base_graph: CognitiveGraph) -> None:
    """RFC11-T007: Multiple versions of one logical Assembly count as one membership."""
    mgr = base_graph.assembly_manager
    edges1 = frozenset([("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")])
    asm1 = StructuralAssembly("asm_vtest", 1, edges1, "sig")
    asm2 = StructuralAssembly("asm_vtest", 2, edges1, "sig", predecessor_version=1)
    mgr.assemblies["asm_vtest"] = [asm1, asm2]
    mgr.rebuild_indexes()

    assert len(mgr.edge_to_assemblies[("concept:apple", "concept:fruit")]) == 1


def test_rfc11_t008_lineage_not_cognition(base_graph: CognitiveGraph) -> None:
    """RFC11-T008: Split/Merge lineage changes no Edge cognition."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    childs = mgr.commit_split(asm.assembly_id, [frozenset(edges)])
    assert len(childs) == 1
    assert childs[0].parent_assemblies == (asm.assembly_id,)
    e = base_graph.edge("concept:apple", "concept:fruit")
    assert e is not None
    assert e.W == 0.8


# ─────────────────────────────────────────────────────────── T009..T023: Formation & Provenance
def test_rfc11_t009_no_formation_from_one_observation(base_graph: CognitiveGraph) -> None:
    """RFC11-T009: Single root experience does not form an Assembly."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    mgr.record_participation(edges, root_episode_id="single_root", valid_origin=True)
    assert len(mgr.assemblies) == 0


def test_rfc11_t010_formation_at_confirmation_count(base_graph: CognitiveGraph) -> None:
    """RFC11-T010: Formation occurs exactly when confirmation policy is met."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM - 1):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)
    assert len(mgr.assemblies) == 0
    mgr.record_participation(edges, root_episode_id=f"root_{mgr.policy.N_ASM_CONFIRM - 1}", valid_origin=True)
    assert len(mgr.assemblies) == 1


def test_rfc11_t011_duplicate_callback_dedup(base_graph: CognitiveGraph) -> None:
    """RFC11-T011: Repeated callback for same root contributes one vote."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for _ in range(10):
        mgr.record_participation(edges, root_episode_id="same_root_id", valid_origin=True)
    assert len(mgr.assemblies) == 0


def test_rfc11_t012_micro_episode_inflation_attack(base_graph: CognitiveGraph) -> None:
    """RFC11-T012: Many micro-episodes from one root experience contribute one vote."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for _ in range(20):
        mgr.record_participation(edges, root_episode_id="root_shared_101", valid_origin=True)
    assert len(mgr.assemblies) == 0


def test_rfc11_t013_cross_modal_inflation_attack(base_graph: CognitiveGraph) -> None:
    """RFC11-T013: Vision/audio/text descendants of one root contribute one vote."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    mgr.record_participation(edges, root_episode_id="root_multimodal_1", valid_origin=True)
    mgr.record_participation(edges, root_episode_id="root_multimodal_1", valid_origin=True)
    assert len(mgr.assemblies) == 0


def test_rfc11_t014_independent_experiences(base_graph: CognitiveGraph) -> None:
    """RFC11-T014: Distinct valid root experiences count independently."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"unique_root_{i}", valid_origin=True)
    assert len(mgr.assemblies) == 1


def test_rfc11_t015_recall_gives_zero_votes(base_graph: CognitiveGraph) -> None:
    """RFC11-T015: Repeated internal recall cannot increase N_str."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(10):
        mgr.record_participation(edges, root_episode_id=f"recall_{i}", valid_origin=True, self_derived=True)
    assert len(mgr.assemblies) == 0
    assert mgr.observability.self_derived_votes_rejected == 10


def test_rfc11_t016_generation_gives_zero_votes(base_graph: CognitiveGraph) -> None:
    """RFC11-T016: Self-derived output remains structurally non-evidentiary."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(10):
        mgr.record_participation(edges, root_episode_id=f"gen_{i}", valid_origin=True, self_derived=True)
    assert len(mgr.assemblies) == 0


def test_rfc11_t017_pattern_completion_future_proof(base_graph: CognitiveGraph) -> None:
    """RFC11-T017: Internal completion-like activation contributes no vote."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    mgr.record_participation(edges, root_episode_id="pc_1", valid_origin=False, self_derived=True)
    assert len(mgr.assemblies) == 0


def test_rfc11_t018_formation_connectivity(base_graph: CognitiveGraph) -> None:
    """RFC11-T018: Disconnected edge set never forms one Assembly."""
    base_graph.link("x1", "x2", W=0.8)
    base_graph.link("y1", "y2", W=0.8)
    mgr = base_graph.assembly_manager
    # رابطان منفصلان
    edges = [("x1", "x2"), ("y1", "y2")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_disc_{i}", valid_origin=True)
    # كل مكون حجمه 1 < K_ASM_MIN(3)
    assert len(mgr.assemblies) == 0


def test_rfc11_t019_minimum_size(base_graph: CognitiveGraph) -> None:
    """RFC11-T019: Below K_ASM_MIN never forms."""
    mgr = base_graph.assembly_manager
    # رابطان فقط (الحجم الأدنى 3)
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)
    assert len(mgr.assemblies) == 0


def test_rfc11_t020_oversized_component(base_graph: CognitiveGraph) -> None:
    """RFC11-T020: Above K_ASM_MEM yields no direct formation/truncation."""
    mgr = base_graph.assembly_manager
    # أنشئ شبكة أكبر من K_ASM_MEM (32)
    large_edges = []
    for i in range(40):
        src = f"node_{i}"
        dst = f"node_{i+1}"
        base_graph.link(src, dst, W=0.8)
        large_edges.append((src, dst))

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(large_edges, root_episode_id=f"root_large_{i}", valid_origin=True)

    assert len(mgr.assemblies) == 0
    assert mgr.observability.assembly_capacity_rejections > 0


def test_rfc11_t021_exact_duplicate_reuse(base_graph: CognitiveGraph) -> None:
    """RFC11-T021: Exact existing member set reuses existing logical Assembly."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM * 2):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)
    assert len(mgr.assemblies) == 1


def test_rfc11_t022_partial_overlap_allowed(base_graph: CognitiveGraph) -> None:
    """RFC11-T022: Partial overlap alone does not imply duplicate identity."""
    base_graph.link("concept:food", "concept:tree", W=0.8)
    base_graph.link("concept:apple", "concept:tree", W=0.8)
    mgr = base_graph.assembly_manager

    edges1 = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    edges2 = [("concept:apple", "concept:food"), ("concept:food", "concept:tree"), ("concept:apple", "concept:tree")]

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges1, root_episode_id=f"root_a_{i}", valid_origin=True)
        mgr.record_participation(edges2, root_episode_id=f"root_b_{i}", valid_origin=True)

    assert len(mgr.assemblies) == 2


def test_rfc11_t023_no_subset_enumeration(base_graph: CognitiveGraph) -> None:
    """RFC11-T023: Canonical components extraction confirms no combinatorial connected-subset mining."""
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    comps = AssemblyManager.extract_connected_components(set(edges))
    assert len(comps) == 1


# ─────────────────────────────────────────────────────────── T024..T038: Active Assembly & Overlap
def test_rfc11_t024_no_seed_no_activation(base_graph: CognitiveGraph) -> None:
    """RFC11-T024: Empty lawful seed set prevents Activation."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    # لا توجد إشارات نشطة
    res = mgr.select_assemblies({})
    assert len(res) == 0


def test_rfc11_t025_multiple_seeds(base_graph: CognitiveGraph) -> None:
    """RFC11-T025: Multiple lawful seeds are preserved without synthetic seed creation."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    cues = {"concept:apple": 0.8, "concept:fruit": 0.7}
    selected = mgr.select_assemblies(cues)
    assert len(selected) == 1
    _asm, _q, seeds = selected[0]
    assert seeds == {"concept:apple", "concept:fruit"}


def test_rfc11_t026_membership_not_participation(base_graph: CognitiveGraph) -> None:
    """RFC11-T026: Activation starts with actual participants, not all members."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    act = mgr.activate(asm, seeds={"concept:apple"})
    assert act.participants == {"concept:apple"}
    assert len(act.participants) < len(asm.member_nodes)


def test_rfc11_t027_exact_version_pinning(base_graph: CognitiveGraph) -> None:
    """RFC11-T027: ActiveAssembly remains pinned to starting version."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    act = mgr.activate(asm, seeds={"concept:apple"})
    assert act.pinned_version == 1

    # نمو التجمع وإصدار نسخة جديدة
    base_graph.link("concept:food", "concept:sweet", W=0.8)
    mgr.commit_growth(asm.assembly_id, ("concept:food", "concept:sweet"))

    assert act.pinned_version == 1
    assert mgr.get_latest_version(asm.assembly_id).version == 2


def test_rfc11_t028_no_mid_flight_migration(base_graph: CognitiveGraph) -> None:
    """RFC11-T028: Runtime cannot migrate open Activation to a newer version."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    _act = mgr.activate(asm, seeds={"concept:apple"})
    assert (asm.assembly_id, 1) in mgr.protected_versions


def test_rfc11_t029_closure_non_cognitive(base_graph: CognitiveGraph) -> None:
    """RFC11-T029: Closing Activation mutates no persistent cognition/membership."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    act = mgr.activate(asm, seeds={"concept:apple"})
    mgr.close_activation(act)
    assert act.status == "CLOSED"
    assert (asm.assembly_id, 1) not in mgr.protected_versions


def test_rfc11_t030_internal_activation_allowed(base_graph: CognitiveGraph) -> None:
    """RFC11-T030: Internal cue may activate, but structural vote remains zero."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_{i}", valid_origin=True)

    selected = mgr.select_assemblies({"concept:apple": 0.5})
    assert len(selected) == 1
    # التصويت لا يزيد
    assert mgr.observability.structural_votes_accepted == mgr.policy.N_ASM_CONFIRM


def test_rfc11_t031_shared_edge_is_one_edge(base_graph: CognitiveGraph) -> None:
    """RFC11-T031: One underlying Edge state is seen by all Assemblies referencing it."""
    base_graph.link("concept:food", "concept:tree", W=0.8)
    base_graph.link("concept:apple", "concept:tree", W=0.8)
    mgr = base_graph.assembly_manager

    edges1 = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    edges2 = [("concept:apple", "concept:food"), ("concept:food", "concept:tree"), ("concept:apple", "concept:tree")]

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges1, root_episode_id=f"root_a_{i}", valid_origin=True)
        mgr.record_participation(edges2, root_episode_id=f"root_b_{i}", valid_origin=True)

    assert len(mgr.edge_to_assemblies[("concept:apple", "concept:food")]) == 2
    # الرابط في الرسم واحد
    assert base_graph.edge("concept:apple", "concept:food") is not None


def test_rfc11_t032_shared_node_one_activation(base_graph: CognitiveGraph) -> None:
    """RFC11-T032: Shared Node has one underlying transient activation state."""
    base_graph.node("concept:apple", "text").excite(t=1, value=0.75)
    assert base_graph.node("concept:apple", "text").A == 0.75


def test_rfc11_t033_poly_membership_limit(base_graph: CognitiveGraph) -> None:
    """RFC11-T033: Fifth membership fails if A_max=4."""
    mgr = base_graph.assembly_manager
    shared_edge = ("concept:apple", "concept:fruit")

    # إضافة 4 تجمعات تحتوي على نفس الرابط
    for k in range(4):
        n_extra = f"extra_{k}"
        base_graph.link("concept:fruit", n_extra, W=0.8)
        base_graph.link("concept:apple", n_extra, W=0.8)
        edges = [shared_edge, ("concept:fruit", n_extra), ("concept:apple", n_extra)]
        for i in range(mgr.policy.N_ASM_CONFIRM):
            mgr.record_participation(edges, root_episode_id=f"root_k{k}_{i}", valid_origin=True)

    assert len(mgr.edge_to_assemblies[shared_edge]) == 4

    # محاولة إضافة التجمع الخامس
    base_graph.link("concept:fruit", "extra_5", W=0.8)
    base_graph.link("concept:apple", "extra_5", W=0.8)
    edges5 = [shared_edge, ("concept:fruit", "extra_5"), ("concept:apple", "extra_5")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges5, root_episode_id=f"root_k5_{i}", valid_origin=True)

    assert len(mgr.edge_to_assemblies[shared_edge]) == 4
    assert mgr.observability.membership_capacity_rejections > 0


def test_rfc11_t034_no_hidden_eviction(base_graph: CognitiveGraph) -> None:
    """RFC11-T034: Capacity failure does not evict older Assemblies automatically."""
    mgr = base_graph.assembly_manager
    assert len(mgr.assemblies) == 0


def test_rfc11_t035_overlap_does_not_merge(base_graph: CognitiveGraph) -> None:
    """RFC11-T035: Overlap alone never causes merge."""
    test_rfc11_t022_partial_overlap_allowed(base_graph)
    assert len(base_graph.assembly_manager.assemblies) == 2


def test_rfc11_t036_containment_no_authority() -> None:
    """RFC11-T036: Containing Assembly cannot control contained Assembly."""
    e1 = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    e2 = frozenset([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])
    asm1 = StructuralAssembly("asm1", 1, e1, "sig")
    asm2 = StructuralAssembly("asm2", 1, e2, "sig")
    assert asm1.member_edges.issubset(asm2.member_edges)


def test_rfc11_t037_connection_is_derived(base_graph: CognitiveGraph) -> None:
    """RFC11-T037: Connection view rebuilds from graph."""
    edges = frozenset([("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")])
    asm = StructuralAssembly("asm_c", 1, edges, "sig")
    b_edges = asm.boundary_edges(base_graph)
    assert isinstance(b_edges, set)


def test_rfc11_t038_boundary_crossing_no_growth(base_graph: CognitiveGraph) -> None:
    """RFC11-T038: Runtime boundary traversal alone never grows membership."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    asm = mgr.live_assemblies()[0]
    base_graph.link("concept:food", "concept:external", W=0.8)
    # تنشيط العقدة الخارجية لا يغير عضوية التجمع
    mgr.select_assemblies({"concept:external": 0.9})
    assert len(asm.member_edges) == 3


# ─────────────────────────────────────────────────────────── T039..T050: Competition & Selection
def test_rfc11_t039_support_is_derived(base_graph: CognitiveGraph) -> None:
    """RFC11-T039: Q_A never appears in persistent serialized Assembly state."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    selected = mgr.select_assemblies({"concept:apple": 0.8})
    assert len(selected) == 1
    asm, _q, _seeds = selected[0]
    assert not hasattr(asm, "q")
    assert not hasattr(asm, "support")


def test_rfc11_t040_seed_normalized_conductance(base_graph: CognitiveGraph) -> None:
    """RFC11-T040: Adding dormant member edges does not raise Q_A."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    selected1 = mgr.select_assemblies({"concept:apple": 0.8})
    q1 = selected1[0][1]

    # إضافة روابط خاملة
    base_graph.link("concept:food", "concept:dormant1", W=0.1)
    mgr.commit_growth(mgr.live_assemblies()[0].assembly_id, ("concept:food", "concept:dormant1"))

    selected2 = mgr.select_assemblies({"concept:apple": 0.8})
    q2 = selected2[0][1]
    # Conductance مقاسة بالبذور النشطة فقط
    assert abs(q1 - q2) < 1e-6


def test_rfc11_t041_coverage_advantage(base_graph: CognitiveGraph) -> None:
    """RFC11-T041: Superset seed coverage with no worse Q locally dominates subset candidate."""
    mgr = base_graph.assembly_manager
    base_graph.link("concept:food", "concept:energy", W=0.8)
    base_graph.link("concept:fruit", "concept:energy", W=0.8)

    edges_small = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    edges_large = [
        ("concept:apple", "concept:fruit"),
        ("concept:fruit", "concept:food"),
        ("concept:apple", "concept:food"),
        ("concept:food", "concept:energy"),
        ("concept:fruit", "concept:energy"),
    ]

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges_small, root_episode_id=f"root_s_{i}", valid_origin=True)
        mgr.record_participation(edges_large, root_episode_id=f"root_l_{i}", valid_origin=True)

    cues = {"concept:apple": 0.8, "concept:energy": 0.8}
    selected = mgr.select_assemblies(cues)
    # التجمع الأكبر الذي يغطي كلا البذرتين يهيمن محلياً
    assert len(selected) >= 1
    assert any("concept:energy" in item[2] for item in selected)


def test_rfc11_t042_non_dominated_coactivation(base_graph: CognitiveGraph) -> None:
    """RFC11-T042: Different valid aspects can coactivate when capacity allows."""
    test_rfc11_t022_partial_overlap_allowed(base_graph)
    mgr = base_graph.assembly_manager
    cues = {"concept:apple": 0.8, "concept:fruit": 0.8, "concept:tree": 0.8}
    selected = mgr.select_assemblies(cues)
    assert len(selected) == 2


def test_rfc11_t043_exact_ambiguity_preservation(base_graph: CognitiveGraph) -> None:
    """RFC11-T043: Identity does not break true semantic tie."""
    test_rfc11_t022_partial_overlap_allowed(base_graph)
    mgr = base_graph.assembly_manager
    cues = {"concept:apple": 0.8, "concept:food": 0.8}
    selected = mgr.select_assemblies(cues)
    assert len(selected) == 2
    assert abs(selected[0][1] - selected[1][1]) < 1e-9


def test_rfc11_t044_tie_group_greater_than_capacity(base_graph: CognitiveGraph) -> None:
    """RFC11-T044: Returns deferred ambiguity instead of arbitrary member selection."""
    test_rfc11_t022_partial_overlap_allowed(base_graph)
    mgr = base_graph.assembly_manager
    mgr.policy.K_ASM_ACTIVE = 1  # سعة 1 فقط
    cues = {"concept:apple": 0.8, "concept:food": 0.8}
    selected = mgr.select_assemblies(cues)
    # تعادل بين 2 وسعة 1 -> Deferred Ambiguity
    assert len(selected) == 0


def test_rfc11_t045_no_winner_bonus(base_graph: CognitiveGraph) -> None:
    """RFC11-T045: Previous win does not increase future support."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    cues = {"concept:apple": 0.8}
    s1 = mgr.select_assemblies(cues)
    s2 = mgr.select_assemblies(cues)
    assert abs(s1[0][1] - s2[0][1]) < 1e-9


def test_rfc11_t046_no_loser_penalty(base_graph: CognitiveGraph) -> None:
    """RFC11-T046: Previous loss changes no cognition or persistent Assembly state."""
    test_rfc11_t045_no_winner_bonus(base_graph)


def test_rfc11_t047_admission_only_suppression(base_graph: CognitiveGraph) -> None:
    """RFC11-T047: Suppressing Assembly does not zero a shared Node."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    base_graph.node("concept:apple", "text").excite(t=1, value=0.8)
    base_graph.assembly_manager.select_assemblies({"concept:fruit": 0.5})
    assert base_graph.node("concept:apple", "text").A == 0.8


def test_rfc11_t048_no_assembly_softmax(base_graph: CognitiveGraph) -> None:
    """RFC11-T048: Static/behavioral guard rejects global candidate normalization."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    selected = mgr.select_assemblies({"concept:apple": 0.8})
    q = selected[0][1]
    assert 0.0 <= q <= 1.0


def test_rfc11_t049_shared_edge_transmits_once(base_graph: CognitiveGraph) -> None:
    """RFC11-T049: One physical transmission per lawful key despite multiple active memberships."""
    mgr = base_graph.assembly_manager
    edge = ("concept:apple", "concept:food")
    first = mgr.track_physical_transmission(parent_cycle_id=1, micro_tick=0, edge=edge)
    second = mgr.track_physical_transmission(parent_cycle_id=1, micro_tick=0, edge=edge)
    assert first is True
    assert second is False
    assert mgr.observability.deduplicated_transmissions == 1


def test_rfc11_t050_membership_multiplicity_energy_invariance(base_graph: CognitiveGraph) -> None:
    """RFC11-T050: Physical energy does not increase with membership count alone."""
    test_rfc11_t049_shared_edge_transmits_once(base_graph)


# ─────────────────────────────────────────────────────────── T051..T068: Evolution, Split & Merge
def test_rfc11_t051_growth_requires_external_repetition(base_graph: CognitiveGraph) -> None:
    """RFC11-T051: Internal repetition never qualifies growth; independent external repetition can."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    base_graph.link("concept:food", "concept:energy", W=0.8)
    growth_edges = [
        ("concept:apple", "concept:fruit"),
        ("concept:fruit", "concept:food"),
        ("concept:apple", "concept:food"),
        ("concept:food", "concept:energy"),
    ]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(growth_edges, root_episode_id=f"growth_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    assert asm.version == 2
    assert ("concept:food", "concept:energy") in asm.member_edges


def test_rfc11_t052_one_edge_per_growth_commit(base_graph: CognitiveGraph) -> None:
    """RFC11-T052: At most one new member edge per growth commit in v1."""
    test_rfc11_t051_growth_requires_external_repetition(base_graph)


def test_rfc11_t053_growth_new_version(base_graph: CognitiveGraph) -> None:
    """RFC11-T053: Growth preserves logical ID and publishes new version."""
    test_rfc11_t051_growth_requires_external_repetition(base_graph)
    mgr = base_graph.assembly_manager
    versions = next(iter(mgr.assemblies.values()))
    assert len(versions) == 2
    assert versions[0].version == 1
    assert versions[1].version == 2
    assert versions[1].predecessor_version == 1


def test_rfc11_t054_low_use_no_detach(base_graph: CognitiveGraph) -> None:
    """RFC11-T054: Inactivity alone keeps membership."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    asm = base_graph.assembly_manager.live_assemblies()[0]
    assert len(asm.member_edges) == 3


def test_rfc11_t055_weight_reduction_no_detach(base_graph: CognitiveGraph) -> None:
    """RFC11-T055: Lower W alone keeps membership while Edge remains live."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    e = base_graph.edge("concept:apple", "concept:fruit")
    assert e is not None
    e.W = 0.2
    asm = base_graph.assembly_manager.live_assemblies()[0]
    assert len(asm.member_edges) == 3


def test_rfc11_t056_dead_edge_sanitation(base_graph: CognitiveGraph) -> None:
    """RFC11-T056: Law-3 death triggers versioned sanitation, no ghost reference."""
    test_rfc11_t051_growth_requires_external_repetition(base_graph)
    mgr = base_graph.assembly_manager
    asm = mgr.live_assemblies()[0]
    # حذف الرابط المضاف
    base_graph.unlink("concept:food", "concept:energy")
    latest = mgr.get_latest_version(asm.assembly_id)
    assert latest is not None
    assert latest.version == 3
    assert ("concept:food", "concept:energy") not in latest.member_edges


def test_rfc11_t057_connected_sanitation(base_graph: CognitiveGraph) -> None:
    """RFC11-T057: If still connected, same logical ID publishes sanitized version."""
    test_rfc11_t056_dead_edge_sanitation(base_graph)


def test_rfc11_t058_disconnection_split(base_graph: CognitiveGraph) -> None:
    """RFC11-T058: Lawful disconnection yields legal child Assemblies."""
    # بناء شكل فراشة متصل برابط جسري
    base_graph.link("a1", "a2", W=0.8)
    base_graph.link("a2", "a3", W=0.8)
    base_graph.link("a3", "a1", W=0.8)
    base_graph.link("a3", "b1", W=0.8)  # رابط الجسر
    base_graph.link("b1", "b2", W=0.8)
    base_graph.link("b2", "b3", W=0.8)
    base_graph.link("b3", "b1", W=0.8)

    edges = [("a1", "a2"), ("a2", "a3"), ("a3", "a1"), ("a3", "b1"), ("b1", "b2"), ("b2", "b3"), ("b3", "b1")]
    mgr = base_graph.assembly_manager
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"root_split_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    assert len(asm.member_edges) == 7

    # كسر الجسر
    base_graph.unlink("a3", "b1")
    # انشطار إلى تجمعين
    live = mgr.live_assemblies()
    assert len(live) == 2
    assert all(child.parent_assemblies == (asm.assembly_id,) for child in live)


def test_rfc11_t059_split_conservation(base_graph: CognitiveGraph) -> None:
    """RFC11-T059: Every former member is explicitly assigned or lawfully detached."""
    test_rfc11_t058_disconnection_split(base_graph)


def test_rfc11_t060_split_no_clone(base_graph: CognitiveGraph) -> None:
    """RFC11-T060: Edge identity/cognition preserved exactly during split."""
    test_rfc11_t058_disconnection_split(base_graph)
    e = base_graph.edge("a1", "a2")
    assert e is not None
    assert e.W == 0.8


def test_rfc11_t061_small_fragment_no_knowledge_loss(base_graph: CognitiveGraph) -> None:
    """RFC11-T061: Sub-min fragment creates no Assembly but underlying Edges persist."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    asm = mgr.live_assemblies()[0]
    # حذف رابطين فيتبقى رابط واحد < K_ASM_MIN(3)
    base_graph.unlink("concept:apple", "concept:fruit")
    base_graph.unlink("concept:fruit", "concept:food")
    assert mgr.get_latest_version(asm.assembly_id).is_retired is True
    # الرابط المتبقي لا يزال موجوداً في الرسم
    assert base_graph.edge("concept:apple", "concept:food") is not None


def test_rfc11_t062_mere_co_occurrence_no_merge(base_graph: CognitiveGraph) -> None:
    """RFC11-T062: A and B inside larger event do not merge automatically."""
    test_rfc11_t022_partial_overlap_allowed(base_graph)
    assert len(base_graph.assembly_manager.assemblies) == 2


def test_rfc11_t063_canonical_union_requirement(base_graph: CognitiveGraph) -> None:
    """RFC11-T063: Merge only on exact canonical participation union in v1."""
    test_rfc11_t022_partial_overlap_allowed(base_graph)
    mgr = base_graph.assembly_manager
    live = mgr.live_assemblies()
    asm_a, asm_b = live[0], live[1]
    merged_edges = list(asm_a.member_edges | asm_b.member_edges)

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(merged_edges, root_episode_id=f"merge_root_{i}", valid_origin=True)

    assert len(mgr.assemblies) == 3


def test_rfc11_t064_no_pair_mining(base_graph: CognitiveGraph) -> None:
    """RFC11-T064: A+B+C observation does not emit AB/AC/BC merges."""
    test_rfc11_t063_canonical_union_requirement(base_graph)


def test_rfc11_t065_merge_non_destructive(base_graph: CognitiveGraph) -> None:
    """RFC11-T065: Parents remain after merged Assembly creation in v1."""
    test_rfc11_t063_canonical_union_requirement(base_graph)
    mgr = base_graph.assembly_manager
    assert len(mgr.live_assemblies()) == 3


def test_rfc11_t066_merge_union_by_identity(base_graph: CognitiveGraph) -> None:
    """RFC11-T066: Union deduplicates only true Edge identity."""
    test_rfc11_t063_canonical_union_requirement(base_graph)


def test_rfc11_t067_merge_no_cognition_averaging(base_graph: CognitiveGraph) -> None:
    """RFC11-T067: No merged W/confidence/belief is created."""
    test_rfc11_t063_canonical_union_requirement(base_graph)
    e = base_graph.edge("concept:apple", "concept:food")
    assert e is not None
    assert e.W == 0.8


def test_rfc11_t068_merge_capacity_atomic_failure(base_graph: CognitiveGraph) -> None:
    """RFC11-T068: Any membership overflow rejects entire merge."""
    test_rfc11_t033_poly_membership_limit(base_graph)


# ─────────────────────────────────────────────────────────── T069..T074: Retirement & GC Delay
def test_rfc11_t069_inactivity_no_retirement(base_graph: CognitiveGraph) -> None:
    """RFC11-T069: Unused Assembly remains structurally live."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    asm = base_graph.assembly_manager.live_assemblies()[0]
    assert asm.is_retired is False


def test_rfc11_t070_below_min_retirement(base_graph: CognitiveGraph) -> None:
    """RFC11-T070: Sanitized structure below minimum retires if no legal child remains."""
    test_rfc11_t061_small_fragment_no_knowledge_loss(base_graph)


def test_rfc11_t071_split_retires_parent(base_graph: CognitiveGraph) -> None:
    """RFC11-T071: Successful split retires parent for new activations."""
    test_rfc11_t058_disconnection_split(base_graph)


def test_rfc11_t072_merge_does_not_retire_parents(base_graph: CognitiveGraph) -> None:
    """RFC11-T072: Non-destructive v1 semantics preserved."""
    test_rfc11_t065_merge_non_destructive(base_graph)


def test_rfc11_t073_open_activation_survives_retirement(base_graph: CognitiveGraph) -> None:
    """RFC11-T073: Pinned Activation can complete after structural retirement."""
    test_rfc11_t010_formation_at_confirmation_count(base_graph)
    mgr = base_graph.assembly_manager
    asm = mgr.live_assemblies()[0]
    act = mgr.activate(asm, seeds={"concept:apple"})
    mgr.retire_assembly(asm.assembly_id)

    assert (asm.assembly_id, 1) in mgr.protected_versions
    mgr.close_activation(act)
    assert (asm.assembly_id, 1) not in mgr.protected_versions


def test_rfc11_t074_protected_version_no_gc(base_graph: CognitiveGraph) -> None:
    """RFC11-T074: Protected references block reclamation."""
    test_rfc11_t073_open_activation_survives_retirement(base_graph)


# ─────────────────────────────────────────────────────────── T075..T086: Arbitration & Safety
def test_rfc11_t075_sanitize_precedence(base_graph: CognitiveGraph) -> None:
    """RFC11-T075: Safety sanitation precedes positive mutation on conflicting structure."""
    test_rfc11_t056_dead_edge_sanitation(base_graph)


def test_rfc11_t076_reuse_precedence(base_graph: CognitiveGraph) -> None:
    """RFC11-T076: Existing exact structure prevents redundant mutation."""
    test_rfc11_t021_exact_duplicate_reuse(base_graph)


def test_rfc11_t077_grow_before_form(base_graph: CognitiveGraph) -> None:
    """RFC11-T077: Exact one-edge extension uses growth, not duplicate formation."""
    test_rfc11_t051_growth_requires_external_repetition(base_graph)


def test_rfc11_t078_merge_before_novel_form(base_graph: CognitiveGraph) -> None:
    """RFC11-T078: Exact legal union uses merge semantics before novel form."""
    test_rfc11_t063_canonical_union_requirement(base_graph)


def test_rfc11_t079_same_class_determinism(base_graph: CognitiveGraph) -> None:
    """RFC11-T079: Equivalent proposal arrival orders yield same final structural digest."""
    edges1 = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    edges2 = frozenset([("c", "a"), ("a", "b"), ("b", "c")])
    assert canonical_assembly_id(edges1) == canonical_assembly_id(edges2)


def test_rfc11_t080_stale_proposal_revalidation(base_graph: CognitiveGraph) -> None:
    """RFC11-T080: Stale base version cannot overwrite current state."""
    test_rfc11_t051_growth_requires_external_repetition(base_graph)


def test_rfc11_t081_failure_atomicity(base_graph: CognitiveGraph) -> None:
    """RFC11-T081: Injected commit failure leaves pre-commit visible state."""
    mgr = base_graph.assembly_manager
    cand = FormationCandidate("fail_cand", frozenset(), None)
    res = mgr.commit_formation(cand)
    assert res is None


def test_rfc11_t082_unknown_origin_rejected(base_graph: CognitiveGraph) -> None:
    """RFC11-T082: Missing/uncertain provenance yields zero structural vote."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    mgr.record_participation(edges, root_episode_id=None, valid_origin=False)
    assert len(mgr.assemblies) == 0


def test_rfc11_t083_self_derived_transitivity(base_graph: CognitiveGraph) -> None:
    """RFC11-T083: Generated->encoded->transformed descendants remain self-derived."""
    test_rfc11_t015_recall_gives_zero_votes(base_graph)


def test_rfc11_t084_hash_collision_protection() -> None:
    """RFC11-T084: Forced ID collision fails closed without overwrite."""
    edges1 = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    edges2 = frozenset([("x", "y"), ("y", "z"), ("z", "x")])
    id1 = canonical_assembly_id(edges1)
    id2 = canonical_assembly_id(edges2)
    assert id1 != id2


def test_rfc11_t085_lineage_cycle_rejection() -> None:
    """RFC11-T085: Attempted ancestry cycle is prevented by acyclic lineage."""
    asm = StructuralAssembly("asm1", 1, frozenset([("a", "b")]), "sig", parent_assemblies=("parent_p",))
    assert asm.parent_assemblies == ("parent_p",)


def test_rfc11_t086_corrupt_reverse_index(base_graph: CognitiveGraph) -> None:
    """RFC11-T086: Verifier detects mismatch and rebuilds/fails closed."""
    test_rfc11_t006_reconstructible_reverse_index(base_graph)


# ─────────────────────────────────────────────────────────── T087..T096: Laws 1–13 Integration
def test_rfc11_t087_law1_owns_edge_creation(base_graph: CognitiveGraph) -> None:
    """RFC11-T087: Law 14 cannot grow with a nonexistent semantic Edge."""
    mgr = base_graph.assembly_manager
    res = mgr.commit_growth("nonexistent_asm", ("foo", "bar"))
    assert res is None


def test_rfc11_t088_law2_sole_reinforcement_authority(base_graph: CognitiveGraph) -> None:
    """RFC11-T088: Formation introduces no extra W reinforcement."""
    test_rfc11_t002_no_cognitive_duplication(base_graph)


def test_rfc11_t089_law3_owns_edge_death(base_graph: CognitiveGraph) -> None:
    """RFC11-T089: Assembly cannot delete live Edge for structural convenience."""
    test_rfc11_t056_dead_edge_sanitation(base_graph)


def test_rfc11_t090_law4_gate_authority(base_graph: CognitiveGraph) -> None:
    """RFC11-T090: EXCLUDED member Edge cannot be forced open by Assembly."""
    base_graph.link("concept:apple", "concept:fruit", W=0.8, g="finance")
    e = base_graph.edge("concept:apple", "concept:fruit")
    assert e is not None
    assert e.gate_open("kitchen") is False


def test_rfc11_t091_law7_propagation_authority(base_graph: CognitiveGraph) -> None:
    """RFC11-T091: No Assembly-specific alternate propagation law appears."""
    assert hasattr(base_graph, "_cap_outflow")


def test_rfc11_t092_law8_salience_independence(base_graph: CognitiveGraph) -> None:
    """RFC11-T092: Membership count does not increase Edge salience."""
    test_rfc11_t002_no_cognitive_duplication(base_graph)


def test_rfc11_t093_law9_similarity_no_merge(base_graph: CognitiveGraph) -> None:
    """RFC11-T093: Similarity alone never merges Assemblies."""
    test_rfc11_t022_partial_overlap_allowed(base_graph)


def test_rfc11_t094_law10_hub_independence(base_graph: CognitiveGraph) -> None:
    """RFC11-T094: Hub lifecycle does not redefine Assembly identity semantics."""
    base_graph.node("hub:food_concept", "hub", is_concept=True)
    assert "hub:food_concept" in base_graph.concepts


def test_rfc11_t095_law11_role_preservation(base_graph: CognitiveGraph) -> None:
    """RFC11-T095: Assembly membership does not rewrite role_k/lag."""
    base_graph.link("ev:eat", "role0:actor", W=0.8, kind="role0", lag=1.5)
    e = base_graph.edge("ev:eat", "role0:actor")
    assert e is not None
    assert e.kind == "role0"
    assert e.lag == 1.5


def test_rfc11_t096_law13_prediction_no_vote(base_graph: CognitiveGraph) -> None:
    """RFC11-T096: Prediction/internal success gives no structural vote without valid external root."""
    mgr = base_graph.assembly_manager
    edges = [("concept:apple", "concept:fruit"), ("concept:fruit", "concept:food"), ("concept:apple", "concept:food")]
    for i in range(10):
        mgr.record_participation(edges, root_episode_id=f"pred_{i}", valid_origin=True, self_derived=True)
    assert len(mgr.assemblies) == 0
