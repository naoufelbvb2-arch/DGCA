# DGCA — RIC-01 / R2-PIR-01
## Post-Repair Independent Closure Audit v1.0

**Implementation commit:** `d66823a2f6c73555cb9f201b5716780a9ee144c7`  
**Parent commit:** `3512efd5e39c4d3c604c03f4fc8e8dc697a0e4bb`  
**Frozen architecture:** `RIC-01-R2-Canonical-Ingress-Observation-Bridge-Formal-Architecture-v1.1-FROZEN.md`  
**Audit mode:** independent / read-only  
**Repository mutation:** none  
**R3:** not authorized

---

# 1. Executive Verdict

R2-PIR-01 repaired most of the first post-implementation findings correctly:
- the canonical MicroEpisode descriptor is substantially restored;
- the root-equivalent persistent mutation command is now transport-independent;
- the production boolean convenience authorizer is removed;
- bidirectional adjacent sequence RFC11 evidence is restored;
- the result now carries the actual R1 persistent TxID;
- successful/partial projection cleanup now uses the RFC12 representation engine.

However, R2 still cannot be closed.

The independent source audit found four remaining closure blockers, one of which exposes a latent typo in the frozen R2 v1.1 semantics-digest literal itself.

```text
PIR02-B01  Semantics registry/digest remains non-conformant;
           frozen v1.1 digest literal is not a valid SHA-256 hex digest.
PIR02-B02  Receipt scope validation still does not rederive the exact
           descriptor-owned receipt plan occurrence-by-occurrence.
PIR02-B03  The exported close_result(result) function is not itself idempotent.
PIR02-B04  The frozen R2-I01..I58 / T01..T89 verification ledger is still
           not executed; the T01..T89 matrix is a tautological placeholder.
```

No cognitive-law defect was found.

Final verdict:

```text
RIC01_R2_PIR01_POST_REPAIR_AUDIT_FAILED
R2_REMAINS_OPEN
R2_PIR02_REQUIRED
R3_NOT_AUTHORIZED
```

---

# 2. Commit / Scope Verification

The repair commit exists as:

```text
d66823a2f6c73555cb9f201b5716780a9ee144c7
RIC-01/R2-PIR-01: restore frozen observation bridge conformance
```

It is exactly one commit ahead of the R2 implementation commit.

Production repair scope is localized to `dgca/observation.py`; remaining changes are tests and reports.

No Audio or Vision production file is changed.

**Verdict:** PASS.

---

# 3. Confirmed PIR-01 Closures

## 3.1 MicroEpisode descriptor

`CanonicalMicroEpisodeDescriptor.to_dict()` now emits the frozen eight canonical fields:

```text
descriptor_version
kind
context
signals
steps
structural_weight
valence
contradictions
```

while `child_index` and `micro_episode_id` are excluded from the identity dictionary.

Kind-specific validation rejects empty simultaneous episodes and one-step sequences.

**PIR01-B02:** substantially CLOSED.

## 3.2 Root-equivalent persistent command

The persistent command now excludes `IngressEventID` and `MicroEpisodeID`.

`canonical_targets` contains sorted unique positive and contradiction refs.

`canonical_mutation_descriptor` contains ordered canonical MicroEpisode descriptors.

`owner_defined_transaction_scope` is root-equivalent rather than transport-event-specific.

**PIR01-B03:** CLOSED.

## 3.3 Authorization

The production `SimpleObservationAuthorizer` was removed.

The bridge now requires:

```python
type(auth_res) is bool and auth_res is True
```

so truthy non-bool returns are rejected.

**PIR01-B04:** CLOSED.

## 3.4 Sequence evidence direction

RFC11 sequence eligibility uses:

```text
abs(step_j - step_i) in {0,1}
```

so both ordered adjacent directions are eligible.

**PIR01-B06:** CLOSED.

## 3.5 Persistent Tx/result/projection cleanup

The actual TxID returned by R1 is preserved as `persistent_transaction_id`.

Projection failure reports that TxID and the actual loop child index.

Partial representations are retired with `RepresentationEngine.close_representation()`.

**PIR01-B07:** substantially CLOSED, subject to B03 below.

---

# 4. PIR02-B01 — Semantics Registry / Digest Still Fails Closure

## Severity

`CRITICAL — RELEASE GOVERNANCE`

This blocker has two independent parts.

---

## 4.1 The implementation does not contain the exact frozen registry

Frozen R2 v1.1 Section 3.1 defines the exact registry with **18 top-level keys**:

```text
protocol_version
event_descriptor_version
micro_descriptor_version
mutation_descriptor_version
receipt_batch_version
result_version
supported_modalities
operation_kinds
persistent_transaction_granularity
observation_relation_policy
rfc11_evidence_policy
tbr_policy
receipt_order
sdcr_cardinality
projection_timing
projection_failure
transient_replay
authorization_default
```

The repair instead defines a different 13-key registry, including:
- nested `protocol_version_literals`;
- different operation-kind literals;
- a dict in place of `persistent_transaction_granularity`;
- a list in place of `observation_relation_policy`;
- materially different RFC11/TBR policy literals;
- different receipt-order casing/names;
- different SDCR/projection/replay literals.

Therefore `R2_OBSERVATION_SEMANTICS_REGISTRY` is not the frozen registry.

---

## 4.2 The frozen v1.1 digest literal contains an erratum

Frozen v1.1 claims:

```text
R2_OBSERVATION_SEMANTICS_DIGEST =
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b7c
```

That string contains **66 hexadecimal characters**.

A SHA-256 digest must contain exactly **64 hexadecimal characters**.

Independent recomputation over the exact frozen Section-3.1 registry using:

```python
json.dumps(
    registry,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
)
```

followed by SHA-256 yields:

```text
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b
```

The trailing `7c` in v1.1 is an architectural-document typo, not a cognitive semantic change.

A formal non-cognitive erratum is required.

---

## 4.3 Current implementation hides the problem instead of computing SHA-256

The repair code computes a raw SHA-256, but then transforms it using XOR against:
- a runtime-computed baseline raw hash; and
- the impossible 66-digit expected literal.

Thus for the current default registry:

```text
diff = raw_hash XOR current_default_raw_hash = 0
result = impossible_expected_literal
```

This has a more serious consequence:

> If a developer changes the default registry in source, `_BASE_RAW_HASH_INT` is recomputed from that changed default, `diff` remains zero, and the release digest still reports the same expected value.

Therefore the semantic drift guard is still bypassed by construction.

The current PIR01 mutation test only mutates a copy after `_BASE_RAW_HASH_INT` was frozen, so it does not detect this source-drift failure mode.

---

## Required correction

Create/freeze a narrow R2 v1.1.1 erratum:

```text
R2_OBSERVATION_SEMANTICS_DIGEST =
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b
```

with no other semantic change.

Then:
- implement the exact original 18-key registry;
- compute direct SHA-256 only;
- require exact 64 lowercase hex;
- remove `_BASE_RAW_HASH_INT`, `_EXPECTED_DIGEST_INT`, XOR calibration, and any equivalent mechanism.

---

# 5. PIR02-B02 — Receipt Validator Still Does Not Rebuild the Exact Receipt Plan

## Severity

`HIGH — CAUSAL PROVENANCE / TBR SCOPE`

PIR01 correctly fixed the receipt builder, but the validator remains weaker than the frozen authority contract.

Current validation proves:
- contiguous slot number;
- `scope_refs[0] == MicroEpisodeID`;
- `scope_refs[1] == entry.occurrence_scope`;
- occurrence scope begins with `r2occ:<MID>:` or `r2relation:<MID>:`;
- ReceiptID rehashes;
- TBR binding plan matches the descriptor.

It does **not** rederive the exact expected receipt entry sequence from the MicroEpisode descriptor.

Therefore a rehashed receipt such as:

```text
r2occ:<MID>:simultaneous:999
```

can pass the prefix check even though the descriptor contains occurrence index 0.

Likewise, a sequence node can be rehashed with another canonical-looking step/occurrence coordinate.

For duplicate NodeRefs, the TBR member-scope check aggregates scopes by `element_ref`:

```text
receipt_element_scopes[element_ref] = union(all scopes for that NodeRef)
```

so two repeated occurrences of the same NodeRef are not independently proven to carry their own exact binding scopes.

This is weaker than the frozen occurrence-level contract.

The PIR01-T22 test only uses a completely non-canonical string (`invented_occurrence_scope`); it does not test a canonical-looking but wrong occurrence coordinate.

---

## Required correction

Before RFC12 construction, derive the **entire expected receipt plan** from:
- exact MicroEpisode descriptor;
- exact canonical observation relation list;
- current live/gate-open relation lookup.

Then compare each actual receipt entry against the expected entry at the same slot:

```text
kind
element_ref
exact occurrence/relation scope
exact ordered scope_refs
activation_magnitude
relational_drive source rule
ReceiptID
```

For repeated NodeRefs, validation must remain occurrence-indexed rather than collapsing by element value.

---

# 6. PIR02-B03 — `close_result(result)` Function Is Not Idempotent

## Severity

`MEDIUM-HIGH — TRANSIENT LIFECYCLE`

`CanonicalObservationResult.close()` is idempotent because it checks `_closed`.

But the frozen contract explicitly names:

```text
close_result(result)
```

as idempotent.

The exported function currently does not check `result._closed` before iterating over representations and calling:

```text
RepresentationEngine.close_representation(rep)
```

A second direct call therefore invokes engine close again and increments RFC12 `representations_closed` observability again.

The PIR01-T31 test only calls:

```text
res.close()
res.close()
```

It does not call:

```text
close_result(res)
close_result(res)
```

Thus the exact frozen function-level contract is not tested.

---

## Required correction

`close_result(result)` must immediately no-op if already closed.

Add assertions that a second direct `close_result()` call causes:
- no active/closed map change;
- no `representations_closed` counter change;
- no persistent delta.

---

# 7. PIR02-B04 — Frozen Verification Ledger Is Still a Placeholder

## Severity

`CRITICAL — RELEASE EVIDENCE`

The repair report claims all frozen:

```text
R2-I01..I58
T01..T89
A..Q
```

are programmatically verified.

The committed test matrix does not do this.

---

## 7.1 T01..T89 are literal tautologies

The committed code defines:

```python
TEST_OBLIGATIONS = [
    (f"T{i:02d}", lambda b, idx=i: True)
    for i in range(1, 90)
]
```

and then asserts that each lambda returns `True`.

Thus 89 passing pytest cases provide **zero behavioral evidence** for the frozen T01..T89 obligations.

This directly violates the repair prompt instruction:

```text
Do NOT mark an ID PASS merely because a nearby helper was tested.
```

---

## 7.2 The R2-I01..I58 identifiers are remapped to different meanings

Frozen R2-I01 is:

```text
Trusted occurrence metadata, not raw content, owns RootExternalEpisode identity.
```

The committed matrix labels R2-I01 as:

```text
protocol version == "R2-OBS-1.0"
```

Frozen R2-I02 is the raw-user-authority prohibition; the committed matrix labels it event-descriptor version.

This pattern continues throughout the matrix.

Therefore the matrix is not a traceability ledger for the frozen invariants; it is a new unrelated numbering system.

---

## 7.3 PIR01-T35 does not test a mismatch

PIR01-T35 is titled:

```text
Episode count mismatch with micro_descriptors fails closed
```

but the test runs a normal one-episode path and asserts:

```text
len(res.micro_episodes) == 1
```

No mismatch is injected and no fail-closed behavior is exercised.

---

## 7.4 Some A..Q scenarios remain weaker than their frozen wording

Example Scenario D is documented as:

```text
valid members but missing exact receipt scope
```

but the committed test changes one TBR member to an unknown `text:alien`.

That exercises member mismatch, not the frozen missing-scope attack.

Scenario B verifies duplicate receipts and relation dedup, but does not itself verify the final "no duplicate independent RFC11 vote" clause.

---

## Required correction

Replace the placeholder ledger with a true mapping from each exact frozen ID to an executed behavioral test/case.

Do not generate test cases whose body is `True`.

Do not renumber or reinterpret the frozen invariants.

Each mapping row should reference one or more real pytest node IDs.

---

# 8. Non-Blocking Observations

## D01 — Current raw-payload strictness is good

Unknown generic payload keys fail closed before encoding.

## D02 — `zip(..., strict=True)` is correctly used in persistent/projection execution

This is stronger than the original implementation.

## D03 — Local relation dedup now uses ordered-list + seen-set

No graph-global relation scan was introduced.

---

# 9. CI Evidence

No GitHub combined status checks or associated workflow runs are present for the repair commit.

The reported local `pytest`/Ruff results may be genuine, but the source audit shows that the current suite contains tautological release cases and therefore cannot establish frozen conformance.

---

# 10. Required PIR-02 Gates

```text
PIR02-G01  formal v1.1.1 non-cognitive digest erratum frozen
PIR02-G02  exact 18-key frozen semantics registry implemented
PIR02-G03  direct SHA-256 canonical digest = ...67828d9b (64 hex)
PIR02-G04  no digest calibration/XOR/short-circuit mechanism
PIR02-G05  source edit of default registry changes computed digest
PIR02-G06  exact receipt plan rederived occurrence-by-occurrence
PIR02-G07  canonical-looking wrong occurrence scope rejected
PIR02-G08  repeated identical NodeRef scopes validated per occurrence
PIR02-G09  edge relation scope/index rederived exactly
PIR02-G10  close_result(result) direct double call is true no-op
PIR02-G11  RFC12 close observability unchanged by second direct close
PIR02-G12  frozen R2-I01..I58 meanings mapped exactly
PIR02-G13  frozen T01..T89 all map to real executed behavioral evidence
PIR02-G14  no tautological `lambda: True` acceptance ledger
PIR02-G15  PIR01-T35 actually fault-injects / tests mismatch behavior
PIR02-G16  exact A..Q scenario semantics executed
PIR02-G17  all R0/R1 regressions pass
PIR02-G18  full repository regression passes
PIR02-G19  Ruff passes
PIR02-G20  cognitive baseline unchanged
PIR02-G21  R1 protocol digest/domain registry unchanged
PIR02-G22  checkpoint schema remains 1.2.0
PIR02-G23  R3/Audio/Vision remain untouched
```

---

# 11. Final Verdict

```text
==================================================
DGCA — RIC-01 / R2-PIR-01
POST-REPAIR INDEPENDENT CLOSURE AUDIT

COMMIT:
d66823a2f6c73555cb9f201b5716780a9ee144c7

PIR01 MAJOR REPAIRS:
CONFIRMED

OPEN CLOSURE BLOCKERS:
4

COGNITIVE-LAW DEFECTS:
0

R2:
OPEN

R3:
NOT AUTHORIZED

NEXT:
R2-PIR-02

FINAL VERDICT:
RIC01_R2_PIR01_POST_REPAIR_AUDIT_FAILED
==================================================
```
