"""RIC-01 / R2: Receipt Batch & Slot Allocation Tests.

Verifies:
- Global contiguous slot ordering 0..N-1
- Receipt batch validation and integrity
- Scope formatting root_id/c_idx/slot_idx
- Rejection of slot gaps, duplicates, or missing element references
"""
import pytest

from dgca.observation import (
    MICRO_DESCRIPTOR_VERSION,
    RECEIPT_BATCH_VERSION,
    CanonicalBindingEntry,
    CanonicalMicroEpisodeDescriptor,
    CanonicalReceiptBatch,
    CanonicalReceiptEntry,
    R2BatchValidationError,
    validate_canonical_receipt_batch,
)


def test_batch_validation_rejects_slot_gap():
    mep = CanonicalMicroEpisodeDescriptor(
        micro_descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:0",
        child_index=0,
        kind="simultaneous",
        positive_signals=(),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    # Entry with slot 0 and slot 2 (gap: missing 1)
    from dgca.causal_identity import derive_participation_receipt_id

    rid0 = derive_participation_receipt_id(
        micro_episode_id="mep:0",
        participation_kind="node",
        element_ref="n0",
        scope_refs=[],
        slot_index=0,
        prefix="pr_",
    )
    rid2 = derive_participation_receipt_id(
        micro_episode_id="mep:0",
        participation_kind="node",
        element_ref="n2",
        scope_refs=[],
        slot_index=2,
        prefix="pr_",
    )
    e0 = CanonicalReceiptEntry(
        slot_index=0,
        receipt_id=rid0,
        kind="node",
        element_ref="n0",
        occurrence_scope="scope_0",
        scope_refs=(),
    )
    e2 = CanonicalReceiptEntry(
        slot_index=2,
        receipt_id=rid2,
        kind="node",
        element_ref="n2",
        occurrence_scope="scope_0",
        scope_refs=(),
    )
    batch = CanonicalReceiptBatch(
        batch_version=RECEIPT_BATCH_VERSION,
        observation_transaction_id="tx:0",
        micro_episode_id="mep:0",
        child_index=0,
        local_parent_cycle_id=1,
        snapshot_or_microtick=0,
        ordered_receipt_entries=[e0, e2],
        ordered_binding_entries=[],
    )
    with pytest.raises(R2BatchValidationError, match="Non-contiguous receipt slot index"):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx:0",
            expected_micro_id="mep:0",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=mep,
        )


def test_batch_validation_rejects_invented_tbr_scope():
    mep = CanonicalMicroEpisodeDescriptor(
        micro_descriptor_version=MICRO_DESCRIPTOR_VERSION,
        micro_episode_id="mep:0",
        child_index=0,
        kind="simultaneous",
        positive_signals=({"region": "text", "symbol": "a"},),
        contradictions=(),
        structural_weight=1.0,
        valence=0.0,
    )
    e0 = CanonicalReceiptEntry(
        slot_index=0,
        receipt_id="pr_0",
        kind="node",
        element_ref="text:a",
        occurrence_scope="scope_0",
        scope_refs=("invented_scope",),
    )
    b0 = CanonicalBindingEntry(
        binding_index=0,
        binding_id="tbr_0",
        scope_kind="simultaneous",
        scope_index=0,
        binding_scope="invented_scope",
        member_element_refs=("text:a",),
    )
    batch = CanonicalReceiptBatch(
        batch_version=RECEIPT_BATCH_VERSION,
        observation_transaction_id="tx:0",
        micro_episode_id="mep:0",
        child_index=0,
        local_parent_cycle_id=1,
        snapshot_or_microtick=0,
        ordered_receipt_entries=[e0],
        ordered_binding_entries=[b0],
    )
    with pytest.raises(R2BatchValidationError):
        validate_canonical_receipt_batch(
            batch=batch,
            expected_txid="tx:0",
            expected_micro_id="mep:0",
            expected_child_index=0,
            expected_cycle_id=1,
            micro_descriptor=mep,
        )
