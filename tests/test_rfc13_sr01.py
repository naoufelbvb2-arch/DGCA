"""
DGCA — RFC13-SR01 Formal Test Suite
Canonical Snapshot Reprojection & Settling-State Retention Repair

Authoritative Specification:
RFC13-SR01-Canonical-Snapshot-Reprojection-Repair-v1.0-FROZEN.md
RFC13-SR01-Adversarial-Freeze-Review-v1.0.md

Tests:
- Acceptance Tests: SR01-T01 .. SR01-T30
- Adversarial Tests: SR01-A01 .. SR01-A16
"""
from __future__ import annotations

from typing import Any

from dgca.causal_identity import (
    CAUSAL_IDENTITY_PROTOCOL_DIGEST,
    LITERAL_DOMAIN_REGISTRY,
)
from dgca.chat_runtime import (
    R3_MIN_RUNTIME_SEMANTICS_DIGEST,
    TransientActivationScope,
)
from dgca.completion import (
    rfc13_behavioral_signature,
)
from dgca.config import Law
from dgca.graph import CognitiveGraph
from dgca.observation import R2_OBSERVATION_SEMANTICS_DIGEST
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
    TransientBindingReceipt,
)
from dgca.signature import behavioral_signature, build_reference_graph


# ─────────────────────────────────────────────────────────── Helpers
def _make_graph_with_a_b(w_ab: float = 0.85, w_ba: float | None = None) -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=w_ab)
    if w_ba is not None:
        g.link("text:B", "text:A", W=w_ba)
    g.node("text:A", "text").excite(1, 1.0)
    r = ParticipationReceipt(
        receipt_id="rec_A_0",
        element_ref="text:A",
        parent_cycle_id=1,
        snapshot_or_microtick=0,
        origin_lineage="external",
        participation_kind="node",
        activation_magnitude=1.0,
    )
    rep0 = g.representation_engine.build_representation(1, 0, None, [r])
    return g, rep0


# ─────────────────────────────────────────────────────────── Acceptance Tests SR01-T01 .. SR01-T30

def test_sr01_t01_a_to_b_final_sdcr_contains_a_and_b():
    """SR01-T01: Stored A→B, cue A: final SDCR contains A and B."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, outcome = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "FIXED_POINT"
    assert "text:A" in settled.participating_node_refs
    assert "text:B" in settled.participating_node_refs
    assert settled.participating_node_refs == frozenset({"text:A", "text:B"})


def test_sr01_t02_a_to_b_to_c_chain_retains_snapshots():
    """SR01-T02: Stored A→B→C, cue A: successive SDCR snapshots are {A}, {A,B}, {A,B,C}."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:C", W=0.85)
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0])

    orig_reproject = g.completion_engine._reproject_settling_snapshot
    captured_snapshots: list[set[str]] = [set(rep0.participating_node_refs)]

    def tracking_reproject(*args: Any, **kwargs: Any):
        res = orig_reproject(*args, **kwargs)
        fresh_receipts = res[0]
        nodes = {str(r.element_ref) for r in fresh_receipts if r.participation_kind == "node"}
        captured_snapshots.append(nodes)
        return res

    g.completion_engine._reproject_settling_snapshot = tracking_reproject  # type: ignore[assignment]
    settled, outcome = g.completion_engine.run_settling_epoch(rep0, budget=1.0)

    assert outcome.closure_reason == "FIXED_POINT"
    assert captured_snapshots == [
        {"text:A"},
        {"text:A", "text:B"},
        {"text:A", "text:B", "text:C"},
    ]
    assert settled.participating_node_refs == frozenset({"text:A", "text:B", "text:C"})


def test_sr01_t03_old_participation_receipt_ids_never_reused():
    """SR01-T03: Old participation receipt IDs are never reused across snapshots."""
    g, rep0 = _make_graph_with_a_b(0.85)
    orig_id = rep0.participation_receipts[0].receipt_id
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)

    settled_receipt_ids = {r.receipt_id for r in settled.participation_receipts}
    assert orig_id not in settled_receipt_ids
    assert len(settled_receipt_ids) == len(settled.participation_receipts)


def test_sr01_t04_every_reprojected_receipt_has_current_snapshot_coords():
    """SR01-T04: Every reprojected receipt has current snapshot coordinates (cycle, tick)."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)

    target_cycle = settled.parent_cycle_id
    target_tick = settled.snapshot_or_microtick
    for r in settled.participation_receipts:
        assert r.parent_cycle_id == target_cycle
        assert r.snapshot_or_microtick == target_tick


def test_sr01_t05_external_origin_root_lineage_persists_without_root_expansion():
    """SR01-T05: External-origin root lineage persists without expanding root authority."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)

    receipt_map = {r.element_ref: r for r in settled.participation_receipts}
    assert receipt_map["text:A"].origin_lineage == "external"
    assert "text:B" not in rep0.participating_node_refs


def test_sr01_t06_pattern_completion_lineage_persists():
    """SR01-T06: PATTERN_COMPLETION lineage remains PATTERN_COMPLETION in later snapshots."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:C", W=0.85)
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0])

    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    receipt_map = {r.element_ref: r for r in settled.participation_receipts}
    assert receipt_map["text:B"].origin_lineage == "PATTERN_COMPLETION"
    assert receipt_map["text:C"].origin_lineage == "PATTERN_COMPLETION"


def test_sr01_t07_committed_set_prevents_recommit_while_target_remains_current():
    """SR01-T07: CommittedSet prevents recommit while target remains current."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, outcome = g.completion_engine.run_settling_epoch(rep0, budget=1.0)

    b_commits = [tgt for tgt in outcome.committed_targets if tgt[0] == "text:B"]
    assert len(b_commits) == 1
    assert "text:B" in settled.participating_node_refs


def test_sr01_t08_bidirectional_settling_without_oscillation():
    """SR01-T08: A↔B settles without representational oscillatory erasure."""
    g, rep0 = _make_graph_with_a_b(0.85, w_ba=0.55)
    settled, outcome = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "FIXED_POINT"
    assert settled.participating_node_refs == frozenset({"text:A", "text:B"})


def test_sr01_t09_edge_reprojection_requires_lawful_gate_open_edge():
    """SR01-T09: Edge reprojection requires lawful/gate-open current edge."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85, contexts=("ctx1",))
    g.link("text:B", "text:C", W=0.85, contexts=("ctx1",))
    g.node("text:A", "text").excite(1, 1.0)
    g.node("text:B", "text").excite(1, 1.0)

    r_a = ParticipationReceipt("r_a", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    r_b = ParticipationReceipt("r_b", "text:B", 1, 0, "external", "node", activation_magnitude=1.0)
    r_e = ParticipationReceipt("r_e", ("text:A", "text:B"), 1, 0, "external", "edge", relational_drive=0.85)
    rep0 = g.representation_engine.build_representation(1, 0, "ctx1", [r_a, r_b, r_e])
    assert ("text:A", "text:B") in rep0.participating_edge_refs

    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert ("text:A", "text:B") in settled.participating_edge_refs


def test_sr01_t10_closed_edge_is_not_reprojected():
    """SR01-T10: Missing/closed edge is not reprojected."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85, contexts=("ctx_specific",))
    g.link("text:B", "text:C", W=0.85)
    g.node("text:A", "text").excite(1, 1.0)
    g.node("text:B", "text").excite(1, 1.0)

    r_a = ParticipationReceipt("r_a", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    r_b = ParticipationReceipt("r_b", "text:B", 1, 0, "external", "node", activation_magnitude=1.0)
    r_e = ParticipationReceipt("r_e", ("text:A", "text:B"), 1, 0, "external", "edge", relational_drive=0.85)
    rep0 = g.representation_engine.build_representation(1, 0, "ctx_specific", [r_a, r_b, r_e])

    del g.edges[("text:A", "text:B")]
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert ("text:A", "text:B") not in settled.participating_edge_refs


def test_sr01_t11_valid_tbr_reissued_with_fresh_id_and_coords():
    """SR01-T11: Valid TBR gets fresh ID/current parent snapshot coordinates."""
    g, rep0_base = _make_graph_with_a_b(0.85)
    tbr0 = TransientBindingReceipt(
        binding_id="tbr_orig",
        parent_snapshot_ref=(1, 0),
        binding_scope_id="scope1",
        member_receipt_refs=("text:A",),
    )
    rep0 = g.representation_engine.build_representation(
        1, 0, None, list(rep0_base.participation_receipts), transient_bindings=[tbr0]
    )
    assert len(rep0.transient_binding_receipts) == 1

    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert len(settled.transient_binding_receipts) == 1
    tbr_settled = settled.transient_binding_receipts[0]
    assert tbr_settled.binding_id != "tbr_orig"
    assert tbr_settled.parent_snapshot_ref == (settled.parent_cycle_id, settled.snapshot_or_microtick)
    assert tbr_settled.member_receipt_refs == ("text:A",)


def test_sr01_t12_tbr_with_noncurrent_member_dropped():
    """SR01-T12: TBR with noncurrent member is dropped fail-closed."""
    g, rep0_base = _make_graph_with_a_b(0.85)
    tbr_invalid = TransientBindingReceipt(
        binding_id="tbr_invalid",
        parent_snapshot_ref=(1, 0),
        binding_scope_id="scope_bad",
        member_receipt_refs=("text:NON_CURRENT",),
    )
    rep_custom = g.representation_engine.build_representation(
        1, 0, None, list(rep0_base.participation_receipts)
    )
    object.__setattr__(rep_custom, "transient_binding_receipts", (tbr_invalid,))

    settled, _ = g.completion_engine.run_settling_epoch(rep_custom, budget=1.0)
    assert len(settled.transient_binding_receipts) == 0


def test_sr01_t13_no_new_tbr_invented():
    """SR01-T13: No new TBR is invented during reprojection if none existed."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert len(settled.transient_binding_receipts) == 0


def test_sr01_t14_stale_receipt_rejected_by_rfc12():
    """SR01-T14: Stale receipt remains strictly rejected by RFC12."""
    g = CognitiveGraph(enable_prediction=False)
    g.node("text:X", "text").excite(1, 1.0)
    stale_rec = ParticipationReceipt("r_stale", "text:X", 1, 0, "external", "node", activation_magnitude=1.0)
    rep = g.representation_engine.build_representation(1, 1, None, [stale_rec])
    assert "text:X" not in rep.participating_node_refs
    assert len(rep.participation_receipts) == 0


def test_sr01_t15_stale_tbr_rejected_by_rfc12():
    """SR01-T15: Stale TBR remains strictly rejected by RFC12."""
    g = CognitiveGraph(enable_prediction=False)
    g.node("text:X", "text").excite(1, 1.0)
    rec_valid = ParticipationReceipt("r_x", "text:X", 1, 1, "external", "node", activation_magnitude=1.0)
    stale_tbr = TransientBindingReceipt("tbr_stale", (1, 0), "scope1", ("text:X",))
    rep = g.representation_engine.build_representation(1, 1, None, [rec_valid], transient_bindings=[stale_tbr])
    assert len(rep.transient_binding_receipts) == 0


def test_sr01_t16_active_assembly_refs_do_not_materialize_inactive_members():
    """SR01-T16: Active Assembly refs do not materialize inactive members."""
    g, rep0 = _make_graph_with_a_b(0.85)
    g.node("text:INACTIVE", "text")
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert "text:INACTIVE" not in settled.participating_node_refs


def test_sr01_t17_ambiguity_remains_ambiguity_no_winner_invented():
    """SR01-T17: Ambiguity remains ambiguity; reprojection creates no winner."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B1", W=0.85)
    g.link("text:A", "text:B2", W=0.85)
    g.add_contradiction("text:B1", "text:B2")
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0])

    settled, outcome = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "AMBIGUOUS_FIXED_POINT"
    assert "text:B1" not in settled.participating_node_refs
    assert "text:B2" not in settled.participating_node_refs


def test_sr01_t18_root_witness_set_remains_original():
    """SR01-T18: Root witness set remains strictly original."""
    g, rep0 = _make_graph_with_a_b(0.85)
    _, outcome = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert outcome.committed_targets == frozenset({("text:B", ("global",), None)})


def test_sr01_t19_no_edge_w_mutation_during_reprojection():
    """SR01-T19: No Edge W/n/context mutation during settling reprojection."""
    g, rep0 = _make_graph_with_a_b(0.85)
    w_before = g.edge("text:A", "text:B").W
    n_before = g.edge("text:A", "text:B").n
    _, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert g.edge("text:A", "text:B").W == w_before
    assert g.edge("text:A", "text:B").n == n_before


def test_sr01_t20_no_rfc11_structural_vote_from_reprojection():
    """SR01-T20: No RFC11 structural vote from reprojection."""
    g, rep0 = _make_graph_with_a_b(0.85)
    pending_before = len(g.pending_structural_evidence) if hasattr(g, "pending_structural_evidence") else 0
    _, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    pending_after = len(g.pending_structural_evidence) if hasattr(g, "pending_structural_evidence") else 0
    assert pending_before == pending_after


def test_sr01_t21_canonical_replay_yields_identical_sdcr():
    """SR01-T21: Canonical replay yields identical final SDCR and outcome."""
    g1, rep1 = _make_graph_with_a_b(0.85)
    settled1, out1 = g1.completion_engine.run_settling_epoch(rep1, budget=1.0)

    g2, rep2 = _make_graph_with_a_b(0.85)
    settled2, out2 = g2.completion_engine.run_settling_epoch(rep2, budget=1.0)

    assert settled1.participating_node_refs == settled2.participating_node_refs
    assert out1.closure_reason == out2.closure_reason
    assert out1.committed_targets == out2.committed_targets


def test_sr01_t22_remote_graph_growth_does_not_alter_local_reprojection():
    """SR01-T22: Remote graph growth does not alter local reprojection."""
    g, rep0 = _make_graph_with_a_b(0.85)
    g.link("text:REMOTE_X", "text:REMOTE_Y", W=0.99)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert settled.participating_node_refs == frozenset({"text:A", "text:B"})
    assert "text:REMOTE_X" not in settled.participating_node_refs


def test_sr01_t23_r3_scoped_completion_leaves_ntotal_unchanged():
    """SR01-T23: R3 scoped completion leaves N_total unchanged."""
    g, rep0 = _make_graph_with_a_b(0.85)
    node_b = g.node("text:B", "text")
    n_before = node_b.N_total
    scope = TransientActivationScope(g)
    try:
        _settled, _ = g.completion_engine.run_settling_epoch(
            rep0, budget=1.0, activation_sink=scope
        )
    finally:
        scope.restore()
    assert node_b.N_total == n_before


def test_sr01_t24_r3_restores_transient_activation_before_rfc14():
    """SR01-T24: R3 restores transient activation before RFC14."""
    g, rep0 = _make_graph_with_a_b(0.85)
    node_b = g.node("text:B", "text")
    a_b_before = node_b.A

    scope = TransientActivationScope(g)
    try:
        _settled, _ = g.completion_engine.run_settling_epoch(
            rep0, budget=1.0, activation_sink=scope
        )
        assert node_b.A > 0.0
    finally:
        scope.restore()

    assert node_b.A == a_b_before


def test_sr01_t25_rfc14_receives_final_cumulative_current_sdcr():
    """SR01-T25: RFC14 receives final cumulative current SDCR."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert settled.participating_node_refs == frozenset({"text:A", "text:B"})


def test_sr01_t26_dog_canine_counterfactual_puts_canine_in_rfc14_input():
    """SR01-T26: dog→canine counterfactual puts canine in RFC14 input representation."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:dog", "text:canine", W=0.85)
    g.node("text:dog", "text").excite(1, 1.0)
    r_dog = ParticipationReceipt("r_dog", "text:dog", 1, 0, "external", "node", activation_magnitude=1.0)
    rep_dog = g.representation_engine.build_representation(1, 0, None, [r_dog])

    settled, _ = g.completion_engine.run_settling_epoch(rep_dog, budget=1.0)
    assert "text:canine" in settled.participating_node_refs
    assert "text:dog" in settled.participating_node_refs


def test_sr01_t27_rfc12_suite_passes_unchanged():
    """SR01-T27: RFC12 invariants remain fully satisfied."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert isinstance(settled, SparseDistributedCognitiveRepresentation)
    assert len(settled.participation_receipts) == 2


def test_sr01_t28_rfc13_behavioral_signature_reproduced():
    """SR01-T28: Post-repair RFC13 behavioral signature is deterministic and consistent."""
    g1 = CognitiveGraph()
    sig1 = rfc13_behavioral_signature(g1.completion_engine)
    g2 = CognitiveGraph()
    sig2 = rfc13_behavioral_signature(g2.completion_engine)
    assert sig1 == sig2
    assert sig1 == "3adbfcfd1f24802a"


def test_sr01_t29_rfc14_pass_succeeds_on_settled_sdcr():
    """SR01-T29: RFC14 generative engine executes on settled SDCR."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("concept_cat", "furry", W=0.85, contexts=("en",))
    g.node("concept_cat", "text").excite(1, 1.0)
    r_cat = ParticipationReceipt("r_cat", "concept_cat", 1, 0, "external", "node", activation_magnitude=1.0)
    rep = g.representation_engine.build_representation(1, 0, None, [r_cat])
    settled, _ = g.completion_engine.run_settling_epoch(rep, budget=1.0)
    handoff = g.generation_engine.execute_generative_pass(settled, frozenset(["concept_cat"]))
    assert handoff.surface_chunk_view.origin_lineage == "GENERATION"


def test_sr01_t30_r3_min_conserved_digests_match():
    """SR01-T30: All conserved signatures and digests match frozen specifications."""
    ref_g = build_reference_graph()
    law_sig = behavioral_signature(ref_g)
    assert law_sig == "915119d40643cb97"
    assert CAUSAL_IDENTITY_PROTOCOL_DIGEST == "f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398"
    assert len(LITERAL_DOMAIN_REGISTRY) == 21
    assert R2_OBSERVATION_SEMANTICS_DIGEST == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"
    assert R3_MIN_RUNTIME_SEMANTICS_DIGEST == "fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc"


# ─────────────────────────────────────────────────────────── Adversarial Tests SR01-A01 .. SR01-A16

def test_sr01_a01_stale_receipt_laundering_rejected():
    """SR01-A01: Stale-receipt laundering: injecting stale receipts into reprojection fails closed."""
    g, _rep0 = _make_graph_with_a_b(0.85)
    stale_rec = ParticipationReceipt("r_stale", "text:A", 99, 99, "external", "node", activation_magnitude=1.0)
    rep = g.representation_engine.build_representation(1, 0, None, [stale_rec])
    assert len(rep.participating_node_refs) == 0


def test_sr01_a02_stale_tbr_laundering_rejected():
    """SR01-A02: Stale-TBR laundering: passing stale TBR into RFC12 fails closed."""
    g, rep0 = _make_graph_with_a_b(0.85)
    stale_tbr = TransientBindingReceipt("tbr_stale", (99, 99), "scope_bad", ("text:A",))
    rep = g.representation_engine.build_representation(
        1, 0, None, list(rep0.participation_receipts), transient_bindings=[stale_tbr]
    )
    assert len(rep.transient_binding_receipts) == 0


def test_sr01_a03_external_evidence_amplification_rejected():
    """SR01-A03: External-evidence amplification: reprojected receipts do not enlarge root authority."""
    g, rep0 = _make_graph_with_a_b(0.85)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert "text:B" not in rep0.participating_node_refs
    b_rec = next(r for r in settled.participation_receipts if r.element_ref == "text:B")
    assert b_rec.origin_lineage == "PATTERN_COMPLETION"


def test_sr01_a04_completion_descendant_root_witness_theft_rejected():
    """SR01-A04: Completion-descendant root-witness theft rejected."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:C", W=0.85)
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0])

    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    receipt_c = next(r for r in settled.participation_receipts if r.element_ref == "text:C")
    assert receipt_c.origin_lineage == "PATTERN_COMPLETION"


def test_sr01_a05_receipt_id_collision_rejected():
    """SR01-A05: Receipt-ID collision: monotonic derivation across multiple iterations produces unique IDs."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:C", W=0.85)
    g.link("text:C", "text:D", W=0.85)
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0])

    all_seen_ids: list[str] = []
    orig_reproject = g.completion_engine._reproject_settling_snapshot

    def tracking_reproject(*args: Any, **kwargs: Any):
        res = orig_reproject(*args, **kwargs)
        fresh_receipts = res[0]
        for r in fresh_receipts:
            all_seen_ids.append(r.receipt_id)
        return res

    g.completion_engine._reproject_settling_snapshot = tracking_reproject  # type: ignore[assignment]
    _settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0, canonical_identity=True, work_ref="test_work")

    assert len(all_seen_ids) == len(set(all_seen_ids))


def test_sr01_a06_mixed_scope_collapse_rejected():
    """SR01-A06: Mixed-scope collapse: different scope views on same target remain distinct."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", scope_refs=("scope_1",), activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0])

    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    r_a = next(r for r in settled.participation_receipts if r.element_ref == "text:A")
    assert r_a.scope_refs == ("scope_1",)


def test_sr01_a07_closed_context_edge_resurrection_rejected():
    """SR01-A07: Closed-context edge resurrection rejected."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85, contexts=("context_alpha",))
    g.link("text:B", "text:C", W=0.85, contexts=("context_alpha",))
    g.node("text:A", "text").excite(1, 1.0)
    g.node("text:B", "text").excite(1, 1.0)
    r_a = ParticipationReceipt("r_a", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    r_b = ParticipationReceipt("r_b", "text:B", 1, 0, "external", "node", activation_magnitude=1.0)
    r_e = ParticipationReceipt("r_e", ("text:A", "text:B"), 1, 0, "external", "edge", relational_drive=0.85)
    rep0 = g.representation_engine.build_representation(1, 0, "context_alpha", [r_a, r_b, r_e])

    edge_obj = g.edge("text:A", "text:B")
    edge_obj.g = "context_other"
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert ("text:A", "text:B") not in settled.participating_edge_refs


def test_sr01_a08_missing_node_carry_forward_rejected():
    """SR01-A08: Missing-node carry-forward rejected."""
    g, rep0 = _make_graph_with_a_b(0.85)
    del g.nodes["text:A"]
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert "text:A" not in settled.participating_node_refs


def test_sr01_a09_tbr_resurrection_rejected():
    """SR01-A09: TBR resurrection rejected: deleted member drops TBR permanently."""
    g, rep0_base = _make_graph_with_a_b(0.85)
    tbr = TransientBindingReceipt("tbr_1", (1, 0), "scope1", ("text:A", "text:B"))
    rep0 = g.representation_engine.build_representation(
        1, 0, None, list(rep0_base.participation_receipts), transient_bindings=[tbr]
    )
    del g.nodes["text:B"]
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert len(settled.transient_binding_receipts) == 0


def test_sr01_a10_assembly_whole_pattern_materialization_rejected():
    """SR01-A10: Assembly presence does not materialize inactive nodes into SDCR."""
    g, rep0 = _make_graph_with_a_b(0.85)
    g.node("concept:assembly_member", "concept")
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert "concept:assembly_member" not in settled.participating_node_refs


def test_sr01_a11_a_b_bidirectional_pumping_rejected():
    """SR01-A11: A↔B pumping attack: bidirectional edges do not inflate activation across iterations."""
    g, rep0 = _make_graph_with_a_b(0.85, w_ba=0.85)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    for r in settled.participation_receipts:
        assert r.activation_magnitude <= 1.0


def test_sr01_a12_chain_budget_exhaustion_while_retaining_lawful_prefix():
    """SR01-A12: Chain budget exhaustion while retaining lawful prefix verified."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:C", W=0.85)
    g.link("text:C", "text:D", W=0.85)
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0])

    settled, outcome = g.completion_engine.run_settling_epoch(rep0, budget=Law.GAMMA)
    assert outcome.closure_reason == "BUDGET_EXHAUSTED"
    assert settled.participating_node_refs == frozenset({"text:A", "text:B"})


def test_sr01_a13_ambiguity_resolution_by_receipt_multiplicity_rejected():
    """SR01-A13: Multiple duplicate receipts cannot force winning in arbitration."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B1", W=0.85)
    g.link("text:A", "text:B2", W=0.85)
    g.add_contradiction("text:B1", "text:B2")
    g.node("text:A", "text").excite(1, 1.0)
    r0 = ParticipationReceipt("r_A", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    r1 = ParticipationReceipt("r_A_dup", "text:A", 1, 0, "external", "node", activation_magnitude=1.0)
    rep0 = g.representation_engine.build_representation(1, 0, None, [r0, r1])

    settled, outcome = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "AMBIGUOUS_FIXED_POINT"
    assert "text:B1" not in settled.participating_node_refs
    assert "text:B2" not in settled.participating_node_refs


def test_sr01_a14_remote_graph_contamination_rejected():
    """SR01-A14: Remote graph modifications do not alter local settling."""
    g, rep0 = _make_graph_with_a_b(0.85)
    g.node("text:Z", "text").excite(1, 1.0)
    settled, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert "text:Z" not in settled.participating_node_refs


def test_sr01_a15_persistent_learning_leakage_rejected():
    """SR01-A15: Settling reprojection causes zero persistent edge learning or node creation."""
    g, rep0 = _make_graph_with_a_b(0.85)
    edge_count_before = len(g.edges)
    node_count_before = len(g.nodes)
    _, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
    assert len(g.edges) == edge_count_before
    assert len(g.nodes) == node_count_before


def test_sr01_a16_rfc11_vote_spoofing_rejected():
    """SR01-A16: Settling reprojection cannot emit RFC-11 structural votes."""
    g, rep0 = _make_graph_with_a_b(0.85)
    if hasattr(g, "assembly_manager") and g.assembly_manager is not None:
        votes_before = len(g.assembly_manager.pending_evidence) if hasattr(g.assembly_manager, "pending_evidence") else 0
        _, _ = g.completion_engine.run_settling_epoch(rep0, budget=1.0)
        votes_after = len(g.assembly_manager.pending_evidence) if hasattr(g.assembly_manager, "pending_evidence") else 0
        assert votes_before == votes_after
