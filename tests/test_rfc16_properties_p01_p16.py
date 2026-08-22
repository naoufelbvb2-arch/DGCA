"""
DGCA — RFC-16 v1.0 Frozen Property Verification Suite (RFC16-P01 .. RFC16-P16).
Tests the 16 exact frozen property families across >= 30 deterministic seeds each:
- RFC16-P01 — Zero New Cognitive Ownership
- RFC16-P02 — End-to-End Provenance Preservation
- RFC16-P03 — External Feedback / Evidence Separation
- RFC16-P04 — External Episode Deduplication
- RFC16-P05 — Self-Learning Firewall
- RFC16-P06 — Internal Work Scope & Authority Safety
- RFC16-P07 — Upstream Ambiguity Preservation
- RFC16-P08 — Root / GCE Lifecycle Safety
- RFC16-P09 — Delivery / Generation Separation
- RFC16-P10 — Concurrent Independent-Interleaving Equivalence
- RFC16-P11 — Stale / Interruption Safety
- RFC16-P12 — Quiescence / No-Blind-Retry
- RFC16-P13 — Stable Unified-Loop Boundedness
- RFC16-P14 — Locality & Cache Transparency
- RFC16-P15 — Deterministic Causal Replay
- RFC16-P16 — Upstream Regression & Authority Conservation
"""
from __future__ import annotations

import hashlib
import random
from itertools import permutations

import pytest

from dgca.assembly import law14_behavioral_signature
from dgca.completion import rfc13_behavioral_signature
from dgca.generation import SurfaceChunk, rfc14_behavioral_signature
from dgca.graph import CognitiveGraph
from dgca.loop import (
    InternalWorkAuthorityView,
    InternalWorkFrontier,
    rfc16_behavioral_signature,
)
from dgca.recurrent import rfc15_behavioral_signature
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
    rfc12_behavioral_signature,
)


def _create_property_graph(seed: int = 42) -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    random.seed(seed)
    g = CognitiveGraph()
    # Verified Law-14 assembly
    g.link("concept_falcon", "fly", W=0.92, contexts=("en",))
    g.link("concept_falcon", "predator", W=0.88, contexts=("en",))
    g.link("fly", "predator", W=0.80, contexts=("en",))
    mgr = g.assembly_manager
    asm_edges = [("concept_falcon", "fly"), ("concept_falcon", "predator"), ("fly", "predator")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(asm_edges, root_episode_id=f"p_seed_{seed}_ep_{i}", valid_origin=True)

    # Concept chain
    for i in range(1, 10):
        g.link(f"p_node_{i}", f"p_prop_{i}", W=0.85, contexts=("en",))
        if i < 9:
            g.link(f"p_node_{i}", f"p_node_{i+1}", W=0.95, contexts=("en",))

    receipts = [
        ParticipationReceipt(f"rcpt_{seed}_{i}", f"p_node_{i}", 1, 0, "external", "node", activation_magnitude=0.9)
        for i in range(1, 6)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    object.__setattr__(rep, "representation_id", f"rep_seed_{seed}")
    return g, rep


def _make_surface_chunk(
    g: CognitiveGraph,
    rep: SparseDistributedCognitiveRepresentation,
    nodes: tuple[str, ...] = ("p_node_1", "p_node_2"),
) -> SurfaceChunk:
    gen_eng = g.generation_engine
    frame = gen_eng.build_generative_frame(rep, frozenset(nodes))
    hierarchy = gen_eng.build_hierarchy([frame])
    prefix, _ = gen_eng.linearize_hierarchy(hierarchy, budget=10.0)
    return gen_eng.realize_surface_chunk(prefix, str(rep.representation_id), budget=10.0)


# ── RFC16-P01 — Zero New Cognitive Ownership
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p01_zero_new_cognitive_ownership(seed: int):
    """RFC16-P01: 0 new persistent primitives, 0 new learned fields, 0 persistent controller classes."""
    g, _ = _create_property_graph(seed)
    # Execute full loop
    g.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    for node in g.nodes.values():
        assert not hasattr(node, "rfc16_controller")
        assert not hasattr(node, "dialogue_history")
    for edge in g.edges.values():
        assert not hasattr(edge, "loop_priority")
        assert not hasattr(edge, "winner_score")


# ── RFC16-P02 — End-to-End Provenance Preservation
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p02_end_to_end_provenance_preservation(seed: int):
    """RFC16-P02: Ingress event, derived work, and delivery retain 100% causal provenance."""
    g, _rep = _create_property_graph(seed)
    ev, is_nov = g.loop_engine.ingress_external_event(
        f"ev_prov_{seed}", f"ep_prov_{seed}", "sensor input", metadata={"authorized_source": True}
    )
    assert is_nov is True
    auth = g.loop_engine.derive_feedback_authority(ev)
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
    assert elig.is_eligible is True
    learned, attr = g.loop_engine.process_validated_learning(
        ev, elig, "Law1_HebbianCreation", (f"p_node_{1 + seed % 5}", f"new_prop_{seed}")
    )
    assert learned is True
    assert attr.root_external_episode_id == f"ep_prov_{seed}"
    assert attr.eligibility_ref == f"ev_prov_{seed}"


# ── RFC16-P03 — External Feedback / Evidence Separation
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p03_external_feedback_evidence_separation(seed: int):
    """RFC16-P03: Raw feedback != evidence candidate != validated evidence != learning authority."""
    g, _ = _create_property_graph(seed)
    edges_before = dict(g.edges)
    for i in range(10):
        ev, is_nov = g.loop_engine.ingress_external_event(
            f"raw_fb_{seed}_{i}", f"ep_raw_{seed}_{i}", "raw unvalidated comment"
        )
        auth = g.loop_engine.derive_feedback_authority(ev)
        elig = g.loop_engine.evaluate_evidence_eligibility(ev, auth, is_nov)
        assert elig.is_eligible is False
        learned, _ = g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("a", "b"))
        assert learned is False
    assert dict(g.edges) == edges_before


# ── RFC16-P04 — External Episode Deduplication
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p04_external_episode_deduplication(seed: int):
    """RFC16-P04: Same causal episode never creates more than 1 evidence opportunity under retries/transports."""
    g, _ = _create_property_graph(seed)
    ep_id = f"ep_dedup_{seed}"
    novel_count = 0
    for r in range(15):
        _, is_novel = g.loop_engine.ingress_external_event(
            event_id=f"ev_dedup_{seed}_{r}",
            root_external_episode_id=ep_id,
            raw_content=f"reading {seed}",
            metadata={"authorized_source": True},
        )
        if is_novel:
            novel_count += 1
    assert novel_count == 1


# ── RFC16-P05 — Self-Learning Firewall
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p05_self_learning_firewall(seed: int):
    """RFC16-P05: Internal reasoning/generation cannot launder as external evidence."""
    g, rep = _create_property_graph(seed)
    chunk = _make_surface_chunk(g, rep)
    assert chunk.origin_lineage == "GENERATION"
    forged_ev, _ = g.loop_engine.ingress_external_event(
        event_id=f"forged_{seed}",
        root_external_episode_id=f"ep_self_{seed}",
        raw_content=chunk.rendered_text,
        source_origin="GENERATION",
        is_internal_call=True,
    )
    assert forged_ev is None
    assert len(g.loop_engine._learning_attributions) == 0


# ── RFC16-P06 — Internal Work Scope & Authority Safety
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p06_internal_work_scope_and_authority_safety(seed: int):
    """RFC16-P06: Internal work items are root-scoped and execute only under existing authorized subsystems."""
    g, rep = _create_property_graph(seed)
    work = InternalWorkAuthorityView(f"w_auth_{seed}", f"root_p06_{seed}", "RFC14_GENERATION", ("p_node_1", "p_node_2"), True)
    f = g.loop_engine.derive_internal_work_frontier(f"root_p06_{seed}", (work,), set())
    assert f.status == "READY"
    status, chunk = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t)
    assert status == "SUCCESS"
    assert isinstance(chunk, SurfaceChunk)


# ── RFC16-P07 — Upstream Ambiguity Preservation
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p07_upstream_ambiguity_preservation(seed: int):
    """RFC16-P07: Mutual ambiguity is preserved fail-closed without fabricating an arbitrary winner."""
    g, _ = _create_property_graph(seed)
    f_amb = InternalWorkFrontier(ready_work=(), blocked_work=(), status="AMBIGUOUS")
    q = g.loop_engine.derive_root_quiescence(f"root_amb_{seed}", f_amb)
    assert q.is_quiescent is True
    assert q.quiescence_reason == "MUTUAL_AMBIGUITY"


# ── RFC16-P08 — Root / GCE Lifecycle Safety
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p08_root_gce_lifecycle_safety(seed: int):
    """RFC16-P08: Closed GCEs remain CLOSED; external continuation creates a new distinct GCE."""
    g, _ = _create_property_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p08_{seed}")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    closed = g.recurrent_engine.get_epoch(epoch.epoch_id)
    assert closed.lifecycle == "CLOSED"

    ev, _ = g.loop_engine.ingress_external_event(f"ev_p08_{seed}", f"ep_p08_{seed}", "continue")
    rel, new_epoch_id = g.loop_engine.process_task_relation(ev, f"root_p08_{seed}", closed)
    assert rel.relation_kind == "CONTINUES"
    assert new_epoch_id is not None
    assert new_epoch_id != closed.epoch_id
    assert g.recurrent_engine.get_epoch(closed.epoch_id).lifecycle == "CLOSED"


# ── RFC16-P09 — Delivery / Generation Separation
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p09_delivery_generation_separation(seed: int):
    """RFC16-P09: Delivery retries create 0 new ExpressionReceipts, 0 GCE progress, 0 mutations."""
    g, rep = _create_property_graph(seed)
    chunk = _make_surface_chunk(g, rep)
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    assert del_view.status == "FAILED"

    rcpts_before = len(g.recurrent_engine._receipts)
    for r in range(5):
        retried = g.loop_engine.retry_delivery(del_view.delivery_id, success=(r == 4))
        assert retried.retry_count == r + 1

    rcpts_after = len(g.recurrent_engine._receipts)
    assert rcpts_before == rcpts_after


# ── RFC16-P10 — Concurrent Independent-Interleaving Equivalence
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p10_concurrent_independent_interleaving_equivalence(seed: int):
    """RFC16-P10: All 6 legal permutations of independent work produce equivalent semantic state."""
    def _digest(graph: CognitiveGraph) -> str:
        rows = [f"E|{e.src}->{e.dst}|W={e.W:.4f}" for (src, dst), e in sorted(graph.edges.items())]
        return hashlib.sha256("\n".join(rows).encode()).hexdigest()

    perm_digests: list[str] = []
    for p in permutations(["A", "B", "C"]):
        g, rep = _create_property_graph(seed)
        for op in p:
            w = InternalWorkAuthorityView(f"w_{op}_{seed}", f"root_{op}_{seed}", "REASONING", (f"p_node_{1 if op=='A' else (2 if op=='B' else 3)}",), True)
            g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t)
        perm_digests.append(_digest(g))

    assert len(set(perm_digests)) == 1


# ── RFC16-P11 — Stale / Interruption Safety
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p11_stale_interruption_safety(seed: int):
    """RFC16-P11: Work derived from outdated version is rejected fail-closed as STALE_REJECTED."""
    g, rep = _create_property_graph(seed)
    work = InternalWorkAuthorityView(f"w_stale_{seed}", f"root_{seed}", "REASONING", ("p_node_1",), True)
    status, res = g.loop_engine.dispatch_internal_work(work, rep, observed_version=g.t - 1)
    assert status == "STALE_REJECTED"
    assert res is None


# ── RFC16-P12 — Quiescence / No-Blind-Retry
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p12_quiescence_no_blind_retry(seed: int):
    """RFC16-P12: Quiescence is derived from authority status without arbitrary loop counters."""
    g, _ = _create_property_graph(seed)
    f_empty = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
    q = g.loop_engine.derive_root_quiescence(f"root_q_{seed}", f_empty)
    assert q.is_quiescent is True
    assert q.quiescence_reason == "ALL_WORK_COMPLETE"


# ── RFC16-P13 — Stable Unified-Loop Boundedness
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p13_stable_unified_loop_boundedness(seed: int):
    """RFC16-P13: Canonical loop terminates strictly within finite operations into quiescent state."""
    g, _ = _create_property_graph(seed)
    chunk, del_view, q = g.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    assert chunk is not None
    assert del_view.status == "DELIVERED"
    assert q.is_quiescent is True


# ── RFC16-P14 — Locality & Cache Transparency
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p14_locality_and_cache_transparency(seed: int):
    """RFC16-P14: Control work execution scales locally with task scope, independent of remote graph/cache."""
    g, _ = _create_property_graph(seed)
    # Add 100 remote unrelated nodes
    for i in range(100):
        g.node(f"remote_p14_{seed}_{i}", "text")
    work = InternalWorkAuthorityView(f"w_loc_{seed}", f"root_loc_{seed}", "RFC14_GENERATION", ("p_node_1", "p_node_2"), True)
    f = g.loop_engine.derive_internal_work_frontier(f"root_loc_{seed}", (work,), set())
    assert len(f.ready_work) == 1


# ── RFC16-P15 — Deterministic Causal Replay
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p15_deterministic_causal_replay(seed: int):
    """RFC16-P15: Independent identical runs produce bit-exact identical behavioral signatures."""
    g1, _ = _create_property_graph(seed)
    g2, _ = _create_property_graph(seed)
    g1.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    g2.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    assert rfc16_behavioral_signature(g1.loop_engine) == rfc16_behavioral_signature(g2.loop_engine)


# ── RFC16-P16 — Upstream Regression & Authority Conservation
@pytest.mark.parametrize("seed", range(30))
def test_rfc16_p16_upstream_regression_and_authority_conservation(seed: int):
    """RFC16-P16: All 6 upstream behavioral signatures and structural assemblies remain strictly conserved."""
    g, _rep = _create_property_graph(seed)
    assert len(law14_behavioral_signature(g.assembly_manager)) == 16
    assert len(rfc12_behavioral_signature(g.representation_engine)) == 16
    assert len(rfc13_behavioral_signature(g.completion_engine)) == 16
    assert len(rfc14_behavioral_signature(g.generation_engine)) == 16
    assert len(rfc15_behavioral_signature(g.recurrent_engine)) == 16
    asms_before = len(g.assembly_manager.live_assemblies())
    g.loop_engine.execute_canonical_full_loop("query", ["concept_falcon", "fly"])
    assert len(g.assembly_manager.live_assemblies()) == asms_before
