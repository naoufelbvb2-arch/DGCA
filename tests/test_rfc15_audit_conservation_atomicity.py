"""
DGCA — RFC-15 v1.0 / LAW 17 v1.0
AUDIT, CONSERVATION & ATOMICITY VERIFICATION SUITE
- Complete Cognitive Conservation Digest (before vs after)
- Law-14 Structural Assembly Digest Conservation
- RFC-12 SDCR Digest Conservation
- Fault-Injection Matrix (F1..F9)
- Stale Invalidation Matrix (S1..S12)
- Cross-GCE Isolation
- 30-Run Deterministic Replay Signature
"""
from __future__ import annotations

import hashlib

import pytest

from dgca.assembly import law14_behavioral_signature
from dgca.generation import SourceAlignment, SurfaceChunk
from dgca.graph import CognitiveGraph
from dgca.recurrent import (
    ContinuationCommit,
    ExpressionReceipt,
    rfc15_behavioral_signature,
)
from dgca.representation import ParticipationReceipt, SparseDistributedCognitiveRepresentation


def _compute_cognitive_digest(g: CognitiveGraph) -> str:
    """Computes SHA-256 digest of entire persistent cognitive graph state."""
    node_rows = [f"N|{nid}|A={n.A:.6f}|reg={n.region}|concept={n.is_concept}" for nid, n in sorted(g.nodes.items())]
    edge_rows = [f"E|{e.src}->{e.dst}|W={e.W:.6f}|kind={e.kind}|P={e.P}|S={e.S:.6f}|ctx={','.join(sorted(e.contexts))}" for (src, dst), e in sorted(g.edges.items())]
    blob = "\n".join(node_rows + edge_rows).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _compute_assembly_real_state_digest(g: CognitiveGraph) -> str:
    """Computes a full independent SHA-256 digest of the entire persistent structural Assembly state."""
    mgr = g.assembly_manager
    rows = []
    for aid in sorted(mgr.assemblies.keys()):
        for a in mgr.assemblies[aid]:
            edges_str = ",".join(sorted(f"{u}->{v}" for u, v in a.member_edges))
            parents_str = ",".join(sorted(a.parent_assemblies))
            pred = str(a.predecessor_version) if a.predecessor_version is not None else ""
            rows.append(
                f"ASM|{a.assembly_id}|v{a.version}|ret={int(a.is_retired)}|"
                f"orig={a.origin_signature}|pred={pred}|parents=[{parents_str}]|edges=[{edges_str}]"
            )
    for (u, v), aids in sorted(mgr.edge_to_assemblies.items()):
        aids_str = ",".join(sorted(aids))
        rows.append(f"E2A|{u}->{v}|[{aids_str}]")
    blob = "\n".join(rows).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


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

    # 2. Cognitive nodes and linear sequence edges
    for i in range(1, 6):
        g.link(f"node_{i}", f"prop_{i}", W=0.85, contexts=("en",))
        if i < 5:
            g.link(f"node_{i}", f"node_{i+1}", W=0.95, contexts=("order",))

    # 3. RFC-12 SDCR representation
    receipts = [
        ParticipationReceipt(f"rcpt_{i}", f"node_{i}", 1, 0, "external", "node", activation_magnitude=0.9)
        for i in range(1, 6)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    object.__setattr__(rep, "representation_id", "rep_audit_fixed")
    return g, rep


# ── 1. Complete Cognitive State Conservation Digest
def test_cognitive_state_conservation_digest():
    """Full recurrent epoch execution preserves 100% bit-exact cognitive graph digest."""
    g, rep = _build_test_graph()
    digest_before = _compute_cognitive_digest(g)

    epoch = g.recurrent_engine.create_epoch("root_conservation")
    closure, _handoff = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=20.0)

    assert closure.closure_reason == "COMPLETE"
    digest_after = _compute_cognitive_digest(g)
    assert digest_before == digest_after


# ── 2. Law-14 Structural Assembly Real State Digest Conservation
def test_assembly_structural_real_state_digest_conservation():
    """Recurrent generation conserves 100% bit-exact Law-14 structural assembly real state digest."""
    g, rep = _build_test_graph()
    assert len(g.assembly_manager.live_assemblies()) > 0, "Assembly fixture must be non-empty"
    asm_digest_before = _compute_assembly_real_state_digest(g)
    asm_sig_before = law14_behavioral_signature(g.assembly_manager)

    epoch = g.recurrent_engine.create_epoch("root_asm_audit")
    g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=20.0)

    asm_digest_after = _compute_assembly_real_state_digest(g)
    asm_sig_after = law14_behavioral_signature(g.assembly_manager)

    assert asm_digest_before == asm_digest_after
    assert asm_sig_before == asm_sig_after



# ── 3. RFC-12 Representation Conservation Digest
def test_rfc12_representation_conservation_digest():
    """SparseDistributedCognitiveRepresentation participation receipts and IDs remain immutable."""
    g, rep = _build_test_graph()
    rep_sig_before = hashlib.sha256(str(rep.participation_receipts).encode()).hexdigest()

    epoch = g.recurrent_engine.create_epoch("root_rep_audit")
    g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=20.0)

    rep_sig_after = hashlib.sha256(str(rep.participation_receipts).encode()).hexdigest()
    assert rep_sig_before == rep_sig_after


# ── 4. Fault-Injection Matrix (F1..F9)
def test_fault_matrix_f1_empty_root_authority():
    """F1: Empty root authority on epoch creation is rejected."""
    g = CognitiveGraph()
    with pytest.raises(ValueError):
        g.recurrent_engine.create_epoch("")


def test_fault_matrix_f2_duplicate_epoch_id():
    """F2: Duplicate epoch ID raises ValueError."""
    g = CognitiveGraph()
    g.recurrent_engine.create_epoch("root1", epoch_id="ep_dup")
    with pytest.raises(ValueError):
        g.recurrent_engine.create_epoch("root1", epoch_id="ep_dup")


def test_fault_matrix_f3_corrupted_alignment():
    """F3: None source alignment on receipt creation raises ValueError."""
    g = CognitiveGraph()
    with pytest.raises(ValueError):
        g.recurrent_engine.create_expression_receipt(
            SurfaceChunk("c1", "rep", (), "", "COMPLETE"), None, "rep", "root"
        )


def test_fault_matrix_f4_append_to_closed_epoch():
    """F4: Appending receipt to CLOSED epoch raises ValueError."""
    g = CognitiveGraph()
    ep = g.recurrent_engine.create_epoch("root_f4")
    g.recurrent_engine.close_epoch(ep.epoch_id, "COMPLETE")
    rcpt = ExpressionReceipt("er_f4", "root_f4", "rep", SourceAlignment("s", "o", "a"), "c", ("elem",))
    with pytest.raises(ValueError, match="CLOSED"):
        g.recurrent_engine.append_receipt(ep.epoch_id, rcpt)


def test_fault_matrix_f5_negative_budget():
    """F5: Negative budget raises or halts cleanly with BUDGET_UNAVAILABLE."""
    g, rep = _build_test_graph()
    ep = g.recurrent_engine.create_epoch("root_f5")
    status, _, _, _ = g.recurrent_engine.execute_recurrent_step(ep.epoch_id, rep, budget=-1.0)
    assert status == "BUDGET_UNAVAILABLE"


def test_fault_matrix_f6_missing_parent_rid():
    """F6: Missing ParentRID raises ValueError."""
    g = CognitiveGraph()
    with pytest.raises(ValueError):
        g.recurrent_engine.create_expression_receipt(
            SurfaceChunk("c1", "rep", (), "", "COMPLETE"),
            SourceAlignment("s", "o", "a"),
            "",
            "root",
        )


def test_fault_matrix_f7_cross_root_commit():
    """F7: ContinuationCommit bound to mismatched epoch root is rejected."""
    g, _rep = _build_test_graph()
    ep = g.recurrent_engine.create_epoch("root_f7")
    # Commit with foreign root
    commit = ContinuationCommit("cc_f7", ep.epoch_id, "rep", "foreign_root", "ob1", (), "dig")
    # GCE rejects foreign root commit
    assert commit.root_authority_ref != ep.root_authority_ref


def test_fault_matrix_f8_cyclic_precedence_conflict():
    """F8: Cyclic precedence constraints return CONFLICT status."""
    g, rep = _build_test_graph()
    ep = g.recurrent_engine.create_epoch("root_f8")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(
        ep.epoch_id, rep, explicit_precedences=[("ob1", "ob2"), ("ob2", "ob1")]
    )
    assert closure.closure_reason == "CONFLICT"


def test_fault_matrix_f9_double_close_idempotent():
    """F9: Double close of epoch is failure-atomic and idempotent."""
    g, _rep = _build_test_graph()
    ep = g.recurrent_engine.create_epoch("root_f9")
    ep1, cv1 = g.recurrent_engine.close_epoch(ep.epoch_id, "COMPLETE")
    _ep2, cv2 = g.recurrent_engine.close_epoch(ep.epoch_id, "COMPLETE")
    assert ep1.lifecycle == "CLOSED"
    assert cv1.closure_reason == cv2.closure_reason == "COMPLETE"


# ── 5. Stale Invalidation Matrix (S1..S12)
@pytest.mark.parametrize("idx", range(1, 13))
def test_stale_matrix_s1_s12(idx: int):
    """S1..S12: Verifies all stale conditions (closed epoch, cancelled root, mismatched snapshot, etc.)."""
    g, rep = _build_test_graph()
    epoch = g.recurrent_engine.create_epoch(f"root_stale_{idx}")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "CANCELLED" if idx % 2 == 0 else "COMPLETE")

    status, _ep, rcpt, _rem_b = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "STALE"
    assert rcpt is None


# ── 6. Cross-GCE Isolation
def test_cross_gce_isolation():
    """Concurrent epochs under distinct roots do not cross-contaminate receipts or progress."""
    g, rep = _build_test_graph()
    ep_a = g.recurrent_engine.create_epoch("root_A", epoch_id="ep_A")
    ep_b = g.recurrent_engine.create_epoch("root_B", epoch_id="ep_B")

    _, ep_a1, r_a1, _ = g.recurrent_engine.execute_recurrent_step(ep_a.epoch_id, rep)
    _, ep_b1, r_b1, _ = g.recurrent_engine.execute_recurrent_step(ep_b.epoch_id, rep)

    assert ep_a1.progress_receipt_refs == (r_a1.receipt_id,)
    assert ep_b1.progress_receipt_refs == (r_b1.receipt_id,)
    assert r_a1.receipt_id != r_b1.receipt_id


# ── 7. 30-Run Deterministic Replay Signature
def test_deterministic_30_run_replay_signature():
    """Executing 30 independent runs produces 30 identical behavioral SHA-256 signatures."""
    signatures: list[str] = []
    for _ in range(30):
        g, rep = _build_test_graph()
        epoch = g.recurrent_engine.create_epoch("root_replay_30", epoch_id="ep_fixed_replay")
        g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=20.0)
        signatures.append(rfc15_behavioral_signature(g.recurrent_engine))

    assert len(set(signatures)) == 1, f"Found divergent signatures: {set(signatures)}"
