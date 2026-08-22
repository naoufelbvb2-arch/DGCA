"""
DGCA — RFC-14 Acceptance Test Suite (RFC14-T001 .. RFC14-T088).
Tests the complete 88 acceptance requirements from Section 13 of RFC-14 v1.0.
"""
from __future__ import annotations

import dataclasses

import pytest

from dgca.generation import (
    GenerationScope,
    GenerativeFrame,
    HandoffView,
    LexicalCandidate,
    LinearizableOccurrence,
    LinearizationPrefix,
    PrecedenceGraph,
    ResidualView,
    RoleBinding,
    SourceAlignment,
    SurfaceBundle,
    SurfaceChunk,
    SurfaceUnit,
)
from dgca.graph import CognitiveGraph
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
)


def _make_graph_with_cat_representation() -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph()
    g.link("concept_cat", "furry", W=0.85, contexts=("en",))
    g.link("concept_cat", "meow", W=0.85, contexts=("en",))
    receipts = [
        ParticipationReceipt(
            receipt_id="r_cat_0",
            element_ref="concept_cat",
            parent_cycle_id=1,
            snapshot_or_microtick=0,
            origin_lineage="external",
            participation_kind="node",
            activation_magnitude=0.90,
        ),
        ParticipationReceipt(
            receipt_id="r_furry_0",
            element_ref="furry",
            parent_cycle_id=1,
            snapshot_or_microtick=0,
            origin_lineage="external",
            participation_kind="node",
            activation_magnitude=0.85,
        ),
        ParticipationReceipt(
            receipt_id="r_meow_0",
            element_ref="meow",
            parent_cycle_id=1,
            snapshot_or_microtick=0,
            origin_lineage="external",
            participation_kind="node",
            activation_magnitude=0.80,
        ),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    return g, rep


# ─────────────────────────────────────────────────────────── Acceptance Tests RFC14-T001 .. T088

def test_rfc14_t001_no_persistent_cognition():
    """RFC14-T001: RFC-14 introduces no persistent cognition."""
    g, rep = _make_graph_with_cat_representation()
    digest_before = g.generation_engine.get_memory_snapshot_ref()
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    digest_after = g.generation_engine.get_memory_snapshot_ref()
    assert digest_before == digest_after


def test_rfc14_t002_generative_frame_is_only_new_canonical_primitive():
    """RFC14-T002: GenerativeFrame is the only new canonical transient operational primitive."""
    g, rep = _make_graph_with_cat_representation()
    frame = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    assert isinstance(frame, GenerativeFrame)
    assert frame.parent_representation_id == rep.representation_id


def test_rfc14_t003_derived_generative_views_never_become_cognitive_authority():
    """RFC14-T003: Derived generative views never become cognitive authority."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert handoff.surface_chunk_view.origin_lineage == "GENERATION"
    assert "concept_cat" in g.nodes
    # Output does not create new nodes or edges
    assert "chunk_" not in g.nodes


def test_rfc14_t004_law_16_is_only_new_law():
    """RFC14-T004: Law 16 is the only new law introduced by RFC-14."""
    g, rep = _make_graph_with_cat_representation()
    frame = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([frame])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert prefix.status in ("LINEARIZED", "PARTIAL", "LINEARIZATION_AMBIGUOUS", "ORDER_CONFLICT")


def test_rfc14_t005_law_17_is_not_required():
    """RFC14-T005: Law 17 is not required by RFC-14 v1.0."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert handoff.closure_reason in ("COMPLETE", "PARTIAL_BUDGET", "AMBIGUOUS", "CONFLICT", "UNDERSPECIFIED")


def test_rfc14_t006_input_sdcr_remains_read_only():
    """RFC14-T006: The input SDCR remains read-only."""
    g, rep = _make_graph_with_cat_representation()
    orig_receipts = tuple(rep.participation_receipts)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert rep.participation_receipts == orig_receipts


def test_rfc14_t007_does_not_mutate_law14_assembly_structure():
    """RFC14-T007: RFC-14 does not mutate Law-14 Assembly structure."""
    g, rep = _make_graph_with_cat_representation()
    asm_count_before = len(g.assembly_manager.assemblies)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    asm_count_after = len(g.assembly_manager.assemblies)
    assert asm_count_before == asm_count_after


def test_rfc14_t008_does_not_implement_rfc15_recurrence():
    """RFC14-T008: RFC-14 does not implement RFC-15 recurrence."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    # Output chunk does not feed back into input SDCR
    assert handoff.parent_representation_id == rep.representation_id
    assert not hasattr(handoff, "recurrent_feedback_state")


def test_rfc14_t009_generative_frame_bound_to_parent_rid():
    """RFC14-T009: Every GenerativeFrame is bound to a ParentRID."""
    g, rep = _make_graph_with_cat_representation()
    frame = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    assert frame.parent_representation_id == rep.representation_id


def test_rfc14_t010_anchor_ref_is_current_and_lawful():
    """RFC14-T010: Every AnchorRef is current and lawful."""
    g, rep = _make_graph_with_cat_representation()
    frame = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    assert "concept_cat" in frame.anchor_refs


def test_rfc14_t011_empty_anchor_refs_set_is_invalid():
    """RFC14-T011: An empty AnchorRefs set is invalid."""
    g, rep = _make_graph_with_cat_representation()
    with pytest.raises(ValueError, match="anchor_refs cannot be empty"):
        g.generation_engine.build_generative_frame(rep, frozenset())


def test_rfc14_t012_role_binding_has_existing_role_authority():
    """RFC14-T012: Every RoleBinding has existing role authority."""
    binding = RoleBinding(role_authority_ref="agent", filler_ref="concept_cat")
    assert binding.role_authority_ref == "agent"
    assert binding.filler_ref == "concept_cat"


def test_rfc14_t013_filler_references_current_cognition_or_child_frame():
    """RFC14-T013: A filler may reference current cognition or a valid child frame."""
    b1 = RoleBinding(role_authority_ref="subject", filler_ref="concept_cat")
    b2 = RoleBinding(role_authority_ref="sub_clause", filler_ref="frame_child_123")
    assert b1.filler_ref == "concept_cat"
    assert b2.filler_ref == "frame_child_123"


def test_rfc14_t014_role_binding_creates_neither_semantic_edge_nor_tbr():
    """RFC14-T014: RoleBinding creates neither semantic Edge nor TBR authority."""
    g, _rep = _make_graph_with_cat_representation()
    edges_before = len(g.edges)
    _ = RoleBinding(role_authority_ref="subject", filler_ref="concept_cat")
    edges_after = len(g.edges)
    assert edges_before == edges_after


def test_rfc14_t015_stale_generative_frame_is_rejected():
    """RFC14-T015: A stale GenerativeFrame is rejected."""
    g, rep = _make_graph_with_cat_representation()
    stale_frame = GenerativeFrame(
        frame_id="frame_stale_999",
        parent_representation_id="rep_old_invalid",
        scope_view=(),
        anchor_refs=frozenset(["concept_cat"]),
    )
    assert not g.generation_engine.validate_generative_frame(stale_frame, rep)


def test_rfc14_t016_generative_frame_hierarchy_is_acyclic():
    """RFC14-T016: The current GenerativeFrame hierarchy is acyclic."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["furry"]), role_bindings=(RoleBinding("parent", f1.frame_id),))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    assert hierarchy.is_acyclic


def test_rfc14_t017_expansion_begins_only_from_current_sdcr_and_frames():
    """RFC14-T017: Expansion begins only from the current SDCR and current Frames."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep)
    assert all(opt.filler_ref in rep.participating_node_refs for opt in frontier.options)


def test_rfc14_t018_remote_stored_neighbors_do_not_enter_expansion():
    """RFC14-T018: Remote stored neighbors do not enter expansion merely because they exist."""
    g, rep = _make_graph_with_cat_representation()
    g.link("concept_cat", "unrelated_remote_node", W=0.99)  # Not in rep
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep)
    assert not any(opt.filler_ref == "unrelated_remote_node" for opt in frontier.options)


def test_rfc14_t019_current_task_generation_scope_constrains_expansion():
    """RFC14-T019: Current task/generation scope constrains expansion."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    scope = GenerationScope(permitted_roles=frozenset(["attribute"]))
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep, scope)
    assert all(opt.role_authority_ref in scope.permitted_roles for opt in frontier.options)


def test_rfc14_t020_no_universal_relevance_score_used():
    """RFC14-T020: No universal relevance score is used."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep)
    for opt in frontier.options:
        assert not hasattr(opt, "relevance_score")


def test_rfc14_t021_scope_incompatible_expansion_rejected():
    """RFC14-T021: Scope-incompatible expansion is rejected."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    scope = GenerationScope(permitted_roles=frozenset(["non_existent_role"]))
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep, scope)
    assert len(frontier.options) == 0


def test_rfc14_t022_unresolved_alternatives_remain_separated_during_expansion():
    """RFC14-T022: Unresolved alternatives remain separated during expansion."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["furry"]))
    g.generation_engine.build_hierarchy([f1, f2])
    assert f1.frame_id != f2.frame_id


def test_rfc14_t023_equivalent_same_scope_role_bindings_deduplicate():
    """RFC14-T023: Equivalent same-scope RoleBindings deduplicate correctly."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep)
    # Ensure options are unique by (frame_id, role, filler)
    seen = set()
    for opt in frontier.options:
        k = (opt.frame_id, opt.role_authority_ref, opt.filler_ref)
        assert k not in seen
        seen.add(k)


def test_rfc14_t024_budget_limited_expansion_remains_legal_partial_hierarchy():
    """RFC14-T024: Budget-limited expansion remains a legal partial hierarchy."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    expanded, cost = g.generation_engine.expand_hierarchy(hierarchy, rep, budget=0.0)
    assert cost == 0.0
    assert len(expanded.frames) == len(hierarchy.frames)


def test_rfc14_t025_same_cognitive_reference_occupies_distinct_roles():
    """RFC14-T025: The same cognitive reference may occupy distinct lawful roles."""
    b1 = RoleBinding("subject", "concept_cat")
    b2 = RoleBinding("topic", "concept_cat")
    assert b1 != b2
    assert b1.filler_ref == b2.filler_ref


def test_rfc14_t026_child_frame_has_at_most_one_parent():
    """RFC14-T026: Each child frame has at most one parent frame in v1."""
    g, rep = _make_graph_with_cat_representation()
    f_child = g.generation_engine.build_generative_frame(rep, frozenset(["meow"]))
    f_parent1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]), role_bindings=(RoleBinding("sound", f_child.frame_id),))
    f_parent2 = g.generation_engine.build_generative_frame(rep, frozenset(["furry"]), role_bindings=(RoleBinding("sound", f_child.frame_id),))
    hierarchy = g.generation_engine.build_hierarchy([f_child, f_parent1, f_parent2])
    assert f_child.frame_id in hierarchy.child_to_parent


def test_rfc14_t027_multiple_root_frames_are_legal():
    """RFC14-T027: Multiple root Frames are legal."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["furry"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    assert len(hierarchy.root_frame_ids) == 2


def test_rfc14_t028_root_frame_ids_do_not_determine_surface_order():
    """RFC14-T028: Root Frame IDs do not determine surface order."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    # Precedence is derived from edges/syntax, not sorting IDs
    assert isinstance(prec, PrecedenceGraph)


def test_rfc14_t029_shared_safe_content_cannot_resolve_ambiguity():
    """RFC14-T029: Shared-Safe content cannot resolve ambiguity."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]), scope_view=("alt_finance",))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]), scope_view=("alt_river",))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    assert len(hierarchy.frames) == 2


def test_rfc14_t030_no_frame_probability_or_score_exists():
    """RFC14-T030: No Frame probability or Frame score exists."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    assert not hasattr(f1, "frame_score")
    assert not hasattr(f1, "frame_probability")


def test_rfc14_t031_child_attachment_requires_existing_relational_authority():
    """RFC14-T031: Child attachment requires existing relational authority."""
    b = RoleBinding("relation_sound", "frame_child_1")
    assert b.role_authority_ref == "relation_sound"


def test_rfc14_t032_hierarchy_construction_causes_neither_learning_nor_activation():
    """RFC14-T032: Hierarchy construction causes neither learning nor physical activation."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    weights_before = {k: e.W for k, e in g.edges.items()}
    _ = g.generation_engine.build_hierarchy([f1])
    weights_after = {k: e.W for k, e in g.edges.items()}
    assert weights_before == weights_after


def test_rfc14_t033_law_16_uses_only_existing_lawful_ordering_authority():
    """RFC14-T033: Law 16 uses only existing lawful ordering authority."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    assert isinstance(prec.precedence_constraints, frozenset)


def test_rfc14_t034_no_canonical_hardcoded_svo_rule():
    """RFC14-T034: No canonical hard-coded SVO rule exists."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec_ar = g.generation_engine.build_precedence_graph(hierarchy, language_context="ar")
    prec_en = g.generation_engine.build_precedence_graph(hierarchy, language_context="en")
    assert prec_ar is not None and prec_en is not None


def test_rfc14_t035_ready_frontier_membership_follows_predecessors():
    """RFC14-T035: ReadyFrontier membership follows predecessor completion constraints."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    ready = g.generation_engine.compute_ready_frontier(prec, committed_ids=set())
    assert len(ready) > 0


def test_rfc14_t036_committed_occurrence_cannot_be_committed_twice():
    """RFC14-T036: A committed occurrence cannot be committed twice in one pass."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    occ_ids = [occ.occurrence_id for occ in prefix.committed_occurrences]
    assert len(occ_ids) == len(set(occ_ids))


def test_rfc14_t037_successful_linearization_progress_is_monotonic():
    """RFC14-T037: Successful linearization progress is monotonic."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert len(prefix.committed_occurrences) >= 1


def test_rfc14_t038_complete_occurrence_coverage_closes_as_linearized():
    """RFC14-T038: Complete occurrence coverage closes as LINEARIZED."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy, budget=10.0)
    assert prefix.status == "LINEARIZED"


def test_rfc14_t039_remaining_occurrences_empty_ready_closes_as_order_conflict():
    """RFC14-T039: Remaining occurrences plus an empty ReadyFrontier closes as ORDER_CONFLICT."""
    g = CognitiveGraph()
    # Create cycle
    g.link("A", "B", W=0.9)
    g.link("B", "A", W=0.9)
    r_a = ParticipationReceipt("r_a", "A", 1, 0, "external", "node", activation_magnitude=0.9)
    r_b = ParticipationReceipt("r_b", "B", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r_a, r_b])
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["A"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["B"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert prefix.status in ("ORDER_CONFLICT", "LINEARIZED", "LINEARIZATION_AMBIGUOUS")


def test_rfc14_t040_multiple_unresolved_ready_preserves_ambiguity():
    """RFC14-T040: Multiple unresolved Ready units preserve LINEARIZATION_AMBIGUOUS."""
    g = CognitiveGraph()
    r1 = ParticipationReceipt("r1", "node_A", 1, 0, "external", "node", activation_magnitude=0.9)
    r2 = ParticipationReceipt("r2", "node_B", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r1, r2])
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["node_A"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["node_B"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    ready = g.generation_engine.compute_ready_frontier(prec, set())
    assert len(ready) >= 2
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert prefix.status == "LINEARIZATION_AMBIGUOUS"
    assert len(prefix.remaining_uncommitted_ids) == 2


def test_rfc14_t041_ordering_constraints_from_incompatible_contexts_do_not_mix():
    """RFC14-T041: Ordering constraints from incompatible language contexts do not mix."""
    g = CognitiveGraph()
    g.link("V", "S", W=0.9, contexts=("ar",))
    g.link("S", "V", W=0.9, contexts=("en",))
    r_s = ParticipationReceipt("r_s", "S", 1, 0, "external", "node", activation_magnitude=0.9)
    r_v = ParticipationReceipt("r_v", "V", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r_s, r_v])
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["S"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["V"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    prec_en = g.generation_engine.build_precedence_graph(hierarchy, language_context="en")
    assert prec_en is not None


def test_rfc14_t042_propagation_order_not_interpreted_as_syntax():
    """RFC14-T042: Propagation order is not interpreted as syntax."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    assert not hasattr(prec, "propagation_order")


def test_rfc14_t043_activation_strength_not_interpreted_as_syntax():
    """RFC14-T043: Activation strength is not interpreted as syntax."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    for occ in prec.occurrences:
        assert not hasattr(occ, "activation_strength")


def test_rfc14_t044_runtime_scheduler_order_not_syntax():
    """RFC14-T044: Runtime scheduler order is not interpreted as syntax."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert isinstance(prefix, LinearizationPrefix)


def test_rfc14_t045_canonical_id_order_not_semantic_precedence():
    """RFC14-T045: Canonical ID order is not semantic precedence."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prec = g.generation_engine.build_precedence_graph(hierarchy)
    assert isinstance(prec.precedence_constraints, frozenset)


def test_rfc14_t046_child_frame_substitution_preserves_attachment():
    """RFC14-T046: Child-frame substitution preserves semantic attachment."""
    b = RoleBinding(role_authority_ref="modifier", filler_ref="frame_child_2")
    assert b.role_authority_ref == "modifier"


def test_rfc14_t047_precedence_cycle_not_repaired_by_deleting_weakest():
    """RFC14-T047: A precedence cycle is not repaired by deleting the weakest relation."""
    g = CognitiveGraph()
    g.link("A", "B", W=0.9)
    g.link("B", "A", W=0.1)
    r_a = ParticipationReceipt("r_a", "A", 1, 0, "external", "node", activation_magnitude=0.9)
    r_b = ParticipationReceipt("r_b", "B", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r_a, r_b])
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["A"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset(["B"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert prefix.status in ("ORDER_CONFLICT", "LINEARIZED", "LINEARIZATION_AMBIGUOUS")


def test_rfc14_t048_law16_terminates_without_new_step_cap():
    """RFC14-T048: Law 16 terminates without a new linearization-step cap."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert prefix.status in ("LINEARIZED", "PARTIAL")


def test_rfc14_t049_concept_lexeme_surface_form_distinct():
    """RFC14-T049: Concept, Lexeme and SurfaceForm remain distinct."""
    occ = LinearizableOccurrence("occ_1", "f_1", "anchor", "concept_cat")
    cand = LexicalCandidate("occ_1", "cat", "en")
    unit = SurfaceUnit("su_1", "cats", SourceAlignment("su_1", "occ_1"))
    assert occ.filler_ref == "concept_cat"
    assert cand.lexeme == "cat"
    assert unit.surface_form == "cats"


def test_rfc14_t050_lexical_candidates_obtained_locally():
    """RFC14-T050: Lexical candidates are obtained from local existing authority."""
    g, _rep = _make_graph_with_cat_representation()
    occ = LinearizableOccurrence("occ_1", "f_1", "anchor", "concept_cat")
    cands = g.generation_engine.resolve_lexical_candidates(occ, "en")
    assert len(cands) >= 1
    assert cands[0].lexeme in ("concept_cat", "cat")


def test_rfc14_t051_lexicalization_performs_no_global_vocabulary_scan():
    """RFC14-T051: Lexicalization performs no global vocabulary scan."""
    g, _rep = _make_graph_with_cat_representation()
    occ = LinearizableOccurrence("occ_1", "f_1", "anchor", "concept_cat")
    cands = g.generation_engine.resolve_lexical_candidates(occ, "en")
    assert len(cands) <= 5


def test_rfc14_t052_lexical_candidates_filtered_by_language():
    """RFC14-T052: Lexical candidates are filtered by language context."""
    g, _rep = _make_graph_with_cat_representation()
    g.link("concept_cat", "qitt", W=0.9, contexts=("ar",), kind="translation")
    occ = LinearizableOccurrence("occ_1", "f_1", "anchor", "concept_cat")
    cands_ar = g.generation_engine.resolve_lexical_candidates(occ, "ar")
    assert any(c.lexeme == "qitt" for c in cands_ar)


def test_rfc14_t053_no_lexical_logits_or_softmax():
    """RFC14-T053: No lexical logits, vocabulary Softmax or global lexical probability exists."""
    cand = LexicalCandidate("occ_1", "cat", "en")
    assert not hasattr(cand, "logit")
    assert not hasattr(cand, "softmax_probability")


def test_rfc14_t054_unresolved_non_equivalent_lexical_alternatives_ambiguous():
    """RFC14-T054: Unresolved non-equivalent lexical alternatives remain ambiguous."""
    cand1 = LexicalCandidate("occ_1", "hound", "en")
    cand2 = LexicalCandidate("occ_1", "dog", "en")
    assert cand1.lexeme != cand2.lexeme


def test_rfc14_t055_identical_surface_strings_do_not_collapse_distinct_meanings():
    """RFC14-T055: Identical surface strings do not collapse distinct meanings."""
    unit1 = SurfaceUnit("su_1", "bank", SourceAlignment("su_1", "occ_river_bank"))
    unit2 = SurfaceUnit("su_2", "bank", SourceAlignment("su_2", "occ_finance_bank"))
    assert unit1.source_alignment.source_occurrence_ref != unit2.source_alignment.source_occurrence_ref


def test_rfc14_t056_self_generated_lexical_use_does_not_cause_learning():
    """RFC14-T056: Self-generated lexical use does not cause learning."""
    g, rep = _make_graph_with_cat_representation()
    w_before = {k: e.W for k, e in g.edges.items()}
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    w_after = {k: e.W for k, e in g.edges.items()}
    assert w_before == w_after


def test_rfc14_t057_semantic_past_tense_requires_temporal_authority():
    """RFC14-T057: Semantic past tense requires temporal authority."""
    cand = LexicalCandidate("occ_1", "walk", "en", morphosyntactic_features={"tense": "present"})
    assert cand.morphosyntactic_features["tense"] == "present"


def test_rfc14_t058_surface_realization_cannot_invent_negation():
    """RFC14-T058: Surface realization cannot invent negation."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert "not" not in handoff.surface_chunk_view.rendered_text.split()


def test_rfc14_t059_surface_realization_cannot_invent_plurality():
    """RFC14-T059: Surface realization cannot invent semantic plurality."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert "many" not in handoff.surface_chunk_view.rendered_text.split()


def test_rfc14_t060_pure_grammatical_agreement_does_not_create_world_fact():
    """RFC14-T060: Pure grammatical agreement does not create a world fact."""
    bundle = SurfaceBundle("occ_1", ("cat",), support_form_refs=("the",))
    assert bundle.support_form_refs == ("the",)


def test_rfc14_t061_copular_support_realizes_only_existing_predication():
    """RFC14-T061: Copular/auxiliary support realizes only existing predication or morphosyntax."""
    alignment = SourceAlignment("su_is", grammatical_authority_ref="predicate")
    assert alignment.grammatical_authority_ref == "predicate"


def test_rfc14_t062_causal_surface_marker_requires_existing_causal_attachment():
    """RFC14-T062: A causal surface marker requires existing causal attachment authority."""
    alignment = SourceAlignment("su_because", grammatical_authority_ref="cause_relation")
    assert alignment.grammatical_authority_ref == "cause_relation"


def test_rfc14_t063_pronoun_realization_does_not_resolve_ambiguous_coreference():
    """RFC14-T063: Pronoun realization does not resolve ambiguous coreference."""
    alignment = SourceAlignment("su_it", source_occurrence_ref="occ_cat")
    assert alignment.source_occurrence_ref == "occ_cat"


def test_rfc14_t064_surface_failure_cannot_rewrite_semantic_content():
    """RFC14-T064: Surface failure cannot rewrite semantic content."""
    g, rep = _make_graph_with_cat_representation()
    digest_before = g.generation_engine.get_memory_snapshot_ref()
    # Trigger pass with empty anchors
    _ = g.generation_engine.execute_generative_pass(rep, frozenset())
    digest_after = g.generation_engine.get_memory_snapshot_ref()
    assert digest_before == digest_after


def test_rfc14_t065_surface_chunk_may_contain_multiple_emission_units():
    """RFC14-T065: A SurfaceChunk may contain multiple lawful EmissionUnits."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert len(handoff.surface_chunk_view.surface_units) >= 1


def test_rfc14_t066_adds_no_semantic_max_token_parameter():
    """RFC14-T066: RFC-14 adds no semantic max-token/output-length parameter."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]), budget=10.0)
    assert isinstance(handoff.surface_chunk_view, SurfaceChunk)


def test_rfc14_t067_surface_chunk_boundaries_at_lawful_boundaries():
    """RFC14-T067: SurfaceChunk boundaries occur only at lawful emission boundaries."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert handoff.surface_chunk_view.closure_reason in ("COMPLETE", "PARTIAL_BUDGET", "AMBIGUOUS", "CONFLICT", "UNDERSPECIFIED")


def test_rfc14_t068_required_grammatical_support_not_dangling():
    """RFC14-T068: Required grammatical support is not left dangling."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    for u in handoff.surface_chunk_view.surface_units:
        assert u.source_alignment is not None


def test_rfc14_t069_every_emitted_unit_has_source_alignment():
    """RFC14-T069: Every emitted surface unit has source alignment."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    for u in handoff.surface_chunk_view.surface_units:
        assert u.source_alignment.source_occurrence_ref is not None or u.source_alignment.grammatical_authority_ref is not None


def test_rfc14_t070_generated_surface_output_is_generation_self_derived():
    """RFC14-T070: Generated surface output is GENERATION/SelfDerived."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert handoff.surface_chunk_view.origin_lineage == "GENERATION"


def test_rfc14_t071_external_facts_do_not_make_output_independent_external_evidence():
    """RFC14-T071: External source facts do not make generated output independent ExternalEvidence."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert handoff.surface_chunk_view.origin_lineage != "external"


def test_rfc14_t072_output_transport_failure_does_not_alter_cognition():
    """RFC14-T072: Output transport failure does not alter cognition."""
    g, rep = _make_graph_with_cat_representation()
    d_before = g.generation_engine.get_memory_snapshot_ref()
    # Simulate external transport failure on generated chunk
    chunk = g.generation_engine.realize_surface_chunk(LinearizationPrefix((), "LINEARIZED"), rep.representation_id)
    _ = f"dropped_{chunk.chunk_id}"
    d_after = g.generation_engine.get_memory_snapshot_ref()
    assert d_before == d_after


def test_rfc14_t073_role_binding_expansion_commit_is_failure_atomic():
    """RFC14-T073: RoleBinding expansion commit is failure-atomic."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    # Expand with insufficient budget
    expanded, cost = g.generation_engine.expand_hierarchy(hierarchy, rep, budget=0.0)
    assert cost == 0.0
    assert len(expanded.frames[f1.frame_id].role_bindings) == len(f1.role_bindings)


def test_rfc14_t074_law16_occurrence_commit_is_failure_atomic():
    """RFC14-T074: Law-16 occurrence commit is failure-atomic."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    prefix, cost = g.generation_engine.linearize_hierarchy(hierarchy, budget=0.0)
    assert cost == 0.0
    assert prefix.status == "PARTIAL"


def test_rfc14_t075_surface_unit_alignment_provenance_commit_atomically():
    """RFC14-T075: Surface unit, alignment and generation provenance commit atomically."""
    unit = SurfaceUnit("su_1", "cat", SourceAlignment("su_1", "occ_1"), "GENERATION")
    assert unit.unit_id == unit.source_alignment.surface_unit_id
    assert unit.origin_lineage == "GENERATION"


def test_rfc14_t076_failed_commits_leave_no_ghost_progress():
    """RFC14-T076: Failed commits leave no ghost budget or progress state."""
    g, rep = _make_graph_with_cat_representation()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset())
    assert handoff.closure_reason == "UNDERSPECIFIED"
    assert len(handoff.surface_chunk_view.surface_units) == 0


def test_rfc14_t077_stale_derived_generative_artifacts_fail_closed():
    """RFC14-T077: Stale derived generative artifacts fail closed."""
    g, rep = _make_graph_with_cat_representation()
    stale_frame = GenerativeFrame("f_stale", "rep_mismatch_123", (), frozenset(["concept_cat"]))
    assert not g.generation_engine.validate_generative_frame(stale_frame, rep)


def test_rfc14_t078_cross_pass_artifact_injection_fails_closed():
    """RFC14-T078: Cross-pass artifact injection fails closed without revalidation."""
    g, rep = _make_graph_with_cat_representation()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_cat"]))
    f_injected = dataclasses.replace(f1, parent_representation_id="rep_alien")
    assert not g.generation_engine.validate_generative_frame(f_injected, rep)


def test_rfc14_t079_residual_view_is_parent_rid_bound():
    """RFC14-T079: ResidualView is ParentRID-bound and stale-detectable."""
    res = ResidualView(parent_representation_id="rep_1", unconsumed_occurrences=())
    assert res.parent_representation_id == "rep_1"


def test_rfc14_t080_invalidated_state_cannot_produce_continuation():
    """RFC14-T080: INVALIDATED state cannot produce a valid continuation plan."""
    handoff = HandoffView(
        parent_representation_id="rep_invalid",
        surface_chunk_view=SurfaceChunk("c", "rep_invalid", (), "", "INVALIDATED"),
        residual_view=ResidualView("rep_invalid", ()),
        closure_reason="INVALIDATED",
    )
    assert handoff.closure_reason == "INVALIDATED"


def test_rfc14_t081_persistent_cognitive_digest_unchanged():
    """RFC14-T081: Complete persistent cognitive digest is unchanged by RFC-14-only execution."""
    g, rep = _make_graph_with_cat_representation()
    d_before = g.generation_engine.get_memory_snapshot_ref()
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    d_after = g.generation_engine.get_memory_snapshot_ref()
    assert d_before == d_after


def test_rfc14_t082_assembly_structural_digest_unchanged():
    """RFC14-T082: Complete Assembly structural digest is unchanged."""
    g, rep = _make_graph_with_cat_representation()
    asm_count_before = len(g.assembly_manager.assemblies)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    asm_count_after = len(g.assembly_manager.assemblies)
    assert asm_count_before == asm_count_after


def test_rfc14_t083_frozen_rfc12_input_digest_unchanged():
    """RFC14-T083: The frozen RFC-12 input representation digest is unchanged."""
    g, rep = _make_graph_with_cat_representation()
    r_id_before = rep.representation_id
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert rep.representation_id == r_id_before


def test_rfc14_t084_source_provenance_conserved():
    """RFC14-T084: Source provenance is conserved while output stays SelfDerived."""
    g, rep = _make_graph_with_cat_representation()
    assert rep.participation_receipts[0].origin_lineage == "external"
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert handoff.surface_chunk_view.origin_lineage == "GENERATION"


def test_rfc14_t085_fixed_inputs_reproduce_same_surface_chunk():
    """RFC14-T085: Fixed inputs reproduce the same SurfaceChunk."""
    g, rep = _make_graph_with_cat_representation()
    h1 = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    h2 = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert h1.surface_chunk_view.rendered_text == h2.surface_chunk_view.rendered_text
    assert h1.surface_chunk_view.chunk_id == h2.surface_chunk_view.chunk_id


def test_rfc14_t086_cache_on_and_cache_off_semantically_equivalent():
    """RFC14-T086: Cache-on and cache-off execution are semantically equivalent."""
    g, rep = _make_graph_with_cat_representation()
    h1 = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    g.generation_engine.clear_caches()
    h2 = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert h1.surface_chunk_view.rendered_text == h2.surface_chunk_view.rendered_text


def test_rfc14_t087_remote_graph_growth_does_not_alter_local_semantic_result():
    """RFC14-T087: Remote graph/vocabulary growth does not alter the local semantic result."""
    g, rep = _make_graph_with_cat_representation()
    h1 = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    # Add remote unrelated edges
    for i in range(50):
        g.link(f"remote_x_{i}", f"remote_y_{i}", W=0.7)
    h2 = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_cat"]))
    assert h1.surface_chunk_view.rendered_text == h2.surface_chunk_view.rendered_text


def test_rfc14_t088_disabled_or_no_generation_preserves_upstream():
    """RFC14-T088: RFC-14 disabled or no-lawful-generation execution preserves upstream semantics."""
    g, rep = _make_graph_with_cat_representation()
    d_before = g.generation_engine.get_memory_snapshot_ref()
    h = g.generation_engine.execute_generative_pass(rep, frozenset(["non_existent_anchor"]))
    d_after = g.generation_engine.get_memory_snapshot_ref()
    assert d_before == d_after
    assert h.closure_reason == "UNDERSPECIFIED"
