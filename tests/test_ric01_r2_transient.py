"""RIC-01 / R2: Transient Observation Tests.

Verifies:
- Default execution mode is TRANSIENT_ONLY
- Zero graph mutation (nodes, edges, weights strictly unchanged)
- Persistent state digest equality before and after
- Zero ledger commits
- SDCR generation and valid projection
"""
from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    OBSERVATION_RESULT_VERSION,
    ExecutionMode,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)


def _setup_runtime():
    graph = CognitiveGraph()
    # Pre-populate some knowledge in graph
    graph.observe([("concept", "light"), ("concept", "sun")], context="nature")
    
    state_digest_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    epoch = create_native_r1_provenance_epoch(state_digest_before)
    ledger = CausalCommitLedger(epoch=epoch)
    runtime = CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version="R2-OBS-1.0",
        lifecycle_guard=RuntimeLifecycleGuard(),
    )
    return runtime, graph, ledger, state_digest_before


def test_transient_observation_zero_graph_mutation():
    runtime, graph, ledger, digest_before = _setup_runtime()
    bridge = runtime.create_observation_bridge()

    node_count_before = len(graph.nodes)
    edge_count_before = len(graph.edges)
    weights_before = {k: v.W for k, v in graph.edges.items()}

    # Observe in default TRANSIENT_ONLY mode
    result = bridge.observe_text(
        boundary_namespace="transient_test",
        source_occurrence_key="occ_transient_001",
        source_event_key="evt_01",
        ingress_boundary="test_ingress",
        raw_text="The moon shines in the dark sky.",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )

    assert result.result_version == OBSERVATION_RESULT_VERSION
    assert result.status == "TRANSIENT_OBSERVED"
    assert len(result.micro_episodes) > 0

    # Invariant: graph state must be strictly unmodified
    assert len(graph.nodes) == node_count_before
    assert len(graph.edges) == edge_count_before
    for k, w in weights_before.items():
        assert graph.edges[k].W == w

    digest_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    assert digest_after == digest_before

    # Invariant: ledger has no transactions committed
    assert len(ledger.committed_transactions) == 0


def test_transient_observation_generates_valid_sdcr():
    runtime, _graph, _ledger, _ = _setup_runtime()
    bridge = runtime.create_observation_bridge()
    
    result = bridge.observe_code(
        boundary_namespace="transient_test",
        source_occurrence_key="occ_transient_002",
        source_event_key="evt_02",
        ingress_boundary="test_ingress",
        source_code="def add(a, b): return a + b",
    )
    assert result.status == "TRANSIENT_OBSERVED"
    assert len(result.representations) > 0
    for sdcr in result.representations:
        assert sdcr is not None
        assert sdcr.status == "ACTIVE"
