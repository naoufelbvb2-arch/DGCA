# DGCA Phase 2.6 — Post-LESR Residual Retrieval Forensics 02 Specification v1.0

## Artifact-Only Diagnosis of Residual Cross-Modal Retrieval Errors After LESR v1.0

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Parent Repair:** Cross-Modal Retrieval Ranking Repair — LESR v1.0  
**Forensic Trial:** Post-LESR Residual Retrieval Forensics 02  
**Version:** 1.0  
**Status:** **FORENSIC PROTOCOL — CANDIDATE FOR FREEZE**  
**Execution Mode:** **ARTIFACT-ONLY / READ-ONLY / NO RETRAINING / NO REPAIR**  
**Architecture Baseline Signature:** `915119d40643cb97`  
**Parent A/B Result:** `OLD 10/20 -> NEW 11/20`  
**Residual New Errors:** `9 / 20`  
**Correct→Wrong Regression:** `1`  
**New Ambiguous:** `0`  
**Primary Goal:** **Determine whether the 9 residual errors are still ranking failures, are caused by grounding specificity, or reveal another downstream mechanism.**

---

# 1. Purpose

LESR v1.0 successfully changed the proven retrieval semantics:

\[
\boxed{
UnweightedPathCounting
\rightarrow
LocalEvidenceShareRanking
}
\]

and removed:

\[
\boxed{
ForcedLexicalTieAuthority
}
\]

The frozen RI01 A/B result changed from:

\[
10\ Correct,\ 10\ Wrong,\ 0\ Ambiguous
\]

to:

\[
11\ Correct,\ 9\ Wrong,\ 0\ Ambiguous
\]

with:

\[
Wrong\rightarrow Correct = 2
\]

and:

\[
Correct\rightarrow Wrong = 1
\]

The parent implementation report also contains an accounting inconsistency:

- executive summary states `CORRECT_TO_WRONG = 0`;
- formal metrics block states `CORRECT_TO_WRONG = 1`.

This forensic trial exists to resolve that contradiction and causally explain all 9 residual wrong probes.

---

# 2. Governing Rule

This trial is diagnostic only.

Required:

\[
\boxed{
DiagnoseBeforeSecondRepair
}
\]

Forbidden:

- retraining;
- additional grounding;
- additional image exposure;
- architecture modification;
- Vision Encoder modification;
- English Encoder modification;
- LESR modification;
- tie policy modification;
- near-tie threshold;
- new ranking formula;
- new specificity weighting;
- manual correction;
- new law;
- new persistent state;
- new learned parameter.

---

# 3. Frozen Parent Facts

The following parent results are immutable inputs:

```text
OldCorrect = 10
OldWrong = 10
OldAmbiguous = 0

NewCorrect = 11
NewWrong = 9
NewAmbiguous = 0

WrongToCorrect = 2
WrongToWrong = 8

CorrectToCorrect = 9
CorrectToWrong = 1

OldExactTies = 6
NewForcedTieWinners = 0

TextToVisual = 10/10
CandidateSetsConserved = 20/20
GraphMutationDuringRanking = 0
```

If these cannot be reproduced from frozen artifacts:

\[
\boxed{
FORENSIC\_BASELINE\_BLOCKED
}
\]

---

# 4. Primary Scientific Questions

## RRF02-Q01

Which exact probe is:

\[
\boxed{
Correct\rightarrow Wrong
}
\]

and why did LESR reverse it?

---

## RRF02-Q02

Was that old correct result genuinely supported, or was it a lucky forced-tie result?

---

## RRF02-Q03

Why are there:

\[
0\ Ambiguous
\]

after exact-tie ambiguity semantics?

Did LESR legitimately break the old ties through edge-strength evidence, or merely replace lexical tie-breaking with very small historical weight differences?

---

## RRF02-Q04

Are all 9 new wrong cases still:

\[
CorrectConceptReachedButLostRanking
\]

or has the failure class changed?

---

## RRF02-Q05

Do the 9 residual errors arise because:

\[
GenericFeatureSupport
\]

still dominates despite normalization?

---

## RRF02-Q06

Or do they arise because the correct concept lacks sufficiently discriminative visual-text grounding?

---

## RRF02-Q07

Do the residual errors reflect visual collision?

---

## RRF02-Q08

Do they reflect edge-weight history from grounding rather than current visual evidence quality?

---

## RRF02-Q09

Is the remaining bottleneck:

```text
RANKING
GROUNDING_SPECIFICITY
VISUAL_COLLISION
EDGE_WEIGHT_HISTORY
EVALUATION
MULTIFACTORIAL
```

---

# 5. Canonical Residual Failure Taxonomy

Each of the 9 new wrong probes must receive exactly one primary class.

## R2-A — RESIDUAL_RANKING_LOSS

Correct concept is stored, reached, present, sufficiently grounded, but loses LESR aggregation.

---

## R2-B — GROUNDING_SPECIFICITY_INSUFFICIENT

Correct concept is stored and reached, but grounding contains too little concept-specific evidence relative to shared generic features.

---

## R2-C — EDGE_WEIGHT_HISTORY_BIAS

Correct and wrong concepts are both grounded, but historical edge-strength asymmetry dominates ranking despite similar current evidence.

---

## R2-D — TRUE_VISUAL_COLLISION

Frozen visual representation genuinely supports wrong concept at least as strongly as correct concept.

---

## R2-E — OLD_LUCKY_TIE_EXPOSED

Applies only when an old "correct" probe was correct solely because old lexical ordering selected the true label from an exact tie, and LESR reveals that the underlying evidence did not favor it.

---

## R2-F — EVALUATION_OR_ACCOUNTING_DEFECT

Used if parent transition bookkeeping, expected-label mapping, or A/B telemetry is wrong.

---

## R2-G — OTHER_CAUSALLY_PROVEN

Only with explicit evidence.

Required:

\[
\sum R2\text{-}A..R2\text{-}G = 9
\]

---

# 6. Required Frozen Inputs

Use existing artifacts only.

Required sources include:

```text
DGCA-CROSS-MODAL-RETRIEVAL-RANKING-REPAIR-IMPLEMENTATION-VERIFICATION-REPORT.md
xmrr_ri01_ab_results.jsonl
xmrr_ri01_ab_summary.json
xmrr_synthetic_controls.json
xmrr_property_tests.json
xmrr_determinism.json
xmrr_readonly_graph_check.json
xmrr_reverse_retrieval_regression.json
xmrr_invariants.json
xmrr_release_gates.json
xmrr_signature_verification.json

DGCA-RI01-CROSSMODAL-RETRIEVAL-FORENSICS-01-REPORT.md
ri01_forensics_probe_ledger.jsonl
ri01_forensics_candidate_rankings.jsonl
ri01_forensics_feature_fanout.json
ri01_forensics_generic_feature_audit.json
ri01_forensics_discriminative_features.json
ri01_forensics_visual_vs_winner_similarity.jsonl
ri01_forensics_path_traces.jsonl
ri01_forensics_score_decomposition.jsonl
ri01_forensics_tie_audit.json
ri01_forensics_candidate_margins.json

RI01 frozen B30 graph/checkpoint
RI01 frozen 20 held-out probes
```

If exact historical state is unavailable, report blocker rather than retraining.

---

# 7. First Task — Resolve Correct→Wrong Accounting

Identify the exact probe with:

```text
OLD = CORRECT
NEW = WRONG
```

Record:

```text
ProbeID
ImageID
TrueConcept
OldWinner
NewWinner
OldOutcome
NewOutcome
OldCorrectScore
OldWrongScore
NewCorrectSupport
NewWrongSupport
OldExactTie
OldTieSet
OldTieBreakApplied
NewTopSupportDifference
```

This case must be explained before any closure.

---

# 8. G13 Re-evaluation

The parent repair gate:

```text
XMRR-G13 — No Correct→Wrong Regression
```

must be re-evaluated.

Allowed outcomes:

```text
G13_TRUE_PASS
G13_PASS_ONLY_IF_OLD_LUCKY_TIE
G13_FAIL
G13_PARENT_REPORT_INCONSISTENT
```

If the case was not an old forced-tie lucky correct outcome:

\[
\boxed{
XMRR\text{-}G13 = FAIL
}
\]

and the parent `16/16` release-gate claim must be corrected historically.

---

# 9. Old Exact-Tie Ledger

For all 6 old exact-tie probes record:

```text
ProbeID
TrueConcept
OldTieSet
OldSelectedWinner
OldOutcome
NewSupportByCandidate
NewWinner
NewOutcome
TrueConceptSupport
WinnerSupport
SupportDifference
```

Required question:

Did LESR break each tie through meaningful learned edge asymmetry?

---

# 10. Tie-Break Replacement Audit

For each old exact tie classify post-LESR result:

```text
TIE_TO_CORRECT_UNIQUE
TIE_TO_WRONG_UNIQUE
TIE_TO_AMBIGUOUS
TIE_TO_NO_RESULT
```

If:

```text
TIE_TO_WRONG_UNIQUE
```

determine whether the unique support difference is:

- grounded in repeated concept-specific evidence;
- caused by generic edge-weight history;
- caused by asymmetric observation counts;
- caused by another implementation artifact.

---

# 11. Residual 9-Probe Ledger

Construct one exact row per new wrong probe.

Required fields:

```text
ProbeID
ImageID
TrueConcept
OldWinner
NewWinner

CorrectConceptStored
CorrectConceptReached
CorrectConceptInCandidateSet

CorrectLESRSupport
WinnerLESRSupport
SupportMargin

CorrectSupportingFeatures
WinnerSupportingFeatures

CorrectSpecificFeatures
WinnerSpecificFeatures

CorrectGenericFeatures
WinnerGenericFeatures

CorrectCrossModalEdgeWeights
WinnerCrossModalEdgeWeights

CorrectGroundingEpisodeSupport
WinnerGroundingEpisodeSupport

VisualSimilarityToTrue
VisualSimilarityToWinner

PrimaryResidualClass
SecondaryMechanism
```

Output:

```text
rrf02_residual_probe_ledger.jsonl
```

---

# 12. Reconstruct Post-LESR Confusion Matrix

Build a new exact 10×10 matrix from the 20 frozen probes.

Compare:

```text
OLD confusion matrix
NEW LESR confusion matrix
```

Report:

- errors removed;
- new error introduced;
- persistent error pairs;
- most common wrong winner;
- whether `apple_vs_ball` still dominates.

---

# 13. Ranking Margin Audit

For all 20 probes compute:

\[
Margin =
Support_{winner}
-
Support_{runnerup}
\]

Separate:

```text
CorrectProbes
WrongProbes
CorrectToWrongProbe
OldTieProbes
```

Report exact distribution.

Do not introduce a margin threshold.

The margin is diagnostic only.

---

# 14. Why New Ambiguous = 0?

This question is mandatory.

For all 6 old ties:

\[
OldScore_1=OldScore_2
\]

but after LESR:

\[
NewSupport_1\neq NewSupport_2
\]

apparently in all cases.

Determine whether inequality comes from:

1. existing cross-modal edge weights;
2. unequal observation counts;
3. evidence deduplication;
4. reciprocal-edge removal;
5. query activation weights;
6. floating arithmetic;
7. implementation ordering;
8. another source.

Required:

```text
NewTieBreakSourceByProbe
```

---

# 15. Edge-Weight History Audit

For each residual error compare:

```text
W(feature,true_concept)
W(feature,wrong_concept)
ObservationCount(feature,true)
ObservationCount(feature,wrong)
GroundingEpisodeOrigin
```

Determine whether the wrong winner is favored because its cross-modal edges accumulated greater historical weight during the 3 grounding exposures.

If yes and current image evidence does not justify the difference:

candidate class:

```text
R2-C EDGE_WEIGHT_HISTORY_BIAS
```

---

# 16. Grounding Specificity Audit

For each concept, derive from frozen grounding episodes:

```text
FeaturesGrounded
FeatureRecurrenceAcross3Images
FeatureFanoutAcrossConcepts
CrossModalWeights
```

Identify:

- concept-specific recurring features;
- generic recurring features;
- one-off features.

Question:

Does the true concept have sufficient discriminative grounding?

If not:

```text
R2-B GROUNDING_SPECIFICITY_INSUFFICIENT
```

---

# 17. Evidence Specificity Without New Scoring

Forensics may calculate evaluation-only metrics such as:

\[
Specificity(f,c)=P(f|c)-P(f|\neg c)
\]

or:

\[
Fanout(f)
\]

But these MUST NOT alter ranking.

Use only to explain why LESR did or did not succeed.

---

# 18. Generic Support Residual Audit

LESR bounded generic support, but generic support may still dominate in aggregate if many generic features point toward the same wrong concept.

For each residual error report:

```text
NumberOfGenericSupportingFeaturesTrue
NumberOfGenericSupportingFeaturesWinner
TotalGenericSupportTrue
TotalGenericSupportWinner

NumberOfSpecificSupportingFeaturesTrue
NumberOfSpecificSupportingFeaturesWinner
TotalSpecificSupportTrue
TotalSpecificSupportWinner
```

Determine whether residual failure is still a ranking aggregation issue.

---

# 19. Feature Diversity Audit

One candidate may receive support from many distinct feature families.

Record support diversity by:

```text
color
luminance
shape/compactness
elongation
solidity
texture
orientation
size
```

Question:

Does LESR treat eight separate generic feature families as eight independent evidence sources even when they are highly correlated descriptors of one same visual region?

This is diagnostic only.

Do not repair.

---

# 20. Correlated-Evidence Hypothesis

Test the hypothesis:

\[
\boxed{
DistinctFeatureTokens
\neq
NecessarilyIndependentEvidence
}
\]

Example:

```text
compact-high
elong-low
solidity-high
shape-circle
```

may all derive from the same region geometry.

If multiple correlated descriptors jointly dominate ranking, record:

```text
CORRELATED_EVIDENCE_MULTIPLICITY_SUPPORTED
```

This may indicate a deeper ranking issue beyond path deduplication.

---

# 21. Grounding-Curriculum History Audit

For each concept inspect exact 3 grounding images.

Record whether all three share accidental properties:

```text
same background
same luminance
same scale
same geometry
same color
```

If a concept's cross-modal weights over-reinforced accidental recurring features, this is grounding-specificity evidence.

No rerun.

---

# 22. Visual Collision Recheck

For each residual error compare held-out signature to:

- true concept grounding signatures;
- wrong concept grounding signatures.

Use evaluation-only prototype:

\[
P_c=\{f:\text{appears in at least 2 of 3 grounding images}\}
\]

If:

\[
J(HeldOut,P_{wrong})
>
J(HeldOut,P_{true})
\]

and graph support follows this relation:

candidate class:

```text
R2-D TRUE_VISUAL_COLLISION
```

---

# 23. Correct Concept Reachability Recheck

Although previous forensics reported 20/20 reachability, verify under post-LESR execution that all residual wrong probes still include the correct concept.

Required:

```text
CorrectReached = 9/9
CorrectInCandidateSet = 9/9
```

If not, failure class changed and must be reported.

---

# 24. Candidate Discovery Conservation Recheck

Confirm:

```text
OldCandidateSet == LESRCandidateSet
```

for all 20 probes.

No candidate-set drift is allowed.

---

# 25. Evaluation Integrity Audit

Recheck:

```text
TrueConcept
ImageID
FileSHA256
OldOutcome
NewOutcome
TransitionClass
```

especially the one `Correct→Wrong` probe.

This resolves the parent report contradiction.

---

# 26. No-Retraining Replay

If deterministic read-only replay is used:

```text
B30DigestBefore
=
B30DigestAfter
```

and:

```text
OldResultReproduced = 20/20
NewResultReproduced = 20/20
```

---

# 27. Primary Residual Decision Tree

For each new wrong probe:

### Step 1

If correct concept not stored:

report changed failure class; do not force R2-A.

### Step 2

If correct concept not reached:

report reachability regression.

### Step 3

If correct concept reached but visual evidence itself favors wrong concept:

\[
R2-D
\]

### Step 4

If visual evidence favors correct concept but grounding lacks concept-specific association:

\[
R2-B
\]

### Step 5

If grounding is adequate but historical edge strength favors wrong concept:

\[
R2-C
\]

### Step 6

If grounding and weights are adequate but LESR aggregation still selects wrong:

\[
R2-A
\]

### Step 7

If telemetry/accounting is wrong:

\[
R2-F
\]

---

# 28. Distinguish Ranking vs Grounding Specificity

The central diagnostic distinction is:

## Ranking Bottleneck

\[
CorrectDiscriminativeEvidenceExists
\land
CorrectGroundingExists
\land
CorrectCandidateReached
\land
AggregationChoosesWrong
\]

## Grounding Specificity Bottleneck

\[
VisualRepresentationAdequate
\land
CorrectCandidateReached
\land
GroundingAssociationsAreMostlyGeneric
\]

This trial must decide which better explains the residual 9 cases.

---

# 29. Required Aggregate Counts

Report:

```text
ResidualErrors = 9

R2-A ResidualRankingLoss
R2-B GroundingSpecificityInsufficient
R2-C EdgeWeightHistoryBias
R2-D TrueVisualCollision
R2-E OldLuckyTieExposed
R2-F EvaluationAccountingDefect
R2-G Other
```

Required:

\[
\boxed{
FailureClassAccounting = 9/9
}
\]

---

# 30. Required Special Accounting for Correct→Wrong

The `Correct→Wrong` probe must additionally receive:

```text
OldCorrectWasForcedTie = YES/NO
OldCorrectWasEvidenceSupported = YES/NO
NewWrongIsEvidenceSupported = YES/NO
RegressionIsReal = YES/NO
XMRR_G13_FinalStatus
```

---

# 31. Forensic Invariants

### RRF02-INV-01 — Artifact-Only

No retraining.

### RRF02-INV-02 — No Repair

LESR remains unchanged.

### RRF02-INV-03 — Architecture Frozen

No architecture mutation.

### RRF02-INV-04 — Encoders Frozen

Vision and English encoders unchanged.

### RRF02-INV-05 — B30 Frozen

No learned graph mutation.

### RRF02-INV-06 — Same 20 Probes

No dataset replacement.

### RRF02-INV-07 — Parent A/B Reproduced

10/10 old and 11/9 new reproduced.

### RRF02-INV-08 — Correct→Wrong Identified

Exact probe isolated.

### RRF02-INV-09 — All 9 Residual Errors Classified

No hidden unresolved case.

### RRF02-INV-10 — Old Six Ties Audited

All six accounted.

### RRF02-INV-11 — Grounding Specificity Tested

Not assumed.

### RRF02-INV-12 — Edge-Weight History Tested

Not assumed.

### RRF02-INV-13 — Visual Collision Rechecked

Not assumed.

### RRF02-INV-14 — Correlated Evidence Tested

Not assumed.

### RRF02-INV-15 — Evaluation Accounting Reconciled

Summary and metrics contradiction resolved.

### RRF02-INV-16 — No New Threshold

No diagnostic metric changes semantics.

### RRF02-INV-17 — Candidate Discovery Unchanged

20/20.

### RRF02-INV-18 — Read-Only Replay Non-Mutating

Digest conserved.

### RRF02-INV-19 — G13 Re-evaluated Honestly

No inherited PASS without evidence.

### RRF02-INV-20 — Scientific Claim Bounded

No second repair recommended as proven until cause closes.

Required:

\[
\boxed{20/20}
\]

---

# 32. Forensic Gates

### RRF02-G01 — Parent A/B Integrity

Old/new results reproduced.

### RRF02-G02 — Correct→Wrong Reconciled

Regression case fully explained.

### RRF02-G03 — Six Old Ties Reconstructed

6/6.

### RRF02-G04 — Residual Ledger Complete

9/9.

### RRF02-G05 — Post-LESR Confusion Matrix Complete

20/20.

### RRF02-G06 — Grounding Specificity Audit Complete

All concepts inspected.

### RRF02-G07 — Edge-Weight History Audit Complete

All residual cases inspected.

### RRF02-G08 — Correlated Evidence Audit Complete

Feature-family dependency assessed.

### RRF02-G09 — Visual Collision Recheck Complete

9/9.

### RRF02-G10 — Evaluation Accounting Consistent

No unresolved summary/metrics contradiction.

### RRF02-G11 — Failure Taxonomy Closed

9/9.

### RRF02-G12 — G13 Final Status Issued

PASS/FAIL/corrected historical interpretation.

### RRF02-G13 — No-Mutation Verification

B30 unchanged.

### RRF02-G14 — Final Residual Causal Verdict Issued

Primary remaining bottleneck localized.

Required:

\[
\boxed{14/14}
\]

---

# 33. Allowed Final Causal Verdicts

Use only if supported:

```text
RESIDUAL_CROSSMODAL_RANKING_BOTTLENECK
GROUNDING_SPECIFICITY_BOTTLENECK
EDGE_WEIGHT_HISTORY_BIAS_SUPPORTED
CORRELATED_EVIDENCE_MULTIPLICITY_SUPPORTED
TRUE_VISUAL_COLLISION_MAJOR
TRUE_VISUAL_COLLISION_MINOR
OLD_LUCKY_TIE_REGRESSION_EXPOSED
XMRR_G13_HISTORICAL_FAIL
XMRR_G13_HISTORICAL_PASS_WITH_TIE_EXCEPTION
PARENT_A_B_ACCOUNTING_DEFECT
MULTIFACTORIAL_POST_LESR_BOTTLENECK
NO_SINGLE_DOMINANT_RESIDUAL_CAUSE
FORENSIC_CLOSURE_PARTIAL
```

---

# 34. Required Machine-Readable Artifacts

Produce:

```text
DGCA-POST-LESR-RESIDUAL-RETRIEVAL-FORENSICS-02-REPORT.md

rrf02_residual_probe_ledger.jsonl
rrf02_correct_to_wrong_audit.json
rrf02_old_six_ties.jsonl
rrf02_post_lesr_confusion_matrix.json
rrf02_error_transitions.json
rrf02_margin_audit.json
rrf02_tie_break_source.jsonl
rrf02_edge_weight_history.jsonl
rrf02_grounding_specificity.json
rrf02_generic_support_residual.jsonl
rrf02_feature_diversity.jsonl
rrf02_correlated_evidence.json
rrf02_grounding_curriculum_history.json
rrf02_visual_collision_recheck.jsonl
rrf02_candidate_conservation.json
rrf02_evaluation_integrity.json
rrf02_replay_integrity.json
rrf02_failure_taxonomy.json
rrf02_invariants.json
rrf02_gates.json
rrf02_failures.jsonl
```

---

# 35. Required Final Answers

The report must answer:

1. Which exact probe changed Correct→Wrong?
2. Was its old correct result caused by an exact forced tie?
3. Was its old correct result genuinely evidence-supported?
4. Why did LESR make it wrong?
5. Is `XMRR-G13` truly PASS or FAIL?
6. Why did new `AMBIGUOUS=0`?
7. What broke the six old exact ties?
8. Were those tie breaks driven by meaningful edge-weight asymmetry?
9. How many of the 9 residual errors are pure ranking losses?
10. How many are grounding-specificity failures?
11. How many are edge-weight-history bias?
12. How many are true visual collisions?
13. How many reflect evaluation/accounting defects?
14. Do generic features still dominate after LESR?
15. Do multiple correlated feature families behave like duplicate evidence?
16. Did the 3-image grounding curriculum reinforce accidental shared features?
17. Does the correct concept still reach candidate scoring in 9/9 cases?
18. Is Vision Encoder v2 still not the primary bottleneck?
19. Is LESR itself insufficient, or is the remaining problem upstream in grounding specificity?
20. What is the exact primary residual bottleneck after LESR?

---

# 36. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — POST-LESR RESIDUAL RETRIEVAL FORENSICS 02

EXECUTION MODE:
ARTIFACT-ONLY / READ-ONLY

RETRAINING:
0

REPAIR DURING FORENSICS:
0

ARCHITECTURE CHANGES:
0

ENCODER CHANGES:
0

FROZEN B30 STATE:
USED / NOT_USED

HELD-OUT PROBES:
20

OLD CORRECT:
10

OLD WRONG:
10

NEW CORRECT:
11

NEW WRONG:
9

NEW AMBIGUOUS:
0

CORRECT -> WRONG PROBE:
...

OLD CORRECT WAS FORCED TIE:
YES / NO

REGRESSION IS REAL:
YES / NO

XMRR-G13 FINAL STATUS:
PASS / FAIL / PASS_WITH_HISTORICAL_TIE_EXCEPTION / PARENT_REPORT_INCONSISTENT

OLD EXACT TIES:
6

OLD TIES RECONSTRUCTED:
... / 6

OLD TIES -> NEW CORRECT:
...

OLD TIES -> NEW WRONG:
...

OLD TIES -> NEW AMBIGUOUS:
...

WHY NEW AMBIGUOUS = 0:
...

RESIDUAL ERRORS:
9

R2-A RESIDUAL RANKING:
...

R2-B GROUNDING SPECIFICITY:
...

R2-C EDGE-WEIGHT HISTORY:
...

R2-D TRUE VISUAL COLLISION:
...

R2-E OLD LUCKY TIE EXPOSED:
...

R2-F EVALUATION / ACCOUNTING:
...

R2-G OTHER:
...

FAILURE CLASS ACCOUNTING:
... / 9

CORRECT CONCEPT REACHED:
... / 9

CORRECT CONCEPT IN CANDIDATE SET:
... / 9

GENERIC SUPPORT STILL DOMINANT:
YES / NO / PARTIAL

CORRELATED EVIDENCE MULTIPLICITY:
SUPPORTED / NOT_SUPPORTED / PARTIAL

GROUNDING SPECIFICITY BOTTLENECK:
SUPPORTED / NOT_SUPPORTED / PARTIAL

EDGE-WEIGHT HISTORY BIAS:
SUPPORTED / NOT_SUPPORTED / PARTIAL

TRUE VISUAL COLLISION:
MAJOR / MINOR / NONE

VISION ENCODER PRIMARY BOTTLENECK:
YES / NO / UNRESOLVED

LESR PRIMARY REMAINING BOTTLENECK:
YES / NO / PARTIAL

GROUNDING PRIMARY REMAINING BOTTLENECK:
YES / NO / PARTIAL

RRF02 INVARIANTS:
x / 20

RRF02 GATES:
x / 14

ARCHITECTURE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / MISMATCH

LEARNED GRAPH MUTATION:
0 / NONZERO

FORENSIC CLOSURE:
COMPLETE / PARTIAL / BLOCKED

FINAL RESIDUAL CAUSAL VERDICT:
...
============================================================
```

---

# 37. Closure Rule

The forensic trial can close only if:

\[
\boxed{
All9ResidualWrongCases
\rightarrow
ExplicitPrimaryCause
}
\]

and:

\[
\boxed{
CorrectToWrongCase
\rightarrow
Resolved
}
\]

and:

\[
\boxed{
XMRR\text{-}G13
\rightarrow
HonestFinalStatus
}
\]

and:

\[
\boxed{
B30StateUnchanged
}
\]

---

# 38. Final Scientific Principle

The question is no longer:

\[
\text{Does LESR improve accuracy?}
\]

That has already been answered:

\[
10/20\rightarrow11/20
\]

The new question is:

\[
\boxed{
\textbf{Why do 9 errors remain after the proven path-counting defect was reduced?}
}
\]

The answer must distinguish:

\[
Ranking
\]

from:

\[
GroundingSpecificity
\]

from:

\[
EdgeWeightHistory
\]

from:

\[
CorrelatedEvidence
\]

from:

\[
VisualCollision
\]

before any second repair is authorized.
