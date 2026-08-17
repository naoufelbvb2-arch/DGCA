"""
اختبارات المرحلة الأولى — الإصلاحات الهيكلية للنواة (Phase 1 Structural Core Repairs).
تغطي الثغرات 22 و23 و28:
1. دورة حياة العقد وتقليم العقد المعزولة (Orphan Node Garbage Collection).
2. حماية العقد الجوهرية (Intrinsic Nodes).
3. دورة حياة عقد الأحداث التلقائية (Event Node Lifecycle).
4. البروز البنيوي المعمم (Generalized Structural Salience).
"""

from dgca.config import TEXT, Law
from dgca.graph import CognitiveGraph


def _rest(g: CognitiveGraph, ticks: int) -> None:
    for _ in range(ticks):
        g.t += 1
        g._law3_decay()


def test_orphan_node_garbage_collection():
    """التحقق من أنه عند تلاشي الرابط بين عقدتين غير جوهريتين وحذفه،
    تُحذف كلتا العقدتين المعزولتين بالكامل من self.nodes وفهارس الجوار."""
    g = CognitiveGraph()
    g.observe([(TEXT, "temp1"), (TEXT, "temp2")], context="session")
    assert "text:temp1" in g.nodes and "text:temp2" in g.nodes
    assert g.edge("text:temp1", "text:temp2") is not None

    # انتظار تلاشي الرابط (16 تكة تآكل)
    _rest(g, 20)

    assert g.edge("text:temp1", "text:temp2") is None
    assert "text:temp1" not in g.nodes
    assert "text:temp2" not in g.nodes
    assert not g.out_adj.get("text:temp1")
    assert not g.in_adj.get("text:temp2")


def test_intrinsic_node_resists_pruning():
    """التأكد من أن العقد الموسومة بـ is_intrinsic=True تبقى في self.nodes
    حتى لو كانت درجة اتصالها صفراً."""
    g = CognitiveGraph()
    n = g.node("text:root", TEXT, is_intrinsic=True)
    n.excite(1, 1.0, "ep1")

    _rest(g, 25)

    assert n.A == 0.0
    assert "text:root" in g.nodes
    assert g.nodes["text:root"].is_intrinsic is True


def test_event_node_automatic_lifecycle():
    """إنشاء عقدة حدث عبر observe_sequence وترك روابط الأدوار تتآكل دون عتبة التقليم،
    والتحقق من أن عقدة ev:* تُحذف تلقائياً من الرسم كعقدة معزولة."""
    g = CognitiveGraph()
    g.observe_sequence([[(TEXT, "start")], [(TEXT, "step")]], context="trace")
    ev_nid = "ev:start->step"
    assert ev_nid in g.nodes

    # ترك روابط الأدوار تتآكل حتى التقليم
    ticks = 0
    while any(e.src == ev_nid or e.dst == ev_nid for e in g.edges.values()):
        _rest(g, 1)
        ticks += 1
        assert ticks < 200

    # فور تقليم روابط الأدوار، تصبح العقدة معزولة وتُحذف في نفس التكة
    assert ev_nid not in g.nodes
    assert not g.out_adj.get(ev_nid)
    assert not g.in_adj.get(ev_nid)


def test_structural_salience_floor_retention():
    """التحقق من أن رابطاً أُنشئ بـ structural_weight=0.8 يحافظ على W >= W_floor
    عبر 50+ تكة صمت عندما v=0، مقاوماً التقليم المبكر في ق3."""
    g = CognitiveGraph()
    g.observe([(TEXT, "def_a"), (TEXT, "def_b")], context="grounding", valence=0.0, structural_weight=0.8)
    e = g.edge("text:def_a", "text:def_b")
    assert e is not None
    assert e.tagged
    assert e.S >= 0.8
    assert e.W_floor > 0.0

    _rest(g, 55)

    e_after = g.edge("text:def_a", "text:def_b")
    assert e_after is not None
    assert e_after.W >= e_after.W_floor
    assert e_after.W > Law.THETA_PRUNE
    assert "text:def_a" in g.nodes and "text:def_b" in g.nodes
