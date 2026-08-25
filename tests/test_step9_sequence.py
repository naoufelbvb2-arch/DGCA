"""
اختبارات الخطوة 9 — التتابع الزمني والدور.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import pytest

from dgca.config import TEXT, VISION
from dgca.graph import CognitiveGraph


def W(sym):
    return [(TEXT, sym)]


def _bite():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe_sequence([W("dog"), W("bit"), W("man")], context="street")
        g.observe_sequence([W("man"), W("bit"), W("dog")], context="street")
    return g


def _chain():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe_sequence([W("a"), W("b"), W("c"), W("d")], context="seq")
    return g


def _events(g):
    return sorted(n for n in g.nodes if n.startswith("ev:"))


# ─────────────────── الاختبار الفاصل
def test_same_nodes_opposite_meanings():
    """الكلب عضّ الرجل ≠ الرجل عضّ الكلب — بنفس العقد الثلاث."""
    g = _bite()
    assert _events(g) == ["ev:dog->bit->man", "ev:man->bit->dog"]
    forward = g.predict_next(["text:dog", "text:bit"])
    backward = g.predict_next(["text:man", "text:bit"])
    assert forward["answer"] == "text:man"
    assert backward["answer"] == "text:dog"
    assert forward["answer"] != backward["answer"]


def test_roles_are_positional():
    g = _bite()
    ev = "ev:dog->bit->man"
    assert g.edge(ev, "text:dog").kind == "role0"
    assert g.edge(ev, "text:bit").kind == "role1"
    assert g.edge(ev, "text:man").kind == "role2"
    assert g.edge("text:dog", ev).kind == "role0"


def test_unknown_prefix_invents_nothing():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe_sequence([W("water"), W("boils"), W("at"), W("hundred")], context="phys")
        g.observe_sequence([W("water"), W("freezes"), W("at"), W("zero")], context="phys")
    assert g.predict_next(["text:water", "text:boils", "text:at"])["answer"] == "text:hundred"
    assert g.predict_next(["text:water", "text:freezes", "text:at"])["answer"] == "text:zero"
    empty = g.predict_next(["text:water", "text:glows", "text:at"])
    assert empty["answer"] is None and empty["ranked"] == []


def test_prefix_must_match_from_position_zero():
    g = _bite()
    assert g.predict_next(["text:bit"])["answer"] is None


# ─────────────────── الاتجاه والمسافة
def test_forward_far_outweighs_backward():
    g = _chain()
    fwd = g.edge("text:a", "text:b")
    rev = g.edge("text:b", "text:a")
    assert fwd.W == pytest.approx(0.7839, abs=1e-3)
    assert rev.W == pytest.approx(0.2032, abs=1e-3)
    assert fwd.W > 3 * rev.W


def test_lag_records_its_direction():
    g = _chain()
    assert g.edge("text:a", "text:b").lag == pytest.approx(1.0)
    assert g.edge("text:b", "text:a").lag == pytest.approx(-1.0)
    assert g.edge("text:a", "text:d").lag == pytest.approx(3.0)


def test_temporal_distance_is_damped():
    g = _chain()
    near = g.edge("text:a", "text:b").W
    far = g.edge("text:a", "text:d").W
    assert far == pytest.approx(0.4362, abs=1e-3)
    assert near > far


def test_ambiguous_corpus_gives_zero_mean_lag():
    """dog→bit ورد بالترتيبين: تناظر حقيقي في البيانات لا خلل."""
    g = _bite()
    assert g.edge("text:dog", "text:bit").lag == pytest.approx(0.0, abs=1e-9)


# ─────────────────── التزامن داخل الخطوة
def test_within_step_keeps_role_logic():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe_sequence([[(TEXT, "apple"), (TEXT, "sweet")], W("tastes")], context="c")
    ent_attr = g.edge("text:apple", "text:sweet").W
    attr_ent = g.edge("text:sweet", "text:apple").W
    assert ent_attr > attr_ent, "منطق الدور يعمل داخل الخطوة الواحدة"


def test_simultaneous_observe_creates_no_event():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "apple"), (VISION, "red")], context="kitchen")
    assert _events(g) == []


# ─────────────────── تفاعل مع القوانين السابقة
def test_events_are_never_merged():
    """أعضاؤهما متطابقة و J = 1.0 — الترتيب هو الفارق الوحيد."""
    g = _bite()
    a = g.nodes["ev:dog->bit->man"]
    b = g.nodes["ev:man->bit->dog"]
    assert a.members == b.members
    assert len(_events(g)) == 2


def test_event_edges_do_not_pollute_similarity():
    g = _bite()
    for e in g.edges.values():
        if e.kind.startswith("role"):
            assert e.kind not in ("assoc", "sim", "cat")
    assert all(k not in g._neighborhood("text:dog") for k in _events(g))


def test_event_layer_survives_neglect_by_decay_rules():
    g = _bite()
    before = len([e for e in g.edges.values() if e.kind.startswith("role")])
    for _ in range(200):
        g.tick()
    after = len([e for e in g.edges.values() if e.kind.startswith("role")])
    assert after == before, "روابط الأدوار لا تتآكل بمرور الوقت في غياب الدليل"


def test_sequence_respects_salience_channel():
    g = CognitiveGraph()
    g.observe_sequence([W("touch"), W("fire")], context="kitchen", valence=-0.9)
    e = g.edge("text:touch", "text:fire")
    assert e.tagged and e.S == pytest.approx(1.0, abs=1e-3)


def test_valence_imprints_on_first_head_only():
    g = CognitiveGraph()
    g.observe_sequence([W("dog"), W("bit"), W("man")], context="street", valence=-0.8)
    assert g.nodes["text:dog"].V == pytest.approx(-0.24, abs=1e-3)
    assert g.nodes["text:man"].V == 0.0


# ─────────────────── سلامة عامة
def test_predict_is_read_only():
    g = _bite()
    before = {(a, b): (e.W, e.n, e.kind) for (a, b), e in g.edges.items()}
    g.predict_next(["text:dog", "text:bit"])
    assert {(a, b): (e.W, e.n, e.kind) for (a, b), e in g.edges.items()} == before


def test_indexes_consistent_after_sequences():
    g = _bite()
    out, inn = {}, {}
    for (a, b), e in g.edges.items():
        out.setdefault(a, {})[b] = e
        inn.setdefault(b, {})[a] = e
    assert {k: v for k, v in g.out_adj.items() if v} == out
    assert {k: v for k, v in g.in_adj.items() if v} == inn
    live = set(g.nodes)
    assert all(a in live and b in live for a, b in g.edges)


def test_signature_captures_lag():
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    next(iter(g.edges.values())).lag += 1.0
    assert behavioral_signature(g) != base


def test_reference_graph_exercises_every_law():
    """الرسم المرجعي يجب أن يمتحن السلوك لا التمثيل وحده."""
    from dgca.signature import build_reference_graph
    g = build_reference_graph()
    kinds = {e.kind for e in g.edges.values()}
    assert "assoc" in kinds
    assert any(k.startswith("role") for k in kinds), "لا حدث في الرسم المرجعي"
    assert any(n.startswith("hub:") for n in g.nodes), "لا مفهوم في الرسم المرجعي"
