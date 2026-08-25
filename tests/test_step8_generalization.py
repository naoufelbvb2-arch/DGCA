"""
اختبارات الخطوة 8 — التعميم والتجريد.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import pytest

from dgca.config import TEXT, VISION, Law
from dgca.graph import CognitiveGraph

FRUITS = {
    "apple": ["sweet", "juicy", "edible", "seed"],
    "mango": ["sweet", "juicy", "edible", "pit"],
    "banana": ["sweet", "soft", "edible", "peel"],
}
ROCK = ["hard", "grey", "inedible", "heavy"]


def _world():
    g = CognitiveGraph()
    for ctx in ("market", "home"):
        for _ in range(3):
            for name, props in FRUITS.items():
                g.observe([(TEXT, name)] + [(TEXT, p) for p in props], context=ctx)
            g.observe([(TEXT, "rock")] + [(TEXT, p) for p in ROCK], context=ctx)
    return g


def _cats(g):
    return sorted(n for n in g.nodes if n.startswith("cat:"))


# ─────────────────── دالة التشابه
def test_similarity_is_asymmetric_containment():
    g = _world()
    for _ in range(2):
        g.observe([(TEXT, "pear"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
    newcomer, _ = g._sim("text:pear", "text:apple")
    veteran, _ = g._sim("text:apple", "text:pear")
    assert newcomer == pytest.approx(1.0, abs=1e-6)
    assert veteran < newcomer, "الوافد يتعلّم من الراسخ، لا العكس"


def test_similarity_needs_two_shared_neighbours():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "car"), (TEXT, "fast"), (TEXT, "metal"), (TEXT, "wheels")],
                  context="road")
        g.observe([(TEXT, "cheetah"), (TEXT, "fast"), (TEXT, "fur"), (TEXT, "legs")],
                  context="road")
    assert g.edge("text:cheetah", "text:car") is None
    assert g.edge("text:car", "text:cheetah") is None


def test_weak_neighbours_do_not_count():
    g = _world()
    assert all(w >= Law.W_SIM_MIN for w in g._neighborhood("text:apple").values())


def test_similarity_is_recalculated_on_touch():
    g = _world()
    sims = [e for e in g.edges.values() if e.kind == "sim"]
    assert sims, "لا بد من نشوء تماثلات"
    before = {(e.src, e.dst): e.W for e in sims}
    for _ in range(50):
        g.tick()
    after = {(a, b): e.W for (a, b), e in g.edges.items() if e.kind == "sim"}
    assert after == before, "المشتقّات تُعاد حسابها ولا تتآكل"


def test_contradictory_nodes_are_never_similar():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "bat"), (VISION, "wings")], context="night")
        g.observe([(TEXT, "bat"), (VISION, "stick")], context="stadium")
    assert g.X.get("vision:wings") == {"vision:stick"}
    assert g.edge("vision:wings", "vision:stick") is None
    assert g.edge("vision:stick", "vision:wings") is None


# ─────────────────── الصنف المجرد
def test_category_emerges_without_being_given():
    g = _world()
    assert _cats(g) == ["cat:text.edible+text.sweet"]
    assert g.nodes["cat:text.edible+text.sweet"].members == {"text:apple", "text:banana", "text:mango"}


def test_rock_is_outside_the_fruit_category():
    g = _world()
    assert all("text:rock" not in g.nodes[c].members for c in _cats(g))


def test_category_needs_three_members():
    g = CognitiveGraph()
    for ctx in ("market", "home"):
        for _ in range(3):
            for name in ("apple", "mango"):
                g.observe([(TEXT, name)] + [(TEXT, p) for p in FRUITS[name]], context=ctx)
    assert _cats(g) == []


# ─────────────────── الاختبار الفاصل
def test_newcomer_inherits_what_it_never_saw():
    """كمّثرى رُئيت مرتين مع sweet و juicy فقط — ولم تُقترن بـ edible قط."""
    g = _world()
    for _ in range(2):
        g.observe([(TEXT, "pear"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
    direct = g.edge("text:pear", "text:edible")
    assert direct is None or direct.kind == "sim", "لا رابط اقتراني مباشر"
    r = g.infer(["text:pear"])
    ranked = dict(r["ranked"])
    assert "text:edible" in ranked
    assert ranked["text:edible"] == pytest.approx(0.139, abs=1e-3)
    assert "text:inedible" not in ranked


def test_inherited_answer_is_marked_as_generalized():
    g = _world()
    for _ in range(2):
        g.observe([(TEXT, "pear"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
    r = g.infer(["text:pear"])
    assert "text:edible" in r["via_generalization"]
    assert "text:sweet" not in r["via_generalization"], "المباشر ليس معمَّماً"


def test_generalization_respects_its_boundary():
    g = _world()
    for _ in range(2):
        g.observe([(TEXT, "pebble"), (TEXT, "hard"), (TEXT, "grey")], context="market")
    ranked = dict(g.infer(["text:pebble"])["ranked"])
    assert "text:inedible" in ranked
    assert "text:edible" not in ranked


def test_transfer_is_attenuated():
    g = _world()
    for _ in range(2):
        g.observe([(TEXT, "pear"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
    ranked = dict(g.infer(["text:pear"])["ranked"])
    assert "text:apple" in ranked and "text:edible" in ranked
    assert Law.DELTA_GEN < 1.0


def test_affective_judgement_of_an_untasted_thing():
    """ق12 × ق9: حكم وجداني على ما لم يُجرَّب قط."""
    g = CognitiveGraph()
    for ctx in ("market", "home"):
        for _ in range(3):
            g.observe([(TEXT, "apple"), (TEXT, "sweet"), (TEXT, "juicy"),
                       (TEXT, "edible")], context=ctx, valence=0.8)
            g.observe([(TEXT, "mango"), (TEXT, "sweet"), (TEXT, "juicy"),
                       (TEXT, "ripe")], context=ctx, valence=0.8)
            g.observe([(TEXT, "berryx"), (TEXT, "bitter"), (TEXT, "pale"),
                       (TEXT, "toxic")], context=ctx, valence=-0.8)
    for _ in range(2):
        g.observe([(TEXT, "pear"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
        g.observe([(TEXT, "berryy"), (TEXT, "bitter"), (TEXT, "pale")], context="market")
    good = g.expected_valence("text:pear")
    bad = g.expected_valence("text:berryy")
    assert good["verdict"] == "good"
    assert bad["verdict"] == "bad"
    assert good["via_generalization"], "الحكم جاء بالتعميم لا بالتجربة"


# ─────────────────── لا انحدار
def test_direct_knowledge_is_not_marked_generalized():
    g = _world()
    r = g.infer(["text:apple"])
    assert "text:sweet" not in r["via_generalization"]


def test_inference_still_read_only():
    g = _world()
    before = {(a, b): (e.W, e.kind, e.n) for (a, b), e in g.edges.items()}
    g.infer(["text:apple"])
    g.expected_valence("text:apple")
    assert {(a, b): (e.W, e.kind, e.n) for (a, b), e in g.edges.items()} == before


def test_indexes_stay_consistent_with_derived_edges():
    g = _world()
    for _ in range(2):
        g.observe([(TEXT, "pear"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
    out, inn = {}, {}
    for (a, b), e in g.edges.items():
        out.setdefault(a, {})[b] = e
        inn.setdefault(b, {})[a] = e
    assert {k: v for k, v in g.out_adj.items() if v} == out
    assert {k: v for k, v in g.in_adj.items() if v} == inn
    live = set(g.nodes)
    assert all(a in live and b in live for a, b in g.edges)


def test_signature_captures_derived_edges():
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    e = next(iter(g.edges.values()))
    e.kind = "sim"
    assert behavioral_signature(g) != base
