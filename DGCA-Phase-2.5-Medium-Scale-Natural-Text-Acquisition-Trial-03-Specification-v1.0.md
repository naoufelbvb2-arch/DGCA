# DGCA Phase 2.5 — Medium-Scale Natural-Text Acquisition Trial 03 Specification v1.0

## Post-Encoder-v2 + Post-Law-3-Abolition Medium-Scale Empirical Acquisition Baseline

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.5 — Empirical Validation  
**Trial:** Medium-Scale Natural-Text Acquisition — Trial 03  
**Version:** 1.0  
**Status:** **PROTOCOL — CANDIDATE FOR FREEZE**  
**Architecture:** **POST-LAW-3-ABOLITION BASELINE**  
**Canonical Post-Abolition Baseline Signature:** `915119d40643cb97`  
**English Encoder:** v2 — IMPLEMENTED / VERIFIED / FROZEN  
**Law 3:** **ABOLISHED / RESERVED**  
**Architecture Changes During Trial:** **0**  
**Primary Question:** **Does repaired DGCA now accumulate usable knowledge from natural text?**

---

# 1. Executive Purpose

Trial 03 is the first medium-scale natural-text acquisition experiment executed after both major Phase-2.5 repairs:

1. **English Encoder v2** — repaired and frozen;
2. **Law 3 abolition** — passive decay, low-weight pruning, and global forgetting removed.

The historical Real-Data Trial 01 established that DGCA could process natural text but failed to accumulate durable usable knowledge.

Trial 02 subsequently demonstrated that post-abolition persistent memory now follows:

\[
\boxed{
Create
\rightarrow
Persist
\rightarrow
LongGap
\rightarrow
Reinforce
}
\]

The unresolved question is now:

\[
\boxed{
\textbf{Does persistent knowledge actually accumulate, remain available, and become usable at medium scale?}
}
\]

This trial must distinguish:

\[
\boxed{
Representation
}
\]

from:

\[
\boxed{
Acquisition
}
\]

from:

\[
\boxed{
Retention
}
\]

from:

\[
\boxed{
Retrieval
}
\]

from:

\[
\boxed{
Expression
}
\]

and from:

\[
\boxed{
GraphGrowth
}
\]

No single metric may substitute for the full causal decomposition.

---

# 2. Core Scientific Chain

Trial 03 evaluates the following end-to-end path:

\[
\boxed{
NaturalText
\rightarrow
EncoderRepresentation
\rightarrow
PersistentKnowledgeFormation
\rightarrow
Reinforcement
\rightarrow
Retention
\rightarrow
Retrieval
\rightarrow
Expression
}
\]

Each transition must be measured independently.

A failure in one stage must not be attributed to another without direct evidence.

---

# 3. Primary Scientific Questions

## T03-Q01 — Acquisition

Do valid Encoder-v2 outputs create persistent graph knowledge at medium scale?

\[
\boxed{
NaturalText
\rightarrow
PersistentKnowledge
}
\]

---

## T03-Q02 — Accumulation

Does the amount of persistent stored knowledge increase cumulatively across checkpoints?

\[
\boxed{
StoredKnowledge(M5K)
>
StoredKnowledge(M100)
}
\]

---

## T03-Q03 — Retention

Does knowledge learned early remain present after thousands of later articles?

\[
\boxed{
EarlyKnowledge
\rightarrow
StillStoredLater
}
\]

---

## T03-Q04 — Reinforcement

When a relation recurs in an independent later article, does DGCA reinforce the existing Edge rather than create a fresh lifecycle?

\[
\boxed{
ExistingEdge
\rightarrow
Reinforced
}
\]

---

## T03-Q05 — Retrieval

Can stored knowledge be causally retrieved by the existing cognition/retrieval path?

\[
\boxed{
Stored
\rightarrow
Retrievable
}
\]

---

## T03-Q06 — Expression

Can retrieved knowledge be expressed through the existing generative loop?

\[
\boxed{
Retrieved
\rightarrow
Expressible
}
\]

---

## T03-Q07 — Graph Growth

After removal of passive pruning, how does graph size scale over 5,000 natural-text articles?

\[
\boxed{
GrowthRate_N,\ GrowthRate_E,\ MemoryGrowth
}
\]

must be measured rather than assumed.

---

## T03-Q08 — Held-Out Safety

Does increased persistence cause unsupported knowledge claims or leakage into held-out probes?

\[
\boxed{
Persistence
\not\Rightarrow
UnsupportedRecallExplosion
}
\]

---

# 4. Trial Scope

The main training run is fixed at:

\[
\boxed{
5{,}000\ Train\ Articles
}
\]

Checkpoints:

\[
\boxed{
M0
\rightarrow
M100
\rightarrow
M500
\rightarrow
M1K
\rightarrow
M2.5K
\rightarrow
M5K
}
\]

Exact checkpoint sizes:

```text
M0      = 0 Train articles
M100    = 100 Train articles
M500    = 500 Train articles
M1K     = 1,000 Train articles
M2.5K   = 2,500 Train articles
M5K     = 5,000 Train articles
```

The run is cumulative.

Each checkpoint continues from the previous checkpoint.

---

# 5. Dataset — Frozen for Comparability

Use the same dataset lineage as Real-Data Trial 01:

```text
Dataset:
wikimedia/wikipedia

Configuration:
20231101.simple

Language:
Simple English Wikipedia

Frozen Dataset SHA256:
31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0
```

Historical frozen dataset accounting:

```text
Total Rows: 241,787
Train:      217,503
HeldOut:     24,284
```

Fields:

```text
id
url
title
text
```

No:

- web augmentation;
- LLM preprocessing;
- semantic paraphrase generation for training;
- image data;
- audio;
- tables;
- infobox augmentation;
- external knowledge sources.

Mechanical preprocessing only.

---

# 6. Frozen Split Rule

Use the exact RDT01 split rule:

```text
SHA256("RDT01-SPLIT-v1\0" || ArticleID)
```

Interpret the first 8 bytes as an unsigned integer.

HeldOut iff:

\[
value \bmod 10 = 0
\]

Otherwise:

```text
Train
```

Trial 03 must not redefine the split.

---

# 7. Frozen Train Order

Use the exact RDT01 deterministic order:

```text
SHA256("RDT01-ORDER-v1\0" || ArticleID)
```

Sort ascending.

Trial 03 consumes the first:

\[
5,000
\]

articles from the frozen Train ordering.

This preserves direct comparability with the earlier real-data baseline.

---

# 8. Episode Semantics

One Wikipedia article remains:

\[
\boxed{
OneRootExternalEpisode
}
\]

Multiple segments from the same article do not count as independent external evidence sources.

Retry:

\[
\boxed{
Retry \neq NewExperience
}
\]

The existing lawful episode/source authority remains unchanged.

---

# 9. Preflight Run

Before Main:

\[
\boxed{
50\ deterministic\ Train\ Articles
}
\]

Purpose:

- ingestion integrity;
- telemetry verification;
- checkpoint save/restore;
- read-only evaluation isolation;
- memory accounting;
- transient cleanup;
- no hidden Law-3 behavior.

The preflight is disposable.

After successful preflight:

\[
\boxed{
DiscardPreflight
}
\]

then return to clean:

\[
M0
\]

Preflight data must not contribute to Main learning.

---

# 10. Frozen Architecture Constraint

During Trial 03:

```text
ArchitectureChanges = 0
EncoderChanges = 0
Law1Changes = 0
Law2Changes = 0
Law5Changes = 0
Law6Changes = 0
Law8Changes = 0
Law11Changes = 0
Law13Changes = 0
Law14Changes = 0
GraphLifecycleChanges = 0
TransientLifecycleChanges = 0
NewParameters = 0
NewCognitivePrimitives = 0
NewNormativeLaws = 0
```

Poor results do not authorize repair during the run.

---

# 11. Encoder Accounting

For every article and checkpoint record:

```text
ArticlesProcessed
SentencesSeen
COMPLETE
SAFE_PARTIAL
UNSUPPORTED
EncoderErrors
GraphAddressableSymbols
GraphAddressableRelations
```

Unsupported input must fail closed.

No silent fallback learning is allowed.

---

# 12. Persistent Acquisition Accounting

For each article and cumulatively record:

```text
PersistentNodesCreated
PersistentNodesReused
PersistentEdgesCreated
PersistentEdgesReused
PersistentEdgesReinforced
PersistentRelationsMaterialized
PersistentRelationCreationFailures
```

Primary acquisition metric:

\[
PersistentKnowledgeYield
=
\frac{
PersistentRelationsMaterialized
}{
GraphAddressableRelationsEmitted
}
\]

where the denominator is defined only by the frozen Encoder-to-Graph contract.

---

# 13. Lifecycle Accounting

At every checkpoint report separately:

\[
\boxed{
CreatedEver
}
\]

\[
\boxed{
AliveNow
}
\]

for both Nodes and Edges.

Required:

```text
NodesEverCreated
NodesAlive
EdgesEverCreated
EdgesAlive
EdgesReinforced
EdgesRecreatedAfterAbsence
```

Because Law 3 is abolished, any recreation of an ordinary persistent relation due solely to inactivity is a blocker.

---

# 14. Persistent vs Transient Accounting

Do not mix transient operational structure with persistent learned memory.

At every checkpoint record:

```text
PersistentNodesAlive
TransientNodesAlive
PersistentEdgesAlive
TransientEdgesAlive
TransientInstancesCreated
TransientInstancesRetired
TransientLeakageAtQuiescence
```

At lawful quiescence, transient objects must satisfy their existing explicit lifecycle contract.

---

# 15. Node Reuse

Measure whether recurring concepts reuse existing graph identity.

Required metrics:

\[
NodeReuseRate
=
\frac{
ExistingPersistentNodeReuses
}{
PersistentNodeMaterializationOpportunities
}
\]

Also record:

```text
DuplicateStructuralIdentityCount
DuplicateConceptIdentityCount
```

No new deduplication policy may be added during the trial.

---

# 16. Edge Reinforcement

For every recurring persistent relation that can be mapped deterministically:

record:

```text
RelationID
FirstArticleID
FirstExposureTick
FirstEdgeID
SecondArticleID
SecondExposureTick
InterArticleGap
AliveBeforeRecurrence
SameEdgeIdentity
WeightBefore
WeightAfter
ReinforcementCountBefore
ReinforcementCountAfter
ContextCountBefore
ContextCountAfter
Result:
    REINFORCED
    RECREATED
    UNRESOLVED
```

The relation must recur in an **independent article** to count toward independent-evidence reinforcement.

---

# 17. Reinforcement Bank

Before Main execution, freeze a deterministic bank of recurring relations present in at least two independent Train articles among the first 5,000.

The bank must be discovered from dataset text using non-learning preprocessing and frozen before the Main graph run.

It must not be selected based on runtime success.

Target size:

\[
\boxed{
20\text{–}50\ auditable\ recurring\ relations
}
\]

If fewer can be frozen safely under exact relation mapping, report the smaller count rather than loosening criteria.

---

# 18. Law-5 Consolidation Observation

Trial 03 does not require a target lock rate.

It observes natural consolidation.

For every Edge reaching Law-5 established state record:

```text
EdgeID
RelationID
FirstArticle
LockArticle
ExposureCountAtLock
IndependentArticleCountAtLock
WeightAtLock
ContextCountAtLock
ArticlesBetweenFirstExposureAndLock
```

Report:

```text
EdgesReachingLaw5Lock
LockRateAmongRecurringAuditableRelations
MedianIndependentExposuresToLock
```

No Law-5 thresholds may be changed.

---

# 19. Law-13 Observation

Do not inject synthetic contradictions into Main.

Observe naturally occurring lawful Law-13 activity.

Record:

```text
Law13Invocations
ValidatedFailureEvents
EdgesCorrected
LockedEdgesUnlocked
TotalNegativeWeightDelta
SpuriousLaw13Invocations
```

Required:

\[
NoValidatedFailure
\Rightarrow
NoLaw13NegativeMutation
\]

---

# 20. Frozen Evaluation Architecture

All checkpoint evaluation must execute on:

\[
\boxed{
ReadOnlyClone(Checkpoint)
}
\]

Evaluation must not:

- reinforce;
- create new evidence;
- create persistent learning state;
- alter contexts;
- alter locks;
- mutate graph structure;
- contaminate later checkpoints.

After evaluation:

\[
TrainingState
\]

must remain bit-identical to pre-evaluation checkpoint state.

---

# 21. Evaluation Bank Overview

Freeze the complete evaluation bank before Main execution.

The bank consists of:

1. **Bank A — Direct Acquisition**
2. **Bank B — Early Retention Anchors**
3. **Bank C — Independent Recurrence/Reinforcement**
4. **Bank D — HeldOut**
5. **Bank E — Free Generation**

Gold/reference data must be frozen independently of DGCA runtime outputs.

No LLM-generated post-hoc gold.

---

# 22. Bank A — Direct Acquisition

Freeze:

\[
\boxed{
100\ target\ relations
}
\]

distributed across exposure windows:

```text
20 from Articles 1–100
20 from Articles 101–500
20 from Articles 501–1,000
20 from Articles 1,001–2,500
20 from Articles 2,501–5,000
```

Each target must be:

- explicitly supported by source text;
- representable by frozen Encoder v2;
- auditable in persistent graph structure.

At each relevant checkpoint score independently:

```text
STORED
RETRIEVABLE
EXPRESSIBLE
```

---

# 23. Stored / Retrievable / Expressible Separation

These are distinct outcomes.

## STORED

The expected persistent relation is present in graph state.

## RETRIEVABLE

The existing cognition/retrieval path can recover the stored relation from the evaluation cue.

## EXPRESSIBLE

The existing generative loop can express the retrieved relation adequately.

The final report must never collapse:

\[
Stored
\]

and:

\[
Retrieved
\]

and:

\[
Expressed
\]

into one accuracy number.

---

# 24. Bank B — Early Retention Anchors

Freeze:

\[
\boxed{
30\ early\ relations
}
\]

from the first 100 Train articles.

Evaluate the same 30 relations at:

\[
M100
\]

\[
M500
\]

\[
M1K
\]

\[
M2.5K
\]

\[
M5K
\]

Record:

```text
StoredRetention
RetrievableRetention
ExpressibleRetention
SameEdgeIdentity
WeightDriftWithoutEvidence
```

Primary retention metric:

\[
StoredRetention(M_k)
=
\frac{
EarlyRelationsStillStoredAtM_k
}{
EarlyRelationsStoredAtM100
}
\]

---

# 25. Bank C — Recurrence/Reinforcement

Use the frozen reinforcement bank.

At each recurrence event, inspect immediately before the later independent article.

Score:

```text
ALIVE_BEFORE_RECURRENCE
REINFORCED
RECREATED
UNRESOLVED
```

Primary recurrence metric:

\[
ReinforcementRate
=
\frac{
Reinforced
}{
Reinforced+Recreated
}
\]

Unresolved cases are excluded from the denominator and reported separately.

---

# 26. Bank D — HeldOut Control

Freeze:

\[
\boxed{
100\ HeldOut\ probes
}
\]

from the frozen HeldOut split.

HeldOut articles must never be used for learning.

For each probe score:

```text
Stored
Retrieved
ExpressedClaim
AppropriateUncertainty
UnsupportedClaim
```

Primary safety questions:

\[
HeldOutStored \stackrel{?}{=} 0
\]

unless equivalent knowledge was lawfully acquired from Train through another source article.

The report must distinguish:

```text
TRAIN-SUPPORTED GENERALIZATION
```

from:

```text
HELDOUT LEAKAGE
```

where possible.

---

# 27. Bank E — Free Generation

Freeze:

\[
\boxed{
20\ natural\ prompts
}
\]

covering learned knowledge from the 5K stream.

Examples may include:

```text
What is X?
What does X have?
Where is X?
What does X do?
```

Free generation is diagnostic.

It is **not** the primary acquisition verdict.

Report:

```text
GroundedContentPresent
PromptEchoOnly
UnsupportedClaim
UsefulExpression
```

---

# 28. Checkpoint Evaluation Schedule

Evaluate at:

```text
M0
M100
M500
M1K
M2.5K
M5K
```

Not every Bank-A relation is expected to be available before its source article has been ingested.

Each target must therefore include:

```text
FirstEligibleCheckpoint
```

and only be scored for acquisition after exposure eligibility.

---

# 29. Graph Growth Metrics

At every checkpoint record:

```text
ArticlesProcessed
SentencesProcessed
WordsProcessed

NodesEverCreated
NodesAlive
PersistentNodesAlive
TransientNodesAlive

EdgesEverCreated
EdgesAlive
PersistentEdgesAlive
TransientEdgesAlive

EdgesCreatedSincePreviousCheckpoint
EdgesReinforcedSincePreviousCheckpoint

NodeReuseCount
EdgeReuseCount

AssembliesAlive

GraphResidentBytes
CheckpointBytes
PeakRAM

WallTime
ArticlesPerSecond
SentencesPerSecond
WordsPerSecond
```

---

# 30. Growth Rates

Compute checkpoint-interval growth:

\[
GrowthRate_N
=
\frac{
\Delta PersistentNodesAlive
}{
\Delta Articles
}
\]

\[
GrowthRate_E
=
\frac{
\Delta PersistentEdgesAlive
}{
\Delta Articles
}
\]

and:

\[
ReinforcementToCreationRatio
=
\frac{
PersistentEdgesReinforced
}{
PersistentEdgesCreated
}
\]

Report trajectories.

Do not impose a performance threshold in advance.

---

# 31. Memory Efficiency

Record:

\[
BytesPerPersistentNode
\]

\[
BytesPerPersistentEdge
\]

\[
BytesPerArticle
\]

\[
CheckpointBytesPerArticle
\]

where measurable without altering cognition.

These are empirical resource metrics only.

No complexity claim beyond the tested regime is allowed.

---

# 32. Graph-Growth Interpretation

Possible empirical patterns include:

### Pattern A — Controlled Accumulation

\[
Knowledge\uparrow
\]

while reuse/reinforcement also rises.

### Pattern B — Linear Persistent Growth

Graph grows roughly proportionally to new information.

### Pattern C — Accelerating Duplication

\[
GrowthRate\uparrow
\]

with high duplicate identity counts.

### Pattern D — Low Growth Because Acquisition Fails

Small graph is not automatically good.

The final report must distinguish these cases.

---

# 33. No Automatic "Unbounded Growth" Verdict

The label:

```text
UNBOUNDED_GRAPH_GROWTH_RISK
```

may be used only if measured growth behavior shows a concrete problematic trend within the 5K regime.

The absence of pruning alone is not evidence of unbounded growth.

---

# 34. Acquisition Verdict Logic

The label:

\[
\boxed{
NATURAL\_TEXT\_ACQUISITION\_DEMONSTRATED
}
\]

requires evidence that all of the following occur:

1. persistent relations are formed in non-trivial quantity;
2. stored knowledge increases across checkpoints;
3. early stored knowledge remains retained;
4. independent recurrence reinforces existing memory;
5. retrieval rises above M0 for exposed targets;
6. results are not explained by HeldOut leakage;
7. graph integrity remains valid.

No arbitrary percentage threshold is imposed.

The evidence pattern, not a single score, controls the verdict.

---

# 35. Alternative Bottleneck Verdicts

If Trial 03 does not support full acquisition demonstration, use the most precise evidence-backed classification.

Allowed labels:

```text
NATURAL_TEXT_ACQUISITION_DEMONSTRATED

ACQUISITION_FORMATION_FAILURE

ACQUISITION_WORKS_RETRIEVAL_FAILS

RETRIEVAL_WORKS_EXPRESSION_FAILS

RETENTION_FAILURE

REINFORCEMENT_FAILURE

DUPLICATE_IDENTITY_GROWTH

UNBOUNDED_GRAPH_GROWTH_RISK

HELDOUT_LEAKAGE_OR_UNSUPPORTED_RECALL

MIXED_OUTCOME
```

Multiple compatible labels may be used.

---

# 36. Comparison With RDT01

Trial 03 must include a dedicated historical comparison section.

At minimum compare:

```text
Encoder:
RDT01 old encoder
vs
Trial03 English Encoder v2

Forgetting:
RDT01 Law 3 active
vs
Trial03 Law 3 abolished

Graph:
RDT01 final tiny graph
vs
Trial03 M100/M500/M1K/M2.5K/M5K growth

Retention:
RDT01 early knowledge collapse
vs
Trial03 early anchor retention

Recurrence:
RDT01 recreation/forgetting regime
vs
Trial03 reinforcement regime

Stored/Retrieved/Expressed:
RDT01
vs
Trial03
```

Do not claim causal attribution beyond the authorized combined repair:

\[
EncoderV2 + Law3Abolition
\]

unless the metric itself isolates the cause.

---

# 37. Historical RDT01 Reference Metrics

The report may use the following prior verified reference values:

```text
RDT01 Full Main:
217,503 Train articles
4,577,840 segments
39,441,064 words

MFULL:
22 nodes
44 edges
0 assemblies

Persistent knowledge acquisition:
effectively failed

Natural-text retention:
failed

Free generation:
largely prompt-anchor echo

HeldOut:
100/100 uncertainty
```

These values are historical comparison points only.

Trial 03 is medium-scale and must not present direct throughput ratios as equivalent-scale comparisons without qualification.

---

# 38. Preflight Integrity Gates

Before Main:

### T03-PG01 — Dataset Hash

Exact dataset hash matches frozen RDT01 hash.

### T03-PG02 — Split Integrity

Same Train/HeldOut split reproduced.

### T03-PG03 — Order Integrity

Same deterministic Train order reproduced.

### T03-PG04 — Baseline Signature

Post-abolition signature matches:

```text
915119d40643cb97
```

### T03-PG05 — Encoder Frozen

English Encoder v2 unchanged.

### T03-PG06 — Evaluation Isolation

Read-only clone proven non-mutating.

### T03-PG07 — Checkpoint Restore

Checkpoint save/restore bit-exact.

### T03-PG08 — Transient Cleanup

No persistent leakage.

### T03-PG09 — Hidden Forgetting

No passive forgetting mechanism detected.

### T03-PG10 — Telemetry Transparency

Instrumentation does not alter cognition.

Required:

\[
\boxed{
T03\text{-}PG01..PG10=10/10\ PASS
}
\]

before Main.

---

# 39. Trial Invariants

### T03-INV-001 — Frozen Architecture

No architecture change during Trial 03.

### T03-INV-002 — Frozen Encoder

English Encoder v2 unchanged.

### T03-INV-003 — Law 3 Remains Abolished

No passive forgetting path may reappear.

### T03-INV-004 — Same Dataset Lineage

Use frozen Simple English Wikipedia dataset.

### T03-INV-005 — Same Split

Use exact RDT01 split rule.

### T03-INV-006 — Same Order

Use exact RDT01 Train order.

### T03-INV-007 — One Article = One RootExternalEpisode

Article segmentation does not create independent evidence sources.

### T03-INV-008 — Retry Is Not Experience

Retries do not create independent evidence.

### T03-INV-009 — Unsupported Fails Closed

Unsupported Encoder input does not silently learn.

### T03-INV-010 — Persistent/Transient Separation

Transient state is not counted as acquired persistent knowledge.

### T03-INV-011 — Evaluation Read-Only

Checkpoint evaluation cannot mutate training state.

### T03-INV-012 — Stored/Retrieved/Expressed Separation

No collapse into one score.

### T03-INV-013 — Recurrence Requires Independent Article

Independent reinforcement bank uses distinct RootExternalEpisodes.

### T03-INV-014 — No Performance-Driven Repair

Poor results remain evidence.

### T03-INV-015 — No Threshold Added Post Hoc

No empirical threshold is invented after results.

### T03-INV-016 — Raw Lifecycle Evidence Preserved

Per-target acquisition/reinforcement traces are retained.

### T03-INV-017 — No Large-Corpus Expansion

Main stops at 5,000 Train articles.

### T03-INV-018 — HeldOut Never Learns

HeldOut probes remain evaluation-only.

### T03-INV-019 — Canonical Baseline Conserved

Trial instrumentation/evaluation does not alter baseline architecture.

### T03-INV-020 — Protocol Verdict Separate From Capability Verdict

A valid protocol may demonstrate failure.

---

# 40. Main Verification Gates

### T03-G01 — Acquisition Telemetry Complete

Persistent formation/reuse metrics available at all checkpoints.

### T03-G02 — Knowledge Growth Curve Complete

M0 through M5K graph growth fully recorded.

### T03-G03 — Early Retention Measured

30 anchors evaluated at all eligible checkpoints.

### T03-G04 — Independent Reinforcement Measured

Recurring relation bank evaluated with same-Edge evidence.

### T03-G05 — Retrieval Evaluated

Stored target retrieval measured separately.

### T03-G06 — Expression Evaluated

Expression measured separately from storage/retrieval.

### T03-G07 — HeldOut Safety Evaluated

HeldOut probes remain isolated.

### T03-G08 — Graph Growth Measured

Node/Edge/resource trajectories complete.

### T03-G09 — Transient Leakage Zero or Fully Accounted

No silent persistent/transient contamination.

### T03-G10 — No Hidden Forgetting

No persistent loss caused solely by inactivity.

### T03-G11 — Full Regression Green

Repository integrity remains valid.

### T03-G12 — Final Causal Classification Complete

Final bottleneck verdict is evidence-backed.

Required protocol condition:

\[
\boxed{
T03\text{-}G01..G12=12/12\ PASS
}
\]

This means the experiment is valid.

It does not imply acquisition success.

---

# 41. Stop Conditions

Stop Main only for:

- dataset hash mismatch;
- split/order mismatch;
- canonical baseline mismatch before Main;
- graph corruption;
- checkpoint corruption;
- evaluation contamination;
- hidden passive forgetting;
- persistent knowledge deleted by transient cleanup;
- instrumentation changes cognition;
- unrecoverable resource failure;
- continuing requires architecture change.

Do not stop because:

- acquisition is weak;
- retrieval is weak;
- expression is weak;
- graph grows rapidly;
- Law 5 never locks;
- Assemblies remain zero;
- HeldOut performance is poor.

Those are scientific outcomes.

---

# 42. Performance Policy

Measure throughput and memory.

Do not optimize during Main.

No code-performance modification is authorized by Trial 03.

If resource use becomes a true blocker, stop and report exact resource state.

Do not introduce pruning or compression mid-trial.

---

# 43. Required Machine-Readable Artifacts

Produce at minimum:

```text
DGCA-MEDIUM-SCALE-NATURAL-TEXT-ACQUISITION-TRIAL-03-REPORT.md

t03_dataset_verification.json
t03_split_order_manifest.json
t03_preflight_report.json

t03_main_article_metrics.jsonl
t03_checkpoint_metrics.json
t03_graph_growth.json
t03_memory_accounting.json

t03_acquisition_bank.json
t03_retention_bank.json
t03_reinforcement_bank.json
t03_heldout_bank.json
t03_generation_bank.json

t03_acquisition_results.jsonl
t03_retention_results.jsonl
t03_reinforcement_results.jsonl
t03_heldout_results.jsonl
t03_generation_results.jsonl

t03_law5_observation.json
t03_law13_observation.json
t03_transient_lifecycle.json

t03_invariants.json
t03_preflight_gates.json
t03_release_gates.json
t03_signature_verification.json
t03_failures.jsonl
```

Additional raw telemetry artifacts may be added.

Raw data is authoritative.

---

# 44. Required Checkpoint Table

The final report must contain a table equivalent to:

| Metric | M0 | M100 | M500 | M1K | M2.5K | M5K |
|---|---:|---:|---:|---:|---:|---:|
| Articles | 0 | 100 | 500 | 1000 | 2500 | 5000 |
| COMPLETE sentences | | | | | | |
| Persistent Nodes Alive | | | | | | |
| Persistent Edges Alive | | | | | | |
| Nodes Ever Created | | | | | | |
| Edges Ever Created | | | | | | |
| Edges Reinforced | | | | | | |
| Node Reuse Rate | | | | | | |
| Edge Reinforcement/Creation Ratio | | | | | | |
| Assemblies | | | | | | |
| Graph Bytes | | | | | | |
| Checkpoint Bytes | | | | | | |
| Peak RAM | | | | | | |
| Acquisition Stored | | | | | | |
| Retrieval | | | | | | |
| Expression | | | | | | |
| Early Retention | | | | | | |
| HeldOut Unsupported Claims | | | | | | |

---

# 45. Required Acquisition Table

For Bank A:

```text
TargetID
SourceArticleID
SourceSentence
FirstEligibleCheckpoint
ExpectedRelation
StoredAtCheckpoint
RetrievedAtCheckpoint
ExpressibleAtCheckpoint
FailureStage
```

FailureStage values:

```text
NONE
ENCODER_UNSUPPORTED
NOT_MATERIALIZED
STORED_NOT_RETRIEVED
RETRIEVED_NOT_EXPRESSED
UNRESOLVED
```

---

# 46. Required Retention Table

For Bank B:

```text
TargetID
StoredAtM100
StoredAtM500
StoredAtM1K
StoredAtM2.5K
StoredAtM5K

SameEdgeIdentityAtM5K
WeightAtM100
WeightAtM5K
LawfulUpdatesBetween
RetentionOutcome
```

---

# 47. Required Reinforcement Table

For Bank C:

```text
RelationID
FirstArticle
SecondArticle
GapArticles
GapTicks
AliveBeforeRecurrence
SameEdgeIdentity
WeightBefore
WeightAfter
NBefore
NAfter
ContextsBefore
ContextsAfter
Law5Locked
Outcome
```

---

# 48. Required HeldOut Table

For Bank D:

```text
ProbeID
HeldOutArticleID
Question/Cue
EquivalentTrainEvidencePresent
Stored
Retrieved
ExpressedClaim
UnsupportedClaim
AppropriateUncertainty
Classification
```

---

# 49. Required Generation Table

For Bank E:

```text
PromptID
Prompt
RelevantStoredKnowledgePresent
RelevantKnowledgeRetrieved
RenderedOutput
GroundedContentPresent
PromptEchoOnly
UnsupportedClaim
UsefulExpression
```

---

# 50. Required Final Scientific Answers

The final report must explicitly answer:

1. Did valid Encoder-v2 natural-text relations materialize into persistent graph knowledge?
2. How many persistent Nodes were alive at each checkpoint?
3. How many persistent Edges were alive at each checkpoint?
4. Did stored knowledge increase from M100 to M5K?
5. Did early M100 knowledge remain stored through M5K?
6. Did recurrence reinforce existing Edge identities?
7. Were any ordinary persistent relations recreated due to inactivity?
8. What was the node reuse rate?
9. What was the duplicate persistent identity count?
10. Did Law 5 lock any relations naturally?
11. Did Law 13 produce lawful negative corrections?
12. Did transient cleanup remain isolated?
13. What was the growth rate per article for Nodes?
14. What was the growth rate per article for Edges?
15. Did growth accelerate, remain stable, or decline with reuse?
16. What was graph/checkpoint memory at M5K?
17. How many Bank-A targets were STORED at M5K?
18. How many stored targets were RETRIEVABLE?
19. How many retrieved targets were EXPRESSIBLE?
20. What was early-anchor stored retention at M5K?
21. Did HeldOut probes remain free of leakage/unsupported recall?
22. Did free generation improve beyond prompt-anchor echo?
23. Is natural-text acquisition now empirically demonstrated?
24. If not, what is the next dominant bottleneck?
25. Is medium-scale persistence stable without Law 3?
26. Is graph growth currently acceptable in the tested 5K regime?
27. Is DGCA ready for a larger acquisition trial?
28. Is DGCA ready for full-corpus retraining?

The answer to #28 must remain:

```text
NO
```

unless a future separately authorized protocol explicitly changes that decision.

---

# 51. Final Scientific Verdict

The report must separate:

## Protocol Integrity

```text
PROTOCOL_PASS
PROTOCOL_FAIL
BLOCKED
```

from:

## Scientific Outcome

Allowed evidence-backed labels:

```text
NATURAL_TEXT_ACQUISITION_DEMONSTRATED
ACQUISITION_FORMATION_FAILURE
ACQUISITION_WORKS_RETRIEVAL_FAILS
RETRIEVAL_WORKS_EXPRESSION_FAILS
RETENTION_FAILURE
REINFORCEMENT_FAILURE
DUPLICATE_IDENTITY_GROWTH
UNBOUNDED_GRAPH_GROWTH_RISK
HELDOUT_LEAKAGE_OR_UNSUPPORTED_RECALL
MIXED_OUTCOME
```

---

# 52. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.5 — MEDIUM-SCALE NATURAL-TEXT ACQUISITION TRIAL 03

PROTOCOL:
DGCA-Phase-2.5-Medium-Scale-Natural-Text-Acquisition-Trial-03-v1.0

POST-ABOLITION BASELINE:
915119d40643cb97

LAW 3:
ABOLISHED / RESERVED

ARCHITECTURE CHANGES:
0

ENCODER CHANGES:
0

DATASET:
wikimedia/wikipedia — 20231101.simple

DATASET SHA256:
31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0

TRAIN ARTICLES:
5,000

CHECKPOINTS:
M0 / M100 / M500 / M1K / M2.5K / M5K

PREFLIGHT:
PASS / FAIL

DATASET HASH:
MATCH / MISMATCH

SPLIT:
MATCH / MISMATCH

ORDER:
MATCH / MISMATCH

ENCODER:

Sentences:
COMPLETE:
SAFE_PARTIAL:
UNSUPPORTED:

ACQUISITION:

Graph-Addressable Relations:
Persistent Relations Materialized:
Persistent Knowledge Yield:

M5K GRAPH:

Persistent Nodes Alive:
Persistent Edges Alive:
Nodes Ever Created:
Edges Ever Created:
Edges Reinforced:
Assemblies:

NODE REUSE:

Node Reuses:
Node Reuse Rate:
Duplicate Persistent Identity Count:

REINFORCEMENT:

Auditable Recurring Relations:
Reinforced:
Recreated:
Unresolved:
Reinforcement Rate:

LAW 5:

Edges Reaching Lock:
Median Independent Exposures To Lock:

LAW 13:

Validated Negative Events:
Edges Corrected:
Spurious Negative Mutations:

RETENTION:

Early Anchors:
Stored At M100:
Stored At M500:
Stored At M1K:
Stored At M2.5K:
Stored At M5K:
M5K Stored Retention Rate:

BANK A — DIRECT ACQUISITION:

Targets:
Stored At M5K:
Retrievable At M5K:
Expressible At M5K:

BANK D — HELDOUT:

Probes:
HeldOut Leakage:
Unsupported Claims:
Appropriate Uncertainty:

BANK E — FREE GENERATION:

Prompts:
Grounded Useful Outputs:
Prompt-Echo-Only:
Unsupported Claims:

GRAPH GROWTH:

Node Growth / Article:
Edge Growth / Article:
Reinforcement / Creation Ratio:
Graph Bytes At M5K:
Checkpoint Bytes At M5K:
Peak RAM:
Wall Time:
Articles / Second:
Words / Second:

TRANSIENT LIFECYCLE:

Transient Leakage:
Persistent Knowledge Lost By Cleanup:

HIDDEN PASSIVE FORGETTING:
0 / NONZERO

POST-ABOLITION SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / MISMATCH

TRIAL INVARIANTS:
T03-INV-001..020:
x/20

PREFLIGHT GATES:
T03-PG01..PG10:
x/10

MAIN VERIFICATION GATES:
T03-G01..G12:
x/12

FULL REGRESSION:
PASS / FAIL

PROTOCOL INTEGRITY:
PROTOCOL_PASS / PROTOCOL_FAIL / BLOCKED

SCIENTIFIC OUTCOME:
...

DOMINANT BOTTLENECK:
...

NATURAL-TEXT ACQUISITION DEMONSTRATED:
YES / NO

MEDIUM-SCALE PERSISTENCE STABLE:
YES / NO

GRAPH GROWTH ACCEPTABLE IN TESTED 5K REGIME:
YES / NO / INCONCLUSIVE

READY FOR LARGER ACQUISITION TRIAL:
YES / NO

READY FOR FULL-CORPUS RETRAINING:
NO
============================================================
```

---

# 53. Interpretation Discipline

The following statements are forbidden unless directly supported:

- "DGCA learns natural language" merely because graph size increases.
- "Acquisition failed" merely because expression is poor.
- "Retrieval failed" when the target was never stored.
- "Generation failed" when retrieval never succeeded.
- "Graph growth is unbounded" from a single M5K endpoint.
- "No pruning is safe at arbitrary scale" from this 5K trial.
- "HeldOut knowledge leaked" without checking equivalent Train evidence.
- "Law 5 failed" merely because no Edge locked.
- "Encoder failed" for a graph-side materialization defect.
- "Full-corpus readiness" from Trial 03 alone.
- "ARC/AGI reasoning improved" from knowledge-acquisition results.
- "World knowledge acquired broadly" from a 5K Simple Wikipedia subset.

---

# 54. Trial Success Principle

Trial 03 is successful as a protocol when it reveals the actual post-repair acquisition pipeline.

The desired scientific path is:

\[
\boxed{
Text
\rightarrow
PersistentKnowledge
\rightarrow
Accumulation
\rightarrow
Retention
\rightarrow
Reinforcement
\rightarrow
Retrieval
}
\]

Expression may remain a separate downstream bottleneck.

A strong result would demonstrate:

\[
\boxed{
StoredKnowledge(M5K)
>
StoredKnowledge(M100)
}
\]

while:

\[
\boxed{
EarlyRetention\ remains\ high
}
\]

and:

\[
\boxed{
IndependentRecurrence
\rightarrow
Reinforcement
}
\]

and:

\[
\boxed{
Retrieval(M5K)>Retrieval(M0)
}
\]

without held-out leakage or destructive graph instability.

---

# 55. Final Principle

RDT01 asked whether frozen Phase-II DGCA could learn from natural text and found that persistent acquisition failed.

Encoder v2 repaired representation.

Law-3 abolition repaired persistence.

Trial 02 verified persistence at small natural-text scale.

Trial 03 now asks the next causal question:

\[
\boxed{
\textbf{After representation and persistence are repaired, does knowledge actually accumulate and become usable?}
}
\]

No further architectural interpretation is authorized until this experiment answers that question.

