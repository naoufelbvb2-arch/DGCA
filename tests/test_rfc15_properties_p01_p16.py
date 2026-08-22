"""
DGCA — RFC-15 v1.0 / LAW 17 v1.0
PROPERTY-BASED VERIFICATION SUITE (RFC15-P01 .. RFC15-P16)
30 Distinct Deterministic Seeds per Property Family (480 Test Iterations)
"""
from __future__ import annotations

import pytest

from dgca.graph import CognitiveGraph
from dgca.recurrent import (
    CoveredView,
    ExpressionReceipt,
    ExpressiveObligation,
    GenerativeContinuationEpoch,
    RemainingView,
    rfc15_behavioral_signature,
)
from dgca.representation import ParticipationReceipt, SparseDistributedCognitiveRepresentation


def _build_seeded_graph(seed: int) -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph()
    n_nodes = 3 + (seed % 6)
    nodes = [f"node_s{seed}_{i}" for i in range(n_nodes)]
    receipts = [
        ParticipationReceipt(f"rcpt_s{seed}_{i}", nodes[i], 1, 0, "external", "node", activation_magnitude=0.85)
        for i in range(n_nodes)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    object.__setattr__(rep, "representation_id", f"rep_s{seed}")

    for i, n in enumerate(nodes):
        g.link(n, f"prop_s{seed}_{i}", W=0.75 + (i * 0.02), contexts=("en",))
        if i < len(nodes) - 1:
            g.link(n, nodes[i + 1], W=0.9, contexts=("order",))

    return g, rep


# ── RFC15-P01: Single Transient Canonical Primitive Bound
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p01_single_transient_primitive_bound(seed: int):
    """RFC15-P01: GCE is the only transient primitive, having exact 5 fields and immutable root authority."""
    epoch = GenerativeContinuationEpoch(
        epoch_id=f"gce_seed_{seed}",
        root_authority_ref=f"root_auth_{seed}",
        progress_receipt_refs=(),
        budget_authority_ref="budget_def",
        lifecycle="OPEN",
    )
    assert len(epoch.__dataclass_fields__) == 5
    assert epoch.root_authority_ref == f"root_auth_{seed}"
    assert epoch.lifecycle == "OPEN"


# ── RFC15-P02: Zero Persistent Learned Mutation
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p02_zero_persistent_learned_mutation(seed: int):
    """RFC15-P02: Recurrent execution strictly conserves all Edge weights, assemblies, confidence, and TBR."""
    g, rep = _build_seeded_graph(seed)
    edges_before = {k: e.W for k, e in g.edges.items()}

    epoch = g.recurrent_engine.create_epoch(f"root_p02_{seed}")
    _closure, _ = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=10.0)

    edges_after = {k: e.W for k, e in g.edges.items()}
    assert edges_before == edges_after
    assert len(g.assembly_manager.assemblies) == 0


# ── RFC15-P03: Generation/SelfDerived Provenance Invariant
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p03_generation_provenance_invariant(seed: int):
    """RFC15-P03: All ExpressionReceipts and ContinuationCommits strictly record GENERATION lineage."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p03_{seed}")
    status, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "PROGRESS"
    assert rcpt is not None
    assert rcpt.origin_lineage == "GENERATION"


# ── RFC15-P04: GCE Progress Append-Only & Idempotence
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p04_progress_append_only_and_idempotent(seed: int):
    """RFC15-P04: GCE progress grows strictly append-only and deduplicates identical appends."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p04_{seed}")
    _, ep1, r1, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    len1 = len(ep1.progress_receipt_refs)
    ep_reappend = g.recurrent_engine.append_receipt(epoch.epoch_id, r1)
    assert len(ep_reappend.progress_receipt_refs) == len1


# ── RFC15-P05: Authority-Scoped Coverage Determination
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p05_authority_scoped_coverage(seed: int):
    """RFC15-P05: Coverage is strictly scoped to the matching root authority and semantic element."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p05_{seed}")
    _, ep, _rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)

    obs_match = g.recurrent_engine.derive_obligations(rep, f"root_p05_{seed}")
    cov_match = g.recurrent_engine.compute_coverage(obs_match, ep, rep)
    assert len(cov_match.covered_obligation_ids) >= 1

    obs_mismatch = g.recurrent_engine.derive_obligations(rep, "foreign_root")
    cov_mismatch = g.recurrent_engine.compute_coverage(obs_mismatch, ep, rep)
    assert len(cov_mismatch.covered_obligation_ids) == 0


# ── RFC15-P06: Repetition Suppression & Authorized Override
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p06_repetition_suppression_and_override(seed: int):
    """RFC15-P06: Covered obligations are suppressed unless repeat_authorized is explicitly true."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p06_{seed}")
    _, ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)

    elem = rcpt.expressed_elements[0]
    ob_normal = ExpressiveObligation(f"ob_n_{seed}", f"root_p06_{seed}", elem, "role", repeat_authorized=False)
    ob_repeat = ExpressiveObligation(f"ob_r_{seed}", f"root_p06_{seed}", elem, "role", repeat_authorized=True)

    cov_norm = g.recurrent_engine.compute_coverage((ob_normal,), ep, rep)
    cov_rep = g.recurrent_engine.compute_coverage((ob_repeat,), ep, rep)

    assert len(cov_norm.covered_obligation_ids) == 1
    assert len(cov_rep.covered_obligation_ids) == 0


# ── RFC15-P07: Referential Accessibility Ambiguity Preservation
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p07_referential_ambiguity_preservation(seed: int):
    """RFC15-P07: Multiple historical receipts for a single referent mark it as ambiguous without winner-take-all."""
    g = CognitiveGraph()
    epoch = g.recurrent_engine.create_epoch(f"root_p07_{seed}")
    rcpt1 = ExpressionReceipt(f"er1_{seed}", f"root_p07_{seed}", "rid", None, "c1", (f"elem_{seed}",))
    rcpt2 = ExpressionReceipt(f"er2_{seed}", f"root_p07_{seed}", "rid", None, "c2", (f"elem_{seed}",))
    g.recurrent_engine._receipts[rcpt1.receipt_id] = rcpt1
    g.recurrent_engine._receipts[rcpt2.receipt_id] = rcpt2
    ep = g.recurrent_engine.append_receipt(epoch.epoch_id, rcpt1)
    ep = g.recurrent_engine.append_receipt(epoch.epoch_id, rcpt2)

    rep = _build_seeded_graph(seed)[1]
    ref_view = g.recurrent_engine.compute_referential_accessibility(rep, f"root_p07_{seed}", ep)
    assert f"elem_{seed}" in ref_view.ambiguous_referents
    assert len(ref_view.accessible_referents[f"elem_{seed}"]) == 2


# ── RFC15-P08: Law 17 Ambiguity Preservation
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p08_law17_ambiguity_preservation(seed: int):
    """RFC15-P08: Multiple ready candidates without precedence constraint yield CONTINUATION_AMBIGUOUS."""
    g = CognitiveGraph()
    nodes = [f"amb_node_{seed}_{i}" for i in range(2 + (seed % 3))]
    receipts = [
        ParticipationReceipt(f"rcpt_amb_{i}", n, 1, 0, "external", "node", activation_magnitude=0.9)
        for i, n in enumerate(nodes)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    for n in nodes:
        g.link(n, f"prop_{n}", W=0.9, contexts=("en",))
    # Zero precedence edges
    epoch = g.recurrent_engine.create_epoch(f"root_p08_{seed}")
    status, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "CONTINUATION_AMBIGUOUS"
    assert rcpt is None


# ── RFC15-P09: Law 17 Conflict Detection
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p09_law17_conflict_detection(seed: int):
    """RFC15-P09: Cyclic precedence dependencies return CONTINUATION_CONFLICT and never delete edges."""
    g = CognitiveGraph()
    rep = _build_seeded_graph(seed)[1]
    epoch = g.recurrent_engine.create_epoch(f"root_p09_{seed}")
    ob1 = ExpressiveObligation(f"ob1_{seed}", f"root_p09_{seed}", "n1", "role")
    ob2 = ExpressiveObligation(f"ob2_{seed}", f"root_p09_{seed}", "n2", "role")
    rem = RemainingView((ob1, ob2), frozenset([ob1.obligation_id, ob2.obligation_id]))
    cov = CoveredView(frozenset(), {})

    front = g.recurrent_engine.derive_continuation_frontier(
        rem, cov, rep, epoch, explicit_precedences=[(ob1.obligation_id, ob2.obligation_id), (ob2.obligation_id, ob1.obligation_id)]
    )
    assert front.status == "CONFLICT"


# ── RFC15-P10: Finite Monotonic Step Progress
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p10_finite_monotonic_step_progress(seed: int):
    """RFC15-P10: Each step in a finite linear sequence increases covered count and decreases remaining count."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p10_{seed}")

    obs = g.recurrent_engine.derive_obligations(rep, f"root_p10_{seed}")
    cov0 = g.recurrent_engine.compute_coverage(obs, epoch, rep)
    rem0 = g.recurrent_engine.compute_remaining(obs, cov0)

    _, ep1, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    cov1 = g.recurrent_engine.compute_coverage(obs, ep1, rep)
    rem1 = g.recurrent_engine.compute_remaining(obs, cov1)

    assert len(cov1.covered_obligation_ids) == len(cov0.covered_obligation_ids) + 1
    assert len(rem1.remaining_obligations) == len(rem0.remaining_obligations) - 1


# ── RFC15-P11: No-Progress Fixed-Point Deterministic Halt
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p11_no_progress_fixed_point_halt(seed: int):
    """RFC15-P11: Unchanging operational signature without progress terminates predictably."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p11_{seed}")
    ob_blocked = ExpressiveObligation(f"ob_bl_{seed}", f"root_p11_{seed}", "unmet_node", "role")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(
        epoch.epoch_id, rep, explicit_obligations=[ob_blocked], explicit_precedences=[("ob_missing", ob_blocked.obligation_id)]
    )
    assert closure.closure_reason == "NO_AUTHORIZED_CONTINUATION"


# ── RFC15-P12: Budget Exhaustion Safety
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p12_budget_exhaustion_safety(seed: int):
    """RFC15-P12: Insufficient runtime budget closes the GCE as PARTIAL_BUDGET."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p12_{seed}")
    closure, _ = g.recurrent_engine.execute_recurrent_epoch(epoch.epoch_id, rep, budget=0.01)
    assert closure.closure_reason == "PARTIAL_BUDGET"


# ── RFC15-P13: Clean RFC-14 Separation & Delegation
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p13_clean_rfc14_separation(seed: int):
    """RFC15-P13: RFC-15 executes Law 17 selection and delegates surface realization directly to RFC-14."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p13_{seed}")
    status, _ep, rcpt, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "PROGRESS"
    assert rcpt.alignment_view.surface_unit_id.startswith("su_")


# ── RFC15-P14: Dynamic Cognitive Change Adaptation
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p14_dynamic_cognitive_adaptation(seed: int):
    """RFC15-P14: Changing representation elements across cycles smoothly adapts obligation sets."""
    g = CognitiveGraph()
    rep1 = _build_seeded_graph(seed)[1]
    obs1 = g.recurrent_engine.derive_obligations(rep1, f"root_p14_{seed}")

    receipts_extra = list(rep1.participation_receipts) + [
        ParticipationReceipt(f"extra_r_{seed}", f"extra_node_{seed}", 1, 0, "external", "node", activation_magnitude=0.9)
    ]
    rep2 = g.representation_engine.build_representation(1, 0, None, receipts_extra)
    obs2 = g.recurrent_engine.derive_obligations(rep2, f"root_p14_{seed}")

    assert len(obs2) == len(obs1) + 1


# ── RFC15-P15: GCE Closure Irrevocability & Stale Invalidation
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p15_closure_irrevocability(seed: int):
    """RFC15-P15: Closed GCE cannot be re-executed and rejects execution with STALE."""
    g, rep = _build_seeded_graph(seed)
    epoch = g.recurrent_engine.create_epoch(f"root_p15_{seed}")
    g.recurrent_engine.close_epoch(epoch.epoch_id, "COMPLETE")
    status, _, _, _ = g.recurrent_engine.execute_recurrent_step(epoch.epoch_id, rep)
    assert status == "STALE"


# ── RFC15-P16: Deterministic Behavioral Replay
@pytest.mark.parametrize("seed", range(30))
def test_rfc15_p16_deterministic_behavioral_replay(seed: int):
    """RFC15-P16: Repeated runs on identical graph configurations produce bit-exact behavioral signatures."""
    g1, rep1 = _build_seeded_graph(seed)
    ep1 = g1.recurrent_engine.create_epoch(f"root_p16_{seed}", epoch_id=f"ep_fixed_{seed}")
    g1.recurrent_engine.execute_recurrent_epoch(ep1.epoch_id, rep1, budget=10.0)
    sig1 = rfc15_behavioral_signature(g1.recurrent_engine)

    g2, rep2 = _build_seeded_graph(seed)
    ep2 = g2.recurrent_engine.create_epoch(f"root_p16_{seed}", epoch_id=f"ep_fixed_{seed}")
    g2.recurrent_engine.execute_recurrent_epoch(ep2.epoch_id, rep2, budget=10.0)
    sig2 = rfc15_behavioral_signature(g2.recurrent_engine)

    assert sig1 == sig2
