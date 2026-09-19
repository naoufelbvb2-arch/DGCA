# DGCA — RFC13-SR01
## Canonical Snapshot Reprojection & Settling-State Retention Repair
### Formal Repair Specification v1.0 — FROZEN

**Trigger:** SCTT-00 (`E2_RETRIEVAL`)  
**Production baseline:** `833241d54309d72715c42dc5f2b939c3179e257d`  
**Parent architecture:** RFC-13 / Law 15 v1.0 — CLOSED / FROZEN  
**Upstream representation contract:** RFC-12 / SDCR-TBR v1.0 — CLOSED / FROZEN  
**R3-Min:** CLOSED  
**RFC-15:** DEFERRED  
**Status:** FROZEN — IMPLEMENTATION AUTHORIZED ONLY UNDER THIS REPAIR CONTRACT

# 1. Empirical Trigger

SCTT-00 proved: encoder 8/8, authorized persistent exposures 40/40, stored relations 8/8, canonical save/restore PASS, OOD 4/4, zero ordinary-chat persistent delta, restore determinism 8/8. Primary learned recall was 0/8 and classified `E2_RETRIEVAL`.

Read-only tracing showed:

```text
dog current
→ RFC13 discovers dog→canine
→ canine passes eligibility
→ canine is committed
→ canine enters epoch.committed_set
→ next SDCR reconstruction rejects previous-snapshot receipts
→ final CurrentSDCR excludes canine
→ RFC14 receives only dog
→ output = dog
```

# 2. Root Cause

Current RFC13 mixes old participation receipts with newly stamped PATTERN_COMPLETION receipts, then asks RFC12 to build the next canonical SDCR. RFC12 correctly rejects any receipt whose `parent_cycle_id` or `snapshot_or_microtick` does not equal the new snapshot. The same latent defect exists for old `TransientBindingReceipt.parent_snapshot_ref`.

This is not an RFC12 defect. RFC12 must continue rejecting stale receipts and stale TBRs.

# 3. Constitutional Reading

RFC12 requires:

```text
R(t+1) = BuildCurrentSDCR(State(t+1))
```

not blind canonical copy-forward. It also requires origin and binding to be re-proven from current lawful evidence across snapshots.

RFC13 already requires:

```text
CompletedElement enters only through a new runtime snapshot.
Each successful settling iteration re-enters through RFC12 canonical construction.
RFC13 downstream output is the CurrentSDCR.
```

SR01 therefore repairs RFC13's implementation of **current-state reprojection across Law-15 micro-snapshots**.

# 4. Repair Principle

> A successful Law-15 transition must reconstruct the next SDCR from fresh current-snapshot receipts representing the still-lawful current state plus newly committed reinstatements. It must never pass stale receipts or stale TBRs into RFC12 and rely on RFC12 to reinterpret them.

```text
R_k        = current canonical SDCR
D_k        = newly approved completion commits
State*_k+1 = lawfully continuing current participation + D_k
R_k+1      = BuildCanonicalSDCR(FreshReceipts(State*_k+1))
```

This is **validated reprojection**, not blind inheritance.

# 5. No New Cognitive Authority

SR01 adds:

```text
new cognitive laws                0
new persistent cognitive fields   0
new learned scalars               0
new thresholds                    0
new scores/probabilities          0
new identity domains              0
```

Only private transient software helpers are permitted.

# 6. Reprojected Node Participation

A node from current canonical `R_k` may be reprojected only if:
1. it was accepted in `R_k`;
2. the underlying node still exists;
3. participation remains lawful under the unchanged settling context;
4. no explicit invalidation/deactivation event occurred.

The fresh receipt MUST:
- have a new receipt ID;
- use new `parent_cycle_id`;
- use new `snapshot_or_microtick`;
- preserve `element_ref`, `participation_kind`, `scope_refs`;
- preserve current activation/support magnitude;
- preserve provenance lineage.

Preserved provenance is continuity only. It is not a new external observation, Root witness, RFC11 vote, or persistent learning event.

# 7. Reprojected Edge Participation

An edge may be reprojected only if:
- edge still exists;
- gate remains open in current context;
- both endpoints remain current participants;
- scope remains compatible.

The fresh edge receipt preserves element ref, scope, origin lineage and current relational drive, but receives new snapshot coordinates and a new receipt ID.

# 8. New PATTERN_COMPLETION Receipts

Every newly committed target in `D_k` receives a fresh receipt:

```text
origin_lineage = PATTERN_COMPLETION
parent_cycle_id = new cycle
snapshot_or_microtick = new tick
activation_magnitude = approved estimated activation
```

The target must already exist in stored graph state. Completion does not create semantic edges.

# 9. Canonical Receipt Identity

Old receipt IDs MUST NOT be reused.

In canonical mode, use the existing R1 `PARTICIPATION_RECEIPT` derivation. Use a deterministic epoch-local monotonically increasing receipt-slot counter across all settling iterations. It is transient operational state only.

Deterministic emission order:
1. current `R_k` receipt tuple order;
2. new commits sorted by `(target_ref, scope_view, role_ref, proposal_id)`.

# 10. TBR Reprojection

Old TBR objects MUST NOT be passed directly.

A current TBR may be reissued only if:
- every member remains in the new current participants;
- `binding_scope_id` remains valid;
- no incompatible scope transition occurred;
- original binding authority remains lawful.

Fresh TBR:
- fresh binding ID;
- `parent_snapshot_ref=(new_cycle,new_tick)`;
- same binding scope;
- same members;
- same origin view.

If any member is not current: drop the TBR. Never invent a TBR.

# 11. Active Assembly / Context Policy

SR01 does not redefine ActiveAssembly or context policy. Existing pinned `active_assembly_refs` remain governed by Law15 memory-snapshot validity. Persistent structure drift still invalidates the epoch. Assembly membership alone never materializes inactive members.

# 12. Required State Evolution

For stored `A→B`, cue `A`:

```text
R0 = {A}
commit B
R1 = {A,B}
next iteration has no new lawful commit
final = {A,B}
```

Forbidden:

```text
{A} → {B} → {A} → ...
```

For `A→B→C`:

```text
R0={A}
R1={A,B}
R2={A,B,C}
```

subject to existing eligibility, scope, context, competition and budget.

This retention applies only within the same bounded SettlingEpoch and only while participation remains lawful.

# 13. CommittedSet and Root Authority

`CommittedSet` remains authority-use history, not representation state. A committed target cannot recommit, but may remain current in later SDCR snapshots.

`root_authority_refs` remains exactly the original root participation set. Reprojected receipts and PATTERN_COMPLETION descendants do not enlarge it.

# 14. RFC12 Conservation

Forbidden repairs:

```text
accept stale participation receipts
accept wrong parent cycle
accept stale TBR parent_snapshot_ref
disable cross-cycle rejection
mutate old/closed SDCR
blindly copy old TBR objects
treat old representation membership as permanent cross-epoch participation
```

`representation.py` should require no production change. If RFC12 weakening appears necessary: `SR01_BLOCKED`.

# 15. RFC14 / R3 Conservation

RFC14 remains unchanged and still may use only final `settled_rep.participating_node_refs`.

R3 `TransientActivationScope` remains unchanged:
- `N_total` unchanged;
- `A/t_spawn/episode` restored after RFC13;
- persistent digest/ledger/RFC11 state unchanged.

# 16. Mandatory Acceptance Tests

```text
SR01-T01  A→B, cue A: final SDCR contains A and B.
SR01-T02  A→B→C, cue A: snapshots are {A},{A,B},{A,B,C}.
SR01-T03  old participation receipt IDs are never reused.
SR01-T04  every reprojected receipt has current snapshot coordinates.
SR01-T05  external-origin root lineage persists without new root authority.
SR01-T06  PATTERN_COMPLETION lineage remains PATTERN_COMPLETION later.
SR01-T07  CommittedSet prevents recommit while target remains current.
SR01-T08  A↔B settles without representational oscillatory erasure.
SR01-T09  edge reprojection requires lawful/gate-open current edge.
SR01-T10  missing/closed edge is not reprojected.
SR01-T11  valid TBR gets fresh ID/current parent snapshot.
SR01-T12  TBR with noncurrent member is dropped.
SR01-T13  no new TBR is invented.
SR01-T14  stale receipt remains rejected by RFC12.
SR01-T15  stale TBR remains rejected by RFC12.
SR01-T16  active Assembly refs do not materialize inactive members.
SR01-T17  ambiguity remains ambiguity; reprojection creates no winner.
SR01-T18  root witness set remains original.
SR01-T19  no Edge W/n/context mutation.
SR01-T20  no RFC11 structural vote from reprojection.
SR01-T21  canonical replay yields identical final SDCR/outcome.
SR01-T22  remote graph growth does not alter local reprojection.
SR01-T23  R3 scoped completion leaves N_total unchanged.
SR01-T24  R3 restores transient activation before RFC14.
SR01-T25  RFC14 receives final cumulative current SDCR.
SR01-T26  dog→canine counterfactual puts canine in RFC14 input.
SR01-T27  RFC12 suite passes unchanged.
SR01-T28  RFC13 acceptance/property/adversarial suite passes, strengthened not weakened.
SR01-T29  RFC14 suite passes.
SR01-T30  R3-Min suite passes.
```

# 17. Mandatory Adversarial Families

```text
SR01-A01 stale-receipt laundering
SR01-A02 stale-TBR laundering
SR01-A03 external-evidence amplification
SR01-A04 completion-descendant root-witness theft
SR01-A05 receipt-ID collision
SR01-A06 mixed-scope collapse
SR01-A07 closed-context edge resurrection
SR01-A08 missing-node carry-forward
SR01-A09 TBR resurrection
SR01-A10 assembly whole-pattern materialization
SR01-A11 A↔B pumping
SR01-A12 chain budget exhaustion while retaining lawful prefix
SR01-A13 ambiguity resolution by receipt multiplicity
SR01-A14 remote graph contamination
SR01-A15 persistent learning leakage
SR01-A16 RFC11 vote spoofing
```

# 18. Counterfactual Gate

Before production edit, prove:

```text
CURRENT:
dog → commits canine → final {dog}

PROPOSED:
dog → commits canine → final {dog,canine}

CURRENT chain:
rotating/single frontier

PROPOSED chain:
{A}→{A,B}→{A,B,C}
```

Also prove zero persistent mutation, frozen root authority, RFC12 stale rejection and no TBR resurrection.

# 19. Production Scope

Expected production change:

```text
dgca/completion.py
```

Unexpected changes to `representation.py`, `generation.py`, `observation.py`, `causal_identity.py`, `recurrent.py`, `loop.py`, graph laws, Audio or Vision require STOP/review.

# 20. Regression Gates

Run all RFC12/RFC13/RFC14/R3/R2/R1/R0 tests, full pytest and Ruff.

Frozen constants remain:
- Cognitive law signature `915119d40643cb97`
- R1 `f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398`
- R1 domains `21`
- R2 `bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b`
- R3 `fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc`
- checkpoint/runtime `1.2.0`
- observation `R2-OBS-1.0`

RFC13 behavioral signature may lawfully change because final-SDCR behavior was defective; report old/new explicitly.

# 21. SCTT-00 Rerun

After implementation and regressions, rerun the exact frozen SCTT-00 unchanged. No extra exposures or tuning.

# 22. Verdict

```text
RFC13-SR01 FORMAL REPAIR
RFC12 STRICT ISOLATION: PRESERVED
LAW15 ROOT AUTHORITY: PRESERVED
COMMITTEDSET SEMANTICS: PRESERVED
PERSISTENT LEARNING: UNCHANGED
NEW LAW: NO
NEW PERSISTENT PRIMITIVE: NO
RFC14: UNCHANGED
RFC15: DEFERRED
IMPLEMENTATION: AUTHORIZED SUBJECT TO COUNTERFACTUAL + TEST GATES
```
