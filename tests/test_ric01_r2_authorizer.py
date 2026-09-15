"""RIC-01 / R2: Persistent Observation Authorizer Tests.

Verifies:
- Default deny behavior of SimpleObservationAuthorizer
- Authorization callback gating
- Fail-closed semantics when authorizer raises exception
- Missing capability gating
"""
from typing import Any

import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    ExecutionMode,
    R2AuthorizationError,
)


class SimpleObservationAuthorizer:
    """Test stub for PersistentObservationAuthorizer Protocol (§13, B04)."""

    def __init__(self, allow: bool = False, callback: Any = None) -> None:
        self.allow = allow
        self.callback = callback

    def verify_persistent_observation(
        self,
        *,
        capability: object,
        root_external_episode_id: str,
        ingress_event_id: str,
        modality: str,
        operation_kind: str,
    ) -> Any:
        if self.callback is not None:
            return self.callback(
                capability=capability,
                root_external_episode_id=root_external_episode_id,
                ingress_event_id=ingress_event_id,
                modality=modality,
                operation_kind=operation_kind,
            )
        return self.allow

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


def test_default_authorizer_denies():
    authorizer = SimpleObservationAuthorizer(allow=False)
    assert authorizer.verify_persistent_observation(
        capability="dummy_cap",
        root_external_episode_id="root:0",
        ingress_event_id="ievt:0",
        modality="text",
        operation_kind="R2_AUTHORIZED_PERSISTENT",
    ) is False


def test_authorized_persistent_fails_without_authorizer():
    bridge = _make_bridge(authorizer=None)
    with pytest.raises(R2AuthorizationError, match="no authorizer configured"):
        bridge.observe_text(
            boundary_namespace="auth_test",
            source_occurrence_key="occ_001",
            source_event_key="evt_001",
            ingress_boundary="boundary",
            raw_text="test text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_capability",
        )


def test_authorized_persistent_fails_without_capability():
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge = _make_bridge(authorizer=authorizer)
    with pytest.raises(R2AuthorizationError, match="capability is None"):
        bridge.observe_text(
            boundary_namespace="auth_test",
            source_occurrence_key="occ_002",
            source_event_key="evt_002",
            ingress_boundary="boundary",
            raw_text="test text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability=None,
        )


def test_authorized_persistent_fails_when_denied():
    authorizer = SimpleObservationAuthorizer(allow=False)
    bridge = _make_bridge(authorizer=authorizer)
    with pytest.raises(R2AuthorizationError, match="authorizer returned non-bool or False"):
        bridge.observe_text(
            boundary_namespace="auth_test",
            source_occurrence_key="occ_003",
            source_event_key="evt_003",
            ingress_boundary="boundary",
            raw_text="test text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap_123",
        )


def test_authorizer_truthy_non_bool_fails_closed():
    # PIR01-B04, PIR01-T13: Non-bool truthy values must fail closed
    for truthy_val in (1, "yes", [1], object()):
        authorizer = SimpleObservationAuthorizer(callback=lambda val=truthy_val, **kwargs: val)
        bridge = _make_bridge(authorizer=authorizer)
        with pytest.raises(R2AuthorizationError, match="authorizer returned non-bool or False"):
            bridge.observe_text(
                boundary_namespace="auth_test",
                source_occurrence_key="occ_truthy",
                source_event_key="evt_truthy",
                ingress_boundary="boundary",
                raw_text="test text",
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability="cap_123",
            )


def test_authorizer_exception_fails_closed():
    def exploding_callback(**kwargs):
        raise RuntimeError("Authorizer internal error!")

    authorizer = SimpleObservationAuthorizer(callback=exploding_callback)
    bridge = _make_bridge(authorizer=authorizer)
    with pytest.raises(R2AuthorizationError, match="Authorizer raised exception"):
        bridge.observe_text(
            boundary_namespace="auth_test",
            source_occurrence_key="occ_004",
            source_event_key="evt_004",
            ingress_boundary="boundary",
            raw_text="test text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap_123",
        )


def test_authorizer_allows_valid_request():
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge = _make_bridge(authorizer=authorizer)
    res = bridge.observe_text(
        boundary_namespace="auth_test",
        source_occurrence_key="occ_005",
        source_event_key="evt_005",
        ingress_boundary="boundary",
        raw_text="trusted message",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res.status == "PERSISTENT_EXECUTED"
