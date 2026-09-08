# DGCA Phase 2.6 — Small Real-Image Scientific Trial 01 Specification v1.0

## Empirical Validation of Real-Image Representation, Visual Consistency, Separability, and Initial Text Grounding

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Trial:** Small Real-Image Scientific Trial 01  
**Version:** 1.0  
**Status:** **PROTOCOL — CANDIDATE FOR FREEZE**  
**Vision Encoder:** **Vision Encoder v2 — IMPLEMENTED / VERIFIED / FROZEN / CLOSED**  
**Architecture Baseline:** Post-Law-3-Abolition DGCA  
**Canonical Baseline Signature:** `915119d40643cb97`  
**Architecture Changes During Trial:** **0**  
**Encoder Changes During Trial:** **0**  
**New Cognitive Primitives:** **0**  
**New Normative Laws:** **0**  
**Primary Scientific Question:** **Can DGCA form stable and usable visual knowledge from multiple real photographs without semantic labels inside the Vision Encoder?**

---

# 1. Purpose

Vision Encoder v2 has already demonstrated:

\[
\boxed{
RawPixels
\rightarrow
DeterministicPerceptualStructure
}
\]

and:

\[
\boxed{
CompatibleVisualExperience
\rightarrow
PersistentVisualEdgeReinforcement
}
\]

without pretrained semantic vision models, paired-text injection, focal weight privilege, or graph-dependent parsing.

This trial therefore does **not** re-test whether pixels can be decoded or whether low-level features can be emitted.

Trial 01 asks the next scientific question:

\[
\boxed{
\textbf{Can repeated real visual experience produce stable, discriminative, persistent, reusable visual knowledge inside DGCA?}
}
\]

The trial proceeds in two strictly separated phases:

\[
\boxed{
Phase\ A = VisionOnly
}
\]

followed only after Phase A is valid by:

\[
\boxed{
Phase\ B = TextGrounding
}
\]

The trial must distinguish visual representation quality from semantic grounding quality.

---

# 2. Governing Scientific Principle

The trial is governed by:

\[
\boxed{
EncoderDescribes
\quad ; \quad
DGCA LearnsMeaning
}
\]

The Vision Encoder must remain semantically blind.

Semantic class names such as:

```text
apple
banana
cup
ball
bottle
car
tree
bird
cat
dog
```

may exist only in:

- dataset metadata;
- evaluation labels;
- later text-grounding episodes.

They must never be passed into Vision Encoder v2.

---

# 3. Core Scientific Questions

## RI01-Q01 — Visual Consistency

Do multiple real photographs of the same semantic concept produce overlapping persistent visual structure?

\[
\boxed{
SameConcept
\Rightarrow
NonZeroVisualOverlap
}
\]

---

## RI01-Q02 — Visual Separability

Do visually different concepts remain distinguishable?

\[
\boxed{
DifferentConcept
\not\Rightarrow
SameVisualRepresentation
}
\]

---

## RI01-Q03 — Persistence

Does visual knowledge survive across unrelated image episodes?

\[
\boxed{
VisualKnowledge
\rightarrow
Persistent
}
\]

---

## RI01-Q04 — Reinforcement

When shared visual descriptors recur across independent images, are existing persistent visual relations reinforced?

\[
\boxed{
RecurringVisualEvidence
\rightarrow
SameEdgeReinforcement
}
\]

---

## RI01-Q05 — Instance/Concept Separation

Do scene-local `inst:vis:*` nodes retire while shared visual feature knowledge remains?

\[
\boxed{
TransientInstanceRetires
\land
PersistentVisualKnowledgeSurvives
}
\]

---

## RI01-Q06 — Background Robustness

Does moderate background variation avoid completely dominating same-concept representation?

---

## RI01-Q07 — Scale Robustness

Does moderate scale variation preserve meaningful feature overlap?

---

## RI01-Q08 — Illumination Robustness

Does moderate illumination variation preserve meaningful feature overlap without erasing real color/luminance evidence?

---

## RI01-Q09 — Confusability Control

Can DGCA avoid collapsing visually similar but semantically different objects into indistinguishable memory solely because they share color or shape?

---

## RI01-Q10 — Text Grounding

After Vision-only validation, can repeated independent pairing between a semantic text label and multiple visual instances ground that label to recurring visual structure?

\[
\boxed{
VisualPattern
+
TextLabel
\rightarrow
CrossModalAssociation
}
\]

without semantic injection inside the encoder.

---

## RI01-Q11 — Cross-Image Generalization

After grounding on some images, can a held-out real image of the same concept activate or retrieve the associated text concept through existing DGCA mechanisms?

---

# 4. Trial Scope

The trial is intentionally small.

Recommended frozen concept set:

\[
\boxed{
10\ semantic\ concepts
}
\]

Canonical initial set:

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

If the dataset cannot support one concept with suitable real images, replace it **before trial execution** and freeze the replacement.

Do not change the concept set after seeing DGCA results.

---

# 5. Image Count

Use:

\[
\boxed{
8\ real\ images\ per\ concept
}
\]

for a total of:

\[
\boxed{
80\ real\ photographs
}
\]

Recommended split per concept:

```text
5 Grounding/Exposure Images
2 Held-Out Recognition Images
1 Adversarial/Variation Image
```

Total:

```text
50 exposure images
20 held-out images
10 adversarial/variation images
```

All images must be real photographs.

Synthetic shapes may be used only for encoder control diagnostics, not as scientific Trial-01 evidence.

---

# 6. Real-Image Requirements

Each selected image should preferably contain:

- one dominant object;
- the object visibly occupying a meaningful portion of the frame;
- limited severe occlusion;
- no embedded text required for interpretation;
- no watermark used as class cue;
- no class-name text visible in the image;
- no duplicate image files;
- no near-identical crop copies counted as independent images.

The trial may include controlled variation in:

- background;
- scale;
- position;
- illumination;
- viewpoint.

---

# 7. Dataset Provenance

For each image record:

```text
ImageID
ConceptLabel_EvaluationOnly
SourceType
SourceURI_or_LocalProvenance
FileSHA256
Width
Height
Format
ExposureRole
VariationTags
```

If internet-sourced images are used, freeze exact files locally before execution.

Scientific execution uses the frozen local image manifest only.

---

# 8. No Semantic Leakage

The evaluation harness may know:

```text
ConceptLabel = apple
```

Vision Encoder v2 may not.

Required input to Vision Encoder:

```text
ImageBytes
ScopeID
FrozenVisionConfig
```

Forbidden:

```text
paired_text
class_name
semantic_label
expected_object
folder_name passed into encoder
```

The implementation must demonstrate that renaming image files or folders does not change encoder output.

---

# 9. Frozen Vision Encoder

During Trial 01:

```text
VisionEncoderChanges = 0
FeatureThresholdChanges = 0
RegionAlgorithmChanges = 0
B_visualChanges = 0
K_spatialChanges = 0
ColorVocabularyChanges = 0
TextureRuleChanges = 0
ShapeRuleChanges = 0
```

Any poor result is evidence.

No tuning during trial.

---

# 10. Trial Architecture Freeze

During Trial 01:

```text
ArchitectureChanges = 0
LawChanges = 0
NewPrimitives = 0
GraphLifecycleChanges = 0
Law1Changes = 0
Law2Changes = 0
Law5Changes = 0
Law6Changes = 0
Law8Changes = 0
Law13Changes = 0
Law14Changes = 0
```

No architecture repair is authorized inside this experiment.

---

# 11. Phase A — Vision-Only Validation

Phase A uses image input only.

No text labels are ingested into DGCA.

No audio.

No cross-modal links.

The purpose is to evaluate:

\[
\boxed{
VisualRepresentation
}
\]

independently from:

\[
\boxed{
SemanticGrounding
}
\]

---

# 12. Phase A Exposure Set

For each of the 10 concepts:

use the 5 frozen exposure images.

Total Phase-A exposure images:

\[
\boxed{
50
}
\]

Each image is:

\[
\boxed{
OneVisualSceneScope
}
\]

Each image is processed exactly once during the primary Phase-A stream unless a separately frozen repeat-control requires otherwise.

---

# 13. Phase A Ordering

Use deterministic ordering.

Recommended:

```text
SHA256("RI01-A-ORDER-v1\0" || ImageID)
```

Sort ascending.

Do not group all images by concept unless a frozen control requires it.

Interleave concepts to ensure that persistence and reinforcement occur across unrelated visual episodes.

---

# 14. Visual Signature Definition

For evaluation only, define each image's encoder-level perceptual signature as the frozen set of emitted shared visual feature identities and bounded spatial relations after removing scene-local instance identity.

Example:

```text
{
  vis:clr:red,
  vis:lum:medium,
  vis:compact:high,
  vis:elong:low,
  vis:tex:smooth,
  vis:ori:mixed,
  vis:sz:large
}
```

This signature is not a new cognitive primitive.

It is an evaluation projection of existing emitted evidence.

---

# 15. Pairwise Visual Overlap

For two image signatures \(F_a,F_b\), compute a diagnostic overlap such as:

\[
J(F_a,F_b)
=
\frac{|F_a\cap F_b|}
{|F_a\cup F_b|}
\]

This metric is evaluation-only.

It must not be used by DGCA learning.

Report:

- within-concept overlap;
- between-concept overlap;
- visually confusable pair overlap.

No threshold is added post hoc to the encoder.

---

# 16. Within-Concept Consistency

For each concept \(c\):

\[
Consistency(c)
=
Median_{a\neq b\in c}
J(F_a,F_b)
\]

Also report:

```text
MinimumWithinConceptOverlap
MedianWithinConceptOverlap
MaximumWithinConceptOverlap
```

The goal is to measure stability, not force an arbitrary threshold.

---

# 17. Between-Concept Separability

For each pair of concepts \(c_i,c_j\):

\[
SeparabilityDistance
=
1-
Median\ J(F_a,F_b)
\]

over cross-concept image pairs.

Report the most confusable pairs.

Do not treat high overlap as semantic failure automatically; inspect which low-level properties legitimately overlap.

---

# 18. Visual Collision Audit

Identify cases where two different semantic concepts produce identical or near-identical encoder-level visual signatures.

Record:

```text
ConceptA
ConceptB
ImageA
ImageB
SignatureA
SignatureB
SharedFeatures
DifferentFeatures
```

A collision is diagnostic.

Do not patch it during the trial.

---

# 19. Persistent Graph Formation

For every exposure image, record:

```text
PersistentVisualNodesCreated
PersistentVisualNodesReused
PersistentVisualEdgesCreated
PersistentVisualEdgesReused
PersistentVisualEdgesReinforced
TransientInstancesCreated
TransientInstancesRetired
```

The trial must prove that real photographs create actual persistent graph structure.

---

# 20. Shared Feature Reinforcement

For recurring visual feature relations across independent images, track:

```text
EdgeID
FirstImageID
LaterImageID
WeightBefore
WeightAfter
ObservationCountBefore
ObservationCountAfter
SameEdgeIdentity
```

Required classification:

```text
REINFORCED
RECREATED
UNRESOLVED
```

Recreation due to inactivity is forbidden.

---

# 21. Phase A Persistence Controls

Freeze at least 10 early visual relations after the first 10 exposure images.

Recheck them after:

```text
10 images
25 images
50 images
```

Record:

```text
Alive
SameEdgeIdentity
Weight
LawfulUpdates
```

Required:

\[
PassiveVisualLoss=0
\]

---

# 22. Transient Lifecycle Control

For every image:

\[
inst:vis:*
\]

must exist only within lawful scene scope.

After scope closure:

```text
TransientInstancesAlive = 0
```

unless an explicitly active scope remains.

Persistent `vis:*` knowledge must survive.

Required:

```text
PersistentKnowledgeLostByTransientCleanup = 0
```

---

# 23. Phase A Held-Out Images

The 20 held-out images are not used during Phase-A exposure.

They are used only after the 50 exposure images are processed.

For each concept:

```text
2 held-out images
```

The encoder processes them normally on a read-only evaluation clone or non-learning path.

The evaluation checks:

- visual signature overlap with learned exposure signatures;
- retrieval of persistent visual structures;
- no training-state mutation.

---

# 24. Held-Out Visual Evaluation

For each held-out image record:

```text
ImageID
ConceptLabel_EvaluationOnly
EncoderStatus
VisualSignature
BestWithinConceptOverlap
BestCrossConceptOverlap
PersistentFeaturesRetrieved
PersistentRelationsRetrieved
EvaluationMutatedTrainingState
```

The test does not require semantic naming yet.

It asks whether unseen real images land near already experienced visual structure.

---

# 25. Phase A Adversarial / Variation Images

Use 10 frozen adversarial/variation images.

Recommended controls include:

```text
red apple vs red ball
green apple vs red apple
same object on light vs dark background
same class at smaller scale
same class at larger scale
partial occlusion
shifted position
different viewpoint
similar silhouette across different concepts
same color across different concepts
different color within same concept
```

These images are evaluation-only unless specifically frozen as exposure controls.

---

# 26. Phase A Scientific Outcomes

Allowed Phase-A labels:

```text
VISUAL_REPRESENTATION_STABLE
VISUAL_REPRESENTATION_PARTIALLY_STABLE
VISUAL_REPRESENTATION_UNSTABLE
VISUAL_COLLISION_RISK
BACKGROUND_DOMINANCE
SCALE_SENSITIVITY
ILLUMINATION_SENSITIVITY
PERSISTENT_VISUAL_LEARNING_DEMONSTRATED
VISUAL_REINFORCEMENT_DEMONSTRATED
TRANSIENT_LIFECYCLE_VALIDATED
MIXED_VISUAL_OUTCOME
```

---

# 27. Gate Before Phase B

Phase B may begin only if Phase A confirms all of:

1. raw real images are processed safely;
2. persistent visual structures are created;
3. transient retirement is correct;
4. no semantic leakage exists;
5. no hidden graph mutation occurs during read-only evaluation;
6. representation is not completely degenerate;
7. no catastrophic collision causes all concepts to collapse to the same signature.

If these fail, Phase B is not executed.

---

# 28. Phase B — Initial Text Grounding

Phase B begins from a clean graph unless the specification explicitly freezes use of the Phase-A learned visual baseline.

Canonical rule for Trial 01:

\[
\boxed{
PhaseBStart = CleanGraph
}
\]

Reason:

Phase B should measure grounding under a controlled multimodal curriculum, not inherit hidden visual exposure asymmetry from Phase A.

Phase-A results remain diagnostic evidence only.

---

# 29. Phase B Grounding Set

Use the same 10 concepts.

For each concept:

use:

```text
3 Grounding Images
```

selected from the 5 exposure images.

Total grounding images:

\[
\boxed{
30
}
\]

Each grounding event consists of:

1. one real image processed by Vision Encoder v2;
2. one text label processed independently by English Encoder v2;
3. both experiences placed within the same lawful external grounding episode or within the exact existing multimodal co-occurrence mechanism;
4. no direct manual edge injection.

---

# 30. Grounding Rule

Forbidden:

```text
graph.link("text:apple", visual_feature, ...)
```

Forbidden:

manual `sim` injection.

Forbidden:

paired_text inside Vision Encoder.

Required:

\[
ImageExperience
+
TextExperience
\rightarrow
ExistingDGCALearningLaws
\]

Cross-modal association must emerge through lawful DGCA graph learning only.

---

# 31. Independent Grounding Evidence

Each concept receives 3 independent grounding episodes:

\[
G_1,G_2,G_3
\]

Each uses a different real photograph.

Thus:

\[
SameConcept
+
DifferentVisualInstances
+
SameTextLabel
\]

allows DGCA to reinforce cross-modal structure that recurs across independent visual experiences.

---

# 32. Cross-Modal Association Accounting

For each concept record:

```text
TextConceptNode
GroundingEpisodeID
VisualInstanceID
SharedVisualFeatureNodes
CrossModalEdgesCreated
CrossModalEdgesReinforced
SameEdgeIdentity
WeightsBeforeAfter
ObservationCountsBeforeAfter
```

No new cross-modal law is introduced.

Existing learning rules only.

---

# 33. Text Label Semantics

The text label must be minimal and unambiguous.

Canonical form:

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

Do not use descriptive sentences in Trial 01 grounding unless explicitly frozen.

Reason:

isolate visual-to-lexical grounding before richer semantic language.

---

# 34. Grounding Evaluation Images

For each concept, reserve:

```text
2 held-out images
```

not used in Phase-B grounding.

Total:

\[
\boxed{
20
}
\]

These test whether the learned text concept can be accessed from a new visual instance.

---

# 35. Cross-Modal Held-Out Evaluation

For a held-out image:

1. process image through Vision Encoder v2 on read-only clone;
2. allow existing retrieval/cognition path to activate learned graph structure;
3. query/retrieve associated text concept without supplying class label;
4. record output.

Required classifications:

```text
CORRECT_TEXT_CONCEPT_RETRIEVED
WRONG_TEXT_CONCEPT_RETRIEVED
NO_TEXT_CONCEPT_RETRIEVED
AMBIGUOUS
```

No learning during evaluation.

---

# 36. Reverse Retrieval Control

Also test the reverse direction:

\[
TextLabel
\rightarrow
LearnedVisualStructure
\]

For each concept, provide text label only and inspect whether associated persistent visual feature structure is retrievable.

This does not require image generation.

It tests graph grounding symmetry/accessibility.

---

# 37. Cross-Modal Reinforcement

For each concept compare grounding episode 1 versus 2 versus 3.

Expected scientific pattern:

\[
G_1:
CreateCrossModalAssociation
\]

\[
G_2,G_3:
ReinforceExistingCrossModalAssociation
\]

where visual evidence overlaps lawfully.

Record creation vs reinforcement separately.

---

# 38. Grounding Specificity

A valid grounding should not reduce every visual feature in an image to semantic truth.

For example, if all apple images have different backgrounds, background-specific visual features should receive weaker/less recurrent cross-modal support than recurring object-related features.

This is an observation target, not a hard-coded rule.

The trial should inspect whether repeated independent images naturally favor recurring visual descriptors.

---

# 39. Background-Control Grounding

At least one concept must have three grounding images with visibly different backgrounds.

Measure whether:

```text
text:<concept>
```

reinforces shared recurring visual features more consistently than one-off background features.

Do not implement special background suppression.

---

# 40. Color-Variation Grounding

At least one concept should vary in color when semantically valid.

Example:

```text
red apple
green apple
```

This tests whether the concept can remain grounded through multiple visual patterns without requiring identical color.

Again, no special invariance code is authorized.

---

# 41. Confusable Pair Control

At least one pair should be deliberately confusable at the low-level feature level.

Recommended:

```text
apple vs ball
cup vs bottle
cat vs dog
```

Evaluate whether independent grounding plus visual differences is sufficient to avoid complete lexical collapse.

---

# 42. No Blind Co-Occurrence Claim

Trial 01 may demonstrate cross-modal association.

It must NOT yet claim that DGCA has solved multimodal causal grounding generally.

A later conflict-control trial will explicitly test:

```text
Image(cat) + Text(dog)
```

and contradictory sensory pairing.

That is outside this Trial 01 unless a minimal negative control is explicitly frozen.

---

# 43. Minimal Negative Control

Trial 01 may include one read-only/non-learning negative comparison:

a held-out image from concept A should not retrieve concept B solely because of shared color.

No contradictory training is performed.

---

# 44. Evaluation Isolation

All held-out evaluation must use:

\[
\boxed{
ReadOnlyClone
}
\]

or an equivalent proven non-learning path.

Training-state digest before evaluation must equal after evaluation.

Required:

```text
EvaluationMutation = 0
```

---

# 45. Dataset Freeze

Before execution, produce:

```text
ri01_image_manifest.json
```

containing all 80 images.

Also produce:

```text
ri01_phase_a_manifest.json
ri01_phase_b_manifest.json
```

No image substitutions after scientific execution begins.

---

# 46. Determinism Control

For at least 10 representative real images:

run Vision Encoder v2 30 times each.

Required:

```text
SameStatus
SameRegions
SameFeatures
SameRelations
SameIRDigest
```

for all replays.

Target:

\[
\boxed{
300/300\ bit\text{-}identical
}
\]

if 10 images × 30 runs are used.

---

# 47. Encoder Disposition Accounting

Report:

```text
COMPLETE
SAFE_PARTIAL
UNSUPPORTED
DecodeFailures
RegionFailures
```

for all 80 images.

Do not silently drop unsupported images.

---

# 48. Region Accounting

For every image record:

```text
RegionCount
DominantRegionAreaRatio
FeatureCount
SpatialRelationCount
Status
```

If an image has many regions, this is evidence to inspect.

Do not automatically label it failure.

---

# 49. Feature Frequency Accounting

Across Phase A, record frequency of each canonical `vis:*` feature.

This detects collapse such as:

```text
90% of images -> same exact feature set
```

or one feature dominating all representations.

Metrics are diagnostic only.

---

# 50. Persistent Graph Growth

At checkpoints:

```text
A0
A10
A25
A50
```

record:

```text
PersistentVisualNodesAlive
PersistentVisualEdgesAlive
VisualEdgesReinforced
TransientNodesAlive
GraphBytes
```

For Phase B:

```text
B0
B10
B20
B30
```

record cross-modal graph growth separately.

---

# 51. Phase A Checkpoints

Canonical:

```text
A0  = clean graph
A10 = after 10 exposure images
A25 = after 25 exposure images
A50 = after 50 exposure images
```

Evaluate early visual persistence at each checkpoint.

---

# 52. Phase B Checkpoints

Canonical:

```text
B0  = clean graph
B10 = after 10 grounding episodes
B20 = after 20 grounding episodes
B30 = after 30 grounding episodes
```

At each checkpoint report:

```text
VisualPersistentEdges
CrossModalEdges
CrossModalEdgesReinforced
TextConceptsGrounded
```

---

# 53. Vision-Only Retrieval Definition

A held-out image is considered visually connected to prior experience if existing persistent visual feature structure can be retrieved or activated without modifying training state.

Do not call this semantic recognition.

Use:

```text
VISUAL_STRUCTURE_RETRIEVED
```

not:

```text
OBJECT_RECOGNIZED
```

unless text grounding is involved.

---

# 54. Semantic Retrieval Definition

After Phase B, semantic visual recognition is operationally defined for this trial as:

\[
HeldOutImage
\rightarrow
CorrectAssociatedTextConcept
\]

through existing DGCA retrieval.

This is a bounded empirical definition, not a claim of general image understanding.

---

# 55. Primary Phase-A Metrics

Report:

```text
TotalRealImages
Complete
SafePartial
Unsupported

MedianWithinConceptOverlap
MedianBetweenConceptOverlap
MostConfusableConceptPair

PersistentVisualNodesCreated
PersistentVisualEdgesCreated
PersistentVisualEdgesReinforced

EarlyVisualRelations
EarlyRelationsAliveAtA50
PassiveVisualLoss

TransientInstancesCreated
TransientInstancesRetired
PersistentKnowledgeLostByCleanup

HeldOutImages
HeldOutVisualStructureRetrieved
```

---

# 56. Primary Phase-B Metrics

Report:

```text
GroundingConcepts
GroundingEpisodes
CrossModalEdgesCreated
CrossModalEdgesReinforced

TextConceptsWithPersistentVisualGrounding

HeldOutGroundingImages
CorrectTextConceptRetrieved
WrongTextConceptRetrieved
NoTextConceptRetrieved
Ambiguous

ReverseTextToVisualRetrieval

UnsupportedClaims
EvaluationMutation
```

---

# 57. No Arbitrary Accuracy Threshold

Trial 01 must not invent a post-hoc threshold such as:

```text
80% = understanding
```

Instead report exact empirical behavior.

However, protocol integrity requires:

```text
SemanticLeakage = 0
EvaluationMutation = 0
PersistentKnowledgeLostByCleanup = 0
HiddenPassiveForgetting = 0
```

These are strict zero-failure requirements.

---

# 58. Visual Consistency Interpretation

Possible outcomes:

### Strong Consistency

Within-concept overlap is systematically higher than unrelated between-concept overlap.

### Partial Consistency

Some concepts show stable recurring structure while others are dominated by viewpoint/background variation.

### Weak Consistency

Within-concept images often share little more structure than unrelated images.

No outcome triggers repair inside the trial.

---

# 59. Grounding Interpretation

Possible outcomes:

### Grounding Demonstrated

Repeated independent image-text episodes create persistent cross-modal associations and held-out images retrieve correct text concepts above baseline behavior.

### Grounding Partial

Associations form for some concepts but fail for others.

### Grounding Failure

Visual representations exist but fail to support stable text association.

### Retrieval Bottleneck

Cross-modal associations are structurally stored but held-out retrieval does not reach them.

---

# 60. Required Protocol Invariants

### RI01-INV-001 — Frozen Vision Encoder

No Vision v2 semantic change during trial.

### RI01-INV-002 — Real Images

Scientific evidence uses real photographs.

### RI01-INV-003 — No Semantic Label Into Vision Encoder

Evaluation labels never enter the encoder.

### RI01-INV-004 — One Image = One Visual Scene Scope

Scene identity remains bounded.

### RI01-INV-005 — Explicit Transient Retirement

No passive visual instance decay.

### RI01-INV-006 — Persistent Visual Knowledge Survives Scope Closure

Transient cleanup cannot remove persistent shared knowledge.

### RI01-INV-007 — Vision-Only Before Grounding

Phase A contains no text learning.

### RI01-INV-008 — Phase-B Clean Start

Grounding starts from clean graph.

### RI01-INV-009 — No Manual Cross-Modal Edge Injection

All grounding uses lawful DGCA learning.

### RI01-INV-010 — Independent Grounding Images

Each concept uses different real images across grounding episodes.

### RI01-INV-011 — Held-Out Images Never Learn

Held-out evaluation is read-only.

### RI01-INV-012 — Evaluation Does Not Mutate Training

Digest before/after evaluation matches.

### RI01-INV-013 — No Pretrained Semantic Vision Model

Vision v2 remains semantically blind.

### RI01-INV-014 — No Performance-Driven Repair

Failures are recorded.

### RI01-INV-015 — No Threshold Added Post Hoc

No success boundary is invented after results.

### RI01-INV-016 — Visual Instance != Concept

Scene-local identity does not become semantic identity.

### RI01-INV-017 — SameColor != SameConcept

No evaluation assumes color equality proves semantic equality.

### RI01-INV-018 — Raw Lifecycle Evidence Preserved

Per-image graph effects remain auditable.

### RI01-INV-019 — No Architecture Change

DGCA laws/ownership remain frozen.

### RI01-INV-020 — Scientific Claim Bounded

Trial result does not claim general computer vision.

Required:

\[
\boxed{
20/20
}
\]

---

# 61. Phase-A Verification Gates

### RI01-A-G01 — Dataset Frozen

All real images and hashes fixed before run.

### RI01-A-G02 — Semantic Firewall

No class label reaches encoder.

### RI01-A-G03 — Real-Image Intake

All supported images pass raw-pixel v2 path.

### RI01-A-G04 — Determinism

Representative replays are bit-identical.

### RI01-A-G05 — Persistent Visual Formation

Real images create persistent visual graph structure.

### RI01-A-G06 — Visual Reinforcement

Recurring shared visual evidence reinforces existing edges.

### RI01-A-G07 — Visual Persistence

Early persistent visual relations survive to A50.

### RI01-A-G08 — Transient Lifecycle

All scene-local instances retire lawfully.

### RI01-A-G09 — Persistent Cleanup Isolation

Transient retirement loses zero persistent knowledge.

### RI01-A-G10 — Held-Out Evaluation Isolation

Held-out images do not mutate training.

### RI01-A-G11 — Representation Diagnostics Complete

Within/between concept overlap and collision diagnostics complete.

### RI01-A-G12 — Phase-A Scientific Classification Complete

Evidence-backed visual representation verdict produced.

Required protocol condition:

\[
\boxed{
12/12\ PASS
}
\]

for valid Phase A.

---

# 62. Phase-B Verification Gates

### RI01-B-G01 — Clean B0

Phase B begins from clean graph.

### RI01-B-G02 — Independent Encoder Paths

Vision and English encoders operate separately.

### RI01-B-G03 — No Manual Edge Injection

Cross-modal links emerge from DGCA learning.

### RI01-B-G04 — Cross-Modal Formation

Grounding episodes create auditable visual-text association.

### RI01-B-G05 — Cross-Modal Reinforcement

Repeated independent grounding reinforces existing associations where recurring evidence supports them.

### RI01-B-G06 — Held-Out Image Retrieval

Held-out images can be evaluated for text-concept retrieval.

### RI01-B-G07 — Reverse Retrieval

Text-to-visual access is measured.

### RI01-B-G08 — No Semantic Leakage

Vision encoder remains label-blind.

### RI01-B-G09 — Evaluation Isolation

No held-out evaluation mutates training.

### RI01-B-G10 — No Hidden Forgetting

No inactivity-driven visual/cross-modal loss.

### RI01-B-G11 — Grounding Diagnostics Complete

Correct/wrong/no/ambiguous retrieval counts reported.

### RI01-B-G12 — Phase-B Scientific Classification Complete

Evidence-backed grounding verdict produced.

Required protocol condition:

\[
\boxed{
12/12\ PASS
}
\]

for valid Phase B.

---

# 63. Stop Conditions

Stop the affected phase only for true protocol blockers:

- semantic class label reaches Vision Encoder;
- pretrained semantic vision path is activated;
- evaluation mutates training state;
- persistent knowledge is deleted by transient cleanup;
- hidden passive forgetting reappears;
- image manifest changes after freeze;
- graph corruption;
- architecture change becomes necessary;
- instrumentation changes cognition.

Do not stop because:

- some images are SAFE_PARTIAL;
- some images are UNSUPPORTED;
- within-concept overlap is weak;
- confusable concepts collide;
- grounding accuracy is poor;
- held-out text retrieval fails.

Those are scientific outcomes.

---

# 64. Required Machine-Readable Artifacts

Produce at minimum:

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

---

# 65. Required Phase-A Final Answers

The report must explicitly answer:

1. How many real images were COMPLETE / SAFE_PARTIAL / UNSUPPORTED?
2. Did real photographs create persistent visual graph structure?
3. Did shared visual evidence reinforce existing edges?
4. Was any persistent visual edge recreated due to inactivity?
5. Did early visual relations survive to A50?
6. Was transient cleanup lossless for persistent knowledge?
7. What was median within-concept overlap?
8. What was median between-concept overlap?
9. Which concept pair was most visually confusable?
10. Did same-concept images show more recurring structure than unrelated images?
11. Did background variation dominate any concept?
12. Did moderate scale variation destroy overlap?
13. Did moderate illumination variation destroy overlap?
14. Did held-out images retrieve previously learned visual structure?
15. Is visual representation stable enough to proceed to text grounding?

---

# 66. Required Phase-B Final Answers

The report must explicitly answer:

1. Did image-text grounding create persistent cross-modal associations?
2. Did repeated independent grounding reinforce them?
3. How many of 10 concepts acquired persistent visual-text grounding?
4. On 20 held-out images, how many retrieved the correct text concept?
5. How many retrieved the wrong concept?
6. How many retrieved no concept?
7. How many were ambiguous?
8. Did reverse text-to-visual retrieval work?
9. Did background-specific one-off features dominate cross-modal grounding?
10. Did varying color destroy concept grounding?
11. Did confusable pairs collapse into the same text concept?
12. Did any manual cross-modal edge injection occur?
13. Did any semantic label reach Vision Encoder v2?
14. Did held-out evaluation mutate training?
15. Is initial real-image semantic grounding empirically demonstrated?

---

# 67. Allowed Scientific Outcome Labels

Phase A:

```text
REAL_IMAGE_VISUAL_REPRESENTATION_DEMONSTRATED
VISUAL_REPRESENTATION_PARTIALLY_STABLE
VISUAL_REPRESENTATION_UNSTABLE
PERSISTENT_VISUAL_LEARNING_DEMONSTRATED
VISUAL_REINFORCEMENT_DEMONSTRATED
VISUAL_COLLISION_RISK
BACKGROUND_DOMINANCE
SCALE_SENSITIVITY
ILLUMINATION_SENSITIVITY
MIXED_VISUAL_OUTCOME
```

Phase B:

```text
REAL_IMAGE_TEXT_GROUNDING_DEMONSTRATED
PARTIAL_VISUAL_TEXT_GROUNDING
VISUAL_TEXT_GROUNDING_FAILURE
CROSSMODAL_RETRIEVAL_BOTTLENECK
CROSSMODAL_COLLISION_RISK
MIXED_GROUNDING_OUTCOME
```

---

# 68. Interpretation Discipline

Forbidden conclusions unless directly supported:

- "DGCA understands vision generally."
- "DGCA recognizes arbitrary objects."
- "Vision is solved."
- "Same feature overlap means same semantic object."
- "One correct held-out retrieval proves generalization."
- "Low overlap proves Encoder failure without inspecting visual causes."
- "Background variation should be fully invariant."
- "Color should be ignored."
- "Text grounding proves causal understanding."
- "Video readiness" from static-image results.

---

# 69. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — SMALL REAL-IMAGE SCIENTIFIC TRIAL 01

VISION ENCODER:
V2 — FROZEN

ARCHITECTURE CHANGES:
0

ENCODER CHANGES:
0

REAL IMAGE CONCEPTS:
10

TOTAL REAL IMAGES:
80

PHASE A — VISION ONLY

Exposure Images:
50

COMPLETE:
...

SAFE_PARTIAL:
...

UNSUPPORTED:
...

Persistent Visual Nodes:
...

Persistent Visual Edges:
...

Visual Edges Reinforced:
...

Recreated Due To Inactivity:
0 / NONZERO

Early Visual Relations:
...

Alive At A50:
...

Passive Visual Loss:
0 / NONZERO

Transient Instances Created:
...

Transient Instances Retired:
...

Persistent Knowledge Lost By Cleanup:
0 / NONZERO

Median Within-Concept Overlap:
...

Median Between-Concept Overlap:
...

Most Confusable Pair:
...

Held-Out Images:
20

Held-Out Visual Structure Retrieved:
...

PHASE-A INVARIANTS:
x / 20 applicable

PHASE-A GATES:
x / 12

PHASE-A SCIENTIFIC OUTCOME:
...

PHASE B — TEXT GROUNDING

Clean B0:
YES / NO

Grounding Concepts:
10

Grounding Episodes:
30

Manual Cross-Modal Edge Injection:
0 / NONZERO

Cross-Modal Edges Created:
...

Cross-Modal Edges Reinforced:
...

Concepts With Persistent Grounding:
...

Held-Out Grounding Images:
20

Correct Text Concept Retrieved:
...

Wrong Text Concept Retrieved:
...

No Text Concept Retrieved:
...

Ambiguous:
...

Reverse Text-To-Visual Retrieval:
...

Semantic Label Leakage Into Vision Encoder:
0 / NONZERO

Evaluation Mutation:
0 / NONZERO

PHASE-B GATES:
x / 12

PHASE-B SCIENTIFIC OUTCOME:
...

HIDDEN PASSIVE FORGETTING:
0 / NONZERO

FULL REGRESSION:
PASS / FAIL

POST-TRIAL ARCHITECTURE SIGNATURE:
...

SIGNATURE STATUS:
MATCH / MISMATCH

PROTOCOL INTEGRITY:
PROTOCOL_PASS / PROTOCOL_FAIL / BLOCKED

FINAL SCIENTIFIC VERDICT:
...

READY FOR AUDIO ENCODER V2 AUDIT/IMPLEMENTATION:
YES / NO

READY FOR LARGER REAL-IMAGE DATA:
YES / NO

READY FOR LARGE-SCALE MULTIMODAL TRAINING:
NO
============================================================
```

---

# 70. Closure Rule

The trial is scientifically successful if it clearly determines whether:

\[
\boxed{
RealImages
\rightarrow
StablePersistentVisualStructure
}
\]

and, if Phase B proceeds:

\[
\boxed{
RepeatedRealImage + TextLabel
\rightarrow
PersistentCrossModalGrounding
}
\]

without:

\[
SemanticLeakage
\]

without:

\[
ManualEdgeInjection
\]

without:

\[
HiddenForgetting
\]

and without changing the frozen architecture.

---

# 71. Final Scientific Principle

Trial 01 must preserve the distinction:

\[
\boxed{
VisualRepresentation
\neq
SemanticGrounding
}
\]

First prove that real images produce stable reusable visual structure.

Then test whether DGCA can learn what that structure means.

The scientific target is:

\[
\boxed{
Pixels
\rightarrow
PersistentVisualEvidence
\rightarrow
CrossModalGrounding
}
\]

not:

\[
\boxed{
Pixels
\rightarrow
PretrainedSemanticAnswer
}
\]

