"""
بروتوكول البصمة السلوكية.

الغرض: كشف أي انحراف سلوكي صامت — من نوع ما تلتقطه اختبارات القبول.
سيناريو مرجعي ثابت مكتوب في الكود، وتلخيص حتمي لحالة الشبكة بعده.
"""
import hashlib

from .config import AUDIO, TEXT, VISION
from .graph import CognitiveGraph

_SILENCE_TICKS = 5
_CYCLES = 3

# ثلاثة كيانات تتقاسم أربع صفات وتفترق في اثنتين: التقاسم يكفي لنشوء التماثل
# وللصنف ثلاثةَ أعضاء، والافتراق يكفي لمنع دمج ق10 — فيمتحن الرسم القوانين
# لا تمثيلها وحده.
_SHARED = [(VISION, "red"), (AUDIO, "crunch"), (TEXT, "juicy"), (TEXT, "sweet")]
_ENTITIES = {
    "apple": [(TEXT, "seed"), (TEXT, "stalk")],
    "pear": [(TEXT, "stem"), (TEXT, "pip")],
    "plum": [(TEXT, "stone"), (TEXT, "skin")],
}
SCENARIO = [
    ([(TEXT, name)] + _SHARED + own, ctx)
    for ctx in ("kitchen", "garden")
    for name, own in _ENTITIES.items()
]

# تتابع مرتّب: يمتحن ق11 — الأدوار الموضعية وعقدة الحدث والفارق الموضعي
SEQUENCE = [[(TEXT, "hand")], [(TEXT, "apple")], [(TEXT, "bite")]]


def build_reference_graph() -> CognitiveGraph:
    """سيناريو ثابت بلا أي عشوائية: تكرار، أنماط متعددة، سياقات، تتابع، ثم صمت."""
    g = CognitiveGraph()
    for _ in range(_CYCLES):
        for signals, ctx in SCENARIO:
            g.observe(signals, context=ctx)
        g.observe_sequence(SEQUENCE, context="kitchen")
    # فترة صمت تشغيلية صامتة (RFC-09: تقدم زمني حيادي)
    for _ in range(_SILENCE_TICKS):
        g.tick()
    return g


def behavioral_signature(g: CognitiveGraph) -> str:
    """16 محرفاً من sha256 لتلخيص حتمي بدقة 9 منازل عشرية.

    حالة القفل جزء من الملخّص: الوزن وحده لا يكشفها، لأن القفل قرار يُشتقّ من
    ثلاثة شروط. وكذلك البوابة ووسم fwd ومجموعات التناقض، ومنفعة المفهوم وأعضاؤه
    ورأسه، وبروز الرابط ووسمه وقطبيته وفارقه الموضعي ووجدان العقدة — وإلا مرّ
    الانحراف في منطق البوابات أو الدمج أو السعة أو البروز أو الترتيب صامتاً.
    """
    rows = [
        f"E|{e.src}|{e.dst}|{e.W:.9f}|{e.kind}|{e.n}"
        f"|{','.join(sorted(e.contexts))}|{int(e.locked)}|{e.g or ''}|{int(e.fwd)}"
        f"|{e.S:.9f}|{int(e.tagged)}|{e.valence:.9f}|{e.lag:.9f}"
        for e in g.edges.values()
        if not (
            e.src.startswith("schema:")
            or e.dst.startswith("schema:")
            or e.kind == "schema"
        )
    ]
    rows += [
        f"N|{n.nid}|{n.region}|{n.A:.9f}|{n.U:.9f}"
        f"|{','.join(sorted(n.members))}|{n.head or ''}|{n.V:.9f}"
        for n in g.nodes.values()
        if not n.nid.startswith("schema:")
    ]
    rows += [
        f"X|{nid}|{','.join(sorted(rivals))}"
        for nid, rivals in g.X.items()
        if not nid.startswith("schema:")
    ]
    blob = "\n".join(sorted(rows))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
