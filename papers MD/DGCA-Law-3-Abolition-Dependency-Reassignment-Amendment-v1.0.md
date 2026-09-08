# DGCA — Law 3 Abolition & Dependency Reassignment Amendment v1.0

## إلغاء قانون التآكل والتقليم والموت الخلوي وإعادة إسناد السلطات المعمارية المتبقية

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Document Type:** Formal Architectural Amendment  
**Version:** 1.0  
**Architectural Decision:** **CLOSED**  
**Implementation Status:** **PENDING**  
**Scope:** Law 3 abolition, dependency repair, authority reassignment, and post-abolition verification  
**New Cognitive Primitives:** 0  
**New Normative Laws:** 0  
**Primary Principle:** **Persistence by Default — Revision by Evidence — Retirement by Lawful Ownership**

---

# 1. Executive Decision

This amendment formally closes the architectural review of:

> **Law 3 — Decay, Pruning & Cellular Death**

The prior Law 3 combined four distinct mechanisms:

1. time-based learned-edge weight decay;
2. time-based salience decay;
3. universal low-weight edge pruning;
4. orphan-node cellular death / garbage collection.

Subsequent real-data diagnosis and dedicated persistence forensics established that correct Nodes and Edges are created, but ordinary learned Edges are destroyed by the current Law-3 timescale before sparse natural recurrence can reliably reinforce or consolidate them.

The architectural review therefore rejects the premise that learned knowledge should weaken merely because unrelated perception ticks pass.

The final decision is:

\[
\boxed{
UniqueArchitecturalNecessity(Law3)=FALSE
}
\]

and:

\[
\boxed{
\textbf{LAW 3 — ABOLISHED}
}
\]

No replacement forgetting law is introduced.

The lawful functions previously mixed into Law 3 are either:

- **removed completely** because they have no unique necessity;
- **returned to an existing semantic owner**;
- or retained only as **local storage/lifecycle mechanisms**, not cognitive laws.

---

# 2. Empirical Basis

The decision is grounded in **DGCA Phase 2.5 — Law-3 Persistence Forensics Trial 01**.

The trial established:

```text
Node Creation Yield: 100.0%
Edge Creation Yield: 100.0%

PF-1:
Unique Nodes Ever Created: 78
Unique Edges Ever Created: 272

PF-2:
Ordinary Unprotected Edge Lifetime: 16 non-reinforcing ticks
Observed Law-3 trajectory: bit-exact with frozen equation

PF-4:
Nodes whose last edge was Law3-pruned: 6
Nodes orphaned: 6
Eligible orphans deleted: 6

PF-5:
Nodes ever created: 167
Nodes GC-deleted: 120
Final alive nodes: 47

Edges ever created: 568
Edges pruned: 452
Final alive edges: 116

Natural recurrence:
Median inter-exposure gap: 20 ticks
75% of observed recurrences recreated dead edges rather than reinforcing living edges
```

The causal chain was directly observed:

\[
\boxed{
EdgeCreation
\rightarrow
Law3Decay
\rightarrow
EdgePruning
\rightarrow
NodeOrphaning
\rightarrow
CellularDeath
}
\]

The principal defect was therefore not failure to form memory.

It was failure of formed memory to survive.

---

# 3. Supersession Rule

Upon adoption of this amendment, the former normative text:

> **Law 3 — Decay, Pruning & Cellular Death**

is superseded in full.

The law number is **not reused or renumbered**.

The formal lawbook shall retain a tombstone entry:

```text
LAW 3 — ABOLISHED / RESERVED

Former title:
Decay, Pruning & Cellular Death

Status:
ABOLISHED

Reason:
No unique architectural necessity remained after empirical persistence
forensics and authority decomposition.

No runtime authority may be assigned to Law 3.
```

Laws 4 and above retain their historical numbering.

\[
\boxed{
NoLawRenumbering=TRUE
}
\]

This preserves document lineage, test lineage, and historical references.

---

# 4. Core Memory Principle After Abolition

The revised DGCA memory philosophy is:

\[
\boxed{
\textbf{Persistent by Default}
}
\]

\[
\boxed{
\textbf{Strengthened by Positive Evidence}
}
\]

\[
\boxed{
\textbf{Corrected by Negative Evidence}
}
\]

\[
\boxed{
\textbf{Retired only by Explicit Lawful Ownership}
}
\]

\[
\boxed{
\textbf{Operational Garbage Collected Locally}
}
\]

For an ordinary persistent learned Edge \(e_{ij}\):

\[
\boxed{
NoLawfulUpdateEvent(e_{ij},t)
\Rightarrow
W_{ij}(t+1)=W_{ij}(t)
}
\]

Therefore:

\[
\boxed{
NoEvidence \neq NegativeEvidence
}
\]

and:

\[
\boxed{
Inactivity \neq Invalidity
}
\]

and:

\[
\boxed{
LowWeight \neq DeletionAuthority
}
\]

---

# 5. Functions Removed Completely

The following former Law-3 mechanisms are deleted and receive **no new owner**.

## 5.1 Time-Based Learned-Weight Decay — REMOVED

Former rule:

\[
W_{ij}(t+1)
=
\max
\left(
W_{floor}(ij),
W_{ij}(t)-\lambda_{decay}
\right)
\]

is abolished for ordinary learned persistent Edges.

The global constant:

```text
LAMBDA_DECAY
```

must no longer have authority over persistent learned knowledge.

No equivalent global, local, lazy, or hidden age-based weight decay may be introduced by this amendment.

---

## 5.2 Time-Based Salience Decay — REMOVED

Former rule:

\[
S_{ij}(t+1)
=
\max(0,S_{ij}(t)-\lambda_S)
\]

is abolished.

The constant:

```text
LAMBDA_SAL
```

is removed from Law-3 semantics.

Salience may remain a Law-8 concept, but unrelated elapsed time is not, by itself, authority to modify it.

---

## 5.3 Universal Low-Weight Pruning — REMOVED

Former rule:

\[
W_{ij}\le\theta_{prune}
\land
Locked=0
\land
\neg is\_intrinsic
\Rightarrow
DeleteEdge
\]

is abolished.

The constant:

```text
THETA_PRUNE
```

must no longer serve as a universal learned-memory deletion threshold.

No equivalent rule may be reintroduced under another name.

Specifically forbidden:

```text
if edge.weight < X:
    delete(edge)
```

when low support is the sole retirement cause.

---

## 5.4 Global Per-Tick Decay Sweep — REMOVED

The runtime must no longer iterate over all non-updated learned Edges for cognitive decay.

The architecture rejects:

\[
EveryGlobalTick
\Rightarrow
MutateUnrelatedMemory
\]

This removes a global coupling between unrelated experiences.

---

## 5.5 Global Post-Decay Node Sweep — REMOVED

The former:

```text
decay all edges
then scan all nodes
then delete zero-degree inactive nodes
```

cycle is abolished.

Orphan reclamation remains allowed only as a local lifecycle consequence of an already-authorized structural removal.

---

# 6. Authority Reassignment Matrix

| Former Law-3 responsibility | Final decision | New authority |
|---|---|---|
| Time-based learned-weight decay | **REMOVE** | None |
| Time-based salience decay | **REMOVE** | None |
| Universal low-weight pruning | **REMOVE** | None |
| Positive support accumulation | Existing behavior retained | **Law 2** |
| Negative evidence correction | Existing behavior retained/repaired | **Law 13** |
| Consolidated-status semantics | Retained/redefined | **Law 5** |
| Salience/significance semantics | Retained/redefined | **Law 8** |
| Persistent event-role lifecycle | Retained/repaired | **Law 11** |
| Episode/source boundary | Retained | **Law 6** |
| Transient `inst:*` scope retirement | Explicit lifecycle | Existing episode/modality owner |
| Derived `sim` retirement | Existing topology owner | **Law 9** |
| Structural/hypothesis retirement | Existing structural owner | Existing owning law/RFC |
| Safe physical Edge/Node removal | Mechanism only | Graph/RFC-10 lifecycle layer |
| Orphan reclamation | Local invariant only | Graph lifecycle layer |
| Assembly sanitation after lawful removal | Reaction only | **Law 14** |
| System clock / `/tick` | Operational time only | RFC-09 runtime |

No single replacement owner inherits Law 3.

\[
\boxed{
NoUniversalForgettingOwner
}
\]

---

# 7. Revised Weight Semantics

After abolition, persistent learned Edge weight is no longer:

\[
EvidenceStrength-AgePenalty
\]

It is governed by lawful evidence events.

Conceptually:

\[
\boxed{
W
=
PositiveSupport
-
EvidenceDrivenCorrection
}
\]

subject to the existing bounded weight domain.

The canonical three-way rule is:

### Positive evidence

\[
Evidence^+
\xrightarrow{Law2}
W\uparrow
\]

### Negative validated evidence

\[
Evidence^-
\xrightarrow{Law13}
W\downarrow
\]

### No relevant evidence

\[
\boxed{
NoEvidence
\Rightarrow
W'=W
}
\]

This amendment introduces no passive weakening path.

---

# 8. Amendment to Law 2 — Cumulative Dual Reinforcement

Law 2 remains the owner of lawful positive reinforcement.

No change is made to its positive Hebbian update equation.

The Law-2 text must remove any implication that Law 3 is the normal opposing force.

The existing locked-edge interaction remains subject to revised Law 5 and Law 13.

Normative boundary:

\[
\boxed{
Law2OwnsPositiveEvidence
}
\]

Law 2 does not:

- decay inactive edges;
- retire edges;
- perform resource cleanup.

---

# 9. Amendment to Law 5 — Consolidation & Revision Stability

## 9.1 Revised Intent

The former intent:

> protect established knowledge from Law-3 forgetting

is removed.

Law 5 is redefined as:

> **Consolidation & Revision Stability** — identify relations supported by repeated, sufficiently diverse lawful evidence and place them into a stable established state that requires stronger counter-evidence for revision.

Law 5 no longer exists as an anti-decay shield.

---

## 9.2 Lock Acquisition

The existing acquisition criteria may remain:

\[
AcquireLock(ij)
\iff
(W_{ij}\ge\theta_{solid})
\land
(n_{ij}\ge N_{min})
\land
(|\mathcal{C}_{ij}|\ge\kappa \lor g_{ij}\neq\varnothing)
\land
(k_{fail}<K_{fail})
\]

with the currently frozen acquisition constants unless separately amended later.

---

## 9.3 Lock Lifecycle

`Locked` becomes an explicit established-state hysteresis flag.

State transition:

\[
Unlocked
\xrightarrow{Law5\ acquisition}
Locked
\]

and:

\[
Locked
\xrightarrow{Law13\ repeated\ validated\ failure}
Unlocked
\]

A locked Edge does not become unlocked merely because time passes.

---

## 9.4 Remove Protection Floor

The former Law-5 rule:

\[
W_{floor}=\theta_{solid}
\]

for locked Edges is removed as an anti-decay mechanism.

The former statement:

> abandoned locked edges decay to 0.75 but never disappear

is deleted.

Without Law 3:

\[
NoEvidence
\Rightarrow
W'=W
\]

therefore no anti-decay floor is required.

---

## 9.5 `inst:*` Exemption Rewritten

The old rationale:

> transient instances must be excluded from locking so Law 3 can kill them

is removed.

Transient objects remain excluded from persistent consolidation because their ontology is **scope-limited**, not because they need to decay.

Their retirement is owned by transient lifecycle authority.

---

# 10. Amendment to Law 8 — Affective & Structural Salience

## 10.1 Revised Intent

Law 8 retains ownership of:

- surprise-derived salience;
- affective salience;
- structural salience;
- salience tagging.

It loses all authority to create a learned-memory survival floor.

Salience is interpreted as:

\[
\boxed{
Significance/Priority
}
\]

not:

\[
\boxed{
RightToSurviveDecay
}
\]

---

## 10.2 Remove `W_floor` Coupling

The former rule:

\[
W_{floor}(ij)=\theta_{protect}S_{ij}
\]

is removed.

The constant:

```text
THETA_PROTECT
```

must no longer affect persistence through Law 3.

If the implementation or a later law uses salience for an already-lawful purpose, that purpose must be explicit and must not silently recreate anti-decay protection.

---

## 10.3 Remove Survival Claims

Statements such as:

```text
a painful edge survives N ticks
a structural fact survives hundreds of ticks
```

are removed from Law 8.

Time-to-death is no longer a salience property.

---

## 10.4 Salience Does Not Block Correction

A salient Edge may still be corrected by lawful negative evidence.

\[
\boxed{
Salience \not\Rightarrow ImmunityFromEvidence
}
\]

This directly affects Law 13.

---

# 11. Amendment to Law 13 — Prediction, Causality & Disappointment

## 11.1 Revised Role

Law 13 becomes the primary owner of **evidence-driven negative weight correction**.

Its negative update remains event-triggered:

\[
\varepsilon_j<0
\Rightarrow
\Delta W_{ij}<0
\]

No update occurs merely because the Edge was inactive.

---

## 11.2 Remove Law-8 Persistence Floor From Negative Correction

The former rule:

> disappointment must not lower \(W\) below \(W_{floor}\)

is removed.

Negative evidence must not be blocked by a salience-derived anti-decay floor.

The corrected bounded form is:

\[
W_{ij}
\leftarrow
\max
\left(
0,
W_{ij}+\Delta W_{ij}
\right)
\]

subject to existing locked-edge hysteresis.

---

## 11.3 Locked-Edge Hysteresis

The existing repeated-failure mechanism remains the lawful path for destabilizing established knowledge.

\[
k_{fail}\uparrow
\]

and when the existing Law-13 unlock criterion is met:

\[
Locked\leftarrow0
\]

This is evidence-based revision, not forgetting.

---

## 11.4 Zero Weight Is Not Automatic Deletion

Even if evidence-driven correction reaches:

\[
W=0
\]

this fact alone does not grant universal deletion authority.

\[
\boxed{
W=0 \not\Rightarrow Delete
}
\]

Physical retirement requires an explicit lawful lifecycle/structural owner.

This amendment deliberately avoids recreating `THETA_PRUNE=0` under another name.

---

# 12. Amendment to Law 11 — Temporal Sequencing & Roles

The former clause:

> `role_k` edges decay under Law 3, and their disappearance kills the `ev:*` node

is abolished.

Persistent event-role structures do not decay merely because the event is not repeated.

\[
\boxed{
NoRepeat(Event)
\not\Rightarrow
Delete(Event)
}
\]

For ordinary Law-11 event memory:

\[
NoLawfulInvalidation
\Rightarrow
role_k\ persistence
\]

and:

\[
NoLawfulInvalidation
\Rightarrow
ev:* \ persistence
\]

If an implementation requires a truly transient event scaffold, its lifetime must be defined by an existing explicit transient scope owner.

No generic `ev:*` inactivity decay remains.

No new persistent/transient event primitive is introduced by this amendment.

---

# 13. Amendment to Law 6 — Episode Isolation

Law 6 remains the owner of:

- episode identity;
- same-episode origin eligibility;
- temporal binding window;
- episode closure.

Law 6 does **not** become a universal deletion law.

Its relevance to Law-3 abolition is limited to providing a lawful scope boundary that transient-object owners may use.

At episode/scope closure, an owning modality or operational subsystem may explicitly retire objects whose existing type semantics are already transient.

\[
EpisodeClosure
\neq
DeletePersistentKnowledge
\]

---

# 14. Amendment to RFC-01 / Quantity Transient Instances

Former behavior relied on:

```text
inst:* excluded from Law 5
→ accelerated/passive decay
→ Law 3 pruning
→ orphan death
```

This chain is removed.

Revised behavior:

```text
create transient inst:*
→ use within its lawful episode/scope
→ scope owner declares lifecycle end
→ explicitly retire transient incident structure
→ local orphan reclamation
```

Persistent numeric backbone and persistent arithmetic/event knowledge do not acquire any decay replacement.

The intrinsic numeric backbone remains protected by its own ontology and ownership, not by exemption from Law 3.

---

# 15. Amendment to RFC-06 / Visual Transient Instances

The former accelerated visual-instance decay:

\[
\lambda_{transient}=0.12
\]

used to guarantee `inst:vis_*` death is removed.

Visual instance cleanup becomes scope-driven.

\[
SceneScopeEnd
\Rightarrow
Retire(inst:vis_*)
\]

through the existing visual/episode lifecycle owner.

This amendment does not require a new learned parameter.

The rationale:

> prevent visual garbage by accelerated forgetting

is replaced with:

> transient visual instances have explicit bounded operational lifetime.

Persistent visual concepts, attributes, and learned relations do not decay because unrelated scenes pass.

---

# 16. Amendment to RFC-09 — Runtime Clock and `/tick`

The former runtime semantics:

```text
step_time(ticks)
→ advance time
→ trigger decay
→ trigger cellular death
```

are abolished.

Revised invariant:

\[
\boxed{
ClockAuthority
\neq
CognitiveEvidenceAuthority
}
\]

`step_time(ticks)` may continue to advance operational time required by existing lawful temporal mechanisms, but:

\[
step\_time(n)
\not\Rightarrow
LearnedWeightDecay
\]

and:

\[
step\_time(n)
\not\Rightarrow
SalienceDecay
\]

and:

\[
step\_time(n)
\not\Rightarrow
LowWeightPruning
\]

The `/tick` command must no longer be described as a forgetting/cellular-death command.

It becomes an operational-time advancement / temporal-runtime inspection command only.

---

# 17. Amendment to RFC-10 — Node Lifecycle & Safe Removal

RFC-10 retains **safe physical deletion mechanics**.

It loses any global cognitive death authority.

## 17.1 Safe Removal Is a Mechanism

Functions such as safe Edge/Node removal may clean:

- adjacency maps;
- Edge registries;
- contradiction references;
- membership references;
- other existing structural references.

But:

\[
\boxed{
Mechanism \neq Authority
}
\]

A storage helper may execute an authorized removal.

It may not decide that persistent knowledge is obsolete merely from age or weight.

---

## 17.2 Local Orphan Reclamation

Orphan reclamation remains:

\[
Orphan(u)
\iff
deg_{in}(u)=0
\land
deg_{out}(u)=0
\land
A_u=0
\land
\neg is\_intrinsic
\]

but it is evaluated only as a local postcondition after a lawful structural/lifecycle removal affects the Node.

Example:

```text
Authorized owner retires Edge(i,j)
        ↓
safe edge removal
        ↓
check endpoint i
check endpoint j
        ↓
if endpoint is operationally orphaned
        ↓
safe node reclamation
```

No full graph scan is required by this amendment.

---

## 17.3 Orphan Reclamation Is Not Forgetting

A Node with no cognitive Edges and no activation is an operational object without persistent cognitive ownership.

Reclaiming such an object is:

\[
\boxed{
GarbageCollection
}
\]

not:

\[
\boxed{
MemoryForgetting
}
\]

---

# 18. Amendment to Law 14 — Assembly Sanitation

Law 14 does not receive cognitive deletion authority.

It remains a structural organization owner.

Any former trigger named specifically:

```text
Law3 lifecycle invalidation
```

must be generalized to:

```text
lawful edge/node lifecycle invalidation
```

When another lawful owner retires a graph object, Law 14 may sanitize stale Assembly membership/reference state exactly within its existing authority.

\[
\Delta CognitiveState_{Law14}=0
\]

must remain true.

---

# 19. Existing Derived/Structural Retirement Remains With Existing Owners

Law-3 abolition does not prohibit deletion where another law already owns a specific derived or structural lifecycle.

Examples include:

- Law-9 derived similarity Edges whose topological derivation is no longer satisfied;
- structural mutation/retirement governed by existing structural laws;
- hypothesis lifecycle removal governed by its existing owner;
- merge/deduplication cleanup already governed by structural identity rules.

These must not be rewritten as general low-weight pruning.

The invariant is:

\[
\boxed{
OwnerThatEstablishesInvalidation
=
OwnerThatMayAuthorizeRetirement
}
\]

subject to existing authority boundaries.

---

# 20. Law 10 Is Not a Replacement for Law 3

Any independent Law-10 concept-capacity or utility mechanism remains outside this amendment unless separately reviewed.

Law 10 must not become a hidden global forgetting mechanism for ordinary learned Edges.

This amendment does not silently expand Law-10 authority.

---

# 21. Intrinsic State After Law-3 Abolition

Former documents often described `is_intrinsic=True` as:

> immune to Law-3 decay/pruning.

That wording becomes obsolete.

Intrinsic state remains semantically protected according to its own architectural ownership.

The post-abolition rule is:

\[
\boxed{
IntrinsicState
\text{ is not subject to generic retirement}
}
\]

because no generic retirement law exists.

Any modification/removal of intrinsic backbone requires its own explicit lawful authority.

---

# 22. No Universal Edge-Deletion Authority

After this amendment:

\[
\boxed{
ThereIsNoUniversalCognitiveDeletePass
}
\]

and:

\[
\boxed{
ThereIsNoUniversalForgettingThreshold
}
\]

Persistent learned Edges are not periodically evaluated for death.

Deletion can occur only through an owner-specific lawful cause already present in the architecture or explicitly specified by a future approved amendment.

This document does **not** create a new generic `RetirementReason` cognitive primitive.

Any implementation labels used for logs are telemetry/engineering metadata only.

---

# 23. Explicitly Forbidden Replacements

The following would violate this amendment:

- rename `LAMBDA_DECAY` and keep the same behavior;
- lazy decay based on `current_tick - last_update`;
- local inactivity counters that silently reduce persistent \(W\);
- deleting Edges after \(N\) unused episodes;
- setting `THETA_PRUNE=0` and calling it evidence retirement;
- using Law 8 salience as permanent correction immunity;
- using Law 13 to scan all weak Edges without actual prediction failure;
- moving the old global sweep into RFC-10;
- creating a new "Memory Cleanup Law" with the same semantics;
- deleting ordinary `ev:*` because they were not repeated;
- retaining `inst:*` by time decay instead of explicit transient lifecycle;
- allowing `/tick` to mutate persistent learned knowledge merely by advancing time.

---

# 24. Complexity Compression Result

Before:

```text
Law 1  → Create
Law 2  → Reinforce
Law 3  → Decay W
          Decay S
          Prune weak Edges
          Kill orphan Nodes
Law 5  → Protect against Law 3
Law 8  → Protect salient Edges against Law 3
Law 11 → Event roles eventually die through Law 3
Law 13 → Correct failed predictions
RFC-10 → Scan/kill after Law 3
RFC-09 → Advance time and trigger Law 3
```

After:

```text
Law 1  → Create
Law 2  → Positive evidence reinforcement
Law 5  → Consolidated status / revision hysteresis
Law 6  → Episode/source boundary
Law 8  → Salience/significance
Law 11 → Persistent event-role structure
Law 13 → Negative evidence correction / unlock

Existing lifecycle owners
       → explicit transient retirement

Existing structural owners
       → owner-specific lawful retirement

Graph lifecycle layer
       → safe local removal + orphan reclamation

Law 14
       → sanitation after lawful lifecycle change

RFC-09
       → operational time only
```

Therefore:

\[
\boxed{
Law3Removed
}
\]

without:

\[
\boxed{
ReplacementLawCreated
}
\]

This is an architectural complexity reduction.

---

# 25. Post-Abolition Invariants

### L3A-INV-001 — Law 3 Has No Runtime Authority

No runtime mutation may be attributed to Law 3.

### L3A-INV-002 — No Time-Based Learned-Weight Decay

Unrelated elapsed time cannot lower persistent learned \(W\).

### L3A-INV-003 — No Time-Based Salience Decay

Unrelated elapsed time cannot lower \(S\) through former Law-3 semantics.

### L3A-INV-004 — No Universal Low-Weight Pruning

Low \(W\) alone cannot delete a persistent learned Edge.

### L3A-INV-005 — No Global Forgetting Sweep

No periodic full-graph cognitive decay pass remains.

### L3A-INV-006 — Positive Evidence Owned by Law 2

Law 2 remains the positive reinforcement owner.

### L3A-INV-007 — Negative Evidence Owned by Law 13

Persistent learned-weight reduction requires lawful evidence-driven correction.

### L3A-INV-008 — No Salience Immunity From Correction

Law 8 cannot create a floor that blocks lawful Law-13 correction.

### L3A-INV-009 — Consolidation Is Not Anti-Decay

Law 5 `Locked` means established revision stability, not protection from time.

### L3A-INV-010 — Event Memory Does Not Expire by Inactivity

Ordinary persistent Law-11 events/roles survive unrelated time.

### L3A-INV-011 — Transient Lifetime Is Explicit

`inst:*` cleanup follows explicit scope lifecycle, not decay.

### L3A-INV-012 — Orphan Reclamation Is Local

GC follows lawful removals and checks affected local endpoints.

### L3A-INV-013 — Mechanism Does Not Grant Authority

Graph removal helpers do not decide cognitive validity.

### L3A-INV-014 — Owner-Specific Retirement

A structural/cognitive owner may retire only state within its existing lawful authority.

### L3A-INV-015 — Law 14 Remains Structurally Reactive

Assembly sanitation does not become cognitive deletion.

### L3A-INV-016 — Runtime Clock Is Cognitively Neutral

Advancing time alone cannot modify persistent learned memory.

### L3A-INV-017 — No Replacement Forgetting Law

No new law reproduces Law-3 semantics.

### L3A-INV-018 — No New Cognitive Primitive

Abolition and reassignment introduce no new persistent cognitive primitive.

### L3A-INV-019 — No Law Renumbering

Law 3 remains an abolished historical slot; later laws retain numbers.

### L3A-INV-020 — Historical Lineage Preserved

Old signatures/reports remain valid historical records and are not rewritten.

---

# 26. Required Implementation Workstreams

## L3A-W01 — Static Dependency Inventory

Find every active reference to:

```text
Law 3
law3
decay
LAMBDA_DECAY
LAMBDA_SAL
THETA_PRUNE
W_floor
THETA_PROTECT
cellular death
step_time decay
transient accelerated decay
```

Classify each as:

```text
REMOVE
AMEND
HISTORICAL_ONLY
UNAFFECTED_DIFFERENT_SEMANTICS
```

---

## L3A-W02 — Remove Law-3 Runtime

Remove/disable the former Law-3 cognitive runtime path.

No compatibility shim may retain its semantics.

---

## L3A-W03 — Amend Law 5

Implement revised consolidation/revision-stability semantics.

Remove anti-decay floor behavior.

---

## L3A-W04 — Amend Law 8

Remove persistence-floor coupling and survival claims.

Preserve only already-lawful salience state/behavior not dependent on Law 3.

---

## L3A-W05 — Amend Law 13

Remove salience-floor protection from negative correction.

Verify evidence-driven weakening and unlock remain lawful.

---

## L3A-W06 — Amend Law 11

Remove role-edge inactivity decay and automatic event death through Law 3.

---

## L3A-W07 — Replace Transient Decay With Explicit Lifecycle

Repair RFC-01/RFC-06 and any other `inst:*` owner.

No persistent knowledge may be caught in transient cleanup.

---

## L3A-W08 — Localize RFC-10 GC

Replace global post-decay node scanning with local post-removal orphan reclamation.

---

## L3A-W09 — Amend RFC-09 Time Semantics

`step_time` and `/tick` must not trigger passive memory mutation.

---

## L3A-W10 — Amend Law 14 Lifecycle Trigger

Replace Law-3-specific invalidation triggers with generic lawful lifecycle invalidation.

---

## L3A-W11 — Documentation & Lawbook Rewrite

Update:

- formal lawbook;
- architecture overview;
- affected RFCs;
- implementation comments;
- CLI/help text;
- test names;
- benchmark explanations.

Historical documents remain historical and should not be rewritten as if Law 3 never existed.

---

# 27. Required Verification Gates

### L3A-G01 — Law-3 Static Absence

No active runtime reference grants Law 3 cognitive authority.

### L3A-G02 — Persistence Under Unrelated Time

A one-shot valid persistent relation remains bit-identical after:

\[
1,\ 16,\ 128,\ 1000
\]

unrelated time advances, absent lawful evidence updates.

### L3A-G03 — Positive Evidence Still Works

Law 2 reinforcement remains functional.

### L3A-G04 — Negative Evidence Still Works

Law 13 disappointment lowers weight only after actual validated failure.

### L3A-G05 — Low Weight Does Not Auto-Delete

A persistent Edge at low or zero weight is not deleted solely because of its weight.

### L3A-G06 — Lock Without Anti-Decay Floor

Law 5 can acquire/hold/release `Locked` under revised semantics without `W_floor`.

### L3A-G07 — Salience Without Persistence Privilege

Law 8 salience updates do not create a survival floor or block correction.

### L3A-G08 — Persistent Event Survival

Law-11 `ev:*` and `role_k` survive unrelated time.

### L3A-G09 — Explicit Transient Retirement

`inst:*` instances are removed at lawful scope end without passive decay.

### L3A-G10 — No Persistent Leakage From Transient Cleanup

Transient retirement cannot delete persistent concept/event knowledge.

### L3A-G11 — Local Orphan Reclamation

Authorized removal of a final incident Edge reclaims only eligible affected orphan Nodes.

### L3A-G12 — No Global GC Requirement

Correct lifecycle behavior occurs without a full graph death scan.

### L3A-G13 — Clock Neutrality

`step_time` changes operational time but not persistent learned cognition absent another lawful time-sensitive owner.

### L3A-G14 — Assembly Sanitation

Law 14 cleans stale membership references after lawful lifecycle changes without changing cognitive Edge state.

### L3A-G15 — No Replacement Law/Primitive

Static and architectural audit confirms:

```text
New forgetting law = 0
New persistent cognitive primitive = 0
```

### L3A-G16 — Full Regression

Repository tests, lint, type checks, and all affected behavioral suites pass under the new architecture.

Required amendment verification condition:

\[
\boxed{
L3A\text{-}G01..G16=16/16\ PASS
}
\]

---

# 28. Mandatory Behavioral Tests

At minimum implement tests equivalent to:

```text
test_persistent_edge_unchanged_after_unrelated_ticks
test_persistent_edge_survives_1000_ticks
test_low_weight_edge_not_auto_pruned
test_zero_weight_edge_not_auto_deleted_without_owner
test_law2_positive_reinforcement_after_long_gap
test_law13_negative_evidence_correction
test_law13_correction_not_blocked_by_salience_floor
test_law5_lock_without_w_floor
test_law5_unlock_by_repeated_validated_failure
test_law8_salience_does_not_change_persistence
test_event_role_edges_do_not_decay
test_event_node_does_not_die_from_inactivity
test_transient_instance_retired_on_scope_close
test_transient_retirement_preserves_persistent_concept
test_authorized_edge_removal_triggers_local_orphan_gc
test_unrelated_nodes_not_scanned_or_deleted
test_step_time_is_persistent_memory_neutral
test_law14_sanitizes_after_generic_lifecycle_invalidation
```

Exact test names may vary.

Semantic coverage may not.

---

# 29. Signature and Lineage Policy

This amendment intentionally changes frozen historical behavior.

Therefore:

\[
\boxed{
OldBehavioralSignatures
\text{ are historical references, not post-amendment targets}
}
\]

The historical signatures must remain recorded as historical closure evidence.

They must not be overwritten.

After implementation and verification, establish a new post-abolition canonical baseline/signature set.

The final implementation report must explicitly distinguish:

```text
Historical pre-abolition signatures
vs.
New post-abolition signatures
```

Signature drift caused by the authorized architectural amendment is not automatically a regression.

Unauthorized drift outside the defined amendment scope remains a failure.

---

# 30. Out of Scope

This amendment does not authorize:

- curriculum Trial 02;
- full Simple Wikipedia retraining;
- a new episodic consolidation buffer;
- cold storage;
- archival compression;
- memory paging;
- a new memory-capacity law;
- new forgetting equations;
- new local inactivity age;
- new recency state;
- revision of Law 10 capacity policy;
- redesign of Law 12 affect dynamics;
- Phase III;
- audio work;
- broad language expansion.

First implement and verify Law-3 abolition.

---

# 31. Required Final Implementation Report

The implementation report must answer:

1. Was every active Law-3 runtime authority removed?
2. Were `LAMBDA_DECAY`, `LAMBDA_SAL`, and `THETA_PRUNE` removed from persistent learned-memory semantics?
3. Does unrelated `step_time` leave persistent learned weights unchanged?
4. Does unrelated time leave Law-11 event-role memory unchanged?
5. Does Law 2 still strengthen valid repeated relations?
6. Does Law 13 still weaken relations after actual prediction failure?
7. Can Law 13 correction cross the old salience floor?
8. Can Law 5 lock/unlock without any anti-decay floor?
9. Does Law 8 retain salience without persistence privilege?
10. Are transient `inst:*` objects retired explicitly at scope end?
11. Is transient cleanup isolated from persistent cognition?
12. Is orphan GC local and owner-triggered?
13. Does RFC-10 safe removal remain reference-clean?
14. Does Law 14 sanitize after generic lawful lifecycle invalidation?
15. Does any hidden low-weight pruning remain?
16. Does any hidden time-based persistent-memory decay remain?
17. Was any replacement forgetting law introduced?
18. Was any new persistent cognitive primitive introduced?
19. Which pre-abolition signatures changed as expected?
20. What are the new post-abolition canonical signatures?
21. Did the full repository regression pass?
22. Is DGCA ready for a small persistence re-validation before any large-corpus rerun?

---

# 32. Final Required Metrics Block

```text
============================================================
DGCA — LAW 3 ABOLITION & DEPENDENCY REASSIGNMENT

DOCUMENT:
DGCA-Law-3-Abolition-Dependency-Reassignment-Amendment-v1.0

ARCHITECTURAL DECISION:
LAW 3 ABOLISHED

UNIQUE ARCHITECTURAL NECESSITY (LAW 3):
FALSE

LAW RENUMBERING:
0

NEW NORMATIVE LAWS:
0

NEW COGNITIVE PRIMITIVES:
0

REMOVED:
Time-Based Weight Decay: YES
Time-Based Salience Decay: YES
Universal Low-Weight Pruning: YES
Global Forgetting Sweep: YES
Global Post-Decay Node Sweep: YES

REASSIGNED:
Positive Evidence: Law 2
Consolidation / Revision Stability: Law 5
Salience: Law 8
Persistent Event Roles: Law 11
Negative Evidence Correction: Law 13
Transient Scope Boundary: Existing Episode/Modality Owner
Safe Removal / Orphan GC: Graph Lifecycle Layer
Assembly Sanitation: Law 14
Operational Clock: RFC-09

LAW 5 ANTI-DECAY FLOOR:
REMOVED

LAW 8 PERSISTENCE FLOOR:
REMOVED

LAW 13 SALIENCE FLOOR BLOCK:
REMOVED

LAW 11 ROLE DECAY:
REMOVED

TRANSIENT PASSIVE DECAY:
REMOVED

PERSISTENCE BY DEFAULT:
ENABLED

NO-EVIDENCE WEIGHT MUTATION:
0

LOW-WEIGHT AUTO-DELETION:
0

GLOBAL COGNITIVE DELETE PASS:
0

POST-ABOLITION INVARIANTS:
L3A-INV-001..020:
x/20

VERIFICATION GATES:
L3A-G01..G16:
x/16

FULL REGRESSION:
PASS / FAIL

HISTORICAL SIGNATURES:
PRESERVED AS HISTORICAL RECORDS

NEW POST-ABOLITION SIGNATURES:
...

FINAL IMPLEMENTATION VERDICT:
PASS / FAIL / BLOCKED

READY FOR SMALL PERSISTENCE RE-VALIDATION:
YES / NO

READY FOR LARGE-CORPUS RETRAINING:
NO
============================================================
```

---

# 33. Final Architectural Statement

The abolished Law 3 was originally introduced to mimic biological forgetting, control noise, and release resources.

Empirical testing demonstrated that its ordinary learned-memory decay caused correct knowledge to disappear before natural sparse recurrence could reinforce it.

After decomposition, no unique cognitive function remained that required a universal forgetting law.

The post-amendment DGCA rule is therefore:

\[
\boxed{
\textbf{Knowledge does not become less valid merely because unrelated time passed.}
}
\]

and:

\[
\boxed{
\textbf{Persistent memory changes because of lawful evidence, not silence.}
}
\]

and:

\[
\boxed{
\textbf{Deletion is an owner-specific lifecycle act, not a universal weak-weight heuristic.}
}
\]

and:

\[
\boxed{
\textbf{Garbage collection reclaims empty operational structure; it does not decide what knowledge deserves to survive.}
}
\]

Therefore:

\[
\boxed{
UniqueArchitecturalNecessity(Law3)=FALSE
}
\]

\[
\boxed{
\textbf{LAW 3 — ABOLISHED / RESERVED}
}
\]

\[
\boxed{
\textbf{No Replacement Forgetting Law Adopted}
}
\]

\[
\boxed{
\textbf{Persistence by Default — Revision by Evidence — Retirement by Lawful Ownership}
}
\]

---

# 34. Closure

The architectural question of Law 3 is closed by this amendment.

No further conceptual redesign of Law 3 is required.

The remaining work is strictly:

\[
\boxed{
Implementation
\rightarrow
DependencyRepair
\rightarrow
Verification
\rightarrow
NewBaseline
}
\]

Only after those steps pass may DGCA proceed to a new empirical persistence validation.

