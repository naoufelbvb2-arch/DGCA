"""
اختبارات المرحلة الثانية — الأعداد والكميات والحساب العلائقي (Phase 2: Numbers, Quantities & RFC-01).
تغطي:
1. الهيكل الجوهري للكميات وحصانته من التآكل (Quantity Backbone Structure & Immunity).
2. التعميم والربط متعدد اللغات للرموز العددية (Multilingual Number Grounding & Generalization).
3. ربط وتلاشي كميات الحالات العابرة (Transient Instance Count Binding & Decay).
4. المقارنة الحتمية بالمسارات (Deterministic Comparison Routine).
5. عدم الانحدار وثبات البصمة السلوكية (Regression & Baseline Signature Integrity).
"""
import math

import pytest

from dgca.config import TEXT, VISION, Law
from dgca.graph import CognitiveGraph
from dgca.numbers import QUANTITY, compare_quantities, init_quantity_backbone
from dgca.signature import behavioral_signature, build_reference_graph


def _rest(g: CognitiveGraph, ticks: int) -> None:
    for _ in range(ticks):
        g.t += 1
        g._law3_decay()


def test_quantity_backbone_structure_and_immunity():
    """التحقق من تأسيس الهيكل الجوهري للكميات (0..9) وروابط التالي والسابق والتشابه الطوبولوجي،
    وصمودها التام أمام 100 تكة صمت دون تآكل أوزانها."""
    g = CognitiveGraph()
    init_quantity_backbone(g)

    # التحقق من وجود العقد الجوهرية 0..9
    for n in range(10):
        nid = f"{QUANTITY}:{n}"
        assert nid in g.nodes
        assert g.nodes[nid].is_intrinsic is True
        assert g.nodes[nid].region == QUANTITY

    # التحقق من روابط التالي والسابق
    for n in range(9):
        e_succ = g.edge(f"{QUANTITY}:{n}", f"{QUANTITY}:{n + 1}")
        assert e_succ is not None
        assert e_succ.kind == "succ"
        assert e_succ.W == 1.0
        assert e_succ.is_intrinsic is True

        e_pred = g.edge(f"{QUANTITY}:{n + 1}", f"{QUANTITY}:{n}")
        assert e_pred is not None
        assert e_pred.kind == "pred"
        assert e_pred.W == 1.0
        assert e_pred.is_intrinsic is True

    # التحقق من القرب الطوبولوجي (sim)
    e_sim_2_5 = g.edge(f"{QUANTITY}:{2}", f"{QUANTITY}:{5}")
    assert e_sim_2_5 is not None
    assert e_sim_2_5.kind == "sim"
    assert e_sim_2_5.W == pytest.approx(math.exp(-0.35 * 3), abs=1e-5)
    assert e_sim_2_5.is_intrinsic is True

    # تشغيل 100 تكة تآكل صامتة
    _rest(g, 100)

    # التأكد من بقاء الهيكل كاملاً بأوزانه الأصلية دون أي تآكل
    for n in range(10):
        assert f"{QUANTITY}:{n}" in g.nodes
    for n in range(9):
        assert g.edge(f"{QUANTITY}:{n}", f"{QUANTITY}:{n + 1}").W == 1.0
        assert g.edge(f"{QUANTITY}:{n + 1}", f"{QUANTITY}:{n}").W == 1.0
    assert g.edge(f"{QUANTITY}:{2}", f"{QUANTITY}:{5}").W == pytest.approx(math.exp(-0.35 * 3), abs=1e-5)


def test_multilingual_number_grounding_generalization():
    """ربط 'text:خمسة' و 'text:5' بنفس الكمية الجوهرية 'quantity:5'،
    والتحقق من أن القانون 9 يشتق رابط تشابه sim بين الرمزين اللغويين."""
    g = CognitiveGraph()
    init_quantity_backbone(g)

    # ملاحظة الرمزين مع الكمية وخاصية مشتركة عبر سياقين
    for ctx in ("math_book", "lesson"):
        g.observe([(TEXT, "خمسة"), (QUANTITY, "5"), (TEXT, "count_5")], context=ctx)
        g.observe([(TEXT, "5"), (QUANTITY, "5"), (TEXT, "count_5")], context=ctx)

    # التحقق من اشتقاق رابط تماثل (sim) بين الرمز العربي والرمز الرقمي
    e_sim = g.edge("text:خمسة", "text:5")
    assert e_sim is not None
    assert e_sim.kind == "sim"
    assert e_sim.W >= Law.THETA_SIM

    # التحقق من أن الاستدلال ينقل التنشيط بالتعميم
    res = g.infer(["text:خمسة"])
    assert "text:5" in [nid for nid, _ in res["ranked"]]
    assert "text:5" in res["via_generalization"]


def test_transient_instance_count_binding_decay():
    """ربط كمية بحالة عابرة (inst:apple_1)، والتأكد من استبعادها من القفل،
    ثم إحالتها للتقاعد عند انتهاء نطاقها (RFC-01) دون التأثير على الكيانات الراسخة."""
    g = CognitiveGraph()
    init_quantity_backbone(g)

    # بناء مفهوم راسخ للتفاحة
    for ctx in ("kitchen", "garden"):
        g.observe([(TEXT, "apple"), (VISION, "red")], context=ctx)
        g.observe([(TEXT, "apple"), (VISION, "red")], context=ctx)

    # ربط حالة عابرة بالكمية 5 والتفاحة عبر عدة سياقات
    for ctx in ("plate1", "plate2", "plate3"):
        g.observe([(TEXT, "inst:apple_1"), (QUANTITY, "5"), (TEXT, "apple")], context=ctx)

    inst_nid = "text:inst:apple_1"
    assert inst_nid in g.nodes
    e_inst = g.edge(inst_nid, f"{QUANTITY}:5")
    assert e_inst is not None
    # التأكد من استثناء روابط الحالات العابرة من القفل الدائم
    assert e_inst.locked is False

    # إحالة الكيانات العابرة للتقاعد عند انتهاء النطاق التشغيلي (RFC-01 Scope Retirement)
    g.retire_transient_scope()

    # التحقق من حذف العقدة العابرة وروابطها بالكامل
    assert g.edge(inst_nid, f"{QUANTITY}:5") is None
    assert inst_nid not in g.nodes
    # التحقق من بقاء المفهوم والكمية الجوهرية سليمين
    assert "text:apple" in g.nodes
    assert f"{QUANTITY}:5" in g.nodes


def test_deterministic_comparison_routine():
    """التحقق من صحة المقارنة الحتمية compare_quantities لجميع أزواج الأعداد [0..9] والحالات الحدية."""
    g = CognitiveGraph()
    init_quantity_backbone(g)

    for a in range(10):
        for b in range(10):
            res = compare_quantities(g, a, b)
            if a < b:
                assert res == -1, f"Expected {a} < {b} to return -1, got {res}"
            elif a > b:
                assert res == 1, f"Expected {a} > {b} to return 1, got {res}"
            else:
                assert res == 0, f"Expected {a} == {b} to return 0, got {res}"

    # حالات حدية صريحة
    assert compare_quantities(g, 0, 9) == -1
    assert compare_quantities(g, 9, 0) == 1
    assert compare_quantities(g, 0, 0) == 0
    assert compare_quantities(g, 9, 9) == 0
    assert compare_quantities(g, 4, 5) == -1
    assert compare_quantities(g, 5, 4) == 1


def test_regression_and_signature():
    """التأكد من أن إضافة المرحلة الثانية لم تغير السلوك المرجعي ولا البصمة المرجعية الحتمية."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "915119d40643cb97", f"Behavioral signature drift detected: {sig}"
