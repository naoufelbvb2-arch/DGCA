"""
اختبارات الخطوة 7 — البروز الانفعالي والحالة الداخلية.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
from itertools import pairwise

import pytest

from dgca.config import TEXT, VISION, Law
from dgca.graph import CognitiveGraph


def _rest(g, ticks):
    for _ in range(ticks):
        g.t += 1
        g._law3_decay()


# ─────────────────── ق8 — البروز
def test_novelty_alone_is_not_salient():
    """حدث جديد محايد: مفاجأة بلا انفعال لا تبلغ العتبة، ولا تسرّع التعلّم."""
    g = CognitiveGraph()
    g.observe([(TEXT, "chair"), (TEXT, "blue")], context="room")
    e = g.edge("text:chair", "text:blue")
    assert e.S == pytest.approx(0.36, abs=1e-3)
    assert not e.tagged and e.W_floor == 0.0


def test_neutral_novelty_is_forgotten():
    g = CognitiveGraph()
    g.observe([(TEXT, "chair"), (TEXT, "blue")], context="room")
    ticks = 0
    while g.edge("text:chair", "text:blue") is not None:
        _rest(g, 1)
        ticks += 1
        assert ticks < 200
    assert ticks == 16


def test_harm_tags_from_a_single_observation():
    g = CognitiveGraph()
    g.observe([(TEXT, "apple"), (TEXT, "seeds")], context="medical", valence=-0.9)
    e = g.edge("text:apple", "text:seeds")
    assert e.S == pytest.approx(1.0, abs=1e-3)
    assert e.tagged and e.valence == pytest.approx(-0.9)
    assert e.W_floor == pytest.approx(Law.THETA_PROTECT, abs=1e-3)


def test_only_affect_accelerates_learning():
    plain = CognitiveGraph()
    plain.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    hurt = CognitiveGraph()
    hurt.observe([(TEXT, "a"), (TEXT, "b")], context="c", valence=-0.9)
    assert plain.edge("text:a", "text:b").W == pytest.approx(0.3700, abs=1e-3)
    assert hurt.edge("text:a", "text:b").W == pytest.approx(0.5644, abs=1e-3)


def test_harm_is_weighted_above_reward():
    neg = CognitiveGraph()
    neg.observe([(TEXT, "a"), (TEXT, "b")], context="c", valence=-0.6)
    pos = CognitiveGraph()
    pos.observe([(TEXT, "a"), (TEXT, "b")], context="c", valence=+0.6)
    assert neg.edge("text:a", "text:b").S == pytest.approx(0.84, abs=1e-3)
    assert pos.edge("text:a", "text:b").S == pytest.approx(0.66, abs=1e-3)
    assert neg.edge("text:a", "text:b").S > pos.edge("text:a", "text:b").S


def test_tagging_does_not_grant_locking():
    """البروز يمنع النسيان، ولا يمنح القفل."""
    g = CognitiveGraph()
    g.observe([(TEXT, "apple"), (TEXT, "seeds")], context="medical", valence=-0.9)
    e = g.edge("text:apple", "text:seeds")
    assert e.tagged and not e.locked
    assert e.n == 1 and len(e.contexts) == 1


def test_tagged_memory_survives_long_neglect():
    g = CognitiveGraph()
    g.observe([(TEXT, "apple"), (TEXT, "seeds")], context="medical", valence=-0.9)
    _rest(g, 150)
    e = g.edge("text:apple", "text:seeds")
    assert e is not None
    assert e.W == pytest.approx(0.3238, abs=1e-3)
    assert e.S == pytest.approx(0.925, abs=1e-3)


def test_salience_fades_so_nothing_is_hoarded_forever():
    g = CognitiveGraph()
    g.observe([(TEXT, "apple"), (TEXT, "seeds")], context="medical", valence=-0.9)
    _rest(g, 150)
    ticks = 0
    while g.edge("text:apple", "text:seeds") is not None:
        _rest(g, 1)
        ticks += 1
        assert ticks < 3000
    assert ticks == 1565


# ─────────────────── ق12 — الحالة الداخلية
def test_depletion_produces_deepening_negative_valence():
    g = CognitiveGraph()
    g.add_drive("energy", level=0.9, weight=1.0, decay=0.05)
    seen = []
    for _ in range(5):
        g.observe([(TEXT, "waiting")], context="idle")
        seen.append(g.nodes["text:waiting"].V)
    assert seen[0] == pytest.approx(-0.0585, abs=1e-3)
    assert seen[-1] == pytest.approx(-0.1956, abs=1e-3)
    assert all(b < a for a, b in pairwise(seen))


def test_restoring_a_drive_is_positive():
    g = CognitiveGraph()
    g.add_drive("energy", level=0.9, weight=1.0, decay=0.05)
    for _ in range(5):
        g.observe([(TEXT, "waiting")], context="idle")
    g.restore("energy", 0.7)
    g.observe([(TEXT, "apple"), (TEXT, "eating")], context="meal")
    assert g.nodes["text:apple"].V == pytest.approx(0.297, abs=1e-3)


def test_damage_is_sharply_negative_and_tags():
    g = CognitiveGraph()
    g.add_drive("energy", level=0.9, weight=1.0, decay=0.05)
    g.damage(0.9)
    g.observe([(TEXT, "fire"), (TEXT, "touch")], context="kitchen")
    assert g.nodes["text:fire"].V < -0.1
    e = g.edge("text:fire", "text:touch")
    assert e.tagged and e.S == pytest.approx(1.0, abs=1e-3)


def test_goal_outcome_signs():
    fail = CognitiveGraph()
    fail.add_drive("e", level=0.8)
    fail.set_goal("text:reach")
    fail.resolve_goal(False)
    fail.observe([(TEXT, "detour"), (TEXT, "blocked")], context="path")
    win = CognitiveGraph()
    win.add_drive("e", level=0.8)
    win.set_goal("text:reach")
    win.resolve_goal(True)
    win.observe([(TEXT, "shortcut"), (TEXT, "open")], context="path")
    assert fail.nodes["text:detour"].V == pytest.approx(-0.18, abs=1e-3)
    assert win.nodes["text:shortcut"].V == pytest.approx(0.12, abs=1e-3)


def test_valence_attaches_to_the_entity_only():
    """الوجدان يلتصق بالمكان لا بالصفة."""
    g = CognitiveGraph()
    g.observe([(TEXT, "apple"), (TEXT, "sweet")], context="meal", valence=0.8)
    assert g.nodes["text:apple"].V == pytest.approx(0.24, abs=1e-3)
    assert g.nodes["text:sweet"].V == 0.0


def test_urgency_amplifies_when_deficit_is_deep():
    shallow = CognitiveGraph()
    shallow.add_drive("e", level=0.9)
    shallow.restore("e", 0.1)
    shallow.observe([(TEXT, "food")], context="c")
    deep = CognitiveGraph()
    deep.add_drive("e", level=0.1)
    deep.restore("e", 0.1)
    deep.observe([(TEXT, "food")], context="c")
    assert deep.nodes["text:food"].V > shallow.nodes["text:food"].V


# ─────────────────── الحكم الوجداني
def test_affective_judgement_of_an_associate():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "apple"), (TEXT, "sweet")], context="meal", valence=0.8)
    for _ in range(3):
        g.observe([(TEXT, "poison"), (TEXT, "bitter")], context="forest", valence=-0.8)
    good = g.expected_valence("text:sweet")
    bad = g.expected_valence("text:bitter")
    assert good["verdict"] == "good" and good["v"] == pytest.approx(0.526, abs=1e-3)
    assert bad["verdict"] == "bad" and bad["v"] == pytest.approx(-0.526, abs=1e-3)


def test_neutral_when_nothing_is_charged():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert g.expected_valence("text:b")["verdict"] == "neutral"


# ─────────────────── لا انحدار
def test_no_drives_means_no_valence_and_old_behaviour():
    g = CognitiveGraph()
    for k in range(6):
        g.observe([(TEXT, "apple"), (VISION, "red")],
                  context="kitchen" if k % 2 == 0 else "garden")
    assert all(n.V == 0.0 for n in g.nodes.values())
    e = g.edge("text:apple", "vision:red")
    assert e.locked and not e.tagged


def test_expected_valence_is_read_only():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "apple"), (TEXT, "sweet")], context="meal", valence=0.8)
    before = {(a, b): (e.W, e.S, e.n) for (a, b), e in g.edges.items()}
    v_before = {n.nid: n.V for n in g.nodes.values()}
    g.expected_valence("text:sweet")
    assert {(a, b): (e.W, e.S, e.n) for (a, b), e in g.edges.items()} == before
    assert {n.nid: n.V for n in g.nodes.values()} == v_before


def test_signature_captures_salience_and_valence():
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    e = next(iter(g.edges.values()))
    e.S += 0.5
    e.tagged = True
    assert behavioral_signature(g) != base
    g2 = build_reference_graph()
    b2 = behavioral_signature(g2)
    next(iter(g2.nodes.values())).V = 0.7
    assert behavioral_signature(g2) != b2
