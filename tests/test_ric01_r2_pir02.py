"""
DGCA — RIC-01 / R2-PIR-02
Final Observation Semantics, Receipt Validation & Release-Evidence Closure Tests
Mandatory Acceptance Tests PIR02-T01 .. PIR02-T27
Strict Repair & Verification Master Prompt v1.0 — FROZEN
"""
import ast
import hashlib
import importlib
import re
from unittest.mock import patch

import pytest

import tests.test_ric01_r2_matrix as matrix_mod
from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    ExternalOccurrenceDescriptor,
    canonical_json_bytes,
    create_native_r1_provenance_epoch,
    derive_participation_receipt_id,
)
from dgca.encoder import SensoryEpisode
from dgca.graph import CognitiveGraph
from dgca.observation import (
    MICRO_DESCRIPTOR_VERSION,
    R2_OBSERVATION_PROTOCOL_VERSION,
    R2_OBSERVATION_SEMANTICS_DIGEST,
    R2_OBSERVATION_SEMANTICS_REGISTRY,
    CanonicalMicroEpisodeDescriptor,
    CanonicalObservationResult,
    CanonicalReceiptEntry,
    ExecutionMode,
    ExpectedReceiptEntry,
    R2BatchValidationError,
    R2DescriptorError,
    close_result,
    compute_r2_observation_semantics_digest,
    derive_expected_receipt_plan,
    validate_canonical_receipt_batch,
    validate_r2_observation_semantics_registry,
)
from dgca.persistence import (
    RuntimeLifecycleGuard,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
)
from tests.test_ric01_r2_authorizer import SimpleObservationAuthorizer


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


# ─────────────────────────────────────────────────────────── PIR02-B01: Semantics Registry & Digest (T01 - T07)

def test_pir02_t01_exact_18_key_registry_equality():
    """PIR02-T01: Exact 18-key frozen semantics registry equality with v1.1.1 erratum."""
    assert isinstance(R2_OBSERVATION_SEMANTICS_REGISTRY, dict)
    assert len(R2_OBSERVATION_SEMANTICS_REGISTRY) == 18

    expected_keys = {
        "protocol_version",
        "event_descriptor_version",
        "micro_descriptor_version",
        "mutation_descriptor_version",
        "receipt_batch_version",
        "result_version",
        "supported_modalities",
        "operation_kinds",
        "persistent_transaction_granularity",
        "observation_relation_policy",
        "rfc11_evidence_policy",
        "tbr_policy",
        "receipt_order",
        "sdcr_cardinality",
        "projection_timing",
        "projection_failure",
        "transient_replay",
        "authorization_default",
    }
    assert set(R2_OBSERVATION_SEMANTICS_REGISTRY.keys()) == expected_keys
    validate_r2_observation_semantics_registry()
    assert R2_OBSERVATION_SEMANTICS_REGISTRY["authorization_default"] == "DENY_ALL"
    assert R2_OBSERVATION_SEMANTICS_REGISTRY["sdcr_cardinality"] == "ONE_PER_OBSERVABLE_MICROEPISODE"
    assert R2_OBSERVATION_SEMANTICS_REGISTRY["transient_replay"] == "CURRENT_STATE_RECONSTRUCTION"
    assert R2_OBSERVATION_SEMANTICS_REGISTRY["persistent_transaction_granularity"] == "ONE_ENCODED_INGRESS_EVENT"


def test_pir02_t02_direct_canonical_sha256_equals_corrected_digest():
    """PIR02-T02: Direct canonical SHA-256 equals corrected digest bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b."""
    expected = "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"
    assert R2_OBSERVATION_SEMANTICS_DIGEST == expected
    computed = compute_r2_observation_semantics_digest()
    assert computed == expected
    assert computed == R2_OBSERVATION_SEMANTICS_DIGEST


def test_pir02_t03_digest_length_exactly_64_hex():
    """PIR02-T03: Digest length is exactly 64 lowercase hexadecimal characters."""
    assert len(R2_OBSERVATION_SEMANTICS_DIGEST) == 64
    assert re.fullmatch(r"[0-9a-f]{64}", R2_OBSERVATION_SEMANTICS_DIGEST) is not None
    computed = compute_r2_observation_semantics_digest()
    assert len(computed) == 64
    assert re.fullmatch(r"[0-9a-f]{64}", computed) is not None


def test_pir02_t04_direct_sha256_recomputed_no_xor_calibration():
    """PIR02-T04: Direct canonical SHA-256 computation matches digest without any XOR calibration."""
    canonical_bytes = canonical_json_bytes(R2_OBSERVATION_SEMANTICS_REGISTRY)
    direct_hash = hashlib.sha256(canonical_bytes).hexdigest()
    assert direct_hash == R2_OBSERVATION_SEMANTICS_DIGEST
    assert compute_r2_observation_semantics_digest() == direct_hash


def test_pir02_t05_changing_one_top_level_literal_changes_digest():
    """PIR02-T05: Changing any one top-level literal changes the computed digest."""
    base_digest = compute_r2_observation_semantics_digest()
    for key in ("authorization_default", "sdcr_cardinality", "transient_replay", "projection_failure"):
        mutated = dict(R2_OBSERVATION_SEMANTICS_REGISTRY)
        mutated[key] = "MUTATED_VALUE"
        mut_digest = compute_r2_observation_semantics_digest(mutated)
        assert mut_digest != base_digest, f"Digest did not change on mutation of {key}"
    # Reverting restores exact digest
    assert compute_r2_observation_semantics_digest(R2_OBSERVATION_SEMANTICS_REGISTRY) == base_digest


def test_pir02_t06_changing_one_nested_literal_changes_digest():
    """PIR02-T06: Changing any one nested literal changes the computed digest."""
    base_digest = compute_r2_observation_semantics_digest()

    # Mutate nested tbr_policy
    mutated = dict(R2_OBSERVATION_SEMANTICS_REGISTRY)
    mutated["tbr_policy"] = dict(R2_OBSERVATION_SEMANTICS_REGISTRY["tbr_policy"])
    mutated["tbr_policy"]["simultaneous"] = "MUTATED_TBR_POLICY"
    assert compute_r2_observation_semantics_digest(mutated) != base_digest

    # Mutate receipt_order
    mutated2 = dict(R2_OBSERVATION_SEMANTICS_REGISTRY)
    mutated2["receipt_order"] = ["MUTATED_ORDER"]
    assert compute_r2_observation_semantics_digest(mutated2) != base_digest

    # Mutate rfc11_evidence_policy
    mutated3 = dict(R2_OBSERVATION_SEMANTICS_REGISTRY)
    mutated3["rfc11_evidence_policy"] = dict(R2_OBSERVATION_SEMANTICS_REGISTRY["rfc11_evidence_policy"])
    mutated3["rfc11_evidence_policy"]["simultaneous"] = "MUTATED_EVIDENCE_POLICY"
    assert compute_r2_observation_semantics_digest(mutated3) != base_digest


def test_pir02_t07_source_code_clean_of_xor_calibration_symbols():
    """PIR02-T07: observation.py source code contains no XOR calibration symbols or constants."""
    with open("dgca/observation.py", "r", encoding="utf-8") as f:
        src = f.read()

    assert "_BASE_RAW_HASH_INT" not in src
    assert "_EXPECTED_DIGEST_INT" not in src
    # Verify no bitwise XOR is used in compute_r2_observation_semantics_digest
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "compute_r2_observation_semantics_digest":
            for sub in ast.walk(node):
                assert not isinstance(sub, ast.BitXor), "Found BitXor (^) in compute_r2_observation_semantics_digest"


# ─────────────────────────────────────────────────────────── PIR02-B02: Receipt Plan Validation (T08 - T15)

def test_pir02_t08_derive_expected_receipt_plan_purity_and_fields():
    """PIR02-T08: derive_expected_receipt_plan purity and exact expected fields."""
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "apple"), ("text", "banana")),
        child_index=0,
        micro_episode_id="mep_pure",
    )
    plan1 = derive_expected_receipt_plan(desc, "mep_pure")
    plan2 = derive_expected_receipt_plan(desc, "mep_pure")
    assert plan1 == plan2

    assert len(plan1) >= 2
    for entry in plan1:
        assert isinstance(entry, ExpectedReceiptEntry)
        assert entry.slot_index >= 0
        assert entry.slot_class in (
            "POSITIVE_NODE_OCCURRENCES",
            "CONTRADICTION_ENDPOINT_OCCURRENCES",
            "LIVE_GATE_OPEN_OBSERVATION_RELATION_EDGE_RECEIPTS",
        )
        assert entry.kind in ("node", "contradiction_endpoint", "edge")
        assert isinstance(entry.element_ref, (str, tuple))
        assert entry.occurrence_scope.startswith("r2occ:") or entry.occurrence_scope.startswith("r2relation:")
        assert isinstance(entry.scope_refs, tuple)
        assert isinstance(entry.activation_magnitude, float)
        assert isinstance(entry.relational_drive, float)


def test_pir02_t09_rejection_simultaneous_forged_slot_scope():
    """PIR02-T09: Rejection of simultaneous canonical-looking wrong occurrence index (e.g. simultaneous:999)."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "apple"),),
        child_index=0,
        micro_episode_id="mep_sim_forged",
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "apple")])
    batch = bridge._build_receipt_batch(
        txid="tx_f1", micro_desc=desc, ep=ep, child_index=0, local_parent_cycle_id=1,
    )

    forged_occ = "r2occ:mep_sim_forged:simultaneous:999"
    new_scope_refs = ("mep_sim_forged", forged_occ)
    rid = derive_participation_receipt_id(
        micro_episode_id="mep_sim_forged",
        participation_kind="node",
        element_ref="text:apple",
        scope_refs=list(new_scope_refs),
        slot_index=0,
        prefix="pr_",
    )
    batch.ordered_receipt_entries[0] = CanonicalReceiptEntry(
        slot_index=0,
        receipt_id=rid,
        kind="node",
        element_ref="text:apple",
        occurrence_scope=forged_occ,
        scope_refs=new_scope_refs,
    )

    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx_f1",
            expected_micro_id="mep_sim_forged",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=desc,
        )


def test_pir02_t10_rejection_sequence_wrong_step_coordinate():
    """PIR02-T10: Rejection of sequence wrong step coordinate (e.g. step:99:0)."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="sequence",
        steps=((("text", "first"),), (("text", "second"),)),
        child_index=0,
        micro_episode_id="mep_seq_forged",
    )
    ep = SensoryEpisode(kind="sequence", steps=[[("text", "first")], [("text", "second")]])
    batch = bridge._build_receipt_batch(
        txid="tx_f2", micro_desc=desc, ep=ep, child_index=0, local_parent_cycle_id=1,
    )

    forged_occ = "r2occ:mep_seq_forged:step:99:0"
    new_scope_refs = ("mep_seq_forged", forged_occ)
    rid = derive_participation_receipt_id(
        micro_episode_id="mep_seq_forged",
        participation_kind="node",
        element_ref="text:first",
        scope_refs=list(new_scope_refs),
        slot_index=0,
        prefix="pr_",
    )
    batch.ordered_receipt_entries[0] = CanonicalReceiptEntry(
        slot_index=0,
        receipt_id=rid,
        kind="node",
        element_ref="text:first",
        occurrence_scope=forged_occ,
        scope_refs=new_scope_refs,
    )

    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx_f2",
            expected_micro_id="mep_seq_forged",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=desc,
        )


def test_pir02_t11_rejection_contradiction_wrong_endpoint_coordinate():
    """PIR02-T11: Rejection of contradiction wrong endpoint coordinate (e.g. contra:0:7)."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        contradictions=(("apple", "orange"),),
        child_index=0,
        micro_episode_id="mep_contra_forged",
    )
    ep = SensoryEpisode(kind="simultaneous", contradictions=[("apple", "orange")])
    batch = bridge._build_receipt_batch(
        txid="tx_f3", micro_desc=desc, ep=ep, child_index=0, local_parent_cycle_id=1,
    )

    forged_occ = "r2occ:mep_contra_forged:contra:0:7"
    new_scope_refs = ("mep_contra_forged", forged_occ)
    rid = derive_participation_receipt_id(
        micro_episode_id="mep_contra_forged",
        participation_kind="node",
        element_ref="text:apple",
        scope_refs=list(new_scope_refs),
        slot_index=0,
        prefix="pr_",
    )
    batch.ordered_receipt_entries[0] = CanonicalReceiptEntry(
        slot_index=0,
        receipt_id=rid,
        kind="node",
        element_ref="text:apple",
        occurrence_scope=forged_occ,
        scope_refs=new_scope_refs,
    )

    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx_f3",
            expected_micro_id="mep_contra_forged",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=desc,
        )


def test_pir02_t12_rejection_forged_relation_index_or_swapped_edge_element():
    """PIR02-T12: Rejection of forged relation index or swapped edge element after valid rehash."""
    bridge = _make_bridge()
    bridge._graph.node("text:a", "text")
    bridge._graph.node("text:b", "text")
    bridge._graph._link("text:a", "text:b", W=0.5)

    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "a"), ("text", "b")),
        child_index=0,
        micro_episode_id="mep_rel_forged",
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "a"), ("text", "b")])
    batch = bridge._build_receipt_batch(
        txid="tx_f4", micro_desc=desc, ep=ep, child_index=0, local_parent_cycle_id=1,
    )

    edge_entries = [e for e in batch.ordered_receipt_entries if e.kind == "edge"]
    assert len(edge_entries) > 0
    edge_idx = batch.ordered_receipt_entries.index(edge_entries[0])

    forged_scope = "r2relation:mep_rel_forged:999"
    new_scope_refs = ("mep_rel_forged", forged_scope)
    rid = derive_participation_receipt_id(
        micro_episode_id="mep_rel_forged",
        participation_kind="edge",
        element_ref=edge_entries[0].element_ref,
        scope_refs=list(new_scope_refs),
        slot_index=edge_idx,
        prefix="pr_",
    )
    batch.ordered_receipt_entries[edge_idx] = CanonicalReceiptEntry(
        slot_index=edge_idx,
        receipt_id=rid,
        kind="edge",
        element_ref=edge_entries[0].element_ref,
        occurrence_scope=forged_scope,
        scope_refs=new_scope_refs,
    )

    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx_f4",
            expected_micro_id="mep_rel_forged",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=desc,
            graph=bridge._graph,
        )


def test_pir02_t13_duplicate_node_occurrence_cannot_borrow_sibling_scope():
    """PIR02-T13: Duplicate NodeRef occurrence cannot borrow sibling binding scope."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "dup"), ("text", "dup")),
        child_index=0,
        micro_episode_id="mep_borrow",
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "dup"), ("text", "dup")])
    batch = bridge._build_receipt_batch(
        txid="tx_b", micro_desc=desc, ep=ep, child_index=0, local_parent_cycle_id=1,
    )

    # Slot 1 borrows slot 0's occurrence scope
    borrowed_scope = batch.ordered_receipt_entries[0].occurrence_scope
    new_scope_refs = ("mep_borrow", borrowed_scope, batch.ordered_binding_entries[0].binding_scope)
    rehashed_rid = derive_participation_receipt_id(
        micro_episode_id="mep_borrow",
        participation_kind="node",
        element_ref="text:dup",
        scope_refs=list(new_scope_refs),
        slot_index=1,
        prefix="pr_",
    )
    batch.ordered_receipt_entries[1] = CanonicalReceiptEntry(
        slot_index=1,
        receipt_id=rehashed_rid,
        kind="node",
        element_ref="text:dup",
        occurrence_scope=borrowed_scope,
        scope_refs=new_scope_refs,
    )

    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx_b",
            expected_micro_id="mep_borrow",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=desc,
        )


def test_pir02_t14_lawful_duplicate_node_occurrences_pass_validation():
    """PIR02-T14: Exact lawful duplicate-occurrence batch accepted."""
    bridge = _make_bridge()
    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "dup"), ("text", "dup"), ("text", "other")),
        child_index=0,
        micro_episode_id="mep_lawful_dup",
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "dup"), ("text", "dup"), ("text", "other")])
    batch = bridge._build_receipt_batch(
        txid="tx_ld", micro_desc=desc, ep=ep, child_index=0, local_parent_cycle_id=1,
    )

    # Must pass validation cleanly
    validate_canonical_receipt_batch(
        batch=batch,
        expected_txid="tx_ld",
        expected_micro_id="mep_lawful_dup",
        expected_child_index=0,
        expected_cycle_id=1,
        micro_descriptor=desc,
    )


def test_pir02_t15_lawful_edge_observation_relations_pass_validation():
    """PIR02-T15: Exact lawful edge relation plan accepted."""
    bridge = _make_bridge()
    bridge._graph.node("text:x", "text")
    bridge._graph.node("text:y", "text")
    bridge._graph._link("text:x", "text:y", W=0.8)

    desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "x"), ("text", "y")),
        child_index=0,
        micro_episode_id="mep_lawful_edge",
    )
    ep = SensoryEpisode(kind="simultaneous", signals=[("text", "x"), ("text", "y")])
    batch = bridge._build_receipt_batch(
        txid="tx_le", micro_desc=desc, ep=ep, child_index=0, local_parent_cycle_id=1,
    )

    # Must pass validation cleanly with graph
    validate_canonical_receipt_batch(
        batch=batch,
        expected_txid="tx_le",
        expected_micro_id="mep_lawful_edge",
        expected_child_index=0,
        expected_cycle_id=1,
        micro_descriptor=desc,
        graph=bridge._graph,
    )


# ─────────────────────────────────────────────────────────── PIR02-B03: close_result Idempotency (T16 - T20)

def test_pir02_t16_close_result_direct_idempotency_engine_called_once():
    """PIR02-T16: direct close_result(res) twice -> no second engine close invocation."""
    class MockEngine:
        def __init__(self):
            self.calls = 0
        def close_representation(self, rep):
            self.calls += 1

    class MockRep:
        pass

    engine = MockEngine()
    res = CanonicalObservationResult(
        result_version="R2-RESULT-1.0",
        status="TRANSIENT_OBSERVED",
        mode=ExecutionMode.TRANSIENT_ONLY,
        root_external_episode_id="root_t16",
        ingress_event_id="evt_t16",
        event_descriptor_digest="a" * 64,
        observation_transaction_id="tx_t16",
        persistent_phase="NOT_REQUESTED",
        persistent_transaction_id=None,
        persistent_executed=False,
        micro_episodes=(),
        representations=(MockRep(),),
        diagnostics={},
        _engine=engine,
    )

    close_result(res)
    assert engine.calls == 1
    assert res.is_closed is True

    # Second direct call: strictly no-op
    close_result(res)
    assert engine.calls == 1
    assert res.is_closed is True


def test_pir02_t17_close_result_counter_unchanged_by_second_direct_close():
    """PIR02-T17: representations_closed counter unchanged by second direct close."""
    bridge = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_t17",
        source_event_key="evt_t17",
        ingress_boundary="b",
        raw_text="Testing counter stability across direct close.",
    )
    rep_engine = bridge._graph.representation_engine

    close_result(res)
    assert res.is_closed is True
    closed_count = rep_engine.observability.representations_closed
    assert closed_count > 0

    # Second direct close
    close_result(res)
    assert rep_engine.observability.representations_closed == closed_count


def test_pir02_t18_active_closed_maps_unchanged_by_second_direct_close():
    """PIR02-T18: active/closed representation maps unchanged by second direct close."""
    bridge = _make_bridge()
    res = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_t18",
        source_event_key="evt_t18",
        ingress_boundary="b",
        raw_text="Testing map stability across direct close.",
    )
    rep_engine = bridge._graph.representation_engine

    close_result(res)
    active_keys_1 = set(rep_engine.active_representations.keys())
    closed_keys_1 = set(rep_engine.closed_representations.keys())

    close_result(res)
    active_keys_2 = set(rep_engine.active_representations.keys())
    closed_keys_2 = set(rep_engine.closed_representations.keys())

    assert active_keys_1 == active_keys_2
    assert closed_keys_1 == closed_keys_2


def test_pir02_t19_persistent_state_neutrality_across_both_closes():
    """PIR02-T19: Persistent graph digest and ledger unchanged across both closes."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge = _make_bridge(authorizer=authorizer)
    res = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_t19",
        source_event_key="evt_t19",
        ingress_boundary="b",
        raw_text="Persistent observation for close neutrality.",
        mode=ExecutionMode.AUTHORIZED_PERSISTENT,
        capability="valid_cap",
    )
    digest_before = compute_checkpoint_state_digest(extract_canonical_persistent_payload(bridge._graph))
    tx_count_before = len(bridge._runtime.ledger.committed_transactions)

    close_result(res)
    digest_after_1 = compute_checkpoint_state_digest(extract_canonical_persistent_payload(bridge._graph))
    tx_count_after_1 = len(bridge._runtime.ledger.committed_transactions)

    close_result(res)
    digest_after_2 = compute_checkpoint_state_digest(extract_canonical_persistent_payload(bridge._graph))
    tx_count_after_2 = len(bridge._runtime.ledger.committed_transactions)

    assert digest_before == digest_after_1 == digest_after_2
    assert tx_count_before == tx_count_after_1 == tx_count_after_2


def test_pir02_t20_mixed_order_close_result_and_res_close():
    """PIR02-T20: res.close() and close_result(res) mixed ordering remains idempotent."""
    bridge = _make_bridge()

    # Order 1: close_result then res.close()
    res1 = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_t20_1",
        source_event_key="evt_t20_1",
        ingress_boundary="b",
        raw_text="Mixed close order one.",
    )
    close_result(res1)
    assert res1.is_closed is True
    res1.close()
    assert res1.is_closed is True

    # Order 2: res.close() then close_result
    res2 = bridge.observe_text(
        boundary_namespace="lifecycle",
        source_occurrence_key="occ_t20_2",
        source_event_key="evt_t20_2",
        ingress_boundary="b",
        raw_text="Mixed close order two.",
    )
    res2.close()
    assert res2.is_closed is True
    close_result(res2)
    assert res2.is_closed is True


# ─────────────────────────────────────────────────────────── PIR02-B04: Matrix & Verification Ledger (T21 - T27)

def test_pir02_t21_no_tautological_acceptance_ledger_remains():
    """PIR02-T21: No tautological lambda: True or constant return remains in matrix."""
    with open("tests/test_ric01_r2_matrix.py", "r", encoding="utf-8") as f:
        src = f.read()

    # Ensure no `lambda ...: True` pattern exists
    assert not re.search(r"lambda\s*[^:]*:\s*True", src), "Found tautological `lambda ...: True` in matrix!"

    # Ensure all test obligations map to real test references
    assert hasattr(matrix_mod, "FROZEN_R2_TEST_EVIDENCE")
    assert len(matrix_mod.FROZEN_R2_TEST_EVIDENCE) == 89
    for tid, refs in matrix_mod.FROZEN_R2_TEST_EVIDENCE.items():
        assert len(refs) > 0, f"{tid} has empty evidence refs"
        for ref in refs:
            assert "::" in ref, f"{tid} ref {ref} is not a valid node path"


def test_pir02_t22_exact_58_invariants_mapped_to_frozen_meanings():
    """PIR02-T22: Exact 58 invariant IDs map to Section 39 definitions and genuine checks pass."""
    assert hasattr(matrix_mod, "FROZEN_R2_INVARIANTS")
    assert len(matrix_mod.FROZEN_R2_INVARIANTS) == 58

    expected_ids = [f"R2-I{i:02d}" for i in range(1, 59)]
    assert list(matrix_mod.FROZEN_R2_INVARIANTS.keys()) == expected_ids

    # R2-I01 frozen meaning check
    assert "Trusted occurrence metadata" in matrix_mod.FROZEN_R2_INVARIANTS["R2-I01"]
    assert "RootExternalEpisode identity" in matrix_mod.FROZEN_R2_INVARIANTS["R2-I01"]

    # R2-I02 raw authority check
    assert "Raw user text/code cannot grant persistent-learning authority" in matrix_mod.FROZEN_R2_INVARIANTS["R2-I02"]

    # Check all 58 invariants have non-empty semantic test evidence
    for inv_id in matrix_mod.FROZEN_R2_INVARIANTS:
        assert inv_id in matrix_mod.FROZEN_R2_INVARIANT_EVIDENCE
        assert len(matrix_mod.FROZEN_R2_INVARIANT_EVIDENCE[inv_id]) > 0


def test_pir02_t23_exact_89_test_ids_map_to_real_tests():
    """PIR02-T23: Exact 89 test IDs T01..T89 map to non-empty test nodes."""
    evidence = matrix_mod.FROZEN_R2_TEST_EVIDENCE
    assert len(evidence) == 89
    for i in range(1, 90):
        tid = f"T{i:02d}"
        assert tid in evidence, f"Missing test obligation {tid}"
        assert len(evidence[tid]) > 0
        for ref in evidence[tid]:
            assert "tests/" in ref and "::test_" in ref


def test_pir02_t24_mapping_references_resolvable_real_tests():
    """PIR02-T24: All test references in FROZEN_R2_TEST_EVIDENCE resolve to existing callable tests."""
    evidence = matrix_mod.FROZEN_R2_TEST_EVIDENCE
    for tid, refs in evidence.items():
        for ref in refs:
            mod_name, func_name = ref.split("::")
            mod = importlib.import_module(mod_name.replace("/", ".").replace("\\", ".").replace(".py", ""))
            fn = getattr(mod, func_name, None)
            assert fn is not None, f"Could not find {func_name} in {mod_name} for {tid}"
            assert callable(fn), f"{func_name} in {mod_name} is not callable"


def test_pir02_t25_pir01_t35_performs_actual_mismatch_fault_injection():
    """PIR02-T25: PIR01-T35 performs actual descriptor length mismatch fault injection and fails closed."""
    bridge = _make_bridge()
    occ = ExternalOccurrenceDescriptor("hardening", "occ_h2_t25")
    dummy_desc = CanonicalMicroEpisodeDescriptor(
        descriptor_version=MICRO_DESCRIPTOR_VERSION,
        kind="simultaneous",
        signals=(("text", "A"),),
        micro_episode_id="mep_dummy",
        child_index=0,
    )
    with (
        patch.object(bridge, "_build_micro_descriptors", return_value=[dummy_desc, dummy_desc]),
        pytest.raises(R2DescriptorError, match="Episode count does not equal micro_descriptor count"),
    ):
        bridge.observe(
            occurrence=occ,
            source_event_key="evt_h2_t25",
            ingress_boundary="b",
            modality="text",
            payload={"raw_text": "hello"},
        )
    assert len(bridge._graph.nodes) == 0
    assert len(bridge._graph.edges) == 0


def test_pir02_t26_scenario_d_tests_missing_member_scope():
    """PIR02-T26: Scenario D tests valid members with missing receipt scope and fails closed."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected,
    )
    # Must execute cleanly and pass the assertion
    test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected()


def test_pir02_t27_scenario_b_proves_no_duplicate_rfc11_independent_vote():
    """PIR02-T27: Scenario B proves assembly candidate root votes remain 1 after multi-occurrence input."""
    from tests.test_ric01_r2_adversarial import (
        test_scenario_b_repeated_same_node_occurrences_receipts_preserved_dedup,
    )
    # Must execute cleanly and pass root_votes assertion
    test_scenario_b_repeated_same_node_occurrences_receipts_preserved_dedup()
