"""
سطر الأوامر التفاعلي للوكيل الإدراكي (DGCA Cognitive Agent Interactive REPL CLI).

يوفر واجهة حوارية حية للتفاعل مع الوكيل، تشفير الحواس، الاستدلال الرنيني،
حل التناسب، المقارنة الفطرية للأرقام، وفحص الذاكرة.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import CognitiveAgent

BANNER = r"""
================================================================================
  ██████╗   ██████╗  ██████╗  █████╗      ██████╗ ███████╗██████╗ ██╗     
  ██╔══██╗ ██╔════╝ ██╔════╝ ██╔══██╗     ██╔══██╗██╔════╝██╔══██╗██║     
  ██║  ██║ ██║  ███╗██║      ███████║     ██████╔╝█████╗  ██████╔╝██║     
  ██║  ██║ ██║   ██║██║      ██╔══██║     ██╔══██╗██╔══╝  ██╔═══╝ ██║     
  ██████╔╝ ╚██████╔╝╚██████╗ ██║  ██║     ██║  ██║███████╗██║     ███████╗
  ╚═════╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝
  DGCA Multimodal Cognitive Agent Runtime (RFC-09) · 100% Deterministic AI
================================================================================
Type /help for available commands, /demo to run an automated tour, or /exit to quit.
"""

HELP_TEXT = """
قائمة الأوامر التفاعلية المتاحة:
  /learn <text>          - تلقين معلومة جديدة في الذاكرة المعرفية
  /ask <query>           - إطلاق الاستدلال الرنيني وتوليد إجابة لغوية
  /code <code>           - تشفير كود بايثون وحفظ هيكليته وأدواره البنيوية
  /analogy <a> <b> <c>   - حل لغز التناسب التناظري (a : b :: c : ?)
  /compare <n1> <n2>     - مقارنة عددين عبر العمود الفقري الفطري للأرقام
  /inspect <nid>         - فحص تفصيلي لحالة العقدة، طاقاتها، وروابطها
  /tick [n]              - تمرير n تكة زمنية صامتة لتفعيل التآكل والموت الخلوي
  /stats                 - عرض إحصائيات حية لحجم الذاكرة والمفاهيم والفرضيات
  /save [path]           - حفظ الحالة المعرفية الحالية في ملف JSON
  /load [path]           - تحميل واستعادة شبكة معرفية من ملف JSON
  /demo                  - تشغيل جولة استعراضية تجريبية شاملة لكافة القدرات
  /help                  - عرض هذه القائمة الإرشادية
  /exit أو quit          - إنهاء الجلسة التفاعلية
"""


def run_agent_demo(agent: CognitiveAgent | None = None) -> None:
    """تشغيل سيناريو تجريبي تفاعلي شامل لإثبات قدرات الوكيل."""
    if agent is None:
        agent = CognitiveAgent()

    print("=" * 80)
    print("🚀 بدء الجولة التجريبية الشاملة للوكيل الإدراكي (DGCA Cognitive Agent Demo)")
    print("=" * 80)

    # 1. التعلّم من النصوص
    print("\n[1] تلقين نصوص ومعارف جديدة:")
    print("  • إدخال: 'The sun provides heat to earth'")
    res1 = agent.perceive_text("The sun provides heat to earth")
    print(f"    <- نتيجة الإدخال: {res1}")

    print("  • إدخال: 'Heat causes evaporation of water'")
    res2 = agent.perceive_text("Heat causes evaporation of water")
    print(f"    <- نتيجة الإدخال: {res2}")

    # 2. الاستدلال اللغوي
    print("\n[2] الاستدلال الرنيني وتوليد الإجابة:")
    q1 = "What does sun provide?"
    print(f"  • سؤال: '{q1}'")
    ans1 = agent.query(q1)
    print(f"    <- إجابة الوكيل: '{ans1}'")

    # 3. إدخال الأكواد البرمجية
    print("\n[3] إدخال وفهم الأكواد البرمجية:")
    code_snip = "def add(x, y):\n    return x + y"
    print(f"  • كود بايثون:\n{code_snip}")
    res_code = agent.perceive_code(code_snip, module="math_ops")
    print(f"    <- نتيجة التشفير: {res_code}")

    # 4. حل التناسب والقياس
    print("\n[4] الاستدلال القياسي وحل التناسب:")
    print("  • تهيئة علاقات تناظرية: king -> man, queen -> woman")
    agent.graph.link("text:king", "text:man", W=0.90, kind="role:gender")
    agent.graph.link("text:queen", "text:woman", W=0.90, kind="role:gender")
    print("  • حل التناسب: king : man :: queen : ?")
    res_an = agent.solve_analogy("text:king", "text:man", "text:queen")
    print(f"    <- النظير المستنتج: {res_an['target_match']} (حالة={res_an['status']}, Sim={res_an['similarity']:.3f})")

    # 5. المقارنة الفطرية للأرقام
    print("\n[5] المقارنة الفطرية للأرقام:")
    v1 = agent.compare(9, 4)
    v2 = agent.compare(3, 8)
    print(f"  • مقارنة 9 مع 4: {v1}")
    print(f"  • مقارنة 3 مع 8: {v2}")

    # 6. فحص العقد والتكات الزمنية
    print("\n[6] فحص العقد والإحصائيات والزمن:")
    inspect_res = agent.inspect_node("text:sun")
    print(f"  • فحص العقدة text:sun: {inspect_res}")
    stats_before = agent.get_stats()
    print(f"  • إحصائيات الذاكرة قبل التكات: {stats_before}")
    tick_res = agent.step_time(ticks=3)
    print(f"  • تمرير 3 تكات زمنية: {tick_res}")
    stats_after = agent.get_stats()
    print(f"  • إحصائيات الذاكرة بعد التكات: {stats_after}")

    print("\n" + "=" * 80)
    print("🎉 اكتملت الجولة التجريبية بنجاح تام وبأعلى معايير الدقة والاتساق!")
    print("=" * 80)


def main():
    if "--demo" in sys.argv:
        run_agent_demo()
        return

    print(BANNER)
    agent = CognitiveAgent()

    # فحص خيار تحميل دماغ مسبق
    if "--brain" in sys.argv:
        idx = sys.argv.index("--brain")
        if idx + 1 < len(sys.argv):
            brain_file = sys.argv[idx + 1]
            if os.path.exists(brain_file):
                agent.load_brain(brain_file)
                st = agent.get_stats()
                print(f"🧠 تم تحميل الدماغ المعرفي بنجاح من: {brain_file} ({st['nodes_count']} عقد، {st['edges_count']} روابط)")
            else:
                print(f"⚠️ ملف الدماغ غير موجود: {brain_file}")

    while True:
        try:
            line = input("dgca> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nوداعاً!")
            break

        if not line:
            continue

        if line in {"/exit", "quit", "exit"}:
            print("إنهاء الجلسة الإدراكية.")
            break

        if line == "/help":
            print(HELP_TEXT)
            continue

        if line == "/demo":
            run_agent_demo(agent)
            continue

        if line == "/stats":
            st = agent.get_stats()
            print(f"📊 إحصائيات الذاكرة: {st}")
            continue

        if line.startswith("/learn "):
            text = line[7:].strip()
            res = agent.perceive_text(text)
            print(f"✅ تم التلقين بنجاح ({res['events_created']} أحداث أُضيفت)")
            continue

        if line.startswith("/ask "):
            query = line[5:].strip()
            ans = agent.query(query)
            print(f"💡 {ans if ans else '(لم يتم استخلاص إجابة واثقة)'}")
            continue

        if line.startswith("/code "):
            code_text = line[6:].strip()
            res = agent.perceive_code(code_text)
            print(f"💻 تم تحليل الكود بنجاح ({res['events_created']} أحداث هيكلية)")
            continue

        if line.startswith("/analogy "):
            parts = line.split()[1:]
            if len(parts) != 3:
                print("⚠️ الاستخدام: /analogy <a> <b> <c>")
                continue
            res = agent.solve_analogy(parts[0], parts[1], parts[2])
            print(f"🧩 نتيجة التناسب: {res}")
            continue

        if line.startswith("/compare "):
            parts = line.split()[1:]
            if len(parts) != 2:
                print("⚠️ الاستخدام: /compare <n1> <n2>")
                continue
            try:
                n1, n2 = int(parts[0]), int(parts[1])
                verdict = agent.compare(n1, n2)
                print(f"⚖️ {verdict}")
            except ValueError:
                print("⚠️ يرجى إدخال أعداد صحيحة.")
            continue

        if line.startswith("/inspect "):
            nid = line[9:].strip()
            info = agent.inspect_node(nid)
            print(f"🔍 تفاصيل العقدة:\n{info}")
            continue

        if line.startswith("/tick"):
            parts = line.split()
            ticks = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
            t_res = agent.step_time(ticks)
            print(f"⏱️ تم تمرير {ticks} تكات (تم تقليم {t_res['pruned_nodes']} عقد)")
            continue

        if line.startswith("/save"):
            parts = line.split(maxsplit=1)
            target_path = parts[1].strip() if len(parts) > 1 else "data/brain_state.json"
            try:
                agent.save_brain(target_path)
                st = agent.get_stats()
                print(f"💾 تم حفظ الدماغ بنجاح في: {target_path} ({st['nodes_count']} عقد، {st['edges_count']} روابط)")
            except (OSError, ValueError, TypeError) as ex:
                print(f"❌ تعذر الحفظ: {ex}")
            continue

        if line.startswith("/load"):
            parts = line.split(maxsplit=1)
            target_path = parts[1].strip() if len(parts) > 1 else "data/brain_curated.json"
            if not os.path.exists(target_path):
                print(f"⚠️ الملف غير موجود: {target_path}")
                continue
            try:
                agent.load_brain(target_path)
                st = agent.get_stats()
                print(f"📂 تم تحميل واستعادة الدماغ بنجاح من: {target_path} ({st['nodes_count']} عقد، {st['edges_count']} روابط)")
            except (OSError, ValueError, TypeError) as ex:
                print(f"❌ تعذر التحميل: {ex}")
            continue

        print(f"⚠️ أمر غير معروف: {line}. اكتب /help للاطلاع على الأوامر.")


if __name__ == "__main__":
    main()
