# DGCA — RIC-01 / R1-PIR-01
## Post-Repair Independent Audit v1.0

**Program:** `RIC-01 — Canonical Runtime Integration Contract`  
**Stage audited:** `R1-PIR-01 — Post-Implementation Repair 01`  
**Authoritative R1 architecture:** `RIC-01-R1-Deterministic-Causal-Identity-Protocol-v1.3-FROZEN.md`  
**Repair commit:** `bf764033dbbeec59c507e0f137d2fbbb513582e1`  
**Repair base:** `d05af8e2f1f68bd7beef8909c01e23260274f62a`  
**Audit mode:** Independent read-only source audit against the frozen R1 contract  
**Repository mutation:** `NONE`  
**R2 authorization:** `NO`

---

# 1. Executive Verdict

The PIR-01 repair materially improves the R1 implementation. The audited commit is exactly one commit ahead of the original R1 implementation and is narrowly scoped to R1 repair files. It closes important parts of the first audit, including:

```text
R0 semantic compatibility firewall reuse
RFC13 canonical-path propagation improvements
RFC14 canonical frame/occurrence/surface integration
RFC15 canonical recurrent propagation improvements
shared atomic file publication with directory fsync
semantic causal-ledger restore checks
non-string canonical mapping-key rejection
```

However, independent source review finds that PIR-01 does **not yet close R1**. Several gaps remain in protocol governance, runtime encapsulation, provenance-epoch semantics, mode isolation, canonical object identity consistency, RFC16 delivery integration, pre-mutation provenance validation, and migration-disclosure preservation.

The reported local test counts are not disputed, but GitHub exposes no commit-status/CI checks for this commit. More importantly, the residual defects are visible directly in the committed source and are not covered by the new PIR-01 tests.

```text
==================================================
DGCA — RIC-01 / R1-PIR-01
POST-REPAIR INDEPENDENT AUDIT v1.0

REPAIR COMMIT:
bf764033dbbeec59c507e0f137d2fbbb513582e1

PIR-01 MATERIAL IMPROVEMENT:
YES

ORIGINAL 7-BLOCKER AUDIT:
SUBSTANTIALLY ADDRESSED

NEW / RESIDUAL CLOSURE BLOCKERS:
9

FATAL COGNITIVE-LAW DEFECTS:
0

COGNITIVE BASELINE CHANGE AUTHORIZED:
NO

R1 STATUS:
OPEN — PIR-02 CLOSURE REQUIRED

R2:
NOT AUTHORIZED

FINAL VERDICT:
RIC01_R1_PIR01_POST_REPAIR_AUDIT_FAILED
==================================================
```

---

# 2. Positive Findings

## PR-A01 — Commit lineage and scope discipline

The repair commit is a single commit on top of `d05af8e...`. The production diff is confined to:

```text
dgca/causal_identity.py
dgca/completion.py
dgca/generation.py
dgca/persistence.py
dgca/recurrent.py
dgca/__init__.py
```

plus R1/PIR tests and reports.

No Audio or Vision production file is changed.

**Verdict:** PASS.

## PR-A02 — R0 semantic firewall is now reused by R1

`validate_semantic_compatibility(...)` checks the runtime/schema contract, cognitive semantics, region digest, active-law digest, policy digest, combined semantics digest, and—under schema 1.2.0—the R1 identity/observation compatibility fields.

It is invoked by the R1 restore and by the 1.1.1→1.2.0 migration path.

**Verdict:** PASS.

## PR-A03 — RFC13 canonical propagation improved

Canonical edge candidates now use `derive_pattern_candidate_id`, proposals receive canonical derivation, canonical settling requires an explicit `work_ref`, and the next SDCR is rebuilt through the canonical representation path.

**Verdict:** SUBSTANTIALLY PASS, with mode-cache defect remaining.

## PR-A04 — RFC14 canonical frame/occurrence/surface integration improved

Canonical frame IDs, occurrence IDs, SurfaceUnit IDs, and SurfaceChunk IDs are now connected to the actual generation engine path. Chunk identity now uses actual `closure_reason` and `origin_lineage`.

**Verdict:** SUBSTANTIALLY PASS, with post-expansion frame-identity defect remaining.

## PR-A05 — RFC15 canonical propagation improved

Canonical recurrent execution now propagates the canonical flag through obligation derivation, continuation commit, RFC14 generation, and ExpressionReceipt construction.

**Verdict:** SUBSTANTIALLY PASS, with protocol-domain and progress-digest defects remaining.

## PR-A06 — R1 save durability repaired

R0 and R1 now share `_atomic_replace_file(...)` with:

```text
same-directory temporary file
flush
file fsync
os.replace
directory fsync where supported
```

**Verdict:** PASS.

## PR-A07 — Causal-ledger restore checks are stronger

The repair rejects key/record mismatch, missing event binding, root mismatch, event digest mismatch, and observation-protocol mismatch before constructing the restored ledger.

**Verdict:** SUBSTANTIALLY PASS, with epoch semantics and save-time validation defects remaining.

---

# 3. Blocker PIR02-B01 — Hidden Unregistered ExpressiveObligation Identity Domain

## Severity

`CRITICAL — PROTOCOL GOVERNANCE`

## Frozen rule

The R1 identity protocol has an exact compatibility-bound literal domain registry. The registry contains 21 domains and does **not** contain:

```text
EXPRESSIVE_OBLIGATION
```

Any identity-domain/formula change requires explicit identity-protocol compatibility governance.

The frozen Section 33 requires a domain-separated canonical obligation encoding but does not authorize silently extending the literal registry.

The PIR-01 repair prompt explicitly prohibited adding a new hidden domain.

## Current code

The repair adds:

```python
derive_expressive_obligation_id(...)
```

which manually hashes:

```text
DGCA:R1:ID:v1
NUL
EXPRESSIVE_OBLIGATION
NUL
canonical_json(payload)
```

without registering `EXPRESSIVE_OBLIGATION` in `LITERAL_DOMAIN_REGISTRY` and without changing `CAUSAL_IDENTITY_PROTOCOL_DIGEST`.

This creates an effective 22nd R1 identity domain outside the compatibility firewall.

The helper also converts:

```python
semantic_element_ref=str(r.element_ref)
```

which can erase type distinctions between a typed reference and a string that happens to contain the same representation.

## Required closure

Do **not** add a new literal domain under protocol version 1.0.

Freeze one sanctioned mapping through an existing R1 domain. PIR-02 freezes:

```text
ExpressiveObligationID
=
DGCA_ID(
  "INTERNAL_WORK",
  {
    "root_authority_ref": ...,
    "subsystem_kind": "EXPRESSIVE_OBLIGATION",
    "scope_refs": [role_scope],
    "prerequisite_work_ids": [],
    "work_index_or_role": {
      "semantic_element_ref": canonical typed reference,
      "alternative_branch_id": ...
    }
  }
)
```

No stringification of typed semantic references.

---

# 4. Blocker PIR02-B02 — Canonical Runtime Still Exposes Live Mutable Graph and Ledger State

## Severity

`CRITICAL — LINEAGE INTEGRITY`

## Frozen rule

Production canonical APIs MUST NOT expose an unguarded public persistent-write path.

Unsafe raw access is allowed only if lineage is invalidated before mutable access is returned.

## Current code

The new `CognitiveGraphInspectionView` is described as read-only, but its API returns live mutable objects:

```text
nodes              → live dict of mutable Node
edges              → live dict of mutable Edge
X                  → live dict/set structure
assembly_manager   → live mutable AssemblyManager
representation_engine / completion_engine / generation_engine /
recurrent_engine / loop_engine → live engine objects
edge(...)           → live mutable Edge
node(existing)      → live mutable Node
__getattr__          → forwards arbitrary graph methods/attributes
```

Only direct proxy methods `link`, `unlink`, and `observe` invalidate lineage.

Therefore a caller can mutate persistent state while lineage remains `VALID`, for example:

```python
runtime.graph.edge("a", "b").W = 999
runtime.graph.nodes["x"] = Node(...)
runtime.graph.X["a"] = {"b"}
runtime.graph.assembly_manager.pending_growth[...] = ...
runtime.graph.loop_engine.process_validated_learning(...)
```

and then canonical-save.

The same structural problem exists for `runtime.ledger`, which remains a public mutable `CausalCommitLedger` exposing mutable dictionaries.

## Required closure

Canonical runtime ownership must become:

```text
_graph   private mutable CognitiveGraph
_ledger  private mutable CausalCommitLedger
```

Public inspection APIs return detached immutable snapshots/copies only.

No public inspection facade may:

```text
return live Node/Edge
return live dict/set
return live AssemblyManager
return live engine
forward unknown attributes via __getattr__
```

Raw graph/ledger access, if retained for developer compatibility, must be explicit `unsafe_*` access and invalidate lineage before returning the mutable object.

Internal canonical orchestration may continue to use private `_graph` / `_ledger`.

---

# 5. Blocker PIR02-B03 — Provenance Epoch Semantics Are Incorrect and Migrated Runtimes Can Become Non-Restorable

## Severity

`CRITICAL — PERSISTENCE / PROVENANCE`

## Frozen rule

`CausalProvenanceEpoch` is coverage-baseline metadata:

```text
epoch_id
history_status
base_state_digest
```

Its ID is deterministic from:

```text
base_state_digest
source_schema
causal_identity_protocol_version
```

`base_state_digest` identifies the state at which this provenance-coverage epoch began. It is not the digest of every future checkpoint.

## Current code defect 1 — arbitrary epoch IDs

`CausalProvenanceEpoch` validates only `history_status`.

The runtime/tests may instantiate arbitrary IDs such as:

```text
epoch_test_pir
epoch_test_16
```

Neither construction nor restore recomputes the frozen deterministic epoch ID.

## Current code defect 2 — PRE_R1 epoch baseline is compared against every future state

The validator currently enforces:

```python
if (
    history_status == "PRE_R1_HISTORY_UNAVAILABLE"
    or not has_transactions
) and base_state_digest != checkpoint_state_digest:
    fail
```

For a migrated pre-R1 checkpoint:

```text
baseline state = D0
epoch.base_state_digest = D0
history_status = PRE_R1_HISTORY_UNAVAILABLE
```

After the first legitimate tracked R1 mutation:

```text
current state = D1
base remains D0
```

Saving is allowed, but restore rejects because `PRE_R1_HISTORY_UNAVAILABLE` forces `D0 == D1`.

This makes migrated runtimes non-restorable after legitimate tracked learning.

## Current code defect 3 — checkpoint build mutates provenance metadata

`build_canonical_r1_checkpoint(...)` may silently rewrite `ledger.epoch.base_state_digest` for an empty ledger, but it does not recompute `epoch_id`.

Checkpoint serialization must not repair provenance metadata by mutating runtime state.

## Required closure

PIR-02 freezes:

```text
base_state_digest is immutable epoch-start state
epoch_id is deterministic and validated
checkpoint builder never mutates the epoch
```

Source-schema mapping for v1.0:

```text
native R1_TRACKED epoch:
    source_schema = "1.2.0"

all pre-R1 migration chains:
    normalize through 1.1.1
    epoch source_schema = "1.1.1"
```

Validation rule:

```text
if committed_transactions is empty:
    current checkpoint state MUST equal epoch.base_state_digest
else:
    current state may differ from epoch.base_state_digest
```

independent of `R1_TRACKED` vs `PRE_R1_HISTORY_UNAVAILABLE`.

`history_status` describes coverage before the baseline, not whether future state may change.

---

# 6. Blocker PIR02-B04 — RFC13 Candidate Cache Cross-Contaminates Canonical and Legacy Modes

## Severity

`HIGH — IDENTITY MODE SEPARATION`

## Frozen rule

Canonical R1 mode is additive and explicit.

Legacy callers must remain explicitly non-canonical and must not silently receive canonical identities.

## Current code

`discover_candidates(...)` uses cache key:

```python
f"{representation.representation_id}|{rcc_filter or 'all'}"
```

but does not include `canonical_identity`.

Therefore:

```text
legacy call first
→ cache contains legacy candidate IDs
→ canonical call returns legacy IDs

canonical call first
→ cache contains canonical IDs
→ legacy call returns canonical IDs
```

This violates both canonical determinism and legacy/canonical mode separation.

## Required closure

Include identity mode in cache identity, or cache only identity-neutral descriptors and derive IDs per mode.

Mandatory replay order tests:

```text
LEGACY → CANONICAL
CANONICAL → LEGACY
```

on the same engine.

Also remove heterogeneous `key=str` identity ordering where possible; pass unordered semantic sets into the canonical R1 canonicalizer so ordering is based on canonical JSON bytes.

---

# 7. Blocker PIR02-B05 — Canonical GenerativeFrameID Becomes Stale After Hierarchy Expansion

## Severity

`HIGH — OBJECT IDENTITY CONSISTENCY`

## Frozen rule

Canonical `GenerativeFrameID` binds:

```text
parent RepresentationID
anchors
scope
role bindings
```

## Current code

`build_generative_frame(... canonical_identity=True)` correctly derives a canonical frame ID.

But `expand_hierarchy(...)` adds new `role_bindings` using:

```python
dataclasses.replace(target_frame, role_bindings=updated_bindings)
```

while preserving the old `frame_id`.

The semantic descriptor has changed while the identity remains the pre-expansion identity.

Downstream canonical occurrence IDs then use this stale frame ID.

## Required closure

Canonical hierarchy expansion must:

1. recompute the canonical frame ID whenever identity-bearing frame fields change;
2. remap hierarchy dictionary keys;
3. remap any parent/child frame references affected by the ID change;
4. preserve deterministic hierarchy topology;
5. keep legacy expansion behavior unchanged.

---

# 8. Blocker PIR02-B06 — Canonical ContinuationCommit Stores a Different Progress Digest Than Its Own ID Uses

## Severity

`HIGH — SELF-INCONSISTENT CANONICAL OBJECT`

## Frozen rule

`ContinuationCommitID` binds:

```text
epoch_id
parent_representation_id
obligation_id
progress_snapshot_digest
```

and the stored commit's `progress_snapshot_digest` must be that same canonical progress digest.

## Current code

Canonical branch computes:

```python
progress_digest =
SHA256(canonical_json_bytes(list(epoch.progress_receipt_refs)))
```

and derives `commit_id` from it.

Immediately afterward the function unconditionally overwrites `progress_digest` with:

```python
SHA256(",".join(epoch.progress_receipt_refs).encode())
```

and stores this second digest in the `ContinuationCommit`.

Thus the ID cannot be re-derived from the committed object's own stored fields.

## Required closure

Compute one progress digest per mode.

For canonical mode:

```text
stored progress_snapshot_digest
==
digest used to derive ContinuationCommitID
```

Add a test that re-derives the canonical commit ID strictly from the returned commit object.

### Related GCE authority hardening

In canonical mode, caller-supplied `epoch_id` must not masquerade as canonical authority.

Either:

```text
reject epoch_id override
```

or:

```text
derive expected canonical GCEID
require supplied epoch_id == expected
```

Canonical `work_ref` must reject empty/whitespace values.

---

# 9. Blocker PIR02-B07 — RFC16 Canonical DeliveryID Is Still Helper-Only

## Severity

`HIGH — DOWNSTREAM INTEGRATION`

## Frozen rule

Section 37 freezes canonical DeliveryID:

```text
DGCA_ID(
  "DELIVERY",
  {
    "surface_chunk_id": ...,
    "parent_representation_id": ...,
    "delivery_channel_ref": optional
  }
)
```

Same committed chunk retry must retain the same DeliveryID.

## Current code

`derive_delivery_id(...)` exists.

But actual:

```python
UnifiedGenerativeCognitiveLoopEngine.deliver_surface_output(...)
```

still constructs:

```text
del_<truncated sha256(chunk_id + parent_rid)>
```

with no canonical mode.

The existing R1 acceptance test tests the helper, not actual RFC16 delivery integration.

## Required closure

Add an additive canonical delivery path:

```text
canonical_identity=True
delivery_channel_ref=...
```

using `derive_delivery_id(...)`.

Preserve legacy default behavior.

`retry_delivery()` must retain the original canonical ID exactly.

R2 ingress/learning policy remains out of scope.

---

# 10. Blocker PIR02-B08 — Canonical Persistent Command Accepts Invalid Provenance Before Mutation and Save Does Not Revalidate Ledger Semantics

## Severity

`CRITICAL — FAIL-CLOSED TRANSACTION INTEGRITY`

## Frozen rule

Canonical provenance must be valid before a persistent owner mutation executes.

A canonical checkpoint may not serialize semantically invalid causal provenance.

## Current code

`execute_persistent_command(...)` accepts caller-provided:

```text
root_external_episode_id
ingress_event_id
event_descriptor_digest
```

and stages a binding before mutation, but the staging path does not enforce the same semantic shape rules used on restore.

Malformed provenance can therefore:

```text
mutate graph
commit ledger
leave runtime HEALTHY
save checkpoint successfully
```

only to fail on later restore.

`build_canonical_r1_checkpoint(...)` serializes `ledger.to_dict()` without calling `validate_causal_provenance_state(...)` before publication.

## Required closure

Before mutator callback:

```text
validate non-empty root/event IDs
validate event_descriptor_digest exact canonical 64 lowercase hex
validate observation protocol consistency
validate replay binding compatibility
```

Where canonical Root/Event IDs are expected, validate authoritative digest form without attempting semantic reconstruction unavailable at this layer.

Before canonical save:

```text
validate_causal_provenance_state(...)
```

against the candidate checkpoint state digest and observation protocol **before** atomic file publication.

If runtime provenance is invalid:

```text
FAIL CLOSED
do not publish checkpoint
```

A provenance validation error before owner mutation must not execute the owner callback.

---

# 11. Blocker PIR02-B09 — Chained Legacy→R1 Migration Drops Earlier R0 Loss Disclosures

## Severity

`HIGH — MIGRATION TRUTHFULNESS`

## Frozen rule

Migration must never fabricate or hide unavailable history.

R0 legacy migration explicitly discloses that RFC11 pending structural evidence was not serialized and cannot be recovered.

R1 migration additionally discloses that pre-R1 causal commit history is unavailable.

Both facts remain true after a chained migration.

## Current code

Canonical R1 restore chains:

```text
1.0 → 1.1.1 → 1.2.0
1.1 → 1.1.1 → 1.2.0
```

but discards the earlier migration report and returns only the final 1.2.0 report.

`migrate_schema_1_1_1_to_1_2_0(...)` also overwrites the single `diagnostic_metadata["migration_report"]`.

Consequently a v1.0→v1.2.0 canonical migration can lose the earlier disclosure:

```text
RFC11 pending structural evidence cannot be recovered
```

and a v1.1 chain can lose its historical ordered-sequence limitation note.

## Required closure

Preserve an ordered diagnostic migration chain, e.g.:

```text
diagnostic_metadata.migration_chain = [
  report_1,
  report_2,
  ...
]
```

The returned developer diagnostic should expose all accumulated loss disclosures.

Do not collapse distinct unrecoverable-state disclosures.

---

# 12. Non-Blocking Hardening Debt

## PIR02-D01 — Digest shape should be exact canonical lowercase

Restore validator currently accepts uppercase hex and a broad underscore-prefix form for transaction IDs.

Canonical runtime produces lowercase full SHA-256 identities.

Tighten restored canonical IDs/digests to the exact authoritative form where the frozen record type requires it.

## PIR02-D02 — Directory fd close on fsync exception

The shared directory-fsync path may leave `dir_fd` unclosed if directory `fsync()` raises before `os.close()`.

Use `try/finally` around the directory fd.

## PIR02-D03 — PIR01-T19 does not assert directory fsync invocation

The implementation visibly contains directory fsync, so this is not a current implementation blocker. Add a mock/fault-injection assertion during PIR-02 to prevent regression.

---

# 13. Why the Current 27 PIR Tests Are Not Sufficient

The new tests validate many repairs, but they do not exercise the remaining failure modes.

Examples:

```text
PIR01-T09/T10
validate only the initially constructed frame/occurrence identities;
they do not expand a canonical frame and revalidate its ID.

PIR01-T13/T15
show recurrent replay stability but do not verify that returned
ContinuationCommit.progress_snapshot_digest re-derives commit_id.

PIR01-T17
calls runtime.graph.link(), which is one of the three explicitly
intercepted proxy methods; it does not mutate a returned Edge/Node/dict/manager.

PIR01-T20..T25
validate restore-time malformed provenance, but do not verify invalid
provenance is rejected before an owner mutation or before canonical save.

No PIR01 test
runs LEGACY→CANONICAL and CANONICAL→LEGACY candidate discovery through
the same RFC13 candidate cache.

No PIR01 test
executes actual RFC16 canonical DeliveryID integration.

No PIR01 test
migrates pre-R1 state, executes a real persistent mutation, saves,
and restores again.

No PIR01 test
checks deterministic provenance epoch_id against the frozen formula.
```

---

# 14. PIR-02 Required Closure Gates

R1 may close only after:

```text
PIR02-G01  no hidden identity domain outside literal registry
PIR02-G02  obligation identity uses sanctioned frozen domain mapping
PIR02-G03  canonical runtime exposes no live mutable graph/provenance via safe API
PIR02-G04  unsafe graph/ledger access invalidates lineage before access
PIR02-G05  provenance epoch ID deterministic and validated
PIR02-G06  pre-R1 baseline epoch remains restorable after tracked mutations
PIR02-G07  checkpoint build never mutates provenance epoch metadata
PIR02-G08  RFC13 cache separates CANONICAL_R1 and LEGACY_NON_CANONICAL
PIR02-G09  canonical expanded GenerativeFrame has descriptor-consistent ID
PIR02-G10  canonical ContinuationCommit stores its identity-bound progress digest
PIR02-G11  canonical GCE cannot accept arbitrary masquerading epoch ID
PIR02-G12  actual RFC16 delivery path supports canonical DeliveryID
PIR02-G13  invalid event provenance rejected before owner mutation
PIR02-G14  invalid provenance rejected before checkpoint publication
PIR02-G15  chained migration preserves all prior loss disclosures
PIR02-G16  all PIR01 tests remain passing
PIR02-G17  all original R1 tests remain passing
PIR02-G18  R0/C01/C02/C03 remain passing
PIR02-G19  full repository regression passes
PIR02-G20  Ruff passes
PIR02-G21  cognitive baseline remains 915119d40643cb97
PIR02-G22  protocol digest remains frozen unless explicit governance says otherwise
PIR02-G23  R2/R3/Audio/Vision remain untouched
```

---

# 15. Closure Decision

PIR-01 is a real improvement and should remain as the repair base.

Do not roll it back.

But R1 is not yet independently closable.

The correct next artifact is:

```text
RIC-01 / R1-PIR-02
Final Causal Identity Closure Specification
```

followed by a narrowly scoped implementation/verification prompt.

```text
FINAL VERDICT:
RIC01_R1_PIR01_POST_REPAIR_AUDIT_FAILED
```
