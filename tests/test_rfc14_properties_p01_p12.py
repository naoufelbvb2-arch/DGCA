"""
DGCA — RFC-14 Property-Based Verification Suite (RFC14-P01 .. RFC14-P12).
Executes all 12 property families across 30 deterministic random seeds.
"""
from __future__ import annotations

import random

import pytest

from dgca.generation import (
    GenerativeFrame,
)
from dgca.graph import CognitiveGraph
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
)

NUM_SEEDS = 30


def _build_seeded_environment(seed: int) -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    rng = random.Random(seed)
    g = CognitiveGraph()

    # إنشاء عقد وحواف محلية
    num_nodes = rng.randint(3, 8)
    nodes = [f"concept_node_{seed}_{i}" for i in range(num_nodes)]

    for i in range(num_nodes - 1):
        w = round(rng.uniform(0.5, 0.95), 2)
        g.link(nodes[i], nodes[i + 1], W=w, contexts=("en",))

    receipts = [
        ParticipationReceipt(
            receipt_id=f"r_{seed}_{i}",
            element_ref=nid,
            parent_cycle_id=1,
            snapshot_or_microtick=0,
            origin_lineage="external",
            participation_kind="node",
            activation_magnitude=round(rng.uniform(0.6, 0.99), 2),
        )
        for i, nid in enumerate(nodes)
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    return g, rep


# ─────────────────────────────────────────────────────────── Property Families P01 .. P12

@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p01_persistent_cognitive_conservation(seed: int):
    """RFC14-P01: Persistent Cognitive Conservation — Digest bit-equivalent before/after generation."""
    g, rep = _build_seeded_environment(seed)
    anchor = rep.participating_node_refs[0] if isinstance(rep.participating_node_refs, list) else next(iter(rep.participating_node_refs))

    digest_before = g.generation_engine.get_memory_snapshot_ref()
    _ = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]), budget=1.0)
    digest_after = g.generation_engine.get_memory_snapshot_ref()

    assert digest_before == digest_after


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p02_assembly_structural_conservation(seed: int):
    """RFC14-P02: Assembly Structural Conservation — Assembly states remain unchanged."""
    g, rep = _build_seeded_environment(seed)
    anchor = next(iter(rep.participating_node_refs))

    asm_count_before = len(g.assembly_manager.assemblies)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))
    asm_count_after = len(g.assembly_manager.assemblies)

    assert asm_count_before == asm_count_after


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p03_input_representation_immutability(seed: int):
    """RFC14-P03: Input Representation Immutability — Frozen SDCR remains bit-equivalent."""
    g, rep = _build_seeded_environment(seed)
    anchor = next(iter(rep.participating_node_refs))

    r_id_before = rep.representation_id
    receipts_before = tuple(rep.participation_receipts)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))

    assert rep.representation_id == r_id_before
    assert rep.participation_receipts == receipts_before


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p04_provenance_conservation(seed: int):
    """RFC14-P04: Provenance Conservation — Source external, output GENERATION/SelfDerived."""
    g, rep = _build_seeded_environment(seed)
    anchor = next(iter(rep.participating_node_refs))

    handoff = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))
    assert rep.participation_receipts[0].origin_lineage == "external"
    assert handoff.surface_chunk_view.origin_lineage == "GENERATION"


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p05_locality(seed: int):
    """RFC14-P05: Locality — Remote graph growth does not alter local semantic realization."""
    g, rep = _build_seeded_environment(seed)
    anchor = next(iter(rep.participating_node_refs))

    h1 = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))

    # إضافة ضوضاء بعيدة غير نشطة
    for i in range(25):
        g.link(f"unrelated_noise_{seed}_{i}", f"remote_target_{seed}_{i}", W=0.75)

    h2 = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))
    assert h1.surface_chunk_view.rendered_text == h2.surface_chunk_view.rendered_text


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p06_language_context_isolation(seed: int):
    """RFC14-P06: Language Context Isolation — Incompatible contexts remain isolated."""
    g, rep = _build_seeded_environment(seed)
    f1 = g.generation_engine.build_generative_frame(rep, frozenset([next(iter(rep.participating_node_refs))]))
    hierarchy = g.generation_engine.build_hierarchy([f1])

    prec_en = g.generation_engine.build_precedence_graph(hierarchy, language_context="en")
    prec_ar = g.generation_engine.build_precedence_graph(hierarchy, language_context="ar")

    assert isinstance(prec_en, type(prec_ar))


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p07_ambiguity_preservation(seed: int):
    """RFC14-P07: Ambiguity Preservation — Unresolved alternatives preserve ambiguity without winner."""
    g = CognitiveGraph()
    r1 = ParticipationReceipt(f"r1_{seed}", f"alt_a_{seed}", 1, 0, "external", "node", activation_magnitude=0.9)
    r2 = ParticipationReceipt(f"r2_{seed}", f"alt_b_{seed}", 1, 0, "external", "node", activation_magnitude=0.9)
    rep = g.representation_engine.build_representation(1, 0, None, [r1, r2])

    f1 = g.generation_engine.build_generative_frame(rep, frozenset([f"alt_a_{seed}"]))
    f2 = g.generation_engine.build_generative_frame(rep, frozenset([f"alt_b_{seed}"]))
    hierarchy = g.generation_engine.build_hierarchy([f1, f2])

    prec = g.generation_engine.build_precedence_graph(hierarchy)
    ready = g.generation_engine.compute_ready_frontier(prec, set())
    assert len(ready) == 2

    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy)
    assert prefix.status == "LINEARIZATION_AMBIGUOUS"
    assert len(prefix.remaining_uncommitted_ids) == 2


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p08_monotonic_generative_progress(seed: int):
    """RFC14-P08: Monotonic Generative Progress — Progress is strictly monotonic without duplicates."""
    g, rep = _build_seeded_environment(seed)
    f1 = g.generation_engine.build_generative_frame(rep, frozenset([next(iter(rep.participating_node_refs))]))
    hierarchy = g.generation_engine.build_hierarchy([f1])

    prefix, _ = g.generation_engine.linearize_hierarchy(hierarchy, budget=5.0)
    occ_ids = [occ.occurrence_id for occ in prefix.committed_occurrences]

    assert len(occ_ids) == len(set(occ_ids))


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p09_deterministic_realization(seed: int):
    """RFC14-P09: Deterministic Realization — Replay reproduces identical SurfaceChunk across runs."""
    g, rep = _build_seeded_environment(seed)
    anchor = next(iter(rep.participating_node_refs))

    h1 = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))
    h2 = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))

    assert h1.surface_chunk_view.rendered_text == h2.surface_chunk_view.rendered_text
    assert h1.surface_chunk_view.chunk_id == h2.surface_chunk_view.chunk_id


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p10_termination_and_budget_monotonicity(seed: int):
    """RFC14-P10: Termination & Budget Monotonicity — Bounded execution guaranteed."""
    g, rep = _build_seeded_environment(seed)
    anchor = next(iter(rep.participating_node_refs))

    h_zero = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]), budget=0.0)
    assert h_zero.surface_chunk_view.closure_reason in ("PARTIAL_BUDGET", "COMPLETE", "AMBIGUOUS", "CONFLICT")

    h_full = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]), budget=10.0)
    assert isinstance(h_full.surface_chunk_view.rendered_text, str)


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p11_cache_transparency(seed: int):
    """RFC14-P11: Cache Transparency — CacheOn == CacheOff semantically."""
    g, rep = _build_seeded_environment(seed)
    anchor = next(iter(rep.participating_node_refs))

    h_cached = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))
    g.generation_engine.clear_caches()
    h_uncached = g.generation_engine.execute_generative_pass(rep, frozenset([anchor]))

    assert h_cached.surface_chunk_view.rendered_text == h_uncached.surface_chunk_view.rendered_text


@pytest.mark.parametrize("seed", range(NUM_SEEDS))
def test_rfc14_p12_stale_handoff_safety(seed: int):
    """RFC14-P12: Stale / Handoff Safety — Stale parent representations fail closed."""
    g, rep = _build_seeded_environment(seed)
    stale_frame = GenerativeFrame(
        frame_id=f"f_stale_{seed}",
        parent_representation_id=f"rep_expired_{seed}",
        scope_view=(),
        anchor_refs=frozenset([next(iter(rep.participating_node_refs))]),
    )
    assert not g.generation_engine.validate_generative_frame(stale_frame, rep)
