# DGCA — RIC-01 / R0-C01

## Persistence Closure Correction

# Formal Correction Specification v1.0 — FROZEN

**Project:** DGCA
**Parent Program:** RIC-01 — Canonical Runtime Integration Contract
**Parent Stage:** R0 — Persistence & Runtime Lifecycle
**Parent Implementation Commit:** `fb3b870824b9141abf67857e07b66c36e0bb8938`
**Trigger:** `RIC01_R0_POST_IMPLEMENTATION_AUDIT_FAIL`
**Status:** FROZEN
**Scope:** Correction-only. No R1/R2/R3 work is authorized.

---

# 1. Purpose

R0-C01 closes five defects found by the independent post-implementation audit of R0:

1. RFC-11 formation-candidate storage-key loss across restore.
2. AssemblyPolicy provenance mismatch between graph state and checkpoint fingerprint.
3. Runtime root swap occurring after the RESTORING guard has already returned to IDLE.
4. Incomplete compatibility validation for `runtime_contract_version` and `combined_semantics_digest`.
5. Ordered durable sequences being reordered during canonicalization.

No cognitive law, learning rule, threshold, encoder, reasoning, generation, vision, audio, or agent behavior may change.

---

# 2. Correction Principle

The correction MUST preserve:
* cognitive semantics
* learned graph state
* RFC-11 semantics
* baseline cognitive signature (`915119d40643cb97`)
* R0 durable/transient ownership classes

and change only persistence/lifecycle correctness.

The required post-correction verdict is:
`RIC01_R0_C01_IMPLEMENTATION_VERIFIED`
followed by a new independent audit before R0 may be closed.

---

# C01-01 — Preserve the True RFC-11 Formation Candidate Storage Key

## 3. Problem
Production RFC-11 stores formation candidates under:
`cand_key = f"{canonical_assembly_id(comp)}:ctx_{context or 'default'}"`
while the candidate object contains:
`candidate_id = canonical_assembly_id(comp)`
`context_signature = context`

Therefore the dictionary storage key is not equal to `candidate_id`.
The R0 implementation serialized candidate content but did not serialize the authoritative dictionary key, and restored candidates under:
`pending_candidates[candidate_id] = candidate`
This breaks context-separated pending evidence continuity.

## 4. Binding Fix
Every serialized pending formation candidate MUST include:
* `storage_key`
* `candidate_id`
* `context_signature`
* `created_t`
* `edges`
* `root_votes`

`storage_key` MUST be restored exactly as the dictionary key.
The canonical expected key is:
`expected_key = f"{candidate_id}:ctx_{context_signature or 'default'}"`

Save-time and restore-time validation MUST require:
`storage_key == expected_key`
If not: FAIL CLOSED. No heuristic repair during normal canonical restore.

## 5. Context Separation Invariant
For identical edge components: context A and context B must remain two distinct pending formation records before and after save/restore.
Required invariant:
`(candidate_id same) AND (context differs) -> storage_key differs -> vote sets remain isolated`
No overwrite, merge, or cross-context vote leakage is permitted.

## 6. Real RFC-11 Continuity Acceptance Test
The correction MUST include a production-path test using `AssemblyManager.record_participation()` rather than manually inserting fixture candidates.
Required sequence:
same connected eligible edge component
root_1 -> accepted vote
root_2 -> accepted vote
root_3 -> accepted vote
root_4 -> accepted vote
SAVE
RESTORE
root_5 -> accepted vote

Expected:
* exactly one `StructuralAssembly` forms
* pending formation record is removed after lawful commit
* assembly formation occurs on the fifth independent root vote

## 7. Cross-Context Production Test
Using `record_participation()`:
* component E, context A -> 4 independent votes
* component E, context B -> 3 independent votes
* SAVE & RESTORE
Expected:
* two distinct pending formation candidates
* A retains exactly 4 votes, B retains exactly 3 votes
Then:
* context A + fifth vote
Expected:
* A commits exactly once
* B remains pending with 3 votes

---

# C01-02 — Policy Provenance Must Match the State That Produced It

## 8. Effective Policy Rule
Define one authoritative effective policy for checkpointing:
```python
if graph._assembly_manager is not None:
    effective_policy = graph._assembly_manager.policy
elif explicit_policy is not None:
    effective_policy = explicit_policy
else:
    effective_policy = AssemblyPolicy()
```
If both graph manager policy and explicit policy exist, they MUST be semantically identical across the complete authoritative policy payload. Otherwise: `CheckpointCompatibilityError` before any checkpoint is written.

## 9. RuntimeRoot Policy Rule
RuntimeRoot MUST NOT silently create a default policy that disagrees with an already-instantiated graph AssemblyManager.
Required:
```python
if explicit_policy is not None:
    if graph._assembly_manager is not None and not policies_semantically_equal(graph._assembly_manager.policy, explicit_policy):
        raise CheckpointCompatibilityError(...)
    self.policy = explicit_policy
elif graph._assembly_manager is not None:
    self.policy = graph._assembly_manager.policy
else:
    self.policy = AssemblyPolicy()
```
On successful restore, the newly created AssemblyManager MUST use the RuntimeRoot authoritative policy.

## 10. Policy Equality
Policy semantic equality MUST compare exactly:
`policy_version`, `K_ASM_MIN`, `N_ASM_CONFIRM`, `A_MAX`, `K_ASM_MEM`, `K_ASM_ACTIVE`, `K_STRUCT_PENDING`. Object identity is irrelevant.

---

# C01-03 — Root Swap Must Occur While Lifecycle State Is RESTORING

## 11. Binding Lifecycle Fix
The complete host-level restore transaction MUST be:
`IDLE -> RESTORING -> Phase A prepare new graph -> validate all postconditions -> root swap while still RESTORING -> IDLE`

There MUST be no observable IDLE state between prepare and swap.
Implementation MUST avoid nested lifecycle contexts that let an inner context reset the shared guard to IDLE while an outer restore is still active.

Preferred decomposition:
* `_prepare_restore_checkpoint(...)` # no lifecycle transition
* `restore_cognitive_checkpoint(...)` # guarded wrapper
* `RuntimeRoot.restore_checkpoint(...)` # one guard around prepare + swap

Mandatory test: at the exact root-swap point: `guard.state == RESTORING`.
After success: `guard.state == IDLE`.
On prepare failure: old root graph remains object-identical, `guard.state == IDLE`.

---

# C01-04 — Complete Compatibility Validation

## 12. Required Compatibility Checks
Canonical restore MUST validate all of:
* `checkpoint_schema_version`
* `runtime_contract_version`
* `cognitive_semantics_version`
* `region_schema_digest`
* `active_law_digest`
* `assembly_policy_digest`
* `combined_semantics_digest`
* `checkpoint_state_digest`

Restore MUST recompute `combined_semantics_digest` and compare it explicitly.
Tampering only the combined digest MUST fail closed (`CheckpointCompatibilityError`).

---

# C01-05 — Ordered Durable Sequences Must Preserve Order

## 13. Hypotheses
`graph.hypotheses` is an ordered list. R0-C01 freezes: hypotheses list order is durable. Do NOT sort the hypotheses list during canonical extraction.

## 14. Parent Assembly Lineage
`StructuralAssembly.parent_assemblies` is an ordered tuple. R0-C01 freezes: parent_assemblies order is durable. Do NOT sort it during serialization.

---

# C01-06 — Corrected Checkpoint Schema and Migration

## 15. Schema Version
Corrected checkpoints MUST use:
* `checkpoint_schema_version = "1.1.1"`
* `runtime_contract_version = "1.1.1"`
* `cognitive_semantics_version = "1.0"`

## 16. Schema 1.1 -> 1.1.1 Migration
Existing canonical R0 schema 1.1 checkpoint files are migratable.
For every old formation record derive:
`storage_key = f"{candidate_id}:ctx_{context_signature or 'default'}"`
Migration MUST fail closed if two records derive the same storage key and the input is ambiguous or non-identical. Do NOT silently union vote sets.
Migration diagnostics MUST state that formation storage keys were reconstructed deterministically.

## 17. Legacy 1.0 Migration
Legacy v1.0 migration remains supported and now targets 1.1.1. Explicit loss rule remains: RFC-11 pending structural evidence was not serialized and cannot be recovered.

---

# 18. Correction Invariants
* C01-I01  Formation storage keys survive exactly.
* C01-I02  Same component in different contexts remains distinct.
* C01-I03  4 votes + restart + fifth vote forms exactly one assembly.
* C01-I04  Pending context B remains unchanged when context A commits.
* C01-I05  Checkpoint policy equals graph structural-state policy.
* C01-I06  RuntimeRoot adopts existing manager policy when no explicit policy is supplied.
* C01-I07  Policy mismatch fails before checkpoint replacement.
* C01-I08  Root swap occurs while guard state is RESTORING.
* C01-I09  No nested guard exposes IDLE before root swap.
* C01-I10  runtime_contract_version is validated.
* C01-I11  combined_semantics_digest is validated.
* C01-I12  Hypothesis list order survives exactly.
* C01-I13  parent_assemblies tuple order survives exactly.
* C01-I14  Existing schema 1.1 checkpoints migrate deterministically to 1.1.1.
* C01-I15  Cognitive baseline signature remains unchanged.

---

# 19. Required Tests
* C01-T01 real RFC11 4+restart+1 formation continuity
* C01-T02 two-context candidate separation across restart
* C01-T03 context A commit does not mutate context B votes
* C01-T04 formation storage-key round-trip exactness
* C01-T05 save policy mismatch fails closed
* C01-T06 RuntimeRoot adopts manager policy
* C01-T07 incompatible restore policy fails closed
* C01-T08 root swap observed while RESTORING
* C01-T09 failed prepare preserves old root and returns guard to IDLE
* C01-T10 tampered runtime_contract_version fails closed
* C01-T11 tampered combined_semantics_digest fails closed
* C01-T12 hypothesis list order exact
* C01-T13 parent_assemblies order exact
* C01-T14 schema 1.1 formation-key migration
* C01-T15 schema 1.1 duplicate-derived-key conflict fails closed
* C01-T16 legacy 1.0 migration still passes
* C01-T17 corrected repeated-save digest deterministic
* C01-T18 full original R0 test suite passes
* C01-T19 full repository regression passes
* C01-T20 baseline signature unchanged

---

# 20. Final Verdict Vocabulary
`RIC01_R0_C01_IMPLEMENTATION_VERIFIED`
