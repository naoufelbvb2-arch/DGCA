# DGCA Phase 2.6 — RI01 Cross-Modal Retrieval Forensics 01 Specification v1.0

## Artifact-Only Causal Diagnosis of Held-Out Image-to-Text Retrieval Errors

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Parent Trial:** Small Real-Image Scientific Trial 01  
**Forensic Trial:** RI01 Cross-Modal Retrieval Forensics 01  
**Version:** 1.0  
**Status:** **FORENSIC PROTOCOL — CANDIDATE FOR FREEZE**  
**Execution Mode:** **ARTIFACT-ONLY / NO RETRAINING / NO ARCHITECTURE CHANGES**  
**Vision Encoder:** Vision Encoder v2 — IMPLEMENTED / VERIFIED / FROZEN / CLOSED  
**Architecture Baseline Signature:** `915119d40643cb97`  
**Parent Trial Protocol Status:** `PROTOCOL_PASS`  
**Parent Trial Phase-A Status:** **REAL_IMAGE_VISUAL_REPRESENTATION_DEMONSTRATED**  
**Parent Trial Phase-B Held-Out Result:** **10 / 20 correct, 10 / 20 wrong, 0 no-result, 0 ambiguous**  
**Primary Question:** **Why did 10 held-out real images retrieve the wrong text concept despite successful visual representation and persistent cross-modal association formation?**

---

# 1. Purpose

The parent Small Real-Image Scientific Trial 01 established:

\[
\boxed{
RealImages
\rightarrow
PersistentVisualStructure
}
\]

and:

\[
\boxed{
RepeatedVisualEvidence
\rightarrow
Reinforcement
}
\]

with strong Phase-A evidence:

- 50 Phase-A exposure images;
- 42 persistent visual nodes;
- 220 persistent visual edges;
- 90 visual edge reinforcements;
- 10/10 early visual anchors survived to A50;
- passive visual loss = 0;
- 20/20 held-out images retrieved learned visual structure;
- median within-concept overlap = 0.7500;
- median between-concept overlap = 0.1667;
- determinism = 300/300 bit-identical.

Phase B also established structural cross-modal learning:

- 30 grounding episodes;
- 80 persistent cross-modal edges created;
- 160 cross-modal edges reinforced;
- 10/10 concepts with persistent grounding;
- reverse text-to-visual retrieval = 10/10;
- semantic label leakage = 0;
- manual edge injection = 0;
- hidden passive forgetting = 0.

However:

\[
\boxed{
HeldOutImage\rightarrow CorrectTextConcept
=
10/20
}
\]

and:

\[
\boxed{
HeldOutImage\rightarrow WrongTextConcept
=
10/20
}
\]

with:

\[
NoResult=0
\]

\[
Ambiguous=0
\]

Therefore the next scientific task is not to redesign the Vision Encoder.

It is to localize the exact failure path.

---

# 2. Governing Forensic Rule

This investigation is:

\[
\boxed{
ArtifactOnly
}
\]

No training rerun.

No architecture repair.

No threshold tuning.

No new data.

No new semantic labels.

No graph mutation.

No alternate curriculum.

No selective re-exposure.

No manual edge injection.

No modified retrieval policy.

The investigation may run deterministic read-only replay only if all required state and inputs are already frozen and replay does not learn.

---

# 3. Core Causal Chain

For every held-out image, reconstruct:

\[
Image
\rightarrow
VisualFrameIR
\rightarrow
VisualFeatureSet
\rightarrow
PersistentVisualStructure
\rightarrow
CrossModalEdgesReached
\rightarrow
TextCandidates
\rightarrow
CandidateScores
\rightarrow
Ranking/Arbitration
\rightarrow
Winner
\]

The forensic trial must identify the earliest stage at which the correct concept is lost.

---

# 4. Mandatory Failure Taxonomy

Each of the 10 incorrect held-out cases must receive exactly one primary causal classification.

## F-A — CORRECT_CONCEPT_NOT_STORED

The intended text concept has no valid persistent grounding supported by the relevant training evidence.

\[
CorrectConceptGroundingAbsent
\]

---

## F-B — CORRECT_CONCEPT_STORED_BUT_NOT_REACHED

The correct concept has valid stored cross-modal grounding, but held-out visual activation does not traverse to it.

\[
Stored
\land
NotReached
\]

---

## F-C — CORRECT_CONCEPT_REACHED_BUT_LOST_RANKING

The correct concept is present among candidates but loses ranking/arbitration to another concept.

\[
Correct\in Candidates
\land
Winner\neq Correct
\]

---

## F-D — GENERIC_VISUAL_FEATURES_OVERGROUNDED

Generic recurring features such as:

```text
vis:sz:large
vis:lum:dark
vis:compact:high
vis:elong:low
```

carry excessive cross-modal support across multiple concepts and dominate more discriminative features.

---

## F-E — VISUAL_COLLISION

The held-out image's visual evidence genuinely collides with another concept at the frozen low-level representation.

Example:

\[
Overlap(Image_{apple},BallMemory)
\ge
Overlap(Image_{apple},AppleMemory)
\]

---

## F-F — EVALUATION_OR_PROBE_DEFECT

The retrieval evaluation, candidate extraction, expected-label mapping, tie handling, or telemetry misclassifies an otherwise correct graph result.

---

## F-G — OTHER_CAUSALLY_PROVEN

Use only if none of F-A..F-F is supported and another specific causal mechanism is proven from artifacts.

No vague "OTHER" without evidence.

---

# 5. Frozen Inputs

Use only existing parent-trial artifacts and frozen repository state.

Required artifacts include:

```text
DGCA-SMALL-REAL-IMAGE-SCIENTIFIC-TRIAL-01-REPORT.md

ri01_image_manifest.json
ri01_phase_a_manifest.json
ri01_phase_b_manifest.json

ri01_encoder_dispositions.jsonl
ri01_visual_signatures.jsonl
ri01_within_concept_overlap.json
ri01_between_concept_overlap.json
ri01_collision_audit.json

ri01_phase_a_graph_metrics.json
ri01_phase_a_reinforcement.jsonl
ri01_phase_a_persistence.json
ri01_phase_a_heldout.jsonl
ri01_phase_a_adversarial.jsonl

ri01_phase_b_grounding.jsonl
ri01_phase_b_crossmodal_edges.jsonl
ri01_phase_b_heldout_retrieval.jsonl
ri01_phase_b_reverse_retrieval.jsonl

ri01_transient_lifecycle.json
ri01_determinism.json
ri01_invariants.json
ri01_phase_a_gates.json
ri01_phase_b_gates.json
ri01_signature_verification.json
ri01_failures.jsonl
```

If a required forensic field is not present, the investigator may inspect the frozen graph/checkpoint and deterministic read-only retrieval path.

Do not retrain.

---

# 6. Parent-Trial Facts That Must Remain Fixed

The forensic process must preserve:

```text
HeldOutImages = 20
Correct = 10
Wrong = 10
NoConcept = 0
Ambiguous = 0

GroundingConcepts = 10
GroundingEpisodes = 30
CrossModalEdgesCreated = 80
CrossModalEdgesReinforced = 160
ConceptsWithPersistentGrounding = 10

ReverseTextToVisual = 10/10

SemanticLeakage = 0
ManualEdgeInjection = 0
EvaluationMutation = 0
HiddenPassiveForgetting = 0
```

If any parent metric changes merely by forensic inspection:

STOP — FORENSIC INTEGRITY FAILURE.

---

# 7. Exact 20-Probe Ledger

Construct one canonical row for every held-out image.

Required fields:

```text
ProbeID
ImageID
TrueConcept
RetrievedConcept
Outcome
EncoderStatus
VisualSignature
CorrectConceptStored
CorrectConceptReached
CorrectConceptCandidateScore
WinnerConcept
WinnerCandidateScore
RankOfCorrectConcept
CandidateCount
TopKCandidates
VisualOverlapToTrueConcept
VisualOverlapToWinnerConcept
CrossModalSupportToTrueConcept
CrossModalSupportToWinnerConcept
PrimaryFailureClass
SecondaryNotes
```

Produce:

```text
ri01_forensics_probe_ledger.jsonl
```

---

# 8. Confusion Matrix

Build exact 10×10 confusion matrix.

Rows:

```text
true concept
```

Columns:

```text
retrieved concept
```

Concept order:

```text
apple
banana
ball
cup
bottle
car
tree
bird
cat
dog
```

Produce:

```text
ri01_forensics_confusion_matrix.json
```

Also produce a human-readable table in the report.

---

# 9. Error Pair Analysis

For each wrong retrieval:

record:

```text
TrueConcept
WrongConcept
Count
ReciprocalConfusion
```

Examples:

```text
apple -> ball
ball -> apple
cup -> bottle
cat -> dog
```

Determine whether errors are:

- pairwise;
- symmetric;
- asymmetric;
- dominated by one universal winner;
- distributed randomly.

This pattern is essential for causal localization.

---

# 10. Candidate Ranking Reconstruction

For every held-out probe, reconstruct the exact candidate list before final winner selection.

Required:

```text
CandidateConcept
RawRetrievalScore
AnyNormalizedScore
Rank
SupportingVisualFeatures
SupportingCrossModalEdges
SupportingPathCount
TieStatus
TieBreakRuleIfAny
```

If the current retrieval path does not explicitly expose scores, instrument only read-only telemetry without changing decision semantics.

Instrumentation must produce identical winner as parent trial.

---

# 11. Correct Concept Presence Test

For each of 20 probes answer:

```text
CorrectConceptStored = YES/NO
CorrectConceptReached = YES/NO
CorrectConceptInCandidateSet = YES/NO
CorrectConceptRank = integer/null
```

Aggregate:

```text
CorrectStoredCount
CorrectReachedCount
CorrectCandidateCount
CorrectRank1Count
CorrectRank2Count
CorrectRank3PlusCount
```

---

# 12. Storage Audit

For each concept inspect the 3 grounding episodes.

Required:

```text
GroundingConcept
GroundingImageIDs
CrossModalEdgesCreated
CrossModalEdgesReinforced
PersistentEdgesAliveAtB30
RelevantVisualFeatures
GroundedTextNode
```

Determine whether every concept had genuine persistent support.

Parent report states:

\[
10/10
\]

concepts grounded.

This forensic step verifies the exact structure behind that summary.

---

# 13. Cross-Modal Edge Specificity

For every visual feature \(v\), compute evaluation-only grounding fanout:

\[
Fanout(v)
=
|\{textConcepts\ connected\ to\ v\}|
\]

Report features with:

```text
Fanout = 1
Fanout = 2
...
Fanout = 10
```

High fanout features are potential generic grounding channels.

This metric is read-only and must not affect cognition.

---

# 14. Generic Feature Audit

Audit recurring generic features, including where present:

```text
vis:lum:*
vis:sz:*
vis:compact:*
vis:elong:*
vis:solidity:*
vis:ori:*
vis:tex:*
vis:clr:*
```

For each token report:

```text
Feature
ConceptFanout
GroundingObservationCount
TotalCrossModalWeight
MeanCrossModalWeight
MaxCrossModalWeight
ConceptsConnected
```

Identify whether generic features dominate candidate scores.

---

# 15. Discriminative Feature Audit

For each concept identify features with:

- high recurrence inside concept;
- lower recurrence outside concept;
- persistent cross-modal connection to correct text node.

For evaluation only define a descriptive specificity metric:

\[
Specificity(f,c)
=
P(f|c)-P(f|\neg c)
\]

or another transparent artifact-only statistic.

Do not feed this metric into DGCA.

It is forensic telemetry only.

---

# 16. The 8-Feature Numerical Pattern Audit

The parent trial reported:

\[
CrossModalEdgesCreated=80
\]

\[
CrossModalEdgesReinforced=160
\]

with:

\[
10\ concepts\times3\ grounding\ episodes
\]

and:

\[
B_{visual}\le8
\]

Audit whether:

\[
80 = 10\times8
\]

and:

\[
160 = 10\times2\times8
\]

reflect exactly 8 visual-to-text associations per concept.

Determine:

```text
DidEachConceptReceiveExactly8CrossModalFeatureEdges = YES/NO
```

If YES, list the eight feature families per concept and determine whether this structure causes broad over-grounding.

Do not infer defect merely from numerical equality.

Prove or reject it.

---

# 17. Visual Similarity vs Retrieval Winner

For each held-out image compute:

```text
SimilarityToTrueConceptPrototype
SimilarityToWinnerConceptPrototype
```

where prototype is evaluation-only aggregation from frozen grounding/exposure visual signatures.

No new cognitive prototype is created.

If:

\[
SimilarityToWinner
>
SimilarityToTrue
\]

classify potential visual collision.

If:

\[
SimilarityToTrue
>
SimilarityToWinner
\]

but wrong concept wins, ranking/cross-modal specificity becomes more likely.

---

# 18. Prototype Definition for Forensics Only

For a concept \(c\), define evaluation-only recurring feature set:

\[
P_c
=
\{f:
f\ appears\ in\ at\ least\ 2\ of\ 3\ grounding\ images\}
\]

This is NOT inserted into graph.

Use only to inspect whether the held-out image resembles the intended concept's recurring visual structure.

---

# 19. Path-Level Trace

For every wrong case provide at least one exact winning path:

\[
HeldOutVisualFeature
\rightarrow
PersistentVisualEdge
\rightarrow
CrossModalEdge
\rightarrow
WrongTextConcept
\]

and at least one correct path if the correct concept was reached:

\[
HeldOutVisualFeature
\rightarrow
PersistentVisualEdge
\rightarrow
CrossModalEdge
\rightarrow
CorrectTextConcept
\]

Include edge IDs/weights/observation counts where available.

---

# 20. Score Decomposition

If candidate score is additive, multiplicative, ranked, path-based, or otherwise decomposable, report exact components.

For each wrong probe:

```text
CorrectCandidateScoreBreakdown
WinnerCandidateScoreBreakdown
```

Do not describe scores abstractly if exact components are available.

---

# 21. Tie-Breaking Audit

Because parent results show:

```text
Wrong = 10
Ambiguous = 0
```

audit deterministic tie handling.

For every probe determine:

```text
ExactTie = YES/NO
NearTie = YES/NO
TieBreakApplied = YES/NO
TieBreakRule
```

If tied candidates are silently forced into one winner, quantify how many errors derive from this.

---

# 22. Candidate Margin

For each probe compute:

\[
Margin
=
Score_{winner}
-
Score_{runnerup}
\]

Report:

- correct probes median margin;
- wrong probes median margin;
- minimum margin;
- maximum margin.

This distinguishes strong wrong retrieval from deterministic near-tie choice.

---

# 23. Wrong-Answer Concentration

Count how often each text concept appears as a wrong winner.

If one concept dominates:

\[
WinnerBias
\]

may exist.

Report:

```text
WrongWinnerFrequencyByConcept
```

---

# 24. Retrieval Direction Asymmetry

Parent result:

\[
Text\rightarrow Visual=10/10
\]

while:

\[
HeldOutImage\rightarrow Text=10/20
\]

Audit directional asymmetry.

For each concept compare:

```text
TextToVisualReachability
VisualToTextReachability
```

and relevant degree/fanout/path-count structure.

Determine whether the graph stores bidirectional access symmetrically or retrieval procedure is directionally asymmetric.

---

# 25. Correct-but-Low-Rank Cases

For every incorrect probe where correct concept appears in candidate set, report:

```text
CorrectRank
CorrectScore
WinnerScore
ScoreDifference
SharedSupportingFeatures
CorrectOnlyFeatures
WinnerOnlyFeatures
```

These are strong candidates for F-C or F-D.

---

# 26. Correct-Not-Reached Cases

For any probe where correct grounding exists but correct concept is absent from candidates, report the earliest broken link:

```text
HeldOut feature missing?
Persistent visual edge missing?
Cross-modal edge not traversed?
Budget exhausted?
Traversal direction blocked?
Context/gating excluded path?
```

Do not speculate; show exact artifact evidence.

---

# 27. Budget / Traversal Audit

If retrieval uses bounded traversal:

record for each wrong probe:

```text
InitialBudget
EdgesConsidered
EdgesTraversed
BudgetRemaining
CorrectPathEligible
CorrectPathTraversed
CorrectPathDroppedReason
```

This can distinguish retrieval budget failure from grounding failure.

---

# 28. Context / Gating Audit

Inspect whether context or gating removes correct candidate paths.

Report:

```text
CorrectPathBeforeGating
CorrectPathAfterGating
WinnerPathBeforeGating
WinnerPathAfterGating
```

No gating changes are allowed.

---

# 29. Collision Cross-Check

Cross-reference wrong cases with:

```text
ri01_collision_audit.json
ri01_between_concept_overlap.json
```

Especially inspect:

```text
apple_vs_ball
```

reported as the most confusable pair.

Determine how many wrong held-out cases are explained by known visual collision versus retrieval-level effects.

---

# 30. Background Feature Cross-Check

For each wrong probe determine whether winning concept was supported primarily by background-like one-off features or recurring concept features.

Use only frozen signatures and grounding artifacts.

No new foreground detector.

---

# 31. Color Dominance Audit

Count wrong cases where:

```text
same dominant color
```

is a major shared support feature.

Determine whether same-color different-concept pairs dominate mistakes.

Do not claim color itself is erroneous.

The issue is whether ranking overweights broadly shared color evidence.

---

# 32. Size / Luminance / Generic Geometry Audit

Repeat the same analysis for:

```text
size
luminance
compactness
elongation
solidity
orientation
texture
```

Determine which feature families contribute most often to wrong winners.

---

# 33. Evaluation Harness Audit

Inspect the held-out evaluator itself.

Verify:

- true-label mapping;
- ImageID mapping;
- candidate extraction;
- concept normalization;
- text node naming;
- score sorting direction;
- tie handling;
- stale state;
- read-only clone correctness;
- no index misalignment;
- no concept-order leakage;
- no off-by-one mapping;
- no accidental filename label use;
- no stale candidate cache.

Produce explicit PASS/FAIL per item.

---

# 34. Filename / Manifest Integrity

Cross-check:

```text
ImageID
FileSHA256
TrueConcept
ManifestRole
```

for all held-out Phase-B images.

Ensure none are mislabeled or assigned to wrong concept.

---

# 35. Read-Only Replay Integrity

If read-only deterministic replay is required:

Before replay:

```text
B30GraphDigest
```

After replay:

```text
B30GraphDigest
```

Required:

\[
Before=After
\]

and:

```text
WinnerReplayMatchesParentTrial = 20/20
```

If parent winners cannot be reproduced:

classify F-F until resolved.

---

# 36. No-Rerun Rule

Forbidden:

- re-running Phase-B training;
- different image order;
- alternative grounding images;
- extra grounding exposure;
- modified text labels;
- altered graph initialization;
- different learning parameters.

Only read-only reproduction is permitted.

---

# 37. No-Repair Rule

Forbidden during forensics:

- new discriminative weighting;
- TF-IDF-like visual scoring inside DGCA;
- attention changes;
- retrieval threshold changes;
- candidate calibration;
- pruning generic features;
- graph rewiring;
- additional negative evidence;
- manual inhibition;
- new law;
- new primitive.

Those may be proposed later only after cause is proven.

---

# 38. Primary Quantitative Outputs

Report:

```text
TotalHeldOutProbes = 20
Correct = 10
Wrong = 10

CorrectConceptStored
CorrectConceptReached
CorrectConceptInCandidateSet

WrongCases_F_A
WrongCases_F_B
WrongCases_F_C
WrongCases_F_D
WrongCases_F_E
WrongCases_F_F
WrongCases_F_G

ExactTies
NearTies
TieBreakErrors

GenericFeatureDominatedErrors
VisualCollisionErrors
RankingLossErrors
EvaluationDefectErrors

MedianCorrectMargin
MedianWrongMargin

MostCommonWrongWinner
MostCommonConfusionPair
```

---

# 39. Required Causal Closure

All 10 incorrect cases must be causally accounted for.

Required:

\[
\sum FailureClassCounts = 10
\]

No unresolved case may be hidden in averages.

If one or more remain unresolved:

```text
FORENSIC_CLOSURE = PARTIAL
```

---

# 40. Forensic Invariants

### RIF01-INV-001 — Parent Trial Frozen

No parent metric changes.

### RIF01-INV-002 — Artifact-Only Investigation

No retraining.

### RIF01-INV-003 — No Architecture Change

DGCA remains unchanged.

### RIF01-INV-004 — No Encoder Change

Vision/English encoders remain frozen.

### RIF01-INV-005 — No Graph Learning During Forensics

Read-only only.

### RIF01-INV-006 — All 20 Probes Accounted

No omitted held-out probe.

### RIF01-INV-007 — All 10 Wrong Cases Classified

Every wrong case receives a primary failure class.

### RIF01-INV-008 — Correct Concept Storage Explicitly Checked

No assumption from summary metrics.

### RIF01-INV-009 — Correct Concept Reachability Explicitly Checked

Stored ≠ reached.

### RIF01-INV-010 — Candidate Ranking Explicitly Reconstructed

Reached ≠ winner.

### RIF01-INV-011 — Generic Feature Fanout Measured

Over-grounding tested explicitly.

### RIF01-INV-012 — Visual Collision Cross-Checked

Encoder representation failure not inferred blindly.

### RIF01-INV-013 — Tie Handling Audited

No forced winner hidden.

### RIF01-INV-014 — Evaluation Harness Audited

Probe defects remain possible until ruled out.

### RIF01-INV-015 — Directional Retrieval Compared

Text→Visual vs Visual→Text asymmetry measured.

### RIF01-INV-016 — Read-Only Replay Non-Mutating

Graph digest conserved.

### RIF01-INV-017 — No Post-Hoc Threshold

No new decision criterion alters results.

### RIF01-INV-018 — No Repair During Diagnosis

Evidence precedes intervention.

### RIF01-INV-019 — Exact Paths Preserved

At least one concrete path shown per wrong probe where available.

### RIF01-INV-020 — Scientific Claim Bounded

Cause conclusion must match evidence.

Required:

\[
\boxed{
20/20
}
\]

---

# 41. Forensic Gates

### RIF01-G01 — Parent Artifacts Integrity

All required parent artifacts present or traceable.

### RIF01-G02 — Parent Metrics Reproduced

10 correct / 10 wrong reproduced exactly.

### RIF01-G03 — Confusion Matrix Complete

10×10 matrix generated.

### RIF01-G04 — Candidate Ranking Complete

All 20 candidate lists reconstructed.

### RIF01-G05 — Correct Storage Audit Complete

Storage status known for all probes.

### RIF01-G06 — Reachability Audit Complete

Reachability known for all probes.

### RIF01-G07 — Feature Fanout Audit Complete

Generic grounding fanout measured.

### RIF01-G08 — Visual Collision Audit Complete

All wrong cases cross-checked.

### RIF01-G09 — Tie-Break Audit Complete

Forced-winner behavior ruled in/out.

### RIF01-G10 — Evaluation Harness Audit Complete

Probe defects ruled in/out.

### RIF01-G11 — Failure Taxonomy Closed

10/10 wrong cases assigned.

### RIF01-G12 — No-Mutation Verification

Architecture and learned state unchanged.

### RIF01-G13 — Final Causal Verdict Issued

Primary bottleneck localized.

Required:

\[
\boxed{
13/13
}
\]

for complete forensic closure.

---

# 42. Allowed Final Causal Verdicts

Use one or more only if supported:

```text
CROSSMODAL_STORAGE_FAILURE
CROSSMODAL_REACHABILITY_BOTTLENECK
CROSSMODAL_RANKING_BOTTLENECK
GENERIC_FEATURE_OVERGROUNDING_SUPPORTED
VISUAL_COLLISION_IS_MAJOR_ERROR_SOURCE
VISUAL_COLLISION_IS_MINOR_ERROR_SOURCE
DIRECTIONAL_RETRIEVAL_ASYMMETRY_SUPPORTED
TIE_BREAKING_ARTIFACT_SUPPORTED
EVALUATION_PROBE_DEFECT_SUPPORTED
MULTIFACTORIAL_RETRIEVAL_FAILURE
NO_SINGLE_DOMINANT_CAUSE
FORENSIC_CLOSURE_PARTIAL
```

---

# 43. Interpretation Logic

## Case 1

If:

```text
CorrectConceptStored = NO
```

then primary cause:

```text
F-A
```

---

## Case 2

If:

```text
CorrectConceptStored = YES
CorrectConceptReached = NO
```

then primary cause:

```text
F-B
```

---

## Case 3

If:

```text
CorrectConceptReached = YES
CorrectRank > 1
```

then primary cause:

```text
F-C
```

unless artifact evidence proves F-D or F-E is the deeper cause.

---

## Case 4

If wrong winner is supported primarily by high-fanout generic visual tokens:

```text
F-D
```

---

## Case 5

If held-out representation is genuinely closer to wrong concept's frozen visual structure than true concept:

```text
F-E
```

---

## Case 6

If evaluation mapping or scoring implementation is wrong:

```text
F-F
```

---

# 44. Distinguishing Ranking from Grounding

Grounding is considered structurally present when:

\[
CorrectConcept
\]

has persistent cross-modal support from grounding episodes.

Retrieval failure is downstream if:

\[
GroundingPresent
\land
HeldOutCueReachedCandidateSet
\land
WinnerWrong
\]

Therefore do not label all 10 wrong probes as grounding failure without inspecting candidate paths.

---

# 45. Distinguishing Vision Failure from Retrieval Failure

Vision-level evidence is considered adequate for a probe when:

- held-out image retrieves previously experienced visual structure;
- signature overlap with true concept is meaningful;
- correct cross-modal grounding exists.

If all three hold but wrong text wins:

\[
\boxed{
VisionEncoderNotPrimaryFailure
}
\]

for that probe.

---

# 46. Required Machine-Readable Artifacts

Produce:

```text
DGCA-RI01-CROSSMODAL-RETRIEVAL-FORENSICS-01-REPORT.md

ri01_forensics_probe_ledger.jsonl
ri01_forensics_confusion_matrix.json
ri01_forensics_error_pairs.json
ri01_forensics_candidate_rankings.jsonl
ri01_forensics_storage_audit.json
ri01_forensics_reachability.jsonl
ri01_forensics_feature_fanout.json
ri01_forensics_generic_feature_audit.json
ri01_forensics_discriminative_features.json
ri01_forensics_eight_feature_pattern.json
ri01_forensics_visual_vs_winner_similarity.jsonl
ri01_forensics_path_traces.jsonl
ri01_forensics_score_decomposition.jsonl
ri01_forensics_tie_audit.json
ri01_forensics_candidate_margins.json
ri01_forensics_directionality.json
ri01_forensics_budget_traversal.jsonl
ri01_forensics_gating.jsonl
ri01_forensics_evaluation_harness_audit.json
ri01_forensics_replay_integrity.json
ri01_forensics_failure_taxonomy.json
ri01_forensics_invariants.json
ri01_forensics_gates.json
ri01_forensics_failures.jsonl
```

---

# 47. Required Final Answers

The report must answer explicitly:

1. Were all 10 correct concepts actually stored?
2. Were all 10 correct concepts reachable from their wrong held-out probes?
3. In how many wrong cases was the correct concept in the candidate set?
4. In how many wrong cases did the correct concept lose ranking?
5. Which concepts were most frequently confused?
6. Was `apple_vs_ball` a major real error pair?
7. Did one wrong text concept dominate retrieval?
8. Did exactly 8 visual feature edges per concept create the 80/160 numerical pattern?
9. Which visual feature families had the highest concept fanout?
10. Did generic features dominate wrong winners?
11. Did discriminative features exist but lose scoring influence?
12. How many wrong cases were genuine visual collisions?
13. How many were retrieval/ranking failures?
14. How many were reachability failures?
15. How many were storage failures?
16. Were any errors caused by tie-breaking?
17. Were any caused by evaluation/probe defects?
18. Did retrieval budget eliminate correct paths?
19. Did context/gating eliminate correct paths?
20. Why is Text→Visual 10/10 while Image→Text is 10/20?
21. Is Vision Encoder v2 the primary bottleneck?
22. Is cross-modal storage the primary bottleneck?
23. Is retrieval/ranking the primary bottleneck?
24. Is over-grounding of generic features supported?
25. What is the exact primary scientific cause of the 10 wrong answers?

---

# 48. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — RI01 CROSS-MODAL RETRIEVAL FORENSICS 01

PARENT TRIAL:
SMALL REAL-IMAGE SCIENTIFIC TRIAL 01

EXECUTION MODE:
ARTIFACT-ONLY / READ-ONLY

RETRAINING:
0

ARCHITECTURE CHANGES:
0

ENCODER CHANGES:
0

HELD-OUT PROBES:
20

PARENT CORRECT:
10

PARENT WRONG:
10

REPRODUCED CORRECT:
...

REPRODUCED WRONG:
...

CORRECT CONCEPT STORED:
... / 20

CORRECT CONCEPT REACHED:
... / 20

CORRECT CONCEPT IN CANDIDATE SET:
... / 20

WRONG CASES — F-A STORAGE:
...

WRONG CASES — F-B REACHABILITY:
...

WRONG CASES — F-C RANKING:
...

WRONG CASES — F-D GENERIC OVERGROUNDING:
...

WRONG CASES — F-E VISUAL COLLISION:
...

WRONG CASES — F-F EVALUATION DEFECT:
...

WRONG CASES — F-G OTHER:
...

FAILURE CLASS ACCOUNTING:
... / 10

EXACT TIES:
...

NEAR TIES:
...

TIE-BREAK ERRORS:
...

GENERIC FEATURE DOMINATED ERRORS:
...

VISUAL COLLISION ERRORS:
...

RANKING LOSS ERRORS:
...

EVALUATION DEFECT ERRORS:
...

MOST CONFUSED TRUE->WINNER PAIR:
...

MOST COMMON WRONG WINNER:
...

MEDIAN CORRECT WINNER MARGIN:
...

MEDIAN WRONG WINNER MARGIN:
...

TEXT->VISUAL:
10 / 10

IMAGE->TEXT:
10 / 20

DIRECTIONAL ASYMMETRY:
SUPPORTED / NOT_SUPPORTED

EIGHT-FEATURE NUMERICAL PATTERN:
CONFIRMED / REJECTED / PARTIAL

GENERIC FEATURE OVERGROUNDING:
SUPPORTED / NOT_SUPPORTED / PARTIAL

VISION ENCODER PRIMARY BOTTLENECK:
YES / NO / UNRESOLVED

CROSSMODAL STORAGE PRIMARY BOTTLENECK:
YES / NO / UNRESOLVED

RETRIEVAL/RANKING PRIMARY BOTTLENECK:
YES / NO / UNRESOLVED

EVALUATION PROBE DEFECT:
YES / NO / PARTIAL

FORENSIC INVARIANTS:
x / 20

FORENSIC GATES:
x / 13

ARCHITECTURE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / MISMATCH

LEARNED GRAPH MUTATION DURING FORENSICS:
0 / NONZERO

FORENSIC CLOSURE:
COMPLETE / PARTIAL / BLOCKED

FINAL CAUSAL VERDICT:
...
============================================================
```

---

# 49. Closure Rule

Forensics may be closed only if:

\[
\boxed{
All10WrongCases
\rightarrow
ExplicitCausalClassification
}
\]

and:

\[
\boxed{
ParentTrialStateUnchanged
}
\]

The objective is not to improve 10/20.

The objective is to explain 10/20.

---

# 50. Final Scientific Principle

The correct order is:

\[
\boxed{
Diagnose
\rightarrow
Localize
\rightarrow
ThenRepair
}
\]

not:

\[
\boxed{
Observe50\%
\rightarrow
TuneUntilHigher
}
\]

The forensic trial must determine whether the remaining limitation lies primarily in:

\[
VisualRepresentation
\]

or:

\[
CrossModalStorage
\]

or:

\[
CueReachability
\]

or:

\[
CandidateRanking
\]

or:

\[
GenericFeatureGrounding
\]

or:

\[
Evaluation
\]

before any future intervention is authorized.
