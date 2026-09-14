"""RIC-01 / R2: RFC-11 Evidence Eligibility & Firewall Tests.

Verifies:
- Simultaneous ordered non-self pairs are RFC-11 eligible
- Sequence same-step & adjacent-step pairs are RFC-11 eligible
- Sequence nonadjacent temporal pairs (dist >= 2) are EXCLUDED from RFC-11 eligibility
- Role edges (ev:), category edges (cat:), concept edges (hub:), and instance edges (inst:)
  are strictly excluded from RFC-11 eligibility
"""
from dgca.causal_identity import (
    CanonicalR1RuntimeRoot,
    CausalCommitLedger,
    create_native_r1_provenance_epoch,
)
from dgca.graph import CognitiveGraph
from dgca.observation import (
    MICRO_DESCRIPTOR_VERSION,
    CanonicalMicroEpisodeDescriptor,
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


def test_rfc11_sequence_adjacent_vs_nonadjacent():
    bridge = _make_bridge()
    # Sequence with 3 steps: step 0 (A), step 1 (B), step 2 (C)
    step0 = ({"region": "text", "symbol": "A"},)
    step1 = ({"region": "text", "symbol": "B"},)
    step2 = ({"region": "text", "symbol": "C"},)
    
    mep = CanonicalMicroEpisodeDescriptor(
        micro_descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:seq_test",
        child_index=0,
        kind="sequence",
        positive_signals=(),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
        steps=(step0, step1, step2),
    )

    eligible = bridge._derive_rfc11_eligible_edges(mep)
    
    # Adjacent pairs (A->B, dist 1) and (B->C, dist 1) must be eligible
    assert ("text:A", "text:B") in eligible
    assert ("text:B", "text:C") in eligible
    
    # Non-adjacent pair (A->C, dist 2) MUST NOT be eligible for RFC-11
    assert ("text:A", "text:C") not in eligible


def test_rfc11_firewall_excludes_role_cat_hub_inst():
    bridge = _make_bridge()
    assert bridge._is_excluded_rfc11_edge("ev:occurrence_01", "text:apple") is True
    assert bridge._is_excluded_rfc11_edge("text:apple", "cat:fruit") is True
    assert bridge._is_excluded_rfc11_edge("hub:concept_red", "text:apple") is True
    assert bridge._is_excluded_rfc11_edge("inst:item_01", "text:apple") is True
    assert bridge._is_excluded_rfc11_edge("text:apple", "text:sweet") is False
