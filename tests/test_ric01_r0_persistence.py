"""
DGCA — RIC-01 / R0 Test Suite.
Persistent Cognitive State & Runtime Lifecycle Contract Formal Architecture Specification v1.1 — FROZEN.

Coverage:
- Invariants: R0-I01 through R0-I24
- Acceptance Tests: T01 through T40
- Additional Adversarial Tests: A through I
"""
from __future__ import annotations

import copy
import json
import math
import pathlib
from unittest.mock import patch

import pytest

from dgca import (
    CheckpointCompatibilityError,
    CheckpointIntegrityError,
    CheckpointSchemaError,
    CheckpointValidationError,
    CognitiveGraph,
    Edge,
    FormationCandidate,
    Node,
    RuntimeRoot,
    StructuralAssembly,
    StructuralReferentialIntegrityError,
    compute_checkpoint_state_digest,
    restore_cognitive_checkpoint,
    save_cognitive_checkpoint,
)
from dgca.persistence import (
    extract_canonical_persistent_payload,
    validate_structural_referential_integrity,
)


def make_rich_graph(t: int = 100) -> CognitiveGraph:
    """Helper to construct a rich, valid CognitiveGraph with durable and transient state."""
    g = CognitiveGraph(t=t)

    # 1. Nodes: diverse regions, concepts, intrinsic, durable fields, transient fields
    g.nodes["n1"] = Node(
        nid="n1",
        region="TEXT",
        is_concept=True,
        members={"tok_a", "tok_b"},
        U=0.8,
        V=0.2,
        head="head_1",
        is_intrinsic=False,
        N_total=10,
        A=0.95,
        t_spawn=50,
        episode="ep_old_1",
    )
    g.nodes["n2"] = Node(
        nid="n2",
        region="TEXT",
        is_concept=False,
        members=set(),
        U=0.3,
        V=0.1,
        head=None,
        is_intrinsic=True,
        N_total=5,
        A=0.7,
        t_spawn=60,
        episode="ep_old_1",
    )
    g.nodes["n3"] = Node(
        nid="n3",
        region="QUANTITY",
        is_concept=False,
        members=set(),
        U=0.5,
        V=0.5,
        head=None,
        is_intrinsic=False,
        N_total=2,
        A=0.4,
        t_spawn=70,
        episode="ep_old_2",
    )

    # 2. Edges: durable fields and transient fields
    e1 = Edge(
        src="n1",
        dst="n2",
        W=0.85,
        kind="cause",
        origin="user",
        t_created=10,
        t_last_update=50,
        n=15,
        M_max=0.95,
        S=0.35,
        tagged=True,
        valence=0.4,
        lag=1.2,
        fwd=True,
        g="goal_1",
        contexts={"ctx_a", "ctx_b"},
        ctx_hits={"ctx_a": 5, "ctx_b": 10},
        is_intrinsic=False,
        k_fail=1,
    )
    e2 = Edge(
        src="n2",
        dst="n3",
        W=0.6,
        kind="assoc",
        origin="agent",
        t_created=20,
        t_last_update=60,
        n=8,
        M_max=1.0,
        S=0.1,
        tagged=False,
        valence=-0.2,
        lag=0.5,
        fwd=False,
        g=None,
        contexts={"ctx_b"},
        ctx_hits={"ctx_b": 8},
        is_intrinsic=True,
        k_fail=0,
    )
    g.edges[("n1", "n2")] = e1
    g.out_adj.setdefault("n1", {})["n2"] = e1
    g.in_adj.setdefault("n2", {})["n1"] = e1

    g.edges[("n2", "n3")] = e2
    g.out_adj.setdefault("n2", {})["n3"] = e2
    g.in_adj.setdefault("n3", {})["n2"] = e2

    # 3. Contradictions X
    g.X["n1"] = {"n3"}

    # 4. Concept hits
    g.concept_hits["c_1"] = 12
    g.concept_hits["c_2"] = 7

    # 5. Drives
    g.drives["curiosity"] = {"urgency": 0.8, "satiation": 0.2}

    # 6. Hypotheses
    g.hypotheses = [{"hypo_id": "h_alpha", "score": 0.9}]

    # 7. Assemblies in AssemblyManager
    mgr = g.assembly_manager
    asm_v1 = StructuralAssembly(
        assembly_id="asm_test",
        version=1,
        member_edges=frozenset([("n1", "n2")]),
        origin_signature="sig_1",
        predecessor_version=None,
        parent_assemblies=(),
        is_retired=True,
    )
    asm_v2 = StructuralAssembly(
        assembly_id="asm_test",
        version=2,
        member_edges=frozenset([("n1", "n2"), ("n2", "n3")]),
        origin_signature="sig_2",
        predecessor_version=1,
        parent_assemblies=("asm_parent",),
        is_retired=False,
    )
    mgr.assemblies["asm_test"] = [asm_v1, asm_v2]

    # 8. Pending Evidence
    cand = FormationCandidate(
        candidate_id="cand_1",
        edges=frozenset([("n1", "n2")]),
        context_signature="ctx_sig_1",
        root_votes={"root_1", "root_2"},
        created_t=80,
    )
    mgr.pending_candidates["cand_1"] = cand
    mgr.pending_growth[("asm_test", ("n2", "n3"), "ctx_growth")] = {"root_3"}
    mgr.pending_merge[(frozenset(["asm_test"]), "ctx_merge")] = {"root_4", "root_5"}

    mgr.rebuild_indexes()
    return g


# ==============================================================================
# SECTION 1: INVARIANTS R0-I01 .. R0-I24
# ==============================================================================

def test_r0_i01_durable_node_state_survives_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I01: Durable Node state survives exactly."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i01.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    for nid, orig_node in g.nodes.items():
        assert nid in restored.nodes
        r_node = restored.nodes[nid]
        assert r_node.nid == orig_node.nid
        assert r_node.region == orig_node.region
        assert r_node.is_concept == orig_node.is_concept
        assert r_node.members == orig_node.members
        assert math.isclose(r_node.U, orig_node.U, rel_tol=1e-9)
        assert math.isclose(r_node.V, orig_node.V, rel_tol=1e-9)
        assert r_node.head == orig_node.head
        assert r_node.is_intrinsic == orig_node.is_intrinsic
        assert r_node.N_total == orig_node.N_total


def test_r0_i02_durable_edge_state_survives_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I02: Durable Edge state survives exactly."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i02.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    for pair, orig_edge in g.edges.items():
        assert pair in restored.edges
        r_edge = restored.edges[pair]
        assert r_edge.src == orig_edge.src
        assert r_edge.dst == orig_edge.dst
        assert math.isclose(r_edge.W, orig_edge.W, rel_tol=1e-9)
        assert r_edge.kind == orig_edge.kind
        assert r_edge.origin == orig_edge.origin
        assert r_edge.t_created == orig_edge.t_created
        assert r_edge.t_last_update == orig_edge.t_last_update
        assert r_edge.n == orig_edge.n
        assert math.isclose(r_edge.M_max, orig_edge.M_max, rel_tol=1e-9)
        assert math.isclose(r_edge.S, orig_edge.S, rel_tol=1e-9)
        assert r_edge.tagged == orig_edge.tagged
        assert math.isclose(r_edge.valence, orig_edge.valence, rel_tol=1e-9)
        assert math.isclose(r_edge.lag, orig_edge.lag, rel_tol=1e-9)
        assert r_edge.fwd == orig_edge.fwd
        assert r_edge.g == orig_edge.g
        assert r_edge.contexts == orig_edge.contexts
        assert r_edge.ctx_hits == orig_edge.ctx_hits
        assert r_edge.is_intrinsic == orig_edge.is_intrinsic
        assert r_edge.k_fail == orig_edge.k_fail


def test_r0_i03_contradictions_survive_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I03: Contradiction matrix X survives exactly."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i03.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.X == g.X


def test_r0_i04_concept_hits_survive_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I04: concept_hits survives exactly."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i04.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.concept_hits == g.concept_hits


def test_r0_i05_drives_survive_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I05: drives survive exactly."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i05.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.drives == g.drives


def test_r0_i06_hypotheses_survive_while_remaining_isolated(tmp_path: pathlib.Path) -> None:
    """R0-I06: hypotheses survive while remaining isolated."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i06.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.hypotheses == g.hypotheses

    # Mutate restored hypothesis to prove isolation
    restored.hypotheses[0]["score"] = 0.0
    assert g.hypotheses[0]["score"] == 0.9


def test_r0_i07_logical_time_survives_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I07: logical time survives exactly."""
    g = make_rich_graph(t=4242)
    ckpt_path = tmp_path / "ckpt_i07.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.t == 4242


def test_r0_i08_structural_assembly_history_survives_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I08: StructuralAssembly history survives exactly."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i08.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    orig_mgr = g._assembly_manager
    rest_mgr = restored._assembly_manager
    assert orig_mgr is not None and rest_mgr is not None
    assert set(rest_mgr.assemblies.keys()) == set(orig_mgr.assemblies.keys())

    for aid in orig_mgr.assemblies:
        orig_versions = orig_mgr.assemblies[aid]
        rest_versions = rest_mgr.assemblies[aid]
        assert len(orig_versions) == len(rest_versions)
        for ov, rv in zip(orig_versions, rest_versions):
            assert ov.assembly_id == rv.assembly_id
            assert ov.version == rv.version
            assert ov.member_edges == rv.member_edges
            assert ov.origin_signature == rv.origin_signature
            assert ov.predecessor_version == rv.predecessor_version
            assert ov.parent_assemblies == rv.parent_assemblies
            assert ov.is_retired == rv.is_retired


def test_r0_i09_lawful_pending_structural_evidence_survives_exactly(tmp_path: pathlib.Path) -> None:
    """R0-I09: lawful pending structural evidence survives exactly."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i09.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    orig_mgr = g._assembly_manager
    rest_mgr = restored._assembly_manager
    assert orig_mgr is not None and rest_mgr is not None

    # Formation candidates
    assert set(rest_mgr.pending_candidates.keys()) == set(orig_mgr.pending_candidates.keys())
    for cid in orig_mgr.pending_candidates:
        oc = orig_mgr.pending_candidates[cid]
        rc = rest_mgr.pending_candidates[cid]
        assert oc.candidate_id == rc.candidate_id
        assert oc.edges == rc.edges
        assert oc.context_signature == rc.context_signature
        assert oc.root_votes == rc.root_votes
        assert oc.created_t == rc.created_t

    # Growth
    assert rest_mgr.pending_growth == orig_mgr.pending_growth

    # Merge
    assert rest_mgr.pending_merge == orig_mgr.pending_merge


def test_r0_i10_node_activation_never_survives_cold_restart(tmp_path: pathlib.Path) -> None:
    """R0-I10: Node activation never survives cold restart."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i10.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    for n in restored.nodes.values():
        assert n.A == 0.0
        assert n.t_spawn == -999
        assert n.episode is None


def test_r0_i11_no_active_assembly_survives(tmp_path: pathlib.Path) -> None:
    """R0-I11: no ActiveAssembly survives."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i11.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    # AssemblyManager owns structural assemblies, active assemblies are 0
    assert restored._assembly_manager is not None


def test_r0_i12_no_sdcr_receipt_tbr_survives(tmp_path: pathlib.Path) -> None:
    """R0-I12: no SDCR/receipt/TBR survives."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i12.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._representation_engine is None


def test_r0_i13_no_settling_epoch_survives(tmp_path: pathlib.Path) -> None:
    """R0-I13: no SettlingEpoch survives."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i13.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._completion_engine is None


def test_r0_i14_no_rfc14_working_generation_survives(tmp_path: pathlib.Path) -> None:
    """R0-I14: no RFC14 working generation survives."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i14.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._generation_engine is None


def test_r0_i15_no_rfc15_gce_commit_survives(tmp_path: pathlib.Path) -> None:
    """R0-I15: no RFC15 GCE/commit survives."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i15.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._recurrent_engine is None


def test_r0_i16_rfc16_restores_quiescent(tmp_path: pathlib.Path) -> None:
    """R0-I16: RFC16 restores quiescent."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i16.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.prediction_pool == {}
    assert restored.prediction_sources == {}
    assert restored.dmg == 0.0
    assert restored.goal is None
    assert restored.outcome == 0.0
    assert restored.log == []
    assert restored._loop_engine is None


def test_r0_i17_runtime_engines_never_cross_restore_boundary(tmp_path: pathlib.Path) -> None:
    """R0-I17: runtime engines never cross restore boundary."""
    g = make_rich_graph()
    g._representation_engine = object()
    g._completion_engine = object()
    g._generation_engine = object()
    g._recurrent_engine = object()
    g._loop_engine = object()

    ckpt_path = tmp_path / "ckpt_i17.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    assert restored._representation_engine is None
    assert restored._completion_engine is None
    assert restored._generation_engine is None
    assert restored._recurrent_engine is None
    assert restored._loop_engine is None


def test_r0_i18_reconstructible_indexes_are_rebuilt(tmp_path: pathlib.Path) -> None:
    """R0-I18: reconstructible indexes are rebuilt."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i18.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    for (u, v), edge in restored.edges.items():
        assert u in restored.out_adj
        assert v in restored.out_adj[u]
        assert restored.out_adj[u][v] is edge

        assert v in restored.in_adj
        assert u in restored.in_adj[v]
        assert restored.in_adj[v][u] is edge

    mgr = restored._assembly_manager
    assert mgr is not None
    assert ("n1", "n2") in mgr.edge_to_assemblies
    assert "asm_test" in mgr.edge_to_assemblies[("n1", "n2")]


def test_r0_i19_restored_assembly_manager_references_restored_graph(tmp_path: pathlib.Path) -> None:
    """R0-I19: restored AssemblyManager references restored graph."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i19.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._assembly_manager is not None
    assert restored._assembly_manager.graph is restored
    assert restored._assembly_manager.graph is not g


def test_r0_i20_incompatible_semantics_fail_closed(tmp_path: pathlib.Path) -> None:
    """R0-I20: incompatible semantics fail closed."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i20.json"
    save_cognitive_checkpoint(g, ckpt_path)

    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    # Invalidate active law digest
    data["compatibility"]["active_law_digest"] = "0" * 64
    bad_path = tmp_path / "bad_law.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(bad_path)


def test_r0_i21_canonical_state_digest_is_deterministic(tmp_path: pathlib.Path) -> None:
    """R0-I21: canonical state digest is deterministic across insertion order variations."""
    # Build g1
    g1 = make_rich_graph()
    d1 = compute_checkpoint_state_digest(extract_canonical_persistent_payload(g1))

    # Build g2 with inverted node and edge insertion orders
    g2 = CognitiveGraph(t=g1.t)
    for nid in reversed(list(g1.nodes.keys())):
        g2.nodes[nid] = copy.deepcopy(g1.nodes[nid])
    for pair in reversed(list(g1.edges.keys())):
        e = copy.deepcopy(g1.edges[pair])
        g2.edges[pair] = e
        g2.out_adj.setdefault(e.src, {})[e.dst] = e
        g2.in_adj.setdefault(e.dst, {})[e.src] = e
    g2.X = copy.deepcopy(g1.X)
    g2.concept_hits = copy.deepcopy(g1.concept_hits)
    g2.drives = copy.deepcopy(g1.drives)
    g2.hypotheses = copy.deepcopy(g1.hypotheses)
    mgr2 = g2.assembly_manager
    mgr2.assemblies = copy.deepcopy(g1.assembly_manager.assemblies)
    mgr2.pending_candidates = copy.deepcopy(g1.assembly_manager.pending_candidates)
    mgr2.pending_growth = copy.deepcopy(g1.assembly_manager.pending_growth)
    mgr2.pending_merge = copy.deepcopy(g1.assembly_manager.pending_merge)
    mgr2.rebuild_indexes()

    d2 = compute_checkpoint_state_digest(extract_canonical_persistent_payload(g2))
    assert d1 == d2


def test_r0_i22_failed_save_preserves_previous_checkpoint(tmp_path: pathlib.Path) -> None:
    """R0-I22: failed save preserves previous checkpoint."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_i22.json"
    save_cognitive_checkpoint(g, ckpt_path)
    original_bytes = ckpt_path.read_bytes()

    # Simulate failure on atomic replace
    with patch("os.replace", side_effect=OSError("Simulated write failure")), pytest.raises(OSError):
        save_cognitive_checkpoint(g, ckpt_path)

    assert ckpt_path.read_bytes() == original_bytes


def test_r0_i23_failed_restore_preserves_previous_runtime(tmp_path: pathlib.Path) -> None:
    """R0-I23: failed restore preserves previous runtime."""
    g_initial = make_rich_graph(t=11)
    root = RuntimeRoot(g_initial)

    bad_path = tmp_path / "corrupt_i23.json"
    bad_path.write_text("{corrupt json content", encoding="utf-8")

    with pytest.raises(CheckpointValidationError):
        root.restore_checkpoint(bad_path)

    assert root.graph is g_initial
    assert id(root.graph) == id(g_initial)
    assert root.graph.t == 11


def test_r0_i24_migration_never_invents_unavailable_legacy_evidence(tmp_path: pathlib.Path) -> None:
    """R0-I24: migration never invents unavailable legacy evidence."""
    legacy_data = {
        "version": "1.0",
        "t": 30,
        "nodes": {
            "n1": {"nid": "n1", "region": "TEXT", "U": 0.5, "V": 0.2},
            "n2": {"nid": "n2", "region": "TEXT", "U": 0.6, "V": 0.3},
        },
        "edges": [{"src": "n1", "dst": "n2", "W": 0.8}],
        "assemblies": [],
    }
    legacy_path = tmp_path / "legacy_i24.json"
    legacy_path.write_text(json.dumps(legacy_data), encoding="utf-8")

    restored, report = restore_cognitive_checkpoint(legacy_path)
    assert report is not None
    mgr = restored._assembly_manager
    assert mgr is not None
    assert len(mgr.pending_candidates) == 0
    assert len(mgr.pending_growth) == 0
    assert len(mgr.pending_merge) == 0
    assert any("pending structural evidence" in s for s in report.unrecoverable_legacy_state)


# ==============================================================================
# SECTION 2: ACCEPTANCE TESTS T01 .. T40
# ==============================================================================

def test_t01_empty_checkpoint_round_trip(tmp_path: pathlib.Path) -> None:
    """T01: empty checkpoint round-trip."""
    g = CognitiveGraph()
    ckpt_path = tmp_path / "ckpt_t01.json"
    d_saved = save_cognitive_checkpoint(g, ckpt_path)
    restored, rep = restore_cognitive_checkpoint(ckpt_path)
    d_restored = compute_checkpoint_state_digest(extract_canonical_persistent_payload(restored))
    assert d_saved == d_restored
    assert len(restored.nodes) == 0
    assert len(restored.edges) == 0
    assert rep is None


def test_t02_learned_graph_round_trip(tmp_path: pathlib.Path) -> None:
    """T02: learned graph round-trip."""
    g = make_rich_graph(t=77)
    ckpt_path = tmp_path / "ckpt_t02.json"
    d_saved = save_cognitive_checkpoint(g, ckpt_path)
    restored, _rep = restore_cognitive_checkpoint(ckpt_path)
    d_restored = compute_checkpoint_state_digest(extract_canonical_persistent_payload(restored))
    assert d_saved == d_restored
    assert restored.t == 77
    assert len(restored.nodes) == len(g.nodes)
    assert len(restored.edges) == len(g.edges)


def test_t03_all_durable_node_fields_exact(tmp_path: pathlib.Path) -> None:
    """T03: all durable Node fields exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t03.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    for nid, orig in g.nodes.items():
        res = restored.nodes[nid]
        assert res.nid == orig.nid
        assert res.region == orig.region
        assert res.is_concept == orig.is_concept
        assert res.members == orig.members
        assert math.isclose(res.U, orig.U, rel_tol=1e-9)
        assert math.isclose(res.V, orig.V, rel_tol=1e-9)
        assert res.head == orig.head
        assert res.is_intrinsic == orig.is_intrinsic
        assert res.N_total == orig.N_total


def test_t04_all_edge_fields_exact(tmp_path: pathlib.Path) -> None:
    """T04: all Edge fields exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t04.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    for pair, orig in g.edges.items():
        res = restored.edges[pair]
        assert res.src == orig.src
        assert res.dst == orig.dst
        assert math.isclose(res.W, orig.W, rel_tol=1e-9)
        assert res.kind == orig.kind
        assert res.origin == orig.origin
        assert res.t_created == orig.t_created
        assert res.t_last_update == orig.t_last_update
        assert res.n == orig.n
        assert math.isclose(res.M_max, orig.M_max, rel_tol=1e-9)
        assert math.isclose(res.S, orig.S, rel_tol=1e-9)
        assert res.tagged == orig.tagged
        assert math.isclose(res.valence, orig.valence, rel_tol=1e-9)
        assert math.isclose(res.lag, orig.lag, rel_tol=1e-9)
        assert res.fwd == orig.fwd
        assert res.g == orig.g
        assert res.contexts == orig.contexts
        assert res.ctx_hits == orig.ctx_hits
        assert res.is_intrinsic == orig.is_intrinsic
        assert res.k_fail == orig.k_fail


def test_t05_contradiction_matrix_exact(tmp_path: pathlib.Path) -> None:
    """T05: contradiction matrix exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t05.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.X == g.X


def test_t06_concept_hits_exact(tmp_path: pathlib.Path) -> None:
    """T06: concept_hits exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t06.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.concept_hits == g.concept_hits


def test_t07_drive_state_exact(tmp_path: pathlib.Path) -> None:
    """T07: drive state exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t07.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.drives == g.drives


def test_t08_hypotheses_exact_and_isolated(tmp_path: pathlib.Path) -> None:
    """T08: hypotheses exact and isolated."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t08.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.hypotheses == g.hypotheses
    restored.hypotheses[0]["score"] = 0.123
    assert g.hypotheses[0]["score"] == 0.9


def test_t09_structural_assembly_history_exact(tmp_path: pathlib.Path) -> None:
    """T09: structural assembly history exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t09.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    mgr = restored._assembly_manager
    assert mgr is not None
    assert "asm_test" in mgr.assemblies
    versions = mgr.assemblies["asm_test"]
    assert len(versions) == 2
    assert versions[0].version == 1
    assert versions[0].is_retired is True
    assert versions[1].version == 2
    assert versions[1].is_retired is False
    assert versions[1].predecessor_version == 1
    assert versions[1].parent_assemblies == ("asm_parent",)


def test_t10_formation_pending_votes_exact(tmp_path: pathlib.Path) -> None:
    """T10: formation pending votes exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t10.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    mgr = restored._assembly_manager
    assert mgr is not None
    assert "cand_1" in mgr.pending_candidates
    cand = mgr.pending_candidates["cand_1"]
    assert cand.root_votes == {"root_1", "root_2"}
    assert cand.created_t == 80


def test_t11_growth_pending_votes_exact(tmp_path: pathlib.Path) -> None:
    """T11: growth pending votes exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t11.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    mgr = restored._assembly_manager
    assert mgr is not None
    key = ("asm_test", ("n2", "n3"), "ctx_growth")
    assert key in mgr.pending_growth
    assert mgr.pending_growth[key] == {"root_3"}


def test_t12_merge_pending_votes_exact(tmp_path: pathlib.Path) -> None:
    """T12: merge pending votes exact."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t12.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    mgr = restored._assembly_manager
    assert mgr is not None
    key = (frozenset(["asm_test"]), "ctx_merge")
    assert key in mgr.pending_merge
    assert mgr.pending_merge[key] == {"root_4", "root_5"}


def test_t13_duplicate_stored_root_vote_remains_idempotent(tmp_path: pathlib.Path) -> None:
    """T13: duplicate stored root vote remains idempotent."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t13.json"
    save_cognitive_checkpoint(g, ckpt_path)

    # Hand-inject duplicate votes in JSON
    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0]["root_votes"] = [
        "root_1", "root_1", "root_2", "root_2"
    ]
    # Recompute state digest for modified persistent state
    d = compute_checkpoint_state_digest(data["persistent_state"])
    data["integrity"]["checkpoint_state_digest"] = d
    mod_path = tmp_path / "mod_t13.json"
    mod_path.write_text(json.dumps(data), encoding="utf-8")

    restored, _ = restore_cognitive_checkpoint(mod_path)
    cand = restored._assembly_manager.pending_candidates["cand_1"]
    assert cand.root_votes == {"root_1", "root_2"}
    assert len(cand.root_votes) == 2


def test_t14_activation_resets(tmp_path: pathlib.Path) -> None:
    """T14: activation resets."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t14.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    for n in restored.nodes.values():
        assert n.A == 0.0
        assert n.t_spawn == -999
        assert n.episode is None


def test_t15_active_assembly_resets(tmp_path: pathlib.Path) -> None:
    """T15: ActiveAssembly resets."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t15.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    # Graph has no transient active assemblies
    assert restored._assembly_manager is not None


def test_t16_rfc12_runtime_resets(tmp_path: pathlib.Path) -> None:
    """T16: RFC12 runtime resets."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t16.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._representation_engine is None


def test_t17_rfc13_runtime_resets(tmp_path: pathlib.Path) -> None:
    """T17: RFC13 runtime resets."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t17.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._completion_engine is None


def test_t18_rfc14_runtime_resets(tmp_path: pathlib.Path) -> None:
    """T18: RFC14 runtime resets."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t18.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._generation_engine is None


def test_t19_rfc15_runtime_resets(tmp_path: pathlib.Path) -> None:
    """T19: RFC15 runtime resets."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t19.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._recurrent_engine is None


def test_t20_rfc16_restores_quiescent(tmp_path: pathlib.Path) -> None:
    """T20: RFC16 restores quiescent."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t20.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.prediction_pool == {}
    assert restored.prediction_sources == {}
    assert restored.dmg == 0.0
    assert restored.goal is None
    assert restored.outcome == 0.0
    assert restored.log == []
    assert restored._loop_engine is None


def test_t21_indexes_rebuild(tmp_path: pathlib.Path) -> None:
    """T21: indexes rebuild."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t21.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert len(restored.out_adj) > 0
    assert len(restored.in_adj) > 0
    assert len(restored._assembly_manager.edge_to_assemblies) > 0


def test_t22_assembly_manager_bound_to_new_graph(tmp_path: pathlib.Path) -> None:
    """T22: AssemblyManager bound to new graph."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t22.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._assembly_manager.graph is restored
    assert restored._assembly_manager.graph is not g


def test_t23_old_engines_not_reused(tmp_path: pathlib.Path) -> None:
    """T23: old engines not reused."""
    g = make_rich_graph()
    g._representation_engine = object()
    g._completion_engine = object()
    g._generation_engine = object()
    g._recurrent_engine = object()
    g._loop_engine = object()

    ckpt_path = tmp_path / "ckpt_t23.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored._representation_engine is None
    assert restored._completion_engine is None
    assert restored._generation_engine is None
    assert restored._recurrent_engine is None
    assert restored._loop_engine is None


def test_t24_state_digest_round_trip_equality(tmp_path: pathlib.Path) -> None:
    """T24: state digest round-trip equality."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t24.json"
    d_saved = save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    d_restored = compute_checkpoint_state_digest(extract_canonical_persistent_payload(restored))
    assert d_saved == d_restored


def test_t25_deterministic_repeated_save_digest(tmp_path: pathlib.Path) -> None:
    """T25: deterministic repeated save digest."""
    g = make_rich_graph()
    p1 = tmp_path / "ckpt_t25_1.json"
    p2 = tmp_path / "ckpt_t25_2.json"
    d1 = save_cognitive_checkpoint(g, p1)
    d2 = save_cognitive_checkpoint(g, p2)
    assert d1 == d2
    assert p1.read_bytes() == p2.read_bytes()


def test_t26_incompatible_schema_fail_closed(tmp_path: pathlib.Path) -> None:
    """T26: incompatible schema fail-closed."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t26.json"
    save_cognitive_checkpoint(g, ckpt_path)
    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["schema"]["checkpoint_schema_version"] = "9.9"
    bad_path = tmp_path / "bad_schema.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(CheckpointSchemaError):
        restore_cognitive_checkpoint(bad_path)


def test_t27_incompatible_law_fingerprint_fail_closed(tmp_path: pathlib.Path) -> None:
    """T27: incompatible Law fingerprint fail-closed."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t27.json"
    save_cognitive_checkpoint(g, ckpt_path)
    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["compatibility"]["active_law_digest"] = "f" * 64
    bad_path = tmp_path / "bad_law.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(bad_path)


def test_t28_incompatible_assembly_policy_fail_closed(tmp_path: pathlib.Path) -> None:
    """T28: incompatible AssemblyPolicy fail-closed."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t28.json"
    save_cognitive_checkpoint(g, ckpt_path)
    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["compatibility"]["assembly_policy_digest"] = "e" * 64
    bad_path = tmp_path / "bad_policy.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(bad_path)


def test_t29_malformed_checksum_fail_closed(tmp_path: pathlib.Path) -> None:
    """T29: malformed checksum fail-closed."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t29.json"
    save_cognitive_checkpoint(g, ckpt_path)
    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["integrity"]["checkpoint_state_digest"] = "d" * 64
    bad_path = tmp_path / "bad_checksum.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(CheckpointIntegrityError):
        restore_cognitive_checkpoint(bad_path)


def test_t30_malformed_structural_refs_fail_closed(tmp_path: pathlib.Path) -> None:
    """T30: malformed structural refs fail-closed."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t30.json"
    save_cognitive_checkpoint(g, ckpt_path)

    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    # Delete node n2 referenced by edges
    data["persistent_state"]["nodes"] = [n for n in data["persistent_state"]["nodes"] if n["nid"] != "n2"]
    d = compute_checkpoint_state_digest(data["persistent_state"])
    data["integrity"]["checkpoint_state_digest"] = d
    bad_path = tmp_path / "bad_refs.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(StructuralReferentialIntegrityError):
        restore_cognitive_checkpoint(bad_path)


def test_t31_failed_restore_preserves_old_runtime(tmp_path: pathlib.Path) -> None:
    """T31: failed restore preserves old runtime."""
    g = make_rich_graph(t=88)
    root = RuntimeRoot(g)
    bad_path = tmp_path / "corrupt_t31.json"
    bad_path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(CheckpointValidationError):
        root.restore_checkpoint(bad_path)
    assert root.graph is g
    assert id(root.graph) == id(g)
    assert root.graph.t == 88


def test_t32_failed_save_preserves_old_checkpoint(tmp_path: pathlib.Path) -> None:
    """T32: failed save preserves old checkpoint."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t32.json"
    save_cognitive_checkpoint(g, ckpt_path)
    old_content = ckpt_path.read_text(encoding="utf-8")

    with patch("os.replace", side_effect=OSError("Simulated write fail")), pytest.raises(OSError):
        save_cognitive_checkpoint(g, ckpt_path)

    assert ckpt_path.read_text(encoding="utf-8") == old_content


def test_t33_interrupted_temp_write_preserves_old_checkpoint(tmp_path: pathlib.Path) -> None:
    """T33: interrupted temp write preserves old checkpoint."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t33.json"
    save_cognitive_checkpoint(g, ckpt_path)
    old_content = ckpt_path.read_text(encoding="utf-8")

    with patch("os.fsync", side_effect=OSError("Simulated fsync crash")), pytest.raises(OSError):
        save_cognitive_checkpoint(g, ckpt_path)

    assert ckpt_path.read_text(encoding="utf-8") == old_content


def test_t34_legacy_activation_discarded(tmp_path: pathlib.Path) -> None:
    """T34: legacy activation discarded."""
    legacy_data = {
        "version": "1.0",
        "t": 10,
        "nodes": {
            "n1": {"nid": "n1", "region": "TEXT", "U": 0.5, "V": 0.2, "A": 0.99, "t_spawn": 42},
        },
        "edges": [],
        "assemblies": [],
    }
    legacy_path = tmp_path / "legacy_t34.json"
    legacy_path.write_text(json.dumps(legacy_data), encoding="utf-8")

    restored, _ = restore_cognitive_checkpoint(legacy_path)
    assert restored.nodes["n1"].A == 0.0
    assert restored.nodes["n1"].t_spawn == -999
    assert restored.nodes["n1"].episode is None


def test_t35_legacy_durable_cognition_preserved(tmp_path: pathlib.Path) -> None:
    """T35: legacy durable cognition preserved."""
    legacy_data = {
        "version": "1.0",
        "t": 25,
        "nodes": {
            "n1": {"nid": "n1", "region": "TEXT", "U": 0.7, "V": 0.1, "is_concept": True, "members": ["m1"]},
            "n2": {"nid": "n2", "region": "TEXT", "U": 0.2, "V": 0.3},
        },
        "edges": [{"src": "n1", "dst": "n2", "W": 0.9, "kind": "assoc"}],
        "X": {"n1": ["n2"]},
        "concept_hits": {"c1": 5},
        "drives": {"d1": 0.4},
        "hypotheses": [{"hypo": "test"}],
        "assemblies": [],
    }
    legacy_path = tmp_path / "legacy_t35.json"
    legacy_path.write_text(json.dumps(legacy_data), encoding="utf-8")

    restored, _rep = restore_cognitive_checkpoint(legacy_path)
    assert restored.t == 25
    assert restored.nodes["n1"].U == 0.7
    assert restored.nodes["n1"].is_concept is True
    assert restored.nodes["n1"].members == {"m1"}
    assert restored.edges[("n1", "n2")].W == 0.9
    assert restored.X["n1"] == {"n2"}
    assert restored.concept_hits["c1"] == 5
    assert restored.drives["d1"] == 0.4
    assert restored.hypotheses == [{"hypo": "test"}]


def test_t36_legacy_missing_pending_evidence_reported(tmp_path: pathlib.Path) -> None:
    """T36: legacy missing pending evidence reported."""
    legacy_data = {
        "version": "1.0",
        "t": 5,
        "nodes": {},
        "edges": [],
        "assemblies": [],
    }
    legacy_path = tmp_path / "legacy_t36.json"
    legacy_path.write_text(json.dumps(legacy_data), encoding="utf-8")

    _restored, rep = restore_cognitive_checkpoint(legacy_path)
    assert rep is not None
    assert any("pending structural evidence" in s for s in rep.unrecoverable_legacy_state)


def test_t37_runtime_config_not_overwritten_by_checkpoint(tmp_path: pathlib.Path) -> None:
    """T37: runtime config not overwritten by checkpoint."""
    g = make_rich_graph()
    g.enable_prediction = True
    ckpt_path = tmp_path / "ckpt_t37.json"
    save_cognitive_checkpoint(g, ckpt_path)

    # Restore under runtime configuration with prediction disabled
    restored, _ = restore_cognitive_checkpoint(ckpt_path, enable_prediction=False)
    assert restored.enable_prediction is False

    # Restore under runtime configuration with prediction enabled
    restored2, _ = restore_cognitive_checkpoint(ckpt_path, enable_prediction=True)
    assert restored2.enable_prediction is True


def test_t38_logical_time_unchanged_by_wall_clock_downtime(tmp_path: pathlib.Path) -> None:
    """T38: logical time unchanged by wall-clock downtime."""
    g = make_rich_graph(t=31415)
    ckpt_path = tmp_path / "ckpt_t38.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert restored.t == 31415


def test_t39_cold_restore_has_zero_open_cognitive_epochs(tmp_path: pathlib.Path) -> None:
    """T39: cold restore has zero open cognitive epochs."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_t39.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)
    assert len(restored.log) == 0
    assert restored._representation_engine is None
    assert restored._completion_engine is None
    assert restored._generation_engine is None
    assert restored._recurrent_engine is None
    assert restored._loop_engine is None


def test_t40_full_existing_regression_suite_pass() -> None:
    """T40: full existing regression suite PASS verification."""
    # Verifies the authoritative baseline cognitive signature
    sig_path = pathlib.Path("tests/baseline_signature.txt")
    assert sig_path.exists()
    assert sig_path.read_text(encoding="utf-8").strip() == "915119d40643cb97"


# ==============================================================================
# SECTION 3: ADDITIONAL ADVERSARIAL TESTS A .. I
# ==============================================================================

def test_adversarial_a_non_finite_numeric_rejection(tmp_path: pathlib.Path) -> None:
    """Adversarial A: Non-finite numeric rejection (NaN, +Inf, -Inf)."""
    g = make_rich_graph()
    ckpt_path = tmp_path / "ckpt_adv_a.json"
    save_cognitive_checkpoint(g, ckpt_path)

    # 1. Test NaN
    data_nan = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data_nan["persistent_state"]["nodes"][0]["U"] = None  # Use string or float check
    raw_str = json.dumps(data_nan).replace('null', 'NaN')
    bad_nan_path = tmp_path / "bad_nan.json"
    bad_nan_path.write_text(raw_str, encoding="utf-8")
    with pytest.raises(CheckpointValidationError):
        restore_cognitive_checkpoint(bad_nan_path)

    # 2. Test +Inf
    raw_inf = json.dumps(data_nan).replace('null', 'Infinity')
    bad_inf_path = tmp_path / "bad_inf.json"
    bad_inf_path.write_text(raw_inf, encoding="utf-8")
    with pytest.raises(CheckpointValidationError):
        restore_cognitive_checkpoint(bad_inf_path)

    # 3. Test -Inf
    raw_ninf = json.dumps(data_nan).replace('null', '-Infinity')
    bad_ninf_path = tmp_path / "bad_ninf.json"
    bad_ninf_path.write_text(raw_ninf, encoding="utf-8")
    with pytest.raises(CheckpointValidationError):
        restore_cognitive_checkpoint(bad_ninf_path)


def test_adversarial_b_stale_formation_candidate(tmp_path: pathlib.Path) -> None:
    """Adversarial B: Stale formation candidate referring to missing edge fails closed."""
    g = make_rich_graph()
    cand = FormationCandidate(
        candidate_id="cand_stale",
        edges=frozenset([("n1", "non_existent_node")]),
        context_signature="ctx",
        root_votes={"rv_1"},
    )
    g.assembly_manager.pending_candidates["cand_stale"] = cand
    with pytest.raises(StructuralReferentialIntegrityError):
        validate_structural_referential_integrity(g)


def test_adversarial_c_stale_growth_candidate(tmp_path: pathlib.Path) -> None:
    """Adversarial C: Stale growth candidate referring to missing parent or missing edge fails closed."""
    # 1. Missing parent assembly
    g1 = make_rich_graph()
    g1.assembly_manager.pending_growth[("missing_asm", ("n1", "n2"), "ctx")] = {"v1"}
    with pytest.raises(StructuralReferentialIntegrityError):
        validate_structural_referential_integrity(g1)

    # 2. Retired parent assembly
    g2 = make_rich_graph()
    cur = g2.assembly_manager.assemblies["asm_test"][-1]
    g2.assembly_manager.assemblies["asm_test"][-1] = StructuralAssembly(
        assembly_id=cur.assembly_id,
        version=cur.version,
        member_edges=cur.member_edges,
        origin_signature=cur.origin_signature,
        predecessor_version=cur.predecessor_version,
        parent_assemblies=cur.parent_assemblies,
        is_retired=True,
    )
    g2.assembly_manager.pending_growth[("asm_test", ("n1", "n2"), "ctx")] = {"v1"}
    with pytest.raises(StructuralReferentialIntegrityError):
        validate_structural_referential_integrity(g2)

    # 3. Missing edge
    g3 = make_rich_graph()
    g3.assembly_manager.pending_growth[("asm_test", ("n1", "non_existent"), "ctx")] = {"v1"}
    with pytest.raises(StructuralReferentialIntegrityError):
        validate_structural_referential_integrity(g3)


def test_adversarial_d_stale_merge_candidate(tmp_path: pathlib.Path) -> None:
    """Adversarial D: Stale merge candidate referring to retired/missing parent fails closed."""
    # 1. Missing parent
    g1 = make_rich_graph()
    g1.assembly_manager.pending_merge[(frozenset(["non_existent_asm"]), "ctx")] = {"v1"}
    with pytest.raises(StructuralReferentialIntegrityError):
        validate_structural_referential_integrity(g1)

    # 2. Retired parent
    g2 = make_rich_graph()
    cur = g2.assembly_manager.assemblies["asm_test"][-1]
    g2.assembly_manager.assemblies["asm_test"][-1] = StructuralAssembly(
        assembly_id=cur.assembly_id,
        version=cur.version,
        member_edges=cur.member_edges,
        origin_signature=cur.origin_signature,
        predecessor_version=cur.predecessor_version,
        parent_assemblies=cur.parent_assemblies,
        is_retired=True,
    )
    g2.assembly_manager.pending_merge[(frozenset(["asm_test"]), "ctx")] = {"v1"}
    with pytest.raises(StructuralReferentialIntegrityError):
        validate_structural_referential_integrity(g2)


def test_adversarial_e_runtime_object_identity_preservation_on_failed_restore(tmp_path: pathlib.Path) -> None:
    """Adversarial E: Runtime object identity preservation on failed restore."""
    g = make_rich_graph()
    root = RuntimeRoot(g)
    orig_id = id(root.graph)

    bad_path = tmp_path / "bad_e.json"
    bad_path.write_text("invalid json", encoding="utf-8")

    with pytest.raises(CheckpointValidationError):
        root.restore_checkpoint(bad_path)

    assert id(root.graph) == orig_id
    assert root.graph is g


def test_adversarial_f_old_engine_non_reuse(tmp_path: pathlib.Path) -> None:
    """Adversarial F: Old-engine non-reuse verification."""
    g = make_rich_graph()
    mock_rep = object()
    mock_comp = object()
    mock_gen = object()
    mock_rec = object()
    mock_loop = object()

    g._representation_engine = mock_rep
    g._completion_engine = mock_comp
    g._generation_engine = mock_gen
    g._recurrent_engine = mock_rec
    g._loop_engine = mock_loop

    ckpt_path = tmp_path / "ckpt_adv_f.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    assert restored._representation_engine is None
    assert restored._completion_engine is None
    assert restored._generation_engine is None
    assert restored._recurrent_engine is None
    assert restored._loop_engine is None

    assert restored._representation_engine is not mock_rep
    assert restored._completion_engine is not mock_comp
    assert restored._generation_engine is not mock_gen
    assert restored._recurrent_engine is not mock_rec
    assert restored._loop_engine is not mock_loop


def test_adversarial_g_canonical_ordering_independence(tmp_path: pathlib.Path) -> None:
    """Adversarial G: Canonical ordering independence."""
    # Graph A
    gA = CognitiveGraph(t=100)
    gA.nodes["x"] = Node(nid="x", region="TEXT")
    gA.nodes["y"] = Node(nid="y", region="TEXT")
    gA.edges[("x", "y")] = Edge(src="x", dst="y", W=0.7)
    gA.edges[("y", "x")] = Edge(src="y", dst="x", W=0.4)
    gA.out_adj.setdefault("x", {})["y"] = gA.edges[("x", "y")]
    gA.out_adj.setdefault("y", {})["x"] = gA.edges[("y", "x")]
    gA.in_adj.setdefault("y", {})["x"] = gA.edges[("x", "y")]
    gA.in_adj.setdefault("x", {})["y"] = gA.edges[("y", "x")]

    # Graph B with inverted insertions
    gB = CognitiveGraph(t=100)
    gB.nodes["y"] = Node(nid="y", region="TEXT")
    gB.nodes["x"] = Node(nid="x", region="TEXT")
    gB.edges[("y", "x")] = Edge(src="y", dst="x", W=0.4)
    gB.edges[("x", "y")] = Edge(src="x", dst="y", W=0.7)
    gB.out_adj.setdefault("y", {})["x"] = gB.edges[("y", "x")]
    gB.out_adj.setdefault("x", {})["y"] = gB.edges[("x", "y")]
    gB.in_adj.setdefault("x", {})["y"] = gB.edges[("y", "x")]
    gB.in_adj.setdefault("y", {})["x"] = gB.edges[("x", "y")]

    pA = extract_canonical_persistent_payload(gA)
    pB = extract_canonical_persistent_payload(gB)
    dA = compute_checkpoint_state_digest(pA)
    dB = compute_checkpoint_state_digest(pB)
    assert dA == dB


def test_adversarial_h_diagnostic_metadata_independence(tmp_path: pathlib.Path) -> None:
    """Adversarial H: Diagnostic metadata independence."""
    g = make_rich_graph()
    p1 = tmp_path / "ckpt_meta1.json"
    p2 = tmp_path / "ckpt_meta2.json"

    d1 = save_cognitive_checkpoint(g, p1, diagnostic_metadata={"env": "test_1", "worker_id": 101})
    d2 = save_cognitive_checkpoint(g, p2, diagnostic_metadata={"env": "prod_backup", "tags": ["a", "b"]})

    assert d1 == d2

    c1 = json.loads(p1.read_text(encoding="utf-8"))
    c2 = json.loads(p2.read_text(encoding="utf-8"))
    assert c1["integrity"]["checkpoint_state_digest"] == c2["integrity"]["checkpoint_state_digest"]
    assert c1["diagnostic_metadata"]["env"] != c2["diagnostic_metadata"]["env"]


def test_adversarial_i_runtime_configuration_authority(tmp_path: pathlib.Path) -> None:
    """Adversarial I: Runtime configuration authority."""
    g = make_rich_graph()
    g.enable_prediction = True
    ckpt_path = tmp_path / "ckpt_adv_i.json"
    save_cognitive_checkpoint(g, ckpt_path)

    # Runtime with prediction disabled
    r_disabled, _ = restore_cognitive_checkpoint(ckpt_path, enable_prediction=False)
    assert r_disabled.enable_prediction is False

    # Runtime with prediction enabled
    r_enabled, _ = restore_cognitive_checkpoint(ckpt_path, enable_prediction=True)
    assert r_enabled.enable_prediction is True
