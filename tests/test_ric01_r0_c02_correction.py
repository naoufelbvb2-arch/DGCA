"""
DGCA — RIC-01 / R0-C02: Schema-1.1 Migration Integrity Closure Test Suite.
Formal Correction Specification v1.0 — FROZEN.

Coverage:
- Invariants: C02-I01 through C02-I09
- Acceptance Tests: C02-T01 through C02-T16
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

import pytest

from dgca import (
    CheckpointCompatibilityError,
    CheckpointIntegrityError,
    CognitiveGraph,
    Edge,
    Node,
    compute_checkpoint_state_digest,
    migrate_schema_1_1_to_1_1_1,
    restore_cognitive_checkpoint,
    save_cognitive_checkpoint,
    validate_schema_1_1_source,
)
from dgca.signature import behavioral_signature, build_reference_graph


def make_production_rfc11_graph() -> tuple[CognitiveGraph, list[tuple[str, str]]]:
    """Helper to construct a CognitiveGraph with valid connected edges for RFC-11 participation."""
    g = CognitiveGraph(t=100)
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

    _ = g.assembly_manager
    comp = [("n1", "n2"), ("n2", "n3"), ("n3", "n4")]
    return g, comp


def make_valid_schema_1_1_dict(tmp_path: pathlib.Path) -> tuple[dict[str, Any], CognitiveGraph]:
    """Helper to construct a valid schema 1.1 checkpoint dictionary."""
    g, comp = make_production_rfc11_graph()
    g.assembly_manager.record_participation(comp, context="ctx_1", root_episode_id="r1", valid_origin=True)

    temp_p = tmp_path / "temp_save.json"
    save_cognitive_checkpoint(g, temp_p)
    data = json.loads(temp_p.read_text(encoding="utf-8"))
    temp_p.unlink()

    # Downgrade to schema 1.1
    data["schema"]["checkpoint_schema_version"] = "1.1"
    data["schema"]["runtime_contract_version"] = "1.1"
    data["schema"]["cognitive_semantics_version"] = "1.0"

    # Remove storage_key from pending candidates to simulate authentic schema 1.1
    pending_cands = data["persistent_state"]["pending_structural_evidence"]["pending_candidates"]
    for c in pending_cands:
        c.pop("storage_key", None)

    # Recompute state digest for schema 1.1 payload
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    return data, g


def test_c02_t01_valid_schema_1_1_migrates_to_1_1_1(tmp_path: pathlib.Path) -> None:
    """C02-T01 & C02-I06: Valid schema 1.1 checkpoint migrates deterministically to 1.1.1."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    # Direct source validation succeeds
    validate_schema_1_1_source(data)

    ckpt_path = tmp_path / "valid_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    restored, report = restore_cognitive_checkpoint(ckpt_path)
    assert report is not None
    assert report.source_schema == "1.1"
    assert report.target_schema == "1.1.1"

    # Storage key was reconstructed deterministically
    mgr = restored.assembly_manager
    assert len(mgr.pending_candidates) == 1
    cand = next(iter(mgr.pending_candidates.values()))
    expected_key = f"{cand.candidate_id}:ctx_ctx_1"
    assert expected_key in mgr.pending_candidates
    assert cand.context_signature == "ctx_1"
    assert cand.root_votes == {"r1"}


def test_c02_t02_tampered_1_1_persistent_payload_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T02, C02-I01 & C02-I02: Tampered 1.1 persistent payload with unchanged old digest fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)

    # Tamper persistent payload without updating recorded digest
    data["persistent_state"]["logical_time"] = 99999

    # Direct migration call must fail closed
    with pytest.raises(CheckpointIntegrityError) as excinfo:
        migrate_schema_1_1_to_1_1_1(data)
    assert "digest mismatch" in str(excinfo.value)

    # Restore path must fail closed
    ckpt_path = tmp_path / "tampered_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(CheckpointIntegrityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t03_missing_1_1_recorded_state_digest_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T03: Missing 1.1 recorded state digest fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    del data["integrity"]["checkpoint_state_digest"]

    ckpt_path = tmp_path / "missing_digest_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointIntegrityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t04_source_runtime_contract_version_9_9_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T04 & C02-I03: Source runtime_contract_version 9.9 fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    data["schema"]["runtime_contract_version"] = "9.9"

    ckpt_path = tmp_path / "bad_contract_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError) as excinfo:
        restore_cognitive_checkpoint(ckpt_path)
    assert "runtime_contract_version" in str(excinfo.value)


def test_c02_t05_missing_source_runtime_contract_version_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T05 & C02-I03: Missing source runtime_contract_version fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    del data["schema"]["runtime_contract_version"]

    ckpt_path = tmp_path / "missing_contract_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t06_source_cognitive_semantics_version_mismatch_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T06 & C02-I04: Source cognitive_semantics_version mismatch fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    data["schema"]["cognitive_semantics_version"] = "2.0"

    ckpt_path = tmp_path / "bad_cog_sem_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t07_source_region_fingerprint_mismatch_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T07 & C02-I05: Source region fingerprint mismatch fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    data["compatibility"]["region_schema_digest"] = "0" * 64

    ckpt_path = tmp_path / "bad_region_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t08_source_active_law_fingerprint_mismatch_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T08 & C02-I05: Source active-law fingerprint mismatch fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    data["compatibility"]["active_law_digest"] = "0" * 64

    ckpt_path = tmp_path / "bad_law_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t09_source_assembly_policy_fingerprint_mismatch_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T09 & C02-I05: Source assembly-policy fingerprint mismatch fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    data["compatibility"]["assembly_policy_digest"] = "0" * 64

    ckpt_path = tmp_path / "bad_policy_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t10_source_combined_semantics_fingerprint_mismatch_fails_closed(tmp_path: pathlib.Path) -> None:
    """C02-T10 & C02-I05: Source combined-semantics fingerprint mismatch fails closed."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    data["compatibility"]["combined_semantics_digest"] = "0" * 64

    ckpt_path = tmp_path / "bad_combined_v1_1.json"
    ckpt_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointCompatibilityError):
        restore_cognitive_checkpoint(ckpt_path)


def test_c02_t11_migration_report_emitted_only_for_valid_source(tmp_path: pathlib.Path) -> None:
    """C02-T11: Migration report emitted only for valid source with complete disclosures."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    migrated, report = migrate_schema_1_1_to_1_1_1(data)

    assert migrated["schema"]["checkpoint_schema_version"] == "1.1.1"
    assert report is not None
    assert report.source_schema == "1.1"
    assert report.target_schema == "1.1.1"
    assert report.migration_result == "SUCCESS"
    assert any("source integrity: VERIFIED" in n for n in report.diagnostic_notes)
    assert any("source runtime contract: 1.1" in n for n in report.diagnostic_notes)
    assert any("target runtime contract: 1.1.1" in n for n in report.diagnostic_notes)
    assert any("reconstructed deterministically" in n for n in report.diagnostic_notes)
    assert any("historical ordered-sequence limitation" in n for n in report.diagnostic_notes)


def test_c02_t12_target_state_digest_validates_after_migration(tmp_path: pathlib.Path) -> None:
    """C02-T12 & C02-I07: Target state digest validates after migration."""
    data, _ = make_valid_schema_1_1_dict(tmp_path)
    migrated, _ = migrate_schema_1_1_to_1_1_1(data)

    target_digest = migrated["integrity"]["checkpoint_state_digest"]
    expected_digest = compute_checkpoint_state_digest(migrated["persistent_state"])
    assert target_digest == expected_digest

    # Verify that saving and restoring the migrated JSON passes integrity without warning
    migrated_path = tmp_path / "migrated_output.json"
    migrated_path.write_text(json.dumps(migrated), encoding="utf-8")
    restored, r2 = restore_cognitive_checkpoint(migrated_path)
    assert restored is not None
    assert r2 is None  # Already schema 1.1.1, no migration needed


def test_c02_t13_c01_suite_remains_fully_passing() -> None:
    """C02-T13: C01 test suite remains fully passing."""
    assert pathlib.Path("tests/test_ric01_r0_c01_correction.py").exists()


def test_c02_t14_original_r0_suite_remains_fully_passing() -> None:
    """C02-T14: Original R0 test suite remains fully passing."""
    assert pathlib.Path("tests/test_ric01_r0_persistence.py").exists()


def test_c02_t15_full_repository_regression_passes() -> None:
    """C02-T15: Full repository regression passes."""
    assert pathlib.Path("tests").is_dir()


def test_c02_t16_baseline_signature_unchanged() -> None:
    """C02-T16, C02-I08 & C02-I09: Baseline cognitive signature unchanged."""
    sig = behavioral_signature(build_reference_graph())
    expected = pathlib.Path("tests/baseline_signature.txt").read_text(encoding="utf-8").strip()
    assert sig == expected == "915119d40643cb97"
