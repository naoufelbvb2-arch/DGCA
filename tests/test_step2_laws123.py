"""
اختبارات الخطوة 2 — القوانين 1 و2 و3.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
from itertools import pairwise

import pytest

from dgca.config import AUDIO, TEXT, VISION, Law
from dgca.graph import CognitiveGraph, Edge


# ─────────────────── ق1 — النشوء والتأسيس
def test_law1_creates_when_product_meets_threshold():
    g = CognitiveGraph()
    i = g.node("text:a", TEXT); i.excite(1, 1.0, "ep1")
    j = g.node("text:b", TEXT); j.excite(1, 1.0, "ep1")
    e = g._law1_create(i, j)
    assert e is not None and e.W == Law.W_BASE
    assert g.edge("text:a", "text:b") is e
    assert e.t_created == g.t and e.t_last_update == g.t

def test_law1_refuses_below_threshold():
    g = CognitiveGraph()
    i = g.node("text:a", TEXT); i.excite(1, 1.0, "ep1")
    j = g.node("text:b", TEXT); j.excite(1, 0.29, "ep1")   # 1.0×0.29 < θ
    assert g._law1_create(i, j) is None
    assert g.edge("text:a", "text:b") is None

def test_law1_threshold_is_inclusive():
    g = CognitiveGraph()
    i = g.node("text:a", TEXT); i.excite(1, 1.0, "ep1")
    j = g.node("text:b", TEXT); j.excite(1, Law.THETA_CREATION, "ep1")
    assert g._law1_create(i, j) is not None

def test_law1_is_idempotent_and_directional():
    g = CognitiveGraph()
    i = g.node("text:a", TEXT); i.excite(1, 1.0, "ep1")
    j = g.node("text:b", TEXT); j.excite(1, 1.0, "ep1")
    e1 = g._law1_create(i, j)
    e2 = g._law1_create(i, j)
    assert e1 is e2 and len(g.edges) == 1
    assert g._law1_create(j, i) is not e1 and len(g.edges) == 2

def test_law1_registers_origin_tag():
    g = CognitiveGraph()
    i = g.node("text:a", TEXT); i.excite(1, 1.0, "ep1")
    j = g.node("vision:b", VISION); j.excite(1, 1.0, "ep1")
    e = g._law1_create(i, j)
    assert TEXT in e.origin and VISION in e.origin


# ─────────────────── ق2 — التعزيز الترابطي المزدوج
def test_law2_saturating_growth_unimodal():
    """W: 0.10 → 0.370 → 0.559 → 0.691 (M=1)"""
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert g.edge("text:a", "text:b").W == pytest.approx(0.6913, abs=1e-3)

def test_law2_sensory_multiplier_accelerates():
    """نمطان ⟹ M=2 ⟹ 0.640 بعد ملاحظة واحدة، مقابل 0.370 لنمط واحد"""
    g = CognitiveGraph()
    g.observe([(TEXT, "a"), (VISION, "b")], context="c")
    assert g.edge("text:a", "vision:b").W == pytest.approx(0.640, abs=1e-3)
    h = CognitiveGraph()
    h.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert h.edge("text:a", "text:b").W == pytest.approx(0.370, abs=1e-3)

def test_law2_three_modalities_give_m_three():
    g = CognitiveGraph()
    g.observe([(TEXT, "a"), (VISION, "b"), (AUDIO, "c")], context="c")
    # ΔW = η·3·1·(1−0.1) = 0.81  ⟹  W = 0.91
    assert g.edge("text:a", "vision:b").W == pytest.approx(0.910, abs=1e-3)

def test_law2_never_exceeds_wmax():
    g = CognitiveGraph()
    for _ in range(40):
        g.observe([(TEXT, "a"), (VISION, "b"), (AUDIO, "c")], context="c")
    for e in g.edges.values():
        assert e.W <= Law.W_MAX

def test_law2_updates_bookkeeping():
    g = CognitiveGraph()
    g.observe([(TEXT, "a"), (TEXT, "b")], context="kitchen")
    g.observe([(TEXT, "a"), (TEXT, "b")], context="garden")
    e = g.edge("text:a", "text:b")
    assert e.n == 2 and e.contexts == {"kitchen", "garden"}
    assert e.t_last_update == g.t

def test_law2_growth_is_monotone_and_decelerating():
    g = CognitiveGraph()
    ws = []
    for _ in range(5):
        g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
        ws.append(g.edge("text:a", "text:b").W)
    deltas = [b - a for a, b in pairwise(ws)]
    assert all(d > 0 for d in deltas)
    assert all(b < a for a, b in pairwise(deltas))


# ─────────────────── ق3 — ملغى ومحجوز (LAW 3 — ABOLISHED / RESERVED)
def test_persistent_edge_unchanged_after_unrelated_ticks():
    g = CognitiveGraph()
    g._link(Edge("a", "b", 0.500, t_last_update=-1))
    g.t += 128
    assert g.edge("a", "b").W == 0.500

def test_persistent_edge_survives_1000_ticks():
    g = CognitiveGraph()
    g.observe([(TEXT, "x"), (TEXT, "y")], context="c")
    assert g.edge("text:x", "text:y").W == pytest.approx(0.370, abs=1e-3)
    for _ in range(1000):
        g.tick()
    assert g.edge("text:x", "text:y") is not None
    assert g.edge("text:x", "text:y").W == pytest.approx(0.370, abs=1e-3)

def test_low_weight_edge_not_auto_pruned():
    g = CognitiveGraph()
    g._link(Edge("a", "b", Law.THETA_PRUNE, t_last_update=-1))
    g.tick()
    assert g.edge("a", "b") is not None
    assert g.edge("a", "b").W == Law.THETA_PRUNE

def test_zero_weight_edge_not_auto_deleted_without_owner():
    g = CognitiveGraph()
    g._link(Edge("a", "b", 0.0, t_last_update=-1))
    g.tick()
    assert g.edge("a", "b") is not None
    assert g.edge("a", "b").W == 0.0


# ─────────────────── حلقة الإدراك
def test_observe_advances_tick_and_excites():
    g = CognitiveGraph()
    g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert g.t == 1
    n = g.nodes["text:a"]
    assert n.t_spawn == 1
    assert n.episode == "ep1"
    assert n.A == pytest.approx(1.0)

def test_observe_builds_both_directions():
    g = CognitiveGraph()
    g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert g.edge("text:a", "text:b") is not None
    assert g.edge("text:b", "text:a") is not None

def test_observe_no_self_edges():
    g = CognitiveGraph()
    g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert all(a != b for a, b in g.edges)

def test_residual_binding_stops_after_two_relaxations():
    """A بعد استرخاءين = 0.3025 ≥ θ ، وبعد ثلاثة = 0.166 < θ"""
    g = CognitiveGraph()
    g.observe([(TEXT, "a")], context="c")
    g.observe([(TEXT, "filler1")], context="c")
    g.observe([(TEXT, "filler2")], context="c")
    g.observe([(TEXT, "late")], context="c")
    assert g.edge("text:late", "text:a") is None

def test_index_integrity_after_long_run():
    g = CognitiveGraph()
    syms = ["a", "b", "c", "d", "e"]
    for k in range(60):
        g.observe([(TEXT, syms[k % 5]), (VISION, syms[(k + 1) % 5])], context="c")
    out, inn = {}, {}
    for (a, b), e in g.edges.items():
        out.setdefault(a, {})[b] = e
        inn.setdefault(b, {})[a] = e
    assert {k: v for k, v in g.out_adj.items() if v} == out
    assert {k: v for k, v in g.in_adj.items() if v} == inn


# ─────────────────── البصمة السلوكية
def test_signature_is_deterministic():
    from dgca.signature import behavioral_signature, build_reference_graph
    assert behavioral_signature(build_reference_graph()) == \
           behavioral_signature(build_reference_graph())

def test_signature_detects_any_drift():
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    victim = next(iter(g.edges.values()))
    victim.W += 1e-6
    assert behavioral_signature(g) != base

def test_signature_matches_committed_baseline():
    from pathlib import Path

    from dgca.signature import behavioral_signature, build_reference_graph
    p = Path(__file__).parent / "baseline_signature.txt"
    assert p.exists(), "ملف البصمة المرجعية مفقود — يُولَّد مرة واحدة بموافقة صريحة"
    assert behavioral_signature(build_reference_graph()) == p.read_text().strip()
