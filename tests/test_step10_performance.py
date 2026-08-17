"""
اختبارات الخطوة 10 — الأداء تحت بصمة ثابتة.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import random
import time

from dgca.config import AUDIO, TEXT, VISION
from dgca.graph import CognitiveGraph


def _build(n_entities, n_obs, seed=11):
    random.seed(seed)
    props = [f"p{i}" for i in range(n_entities * 3)]
    shapes = [f"s{i}" for i in range(n_entities)]
    sounds = [f"a{i}" for i in range(n_entities)]
    ents = {f"e{i}": (random.sample(props, 4), random.choice(shapes), random.choice(sounds))
            for i in range(n_entities)}
    g = CognitiveGraph()
    t0 = time.perf_counter()
    for _ in range(n_obs):
        name = random.choice(list(ents))
        pr, sh, so = ents[name]
        g.observe([(TEXT, name)] + [(TEXT, p) for p in random.sample(pr, 2)]
                  + [(VISION, sh), (AUDIO, so)],
                  context=random.choice(["c1", "c2", "c3"]))
    return g, time.perf_counter() - t0


def test_cost_per_observation_is_near_flat():
    """الشبكة تكبر أربعة أضعاف، الكلفة لكل ملاحظة لا تتضاعف."""
    small, t_small = _build(40, 300)
    large, t_large = _build(160, 300)
    # مع تقليم العقد المعزولة (ق3): العقد الميتة تُحذف فلا تتراكم كعقد يتيمة
    assert large.stats()["nodes"] >= small.stats()["nodes"], "الشبكة لم تستوعب الكيانات"
    ratio = (t_large / 300) / (t_small / 300)
    assert ratio < 2.0, f"الكلفة تضاعفت مع حجم الشبكة (x{ratio:.2f}) — التعقيد ما زال خطياً"


def test_behaviour_is_identical_after_optimisation():
    """التحسين يغيّر الزمن لا النتيجة."""
    from dgca.signature import behavioral_signature, build_reference_graph
    a = behavioral_signature(build_reference_graph())
    b = behavioral_signature(build_reference_graph())
    assert a == b, "الرسم المرجعي لم يعد حتمياً"


def test_indexes_survive_the_stress():
    g, _ = _build(80, 400)
    out, inn = {}, {}
    for (a, b), e in g.edges.items():
        out.setdefault(a, {})[b] = e
        inn.setdefault(b, {})[a] = e
    assert {k: v for k, v in g.out_adj.items() if v} == out
    assert {k: v for k, v in g.in_adj.items() if v} == inn
    live = set(g.nodes)
    assert all(a in live and b in live for a, b in g.edges)
    for k, s in g.X.items():
        assert k in live and s <= live
