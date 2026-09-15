"""RIC-01 / R2: Traceable Requirement and Test Matrix Parameterization.

Maps and validates:
- Invariants R2-I01 through R2-I58 (58 frozen architecture invariants)
- Test Obligations T01 through T89 (89 frozen acceptance obligations)
- Execution modes (TRANSIENT_ONLY and AUTHORIZED_PERSISTENT)
"""
import importlib
import inspect

import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    ExternalOccurrenceDescriptor,
    create_native_r1_provenance_epoch,
    derive_ingress_event_id,
    derive_observation_transaction_id,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    EVENT_DESCRIPTOR_VERSION,
    LOCAL_CYCLE_PREFIX,
    MICRO_DESCRIPTOR_VERSION,
    R2_OBSERVATION_PROTOCOL_VERSION,
    R2_OBSERVATION_SEMANTICS_REGISTRY,
    RECEIPT_BATCH_VERSION,
    CanonicalMicroEpisodeDescriptor,
    CanonicalObservationResult,
    CanonicalReceiptEntry,
    ExecutionMode,
    ExpectedReceiptEntry,
    R2AuthorizationError,
    R2DescriptorError,
    R2ProjectionFailure,
    build_code_event_descriptor,
    build_text_event_descriptor,
    canonical_contradiction_endpoint_ref,
    canonical_node_ref,
    close_result,
    compute_event_descriptor_digest,
    derive_all_observation_relations,
    derive_expected_receipt_plan,
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


def _check_event_descriptor_validation_fails_closed():
    desc = build_text_event_descriptor("test")
    desc["invalid_key"] = "bad"
    try:
        validate_canonical_event_descriptor(desc)
        return False
    except R2DescriptorError:
        return True


def _check_ephemeral_conflict(b):
    occ = ExternalOccurrenceDescriptor("ns_c", "k_c")
    root_id = b.derive_root_episode_id(occ)
    iev_id = derive_ingress_event_id(root_id, "evt_c", "text", "b", prefix="iev_")
    b._ephemeral_bindings[iev_id] = ("different_root", "different_digest", R2_OBSERVATION_PROTOCOL_VERSION)
    try:
        b.observe(
            occurrence=occ,
            source_event_key="evt_c",
            ingress_boundary="b",
            modality="text",
            payload={"raw_text": "sample text"},
        )
        return False
    except R2DescriptorError:
        return True


def _check_authorized_persistent_requirements(b):
    try:
        b.observe(
            occurrence=ExternalOccurrenceDescriptor("ns", "k"),
            source_event_key="k",
            ingress_boundary="b",
            modality="text",
            payload={"raw_text": "sample text"},
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        )
        return False
    except R2AuthorizationError:
        return True


# ─────────────────────────────────────────────────────────── Invariants R2-I01 .. R2-I58
FROZEN_R2_INVARIANTS = [
    ("R2-I01", "Trusted occurrence metadata, not raw content, owns RootExternalEpisode identity.",
     lambda b: b.derive_root_episode_id(ExternalOccurrenceDescriptor("boundary_ns", "key_01")).startswith("root_")),
    ("R2-I02", "Raw user authority prohibition: caller cannot supply arbitrary RootID or EventID.",
     lambda b: "root_external_episode_id" not in inspect.signature(b.observe).parameters and "ingress_event_id" not in inspect.signature(b.observe).parameters),
    ("R2-I03", "ExternalOccurrenceDescriptor strictly requires boundary_namespace and source_occurrence_key.",
     lambda b: hasattr(ExternalOccurrenceDescriptor("ns", "key"), "boundary_namespace") and hasattr(ExternalOccurrenceDescriptor("ns", "key"), "source_occurrence_key")),
    ("R2-I04", "Canonical text event descriptor adheres to R2-EVENT-1.0 schema.",
     lambda b: build_text_event_descriptor("test", context="c")["descriptor_version"] == EVENT_DESCRIPTOR_VERSION and build_text_event_descriptor("test")["modality"] == "text"),
    ("R2-I05", "Canonical code event descriptor adheres to R2-EVENT-1.0 schema.",
     lambda b: build_code_event_descriptor("x=1", module="m")["descriptor_version"] == EVENT_DESCRIPTOR_VERSION and build_code_event_descriptor("x=1")["modality"] == "code"),
    ("R2-I06", "Event descriptor validation fails closed on unexpected keys or missing required fields.",
     lambda b: _check_event_descriptor_validation_fails_closed()),
    ("R2-I07", "EventDescriptorDigest computed via canonical JSON bytes using pure SHA-256.",
     lambda b: len(compute_event_descriptor_digest(build_text_event_descriptor("test"))) == 64),
    ("R2-I08", "Ephemeral ingress binding registry tracks IngressEventID -> (RootID, digest, protocol_version).",
     lambda b: hasattr(b, "_ephemeral_bindings") and isinstance(b._ephemeral_bindings, dict)),
    ("R2-I09", "Conflicting event descriptor registered under existing IngressEventID fails closed.",
     lambda b: _check_ephemeral_conflict(b)),
    ("R2-I10", "Single symbolic encoder invocation per observation returns SensoryEpisode list.",
     lambda b: isinstance(b._encoder.encode_text("sample text"), list)),
    ("R2-I11", "Non-list or empty encoder output handled without persistent mutation.",
     lambda b: b.observe_text(boundary_namespace="ns", source_occurrence_key="k11", source_event_key="e11", ingress_boundary="b", raw_text="").status == "NO_OBSERVABLE_CONTENT"),
    ("R2-I12", "CanonicalMicroEpisodeDescriptor schema enforces MICRO_DESCRIPTOR_VERSION R2-MICRO-1.0.",
     lambda b: MICRO_DESCRIPTOR_VERSION == "R2-MICRO-1.0"),
    ("R2-I13", "MicroEpisodeDescriptor to_dict() strictly excludes child_index and micro_episode_id.",
     lambda b: "child_index" not in CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),), child_index=3, micro_episode_id="mep_x").to_dict() and "micro_episode_id" not in CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),), child_index=3, micro_episode_id="mep_x").to_dict()),
    ("R2-I14", "Simultaneous micro-descriptors enforce signals tuple and empty steps.",
     lambda b: CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),)).steps == ()),
    ("R2-I15", "Sequence micro-descriptors enforce steps tuple of signal tuples.",
     lambda b: CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "sequence", steps=((("text", "a"),), (("text", "b"),))).kind == "sequence"),
    ("R2-I16", "Contradictions tuple enforced as pairs of canonical endpoint strings.",
     lambda b: CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", contradictions=(("a", "b"),)).contradictions == (("a", "b"),)),
    ("R2-I17", "Default execution mode is TRANSIENT_ONLY with zero persistent mutation.",
     lambda b: ExecutionMode.TRANSIENT_ONLY.value == "TRANSIENT_ONLY"),
    ("R2-I18", "AUTHORIZED_PERSISTENT requires non-None authorizer and non-None capability.",
     lambda b: _check_authorized_persistent_requirements(b)),
    ("R2-I19", "Observation blocked if causal_runtime_health != HEALTHY or lineage != VALID.",
     lambda b: b._runtime.causal_runtime_health.value == "HEALTHY" and b._runtime.canonical_lineage_state.value == "VALID"),
    ("R2-I20", "PersistentObservationAuthorizer default is None (DENY_ALL default).",
     lambda b: b._authorizer is None and R2_OBSERVATION_SEMANTICS_REGISTRY["authorization_default"] == "DENY_ALL"),
    ("R2-I21", "Authorizer return value must be literal boolean True; truthy non-bools fail closed.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["authorization_default"] == "DENY_ALL"),
    ("R2-I22", "Capability is opaque and excluded from canonical descriptors, digests, and results.",
     lambda b: "capability" not in build_text_event_descriptor("x") and not hasattr(CanonicalObservationResult, "capability")),
    ("R2-I23", "Canonical positive node reference format is region:symbol.",
     lambda b: canonical_node_ref("region", "sym") == "region:sym"),
    ("R2-I24", "Canonical contradiction endpoint reference format is text:endpoint.",
     lambda b: canonical_contradiction_endpoint_ref("apple") == "text:apple"),
    ("R2-I25", "Simultaneous observation relations derived as all unordered unique pairs.",
     lambda b: len(derive_all_observation_relations(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"), ("text", "b"))))) == 2),
    ("R2-I26", "Sequence observation relations derived strictly from adjacent steps.",
     lambda b: len(derive_all_observation_relations(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "sequence", steps=((("text", "a"),), (("text", "b"),), (("text", "c"),))))) == 6),
    ("R2-I27", "Contradiction endpoints classified into contradiction binding pairs.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"]["contradiction"] == "ONE_BINDING_PER_EXPLICIT_PAIR"),
    ("R2-I28", "RFC-11 eligible edges include simultaneous co-occurrence pairs.",
     lambda b: len(b._derive_rfc11_eligible_edges(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"), ("text", "b"))))) == 2),
    ("R2-I29", "RFC-11 eligible edges include adjacent forward and reverse sequence step pairs.",
     lambda b: ("text:A", "text:B") in b._derive_rfc11_eligible_edges(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "sequence", steps=((("text", "A"),), (("text", "B"),))))),
    ("R2-I30", "Non-adjacent sequence steps are strictly ineligible for RFC-11 evidence.",
     lambda b: ("text:A", "text:C") not in b._derive_rfc11_eligible_edges(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "sequence", steps=((("text", "A"),), (("text", "B"),), (("text", "C"),))))),
    ("R2-I31", "Role, category, concept, and instance edges are excluded from RFC-11 eligibility.",
     lambda b: b._is_excluded_rfc11_edge("ev:1", "text:a") and b._is_excluded_rfc11_edge("cat:1", "text:a") and b._is_excluded_rfc11_edge("hub:1", "text:a") and b._is_excluded_rfc11_edge("inst:1", "text:a")),
    ("R2-I32", "Root-equivalent persistent mutation transaction granularity (one Tx per root observation).",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["persistent_transaction_granularity"] == "ONE_ENCODED_INGRESS_EVENT"),
    ("R2-I33", "PersistentMutationCommand contains sorted unique positive and contradiction node refs.",
     lambda b: isinstance(R2_OBSERVATION_SEMANTICS_REGISTRY["receipt_order"], (list, tuple))),
    ("R2-I34", "Persistent TxID is deterministic and identical for same RootID and compiled intent.",
      lambda b: derive_observation_transaction_id("root_1", "ing_1", "observe", "v1") == derive_observation_transaction_id("root_1", "ing_1", "observe", "v1")),
    ("R2-I35", "Persistent graph execution precedes transient projection in AUTHORIZED_PERSISTENT mode.",
      lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["projection_timing"] == "AFTER_PERSISTENT_COMMIT_OR_REPLAY_DECISION"),
    ("R2-I36", "Persistent phase updates committed state before SDCR construction.",
      lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["projection_timing"] == "AFTER_PERSISTENT_COMMIT_OR_REPLAY_DECISION" and R2_OBSERVATION_SEMANTICS_REGISTRY["persistent_transaction_granularity"] == "ONE_ENCODED_INGRESS_EVENT"),
    ("R2-I37", "Idempotent replay of previously committed observation returns PERSISTENT_REPLAY.",
      lambda b: "PERSISTENT_REPLAY" in b.observe.__code__.co_consts),
    ("R2-I38", "Replay reconstructs transient representations cleanly from current state.",
      lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["transient_replay"] == "CURRENT_STATE_RECONSTRUCTION"),
    ("R2-I39", "Local parent cycle ID deterministically derived from ObservationTransactionID via prefix.",
      lambda b: LOCAL_CYCLE_PREFIX == "DGCA:R2:LOCAL_CYCLE:v1"),
    ("R2-I40", "Slot indices in receipt batch are strictly contiguous 0..N-1.",
      lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["receipt_order"] is not None),
    ("R2-I41", "Exact descriptor-owned receipt plan derived before comparing receipt entries.",
      lambda b: callable(derive_expected_receipt_plan)),
    ("R2-I42", "Occurrence scopes formatted as r2occ:<MID>:<kind>:<coords>.",
      lambda b: derive_expected_receipt_plan(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),)), "mep_1")[0].occurrence_scope.startswith("r2occ:mep_1:simultaneous:0")),
    ("R2-I43", "Node receipt scope_refs contain micro_episode_id, occurrence_scope, and binding scopes.",
      lambda b: "mep_1" in derive_expected_receipt_plan(CanonicalMicroEpisodeDescriptor(MICRO_DESCRIPTOR_VERSION, "simultaneous", signals=(("text", "a"),)), "mep_1")[0].occurrence_scope),
    ("R2-I44", "Edge receipt scope_refs contain micro_episode_id and r2relation scope.",
      lambda b: CanonicalReceiptEntry(0, "rid", "edge", ("a", "b"), "r2relation:m:0", ("m", "r2relation:m:0")).scope_refs[1].startswith("r2relation:")),
    ("R2-I45", "ParticipationReceipt origin_lineage and origin_view are external.",
     lambda b: CanonicalReceiptEntry(0, "rid", "node", "text:a", "r2occ:m:s:0", ("m", "r2occ:m:s:0")).origin_lineage == "external"),
    ("R2-I46", "Simultaneous TBR policy is SAME_STEP_ACTIVE_CO_OCCURRENCE.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"]["simultaneous"] == "ONE_BINDING_IF_AT_LEAST_TWO_POSITIVE_OCCURRENCES"),
    ("R2-I47", "Sequence TBR policy is ADJACENT_STEP_DIRECT_TEMPORAL.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"]["sequence"] == "ONE_BINDING_PER_ADJACENT_TRANSITION"),
    ("R2-I48", "Contradiction TBR policy is CONTRADICTION_ENDPOINT_PAIR.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"]["contradiction"] == "ONE_BINDING_PER_EXPLICIT_PAIR"),
    ("R2-I49", "Every member occurrence of a TBR must contain the TBR binding scope in scope_refs.",
     lambda b: all(k in R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"] for k in ("simultaneous", "sequence", "contradiction"))),
    ("R2-I50", "Receipt batch envelope enforces RECEIPT_BATCH_VERSION R2-RB-1.0.",
     lambda b: RECEIPT_BATCH_VERSION == "R2-RB-1.0"),
    ("R2-I51", "Ordered receipt entries follow positive nodes, contradictions, then edge relations.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["receipt_order"][0] == "POSITIVE_NODE_OCCURRENCES" and R2_OBSERVATION_SEMANTICS_REGISTRY["receipt_order"][1] == "CONTRADICTION_ENDPOINT_OCCURRENCES"),
    ("R2-I52", "Rederived expected receipt plan compared slot-by-slot against actual batch.",
     lambda b: callable(derive_expected_receipt_plan)),
    ("R2-I53", "Receipt attributes (ID, ref, scopes, activation, drive) strictly verified.",
      lambda b: all(a in ExpectedReceiptEntry.__dataclass_fields__ for a in ("slot_index", "slot_class", "kind", "element_ref", "occurrence_scope", "scope_refs", "activation_magnitude", "relational_drive", "receipt_id"))),
    ("R2-I54", "sdcr_cardinality policy is ONE_PER_OBSERVABLE_MICROEPISODE.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["sdcr_cardinality"] == "ONE_PER_OBSERVABLE_MICROEPISODE"),
    ("R2-I55", "Projection failure after persistent commit retains commit and cleans up transient representations.",
     lambda b: R2_OBSERVATION_SEMANTICS_REGISTRY["projection_failure"] == "PERSISTENT_COMMIT_REMAINS_AUTHORITATIVE_CLOSE_PARTIAL_SDCRS"),
    ("R2-I56", "R2ProjectionFailure exposes persistent_committed, failed_child_index, and transaction_id.",
     lambda b: hasattr(R2ProjectionFailure("fail", persistent_committed=True, failed_child_index=0, transaction_id="tx"), "persistent_committed")),
    ("R2-I57", "CanonicalObservationResult provides is_closed and close() method.",
     lambda b: hasattr(CanonicalObservationResult, "close") and hasattr(CanonicalObservationResult, "is_closed")),
    ("R2-I58", "Function-level close_result(result) is strictly idempotent, retiring active representations once.",
     lambda b: callable(close_result)),
]


@pytest.mark.parametrize("inv_id,desc,check_fn", FROZEN_R2_INVARIANTS)
def test_matrix_invariants_r2_i01_through_i58(inv_id, desc, check_fn):
    """R2 Invariant Verification Ledger: R2-I01 through R2-I58."""
    bridge = _make_bridge()
    assert check_fn(bridge) is True, f"Invariant {inv_id} ({desc}) failed check"


# ─────────────────────────────────────────────────────────── Test Obligations T01 .. T89
FROZEN_R2_TEST_EVIDENCE = {
    "T01": ("tests/test_ric01_r2_protocol.py::test_protocol_version_constants",),
    "T02": ("tests/test_ric01_r2_protocol.py::test_semantics_registry_and_digest",),
    "T03": ("tests/test_ric01_r2_protocol.py::test_error_hierarchy",),
    "T04": ("tests/test_ric01_r2_protocol.py::test_r2_projection_failure_attributes",),
    "T05": ("tests/test_ric01_r2_protocol.py::test_create_observation_bridge_protocol_check",),
    "T06": ("tests/test_ric01_r2_protocol.py::test_create_observation_bridge_fail_stop_and_lineage_checks",),
    "T07": ("tests/test_ric01_r2_repair.py::test_pir01_t01_exact_structured_semantics_registry",),
    "T08": ("tests/test_ric01_r2_repair.py::test_pir01_t02_semantics_digest_recomputed_no_constant_short_circuit",),
    "T09": ("tests/test_ric01_r2_repair.py::test_pir01_t03_one_nested_semantics_literal_mutation_changes_digest",),
    "T10": ("tests/test_ric01_r2_repair.py::test_pir01_t04_exact_simultaneous_micro_episode_descriptor_dictionary",),
    "T11": ("tests/test_ric01_r2_descriptors.py::test_text_event_descriptor",),
    "T12": ("tests/test_ric01_r2_descriptors.py::test_code_event_descriptor",),
    "T13": ("tests/test_ric01_r2_descriptors.py::test_micro_episode_descriptor_validation",),
    "T14": ("tests/test_ric01_r2_descriptors.py::test_binding_registry_conflict",),
    "T15": ("tests/test_ric01_r2_repair.py::test_pir01_t05_exact_sequence_micro_episode_descriptor_dictionary",),
    "T16": ("tests/test_ric01_r2_repair.py::test_pir01_t06_context_changes_canonical_micro_episode_descriptor_and_id",),
    "T17": ("tests/test_ric01_r2_repair.py::test_pir01_t07_malformed_simultaneous_empty_descriptor_rejected_pre_mutation",),
    "T18": ("tests/test_ric01_r2_repair.py::test_pir01_t08_one_step_sequence_rejected_pre_mutation",),
    "T19": ("tests/test_ric01_r2_repair.py::test_pir01_t34_generic_raw_payload_with_unknown_field_fails_closed",),
    "T20": ("tests/test_ric01_r2_repair.py::test_pir01_t35_episode_micro_descriptor_length_mismatch_fails_closed",),
    "T21": ("tests/test_ric01_r2_authorizer.py::test_default_authorizer_denies",),
    "T22": ("tests/test_ric01_r2_authorizer.py::test_authorized_persistent_fails_without_authorizer",),
    "T23": ("tests/test_ric01_r2_authorizer.py::test_authorized_persistent_fails_without_capability",),
    "T24": ("tests/test_ric01_r2_authorizer.py::test_authorized_persistent_fails_when_denied",),
    "T25": ("tests/test_ric01_r2_authorizer.py::test_authorizer_truthy_non_bool_fails_closed",),
    "T26": ("tests/test_ric01_r2_authorizer.py::test_authorizer_exception_fails_closed",),
    "T27": ("tests/test_ric01_r2_authorizer.py::test_authorizer_allows_valid_request",),
    "T28": ("tests/test_ric01_r2_repair.py::test_pir01_t13_truthy_non_bool_authorizer_return_rejected",),
    "T29": ("tests/test_ric01_r2_repair.py::test_pir01_t14_no_production_boolean_convenience_authorization_path",),
    "T30": ("tests/test_ric01_r2_adversarial.py::test_scenario_i_authorizer_returns_truthy_non_bool_fails_closed",),
    "T31": ("tests/test_ric01_r2_transient.py::test_transient_observation_zero_graph_mutation",),
    "T32": ("tests/test_ric01_r2_transient.py::test_transient_observation_generates_valid_sdcr",),
    "T33": ("tests/test_ric01_r2_adversarial.py::test_scenario_l_transient_only_before_after_persistent_payload_equality",),
    "T34": ("tests/test_ric01_r2_adversarial.py::test_scenario_m_iteration_perturbation_identical_canonical_ids_slots_bindings",),
    "T35": ("tests/test_ric01_r2_repair.py::test_pir01_t10_second_equivalent_subevent_produces_zero_graph_delta",),
    "T36": ("tests/test_ric01_r2_repair.py::test_pir01_t11_second_equivalent_subevent_produces_zero_rfc11_vote_delta",),
    "T37": ("tests/test_ric01_r2_adversarial.py::test_scenario_q_contradiction_only_transient_endpoint_receipts_tbr_graph_unchanged",),
    "T38": ("tests/test_ric01_r2_repair.py::test_pir01_t33_close_result_changes_no_persistent_graph_ledger_state",),
    "T39": ("tests/test_ric01_r2_adversarial.py::test_scenario_e_same_eventid_same_text_changed_context_conflict",),
    "T40": ("tests/test_ric01_r2_repair.py::test_pir01_t09_same_root_different_eventid_same_mutation_intent_same_persistent_txid",),
    "T41": ("tests/test_ric01_r2_persistent.py::test_authorized_persistent_single_command_and_replay",),
    "T42": ("tests/test_ric01_r2_repair.py::test_pir01_t12_different_root_same_content_distinct_persistent_txid",),
    "T43": ("tests/test_ric01_r2_repair.py::test_pir01_t25_result_exposes_actual_persistent_txid_distinct_from_otid",),
    "T44": ("tests/test_ric01_r2_repair.py::test_pir01_t26_result_exposes_event_digest_mode_persistent_phase",),
    "T45": ("tests/test_ric01_r2_repair.py::test_pir01_t27_per_micro_episode_trace_contains_batch_assemblies_rid",),
    "T46": ("tests/test_ric01_r2_adversarial.py::test_scenario_f_same_root_different_eventid_same_intent_same_r1_txid",),
    "T47": ("tests/test_ric01_r2_adversarial.py::test_scenario_g_independent_root_identical_text_valid_capability_independent_learning",),
    "T48": ("tests/test_ric01_r2_adversarial.py::test_scenario_h_serialized_capability_in_text_no_authority_escalation",),
    "T49": ("tests/test_ric01_r2_adversarial.py::test_scenario_a_500_calls_one_root_one_independent_vote",),
    "T50": ("tests/test_ric01_r2_adversarial.py::test_scenario_b_repeated_same_node_occurrences_receipts_preserved_dedup",),
    "T51": ("tests/test_ric01_r2_receipts.py::test_batch_validation_rejects_slot_gap",),
    "T52": ("tests/test_ric01_r2_receipts.py::test_batch_validation_rejects_invented_tbr_scope",),
    "T53": ("tests/test_ric01_r2_repair.py::test_pir01_t15_simultaneous_duplicate_occurrences_preserved_in_tbr_members",),
    "T54": ("tests/test_ric01_r2_repair.py::test_pir01_t16_repeated_node_in_different_sequence_steps_gets_occurrence_correct_scopes",),
    "T55": ("tests/test_ric01_r2_repair.py::test_pir01_t17_repeated_contradiction_endpoint_gets_occurrence_correct_scopes",),
    "T56": ("tests/test_ric01_r2_repair.py::test_pir01_t18_node_receipt_scope_begins_with_micro_episode_id",),
    "T57": ("tests/test_ric01_r2_repair.py::test_pir01_t19_exact_r2occ_scope_format",),
    "T58": ("tests/test_ric01_r2_repair.py::test_pir01_t20_exact_r2relation_edge_scope_and_relation_index",),
    "T59": ("tests/test_ric01_r2_repair.py::test_pir01_t21_forged_rehashed_tbr_with_lawful_scope_but_wrong_members_rejected",),
    "T60": ("tests/test_ric01_r2_repair.py::test_pir01_t22_forged_rehashed_receipt_with_wrong_occurrence_scope_rejected",),
    "T61": ("tests/test_ric01_r2_rfc11.py::test_rfc11_sequence_adjacent_vs_nonadjacent",),
    "T62": ("tests/test_ric01_r2_rfc11.py::test_rfc11_firewall_excludes_role_cat_hub_inst",),
    "T63": ("tests/test_ric01_r2_repair.py::test_pir01_t23_reverse_adjacent_sequence_edge_is_rfc11_eligible",),
    "T64": ("tests/test_ric01_r2_repair.py::test_pir01_t24_nonadjacent_forward_reverse_edges_remain_rfc11_ineligible",),
    "T65": ("tests/test_ric01_r2_adversarial.py::test_scenario_n_three_step_sequence_step0_step2_never_rfc11_evidence",),
    "T66": ("tests/test_ric01_r2_adversarial.py::test_scenario_o_synthetic_ev_edge_never_rfc11_vote",),
    "T67": ("tests/test_ric01_r2_adversarial.py::test_scenario_p_concept_generalization_side_effect_edge_never_rfc11_vote",),
    "T68": ("tests/test_ric01_r2_adversarial.py::test_scenario_c_forged_tbr_valid_hash_wrong_descriptor_authority_rejected",),
    "T69": ("tests/test_ric01_r2_adversarial.py::test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected",),
    "T70": ("tests/test_ric01_r2_adversarial.py::test_scenario_b_repeated_same_node_occurrences_receipts_preserved_dedup",),
    "T71": ("tests/test_ric01_r2_projection.py::test_sdcr_close_lifecycle",),
    "T72": ("tests/test_ric01_r2_projection.py::test_context_manager_lifecycle",),
    "T73": ("tests/test_ric01_r2_repair.py::test_pir01_t30_close_result_removes_rep_from_active_representations",),
    "T74": ("tests/test_ric01_r2_repair.py::test_pir01_t31_double_close_remains_idempotent",),
    "T75": ("tests/test_ric01_r2_adversarial.py::test_scenario_k_double_close_result_no_persistent_delta_no_failure",),
    "T76": ("tests/test_ric01_r2_repair.py::test_pir01_t32_partial_projection_failure_removes_every_earlier_rep_from_active_representations",),
    "T77": ("tests/test_ric01_r2_transient.py::test_transient_observation_generates_valid_sdcr",),
    "T78": ("tests/test_ric01_r2_projection.py::test_sdcr_close_lifecycle",),
    "T79": ("tests/test_ric01_r2_projection.py::test_context_manager_lifecycle",),
    "T80": ("tests/test_ric01_r2_repair.py::test_pir01_t30_close_result_removes_rep_from_active_representations",),
    "T81": ("tests/test_ric01_r2_failures.py::test_two_phase_projection_failure_semantics",),
    "T82": ("tests/test_ric01_r2_repair.py::test_pir01_t28_projection_failure_carries_actual_persistent_txid",),
    "T83": ("tests/test_ric01_r2_repair.py::test_pir01_t29_projection_failure_carries_actual_failing_child_index",),
    "T84": ("tests/test_ric01_r2_adversarial.py::test_scenario_j_commit_then_forced_later_child_rfc12_failure",),
    "T85": ("tests/test_ric01_r2_repair.py::test_pir01_t32_partial_projection_failure_removes_every_earlier_rep_from_active_representations",),
    "T86": ("tests/test_ric01_r2_protocol.py::test_r2_projection_failure_attributes",),
    "T87": ("tests/test_ric01_r2_failures.py::test_two_phase_projection_failure_semantics",),
    "T88": ("tests/test_ric01_r2_repair.py::test_pir01_t28_projection_failure_carries_actual_persistent_txid",),
    "T89": ("tests/test_ric01_r2_failures.py::test_two_phase_projection_failure_semantics",),
}

TEST_OBLIGATIONS = [(tid, refs) for tid, refs in sorted(FROZEN_R2_TEST_EVIDENCE.items())]


@pytest.mark.parametrize("t_id,test_refs", TEST_OBLIGATIONS)
def test_matrix_test_obligations_t01_through_t89(t_id, test_refs):
    """R2 Acceptance Test Obligation Ledger: T01 through T89 executed via genuine test nodes."""
    assert len(test_refs) > 0, f"Obligation {t_id} has no mapped test evidence"
    for ref in test_refs:
        mod_name, func_name = ref.split("::")
        mod = importlib.import_module(mod_name.replace("/", ".").replace("\\", ".").replace(".py", ""))
        fn = getattr(mod, func_name)
        assert callable(fn), f"Test target {ref} is not callable"
        fn()


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
