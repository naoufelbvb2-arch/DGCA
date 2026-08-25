"""
اختبارات المرحلة الأولى — الإصلاحات الهيكلية للنواة (Phase 1 Structural Core Repairs).
تغطي الثغرات 22 و23 و28:
1. دورة حياة العقد وتقليم العقد المعزولة (Orphan Node Garbage Collection).
2. حماية العقد الجوهرية (Intrinsic Nodes).
3. دورة حياة عقد الأحداث التلقائية (Event Node Lifecycle).
4. البروز البنيوي المعمم (Generalized Structural Salience).
"""

import pytest

from dgca.config import TEXT
from dgca.graph import CognitiveGraph


def _rest(g: CognitiveGraph, ticks: int) -> None:
    for _ in range(ticks):
        g.tick()


def test_orphan_node_garbage_collection():
    """التحقق من أنه عند فك الرابط بين عقدتين غير جوهريتين،
    تُحذف كلتا العقدتين المعزولتين محلياً (RFC-10 Local Orphan Reclamation)."""
    g = CognitiveGraph()
    g.observe([(TEXT, "temp1"), (TEXT, "temp2")], context="session")
    assert "text:temp1" in g.nodes and "text:temp2" in g.nodes
    assert g.edge("text:temp1", "text:temp2") is not None

    # فك صريح للرابط عبر المالكون المحولون (Local Orphan Reclamation)
    g.unlink("text:temp1", "text:temp2")
    g.unlink("text:temp2", "text:temp1")

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

    assert "text:root" in g.nodes
    assert g.nodes["text:root"].is_intrinsic is True


def test_event_node_automatic_lifecycle():
    """عقد الحدث تظل حية مع مرور التكات وتستعاد عند الفك الصريح لأدوارها."""
    g = CognitiveGraph()
    g.observe_sequence([[(TEXT, "start")], [(TEXT, "step")]], context="trace")
    ev_nid = "ev:start->step"
    assert ev_nid in g.nodes

    # التكات الصامتة لا تقتلها
    _rest(g, 50)
    assert ev_nid in g.nodes

    # عند فك أدوار الحدث صراحة تُستعاد العقدة معزولةً محلياً
    for e in list(g.out_edges(ev_nid)) + list(g.in_edges(ev_nid)):
        g.unlink(e.src, e.dst)

    assert ev_nid not in g.nodes


def test_structural_salience_floor_retention():
    """التحقق من أن رابطاً أُنشئ بـ structural_weight=0.8 يحافظ على أوزانه
    عبر 55+ تكة صمت تحت إدراك استمراري حيادي."""
    g = CognitiveGraph()
    g.observe([(TEXT, "def_a"), (TEXT, "def_b")], context="grounding", valence=0.0, structural_weight=0.8)
    e = g.edge("text:def_a", "text:def_b")
    assert e is not None
    assert e.tagged
    assert e.S >= 0.8
    initial_w = e.W

    _rest(g, 55)

    e_after = g.edge("text:def_a", "text:def_b")
    assert e_after is not None
    assert e_after.W == pytest.approx(initial_w)
    assert "text:def_a" in g.nodes and "text:def_b" in g.nodes
