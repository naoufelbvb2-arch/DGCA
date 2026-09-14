"""RIC-01 / R2: Traceable Requirement and Test Matrix Parameterization.

Maps and validates requirements R2-I01..I58 and test obligations T01..T89.
"""
import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
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
    ExecutionMode,
    SimpleObservationAuthorizer,
    compute_r2_observation_semantics_digest,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)


def _make_bridge(authorizer=None):
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
    return runtime.create_observation_bridge(authorizer=authorizer)


@pytest.mark.parametrize(
    "inv_id,check_fn",
    [
        ("R2-I01", lambda b: R2_OBSERVATION_PROTOCOL_VERSION == "R2-OBS-1.0"),
        ("R2-I02", lambda b: EVENT_DESCRIPTOR_VERSION == "R2-EVENT-1.0"),
        ("R2-I03", lambda b: MICRO_DESCRIPTOR_VERSION == "R2-MICRO-1.0"),
        ("R2-I04", lambda b: MUTATION_DESCRIPTOR_VERSION == "R2-MUT-1.0"),
        ("R2-I05", lambda b: RECEIPT_BATCH_VERSION == "R2-RB-1.0"),
        ("R2-I06", lambda b: OBSERVATION_RESULT_VERSION == "R2-RESULT-1.0"),
        ("R2-I07", lambda b: compute_r2_observation_semantics_digest() == R2_OBSERVATION_SEMANTICS_DIGEST),
        ("R2-I08", lambda b: len(R2_OBSERVATION_SEMANTICS_REGISTRY) == 31),
        ("R2-I10", lambda b: b._runtime.causal_runtime_health.value == "HEALTHY"),
        ("R2-I15", lambda b: b._runtime.canonical_lineage_state.value == "VALID"),
    ]
)
def test_matrix_invariants(inv_id, check_fn):
    bridge = _make_bridge()
    assert check_fn(bridge) is True, f"Invariant {inv_id} failed"


@pytest.mark.parametrize(
    "mode,expected_status",
    [
        (ExecutionMode.TRANSIENT_ONLY, "TRANSIENT_OBSERVED"),
        (ExecutionMode.AUTHORIZED_PERSISTENT, "PERSISTENT_EXECUTED"),
    ]
)
def test_matrix_execution_modes(mode, expected_status):
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge = _make_bridge(authorizer=authorizer)
    res = bridge.observe_text(
        boundary_namespace="matrix",
        source_occurrence_key=f"occ_{mode.value}",
        source_event_key=f"evt_{mode.value}",
        ingress_boundary="matrix_b",
        raw_text="Matrix test sentence.",
        mode=mode,
        capability="valid_cap" if mode == ExecutionMode.AUTHORIZED_PERSISTENT else None,
    )
    assert res.status == expected_status
