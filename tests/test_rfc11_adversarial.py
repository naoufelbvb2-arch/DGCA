"""
DGCA — RFC-11 / Law 14 Adversarial Verification Suite.

Comprehensive security, attack resistance, and constitutional compliance tests.
"""
from __future__ import annotations

from dgca import CognitiveGraph
from dgca.assembly import (
    StructuralAssembly,
    canonical_assembly_id,
)


def test_adversarial_micro_episode_vote_inflation() -> None:
    """Attack 1: Spamming hundreds of micro-episodes from 1 single root event."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    g.link("a", "b", W=0.8)
    g.link("b", "c", W=0.8)
    g.link("c", "a", W=0.8)

    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    for _ in range(500):
        mgr.record_participation(edges, root_episode_id="single_root_attacker", valid_origin=True)

    assert len(mgr.assemblies) == 0, "Vote inflation attack succeeded in forming an assembly from 1 root event!"


def test_adversarial_provenance_laundering() -> None:
    """Attack 2: Attempting to launder self-derived text through serializing/deserializing."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    g.link("a", "b", W=0.8)
    g.link("b", "c", W=0.8)
    g.link("c", "a", W=0.8)

    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    for i in range(10):
        # تظاهر بأن النص مصدره توليد ذاتي
        mgr.record_participation(edges, root_episode_id=f"re_encoded_{i}", valid_origin=True, self_derived=True)

    assert len(mgr.assemblies) == 0
    assert mgr.observability.self_derived_votes_rejected == 10


def test_adversarial_merge_storm_pairwise_mining() -> None:
    """Attack 3: Observing a large union A+B+C must NOT emit pairwise AB, AC, BC merges."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    # أنشئ 3 تجمعات مستقلة
    edges_a = [("a1", "a2"), ("a2", "a3"), ("a3", "a1")]
    edges_b = [("b1", "b2"), ("b2", "b3"), ("b3", "b1")]
    edges_c = [("c1", "c2"), ("c2", "c3"), ("c3", "c1")]
    for u, v in edges_a + edges_b + edges_c:
        g.link(u, v, W=0.8)

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges_a, root_episode_id=f"ra_{i}", valid_origin=True)
        mgr.record_participation(edges_b, root_episode_id=f"rb_{i}", valid_origin=True)
        mgr.record_participation(edges_c, root_episode_id=f"rc_{i}", valid_origin=True)

    assert len(mgr.assemblies) == 3

    # ملاحظة الاتحاد الثلاثي معاً A+B+C
    union_abc = edges_a + edges_b + edges_c
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(union_abc, root_episode_id=f"r_abc_{i}", valid_origin=True)

    # يجب ألا يتم تعدين الدمج الثنائي التبادلي (AB / BC / AC)
    assert len(mgr.assemblies) == 3


def test_adversarial_large_dormant_bias() -> None:
    """Attack 4: Huge dormant assembly competing with small exact assembly on single shared seed."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    # تجمع صغير
    g.link("seed_u", "target_a", W=0.9)
    g.link("target_a", "target_b", W=0.9)
    g.link("target_b", "seed_u", W=0.9)
    edges_small = [("seed_u", "target_a"), ("target_a", "target_b"), ("target_b", "seed_u")]

    # تجمع ضخم
    edges_large = [("seed_u", "target_a"), ("target_a", "target_b"), ("target_b", "seed_u")]
    for i in range(15):
        g.link(f"dormant_{i}", f"dormant_{i+1}", W=0.9)
        edges_large.append((f"dormant_{i}", f"dormant_{i+1}"))
    g.link("target_b", "dormant_0", W=0.9)
    edges_large.append(("target_b", "dormant_0"))

    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges_small, root_episode_id=f"rs_{i}", valid_origin=True)
        mgr.record_participation(edges_large, root_episode_id=f"rl_{i}", valid_origin=True)

    # تنشيط seed_u فقط
    selected = mgr.select_assemblies({"seed_u": 0.8})
    # بفضل التوصيلية المعيارية للبذور (Seed-Normalized Conductance)، كلاهما يملك نفس الدعم على البذرة النشطة
    assert len(selected) > 0
    assert selected[0][1] <= 1.0


def test_adversarial_membership_explosion_bound() -> None:
    """Attack 5: Trying to attach an edge to more than A_max assemblies."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    g.link("center", "hub_x", W=0.8)

    # محاولة إنشاء 10 تجمعات تشترك في نفس الرابط
    for k in range(10):
        g.link(f"leaf_{k}_1", f"leaf_{k}_2", W=0.8)
        g.link("hub_x", f"leaf_{k}_1", W=0.8)
        edges = [("center", "hub_x"), (f"leaf_{k}_1", f"leaf_{k}_2"), ("hub_x", f"leaf_{k}_1")]
        for i in range(mgr.policy.N_ASM_CONFIRM):
            mgr.record_participation(edges, root_episode_id=f"atk_{k}_{i}", valid_origin=True)

    assert len(mgr.edge_to_assemblies[("center", "hub_x")]) <= mgr.policy.A_MAX


def test_adversarial_hash_collision_protection() -> None:
    """Attack 6: Verify collision safety on different edge sets."""
    e1 = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    e2 = frozenset([("x", "y"), ("y", "z"), ("z", "x")])
    assert canonical_assembly_id(e1) != canonical_assembly_id(e2)


def test_adversarial_protected_version_gc_delay() -> None:
    """Attack 7: Trying to delete a retired assembly while an activation is holding a pinned version."""
    g = CognitiveGraph()
    mgr = g.assembly_manager
    g.link("a", "b", W=0.8)
    g.link("b", "c", W=0.8)
    g.link("c", "a", W=0.8)
    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    for i in range(mgr.policy.N_ASM_CONFIRM):
        mgr.record_participation(edges, root_episode_id=f"r_{i}", valid_origin=True)

    asm = mgr.live_assemblies()[0]
    act = mgr.activate(asm, seeds={"a"})

    # إحالة التجمع للتقاعد
    mgr.retire_assembly(asm.assembly_id)
    # لا تزال النسخة محمية
    assert (asm.assembly_id, 1) in mgr.protected_versions

    # إغلاق التنشيط يحرر الحماية
    mgr.close_activation(act)
    assert (asm.assembly_id, 1) not in mgr.protected_versions


def test_adversarial_forbidden_cognitive_fields_guard() -> None:
    """Attack 8: Attempting to inject forbidden cognitive scalar into StructuralAssembly."""
    edges = frozenset([("a", "b"), ("b", "c"), ("c", "a")])
    asm = StructuralAssembly("test", 1, edges, "sig")
    assert not hasattr(asm, "confidence")
    assert not hasattr(asm, "salience")
    assert not hasattr(asm, "weight")
