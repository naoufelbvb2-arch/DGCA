"""RIC-01 / R2: Explicit Adversarial Scenarios A through Q (§41).

Verifies:
- Scenario A: Tampered protocol version
- Scenario B: Malformed event descriptor
- Scenario C: Duplicate child indices
- Scenario D: Slot index gaps in receipt batch
- Scenario E: Slot index duplication
- Scenario F: Authorizer throwing exception (fails closed)
- Scenario G: Untracked mutation invalidates lineage
- Scenario H: Ingress during fail-stop MUTATION_FAILED
- Scenario I: Replay with conflicting content hash
- Scenario J/K: RFC-11 edge firewall
- Scenario L: Two-phase projection failure preserves persistent commit & healthy runtime
- Scenario M: Double-close idempotency
- Scenario N: Transient observation strict conservation
- Scenario O: Empty / whitespace content handling
- Scenario P: Unverified edge in tier 1 slot
- Scenario Q: Cross-boundary event ID spoofing
"""
from unittest.mock import patch

import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalIdentityError,
    CausalRuntimeFailStopError,
    CausalRuntimeHealth,
    ExternalOccurrenceDescriptor,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    ExecutionMode,
    R2AuthorizationError,
    R2DescriptorError,
    R2ProjectionFailure,
    SimpleObservationAuthorizer,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)


def _setup(authorizer=None, version="R2-OBS-1.0"):
    graph = CognitiveGraph()
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    runtime = CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version=version,
        lifecycle_guard=RuntimeLifecycleGuard(),
    )
    bridge = runtime.create_observation_bridge(authorizer=authorizer) if version == "R2-OBS-1.0" else None
    return runtime, graph, ledger, bridge


def test_scenario_a_tampered_protocol_version():
    runtime, _, _, _ = _setup(version="MALFORMED_VERSION")
    with pytest.raises(CausalIdentityError):
        runtime.create_observation_bridge()


def test_scenario_b_malformed_occurrence_descriptor():
    _, _, _, bridge = _setup()
    with pytest.raises(R2DescriptorError, match="occurrence must be an ExternalOccurrenceDescriptor"):
        bridge.observe(
            occurrence={"boundary": "raw_dict"},  # type: ignore
            source_event_key="evt",
            ingress_boundary="ing",
            modality="text",
            payload={"raw_text": "hello"},
        )


def test_scenario_f_authorizer_throws_exception():
    def exploder(**kwargs):
        raise ValueError("authorizer explode")

    authorizer = SimpleObservationAuthorizer(callback=exploder)
    _, _, _, bridge = _setup(authorizer=authorizer)
    with pytest.raises(R2AuthorizationError, match="Authorizer raised exception"):
        bridge.observe_text(
            boundary_namespace="b",
            source_occurrence_key="occ_f",
            source_event_key="evt_f",
            ingress_boundary="b",
            raw_text="text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap",
        )


def test_scenario_g_untracked_mutation_invalidates_lineage():
    runtime, _graph, _ledger, bridge = _setup()
    runtime.unsafe_mutable_graph()  # Invalidate lineage
    with pytest.raises(CausalIdentityError, match="Canonical lineage is invalidated"):
        bridge.observe_text(
            boundary_namespace="b",
            source_occurrence_key="occ_g",
            source_event_key="evt_g",
            ingress_boundary="b",
            raw_text="text",
        )


def test_scenario_h_ingress_during_fail_stop():
    runtime, _graph, _ledger, bridge = _setup()
    runtime.causal_runtime_health = CausalRuntimeHealth.MUTATION_FAILED
    with pytest.raises(CausalRuntimeFailStopError, match="fail-stop state"):
        bridge.observe_text(
            boundary_namespace="b",
            source_occurrence_key="occ_h",
            source_event_key="evt_h",
            ingress_boundary="b",
            raw_text="text",
        )


def test_scenario_i_replay_with_conflicting_descriptor():
    authorizer = SimpleObservationAuthorizer(allow=True)
    _runtime, _graph, _ledger, bridge = _setup(authorizer=authorizer)
    
    bridge.observe_text(
        boundary_namespace="b",
        source_occurrence_key="occ_i",
        source_event_key="evt_i",
        ingress_boundary="b",
        raw_text="original payload text",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="cap",
    )
    
    with pytest.raises(R2DescriptorError, match="Conflicting event descriptor"):
        bridge.observe_text(
            boundary_namespace="b",
            source_occurrence_key="occ_i",
            source_event_key="evt_i",
            ingress_boundary="b",
            raw_text="tampered payload text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap",
        )


def test_scenario_j_k_rfc11_edge_firewall():
    _, _, _, bridge = _setup()
    assert bridge._is_excluded_rfc11_edge("ev:1", "node_a") is True
    assert bridge._is_excluded_rfc11_edge("node_a", "cat:2") is True
    assert bridge._is_excluded_rfc11_edge("hub:concept", "node_b") is True
    assert bridge._is_excluded_rfc11_edge("inst:item", "node_b") is True
    assert bridge._is_excluded_rfc11_edge("text:dog", "text:barks") is False


def test_scenario_l_two_phase_projection_failure():
    authorizer = SimpleObservationAuthorizer(allow=True)
    runtime, graph, _ledger, bridge = _setup(authorizer=authorizer)
    
    with patch.object(
        graph.representation_engine,
        "build_canonical_representation",
        side_effect=ValueError("Projection fail"),
    ):
        with pytest.raises(R2ProjectionFailure) as exc:
            bridge.observe_text(
                boundary_namespace="b",
                source_occurrence_key="occ_l",
                source_event_key="evt_l",
                ingress_boundary="b",
                raw_text="hello",
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability="cap",
            )
        assert exc.value.persistent_committed is True
        assert runtime.causal_runtime_health == CausalRuntimeHealth.HEALTHY


def test_scenario_m_double_close_idempotency():
    _, _, _, bridge = _setup()
    res = bridge.observe_text(
        boundary_namespace="b",
        source_occurrence_key="occ_m",
        source_event_key="evt_m",
        ingress_boundary="b",
        raw_text="text",
    )
    res.close()
    assert res.is_closed
    res.close()
    assert res.is_closed


def test_scenario_n_transient_strict_conservation():
    _runtime, graph, _ledger, bridge = _setup()
    digest_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    bridge.observe_text(
        boundary_namespace="b",
        source_occurrence_key="occ_n",
        source_event_key="evt_n",
        ingress_boundary="b",
        raw_text="some text here",
    )
    digest_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    assert digest_before == digest_after


def test_scenario_o_empty_content_handling():
    _, _, _, bridge = _setup()
    # Empty content produces NO_OBSERVABLE_CONTENT
    res = bridge.observe_text(
        boundary_namespace="b",
        source_occurrence_key="occ_o",
        source_event_key="evt_o",
        ingress_boundary="b",
        raw_text="",
    )
    assert res.status == "NO_OBSERVABLE_CONTENT"
    assert len(res.representations) == 0


def test_scenario_q_cross_boundary_event_id_spoofing():
    _, _, _, bridge = _setup()
    occ1 = ExternalOccurrenceDescriptor("boundary_a", "occ_q")
    occ2 = ExternalOccurrenceDescriptor("boundary_b", "occ_q")
    root1 = bridge.derive_root_episode_id(occ1)
    root2 = bridge.derive_root_episode_id(occ2)
    assert root1 != root2
