# DGCA Phase 2.6 — ATGF01
## Auditory Temporal Granularity Forensics 01
## Formal Forensic Specification v1.0

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Auditory Representation Diagnostics  
**Study ID:** `ATGF01` — Auditory Temporal Granularity Forensics 01  
**Document Type:** Formal Forensic Specification  
**Version:** 1.0  
**Status:** **FROZEN AFTER FREEZE REVIEW**

**Parent Trial:** `ATG01`  
**Parent ASUR01 Verdict:** `ASUR01_PREIMPLEMENTATION_REJECTED`  
**Parent ATG01 Commit:** `7e43974`  
**Parent F01 Commit:** `74f788e`  
**Parent ARSR01 Counterfactual Commit:** `c3bf4dc`  
**Parent ARSR01 Implementation Commit:** `a26deb5`  
**Historical Cognitive Signature:** `915119d40643cb97`

**Authorized Class:** `R-E AUDIO_REPRESENTATION_REVISIT — DIAGNOSTIC ONLY`

**Audio Encoder v2:** FROZEN DURING FORENSICS  
**English Encoder v2:** FROZEN  
**Grounding:** FROZEN  
**LESR / LDSR / IGSV:** FROZEN  
**Retrieval:** FROZEN  
**Graph Learning:** OFF  
**Persistent Graph Mutation:** `0`  
**New Grounding:** `0`  
**New Persistent Primitive:** `0`  
**New Persistent Field:** `0`  
**New Law:** `0`  
**Implementation Repair:** FORBIDDEN

---

# 1. Formal Scientific Question

ASUR01 established that event-level sequence utilization cannot operate because the majority of isolated spoken-word clips are represented as one acoustic event.

Observed parent condition:

\[
68/70
\]

Speech Commands recordings:

```text
num_events = 1
```

and for held-out queries:

\[
|U_Q|>0 = 0/20
\]

Therefore ATGF01 asks:

\[
\boxed{
\textbf{At what exact stage is discriminative intra-word temporal information lost?}
}
\]

---

# 2. Frozen Causal Chain

ATGF01 audits the following chain:

\[
RawAudio
\rightarrow
FrameFrontend
\rightarrow
FrameEvidence
\rightarrow
EventMembership
\rightarrow
EventAggregatePreCompression
\rightarrow
EventDescriptorCompression
\rightarrow
AudioTemporalIR
\rightarrow
GraphFacingRepresentation
\]

Allowed earliest-loss stages:

```text
FRONTEND_FRAME_REPRESENTATION
EVENT_AGGREGATION
EVENT_DESCRIPTOR_COMPRESSION
AUDIOTEMPORAL_IR
GRAPH_PERSISTENCE
MULTI_STAGE
NO_TEMPORAL_SIGNAL
INCONCLUSIVE
```

---

# 3. Primary Hypothesis

Primary hypothesis:

\[
\boxed{
\textbf{Useful intra-word temporal structure exists at frame level but is lost during event aggregation.}
}
\]

This hypothesis MUST NOT be assumed true.

ATGF01 must be capable of rejecting it.

---

# 4. Parent Data Freeze

Use only the exact frozen ATG01 Speech Commands assets.

No new audio.

Required probe families:

```text
40 grounded training recordings
20 held-out grounded-word recordings
10 OOD recordings
```

Any already-used preflight items may be inspected only for representation inventory and must not enter primary held-out efficacy counts.

No replacement files.

No new speakers.

---

# 5. Speaker Isolation

Held-out evaluation must preserve the original speaker isolation.

No same-speaker overlap between grounding and held-out.

No speaker embedding.

No speaker-specific normalization.

---

# 6. Read-Only Execution

ATGF01 execution mode:

```text
STRICT_READ_ONLY
```

Required:

```text
graph mutation = 0
Audio Encoder source changes = 0
retrieval source changes = 0
grounding changes = 0
new persistent state = 0
```

Diagnostic scripts and telemetry files only may be added.

---

# 7. Stage F0 — Raw Frame Inventory

For every audio item, record the exact existing frame stream before event aggregation.

Per frame:

- absolute frame index;
- timestamp;
- valid/low-energy status;
- active ERB channels;
- spectral peak identities;
- periodicity state;
- frame RMS/energy descriptor;
- novelty value;
- any existing transient auditory descriptors.

No new feature extractor is allowed.

---

# 8. Existing Frame Semantics Only

ATGF01 may inspect only quantities already produced by Audio Encoder v2.

Forbidden:

- MFCC;
- learned embeddings;
- mel spectrogram classifier;
- phoneme posterior;
- ASR logits;
- external DSP descriptors not already in Audio v2.

---

# 9. Stage F0 Representation

For diagnostic comparison, define the frame-evidence sequence:

\[
F_Q=(f_1,f_2,\dots,f_m)
\]

where each \(f_i\) is the set/vector of existing Audio v2 frame descriptors.

The exact canonical descriptor serialization must be frozen in the execution report.

---

# 10. Frame Similarity Primitive

For two frame evidence items \(f_i,f_j\), define only descriptor-overlap measures derivable from existing categorical/normalized evidence.

Primary frozen candidate:

\[
J(f_i,f_j)
=
\frac{|D_i\cap D_j|}{|D_i\cup D_j|}
\]

for canonical descriptor identity sets \(D_i,D_j\).

If both sets are empty:

```text
J = 1
```

only for structural equality accounting; low-energy/empty frames must be excluded from lexical similarity aggregation unless explicitly valid under Audio v2.

No learned metric.

---

# 11. Frame-to-Frame Temporal Change

For valid consecutive frames:

\[
\Delta_i
=
1-J(f_i,f_{i+1})
\]

Report per recording:

- mean \(\Delta\);
- median \(\Delta\);
- max \(\Delta\);
- count of large local changes;
- novelty-peak correspondence.

Large-change thresholds must NOT be tuned from labels.

Use distributional reporting rather than a decision threshold.

---

# 12. Fixed Temporal Partition Families

Construct three read-only diagnostic partitions over valid frame span:

```text
P2 = 2 equal-duration blocks
P4 = 4 equal-duration blocks
P8 = 8 equal-duration blocks
```

Block boundaries are deterministic functions of normalized time only.

The normalized interval is anchored from the center timestamp of the first valid frame to the center timestamp of the last valid frame.

Internal low-energy gaps are NOT removed or time-compressed. Frames retain their original temporal positions.

No adaptive boundary.

No label-dependent boundary.

No learned segmentation.

---

# 13. Block Construction

For partition \(P_k\), each block \(b_r\) aggregates only existing frame descriptors inside its fixed temporal interval.

For each descriptor identity \(d\), block support is:

\[
A_{r,d}
=
\frac{\#\{\text{valid frames in block }r\text{ containing }d\}}
{\#\{\text{valid frames in block }r\}}
\]

if block has valid frames.

No learned weighting.

---

# 14. Block Descriptor Presence

For categorical comparison, a descriptor may be reported with its exact support fraction \(A_{r,d}\).

Do NOT threshold support into binary presence for primary metrics.

Primary comparison must retain support fractions.

---

# 15. Block Similarity

For two blocks \(b_r,b'_r\), use weighted Jaccard:

\[
WJ(b,b')
=
\frac{\sum_d \min(A_d,A'_d)}
{\sum_d \max(A_d,A'_d)}
\]

If both blocks contain no valid descriptors, mark the pair:

```text
EMPTY_EMPTY
```

and exclude that block position from the lexical-similarity denominator.

If exactly one block is empty:

```text
WJ = 0
```

This prevents aligned silence/empty evidence from inflating lexical similarity.

---

# 16. Ordered Partition Similarity

For two recordings under the same \(P_k\), let:

\[
R_{valid}
=
\{r:\text{at least one of }b_r^Q,b_r^X\text{ contains valid descriptors}\}
\]

Then:

\[
Sim_{ord}^{(k)}(Q,X)
=
\frac1{|R_{valid}|}
\sum_{r\in R_{valid}}
WJ(b_r^Q,b_r^X)
\]

If:

\[
|R_{valid}|=0
\]

the comparison is `NONDISCRIMINATIVE`, not similarity 1.

This is a fixed normalized-time comparison.

It is diagnostic only.

It is NOT DTW.

---

# 17. Unordered Partition Similarity

Define unordered comparison as the average block-support representation collapsed across time:

\[
\bar A_d
=
\frac1{k}\sum_r A_{r,d}
\]

Then:

\[
Sim_{bag}^{(k)}(Q,X)
=
WJ(\bar A^Q,\bar A^X)
\]

This removes temporal order while preserving overall descriptor content.

---

# 18. Order Gain

Define:

\[
OrderGain^{(k)}(Q,X)
=
Sim_{ord}^{(k)}(Q,X)
-
Sim_{bag}^{(k)}(Q,X)
\]

Positive value means fixed temporal order provides extra matching structure beyond unordered content.

This is diagnostic only.

---

# 19. Reversal Control

For comparison recording \(X\), reverse block order:

\[
Rev(X)=(b_k,\dots,b_1)
\]

Compute:

\[
Sim_{rev}^{(k)}(Q,X)
\]

using the same ordered formula.

No graph change.

---

# 20. Deterministic Shuffle Control

For each \(k\), define one fixed non-identity permutation before looking at outcomes.

Frozen permutations:

```text
P2: [1,0]
P4: [2,0,3,1]
P8: [4,0,6,2,7,3,5,1]
```

Apply identically to all items.

For `P2`, the only non-identity permutation is the reversal itself. Therefore `P2-SHUFFLE` is explicitly marked `DEGENERATE_WITH_REVERSAL` and is NOT counted as an independent control.

For `P4` and `P8`, shuffle and reversal are distinct controls.

No random seed search.

No best-of-shuffles selection.

---

# 21. Temporal Order Evidence Condition

Order informativeness is evaluated at the **correct-vs-best-wrong concept margin**, not merely by increasing correct-concept similarity.

For control mode \(m\in\{ordered,bag,reversed,shuffled\}\):

\[
Margin_m^{(k)}(Q)
=
CorrectMean_m^{(k)}(Q)
-
BestWrongMean_m^{(k)}(Q)
\]

Define `TEMPORAL_ORDER_WIN` for `P4` and `P8` iff:

\[
Margin_{ordered}
>
Margin_{bag}
\]

\[
Margin_{ordered}
>
Margin_{reversed}
\]

\[
Margin_{ordered}
>
Margin_{shuffled}
\]

using only the frozen numeric tolerance for equality.

For `P2`, because shuffle is identical to reversal, require:

\[
Margin_{ordered}>Margin_{bag}
\]

and:

\[
Margin_{ordered}>Margin_{reversed}
\]

and record `P2-SHUFFLE = DEGENERATE_WITH_REVERSAL`.

A rise in correct similarity that is matched or exceeded by wrong-concept similarity is NOT temporal-order evidence.

This is diagnostic, not an implementation threshold.

---

# 22. Same-Concept Comparison Set

Each held-out grounded-word query is compared against the exact four grounding examples of its correct concept.

For concept \(c\):

\[
CorrectMean_k(Q)
=
\frac14\sum_{x\in Train(c)}Sim_k(Q,x)
\]

\[
CorrectMax_k(Q)
=
\max_{x\in Train(c)}Sim_k(Q,x)
\]

---

# 23. Wrong-Concept Comparison Set

For each wrong concept \(w\):

\[
WrongMean_k(Q,w)
=
\frac14\sum_{x\in Train(w)}Sim_k(Q,x)
\]

Define:

\[
BestWrongMean_k(Q)
=
\max_{w\neq c}WrongMean_k(Q,w)
\]

and:

\[
BestWrongMax_k(Q)
=
\max_{w\neq c,x\in Train(w)}Sim_k(Q,x)
\]

---

# 24. Correct Rank

Rank concepts by mean similarity:

\[
Rank_k(Q)
\]

Tie handling:

```text
exact numeric ties = AMBIGUOUS RANK
```

No lexical tie-breaker.

---

# 25. Stage Classification

For each held-out probe and representation stage:

### CORRECT_DOMINANT

\[
CorrectMean > BestWrongMean
\]

### CORRECT_COMPETITIVE

Correct concept is tied for best or rank <=3 but not strictly dominant.

### WRONG_DOMINANT

A wrong concept strictly exceeds correct concept and correct rank >3.

### NONDISCRIMINATIVE

Scores are all equal / structurally insufficient / no meaningful valid evidence.

---

# 26. Stages to Classify

Required stages:

```text
F0-UNORDERED-FRAME-SUMMARY
F2-ORDERED
F4-ORDERED
F8-ORDERED
F2-BAG
F4-BAG
F8-BAG
EA-PRECOMPRESSION
E-DESCRIPTOR-COMPRESSED
IR-CURRENT-AUDIOTEMPORAL-IR
G-GRAPH-FACING-ACOUSTIC-ONLY
```

`EA-PRECOMPRESSION` is a read-only forensic reconstruction using the **exact current event membership** but retaining support fractions of all existing internal frame descriptors before current event descriptor pruning/compression.

It is NOT a new production representation and MUST NOT be persisted.

---

# 27. Current Event Representation Reproduction

Reproduce exact Audio v2 event output for all parent items.

Required parent finding:

```text
68/70 Speech Commands items have num_events=1
```

If not reproduced:

```text
ATGF01_BLOCKED
```

---

# 28. Event Aggregation Telemetry

For every event record:

- start time;
- end time;
- duration;
- number of frames;
- onset reason;
- closure reason;
- novelty behavior;
- descriptor accumulation;
- descriptor pruning/compression;
- final descriptor set.

---

# 29. Event Closure Cause Taxonomy

Allowed closure causes must map to actual Audio v2 implementation semantics.

Examples only if code supports them:

```text
OFFSET_HYSTERESIS
MAX_EVENT_DURATION
LOW_ENERGY_TERMINATION
END_OF_STREAM
NOVELTY_BOUNDARY
OTHER_EXPLICIT
```

Do not invent causes.

---

# 30. Single-Event Analysis

For every single-event recording calculate:

- valid frame count;
- event duration;
- mean frame change;
- max frame change;
- number of novelty peaks;
- F2/F4/F8 internal block divergence;
- descriptors present early but absent late;
- descriptors present late but absent early.

---

# 31. Event Descriptor Compression Audit

For each current event, first reconstruct the read-only pre-compression support map:

\[
EA_e(d)
=
\frac{
\#\{\text{valid member frames of event }e\text{ containing }d\}
}{
\#\{\text{valid member frames of event }e\}
}
\]

using exact current event membership.

Then compare `EA-PRECOMPRESSION` against the actual final event descriptor set emitted by Audio v2.

For descriptor \(d\):

\[
Retention(d)
=
\mathbf{1}[d\in EventDescriptorSet]
\]

Report:

- pre-compression descriptors/support;
- retained descriptors;
- lost descriptors;
- descriptor-family retention;
- whether correct-vs-wrong representational margin is lost from `EA-PRECOMPRESSION` to `E-DESCRIPTOR-COMPRESSED`.

Do not attribute order loss to descriptor compression if the order was already eliminated by event membership/aggregation.

No semantic labels enter representation construction.

---

# 32. AudioTemporalIR Audit

Record exactly what current event representation exposes to AudioTemporalIR:

- event identity;
- event timing;
- descriptor list;
- sequence relation eligibility;
- transition count.

Determine whether intra-event frame order survives at all.

---

# 33. Graph-Facing Audit

Record exactly what auditory structures are presented to graph persistence.

No graph write.

Report:

- persistent node candidates;
- event relations;
- sequence relations;
- lost frame-order information;
- any retained timing provenance.

---

# 33A. Common Acoustic Evidence Projection

To compare stages without changing metrics mid-pipeline, each reconstructable stage MUST be projected into a canonical **acoustic-only descriptor-support map**:

\[
\Phi_s(X)=\{d\mapsto A_{s,d}\}
\]

using only descriptor identities already present at stage \(s\).

Rules:

- no lexical concept identity;
- no cross-modal text edge;
- no class label;
- no candidate degree/path count;
- no new feature synthesis.

Stage-specific construction:

### F0
Full-recording valid-frame descriptor support fractions.

### EA-PRECOMPRESSION
Use exact current event membership. For each current event, retain support fractions of **all existing frame descriptors** assigned to that event before current descriptor pruning. For primary single-event items this yields one event support map.

### E-DESCRIPTOR-COMPRESSED
Use only the actual final event descriptors emitted by current Audio v2.

### IR
Use only acoustic descriptor/timing identities actually exposed by current AudioTemporalIR.

### G
Use only graph-facing **acoustic-origin** identities/provenance. Exclude lexical/cross-modal concept identities and grounding labels from representational similarity.

Where a stage contains multiple current events, preserve current event order for reporting, but primary earliest-loss claims MUST be supported on the parent single-event regime and must not depend on inventing a new multi-event alignment algorithm.

Similarity between support maps uses the same weighted-Jaccard primitive as the block analysis.

---

# 33B. Aggregation-vs-Compression Separation

The following causal distinction is binding:

### Event Aggregation Loss
P2/P4/P8 show temporal specificity, but `EA-PRECOMPRESSION` loses it because current event membership collapses temporally distinct frame regions into a common event representation.

### Event Descriptor Compression Loss
`EA-PRECOMPRESSION` retains correct-concept specificity materially better than `E-DESCRIPTOR-COMPRESSED`, and the loss is attributable to current descriptor selection/pruning.

Without `EA-PRECOMPRESSION`, the study MUST NOT claim to distinguish these two stages.

---

# 34. OOD Role

OOD recordings are used only to measure representation genericity and accidental temporal similarity.

OOD labels do not enter representation construction.

No OOD-specific threshold.

---

# 35. Raw Frame Summary Baseline

Define F0 unordered summary by averaging frame descriptor support over the full valid recording.

This baseline asks:

\[
\text{Does temporal partitioning outperform the same descriptor content without order?}
\]

---

# 36. Temporal Partition Efficacy Metrics

For each of P2/P4/P8 report:

- held-out correct dominant /20;
- correct competitive /20;
- wrong dominant /20;
- nondiscriminative /20;
- median correct rank;
- mean correct rank.

Do NOT select a partition solely on top-1 accuracy.

---

# 37. Partition Selection Is Forbidden

ATGF01 is forensic.

It MUST NOT output:

```text
P4 is the new production segmentation
```

or similar.

P2/P4/P8 are diagnostic probes only.

---

# 38. Evidence of Frame-Level Temporal Signal

Frame-level temporal signal is considered demonstrated only if at least TWO of `P2/P4/P8` satisfy ALL:

1. median correct rank is better than `E-DESCRIPTOR-COMPRESSED`;
2. at least `6/20` held-out probes improve correct rank relative to `E-DESCRIPTOR-COMPRESSED`;
3. at least `6/20` held-out probes satisfy the frozen `TEMPORAL_ORDER_WIN` margin criterion;
4. median correct-vs-best-wrong margin is greater in ordered mode than in bag mode;
5. no evidence of speaker leakage.

For `P2`, the degenerate shuffle/reversal identity is acknowledged and only the independent controls are counted.

This is a forensic criterion, not a production gate.

---

# 39. Evidence of Event-Aggregation Loss

Classify `EVENT_AGGREGATION` as earliest loss only if ALL:

1. frame/partition temporal-signal criterion passes;
2. `EA-PRECOMPRESSION` is materially worse than the informative ordered partition stages;
3. the loss follows from exact current event membership collapsing temporally distinct frame regions into one event or too few events;
4. `EA-PRECOMPRESSION → E-DESCRIPTOR-COMPRESSED` does not account for the majority of the already-observed loss;
5. AudioTemporalIR receives no equivalent intra-event ordered structure.

The report must show the stage delta explicitly.

---

# 40. Evidence of Frontend Frame Failure

Classify:

`FRONTEND_FRAME_REPRESENTATION`

if:

- P2/P4/P8 all fail to show reproducible same-concept temporal specificity;
- current event representation is not materially worse than frame/block diagnostics;
- order controls show no coherent advantage.

This would justify a deeper representation revisit.

---

# 41. Evidence of Event Descriptor Compression Loss

Classify `EVENT_DESCRIPTOR_COMPRESSION` only if ALL:

1. `EA-PRECOMPRESSION` retains reproducible correct-concept specificity;
2. `E-DESCRIPTOR-COMPRESSED` is materially worse in correct rank and/or correct-vs-best-wrong margin;
3. lost descriptor identities/support can be traced to current event descriptor selection/pruning;
4. the majority of this stage-local loss cannot be explained by event membership count alone.

Event descriptor compression cannot be blamed for temporal order that was already absent in `EA-PRECOMPRESSION`.

---

# 42. Evidence of AudioTemporalIR Loss

Classify `AUDIOTEMPORAL_IR` only if `E-DESCRIPTOR-COMPRESSED` retains useful acoustic specificity that is measurably reduced in the acoustic-only `IR` projection, with the lost identities/timing traceable to IR conversion.

---

# 43. Evidence of Graph Persistence Loss

Classify `GRAPH_PERSISTENCE` only if the acoustic-only `IR` projection retains useful specificity that is measurably reduced in the acoustic-only graph-facing projection, with no lexical/cross-modal identities used in the similarity calculation.

---

# 44. Multi-Stage Rule

Use:

`MULTI_STAGE`

only if two or more stages independently satisfy loss criteria and neither can explain the downstream failure alone.

Do not use multi-stage as uncertainty fallback.

---

# 45. No Temporal Signal Rule

Use:

`NO_TEMPORAL_SIGNAL`

if no audited pre-event representation demonstrates meaningful held-out temporal specificity.

---

# 46. Inconclusive Rule

Use:

`INCONCLUSIVE`

if required telemetry is unavailable or causal criteria cannot distinguish stages.

---

# 47. Earliest-Loss Priority

If multiple downstream losses occur, report the earliest causally sufficient stage.

Priority follows actual pipeline order:

```text
FRONTEND_FRAME_REPRESENTATION
→ EVENT_AGGREGATION
→ EVENT_DESCRIPTOR_COMPRESSION
→ AUDIOTEMPORAL_IR
→ GRAPH_PERSISTENCE
```

---

# 48. Audio Reopening Decisions

Exactly one final reopening decision:

### REOPEN_AUDIO_EVENT_GRANULARITY

Only if earliest loss is `EVENT_AGGREGATION`.

### REOPEN_AUDIO_TEMPORAL_REPRESENTATION

Only if earliest loss is `FRONTEND_FRAME_REPRESENTATION`.

### REPAIR_DOWNSTREAM_TEMPORAL_PERSISTENCE

Only if earliest loss is `AUDIOTEMPORAL_IR` or `GRAPH_PERSISTENCE`.

### NO_AUDIO_REOPENING_JUSTIFIED

If current evidence does not justify Audio v2 modification.

### FORENSICS_INCONCLUSIVE

If causal localization fails.

---

# 49. Event Descriptor Compression Decision Mapping

If earliest loss is:

`EVENT_DESCRIPTOR_COMPRESSION`

the reopening decision is:

`REOPEN_AUDIO_EVENT_GRANULARITY`

but the report MUST state explicitly that the target is event descriptor retention/compression rather than event boundary count.

---

# 50. No Repair Design in ATGF01

ATGF01 may recommend a repair CLASS only.

It MUST NOT design or implement:
- a new segmentation algorithm;
- new frame blocks;
- new event thresholds;
- new descriptor fields;
- new persistence structures.

---

# 51. No Threshold Tuning

Forbidden:
- tuning novelty threshold;
- tuning onset threshold;
- tuning offset hysteresis;
- tuning max event duration;
- tuning block count.

All current encoder constants remain frozen.

---

# 52. No Semantic Unit Naming

Diagnostic blocks/events may not be called:
- phonemes;
- syllables;
- morphemes;
- word-parts.

Use:
`frame`, `block`, `event`, `transition`.

---

# 53. No External Features

Forbidden:
- pretrained audio model;
- wav2vec;
- Whisper;
- HuBERT;
- MFCC classifier;
- spectrogram CNN;
- learned embeddings.

---

# 54. No New Data

No additional Speech Commands clips.

No synthetic speech.

No augmentation.

No noise injection.

---

# 55. Determinism

Repeated forensic extraction on identical item must produce bit/canonical-identical:
- frame inventory;
- partitions;
- block supports;
- similarity matrices;
- stage classification.

---

# 56. Numeric Tolerance

Use one fixed machine tolerance for floating equality:

```text
1e-12
```

unless existing DGCA numeric policy already specifies a stricter canonical tolerance.

Do not change tolerance after outcome inspection.

---

# 57. Required Similarity Matrices

For each stage/partition, produce held-out-to-training comparison matrices:

```text
20 held-out × 40 grounded examples
```

and concept-aggregated matrices:

```text
20 held-out × 10 concepts
```

---

# 58. Order-Control Matrices

For P2/P4/P8 produce:
- ordered;
- bag;
- reversed;
- deterministic shuffled.

Same probe set.

---

# 59. Event-vs-Partition Delta

For every held-out probe report:

\[
\Delta Rank_k
=
Rank_{Event}
-
Rank_{P_k}
\]

Positive means partition representation improves correct rank relative to current event representation.

---

# 60. Correct-Dominance Delta

For each partition:

\[
\Delta CD_k
=
CorrectDominant_{P_k}
-
CorrectDominant_{Event}
\]

Diagnostic only.

---

# 61. Temporal Specificity Advantage

For correct concept:

\[
TSA_k(Q)
=
CorrectMean_{ordered}
-
CorrectMean_{bag}
\]

Also compute against reversed and shuffled controls.

---

# 62. Wrong-Concept Temporal Advantage

Compute identical metrics for best wrong concept.

A useful temporal representation should not merely increase all similarities.

---

# 63. Correct-vs-Wrong Temporal Margin

Define:

\[
Margin_k(Q)
=
CorrectMean_k(Q)-BestWrongMean_k(Q)
\]

Report parent event margin and each partition margin.

---

# 64. Representation Leakage Check

Labels may be used only after representation extraction to group offline metrics.

Assert:
- no label input to encoder;
- no concept-specific partition;
- no class-specific weighting;
- no probe-specific transformation.

---

# 65. Held-Out Primary Probe Count

All primary stage conclusions use exactly:

\[
20
\]

held-out grounded-word probes.

No excluded failure probes.

---

# 66. OOD Secondary Probe Count

Use exactly:

\[
10
\]

OOD probes for genericity/control reporting.

---

# 67. Parent Single-Event Reproduction Gate

Required:

`68/70` exact reproduction.

If current code/asset state yields a different count, report mismatch and block causal closure until reconciled.

---

# 68. Frame Inventory Completeness Gate

Required:
- all 70 ATG01 items;
- all valid frames;
- all current Audio v2 frame descriptors.

No sampled subset.

---

# 69. Partition Completeness Gate

Required P2/P4/P8 for all items with sufficient valid frames.

If an item lacks enough valid frames for a partition:
- record explicit structural insufficiency;
- do not invent frames.

---

# 70. Stage Classification Completeness

Required:

`20/20` held-out probes classified at every reconstructable stage.

---

# 71. Earliest-Loss Evidence Table

Final report must include one table with rows:

```text
F0
P2
P4
P8
EA-PRECOMPRESSION
E-DESCRIPTOR-COMPRESSED
AUDIOTEMPORAL_IR
GRAPH-ACOUSTIC-ONLY
```

and columns:
- correct dominant;
- correct competitive;
- wrong dominant;
- nondiscriminative;
- median rank;
- temporal order advantage;
- information retained/lost.

---

# 72. Formal Invariants

### ATGF01-INV-01
Parent lineage exact.

### ATGF01-INV-02
Parent data unchanged.

### ATGF01-INV-03
Audio Encoder source unchanged.

### ATGF01-INV-04
Retrieval source unchanged.

### ATGF01-INV-05
Grounding unchanged.

### ATGF01-INV-06
Graph mutation zero.

### ATGF01-INV-07
No new persistent state.

### ATGF01-INV-08
No new Law.

### ATGF01-INV-09
No learned scalar.

### ATGF01-INV-10
No semantic labels enter representation.

### ATGF01-INV-11
Held-out speakers isolated.

### ATGF01-INV-12
Current frame stream used exactly.

### ATGF01-INV-13
Current event representation reproduced.

### ATGF01-INV-14
68/70 single-event finding reproduced.

### ATGF01-INV-15
P2 fixed.

### ATGF01-INV-16
P4 fixed.

### ATGF01-INV-17
P8 fixed.

### ATGF01-INV-18
No adaptive segmentation.

### ATGF01-INV-19
Ordered comparison deterministic.

### ATGF01-INV-20
Bag control deterministic and empty-empty blocks never add lexical similarity mass.

### ATGF01-INV-21
Reversal control deterministic.

### ATGF01-INV-22
Shuffle control fixed before outcomes; P2 shuffle/reversal degeneracy explicitly recorded.

### ATGF01-INV-23
No external alignment.

### ATGF01-INV-24
No external feature extractor.

### ATGF01-INV-25
No phoneme semantics.

### ATGF01-INV-26
Similarity formula and common acoustic-only stage projection fixed.

### ATGF01-INV-27
No partition selection as repair.

### ATGF01-INV-28
20/20 primary probes retained.

### ATGF01-INV-29
10/10 OOD controls retained.

### ATGF01-INV-30
Stage classification includes EA-PRECOMPRESSION and E-DESCRIPTOR-COMPRESSED separately.

### ATGF01-INV-31
Earliest-loss rule obeyed.

### ATGF01-INV-32
No post-hoc threshold tuning.

### ATGF01-INV-33
No source replacement.

### ATGF01-INV-34
Failures retained.

### ATGF01-INV-35
Scientific conclusion bounded.

### ATGF01-INV-36
Historical signature MATCH.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 73. Forbidden Mechanisms

1. Audio Encoder modification.  
2. Retrieval modification.  
3. Grounding modification.  
4. Graph learning.  
5. New persistent field.  
6. New primitive.  
7. New Law.  
8. New threshold.  
9. Threshold tuning.  
10. Learned segmentation.  
11. Adaptive block boundaries.  
12. Label-dependent partition.  
13. Concept-specific transformation.  
14. Speaker embedding.  
15. ASR.  
16. Phoneme model.  
17. Forced alignment.  
18. DTW.  
19. Edit distance classifier.  
20. LCS classifier.  
21. Template matching.  
22. Wav2vec/HuBERT/Whisper.  
23. MFCC classifier.  
24. New audio feature extractor.  
25. Data augmentation.  
26. New recordings.  
27. Synthetic speech.  
28. Same-speaker shortcut.  
29. Probe exclusion.  
30. Best-of-partition cherry-picking.  
31. Best-of-shuffle cherry-picking or treating P2 reversal as an independent shuffle control.  
32. Post-hoc numeric tolerance change.  
33. Event-threshold modification.  
34. Persistent frame-block creation or lexical/cross-modal identities in stage-similarity projections.  
35. Repair implementation.  
36. Claiming phoneme/syllable discovery.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 74. Formal Forensic Gates

### ATGF01-G01
Parent lineage verified.

### ATGF01-G02
Manifest/data identity verified.

### ATGF01-G03
Audio v2 source unchanged.

### ATGF01-G04
Read-only guards PASS.

### ATGF01-G05
68/70 single-event finding reproduced.

### ATGF01-G06
Frame inventory complete.

### ATGF01-G07
Event aggregation telemetry complete.

### ATGF01-G08
EA-PRECOMPRESSION reconstruction + event descriptor compression audit complete.

### ATGF01-G09
AudioTemporalIR audit complete.

### ATGF01-G10
Graph-facing audit complete.

### ATGF01-G11
P2 extraction complete.

### ATGF01-G12
P4 extraction complete.

### ATGF01-G13
P8 extraction complete.

### ATGF01-G14
Ordered matrices complete with empty-block exclusion semantics.

### ATGF01-G15
Bag matrices complete.

### ATGF01-G16
Reversal matrices complete.

### ATGF01-G17
Shuffle matrices complete; P2 degeneracy recorded.

### ATGF01-G18
Same-word/different-word matrices complete.

### ATGF01-G19
Speaker isolation verified.

### ATGF01-G20
Stage classifications complete 20/20.

### ATGF01-G21
Frame temporal-signal criterion evaluated.

### ATGF01-G22
Event-aggregation vs event-descriptor-compression causal separation evaluated.

### ATGF01-G23
Frontend-failure criterion evaluated.

### ATGF01-G24
IR/persistence loss criteria evaluated.

### ATGF01-G25
Exactly one earliest-loss verdict.

### ATGF01-G26
Exactly one reopening decision.

### ATGF01-G27
36/36 invariants + 36/36 forbidden PASS.

### ATGF01-G28
Historical signature MATCH + full regression untouched.

Required for forensic closure:

\[
\boxed{28/28\ PASS}
\]

---

# 75. Allowed Earliest-Loss Verdicts

Exactly one:

```text
FRONTEND_FRAME_REPRESENTATION
EVENT_AGGREGATION
EVENT_DESCRIPTOR_COMPRESSION
AUDIOTEMPORAL_IR
GRAPH_PERSISTENCE
MULTI_STAGE
NO_TEMPORAL_SIGNAL
INCONCLUSIVE
```

---

# 76. Allowed Reopening Decisions

Exactly one:

```text
REOPEN_AUDIO_EVENT_GRANULARITY
REOPEN_AUDIO_TEMPORAL_REPRESENTATION
REPAIR_DOWNSTREAM_TEMPORAL_PERSISTENCE
NO_AUDIO_REOPENING_JUSTIFIED
FORENSICS_INCONCLUSIVE
```

---

# 77. Required Artifacts

Produce:

```text
ATGF01-AUDITORY-TEMPORAL-GRANULARITY-FORENSIC-REPORT.md

atgf01_lineage.json
atgf01_readonly_guard.json
atgf01_frame_inventory.jsonl
atgf01_frame_change.jsonl
atgf01_event_aggregation.jsonl
atgf01_event_descriptor_compression.jsonl
atgf01_audiotemporal_ir.jsonl
atgf01_graph_facing.jsonl

atgf01_partition_2.jsonl
atgf01_partition_4.jsonl
atgf01_partition_8.jsonl

atgf01_similarity_f0.jsonl
atgf01_similarity_p2_ordered.jsonl
atgf01_similarity_p4_ordered.jsonl
atgf01_similarity_p8_ordered.jsonl
atgf01_similarity_p2_bag.jsonl
atgf01_similarity_p4_bag.jsonl
atgf01_similarity_p8_bag.jsonl
atgf01_similarity_reversed.jsonl
atgf01_similarity_shuffled.jsonl

atgf01_concept_matrices.json
atgf01_order_controls.jsonl
atgf01_temporal_margins.jsonl
atgf01_stage_classification.jsonl
atgf01_stage_summary.json
atgf01_earliest_loss.json
atgf01_audio_reopening_decision.json

atgf01_invariants.json
atgf01_forbidden.json
atgf01_gates.json
atgf01_signature_verification.json
atgf01_failures.jsonl
```

---

# 78. Required Human-Readable Report Sections

1. Executive Verdict  
2. Parent Lineage  
3. Read-Only Integrity  
4. Reproduction of 68/70 Single-Event Finding  
5. Frame Inventory  
6. Frame Temporal Evolution  
7. Event Aggregation Causes  
8. Event Pre-Compression Reconstruction  
9. Event Descriptor Compression  
10. AudioTemporalIR Exposure  
10. Graph-Facing Exposure  
11. P2 Diagnostics  
12. P4 Diagnostics  
13. P8 Diagnostics  
14. Ordered vs Bag  
15. Reversal Control  
16. Shuffle Control  
17. Same-Word vs Different-Word Generalization  
18. Speaker Isolation  
19. Stage-by-Stage Classification  
20. Earliest Information-Loss Analysis  
21. Audio Reopening Decision  
22. 36 Invariants  
23. 36 Forbidden Mechanisms  
24. 28 Gates  
25. Bounded Scientific Interpretation

---

# 79. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — ATGF01
AUDITORY TEMPORAL GRANULARITY FORENSICS

PARENT ATG01 COMMIT:
7e43974

PARENT F01 COMMIT:
74f788e

PARENT ARSR01 IMPLEMENTATION:
a26deb5

HISTORICAL SIGNATURE:
915119d40643cb97

EXECUTION MODE:
STRICT_READ_ONLY

AUDIO ENCODER SOURCE CHANGES:
0 / NONZERO

RETRIEVAL SOURCE CHANGES:
0 / NONZERO

GRAPH MUTATION:
0 / NONZERO

SINGLE-EVENT REPRODUCTION:
... /70

FRAME INVENTORY:
COMPLETE / INCOMPLETE

HELD-OUT PRIMARY PROBES:
... /20

OOD CONTROL PROBES:
... /10

EA-PRECOMPRESSION:
CORRECT DOMINANT ... /20
CORRECT COMPETITIVE ... /20
WRONG DOMINANT ... /20
NONDISCRIMINATIVE ... /20
MEDIAN CORRECT RANK ...

E-DESCRIPTOR-COMPRESSED:
CORRECT DOMINANT ... /20
CORRECT COMPETITIVE ... /20
WRONG DOMINANT ... /20
NONDISCRIMINATIVE ... /20
MEDIAN CORRECT RANK ...

P2 ORDERED:
CORRECT DOMINANT ... /20
MEDIAN CORRECT RANK ...
ORDER ADVANTAGE ... /20

P4 ORDERED:
CORRECT DOMINANT ... /20
MEDIAN CORRECT RANK ...
ORDER ADVANTAGE ... /20

P8 ORDERED:
CORRECT DOMINANT ... /20
MEDIAN CORRECT RANK ...
ORDER ADVANTAGE ... /20

FRAME TEMPORAL SIGNAL:
DEMONSTRATED / NOT_DEMONSTRATED / INCONCLUSIVE

EVENT AGGREGATION LOSS:
DEMONSTRATED / NOT_DEMONSTRATED / INCONCLUSIVE

EVENT DESCRIPTOR COMPRESSION LOSS:
DEMONSTRATED / NOT_DEMONSTRATED / INCONCLUSIVE

AUDIOTEMPORAL_IR LOSS:
DEMONSTRATED / NOT_DEMONSTRATED / INCONCLUSIVE

GRAPH PERSISTENCE LOSS:
DEMONSTRATED / NOT_DEMONSTRATED / INCONCLUSIVE

EARLIEST INFORMATION-LOSS STAGE:
...

AUDIO REOPENING DECISION:
...

ATGF01 INVARIANTS:
x /36

FORBIDDEN MECHANISMS:
x /36

FORENSIC GATES:
x /28

HISTORICAL SIGNATURE:
MATCH / MISMATCH

FINAL FORENSIC STATUS:
ATGF01_FORENSICALLY_CLOSED /
ATGF01_BLOCKED /
ATGF01_INCONCLUSIVE
============================================================
```

---

# 80. Formal Status

\[
\boxed{
\textbf{ATGF01 Formal Forensic Specification v1.0 — COMPLETE}
}
\]

Status:

```text
FROZEN AFTER FREEZE REVIEW AMENDMENTS
```

Binding freeze amendments include:

- explicit `EA-PRECOMPRESSION` stage to separate event aggregation from descriptor compression;
- acoustic-only common stage projection;
- empty-empty block comparisons excluded from lexical similarity;
- P2 shuffle/reversal degeneracy explicitly recorded;
- temporal-order evidence defined on correct-vs-best-wrong margin;
- no lexical/cross-modal identities in graph-facing representation similarity.

No Audio Encoder reopening or repair implementation is authorized by this freeze.
The next authorized action is the ATGF01 read-only forensic execution.
