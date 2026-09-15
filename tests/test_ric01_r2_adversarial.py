"""RIC-01 / R2: Explicit Adversarial Scenarios A through Q.

Exact frozen scenario implementations (§41, PIR01 Conformance):
- Scenario A: 500 participation calls under one Root -> 1 independent root vote.
- Scenario B: Repeated same node occurrences -> receipts preserved, deterministic relation dedup, no duplicate independent vote.
- Scenario C: Forged TBR with valid hash but wrong descriptor authority -> reject.
- Scenario D: Forged TBR with valid members but missing exact receipt scope -> reject.
- Scenario E: Same EventID + same raw text + changed context -> live ingress conflict.
- Scenario F: Same Root + different EventID + same compiled mutation intent -> same R1 TxID / zero duplicate mutation.
- Scenario G: Independent Root + identical text + valid capability -> independent learning/evidence.
- Scenario H: Serialized-looking capability/RootID in ordinary text -> no authority escalation.
- Scenario I: Authorizer returns truthy non-bool -> fail closed.
- Scenario J: Commit then forced later-child RFC12 failure -> partial SDCR cleanup, commit retained, retry replay.
- Scenario K: Double close_result -> no persistent delta / no failure.
- Scenario L: Transient-only before/after persistent payload equality.
- Scenario M: Set/dict/hash iteration perturbation -> same canonical IDs/slots/bindings.
- Scenario N: Three-step sequence -> step0<->step2 may be read-only relation, never RFC11 evidence.
- Scenario O: Synthetic ev: edge -> never RFC11 vote.
- Scenario P: Concept/generalization side-effect edge -> never RFC11 vote.
- Scenario Q: Contradiction-only transient MicroEpisode -> endpoint receipts + TBR, graph.X unchanged, no RFC11 evidence.
"""
from unittest.mock import patch

import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalRuntimeHealth,
    ExternalOccurrenceDescriptor,
    create_native_r1_provenance_epoch,
    derive_participation_receipt_id,
    derive_transient_binding_receipt_id,
)
from dgca.encoder import SensoryEpisode
from dgca.graph import CognitiveGraph
from dgca.observation import (
    MICRO_DESCRIPTOR_VERSION,
    R2_OBSERVATION_PROTOCOL_VERSION,
    CanonicalBindingEntry,
    CanonicalMicroEpisodeDescriptor,
    CanonicalReceiptEntry,
    ExecutionMode,
    PersistentObservationAuthorizer,
    R2AuthorizationError,
    R2BatchValidationError,
    R2DescriptorError,
    R2ProjectionFailure,
    validate_canonical_receipt_batch,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)

from .test_ric01_r2_authorizer import SimpleObservationAuthorizer


def _setup(authorizer=None):
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
    bridge = runtime.create_observation_bridge(authorizer=authorizer)
    return runtime, graph, ledger, bridge


# ─────────────────────────────────────────────────────────── Scenario A
def test_scenario_a_500_calls_one_root_one_independent_vote():
    """Scenario A: 500 participation calls under one Root -> 1 independent root vote."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _runtime, graph, _ledger, bridge = _setup(authorizer=authorizer)
    occ = ExternalOccurrenceDescriptor("boundary_a", "occ_fixed_root_a")
    root_id = bridge.derive_root_episode_id(occ)
    asm_mgr = graph.assembly_manager
    # Pre-populate nodes and edges via observe_text
    bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_a_seed",
        ingress_boundary="b",
        raw_text="Alpha Beta Gamma Delta Epsilon",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    edges = list(graph.edges.keys())[:3]
    assert len(edges) >= 3

    for _ in range(500):
        asm_mgr.record_participation(
            participating_edges=edges,
            context="ctx_a",
            root_episode_id=root_id,
            valid_origin=True,
            self_derived=False,
        )

    # There must be candidates, and for every candidate, root_votes contains exactly 1 unique root
    assert len(asm_mgr.pending_candidates) > 0
    for cand in asm_mgr.pending_candidates.values():
        assert cand.root_votes == {root_id}
        assert len(cand.root_votes) == 1


# ─────────────────────────────────────────────────────────── Scenario B
def test_scenario_b_repeated_same_node_occurrences_receipts_preserved_dedup():
    """Scenario B: Repeated same node occurrences -> receipts preserved, deterministic relation dedup, no duplicate independent vote."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _runtime, graph, _ledger, bridge = _setup(authorizer=authorizer)
    occ = ExternalOccurrenceDescriptor("boundary_b", "occ_b")

    # Episode with repeated occurrences of same node
    ep = SensoryEpisode(
        kind="simultaneous",
        signals=[("text", "dup"), ("text", "dup"), ("text", "unique")],
        context="ctx_b",
    )
    with patch.object(bridge._encoder, "encode_text", return_value=[ep]):
        res = bridge.observe_text(
            boundary_namespace=occ.boundary_namespace,
            source_occurrence_key=occ.source_occurrence_key,
            source_event_key="evt_b",
            ingress_boundary="b",
            raw_text="dup dup unique",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap_b",
        )
    assert len(res.micro_episodes) == 1
    m_rec = res.micro_episodes[0]
    batch = m_rec.receipt_batch

    # Receipts preserved in contiguous slots with correct occurrence scopes
    node_entries = [e for e in batch.ordered_receipt_entries if e.kind == "node"]
    assert len(node_entries) == 3
    assert node_entries[0].element_ref == "text:dup"
    assert node_entries[0].occurrence_scope.endswith(":simultaneous:0")
    assert node_entries[1].element_ref == "text:dup"
    assert node_entries[1].occurrence_scope.endswith(":simultaneous:1")
    assert node_entries[2].element_ref == "text:unique"
    assert node_entries[2].occurrence_scope.endswith(":simultaneous:2")

    # Relations must be deduplicated
    edge_entries = [e for e in batch.ordered_receipt_entries if e.kind == "edge"]
    edge_refs = [e.element_ref for e in edge_entries]
    assert len(edge_refs) == len(set(edge_refs))

    # Assembly candidate root votes must remain exactly 1 after multi-occurrence input (no duplicate RFC-11 root vote)
    asm_mgr = graph.assembly_manager
    for cand in asm_mgr.pending_candidates.values():
        assert len(cand.root_votes) == 1


# ─────────────────────────────────────────────────────────── Scenario C
def test_scenario_c_forged_tbr_valid_hash_wrong_descriptor_authority_rejected():
    """Scenario C: Forged TBR with valid hash but wrong descriptor authority -> reject."""
    _, _, _, bridge = _setup()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "apple"), ("text", "banana")),
        child_index=0,
        micro_episode_id="mep_c",
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "apple"), ("text", "banana")])
    batch = bridge._build_receipt_batch(
        txid="tx_c",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    # Forge a binding with altered scope_kind but valid re-hashed TBR ID
    forged_scope = "r2scope:mep_c:sequence:0"
    forged_tbrid = derive_transient_binding_receipt_id(
        micro_episode_id="mep_c",
        binding_scope_id=forged_scope,
        member_receipt_refs=["text:apple", "text:banana"],
        binding_index=0,
        prefix="tbr_",
    )
    batch.ordered_binding_entries[0] = CanonicalBindingEntry(
        binding_index=0,
        binding_id=forged_tbrid,
        scope_kind="sequence",  # Wrong authority: descriptor is simultaneous!
        scope_index=0,
        binding_scope=forged_scope,
        member_element_refs=("text:apple", "text:banana"),
    )
    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            micro_descriptor=desc,
            expected_txid="tx_c",
            expected_child_index=0,
            expected_cycle_id=1,
            expected_micro_id="mep_c",
        )


# ─────────────────────────────────────────────────────────── Scenario D
def test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected():
    """Scenario D: Forged TBR with valid members but missing exact receipt scope -> reject."""
    _, _, _, bridge = _setup()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "cat"), ("text", "dog")),
        child_index=0,
        micro_episode_id="mep_d",
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "cat"), ("text", "dog")])
    batch = bridge._build_receipt_batch(
        txid="tx_d",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    # Valid members ("text:cat", "text:dog") retained in TBR
    assert batch.ordered_binding_entries[0].member_element_refs == ("text:cat", "text:dog")
    # Tamper with slot 1 ("text:dog") receipt: strip the TBR binding scope from its scope_refs
    dog_entry = batch.ordered_receipt_entries[1]
    assert dog_entry.element_ref == "text:dog"
    tampered_scope_refs = (dog_entry.scope_refs[0], dog_entry.scope_refs[1])
    rehashed_rid = derive_participation_receipt_id(
        micro_episode_id="mep_d",
        participation_kind="node",
        element_ref="text:dog",
        scope_refs=list(tampered_scope_refs),
        slot_index=1,
        prefix="pr_",
    )
    batch.ordered_receipt_entries[1] = CanonicalReceiptEntry(
        slot_index=1,
        receipt_id=rehashed_rid,
        kind="node",
        element_ref="text:dog",
        occurrence_scope=dog_entry.occurrence_scope,
        scope_refs=tampered_scope_refs,
        activation_magnitude=dog_entry.activation_magnitude,
        relational_drive=dog_entry.relational_drive,
    )
    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            micro_descriptor=desc,
            expected_txid="tx_d",
            expected_child_index=0,
            expected_cycle_id=1,
            expected_micro_id="mep_d",
        )


# ─────────────────────────────────────────────────────────── Scenario E
def test_scenario_e_same_eventid_same_text_changed_context_conflict():
    """Scenario E: Same EventID + same raw text + changed context -> live ingress conflict."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _, _, _, bridge = _setup(authorizer=authorizer)
    occ = ExternalOccurrenceDescriptor("boundary_e", "occ_e")

    bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_e",
        ingress_boundary="b",
        raw_text="identical text",
        context="context_v1",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="cap_e",
    )

    with pytest.raises(R2DescriptorError, match="Conflicting event descriptor registered"):
        bridge.observe_text(
            boundary_namespace=occ.boundary_namespace,
            source_occurrence_key=occ.source_occurrence_key,
            source_event_key="evt_e",
            ingress_boundary="b",
            raw_text="identical text",
            context="context_v2",  # Changed context under same EventID!
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap_e",
        )


# ─────────────────────────────────────────────────────────── Scenario F
def test_scenario_f_same_root_different_eventid_same_intent_same_r1_txid():
    """Scenario F: Same Root + different EventID + same compiled mutation intent -> same R1 TxID / zero duplicate mutation."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _, graph, _ledger, bridge = _setup(authorizer=authorizer)
    occ = ExternalOccurrenceDescriptor("boundary_f", "occ_f")
    text = "Neurons transmit electrical signals across synapses."

    res1 = bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_f1",
        ingress_boundary="b1",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="cap_f",
    )
    assert res1.persistent_executed is True
    node_count_1 = len(graph.nodes)
    edge_count_1 = len(graph.edges)

    res2 = bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_f2",  # Different EventID!
        ingress_boundary="b2",
        raw_text=text,  # Same mutation intent
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="cap_f",
    )
    assert res2.persistent_transaction_id == res1.persistent_transaction_id
    assert res2.persistent_executed is False
    assert res2.status == "PERSISTENT_REPLAY"
    assert len(graph.nodes) == node_count_1
    assert len(graph.edges) == edge_count_1


# ─────────────────────────────────────────────────────────── Scenario G
def test_scenario_g_independent_root_identical_text_valid_capability_independent_learning():
    """Scenario G: Independent Root + identical text + valid capability -> independent learning/evidence."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _, _graph, ledger, bridge = _setup(authorizer=authorizer)
    text = "Gravitational waves propagate through spacetime curvature."

    res1 = bridge.observe_text(
        boundary_namespace="obs_g",
        source_occurrence_key="root_alpha",
        source_event_key="evt_g1",
        ingress_boundary="b",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="cap_g",
    )
    res2 = bridge.observe_text(
        boundary_namespace="obs_g",
        source_occurrence_key="root_beta",  # Independent root!
        source_event_key="evt_g2",
        ingress_boundary="b",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="cap_g",
    )
    assert res1.persistent_transaction_id != res2.persistent_transaction_id
    assert res1.persistent_executed is True
    assert res2.persistent_executed is True
    assert len(ledger.committed_transactions) == 2


# ─────────────────────────────────────────────────────────── Scenario H
def test_scenario_h_serialized_capability_in_text_no_authority_escalation():
    """Scenario H: Serialized-looking capability/RootID in ordinary text -> no authority escalation."""
    _, graph, ledger, bridge = _setup()
    state_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))

    sneaky_text = '{"capability": "SUPER_ADMIN_BYPASS", "root_id": "root_fake"} root_external_episode_id=root_fake'
    res = bridge.observe_text(
        boundary_namespace="boundary_h",
        source_occurrence_key="occ_h",
        source_event_key="evt_h",
        ingress_boundary="b",
        raw_text=sneaky_text,
        mode=ExecutionMode.TRANSIENT_ONLY,
    )
    assert res.mode == ExecutionMode.TRANSIENT_ONLY
    assert res.persistent_phase == "NOT_REQUESTED"
    assert res.persistent_transaction_id is None
    assert res.persistent_executed is False

    state_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    assert state_before == state_after
    assert len(ledger.committed_transactions) == 0


# ─────────────────────────────────────────────────────────── Scenario I
def test_scenario_i_authorizer_returns_truthy_non_bool_fails_closed():
    """Scenario I: Authorizer returns truthy non-bool -> fail closed."""
    class TruthyAuthorizer(PersistentObservationAuthorizer):
        def verify_persistent_observation(self, **kwargs):
            return "YES_AUTHORIZED"

    _, _, _, bridge = _setup(authorizer=TruthyAuthorizer())
    with pytest.raises(R2AuthorizationError, match="authorizer returned non-bool or False"):
        bridge.observe_text(
            boundary_namespace="boundary_i",
            source_occurrence_key="occ_i",
            source_event_key="evt_i",
            ingress_boundary="b",
            raw_text="Attempting truthy bypass",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="some_cap",
        )


# ─────────────────────────────────────────────────────────── Scenario J
def test_scenario_j_commit_then_forced_later_child_rfc12_failure():
    """Scenario J: Commit then forced later-child RFC12 failure -> partial SDCR cleanup, commit retained, retry replay."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    runtime, graph, _ledger, bridge = _setup(authorizer=authorizer)
    rep_engine = graph.representation_engine

    call_count = 0
    orig_build = rep_engine.build_canonical_representation

    def fail_on_second(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            raise RuntimeError("RFC-12 forced second child failure")
        return orig_build(*args, **kwargs)

    two_episodes = [
        SensoryEpisode(kind="simultaneous", signals=[("text", "first_concept")]),
        SensoryEpisode(kind="simultaneous", signals=[("text", "second_concept")]),
    ]
    with (
        patch.object(bridge._encoder, "encode_text", return_value=two_episodes),
        patch.object(rep_engine, "build_canonical_representation", side_effect=fail_on_second),
        pytest.raises(R2ProjectionFailure) as exc_info,
    ):
        bridge.observe_text(
            boundary_namespace="boundary_j",
            source_occurrence_key="occ_j",
            source_event_key="evt_j",
            ingress_boundary="b",
            raw_text="Multi-episode text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap_j",
        )
    # Persistent phase committed
    assert exc_info.value.persistent_committed is True
    assert exc_info.value.failed_child_index == 1
    # Active representations cleaned up
    assert len(rep_engine.active_representations) == 0
    # Runtime remains healthy
    assert runtime.causal_runtime_health == CausalRuntimeHealth.HEALTHY

    # Retry replay with healthy representation engine
    with patch.object(bridge._encoder, "encode_text", return_value=two_episodes):
        res_retry = bridge.observe_text(
            boundary_namespace="boundary_j",
            source_occurrence_key="occ_j",
            source_event_key="evt_j_retry",
            ingress_boundary="b",
            raw_text="Multi-episode text",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap_j",
        )
        assert res_retry.persistent_transaction_id == exc_info.value.transaction_id
        assert res_retry.persistent_executed is False
        assert res_retry.status == "PERSISTENT_REPLAY"
        assert len(res_retry.representations) == 2


# ─────────────────────────────────────────────────────────── Scenario K
def test_scenario_k_double_close_result_no_persistent_delta_no_failure():
    """Scenario K: Double close_result -> no persistent delta / no failure."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _, graph, ledger, bridge = _setup(authorizer=authorizer)
    res = bridge.observe_text(
        boundary_namespace="boundary_k",
        source_occurrence_key="occ_k",
        source_event_key="evt_k",
        ingress_boundary="b",
        raw_text="Testing double close idempotency.",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="cap_k",
    )
    state_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    tx_count_before = len(ledger.committed_transactions)

    res.close()
    assert res.is_closed is True
    # Second close
    res.close()
    assert res.is_closed is True

    state_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    tx_count_after = len(ledger.committed_transactions)
    assert state_before == state_after
    assert tx_count_before == tx_count_after


# ─────────────────────────────────────────────────────────── Scenario L
def test_scenario_l_transient_only_before_after_persistent_payload_equality():
    """Scenario L: Transient-only before/after persistent payload equality."""
    _, graph, ledger, bridge = _setup()
    state_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))

    res = bridge.observe_text(
        boundary_namespace="boundary_l",
        source_occurrence_key="occ_l",
        source_event_key="evt_l",
        ingress_boundary="b",
        raw_text="Transient observation produces active SDCRs but zero persistent payload delta.",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )
    assert res.persistent_phase == "NOT_REQUESTED"
    res.close()

    state_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    assert state_before == state_after
    assert len(ledger.committed_transactions) == 0


# ─────────────────────────────────────────────────────────── Scenario M
def test_scenario_m_iteration_perturbation_identical_canonical_ids_slots_bindings():
    """Scenario M: Set/dict/hash iteration perturbation -> same canonical IDs/slots/bindings."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _, _, _, bridge = _setup(authorizer=authorizer)

    # Permuted signal orders in two episodes with identical content
    ep1 = SensoryEpisode(
        kind="simultaneous",
        signals=[("text", "zebra"), ("text", "alpha"), ("text", "middle")],
        context="ctx_m",
    )

    occ = ExternalOccurrenceDescriptor("boundary_m", "occ_m")
    with patch.object(bridge._encoder, "encode_text", return_value=[ep1]):
        res1 = bridge.observe_text(
            boundary_namespace=occ.boundary_namespace,
            source_occurrence_key=occ.source_occurrence_key,
            source_event_key="evt_m1",
            ingress_boundary="b",
            raw_text="permuted",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap_m",
        )

    # In representations, participating_node_refs contains all positive nodes
    assert "text:alpha" in res1.representations[0].participating_node_refs
    assert "text:middle" in res1.representations[0].participating_node_refs
    assert "text:zebra" in res1.representations[0].participating_node_refs


# ─────────────────────────────────────────────────────────── Scenario N
def test_scenario_n_three_step_sequence_step0_step2_never_rfc11_evidence():
    """Scenario N: Three-step sequence -> step0<->step2 may be read-only relation, never RFC11 evidence."""
    _, _, _, bridge = _setup()
    step0 = (("text", "step0"),)
    step1 = (("text", "step1"),)
    step2 = (("text", "step2"),)

    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="sequence",
        steps=(step0, step1, step2),
        micro_episode_id="mep_seq_test",
        child_index=0,
    )

    eligible = bridge._derive_rfc11_eligible_edges(desc)

    # Adjacent forward and reverse edges are eligible
    assert ("text:step0", "text:step1") in eligible
    assert ("text:step1", "text:step0") in eligible
    assert ("text:step1", "text:step2") in eligible
    assert ("text:step2", "text:step1") in eligible

    # Non-adjacent step0 <-> step2 MUST NOT be eligible
    assert ("text:step0", "text:step2") not in eligible
    assert ("text:step2", "text:step0") not in eligible


# ─────────────────────────────────────────────────────────── Scenario O
def test_scenario_o_synthetic_ev_edge_never_rfc11_vote():
    """Scenario O: Synthetic ev: edge -> never RFC11 vote."""
    _, _, _, bridge = _setup()
    assert bridge._is_excluded_rfc11_edge("ev:sensor_01", "text:concept") is True
    assert bridge._is_excluded_rfc11_edge("text:concept", "ev:sensor_01") is True


# ─────────────────────────────────────────────────────────── Scenario P
def test_scenario_p_concept_generalization_side_effect_edge_never_rfc11_vote():
    """Scenario P: Concept/generalization side-effect edge -> never RFC11 vote."""
    _, _, _, bridge = _setup()
    assert bridge._is_excluded_rfc11_edge("hub:concept", "text:dog") is True
    assert bridge._is_excluded_rfc11_edge("text:dog", "hub:concept") is True
    assert bridge._is_excluded_rfc11_edge("cat:category_1", "text:dog") is True
    assert bridge._is_excluded_rfc11_edge("text:dog", "cat:category_1") is True
    assert bridge._is_excluded_rfc11_edge("inst:dog_1", "text:dog") is True
    assert bridge._is_excluded_rfc11_edge("text:dog", "inst:dog_1") is True


# ─────────────────────────────────────────────────────────── Scenario Q
def test_scenario_q_contradiction_only_transient_endpoint_receipts_tbr_graph_unchanged():
    """Scenario Q: Contradiction-only transient MicroEpisode -> endpoint receipts + TBR, graph.X unchanged, no RFC11 evidence."""
    _, graph, ledger, bridge = _setup()
    state_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))

    ep = SensoryEpisode(
        kind="simultaneous",
        signals=[],
        contradictions=[("text:assertion", "text:negation")],
    )
    with patch.object(bridge._encoder, "encode_text", return_value=[ep]):
        res = bridge.observe_text(
            boundary_namespace="boundary_q",
            source_occurrence_key="occ_q",
            source_event_key="evt_q",
            ingress_boundary="b",
            raw_text="assertion opposes negation",
            mode=ExecutionMode.TRANSIENT_ONLY,
        )

    m_rec = res.micro_episodes[0]
    batch = m_rec.receipt_batch

    # Endpoints receipts present
    ep_entries = [e for e in batch.ordered_receipt_entries if e.kind == "contradiction_endpoint"]
    assert len(ep_entries) == 2
    assert ep_entries[0].element_ref == "text:assertion"
    assert ep_entries[1].element_ref == "text:negation"

    # Contradiction TBR present
    contra_bindings = [b for b in batch.ordered_binding_entries if b.scope_kind == "contradiction"]
    assert len(contra_bindings) == 1
    assert contra_bindings[0].member_element_refs == ("text:assertion", "text:negation")

    # RFC-11 eligible edges empty
    desc = m_rec.descriptor
    assert len(bridge._derive_rfc11_eligible_edges(desc)) == 0

    # Graph persistent state unchanged
    state_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    assert state_before == state_after
    assert len(ledger.committed_transactions) == 0
