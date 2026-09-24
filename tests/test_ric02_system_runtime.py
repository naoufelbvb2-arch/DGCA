"""
DGCA — RIC-02: Canonical System Runtime & CognitiveAgent Boundary Architecture
Test Suite: RIC02-T01 through RIC02-T30, AST/Source Gates, and Adversarial Invariants.

Authoritative Specification:
papers MD/RIC-02-Canonical-System-Runtime-and-Agent-Boundary-Architecture-v1.0-FROZEN.md
Status: FROZEN / ADOPTED
Authoritative Baseline: 006c16b8bba14ebdc78594604962437dd3e4d4ac
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from dgca.agent import CognitiveAgent
from dgca.causal_identity import (
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalRuntimeHealth,
)
from dgca.chat_runtime import (
    R3_MIN_RUNTIME_SEMANTICS_DIGEST,
    CanonicalChatRuntime,
)
from dgca.completion import rfc13_behavioral_signature
from dgca.generation import rfc14_behavioral_signature
from dgca.graph import CognitiveGraph
from dgca.legacy_agent import LegacyCognitiveAgent
from dgca.persistence import (
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)
from dgca.system_runtime import CanonicalSystemRuntime
from scripts.audit_rfc16_benchmarks import _build_benchmark_fixture

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_PY_PATH = REPO_ROOT / "dgca" / "agent.py"
SCTT00_CHECKPOINT = REPO_ROOT / "data" / "checkpoints" / "SCTT00-trained.json"
BASELINE_COMMIT = "006c16b8bba14ebdc78594604962437dd3e4d4ac"


# =============================================================================
# RIC02-T01 .. RIC02-T30
# =============================================================================

def test_ric02_t01_fresh_produces_healthy_r1_runtime():
    """RIC02-T01: CanonicalSystemRuntime.fresh() produces healthy R1 runtime."""
    runtime = CanonicalSystemRuntime.fresh()
    assert runtime.runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY


def test_ric02_t02_fresh_runtime_lineage_valid():
    """RIC02-T02: Fresh runtime lineage == VALID."""
    runtime = CanonicalSystemRuntime.fresh()
    assert runtime.runtime_root.canonical_lineage_state == CanonicalLineageState.VALID


def test_ric02_t03_observation_protocol_version():
    """RIC02-T03: Observation protocol == R2-OBS-1.0."""
    runtime = CanonicalSystemRuntime.fresh()
    assert runtime.runtime_root.observation_protocol_version == "R2-OBS-1.0"


def test_ric02_t04_prediction_disabled_on_fresh_graph():
    """RIC02-T04: Prediction disabled on fresh graph."""
    runtime = CanonicalSystemRuntime.fresh()
    assert runtime._graph.enable_prediction is False


def test_ric02_t05_owns_exactly_one_canonical_r1_root():
    """RIC02-T05: CanonicalSystemRuntime owns exactly one canonical R1 root."""
    runtime = CanonicalSystemRuntime.fresh()
    assert isinstance(runtime.runtime_root, CanonicalR1RuntimeRoot)
    assert runtime.runtime_root is runtime._root


def test_ric02_t06_owns_one_chat_runtime_bound_to_same_r1_root():
    """RIC02-T06: CanonicalSystemRuntime owns one chat runtime bound to same R1 root."""
    runtime = CanonicalSystemRuntime.fresh()
    assert isinstance(runtime.chat_runtime, CanonicalChatRuntime)
    assert runtime.chat_runtime._runtime_root is runtime.runtime_root


def test_ric02_t07_cognitive_agent_stores_only_system_runtime_authority():
    """RIC02-T07: CognitiveAgent stores only system runtime authority."""
    agent = CognitiveAgent()
    assert CognitiveAgent.__slots__ == ("_runtime",)
    assert hasattr(agent, "_runtime")
    assert isinstance(agent._runtime, CanonicalSystemRuntime)
    with pytest.raises(AttributeError):
        agent.extra_field = "unauthorized"


def test_ric02_t08_agent_py_does_not_import_cognitive_graph():
    """RIC02-T08: agent.py does not import CognitiveGraph."""
    source = AGENT_PY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "CognitiveGraph" not in alias.name
        elif isinstance(node, ast.ImportFrom):
            assert node.module != "dgca.graph"
            for alias in node.names:
                assert alias.name != "CognitiveGraph"


def test_ric02_t09_agent_py_does_not_import_bootstrap_persistence_causal_apis():
    """RIC02-T09: agent.py does not import bootstrap/persistence/causal construction APIs."""
    source = AGENT_PY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_modules = {
        "dgca.graph",
        "dgca.numbers",
        "dgca.persistence",
        "dgca.causal_identity",
        "dgca.observation",
        "dgca.completion",
        "dgca.generation",
        "dgca.recurrent",
        "dgca.loop",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module not in forbidden_modules, f"Forbidden import from {node.module} in agent.py"


def test_ric02_t10_cognitive_agent_chat_delegates_exactly_once():
    """RIC02-T10: CognitiveAgent.chat delegates exactly once to CanonicalSystemRuntime.chat()."""
    with patch.object(CanonicalSystemRuntime, "chat", autospec=True, return_value="mock_reply") as mock_chat:
        agent = CognitiveAgent()
        reply = agent.chat("test cue")
        mock_chat.assert_called_once_with(agent._runtime, "test cue")
        assert reply == "mock_reply"


def test_ric02_t11_cognitive_agent_call_delegates_to_chat():
    """RIC02-T11: CognitiveAgent.__call__ delegates to chat."""
    with patch.object(CognitiveAgent, "chat", autospec=True, return_value="call_reply") as mock_agent_chat:
        agent = CognitiveAgent()
        reply = agent("call cue")
        mock_agent_chat.assert_called_once_with(agent, "call cue")
        assert reply == "call_reply"


def test_ric02_t12_cognitive_agent_last_turn_delegates_read_only():
    """RIC02-T12: CognitiveAgent.last_turn delegates read-only."""
    agent = CognitiveAgent()
    assert agent.last_turn is None
    agent.chat("hello world")
    assert agent.last_turn is not None
    assert agent.last_turn is agent._runtime.last_turn


def test_ric02_t13_cognitive_agent_from_checkpoint_delegates_to_runtime(tmp_path: Path):
    """RIC02-T13: CognitiveAgent.from_checkpoint delegates to CanonicalSystemRuntime."""
    runtime = CanonicalSystemRuntime.fresh()
    ckpt_path = tmp_path / "t13_test_ckpt.json"
    runtime.save_checkpoint(ckpt_path)

    agent = CognitiveAgent.from_checkpoint(ckpt_path)
    assert isinstance(agent, CognitiveAgent)
    assert isinstance(agent._runtime, CanonicalSystemRuntime)
    assert agent._runtime.runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY


def test_ric02_t14_fresh_bootstrap_persistent_state_identical_to_baseline():
    """RIC02-T14: Fresh bootstrap persistent state is behaviorally identical to pre-RIC02 baseline."""
    runtime = CanonicalSystemRuntime.fresh()
    payload = extract_canonical_persistent_payload(runtime._graph)
    digest = compute_checkpoint_state_digest(payload)
    expected_fresh_digest = "975d6953a4dd34d39f6fa678fb37fe1289118b1b579ddc6576b4cb892f76ac32"
    assert digest == expected_fresh_digest


def test_ric02_t15_checkpoint_restored_graph_state_digest_identical():
    """RIC02-T15: Checkpoint restored graph state digest is identical to baseline."""
    runtime = CanonicalSystemRuntime.from_checkpoint(SCTT00_CHECKPOINT)
    payload = extract_canonical_persistent_payload(runtime._graph)
    digest = compute_checkpoint_state_digest(payload)
    expected_ckpt_digest = "548e6fee4b450ba841857ec209df9d0ffb467de62a8639d32fe290eb1b681c3a"
    assert digest == expected_ckpt_digest


def test_ric02_t16_checkpoint_bundle_integrity_remains_unchanged(tmp_path: Path):
    """RIC02-T16: Checkpoint bundle integrity remains unchanged across save/restore roundtrip."""
    runtime = CanonicalSystemRuntime.fresh()
    test_ckpt = tmp_path / "roundtrip.json"
    bundle_digest = runtime.save_checkpoint(test_ckpt)
    assert len(bundle_digest) == 64

    restored = CanonicalSystemRuntime.from_checkpoint(test_ckpt)
    assert restored.runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY

    p1 = extract_canonical_persistent_payload(runtime._graph)
    p2 = extract_canonical_persistent_payload(restored._graph)
    assert compute_checkpoint_state_digest(p1) == compute_checkpoint_state_digest(p2)


def test_ric02_t17_sctt_trained_checkpoint_restores_successfully():
    """RIC02-T17: SCTT trained checkpoint restores successfully."""
    agent = CognitiveAgent.from_checkpoint(SCTT00_CHECKPOINT)
    root = agent._runtime.runtime_root
    assert root.causal_runtime_health == CausalRuntimeHealth.HEALTHY
    assert root.canonical_lineage_state == CanonicalLineageState.VALID


def test_ric02_t18_all_8_sctt_learned_probes_retain_exact_outputs():
    """RIC02-T18: All 8 SCTT learned probes retain exact current outputs."""
    agent = CognitiveAgent.from_checkpoint(SCTT00_CHECKPOINT)
    expected_probes = [
        ("dog", "dog canine"),
        ("cat", "cat feline"),
        ("robin", "robin bird"),
        ("rose", "rose flower"),
        ("apple", "apple fruit"),
        ("car", "car vehicle"),
        ("ice", "ice solid"),
        ("water", "water liquid"),
    ]
    for cue, expected_reply in expected_probes:
        reply = agent.chat(cue)
        assert reply == expected_reply, f"Probe mismatch for '{cue}': expected '{expected_reply}', got '{reply}'"
        assert agent.last_turn is not None
        assert "FIXED_POINT" in agent.last_turn.completion_closure_reasons


def test_ric02_t19_ood_behavior_remains_unchanged():
    """RIC02-T19: OOD behavior remains unchanged."""
    agent = CognitiveAgent.from_checkpoint(SCTT00_CHECKPOINT)
    targets = {"canine", "feline", "bird", "flower", "fruit", "vehicle", "solid", "liquid"}
    ood_cues = ["pizza", "computer", "chair", "ocean"]

    for cue in ood_cues:
        reply = agent.chat(cue)
        lt = agent.last_turn
        assert lt is not None
        assert lt.used_fallback is False
        tokens = set(reply.split())
        assert len(tokens & targets) == 0, f"Contamination in OOD reply: {tokens & targets}"


def test_ric02_t20_ordinary_chat_persistent_delta_remains_zero():
    """RIC02-T20: Ordinary chat persistent delta remains zero."""
    agent = CognitiveAgent.from_checkpoint(SCTT00_CHECKPOINT)
    g = agent._runtime._graph
    d_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(g))

    agent.chat("dog")
    agent.chat("pizza")
    agent.chat("What is a robin?")

    d_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(g))
    assert d_before == d_after, "Persistent state mutated during ordinary chat!"


def test_ric02_t21_rfc15_remains_unmaterialized():
    """RIC02-T21: RFC15 remains unmaterialized."""
    runtime = CanonicalSystemRuntime.fresh()
    assert runtime._graph._recurrent_engine is None

    agent = CognitiveAgent.from_checkpoint(SCTT00_CHECKPOINT)
    assert agent._runtime._graph._recurrent_engine is None


def test_ric02_t22_rfc16_full_loop_remains_unused():
    """RIC02-T22: RFC16 full loop remains unused."""
    runtime = CanonicalSystemRuntime.fresh()
    assert getattr(runtime._graph, "_loop_engine", None) is None


def test_ric02_t23_r3_min_runtime_semantics_digest_unchanged():
    """RIC02-T23: R3_MIN_RUNTIME_SEMANTICS_DIGEST unchanged."""
    expected = "fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc"
    assert R3_MIN_RUNTIME_SEMANTICS_DIGEST == expected


def test_ric02_t24_canonical_chat_runtime_file_unchanged_from_baseline():
    """RIC02-T24: CanonicalChatRuntime file is unchanged from baseline."""
    res = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            BASELINE_COMMIT,
            "--",
            "dgca/chat_runtime.py",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    diff_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    assert diff_files == [], f"dgca/chat_runtime.py was modified: {diff_files}"


def test_ric02_t25_rfc13_behavioral_signature_unchanged():
    """RIC02-T25: RFC13 behavioral signature unchanged."""
    g = CognitiveGraph()
    sig = rfc13_behavioral_signature(g.completion_engine)
    assert sig == "3adbfcfd1f24802a"


def test_ric02_t26_rfc14_behavioral_signature_unchanged():
    """RIC02-T26: RFC14 behavioral signature unchanged."""
    g, _ = _build_benchmark_fixture()
    sig = rfc14_behavioral_signature(g.generation_engine)
    assert sig == "46213188cdb02ee8"


def test_ric02_t27_legacy_cognitive_agent_unchanged_and_usable():
    """RIC02-T27: LegacyCognitiveAgent unchanged and still separately usable."""
    legacy = LegacyCognitiveAgent()
    assert hasattr(legacy, "perceive_text")
    assert hasattr(legacy, "perceive_code")
    assert hasattr(legacy, "query")
    res = legacy.perceive_text("Cats are mammals.")
    assert res["status"] == "INGESTED"


def test_ric02_t28_repl_continues_to_use_only_cognitive_agent_chat():
    """RIC02-T28: REPL continues to use only CognitiveAgent.chat."""
    repl_path = REPO_ROOT / "scripts" / "repl.py"
    source = repl_path.read_text(encoding="utf-8")
    assert "from dgca import CognitiveAgent" in source
    assert "agent = CognitiveAgent()" in source
    assert "reply = agent.chat(line)" in source
    assert "learn(" not in source
    assert "save_checkpoint" not in source


def test_ric02_t29_cognitive_agent_exposes_no_learn_perceive_raw_graph_api():
    """RIC02-T29: CognitiveAgent exposes no learn/perceive/raw-graph API."""
    forbidden_agent_attrs = [
        "learn",
        "perceive_text",
        "perceive_code",
        "graph",
        "ledger",
        "runtime_root",
        "chat_runtime",
        "save_checkpoint",
    ]
    for attr in forbidden_agent_attrs:
        assert not hasattr(CognitiveAgent, attr), f"CognitiveAgent unlawfully exposes {attr}"


def test_ric02_t30_no_persistent_authority_reachable_from_ordinary_agent_api():
    """RIC02-T30: No persistent authority is reachable from ordinary CognitiveAgent API."""
    agent = CognitiveAgent()
    forbidden_instance_attrs = [
        "_graph",
        "_root",
        "_ledger",
        "_chat_runtime",
        "save_checkpoint",
        "learn",
    ]
    for attr in forbidden_instance_attrs:
        assert not hasattr(agent, attr), f"CognitiveAgent instance unlawfully exposes {attr}"


# =============================================================================
# Section 14: Source-Level Architecture Gates
# =============================================================================

def test_ric02_source_gate_forbidden_symbols_absent():
    """Section 14: agent.py contains none of the forbidden composition/cognitive symbols."""
    source = AGENT_PY_PATH.read_text(encoding="utf-8")
    forbidden_symbols = [
        "CognitiveGraph(",
        "init_quantity_backbone(",
        "create_native_r1_provenance_epoch(",
        "CausalCommitLedger(",
        "RuntimeLifecycleGuard(",
        "CanonicalR1RuntimeRoot(",
        "restore_canonical_r1_checkpoint(",
        "save_canonical_r1_checkpoint(",
        "create_observation_bridge(",
        "completion_engine",
        "generation_engine",
        "recurrent_engine",
        "loop_engine",
    ]
    for sym in forbidden_symbols:
        assert sym not in source, f"Forbidden symbol '{sym}' present in dgca/agent.py"


def test_ric02_source_gate_agent_slots_and_dependencies():
    """Section 14: agent.py has only CanonicalSystemRuntime as system-owning dependency and strict slots."""
    source = AGENT_PY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    # Allowed non-typing imports: system_runtime, pathlib, __future__, typing, chat_runtime
    allowed_imported_modules = {
        "__future__",
        "pathlib",
        "system_runtime",
        ".system_runtime",
        "typing",
        "chat_runtime",
        ".chat_runtime",  # TYPE_CHECKING only
    }
    assert imported_modules.issubset(allowed_imported_modules), f"Unexpected imports: {imported_modules}"


# =============================================================================
# Adversarial Invariant Tests
# =============================================================================

def test_ric02_adv_agent_rejects_prediction_parameter():
    """Adversarial: CognitiveAgent rejects prediction parameter."""
    with pytest.raises(TypeError):
        CognitiveAgent(enable_prediction=False)  # type: ignore


def test_ric02_adv_agent_rejects_session_nonce_parameter():
    """Adversarial: CognitiveAgent rejects session nonce parameter."""
    with pytest.raises(TypeError):
        CognitiveAgent(session_nonce="nonce_123")  # type: ignore


def test_ric02_adv_from_checkpoint_rejects_session_nonce():
    """Adversarial: CognitiveAgent.from_checkpoint rejects session nonce parameter."""
    with pytest.raises(TypeError):
        CognitiveAgent.from_checkpoint(SCTT00_CHECKPOINT, session_nonce="nonce_123")  # type: ignore


def test_ric02_adv_agent_slots_prevent_arbitrary_attribute_binding():
    """Adversarial: CognitiveAgent slots prevent attaching arbitrary attributes."""
    agent = CognitiveAgent()
    with pytest.raises(AttributeError):
        agent._graph = "fake_graph"
    with pytest.raises(AttributeError):
        agent._root = "fake_root"
    with pytest.raises(AttributeError):
        agent._chat_runtime = "fake_chat"
    assert not hasattr(agent, "__dict__")
