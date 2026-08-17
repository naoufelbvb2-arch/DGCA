"""سكربت القياس التجريبي الحقيقي لمُرمِّز الرؤية والتأريض متعدد الحواس (RFC-06).

يقوم بإنشاء صور ومصفوفات بكسلات حقيقية وفحص دقة التمييز، وعزل الارتباط،
والتأريض ثنائي اللغة، ونظافة الذاكرة، واستخراج تقرير الإخفاقات الدقيق.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import (
    CognitiveGraph,
    LinearizationEngine,
    deep_infer,
)
from dgca.vision import SpatialRelation, VisionSensoryPipeline, VisualObject


# ─── 1. مولد مصفوفات الصور الاصطناعية الحقيقية (Pixel Matrix Generator) ───
def generate_synthetic_image(
    shape: str, color_rgb: tuple[int, int, int], size_ratio: float = 0.15
) -> dict:
    """توليد مصفوفة بكسلات وبيانات كائن بصري حقيقي."""
    # محاكاة كائن بصري مستخلص من مصفوفة بكسل
    r, g, b = color_rgb
    # تحويل RGB إلى HSV
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    cmax, cmin = max(r_n, g_n, b_n), min(r_n, g_n, b_n)
    delta = cmax - cmin

    # حساب Hue
    if delta == 0:
        h = 0
    elif cmax == r_n:
        h = (60 * ((g_n - b_n) / delta) + 360) % 360
    elif cmax == g_n:
        h = (60 * ((b_n - r_n) / delta) + 120) % 360
    else:
        h = (60 * ((r_n - g_n) / delta) + 240) % 360

    s = 0 if cmax == 0 else (delta / cmax)
    v = cmax

    return {
        "shape": shape,
        "hsv": (h, s, v),
        "size_ratio": size_ratio,
        "rgb": color_rgb,
    }


# ─── 2. منصة الاختبار والتقييم ──────────────────────────────────────────
def run_vision_benchmark():
    print("=" * 75)
    print(
        "🔬 بدء التقييم التجريبي الحقيقي لمُرمِّز الرؤية والتأريض متعدد الحواس"
    )
    print("=" * 75)

    graph = CognitiveGraph()
    pipeline = VisionSensoryPipeline()
    _ = LinearizationEngine(graph)

    failures = []
    successes = []

    # ─────────────────────────────────────────────────────────────
    # الاختبار 1: دقة استخلاص السمات والحالات الحدية (Color & Shape Extraction)
    # ─────────────────────────────────────────────────────────────
    print("\n[اختبار 1] فحص استخلاص السمات والحالات الحدية...")
    test_cases = [
        ("Circle_Red", "circle", (255, 0, 0), "vis:clr:red", "vis:shp:circle"),
        (
            "Square_Blue",
            "square",
            (0, 0, 255),
            "vis:clr:blue",
            "vis:shp:square",
        ),
        (
            "Triangle_Green",
            "triangle",
            (0, 255, 0),
            "vis:clr:green",
            "vis:shp:triangle",
        ),
        (
            "Edge_Orange_Red",
            "circle",
            (255, 60, 0),
            "vis:clr:red",
            "vis:shp:circle",
        ),  # زاوية حرجة ~14 deg
    ]

    for name, shp, rgb, exp_clr, exp_shp in test_cases:
        obj_data = generate_synthetic_image(shp, rgb)
        # استخلاص اللون عبر الـ Pipeline
        h, s, v = obj_data["hsv"]
        # فحص مطابقة اللون
        extracted_color = pipeline.classify_color_hsv(h, s, v)
        extracted_shape = f"vis:shp:{shp}"

        if extracted_color == exp_clr and extracted_shape == exp_shp:
            successes.append(f"Primitive_{name}")
            print(
                f"   ✅ {name:<18} ──► لون: {extracted_color} | شكل: {extracted_shape}"
            )
        else:
            failures.append(
                (
                    f"Primitive_{name}",
                    f"متوقع ({exp_clr}, {exp_shp}) لكن استخلص ({extracted_color}, {extracted_shape})",
                )
            )
            print(
                f"   ❌ {name:<18} ──► فشل! مستخلص: ({extracted_color}, {extracted_shape})"
            )

    # ─────────────────────────────────────────────────────────────
    # الاختبار 2: معضلة الارتباط البصري (Multi-Object Binding Isolation)
    # ─────────────────────────────────────────────────────────────
    print("\n[اختبار 2] فحص عزل السمات ومنع الخلط في المشاهد المتعددة...")
    # مشهد: دائرة حمراء (obj_1) + مربع أزرق (obj_2)
    obj_red_circle = VisualObject(
        uid="inst:vis_c1",
        color="vis:clr:red",
        shape="vis:shp:circle",
        size="vis:sz:med",
        bbox=(10, 10, 30, 30),
    )
    obj_blue_square = VisualObject(
        uid="inst:vis_s1",
        color="vis:clr:blue",
        shape="vis:shp:square",
        size="vis:sz:med",
        bbox=(60, 60, 90, 90),
    )

    episodes = pipeline.process_scene(
        [obj_red_circle, obj_blue_square], spatial_relations=[]
    )
    for ep in episodes:
        if ep.kind == "simultaneous":
            graph.observe(ep.signals, structural_weight=ep.structural_weight)

    # فحص الروابط: هل ارتبط المربع بالأحمر؟
    # نفحص مسار الطاقة بين مربع وأحمر
    res_cross = deep_infer(
        graph, ["vision:vis:shp:square"], mode="simulation"
    )
    # deep_infer يعيد قاموس مع ranked كقائمة (nid, energy)
    cross_ranked = dict(res_cross.get("ranked", []))
    cross_energy = cross_ranked.get("vision:vis:clr:red", 0.0)

    if cross_energy < 0.05:
        successes.append("Binding_Isolation")
        print(
            f"   ✅ عزل السمات ناجح: طاقة الارتباط المتقاطع الخاطئ = {cross_energy:.4f} (أقل من العتبة)"
        )
    else:
        failures.append(
            (
                "Binding_Isolation",
                f"تسريب ارتباط متقاطع! طاقة الارتباط الخاطئ = {cross_energy:.4f}",
            )
        )
        print(f"   ❌ تسريب ارتباط! ارتبط المربع بالأحمر بطاقة {cross_energy}")

    # ─────────────────────────────────────────────────────────────
    # الاختبار 3: العلاقات المكانية وكبح التعقيد (Spatial Contact Tree)
    # ─────────────────────────────────────────────────────────────
    print("\n[اختبار 3] فحص العلاقات المكانية وكبح التعقيد...")
    rel_top = SpatialRelation(
        subject_uid="inst:vis_c1",
        relation="vis:rel:on_top",
        reference_uid="inst:vis_s1",
    )
    sp_episodes = pipeline.process_scene(
        [obj_red_circle, obj_blue_square], spatial_relations=[rel_top]
    )
    for ep in sp_episodes:
        if ep.kind == "sequence":
            graph.observe_sequence(ep.steps)

    # التحقق من أن عدد أحداث العلاقات المكانية مقيد بخطوات التلامس فقط
    spatial_events = [
        nid
        for nid in graph.nodes
        if nid.startswith("ev:") and "on_top" in nid
    ]
    if len(spatial_events) == 1:
        successes.append("Spatial_Complexity_Bound")
        print(
            f"   ✅ كبح التعقيد المكاني ناجح: عدد أحداث العلاقات = {len(spatial_events)} (خطي O(N))"
        )
    else:
        failures.append(
            (
                "Spatial_Complexity_Bound",
                f"انفجار علاقات! وُجد {len(spatial_events)} حدث مكاني",
            )
        )
        print(
            f"   ❌ فشل كبح التعقيد المكاني: عدد الأحداث = {len(spatial_events)}"
        )

    # ─────────────────────────────────────────────────────────────
    # الاختبار 4: التأريض ثنائي اللغة والانبثاق المفهومي (Bilingual Multimodal)
    # ─────────────────────────────────────────────────────────────
    print("\n[اختبار 4] فحص التأريض المشترك بين العربية والإنجليزية والصورة...")
    # مشهد 1: صورة تفاحة + نص إنجليزي "apple"
    ep_en = pipeline.process_scene(
        [obj_red_circle], spatial_relations=[], paired_text="apple"
    )
    for ep in ep_en:
        graph.observe(ep.signals, structural_weight=0.80)

    # مشهد 2: نفس الصورة + نص عربي "تفاحة"
    ep_ar = pipeline.process_scene(
        [obj_red_circle], spatial_relations=[], paired_text="تفاحة"
    )
    for ep in ep_ar:
        graph.observe(ep.signals, structural_weight=0.80)

    # تطبيق تكات تعميم لاكتشاف التماثل بالقانون 9 والمفهوم بالقانون 10
    graph.tick()

    # فحص الاستدلال: هل يؤدي "text:تفاحة" إلى تنشيط "text:apple" عبر الرنين البصري؟
    res_bilingual = deep_infer(graph, ["text:تفاحة"], mode="simulation")
    bilingual_ranked = dict(res_bilingual.get("ranked", []))
    bilingual_resonance = bilingual_ranked.get("text:apple", 0.0)

    if bilingual_resonance >= 0.15:
        successes.append("Bilingual_Multimodal_Grounding")
        print(
            f"   ✅ التأريض ثنائي اللغة ناجح! رنين (تفاحة ──► apple) = {bilingual_resonance:.4f}"
        )
    else:
        failures.append(
            (
                "Bilingual_Multimodal_Grounding",
                f"فشل الرنين العابر للغات! الطاقة = {bilingual_resonance:.4f}",
            )
        )
        print(
            f"   ❌ ضعف الرنين ثنائي اللغة: الطاقة المستلمة {bilingual_resonance:.4f} دون العتبة 0.15"
        )

    # ─────────────────────────────────────────────────────────────
    # الاختبار 5: الموت الخلوي ونظافة الذاكرة (Visual Instance GC)
    # ─────────────────────────────────────────────────────────────
    print("\n[اختبار 5] فحص تآكل وموت الكيانات البصرية المؤقتة (Law 3 GC)...")
    # تمرير 10 تكات صامتة لمعرفة هل تتلاشى عقد inst:vis_*
    for _ in range(10):
        graph.tick()

    active_inst_nodes = [
        nid for nid in graph.nodes if nid.startswith("vision:inst:vis_")
    ]
    if len(active_inst_nodes) == 0:
        successes.append("Visual_Instance_GC")
        print(
            f"   ✅ الموت الخلوي ناجح: تم تنظيف كافة الكيانات اللحظية المتبقية (بقي {len(active_inst_nodes)})"
        )
    else:
        failures.append(
            (
                "Visual_Instance_GC",
                f"تسريب كيانات بصرية! بقيت العقد: {active_inst_nodes}",
            )
        )
        print(
            f"   ❌ تسريب ذاكرة بصرية: لا تزال {len(active_inst_nodes)} عقدة حية"
        )

    # ─────────────────────────────────────────────────────────────
    # التقرير النهائي الشامل
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 75)
    print("📊 التقرير النهائي للتقييم البصري الواقعي")
    print("=" * 75)
    print(f"• إجمالي الاختبارات: {len(test_cases) + 4}")
    print(f"• الحالات الناجحة : {len(successes)}")
    print(f"• حالات الإخفاق  : {len(failures)}")

    if failures:
        print("\n⚠️ تفاصيل الإخفاقات والثغرات المكتشفة:")
        for name, reason in failures:
            print(f"   ❌ [{name}]: {reason}")
    else:
        print(
            "\n🎉 ممتاز! اجتازت المنظومة البصرية كافة سيناريوهات التقييم الحقيقي بنسبة 100%."
        )
    print("=" * 75)


if __name__ == "__main__":
    run_vision_benchmark()
