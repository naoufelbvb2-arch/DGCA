"""
سكربت التقييم التجريبي الشامل لمحرك الاستدلال القياسي ونقل المعرفة عبر المجالات (RFC-07).

يتحقق من:
1. حل التناسب الرباعي الكلاسيكي (king : man :: queen : ? -> woman).
2. مطابقة البنية العميقة عبر المجالات (النظام الشمسي -> الذرة: Sun : Planet :: Nucleus : Electron).
3. فخ انعكاس الأدوار ورفضه (Teacher : Student :: Patient : ? -> REJECT).
4. رفض التمويه المكاني السطحي (Car on road vs Apple on table -> REJECT بسبب انخفاض SDI).
5. بوابة فحص التناقض الصارم قبل الإسقاط (Pre-Projection Contradiction Gate).
6. العزل التام للفرضيات وثبات البصمة السلوكية المرجعية (c4b2549940a49789).
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import (
    AnalogicalReasoningEngine,
    CognitiveGraph,
)
from dgca.signature import behavioral_signature, build_reference_graph


def run_analogy_benchmark():
    print("=" * 80)
    print("🧠 بدء التقييم التجريبي لمحرك الاستدلال القياسي ونقل المعرفة (RFC-07)")
    print("=" * 80)

    successes = []
    failures = []

    # ─────────────────────────────────────────────────────────────
    # السيناريو 1: حل التناسب الرباعي الكلاسيكي (King : Man :: Queen : ?)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 1] حل التناسب الرباعي الكلاسيكي (King : Man :: Queen : ?)...")
    g1 = CognitiveGraph()
    # بناء مجال المصدر (الملك والرجل) والهدف (الملكة والمرأة)
    g1._link("text:king", "text:man", kind="role:gender", W=0.90)
    g1._link("text:king", "text:crown", kind="rules", W=0.85)
    g1._link("text:queen", "text:woman", kind="role:gender", W=0.90)
    g1._link("text:queen", "text:crown", kind="rules", W=0.85)

    engine1 = AnalogicalReasoningEngine(g1)
    res1 = engine1.solve_proportion("text:king", "text:man", "text:queen")

    if res1.status == "SUCCESS" and res1.target_match == "text:woman":
        successes.append("Classical_4Way_Proportion")
        print(f"   ✅ نجاح حل التناسب: king : man :: queen : {res1.target_match} (Sim={res1.mapping.similarity:.3f})")
    else:
        failures.append(("Classical_4Way_Proportion", f"حالة: {res1.status}, المخرج: {res1.target_match}"))
        print(f"   ❌ فشل حل التناسب: {res1.status}, {res1.target_match}")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 2: مطابقة البنية العميقة عبر المجالات (Solar System -> Atom)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 2] مطابقة البنية العميقة عبر المجالات (Solar System -> Atom)...")
    g2 = CognitiveGraph()
    # النظام الشمسي: الشمس تجذب الكوكب، والكوكب يدور حول الشمس
    g2._link("text:sun", "text:planet", kind="attracts", W=0.95)
    g2._link("text:planet", "text:sun", kind="revolves_around", W=0.90)
    g2._link("text:sun", "text:gravity_force", kind="causes", W=0.85)

    # الذرة: النواة تجذب الإلكترون، والإلكترون يدور حول النواة
    g2._link("text:nucleus", "text:electron", kind="attracts", W=0.95)
    g2._link("text:electron", "text:nucleus", kind="revolves_around", W=0.90)

    engine2 = AnalogicalReasoningEngine(g2)
    mapping2 = engine2.evaluate_analogy(
        ("text:sun", "text:planet"),
        ("text:nucleus", "text:electron")
    )
    res2 = engine2.solve_proportion("text:sun", "text:planet", "text:nucleus")

    if mapping2.is_valid and mapping2.similarity >= 0.70 and res2.target_match == "text:electron":
        successes.append("Cross_Domain_Structure_Mapping")
        print(f"   ✅ مطابقة بنيوية عميقة ناجحة! Sim={mapping2.similarity:.3f}, SDI={mapping2.sdi_score:.3f}")
        print(f"   🎯 حل التناسب: Sun : Planet :: Nucleus : {res2.target_match}")
        if res2.inferences:
            print(f"   💡 الإسقاط القياسي المنقول: {res2.inferences[0].projected_edge} (Status={res2.inferences[0].status})")
    else:
        failures.append(("Cross_Domain_Structure_Mapping", f"Sim={mapping2.similarity}, Valid={mapping2.is_valid}"))
        print(f"   ❌ فشل المطابقة: Sim={mapping2.similarity}, SDI={mapping2.sdi_score}")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 3: فخ انعكاس قطبية الأدوار (Role Inversion Rejection)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 3] فحص رفض انعكاس قطبية الأدوار (Teacher:Student :: Patient:?)...")
    g3 = CognitiveGraph()
    # المعلم يعلم الطالب (Teacher -> Student)
    g3._link("text:teacher", "text:student", kind="teaches", W=0.90)
    # الطبيب يعالج المريض (Doctor -> Patient)
    g3._link("text:doctor", "text:patient", kind="treats", W=0.90)

    engine3 = AnalogicalReasoningEngine(g3)
    # محاولة قياس الفاعل بالمفعول: Teacher (Agent) : Student (Patient) :: Patient (Patient) : ?
    mapping3 = engine3.evaluate_analogy(
        ("text:teacher", "text:student"),
        ("text:patient", "text:doctor")
    )

    if not mapping3.is_valid and mapping3.similarity == 0.0:
        successes.append("Role_Inversion_Rejection")
        print("   ✅ تم كشف ورفض انعكاس الأدوار بنجاح (Polarity Gate Active).")
    else:
        failures.append(("Role_Inversion_Rejection", f"تم قبول الانعكاس الخاطئ! Sim={mapping3.similarity}"))
        print("   ❌ فشل: تم قبول انعكاس الأدوار!")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 4: رفض التمويه المكاني السطحي (Anti-Superficial Camouflage)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 4] فحص رفض التمويه المكاني السطحي (Car on road vs Apple on table)...")
    g4 = CognitiveGraph()
    g4._link("text:car", "text:road", kind="vis:rel:on_top", W=0.80)
    g4._link("text:apple", "text:table", kind="vis:rel:on_top", W=0.80)

    engine4 = AnalogicalReasoningEngine(g4)
    mapping4 = engine4.evaluate_analogy(
        ("text:car", "text:road"),
        ("text:apple", "text:table")
    )

    if not mapping4.is_valid and mapping4.sdi_score < 0.65:
        successes.append("Anti_Superficial_Camouflage")
        print(f"   ✅ تم رفض القياس السطحي: SDI={mapping4.sdi_score:.3f} (أقل من العتبة 0.65 لغياب الروابط السببية).")
    else:
        failures.append(("Anti_Superficial_Camouflage", f"تم قبول قياس سطحي! SDI={mapping4.sdi_score}"))
        print(f"   ❌ فشل: تم قبول قياس سطحي بـ SDI={mapping4.sdi_score}")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 5: بوابة فحص التناقض الصارم قبل الإسقاط (Pre-Projection Contradiction Gate)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 5] فحص حظر الإسقاط القياسي المتناقض مع مصفوفة X...")
    g5 = CognitiveGraph()
    g5._link("text:bird", "text:eagle", kind="rules", W=0.85)
    g5._link("text:eagle", "text:flies", kind="causes", W=0.90)

    g5._link("text:fish", "text:penguin", kind="rules", W=0.85)
    # تسجيل تناقض صريح: البطريق يناقض الطيران
    g5.node("text:penguin", region="text")
    g5.node("text:flies", region="text")
    g5._link_contradiction("text:penguin", "text:flies")

    engine5 = AnalogicalReasoningEngine(g5)
    res5 = engine5.solve_proportion("text:bird", "text:eagle", "text:fish")

    blocked_inferences = [inf for inf in res5.inferences if inf.status == "BLOCKED_BY_CONTRADICTION"]
    if blocked_inferences:
        successes.append("Contradiction_Gate_Blocking")
        print(f"   ✅ تم حظر الإسقاط القياسي المتناقض بنجاح: {blocked_inferences[0].projected_edge} (Status=BLOCKED_BY_CONTRADICTION)")
    else:
        failures.append(("Contradiction_Gate_Blocking", "لم يتم حظر الفرضية المتناقضة!"))
        print("   ❌ فشل: تم تمرير فرضية تناقض مصفوفة X!")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 6: العزل التام للفرضيات وثبات البصمة السلوكية المرجعية
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 6] فحص العزل التام للفرضيات وثبات البصمة السلوكية المرجعية...")
    ref_g = build_reference_graph()
    sig_before = behavioral_signature(ref_g)

    # تشغيل عمليات قياس وتجريد قوالب على الرسم المرجعي
    ref_engine = AnalogicalReasoningEngine(ref_g)
    ref_engine.solve_proportion("text:apple", "text:sweet", "text:pear", abstract_schema=True)

    sig_after = behavioral_signature(ref_g)

    if sig_before == sig_after == "c4b2549940a49789":
        successes.append("Hypothesis_Sandbox_Signature_Immunity")
        print(f"   ✅ ثبات البصمة السلوكية 100%: {sig_after} (مطابقة تامة للمرجع c4b2549940a49789)")
    else:
        failures.append(("Hypothesis_Sandbox_Signature_Immunity", f"تغيرت البصمة: {sig_before} -> {sig_after}"))
        print(f"   ❌ تغيرت البصمة السلوكية: {sig_after}")

    # ─────────────────────────────────────────────────────────────
    # التقرير النهائي الشامل
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("📊 التقرير النهائي لتقييم محرك الاستدلال القياسي (RFC-07)")
    print("=" * 80)
    print("• إجمالي السيناريوهات: 6")
    print(f"• السيناريوهات الناجحة: {len(successes)}")
    print(f"• حالات الإخفاق      : {len(failures)}")

    if failures:
        print("\n⚠️ تفاصيل الإخفاقات:")
        for name, reason in failures:
            print(f"   ❌ [{name}]: {reason}")
    else:
        print("\n🎉 ممتاز! اجتاز محرك الاستدلال القياسي كافة السيناريوهات بنسبة نجاح 100%.")
    print("=" * 80)


if __name__ == "__main__":
    run_analogy_benchmark()
