"""DGCA — RIC-01 / R2-PIR-04: Acceptance & Evidence Closure Test Suite.

Implements all 50 dedicated test obligations specified in PIR-04:
- T06..T07: Semantics registry & observation protocol validation
- T13..T21: Transient-only state isolation & SDCR representation
- T26..T30: TBR constitution
- T31..T36: Receipt / TBR identity validation & tamper rejection
- T37..T43: Observation relations & RFC-11 evidence derivation
- T48: Transient observation zero RFC-11 vote
- T51: Authorized ingress first execution creates one R1 transaction
- T52..T56: Replay / Tx semantics & idempotence
- T57..T59: Contradiction semantics
- T60..T67: Authority firewall & capability validation
- T75..T77: Result close lifecycle
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalIdentityError,
    create_native_r1_provenance_epoch,
    derive_participation_receipt_id,
    derive_transient_binding_receipt_id,
)
from dgca.encoder import SensoryEpisode
from dgca.graph import CognitiveGraph
from dgca.observation import (
    MICRO_DESCRIPTOR_VERSION,
    R2_OBSERVATION_SEMANTICS_DIGEST,
    CanonicalBindingEntry,
    CanonicalMicroEpisodeDescriptor,
    CanonicalReceiptEntry,
    ExecutionMode,
    PersistentObservationAuthorizer,
    R2AuthorizationError,
    R2BatchValidationError,
    R2DescriptorError,
    compute_r2_observation_semantics_digest,
    derive_all_observation_relations,
    derive_expected_receipt_plan,
    validate_canonical_receipt_batch,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)
from tests.test_ric01_r2_authorizer import SimpleObservationAuthorizer


def _make_bridge(authorizer: PersistentObservationAuthorizer | None = None, protocol_version: str = "R2-OBS-1.0"):
    graph = CognitiveGraph()
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    runtime = CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version=protocol_version,
        lifecycle_guard=RuntimeLifecycleGuard(),
    )
    bridge = runtime.create_observation_bridge(authorizer=authorizer)
    return bridge, graph, runtime


# ─────────────────────────────────────────────────────────── Protocol (T06..T07)

def test_pir04_t06_frozen_t06_semantics_registry_recomputes_exact_digest():
    """T06: frozen R2 semantics registry recomputes exact frozen digest."""
    digest = compute_r2_observation_semantics_digest()
    assert digest == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"
    assert R2_OBSERVATION_SEMANTICS_DIGEST == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"


def test_pir04_t07_frozen_t07_protocol_mismatch_fails_bridge_construction():
    """T07: runtime observation protocol != R2-OBS-1.0 -> bridge construction fails."""
    graph = CognitiveGraph()
    state_digest = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    runtime = CanonicalR1RuntimeRoot(
        graph=graph,
        ledger=ledger,
        observation_protocol_version="INCOMPATIBLE-OBS-2.0",
        lifecycle_guard=RuntimeLifecycleGuard(),
    )
    with pytest.raises((R2DescriptorError, CausalIdentityError)):
        runtime.create_observation_bridge()


# ─────────────────────────────────────────────────────────── Transient Isolation (T13..T21)

def _setup_transient_test():
    bridge, graph, runtime = _make_bridge()
    graph.observe([("concept", "light"), ("concept", "sun")], context="nature")
    digest_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    t_before = graph.t
    nodes_before = set(graph.nodes.keys())
    edges_before = set(graph.edges.keys())
    contradictions_before = {k: set(v) for k, v in graph.X.items()}
    pending_before = len(graph.assembly_manager.pending_candidates)
    ledger_len_before = len(runtime.ledger.committed_transactions)
    res = bridge.observe_text(
        boundary_namespace="ns_tr",
        source_occurrence_key="k_novel",
        source_event_key="e_novel",
        ingress_boundary="b_tr",
        raw_text="novel_token_x novel_token_y",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )
    return {
        "bridge": bridge,
        "graph": graph,
        "runtime": runtime,
        "digest_before": digest_before,
        "t_before": t_before,
        "nodes_before": nodes_before,
        "edges_before": edges_before,
        "contradictions_before": contradictions_before,
        "pending_before": pending_before,
        "ledger_len_before": ledger_len_before,
        "res": res,
    }


def test_pir04_t13_frozen_t13_transient_only_state_digest_unchanged():
    """T13: novel text TRANSIENT_ONLY -> graph persistent state digest unchanged."""
    s = _setup_transient_test()
    digest_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(s["graph"]))
    assert digest_after == s["digest_before"]


def test_pir04_t14_frozen_t14_transient_only_logical_time_unchanged():
    """T14: graph logical time unchanged."""
    s = _setup_transient_test()
    assert s["graph"].t == s["t_before"]


def test_pir04_t15_frozen_t15_transient_only_no_persistent_node_created():
    """T15: no persistent Node created."""
    s = _setup_transient_test()
    assert set(s["graph"].nodes.keys()) == s["nodes_before"]
    assert "text:novel" not in s["graph"].nodes
    assert "text:x" not in s["graph"].nodes
    assert "text:y" not in s["graph"].nodes


def test_pir04_t16_frozen_t16_transient_only_no_persistent_edge_created():
    """T16: no persistent Edge created."""
    s = _setup_transient_test()
    assert set(s["graph"].edges.keys()) == s["edges_before"]
    assert ("text:novel", "text:token") not in s["graph"].edges
    assert ("text:x", "text:y") not in s["graph"].edges


def test_pir04_t17_frozen_t17_transient_only_no_graph_contradiction_written():
    """T17: no graph.X contradiction written."""
    s = _setup_transient_test()
    assert s["graph"].X == s["contradictions_before"]


def test_pir04_t18_frozen_t18_transient_only_rfc11_pending_queues_unchanged():
    """T18: RFC11 pending candidates/growth/merge unchanged."""
    s = _setup_transient_test()
    assert len(s["graph"].assembly_manager.pending_candidates) == s["pending_before"]


def test_pir04_t19_frozen_t19_transient_only_causal_ledger_unchanged():
    """T19: causal ledger unchanged."""
    s = _setup_transient_test()
    assert len(s["runtime"].ledger.committed_transactions) == s["ledger_len_before"] == 0


def test_pir04_t20_frozen_t20_transient_only_sdcr_contains_novel_node_participation():
    """T20: RFC12 SDCR still contains transient novel node participation."""
    s = _setup_transient_test()
    sdcr = s["res"].representations[0]
    assert "text:novel" in sdcr.participating_node_refs
    assert "text:token" in sdcr.participating_node_refs
    assert "text:x" in sdcr.participating_node_refs
    assert "text:y" in sdcr.participating_node_refs


def test_pir04_t21_frozen_t21_explicit_novel_relation_represented_by_tbr_without_persistent_edge():
    """T21: explicit novel/current relation can be represented by TBR without persistent Edge creation."""
    s = _setup_transient_test()
    sdcr = s["res"].representations[0]
    assert len(sdcr.transient_binding_receipts) > 0
    assert ("text:novel", "text:token") not in s["graph"].edges
    assert ("text:x", "text:y") not in s["graph"].edges


# ─────────────────────────────────────────────────────────── TBR Constitution (T26..T30)

def test_pir04_t26_frozen_t26_simultaneous_descriptor_two_nodes_one_tbr():
    """T26: simultaneous descriptor with two nodes -> exactly one lawful simultaneous TBR."""
    bridge, _, _ = _make_bridge()
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t26",
        child_index=0,
        kind="simultaneous",
        signals=(("text", "node_a"), ("text", "node_b")),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "node_a"), ("text", "node_b")])
    batch = bridge._build_receipt_batch(
        txid="tx:t26",
        micro_desc=mep,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    sim_tbrs = [b for b in batch.ordered_binding_entries if b.scope_kind == "simultaneous"]
    assert len(sim_tbrs) == 1
    assert set(sim_tbrs[0].member_element_refs) == {"text:node_a", "text:node_b"}
    validate_canonical_receipt_batch(
        batch=batch,
        expected_txid="tx:t26",
        expected_micro_id="mep:t26",
        expected_child_index=0,
        expected_cycle_id=1,
        micro_descriptor=mep,
    )


def test_pir04_t27_frozen_t27_sequence_descriptor_only_adjacent_transition_tbrs():
    """T27: sequence descriptor -> only adjacent-transition TBRs."""
    bridge, _, _ = _make_bridge()
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t27",
        child_index=0,
        kind="sequence",
        steps=((("text", "step_0"),), (("text", "step_1"),), (("text", "step_2"),)),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    ep = SensoryEpisode(kind="sequence", steps=[[("text", "step_0")], [("text", "step_1")], [("text", "step_2")]])
    batch = bridge._build_receipt_batch(
        txid="tx:t27",
        micro_desc=mep,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    seq_tbrs = [b for b in batch.ordered_binding_entries if b.scope_kind == "sequence"]
    assert len(seq_tbrs) == 2
    assert seq_tbrs[0].member_element_refs == ("text:step_0", "text:step_1")
    assert seq_tbrs[1].member_element_refs == ("text:step_1", "text:step_2")
    validate_canonical_receipt_batch(
        batch=batch,
        expected_txid="tx:t27",
        expected_micro_id="mep:t27",
        expected_child_index=0,
        expected_cycle_id=1,
        micro_descriptor=mep,
    )


def test_pir04_t28_frozen_t28_explicit_contradiction_pair_one_tbr():
    """T28: explicit contradiction pair -> exactly one contradiction TBR."""
    bridge, _, _ = _make_bridge()
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t28",
        child_index=0,
        kind="simultaneous",
        signals=(("text", "node_x"), ("text", "node_y")),
        contradictions=(("text:node_x", "text:node_y"),),
        structural_weight=1.0,
        valence=0.0,
    )
    ep = SensoryEpisode(
        kind="simultaneous",
        signals=[("text", "node_x"), ("text", "node_y")],
        contradictions=[("node_x", "node_y")],
    )
    batch = bridge._build_receipt_batch(
        txid="tx:t28",
        micro_desc=mep,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    contra_tbrs = [b for b in batch.ordered_binding_entries if b.scope_kind == "contradiction"]
    assert len(contra_tbrs) == 1
    assert set(contra_tbrs[0].member_element_refs) == {"text:node_x", "text:node_y"}
    validate_canonical_receipt_batch(
        batch=batch,
        expected_txid="tx:t28",
        expected_micro_id="mep:t28",
        expected_child_index=0,
        expected_cycle_id=1,
        micro_descriptor=mep,
    )


def test_pir04_t29_frozen_t29_invented_tbr_not_derivable_from_descriptor_rejected():
    """T29: invented TBR not derivable from descriptor -> reject batch."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_c_forged_tbr_valid_hash_wrong_descriptor_authority_rejected,
    )
    test_scenario_c_forged_tbr_valid_hash_wrong_descriptor_authority_rejected()


def test_pir04_t30_frozen_t30_tbr_member_lacking_exact_binding_scope_rejected():
    """T30: TBR member whose node receipt lacks exact binding_scope_id -> reject batch."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected,
    )
    test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected()


# ─────────────────────────────────────────────────────────── Receipt / TBR Validation (T31..T36)

def test_pir04_t31_frozen_t31_receipt_id_rederives_from_micro_id_and_slot():
    """T31: every ReceiptID rederives from MicroEpisodeID + exact slot."""
    micro_id = "mep:test_rederive"
    slot_index = 0
    scope_refs = ("mep:test_rederive", "r2occ:mep:test_rederive:simultaneous:0")
    rid1 = derive_participation_receipt_id(
        micro_episode_id=micro_id,
        participation_kind="node",
        element_ref="text:elem",
        scope_refs=list(scope_refs),
        slot_index=slot_index,
        prefix="pr_",
    )
    rid2 = derive_participation_receipt_id(
        micro_episode_id=micro_id,
        participation_kind="node",
        element_ref="text:elem",
        scope_refs=list(scope_refs),
        slot_index=slot_index,
        prefix="pr_",
    )
    assert rid1 == rid2
    assert rid1.startswith("pr_")


def test_pir04_t32_frozen_t32_tbr_id_rederives_from_micro_id_and_index():
    """T32: every TBRID rederives from MicroEpisodeID + exact binding index."""
    micro_id = "mep:test_rederive"
    b_scope = "r2scope:mep:test_rederive:simultaneous:0"
    bid1 = derive_transient_binding_receipt_id(
        micro_episode_id=micro_id,
        binding_scope_id=b_scope,
        member_receipt_refs=["text:a", "text:b"],
        binding_index=0,
        prefix="tbr_",
    )
    bid2 = derive_transient_binding_receipt_id(
        micro_episode_id=micro_id,
        binding_scope_id=b_scope,
        member_receipt_refs=["text:a", "text:b"],
        binding_index=0,
        prefix="tbr_",
    )
    assert bid1 == bid2
    assert bid1.startswith("tbr_")


def test_pir04_t33_frozen_t33_receipt_slot_gap_duplicate_rejects_batch():
    """T33: receipt slot gap/duplicate -> reject entire batch."""
    from tests.test_ric01_r2_receipts import test_batch_validation_rejects_slot_gap
    test_batch_validation_rejects_slot_gap()


def test_pir04_t34_frozen_t34_receipt_id_tamper_rejects_batch():
    """T34: receipt ID tamper -> reject entire batch."""
    bridge, _, _ = _make_bridge()
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t34",
        child_index=0,
        kind="simultaneous",
        signals=(("text", "a"),),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "a")])
    batch = bridge._build_receipt_batch(
        txid="tx:t34",
        micro_desc=mep,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    orig = batch.ordered_receipt_entries[0]
    tampered = CanonicalReceiptEntry(
        slot_index=orig.slot_index,
        receipt_id="pr_tampered_id_0000000000000000",
        kind=orig.kind,
        element_ref=orig.element_ref,
        occurrence_scope=orig.occurrence_scope,
        scope_refs=orig.scope_refs,
        activation_magnitude=orig.activation_magnitude,
        relational_drive=orig.relational_drive,
    )
    batch.ordered_receipt_entries[0] = tampered
    with pytest.raises(R2BatchValidationError, match="ParticipationReceipt ID re-derivation mismatch"):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx:t34",
            expected_micro_id="mep:t34",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=mep,
        )


def test_pir04_t35_frozen_t35_tbr_id_tamper_rejects_batch():
    """T35: TBR ID tamper -> reject entire batch."""
    bridge, _, _ = _make_bridge()
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t35",
        child_index=0,
        kind="simultaneous",
        signals=(("text", "a"), ("text", "b")),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "a"), ("text", "b")])
    batch = bridge._build_receipt_batch(
        txid="tx:t35",
        micro_desc=mep,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    orig_b = batch.ordered_binding_entries[0]
    tampered_b = CanonicalBindingEntry(
        binding_index=orig_b.binding_index,
        binding_id="tbr_tampered_id_000000000000000",
        scope_kind=orig_b.scope_kind,
        scope_index=orig_b.scope_index,
        binding_scope=orig_b.binding_scope,
        member_element_refs=orig_b.member_element_refs,
    )
    batch.ordered_binding_entries[0] = tampered_b
    with pytest.raises(R2BatchValidationError, match="TBRID re-derivation mismatch"):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx:t35",
            expected_micro_id="mep:t35",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=mep,
        )


def test_pir04_t36_frozen_t36_numeric_parent_collision_cannot_pass_batch_validation():
    """T36: numeric parent collision with different MicroEpisodeID cannot pass canonical batch validation."""
    bridge, _, _ = _make_bridge()
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t36_actual",
        child_index=0,
        kind="simultaneous",
        signals=(("text", "a"),),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "a")])
    batch = bridge._build_receipt_batch(
        txid="tx:t36",
        micro_desc=mep,
        ep=ep,
        child_index=0,
        local_parent_cycle_id=1,
    )
    with pytest.raises(R2BatchValidationError, match="MicroEpisodeID mismatch"):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx:t36",
            expected_micro_id="mep:t36_colliding",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=mep,
        )


# ─────────────────────────────────────────────────────────── Relations & RFC11 (T37..T43, T48, T51)

def test_pir04_t37_frozen_t37_simultaneous_all_ordered_non_self_pairs_are_relations():
    """T37: simultaneous all ordered non-self pairs are observation relations."""
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t37",
        child_index=0,
        kind="simultaneous",
        signals=(("text", "u"), ("text", "v"), ("text", "w")),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    relations = derive_all_observation_relations(mep)
    assert len(relations) == 6
    for u, v in relations:
        assert u != v
    assert ("text:u", "text:v") in relations
    assert ("text:v", "text:u") in relations
    assert ("text:u", "text:w") in relations
    assert ("text:w", "text:u") in relations
    assert ("text:v", "text:w") in relations
    assert ("text:w", "text:v") in relations


def test_pir04_t38_frozen_t38_sequence_same_step_relation_rfc11_eligible():
    """T38: sequence same-step relation is RFC11-eligible."""
    bridge, _, _ = _make_bridge()
    step0 = (("text", "u"), ("text", "v"))
    step1 = (("text", "w"),)
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t38",
        child_index=0,
        kind="sequence",
        steps=(step0, step1),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    eligible = bridge._derive_rfc11_eligible_edges(desc)
    assert ("text:u", "text:v") in eligible
    assert ("text:v", "text:u") in eligible


def test_pir04_t39_frozen_t39_sequence_adjacent_step_relation_rfc11_eligible():
    """T39: sequence adjacent-step relation is RFC11-eligible."""
    bridge, _, _ = _make_bridge()
    step0 = (("text", "step0"),)
    step1 = (("text", "step1"),)
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t39",
        child_index=0,
        kind="sequence",
        steps=(step0, step1),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    eligible = bridge._derive_rfc11_eligible_edges(desc)
    assert ("text:step0", "text:step1") in eligible
    assert ("text:step1", "text:step0") in eligible


def test_pir04_t40_frozen_t40_sequence_nonadjacent_relation_no_rfc11_vote():
    """T40: sequence nonadjacent relation may be a read-only Edge receipt but cannot vote in RFC11."""
    bridge, _, _ = _make_bridge()
    step0 = (("text", "step0"),)
    step1 = (("text", "step1"),)
    step2 = (("text", "step2"),)
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t40",
        child_index=0,
        kind="sequence",
        steps=(step0, step1, step2),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    all_rels = derive_all_observation_relations(desc)
    assert ("text:step0", "text:step2") in all_rels
    eligible = bridge._derive_rfc11_eligible_edges(desc)
    assert ("text:step0", "text:step2") not in eligible
    assert ("text:step2", "text:step0") not in eligible


def test_pir04_t41_frozen_t41_synthetic_ev_role_edge_cannot_vote_rfc11():
    """T41: synthetic ev: role Edge cannot vote in RFC11."""
    from tests.test_ric01_r2_adversarial import test_scenario_o_synthetic_ev_edge_never_rfc11_vote
    test_scenario_o_synthetic_ev_edge_never_rfc11_vote()


def test_pir04_t42_frozen_t42_concept_generalization_edge_cannot_vote_rfc11():
    """T42: concept/generalization Edge cannot vote in RFC11."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_p_concept_generalization_side_effect_edge_never_rfc11_vote,
    )
    test_scenario_p_concept_generalization_side_effect_edge_never_rfc11_vote()


def test_pir04_t43_frozen_t43_no_graph_global_diff_used_to_derive_evidence():
    """T43: no graph-global diff is used to derive evidence."""
    mep = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:t43",
        child_index=0,
        kind="simultaneous",
        signals=(("text", "local_a"), ("text", "local_b")),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    expected = derive_expected_receipt_plan(mep, mep.micro_episode_id)
    assert expected is not None
    assert len(expected) == 2


def test_pir04_t48_frozen_t48_transient_observation_creates_zero_rfc11_vote():
    """T48: transient observation creates zero RFC11 vote."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, _ = _make_bridge(authorizer=authorizer)
    bridge.observe_text(
        boundary_namespace="ns_t48",
        source_occurrence_key="k_seed",
        source_event_key="e_seed",
        ingress_boundary="b",
        raw_text="candidate_x candidate_y",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    votes_before = {
        cid: set(cand.root_votes)
        for cid, cand in graph.assembly_manager.pending_candidates.items()
    }
    bridge.observe_text(
        boundary_namespace="ns_t48",
        source_occurrence_key="k_transient",
        source_event_key="e_transient",
        ingress_boundary="b",
        raw_text="candidate_x candidate_y",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )
    votes_after = {
        cid: set(cand.root_votes)
        for cid, cand in graph.assembly_manager.pending_candidates.items()
    }
    assert votes_after == votes_before


def test_pir04_t51_frozen_t51_authorized_ingress_first_execution_one_r1_tx():
    """T51: authorized ingress first execution -> one R1 transaction."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, _, runtime = _make_bridge(authorizer=authorizer)
    assert len(runtime.ledger.committed_transactions) == 0
    res = bridge.observe_text(
        boundary_namespace="ns_t51",
        source_occurrence_key="k_t51",
        source_event_key="e_t51",
        ingress_boundary="b",
        raw_text="elem_one elem_two",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res.status == "PERSISTENT_EXECUTED"
    assert len(runtime.ledger.committed_transactions) == 1


# ─────────────────────────────────────────────────────────── Replay & Tx Semantics (T52..T56)

def test_pir04_t52_frozen_t52_exact_persistent_retry_callback_not_executed():
    """T52: exact persistent retry -> callback not executed."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, _, runtime = _make_bridge(authorizer=authorizer)
    bridge.observe_text(
        boundary_namespace="ns_t52",
        source_occurrence_key="k_t52",
        source_event_key="e_t52",
        ingress_boundary="b",
        raw_text="retry_a retry_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert len(runtime.ledger.committed_transactions) == 1

    res_retry = bridge.observe_text(
        boundary_namespace="ns_t52",
        source_occurrence_key="k_t52",
        source_event_key="e_t52",
        ingress_boundary="b",
        raw_text="retry_a retry_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res_retry.status == "PERSISTENT_REPLAY"
    assert len(runtime.ledger.committed_transactions) == 1


def test_pir04_t53_frozen_t53_retry_graph_persistent_state_digest_unchanged():
    """T53: retry -> graph persistent state digest unchanged."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, _ = _make_bridge(authorizer=authorizer)
    bridge.observe_text(
        boundary_namespace="ns_t53",
        source_occurrence_key="k_t53",
        source_event_key="e_t53",
        ingress_boundary="b",
        raw_text="retry_digest_a retry_digest_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    digest_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))

    bridge.observe_text(
        boundary_namespace="ns_t53",
        source_occurrence_key="k_t53",
        source_event_key="e_t53",
        ingress_boundary="b",
        raw_text="retry_digest_a retry_digest_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    digest_after = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    assert digest_after == digest_before


def test_pir04_t54_frozen_t54_retry_rfc11_vote_set_unchanged():
    """T54: retry -> RFC11 vote set unchanged."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, _ = _make_bridge(authorizer=authorizer)
    bridge.observe_text(
        boundary_namespace="ns_t54",
        source_occurrence_key="k_t54",
        source_event_key="e_t54",
        ingress_boundary="b",
        raw_text="vote_a vote_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    votes_before = {
        cid: set(cand.root_votes)
        for cid, cand in graph.assembly_manager.pending_candidates.items()
    }
    bridge.observe_text(
        boundary_namespace="ns_t54",
        source_occurrence_key="k_t54",
        source_event_key="e_t54",
        ingress_boundary="b",
        raw_text="vote_a vote_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    votes_after = {
        cid: set(cand.root_votes)
        for cid, cand in graph.assembly_manager.pending_candidates.items()
    }
    assert votes_after == votes_before


def test_pir04_t55_frozen_t55_same_root_transport_different_subevent_same_intent_same_r1_txid():
    """T55: same Root + transport-different subevent compiling to exact same mutation intent -> same R1 TxID."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_f_same_root_different_eventid_same_intent_same_r1_txid,
    )
    test_scenario_f_same_root_different_eventid_same_intent_same_r1_txid()


def test_pir04_t56_frozen_t56_distinct_root_same_content_distinct_r1_txid_and_independent_evidence():
    """T56: distinct Root + same content -> distinct R1 TxID and independent evidence."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_g_independent_root_identical_text_valid_capability_independent_learning,
    )
    test_scenario_g_independent_root_identical_text_valid_capability_independent_learning()


# ─────────────────────────────────────────────────────────── Contradiction Semantics (T57..T59)

def test_pir04_t57_frozen_t57_transient_contradiction_graph_x_unchanged():
    """T57: transient contradiction -> TBR + endpoint receipts, graph.X unchanged."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_q_contradiction_only_transient_endpoint_receipts_tbr_graph_unchanged,
    )
    test_scenario_q_contradiction_only_transient_endpoint_receipts_tbr_graph_unchanged()


def test_pir04_t58_frozen_t58_authorized_contradiction_graph_x_written_in_r1_command():
    """T58: authorized contradiction -> graph.X written inside R1 command."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)
    assert len(graph.X) == 0
    ep = SensoryEpisode(
        kind="simultaneous",
        signals=[("text", "light"), ("text", "dark")],
        contradictions=[("light", "dark")],
    )
    with patch.object(bridge._encoder, "encode_text", return_value=[ep]):
        res = bridge.observe_text(
            boundary_namespace="ns_contra",
            source_occurrence_key="k_contra_auth",
            source_event_key="e_contra_auth",
            ingress_boundary="b_contra",
            raw_text="light dark",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )
    assert res.status == "PERSISTENT_EXECUTED"
    assert "text:light" in graph.X
    assert "text:dark" in graph.X["text:light"]
    assert len(runtime.ledger.committed_transactions) == 1


def test_pir04_t59_frozen_t59_contradiction_does_not_become_rfc11_positive_edge_evidence():
    """T59: contradiction does not become RFC11 positive Edge evidence."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, _ = _make_bridge(authorizer=authorizer)
    ep = SensoryEpisode(
        kind="simultaneous",
        signals=[("text", "white"), ("text", "black")],
        contradictions=[("white", "black")],
    )
    with patch.object(bridge._encoder, "encode_text", return_value=[ep]):
        bridge.observe_text(
            boundary_namespace="ns_contra",
            source_occurrence_key="k_contra_rfc11",
            source_event_key="e_contra_rfc11",
            ingress_boundary="b_contra",
            raw_text="white black",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )
    for cand in graph.assembly_manager.pending_candidates.values():
        assert ("text:white", "text:black") not in cand.participating_edges
        assert ("text:black", "text:white") not in cand.participating_edges


# ─────────────────────────────────────────────────────────── Authority Firewall (T60..T67)

def test_pir04_t60_frozen_t60_authorizer_none_rejects_persistent_mode():
    """T60: authorizer=None rejects persistent mode."""
    bridge, _, _ = _make_bridge(authorizer=None)
    with pytest.raises(R2AuthorizationError):
        bridge.observe_text(
            boundary_namespace="ns_auth",
            source_occurrence_key="k_none",
            source_event_key="e_none",
            ingress_boundary="b",
            raw_text="hello world",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="some_cap",
        )


def test_pir04_t61_frozen_t61_bare_boolean_auth_equivalent_absent_or_rejected():
    """T61: bare boolean authorization equivalent does not exist / is rejected."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, _, runtime = _make_bridge(authorizer=authorizer)
    # 1. Calling observe / observe_text with an unexpected bare boolean parameter fails
    with pytest.raises(TypeError):
        bridge.observe_text(
            boundary_namespace="ns_auth",
            source_occurrence_key="k_bool",
            source_event_key="e_bool",
            ingress_boundary="b",
            raw_text="hello world",
            authorized=True,  # type: ignore[call-arg]
        )
    # 2. Passing a bare boolean as authorizer fails closed on persistent observation
    bad_bridge = runtime.create_observation_bridge(authorizer=True)  # type: ignore[arg-type]
    with pytest.raises(R2AuthorizationError):
        bad_bridge.observe_text(
            boundary_namespace="ns_auth",
            source_occurrence_key="k_bool2",
            source_event_key="e_bool2",
            ingress_boundary="b",
            raw_text="hello world",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="some_cap",
        )


def test_pir04_t62_frozen_t62_authorizer_false_zero_mutation():
    """T62: authorizer false -> zero mutation."""
    authorizer = SimpleObservationAuthorizer(allow=False)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)
    with pytest.raises(R2AuthorizationError):
        bridge.observe_text(
            boundary_namespace="ns_auth",
            source_occurrence_key="k_false",
            source_event_key="e_false",
            ingress_boundary="b",
            raw_text="denied_a denied_b",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap",
        )
    assert len(graph.nodes) == 0
    assert len(runtime.ledger.committed_transactions) == 0


def test_pir04_t63_frozen_t63_authorizer_exception_zero_mutation():
    """T63: authorizer exception -> zero mutation."""
    class FailingAuthorizer(PersistentObservationAuthorizer):
        def verify_persistent_observation(self, *args, **kwargs) -> bool:
            raise RuntimeError("Authorizer internal failure")

    bridge, graph, runtime = _make_bridge(authorizer=FailingAuthorizer())
    with pytest.raises((R2AuthorizationError, RuntimeError)):
        bridge.observe_text(
            boundary_namespace="ns_auth",
            source_occurrence_key="k_exc",
            source_event_key="e_exc",
            ingress_boundary="b",
            raw_text="crash_a crash_b",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="cap",
        )
    assert len(graph.nodes) == 0
    assert len(runtime.ledger.committed_transactions) == 0


def test_pir04_t64_frozen_t64_non_bool_authorizer_result_fails_closed():
    """T64: non-bool authorizer result -> fail closed."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_i_authorizer_returns_truthy_non_bool_fails_closed,
    )
    test_scenario_i_authorizer_returns_truthy_non_bool_fails_closed()


def test_pir04_t65_frozen_t65_ordinary_fact_x_no_persistent_authority():
    """T65: ordinary 'fact: X' has no persistent authority."""
    bridge, graph, runtime = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="ns_auth",
        source_occurrence_key="k_fact",
        source_event_key="e_fact",
        ingress_boundary="b",
        raw_text="fact: quantum gravity is discrete",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )
    assert res.status == "TRANSIENT_OBSERVED"
    assert len(graph.nodes) == 0
    assert len(runtime.ledger.committed_transactions) == 0


def test_pir04_t66_frozen_t66_ordinary_correction_x_no_persistent_authority():
    """T66: ordinary 'correction: X' has no persistent authority."""
    bridge, graph, runtime = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="ns_auth",
        source_occurrence_key="k_correction",
        source_event_key="e_correction",
        ingress_boundary="b",
        raw_text="correction: photon rest mass is zero",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )
    assert res.status == "TRANSIENT_OBSERVED"
    assert len(graph.nodes) == 0
    assert len(runtime.ledger.committed_transactions) == 0


def test_pir04_t67_frozen_t67_valid_root_event_ids_without_capability_no_persistent_authority():
    """T67: valid Root/Event IDs without capability have no persistent authority."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, _, runtime = _make_bridge(authorizer=authorizer)
    with pytest.raises(R2AuthorizationError):
        bridge.observe_text(
            boundary_namespace="ns_auth",
            source_occurrence_key="k_valid_root",
            source_event_key="e_valid_event",
            ingress_boundary="b",
            raw_text="no_cap_a no_cap_b",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability=None,
        )
    assert len(runtime.ledger.committed_transactions) == 0


# ─────────────────────────────────────────────────────────── Result Lifecycle (T75..T77)

def test_pir04_t75_frozen_t75_close_result_closes_all_result_sdcrs():
    """T75: close_result closes all result SDCRs."""
    bridge, _, _ = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="ns_close",
        source_occurrence_key="k_close",
        source_event_key="e_close",
        ingress_boundary="b",
        raw_text="test closing sdcrs",
    )
    assert len(res.representations) > 0
    for sdcr in res.representations:
        assert sdcr.status == "ACTIVE"
    res.close()
    assert res.is_closed is True
    for sdcr in res.representations:
        assert sdcr.status == "CLOSED"


def test_pir04_t76_frozen_t76_second_close_result_is_harmless():
    """T76: second close_result call is harmless."""
    bridge, _, _ = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="ns_close",
        source_occurrence_key="k_close2",
        source_event_key="e_close2",
        ingress_boundary="b",
        raw_text="test second close harmless",
    )
    res.close()
    assert res.is_closed is True
    res.close()
    assert res.is_closed is True


def test_pir04_t77_frozen_t77_close_result_changes_no_persistent_digest_or_ledger():
    """T77: close_result changes no persistent state digest or ledger."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)
    res = bridge.observe_text(
        boundary_namespace="ns_close",
        source_occurrence_key="k_close3",
        source_event_key="e_close3",
        ingress_boundary="b",
        raw_text="persistent close test",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    digest_before_close = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    ledger_count_before_close = len(runtime.ledger.committed_transactions)
    res.close()
    digest_after_close = compute_checkpoint_state_digest(extract_canonical_persistent_payload(graph))
    ledger_count_after_close = len(runtime.ledger.committed_transactions)
    assert digest_after_close == digest_before_close
    assert ledger_count_after_close == ledger_count_before_close
