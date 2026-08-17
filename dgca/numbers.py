"""
الأعداد والكميات والحساب العلائقي (RFC-01: Numbers, Quantities & Relational Arithmetic).

يوفر الهيكل الجوهري للكميات (quantity:0..9)، وعلاقات التالي (succ) والسابق (pred)،
وقياس القرب الطوبولوجي (sim)، والمقارنة الحتمية بالمسارات دون الحاجة لمعالجات حسابية خارجية.
"""
import math

from .graph import CognitiveGraph, Edge

QUANTITY = "quantity"


def init_quantity_backbone(graph: CognitiveGraph) -> None:
    """تأسيس الهيكل الجوهري الدائم للكميات من 0 إلى 9.

    1. عقد جوهرية: quantity:0 .. quantity:9 مع is_intrinsic=True.
    2. روابط التالي والسابق: succ و pred بأوزان كاملة 1.0 و is_intrinsic=True.
    3. روابط القرب الطوبولوجي: W_sim(n, m) = exp(-0.35 * |n - m|) مع is_intrinsic=True.
    """
    # 1. العقد الجوهرية
    for n in range(10):
        graph.node(f"{QUANTITY}:{n}", QUANTITY, is_intrinsic=True)

    # 2. روابط التالي والسابق
    for n in range(9):
        src_succ = f"{QUANTITY}:{n}"
        dst_succ = f"{QUANTITY}:{n + 1}"
        e_succ = Edge(
            src_succ,
            dst_succ,
            W=1.0,
            kind="succ",
            origin=f"{QUANTITY}→{QUANTITY}",
            t_created=graph.t,
            t_last_update=graph.t,
            is_intrinsic=True,
        )
        graph._link(e_succ)

        src_pred = f"{QUANTITY}:{n + 1}"
        dst_pred = f"{QUANTITY}:{n}"
        e_pred = Edge(
            src_pred,
            dst_pred,
            W=1.0,
            kind="pred",
            origin=f"{QUANTITY}→{QUANTITY}",
            t_created=graph.t,
            t_last_update=graph.t,
            is_intrinsic=True,
        )
        graph._link(e_pred)

    # 3. روابط القرب الطوبولوجي (sim) للأزواج غير المتجاورة مباشرة
    for n in range(10):
        for m in range(10):
            dist = abs(n - m)
            if dist <= 1:
                continue
            w_sim = math.exp(-0.35 * dist)
            e_sim = Edge(
                f"{QUANTITY}:{n}",
                f"{QUANTITY}:{m}",
                W=w_sim,
                kind="sim",
                origin=f"{QUANTITY}→{QUANTITY}",
                t_created=graph.t,
                t_last_update=graph.t,
                is_intrinsic=True,
            )
            graph._link(e_sim)


def compare_quantities(graph: CognitiveGraph, a: int, b: int) -> int:
    """مقارنة حتمية بين كميتين a و b عبر المسار الاتجاهي في الرسم.

    - يعيد -1 إذا كان a < b (عبر تتبع روابط succ).
    - يعيد +1 إذا كان a > b (عبر تتبع روابط pred).
    - يعيد 0 إذا كان a == b.
    """
    if a == b:
        return 0

    src_nid = f"{QUANTITY}:{a}"
    dst_nid = f"{QUANTITY}:{b}"

    # تتبع روابط التالي succ للتحقق مما إذا كان a أصغر من b
    curr = src_nid
    while True:
        succ_edges = [e for e in graph.out_edges(curr) if e.kind == "succ"]
        if not succ_edges:
            break
        curr = succ_edges[0].dst
        if curr == dst_nid:
            return -1

    # تتبع روابط السابق pred للتحقق مما إذا كان a أكبر من b
    curr = src_nid
    while True:
        pred_edges = [e for e in graph.out_edges(curr) if e.kind == "pred"]
        if not pred_edges:
            break
        curr = pred_edges[0].dst
        if curr == dst_nid:
            return 1

    return -1 if a < b else 1
