# DGCA Phase 2.5 — Small Natural-Text Persistence Validation Trial 02 Specification v1.0

## Post-Law-3-Abolition Empirical Persistence Re-Validation

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.5 — Empirical Validation  
**Trial:** Small Natural-Text Persistence Validation — Trial 02  
**Version:** 1.0  
**Status:** **PROTOCOL — CANDIDATE FOR FREEZE**  
**Architecture:** **POST-LAW-3-ABOLITION BASELINE**  
**Canonical Post-Abolition Baseline Signature:** `915119d40643cb97`  
**English Encoder:** v2 — IMPLEMENTED / VERIFIED / FROZEN  
**Law 3:** **ABOLISHED / RESERVED**  
**Architecture Changes During Trial:** **0**  
**Primary Principle:** **Create → Persist → Reinforce**

---

# 1. Purpose

Trial 02 verifies, on small natural English input, that the post-Law-3-ablation DGCA memory architecture behaves according to the new persistence rule:

\[
\boxed{NoEvidence \Rightarrow NoPersistentWeightChange}
\]

and that natural recurrence after a long unrelated gap:

\[
\boxed{ReinforcesExistingMemory}
\]

rather than:

\[
\boxed{RecreatesDeadMemory}
\]

The trial also verifies that lawful negative evidence still modifies learned memory through Law 13, transient `inst:*` structures retire at scope end, persistent concepts/event memory survive transient cleanup, and no hidden forgetting mechanism remains.

---

# 2. Scientific Questions

## SNTP-Q01 — One-Shot Persistence

Does a persistent relation learned once remain alive after many unrelated natural-text episodes?

\[
\boxed{OneShotRelation \rightarrow StillAlive}
\]

## SNTP-Q02 — Sparse Recurrence

When the same relation returns after a long gap, is the existing Edge reinforced?

\[
\boxed{ExistingEdge \rightarrow Reinforced}
\]

rather than:

\[
\boxed{DeadEdge \rightarrow Recreated}
\]

## SNTP-Q03 — Negative Evidence Control

Can lawful validated negative evidence still reduce persistent learned weight through Law 13?

\[
\boxed{Evidence^- \rightarrow W\downarrow}
\]

## SNTP-Q04 — Transient Lifecycle Control

Are transient `inst:*` structures explicitly retired at scope end while persistent knowledge remains intact?

\[
\boxed{TransientRetires \land PersistentKnowledgeSurvives}
\]

---

# 3. Frozen Architecture Rule

During Trial 02:

```text
ArchitectureChanges = 0
EncoderChanges = 0
Law2Changes = 0
Law5Changes = 0
Law6Changes = 0
Law8Changes = 0
Law11Changes = 0
Law13Changes = 0
TransientLifecycleChanges = 0
NewParameters = 0
NewCognitivePrimitives = 0
NewNormativeLaws = 0
```

Poor results do not authorize repair during the trial.

---

# 4. Canonical Baseline

The trial begins from the verified post-Law-3-ablation implementation:

```text
Law 3 Status:
ABOLISHED / RESERVED

Canonical Post-Abolition Baseline:
915119d40643cb97

Full Regression:
2416 / 2416 PASS

Forbidden Mechanism Audit:
16 / 16 PASS

Post-Abolition Invariants:
20 / 20 PASS

Verification Gates:
16 / 16 PASS
```

The pre-Law-3-ablation historical signature remains historical only:

```text
c4b2549940a49789
```

---

# 5. Input Scale

Use a deterministic stream of:

\[
\boxed{60\text{–}100\ natural\ English\ sentences}
\]

All primary-learning sentences must be analyzed by English Encoder v2 as:

```text
COMPLETE
```

Unsupported sentences may be recorded, but must not silently enter learning.

Forbidden:

```text
Simple Wikipedia full corpus
1K+ article run
curriculum training
parameter tuning
external LLM preprocessing
semantic augmentation
```

---

# 6. Natural-Text Stream Design

The stream must contain three relation groups.

## Group A — One-Shot Persistent Relations

Approximately 10–20 relations appear once and are never intentionally repeated.

Purpose:

\[
\boxed{NoRecurrence \Rightarrow MemoryStillPersists}
\]

## Group B — Sparse Recurring Relations

Approximately 8–15 target relations recur later in semantically compatible natural formulations.

The second exposure must not be a transport retry or identical source replay.

## Group C — Controls

Include:

1. Law-13 negative-evidence cases;
2. transient `inst:*` lifecycle cases;
3. persistent Event/role memory control if available through existing supported natural-text behavior.

---

# 7. Target Gap Ranges

Sparse recurring relations should be distributed across gaps at or above the former Law-3 failure region.

Target observed gaps:

\[
\boxed{16,\ 32,\ 64,\ 128}
\]

The stream must include at least one recurrence after `g >= 16`, one after `g >= 32`, one after `g >= 64`, and preferably one after `g >= 128` if stream length permits.

Gap is measured in actual lawful processed episodes/ticks between target relation exposures.

---

# 8. Core Relation Lifecycle Record

For each target persistent relation record:

```text
RelationID
FirstSentenceID
FirstExposureTick
FirstEdgeID
SourceNode
TargetNode
EdgeKind
InitialWeight
InitialReinforcementCount

GapTicks

AliveBeforeRecurrence
EdgeIDBeforeRecurrence
WeightBeforeRecurrence
ReinforcementCountBeforeRecurrence

SecondSentenceID
SecondExposureTick
SecondExposureAction:
    REINFORCED
    RECREATED
    UNRESOLVED

EdgeIDAfterRecurrence
WeightAfterRecurrence
ReinforcementCountAfterRecurrence

FinalAlive
FinalWeight
FinalReinforcementCount
```

---

# 9. Edge Identity Rule

A recurrence counts as successful reinforcement only if:

```text
Edge existed before recurrence
AND
same lawful structural Edge identity remains
AND
reinforcement count and/or lawful weight increases
```

A recurrence is classified `RECREATED` if the original Edge no longer exists and a new lifecycle is created.

Transport retries or duplicate processing are not independent recurrence.

---

# 10. SNTP-P1 — One-Shot Persistence

For each Group-A relation:

1. ingest once;
2. record Edge identity and weight;
3. process the remaining unrelated natural-text stream;
4. inspect the relation at the end.

Required measurements:

```text
Created
AliveAtEnd
InitialWeight
FinalWeight
WeightDrift
EdgeIDStable
```

Primary invariant:

\[
\boxed{FinalWeight=InitialWeight}
\]

unless an actual lawful evidence event touched the relation.

---

# 11. SNTP-P2 — Sparse Natural Recurrence

For each Group-B relation:

1. record first creation;
2. process unrelated sentences;
3. immediately before recurrence, inspect target Edge;
4. process recurrence;
5. determine whether it was reinforced or recreated.

Primary success path:

\[
\boxed{Created \rightarrow LongGap \rightarrow Alive \rightarrow Reinforced}
\]

Former failure path:

\[
\boxed{Created \rightarrow Gap \rightarrow Dead \rightarrow Recreated}
\]

must not occur from inactivity alone.

---

# 12. SNTP-P3 — Law 13 Negative-Evidence Control

Use a small deterministic set of cases where the existing runtime can produce lawful validated disappointment/prediction failure.

Do not invent artificial negative evidence semantics.

For each case record:

```text
EdgeID
WeightBeforeFailure
ValidatedFailureEvent
Law13Invoked
WeightAfterFailure
DeltaWeight
LockedBefore
LockedAfter
```

Required:

\[
\boxed{ValidatedNegativeEvidence \Rightarrow Law13Correction}
\]

and:

\[
\boxed{NoNegativeEvidence \Rightarrow NoLaw13WeightDecrease}
\]

---

# 13. SNTP-P4 — Transient Lifecycle Control

For supported transient `inst:*` structures:

1. create through normal lawful input;
2. confirm existence during scope;
3. close the lawful scope;
4. confirm explicit retirement;
5. verify persistent concept/relation survives.

Record:

```text
TransientID
PersistentConceptID
CreatedInScope
AliveDuringScope
ScopeEnd
RetiredAtScopeEnd
PersistentConceptAliveAfterCleanup
PersistentEdgesLost
```

Required:

\[
\boxed{TransientRetired=TRUE}
\]

\[
\boxed{PersistentConceptLost=FALSE}
\]

---

# 14. Optional Event Persistence Control

If the current natural-text path creates persistent Law-11 Event Nodes and role Edges, create one representative Event memory, process unrelated text, and verify the Event Node/role Edges remain alive without inactivity-based mutation.

If this cannot be exercised without architecture changes, mark:

```text
NOT_EXERCISED
```

---

# 15. Primary Metrics

The final report must include:

```text
TotalSentences
CompleteSentences
UnsupportedSentences

UniquePersistentRelationsCreated

OneShotRelations
OneShotRelationsAliveAtEnd
OneShotPersistenceRate

RecurringRelations
RecurringRelationsAliveBeforeRecurrence
ReinforcedRecurrences
RecreatedRecurrences
UnresolvedRecurrences

ReinforcementInsteadOfRecreationRate

MinimumSuccessfulGap
MedianSuccessfulGap
MaximumSuccessfulGap

PersistentWeightDriftWithoutEvidence

Law13ControlCases
Law13SuccessfulCorrections

TransientInstancesCreated
TransientInstancesRetired
PersistentConceptsLostByTransientCleanup

FinalNodes
FinalEdges
```

---

# 16. Critical Primary Metric

\[
ReinforcementInsteadOfRecreationRate
=
\frac{ReinforcedRecurrences}{ReinforcedRecurrences+RecreatedRecurrences}
\]

`UNRESOLVED` cases are excluded from this denominator and must remain visible separately.

---

# 17. Required Zero-Failure Conditions

For persistent relations with no lawful invalidation:

\[
\boxed{RecreatedAfterInactivity=0}
\]

and:

\[
\boxed{PassiveWeightDrift=0}
\]

Any nonzero occurrence is a forensic blocker requiring explanation.

---

# 18. Protocol Invariants

### SNTP-INV-001 — Frozen Post-Abolition Architecture
No semantic architecture change during Trial 02.

### SNTP-INV-002 — English Encoder v2 Frozen
No parser/encoder modification.

### SNTP-INV-003 — Law 3 Remains Abolished
No Law-3 runtime authority may reappear.

### SNTP-INV-004 — No Hidden Decay
Unrelated time/input cannot passively alter persistent `W`.

### SNTP-INV-005 — One-Shot Memory Is Eligible to Persist
Lack of recurrence alone is not deletion authority.

### SNTP-INV-006 — Recurrence Requires Existing-Edge Check
Reinforcement vs recreation is explicitly distinguished.

### SNTP-INV-007 — Retry Is Not Recurrence
Duplicate transport/retry is not independent evidence.

### SNTP-INV-008 — Negative Correction Requires Lawful Failure
Law 13 cannot weaken without actual validated negative evidence.

### SNTP-INV-009 — Transient Cleanup Is Explicit
Transient retirement occurs through lawful scope lifecycle.

### SNTP-INV-010 — Transient Cleanup Cannot Delete Persistent Knowledge
Persistent concept/Edge loss from transient cleanup is forbidden.

### SNTP-INV-011 — No Performance-Driven Repair
Failure is recorded, not patched.

### SNTP-INV-012 — No Large-Corpus Expansion
Trial remains small and diagnostic.

### SNTP-INV-013 — Post-Abolition Baseline Verified
`915119d40643cb97` is verified before trial execution.

### SNTP-INV-014 — Raw Lifecycle Evidence Preserved
Per-relation lifecycle traces are retained.

### SNTP-INV-015 — Unsupported Input Fails Closed
Unsupported sentences do not silently learn.

### SNTP-INV-016 — Protocol Verdict Separate From Capability Verdict
A valid protocol may expose post-abolition defects.

---

# 19. Verification Gates

### SNTP-G01 — Baseline Integrity
Post-abolition baseline verified.

### SNTP-G02 — Natural Stream Frozen
Input manifest fixed before execution.

### SNTP-G03 — One-Shot Persistence
No passive loss of one-shot persistent target memory.

### SNTP-G04 — Sparse Recurrence
Long-gap recurrence reaches living memory.

### SNTP-G05 — Reinforcement Not Recreation
Resolved persistent recurrence is reinforced, not recreated due to inactivity.

### SNTP-G06 — Zero Passive Weight Drift
Untouched persistent Edges remain bit-identical in weight.

### SNTP-G07 — Law 13 Control
Validated negative evidence still produces lawful correction.

### SNTP-G08 — No Spurious Law 13 Activity
No negative correction without validated failure.

### SNTP-G09 — Explicit Transient Retirement
Transient instances retire at lawful scope end.

### SNTP-G10 — Persistent Knowledge Isolation
Transient cleanup does not delete persistent knowledge.

### SNTP-G11 — No Hidden Forgetting Mechanism
Static/runtime evidence shows no passive memory-loss path.

### SNTP-G12 — Full Regression
Repository integrity remains green after trial instrumentation/execution.

Required:

\[
\boxed{SNTP\text{-}G01..G12=12/12\ PASS}
\]

---

# 20. Stop Conditions

Stop only for:

- post-abolition signature mismatch before trial;
- architecture/invariant drift;
- hidden passive forgetting;
- persistent-state corruption;
- transient cleanup deleting persistent knowledge;
- inability to distinguish reinforcement from recreation;
- instrumentation changing cognition;
- unrecoverable runtime failure.

Do not stop because a scientific outcome is poor.

---

# 21. Required Machine-Readable Artifacts

```text
DGCA-SMALL-NATURAL-TEXT-PERSISTENCE-TRIAL-02-REPORT.md
sntp_trial02_manifest.json
sntp_trial02_relation_lifecycles.jsonl
sntp_trial02_one_shot_persistence.json
sntp_trial02_sparse_recurrence.json
sntp_trial02_law13_control.json
sntp_trial02_transient_control.json
sntp_trial02_event_control.json
sntp_trial02_invariants.json
sntp_trial02_release_gates.json
sntp_trial02_signature_verification.json
sntp_trial02_failures.jsonl
```

---

# 22. Required Final Scientific Answers

The final report must explicitly answer:

1. Did one-shot natural-text relations persist to the end?
2. Was passive persistent-weight drift exactly zero?
3. Did recurring relations remain alive before recurrence?
4. Did recurrence reinforce existing Edges?
5. Did any persistent recurrence recreate a dead Edge because of inactivity?
6. What was the maximum successful observed recurrence gap?
7. Did relations survive beyond the former 16-tick Law-3 lifetime?
8. Did Law 13 still lower weight after lawful validated failure?
9. Did Law 13 remain inactive without negative evidence?
10. Were transient `inst:*` structures retired explicitly?
11. Did transient cleanup preserve persistent concepts and Edges?
12. Did persistent Event/role memory survive inactivity, if exercised?
13. Did any hidden passive forgetting mechanism appear?
14. Did the canonical post-abolition baseline remain valid?
15. Is DGCA ready for a medium-scale natural-text acquisition trial?
16. Is DGCA ready for full-corpus retraining?

The answer to #16 must remain:

```text
NO
```

until a later explicitly authorized trial.

---

# 23. Allowed Scientific Outcomes

```text
PERSISTENCE_VALIDATED
PERSISTENCE_FAILURE
SPARSE_RECURRENCE_REINFORCES
SPARSE_RECURRENCE_RECREATES
PASSIVE_WEIGHT_DRIFT_DETECTED
LAW13_CORRECTION_VALIDATED
LAW13_CORRECTION_FAILURE
TRANSIENT_RETIREMENT_VALIDATED
TRANSIENT_RETIREMENT_FAILURE
PERSISTENT_LEAKAGE_FROM_TRANSIENT_CLEANUP
EVENT_PERSISTENCE_VALIDATED
HIDDEN_FORGETTING_MECHANISM_DETECTED
MIXED_OUTCOME
```

---

# 24. Final Required Metrics Block

```text
============================================================
DGCA PHASE 2.5 — SMALL NATURAL-TEXT PERSISTENCE TRIAL 02

PROTOCOL:
DGCA-Phase-2.5-Small-Natural-Text-Persistence-Trial-02-v1.0

POST-ABOLITION BASELINE:
915119d40643cb97

ARCHITECTURE CHANGES:
0

LAW 3 STATUS:
ABOLISHED / RESERVED

ENCODER CHANGES:
0

TOTAL SENTENCES:
...

COMPLETE:
...

UNSUPPORTED:
...

ONE-SHOT PERSISTENCE:
Relations:
Alive At End:
Persistence Rate:
Passive Weight Drift:

SPARSE RECURRENCE:
Relations:
Alive Before Recurrence:
Reinforced:
Recreated:
Unresolved:
Reinforcement Instead Of Recreation Rate:
Minimum Successful Gap:
Median Successful Gap:
Maximum Successful Gap:

FORMER 16-TICK BARRIER EXCEEDED:
YES / NO

LAW 13 CONTROL:
Cases:
Successful Corrections:
Spurious Corrections:

TRANSIENT CONTROL:
Instances Created:
Instances Retired:
Persistent Concepts Lost:
Persistent Edges Lost:

EVENT CONTROL:
EXERCISED / NOT EXERCISED
Persistent Events Created:
Persistent Events Alive At End:
Role Edges Lost To Inactivity:

HIDDEN PASSIVE FORGETTING:
0 / NONZERO

PROTOCOL INVARIANTS:
SNTP-INV-001..016:
x/16

VERIFICATION GATES:
SNTP-G01..G12:
x/12

FULL REGRESSION:
PASS / FAIL

SCIENTIFIC OUTCOME:
...

READY FOR MEDIUM-SCALE NATURAL-TEXT ACQUISITION:
YES / NO

READY FOR FULL-CORPUS RETRAINING:
NO
============================================================
```

---

# 25. Closure Rule

Trial 02 succeeds scientifically if it demonstrates:

\[
\boxed{Create \rightarrow Persist \rightarrow LongGap \rightarrow Reinforce}
\]

while preserving:

\[
\boxed{NegativeEvidence \rightarrow Law13Correction}
\]

and:

\[
\boxed{TransientScopeEnd \rightarrow TransientRetirement}
\]

The trial verifies persistence behavior only. It is not proof of large-scale natural-language learning.

---

# 26. Final Principle

\[
\boxed{\textbf{Persistent knowledge survives silence.}}
\]

\[
\boxed{\textbf{Evidence changes memory.}}
\]

\[
\boxed{\textbf{Recurrence strengthens existing memory instead of rebuilding it.}}
\]

\[
\boxed{\textbf{Transient structure still retires lawfully.}}
\]
