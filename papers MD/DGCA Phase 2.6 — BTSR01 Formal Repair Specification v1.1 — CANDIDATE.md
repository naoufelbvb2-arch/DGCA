# DGCA Phase 2.6 — BTSR01

## Bounded Tonotopic Selection Repair 01

# Formal Repair Specification v1.1 — CANDIDATE

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6  
**Repair ID:** `BTSR01`

**Parent Repair:**  
`BFAR01_COUNTERFACTUAL_EFFICACY_FAIL`

**Parent Forensic:**  
`BFAR01_F01_FORENSIC_PASS`

**Closure Clarification:**  
`BFAR01_F01_C01_CLOSED_WITH_CLARIFICATIONS`

**Parent Forensic Commit:** `73a283b`  
**Closure Commit:** `cbd6617`

**Historical Cognitive Signature:**  
`915119d40643cb97`

**Version:** `1.1`  
**Status:** `CANDIDATE — NOT FROZEN`

**Production Implementation:** `NOT AUTHORIZED`  
**Counterfactual Execution:** `NOT AUTHORIZED YET`

---

# 1. Repair Mission

BTSR01 targets exactly:

```text
RANKED_SELECTION_MISALIGNMENT
```

observed under BFAR01.

The repair changes only:

```text
GRAPH-FACING CHILD-EVENT
SPECTRAL DESCRIPTOR SELECTION
```

The following remain frozen:

```text
Audio v2
AEGR event boundaries
AEMG base authority
spectral descriptor vocabulary
periodicity semantics
B_audio,event = 8
actual-adjacency transition construction
LDSR
ASUR
candidate discovery
Law 11
```

---

# 2. Frozen Scientific Basis

Authoritative results:

```text
TOTAL COMPETITOR RELATIONS:
19

GROUNDING-DERIVED:
17

NON-GROUNDED:
2

K_ATOMIC_GLOBAL_MAX:
1

K_ATOMIC_DECISION_MAX:
1

K_TRANSITION_GLOBAL_MAX:
1

K_TRANSITION_DECISION_MAX:
1

RELATIONS REQUIRING >8:
0/17
```

Therefore:

\[
K^{transition,global}_{max}=1
\ll
B_{audio,event}=8
\]

The event budget is not the causal bottleneck.

---

# 3. Grounded Parent Failure Partition

Freeze:

```text
CLOSED:
9/17

L1 MEMBERSHIP FAILURE:
3/17

L2 DIRECTIONAL FAILURE:
1/17

L3 NONPOSITIVE MARGIN:
4/17
```

The two remaining frozen relations:

```text
CA1_03
CA2_07
```

are:

```text
NOT_APPLICABLE_TO_GROUNDED_CAUSAL_COVER
```

and remain telemetry only.

---

# 4. Repair Hypothesis

BFAR01 used:

```text
GLOBAL WITHIN-EVENT SUPPORT RANK
```

to choose spectral descriptors.

BTSR01 tests one fixed hypothesis:

\[
\boxed{
GlobalRankConcentration
\rightarrow
FixedTonotopicCoverage
}
\]

The hypothesis is:

> A bounded, label-free selection that preserves coverage across the pre-existing tonotopic axis will retain more useful acoustic distinctions than global support rank alone.

This is a repair hypothesis.

It is NOT a law.

It is NOT proven optimal.

---

# 5. Oracle Firewall

The BTSR selector may NOT access:

```text
minimum-cover assignment
minimum-cover union
budget-feasible solutions
causal witness IDs
causal path IDs
correct concepts
wrong concepts
CA1 labels
CA2 labels
heldout outcomes
causal margins
grounding transition memory
```

The forensic results justify opening BTSR01 but do not define its selections.

---

# 6. Frozen Budget

\[
B_{audio,event}=8
\]

Required:

\[
|F_{BTSR}(E)|\le8
\]

for every event.

No event may exceed 8 graph-facing descriptors.

---

# 7. Existing Descriptor Vocabulary Only

BTSR may emit only already-existing Audio v2 identities.

Required:

```text
NEW SPECTRAL IDENTITIES:
0

NEW PERIODICITY IDENTITIES:
0

NEW DESCRIPTOR FAMILY:
0

NEW COMPOUND TOKEN:
0

NEW WHOLE-PROFILE TOKEN:
0

NEW PAIR TOKEN:
0
```

---

# 8. Fixed Spectral Axis

Use the existing 24-channel Audio v2 tonotopic ordering:

\[
i\in\{0,\ldots,23\}
\]

No reordering.

No learned frequency topology.

No corpus-derived frequency topology.

---

# 9. Fixed Eight-Stratum Geometry

BTSR01 v1.1 freezes exactly:

\[
M=8
\]

spectral strata.

Define:

\[
g(i)
=
\left\lfloor
\frac{8i}{24}
\right\rfloor
=
\left\lfloor
\frac{i}{3}
\right\rfloor
\]

Thus:

```text
S0 = channels  0,1,2
S1 = channels  3,4,5
S2 = channels  6,7,8
S3 = channels  9,10,11
S4 = channels 12,13,14
S5 = channels 15,16,17
S6 = channels 18,19,20
S7 = channels 21,22,23
```

This partition is identical for every event.

---

# 10. No Event-Dependent Repartition

Forbidden:

```text
7 strata when periodicity exists
8 strata otherwise
```

Forbidden:

```text
event-specific stratum boundaries
speaker-specific strata
label-specific strata
data-derived strata
```

Periodicity may not change the geometry of the spectral partition.

---

# 11. Why Eight Strata

The value `8` is inherited from the frozen graph-facing event budget:

\[
B_{audio,event}=8
\]

and the frontend already has:

\[
24
\]

ordered channels.

Therefore:

\[
24/8=3
\]

channels per fixed stratum.

No value was fitted to heldout accuracy.

---

# 12. Existing Spectral Evidence

For event \(E\), use the exact frozen within-event spectral evidence/order:

\[
\Pi_{spec}(E)
\]

No new magnitude.

No new feature.

No new support score.

---

# 13. Primary Tonotopic Selection

For every non-empty stratum \(s\), choose one descriptor:

\[
w_s(E)
\]

equal to the valid spectral descriptor in that stratum having highest existing within-event spectral support.

Let:

\[
W(E)=\{w_s(E)\}
\]

over all non-empty strata.

---

# 14. Primary Tie Break

If two descriptors inside one stratum have exactly equal support:

1. use existing canonical spectral evidence order;
2. if still tied, use lower canonical channel index.

Required:

```text
RANDOM TIE BREAK:
0
```

---

# 15. Empty Strata

If a stratum contains no valid spectral evidence:

```text
EMIT NOTHING FROM THAT STRATUM
```

during primary selection.

Do not fabricate a descriptor.

---

# 16. Periodicity Semantics Remain Frozen

Use the exact inherited BFAR periodicity rule.

Define:

\[
b_{per}(E)=
\begin{cases}
1,&\text{if valid modal periodicity exists}\\
0,&\text{otherwise}
\end{cases}
\]

Periodicity semantics themselves are unchanged.

---

# 17. Spectral Capacity

Define:

\[
b_{spec}(E)=8-b_{per}(E)
\]

Thus:

```text
no valid periodicity:
spectral capacity = 8

valid periodicity:
spectral capacity = 7
```

Crucially:

```text
SPECTRAL STRATUM GEOMETRY:
ALWAYS 8 STRATA
```

---

# 18. Periodicity Reduction Rule

If:

\[
b_{per}(E)=1
\]

and:

\[
|W(E)|>7
\]

remove exactly:

```text
ONE
```

stratum winner.

The removed winner must be the member of \(W(E)\) with lowest existing within-event spectral support.

---

# 19. Periodicity Reduction Tie Break

If multiple stratum winners tie for lowest support, discard according to the inverse of canonical winner priority:

1. lowest existing support;
2. later canonical support-order position;
3. higher channel index.

The result must be deterministic.

---

# 20. Periodicity Structural Authority Bound

Periodicity may therefore directly cause at most:

```text
ONE SPECTRAL WINNER
```

to be removed.

It may NOT:

```text
move stratum boundaries
change stratum membership
change which channels compete inside a stratum
```

This closes the v1.0 periodicity repartition confound.

---

# 21. Residual Spectral Capacity

After primary fixed-stratum selection and any one-slot periodicity reduction, define:

\[
r(E)
=
b_{spec}(E)-|S_{primary}(E)|
\]

where:

\[
S_{primary}(E)
\]

is the retained stratum-winner set.

---

# 22. Residual Fill

If:

\[
r(E)>0
\]

select up to \(r(E)\) additional descriptors from:

```text
valid
unselected
spectral descriptors
```

using the exact pre-existing global within-event spectral support order.

Stop when:

\[
|S_{spec}(E)|=b_{spec}(E)
\]

or no lawful spectral evidence remains.

---

# 23. Residual Fill Is Secondary

The exact order is:

```text
TONOTOPIC PRIMARY COVERAGE
FIRST

RESIDUAL GLOBAL SUPPORT FILL
SECOND
```

Residual fill may not displace an already-selected stratum winner.

---

# 24. No Forced Padding

If fewer descriptors exist than available capacity:

\[
|F(E)|<8
\]

is legal.

Do not fabricate evidence merely to saturate the budget.

---

# 25. Final BTSR Projection

Define:

\[
F_{BTSR}(E)
=
S_{spec}(E)
\cup
ModalPeriodicity(E)
\]

with structural-identity deduplication.

Required:

\[
|F_{BTSR}(E)|\le8
\]

---

# 26. Event Identity Is Unchanged

BTSR modifies only:

```text
CHILD SEQUENCE DESCRIPTOR PROJECTION
```

It does NOT modify:

```text
AEGR event identity
event boundary timing
Parent event identity
recording identity
frame ownership
```

---

# 27. Same-Stratum Causal Collision Audit

After BTSR output is frozen, audit each event/stratum for frozen grounded causal evidence.

Report:

```text
valid causal descriptors in stratum
selected descriptor
causal descriptors dropped
whether residual fill recovered a dropped descriptor
```

Classify each causal collision:

```text
NO_CAUSAL_COLLISION

CAUSAL_COLLISION_RECOVERED_BY_RESIDUAL_FILL

CAUSAL_COLLISION_UNRECOVERED
```

---

# 28. Collision Audit Is Read-Only

The collision audit may NOT alter:

```text
winner selection
stratum layout
residual filling
periodicity handling
```

No repair-inside-repair.

---

# 29. Residual-Fill Concentration Audit

Report:

```text
events using residual fill
total residual-fill selections
mean residual-fill slots/event
max residual-fill slots/event
fraction of selected spectral descriptors
coming from residual fill
```

This quantifies how much of the BFAR-style global ranking re-enters after primary tonotopic coverage.

---

# 30. Selector Input Domain

The BTSR selector may access only:

```text
current finalized event spectral evidence
canonical channel index
valid modal periodicity state
frozen budget
```

---

# 31. Forbidden Selector Inputs

Required:

```text
LABEL DEPENDENCE:
0

HELDOUT DEPENDENCE:
0

CANDIDATE DEPENDENCE:
0

GRAPH TRANSITION MEMORY DEPENDENCE:
0

SPEAKER DEPENDENCE:
0

FORENSIC ORACLE DEPENDENCE:
0
```

---

# 32. Same Selector Everywhere

Use the identical BTSR selector during:

```text
first exposure
grounding exposure
heldout retrieval
OOD retrieval
whole-stream replay
chunked replay
```

No grounding/query selector asymmetry.

---

# 33. No Bootstrap Dependency

BTSR must not require previously learned:

```text
concept relation
transition recurrence
candidate score
lexical context
```

to determine current event representation.

Therefore BTSR can operate on the first exposure.

---

# 34. AEMG Base Authority Remains Frozen

Required:

\[
GROUNDINGTX_{BTSR}
=
GROUNDINGTX_{AEMG}
=
GROUNDINGTX_P
\]

Child BTSR descriptors retain:

```text
BASE LEXICAL AUTHORITY:
0
```

---

# 35. Base Nonconductance

Required:

```text
BASE SEMANTIC DIFF:
0

CONTINUATION BASE DIFF:
0

CHILD LEXICAL AUTHORITY:
0

DOUBLE AUTHORITY:
0

SEQUENCE→BASE CONDUCTANCE:
0
```

---

# 36. Candidate Discovery Remains Frozen

For every frozen query:

\[
C_Q^{BTSR}
=
C_Q^{AEMG}
\]

Required:

```text
CANDIDATE SET DIFF:
0
```

---

# 37. Sequence Construction

Use the exact existing actual-adjacency sequence constructor over:

\[
F_{BTSR}(E_t)
\]

and:

\[
F_{BTSR}(E_{t+1})
\]

No new transition primitive.

---

# 38. Transition Opportunity Ceiling

Because:

\[
|F(E)|\le8
\]

raw pair opportunities remain:

\[
\le64
\]

per actual boundary.

---

# 39. Sequence Mathematics Frozen

Do NOT modify:

\[
W_{t,c}
\]

\[
Z_t
\]

\[
\rho_Q(t,c)
\]

\[
SeqLDSR_Q(t,c)
\]

\[
q_t
\]

or:

\[
S_{seq}(c|Q)
\]

No new coefficient.

No new genericity penalty.

No new normalization.

---

# 40. Parent Residual L3 Risk

Freeze:

```text
GROUNDED L3 NONPOSITIVE:
4/17
```

under parent BFAR.

BTSR must determine whether those margins persist after lawful selection topology changes.

---

# 41. No LDSR/ASUR Modification

Even if BTSR continues to show L3 failures:

```text
DO NOT MODIFY LDSR
DO NOT MODIFY ASUR
```

inside BTSR01.

---

# 42. Grounded Evaluation Domain

Causal selector validation uses exactly:

```text
17 GROUNDING-DERIVED COMPETITOR RELATIONS
```

The two non-grounded relations are excluded from causal efficacy denominators.

---

# 43. Grounded CA1 Domain

Freeze:

```text
CA1 GROUNDED RELATIONS:
4
```

Required for full PASS:

```text
4/4 POSITIVE CAUSAL CLOSURE
```

---

# 44. Grounded CA2 Domain

Freeze:

```text
CA2 GROUNDED RELATIONS:
13
```

Required for full PASS:

```text
13/13 POSITIVE CAUSAL CLOSURE
```

---

# 45. Non-Grounded Relations

Freeze:

```text
CA1_03
CA2_07
```

as:

```text
NON-GROUNDED TELEMETRY
```

They may not influence:

```text
selector design
strata
tie breaks
PASS causal denominator
```

---

# 46. Grounded Causal-Path Retention Gate

For all 17 grounded competitor relations, BTSR must preserve at least one complete frozen grounding-derived causal path.

Required:

```text
GROUNDED CAUSAL PATH MEMBERSHIP:
17/17
```

---

# 47. Parent L1 Repair Gate

The three known grounded L1 failures must be repaired:

```text
CA1_01
CA1_04
CA2_08
```

Required:

```text
PARENT L1 FAILURES REPAIRED:
3/3
```

---

# 48. No New L1 Regression

Required:

```text
NEW GROUNDED L1 FAILURES:
0
```

---

# 49. L2 Realizability Gate

For every grounded relation:

```text
complete retained causal membership
+
lawful grounded directional path
```

must exist.

Required:

```text
GROUNDED L2 REALIZABILITY:
17/17
```

---

# 50. Grounded Causal-Boundary Inventory

Before counterfactual execution, BTSR01 must reproduce and freeze the exact grounding-derived causal-boundary inventory from:

```text
BFAR01-F01
+
BFAR01-F01-C01
```

Let its exact denominator be:

\[
N_G
\]

The artifact must contain every boundary ID.

---

# 51. Boundary Denominator Freeze Rule

`N_G` MUST be resolved before BTSR01 execution Master Prompt is frozen.

No runtime denominator reduction is allowed.

For BTSR PASS:

\[
Support_{causal-boundary}
=
N_G/N_G
\]

---

# 52. Candidate v1.1 Boundary Status

At this candidate stage:

```text
GROUNDED CAUSAL BOUNDARY INVENTORY:
MUST BE RESOLVED DURING CLOSURE REVIEW

RUNTIME CONDITIONAL DENOMINATOR:
FORBIDDEN
```

Thus the Closure Review must either freeze `N_G` and IDs or deny formal freeze.

---

# 53. L3 Causal Margin

For grounded relation:

\[
r=(c^*,w)
\]

compute the frozen causal decomposition under BTSR and define:

\[
\Delta_{causal}^{BTSR}(r)
=
S^{causal}_{seq}(c^*)
-
S^{causal}_{seq}(w)
\]

---

# 54. Full L3 Gate

Required for full BTSR PASS:

\[
\Delta_{causal}^{BTSR}(r)>0
\]

for:

```text
17/17 grounded relations
```

---

# 55. Structural Selection Component Verdict

Report:

```text
BTSR_STRUCTURAL_SELECTION_VALIDATED:
YES / NO
```

Set `YES` iff:

```text
grounded path membership = 17/17
parent L1 failures repaired = 3/3
new grounded L1 failures = 0
grounded L2 realization = 17/17
causal boundary support = N_G/N_G
```

L3 is not part of this structural sub-verdict.

---

# 56. Full Component Validation

Report:

```text
BTSR01_COMPONENT_VALIDATED:
YES / NO
```

Set `YES` only when all full release gates pass, including:

```text
positive grounded causal margins =17/17
```

---

# 57. Structural Pass / L3 Failure

If:

```text
BTSR_STRUCTURAL_SELECTION_VALIDATED:
YES
```

but:

```text
POSITIVE GROUNDED CAUSAL MARGINS:
<17/17
```

then final verdict is:

```text
BTSR01_COUNTERFACTUAL_EFFICACY_FAIL
```

and report:

```text
RESIDUAL_SEQUENCE_DISCRIMINATION:
CONFIRMED_AFTER_SELECTION_REPAIR
```

This would scientifically authorize a later narrow sequence-discrimination repair.

---

# 58. Structural Failure

If L1 or L2 remains incomplete:

```text
BTSR_STRUCTURAL_SELECTION_VALIDATED:
NO
```

The fixed tonotopic hypothesis fails.

Do not tune strata after observing failure.

---

# 59. Causal Closure vs Final Rank

Keep separate:

```text
FROZEN CAUSAL COMPETITOR CLOSURE
```

and:

```text
FINAL PROBE RANK
```

A causal relation can close without the probe becoming Rank 1.

---

# 60. Functional Heldout Telemetry

For every frozen heldout probe report:

```text
correct candidate
correct rank
best wrong candidate
S_base
S_seq
final score
Rank-1 yes/no
```

Global rank must not redefine causal closure.

---

# 61. Sequence Signal

Parent clarification:

```text
SEQUENCE_SIGNAL_PRESENT:
20/20
```

Under BTSR report:

```text
SEQUENCE_SIGNAL_PRESENT:
<count>/20
```

Required for full PASS:

```text
20/20
```

---

# 62. Global Rank-1 Governance

If the original frozen ATG01 protocol contains a hard global Rank-1 acceptance criterion, preserve it exactly.

Otherwise global Rank-1 remains functional telemetry for BTSR component analysis and a mandatory later Audio Composite gate.

Do not invent a new rank threshold inside BTSR.

---

# 63. Non-Grounded Telemetry

For the two non-grounded relations report:

```text
parent correct rank
BTSR correct rank

parent S_seq
BTSR S_seq

parent final score
BTSR final score

forced/ambiguous/not-forced state
```

They do NOT count as causal efficacy evidence.

---

# 64. OOD Safety Domain

Use all frozen 10 OOD probes.

Required:

```text
OOD SAFETY:
10/10

NEWLY FORCED OOD:
0
```

---

# 65. Transition Authority Audit

Required:

```text
DUPLICATE QUERY TRANSITIONS:
0

DUPLICATE CONTEXT AUTHORITY:
0

NON-ADJACENT AUTHORITY:
0

HELDOUT-DERIVED AUTHORITY:
0

Q_T NORMALIZATION:
PASS

SEQUENCE→BASE CONDUCTANCE:
0
```

---

# 66. Transition Authority Verdict

Required:

```text
NO_UNLAWFUL_TRANSITION_AUTHORITY_INFLATION
```

---

# 67. BFAR-vs-BTSR Transition Topology

Report both systems side by side:

```text
distinct transition identities
singleton transition identities
cross-recording recurrent transitions
cross-speaker recurrent transitions
grounding→heldout recurrent transitions
median transition fanout
p90 transition fanout
max transition fanout
median candidate fanout
```

No new fanout penalty.

---

# 68. Same-Stratum Collision Metrics

Report:

```text
events with grounded causal same-stratum collisions
total causal same-stratum collisions
recovered by residual fill
unrecovered after final BTSR projection
```

For full structural validation:

```text
UNRECOVERED COLLISION CAUSING GROUNDED PATH LOSS:
0
```

---

# 69. Periodicity Displacement Ledger

With fixed strata, report:

```text
events with periodicity
events where periodicity removed one stratum winner
identity of removed winner
whether removed winner is causal
whether another complete grounded path survives
```

No periodicity ablation.

---

# 70. Parent Dropped-Causal Recovery

After BTSR output is frozen, report:

```text
parent BFAR dropped causal descriptors
recovered by BTSR
still absent
new causal descriptors lost by BTSR
```

Diagnostic only.

---

# 71. Rank 8–11 Audit

Parent forensic identified dropped causal descriptors at:

```text
rank 8
rank 9
rank 10
rank 11
```

Report BTSR retention separately for each rank.

No rank-specific selection rule may be introduced.

---

# 72. Counterfactual Conditions

Construct independently:

```text
P
Historical Parent

B
BFAR01 ranked-selection parent

T0
BTSR projection with S_seq disabled

T1
BTSR projection with frozen LDSR/ASUR

T2
BTSR representation under exact event-order reversal

W
Read-only causal forensic view
```

---

# 73. T0 Gate

Required:

```text
T0 BASE SEMANTIC DIFF:
0

T0 CONTINUATION DIFF:
0

T0 CANDIDATE SET DIFF:
0

T0 CHILD LEXICAL AUTHORITY:
0
```

---

# 74. T1 Gate

T1 is the primary BTSR efficacy condition.

No downstream mathematics may change.

---

# 75. T2 Reversal

T2 must preserve:

```text
BTSR descriptor multiset
base state
candidate sets
recording identity
```

and reverse exact event order.

Reuse the frozen asymmetric-transition audit methodology.

---

# 76. Streaming / Chunk Equivalence

For every frozen chunking:

\[
F_{whole}(E)
=
F_{chunked}(E)
\]

Required:

```text
PASS
```

---

# 77. Deterministic Replay

Run complete BTSR counterfactual twice independently.

Required:

```text
DETERMINISTIC REPLAY:
EXACT
```

---

# 78. SRA01 Safety

Required:

```text
SRA01:
PASS
```

No Audio v2 frontend change.

---

# 79. Text / Vision Isolation

Required:

```text
TEXT CHANGE:
0

VISION CHANGE:
0
```

---

# 80. No New Learned Parameters

Required:

```text
NEW LEARNED PARAMETERS:
0

NEW TUNED THRESHOLDS:
0

NEW CORPUS-FIT CONSTANTS:
0
```

---

# 81. No Partition Search

Forbidden:

```text
try 6 strata
try 7 strata
try 8 strata
compare boundaries
shift boundaries
learn band groups
```

Only:

```text
8 fixed strata × 3 channels
```

is tested.

---

# 82. No Tie-Break Search

Do not test alternative tie rules.

The frozen deterministic tie rule is the only candidate.

---

# 83. No Residual-Fill Variant Search

Do not compare:

```text
residual fill
vs
no residual fill
```

within BTSR01.

The v1.1 candidate includes residual fill exactly as specified.

---

# 84. No Causal Selector

Forbidden:

```text
prefer descriptor because forensic says causal
prefer budget-core descriptor
prefer minimum-cover descriptor
prefer transition-recurrent descriptor
```

---

# 85. Pre-Implementation Prechecks

Evaluate exactly 26:

```text
P01 historical signature exact
P02 lineage exact
P03 BFAR parent exact
P04 BFAR01-F01 exact
P05 BFAR01-F01-C01 exact
P06 grounded relation domain =17
P07 non-grounded domain =2
P08 K_transition_global_max=1 reproduced
P09 K=1 assignment not used by selector
P10 24 spectral channels exact
P11 canonical channel order exact
P12 fixed stratum count =8
P13 fixed stratum membership exact
P14 Pi_spec exact
P15 periodicity semantics exact
P16 event budget=8
P17 periodicity cannot alter partition
P18 selector event-local
P19 no label dependency
P20 no heldout dependency
P21 no candidate dependency
P22 no graph-memory dependency
P23 no speaker dependency
P24 no oracle dependency
P25 grounded causal boundary inventory frozen exactly
P26 deterministic projection exact
```

Required:

```text
26/26 PASS
```

---

# 86. Structural Invariants

Evaluate exactly 48:

```text
INV01 Audio v2 unchanged.
INV02 Frame evidence unchanged.
INV03 AEGR boundaries unchanged.
INV04 Event identity unchanged.
INV05 AEMG base authority unchanged.
INV06 Parent lexical transactions unchanged.
INV07 Candidate discovery unchanged.
INV08 LDSR unchanged.
INV09 ASUR unchanged.
INV10 Law 11 unchanged.
INV11 B_audio,event=8.
INV12 24-channel order unchanged.
INV13 Existing descriptor vocabulary only.
INV14 No whole-profile token.
INV15 No compound token.
INV16 No pair token.
INV17 No new acoustic feature.
INV18 Fixed stratum count=8.
INV19 Fixed 3-channel stratum geometry.
INV20 No event-dependent repartition.
INV21 No periodicity-dependent repartition.
INV22 One primary winner/non-empty stratum.
INV23 Primary winner uses existing support only.
INV24 Primary tie break deterministic.
INV25 Periodicity semantics unchanged.
INV26 Periodicity directly removes <=1 winner.
INV27 Residual fill occurs only after primary coverage.
INV28 Residual fill uses existing support order.
INV29 No residual displacement of primary winner.
INV30 No fabricated descriptor.
INV31 No forced padding.
INV32 Max tokens/event <=8.
INV33 Same selector grounding/query/OOD.
INV34 No label-conditioned selection.
INV35 No heldout-conditioned selection.
INV36 No candidate-conditioned selection.
INV37 No transition-memory selection.
INV38 No speaker-conditioned selection.
INV39 No forensic-oracle selection.
INV40 Actual adjacency only.
INV41 q_t unchanged.
INV42 Sequence→base conductance zero.
INV43 Candidate set unchanged.
INV44 Grounded/non-grounded denominators preserved.
INV45 Causal boundary denominator frozen.
INV46 Streaming/chunk equivalence.
INV47 Deterministic replay exact.
INV48 Historical signature conserved.
```

Required:

```text
48/48 PASS
```

---

# 87. Forbidden Mechanisms

Evaluate exactly 42:

```text
FM01 causal-oracle selector
FM02 minimum-cover selector
FM03 budget-core selector
FM04 transition-memory selector
FM05 label-conditioned selector
FM06 heldout-conditioned selector
FM07 candidate-conditioned selector
FM08 speaker-conditioned selector
FM09 learned partition
FM10 tuned partition
FM11 event-dependent partition
FM12 periodicity-dependent partition
FM13 boundary-offset search
FM14 learned channel weighting
FM15 corpus-fit weighting
FM16 adaptive top-k
FM17 dynamic budget
FM18 budget increase
FM19 periodicity ablation
FM20 periodicity adaptation
FM21 new descriptor
FM22 pair token
FM23 whole-profile token
FM24 compound token
FM25 phoneme model
FM26 syllable model
FM27 ASR
FM28 embedding
FM29 prototype
FM30 clustering
FM31 similarity threshold
FM32 IDF
FM33 genericity weighting
FM34 transition pruning
FM35 new sequence coefficient
FM36 q_t modification
FM37 LDSR modification
FM38 ASUR modification
FM39 AEGR/AEMG modification
FM40 second graph
FM41 graph surgery
FM42 production implementation
```

Required:

```text
42/42 PASS
```

---

# 88. Release Gates

Evaluate exactly 44:

```text
G01 lineage exact
G02 assets exact
G03 regression-before PASS
G04 historical signature exact
G05 BFAR reproduction exact
G06 BFAR01-F01 reproduction exact
G07 C01 clarification exact
G08 grounded domain 17/19 exact
G09 grounded causal boundary inventory exact
G10 BTSR fixed-stratum grammar exact
G11 prechecks 26/26
G12 event budget <=8
G13 new descriptors 0
G14 compound/whole/pair tokens 0
G15 selector label firewall PASS
G16 selector heldout firewall PASS
G17 selector candidate firewall PASS
G18 selector graph-memory firewall PASS
G19 selector speaker firewall PASS
G20 selector oracle firewall PASS
G21 T0 base diff 0
G22 candidate set diff 0
G23 sequence→base conductance 0
G24 grounded causal path membership 17/17
G25 parent L1 failures repaired 3/3
G26 new grounded L1 failures 0
G27 grounded L2 realization 17/17
G28 causal boundary support N_G/N_G
G29 same-stratum causal path loss 0
G30 positive grounded causal margins 17/17
G31 CA1 grounded closure 4/4
G32 CA2 grounded closure 13/13
G33 sequence signal 20/20
G34 transition authority SAFE
G35 OOD safety 10/10
G36 newly forced OOD 0
G37 T2 reversal PASS
G38 streaming/chunk PASS
G39 deterministic replay PASS
G40 SRA01 PASS
G41 text/vision isolation PASS
G42 invariants 48/48
G43 forbidden 42/42
G44 regression-after + production hashes MATCH
```

For full BTSR PASS:

```text
44/44 PASS
```

---

# 89. Verdict Vocabulary

Use exactly:

```text
BTSR01_COUNTERFACTUAL_PASS

BTSR01_COUNTERFACTUAL_EFFICACY_FAIL

BTSR01_COUNTERFACTUAL_SAFETY_FAIL

BTSR01_PREIMPLEMENTATION_REJECTED

BTSR01_COUNTERFACTUAL_BLOCKED
```

---

# 90. Verdict Precedence

```text
BLOCKED
↓
PREIMPLEMENTATION_REJECTED
↓
SAFETY_FAIL
↓
EFFICACY_FAIL
↓
PASS
```

---

# 91. BLOCKED

Use for invalid reconstruction:

```text
lineage mismatch
asset mismatch
historical signature mismatch
parent result mismatch
grounded-domain mismatch
unresolved grounded-boundary denominator
```

---

# 92. PREIMPLEMENTATION_REJECTED

Use if BTSR requires:

```text
new persistent primitive
new descriptor grammar
new graph type
new retrieval branch
new sequence engine
```

---

# 93. SAFETY_FAIL

Use for lawful-realizable BTSR that violates:

```text
event budget
base isolation
candidate conservation
transition authority
OOD safety
streaming
determinism
SRA01
text/vision isolation
regression
```

---

# 94. EFFICACY_FAIL

Use when BTSR is safe but fails one or more:

```text
grounded path membership 17/17
parent L1 repair 3/3
new L1 failures 0
grounded L2 17/17
causal boundary support complete
positive grounded margins 17/17
CA1 grounded closure 4/4
CA2 grounded closure 13/13
sequence signal 20/20
```

---

# 95. PASS

`BTSR01_COUNTERFACTUAL_PASS` requires:

```text
structural selection validated
+
L3 grounded closure 17/17
+
all safety/integrity gates
```

PASS authorizes no production implementation.

---

# 96. Sequence Repair Authorization Logic

If:

```text
STRUCTURAL_SELECTION_VALIDATED = YES
```

and:

```text
POSITIVE GROUNDED CAUSAL MARGINS <17/17
```

then:

```text
SEQUENCE_DISCRIMINATION_REPAIR:
SCIENTIFICALLY JUSTIFIED
```

If:

```text
17/17 positive margins
```

then:

```text
SEQUENCE_DISCRIMINATION_REPAIR:
NOT JUSTIFIED
```

---

# 97. Required New Artifacts

In addition to v1.0 artifacts generate:

```text
fixed-stratum-map.json

grounded-causal-boundary-inventory.json

same-stratum-causal-collision-ledger.json

residual-fill-telemetry.json

periodicity-single-slot-displacement.json

bfar-vs-btsr-transition-topology.json

structural-selection-verdict.json
```

---

# 98. Required Final Metrics Additions

The final report must explicitly include:

```text
GROUNDED CAUSAL BOUNDARY DENOMINATOR:
N_G

FIXED STRATA:
8

CHANNELS PER STRATUM:
3

EVENT-DEPENDENT REPARTITION:
0

PERIODICITY-DEPENDENT REPARTITION:
0

EVENTS WITH SAME-STRATUM CAUSAL COLLISION:
<count>

COLLISIONS RECOVERED BY RESIDUAL FILL:
<count>

UNRECOVERED COLLISIONS:
<count>

EVENTS USING RESIDUAL FILL:
<count>

RESIDUAL-FILL SELECTED DESCRIPTORS:
<count>

PERIODICITY WINNER DISPLACEMENTS:
<count>

PERIODICITY CAUSAL WINNER DISPLACEMENTS:
<count>

BTSR_STRUCTURAL_SELECTION_VALIDATED:
YES / NO

RESIDUAL_SEQUENCE_DISCRIMINATION:
CONFIRMED_AFTER_SELECTION_REPAIR /
NOT_CONFIRMED /
NOT_APPLICABLE
```

---

# 99. Production Governance

Even if:

```text
BTSR01_COUNTERFACTUAL_PASS
```

return:

```text
PRODUCTION IMPLEMENTATION AUTHORIZED:
NO
```

PASS authorizes only:

```text
AUDIO_COMPOSITE_REPAIR_COUNTERFACTUAL
```

unless structural selection succeeds but L3 fails, in which case a narrow sequence-discrimination formal repair must occur first.

---

# 100. Expected Candidate Stack

```text
Raw Audio
   ↓
Audio v2
24-channel Stateful Sparse Temporal Frontend
   ↓
AEGR01
Event Granularity
   ↓
BTSR01
Fixed 8-Stratum Tonotopic Selection
   ↓
AEMG01
Parent-Equivalent Base Authority
   ↓
Existing Actual-Adjacency Sequence Structure
   ↓
Frozen LDSR / ASUR
   ↓
Cross-Modal Retrieval
```

---

# 101. Closure Questions

Before freezing v1.1, the final Closure Review MUST answer:

```text
Q1
Is fixed 8×3-channel stratification a sufficiently
bounded single hypothesis rather than an implicit family?

Q2
Does the periodicity reduction tie rule have any hidden
equivalent tuning freedom?

Q3
Is residual fill fully deterministic and incapable of
overwriting primary tonotopic coverage?

Q4
Is same-stratum collision telemetry sufficient to detect
the core failure mode without altering selection?

Q5
Is N_G fully resolved and immutable?

Q6
Can structural selector validation be legitimately
separated from full L3 validation?

Q7
Does 17/17 L3 remain the correct full component gate?

Q8
Can non-grounded telemetry cause any release-gate failure?

Q9
Are global Rank-1 requirements inherited correctly from
ATG01 rather than invented here?

Q10
Does any selector rule depend, even indirectly, on
cross-recording knowledge unavailable on first exposure?
```

---

# 102. Current Formal Status

```text
============================================================
DGCA PHASE 2.6 — BTSR01

FORMAL REPAIR SPECIFICATION:
v1.1 CANDIDATE

PARENT:
BFAR01_COUNTERFACTUAL_EFFICACY_FAIL

PARENT FORENSIC:
BFAR01_F01_FORENSIC_PASS

CLOSURE:
BFAR01_F01_C01_CLOSED_WITH_CLARIFICATIONS

REPAIR TARGET:
RANKED SELECTION MISALIGNMENT

PRIMARY HYPOTHESIS:
FIXED TONOTOPIC COVERAGE

SPECTRAL FRONTEND:
24 CHANNELS FROZEN

TONOTOPIC STRATA:
8 FIXED

CHANNELS / STRATUM:
3

EVENT-DEPENDENT REPARTITION:
FORBIDDEN

PERIODICITY-DEPENDENT REPARTITION:
FORBIDDEN

PERIODICITY EFFECT:
ONE BUDGET SLOT MAXIMUM

RESIDUAL FILL:
SECONDARY / FIXED

B_AUDIO_EVENT:
8 FROZEN

K_TRANSITION_GLOBAL_MAX:
1

GROUNDING-DERIVED RELATIONS:
17

NON-GROUNDED RELATIONS:
2

GROUNDED CAUSAL BOUNDARY DENOMINATOR:
MUST BE FROZEN BEFORE EXECUTION

STRUCTURAL SELECTION VERDICT:
MANDATORY

FULL L3 VALIDATION:
17/17 REQUIRED FOR PASS

NEW DESCRIPTORS:
0

NEW LEARNED PARAMETERS:
0

LABEL DEPENDENCE:
FORBIDDEN

HELDOUT DEPENDENCE:
FORBIDDEN

GRAPH-MEMORY DEPENDENCE:
FORBIDDEN

FORENSIC-ORACLE DEPENDENCE:
FORBIDDEN

LDSR:
FROZEN

ASUR:
FROZEN

PRODUCTION IMPLEMENTATION:
NOT AUTHORIZED

COUNTERFACTUAL EXECUTION:
NOT AUTHORIZED YET

NEXT REQUIRED ACTION:
BTSR01 v1.1
CLOSURE ADVERSARIAL FREEZE REVIEW
============================================================
```

## END OF FORMAL REPAIR SPECIFICATION