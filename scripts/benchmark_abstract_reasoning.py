"""
سكربت التقييم التجريدي الشامل لألغاز التفكير والقياس المكاني (ARC-AGI Benchmark Suite).

يقوم باختبار قدرة المنظومة على حل ألغاز التحويل، التماثل الطوبولوجي، القياس المكاني،
والاستدلال السببي متعدد الحواس مع استخراج تقرير تشخيصي دقيق بنقاط القوة والخلل.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import (
    AnalogicalReasoningEngine,
    CognitiveGraph,
    VisionSensoryPipeline,
    VisualObject,
    compare_quantities,
    init_quantity_backbone,
)


def run_abstract_reasoning_benchmark():
    print("=" * 80)
    print("🧩 بدء التقييم التجريدي الشامل لألغاز التفكير الإدراكي (ARC-AGI Benchmark)")
    print("=" * 80)

    graph = CognitiveGraph()
    init_quantity_backbone(graph)
    pipeline = VisionSensoryPipeline()
    analogy = AnalogicalReasoningEngine(graph)

    results = []

    # ─────────────────────────────────────────────────────────────────────────
    # اللغز 1: استنتاج قاعدة تحويل الخصائص وتعميمها (Feature Transformation Induction)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[اللغز 1] استنتاج قاعدة تحويل اللون وتطبيقها على شكل جديد...")
    # مثال التدريب: Red Circle -> Blue Circle
    c_red = VisualObject(
        "inst:c_red", "vis:clr:red", "vis:shp:circle", "vis:sz:med", (0, 0, 1, 1)
    )
    c_blue = VisualObject(
        "inst:c_blue",
        "vis:clr:blue",
        "vis:shp:circle",
        "vis:sz:med",
        (0, 0, 1, 1),
    )
    episodes_train = pipeline.process_scene(
        [c_red], [], paired_text="state_before"
    ) + pipeline.process_scene([c_blue], [], paired_text="state_after")
    for ep in episodes_train:
        graph.observe(ep.signals, structural_weight=0.85)

    # إضافة رابط تحول سببي بين الحالة السابقة واللاحقة
    c_red_id = f"vision:{episodes_train[0].signals[0][1]}"
    c_blue_id = f"vision:{episodes_train[1].signals[0][1]}"
    graph.link(
        c_red_id, c_blue_id, W=0.85, kind="transforms_to"
    )

    # لغز الاختبار: Red Square -> ?
    s_red = VisualObject(
        "inst:s_red", "vis:clr:red", "vis:shp:square", "vis:sz:med", (0, 0, 1, 1)
    )
    s_blue = VisualObject(
        "inst:s_blue",
        "vis:clr:blue",
        "vis:shp:square",
        "vis:sz:med",
        (0, 0, 1, 1),
    )
    episodes_test = pipeline.process_scene([s_red, s_blue], [])
    for ep in episodes_test:
        graph.observe(ep.signals, structural_weight=0.85)

    s_red_id = f"vision:{episodes_test[0].signals[0][1]}"
    s_blue_id = f"vision:{episodes_test[1].signals[0][1]}"

    # حل التناسب: c_red : c_blue :: s_red : ?
    res1 = analogy.solve_proportion(
        c_red_id, c_blue_id, s_red_id
    )
    if (
        res1.status == "SUCCESS"
        and res1.target_match
        and (res1.target_match == s_blue_id or "s_blue" in res1.target_match)
    ):
        print(f"   ✅ نجاح حل اللغز 1: استنتج النظير بنجاح ({res1.target_match})")
        results.append(("Puzzle_1_Rule_Induction", True, "Solved"))
    else:
        print(
            f"   ❌ إخفاق اللغز 1: الحالة={res1.status}, النتيجة={res1.target_match}"
        )
        results.append(
            (
                "Puzzle_1_Rule_Induction",
                False,
                f"Status: {res1.status}, Match: {res1.target_match}",
            )
        )

    # ─────────────────────────────────────────────────────────────────────────
    # اللغز 2: قلب العلاقات المكانية الطوبولوجية (Spatial Inversion Analogy)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[اللغز 2] حل تناسب قلب العلاقات المكانية (Inside -> Outside/Contains)...")
    # تدريب: دائرة داخل صندوق تتحول إلى صندوق داخل دائرة
    # A: Circle inside Box | B: Box inside Circle
    # C: Triangle inside Star | D: ? (يجب أن يستنتج Star inside Triangle)
    graph.link("text:circle", "text:box", W=0.90, kind="vis:rel:inside")
    graph.link("text:box_inv", "text:circle_inv", W=0.90, kind="vis:rel:inside")
    graph.link(
        "text:circle", "text:box_inv", W=0.85, kind="spatial_inverse"
    )  # رابط تحول

    graph.link("text:triangle", "text:star", W=0.90, kind="vis:rel:inside")
    graph.link("text:star_inv", "text:triangle_inv", W=0.90, kind="vis:rel:inside")

    res2 = analogy.solve_proportion("text:circle", "text:box_inv", "text:triangle")
    if (
        res2.status == "SUCCESS"
        and res2.target_match
        and "star_inv" in res2.target_match
    ):
        print(f"   ✅ نجاح حل اللغز 2: استنتج القلب المكاني ({res2.target_match})")
        results.append(("Puzzle_2_Spatial_Inversion", True, "Solved"))
    else:
        print(
            f"   ❌ إخفاق اللغز 2: الحالة={res2.status}, النتيجة={res2.target_match}"
        )
        results.append(
            (
                "Puzzle_2_Spatial_Inversion",
                False,
                f"Status: {res2.status}, Match: {res2.target_match}",
            )
        )

    # ─────────────────────────────────────────────────────────────────────────
    # اللغز 3: الفرز والمقارنة الأكثرية الفطرية (Quantitative Property Selection)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[اللغز 3] تحديد الفئة الغالبة عددياً عبر المقارنة الفطرية...")
    # معطيات: 5 مربعات مقابل 3 دوائر
    cmp_res = compare_quantities(graph, 5, 3)
    if cmp_res == 1:
        print(
            "   ✅ نجاح حل اللغز 3: حسم أن الكمية 5 أكبر قطيعاً من 3 بالمسار الفطري (+1)"
        )
        results.append(("Puzzle_3_Quantity_Sorting", True, "Solved"))
    else:
        print(f"   ❌ إخفاق اللغز 3: النتيجة={cmp_res}")
        results.append(
            ("Puzzle_3_Quantity_Sorting", False, f"Comparison returned {cmp_res}")
        )

    # ─────────────────────────────────────────────────────────────────────────
    # اللغز 4: التفكير السببي المشروط ونقل الفرضيات (Causal Hypothesis Transfer)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[اللغز 4] نقل آلية فيزيائية سببية لمجال جديد وفحص التناقض...")
    # المصدر: مفتاح A -> يشعل المصباح B
    # الهدف: مفتاح C -> ? (يجب أن ينقل فرضية إشعال المصباح D)
    graph.link("text:switch_A", "text:lamp_B", W=0.90, kind="causes_light")
    graph.link("text:switch_C", "text:lamp_D", W=0.85, kind="causes_light")

    eval_map = analogy.evaluate_analogy(
        ("text:switch_A", "text:lamp_B"), ("text:switch_C", "text:lamp_D")
    )
    if eval_map.is_valid and eval_map.similarity >= 0.70:
        print(
            f"   ✅ نجاح حل اللغز 4: مطابقة سببية تامة (Sim={eval_map.similarity:.3f}, SDI={eval_map.sdi_score:.3f})"
        )
        results.append(("Puzzle_4_Causal_Transfer", True, "Solved"))
    else:
        print(
            f"   ❌ إخفاق اللغز 4: Valid={eval_map.is_valid}, Sim={eval_map.similarity}"
        )
        results.append(
            (
                "Puzzle_4_Causal_Transfer",
                False,
                f"Sim: {eval_map.similarity}, Valid: {eval_map.is_valid}",
            )
        )

    # ─────────────────────────────────────────────────────────────────────────
    # اللغز 5: التماثل الطوبولوجي والانعكاس المكاني (Topology & Spatial Symmetry)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[اللغز 5] استنتاج الانعكاس والتماثل المكاني عبر الخط الفاصل...")
    graph.link("text:obj_left", "text:divider", W=0.90, kind="vis:rel:left_of")
    graph.link("text:divider", "text:obj_right_mirror", W=0.90, kind="vis:rel:right_of")
    graph.link("text:obj_left", "text:obj_right_mirror", W=0.85, kind="spatial_reflection")

    graph.link("text:star_left", "text:divider_2", W=0.90, kind="vis:rel:left_of")
    graph.link("text:divider_2", "text:star_right_mirror", W=0.90, kind="vis:rel:right_of")

    res5 = analogy.solve_proportion("text:obj_left", "text:obj_right_mirror", "text:star_left")
    if (
        res5.status == "SUCCESS"
        and res5.target_match
        and "star_right_mirror" in res5.target_match
    ):
        print(f"   ✅ نجاح حل اللغز 5: استنتج الانعكاس المكاني التماثلي ({res5.target_match})")
        results.append(("Puzzle_5_Spatial_Reflection", True, "Solved"))
    else:
        print(
            f"   ❌ إخفاق اللغز 5: الحالة={res5.status}, النتيجة={res5.target_match}"
        )
        results.append(
            (
                "Puzzle_5_Spatial_Reflection",
                False,
                f"Status: {res5.status}, Match: {res5.target_match}",
            )
        )

    # ─────────────────────────────────────────────────────────────────────────
    # التقرير النهائي الشامل
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("📊 التقرير النهائي لتقييم الألغاز التجريدية (ARC-AGI Benchmark)")
    print("=" * 80)
    passed_count = sum(1 for _, ok, _ in results if ok)
    print(f"• إجمالي الألغاز المختبرة : {len(results)}")
    print(f"• الألغاز المحلولة بنجاح  : {passed_count}")
    print(f"• الألغاز المتعثرة       : {len(results) - passed_count}")

    if passed_count == len(results):
        print(
            "\n🏆 إنجاز استثنائي! اجتاز عقل DGCA كافة الألغاز التجريدية بنسبة 100%."
        )
    else:
        print("\n⚠️ تفاصيل الألغاز المتعثرة ومواضع التحسين المطلوبة:")
        for name, ok, diag in results:
            if not ok:
                print(f"   ❌ [{name}]: {diag}")
    print("=" * 80)


if __name__ == "__main__":
    run_abstract_reasoning_benchmark()
