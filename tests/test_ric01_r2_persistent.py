"""RIC-01 / R2: Authorized Persistent Ingress & Idempotent Replay Tests.

Verifies:
- AUTHORIZED_PERSISTENT mode executes exactly once on R1 runtime
- Single canonical R1 PersistentMutationCommand executed
- Ledger records CausalCommitRecord
- Subsequent ingress with same ExternalOccurrenceDescriptor replays without double-learning
- Result status PERSISTENT_EXECUTED vs PERSISTENT_REPLAY
"""
from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    ExecutionMode,
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


def test_authorized_persistent_single_command_and_replay():
    _runtime, graph, ledger, bridge = _setup()

    code_text = "def greet(name): return f'Hello, {name}'"

    # Ingress 1: First execution
    res1 = bridge.observe_code(
        boundary_namespace="persistent_test",
        source_occurrence_key="occ_persist_001",
        source_event_key="evt_01",
        ingress_boundary="boundary",
        source_code=code_text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res1.status == "PERSISTENT_EXECUTED"
    assert len(ledger.committed_transactions) == 1

    # Record state after first execution
    node_count_first = len(graph.nodes)
    edge_count_first = len(graph.edges)
    weights_first = {k: v.W for k, v in graph.edges.items()}
    digest_first = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))

    # Ingress 2: Replay with identical descriptor and content
    res2 = bridge.observe_code(
        boundary_namespace="persistent_test",
        source_occurrence_key="occ_persist_001",
        source_event_key="evt_01",
        ingress_boundary="boundary",
        source_code=code_text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res2.status == "PERSISTENT_REPLAY"
    assert res2.observation_transaction_id == res1.observation_transaction_id
    assert len(ledger.committed_transactions) == 1  # No duplicate ledger commit

    # Verify zero double-learning / exact state preservation
    assert len(graph.nodes) == node_count_first
    assert len(graph.edges) == edge_count_first
    for k, w in weights_first.items():
        assert graph.edges[k].W == w
    digest_second = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    assert digest_second == digest_first
