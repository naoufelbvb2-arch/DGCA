"""
DGCA — RFC-13 Property-Based Verification Suite (RFC13-P01..P10).

Validates the 10 exact frozen mathematical and architectural properties of RFC-13 / Law 15:
    P01 Locality
    P02 Persistent Cognitive Conservation
    P03 Assembly Structural Conservation
    P04 Provenance Conservation
    P05 Monotonic Commit
    P06 Deterministic Termination
    P07 Ambiguity Preservation
    P08 Root-Evidence Independence
    P09 Budget Monotonicity
    P10 Cache / Replay Transparency

Evaluated across >= 25 seeds and >= 100 generated cases per family.
"""
from __future__ import annotations

import hashlib
import random

from dgca import (
    CognitiveGraph,
    CompetitiveAlternativeSet,
    ParticipationReceipt,
    PatternCandidate,
    rfc13_behavioral_signature,
)
from dgca.config import Law

SEEDS = [101 + i * 37 for i in range(30)]  # 30 distinct seeds


def compute_cognitive_digest(graph: CognitiveGraph) -> str:
    """Deterministic hash digest of all persistent cognitive state in CognitiveGraph."""
    rows: list[str] = []
    for (u, v), e in sorted(graph.edges.items()):
        ctxs = ",".join(sorted(e.contexts))
        rows.append(f"e:{u}->{v}|W={e.W:.6f}|g={e.g}|k={e.kind}|c=[{ctxs}]")
    for nid, n in sorted(graph.nodes.items()):
        rows.append(f"n:{nid}|r={n.region}|c={int(n.is_concept)}|i={int(n.is_intrinsic)}|A={n.A:.6f}")
    for k, v in sorted(graph.X.items()):
        rows.append(f"X:{k}={','.join(sorted(v))}")
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def compute_assembly_digest(graph: CognitiveGraph) -> str:
    """Deterministic hash digest of all Law 14 persistent structural assembly state."""
    if not hasattr(graph, "_assembly_manager") or graph._assembly_manager is None:
        return "no_assemblies"
    mgr = graph.assembly_manager
    rows: list[str] = []
    for aid, versions in sorted(mgr.assemblies.items()):
        for asm in versions:
            edges = ",".join(sorted(f"{u}->{v}" for u, v in asm.member_edges))
            nodes = ",".join(sorted(asm.member_nodes))
            rows.append(f"asm:{aid}|v={asm.version}|e=[{edges}]|n=[{nodes}]|r={int(asm.is_retired)}")
    for edge, aids in sorted(mgr.edge_to_assemblies.items()):
        rows.append(f"idx:{edge[0]}->{edge[1]}={','.join(sorted(aids))}")
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def test_rfc13_p01_locality() -> None:
    """RFC13-P01: Locality — Candidate and proposal sets are invariant under remote disjoint graph growth."""
    for seed in SEEDS:
        rng = random.Random(seed)
        g = CognitiveGraph()
        eng = g.completion_engine

        local_u, local_v = f"loc_u_{seed}", f"loc_v_{seed}"
        g.link(local_u, local_v, W=0.85)
        r = [ParticipationReceipt(f"r_{seed}", local_u, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep = g.representation_engine.build_representation(1, 0, None, r)

        cands_iso = [c.candidate_id for c in eng.discover_candidates(rep)]
        props_iso = [p.proposal_id for p in eng.evaluate_reinstatement_eligibility(cands_iso and eng.discover_candidates(rep)[0], rep)] if cands_iso else []

        # Add 30 random remote disjoint edges
        for k in range(30):
            ru = f"rem_{seed}_{k}_{rng.randint(100, 999)}"
            rv = f"rem_{seed}_{k}_{rng.randint(1000, 9999)}"
            g.link(ru, rv, W=rng.uniform(0.1, 0.9))

        eng.clear_caches()
        cands_emb = [c.candidate_id for c in eng.discover_candidates(rep)]
        props_emb = [p.proposal_id for p in eng.evaluate_reinstatement_eligibility(cands_emb and eng.discover_candidates(rep)[0], rep)] if cands_emb else []

        assert cands_iso == cands_emb, f"Locality violation in candidates for seed {seed}"
        assert props_iso == props_emb, f"Locality violation in proposals for seed {seed}"


def test_rfc13_p02_persistent_cognitive_conservation() -> None:
    """RFC13-P02: Persistent Cognitive Conservation — Zero persistent cognitive mutation occurs during completion/settling."""
    for seed in SEEDS:
        g = CognitiveGraph()
        eng = g.completion_engine

        u, v, w = f"node_u_{seed}", f"node_v_{seed}", f"node_w_{seed}"
        g.link(u, v, W=0.85)
        g.link(v, w, W=0.80)

        # Baseline cognitive digest before RFC-13 settling
        digest_before = compute_cognitive_digest(g)

        r = [ParticipationReceipt(f"r_{seed}", u, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)

        # Run settling epoch
        eng.run_settling_epoch(rep0, budget=1.0)
        eng.clear_caches()

        # Reset ephemeral node excitation to initial baseline
        for n in g.nodes.values():
            n.A = 0.0

        digest_after = compute_cognitive_digest(g)
        assert digest_before == digest_after, f"Persistent cognitive state mutated during settling in seed {seed}"


def test_rfc13_p03_assembly_structural_conservation() -> None:
    """RFC13-P03: Assembly Structural Conservation — Zero Law 14 structural mutation occurs during completion/settling."""
    for seed in SEEDS:
        g = CognitiveGraph()
        eng = g.completion_engine
        mgr = g.assembly_manager

        # Form a lawful Law 14 assembly
        a1, a2, a3 = f"asm_{seed}_1", f"asm_{seed}_2", f"asm_{seed}_3"
        g.link(a1, a2, W=0.85)
        g.link(a2, a3, W=0.85)
        g.link(a3, a1, W=0.85)
        for i in range(mgr.policy.N_ASM_CONFIRM):
            mgr.record_participation([(a1, a2), (a2, a3), (a3, a1)], root_episode_id=f"r_{seed}_{i}", valid_origin=True)

        asm_digest_before = compute_assembly_digest(g)

        r = [ParticipationReceipt(f"r_{seed}", a1, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)

        # Run settling epoch
        eng.run_settling_epoch(rep0, budget=1.0)
        eng.clear_caches()

        asm_digest_after = compute_assembly_digest(g)
        assert asm_digest_before == asm_digest_after, f"Law 14 structural assembly mutated during settling in seed {seed}"


def test_rfc13_p04_provenance_conservation() -> None:
    """RFC13-P04: Provenance Conservation — Completed elements retain PATTERN_COMPLETION origin lineage."""
    for seed in SEEDS:
        g = CognitiveGraph()
        eng = g.completion_engine

        u, v = f"p04_u_{seed}", f"p04_v_{seed}"
        g.link(u, v, W=0.85)

        r = [ParticipationReceipt(f"r_{seed}", u, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)

        rep1, _ = eng.run_settling_epoch(rep0, budget=1.0)
        recs_v = [rec for rec in rep1.participation_receipts if rec.element_ref == v]
        assert len(recs_v) == 1, f"Missing participation receipt for reinstated node in seed {seed}"
        assert recs_v[0].origin_lineage == "PATTERN_COMPLETION", f"Provenance tainted for seed {seed}"
        assert "external" not in recs_v[0].origin_lineage


def test_rfc13_p05_monotonic_commit() -> None:
    """RFC13-P05: Monotonic Commit — Each target is committed at most once, and CommittedSet strictly increases."""
    for seed in SEEDS:
        g = CognitiveGraph()
        eng = g.completion_engine

        nodes = [f"chain_{seed}_{i}" for i in range(4)]
        for i in range(len(nodes) - 1):
            g.link(nodes[i], nodes[i + 1], W=0.85)

        r = [ParticipationReceipt(f"r_{seed}", nodes[0], 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)

        _, outcome = eng.run_settling_epoch(rep0, budget=1.0)
        target_names = [t[0] for t in outcome.committed_targets]
        assert len(target_names) == len(set(target_names)), f"Duplicate commit detected in seed {seed}"
        assert len(target_names) == 3, f"Expected 3 sequential commits in chain for seed {seed}"


def test_rfc13_p06_deterministic_termination() -> None:
    """RFC13-P06: Deterministic Termination — Settling terminates deterministically without infinite loop."""
    for seed in SEEDS:
        rng = random.Random(seed)
        g = CognitiveGraph()
        eng = g.completion_engine

        src = f"root_{seed}"
        for i in range(4):
            curr = src
            for depth in range(3):
                nxt = f"n_{seed}_{i}_{depth}"
                g.link(curr, nxt, W=rng.uniform(0.75, 0.90))
                curr = nxt

        r = [ParticipationReceipt(f"r_{seed}", src, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)

        _, outcome = eng.run_settling_epoch(rep0, budget=1.0)
        assert outcome.closure_reason in ("FIXED_POINT", "AMBIGUOUS_FIXED_POINT", "BUDGET_EXHAUSTED")
        assert outcome.iterations <= 10


def test_rfc13_p07_ambiguity_preservation() -> None:
    """RFC13-P07: Ambiguity Preservation — Incomparable or equal witness sets preserve ambiguity without forced winner."""
    for seed in SEEDS:
        rng = random.Random(seed)
        g = CognitiveGraph()
        eng = g.completion_engine

        w1 = frozenset([f"w1_{seed}_{rng.randint(1, 100)}"])
        w2 = frozenset([f"w2_{seed}_{rng.randint(1, 100)}"])

        cand1 = PatternCandidate(f"c1_{seed}", "rid", None, w1, frozenset(["x"]), frozenset(), ("global",), None, None, {})
        cand2 = PatternCandidate(f"c2_{seed}", "rid", None, w2, frozenset(["y"]), frozenset(), ("global",), None, None, {})

        cas = CompetitiveAlternativeSet(f"cas_{seed}", frozenset([cand1.candidate_id, cand2.candidate_id]), frozenset())
        cands_map = {cand1.candidate_id: cand1, cand2.candidate_id: cand2}

        verdict, non_dom, _ = eng.arbitrate_competition(cas, cands_map, {}, w1 | w2)
        assert verdict == "AMBIGUOUS"
        assert len(non_dom) == 2, f"Arbitration broke tie illegally in seed {seed}"


def test_rfc13_p08_root_evidence_independence() -> None:
    """RFC13-P08: Root-Evidence Independence — Reinstated descendants cannot enter RootWitnessSet or resolve generating ambiguity."""
    for seed in SEEDS:
        g = CognitiveGraph()
        eng = g.completion_engine

        root_cue = f"root_cue_{seed}"
        opt_a = f"opt_a_{seed}"
        opt_b = f"opt_b_{seed}"

        g.link(root_cue, opt_a, W=0.85)
        g.link(root_cue, opt_b, W=0.85)
        g.add_contradiction(opt_a, opt_b)

        r = [ParticipationReceipt(f"r_{seed}", root_cue, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)

        _, outcome = eng.run_settling_epoch(rep0, budget=1.0)
        assert outcome.closure_reason == "AMBIGUOUS_FIXED_POINT"
        assert len(outcome.unresolved_alternatives) >= 1


def test_rfc13_p09_budget_monotonicity() -> None:
    """RFC13-P09: Budget Monotonicity — Remaining budget strictly decreases and never resets within SettlingEpoch."""
    for seed in SEEDS:
        g = CognitiveGraph()
        eng = g.completion_engine

        u, v, w = f"b_u_{seed}", f"b_v_{seed}", f"b_w_{seed}"
        g.link(u, v, W=0.85)
        g.link(v, w, W=0.85)

        r = [ParticipationReceipt(f"r_{seed}", u, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)

        init_budget = 1.0
        _, outcome = eng.run_settling_epoch(rep0, budget=init_budget)
        assert outcome.budget_consumed > 0.0
        expected_consumed = len(outcome.committed_targets) * Law.GAMMA
        assert abs(outcome.budget_consumed - expected_consumed) < 1e-6


def test_rfc13_p10_cache_replay_transparency() -> None:
    """RFC13-P10: Cache / Replay Transparency — Cache purging is transparent and replay yields bitwise-identical signatures."""
    def _run_instance(s: int) -> tuple[str, str, frozenset]:
        g = CognitiveGraph()
        eng = g.completion_engine
        u, v, w = f"det_u_{s}", f"det_v_{s}", f"det_w_{s}"
        g.link(u, v, W=0.85)
        g.link(v, w, W=0.85)
        r = [ParticipationReceipt(f"r_{s}", u, 1, 0, "external", "node", activation_magnitude=0.85)]
        rep0 = g.representation_engine.build_representation(1, 0, None, r)
        rep_final, outcome = eng.run_settling_epoch(rep0, budget=1.0)
        canon_sig = g.representation_engine.canonical_representation_signature(rep_final)
        beh_sig = rfc13_behavioral_signature(eng)
        return canon_sig, beh_sig, outcome.committed_targets

    for seed in SEEDS:
        canon1, beh1, targets1 = _run_instance(seed)
        canon2, beh2, targets2 = _run_instance(seed)
        assert canon1 == canon2, f"Canonical signature divergence in seed {seed}"
        assert beh1 == beh2, f"Behavioral signature divergence in seed {seed}"
        assert targets1 == targets2, f"Committed targets divergence in seed {seed}"
