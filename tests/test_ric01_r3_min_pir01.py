"""
DGCA — RIC-01 / R3-Min-PIR-01
Public Runtime Authority Boundary & Verification Artifact Repair Test Suite

Verification Obligations:
PIR01-T01 .. PIR01-T18
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

import dgca
from dgca import (
    R3_MIN_RUNTIME_SEMANTICS_DIGEST,
    R3_MIN_RUNTIME_SEMANTICS_REGISTRY,
    CognitiveAgent,
    compute_r3_min_runtime_semantics_digest,
)
from dgca.persistence import save_canonical_r1_checkpoint

EXPECTED_FROZEN_32_REGISTRY = {
    "activation_scope_lifetime": "RFC13_CALL_ONLY_RESTORE_BEFORE_RFC14",
    "activation_sink_contract": "EXISTING_NODES_ONLY_TRANSIENT_FIELDS_ONLY",
    "anchor_policy": "EXTERNAL_POSITIVE_NODE_RECEIPTS_ONLY",
    "checkpoint_restore": "CANONICAL_R1_SCHEMA_1_2_0",
    "chunk_policy": "JOIN_NONEMPTY_RENDERED_TEXT_WITH_SINGLE_SPACE",
    "completion_activation_mode": "SCOPED_TRANSIENT_UNCOUNTED_RESTORED",
    "completion_budget": "LAW_E_BUDGET_0",
    "completion_canonical_identity": True,
    "completion_owner": "RFC13",
    "external_ingress_count_per_turn": "EXACTLY_ONE",
    "fallback_text": "I don't have enough information.",
    "fresh_bootstrap": "QUANTITY_BACKBONE_BEFORE_R1_PROVENANCE_EPOCH",
    "fresh_prediction_policy": "DISABLED",
    "generation_budget": 1.0,
    "generation_canonical_identity": True,
    "generation_owner": "RFC14",
    "ingress_owner": "R2_CANONICAL_OBSERVATION_BRIDGE",
    "language_context": "en",
    "learning_api": "ABSENT",
    "legacy_compatibility": "EXPLICIT_LEGACY_COGNITIVE_AGENT",
    "legacy_linearizer_policy": "FORBIDDEN_ON_CANONICAL_PATH",
    "loop_policy": "RFC16_NO_EXTERNAL_INGRESS_ON_R3_MIN_PATH",
    "multi_microepisode_policy": "PROCESS_ALL_OBSERVABLE_CHILDREN_IN_CANONICAL_CHILD_ORDER",
    "observation_mode": "TRANSIENT_ONLY",
    "occurrence_policy": "HOST_SESSION_NONCE_PLUS_MONOTONIC_TURN",
    "protocol_version": "R3-MIN-1.0",
    "public_api": ["chat", "__call__", "from_checkpoint"],
    "recurrent_policy": "RFC15_DEFERRED",
    "restore_prediction_policy": "DISABLED",
    "supported_modalities": ["text"],
    "transient_cleanup_policy": "CLOSE_R2_AND_RFC13_DERIVED_SDCRS",
    "turn_concurrency": "SINGLE_ACTIVE_TURN_FAIL_CLOSED",
}


def test_pir01_t01_public_agent_signature_no_enable_prediction():
    """PIR01-T01: public CognitiveAgent signature has no enable_prediction parameter."""
    sig = inspect.signature(CognitiveAgent)
    assert "enable_prediction" not in sig.parameters
    assert len(sig.parameters) == 0


def test_pir01_t02_public_agent_signature_no_session_nonce():
    """PIR01-T02: public CognitiveAgent signature has no session_nonce parameter."""
    sig = inspect.signature(CognitiveAgent)
    assert "session_nonce" not in sig.parameters
    assert len(sig.parameters) == 0


def test_pir01_t03_agent_enable_prediction_rejected():
    """PIR01-T03: CognitiveAgent(enable_prediction=True) rejected with TypeError."""
    with pytest.raises(TypeError, match=r"got an unexpected keyword argument 'enable_prediction'"):
        CognitiveAgent(enable_prediction=True)


def test_pir01_t04_agent_session_nonce_rejected():
    """PIR01-T04: CognitiveAgent(session_nonce=...) rejected with TypeError."""
    with pytest.raises(TypeError, match=r"got an unexpected keyword argument 'session_nonce'"):
        CognitiveAgent(session_nonce="a" * 32)


def test_pir01_t05_fresh_graph_prediction_always_disabled():
    """PIR01-T05: fresh graph prediction always disabled."""
    agent = CognitiveAgent()
    assert agent._chat_runtime._graph.enable_prediction is False


def test_pir01_t06_public_from_checkpoint_no_session_nonce():
    """PIR01-T06: public from_checkpoint has no session_nonce parameter."""
    sig = inspect.signature(CognitiveAgent.from_checkpoint)
    assert "session_nonce" not in sig.parameters
    assert list(sig.parameters.keys()) == ["filepath"]


def test_pir01_t07_from_checkpoint_session_nonce_rejected(tmp_path):
    """PIR01-T07: from_checkpoint(..., session_nonce=...) rejected with TypeError."""
    base_agent = CognitiveAgent()
    ckpt_path = tmp_path / "test_ckpt.json"
    save_canonical_r1_checkpoint(base_agent._root, ckpt_path)

    with pytest.raises(TypeError, match=r"got an unexpected keyword argument 'session_nonce'"):
        CognitiveAgent.from_checkpoint(ckpt_path, session_nonce="a" * 32)


def test_pir01_t08_restored_graph_prediction_disabled(tmp_path):
    """PIR01-T08: restored graph prediction disabled."""
    base_agent = CognitiveAgent()
    ckpt_path = tmp_path / "test_ckpt.json"
    save_canonical_r1_checkpoint(base_agent._root, ckpt_path)

    restored = CognitiveAgent.from_checkpoint(ckpt_path)
    assert restored._chat_runtime._graph.enable_prediction is False


def test_pir01_t09_private_deterministic_nonce_seam_works(tmp_path):
    """PIR01-T09: private deterministic nonce seam works for fresh and restored agents."""
    fixed_nonce = "b" * 32
    agent1 = CognitiveAgent._for_test(session_nonce=fixed_nonce)
    assert agent1._chat_runtime.session_nonce == fixed_nonce

    agent1.chat("hello world")
    r1 = agent1.last_turn.root_external_episode_id

    agent2 = CognitiveAgent._for_test(session_nonce=fixed_nonce)
    agent2.chat("completely different sentence")
    r2 = agent2.last_turn.root_external_episode_id
    assert r1 == r2

    # Restored checkpoint private seam
    ckpt_path = tmp_path / "test_ckpt.json"
    save_canonical_r1_checkpoint(agent1._root, ckpt_path)

    agent_restored = CognitiveAgent._from_checkpoint_for_test(ckpt_path, session_nonce=fixed_nonce)
    assert agent_restored._chat_runtime.session_nonce == fixed_nonce


def test_pir01_t10_ordinary_two_identical_text_calls_create_distinct_roots():
    """PIR01-T10: ordinary two identical-text calls create distinct Roots."""
    agent = CognitiveAgent()
    agent.chat("Same exact phrase")
    r1 = agent.last_turn.root_external_episode_id

    agent.chat("Same exact phrase")
    r2 = agent.last_turn.root_external_episode_id

    assert r1 != r2


def test_pir01_t11_ordinary_caller_cannot_choose_root_host_nonce():
    """PIR01-T11: ordinary caller cannot choose Root host nonce."""
    # Cannot pass to CognitiveAgent
    with pytest.raises(TypeError):
        CognitiveAgent(session_nonce="f" * 32)

    # dgca package does not expose public factory for choosing host nonce
    assert not hasattr(dgca, "create_chat_runtime_with_nonce")
    assert not hasattr(dgca, "CognitiveAgentWithNonce")


def test_pir01_t12_exact_32_entry_registry_dictionary_equality():
    """PIR01-T12: exact 32-entry registry dictionary equality."""
    assert R3_MIN_RUNTIME_SEMANTICS_REGISTRY == EXPECTED_FROZEN_32_REGISTRY
    assert len(R3_MIN_RUNTIME_SEMANTICS_REGISTRY) == 32


def test_pir01_t13_direct_r3_digest_exact():
    """PIR01-T13: direct R3 digest exact."""
    computed = compute_r3_min_runtime_semantics_digest()
    expected = "fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc"
    assert computed == expected
    assert R3_MIN_RUNTIME_SEMANTICS_DIGEST == expected


def test_pir01_t14_mutated_registry_copy_changes_digest():
    """PIR01-T14: mutated registry copy changes digest."""
    mutated = copy.deepcopy(R3_MIN_RUNTIME_SEMANTICS_REGISTRY)
    mutated["generation_budget"] = 0.5
    payload = json.dumps(
        mutated,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    assert hashlib.sha256(payload).hexdigest() != R3_MIN_RUNTIME_SEMANTICS_DIGEST


def test_pir01_t15_canonical_repl_uses_ordinary_constructor():
    """PIR01-T15: canonical REPL uses ordinary constructor without host override."""
    repl_path = Path(__file__).resolve().parent.parent / "scripts" / "repl.py"
    content = repl_path.read_text(encoding="utf-8")

    assert "agent = CognitiveAgent()" in content
    assert "session_nonce" not in content
    assert "enable_prediction" not in content
    assert "_for_test" not in content


def test_pir01_t16_reports_contain_exact_frozen_registry():
    """PIR01-T16: both verification reports contain exact frozen registry keys."""
    root_report = Path(__file__).resolve().parent.parent / "RIC-01-R3-MIN-IMPLEMENTATION-VERIFICATION-REPORT.md"
    papers_report = Path(__file__).resolve().parent.parent / "papers MD" / "RIC-01-R3-MIN-IMPLEMENTATION-VERIFICATION-REPORT.md"

    for path in (root_report, papers_report):
        assert path.exists(), f"Report missing at {path}"
        text = path.read_text(encoding="utf-8")
        assert "activation_scope_lifetime" in text
        assert "turn_concurrency" in text
        assert "fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc" in text
        # Confirm old incorrect keys are absent
        assert "allow_prompt_authority" not in text
        assert "anchor_source" not in text
        assert "causal_epoch_mutation_on_chat" not in text


def test_pir01_t17_reports_contain_correct_min_law_c_max_description():
    """PIR01-T17: reports contain correct min(Law.C_MAX, value) description."""
    root_report = Path(__file__).resolve().parent.parent / "RIC-01-R3-MIN-IMPLEMENTATION-VERIFICATION-REPORT.md"
    papers_report = Path(__file__).resolve().parent.parent / "papers MD" / "RIC-01-R3-MIN-IMPLEMENTATION-VERIFICATION-REPORT.md"

    for path in (root_report, papers_report):
        text = path.read_text(encoding="utf-8")
        assert "min(Law.C_MAX, value)" in text
        assert "max(node.A, value)" not in text


def test_pir01_t18_reports_record_both_baseline_and_immediate_parent():
    """PIR01-T18: reports record both baseline and immediate parent."""
    root_report = Path(__file__).resolve().parent.parent / "RIC-01-R3-MIN-IMPLEMENTATION-VERIFICATION-REPORT.md"
    papers_report = Path(__file__).resolve().parent.parent / "papers MD" / "RIC-01-R3-MIN-IMPLEMENTATION-VERIFICATION-REPORT.md"

    for path in (root_report, papers_report):
        text = path.read_text(encoding="utf-8")
        assert "c04c0820ef3cb329008a6bc7be0d9c4fd8754403" in text
        assert "462d102876eb68600bfa8e35fcdcfe31d987258a" in text
