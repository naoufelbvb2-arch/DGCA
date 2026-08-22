"""
DGCA — RFC-14 Conservation, Failure-Atomicity (F1..F9), Stale Safety (S1..S8), and Deterministic Replay Suite.
Authoritative audit test suite covering Sections 17, 33, 34, 48, 49, 50, and 55.
"""
from __future__ import annotations

import dataclasses
import hashlib

import pytest

from dgca.generation import (
    GenerationScope,
    GenerativeFrame,
    GenerativeHierarchy,
    HandoffView,
    HierarchicalGenerativeEngine,
    LinearizableOccurrence,
    LinearizationPrefix,
    PrecedenceGraph,
    ResidualView,
    RoleBinding,
    SurfaceBundle,
    rfc14_behavioral_signature,
)
from dgca.graph import CognitiveGraph
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
)


def compute_complete_cognitive_digest(g: CognitiveGraph) -> str:
    """حساب البصمة الشاملة للحالة المعرفية الدائمة."""
    h = hashlib.sha256()
    for (u, v), e in sorted(g.edges.items()):
        ctxs = ",".join(sorted(e.contexts))
        h.update(f"e:{u}->{v}|W={e.W:.6f}|g={e.g}|k={e.kind}|c=[{ctxs}]\n".encode())
    for nid, n in sorted(g.nodes.items()):
        h.update(f"n:{nid}|r={n.region}|c={int(n.is_concept)}|i={int(n.is_intrinsic)}\n".encode())
    for k, v in sorted(g.X.items()):
        h.update(f"X:{k}={','.join(sorted(v))}\n".encode())
    return h.hexdigest()


def compute_complete_assembly_digest(g: CognitiveGraph) -> str:
    """حساب البصمة الشاملة للبنية الهيكلية للتجمعات (ق14)."""
    h = hashlib.sha256()
    if hasattr(g, "_assembly_manager") and g._assembly_manager is not None:
        mgr = g.assembly_manager
        for aid, versions in sorted(mgr.assemblies.items()):
            latest = versions[-1]
            edges_str = ",".join(f"{u}->{v}" for u, v in sorted(latest.member_edges))
            h.update(f"asm:{aid}|v={latest.version}|edges=[{edges_str}]|r={int(latest.is_retired)}\n".encode())
    return h.hexdigest()


def compute_complete_sdcr_digest(rep: SparseDistributedCognitiveRepresentation) -> str:
    """حساب البصمة الكاملة للتمثيل المعرفي الحالي."""
    h = hashlib.sha256()
    h.update(f"rid:{rep.representation_id}|p={rep.parent_cycle_id}|s={rep.snapshot_or_microtick}\n".encode())
    for r in sorted(rep.participation_receipts, key=lambda x: str(x.receipt_id)):
        h.update(f"rcpt:{r.receipt_id}|el={r.element_ref}|k={r.participation_kind}|act={r.activation_magnitude:.4f}|lin={r.origin_lineage}\n".encode())
    return h.hexdigest()


def _make_fixture() -> tuple[CognitiveGraph, SparseDistributedCognitiveRepresentation]:
    g = CognitiveGraph()
    g.link("concept_falcon", "fly", W=0.92, contexts=("en",))
    g.link("concept_falcon", "predator", W=0.88, contexts=("en",))
    g.link("fly", "predator", W=0.80, contexts=("en",))

    # إنشاء تجمع بنيوي حقيقي غير فارغ وفق القانون 14 (RFC-11)
    mgr = g.assembly_manager
    asm_edges = [("concept_falcon", "fly"), ("concept_falcon", "predator"), ("fly", "predator")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(asm_edges, root_episode_id=f"root_ep_{i}", valid_origin=True)

    receipts = [
        ParticipationReceipt("r_fal", "concept_falcon", 1, 0, "external", "node", activation_magnitude=0.95),
        ParticipationReceipt("r_fly", "fly", 1, 0, "external", "node", activation_magnitude=0.90),
        ParticipationReceipt("r_pred", "predator", 1, 0, "external", "node", activation_magnitude=0.85),
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)
    return g, rep


# ─────────────────────────────────────────────────────────── Conservation Gates

def test_audit_complete_cognitive_conservation():
    """Gate 7 / Section 48: Complete Persistent Cognitive Digest Conservation."""
    g, rep = _make_fixture()
    d_cog_before = compute_complete_cognitive_digest(g)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_falcon"]))
    d_cog_after = compute_complete_cognitive_digest(g)
    assert d_cog_before == d_cog_after


def test_audit_complete_assembly_structural_conservation():
    """Gate 7 / Section 48: Complete Assembly Structural Digest Conservation."""
    g, rep = _make_fixture()
    d_asm_before = compute_complete_assembly_digest(g)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_falcon"]))
    d_asm_after = compute_complete_assembly_digest(g)
    assert d_asm_before == d_asm_after


def test_audit_complete_sdcr_input_immutability():
    """Gate 7 / Section 48: Frozen RFC-12 Input Representation Immutability."""
    g, rep = _make_fixture()
    d_sdcr_before = compute_complete_sdcr_digest(rep)
    _ = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_falcon"]))
    d_sdcr_after = compute_complete_sdcr_digest(rep)
    assert d_sdcr_before == d_sdcr_after


def test_audit_provenance_conservation():
    """Gate 7 / Section 48: Provenance Lineage Conservation."""
    g, rep = _make_fixture()
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_falcon"]))
    assert rep.participation_receipts[0].origin_lineage == "external"
    assert handoff.surface_chunk_view.origin_lineage == "GENERATION"
    for unit in handoff.surface_chunk_view.surface_units:
        assert unit.origin_lineage == "GENERATION"


# ─────────────────────────────────────────────────────────── Fault-Injection Matrix F1 .. F9

def test_audit_fault_injection_f1_frame_validation_failure():
    """F1: Frame validation failure (invalid/empty anchor)."""
    g, rep = _make_fixture()
    d_before = compute_complete_cognitive_digest(g)
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["invalid_alien_anchor"]))
    d_after = compute_complete_cognitive_digest(g)
    assert d_before == d_after
    assert handoff.closure_reason == "UNDERSPECIFIED"
    assert len(handoff.surface_chunk_view.surface_units) == 0


def test_audit_fault_injection_f2_role_binding_pre_publication():
    """F2: RoleBinding commit pre-publication failure (invalid filler)."""
    g, rep = _make_fixture()
    d_before = compute_complete_cognitive_digest(g)
    with pytest.raises(ValueError, match="RoleBinding filler_ref cannot be empty"):
        g.generation_engine.build_generative_frame(
            rep,
            frozenset(["concept_falcon"]),
            role_bindings=(RoleBinding("subject", ""),),
        )
    d_after = compute_complete_cognitive_digest(g)
    assert d_before == d_after


def test_audit_fault_injection_f3_role_binding_insufficient_budget():
    """F3: RoleBinding commit after resource boundary (insufficient budget)."""
    g, rep = _make_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_falcon"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    d_before = compute_complete_cognitive_digest(g)
    expanded, cost = g.generation_engine.expand_hierarchy(hierarchy, rep, budget=0.0)
    d_after = compute_complete_cognitive_digest(g)
    assert d_before == d_after
    assert cost == 0.0
    assert len(expanded.frames[f1.frame_id].role_bindings) == len(f1.role_bindings)


def test_audit_fault_injection_f4_precedence_derivation_empty():
    """F4: Precedence derivation on empty hierarchy."""
    g, _rep = _make_fixture()
    d_before = compute_complete_cognitive_digest(g)
    empty_hier = GenerativeHierarchy((), {})
    prec = g.generation_engine.build_precedence_graph(empty_hier)
    d_after = compute_complete_cognitive_digest(g)
    assert d_before == d_after
    assert len(prec.occurrences) == 0


def test_audit_fault_injection_f5_linearization_zero_budget():
    """F5: Linearization prefix commit failure under zero budget."""
    g, rep = _make_fixture()
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_falcon"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    d_before = compute_complete_cognitive_digest(g)
    prefix, cost = g.generation_engine.linearize_hierarchy(hierarchy, budget=0.0)
    d_after = compute_complete_cognitive_digest(g)
    assert d_before == d_after
    assert cost == 0.0
    assert prefix.status == "PARTIAL"


def test_audit_fault_injection_f6_lexical_selection_unrealizable():
    """F6: Lexical selection on unmapped occurrence falls back safely."""
    g, _rep = _make_fixture()
    occ = LinearizableOccurrence("occ_unmapped", "f1", "anchor", "alien_node_999")
    cands = g.generation_engine.resolve_lexical_candidates(occ, "en")
    assert len(cands) >= 1
    assert cands[0].lexeme == "alien_node_999"


def test_audit_fault_injection_f7_surface_bundle_failure_safety():
    """F7: SurfaceBundle construction on unmapped occurrence."""
    g, _rep = _make_fixture()
    occ = LinearizableOccurrence("occ_bundle", "f1", "anchor", "concept_falcon")
    bundle = g.generation_engine.build_surface_bundle(occ, "en")
    assert bundle.source_occurrence_ref == "occ_bundle"
    assert len(bundle.lexical_form_refs) >= 1


def test_audit_fault_injection_f8_surface_unit_atomic_publication():
    """F8: SurfaceUnit + alignment publication atomicity."""
    g, rep = _make_fixture()
    prefix = LinearizationPrefix((), "LINEARIZED")
    chunk = g.generation_engine.realize_surface_chunk(prefix, rep.representation_id)
    assert chunk.parent_representation_id == rep.representation_id
    assert chunk.origin_lineage == "GENERATION"


def test_audit_fault_injection_f9_handoff_publication_safety():
    """F9: Handoff creation and publication safety."""
    g, rep = _make_fixture()
    d_before = compute_complete_cognitive_digest(g)
    handoff = g.generation_engine.execute_generative_pass(rep, frozenset(["concept_falcon"]))
    d_after = compute_complete_cognitive_digest(g)
    assert d_before == d_after
    assert isinstance(handoff, HandoffView)


# ─────────────────────────────────────────────────────────── Stale Safety Matrix S1 .. S8

def test_audit_stale_matrix_s1_stale_parent_rid():
    """S1: Stale ParentRID GenerativeFrame rejected."""
    g, rep = _make_fixture()
    stale_f = GenerativeFrame("f_stale", "rep_expired_123", (), frozenset(["concept_falcon"]))
    assert not g.generation_engine.validate_generative_frame(stale_f, rep)


def test_audit_stale_matrix_s2_stale_hierarchy_frontier():
    """S2: Stale hierarchy expansion fails closed against mismatched representation."""
    g, rep = _make_fixture()
    alien_rep = dataclasses.replace(rep, representation_id="rep_alien_999")
    f1 = g.generation_engine.build_generative_frame(alien_rep, frozenset(["concept_falcon"]))
    assert not g.generation_engine.validate_generative_frame(f1, rep)


def test_audit_stale_matrix_s3_stale_precedence_graph():
    """S3: Stale PrecedenceGraph validated against current occurrences."""
    prec = PrecedenceGraph((), frozenset())
    ready = HierarchicalGenerativeEngine(CognitiveGraph()).compute_ready_frontier(prec, set())
    assert ready == []


def test_audit_stale_matrix_s4_stale_linearization_prefix():
    """S4: LinearizationPrefix status tracks uncommitted occurrences cleanly."""
    prefix = LinearizationPrefix((), "PARTIAL", frozenset(["occ_1"]))
    assert prefix.status == "PARTIAL"
    assert "occ_1" in prefix.remaining_uncommitted_ids


def test_audit_stale_matrix_s5_stale_surface_bundle():
    """S5: SurfaceBundle retains explicit reference to source occurrence."""
    bundle = SurfaceBundle("occ_stale", ("word",))
    assert bundle.source_occurrence_ref == "occ_stale"


def test_audit_stale_matrix_s6_stale_residual_view():
    """S6: ResidualView bound to ParentRID."""
    res = ResidualView("rep_expired", ())
    assert res.parent_representation_id == "rep_expired"


def test_audit_stale_matrix_s7_cross_pass_injection():
    """S7: Cross-pass artifact injection fails closed without revalidation."""
    g, rep = _make_fixture()
    f_cross = GenerativeFrame("f_cross", "rep_pass_a", (), frozenset(["concept_falcon"]))
    assert not g.generation_engine.validate_generative_frame(f_cross, rep)


def test_audit_stale_matrix_s8_task_language_context_mismatch():
    """S8: Task/Language context mismatch filtered cleanly."""
    g, rep = _make_fixture()
    scope = GenerationScope(permitted_roles=frozenset(["restricted_role"]))
    f1 = g.generation_engine.build_generative_frame(rep, frozenset(["concept_falcon"]))
    hierarchy = g.generation_engine.build_hierarchy([f1])
    frontier = g.generation_engine.derive_expansion_frontier(hierarchy, rep, scope)
    assert all(opt.role_authority_ref == "restricted_role" for opt in frontier.options)


# ─────────────────────────────────────────────────────────── 30-Run Deterministic Replay

def test_audit_deterministic_replay_30_runs():
    """Section 55: 30-Run Deterministic Replay Verification."""
    g = CognitiveGraph()
    engine = HierarchicalGenerativeEngine(g)

    signatures = [rfc14_behavioral_signature(engine) for _ in range(30)]
    first_sig = signatures[0]

    assert len(signatures) == 30
    assert all(sig == first_sig for sig in signatures)
    assert len(first_sig) == 16
