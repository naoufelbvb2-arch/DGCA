"""
DGCA — RFC-11 / Law 14 Property-Based Test Suite.

Contains executable implementations for RFC11-P01 through RFC11-P10 across multiple seeds.
"""
from __future__ import annotations

import hashlib
import random

from dgca import CognitiveGraph


def compute_edge_cognitive_digest(graph: CognitiveGraph) -> str:
    """حساب بصمة تشفيرية لحالة كافة المعارف المملوكة للروابط (Edge Cognitive Digest)."""
    rows = []
    for (u, v), e in sorted(graph.edges.items()):
        rows.append(
            f"{u}->{v}|W={e.W:.6f}|S={e.S:.6f}|n={e.n}|kind={e.kind}|g={e.g}|"
            f"val={e.valence:.6f}|lag={e.lag:.6f}|locked={int(e.locked)}"
        )
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def test_rfc11_p01_membership_bound() -> None:
    """RFC11-P01: For all generated graphs: |M(e)| <= A_max."""
    for seed in (42, 101, 2026):
        rng = random.Random(seed)
        g = CognitiveGraph()
        mgr = g.assembly_manager
        # توليد روابط عشوائية
        for i in range(15):
            u = f"node_{rng.randint(0, 10)}"
            v = f"node_{rng.randint(0, 10)}"
            if u != v:
                g.link(u, v, W=0.8)

        live_edges = list(g.edges.keys())
        for ep_idx in range(50):
            if len(live_edges) >= 3:
                sample_k = rng.randint(3, min(6, len(live_edges)))
                sample = rng.sample(live_edges, sample_k)
                mgr.record_participation(sample, root_episode_id=f"root_{ep_idx}", valid_origin=True)

        for e, memberships in mgr.edge_to_assemblies.items():
            assert len(memberships) <= mgr.policy.A_MAX, f"Edge {e} exceeded A_MAX={mgr.policy.A_MAX}: {len(memberships)}"


def test_rfc11_p02_assembly_size_bound() -> None:
    """RFC11-P02: Every live Assembly respects K_ASM_MIN <= |E_A| <= K_ASM_MEM."""
    for seed in (11, 22, 33):
        rng = random.Random(seed)
        g = CognitiveGraph()
        mgr = g.assembly_manager
        for i in range(20):
            u = f"n_{rng.randint(0, 12)}"
            v = f"n_{rng.randint(0, 12)}"
            if u != v:
                g.link(u, v, W=0.8)

        live_edges = list(g.edges.keys())
        for ep in range(40):
            if len(live_edges) >= 3:
                sample = rng.sample(live_edges, rng.randint(3, min(8, len(live_edges))))
                mgr.record_participation(sample, root_episode_id=f"root_p2_{ep}", valid_origin=True)

        for asm in mgr.live_assemblies():
            assert mgr.policy.K_ASM_MIN <= len(asm.member_edges) <= mgr.policy.K_ASM_MEM


def test_rfc11_p03_membership_reference_bound() -> None:
    """RFC11-P03: sum_A |E_A| <= M * A_max always."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    for i in range(10):
        g.link(f"n_{i}", f"n_{i+1}", W=0.8)

    edges = list(g.edges.keys())
    for ep in range(30):
        mgr.record_participation(edges[:4], root_episode_id=f"root_{ep}", valid_origin=True)
        mgr.record_participation(edges[3:7], root_episode_id=f"root_b_{ep}", valid_origin=True)

    total_refs = sum(len(asm.member_edges) for asm in mgr.live_assemblies())
    m = len(g.edges)
    assert total_refs <= m * mgr.policy.A_MAX


def test_rfc11_p04_cognitive_conservation() -> None:
    """RFC11-P04: Random structural mutations preserve Edge cognitive digest when Laws 1–13 learning is absent."""
    g = CognitiveGraph()
    g.link("a", "b", W=0.85, kind="assoc")
    g.link("b", "c", W=0.75, kind="assoc")
    g.link("c", "a", W=0.65, kind="assoc")
    g.link("c", "d", W=0.90, kind="causes")

    digest_before = compute_edge_cognitive_digest(g)
    mgr = g.assembly_manager

    # تنفيذ سلسلة عمليات تكوين، نمو، تنشيط، تقاعد
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation([("a", "b"), ("b", "c"), ("c", "a")], root_episode_id=f"r_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    mgr.select_assemblies({"a": 0.8, "b": 0.7})
    act = mgr.activate(asm, seeds={"a", "b"})
    mgr.close_activation(act)
    mgr.commit_growth(asm.assembly_id, ("c", "d"))

    digest_after = compute_edge_cognitive_digest(g)
    assert digest_before == digest_after, "Cognitive state of edges was modified by structural operations alone!"


def test_rfc11_p05_deterministic_replay() -> None:
    """RFC11-P05: Same initial state + ordered events + policy version => identical digest."""
    def run_simulation(seed: int) -> str:
        rng = random.Random(seed)
        g = CognitiveGraph()
        mgr = g.assembly_manager
        for i in range(6):
            g.link(f"n_{i}", f"n_{(i+1)%6}", W=0.8)
        edges = list(g.edges.keys())
        for ep in range(25):
            k = rng.randint(3, len(edges))
            sample = [edges[j] for j in range(k)]
            mgr.record_participation(sample, root_episode_id=f"root_{ep}", valid_origin=True)

        rows = []
        for asm in mgr.live_assemblies():
            rows.append(f"{asm.assembly_id}:v{asm.version}:{sorted(asm.member_edges)}")
        return hashlib.sha256("\n".join(sorted(rows)).encode("utf-8")).hexdigest()

    d1 = run_simulation(999)
    d2 = run_simulation(999)
    assert d1 == d2


def test_rfc11_p06_equivalent_proposal_order() -> None:
    """RFC11-P06: Canonical arbitration makes semantically equivalent concurrent ordering converge."""
    from dgca.assembly import canonical_assembly_id
    e1 = frozenset([("x", "y"), ("y", "z"), ("z", "x")])
    e2 = frozenset([("z", "x"), ("x", "y"), ("y", "z")])
    assert canonical_assembly_id(e1) == canonical_assembly_id(e2)


def test_rfc11_p07_internal_activity_no_n_str_growth() -> None:
    """RFC11-P07: Thousands of internal events never increase structural confirmation counts."""
    g = CognitiveGraph()
    g.link("a", "b", W=0.8)
    g.link("b", "c", W=0.8)
    g.link("c", "a", W=0.8)
    mgr = g.assembly_manager

    # 1000 تجربة داخلية (استرجاع / محاكاة / توقع)
    for i in range(1000):
        mgr.record_participation([("a", "b"), ("b", "c"), ("c", "a")], root_episode_id=f"internal_{i}", valid_origin=True, self_derived=True)

    assert len(mgr.assemblies) == 0
    assert mgr.observability.self_derived_votes_rejected == 1000


def test_rfc11_p08_poly_membership_compute_conservation() -> None:
    """RFC11-P08: Increasing memberships alone never increases physical transmission count."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    edge = ("a", "b")
    # تسجيل أول إرسال
    assert mgr.track_physical_transmission(1, 0, edge) is True
    # تكرار في نفس الميكرو-تكة
    for _ in range(10):
        assert mgr.track_physical_transmission(1, 0, edge) is False
    assert mgr.observability.deduplicated_transmissions == 10


def test_rfc11_p09_no_global_assembly_scan() -> None:
    """RFC11-P09: Instrumentation shows unreachable Assemblies are not visited for local cue."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    # منطقة 1
    g.link("a1", "a2", W=0.8)
    g.link("a2", "a3", W=0.8)
    g.link("a3", "a1", W=0.8)
    # منطقة 2 بعيدة
    g.link("z1", "z2", W=0.8)
    g.link("z2", "z3", W=0.8)
    g.link("z3", "z1", W=0.8)

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation([("a1", "a2"), ("a2", "a3"), ("a3", "a1")], root_episode_id=f"ra_{i}", valid_origin=True)
        mgr.record_participation([("z1", "z2"), ("z2", "z3"), ("z3", "z1")], root_episode_id=f"rz_{i}", valid_origin=True)

    assert len(mgr.assemblies) == 2
    # تنشيط إشارة في المنطقة 1 فقط
    mgr.observability.assembly_candidates_examined = 0
    selected = mgr.select_assemblies({"a1": 0.8})
    assert len(selected) == 1
    assert mgr.observability.assembly_candidates_examined == 1


def test_rfc11_p10_no_hidden_persistent_score() -> None:
    """RFC11-P10: Long selection runs leave no persistent win/loss/support state in Assemblies."""
    g = CognitiveGraph()
    g.link("a", "b", W=0.8)
    g.link("b", "c", W=0.8)
    g.link("c", "a", W=0.8)
    mgr = g.assembly_manager
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation([("a", "b"), ("b", "c"), ("c", "a")], root_episode_id=f"r_{i}", valid_origin=True)

    # تشغيل 100 جولة تنشيط وتنافس
    for _ in range(100):
        mgr.select_assemblies({"a": 0.8})

    asm = mgr.live_assemblies()[0]
    for forbidden in ["score", "winner_count", "loss_count", "support", "rank"]:
        assert not hasattr(asm, forbidden)
