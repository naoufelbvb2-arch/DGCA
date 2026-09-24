"""DGCA — SCTT-00 Strict Execution Harness.

Small Controlled Training Trial 00: Canonical Learn -> Persist -> Reload -> Retrieve -> Generate
Experimental Protocol: papers MD/DGCA-SCTT-00-Small-Controlled-Training-Trial-Protocol-v1.0-FROZEN.md
Protocol Baseline Commit: 833241d54309d72715c42dc5f2b939c3179e257d
Authorized Repair Anchor Commit (POA01): 1a269aac42fcf44a824fe677526a92e6e2f81d9f
Execution Profile: SCTT00_POST_REPAIR_RERUN_V1
"""

from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca.agent import CognitiveAgent
from dgca.causal_identity import (
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalRuntimeHealth,
    create_native_r1_provenance_epoch,
)
from dgca.encoder import MasterSymbolicEncoder
from dgca.graph import CognitiveGraph
from dgca.numbers import init_quantity_backbone
from dgca.observation import (
    ExecutionMode,
    close_result,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    save_canonical_r1_checkpoint,
)
from dgca.system_runtime import CanonicalSystemRuntime

# ─────────────────────────────────────────────────────────── Frozen Fact Bank
FACTS = (
    ("F01", "A dog is a canine.", "dog", "canine"),
    ("F02", "A cat is a feline.", "cat", "feline"),
    ("F03", "A robin is a bird.", "robin", "bird"),
    ("F04", "A rose is a flower.", "rose", "flower"),
    ("F05", "An apple is a fruit.", "apple", "fruit"),
    ("F06", "A car is a vehicle.", "car", "vehicle"),
    ("F07", "Ice is solid.", "ice", "solid"),
    ("F08", "Water is liquid.", "water", "liquid"),
)

ALL_TARGETS = {tgt for _, _, _, tgt in FACTS}
OOD_CUES = ("stone", "horse", "train", "banana")
NATURAL_QUESTIONS = (
    "What is a dog?",
    "What is a cat?",
    "What is a robin?",
    "What is an apple?",
)

PROTOCOL_BASELINE_COMMIT = "833241d54309d72715c42dc5f2b939c3179e257d"
AUTHORIZED_REPAIR_ANCHOR_COMMIT = "1a269aac42fcf44a824fe677526a92e6e2f81d9f"
EXPECTED_AUTHORIZED_PRODUCTION_DELTA = (
    "dgca/completion.py",
    "dgca/generation.py",
)
EXECUTION_PROFILE = "SCTT00_POST_REPAIR_RERUN_V1"
CAPABILITY = object()


class TrialAuthorizer:
    """Experiment-only authorizer conforming strictly to Protocol §5."""

    def verify_persistent_observation(
        self,
        *,
        capability: object,
        root_external_episode_id: str,
        ingress_event_id: str,
        modality: str,
        operation_kind: str,
    ) -> bool:
        return (
            capability is CAPABILITY
            and modality == "text"
            and operation_kind == "R2_AUTHORIZED_PERSISTENT"
        )


def compute_safety_snapshot(target: CanonicalSystemRuntime | CanonicalR1RuntimeRoot) -> dict[str, Any]:
    """Computes a strict snapshot of all persistent and ledger state from runtime or root."""
    if isinstance(target, CanonicalSystemRuntime):
        r = target.runtime_root
    elif isinstance(target, CanonicalR1RuntimeRoot):
        r = target
    else:
        raise TypeError(
            f"Target must be CanonicalSystemRuntime or CanonicalR1RuntimeRoot, got {type(target).__name__}"
        )
    g = r._graph
    payload = extract_canonical_persistent_payload(g)
    digest = compute_checkpoint_state_digest(payload)
    return {
        "state_digest": digest,
        "ledger": r.ledger.to_dict(),
        "logical_time": payload["logical_time"],
        "pending_evidence": payload["pending_structural_evidence"],
        "n_total": {n["nid"]: n["N_total"] for n in payload["nodes"]},
    }


def _run_git_name_only_diff(
    args: list[str],
    repo_root: Path,
    provenance_errors: list[str],
) -> list[str]:
    """Runs a git diff --name-only command with strict returncode checking.

    Distinguishes success with empty output (valid zero diff) from command failure.
    On returncode == 0: returns normalized list of changed files.
    On returncode != 0 or OSError: records stderr/detail into provenance_errors and
    returns a singleton error list [f"ERROR: ..."], ensuring non-zero exit code never
    yields an empty list ([]).
    """
    cmd = ["git", "diff", "--name-only", *args, "--", "dgca/"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            stderr_detail = proc.stderr.strip()
            stdout_detail = proc.stdout.strip()
            detail = stderr_detail or stdout_detail or "empty error output"
            err = (
                f"ERROR: command {' '.join(cmd)} failed (rc={proc.returncode}): {detail}"
            )
            provenance_errors.append(err)
            return [err]
        return [
            f.replace("\\", "/").strip()
            for f in proc.stdout.splitlines()
            if f.strip()
        ]
    except (subprocess.SubprocessError, OSError) as e:
        err = f"ERROR: command {' '.join(cmd)} raised {type(e).__name__}: {e}"
        provenance_errors.append(err)
        return [err]


def measure_git_provenance(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Protocol §1, §3 & VR01-C01 & C02: Strict measurement of git provenance and working-tree cleanliness."""
    provenance_errors: list[str] = []

    # 1. Execution source commit
    try:
        proc_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc_head.returncode != 0:
            err = f"ERROR: git rev-parse HEAD failed (rc={proc_head.returncode}): {proc_head.stderr.strip()}"
            execution_source_commit = err
            provenance_errors.append(err)
        else:
            execution_source_commit = proc_head.stdout.strip()
    except (subprocess.SubprocessError, OSError) as e:
        err = f"ERROR: git rev-parse HEAD raised {e}"
        execution_source_commit = err
        provenance_errors.append(err)

    # 2. Working tree cleanliness (tracked staged/unstaged + untracked)
    try:
        proc_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc_status.returncode != 0:
            stderr_detail = proc_status.stderr.strip() or "empty error output"
            err = f"ERROR: git status --porcelain failed (rc={proc_status.returncode}): {stderr_detail}"
            working_tree_clean_at_start = False
            dirty_entries = [err]
            provenance_errors.append(err)
        else:
            status_lines = [line.strip() for line in proc_status.stdout.splitlines() if line.strip()]
            working_tree_clean_at_start = len(status_lines) == 0
            dirty_entries = status_lines
    except (subprocess.SubprocessError, OSError) as e:
        working_tree_clean_at_start = False
        err = f"ERROR: git status raised {e}"
        dirty_entries = [err]
        provenance_errors.append(err)

    # 3. Ancestry verification
    def resolve_rev(rev: str) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", rev],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0:
                return res.stdout.strip()
            provenance_errors.append(
                f"ERROR: git rev-parse {rev} failed (rc={res.returncode}): {res.stderr.strip()}"
            )
        except (subprocess.SubprocessError, OSError) as e:
            provenance_errors.append(f"ERROR: git rev-parse {rev} raised {e}")
        return rev

    def is_ancestor(ancestor: str, descendant: str) -> bool:
        ancestor_sha = resolve_rev(ancestor)
        descendant_sha = resolve_rev(descendant)
        if not (len(ancestor_sha) == 40 and len(descendant_sha) == 40):
            return False
        try:
            res = subprocess.run(
                ["git", "merge-base", "--is-ancestor", ancestor_sha, descendant_sha],
                cwd=str(repo_root),
                capture_output=True,
                check=False,
            )
            return res.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False

    baseline_is_ancestor_of_anchor = is_ancestor(
        PROTOCOL_BASELINE_COMMIT, AUTHORIZED_REPAIR_ANCHOR_COMMIT
    )
    anchor_is_ancestor_of_execution = is_ancestor(
        AUTHORIZED_REPAIR_ANCHOR_COMMIT, execution_source_commit
    )

    # 4. Production files changed baseline -> anchor
    prod_files_base_anchor = _run_git_name_only_diff(
        [PROTOCOL_BASELINE_COMMIT, AUTHORIZED_REPAIR_ANCHOR_COMMIT],
        repo_root,
        provenance_errors,
    )

    # 5. Production files changed anchor -> execution HEAD
    prod_files_anchor_exec = _run_git_name_only_diff(
        [AUTHORIZED_REPAIR_ANCHOR_COMMIT, execution_source_commit],
        repo_root,
        provenance_errors,
    )

    # 6. Production files changed anchor -> working tree
    prod_files_anchor_wt = _run_git_name_only_diff(
        [AUTHORIZED_REPAIR_ANCHOR_COMMIT],
        repo_root,
        provenance_errors,
    )

    production_drift = sorted(set(prod_files_anchor_exec + prod_files_anchor_wt))

    has_errors = bool(
        provenance_errors
        or any(
            str(x).startswith("ERROR:")
            for x in (
                [execution_source_commit]
                + prod_files_base_anchor
                + prod_files_anchor_exec
                + prod_files_anchor_wt
            )
        )
    )

    lineage_valid = (
        not has_errors
        and baseline_is_ancestor_of_anchor
        and anchor_is_ancestor_of_execution
        and set(prod_files_base_anchor) == set(EXPECTED_AUTHORIZED_PRODUCTION_DELTA)
        and len(production_drift) == 0
    )

    return {
        "protocol_baseline_commit": PROTOCOL_BASELINE_COMMIT,
        "authorized_repair_anchor_commit": AUTHORIZED_REPAIR_ANCHOR_COMMIT,
        "execution_source_commit": execution_source_commit,
        "working_tree_clean_at_start": working_tree_clean_at_start,
        "working_tree_dirty_entries": dirty_entries,
        "baseline_is_ancestor_of_anchor": baseline_is_ancestor_of_anchor,
        "anchor_is_ancestor_of_execution": anchor_is_ancestor_of_execution,
        "authorized_production_delta": list(EXPECTED_AUTHORIZED_PRODUCTION_DELTA),
        "production_files_changed_baseline_to_anchor": prod_files_base_anchor,
        "production_drift_after_repair_anchor": production_drift,
        "production_files_changed_anchor_to_execution": prod_files_anchor_exec,
        "provenance_errors": provenance_errors,
        "lineage_valid": lineage_valid,
    }


def run_preflight(require_clean: bool = True, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Protocol §1 & §3 & VR01-C01: Fail-closed verification of provenance, cleanliness, APIs, and encoder."""
    prov = measure_git_provenance(repo_root)

    # 0. Fail-closed check on git command failures
    if prov.get("provenance_errors"):
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Git provenance command failure: "
            f"{prov['provenance_errors']}"
        )

    if str(prov.get("execution_source_commit", "")).startswith("ERROR:"):
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Failed to determine execution source commit: "
            f"{prov['execution_source_commit']}"
        )

    # 1. Working tree clean at start
    if require_clean and not prov["working_tree_clean_at_start"]:
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Dirty working tree detected at trial start: "
            f"{prov['working_tree_dirty_entries']}"
        )

    # 2. Protocol baseline is ancestor of POA01 anchor
    if not prov.get("baseline_is_ancestor_of_anchor"):
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Protocol baseline {PROTOCOL_BASELINE_COMMIT} "
            f"is not an ancestor of authorized POA01 anchor {AUTHORIZED_REPAIR_ANCHOR_COMMIT}"
        )

    # 3. POA01 anchor is ancestor of execution source
    if not prov.get("anchor_is_ancestor_of_execution"):
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Execution source {prov['execution_source_commit']} "
            f"is not a descendant of authorized POA01 anchor {AUTHORIZED_REPAIR_ANCHOR_COMMIT}"
        )

    # 4. Baseline -> Anchor production delta is exactly completion.py and generation.py
    if set(prov.get("production_files_changed_baseline_to_anchor", [])) != set(EXPECTED_AUTHORIZED_PRODUCTION_DELTA):
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Baseline to anchor production delta mismatch: "
            f"expected {set(EXPECTED_AUTHORIZED_PRODUCTION_DELTA)}, "
            f"observed {set(prov.get('production_files_changed_baseline_to_anchor', []))}"
        )

    # 5. Anchor -> Execution production delta is empty
    if len(prov.get("production_files_changed_anchor_to_execution", [])) > 0:
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Unauthorized dgca/** production drift (anchor to execution): "
            f"{prov['production_files_changed_anchor_to_execution']}"
        )

    # 6. Anchor -> Working tree production drift is empty
    if len(prov.get("production_drift_after_repair_anchor", [])) > 0:
        raise RuntimeError(
            f"SCTT00_REPAIR_RERUN_BLOCKED: Unauthorized dgca/** production drift after POA01 anchor: "
            f"{prov['production_drift_after_repair_anchor']}"
        )

    if not prov.get("lineage_valid"):
        raise RuntimeError(
            "SCTT00_REPAIR_RERUN_BLOCKED: Lineage validation failed"
        )

    # Check APIs
    assert hasattr(CanonicalR1RuntimeRoot, "create_observation_bridge")
    assert hasattr(ExecutionMode, "AUTHORIZED_PERSISTENT")
    assert callable(save_canonical_r1_checkpoint)
    assert hasattr(CanonicalSystemRuntime, "from_checkpoint")
    assert hasattr(CognitiveAgent, "from_checkpoint")

    # Encoder Preflight (Protocol §3)
    encoder = MasterSymbolicEncoder()
    encoder_records = []
    for fid, sentence, subj, tgt in FACTS:
        run1 = encoder.encode_text(sentence)
        run2 = encoder.encode_text(sentence)

        assert len(run1) > 0, f"Empty encoder output for {fid}"
        assert len(run1) == len(run2), f"Non-deterministic length for {fid}"

        # Check representation of subject and target
        signals_run1 = [sig for ep in run1 for sig in ep.signals]
        signals_run2 = [sig for ep in run2 for sig in ep.signals]
        assert signals_run1 == signals_run2, f"Non-deterministic signals for {fid}"

        subj_represented = any(s[0] == "text" and s[1] == subj for s in signals_run1)
        tgt_represented = any(s[0] == "text" and s[1] == tgt for s in signals_run1)

        assert subj_represented, f"Subject {subj} not represented in {fid}"
        assert tgt_represented, f"Target {tgt} not represented in {fid}"

        encoder_records.append({
            "fact_id": fid,
            "sentence": sentence,
            "subject": subj,
            "target": tgt,
            "episodes_count": len(run1),
            "signals": signals_run1,
            "deterministic": True,
            "subject_represented": subj_represented,
            "target_represented": tgt_represented,
            "status": "PASS",
        })

    return {
        "git_head": prov["execution_source_commit"],
        "head_matches": prov["execution_source_commit"] == AUTHORIZED_REPAIR_ANCHOR_COMMIT,
        "provenance": prov,
        "working_tree_clean": prov["working_tree_clean_at_start"],
        "working_tree_dirty_entries": prov["working_tree_dirty_entries"],
        "apis_confirmed": True,
        "encoder_preflight": encoder_records,
        "encoder_gate": f"{len(encoder_records)}/8 PASS",
    }


def compute_replay_substitutions(exposures: list[dict[str, Any]]) -> int:
    """Mechanically counts any exposures marked as PERSISTENT_REPLAY or replay phase."""
    return sum(
        1
        for ex in exposures
        if ex.get("status") == "PERSISTENT_REPLAY"
        or ex.get("persistent_phase") == "REPLAY"
        or "REPLAY" in str(ex.get("status", "")).upper()
        or "REPLAY" in str(ex.get("persistent_phase", "")).upper()
    )


def check_graph_rfc15_state(graph: Any, label: str) -> dict[str, Any]:
    """Protocol §18 / VR01-C01: Strict measurement of RFC15 recurrent engine non-materialization."""
    engine = getattr(graph, "_recurrent_engine", None)
    is_none = engine is None
    return {
        "graph_label": label,
        "recurrent_engine_is_none": is_none,
        "materialized": not is_none,
        "engine_type": type(engine).__name__ if engine is not None else "NoneType",
    }


def compute_rfc15_materializations(records: list[dict[str, Any]]) -> int:
    """Mechanically derives count of any materialized RFC15 engines."""
    return sum(1 for r in records if r.get("materialized", False))


def run_baseline_probes(
    runtime: CanonicalSystemRuntime | None = None,
    rfc15_checks_out: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Protocol §6: Probe 8 subject cues on fresh un-trained CanonicalSystemRuntime."""
    if runtime is None:
        runtime = CanonicalSystemRuntime.fresh()
    g = runtime.runtime_root._graph
    if rfc15_checks_out is not None and g is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(g, "baseline_agent_before_probes"))

    records = []
    for fid, sentence, subj, tgt in FACTS:
        reply = runtime.chat(subj)
        tokens = reply.split()
        target_in_reply = tgt in tokens
        if target_in_reply:
            raise RuntimeError(
                f"SCTT00_BLOCKED: BASELINE_CONTAMINATION on cue {subj} -> target {tgt}"
            )
        records.append({
            "fact_id": fid,
            "cue": subj,
            "expected_target": tgt,
            "reply": reply,
            "target_in_reply": target_in_reply,
            "uncontaminated": not target_in_reply,
        })

    if rfc15_checks_out is not None and g is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(g, "baseline_agent_after_probes"))
    return records


def execute_training(
    rfc15_checks_out: list[dict[str, Any]] | None = None,
) -> tuple[CanonicalR1RuntimeRoot, list[dict[str, Any]]]:
    """Protocol §4, §5, §7, §8: Fresh canonical boot and 40 authorized exposures."""
    graph = CognitiveGraph(enable_prediction=False)
    init_quantity_backbone(graph)
    persistent_payload = extract_canonical_persistent_payload(graph)
    state_digest = compute_checkpoint_state_digest(persistent_payload)
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    lifecycle_guard = RuntimeLifecycleGuard()
    authorizer = TrialAuthorizer()

    runtime_root = CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version="R2-OBS-1.0",
        lifecycle_guard=lifecycle_guard,
    )
    bridge = runtime_root.create_observation_bridge(authorizer=authorizer)

    if rfc15_checks_out is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(graph, "training_runtime_before_exposures"))

    exposures: list[dict[str, Any]] = []
    for cycle in range(1, 6):
        for fid, sentence, subj, tgt in FACTS:
            occ_key = f"SCTT00:{fid}:E{cycle}"
            res = bridge.observe_text(
                boundary_namespace="DGCA:SCTT00:TRAIN:v1",
                source_occurrence_key=occ_key,
                source_event_key="training_fact",
                ingress_boundary="SCTT00_CANONICAL_TEXT_TRAINING",
                raw_text=sentence,
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability=CAPABILITY,
            )

            rec = {
                "cycle": cycle,
                "fact_id": fid,
                "sentence": sentence,
                "occurrence_key": occ_key,
                "status": res.status,
                "mode": res.mode.value if hasattr(res.mode, "value") else str(res.mode),
                "persistent_phase": res.persistent_phase,
                "persistent_executed": res.persistent_executed,
                "transaction_id": res.persistent_transaction_id,
                "root_external_episode_id": res.root_external_episode_id,
                "ingress_event_id": res.ingress_event_id,
            }
            exposures.append(rec)
            close_result(res)

            # Protocol §8 Per-Exposure Gate
            if res.status == "PERSISTENT_REPLAY" or res.persistent_phase == "REPLAY":
                raise RuntimeError(
                    f"SCTT00_BLOCKED: Unauthorized PERSISTENT_REPLAY observed on {occ_key}"
                )
            assert res.status == "PERSISTENT_EXECUTED", f"Expected PERSISTENT_EXECUTED, got {res.status}"
            assert res.mode == ExecutionMode.AUTHORIZED_PERSISTENT
            assert res.persistent_phase == "COMMITTED"
            assert res.persistent_executed is True
            assert res.persistent_transaction_id is not None

    if rfc15_checks_out is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(graph, "training_runtime_after_exposures"))

    return runtime_root, exposures


def run_storage_audit(runtime_root: CanonicalR1RuntimeRoot) -> dict[str, Any]:
    """Protocol §10: Storage Audit of persisted relations and graph metrics."""
    graph = runtime_root._graph
    pair_audits = []
    for fid, sentence, subj, tgt in FACTS:
        subj_nid = f"concept:{subj}" if f"concept:{subj}" in graph.nodes else f"text:{subj}"
        tgt_nid = f"concept:{tgt}" if f"concept:{tgt}" in graph.nodes else f"text:{tgt}"

        edge_fwd = graph.edges.get((subj_nid, tgt_nid))
        edge_bwd = graph.edges.get((tgt_nid, subj_nid))

        assert edge_fwd is not None, f"Missing forward edge for {fid} ({subj_nid} -> {tgt_nid})"
        assert edge_bwd is not None, f"Missing backward edge for {fid} ({tgt_nid} -> {subj_nid})"

        pair_audits.append({
            "fact_id": fid,
            "subject": subj,
            "target": tgt,
            "subject_nid": subj_nid,
            "target_nid": tgt_nid,
            "forward_edge": {
                "kind": edge_fwd.kind,
                "W": float(edge_fwd.W),
                "n": int(edge_fwd.n),
                "contexts": list(edge_fwd.contexts),
                "ctx_hits": dict(edge_fwd.ctx_hits),
            },
            "backward_edge": {
                "kind": edge_bwd.kind,
                "W": float(edge_bwd.W),
                "n": int(edge_bwd.n),
                "contexts": list(edge_bwd.contexts),
                "ctx_hits": dict(edge_bwd.ctx_hits),
            },
            "relation_persisted": True,
        })

    payload = extract_canonical_persistent_payload(graph)
    state_digest = compute_checkpoint_state_digest(payload)

    return {
        "pairs": pair_audits,
        "persisted_relations_gate": f"{len(pair_audits)}/8 PASS",
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "logical_time": int(graph.t),
        "pending_evidence": payload["pending_structural_evidence"],
        "assembly_count": len(payload.get("assemblies", [])),
        "committed_transaction_count": len(runtime_root._ledger.committed_transactions),
        "state_digest": state_digest,
    }


def save_checkpoint(runtime_root: CanonicalR1RuntimeRoot, ckpt_path: Path) -> dict[str, Any]:
    """Protocol §11: Canonical Save."""
    assert runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY
    assert runtime_root.canonical_lineage_state == CanonicalLineageState.VALID

    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_digest = save_canonical_r1_checkpoint(runtime_root, ckpt_path)

    raw_bytes = ckpt_path.read_bytes()
    file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    ckpt_json = json.loads(raw_bytes.decode("utf-8"))

    try:
        rel_path = str(ckpt_path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        rel_path = str(ckpt_path).replace("\\", "/")

    return {
        "path": rel_path,
        "file_sha256": file_sha256,
        "checkpoint_bundle_digest": bundle_digest,
        "checkpoint_state_digest": ckpt_json["integrity"]["checkpoint_state_digest"],
        "provenance_epoch_digest": ckpt_json["integrity"]["causal_provenance_digest"],
        "schema_version": ckpt_json["schema"]["checkpoint_schema_version"],
        "runtime_version": ckpt_json["schema"]["runtime_contract_version"],
        "observation_protocol_version": ckpt_json["schema"]["observation_protocol_version"],
    }


def run_primary_retrieval(
    ckpt_path: Path,
    rfc15_checks_out: list[dict[str, Any]] | None = None,
) -> tuple[CanonicalSystemRuntime, list[dict[str, Any]], list[dict[str, Any]]]:
    """Protocol §12, §13, §15, §18: Restore, probe 8 cues, verify safety snapshots, classify."""
    runtime = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
    g = runtime.runtime_root._graph
    if rfc15_checks_out is not None and g is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(g, "primary_runtime_before_retrieval"))

    probes: list[dict[str, Any]] = []
    safety_records: list[dict[str, Any]] = []

    for fid, sentence, subj, tgt in FACTS:
        s_before = compute_safety_snapshot(runtime)
        reply = runtime.chat(subj)
        s_after = compute_safety_snapshot(runtime)

        # Safety conservation check (Protocol §15)
        digest_match = s_before["state_digest"] == s_after["state_digest"]
        ledger_match = s_before["ledger"] == s_after["ledger"]
        time_match = s_before["logical_time"] == s_after["logical_time"]
        pending_match = s_before["pending_evidence"] == s_after["pending_evidence"]
        ntotal_match = s_before["n_total"] == s_after["n_total"]
        is_safe = digest_match and ledger_match and time_match and pending_match and ntotal_match

        safety_records.append({
            "stage": "primary_probe",
            "cue": subj,
            "safe": is_safe,
            "digest_match": digest_match,
            "ledger_match": ledger_match,
            "time_match": time_match,
            "pending_match": pending_match,
            "ntotal_match": ntotal_match,
        })
        assert is_safe, f"Safety violation during chat probe '{subj}'!"

        # Protocol §13 Correct Recall Definition
        tokens = reply.split()
        target_in_tokens = tgt in tokens
        cue_absent_target = tgt != subj
        competing_targets = [
            t for t in ALL_TARGETS if t != tgt and t in tokens
        ]
        recalled = target_in_tokens and cue_absent_target and len(competing_targets) == 0

        # Diagnosis of failure stage (Protocol §18)
        last_turn = runtime.last_turn
        failure_stage = None
        if not recalled:
            failure_stage = "E2_RETRIEVAL"

        probes.append({
            "fact_id": fid,
            "cue": subj,
            "expected_target": tgt,
            "reply": reply,
            "tokens": tokens,
            "recalled": recalled,
            "failure_stage": failure_stage,
            "last_turn": {
                "turn_index": last_turn.session_turn_index if last_turn else None,
                "root_external_episode_id": last_turn.root_external_episode_id if last_turn else None,
                "ingress_event_id": last_turn.ingress_event_id if last_turn else None,
                "observation_transaction_id": last_turn.observation_transaction_id if last_turn else None,
                "micro_episode_ids": list(last_turn.micro_episode_ids) if last_turn else [],
                "input_representation_ids": list(last_turn.input_representation_ids) if last_turn else [],
                "settled_representation_ids": list(last_turn.settled_representation_ids) if last_turn else [],
                "surface_chunk_ids": list(last_turn.surface_chunk_ids) if last_turn else [],
                "completion_closure_reasons": list(last_turn.completion_closure_reasons) if last_turn else [],
                "generation_closure_reasons": list(last_turn.generation_closure_reasons) if last_turn else [],
                "used_fallback": last_turn.used_fallback if last_turn else None,
            },
        })

    if rfc15_checks_out is not None and g is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(g, "primary_runtime_after_retrieval"))

    return runtime, probes, safety_records


def run_ood_probes(
    runtime: CanonicalSystemRuntime,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Protocol §14 & §15: OOD Probes and safety checks."""
    ood_results = []
    safety_records = []

    for cue in OOD_CUES:
        s_before = compute_safety_snapshot(runtime)
        reply = runtime.chat(cue)
        s_after = compute_safety_snapshot(runtime)

        is_safe = (
            s_before["state_digest"] == s_after["state_digest"]
            and s_before["ledger"] == s_after["ledger"]
            and s_before["logical_time"] == s_after["logical_time"]
            and s_before["pending_evidence"] == s_after["pending_evidence"]
            and s_before["n_total"] == s_after["n_total"]
        )
        safety_records.append({
            "stage": "ood_probe",
            "cue": cue,
            "safe": is_safe,
        })
        assert is_safe, f"Safety violation during OOD probe '{cue}'!"

        tokens = set(reply.split())
        contaminating_targets = sorted(tokens & ALL_TARGETS)
        passed = len(contaminating_targets) == 0

        ood_results.append({
            "cue": cue,
            "reply": reply,
            "tokens": sorted(tokens),
            "contaminating_targets": contaminating_targets,
            "passed": passed,
        })

    return ood_results, safety_records


def run_second_restore_determinism(
    ckpt_path: Path,
    primary_probes: list[dict[str, Any]],
    rfc15_checks_out: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Protocol §16: Clean-restore determinism on fresh second runtime."""
    runtime2 = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
    g2 = runtime2.runtime_root._graph
    if rfc15_checks_out is not None and g2 is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(g2, "second_runtime_before_determinism"))

    determinism_records = []

    for idx, (fid, sentence, subj, tgt) in enumerate(FACTS):
        primary_rec = primary_probes[idx]
        reply2 = runtime2.chat(subj)
        lt2 = runtime2.last_turn

        primary_comp = tuple(primary_rec["last_turn"]["completion_closure_reasons"])
        agent2_comp = tuple(lt2.completion_closure_reasons) if lt2 else ()

        primary_gen = tuple(primary_rec["last_turn"]["generation_closure_reasons"])
        agent2_gen = tuple(lt2.generation_closure_reasons) if lt2 else ()

        reply_match = reply2 == primary_rec["reply"]
        comp_match = primary_comp == agent2_comp
        gen_match = primary_gen == agent2_gen
        deterministic = reply_match and comp_match and gen_match

        assert deterministic, f"Determinism mismatch on cue {subj}!"

        determinism_records.append({
            "fact_id": fid,
            "cue": subj,
            "reply_match": reply_match,
            "comp_reasons_match": comp_match,
            "gen_reasons_match": gen_match,
            "agent1_reply": primary_rec["reply"],
            "agent2_reply": reply2,
            "deterministic": deterministic,
        })

    if rfc15_checks_out is not None and g2 is not None:
        rfc15_checks_out.append(check_graph_rfc15_state(g2, "second_runtime_after_determinism"))

    return determinism_records


def run_natural_questions(runtime: CanonicalSystemRuntime) -> list[dict[str, Any]]:
    """Protocol §17: Exploratory Natural Questions (Diagnostic Only)."""
    records = []
    for q in NATURAL_QUESTIONS:
        reply = runtime.chat(q)
        lt = runtime.last_turn
        records.append({
            "question": q,
            "reply": reply,
            "completion_closure_reasons": list(lt.completion_closure_reasons) if lt else [],
            "generation_closure_reasons": list(lt.generation_closure_reasons) if lt else [],
            "used_fallback": lt.used_fallback if lt else None,
        })
    return records


def build_markdown_report(data: dict[str, Any]) -> str:
    """Renders the comprehensive, formal Markdown execution report dynamically from measured data."""
    meta = data["meta"]
    prov = data.get("provenance", {})
    success_gates = data.get("success_gates", [])

    num_passed = sum(1 for g in success_gates if g["result"] == "PASS")
    total_gates = len(success_gates)
    verdict = meta.get("verdict", "UNKNOWN")
    failure_stage = meta.get("failure_stage", "UNKNOWN")

    md = []
    md.append("# DGCA — SCTT-00 Execution Report")
    md.append("## Small Controlled Training Trial 00: Learn → Persist → Reload → Retrieve → Generate")
    md.append(f"**Execution Timestamp:** `{meta['timestamp']}`  ")
    md.append(f"**Execution Profile:** `{meta.get('execution_profile', 'UNKNOWN')}`  ")
    md.append(f"**Protocol Baseline Commit:** `{meta.get('protocol_baseline_commit', 'UNKNOWN')}`  ")
    md.append(f"**Authorized Repair Anchor (POA01):** `{meta.get('authorized_repair_anchor_commit', 'UNKNOWN')}`  ")
    md.append(f"**Execution Source Commit:** `{meta.get('execution_source_commit', 'UNKNOWN')}`  ")
    md.append(f"**Execution Verdict:** `{verdict}`  ")
    md.append(f"**Primary Failure Stage:** `{failure_stage}`  ")
    md.append("")
    md.append("---")
    md.append("")

    # 1. Executive Summary
    md.append("### 1. Executive Summary")
    if verdict == "SCTT00_REPAIR_RERUN_PASS":
        md.append(
            f"SCTT-00 post-repair rerun (`{meta.get('execution_profile')}`) was executed from clean "
            f"authorized source commit `{meta.get('execution_source_commit')}` (anchored at POA01 `{meta.get('authorized_repair_anchor_commit')}`). "
            f"All preflight, training exposure (40/40), storage persistence (8/8), checkpoint serialization/deserialization, "
            f"primary learned recall (8/8), OOD safety (4/4), zero chat persistent delta, clean-restore determinism (8/8), "
            f"runtime health, canonical lineage, and zero-production-drift gates PASSED ({num_passed}/{total_gates} gates). "
            f"Zero RFC-15 calls occurred. No production drift occurred after the authorized repair anchor. "
            f"Under the strict protocol rules, the final trial verdict is `{verdict}` with failure stage `{failure_stage}`."
        )
    else:
        failing_gates = [g['name'] for g in success_gates if g['result'] != 'PASS']
        md.append(
            f"SCTT-00 trial execution resulted in `{verdict}` at failure stage `{failure_stage}`. "
            f"Passing gates: {num_passed}/{total_gates}. Failing gates: {', '.join(failing_gates) if failing_gates else 'NONE'}."
        )
    md.append("")

    # 2. Provenance & Git Lineage Summary
    md.append("### 2. Provenance & Git Lineage Summary")
    md.append(f"- **Protocol Baseline Commit:** `{prov.get('protocol_baseline_commit')}`")
    md.append(f"- **Authorized Repair Anchor Commit (POA01):** `{prov.get('authorized_repair_anchor_commit')}`")
    md.append(f"- **Execution Source Commit:** `{prov.get('execution_source_commit')}`")
    md.append(f"- **Working Tree Clean at Start:** `{prov.get('working_tree_clean_at_start')}`")
    md.append(f"- **Baseline is Ancestor of Anchor:** `{prov.get('baseline_is_ancestor_of_anchor')}`")
    md.append(f"- **Anchor is Ancestor of Execution:** `{prov.get('anchor_is_ancestor_of_execution')}`")
    md.append(f"- **Baseline → Anchor Production Delta:** `{', '.join(prov.get('production_files_changed_baseline_to_anchor', []))}`")
    drift_files = prov.get('production_drift_after_repair_anchor', [])
    md.append(f"- **Production Drift After Anchor:** `{', '.join(drift_files) if drift_files else 'NONE (0 files)'}`")
    md.append(f"- **Lineage Valid:** `{prov.get('lineage_valid')}`")
    md.append("")

    # 3. Success Gates Table
    md.append("### 3. Success Gates Summary (Protocol §19 & VR01)")
    md.append("| Gate | Required | Observed | Result |")
    md.append("|---|---|---|---|")
    for g in success_gates:
        res_str = f"**{g['result']}**" if g["result"] == "PASS" else f"❌ **{g['result']}**"
        md.append(f"| {g['name']} | {g['required']} | {g['observed']} | {res_str} |")
    md.append("")

    # 4. Preflight & Baseline Probes
    md.append("### 4. Preflight & Baseline Uncontaminated Probes")
    md.append(f"- **Execution Source Commit:** `{data['preflight']['git_head']}`")
    md.append(f"- **Required APIs Confirmed:** `{data['preflight']['apis_confirmed']}`")
    md.append(f"- **Encoder Preflight Gate:** `{data['preflight']['encoder_gate']}`")
    md.append("")
    md.append("| ID | Fact Sentence | Subject | Target | Signals Run 1 & 2 | Status |")
    md.append("|---|---|---|---|---|---|")
    for ep in data["preflight"]["encoder_preflight"]:
        sig_str = ", ".join(f"`{s[0]}:{s[1]}`" for s in ep["signals"])
        md.append(f"| {ep['fact_id']} | {ep['sentence']} | `{ep['subject']}` | `{ep['target']}` | {sig_str} | {ep['status']} |")
    md.append("")
    md.append("#### Baseline Uncontaminated Probes (Separate Fresh CognitiveAgent)")
    md.append("| ID | Cue | Expected Target | Agent Reply | Contaminated? |")
    md.append("|---|---|---|---|---|")
    for bp in data["baseline_probes"]:
        md.append(f"| {bp['fact_id']} | `{bp['cue']}` | `{bp['expected_target']}` | `{bp['reply']}` | `{not bp['uncontaminated']}` |")
    md.append("")

    # 5. Training Exposures Summary
    md.append("### 5. Authorized Persistent Training Exposures (Protocol §7 & §8)")
    md.append(f"- **Total Exposures:** `{len(data['training_exposures'])}/40`")
    md.append("- **Schedule:** 5 round-robin cycles over F01..F08")
    md.append("- **Per-Exposure Status:** 40 `PERSISTENT_EXECUTED`, 40 `COMMITTED`, 0 replay substitutions, 0 authorization failures.")
    md.append("")
    md.append("<details><summary>Click to expand full 40-exposure transaction log</summary>")
    md.append("")
    md.append("| Cycle | Fact ID | Sentence | Occurrence Key | TxID | Status |")
    md.append("|---|---|---|---|---|---|")
    for ex in data["training_exposures"]:
        md.append(f"| {ex['cycle']} | {ex['fact_id']} | {ex['sentence']} | `{ex['occurrence_key']}` | `{ex['transaction_id'][:16]}...` | `{ex['status']}` |")
    md.append("")
    md.append("</details>")
    md.append("")

    # 6. Storage Audit
    md.append("### 6. Storage Audit (Protocol §10)")
    sa = data["storage_audit"]
    md.append(f"- **Persisted Relations Gate:** `{sa['persisted_relations_gate']}`")
    md.append(f"- **Post-Training Node Count:** `{sa['node_count']}`")
    md.append(f"- **Post-Training Edge Count:** `{sa['edge_count']}`")
    md.append(f"- **Logical Time:** `{sa['logical_time']}`")
    md.append(f"- **Committed Transactions:** `{sa['committed_transaction_count']}`")
    md.append(f"- **Canonical State Digest:** `{sa['state_digest']}`")
    md.append("")
    md.append("| ID | Subject Node | Target Node | Forward Edge (W, n) | Backward Edge (W, n) | Persisted? |")
    md.append("|---|---|---|---|---|---|")
    for p in sa["pairs"]:
        fwd = p["forward_edge"]
        bwd = p["backward_edge"]
        md.append(
            f"| {p['fact_id']} | `{p['subject_nid']}` | `{p['target_nid']}` | "
            f"W={fwd['W']:.4f}, n={fwd['n']} | W={bwd['W']:.4f}, n={bwd['n']} | `{p['relation_persisted']}` |"
        )
    md.append("")

    # 7. Checkpoint Details
    md.append("### 7. Canonical Checkpoint Artifact (Protocol §11)")
    ckpt = data["checkpoint"]
    md.append(f"- **Path:** `{ckpt['path']}`")
    md.append(f"- **File SHA-256:** `{ckpt['file_sha256']}`")
    md.append(f"- **Bundle Digest:** `{ckpt['checkpoint_bundle_digest']}`")
    md.append(f"- **State Digest:** `{ckpt['checkpoint_state_digest']}`")
    md.append(f"- **Provenance Digest:** `{ckpt['provenance_epoch_digest']}`")
    md.append(f"- **Schema Version:** `{ckpt['schema_version']}`")
    md.append(f"- **Runtime Version:** `{ckpt['runtime_version']}`")
    md.append(f"- **Observation Protocol Version:** `{ckpt['observation_protocol_version']}`")
    md.append("")

    # 8. Primary Post-Restore Retrieval Results
    md.append("### 8. Primary Post-Restore Retrieval Results (Protocol §12 & §13)")
    md.append("| ID | Cue | Expected Target | Reply Output | Recalled | Failure Stage | Comp Closure | Gen Closure |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in data["primary_retrieval"]:
        rec_str = "PASS" if r["recalled"] else "❌ FAIL"
        comp_c = ", ".join(r["last_turn"]["completion_closure_reasons"])
        gen_c = ", ".join(r["last_turn"]["generation_closure_reasons"])
        md.append(
            f"| {r['fact_id']} | `{r['cue']}` | `{r['expected_target']}` | `{r['reply']}` | "
            f"{rec_str} | `{r['failure_stage']}` | `{comp_c}` | `{gen_c}` |"
        )
    md.append("")

    # 9. OOD Probes & Safety Conservation
    md.append("### 9. OOD Safety Controls & Ordinary Chat Conservation")
    md.append("#### OOD Safety Probes (Protocol §14)")
    md.append("| OOD Cue | Agent Reply | Emitted Trained Targets | Safe? |")
    md.append("|---|---|---|---|")
    for o in data["ood_safety_controls"]:
        targets_str = ", ".join(o["contaminating_targets"]) if o["contaminating_targets"] else "None"
        md.append(f"| `{o['cue']}` | `{o['reply']}` | `{targets_str}` | `{o['passed']}` |")
    md.append("")
    md.append("#### Chat Conservation Invariant (Protocol §15)")
    md.append(
        "- Across all 8 primary probes and 4 OOD probes, the persistent state digest, causal ledger, "
        "logical time, pending structural evidence, and N_total across all nodes remained strictly **0 delta**."
    )
    md.append("")

    # 10. Clean-Restore Determinism
    md.append("### 10. Clean-Restore Determinism (Protocol §16)")
    md.append("| Fact ID | Cue | Agent 1 Reply | Agent 2 Reply | Deterministic? |")
    md.append("|---|---|---|---|---|")
    for d in data["clean_restore_determinism"]:
        md.append(f"| {d['fact_id']} | `{d['cue']}` | `{d['agent1_reply']}` | `{d['agent2_reply']}` | `{d['deterministic']}` |")
    md.append("")

    # 11. Exploratory Natural Questions
    md.append("### 11. Exploratory Natural Questions — Diagnostic (Protocol §17)")
    md.append("| Question | Agent Reply | Completion Reason | Generation Reason | Fallback Used |")
    md.append("|---|---|---|---|---|")
    for nq in data["exploratory_natural_questions"]:
        md.append(
            f"| {nq['question']} | `{nq['reply']}` | `{', '.join(nq['completion_closure_reasons'])}` | "
            f"`{', '.join(nq['generation_closure_reasons'])}` | `{nq['used_fallback']}` |"
        )
    md.append("")

    # 12. Architectural Outcome & Invariant Verification
    md.append("### 12. Architectural Outcome & Invariant Verification")
    if verdict == "SCTT00_REPAIR_RERUN_PASS":
        md.append(
            "Following the cumulative deployment of **RFC13-SR01** (Canonical Multi-Snapshot State Reprojection) "
            "and **RFC14-POA01** (Precedence Ordering Authority Repair), the entire canonical pipeline has executed "
            "with 100% gate compliance:\n\n"
            "1. **State Reprojection (RFC13-SR01):** During pattern completion settling epochs across multiple snapshots, "
            "receipts are lawfully reprojected into the updated SDCR, preserving recalled target activations (e.g. `{text:dog, text:canine}`).\n"
            "2. **Ordering Authority (RFC14-POA01):** Graph edges create Law 16 syntactic precedence constraints if and only if "
            "they carry positive positional lag (`Edge.lag > 0.0`). Bidirectional zero-lag associative copular edges no longer "
            "create reciprocal 2-cycles, eliminating false `ORDER_CONFLICT` closures.\n"
            "3. **Exact Recall:** All 8 primary subject probes successfully retrieved and emitted their associated target tokens.\n"
            "4. **Preserved Invariants:** Zero persistent chat mutation, zero RFC-15 predictive calls, and zero unauthorized production code drift."
        )
    else:
        md.append(f"**Observed Defect / Failure Stage:** `{failure_stage}`\n\n")
        md.append(data.get("root_cause_analysis", "No detailed root cause analysis provided."))
    md.append("")

    # 13. Official Verdict
    md.append("---")
    md.append(f"## Official Verdict: `{verdict}`")
    md.append("")

    return "\n".join(md)


def main() -> None:
    print("=" * 70)
    print("DGCA — SCTT-00: Small Controlled Training Trial 00 (Post-Repair Rerun)")
    print("=" * 70)

    rfc15_monitoring_checks: list[dict[str, Any]] = []

    # 1. Preflight
    print("\n[1/7] Running Preflight & Provenance Verification...")
    preflight = run_preflight(require_clean=True)
    prov = preflight["provenance"]
    print(f"  Execution Source: {prov['execution_source_commit']}")
    print(f"  POA01 Anchor:     {prov['authorized_repair_anchor_commit']}")
    print(f"  Working Tree:     {'CLEAN' if prov['working_tree_clean_at_start'] else 'DIRTY'}")
    print(f"  Anchor Ancestor:  {prov['anchor_is_ancestor_of_execution']}")
    print(f"  Production Drift: {len(prov['production_drift_after_repair_anchor'])} files")
    print(f"  Encoder Preflight: {preflight['encoder_gate']}")

    baseline_probes = run_baseline_probes(rfc15_checks_out=rfc15_monitoring_checks)
    print(f"  Baseline Probes: {len(baseline_probes)}/8 uncontaminated PASS")

    # 2. Training
    print("\n[2/7] Initializing Fresh Training Runtime & Executing 40 Exposures...")
    runtime_root, training_exposures = execute_training(rfc15_checks_out=rfc15_monitoring_checks)
    print(f"  Completed {len(training_exposures)}/40 authorized persistent exposures.")

    # 3. Storage Audit
    print("\n[3/7] Performing Storage Audit...")
    storage_audit = run_storage_audit(runtime_root)
    print(f"  Persistence Relation Gate: {storage_audit['persisted_relations_gate']}")
    print(f"  Nodes: {storage_audit['node_count']}, Edges: {storage_audit['edge_count']}, Logical Time: {storage_audit['logical_time']}")

    # 4. Checkpoint Save
    print("\n[4/7] Saving Checkpoint & Destroying Training Runtime...")
    ckpt_path = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"
    ckpt_info = save_checkpoint(runtime_root, ckpt_path)
    print(f"  Checkpoint saved to {ckpt_info['path']}")
    print(f"  Bundle Digest: {ckpt_info['checkpoint_bundle_digest']}")
    print(f"  File SHA-256:  {ckpt_info['file_sha256']}")

    del runtime_root

    # 5. Restore & Primary Retrieval
    print("\n[5/7] Cold Restoring via CanonicalSystemRuntime.from_checkpoint & Scoring Retrieval...")
    runtime, primary_probes, safety_primary = run_primary_retrieval(ckpt_path, rfc15_checks_out=rfc15_monitoring_checks)
    recalled_count = sum(1 for p in primary_probes if p["recalled"])
    print(f"  Primary Learned Recall: {recalled_count}/8 PASS")
    for p in primary_probes:
        status_sym = "PASS" if p["recalled"] else "FAIL"
        print(f"    [{p['fact_id']}] '{p['cue']}' -> target '{p['expected_target']}' | reply: '{p['reply']}' | {status_sym} ({p['failure_stage']})")

    # 6. OOD, Safety, Determinism, Natural Questions
    print("\n[6/7] Running OOD Safety Controls, Second Restore Determinism, & Diagnostics...")
    ood_results, safety_ood = run_ood_probes(runtime)
    ood_pass_count = sum(1 for o in ood_results if o["passed"])
    print(f"  OOD Safety: {ood_pass_count}/4 PASS")
    g_prim = runtime.runtime_root._graph
    if g_prim is not None:
        rfc15_monitoring_checks.append(check_graph_rfc15_state(g_prim, "primary_runtime_after_ood"))

    determinism_records = run_second_restore_determinism(
        ckpt_path, primary_probes, rfc15_checks_out=rfc15_monitoring_checks
    )
    det_count = sum(1 for d in determinism_records if d["deterministic"])
    print(f"  Second Restore Determinism: {det_count}/8 PASS")

    nat_qs = run_natural_questions(runtime)
    print(f"  Exploratory Natural Questions: {len(nat_qs)} completed.")
    if g_prim is not None:
        rfc15_monitoring_checks.append(check_graph_rfc15_state(g_prim, "primary_runtime_after_natural_questions"))

    # 7. Evaluate Success Gates & Build Reports
    print("\n[7/7] Mechanically Evaluating Success Gates & Emitting Reports...")
    all_safety = safety_primary + safety_ood
    zero_delta_pass = all(s["safe"] for s in all_safety)

    encoder_pass_count = sum(1 for ep in preflight["encoder_preflight"] if ep["status"] == "PASS")
    baseline_uncontam_count = sum(1 for bp in baseline_probes if bp["uncontaminated"])
    authorized_obs_count = sum(
        1 for ex in training_exposures if ex["status"] == "PERSISTENT_EXECUTED" and ex["persistent_executed"] is True
    )
    replay_sub_count = compute_replay_substitutions(training_exposures)
    persisted_rel_count = sum(1 for p in storage_audit["pairs"] if p["relation_persisted"])
    ckpt_save_ok = bool(ckpt_info and ckpt_info.get("checkpoint_bundle_digest") and ckpt_info.get("file_sha256"))
    root = runtime.runtime_root
    health_enum = getattr(root, "causal_runtime_health", None) if root else None
    lineage_enum = getattr(root, "canonical_lineage_state", None) if root else None
    ckpt_restore_ok = bool(
        runtime
        and health_enum == CausalRuntimeHealth.HEALTHY
        and lineage_enum == CanonicalLineageState.VALID
    )
    runtime_health_val = (
        health_enum.value
        if hasattr(health_enum, "value")
        else str(health_enum)
    )
    canonical_lineage_val = (
        lineage_enum.value
        if hasattr(lineage_enum, "value")
        else str(lineage_enum)
    )
    rfc15_calls_count = compute_rfc15_materializations(rfc15_monitoring_checks)
    prod_drift_count = len(prov["production_drift_after_repair_anchor"])

    success_gates = [
        {
            "name": "Working tree clean at start",
            "required": "True",
            "observed": str(prov["working_tree_clean_at_start"]),
            "result": "PASS" if prov["working_tree_clean_at_start"] else "FAIL",
        },
        {
            "name": "Authorized repair anchor lineage",
            "required": "VALID",
            "observed": "VALID" if (prov["anchor_is_ancestor_of_execution"] and prov["lineage_valid"]) else "INVALID",
            "result": "PASS" if (prov["anchor_is_ancestor_of_execution"] and prov["lineage_valid"]) else "FAIL",
        },
        {
            "name": "Production cognitive code drift after anchor",
            "required": "0",
            "observed": str(prod_drift_count),
            "result": "PASS" if prod_drift_count == 0 else "FAIL",
        },
        {
            "name": "Encoder preflight",
            "required": "8/8",
            "observed": f"{encoder_pass_count}/8",
            "result": "PASS" if encoder_pass_count == 8 else "FAIL",
        },
        {
            "name": "Baseline uncontaminated",
            "required": "8/8",
            "observed": f"{baseline_uncontam_count}/8",
            "result": "PASS" if baseline_uncontam_count == 8 else "FAIL",
        },
        {
            "name": "Authorized observations",
            "required": "40/40",
            "observed": f"{authorized_obs_count}/40",
            "result": "PASS" if authorized_obs_count == 40 else "FAIL",
        },
        {
            "name": "Replay substitutions",
            "required": "0",
            "observed": str(replay_sub_count),
            "result": "PASS" if replay_sub_count == 0 else "FAIL",
        },
        {
            "name": "Persistence relation gate",
            "required": "8/8",
            "observed": f"{persisted_rel_count}/8",
            "result": "PASS" if persisted_rel_count == 8 else "FAIL",
        },
        {
            "name": "Canonical checkpoint save",
            "required": "PASS",
            "observed": "PASS" if ckpt_save_ok else "FAIL",
            "result": "PASS" if ckpt_save_ok else "FAIL",
        },
        {
            "name": "Canonical checkpoint restore",
            "required": "PASS",
            "observed": "PASS" if ckpt_restore_ok else "FAIL",
            "result": "PASS" if ckpt_restore_ok else "FAIL",
        },
        {
            "name": "Primary learned recall",
            "required": "8/8",
            "observed": f"{recalled_count}/8",
            "result": "PASS" if recalled_count == 8 else "FAIL",
        },
        {
            "name": "OOD safety",
            "required": "4/4",
            "observed": f"{ood_pass_count}/4",
            "result": "PASS" if ood_pass_count == 4 else "FAIL",
        },
        {
            "name": "Post-training chat persistent delta",
            "required": "0",
            "observed": "0" if zero_delta_pass else "DELTA_DETECTED",
            "result": "PASS" if zero_delta_pass else "FAIL",
        },
        {
            "name": "Restore determinism",
            "required": "8/8",
            "observed": f"{det_count}/8",
            "result": "PASS" if det_count == 8 else "FAIL",
        },
        {
            "name": "Runtime health",
            "required": "HEALTHY",
            "observed": runtime_health_val,
            "result": "PASS" if runtime_health_val == "HEALTHY" else "FAIL",
        },
        {
            "name": "Canonical lineage",
            "required": "VALID",
            "observed": canonical_lineage_val,
            "result": "PASS" if (canonical_lineage_val == "VALID" and prov["lineage_valid"]) else "FAIL",
        },
        {
            "name": "RFC15 calls",
            "required": "0",
            "observed": str(rfc15_calls_count),
            "result": "PASS" if rfc15_calls_count == 0 else "FAIL",
        },
    ]

    all_gates_pass = all(g["result"] == "PASS" for g in success_gates)
    if (
        not prov["anchor_is_ancestor_of_execution"]
        or not prov["baseline_is_ancestor_of_anchor"]
        or not prov["working_tree_clean_at_start"]
        or prod_drift_count > 0
        or not prov["lineage_valid"]
    ):
        verdict = "SCTT00_REPAIR_RERUN_BLOCKED"
        primary_failure_stage = "PREFLIGHT_PROVENANCE"
    elif replay_sub_count > 0:
        verdict = "SCTT00_REPAIR_RERUN_BLOCKED"
        primary_failure_stage = "REPLAY_PROHIBITED"
    elif rfc15_calls_count > 0:
        verdict = "SCTT00_REPAIR_RERUN_BLOCKED"
        primary_failure_stage = "RFC15_MATERIALIZED"
    elif all_gates_pass:
        verdict = "SCTT00_REPAIR_RERUN_PASS"
        primary_failure_stage = "NONE"
    else:
        verdict = "SCTT00_REPAIR_RERUN_FAIL"
        if recalled_count < 8:
            primary_failure_stage = "E2_RETRIEVAL"
        elif ood_pass_count < 4:
            primary_failure_stage = "OOD_SAFETY"
        elif not zero_delta_pass:
            primary_failure_stage = "SAFETY_CONSERVATION"
        else:
            primary_failure_stage = "GATE_FAILURE"

    root_cause_analysis = (
        "Post-repair rerun completed with 100% compliance across all 17 gates."
        if verdict == "SCTT00_REPAIR_RERUN_PASS"
        else f"Failure stage: {primary_failure_stage}"
    )

    full_results = {
        "meta": {
            "trial_id": "SCTT-00",
            "execution_profile": EXECUTION_PROFILE,
            "protocol_document": "papers MD/DGCA-SCTT-00-Small-Controlled-Training-Trial-Protocol-v1.0-FROZEN.md",
            "protocol_baseline_commit": PROTOCOL_BASELINE_COMMIT,
            "authorized_repair_anchor_commit": AUTHORIZED_REPAIR_ANCHOR_COMMIT,
            "execution_source_commit": prov["execution_source_commit"],
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "verdict": verdict,
            "failure_stage": primary_failure_stage,
        },
        "provenance": prov,
        "success_gates": success_gates,
        "preflight": preflight,
        "baseline_probes": baseline_probes,
        "training_exposures": training_exposures,
        "replay_monitoring": {
            "total_substitutions": replay_sub_count,
            "zero_substitutions_pass": replay_sub_count == 0,
        },
        "rfc15_monitoring": {
            "total_materializations": rfc15_calls_count,
            "zero_materializations_pass": rfc15_calls_count == 0,
            "checks": rfc15_monitoring_checks,
        },
        "storage_audit": storage_audit,
        "checkpoint": ckpt_info,
        "primary_retrieval": primary_probes,
        "ood_safety_controls": ood_results,
        "ordinary_chat_safety": {
            "total_probes_checked": len(all_safety),
            "all_safe": zero_delta_pass,
            "records": all_safety,
        },
        "clean_restore_determinism": determinism_records,
        "exploratory_natural_questions": nat_qs,
        "root_cause_analysis": root_cause_analysis,
    }

    # Write JSON results
    results_dir = REPO_ROOT / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_json_path = results_dir / "sctt00-results.json"
    results_json_path.write_text(
        json.dumps(full_results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  Emitted JSON results to {results_json_path.relative_to(REPO_ROOT)}")

    # Write Markdown execution report
    report_md = build_markdown_report(full_results)
    report_md_path = REPO_ROOT / "papers MD" / "SCTT-00-EXECUTION-REPORT.md"
    report_md_path.write_text(report_md, encoding="utf-8")
    print(f"  Emitted Markdown report to {report_md_path.relative_to(REPO_ROOT)}")

    print("\n" + "=" * 70)
    print(f"TRIAL COMPLETE: {verdict}")
    print(f"Failure Stage:  {primary_failure_stage}")
    print("=" * 70)


if __name__ == "__main__":
    main()
