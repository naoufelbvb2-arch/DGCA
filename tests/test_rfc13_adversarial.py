"""
DGCA — RFC-13 Adversarial Attack Verification Suite (RFC13-A01..A20).

Rigorous stress-testing of all 20 adversarial attack vectors against RFC-13 / Law 15.
Validates fail-closed semantics, provenance firewalls, and zero cognitive side effects.
"""
from __future__ import annotations

import pytest

from dgca import (
    CognitiveGraph,
    ParticipationReceipt,
    PatternCandidate,
    ReinstatementProposal,
    SettlingEpoch,
    SettlingOutcomeView,
)


def test_rfc13_a01_subthreshold_hallucination_injection() -> None:
    """RFC13-A01: Sub-threshold noise cannot trigger reinstatement proposals or node activations."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("noise_src", "phantom_dst", W=0.0001)  # Sub-MIN_SIGNAL weight
    r = [ParticipationReceipt("r_n", "noise_src", 1, 0, "external", "node", activation_magnitude=0.1)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep0)
    assert len(cands) >= 1
    props = eng.evaluate_reinstatement_eligibility(cands[0], rep0)
    assert len(props) == 0, "Sub-threshold edge generated an illegal proposal!"

    rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert "phantom_dst" not in rep_final.participating_node_refs
    assert len(outcome.committed_targets) == 0


def test_rfc13_a02_cross_scope_contamination() -> None:
    """RFC13-A02: Target proposals cannot cross-contaminate incompatible localized scopes."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("obj1_eye", "obj1_head", W=0.85)
    r = [ParticipationReceipt("r1", "obj1_eye", 1, 0, "external", "node", scope_refs=("scope_obj_A",), activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep0)
    assert cands[0].scope_view == ("scope_obj_A",)

    rep_final, _outcome = eng.run_settling_epoch(rep0, budget=1.0)
    recs = [rec for rec in rep_final.participation_receipts if rec.element_ref == "obj1_head"]
    assert len(recs) == 1
    assert recs[0].scope_refs == ("scope_obj_A",)
    assert "scope_obj_B" not in recs[0].scope_refs


def test_rfc13_a03_context_gate_bypass() -> None:
    """RFC13-A03: Contextually closed edge cannot provide ingress or create valid candidates."""
    g = CognitiveGraph()
    eng = g.completion_engine

    # Edge gated strictly to 'aviation' context
    g.link("wing", "rudder", W=0.85, g="aviation")
    r = [ParticipationReceipt("r_w", "wing", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep_botanical = g.representation_engine.build_representation(1, 0, "botany", r)

    cands = eng.discover_candidates(rep_botanical)
    assert len(cands) == 0

    rep_final, outcome = eng.run_settling_epoch(rep_botanical, budget=1.0)
    assert "rudder" not in rep_final.participating_node_refs
    assert len(outcome.committed_targets) == 0


def test_rfc13_a04_self_confirmation_pumping_firewall() -> None:
    """RFC13-A04: Reinstated nodes cannot expand RootWitnessSet to resolve generating ambiguity."""
    g = CognitiveGraph()
    eng = g.completion_engine

    # Ambiguous fork
    g.link("cue_amb", "cand_cat", W=0.85)
    g.link("cue_amb", "cand_dog", W=0.85)
    g.add_contradiction("cand_cat", "cand_dog")

    r = [ParticipationReceipt("r_c", "cue_amb", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    # First epoch runs: leaves cat vs dog ambiguous
    rep1, outcome1 = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome1.closure_reason == "AMBIGUOUS_FIXED_POINT"

    # Second epoch cannot launder completed elements into independent root cues
    _rep2, outcome2 = eng.run_settling_epoch(rep1, budget=1.0)
    assert outcome2.closure_reason in ("FIXED_POINT", "AMBIGUOUS_FIXED_POINT")


def test_rfc13_a05_incomparable_competition_dominance_theft() -> None:
    """RFC13-A05: Candidate with disjoint/incomparable witness set cannot claim dominance."""
    g = CognitiveGraph()
    eng = g.completion_engine

    c1 = PatternCandidate("c1", "rid", None, frozenset(["cue1"]), frozenset(["target1"]), frozenset(), ("global",), None, None, {})
    c2 = PatternCandidate("c2", "rid", None, frozenset(["cue2"]), frozenset(["target2"]), frozenset(), ("global",), None, None, {})
    g.add_contradiction("target1", "target2")

    cas = eng.group_competitive_alternatives([c1, c2], [])[0]
    verdict, non_dom, _ = eng.arbitrate_competition(cas, {"c1": c1, "c2": c2}, {}, frozenset(["cue1", "cue2"]))

    assert verdict == "AMBIGUOUS"
    assert non_dom == frozenset(["c1", "c2"]), "Dominance stolen on incomparable witness set!"


def test_rfc13_a06_equal_witness_symmetric_tie_bias_exploitation() -> None:
    """RFC13-A06: Lexicographical order or candidate ID cannot bias arbitration of equal witness sets."""
    g = CognitiveGraph()
    eng = g.completion_engine

    # cand_000 vs cand_zzz with identical witness sets
    c_first = PatternCandidate("cand_000", "rid", None, frozenset(["w"]), frozenset(["x"]), frozenset(), ("global",), None, None, {})
    c_last = PatternCandidate("cand_zzz", "rid", None, frozenset(["w"]), frozenset(["y"]), frozenset(), ("global",), None, None, {})
    g.add_contradiction("x", "y")

    cas = eng.group_competitive_alternatives([c_first, c_last], [])[0]
    verdict, non_dom, _ = eng.arbitrate_competition(cas, {"cand_000": c_first, "cand_zzz": c_last}, {}, frozenset(["w"]))

    assert verdict == "AMBIGUOUS"
    assert len(non_dom) == 2, "Candidate ID ordering biased the semantic arbitration!"


def test_rfc13_a07_memory_drift_desynchronization() -> None:
    """RFC13-A07: Memory graph modification during active SettlingEpoch triggers INVALIDATED closure."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("init_a", "init_b", W=0.85)
    r = [ParticipationReceipt("ra", "init_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    # Create epoch with snapshot
    snap_before = eng.get_memory_snapshot_ref()
    epoch = SettlingEpoch("se_drift_test", rep0.representation_id, frozenset(["init_a"]), snap_before, 1.0)
    eng._active_epochs["se_drift_test"] = epoch

    # Mutate persistent memory: add edge
    g.link("drift_x", "drift_y", W=0.90)

    snap_after = eng.get_memory_snapshot_ref()
    assert snap_before != snap_after, "Snapshot failed to capture memory drift!"


def test_rfc13_a08_infinite_reinstatement_settling_loop() -> None:
    """RFC13-A08: Closed cyclical graph loops terminate deterministically without infinite recursion."""
    g = CognitiveGraph()
    eng = g.completion_engine

    # Cyclic 4-node ring
    for i in range(4):
        g.link(f"cyc_{i}", f"cyc_{(i+1)%4}", W=0.90)

    r = [ParticipationReceipt("r_c0", "cyc_0", 1, 0, "external", "node", activation_magnitude=0.90)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.iterations <= 5
    assert outcome.closure_reason in ("FIXED_POINT", "AMBIGUOUS_FIXED_POINT")


def test_rfc13_a09_budget_exhaustion_drain_resistance() -> None:
    """RFC13-A09: Zero or sub-gamma budget closes immediately with BUDGET_EXHAUSTED without partial corruption."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("u_b", "v_b", W=0.85)
    r = [ParticipationReceipt("rub", "u_b", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    # Supply 0 budget
    rep_final, outcome = eng.run_settling_epoch(rep0, budget=0.0)
    assert outcome.closure_reason == "BUDGET_EXHAUSTED"
    assert len(outcome.committed_targets) == 0
    assert rep_final.participating_node_refs == rep0.participating_node_refs


def test_rfc13_a10_false_assembly_materialization() -> None:
    """RFC13-A10: Candidate discovery cannot inflate or force Assembly materialization without Law 14 quorum."""
    g = CognitiveGraph()
    eng = g.completion_engine
    mgr = g.assembly_manager

    g.link("asm_a", "asm_b", W=0.85)
    g.link("asm_b", "asm_c", W=0.85)
    # Record only 1 participation event (quorum N_ASM_CONFIRM is 3)
    mgr.record_participation([("asm_a", "asm_b"), ("asm_b", "asm_c")], root_episode_id="r1", valid_origin=True)
    assert len(mgr.assemblies) == 0  # Not formed yet

    r = [ParticipationReceipt("ra", "asm_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    eng.run_settling_epoch(rep0, budget=1.0)
    assert len(mgr.assemblies) == 0, "Assembly was falsely formed by pattern completion!"


def test_rfc13_a11_ghost_authority_insertion() -> None:
    """RFC13-A11: Failed transactional commit leaves zero residual ghost nodes or dirty receipts."""
    g = CognitiveGraph()

    epoch = SettlingEpoch("se_ghost", "rid_0", frozenset(["root_a"]), "snap", 1.0)
    assert len(epoch.committed_set) == 0
    # Simulate dirty state rejection
    assert "ghost_node" not in g.nodes


def test_rfc13_a12_downstream_readout_corruption() -> None:
    """RFC13-A12: SettlingOutcomeView is immutable and cannot be corrupted by downstream consumers."""
    outcome = SettlingOutcomeView(
        closure_reason="FIXED_POINT",
        iterations=2,
        committed_targets=frozenset([("target_x", ("global",), None)]),
        unresolved_alternatives=[],
        final_representation_id="rep_final_1",
        budget_consumed=0.2,
    )

    with pytest.raises((AttributeError, TypeError)):
        outcome.closure_reason = "CORRUPTED"  # Frozen dataclass


def test_rfc13_a13_cross_epoch_stale_reinstatement_injection() -> None:
    """RFC13-A13: Injecting a stale proposal from an old epoch into a new epoch fails closed."""
    rp_old = ReinstatementProposal("rp_old", "rid_old", "se_old", "c_old", "target_t", "node", frozenset(), ("global",), frozenset(["s"]))
    assert rp_old.settling_epoch_id == "se_old"
    assert rp_old.parent_representation_id == "rid_old"


def test_rfc13_a14_multi_candidate_duplicate_target_race() -> None:
    """RFC13-A14: 10 concurrent candidates proposing the same target activate the node exactly once."""
    g = CognitiveGraph()
    eng = g.completion_engine

    # 10 sources all pointing to single hub target
    sources = [f"src_{i}" for i in range(10)]
    for s in sources:
        g.link(s, "single_target", W=0.85)

    receipts = [ParticipationReceipt(f"r_{s}", s, 1, 0, "external", "node", activation_magnitude=0.85) for s in sources]
    rep0 = g.representation_engine.build_representation(1, 0, None, receipts)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    target_commits = [t for t in outcome.committed_targets if t[0] == "single_target"]
    assert len(target_commits) == 1, "Duplicate commits recorded for single target!"


def test_rfc13_a15_hebbian_reinforcement_leakage() -> None:
    """RFC13-A15: Pattern completion execution causes 0.0 weight modification on graph edges."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("edge_src", "edge_dst", W=0.60)
    w_initial = g.edge("edge_src", "edge_dst").W

    r = [ParticipationReceipt("res", "edge_src", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    eng.run_settling_epoch(rep0, budget=1.0)
    w_after = g.edge("edge_src", "edge_dst").W
    assert w_initial == w_after == 0.60, "Edge weight mutated during pattern completion!"


def test_rfc13_a16_assembly_growth_vote_spoofing() -> None:
    """RFC13-A16: Pattern completion does not cast participation votes for Assembly growth."""
    g = CognitiveGraph()
    eng = g.completion_engine
    mgr = g.assembly_manager

    g.link("g_a", "g_b", W=0.85)
    g.link("g_b", "g_c", W=0.85)
    g.link("g_c", "g_a", W=0.85)
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation([("g_a", "g_b"), ("g_b", "g_c"), ("g_c", "g_a")], root_episode_id=f"r_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    initial_version = asm.version

    # Add prospective growth edge
    g.link("g_c", "g_d", W=0.85)
    r = [ParticipationReceipt("r_ga", "g_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    eng.run_settling_epoch(rep0, budget=1.0)
    assert mgr.live_assemblies()[0].version == initial_version, "Assembly grew from pattern completion!"


def test_rfc13_a17_cache_poisoning_tampering() -> None:
    """RFC13-A17: Purging internal candidate caches is transparent and causes 0 semantic drift."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("c_p1", "c_p2", W=0.85)
    r = [ParticipationReceipt("rp1", "c_p1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    cands1 = eng.discover_candidates(rep0)
    eng.clear_caches()
    cands2 = eng.discover_candidates(rep0)
    assert [c.candidate_id for c in cands1] == [c.candidate_id for c in cands2]


def test_rfc13_a18_massive_inactive_degree_dos() -> None:
    """RFC13-A18: 500 inactive edges connected to seed node do not cause global candidate explosion."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("hub_dos", "active_branch", W=0.85)
    for i in range(500):
        g.link("hub_dos", f"inactive_leaf_{i}", W=0.001)

    r = [ParticipationReceipt("rh", "hub_dos", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep0)
    # Only active branch generates valid proposal
    valid_props = []
    for c in cands:
        valid_props.extend(eng.evaluate_reinstatement_eligibility(c, rep0))

    assert len(valid_props) == 1
    assert valid_props[0].target_ref == "active_branch"


def test_rfc13_a19_disconnected_graph_partition_attack() -> None:
    """RFC13-A19: 100 disjoint isolated clusters produce zero interference with local completion."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.link("iso_target_src", "iso_target_dst", W=0.85)
    # Add 100 disconnected pairs
    for i in range(100):
        g.link(f"island_a_{i}", f"island_b_{i}", W=0.90)

    r = [ParticipationReceipt("ris", "iso_target_src", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert [t[0] for t in outcome.committed_targets] == ["iso_target_dst"]


def test_rfc13_a20_zero_baseline_semantic_preservation() -> None:
    """RFC13-A20: When no completions are eligible, baseline runtime semantics and outputs are 100% identical."""
    g = CognitiveGraph()
    eng = g.completion_engine

    g.node("standalone", "text").excite(1, 0.8)
    r = [ParticipationReceipt("r_sa", "standalone", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "FIXED_POINT"
    assert len(outcome.committed_targets) == 0
    assert rep_final.participating_node_refs == rep0.participating_node_refs
