"""
اختبارات الخطوة 3 — القانونان 5 و6.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import math

import pytest

from dgca.config import TEXT, VISION, Law
from dgca.graph import CognitiveGraph, Edge


def _pair(g, ep="ep1", t=1, a=1.0, b=1.0):
    i = g.node("text:a", TEXT); i.excite(t, a, ep)
    j = g.node("text:b", TEXT); j.excite(t, b, ep)
    return i, j


# ─────────────────── ق5 — التثبيت والحماية
def test_law5_lock_needs_all_three_conditions():
    e = Edge("a", "b", Law.THETA_SOLID)
    e.n = Law.N_MIN
    e.contexts = {"c1", "c2"}
    assert e.locked and e.P == 0

    below_w = Edge("a", "b", Law.THETA_SOLID - 0.01)
    below_w.n = Law.N_MIN; below_w.contexts = {"c1", "c2"}
    assert not below_w.locked and below_w.P == 1

    below_n = Edge("a", "b", Law.THETA_SOLID)
    below_n.n = Law.N_MIN - 1; below_n.contexts = {"c1", "c2"}
    assert not below_n.locked

    below_ctx = Edge("a", "b", Law.THETA_SOLID)
    below_ctx.n = Law.N_MIN; below_ctx.contexts = {"c1"}
    assert not below_ctx.locked


def test_law5_gate_exempts_from_context_requirement():
    e = Edge("a", "b", Law.THETA_SOLID)
    e.n = Law.N_MIN; e.contexts = {"night"}
    assert not e.locked
    e.g = "night"
    assert e.locked


def test_law5_floor_follows_lock():
    e = Edge("a", "b", Law.THETA_SOLID)
    e.n = Law.N_MIN; e.contexts = {"c1", "c2"}
    assert e.W_floor == pytest.approx(Law.THETA_SOLID)
    e.contexts = {"c1"}
    assert e.W_floor == 0.0


def test_law5_locks_on_third_observation_and_freezes():
    """نمطان + سياقان بالتناوب: 0.6400 → 0.8560 → 0.9424 ثم تجمّد."""
    g = CognitiveGraph()
    seen = []
    for k in range(6):
        g.observe([(TEXT, "apple"), (VISION, "red")],
                  context="kitchen" if k % 2 == 0 else "garden")
        e = g.edge("text:apple", "vision:red")
        seen.append((round(e.W, 4), e.n, e.locked))
    assert seen[0][:2] == (0.6400, 1) and not seen[0][2]
    assert seen[1][:2] == (0.8560, 2) and not seen[1][2]
    assert seen[2][:2] == (0.9424, 3) and seen[2][2]
    assert all(s[0] == 0.9424 and s[2] for s in seen[2:])


def test_law5_single_context_never_locks():
    g = CognitiveGraph()
    for _ in range(6):
        g.observe([(TEXT, "unicorn"), (VISION, "horn")], context="story")
    e = g.edge("text:unicorn", "vision:horn")
    assert e.W == pytest.approx(0.9963, abs=1e-3)
    assert e.n == 6 and len(e.contexts) == 1
    assert not e.locked, "الوزن العالي وحده لا يقفل — التحدي السادس"


def test_law5_locked_edge_survives_long_neglect():
    g = CognitiveGraph()
    for k in range(4):
        g.observe([(TEXT, "apple"), (VISION, "red")],
                  context="kitchen" if k % 2 == 0 else "garden")
    for _ in range(200):
        g.t += 1
        g._law3_decay()
    e = g.edge("text:apple", "vision:red")
    assert e is not None and e.W == pytest.approx(Law.THETA_SOLID)


def test_law5_unlocked_edge_dies_in_thirtythree_ticks():
    g = CognitiveGraph()
    for _ in range(3):
        g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert g.edge("text:a", "text:b").W == pytest.approx(0.6913, abs=1e-3)
    ticks = 0
    while g.edge("text:a", "text:b") is not None:
        g.t += 1
        g._law3_decay()
        ticks += 1
        assert ticks < 200
    assert ticks == 33


def test_law5_lock_zeroes_reinforcement():
    g = CognitiveGraph()
    i, j = _pair(g)
    e = g._law1_create(i, j)
    e.W = 0.90; e.n = Law.N_MIN; e.contexts = {"c1", "c2"}
    g._law2_reinforce(e, i, j, 2.0, "c3")
    assert e.W == pytest.approx(0.90), "P_ij = 0 يجب أن يصفّر ΔW"


# ─────────────────── ق6 — البصمة الزمنية والمصدر
def test_law6_valid_origin_blocks_creation_across_episodes():
    g = CognitiveGraph()
    i = g.node("text:a", TEXT); i.excite(1, 1.0, "ep1")
    j = g.node("text:b", TEXT); j.excite(2, 1.0, "ep2")
    assert i.A * j.A >= Law.THETA_CREATION
    assert g._law1_create(i, j) is None


def test_law6_missing_episode_is_invalid():
    g = CognitiveGraph()
    i = g.node("text:a", TEXT); i.excite(1, 1.0, None)
    j = g.node("text:b", TEXT); j.excite(1, 1.0, None)
    assert g._law1_create(i, j) is None


def test_law6_invalid_origin_produces_no_event_at_all():
    """لا وزن، ولا عدّاد، ولا سياق — الحدث لم يقع أصلاً."""
    g = CognitiveGraph()
    i, j = _pair(g)
    e = g._law1_create(i, j)
    before = (e.W, e.n, set(e.contexts), e.t_last_update)
    j.episode = "ep_other"
    g._law2_reinforce(e, i, j, 2.0, "newctx")
    assert (e.W, e.n, set(e.contexts), e.t_last_update) == before


def test_law6_temporal_coherence_factor():
    """ΔW مضروب في e^(-α·|t − t_spawn_i|)."""
    results = {}
    for dt in (0, 2):
        g = CognitiveGraph()
        g.t = 10
        i = g.node("text:a", TEXT); i.excite(10 - dt, 1.0, "ep")
        j = g.node("text:b", TEXT); j.excite(10, 1.0, "ep")
        i.A = 1.0
        e = Edge("text:a", "text:b", Law.W_BASE)
        g._link(e)
        g._law2_reinforce(e, i, j, 1.0, "c")
        results[dt] = e.W - Law.W_BASE
    expected_ratio = math.exp(-Law.ALPHA * 2)
    assert results[2] / results[0] == pytest.approx(expected_ratio, abs=1e-6)


def test_law6_same_episode_gives_full_coherence():
    g = CognitiveGraph()
    g.observe([(TEXT, "a"), (TEXT, "b")], context="c")
    assert g.edge("text:a", "text:b").W == pytest.approx(0.370, abs=1e-3)


def test_law6_residual_activation_no_longer_binds_across_ticks():
    """تصحيح لسلوك الخطوة 2: التزامن الخام لم يعد كافياً."""
    g = CognitiveGraph()
    g.observe([(TEXT, "a")], context="c")
    g.observe([(TEXT, "b")], context="c")
    assert g.edge("text:b", "text:a") is None
    assert g.edge("text:a", "text:b") is None


def test_law6_spurious_pair_never_enters_graph():
    g = CognitiveGraph()
    for _ in range(6):
        g.observe([(TEXT, "apple"), (VISION, "red")], context="kitchen")
    g.observe([(TEXT, "carhorn")], context="street")
    assert g.edge("text:apple", "text:carhorn") is None
    assert g.edge("text:carhorn", "text:apple") is None


# ─────────────────── التكامل
def test_no_orphan_nodes_or_index_drift():
    g = CognitiveGraph()
    syms = ["a", "b", "c", "d"]
    for k in range(40):
        g.observe([(TEXT, syms[k % 4]), (VISION, syms[(k + 1) % 4])],
                  context="c1" if k % 2 == 0 else "c2")
    out, inn = {}, {}
    for (a, b), e in g.edges.items():
        out.setdefault(a, {})[b] = e
        inn.setdefault(b, {})[a] = e
    assert {k: v for k, v in g.out_adj.items() if v} == out
    assert {k: v for k, v in g.in_adj.items() if v} == inn


def test_signature_still_deterministic_and_sensitive():
    from dgca.signature import behavioral_signature, build_reference_graph
    a = build_reference_graph()
    assert behavioral_signature(a) == behavioral_signature(build_reference_graph())
    victim = next(iter(a.edges.values()))
    victim.W += 1e-6
    assert behavioral_signature(a) != behavioral_signature(build_reference_graph())


def test_signature_records_lock_state():
    """البصمة يجب أن تلتقط حالة القفل — وإلا مرّ الحراف صامت."""
    from dgca.signature import behavioral_signature, build_reference_graph
    g = build_reference_graph()
    base = behavioral_signature(g)
    victim = next((e for e in g.edges.values() if e.locked), None)
    assert victim is not None, "السيناريو المرجعي يجب أن يحوي رابطاً مقفلاً"
    victim.contexts = {"only_one"}
    assert not victim.locked
    assert behavioral_signature(g) != base
