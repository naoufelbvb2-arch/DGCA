"""
اختبارات الخطوة 6 — المفاهيم المجردة، ودمج المركز، وسقف السعة.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import random

import pytest

from dgca.config import AUDIO, HUB, TEXT, VISION, Law
from dgca.graph import CognitiveGraph


def _hubs(g):
    """مفاهيم الكيانات وحدها — عقد الأصناف (cat:) تجريد آخر."""
    return sorted(n.nid for n in g.nodes.values() if n.nid.startswith("hub:"))


def _apple(n=4):
    g = CognitiveGraph()
    for k in range(n):
        g.observe([(TEXT, "apple"), (VISION, "red"), (AUDIO, "crunch")],
                  context="kitchen" if k % 2 == 0 else "garden")
    return g


def _stress(n_ent=25, n_obs=600, seed=7):
    random.seed(seed)
    props = [f"p{i}" for i in range(30)]
    shapes = [f"s{i}" for i in range(12)]
    sounds = [f"a{i}" for i in range(10)]
    ents = {f"e{i}": (random.sample(props, 3), random.choice(shapes), random.choice(sounds))
            for i in range(n_ent)}
    g = CognitiveGraph()
    curve = {}
    for step in range(1, n_obs + 1):
        name = random.choice(list(ents))
        pr, sh, so = ents[name]
        sig = [(TEXT, name)] + [(TEXT, p) for p in random.sample(pr, 2)]
        if random.random() < 0.8:
            sig.append((VISION, sh))
        if random.random() < 0.5:
            sig.append((AUDIO, so))
        g.observe(sig, context=random.choice(["c1", "c2", "c3"]))
        if step % 150 == 0:
            curve[step] = len(_hubs(g))
    return g, curve


# ─────────────────── ولادة المفهوم
def test_concept_needs_two_modalities():
    g = CognitiveGraph()
    for _ in range(5):
        g.observe([(TEXT, "apple"), (TEXT, "sweet")], context="kitchen")
    assert _hubs(g) == []


def test_concept_needs_repetition():
    g = _apple(n=1)
    assert _hubs(g) == []
    g2 = _apple(n=2)
    assert _hubs(g2) == ["hub:apple"]


def test_concept_is_named_after_the_entity():
    g = _apple()
    c = g.nodes["hub:apple"]
    assert c.is_concept and c.region == HUB and c.head == "text:apple"


def test_concept_gathers_its_members():
    g = _apple()
    assert g.nodes["hub:apple"].members == {"text:apple", "vision:red", "audio:crunch"}


def test_concept_is_wired_both_ways():
    g = _apple()
    assert g.edge("hub:apple", "vision:red").W == pytest.approx(0.9991, abs=1e-3)
    assert g.edge("text:apple", "hub:apple").W == pytest.approx(0.9991, abs=1e-3)
    for m in ("text:apple", "vision:red", "audio:crunch"):
        assert g.edge(m, "hub:apple") is not None
        assert g.edge("hub:apple", m) is not None


def test_identity_is_the_entity_not_the_combination():
    """ثلاث تركيبات مختلفة عن الكلب ⟵ مفهوم واحد يتّسع."""
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "dog"), (VISION, "furry"), (AUDIO, "bark")], context="park")
        g.observe([(TEXT, "dog"), (VISION, "brown"), (AUDIO, "bark")], context="home")
        g.observe([(TEXT, "dog"), (VISION, "furry"), (TEXT, "loyal")], context="park")
    assert _hubs(g) == ["hub:dog"]
    assert g.nodes["hub:dog"].members == {
        "text:dog", "text:loyal", "vision:furry", "vision:brown", "audio:bark"}


def test_utility_accumulates_and_decays():
    g = _apple()
    assert g.nodes["hub:apple"].U > 0
    before = g.nodes["hub:apple"].U
    for _ in range(50):
        g.t += 1
        g._law3_decay()
    assert g.nodes["hub:apple"].U < before


def test_members_are_capped():
    g = CognitiveGraph()
    for k in range(12):
        g.observe([(TEXT, "thing"), (VISION, f"v{k}"), (AUDIO, f"a{k}")], context="c")
    assert len(g.nodes["hub:thing"].members) <= Law.K_MEMBERS


# ─────────────────── الدمج
def test_identical_cores_merge():
    """اسمان لشيء واحد: النواة متطابقة فيندمجان."""
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "cat"), (VISION, "whiskers"), (AUDIO, "meow")], context="home")
        g.observe([(TEXT, "kitty"), (VISION, "whiskers"), (AUDIO, "meow")], context="home")
    assert len(_hubs(g)) == 1
    survivor = g.nodes[_hubs(g)[0]]
    assert {"text:cat", "text:kitty", "vision:whiskers", "audio:meow"} <= survivor.members


def test_distinct_concepts_do_not_merge():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "cat"), (VISION, "whiskers"), (AUDIO, "meow")], context="home")
        g.observe([(TEXT, "car"), (VISION, "wheels"), (AUDIO, "engine")], context="road")
    assert _hubs(g) == ["hub:car", "hub:cat"]


def test_merge_leaves_no_dangling_edges():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "cat"), (VISION, "whiskers"), (AUDIO, "meow")], context="home")
        g.observe([(TEXT, "kitty"), (VISION, "whiskers"), (AUDIO, "meow")], context="home")
    live = set(g.nodes)
    assert all(a in live and b in live for a, b in g.edges)
    out, inn = {}, {}
    for (a, b), e in g.edges.items():
        out.setdefault(a, {})[b] = e
        inn.setdefault(b, {})[a] = e
    assert {k: v for k, v in g.out_adj.items() if v} == out
    assert {k: v for k, v in g.in_adj.items() if v} == inn


def test_no_self_loop_after_merge():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "cat"), (VISION, "whiskers"), (AUDIO, "meow")], context="home")
        g.observe([(TEXT, "kitty"), (VISION, "whiskers"), (AUDIO, "meow")], context="home")
    assert all(a != b for a, b in g.edges)


# ─────────────────── التشبيع والسعة
def test_hub_growth_saturates_at_entity_count():
    g, curve = _stress()
    assert curve == {150: 22, 300: 25, 450: 25, 600: 25}
    assert len(_hubs(g)) == 25


def test_hub_stays_a_minority_of_the_network():
    g, _ = _stress()
    assert len(_hubs(g)) / len(g.nodes) < 0.40


def test_capacity_ceiling_is_enforced():
    old = Law.C_HUB
    Law.C_HUB = 10
    try:
        g, _ = _stress(n_ent=30, n_obs=400, seed=3)
        assert len(_hubs(g)) <= 10
        assert any("prune" in line for line in g.log)
    finally:
        Law.C_HUB = old


def test_capacity_prunes_least_useful_first():
    old = Law.C_HUB
    Law.C_HUB = 3
    try:
        g = CognitiveGraph()
        for k in range(6):
            reps = 6 if k == 0 else 2
            for _ in range(reps):
                g.observe([(TEXT, f"e{k}"), (VISION, f"v{k}"), (AUDIO, f"a{k}")],
                          context="c")
        assert len(_hubs(g)) <= 3
        assert "hub:e0" in _hubs(g), "الأكثر منفعة يبقى"
    finally:
        Law.C_HUB = old


# ─────────────────── لا انحدار
def test_polysemy_survives_the_concept_layer():
    """المفهوم الواحد لمكان متعدد المعاني لا يسرّب بين السياقين."""
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "bat"), (VISION, "wings")], context="night")
        g.observe([(TEXT, "bat"), (VISION, "stick")], context="stadium")
    assert _hubs(g) == ["hub:bat"]
    for ctx, want in (("night", "vision:wings"), ("stadium", "vision:stick")):
        vis = [n for n, _ in g.infer(["text:bat"], context=ctx)["ranked"]
               if n.startswith("vision:")]
        assert vis == [want], f"تسرّب في السياق {ctx}"


def test_concept_edges_are_gated_too():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "bat"), (VISION, "wings")], context="night")
        g.observe([(TEXT, "bat"), (VISION, "stick")], context="stadium")
    assert g.edge("hub:bat", "vision:wings").g == "night"
    assert g.edge("hub:bat", "vision:stick").g == "stadium"


def test_inference_still_read_only():
    g = _apple()
    before = {(a, b): (e.W, e.n, e.g) for (a, b), e in g.edges.items()}
    u_before = {n.nid: n.U for n in g.nodes.values()}
    members_before = {n.nid: set(n.members) for n in g.nodes.values()}
    g.infer(["vision:red"])
    assert {(a, b): (e.W, e.n, e.g) for (a, b), e in g.edges.items()} == before
    assert {n.nid: n.U for n in g.nodes.values()} == u_before
    assert {n.nid: set(n.members) for n in g.nodes.values()} == members_before


def test_signature_captures_concepts():
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    concept = next((n for n in g.nodes.values() if n.region == HUB), None)
    assert concept is not None, "السيناريو المرجعي يجب أن يحوي مفهوماً"
    concept.members = concept.members | {"text:intruder"}
    assert behavioral_signature(g) != base
