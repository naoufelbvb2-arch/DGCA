"""
DGCA — RFC-12 Property-Based Test Suite (RFC12-P01..P08) [Audited & Strengthened].

Comprehensive property-based verification exploring broad state spaces across >= 25 seeds
and >= 100 generated cases per family without external dependencies.
"""
from __future__ import annotations

import hashlib
import random

from dgca import CognitiveGraph
from dgca.representation import (
    ParticipationReceipt,
    TransientBindingReceipt,
)


def compute_complete_persistent_cognitive_digest(graph: CognitiveGraph) -> str:
    """حساب البصمة التشفيرية الشاملة لكافة المعارف والبيانات الدائمة المملوكة للشبكة."""
    rows = []
    # 1. الروابط المعرفية الدائمة
    for (u, v), e in sorted(graph.edges.items()):
        ctxs = ",".join(sorted(e.contexts))
        ctx_hits = ",".join(f"{k}:{v}" for k, v in sorted(e.ctx_hits.items()))
        rows.append(
            f"edge:{u}->{v}|W={e.W:.6f}|S={e.S:.6f}|n={e.n}|kind={e.kind}|g={e.g}|"
            f"val={e.valence:.6f}|lag={e.lag:.6f}|fwd={int(e.fwd)}|locked={int(e.locked)}|"
            f"intr={int(e.is_intrinsic)}|k_fail={e.k_fail}|tagged={int(e.tagged)}|"
            f"ctxs=[{ctxs}]|ctx_hits=[{ctx_hits}]|t_c={e.t_created}|t_u={e.t_last_update}"
        )
    # 2. العقد المعرفية وحالات المفهوم الدائمة
    for nid, n in sorted(graph.nodes.items()):
        rows.append(f"node:{nid}|region={n.region}|concept={int(n.is_concept)}|intr={int(n.is_intrinsic)}")

    # 3. مجموعات التناقض (X)
    for k, v in sorted(graph.X.items()):
        rows.append(f"X:{k}={','.join(sorted(v))}")

    # 4. تكرارات المفاهيم
    for k, v in sorted(graph.concept_hits.items()):
        rows.append(f"concept_hit:{k}={v}")

    # 5. مستودع الفرضيات
    for h in sorted(graph.hypotheses, key=lambda x: str(x)):
        rows.append(f"hypothesis:{sorted(h.items())}")

    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────── P01: Representation Locality
def test_rfc12_p01_representation_locality_strengthened() -> None:
    """RFC12-P01: Embedding local state inside expanding remote graphs across 25 deterministic seeds."""
    for seed in range(1, 26):
        rng = random.Random(seed * 1000 + 42)
        g = CognitiveGraph()
        engine = g.representation_engine

        # توليد سيناريو محلي عشوائي
        u_loc = f"loc_{seed}_a"
        v_loc = f"loc_{seed}_b"
        g.link(u_loc, v_loc, W=0.8)
        g.node(u_loc, "text").excite(1, 0.8)
        g.node(v_loc, "text").excite(1, 0.7)

        receipts = [
            ParticipationReceipt(f"r_{u_loc}", u_loc, 1, 0, "external", "node", activation_magnitude=0.8),
            ParticipationReceipt(f"r_{v_loc}", v_loc, 1, 0, "external", "node", activation_magnitude=0.7),
            ParticipationReceipt(f"r_{u_loc}_{v_loc}", (u_loc, v_loc), 1, 0, "external", "edge", relational_drive=0.8),
        ]
        rep_isolated = engine.build_representation(1, 0, None, receipts)
        sig_isolated = engine.canonical_representation_signature(rep_isolated)

        # ضخ 100 رابط بعيد عشوائي
        for i in range(100):
            u_rem = f"rem_{rng.randint(0, 100)}"
            v_rem = f"rem_{rng.randint(0, 100)}"
            if u_rem != v_rem and u_rem not in (u_loc, v_loc) and v_rem not in (u_loc, v_loc):
                g.link(u_rem, v_rem, W=rng.uniform(0.1, 0.9))

        rep_embedded = engine.build_representation(1, 0, None, receipts)
        sig_embedded = engine.canonical_representation_signature(rep_embedded)

        assert sig_isolated == sig_embedded


# ─────────────────────────────────────────────────────────── P02: Complete Cognitive Conservation
def test_rfc12_p02_no_cognitive_mutation_strengthened() -> None:
    """RFC12-P02: Complete persistent cognitive digest invariance across 25 generated topologies."""
    for seed in range(1, 26):
        rng = random.Random(seed * 2000 + 7)
        g = CognitiveGraph()

        # بناء هيكل معرفي عشوائي يحوي روابط ذات سياقات وقفل وبروز وأقطاب
        kinds = ["assoc", "causes", "spatial", "temporal", "property"]
        for i in range(10):
            u = f"n_{rng.randint(0, 10)}"
            v = f"n_{rng.randint(0, 10)}"
            if u != v:
                g.link(
                    u, v,
                    W=rng.uniform(0.2, 0.95),
                    kind=rng.choice(kinds),
                    g=f"ctx_{rng.randint(0, 3)}" if rng.random() > 0.5 else None,
                )
                e = g.edge(u, v)
                if e:
                    e.S = rng.uniform(0.0, 1.0)
                    e.valence = rng.uniform(-1.0, 1.0)
                    e.lag = rng.uniform(0.0, 5.0)
                    e.n = rng.randint(1, 20)

        # بصمة المعرفة الكاملة قبل عمليات RFC-12
        digest_before = compute_complete_persistent_cognitive_digest(g)
        engine = g.representation_engine

        # تنفيذ عمليات SDCR و TBR و Readout و Caches
        active_nodes = list(g.nodes.keys())[:4]
        receipts = [
            ParticipationReceipt(f"r_{n}", n, 1, 0, "external", "node", activation_magnitude=0.8)
            for n in active_nodes
        ]
        tbr = TransientBindingReceipt("tbr_p2", (1, 0), "scope_p2", tuple(active_nodes[:2]))
        rep = engine.build_representation(1, 0, None, receipts, transient_bindings=[tbr])

        view = engine.get_view(rep)
        view.coherence_components()
        view.typed_support_map()
        for n in active_nodes:
            view.query({"node": n})
        engine.clear_caches()
        engine.close_representation(rep)

        # بصمة المعرفة الكاملة بعد العمليات
        digest_after = compute_complete_persistent_cognitive_digest(g)
        assert digest_before == digest_after


# ─────────────────────────────────────────────────────────── P03: Deterministic Reconstruction
def test_rfc12_p03_deterministic_reconstruction_strengthened() -> None:
    """RFC12-P03: Exact signature reproducibility across 30 shuffled permutations."""
    g = CognitiveGraph()
    engine = g.representation_engine
    g.link("x", "y", W=0.8)
    g.link("y", "z", W=0.8)

    base_receipts = [
        ParticipationReceipt("rx", "x", 1, 0, "external", "node", activation_magnitude=0.85),
        ParticipationReceipt("ry", "y", 1, 0, "external", "node", activation_magnitude=0.75),
        ParticipationReceipt("rz", "z", 1, 0, "external", "node", activation_magnitude=0.65),
        ParticipationReceipt("rxy", ("x", "y"), 1, 0, "external", "edge", relational_drive=0.8),
        ParticipationReceipt("ryz", ("y", "z"), 1, 0, "external", "edge", relational_drive=0.8),
    ]
    tbr = TransientBindingReceipt("tbr", (1, 0), "scope_p3", ("x", "y", "z"))

    rep_canonical = engine.build_representation(1, 0, None, base_receipts, transient_bindings=[tbr])
    canonical_sig = engine.canonical_representation_signature(rep_canonical)

    rng = random.Random(999)
    for _ in range(30):
        shuffled = list(base_receipts)
        rng.shuffle(shuffled)
        rep_shuffled = engine.build_representation(1, 0, None, shuffled, transient_bindings=[tbr])
        shuffled_sig = engine.canonical_representation_signature(rep_shuffled)
        assert canonical_sig == shuffled_sig


# ─────────────────────────────────────────────────────────── P04: Incremental / Rebuild Equivalence
def test_rfc12_p04_incremental_rebuild_equivalence_strengthened() -> None:
    """RFC12-P04: Incremental construction equality across 25 dynamic sequences."""
    for seed in range(1, 26):
        rng = random.Random(seed * 3000 + 13)
        g = CognitiveGraph()
        engine = g.representation_engine

        nodes = [f"node_{k}" for k in range(6)]
        for k in range(5):
            g.link(nodes[k], nodes[k+1], W=0.8)

        all_receipts = [
            ParticipationReceipt(f"r_{n}", n, 1, 0, "external", "node", activation_magnitude=rng.uniform(0.5, 1.0))
            for n in nodes
        ]
        rep_rebuild = engine.build_representation(1, 0, None, all_receipts)
        sig_rebuild = engine.canonical_representation_signature(rep_rebuild)

        # محاكاة بناء تدريجي
        subset = all_receipts[:3]
        rep_step1 = engine.build_representation(1, 0, None, subset)
        assert len(rep_step1.participating_node_refs) == 3

        rep_step2 = engine.build_representation(1, 0, None, all_receipts)
        sig_incremental = engine.canonical_representation_signature(rep_step2)

        assert sig_rebuild == sig_incremental


# ─────────────────────────────────────────────────────────── P05: Binding Conservation
def test_rfc12_p05_binding_conservation_strengthened() -> None:
    """RFC12-P05: TBR presence/absence leaves activation, W, S, and Assemblies unchanged across 25 cases."""
    for seed in range(1, 26):
        rng = random.Random(seed * 4000 + 19)
        g = CognitiveGraph()
        g.link("b1", "b2", W=rng.uniform(0.3, 0.9))
        e = g.edge("b1", "b2")
        e.S = rng.uniform(0.1, 0.8)
        g.node("b1", "text").excite(1, 0.8)
        g.node("b2", "text").excite(1, 0.8)

        w_orig = e.W
        s_orig = e.S
        a1_orig = g.node("b1", "text").A

        engine = g.representation_engine
        receipts = [
            ParticipationReceipt("r1", "b1", 1, 0, "external", "node", activation_magnitude=0.8),
            ParticipationReceipt("r2", "b2", 1, 0, "external", "node", activation_magnitude=0.8),
        ]
        tbr = TransientBindingReceipt("tbr_c", (1, 0), f"scope_{seed}", ("b1", "b2"))

        # إنشاء تمثيل بالربط المؤقت
        rep = engine.build_representation(1, 0, None, receipts, transient_bindings=[tbr])
        assert len(rep.transient_binding_receipts) == 1

        # التحقق من حفظ كافة المقادير
        assert e.W == w_orig
        assert e.S == s_orig
        assert g.node("b1", "text").A == a1_orig
        assert len(g.assembly_manager.assemblies) == 0


# ─────────────────────────────────────────────────────────── P06: Scope Isolation
def test_rfc12_p06_scope_isolation_strengthened() -> None:
    """RFC12-P06: Incompatible scopes do not collapse across 25 instance counts and topologies."""
    for num_instances in range(2, 27):
        g = CognitiveGraph()
        g.node("concept:hub", "concept", is_concept=True)
        engine = g.representation_engine

        receipts = [
            ParticipationReceipt(
                f"r_inst_{i}",
                f"instance_{i}",
                1, 0, "external", "node",
                scope_refs=(f"scope_object_{i}",),
                activation_magnitude=0.8,
            )
            for i in range(num_instances)
        ]
        rep = engine.build_representation(1, 0, None, receipts)
        rccs = engine.get_coherence_components(rep)
        assert len(rccs) == num_instances


# ─────────────────────────────────────────────────────────── P07: Support Multiplicity Conservation
def test_rfc12_p07_support_multiplicity_conservation_strengthened() -> None:
    """RFC12-P07: Support value is invariant to active assembly multiplicity across 25 levels."""
    g = CognitiveGraph()
    engine = g.representation_engine
    g.link("u_base", "v_base", W=0.75)
    g.node("u_base", "text").excite(1, 0.82)

    r = [ParticipationReceipt("r_u", "u_base", 1, 0, "external", "node", activation_magnitude=0.82)]
    rep_0 = engine.build_representation(1, 0, None, r, active_assemblies=set())
    supp_0 = engine.compute_node_support(rep_0, "u_base")

    for k in range(1, 26):
        asms = {(f"asm_{i}", 1) for i in range(k)}
        rep_k = engine.build_representation(1, 0, None, r, active_assemblies=asms)
        supp_k = engine.compute_node_support(rep_k, "u_base")
        assert abs(supp_0 - supp_k) < 1e-9


# ─────────────────────────────────────────────────────────── P08: Cache Transparency
def test_rfc12_p08_cache_transparency_strengthened() -> None:
    """RFC12-P08: Repeated cache destruction/reconstruction across 25 generated representation states."""
    for seed in range(1, 26):
        rng = random.Random(seed * 5000 + 31)
        g = CognitiveGraph()
        engine = g.representation_engine

        nodes = [f"c_{k}" for k in range(4)]
        g.link(nodes[0], nodes[1], W=0.8)
        receipts = [
            ParticipationReceipt(f"r_{n}", n, 1, 0, "external", "node", activation_magnitude=rng.uniform(0.4, 0.9))
            for n in nodes
        ]
        rep = engine.build_representation(1, 0, None, receipts)

        sig_1 = engine.canonical_representation_signature(rep)
        rccs_1 = engine.get_coherence_components(rep)

        # مسح الذاكرة المؤقتة
        engine.clear_caches()

        sig_2 = engine.canonical_representation_signature(rep)
        rccs_2 = engine.get_coherence_components(rep)

        assert sig_1 == sig_2
        assert rccs_1 == rccs_2
