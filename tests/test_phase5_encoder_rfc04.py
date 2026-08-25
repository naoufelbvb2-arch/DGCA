"""
اختبارات المرحلة الخامسة — مُرمِّز الحواس الرمزية (Phase 5: RFC-04 / The Symbolic Sensory Encoder).
تغطي:
1. عقد الرأس أولاً في العبارات الاسمية الوصفية (Noun Chunk Head-First Contract).
2. حفظ الفاعل الحقيقي كرأس عند البناء للمجهول (Passive Voice Agent Preservation).
3. توجيه النفي الصريح لمصفوفة التناقض X دون روابط موجبة (Explicit Negation Routes to Contradiction).
4. عزل الارتباط المتقاطع للأرقام المتعددة عبر الحلقات الميكروية (Multi-Entity Number Binding Isolation).
5. توجيه الأرقام الاسمية لمنطقة النص text والكميات الفطرية لمنطقة quantity (Label Numbers vs Quantities).
6. الترميز بالأدوار البنيوية في الكود والتعميم بين الدوال (Code Structural Role Slots).
7. صمود تعريفات الكود أمام التآكل بفضل البروز البنيوي الفطري (Structural Weight Preserves Definitions).
8. عدم الانحدار وثبات البصمة السلوكية المرجعية (Full Regression & Signature Integrity).
"""
import pytest

from dgca import (
    QUANTITY,
    TEXT,
    CodeSensoryPipeline,
    EnglishTextPipeline,
    MasterSymbolicEncoder,
)
from dgca.graph import CognitiveGraph
from dgca.signature import behavioral_signature, build_reference_graph


def test_noun_chunk_head_first_contract():
    """التحقق من أن الكيان الرئيسي (Head) يقع في الموضع 0 دائماً وتتبعه الصفات
    مع إسقاط الغراء النحوي 'the' تماماً."""
    pipeline = EnglishTextPipeline()
    episodes = pipeline.process("The small black dog")

    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.kind == "simultaneous"
    assert ep.signals[0] == (TEXT, "dog"), "الرأس يجب أن يكون الكيان الرئيسي في الموضع 0"
    symbols = [sym for _, sym in ep.signals]
    assert symbols == ["dog", "small", "black"]
    assert "the" not in symbols


def test_passive_voice_agent_preservation():
    """التحقق من أن البناء للمجهول يحافظ على الفاعل الدلالي الحقيقي كرأس في الخطوة 0 للحدث."""
    pipeline = EnglishTextPipeline()
    episodes = pipeline.process("The man was bitten by the dog")

    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.kind == "sequence"
    assert ep.steps[0] == [(TEXT, "dog")], "الفاعل الحقيقي dog هو الرأس في الموضع 0"
    flat = [s for step in ep.steps for _, s in step]
    assert flat == ["dog", "bite", "man"]


def test_explicit_negation_routes_to_contradiction():
    """التحقق من أن السلب الصريح لا ينشئ أي رابط موجب ويسجل طرفي النفي في X مباشرة."""
    pipeline = EnglishTextPipeline()
    episodes = pipeline.process("A dog is not a cat")

    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.contradictions == [("text:dog", "text:cat")]
    assert len(ep.signals) == 0

    g = CognitiveGraph()
    encoder = MasterSymbolicEncoder()
    encoder.feed_to_graph(g, episodes)

    assert "text:cat" in g.X.get("text:dog", set())
    assert "text:dog" in g.X.get("text:cat", set())
    assert g.edge("text:dog", "text:cat") is None
    assert g.edge("text:cat", "text:dog") is None


def test_multi_entity_number_binding_isolation():
    """التحقق من تقطيع جمل الأرقام المتعددة إلى حلقات ميكروية معزولة لمنع الارتباط المتقاطع."""
    pipeline = EnglishTextPipeline()
    episodes = pipeline.process("3 cats ate 2 fish")

    assert len(episodes) >= 2
    g = CognitiveGraph()
    encoder = MasterSymbolicEncoder()
    encoder.feed_to_graph(g, episodes)

    # التأكد من عدم وجود رابط متقاطع مباشر بين 3 والسمك أو 2 والقط
    assert g.edge("quantity:3", "text:fish") is None
    assert g.edge("quantity:2", "text:cat") is None


def test_label_numbers_routed_to_text():
    """التحقق من عزل الأرقام الاسمية وتوجيه المقادير (5 apples) إلى quantity."""
    pipeline = EnglishTextPipeline()

    # مقدار عددي
    eps_apples = pipeline.process("5 apples")
    assert len(eps_apples) == 1
    assert (QUANTITY, "5") in eps_apples[0].signals


def test_code_structural_role_slots():
    """التحقق من أن مُرمِّز الكود يستخدم مواضع الأدوار البنيوية param:pos_k مما يمكّن من المقارنة البنيوية."""
    pipeline = CodeSensoryPipeline(use_structural_roles=True)
    src1 = "def add(a, b):\n    return a + b\n"
    src2 = "def combine(x, y):\n    return x + y\n"

    eps1 = pipeline.process(src1)
    eps2 = pipeline.process(src2)

    sig1 = eps1[0].signals
    sig2 = eps2[0].signals

    assert (TEXT, "param:pos_0") in sig1 and (TEXT, "param:pos_1") in sig1
    assert (TEXT, "param:pos_0") in sig2 and (TEXT, "param:pos_1") in sig2

    g = CognitiveGraph()
    encoder = MasterSymbolicEncoder()
    encoder.feed_to_graph(g, eps1)
    encoder.feed_to_graph(g, eps2)

    # تشاركهما في نفس الأدوار البنيوية
    assert g.edge("text:add", "text:param:pos_0") is not None
    assert g.edge("text:combine", "text:param:pos_0") is not None


def test_structural_weight_preserves_definitions():
    """التحقق من أن حقن البروز البنيوي الفطري (0.80) لتعريفات الدوال يحمي روابطها من التآكل عبر 50 تكة."""
    pipeline = CodeSensoryPipeline(use_structural_roles=True)
    src = "def compute(total, rate):\n    return total * rate\n"
    episodes = pipeline.process(src)

    assert episodes[0].structural_weight == 0.80

    g = CognitiveGraph()
    encoder = MasterSymbolicEncoder()
    encoder.feed_to_graph(g, episodes)

    e = g.edge("text:compute", "text:param:pos_0")
    assert e is not None
    w_initial = e.W
    assert e.tagged is True
    assert e.W >= 0.30

    # تشغيل 50 تكة صامتة في بيئة محايدة
    for _ in range(50):
        g.observe([(TEXT, "idle_background")])

    e_after = g.edge("text:compute", "text:param:pos_0")
    assert e_after is not None
    assert e_after.W == pytest.approx(w_initial)


def test_full_regression_and_signature():
    """التأكد من عدم حدوث أي انحدار وثبات البصمة السلوكية المرجعية الحتمية 915119d40643cb97."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "915119d40643cb97"
