"""
اختبارات الخطوة 5 — عدم تناظر الدور، والبوابات السياقية، والكبح التنافسي.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import pytest

from dgca.config import TEXT, VISION, Law
from dgca.graph import CognitiveGraph, Edge


def _polysemy():
    """bat: أجنحة في الليل، عصا في الملعب."""
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "bat"), (VISION, "wings")], context="night")
        g.observe([(TEXT, "bat"), (VISION, "stick")], context="stadium")
    return g


# ─────────────────── ق2-ب — عدم تناظر الدور
def test_role_asymmetry_three_tiers():
    """مكان→صفة أقوى من صفة→مكان، وكلاهما أقوى من صفة→صفة."""
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "apple"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
    ent_attr = g.edge("text:apple", "text:sweet").W
    attr_ent = g.edge("text:sweet", "text:apple").W
    attr_attr = g.edge("text:sweet", "text:juicy").W
    assert ent_attr == pytest.approx(0.6913, abs=1e-3)
    assert attr_ent == pytest.approx(0.3867, abs=1e-3)
    assert attr_attr == pytest.approx(0.1786, abs=1e-3)
    assert ent_attr > attr_ent > attr_attr


def test_fwd_flag_marks_only_entity_to_attribute():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "apple"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
    assert g.edge("text:apple", "text:sweet").fwd
    assert g.edge("text:apple", "text:juicy").fwd
    assert not g.edge("text:sweet", "text:apple").fwd
    assert not g.edge("text:sweet", "text:juicy").fwd


def test_head_is_first_signal():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(VISION, "shape"), (TEXT, "name")], context="c")
    assert g.edge("vision:shape", "text:name").fwd
    assert not g.edge("text:name", "vision:shape").fwd


# ─────────────────── ق4 — نشوء البوابة والتناقض تلقائياً
def test_gates_emerge_without_being_told():
    g = _polysemy()
    assert g.edge("text:bat", "vision:wings").g == "night"
    assert g.edge("text:bat", "vision:stick").g == "stadium"


def test_contradiction_registered_both_ways():
    g = _polysemy()
    assert g.X["vision:wings"] == {"vision:stick"}
    assert g.X["vision:stick"] == {"vision:wings"}


def test_shared_context_means_no_rivalry():
    """هدفان من مصدر واحد بسياق مشترك ليسا متنافسين."""
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "apple"), (VISION, "red")], context="kitchen")
        g.observe([(TEXT, "apple"), (VISION, "round")], context="kitchen")
    assert g.edge("text:apple", "vision:red").g is None
    assert g.edge("text:apple", "vision:round").g is None
    assert g.X == {}


def test_co_hyponyms_are_never_rivals():
    """كيانان يتشاركان صفة في سياقين مختلفين — ليسا متناقضين."""
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "apple"), (TEXT, "sweet"), (TEXT, "juicy")], context="market")
        g.observe([(TEXT, "pear"), (TEXT, "sweet"), (TEXT, "juicy")], context="orchard")
    assert g.X == {}, "التنافس بين صفات مكان واحد، لا بين كيانات تشترك في صفة"
    assert all(e.g is None for e in g.edges.values())


def test_reverse_edges_never_generate_rivalry():
    g = _polysemy()
    assert g.edge("vision:wings", "text:bat").g is None
    assert g.edge("vision:stick", "text:bat").g is None


def test_gate_uses_dominant_context():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "bat"), (VISION, "wings")], context="night")
    g.observe([(TEXT, "bat"), (VISION, "wings")], context="cave")
    for _ in range(4):
        g.observe([(TEXT, "bat"), (VISION, "stick")], context="stadium")
    assert g.edge("text:bat", "vision:wings").g == "night"


# ─────────────────── البوابة في الاستدلال
def test_each_context_yields_its_own_meaning():
    g = _polysemy()
    night = g.infer(["text:bat"], context="night")["ranked"]
    stadium = g.infer(["text:bat"], context="stadium")["ranked"]
    assert [n for n, _ in night if n.startswith("vision:")] == ["vision:wings"]
    assert [n for n, _ in stadium if n.startswith("vision:")] == ["vision:stick"]


def test_gated_knowledge_needs_context():
    g = _polysemy()
    ranked = g.infer(["text:bat"])["ranked"]
    assert [n for n, _ in ranked if n.startswith("vision:")] == []


def test_ungated_edges_pass_any_context():
    g = CognitiveGraph()
    for _ in range(4):
        g.observe([(TEXT, "apple"), (VISION, "red")], context="kitchen")
    assert g.edge("text:apple", "vision:red").g is None
    for ctx in (None, "kitchen", "anywhere"):
        assert dict(g.infer(["text:apple"], context=ctx)["ranked"])["vision:red"] > 0


def test_gate_open_semantics():
    e = Edge("a", "b")
    assert e.gate_open(None) and e.gate_open("x")
    e.g = "night"
    assert e.gate_open("night")
    assert not e.gate_open("stadium") and not e.gate_open(None)


# ─────────────────── الكبح التنافسي
def test_mutual_inhibition_suppresses_both_equals():
    g = CognitiveGraph()
    for sym in ("a", "x", "y"):
        g.node(f"text:{sym}", TEXT)
    g._link(Edge("text:a", "text:x", 0.9))
    g._link(Edge("text:a", "text:y", 0.9))
    free = dict(g.infer(["text:a"])["ranked"])
    assert free["text:x"] == pytest.approx(0.393, abs=1e-3)
    g.X = {"text:x": {"text:y"}, "text:y": {"text:x"}}
    fought = dict(g.infer(["text:a"])["ranked"])
    assert fought["text:x"] == pytest.approx(0.049, abs=1e-3)
    assert fought["text:x"] < free["text:x"]


def test_inhibition_lets_the_strong_win_outright():
    g = CognitiveGraph()
    for sym in ("a", "x", "y"):
        g.node(f"text:{sym}", TEXT)
    g._link(Edge("text:a", "text:x", 0.9))
    g._link(Edge("text:a", "text:y", 0.3))
    g.X = {"text:x": {"text:y"}, "text:y": {"text:x"}}
    r = g.infer(["text:a"])
    assert [n for n, _ in r["ranked"]] == ["text:x"]
    assert dict(r["ranked"])["text:x"] == pytest.approx(0.408, abs=1e-3)


def test_no_contradictions_means_no_inhibition():
    g = CognitiveGraph()
    for sym in ("a", "x"):
        g.node(f"text:{sym}", TEXT)
    g._link(Edge("text:a", "text:x", 0.9))
    assert g.X == {}
    assert dict(g.infer(["text:a"])["ranked"])["text:x"] == pytest.approx(0.593, abs=1e-3)


# ─────────────────── التكامل
def test_inference_still_read_only():
    g = _polysemy()
    before = {(a, b): (e.W, e.n, e.g, e.t_last_update) for (a, b), e in g.edges.items()}
    x_before = {k: set(v) for k, v in g.X.items()}
    g.infer(["text:bat"], context="night")
    after = {(a, b): (e.W, e.n, e.g, e.t_last_update) for (a, b), e in g.edges.items()}
    assert after == before and {k: set(v) for k, v in g.X.items()} == x_before


def test_gate_exemption_now_reachable():
    """ق5 يعفي المُبوَّب من شرط تعدد السياقات — البند صار فعّالاً."""
    g = _polysemy()
    e = g.edge("text:bat", "vision:wings")
    assert e.g == "night" and len(e.contexts) == 1
    assert e.W >= Law.THETA_SOLID and e.n >= Law.N_MIN
    assert e.locked, "البوابة تُغني عن تعدد السياقات"


def test_signature_captures_gates():
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    victim = next(iter(g.edges.values()))
    victim.g = "some_context"
    assert behavioral_signature(g) != base
