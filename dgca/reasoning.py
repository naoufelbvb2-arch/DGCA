"""
الاستدلال الرنيني العميق والتركيب المتعدي (RFC-03 / Law 7 Extended: Deep Resonant Reasoning & Transitive Composition).

يوفر:
1. الاستدلال الرنيني العميق (deep_infer): كسر حاجز القفزات الخمس بالتآكل الأسي (0.12)
   والشحن الرنيني عند المفاهيم المركزية (recharge boost) حتى 15-20 قفزة،
   وحقل توجيه الجهد نحو الهدف (Target Conductance Field).
2. التركيب المتعدي للعلاقات (compose_relations): استنتاج العلاقات المتعدية وهرميات الأنساب.
3. نمط المحاكاة النقي (mode="simulation"): قراءة خالصة دون أي تعديل في حالة الرسم.
"""
from .config import Law
from .graph import CognitiveGraph

TRANSITIVE_PRIMITIVES = {
    "succ",
    "pred",
    "greater",
    "taller",
    "part_of",
    "subset_of",
    "role:part_of",
    ">",
    "<",
    "ancestor",
    "descendant",
}

SCHEMA_COMPOSITIONS = {
    ("role:parent", "role:parent"): "role:grandparent",
    ("parent", "parent"): "grandparent",
    ("role:child", "role:child"): "role:grandchild",
    ("child", "child"): "grandchild",
    ("role:part_of", "role:part_of"): "role:part_of",
    ("part_of", "part_of"): "part_of",
    ("subset_of", "subset_of"): "subset_of",
    ("succ", "succ"): "greater",
    ("greater", "greater"): "greater",
    ("taller", "taller"): "taller",
    (">", ">"): ">",
    ("<", "<"): "<",
}


def deep_infer(
    graph: CognitiveGraph,
    seeds: list[str],
    context: str | None = None,
    target: str | None = None,
    mode: str = "resonant",
) -> dict:
    """استدلال رنيني عميق يكسر حد الـ 5 قفزات عبر التآكل الأسي وإعادة الشحن عند المعالم المركزية.

    - التآكل الأسي: E(h+1) = E(h) · (1 − γ_decay) · W_eff (حيث γ_decay = 0.12).
    - الشحن الرنيني: عند بلوغ مفهوم مركزي راسخ و E_in ≥ 0.25، يُزاد E_out = min(1.0, E_in + 0.45)، مسقوفاً بـ 3 مرات كحد أقصى لمنع الدوران.
    - حقل الجهد نحو الهدف: W_effective(i → target) = min(1.0, W · 1.40).
    - نمط المحاكاة (simulation): قراءة خالصة ومستقلة 100% دون أي تعديل في الرسم.
    """
    activation = {nid: Law.C_MAX for nid in seeds if nid in graph.nodes}
    visited = set(activation)
    parent: dict[str, str] = {}
    generalized: set[str] = set()
    energy_map: dict[str, float] = {nid: Law.E_BUDGET_0 for nid in seeds}
    recharges_map: dict[str, int] = {nid: 0 for nid in seeds}
    frontier = list(activation)
    trace: list[dict] = []
    hop = 0

    while frontier:
        hop += 1
        incoming: dict[str, float] = {}
        best_capped: dict[str, float] = {}
        next_energy: dict[str, float] = {}
        next_recharges: dict[str, int] = {}
        derived_src: set[str] = set()

        for src in frontier:
            e_src = energy_map.get(src, Law.E_BUDGET_0)
            r_src = recharges_map.get(src, 0)
            raw = {}
            for e in graph.out_edges(src):
                if e.dst in visited or e.dst == parent.get(src):
                    continue
                if not e.gate_open(context):
                    continue
                # عزل توصيل القوالب التجريدية schema:* في أنماط الاستدلال العادي والمحاكاة (RFC-07)
                if mode != "analogical" and (
                    e.dst.startswith("schema:")
                    or src.startswith("schema:")
                    or e.kind == "schema"
                ):
                    continue

                w_eff = e.W
                if target is not None and (e.dst == target or e.dst.endswith(f":{target}")):
                    w_eff = min(1.0, e.W * Law.TARGET_CONDUCTANCE_BOOST)

                # التآكل الأسي لميزانية الطاقة
                e_next = e_src * (1.0 - Law.GAMMA_EXP)

                # الشحن الرنيني عند المفاهيم المركزية
                dst_node = graph.nodes.get(e.dst)
                r_count = r_src
                if (
                    dst_node is not None
                    and (dst_node.is_concept or dst_node.nid.startswith(("hub:", "cat:")))
                    and e_next >= Law.THETA_RECHARGE
                    and r_count < Law.MAX_RECHARGES
                ):
                    e_next = min(1.0, e_next + Law.E_BOOST)
                    r_count += 1

                if e_next <= 0.005:
                    continue

                raw[e.dst] = activation[src] * w_eff * e_next
                if e.kind != "assoc":
                    raw[e.dst] *= Law.DELTA_GEN
                    derived_src.add(e.dst)

            for dst, share in graph._cap_outflow(raw).items():
                if share <= 0.005:
                    continue
                incoming[dst] = incoming.get(dst, 0.0) + share
                if share > best_capped.get(dst, 0.0):
                    best_capped[dst] = share
                    parent[dst] = src
                    next_energy[dst] = e_next
                    next_recharges[dst] = r_count

        activated = []
        for dst, total in incoming.items():
            press = sum(
                max(incoming.get(k, 0.0), activation.get(k, 0.0))
                for k in graph.X.get(dst, ())
            )
            a = min(Law.C_MAX, graph._sigma(total - Law.BETA_INHIBIT * press))
            if a <= 0.005:
                continue
            activation[dst] = a
            visited.add(dst)
            activated.append(dst)
            if dst in derived_src or parent.get(dst) in generalized:
                generalized.add(dst)

        if not activated:
            break

        max_e = round(max((next_energy[dst] for dst in activated if dst in next_energy), default=0.0), 2)
        trace.append({"hop": hop, "E": max_e, "activated": activated})
        frontier = activated
        energy_map = next_energy
        recharges_map = next_recharges

        if hop >= 25:
            break

    ranked = sorted(
        ((nid, round(a, 3)) for nid, a in activation.items() if nid not in seeds),
        key=lambda pair: (-pair[1], pair[0]),
    )
    return {
        "answer": ranked[0][0] if ranked else None,
        "ranked": ranked,
        "hops": len(trace),
        "trace": trace,
        "via_generalization": generalized,
    }


def compose_relations(
    graph: CognitiveGraph,
    a: str,
    r1: str,
    b: str,
    r2: str,
    c: str,
) -> str | None:
    """تركيب العلاقات المتعدية وفق مخططات التعدي الصريح والهرمي.

    - التعدي المباشر: r1 == r2 للعلاقات المتعدية الصريحة (مثل succ, pred, greater, part_of).
    - التركيب الهرمي: مثل (parent, parent) -> grandparent.
    - الرفض الافتراضي: إعادة None للعلاقات غير المتعدية (مثل loves, friend).
    """
    key = (r1, r2)
    if key in SCHEMA_COMPOSITIONS:
        return SCHEMA_COMPOSITIONS[key]

    key_lower = (r1.lower(), r2.lower())
    if key_lower in SCHEMA_COMPOSITIONS:
        return SCHEMA_COMPOSITIONS[key_lower]

    if r1 == r2 and (r1 in TRANSITIVE_PRIMITIVES or r1.lower() in TRANSITIVE_PRIMITIVES):
        return r1

    return None
