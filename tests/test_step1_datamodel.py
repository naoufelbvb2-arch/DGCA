"""
اختبارات الخطوة ١ — نموذج البيانات.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import random

import pytest

from dgca.config import HUB, TEXT, Law
from dgca.graph import CognitiveGraph, Edge, Node


# ─────────────────────────── العقدة
def test_node_defaults():
    n = Node("text:apple", TEXT)
    assert (n.nid, n.region, n.is_concept) == ("text:apple", TEXT, False)
    assert n.A == 0.0 and n.episode is None and n.members == set()
    assert n.U == 0.0 and n.V == 0.0 and n.head is None

def test_node_excite_sets_signal_packet():
    n = Node("text:a", TEXT)
    n.excite(7, 1.0, "ep7")
    assert n.A == 1.0 and n.t_spawn == 7 and n.episode == "ep7"

def test_node_excite_capped_at_cmax():
    n = Node("text:a", TEXT)
    n.excite(1, 5.0)
    assert n.A == Law.C_MAX

def test_node_relax_decays_then_floors_to_zero():
    n = Node("text:a", TEXT)
    n.excite(1, 1.0)
    n.relax()
    assert n.A == pytest.approx(Law.RHO_ACTIVATION)
    for _ in range(20):
        n.relax()
    assert n.A == 0.0


# ─────────────────────────── الرابط
def test_edge_defaults():
    e = Edge("a", "b")
    assert e.kind == "assoc" and e.g is None and e.fwd is False
    assert e.n == 0 and e.lag == 0.0 and e.contexts == set() and e.ctx_hits == {}

def test_edge_gate_open():
    e = Edge("a", "b")
    assert e.gate_open(None) and e.gate_open("night")
    e.g = "night"
    assert e.gate_open("night")
    assert not e.gate_open("stadium")
    assert not e.gate_open(None)

def test_edges_are_independent_instances():
    e1, e2 = Edge("a", "b"), Edge("c", "d")
    e1.contexts.add("x")
    assert e2.contexts == set()


# ─────────────────────────── الشبكة
def test_node_factory_is_idempotent():
    g = CognitiveGraph()
    a = g.node("text:apple", TEXT)
    b = g.node("text:apple", TEXT)
    assert a is b and len(g.nodes) == 1

def test_edge_lookup_missing_returns_none():
    assert CognitiveGraph().edge("a", "b") is None

def test_link_populates_all_three_structures():
    g = CognitiveGraph()
    e = Edge("a", "b", 0.5)
    g._link(e)
    assert g.edges[("a", "b")] is e
    assert g.out_adj["a"]["b"] is e
    assert g.in_adj["b"]["a"] is e
    assert g.edge("a", "b") is e

def test_unlink_removes_from_all_three_structures():
    g = CognitiveGraph()
    g._link(Edge("a", "b"))
    g._unlink("a", "b")
    assert ("a", "b") not in g.edges
    assert not g.out_adj.get("a")
    assert not g.in_adj.get("b")

def test_unlink_missing_edge_is_safe():
    CognitiveGraph()._unlink("nope", "nada")   # لا يرفع استثناءً

def test_out_and_in_edges():
    g = CognitiveGraph()
    for a, b in (("a", "b"), ("a", "c"), ("z", "b")):
        g._link(Edge(a, b))
    assert {e.dst for e in g.out_edges("a")} == {"b", "c"}
    assert {e.src for e in g.in_edges("b")} == {"a", "z"}
    assert g.out_edges("ghost") == [] and g.in_edges("ghost") == []

def test_relink_same_pair_replaces_cleanly():
    g = CognitiveGraph()
    g._link(Edge("a", "b", 0.1))
    g._link(Edge("a", "b", 0.9))
    assert len(g.edges) == 1
    assert g.edge("a", "b").W == 0.9
    assert g.out_adj["a"]["b"] is g.edge("a", "b")
    assert g.in_adj["b"]["a"] is g.edge("a", "b")


# ─────────────────────────── الثبات البنيوي (الأهم)
def _rebuild(g):
    out, inn = {}, {}
    for (a, b), e in g.edges.items():
        out.setdefault(a, {})[b] = e
        inn.setdefault(b, {})[a] = e
    return out, inn

def _prune_empty(d):
    return {k: v for k, v in d.items() if v}

def test_index_integrity_under_random_churn():
    random.seed(1234)
    g = CognitiveGraph()
    ids = [f"n{i}" for i in range(12)]
    for _ in range(600):
        a, b = random.choice(ids), random.choice(ids)
        if a == b:
            continue
        if random.random() < 0.6:
            g._link(Edge(a, b, random.random()))
        else:
            g._unlink(a, b)
    out, inn = _rebuild(g)
    assert _prune_empty(g.out_adj) == out
    assert _prune_empty(g.in_adj) == inn
    for (a, b), e in g.edges.items():
        assert g.out_adj[a][b] is e and g.in_adj[b][a] is e

def test_redirect_edge_endpoint_keeps_integrity():
    """سيناريو الدمج: نقل رابط من عقدة إلى أخرى."""
    g = CognitiveGraph()
    e = Edge("old", "target", 0.7)
    g._link(e)
    g._unlink("old", "target")
    e.src = "new"
    g._link(e)
    out, inn = _rebuild(g)
    assert _prune_empty(g.out_adj) == out and _prune_empty(g.in_adj) == inn
    assert g.edge("new", "target").W == 0.7 and g.edge("old", "target") is None


# ─────────────────────────── متفرقات
def test_log_records_tick():
    g = CognitiveGraph()
    g.t = 5
    g._say("حدث")
    assert len(g.log) == 1 and "5" in g.log[0] and "حدث" in g.log[0]

def test_stats_shape():
    g = CognitiveGraph()
    g.node("text:a", TEXT)
    g.node("hub:c", HUB, is_concept=True)
    g._link(Edge("text:a", "hub:c"))
    s = g.stats()
    assert s["t"] == 0 and s["nodes"] == 2 and s["edges"] == 1 and s["concepts"] == 1
