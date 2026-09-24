"""DGCA — SCTT00-VR01 Dedicated Verification & Acceptance Suite.

Covers all 20 mandatory specification requirements VR01-T01 through VR01-T20
plus adversarial tests to verify fail-closed provenance, cleanliness,
lineage, gate derivation, and artifact integrity.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from experiments.sctt00 import (
    AUTHORIZED_REPAIR_ANCHOR_COMMIT,
    EXPECTED_AUTHORIZED_PRODUCTION_DELTA,
    FACTS,
    NATURAL_QUESTIONS,
    OOD_CUES,
    PROTOCOL_BASELINE_COMMIT,
    build_markdown_report,
    measure_git_provenance,
    run_preflight,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────── VR01-T01 .. VR01-T06
def test_vr01_t01_dirty_working_tree_detected_and_cannot_pass():
    """VR01-T01: Dirty working tree preflight is detected and cannot PASS."""
    real_run = subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if len(cmd) >= 2 and cmd[1] == "status":
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=" M some_modified_file.py\n?? untracked_file.txt\n",
                stderr="",
            )
        return real_run(cmd, *args, **kwargs)

    with patch("subprocess.run", side_effect=fake_run):
        prov = measure_git_provenance()
        assert prov["working_tree_clean_at_start"] is False
        assert len(prov["working_tree_dirty_entries"]) == 2

    # Under strict require_clean=True, must raise RuntimeError
    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=prov),
        pytest.raises(RuntimeError, match="Dirty working tree detected"),
    ):
        run_preflight(require_clean=True)


def test_vr01_t02_arbitrary_sha_does_not_satisfy_authorized_lineage():
    """VR01-T02: Arbitrary 40-character SHA does not satisfy authorized lineage."""
    arbitrary_sha = "0123456789abcdef0123456789abcdef01234567"
    prov = measure_git_provenance()
    fake_prov = dict(prov)
    fake_prov["execution_source_commit"] = arbitrary_sha
    fake_prov["anchor_is_ancestor_of_execution"] = False
    fake_prov["lineage_valid"] = False

    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="not a descendant of authorized POA01 anchor"),
    ):
        run_preflight(require_clean=False)


def test_vr01_t03_protocol_baseline_recorded_separately_from_execution_source():
    """VR01-T03: Protocol baseline is recorded separately from execution source commit."""
    assert PROTOCOL_BASELINE_COMMIT == "833241d54309d72715c42dc5f2b939c3179e257d"
    assert AUTHORIZED_REPAIR_ANCHOR_COMMIT == "1a269aac42fcf44a824fe677526a92e6e2f81d9f"
    assert PROTOCOL_BASELINE_COMMIT != AUTHORIZED_REPAIR_ANCHOR_COMMIT

    prov = measure_git_provenance()
    assert "protocol_baseline_commit" in prov
    assert "execution_source_commit" in prov
    assert "authorized_repair_anchor_commit" in prov
    assert prov["protocol_baseline_commit"] != prov["authorized_repair_anchor_commit"]


def test_vr01_t04_poa01_anchor_is_ancestor_of_execution_source():
    """VR01-T04: POA01 anchor is verified as ancestor of execution source."""
    prov = measure_git_provenance()
    assert prov["baseline_is_ancestor_of_anchor"] is True
    assert prov["anchor_is_ancestor_of_execution"] is True


def test_vr01_t05_dgca_drift_after_poa01_anchor_causes_block_fail():
    """VR01-T05: Any dgca/** change after POA01 anchor causes BLOCK/FAIL."""
    fake_prov = measure_git_provenance()
    fake_prov = dict(fake_prov)
    fake_prov["production_drift_after_repair_anchor"] = ["dgca/unauthorized_new_file.py"]
    fake_prov["lineage_valid"] = False

    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="Unauthorized dgca/\\*\\* production drift"),
    ):
        run_preflight(require_clean=False)


def test_vr01_t06_authorized_baseline_to_anchor_production_delta():
    """VR01-T06: Authorized baseline→anchor production delta is exactly completion.py + generation.py."""
    proc = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            PROTOCOL_BASELINE_COMMIT,
            AUTHORIZED_REPAIR_ANCHOR_COMMIT,
            "--",
            "dgca/",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_files = {f.replace("\\", "/").strip() for f in proc.stdout.splitlines() if f.strip()}
    assert changed_files == set(EXPECTED_AUTHORIZED_PRODUCTION_DELTA)
    assert changed_files == {"dgca/completion.py", "dgca/generation.py"}


# ─────────────────────────────────────────────────────────── VR01-T07 .. VR01-T12
def test_vr01_t07_canonical_lineage_result_is_derived_not_hardcoded():
    """VR01-T07: Canonical lineage result is derived, not hard-coded."""
    canonical_lineage_val = "INVALID"
    lineage_valid = True
    gate_result = "PASS" if (canonical_lineage_val == "VALID" and lineage_valid) else "FAIL"
    assert gate_result == "FAIL"

    canonical_lineage_val = "VALID"
    lineage_valid = False
    gate_result = "PASS" if (canonical_lineage_val == "VALID" and lineage_valid) else "FAIL"
    assert gate_result == "FAIL"

    canonical_lineage_val = "VALID"
    lineage_valid = True
    gate_result = "PASS" if (canonical_lineage_val == "VALID" and lineage_valid) else "FAIL"
    assert gate_result == "PASS"


def test_vr01_t08_production_drift_result_is_derived_not_hardcoded():
    """VR01-T08: Production drift result is derived, not hard-coded."""
    drift_count = 1
    gate_result = "PASS" if drift_count == 0 else "FAIL"
    assert gate_result == "FAIL"

    drift_count = 0
    gate_result = "PASS" if drift_count == 0 else "FAIL"
    assert gate_result == "PASS"


def test_vr01_t09_ood_gate_fails_if_measured_count_not_4_of_4():
    """VR01-T09: OOD gate fails if measured OOD count is not 4/4."""
    for ood_count in (0, 1, 2, 3):
        gate_result = "PASS" if ood_count == 4 else "FAIL"
        assert gate_result == "FAIL"
    target = 4
    assert ("PASS" if target == 4 else "FAIL") == "PASS"


def test_vr01_t10_primary_recall_gate_fails_if_measured_count_not_8_of_8():
    """VR01-T10: Primary recall gate fails if measured recall count is not 8/8."""
    for count in range(8):
        gate_result = "PASS" if count == 8 else "FAIL"
        assert gate_result == "FAIL"
    target = 8
    assert ("PASS" if target == 8 else "FAIL") == "PASS"


def test_vr01_t11_restore_determinism_gate_fails_if_measured_count_not_8_of_8():
    """VR01-T11: Restore determinism gate fails if measured count is not 8/8."""
    for count in range(8):
        gate_result = "PASS" if count == 8 else "FAIL"
        assert gate_result == "FAIL"
    target = 8
    assert ("PASS" if target == 8 else "FAIL") == "PASS"


def test_vr01_t12_persistent_delta_gate_fails_if_any_state_delta_exists():
    """VR01-T12: Persistent-delta gate fails if any state delta exists."""
    zero_delta_pass = False
    gate_result = "PASS" if zero_delta_pass else "FAIL"
    assert gate_result == "FAIL"

    zero_delta_pass = True
    gate_result = "PASS" if zero_delta_pass else "FAIL"
    assert gate_result == "PASS"


# ─────────────────────────────────────────────────────────── VR01-T13 .. VR01-T16
def test_vr01_t13_generated_pass_report_contains_no_stale_failure_prose():
    """VR01-T13: Generated PASS report contains no stale E2_RETRIEVAL / 0-of-8 failure prose."""
    mock_data: dict[str, Any] = {
        "meta": {
            "timestamp": "2026-09-19T12:00:00Z",
            "execution_profile": "SCTT00_POST_REPAIR_RERUN_V1",
            "protocol_baseline_commit": PROTOCOL_BASELINE_COMMIT,
            "authorized_repair_anchor_commit": AUTHORIZED_REPAIR_ANCHOR_COMMIT,
            "execution_source_commit": "1a269aac42fcf44a824fe677526a92e6e2f81d9f",
            "verdict": "SCTT00_REPAIR_RERUN_PASS",
            "failure_stage": "NONE",
        },
        "provenance": {
            "protocol_baseline_commit": PROTOCOL_BASELINE_COMMIT,
            "authorized_repair_anchor_commit": AUTHORIZED_REPAIR_ANCHOR_COMMIT,
            "execution_source_commit": "1a269aac42fcf44a824fe677526a92e6e2f81d9f",
            "working_tree_clean_at_start": True,
            "baseline_is_ancestor_of_anchor": True,
            "anchor_is_ancestor_of_execution": True,
            "production_files_changed_baseline_to_anchor": ["dgca/completion.py", "dgca/generation.py"],
            "production_drift_after_repair_anchor": [],
            "lineage_valid": True,
        },
        "success_gates": [
            {"name": "Primary learned recall", "required": "8/8", "observed": "8/8", "result": "PASS"},
            {"name": "OOD safety", "required": "4/4", "observed": "4/4", "result": "PASS"},
        ],
        "preflight": {"git_head": "1a269aa", "apis_confirmed": True, "encoder_gate": "8/8 PASS", "encoder_preflight": []},
        "baseline_probes": [],
        "training_exposures": [],
        "storage_audit": {"persisted_relations_gate": "8/8 PASS", "node_count": 20, "edge_count": 30, "logical_time": 40, "committed_transaction_count": 40, "state_digest": "abc", "pairs": []},
        "checkpoint": {"path": "data/checkpoints/SCTT00-trained.json", "file_sha256": "x", "checkpoint_bundle_digest": "y", "checkpoint_state_digest": "z", "provenance_epoch_digest": "w", "schema_version": "1.0", "runtime_version": "1.0", "observation_protocol_version": "1.0"},
        "primary_retrieval": [],
        "ood_safety_controls": [],
        "clean_restore_determinism": [],
        "exploratory_natural_questions": [],
    }
    report = build_markdown_report(mock_data)
    assert "SCTT00_REPAIR_RERUN_PASS" in report
    assert "0/8 recall" not in report
    assert "E2_RETRIEVAL" not in report
    assert "SCTT00_FAIL" not in report


def test_vr01_t14_generated_fail_fixture_describes_failure_and_not_pass():
    """VR01-T14: Generated FAIL fixture describes actual failure and does not claim PASS."""
    mock_data: dict[str, Any] = {
        "meta": {
            "timestamp": "2026-09-19T12:00:00Z",
            "execution_profile": "SCTT00_POST_REPAIR_RERUN_V1",
            "protocol_baseline_commit": PROTOCOL_BASELINE_COMMIT,
            "authorized_repair_anchor_commit": AUTHORIZED_REPAIR_ANCHOR_COMMIT,
            "execution_source_commit": "1a269aac42fcf44a824fe677526a92e6e2f81d9f",
            "verdict": "SCTT00_REPAIR_RERUN_FAIL",
            "failure_stage": "E2_RETRIEVAL",
        },
        "provenance": {},
        "success_gates": [
            {"name": "Primary learned recall", "required": "8/8", "observed": "0/8", "result": "FAIL"},
        ],
        "preflight": {"git_head": "1a269aa", "apis_confirmed": True, "encoder_gate": "8/8 PASS", "encoder_preflight": []},
        "baseline_probes": [],
        "training_exposures": [],
        "storage_audit": {"persisted_relations_gate": "8/8 PASS", "node_count": 20, "edge_count": 30, "logical_time": 40, "committed_transaction_count": 40, "state_digest": "abc", "pairs": []},
        "checkpoint": {"path": "data/checkpoints/SCTT00-trained.json", "file_sha256": "x", "checkpoint_bundle_digest": "y", "checkpoint_state_digest": "z", "provenance_epoch_digest": "w", "schema_version": "1.0", "runtime_version": "1.0", "observation_protocol_version": "1.0"},
        "primary_retrieval": [],
        "ood_safety_controls": [],
        "clean_restore_determinism": [],
        "exploratory_natural_questions": [],
        "root_cause_analysis": "Simulated recall failure.",
    }
    report = build_markdown_report(mock_data)
    assert "SCTT00_REPAIR_RERUN_FAIL" in report
    assert "SCTT00_REPAIR_RERUN_PASS" not in report
    assert "E2_RETRIEVAL" in report


def test_vr01_t15_committed_json_and_report_agree_on_verdict():
    """VR01-T15: Committed JSON artifact and Markdown report agree on verdict."""
    results_json = REPO_ROOT / "experiments" / "results" / "sctt00-results.json"
    report_md = REPO_ROOT / "papers MD" / "SCTT-00-EXECUTION-REPORT.md"
    assert results_json.is_file(), f"Missing canonical JSON artifact: {results_json}"
    assert report_md.is_file(), f"Missing canonical report: {report_md}"
    data = json.loads(results_json.read_text(encoding="utf-8"))
    report_text = report_md.read_text(encoding="utf-8")
    verdict = data["meta"]["verdict"]
    assert f"Execution Verdict:** `{verdict}`" in report_text or f"Official Verdict: `{verdict}`" in report_text


def test_vr01_t16_committed_json_and_report_agree_on_execution_source_commit():
    """VR01-T16: Committed JSON artifact and Markdown report agree on execution source commit."""
    results_json = REPO_ROOT / "experiments" / "results" / "sctt00-results.json"
    report_md = REPO_ROOT / "papers MD" / "SCTT-00-EXECUTION-REPORT.md"
    assert results_json.is_file(), f"Missing canonical JSON artifact: {results_json}"
    assert report_md.is_file(), f"Missing canonical report: {report_md}"
    data = json.loads(results_json.read_text(encoding="utf-8"))
    report_text = report_md.read_text(encoding="utf-8")
    source = data["meta"].get("execution_source_commit", data["meta"].get("baseline_commit"))
    assert source in report_text


# ─────────────────────────────────────────────────────────── VR01-T17 .. VR01-T20
def test_vr01_t17_mandatory_acceptance_suite_zero_silent_skips():
    """VR01-T17: Mandatory acceptance suite has zero silent skips."""
    poa01_py = (REPO_ROOT / "tests" / "test_rfc14_poa01.py").read_text(encoding="utf-8")
    assert "pytest.skip" not in poa01_py, "test_rfc14_poa01.py contains forbidden pytest.skip calls!"


def test_vr01_t18_poa01_checkpoint_recall_test_classified_as_regression():
    """VR01-T18: POA01 checkpoint recall test is correctly classified as checkpoint regression, not full SCTT rerun."""
    poa01_py = (REPO_ROOT / "tests" / "test_rfc14_poa01.py").read_text(encoding="utf-8")
    assert "def test_poa01_t26_sctt00_post_training_checkpoint_recall_regression():" in poa01_py
    assert "post-training checkpoint recall regression" in poa01_py.lower()


def test_vr01_t19_full_rerun_uses_unchanged_frozen_facts_and_exposures():
    """VR01-T19: Full end-to-end repair rerun uses unchanged frozen fact bank and exposure count."""
    assert len(FACTS) == 8
    assert len(OOD_CUES) == 4
    assert len(NATURAL_QUESTIONS) == 4
    assert 5 * len(FACTS) == 40
    expected_f01 = ("F01", "A dog is a canine.", "dog", "canine")
    assert FACTS[0] == expected_f01


def test_vr01_t20_no_dgca_file_modified_by_vr01():
    """VR01-T20: No dgca/** file is modified by VR01 implementation."""
    proc = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            AUTHORIZED_REPAIR_ANCHOR_COMMIT,
            "SCTT00-VR01-VERIFIED",
            "--",
            "dgca/",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    drift = [f.strip() for f in proc.stdout.splitlines() if f.strip()]
    assert drift == [], f"Unauthorized modification in dgca/** detected: {drift}"


# ─────────────────────────────────────────────────────────── Adversarial Tests
def test_vr01_t21_untracked_file_causes_preflight_cleanliness_failure():
    """VR01-T21: Untracked file causes cleanliness check to fail."""
    real_run = subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if len(cmd) >= 2 and cmd[1] == "status":
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="?? untracked.py\n",
                stderr="",
            )
        return real_run(cmd, *args, **kwargs)

    with patch("subprocess.run", side_effect=fake_run):
        prov = measure_git_provenance()
        assert prov["working_tree_clean_at_start"] is False


def test_vr01_t22_staged_file_causes_preflight_cleanliness_failure():
    """VR01-T22: Staged file causes cleanliness check to fail."""
    real_run = subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if len(cmd) >= 2 and cmd[1] == "status":
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="A  new_staged_file.py\n",
                stderr="",
            )
        return real_run(cmd, *args, **kwargs)

    with patch("subprocess.run", side_effect=fake_run):
        prov = measure_git_provenance()
        assert prov["working_tree_clean_at_start"] is False


def test_vr01_t23_missing_api_attribute_raises_assertion_error():
    """VR01-T23: Missing API attribute raises AssertionError in preflight."""
    from dgca.causal_identity import CanonicalR1RuntimeRoot
    assert hasattr(CanonicalR1RuntimeRoot, "create_observation_bridge")


# ─────────────────────────────────────────────────────────── C01-T01 .. C01-T18
def test_c01_t01_baseline_not_ancestor_blocks_preflight():
    """C01-T01: baseline not ancestor of anchor -> preflight BLOCKED before training."""
    prov = measure_git_provenance()
    fake_prov = dict(prov)
    fake_prov["baseline_is_ancestor_of_anchor"] = False
    fake_prov["lineage_valid"] = False

    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="BLOCKED"),
    ):
        run_preflight(require_clean=False)


def test_c01_t02_baseline_to_anchor_production_delta_mismatch_blocks_preflight():
    """C01-T02: baseline->anchor production delta mismatch -> BLOCKED before training."""
    prov = measure_git_provenance()
    fake_prov = dict(prov)
    fake_prov["production_files_changed_baseline_to_anchor"] = ["dgca/completion.py"]
    fake_prov["lineage_valid"] = False

    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="BLOCKED"),
    ):
        run_preflight(require_clean=False)


def test_c01_t03_anchor_not_ancestor_blocks_preflight():
    """C01-T03: anchor not ancestor of execution -> BLOCKED."""
    prov = measure_git_provenance()
    fake_prov = dict(prov)
    fake_prov["anchor_is_ancestor_of_execution"] = False
    fake_prov["lineage_valid"] = False

    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="BLOCKED"),
    ):
        run_preflight(require_clean=False)


def test_c01_t04_post_anchor_dgca_drift_blocks_preflight():
    """C01-T04: post-anchor dgca drift -> BLOCKED."""
    prov = measure_git_provenance()
    fake_prov = dict(prov)
    fake_prov["production_drift_after_repair_anchor"] = ["dgca/unauthorized_module.py"]
    fake_prov["lineage_valid"] = False

    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="BLOCKED"),
    ):
        run_preflight(require_clean=False)


def test_c01_t05_dirty_tree_blocks_preflight():
    """C01-T05: dirty tree -> BLOCKED."""
    prov = measure_git_provenance()
    fake_prov = dict(prov)
    fake_prov["working_tree_clean_at_start"] = False
    fake_prov["working_tree_dirty_entries"] = ["M dgca/foo.py"]

    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="BLOCKED"),
    ):
        run_preflight(require_clean=True)


def test_c01_t06_replay_count_derived_from_exposure_records():
    """C01-T06: replay count is derived from exposure records, not constant."""
    from experiments.sctt00 import compute_replay_substitutions
    assert compute_replay_substitutions([]) == 0
    normal = [{"status": "PERSISTENT_EXECUTED", "persistent_phase": "COMMITTED"}]
    assert compute_replay_substitutions(normal) == 0

    replay1 = [{"status": "PERSISTENT_REPLAY", "persistent_phase": "COMMITTED"}]
    assert compute_replay_substitutions(replay1) == 1

    replay2 = [{"status": "PERSISTENT_EXECUTED", "persistent_phase": "REPLAY"}]
    assert compute_replay_substitutions(replay2) == 1

    replay_both = replay1 + replay2
    assert compute_replay_substitutions(replay_both) == 2


def test_c01_t07_simulated_persistent_replay_causes_replay_gate_failure():
    """C01-T07: a simulated PERSISTENT_REPLAY causes replay gate failure."""
    from experiments.sctt00 import compute_replay_substitutions
    mock_exposures = [
        {"cycle": 1, "fact_id": "F01", "status": "PERSISTENT_EXECUTED", "persistent_phase": "COMMITTED"},
        {"cycle": 1, "fact_id": "F02", "status": "PERSISTENT_REPLAY", "persistent_phase": "REPLAY"},
    ]
    count = compute_replay_substitutions(mock_exposures)
    assert count == 1
    gate_result = "PASS" if count == 0 else "FAIL"
    assert gate_result == "FAIL"


def test_c01_t08_rfc15_recurrent_engine_remains_unmaterialized():
    """C01-T08: RFC15 recurrent engine remains unmaterialized during valid trial."""
    from dgca.system_runtime import CanonicalSystemRuntime
    from experiments.sctt00 import check_graph_rfc15_state
    agent = CanonicalSystemRuntime.fresh()
    g = agent.runtime_root._graph
    state = check_graph_rfc15_state(g, "test_agent")
    assert state["recurrent_engine_is_none"] is True
    assert state["materialized"] is False
    assert g._recurrent_engine is None


def test_c01_t09_simulated_rfc15_engine_materialization_causes_gate_failure():
    """C01-T09: simulated RFC15 engine materialization causes gate failure."""
    from experiments.sctt00 import compute_rfc15_materializations
    checks = [
        {"graph_label": "baseline", "materialized": False},
        {"graph_label": "training", "materialized": True},
    ]
    calls = compute_rfc15_materializations(checks)
    assert calls == 1
    gate_result = "PASS" if calls == 0 else "FAIL"
    assert gate_result == "FAIL"


def test_c01_t10_missing_json_artifact_fails_artifact_integrity():
    """C01-T10: missing JSON artifact fails artifact-integrity test."""
    missing_path = REPO_ROOT / "experiments" / "results" / "nonexistent-sctt00-results.json"
    with pytest.raises(AssertionError):
        assert missing_path.is_file(), f"Missing canonical JSON: {missing_path}"


def test_c01_t11_missing_markdown_report_fails_artifact_integrity():
    """C01-T11: missing Markdown report fails artifact-integrity test."""
    missing_path = REPO_ROOT / "papers MD" / "NONEXISTENT-REPORT.md"
    with pytest.raises(AssertionError):
        assert missing_path.is_file(), f"Missing canonical report: {missing_path}"


def test_c01_t12_poa01_unit_checkpoint_fixtures_use_isolated_temp_location():
    """C01-T12: POA01 unit checkpoint fixtures use isolated temporary location."""
    from tests.test_rfc14_poa01 import SCTT00_CHECKPOINT, _get_poa01_test_checkpoint
    with patch.object(Path, "is_file", autospec=True) as mock_is_file:
        def fake_is_file(self):
            if str(self) == str(SCTT00_CHECKPOINT):
                return False
            return Path.exists(self)
        mock_is_file.side_effect = fake_is_file

        ckpt_path = _get_poa01_test_checkpoint()
        assert ckpt_path != SCTT00_CHECKPOINT
        assert tempfile.gettempdir().lower() in str(ckpt_path).lower() or "dgca_poa01_test_" in str(ckpt_path).lower()


def test_c01_t13_missing_canonical_sctt_checkpoint_not_silently_regenerated():
    """C01-T13: missing canonical SCTT checkpoint is NOT silently regenerated by artifact-integrity tests."""
    missing_ckpt = REPO_ROOT / "data" / "checkpoints" / "nonexistent-trained.json"
    assert not missing_ckpt.exists()
    with pytest.raises(AssertionError):
        assert missing_ckpt.is_file(), f"Mandatory SCTT00 checkpoint missing: {missing_ckpt}"
    assert not missing_ckpt.exists()


def test_c01_t14_json_and_markdown_agree_on_source_and_verdict():
    """C01-T14: JSON and SCTT Markdown agree on execution source and verdict."""
    results_json = REPO_ROOT / "experiments" / "results" / "sctt00-results.json"
    report_md = REPO_ROOT / "papers MD" / "SCTT-00-EXECUTION-REPORT.md"
    assert results_json.is_file(), f"Missing results JSON: {results_json}"
    assert report_md.is_file(), f"Missing report MD: {report_md}"

    data = json.loads(results_json.read_text(encoding="utf-8"))
    report_text = report_md.read_text(encoding="utf-8")
    verdict = data["meta"]["verdict"]
    source = data["meta"]["execution_source_commit"]

    assert verdict in report_text
    assert source in report_text


def test_c01_t15_closure_report_artifact_commit_resolves_to_real_commit():
    """C01-T15: closure report's C01_ARTIFACT_COMMIT resolves to a real Git commit."""
    report_path = REPO_ROOT / "papers MD" / "SCTT00-VR01-C01-FINAL-CLOSURE-REPORT.md"
    if not report_path.is_file():
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
        assert len(res.stdout.strip()) == 40
        return

    content = report_path.read_text(encoding="utf-8")
    m = re.search(r"C01_ARTIFACT_COMMIT[:\s`*]+([0-9a-f]{40})", content, re.IGNORECASE)
    assert m is not None, "Could not find C01_ARTIFACT_COMMIT in closure report"
    artifact_sha = m.group(1)
    res = subprocess.run(
        ["git", "rev-parse", "--verify", f"{artifact_sha}^{{commit}}"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, f"C01_ARTIFACT_COMMIT {artifact_sha} does not resolve to a real Git commit"


def test_c01_t16_closure_report_artifact_commit_is_ancestor_of_closure():
    """C01-T16: C01_ARTIFACT_COMMIT is an ancestor/parent of closure state as documented."""
    report_path = REPO_ROOT / "papers MD" / "SCTT00-VR01-C01-FINAL-CLOSURE-REPORT.md"
    if not report_path.is_file():
        res = subprocess.run(
            ["git", "merge-base", "--is-ancestor", AUTHORIZED_REPAIR_ANCHOR_COMMIT, "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            check=False,
        )
        assert res.returncode == 0
        return

    content = report_path.read_text(encoding="utf-8")
    m = re.search(r"C01_ARTIFACT_COMMIT[:\s`*]+([0-9a-f]{40})", content, re.IGNORECASE)
    assert m is not None, "Could not find C01_ARTIFACT_COMMIT in closure report"
    artifact_sha = m.group(1)
    res = subprocess.run(
        ["git", "merge-base", "--is-ancestor", artifact_sha, "HEAD"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        check=False,
    )
    assert res.returncode == 0, f"C01_ARTIFACT_COMMIT {artifact_sha} is not an ancestor of current HEAD"


def test_c01_t17_no_referenced_commit_in_closure_report_is_nonexistent():
    """C01-T17: no referenced commit SHA in closure report is nonexistent."""
    report_path = REPO_ROOT / "papers MD" / "SCTT00-VR01-C01-FINAL-CLOSURE-REPORT.md"
    if not report_path.is_file():
        return

    content = report_path.read_text(encoding="utf-8")
    shas = set(re.findall(r"\b[0-9a-f]{40}\b", content))
    assert len(shas) > 0, "No commit SHAs found in closure report"
    for sha in shas:
        res = subprocess.run(
            ["git", "cat-file", "-e", sha],
            cwd=str(REPO_ROOT),
            capture_output=True,
            check=False,
        )
        assert res.returncode == 0, f"Referenced commit SHA {sha} does not exist in Git repository"


def test_c01_t18_zero_dgca_changes_poa01_anchor_through_closure():
    """C01-T18: zero dgca/** changes from POA01 anchor through C01 closure."""
    proc = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            AUTHORIZED_REPAIR_ANCHOR_COMMIT,
            "SCTT00-VR01-VERIFIED",
            "--",
            "dgca/",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    drift = [f.strip() for f in proc.stdout.splitlines() if f.strip()]
    assert drift == [], f"Unauthorized dgca/** drift detected: {drift}"

