"""
اختبارات الخطوة 4 — القانونان 4 و7 (الطاقة والاستدلال).
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import math

import pytest

from dgca.config import AUDIO, TEXT, VISION, Law
from dgca.graph import CognitiveGraph, Edge


def _trained():
    """تفاحة: حمراء، مقرمشة، حلوة — عبر سياقين."""
    g = CognitiveGraph()
    for k in range(6):
        g.observe([(TEXT, "apple"), (VISION, "red"), (AUDIO, "crunch")],
                  context="kitchen" if k % 2 == 0 else "garden")
    for k in range(6):
        g.observe([(TEXT, "apple"), (TEXT, "sweet")],
                  context="kitchen" if k % 2 == 0 else "garden")
    return g


def _chain(n):
    """سلسلة موجّهة n0 → n1 → ... بأوزان قوية، بلا روابط عكسية."""
    g = CognitiveGraph()
    for i in range(n):
        g.node(f"text:n{i}", TEXT)
    for i in range(n - 1):
        g._link(Edge(f"text:n{i}", f"text:n{i+1}", 0.95))
    return g


# ─────────────────── ق4 — توازن الطاقة والسعة
def test_law4_sigma_is_exponential_saturation():
    g = CognitiveGraph()
    assert g._sigma(0.0) == pytest.approx(0.0)
    assert g._sigma(0.25) == pytest.approx(1 - math.exp(-0.25), abs=1e-9)
    assert g._sigma(10.0) < Law.C_MAX
    assert g._sigma(2.0) > g._sigma(1.0) > g._sigma(0.5)


def test_law4_outflow_cap_scales_proportionally():
    g = CognitiveGraph()
    raw = {"a": 0.9, "b": 0.9, "c": 0.9, "d": 0.9}
    out = g._cap_outflow(raw)
    assert sum(out.values()) == pytest.approx(Law.C_MAX, abs=1e-9)
    assert all(v == pytest.approx(0.25, abs=1e-9) for v in out.values())


def test_law4_outflow_below_cap_untouched():
    g = CognitiveGraph()
    raw = {"a": 0.3, "b": 0.2}
    assert g._cap_outflow(raw) == raw


def test_law4_outflow_cap_handles_empty():
    assert CognitiveGraph()._cap_outflow({}) == {}


def test_law4_activation_never_exceeds_cmax():
    g = _trained()
    for nid, a in g.infer(["vision:red"])["ranked"]:
        assert 0.0 <= a <= Law.C_MAX


# ─────────────────── ق7 — الاستدلال الانبثاقي
def test_law7_reaches_associates_from_a_single_seed():
    """الأرقام محسوبة بعد دخول عدم تناظر الدور (ق2-ب) وإلغاء التآكل (ق3)."""
    r = _trained().infer(["vision:red"])
    ranked = dict(r["ranked"])
    assert set(ranked) == {"hub:apple", "text:apple", "text:sweet", "audio:crunch"}
    assert ranked["hub:apple"] == pytest.approx(0.358, abs=1e-3)
    assert ranked["text:apple"] == pytest.approx(0.288, abs=1e-3)
    assert ranked["audio:crunch"] == pytest.approx(0.195, abs=1e-3)
    assert ranked["text:sweet"] == pytest.approx(0.165, abs=1e-3)
    assert r["answer"] == "hub:apple", "المفهوم يجمع الأنماط فيسبقها"


def test_law7_seed_excluded_from_ranking():
    r = _trained().infer(["vision:red"])
    assert all(nid != "vision:red" for nid, _ in r["ranked"])


def test_law7_indirect_association_is_weaker():
    """sweet لم يقترن بـ red قط — يصل عبر apple بتنشيط أقل."""
    g = _trained()
    assert g.edge("vision:red", "text:sweet") is None
    ranked = dict(g.infer(["vision:red"])["ranked"])
    assert ranked["text:sweet"] < ranked["text:apple"]


def test_law7_multiple_seeds_converge_superadditively():
    g = _trained()
    one = dict(g.infer(["vision:red"])["ranked"])["text:apple"]
    two = dict(g.infer(["vision:red", "audio:crunch"])["ranked"])["text:apple"]
    assert two == pytest.approx(0.58, abs=1e-3)
    assert two > one


def test_law7_unknown_seed_yields_nothing():
    r = _trained().infer(["text:ghost"])
    assert r["answer"] is None and r["ranked"] == [] and r["hops"] == 0


def test_law7_budget_decreases_linearly_and_halts():
    g = _chain(12)
    r = g.infer(["text:n0"])
    budgets = [s["E"] for s in r["trace"]]
    assert budgets[:5] == [1.0, 0.8, 0.6, 0.4, 0.2]
    assert len(budgets) == 5, "E = 0 عند القفزة السادسة ⟹ توقّف"


def test_law7_no_node_activates_twice():
    g = _trained()
    seen = [n for s in g.infer(["vision:red"])["trace"] for n in s["activated"]]
    assert len(seen) == len(set(seen))


def test_law7_no_backflow_to_parent():
    """رابطان متقابلان قويان: لا ترتد الطاقة إلى المُرسِل."""
    g = CognitiveGraph()
    g.node("text:a", TEXT); g.node("text:b", TEXT)
    g._link(Edge("text:a", "text:b", 0.95))
    g._link(Edge("text:b", "text:a", 0.95))
    r = g.infer(["text:a"])
    assert [n for s in r["trace"] for n in s["activated"]] == ["text:b"]


def test_law7_trace_shape():
    r = _trained().infer(["vision:red"])
    assert r["trace"][0]["hop"] == 1 and r["trace"][0]["E"] == 1.0
    assert set(r["trace"][0]["activated"]) == {"text:apple", "audio:crunch", "hub:apple"}
    for s in r["trace"]:
        assert set(s) == {"hop", "E", "activated"}


def test_law7_ranking_is_sorted_descending():
    vals = [v for _, v in _trained().infer(["vision:red"])["ranked"]]
    assert vals == sorted(vals, reverse=True)


def test_law7_inference_does_not_mutate_the_graph():
    g = _trained()
    before_t = g.t
    before = {(a, b): (e.W, e.n, e.t_last_update) for (a, b), e in g.edges.items()}
    before_A = {n.nid: n.A for n in g.nodes.values()}
    g.infer(["vision:red"])
    after = {(a, b): (e.W, e.n, e.t_last_update) for (a, b), e in g.edges.items()}
    assert after == before and g.t == before_t
    assert {n.nid: n.A for n in g.nodes.values()} == before_A


def test_law7_weak_signal_is_dropped():
    g = CognitiveGraph()
    g.node("text:a", TEXT); g.node("text:b", TEXT)
    g._link(Edge("text:a", "text:b", Law.MIN_SIGNAL / 2))
    assert g.infer(["text:a"])["ranked"] == []


def test_law7_stronger_edge_wins():
    g = CognitiveGraph()
    for sym in ("a", "strong", "weak"):
        g.node(f"text:{sym}", TEXT)
    g._link(Edge("text:a", "text:strong", 0.90))
    g._link(Edge("text:a", "text:weak", 0.20))
    r = g.infer(["text:a"])
    assert r["answer"] == "text:strong"
    assert dict(r["ranked"])["text:strong"] > dict(r["ranked"])["text:weak"]


# ─────────────────── البصمة
def test_signature_unchanged_by_inference():
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    for nid in list(g.nodes)[:3]:
        g.infer([nid])
    assert behavioral_signature(g) == base, "الاستدلال قراءة لا كتابة"
