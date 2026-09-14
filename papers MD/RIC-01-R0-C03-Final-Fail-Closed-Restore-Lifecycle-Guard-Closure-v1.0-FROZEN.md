# DGCA — RIC-01 / R0-C03

## Final Fail-Closed Restore & Lifecycle Guard Closure

# Formal Correction Specification v1.0 — FROZEN

**Project:** DGCA  
**Parent Program:** RIC-01 — Canonical Runtime Integration Contract  
**Parent Stage:** R0 — Persistence & Runtime Lifecycle  
**Parent Commit:** `4c515fc6b7fb3ff1e8f69094412c1b32a6301433`  
**Trigger:** Full R0 closure audit after C02  
**Status:** FROZEN  
**Scope:** R0 persistence/lifecycle hardening only. R1 remains unauthorized.  

---

# 1. Purpose

Close the final fail-closed gaps found in the full R0 closure audit after C02:

1. Schema-less JSON is currently treated as legacy v1.0.
2. Duplicate canonical identities can silently overwrite earlier records during restore.
3. RFC-11 pending structural identity is not fully validated.
4. RuntimeLifecycleGuard permits same-state nested entry, allowing an inner context to reset the guard to IDLE while an outer operation is still active.

No cognitive law or cognitive subsystem may change.

---

# 2. C03-01 — Strict Source-Family Recognition

Recognize only:
* legacy: `version == "1.0"` and no canonical schema
* migration source: `schema.checkpoint_schema_version == "1.1"`
* current: `schema.checkpoint_schema_version == "1.1.1"`

Anything else fails closed (`CheckpointSchemaError`). Missing schema alone is never proof of legacy format. `{}` or `{"nodes":{}}` must fail.

---

# 3. C03-02 — Legacy v1.0 Source Validation

Before migration require `version == "1.0"` and durable legacy sections emitted by `CognitiveGraph.to_dict()`:
* `t`
* `concept_hits`
* `drives`
* `hypotheses`
* `X`
* `nodes`
* `edges`
* `assemblies`

with compatible container types. Direct calls to legacy migration must enforce the same validation. Missing durable sections are not defaulted or invented.

---

# 4. C03-03 — Strict JSON Parsing

Reject duplicate JSON object keys instead of last-key-wins behavior. Duplicate top-level or nested checkpoint keys are malformed input (`CheckpointSchemaError`).

---

# 5. C03-04 — Canonical 1.1.1 Shape Validation

Before construction require top-level:
* `schema`
* `compatibility`
* `integrity`
* `persistent_state`

and persistent fields:
* `logical_time`
* `nodes`
* `edges`
* `contradictions`
* `concept_hits`
* `drives`
* `hypotheses`
* `assemblies`
* `pending_structural_evidence`

with pending:
* `pending_candidates`
* `pending_growth`
* `pending_merge`

Do not silently substitute missing durable sections with empty defaults. Apply equivalent shape checks to schema 1.1 before migration.

---

# 6. C03-05 — Duplicate Identity Rejection

Reject duplicate authoritative identities before dict insertion (`CheckpointValidationError` / `CheckpointIntegrityError`):
* `Node.nid`
* `Edge(src, dst)`
* `StructuralAssembly(assembly_id, version)`
* Formation `storage_key`
* Growth key `(assembly_id, new_edge, context)`
* Merge key `(parent-set, context)`

Root votes retain intentional set/idempotent semantics.

---

# 7. C03-06 — RFC-11 Pending Identity Validation

### Formation:
* `candidate_id == canonical_assembly_id(edges)`
* `storage_key == f"{candidate_id}:ctx_{context_signature or 'default'}"`
* `K_ASM_MIN <= len(edges) <= K_ASM_MEM`
* all edges live

### Growth:
* parent exists and live
* new edge exists
* new edge is not already a member of parent

### Merge:
* exactly two distinct parent assembly IDs (`len(parents) == 2`)
* both parents exist
* both latest versions live

Persistence validates RFC-11 state; it does not alter RFC-11 cognition.

---

# 8. C03-07 — Lifecycle Guard Re-entry

Allowed transitions remain only:
* `IDLE -> MUTATING -> IDLE`
* `IDLE -> CHECKPOINTING -> IDLE`
* `IDLE -> RESTORING -> IDLE`

Nested same-state entries (`RESTORING -> RESTORING`, `CHECKPOINTING -> CHECKPOINTING`, `MUTATING -> MUTATING`) must raise `IllegalLifecycleTransitionError`. An inner failed entry must not force the outer guard to IDLE.

---

# 9. Required Invariants

* **C03-I01**  schema-less JSON is never treated as legacy
* **C03-I02**  legacy migration accepts only explicit v1.0
* **C03-I03**  missing durable legacy fields fail closed
* **C03-I04**  duplicate JSON keys fail closed
* **C03-I05**  missing canonical durable sections fail closed
* **C03-I06**  duplicate Node IDs fail closed
* **C03-I07**  duplicate Edge IDs fail closed
* **C03-I08**  duplicate Assembly versions fail closed
* **C03-I09**  duplicate pending formation/growth/merge identities fail closed
* **C03-I10**  formation candidate identity matches canonical edge identity
* **C03-I11**  formation size respects RFC-11 bounds
* **C03-I12**  growth edge is not already in parent
* **C03-I13**  merge has exactly two distinct live parents
* **C03-I14**  same-state lifecycle nesting fails closed
* **C03-I15**  lawful C02/C01/R0 behavior remains unchanged
* **C03-I16**  baseline signature remains unchanged

---

# 10. Required Acceptance Tests

* **C03-T01**  `{}` fails
* **C03-T02**  schema-less pseudo-legacy fails
* **C03-T03**  valid explicit v1.0 still migrates
* **C03-T04**  missing/unknown legacy version fails
* **C03-T05**  missing durable legacy section fails
* **C03-T06**  duplicate JSON key fails
* **C03-T07**  current checkpoint missing durable section fails
* **C03-T08**  duplicate node fails
* **C03-T09**  duplicate edge fails
* **C03-T10**  duplicate assembly version fails
* **C03-T11**  duplicate formation key fails
* **C03-T12**  duplicate growth key fails
* **C03-T13**  duplicate merge key fails
* **C03-T14**  noncanonical formation candidate_id fails
* **C03-T15**  invalid formation size fails
* **C03-T16**  growth edge already in parent fails
* **C03-T17**  one-parent merge fails
* **C03-T18**  >2-parent merge fails
* **C03-T19**  nested RESTORING fails and outer remains RESTORING
* **C03-T20**  nested CHECKPOINTING fails
* **C03-T21**  nested MUTATING fails
* **C03-T22**  lawful RuntimeRoot restore still swaps under RESTORING
* **C03-T23**  valid 1.1 migration passes
* **C03-T24**  valid 1.0 migration passes
* **C03-T25**  C02 suite passes
* **C03-T26**  C01 suite passes
* **C03-T27**  original R0 suite passes
* **C03-T28**  full regression passes
* **C03-T29**  baseline signature unchanged

---

# 11. Fixture Correction

Any older R0 fixture containing a pending merge record with only one parent is not production-lawful state. Correct the fixture to use two distinct valid parent assemblies; do not weaken validation to preserve an invalid fixture.

---

# 12. Forbidden Changes

Do not modify RFC-11 cognition, laws, Encoder, Vision, Audio, Reasoning, RFC12–16 engines, Agent, REPL, R1/R2/R3.

---

# 13. Release Gate

All C03 invariants/tests, C02/C01/R0 suites, full regression, quality gates, unchanged baseline signature, and scope audit must pass.

Final verdict:
* `RIC01_R0_C03_IMPLEMENTATION_VERIFIED`
* `RIC01_R0_C03_IMPLEMENTATION_FAILED`
* `RIC01_R0_C03_IMPLEMENTATION_BLOCKED`

---

# 14. Freeze Review

* CORE MODEL: PASS
* NEW COGNITIVE LAW: NO
* STRICT LEGACY RECOGNITION: CLOSED BY SPEC
* DUPLICATE IDENTITY COLLAPSE: CLOSED BY SPEC
* RFC11 PENDING IDENTITY VALIDATION: CLOSED BY SPEC
* LIFECYCLE REENTRY: CLOSED BY SPEC
* R1/R2/R3 SCOPE LEAK: NO
* REMAINING FREEZE BLOCKERS: 0
* FORMAL FREEZE: AUTHORIZED

---

# Final Specification Identifier
`RIC-01 / R0-C03 Final Fail-Closed Restore & Lifecycle Guard Closure v1.0 — FROZEN`
