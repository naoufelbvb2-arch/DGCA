"""
اختبارات المرحلة العاشرة — بيئة الوكيل الإدراكي التفاعلي والواجهة الحية (Phase 10: RFC-09).

تغطي:
1. التهيئة الشاملة لمنظومة الوكيل وجميع الأنظمة الفرعية.
2. استقبال النصوص والاستدلال اللغوي المباشر وتوليد الإجابات.
3. تشفير وهيكلة الأكواد البرمجية وتكاملها مع الذاكرة.
4. حل الألغاز التناظرية ونقل الفرضيات.
5. المقارنة الفطرية للأرقام والمقادير.
6. التكات الزمنية والتآكل والموت الخلوي للعقد اللحظية (step_time GC).
7. الفحص المجهري للعقد (inspect_node) ومعالجة العقد المفقودة.
8. عدم الانحدار وثبات البصمة السلوكية الحتمية المرجعية c4b2549940a49789.
"""

from dgca import CognitiveAgent
from dgca.signature import behavioral_signature, build_reference_graph


def test_agent_initialization():
    """التحقق من تهيئة الوكيل ومكوناته الفرعية والعمود الفقري للأرقام."""
    agent = CognitiveAgent()
    assert agent.graph is not None
    assert agent.encoder is not None
    assert agent.linearizer is not None
    assert agent.analogy is not None
    assert len(agent.history) == 0
    # التحقق من تهيئة أرقام العمود الفقري 0..9
    assert "quantity:0" in agent.graph.nodes
    assert "quantity:9" in agent.graph.nodes


def test_agent_perceive_and_query():
    """التحقق من تلقين النصوص والاستدلال وتوليد الردود اللغوية."""
    agent = CognitiveAgent()
    res = agent.perceive_text("The sun provides heat")
    assert res["status"] == "INGESTED"
    assert res["episodes_count"] >= 1

    ans = agent.query("What does sun provide?")
    assert len(ans) > 0
    assert len(agent.history) == 2
    assert agent.history[0].kind == "learn_text"
    assert agent.history[1].kind == "query"


def test_agent_code_perception():
    """التحقق من تشفير الكود البرمجي وحفظ هيكليته في الذاكرة."""
    agent = CognitiveAgent()
    code_str = "def multiply(a, b):\n    return a * b"
    res = agent.perceive_code(code_str, module="math_mod")
    assert res["status"] == "INGESTED_CODE"
    assert res["events_created"] >= 1
    assert any("param:a" in n for n in agent.graph.nodes)
    assert any("kw.return" in n for n in agent.graph.nodes)


def test_agent_analogy_solving():
    """التحقق من حل التناسب التناظري عبر الوكيل king : man :: queen : ? -> woman."""
    agent = CognitiveAgent()
    agent.graph.link("text:king", "text:man", W=0.90, kind="role:gender")
    agent.graph.link("text:queen", "text:woman", W=0.90, kind="role:gender")

    res = agent.solve_analogy("text:king", "text:man", "text:queen")
    assert res["status"] == "SUCCESS"
    assert res["target_match"] == "text:woman"
    assert res["similarity"] >= 0.70


def test_agent_quantity_comparison():
    """التحقق من المقارنة الفطرية للأعداد عبر الوكيل."""
    agent = CognitiveAgent()
    v1 = agent.compare(7, 4)
    assert v1 == "7 is greater than 4"
    v2 = agent.compare(2, 6)
    assert v2 == "2 is less than 6"
    v3 = agent.compare(5, 5)
    assert v3 == "5 is equal to 5"


def test_agent_silent_ticks_and_gc():
    """التحقق من تمرير التكات الزمنية والتآكل والموت الخلوي للعقد اللحظية."""
    agent = CognitiveAgent()
    # إضافة عقد لحظية
    agent.graph.node("inst:tmp_1", region="vision")
    agent.graph.node("inst:tmp_2", region="vision")
    agent.graph.link("inst:tmp_1", "inst:tmp_2", W=0.30, kind="assoc")

    # تمرير تكات زمنية صامتة
    res = agent.step_time(ticks=8)
    assert res["ticks"] == 8
    assert res["pruned_nodes"] >= 2
    assert "inst:tmp_1" not in agent.graph.nodes


def test_agent_node_inspection():
    """التحقق من فحص تفاصيل العقدة ومعالجة العقد المفقودة."""
    agent = CognitiveAgent()
    agent.perceive_text("Cats chase mice")

    info = agent.inspect_node("text:cats")
    assert info["nid"] == "text:cats"
    assert info["region"] == "text"
    assert "out_edges" in info
    assert "in_edges" in info

    missing = agent.inspect_node("text:non_existent_node_xyz")
    assert "error" in missing


def test_full_regression_and_signature():
    """التحقق من عدم الانحدار وثبات البصمة السلوكية المرجعية الحتمية c4b2549940a49789."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "c4b2549940a49789"
