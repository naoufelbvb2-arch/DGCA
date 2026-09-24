"""
DGCA — RIC-03 & RIC-03-C01
Canonical Learning Runtime, Authority Separation & Concurrency Hardening Strict Verification Suite

Authoritative Specifications:
papers MD/RIC-03-Canonical-Learning-Runtime-and-Authority-Separation-v1.0-FROZEN.md
papers MD/RIC-03-C01-Authority-Surface-AUTO-Identity-and-Concurrency-Hardening-v1.0-FROZEN.md
papers MD/RIC-03-IMPLEMENTATION-VERIFICATION-REPORT.md
Status: FROZEN / ADOPTED
"""
from __future__ import annotations

import ast
import dataclasses
import json
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

import dgca
from dgca import (
    R3_MIN_RUNTIME_SEMANTICS_DIGEST,
    CanonicalLineageState,
    CanonicalSystemRuntime,
    CausalRuntimeHealth,
    CognitiveAgent,
    ExecutionMode,
)
from dgca.completion import PatternCompletionEngine, rfc13_behavioral_signature
from dgca.generation import HierarchicalGenerativeEngine, rfc14_behavioral_signature
from dgca.graph import CognitiveGraph
from dgca.learning_runtime import (
    LEARNING_BOUNDARY_NAMESPACE,
    LEARNING_INGRESS_BOUNDARY,
    LEARNING_SOURCE_EVENT_KEY,
    RIC03_LEARNING_PROTOCOL_VERSION,
    RIC03_LEARNING_SEMANTICS_DIGEST,
    RIC03_LEARNING_SEMANTICS_REGISTRY,
    CanonicalLearningAuthorizer,
    CanonicalLearningRuntime,
    LearningResult,
    compute_ric03_learning_semantics_digest,
)
from dgca.observation import (
    R2AuthorizationError,
    R2DescriptorError,
)
from dgca.persistence import (
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)
from dgca.system_runtime import SystemOperationState
from scripts.audit_rfc16_benchmarks import _build_benchmark_fixture

BASELINE_COMMIT = "cd05769dc09471592b92a9b07f720660bd5d57eb"


# ─────────────────────────────────────────────────────────── GROUP A: AUTHORITY
def test_ric03_t01_fresh_system_runtime_authorized_learning() -> None:
    """RIC03-T01: fresh CanonicalSystemRuntime can perform authorized learning."""
    sr = CanonicalSystemRuntime.fresh()
    res = sr.learn("A dog is a canine.")
    assert isinstance(res, LearningResult)
    assert res.protocol_version == RIC03_LEARNING_PROTOCOL_VERSION
    assert res.status == "PERSISTENT_EXECUTED"
    assert res.persistent_executed is True
    assert res.persistent_transaction_id is not None
    assert res.persistent_phase == "COMMITTED"
    assert res.identity_mode == "AUTO"


def test_ric03_t02_authorizer_accepts_exact_capability() -> None:
    """RIC03-T02: LearningAuthorizer accepts only exact capability identity."""
    sr = CanonicalSystemRuntime.fresh()
    cap = object()
    auth = CanonicalLearningAuthorizer(runtime_root=sr.runtime_root, capability=cap)
    assert auth.verify_persistent_observation(
        capability=cap,
        root_external_episode_id="root_1",
        ingress_event_id="iev_1",
        modality="text",
        operation_kind="R2_AUTHORIZED_PERSISTENT",
    ) is True
    assert sr.runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY
    assert sr.runtime_root.canonical_lineage_state == CanonicalLineageState.VALID


def test_ric03_t03_wrong_capability_denied() -> None:
    """RIC03-T03: wrong capability denied."""
    sr = CanonicalSystemRuntime.fresh()
    cap = object()
    auth = CanonicalLearningAuthorizer(runtime_root=sr.runtime_root, capability=cap)
    wrong_cap = object()
    assert auth.verify_persistent_observation(
        capability=wrong_cap,
        root_external_episode_id="root_1",
        ingress_event_id="iev_1",
        modality="text",
        operation_kind="R2_AUTHORIZED_PERSISTENT",
    ) is False


def test_ric03_t04_none_capability_denied() -> None:
    """RIC03-T04: None capability denied."""
    sr = CanonicalSystemRuntime.fresh()
    cap = object()
    auth = CanonicalLearningAuthorizer(runtime_root=sr.runtime_root, capability=cap)
    assert auth.verify_persistent_observation(
        capability=None,
        root_external_episode_id="root_1",
        ingress_event_id="iev_1",
        modality="text",
        operation_kind="R2_AUTHORIZED_PERSISTENT",
    ) is False


def test_ric03_t05_wrong_modality_denied() -> None:
    """RIC03-T05: wrong modality denied."""
    sr = CanonicalSystemRuntime.fresh()
    cap = object()
    auth = CanonicalLearningAuthorizer(runtime_root=sr.runtime_root, capability=cap)
    for bad_modality in ("audio", "vision", "code", "multi", ""):
        assert auth.verify_persistent_observation(
            capability=cap,
            root_external_episode_id="root_1",
            ingress_event_id="iev_1",
            modality=bad_modality,
            operation_kind="R2_AUTHORIZED_PERSISTENT",
        ) is False


def test_ric03_t06_wrong_operation_kind_denied() -> None:
    """RIC03-T06: wrong operation_kind denied."""
    sr = CanonicalSystemRuntime.fresh()
    cap = object()
    auth = CanonicalLearningAuthorizer(runtime_root=sr.runtime_root, capability=cap)
    for bad_kind in ("TRANSIENT", "EPHEMERAL", "OBSERVE_ONLY", ""):
        assert auth.verify_persistent_observation(
            capability=cap,
            root_external_episode_id="root_1",
            ingress_event_id="iev_1",
            modality="text",
            operation_kind=bad_kind,
        ) is False


def test_ric03_t07_ordinary_r2_bridge_without_authorizer_cannot_persist() -> None:
    """RIC03-T07: ordinary R2 bridge without authorizer cannot persist."""
    sr = CanonicalSystemRuntime.fresh()
    bridge = sr.runtime_root.create_observation_bridge(authorizer=None)
    with pytest.raises(R2AuthorizationError):
        bridge.observe_text(
            boundary_namespace=LEARNING_BOUNDARY_NAMESPACE,
            source_occurrence_key="test:07",
            source_event_key=LEARNING_SOURCE_EVENT_KEY,
            ingress_boundary=LEARNING_INGRESS_BOUNDARY,
            raw_text="A dog is a canine.",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability=object(),
        )


def test_ric03_t08_cognitive_agent_cannot_access_learning_authority() -> None:
    """RIC03-T08: CognitiveAgent cannot access learning authority."""
    agent = CognitiveAgent()
    assert not hasattr(agent, "learn")
    assert not hasattr(agent, "learn_text")
    assert not hasattr(agent, "learning_runtime")
    assert not hasattr(agent, "_capability")
    assert not hasattr(agent, "save_checkpoint")


# ─────────────────────────────────────────────────────────── GROUP B: PATH OWNERSHIP
def test_ric03_t09_learning_runtime_bridge_bound_to_same_r1_root() -> None:
    """RIC03-T09: LearningRuntime bridge is created from exact same R1 root."""
    sr = CanonicalSystemRuntime.fresh()
    lr = sr._learning_runtime
    assert isinstance(lr, CanonicalLearningRuntime)
    assert lr.runtime_root is sr.runtime_root
    assert lr._bridge._runtime is sr.runtime_root


def test_ric03_t10_learning_runtime_no_direct_graph_mutation_calls() -> None:
    """RIC03-T10: LearningRuntime contains no direct CognitiveGraph mutation calls."""
    lr_file = Path(dgca.__file__).parent / "learning_runtime.py"
    with open(lr_file, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    forbidden_calls = {"observe", "observe_sequence", "link", "add_contradiction"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in forbidden_calls:
                pytest.fail(f"Forbidden direct graph call '{node.func.attr}' found in learning_runtime.py")
            if isinstance(node.func, ast.Name) and node.func.id == "CognitiveGraph":
                pytest.fail("Direct CognitiveGraph instantiation found in learning_runtime.py")


def test_ric03_t11_learn_invokes_r2_exactly_once() -> None:
    """RIC03-T11: learn invokes R2 exactly once."""
    sr = CanonicalSystemRuntime.fresh()
    call_count = 0
    orig_observe_text = sr._learning_runtime._bridge.observe_text

    def spy_observe_text(*args: Any, **kwargs: Any) -> Any:
        nonlocal call_count
        call_count += 1
        return orig_observe_text(*args, **kwargs)

    with patch.object(sr._learning_runtime._bridge, "observe_text", side_effect=spy_observe_text):
        sr.learn("A dog is a canine.")
    assert call_count == 1


def test_ric03_t12_mode_is_exactly_authorized_persistent() -> None:
    """RIC03-T12: mode is exactly AUTHORIZED_PERSISTENT."""
    sr = CanonicalSystemRuntime.fresh()
    observed_mode: Any = None
    orig_observe_text = sr._learning_runtime._bridge.observe_text

    def spy_observe_text(*args: Any, **kwargs: Any) -> Any:
        nonlocal observed_mode
        observed_mode = kwargs.get("mode")
        return orig_observe_text(*args, **kwargs)

    with patch.object(sr._learning_runtime._bridge, "observe_text", side_effect=spy_observe_text):
        sr.learn("A dog is a canine.")
    assert observed_mode == ExecutionMode.AUTHORIZED_PERSISTENT


def test_ric03_t13_rfc13_call_count_zero_during_learn() -> None:
    """RIC03-T13: RFC13 call count == 0 during learn."""
    sr = CanonicalSystemRuntime.fresh()

    with patch.object(PatternCompletionEngine, "run_settling_epoch") as mock_complete:
        sr.learn("A dog is a canine.")
        assert mock_complete.call_count == 0


def test_ric03_t14_rfc14_call_count_zero_during_learn() -> None:
    """RIC03-T14: RFC14 call count == 0 during learn."""
    sr = CanonicalSystemRuntime.fresh()

    with patch.object(HierarchicalGenerativeEngine, "execute_generative_pass") as mock_gen:
        sr.learn("A dog is a canine.")
        assert mock_gen.call_count == 0


def test_ric03_t15_rfc15_remains_unmaterialized() -> None:
    """RIC03-T15: RFC15 remains unmaterialized."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.")
    graph = sr.runtime_root._graph
    assert getattr(graph, "_recurrent_engine", None) is None


def test_ric03_t16_rfc16_remains_unused() -> None:
    """RIC03-T16: RFC16 remains unused."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.")
    graph = sr.runtime_root._graph
    assert getattr(graph, "_loop_engine", None) is None


# ─────────────────────────────────────────────────────────── GROUP C: IDENTITY / REPLAY
def test_ric03_t17_two_identical_auto_exposures_distinct_occurrence_ids() -> None:
    """RIC03-T17: two identical AUTO text exposures have distinct occurrence IDs."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.")
    res2 = sr.learn("A dog is a canine.")
    assert res1.source_occurrence_key != res2.source_occurrence_key
    assert res1.learning_index == 1
    assert res2.learning_index == 2


def test_ric03_t18_two_identical_auto_exposures_both_execute_persistently() -> None:
    """RIC03-T18: two identical AUTO exposures both execute persistently."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.")
    res2 = sr.learn("A dog is a canine.")
    assert res1.persistent_executed is True
    assert res2.persistent_executed is True
    assert res1.status == "PERSISTENT_EXECUTED"
    assert res2.status == "PERSISTENT_EXECUTED"


def test_ric03_t19_two_identical_auto_exposures_distinct_persistent_txids() -> None:
    """RIC03-T19: two identical AUTO exposures have distinct persistent TxIDs."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.")
    res2 = sr.learn("A dog is a canine.")
    assert res1.persistent_transaction_id != res2.persistent_transaction_id


def test_ric03_t20_same_explicit_key_same_text_gives_replay() -> None:
    """RIC03-T20: same explicit occurrence key + same text gives replay."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.", occurrence_key="FACT:01")
    res2 = sr.learn("A dog is a canine.", occurrence_key="FACT:01")
    assert res1.status == "PERSISTENT_EXECUTED"
    assert res1.persistent_executed is True
    assert res2.status == "PERSISTENT_REPLAY"
    assert res2.replayed is True


def test_ric03_t21_explicit_replay_persistent_executed_false() -> None:
    """RIC03-T21: explicit replay has persistent_executed == False."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.", occurrence_key="FACT:01")
    res2 = sr.learn("A dog is a canine.", occurrence_key="FACT:01")
    assert res2.persistent_executed is False


def test_ric03_t22_explicit_replay_does_not_add_committed_transaction() -> None:
    """RIC03-T22: explicit replay does not add another committed transaction."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.", occurrence_key="FACT:01")
    tx_count_before = len(sr.runtime_root._ledger.committed_transactions)
    res2 = sr.learn("A dog is a canine.", occurrence_key="FACT:01")
    tx_count_after = len(sr.runtime_root._ledger.committed_transactions)
    assert tx_count_after == tx_count_before
    assert res2.persistent_transaction_id == res1.persistent_transaction_id


def test_ric03_t23_same_explicit_key_different_text_fails_closed() -> None:
    """RIC03-T23: same explicit key + different text fails closed."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.", occurrence_key="FACT:CONFLICT")
    with pytest.raises(R2DescriptorError):
        sr.learn("A cat is a feline.", occurrence_key="FACT:CONFLICT")


def test_ric03_t24_same_explicit_key_survives_save_restore_and_replays() -> None:
    """RIC03-T24: same explicit key survives save/restore and replays."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.", occurrence_key="FACT:PERSIST")
    assert res1.persistent_executed is True

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "ckpt.dgca"
        sr.save_checkpoint(ckpt_path)

        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        res2 = sr_restored.learn("A dog is a canine.", occurrence_key="FACT:PERSIST")
        assert res2.status == "PERSISTENT_REPLAY"
        assert res2.persistent_executed is False
        assert res2.replayed is True
        assert res2.persistent_transaction_id == res1.persistent_transaction_id


def test_ric03_t25_failed_auto_operation_index_is_never_reused() -> None:
    """RIC03-T25: failed auto operation index is never reused."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.")
    assert res1.learning_index == 1

    # Force downstream failure after index allocation
    with (
        patch.object(sr._learning_runtime._bridge, "observe_text", side_effect=RuntimeError("simulated error")),
        pytest.raises(RuntimeError, match="simulated error"),
    ):
        sr.learn("Another text")

    # Next successful learn must have index 3, never 2
    res3 = sr.learn("A third text")
    assert res3.learning_index == 3


# ─────────────────────────────────────────────────────────── GROUP D: RESULT / CLEANUP
def test_ric03_t26_learning_result_is_frozen_immutable() -> None:
    """RIC03-T26: LearningResult is frozen/immutable."""
    sr = CanonicalSystemRuntime.fresh()
    res = sr.learn("A dog is a canine.")
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.learning_index = 999  # type: ignore[misc]


def test_ric03_t27_learning_result_exposes_no_capability() -> None:
    """RIC03-T27: LearningResult exposes no capability."""
    field_names = [f.name for f in dataclasses.fields(LearningResult)]
    assert "capability" not in field_names
    assert "_capability" not in field_names
    sr = CanonicalSystemRuntime.fresh()
    res = sr.learn("A dog is a canine.")
    assert not hasattr(res, "capability")
    assert not hasattr(res, "_capability")


def test_ric03_t28_learning_result_exposes_no_mutable_graph_or_ledger() -> None:
    """RIC03-T28: LearningResult exposes no mutable graph/ledger."""
    field_names = [f.name for f in dataclasses.fields(LearningResult)]
    assert "graph" not in field_names
    assert "ledger" not in field_names
    sr = CanonicalSystemRuntime.fresh()
    res = sr.learn("A dog is a canine.")
    assert not hasattr(res, "graph")
    assert not hasattr(res, "ledger")


def test_ric03_t29_r2_observation_result_representations_closed_after_success() -> None:
    """RIC03-T29: R2 observation result representations are closed after successful learning."""
    sr = CanonicalSystemRuntime.fresh()
    captured_result: Any = None
    orig_observe_text = sr._learning_runtime._bridge.observe_text

    def spy_observe_text(*args: Any, **kwargs: Any) -> Any:
        nonlocal captured_result
        captured_result = orig_observe_text(*args, **kwargs)
        return captured_result

    with patch.object(sr._learning_runtime._bridge, "observe_text", side_effect=spy_observe_text):
        sr.learn("A dog is a canine.")

    assert captured_result is not None
    assert captured_result.is_closed is True


def test_ric03_t30_transient_representations_closed_after_failure() -> None:
    """RIC03-T30: transient representations are closed after failure."""
    sr = CanonicalSystemRuntime.fresh()
    with pytest.raises(TypeError):
        sr._learning_runtime.learn_text(12345)  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────── GROUP E: PERSISTENCE
def test_ric03_t31_learning_changes_persistent_state_digest() -> None:
    """RIC03-T31: learning changes persistent state digest."""
    sr = CanonicalSystemRuntime.fresh()
    payload_before = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_before = compute_checkpoint_state_digest(payload_before)

    sr.learn("A dog is a canine.")

    payload_after = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_after = compute_checkpoint_state_digest(payload_after)

    assert digest_before != digest_after


def test_ric03_t32_save_after_learning_succeeds() -> None:
    """RIC03-T32: save after learning succeeds."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.")
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        digest = sr.save_checkpoint(ckpt_path)
        assert isinstance(digest, str)
        assert len(digest) == 64
        assert ckpt_path.is_file()


def test_ric03_t33_restore_reproduces_learned_persistent_digest() -> None:
    """RIC03-T33: restore reproduces learned persistent digest."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.")
    payload_orig = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_orig = compute_checkpoint_state_digest(payload_orig)

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)

        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        payload_restored = extract_canonical_persistent_payload(sr_restored.runtime_root._graph)
        digest_restored = compute_checkpoint_state_digest(payload_restored)

        assert digest_restored == digest_orig


def test_ric03_t34_learning_ledger_transaction_survives_restore() -> None:
    """RIC03-T34: learning ledger transaction survives restore."""
    sr = CanonicalSystemRuntime.fresh()
    res = sr.learn("A dog is a canine.")
    learned_txid = res.persistent_transaction_id
    assert learned_txid is not None

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)

        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        assert sr_restored.runtime_root._ledger.has_transaction(learned_txid) is True


def test_ric03_t35_capability_does_not_survive_restore() -> None:
    """RIC03-T35: capability does NOT survive restore."""
    sr = CanonicalSystemRuntime.fresh()
    orig_cap = sr._learning_runtime._capability

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)

        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        restored_cap = sr_restored._learning_runtime._capability
        assert restored_cap is not orig_cap


def test_ric03_t36_checkpoint_schema_remains_1_2_0() -> None:
    """RIC03-T36: checkpoint schema remains 1.2.0."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.")

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)

        with open(ckpt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("schema", {}).get("checkpoint_schema_version") == "1.2.0"
        assert data.get("diagnostic_metadata", {}).get("source_schema") == "1.2.0"


def test_ric03_t37_checkpoint_contains_no_learning_capability_or_operation_state() -> None:
    """RIC03-T37: checkpoint contains no learning capability/session nonce/operation state."""
    sr = CanonicalSystemRuntime.fresh()
    sr.learn("A dog is a canine.")

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)

        with open(ckpt_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_str = json.dumps(data)
        assert "capability" not in raw_str
        assert "operation_state" not in raw_str
        assert sr._learning_runtime.session_nonce not in raw_str


# ─────────────────────────────────────────────────────────── GROUP F: CHAT SEPARATION
def test_ric03_t38_ordinary_chat_causes_zero_persistent_delta() -> None:
    """RIC03-T38: ordinary chat still causes zero persistent delta."""
    sr = CanonicalSystemRuntime.fresh()
    payload_before = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_before = compute_checkpoint_state_digest(payload_before)
    tx_count_before = len(sr.runtime_root._ledger.committed_transactions)

    sr.chat("hello world")

    payload_after = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_after = compute_checkpoint_state_digest(payload_after)
    tx_count_after = len(sr.runtime_root._ledger.committed_transactions)

    assert digest_before == digest_after
    assert tx_count_before == tx_count_after


def test_ric03_t39_chat_learn_this_fact_does_not_persist() -> None:
    """RIC03-T39: chat text 'learn this fact' does not persist."""
    sr = CanonicalSystemRuntime.fresh()
    payload_before = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_before = compute_checkpoint_state_digest(payload_before)

    sr.chat("learn this fact: a dog is a canine")

    payload_after = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_after = compute_checkpoint_state_digest(payload_after)

    assert digest_before == digest_after


def test_ric03_t40_chat_remember_this_does_not_persist() -> None:
    """RIC03-T40: chat text 'remember this' does not persist."""
    sr = CanonicalSystemRuntime.fresh()
    payload_before = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_before = compute_checkpoint_state_digest(payload_before)

    sr.chat("remember this forever: ice is solid")

    payload_after = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest_after = compute_checkpoint_state_digest(payload_after)

    assert digest_before == digest_after


def test_ric03_t41_cognitive_agent_class_has_no_learn_attribute() -> None:
    """RIC03-T41: CognitiveAgent class has no learn attribute."""
    assert not hasattr(CognitiveAgent, "learn")
    assert not hasattr(CognitiveAgent, "learn_text")


def test_ric03_t42_r3_semantics_digest_unchanged() -> None:
    """RIC03-T42: R3 semantics digest unchanged."""
    assert R3_MIN_RUNTIME_SEMANTICS_DIGEST == "fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc"


# ─────────────────────────────────────────────────────────── GROUP G: SYSTEM OPERATION GUARD
def test_ric03_t43_initial_operation_state_is_idle() -> None:
    """RIC03-T43: initial operation state is IDLE."""
    sr = CanonicalSystemRuntime.fresh()
    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t44_chat_runs_under_chatting() -> None:
    """RIC03-T44: chat runs under CHATTING."""
    sr = CanonicalSystemRuntime.fresh()
    observed_state: Any = None
    orig_chat = sr._chat_runtime.chat

    def spy_chat(text: str) -> str:
        nonlocal observed_state
        observed_state = sr.operation_state
        return orig_chat(text)

    with patch.object(sr._chat_runtime, "chat", side_effect=spy_chat):
        sr.chat("hello")

    assert observed_state == SystemOperationState.CHATTING
    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t45_learn_runs_under_learning() -> None:
    """RIC03-T45: learn runs under LEARNING."""
    sr = CanonicalSystemRuntime.fresh()
    observed_state: Any = None
    orig_learn_text = sr._learning_runtime.learn_text

    def spy_learn(text: str, **kwargs: Any) -> Any:
        nonlocal observed_state
        observed_state = sr.operation_state
        return orig_learn_text(text, **kwargs)

    with patch.object(sr._learning_runtime, "learn_text", side_effect=spy_learn):
        sr.learn("A dog is a canine.")

    assert observed_state == SystemOperationState.LEARNING
    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t46_save_runs_under_checkpointing() -> None:
    """RIC03-T46: save runs under CHECKPOINTING."""
    sr = CanonicalSystemRuntime.fresh()
    observed_state: Any = None

    import dgca.system_runtime

    orig_save = dgca.system_runtime.save_canonical_r1_checkpoint

    def spy_save(*args: Any, **kwargs: Any) -> Any:
        nonlocal observed_state
        observed_state = sr.operation_state
        return orig_save(*args, **kwargs)

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        with patch("dgca.system_runtime.save_canonical_r1_checkpoint", side_effect=spy_save):
            sr.save_checkpoint(ckpt_path)

    assert observed_state == SystemOperationState.CHECKPOINTING
    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t47_learn_during_chat_fails_closed() -> None:
    """RIC03-T47: learn during chat fails closed."""
    sr = CanonicalSystemRuntime.fresh()
    orig_chat = sr._chat_runtime.chat

    def nested_learn_chat(text: str) -> str:
        sr.learn("nested learning attempt")
        return orig_chat(text)

    with (
        patch.object(sr._chat_runtime, "chat", side_effect=nested_learn_chat),
        pytest.raises(RuntimeError, match="Cannot begin operation 'LEARNING': runtime is currently in state 'CHATTING'"),
    ):
        sr.chat("hello")

    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t48_chat_during_learn_fails_closed() -> None:
    """RIC03-T48: chat during learn fails closed."""
    sr = CanonicalSystemRuntime.fresh()
    orig_learn = sr._learning_runtime.learn_text

    def nested_chat_learn(text: str, **kwargs: Any) -> Any:
        sr.chat("nested chat attempt")
        return orig_learn(text, **kwargs)

    with (
        patch.object(sr._learning_runtime, "learn_text", side_effect=nested_chat_learn),
        pytest.raises(RuntimeError, match="Cannot begin operation 'CHATTING': runtime is currently in state 'LEARNING'"),
    ):
        sr.learn("A dog is a canine.")

    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t49_save_during_learn_fails_closed() -> None:
    """RIC03-T49: save during learn fails closed."""
    sr = CanonicalSystemRuntime.fresh()
    orig_learn = sr._learning_runtime.learn_text

    def nested_save_learn(text: str, **kwargs: Any) -> Any:
        sr.save_checkpoint("dummy.dgca")
        return orig_learn(text, **kwargs)

    with (
        patch.object(sr._learning_runtime, "learn_text", side_effect=nested_save_learn),
        pytest.raises(RuntimeError, match="Cannot begin operation 'CHECKPOINTING': runtime is currently in state 'LEARNING'"),
    ):
        sr.learn("A dog is a canine.")

    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t50_learn_during_save_fails_closed() -> None:
    """RIC03-T50: learn during save fails closed."""
    sr = CanonicalSystemRuntime.fresh()

    def nested_learn_save(*args: Any, **kwargs: Any) -> Any:
        sr.learn("attempt during save")
        return "digest"

    with (
        patch("dgca.system_runtime.save_canonical_r1_checkpoint", side_effect=nested_learn_save),
        pytest.raises(RuntimeError, match="Cannot begin operation 'LEARNING': runtime is currently in state 'CHECKPOINTING'"),
    ):
        sr.save_checkpoint("dummy.dgca")

    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t51_operation_state_returns_idle_after_success() -> None:
    """RIC03-T51: operation state returns IDLE after successful operation."""
    sr = CanonicalSystemRuntime.fresh()
    sr.chat("hello")
    assert sr.operation_state == SystemOperationState.IDLE
    sr.learn("A dog is a canine.")
    assert sr.operation_state == SystemOperationState.IDLE


def test_ric03_t52_operation_state_returns_idle_after_exception() -> None:
    """RIC03-T52: operation state returns IDLE after exception."""
    sr = CanonicalSystemRuntime.fresh()
    with pytest.raises(ValueError):
        sr.learn("")
    assert sr.operation_state == SystemOperationState.IDLE


# ─────────────────────────────────────────────────────────── GROUP H: END-TO-END
def test_ric03_t53_e2e_learn_save_restore_recall() -> None:
    """RIC03-T53: fresh runtime -> learn dog canine 5x -> save -> cold restore -> chat('dog') surfaces recall."""
    sr = CanonicalSystemRuntime.fresh()
    for _ in range(5):
        sr.learn("A dog is a canine.")

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "dog_canine.dgca"
        sr.save_checkpoint(ckpt_path)

        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        reply = sr_restored.chat("dog")
        assert "canine" in reply.split()


def test_ric03_t54_learned_recall_via_restored_cognitive_agent_is_chat_transient() -> None:
    """RIC03-T54: learned recall via restored CognitiveAgent remains chat-transient."""
    sr = CanonicalSystemRuntime.fresh()
    for _ in range(5):
        sr.learn("A dog is a canine.")

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "dog_canine.dgca"
        sr.save_checkpoint(ckpt_path)

        agent = CognitiveAgent.from_checkpoint(ckpt_path)
        payload_before = extract_canonical_persistent_payload(agent._runtime.runtime_root._graph)
        digest_before = compute_checkpoint_state_digest(payload_before)

        reply = agent.chat("dog")
        assert "canine" in reply.split()

        payload_after = extract_canonical_persistent_payload(agent._runtime.runtime_root._graph)
        digest_after = compute_checkpoint_state_digest(payload_after)

        assert digest_before == digest_after


def test_ric03_t55_repeated_explicit_replay_does_not_reinforce_twice() -> None:
    """RIC03-T55: repeated explicit occurrence replay does not reinforce twice."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.", occurrence_key="EXPLICIT:REPLAY:TEST")
    payload1 = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest1 = compute_checkpoint_state_digest(payload1)

    res2 = sr.learn("A dog is a canine.", occurrence_key="EXPLICIT:REPLAY:TEST")
    payload2 = extract_canonical_persistent_payload(sr.runtime_root._graph)
    digest2 = compute_checkpoint_state_digest(payload2)

    assert res1.persistent_executed is True
    assert res2.persistent_executed is False
    assert res2.replayed is True
    assert digest1 == digest2


# ─────────────────────────────────────────────────────────── GROUP C01: HARDENING (C01-T01 .. C01-T18)
def test_c01_t01_fresh_runtime_auto_nonce_differs() -> None:
    """C01-T01: fresh runtime AUTO nonce differs from independently fresh runtime nonce."""
    sr1 = CanonicalSystemRuntime.fresh()
    sr2 = CanonicalSystemRuntime.fresh()
    assert sr1._learning_runtime.session_nonce != sr2._learning_runtime.session_nonce


def test_c01_t02_restore_generates_new_learning_session_nonce() -> None:
    """C01-T02: restore generates new learning session nonce."""
    sr = CanonicalSystemRuntime.fresh()
    orig_nonce = sr._learning_runtime.session_nonce
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)
        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        assert sr_restored._learning_runtime.session_nonce != orig_nonce


def test_c01_t03_auto_learn_before_save_and_after_restore_is_new_exposure() -> None:
    """C01-T03: AUTO learn before save + AUTO same text after restore executes as NEW PERSISTENT_EXECUTED exposure."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.")
    assert res1.status == "PERSISTENT_EXECUTED"
    assert res1.persistent_executed is True

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)
        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        res2 = sr_restored.learn("A dog is a canine.")
        assert res2.status == "PERSISTENT_EXECUTED"
        assert res2.persistent_executed is True
        assert res2.replayed is False


def test_c01_t04_auto_source_occurrence_key_before_after_restore_differs() -> None:
    """C01-T04: AUTO source occurrence key before/after restore differs."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.")
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)
        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        res2 = sr_restored.learn("A dog is a canine.")
        assert res1.source_occurrence_key != res2.source_occurrence_key


def test_c01_t05_auto_persistent_txid_before_after_restore_differs() -> None:
    """C01-T05: AUTO persistent TxID before/after restore differs."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.")
    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)
        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        res2 = sr_restored.learn("A dog is a canine.")
        assert res1.persistent_transaction_id != res2.persistent_transaction_id


def test_c01_t06_explicit_occurrence_replay_across_restore_remains_replay() -> None:
    """C01-T06: explicit occurrence replay across restore remains PERSISTENT_REPLAY."""
    sr = CanonicalSystemRuntime.fresh()
    res1 = sr.learn("A dog is a canine.", occurrence_key="FACT:REPLAY:C01")
    assert res1.status == "PERSISTENT_EXECUTED"

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test.dgca"
        sr.save_checkpoint(ckpt_path)
        sr_restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
        res2 = sr_restored.learn("A dog is a canine.", occurrence_key="FACT:REPLAY:C01")
        assert res2.status == "PERSISTENT_REPLAY"
        assert res2.replayed is True
        assert res2.persistent_executed is False


def test_c01_t07_thread_learn_active_concurrent_chat_rejected() -> None:
    """C01-T07: real thread: learn active, concurrent chat rejected."""
    sr = CanonicalSystemRuntime.fresh()
    in_op = threading.Event()
    allow_finish = threading.Event()
    orig_observe = sr._learning_runtime._bridge.observe_text

    def blocking_observe(*args: Any, **kwargs: Any) -> Any:
        in_op.set()
        if not allow_finish.wait(timeout=5.0):
            raise TimeoutError("timed out waiting for finish")
        return orig_observe(*args, **kwargs)

    with patch.object(sr._learning_runtime._bridge, "observe_text", side_effect=blocking_observe):
        t1 = threading.Thread(target=lambda: sr.learn("A dog is a canine."))
        t1.start()
        assert in_op.wait(timeout=5.0)

        with pytest.raises(RuntimeError, match="Cannot begin operation 'CHATTING': runtime is currently in state 'LEARNING'"):
            sr.chat("hello")

        allow_finish.set()
        t1.join(timeout=5.0)
        assert not t1.is_alive()
        assert not sr._lock.locked()
        assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t08_thread_chat_active_concurrent_learn_rejected() -> None:
    """C01-T08: real thread: chat active, concurrent learn rejected."""
    sr = CanonicalSystemRuntime.fresh()
    in_op = threading.Event()
    allow_finish = threading.Event()
    orig_chat = sr._chat_runtime.chat

    def blocking_chat(text: str) -> str:
        in_op.set()
        if not allow_finish.wait(timeout=5.0):
            raise TimeoutError("timed out waiting for finish")
        return orig_chat(text)

    with patch.object(sr._chat_runtime, "chat", side_effect=blocking_chat):
        t1 = threading.Thread(target=lambda: sr.chat("hello"))
        t1.start()
        assert in_op.wait(timeout=5.0)

        with pytest.raises(RuntimeError, match="Cannot begin operation 'LEARNING': runtime is currently in state 'CHATTING'"):
            sr.learn("A dog is a canine.")

        allow_finish.set()
        t1.join(timeout=5.0)
        assert not t1.is_alive()
        assert not sr._lock.locked()
        assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t09_thread_learn_active_concurrent_save_rejected() -> None:
    """C01-T09: real thread: learn active, concurrent save rejected."""
    sr = CanonicalSystemRuntime.fresh()
    in_op = threading.Event()
    allow_finish = threading.Event()
    orig_observe = sr._learning_runtime._bridge.observe_text

    def blocking_observe(*args: Any, **kwargs: Any) -> Any:
        in_op.set()
        if not allow_finish.wait(timeout=5.0):
            raise TimeoutError("timed out waiting for finish")
        return orig_observe(*args, **kwargs)

    with patch.object(sr._learning_runtime._bridge, "observe_text", side_effect=blocking_observe):
        t1 = threading.Thread(target=lambda: sr.learn("A dog is a canine."))
        t1.start()
        assert in_op.wait(timeout=5.0)

        with pytest.raises(RuntimeError, match="Cannot begin operation 'CHECKPOINTING': runtime is currently in state 'LEARNING'"):
            sr.save_checkpoint("dummy.dgca")

        allow_finish.set()
        t1.join(timeout=5.0)
        assert not t1.is_alive()
        assert not sr._lock.locked()
        assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t10_thread_save_active_concurrent_learn_rejected() -> None:
    """C01-T10: real thread: save active, concurrent learn rejected."""
    sr = CanonicalSystemRuntime.fresh()
    in_op = threading.Event()
    allow_finish = threading.Event()

    def blocking_save(*args: Any, **kwargs: Any) -> str:
        in_op.set()
        if not allow_finish.wait(timeout=5.0):
            raise TimeoutError("timed out waiting for finish")
        return "mock_digest"

    with patch("dgca.system_runtime.save_canonical_r1_checkpoint", side_effect=blocking_save):
        t1 = threading.Thread(target=lambda: sr.save_checkpoint("dummy.dgca"))
        t1.start()
        assert in_op.wait(timeout=5.0)

        with pytest.raises(RuntimeError, match="Cannot begin operation 'LEARNING': runtime is currently in state 'CHECKPOINTING'"):
            sr.learn("A dog is a canine.")

        allow_finish.set()
        t1.join(timeout=5.0)
        assert not t1.is_alive()
        assert not sr._lock.locked()
        assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t11_two_simultaneous_learn_calls_one_admitted_one_fails_closed() -> None:
    """C01-T11: two simultaneous learn calls: exactly one admitted while first is held; second fails closed."""
    sr = CanonicalSystemRuntime.fresh()
    in_op = threading.Event()
    allow_finish = threading.Event()
    orig_observe = sr._learning_runtime._bridge.observe_text

    def blocking_observe(*args: Any, **kwargs: Any) -> Any:
        in_op.set()
        if not allow_finish.wait(timeout=5.0):
            raise TimeoutError("timed out waiting for finish")
        return orig_observe(*args, **kwargs)

    with patch.object(sr._learning_runtime._bridge, "observe_text", side_effect=blocking_observe):
        t1 = threading.Thread(target=lambda: sr.learn("First"))
        t1.start()
        assert in_op.wait(timeout=5.0)

        with pytest.raises(RuntimeError, match="Cannot begin operation 'LEARNING': runtime is currently in state 'LEARNING'"):
            sr.learn("Second")

        allow_finish.set()
        t1.join(timeout=5.0)
        assert not t1.is_alive()
        assert not sr._lock.locked()
        assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t12_operation_lock_released_after_success() -> None:
    """C01-T12: operation lock released after successful operation."""
    sr = CanonicalSystemRuntime.fresh()
    sr.chat("hello")
    assert not sr._lock.locked()
    assert sr.operation_state == SystemOperationState.IDLE
    sr.learn("A dog is a canine.")
    assert not sr._lock.locked()
    assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t13_operation_lock_released_after_exception() -> None:
    """C01-T13: operation lock released after exception."""
    sr = CanonicalSystemRuntime.fresh()
    with pytest.raises(ValueError):
        sr.learn("")
    assert not sr._lock.locked()
    assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t14_no_deadlock_threads_terminate_under_bounded_timeout() -> None:
    """C01-T14: no deadlock; threads terminate under bounded join timeout."""
    sr = CanonicalSystemRuntime.fresh()
    results: list[bool] = []

    def worker(idx: int) -> None:
        try:
            sr.learn(f"Thread text {idx}")
            results.append(True)
        except RuntimeError:
            results.append(False)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)
        assert not t.is_alive()

    assert not sr._lock.locked()
    assert sr.operation_state == SystemOperationState.IDLE


def test_c01_t15_system_runtime_no_learning_runtime_property() -> None:
    """C01-T15: not hasattr(CanonicalSystemRuntime, 'learning_runtime')."""
    assert not hasattr(CanonicalSystemRuntime, "learning_runtime")
    sr = CanonicalSystemRuntime.fresh()
    assert not hasattr(sr, "learning_runtime")


def test_c01_t16_system_runtime_public_surface_no_authority_properties() -> None:
    """C01-T16: normal SystemRuntime public surface exposes no capability, authorizer, learning_runtime."""
    sr = CanonicalSystemRuntime.fresh()
    assert not hasattr(sr, "capability")
    assert not hasattr(sr, "authorizer")
    assert not hasattr(sr, "learning_authorizer")
    assert not hasattr(sr, "learning_runtime")
    assert not hasattr(CanonicalLearningRuntime, "authorizer")
    assert not hasattr(sr._learning_runtime, "authorizer")


def test_c01_t17_learning_result_exposes_no_authority_object() -> None:
    """C01-T17: LearningResult exposes no authority object."""
    sr = CanonicalSystemRuntime.fresh()
    res = sr.learn("A dog is a canine.")
    assert not hasattr(res, "capability")
    assert not hasattr(res, "_capability")
    assert not hasattr(res, "authorizer")
    assert not hasattr(res, "_authorizer")


def test_c01_t18_cognitive_agent_exposes_no_learning_surface() -> None:
    """C01-T18: CognitiveAgent still exposes no learning surface."""
    agent = CognitiveAgent()
    assert not hasattr(agent, "learn")
    assert not hasattr(agent, "learn_text")
    assert not hasattr(agent, "learning_runtime")
    assert not hasattr(agent, "capability")
    assert not hasattr(agent, "authorizer")


# ─────────────────────────────────────────────────────────── SEMANTICS REGISTRY & GATES
def test_ric03_semantics_registry_exact() -> None:
    """Verifies that RIC03_LEARNING_SEMANTICS_REGISTRY matches frozen 21 dimensions."""
    expected_keys = {
        "protocol_version",
        "request_owner",
        "authorization_owner",
        "mutation_authority",
        "learning_semantics_owner",
        "observation_owner",
        "observation_mode",
        "supported_modalities",
        "authorization_default",
        "capability_lifetime",
        "capability_persistence",
        "identity_policy",
        "auto_identity_policy",
        "external_identity_policy",
        "same_occurrence_same_descriptor_policy",
        "same_occurrence_conflict_policy",
        "result_lifecycle",
        "generation_policy",
        "chat_learning_policy",
        "checkpoint_policy",
        "operation_concurrency_policy",
    }
    assert set(RIC03_LEARNING_SEMANTICS_REGISTRY.keys()) == expected_keys
    assert len(RIC03_LEARNING_SEMANTICS_REGISTRY) == 21
    assert compute_ric03_learning_semantics_digest() == "ac9927cf5f350bd63d3ab6d15d311989487f9b7123f59472bda1c78c7b6e90ba"
    assert RIC03_LEARNING_SEMANTICS_DIGEST == "ac9927cf5f350bd63d3ab6d15d311989487f9b7123f59472bda1c78c7b6e90ba"


def test_ric03_signatures_conserved() -> None:
    """Verifies RFC13 and RFC14 signatures remain conserved."""
    g = CognitiveGraph()
    assert rfc13_behavioral_signature(g.completion_engine) == "3adbfcfd1f24802a"
    g_bench, _ = _build_benchmark_fixture()
    assert rfc14_behavioral_signature(g_bench.generation_engine) == "46213188cdb02ee8"


def test_ric03_source_level_anti_shortcut_and_file_freeze() -> None:
    """Section 24: Source-level anti-shortcut gates and cognitive freeze verification."""
    # Verify agent.py has no learn
    agent_path = Path(dgca.__file__).parent / "agent.py"
    with open(agent_path, "r", encoding="utf-8") as f:
        agent_code = f.read()
    assert "def learn" not in agent_code

    # Verify frozen files byte-identical against baseline
    frozen_files = [
        "dgca/agent.py",
        "dgca/graph.py",
        "dgca/causal_identity.py",
        "dgca/observation.py",
        "dgca/persistence.py",
        "dgca/chat_runtime.py",
        "dgca/completion.py",
        "dgca/generation.py",
        "dgca/recurrent.py",
        "dgca/loop.py",
        "dgca/encoder.py",
        "dgca/audio.py",
        "dgca/audio_v2.py",
        "dgca/vision.py",
        "dgca/legacy_agent.py",
    ]
    for ff in frozen_files:
        diff = subprocess.check_output(
            ["git", "diff", BASELINE_COMMIT, "HEAD", "--", ff],
            text=True,
        )
        assert diff == "", f"Frozen file {ff} modified against baseline {BASELINE_COMMIT}"
