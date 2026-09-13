# DGCA — RIC-01 / R0-C02

## Schema-1.1 Migration Integrity Closure

# Formal Correction Specification v1.0 — FROZEN

**Project:** DGCA  
**Parent Program:** RIC-01 — Canonical Runtime Integration Contract  
**Parent Stage:** R0 — Persistence & Runtime Lifecycle  
**Parent Correction:** R0-C01 — Persistence Closure Correction  
**Parent Commit:** `71689befc31d3e4258a04636872c5ead4fa85673`  
**Trigger:** Independent post-C01 audit  
**Status:** FROZEN  
**Scope:** Migration-integrity correction only. R1 remains unauthorized.  

---

# 1. Purpose

R0-C02 closes one remaining integrity defect in the new schema 1.1 -> 1.1.1 migration path.

The current migration mutates the source checkpoint and recomputes a new state digest before proving that the original schema-1.1 checkpoint was internally valid.

Therefore a schema-1.1 checkpoint whose persistent payload was tampered without updating its original recorded digest can be migrated and re-signed by the migration code.

The same path also overwrites `runtime_contract_version` with 1.1.1 before proving that the source checkpoint actually declared the supported source contract 1.1.

This violates the fail-closed checkpoint contract.

---

# 2. Governing Rule

Migration MUST transform only a valid source checkpoint.

Formally:
```text
ValidateSource(source)
    MUST PASS
before
Transform(source -> target)
```

**Forbidden:**
```text
tampered source
→ migration recomputes digest
→ source becomes accepted target
```

Migration authority is not repair authority.

---

# 3. Schema-1.1 Source Validation

Before `migrate_schema_1_1_to_1_1_1(...)` changes any field, it MUST validate the source checkpoint as schema 1.1.

Required source checks:
* `checkpoint_schema_version == "1.1"`
* `runtime_contract_version == "1.1"`
* `cognitive_semantics_version == "1.0"`
* `persistent_state` exists and is structurally valid JSON data
* all numeric values are finite
* recorded `checkpoint_state_digest` exists
* `SHA256(canonical source persistent_state) == recorded checkpoint_state_digest`

If any check fails:
**FAIL CLOSED**

No target checkpoint may be emitted.

---

# 4. Source Semantic Compatibility

The schema-1.1 source checkpoint MUST also remain subject to semantic compatibility.

Before or immediately after structural migration, but before acceptance, verify the source compatibility header against the current runtime:
* `region_schema_digest`
* `active_law_digest`
* `assembly_policy_digest`
* `combined_semantics_digest`

The migration MUST NOT replace incompatible semantic fingerprints with current values merely to make the checkpoint loadable.

Schema migration changes representation format only.
It does not authorize cognitive-semantic migration.

---

# 5. State Digest Rule

For schema 1.1:
```text
D_source_recorded == SHA256(CanonicalPersistentPayload_source)
```
must be proven first.

Only after that proof may migration add deterministic `storage_key` values and calculate:
```text
D_target = SHA256(CanonicalPersistentPayload_target)
```

The two digests may differ because the canonical persistent representation changes by adding `storage_key`.
This difference is lawful only after source integrity has passed.

---

# 6. Source Runtime Contract Rule

The migration entry point for 1.1 -> 1.1.1 MUST reject:
`runtime_contract_version != "1.1"`

It MUST NOT silently overwrite unknown source contract versions.

Examples:
* `checkpoint_schema_version = 1.1`, `runtime_contract_version = 9.9` → **REJECT**
* `checkpoint_schema_version = 1.1`, `runtime_contract_version` missing → **REJECT**

---

# 7. Migration Report Rule

A `MigrationReport` may be returned only after source validation succeeds.

For valid schema-1.1 migration, the report SHOULD record:
* source integrity: `VERIFIED`
* source runtime contract: `1.1`
* target runtime contract: `1.1.1`
* formation storage keys: reconstructed deterministically

No report may describe an invalid source migration as successful.

---

# 8. Historical Ordered-Sequence Limitation

Schema 1.1 had already serialized hypotheses and parent_assemblies in canonical sorted order.

R0-C02 freezes the following migration interpretation:
* For a schema-1.1 file, the serialized sequence order is authoritative source data.
* Pre-serialization ordering that was lost under schema 1.1 cannot be reconstructed.

The migration report SHOULD disclose this limitation.
No heuristic reconstruction is permitted.

This is a historical migration limitation, not a new runtime defect.

---

# 9. Required Invariants

* **C02-I01**  Invalid schema-1.1 source digest can never be re-signed by migration.
* **C02-I02**  Source persistent payload is verified before any migration mutation.
* **C02-I03**  Source `runtime_contract_version` must equal 1.1.
* **C02-I04**  Source `cognitive_semantics_version` must equal 1.0.
* **C02-I05**  Source semantic fingerprints remain subject to compatibility validation.
* **C02-I06**  Valid schema-1.1 checkpoint still migrates deterministically to 1.1.1.
* **C02-I07**  Target digest is computed only after source integrity passes.
* **C02-I08**  No migration changes cognitive semantics.
* **C02-I09**  Baseline cognitive signature remains unchanged.

---

# 10. Required Acceptance Tests

* **C02-T01** valid schema 1.1 migrates to 1.1.1
* **C02-T02** tampered 1.1 persistent payload with unchanged old digest fails closed
* **C02-T03** missing 1.1 recorded state digest fails closed
* **C02-T04** source `runtime_contract_version` 9.9 fails closed
* **C02-T05** missing source `runtime_contract_version` fails closed
* **C02-T06** source `cognitive_semantics_version` mismatch fails closed
* **C02-T07** source region fingerprint mismatch fails closed
* **C02-T08** source active-law fingerprint mismatch fails closed
* **C02-T09** source assembly-policy fingerprint mismatch fails closed
* **C02-T10** source combined-semantics fingerprint mismatch fails closed
* **C02-T11** migration report emitted only for valid source
* **C02-T12** target state digest validates after migration
* **C02-T13** C01 suite remains fully passing
* **C02-T14** original R0 suite remains fully passing
* **C02-T15** full repository regression passes
* **C02-T16** baseline signature unchanged

---

# 11. Forbidden Changes

R0-C02 MUST NOT modify:
* RFC-11 cognition
* `AssemblyManager.record_participation`
* Law constants
* Encoder
* Vision
* Audio
* Reasoning
* Generation
* RFC12-RFC16 engine logic
* Agent
* REPL
* R1
* R2
* R3

No new cognitive state is authorized.

---

# 12. Release Gate

R0-C02 closes only if:
* C02-I01..C02-I09 = PASS
* C02-T01..C02-T16 = PASS
* C01 tests = PASS
* original R0 tests = PASS
* full regression = PASS
* quality gates = PASS
* baseline signature = unchanged
* scope audit = PASS

Final implementation verdict must be exactly one of:
* `RIC01_R0_C02_IMPLEMENTATION_VERIFIED`
* `RIC01_R0_C02_IMPLEMENTATION_FAILED`
* `RIC01_R0_C02_IMPLEMENTATION_BLOCKED`

---

# 13. Freeze Review

* CORE CORRECTION MODEL: PASS
* NEW COGNITIVE SEMANTICS: NO
* SOURCE-INTEGRITY BYPASS: CLOSED BY SPEC
* SOURCE-CONTRACT BYPASS: CLOSED BY SPEC
* R1/R2/R3 SCOPE LEAK: NO
* REMAINING FREEZE BLOCKERS: 0
* FORMAL FREEZE: AUTHORIZED

---

# Final Specification Identifier
`RIC-01 / R0-C02 Schema-1.1 Migration Integrity Closure v1.0 — FROZEN`
