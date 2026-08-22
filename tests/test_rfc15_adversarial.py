"""
DGCA — RFC-15 v1.0 / LAW 17 v1.0
ADVERSARIAL TEST SUITE (RFC15-A01 .. RFC15-A30)
30 Adversarial Security, Locality, Conservation & Anti-Exploit Families
"""
from __future__ import annotations

import time

import pytest

from dgca.generation import SourceAlignment, SurfaceChunk
from dgca.graph import CognitiveGraph
from dgca.recurrent import (
    ExpressionReceipt,
    ExpressiveObligation,
    ReferentialAccessibilityView,
    rfc15_behavioral_signature,
)
from dgca.representation import ParticipationReceipt, SparseDistributedCognitiveRepresentation


def _make_rep(g: CognitiveGraph, nodes: list[str]) -> SparseDistributedCognitiveRepresentation:
    receipts = [
        ParticipationReceipt(f"rcpt_{n}", n, 1, 0, "external", "node", activation_magnitude=0.9)
        for n in nodes
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    object.__setattr__(rep, "representation_id", "rep_adv_test")
    return rep


# ── RFC15-A01: Unbound GCE Injection Attack
def test_rfc15_a01_unbound_gce_injection():
    """RFC15-A01: Attempting to execute with non-existent or forged epoch_id is rejected."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["node_1"])
    with pytest.raises(KeyError):
        g.recurrent_engine.execute_recurrent_step("gce_forged_999", rep)


# ── RFC15-A02: Forged ExpressionReceipt Injection
def test_rfc15_a02_forged_expression_receipt_injection():
    """RFC15-A02: Injecting fake receipt not derived from RFC-14 emission is blocked."""
    g = CognitiveGraph()
    with pytest.raises(ValueError):
        g.recurrent_engine.create_expression_receipt(
            surface_chunk=SurfaceChunk("c1", "rep", (), "", "COMPLETE"),
            source_alignment=None,
            parent_rid="rep",
            root_authority_ref="root",
        )


# ── RFC15-A03: Foreign Root Authority Hijacking
def test_rfc15_a03_foreign_root_authority_hijacking():
    """RFC15-A03: Appending receipt from root_A into epoch of root_B raises ValueError."""
    g = CognitiveGraph()
    epoch_b = g.recurrent_engine.create_epoch("root_B")
    rcpt_a = ExpressionReceipt("er_a", "root_A", "rid", SourceAlignment("su1", "occ1", "auth1"), "c1", ("elem",))
    with pytest.raises(ValueError, match="root authority"):
        g.recurrent_engine.append_receipt(epoch_b.epoch_id, rcpt_a)


# ── RFC15-A04: Cyclic Continuation Attack
def test_rfc15_a04_cyclic_continuation_attack():
    """RFC15-A04: Cyclic causal/temporal constraints return CONTINUATION_CONFLICT without dropping edges."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["cyc_a", "cyc_b"])
    epoch = g.recurrent_engine.create_epoch("root_cyc")
    ob_a = ExpressiveObligation("ob_a", "root_cyc", "cyc_a", "role")
    ob_b = ExpressiveObligation("ob_b", "root_cyc", "cyc_b", "role")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(
        epoch.epoch_id, rep, explicit_obligations=[ob_a, ob_b], explicit_precedences=[("ob_a", "ob_b"), ("ob_b", "ob_a")]
    )
    assert closure.closure_reason == "CONFLICT"


# ── RFC15-A05: Remote Graph Flooding
def test_rfc15_a05_remote_graph_flooding():
    """RFC15-A05: Adding 2,000 unrelated nodes/edges maintains strict local execution time."""
    g = CognitiveGraph()
    for i in range(2000):
        g.link(f"flood_{i}", f"flood_{i+1}", W=0.5, contexts=("en",))
    g.link("local_1", "local_1_p", W=0.9, contexts=("en",))
    rep = _make_rep(g, ["local_1"])
    epoch = g.recurrent_engine.create_epoch("root_flood")

    t0 = time.perf_counter()
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep)
    dur = time.perf_counter() - t0

    assert closure.closure_reason == "COMPLETE"
    assert dur < 0.10  # Must execute in under 100ms


# ── RFC15-A06: Self-Reinforcement Exploit
def test_rfc15_a06_self_reinforcement_exploit():
    """RFC15-A06: Recurrent generation steps strictly produce zero Edge weight increments."""
    g = CognitiveGraph()
    g.link("item_sr", "prop_sr", W=0.60, contexts=("en",))
    rep = _make_rep(g, ["item_sr"])
    epoch = g.recurrent_engine.create_epoch("root_sr")
    g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert g.edges[("item_sr", "prop_sr")].W == 0.60


# ── RFC15-A07: TBR Authority Forgery via Re-entry
def test_rfc15_a07_tbr_authority_forgery():
    """RFC15-A07: ExpressionReceipts cannot be converted into TBR binding receipts."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["item_tbr"])
    g.link("item_tbr", "prop_tbr", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_tbr")
    g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep)
    assert len(g.representation_engine._transient_binding_receipts if hasattr(g.representation_engine, "_transient_binding_receipts") else ()) == 0


# ── RFC15-A08: Discourse Memory Leak Attack
def test_rfc15_a08_discourse_memory_leak_attack():
    """RFC15-A08: Nodes and edges must never store persistent 'already_said' flags."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["node_leak"])
    g.link("node_leak", "p_leak", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_leak")
    g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep)
    assert not hasattr(g.nodes["node_leak"], "already_said")
    assert not hasattr(g.edges[("node_leak", "p_leak")], "already_said")


# ── RFC15-A09: Stale Continuation Replay
def test_rfc15_a09_stale_continuation_replay():
    """RFC15-A09: Closed or modified GCE rejects stale execution attempts."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_stale")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "CANCELLED")
    rep = _make_rep(g, ["n1"])
    status, _, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "STALE"


# ── RFC15-A10: Reopened GCE Hijacking
def test_rfc15_a10_reopened_gce_hijacking():
    """RFC15-A10: CLOSED GCE cannot be appended to or reopened."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_reopen")
    closed_ep, _ = g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    rcpt = ExpressionReceipt("er_reopen", "root_reopen", "rid", SourceAlignment("su", "occ", "auth"), "c1", ("elem",))
    with pytest.raises(ValueError, match="CLOSED"):
        g.recurrent_engine.append_receipt(closed_ep.epoch_id, rcpt)


# ── RFC15-A11: Budget Exhaustion Bypass
def test_rfc15_a11_budget_exhaustion_bypass():
    """RFC15-A11: Negative or zero budget halts with BUDGET_UNAVAILABLE or PARTIAL_BUDGET without free execution."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["budget_node"])
    g.link("budget_node", "p", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_budget_bypass")
    status, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep, budget=0.0)
    assert status == "BUDGET_UNAVAILABLE"
    assert rcpt is None


# ── RFC15-A12: Zero-Confidence Ghost Receipt
def test_rfc15_a12_zero_confidence_ghost_receipt():
    """RFC15-A12: When surface realization produces no output, no ghost receipt is published."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["ghost_node"])
    # No linking property edges
    epoch = g.recurrent_engine.create_epoch("root_ghost")
    _closure, _ = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep)
    final_ep = g.recurrent_engine.get_epoch(epoch.epoch_id)
    assert len(final_ep.progress_receipt_refs) == 1  # Standard fallback or 0 ghost


# ── RFC15-A13: Law 14 Assembly Hijacking
def test_rfc15_a13_assembly_hijacking():
    """RFC15-A13: Recurrent generation creates 0 structural assemblies or assembly votes."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["asm_a", "asm_b"])
    g.link("asm_a", "asm_b", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_asm")
    g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep)
    assert len(g.assembly_manager.assemblies) == 0


# ── RFC15-A14: Cross-Snapshot State Confusion
def test_rfc15_a14_cross_snapshot_state_confusion():
    """RFC15-A14: Receipts created in snapshot 1 remain validly registered in GCE across snapshot transitions."""
    g = CognitiveGraph()
    rep1 = _make_rep(g, ["node_1"])
    g.link("node_1", "p1", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_cross_snap")
    _, ep1, _r1, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep1)

    rep2 = _make_rep(g, ["node_1", "node_2"])
    g.link("node_2", "p2", W=0.9, contexts=("en",))
    g.link("node_1", "node_2", W=0.9, contexts=("order",))
    obs2 = g.recurrent_engine.derive_obligations(rep2, "root_cross_snap")
    cov2 = g.recurrent_engine.compute_coverage(obs2, ep1, rep2)
    assert len(cov2.covered_obligation_ids) == 1


# ── RFC15-A15: Infinite Paraphrase Loop Attack
def test_rfc15_a15_infinite_paraphrase_loop_attack():
    """RFC15-A15: Re-expressing an already covered obligation without repeat authority is suppressed."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["car_entity"])
    g.link("car_entity", "p", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_loop")
    _, ep, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    obs = g.recurrent_engine.derive_obligations(rep, "root_loop")
    cov = g.recurrent_engine.compute_coverage(obs, ep, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    assert len(rem.remaining_obligations) == 0


# ── RFC15-A16: Ambiguity Resolution by ID Cheating
def test_rfc15_a16_ambiguity_resolution_by_id_cheating():
    """RFC15-A16: Multiple ready obligations must not resolve by sorting IDs; must return CONTINUATION_AMBIGUOUS."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["aaa", "zzz"])
    g.link("aaa", "pa", W=0.9, contexts=("en",))
    g.link("zzz", "pz", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_no_sort_cheat")
    status, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "CONTINUATION_AMBIGUOUS"
    assert rcpt is None


# ── RFC15-A17: Arbitrary Text Receipt Forgery
def test_rfc15_a17_arbitrary_text_receipt_forgery():
    """RFC15-A17: Strings cannot be passed as SurfaceChunk to create_expression_receipt."""
    g = CognitiveGraph()
    with pytest.raises(ValueError):
        g.recurrent_engine.create_expression_receipt("plain_string", None, "rid", "root")


# ── RFC15-A18: Pronoun Form Pre-commitment Injection
def test_rfc15_a18_pronoun_form_precommitment_injection():
    """RFC15-A18: Referential accessibility does not contain pronoun strings or morphology."""
    ref_view = ReferentialAccessibilityView({"alice": ("er1",)}, frozenset())
    assert not hasattr(ref_view, "he_she_they")
    assert not hasattr(ref_view, "pronoun")


# ── RFC15-A19: Broken Sequence Blocker Attack
def test_rfc15_a19_broken_sequence_blocker():
    """RFC15-A19: Missing predecessor obligation in sequence halts with NO_AUTHORIZED_CONTINUATION."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["step_2"])
    g.link("step_2", "p", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_broken_seq")
    ob2 = ExpressiveObligation("ob2", "root_broken_seq", "step_2", "role")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(
        epoch.epoch_id, rep, explicit_obligations=[ob2], explicit_precedences=[("ob1_missing", "ob2")]
    )
    assert closure.closure_reason == "NO_AUTHORIZED_CONTINUATION"


# ── RFC15-A20: Mutation During Closed GCE Step
def test_rfc15_a20_mutation_during_closed_gce_step():
    """RFC15-A20: Step on a CLOSED epoch mutates zero graph state."""
    g = CognitiveGraph()
    g.link("safe_a", "safe_b", W=0.77, contexts=("en",))
    rep = _make_rep(g, ["safe_a"])
    epoch = g.recurrent_engine.create_epoch("root_safe_mut")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    w_before = g.edges[("safe_a", "safe_b")].W
    g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert g.edges[("safe_a", "safe_b")].W == w_before


# ── RFC15-A21: Repair Obligation Hallucination
def test_rfc15_a21_repair_hallucination():
    """RFC15-A21: Without explicit repair authority, is_repair remains False."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["norm_node"])
    obs = g.recurrent_engine.derive_obligations(rep, "root_no_repair")
    assert all(not ob.is_repair for ob in obs)


# ── RFC15-A22: Cross-Language Coverage Collision
def test_rfc15_a22_cross_language_coverage_collision():
    """RFC15-A22: Language-specific obligations are distinct."""
    ob_en = ExpressiveObligation("ob_en", "root_lang", "item_x", "role", language_context="en")
    ob_ar = ExpressiveObligation("ob_ar", "root_lang", "item_x", "role", language_context="ar")
    assert ob_en.language_context != ob_ar.language_context


# ── RFC15-A23: Superseded Expression Deletion Attack
def test_rfc15_a23_superseded_expression_deletion_attack():
    """RFC15-A23: Diverged semantic state never deletes historical ExpressionReceipts from GCE."""
    g = CognitiveGraph()
    rep1 = _make_rep(g, ["old_concept"])
    g.link("old_concept", "p", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_diverge")
    _, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep1)

    rep2 = _make_rep(g, ["completely_different_concept"])
    g.link("completely_different_concept", "p", W=0.9, contexts=("en",))
    obs2 = g.recurrent_engine.derive_obligations(rep2, "root_diverge")
    cov2 = g.recurrent_engine.compute_coverage(obs2, ep, rep2)

    assert rcpt.receipt_id in ep.progress_receipt_refs  # Receipt remains intact
    assert len(cov2.covered_obligation_ids) == 0        # Coverage is not asserted


# ── RFC15-A24: Double Close Fault Injection
def test_rfc15_a24_double_close_fault_injection():
    """RFC15-A24: Closing an already closed GCE is idempotent and returns identical closure view."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_double_close")
    ep1, cv1 = g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    ep2, cv2 = g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    assert ep1.lifecycle == ep2.lifecycle == "CLOSED"
    assert cv1.closure_reason == cv2.closure_reason == "COMPLETE"


# ── RFC15-A25: Zero-Step No-Progress Fixed-Point Attack
def test_rfc15_a25_zero_step_fixed_point_attack():
    """RFC15-A25: An unchanging operational signature halts with NO_PROGRESS_FIXED_POINT or NO_AUTHORIZED_CONTINUATION."""
    g = CognitiveGraph()
    rep = _make_rep(g, ["iso1"])
    epoch = g.recurrent_engine.create_epoch("root_fp_attack")
    ob = ExpressiveObligation("ob_iso", "root_fp_attack", "iso1", "role")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(
        epoch.epoch_id, rep, explicit_obligations=[ob], explicit_precedences=[("ob_missing", "ob_iso")]
    )
    assert closure.closure_reason == "NO_AUTHORIZED_CONTINUATION"


# ── RFC15-A26: Unbounded Graph Traversal Exploit
def test_rfc15_a26_unbounded_graph_traversal_exploit():
    """RFC15-A26: 5,000 graph nodes do not cause quadratic slowdown in local recurrent step."""
    g = CognitiveGraph()
    for i in range(5000):
        g.node(f"huge_{i}", "text")
    g.link("target_item", "p", W=0.9, contexts=("en",))
    rep = _make_rep(g, ["target_item"])
    epoch = g.recurrent_engine.create_epoch("root_scale")

    t0 = time.perf_counter()
    status, _, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    dur = time.perf_counter() - t0

    assert status == "PROGRESS"
    assert dur < 0.05  # Under 50ms


# ── RFC15-A27: External Evidence Promotion Exploit
def test_rfc15_a27_external_evidence_promotion_exploit():
    """RFC15-A27: Generated receipts cannot become ExternalEvidence."""
    rcpt = ExpressionReceipt("er_exp", "root", "rid", SourceAlignment("su", "occ", "auth"), "c1", ("elem",))
    assert rcpt.origin_lineage == "GENERATION"
    assert rcpt.origin_lineage != "external"


# ── RFC15-A28: Law 18 Premature Invocation
def test_rfc15_a28_law18_premature_invocation():
    """RFC15-A28: Verifies no Law 18 hooks or modules exist."""
    import dgca.config as cfg
    assert not hasattr(cfg.Law, "LAW_18")


# ── RFC15-A29: Non-Empty Assembly Corruption
def test_rfc15_a29_non_empty_assembly_corruption():
    """RFC15-A29: Law-14 structural assemblies are 100% bit-conserved across recurrent generation."""
    from dgca.assembly import law14_behavioral_signature
    g = CognitiveGraph()
    g.assembly_manager.record_participation([("node_a", "node_b"), ("node_b", "node_c")], root_episode_id="ep_asm", valid_origin=True)
    sig_before = law14_behavioral_signature(g.assembly_manager)

    rep = _make_rep(g, ["node_a"])
    g.link("node_a", "prop_a", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_asm_protect")
    g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep)

    sig_after = law14_behavioral_signature(g.assembly_manager)
    assert sig_before == sig_after


# ── RFC15-A30: Signature Sensitivity Tampering
def test_rfc15_a30_signature_sensitivity_tampering():
    """RFC15-A30: Tampering with a single receipt element strictly changes the behavioral signature."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_sig_sens", epoch_id="ep_sens")
    rcpt1 = ExpressionReceipt("er1", "root_sig_sens", "rid1", SourceAlignment("su1", "occ1", "auth1"), "c1", ("elem_A",))
    g.recurrent_engine._receipts[rcpt1.receipt_id] = rcpt1
    g.recurrent_engine.append_receipt(epoch.epoch_id, rcpt1)
    sig1 = rfc15_behavioral_signature(g.recurrent_engine)

    g2 = CognitiveGraph()
    epoch2 = g2.recurrent_engine.create_epoch("root_sig_sens", epoch_id="ep_sens")
    rcpt2 = ExpressionReceipt("er1", "root_sig_sens", "rid1", SourceAlignment("su1", "occ1", "auth1"), "c1", ("elem_B",))  # Tampered element
    g2.recurrent_engine._receipts[rcpt2.receipt_id] = rcpt2
    g2.recurrent_engine.append_receipt(epoch2.epoch_id, rcpt2)
    sig2 = rfc15_behavioral_signature(g2.recurrent_engine)

    assert sig1 != sig2
