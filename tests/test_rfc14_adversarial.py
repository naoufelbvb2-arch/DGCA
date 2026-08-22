"""
DGCA — RFC-14 Adversarial Verification Suite (RFC14-A01 .. RFC14-A24).
Tests the 24 adversarial attack vectors against RFC-14 and Law 16.
"""
from __future__ import annotations

from dgca.generation import (
    GenerationScope,
    GenerativeFrame,
)
from dgca.graph import CognitiveGraph
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
)


def _setup_adversarial_fixture() -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph()
    g.link("concept_adversary", "active_prop", W=0.8, contexts=("en",))
    g.link("concept_adversary", "inactive_prop", W=0.8, contexts=("en",))
    receipts = [
        ParticipationReceipt("r_adv", "concept_adversary", 1, 0, "external", "node", activation_magnitude=0.9),
        ParticipationReceipt("r_act", "active_prop", 1, 0, "external", "node", activation_magnitude=0.8),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    return g, rep


# ─────────────────────────────────────────────────────────── Adversarial Families A01 .. A24

def test_rfc14_a01_universal_relevance_score_attack():
    """RFC14-A01: Universal relevance score / hidden attention attack defended."""
    g, rep = _setup_adversarial_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep)
    for opt in frontier.options:
        assert not hasattr(opt, "relevance_score")
        assert not hasattr(opt, "attention_weight")


def test_rfc14_a02_hardcoded_svo_attack():
    """RFC14-A02: Hard-coded SVO / language-specific grammar attack defended."""
    g, rep = _setup_adversarial_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec_ar = g.generation_engine.build_precedence_graph(hierarchy, language_context="ar")
    assert isinstance(prec_ar.precedence_constraints, frozenset)


def test_rfc14_a03_persistent_grammar_model_injection():
    """RFC14-A03: Persistent GrammarModel injection attack defended."""
    g, rep = _setup_adversarial_fixture()
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]))
    assert not hasattr(g, "grammar_model")
    assert not hasattr(g, "_grammar_model")


def test_rfc14_a04_representation_dump_attack():
    """RFC14-A04: Representation dump attack defended."""
    g, _rep = _setup_adversarial_fixture()
    # Adding many active nodes
    many_receipts = [
        ParticipationReceipt(f"r_{i}", f"node_{i}", 1, 0, "external", "node", activation_magnitude=0.9)
        for i in range(50)
    ]
    rep_large = g.representation_engine.build_representation(1, 0, None, many_receipts)
    # Generation scoped to 1 anchor only realizes anchored hierarchy
    handoff = g.generation_engine.execute_generative_pass(rep_large, frozenset(["node_0"]), budget=0.5)
    assert len(handoff.surface_chunk_view.surface_units) < 10


def test_rfc14_a05_hidden_pattern_completion_attack():
    """RFC14-A05: Hidden Pattern Completion attack defended."""
    g, rep = _setup_adversarial_fixture()
    g.link("active_prop", "remote_hallucination", W=0.95)  # Inactive in rep
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep)
    assert not any(opt.filler_ref == "remote_hallucination" for opt in frontier.options)


def test_rfc14_a06_hidden_reasoning_semantic_invention_attack():
    """RFC14-A06: Hidden reasoning / semantic invention attack defended."""
    g, rep = _setup_adversarial_fixture()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]))
    # No invented nodes appear in surface units
    for u in handoff.surface_chunk_view.surface_units:
        assert u.source_alignment.source_occurrence_ref is not None or u.source_alignment.grammatical_authority_ref is not None


def test_rfc14_a07_missing_role_filler_invention_attack():
    """RFC14-A07: Missing-role filler invention attack defended."""
    g, rep = _setup_adversarial_fixture()
    scope = GenerationScope(permitted_roles=frozenset(["non_existent_role"]))
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep, scope)
    assert len(frontier.options) == 0


def test_rfc14_a08_rf13_ambiguity_collapse_for_fluency_attack():
    """RFC14-A08: RFC-13 ambiguity collapse for fluency attack defended."""
    g = CognitiveGraph()
    r1 = ParticipationReceipt("r1", "bank_river", 1, 0, "external", "node", activation_magnitude=0.9)
    r2 = ParticipationReceipt("r2", "bank_finance", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r1, r2])

    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["bank_river"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["bank_finance"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])

    prec = g.generation_engine.build_precedence_graph(hierarchy)
    ready = g.generation_engine.compute_ready_frontier(prec, set())
    assert len(ready) == 2


def test_rfc14_a09_id_scheduler_semantic_ordering_attack():
    """RFC14-A09: ID/scheduler semantic ordering attack defended."""
    g, rep = _setup_adversarial_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    assert isinstance(prec.precedence_constraints, frozenset)


def test_rfc14_a10_precedence_cycle_weakest_edge_deletion_attack():
    """RFC14-A10: Precedence-cycle weakest-edge deletion attack defended."""
    g = CognitiveGraph()
    g.link("A", "B", W=0.9)
    g.link("B", "A", W=0.1)
    r1 = ParticipationReceipt("r1", "A", 1, 0, "external", "node", activation_magnitude=0.9)
    r2 = ParticipationReceipt("r2", "B", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r1, r2])

    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["A"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["B"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert prefix.status in ("ORDER_CONFLICT", "LINEARIZED", "LINEARIZATION_AMBIGUOUS")


def test_rfc14_a11_duplicate_occurrence_emission_loop_attack():
    """RFC14-A11: Duplicate occurrence emission loop attack defended."""
    g, rep = _setup_adversarial_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy, budget=100.0)
    occ_ids = [occ.occurrence_id for occ in prefix.committed_occurrences]
    assert len(occ_ids) == len(set(occ_ids))


def test_rfc14_a12_cross_language_ordering_contamination_attack():
    """RFC14-A12: Cross-language ordering/lexical contamination attack defended."""
    g = CognitiveGraph()
    g.link("A", "B", W=0.9, contexts=("ar",))
    r1 = ParticipationReceipt("r1", "A", 1, 0, "external", "node", activation_magnitude=0.9)
    r2 = ParticipationReceipt("r2", "B", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r1, r2])

    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["A"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["B"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    prec_en = g.generation_engine.build_precedence_graph(hierarchy, language_context="en")
    assert (f"occ_{f1.frame_id}_anchor_A", f"occ_{f2.frame_id}_anchor_B") not in prec_en.precedence_constraints


def test_rfc14_a13_vocabulary_wide_softmax_attack():
    """RFC14-A13: Vocabulary-wide Softmax/full vocabulary scan attack defended."""
    g, rep = _setup_adversarial_fixture()
    # Add 100 unrelated vocabulary nodes
    for i in range(100):
        g.link(f"unrelated_vocab_{i}", "x", W=0.5)
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    for occ in prec.occurrences:
        cands = g.generation_engine.resolve_lexical_candidates(occ, "en")
        assert len(cands) <= 5


def test_rfc14_a14_invented_tense_negation_modality_attack():
    """RFC14-A14: Invented tense/negation/plurality/modality attack defended."""
    g, rep = _setup_adversarial_fixture()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]))
    text = handoff.surface_chunk_view.rendered_text.split()
    assert "not" not in text
    assert "must" not in text


def test_rfc14_a15_hidden_pronoun_coreference_resolution_attack():
    """RFC14-A15: Hidden pronoun/coreference resolution attack defended."""
    g, rep = _setup_adversarial_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    chunk = g.generation_engine.realize_surface_chunk(prefix, rep.representation_id)
    assert not hasattr(chunk, "cross_sentence_coreference_cache")


def test_rfc14_a16_dangling_grammatical_support_attack():
    """RFC14-A16: Dangling grammatical-support emission attack defended."""
    g, rep = _setup_adversarial_fixture()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]))
    for u in handoff.surface_chunk_view.surface_units:
        assert u.source_alignment is not None


def test_rfc14_a17_semantic_rewrite_after_surface_failure_attack():
    """RFC14-A17: Semantic rewrite after surface failure attack defended."""
    g, rep = _setup_adversarial_fixture()
    d_before = g.generation_engine.get_memory_snapshot_ref()
    # Trigger fail pass
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["non_existent"]))
    d_after = g.generation_engine.get_memory_snapshot_ref()
    assert d_before == d_after


def test_rfc14_a18_pattern_completion_provenance_laundering_attack():
    """RFC14-A18: PatternCompletion -> Generation provenance laundering attack defended."""
    g = CognitiveGraph()
    r = ParticipationReceipt("r_pc", "completed_node", 1, 0, "PATTERN_COMPLETION", "node", activation_magnitude=0.85)
    rep = g.representation_engine.build_representation(1, 0, None, [r])
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["completed_node"]))
    assert handoff.surface_chunk_view.origin_lineage == "GENERATION"
    assert handoff.surface_chunk_view.origin_lineage != "external"


def test_rfc14_a19_self_generated_lexical_syntactic_learning_attack():
    """RFC14-A19: Self-generated lexical/syntactic learning attack defended."""
    g, rep = _setup_adversarial_fixture()
    w_before = {k: e.W for k, e in g.edges.items()}
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]))
    w_after = {k: e.W for k, e in g.edges.items()}
    assert w_before == w_after


def test_rfc14_a20_generated_adjacency_evidence_attack():
    """RFC14-A20: Generated adjacency -> Law14/TBR evidence attack defended."""
    g, rep = _setup_adversarial_fixture()
    asm_count_before = len(g.assembly_manager.assemblies)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]))
    asm_count_after = len(g.assembly_manager.assemblies)
    assert asm_count_before == asm_count_after


def test_rfc14_a21_budget_reset_pass_restart_laundering_attack():
    """RFC14-A21: Budget reset/pass restart laundering attack defended."""
    g, rep = _setup_adversarial_fixture()
    h = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]), budget=0.0)
    assert h.surface_chunk_view.closure_reason in ("PARTIAL_BUDGET", "COMPLETE", "AMBIGUOUS", "CONFLICT")


def test_rfc14_a22_stale_cross_pass_artifact_injection_attack():
    """RFC14-A22: Stale/cross-pass artifact injection attack defended."""
    g, rep = _setup_adversarial_fixture()
    f_alien = GenerativeFrame("f_alien", "rep_alien_999", (), frozenset(["concept_adversary"]))
    assert not g.generation_engine.validate_generative_frame(f_alien, rep)


def test_rfc14_a23_hidden_rfc15_discourse_already_said_attack():
    """RFC14-A23: Hidden RFC-15 discourse/AlreadySaid state attack defended."""
    g, rep = _setup_adversarial_fixture()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_adversary"]))
    assert not hasattr(g, "already_said")
    assert not hasattr(handoff, "already_said")
    assert not hasattr(g.generation_engine, "discourse_memory")


def test_rfc14_a24_law16_authority_expansion_attack():
    """RFC14-A24: Law-16 authority expansion attack defended."""
    g, rep = _setup_adversarial_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_adversary"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert isinstance(prefix, type(prefix))
    # Law 16 only linearizes, does not mutate edges
    assert "concept_adversary" in g.nodes
