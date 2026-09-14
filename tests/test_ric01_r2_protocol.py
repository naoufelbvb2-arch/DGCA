"""RIC-01 / R2: Protocol Constants, Semantics Digest, and Error Hierarchy Tests.

Verifies:
- Protocol version constants
- R2 observation semantics registry (31 items) and SHA-256 digest
- Error hierarchy under R2ObservationError / CausalIdentityError
- create_observation_bridge protocol validation
"""
import pytest

from dgca.causal_identity import (
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalIdentityError,
    CausalIdentityValidationError,
    CausalRuntimeFailStopError,
    CausalRuntimeHealth,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    EVENT_DESCRIPTOR_VERSION,
    MICRO_DESCRIPTOR_VERSION,
    MUTATION_DESCRIPTOR_VERSION,
    OBSERVATION_RESULT_VERSION,
    R2_OBSERVATION_PROTOCOL_VERSION,
    R2_OBSERVATION_SEMANTICS_DIGEST,
    R2_OBSERVATION_SEMANTICS_REGISTRY,
    RECEIPT_BATCH_VERSION,
    R2AuthorizationError,
    R2BatchValidationError,
    R2DescriptorValidationError,
    R2LifecycleError,
    R2ObservationError,
    R2ProjectionFailure,
    R2ReplayConflictError,
    compute_r2_observation_semantics_digest,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)


def _make_runtime(graph=None, observation_protocol_version="R2-OBS-1.0"):
    if graph is None:
        graph = CognitiveGraph()
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    return CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version=observation_protocol_version,
        lifecycle_guard=RuntimeLifecycleGuard(),
    )


def test_protocol_version_constants():
    assert R2_OBSERVATION_PROTOCOL_VERSION == "R2-OBS-1.0"
    assert EVENT_DESCRIPTOR_VERSION == "R2-EVENT-1.0"
    assert MICRO_DESCRIPTOR_VERSION == "R2-MICRO-1.0"
    assert MUTATION_DESCRIPTOR_VERSION == "R2-MUT-1.0"
    assert RECEIPT_BATCH_VERSION == "R2-RB-1.0"
    assert OBSERVATION_RESULT_VERSION == "R2-RESULT-1.0"


def test_semantics_registry_and_digest():
    assert len(R2_OBSERVATION_SEMANTICS_REGISTRY) == 31
    assert R2_OBSERVATION_SEMANTICS_DIGEST == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b7c"
    computed = compute_r2_observation_semantics_digest()
    assert computed == R2_OBSERVATION_SEMANTICS_DIGEST


def test_error_hierarchy():
    assert issubclass(R2ObservationError, CausalIdentityError)
    assert issubclass(R2ObservationError, Exception)
    assert issubclass(R2AuthorizationError, R2ObservationError)
    assert issubclass(R2DescriptorValidationError, R2ObservationError)
    assert issubclass(R2BatchValidationError, R2ObservationError)
    assert issubclass(R2ProjectionFailure, R2ObservationError)
    assert issubclass(R2ReplayConflictError, R2ObservationError)
    assert issubclass(R2LifecycleError, R2ObservationError)


def test_r2_projection_failure_attributes():
    orig = ValueError("boom")
    err = R2ProjectionFailure(
        "projection failed",
        transaction_id="tx:123",
        persistent_executed=True,
        persistent_committed=True,
        failed_child_index=2,
        stage="transient_projection",
        original_exception=orig,
    )
    assert err.transaction_id == "tx:123"
    assert err.persistent_executed is True
    assert err.persistent_committed is True
    assert err.failed_child_index == 2
    assert err.stage == "transient_projection"
    assert err.original_exception is orig


def test_create_observation_bridge_protocol_check():
    # Valid protocol
    runtime_valid = _make_runtime(observation_protocol_version="R2-OBS-1.0")
    bridge = runtime_valid.create_observation_bridge()
    assert bridge is not None

    # Invalid protocol
    runtime_invalid = _make_runtime(observation_protocol_version="R1-OBS-1.0")
    with pytest.raises(CausalIdentityValidationError, match="requires observation_protocol_version 'R2-OBS-1.0'"):
        runtime_invalid.create_observation_bridge()


def test_create_observation_bridge_fail_stop_and_lineage_checks():
    runtime = _make_runtime(observation_protocol_version="R2-OBS-1.0")
    
    # Mark health as MUTATION_FAILED
    runtime.causal_runtime_health = CausalRuntimeHealth.MUTATION_FAILED
    with pytest.raises(CausalRuntimeFailStopError, match="fail-stop state"):
        runtime.create_observation_bridge()
    
    # Restore health, but invalidate lineage
    runtime.causal_runtime_health = CausalRuntimeHealth.HEALTHY
    runtime.canonical_lineage_state = CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
    with pytest.raises(CausalIdentityError, match="Canonical lineage is invalidated"):
        runtime.create_observation_bridge()
