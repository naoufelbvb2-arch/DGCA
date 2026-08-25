"""
اختبارات المرحلة السابعة — مُرمِّز الحاسة البصرية والتأريض متعدد الحواس واللغات (Phase 7: RFC-06).

تغطي:
1. استخلاص السمات الحتمية وتكميم الألوان في فضاء HSV ومعاملات الأشكال الهندسية.
2. كبح التعقيد المكاني لشجرة التلامس في حدود O(N).
3. تطبيق عقد الرأس أولاً (Head-first) لكافة إشارات الكائنات البصرية.
4. إعفاء الكيانات اللحظية من قفل ق5 والموت الخلوي الإلزامي التام بعد التآكل.
5. التأريض الثلاثي بين العربية والإنجليزية والصورة وانبثاق الرنين العابر للغات.
6. كبح ميزانية الحواس وحصر السمات البصرية في سقف 3 سمات لمنع طغيان الكثافة.
7. فك تشبيك وصياغة الأحداث المكانية عبر محرك التوليد LinearizationEngine.
8. عدم الانحدار وثبات البصمة السلوكية المرجعية الحتمية c4b2549940a49789.
"""
from dgca.graph import CognitiveGraph
from dgca.linearizer import LinearizationEngine
from dgca.reasoning import deep_infer
from dgca.signature import behavioral_signature, build_reference_graph
from dgca.vision import SpatialRelation, VisionSensoryPipeline, VisualObject


def test_cv_primitive_feature_extraction():
    """التحقق من تكميم الألوان واستخلاص الأشكال والأحجام بدقة حتمية."""
    pipeline = VisionSensoryPipeline()

    # فحص الألوان
    assert pipeline.classify_color_hsv(0.0, 1.0, 1.0) == "vis:clr:red"
    assert pipeline.classify_color_hsv(120.0, 1.0, 1.0) == "vis:clr:green"
    assert pipeline.classify_color_hsv(240.0, 1.0, 1.0) == "vis:clr:blue"
    assert pipeline.classify_color_hsv(0.0, 0.05, 0.95) == "vis:clr:white"
    assert pipeline.classify_color_hsv(0.0, 0.0, 0.05) == "vis:clr:black"
    assert pipeline.classify_color_hsv(0.0, 0.05, 0.50) == "vis:clr:gray"

    # فحص الأشكال
    assert pipeline.classify_shape(circularity=0.88) == "vis:shp:circle"
    assert pipeline.classify_shape(circularity=0.75, n_vertices=3) == "vis:shp:triangle"
    assert (
        pipeline.classify_shape(
            circularity=0.75, aspect_ratio=1.0, convexity=0.95, n_vertices=4
        )
        == "vis:shp:square"
    )
    assert (
        pipeline.classify_shape(
            circularity=0.70, aspect_ratio=2.0, convexity=0.95, n_vertices=4
        )
        == "vis:shp:rectangle"
    )

    # فحص الأحجام
    assert pipeline.classify_size(0.02) == "vis:sz:small"
    assert pipeline.classify_size(0.15) == "vis:sz:medium"
    assert pipeline.classify_size(0.35) == "vis:sz:large"


def test_spatial_contact_tree_linear_complexity():
    """التحقق من أن استخراج العلاقات المكانية مقيد بـ O(N) ويمنع الانفجار O(N^2)."""
    pipeline = VisionSensoryPipeline()
    objects = [
        VisualObject("inst:vis_1", "vis:clr:red", "vis:shp:circle", "vis:sz:medium", (10, 10, 30, 30), is_focal=True),
        VisualObject("inst:vis_2", "vis:clr:blue", "vis:shp:square", "vis:sz:medium", (10, 35, 30, 55)),
        VisualObject("inst:vis_3", "vis:clr:green", "vis:shp:triangle", "vis:sz:small", (40, 10, 60, 30)),
    ]

    relations = pipeline.extract_spatial_relations(objects, max_relations_per_obj=2)
    assert len(relations) <= len(objects) * 2
    assert len(relations) >= 1


def test_vision_head_first_contract():
    """التحقق من أن معرف الكائن البصري اللحظي inst:vis_* يقع في الموضع 0 في الإشارات دائماً."""
    pipeline = VisionSensoryPipeline()
    obj = VisualObject("inst:vis_box1", "vis:clr:yellow", "vis:shp:square", "vis:sz:large", (0, 0, 50, 50), is_focal=True)

    episodes = pipeline.process_scene([obj], spatial_relations=[])
    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.signals[0][0] == "vision"
    assert ep.signals[0][1] == "inst:vis_box1"
    assert ep.structural_weight == 0.80  # كائن بؤري


def test_visual_instance_law5_immunity_and_gc():
    """التحقق من إعفاء الكيانات البصرية من القفل الدائم وتحللها خلوياً بعد التآكل."""
    graph = CognitiveGraph()
    pipeline = VisionSensoryPipeline()
    obj = VisualObject("inst:vis_tmp", "vis:clr:red", "vis:shp:circle", "vis:sz:medium", (0, 0, 20, 20))

    episodes = pipeline.process_scene([obj])
    for ep in episodes:
        graph.observe(ep.signals, structural_weight=0.80)

    # التحقق من أن الرابط ليس مقفلاً W_floor = 0
    for e in graph.edges.values():
        if "inst:vis_tmp" in e.src or "inst:vis_tmp" in e.dst:
            assert e.W_floor == 0.0
            assert not e.locked

    # إحالة الكيانات البصرية العابرة للتقاعد عند انتهاء المشهد (RFC-06 Scene Scope End)
    graph.retire_transient_scope()

    active_inst = [nid for nid in graph.nodes if "inst:vis_tmp" in nid]
    assert len(active_inst) == 0


def test_multimodal_triangular_grounding_bilingual():
    """التحقق من التأريض الثلاثي وانبثاق الرنين العابر للغات بين العربية والإنجليزية والصورة."""
    graph = CognitiveGraph()
    pipeline = VisionSensoryPipeline()
    obj = VisualObject("inst:vis_apple_shared", "vis:clr:red", "vis:shp:circle", "vis:sz:medium", (10, 10, 30, 30))

    ep_en = pipeline.process_scene([obj], paired_text="apple")
    for ep in ep_en:
        graph.observe(ep.signals, structural_weight=0.80)

    ep_ar = pipeline.process_scene([obj], paired_text="تفاحة")
    for ep in ep_ar:
        graph.observe(ep.signals, structural_weight=0.80)

    graph.tick()

    res = deep_infer(graph, ["text:تفاحة"], mode="simulation")
    ranked = dict(res.get("ranked", []))
    resonance = ranked.get("text:apple", 0.0)

    assert resonance >= 0.15


def test_modality_budget_clamping():
    """التحقق من حصر السمات البصرية في سقف 3 سمات أساسية (لون، شكل، حجم) لكل كائن."""
    pipeline = VisionSensoryPipeline()
    obj = VisualObject("inst:vis_item", "vis:clr:cyan", "vis:shp:rectangle", "vis:sz:small", (0, 0, 10, 20))

    episodes = pipeline.process_scene([obj])
    signals = episodes[0].signals

    # الرأس (1) + السمات البصرية (3) = 4 إشارات
    vis_signals = [s for s in signals if s[0] == "vision"]
    assert len(vis_signals) == 4  # uid, color, shape, size


def test_spatial_event_linearization():
    """التحقق من قدرة محرك التوليد على فك تشبيك الأحداث المكانية إلى لغة طبيعية."""
    graph = CognitiveGraph()
    pipeline = VisionSensoryPipeline()
    engine = LinearizationEngine(graph)

    obj_c = VisualObject("inst:vis_c", "vis:clr:red", "vis:shp:circle", "vis:sz:medium", (10, 10, 30, 30))
    obj_s = VisualObject("inst:vis_s", "vis:clr:blue", "vis:shp:square", "vis:sz:medium", (60, 60, 90, 90))
    rel = SpatialRelation("inst:vis_c", "vis:rel:on_top", "inst:vis_s")

    episodes = pipeline.process_scene([obj_c, obj_s], spatial_relations=[rel])
    for ep in episodes:
        if ep.kind == "simultaneous":
            graph.observe(ep.signals)
        else:
            graph.observe_sequence(ep.steps)

    packet = engine.generate(seeds=["ev:inst:vis_c->vis:rel:on_top->inst:vis_s"])
    assert packet.status == "SUCCESS"
    assert "circle" in packet.text
    assert "on_top" in packet.text
    assert "square" in packet.text


def test_full_regression_and_signature():
    """التحقق من عدم الانحدار وثبات البصمة السلوكية المرجعية الحتمية 915119d40643cb97."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "915119d40643cb97"
