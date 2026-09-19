"""
DGCA — RFC14-POA01
Precedence Ordering Authority Repair Acceptance & Invariant Test Suite.

Tests POA01-T01 through POA01-T26 enforcing:
- Directed semantic association != surface word order precedence authority.
- Only lawful positive positional lag (edge.lag > 0) creates graph precedence constraints.
- lag <= 0 carries zero precedence authority.
- No-order ambiguity and genuine order conflicts are conserved.
- Primary learned recall surfaces target concepts in SCTT-00.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from dgca.agent import CognitiveAgent
from dgca.generation import (
    GenerationScope,
    GenerativeFrame,
)
from dgca.graph import CognitiveGraph, Edge
from dgca.observation import ExecutionMode
from dgca.persistence import (
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCTT00_CHECKPOINT = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"


def _make_two_frame_hierarchy(graph: CognitiveGraph, u_ref: str, v_ref: str):
    f1 = GenerativeFrame("f1", "rep1", (), frozenset([u_ref]), ())
    f2 = GenerativeFrame("f2", "rep1", (), frozenset([v_ref]), ())
    return graph.generation_engine.build_hierarchy([f1, f2])


# ─────────────────────────────────────────────────────────── POA01-T01 .. POA01-T15
def test_poa01_t01_bidirectional_zero_lag_assoc_zero_reciprocal_precedence():
    """POA01-T01: Bidirectional assoc edges with lag=0 create zero reciprocal precedence."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:A", W=0.55)
    assert g.edge("text:A", "text:B").lag == 0.0
    assert g.edge("text:B", "text:A").lag == 0.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 0


def test_poa01_t02_semantic_edge_direction_alone_not_precedence_authority():
    """POA01-T02: Semantic edge direction alone is not precedence authority."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.99)
    assert g.edge("text:A", "text:B").lag == 0.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 0


def test_poa01_t03_w_asymmetry_alone_not_precedence_authority():
    """POA01-T03: W asymmetry alone is not precedence authority."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.999)
    g.link("text:B", "text:A", W=0.001)

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 0


def test_poa01_t04_n_asymmetry_alone_not_precedence_authority():
    """POA01-T04: n asymmetry alone is not precedence authority."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.8)
    g.edge("text:A", "text:B").n = 1000
    g.link("text:B", "text:A", W=0.8)
    g.edge("text:B", "text:A").n = 1

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 0


def test_poa01_t05_fwd_true_alone_not_precedence_authority():
    """POA01-T05: fwd=True alone is not precedence authority."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.edge("text:A", "text:B").fwd = True
    assert g.edge("text:A", "text:B").lag == 0.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 0


def test_poa01_t06_sim_cat_relations_do_not_create_syntax_precedence():
    """POA01-T06: sim/cat relations do not create syntax precedence."""
    g = CognitiveGraph(enable_prediction=False)
    e_sim = Edge("text:A", "text:B", W=0.9, kind="sim")
    e_cat = Edge("text:B", "text:C", W=0.9, kind="cat")
    g._link(e_sim)
    g._link(e_cat)

    hier = g.generation_engine.build_hierarchy([
        GenerativeFrame("f1", "rep1", (), frozenset(["text:A"]), ()),
        GenerativeFrame("f2", "rep1", (), frozenset(["text:B"]), ()),
        GenerativeFrame("f3", "rep1", (), frozenset(["text:C"]), ()),
    ])
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 0


def test_poa01_t07_positive_lag_creates_forward_precedence():
    """POA01-T07: Positive lag creates forward precedence when context-compatible."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.edge("text:A", "text:B").lag = 1.2

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 1
    u_id, v_id = next(iter(prec.precedence_constraints))
    assert "text:A" in u_id and "text:B" in v_id


def test_poa01_t08_negative_lag_on_uv_does_not_create_uv():
    """POA01-T08: Negative lag on u->v does not create u<v."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:B", "text:A", W=0.85)
    g.edge("text:B", "text:A").lag = -1.2

    hier = _make_two_frame_hierarchy(g, "text:B", "text:A")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 0


def test_poa01_t09_observe_sequence_ab_yields_forward_not_reciprocal_order():
    """POA01-T09: observe_sequence A->B yields forward, not reciprocal, Law16 order."""
    g = CognitiveGraph(enable_prediction=False)
    g.observe_sequence([[("text", "A")], [("text", "B")]])
    assert g.edge("text:A", "text:B").lag > 0.0
    assert g.edge("text:B", "text:A").lag < 0.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec.precedence_constraints) == 1
    u_id, v_id = next(iter(prec.precedence_constraints))
    assert "text:A" in u_id and "text:B" in v_id

    prefix, _ = g.generation_engine.linearize_hierarchy(hier, language_context="en")
    assert prefix.status == "LINEARIZED"
    assert [occ.filler_ref for occ in prefix.committed_occurrences] == ["text:A", "text:B"]


def test_poa01_t10_observe_sequence_abc_preserves_ordering():
    """POA01-T10: observe_sequence A->B->C preserves ordering."""
    g = CognitiveGraph(enable_prediction=False)
    g.observe_sequence([[("text", "A")], [("text", "B")], [("text", "C")]])

    hier = g.generation_engine.build_hierarchy([
        GenerativeFrame("f1", "rep1", (), frozenset(["text:A"]), ()),
        GenerativeFrame("f2", "rep1", (), frozenset(["text:B"]), ()),
        GenerativeFrame("f3", "rep1", (), frozenset(["text:C"]), ()),
    ])
    prefix, _ = g.generation_engine.linearize_hierarchy(hier, language_context="en")
    assert prefix.status == "LINEARIZED"
    assert [occ.filler_ref for occ in prefix.committed_occurrences] == ["text:A", "text:B", "text:C"]


def test_poa01_t11_incompatible_language_context_ordering_ignored():
    """POA01-T11: Incompatible language/context ordering evidence is ignored."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85, contexts=("ar",))
    g.edge("text:A", "text:B").lag = 1.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prec_en = g.generation_engine.build_precedence_graph(hier, language_context="en")
    assert len(prec_en.precedence_constraints) == 0

    prec_ar = g.generation_engine.build_precedence_graph(hier, language_context="ar")
    assert len(prec_ar.precedence_constraints) == 1


def test_poa01_t12_genuine_opposite_order_authorities_produce_order_conflict():
    """POA01-T12: Genuine opposite order authorities still produce ORDER_CONFLICT."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:A", W=0.85)
    g.edge("text:A", "text:B").lag = 1.0
    g.edge("text:B", "text:A").lag = 1.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prefix, _ = g.generation_engine.linearize_hierarchy(hier, language_context="en")
    assert prefix.status == "ORDER_CONFLICT"


def test_poa01_t13_genuine_conflict_not_resolved_by_edge_weight():
    """POA01-T13: Genuine conflict is not resolved by edge weight."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.999)
    g.link("text:B", "text:A", W=0.001)
    g.edge("text:A", "text:B").lag = 1.0
    g.edge("text:B", "text:A").lag = 1.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prefix, _ = g.generation_engine.linearize_hierarchy(hier, language_context="en")
    assert prefix.status == "ORDER_CONFLICT"


def test_poa01_t14_genuine_conflict_not_resolved_by_ids():
    """POA01-T14: Genuine conflict is not resolved by IDs."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:A", "text:B", W=0.85)
    g.link("text:B", "text:A", W=0.85)
    g.edge("text:A", "text:B").lag = 1.0
    g.edge("text:B", "text:A").lag = 1.0

    hier = _make_two_frame_hierarchy(g, "text:A", "text:B")
    prefix, _ = g.generation_engine.linearize_hierarchy(hier, language_context="en", canonical_identity=True)
    assert prefix.status == "ORDER_CONFLICT"


def test_poa01_t15_no_order_multiple_root_case_remains_linearization_ambiguous():
    """POA01-T15: No-order multiple-root case remains LINEARIZATION_AMBIGUOUS."""
    g = CognitiveGraph(enable_prediction=False)
    # Disconnected roots
    hier = _make_two_frame_hierarchy(g, "text:ALT_1", "text:ALT_2")
    prefix, _ = g.generation_engine.linearize_hierarchy(hier, language_context="en")
    assert prefix.status == "LINEARIZATION_AMBIGUOUS"
    assert len(prefix.remaining_uncommitted_ids) == 2


# ─────────────────────────────────────────────────────────── POA01-T16 .. POA01-T26
_POA01_ISOLATED_TEST_CHECKPOINT: Path | None = None


def _get_poa01_test_checkpoint() -> Path:
    """Provides a trained checkpoint for POA01 unit tests.

    If the canonical repository checkpoint exists, it is used.
    If absent, a test-local deterministic checkpoint is generated under
    an isolated temporary directory. The canonical repository artifact
    data/checkpoints/SCTT00-trained.json is NEVER self-healed or created here.
    """
    if SCTT00_CHECKPOINT.is_file():
        return SCTT00_CHECKPOINT
    global _POA01_ISOLATED_TEST_CHECKPOINT
    if _POA01_ISOLATED_TEST_CHECKPOINT is not None and _POA01_ISOLATED_TEST_CHECKPOINT.is_file():
        return _POA01_ISOLATED_TEST_CHECKPOINT
    import tempfile

    from experiments.sctt00 import execute_training, save_checkpoint

    tmp_dir = Path(tempfile.mkdtemp(prefix="dgca_poa01_test_"))
    tmp_ckpt = tmp_dir / "poa01-test-checkpoint.json"
    runtime_root, _ = execute_training()
    save_checkpoint(runtime_root, tmp_ckpt)
    _POA01_ISOLATED_TEST_CHECKPOINT = tmp_ckpt
    return _POA01_ISOLATED_TEST_CHECKPOINT


def _require_sctt00_checkpoint() -> Path:
    """Backward-compatible alias pointing to the isolated test checkpoint provider."""
    return _get_poa01_test_checkpoint()


def test_poa01_t16_sctt_dog_canine_no_longer_false_order_conflict():
    """POA01-T16: RFC13-SR01 final {dog,canine} no longer creates false ORDER_CONFLICT."""
    ckpt = _get_poa01_test_checkpoint()

    agent = CognitiveAgent.from_checkpoint(ckpt)
    g = agent._root._graph
    obs = agent._chat_runtime._bridge.observe_text(
        boundary_namespace="DGCA:R3:CHAT:v1",
        source_occurrence_key="test:t16",
        source_event_key="msg",
        ingress_boundary="R3_CHAT_TEXT",
        raw_text="dog",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )
    settled, outcome = g.completion_engine.run_settling_epoch(obs.representations[0], budget=1.0)
    assert outcome.closure_reason == "FIXED_POINT"
    assert settled.participating_node_refs == frozenset({"text:dog", "text:canine"})

    base = g.generation_engine.build_generative_frame(settled, frozenset({"text:dog"}), canonical_identity=True)
    hier = g.generation_engine.build_hierarchy([base])
    exp_hier, _ = g.generation_engine.expand_hierarchy(hier, settled, GenerationScope("t", "q", "e"), budget=0.4, canonical_identity=True)

    prefix, _ = g.generation_engine.linearize_hierarchy(exp_hier, language_context="en", budget=0.6, canonical_identity=True)
    assert prefix.status == "LINEARIZED"
    assert [occ.filler_ref for occ in prefix.committed_occurrences] == ["text:dog", "text:canine"]


def test_poa01_t17_dog_probe_surfaces_canine_through_frame_local_structure():
    """POA01-T17: dog probe can surface canine through unchanged frame-local structure."""
    ckpt = _get_poa01_test_checkpoint()

    agent = CognitiveAgent.from_checkpoint(ckpt)
    reply = agent.chat("dog")
    assert "canine" in reply.split()
    assert agent.last_turn is not None
    assert not agent.last_turn.used_fallback
    assert "COMPLETE" in agent.last_turn.generation_closure_reasons


def test_poa01_t18_generation_causes_zero_persistent_cognitive_mutation():
    """POA01-T18: Generation causes zero persistent cognitive mutation."""
    ckpt = _get_poa01_test_checkpoint()

    agent = CognitiveAgent.from_checkpoint(ckpt)
    g = agent._root._graph
    d_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(g))
    t_before = g.t

    _ = agent.chat("dog")

    d_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(g))
    t_after = g.t
    assert d_before == d_after
    assert t_before == t_after


def test_poa01_t19_generation_causes_zero_assembly_mutation():
    """POA01-T19: Generation causes zero Assembly mutation."""
    ckpt = _get_poa01_test_checkpoint()

    agent = CognitiveAgent.from_checkpoint(ckpt)
    g = agent._root._graph
    asm_before = set(g.assemblies.keys()) if hasattr(g, "assemblies") else set()

    _ = agent.chat("dog")

    asm_after = set(g.assemblies.keys()) if hasattr(g, "assemblies") else set()
    assert asm_before == asm_after


def test_poa01_t20_rfc15_remains_unused():
    """POA01-T20: RFC15 remains unused."""
    import sys
    assert "dgca.rfc15" not in sys.modules
    # Ensure generation handoff has not invoked any external predictive engine
    agent = CognitiveAgent()
    assert not hasattr(agent._root._graph, "predictive_engine")


def test_poa01_t21_existing_context_isolation_remains_valid():
    """POA01-T21: Existing context isolation remains valid."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:X", "text:Y", W=0.85, contexts=("legal",))
    g.edge("text:X", "text:Y").lag = 1.0

    hier = _make_two_frame_hierarchy(g, "text:X", "text:Y")
    prec_med = g.generation_engine.build_precedence_graph(hier, language_context="medical")
    prec_leg = g.generation_engine.build_precedence_graph(hier, language_context="legal")

    assert len(prec_med.precedence_constraints) == 0
    assert len(prec_leg.precedence_constraints) == 1


def test_poa01_t22_weakest_edge_deletion_defense_valid_with_genuine_fixtures():
    """POA01-T22: Weakest-edge-deletion defense remains valid using genuine order-bearing fixtures."""
    g = CognitiveGraph(enable_prediction=False)
    g.link("text:P", "text:Q", W=0.95)
    g.link("text:Q", "text:P", W=0.05)
    g.edge("text:P", "text:Q").lag = 2.0
    g.edge("text:Q", "text:P").lag = 2.0

    hier = _make_two_frame_hierarchy(g, "text:P", "text:Q")
    prefix, _ = g.generation_engine.linearize_hierarchy(hier)
    assert prefix.status == "ORDER_CONFLICT"
    assert len(prefix.committed_occurrences) == 0


def test_poa01_t23_deterministic_replay_across_runs():
    """POA01-T23: Deterministic fixed state/context/budget."""
    ckpt = _get_poa01_test_checkpoint()

    agent = CognitiveAgent.from_checkpoint(ckpt)
    replies = [agent.chat("dog") for _ in range(5)]
    assert len(set(replies)) == 1
    assert replies[0] == "dog canine"


def test_poa01_t24_all_rfc13_sr01_tests_pass():
    """POA01-T24: All RFC13-SR01 tests pass unchanged."""
    res = pytest.main(["-q", str(REPO_ROOT / "tests" / "test_rfc13_sr01.py")])
    assert res == pytest.ExitCode.OK


def test_poa01_t25_all_r3_min_tests_pass():
    """POA01-T25: All R3-Min tests pass unchanged."""
    res = pytest.main(["-q", str(REPO_ROOT / "tests" / "test_ric01_r3_min.py")])
    assert res == pytest.ExitCode.OK


def test_poa01_t26_sctt00_post_training_checkpoint_recall_regression():
    """POA01-T26: Post-training checkpoint recall regression.

    Verifies all 8 cues surface expected targets from the trained checkpoint.
    Note: This is a post-training checkpoint recall regression, not the full
    end-to-end SCTT training rerun.
    """
    ckpt = _get_poa01_test_checkpoint()

    agent = CognitiveAgent.from_checkpoint(ckpt)
    cues_and_targets = [
        ("dog", "canine"),
        ("cat", "feline"),
        ("robin", "bird"),
        ("rose", "flower"),
        ("apple", "fruit"),
        ("car", "vehicle"),
        ("ice", "solid"),
        ("water", "liquid"),
    ]
    for cue, target in cues_and_targets:
        reply = agent.chat(cue)
        tokens = reply.split()
        assert target in tokens, f"Expected {target} in tokens for cue '{cue}', got {reply!r}"

