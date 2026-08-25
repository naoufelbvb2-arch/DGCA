# DGCA Phase 2.5 — Law-3 Persistence Forensics Trial 01 Specification v1.0

## Creation, Decay, Pruning, Consolidation & Orphan-Node Survival in the Frozen DGCA Graph

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Experiment:** Law-3 Persistence Forensics — Trial 01  
**Version:** 1.0  
**Language Front-End:** English Encoder v2 — IMPLEMENTED / VERIFIED / FROZEN  
**Status:** **PROTOCOL — CANDIDATE FOR FREEZE**  
**Architecture Status During Trial:** **FROZEN**  
**Law 3 Status During Trial:** **UNCHANGED / UNDER OBSERVATION ONLY**  
**Phase Status:** Phase 2.5 empirical diagnosis; **not Phase III**  
**Primary Principle:** **Observe First → Diagnose → Then Redesign**

---

# 1. Executive Purpose

Real-Data Trial 01 established that DGCA could process a large natural-text corpus while producing almost no durable graph memory at final checkpoints. That trial could not distinguish between two fundamentally different failure modes:

\[
\boxed{\text{Failure A: Nodes/Edges are not created correctly}}
\]

and

\[
\boxed{\text{Failure B: Nodes/Edges are created, then rapidly destroyed}}
\]

English Encoder v2 has now been independently repaired, verified, and frozen. The principal unresolved persistence suspect is therefore **Law 3 — Decay, Pruning & Cellular Death**, together with its lawful interactions with reinforcement, consolidation, salience protection, and orphan-node garbage collection.

This experiment exists to answer the questions in the correct causal order:

\[
\boxed{\textbf{STEP 1 — Do Nodes and Edges actually get created?}}
\]

\[
\boxed{\textbf{STEP 2 — If created, how long do they survive and what kills them?}}
\]

\[
\boxed{\textbf{STEP 3 — What reinforcement count and inter-exposure gap are required for survival?}}
\]

The experiment is diagnostic. It does **not** authorize any change to Law 3, any parameter calibration, any new memory mechanism, any curriculum intervention, or any large-corpus retraining.

A poor scientific outcome is allowed.

\[
\boxed{\text{ProtocolSuccess} \neq \text{Law3CapabilitySuccess}}
\]

---

# 2. Authoritative Baseline

The trial is governed by the currently frozen DGCA implementation and its formal lawbook.

The relevant frozen laws are:

- **Law 1 — Creation & Emergence**
- **Law 2 — Cumulative Dual Reinforcement**
- **Law 2-b — Role Asymmetry**
- **Law 3 — Decay, Pruning & Cellular Death**
- **Law 5 — Consolidation & Protection**
- **Law 6 — Episode Isolation**
- **Law 8 — Affective & Structural Salience**

The current canonical Phase-I reference signature is:

```text
c4b2549940a49789
```

The upstream closure registry remains:

```text
Phase-I: c4b2549940a49789
RFC-11:  412730689a2befa5
RFC-12:  f121b698e6d97292
RFC-13:  8652eb05126afa8c
RFC-14:  46213188cdb02ee8
RFC-15:  92c6ba731b372f10
RFC-16:  cc9363dc6394a7cf
```

All must remain unchanged by this forensic trial.

---

# 3. Frozen Mathematical Baseline

## 3.1 Law 1 — Creation

A new edge is created when co-activation passes the frozen creation requirement:

\[
E_{edge}(i,j)=1
\iff
A_i(t)A_j(t)\ge\theta_{creation}
\land
\mathbf{1}_{ValidOrigin}(i,j)
\]

with:

\[
\theta_{creation}=0.30
\]

and initial edge weight:

\[
W_{base}=0.10
\]

---

## 3.2 Law 2 — Reinforcement

For an eligible active edge:

\[
\Delta W_{ij}
=
\eta
(W_{max}-W_{ij})
A_iA_j
M_{boost}
\zeta_{dir}
\]

with:

\[
\eta=0.30
\]

\[
W_{max}=1.00
\]

and frozen direction factors including:

\[
\zeta_{fwd}=1.0
\]

\[
\zeta_{back}=0.40
\]

\[
\zeta_{lat}=0.10
\]

Law 2 also updates:

- reinforcement/co-occurrence count \(n_{ij}\);
- context set \(\mathcal{C}_{ij}\);
- last-update time.

---

## 3.3 Law 3 — Decay

For an edge not updated in the current tick:

\[
W_{ij}(t+1)
=
\max
\left(
W_{floor}(ij),
W_{ij}(t)-\lambda_{decay}
\right)
\]

with:

\[
\lambda_{decay}=0.020
\]

Salience also decays:

\[
S_{ij}(t+1)
=
\max
\left(
0,
S_{ij}(t)-\lambda_S
\right)
\]

with:

\[
\lambda_S=0.0005
\]

---

## 3.4 Law 3 — Edge Pruning

An edge is pruned when:

\[
\text{Prune}(i,j)
\iff
W_{ij}(t+1)\le\theta_{prune}
\land
Locked=0
\land
\neg is\_intrinsic
\]

with:

\[
\theta_{prune}=0.05
\]

---

## 3.5 Law 3 — Cellular Death

A node is deleted when:

\[
\text{CellularDeath}(u)
\iff
\deg_{in}(u)=0
\land
\deg_{out}(u)=0
\land
A_u=0
\land
\neg is\_intrinsic
\]

The experiment must distinguish:

\[
\boxed{\text{EdgePruning}}
\]

from:

\[
\boxed{\text{OrphanNodeGC}}
\]

They are not the same event.

---

## 3.6 Law 5 — Consolidation

An edge becomes locked only if all frozen requirements are satisfied:

\[
Locked(ij)
\iff
(W_{ij}\ge\theta_{solid})
\land
(n_{ij}\ge N_{min})
\land
(|\mathcal{C}_{ij}|\ge\kappa \lor g_{ij}\neq\varnothing)
\land
(k_{fail}<K_{fail})
\]

with:

\[
\theta_{solid}=0.75
\]

\[
N_{min}=3
\]

\[
\kappa=2
\]

A locked edge receives a stable floor:

\[
W_{floor}=0.75
\]

and Law 3 must not prune it.

---

## 3.7 Law 8 — Salience Protection

For tagged, unlocked edges:

\[
W_{floor}(ij)=\theta_{protect}S_{ij}
\]

with:

\[
\theta_{protect}=0.35
\]

Structural facts may receive:

\[
structural\_weight=0.80
\]

Therefore some definition-like relations can have a lawful survival advantage independent of ordinary repetition.

This is a critical confound and MUST be measured rather than ignored.

---

# 4. Central Scientific Rule

The experiment must never infer failure from final graph size alone.

For both Nodes and Edges it must measure three distinct quantities:

\[
\boxed{Created}
\]

\[
\boxed{PeakAlive}
\]

\[
\boxed{FinalAlive}
\]

Example:

```text
Unique Nodes Ever Created: 12,450
Peak Concurrent Nodes:      2,180
Final Surviving Nodes:         31
```

Those three values describe completely different phenomena.

The same accounting is required for Edges.

---

# 5. Primary Scientific Questions

## L3-Q01 — Node Creation

After English Encoder v2 emits structurally valid episodes, are graph Nodes actually materialized?

Required distinction:

\[
EncoderOutput
\rightarrow
NodeCreation
\]

must be measured directly.

---

## L3-Q02 — Edge Creation

Before Law 3 can destroy anything, do Law 1 / structural event mechanisms create the expected local Edges?

Required distinction:

\[
NodesCreated
\not\Rightarrow
EdgesCreated
\]

Both must be observed independently.

---

## L3-Q03 — Destruction Attribution

If Nodes/Edges are created and later disappear:

**Which exact mechanism removes them?**

Possible lawful owners include:

- Law 3 weight decay;
- Law 3 edge pruning;
- cellular death after orphaning;
- existing structural lifecycle rules;
- another already-frozen owner revealed by the runtime.

No cause may be inferred merely from timing.

---

## L3-Q04 — Edge Lifetime

For a newly created, unreinforced edge:

\[
\boxed{\text{How many non-reinforcing ticks does it survive?}}
\]

The result must be measured by edge class, not collapsed into one global average.

---

## L3-Q05 — Reinforcement & Gap Requirement

For lawful independent re-exposures:

\[
\boxed{\text{How many exposures are needed for stable survival?}}
\]

and:

\[
\boxed{\text{What maximum inter-exposure gap can the edge tolerate?}}
\]

This must include the transition, if any, into Law-5 consolidation.

---

# 6. Explicit Non-Questions

This trial does **not** ask:

- whether Law 3 should be removed;
- what the new \(\lambda_{decay}\) should be;
- what the new pruning threshold should be;
- whether decay should be global or local;
- whether DGCA requires episodic replay;
- whether a developmental curriculum is better;
- whether large Wikipedia training should be repeated;
- whether a new memory primitive is needed.

Those are later design questions.

Trial 01 only produces evidence.

---

# 7. Frozen Architecture Constraint

During the entire experiment:

\[
\boxed{\textbf{ArchitectureChangesDuringForensics}=0}
\]

Specifically forbidden:

- Law 3 equation changes;
- `LAMBDA_DECAY` changes;
- `THETA_PRUNE` changes;
- `LAMBDA_SAL` changes;
- Law 5 threshold changes;
- Law 8 threshold changes;
- changed tick timing;
- changed law order;
- changed orphan-GC criteria;
- changed creation threshold;
- changed reinforcement rule;
- changed encoder semantics;
- new persistence state;
- new learned fields;
- new cognitive primitive;
- new normative law;
- new semantic threshold;
- new replay/consolidation mechanism;
- special-case exemptions inserted for this trial.

The trial may add **external telemetry and read-only instrumentation only**.

---

# 8. Telemetry Is Not Cognition

The following are allowed as experimental telemetry:

- counters;
- timestamps;
- event logs;
- before/after snapshots;
- edge lifecycle records;
- node lifecycle records;
- immutable trace IDs;
- state digests;
- causal attribution labels derived from actual runtime owners.

These must live outside persistent cognitive state.

Formally:

\[
\boxed{
TelemetryState
\cap
CognitivePersistentState
=
\varnothing
}
\]

Telemetry must never affect:

- edge creation;
- edge reinforcement;
- edge decay;
- pruning;
- node deletion;
- locking;
- salience;
- graph ranking;
- graph traversal;
- context;
- evidence authority.

---

# 9. Instrumentation Transparency Requirement

Before the scientific trial, prove that instrumentation itself is behaviorally transparent.

Run an identical fixed micro-sequence twice:

1. instrumentation disabled;
2. instrumentation enabled.

Require:

\[
Digest_{off}=Digest_{on}
\]

and identical:

- created node identities;
- created edge identities;
- weights;
- lock states;
- salience;
- contexts;
- final graph;
- canonical upstream signatures.

If instrumentation changes behavior:

\[
\boxed{\text{TRIAL BLOCKED}}
\]

---

# 10. Runtime Owner Map — Mandatory Preflight

Before collecting results, inspect the actual implementation and document the exact within-tick execution order.

Do not assume the paper ordering is identical to runtime ordering.

The preflight must identify, at minimum:

1. node materialization owner;
2. edge creation owner;
3. reinforcement owner;
4. salience update owner;
5. consolidation/lock owner;
6. Law 3 decay owner;
7. edge-pruning owner;
8. orphan-node deletion owner;
9. transient reset/settling owner.

The final report must record the actual call order.

Instrumentation hooks must be placed around actual owners without changing their order.

---

# 11. Required Within-Tick Observation Points

For every observed perception cycle, capture the closest lawful equivalents of:

### T0 — Pre-Ingress Graph State

Before the target input changes graph state.

### T1 — Post-Encoder / Pre-Graph

Capture Encoder v2 episodes only.

### T2 — Post-Node Materialization

Nodes that now exist before destructive persistence logic.

### T3 — Post-Creation / Reinforcement

Capture all new/updated edges before Law 3 destruction.

### T4 — Immediately Pre-Law-3

Record exact edge fields entering Law 3.

### T5 — Immediately Post-Law-3 Decay / Edge Pruning

Record changed weights and removed edges.

### T6 — Post-Orphan-GC

Record node deletions caused by isolation.

### T7 — End-of-Tick / Quiescent State

Final lawful graph state for that cycle.

If implementation combines two stages inside one function, instrumentation may be inserted around internal substeps only if it is observational and semantically transparent.

---

# 12. Core Node Lifecycle Record

For every non-intrinsic Node observed during the trial, record:

```text
NodeID
NodeKind/Region
SourceEpisodeID
CreatedAtTick
CreatedByOwner
FirstSeenFromEncoderSymbol
PeakInDegree
PeakOutDegree
EdgesEverAttached
LastIncidentEdgeRemovedAtTick
OrphanedAtTick
DeletedAtTick
DeletionOwner
DeletionCause
FinalStatus
```

Required deletion-cause categories include at least:

```text
NOT_DELETED
ORPHAN_AFTER_LAW3_PRUNE
OTHER_EXISTING_OWNER
UNKNOWN_BLOCKING_ERROR
```

`UNKNOWN` is not an acceptable final scientific attribution; if attribution truly cannot be established from the runtime, report that as an instrumentation limitation and do not guess.

---

# 13. Core Edge Lifecycle Record

For every target Edge observed, record:

```text
EdgeID
SourceNode
TargetNode
Kind
DirectionClass
fwd
is_intrinsic
tagged
Locked
CreatedAtTick
CreatedByOwner
InitialWeight
InitialSalience
InitialFloor
ReinforcementCountAtCreation
ContextCountAtCreation
EveryReinforcementTick
EveryLaw3ApplicationTick
WeightBeforeLaw3
WeightAfterLaw3
SalienceBeforeLaw3
SalienceAfterLaw3
FloorBeforeLaw3
FloorAfterLaw3
MaxWeight
MaxSalience
LastUpdatedTick
LockedAtTick
PrunedAtTick
PrunedByOwner
PruneReason
LifetimeNonReinforcingTicks
FinalStatus
```

This record is the primary forensic evidence.

---

# 14. Edge-Class Stratification

Do not collapse all Edges into one statistic.

At minimum stratify by observed fields:

### Class A — Ordinary Unprotected Edge

```text
Locked = 0
tagged = 0
is_intrinsic = 0
```

### Class B — Salience-Protected Edge

```text
Locked = 0
tagged = 1
W_floor > 0
```

### Class C — Law-5 Locked Edge

```text
Locked = 1
```

### Class D — Intrinsic Edge

```text
is_intrinsic = 1
```

Intrinsic edges are controls only and are not used to judge ordinary learned-memory lifetime.

### Class E — Instance / Transient Structural Edge

Where existing implementation marks an edge or its endpoint as transient/non-lockable.

### Class F — Role / Event Edge

Where `kind` belongs to the existing structural/event role family.

Additional classes may be reported if already present in the frozen implementation.

No new edge kind may be invented for this experiment.

---

# 15. Primary Forensic Phase PF-0 — Baseline Integrity

Before all scientific observations:

1. verify English Encoder v2 remains frozen;
2. run current full test baseline;
3. run ruff;
4. run repository type-check policy;
5. verify all canonical signatures;
6. record current Law 1/2/3/5/8 constants;
7. verify no uncommitted semantic Law-3 modification exists;
8. build runtime owner map;
9. prove instrumentation transparency.

PF-0 must pass before PF-1.

---

# 16. Primary Forensic Phase PF-1 — Creation Forensics

## Objective

Answer only:

\[
\boxed{\text{Do Nodes and Edges get created before pruning can explain their absence?}}
\]

Use a small deterministic set of English sentences that Encoder v2 marks `COMPLETE`.

The primary set should contain approximately **20 sentences** and cover:

- copular definition;
- adjective/property binding;
- active SVO;
- possession;
- prepositional relation;
- quantity binding;
- proper-name relation;
- passive normalization;
- simple relative clause;
- ordinary event sequences.

The exact sentence set must be frozen before execution in:

```text
law3_pf1_creation_set.json
```

For each sentence preserve:

```text
CaseID
RawSentence
EncoderDisposition
EncoderEpisodes
SourceEpisodeID
ExpectedGraphAddressableSymbols
ExpectedRelationStructures
```

No LLM may generate the expected graph structures after seeing runtime output.

---

# 17. PF-1 Required Metrics

For each case and cumulative across the set:

```text
EncoderUniqueSymbols
NodesBefore
NodesCreatedThisCase
UniqueNodesEverCreated
NodesAfterCreationPreLaw3
NodesAfterLaw3
NodesAfterGC
PeakAliveNodes
FinalAliveNodes

EdgesBefore
EdgesCreatedThisCase
EdgesReusedThisCase
EdgesReinforcedThisCase
UniqueEdgesEverCreated
EdgesPreLaw3
EdgesPostLaw3
PeakAliveEdges
FinalAliveEdges
```

Also record:

\[
NodeCreationYield
=
\frac{
GraphAddressableEncoderSymbolsMaterialized
}{
GraphAddressableEncoderSymbolsExpected
}
\]

where the denominator is defined only by the frozen graph-addressing contract, not by an invented ontology.

And:

\[
ImmediateEdgeSurvivalRate
=
\frac{
EdgesAliveAfterLaw3
}{
EdgesPresentImmediatelyBeforeLaw3
}
\]

---

# 18. PF-1 Scientific Interpretation

### Outcome PF1-A — Creation Failure

If Encoder v2 emits valid graph-addressable symbols but few/no Nodes are materialized:

\[
\boxed{\text{CreationPipelineFailure}}
\]

Do not blame Law 3.

### Outcome PF1-B — Node Creation Works, Edge Creation Fails

If Nodes materialize but expected local relations do not:

\[
\boxed{\text{EdgeCreationFailure}}
\]

Do not blame Law 3.

### Outcome PF1-C — Creation Works

If substantial Nodes/Edges exist before Law 3:

\[
\boxed{\text{CreationConfirmed}}
\]

Proceed to PF-2.

No arbitrary numeric threshold is frozen for "substantial." The report must show exact per-case mappings and counts.

---

# 19. Primary Forensic Phase PF-2 — Single-Exposure Death Trajectory

## Objective

For edges that are successfully created, determine their exact survival trajectory without reinforcement.

Select representative target edges from observed edge classes, especially:

- ordinary unprotected forward edge;
- ordinary unprotected reverse/lateral edge if present;
- role/event edge;
- salience-protected structural edge if present.

Do not force a class to exist.

If a class is absent, report it as absent.

---

# 20. Definition of a Non-Reinforcing Tick

For a target edge \(e\), a **NonReinforcingTick** is a lawful runtime tick during which:

```text
e is alive at tick start
e receives no Law-2 update
e's n_ij does not increase
e's context set is not expanded by target re-exposure
e's last-update tick remains unchanged
```

The trial must verify this condition from telemetry.

Do not define gap length merely by counting loop iterations.

---

# 21. PF-2 Gap Driver

Primary gap driver:

**deterministic unrelated external episodes** that do not mention or reactivate the target relation.

This best approximates natural corpus exposure.

A fixed filler manifest must be frozen:

```text
law3_gap_filler_manifest.json
```

The filler stream must:

- parse `COMPLETE` in Encoder v2;
- not contain target symbols;
- not intentionally reinforce target edges;
- remain identical across comparable runs.

Optional idle-tick control is allowed only if the frozen runtime already supports lawful time advancement without new semantics.

Idle ticks may not replace the primary unrelated-exposure condition.

---

# 22. PF-2 Survival Observation Horizon

For each target edge, observe at least:

\[
g \in
\{1,2,4,8,16,32,64,128\}
\]

non-reinforcing ticks, or until lawful deletion occurs.

After each selected gap point record:

```text
Alive / Dead
Weight
Salience
Floor
Locked
tagged
n_ij
ContextCount
LastUpdateTick
```

If deletion occurs between checkpoints, record the exact death tick.

---

# 23. Analytical Unprotected-Edge Control

For an edge with:

```text
Locked = 0
tagged = 0
is_intrinsic = 0
W_floor = 0
no reinforcement
```

the frozen Law-3 prediction is:

\[
W(k)=W_0-k\lambda_{decay}
\]

until pruning.

The expected first pruning application is:

\[
k^*
=
\min
\left\{
k\ge1:
W_0-k\lambda_{decay}
\le
\theta_{prune}
\right\}
\]

with:

\[
\lambda_{decay}=0.020
\]

\[
\theta_{prune}=0.05
\]

This analytical result is a **consistency control**, not a new law and not a performance target.

Observed runtime lifetime must be compared against it.

For tagged/protected edges, do not use this simple formula because \(S\) and \(W_{floor}\) are dynamic.

---

# 24. PF-2 Required Outputs

For each target edge generate a trajectory:

```text
Tick
UpdatedThisTick
W_before
W_after
S_before
S_after
Floor_before
Floor_after
tagged
Locked
n_ij
ContextCount
Alive
PruneEvent
NodeOrphanEvent
NodeDeletionEvent
```

Produce:

- raw CSV/JSONL;
- human-readable trajectory table;
- weight-vs-tick plot data;
- survival-state series;
- exact death attribution.

---

# 25. Primary Forensic Phase PF-3 — Repetition × Gap Matrix

## Objective

Measure how reinforcement frequency interacts with Law 3.

Use lawful independent exposures.

A re-exposure must be a genuinely new external episode identity.

\[
\boxed{Retry \neq IndependentExperience}
\]

Transport retry, duplicate replay, or reused source identity must not be counted as reinforcement evidence.

---

# 26. PF-3 Exposure Counts

Test:

\[
r \in
\{1,2,3,5,10\}
\]

independent exposures where practical.

---

# 27. PF-3 Gap Matrix

For each selected target relation, combine exposure count with gaps:

\[
g \in
\{1,2,4,8,16,32,64,128\}
\]

The full matrix may stop a branch once the target edge is already dead and cannot lawfully receive reinforcement without being recreated.

If recreated, record:

```text
RECREATED_AFTER_DEATH
```

as a new lifecycle event rather than pretending the original edge survived.

---

# 28. PF-3 What Must Be Measured

For every matrix cell:

```text
ExposureCount
IndependentEpisodeCount
GapTicks
EdgeCreatedCount
EdgeRecreatedCount
ReinforcementCount
WeightAfterEachExposure
MinimumWeightBetweenExposures
MaximumWeight
n_ij
ContextCount
tagged
Locked
LockTick
AliveAtEnd
DeathTick
DeathCause
```

This answers:

\[
\boxed{
HowManyIndependentExposuresToSurvive(g)?
}
\]

and:

\[
\boxed{
MaximumGapBeforeDeath(r)?
}
\]

---

# 29. Law-5 Consolidation Transition

PF-3 must explicitly observe whether/when:

\[
W\ge0.75
\]

\[
n_{ij}\ge3
\]

\[
|\mathcal{C}_{ij}|\ge2
\]

or another already-lawful gate condition is satisfied.

Record:

```text
LockEligibilityTick
ActualLockedTick
ConditionW
ConditionN
ConditionContexts
ConditionGate
ConditionFailureCount
```

If repeated exposure never reaches lock, do not infer why until all conditions are individually reported.

Possible finding:

\[
\boxed{\text{ConsolidationGateUnreachableUnderNaturalGap}}
\]

is allowed, but only with direct evidence.

---

# 30. Law-8 Protection Stratification

Because structurally salient facts may be protected without repeated exposure, PF-2/PF-3 must compare at least:

- an ordinary untagged edge;
- a structurally tagged/protected edge, if naturally produced.

Record:

\[
S(t)
\]

\[
W_{floor}(t)
\]

\[
tagged(t)
\]

throughout the trajectory.

The report must not describe a protected edge as "Law-3-resistant because of Law 3."

If survival comes from Law 8:

\[
\boxed{\text{SurvivalOwner = Law 8 Protection}}
\]

If survival comes from Law 5:

\[
\boxed{\text{SurvivalOwner = Law 5 Lock}}
\]

---

# 31. Primary Forensic Phase PF-4 — Node Death After Edge Loss

## Objective

Explain the very small final node count seen historically.

For every target Node whose last incident edge is removed:

record:

```text
LastIncidentEdgeID
LastIncidentEdgeRemovedTick
DegreeImmediatelyAfterEdgeRemoval
ActivationImmediatelyAfterEdgeRemoval
IntrinsicFlag
OrphanConditionSatisfied
NodeDeletedSameTick
NodeDeletionTick
```

Primary question:

\[
\boxed{
EdgePruning
\rightarrow
Orphaning
\rightarrow
CellularDeath?
}
\]

Measure exact frequency.

---

# 32. PF-4 Attribution Metrics

Report:

\[
OrphanAfterPruneRate
=
\frac{
NodesThatBecomeOrphansAfterLaw3EdgePrune
}{
NodesWhoseLastIncidentEdgeWasLaw3Pruned
}
\]

and:

\[
OrphanDeathRate
=
\frac{
OrphanNodesDeleted
}{
EligibleOrphanNodes
}
\]

Also:

```text
NodesEverCreated
NodesEverOrphaned
NodesDeletedByOrphanGC
NodesSurvivingDespiteZeroRecentUse
```

This phase is critical for resolving the historical "22 Nodes" mystery.

---

# 33. Primary Forensic Phase PF-5 — Small Natural Sparse-Repetition Run

This phase occurs only after PF-1 through PF-4.

Use approximately **50–100 natural English sentences** that Encoder v2 marks `COMPLETE`.

The set must contain semantically repeated relations at naturally separated positions.

Example conceptual pattern:

```text
Falcons are birds.
...
Birds have feathers.
...
Falcons hunt animals.
...
A falcon is a bird of prey.
...
Falcons have wings.
...
Many birds can fly.
...
Falcons are fast birds.
```

The purpose is not benchmark accuracy.

The purpose is to observe whether semantic recurrence in a small natural stream reaches reinforcement and consolidation before Law 3 deletes the relation.

The exact sentence stream must be frozen before execution.

---

# 34. PF-5 Required Metrics

Report:

```text
TotalSentences
TotalEncoderEpisodes
UniqueNodesEverCreated
PeakAliveNodes
FinalAliveNodes
UniqueEdgesEverCreated
PeakAliveEdges
FinalAliveEdges
EdgesCreated
EdgesReinforced
EdgesRecreatedAfterDeath
EdgesPrunedByLaw3
NodesDeletedByOrphanGC
EdgesTaggedByLaw8
EdgesLockedByLaw5
MedianUnprotectedEdgeLifetime
MaxUnprotectedEdgeLifetime
MedianInterExposureGap
ReinforcementSuccessByGap
```

Also preserve a set of named relation lifecycles longitudinally.

---

# 35. No Large-Corpus Run

Trial 01 must not ingest:

- 1K Wikipedia articles;
- 10K articles;
- 100K articles;
- full Simple Wikipedia.

This is a small forensic trial.

A large rerun before resolving persistence causality would obscure the result.

---

# 36. Primary Metrics

The final report must include at least:

## Creation

\[
UniqueNodesEverCreated
\]

\[
UniqueEdgesEverCreated
\]

\[
NodeCreationYield
\]

\[
EdgeCreationYield
\]

## Survival

\[
PeakAliveNodes
\]

\[
FinalAliveNodes
\]

\[
PeakAliveEdges
\]

\[
FinalAliveEdges
\]

## Law-3 Destruction

\[
EdgesPrunedByLaw3
\]

\[
PruneAttributionRate
\]

\[
MedianEdgeLifetime
\]

\[
LifetimeByEdgeClass
\]

## Node Death

\[
NodesDeletedByOrphanGC
\]

\[
OrphanAfterPruneRate
\]

## Reinforcement

\[
EdgesReinforced
\]

\[
ReinforcementCountDistribution
\]

\[
MaximumSurvivableGapByExposureCount
\]

## Consolidation

\[
EdgesTaggedByLaw8
\]

\[
EdgesLockedByLaw5
\]

\[
LockAttainmentRate
\]

\[
TicksToLock
\]

---

# 37. Creation vs Persistence Decision Table

The report must classify the evidence using the following causal matrix.

| Nodes Created | Edges Created | Rapid Destruction | Interpretation |
|---|---|---|---|
| No | — | — | Creation/materialization defect |
| Yes | No | — | Edge-creation defect |
| Yes | Yes | No | Persistence broadly functioning in tested regime |
| Yes | Yes | Yes | Persistence failure/short-lifetime regime supported |
| Yes | Yes | Selective | Stratify by protection, kind, direction, salience, lock |

Do not compress selective outcomes into one global PASS/FAIL.

---

# 38. Timescale-Mismatch Criterion

The phrase:

\[
\boxed{\text{Law-3 Timescale Mismatch}}
\]

may be used only if the evidence shows:

1. target relations are correctly created;
2. target relations receive no hidden reinforcement;
3. Law 3 is the actual pruning owner;
4. measured unprotected lifetimes are short relative to measured natural inter-exposure gaps in PF-5;
5. the relation commonly dies before lawful recurrence can reinforce/consolidate it.

This is an empirical criterion, not a subjective judgment.

---

# 39. No Premature Calibration

The following reactions are forbidden during Trial 01:

```text
"Lifetime is too short, lower lambda."
"Too many nodes died, lower prune threshold."
"Law 5 did not lock, lower N_MIN."
"Structural facts survive, tag more edges."
"Add replay."
"Protect all word nodes."
"Pre-allocate vocabulary nodes."
```

Any such idea belongs in the **post-trial hypothesis section only**.

No code change may be made from it during the run.

---

# 40. Experimental Invariants

The trial freezes the following invariants.

### L3F-INV-001 — Frozen Law 3

Law 3 equations and parameters remain unchanged.

### L3F-INV-002 — Frozen Creation Physics

Law 1 remains unchanged.

### L3F-INV-003 — Frozen Reinforcement Physics

Law 2 / Law 2-b remain unchanged.

### L3F-INV-004 — Frozen Consolidation Physics

Law 5 remains unchanged.

### L3F-INV-005 — Frozen Salience Physics

Law 8 remains unchanged.

### L3F-INV-006 — Encoder v2 Frozen

No English Encoder semantic change during the trial.

### L3F-INV-007 — No New Cognitive Primitive

Telemetry does not become cognition.

### L3F-INV-008 — No New Normative Law

Trial instrumentation creates no new law.

### L3F-INV-009 — No Persistent Learned Telemetry

Lifecycle logs live outside graph cognition.

### L3F-INV-010 — Instrumentation Transparency

Instrumentation on/off produces identical cognitive behavior.

### L3F-INV-011 — Runtime Order Preserved

Instrumentation does not reorder owners/laws.

### L3F-INV-012 — Pre-Law-3 Visibility

Creation must be observed before Law-3 destruction.

### L3F-INV-013 — Edge Pruning Separate from Node GC

Both events are attributed independently.

### L3F-INV-014 — Exact Death Owner

No inferred deletion cause without runtime evidence.

### L3F-INV-015 — Independent Exposure Identity

Reinforcement trials use lawful independent episode identities.

### L3F-INV-016 — Retry Is Not Experience

Transport retry does not count as independent reinforcement.

### L3F-INV-017 — Non-Reinforcing Gap Verified

Gap ticks must actually leave target edge unupdated.

### L3F-INV-018 — Protection Fields Preserved

`tagged`, `Locked`, `S`, `W_floor`, `is_intrinsic` are measured and not overridden.

### L3F-INV-019 — Edge Classes Not Collapsed

Protected and unprotected edges are analyzed separately.

### L3F-INV-020 — Node Counts Are Lifecycle Counts

Report Created, PeakAlive, and FinalAlive separately.

### L3F-INV-021 — Edge Counts Are Lifecycle Counts

Report Created, PeakAlive, and FinalAlive separately.

### L3F-INV-022 — No Large-Corpus Training

Trial remains small and diagnostic.

### L3F-INV-023 — No Performance-Driven Repair

Poor results do not authorize tuning.

### L3F-INV-024 — Raw Trajectories Preserved

Lifecycle traces must be retained.

### L3F-INV-025 — Canonical Signatures Conserved

All frozen upstream signatures remain unchanged.

### L3F-INV-026 — Protocol Verdict Separate from Scientific Verdict

A valid trial may demonstrate a serious Law-3 defect.

---

# 41. Protocol Integrity Gates

Before declaring the trial scientifically usable, evaluate:

### L3F-G01 — Baseline Integrity

Current tests, signatures, and law constants recorded before execution.

### L3F-G02 — Instrumentation Transparency

Instrumented and non-instrumented control digest match.

### L3F-G03 — Runtime Owner Map

Actual within-tick owner order documented.

### L3F-G04 — Creation Visibility

PF-1 captures state before and after Law 3.

### L3F-G05 — Lifecycle Attribution

Edge and Node deaths have explicit owners.

### L3F-G06 — Gap Integrity

PF-2/PF-3 gaps are verified non-reinforcing ticks.

### L3F-G07 — Re-exposure Integrity

Independent episode identity is preserved; retries are not counted.

### L3F-G08 — Protection Stratification

Law-5/Law-8/intrinsic protection is separated from ordinary edges.

### L3F-G09 — Raw Evidence Preservation

Machine-readable lifecycle logs and manifests are complete.

### L3F-G10 — Frozen Architecture

No Law/Encoder/cognitive-semantic change occurred during the trial.

### L3F-G11 — Upstream Conservation

Canonical signatures remain unchanged.

### L3F-G12 — Final Causal Accounting

Creation, pruning, consolidation, and orphan-GC results are reported separately.

Required protocol condition:

\[
\boxed{L3F\text{-}G01..G12=12/12\ PASS}
\]

This means only that the experiment is scientifically valid.

It does not mean Law 3 is good.

---

# 42. Stop Conditions

Stop the scientific run only for:

- instrumentation changes cognitive behavior;
- canonical signature drift;
- invariant violation;
- corrupted graph state;
- non-restorable state;
- inability to observe pre/post-Law-3 boundaries without semantic modification;
- telemetry entering persistent cognitive state;
- runtime crash that prevents reliable attribution;
- host/resource failure;
- need to modify frozen architecture to continue.

Do **not** stop because:

- all edges die;
- no edges die;
- no nodes are created;
- Law 5 never locks;
- Law 8 dominates survival;
- results are unexpectedly poor.

Those are scientific outcomes.

---

# 43. Failure / Outcome Taxonomy

Machine-readable trial outcomes may use:

```text
NODE_NOT_CREATED
EDGE_NOT_CREATED
EDGE_CREATED
EDGE_REINFORCED
EDGE_DECAYED
EDGE_PRUNED_BY_LAW3
EDGE_RECREATED_AFTER_DEATH
EDGE_TAGGED_BY_LAW8
EDGE_LOCKED_BY_LAW5
NODE_ORPHANED
NODE_DELETED_BY_ORPHAN_GC
NODE_SURVIVED
EDGE_SURVIVED
INTRINSIC_EXEMPT
PROTECTED_FLOOR_ACTIVE
UNKNOWN_RUNTIME_ATTRIBUTION
INSTRUMENTATION_FAILURE
INVARIANT_FAILURE
RESOURCE_FAILURE
```

These are telemetry labels only.

They are not cognitive states.

---

# 44. Required Machine-Readable Artifacts

The execution must produce:

1. `DGCA-LAW3-PERSISTENCE-FORENSICS-TRIAL-01-REPORT.md`
2. `law3_runtime_owner_map.json`
3. `law3_instrumentation_transparency.json`
4. `law3_pf1_creation_set.json`
5. `law3_pf1_creation_trace.jsonl`
6. `law3_edge_lifecycles.jsonl`
7. `law3_node_lifecycles.jsonl`
8. `law3_gap_filler_manifest.json`
9. `law3_pf2_single_exposure_trajectories.jsonl`
10. `law3_pf3_repetition_gap_matrix.jsonl`
11. `law3_pf4_orphan_gc_attribution.jsonl`
12. `law3_pf5_natural_stream_manifest.json`
13. `law3_pf5_natural_stream_trace.jsonl`
14. `law3_protocol_invariants.json`
15. `law3_protocol_release_gates.json`
16. `law3_signature_conservation.json`
17. `law3_failures.jsonl`

Optional visualization artifacts may be added, but raw data is authoritative.

---

# 45. Required Human-Readable Tables

The final report must include at least:

## Table A — Creation Accounting

```text
Case
EncoderSymbols
NodesCreated
EdgesCreated
NodesPreLaw3
EdgesPreLaw3
NodesPostLaw3
EdgesPostLaw3
NodesPostGC
```

## Table B — Edge Lifetime

```text
Edge
Class
InitialW
InitialS
InitialFloor
Reinforcements
DeathTick
Lifetime
DeathOwner
```

## Table C — Repetition × Gap

```text
Relation
ExposureCount
Gap
MaxW
MinW
Locked
AliveAtEnd
DeathTick
```

## Table D — Node Orphan Attribution

```text
Node
CreatedAt
EdgesEverAttached
LastEdgePrunedAt
OrphanedAt
DeletedAt
DeletionOwner
```

## Table E — Natural Sparse Stream

```text
Relation
FirstExposure
NextExposure
Gap
AliveBeforeRepeat
ReinforcedOrRecreated
FinalStatus
```

---

# 46. Required Final Scientific Answers

The final report must explicitly answer:

1. Did English Encoder v2 symbols materialize into graph Nodes?
2. How many unique Nodes were ever created in PF-1?
3. What was the peak live Node count?
4. What was the final live Node count?
5. How many unique Edges were ever created before Law 3?
6. Did expected local relations exist before Law 3?
7. What proportion of edges survived their first Law-3 application?
8. Which edge classes died fastest?
9. What were the median and exact representative lifetimes?
10. Did measured unprotected lifetimes match the frozen Law-3 equation?
11. How many Edges were pruned specifically by Law 3?
12. How many Nodes became orphaned because their last Edge was Law-3-pruned?
13. How many eligible orphan Nodes were deleted?
14. Did Law 8 create meaningful protection floors?
15. Which relations survived because of Law 8?
16. Did any relation reach Law-5 lock?
17. At what exposure count and gap did locking occur?
18. Which Law-5 condition was limiting when lock did not occur?
19. What maximum inter-exposure gap was survivable after 1, 2, 3, 5, and 10 exposures?
20. Did dead Edges get recreated rather than reinforced?
21. In PF-5, were natural semantic repetitions usually reinforcement events or recreations after death?
22. Was a Law-3 timescale mismatch empirically demonstrated?
23. Was the historically tiny final Node count explained by orphan GC after pruning?
24. What is the dominant causal bottleneck after Encoder repair?
25. What should the next experiment investigate?
26. What **must not** yet be changed because evidence remains insufficient?

---

# 47. Allowed Final Scientific Verdicts

The report must separate **Protocol Integrity** from **Scientific Outcome**.

## Protocol Integrity

```text
PROTOCOL_PASS
PROTOCOL_FAIL
BLOCKED
```

## Scientific Outcome

One or more evidence-backed labels may be used:

```text
CREATION_FAILURE
EDGE_CREATION_FAILURE
CREATION_CONFIRMED
PERSISTENCE_FAILURE
LAW3_TIMESCALE_MISMATCH_SUPPORTED
LAW3_TIMESCALE_MISMATCH_NOT_SUPPORTED
ORPHAN_GC_IS_MAJOR_SECONDARY_LOSS_PATH
LAW8_PROTECTION_DOMINATES_SELECTED_RELATIONS
LAW5_CONSOLIDATION_REACHED
LAW5_CONSOLIDATION_NOT_REACHED
NATURAL_REPETITION_REINFORCES
NATURAL_REPETITION_MOSTLY_RECREATES
NO_CRITICAL_PERSISTENCE_DEFECT_DEMONSTRATED
MIXED_EDGE_CLASS_OUTCOME
```

No label may be selected without corresponding raw evidence.

---

# 48. Phase-III Boundary

This trial does not open Phase III.

After the report is complete, possible future questions may include:

- Law-3 parameter calibration;
- Law-3 timescale redesign;
- local-opportunity-based decay;
- consolidation replay;
- developmental curriculum;
- symbol-identity persistence;
- revised protection policy.

But the report may list these only as **questions/hypotheses**.

It must not implement them.

---

# 49. Relationship to Future Curriculum Testing

If PF-3/PF-5 demonstrates that lawful repeated experience stabilizes relations when recurrence falls within a measurable survival window, then a future curriculum experiment becomes scientifically justified.

If creation or persistence fails before useful recurrence is possible, curriculum testing must remain deferred.

Therefore:

\[
\boxed{
Trial02Curriculum
\text{ depends on }
Law3ForensicEvidence
}
\]

---

# 50. Final Required Metrics Block

The final report must end with a block equivalent to:

```text
============================================================
DGCA LAW-3 PERSISTENCE FORENSICS — TRIAL 01

PROTOCOL:
DGCA-Law3-Persistence-Forensics-Trial-01-Specification-v1.0

ARCHITECTURE CHANGES:
0

LAW 3 CHANGES:
0

ENCODER CHANGES:
0

NEW COGNITIVE PRIMITIVES:
0

NEW NORMATIVE LAWS:
0

PF-0 BASELINE:
PASS / FAIL

INSTRUMENTATION TRANSPARENCY:
PASS / FAIL

PF-1 CREATION:
Sentences:
Unique Encoder Symbols:
Unique Nodes Ever Created:
Peak Alive Nodes:
Final Alive Nodes:
Unique Edges Ever Created:
Peak Alive Edges:
Final Alive Edges:
Node Creation Yield:
Edge Creation Yield:

PF-2 SINGLE-EXPOSURE LIFETIME:
Target Edges:
Median Unprotected Lifetime:
Minimum Unprotected Lifetime:
Maximum Unprotected Lifetime:
Law3-Pruned Edges:
Protected Edge Outcomes:
Analytical-vs-Observed Consistency:

PF-3 REPETITION × GAP:
Exposure counts tested:
Gap values tested:
Maximum survivable gap after 1 exposure:
Maximum survivable gap after 2 exposures:
Maximum survivable gap after 3 exposures:
Maximum survivable gap after 5 exposures:
Maximum survivable gap after 10 exposures:
Edges reaching Law5 lock:
Median ticks/exposures to lock:
Recreations after death:

PF-4 ORPHAN GC:
Nodes whose last edge was Law3-pruned:
Nodes orphaned:
Eligible orphans deleted:
OrphanAfterPruneRate:
OrphanDeathRate:

PF-5 NATURAL SPARSE STREAM:
Sentences:
Nodes ever created:
Edges ever created:
Edges reinforced:
Edges recreated after death:
Edges pruned:
Nodes GC-deleted:
Law8-tagged edges:
Law5-locked edges:

LAW3 TIMESCALE MISMATCH:
SUPPORTED / NOT SUPPORTED / INCONCLUSIVE

DOMINANT CAUSAL BOTTLENECK:
...

PROTOCOL INVARIANTS:
L3F-INV-001..026:
x/26

PROTOCOL GATES:
L3F-G01..G12:
x/12

UPSTREAM SIGNATURES:
Phase-I:
RFC-11:
RFC-12:
RFC-13:
RFC-14:
RFC-15:
RFC-16:

PROTOCOL INTEGRITY VERDICT:
PROTOCOL_PASS / PROTOCOL_FAIL / BLOCKED

SCIENTIFIC OUTCOME:
...

READY FOR LAW-3 REDESIGN DISCUSSION:
YES / NO

READY FOR LARGE-CORPUS RETRAINING:
NO

READY FOR CURRICULUM TRIAL:
YES / NO / DEFERRED
============================================================
```

---

# 51. Interpretation Discipline

The following statements are forbidden unless directly supported:

- "Law 3 caused the RDT01 failure" merely because final memory is small.
- "Nodes were never created" without pre-Law-3 observation.
- "Law 3 deleted a Node" when only its Edges were pruned and orphan GC deleted the Node.
- "Three repetitions are enough" without satisfying all Law-5 conditions.
- "Definitions survive" without attributing Law-8 protection where applicable.
- "The model forgets after N sentences" when N was actually measured in runtime ticks.
- "Curriculum will solve the problem" before recurrence-vs-survival evidence.
- "Lower decay is the solution" before the trial is complete.
- "No catastrophic forgetting" from this trial.
- "O(1)" or scalability claims from small forensic timing.
- "Natural language learning is fixed" merely because Encoder v2 is fixed.

---

# 52. Final Principle

The historical observation:

\[
FinalNodes \approx 22
\]

is not itself a diagnosis.

The correct causal decomposition is:

\[
Text
\rightarrow
EncoderEpisodes
\rightarrow
NodeCreation
\rightarrow
EdgeCreation
\rightarrow
Reinforcement
\rightarrow
Protection/Lock
\rightarrow
Decay
\rightarrow
Pruning
\rightarrow
Orphaning
\rightarrow
CellularDeath
\]

Trial 01 must observe every relevant transition.

The experiment succeeds scientifically when it can answer:

\[
\boxed{\textbf{Did memory fail to form, or did formed memory fail to survive?}}
\]

and, if memory failed to survive:

\[
\boxed{\textbf{Exactly which lawful mechanism killed it, after how many ticks, and before which opportunity for reinforcement?}}
\]

Only after those questions are answered may DGCA redesign Law 3.

---

# 53. Protocol Freeze Condition

This specification becomes frozen when explicitly approved.

After freeze:

- no experimental question may be removed because it produces an inconvenient result;
- no threshold may be added post hoc;
- no Law-3 parameter may be changed during Trial 01;
- no corpus scale may be expanded to compensate for poor results;
- no result may be repaired and resumed as if it were the same run.

Any semantic intervention creates a future experiment version.

\[
\boxed{
\textbf{DGCA Law-3 Persistence Forensics — Trial 01}
}
\]

\[
\boxed{
\textbf{Observe First. Attribute Exactly. Redesign Later.}
}
\]
