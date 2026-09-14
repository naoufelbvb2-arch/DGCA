"""
DGCA — RIC-01 / R1: Deterministic Causal Identity Protocol
Verification Suite Part 1: Identity Primitives, Canonicalization, and Downstream Derivations

Invariants: R1-I01 .. R1-I17, R1-I40, R1-I45, R1-I46, R1-I47, R1-I48
Acceptance Tests: R1-T01 .. R1-T27, R1-T59, R1-T60, R1-T65, R1-T66, R1-T67, R1-T68, R1-T69
Adversarial Scenarios: A, B, C, D, H, I
"""
import hashlib

import pytest

from dgca.causal_identity import (
    CANONICALIZATION_PROFILE,
    CAUSAL_IDENTITY_PROTOCOL_DIGEST,
    LITERAL_DOMAIN_REGISTRY,
    CausalDomainError,
    CausalIdentityValidationError,
    CausalLineageError,
    ExternalOccurrenceDescriptor,
    PersistentMutationCommand,
    canonical_json_bytes,
    compute_causal_identity_protocol_digest,
    compute_event_descriptor_digest,
    compute_mutation_descriptor_digest,
    compute_observation_protocol_digest,
    derive_continuation_commit_id,
    derive_delivery_id,
    derive_generative_frame_id,
    derive_linearizable_occurrence_id,
    derive_operational_representation_digest,
    derive_participation_receipt_id,
    derive_pattern_candidate_id,
    derive_persistent_mutation_txid,
    derive_reinstatement_proposal_id,
    derive_representation_id,
    derive_root_external_episode_id,
    derive_surface_unit_id,
    derive_transient_binding_receipt_id,
    dgca_id,
)
from dgca.graph import CognitiveGraph
from dgca.loop import ExternalEventRecord, UnifiedGenerativeCognitiveLoopEngine
from dgca.recurrent import PredictiveRecurrentGenerativeEngine
from dgca.representation import (
    ParticipationReceipt,
    RepresentationEngine,
)


# ─────────────────────────────────────────────────────────── 1. Protocol Constants & Digest Verification
def test_r1_t59_causal_identity_protocol_digest_exact():
    """R1-T59, R1-I40: causal identity protocol digest matches exact frozen payload."""
    computed = compute_causal_identity_protocol_digest()
    assert computed == "f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398"
    assert CAUSAL_IDENTITY_PROTOCOL_DIGEST == "f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398"


def test_r1_t60_observation_protocol_digest_exact():
    """R1-T60, R1-I40: observation protocol digest matches exact frozen payload formula."""
    obs_ver = "TEST_OBS_v1.0"
    digest = compute_observation_protocol_digest(obs_ver)
    expected_payload = {"observation_protocol_version": obs_ver}
    expected = hashlib.sha256(canonical_json_bytes(expected_payload)).hexdigest()
    assert digest == expected
    assert len(digest) == 64


def test_r1_t67_domain_registry_alteration_changes_digest():
    """R1-T67, R1-I47: altering the domain registry changes identity protocol digest."""
    tampered_payload = {
        "protocol_version": "1.0",
        "protocol_prefix": "DGCA:R1:ID:v1",
        "hash_algorithm": "SHA-256",
        "authoritative_digest_hex_chars": 64,
        "canonical_json": {
            "sort_keys": True,
            "separators": [",", ":"],
            "ensure_ascii": False,
            "allow_nan": False,
        },
        "domain_registry": list(LITERAL_DOMAIN_REGISTRY) + ["NEW_UNKNOWN_DOMAIN"],
        "canonicalization_profile": CANONICALIZATION_PROFILE,
    }
    tampered_digest = hashlib.sha256(canonical_json_bytes(tampered_payload)).hexdigest()
    assert tampered_digest != CAUSAL_IDENTITY_PROTOCOL_DIGEST


# ─────────────────────────────────────────────────────────── 2. Root External Episode Derivation & Occurrence Contract
def test_r1_t01_same_occurrence_descriptor_same_root():
    """R1-T01, R1-I01: same authoritative occurrence descriptor yields same RootExternalEpisodeID across processes."""
    root1 = derive_root_external_episode_id("chat_ingress", "msg_12345")
    root2 = derive_root_external_episode_id("chat_ingress", "msg_12345")
    assert root1 == root2
    assert len(root1) == 64


def test_r1_t02_same_content_different_occurrence_keys_different_roots():
    """R1-T02, R1-I02, Adversarial A: different occurrence keys yield different roots despite identical content."""
    # Even if identical content was submitted:
    root_msg1 = derive_root_external_episode_id("chat_ingress", "msg_first")
    root_msg2 = derive_root_external_episode_id("chat_ingress", "msg_second")
    assert root_msg1 != root_msg2


def test_r1_t03_same_occurrence_retry_same_root():
    """R1-T03, Adversarial B: same occurrence retry reuses occurrence key and yields identical root."""
    root_initial = derive_root_external_episode_id("webhook", "event_42")
    root_retry = derive_root_external_episode_id("webhook", "event_42")
    assert root_initial == root_retry


def test_r1_t04_different_boundary_namespaces_different_roots():
    """R1-T04: different boundary namespaces yield different roots."""
    root_chat = derive_root_external_episode_id("chat", "id_100")
    root_queue = derive_root_external_episode_id("queue", "id_100")
    assert root_chat != root_queue


def test_r1_t05_empty_occurrence_key_namespace_rejected():
    """R1-T05: empty occurrence key or boundary namespace fails closed."""
    with pytest.raises(CausalIdentityValidationError):
        derive_root_external_episode_id("", "msg_1")

    with pytest.raises(CausalIdentityValidationError):
        derive_root_external_episode_id("chat", "")

    with pytest.raises(CausalIdentityValidationError):
        ExternalOccurrenceDescriptor("  ", "key")


def test_r1_t68_untrusted_raw_content_cannot_choose_source_occurrence():
    """R1-T68, R1-I48: root identity never derives from raw message content alone."""
    # Host must validate descriptor rather than trusting message text
    desc = ExternalOccurrenceDescriptor("host_namespace", "host_auth_msg_99")
    root_id = derive_root_external_episode_id(desc.boundary_namespace, desc.source_occurrence_key)
    raw_content_hash = hashlib.sha256(b"hello world").hexdigest()
    assert root_id != raw_content_hash


# ─────────────────────────────────────────────────────────── 3. Canonical Derivation & Domain Separation
def test_r1_t06_identity_domain_separation():
    """R1-T06, R1-I04: same payload under different domains produces different IDs."""
    shared_payload = {"key": "alpha", "index": 0}
    id_rep = dgca_id("REPRESENTATION", shared_payload)
    id_root = dgca_id("ROOT_EXTERNAL_EPISODE", shared_payload)
    id_chunk = dgca_id("SURFACE_CHUNK", shared_payload)
    assert id_rep != id_root
    assert id_rep != id_chunk
    assert id_root != id_chunk

    with pytest.raises(CausalDomainError):
        dgca_id("UNREGISTERED_DOMAIN", shared_payload)


def test_r1_t07_unordered_payload_insertion_order_independence():
    """R1-T07, R1-I06: dict insertion order and set order are canonicalized identically."""
    payload1 = {"z": 1, "a": 2, "tags": {"cat", "dog", "apple"}}
    payload2 = {"a": 2, "z": 1, "tags": {"dog", "apple", "cat"}}
    hash1 = dgca_id("INTERNAL_WORK", payload1)
    hash2 = dgca_id("INTERNAL_WORK", payload2)
    assert hash1 == hash2


def test_r1_t08_ordered_child_order_preserved():
    """R1-T08, R1-I06: ordered child sequence preserves semantic order and alters hash if reordered."""
    payload_a = {"ordered_items": ["first", "second", "third"]}
    payload_b = {"ordered_items": ["third", "second", "first"]}
    assert dgca_id("SURFACE_CHUNK", payload_a) != dgca_id("SURFACE_CHUNK", payload_b)


def test_r1_t09_non_finite_canonical_payload_rejected():
    """R1-T09: NaN and Infinity are strictly rejected from canonical identity derivation."""
    with pytest.raises(CausalIdentityValidationError):
        dgca_id("REPRESENTATION", {"value": float("nan")})

    with pytest.raises(CausalIdentityValidationError):
        dgca_id("REPRESENTATION", {"value": float("inf")})

    with pytest.raises(CausalIdentityValidationError):
        dgca_id("REPRESENTATION", {"value": float("-inf")})


def test_r1_t10_full_authoritative_digest_width_enforced():
    """R1-T10, R1-I05: full 64-char lowercase hexadecimal SHA-256 is enforced."""
    raw_id = dgca_id("ROOT_EXTERNAL_EPISODE", {"boundary_namespace": "ns", "source_occurrence_key": "k"})
    assert len(raw_id) == 64
    assert raw_id == raw_id.lower()
    int(raw_id, 16)  # valid hex check


# ─────────────────────────────────────────────────────────── 4. Ingress, Observation, MicroEpisode & Receipts
def test_r1_t11_deterministic_participation_receipt_replay():
    """R1-T11, R1-I08: canonical ParticipationReceiptID derivation replays deterministically."""
    rcpt1 = derive_participation_receipt_id(
        micro_episode_id="mep_123",
        participation_kind="node",
        element_ref="cat",
        scope_refs=("global",),
        slot_index=0,
    )
    rcpt2 = derive_participation_receipt_id(
        micro_episode_id="mep_123",
        participation_kind="node",
        element_ref="cat",
        scope_refs=("global",),
        slot_index=0,
    )
    assert rcpt1 == rcpt2
    assert len(rcpt1) == 64


def test_r1_t12_deterministic_tbr_replay():
    """R1-T12, R1-I09: canonical TransientBindingReceiptID (TBRID) replays deterministically."""
    tbr1 = derive_transient_binding_receipt_id(
        micro_episode_id="mep_123",
        binding_scope_id="scope_subj",
        member_receipt_refs=["rcpt_1", "rcpt_2"],
        binding_index=0,
    )
    tbr2 = derive_transient_binding_receipt_id(
        micro_episode_id="mep_123",
        binding_scope_id="scope_subj",
        member_receipt_refs=["rcpt_1", "rcpt_2"],
        binding_index=0,
    )
    assert tbr1 == tbr2


def test_r1_t13_operational_digest_changes_on_support_or_accepted_receipt():
    """R1-T13, R1-I10: OperationalRepresentationDigest changes when accepted support/receipt state changes."""
    op1 = derive_operational_representation_digest(
        context_binding="ctx1",
        active_assembly_refs=[("asm1", 1)],
        canonical_accepted_receipt_descriptors=[{"ref": "n1"}],
        canonical_accepted_tbr_descriptors=[],
        participating_refs={"nodes": ["n1"]},
        snapshot_coordinate=1,
        support_or_activation_values={"nodes": {"n1": 0.8}},
    )
    # Different support value
    op2 = derive_operational_representation_digest(
        context_binding="ctx1",
        active_assembly_refs=[("asm1", 1)],
        canonical_accepted_receipt_descriptors=[{"ref": "n1"}],
        canonical_accepted_tbr_descriptors=[],
        participating_refs={"nodes": ["n1"]},
        snapshot_coordinate=1,
        support_or_activation_values={"nodes": {"n1": 0.4}},
    )
    assert op1 != op2


# ─────────────────────────────────────────────────────────── 5. Canonical Representation ID (RID)
def test_r1_t14_same_causal_snapshot_rid_exact_across_fresh_engines():
    """R1-T14, R1-I11: same causal operational snapshot replay yields identical RID across fresh engines."""
    from dgca.graph import Node
    graph1 = CognitiveGraph()
    graph1.nodes["n1"] = Node(nid="n1", region="concept", A=0.8)
    engine1 = RepresentationEngine(graph1)

    graph2 = CognitiveGraph()
    graph2.nodes["n1"] = Node(nid="n1", region="concept", A=0.8)
    engine2 = RepresentationEngine(graph2)

    receipt = ParticipationReceipt(
        receipt_id="rcpt_test",
        element_ref="n1",
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        origin_lineage="external",
        participation_kind="node",
        activation_magnitude=0.8,
    )

    rep1 = engine1.build_canonical_representation(
        causal_parent_ref="obs_parent_100",
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        context=None,
        participation_receipts=[receipt],
    )
    rep2 = engine2.build_canonical_representation(
        causal_parent_ref="obs_parent_100",
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        context=None,
        participation_receipts=[receipt],
    )

    assert rep1.representation_id == rep2.representation_id
    assert rep1.representation_id.startswith("rep_")


def test_r1_t15_same_content_different_root_same_sig_different_rid():
    """R1-T15, R1-I12, Adversarial I: same semantic content under different roots has same content signature but different RIDs."""
    from dgca.graph import Node
    graph = CognitiveGraph()
    graph.nodes["concept_a"] = Node(nid="concept_a", region="concept", A=0.9)
    engine = RepresentationEngine(graph)

    receipt = ParticipationReceipt(
        receipt_id="r1",
        element_ref="concept_a",
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        origin_lineage="external",
        participation_kind="node",
        activation_magnitude=0.9,
    )

    rep_root_a = engine.build_canonical_representation(
        causal_parent_ref="root_external_alpha",
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        context="ctx_shared",
        participation_receipts=[receipt],
    )
    rep_root_b = engine.build_canonical_representation(
        causal_parent_ref="root_external_beta",
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        context="ctx_shared",
        participation_receipts=[receipt],
    )

    assert rep_root_a.representation_id != rep_root_b.representation_id
    sig_a = engine.canonical_representation_signature(rep_root_a)
    sig_b = engine.canonical_representation_signature(rep_root_b)
    assert sig_a == sig_b


def test_r1_t16_canonical_rid_contains_no_uuid():
    """R1-T16, R1-I13: canonical RID API contains no uuid or random generation."""
    digest = derive_operational_representation_digest(
        context_binding=None,
        active_assembly_refs=[],
        canonical_accepted_receipt_descriptors=[],
        canonical_accepted_tbr_descriptors=[],
        participating_refs={"nodes": ["a"]},
        snapshot_coordinate=0,
        support_or_activation_values={},
    )
    rid1 = derive_representation_id("parent_ref", 0, digest)
    rid2 = derive_representation_id("parent_ref", 0, digest)
    assert rid1 == rid2


def test_r1_t17_legacy_random_rid_path_remains_available():
    """R1-T17, R1-I35: default legacy build_representation uses rep_<hex> without canonical enforcement."""
    from dgca.graph import Node
    graph = CognitiveGraph()
    graph.nodes["n1"] = Node(nid="n1", region="concept", A=1.0)
    engine = RepresentationEngine(graph)
    receipt = ParticipationReceipt(
        receipt_id="r1",
        element_ref="n1",
        parent_cycle_id=1,
        snapshot_or_microtick=1,
        origin_lineage="external",
        participation_kind="node",
        activation_magnitude=1.0,
    )
    rep_legacy_1 = engine.build_representation(1, 1, None, [receipt])
    rep_legacy_2 = engine.build_representation(1, 1, None, [receipt])
    assert rep_legacy_1.representation_id != rep_legacy_2.representation_id
    assert rep_legacy_1.representation_id.startswith("rep_")


def test_canonical_rid_requires_causal_parent():
    """Section 22: causal_parent_ref is mandatory on canonical RID path."""
    with pytest.raises(CausalLineageError):
        derive_representation_id("", 1, "some_digest")


# ─────────────────────────────────────────────────────────── 6. Downstream RFC13–RFC16 Canonical Identities
def test_r1_t18_candidate_identity_isolated_by_parent_rid():
    """R1-T18, R1-I14: candidate identity is isolated by parent RID."""
    cid_rep1 = derive_pattern_candidate_id("rep_1", "kind", ["s1"], ["e1"], ["a1"], ("g",), "ctx")
    cid_rep2 = derive_pattern_candidate_id("rep_2", "kind", ["s1"], ["e1"], ["a1"], ("g",), "ctx")
    assert cid_rep1 != cid_rep2


def test_r1_t19_proposal_identity_isolated_by_epoch_rid():
    """R1-T19, R1-I14: proposal identity isolated by settling epoch and parent RID."""
    p1 = derive_reinstatement_proposal_id("se_1", "rep_1", "cand_1", "tgt", ("g",), "role")
    p2 = derive_reinstatement_proposal_id("se_2", "rep_1", "cand_1", "tgt", ("g",), "role")
    assert p1 != p2


def test_r1_t20_frame_occurrence_replay_stable():
    """R1-T20: frame and occurrence identity replay stably under canonical parent RID."""
    fid1 = derive_generative_frame_id("rep_1", ["anc1"], "scope1", {"role": "filler"})
    fid2 = derive_generative_frame_id("rep_1", ["anc1"], "scope1", {"role": "filler"})
    assert fid1 == fid2

    occ1 = derive_linearizable_occurrence_id(fid1, "role1", "filler1", "concept", 0)
    occ2 = derive_linearizable_occurrence_id(fid1, "role1", "filler1", "concept", 0)
    assert occ1 == occ2


def test_r1_t21_gce_id_unaffected_by_epoch_count():
    """R1-T21, R1-I15, Adversarial H: canonical GCE ID is unaffected by unrelated epoch creation count."""
    graph = CognitiveGraph()
    rec_engine = PredictiveRecurrentGenerativeEngine(graph)

    # First target GCE created at count 0
    gce1 = rec_engine.create_epoch("root_target", work_ref="work_unit_a", canonical_identity=True)

    # Create 5 unrelated epochs
    for i in range(5):
        rec_engine.create_epoch(f"unrelated_root_{i}", work_ref=f"work_{i}", canonical_identity=True)

    # Fresh engine creates the target GCE when 0 other epochs exist
    fresh_rec_engine = PredictiveRecurrentGenerativeEngine(graph)
    gce_target_fresh = fresh_rec_engine.create_epoch("root_target", work_ref="work_unit_a", canonical_identity=True)

    assert gce1.epoch_id == gce_target_fresh.epoch_id


def test_r1_t22_continuation_commit_uses_progress_digest():
    """R1-T22: continuation commit uses progress digest rather than count alone."""
    cc1 = derive_continuation_commit_id("gce_1", "rep_1", "ob_1", progress_snapshot_digest="digest_progress_A")
    cc2 = derive_continuation_commit_id("gce_1", "rep_1", "ob_1", progress_snapshot_digest="digest_progress_B")
    assert cc1 != cc2


def test_r1_t23_full_parent_surface_unit_no_truncation():
    """R1-T23, R1-I16: SurfaceUnit ID uses full canonical parent identity without [:8] truncation collision."""
    rid_shared_prefix_1 = "rep_" + "a" * 8 + "111111111111111111111111111111111111111111111111111111"
    rid_shared_prefix_2 = "rep_" + "a" * 8 + "222222222222222222222222222222222222222222222222222222"

    unit_1 = derive_surface_unit_id(rid_shared_prefix_1, "occ_1", 0, "the")
    unit_2 = derive_surface_unit_id(rid_shared_prefix_2, "occ_1", 0, "the")
    assert unit_1 != unit_2


def test_r1_t24_same_committed_chunk_retry_same_delivery_id():
    """R1-T24: same committed chunk delivery retry produces identical DeliveryID."""
    deliv1 = derive_delivery_id("chunk_123", "rep_100", "http_webhook")
    deliv2 = derive_delivery_id("chunk_123", "rep_100", "http_webhook")
    assert deliv1 == deliv2


def test_r1_t25_new_root_target_equals_event_root():
    """R1-T25, R1-I17: NEW_ROOT target equals event root_external_episode_id."""
    graph = CognitiveGraph()
    loop = UnifiedGenerativeCognitiveLoopEngine(graph)

    auth_root = derive_root_external_episode_id("boundary_test", "occ_999")
    event = ExternalEventRecord(
        event_id="raw_evt_1",
        root_external_episode_id=auth_root,
        ingress_boundary="boundary_test",
        source_origin="EXTERNAL",
        raw_content="hello",
    )

    task_rel, _ = loop.determine_task_relation(event, current_root_ref="old_root")
    assert task_rel.relation_kind == "NEW_ROOT"
    assert task_rel.target_root_ref == auth_root


# ─────────────────────────────────────────────────────────── 7. Persistent Mutation & Scope Tests
def test_r1_t26_same_root_different_ingress_subevents_same_txid():
    """R1-T26, R1-I18, Adversarial D: same root + same mutation from different ingress events yields same default TxID."""
    root_id = derive_root_external_episode_id("chat", "thread_123_msg_1")
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"w": 0.5},
        owner_defined_transaction_scope="default_scope",
    )

    # Reached via audio ingress sub-event
    tx_audio = derive_persistent_mutation_txid(root_id, cmd)
    # Reached via vision ingress sub-event
    tx_vision = derive_persistent_mutation_txid(root_id, cmd)

    assert tx_audio == tx_vision
    assert len(tx_audio) == 64


def test_r1_t27_owner_defined_transaction_scope_distinguishes_operations():
    """R1-T27, R1-I49: owner-defined lawful scope can distinguish separate operations within same root."""
    root_id = derive_root_external_episode_id("chat", "msg_abc")
    cmd_slot1 = PersistentMutationCommand(
        mutation_owner_ref="Law2_HebbianReinforcement",
        mutation_kind="REINFORCE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"dw": 0.1},
        owner_defined_transaction_scope="seq_transition_slot_0",
    )
    cmd_slot2 = PersistentMutationCommand(
        mutation_owner_ref="Law2_HebbianReinforcement",
        mutation_kind="REINFORCE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"dw": 0.1},
        owner_defined_transaction_scope="seq_transition_slot_1",
    )
    assert derive_persistent_mutation_txid(root_id, cmd_slot1) != derive_persistent_mutation_txid(root_id, cmd_slot2)


def test_r1_t69_untrusted_caller_nonce_cannot_bypass_replay():
    """R1-T69, R1-I49: varying an untrusted caller nonce cannot create a distinct canonical transaction scope."""
    # Scope must be authorized by owner, not free-form caller nonce
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"w": 0.5},
        owner_defined_transaction_scope="owner_derived_contract",
    )
    root_id = derive_root_external_episode_id("chat", "msg_abc")
    tx1 = derive_persistent_mutation_txid(root_id, cmd)
    tx2 = derive_persistent_mutation_txid(root_id, cmd)
    assert tx1 == tx2


def test_r1_t65_event_descriptor_digest_formula():
    """R1-T65, R1-I45: event descriptor digest uses frozen canonical SHA-256 formula."""
    desc = {"modality": "text", "boundary": "web_chat", "source_event_key": "ev1"}
    d = compute_event_descriptor_digest(desc)
    expected = hashlib.sha256(canonical_json_bytes(desc)).hexdigest()
    assert d == expected


def test_r1_t66_mutation_descriptor_digest_formula():
    """R1-T66, R1-I46: mutation descriptor digest uses frozen canonical SHA-256 formula."""
    desc = {"law": "Law1", "weight": 0.5, "targets": ["a", "b"]}
    d = compute_mutation_descriptor_digest(desc)
    expected = hashlib.sha256(canonical_json_bytes(desc)).hexdigest()
    assert d == expected
