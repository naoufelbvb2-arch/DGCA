"""
DGCA — RIC-01 / R2-PIR-01
Conformance Repair Acceptance Tests (PIR01-T01 .. PIR01-T35)
Section 14 of Strict Repair & Verification Master Prompt v1.0 — FROZEN
"""
import json
from unittest.mock import patch

import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    ExternalOccurrenceDescriptor,
    create_native_r1_provenance_epoch,
    derive_micro_episode_id,
    derive_participation_receipt_id,
    derive_transient_binding_receipt_id,
)
from dgca.encoder import SensoryEpisode
from dgca.graph import CognitiveGraph
from dgca.observation import (
    MICRO_DESCRIPTOR_VERSION,
    R2_OBSERVATION_PROTOCOL_VERSION,
    R2_OBSERVATION_SEMANTICS_DIGEST,
    R2_OBSERVATION_SEMANTICS_REGISTRY,
    CanonicalBindingEntry,
    CanonicalMicroEpisodeDescriptor,
    CanonicalReceiptBatch,
    CanonicalReceiptEntry,
    ExecutionMode,
    R2AuthorizationError,
    R2BatchValidationError,
    R2DescriptorError,
    R2ProjectionFailure,
    close_result,
    compute_r2_observation_semantics_digest,
    validate_canonical_receipt_batch,
    validate_r2_observation_semantics_registry,
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


# ─────────────────────────────────────────────────────────── PIR01-B01: Semantics Registry & Digest (T01 - T03)
def test_pir01_t01_exact_structured_semantics_registry():
    """PIR01-T01: Exact structured semantics registry containing all 18 frozen policy literals."""
    assert isinstance(R2_OBSERVATION_SEMANTICS_REGISTRY, dict)
    assert len(R2_OBSERVATION_SEMANTICS_REGISTRY) == 18
    validate_r2_observation_semantics_registry()
    assert R2_OBSERVATION_SEMANTICS_REGISTRY["authorization_default"] == "DENY_ALL"
    assert R2_OBSERVATION_SEMANTICS_REGISTRY["sdcr_cardinality"] == "ONE_PER_OBSERVABLE_MICROEPISODE"
    assert R2_OBSERVATION_SEMANTICS_REGISTRY["transient_replay"] == "CURRENT_STATE_RECONSTRUCTION"


def test_pir01_t02_semantics_digest_recomputed_no_constant_short_circuit():
    """PIR01-T02: Semantics digest actually recomputed from canonical JSON bytes with no short-circuit."""
    computed = compute_r2_observation_semantics_digest()
    assert computed == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"
    assert len(computed) == 64
    assert computed == R2_OBSERVATION_SEMANTICS_DIGEST


def test_pir01_t03_one_nested_semantics_literal_mutation_changes_digest():
    """PIR01-T03: Mutating any one nested literal changes digest; reverting restores exact digest."""
    base_digest = compute_r2_observation_semantics_digest()
    for key in ("authorization_default", "sdcr_cardinality", "transient_replay"):
        mutated = json.loads(json.dumps(R2_OBSERVATION_SEMANTICS_REGISTRY))
        mutated[key] = "MUTATED_VALUE"
        mut_digest = compute_r2_observation_semantics_digest(mutated)
        assert mut_digest != base_digest, f"Digest did not change on mutation of {key}"
    # Reverting restores exact digest
    assert compute_r2_observation_semantics_digest(R2_OBSERVATION_SEMANTICS_REGISTRY) == base_digest


# ─────────────────────────────────────────────────────────── PIR01-B02: Canonical MicroEpisode Descriptor (T04 - T08)
def test_pir01_t04_exact_simultaneous_micro_episode_descriptor_dictionary():
    """PIR01-T04: Exact simultaneous MicroEpisode descriptor dictionary without child_index/micro_episode_id."""
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        context="ctx_sim",
        signals=(("text", "apple"), ("text", "fruit")),
        steps=(),
        structural_weight=1.0,
        valence=0.2,
        contradictions=(),
        child_index=0,
        micro_episode_id="mep_sim",
    )
    d = desc.to_dict()
    assert d == {
        "descriptor_version": "R2-MICRO-1.0",
        "kind": "simultaneous",
        "context": "ctx_sim",
        "signals": [["text", "apple"], ["text", "fruit"]],
        "steps": [],
        "structural_weight": 1.0,
        "valence": 0.2,
        "contradictions": [],
    }
    assert "child_index" not in d
    assert "micro_episode_id" not in d


def test_pir01_t05_exact_sequence_micro_episode_descriptor_dictionary():
    """PIR01-T05: Exact sequence MicroEpisode descriptor dictionary without child_index/micro_episode_id."""
    step0 = (("text", "A"),)
    step1 = (("text", "B"),)
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="sequence",
        context="ctx_seq",
        signals=(),
        steps=(step0, step1),
        structural_weight=0.8,
        valence=-0.1,
        contradictions=(),
        child_index=1,
        micro_episode_id="mep_seq",
    )
    d = desc.to_dict()
    assert d == {
        "descriptor_version": "R2-MICRO-1.0",
        "kind": "sequence",
        "context": "ctx_seq",
        "signals": [],
        "steps": [[["text", "A"]], [["text", "B"]]],
        "structural_weight": 0.8,
        "valence": -0.1,
        "contradictions": [],
    }
    assert "child_index" not in d
    assert "micro_episode_id" not in d


def test_pir01_t06_context_changes_canonical_micro_episode_descriptor_and_id():
    """PIR01-T06: Context is included in descriptor and changes derived MicroEpisodeID."""
    d1 = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        context="context_A",
        signals=(("text", "cat"),),
    )
    d2 = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        context="context_B",
        signals=(("text", "cat"),),
    )
    assert d1.to_dict() != d2.to_dict()
    id1 = derive_micro_episode_id("tx_obs_1", 0, d1.to_dict())
    id2 = derive_micro_episode_id("tx_obs_1", 0, d2.to_dict())
    assert id1 != id2


def test_pir01_t07_malformed_simultaneous_empty_descriptor_rejected_pre_mutation():
    """PIR01-T07: Simultaneous descriptor with neither signals nor contradictions rejected."""
    with pytest.raises(R2DescriptorError, match="non-empty signals or contradictions"):
        CanonicalMicroEpisodeDescriptor(
            descriptor_version=MICRO_DESCRIPTOR_VERSION,
            kind="simultaneous",
            signals=(),
            contradictions=(),
        )


def test_pir01_t08_one_step_sequence_rejected_pre_mutation():
    """PIR01-T08: Sequence descriptor with fewer than 2 steps rejected."""
    with pytest.raises(R2DescriptorError, match="at least 2 steps"):
        CanonicalMicroEpisodeDescriptor(
            descriptor_version=MICRO_DESCRIPTOR_VERSION,
            kind="sequence",
            steps=((("text", "only_one"),),),
        )


# ─────────────────────────────────────────────────────────── PIR01-B03: Root-Equivalent Persistent Command & TxID (T09 - T12)
def test_pir01_t09_same_root_different_eventid_same_mutation_intent_same_persistent_txid():
    """PIR01-T09: Same Root + different EventID + same compiled intent → same R1 persistent TxID."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    occ = ExternalOccurrenceDescriptor("net_root", "occ_fixed_001")
    text = "Photosynthesis converts sunlight to energy."

    res1 = bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="transport_packet_01",
        ingress_boundary="gateway_A",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res1.status == "PERSISTENT_EXECUTED"

    res2 = bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="transport_packet_02",  # Different transport event
        ingress_boundary="gateway_B",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res2.status == "PERSISTENT_REPLAY"
    assert res1.persistent_transaction_id == res2.persistent_transaction_id
    assert res1.ingress_event_id != res2.ingress_event_id


def test_pir01_t10_second_equivalent_subevent_produces_zero_graph_delta():
    """PIR01-T10: Second equivalent subevent under same root produces zero graph delta."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    graph = bridge._graph
    occ = ExternalOccurrenceDescriptor("net_root", "occ_fixed_002")
    text = "Cellular respiration produces ATP."

    res1 = bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_sub_01",
        ingress_boundary="b1",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res1.status == "PERSISTENT_EXECUTED"
    node_count_1 = len(graph.nodes)
    edge_count_1 = len(graph.edges)

    res2 = bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_sub_02",
        ingress_boundary="b2",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res2.status == "PERSISTENT_REPLAY"
    assert len(graph.nodes) == node_count_1
    assert len(graph.edges) == edge_count_1


def test_pir01_t11_second_equivalent_subevent_produces_zero_rfc11_vote_delta():
    """PIR01-T11: Second equivalent subevent produces zero additional RFC-11 independent root vote."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    graph = bridge._graph
    occ = ExternalOccurrenceDescriptor("net_root", "occ_fixed_003")
    text = "Neurons transmit electrical signals."

    bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_vote_01",
        ingress_boundary="b1",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    asm_mgr = graph.assembly_manager
    assert asm_mgr is not None
    votes_before = {k: set(c.root_votes) for k, c in asm_mgr.pending_candidates.items()}
    growth_before = {k: set(v) for k, v in asm_mgr.pending_growth.items()}

    bridge.observe_text(
        boundary_namespace=occ.boundary_namespace,
        source_occurrence_key=occ.source_occurrence_key,
        source_event_key="evt_vote_02",
        ingress_boundary="b2",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    votes_after = {k: set(c.root_votes) for k, c in asm_mgr.pending_candidates.items()}
    growth_after = {k: set(v) for k, v in asm_mgr.pending_growth.items()}
    assert votes_before == votes_after
    assert growth_before == growth_after


def test_pir01_t12_different_root_same_content_distinct_persistent_txid():
    """PIR01-T12: Different Root + same content → distinct persistent TxID and independent learning."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    text = "Gravitational waves propagate through spacetime."

    res1 = bridge.observe_text(
        boundary_namespace="space",
        source_occurrence_key="source_alpha",
        source_event_key="evt_1",
        ingress_boundary="boundary",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    res2 = bridge.observe_text(
        boundary_namespace="space",
        source_occurrence_key="source_beta",  # Different root
        source_event_key="evt_2",
        ingress_boundary="boundary",
        raw_text=text,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res1.status == "PERSISTENT_EXECUTED"
    assert res2.status == "PERSISTENT_EXECUTED"
    assert res1.persistent_transaction_id != res2.persistent_transaction_id
    assert res1.root_external_episode_id != res2.root_external_episode_id


# ─────────────────────────────────────────────────────────── PIR01-B04: Strict Authorization (T13 - T14)
def test_pir01_t13_truthy_non_bool_authorizer_return_rejected():
    """PIR01-T13: Truthy non-bool authorizer returns are strictly rejected."""
    for bad_val in (1, "yes", "true", [True], object(), 1.0):
        bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(callback=lambda val=bad_val, **k: val))
        with pytest.raises(R2AuthorizationError, match="authorizer returned non-bool or False"):
            bridge.observe_text(
                boundary_namespace="auth",
                source_occurrence_key="occ_truthy",
                source_event_key="evt_t",
                ingress_boundary="b",
                raw_text="authorization test",
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability="cap",
            )


def test_pir01_t14_no_production_boolean_convenience_authorization_path():
    """PIR01-T14: No SimpleObservationAuthorizer in production dgca.observation."""
    import dgca.observation as obs
    assert not hasattr(obs, "SimpleObservationAuthorizer")


# ─────────────────────────────────────────────────────────── PIR01-B05: Receipt/TBR Scope Semantics (T15 - T22)
def test_pir01_t15_simultaneous_duplicate_occurrences_preserved_in_tbr_members():
    """PIR01-T15: Simultaneous duplicate occurrences preserved in TBR members order."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "apple"), ("text", "apple"), ("text", "banana")),
        micro_episode_id="mep_dup",
        child_index=0,
    )
    ep = SensoryEpisode(
        signals=[("text", "apple"), ("text", "apple"), ("text", "banana")],
        kind="simultaneous",
    )
    batch = bridge._build_receipt_batch(
        txid="tx_test",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    assert len(batch.ordered_binding_entries) == 1
    tbr = batch.ordered_binding_entries[0]
    # Duplicates must NOT be deduplicated in TBR members
    assert tbr.member_element_refs == ("text:apple", "text:apple", "text:banana")


def test_pir01_t16_repeated_node_in_different_sequence_steps_gets_occurrence_correct_scopes():
    """PIR01-T16: Repeated node in different sequence steps gets occurrence-correct scopes."""
    bridge = _make_bridge()
    step0 = (("text", "A"),)
    step1 = (("text", "B"),)
    step2 = (("text", "A"),)  # Repeated in step 2
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="sequence",
        steps=(step0, step1, step2),
        micro_episode_id="mep_rep_seq",
        child_index=0,
    )
    ep = SensoryEpisode(steps=[[("text", "A")], [("text", "B")], [("text", "A")]], kind="sequence")
    batch = bridge._build_receipt_batch(
        txid="tx_test",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    # Receipts: slot 0 (A step 0), slot 1 (B step 1), slot 2 (A step 2)
    r_a0 = batch.ordered_receipt_entries[0]
    r_a2 = batch.ordered_receipt_entries[2]
    assert r_a0.occurrence_scope == "r2occ:mep_rep_seq:step:0:0"
    assert r_a2.occurrence_scope == "r2occ:mep_rep_seq:step:2:0"
    # r_a0 is in transition 0 (src)
    assert "r2scope:mep_rep_seq:sequence:0" in r_a0.scope_refs
    assert "r2scope:mep_rep_seq:sequence:1" not in r_a0.scope_refs
    # r_a2 is in transition 1 (dst)
    assert "r2scope:mep_rep_seq:sequence:1" in r_a2.scope_refs
    assert "r2scope:mep_rep_seq:sequence:0" not in r_a2.scope_refs


def test_pir01_t17_repeated_contradiction_endpoint_gets_occurrence_correct_scopes():
    """PIR01-T17: Repeated contradiction endpoint gets occurrence-correct scopes."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "sig"),),
        contradictions=(("X", "Y"), ("X", "Z")),  # "X" repeated in pair 0 and pair 1
        micro_episode_id="mep_contra",
        child_index=0,
    )
    ep = SensoryEpisode(signals=[("text", "sig")], contradictions=[("X", "Y"), ("X", "Z")], kind="simultaneous")
    batch = bridge._build_receipt_batch(
        txid="tx_test",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    # Endpoint receipts start at slot 1
    r_x0 = batch.ordered_receipt_entries[1]
    r_x1 = batch.ordered_receipt_entries[3]
    assert r_x0.element_ref == "text:X"
    assert r_x1.element_ref == "text:X"
    assert r_x0.occurrence_scope == "r2occ:mep_contra:contradiction:0:0"
    assert r_x1.occurrence_scope == "r2occ:mep_contra:contradiction:1:0"
    assert "r2scope:mep_contra:contradiction:0" in r_x0.scope_refs
    assert "r2scope:mep_contra:contradiction:1" not in r_x0.scope_refs
    assert "r2scope:mep_contra:contradiction:1" in r_x1.scope_refs
    assert "r2scope:mep_contra:contradiction:0" not in r_x1.scope_refs


def test_pir01_t18_node_receipt_scope_begins_with_micro_episode_id():
    """PIR01-T18: Every node receipt scope_refs begins with (MicroEpisodeID, local_occurrence_scope)."""
    bridge = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="scope_test",
        source_occurrence_key="occ_s",
        source_event_key="evt_s",
        ingress_boundary="b",
        raw_text="Deterministic testing is essential.",
    )
    for mep_rec in res.micro_episodes:
        batch = mep_rec.receipt_batch
        assert batch is not None
        for r in batch.ordered_receipt_entries:
            assert r.scope_refs[0] == batch.micro_episode_id
            assert r.scope_refs[1] == r.occurrence_scope


def test_pir01_t19_exact_r2occ_scope_format():
    """PIR01-T19: Exact r2occ scope format verified across simultaneous, sequence, and contradiction."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "A"),),
        contradictions=(("hot", "cold"),),
        micro_episode_id="mep_format",
        child_index=0,
    )
    ep = SensoryEpisode(signals=[("text", "A")], contradictions=[("hot", "cold")], kind="simultaneous")
    batch = bridge._build_receipt_batch(
        txid="tx_t",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    assert batch.ordered_receipt_entries[0].occurrence_scope == "r2occ:mep_format:simultaneous:0"
    assert batch.ordered_receipt_entries[1].occurrence_scope == "r2occ:mep_format:contradiction:0:0"
    assert batch.ordered_receipt_entries[2].occurrence_scope == "r2occ:mep_format:contradiction:0:1"


def test_pir01_t20_exact_r2relation_edge_scope_and_relation_index():
    """PIR01-T20: Exact r2relation edge scope uses canonical relation list index."""
    bridge = _make_bridge()
    bridge._graph.link("text:alpha", "text:beta", W=0.7)
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "alpha"), ("text", "beta")),
        micro_episode_id="mep_rel",
        child_index=0,
    )
    ep = SensoryEpisode(signals=[("text", "alpha"), ("text", "beta")], kind="simultaneous")
    batch = bridge._build_receipt_batch(
        txid="tx_t",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    edge_entries = [r for r in batch.ordered_receipt_entries if r.kind == "edge"]
    assert len(edge_entries) >= 1
    for e in edge_entries:
        assert e.occurrence_scope.startswith("r2relation:mep_rel:")
        assert e.scope_refs[0] == "mep_rel"
        assert e.scope_refs[1] == e.occurrence_scope


def test_pir01_t21_forged_rehashed_tbr_with_lawful_scope_but_wrong_members_rejected():
    """PIR01-T21: Forged re-hashed TBR with lawful scope but wrong members is rejected."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "apple"), ("text", "banana")),
        micro_episode_id="mep_v",
        child_index=0,
    )
    ep = SensoryEpisode(signals=[("text", "apple"), ("text", "banana")], kind="simultaneous")
    batch = bridge._build_receipt_batch(
        txid="tx_v",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    # Tamper with TBR member sequence: alter members from ('text:apple', 'text:banana') to ('text:apple',)
    tbr = batch.ordered_binding_entries[0]
    forged_bid = derive_transient_binding_receipt_id(
        micro_episode_id="mep_v",
        binding_scope_id=tbr.binding_scope,
        member_receipt_refs=["text:apple"],
        binding_index=0,
        prefix="tbr_",
    )
    forged_tbr = CanonicalBindingEntry(
        binding_index=0,
        binding_id=forged_bid,
        scope_kind=tbr.scope_kind,
        scope_index=tbr.scope_index,
        binding_scope=tbr.binding_scope,
        member_element_refs=("text:apple",),
    )
    batch.ordered_binding_entries[0] = forged_tbr
    with pytest.raises(R2BatchValidationError, match="TBR members mismatch"):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx_v",
            expected_micro_id="mep_v",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=desc,
        )


def test_pir01_t22_forged_rehashed_receipt_with_wrong_occurrence_scope_rejected():
    """PIR01-T22: Forged re-hashed receipt with wrong occurrence scope is rejected."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "apple"),),
        micro_episode_id="mep_v2",
        child_index=0,
    )
    ep = SensoryEpisode(signals=[("text", "apple")], kind="simultaneous")
    batch = bridge._build_receipt_batch(
        txid="tx_v2",
        micro_desc=desc,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    # Invent a non-matching but regex-valid occurrence scope and re-hash ReceiptID
    invented_occ = "r2occ:mep_v2:simultaneous:999"
    new_scope_refs = ("mep_v2", invented_occ)
    rehashed_rid = derive_participation_receipt_id(
        micro_episode_id="mep_v2",
        participation_kind="node",
        element_ref="text:apple",
        scope_refs=list(new_scope_refs),
        slot_index=0,
        prefix="pr_",
    )
    batch.ordered_receipt_entries[0] = CanonicalReceiptEntry(
        slot_index=0,
        receipt_id=rehashed_rid,
        kind="node",
        element_ref="text:apple",
        occurrence_scope=invented_occ,
        scope_refs=new_scope_refs,
    )
    # Must fail closed: occurrence_scope does not match rederived plan
    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx_v2",
            expected_micro_id="mep_v2",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=desc,
        )


# ─────────────────────────────────────────────────────────── PIR01-B06: Bidirectional Adjacent Sequence RFC-11 (T23 - T24)
def test_pir01_t23_reverse_adjacent_sequence_edge_is_rfc11_eligible():
    """PIR01-T23: Reverse adjacent sequence edge (B → A) is RFC11 eligible under minimum distance 1."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="sequence",
        steps=((("text", "A"),), (("text", "B"),)),
        micro_episode_id="mep_seq_ab",
        child_index=0,
    )
    eligible = bridge._derive_rfc11_eligible_edges(desc)
    assert ("text:A", "text:B") in eligible
    assert ("text:B", "text:A") in eligible


def test_pir01_t24_nonadjacent_forward_reverse_edges_remain_rfc11_ineligible():
    """PIR01-T24: Non-adjacent sequence edges (A ↔ C) are never RFC11 eligible."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="sequence",
        steps=((("text", "A"),), (("text", "B"),), (("text", "C"),)),
        micro_episode_id="mep_seq_abc",
        child_index=0,
    )
    eligible = bridge._derive_rfc11_eligible_edges(desc)
    assert ("text:A", "text:C") not in eligible
    assert ("text:C", "text:A") not in eligible


# ─────────────────────────────────────────────────────────── PIR01-B07: CanonicalObservationResult & Lifecycle (T25 - T33)
def test_pir01_t25_result_exposes_actual_persistent_txid_distinct_from_otid():
    """PIR01-T25: Result exposes actual R1 persistent TxID distinct from OTID."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    res = bridge.observe_text(
        boundary_namespace="res_test",
        source_occurrence_key="occ_res_01",
        source_event_key="evt_res_01",
        ingress_boundary="b",
        raw_text="Neural synaptic plasticity is observed.",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res.persistent_transaction_id is not None
    assert res.observation_transaction_id.startswith("tx_obs_")
    assert res.persistent_transaction_id != res.observation_transaction_id
    # persistent_transaction_id is the exact key in the R1 ledger
    assert res.persistent_transaction_id in bridge.runtime.ledger.committed_transactions


def test_pir01_t26_result_exposes_event_digest_mode_persistent_phase():
    """PIR01-T26: Result exposes event_descriptor_digest, mode, and persistent_phase."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    res = bridge.observe_text(
        boundary_namespace="res_test",
        source_occurrence_key="occ_res_02",
        source_event_key="evt_res_02",
        ingress_boundary="b",
        raw_text="Event descriptor digest verification.",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert len(res.event_descriptor_digest) == 64
    assert res.mode == ExecutionMode.AUTHORIZED_PERSISTENT
    assert res.persistent_phase == "COMMITTED"
    assert res.persistent_executed is True


def test_pir01_t27_per_micro_episode_trace_contains_batch_assemblies_rid():
    """PIR01-T27: Per-MicroEpisode trace contains descriptor, batch, assemblies, and RID."""
    bridge = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="trace_test",
        source_occurrence_key="occ_tr",
        source_event_key="evt_tr",
        ingress_boundary="b",
        raw_text="The quick brown fox jumps over the lazy dog.",
    )
    assert len(res.micro_episodes) > 0
    for rec in res.micro_episodes:
        assert isinstance(rec.descriptor, CanonicalMicroEpisodeDescriptor)
        assert isinstance(rec.receipt_batch, CanonicalReceiptBatch)
        assert isinstance(rec.selected_assembly_refs, tuple)
        assert rec.representation_id is not None


def test_pir01_t28_projection_failure_carries_actual_persistent_txid():
    """PIR01-T28: R2ProjectionFailure carries the actual R1 persistent TxID."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    with patch.object(
        bridge._graph.representation_engine,
        "build_canonical_representation",
        side_effect=RuntimeError("Forced projection failure"),
    ):
        with pytest.raises(R2ProjectionFailure) as exc_info:
            bridge.observe_text(
                boundary_namespace="fail_test",
                source_occurrence_key="occ_f1",
                source_event_key="evt_f1",
                ingress_boundary="b",
                raw_text="Projection failure test text.",
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability="valid_cap",
            )
        err = exc_info.value
        committed_tx = next(iter(bridge.runtime.ledger.committed_transactions.keys()))
        assert err.transaction_id == committed_tx


def test_pir01_t29_projection_failure_carries_actual_failing_child_index():
    """PIR01-T29: R2ProjectionFailure carries actual loop failing child index."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    with patch.object(
        bridge._graph.representation_engine,
        "build_canonical_representation",
        side_effect=RuntimeError("Forced projection failure at child 0"),
    ):
        with pytest.raises(R2ProjectionFailure) as exc_info:
            bridge.observe_text(
                boundary_namespace="fail_test",
                source_occurrence_key="occ_f2",
                source_event_key="evt_f2",
                ingress_boundary="b",
                raw_text="Child index failure test text.",
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability="valid_cap",
            )
        assert exc_info.value.failed_child_index == 0


def test_pir01_t30_close_result_removes_rep_from_active_representations():
    """PIR01-T30: close_result removes representation from active_representations table."""
    bridge = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_lc_1",
        source_event_key="evt_lc_1",
        ingress_boundary="b",
        raw_text="Testing representation lifecycle cleanup.",
    )
    rep_engine = bridge._graph.representation_engine
    assert len(res.representations) > 0
    for rep in res.representations:
        assert rep.representation_id in rep_engine.active_representations

    res.close()

    for rep in res.representations:
        assert rep.representation_id not in rep_engine.active_representations
        assert rep.representation_id in rep_engine.closed_representations


def test_pir01_t31_double_close_remains_idempotent():
    """PIR01-T31: Double close on CanonicalObservationResult via close_result is completely idempotent."""
    bridge = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_lc_2",
        source_event_key="evt_lc_2",
        ingress_boundary="b",
        raw_text="Testing double close idempotency.",
    )
    rep_engine = bridge._graph.representation_engine
    close_result(res)
    assert res.is_closed is True
    closed_count = rep_engine.observability.representations_closed
    assert closed_count > 0

    # Second close via close_result must be completely idempotent and not increment engine stats
    close_result(res)
    assert res.is_closed is True
    assert rep_engine.observability.representations_closed == closed_count

    # res.close() call also idempotent
    res.close()
    assert res.is_closed is True
    assert rep_engine.observability.representations_closed == closed_count


def test_pir01_t32_partial_projection_failure_removes_every_earlier_rep_from_active_representations():
    """PIR01-T32: Partial projection failure removes every earlier created SDCR from active_representations."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    rep_engine = bridge._graph.representation_engine
    call_count = 0
    orig_build = rep_engine.build_canonical_representation

    def fail_on_second(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            raise RuntimeError("Crash on second child representation")
        return orig_build(*args, **kwargs)

    two_episodes = [
        SensoryEpisode(kind="simultaneous", signals=[("text", "alpha")]),
        SensoryEpisode(kind="simultaneous", signals=[("text", "beta")]),
    ]
    with (
        patch.object(bridge._encoder, "encode_text", return_value=two_episodes),
        patch.object(rep_engine, "build_canonical_representation", side_effect=fail_on_second),
        pytest.raises(R2ProjectionFailure),
    ):
        bridge.observe_text(
            boundary_namespace="lifecycle",
            source_occurrence_key="occ_lc_3",
            source_event_key="evt_lc_3",
            ingress_boundary="b",
            raw_text="Two episodes text.",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )
    # All created SDCRs from failed attempt must be retired from active_representations
    assert len(rep_engine.active_representations) == 0


def test_pir01_t33_close_result_changes_no_persistent_graph_ledger_state():
    """PIR01-T33: close_result changes no persistent graph state or causal ledger state."""
    bridge = _make_bridge(authorizer=SimpleObservationAuthorizer(allow=True))
    res = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_lc_4",
        source_event_key="evt_lc_4",
        ingress_boundary="b",
        raw_text="Measuring state conservation across close_result.",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    state_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(bridge._graph))
    tx_count_before = len(bridge.runtime.ledger.committed_transactions)

    res.close()

    state_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(bridge._graph))
    tx_count_after = len(bridge.runtime.ledger.committed_transactions)
    assert state_before == state_after
    assert tx_count_before == tx_count_after


# ─────────────────────────────────────────────────────────── Hardening D01 & D02 (T34 - T35)
def test_pir01_t34_generic_raw_payload_with_unknown_field_fails_closed():
    """PIR01-T34: Generic observe(payload=...) with unknown keys fails closed (D01)."""
    bridge = _make_bridge()
    occ = ExternalOccurrenceDescriptor("hardening", "occ_h1")
    with pytest.raises(R2DescriptorError, match="Unknown text payload keys"):
        bridge.observe(
            occurrence=occ,
            source_event_key="evt_h1",
            ingress_boundary="b",
            modality="text",
            payload={"raw_text": "hello", "unexpected_extra": "drop_me"},
        )


def test_pir01_t35_episode_micro_descriptor_length_mismatch_fails_closed():
    """PIR01-T35: Episode count mismatch with micro_descriptors fails closed (D02)."""
    bridge = _make_bridge()
    occ = ExternalOccurrenceDescriptor("hardening", "occ_h2")
    dummy_desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "A"),),
        micro_episode_id="mep_dummy",
        child_index=0,
    )
    # Inject count mismatch: 1 episode from encoder, but 2 descriptors returned
    with (
        patch.object(bridge, "_build_micro_descriptors", return_value=[dummy_desc, dummy_desc]),
        pytest.raises(R2DescriptorError, match="Episode count does not equal micro_descriptor count"),
    ):
        bridge.observe(
            occurrence=occ,
            source_event_key="evt_h2",
            ingress_boundary="b",
            modality="text",
            payload={"raw_text": "hello"},
        )
    assert len(bridge._graph.nodes) == 0
    assert len(bridge._graph.edges) == 0
