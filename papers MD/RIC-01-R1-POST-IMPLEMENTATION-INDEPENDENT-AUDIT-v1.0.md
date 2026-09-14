# DGCA — RIC-01 / R1
## Post-Implementation Independent Audit v1.0

**Program:** `RIC-01 — Canonical Runtime Integration Contract`  
**Stage audited:** `R1 — Deterministic Causal Identity Protocol`  
**Frozen architecture:** `RIC-01-R1-Deterministic-Causal-Identity-Protocol-v1.3-FROZEN.md`  
**Implementation commit:** `d05af8e2f1f68bd7beef8909c01e23260274f62a`  
**Parent commit:** `0f9c397d1bd1fc02a678fa55a9206075efe2bc35`  
**Audit mode:** Independent read-only code review  
**Repository mutation:** `NONE`  
**R2 authorization:** `NO`

---

# 1. Executive Verdict

The implementation commit exists, is exactly one commit ahead of the R0 closure commit, and is scope-disciplined at the changed-file level.

The implementation also contains substantial correct R1 infrastructure:

- authoritative domain-separated SHA-256 causal IDs,
- deterministic RootExternalEpisodeID derivation,
- additive canonical RID support,
- a non-cognitive causal commit ledger,
- schema-1.2.0 checkpoint packaging,
- event binding and replay protection,
- fail-stop runtime health,
- canonical-lineage invalidation state,
- NEW_ROOT preservation of the external root ID.

However, independent code review finds multiple frozen-contract violations that are not exercised end-to-end by the reported R1 test suite.

Therefore the reported `RIC01_R1_IMPLEMENTATION_VERIFIED` verdict cannot be independently accepted.

```text
==================================================
RIC-01 / R1
POST-IMPLEMENTATION INDEPENDENT AUDIT v1.0

IMPLEMENTATION COMMIT:
d05af8e2f1f68bd7beef8909c01e23260274f62a

CORE R1 INFRASTRUCTURE:
SUBSTANTIALLY IMPLEMENTED

COGNITIVE BASELINE DRIFT:
NO DRIFT REPORTED / DIFF DOES NOT MODIFY BASELINE FILE

R1 END-TO-END CONFORMANCE:
FAIL

FATAL COGNITIVE-LAW DEFECTS:
0

POST-IMPLEMENTATION BLOCKERS:
7

NON-FATAL HARDENING DEBT:
1

R1 STATUS:
OPEN — REPAIR REQUIRED

R2:
NOT AUTHORIZED

FINAL VERDICT:
RIC01_R1_POST_IMPLEMENTATION_AUDIT_FAILED
==================================================
```

---

# 2. Positive Findings

## P01 — Commit lineage and scope

The audited commit is exactly one commit ahead of the R0 parent. No Audio or Vision production files are changed.

**Verdict:** PASS.

## P02 — Core identity primitive

The implementation provides:

```text
DGCA:R1:ID:v1
SHA-256
full 64-hex authoritative digest
literal domain registry
canonical JSON
domain separation
```

and rejects non-finite numbers.

**Verdict:** PASS.

## P03 — Root external occurrence identity

Production root identity is derived from:

```text
boundary_namespace
source_occurrence_key
```

rather than raw content.

**Verdict:** PASS.

## P04 — Additive canonical RID

RFC-12 retains its legacy UUID path while adding a canonical representation path with causal parent + operational representation digest.

**Verdict:** PASS IN ISOLATION.

## P05 — Durable non-cognitive causal ledger

`CausalCommitLedger`, `EventBindingRecord`, `CausalCommitRecord`, and `CausalProvenanceEpoch` exist outside `CognitiveGraph`.

**Verdict:** PASS IN PRINCIPLE.

## P06 — Fail-stop semantics

Owner mutation failure and ledger-commit failure place the canonical runtime in `MUTATION_FAILED`, matching the frozen architecture's conservative no-false-rollback policy.

**Verdict:** PASS.

## P07 — Pre-R1 migration disclosure

Migration creates an empty R1 ledger and marks historical provenance as unavailable.

**Verdict:** PASS.

---

# 3. Blocker PIR01-B01 — R1 Restore Bypasses the R0 Semantic Compatibility Firewall

## Severity

`CRITICAL`

## Frozen requirement

Canonical R1 restore must preserve the complete R0 compatibility firewall:

```text
region schema
active Law configuration
AssemblyPolicy
combined semantic digest
cognitive semantics version
runtime contract
```

plus R1 causal/observation protocol compatibility.

## Actual implementation

The R0 restore path recomputes and validates:

```text
region_schema_digest
active_law_digest
assembly_policy_digest
combined_semantics_digest
checkpoint_state_digest
```

before graph construction.

The R1 restore path validates:

```text
observation protocol
causal identity protocol digest
state digest
causal provenance digest
bundle digest
```

but then directly calls `_restore_graph_from_persistent_payload()` without independently recomputing and enforcing the R0 semantic compatibility digests.

This allows a schema-1.2.0 checkpoint whose compatibility section is internally re-hashed consistently but semantically incompatible with the running Laws/policy/regions to pass the R1-specific integrity checks.

The 1.1.1→1.2.0 migration path also does not perform the full R0 source semantic-compatibility firewall before promoting the checkpoint.

## Required repair

Create one shared authoritative compatibility validator and require it in:

```text
R0 canonical restore
R1 schema-1.2.0 restore
1.1.1 → 1.2.0 migration
```

R1 restore must fail closed on every R0 semantic mismatch before graph construction.

---

# 4. Blocker PIR01-B02 — RFC-13 Canonical Identity Mode Breaks During Actual Settling

## Severity

`CRITICAL`

## Frozen requirement

Once a canonical causal representation enters RFC-13, all canonical cross-subsystem descendants must remain deterministic and parent-scoped:

```text
SettlingEpochID
PatternCandidateID
ReinstatementProposalID
next RepresentationID
```

## Actual implementation

`run_settling_epoch(... canonical_identity=True, ...)` can create a canonical epoch ID, but its internal loop calls:

```text
discover_candidates(current_rep)
evaluate_reinstatement_eligibility(...)
build_representation(...)
```

without propagating canonical identity mode or a causal parent reference.

Consequences:

1. edge-based candidates still use the legacy truncated candidate hash even when canonical identity is requested;
2. proposals fall back to legacy graph-time-based IDs;
3. the next RFC-12 representation falls back to random `uuid4()` RID after the first settling iteration;
4. the canonical causal chain is therefore broken inside the canonical settling execution itself.

Additionally, absent `work_ref` falls back to graph logical time, which is not sufficient causal work identity under the frozen R1 contract.

## Required repair

Canonical settling must explicitly propagate one immutable canonical identity context through every internal step:

```text
canonical candidate discovery
canonical proposal derivation
canonical settling work reference
canonical completion receipt identity
canonical next-snapshot RID
```

No canonical path may silently call a legacy identity branch.

---

# 5. Blocker PIR01-B03 — RFC-14 Canonical Frame/Occurrence Integration Is Missing and SurfaceChunk Identity Is Wrong

## Severity

`CRITICAL`

## Frozen requirement

Canonical RFC-14 execution must derive:

```text
GenerativeFrameID
LinearizableOccurrenceID
SurfaceUnitID
SurfaceChunkID
```

through R1 causal identity.

`SurfaceChunkID` must bind the actual:

```text
parent RID
ordered SurfaceUnitIDs
rendered text
closure_reason
origin_lineage
```

## Actual implementation

`build_generative_frame()` still always creates the legacy truncated hash ID.

`build_precedence_graph()` still always creates occurrence IDs through string concatenation:

```text
occ_<frame>_<role>_<filler>
```

Only `realize_surface_chunk()` has an additive canonical flag.

Worse, in its canonical branch the chunk ID is derived with:

```text
closure_reason="COMPLETED"
origin_lineage="generation"
```

even though the actual `SurfaceChunk` object may carry:

```text
COMPLETE
CONFLICT
AMBIGUOUS
PARTIAL_BUDGET
```

and uses `origin_lineage="GENERATION"`.

Thus causally different surface objects can collapse to the same canonical chunk identity.

## Required repair

Add canonical identity propagation to frame construction and occurrence construction.

Derive chunk identity from the exact final object semantics:

```text
actual closure_reason
actual origin_lineage
actual ordered unit IDs
```

No hard-coded substitute values.

---

# 6. Blocker PIR01-B04 — RFC-15 Canonical Identity Is Not Propagated Through Recurrent Execution

## Severity

`CRITICAL`

## Frozen requirement

A canonical GCE execution must remain canonical through:

```text
GCE
obligations
ContinuationCommit
RFC-14 frame/occurrence/surface
ExpressionReceipt
progress
```

## Actual implementation

`create_epoch(... canonical_identity=True)` and `commit_continuation(... canonical_identity=True)` have helper support.

But the actual `execute_recurrent_step()`:

- has no canonical identity mode/context;
- calls `commit_continuation()` without canonical mode;
- calls legacy `build_generative_frame()`;
- calls `realize_surface_chunk()` without canonical mode;
- calls `create_expression_receipt()` which has no canonical mode and uses a legacy ad-hoc truncated hash;
- `derive_obligations()` still uses the legacy obligation ID formula.

Therefore a canonical GCE does not produce a canonical recurrent causal chain.

## Required repair

Introduce one canonical recurrent execution context and propagate it through the whole step/epoch.

Canonical execution must never fall back to legacy identity derivation.

---

# 7. Blocker PIR01-B05 — Canonical Runtime Exposes Unguarded Persistent Mutation and Allows Guardless Construction

## Severity

`CRITICAL`

## Frozen requirement

Production canonical APIs must not expose an unguarded public persistent-write path.

A canonical runtime must have one authoritative lifecycle guard shared by persistent mutation and checkpointing.

An explicit unsafe escape hatch may exist only if using it invalidates canonical lineage.

## Actual implementation

`CanonicalR1RuntimeRoot` stores:

```text
self.graph = graph
```

as a publicly mutable object.

A caller can directly execute:

```python
runtime.graph.link(...)
runtime.graph.observe(...)
```

without using the unsafe escape hatch, leaving:

```text
canonical_lineage_state == VALID
```

and then produce a canonical R1 checkpoint whose graph contains untracked persistent state absent from the ledger.

Also:

```text
lifecycle_guard=None
```

is accepted.

When no guard is supplied, persistent command execution runs without an R0 lifecycle guard, while save creates a temporary independent guard.

This defeats the single-runtime lifecycle exclusion contract.

## Required repair

A canonical R1 runtime must always own a real guard.

Its cognitive graph must be private to the canonical host API, with read-only inspection surfaces where appropriate.

If raw mutable graph access is retained for developer compatibility, obtaining it must be an explicitly unsafe operation that invalidates lineage before access is returned.

Canonical mutation and canonical checkpoint save must use the same guard instance.

---

# 8. Blocker PIR01-B06 — R1 Atomic Save Regresses R0 Directory Durability

## Severity

`HIGH`

## Frozen requirement

R1 checkpointing must reuse/extend R0's atomic-save protocol.

R0 already does:

```text
temp file in same directory
file flush
file fsync
os.replace
directory fsync where supported
```

## Actual implementation

`save_canonical_r1_checkpoint()` performs:

```text
temp file
file fsync
os.replace
```

but omits the post-replace directory fsync already present in the R0 saver.

That is a persistence durability regression.

## Required repair

Factor the atomic file replacement routine into a shared helper and reuse it for both R0 and R1, including best-effort directory fsync.

---

# 9. Blocker PIR01-B07 — Ledger Restore Is Digest-Protected but Not Semantically Fail-Closed

## Severity

`HIGH`

## Frozen requirement

Malformed causal provenance must fail closed even when checksums are internally consistent.

Required relationships include:

```text
dictionary key == record identity field
TxID == canonical derivation of stored transaction descriptor
EventID == canonical derivation/expected immutable identity where applicable
transaction references an existing compatible event binding
transaction root/event/protocol agree with event binding
provenance epoch is structurally valid
```

## Actual implementation

`CausalCommitLedger.from_dict()` reconstructs records but does not verify these semantic relationships.

The current R1-T38 only tampers with ledger bytes without recomputing the provenance/bundle digests. Restore then rejects the checksum mismatch.

That does not prove rejection of a semantically malformed but correctly re-digested checkpoint.

## Required repair

Add a strict `validate_causal_provenance_state()` executed before runtime construction.

Add adversarial tests that construct malformed provenance, recompute all R1 digests correctly, and confirm restore still rejects it.

---

# 10. Non-Fatal Hardening Debt PIR01-D01 — Mapping-Key Canonicalization Can Collapse Distinct Python Keys

## Severity

`MEDIUM`

## Actual implementation

Canonicalization converts dictionary keys using:

```python
str(k)
```

This can collapse distinct Python mappings such as:

```python
{1: "a", "1": "b"}
```

into one JSON key.

## Required hardening

For authoritative R1 identity payloads, require string mapping keys and reject unsupported/non-string mapping keys rather than coercing them.

At minimum reject post-canonicalization duplicate keys.

This is identity infrastructure and should be hardened in PIR-01 while the code is localized.

---

# 11. Test-Coverage Audit

The reported passing test count is not disputed.

The problem is sufficiency of the test mapping.

Several acceptance tests exercise identity helper functions rather than the real subsystem execution path.

Examples:

```text
T18/T19:
helper-level candidate/proposal identity checks

T20:
helper-level frame/occurrence derivation, not HierarchicalGenerativeEngine integration

T22:
helper-level continuation-commit derivation, not recurrent execution

T23:
helper-level SurfaceUnit derivation, not actual surface realization chain

T38:
checksum tamper, not semantically malformed re-digested ledger

T48/T49:
does not execute an observation-protocol change against persisted RFC-11 root evidence

T69:
replays one fixed scope; does not prove that canonical production APIs reject caller-controlled scope variation
```

Therefore:

```text
65 / 65 PASS
```

does not establish full conformance to the frozen R1 contract.

---

# 12. Required PIR-01 Repair Gates

R1 may close only after all of the following pass:

```text
PIR01-G01  full R0 semantic compatibility firewall applied to R1 restore/migration
PIR01-G02  canonical RFC13 settling remains canonical across multi-iteration snapshots
PIR01-G03  RFC14 frame + occurrence + actual chunk descriptor identity are canonical
PIR01-G04  RFC15 recurrent execution remains canonical end-to-end
PIR01-G05  canonical runtime has mandatory shared lifecycle guard
PIR01-G06  untracked mutable-graph access cannot preserve VALID lineage
PIR01-G07  R1 save uses R0-equivalent directory durability semantics
PIR01-G08  semantically malformed but correctly re-digested causal ledger fails closed
PIR01-G09  canonical mapping-key collision hardening passes
PIR01-G10  all original R1 tests pass
PIR01-G11  all R0/C01/C02/C03 tests pass
PIR01-G12  full repository regression passes
PIR01-G13  Ruff passes
PIR01-G14  cognitive baseline remains 915119d40643cb97
PIR01-G15  R2/R3/Audio/Vision remain untouched
```

---

# 13. Closure Decision

The R1 architecture remains frozen.

The implementation is not discarded; the majority of R1 infrastructure is reusable.

The correct next action is a narrowly scoped post-implementation repair:

```text
RIC-01 / R1-PIR-01
Post-Implementation Repair 01
```

R2 remains unauthorized until PIR-01 is implemented and independently re-audited.

```text
FINAL VERDICT:
RIC01_R1_POST_IMPLEMENTATION_AUDIT_FAILED
```
