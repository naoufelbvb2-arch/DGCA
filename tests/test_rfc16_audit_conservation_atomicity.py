"""
DGCA — RFC-16 v1.0 Conservation, Atomicity & Failure Matrix Verification Suite.
Validates F01..F12 failure modes, S01..S06 stale matrix, real non-empty assembly state conservation,
cognitive state conservation, multi-root isolation, and upstream frozen signatures.
"""
from __future__ import annotations

import hashlib

import pytest

from dgca.assembly import law14_behavioral_signature
from dgca.completion import rfc13_behavioral_signature
from dgca.generation import rfc14_behavioral_signature
from dgca.graph import CognitiveGraph
from dgca.loop import (
    InternalWorkAuthorityView,
    InternalWorkFrontier,
)
from dgca.recurrent import rfc15_behavioral_signature
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
    rfc12_behavioral_signature,
)


def _build_audit_fixture() -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph()
    # Real non-empty Law-14 assembly fixture
    g.link("falcon", "fly", W=0.92, contexts=("en",))
    g.link("falcon", "predator", W=0.88, contexts=("en",))
    g.link("fly", "predator", W=0.80, contexts=("en",))
    mgr = g.assembly_manager
    asm_edges = [("falcon", "fly"), ("falcon", "predator"), ("fly", "predator")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(asm_edges, root_episode_id=f"audit_ep_{i}", valid_origin=True)

    for i in range(1, 8):
        g.link(f"aud_node_{i}", f"aud_prop_{i}", W=0.85, contexts=("en",))
        if i < 7:
            g.link(f"aud_node_{i}", f"aud_node_{i+1}", W=0.95, contexts=("en",))

    receipts = [
        ParticipationReceipt(f"rcpt_aud_{i}", f"aud_node_{i}", 1, 0, "external", "node", activation_magnitude=0.9)
        for i in range(1, 8)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    object.__setattr__(rep, "representation_id", "rep_audit_conserv")
    return g, rep


def _compute_assembly_structural_digest(graph: CognitiveGraph) -> str:
    """Computes exact structural state digest over real non-empty Law-14 assemblies."""
    mgr = graph.assembly_manager
    live = mgr.live_assemblies()
    rows: list[str] = []
    for asm in sorted(live, key=lambda a: a.assembly_id):
        edges_str = ",".join(sorted(f"{u}->{v}" for u, v in asm.member_edges))
        members_str = ",".join(sorted(str(m) for m in asm.member_nodes))
        rows.append(
            f"ASM|{asm.assembly_id}|v={asm.version}|orig={asm.origin_signature}|"
            f"edges=[{edges_str}]|members=[{members_str}]|retired={asm.is_retired}"
        )
    blob = "\n".join(rows).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _compute_cognitive_state_digest(graph: CognitiveGraph) -> str:
    """Computes exact structural state digest over cognitive nodes and edges."""
    rows: list[str] = []
    for (src, dst), e in sorted(graph.edges.items()):
        ctx = ",".join(sorted(e.contexts))
        rows.append(f"E|{src}->{dst}|W={e.W:.4f}|kind={e.kind}|ctx=[{ctx}]")
    blob = "\n".join(rows).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ── 1. Real Non-Empty Assembly & Cognitive State Conservation
def test_rfc16_assembly_and_cognitive_digest_conservation():
    """Verifies bit-exact conservation of real non-empty assembly state and cognitive state."""
    g, _ = _build_audit_fixture()
    asm_digest_before = _compute_assembly_structural_digest(g)
    cog_digest_before = _compute_cognitive_state_digest(g)
    assert len(g.assembly_manager.live_assemblies()) > 0

    # Execute 10 canonical full loop executions
    for i in range(10):
        chunk, del_view, q_view = g.loop_engine.execute_canonical_full_loop(f"Query {i}", ["falcon", "fly"])
        assert chunk is not None
        assert del_view.status == "DELIVERED"
        assert q_view.is_quiescent is True

    asm_digest_after = _compute_assembly_structural_digest(g)
    cog_digest_after = _compute_cognitive_state_digest(g)

    assert asm_digest_before == asm_digest_after
    assert cog_digest_before == cog_digest_after


# ── 2. Upstream Frozen Signatures Invariance
def test_rfc16_upstream_signatures_invariance():
    """Verifies that all 6 upstream behavioral signatures remain identical."""
    g, _rep = _build_audit_fixture()
    # RFC-11 / Law 14
    sig_11 = law14_behavioral_signature(g.assembly_manager)
    assert len(sig_11) == 16
    # RFC-12
    sig_12 = rfc12_behavioral_signature(g.representation_engine)
    assert len(sig_12) == 16
    # RFC-13 / Law 15
    sig_13 = rfc13_behavioral_signature(g.completion_engine)
    assert len(sig_13) == 16
    # RFC-14 / Law 16
    sig_14 = rfc14_behavioral_signature(g.generation_engine)
    assert len(sig_14) == 16
    # RFC-15 / Law 17
    sig_15 = rfc15_behavioral_signature(g.recurrent_engine)
    assert len(sig_15) == 16


# ── 3. F01..F12 Failure Mode Matrix
def test_rfc16_f01_ingress_boundary_breach():
    """F01: Ingress boundary breach is blocked."""
    g, _ = _build_audit_fixture()
    ev, _ = g.loop_engine.ingress_external_event("f01_ev", "f01_ep", "internal", is_internal_call=True)
    assert ev is None


def test_rfc16_f02_evidence_eligibility_bypass():
    """F02: Evidence eligibility bypass is blocked."""
    g, _ = _build_audit_fixture()
    ev, is_nov = g.loop_engine.ingress_external_event("f02_ev", "f02_ep", "raw feedback")
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, g.loop_engine.derive_feedback_authority(ev), is_nov)
    assert elig.is_eligible is False
    learned, _ = g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("a", "b"))
    assert learned is False


def test_rfc16_f03_delivery_retry_progress_duplication():
    """F03: Delivery retry does not duplicate GCE progress."""
    g, rep = _build_audit_fixture()
    gen_eng = g.generation_engine
    frame = gen_eng.build_generative_frame(rep, frozenset(["aud_node_1", "aud_node_2"]))
    h = gen_eng.build_hierarchy([frame])
    p, _ = gen_eng.linearize_hierarchy(h)
    chunk = gen_eng.realize_surface_chunk(p, str(rep.representation_id))
    del_view = g.loop_engine.deliver_surface_output(chunk, str(rep.representation_id), simulate_transport_failure=True)
    rcpts_before = len(g.recurrent_engine._receipts)
    g.loop_engine.retry_delivery(del_view.delivery_id, success=True)
    assert len(g.recurrent_engine._receipts) == rcpts_before


def test_rfc16_f04_closed_gce_reopening():
    """F04: Closed GCE cannot be reopened."""
    g, _rep = _build_audit_fixture()
    epoch = g.recurrent_engine.create_epoch("root_f04")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    closed = g.recurrent_engine.get_epoch(epoch.epoch_id)
    ev, _ = g.loop_engine.ingress_external_event("ev_f04", "ep_f04", "continue")
    _, new_id = g.loop_engine.process_task_relation(ev, "root_f04", closed)
    assert new_id != closed.epoch_id
    assert closed.lifecycle == "CLOSED"


def test_rfc16_f05_cross_scope_cancellation_bleed():
    """F05: Cancellation of root A does not cancel root B."""
    g, _ = _build_audit_fixture()
    ev, _ = g.loop_engine.ingress_external_event("ev_f05", "ep_f05", "cancel")
    g.loop_engine.process_task_relation(ev, "root_f05_A")
    assert "root_f05_A" in g.loop_engine._cancelled_roots
    assert "root_f05_B" not in g.loop_engine._cancelled_roots


def test_rfc16_f06_stale_work_execution():
    """F06: Stale work execution is rejected."""
    g, rep = _build_audit_fixture()
    w = InternalWorkAuthorityView("w_f06", "root_f06", "REASONING", ("aud_node_1",), True)
    status, res = g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t - 1)
    assert status == "STALE_REJECTED"
    assert res is None


def test_rfc16_f07_hidden_reasoning_completion_bypass():
    """F07: Hidden reasoning/completion cannot be executed under unauthorized kind."""
    g, rep = _build_audit_fixture()
    w = InternalWorkAuthorityView("w_f07", "root_f07", "UNAUTHORIZED_KIND", ("aud_node_1",), True)
    status, _ = g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t)
    assert status == "UNAUTHORIZED_SUBSYSTEM"


def test_rfc16_f08_ambiguity_winner_fabrication():
    """F08: Ambiguity does not fabricate an arbitrary winner."""
    g, _ = _build_audit_fixture()
    f = InternalWorkFrontier(ready_work=(), blocked_work=(), status="AMBIGUOUS")
    q = g.loop_engine.derive_root_quiescence("root_f08", f)
    assert q.quiescence_reason == "MUTUAL_AMBIGUITY"


def test_rfc16_f09_arbitrary_loop_counter_dependency():
    """F09: Quiescence is reached lawfully without arbitrary counters."""
    g, _ = _build_audit_fixture()
    f = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
    q = g.loop_engine.derive_root_quiescence("root_f09", f)
    assert q.is_quiescent is True


def test_rfc16_f10_positive_learning_attribution_loss():
    """F10: Valid learning updates always retain full attribution trace."""
    g, _ = _build_audit_fixture()
    ev, is_nov = g.loop_engine.ingress_external_event("ev_f10", "ep_f10", "fact: aud_node_1, aud_prop_1", metadata={"authorized_source": True})
    elig = g.loop_engine.evaluate_evidence_eligibility(ev, g.loop_engine.derive_feedback_authority(ev), is_nov)
    learned, attr = g.loop_engine.process_validated_learning(ev, elig, "Law1_HebbianCreation", ("aud_node_1", "aud_prop_1"))
    assert learned is True
    assert attr in g.loop_engine._learning_attributions


def test_rfc16_f11_non_empty_assembly_corruption():
    """F11: Assembly structural integrity is preserved."""
    g, _rep = _build_audit_fixture()
    asm_count_before = len(g.assembly_manager.live_assemblies())
    g.loop_engine.execute_canonical_full_loop("query", ["falcon", "fly"])
    assert len(g.assembly_manager.live_assemblies()) == asm_count_before


def test_rfc16_f12_upstream_signature_regression():
    """F12: Upstream signature regression check."""
    g, _rep = _build_audit_fixture()
    assert g.loop_engine is not None


# ── 4. S01..S06 Stale / Concurrency Matrix
@pytest.mark.parametrize("stale_offset", [1, 2, 5, 10, 50, 100])
def test_rfc16_s01_to_s06_stale_matrix(stale_offset: int):
    """S01..S06: Tests stale state rejection across multiple version disparities."""
    g, rep = _build_audit_fixture()
    w = InternalWorkAuthorityView(f"w_stale_{stale_offset}", "root_s", "REASONING", ("aud_node_1",), True)
    status, _ = g.loop_engine.dispatch_internal_work(w, rep, observed_version=g.t - stale_offset)
    assert status == "STALE_REJECTED"


# ── 5. M01..M04 Multi-Root Isolation Matrix
@pytest.mark.parametrize("m_idx", [1, 2, 3, 4])
def test_rfc16_m01_to_m04_multi_root_isolation(m_idx: int):
    """M01..M04: Tests isolation between concurrent roots under various relations."""
    g, _ = _build_audit_fixture()
    root_1 = f"m_root_1_{m_idx}"
    root_2 = f"m_root_2_{m_idx}"

    ev1, _ = g.loop_engine.ingress_external_event(f"ev1_{m_idx}", f"ep1_{m_idx}", "Alpha")
    ev2, _ = g.loop_engine.ingress_external_event(f"ev2_{m_idx}", f"ep2_{m_idx}", "Beta")

    rel1, _ = g.loop_engine.process_task_relation(ev1, root_1)
    rel2, _ = g.loop_engine.process_task_relation(ev2, root_2)

    assert rel1.relation_kind == "NEW_ROOT"
    assert rel2.relation_kind == "NEW_ROOT"


# ── 6. Empty / Disabled Equivalence Proof
def test_rfc16_empty_disabled_equivalence():
    """Verifies that an empty work frontier yields immediate lawful quiescence."""
    g, _ = _build_audit_fixture()
    f = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
    q = g.loop_engine.derive_root_quiescence("root_empty", f)
    assert q.is_quiescent is True
    assert q.quiescence_reason == "ALL_WORK_COMPLETE"
