"""
اختبارات المرحلة الثالثة — محرك التنبؤ والسببية والتعلم من الخيبة (Phase 3: RFC-02 / Law 13).
تغطي:
1. حدود بركة التنبؤ وتوليد الطاقة الاستشرافية (Prediction Pool Bounds & Activation).
2. تآكل الخيبة عند فشل التوقع (Disappointment Decay on Miss).
3. إلغاء القفل بالتباطؤ بعد ثلاث خيبات متتالية (Hysteresis Unlock after 3 Failures).
4. السببية التفاضلية المحلية: صياح الديك وشروق الشمس (Differential Causality: Rooster vs Sunrise).
5. اشتقاق فشل الهدف تلقائياً من خيبة التوقع (Goal Failure Derived from Disappointment).
6. عدم الانحدار وثبات البصمة السلوكية المرجعية (Full Regression & Signature Integrity).
"""
import pytest

from dgca.causality import causal_strength
from dgca.config import AUDIO, TEXT, VISION, Law
from dgca.graph import CognitiveGraph
from dgca.signature import behavioral_signature, build_reference_graph


def test_prediction_pool_bounds_and_activation():
    """التحقق من توليد الطاقة الاستشرافية Â_j(t) عبر روابط fwd ودخول العقد في بركة التنبؤ
    حصراً إذا بلغت عتبة التنبؤ θ_pred = 0.25."""
    g = CognitiveGraph(enable_prediction=True)
    g.observe([(TEXT, "cloud"), (VISION, "dark")], context="sky")

    # بعد التكة الأولى، text:cloud (الرأس) نشط وله رابط fwd نحو vision:dark
    assert "vision:dark" in g.prediction_pool
    assert g.prediction_pool["vision:dark"] >= Law.THETA_PRED


def test_disappointment_decay_on_miss():
    """التحقق من تآكل وزن الرابط فوراً عند خيبة التوقع مع احترام أرضية الحماية W_floor وزيادة k_fail."""
    g = CognitiveGraph(enable_prediction=True)
    g.observe([(TEXT, "bell"), (AUDIO, "ring")], context="lab")
    g.observe([(TEXT, "bell"), (AUDIO, "ring")], context="lab")

    e = g.edge("text:bell", "audio:ring")
    assert e is not None
    w_before = e.W
    assert e.k_fail == 0

    # عند التكة التالية، يُقرع الجرس دون سماع الرنين (خيبة توقع)
    g.observe([(TEXT, "bell"), (VISION, "flash")], context="lab")

    e_after = g.edge("text:bell", "audio:ring")
    assert e_after is not None
    assert e_after.W < w_before
    assert e_after.W >= e_after.W_floor
    assert e_after.k_fail == 1


def test_hysteresis_unlock_after_three_failures():
    """التحقق من أن الرابط المقفل يمتص الخيبة بتآكل مخفف (1 - 0.8 = 0.2)،
    لكنه يلغي القفل بالتباطؤ فور بلوغ 3 خيبات متتالية."""
    g = CognitiveGraph(enable_prediction=True)

    # بناء رابط مقفل راسخ
    for ctx in ("c1", "c2", "c3"):
        g.observe([(TEXT, "switch"), (VISION, "light")], context=ctx)
        g.observe([(TEXT, "switch"), (VISION, "light")], context=ctx)

    e = g.edge("text:switch", "vision:light")
    assert e is not None
    assert e.locked is True

    # خيبة 1
    g.observe([(TEXT, "switch")], context="test")
    assert e.k_fail == 1
    assert e.locked is True

    # خيبة 2
    g.observe([(TEXT, "switch")], context="test")
    assert e.k_fail == 2
    assert e.locked is True

    # خيبة 3: إلغاء القفل بالتباطؤ
    g.observe([(TEXT, "switch")], context="test")
    assert e.k_fail == 3
    assert e.locked is False


def test_differential_causality_rooster_vs_sunrise():
    """التحقق من أن السببية التفاضلية تفصل الاقتران الزائف عالي التكرار (صياح الديك قبل الشروق)
    عن السببية الحقيقية (مفتاح النور والضوء)."""
    # 1. صياح الديك وشروق الشمس: الشروق يقع دائماً (BaseRate ≈ 1.0)
    g_rooster = CognitiveGraph()
    for _ in range(80):
        g_rooster.observe([(VISION, "sunrise")])
    for _ in range(20):
        g_rooster.observe_sequence([[(TEXT, "rooster")], [(VISION, "sunrise")]])

    c_rooster = causal_strength(g_rooster, "text:rooster", "vision:sunrise")
    assert c_rooster == pytest.approx(0.0, abs=1e-4)

    # 2. مفتاح النور والضوء: الضوء لا يقع إلا عند الضغط على المفتاح
    g_switch = CognitiveGraph()
    for _ in range(80):
        g_switch.observe([(TEXT, "idle")])
    for _ in range(20):
        g_switch.observe_sequence([[(TEXT, "switch_on")], [(VISION, "light_on")]])

    c_switch = causal_strength(g_switch, "text:switch_on", "vision:light_on")
    assert c_switch > 0.5


def test_goal_failure_derived_from_disappointment():
    """التحقق من اشتقاق نبضة فشل الهدف السلبية o(t) تلقائياً عند خيبة توقع العقدة المستهدفة."""
    g = CognitiveGraph(enable_prediction=True)
    g.observe([(TEXT, "lever"), (TEXT, "food")], context="cage")
    g.observe([(TEXT, "lever"), (TEXT, "food")], context="cage")

    # تحديد الهدف
    g.goal = "text:food"
    assert "text:food" in g.prediction_pool

    # التكة التالية: الضغط على الرافعة دون ظهور الطعام
    g.observe([(TEXT, "lever"), (TEXT, "empty")], context="cage")

    # اشتقاق نبضة فشل سالبة وتفريغ الهدف وطبع الوجدان السالب على الرأس
    assert g.nodes["text:lever"].V < 0.0
    assert g.goal is None


def test_full_regression_and_signature():
    """التأكد من مطابقة البصمة السلوكية المرجعية الحتمية 915119d40643cb97 وعدم حدوث أي انحدار."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "915119d40643cb97"
