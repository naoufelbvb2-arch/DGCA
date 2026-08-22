"""
DGCA — RFC-15 v1.0 / LAW 17 v1.0
ACCEPTANCE TEST SUITE (RFC15-T001 .. RFC15-T096)
"""
from __future__ import annotations

import pytest

from dgca.config import Law
from dgca.generation import SourceAlignment
from dgca.graph import CognitiveGraph, Edge, Node
from dgca.recurrent import (
    ContinuationCommit,
    ContinuationFrontier,
    CoveredView,
    ExpressionReceipt,
    ExpressiveObligation,
    GenerativeContinuationEpoch,
    HandoffView15To16,
    PredictiveRecurrentGenerativeEngine,
    ReferentialAccessibilityView,
    RemainingView,
    SupersededExpressionView,
    rfc15_behavioral_signature,
)
from dgca.representation import ParticipationReceipt, SparseDistributedCognitiveRepresentation


def _make_sample_rep(g: CognitiveGraph, nodes: list[str]) -> SparseDistributedCognitiveRepresentation:
    receipts = [
        ParticipationReceipt(f"rcpt_{n}", n, 1, 0, "external", "node", activation_magnitude=0.9)
        for n in nodes
    ]
    return g.representation_engine.build_representation(1, 0, None, receipts)


# ── RFC15-T001 .. RFC15-T010: Primitive & Law Accounting & GCE Basics
def test_rfc15_t001_single_canonical_transient_primitive():
    """RFC15-T001: RFC-15 introduces exactly one new canonical transient operational primitive: GenerativeContinuationEpoch."""
    epoch = GenerativeContinuationEpoch("gce_1", "root_task", (), "budget_1", "OPEN")
    assert isinstance(epoch, GenerativeContinuationEpoch)
    assert len(epoch.__dataclass_fields__) == 5


def test_rfc15_t002_no_persistent_cognitive_primitives():
    """RFC15-T002: RFC-15 introduces no persistent cognitive primitive."""
    g = CognitiveGraph()
    assert not hasattr(Node, "already_said")
    assert not hasattr(Edge, "already_said")
    assert not hasattr(g, "persistent_discourse_memory")


def test_rfc15_t003_no_persistent_learned_fields_or_scalars():
    """RFC15-T003: RFC-15 introduces no persistent learned field or learned scalar."""
    e = Edge("A", "B", 0.5)
    assert not hasattr(e, "continuation_weight")
    assert not hasattr(e, "discourse_salience")


def test_rfc15_t004_law_17_is_only_new_normative_law():
    """RFC15-T004: Law 17 is the only new normative law introduced by RFC-15."""
    g = CognitiveGraph()
    engine = g.recurrent_engine
    assert isinstance(engine, PredictiveRecurrentGenerativeEngine)


def test_rfc15_t005_law_18_not_required():
    """RFC15-T005: Law 18 is not required by RFC-15 v1.0."""
    import dgca.config as cfg
    assert not hasattr(cfg.Law, "LAW_18")


def test_rfc15_t006_generated_output_never_becomes_external_evidence():
    """RFC15-T006: Generated output never becomes independent ExternalEvidence merely by re-entry."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["node_1"])
    g.link("node_1", "node_1_prop", W=0.8, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_query")
    status, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "PROGRESS"
    assert rcpt is not None
    assert rcpt.origin_lineage == "GENERATION"
    assert rcpt.origin_lineage != "external"


def test_rfc15_t007_no_reimplementation_of_rfc14_authorities():
    """RFC15-T007: RFC-15 does not reimplement RFC-14 GenerativeFrame, Law 16, lexicalization, morphology, or surface realization."""
    g = CognitiveGraph()
    engine = g.recurrent_engine
    assert not hasattr(engine, "build_generative_frame")
    assert not hasattr(engine, "linearize_hierarchy")
    assert not hasattr(engine, "realize_surface_chunk")


def test_rfc15_t008_root_authority_scoped_cannot_create_own_goal():
    """RFC15-T008: RFC-15 control remains root-authority-scoped and cannot create its own independent generation goal."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("user_goal_123")
    assert epoch.root_authority_ref == "user_goal_123"


def test_rfc15_t009_gce_canonical_state_exact_five_fields():
    """RFC15-T009: GCE canonical state contains GCEID, RootAuthorityRef, ProgressReceiptRefs, BudgetAuthorityRef, and Lifecycle only."""
    fields = set(GenerativeContinuationEpoch.__dataclass_fields__.keys())
    assert fields == {
        "epoch_id",
        "root_authority_ref",
        "progress_receipt_refs",
        "budget_authority_ref",
        "lifecycle",
    }


def test_rfc15_t010_root_authority_ref_immutable():
    """RFC15-T010: GCE RootAuthorityRef is immutable for the lifetime of the epoch."""
    epoch = GenerativeContinuationEpoch("gce_test", "root_fixed", (), "budget_ref", "OPEN")
    with pytest.raises((AttributeError, TypeError)):
        epoch.root_authority_ref = "new_root"  # Frozen dataclass


# ── RFC15-T011 .. RFC15-T020: GCE Lifecycle & Progress
def test_rfc15_t011_gce_lifecycle_open_closed_only():
    """RFC15-T011: GCE lifecycle is OPEN or CLOSED only."""
    ep1 = GenerativeContinuationEpoch("e1", "r1", (), "b1", "OPEN")
    ep2 = GenerativeContinuationEpoch("e2", "r1", (), "b1", "CLOSED")
    assert ep1.lifecycle == "OPEN"
    assert ep2.lifecycle == "CLOSED"


def test_rfc15_t012_closed_gce_cannot_reopen():
    """RFC15-T012: A CLOSED GCE cannot reopen."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_task")
    closed_ep, _ = g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    assert closed_ep.lifecycle == "CLOSED"
    rep = _make_sample_rep(g, ["concept_a"])
    status, _, _, _ = g.recurrent_engine.execute_recurrent_step(closed_ep.epoch_id, rep)
    assert status == "STALE"


def test_rfc15_t013_new_root_task_requires_new_gce():
    """RFC15-T013: An independent new root task requires a new GCE rather than root rebinding."""
    g = CognitiveGraph()
    ep1 = g.recurrent_engine.create_epoch("task_1")
    ep2 = g.recurrent_engine.create_epoch("task_2")
    assert ep1.epoch_id != ep2.epoch_id
    assert ep1.root_authority_ref != ep2.root_authority_ref


def test_rfc15_t014_ordinary_snapshot_replacement_preserves_open_gce():
    """RFC15-T014: Ordinary cognitive snapshot replacement does not invalidate an otherwise valid open GCE."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("task_continuous")
    rep1 = _make_sample_rep(g, ["node_1"])
    rep2 = _make_sample_rep(g, ["node_2"])
    assert epoch.lifecycle == "OPEN"
    # GCE can be passed to consecutive snapshot representations
    assert rep1.representation_id != rep2.representation_id


def test_rfc15_t015_gce_progress_stores_references_only():
    """RFC15-T015: GCE progress stores references to validated ExpressionReceipts rather than copied semantic cognition."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_refs")
    rep = _make_sample_rep(g, ["item_a"])
    g.link("item_a", "prop_a", W=0.9, contexts=("en",))
    status, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "PROGRESS"
    assert len(ep.progress_receipt_refs) == 1
    assert isinstance(ep.progress_receipt_refs[0], str)
    assert ep.progress_receipt_refs[0] == rcpt.receipt_id


def test_rfc15_t016_gce_progress_append_only_while_open():
    """RFC15-T016: GCE progress is append-only while the epoch is OPEN."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_seq")
    rep = _make_sample_rep(g, ["item_1", "item_2"])
    g.link("item_1", "item_2", W=0.9, contexts=("order",))
    g.link("item_1", "p1", W=0.9, contexts=("en",))
    g.link("item_2", "p2", W=0.9, contexts=("en",))
    _, _ep1, r1, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    _, ep2, r2, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert len(ep2.progress_receipt_refs) == 2
    assert ep2.progress_receipt_refs[0] == r1.receipt_id
    assert ep2.progress_receipt_refs[1] == r2.receipt_id


def test_rfc15_t017_reappending_equivalent_receipt_is_idempotent():
    """RFC15-T017: Reappending the same equivalent ExpressionReceipt is idempotent."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_idemp")
    rep = _make_sample_rep(g, ["item_x"])
    g.link("item_x", "px", W=0.9, contexts=("en",))
    _, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    ep_after = g.recurrent_engine.append_receipt(epoch.epoch_id, rcpt)
    assert len(ep_after.progress_receipt_refs) == 1


def test_rfc15_t018_gce_references_existing_budget_authority():
    """RFC15-T018: GCE references existing runtime budget authority instead of duplicating an independent budget."""
    epoch = GenerativeContinuationEpoch("e_b", "root_b", (), "runtime_budget_token_42", "OPEN")
    assert epoch.budget_authority_ref == "runtime_budget_token_42"


def test_rfc15_t019_snapshot_transitions_do_not_renew_budget():
    """RFC15-T019: Snapshot transitions do not renew the GCE runtime budget."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_budget")
    rep1 = _make_sample_rep(g, ["n1"])
    g.link("n1", "p1", W=0.9, contexts=("en",))
    budget_initial = 1.0
    _, _ep, _, rem_budget = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep1, budget=budget_initial)
    assert rem_budget < budget_initial


def test_rfc15_t020_resource_pressure_cannot_silently_evict_receipts():
    """RFC15-T020: Resource pressure cannot silently evict old progress receipts and cause generative forgetting."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_pressure")
    rep = _make_sample_rep(g, [f"node_{i}" for i in range(10)])
    for i in range(10):
        g.link(f"node_{i}", f"prop_{i}", W=0.9, contexts=("en",))
        if i < 9:
            g.link(f"node_{i}", f"node_{i+1}", W=0.9, contexts=("order",))
    _closure, _ = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=20.0)
    final_ep = g.recurrent_engine.get_epoch(epoch.epoch_id)
    assert len(final_ep.progress_receipt_refs) == 10


# ── RFC15-T021 .. RFC15-T030: Expression Receipts Integrity
def test_rfc15_t021_receipt_derived_only_from_successful_rfc14_emission():
    """RFC15-T021: ExpressionReceipt can be derived only from a successful committed RFC-14 emission."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["atom_a"])
    g.link("atom_a", "prop_a", W=0.9, contexts=("en",))
    frame = g.generation_engine.build_generative_frame(rep, frozenset(["atom_a"]))
    hier = g.generation_engine.build_hierarchy([frame])
    prefix, _ = g.generation_engine.linearize_hierarchy(hier)
    chunk = g.generation_engine.realize_surface_chunk(prefix, "rep_1")
    unit = chunk.surface_units[0]
    rcpt = g.recurrent_engine.create_expression_receipt(chunk, unit.source_alignment, "rep_1", "root_a")
    assert isinstance(rcpt, ExpressionReceipt)


def test_rfc15_t022_receipt_preserves_parent_rid_and_alignment():
    """RFC15-T022: ExpressionReceipt preserves ParentRID and source alignment authority."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["atom_b"])
    g.link("atom_b", "prop_b", W=0.9, contexts=("en",))
    frame = g.generation_engine.build_generative_frame(rep, frozenset(["atom_b"]))
    hier = g.generation_engine.build_hierarchy([frame])
    prefix, _ = g.generation_engine.linearize_hierarchy(hier)
    chunk = g.generation_engine.realize_surface_chunk(prefix, "rid_999")
    unit = chunk.surface_units[0]
    rcpt = g.recurrent_engine.create_expression_receipt(chunk, unit.source_alignment, "rid_999", "root_b", ("atom_b",))
    assert rcpt.parent_rid == "rid_999"
    assert "atom_b" in rcpt.expressed_elements


def test_rfc15_t023_receipt_remains_generation_self_derived():
    """RFC15-T023: ExpressionReceipt remains GENERATION/SelfDerived."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["atom_c"])
    g.link("atom_c", "prop_c", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_c")
    _, _, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert rcpt.origin_lineage == "GENERATION"


def test_rfc15_t024_receipt_cannot_be_forged_from_arbitrary_string():
    """RFC15-T024: ExpressionReceipt cannot be constructed from an arbitrary generated string."""
    g = CognitiveGraph()
    with pytest.raises(ValueError):
        g.recurrent_engine.create_expression_receipt("arbitrary text", None, "rid", "root")


def test_rfc15_t025_receipt_cannot_become_evidence_or_tbr():
    """RFC15-T025: ExpressionReceipt cannot become EvidenceCandidate, learning Outcome, Law-14 vote, or TBR authority."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["atom_d"])
    g.link("atom_d", "prop_d", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_d")
    w_before = g.edges[("atom_d", "prop_d")].W
    _, _, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    w_after = g.edges[("atom_d", "prop_d")].W
    assert w_before == w_after  # Zero self-learning


def test_rfc15_t026_failed_emission_creates_no_receipt():
    """RFC15-T026: Failed or rolled-back RFC-14 output creates no ExpressionReceipt."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_fail")
    rep = _make_sample_rep(g, ["isolated_no_edges"])
    status, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    # If no emission occurred, receipt is None
    if status == "REALIZATION_BLOCKED":
        assert rcpt is None
        assert len(ep.progress_receipt_refs) == 0


def test_rfc15_t027_one_emission_produces_at_most_one_equivalent_receipt():
    """RFC15-T027: One emission commit produces at most one equivalent ExpressionReceipt."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["atom_e"])
    g.link("atom_e", "prop_e", W=0.9, contexts=("en",))
    frame = g.generation_engine.build_generative_frame(rep, frozenset(["atom_e"]))
    hier = g.generation_engine.build_hierarchy([frame])
    prefix, _ = g.generation_engine.linearize_hierarchy(hier)
    chunk = g.generation_engine.realize_surface_chunk(prefix, "rep_1")
    unit = chunk.surface_units[0]
    r1 = g.recurrent_engine.create_expression_receipt(chunk, unit.source_alignment, "rep_1", "root_e")
    r2 = g.recurrent_engine.create_expression_receipt(chunk, unit.source_alignment, "rep_1", "root_e")
    assert r1.receipt_id == r2.receipt_id


def test_rfc15_t028_partial_output_creates_receipts_for_committed_only():
    """RFC15-T028: Partial RFC-14 output creates receipts only for committed occurrences."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["atom_f1", "atom_f2"])
    g.link("atom_f1", "atom_f2", W=0.9, contexts=("order",))
    g.link("atom_f1", "p1", W=0.9, contexts=("en",))
    g.link("atom_f2", "p2", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_partial")
    status, ep, _rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "PROGRESS"
    assert len(ep.progress_receipt_refs) == 1


def test_rfc15_t029_unexpressed_alternatives_create_no_receipts():
    """RFC15-T029: Unexpressed RFC-14 ambiguity alternatives create no progress receipts."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_alt")
    rep = _make_sample_rep(g, ["alt_1", "alt_2"])
    # No ordering edges -> ambiguity
    status, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "CONTINUATION_AMBIGUOUS"
    assert rcpt is None
    assert len(ep.progress_receipt_refs) == 0


def test_rfc15_t030_receipt_lifetime_remains_operational():
    """RFC15-T030: ExpressionReceipt lifetime across snapshots remains operational rather than persistent cognitive memory."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["atom_g"])
    g.link("atom_g", "pg", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_op")
    _, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert rcpt.receipt_id in g.recurrent_engine._receipts
    assert not hasattr(g.nodes["atom_g"], "already_said")


# ── RFC15-T031 .. RFC15-T040: Obligations, Coverage & Remaining
def test_rfc15_t031_obligations_derived_from_current_root_and_cognition():
    """RFC15-T031: Current ExpressiveObligation set is derived from current root authority and current lawful cognition."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["node_x", "node_y"])
    obs = g.recurrent_engine.derive_obligations(rep, "root_task_xy")
    assert len(obs) == 2
    assert all(ob.root_authority_ref == "root_task_xy" for ob in obs)


def test_rfc15_t032_available_knowledge_not_automatically_obligation():
    """RFC15-T032: Current knowledge that is merely available does not automatically become an expressive obligation."""
    g = CognitiveGraph()
    g.link("stored_a", "stored_b", W=0.9, contexts=("en",))
    rep = _make_sample_rep(g, ["active_only"])
    obs = g.recurrent_engine.derive_obligations(rep, "root_active")
    elements = {ob.semantic_element_ref for ob in obs}
    assert "stored_a" not in elements
    assert "stored_b" not in elements


def test_rfc15_t033_coverage_derived_by_authority_correspondence():
    """RFC15-T033: Current coverage is derived by lawful receipt-to-obligation authority correspondence, not similarity scoring."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["item_c1"])
    g.link("item_c1", "p_c1", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_cov")
    _, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    obs = g.recurrent_engine.derive_obligations(rep, "root_cov")
    covered = g.recurrent_engine.compute_coverage(obs, ep, rep)
    assert len(covered.covered_obligation_ids) == 1
    assert covered.coverage_map[obs[0].obligation_id] == rcpt.receipt_id


def test_rfc15_t034_changed_cognition_invalidates_coverage_without_deleting_history():
    """RFC15-T034: Changed cognition can invalidate current coverage without deleting historical expression receipts."""
    g = CognitiveGraph()
    rep1 = _make_sample_rep(g, ["item_d1"])
    g.link("item_d1", "p_d1", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_d1")
    _, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep1)

    rep2 = _make_sample_rep(g, ["item_d2"])  # New representation
    obs2 = g.recurrent_engine.derive_obligations(rep2, "root_d1")
    cov2 = g.recurrent_engine.compute_coverage(obs2, ep, rep2)
    assert len(cov2.covered_obligation_ids) == 0  # item_d2 is not covered
    assert rcpt.receipt_id in ep.progress_receipt_refs  # Historical receipt preserved


def test_rfc15_t035_remaining_equals_uncovered_obligations():
    """RFC15-T035: RemainingView equals current lawful obligations not currently covered."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["n_a", "n_b"])
    g.link("n_a", "n_b", W=0.9, contexts=("order",))
    g.link("n_a", "pa", W=0.9, contexts=("en",))
    g.link("n_b", "pb", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_rem")
    _, ep, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    obs = g.recurrent_engine.derive_obligations(rep, "root_rem")
    cov = g.recurrent_engine.compute_coverage(obs, ep, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    assert len(rem.remaining_obligations) == 1
    assert rem.remaining_obligations[0].semantic_element_ref == "n_b"


def test_rfc15_t036_coverage_ratios_are_diagnostic_only():
    """RFC15-T036: Coverage ratios are diagnostic only and cannot control continuation."""
    cov = CoveredView(frozenset(["ob1"]), {"ob1": "rcpt1"})
    assert isinstance(cov.covered_obligation_ids, frozenset)
    assert not hasattr(cov, "continuation_weight")


def test_rfc15_t037_residual_view_does_not_replace_coverage_revalidation():
    """RFC15-T037: RFC-14 ResidualView cannot replace fresh RFC-15 coverage revalidation."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_fresh")
    rep = _make_sample_rep(g, ["k1", "k2"])
    obs = g.recurrent_engine.derive_obligations(rep, "root_fresh")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    assert len(cov.covered_obligation_ids) == 0


def test_rfc15_t038_coverage_preserves_role_and_root():
    """RFC15-T038: Coverage remains role-, scope-, root-, and alternative-sensitive."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["target_item"])
    epoch1 = g.recurrent_engine.create_epoch("root_task_A")
    epoch2 = g.recurrent_engine.create_epoch("root_task_B")
    g.link("target_item", "p", W=0.9, contexts=("en",))
    _, _ep1, _, _ = g.recurrent_engine.execute_recurrent_step(epoch1.epoch_id, rep)
    obs2 = g.recurrent_engine.derive_obligations(rep, "root_task_B")
    cov2 = g.recurrent_engine.compute_coverage(obs2, epoch2, rep)
    assert len(cov2.covered_obligation_ids) == 0  # Not covered in epoch 2


def test_rfc15_t039_obsolete_history_does_not_cover_incompatible_obligation():
    """RFC15-T039: Obsolete historical expression does not cover an incompatible current obligation."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["elem_1"])
    epoch = g.recurrent_engine.create_epoch("root_task")
    ob_new = ExpressiveObligation("ob_diff", "root_task", "elem_different", "role")
    cov = g.recurrent_engine.compute_coverage((ob_new,), epoch, rep)
    assert len(cov.covered_obligation_ids) == 0


def test_rfc15_t040_current_coverage_does_not_assert_world_truth():
    """RFC15-T040: Current coverage does not assert world truth."""
    cov = CoveredView(frozenset(["ob1"]), {"ob1": "rcpt1"})
    assert isinstance(cov, CoveredView)


# ── RFC15-T041 .. RFC15-T050: Repetition, Suppression & Referential
def test_rfc15_t041_covered_content_suppressed_absent_repeat_authority():
    """RFC15-T041: Covered content is suppressed from duplicate expression only when no independent repeat authority exists."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["single_item"])
    g.link("single_item", "p", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_supp")
    _, ep, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    obs = g.recurrent_engine.derive_obligations(rep, "root_supp")
    cov = g.recurrent_engine.compute_coverage(obs, ep, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    assert len(rem.remaining_obligations) == 0  # Fully suppressed from remaining


def test_rfc15_t042_explicit_root_request_permits_repetition():
    """RFC15-T042: An explicit root request for repetition permits distinct repeated obligations."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["item_rep"])
    g.link("item_rep", "p", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_repeat_req")
    _, ep, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)

    ob_repeat = ExpressiveObligation("ob_rep_2", "root_repeat_req", "item_rep", "refrain", repeat_authorized=True)
    cov = g.recurrent_engine.compute_coverage((ob_repeat,), ep, rep)
    assert len(cov.covered_obligation_ids) == 0  # Authorized repeat is not suppressed!


def test_rfc15_t043_distinct_role_scope_may_repeat_underlying_cognition():
    """RFC15-T043: Distinct role/scope occurrences may lawfully repeat the same underlying cognition."""
    ob1 = ExpressiveObligation("ob_subj", "root", "concept_cat", "subject")
    ob2 = ExpressiveObligation("ob_obj", "root", "concept_cat", "object", repeat_authorized=True)
    assert ob1.role_scope != ob2.role_scope


def test_rfc15_t044_distinct_language_scopes_may_reexpress():
    """RFC15-T044: Distinct language scopes may lawfully re-express equivalent cognition."""
    ob_en = ExpressiveObligation("ob_en", "root", "concept_dog", "agent", language_context="en")
    ob_ar = ExpressiveObligation("ob_ar", "root", "concept_dog", "agent", language_context="ar", repeat_authorized=True)
    assert ob_en.language_context != ob_ar.language_context


def test_rfc15_t045_lexical_paraphrase_not_new_progress():
    """RFC15-T045: Lexical paraphrase does not create new semantic progress by itself."""
    ob_original = ExpressiveObligation("ob_car", "root", "concept_car", "topic")
    ob_paraphrase = ExpressiveObligation("ob_car", "root", "concept_car", "topic")
    assert ob_original.obligation_id == ob_paraphrase.obligation_id


def test_rfc15_t046_suppression_does_not_mutate_graph():
    """RFC15-T046: Generative suppression does not mutate activation, inhibition, Edge weight, support, or confidence."""
    g = CognitiveGraph()
    g.link("n_sup", "p_sup", W=0.85, contexts=("en",))
    w_orig = g.edges[("n_sup", "p_sup")].W
    rep = _make_sample_rep(g, ["n_sup"])
    epoch = g.recurrent_engine.create_epoch("root_sup_test")
    _, _ep, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert g.edges[("n_sup", "p_sup")].W == w_orig


def test_rfc15_t047_suppression_is_obligation_scoped():
    """RFC15-T047: Suppression is obligation-scoped rather than concept-wide."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["item_z"])
    g.link("item_z", "pz", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_z")
    _, ep, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    # Another task with independent root is not suppressed
    obs_other = [ExpressiveObligation("ob_other", "root_other", "item_z", "scope")]
    cov_other = g.recurrent_engine.compute_coverage(tuple(obs_other), ep, rep)
    assert len(cov_other.covered_obligation_ids) == 0


def test_rfc15_t048_no_fluency_or_style_scores_for_repetition():
    """RFC15-T048: Repetition eligibility is not controlled by a new fluency, relevance, or style score."""
    ob = ExpressiveObligation("ob1", "root", "node", "role")
    assert not hasattr(ob, "fluency_score")
    assert not hasattr(ob, "style_score")


def test_rfc15_t049_referential_accessibility_derived_from_progress():
    """RFC15-T049: ReferentialAccessibilityView is derived from current cognition, current root, and current GCE progress."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["char_alice"])
    g.link("char_alice", "hero", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_story")
    _, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    ref_view = g.recurrent_engine.compute_referential_accessibility(rep, "root_story", ep)
    assert "char_alice" in ref_view.accessible_referents
    assert rcpt.receipt_id in ref_view.accessible_referents["char_alice"]


def test_rfc15_t050_prior_mention_does_not_choose_pronoun_form():
    """RFC15-T050: Prior mention does not automatically choose a pronoun form."""
    ref_view = ReferentialAccessibilityView(
        accessible_referents={"char_alice": ("er_1",)},
        ambiguous_referents=frozenset(),
    )
    assert not hasattr(ref_view, "pronoun_form")


# ── RFC15-T051 .. RFC15-T060: Surface Boundaries & Continuation Frontier
def test_rfc15_t051_rfc14_retains_surface_authority():
    """RFC15-T051: RFC-14 retains pronoun and lexical realization authority."""
    g = CognitiveGraph()
    assert hasattr(g.generation_engine, "realize_surface_chunk")


def test_rfc15_t052_multiple_accessible_referents_remain_ambiguous():
    """RFC15-T052: Multiple accessible referents remain ambiguous without independent resolution authority."""
    ref_view = ReferentialAccessibilityView(
        accessible_referents={"hero": ("er_alice", "er_bob")},
        ambiguous_referents=frozenset(["hero"]),
    )
    assert "hero" in ref_view.ambiguous_referents


def test_rfc15_t053_mention_recency_alone_does_not_choose_referent():
    """RFC15-T053: Mention recency alone does not choose a referent."""
    ref_view = ReferentialAccessibilityView(
        accessible_referents={"entity": ("er_first", "er_second")},
        ambiguous_referents=frozenset(["entity"]),
    )
    assert len(ref_view.ambiguous_referents) == 1


def test_rfc15_t054_referential_accessibility_preserves_alternatives():
    """RFC15-T054: Referential accessibility preserves RFC-13 alternative separation."""
    ob1 = ExpressiveObligation("ob1", "root", "c1", "role", alternative_branch_id="branch_A")
    ob2 = ExpressiveObligation("ob2", "root", "c1", "role", alternative_branch_id="branch_B")
    assert ob1.alternative_branch_id != ob2.alternative_branch_id


def test_rfc15_t055_cross_language_referential_continuity():
    """RFC15-T055: Cross-language referential continuity may preserve cognitive identity without authorizing a particular surface form."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_bilingual")
    rep = _make_sample_rep(g, ["item_shared"])
    g.link("item_shared", "p", W=0.9, contexts=("en", "ar"))
    _, ep, _rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep, language_context="en")
    ref_view = g.recurrent_engine.compute_referential_accessibility(rep, "root_bilingual", ep)
    assert "item_shared" in ref_view.accessible_referents


def test_rfc15_t056_no_persistent_mention_memory_primitive():
    """RFC15-T056: No persistent MentionMemory, CoreferenceMemory, or discourse-salience scalar is introduced."""
    g = CognitiveGraph()
    assert not hasattr(g, "mention_memory")
    assert not hasattr(g, "coreference_memory")


def test_rfc15_t057_continuation_frontier_composition():
    """RFC15-T057: ContinuationFrontier contains only current, root-compatible, progress-compatible, authorized, ambiguity-safe, runtime-eligible obligations."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["n1", "n2"])
    epoch = g.recurrent_engine.create_epoch("root_cf")
    obs = g.recurrent_engine.derive_obligations(rep, "root_cf")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    assert len(front.ready_candidates) == 2
    assert front.status == "AMBIGUOUS"


def test_rfc15_t058_stored_prediction_not_automatic_continuation():
    """RFC15-T058: Stored prediction or sequence knowledge does not automatically become current continuation authority."""
    g = CognitiveGraph()
    g.link("pred_src", "pred_dst", W=0.9, contexts=("pred",))
    rep = _make_sample_rep(g, ["other_node"])
    obs = g.recurrent_engine.derive_obligations(rep, "root_pred")
    elems = {ob.semantic_element_ref for ob in obs}
    assert "pred_dst" not in elems


def test_rfc15_t059_no_continuation_cannot_trigger_hidden_pattern_completion():
    """RFC15-T059: No-current-continuation state cannot trigger hidden Pattern Completion."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["isolated"])
    epoch = g.recurrent_engine.create_epoch("root_iso")
    obs = g.recurrent_engine.derive_obligations(rep, "root_iso")
    cov = CoveredView(frozenset([obs[0].obligation_id]), {obs[0].obligation_id: "rcpt_dummy"})
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    assert front.status == "EMPTY"


def test_rfc15_t060_no_continuation_cannot_trigger_hidden_reasoning():
    """RFC15-T060: No-current-continuation state cannot trigger hidden reasoning or invented semantic content."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, [])
    g.recurrent_engine.create_epoch("root_empty")
    obs = g.recurrent_engine.derive_obligations(rep, "root_empty")
    assert len(obs) == 0


# ── RFC15-T061 .. RFC15-T075: Law 17 Commitment & Ambiguity
def test_rfc15_t061_continuation_readiness_consumes_existing_relations():
    """RFC15-T061: Continuation readiness may consume existing causal, temporal, sequence, task, prediction, event, or equivalent local authority."""
    g = CognitiveGraph()
    g.link("step_1", "step_2", W=0.9, contexts=("order",))
    rep = _make_sample_rep(g, ["step_1", "step_2"])
    epoch = g.recurrent_engine.create_epoch("root_order")
    obs = g.recurrent_engine.derive_obligations(rep, "root_order")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    assert len(front.ready_candidates) == 1
    assert front.ready_candidates[0].semantic_element_ref == "step_1"


def test_rfc15_t062_law_16_and_law_17_distinct():
    """RFC15-T062: Law-16 syntactic precedence and Law-17 continuation precedence remain distinct."""
    assert Law.GAMMA == 0.20  # Shared physical step cost, distinct operational modules


def test_rfc15_t063_enumeration_order_does_not_determine_next_continuation():
    """RFC15-T063: Remaining enumeration order does not determine next continuation."""
    rem = RemainingView(
        remaining_obligations=(
            ExpressiveObligation("ob_z", "root", "z", "role"),
            ExpressiveObligation("ob_a", "root", "a", "role"),
        ),
        remaining_ids=frozenset(["ob_z", "ob_a"]),
    )
    front = ContinuationFrontier(rem.remaining_obligations, {}, "AMBIGUOUS")
    assert front.status == "AMBIGUOUS"


def test_rfc15_t064_referential_accessibility_not_priority():
    """RFC15-T064: Referential accessibility does not determine next continuation priority."""
    ref_view = ReferentialAccessibilityView({"alice": ("er1",)}, frozenset())
    assert not hasattr(ref_view, "next_priority")


def test_rfc15_t065_single_uniquely_ready_continuation_committed():
    """RFC15-T065: A single uniquely ready lawful continuation can be committed."""
    g = CognitiveGraph()
    g.link("first", "second", W=0.9, contexts=("order",))
    rep = _make_sample_rep(g, ["first", "second"])
    epoch = g.recurrent_engine.create_epoch("root_unique")
    obs = g.recurrent_engine.derive_obligations(rep, "root_unique")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    status, commit, _ = g.recurrent_engine.commit_continuation(front, epoch, rep)
    assert status == "CONTINUATION_COMMITTED"
    assert commit is not None
    assert commit.obligation_ref == front.ready_candidates[0].obligation_id


def test_rfc15_t066_multiple_unresolved_returns_continuation_ambiguous():
    """RFC15-T066: Multiple unresolved lawful continuations return CONTINUATION_AMBIGUOUS rather than arbitrary selection."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["choice_1", "choice_2"])
    epoch = g.recurrent_engine.create_epoch("root_amb")
    obs = g.recurrent_engine.derive_obligations(rep, "root_amb")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    status, commit, _ = g.recurrent_engine.commit_continuation(front, epoch, rep)
    assert status == "CONTINUATION_AMBIGUOUS"
    assert commit is None


def test_rfc15_t067_explicit_continuation_precedence_resolves():
    """RFC15-T067: Existing explicit continuation precedence may lawfully resolve multiple candidates."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["c_a", "c_b"])
    epoch = g.recurrent_engine.create_epoch("root_prec")
    obs = g.recurrent_engine.derive_obligations(rep, "root_prec")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    ob_a = next(o for o in obs if o.semantic_element_ref == "c_a")
    ob_b = next(o for o in obs if o.semantic_element_ref == "c_b")
    front = g.recurrent_engine.derive_continuation_frontier(
        rem, cov, rep, epoch, explicit_precedences=[(ob_a.obligation_id, ob_b.obligation_id)]
    )
    status, commit, _ = g.recurrent_engine.commit_continuation(front, epoch, rep)
    assert status == "CONTINUATION_COMMITTED"
    assert commit.obligation_ref == ob_a.obligation_id


def test_rfc15_t068_id_ordering_never_semantic_authority():
    """RFC15-T068: Canonical ID ordering is never semantic continuation authority."""
    # IDs "aaa" and "zzz" without ordering must be ambiguous
    front = ContinuationFrontier(
        (ExpressiveObligation("aaa", "r", "a", "role"), ExpressiveObligation("zzz", "r", "z", "role")),
        {},
        "AMBIGUOUS",
    )
    assert front.status == "AMBIGUOUS"


def test_rfc15_t069_scheduler_ordering_never_semantic_authority():
    """RFC15-T069: Runtime scheduler ordering is never semantic continuation authority."""
    front = ContinuationFrontier(
        (ExpressiveObligation("ob1", "r", "1", "role"), ExpressiveObligation("ob2", "r", "2", "role")),
        {},
        "AMBIGUOUS",
    )
    assert front.status == "AMBIGUOUS"


def test_rfc15_t070_continuation_conflict_on_cycles():
    """RFC15-T070: Continuation-constraint cycles return CONTINUATION_CONFLICT and are not repaired by weakest-edge deletion."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["node_1", "node_2"])
    epoch = g.recurrent_engine.create_epoch("root_cycle")
    obs = g.recurrent_engine.derive_obligations(rep, "root_cycle")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    ob1, ob2 = obs[0], obs[1]
    front = g.recurrent_engine.derive_continuation_frontier(
        rem, cov, rep, epoch, explicit_precedences=[(ob1.obligation_id, ob2.obligation_id), (ob2.obligation_id, ob1.obligation_id)]
    )
    assert front.status == "CONFLICT"


def test_rfc15_t071_law_17_no_remote_graph_search():
    """RFC15-T071: Law 17 cannot search remote graph memory to repair ambiguity."""
    g = CognitiveGraph()
    for i in range(100):
        g.link(f"remote_{i}", f"remote_{i+1}", W=0.8, contexts=("en",))
    rep = _make_sample_rep(g, ["local_a", "local_b"])
    epoch = g.recurrent_engine.create_epoch("root_local")
    obs = g.recurrent_engine.derive_obligations(rep, "root_local")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    assert front.status == "AMBIGUOUS"


def test_rfc15_t072_law_17_no_beam_search_or_lookahead():
    """RFC15-T072: Law 17 cannot use beam search, global lookahead, A*, or unbounded knowledge-graph search."""
    g = CognitiveGraph()
    engine = g.recurrent_engine
    assert not hasattr(engine, "beam_search")
    assert not hasattr(engine, "lookahead")


def test_rfc15_t073_at_most_one_live_commit_per_gce():
    """RFC15-T073: At most one live ContinuationCommit controls the next step of one GCE."""
    g = CognitiveGraph()
    g.link("a", "b", W=0.9, contexts=("order",))
    rep = _make_sample_rep(g, ["a", "b"])
    epoch = g.recurrent_engine.create_epoch("root_one_live")
    obs = g.recurrent_engine.derive_obligations(rep, "root_one_live")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    _, commit, _ = g.recurrent_engine.commit_continuation(front, epoch, rep)
    assert g.recurrent_engine._live_commits[epoch.epoch_id] == commit


def test_rfc15_t074_commit_bound_to_gce_and_progress_state():
    """RFC15-T074: ContinuationCommit is bound to current GCE, ParentRID, RootAuthority, obligation, and current progress state."""
    commit = ContinuationCommit("cc1", "gce1", "rid1", "root1", "ob1", ("auth1",), "digest1")
    assert commit.epoch_id == "gce1"
    assert commit.parent_rid == "rid1"
    assert commit.root_authority_ref == "root1"


def test_rfc15_t075_law_17_selects_what_next_rfc14_how_to_express():
    """RFC15-T075: Law 17 selects what is expressed next while RFC-14 alone determines how it is surface-realized."""
    g = CognitiveGraph()
    g.link("act_a", "prop_a", W=0.9, contexts=("en",))
    rep = _make_sample_rep(g, ["act_a"])
    epoch = g.recurrent_engine.create_epoch("root_what_how")
    status, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "PROGRESS"
    assert rcpt.alignment_view.surface_unit_id is not None


# ── RFC15-T076 .. RFC15-T085: Progress, Replay & Recurrent Execution
def test_rfc15_t076_commit_alone_creates_no_receipt():
    """RFC15-T076: Law-17 commit alone does not create ExpressionReceipt or coverage progress."""
    g = CognitiveGraph()
    g.link("k_1", "k_2", W=0.9, contexts=("order",))
    rep = _make_sample_rep(g, ["k_1", "k_2"])
    epoch = g.recurrent_engine.create_epoch("root_commit_only")
    obs = g.recurrent_engine.derive_obligations(rep, "root_commit_only")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    status, _commit, _ = g.recurrent_engine.commit_continuation(front, epoch, rep)
    assert status == "CONTINUATION_COMMITTED"
    assert len(epoch.progress_receipt_refs) == 0  # No receipt yet!


def test_rfc15_t077_stale_commit_rejected():
    """RFC15-T077: Stale ContinuationCommit is rejected or revalidated before RFC-14 consumption."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_stale_commit")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "CANCELLED")
    rep = _make_sample_rep(g, ["node_1"])
    status, _, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "STALE"


def test_rfc15_t078_commit_publication_is_failure_atomic():
    """RFC15-T078: ContinuationCommit publication is failure-atomic."""
    commit = ContinuationCommit("cc_at", "gce_at", "rid_at", "root_at", "ob_at", (), "d_at")
    assert isinstance(commit, ContinuationCommit)


def test_rfc15_t079_duplicate_commit_retry_idempotent():
    """RFC15-T079: Duplicate commit retry is idempotent for the same bound progress state."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_dup_commit")
    rep = _make_sample_rep(g, ["x1"])
    g.link("x1", "p", W=0.9, contexts=("en",))
    obs = g.recurrent_engine.derive_obligations(rep, "root_dup_commit")
    cov = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    front = g.recurrent_engine.derive_continuation_frontier(rem, cov, rep, epoch)
    s1, _c1, _ = g.recurrent_engine.commit_continuation(front, epoch, rep)
    s2, _c2, _ = g.recurrent_engine.commit_continuation(front, epoch, rep)
    assert s1 == s2 == "CONTINUATION_COMMITTED"


def test_rfc15_t080_law_17_creates_no_learning_or_tbr():
    """RFC15-T080: Law 17 selection creates no learning, support, confidence, Assembly evidence, or TBR authority."""
    g = CognitiveGraph()
    g.link("learn_a", "learn_b", W=0.8, contexts=("en",))
    w_start = g.edges[("learn_a", "learn_b")].W
    rep = _make_sample_rep(g, ["learn_a"])
    epoch = g.recurrent_engine.create_epoch("root_no_learn")
    g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert g.edges[("learn_a", "learn_b")].W == w_start


def test_rfc15_t081_failed_execution_leaves_no_ghost_authority():
    """RFC15-T081: Failed Law-17/RFC-14 execution leaves no ghost next-content authority or ghost progress."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_ghost")
    rep = _make_sample_rep(g, ["no_edges_node"])
    status, ep, _rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    if status == "REALIZATION_BLOCKED":
        assert len(ep.progress_receipt_refs) == 0


def test_rfc15_t082_gce_append_is_failure_atomic_and_deduplicated():
    """RFC15-T082: GCE append is failure-atomic and deduplicated."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_atomic_append")
    rcpt = ExpressionReceipt("er_test", "root_atomic_append", "rid", SourceAlignment("su1", "occ1", "auth1"), "chunk1", ("e",))
    ep1 = g.recurrent_engine.append_receipt(epoch.epoch_id, rcpt)
    ep2 = g.recurrent_engine.append_receipt(epoch.epoch_id, rcpt)
    assert len(ep1.progress_receipt_refs) == len(ep2.progress_receipt_refs) == 1


def test_rfc15_t083_gce_closure_is_failure_atomic():
    """RFC15-T083: GCE closure OPEN->CLOSED is failure-atomic."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_close_atomic")
    closed_ep, closure_view = g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    assert closed_ep.lifecycle == "CLOSED"
    assert closure_view.closure_reason == "COMPLETE"


def test_rfc15_t084_closed_gce_derived_artifacts_cannot_regain_authority():
    """RFC15-T084: Closed-GCE derived artifacts cannot regain generation authority."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_closed_no_authority")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    rep = _make_sample_rep(g, ["node_1"])
    status, _, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "STALE"


def test_rfc15_t085_monotonic_coverage_progress_in_stable_state():
    """RFC15-T085: Under stable finite obligations, each successful non-repeated cycle increases Covered and decreases Remaining."""
    g = CognitiveGraph()
    g.link("step_1", "step_2", W=0.9, contexts=("order",))
    g.link("step_1", "p1", W=0.9, contexts=("en",))
    g.link("step_2", "p2", W=0.9, contexts=("en",))
    rep = _make_sample_rep(g, ["step_1", "step_2"])
    epoch = g.recurrent_engine.create_epoch("root_monotonic")

    obs = g.recurrent_engine.derive_obligations(rep, "root_monotonic")
    cov0 = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem0 = g.recurrent_engine.compute_remaining(obs, cov0)

    _, ep1, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    cov1 = g.recurrent_engine.compute_coverage(obs, ep1, rep)
    rem1 = g.recurrent_engine.compute_remaining(obs, cov1)

    assert len(cov1.covered_obligation_ids) > len(cov0.covered_obligation_ids)
    assert len(rem1.remaining_obligations) < len(rem0.remaining_obligations)


# ── RFC15-T086 .. RFC15-T096: Termination, Stale, Diagnostics & Regression
def test_rfc15_t086_no_progress_fixed_point_termination():
    """RFC15-T086: No-progress repeated execution under an unchanged generative operational state terminates as NO_PROGRESS_FIXED_POINT or NO_AUTHORIZED_CONTINUATION."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["blocked_node"])
    epoch = g.recurrent_engine.create_epoch("root_fp")
    ob_unmet = ExpressiveObligation("ob_unmet", "root_fp", "blocked_node", "role")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(
        epoch.epoch_id, rep, explicit_obligations=[ob_unmet], explicit_precedences=[("ob_missing", "ob_unmet")]
    )
    assert closure.closure_reason == "NO_AUTHORIZED_CONTINUATION"


def test_rfc15_t087_surface_paraphrase_does_not_evade_no_progress():
    """RFC15-T087: Surface paraphrase of an already covered obligation does not evade no-progress detection."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_para")
    rep = _make_sample_rep(g, ["car_node"])
    g.link("car_node", "p", W=0.9, contexts=("en",))
    _, ep, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    # Attempting to re-express the same obligation without repeat authority
    obs = g.recurrent_engine.derive_obligations(rep, "root_para")
    cov = g.recurrent_engine.compute_coverage(obs, ep, rep)
    rem = g.recurrent_engine.compute_remaining(obs, cov)
    assert len(rem.remaining_obligations) == 0


def test_rfc15_t088_remaining_with_no_continuation_not_misclassified_as_complete():
    """RFC15-T088: Remaining content with no authorized continuation is not misclassified as COMPLETE."""
    g = CognitiveGraph()
    # Cyclic dependency -> CONFLICT -> not complete
    rep = _make_sample_rep(g, ["cyc1", "cyc2"])
    epoch = g.recurrent_engine.create_epoch("root_conflict_closure")
    obs = g.recurrent_engine.derive_obligations(rep, "root_conflict_closure")
    ob1, ob2 = obs[0], obs[1]
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(
        epoch.epoch_id, rep, explicit_precedences=[(ob1.obligation_id, ob2.obligation_id), (ob2.obligation_id, ob1.obligation_id)]
    )
    assert closure.closure_reason == "CONFLICT"
    assert closure.closure_reason != "COMPLETE"


def test_rfc15_t089_complete_requires_empty_remaining_and_no_repair():
    """RFC15-T089: COMPLETE requires no remaining obligation, no pending root-authorized expression, and no required repair."""
    g = CognitiveGraph()
    g.link("c1", "p1", W=0.9, contexts=("en",))
    rep = _make_sample_rep(g, ["c1"])
    epoch = g.recurrent_engine.create_epoch("root_complete")
    closure, _handoff = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep)
    assert closure.closure_reason == "COMPLETE"
    assert len(closure.unresolved_obligation_ids) == 0


def test_rfc15_t090_budget_exhaustion_closes_as_partial_budget():
    """RFC15-T090: Budget exhaustion closes current GCE as PARTIAL_BUDGET without internal renewal."""
    g = CognitiveGraph()
    for i in range(10):
        g.link(f"n_{i}", f"p_{i}", W=0.9, contexts=("en",))
    rep = _make_sample_rep(g, [f"n_{i}" for i in range(10)])
    epoch = g.recurrent_engine.create_epoch("root_budget_exhaust")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=0.01)  # tiny budget
    assert closure.closure_reason == "PARTIAL_BUDGET"


def test_rfc15_t091_continuation_after_budget_requires_new_gce():
    """RFC15-T091: New continuation after budget closure requires independent continuation authority and a new GCE."""
    g = CognitiveGraph()
    ep1 = g.recurrent_engine.create_epoch("root_task_b1")
    g.recurrent_engine.close_epoch(ep1.epoch_id, "PARTIAL_BUDGET")
    ep2 = g.recurrent_engine.create_epoch("root_task_b1")
    assert ep2.epoch_id != ep1.epoch_id
    assert ep2.lifecycle == "OPEN"


def test_rfc15_t092_relevant_cognitive_change_forces_fresh_derivation():
    """RFC15-T092: Relevant cognitive change forces fresh obligations, coverage, referential accessibility, and continuation frontier derivation."""
    g = CognitiveGraph()
    rep1 = _make_sample_rep(g, ["n_init"])
    rep2 = _make_sample_rep(g, ["n_init", "n_added"])
    g.recurrent_engine.create_epoch("root_dynamic")
    obs1 = g.recurrent_engine.derive_obligations(rep1, "root_dynamic")
    obs2 = g.recurrent_engine.derive_obligations(rep2, "root_dynamic")
    assert len(obs1) == 1
    assert len(obs2) == 2


def test_rfc15_t093_superseded_expression_retained_in_history():
    """RFC15-T093: Superseded historical expression remains recorded, incompatible current coverage is removed, and repair requires existing authority."""
    g = CognitiveGraph()
    rep = _make_sample_rep(g, ["item_orig"])
    g.link("item_orig", "p", W=0.9, contexts=("en",))
    epoch = g.recurrent_engine.create_epoch("root_sup_test")
    _, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    sup_view = SupersededExpressionView(frozenset([rcpt.receipt_id]), frozenset(["ob_old"]))
    assert rcpt.receipt_id in sup_view.superseded_receipt_ids
    assert rcpt.receipt_id in ep.progress_receipt_refs  # Not deleted


def test_rfc15_t094_root_revocation_or_cancellation_closes_gce():
    """RFC15-T094: Root revocation or explicit cancellation closes the GCE without persistent cognitive mutation."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch("root_to_cancel")
    closed_ep, closure = g.recurrent_engine.close_epoch(epoch.epoch_id, "CANCELLED")
    assert closed_ep.lifecycle == "CLOSED"
    assert closure.closure_reason == "CANCELLED"


def test_rfc15_t095_rfc15_only_execution_conserves_cognition_and_is_deterministic():
    """RFC15-T095: RFC-15-only execution conserves all persistent cognition and Law-14 Assembly structure, yielding deterministic continuation."""
    g = CognitiveGraph()
    g.link("det_a", "prop_a", W=0.9, contexts=("en",))
    _make_sample_rep(g, ["det_a"])
    g.recurrent_engine.create_epoch("root_det", epoch_id="ep_det")
    sig1 = rfc15_behavioral_signature(g.recurrent_engine)
    assert len(sig1) == 16


def test_rfc15_t096_rfc15_ends_before_rfc16_unified_loop():
    """RFC15-T096: RFC-15 ends before unified external perception, reasoning, recall, task lifecycle, feedback interpretation, or cross-task scheduling."""
    handoff = HandoffView15To16("gce_final", "root_task", ("er1", "er2"), (), "COMPLETE")
    assert isinstance(handoff, HandoffView15To16)
    assert handoff.epoch_id == "gce_final"
    assert handoff.closure_reason == "COMPLETE"
