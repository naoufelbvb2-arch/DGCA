"""
اختبارات المرحلة السادسة — محرك فك التشبيك والتوليد الخطي وحلقة الفعل (Phase 6: RFC-05 / Linearization Engine).
تغطي:
1. توليد الجمل النشطة من عقد الأحداث ev:* والأدوار (Active Voice Event Linearization).
2. كبح التكرار ومنع الدوران العكسي في الروابط الثنائية (Inhibition of Return Prevents Echo Loops).
3. بوابة منع الهلوسة في غياب المسار الرنيني (Disconnected Hallucination Rejection).
4. العزل التخيلي التام وعدم تعديل الرسم بأي شكل (Ephemeral Overlay Zero Graph Mutation).
5. فك تشبيك المقارنات العددية إلى لغة طبيعية (Numerical Comparison Linearization).
6. صياغة استدعاءات الكود البرمجي التنفيذية (Code AST Call Synthesis).
7. صياغة التفسير الاستدلالي المتعدي (Transitive Reasoning Explanation).
8. عدم الانحدار وثبات البصمة السلوكية المرجعية (Full Regression & Signature Integrity).
"""
from dgca.config import TEXT
from dgca.encoder import CodeSensoryPipeline, MasterSymbolicEncoder
from dgca.graph import CognitiveGraph, Edge
from dgca.linearizer import LinearizationEngine
from dgca.numbers import init_quantity_backbone
from dgca.signature import behavioral_signature, build_reference_graph


def test_linearize_simple_event_active_voice():
    """التحقق من توليد جملة متسلسلة صحيحة 'dog bit man' من عقدة حدث ev:* وأدوارها."""
    g = CognitiveGraph()
    g.observe_sequence([[(TEXT, "dog")], [(TEXT, "bit")], [(TEXT, "man")]])

    engine = LinearizationEngine(g)
    packet = engine.generate(seeds=["text:dog"], target="text:man")

    assert packet.status == "SUCCESS"
    assert packet.text == "dog bit man"
    assert packet.tokens == ["dog", "bit", "man"]


def test_inhibition_of_return_prevents_echo_loops():
    """التحقق من أن الكبح التنافسي المؤقت يمنع الدوران والتكرار اللانهائي بين عقدتين مترابطتين بقوة."""
    g = CognitiveGraph()
    g.observe([(TEXT, "apple"), (TEXT, "red")])
    g.observe([(TEXT, "apple"), (TEXT, "red")])

    engine = LinearizationEngine(g)
    ordered = engine._competitive_queue({"text:apple": 1.0, "text:red": 1.0}, "text:apple", max_steps=10)

    # يجب أن تتوقف السلسلة فور زيارة العقد المتاحة دون تكرار
    assert len(ordered) == 2
    assert ordered == ["text:apple", "text:red"]


def test_disconnected_hallucination_rejection():
    """التحقق من أن محاولة التوليد بين عقدتين غير موصولتين برنين كافٍ تعيد NO_RESONANT_PATH منعاً للهلوسة."""
    g = CognitiveGraph()
    g.observe([(TEXT, "cat")])
    g.observe([(TEXT, "airplane")])

    engine = LinearizationEngine(g)
    packet = engine.generate(seeds=["text:cat"], target="text:airplane")

    assert packet.status == "NO_RESONANT_PATH"
    assert packet.text == ""


def test_mental_overlay_zero_graph_mutation():
    """التحقق من أن تشغيل التوليد 50 مرة في نمط المحاكاة العازلة لا يُعدل أوزان الرسم أو بصمته السلوكية."""
    g = build_reference_graph()
    sig_before = behavioral_signature(g)

    engine = LinearizationEngine(g)
    for _ in range(50):
        engine.generate(seeds=["text:apple"], target="text:sweet")
        engine.generate(seeds=["vision:red"], target="text:apple")

    sig_after = behavioral_signature(g)
    assert sig_before == sig_after == "c4b2549940a49789"


def test_linearize_numerical_comparison():
    """التحقق من فك تشبيك المقارنة العددية إلى جملة طبيعية عبر العمود الفقري الفطري للكميات."""
    g = CognitiveGraph()
    init_quantity_backbone(g)

    engine = LinearizationEngine(g)

    packet_gt = engine.generate(seeds=["quantity:5"], target="quantity:3")
    assert packet_gt.status == "SUCCESS"
    assert packet_gt.text == "5 is greater than 3"

    packet_lt = engine.generate(seeds=["quantity:2"], target="quantity:7")
    assert packet_lt.status == "SUCCESS"
    assert packet_lt.text == "2 is less than 7"


def test_linearize_code_ast_call():
    """التحقق من صياغة استدعاءات الكود البرمجي بدقة بناءً على مواضع المعاملات البنيوية."""
    g = CognitiveGraph()
    pipeline = CodeSensoryPipeline(use_structural_roles=True)
    eps = pipeline.process("def compute(total, rate):\n    return total * rate\n")
    MasterSymbolicEncoder().feed_to_graph(g, eps)

    engine = LinearizationEngine(g)
    packet = engine.generate(seeds=["text:compute"], output_format="code")

    assert packet.status == "SUCCESS"
    assert "compute(" in packet.text
    assert "param:pos_0" in packet.text
    assert "param:pos_1" in packet.text


def test_transitive_reasoning_explanation():
    """التحقق من صياغة مسار الاستدلال المتعدي وتفسيره بلغة طبيعية واضحة."""
    g = CognitiveGraph()
    g._link(Edge("text:A", "text:B", 0.90, kind="parent"))
    g._link(Edge("text:B", "text:C", 0.90, kind="parent"))

    engine = LinearizationEngine(g)
    packet = engine.generate(seeds=["text:A"], target="text:C")

    assert packet.status == "SUCCESS"
    assert "grandparent" in packet.text
    assert "because" in packet.text


def test_full_regression_and_signature():
    """التأكد من عدم حدوث أي انحدار وثبات البصمة السلوكية المرجعية الحتمية c4b2549940a49789."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "c4b2549940a49789"
