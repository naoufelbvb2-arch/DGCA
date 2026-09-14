"""RIC-01 / R2: Projection & SDCR Lifecycle Tests.

Verifies:
- Read-only assembly selection
- RFC-12 SDCR creation and close() lifecycle
- Context manager closing SDCRs cleanly
"""
from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)


def _make_bridge():
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
    return runtime.create_observation_bridge()


def test_sdcr_close_lifecycle():
    bridge = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="sdcr_lifecycle_test",
        source_occurrence_key="occ_lifecycle_001",
        source_event_key="evt_001",
        ingress_boundary="boundary",
        raw_text="The bird sang in the tree.",
    )
    assert not res.is_closed
    for rep in res.representations:
        assert rep.status == "ACTIVE"

    # Close result
    res.close()
    assert res.is_closed
    for rep in res.representations:
        assert rep.status == "CLOSED"

    # Double close is safe / idempotent
    res.close()
    assert res.is_closed


def test_context_manager_lifecycle():
    bridge = _make_bridge()
    with bridge.observe_text(
        boundary_namespace="sdcr_lifecycle_test",
        source_occurrence_key="occ_lifecycle_002",
        source_event_key="evt_002",
        ingress_boundary="boundary",
        raw_text="Sunrise over the mountains.",
    ) as res:
        assert not res.is_closed
        assert len(res.representations) > 0
    
    # Upon exit, result must be closed
    assert res.is_closed
    for rep in res.representations:
        assert rep.status == "CLOSED"
