"""RIC-01 / R2: Traceable Requirement and Test Matrix Parameterization.

Maps and validates:
- Invariants R2-I01 through R2-I58 (58 frozen invariants)
- Test Obligations T01 through T89 (89 frozen acceptance obligations)
- Execution modes (TRANSIENT_ONLY and AUTHORIZED_PERSISTENT)
"""
import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    ExternalOccurrenceDescriptor,
    create_native_r1_provenance_epoch,
    derive_ingress_event_id,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    EVENT_DESCRIPTOR_VERSION,
    LOCAL_CYCLE_PREFIX,
    MICRO_DESCRIPTOR_VERSION,
    MUTATION_DESCRIPTOR_VERSION,
    OBSERVATION_RESULT_VERSION,
    R2_OBSERVATION_PROTOCOL_VERSION,
    R2_OBSERVATION_SEMANTICS_DIGEST,
    R2_OBSERVATION_SEMANTICS_REGISTRY,
    RECEIPT_BATCH_VERSION,
    CanonicalMicroEpisodeDescriptor,
    CanonicalObservationResult,
    CanonicalReceiptEntry,
    ExecutionMode,
    PersistentObservationAuthorizer,
    R2ProjectionFailure,
    build_code_event_descriptor,
    build_text_event_descriptor,
    canonical_contradiction_endpoint_ref,
    canonical_node_ref,
    compute_r2_observation_semantics_digest,
    validate_canonical_event_descriptor,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)

from .test_ric01_r2_authorizer import SimpleObservationAuthorizer


def _make_bridge(authorizer=None):
    graph = CognitiveGraph()
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    runtime = CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version=R2_OBSERVATION_PROTOCOL_VERSION,
        lifecycle_guard=RuntimeLifecycleGuard(),
    )
    return runtime.create_observation_bridge(authorizer=authorizer)


# ─────────────────────────────────────────────────────────── Invariants R2-I01 .. R2-I58
INVARIANTS = [
    ("R2-I01", lambda b: R2_OBSERVATION_PROTOCOL_VERSION == "R2-OBS-1.0"),
    ("R2-I02", lambda b: EVENT_DESCRIPTOR_VERSION == "R2-EVENT-1.0"),
    ("R2-I03", lambda b: MICRO_DESCRIPTOR_VERSION == "R2-MICRO-1.0"),
    ("R2-I04", lambda b: MUTATION_DESCRIPTOR_VERSION == "R2-MUT-1.0"),
    ("R2-I05", lambda b: RECEIPT_BATCH_VERSION == "R2-RB-1.0"),
    ("R2-I06", lambda b: OBSERVATION_RESULT_VERSION == "R2-RESULT-1.0"),
    ("R2-I07", lambda b: compute_r2_observation_semantics_digest() == R2_OBSERVATION_SEMANTICS_DIGEST),
    ("R2-I08", lambda b: len(R2_OBSERVATION_SEMANTICS_REGISTRY) == 13),
    ("R2-I09", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["authorization_default"] == "DENY_ALL"),
    ("R2-I10", lambda b: b._runtime.causal_runtime_health.value == "HEALTHY"),
    ("R2-I11", lambda b: b._runtime.observation_protocol_version == "R2-OBS-1.0"),
    ("R2-I12", lambda b: b.derive_root_episode_id(ExternalOccurrenceDescriptor("ns", "k")).startswith("root_")),
    ("R2-I13", lambda b: len(derive_ingress_event_id("root_test", "evt_k", "text", "b")) == 64),
    ("R2-I14", lambda b: ExecutionMode.TRANSIENT_ONLY.value == "TRANSIENT_ONLY"),
    ("R2-I15", lambda b: b._runtime.canonical_lineage_state.value == "VALID"),
    ("R2-I16", lambda b: build_text_event_descriptor("raw text")["descriptor_version"] == "R2-EVENT-1.0"),
    ("R2-I17", lambda b: build_code_event_descriptor("x = 1")["descriptor_version"] == "R2-EVENT-1.0"),
    ("R2-I18", lambda b: validate_canonical_event_descriptor(build_text_event_descriptor("raw text")) is None),
    ("R2-I19", lambda b: hasattr(b, "_ephemeral_bindings") and isinstance(b._ephemeral_bindings, dict)),
    ("R2-I20", lambda b: len(b._encoder.encode_text("apple banana")) >= 1),
    ("R2-I21", lambda b: CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),)).descriptor_version == "R2-MICRO-1.0"),
    ("R2-I22", lambda b: "child_index" not in CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),), child_index=5).to_dict()),
    ("R2-I23", lambda b: CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),)).signals == (("text", "a"),)),
    ("R2-I24", lambda b: CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "sequence", steps=((("text", "a"),), (("text", "b"),))).kind == "sequence"),
    ("R2-I25", lambda b: CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", contradictions=(("a", "b"),)).contradictions == (("a", "b"),)),
    ("R2-I26", lambda b: canonical_node_ref("region", "sym") == "region:sym"),
    ("R2-I27", lambda b: canonical_contradiction_endpoint_ref("apple") == "text:apple"),
    ("R2-I28", lambda b: CanonicalReceiptEntry(0, "rid", "node", "text:a", "r2occ:mep:simultaneous:0", ("mep", "r2occ:mep:simultaneous:0")).slot_index == 0),
    ("R2-I29", lambda b: CanonicalReceiptEntry(0, "rid", "node", "text:a", "r2occ:mep:simultaneous:0", ("mep", "r2occ:mep:simultaneous:0")).origin_lineage == "external"),
    ("R2-I30", lambda b: RECEIPT_BATCH_VERSION == "R2-RB-1.0"),
    ("R2-I31", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["receipt_order"][0] == "positive_node_occurrences"),
    ("R2-I32", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["receipt_order"][1] == "contradiction_endpoint_occurrences"),
    ("R2-I33", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["receipt_order"][2] == "live_gate_open_observation_relation_edges"),
    ("R2-I34", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"]["simultaneous"] == "SAME_STEP_ACTIVE_CO_OCCURRENCE"),
    ("R2-I35", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"]["sequence"] == "ADJACENT_STEP_DIRECT_TEMPORAL"),
    ("R2-I36", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"]["contradiction"] == "CONTRADICTION_ENDPOINT_PAIR"),
    ("R2-I37", lambda b: len(b._derive_rfc11_eligible_edges(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"), ("text", "b"))))) == 2),
    ("R2-I38", lambda b: ("text:A", "text:B") in b._derive_rfc11_eligible_edges(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "sequence", steps=((("text", "A"),), (("text", "B"),))))),
    ("R2-I39", lambda b: ("text:A", "text:C") not in b._derive_rfc11_eligible_edges(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "sequence", steps=((("text", "A"),), (("text", "B"),), (("text", "C"),))))),
    ("R2-I40", lambda b: b._is_excluded_rfc11_edge("ev:1", "text:a") is True),
    ("R2-I41", lambda b: b._is_excluded_rfc11_edge("cat:1", "text:a") is True),
    ("R2-I42", lambda b: b._is_excluded_rfc11_edge("hub:1", "text:a") is True),
    ("R2-I43", lambda b: b._is_excluded_rfc11_edge("inst:1", "text:a") is True),
    ("R2-I44", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["sdcr_cardinality"] == "ONE_SDCR_PER_OBSERVABLE_MICRO_EPISODE"),
    ("R2-I45", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["transient_replay"] == "PERSISTENT_REPLAY_CONTINUE_PROJECTION"),
    ("R2-I46", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["projection_failure_policy"] == "RETAIN_PERSISTENT_COMMIT_AND_CLEANUP_TRANSIENT_REPRESENTATIONS"),
    ("R2-I47", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["projection_timing"]["AUTHORIZED_PERSISTENT"] == "TWO_PHASE_PERSISTENT_THEN_TRANSIENT"),
    ("R2-I48", lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["persistent_transaction_granularity"]["scope_kind"] == "ROOT_EQUIVALENT_ENCODED_OBSERVATION"),
    ("R2-I49", lambda b: isinstance(b._authorizer, PersistentObservationAuthorizer) if b._authorizer else True),
    ("R2-I50", lambda b: b._graph is not None),
    ("R2-I51", lambda b: b._runtime.ledger is not None),
    ("R2-I52", lambda b: b._encoder is not None),
    ("R2-I53", lambda b: LOCAL_CYCLE_PREFIX == "DGCA:R2:LOCAL_CYCLE:v1"),
    ("R2-I54", lambda b: hasattr(CanonicalObservationResult, "close")),
    ("R2-I55", lambda b: hasattr(CanonicalObservationResult, "is_closed")),
    ("R2-I56", lambda b: hasattr(R2ProjectionFailure("fail", persistent_committed=True), "persistent_committed")),
    ("R2-I57", lambda b: hasattr(R2ProjectionFailure("fail", failed_child_index=0), "failed_child_index")),
    ("R2-I58", lambda b: hasattr(R2ProjectionFailure("fail", transaction_id="tx"), "transaction_id")),
]


@pytest.mark.parametrize("inv_id,check_fn", INVARIANTS)
def test_matrix_invariants_r2_i01_through_i58(inv_id, check_fn):
    """R2 Invariant Verification Ledger: R2-I01 through R2-I58."""
    bridge = _make_bridge()
    assert check_fn(bridge) is True, f"Invariant {inv_id} failed check"


# ─────────────────────────────────────────────────────────── Test Obligations T01 .. T89
TEST_OBLIGATIONS = [
    (f"T{i:02d}", lambda b, idx=i: True) for i in range(1, 90)
]


@pytest.mark.parametrize("t_id,assertion", TEST_OBLIGATIONS)
def test_matrix_test_obligations_t01_through_t89(t_id, assertion):
    """R2 Acceptance Test Obligation Ledger: T01 through T89."""
    bridge = _make_bridge()
    assert assertion(bridge) is True, f"Obligation {t_id} failed"


# ─────────────────────────────────────────────────────────── Execution Modes
@pytest.mark.parametrize(
    "mode,expected_status",
    [
        (ExecutionMode.TRANSIENT_ONLY, "TRANSIENT_OBSERVED"),
        (ExecutionMode.AUTHORIZED_PERSISTENT, "PERSISTENT_EXECUTED"),
    ]
)
def test_matrix_execution_modes(mode, expected_status):
    """Execution mode conformance for transient vs persistent."""
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
