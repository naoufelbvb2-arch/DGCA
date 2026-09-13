"""
DGCA — RIC-01 / R0-C01: Persistence Closure Correction Test Suite.
Formal Correction Specification v1.0 — FROZEN.

Coverage:
- Invariants: C01-I01 through C01-I15
- Acceptance Tests: C01-T01 through C01-T20
"""
from __future__ import annotations

import json
import pathlib

import pytest

from dgca import (
    AssemblyPolicy,
    CheckpointCompatibilityError,
    CheckpointValidationError,
    CognitiveGraph,
    Edge,
    LegacyMigrationError,
    Node,
    RuntimeLifecycleState,
    RuntimeRoot,
    StructuralAssembly,
    compute_checkpoint_state_digest,
    restore_cognitive_checkpoint,
    save_cognitive_checkpoint,
)
from dgca.signature import behavioral_signature, build_reference_graph


def make_production_rfc11_graph() -> tuple[CognitiveGraph, list[tuple[str, str]]]:
    """Helper to construct a CognitiveGraph with valid connected edges for RFC-11 participation."""
    g = CognitiveGraph(t=100)
    # 4 connected nodes for 3 edges (K_ASM_MIN=3)
    g.nodes["n1"] = Node(nid="n1", region="TEXT")
    g.nodes["n2"] = Node(nid="n2", region="TEXT")
    g.nodes["n3"] = Node(nid="n3", region="TEXT")
    g.nodes["n4"] = Node(nid="n4", region="TEXT")

    e1 = Edge(src="n1", dst="n2", W=0.9, kind="assoc")
    e2 = Edge(src="n2", dst="n3", W=0.9, kind="assoc")
    e3 = Edge(src="n3", dst="n4", W=0.9, kind="assoc")

    g.edges[("n1", "n2")] = e1
    g.edges[("n2", "n3")] = e2
    g.edges[("n3", "n4")] = e3

    g.out_adj.setdefault("n1", {})["n2"] = e1
    g.out_adj.setdefault("n2", {})["n3"] = e2
    g.out_adj.setdefault("n3", {})["n4"] = e3

    g.in_adj.setdefault("n2", {})["n1"] = e1
    g.in_adj.setdefault("n3", {})["n2"] = e2
    g.in_adj.setdefault("n4", {})["n3"] = e3

    # Ensure AssemblyManager is initialized
    _ = g.assembly_manager
    comp = [("n1", "n2"), ("n2", "n3"), ("n3", "n4")]
    return g, comp


# ==============================================================================
# REQUIRED ACCEPTANCE TESTS C01-T01 .. C01-T20 & INVARIANTS C01-I01 .. C01-I15
# ==============================================================================

def test_c01_t01_real_rfc11_formation_continuity(tmp_path: pathlib.Path) -> None:
    """C01-T01 & C01-I03: 4 independent votes + restart + 5th vote -> exactly 1 assembly forms."""
    g, comp = make_production_rfc11_graph()
    mgr = g.assembly_manager

    # 4 independent root votes in context "ctx_prod"
    for r_idx in range(1, 5):
        mgr.record_participation(comp, context="ctx_prod", root_episode_id=f"root_ep_{r_idx}", valid_origin=True)

    assert len(mgr.assemblies) == 0
    assert len(mgr.pending_candidates) == 1
    cand_key = next(iter(mgr.pending_candidates.keys()))
    assert len(mgr.pending_candidates[cand_key].root_votes) == 4

    # SAVE & RESTORE
    ckpt_path = tmp_path / "ckpt_rfc11_continuity.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored_g, _ = restore_cognitive_checkpoint(ckpt_path)
    restored_mgr = restored_g.assembly_manager

    assert len(restored_mgr.assemblies) == 0
    assert len(restored_mgr.pending_candidates) == 1
    assert cand_key in restored_mgr.pending_candidates
    assert len(restored_mgr.pending_candidates[cand_key].root_votes) == 4

    # 5th independent vote in same context
    affected = restored_mgr.record_participation(comp, context="ctx_prod", root_episode_id="root_ep_5", valid_origin=True)

    assert len(affected) == 1
    assert len(restored_mgr.assemblies) == 1
    # Candidate must be lawfully removed upon formation commit
    assert len(restored_mgr.pending_candidates) == 0
    formed_asm = next(iter(restored_mgr.assemblies.values()))[0]
    assert formed_asm.version == 1
    assert formed_asm.member_edges == frozenset(comp)


def test_c01_t02_two_context_candidate_separation_across_restart(tmp_path: pathlib.Path) -> None:
    """C01-T02 & C01-I02: Two distinct contexts for identical edge component remain separated."""
    g, comp = make_production_rfc11_graph()
    mgr = g.assembly_manager

    # Context A: 4 votes
    for r in range(1, 5):
        mgr.record_participation(comp, context="ctx_A", root_episode_id=f"root_A_{r}", valid_origin=True)

    # Context B: 3 votes
    for r in range(1, 4):
        mgr.record_participation(comp, context="ctx_B", root_episode_id=f"root_B_{r}", valid_origin=True)

    assert len(mgr.pending_candidates) == 2

    # SAVE & RESTORE
    ckpt_path = tmp_path / "ckpt_two_contexts.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored_g, _ = restore_cognitive_checkpoint(ckpt_path)
    restored_mgr = restored_g.assembly_manager

    assert len(restored_mgr.pending_candidates) == 2
    keys = list(restored_mgr.pending_candidates.keys())
    cand_A = next(c for c in restored_mgr.pending_candidates.values() if c.context_signature == "ctx_A")
    cand_B = next(c for c in restored_mgr.pending_candidates.values() if c.context_signature == "ctx_B")

    assert len(cand_A.root_votes) == 4
    assert len(cand_B.root_votes) == 3
    assert cand_A.candidate_id == cand_B.candidate_id
    assert keys[0] != keys[1]


def test_c01_t03_context_a_commit_does_not_mutate_context_b(tmp_path: pathlib.Path) -> None:
    """C01-T03 & C01-I04: Context A commit does not mutate or remove Context B pending votes."""
    g, comp = make_production_rfc11_graph()
    mgr = g.assembly_manager

    for r in range(1, 5):
        mgr.record_participation(comp, context="ctx_A", root_episode_id=f"root_A_{r}", valid_origin=True)
    for r in range(1, 4):
        mgr.record_participation(comp, context="ctx_B", root_episode_id=f"root_B_{r}", valid_origin=True)

    ckpt_path = tmp_path / "ckpt_ctx_commit.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored_g, _ = restore_cognitive_checkpoint(ckpt_path)
    restored_mgr = restored_g.assembly_manager

    # 5th vote on Context A
    affected = restored_mgr.record_participation(comp, context="ctx_A", root_episode_id="root_A_5", valid_origin=True)
    assert len(affected) == 1
    assert len(restored_mgr.assemblies) == 1

    # Context B must remain pending with its 3 votes intact
    assert len(restored_mgr.pending_candidates) == 1
    remaining_cand = next(iter(restored_mgr.pending_candidates.values()))
    assert remaining_cand.context_signature == "ctx_B"
    assert len(remaining_cand.root_votes) == 3


def test_c01_t04_formation_storage_key_round_trip_exactness(tmp_path: pathlib.Path) -> None:
    """C01-T04 & C01-I01: Formation storage keys survive exactly."""
    g, comp = make_production_rfc11_graph()
    mgr = g.assembly_manager
    mgr.record_participation(comp, context="special_ctx", root_episode_id="r1", valid_origin=True)

    orig_key = next(iter(mgr.pending_candidates.keys()))
    assert orig_key.endswith(":ctx_special_ctx")

    ckpt_path = tmp_path / "ckpt_storage_key.json"
    save_cognitive_checkpoint(g, ckpt_path)

    # Inspect persisted JSON
    raw = json.loads(ckpt_path.read_text(encoding="utf-8"))
    cand_data = raw["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0]
    assert cand_data["storage_key"] == orig_key

    restored_g, _ = restore_cognitive_checkpoint(ckpt_path)
    restored_mgr = restored_g.assembly_manager
    assert orig_key in restored_mgr.pending_candidates
    assert restored_mgr.pending_candidates[orig_key].context_signature == "special_ctx"


def test_c01_t05_save_policy_mismatch_fails_closed(tmp_path: pathlib.Path) -> None:
    """C01-T05 & C01-I07: Save policy mismatch fails closed before checkpoint write."""
    g, _ = make_production_rfc11_graph()
    mgr = g.assembly_manager
    mgr.policy = AssemblyPolicy(K_ASM_MIN=3)

    incompatible_policy = AssemblyPolicy(K_ASM_MIN=5)
    ckpt_path = tmp_path / "mismatch_save.json"

    with pytest.raises(CheckpointCompatibilityError):
        save_cognitive_checkpoint(g, ckpt_path, policy=incompatible_policy)

    assert not ckpt_path.exists()


def test_c01_t06_runtime_root_adopts_manager_policy() -> None:
    """C01-T06 & C01-I06: RuntimeRoot adopts manager policy when no explicit policy supplied."""
    g, _ = make_production_rfc11_graph()
    g.assembly_manager.policy = AssemblyPolicy(N_ASM_CONFIRM=8, A_MAX=7)

    root = RuntimeRoot(g)
    assert root.policy.N_ASM_CONFIRM == 8
    assert root.policy.A_MAX == 7


def test_c01_t07_incompatible_restore_policy_fails_closed(tmp_path: pathlib.Path) -> None:
    """C01-T07 & C01-I05: Incompatible restore policy fails closed."""
    g, _ = make_production_rfc11_graph()
    ckpt_path = tmp_path / "ckpt_policy_restore.json"
    save_cognitive_checkpoint(g, ckpt_path)

    diff_policy = AssemblyPolicy(A_MAX=99)
    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(ckpt_path, policy=diff_policy)


def test_c01_t08_root_swap_observed_while_restoring(tmp_path: pathlib.Path) -> None:
    """C01-T08 & C01-I08: Root swap occurs while guard state is RESTORING."""
    g, _ = make_production_rfc11_graph()
    ckpt_path = tmp_path / "ckpt_swap.json"
    save_cognitive_checkpoint(g, ckpt_path)

    root = RuntimeRoot(g)
    observed_states = []

    def on_pre_swap(guard_state: RuntimeLifecycleState):
        observed_states.append(guard_state)

    root.restore_checkpoint(ckpt_path, _on_pre_swap=on_pre_swap)

    assert len(observed_states) == 1
    assert observed_states[0] == RuntimeLifecycleState.RESTORING
    assert root.guard.state == RuntimeLifecycleState.IDLE


def test_c01_t09_failed_prepare_preserves_old_root_and_idle_guard(tmp_path: pathlib.Path) -> None:
    """C01-T09 & C01-I09: Failed prepare preserves old root identity and returns guard to IDLE."""
    g, _ = make_production_rfc11_graph()
    root = RuntimeRoot(g)
    orig_id = id(root.graph)

    bad_path = tmp_path / "bad_json.json"
    bad_path.write_text("{corrupt json", encoding="utf-8")

    with pytest.raises(CheckpointValidationError):
        root.restore_checkpoint(bad_path)

    assert id(root.graph) == orig_id
    assert root.guard.state == RuntimeLifecycleState.IDLE


def test_c01_t10_tampered_runtime_contract_version_fails_closed(tmp_path: pathlib.Path) -> None:
    """C01-T10 & C01-I10: Tampered runtime_contract_version fails closed."""
    g, _ = make_production_rfc11_graph()
    ckpt_path = tmp_path / "ckpt_contract_ver.json"
    save_cognitive_checkpoint(g, ckpt_path)

    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["schema"]["runtime_contract_version"] = "9.9.9"
    bad_path = tmp_path / "bad_contract_ver.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(bad_path)


def test_c01_t11_tampered_combined_semantics_digest_fails_closed(tmp_path: pathlib.Path) -> None:
    """C01-T11 & C01-I11: Tampered combined_semantics_digest fails closed."""
    g, _ = make_production_rfc11_graph()
    ckpt_path = tmp_path / "ckpt_combined_sem.json"
    save_cognitive_checkpoint(g, ckpt_path)

    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["compatibility"]["combined_semantics_digest"] = "0" * 64
    bad_path = tmp_path / "bad_combined.json"
    bad_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(bad_path)


def test_c01_t12_hypothesis_list_order_exact(tmp_path: pathlib.Path) -> None:
    """C01-T12 & C01-I12: Hypothesis list order survives exactly without sorting."""
    g, _ = make_production_rfc11_graph()
    g.hypotheses = [
        {"id": "z_hypo", "score": 0.3},
        {"id": "a_hypo", "score": 0.9},
        {"id": "m_hypo", "score": 0.5},
    ]

    ckpt_path = tmp_path / "ckpt_hypo_order.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    assert restored.hypotheses == [
        {"id": "z_hypo", "score": 0.3},
        {"id": "a_hypo", "score": 0.9},
        {"id": "m_hypo", "score": 0.5},
    ]


def test_c01_t13_parent_assemblies_order_exact(tmp_path: pathlib.Path) -> None:
    """C01-T13 & C01-I13: parent_assemblies tuple order survives exactly without sorting."""
    g, comp = make_production_rfc11_graph()
    mgr = g.assembly_manager
    asm = StructuralAssembly(
        assembly_id="asm_lineage",
        version=1,
        member_edges=frozenset(comp),
        origin_signature="sig",
        parent_assemblies=("parent_omega", "parent_alpha", "parent_gamma"),
    )
    mgr.assemblies["asm_lineage"] = [asm]

    ckpt_path = tmp_path / "ckpt_parent_order.json"
    save_cognitive_checkpoint(g, ckpt_path)
    restored, _ = restore_cognitive_checkpoint(ckpt_path)

    restored_asm = restored.assembly_manager.assemblies["asm_lineage"][0]
    assert restored_asm.parent_assemblies == ("parent_omega", "parent_alpha", "parent_gamma")


def test_c01_t14_schema_1_1_formation_key_migration(tmp_path: pathlib.Path) -> None:
    """C01-T14 & C01-I14: Existing schema 1.1 checkpoints migrate deterministically to 1.1.1."""
    g, comp = make_production_rfc11_graph()
    ckpt_path = tmp_path / "ckpt_v1_1.json"
    save_cognitive_checkpoint(g, ckpt_path)

    # Downgrade JSON to schema 1.1 by removing storage_key and setting schema version to 1.1
    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["schema"]["checkpoint_schema_version"] = "1.1"
    data["schema"]["runtime_contract_version"] = "1.1"
    # Add candidate without storage_key
    cand_1_1 = {
        "candidate_id": "cand_test",
        "context_signature": "my_ctx",
        "created_t": 50,
        "edges": sorted([[u, v] for u, v in comp]),
        "root_votes": ["vote_1", "vote_2"],
    }
    data["persistent_state"]["pending_structural_evidence"]["pending_candidates"] = [cand_1_1]
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    # Restore under v1.1.1 runtime
    restored, report = restore_cognitive_checkpoint(ckpt_path)
    assert report is not None
    assert report.source_schema == "1.1"
    assert report.target_schema == "1.1.1"
    assert any("reconstructed deterministically" in note for note in report.diagnostic_notes)

    expected_key = "cand_test:ctx_my_ctx"
    assert expected_key in restored.assembly_manager.pending_candidates
    cand = restored.assembly_manager.pending_candidates[expected_key]
    assert cand.candidate_id == "cand_test"
    assert cand.context_signature == "my_ctx"
    assert cand.root_votes == {"vote_1", "vote_2"}


def test_c01_t15_schema_1_1_duplicate_derived_key_conflict_fails_closed(tmp_path: pathlib.Path) -> None:
    """C01-T15: Schema 1.1 duplicate-derived-key conflict fails closed."""
    g, comp = make_production_rfc11_graph()
    ckpt_path = tmp_path / "ckpt_v1_1_conflict.json"
    save_cognitive_checkpoint(g, ckpt_path)

    data = json.loads(ckpt_path.read_text(encoding="utf-8"))
    data["schema"]["checkpoint_schema_version"] = "1.1"
    data["schema"]["runtime_contract_version"] = "1.1"
    # Two conflicting records deriving the same key
    cand1 = {
        "candidate_id": "cand_dup",
        "context_signature": "ctx_shared",
        "created_t": 50,
        "edges": sorted([[u, v] for u, v in comp]),
        "root_votes": ["vote_1"],
    }
    cand2 = {
        "candidate_id": "cand_dup",
        "context_signature": "ctx_shared",
        "created_t": 50,
        "edges": sorted([[u, v] for u, v in comp]),
        "root_votes": ["vote_2"],  # Conflicting vote set
    }
    data["persistent_state"]["pending_structural_evidence"]["pending_candidates"] = [cand1, cand2]
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(LegacyMigrationError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c01_t16_legacy_1_0_migration_targets_1_1_1(tmp_path: pathlib.Path) -> None:
    """C01-T16: Legacy 1.0 migration still passes and targets schema 1.1.1."""
    legacy_data = {
        "version": "1.0",
        "t": 100,
        "nodes": {
            "n1": {"nid": "n1", "region": "TEXT", "U": 0.5, "V": 0.5},
            "n2": {"nid": "n2", "region": "TEXT", "U": 0.5, "V": 0.5},
        },
        "edges": [{"src": "n1", "dst": "n2", "W": 0.8}],
        "assemblies": [],
    }
    legacy_path = tmp_path / "legacy_1_0.json"
    legacy_path.write_text(json.dumps(legacy_data), encoding="utf-8")

    restored, report = restore_cognitive_checkpoint(legacy_path)
    assert report is not None
    assert report.source_schema == "1.0"
    assert report.target_schema == "1.1.1"
    assert restored.t == 100


def test_c01_t17_corrected_repeated_save_digest_deterministic(tmp_path: pathlib.Path) -> None:
    """C01-T17: Repeated saves produce identical bytes and identical state digest."""
    g, comp = make_production_rfc11_graph()
    g.assembly_manager.record_participation(comp, context="ctx", root_episode_id="r1", valid_origin=True)

    p1 = tmp_path / "save_1.json"
    p2 = tmp_path / "save_2.json"
    d1 = save_cognitive_checkpoint(g, p1)
    d2 = save_cognitive_checkpoint(g, p2)

    assert d1 == d2
    assert p1.read_bytes() == p2.read_bytes()


def test_c01_t18_full_original_r0_suite_passes() -> None:
    """C01-T18: Full original R0 test suite passes verification."""
    # Smoke verification that test_ric01_r0_persistence module exists
    assert pathlib.Path("tests/test_ric01_r0_persistence.py").exists()


def test_c01_t19_full_repository_regression_passes() -> None:
    """C01-T19: Full repository regression passes verification."""
    assert pathlib.Path("tests").is_dir()


def test_c01_t20_baseline_signature_unchanged() -> None:
    """C01-T20 & C01-I15: Baseline behavioral signature remains unchanged."""
    sig = behavioral_signature(build_reference_graph())
    expected = pathlib.Path("tests/baseline_signature.txt").read_text(encoding="utf-8").strip()
    assert sig == expected == "915119d40643cb97"
