"""
DGCA — RIC-01 / R1-PIR-03: Final Runtime Encapsulation & Identity Strictness Repair
Verification and Acceptance Test Suite (T01 through T19)

Authoritative specification: RIC-01-R1-Deterministic-Causal-Identity-Protocol-v1.3-FROZEN.md
Trigger: RIC-01-R1-PIR-02-FINAL-INDEPENDENT-CLOSURE-AUDIT-v1.0.md
"""
from __future__ import annotations

import json

import pytest

from dgca.assembly import AssemblyPolicy
from dgca.causal_identity import (
    CAUSAL_IDENTITY_PROTOCOL_DIGEST,
    CanonicalLineageState,
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    CausalIdentityValidationError,
    CausalLedgerInspectionView,
    CausalProvenanceEpoch,
    CognitiveGraphInspectionView,
    PersistentMutationCommand,
    compute_causal_provenance_digest,
    compute_checkpoint_bundle_digest,
    create_migrated_r1_provenance_epoch,
    create_native_r1_provenance_epoch,
    derive_causal_provenance_epoch_id,
)
from dgca.config import Law
from dgca.graph import CognitiveGraph
from dgca.persistence import (
    RuntimeLifecycleGuard,
    build_canonical_r1_checkpoint,
    compute_checkpoint_state_digest,
    extract_canonical_persistent_payload,
    restore_canonical_r1_checkpoint,
    save_canonical_r1_checkpoint,
)


@pytest.fixture
def clean_graph():
    return CognitiveGraph()


@pytest.fixture
def clean_guard():
    return RuntimeLifecycleGuard()


@pytest.fixture
def sample_runtime(clean_graph, clean_guard):
    state_digest = compute_checkpoint_state_digest(
        extract_canonical_persistent_payload(clean_graph, AssemblyPolicy())
    )
    epoch = create_native_r1_provenance_epoch(state_digest)
    ledger = CausalCommitLedger(epoch=epoch)
    return CanonicalR1RuntimeRoot(
        graph=clean_graph,
        ledger=ledger,
        observation_protocol_version="1.0.0",
        lifecycle_guard=clean_guard,
    )


def _recompute_checkpoint_integrity(data: dict) -> None:
    prov_bytes = compute_causal_provenance_digest(data["causal_provenance_state"])
    data["integrity"]["causal_provenance_digest"] = prov_bytes
    data["integrity"]["checkpoint_bundle_digest"] = compute_checkpoint_bundle_digest(
        checkpoint_state_digest=data["integrity"]["checkpoint_state_digest"],
        causal_provenance_digest=prov_bytes,
        combined_semantics_digest=data["compatibility"]["combined_semantics_digest"],
        causal_identity_protocol_digest=CAUSAL_IDENTITY_PROTOCOL_DIGEST,
        observation_protocol_digest=data["compatibility"]["observation_protocol_digest"],
        causal_provenance_epoch=data["causal_provenance_state"]["causal_provenance_epoch"],
    )


# ─────────────────────────────────────────────────────────── PIR03-B01: Safe Canonical Inspection Detachment (T01 - T09)

def test_pir03_t01_runtime_graph_remains_inspection_view_inside_mutator(sample_runtime):
    """PIR03-T01: runtime.graph and runtime.ledger remain detached inspection views inside mutator callback."""
    observed_graph_type = None
    observed_ledger_type = None

    def callback():
        nonlocal observed_graph_type, observed_ledger_type
        observed_graph_type = type(sample_runtime.graph)
        observed_ledger_type = type(sample_runtime.ledger)
        sample_runtime.graph.link("a", "b", W=Law.W_BASE)

    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["a", "b"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_ep_1",
        ingress_event_id="evt_1",
        event_descriptor_digest="a" * 64,
        mutator_callback=callback,
    )

    assert observed_graph_type is CognitiveGraphInspectionView
    assert observed_ledger_type is CausalLedgerInspectionView
    assert isinstance(sample_runtime.graph, CognitiveGraphInspectionView)
    assert isinstance(sample_runtime.ledger, CausalLedgerInspectionView)


def test_pir03_t02_node_members_mutation_cannot_affect_live_node(sample_runtime):
    """PIR03-T02: Returned Node.members mutation cannot affect the live CognitiveGraph node."""
    raw_g = sample_runtime.unsafe_mutable_graph()
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID
    live_node = raw_g.node("concept:test", region="central")
    live_node.members.add("live_member_1")

    # Access via property
    inspect_node = sample_runtime.graph.node("concept:test")
    inspect_node.members.add("leak_candidate")

    # Verify live node is untouched
    assert "leak_candidate" not in raw_g.nodes["concept:test"].members
    assert "leak_candidate" not in sample_runtime.graph.nodes["concept:test"].members
    assert "live_member_1" in raw_g.nodes["concept:test"].members


def test_pir03_t03_edge_contexts_mutation_cannot_affect_live_edge(sample_runtime):
    """PIR03-T03: Returned Edge.contexts mutation cannot affect the live Edge."""
    raw_g = sample_runtime.unsafe_mutable_graph()
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID
    raw_g.link("u", "v", W=Law.W_BASE, contexts={"ctx_initial"})

    inspect_edge = sample_runtime.graph.edge("u", "v")
    inspect_edge.contexts.add("ctx_leaked")

    assert "ctx_leaked" not in raw_g.edges[("u", "v")].contexts
    assert "ctx_leaked" not in sample_runtime.graph.edge("u", "v").contexts
    assert "ctx_initial" in raw_g.edges[("u", "v")].contexts


def test_pir03_t04_edge_ctx_hits_mutation_cannot_affect_live_edge(sample_runtime):
    """PIR03-T04: Returned Edge.ctx_hits mutation cannot affect the live Edge."""
    raw_g = sample_runtime.unsafe_mutable_graph()
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID
    raw_g.link("u", "v", W=Law.W_BASE)
    live_edge = raw_g.edges[("u", "v")]
    live_edge.ctx_hits["ctx_1"] = 5

    inspect_edge = sample_runtime.graph.edges[("u", "v")]
    inspect_edge.ctx_hits["ctx_1"] = 9999
    inspect_edge.ctx_hits["ctx_new"] = 1

    assert raw_g.edges[("u", "v")].ctx_hits["ctx_1"] == 5
    assert "ctx_new" not in raw_g.edges[("u", "v")].ctx_hits
    assert sample_runtime.graph.edges[("u", "v")].ctx_hits["ctx_1"] == 5


def test_pir03_t05_inspection_view_exposes_no_live_assembly_manager(sample_runtime):
    """PIR03-T05: CognitiveGraphInspectionView exposes no _assembly_manager property."""
    assert not hasattr(sample_runtime.graph, "_assembly_manager")
    with pytest.raises(AttributeError):
        _ = sample_runtime.graph._assembly_manager


def test_pir03_t06_inspection_view_exposes_no_rfc12_to_rfc16_engine_objects(sample_runtime):
    """PIR03-T06: CognitiveGraphInspectionView exposes no RFC12-RFC16 engine objects."""
    engines = [
        "_representation_engine",
        "_completion_engine",
        "_generation_engine",
        "_recurrent_engine",
        "_loop_engine",
    ]
    for engine_prop in engines:
        assert not hasattr(sample_runtime.graph, engine_prop)
        with pytest.raises(AttributeError):
            _ = getattr(sample_runtime.graph, engine_prop)


def test_pir03_t07_ledger_inspection_exposes_no_commit_or_mutation_method(sample_runtime):
    """PIR03-T07: CausalLedgerInspectionView exposes no commit_transaction method."""
    assert not hasattr(sample_runtime.ledger, "commit_transaction")
    with pytest.raises(AttributeError):
        _ = sample_runtime.ledger.commit_transaction


def test_pir03_t08_unsafe_graph_access_invalidates_lineage_before_return(sample_runtime):
    """PIR03-T08: runtime.unsafe_mutable_graph() invalidates canonical_lineage_state before return."""
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.VALID
    g = sample_runtime.unsafe_mutable_graph()
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
    assert isinstance(g, CognitiveGraph)


def test_pir03_t09_unsafe_ledger_access_invalidates_lineage_before_return(sample_runtime):
    """PIR03-T09: runtime.unsafe_mutable_ledger() invalidates canonical_lineage_state before return."""
    sample_runtime.canonical_lineage_state = CanonicalLineageState.VALID
    l = sample_runtime.unsafe_mutable_ledger()
    assert sample_runtime.canonical_lineage_state == CanonicalLineageState.INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
    assert isinstance(l, CausalCommitLedger)


# ─────────────────────────────────────────────────────────── PIR03-B02: Provenance Epoch Fail-Closed Construction (T10 - T14)

def test_pir03_t10_native_epoch_factory_succeeds():
    """PIR03-T10: create_native_r1_provenance_epoch constructs valid epoch with deterministic epoch_id."""
    digest = "1" * 64
    epoch = create_native_r1_provenance_epoch(digest)
    expected_id = derive_causal_provenance_epoch_id(digest, "1.2.0", "1.0", prefix="cpe_")
    assert epoch.epoch_id == expected_id
    assert epoch.history_status == "R1_TRACKED"
    assert epoch.base_state_digest == digest


def test_pir03_t11_migrated_epoch_factory_succeeds():
    """PIR03-T11: create_migrated_r1_provenance_epoch constructs valid migrated epoch."""
    digest = "2" * 64
    epoch = create_migrated_r1_provenance_epoch(digest)
    expected_id = derive_causal_provenance_epoch_id(digest, "1.1.1", "1.0", prefix="cpe_")
    assert epoch.epoch_id == expected_id
    assert epoch.history_status == "PRE_R1_HISTORY_UNAVAILABLE"
    assert epoch.base_state_digest == digest


def test_pir03_t12_arbitrary_direct_epoch_id_construction_fails():
    """PIR03-T12: Direct construction of CausalProvenanceEpoch with arbitrary epoch_id fails closed."""
    digest = "3" * 64
    with pytest.raises(CausalIdentityValidationError):
        CausalProvenanceEpoch("custom_user_epoch_id", "R1_TRACKED", digest)

    with pytest.raises(CausalIdentityValidationError):
        CausalProvenanceEpoch("cpe_arbitrary_hash", "R1_TRACKED", digest)


def test_pir03_t13_tampered_persisted_epoch_id_fails_restore(sample_runtime, tmp_path):
    """PIR03-T13: Checkpoint containing tampered epoch_id fails closed during restore."""
    cp_path = tmp_path / "tampered_epoch.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    data["causal_provenance_state"]["causal_provenance_epoch"]["epoch_id"] = "cpe_" + "e" * 64
    _recompute_checkpoint_integrity(data)
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CausalIdentityValidationError, match="Provenance epoch_id mismatch"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir03_t14_checkpoint_build_cannot_normalize_corrupted_epoch(sample_runtime):
    """PIR03-T14: build_canonical_r1_checkpoint fails closed when ledger epoch is corrupted."""
    object.__setattr__(sample_runtime._ledger.epoch, "epoch_id", "cpe_" + "9" * 64)
    with pytest.raises(CausalIdentityValidationError, match="Provenance epoch_id mismatch"):
        build_canonical_r1_checkpoint(
            sample_runtime._graph,
            sample_runtime._ledger,
            observation_protocol_version="1.0.0",
        )


# ─────────────────────────────────────────────────────────── PIR03-B03: Exact 64 Lowercase Hex TxID Validation (T15 - T19)

def test_pir03_t15_valid_64_lowercase_hex_txid_restores(sample_runtime, tmp_path):
    """PIR03-T15: Checkpoint with authoritative 64 lowercase hex TxID restores cleanly."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_ep_1",
        ingress_event_id="evt_1",
        event_descriptor_digest="f" * 64,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "valid_tx.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    restored, _ = restore_canonical_r1_checkpoint(
        cp_path,
        expected_observation_protocol_version="1.0.0",
    )
    assert len(restored.ledger.committed_transactions) == 1


def test_pir03_t16_uppercase_txid_rejected(sample_runtime, tmp_path):
    """PIR03-T16: Transaction-ID containing uppercase hex fails closed on restore."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_ep_1",
        ingress_event_id="evt_1",
        event_descriptor_digest="f" * 64,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "upper_tx.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    txs = data["causal_provenance_state"]["committed_transactions"]
    orig_txid = next(iter(txs.keys()))
    upper_txid = orig_txid.upper()
    rec = txs.pop(orig_txid)
    rec["transaction_id"] = upper_txid
    txs[upper_txid] = rec
    _recompute_checkpoint_integrity(data)
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CausalIdentityValidationError, match="invalid authoritative TxID digest shape"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir03_t17_evil_prefix_64hex_txid_rejected(sample_runtime, tmp_path):
    """PIR03-T17: Transaction-ID with evil_<64hex> prefix fails closed on restore."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_ep_1",
        ingress_event_id="evt_1",
        event_descriptor_digest="f" * 64,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "evil_tx.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    txs = data["causal_provenance_state"]["committed_transactions"]
    orig_txid = next(iter(txs.keys()))
    evil_txid = f"evil_{orig_txid}"
    rec = txs.pop(orig_txid)
    rec["transaction_id"] = evil_txid
    txs[evil_txid] = rec
    _recompute_checkpoint_integrity(data)
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CausalIdentityValidationError, match="invalid authoritative TxID digest shape"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir03_t18_tx_prefix_64hex_txid_rejected(sample_runtime, tmp_path):
    """PIR03-T18: Transaction-ID with tx_<64hex> prefix fails closed on restore."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_ep_1",
        ingress_event_id="evt_1",
        event_descriptor_digest="f" * 64,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "prefix_tx.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    txs = data["causal_provenance_state"]["committed_transactions"]
    orig_txid = next(iter(txs.keys()))
    prefixed_txid = f"tx_{orig_txid}"
    rec = txs.pop(orig_txid)
    rec["transaction_id"] = prefixed_txid
    txs[prefixed_txid] = rec
    _recompute_checkpoint_integrity(data)
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CausalIdentityValidationError, match="invalid authoritative TxID digest shape"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")


def test_pir03_t19_malformed_length_txid_rejected(sample_runtime, tmp_path):
    """PIR03-T19: Transaction-ID with non-64 length fails closed on restore."""
    cmd = PersistentMutationCommand(
        mutation_owner_ref="Law1_HebbianCreation",
        mutation_kind="CREATE_EDGE",
        canonical_targets=["n1", "n2"],
        canonical_mutation_descriptor={"weight": Law.W_BASE},
        owner_defined_transaction_scope="scope",
    )
    sample_runtime.execute_persistent_command(
        command=cmd,
        root_external_episode_id="root_ep_1",
        ingress_event_id="evt_1",
        event_descriptor_digest="f" * 64,
        mutator_callback=lambda: None,
    )
    cp_path = tmp_path / "short_tx.json"
    save_canonical_r1_checkpoint(sample_runtime, cp_path)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    txs = data["causal_provenance_state"]["committed_transactions"]
    orig_txid = next(iter(txs.keys()))
    short_txid = orig_txid[:-1]  # 63 hex chars
    rec = txs.pop(orig_txid)
    rec["transaction_id"] = short_txid
    txs[short_txid] = rec
    _recompute_checkpoint_integrity(data)
    cp_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CausalIdentityValidationError, match="invalid authoritative TxID digest shape"):
        restore_canonical_r1_checkpoint(cp_path, expected_observation_protocol_version="1.0.0")