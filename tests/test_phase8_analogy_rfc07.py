"""
اختبارات المرحلة الثامنة — محرك الاستدلال القياسي ونقل المعرفة عبر المجالات (Phase 8: RFC-07).

تغطي:
1. مطابقة البنية العميقة عبر المجالات (Solar System -> Atom: Sim >= 0.70).
2. حل التناسب التناظري الرباعي (king : man :: queen : ? -> woman).
3. فحص قطبية الأدوار ورفض انعكاس الفاعل والمفعول (Teacher : Student :: Patient : ? -> REJECT).
4. كشف ورفض التمويه المكاني السطحي (Car on road vs Apple on table -> REJECT بسبب انخفاض SDI).
5. بوابة فحص التناقض الصارم قبل الإسقاط (Pre-Projection Contradiction Gate via Law 4 X).
6. العزل التام لمستودع الفرضيات وعدم تعديل مصفوفة الروابط الأساسية.
7. تجريد القوالب العلائقية schema:* وعزل توصيلها في أوضاع الاستدلال العادية والمحاكاة.
8. عدم الانحدار وثبات البصمة السلوكية المرجعية الحتمية c4b2549940a49789.
"""

from dgca import (
    AnalogicalReasoningEngine,
    CognitiveGraph,
    deep_infer,
)
from dgca.signature import behavioral_signature, build_reference_graph


def test_cross_domain_structural_mapping():
    """التحقق من مطابقة النظام الشمسي بنموذج الذرة برنين وتماثل بنيوي عميق Sim >= 0.70."""
    g = CognitiveGraph()
    # النظام الشمسي
    g._link("text:sun", "text:planet", kind="attracts", W=0.95)
    g._link("text:planet", "text:sun", kind="revolves_around", W=0.90)
    g._link("text:sun", "text:gravity_force", kind="causes", W=0.85)

    # الذرة
    g._link("text:nucleus", "text:electron", kind="attracts", W=0.95)
    g._link("text:electron", "text:nucleus", kind="revolves_around", W=0.90)

    engine = AnalogicalReasoningEngine(g)
    mapping = engine.evaluate_analogy(
        ("text:sun", "text:planet"),
        ("text:nucleus", "text:electron")
    )
    assert mapping.is_valid
    assert mapping.similarity >= 0.70
    assert mapping.sdi_score >= 0.65


def test_solve_analogical_proportion_king_queen():
    """التحقق من حل التناسب الكلاسيكي: king : man :: queen : ? -> woman."""
    g = CognitiveGraph()
    g._link("text:king", "text:man", kind="role:gender", W=0.90)
    g._link("text:king", "text:crown", kind="rules", W=0.85)
    g._link("text:queen", "text:woman", kind="role:gender", W=0.90)
    g._link("text:queen", "text:crown", kind="rules", W=0.85)

    engine = AnalogicalReasoningEngine(g)
    res = engine.solve_proportion("text:king", "text:man", "text:queen")

    assert res.status == "SUCCESS"
    assert res.target_match == "text:woman"
    assert res.mapping is not None
    assert res.mapping.similarity >= 0.70


def test_role_inversion_polarity_rejection():
    """التحقق من كشف ورفض انعكاس الأدوار (Teacher : Student :: Patient : ?)."""
    g = CognitiveGraph()
    g._link("text:teacher", "text:student", kind="teaches", W=0.90)
    g._link("text:doctor", "text:patient", kind="treats", W=0.90)

    engine = AnalogicalReasoningEngine(g)
    mapping = engine.evaluate_analogy(
        ("text:teacher", "text:student"),
        ("text:patient", "text:doctor")
    )
    assert not mapping.is_valid
    assert mapping.similarity == 0.0


def test_anti_superficial_spatial_camouflage():
    """التحقق من رفض القياس الزائف المبني على روابط مكانية عابرة SDI < 0.65."""
    g = CognitiveGraph()
    g._link("text:car", "text:road", kind="vis:rel:on_top", W=0.80)
    g._link("text:apple", "text:table", kind="vis:rel:on_top", W=0.80)

    engine = AnalogicalReasoningEngine(g)
    mapping = engine.evaluate_analogy(
        ("text:car", "text:road"),
        ("text:apple", "text:table")
    )
    assert not mapping.is_valid
    assert mapping.sdi_score < 0.65


def test_pre_projection_contradiction_blocking():
    """التحقق من حظر الإسقاط القياسي إذا تعارضت الفرضية مع مصفوفة التناقض X."""
    g = CognitiveGraph()
    g._link("text:bird", "text:eagle", kind="rules", W=0.85)
    g._link("text:eagle", "text:flies", kind="causes", W=0.90)

    g._link("text:fish", "text:penguin", kind="rules", W=0.85)
    g.node("text:penguin", region="text")
    g.node("text:flies", region="text")
    g._link_contradiction("text:penguin", "text:flies")

    engine = AnalogicalReasoningEngine(g)
    res = engine.solve_proportion("text:bird", "text:eagle", "text:fish")

    assert res.status == "SUCCESS"
    assert res.target_match == "text:penguin"
    blocked = [inf for inf in res.inferences if inf.status == "BLOCKED_BY_CONTRADICTION"]
    assert len(blocked) >= 1
    # لم تُضف الفرضية المحظورة إلى hypotheses
    assert not any("flies" in h.get("dst", "") for h in g.hypotheses)


def test_hypothesis_sandbox_zero_graph_mutation():
    """التحقق من أن حفظ الفرضيات لا يُعدل أوزان الروابط الأساسية أو مصفوفة الرسم الدائمة."""
    g = CognitiveGraph()
    g._link("text:sun", "text:planet", kind="attracts", W=0.95)
    g._link("text:planet", "text:sun", kind="revolves_around", W=0.90)
    g._link("text:sun", "text:gravity_force", kind="causes", W=0.85)

    g._link("text:nucleus", "text:electron", kind="attracts", W=0.95)
    g._link("text:electron", "text:nucleus", kind="revolves_around", W=0.90)

    edge_count_before = len(g.edges)
    engine = AnalogicalReasoningEngine(g)
    res = engine.solve_proportion("text:sun", "text:planet", "text:nucleus", project_inferences=True)

    assert res.status == "SUCCESS"
    assert len(g.hypotheses) >= 1
    # عدد الروابط الدائمة في edges لم يتغير
    assert len(g.edges) == edge_count_before


def test_schema_abstraction_and_conductance_isolation():
    """التحقق من تجريد القالب schema:* وعزل توصيله في نمط الاستدلال العادي."""
    g = CognitiveGraph()
    g._link("text:sun", "text:planet", kind="attracts", W=0.95)
    g._link("text:planet", "text:sun", kind="revolves_around", W=0.90)
    g._link("text:nucleus", "text:electron", kind="attracts", W=0.95)
    g._link("text:electron", "text:nucleus", kind="revolves_around", W=0.90)

    engine = AnalogicalReasoningEngine(g)
    res = engine.solve_proportion("text:sun", "text:planet", "text:nucleus", abstract_schema=True)

    assert res.status == "SUCCESS"
    assert res.schema_id is not None
    assert res.schema_id.startswith("schema:")
    assert res.schema_id in g.nodes

    # ربط القالب بعقدة خارجية لفحص العزل التوصيلي
    g._link(res.schema_id, "text:galaxy", kind="schema", W=0.90)

    # 1. في نمط الاستدلال العادي أو المحاكاة: التوصيل معزول (0.0)
    sim_res = deep_infer(g, seeds=[res.schema_id], mode="simulation")
    ranked_sim = dict(sim_res.get("ranked", []))
    assert "text:galaxy" not in ranked_sim

    # 2. في النمط القياسي mode="analogical": بوابات القالب مفتوحة
    ana_res = deep_infer(g, seeds=[res.schema_id], mode="analogical")
    ranked_ana = dict(ana_res.get("ranked", []))
    assert "text:galaxy" in ranked_ana


def test_full_regression_and_signature():
    """التحقق من عدم الانحدار وثبات البصمة السلوكية المرجعية الحتمية c4b2549940a49789."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "c4b2549940a49789"
