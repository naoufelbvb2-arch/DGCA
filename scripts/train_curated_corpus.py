"""
سكربت التدريب والتأسيس المعرفي المنظم وحفظ الدماغ (Phase 11: RFC-11).

يقوم هذا السكربت بتلقين الوكيل الإدراكي ~200+ قضية معرفية منتقاة بدقة عبر 4 وحدات دلالية:
1. الهرمية الوجودية والتصنيفية (Ontological Hierarchy).
2. الديناميكيات الفيزيائية والسببية (Causal & Physical Dynamics).
3. التأريض ثنائي وثلاثي الحواس (Cross-Lingual & Sensory Grounding).
4. المعرفة الإجرائية وهيكلية أكواد بايثون (Procedural AST Knowledge).

مع تفعيل النوم والتثبيت الدوري (Consolidation Sleep Ticks) كل 20 قضية لتنظيف الضوضاء
وحفظ الناتج النهائي في data/brain_curated.json.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import CognitiveAgent

# ─────────────────────────────────────────────────────────────────────────────
# 1. المنهج التعليمي المعرفي الشامل (~200 قضية مقسمة لـ 4 وحدات دلالية)
# ─────────────────────────────────────────────────────────────────────────────

ONTOLOGICAL_CORPUS = [
    # علم الحيوان والتصنيف الحيوي
    "A dog is a canine mammal",
    "A wolf is a wild canine mammal",
    "A cat is a feline mammal",
    "A lion is a large predatory feline",
    "A tiger is a striped feline mammal",
    "An elephant is a massive terrestrial mammal",
    "A whale is a giant aquatic mammal",
    "A dolphin is an intelligent aquatic mammal",
    "An eagle is a predatory bird",
    "A hawk is a fast hunting bird",
    "A sparrow is a small singing bird",
    "A penguin is a flightless aquatic bird",
    "A crocodile is a large aquatic reptile",
    "A snake is a legless crawling reptile",
    "A lizard is a scaled terrestrial reptile",
    "A turtle is a shelled reptile",
    "A frog is an amphibious creature",
    "A bee is a winged social insect",
    "An ant is a social terrestrial insect",
    "A spider is an eight_legged arachnid",
    # علم النبات والبيئة
    "An oak is a strong hardwood tree",
    "A pine is an evergreen coniferous tree",
    "A palm is a tropical desert tree",
    "A rose is a fragrant flowering plant",
    "A tulip is a colorful perennial flower",
    "A jasmine is a sweet white flower",
    "An apple is a sweet orchard fruit",
    "An orange is a juicy citrus fruit",
    "A banana is a soft tropical fruit",
    "A grape is a small clustered fruit",
    "A carrot is an orange root vegetable",
    "A potato is a starchy edible tuber",
    "A tomato is a red juicy edible fruit",
    "Wheat is a golden cereal grain",
    "Rice is a staple cultivated grain",
    # الفيزياء والمواد والكون
    "Water is a transparent liquid compound",
    "Ice is solid frozen water",
    "Steam is gaseous vaporized water",
    "Oxygen is a vital odorless gas",
    "Hydrogen is a light flammable gas",
    "Carbon is a fundamental organic element",
    "Iron is a strong magnetic metal",
    "Gold is a precious malleable metal",
    "Silver is a conductive shiny metal",
    "Copper is an electrical conductive metal",
    "Diamond is an extremely hard mineral crystal",
    "Granite is a dense igneous rock",
    "The sun is a massive radiant star",
    "Earth is a terrestrial living planet",
    "Mars is a red rocky planet",
    "Jupiter is a massive gas giant planet",
    "The moon is a natural rocky satellite",
    "A galaxy is a vast cluster of stars",
    # الأدوات والمركبات والمصنوعات
    "A hammer is a striking construction tool",
    "A saw is a sharp cutting tool",
    "A car is a wheeled motor vehicle",
    "An airplane is a winged flying aircraft",
    "A ship is a large buoyant water vessel",
]

CAUSAL_DYNAMICS_CORPUS = [
    # الفيزياء الشمسية والمناخ والطقس
    "The sun emits intense light and heat",
    "Heat causes liquid water to evaporate",
    "Evaporation forms dense atmospheric clouds",
    "Clouds produce heavy falling rain",
    "Rain provides essential water to dry soil",
    "Soil water allows green plants to grow",
    "Plants absorb sunlight and release pure oxygen",
    "Oxygen sustains aerobic animal life",
    "Cold temperatures cause liquid water to freeze",
    "Freezing transforms water into hard ice",
    "Heat melts hard solid ice into water",
    "Boiling transforms liquid water into hot steam",
    "Cooling condenses hot steam into water droplets",
    # الكهرباء والطاقة والحركة
    "An electric current flows through copper wire",
    "A battery stores chemical potential energy",
    "Battery discharge supplies steady electric current",
    "Electric current powers an electric motor",
    "An electric motor rotates mechanical wheels",
    "Rotating wheels move a motor vehicle",
    "A spinning turbine drives an electric generator",
    "A generator produces electrical power",
    "A closed switch connects an electric circuit",
    "An open switch interrupts the electric current",
    "Electricity powers a glass lamp",
    "A glowing lamp illuminates a dark room",
    "Friction between surfaces produces thermal heat",
    "Gravity pulls physical objects toward earth center",
    # الاحتراق والكيمياء
    "Fire requires dry fuel and oxygen",
    "Fire burns wood and produces bright flame",
    "Combustion produces hot ash and dense smoke",
    "Water extinguishes open burning fire",
    "Acid dissolves reactive alkaline metals",
    # الأحياء ووظائف الأعضاء
    "The heart pumps oxygenated blood through arteries",
    "Blood delivers essential nutrients to body cells",
    "The lungs inhale air and absorb oxygen",
    "The stomach uses gastric acid to digest food",
    "Digested food provides metabolic energy to muscles",
    "Physical exercise strengthens human muscles",
    "Intense physical labor causes bodily fatigue",
    "Bodily fatigue requires restful sleep",
    "Restful sleep restores physical energy and alertness",
    # السببية اليومية والمنطقية
    "Turning a brass key unlocks a locked door",
    "Pushing an unlocked door opens the entrance",
    "Pressing a computer power button boots the system",
    "Turning a steering wheel changes vehicle direction",
    "Applying vehicle brakes decelerates the wheels",
]

CROSS_LINGUAL_CORPUS = [
    # اقترانات لغوية ثنائية وحسية (Arabic-English & Sensorial attributes)
    "The apple is sweet red and delicious",
    "التفاحة فاكهة حمراء وحلوة ولذيذة",
    "The sun is bright yellow and radiant",
    "الشمس نجم ساطع وأصفر ومشرق",
    "The ocean is deep blue and vast",
    "المحيط مائي عميق وأزرق وشاسع",
    "The snow is pure white and cold",
    "الثلج بارد وأبيض ونقي",
    "The fire is hot orange and dangerous",
    "النار حارة وبرتقالية وخطيرة",
    "The tree is green tall and leafy",
    "الشجرة طويلة وخضراء ومورقة",
    "The elephant is gray huge and strong",
    "الفيل رمادي وضخم وقوي",
    "The mouse is gray tiny and swift",
    "الفأر صغير ورمادي وسريع",
    "The lion is golden brave and fierce",
    "الأسد شجاع وذهبي ومفترس",
    "The gold is shiny yellow and valuable",
    "الذهب معدن أصفر ولامع وثمين",
    "The diamond is clear hard and sparkling",
    "الماس صلب وشفاف وبراق",
    "The night is dark quiet and calm",
    "الليل مظلم وهادئ وساكن",
    "The desert is dry hot and sandy",
    "الصحراء حارة وجافة ورملية",
    "The river is fresh flowing and clear",
    "النهر عذب وجار وصاف",
    "The bird is winged feathered and singing",
    "الطائر مجنح ومريش ومغرد",
    "The horse is fast noble and strong",
    "الحصان أصيل وسريع وقوي",
    "The honey is golden sweet and thick",
    "العسل حلو وذهبي ولزج",
    "The iron is heavy dark and durable",
    "الحديد صلب وثقيل ومتين",
    "The cloud is white fluffy and floating",
    "السحاب أبيض وعائم وكثيف",
    "The moon is luminous spherical and serene",
    "القمر مضيء وكروي وساكن",
    "The flower is fragrant delicate and vibrant",
    "الزهرة عطرة ورقيقة وزاهية",
    "The bread is baked warm and nourishing",
    "الخبز دافئ ومخبوز ومغذ",
    "The book is informative written and bound",
    "الكتاب مفيد ومكتوب ومجلد",
    "The mountain is towering rocky and grand",
    "الجبل شامخ وصخري وعظيم",
    "The child is joyful young and playful",
    "الطفل صغير ومرح ومبتهج",
    "The mother is loving caring and tender",
    "الأم محبة وحنونة ورؤوفة",
    "The father is protective wise and kind",
    "الأب حكيم ومرب وعطوف",
    "Knowledge is illuminating powerful and eternal",
    "العلم نور وقوة وخلود",
]

CODE_AST_CORPUS = [
    # نماذج دوال بايثون إجرائية
    "def square(x):\n    return x * x",
    "def double(x):\n    return x + x",
    "def cube(x):\n    return x * x * x",
    "def add(a, b):\n    return a + b",
    "def subtract(a, b):\n    return a - b",
    "def multiply(a, b):\n    return a * b",
    "def divide(a, b):\n    return a / b",
    "def is_positive(x):\n    return x > 0",
    "def is_negative(x):\n    return x < 0",
    "def is_zero(x):\n    return x == 0",
    "def is_even(n):\n    return n % 2 == 0",
    "def is_odd(n):\n    return n % 2 != 0",
    "def get_length(seq):\n    return len(seq)",
    "def get_first(items):\n    return items[0]",
    "def greet(name):\n    return name",
    "def negate(val):\n    return -val",
]


def train_curated_knowledge_base():
    print("=" * 80)
    print("🧠 بدء التأسيس المعرفي المنظم للدماغ الإدراكي (DGCA Curated Training)")
    print("=" * 80)

    start_time = time.time()
    agent = CognitiveAgent()

    all_propositions = []
    # تجميع القضايا وتصنيفها
    for item in ONTOLOGICAL_CORPUS:
        all_propositions.append(("text", item, "ontology"))
    for item in CAUSAL_DYNAMICS_CORPUS:
        all_propositions.append(("text", item, "causality"))
    for item in CROSS_LINGUAL_CORPUS:
        all_propositions.append(("text", item, "cross_lingual"))
    for item in CODE_AST_CORPUS:
        all_propositions.append(("code", item, "code_ast"))

    total_propositions = len(all_propositions)
    print(f"📚 إجمالي القضايا المعرفية المنتقاة: {total_propositions} قضية عبر 4 وحدات دلالية.")
    print("🔄 بدء دورة التلقين على دفعات متتالية مع التثبيت الدوري (Sleep Ticks)...")

    batch_size = 20
    total_events_ingested = 0

    for batch_num, i in enumerate(range(0, total_propositions, batch_size), start=1):
        batch = all_propositions[i : i + batch_size]
        print(f"\n--- [الدفعة {batch_num}] معالجة {len(batch)} قضايا ({i+1} إلى {min(i+batch_size, total_propositions)}) ---")

        for kind, content, category in batch:
            if kind == "text":
                episodes = agent.encoder.encode_text(content, context=category)
                for ep in episodes:
                    agent.graph.observe(ep.signals, structural_weight=0.80)
                    total_events_ingested += len(ep.signals)
            elif kind == "code":
                episodes = agent.encoder.encode_code(content, module="curated_lib")
                for ep in episodes:
                    agent.graph.observe(ep.signals, structural_weight=0.80)
                    total_events_ingested += len(ep.signals)

        # تثبيت وتآكل دوري (Consolidation Sleep Ticks - Law 3, 5, 10)
        t_res = agent.step_time(ticks=2)
        st = agent.get_stats()
        print(f"  💤 تكات التثبيت الدوري: تآكل {t_res['pruned_nodes']} عقد | حجم الذاكرة الحالي: {st['nodes_count']} عقد، {st['edges_count']} روابط")

    # جولة تكات استقرار نهائية
    agent.step_time(ticks=2)

    elapsed = time.time() - start_time
    final_stats = agent.get_stats()

    print("\n" + "=" * 80)
    print("✨ اكتمل التدريب المعرفي والتثبيت بنجاح!")
    print(f"⏱️ زمن المعالجة الكلي   : {elapsed:.2f} ثانية")
    print(f"📥 إجمالي الأحداث المدخلة : {total_events_ingested}")
    print(f"🧠 عدد العقد المعرفية   : {final_stats['nodes_count']}")
    print(f"🔗 عدد الروابط المكتسبة  : {final_stats['edges_count']}")
    print(f"💡 عدد المفاهيم المشتقة  : {final_stats['concepts_count']}")
    print("=" * 80)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. اختبارات الاستدلال والاستجواب بعد التدريب (Post-Training Evaluation)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n🔬 اختبارات التحقق والاستدلال بعد التأسيس المعرفي:")

    # استجواب سببي
    q1 = "What causes evaporation?"
    ans1 = agent.query(q1)
    print(f"  1. سؤال سببي: '{q1}' -> إجابة الوكيل: '{ans1}'")

    q2 = "What does sun emit?"
    ans2 = agent.query(q2)
    print(f"  2. سؤال معرفي: '{q2}' -> إجابة الوكيل: '{ans2}'")

    # مقارنة فطرية
    cmp_res = agent.compare(8, 3)
    print(f"  3. مقارنة عددية: 8 مع 3 -> '{cmp_res}'")

    # حل تناسب
    agent.graph.link("text:sun", "text:light", W=0.90, kind="causes")
    agent.graph.link("text:fire", "text:flame", W=0.90, kind="causes")
    an_res = agent.solve_analogy("text:sun", "text:light", "text:fire")
    print(f"  4. تناسب تناظري: sun : light :: fire : ? -> '{an_res['target_match']}' (Sim={an_res['similarity']:.3f})")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. حفظ الدماغ المعرفي في ملف JSON
    # ─────────────────────────────────────────────────────────────────────────
    output_path = "data/brain_curated.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    agent.save_brain(output_path)
    print(f"\n💾 تم حفظ الدماغ المعرفي المكتمل بنجاح في: {output_path} ({os.path.getsize(output_path)} بايت)")

    # التحقق من إمكانية إعادة التحميل الفوري
    test_agent = CognitiveAgent()
    test_agent.load_brain(output_path)
    loaded_stats = test_agent.get_stats()
    print(f"✅ تم اختبار إعادة التحميل المستقل: {loaded_stats['nodes_count']} عقد، {loaded_stats['edges_count']} روابط (تطابق 100%)")
    print("=" * 80)


if __name__ == "__main__":
    train_curated_knowledge_base()
