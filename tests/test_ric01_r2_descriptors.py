"""RIC-01 / R2: Ingress & Micro-Episode Descriptors Tests.

Verifies:
- Text and code event descriptor generation and digest computation
- MicroEpisodeDescriptor schema, indexing, and ID derivation
- Ephemeral ingress binding registry & collision handling
"""
import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    ExternalOccurrenceDescriptor,
    compute_event_descriptor_digest,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    EVENT_DESCRIPTOR_VERSION,
    MICRO_DESCRIPTOR_VERSION,
    CanonicalMicroEpisodeDescriptor,
    R2DescriptorError,
    build_code_event_descriptor,
    build_text_event_descriptor,
    derive_code_event_descriptor,
    derive_text_event_descriptor,
    validate_canonical_event_descriptor,
)
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


def test_text_event_descriptor():
    desc = build_text_event_descriptor("hello world", context="general")
    assert desc["descriptor_version"] == EVENT_DESCRIPTOR_VERSION
    assert desc["modality"] == "text"
    assert desc["encoder_contract"] == "DGCA_SYMBOLIC_TEXT_V1"
    assert desc["payload"]["raw_text"] == "hello world"
    assert desc["payload"]["context"] == "general"
    validate_canonical_event_descriptor(desc)
    digest = compute_event_descriptor_digest(desc)
    assert len(digest) == 64
    assert derive_text_event_descriptor("hello world", context="general") == desc


def test_code_event_descriptor():
    code = "x = 42\ny = x + 1"
    desc = build_code_event_descriptor(code, module="test_mod")
    assert desc["descriptor_version"] == EVENT_DESCRIPTOR_VERSION
    assert desc["modality"] == "code"
    assert desc["encoder_contract"] == "DGCA_SYMBOLIC_CODE_V1"
    assert desc["payload"]["source_code"] == code
    assert desc["payload"]["module"] == "test_mod"
    validate_canonical_event_descriptor(desc)
    digest = compute_event_descriptor_digest(desc)
    assert len(digest) == 64
    assert derive_code_event_descriptor(code, module="test_mod") == desc


def test_micro_episode_descriptor_validation():
    mep = CanonicalMicroEpisodeDescriptor(
        micro_descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:001",
        child_index=0,
        kind="simultaneous",
        positive_signals=({"region": "text", "symbol": "apple"},),
        contradictions=(),
        structural_weight=1.0,
        valence=0.5,
    )
    assert mep.micro_descriptor_version == MICRO_DESCRIPTOR_VERSION
    assert mep.child_index == 0
    d = mep.to_dict()
    assert d["micro_descriptor_version"] == MICRO_DESCRIPTOR_VERSION
    assert d["kind"] == "simultaneous"


def test_binding_registry_conflict():
    bridge = _make_bridge()
    occ = ExternalOccurrenceDescriptor(
        boundary_namespace="test_boundary",
        source_occurrence_key="occ_conflict",
    )
    # First observation
    res1 = bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_01",
        ingress_boundary="ingress_01",
        raw_text="first sentence with apple",
    )
    assert res1.status == "TRANSIENT_OBSERVED"

    # Conflicting observation with same source_event_key and ingress_boundary but different content
    with pytest.raises(R2DescriptorError, match="Conflicting event descriptor registered"):
        bridge.observe_text(
            boundary_namespace=occ.boundary_namespace,
            source_occurrence_key=occ.source_occurrence_key,
            source_event_key="evt_01",
            ingress_boundary="ingress_01",
            raw_text="completely different text with orange",
        )
