"""Unit tests for SCTT-00 trial harness and generated artifacts.

Verifies that experiments/sctt00.py runs, maintains all protocol invariants,
enforces real fail-closed git provenance, and produces schema-compliant results.
"""

import json
from pathlib import Path

from dgca.agent import CognitiveAgent
from experiments.sctt00 import (
    AUTHORIZED_REPAIR_ANCHOR_COMMIT,
    PROTOCOL_BASELINE_COMMIT,
    compute_safety_snapshot,
    run_preflight,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_sctt00_preflight() -> None:
    """Verifies that preflight checks pass cleanly and enforce real provenance."""
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

    assert results_json.exists(), "experiments/results/sctt00-results.json missing"
    assert report_md.exists(), "papers MD/SCTT-00-EXECUTION-REPORT.md missing"
    assert ckpt_file.exists(), "data/checkpoints/SCTT00-trained.json missing"

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
    agent = CognitiveAgent.from_checkpoint(ckpt_file)

    s_before = compute_safety_snapshot(agent)
    agent.chat("dog")
    s_after = compute_safety_snapshot(agent)

    assert s_before["state_digest"] == s_after["state_digest"]
    assert s_before["ledger"] == s_after["ledger"]
    assert s_before["logical_time"] == s_after["logical_time"]
    assert s_before["pending_evidence"] == s_after["pending_evidence"]
    assert s_before["n_total"] == s_after["n_total"]
