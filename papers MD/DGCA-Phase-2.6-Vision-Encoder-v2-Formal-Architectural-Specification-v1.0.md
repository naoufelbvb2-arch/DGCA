# DGCA Phase 2.6 — Vision Encoder v2 Formal Architectural Specification v1.0

## Deterministic Low-Level Perceptual Compiler for Raw Static Images

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Component:** Vision Encoder v2  
**Document Type:** Formal Architectural Specification  
**Version:** 1.0  
**Status:** **ARCHITECTURAL DESIGN — CANDIDATE FOR FREEZE**  
**Implementation Status:** **PENDING**  
**Architecture Baseline:** Post-Law-3-Abolition DGCA  
**Canonical Baseline Signature:** `915119d40643cb97`  
**Legacy Vision Reference:** RFC-06 / current `dgca/vision.py`  
**New Cognitive Primitives:** `0`  
**New Normative Laws:** `0`  
**Persistent Cognitive Schema Delta:** `0`  
**Primary Principle:** **The encoder describes visual evidence; DGCA learns meaning.**

---

# 1. Purpose

Vision Encoder v2 replaces the legacy feature-to-episode visual frontend with a deterministic raw-pixel perceptual compiler.

The legacy path begins from pre-extracted objects:

```text
VisualObject(color, shape, size, bbox)
-> SensoryEpisode
```

Vision Encoder v2 begins from actual image pixels:

\[
\boxed{
RawPixels
\rightarrow
PerceptualRegions
\rightarrow
MeasuredVisualStructure
\rightarrow
VisualFrameIR
\rightarrow
ExistingSensoryEpisode
}
\]

The encoder must not inject semantic object identity.

It may describe:

```text
red
bright
compact
elongated
smooth
left_of
inside
large
```

It must not directly emit:

```text
apple
dog
car
person
tree
```

unless such semantic identity is learned later by DGCA through lawful cross-modal experience.

---

# 2. Governing Architectural Principle

The primary design law of Vision Encoder v2 is:

\[
\boxed{
EncoderMayDescribeSignal
}
\]

but:

\[
\boxed{
EncoderMustNotSupplyLearnedMeaning
}
\]

Equivalently:

\[
\boxed{
Pixels
\rightarrow
PerceptualStructure
}
\]

but not:

\[
\boxed{
Pixels
\rightarrow
SemanticLabel
}
\]

Semantic meaning remains cognitive graph-owned.

---

# 3. Architectural Role

Vision Encoder v2 is:

\[
\boxed{
\textbf{A deterministic low-level perceptual compiler}
}
\]

It is NOT:

- an object classifier;
- a semantic detector;
- a pretrained vision model;
- a caption generator;
- a world-knowledge module;
- a retrieval model;
- a multimodal grounding model.

Its responsibility ends when raw visual evidence has been converted into a bounded, reusable, graph-compatible sensory representation.

---

# 4. Constitutional Constraints

Vision Encoder v2 must preserve the following DGCA principles:

1. **No New Primitive Without Unique Necessity**
2. **No New Law Without Unique Necessity**
3. **Encoder remains graph-independent**
4. **No pretrained semantic intelligence hidden in the frontend**
5. **No persistent cognitive state owned by the encoder**
6. **No backpropagation**
7. **No learned visual classifier**
8. **Sparse bounded emission**
9. **Deterministic execution**
10. **No-Guess behavior under ambiguity**
11. **Existing SensoryEpisode contract preserved**
12. **Existing transient lifecycle authority preserved**
13. **No Law-3 semantics**
14. **Static-image scope only in v2.0**
15. **Cross-modal meaning remains outside the Vision Encoder**

---

# 5. High-Level Pipeline

The canonical pipeline is:

```text
Image Bytes
    |
    v
[1] Mechanical Decode
    |
    v
PixelFrame
    |
    v
[2] Canonical Normalization
    |
    v
CanonicalPixelFrame
    |
    +------------------+
    |                  |
    v                  v
[3A] Color Maps    [3B] Luminance / Edge Maps
    |                  |
    +---------+--------+
              |
              v
[4] Perceptual Region Formation
              |
              v
[5] Region Geometry & Appearance
              |
              v
[6] Sparse Visual Feature Encoding
              |
              v
[7] Bounded Spatial Topology
              |
              v
[8] Encoder-Local VisualFrameIR
              |
              v
[9] Existing SensoryEpisode Emission
              |
              v
             DGCA
```

Canonical contract:

\[
\boxed{
RawImage
\rightarrow
EncoderLocalIR
\rightarrow
ExistingSensoryEpisode
}
\]

---

# 6. Scope of v2.0

Vision Encoder v2.0 supports:

- static images;
- deterministic RGB decoding;
- low-level visual maps;
- deterministic region formation;
- geometry;
- appearance descriptors;
- sparse reusable sensory tokens;
- normalized spatial relations;
- transient visual instance identity;
- existing SensoryEpisode emission.

Vision Encoder v2.0 does NOT support:

- video;
- motion;
- optical flow;
- cross-frame tracking;
- object permanence across frames;
- semantic object detection;
- face recognition;
- OCR meaning;
- learned embeddings;
- scene captions;
- pretrained neural vision models.

---

# 7. Stage 1 — Mechanical Decode

The codec layer mechanically converts supported image input into a canonical pixel frame.

Recommended input contract:

```python
@dataclass(frozen=True)
class PixelFrame:
    width: int
    height: int
    channels: int
    pixels: bytes | array
    source_scope_id: str
```

The decoder may support PNG first.

JPEG or other formats may be added later as mechanical adapters.

Codec behavior must not:

- classify;
- segment semantically;
- infer object labels;
- change visual meaning.

---

# 8. Stage 2 — Canonical Normalization

The encoder must normalize mechanically without semantic inference.

Required normalization domains:

### 8.1 Coordinate normalization

All spatial coordinates must be mapped to:

\[
x,y \in [0,1]
\]

For a pixel coordinate:

\[
x_n = \frac{x}{W}
\]

\[
y_n = \frac{y}{H}
\]

Bounding boxes must be stored in normalized coordinates.

No spatial-relation rule may depend on fixed raw-pixel constants such as:

```text
+5 pixels
<20 pixels
```

### 8.2 Color-space normalization

Input must be converted deterministically to one canonical color space.

The implementation may internally use:

```text
RGB
```

and optionally a deterministic auxiliary space such as:

```text
HSV
Lab
```

for measurement.

### 8.3 Orientation metadata normalization

Image EXIF/orientation metadata must be resolved mechanically before visual analysis.

### 8.4 Resolution normalization

Resolution normalization may be used only if deterministic and documented.

It must preserve aspect ratio.

No learned rescaling is allowed.

---

# 9. Stage 3 — Low-Level Visual Maps

The encoder must derive visual evidence directly from pixels.

Required visual evidence families:

\[
Color
\]

\[
Luminance
\]

\[
LocalGradient
\]

\[
BoundaryStrength
\]

\[
TextureStatistics
\]

Optional deterministic diagnostics may include:

```text
edge magnitude
gradient orientation
local variance
color histogram
```

These diagnostics remain encoder-local unless explicitly quantized into sensory features.

---

# 10. Color Representation

Region color must be measured from region pixels.

The encoder must not accept caller-supplied semantic color labels as authoritative input.

Recommended robust statistics:

\[
MedianColor(region)
\]

or:

\[
DominantHistogramBin(region)
\]

A region may emit one dominant color token:

```text
vis:clr:red
vis:clr:green
vis:clr:blue
vis:clr:yellow
vis:clr:orange
vis:clr:purple
vis:clr:brown
vis:clr:black
vis:clr:white
vis:clr:gray
```

The exact frozen color vocabulary must be deterministic and bounded.

No learned color classifier is permitted.

---

# 11. Luminance Representation

For region luminance:

\[
L = f(R,G,B)
\]

using one deterministic formula.

Quantize to one bounded token:

```text
vis:lum:dark
vis:lum:medium
vis:lum:bright
```

The exact thresholds must be frozen before implementation verification.

No semantic interpretation is attached to luminance.

---

# 12. Stage 4 — Perceptual Region Formation

Vision Encoder v2 replaces semantic "objects" with:

\[
\boxed{
PerceptualRegion
}
\]

A perceptual region is a spatially connected area supported by visual continuity.

Region formation may use:

\[
ColorContinuity
\]

\[
LuminanceContinuity
\]

\[
EdgeBoundaries
\]

\[
Connectedness
\]

A generic merge condition may be expressed as:

\[
Merge(p_i,p_j)
\iff
Adjacent(i,j)
\land
D_{visual}(i,j)\le\tau_r
\land
BoundaryStrength(i,j)<\tau_b
\]

where:

- \(\tau_r\) is fixed and deterministic;
- \(\tau_b\) is fixed and deterministic;
- neither is learned.

The exact algorithm must be deterministic.

---

# 13. Region Is Not Object

This invariant is mandatory:

\[
\boxed{
PerceptualRegion \neq SemanticObject
}
\]

A real semantic object may:

- correspond to one region;
- correspond to several regions;
- be partially merged with background;
- be partially occluded.

The encoder must not invent semantic object identity to hide region ambiguity.

If region formation is insufficiently stable:

```text
SAFE_PARTIAL
```

or:

```text
UNSUPPORTED
```

must be used instead of semantic guessing.

---

# 14. Region Filtering

The encoder may reject visual noise regions using deterministic geometric rules.

Examples:

```text
minimum area ratio
minimum connected support
minimum boundary support
```

Noise filtering must not depend on semantic category.

No rule may say:

```text
ignore if not object-like
```

unless "object-like" is defined purely by frozen low-level geometry.

---

# 15. Canonical Region Ordering

Region identity must be deterministic.

Recommended ordering:

\[
(y_{centroid}, x_{centroid}, -Area, MaskDigest)
\]

ascending lexicographically.

Then assign transient ranks:

```text
R00
R01
R02
...
```

Required:

\[
SameFrame + SameScope + SameConfig
\Rightarrow
SameRegionOrdering
\]

---

# 16. Stage 5 — Region Geometry

For each region compute:

\[
Area
\]

\[
Perimeter
\]

\[
BoundingBox
\]

\[
Centroid
\]

\[
AspectRatio
\]

\[
Elongation
\]

\[
Solidity
\]

\[
Compactness
\]

\[
Orientation
\]

All geometry must be measured from actual region support.

---

# 17. True Contour Requirement

The legacy real-image experiment derived perimeter from area, making circularity tautologically near 1.

Vision Encoder v2 must instead measure contour directly.

For a region:

\[
A = |\text{mask pixels}|
\]

\[
P = |\text{measured contour boundary}|
\]

Then:

\[
Circularity =
\frac{4\pi A}{P^2}
\]

The circularity score is valid only when \(P\) is independently measured from the boundary.

No derived-perimeter shortcut is allowed.

---

# 18. Shape Representation

Vision Encoder v2 must not assume all visual entities belong to:

```text
circle
square
triangle
rectangle
```

Instead, generic shape descriptors are primary:

```text
vis:compact:low
vis:compact:medium
vis:compact:high

vis:elong:low
vis:elong:medium
vis:elong:high

vis:solidity:low
vis:solidity:medium
vis:solidity:high
```

A discrete geometric class such as:

```text
vis:shp:circle
vis:shp:rectangle
vis:shp:triangle
```

may be emitted only when deterministic contour criteria are clearly satisfied.

If not:

no geometric-class token is emitted.

---

# 19. Texture Representation

Texture must be computed from local pixel structure.

Allowed deterministic measurements include:

\[
LocalGradientVariance
\]

\[
EdgeDensity
\]

\[
LocalPatternTransitionRate
\]

Quantized texture tokens may include:

```text
vis:tex:smooth
vis:tex:fine
vis:tex:coarse
vis:tex:mixed
```

Forbidden semantic texture labels include:

```text
fur
wood
metal
skin
```

unless learned later by DGCA.

---

# 20. Orientation Representation

A bounded gradient-orientation histogram may be used.

Example canonical bins:

\[
0^\circ,\ 45^\circ,\ 90^\circ,\ 135^\circ
\]

Emit at most one dominant-orientation token:

```text
vis:ori:horizontal
vis:ori:vertical
vis:ori:diag_pos
vis:ori:diag_neg
vis:ori:mixed
```

Orientation must remain visual evidence, not semantic interpretation.

---

# 21. Relative Size

Region size should be normalized to frame area:

\[
r_A = \frac{Area(region)}{Area(frame)}
\]

Quantize to:

```text
vis:sz:small
vis:sz:medium
vis:sz:large
```

Thresholds must be frozen and resolution-independent.

---

# 22. Sparse Visual Feature Budget

The encoder must emit a bounded number of reusable sensory identity features per region.

Canonical maximum:

\[
\boxed{
B_{visual}=8
}
\]

Recommended feature families:

1. dominant color
2. luminance
3. compactness
4. elongation
5. solidity or clear geometric class
6. texture
7. dominant orientation
8. relative size

No learned ranking.

No unbounded top-N feature extraction.

No semantic probability distribution.

---

# 23. Feature Emission Rule

For every region:

\[
|Features(region)| \le B_{visual}
\]

If a feature family is ambiguous:

omit that feature.

Do not replace missing evidence with a guessed token.

Therefore:

\[
NoEvidence
\Rightarrow
NoFeature
\]

not:

\[
NoEvidence
\Rightarrow
BestGuessFeature
\]

---

# 24. Stage 6 — Transient Visual Instance Identity

Each perceptual region receives a transient scene-local identity:

```text
inst:vis:<scope_id>:<region_rank>
```

Example:

```text
inst:vis:S104:R03
```

A later scene receives a different identity even for the same semantic object:

```text
inst:vis:S105:R01
```

Required:

\[
\boxed{
VisualInstanceIdentity \neq ConceptIdentity
}
\]

The encoder must not persist scene-specific instance identity across unrelated images.

---

# 25. Shared Feature Identity

Reusable visual descriptors use shared canonical tokens:

```text
vis:clr:red
vis:tex:smooth
vis:compact:high
vis:sz:large
```

These feature identities may recur across scenes.

This permits DGCA to discover recurring visual structure through ordinary graph learning.

---

# 26. Stage 7 — Bounded Spatial Topology

Vision Encoder v2 must emit bounded spatial relations between regions.

Allowed core relations:

```text
left_of
right_of
above
below
inside
contains
touching
near
overlap
```

All spatial rules must use normalized coordinates.

No raw-pixel thresholds.

---

# 27. Local Spatial Neighborhood

The encoder must not emit all pairwise relations for all regions.

Instead, use a bounded local topology.

For each region, select only a limited number of nearest spatially relevant neighbors.

Required:

\[
RelationsPerRegion \le K_{spatial}
\]

with frozen small \(K_{spatial}\).

Target complexity:

\[
\boxed{
|E_{spatial}| = O(N)
}
\]

for \(N\) regions.

---

# 28. Example Spatial Rule

For normalized bounding boxes:

\[
left\_of(A,B)
\]

may be emitted if:

\[
x^A_{max} + \epsilon_x < x^B_{min}
\]

where:

\[
\epsilon_x
\]

is a normalized deterministic tolerance.

The tolerance must not depend on image resolution in pixels.

---

# 29. Focal Region Semantics

A focal region may be selected mechanically for:

- relation ordering;
- bounded neighborhood prioritization;
- deterministic emission order;
- diagnostics.

Focal-region status must NOT create cognitive weight privilege.

Forbidden:

\[
FocalRegion
\Rightarrow
W=0.80
\]

or any equivalent direct learned-weight assignment.

Required:

\[
\boxed{
VisualSalience \neq LearnedWeightAuthority
}
\]

Law 3 is abolished and no anti-decay privilege remains justified.

---

# 30. Removal of `paired_text`

Vision Encoder v2 must not accept paired semantic text as part of the visual encoding contract.

Forbidden API pattern:

```python
process_scene(..., paired_text="apple")
```

Vision encoding and cross-modal grounding must be separate.

Required decomposition:

```text
VisionEncoderV2
-> Visual SensoryEpisode(s)

EnglishEncoderV2
-> Text SensoryEpisode(s)

CrossModal Grounding
-> DGCA learning
```

This prevents accidental binding of one text label to every region in a multi-object scene.

---

# 31. Multimodal Boundary

Vision Encoder v2 ends before semantic fusion.

It must not decide:

```text
this region corresponds to the word apple
```

That relationship belongs to later multimodal grounding.

Therefore:

\[
\boxed{
CrossModalMeaningBelongsToDGCA
}
\]

not to Vision Encoder v2.

---

# 32. Encoder-Local IR

The canonical local IR is:

```python
@dataclass(frozen=True)
class VisualRegionIR:
    region_id: str
    bbox_norm: tuple[float, float, float, float]
    centroid_norm: tuple[float, float]
    area_ratio: float
    features: tuple[str, ...]
    mask_digest: str

@dataclass(frozen=True)
class VisualRelationIR:
    subject_region: str
    relation: str
    reference_region: str

@dataclass(frozen=True)
class VisualFrameIR:
    scope_id: str
    status: str
    regions: tuple[VisualRegionIR, ...]
    relations: tuple[VisualRelationIR, ...]
```

This IR is:

\[
\boxed{
EncoderLocalTransientIR
}
\]

It is not a DGCA persistent cognitive primitive.

---

# 33. IR Purity

VisualFrameIR must be:

- immutable;
- deterministic;
- graph-independent;
- free of learned semantic labels;
- free of learned weights;
- free of persistent cognitive ownership.

The encoder must not read graph state to decide visual interpretation.

Required:

\[
EncoderOutput = f(Image, Config, ScopeID)
\]

not:

\[
EncoderOutput = f(Image, GraphKnowledge)
\]

---

# 34. Existing SensoryEpisode Contract

The v2 emitter must preserve the existing DGCA sensory episode contract wherever possible.

The encoder may emit one bounded sensory episode per perceptual region plus bounded spatial relation episodes if that is the existing lawful representation pattern.

No new persistent schema is authorized.

If current SensoryEpisode cannot represent one required field without semantic loss, implementation must report a blocker instead of silently creating a new persistent primitive.

---

# 35. Scene Scope

Each static image is:

\[
\boxed{
OneVisualSceneScope
}
\]

All `inst:vis:*` identities belong to that scope.

After lawful scene completion:

\[
ScopeEnd
\rightarrow
ExplicitTransientRetirement
\]

using existing post-Law-3 lifecycle mechanisms.

No passive decay.

No time-based cleanup.

---

# 36. Persistent Feature Survival

Reusable sensory features and learned relations survive scene closure according to existing DGCA memory laws.

Scene closure must not delete persistent shared visual knowledge.

Required:

\[
TransientInstanceRetires
\]

while:

\[
PersistentVisualKnowledgeSurvives
\]

---

# 37. Encoder Disposition States

Vision Encoder v2 uses:

```text
COMPLETE
SAFE_PARTIAL
UNSUPPORTED
```

---

# 38. COMPLETE

Return `COMPLETE` when:

- image decoding succeeds;
- normalization succeeds;
- region formation is stable enough;
- all emitted features are supported by measured evidence;
- spatial relations are internally consistent;
- no high-severity ambiguity requires guessing.

---

# 39. SAFE_PARTIAL

Return `SAFE_PARTIAL` when:

- some low-level evidence is reliable;
- full region partition is not fully stable;
- some feature families are ambiguous;
- safe bounded emission is still possible.

SAFE_PARTIAL must emit only supported evidence.

It must never invent missing structure.

---

# 40. UNSUPPORTED

Return `UNSUPPORTED` when:

- image format cannot be decoded;
- image is outside frozen dimensional/resource limits;
- region extraction fails completely;
- input is malformed;
- no safe visual structure can be emitted.

UNSUPPORTED must fail closed.

---

# 41. No-Guess Contract

The governing uncertainty rule is:

\[
\boxed{
UncertainVision
\Rightarrow
NoInventedStructure
}
\]

No semantic confidence score may override this rule.

---

# 42. Forbidden Semantic Confidence

Vision Encoder v2 must not emit:

```text
apple probability = 0.83
dog confidence = 0.71
object class = car
```

Allowed encoder-local diagnostic values include:

```text
circularity = 0.73
edge_density = 0.21
mean_luminance = ...
```

These remain measurements, not semantic beliefs.

---

# 43. No Pretrained Models

Forbidden inside Vision Encoder v2:

- YOLO;
- CLIP;
- ImageNet classifiers;
- pretrained CNN embeddings;
- pretrained segmentation models;
- VLM captioning;
- face-recognition models;
- OCR semantic models;
- external LLM vision reasoning.

Reason:

\[
ExternalModelUnderstanding
\neq
DGCAUnderstanding
\]

---

# 44. Determinism

Required:

\[
SameImage
+
SameConfig
+
SameScope
\Rightarrow
SameVisualFrameIR
\]

The following must be deterministic:

- decode;
- normalization;
- region formation;
- region ordering;
- feature quantization;
- spatial relation emission;
- SensoryEpisode emission.

No random seeds may affect normative output.

---

# 45. Static Image Only

Version 2.0 is frozen to:

\[
\boxed{
StaticImageVisionOnly
}
\]

Do not implement:

- video;
- cross-frame motion;
- optical flow;
- visual tracking;
- temporal object identity;
- frame-to-frame persistence.

These belong to a later temporal-vision extension if justified.

---

# 46. Real-Image First Validation Strategy

The first empirical real-image validation after implementation must use:

\[
\boxed{
SingleDominantObjectPerImage
}
\]

with real photographs.

Reason:

- isolates raw-pixel visual encoding;
- minimizes ambiguous region-to-text grounding;
- separates segmentation defects from multimodal binding defects.

Recommended concept set later:

```text
apple
banana
cup
ball
tree
cat
dog
car
bird
bottle
```

The semantic labels belong to evaluation/grounding, not Vision Encoder v2 output.

---

# 47. Required Robustness Dimensions

Vision Encoder v2 must be tested across controlled changes in:

\[
Translation
\]

\[
ModerateScale
\]

\[
ModerateIllumination
\]

\[
Background
\]

The encoder need not be fully invariant.

It must preserve meaningful visual differences.

---

# 48. Non-Invariance Requirements

The encoder must NOT intentionally erase:

\[
Color
\]

\[
Orientation
\]

\[
RelativeSize
\]

because these may carry real cognitive meaning.

Therefore:

\[
Robustness \neq InformationErasure
\]

---

# 49. Canonical Adversarial Visual Controls

Future verification must include cases such as:

```text
red apple vs red ball
green apple vs red apple
same object on white vs dark background
same object at different scale
same object shifted left/right
different image resolution
partial occlusion
two objects in one frame
same color but different shape
same shape but different texture
```

The purpose is to prove:

\[
SameColor \neq SameConcept
\]

and:

\[
SameSemanticObject \neq SamePixels
\]

---

# 50. Canonical Architectural Invariants

### V2-INV-01 — Raw Pixels Are the Sensory Source

No caller-supplied object labels or shape/color declarations replace pixel measurement.

### V2-INV-02 — Encoder Is Graph-Independent

Vision encoding never reads cognitive graph state.

### V2-INV-03 — No Semantic Object Labels

Vision Encoder v2 does not emit learned semantic object identity.

### V2-INV-04 — No Pretrained Learned Vision Model

No pretrained model supplies visual meaning.

### V2-INV-05 — Region Is Not Semantic Object

Perceptual regions are low-level visual structure only.

### V2-INV-06 — Deterministic IR

Same input/config/scope produces identical VisualFrameIR.

### V2-INV-07 — Normalized Coordinates

All spatial reasoning uses canonical normalized coordinates.

### V2-INV-08 — True Contour Evidence

Shape/circularity uses independently measured contour geometry.

### V2-INV-09 — Bounded Feature Emission

Each region emits at most \(B_{visual}=8\) identity features.

### V2-INV-10 — Bounded Spatial Topology

Spatial relation count remains locally bounded.

### V2-INV-11 — No Paired-Text Injection

Vision Encoder v2 does not accept semantic paired text.

### V2-INV-12 — No Focal Weight Privilege

Focal visual status does not directly modify learned cognitive weight.

### V2-INV-13 — Visual Instance IDs Are Transient

`inst:vis:*` identities are scope-limited.

### V2-INV-14 — Feature Identities Are Reusable

Canonical `vis:*` feature tokens may recur across scenes.

### V2-INV-15 — Scene Closure Retires Transients

Visual transient instances retire explicitly at scope end.

### V2-INV-16 — No Persistent Graph Mutation Inside Encoder

The encoder itself owns no persistent learning state.

### V2-INV-17 — Unsupported Ambiguity Fails Closed

Ambiguity produces omission, SAFE_PARTIAL, or UNSUPPORTED.

### V2-INV-18 — Static Image Scope Only

Version 2.0 contains no temporal vision semantics.

### V2-INV-19 — No New Cognitive Primitive

VisualFrameIR and VisualRegionIR are encoder-local only.

### V2-INV-20 — Cross-Modal Meaning Belongs to DGCA

Semantic grounding is not owned by Vision Encoder v2.

Required:

\[
\boxed{
20/20
}
\]

---

# 51. Forbidden Mechanisms Audit

The implementation audit must prove absence of:

1. semantic class labels from encoder;
2. pretrained detector inference;
3. pretrained image embeddings;
4. text labels injected into region features;
5. raw-pixel spatial thresholds;
6. area-derived fake perimeter;
7. unbounded pairwise spatial graph;
8. focal-object weight bonus;
9. graph-state-dependent visual parsing;
10. persistent encoder memory;
11. passive Law-3 transient decay;
12. video tracking hidden inside v2.0;
13. random nondeterministic region ordering;
14. semantic confidence scores;
15. hidden object-name lookup table;
16. graph mutation during pure encoding.

Required:

\[
\boxed{
16/16\ PASS
}
\]

---

# 52. Required Canonical Unit Test Families

Implementation must include tests for:

### Decode
- valid PNG
- malformed PNG
- orientation metadata
- deterministic decode

### Normalization
- coordinate normalization
- resolution independence
- aspect-ratio preservation

### Region Formation
- one clear foreground region
- two disconnected regions
- edge-separated adjacent regions
- background/noise rejection
- deterministic region ordering

### Geometry
- independently measured contour
- circle control
- rectangle control
- elongated object
- irregular region

### Color
- dominant red
- dominant green
- mixed color
- illumination variation

### Texture
- smooth
- fine
- coarse
- mixed

### Orientation
- horizontal dominant structure
- vertical
- diagonal
- mixed

### Size
- small
- medium
- large relative-area controls

### Spatial
- left/right
- above/below
- inside/contains
- touching
- near
- overlap
- normalized-resolution consistency

### Lifecycle
- transient region instance exists during scene
- retires at scene end
- persistent feature knowledge survives

### No-Guess
- ambiguous region partition
- ambiguous geometric class
- unsupported input

---

# 53. Canonical Synthetic Controls

Synthetic controls are allowed for geometry verification only.

Examples:

- perfect circle mask;
- rectangle mask;
- two colored blocks;
- nested rectangle;
- touching shapes;
- noisy background.

These controls verify mathematics.

They do not count as evidence of real-image understanding.

---

# 54. Required Real-Image Evaluation

A later real-image trial must use actual photographs.

Minimum required categories:

- single-object photographs;
- multiple samples of same semantic class;
- same object class under different backgrounds;
- same class under moderate scale changes;
- same class under moderate illumination changes;
- visually confusable different classes.

The Vision Encoder must remain unaware of semantic labels during encoding.

---

# 55. Real-Image Evaluation Questions

The real-image trial must answer:

1. Are repeated images encoded deterministically?
2. Are visually similar instances represented with overlapping low-level features?
3. Are visually distinct objects sufficiently separable?
4. Does background variation dominate the encoding?
5. Does scale variation destroy representation overlap?
6. Does illumination variation destroy representation overlap?
7. Do transient visual instances retire correctly?
8. Does persistent visual feature memory survive?
9. Does the encoder ever emit semantic labels?
10. Does the encoder remain graph-independent?

---

# 56. Release Gates

### V2-G01 — Raw Pixel Intake

Vision v2 consumes real pixel input.

### V2-G02 — Graph Independence

Pure encoder path does not read or mutate graph state.

### V2-G03 — Semantic Firewall

No semantic object label is emitted.

### V2-G04 — Deterministic Region Formation

Repeated input yields identical regions and ordering.

### V2-G05 — True Geometry

Contour-based shape metrics are validated independently.

### V2-G06 — Bounded Sparse Features

Feature budget is enforced.

### V2-G07 — Resolution-Neutral Spatial Semantics

Spatial relations remain stable across resolution changes.

### V2-G08 — No Paired-Text Injection

Visual encoding contains no semantic text binding.

### V2-G09 — No Focal Weight Privilege

Visual focus cannot directly change cognitive learned weight.

### V2-G10 — Explicit Transient Lifecycle

Scene-local visual instances retire lawfully.

### V2-G11 — Persistent Knowledge Preservation

Transient cleanup does not delete persistent visual knowledge.

### V2-G12 — Real-Image Validation

Real image suite executes with complete diagnostics.

### V2-G13 — No Hidden Learned Vision Model

Forbidden pretrained mechanisms audit passes.

### V2-G14 — Static Scope Integrity

No video/temporal tracking semantics are introduced.

### V2-G15 — Full Repository Regression

DGCA regression remains green.

### V2-G16 — No New Primitive/Law

Persistent schema/law count remains unchanged.

Required:

\[
\boxed{
16/16\ PASS
}
\]

---

# 57. Required Implementation Workstreams

### V2-W01 — Legacy Dependency Inventory

Map all active RFC-06 / vision.py dependencies.

### V2-W02 — PixelFrame / Decode Adapter

Implement canonical raw-image intake.

### V2-W03 — Normalization

Implement deterministic frame normalization.

### V2-W04 — Region Formation

Implement deterministic perceptual-region extraction.

### V2-W05 — Geometry

Implement contour and shape measurements.

### V2-W06 — Appearance

Implement color, luminance, texture, orientation, size.

### V2-W07 — Spatial Topology

Implement normalized bounded relations.

### V2-W08 — VisualFrameIR

Implement immutable encoder-local IR.

### V2-W09 — SensoryEpisode Emission

Bridge IR to existing graph-compatible sensory contract.

### V2-W10 — Transient Lifecycle

Integrate explicit `inst:vis:*` retirement.

### V2-W11 — Remove Legacy Semantic Coupling

Remove/retire `paired_text` and focal weight privilege.

### V2-W12 — Verification

Run synthetic, adversarial, real-image, regression, and static audits.

---

# 58. Legacy Compatibility Policy

Legacy RFC-06 remains historical.

Do not rewrite historical reports as if v2 always existed.

Current legacy API may be retained temporarily only for compatibility if:

- clearly marked legacy;
- not used by Vision v2 normative path;
- no semantic behavior leaks into v2;
- no old Law-3 decay behavior remains active.

---

# 59. Law-3 Compatibility

Vision Encoder v2 must not use:

- transient decay;
- passive weight decay;
- inactivity pruning;
- decay-based instance death.

Transient lifecycle must be explicit.

Required:

\[
SceneScopeEnd
\rightarrow
TransientRetirement
\]

not:

\[
SceneScopeEnd
\rightarrow
WaitForDecay
\]

---

# 60. Law-8 / Salience Compatibility

Visual salience may influence presentation or attention ordering only through existing lawful mechanisms.

It must not create persistent weight floors.

Required:

\[
Salience \neq PersistencePrivilege
\]

---

# 61. Law-13 Compatibility

Vision Encoder v2 does not own negative correction.

If later multimodal evidence conflicts, correction remains graph/law-owned.

The encoder only emits visual evidence.

---

# 62. Cross-Modal Future Contract

After Vision v2 is closed, later experiments may test:

\[
VisualPattern
+
TextLabel
\]

or:

\[
VisualPattern
+
AudioPattern
+
TextLabel
\]

The encoder must remain unchanged during those grounding trials.

This allows causal attribution.

---

# 63. First Real-Image Trial Boundary

The first empirical trial after implementation should be:

\[
\boxed{
SmallRealImageSingleObjectTrial
}
\]

Recommended size:

```text
10–20 semantic concepts
3–10 real images per concept
```

The trial should test:

- deterministic encoding;
- representation overlap;
- separability;
- robustness;
- transient lifecycle;
- no semantic leakage.

No large image corpus is authorized yet.

---

# 64. Out of Scope

Explicitly out of scope for Vision Encoder v2.0:

- audio;
- speech;
- video;
- motion;
- tracking;
- multimodal fusion;
- semantic object classification;
- OCR semantics;
- pretrained embeddings;
- object naming;
- world knowledge;
- large-scale image training;
- Phase III;
- new laws;
- new persistent primitives.

---

# 65. Required Machine-Readable Verification Artifacts

Implementation should produce at minimum:

```text
vision_v2_dependency_inventory.json
vision_v2_forbidden_mechanism_audit.json
vision_v2_invariants.json
vision_v2_release_gates.json
vision_v2_synthetic_controls.json
vision_v2_real_image_results.json
vision_v2_determinism.json
vision_v2_transient_lifecycle.json
vision_v2_signature_verification.json
vision_v2_failures.jsonl
```

---

# 66. Required Final Implementation Report

Produce:

```text
DGCA-VISION-ENCODER-V2-IMPLEMENTATION-VERIFICATION-REPORT.md
```

The report must explicitly answer:

1. Does Vision v2 begin from raw pixels?
2. Is the encoder graph-independent?
3. Are all emitted visual features measured from pixels?
4. Does any semantic object label remain in the encoder?
5. Does any pretrained learned vision model remain?
6. Are coordinates normalized?
7. Is region formation deterministic?
8. Is contour measured independently?
9. Is feature emission bounded to \(B_{visual}=8\)?
10. Is spatial topology bounded?
11. Is `paired_text` absent from the v2 path?
12. Is focal-object weight privilege absent?
13. Are visual instance IDs transient?
14. Are shared feature IDs reusable?
15. Does scene closure retire transients explicitly?
16. Does transient cleanup preserve persistent visual knowledge?
17. Are ambiguous inputs fail-closed?
18. Is static-image scope preserved?
19. Were new cognitive primitives introduced?
20. Were new normative laws introduced?
21. Did all 20 invariants pass?
22. Did all 16 release gates pass?
23. Did forbidden-mechanism audit pass 16/16?
24. Did full repository regression pass?
25. Is Vision Encoder v2 ready for a small real-image trial?

---

# 67. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — VISION ENCODER V2

SPECIFICATION:
DGCA-Phase-2.6-Vision-Encoder-v2-Formal-Architectural-Specification-v1.0

ARCHITECTURAL ROLE:
DETERMINISTIC LOW-LEVEL PERCEPTUAL COMPILER

RAW PIXEL INPUT:
YES / NO

GRAPH INDEPENDENT:
YES / NO

SEMANTIC OBJECT LABELS:
0 / NONZERO

PRETRAINED VISION MODELS:
0 / NONZERO

NEW COGNITIVE PRIMITIVES:
0 / NONZERO

NEW NORMATIVE LAWS:
0 / NONZERO

PERSISTENT SCHEMA DELTA:
0 / NONZERO

VISUAL FEATURE BUDGET:
8

COORDINATE SYSTEM:
NORMALIZED / RAW PIXEL

REGION FORMATION:
DETERMINISTIC / NONDETERMINISTIC

TRUE CONTOUR MEASUREMENT:
YES / NO

PAIRED TEXT INJECTION:
0 / NONZERO

FOCAL WEIGHT PRIVILEGE:
0 / NONZERO

STATIC IMAGE SCOPE:
YES / NO

TRANSIENT VISUAL INSTANCES:
EXPLICIT RETIREMENT / PASSIVE DECAY

PERSISTENT KNOWLEDGE LOST BY TRANSIENT CLEANUP:
0 / NONZERO

FORBIDDEN MECHANISM AUDIT:
x / 16

ARCHITECTURAL INVARIANTS:
V2-INV-01..20:
x / 20

RELEASE GATES:
V2-G01..G16:
x / 16

SYNTHETIC CONTROL SUITE:
PASS / FAIL

REAL IMAGE SUITE:
PASS / FAIL / NOT YET EXECUTED

DETERMINISM:
PASS / FAIL

FULL PYTEST:
...

RUFF:
PASS / FAIL

TYPE CHECK:
PASS / FAIL

POST-ABOLITION BASELINE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / MISMATCH

FINAL VERDICT:
PASS / FAIL / BLOCKED

READY FOR SMALL REAL-IMAGE TRIAL:
YES / NO
============================================================
```

---

# 68. Closure Criterion

Vision Encoder v2 can be frozen only if:

\[
\boxed{
RawPixels
\rightarrow
DeterministicPerceptualStructure
}
\]

is demonstrated without:

\[
SemanticLeakage
\]

without:

\[
GraphDependentParsing
\]

without:

\[
PretrainedVisionIntelligence
\]

and without:

\[
PersistentEncoderOwnedState
\]

The target is not object recognition.

The target is a clean sensory representation from which DGCA can later learn object meaning.

---

# 69. Final Architectural Statement

Vision Encoder v2 is defined as:

\[
\boxed{
\textbf{A deterministic low-level perceptual compiler from raw static image pixels to sparse reusable visual evidence.}
}
\]

It must preserve the distinction:

\[
\boxed{
Perception \neq Meaning
}
\]

and:

\[
\boxed{
VisualDescription \neq SemanticKnowledge
}
\]

The encoder describes the signal.

DGCA learns what the signal means.

