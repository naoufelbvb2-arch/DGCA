"""سكربت التحقق التكاملي الحي: من استقبال النص الخام إلى التوليد اللغوي

End-to-End Pipeline: Raw Text/Code -> MasterSymbolicEncoder -> CognitiveGraph
-> Deep Resonant Reasoning -> LinearizationEngine -> Generated Text
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import (
    CognitiveGraph,
    LinearizationEngine,
    MasterSymbolicEncoder,
    init_quantity_backbone,
)


def run_live_demonstration():
    print("=" * 75)
    print("🧪 بدء الاختبار التكاملي الحي لتوليد اللغة والأفعال (DGCA Live Demo)")
    print("=" * 75)

    # 1. تهيئة المنظومة
    graph = CognitiveGraph()
    init_quantity_backbone(graph)
    encoder = MasterSymbolicEncoder()
    engine = LinearizationEngine(graph)

    # ─────────────────────────────────────────────────────────────
    # السيناريو 1: استرجاع وصياغة حدث حركي متعدٍ (Event Realization)
    # ─────────────────────────────────────────────────────────────
    print("\n[1] سيناريو الحدث اللغوي (Event Realization):")
    text_input_1 = "The cat chased the mouse"
    print(f"📥 المدخل الخام: '{text_input_1}'")

    episodes = encoder.encode_text(text_input_1)
    encoder.feed_to_graph(graph, episodes)

    # استفسار: ما الذي فعلته القطة؟ (Seed: cat)
    response = engine.generate(seeds=["text:cat"], target="text:mouse")
    print(f"   • حالة التوليد: {response.status}")
    print(f"   • المسار الطاقي: {response.trajectory}")
    print(f"   🗣️  النص المولد : \"{response.text}\"")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 2: استرجاع الصفات والتصنيف (Attributive Expression)
    # ─────────────────────────────────────────────────────────────
    print("\n[2] سيناريو الخصائص والصفات (Attributive Expression):")
    text_input_2 = "Apples are sweet and red"
    print(f"📥 المدخل الخام: '{text_input_2}'")

    episodes = encoder.encode_text(text_input_2)
    encoder.feed_to_graph(graph, episodes)

    response = engine.generate(seeds=["text:apple"], target="text:sweet")
    print(f"   • حالة التوليد: {response.status}")
    print(f"   🗣️  النص المولد : \"{response.text}\"")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 3: الاستدلال المتعدي وصياغة التبرير (Transitive Reasoning)
    # ─────────────────────────────────────────────────────────────
    print("\n[3] سيناريو الاستدلال المتعدي والتبرير اللفظي (Transitive Deduction):")
    # محاكاة شبكة القرابة: A parent B, B parent C
    graph.observe([("text", "Alice"), ("text", "Bob")], context="family")
    graph.observe([("text", "Bob"), ("text", "Charlie")], context="family")
    # إضافة روابط الأدوار
    graph._link("text:Alice", "text:Bob", kind="role:parent", W=0.90)
    graph._link("text:Bob", "text:Charlie", kind="role:parent", W=0.90)

    print("📥 المعطيات: Alice is parent of Bob, and Bob is parent of Charlie")
    response = engine.generate(seeds=["text:Alice"], target="text:Charlie")
    print(f"   • حالة التوليد: {response.status}")
    print(f"   • مسار الاستدلال: {response.trajectory}")
    print(f"   🗣️  النص المولد : \"{response.text}\"")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 4: المقارنة العددية وصياغتها لغوياً (Numerical Comparison)
    # ─────────────────────────────────────────────────────────────
    print("\n[4] سيناريو المقارنة العددية (Numerical Comparison):")
    print("📥 الاستفسار: قارن بين الكميتين 5 و 3 عبر شبكة RFC-01")
    response = engine.generate(seeds=["quantity:5"], target="quantity:3")
    print(f"   • حالة التوليد: {response.status}")
    print(f"   🗣️  النص المولد : \"{response.text}\"")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 5: فحص بوابة كشف ومنع الهلوسة (Anti-Hallucination Gate)
    # ─────────────────────────────────────────────────────────────
    print("\n[5] سيناريو اختبار منع الهلوسة (Anti-Hallucination Rejection):")
    print(
        "📥 استفسار عن علاقة كاذبة وغير موجودة: هل ترتبط 'cat' بـ 'quantum_gravity'؟"
    )
    graph.node("text:quantum_gravity", region="text")

    response = engine.generate(
        seeds=["text:cat"], target="text:quantum_gravity"
    )
    print(f"   • حالة التوليد: {response.status}")
    print(f"   🗣️  النص المولد : \"{response.text}\"")
    if response.status == "NO_RESONANT_PATH":
        print(
            "   🛡️  حكم الأمان: تم صد الهلوسة بنجاح ورفض توليد إجابة كاذبة."
        )

    # ─────────────────────────────────────────────────────────────
    # السيناريو 6: استخلاص استدعاء الكود البرمجي (Code Realization)
    # ─────────────────────────────────────────────────────────────
    print("\n[6] سيناريو صياغة الكود البرمجي (Code Realization):")
    code_input = "def calculate_area(width, height):\n    return width * height"
    print(f"📥 كود بايثون الخام:\n{code_input}")

    episodes = encoder.encode_code(code_input, module="geometry")
    encoder.feed_to_graph(graph, episodes)

    response = engine.generate(
        seeds=["text:calculate_area"], output_format="code"
    )
    print(f"   • حالة التوليد: {response.status}")
    print(f"   💻 الكود المولد : \"{response.text}\"")

    print("\n" + "=" * 75)
    print("🏁 اكتمل الاختبار التكاملي الحي بنجاح.")
    print("=" * 75)


if __name__ == "__main__":
    run_live_demonstration()
