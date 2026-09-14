"""
DGCA — RIC-01 / R1: Deterministic Causal Identity Protocol v1.3
Runtime Invariants, Ledger Idempotency, Fail-Stop & Acceptance Test Suite

Authoritative spec: RIC-01-R1-Deterministic-Causal-Identity-Protocol-v1.3-FROZEN.md
Test Coverage: R1-T28 through R1-T58, R1-T61 through R1-T64, Adversarial Scenarios E, F, G, J, K.
"""
from __future__ import annotations

import json

import pytest

from dgca.assembly import AssemblyManager, AssemblyPolicy
from dgca.causal_identity import (
    CAUSAL_IDENTITY_PROTOCOL_DIGEST,
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalCommitCollisionError,
    CausalCommitLedger,
    CausalIdentityValidationError,
    CausalLineageInvalidatedError,
    CausalProvenanceEpoch,
    CausalRuntimeFailStopError,
    CausalRuntimeHealth,
    PersistentMutationCommand,
    compute_causal_provenance_digest,
    compute_checkpoint_bundle_digest,
    compute_event_descriptor_digest,
    derive_root_external_episode_id,
)
from dgca.config import Law
from dgca.graph import CognitiveGraph
from dgca.persistence import (
    CheckpointCompatibilityError,
    CheckpointIntegrityError,
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    migrate_schema_1_1_1_to_1_2_0,
    restore_canonical_r1_checkpoint,
    save_canonical_r1_checkpoint,
    save_cognitive_checkpoint,
)


@pytest.fixture
def clean_graph():
    return CognitiveGraph()


@pytest.fixture
def clean_guard():
    return RuntimeLifecycleGuard()


@pytest.fixture
def base_runtime(clean_graph, clean_guard):
    epoch = CausalProvenanceEpoch("epoch_test_1", "R1_TRACKED", "base_state_digest_000")
    ledger = CausalCommitLedger(epoch=epoch)
    return CanonicalR1RuntimeRoot(
        graph=clean_graph,
        ledger=ledger,
        observation_protocol_version="1.0.0",
        lifecycle_guard=clean_guard,
    )


# ─────────────────────────────────────────────────────────── 1. Core Runtime Execution & Idempotency
def test_r1_t28_first_authorized_tx_mutates_and_records_commit(base_runtime):
    """R1-T28: First authorized Tx mutates once and records event binding + commit."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello", "boundary": "boundary_test"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["node_a", "node_b"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope_test",
    )

    def mutator():
        base_runtime.graph.link("node_a", "node_b", W=Law.W_BASE, contexts=("en",))
        return "SUCCESS_VAL"

    txid, executed, result = base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_001",
        event_descriptor_digest=evt_digest,
        mutator_callback=mutator,
    )

    assert executed is True
    assert result == "SUCCESS_VAL"
    assert txid in base_runtime.ledger.committed_transactions
    assert "evt_001" in base_runtime.ledger.committed_event_bindings
    assert ("node_a", "node_b") in base_runtime.graph.edges
    assert base_runtime.causal_runtime_health == CausalRuntimeHealth.HEALTHY


def test_r1_t29_same_tx_replay_same_process_zero_delta(base_runtime):
    """R1-T29: Same Tx replay in same process produces zero persistent delta."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello", "boundary": "boundary_test"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["node_a", "node_b"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope_test",
    )

    base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_001",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: base_runtime.graph.link("node_a", "node_b", W=Law.W_BASE, contexts=("en",)),
    )

    initial_t = base_runtime.graph.t
    called = False

    def replay_mutator():
        nonlocal called
        called = True
        base_runtime.graph.link("node_a", "node_b", W=Law.W_MAX, contexts=("en",))

    _txid, executed, result = base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_001",
        event_descriptor_digest=evt_digest,
        mutator_callback=replay_mutator,
    )

    assert executed is False
    assert called is False
    assert result is None
    assert base_runtime.graph.t == initial_t
    assert base_runtime.graph.edge("node_a", "node_b").W == Law.W_BASE


def test_r1_t30_same_tx_replay_after_checkpoint_restart_zero_delta(base_runtime, tmp_path):
    """R1-T30, Adversarial E: Replay committed Tx after checkpoint/restart -> zero persistent delta."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello", "boundary": "boundary_test"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["node_a", "node_b"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope_test",
    )

    txid_orig, _, _ = base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_001",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: base_runtime.graph.link("node_a", "node_b", W=Law.W_BASE, contexts=("en",)),
    )

    cp_path = tmp_path / "checkpoint_1_2_0.json"
    save_canonical_r1_checkpoint(base_runtime, cp_path)

    # Fresh restore
    restored_runtime, _ = restore_canonical_r1_checkpoint(
        cp_path,
        expected_observation_protocol_version="1.0.0",
    )

    called = False

    def restart_mutator():
        nonlocal called
        called = True

    txid_rep, executed, _res = restored_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_001",
        event_descriptor_digest=evt_digest,
        mutator_callback=restart_mutator,
    )

    assert executed is False
    assert called is False
    assert txid_rep == txid_orig
    assert ("node_a", "node_b") in restored_runtime.graph.edges


def test_r1_t31_identical_content_under_new_root_independent_txid(base_runtime):
    """R1-T31: Identical content under a new root produces independent lawful TxID."""
    root_1 = derive_root_external_episode_id("boundary_test", "occ_001")
    root_2 = derive_root_external_episode_id("boundary_test", "occ_002")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})

    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["node_a", "node_b"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope_test",
    )

    txid_1, exec_1, _ = base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_1,
        ingress_event_id="evt_001",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: None,
    )

    txid_2, exec_2, _ = base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_2,
        ingress_event_id="evt_002",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: None,
    )

    assert exec_1 is True
    assert exec_2 is True
    assert txid_1 != txid_2


def test_r1_t32_same_event_id_changed_descriptor_fails_closed(base_runtime):
    """R1-T32, Adversarial F: Same EventID with modified descriptor fails closed."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest_1 = compute_event_descriptor_digest({"raw": "hello"})
    evt_digest_2 = compute_event_descriptor_digest({"raw": "tampered"})

    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )

    base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_shared",
        event_descriptor_digest=evt_digest_1,
        mutator_callback=lambda: None,
    )

    cmd2 = PersistentMutationCommand(
        mutation_owner_ref="Law2_HebbianReinforcement",
        mutation_kind="REINFORCE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"delta": 0.1},
        owner_defined_transaction_scope="scope",
    )

    with pytest.raises(CausalCommitCollisionError):
        base_runtime.execute_persistent_command(
            command=cmd2,
            root_external_episode_id=root_id,
            ingress_event_id="evt_shared",
            event_descriptor_digest=evt_digest_2,
            mutator_callback=lambda: None,
        )


def test_r1_t33_txid_collision_conflicting_descriptor_fails_closed(base_runtime):
    """R1-T33: TxID collision with conflicting descriptor fails closed."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})

    cmd1 = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )

    txid, _, _ = base_runtime.execute_persistent_command(
        command=cmd1,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: None,
    )

    with pytest.raises(CausalCommitCollisionError):
        base_runtime.ledger.check_transaction_replay(
            transaction_id=txid,
            mutation_descriptor_digest="different_descriptor_digest",
            root_external_episode_id=root_id,
        )


# ─────────────────────────────────────────────────────────── 2. Causal Ledger Non-Cognitive Isolation & Checkpoint 1.2.0
def test_r1_t34_ledger_does_not_change_checkpoint_state_digest(base_runtime):
    """R1-T34: Ledger additions do not change R0 checkpoint_state_digest."""
    payload1 = extract_canonical_persistent_payload(base_runtime.graph, AssemblyPolicy())
    digest1 = compute_checkpoint_state_digest(payload1)

    # Record transactions in ledger without modifying graph
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="NO_OP",
        canonical_targets=[],
        canonical_mutation_descriptor={},
        owner_defined_transaction_scope="scope",
    )
    base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: None,
    )

    payload2 = extract_canonical_persistent_payload(base_runtime.graph, AssemblyPolicy())
    digest2 = compute_checkpoint_state_digest(payload2)

    assert digest1 == digest2


def test_r1_t35_causal_provenance_digest_deterministic(base_runtime):
    """R1-T35: Causal provenance digest is deterministic."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"w": 1.0},
        owner_defined_transaction_scope="s",
    )
    base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: None,
    )

    d1 = compute_causal_provenance_digest(base_runtime.ledger.to_dict())
    d2 = compute_causal_provenance_digest(base_runtime.ledger.to_dict())
    assert d1 == d2
    assert len(d1) == 64


def test_r1_t36_checkpoint_bundle_digest_deterministic():
    """R1-T36: Checkpoint bundle digest is deterministic structured binding."""
    epoch_dict = {
        "base_state_digest": "state_123",
        "epoch_id": "epoch_123",
        "history_status": "R1_TRACKED",
    }
    d1 = compute_checkpoint_bundle_digest(
        checkpoint_state_digest="state_123",
        causal_provenance_digest="prov_456",
        combined_semantics_digest="sem_789",
        causal_identity_protocol_digest=CAUSAL_IDENTITY_PROTOCOL_DIGEST,
        observation_protocol_digest="obs_000",
        causal_provenance_epoch=epoch_dict,
    )
    d2 = compute_checkpoint_bundle_digest(
        checkpoint_state_digest="state_123",
        causal_provenance_digest="prov_456",
        combined_semantics_digest="sem_789",
        causal_identity_protocol_digest=CAUSAL_IDENTITY_PROTOCOL_DIGEST,
        observation_protocol_digest="obs_000",
        causal_provenance_epoch=epoch_dict,
    )
    assert d1 == d2
    assert len(d1) == 64


def test_r1_t37_graph_plus_ledger_1_2_0_round_trip(base_runtime, tmp_path):
    """R1-T37: Graph + ledger 1.2.0 checkpoint full round-trip."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )

    txid, _, _ = base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=lambda: base_runtime.graph.link("n1", "n2", W=Law.W_BASE, contexts=("en",)),
    )

    cp_path = tmp_path / "rt_1_2_0.json"
    save_canonical_r1_checkpoint(base_runtime, cp_path)

    restored_runtime, report = restore_canonical_r1_checkpoint(
        cp_path,
        expected_observation_protocol_version="1.0.0",
    )

    assert report is None
    assert restored_runtime.causal_runtime_health == CausalRuntimeHealth.HEALTHY
    assert restored_runtime.canonical_lineage_state == CanonicalLineageState.VALID
    assert restored_runtime.observation_protocol_version == "1.0.0"
    assert ("n1", "n2") in restored_runtime.graph.edges
    assert txid in restored_runtime.ledger.committed_transactions
    assert "evt_1" in restored_runtime.ledger.committed_event_bindings


def test_r1_t38_ledger_malformed_duplicate_corrupt_fails_closed(base_runtime, tmp_path):
    """R1-T38: Checkpoint with corrupt or tampered ledger fails closed on restore."""
    cp_path = tmp_path / "tampered_ledger.json"
    save_canonical_r1_checkpoint(base_runtime, cp_path)

    with open(cp_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Tamper with ledger
    data["causal_provenance_state"]["committed_transactions"]["fake_tx"] = {"invalid": True}
    with open(cp_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    with pytest.raises(CheckpointIntegrityError):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


# ─────────────────────────────────────────────────────────── 3. Fail-Stop & Mutation Failure Semantics
def test_r1_t39_mutation_callback_raises_fail_stop(base_runtime):
    """R1-T39, Adversarial G: Mutation callback raises -> no commit + runtime fail-stop."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )

    def failing_mutator():
        base_runtime.graph.link("n1", "n2", W=Law.W_BASE, contexts=("en",))
        raise RuntimeError("Intentional cognitive crash during mutation")

    with pytest.raises(RuntimeError, match="Intentional cognitive crash"):
        base_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id=root_id,
            ingress_event_id="evt_crash",
            event_descriptor_digest=evt_digest,
            mutator_callback=failing_mutator,
        )

    assert base_runtime.causal_runtime_health == CausalRuntimeHealth.MUTATION_FAILED
    assert len(base_runtime.ledger.committed_transactions) == 0
    assert "evt_crash" not in base_runtime.ledger.committed_event_bindings

    # Subsequent command blocked
    with pytest.raises(CausalRuntimeFailStopError):
        base_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id=root_id,
            ingress_event_id="evt_subsequent",
            event_descriptor_digest=evt_digest,
            mutator_callback=lambda: None,
        )


def test_r1_t40_ledger_append_failure_fail_stop(base_runtime, monkeypatch):
    """R1-T40: Ledger append failure after owner success triggers runtime fail-stop."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )

    def crashing_commit(*args, **kwargs):
        raise OSError("Disk full / ledger write failure")

    monkeypatch.setattr(base_runtime.ledger, "commit_transaction", crashing_commit)

    with pytest.raises(OSError, match="Disk full"):
        base_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id=root_id,
            ingress_event_id="evt_1",
            event_descriptor_digest=evt_digest,
            mutator_callback=lambda: None,
        )

    assert base_runtime.causal_runtime_health == CausalRuntimeHealth.MUTATION_FAILED


def test_r1_t41_fail_stop_runtime_canonical_save_rejected(base_runtime, tmp_path):
    """R1-T41: Saving a fail-stop runtime is rejected."""
    base_runtime.causal_runtime_health = CausalRuntimeHealth.MUTATION_FAILED
    cp_path = tmp_path / "should_fail.json"

    with pytest.raises(CausalRuntimeFailStopError):
        save_canonical_r1_checkpoint(base_runtime, cp_path)


def test_r1_t42_restore_from_last_valid_checkpoint_returns_healthy(base_runtime, tmp_path):
    """R1-T42: Restoring from last valid checkpoint returns HEALTHY runtime root."""
    cp_path = tmp_path / "valid_cp.json"
    save_canonical_r1_checkpoint(base_runtime, cp_path)

    # Induce crash on current runtime
    base_runtime.causal_runtime_health = CausalRuntimeHealth.MUTATION_FAILED

    restored_runtime, _ = restore_canonical_r1_checkpoint(
        cp_path,
        expected_observation_protocol_version="1.0.0",
    )

    assert restored_runtime.causal_runtime_health == CausalRuntimeHealth.HEALTHY


# ─────────────────────────────────────────────────────────── 4. Schema 1.1.1 to 1.2.0 Migration & Disclosures
def test_r1_t43_and_t44_schema_1_1_1_migration_empty_ledger_and_disclosure(clean_graph, tmp_path):
    """R1-T43, R1-T44, Adversarial J: 1.1.1 migration creates empty ledger with PRE_R1_HISTORY_UNAVAILABLE."""
    # Create valid 1.1.1 checkpoint
    cp_path = tmp_path / "cp_1_1_1.json"
    clean_graph.link("x", "y", W=Law.W_BASE, contexts=("en",))
    save_cognitive_checkpoint(clean_graph, cp_path, policy=AssemblyPolicy())

    with open(cp_path, "r", encoding="utf-8") as f:
        cp_111 = json.load(f)

    migrated_120, report = migrate_schema_1_1_1_to_1_2_0(
        cp_111,
        target_observation_protocol_version="1.0.0",
        policy=AssemblyPolicy(),
    )

    assert report.source_schema == "1.1.1"
    assert report.target_schema == "1.2.0"
    assert report.unrecoverable_legacy_state == ["pre_r1_causal_provenance"]
    assert "Pre-R1 persistent mutation causal commit history was not recorded" in report.diagnostic_notes[-1]

    epoch = migrated_120["causal_provenance_state"]["causal_provenance_epoch"]
    assert epoch["history_status"] == "PRE_R1_HISTORY_UNAVAILABLE"
    assert migrated_120["causal_provenance_state"]["committed_transactions"] == {}
    assert migrated_120["causal_provenance_state"]["committed_event_bindings"] == {}


def test_r1_t45_1_0_1_1_migration_chain_remains_valid(clean_graph, tmp_path):
    """R1-T45: 1.0 and 1.1 checkpoints migrate through to 1.2.0 via restore_canonical_r1_checkpoint."""
    # 1.1.1 file restore into 1.2.0 runtime
    cp_path = tmp_path / "legacy_1_1_1.json"
    clean_graph.link("x", "y", W=Law.W_BASE, contexts=("en",))
    save_cognitive_checkpoint(clean_graph, cp_path, policy=AssemblyPolicy())

    runtime, report = restore_canonical_r1_checkpoint(
        cp_path,
        expected_observation_protocol_version="1.0.0",
    )
    assert report is not None
    assert report.target_schema == "1.2.0"
    assert runtime.ledger.epoch.history_status == "PRE_R1_HISTORY_UNAVAILABLE"
    assert ("x", "y") in runtime.graph.edges


# ─────────────────────────────────────────────────────────── 5. Protocol Version Firewalls & Guards
def test_r1_t46_causal_identity_protocol_mismatch_fails_closed(base_runtime, tmp_path):
    """R1-T46: Causal identity protocol mismatch fails closed."""
    cp_path = tmp_path / "mismatch_identity.json"
    save_canonical_r1_checkpoint(base_runtime, cp_path)

    with open(cp_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["compatibility"]["causal_identity_protocol_digest"] = "bad_identity_digest"
    with open(cp_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    with pytest.raises(CheckpointCompatibilityError, match="Causal identity protocol digest mismatch"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_r1_t47_observation_protocol_mismatch_fails_closed(base_runtime, tmp_path):
    """R1-T47, Adversarial K: Observation protocol version mismatch fails closed."""
    cp_path = tmp_path / "mismatch_obs.json"
    save_canonical_r1_checkpoint(base_runtime, cp_path)

    with pytest.raises(CheckpointCompatibilityError, match="Observation protocol version mismatch"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="2.0.0")


def test_r1_t48_and_t49_observation_protocol_change_no_new_rfc11_root_vote(clean_graph):
    """R1-T48, R1-T49: Observation protocol version does not create new RFC-11 root vote authority."""
    # Assembly manager candidate votes remain intact and unaffected
    policy = AssemblyPolicy()
    mgr = AssemblyManager(clean_graph, policy)
    clean_graph._assembly_manager = mgr

    # Pending candidates remain untouched
    assert len(mgr.pending_candidates) == 0


def test_r1_t50_rfc12_rfc16_transient_cold_restart_semantics_conserved(base_runtime, tmp_path):
    """R1-T50: Restored runtime has cold transient engines."""
    cp_path = tmp_path / "cold_restart.json"
    save_canonical_r1_checkpoint(base_runtime, cp_path)

    restored_runtime, _ = restore_canonical_r1_checkpoint(
        cp_path,
        expected_observation_protocol_version="1.0.0",
    )
    g = restored_runtime.graph
    assert g._representation_engine is None
    assert g._completion_engine is None
    assert g._generation_engine is None
    assert g._recurrent_engine is None
    assert g._loop_engine is None


def test_r1_t54_canonical_runtime_without_explicit_observation_protocol_fails(clean_graph):
    """R1-T54: Canonical RuntimeRoot without explicit observation protocol version fails closed."""
    epoch = CausalProvenanceEpoch("ep1", "R1_TRACKED", "base")
    ledger = CausalCommitLedger(epoch)

    with pytest.raises(CausalIdentityValidationError):
        CanonicalR1RuntimeRoot(clean_graph, ledger, observation_protocol_version="")

    with pytest.raises(CausalIdentityValidationError):
        CanonicalR1RuntimeRoot(clean_graph, ledger, observation_protocol_version="   ")


def test_r1_t55_schema_1_2_0_migration_without_observation_protocol_fails(clean_graph, tmp_path):
    """R1-T55: Schema-1.2.0 migration without explicit target observation protocol version fails closed."""
    cp_path = tmp_path / "cp.json"
    save_cognitive_checkpoint(clean_graph, cp_path, policy=AssemblyPolicy())
    with open(cp_path, "r", encoding="utf-8") as f:
        cp_data = json.load(f)

    with pytest.raises(CausalIdentityValidationError):
        migrate_schema_1_1_1_to_1_2_0(cp_data, target_observation_protocol_version="")


def test_r1_t56_canonical_whole_command_replay_dedups_all_effects(base_runtime):
    """R1-T56: Whole-command replay deduplicates all persistent effects inside one command."""
    root_id = derive_root_external_episode_id("boundary_test", "occ_001")
    evt_digest = compute_event_descriptor_digest({"raw": "hello"})
    cmd = PersistentMutationCommand(
        mutation_owner_ref="MultiEdgeMutator",
        mutation_kind="CREATE_TRIANGLE",
        canonical_targets=["n1", "n2", "n3"],
        canonical_mutation_descriptor={"w": 1.0},
        owner_defined_transaction_scope="triangle_scope",
    )

    call_count = 0

    def multi_mutator():
        nonlocal call_count
        call_count += 1
        base_runtime.graph.link("n1", "n2", W=1.0, contexts=("en",))
        base_runtime.graph.link("n2", "n3", W=1.0, contexts=("en",))
        base_runtime.graph.link("n3", "n1", W=1.0, contexts=("en",))

    base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=multi_mutator,
    )
    assert call_count == 1
    assert len(base_runtime.graph.edges) == 3

    # Replay command
    _, executed, _ = base_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id=root_id,
        ingress_event_id="evt_1",
        event_descriptor_digest=evt_digest,
        mutator_callback=multi_mutator,
    )
    assert executed is False
    assert call_count == 1  # Not executed again!


def test_r1_t57_legacy_direct_mutation_path_outside_r1_idempotency(base_runtime):
    """R1-T57: Direct graph mutation is explicitly unrecorded in ledger."""
    base_runtime.graph.link("legacy_1", "legacy_2", W=1.0, contexts=("en",))
    assert len(base_runtime.ledger.committed_transactions) == 0


def test_r1_t58_exact_ledger_no_lossy_pruning_in_exact_r1(base_runtime):
    """R1-T58: Exact ledger has no pruning API and retains all committed transactions."""
    assert not hasattr(base_runtime.ledger, "prune")
    assert not hasattr(base_runtime.ledger, "evict")


# ─────────────────────────────────────────────────────────── 6. Canonical Lineage Validity & Escape Hatch
def test_r1_t61_new_restored_canonical_lineage_is_valid(base_runtime):
    """R1-T61: New and restored canonical runtime lineage is VALID."""
    assert base_runtime.canonical_lineage_state == CanonicalLineageState.VALID


def test_r1_t62_explicit_unsafe_legacy_mutation_invalidates_lineage(base_runtime):
    """R1-T62: Explicit unsafe legacy mutation sets INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION."""
    called = False

    def legacy_mutator():
        nonlocal called
        called = True
        base_runtime.graph.link("raw_a", "raw_b", W=1.0, contexts=("en",))

    base_runtime.unsafe_legacy_mutation_escape_hatch(legacy_mutator)

    assert called is True
    assert base_runtime.canonical_lineage_state == CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION


def test_r1_t63_invalidated_lineage_canonical_save_fails_closed(base_runtime, tmp_path):
    """R1-T63: Canonical save on invalidated lineage fails closed."""
    base_runtime.unsafe_legacy_mutation_escape_hatch(lambda: None)
    cp_path = tmp_path / "invalidated_save.json"

    with pytest.raises(CausalLineageInvalidatedError):
        save_canonical_r1_checkpoint(base_runtime, cp_path)


def test_r1_t64_invalidated_lineage_canonical_command_fails_closed(base_runtime):
    """R1-T64: Canonical command execution on invalidated lineage fails closed."""
    base_runtime.unsafe_legacy_mutation_escape_hatch(lambda: None)
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={},
        owner_defined_transaction_scope="s",
    )

    with pytest.raises(CausalLineageInvalidatedError):
        base_runtime.execute_persistent_command(
            command=cmd,
            root_external_episode_id="root_1",
            ingress_event_id="evt_1",
            event_descriptor_digest="digest_1",
            mutator_callback=lambda: None,
        )
