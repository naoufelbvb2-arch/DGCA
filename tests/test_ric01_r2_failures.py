"""RIC-01 / R2: Two-Phase Projection Failures & Retry Replay Tests (§29).

Verifies:
- Two-phase projection failure semantics
- If transient projection fails after persistent decision, persistent state is NOT rolled back
- R2ProjectionFailure carries non-secret diagnostic state
- R1 runtime is NOT marked as MUTATION_FAILED
- Subsequent retry cleanly reaches R1 idempotent replay
"""
from unittest.mock import patch

import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalRuntimeHealth,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    ExecutionMode,
    R2ProjectionFailure,
    SimpleObservationAuthorizer,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)


def _setup():
    graph = CognitiveGraph()
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    runtime = CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version="R2-OBS-1.0",
        lifecycle_guard=RuntimeLifecycleGuard(),
    )
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge = runtime.create_observation_bridge(authorizer=authorizer)
    return runtime, graph, ledger, bridge


def test_two_phase_projection_failure_semantics():
    runtime, graph, ledger, bridge = _setup()

    # Mock representation engine to fail after persistent mutation
    with patch.object(
        graph.representation_engine,
        "build_canonical_representation",
        side_effect=RuntimeError("Simulated projection crash"),
    ):
        with pytest.raises(R2ProjectionFailure) as exc_info:
            bridge.observe_text(
                boundary_namespace="failure_test",
                source_occurrence_key="occ_fail_001",
                source_event_key="evt_fail",
                ingress_boundary="boundary",
                raw_text="Quantum gravity observation",
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability="valid_cap",
            )
        
        err = exc_info.value
        assert err.persistent_committed is True
        assert err.persistent_executed is True
        assert err.stage == "transient_projection"
        assert err.transaction_id.startswith("tx_obs_")

    # Invariant: persistent commit is authoritative in ledger
    assert len(ledger.committed_transactions) == 1
    committed_tx = next(iter(ledger.committed_transactions.values()))
    assert len(committed_tx.transaction_id) == 64
    assert committed_tx.root_external_episode_id.startswith("root_")

    # Invariant: R1 runtime is NOT marked MUTATION_FAILED
    assert runtime.causal_runtime_health == CausalRuntimeHealth.HEALTHY

    # Retry without patch: reaches R1 idempotent replay and reconstructs transient SDCRs cleanly
    res_retry = bridge.observe_text(
        boundary_namespace="failure_test",
        source_occurrence_key="occ_fail_001",
        source_event_key="evt_fail",
        ingress_boundary="boundary",
        raw_text="Quantum gravity observation",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res_retry.status == "PERSISTENT_REPLAY"
    assert res_retry.observation_transaction_id == err.transaction_id
    assert len(res_retry.representations) > 0
