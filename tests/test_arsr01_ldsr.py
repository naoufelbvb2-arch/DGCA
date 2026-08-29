"""
DGCA Phase 2.6 — ARSR01 / LDSR v1.0 Mathematical & Property Test Suite.

Authoritative Specifications:
- DGCA-Phase-2.6-ARSR01-LDSR-Formal-Repair-Specification-v1.0-FROZEN.md
- DGCA-ARSR01-LDSR-Formal-Repair-Specification-Freeze-Review-v1.0.md
"""
import pytest

from dgca.graph import CognitiveGraph, local_differential_specificity_residual


def test_m01_uniform_10_way():
    candidates = {f"text:c{i}" for i in range(10)}
    weights = {f"text:c{i}": 1.0 for i in range(10)}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    assert res == {}


def test_m02_two_of_ten_equal():
    candidates = {f"text:c{i}" for i in range(10)}
    weights = {"text:c0": 2.0, "text:c1": 2.0}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    assert pytest.approx(res["text:c0"], rel=1e-6) == 0.4
    assert pytest.approx(res["text:c1"], rel=1e-6) == 0.4
    assert len(res) == 2


def test_m03_unique_of_ten():
    candidates = {f"text:c{i}" for i in range(10)}
    weights = {"text:c0": 5.0}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    assert pytest.approx(res["text:c0"], rel=1e-6) == 0.9
    assert len(res) == 1


def test_m04_weak_asymmetry_preserved():
    candidates = {"text:c0", "text:c1"}
    weights = {"text:c0": 0.51, "text:c1": 0.49}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    assert pytest.approx(res["text:c0"], rel=1e-6) == 0.01
    assert "text:c1" not in res


def test_m05_uniform_2_way():
    candidates = {"text:c0", "text:c1"}
    weights = {"text:c0": 1.0, "text:c1": 1.0}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    assert res == {}


def test_m06_nq_1():
    candidates = {"text:c0"}
    weights = {"text:c0": 1.0}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    assert res == {}


def test_m07_total_variation_identity():
    candidates = {f"text:c{i}" for i in range(5)}
    weights = {"text:c0": 3.0, "text:c1": 1.0, "text:c2": 2.0}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    Z_f = sum(weights.values())
    rho = {c: weights.get(c, 0.0) / Z_f for c in candidates}
    lhs = sum(res.values())
    rhs = 0.5 * sum(abs(rho[c] - u_Q) for c in candidates)
    assert pytest.approx(lhs, rel=1e-6) == rhs


def test_m08_permutation_invariance():
    candidates = {"text:a", "text:b", "text:c", "text:d"}
    weights = {"text:a": 1.0, "text:b": 3.0, "text:c": 0.0, "text:d": 2.0}
    u_Q = 1.0 / len(candidates)
    res1 = local_differential_specificity_residual(weights, candidates, u_Q)

    # Reordered
    reordered_cands = {"text:d", "text:b", "text:a", "text:c"}
    res2 = local_differential_specificity_residual(weights, reordered_cands, u_Q)
    assert res1 == res2


def test_m09_scale_invariance():
    candidates = {"text:a", "text:b", "text:c"}
    weights1 = {"text:a": 2.0, "text:b": 4.0}
    weights2 = {"text:a": 20.0, "text:b": 40.0}
    u_Q = 1.0 / len(candidates)
    res1 = local_differential_specificity_residual(weights1, candidates, u_Q)
    res2 = local_differential_specificity_residual(weights2, candidates, u_Q)
    assert pytest.approx(res1["text:b"], rel=1e-6) == res2["text:b"]


def test_m10_unsupported_candidate_zero():
    candidates = {"text:a", "text:b", "text:unsupported"}
    weights = {"text:a": 1.0, "text:b": 2.0}
    u_Q = 1.0 / len(candidates)
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    assert "text:unsupported" not in res


def test_m11_no_residual_renormalization():
    candidates = {"text:a", "text:b"}
    weights = {"text:a": 0.51, "text:b": 0.49}
    u_Q = 0.5
    res = local_differential_specificity_residual(weights, candidates, u_Q)
    # Must be 0.01, NOT normalized to 1.0
    assert pytest.approx(res["text:a"], rel=1e-6) == 0.01


def test_m12_zero_graph_mutation_in_query():
    g = CognitiveGraph()
    g.observe([("audio", "aud:band:0"), ("text", "cat")], "ctx1")
    g.observe([("audio", "aud:band:0"), ("text", "dog")], "ctx2")
    nodes_before = set(g.nodes.keys())
    edges_before = {(e.src, e.dst): (e.W, e.n) for e in g.edges.values()}

    _ = g.query_cross_modal([("audio", "aud:band:0")], target_prefix="text:")

    nodes_after = set(g.nodes.keys())
    edges_after = {(e.src, e.dst): (e.W, e.n) for e in g.edges.values()}
    assert nodes_before == nodes_after
    assert edges_before == edges_after

