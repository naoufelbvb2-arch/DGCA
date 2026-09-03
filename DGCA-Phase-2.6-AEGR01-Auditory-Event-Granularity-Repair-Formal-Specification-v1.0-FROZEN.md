# DGCA Phase 2.6 — AEGR01
## Auditory Event Granularity Repair 01
## Formal Repair Specification v1.0

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Auditory Representation Repair  
**Repair ID:** `AEGR01` — Auditory Event Granularity Repair 01  
**Document Type:** Formal Repair Specification  
**Version:** 1.0  
**Status:** **FROZEN AFTER FREEZE REVIEW**

**Parent Forensics:** `ATGF01`  
**ATGF01 Forensic Commit:** `d48c76a`  
**Parent ATG01 Commit:** `7e43974`  
**Parent F01 Commit:** `74f788e`  
**Parent ARSR01 Counterfactual Commit:** `c3bf4dc`  
**Parent ARSR01 Implementation Commit:** `a26deb5`  
**Historical Cognitive Signature:** `915119d40643cb97`

**Authoritative Parent Verdict:** `EVENT_AGGREGATION`  
**Audio Reopening Authorization:** `REOPEN_AUDIO_EVENT_GRANULARITY`

**Audio Encoder v2 Frontend:** FROZEN  
**Event-Granularity Layer:** REOPENED FOR THIS REPAIR ONLY  
**Event Descriptor Compression:** FROZEN  
**AudioTemporalIR Schema:** FROZEN  
**Graph Persistence:** FROZEN  
**Grounding:** FROZEN  
**LESR / LDSR / IGSV:** FROZEN  
**Abstention:** FROZEN  
**DGCA Laws:** FROZEN

**New Persistent Primitive:** `0`  
**New Persistent Field:** `0`  
**New Law:** `0`  
**New Learned Scalar:** `0`  
**New Learned Threshold:** `0`  
**Semantic Segmentation:** `0`

---

# 1. Formal Repair Problem

ATGF01 established:

- frame temporal signal: `DEMONSTRATED`;
- event aggregation loss: `DEMONSTRATED`;
- descriptor compression loss: `DEMONSTRATED`;
- AudioTemporalIR loss: `NOT_DEMONSTRATED`;
- graph persistence loss: `NOT_DEMONSTRATED`.

The earliest causally sufficient loss is:

\[
\boxed{\textbf{EVENT\_AGGREGATION}}
\]

Parent Speech Commands behavior:

\[
68/70
\]

items become one monolithic event.

The repair target is therefore not new acoustic features.

The target is:

\[
\boxed{
\textbf{Expose already-existing frame-level acoustic regime changes as a sparse
ordered sequence of ordinary Audio v2 events.}
}
\]

---

# 2. Causal Isolation

AEGR01 modifies only internal event boundary formation.

It MUST NOT repair the demonstrated secondary descriptor-compression bottleneck
in the same intervention.

Binding:

\[
\boxed{
AEGR01 = EVENT\ GRANULARITY\ ONLY
}
\]

---

# 3. Frozen Production Chain

The repaired candidate chain is:

\[
RawAudio
\rightarrow
ExistingFrameFrontend
\rightarrow
ExistingFrameEvidence
\rightarrow
AEGR01BoundaryFormation
\rightarrow
ExistingAudioEvents
\rightarrow
ExistingDescriptorCompression
\rightarrow
ExistingAudioTemporalIR
\rightarrow
ExistingGraphSequence
\]

No new semantic stage.

---

# 4. Rejected Production Strategies

The following are forbidden:

- P2 fixed split;
- P4 fixed split;
- P8 fixed split;
- equal-duration production blocks;
- phoneme segmentation;
- syllable segmentation;
- ASR-driven boundaries;
- DTW;
- learned change-point detection;
- corpus-trained segmentation;
- word-specific boundaries.

ATGF01 P2/P4/P8 remain forensic evidence only.

---

# 5. One Boundary Rule Only

Freeze exactly one rule:

\[
\boxed{\textbf{B3 — EXISTING TRANSITION CANDIDATE + REGIME SEPARATION}}
\]

No novelty-only, turnover-only, or rule-family comparison is permitted.

---

# 6. Existing Frame Quantities

Use only:
- exact existing Audio v2 combined novelty \(D_t\);
- exact existing novelty baseline \(\mu_{t-1}\);
- existing frame descriptor identities for regime-support maps;
- existing absolute frame/sample anchors;
- existing valid/low-energy state.

No new acoustic feature extractor.

---

# 7. Existing Audio v2 Transition Candidate

AEGR01 does NOT invent a new novelty threshold or local-maximum policy.

Reuse the exact frozen Audio v2 transition-candidate rule:

\[
\boxed{
ExistingTransitionCandidate(t)
\iff
D_t\ge\max(0.25,\;2.5\mu_{t-1})
}
\]

with current frame containing lawful non-low-energy evidence.

The combined novelty remains exactly:

\[
D_t=0.7D^{spec}_t+0.3D^{eng}_t
\]

No coefficient or threshold changes.

---

# 8. Candidate Transition Eligibility

A transition \(t\) is eligible only if:
1. it lies inside an already-lawful current parent event;
2. `ExistingTransitionCandidate(t)` is true;
3. lawful non-empty evidence exists around the transition;
4. it is not the parent onset;
5. it is not the parent final offset;
6. complete local regime support exists on both sides.

---

# 9. Verified Existing Temporal Constants

Freeze Review verified from frozen Audio v2:

\[
\boxed{T_p=40\text{ ms}}
\]

remains frozen for periodicity analysis only and is NOT reused as a boundary parameter.

For AEGR01 regime support, freeze:

\[
\boxed{H=T_{ref}=20\text{ ms}}
\]

because \(T_{ref}\) is the existing Audio v2 minimum separation between independent event onsets and therefore belongs to event-boundary semantics.

Also conserved:

\[
\boxed{T_{event,min}=10\text{ ms}}
\]

\[
\boxed{T_{event,max}=1000\text{ ms}}
\]

AEGR01 introduces no new temporal scalar and does not borrow the unrelated periodicity horizon.

---

# 10. Left and Right Regime Windows

\[
L_t=[t-H,t),\qquad R_t=[t,t+H)
\]

using absolute frame anchors.

Internal low-energy gaps remain at original temporal positions.
Only valid existing frame evidence contributes.

---

# 11. Minimum Regime Evidence

Both \(L_t\) and \(R_t\) must contain at least two valid evidence-bearing frame anchors.

If either side is structurally insufficient:

`BOUNDARY_INELIGIBLE`.

---

# 12. Regime Support Maps

\[
A_L(d)=
\frac{\#\{\text{valid frames in }L_t\text{ containing }d\}}
{\#\{\text{valid frames in }L_t\}}
\]

\[
A_R(d)=
\frac{\#\{\text{valid frames in }R_t\text{ containing }d\}}
{\#\{\text{valid frames in }R_t\}}
\]

No descriptor threshold.

---

# 13. Weighted-Jaccard Support Similarity

\[
WJ(A,B)=
\frac{\sum_d\min(A_d,B_d)}
{\sum_d\max(A_d,B_d)}
\]

If both lack lawful descriptor support: `UNDEFINED_EMPTY`.

---

# 14. Within-Regime Consistency

\[
C_L(t)=\operatorname{mean}_{f\in L_t}WJ(f,A_L)
\]

\[
C_R(t)=\operatorname{mean}_{f\in R_t}WJ(f,A_R)
\]

over evidence-bearing frames only.

---

# 15. Across-Boundary Similarity

\[
X(t)=WJ(A_L,A_R)
\]

---

# 16. Regime Separation Margin

\[
\boxed{
R(t)=\min(C_L(t),C_R(t))-X(t)
}
\]

A positive margin means both sides are more internally coherent than mutually similar.

No learned threshold.

---

# 17. Frozen AEGR01 Boundary Candidate

\[
\boxed{
Candidate(t)=ExistingTransitionCandidate(t)\land[R(t)>0]
}
\]

No novelty local-maximum rule.
No descriptor-turnover local-maximum rule.
No weighted combination.
No threshold search.

---

# 18. Descriptor Turnover Is Diagnostic Only

AEGR01 MAY report:

\[
\delta_t=1-J(D^{frame}_{t-1},D^{frame}_{t})
\]

for telemetry, but \(\delta_t\) does NOT gate a production boundary.

---

# 19. Candidate Strength Tuple

\[
\boxed{
Strength(t)=(R(t),D_t,-time_t)
}
\]

Higher tuple wins lexicographically.
Earlier time is final exact tie-breaker.

---

# 20. Structural Anti-Chatter Rule

Accepted internal boundaries must satisfy:

\[
\boxed{|time_i-time_j|\ge H}
\]

Because:

\[
H=T_{ref}=20\text{ ms}
\]

the anti-chatter scale is exactly the frozen parent event-onset refractory scale.

No new refractory scalar.

---

# 21. Parent-Edge Protection

A boundary must have a complete \(H\)-sized regime-support window on both sides inside parent-event ownership.

No separate edge-duration scalar.

---

# 22. Candidate Conflict Resolution

Within each parent event:
1. enumerate lawful candidates;
2. sort by `Strength(t)` descending;
3. accept strongest;
4. reject remaining candidates within \(H\);
5. continue until none remain;
6. sort accepted boundaries by absolute time.

No event-count optimization.

---

# 23. Descriptor Budget Is Not an Event-Count Budget

Freeze Review verified:

\[
\boxed{B_{audio,event}=8}
\]

is the maximum descriptor count emitted for **one event**.

It is NOT a maximum number of events per recording.

AEGR01 MUST NOT repurpose it as an event-count cap.

---

# 24. Structural Event-Count Bound

AEGR01 introduces no fixed event-count hyperparameter.

For parent active duration \(L\), the \(H\)-window and \(H\)-separation rules imply:

\[
N_{boundary,max}(L)
=
\max\left(
0,
\left\lfloor\frac{L-2H}{H}\right\rfloor+1
\right)
\]

for \(L\ge2H\), else zero.

\[
N_{event,max}(L)=N_{boundary,max}(L)+1
\]

This is a derived bound, not a tunable target.

---

# 25. Existing Event Duration Semantics

Every resulting event conserves:
- no empty/fabricated event;
- \(T_{event,min}=10ms\);
- \(T_{event,max}=1000ms\) continuation semantics.

---

# 26. No Budgeted Candidate Truncation

There is no event-count budget and therefore no top-k boundary truncation.

Suppression occurs only through eligibility, \(R(t)>0\), \(H\)-conflict resolution, and parent ownership.

---

# 27. Boundary Timestamp

For accepted transition \(t\):

the boundary timestamp/sample anchor is the exact existing absolute frame-hop
anchor of the first frame on the right side of the transition.

Frames with anchors before the boundary belong to the left sub-event.

Frames with anchors at/after the boundary belong to the right sub-event.

No frame identity is duplicated across sub-events.

---

# 28. Parent Onset Conservation

The first resulting sub-event inherits the exact current parent-event onset.

AEGR01 does not alter onset detection.

---

# 29. Parent Offset Conservation

The final resulting sub-event inherits the exact current parent-event offset.

AEGR01 does not alter final offset detection.

---

# 30. Parent Event Ownership

Internal segmentation occurs only inside an event already formed lawfully by
current Audio v2 onset/offset semantics.

AEGR01 does not create acoustic evidence outside parent event ownership.

---

# 31. Delayed Commitment / Backdating Semantics

AEGR01 may evaluate an internal candidate only after the right-side horizon
\(R_t\) is observable.

Thus earliest causal commitment delay is:

\[
H
\]

The boundary itself is backdated to the frozen transition anchor.

Implementation may equivalently finalize all internal splits when the current
parent event closes.

This adds no semantic look-ahead beyond existing bounded event buffering.

---

# 32. Streaming Equivalence Requirement

Boundary identity depends on absolute frame anchors and completed local evidence,
not caller chunk boundaries.

Required future property:

\[
Boundaries(whole\ clip)
=
Boundaries(chunked\ stream)
\]

after lawful delayed commitment.

---

# 33. Event Construction

Accepted boundaries partition the parent event into ordinary Audio v2
sub-events.

No new event class.

No new persistent primitive.

---

# 34. Minimum Event Integrity

Every resulting sub-event must contain at least one valid evidence-bearing
frame.

No empty event.

No all-low-energy fabricated event.

---

# 35. Existing Descriptor Compression Conservation

Each resulting sub-event is passed through the exact current frozen event
descriptor compressor.

Required:

- same code;
- same top-k policy;
- same periodicity policy;
- same descriptor identity rules;
- same numeric constants.

AEGR01 may not retain additional descriptors inside an event.

---

# 36. Descriptor-Mass Consequence Is Observable, Not Hidden

Splitting one event into several events can lawfully increase the total number
of retained descriptors across the whole recording even when per-event
compression is unchanged.

This is a known consequence, not itself proof of temporal-order recovery.

Therefore counterfactual validation MUST isolate:

\[
OrderBenefit
\]

from:

\[
DescriptorMassBenefit
\]

---

# 37. AudioTemporalIR Conservation

The current AudioTemporalIR schema remains unchanged.

It receives a sequence of ordinary existing event objects.

No new field.

No subword flag.

No boundary confidence field.

---

# 38. Law 11 Conservation

Existing directional sequence observation remains unchanged.

If multiple events are emitted:

\[
E_1\rightarrow E_2\rightarrow\dots
\]

may be observed under existing Law 11 semantics.

No new transition law.

---

# 39. Grounding Conservation

Grounding procedure is unchanged.

Exact ATG01 grounding schedule and contexts remain unchanged.

Only auditory event granularity differs in counterfactual/implementation.

---

# 40. Retrieval Conservation

LESR, LDSR, IGSV, candidate discovery, commitment, abstention, and retrieval
semantics remain unchanged.

Any retrieval improvement must emerge from changed auditory representation only.

---

# 41. Counterfactual Before Source Modification

No Audio v2 source modification is authorized until a strict read-only
counterfactual simulation passes.

Counterfactual uses:

- exact ATGF01 frame telemetry;
- exact current event memberships;
- frozen B3 boundary rule;
- frozen existing compressor;
- frozen IR schema;
- isolated ephemeral graph replay where needed.

Production graph remains unchanged.

---

# 42. Counterfactual Dataset

Primary:

```text
40 ATG01 grounding
20 ATG01 held-out
10 ATG01 OOD
```

Exact parent files and speakers.

Secondary regression:

frozen SRA01 assets/artifacts required to evaluate event sparsity, determinism,
and streaming/chunk behavior where reconstructable.

No new data.

---

# 43. Ephemeral Diagnostic Graph

Counterfactual may create an isolated temporary graph solely to replay the exact
ATG01 grounding/retrieval protocol under simulated AEGR01 event output.

Binding:

- production graph mutation = 0;
- temporary graph discarded;
- grounding laws unchanged;
- retrieval unchanged;
- no extra exposure;
- no held-out learning.

This is diagnostic simulation, not production learning.

---

# 44. Counterfactual Baseline A0

A0:

current installed post-ARSR01 behavior with current Audio v2 eventization.

Required exact reproduction:

Held-out:
```text
0 correct /20
19 wrong /20
1 ambiguous /20
median correct rank 5.0
```

OOD:
```text
9 forced /10
1 ambiguous /10
```

Permutation:
```text
1/8 permuted target correct
1/8 natural target dominant
```

If A0 does not reproduce exactly:

```text
AEGR01_COUNTERFACTUAL_BLOCKED
```

---

# 45. Counterfactual Representation Condition A1

A1 uses simulated AEGR01 boundaries with:
- existing descriptor compression;
- existing AudioTemporalIR;
- exact grounding schedule;
- exact installed retrieval stack.

Because current production auditory→lexical retrieval is sequence-blind, A1
retrieval outcomes are mass/non-regression controls, not proof of order benefit.

---

# 46. Production Retrieval Cannot Be the Order-Efficacy Gate

F01/ASUR01 established `SEQUENCE UTILIZATION = ABSENT` in current lexical scoring.

Therefore AEGR01 must separate:
1. representation repair;
2. descriptor-mass effect under current retrieval;
3. downstream sequence-readiness under the already-frozen ASUR01 diagnostic scorer.

No production retrieval change is authorized.

---

# 47. Mass-Control Condition M0

M0 is the installed post-ARSR01 scorer operating on A1 multi-event output with no new sequence scorer.

It measures finer granularity plus extra descriptor mass retained across independently compressed events.

M0 is a safety/non-regression control, not temporal-order efficacy.

---

# 48. Frozen ASUR01 Downstream-Readiness Diagnostic D1

D1 applies the already-frozen ASUR01 mathematics read-only to the A1 ephemeral graph.

\[
W_{t,c}=|\Gamma_t\cap\Gamma_c|
\]

\[
\rho_Q(t,c)=\frac{W_{t,c}}{\sum_{k\in C_Q}W_{t,k}}
\]

\[
SeqLDSR_Q(t,c)=
\max\left(0,\rho_Q(t,c)-\frac1{N_Q}\right)
\]

No residual renormalization.

D1 combines this sequence contribution with the frozen post-ARSR01 base score
for diagnostic evaluation only.

This does NOT implement ASUR01.

---

# 49. Sequence-Blind Diagnostic D0

D0 uses the same A1 multi-event representation, same descriptor mass, candidate
set and base scorer as D1, but:

\[
S_{seq}=0
\]

Thus:

\[
D1-D0
\]

isolates the value of newly exposed directional sequence evidence without
descriptor-mass confounding.

---

# 50. Reversal Diagnostic D2

For held-out diagnostics:
- preserve identical simulated events/descriptors;
- reverse only directional event order;
- recompute frozen ASUR01 sequence evidence;
- do not relearn grounding.

D2 tests direction sensitivity.

---

# 51. Boundary Simulation Telemetry

For all 70 ATG01 items record:
- parent event count;
- existing transition-candidate count;
- regime-qualified candidate count;
- accepted internal boundaries;
- final simulated events;
- boundary timestamps;
- \(D_t\), \(\mu_{t-1}\);
- optional diagnostic \(\delta_t\);
- \(C_L,C_R,X,R\);
- rejection reasons;
- H-conflict suppression.

No event-budget truncation.

---

# 52. Boundary Coverage Metrics

Report separately for 40 grounding, 20 held-out, 10 OOD.

Held-out:
- multi-event queries /20;
- queries with >=1 Law11-eligible directional transition /20.

---

# 53. Sequence Support Reconstruction

Under isolated grounding replay report:
- correct concept sequence support /20;
- wrong concept sequence support;
- transition fanout;
- grounding contexts.

Use exact frozen ASUR01 context-intersection semantics.

---

# 54. Structural Coverage Gates

Required:

\[
\boxed{MultiEventHeldout\ge12/20}
\]

\[
\boxed{CorrectConceptSequenceSupport\ge10/20}
\]

---

# 55. Sparsity / Structural-Bound Gate

For every parent event:
- accepted boundaries obey H separation;
- each boundary has complete H support;
- final event count obeys derived structural bound;
- all events obey frozen event integrity.

No fixed event-count cap.

Report median/p90/max event counts for ATG01 and SRA01.

---

# 56. Boundary Stability Gate

Repeated identical simulation must produce identical boundaries for 70/70 ATG01 and all tested SRA01 items.

---

# 57. Chunk-Equivalence Counterfactual Gate

Reuse frozen Audio v2 chunk-equivalence test families.

Required: identical boundary sets after lawful delayed commitment.

---

# 58. Event Descriptor Compression Conservation Gate

Every simulated sub-event uses exact frozen compression, including:

\[
B_{audio,event}=8
\]

as a per-event descriptor ceiling only.

No compressor policy or constant changes.

---

# 59. Descriptor-Mass Audit

Report parent retained-descriptor total vs simulated multi-event retained total.

Any increase is `DESCRIPTOR_MASS_OR_GRANULARITY_EFFECT`, not sequence-order proof.

---

# 60. Sequence-Readiness Directional Gate

D1 must pass ALL:

### Q1 — Positive Correct Sequence Evidence

\[
PositiveCorrectSequenceContribution\ge10/20
\]

### Q2 — Correct Sequence Advantage

At least:

\[
6/20
\]

held-out probes satisfy:

\[
S_{seq}(correct)>S_{seq}(strongest\ wrong\ candidate\ under\ D0)
\]

### Q3 — Direction Sensitivity

For at least:

\[
6/20
\]

held-out probes with non-empty sequence evidence, D2 reversal reduces correct
sequence margin or changes directional sequence ranking against the correct concept.

---

# 61. Frozen ASUR01 Downstream-Readiness Outcome Gate

Require at least one:

### E1
\[
D1HeldoutCorrect\ge2/20
\]

### E2
\[
D1PermutedTargetCorrect\ge3/8
\]

This is diagnostic readiness, not production retrieval behavior.

---

# 62. Frozen ASUR01 Supporting Gate

Require at least one:

### E3
\[
D1MedianCorrectRank\le4.0
\]

### E4
At least `6/20` held-out probes improve correct rank D0→D1, with <=2 worsening by >1 rank.

### E5
Q2 correct-sequence advantage reaches `8/20`.

---

# 63. Current Retrieval / Descriptor-Mass Non-Regression

M0 is safety only.

Required:
- held-out wrong <= parent `19/20`;
- median correct rank <= parent `5.0`;
- OOD forced <= `9/10`;
- natural-target dominance <= `2/8`;
- reverse Text→Audio wrong-dominant = 0.

---

# 64. Event-Order Reversal Interpretation

D2 is diagnostic only.

A viable AEGR01 representation must not remain directionally invariant after D1 sequence-readiness scoring.

No production Law 11 or retrieval change.

---

# 65. SRA01 Regression Requirements

Read-only counterfactual and later implementation must evaluate frozen SRA01
behavior.

Required:

- no fabricated silence;
- deterministic replay;
- event count obeys the derived H-based structural bound and frozen event integrity;
- order probes remain distinguishable;
- mixture evidence does not regress catastrophically;
- chunk equivalence is preserved or predicted exactly by the frozen rule.

Formal counterfactual must report all available frozen SRA01 checks.

---

# 66. Vision and Text Isolation

AEGR01 cannot alter Vision or text-only behavior.

No shared retrieval change is authorized.

---

# 67. Production Graph Mutation in Counterfactual

Required:

\[
\Delta PersistentGraph=0
\]

The isolated diagnostic graph does not count as production mutation and must be
discarded after simulation.

---

# 68. Counterfactual Safety Gates

All required:

S1 Parent lineage/data exact.  
S2 A0 reproduced exactly.  
S3 Production graph mutation = 0.  
S4 Frozen B3 rule used; no rule search.  
S5 Exact frozen Audio v2 transition-candidate equation reused.  
S6 No labels/speaker identity in boundary formation.  
S7 Frontend/frame evidence/novelty computation unchanged.  
S8 Existing onset/final-offset semantics preserved.  
S9 No empty/fabricated events.  
S10 H-based structural separation/bound PASS all items.  
S11 Boundary determinism 70/70.  
S12 Chunk-equivalence counterfactual PASS.  
S13 Descriptor compression unchanged; \(B_{audio,event}=8\) remains descriptor ceiling only.  
S14 AudioTemporalIR/grounding/production retrieval/Law11 unchanged.  
S15 M0 current-retrieval non-regression PASS.  
S16 SRA01 regression counterfactual PASS.

Required:

\[
\boxed{16/16\ PASS}
\]

---

# 69. Counterfactual Authorization Logic

ImplementationAuthorized = YES iff ALL:

1. S1–S16 PASS;
2. `MultiEventHeldout >=12/20`;
3. `CorrectConceptSequenceSupport >=10/20`;
4. Q1–Q3 PASS;
5. at least one D1 outcome signal E1/E2 PASS;
6. at least one D1 supporting signal E3/E4/E5 PASS;
7. 36/36 invariants PASS;
8. 36/36 forbidden mechanisms PASS.

Current production retrieval improvement is NOT required because production
auditory lexical scoring is sequence-blind.

Otherwise `IMPLEMENTATION_AUTHORIZED = NO`.

---

# 70. Counterfactual Verdicts

Allowed:
- `AEGR01_COUNTERFACTUAL_PASS`
- `AEGR01_PREIMPLEMENTATION_REJECTED`
- `AEGR01_COUNTERFACTUAL_SAFETY_FAIL`
- `AEGR01_COUNTERFACTUAL_BLOCKED`

---

# 71. PASS Rule

PASS only if full authorization logic passes.

Even on PASS, do not modify Audio v2 source in the counterfactual task.

---

# 72. PREIMPLEMENTATION_REJECTED Rule

Use if safe/reconstructable but structural coverage, Q1–Q3, D1 outcome readiness,
or D1 supporting readiness fails.

---

# 73. SAFETY_FAIL Rule

Use if any S1–S16 fails.

---

# 74. BLOCKED Rule

Use if parent frame telemetry, 40ms horizon, 20ms refractory/event-duration
semantics, exact transition-candidate equation, compressor, A0, isolated replay,
or SRA01 regression evidence cannot be reconstructed.

Do NOT block because no event-count budget exists: Freeze Review established
that \(B_{audio,event}=8\) is a descriptor ceiling, not an event-count budget.

---

# 75. Implementation Scope If Later Authorized

Only after counterfactual PASS may implementation modify the minimal Audio v2
event-granularity code needed to:

- reuse the exact existing Audio v2 transition-candidate signal;
- evaluate 20 ms regime support using frozen T_ref;
- apply R(t)>0;
- resolve H-conflicting candidates;
- backdate internal boundaries;
- partition existing parent events.

No other source changes are authorized.

---

# 76. Exact Validation After Future Implementation

Future implementation must repeat:

- exact ATG01 70-item trial;
- exact 40 grounding schedule;
- exact held-out/OOD;
- permutation control;
- reverse control;
- SRA01 regression;
- determinism;
- chunk equivalence;
- graph persistence checks;
- historical signature governance.

---

# 77. Full Repair Verification Targets

R1 Implementation matches frozen counterfactual.  
R2 Frontend/novelty/compression identities unchanged.  
R3 Multi-event held-out coverage >=12/20.  
R4 Correct concept sequence support >=10/20.  
R5 Q1–Q3 sequence-readiness gates reproduced.  
R6 D1 retains at least one E1/E2 outcome-readiness signal.  
R7 D1 retains at least one E3/E4/E5 supporting signal.  
R8 M0 production retrieval non-regression.  
R9 OOD/permutation/reverse safety pass.  
R10 H-based structural sparsity bound pass.  
R11 Determinism + chunk equivalence PASS.  
R12 SRA01 regression PASS.

These targets do not authorize implementation yet.

---

# 78. Descriptor Compression Remains Deferred

If AEGR01 later succeeds but residual retrieval remains limited, ATGF01's
secondary descriptor-compression loss may become a separate repair candidate.

It must not be silently folded into AEGR01.

---

# 79. Mathematical Property Tests

M01 Existing combined novelty equation/range match frozen Audio v2.  
M02 Existing transition-candidate equation reproduces exactly:
\[
D_t\ge\max(0.25,2.5\mu_{t-1})
\]
M03 Regime support fractions in [0,1].  
M04 Weighted Jaccard in [0,1].  
M05 Within consistency in [0,1].  
M06 Across similarity in [0,1].  
M07 \(-1\le R(t)\le1\).  
M08 Candidate requires existing transition candidate AND \(R(t)>0\).  
M09 No boundary from empty/insufficient regime evidence.  
M10 No new novelty or turnover threshold exists.  
M11 Accepted boundaries separated by >=H.  
M12 H>T_ref conserves current refractory.  
M13 Parent onset/offset conserved.  
M14 No frame membership duplication.  
M15 Conflict resolution deterministic after canonical sort.  
M16 Identical frame stream -> identical boundary set.

---

# 80. Architectural Invariants

### AEGR01-INV-01
ERB frontend unchanged.

### AEGR01-INV-02
IHC unchanged.

### AEGR01-INV-03
Adaptation unchanged.

### AEGR01-INV-04
Frame width/hop/phase unchanged.

### AEGR01-INV-05
Frame descriptor identities unchanged.

### AEGR01-INV-06
Existing novelty computation unchanged.

### AEGR01-INV-07
Periodicity computation/horizon unchanged.

### AEGR01-INV-08
Energy evidence unchanged.

### AEGR01-INV-09
Only event granularity reopened.

### AEGR01-INV-10
Onset semantics unchanged.

### AEGR01-INV-11
Final offset semantics unchanged.

### AEGR01-INV-12
Descriptor compression unchanged.

### AEGR01-INV-13
AudioTemporalIR schema unchanged.

### AEGR01-INV-14
Graph persistence schema unchanged.

### AEGR01-INV-15
Grounding unchanged.

### AEGR01-INV-16
Retrieval unchanged.

### AEGR01-INV-17
Law 11 unchanged.

### AEGR01-INV-18
No new persistent primitive.

### AEGR01-INV-19
No new persistent field.

### AEGR01-INV-20
No new Law.

### AEGR01-INV-21
No new learned/hand-tuned threshold or scalar; frozen Audio v2 novelty thresholds reused unchanged.

### AEGR01-INV-22
No semantic label in boundary formation.

### AEGR01-INV-23
No speaker identity in boundary formation.

### AEGR01-INV-24
P2/P4/P8 not used as production segmentation.

### AEGR01-INV-25
H=T_ref=20ms uses frozen event-boundary semantics; T_p=40ms remains periodicity-only.

### AEGR01-INV-26
B_audio,event=8 remains descriptor ceiling only; no event-count budget invented.

### AEGR01-INV-27
No empty/fabricated event.

### AEGR01-INV-28
Boundary determinism.

### AEGR01-INV-29
Streaming/chunk equivalence preserved under delayed H-window commitment.

### AEGR01-INV-30
No frame-level token explosion.

### AEGR01-INV-31
Descriptor-mass confound measured separately from frozen-ASUR01 sequence readiness.

### AEGR01-INV-32
D0/D1/D2 sequence-readiness diagnostics required without production retrieval modification.

### AEGR01-INV-33
Exact parent data retained.

### AEGR01-INV-34
Production graph unchanged during counterfactual.

### AEGR01-INV-35
Failures retained and reported.

### AEGR01-INV-36
Descriptor-compression repair remains separate.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 81. Forbidden Mechanisms

1. Phoneme model.  
2. Syllable model.  
3. ASR.  
4. DTW.  
5. Forced alignment.  
6. Learned change-point model.  
7. Neural segmentation model.  
8. Speaker embedding.  
9. Word-specific boundary.  
10. Class-specific boundary.  
11. Label-dependent threshold.  
12. P2 production split.  
13. P4 production split.  
14. P8 production split.  
15. Equal-duration production segmentation.  
16. Corpus-derived boundary frequency.  
17. Learned novelty threshold.  
18. New turnover threshold or turnover-local-max boundary gate.  
19. Post-hoc held-out threshold search.  
20. New persistent MicroEvent.  
21. New persistent SubwordEvent.  
22. New persistent PhonemeEvent.  
23. New Law.  
24. Descriptor-compression repair.  
25. IGSV repair.  
26. Abstention repair.  
27. Grounding change.  
28. Retrieval-rule change.  
29. Global audio statistic or invented event-count budget.  
30. Event-count target learned from labels.  
31. Source/data replacement.  
32. New training audio.  
33. Augmentation.  
34. Failure-probe deletion.  
35. Hidden parameter/rule search or novelty local-maximum rule replacing frozen transition-candidate semantics.  
36. Claiming discovered linguistic units.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 82. Formal Release Gates

### AEGR01-G01
Parent ATGF01 causal verdict and lineage verified.

### AEGR01-G02
Frozen novelty equation, transition-candidate thresholds, T_p=40ms periodicity-only, T_ref=20ms boundary horizon, event durations, and descriptor ceiling audited.

### AEGR01-G03
Existing 40 ms temporal horizon verified.

### AEGR01-G04
B_audio,event=8 verified as descriptor ceiling; absence of event-count budget recorded.

### AEGR01-G05
B3 = ExistingTransitionCandidate AND R(t)>0 frozen.

### AEGR01-G06
Candidate eligibility frozen.

### AEGR01-G07
Regime support construction frozen.

### AEGR01-G08
Exact existing Audio v2 transition-candidate semantics frozen; no new local-maximum gate.

### AEGR01-G09
Anti-chatter/conflict rule frozen.

### AEGR01-G10
Boundary timestamp/backdating frozen.

### AEGR01-G11
Parent onset/final offset conservation frozen.

### AEGR01-G12
Existing compressor conservation frozen.

### AEGR01-G13
AudioTemporalIR/Law11 compatibility frozen.

### AEGR01-G14
A0 baseline reproduction complete.

### AEGR01-G15
Read-only boundary counterfactual complete 70/70.

### AEGR01-G16
Structural coverage gates pass.

### AEGR01-G17
H-based structural sparsity/event-integrity gate pass.

### AEGR01-G18
Determinism/chunk-equivalence counterfactual pass.

### AEGR01-G19
A1 exact isolated replay complete.

### AEGR01-G20
D0 sequence-blind + D1 frozen-ASUR01 readiness diagnostics complete.

### AEGR01-G21
D2 directional reversal diagnostic complete.

### AEGR01-G22
Q1-Q3 sequence-readiness directional gates pass.

### AEGR01-G23
D1 frozen-ASUR01 outcome readiness E1/E2 pass.

### AEGR01-G24
D1 supporting readiness E3/E4/E5 pass.

### AEGR01-G25
M0 + OOD/permutation/reverse non-regression controls pass.

### AEGR01-G26
SRA01 regression counterfactual complete.

### AEGR01-G27
36/36 invariants + 36/36 forbidden PASS.

### AEGR01-G28
Historical signature governance + no production mutation PASS.

Full counterfactual authorization requires all applicable gates through G28,
including authorization logic in Section 69.

---

# 83. Required Counterfactual Artifacts

Produce:

```text
AEGR01-EVENT-GRANULARITY-COUNTERFACTUAL-REPORT.md

aegr01_lineage.json
aegr01_source_constant_audit.json
aegr01_boundary_math_tests.json
aegr01_boundary_candidates.jsonl
aegr01_regime_support.jsonl
aegr01_boundary_resolution.jsonl
aegr01_eventization_70.jsonl
aegr01_structural_sparsity_summary.json
aegr01_determinism.json
aegr01_chunk_equivalence.json

aegr01_compression_conservation.jsonl
aegr01_descriptor_mass_audit.jsonl
aegr01_ir_conservation.json
aegr01_law11_sequence_coverage.json

aegr01_A0_baseline.json
aegr01_M0_current_retrieval_heldout.jsonl
aegr01_M0_current_retrieval_ood.jsonl
aegr01_M0_current_retrieval_permutation.jsonl
aegr01_M0_current_retrieval_reverse.jsonl

aegr01_D0_sequence_blind_diagnostic.jsonl
aegr01_D2_reversal_diagnostic.jsonl
aegr01_D1_frozen_asur01_readiness.jsonl

aegr01_sra01_regression.json
aegr01_safety_gates.json
aegr01_coverage_gates.json
aegr01_efficacy_gates.json
aegr01_invariants.json
aegr01_forbidden.json
aegr01_release_gates.json
aegr01_counterfactual_verdict.json
aegr01_failures.jsonl
```

---

# 84. Required Counterfactual Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — AEGR01
PRE-IMPLEMENTATION EVENT-GRANULARITY COUNTERFACTUAL

PARENT ATGF01 COMMIT:
d48c76a

HISTORICAL SIGNATURE:
915119d40643cb97

EXECUTION MODE:
STRICT_READ_ONLY_COUNTERFACTUAL

AUDIO V2 SOURCE CHANGES:
0 / NONZERO

PRODUCTION GRAPH MUTATION:
0 / NONZERO

BOUNDARY RULE:
EXISTING_TRANSITION_CANDIDATE_AND_REGIME_SEPARATION

FROZEN NOVELTY CANDIDATE:
D >= max(0.25, 2.5 * baseline)
MATCH / MISMATCH

PERIODICITY HORIZON:
40 ms — FROZEN / MISMATCH

REGIME / EVENT-REFRACTORY HORIZON:
20 ms — MATCH / MISMATCH

PER-EVENT DESCRIPTOR CEILING:
8 — MATCH / MISMATCH

EVENT-COUNT BUDGET:
NONE / INCORRECTLY_INVENTED

A0 BASELINE:
MATCH / MISMATCH

ATG01 ITEMS SIMULATED:
... /70

GROUNDING MULTI-EVENT:
... /40

HELD-OUT MULTI-EVENT:
... /20

OOD MULTI-EVENT:
... /10

CORRECT CONCEPT SEQUENCE SUPPORT:
... /20

H-BASED STRUCTURAL SPARSITY:
PASS / FAIL

BOUNDARY DETERMINISM:
... /70

CHUNK EQUIVALENCE:
PASS / FAIL

M0 CURRENT RETRIEVAL:
HELDOUT CORRECT ... /20
HELDOUT WRONG ... /20
MEDIAN CORRECT RANK ...
OOD FORCED ... /10
NATURAL TARGET DOMINANT ... /8
REVERSE WRONG ... /10
NON-REGRESSION PASS / FAIL

D0 SEQUENCE-BLIND:
CORRECT ... /20
MEDIAN CORRECT RANK ...

D1 FROZEN-ASUR01 READINESS:
CORRECT ... /20
MEDIAN CORRECT RANK ...
PERMUTED CORRECT ... /8

Q1 POSITIVE CORRECT SEQUENCE:
... /20 — PASS / FAIL

Q2 CORRECT SEQUENCE ADVANTAGE:
... /20 — PASS / FAIL

Q3 DIRECTION SENSITIVITY:
... /20 — PASS / FAIL

D1 OUTCOME READINESS:
E1 PASS/FAIL
E2 PASS/FAIL

D1 SUPPORTING READINESS:
E3 PASS/FAIL
E4 PASS/FAIL
E5 PASS/FAIL

D2 REVERSAL:
DIRECTIONAL EFFECT DEMONSTRATED / NOT_DEMONSTRATED

SRA01 REGRESSION:
PASS / FAIL / BLOCKED

SAFETY GATES:
... /16

STRUCTURAL COVERAGE:
PASS / FAIL

SEQUENCE-READINESS DIRECTIONAL GATES:
PASS / FAIL

AEGR01 INVARIANTS:
... /36

FORBIDDEN MECHANISMS:
... /36

FINAL COUNTERFACTUAL VERDICT:
AEGR01_COUNTERFACTUAL_PASS /
AEGR01_PREIMPLEMENTATION_REJECTED /
AEGR01_COUNTERFACTUAL_SAFETY_FAIL /
AEGR01_COUNTERFACTUAL_BLOCKED

IMPLEMENTATION AUTHORIZED:
YES / NO
============================================================
```

---

# 85. Formal Status

\[
\boxed{
\textbf{AEGR01 — Auditory Event Granularity Repair 01}
}
\]

\[
\boxed{
\textbf{Formal Repair Specification v1.0 — COMPLETE}
}
\]

Status:

```text
FROZEN AFTER FREEZE REVIEW AMENDMENTS
```

Next authorized action: strict read-only AEGR01 counterfactual execution.
No Audio v2 source modification is authorized until that counterfactual returns
`AEGR01_COUNTERFACTUAL_PASS` and `IMPLEMENTATION_AUTHORIZED=YES`.
