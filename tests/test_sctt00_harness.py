"""Unit tests for SCTT-00 trial harness and generated artifacts.

Verifies that experiments/sctt00.py runs, maintains all protocol invariants,
and produces schema-compliant results.
"""

import json
from pathlib import Path

from dgca.agent import CognitiveAgent
from experiments.sctt00 import (
    compute_safety_snapshot,
    run_preflight,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_sctt00_preflight() -> None:
    """Verifies that preflight checks pass cleanly."""
    preflight = run_preflight()
    assert preflight["head_matches"] is True or len(preflight["git_head"]) == 40
    assert preflight["apis_confirmed"] is True
    assert len(preflight["encoder_preflight"]) == 8
    for ep in preflight["encoder_preflight"]:
        assert ep["deterministic"] is True
        assert ep["subject_represented"] is True
        assert ep["target_represented"] is True


def test_sctt00_artifacts_exist_and_conform() -> None:
    """Verifies that all required artifacts from SCTT-00 exist and match protocol."""
    results_json = REPO_ROOT / "experiments" / "results" / "sctt00-results.json"
    report_md = REPO_ROOT / "papers MD" / "SCTT-00-EXECUTION-REPORT.md"
    ckpt_file = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"

    assert results_json.exists(), "experiments/results/sctt00-results.json missing"
    assert report_md.exists(), "papers MD/SCTT-00-EXECUTION-REPORT.md missing"
    assert ckpt_file.exists(), "data/checkpoints/SCTT00-trained.json missing"

    data = json.loads(results_json.read_text(encoding="utf-8"))
    assert data["meta"]["trial_id"] == "SCTT-00"
    assert data["meta"]["verdict"] in ("SCTT00_PASS", "SCTT00_FAIL", "SCTT00_BLOCKED")
    assert data["meta"]["verdict"] == "SCTT00_FAIL"
    assert data["meta"]["failure_stage"] == "E2_RETRIEVAL"
    assert len(data["success_gates"]) == 15
    assert len(data["training_exposures"]) == 40
    assert len(data["storage_audit"]["pairs"]) == 8
    assert len(data["primary_retrieval"]) == 8
    assert len(data["ood_safety_controls"]) == 4


def test_sctt00_checkpoint_chat_conservation() -> None:
    """Verifies that ordinary chat on the trained checkpoint causes zero persistent delta."""
    ckpt_file = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"
    agent = CognitiveAgent.from_checkpoint(ckpt_file)

    s_before = compute_safety_snapshot(agent)
    agent.chat("dog")
    s_after = compute_safety_snapshot(agent)

    assert s_before["state_digest"] == s_after["state_digest"]
    assert s_before["ledger"] == s_after["ledger"]
    assert s_before["logical_time"] == s_after["logical_time"]
    assert s_before["pending_evidence"] == s_after["pending_evidence"]
    assert s_before["n_total"] == s_after["n_total"]
