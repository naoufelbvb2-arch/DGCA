"""
اختبارات المرحلة الرابعة — الاستدلال الرنيني العميق والتركيب المتعدي (Phase 4: RFC-03 / Law 7 Extended).
تغطي:
1. التآكل الأسي والوصول الطبيعي لـ 7-8 قفزات (Exponential Decay Natural Depth).
2. الشحن الرنيني عند المعالم المركزية وبلوغ 12-16 قفزة (Resonant Recharge Milestones).
3. السقف الحاسم لمنع الدوران اللانهائي (Hard Cap Prevents Infinite Cycles).
4. حقل الجهد الموجه نحو الهدف (Goal Potential Biases Search).
5. تركيب العلاقات المتعدية والهرمية (Transitive Relation Composition).
6. نمط المحاكاة النقي الخالي من أي أثر جانبي (Simulation Mode Zero Side-Effects).
7. عدم الانحدار وثبات البصمة السلوكية المرجعية (Full Regression & Signature Integrity).
"""
from dgca.config import TEXT
from dgca.graph import CognitiveGraph, Edge
from dgca.reasoning import compose_relations, deep_infer
from dgca.signature import behavioral_signature, build_reference_graph


def _chain(n: int, weight: float = 0.98) -> CognitiveGraph:
    g = CognitiveGraph()
    for i in range(n):
        g.node(f"text:n{i}", TEXT)
    for i in range(n - 1):
        g._link(Edge(f"text:n{i}", f"text:n{i+1}", weight, kind="assoc"))
    return g


def test_exponential_decay_natural_depth():
    """التحقق من أن التآكل الأسي في الاستدلال الرنيني يكسر حاجز القفزات الخمس الخطية
    ويصل طبيعياً إلى 7-8 قفزات عبر الروابط القوية."""
    g = _chain(12, weight=0.98)

    # الاستدلال الخطي القياسي يقف حتماً عند 5 قفزات
    r_linear = g.infer(["text:n0"], resonant=False)
    assert r_linear["hops"] == 5

    # الاستدلال الرنيني الأسي يمتد لـ 7-8 قفزات دون شحن
    r_deep = deep_infer(g, ["text:n0"], mode="resonant")
    assert r_deep["hops"] >= 7
    assert "text:n7" in [nid for nid, _ in r_deep["ranked"]]


def test_resonant_recharge_milestones():
    """التحقق من أن بلوغ المفاهيم المركزية الراسخة (hub:) يمنح شحنة تعزيز (+0.45)،
    مما يمكّن من بلوغ 12-16 قفزة عبر السلسلة الطويلة."""
    g = _chain(18, weight=0.95)

    # وضع مفاهيم مركزية راسخة كمعالم على المسار
    g.node("hub:milestone1", "hub", is_concept=True)
    g.node("hub:milestone2", "hub", is_concept=True)

    # ربط المعالم بالسلسلة وتوجيه المسار عبرها
    g._unlink("text:n4", "text:n5")
    g._link(Edge("text:n4", "hub:milestone1", 0.95, kind="assoc"))
    g._link(Edge("hub:milestone1", "text:n5", 0.95, kind="assoc"))

    g._unlink("text:n9", "text:n10")
    g._link(Edge("text:n9", "hub:milestone2", 0.95, kind="assoc"))
    g._link(Edge("hub:milestone2", "text:n10", 0.95, kind="assoc"))

    r = deep_infer(g, ["text:n0"], mode="resonant")
    # التأكد من امتداد الاستدلال لـ 12 قفزة على الأقل بفضل الشحن الرنيني
    assert r["hops"] >= 12
    ranked_nodes = [nid for nid, _ in r["ranked"]]
    assert "text:n10" in ranked_nodes
    assert "hub:milestone1" in ranked_nodes
    assert "hub:milestone2" in ranked_nodes


def test_hard_cap_prevents_infinite_cycles():
    """التحقق من أن حلقات المفاهيم المركزية المتبادلة لا تؤدي إلى رنين لانهائي،
    وتتوقف حتماً تحت سقف الشحن (recharges <= 3)."""
    g = CognitiveGraph()
    g.node("hub:a", "hub", is_concept=True)
    g.node("hub:b", "hub", is_concept=True)
    g.node("hub:c", "hub", is_concept=True)

    # حلقة مغلقة بين مفاهيم مركزية
    g._link(Edge("hub:a", "hub:b", 0.98, kind="assoc"))
    g._link(Edge("hub:b", "hub:c", 0.98, kind="assoc"))
    g._link(Edge("hub:c", "hub:a", 0.98, kind="assoc"))

    r = deep_infer(g, ["hub:a"], mode="resonant")
    # التأكد من التوقف الحتمي وعدم تجاوز السقف
    assert r["hops"] <= 20


def test_goal_potential_biases_search():
    """التحقق من أن تحديد هدف target يرفع التوصيل الفعال W_effective نحو مسار الهدف."""
    g = CognitiveGraph()
    for name in ("start", "path_a1", "path_a2", "path_b1", "path_b2", "target_dest"):
        g.node(f"text:{name}", TEXT)

    # مساران متساويان نحو الهدف ومقصد آخر
    g._link(Edge("text:start", "text:path_a1", 0.70))
    g._link(Edge("text:path_a1", "text:target_dest", 0.70))

    g._link(Edge("text:start", "text:path_b1", 0.70))
    g._link(Edge("text:path_b1", "text:path_b2", 0.70))

    # استدلال محايد
    r_neutral = deep_infer(g, ["text:start"])
    # استدلال موجه نحو الهدف
    r_guided = deep_infer(g, ["text:start"], target="text:target_dest")

    ranked_neutral = dict(r_neutral["ranked"])
    ranked_guided = dict(r_guided["ranked"])

    assert ranked_guided.get("text:target_dest", 0.0) > ranked_neutral.get("text:target_dest", 0.0)


def test_transitive_relation_composition():
    """التحقق من قواعد تركيب العلاقات المتعدية والهرمية ورفض غير المتعدي."""
    g = CognitiveGraph()

    # تعدي مباشر
    assert compose_relations(g, "A", "greater", "B", "greater", "C") == "greater"
    assert compose_relations(g, "A", "taller", "B", "taller", "C") == "taller"
    assert compose_relations(g, "A", "part_of", "B", "part_of", "C") == "part_of"
    assert compose_relations(g, "A", "succ", "B", "succ", "C") == "greater"

    # تركيب هرمي
    assert compose_relations(g, "A", "parent", "B", "parent", "C") == "grandparent"
    assert compose_relations(g, "A", "role:parent", "B", "role:parent", "C") == "role:grandparent"

    # علاقات غير متعدية تُرفض
    assert compose_relations(g, "A", "loves", "B", "loves", "C") is None
    assert compose_relations(g, "A", "friend", "B", "friend", "C") is None


def test_simulation_mode_zero_side_effects():
    """التحقق من أن نمط المحاكاة mode='simulation' هو قراءة خالصة 100% دون أي تعديل في الرسم."""
    g = build_reference_graph()
    sig_before = behavioral_signature(g)

    # تشغيل عدة استدلالات عميقة في نمط المحاكاة
    deep_infer(g, ["text:apple"], mode="simulation")
    deep_infer(g, ["vision:red"], target="text:sweet", mode="simulation")

    sig_after = behavioral_signature(g)
    assert sig_before == sig_after == "c4b2549940a49789"


def test_full_regression_and_signature():
    """التأكد من عدم حدوث أي انحدار وثبات البصمة المرجعية c4b2549940a49789."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "c4b2549940a49789"
