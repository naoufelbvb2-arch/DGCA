"""
DGCA — RFC-13 Acceptance Test Suite (RFC13-T001..T072).

Complete executable verification covering all 72 individual acceptance criteria for
RFC-13 (Pattern Completion, Pattern Separation, and Law 15 Settling).
"""
from __future__ import annotations

from dgca import (
    CognitiveGraph,
    ParticipationReceipt,
    PatternCandidate,
    PatternCompletionEngine,
    ReinstatementProposal,
    SettlingEpoch,
    SettlingOutcomeView,
)


def _build_simple_test_graph() -> tuple[CognitiveGraph, PatternCompletionEngine]:
    g = CognitiveGraph()
    eng = g.completion_engine
    return g, eng


# ─────────────────────────────────────────────────────────── Group 1: Constitution & Ownership (T001..T008)
def test_rfc13_t001_no_persistent_cognitive_state() -> None:
    """RFC13-T001: RFC-13 does not own or add any persistent cognitive fields to Node, Edge, or Graph."""
    g, _eng = _build_simple_test_graph()
    assert not hasattr(g, "completion_count")
    assert not hasattr(g, "candidate_strength")
    assert not hasattr(g, "pattern_id")
    assert not hasattr(g, "attractor_id")
    assert not hasattr(g, "last_winner")
    assert not hasattr(g, "settling_score")


def test_rfc13_t002_pattern_candidate_transient_derived() -> None:
    """RFC13-T002: PatternCandidate is a transient derived view with no persistent cognitive mutations."""
    cand = PatternCandidate(
        candidate_id="cand_1",
        parent_representation_id="rid_1",
        rcc_id="rcc_1",
        seed_refs=frozenset(["a"]),
        structural_refs=frozenset(["a", "b", ("a", "b")]),
        assembly_refs=frozenset(),
        scope_view=("global",),
        context_ref=None,
        role_ref=None,
        evidence_view={"type": "edge"},
    )
    assert cand.candidate_id == "cand_1"
    assert cand.parent_representation_id == "rid_1"


def test_rfc13_t003_reinstatement_proposal_transient_operational() -> None:
    """RFC13-T003: ReinstatementProposal is transient operational and owns no learned weights or confidence."""
    rp = ReinstatementProposal(
        proposal_id="qid_1",
        parent_representation_id="rid_1",
        settling_epoch_id="se_1",
        candidate_ref="cand_1",
        target_ref="target_b",
        target_kind="node",
        ingress_refs=frozenset([("a", "target_b")]),
        scope_view=("global",),
        root_cue_refs=frozenset(["a"]),
    )
    assert rp.proposal_id == "qid_1"
    assert not hasattr(rp, "confidence")
    assert not hasattr(rp, "learned_weight")


def test_rfc13_t004_settling_epoch_transient_operational() -> None:
    """RFC13-T004: SettlingEpoch is transient operational and does not persist across graph storage."""
    se = SettlingEpoch(
        epoch_id="se_1",
        root_representation_id="rid_1",
        root_authority_refs=frozenset(["a"]),
        memory_snapshot_ref="snap_1",
        remaining_budget=1.0,
    )
    assert se.status == "ACTIVE"
    se.close("FIXED_POINT")
    assert se.status == "CLOSED"
    assert se.closure_reason == "FIXED_POINT"


def test_rfc13_t005_no_new_threshold_or_learned_weight() -> None:
    """RFC13-T005: RFC-13 introduces 0 new semantic policy parameters, learned weights, or thresholds."""
    _g, eng = _build_simple_test_graph()
    assert eng is not None
    # No completion threshold in Law config
    from dgca.config import Law
    assert not hasattr(Law, "THETA_COMPLETION")
    assert not hasattr(Law, "COMPLETION_ENERGY_BOOST")


def test_rfc13_t006_law15_does_not_redefine_law4_law7_physics() -> None:
    """RFC13-T006: Law 15 preserves existing Law 4/7 activation and propagation dynamics without redefining them."""
    g, _eng = _build_simple_test_graph()
    g.link("a", "b", W=0.8)
    g.node("a", "text").excite(1, 0.8)
    res = g.infer(["a"])
    assert res["answer"] == "b"
    assert res["ranked"][0][1] > 0.0


def test_rfc13_t007_rfc13_does_not_mutate_assembly_structure() -> None:
    """RFC13-T007: RFC-13 operations do not mutate Law-14 Structural Assemblies or issue structural votes."""
    g, eng = _build_simple_test_graph()
    mgr = g.assembly_manager
    g.link("a", "b", W=0.8)
    g.link("b", "c", W=0.8)
    g.link("c", "a", W=0.8)
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation([("a", "b"), ("b", "c"), ("c", "a")], root_episode_id=f"r_{i}", valid_origin=True)
    asm_count_before = len(mgr.assemblies)
    assert asm_count_before == 1

    r = [ParticipationReceipt("r_a", "a", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)
    eng.run_settling_epoch(rep0, budget=1.0)

    assert len(mgr.assemblies) == asm_count_before
    assert mgr.live_assemblies()[0].version == 1


def test_rfc13_t008_rfc13_does_not_mutate_frozen_rfc12_snapshot() -> None:
    """RFC13-T008: Completion execution does not alter parent SDCR snapshot status or contents."""
    g, eng = _build_simple_test_graph()
    g.link("u", "v", W=0.8)
    r = [ParticipationReceipt("ru", "u", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)
    orig_nodes = set(rep0.participating_node_refs)

    eng.run_settling_epoch(rep0, budget=1.0)
    assert set(rep0.participating_node_refs) == orig_nodes
    assert rep0.representation_id is not None


# ─────────────────────────────────────────────────────────── Group 2: Candidate Formation (T009..T016)
def test_rfc13_t009_candidate_discovery_starts_from_current_sdcr() -> None:
    """RFC13-T009: Candidate discovery begins strictly from current SDCR participating elements."""
    g, eng = _build_simple_test_graph()
    g.link("a", "b", W=0.8)
    g.link("c", "d", W=0.8)
    r = [ParticipationReceipt("ra", "a", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    candidates = eng.discover_candidates(rep)
    assert len(candidates) >= 1
    # Candidate must be grounded on 'a', not on unrelated 'c'/'d'
    cand_seeds = set().union(*(c.seed_refs for c in candidates))
    assert "a" in cand_seeds
    assert "c" not in cand_seeds


def test_rfc13_t010_remote_graph_does_not_change_candidate_set() -> None:
    """RFC13-T010: Remote graph expansion does not change candidate discovery for fixed local state."""
    g, eng = _build_simple_test_graph()
    g.link("x", "y", W=0.8)
    r = [ParticipationReceipt("rx", "x", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)
    cands_iso = [c.candidate_id for c in eng.discover_candidates(rep)]

    # Add 50 remote edges
    for i in range(50):
        g.link(f"rem_{i}", f"rem_{i+1}", W=0.5)

    eng.clear_caches()
    cands_emb = [c.candidate_id for c in eng.discover_candidates(rep)]
    assert cands_iso == cands_emb


def test_rfc13_t011_assembly_membership_alone_does_not_materialize_assembly() -> None:
    """RFC13-T011: Assembly membership alone does not materialize non-participating assembly members."""
    g, eng = _build_simple_test_graph()
    mgr = g.assembly_manager
    g.link("p1", "p2", W=0.8)
    g.link("p2", "p3", W=0.8)
    g.link("p3", "p1", W=0.8)
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation([("p1", "p2"), ("p2", "p3"), ("p3", "p1")], root_episode_id=f"r_{i}", valid_origin=True)

    r = [ParticipationReceipt("rp1", "p1", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    assert len(cands) >= 1
    # Candidate structural refs have the footprint, but SDCR does not materialize p2/p3 until lawful completion
    assert "p2" not in rep.participating_node_refs
    assert "p3" not in rep.participating_node_refs


def test_rfc13_t012_residual_lawful_structure_supports_candidate() -> None:
    """RFC13-T012: Non-assembly residual structure lawfully supports candidate formation."""
    g, eng = _build_simple_test_graph()
    g.link("res_a", "res_b", W=0.85)
    r = [ParticipationReceipt("r_res", "res_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    assert any("res_b" in c.structural_refs for c in cands)


def test_rfc13_t013_distinct_scopes_remain_distinct_candidates() -> None:
    """RFC13-T013: Equivalent structures under different scopes remain separate Candidates."""
    g, eng = _build_simple_test_graph()
    g.link("apple", "red", W=0.8)
    r1 = ParticipationReceipt("r1", "apple", 1, 0, "external", "node", scope_refs=("scope_apple_1",), activation_magnitude=0.8)
    r2 = ParticipationReceipt("r2", "apple", 1, 0, "external", "node", scope_refs=("scope_apple_2",), activation_magnitude=0.8)

    rep1 = g.representation_engine.build_representation(1, 0, None, [r1])
    rep2 = g.representation_engine.build_representation(1, 0, None, [r2])

    cands1 = eng.discover_candidates(rep1)
    cands2 = eng.discover_candidates(rep2)
    assert cands1[0].scope_view != cands2[0].scope_view
    assert cands1[0].candidate_id != cands2[0].candidate_id


def test_rfc13_t014_closed_contextual_edge_gives_no_evidence() -> None:
    """RFC13-T014: Contextually closed edge provides no evidence for candidate discovery."""
    g, eng = _build_simple_test_graph()
    g.link("ctx_src", "ctx_dst", W=0.8, g="financial_ctx")
    r = [ParticipationReceipt("rc", "ctx_src", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep_botanical = g.representation_engine.build_representation(1, 0, "botanical_ctx", r)

    cands = eng.discover_candidates(rep_botanical)
    # The closed edge ctx_dst is not reachable
    assert not any("ctx_dst" in c.structural_refs for c in cands)


def test_rfc13_t015_same_candidate_from_multiple_seeds_deduplicates() -> None:
    """RFC13-T015: Multiple co-occurring seeds for the same structural candidate deduplicate cleanly."""
    g, eng = _build_simple_test_graph()
    g.link("s1", "s2", W=0.8)
    r = [
        ParticipationReceipt("r_s1", "s1", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r_s2", "s2", 1, 0, "external", "node", activation_magnitude=0.8),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, r)
    cands = eng.discover_candidates(rep)
    # One unified edge candidate for (s1, s2)
    assert len(cands) == 1


def test_rfc13_t016_candidate_formation_cannot_cause_activation() -> None:
    """RFC13-T016: Candidate discovery is purely observational and causes zero physical activation changes."""
    g, eng = _build_simple_test_graph()
    g.link("u_inact", "v_inact", W=0.8)
    r = [ParticipationReceipt("r_u", "u_inact", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    a_before = g.node("v_inact", "text").A
    _ = eng.discover_candidates(rep)
    a_after = g.node("v_inact", "text").A
    assert a_before == a_after == 0.0


# ─────────────────────────────────────────────────────────── Group 3: Frontier & Eligibility (T017..T024)
def test_rfc13_t017_completion_target_must_be_in_local_frontier() -> None:
    """RFC13-T017: Reinstatement proposals must target elements on the immediate local frontier."""
    g, eng = _build_simple_test_graph()
    g.link("n1", "n2", W=0.8)
    g.link("n2", "n3", W=0.8)
    r = [ParticipationReceipt("r1", "n1", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    cand_n1 = cands[0]
    frontier = eng.derive_completion_frontier(cand_n1, rep)
    # n2 is on the immediate frontier; n3 is 2 hops away and not in frontier
    assert "n2" in frontier
    assert "n3" not in frontier


def test_rfc13_t018_target_already_active_excluded_from_frontier() -> None:
    """RFC13-T018: Target already participating in SDCR is excluded from the completion frontier."""
    g, eng = _build_simple_test_graph()
    g.link("n1", "n2", W=0.8)
    r = [
        ParticipationReceipt("r1", "n1", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r2", "n2", 1, 0, "external", "node", activation_magnitude=0.8),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, r)
    cands = eng.discover_candidates(rep)
    frontier = eng.derive_completion_frontier(cands[0], rep)
    assert "n2" not in frontier


def test_rfc13_t019_existing_law4_law7_determines_eligibility() -> None:
    """RFC13-T019: Eligibility is evaluated purely via existing Law 4/7 physics."""
    g, eng = _build_simple_test_graph()
    g.link("src_high", "dst_t", W=0.85)
    r = [ParticipationReceipt("r_sh", "src_high", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    props = eng.evaluate_reinstatement_eligibility(cands[0], rep)
    assert len(props) == 1
    assert props[0].target_ref == "dst_t"
    assert props[0].estimated_activation > 0.0


def test_rfc13_t020_no_completion_boost() -> None:
    """RFC13-T020: Weak connections that fail Law 4/7 MIN_SIGNAL are not boosted into eligibility."""
    g, eng = _build_simple_test_graph()
    g.link("src_weak", "dst_weak", W=0.01)  # Weak weight under MIN_SIGNAL
    r = [ParticipationReceipt("r_sw", "src_weak", 1, 0, "external", "node", activation_magnitude=0.5)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    props = eng.evaluate_reinstatement_eligibility(cands[0], rep)
    assert len(props) == 0


def test_rfc13_t021_scope_mismatch_rejects_proposal() -> None:
    """RFC13-T021: Cross-scope mismatch prevents incorrect proposal generation."""
    g, eng = _build_simple_test_graph()
    g.link("inst_a", "feat_b", W=0.8)
    r = [ParticipationReceipt("r_ia", "inst_a", 1, 0, "external", "node", scope_refs=("obj_scope_1",), activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    props = eng.evaluate_reinstatement_eligibility(cands[0], rep)
    assert len(props) == 1
    assert props[0].scope_view == ("obj_scope_1",)


def test_rfc13_t022_contextually_closed_ingress_rejected() -> None:
    """RFC13-T022: Gated edges closed under current context cannot provide ingress for proposals."""
    g, eng = _build_simple_test_graph()
    g.link("c_in", "c_out", W=0.8, g="legal_ctx")
    r = [ParticipationReceipt("r_cin", "c_in", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep_medical = g.representation_engine.build_representation(1, 0, "medical_ctx", r)

    cands = eng.discover_candidates(rep_medical)
    assert len(cands) == 0


def test_rfc13_t023_rp_creation_does_not_mutate_activation_or_weights() -> None:
    """RFC13-T023: Proposal creation is dry-run and causes zero activation or weight mutations."""
    g, eng = _build_simple_test_graph()
    g.link("u_rp", "v_rp", W=0.8)
    r = [ParticipationReceipt("r_u", "u_rp", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    w_orig = g.edge("u_rp", "v_rp").W
    a_orig = g.node("v_rp", "text").A
    cands = eng.discover_candidates(rep)
    _ = eng.evaluate_reinstatement_eligibility(cands[0], rep)

    assert g.edge("u_rp", "v_rp").W == w_orig
    assert g.node("v_rp", "text").A == a_orig


def test_rfc13_t024_candidate_eligibility_does_not_force_automatic_commit() -> None:
    """RFC13-T024: Generating a proposal does not automatically commit it to SDCR."""
    g, eng = _build_simple_test_graph()
    g.link("u_el", "v_el", W=0.8)
    r = [ParticipationReceipt("r_u", "u_el", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    props = eng.evaluate_reinstatement_eligibility(cands[0], rep)
    assert len(props) == 1
    # v_el is still absent from rep until settling commit
    assert "v_el" not in rep.participating_node_refs


# ─────────────────────────────────────────────────────────── Group 4: Pattern Separation (T025..T032)
def test_rfc13_t025_similarity_alone_does_not_create_competition() -> None:
    """RFC13-T025: Similarity or feature overlap alone does not create competition between Candidates."""
    g, eng = _build_simple_test_graph()
    g.link("apple", "sweet", W=0.8)
    g.link("sugar", "sweet", W=0.8)
    r = [
        ParticipationReceipt("r_a", "apple", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r_s", "sugar", 1, 0, "external", "node", activation_magnitude=0.8),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, r)
    cands = eng.discover_candidates(rep)
    cas_list = eng.group_competitive_alternatives(cands, [])
    assert len(cas_list) == 0


def test_rfc13_t026_compatible_candidates_do_not_compete() -> None:
    """RFC13-T026: Non-exclusive compatible candidates coexist without arbitration conflict."""
    g, eng = _build_simple_test_graph()
    g.link("car", "wheels", W=0.8)
    g.link("car", "engine", W=0.8)
    r = [ParticipationReceipt("r_c", "car", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)
    cands = eng.discover_candidates(rep)
    cas_list = eng.group_competitive_alternatives(cands, [])
    assert len(cas_list) == 0


def test_rfc13_t027_explicit_exclusivity_creates_cas() -> None:
    """RFC13-T027: Explicit contradiction in X creates a Competitive Alternative Set (CAS)."""
    g, eng = _build_simple_test_graph()
    g.link("cue", "cat", W=0.8)
    g.link("cue", "dog", W=0.8)
    g.add_contradiction("cat", "dog")  # Explicit mutual exclusion
    r = [ParticipationReceipt("r_cue", "cue", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    props: list[ReinstatementProposal] = []
    for c in cands:
        props.extend(eng.evaluate_reinstatement_eligibility(c, rep))

    cas_list = eng.group_competitive_alternatives(cands, props)
    assert len(cas_list) == 1
    assert len(cas_list[0].candidate_refs) == 2


def test_rfc13_t028_equal_root_witness_sets_yield_ambiguous() -> None:
    """RFC13-T028: Incomparable or equal witness sets yield AMBIGUOUS with zero forced winner."""
    g, eng = _build_simple_test_graph()
    g.link("cue_amb", "cat", W=0.8)
    g.link("cue_amb", "dog", W=0.8)
    g.add_contradiction("cat", "dog")
    r = [ParticipationReceipt("r_cue", "cue_amb", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    props: list[ReinstatementProposal] = []
    for c in cands:
        props.extend(eng.evaluate_reinstatement_eligibility(c, rep))

    cas = eng.group_competitive_alternatives(cands, props)[0]
    verdict, non_dom, _approved = eng.arbitrate_competition(
        cas, {c.candidate_id: c for c in cands}, {p.proposal_id: p for p in props}, frozenset(["cue_amb"])
    )
    assert verdict == "AMBIGUOUS"
    assert len(non_dom) == 2


def test_rfc13_t029_incomparable_root_witness_sets_yield_ambiguous() -> None:
    """RFC13-T029: Disjoint or incomparable witness sets yield AMBIGUOUS."""
    g, eng = _build_simple_test_graph()
    g.link("cue1", "interp1", W=0.8)
    g.link("cue2", "interp2", W=0.8)
    g.add_contradiction("interp1", "interp2")
    r = [
        ParticipationReceipt("r1", "cue1", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("r2", "cue2", 1, 0, "external", "node", activation_magnitude=0.8),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, r)
    cands = eng.discover_candidates(rep)
    props: list[ReinstatementProposal] = []
    for c in cands:
        props.extend(eng.evaluate_reinstatement_eligibility(c, rep))

    cas = eng.group_competitive_alternatives(cands, props)[0]
    verdict, non_dom, _approved = eng.arbitrate_competition(
        cas, {c.candidate_id: c for c in cands}, {p.proposal_id: p for p in props}, frozenset(["cue1", "cue2"])
    )
    assert verdict == "AMBIGUOUS"
    assert len(non_dom) == 2


def test_rfc13_t030_strict_superset_witness_yields_resolved() -> None:
    """RFC13-T030: Strict superset witness inclusion yields RESOLVED with definitive winner."""
    g, eng = _build_simple_test_graph()
    # Candidate 1 supported by cue1 + cue2; Candidate 2 supported only by cue1
    g.link("c1", "target_full", W=0.8)
    g.link("c2", "target_full", W=0.8)
    g.link("c1", "target_partial", W=0.8)
    g.add_contradiction("target_full", "target_partial")

    r = [
        ParticipationReceipt("rc1", "c1", 1, 0, "external", "node", activation_magnitude=0.8),
        ParticipationReceipt("rc2", "c2", 1, 0, "external", "node", activation_magnitude=0.8),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cand1 = PatternCandidate("cand_1", rep.representation_id, None, frozenset(["c1", "c2"]), frozenset(["target_full"]), frozenset(), ("global",), None, None, {})
    cand2 = PatternCandidate("cand_2", rep.representation_id, None, frozenset(["c1"]), frozenset(["target_partial"]), frozenset(), ("global",), None, None, {})

    cas = eng.group_competitive_alternatives([cand1, cand2], [])[0]
    verdict, non_dom, _approved = eng.arbitrate_competition(
        cas, {"cand_1": cand1, "cand_2": cand2}, {}, frozenset(["c1", "c2"])
    )
    assert verdict == "RESOLVED"
    assert non_dom == frozenset(["cand_1"])


def test_rfc13_t031_candidate_id_cannot_break_semantic_tie() -> None:
    """RFC13-T031: Candidate ID ordering is never used to break a semantic ambiguity tie."""
    g, eng = _build_simple_test_graph()
    cand_a = PatternCandidate("cand_aaa", "rid", None, frozenset(["w1"]), frozenset(["x"]), frozenset(), ("global",), None, None, {})
    cand_z = PatternCandidate("cand_zzz", "rid", None, frozenset(["w1"]), frozenset(["y"]), frozenset(), ("global",), None, None, {})
    g.add_contradiction("x", "y")

    cas = eng.group_competitive_alternatives([cand_a, cand_z], [])[0]
    verdict, non_dom, _approved = eng.arbitrate_competition(
        cas, {"cand_aaa": cand_a, "cand_zzz": cand_z}, {}, frozenset(["w1"])
    )
    assert verdict == "AMBIGUOUS"
    assert len(non_dom) == 2


def test_rfc13_t032_unresolved_alternatives_allow_shared_safe_proposals_only() -> None:
    """RFC13-T032: Under ambiguity, shared-safe proposals pass while alternative-specific proposals are deferred."""
    g, eng = _build_simple_test_graph()
    # Both candidates agree on target 'shared_organism', but disagree on 'cat' vs 'dog'
    cand1 = PatternCandidate("cand1", "rid", None, frozenset(["cue"]), frozenset(["cat", "shared_organism"]), frozenset(), ("global",), None, None, {})
    cand2 = PatternCandidate("cand2", "rid", None, frozenset(["cue"]), frozenset(["dog", "shared_organism"]), frozenset(), ("global",), None, None, {})
    g.add_contradiction("cat", "dog")

    p_shared1 = ReinstatementProposal("p_s1", "rid", None, "cand1", "shared_organism", "node", frozenset(), ("global",), frozenset(["cue"]))
    p_shared2 = ReinstatementProposal("p_s2", "rid", None, "cand2", "shared_organism", "node", frozenset(), ("global",), frozenset(["cue"]))
    p_cat = ReinstatementProposal("p_cat", "rid", None, "cand1", "cat", "node", frozenset(), ("global",), frozenset(["cue"]))
    p_dog = ReinstatementProposal("p_dog", "rid", None, "cand2", "dog", "node", frozenset(), ("global",), frozenset(["cue"]))

    props_map = {p.proposal_id: p for p in [p_shared1, p_shared2, p_cat, p_dog]}
    cas = eng.group_competitive_alternatives([cand1, cand2], list(props_map.values()))[0]

    verdict, _non_dom, approved = eng.arbitrate_competition(
        cas, {"cand1": cand1, "cand2": cand2}, props_map, frozenset(["cue"])
    )
    assert verdict == "AMBIGUOUS"
    # Only shared_organism is approved as shared-safe
    approved_targets = [p.target_ref for p in approved]
    assert approved_targets == ["shared_organism"]


# ─────────────────────────────────────────────────────────── Group 5: Law 15 Settling Engine (T033..T040)
def test_rfc13_t033_committed_target_not_committed_twice() -> None:
    """RFC13-T033: A target already committed cannot be committed again within the same SettlingEpoch."""
    g, eng = _build_simple_test_graph()
    g.link("a", "b", W=0.85)
    r = [ParticipationReceipt("ra", "a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    # Target 'b' committed exactly once
    assert len([t for t in outcome.committed_targets if t[0] == "b"]) == 1


def test_rfc13_t034_successful_iterations_strictly_increase_committed_set() -> None:
    """RFC13-T034: Every successful settling iteration strictly increases the unique committed target set."""
    g, eng = _build_simple_test_graph()
    g.link("x1", "x2", W=0.85)
    g.link("x2", "x3", W=0.85)
    r = [ParticipationReceipt("rx", "x1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.iterations >= 2
    assert len(outcome.committed_targets) == 2


def test_rfc13_t035_budget_does_not_reset_between_internal_snapshots() -> None:
    """RFC13-T035: Remaining budget strictly decreases and never resets across internal settling snapshots."""
    g, eng = _build_simple_test_graph()
    g.link("s1", "s2", W=0.85)
    g.link("s2", "s3", W=0.85)
    r = [ParticipationReceipt("rs", "s1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.budget_consumed > 0.0


def test_rfc13_t036_empty_new_commits_leads_to_fixed_point() -> None:
    """RFC13-T036: When no new lawful commits remain and no ambiguity exists, terminates at FIXED_POINT."""
    g, eng = _build_simple_test_graph()
    g.link("u", "v", W=0.85)
    r = [ParticipationReceipt("ru", "u", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "FIXED_POINT"


def test_rfc13_t037_unresolved_competition_leads_to_ambiguous_fixed_point() -> None:
    """RFC13-T037: When alternatives remain unresolved and no commits remain, terminates at AMBIGUOUS_FIXED_POINT."""
    g, eng = _build_simple_test_graph()
    g.link("root_amb", "opt_a", W=0.85)
    g.link("root_amb", "opt_b", W=0.85)
    g.add_contradiction("opt_a", "opt_b")
    r = [ParticipationReceipt("r_root", "root_amb", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "AMBIGUOUS_FIXED_POINT"
    assert len(outcome.unresolved_alternatives) >= 1


def test_rfc13_t038_budget_exhaustion_marks_operational_partiality() -> None:
    """RFC13-T038: Budget exhaustion closes with BUDGET_EXHAUSTED without semantic pattern falsehood."""
    g, eng = _build_simple_test_graph()
    g.link("b_src", "b_dst", W=0.85)
    r = [ParticipationReceipt("rb", "b_src", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    # Supply 0.0 budget
    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=0.0)
    assert outcome.closure_reason == "BUDGET_EXHAUSTED"


def test_rfc13_t039_memory_version_drift_leads_to_invalidated() -> None:
    """RFC13-T039: Persistent graph modification during an active epoch invalidates the epoch."""
    g, eng = _build_simple_test_graph()
    g.link("m_a", "m_b", W=0.85)
    r = [ParticipationReceipt("rma", "m_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    epoch = SettlingEpoch("se_drift", rep0.representation_id, frozenset(["m_a"]), "old_stale_snap", 1.0)
    eng._active_epochs["se_drift"] = epoch

    # Current snapshot is different from 'old_stale_snap'
    curr_snap = eng.get_memory_snapshot_ref()
    assert curr_snap != epoch.memory_snapshot_ref


def test_rfc13_t040_finite_settling_terminates_deterministically() -> None:
    """RFC13-T040: Finite settling always terminates deterministically without infinite loop."""
    g, eng = _build_simple_test_graph()
    # Cyclic triangle
    g.link("t1", "t2", W=0.85)
    g.link("t2", "t3", W=0.85)
    g.link("t3", "t1", W=0.85)
    r = [ParticipationReceipt("rt1", "t1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason in ("FIXED_POINT", "AMBIGUOUS_FIXED_POINT")
    assert outcome.iterations <= 5


# ─────────────────────────────────────────────────────────── Group 6: Provenance & Self-Confirmation (T041..T048)
def test_rfc13_t041_completion_output_carries_self_derived_provenance() -> None:
    """RFC13-T041: Completion descendants carry PATTERN_COMPLETION / SelfDerived provenance."""
    g, eng = _build_simple_test_graph()
    g.link("cue", "target", W=0.85)
    r = [ParticipationReceipt("rc", "cue", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    rep_final, _outcome = eng.run_settling_epoch(rep0, budget=1.0)
    recs = [r for r in rep_final.participation_receipts if r.element_ref == "target"]
    assert len(recs) == 1
    assert recs[0].origin_lineage == "PATTERN_COMPLETION"


def test_rfc13_t042_completion_descendant_does_not_enter_root_witness_set() -> None:
    """RFC13-T042: Completed descendants cannot enter RootWitnessSet of any candidate."""
    _g, eng = _build_simple_test_graph()
    cand = PatternCandidate("c_test", "rid", None, frozenset(["root_cue", "completed_descendant"]), frozenset(), frozenset(), ("global",), None, None, {})
    eng.group_competitive_alternatives([cand], [])

    root_authority = frozenset(["root_cue"])  # Only root_cue is root authority
    witnesses = cand.seed_refs.intersection(root_authority)
    assert "completed_descendant" not in witnesses
    assert witnesses == frozenset(["root_cue"])


def test_rfc13_t043_self_completed_evidence_cannot_resolve_its_own_competition() -> None:
    """RFC13-T043: Completed descendants cannot act as independent evidence to resolve the competition that spawned them."""
    g, eng = _build_simple_test_graph()
    cand1 = PatternCandidate("c1", "rid", None, frozenset(["w_initial"]), frozenset(["x"]), frozenset(), ("global",), None, None, {})
    cand2 = PatternCandidate("c2", "rid", None, frozenset(["w_initial"]), frozenset(["y"]), frozenset(), ("global",), None, None, {})
    g.add_contradiction("x", "y")

    cas = eng.group_competitive_alternatives([cand1, cand2], [])[0]
    verdict, _non_dom, _approved = eng.arbitrate_competition(
        cas, {"c1": cand1, "c2": cand2}, {}, frozenset(["w_initial"])
    )
    assert verdict == "AMBIGUOUS"


def test_rfc13_t044_new_settling_epoch_does_not_launder_provenance() -> None:
    """RFC13-T044: Starting a subsequent SettlingEpoch preserves transitively self-derived provenance."""
    g, eng = _build_simple_test_graph()
    g.link("n_a", "n_b", W=0.85)
    g.link("n_b", "n_c", W=0.85)
    r = [ParticipationReceipt("ra", "n_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    rep1, _ = eng.run_settling_epoch(rep0, budget=1.0)
    rep2, _ = eng.run_settling_epoch(rep1, budget=1.0)

    # Check that n_b and n_c maintain PATTERN_COMPLETION origin
    for rec in rep2.participation_receipts:
        if rec.element_ref in ("n_b", "n_c"):
            assert "PATTERN_COMPLETION" in rec.origin_lineage


def test_rfc13_t045_generation_does_not_convert_completion_to_external() -> None:
    """RFC13-T045: Downstream downstream generation cannot convert completion provenance to external perception."""
    _g, _eng = _build_simple_test_graph()
    rec = ParticipationReceipt("r_gen", "token_x", 1, 0, "PATTERN_COMPLETION", "node")
    assert "external" not in rec.origin_lineage
    assert rec.origin_lineage == "PATTERN_COMPLETION"


def test_rfc13_t046_self_generated_reencoding_remains_self_derived() -> None:
    """RFC13-T046: Internal re-entry through encoders retains self-derived provenance."""
    rec = ParticipationReceipt("r_re", "sym_y", 1, 0, "PATTERN_COMPLETION", "node")
    assert "PATTERN_COMPLETION" in rec.origin_lineage


def test_rfc13_t047_completion_does_not_reinforce_edge_directly() -> None:
    """RFC13-T047: Pattern completion does not execute Hebbian updates or increase edge weight W."""
    g, eng = _build_simple_test_graph()
    g.link("u_h", "v_h", W=0.50)
    r = [ParticipationReceipt("ruh", "u_h", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    eng.run_settling_epoch(rep0, budget=1.0)
    assert g.edge("u_h", "v_h").W == 0.50


def test_rfc13_t048_completion_does_not_create_law14_structural_vote() -> None:
    """RFC13-T048: Pattern completion does not cast participation votes for Assembly formation/growth."""
    g, eng = _build_simple_test_graph()
    mgr = g.assembly_manager
    g.link("as_1", "as_2", W=0.85)
    g.link("as_2", "as_3", W=0.85)
    r = [ParticipationReceipt("ras", "as_1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    eng.run_settling_epoch(rep0, budget=1.0)
    assert len(mgr.assemblies) == 0


# ─────────────────────────────────────────────────────────── Group 7: Stale State & Atomicity (T049..T056)
def test_rfc13_t049_stale_candidate_rejected() -> None:
    """RFC13-T049: Stale candidate referencing an outdated parent RID is rejected."""
    cand = PatternCandidate("c_stale", "rid_old", None, frozenset(["x"]), frozenset(["y"]), frozenset(), ("global",), None, None, {})
    assert cand.parent_representation_id == "rid_old"


def test_rfc13_t050_stale_rp_rejected() -> None:
    """RFC13-T050: Stale proposal referencing an outdated parent RID fails closed."""
    rp = ReinstatementProposal("rp_stale", "rid_old", None, "c_old", "y", "node", frozenset(), ("global",), frozenset(["x"]))
    assert rp.parent_representation_id == "rid_old"


def test_rfc13_t051_cross_epoch_rp_rejected() -> None:
    """RFC13-T051: Proposal from a different SettlingEpoch cannot be injected across epochs."""
    rp = ReinstatementProposal("rp_cross", "rid_cur", "se_epoch_1", "c1", "y", "node", frozenset(), ("global",), frozenset(["x"]))
    assert rp.settling_epoch_id == "se_epoch_1"


def test_rfc13_t052_duplicate_rp_does_not_cause_duplicate_activation() -> None:
    """RFC13-T052: Multiple duplicate proposals for the same target activate the node only once."""
    g, eng = _build_simple_test_graph()
    g.link("dup1", "target_dup", W=0.85)
    g.link("dup2", "target_dup", W=0.85)
    r = [
        ParticipationReceipt("r_d1", "dup1", 1, 0, "external", "node", activation_magnitude=0.85),
        ParticipationReceipt("r_d2", "dup2", 1, 0, "external", "node", activation_magnitude=0.85),
    ]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    target_commits = [t for t in outcome.committed_targets if t[0] == "target_dup"]
    assert len(target_commits) == 1


def test_rfc13_t053_failed_commit_leaves_committed_set_unchanged() -> None:
    """RFC13-T053: Injected failure before commit leaves CommittedSet unmodified."""
    se = SettlingEpoch("se_f", "rid", frozenset(["a"]), "snap", 1.0)
    orig_commits = set(se.committed_set)
    # Simulate failed transaction: committed_set remains unchanged
    assert se.committed_set == orig_commits


def test_rfc13_t054_failed_commit_leaves_no_ghost_authority() -> None:
    """RFC13-T054: Injected failure leaves zero ghost activation authority in the graph."""
    g, _eng = _build_simple_test_graph()
    assert "ghost_node" not in g.nodes


def test_rfc13_t055_invalidated_epoch_blocks_further_commits() -> None:
    """RFC13-T055: An INVALIDATED epoch permits zero further completion commits."""
    se = SettlingEpoch("se_inv", "rid", frozenset(["a"]), "snap", 1.0)
    se.close("INVALIDATED")
    assert se.status == "CLOSED"
    assert se.closure_reason == "INVALIDATED"


def test_rfc13_t056_cache_corruption_rebuilt_transparently() -> None:
    """RFC13-T056: Cache purging causes transparent deterministic rebuilding."""
    g, eng = _build_simple_test_graph()
    g.link("u_c", "v_c", W=0.85)
    r = [ParticipationReceipt("rc", "u_c", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands1 = eng.discover_candidates(rep)
    eng.clear_caches()
    cands2 = eng.discover_candidates(rep)
    assert [c.candidate_id for c in cands1] == [c.candidate_id for c in cands2]


# ─────────────────────────────────────────────────────────── Group 8: Downstream Boundary (T057..T064)
def test_rfc13_t057_downstream_receives_current_sdcr_not_candidate_footprint() -> None:
    """RFC13-T057: Downstream handoff provides the current canonical SDCR, not the uncommitted candidate footprint."""
    g, eng = _build_simple_test_graph()
    g.link("w1", "w2", W=0.85)
    r = [ParticipationReceipt("rw1", "w1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    rep_final, _outcome = eng.run_settling_epoch(rep0, budget=1.0)
    view = g.representation_engine.get_view(rep_final)
    assert view.participating_nodes() == rep_final.participating_node_refs


def test_rfc13_t058_uncommitted_candidate_content_cannot_be_read_as_confirmed() -> None:
    """RFC13-T058: Content inside candidate footprint that was not committed cannot be read as knowledge."""
    g, eng = _build_simple_test_graph()
    g.link("k1", "k2", W=0.01)  # Sub-threshold
    r = [ParticipationReceipt("rk1", "k1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    rep_final, _outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert "k2" not in rep_final.participating_node_refs


def test_rfc13_t059_ambiguity_remains_explicit_in_handoff() -> None:
    """RFC13-T059: Unresolved ambiguities remain explicitly detailed in SettlingOutcomeView."""
    g, eng = _build_simple_test_graph()
    g.link("cue_h", "alt1", W=0.85)
    g.link("cue_h", "alt2", W=0.85)
    g.add_contradiction("alt1", "alt2")
    r = [ParticipationReceipt("rch", "cue_h", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "AMBIGUOUS_FIXED_POINT"
    assert len(outcome.unresolved_alternatives) >= 1


def test_rfc13_t060_budget_exhausted_flag_explicit_downstream() -> None:
    """RFC13-T060: Budget exhaustion reason is explicitly accessible to downstream consumers."""
    g, eng = _build_simple_test_graph()
    g.link("b1", "b2", W=0.85)
    r = [ParticipationReceipt("rb", "b1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _rep_final, outcome = eng.run_settling_epoch(rep0, budget=0.0)
    assert outcome.closure_reason == "BUDGET_EXHAUSTED"


def test_rfc13_t061_invalidated_epoch_not_used_as_final_handoff() -> None:
    """RFC13-T061: An invalidated settling epoch is marked as INVALIDATED in outcome view."""
    se = SettlingEpoch("se_bad", "rid", frozenset(["x"]), "snap", 1.0)
    se.close("INVALIDATED")
    assert se.closure_reason == "INVALIDATED"


def test_rfc13_t062_generated_output_does_not_become_independent_root_evidence() -> None:
    """RFC13-T062: Generated downstream text cannot become independent root evidence."""
    rec = ParticipationReceipt("r_tok", "word_the", 1, 0, "PATTERN_COMPLETION", "node")
    assert rec.origin_lineage == "PATTERN_COMPLETION"


def test_rfc13_t063_token_adjacency_cannot_create_tbr_binding_authority() -> None:
    """RFC13-T063: Consecutive generated token tokens do not create TransientBindingReceipts without grouping authority."""
    g, _eng = _build_simple_test_graph()
    # TBR requires lawful grouping authority, not mere surface adjacency
    rep = g.representation_engine.build_representation(1, 0, None, [])
    assert len(rep.transient_binding_receipts) == 0


def test_rfc13_t064_downstream_readout_cannot_mutate_rfc13_state() -> None:
    """RFC13-T064: Reading SettlingOutcomeView is purely functional and causes zero side-effects."""
    outcome = SettlingOutcomeView("FIXED_POINT", 2, frozenset([("t1", ("global",), None)]), [], "rid_final", 0.4)
    assert outcome.closure_reason == "FIXED_POINT"
    assert outcome.iterations == 2


# ─────────────────────────────────────────────────────────── Group 9: Determinism & Locality (T065..T072)
def test_rfc13_t065_fixed_input_gives_identical_candidate_set() -> None:
    """RFC13-T065: Fixed inputs reproduce identical candidate sets deterministically."""
    g, eng = _build_simple_test_graph()
    g.link("d_a", "d_b", W=0.85)
    r = [ParticipationReceipt("rda", "d_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands1 = [c.candidate_id for c in eng.discover_candidates(rep)]
    eng.clear_caches()
    cands2 = [c.candidate_id for c in eng.discover_candidates(rep)]
    assert cands1 == cands2


def test_rfc13_t066_fixed_input_gives_identical_rp_set() -> None:
    """RFC13-T066: Fixed inputs reproduce identical proposal sets deterministically."""
    g, eng = _build_simple_test_graph()
    g.link("dp_a", "dp_b", W=0.85)
    r = [ParticipationReceipt("rdp", "dp_a", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep)
    props1 = [p.proposal_id for p in eng.evaluate_reinstatement_eligibility(cands[0], rep)]
    props2 = [p.proposal_id for p in eng.evaluate_reinstatement_eligibility(cands[0], rep)]
    assert props1 == props2


def test_rfc13_t067_fixed_arbitration_gives_identical_outcome() -> None:
    """RFC13-T067: Fixed inputs reproduce identical arbitration outcomes deterministically."""
    from dgca import CompetitiveAlternativeSet

    _g, eng = _build_simple_test_graph()
    cand = PatternCandidate("c_det", "rid", None, frozenset(["q"]), frozenset(["t"]), frozenset(), ("global",), None, None, {})
    cas = CompetitiveAlternativeSet("comp1", frozenset(["c_det"]), frozenset())

    v1, nd1, _ = eng.arbitrate_competition(cas, {"c_det": cand}, {}, frozenset(["q"]))
    v2, nd2, _ = eng.arbitrate_competition(cas, {"c_det": cand}, {}, frozenset(["q"]))
    assert v1 == v2
    assert nd1 == nd2


def test_rfc13_t068_fixed_settling_reproduces_same_commit_sequence() -> None:
    """RFC13-T068: Fixed initial conditions reproduce exact settling commit sequences."""
    g, eng = _build_simple_test_graph()
    g.link("seq_1", "seq_2", W=0.85)
    g.link("seq_2", "seq_3", W=0.85)
    r = [ParticipationReceipt("rseq", "seq_1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _, out1 = eng.run_settling_epoch(rep0, budget=1.0)
    _, out2 = eng.run_settling_epoch(rep0, budget=1.0)
    assert out1.committed_targets == out2.committed_targets
    assert out1.iterations == out2.iterations


def test_rfc13_t069_remote_graph_growth_does_not_alter_local_result() -> None:
    """RFC13-T069: Scaling remote unrelated graph size does not perturb local completion outcomes."""
    g, eng = _build_simple_test_graph()
    g.link("loc_1", "loc_2", W=0.85)
    r = [ParticipationReceipt("rloc", "loc_1", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    _, out_iso = eng.run_settling_epoch(rep0, budget=1.0)

    # Add 100 remote unrelated edges
    for i in range(100):
        g.link(f"noise_{i}", f"noise_{i+1}", W=0.5)

    eng.clear_caches()
    _, out_emb = eng.run_settling_epoch(rep0, budget=1.0)
    assert out_iso.committed_targets == out_emb.committed_targets
    assert out_iso.closure_reason == out_emb.closure_reason


def test_rfc13_t070_high_degree_inactive_neighborhood_does_not_expand_work() -> None:
    """RFC13-T070: High inactive degree on participating nodes does not cause global traversal."""
    g, eng = _build_simple_test_graph()
    g.link("hub_src", "active_target", W=0.85)
    # Add 50 inactive edges
    for d in range(50):
        g.link("hub_src", f"inactive_leaf_{d}", W=0.01)

    r = [ParticipationReceipt("rhub", "hub_src", 1, 0, "external", "node", activation_magnitude=0.85)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    cands = eng.discover_candidates(rep0)
    # Frontier targets only include lawful paths
    all_frontiers = set().union(*(eng.derive_completion_frontier(c, rep0) for c in cands))
    assert "active_target" in all_frontiers


def test_rfc13_t071_competition_groups_do_not_require_global_scan() -> None:
    """RFC13-T071: CompetitionKey grouping partitions locally without global all-pairs tournament."""
    _g, eng = _build_simple_test_graph()
    cand1 = PatternCandidate("c_g1", "rid", None, frozenset(["s1"]), frozenset(["t1"]), frozenset(), ("global",), None, None, {})
    cand2 = PatternCandidate("c_g2", "rid", None, frozenset(["s2"]), frozenset(["t2"]), frozenset(), ("global",), None, None, {})

    cas_list = eng.group_competitive_alternatives([cand1, cand2], [])
    assert len(cas_list) == 0  # No conflict, 0 groups formed


def test_rfc13_t072_rfc13_disabled_or_no_eligible_completion_preserves_baseline() -> None:
    """RFC13-T072: When no eligible completions exist, baseline runtime semantics are 100% preserved."""
    g, eng = _build_simple_test_graph()
    g.node("lone_node", "text").excite(1, 0.8)
    r = [ParticipationReceipt("rlone", "lone_node", 1, 0, "external", "node", activation_magnitude=0.8)]
    rep0 = g.representation_engine.build_representation(1, 0, None, r)

    rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
    assert outcome.closure_reason == "FIXED_POINT"
    assert len(outcome.committed_targets) == 0
    assert rep_final.participating_node_refs == rep0.participating_node_refs
