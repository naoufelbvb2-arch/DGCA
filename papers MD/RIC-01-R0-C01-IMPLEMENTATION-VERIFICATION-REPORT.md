# DGCA — RIC-01 / R0-C01 Implementation & Verification Report

## Stage: R0-C01 — Persistence Closure Correction
**Authoritative Specification:** `RIC-01-R0-C01-Persistence-Closure-Correction-v1.0-FROZEN.md`  
**Master Prompt:** `DGCA — RIC-01 / R0-C01 Strict Correction Implementation & Verification Master Prompt v1.0 — FROZEN`  
**Parent Program:** RIC-01 — Canonical Runtime Integration Contract  
**Parent Stage:** R0 — Persistence & Runtime Lifecycle  
**Parent Implementation Commit:** `fb3b870824b9141abf67857e07b66c36e0bb8938`  
**Trigger:** `RIC01_R0_POST_IMPLEMENTATION_AUDIT_FAIL`  
**Execution Date:** 2026-09-13  
**Execution Mode:** Strict Correction Implementation & Verification  
**Scope:** R0-C01 Only (No R1/R2/R3 authorization)  

---

## 1. Baseline
* **Starting Commit:** `fb3b870824b9141abf67857e07b66c36e0bb8938`
* **Branch:** `main`
* **Pre-correction Test Result:** 2,513 passed in 11.27s, 0 failures.
* **Authoritative Baseline Cognitive Signature:** `915119d40643cb97` (`tests/baseline_signature.txt`).
* **Clean Working Tree:** Verified prior to edits.

---

## 2. Files Created & Modified
1. `dgca/persistence.py` (Modified):
   - Implemented `storage_key` preservation and validation for RFC-11 pending formation candidates.
   - Implemented `policies_semantically_equal` across the 7 authoritative policy fields.
   - Implemented `resolve_effective_policy` enforcing manager priority and failing closed on mismatch.
   - Updated `RuntimeRoot` policy adoption and validation logic.
   - Decomposed restore into Phase A `_prepare_restored_cognitive_graph` and guarded wrapper `restore_cognitive_checkpoint`.
   - Refactored `RuntimeRoot.restore_checkpoint` so that `self.guard.restoring()` encompasses prepare, validation, and the authoritative `self.graph = new_graph` swap.
   - Updated schema versioning to `1.1.1` (`checkpoint_schema_version = "1.1.1"`, `runtime_contract_version = "1.1.1"`, `cognitive_semantics_version = "1.0"`).
   - Added complete compatibility validation: explicit `runtime_contract_version` checking and recomputed `combined_semantics_digest` validation.
   - Preserved exact sequence ordering for `graph.hypotheses` (list) and `StructuralAssembly.parent_assemblies` (tuple).
   - Implemented `migrate_schema_1_1_to_1_1_1` with deterministic key derivation and fail-closed conflict handling.
   - Updated `migrate_legacy_v1_checkpoint` to target schema `1.1.1`.
2. `dgca/__init__.py` (Modified):
   - Exported `migrate_schema_1_1_to_1_1_1` and `policies_semantically_equal`.
3. `tests/test_ric01_r0_persistence.py` (Modified):
   - Updated formation fixture assertions to use canonical `storage_key`.
4. `tests/test_ric01_r0_c01_correction.py` (Created):
   - Dedicated R0-C01 test suite covering all 15 Invariants (`C01-I01`..`C01-I15`) and 20 Acceptance Tests (`C01-T01`..`C01-T20`), including end-to-end production RFC-11 participation tests.
5. `papers MD/RIC-01-R0-C01-Persistence-Closure-Correction-v1.0-FROZEN.md` (Created):
   - Authoritative frozen correction specification.
6. `RIC-01-R0-C01-IMPLEMENTATION-VERIFICATION-REPORT.md` (Created):
   - Authoritative verification report.

Zero lines modified outside persistence and lifecycle testing. No cognitive laws, learning rules, encoders, or R1/R2/R3 code touched.

---

## 3. Defects Closed

### Defect 1: RFC-11 Formation-Candidate Storage-Key Loss Across Restore
* **Problem:** In RFC-11 (`dgca/assembly.py`), formation candidates are keyed in `pending_candidates` by `cand_key = f"{canonical_assembly_id(comp)}:ctx_{context or 'default'}"`, which differs from `candidate.candidate_id` when context is present. R0 serialized only `candidate_id` and restored into `pending_candidates[candidate_id]`, collapsing distinct context-separated candidates and corrupting pending evidence continuity.
* **Correction:**
  - Added `storage_key` to `SerializedFormationCandidate`.
  - Enforced `expected_key = f"{candidate_id}:ctx_{context_signature or 'default'}"`.
  - Save and restore strictly validate `storage_key == expected_key`; any mismatch fails closed (`CheckpointValidationError`).
  - Restored under `new_mgr.pending_candidates[storage_key] = candidate`.
  - Invariant verified: `(candidate_id same) AND (context differs) -> storage_key differs -> vote sets remain isolated`.

### Defect 2: AssemblyPolicy Provenance Mismatch
* **Problem:** If a caller passed an explicit policy to `save_cognitive_checkpoint` or `RuntimeRoot` that disagreed with the policy attached to `graph._assembly_manager`, the checkpoint digest could be computed from an unrepresentative policy. Furthermore, `RuntimeRoot.__init__` defaulted to `AssemblyPolicy()` even if the graph had a manager with custom policy settings.
* **Correction:**
  - Implemented `policies_semantically_equal(p1, p2)` strictly comparing: `policy_version`, `K_ASM_MIN`, `N_ASM_CONFIRM`, `A_MAX`, `K_ASM_MEM`, `K_ASM_ACTIVE`, `K_STRUCT_PENDING`.
  - Implemented `resolve_effective_policy(graph, explicit_policy)`: if graph manager exists, its policy is authoritative. If explicit policy also provided and differs, fail closed with `CheckpointCompatibilityError`.
  - `RuntimeRoot` adopts `graph._assembly_manager.policy` when no explicit policy is provided, and validates equality when an explicit policy is provided.

### Defect 3: Runtime Root Swap Outside RESTORING Guard
* **Problem:** In R0, `restore_cognitive_checkpoint` was decorated with `@guard.restoring()`, which transitioned `guard.state` back to `IDLE` upon returning the new graph. Consequently, when `RuntimeRoot.restore_checkpoint` subsequently performed `self.graph = new_graph`, the lifecycle guard was already `IDLE`.
* **Correction:**
  - Decomposed restore into `_prepare_restored_cognitive_graph(...)` (Phase A object construction & postcondition validation, lifecycle-agnostic) and `restore_cognitive_checkpoint(...)` (top-level guarded standalone restore).
  - In `RuntimeRoot.restore_checkpoint`, a single `with self.guard.restoring():` block encloses `_prepare_restored_cognitive_graph`, runtime config application, pre-swap inspection, and the root swap `self.graph = new_graph`.
  - Asserted `self.guard.state == RuntimeLifecycleState.RESTORING` at the exact swap instant.
  - If preparation fails, the old root graph is untouched and the guard safely resets to `IDLE`.

### Defect 4: Incomplete Compatibility Validation
* **Problem:** R0 failed to explicitly recompute and validate `combined_semantics_digest`, and did not validate `runtime_contract_version`.
* **Correction:**
  - Added explicit check: `runtime_contract_version` must match supported version ("1.1.1").
  - Restore recomputes `combined_semantics_digest = sha256(region_schema_digest + active_law_digest + assembly_policy_digest)`.
  - Explicitly asserts `combined_semantics_digest == compatibility["combined_semantics_digest"]`, failing closed (`CheckpointCompatibilityError`) if tampered.

### Defect 5: Ordered Durable Sequences Reordered During Canonicalization
* **Problem:** R0 canonicalization sorted all sequences, including `graph.hypotheses` and `StructuralAssembly.parent_assemblies`, altering their durable order.
* **Correction:**
  - `graph.hypotheses` list order is durable and preserved exactly without sorting.
  - `StructuralAssembly.parent_assemblies` tuple order is durable and preserved exactly without sorting.
  - Unordered sets (members, contexts, edges) remain canonically sorted.

---

## 4. Checkpoint Schema Migration
* **Schema 1.1.1:**
  - `checkpoint_schema_version = "1.1.1"`
  - `runtime_contract_version = "1.1.1"`
  - `cognitive_semantics_version = "1.0"`
* **1.1 -> 1.1.1 Migration (`migrate_schema_1_1_to_1_1_1`):**
  - Reconstructs `storage_key = f"{candidate_id}:ctx_{context_signature or 'default'}"` for each pending formation candidate.
  - Detects duplicate derived storage keys: fails closed (`LegacyMigrationError`) if ambiguous or non-identical; never silently merges or unions vote sets.
  - Emits diagnostic records detailing reconstructed keys.
* **Legacy 1.0 Migration (`migrate_legacy_v1_checkpoint`):**
  - Migrates legacy checkpoints directly to target schema `1.1.1`.
  - Emits explicit loss warning for unpersisted RFC-11 pending structural candidates.

---

## 5. Invariant Verification Ledger (C01-I01 .. C01-I15)

| Invariant | Description | Status |
|:---|:---|:---:|
| **C01-I01** | Formation storage keys survive exactly across checkpoint save/restore | **VERIFIED** |
| **C01-I02** | Same component in different contexts remains distinct in pending state | **VERIFIED** |
| **C01-I03** | 4 votes + restart + fifth vote forms exactly one assembly | **VERIFIED** |
| **C01-I04** | Pending context B remains unchanged when context A commits | **VERIFIED** |
| **C01-I05** | Checkpoint policy equals graph structural-state policy | **VERIFIED** |
| **C01-I06** | RuntimeRoot adopts existing manager policy when no explicit policy is supplied | **VERIFIED** |
| **C01-I07** | Policy mismatch fails before checkpoint replacement | **VERIFIED** |
| **C01-I08** | Root swap occurs while guard state is RESTORING | **VERIFIED** |
| **C01-I09** | No nested guard exposes IDLE before root swap | **VERIFIED** |
| **C01-I10** | `runtime_contract_version` is validated during restore | **VERIFIED** |
| **C01-I11** | `combined_semantics_digest` is recomputed and validated during restore | **VERIFIED** |
| **C01-I12** | Hypothesis list order survives exactly | **VERIFIED** |
| **C01-I13** | `parent_assemblies` tuple order survives exactly | **VERIFIED** |
| **C01-I14** | Existing schema 1.1 checkpoints migrate deterministically to 1.1.1 | **VERIFIED** |
| **C01-I15** | Cognitive baseline signature remains unchanged (`915119d40643cb97`) | **VERIFIED** |

---

## 6. Acceptance Test Results (C01-T01 .. C01-T20)

| Test ID | Test Name / Focus | Result | Execution Time |
|:---|:---|:---:|:---:|
| **C01-T01** | Real RFC-11 4+restart+1 formation continuity via `record_participation` | **PASS** | 0.08s |
| **C01-T02** | Two-context candidate separation across restart | **PASS** | 0.05s |
| **C01-T03** | Context A commit does not mutate context B votes | **PASS** | 0.06s |
| **C01-T04** | Formation storage-key round-trip exactness | **PASS** | 0.04s |
| **C01-T05** | Save policy mismatch fails closed | **PASS** | 0.03s |
| **C01-T06** | `RuntimeRoot` adopts manager policy | **PASS** | 0.04s |
| **C01-T07** | Incompatible restore policy fails closed | **PASS** | 0.04s |
| **C01-T08** | Root swap observed while guard state is RESTORING | **PASS** | 0.04s |
| **C01-T09** | Failed prepare preserves old root and returns guard to IDLE | **PASS** | 0.04s |
| **C01-T10** | Tampered `runtime_contract_version` fails closed | **PASS** | 0.04s |
| **C01-T11** | Tampered `combined_semantics_digest` fails closed | **PASS** | 0.04s |
| **C01-T12** | Hypothesis list order exact across restore | **PASS** | 0.04s |
| **C01-T13** | `parent_assemblies` tuple order exact across restore | **PASS** | 0.04s |
| **C01-T14** | Schema 1.1 formation-key migration | **PASS** | 0.04s |
| **C01-T15** | Schema 1.1 duplicate-derived-key conflict fails closed | **PASS** | 0.03s |
| **C01-T16** | Legacy 1.0 migration to 1.1.1 passes | **PASS** | 0.04s |
| **C01-T17** | Corrected repeated-save digest deterministic | **PASS** | 0.05s |
| **C01-T18** | Full original R0 test suite passes (73/73) | **PASS** | 2.22s |
| **C01-T19** | Full repository regression passes (2,533/2,533) | **PASS** | 24.00s |
| **C01-T20** | Baseline signature unchanged (`915119d40643cb97`) | **PASS** | 0.03s |

**C01 Test Suite Summary:** 20 passed in 1.71s (100% PASS).

---

## 7. Regression & Quality Gate Results

### Original R0 Test Suite
* **Suite:** `tests/test_ric01_r0_persistence.py`
* **Result:** **73 passed** in 2.22s (100% PASS).

### Repository Full Regression Suite
* **Command:** `pytest tests/`
* **Result:** **2,533 passed** in 24.00s, 0 failed, 0 errors.

### Linter Check
* **Command:** `ruff check dgca/persistence.py dgca/__init__.py tests/test_ric01_r0_persistence.py tests/test_ric01_r0_c01_correction.py`
* **Result:** **All checks passed!** (0 errors, 0 warnings).

### Behavioral Baseline Signature
* **Command:** `python -c "from dgca.signature import behavioral_signature, build_reference_graph; print(behavioral_signature(build_reference_graph()))"`
* **Expected:** `915119d40643cb97`
* **Actual:** `915119d40643cb97`
* **Delta:** Exact match (0 bit delta).

---

## 8. Scope Audit
* **Persistence & Lifecycle:** Strictly confined to `dgca/persistence.py` and narrow export in `dgca/__init__.py`.
* **Testing:** Dedicated test suite `tests/test_ric01_r0_c01_correction.py` and canonical assertion update in `tests/test_ric01_r0_persistence.py`.
* **Prohibited Areas Untouched:**
  - Audio / Vision / Encoders: 0 lines touched.
  - Reasoning / Causality / Law constants: 0 lines touched.
  - RFC-11 through RFC-16 engine logic: 0 lines touched.
  - R1 / R2 / R3 scope: Strictly unstarted and unauthorized.

---

## 9. Final Verdict

# `RIC01_R0_C01_IMPLEMENTATION_VERIFIED`
