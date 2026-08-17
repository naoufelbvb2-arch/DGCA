"""
قياس الأداء — ليس اختباراً. يُشغَّل يدوياً: python bench.py [profile]

الغرض: قياس الزمن لكل ملاحظة مقابل حجم الشبكة، لا مقابل عدد الملاحظات.
الشبكة الثابتة الحجم تُخفي التعقيد، الشبكة المتنامية تكشفه.
"""
import cProfile
import io
import pstats
import random
import sys
import time

from dgca.config import AUDIO, TEXT, VISION
from dgca.graph import CognitiveGraph


def build(n_entities, n_obs, seed=11):
    random.seed(seed)
    props = [f"p{i}" for i in range(n_entities * 3)]
    shapes = [f"s{i}" for i in range(n_entities)]
    sounds = [f"a{i}" for i in range(n_entities)]
    ents = {f"e{i}": (random.sample(props, 4), random.choice(shapes), random.choice(sounds))
            for i in range(n_entities)}
    g = CognitiveGraph()
    t0 = time.perf_counter()
    for step in range(n_obs):
        name = random.choice(list(ents))
        pr, sh, so = ents[name]
        signals = [(TEXT, name)] + [(TEXT, p) for p in random.sample(pr, 2)]
        signals.append((VISION, sh))
        signals.append((AUDIO, so))
        g.observe(signals, context=random.choice(["c1", "c2", "c3"]))
        if step % 20 == 19:
            g.observe_sequence([[(TEXT, name)], [(TEXT, "leads")], [(TEXT, pr[0])]],
                               context="seq")
    return g, time.perf_counter() - t0


def scaling(n_obs=600):
    print(f"  {'كيانات':>8} | {'عقد':>7} | {'روابط':>7} | {'ms/ملاحظة':>10} | نمو")
    prev = None
    for n_ent in (20, 40, 80, 160, 320):
        g, dt = build(n_ent, n_obs)
        ms = 1000 * dt / n_obs
        st = g.stats()
        growth = f"x{ms / prev:.2f}" if prev else ""
        print(f"  {n_ent:>8} | {st['nodes']:>7} | {st['edges']:>7} | {ms:>9.2f} | {growth}")
        prev = ms


def profile(n_ent=80, n_obs=400):
    pr = cProfile.Profile()
    pr.enable()
    build(n_ent, n_obs)
    pr.disable()
    out = io.StringIO()
    pstats.Stats(pr, stream=out).sort_stats("tottime").print_stats(12)
    print(out.getvalue())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "profile":
        profile()
    else:
        scaling()
