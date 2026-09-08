# DGCA Phase 2.6 — ADCAR01

## Auditory Descriptor Compression Aliasing Repair 01

# Formal Repair Specification v1.1 — CANDIDATE

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6  
**Repair ID:** `ADCAR01`  
**Full Name:** Auditory Descriptor Compression Aliasing Repair 01  
**Document Type:** Formal Repair Specification  
**Version:** `1.1`  
**Status:** `CANDIDATE — NOT FROZEN`

**Parent Forensics:** `AEGR01-F01`  
**Validated Upstream Component:** `AEMG01_COUNTERFACTUAL_PASS`  
**AEMG01 Execution Commit:** `6fd2157`

**Historical Cognitive Signature:** `915119d40643cb97`

**Production Implementation:** `NOT AUTHORIZED`  
**Counterfactual Execution:** `NOT AUTHORIZED YET`

---

# 1. Repair Target

ADCAR01 targets exactly:

```text
DESCRIPTOR_COMPRESSION_ALIASING
```

inside the auditory child-event sequence representation.

It does NOT reopen:

```text
Audio v2 frontend
AEGR01 event boundaries
AEMG01 lexical authority
Parent grounding transactions
Candidate discovery
LESR
LDSR
ASUR01 mathematics
Law 11
Commitment
Abstention
Persistent graph schema
```

---

# 2. Frozen Causal Basis

AEGR01-F01 established:

```text
CA1 LARGE REGRESSIONS:
5/5 compression-alias traced

CA2 Q2 FAILURES:
13/14 compression-alias traced
```

The causal sequence is:

```text
precompression acoustic support
        ↓
specificity favors correct concept
        ↓
event descriptor compression
        ↓
distinct acoustic profiles collapse
        ↓
generic / shared transitions
        ↓
wrong SeqLDSR support
```

Therefore the repair target remains:

```text
EVENT DESCRIPTOR COMPRESSION
/
SEQUENCE IDENTITY
```

---

# 3. Core Scientific Hypothesis

ADCAR01 tests:

\[
\boxed{
Discarded\ precompression\ acoustic\ specificity
\ can\ be\ retained\ in\ a\ bounded,\ deterministic,
\ sequence-only\ event\ identity
}
\]

such that:

\[
\boxed{
AEMG01\ base\ authority
\ remains\ unchanged
}
\]

and:

\[
\boxed{
compression-induced\ sequence\ aliasing
\ decreases
}
\]

without learned parameters or new persistent cognitive state.

---

# 4. BCAP Candidate

Define:

```text
BCAP
Bounded Conjunctive Acoustic Profile
```

as a candidate event-level sequence identity derived solely from already-existing precompression Audio v2 acoustic support.

BCAP does NOT introduce new acoustic measurements.

---

# 5. Existing Acoustic Inputs Only

Authorized inputs:

```text
existing spectral band support
existing periodicity support
existing validity masks
existing deterministic event aggregation
```

Forbidden new inputs:

```text
phoneme label
concept label
speaker ID
file ID
recording index
dataset split
OOD status
learned embedding
external ASR
```

---

# 6. Precompression Spectral Profile

For event \(E\), let:

\[
S_E^{spec}(b)
\]

be the already-existing precompression support for spectral band \(b\).

Construct:

\[
\Pi_{spec}(E)
\]

using:

1. all existing valid spectral identities;
2. descending existing support;
3. canonical band index as deterministic tie-break.

---

# 7. Precompression Periodicity Profile

Likewise construct:

\[
\Pi_{per}(E)
\]

from all valid existing periodicity identities using:

1. descending support;
2. canonical periodicity index tie-break.

No new threshold.

No new quantization.

---

# 8. BCAP v1.1 Representation

Candidate:

\[
BCAP(E)
=
CanonicalConjunction(
\Pi_{spec}(E),
\Pi_{per}(E)
)
\]

The candidate preserves:

```text
descriptor membership
+
relative support ordering
+
spectral/periodicity conjunction
```

It does NOT preserve raw floating-point magnitude.

---

# 9. Rank-Only Status

Rank-only representation is a hypothesis, NOT a frozen fact.

Therefore ADCAR01 v1.1 requires a mandatory separability preflight before efficacy evaluation.

No PASS is permitted merely because BCAP was constructible.

---

# 10. PRECOMPRESSION REPRESENTATION SEPARABILITY AUDIT

For every exact frozen compression-alias witness, classify the precompression distinction as exactly one of:

```text
IDENTITY_SET_DIFFERENCE

RANK_ORDER_DIFFERENCE

MAGNITUDE_ONLY_DIFFERENCE

TRUE_PRECOMPRESSION_PROFILE_COLLISION

INCONCLUSIVE
```

---

# 11. BCAP Applicability Rule

BCAP v1.1 is structurally capable of separating a witness only if:

```text
IDENTITY_SET_DIFFERENCE
```

or:

```text
RANK_ORDER_DIFFERENCE
```

is present.

If any mandatory CA1 witness is:

```text
MAGNITUDE_ONLY_DIFFERENCE
```

or:

```text
TRUE_PRECOMPRESSION_PROFILE_COLLISION
```

then:

```text
BCAP_REPRESENTATION_INSUFFICIENT
```

and ADCAR01 v1.1 cannot PASS.

Do not add magnitude quantization during the same execution.

---

# 12. Descriptor Budget Non-Laundering Principle

BCAP MUST NOT evade the frozen auditory descriptor budget by hiding arbitrary independent evidence inside one serialized token.

The counterfactual must determine the exact architectural meaning of:

\[
B_{audio,event}=8
\]

before BCAP is considered lawful.

---

# 13. DESCRIPTOR_BUDGET_NON_LAUNDERING_GATE

Audit existing Audio/DGCA semantics and classify the budget as one of:

```text
A
GRAPH-FACING DESCRIPTOR COUNT BOUND

B
INDEPENDENT COGNITIVE INFORMATION COMPONENT BOUND

C
SEMANTICS AMBIGUOUS
```

---

# 14. Budget Case A

If the existing architecture already permits conjunctive categorical identities as one lawful descriptor and internal tuple members are not independently retrievable/weighted as graph evidence:

```text
BCAP BUDGET COMPATIBILITY:
POSSIBLE
```

The execution must still prove no hidden independent evidence channels exist.

---

# 15. Budget Case B

If the budget limits the amount of independent acoustic information exposed per event rather than syntactic node count:

packing a full 24+6 ordering into one identity is prohibited.

Verdict:

```text
ADCAR01_PREIMPLEMENTATION_REJECTED
```

for BCAP v1.1.

---

# 16. Budget Case C

If frozen architecture does not permit a definitive interpretation:

```text
ADCAR01_COUNTERFACTUAL_BLOCKED
```

Reason:

```text
DESCRIPTOR_BUDGET_SEMANTICS_UNRESOLVED
```

Do not choose the interpretation that helps BCAP pass.

---

# 17. BCAP Identity Grammar Compatibility

Create:

```text
BCAP_IDENTITY_GRAMMAR_COMPATIBILITY_AUDIT
```

Verify that existing current-schema DGCA signal identity machinery can represent BCAP without:

```text
new node type
new edge type
new persistent field
new modality
new parser semantics
new retrieval branch
new Law
```

Required:

```text
NEW_PERSISTENT_PRIMITIVE = 0

NEW_PERSISTENT_FIELD = 0

NEW_SIGNAL_SCHEMA = 0

SPECIAL_RETRIEVAL_SEMANTICS = 0
```

---

# 18. Identity Grammar Failure

If BCAP requires any new persistent semantic type:

```text
ADCAR01_PREIMPLEMENTATION_REJECTED
```

A serialized string is NOT sufficient proof of compatibility.

Semantic compatibility must be established.

---

# 19. No Raw Frame Persistence

Forbidden:

```text
raw waveform nodes
per-frame spectral nodes
per-frame periodicity nodes
floating-point frame vector persistence
frame-history cognitive storage
```

BCAP remains event-level.

---

# 20. No Unbounded Descriptor Retention

Forbidden:

```text
retain every discarded descriptor
as an independent graph-facing signal
```

ADCAR01 is a compression repair, not compressor removal.

---

# 21. Exact Frozen Alias Witness Inventories

Load exact F01 witness sets:

\[
\mathcal A_{CA1}
\]

and:

\[
\mathcal A_{CA2}
\]

from frozen forensic artifacts.

Do NOT assume:

```text
5 probes = 5 arbitrary pairs
13 probes = 13 arbitrary pairs
```

The exact traced transition/profile witnesses are authoritative.

---

# 22. CA1 Inventory Gate

Required:

```text
CA1 FROZEN PROBES:
5/5 reproduced

CA1 EXACT WITNESS INVENTORY:
100% reproduced
```

No witness may be omitted or replaced.

---

# 23. CA2 Inventory Gate

Required:

```text
CA2 FROZEN PROBES:
13/13 reproduced

CA2 EXACT WITNESS INVENTORY:
100% reproduced
```

Let:

\[
N_{CA2}=|\mathcal A_{CA2}|
\]

be measured from artifacts.

No hardcoded witness count beyond frozen probe count.

---

# 24. Causal Witness Concordance

For every frozen alias witness identify the precompression feature difference responsible for the previously observed correct-vs-wrong specificity advantage.

Classify BCAP preservation as:

```text
CAUSAL_WITNESS_PRESERVED

ALIAS_BROKEN_BY_NONCAUSAL_TAIL_DIFFERENCE

MAGNITUDE_WITNESS_LOST

TRUE_PROFILE_COLLISION

INCONCLUSIVE
```

Only:

```text
CAUSAL_WITNESS_PRESERVED
```

supports the strong ADCAR01 causal claim.

---

# 25. No Tail-Noise Success

A witness is NOT considered causally repaired merely because:

\[
BCAP(E_a)\neq BCAP(E_b)
\]

If the distinguishing tuple component did not contribute to the F01 precompression specificity relation, classify:

```text
ALIAS_BROKEN_BY_NONCAUSAL_TAIL_DIFFERENCE
```

This does not count toward the causal repair gate.

---

# 26. Topology Confound

BCAP changes sequence endpoint structure from:

```text
multiple coarse descriptors/event
```

to:

```text
one conjunctive identity/event
```

Therefore improvement relative to current R0 alone cannot establish recovered specificity as the cause.

---

# 27. R0C — Coarse Conjunctive Topology Control

Define:

```text
CCAP
Coarse Conjunctive Acoustic Profile
```

For event \(E\):

\[
CCAP(E)
=
CanonicalTuple(C(E))
\]

using ONLY descriptors already retained by the frozen current event compressor.

No discarded precompression support may enter CCAP.

---

# 28. R0C Purpose

R0C has:

```text
one conjunctive identity/event
```

like R1 BCAP.

Therefore:

```text
R0 → R0C
```

isolates:

```text
TOPOLOGY / CONJUNCTION EFFECT
```

while:

```text
R0C → R1
```

isolates:

```text
RECOVERED PRECOMPRESSION SPECIFICITY EFFECT
```

---

# 29. R0C Is Diagnostic Only

CCAP is NOT a production repair candidate.

It cannot authorize implementation.

Its only role is causal control.

---

# 30. Experimental Conditions

Use exactly:

```text
P
Historical Parent base reference.

B
Validated AEMG01 + AEGR01 coarse sequence reference.

R0
Exact current governed coarse sequence baseline.

R0C
Topology-matched coarse conjunction control.

R1
BCAP precompression-specificity representation.

R2
R1 reversed-order diagnostic.

R3
Frozen alias-witness forensic projection.
```

---

# 31. Independent Genesis

All graph-bearing conditions must begin from equivalent canonical genesis.

No:

```text
R0 → mutate → R0C → mutate → R1
```

state chain.

Use independent reproducible replays.

---

# 32. R0 Reproduction

Required before ADCAR01 evaluation:

```text
AEMG01 COUNTERFACTUAL:
PASS

BASE SEMANTIC DIFF:
0

POST-CONTINUATION BASE DIFF:
0

G1 MULTI-EVENT:
20/20

G1 CORRECT-CONCEPT SUPPORT:
20/20

TRANSITIONS:
592/592

SEQUENCE→BASE CONDUCTANCE:
0
```

Failure:

```text
ADCAR01_COUNTERFACTUAL_BLOCKED
```

---

# 33. R0C Construction

For every child event:

```text
current coarse descriptor set
        ↓
canonical deterministic conjunction
        ↓
CCAP identity
```

Use same transition provenance and sequence mathematics as R1.

No extra acoustic information.

---

# 34. R1 Construction

For every child event:

```text
existing precompression support
        ↓
identity/rank profile
        ↓
BCAP
```

Then construct directional BCAP transitions.

No labels participate.

---

# 35. AEMG01 Base Authority Frozen

R0C/R1/R2/R3 MUST NOT alter:

```text
Parent event identity
Parent grounding transactions
Parent lexical authority
Base evidence
Base candidate discovery
Base LDSR
Base score
AEMG01 continuation state
```

---

# 36. BCAP Lexical Authority

Required:

\[
DirectUnorderedLexicalAuthority(BCAP)=0
\]

Forbidden:

```text
observe(BCAP + text label)
```

as unordered grounding.

---

# 37. CCAP Lexical Authority

Likewise:

\[
DirectUnorderedLexicalAuthority(CCAP)=0
\]

R0C must not become a hidden alternate lexical grounding path.

---

# 38. Transition Provenance

R0C and R1 must use the exact AEMG01-validated lawful sequence provenance mechanism.

Required:

```text
ILLICIT CHILD LEXICAL TRANSITION CONTEXTS:
0

SEQUENCE→BASE CONDUCTANCE:
0
```

---

# 39. Candidate-Set Conservation

BCAP is sequence-only.

Therefore for every probe:

\[
C_Q^{R1}=C_Q^{AEMG01}
\]

and:

\[
C_Q^{R0C}=C_Q^{AEMG01}
\]

Required:

```text
CANDIDATE_SET_DIFF_R0C:
0

CANDIDATE_SET_DIFF_R1:
0
```

---

# 40. Base State Conservation

Required for R0C and R1:

```text
BASE GROUNDING SEMANTIC DIFF:
0

POST-CONTINUATION BASE DIFF:
0

CHILD LEXICAL AUTHORITY LEAKS:
0

DOUBLE AUTHORITY VIOLATIONS:
0

SEQUENCE→BASE CONDUCTANCE:
0
```

---

# 41. ASUR01 Mathematics Frozen

Do not change:

\[
W_{t,c}=|\Gamma_t\cap\Gamma_c|
\]

\[
N_Q=|C_Q|
\]

\[
Z_t=\sum_{k\in C_Q}W_{t,k}
\]

\[
\rho_Q(t,c)=\frac{W_{t,c}}{Z_t}
\]

\[
SeqLDSR_Q(t,c)
=
\max
\left(
0,
\rho_Q(t,c)-\frac1{N_Q}
\right)
\]

No coefficient.

No renormalization.

---

# 42. Query Transition Activation

Any existing frozen transition activation normalization \(q_t\) remains unchanged.

Do NOT compensate for R0/R0C/R1 transition count differences with new mathematics.

Instead report those differences explicitly.

---

# 43. Topology-Matched Causal Requirement

ADCAR01 causal validation requires evidence that:

\[
R1
\]

improves the frozen compression-alias target beyond:

\[
R0C
\]

on the same one-profile-per-event topology class.

If:

\[
R1\approx R0C
\]

and both outperform R0 similarly:

classify:

```text
COARSE_CONJUNCTION_TOPOLOGY_EFFECT
```

ADCAR01 BCAP hypothesis fails efficacy.

---

# 44. Precompression Specificity Effect

Support:

```text
RECOVERED_PRECOMPRESSION_SPECIFICITY_EFFECT
```

only where:

1. frozen witness existed;
2. R0C remains aliased or loses the causal relation;
3. R1 preserves the causal witness;
4. R1 restores correct specificity ordering.

---

# 45. CA1 Structural Gate

For every rank/identity-separable CA1 witness require:

```text
CAUSAL BCAP ALIAS BREAK:
PASS
```

Across all mandatory CA1 probes:

```text
CA1 PROBES CAUSALLY REPAIRED:
5/5
```

A magnitude-only mandatory CA1 witness yields:

```text
BCAP_REPRESENTATION_INSUFFICIENT
```

and prevents PASS.

---

# 46. CA1 Score Gate

For each frozen dominant CA1 wrong competitor \(w\):

\[
S_{seq}^{R1}(c^*) > S_{seq}^{R1}(w)
\]

required after causal alias repair.

Report:

```text
R0 margin
R0C margin
R1 margin
```

This separates topology effect from specificity effect.

---

# 47. CA2 Structural Gate

For exact frozen:

\[
\mathcal A_{CA2}
\]

report:

```text
total witnesses
identity-set separable
rank-order separable
magnitude-only
true collision
inconclusive
causal aliases broken by R1
causal aliases broken by R0C
```

---

# 48. CA2 Probe-Level Gate

Separately report:

```text
CA2 PROBES WITH ALL CAUSAL ALIASES RESOLVED:
<count>/13
```

No single convenient transition may stand in for a probe containing multiple causal aliases.

---

# 49. BCAP Generalization Requirement

BCAP cannot act as an utterance fingerprint.

Held-out correct sequence support must originate from grounding-derived contexts.

Required:

```text
HELDOUT SELF-GROUNDING CONTRIBUTIONS:
0

HELDOUT MULTI-EVENT COVERAGE:
20/20

HELDOUT CORRECT-CONCEPT SEQUENCE SUPPORT:
20/20
```

---

# 50. Profile Over-Specificity

If BCAP makes training profiles too unique to recur across held-out speech:

```text
PROFILE_OVER_SPECIFICITY
```

This produces:

```text
ADCAR01_COUNTERFACTUAL_EFFICACY_FAIL
```

provided safety remains intact.

---

# 51. Global BCAP Complexity Telemetry

Report:

```text
BCAP event occurrences
distinct BCAP identities
singleton BCAP identities
recurrent BCAP identities
cross-recording recurring identities
cross-speaker recurring identities
held-out identities with grounding support
unseen held-out identity count
BCAP transition occurrences
distinct BCAP transitions
singleton BCAP transitions
```

No invented threshold.

---

# 52. CCAP Complexity Telemetry

Report the same metrics for R0C.

This allows comparison between:

```text
topology-induced uniqueness
```

and:

```text
precompression-specificity-induced uniqueness
```

---

# 53. Reuse Telemetry

Report descriptive:

\[
ProfileReuseRate
\]

for R0C and R1.

Do NOT freeze a numeric minimum unless already defined elsewhere in DGCA.

Interpretation must rely on actual held-out grounding support, not arbitrary threshold.

---

# 54. Transition Fanout

Recompute for:

```text
R0
R0C
R1
```

Current R0 reference:

```text
592 transitions

251 UNIQUE
170 LOW_SHARED
97 MID_SHARED
61 HIGH_SHARED
13 GLOBAL
```

No target distribution is frozen.

---

# 55. No Genericity Tuning

Forbidden:

```text
fanout penalty
generic-transition suppression
inverse-frequency weighting
transition pruning because too shared
```

Any fanout improvement must emerge from representation alone.

---

# 56. R2 Reversal Control

Reverse R1 event order while preserving identical BCAP multiset.

Required:

```text
BASE STATE:
UNCHANGED

CANDIDATE SET:
UNCHANGED
```

Sequence contribution should respond to direction.

If reversal leaves sequence behavior identical where directional evidence exists, investigate transition semantics.

Do not patch.

---

# 57. OOD Safety — Per Probe

Aggregate OOD count is insufficient.

Compare all 10 probes against AEMG01 Parent-equivalent baseline.

Required:

```text
NEWLY_FORCED_OOD_VS_PARENT:
0
```

and full:

```text
OOD_PER_PROBE_SAFETY_AUDIT:
10/10
```

---

# 58. OOD Safety Failure

If any historically non-forced Parent OOD probe becomes forced:

```text
ADCAR01_COUNTERFACTUAL_SAFETY_FAIL
```

even if another probe changes in the opposite direction and aggregate remains 9/10.

---

# 59. Held-Out Global Outcome

Report for:

```text
R0
R0C
R1
```

exactly:

```text
correct /20
wrong /20
ambiguous /20
median correct rank
mean correct rank
```

Current AEMG01 G2 reference:

```text
4/20 correct
median rank 5.0
```

Reference only.

No parameter selection may target this value.

---

# 60. Efficacy Is Causal, Not Accuracy-Only

R1 must not PASS merely because:

```text
accuracy > 4/20
```

A PASS requires frozen compression-alias witnesses to be causally repaired.

Accuracy is secondary telemetry.

---

# 61. Residual Alias Taxonomy

Use exactly:

```text
RESIDUAL_SUPPORT_MAGNITUDE_ALIASING

TRUE_PRECOMPRESSION_PROFILE_COLLISION

GROUNDING_COVERAGE_LOSS

PROFILE_OVER_SPECIFICITY

TRANSITION_PROVENANCE_FAILURE

COARSE_CONJUNCTION_TOPOLOGY_EFFECT

BCAP_REPRESENTATION_INSUFFICIENT

NO_RESIDUAL_ALIAS_FOUND

INCONCLUSIVE
```

---

# 62. No Magnitude Repair During v1.1

If rank/identity BCAP fails because important differences are magnitude-only:

do NOT add:

```text
magnitude bins
quantized amplitude
new thresholds
learned quantizer
```

inside ADCAR01 v1.1 execution.

Return efficacy failure with exact residual classification.

---

# 63. Determinism

BCAP and CCAP must be deterministic.

Canonical sorting:

```text
descending existing support
then canonical descriptor identity
```

Repeated replay must produce identical identities and transitions.

---

# 64. Streaming / Chunk Equivalence

For every child event:

\[
BCAP_{whole}(E)=BCAP_{chunked}(E)
\]

and:

\[
CCAP_{whole}(E)=CCAP_{chunked}(E)
\]

Required sequence equality under lawful chunkings.

---

# 65. SRA01 Regression

Re-run applicable SRA01 safety checks.

ADCAR01 must not change:

```text
Audio v2 event boundaries
silence semantics
onset/offset
streaming behavior
front-end outputs
```

BCAP/CCAP are sequence identity projections only.

---

# 66. Text and Vision Isolation

Required:

```text
TEXT BEHAVIOR CHANGE:
0

VISION BEHAVIOR CHANGE:
0
```

No shared retrieval mathematics changes are allowed.

---

# 67. Descriptor-Budget Complexity Audit

Report for BCAP:

```text
serialized component count
semantic independent component count
graph-facing signal count
retrievable internal component count
independently weighted internal component count
```

Required:

```text
INTERNAL COMPONENTS INDEPENDENTLY GRAPH-ACCESSIBLE:
0
```

for lawful Case-A compound identity.

---

# 68. Fingerprint Audit

For each BCAP identity report recurrence by:

```text
recording
speaker
concept
split
```

Concept/speaker metadata are forensic-only.

Do NOT use them to build BCAP.

A profile occurring once is not automatically illegal, but systematic one-profile-per-recording behavior must be classified.

---

# 69. Candidate-Set Safety

For all held-out/OOD/permutation/reversal probes:

```text
CANDIDATE SET R0C:
exact AEMG01

CANDIDATE SET R1:
exact AEMG01
```

Any difference:

```text
SEQUENCE_TO_BASE_CONDUCTANCE
```

unless proven otherwise.

---

# 70. Production Schema

Required:

```text
PERSISTENT_SCHEMA_DELTA:
0

NEW COGNITIVE PRIMITIVES:
0

NEW LAWS:
0

NEW LEARNED PARAMETERS:
0

NEW LEARNED THRESHOLDS:
0
```

---

# 71. Forbidden Mechanisms

Exactly 40 mandatory forbidden mechanisms:

```text
FM01 phoneme model
FM02 syllable model
FM03 ASR
FM04 DTW
FM05 forced alignment
FM06 speaker embedding
FM07 label-conditioned BCAP
FM08 concept-conditioned BCAP
FM09 OOD-conditioned BCAP
FM10 held-out tuning
FM11 learned acoustic embedding
FM12 neural compressor
FM13 learned quantizer
FM14 k-means
FM15 corpus-trained codebook
FM16 magnitude-bin threshold search
FM17 top-k search
FM18 unrestricted descriptor ceiling increase
FM19 independent persistence of all frame descriptors
FM20 raw frame-vector persistence
FM21 waveform persistence
FM22 transition fanout penalty
FM23 generic-transition suppression
FM24 inverse-frequency weighting
FM25 TF-IDF
FM26 retrieval-rule modification
FM27 LDSR modification
FM28 ASUR mathematics modification
FM29 Law 11 modification
FM30 AEGR01 boundary modification
FM31 AEMG01 authority modification
FM32 child lexical grounding
FM33 new persistent scope field
FM34 second cognitive graph
FM35 post-hoc edge surgery
FM36 test-specific exception
FM37 descriptor-budget laundering
FM38 BCAP internal-component retrieval backdoor
FM39 F01 witness cherry-picking
FM40 aggregate-only OOD safety masking
```

Required:

```text
40/40 PASS
```

---

# 72. Structural Invariants

Require at minimum 40:

```text
INV01 Audio v2 frontend unchanged.
INV02 Audio v2 validity semantics unchanged.
INV03 Parent events unchanged.
INV04 AEGR01 boundaries unchanged.
INV05 Child frame partition unchanged.
INV06 Current coarse descriptors reproducible.
INV07 AEMG01 Parent authority unchanged.
INV08 Parent transactions unchanged.
INV09 Base graph semantic equality.
INV10 Continuation equality.
INV11 Child lexical authority zero.
INV12 Sequence→base conductance zero.
INV13 Candidate discovery unchanged.
INV14 LDSR unchanged.
INV15 ASUR mathematics unchanged.
INV16 Law 11 unchanged.
INV17 BCAP uses existing acoustic support only.
INV18 CCAP uses coarse compressed support only.
INV19 BCAP deterministic.
INV20 CCAP deterministic.
INV21 BCAP label-independent.
INV22 BCAP speaker-independent by construction.
INV23 BCAP file-independent by construction.
INV24 No learned codebook.
INV25 No new magnitude quantization.
INV26 Frozen witness inventory exact.
INV27 CA1 witness completeness.
INV28 CA2 witness completeness.
INV29 R0C topology matched to R1.
INV30 R0C contains no discarded specificity.
INV31 R1 contains no new acoustic feature.
INV32 Transition provenance lawful.
INV33 Held-out self-grounding zero.
INV34 OOD audit per probe.
INV35 Streaming/chunk equivalence.
INV36 SRA01 safety.
INV37 Text isolation.
INV38 Vision isolation.
INV39 Persistent schema unchanged.
INV40 Descriptor-budget semantics obeyed.
```

Required:

```text
40/40 PASS
```

---

# 73. Mathematical / Formal Prechecks

Require 28:

```text
M01 Parent event reproduction exact.
M02 AEMG01 base reproduction exact.
M03 F01 CA1 inventory exact.
M04 F01 CA2 inventory exact.
M05 Precompression support reproduction exact.
M06 Coarse descriptor reproduction exact.
M07 Spectral profile deterministic ordering.
M08 Periodicity profile deterministic ordering.
M09 BCAP canonical identity deterministic.
M10 CCAP canonical identity deterministic.
M11 BCAP label independence.
M12 CCAP label independence.
M13 Descriptor-budget interpretation resolved.
M14 BCAP grammar compatibility PASS.
M15 R0 reproduced.
M16 R0C uses no discarded acoustic evidence.
M17 R1 uses no new acoustic evidence.
M18 R0C/R1 topology class matched.
M19 Causal witness concordance complete.
M20 Identity/rank separability audit complete.
M21 AEMG01 base semantic diff 0.
M22 Candidate set diff 0.
M23 Sequence→base conductance 0.
M24 Held-out self-grounding 0.
M25 OOD per-probe safety complete.
M26 Streaming/chunk equivalence.
M27 Determinism exact.
M28 No forbidden mechanism required.
```

Required:

```text
28/28 PASS
```

---

# 74. Release Gates

Require 36 release gates.

Key gates:

```text
G01 lineage exact
G02 assets exact
G03 current regression PASS
G04 historical signature exact
G05 AEMG01 baseline reproduced
G06 Parent events exact
G07 F01 CA1 inventory exact
G08 F01 CA2 inventory exact
G09 precompression evidence exact
G10 coarse descriptor evidence exact
G11 descriptor-budget semantics resolved
G12 BCAP grammar compatible
G13 no budget laundering
G14 separability audit complete
G15 R0 exact
G16 R0C valid
G17 R1 valid
G18 topology match R0C/R1
G19 base semantic diff 0
G20 continuation diff 0
G21 child lexical leaks 0
G22 candidate set diff 0
G23 sequence→base conductance 0
G24 transition provenance legal
G25 CA1 causal alias repair complete
G26 CA1 score inversion repaired
G27 CA2 witness telemetry complete
G28 CA2 causal probe resolution
G29 held-out self-grounding 0
G30 held-out multi-event 20/20
G31 held-out correct-concept sequence support 20/20
G32 OOD per-probe safety 10/10
G33 streaming/chunk PASS
G34 deterministic replay PASS
G35 SRA01/text/vision regression safety PASS
G36 math/invariants/forbidden all PASS
```

Required:

```text
36/36 PASS
```

---

# 75. Verdict Vocabulary

Exactly five:

```text
ADCAR01_COUNTERFACTUAL_PASS

ADCAR01_COUNTERFACTUAL_EFFICACY_FAIL

ADCAR01_COUNTERFACTUAL_SAFETY_FAIL

ADCAR01_PREIMPLEMENTATION_REJECTED

ADCAR01_COUNTERFACTUAL_BLOCKED
```

---

# 76. Verdict Precedence

Use:

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

# 77. BLOCKED

Use when the experiment cannot establish trustworthy reconstruction.

Examples:

```text
lineage mismatch
asset mismatch
AEMG01 baseline cannot reproduce
F01 witness inventory unavailable
precompression evidence unavailable
descriptor-budget semantics unresolved
```

---

# 78. PREIMPLEMENTATION_REJECTED

Use when BCAP requires forbidden architecture.

Examples:

```text
descriptor-budget laundering
new persistent primitive
new schema field
special retrieval branch
second graph
new Law
learned codebook
```

---

# 79. SAFETY_FAIL

Use when BCAP is lawfully realizable but violates frozen safety:

```text
base state changes
candidate set changes
new OOD forced probe
child lexical authority
sequence→base conductance
regression failure
```

---

# 80. EFFICACY_FAIL

Use when execution is valid and safe but BCAP does not causally repair the compression target.

Examples:

```text
mandatory CA1 witness magnitude-only
R1 gives no causal improvement beyond R0C
CA1 inversion unresolved
CA2 causal aliases unresolved
profile over-specificity
20/20 sequence support lost
BCAP representation insufficient
```

---

# 81. PASS

PASS requires all:

```text
descriptor-budget compatibility:
PASS

BCAP grammar compatibility:
PASS

separability audit:
complete

AEMG01 base:
exact

candidate sets:
exact

CA1 causal repair:
5/5

CA1 score inversion resolution:
5/5

CA2 causal repair:
required frozen target satisfied

held-out multi-event:
20/20

held-out correct-concept sequence support:
20/20

held-out self-grounding:
0

OOD per-probe safety:
10/10

sequence→base conductance:
0

streaming:
PASS

determinism:
PASS

schema delta:
0

math:
28/28

invariants:
40/40

forbidden:
40/40

release gates:
36/36
```

---

# 82. Meaning of PASS

PASS means only:

```text
DESCRIPTOR_COMPRESSION_ALIASING REPAIR:
COMPONENT VALIDATED

RECOVERED PRECOMPRESSION SPECIFICITY EFFECT:
SUPPORTED

COARSE TOPOLOGY EFFECT:
CONTROLLED

AEMG01 BASE AUTHORITY:
CONSERVED

GENERALIZED SEQUENCE SUPPORT:
CONSERVED

DESCRIPTOR BUDGET:
LAWFULLY RESPECTED

PRODUCTION READINESS:
NOT ESTABLISHED
```

---

# 83. Production Governance

Even on PASS:

```text
AEGR01 IMPLEMENTATION AUTHORIZED:
NO

AEMG01 PRODUCTION IMPLEMENTATION AUTHORIZED:
NO

ADCAR01 PRODUCTION IMPLEMENTATION AUTHORIZED:
NO
```

---

# 84. Required Next Stage After PASS

Only after:

```text
ADCAR01_COUNTERFACTUAL_PASS
```

open:

```text
AUDIO_COMPOSITE_REPAIR_COUNTERFACTUAL
```

containing:

```text
Audio v2
+
AEGR01
+
AEMG01
+
ADCAR01
```

as one architecture.

---

# 85. Composite Goal

The later composite trial must test actual end-to-end auditory grounding after all two-stage causal repairs coexist.

No production implementation before composite success.

---

# 86. Scientific Claim Limit

If PASS, the strongest authorized claim is:

> ADCAR01 validated that sequence-relevant acoustic specificity lost by the frozen auditory event compressor can be restored through a lawful bounded conjunctive event identity beyond a topology-matched coarse-conjunction control, while preserving AEMG01 Parent-equivalent lexical authority, existing DGCA sequence mathematics, and current persistent graph schema.

Do NOT claim full speech recognition solved.

---

# 87. Formal Status

```text
============================================================
DGCA PHASE 2.6 — ADCAR01

FORMAL REPAIR SPECIFICATION:
v1.1 CANDIDATE

CAUSAL TARGET:
DESCRIPTOR_COMPRESSION_ALIASING

PRIMARY CANDIDATE:
BCAP

TOPOLOGY CONTROL:
R0C / CCAP

DESCRIPTOR BUDGET NON-LAUNDERING:
MANDATORY

IDENTITY GRAMMAR COMPATIBILITY:
MANDATORY

PRECOMPRESSION SEPARABILITY AUDIT:
MANDATORY

CAUSAL WITNESS CONCORDANCE:
MANDATORY

CA1 WITNESS INVENTORY:
FROZEN / COMPLETE

CA2 WITNESS INVENTORY:
FROZEN / COMPLETE

OOD SAFETY:
PER-PROBE

CANDIDATE SET CONSERVATION:
EXACT

OVER-SPECIFICITY:
EXPLICIT FAILURE MODE

EFFICACY FAILURE VERDICT:
ADDED

BASE AUTHORITY:
AEMG01 FROZEN

AEGR01 BOUNDARIES:
FROZEN

AUDIO V2:
FROZEN

ASUR01 MATHEMATICS:
FROZEN

LAW 11:
FROZEN

PRODUCTION IMPLEMENTATION:
NOT AUTHORIZED

COUNTERFACTUAL EXECUTION:
NOT AUTHORIZED YET

CURRENT STATUS:
ADCAR01_FORMAL_REPAIR_SPECIFICATION_v1.1_CANDIDATE

NEXT REQUIRED ACTION:
ADCAR01 v1.1
CLOSURE ADVERSARIAL FREEZE REVIEW
============================================================
```