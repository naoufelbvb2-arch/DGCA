"""Unit tests for SCTT-00 trial harness and generated artifacts.

Verifies that experiments/sctt00.py runs, maintains all protocol invariants,
enforces real fail-closed git provenance, and produces schema-compliant results.
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from dgca.agent import CognitiveAgent
from experiments.sctt00 import (
    AUTHORIZED_REPAIR_ANCHOR_COMMIT,
    PROTOCOL_BASELINE_COMMIT,
    _run_git_name_only_diff,
    compute_safety_snapshot,
    measure_git_provenance,
    run_preflight,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_sctt00_preflight() -> None:
    """Verifies that preflight checks fail-closed on current HEAD with drift and pass on historical anchor."""
    with pytest.raises(RuntimeError, match="Unauthorized dgca/\\*\\* production drift"):
        run_preflight(require_clean=False)

    fake_prov = measure_git_provenance()
    fake_prov = dict(fake_prov)
    fake_prov["production_files_changed_anchor_to_execution"] = []
    fake_prov["production_drift_after_repair_anchor"] = []
    fake_prov["lineage_valid"] = True
    with patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov):
        preflight = run_preflight(require_clean=False)
        prov = preflight["provenance"]

        assert prov["protocol_baseline_commit"] == PROTOCOL_BASELINE_COMMIT
        assert prov["authorized_repair_anchor_commit"] == AUTHORIZED_REPAIR_ANCHOR_COMMIT
        assert prov["baseline_is_ancestor_of_anchor"] is True
        assert prov["anchor_is_ancestor_of_execution"] is True
        assert len(prov["production_drift_after_repair_anchor"]) == 0
        assert prov["authorized_production_delta"] == ["dgca/completion.py", "dgca/generation.py"]
        assert set(prov["production_files_changed_baseline_to_anchor"]) == {
            "dgca/completion.py",
            "dgca/generation.py",
        }

        assert preflight["apis_confirmed"] is True
        assert len(preflight["encoder_preflight"]) == 8
        for ep in preflight["encoder_preflight"]:
            assert ep["deterministic"] is True
            assert ep["subject_represented"] is True
            assert ep["target_represented"] is True
            assert ep["status"] == "PASS"


def test_sctt00_artifacts_exist_and_conform() -> None:
    """Verifies that all required artifacts from SCTT-00 exist, match protocol and rerun semantics."""
    results_json = REPO_ROOT / "experiments" / "results" / "sctt00-results.json"
    report_md = REPO_ROOT / "papers MD" / "SCTT-00-EXECUTION-REPORT.md"
    ckpt_file = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"

    assert results_json.is_file(), f"experiments/results/sctt00-results.json missing: {results_json}"
    assert report_md.is_file(), f"papers MD/SCTT-00-EXECUTION-REPORT.md missing: {report_md}"
    assert ckpt_file.is_file(), f"data/checkpoints/SCTT00-trained.json missing: {ckpt_file}"

    data = json.loads(results_json.read_text(encoding="utf-8"))
    meta = data["meta"]
    prov = data.get("provenance", {})

    # Execution profile and provenance verification
    assert meta["trial_id"] == "SCTT-00"
    assert meta["verdict"] in ("SCTT00_PASS", "SCTT00_REPAIR_RERUN_PASS")
    assert meta["failure_stage"] == "NONE"

    # Verification of trial counts
    assert len(data["training_exposures"]) == 40
    assert len(data["storage_audit"]["pairs"]) == 8

    # Learned recall 8/8
    assert len(data["primary_retrieval"]) == 8
    recalled_count = sum(1 for p in data["primary_retrieval"] if p["recalled"])
    assert recalled_count == 8

    # OOD safety 4/4
    assert len(data["ood_safety_controls"]) == 4
    ood_passed = sum(1 for o in data["ood_safety_controls"] if o["passed"])
    assert ood_passed == 4

    # Restore determinism 8/8
    det_passed = sum(1 for d in data.get("clean_restore_determinism", []) if d["deterministic"])
    assert det_passed == 8

    # Ordinary chat safety
    assert data["ordinary_chat_safety"]["all_safe"] is True

    # In repair rerun profile, verify strict provenance keys and report coherence
    if meta.get("execution_profile") == "SCTT00_POST_REPAIR_RERUN_V1":
        assert meta["verdict"] == "SCTT00_REPAIR_RERUN_PASS"
        assert prov.get("protocol_baseline_commit") == PROTOCOL_BASELINE_COMMIT
        assert prov.get("authorized_repair_anchor_commit") == AUTHORIZED_REPAIR_ANCHOR_COMMIT
        assert prov.get("working_tree_clean_at_start") is True
        assert prov.get("anchor_is_ancestor_of_execution") is True
        assert prov.get("production_drift_after_repair_anchor") == []
        report_text = report_md.read_text(encoding="utf-8")
        assert meta["verdict"] in report_text
        assert "0/8 recall" not in report_text
        assert "E2_RETRIEVAL" not in report_text


def test_sctt00_checkpoint_chat_conservation() -> None:
    """Verifies that ordinary chat on the trained checkpoint causes zero persistent delta."""
    ckpt_file = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"
    assert ckpt_file.is_file(), f"data/checkpoints/SCTT00-trained.json missing: {ckpt_file}"
    agent = CognitiveAgent.from_checkpoint(ckpt_file)
    runtime = agent._runtime

    # Passing agent raises TypeError per strict typing
    with pytest.raises(TypeError, match="Target must be CanonicalSystemRuntime or CanonicalR1RuntimeRoot"):
        compute_safety_snapshot(agent)

    s_before = compute_safety_snapshot(runtime)
    agent.chat("dog")
    s_after = compute_safety_snapshot(runtime)

    assert s_before["state_digest"] == s_after["state_digest"]
    assert s_before["ledger"] == s_after["ledger"]
    assert s_before["logical_time"] == s_after["logical_time"]
    assert s_before["pending_evidence"] == s_after["pending_evidence"]
    assert s_before["n_total"] == s_after["n_total"]


# =============================================================================
# C02 Tests: Git Provenance Command Failure Hardening (C02-T01 to C02-T09)
# =============================================================================

def test_c02_t01_baseline_to_anchor_git_diff_nonzero_blocks():
    """C02-T01: baseline -> anchor git diff returns non-zero => BLOCKED."""
    original_subprocess_run = subprocess.run

    def fake_subprocess_run(cmd, *args, **kwargs):
        if cmd[:3] == ["git", "diff", "--name-only"] and PROTOCOL_BASELINE_COMMIT in cmd:
            return subprocess.CompletedProcess(
                cmd, returncode=128, stdout="", stderr="fatal: bad baseline object"
            )
        return original_subprocess_run(cmd, *args, **kwargs)

    with patch("subprocess.run", side_effect=fake_subprocess_run):
        prov = measure_git_provenance()
        assert prov["lineage_valid"] is False
        assert any("fatal: bad baseline object" in err for err in prov["provenance_errors"])
        with pytest.raises(RuntimeError, match="BLOCKED"):
            run_preflight(require_clean=False)


def test_c02_t02_anchor_to_execution_git_diff_nonzero_blocks():
    """C02-T02: anchor -> execution git diff returns non-zero => BLOCKED."""
    original_subprocess_run = subprocess.run

    def fake_subprocess_run(cmd, *args, **kwargs):
        if (
            cmd[:3] == ["git", "diff", "--name-only"]
            and AUTHORIZED_REPAIR_ANCHOR_COMMIT in cmd
            and len(cmd) > 5
            and cmd[4] != "--"
        ):
            return subprocess.CompletedProcess(
                cmd, returncode=128, stdout="", stderr="fatal: bad execution revision"
            )
        return original_subprocess_run(cmd, *args, **kwargs)

    with patch("subprocess.run", side_effect=fake_subprocess_run):
        prov = measure_git_provenance()
        assert prov["lineage_valid"] is False
        assert any("fatal: bad execution revision" in err for err in prov["provenance_errors"])
        with pytest.raises(RuntimeError, match="BLOCKED"):
            run_preflight(require_clean=False)


def test_c02_t03_anchor_to_working_tree_git_diff_nonzero_blocks():
    """C02-T03: anchor -> working-tree git diff returns non-zero => BLOCKED."""
    original_subprocess_run = subprocess.run

    def fake_subprocess_run(cmd, *args, **kwargs):
        if (
            cmd[:3] == ["git", "diff", "--name-only"]
            and AUTHORIZED_REPAIR_ANCHOR_COMMIT in cmd
            and len(cmd) > 4
            and cmd[4] == "--"
        ):
            return subprocess.CompletedProcess(
                cmd, returncode=128, stdout="", stderr="fatal: working tree read error"
            )
        return original_subprocess_run(cmd, *args, **kwargs)

    with patch("subprocess.run", side_effect=fake_subprocess_run):
        prov = measure_git_provenance()
        assert prov["lineage_valid"] is False
        assert any("fatal: working tree read error" in err for err in prov["provenance_errors"])
        with pytest.raises(RuntimeError, match="BLOCKED"):
            run_preflight(require_clean=False)


def test_c02_t04_nonzero_git_diff_with_empty_stdout_cannot_become_empty_list():
    """C02-T04: non-zero git diff with empty stdout cannot become []."""
    mock_errors: list[str] = []
    fake_proc = subprocess.CompletedProcess(
        ["git", "diff", "--name-only", "A", "B", "--", "dgca/"],
        returncode=128,
        stdout="",
        stderr="fatal: corrupted repository index",
    )
    with patch("subprocess.run", return_value=fake_proc):
        diff_result = _run_git_name_only_diff(["A", "B"], REPO_ROOT, mock_errors)

    assert diff_result != []
    assert len(diff_result) == 1
    assert diff_result[0].startswith("ERROR:")
    assert "corrupted repository index" in diff_result[0]
    assert len(mock_errors) == 1


def test_c02_t05_nonzero_git_diff_with_partial_stdout_still_blocked():
    """C02-T05: non-zero git diff with misleading partial stdout still BLOCKED."""
    mock_errors: list[str] = []
    fake_proc = subprocess.CompletedProcess(
        ["git", "diff", "--name-only", "A", "B", "--", "dgca/"],
        returncode=1,
        stdout="dgca/completion.py\ndgca/generation.py\n",
        stderr="warning: partial diff error",
    )
    with patch("subprocess.run", return_value=fake_proc):
        diff_result = _run_git_name_only_diff(["A", "B"], REPO_ROOT, mock_errors)

    assert diff_result != ["dgca/completion.py", "dgca/generation.py"]
    assert len(diff_result) == 1
    assert diff_result[0].startswith("ERROR:")
    assert len(mock_errors) == 1

    fake_prov = measure_git_provenance()
    fake_prov = dict(fake_prov)
    fake_prov["provenance_errors"] = ["ERROR: git diff failed (rc=1): warning: partial diff error"]
    with (
        patch("experiments.sctt00.measure_git_provenance", return_value=fake_prov),
        pytest.raises(RuntimeError, match="BLOCKED"),
    ):
        run_preflight(require_clean=False)


def test_c02_t06_successful_git_diff_with_empty_stdout_remains_valid_empty_diff():
    """C02-T06: successful git diff with empty stdout remains valid empty diff."""
    mock_errors: list[str] = []
    fake_proc = subprocess.CompletedProcess(
        ["git", "diff", "--name-only", "A", "B", "--", "dgca/"],
        returncode=0,
        stdout="",
        stderr="",
    )
    with patch("subprocess.run", return_value=fake_proc):
        diff_result = _run_git_name_only_diff(["A", "B"], REPO_ROOT, mock_errors)

    assert diff_result == []
    assert len(mock_errors) == 0


def test_c02_t07_stderr_error_detail_is_retained_for_diagnostics():
    """C02-T07: stderr/error detail is retained for diagnostics."""
    mock_errors: list[str] = []
    diagnostic_stderr = "fatal: ambiguous argument 'HEAD~99': unknown revision"
    fake_proc = subprocess.CompletedProcess(
        ["git", "diff", "--name-only", "HEAD~99", "--", "dgca/"],
        returncode=128,
        stdout="",
        stderr=diagnostic_stderr,
    )
    with patch("subprocess.run", return_value=fake_proc):
        diff_result = _run_git_name_only_diff(["HEAD~99"], REPO_ROOT, mock_errors)

    assert len(diff_result) == 1
    assert diagnostic_stderr in diff_result[0]
    assert len(mock_errors) == 1
    assert diagnostic_stderr in mock_errors[0]


def test_c02_t08_ordinary_current_ric02_head_blocks_sctt_preflight():
    """C02-T08: ordinary current RIC-02 HEAD still blocks historical SCTT preflight because of real post-anchor production drift."""
    with pytest.raises(RuntimeError, match="Unauthorized dgca/\\*\\* production drift"):
        run_preflight(require_clean=False)


def test_c02_t09_historical_committed_sctt_artifacts_remain_untouched():
    """C02-T09: historical committed SCTT artifacts remain untouched and conform to historical tag."""
    results_json = REPO_ROOT / "experiments" / "results" / "sctt00-results.json"
    report_md = REPO_ROOT / "papers MD" / "SCTT-00-EXECUTION-REPORT.md"
    ckpt_file = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"

    assert results_json.is_file()
    assert report_md.is_file()
    assert ckpt_file.is_file()

    diff_res = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "SCTT00-VR01-VERIFIED",
            "HEAD",
            "--",
            "experiments/results/sctt00-results.json",
            "papers MD/SCTT-00-EXECUTION-REPORT.md",
            "data/checkpoints/SCTT00-trained.json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_artifacts = [line.strip() for line in diff_res.stdout.splitlines() if line.strip()]
    assert changed_artifacts == [], f"Historical artifacts modified from tag: {changed_artifacts}"
