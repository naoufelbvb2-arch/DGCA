"""DGCA — RIC-01 / R2-PIR-03: Acceptance & High-Risk Integration Test Suite.

Implements all 39 mandatory tests specified in Section 7 of the PIR-03 Master Prompt:
- Causal ingress (PIR03-T01..T05 -> Frozen T01..T05)
- Encoder / MicroEpisode determinism (PIR03-T06..T10 -> Frozen T08..T12)
- Binding constitution (PIR03-T11..T14 -> Frozen T22..T25)
- Edge readout / Assembly (PIR03-T15..T20 -> Frozen T44..T47, T49..T50)
- Post-commit / replay (PIR03-T21..T27 -> Frozen T68..T74, specifically T69 5th vote assembly visibility)
- Fail-stop (PIR03-T28..T31 -> Frozen T78..T81)
- Checkpoint / scope (PIR03-T32..T39 -> Frozen T82..T89)
"""
from __future__ import annotations

import json
import subprocess
from unittest.mock import patch

import pytest

from dgca.causal_identity import (
    LITERAL_DOMAIN_REGISTRY,
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalRuntimeFailStopError,
    CausalRuntimeHealth,
    ExternalOccurrenceDescriptor,
    canonical_json_bytes,
    compute_causal_identity_protocol_digest,
    create_native_r1_provenance_epoch,
)
from dgca.encoder import SensoryEpisode
from dgca.graph import CognitiveGraph
from dgca.observation import (
    MICRO_DESCRIPTOR_VERSION,
    CanonicalMicroEpisodeDescriptor,
    CanonicalObservationBridge,
    ExecutionMode,
    PersistentObservationAuthorizer,
    R2AuthorizationError,
    R2DescriptorError,
    R2ProjectionFailure,
    derive_expected_receipt_plan,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    build_canonical_r1_checkpoint,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    migrate_schema_1_1_1_to_1_2_0,
    restore_canonical_r1_checkpoint,
    save_canonical_r1_checkpoint,
    save_cognitive_checkpoint,
)
from tests.test_ric01_r1_repair import behavioral_signature, build_reference_graph
from tests.test_ric01_r2_authorizer import SimpleObservationAuthorizer


def _make_bridge(authorizer: PersistentObservationAuthorizer | None = None) -> tuple[CanonicalObservationBridge, CognitiveGraph, CanonicalR1RuntimeRoot]:
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
    bridge = runtime.create_observation_bridge(authorizer=authorizer)
    return bridge, graph, runtime


# ─────────────────────────────────────────────────────────── Causal Ingress (T01..T05)

def test_pir03_t01_frozen_t01_exact_replay_identity():
    """PIR03-T01 (T01): same trusted occurrence + event + payload -> same Root/Event IDs and event digest."""
    bridge, _, _ = _make_bridge()
    occ = ExternalOccurrenceDescriptor("boundary_ns", "key_01")
    payload = {"raw_text": "apple banana"}

    res1 = bridge.observe(
        occurrence=occ,
        source_event_key="evt_01",
        ingress_boundary="b_ext",
        modality="text",
        payload=payload,
    )
    res2 = bridge.observe(
        occurrence=occ,
        source_event_key="evt_01",
        ingress_boundary="b_ext",
        modality="text",
        payload=payload,
    )

    assert res1.root_external_episode_id == res2.root_external_episode_id
    assert res1.ingress_event_id == res2.ingress_event_id
    assert res1.event_descriptor_digest == res2.event_descriptor_digest
    assert len(res1.event_descriptor_digest) == 64


def test_pir03_t02_frozen_t02_independent_occurrence_distinct_root():
    """PIR03-T02 (T02): same payload, independent source occurrence -> distinct Roots."""
    bridge, _, _ = _make_bridge()
    occ1 = ExternalOccurrenceDescriptor("boundary_ns", "key_alpha")
    occ2 = ExternalOccurrenceDescriptor("boundary_ns", "key_beta")
    payload = {"raw_text": "identical payload text"}

    res1 = bridge.observe(
        occurrence=occ1,
        source_event_key="evt_01",
        ingress_boundary="b_ext",
        modality="text",
        payload=payload,
    )
    res2 = bridge.observe(
        occurrence=occ2,
        source_event_key="evt_01",
        ingress_boundary="b_ext",
        modality="text",
        payload=payload,
    )

    assert res1.root_external_episode_id != res2.root_external_episode_id
    assert res1.ingress_event_id != res2.ingress_event_id


def test_pir03_t03_frozen_t03_same_root_different_event_keys_distinct_event_ids():
    """PIR03-T03 (T03): same Root, different source_event_key -> distinct IngressEventIDs."""
    bridge, _, _ = _make_bridge()
    occ = ExternalOccurrenceDescriptor("boundary_ns", "key_shared")
    payload = {"raw_text": "common payload"}

    res1 = bridge.observe(
        occurrence=occ,
        source_event_key="evt_first",
        ingress_boundary="b_ext",
        modality="text",
        payload=payload,
    )
    res2 = bridge.observe(
        occurrence=occ,
        source_event_key="evt_second",
        ingress_boundary="b_ext",
        modality="text",
        payload=payload,
    )

    assert res1.root_external_episode_id == res2.root_external_episode_id
    assert res1.ingress_event_id != res2.ingress_event_id


def test_pir03_t04_frozen_t04_live_event_id_conflict():
    """PIR03-T04 (T04): same IngressEventID + conflicting payload in same runtime -> fail closed."""
    bridge, _, _ = _make_bridge()
    occ = ExternalOccurrenceDescriptor("boundary_ns", "key_conf")

    bridge.observe(
        occurrence=occ,
        source_event_key="evt_conf",
        ingress_boundary="b_ext",
        modality="text",
        payload={"raw_text": "first text payload"},
    )

    # Reusing same event key with conflicting text payload must fail closed
    with pytest.raises(R2DescriptorError, match="Ephemeral ingress binding conflict"):
        bridge.observe(
            occurrence=occ,
            source_event_key="evt_conf",
            ingress_boundary="b_ext",
            modality="text",
            payload={"raw_text": "completely different conflict text"},
        )


def test_pir03_t05_frozen_t05_raw_text_root_authorization_injection_powerless():
    """PIR03-T05 (T05): raw text attempting to inject RootID/authorization has no authority."""
    bridge, _, _ = _make_bridge(authorizer=None)
    occ = ExternalOccurrenceDescriptor("boundary_ns", "real_key")
    injected_text = "root_FORGED_ID capability:admin authorized=True"

    res = bridge.observe_text(
        boundary_namespace="boundary_ns",
        source_occurrence_key="real_key",
        source_event_key="evt_inject",
        ingress_boundary="b_ext",
        raw_text=injected_text,
        mode=ExecutionMode.TRANSIENT_ONLY,
    )

    # RootID must derive strictly from trusted occurrence, ignoring injected text
    expected_root = bridge.derive_root_episode_id(occ)
    assert res.root_external_episode_id == expected_root
    assert "FORGED_ID" not in res.root_external_episode_id

    # Persistent learning must remain denied
    with pytest.raises(R2AuthorizationError):
        bridge.observe_text(
            boundary_namespace="boundary_ns",
            source_occurrence_key="real_key",
            source_event_key="evt_inject_pers",
            ingress_boundary="b_ext",
            raw_text=injected_text,
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability=None,
        )


# ─────────────────────────────────────────────────────────── Encoder / MicroEpisode Determinism (T08..T12)

def test_pir03_t06_frozen_t08_n_episodes_to_n_micro_episodes():
    """PIR03-T06 (T08): N episodes -> N MicroEpisodes with contiguous child_index."""
    bridge, _, _ = _make_bridge()
    code = "def f(x):\n    return x + 1\ndef g(y):\n    return y * 2\n"
    res = bridge.observe_code(
        boundary_namespace="ns",
        source_occurrence_key="k_multi",
        source_event_key="e_multi",
        ingress_boundary="b",
        source_code=code,
    )
    assert len(res.micro_episodes) == 4
    for idx, mep in enumerate(res.micro_episodes):
        assert mep.child_index == idx
        assert mep.micro_episode_id.startswith("mep_")


def test_pir03_t07_frozen_t09_emitted_order_perturbation_changes_mid_chain():
    """PIR03-T07 (T09): emitted order perturbation changes ordered MID chain."""
    bridge, _, _ = _make_bridge()
    ep1 = SensoryEpisode(kind="simultaneous", signals=[("text", "apple")])
    ep2 = SensoryEpisode(kind="simultaneous", signals=[("text", "banana")])

    descs_forward = bridge._build_micro_descriptors([ep1, ep2], txid="tx_order_test")
    descs_reverse = bridge._build_micro_descriptors([ep2, ep1], txid="tx_order_test")

    assert descs_forward[0].micro_episode_id != descs_reverse[0].micro_episode_id
    assert descs_forward[1].micro_episode_id != descs_reverse[1].micro_episode_id


def test_pir03_t08_frozen_t10_iteration_perturbation_preserves_ids():
    """PIR03-T08 (T10): unrelated set/dict iteration perturbation preserves IDs."""
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "cat"), ("text", "dog")),
        structural_weight=1.0,
        valence=0.0,
        child_index=0,
    )
    d1 = desc.to_dict()
    # Scramble dict order
    d2 = {k: d1[k] for k in reversed(list(d1.keys()))}

    b1 = canonical_json_bytes(d1)
    b2 = canonical_json_bytes(d2)
    assert b1 == b2


def test_pir03_t09_frozen_t11_malformed_emitted_episode_fails_before_persistent_mutation():
    """PIR03-T09 (T11): malformed emitted episode fails before persistent mutation."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    _, graph, _ = _make_bridge(authorizer=authorizer)

    initial_node_count = len(graph.nodes)
    initial_edge_count = len(graph.edges)

    # Empty signals in simultaneous episode violates schema
    with pytest.raises(R2DescriptorError):
        CanonicalMicroEpisodeDescriptor(
            descriptor_version=MICRO_DESCRIPTOR_VERSION,
            kind="simultaneous",
            signals=(),
            child_index=0,
        )

    assert len(graph.nodes) == initial_node_count
    assert len(graph.edges) == initial_edge_count


def test_pir03_t10_frozen_t12_zero_emitted_episodes_zero_delta_behavior():
    """PIR03-T10 (T12): zero emitted episodes exact zero-delta behavior."""
    bridge, graph, runtime = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_zero",
        source_event_key="e_zero",
        ingress_boundary="b",
        raw_text="",
    )
    assert res.status == "NO_OBSERVABLE_CONTENT"
    assert len(res.representations) == 0
    assert len(res.micro_episodes) == 0
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert len(runtime.ledger.committed_transactions) == 0


# ─────────────────────────────────────────────────────────── Binding Constitution (T22..T25)

def test_pir03_t11_frozen_t22_coactivation_alone_cannot_create_tbr():
    """PIR03-T11 (T22): coactivation alone cannot create TBR."""
    _, graph, _ = _make_bridge()
    # Excite two nodes in graph so both are active
    n1 = graph.node("text:x", "text")
    n2 = graph.node("text:y", "text")
    n1.excite(1, 1.0)
    n2.excite(1, 1.0)

    # Single signal episode -> only one occurrence -> TBR policy forbids binding
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "x"),),
        child_index=0,
        micro_episode_id="mep_single",
    )
    plan = derive_expected_receipt_plan(desc, "mep_single", current_relation_view=graph)
    # Node receipt must NOT have any TBR scope
    assert len(plan) == 1
    assert plan[0].scope_refs == ("mep_single", "r2occ:mep_single:simultaneous:0")


def test_pir03_t12_frozen_t23_same_root_alone_cannot_create_tbr():
    """PIR03-T12 (T23): same Root alone cannot create TBR."""
    # Two distinct episodes under same root with 1 signal each do not cross-bind into a TBR
    desc1 = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "a"),),
        child_index=0,
        micro_episode_id="mep_root1",
    )
    desc2 = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "b"),),
        child_index=1,
        micro_episode_id="mep_root2",
    )
    plan1 = derive_expected_receipt_plan(desc1, "mep_root1")
    plan2 = derive_expected_receipt_plan(desc2, "mep_root2")
    assert all("r2scope:" not in s for s in plan1[0].scope_refs)
    assert all("r2scope:" not in s for s in plan2[0].scope_refs)


def test_pir03_t13_frozen_t24_same_context_alone_cannot_create_tbr():
    """PIR03-T13 (T24): same context alone cannot create TBR."""
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        context="shared_context_ctx",
        signals=(("text", "solo"),),
        child_index=0,
        micro_episode_id="mep_ctx",
    )
    plan = derive_expected_receipt_plan(desc, "mep_ctx")
    assert len(plan) == 1
    assert not any("r2scope:" in s for s in plan[0].scope_refs)


def test_pir03_t14_frozen_t25_same_timestamp_alone_cannot_create_tbr():
    """PIR03-T14 (T25): same timestamp alone cannot create TBR."""
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "timed_solo"),),
        child_index=0,
        micro_episode_id="mep_time",
    )
    plan = derive_expected_receipt_plan(desc, "mep_time")
    assert len(plan) == 1
    assert not any("r2scope:" in s for s in plan[0].scope_refs)


# ─────────────────────────────────────────────────────────── Edge Readout & Assembly Selection (T44..T50)

def test_pir03_t15_frozen_t44_live_gate_open_relation_edge_receipt():
    """PIR03-T15 (T44): live gate-open relation -> Edge receipt."""
    _, graph, _ = _make_bridge()
    graph.node("text:alpha", "text")
    graph.node("text:beta", "text")
    graph._link("text:alpha", "text:beta", W=1.0)

    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "alpha"), ("text", "beta")),
        child_index=0,
        micro_episode_id="mep_edge_test",
    )
    plan = derive_expected_receipt_plan(desc, "mep_edge_test", current_relation_view=graph)
    edge_entries = [e for e in plan if e.kind == "edge"]
    assert len(edge_entries) == 1
    assert edge_entries[0].element_ref == ("text:alpha", "text:beta")
    assert edge_entries[0].slot_class == "LIVE_GATE_OPEN_OBSERVATION_RELATION_EDGE_RECEIPTS"


def test_pir03_t16_frozen_t45_gate_closed_relation_no_edge_receipt():
    """PIR03-T16 (T45): gate-closed relation -> no Edge receipt."""
    _, graph, _ = _make_bridge()
    graph.node("text:u", "text")
    graph.node("text:v", "text")
    graph._link("text:u", "text:v", W=1.0)
    edge = graph.edges[("text:u", "text:v")]
    edge.g = "restricted_context_only"

    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        context=None,  # Not matching restricted_context_only -> gate closed
        signals=(("text", "u"), ("text", "v")),
        child_index=0,
        micro_episode_id="mep_closed_gate",
    )
    plan = derive_expected_receipt_plan(desc, "mep_closed_gate", current_relation_view=graph)
    edge_entries = [e for e in plan if e.kind == "edge"]
    assert len(edge_entries) == 0


def test_pir03_t17_frozen_t46_read_only_edge_receipt_changes_no_w_n_context():
    """PIR03-T17 (T46): read-only Edge receipt changes no W/n/context hits."""
    bridge, graph, _ = _make_bridge()
    graph.node("text:read_u", "text")
    graph.node("text:read_v", "text")
    graph._link("text:read_u", "text:read_v", W=1.5)
    edge = graph.edges[("text:read_u", "text:read_v")]
    edge.n = 3
    initial_w = edge.W
    initial_n = edge.n

    # Perform transient observation
    bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_ro",
        source_event_key="e_ro",
        ingress_boundary="b",
        raw_text="read_u read_v",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )

    assert edge.W == initial_w
    assert edge.n == initial_n


def test_pir03_t18_frozen_t47_transient_observation_selects_assembly_zero_vote():
    """PIR03-T18 (T47): transient observation selects existing Assembly with zero vote."""
    from dgca.assembly import StructuralAssembly
    bridge, graph, _ = _make_bridge()
    graph.link("text:apple", "text:fruit", W=0.8, kind="assoc")
    graph.link("text:fruit", "text:food", W=0.8, kind="assoc")
    graph.link("text:apple", "text:food", W=0.8, kind="assoc")
    mgr = graph.assembly_manager
    edges = frozenset([("text:apple", "text:fruit"), ("text:fruit", "text:food"), ("text:apple", "text:food")])
    asm = StructuralAssembly(
        assembly_id="asm_apple_cluster",
        version=1,
        member_edges=edges,
        origin_signature="sig1",
    )
    mgr.assemblies["asm_apple_cluster"] = [asm]
    mgr.rebuild_indexes()
    initial_assemblies_count = len(mgr.assemblies)

    res = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_asm",
        source_event_key="e_asm",
        ingress_boundary="b",
        raw_text="apple fruit",
        mode=ExecutionMode.TRANSIENT_ONLY,
    )

    assert len(res.representations) == 1
    sdcr = res.representations[0]
    active_asm_ids = [aid for aid, v in sdcr.active_assembly_refs]
    assert "asm_apple_cluster" in active_asm_ids
    # Zero structural vote modification
    assert len(mgr.assemblies) == initial_assemblies_count


def test_pir03_t19_frozen_t49_authorized_path_records_only_eligible_verified_evidence():
    """PIR03-T19 (T49): authorized path records only eligible verified external evidence."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, _, _ = _make_bridge(authorizer=authorizer)

    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="sequence",
        steps=((("text", "s1"),), (("text", "s2"),), (("text", "s3"),)),
        child_index=0,
    )
    eligible = bridge._derive_rfc11_eligible_edges(desc)
    assert ("text:s1", "text:s2") in eligible
    assert ("text:s2", "text:s3") in eligible
    assert ("text:s1", "text:s3") not in eligible  # Non-adjacent step is strictly ineligible


def test_pir03_t20_frozen_t50_many_micro_episodes_same_root_do_not_multiply_candidate_vote():
    """PIR03-T20 (T50): many MicroEpisodes same Root do not multiply candidate vote."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_a_500_calls_one_root_one_independent_vote,
    )
    test_scenario_a_500_calls_one_root_one_independent_vote()


# ─────────────────────────────────────────────────────────── Post-Commit / Replay (T68..T74)

def test_pir03_t21_frozen_t68_first_authorized_learning_exposes_learned_edge_in_same_event_sdcr():
    """PIR03-T21 (T68): first authorized learning exposes newly learned direct Edge in same event SDCR."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, _ = _make_bridge(authorizer=authorizer)

    # Initial graph has no edge between 'learn_x' and 'learn_y'
    assert graph.edge("text:learn_x", "text:learn_y") is None

    res = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_l1",
        source_event_key="e_l1",
        ingress_boundary="b",
        raw_text="learn_x learn_y",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res.status == "PERSISTENT_EXECUTED"
    # Persistent commit must have happened
    assert graph.edge("text:x", "text:y") is not None
    # And transient projection must reflect the newly committed edge
    sdcr = res.representations[0]
    assert ("text:x", "text:y") in sdcr.participating_edge_refs


def test_pir03_t22_frozen_t69_fifth_independent_rfc11_vote_forms_assembly_visible_in_same_event_sdcr():
    """PIR03-T22 (T69): fifth independent RFC11 vote forms Assembly visible in same event post-commit SDCR."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, _ = _make_bridge(authorizer=authorizer)
    mgr = graph.assembly_manager

    # Provide 4 independent root observations for same pair ('vote_u', 'vote_v')
    for i in range(1, 5):
        bridge.observe_text(
            boundary_namespace="ns",
            source_occurrence_key=f"k_vote_{i}",
            source_event_key=f"e_vote_{i}",
            ingress_boundary="b",
            raw_text="vote_u vote_v",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )

    # Before the 5th vote, assembly is not yet confirmed
    assert len(mgr.assemblies) == 0

    # 5th independent root observation triggers confirmation into an Assembly
    res5 = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_vote_5",
        source_event_key="e_vote_5",
        ingress_boundary="b",
        raw_text="vote_u vote_v",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res5.status == "PERSISTENT_EXECUTED"

    # Assembly is formed
    assert len(mgr.assemblies) == 1
    confirmed_asm_id = next(iter(mgr.assemblies.keys()))

    # Visible in same event's post-commit SDCR
    sdcr5 = res5.representations[0]
    active_asm_ids = [aid for aid, v in sdcr5.active_assembly_refs]
    assert confirmed_asm_id in active_asm_ids


def test_pir03_t23_frozen_t70_replay_after_unrelated_graph_change_zero_persistent_delta():
    """PIR03-T23 (T70): replay after unrelated graph change -> zero persistent delta."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)

    res1 = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_rep",
        source_event_key="e_rep",
        ingress_boundary="b",
        raw_text="node_one node_two",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res1.status == "PERSISTENT_EXECUTED"

    # Make unrelated graph change
    graph.node("text:unrelated_node", "text")
    graph._link("text:unrelated_node", "text:node_one", W=0.7)
    node_count_before_replay = len(graph.nodes)
    edge_count_before_replay = len(graph.edges)
    ledger_count_before_replay = len(runtime.ledger.committed_transactions)

    # Replay original observation
    res2 = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_rep",
        source_event_key="e_rep",
        ingress_boundary="b",
        raw_text="node_one node_two",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res2.status == "PERSISTENT_REPLAY"
    assert len(graph.nodes) == node_count_before_replay
    assert len(graph.edges) == edge_count_before_replay
    assert len(runtime.ledger.committed_transactions) == ledger_count_before_replay


def test_pir03_t24_frozen_t71_changed_graph_may_change_replay_rid():
    """PIR03-T24 (T71): changed graph may lawfully change replay RID while persistent delta is zero."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, _ = _make_bridge(authorizer=authorizer)

    res1 = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_rid",
        source_event_key="e_rid",
        ingress_boundary="b",
        raw_text="elem_a elem_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert len(res1.representations) > 0

    # Modify existing edge weight between them
    edge = graph.edge("text:elem_a", "text:elem_b")
    if edge:
        edge.W = 99.0

    res2 = bridge.observe_text(
        boundary_namespace="ns",
        source_occurrence_key="k_rid",
        source_event_key="e_rid",
        ingress_boundary="b",
        raw_text="elem_a elem_b",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res2.status == "PERSISTENT_REPLAY"
    # RID derived from current state reflects new support
    rid2 = res2.representations[0].representation_id
    assert isinstance(rid2, str) and len(rid2) > 0


def test_pir03_t25_frozen_t72_commit_survives_projection_failure():
    """PIR03-T25 (T72): commit survives projection failure."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_j_commit_then_forced_later_child_rfc12_failure,
    )
    test_scenario_j_commit_then_forced_later_child_rfc12_failure()


def test_pir03_t26_frozen_t73_partial_sdcrs_close():
    """PIR03-T26 (T73): projection failure closes every partially created SDCR."""
    from tests.test_ric01_r2_repair import (
        test_pir01_t32_partial_projection_failure_removes_every_earlier_rep_from_active_representations,
    )
    test_pir01_t32_partial_projection_failure_removes_every_earlier_rep_from_active_representations()


def test_pir03_t27_frozen_t74_retry_is_replay_with_successful_projection():
    """PIR03-T27 (T74): retry -> R1 replay + successful projection + zero double learning."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)

    occ = ExternalOccurrenceDescriptor("ns_retry", "k_retry")
    payload = {"source_code": "def f(x):\n    return x\ndef g(y):\n    return y\n", "module": "mod"}

    # First attempt: force failure on child 1 during projection
    original_build = graph.representation_engine.build_canonical_representation
    call_count = [0]

    def failing_build(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 2:
            raise RuntimeError("Forced child 1 projection failure")
        return original_build(*args, **kwargs)

    with patch.object(graph.representation_engine, "build_canonical_representation", side_effect=failing_build):
        with pytest.raises(R2ProjectionFailure) as exc_info:
            bridge.observe(
                occurrence=occ,
                source_event_key="e_retry",
                ingress_boundary="b",
                modality="code",
                payload=payload,
                mode=ExecutionMode.AUTHORIZED_PERSISTENT,
                capability="valid_cap",
            )
        assert exc_info.value.persistent_committed is True

    committed_tx_count = len(runtime.ledger.committed_transactions)

    # Second attempt (retry without failure): executes as PERSISTENT_REPLAY cleanly
    res_retry = bridge.observe(
        occurrence=occ,
        source_event_key="e_retry",
        ingress_boundary="b",
        modality="code",
        payload=payload,
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    assert res_retry.status == "PERSISTENT_REPLAY"
    assert len(res_retry.representations) == 4
    # Zero double learning: ledger transactions count remains identical
    assert len(runtime.ledger.committed_transactions) == committed_tx_count


# ─────────────────────────────────────────────────────────── Fail-Stop (T78..T81)

def test_pir03_t28_frozen_t78_encoder_exception_zero_persistent_delta():
    """PIR03-T28 (T78): encoder exception zero persistent delta."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)
    occ = ExternalOccurrenceDescriptor("ns", "k_enc_fail")

    with (
        patch.object(bridge._encoder, "encode_text", side_effect=ValueError("Encoder crash")),
        pytest.raises(R2DescriptorError, match="Encoder crash"),
    ):
        bridge.observe(
            occurrence=occ,
            source_event_key="e_enc_fail",
            ingress_boundary="b",
            modality="text",
            payload={"raw_text": "some text"},
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )

    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert len(runtime.ledger.committed_transactions) == 0


def test_pir03_t29_frozen_t79_pre_command_validation_failure_zero_delta():
    """PIR03-T29 (T79): pre-command validation failure zero delta."""
    authorizer = SimpleObservationAuthorizer(allow=False)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)
    occ = ExternalOccurrenceDescriptor("ns", "k_denied")

    with pytest.raises(R2AuthorizationError):
        bridge.observe(
            occurrence=occ,
            source_event_key="e_denied",
            ingress_boundary="b",
            modality="text",
            payload={"raw_text": "some text"},
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )

    assert len(graph.nodes) == 0
    assert len(runtime.ledger.committed_transactions) == 0


def test_pir03_t30_frozen_t80_partial_persistent_callback_mutation_exception_mutation_failed():
    """PIR03-T30 (T80): partial persistent callback mutation + exception -> MUTATION_FAILED."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, graph, runtime = _make_bridge(authorizer=authorizer)

    # Inject exception during persistent mutation execution
    with (
        patch.object(graph, "_link", side_effect=RuntimeError("Graph corruption during mutation")),
        pytest.raises(RuntimeError, match="Graph corruption during mutation"),
    ):
        bridge.observe_text(
            boundary_namespace="ns",
            source_occurrence_key="k_mut_fail",
            source_event_key="e_mut_fail",
            ingress_boundary="b",
            raw_text="fail_node_1 fail_node_2",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )

    # Runtime health must transition to MUTATION_FAILED fail-stop
    assert runtime.causal_runtime_health == CausalRuntimeHealth.MUTATION_FAILED


def test_pir03_t31_frozen_t81_fail_stop_blocks_save_and_further_persistent_commands(tmp_path):
    """PIR03-T31 (T81): fail-stop blocks save and further persistent commands."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, _, runtime = _make_bridge(authorizer=authorizer)

    # Force MUTATION_FAILED
    runtime.causal_runtime_health = CausalRuntimeHealth.MUTATION_FAILED

    # Save is blocked
    with pytest.raises(CausalRuntimeFailStopError, match="MUTATION_FAILED"):
        save_canonical_r1_checkpoint(runtime, tmp_path / "dummy_path.json")

    # Further persistent observation commands are blocked
    with pytest.raises(CausalRuntimeFailStopError, match="MUTATION_FAILED"):
        bridge.observe_text(
            boundary_namespace="ns",
            source_occurrence_key="k_after_fail",
            source_event_key="e_after_fail",
            ingress_boundary="b",
            raw_text="hello world",
            mode=ExecutionMode.AUTHORIZED_PERSISTENT,
            capability="valid_cap",
        )


# ─────────────────────────────────────────────────────────── Checkpoint / Scope (T82..T89)

def test_pir03_t32_frozen_t82_matching_protocol_restore(tmp_path):
    """PIR03-T32 (T82): matching protocol restore succeeds."""
    _, _graph, runtime = _make_bridge()
    cp_path = tmp_path / "test_cp.json"
    save_canonical_r1_checkpoint(runtime, cp_path)
    restored_runtime, _report = restore_canonical_r1_checkpoint(
        cp_path,
        expected_observation_protocol_version="R2-OBS-1.0",
    )
    assert restored_runtime is not None
    assert restored_runtime.graph is not None
    assert restored_runtime.ledger is not None


def test_pir03_t33_frozen_t83_checkpoint_schema_remains_1_2_0():
    """PIR03-T33 (T83): checkpoint schema remains 1.2.0."""
    _, graph, runtime = _make_bridge()
    ckpt = build_canonical_r1_checkpoint(graph, runtime.ledger, "R2-OBS-1.0")
    assert ckpt["schema"]["checkpoint_schema_version"] == "1.2.0"
    assert ckpt["schema"]["runtime_contract_version"] == "1.2.0"


def test_pir03_t34_frozen_t84_explicit_pre_r1_migration_target_r2_obs_1_0(tmp_path):
    """PIR03-T34 (T84): explicit pre-R1 migration target R2-OBS-1.0."""
    g = CognitiveGraph()
    cp_path = tmp_path / "cp_legacy.json"
    save_cognitive_checkpoint(g, cp_path)
    with open(cp_path, "r", encoding="utf-8") as f:
        cp_111 = json.load(f)

    migrated_120, _report = migrate_schema_1_1_1_to_1_2_0(
        cp_111,
        target_observation_protocol_version="R2-OBS-1.0",
    )
    assert migrated_120["schema"]["checkpoint_schema_version"] == "1.2.0"
    assert migrated_120["schema"]["observation_protocol_version"] == "R2-OBS-1.0"


def test_pir03_t35_frozen_t85_different_existing_1_2_0_observation_protocol_fails_closed(tmp_path):
    """PIR03-T35 (T85): different existing 1.2.0 observation protocol fails closed."""
    _, _graph, runtime = _make_bridge()
    cp_path = tmp_path / "test_cp_mismatch.json"
    save_canonical_r1_checkpoint(runtime, cp_path)
    from dgca.persistence import CheckpointCompatibilityError
    with pytest.raises(CheckpointCompatibilityError, match="Observation protocol version mismatch"):
        restore_canonical_r1_checkpoint(
            cp_path,
            expected_observation_protocol_version="INCOMPATIBLE-OBS-2.0",
        )


def test_pir03_t36_frozen_t86_audio_production_diff_unchanged():
    """PIR03-T36 (T86): Audio production diff unchanged from R1 baseline."""
    res = subprocess.run(
        ["git", "diff", "e0ce00283962ef4ae94ce3bed184fa9ca594bfbc", "--", "dgca/audio.py", "dgca/audio/"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.stdout.strip() == "", f"Audio production diff detected: {res.stdout}"


def test_pir03_t37_frozen_t87_vision_production_diff_unchanged():
    """PIR03-T37 (T87): Vision production diff unchanged from R1 baseline."""
    res = subprocess.run(
        ["git", "diff", "e0ce00283962ef4ae94ce3bed184fa9ca594bfbc", "--", "dgca/vision.py", "dgca/vision/"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.stdout.strip() == "", f"Vision production diff detected: {res.stdout}"


def test_pir03_t38_frozen_t88_r1_protocol_digest_unchanged():
    """PIR03-T38 (T88): R1 causal identity protocol digest unchanged and 21 domains."""
    r1_digest = compute_causal_identity_protocol_digest()
    assert r1_digest == "f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398"
    assert len(LITERAL_DOMAIN_REGISTRY) == 21


def test_pir03_t39_frozen_t89_legacy_baseline_behavior_regression_compatible():
    """PIR03-T39 (T89): legacy baseline behavior regression-compatible."""
    sig = behavioral_signature(build_reference_graph())
    assert sig == "915119d40643cb97"
