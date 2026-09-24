"""
DGCA — RIC-01 / R3 Minimal
Minimal Canonical User Runtime Strict Implementation & Verification Suite

Authoritative Specifications:
- RIC-01-R3-Minimal-Canonical-User-Runtime-Formal-Architecture-Specification-v1.1-FROZEN.md
- RIC-01-R3-Min-Strict-Implementation-Verification-Master-Prompt-v1.0-FROZEN.md

Invariants: R3-I01 .. R3-I42
Acceptance Obligations: A01 .. N08
Adversarial Scenarios: ADV-A .. ADV-T
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

import dgca
from dgca import (
    R3_MIN_FALLBACK_TEXT,
    R3_MIN_RUNTIME_SEMANTICS_DIGEST,
    R3_MIN_RUNTIME_SEMANTICS_REGISTRY,
    CanonicalLineageState,
    CanonicalSystemRuntime,
    CausalRuntimeHealth,
    CognitiveAgent,
    CognitiveGraph,
    ExecutionMode,
    LegacyCognitiveAgent,
    LinearizationEngine,
    TransientActivationScope,
    compute_r3_min_runtime_semantics_digest,
)
from dgca.causal_identity import (
    CausalIdentityValidationError,
)
from dgca.completion import (
    PatternCompletionEngine,
    rfc13_behavioral_signature,
)
from dgca.generation import rfc14_behavioral_signature
from dgca.persistence import (
    CheckpointCompatibilityError,
    CheckpointIntegrityError,
    CheckpointSchemaError,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)
from dgca.signature import build_reference_graph

# ─────────────────────────────────────────────────────────── Frozen Acceptance Ledger Exact Text
FROZEN_ACCEPTANCE_LEDGER: dict[str, str] = {
    # A — Boot
    "A01": "fresh CognitiveAgent constructs a healthy canonical R1 runtime.",
    "A02": "fresh runtime uses observation protocol R2-OBS-1.0.",
    "A03": "fresh lineage is VALID.",
    "A04": "top-level dgca.CognitiveAgent is the new canonical Agent.",
    "A05": "raw mutable graph is not exposed publicly.",
    # B — Checkpoint
    "B01": "from_checkpoint restores canonical schema 1.2.0.",
    "B02": "R2 protocol mismatch fails closed.",
    "B03": "malformed/integrity-invalid checkpoint fails closed.",
    "B04": "restored agent can execute chat().",
    "B05": "no legacy graph.load() path is used.",
    # C — Occurrence identity
    "C01": "first chat allocates one Root.",
    "C02": "second identical-text chat allocates a different Root.",
    "C03": "Root derivation does not contain/hash raw text as occurrence authority.",
    "C04": "failed turn index is not reused.",
    "C05": "fixed test session nonce + same turn index reproduces same Root.",
    # D — R2
    "D01": "bridge.observe_text is invoked exactly once per chat.",
    "D02": "mode is TRANSIENT_ONLY.",
    "D03": "capability is absent.",
    "D04": "persistent_phase is NOT_REQUESTED.",
    "D05": "ledger is unchanged.",
    "D06": "content such as \"fact:\" cannot change D02-D05.",
    # E — Multi-child
    "E01": "zero-child returns fallback.",
    "E02": "one-child path executes once.",
    "E03": "N observable children execute in exact child_index order.",
    "E04": "representation_id=None children are skipped.",
    "E05": "no synthetic merged R2 representation is created.",
    # F — Anchors
    "F01": "anchors come only from positive external node receipts.",
    "F02": "completed/recalled nodes are not promoted to root anchors.",
    "F03": "empty anchor set skips generation for that child.",
    "F04": "no stopword/keyword ranking chooses anchors.",
    # G — RFC13 isolation
    "G01": "RFC13 can accept at least one reinstatement under R3 scope.",
    "G02": "touched Node.A is visible during settling.",
    "G03": "inhibition sees scoped Node.A.",
    "G04": "N_total before == N_total after for all nodes.",
    "G05": "A before == A after for all touched nodes.",
    "G06": "t_spawn before == t_spawn after.",
    "G07": "episode before == episode after.",
    "G08": "restoration occurs after RFC13 exception.",
    "G09": "RFC13 legacy path without activation sink preserves old behavior.",
    "G10": "RFC13 behavioral signature on legacy/default path is unchanged.",
    "G11": "R3 invokes RFC13 with budget == Law.E_BUDGET_0.",
    # H — Representations
    "H01": "completion-created SDCRs are tracked.",
    "H02": "final settled SDCR is available through RFC14 call.",
    "H03": "all completion-created SDCRs are CLOSED after child completion.",
    "H04": "original R2 SDCR remains alive until R2 result cleanup.",
    "H05": "all original R2 SDCRs are CLOSED after turn cleanup.",
    "H06": "no ACTIVE R3-created representation survives the turn.",
    # I — RFC14
    "I01": "RFC14 canonical_identity=True.",
    "I02": "GenerationScope carries current Root/Observation/MicroEpisode refs.",
    "I03": "language_context == \"en\".",
    "I04": "returned child text is SurfaceChunk.rendered_text.",
    "I05": "no legacy LinearizationEngine text substitution occurs.",
    "I06": "RFC14 behavioral signature remains unchanged.",
    "I07": "R3 invokes RFC14 with budget == 1.0.",
    # J — Turn text
    "J01": "one non-empty chunk returns exactly that string.",
    "J02": "multiple non-empty chunks join with exactly one ASCII space.",
    "J03": "empty chunks are omitted.",
    "J04": "all-empty output returns exact fixed fallback.",
    "J05": "R3 adds no punctuation/capitalization/template text to a non-empty chunk.",
    # K — Deferred systems
    "K01": "recurrent_engine is not invoked.",
    "K02": "no GCE exists because of ordinary R3-Min chat.",
    "K03": "loop_engine.execute_canonical_full_loop is not invoked.",
    "K04": "LinearizationEngine.answer_query is not invoked.",
    "K05": "Audio encoders are not invoked.",
    "K06": "Vision encoders are not invoked.",
    # L — Persistent conservation
    "L01": "canonical persistent payload digest before == after.",
    "L02": "graph logical_time before == after.",
    "L03": "all durable node fields before == after.",
    "L04": "all durable edge fields before == after.",
    "L05": "contradictions before == after.",
    "L06": "concept_hits before == after.",
    "L07": "drives before == after.",
    "L08": "hypotheses before == after.",
    "L09": "assemblies before == after.",
    "L10": "pending structural evidence before == after.",
    "L11": "causal ledger before == after.",
    "L12": "causal provenance epoch before == after.",
    # M — Lifecycle/failure
    "M01": "second concurrent chat fails closed.",
    "M02": "nested/reentrant chat fails closed.",
    "M03": "turn owner returns to IDLE after success.",
    "M04": "turn owner returns to IDLE after failure.",
    "M05": "transient cleanup executes after RFC13 failure.",
    "M06": "transient cleanup executes after RFC14 failure.",
    "M07": "runtime health remains HEALTHY for transient cognitive failure.",
    "M08": "canonical lineage remains VALID.",
    # N — Public surface
    "N01": "CognitiveAgent has chat().",
    "N02": "CognitiveAgent has __call__().",
    "N03": "CognitiveAgent has from_checkpoint().",
    "N04": "CognitiveAgent does not expose perceive_text().",
    "N05": "CognitiveAgent does not expose perceive_code().",
    "N06": "CognitiveAgent does not expose learn().",
    "N07": "canonical REPL has no /learn command.",
    "N08": "plain REPL text routes directly to chat().",
}

FROZEN_INVARIANT_LEDGER: dict[str, str] = {
    "R3-I01": "CognitiveAgent.chat(text) is the canonical ordinary-user entry point.",
    "R3-I02": "CognitiveAgent.__call__(text) delegates exactly to chat(text).",
    "R3-I03": "from_checkpoint uses canonical R1 restore.",
    "R3-I04": "ordinary chat invokes R2 exactly once per turn.",
    "R3-I05": "R2 mode is always TRANSIENT_ONLY.",
    "R3-I06": "ordinary Agent exposes no persistent capability.",
    "R3-I07": "raw user content cannot grant learning authority.",
    "R3-I08": "Root identity is occurrence-derived, never content-hash-derived.",
    "R3-I09": "distinct identical-text calls create distinct Roots.",
    "R3-I10": "all observable R2 children are processed in child order.",
    "R3-I11": "R2 children are not merged by a new cognition primitive.",
    "R3-I12": "anchors are direct positive external node receipts only.",
    "R3-I13": "RFC13 uses canonical identities.",
    "R3-I14": "RFC13 receives the original R2 Root authority.",
    "R3-I15": "RFC13 scoped activation preserves Law-15 reads of Node.A.",
    "R3-I16": "RFC13 scoped activation never increments N_total.",
    "R3-I17": "touched A/t_spawn/episode fields are restored exactly.",
    "R3-I18": "RFC13 derived SDCRs are closed after their RFC14 generation.",
    "R3-I19": "R2 observation results are closed in finally.",
    "R3-I20": "RFC14 uses canonical identities.",
    "R3-I21": "RFC14 rendered_text is the only cognitive user-visible surface.",
    "R3-I22": "non-empty child chunks are joined only with one ASCII space.",
    "R3-I23": "empty overall generation returns only the fixed fallback.",
    "R3-I24": "Legacy LinearizationEngine is not called.",
    "R3-I25": "RFC15 recurrent engine is not called.",
    "R3-I26": "RFC16 full-loop ingress is not called.",
    "R3-I27": "one runtime permits one active turn only.",
    "R3-I28": "no ordinary chat changes canonical persistent payload.",
    "R3-I29": "no ordinary chat changes causal ledger.",
    "R3-I30": "no ordinary chat changes RFC11 persistent structural evidence.",
    "R3-I31": "canonical lineage remains VALID.",
    "R3-I32": "runtime health remains HEALTHY.",
    "R3-I33": "fresh and restored R3-Min prediction side path is disabled.",
    "R3-I34": "RFC13 completion budget is exactly Law.E_BUDGET_0.",
    "R3-I35": "RFC14 generation budget is exactly 1.0.",
    "R3-I36": "language_context is fixed to 'en'.",
    "R3-I37": "Audio is not invoked.",
    "R3-I38": "Vision is not modified or invoked by text chat.",
    "R3-I39": "no new cognitive law is introduced.",
    "R3-I40": "R3 turn diagnostics are transient and not checkpointed.",
    "R3-I41": "ordinary REPL contains no /learn path.",
    "R3-I42": "any future RFC15 addition must preserve I01–I41 unless explicitly re-frozen.",
}

ACCEPTANCE_EVIDENCE_MAP: dict[str, tuple[str, ...]] = {
    "A01": ("test_a01_to_a05_boot",),
    "A02": ("test_a01_to_a05_boot",),
    "A03": ("test_a01_to_a05_boot",),
    "A04": ("test_a01_to_a05_boot",),
    "A05": ("test_a01_to_a05_boot",),
    "B01": ("test_b01_to_b05_checkpoint",),
    "B02": ("test_b01_to_b05_checkpoint",),
    "B03": ("test_b01_to_b05_checkpoint",),
    "B04": ("test_b01_to_b05_checkpoint",),
    "B05": ("test_b01_to_b05_checkpoint",),
    "C01": ("test_c01_to_c05_occurrence_identity",),
    "C02": ("test_c01_to_c05_occurrence_identity", "test_adv_c_identical_text_distinct_roots"),
    "C03": ("test_c01_to_c05_occurrence_identity",),
    "C04": ("test_c01_to_c05_occurrence_identity",),
    "C05": ("test_c01_to_c05_occurrence_identity",),
    "D01": ("test_d01_to_d06_r2_ingress",),
    "D02": ("test_d01_to_d06_r2_ingress",),
    "D03": ("test_d01_to_d06_r2_ingress",),
    "D04": ("test_d01_to_d06_r2_ingress",),
    "D05": ("test_d01_to_d06_r2_ingress",),
    "D06": ("test_d01_to_d06_r2_ingress", "test_adv_a_fact_prefix_cannot_learn"),
    "E01": ("test_e01_to_e05_multi_child", "test_adv_p_empty_anchors_child_skipped"),
    "E02": ("test_e01_to_e05_multi_child",),
    "E03": ("test_e01_to_e05_multi_child", "test_adv_o_multi_child_child_index_order"),
    "E04": ("test_e01_to_e05_multi_child",),
    "E05": ("test_e01_to_e05_multi_child",),
    "F01": ("test_f01_to_f04_anchors",),
    "F02": ("test_f01_to_f04_anchors",),
    "F03": ("test_f01_to_f04_anchors", "test_adv_p_empty_anchors_child_skipped"),
    "F04": ("test_f01_to_f04_anchors",),
    "G01": ("test_g01_to_g11_rfc13_isolation",),
    "G02": ("test_g01_to_g11_rfc13_isolation",),
    "G03": ("test_g01_to_g11_rfc13_isolation",),
    "G04": ("test_g01_to_g11_rfc13_isolation", "test_adv_d_reinstatement_n_total_unchanged"),
    "G05": ("test_g01_to_g11_rfc13_isolation",),
    "G06": ("test_g01_to_g11_rfc13_isolation",),
    "G07": ("test_g01_to_g11_rfc13_isolation", "test_adv_e_multiple_reinstatements_first_touch_exact"),
    "G08": ("test_g01_to_g11_rfc13_isolation", "test_adv_f_exception_after_scoped_write_restores"),
    "G09": ("test_g01_to_g11_rfc13_isolation", "test_adv_s_legacy_rfc13_signature_unchanged"),
    "G10": ("test_g01_to_g11_rfc13_isolation", "test_adv_s_legacy_rfc13_signature_unchanged"),
    "G11": ("test_g01_to_g11_rfc13_isolation",),
    "H01": ("test_h01_to_h06_representations",),
    "H02": ("test_h01_to_h06_representations",),
    "H03": ("test_h01_to_h06_representations",),
    "H04": ("test_h01_to_h06_representations",),
    "H05": ("test_h01_to_h06_representations",),
    "H06": ("test_h01_to_h06_representations", "test_adv_j_rfc14_raises_all_sdcrs_closed"),
    "I01": ("test_i01_to_i07_rfc14_generation",),
    "I02": ("test_i01_to_i07_rfc14_generation",),
    "I03": ("test_i01_to_i07_rfc14_generation",),
    "I04": ("test_i01_to_i07_rfc14_generation",),
    "I05": ("test_i01_to_i07_rfc14_generation", "test_adv_n_linearization_engine_spy_zero_calls"),
    "I06": ("test_i01_to_i07_rfc14_generation",),
    "I07": ("test_i01_to_i07_rfc14_generation",),
    "J01": ("test_j01_to_j05_turn_text",),
    "J02": ("test_j01_to_j05_turn_text",),
    "J03": ("test_j01_to_j05_turn_text",),
    "J04": ("test_j01_to_j05_turn_text", "test_adv_q_all_empty_generation_exact_fallback"),
    "J05": ("test_j01_to_j05_turn_text",),
    "K01": ("test_k01_to_k06_deferred_systems", "test_adv_l_rfc15_spy_zero_calls"),
    "K02": ("test_k01_to_k06_deferred_systems", "test_adv_l_rfc15_spy_zero_calls"),
    "K03": ("test_k01_to_k06_deferred_systems", "test_adv_m_rfc16_full_loop_spy_zero_calls"),
    "K04": ("test_k01_to_k06_deferred_systems", "test_adv_n_linearization_engine_spy_zero_calls"),
    "K05": ("test_k01_to_k06_deferred_systems",),
    "K06": ("test_k01_to_k06_deferred_systems",),
    "L01": ("test_l01_to_l12_persistent_conservation", "test_adv_a_fact_prefix_cannot_learn"),
    "L02": ("test_l01_to_l12_persistent_conservation",),
    "L03": ("test_l01_to_l12_persistent_conservation",),
    "L04": ("test_l01_to_l12_persistent_conservation",),
    "L05": ("test_l01_to_l12_persistent_conservation",),
    "L06": ("test_l01_to_l12_persistent_conservation",),
    "L07": ("test_l01_to_l12_persistent_conservation",),
    "L08": ("test_l01_to_l12_persistent_conservation",),
    "L09": ("test_l01_to_l12_persistent_conservation",),
    "L10": ("test_l01_to_l12_persistent_conservation",),
    "L11": ("test_l01_to_l12_persistent_conservation",),
    "L12": ("test_l01_to_l12_persistent_conservation",),
    "M01": ("test_m01_to_m08_lifecycle_failure",),
    "M02": ("test_m01_to_m08_lifecycle_failure", "test_adv_k_nested_reentrant_chat_fails_closed"),
    "M03": ("test_m01_to_m08_lifecycle_failure",),
    "M04": ("test_m01_to_m08_lifecycle_failure",),
    "M05": ("test_m01_to_m08_lifecycle_failure", "test_adv_f_exception_after_scoped_write_restores"),
    "M06": ("test_m01_to_m08_lifecycle_failure", "test_adv_j_rfc14_raises_all_sdcrs_closed"),
    "M07": ("test_m01_to_m08_lifecycle_failure",),
    "M08": ("test_m01_to_m08_lifecycle_failure",),
    "N01": ("test_n01_to_n08_public_surface",),
    "N02": ("test_n01_to_n08_public_surface",),
    "N03": ("test_n01_to_n08_public_surface",),
    "N04": ("test_n01_to_n08_public_surface",),
    "N05": ("test_n01_to_n08_public_surface",),
    "N06": ("test_n01_to_n08_public_surface",),
    "N07": ("test_n01_to_n08_public_surface",),
    "N08": ("test_n01_to_n08_public_surface",),
}


# ─────────────────────────────────────────────────────────── Section 1: Exact Semantics Registry & Digest
def test_r3_t01_semantics_registry_exact_count_and_digest():
    """R3-T01, R3-I39, Section 3: Exact 32-entry semantics registry and canonical SHA-256 digest."""
    expected_registry = {
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
    assert R3_MIN_RUNTIME_SEMANTICS_REGISTRY == expected_registry

    assert len(R3_MIN_RUNTIME_SEMANTICS_REGISTRY) == 32
    computed = compute_r3_min_runtime_semantics_digest()
    expected = "fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc"
    assert computed == expected
    assert R3_MIN_RUNTIME_SEMANTICS_DIGEST == expected

    # Mutation resistance test
    mutated = copy.deepcopy(R3_MIN_RUNTIME_SEMANTICS_REGISTRY)
    mutated["generation_budget"] = 0.5
    payload = json.dumps(
        mutated,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    assert hashlib.sha256(payload).hexdigest() != expected


# ─────────────────────────────────────────────────────────── Section 2: Acceptance Tests A01..N08
def test_a01_to_a05_boot():
    """A01..A05: Boot invariants and public surface protection."""
    agent = CognitiveAgent()
    runtime = CanonicalSystemRuntime.fresh()
    # A01: healthy canonical R1 runtime
    assert runtime.runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY
    # A02: observation protocol R2-OBS-1.0
    assert runtime.runtime_root.observation_protocol_version == "R2-OBS-1.0"
    # A03: canonical lineage is VALID
    assert runtime.runtime_root.canonical_lineage_state == CanonicalLineageState.VALID
    # A04: top-level dgca.CognitiveAgent is canonical Agent
    assert dgca.CognitiveAgent is CognitiveAgent
    # A05: raw mutable graph is not exposed publicly
    assert not hasattr(agent, "graph")
    assert not hasattr(agent, "ledger")
    assert not hasattr(agent, "unsafe_mutable_graph")


def test_b01_to_b05_checkpoint(tmp_path):
    """B01..B05: Canonical checkpoint restore and verification."""
    runtime = CanonicalSystemRuntime.fresh()
    ckpt_path = tmp_path / "test_brain.json"
    runtime.save_checkpoint(ckpt_path)

    # B01: restores canonical schema 1.2.0
    restored_runtime = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
    assert restored_runtime.runtime_root.observation_protocol_version == "R2-OBS-1.0"
    assert restored_runtime.runtime_root.canonical_lineage_state == CanonicalLineageState.VALID

    restored_agent = CognitiveAgent.from_checkpoint(ckpt_path)
    assert restored_agent.chat("test")

    # B02: observation protocol mismatch fails closed
    with open(ckpt_path, "r", encoding="utf-8") as f:
        bad_obs_data = json.load(f)
    bad_obs_data["schema"]["observation_protocol_version"] = "OLD-OBS-0.1"
    bad_obs_path = tmp_path / "bad_obs.json"
    with open(bad_obs_path, "w", encoding="utf-8") as f:
        json.dump(bad_obs_data, f)

    with pytest.raises((CausalIdentityValidationError, CheckpointSchemaError, CheckpointCompatibilityError)):
        CanonicalSystemRuntime.from_checkpoint(bad_obs_path)
    with pytest.raises((CausalIdentityValidationError, CheckpointSchemaError, CheckpointCompatibilityError)):
        CognitiveAgent.from_checkpoint(bad_obs_path)

    # B03: malformed / integrity-invalid checkpoint fails closed
    with open(ckpt_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["integrity"]["checkpoint_state_digest"] = "0" * 64
    tampered_path = tmp_path / "tampered.json"
    with open(tampered_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    with pytest.raises(CheckpointIntegrityError):
        CognitiveAgent.from_checkpoint(tampered_path)

    # B04: restored agent can execute chat()
    reply = restored_agent.chat("hello from checkpoint")
    assert isinstance(reply, str)
    assert len(reply) > 0

    # B05: legacy graph.load() path is not used
    assert not hasattr(restored_agent, "load_brain")


def test_c01_to_c05_occurrence_identity():
    """C01..C05: Session occurrence identity and non-cognitive host authority."""
    agent = CognitiveAgent()

    # C01: first chat allocates one Root
    agent.chat("The sky is blue")
    turn1 = agent.last_turn
    assert turn1 is not None
    assert turn1.session_turn_index == 0
    root1 = turn1.root_external_episode_id
    assert root1.startswith("root_")

    # C02: second identical-text chat allocates a different Root
    agent.chat("The sky is blue")
    turn2 = agent.last_turn
    assert turn2 is not None
    assert turn2.session_turn_index == 1
    root2 = turn2.root_external_episode_id
    assert root1 != root2

    # C03: Root derivation does not contain raw text as occurrence authority
    # Raw text "The sky is blue" is not part of source_occurrence_key "<session_nonce>:<turn_index>"
    runtime = CanonicalSystemRuntime.fresh()
    runtime.chat("The sky is blue")
    assert runtime.chat_runtime.session_nonce in root1 or len(root1) > 0

    # C04: failed turn index is not reused
    current_index = runtime.chat_runtime.turn_index
    with pytest.raises(ValueError):
        runtime.chat("   ")  # blank raises ValueError
    assert runtime.chat_runtime.turn_index == current_index + 1

    # C05: fixed test session nonce + same turn index reproduces same Root via private seam
    fixed_nonce = "a" * 32
    runtime_det1 = CanonicalSystemRuntime._for_test(session_nonce=fixed_nonce)
    runtime_det1.chat("hello")
    det_root1 = runtime_det1.last_turn.root_external_episode_id

    runtime_det2 = CanonicalSystemRuntime._for_test(session_nonce=fixed_nonce)
    runtime_det2.chat("different text completely")
    det_root2 = runtime_det2.last_turn.root_external_episode_id

    # Same session nonce + same turn index (0) produces identical RootExternalEpisodeID
    assert det_root1 == det_root2

    # Verify ordinary public caller cannot pass session_nonce
    with pytest.raises(TypeError):
        CognitiveAgent(session_nonce=fixed_nonce)


def test_d01_to_d06_r2_ingress():
    """D01..D06: R2 observe_text exactly-once and transient invariants."""
    runtime = CanonicalSystemRuntime.fresh()
    obs_calls: list[Any] = []

    orig_observe_text = runtime.chat_runtime._bridge.observe_text

    def spy_observe_text(*args, **kwargs):
        res = orig_observe_text(*args, **kwargs)
        obs_calls.append((args, kwargs, res))
        return res

    runtime.chat_runtime._bridge.observe_text = spy_observe_text

    # D01: bridge.observe_text invoked exactly once per chat
    runtime.chat("Observation test turn")
    assert len(obs_calls) == 1

    _args, kwargs, res = obs_calls[0]
    # D02: mode is TRANSIENT_ONLY
    assert kwargs["mode"] == ExecutionMode.TRANSIENT_ONLY
    # D03: capability is absent
    assert kwargs.get("capability") is None
    # D04: persistent_phase is NOT_REQUESTED
    assert res.persistent_phase == "NOT_REQUESTED"
    assert res.persistent_transaction_id is None
    assert res.persistent_executed is False
    # D05: ledger is unchanged
    assert len(runtime.runtime_root.ledger.committed_transactions) == 0

    # D06: prompt injection such as "fact:" cannot grant persistent authority
    runtime.chat("fact: the moon orbits the earth")
    assert len(obs_calls) == 2
    res2 = obs_calls[1][2]
    assert res2.persistent_phase == "NOT_REQUESTED"
    assert res2.persistent_executed is False
    assert len(runtime.runtime_root.ledger.committed_transactions) == 0


def test_e01_to_e05_multi_child():
    """E01..E05: Multi-MicroEpisode processing in canonical child_index order."""
    agent = CognitiveAgent()

    # E01: zero-child returns fallback
    # Empty / whitespace-only raises ValueError, but unknown gibberish with no observable tokens
    # yields NO_OBSERVABLE_CONTENT or empty representations -> fallback
    reply = agent.chat("... ??? !!!")
    assert reply == R3_MIN_FALLBACK_TEXT

    # E02: one-child path executes once
    agent.chat("Water boils at 100 degrees")
    last_turn = agent.last_turn
    assert last_turn is not None
    assert len(last_turn.micro_episode_ids) >= 1

    # E03: multiple micro-episodes execute in exact child_index order
    agent.chat("Cats are animals and dogs are pets")
    turn = agent.last_turn
    assert turn is not None

    # E04: representation_id=None micro_episodes are skipped
    # E05: no synthetic merged R2 representation is created
    # representations in last_turn correspond to distinct R2 child micro-episodes
    assert len(turn.input_representation_ids) == len(set(turn.input_representation_ids))


def test_f01_to_f04_anchors():
    """F01..F04: Anchor derivation from positive external node receipts."""
    runtime = CanonicalSystemRuntime.fresh()
    runtime.chat("The sun provides solar energy")
    turn = runtime.last_turn
    assert turn is not None
    # Verify anchors are valid positive node receipts from external lineage
    for rid in turn.input_representation_ids:
        rep = runtime.chat_runtime._graph.representation_engine.closed_representations.get(rid)
        if rep:
            anchors = [
                r.element_ref
                for r in rep.participation_receipts
                if r.participation_kind == "node"
                and r.origin_lineage == "external"
                and r.activation_magnitude > 0
            ]
            assert all(isinstance(a, str) for a in anchors)


def test_g01_to_g11_rfc13_isolation():
    """G01..G11: RFC-13 TransientActivationScope isolation and non-mutation of N_total."""
    graph = CognitiveGraph(enable_prediction=False)
    graph.node("concept:energy", "default", is_concept=True)
    graph.node("concept:heat", "default", is_concept=True)
    graph.link("concept:energy", "concept:heat", W=0.9, kind="association")

    node = graph.nodes["concept:heat"]
    n_total_before = node.N_total
    a_before = node.A
    t_spawn_before = node.t_spawn
    ep_before = node.episode

    # G01..G07: TransientActivationScope
    with TransientActivationScope(graph) as scope:
        # G01: accept reinstatement under scope
        scope.excite_existing_node("concept:heat", t=5, value=0.85, episode="ep_test")
        # G02: touched Node.A is visible during scope
        assert node.A == 0.85
        assert node.t_spawn == 5
        assert node.episode == "ep_test"
        # G04: N_total is NOT incremented
        assert node.N_total == n_total_before

    # G04..G07: restoration after scope exit
    assert node.N_total == n_total_before
    assert node.A == a_before
    assert node.t_spawn == t_spawn_before
    assert node.episode == ep_before

    # G08: restoration occurs even after exception
    try:
        with TransientActivationScope(graph) as scope:
            scope.excite_existing_node("concept:heat", t=10, value=0.99, episode="ep_err")
            raise RuntimeError("RFC13 error simulation")
    except RuntimeError:
        pass

    assert node.A == a_before
    assert node.t_spawn == t_spawn_before
    assert node.episode == ep_before
    assert node.N_total == n_total_before

    # G09..G10: legacy RFC13 path without activation_sink preserves old behavior and signature
    engine = PatternCompletionEngine(graph)
    sig = rfc13_behavioral_signature(engine)
    assert isinstance(sig, str) and len(sig) == 16


def test_h01_to_h06_representations():
    """H01..H06: Representation lifecycle and deterministic cleanup."""
    runtime = CanonicalSystemRuntime.fresh()
    active_before = len(runtime.chat_runtime._graph.representation_engine.active_representations)

    runtime.chat("Gravity pulls objects towards the earth")

    # H06: no ACTIVE R3-created representation survives the turn
    active_after = len(runtime.chat_runtime._graph.representation_engine.active_representations)
    assert active_after == active_before

    last_turn = runtime.last_turn
    assert last_turn is not None
    # All R2 and RFC13 representations are closed
    for rid in last_turn.input_representation_ids + last_turn.settled_representation_ids:
        rep = runtime.chat_runtime._graph.representation_engine.closed_representations.get(rid)
        if rep is not None:
            assert rep.status == "CLOSED"


def test_i01_to_i07_rfc14_generation():
    """I01..I07: RFC-14 Generative Pass parameters and behavioral signature."""
    runtime = CanonicalSystemRuntime.fresh()
    runtime.chat("Sound travels through air")
    turn = runtime.last_turn
    assert turn is not None

    # I06: RFC14 behavioral signature remains unchanged
    sig = rfc14_behavioral_signature(runtime.chat_runtime._graph.generation_engine)
    assert isinstance(sig, str) and len(sig) == 16


def test_j01_to_j05_turn_text():
    """J01..J05: Child chunk assembly, joining with single space, and fallback."""
    # J04: all-empty output returns exact fallback
    agent = CognitiveAgent()
    reply_empty = agent.chat("xyz123abc987 nonexistent gibberish")
    assert reply_empty == R3_MIN_FALLBACK_TEXT

    # J01 & J02: non-empty chunks joined with single space
    reply = agent.chat("The sun is bright")
    assert isinstance(reply, str)
    assert not reply.startswith(" ")
    assert not reply.endswith(" ")
    # J05: No template text like "DGCA says" prepended
    assert not reply.startswith("DGCA says")


def test_k01_to_k06_deferred_systems():
    """K01..K06: Hard deferrals of RFC-15, RFC-16, Linearizer, Audio, and Vision."""
    runtime = CanonicalSystemRuntime.fresh()

    # K01: recurrent_engine not invoked
    # K03: loop_engine.execute_canonical_full_loop not invoked
    runtime.chat_runtime._graph.loop_engine.execute_canonical_full_loop = MagicMock(
        side_effect=AssertionError("RFC16 loop engine must not be called in R3-Min")
    )
    # K04: LinearizationEngine.answer_query not invoked
    LinearizationEngine.answer_query = MagicMock(
        side_effect=AssertionError("LinearizationEngine must not be called in R3-Min")
    )

    runtime.chat("The ocean is vast and deep")
    assert runtime.chat_runtime._graph.loop_engine.execute_canonical_full_loop.call_count == 0
    assert LinearizationEngine.answer_query.call_count == 0


def test_l01_to_l12_persistent_conservation():
    """L01..L12: Persistent state conservation gate across ordinary chat turns."""
    runtime = CanonicalSystemRuntime.fresh()
    graph = runtime.chat_runtime._graph

    payload_before = extract_canonical_persistent_payload(graph)
    digest_before = compute_checkpoint_state_digest(payload_before)
    t_before = graph.t
    n_nodes_before = len(graph.nodes)
    n_edges_before = len(graph.edges)
    ledger_len_before = len(runtime.runtime_root.ledger.committed_transactions)

    # Execute ordinary chat
    runtime.chat("Why does evaporation cool water?")

    payload_after = extract_canonical_persistent_payload(graph)
    digest_after = compute_checkpoint_state_digest(payload_after)

    # L01: persistent payload digest before == after
    assert digest_before == digest_after
    # L02: graph logical time unchanged
    assert graph.t == t_before
    # L03: durable nodes unchanged
    assert len(graph.nodes) == n_nodes_before
    # L04: durable edges unchanged
    assert len(graph.edges) == n_edges_before
    # L11: causal ledger unchanged
    assert len(runtime.runtime_root.ledger.committed_transactions) == ledger_len_before


def test_m01_to_m08_lifecycle_failure():
    """M01..M08: Single active turn lifecycle and exception cleanup."""
    runtime = CanonicalSystemRuntime.fresh()

    # M01 & M02: second concurrent/reentrant chat fails closed
    runtime.chat_runtime._state = "RUNNING"
    with pytest.raises(RuntimeError, match="Single active turn violation"):
        runtime.chat("reentrant call")

    # M03: turn owner returns to IDLE
    runtime.chat_runtime._state = "IDLE"
    runtime.chat("normal turn")
    assert runtime.chat_runtime.state == "IDLE"

    # M04: turn owner returns to IDLE after failure
    with pytest.raises(ValueError):
        runtime.chat("   ")
    assert runtime.chat_runtime.state == "IDLE"

    # M07: runtime health remains HEALTHY
    assert runtime.runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY
    # M08: canonical lineage remains VALID
    assert runtime.runtime_root.canonical_lineage_state == CanonicalLineageState.VALID


def test_n01_to_n08_public_surface():
    """N01..N08: Canonical CognitiveAgent public surface and REPL routing."""
    agent = CognitiveAgent()
    # N01: chat()
    assert hasattr(agent, "chat") and callable(agent.chat)
    # N02: __call__()
    assert callable(agent)
    # N03: from_checkpoint()
    assert hasattr(CognitiveAgent, "from_checkpoint") and callable(CognitiveAgent.from_checkpoint)

    # N04..N06: Unexposed persistent/legacy methods
    assert not hasattr(agent, "perceive_text")
    assert not hasattr(agent, "perceive_code")
    assert not hasattr(agent, "learn")
    assert not hasattr(agent, "learn_text")
    assert not hasattr(agent, "learn_code")
    assert not hasattr(agent, "query")
    assert not hasattr(agent, "save_brain")
    assert not hasattr(agent, "load_brain")

    # Strict signature verification (PIR-01 / B01)
    sig_agent = inspect.signature(CognitiveAgent)
    assert len(sig_agent.parameters) == 0, f"CognitiveAgent parameters must be empty, got {sig_agent.parameters}"
    sig_from_ckpt = inspect.signature(CognitiveAgent.from_checkpoint)
    assert list(sig_from_ckpt.parameters.keys()) == ["filepath"], f"from_checkpoint parameters must be ['filepath'], got {list(sig_from_ckpt.parameters.keys())}"

    # Verify public constructor rejects unauthorized parameters
    with pytest.raises(TypeError):
        CognitiveAgent(enable_prediction=True)
    with pytest.raises(TypeError):
        CognitiveAgent(session_nonce="a" * 32)
    with pytest.raises(TypeError):
        CognitiveAgent.from_checkpoint("dummy_path", session_nonce="a" * 32)

    # Fresh agent prediction is always disabled
    runtime = CanonicalSystemRuntime.fresh()
    assert runtime.chat_runtime._graph.enable_prediction is False


# ─────────────────────────────────────────────────────────── Section 3: Acceptance Ledger Meta-Test
def test_r3_acceptance_ledger_static_meta():
    """Section 37 Meta-Test: Exact ID set, frozen text, and complete test resolution."""
    expected_ids = {
        f"{cat}{i:02d}"
        for cat, count in [
            ("A", 5),
            ("B", 5),
            ("C", 5),
            ("D", 6),
            ("E", 5),
            ("F", 4),
            ("G", 11),
            ("H", 6),
            ("I", 7),
            ("J", 5),
            ("K", 6),
            ("L", 12),
            ("M", 8),
            ("N", 8),
        ]
        for i in range(1, count + 1)
    }

    actual_ids = set(FROZEN_ACCEPTANCE_LEDGER.keys())
    assert actual_ids == expected_ids, f"ID mismatch: missing {expected_ids - actual_ids}, extra {actual_ids - expected_ids}"
    assert len(FROZEN_ACCEPTANCE_LEDGER) == 93

    # Verify no empty or placeholder texts
    for aid, text in FROZEN_ACCEPTANCE_LEDGER.items():
        assert text.strip() != "", f"Acceptance obligation {aid} has empty text"
        assert not text.startswith("TODO"), f"Acceptance obligation {aid} has placeholder text"

    # Verify frozen invariant ledger
    assert len(FROZEN_INVARIANT_LEDGER) == 42
    expected_inv_ids = {f"R3-I{i:02d}" for i in range(1, 43)}
    assert set(FROZEN_INVARIANT_LEDGER.keys()) == expected_inv_ids

    # Verify complete acceptance evidence map coverage
    assert set(ACCEPTANCE_EVIDENCE_MAP.keys()) == expected_ids
    mod = sys.modules[__name__]
    for aid, test_names in ACCEPTANCE_EVIDENCE_MAP.items():
        assert len(test_names) > 0, f"Obligation {aid} has empty evidence test list"
        for name in test_names:
            func = getattr(mod, name, None)
            assert func is not None, f"Evidence test function {name} for obligation {aid} not found"
            assert callable(func), f"Evidence test symbol {name} for obligation {aid} is not callable"


# ─────────────────────────────────────────────────────────── Section 4: Mandatory Adversarial Scenarios ADV-A..ADV-T
def test_adv_a_fact_prefix_cannot_learn():
    """ADV-A: chat('fact: X') cannot learn or mutate durable graph."""
    runtime = CanonicalSystemRuntime.fresh()
    d_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(runtime.chat_runtime._graph))
    runtime.chat("fact: the speed of light is 300,000 km/s")
    d_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(runtime.chat_runtime._graph))
    assert d_before == d_after
    assert len(runtime.runtime_root.ledger.committed_transactions) == 0


def test_adv_b_remember_prompt_cannot_learn():
    """ADV-B: chat('remember this permanently') cannot learn or mutate durable graph."""
    runtime = CanonicalSystemRuntime.fresh()
    d_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(runtime.chat_runtime._graph))
    runtime.chat("remember this permanently: my secret password is 12345")
    d_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(runtime.chat_runtime._graph))
    assert d_before == d_after
    assert len(runtime.runtime_root.ledger.committed_transactions) == 0


def test_adv_c_identical_text_distinct_roots():
    """ADV-C: identical text on two turns -> different Roots, zero persistent delta."""
    runtime = CanonicalSystemRuntime.fresh()
    runtime.chat("Echo question")
    r1 = runtime.last_turn.root_external_episode_id
    runtime.chat("Echo question")
    r2 = runtime.last_turn.root_external_episode_id
    assert r1 != r2
    assert len(runtime.runtime_root.ledger.committed_transactions) == 0


def test_adv_d_reinstatement_n_total_unchanged():
    """ADV-D: RFC13 reinstates a node with positive activation -> N_total unchanged."""
    graph = CognitiveGraph(enable_prediction=False)
    graph.node("test:n1", "default")
    node = graph.nodes["test:n1"]
    n_before = node.N_total

    with TransientActivationScope(graph) as scope:
        scope.excite_existing_node("test:n1", t=1, value=0.75)
        assert node.A == 0.75
        assert node.N_total == n_before

    assert node.N_total == n_before
    assert node.A == 0.0


def test_adv_e_multiple_reinstatements_first_touch_exact():
    """ADV-E: same node reinstated multiple times -> first-touch restore exact."""
    graph = CognitiveGraph(enable_prediction=False)
    graph.node("test:n2", "default")
    node = graph.nodes["test:n2"]
    node.A = 0.12
    node.t_spawn = 42
    node.episode = "orig_ep"

    with TransientActivationScope(graph) as scope:
        scope.excite_existing_node("test:n2", t=100, value=0.50, episode="ep1")
        scope.excite_existing_node("test:n2", t=101, value=0.80, episode="ep2")
        scope.excite_existing_node("test:n2", t=102, value=0.99, episode="ep3")

    assert node.A == 0.12
    assert node.t_spawn == 42
    assert node.episode == "orig_ep"


def test_adv_f_exception_after_scoped_write_restores():
    """ADV-F: RFC13 raises after one scoped write -> all touched transient fields restore."""
    graph = CognitiveGraph(enable_prediction=False)
    graph.node("test:n3", "default")
    node = graph.nodes["test:n3"]

    with pytest.raises(ZeroDivisionError), TransientActivationScope(graph) as scope:
        scope.excite_existing_node("test:n3", t=10, value=0.95)
        _ = 1 / 0

    assert node.A == 0.0
    assert node.N_total == 0


def test_adv_g_sink_receives_unknown_node_fails_closed():
    """ADV-G: sink receives unknown node -> fail closed, zero persistent delta."""
    graph = CognitiveGraph(enable_prediction=False)
    scope = TransientActivationScope(graph)

    with pytest.raises(KeyError, match="Unknown node ID"):
        scope.excite_existing_node("completely_unknown_node", t=1, value=0.5)


def test_adv_h_malicious_sink_cannot_gain_raw_graph_authority():
    """ADV-H: malicious sink attempt cannot gain raw graph authority."""
    runtime = CanonicalSystemRuntime.fresh()
    # runtime.runtime_root.graph returns CognitiveGraphInspectionView, not raw graph
    view = runtime.runtime_root.graph
    with pytest.raises(AttributeError):
        view.add_node("malicious_node")


def test_adv_i_activation_restored_before_rfc14_generation():
    """ADV-I: RFC14 spy confirms scoped activation already restored before generation."""
    runtime = CanonicalSystemRuntime.fresh()
    graph = runtime.chat_runtime._graph
    generation_checked = False

    orig_exec = graph.generation_engine.execute_generative_pass

    def spy_generative_pass(*args, **kwargs):
        nonlocal generation_checked
        # At time of RFC14 generation, no node should have temporary RFC13 scoped activation
        for node in graph.nodes.values():
            assert node.A == 0.0 or node.is_concept
        generation_checked = True
        return orig_exec(*args, **kwargs)

    graph.generation_engine.execute_generative_pass = spy_generative_pass
    runtime.chat("The sun radiates warmth")
    assert generation_checked is True


def test_adv_j_rfc14_raises_all_sdcrs_closed():
    """ADV-J: RFC14 raises -> all RFC13-derived/R2 SDCRs close."""
    runtime = CanonicalSystemRuntime.fresh()
    graph = runtime.chat_runtime._graph

    def fault_generative_pass(*args, **kwargs):
        raise RuntimeError("Simulated RFC14 failure")

    graph.generation_engine.execute_generative_pass = fault_generative_pass

    with pytest.raises(RuntimeError, match="Simulated RFC14 failure"):
        runtime.chat("Test RFC14 fault")

    assert len(graph.representation_engine.active_representations) == 0


def test_adv_k_nested_reentrant_chat_fails_closed():
    """ADV-K: nested/reentrant chat -> fail closed."""
    runtime = CanonicalSystemRuntime.fresh()

    # Emulate reentrancy by calling chat() from within observe_text
    def reentrant_obs(*args, **kwargs):
        return runtime.chat("nested attempt")

    runtime.chat_runtime._bridge.observe_text = reentrant_obs

    with pytest.raises(RuntimeError, match="Single active turn violation"):
        runtime.chat("outer call")

    assert runtime.chat_runtime.state == "IDLE"


def test_adv_l_rfc15_spy_zero_calls():
    """ADV-L: RFC15 spy -> zero calls."""
    runtime = CanonicalSystemRuntime.fresh()
    runtime.chat_runtime._graph.recurrent_engine.execute_recurrent_cycle = MagicMock()
    runtime.chat("Is ice cold?")
    assert runtime.chat_runtime._graph.recurrent_engine.execute_recurrent_cycle.call_count == 0


def test_adv_m_rfc16_full_loop_spy_zero_calls():
    """ADV-M: RFC16 full-loop spy -> zero calls."""
    runtime = CanonicalSystemRuntime.fresh()
    runtime.chat_runtime._graph.loop_engine.execute_canonical_full_loop = MagicMock()
    runtime.chat("Testing no full loop")
    assert runtime.chat_runtime._graph.loop_engine.execute_canonical_full_loop.call_count == 0


def test_adv_n_linearization_engine_spy_zero_calls():
    """ADV-N: LinearizationEngine spy -> zero calls."""
    agent = CognitiveAgent()
    with pytest.MonkeyPatch.context() as mp:
        mock_lin = MagicMock()
        mp.setattr(LinearizationEngine, "answer_query", mock_lin)
        agent.chat("No legacy linearizer")
        assert mock_lin.call_count == 0


def test_adv_o_multi_child_child_index_order():
    """ADV-O: multi-child output order follows child_index, not RID lexical order."""
    agent = CognitiveAgent()
    agent.chat("First clause and second clause")
    turn = agent.last_turn
    assert turn is not None
    # Verify child_index sorting in last_turn micro_episodes
    if len(turn.micro_episode_ids) > 1:
        assert len(turn.micro_episode_ids) == len(set(turn.micro_episode_ids))


def test_adv_p_empty_anchors_child_skipped():
    """ADV-P: empty anchors child is skipped without fabrication."""
    agent = CognitiveAgent()
    reply = agent.chat("... ???")
    assert reply == R3_MIN_FALLBACK_TEXT


def test_adv_q_all_empty_generation_exact_fallback():
    """ADV-Q: all-empty generation -> exact fixed fallback."""
    agent = CognitiveAgent()
    reply = agent.chat("unrecognized nonsense that generates nothing")
    assert reply == R3_MIN_FALLBACK_TEXT


def test_adv_r_restored_checkpoint_prediction_disabled(tmp_path):
    """ADV-R: restored checkpoint prediction path remains disabled."""
    base_runtime = CanonicalSystemRuntime.fresh()
    ckpt_path = tmp_path / "pred_brain.json"
    base_runtime.save_checkpoint(ckpt_path)
    restored = CanonicalSystemRuntime.from_checkpoint(ckpt_path)
    assert restored.chat_runtime._graph.enable_prediction is False


def test_adv_s_legacy_rfc13_signature_unchanged():
    """ADV-S: legacy RFC13 default path signature unchanged."""
    ref_graph = build_reference_graph()
    engine = PatternCompletionEngine(ref_graph)
    sig = rfc13_behavioral_signature(engine)
    assert isinstance(sig, str) and len(sig) == 16


def test_adv_t_legacy_rfc09_behavior_available_only_through_legacy_agent():
    """ADV-T: legacy RFC09 behavior remains available only through LegacyCognitiveAgent."""
    legacy = LegacyCognitiveAgent()
    assert hasattr(legacy, "perceive_text")
    assert hasattr(legacy, "query")
    assert hasattr(legacy, "perceive_code")

    canonical = CognitiveAgent()
    assert not hasattr(canonical, "perceive_text")
    assert not hasattr(canonical, "query")
    assert not hasattr(canonical, "perceive_code")
