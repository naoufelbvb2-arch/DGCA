# DGCA Cross-Modal Retrieval Ranking Repair — Formal Architectural Specification v1.0

## Local Evidence Share Ranking (LESR) and Exact-Tie Ambiguity Semantics

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Component:** Cross-Modal Retrieval Ranking  
**Document Type:** Formal Architectural Specification  
**Version:** 1.0  
**Status:** **ARCHITECTURAL SPECIFICATION — CANDIDATE FOR FREEZE**  
**Implementation Status:** **PENDING**  
**Parent Evidence:** RI01 Cross-Modal Retrieval Forensics 01  
**Parent Causal Verdict:** `CROSSMODAL_RANKING_BOTTLENECK`  
**Architecture Baseline Signature:** `915119d40643cb97`  
**Vision Encoder v2:** **IMPLEMENTED / VERIFIED / FROZEN / CLOSED**  
**New Cognitive Primitives:** `0`  
**New Persistent Fields:** `0`  
**New Learned Scalars:** `0`  
**New Normative Laws:** `0`  
**New Global Authority:** `0`  
**Primary Repair Type:** **Existing Retrieval Semantics Amendment**  
**Primary Mechanism:** **Local Evidence Share Ranking (LESR)**  
**Tie Policy:** **Exact top-score tie => AMBIGUOUS**  

---

# 1. Purpose

RI01 Cross-Modal Retrieval Forensics 01 proved that the remaining held-out image-to-text failure is not caused by visual encoding, persistent storage, or candidate reachability.

The exact forensic facts are:

\[
CorrectConceptStored = 20/20
\]

\[
CorrectConceptReached = 20/20
\]

\[
CorrectConceptInCandidateSet = 20/20
\]

while:

\[
Image\rightarrow Text = 10/20
\]

and all 10 wrong cases were:

\[
\boxed{
F\text{-}C:
CorrectConceptReachedButLostRanking
}
\]

The forensic causal verdict was:

\[
\boxed{
\textbf{CROSSMODAL\_RANKING\_BOTTLENECK}
}
\]

The proven mechanism was:

\[
\boxed{
UnweightedCoOccurrencePathCounting
+
DeterministicTieBreaking
}
\]

with generic visual features connected to many text concepts and therefore contributing excessive undifferentiated support.

This specification defines the minimal architectural repair.

---

# 2. Scope of Repair

The repair applies only to:

\[
\boxed{
CrossModalCandidateRanking
}
\]

after lawful candidate discovery and reachability.

The repair does NOT change:

- Vision Encoder v2;
- English Encoder v2;
- candidate discovery;
- graph learning;
- Law 1;
- Law 2;
- Law 5;
- Law 6;
- Law 8;
- Law 13;
- Law 14;
- transient lifecycle;
- graph storage;
- grounding formation;
- cross-modal edge creation;
- persistent edge weights;
- traversal eligibility;
- context authority;
- gating authority.

The repair is strictly:

\[
\boxed{
ReadTimeRankingSemantics
}
\]

---

# 3. Proven Failure Mechanism

The existing ranking behaves approximately as:

\[
Score(c)
\propto
NumberOfSupportingPaths(c)
\]

This implicitly assumes:

\[
\boxed{
AllSupportingPaths
=
IndependentEvidence
}
\]

and:

\[
\boxed{
AllVisualFeatures
=
EqualDiscriminativeValue
}
\]

The forensics disproved both assumptions.

Generic features such as:

```text
vis:lum:dark
vis:compact:high
vis:elong:low
vis:solidity:high
vis:tex:smooth
```

were connected to many concepts.

Therefore a feature with high cross-modal fanout could contribute support to many concepts without its total support being bounded.

The failure is amplified when equal candidate scores are converted into a forced lexical winner.

---

# 4. Governing Repair Principle

The repair is governed by:

\[
\boxed{
\textbf{Each evidence source owns a bounded amount of retrieval support.}
}
\]

One evidence source must not create unlimited candidate support merely because it has many outgoing candidate associations.

Equivalently:

\[
\boxed{
OneEvidenceSource
\not\Rightarrow
UnlimitedSupportMass
}
\]

---

# 5. Local Evidence Conservation

For each active evidence source \(f\), define a bounded local support budget.

The support assigned by \(f\) to all eligible candidates must satisfy:

\[
\boxed{
\sum_{c\in C_f}\rho(f,c)=1
}
\]

when the denominator is non-zero.

This is:

\[
\boxed{
\textbf{Local Evidence Conservation}
}
\]

It is a retrieval computation rule.

It is NOT a new cognitive law.

It is NOT a learning rule.

It is NOT persistent state.

---

# 6. Local Evidence Share Ranking — LESR

For an active evidence node \(f\), let:

\[
C_f
\]

be the set of lawfully eligible candidate concept neighbors reachable through the existing cross-modal relation in the current retrieval direction.

Let:

\[
W_{f,c}
\]

be the existing persistent edge weight between evidence source \(f\) and candidate \(c\).

Define:

\[
Z_f
=
\sum_{k\in C_f} W_{f,k}
\]

Then define local evidence share:

\[
\boxed{
\rho(f,c)
=
\frac{W_{f,c}}{Z_f}
}
\]

when:

\[
Z_f>0
\]

If:

\[
Z_f=0
\]

then:

\[
\boxed{
\rho(f,c)=0
}
\]

and the evidence source abstains.

---

# 7. Semantic Meaning of LESR

LESR does not claim probability.

\[
\rho(f,c)
\]

means:

\[
\boxed{
NormalizedLocalRetrievalSupport
}
\]

It is not:

- calibrated probability;
- confidence;
- posterior belief;
- semantic certainty.

It is only the share of the current evidence source's bounded local support allocated to candidate \(c\).

---

# 8. Why Local Normalization Solves the Proven Failure

If feature \(f\) is linked equally to one concept:

\[
C_f=\{c\}
\]

then:

\[
\rho(f,c)=1
\]

If feature \(f\) is linked equally to ten concepts:

\[
|C_f|=10
\]

then each receives approximately:

\[
\rho(f,c)=0.1
\]

Thus:

\[
\boxed{
HighFanout
\Rightarrow
LowPerCandidateSupport
}
\]

without introducing a global IDF table or manually labeling the feature as generic.

---

# 9. Existing Edge Strength Remains Authoritative

LESR uses existing edge weights.

Example:

\[
W_{f,apple}=0.8
\]

\[
W_{f,ball}=0.2
\]

Then:

\[
\rho(f,apple)=0.8
\]

\[
\rho(f,ball)=0.2
\]

Therefore LESR preserves learned evidence asymmetry already contained in the graph.

It does not replace memory strength.

It normalizes the support budget of one evidence source.

---

# 10. Query-Level Candidate Support

Let the active query evidence set be:

\[
Q=\{f_1,f_2,\dots,f_m\}
\]

For each evidence source \(f\), let its existing activation be:

\[
A_f
\]

Define normalized query evidence participation:

\[
q_f
=
\frac{A_f}
{\sum_{g\in Q}A_g}
\]

when the denominator is positive.

Then candidate support is:

\[
\boxed{
S(c|Q)
=
\sum_{f\in Q}
q_f\cdot\rho(f,c)
}
\]

If all evidence activations are equal:

\[
A_f=1
\]

then:

\[
q_f=\frac{1}{m}
\]

---

# 11. No New Activation Semantics

LESR does not modify \(A_f\).

It consumes whatever activation semantics already exist in the lawful retrieval path.

If existing retrieval treats active evidence sources uniformly, then \(q_f\) may reduce to equal shares.

No new activation law is introduced.

---

# 12. Evidence Identity, Not Traversal Multiplicity

The forensic failure showed that path count can overstate support.

Therefore:

\[
\boxed{
IndependentEvidenceIdentity
>
TraversalMultiplicity
}
\]

A single canonical evidence source must not create multiple votes for the same candidate merely because traversal reaches the same candidate through duplicate equivalent paths.

---

# 13. Query-Scope Evidence Deduplication

Within one retrieval query scope:

\[
\boxed{
SameCanonicalEvidenceNode
\Rightarrow
OneEvidenceSource
}
\]

If the same `vis:*` feature appears through multiple scene-local regions, it must not automatically become multiple independent votes unless existing architecture explicitly represents independent activation mass.

The normative default is:

\[
\boxed{
CanonicalFeatureIdentityDeduplicatedWithinQueryScope
}
\]

---

# 14. Reciprocal Representation Is Not Duplicate Evidence

The parent grounding state contains directed cross-modal relations in both directions.

For retrieval:

\[
Vision\rightarrow Text
\]

the reverse representation:

\[
Text\rightarrow Vision
\]

must not be counted again as an independent confirmation of the same association.

Required:

\[
\boxed{
ReciprocalRepresentation
\neq
TwoIndependentEvidenceSources
}
\]

---

# 15. Candidate Discovery Is Frozen

RI01 forensics proved:

\[
CorrectConceptReached=20/20
\]

Therefore candidate discovery is not authorized for repair.

Required:

\[
\boxed{
CandidateDiscovery=UNCHANGED
}
\]

LESR operates only after candidate discovery has produced a lawful eligible candidate set.

---

# 16. Gating and Eligibility Remain Upstream Authorities

LESR does not bypass:

- context;
- gating;
- edge eligibility;
- role authority;
- traversal budget;
- lawful candidate filtering.

Only eligible local candidate neighbors may enter:

\[
C_f
\]

Required:

\[
\boxed{
LESRHasNoCandidateCreationAuthority
}
\]

---

# 17. No Global Graph Scan

To calculate:

\[
Z_f
\]

the implementation must inspect only eligible local candidate neighbors of \(f\).

Forbidden:

- scanning all concept nodes;
- computing corpus-wide concept frequency;
- building global specificity statistics at query time.

Target complexity:

\[
\boxed{
O\left(\sum_{f\in Q}|C_f|\right)
}
\]

---

# 18. No Persistent Specificity State

The implementation must not add fields such as:

```text
feature_specificity
idf
concept_fanout_score
retrieval_discrimination_weight
```

to persistent graph state.

Required:

\[
\boxed{
NewPersistentSpecificityState=0
}
\]

---

# 19. No Learned Ranking Parameters

Forbidden:

- ranking learning rate;
- learned temperature;
- trainable feature weights;
- learned thresholds;
- classifier parameters;
- learned calibration coefficients.

Required:

\[
\boxed{
NewLearnedParameters=0
}
\]

---

# 20. No Manual Feature-Family Weights

Forbidden examples:

```text
color_weight = 1.5
texture_weight = 0.7
luminance_weight = 0.2
```

The architecture must not hard-code which visual feature family is semantically more useful.

Specificity must emerge from local graph topology and existing learned edge strengths.

---

# 21. No Global IDF in v1.0

A global formulation such as:

\[
IDF(f)=\log\frac{N}{df(f)}
\]

is not adopted in v1.0.

Reason:

- it introduces global statistics;
- it is not necessary to solve the proven local fanout failure;
- it adds complexity beyond current unique necessity.

Status:

\[
\boxed{
GlobalIDF=DEFERRED
}
\]

---

# 22. Exact-Tie Problem

RI01 forensics found:

\[
ExactTies=6
\]

with:

\[
TieBreakErrors=6
\]

The previous retrieval behavior converted equal scores into one forced lexical/canonical winner.

This is deterministic but not cognitively justified.

---

# 23. New Exact-Tie Semantics

Let:

\[
S_{max}
=
\max_c S(c|Q)
\]

and:

\[
T
=
\{c:S(c|Q)=S_{max}\}
\]

If:

\[
|T|=1
\]

then:

\[
\boxed{
Winner=T_1
}
\]

If:

\[
|T|>1
\]

then:

\[
\boxed{
Outcome=AMBIGUOUS
}
\]

No concept receives winner authority.

---

# 24. Lexical Ordering Loses Cognitive Authority

Canonical ordering may remain for:

- serialization;
- deterministic display;
- reproducible logs.

But:

\[
\boxed{
SerializationOrder
\neq
CognitiveWinnerAuthority
}
\]

Alphabetical ordering must not resolve equal semantic support.

---

# 25. No Near-Tie Threshold

v1.0 does not introduce:

\[
|S_1-S_2|<\epsilon
\Rightarrow
AMBIGUOUS
\]

No new tie epsilon is authorized.

Only exact equality under canonical deterministic arithmetic invokes ambiguity.

If near-ties later prove to be an independent problem, they require separate evidence and review.

---

# 26. Floating-Point Determinism

The implementation must use the repository's existing deterministic numeric conventions.

Do not introduce a new arbitrary floating tolerance for semantic tie detection.

If a canonical score representation already exists, use it.

Otherwise preserve exact deterministic computation and serialization.

---

# 27. No Probability Claim

Even if normalized supports sum to one:

\[
\sum_c S(c|Q)=1
\]

under a specific eligible set, they must not be called probabilities.

Use:

```text
normalized retrieval support
candidate support
evidence share
```

not:

```text
confidence
probability
posterior
```

---

# 28. Modality-Neutral Principle

LESR should not be implemented as:

```python
if modality == "vision":
    ...
```

The principle is modality-neutral:

> when multiple evidence nodes support candidate concepts, each evidence node owns a bounded local support budget distributed across its lawful candidate neighbors.

This may later apply to:

\[
Audio\rightarrow Text
\]

without a new ranking design.

---

# 29. Initial Implementation Scope Is Narrow

Although LESR is modality-neutral in principle, the first implementation and verification scope is limited to the empirically proven failure:

\[
\boxed{
RealImage\rightarrow TextConcept
}
\]

Do not expand LESR to all reasoning, GTR ranking, hypothesis ranking, or generative arbitration.

---

# 30. Minimal Architecture Delta

Old:

```text
Candidate Discovery
-> Supporting Paths
-> Raw / Unweighted Path Count
-> Deterministic Forced Winner
```

New:

```text
Candidate Discovery
-> Canonical Unique Evidence Sources
-> Eligible Local Candidate Neighbors
-> Local Evidence Share Normalization
-> Candidate Aggregate Support
-> Unique Maximum OR AMBIGUOUS
```

Required:

\[
\boxed{
\Delta PersistentSchema=0
}
\]

\[
\boxed{
\Delta CognitivePrimitives=0
}
\]

\[
\boxed{
\Delta NormativeLaws=0
}
\]

---

# 31. Unique Necessity Review

## New Law

\[
\boxed{
UniqueArchitecturalNecessity(NewLaw)=FALSE
}
\]

The defect is a retrieval ranking semantic problem, not a missing learning law.

## New Persistent Primitive

\[
\boxed{
UniqueArchitecturalNecessity(NewPersistentPrimitive)=FALSE
}
\]

## New Learned Scalar

\[
\boxed{
UniqueArchitecturalNecessity(NewLearnedScalar)=FALSE
}
\]

## New Global Authority

\[
\boxed{
UniqueArchitecturalNecessity(NewGlobalAuthority)=FALSE
}
\]

## Retrieval Semantic Amendment

\[
\boxed{
UniqueArchitecturalNecessity(RetrievalSemanticAmendment)=TRUE
}
\]

---

# 32. Alternative A — Raw Path Count

\[
Score(c)=PathCount(c)
\]

Status:

\[
\boxed{REJECTED}
\]

Reason:

This is the forensic-proven failure mechanism.

---

# 33. Alternative B — Manual Feature Weights

Example:

```text
shape = 1.5
color = 0.8
luminance = 0.2
```

Status:

\[
\boxed{REJECTED}
\]

Reason:

Hand-tuned semantic assumptions and hidden task-specific policy.

---

# 34. Alternative C — Global IDF

\[
Score(f)\propto\log(N/df)
\]

Status:

\[
\boxed{DEFERRED}
\]

Reason:

More global state/complexity than necessary.

---

# 35. Alternative D — Learned Ranker

Status:

\[
\boxed{REJECTED}
\]

Reason:

Would add an external learning model over DGCA and obscure the architecture under study.

---

# 36. Alternative E — Negative Inhibition

Status:

\[
\boxed{DEFERRED}
\]

Reason:

Current evidence does not prove negative learning is necessary.

---

# 37. Alternative F — Local Evidence Share Ranking

Status:

\[
\boxed{\textbf{RECOMMENDED}}
\]

Reason:

- directly targets forensic cause;
- local;
- deterministic;
- bounded;
- uses existing persistent edge state;
- no new persistent state;
- no new law;
- no new learned parameter;
- no semantic hand-tuning.

---

# 38. Core Architectural Invariants

### XMRR-INV-01 — Candidate Discovery Unchanged

LESR does not modify candidate discovery.

### XMRR-INV-02 — Ranking Is Read-Only

Ranking cannot modify persistent graph state.

### XMRR-INV-03 — One Evidence Source Has Bounded Total Support

For valid \(Z_f>0\):

\[
\sum_c\rho(f,c)=1
\]

### XMRR-INV-04 — Local Eligible Neighbors Only

Support is distributed only over existing lawful eligible candidate neighbors.

### XMRR-INV-05 — Existing Edge Weight Determines Local Proportion

No substitute learned score replaces \(W_{f,c}\).

### XMRR-INV-06 — High Fanout Cannot Multiply Support Mass

One generic evidence source cannot create more than one total unit of normalized local support.

### XMRR-INV-07 — Reciprocal Representation Is Not Duplicate Evidence

Reverse edge representation is not counted as independent support in the same retrieval direction.

### XMRR-INV-08 — Duplicate Paths Are Not Duplicate Evidence

Traversal multiplicity does not inflate evidence count.

### XMRR-INV-09 — Canonical Evidence Identity Deduplicated

Same evidence node is counted once per query scope.

### XMRR-INV-10 — No Manual Feature-Family Weighting

No semantic feature-family coefficients.

### XMRR-INV-11 — No Global Graph Scan

Ranking remains local.

### XMRR-INV-12 — No New Learned Parameter

No trainable ranking scalar.

### XMRR-INV-13 — No New Persistent State

No ranking memory field is added.

### XMRR-INV-14 — No New Normative Law

Repair is retrieval semantics only.

### XMRR-INV-15 — Exact Top Tie => AMBIGUOUS

Equal maximal candidate support grants no unique winner.

### XMRR-INV-16 — Lexical Order Has No Winner Authority

Canonical ordering is display-only.

### XMRR-INV-17 — No Near-Tie Threshold

v1.0 introduces no margin/epsilon policy.

### XMRR-INV-18 — Read-Only Ranking Cannot Mutate Graph

Graph digest before/after ranking must match.

### XMRR-INV-19 — Existing Text→Visual Behavior Must Regress Cleanly

Successful reverse retrieval must not be silently broken by the change.

### XMRR-INV-20 — Vision Encoder v2 Remains Unchanged

No visual encoding change is authorized.

Required:

\[
\boxed{20/20}
\]

---

# 39. Forbidden Mechanisms Audit

The implementation must prove absence of:

1. manual color/shape/texture family weights;
2. global IDF state;
3. persistent specificity fields;
4. learned ranker;
5. new confidence model;
6. new near-tie threshold;
7. alphabetical winner authority;
8. duplicate reciprocal-edge counting;
9. duplicate path counting;
10. global concept scan;
11. graph mutation during ranking;
12. Vision Encoder modification;
13. English Encoder modification;
14. new learning law;
15. new persistent cognitive primitive;
16. new learned scalar.

Required:

\[
\boxed{16/16\ PASS}
\]

---

# 40. Read-Time Computational Contract

LESR may allocate transient local structures such as:

```text
EvidenceSource
CandidateSupport
LocalNormalizationDenominator
CandidateAggregate
TieSet
```

These are runtime-only.

They must not become persistent graph records.

---

# 41. Query Evidence Construction

The implementation must derive a canonical set:

\[
Q
\]

from active evidence nodes already selected by existing retrieval semantics.

Do not create new candidate-generating features.

Do not expand the visual evidence vocabulary.

---

# 42. Eligible Candidate Set

For each \(f\in Q\), derive:

\[
C_f
\]

from lawful candidate neighbors only.

A node not already reachable/eligible under current retrieval policy cannot receive LESR support.

---

# 43. Zero-Denominator Rule

If:

\[
Z_f=0
\]

the evidence source contributes no support.

Required:

\[
\boxed{
NoCandidateSupport
\Rightarrow
Abstain
}
\]

not:

\[
NoCandidateSupport
\Rightarrow
FallbackGuess
\]

---

# 44. Candidate Aggregation

For each candidate:

\[
S(c|Q)
=
\sum_{f\in Q}
q_f\rho(f,c)
\]

The aggregation must be deterministic.

No candidate-specific external prior is added in v1.0.

---

# 45. Candidate Outcome Semantics

Possible outcomes:

```text
WINNER
AMBIGUOUS
NO_RESULT
```

### WINNER

Exactly one candidate has maximal support.

### AMBIGUOUS

More than one candidate has exactly maximal support.

### NO_RESULT

No lawful candidate has positive support.

---

# 46. No Forced Winner

If:

\[
T=\{c_1,c_2\}
\]

and:

\[
S(c_1)=S(c_2)=S_{max}
\]

the system must not use:

- alphabetical order;
- insertion order;
- dictionary order;
- node ID order;
- serialization order;

to create cognitive winner authority.

---

# 47. Deterministic Ambiguity Serialization

For deterministic logs, tied candidates may be serialized in canonical order.

Example:

```text
AMBIGUOUS: [apple, ball]
```

But no first element is semantically privileged.

---

# 48. Existing Retrieval Compatibility

The amendment must preserve:

- existing eligible candidate identities;
- edge direction rules;
- context constraints;
- traversal budgets;
- graph ownership boundaries.

Only ranking arithmetic and exact-tie resolution change.

---

# 49. No Storage Migration

No persistent graph migration is authorized.

Existing B30 graph from RI01 must be rankable directly under LESR.

This is essential for causal A/B testing.

---

# 50. Frozen A/B Validation State

Primary validation must use:

\[
\boxed{
The exact frozen RI01 B30 learned graph
}
\]

and:

\[
\boxed{
The exact same 20 held-out images
}
\]

No retraining.

No new grounding.

No new image exposures.

No label changes.

---

# 51. A/B Evaluation Design

For each held-out probe evaluate:

### OLD

Existing ranking semantics.

### NEW

LESR + exact-tie ambiguity semantics.

Same:

- graph;
- candidate set;
- evidence;
- retrieval context;
- held-out image;
- encoder output.

Only ranking semantics differ.

---

# 52. Required Per-Probe A/B Record

Record:

```text
ProbeID
TrueConcept

OldCandidateSet
NewCandidateSet

OldWinner
OldOutcome
OldScoreBreakdown

NewWinner
NewOutcome
NewSupportBreakdown

CorrectConceptOldRank
CorrectConceptNewRank

OldTopTie
NewTopTie

OldGenericFeatureContribution
NewGenericFeatureContribution

GraphDigestBefore
GraphDigestAfter
```

Candidate sets should remain identical.

Any candidate-set difference requires investigation.

---

# 53. Allowed A/B Outcomes

Per probe:

```text
CORRECT_TO_CORRECT
WRONG_TO_CORRECT
WRONG_TO_AMBIGUOUS
WRONG_TO_WRONG
CORRECT_TO_AMBIGUOUS
CORRECT_TO_WRONG
AMBIGUOUS_TO_CORRECT
AMBIGUOUS_TO_AMBIGUOUS
NO_RESULT
```

---

# 54. Interpretation of Wrong→Ambiguous

If an old false winner resulted from exact equality and new semantics return:

```text
AMBIGUOUS
```

this is considered a semantic correctness improvement.

Reason:

\[
\boxed{
KnownAmbiguity
>
FalseCertainty
}
\]

It is not counted as correct recognition.

---

# 55. No Accuracy-Only Success Rule

The repair is not judged solely by:

\[
Correct/20
\]

The architecture must also satisfy:

- evidence conservation;
- no duplicate path inflation;
- no lexical tie authority;
- no graph mutation;
- no state/law/parameter addition.

---

# 56. Primary A/B Metrics

Report:

```text
OldCorrect
OldWrong
OldAmbiguous
OldNoResult

NewCorrect
NewWrong
NewAmbiguous
NewNoResult

WrongToCorrect
WrongToAmbiguous
WrongToWrong

CorrectToCorrect
CorrectToAmbiguous
CorrectToWrong
```

---

# 57. Ranking Metrics

Report:

```text
OldCorrectConceptRankDistribution
NewCorrectConceptRankDistribution

OldExactTies
NewExactTies

OldForcedTieWinners
NewForcedTieWinners

OldMedianWinnerMargin
NewMedianWinnerMargin

OldGenericFeatureContributionShare
NewGenericFeatureContributionShare

OldDiscriminativeFeatureContributionShare
NewDiscriminativeFeatureContributionShare
```

---

# 58. Strict Regression Requirements

Required:

```text
CorrectToWrong = 0
```

unless the old result was only correct by unjustified tie ordering and the new result is AMBIGUOUS.

Such a case must be separately classified and explained.

No hidden regression may be averaged away.

---

# 59. Text→Visual Regression Control

RI01 established:

\[
Text\rightarrow Visual=10/10
\]

After implementation, run the same reverse retrieval control.

Required target:

\[
\boxed{
10/10\ preserved
}
\]

If LESR is not invoked in that direction by scope design, verify explicitly that behavior remains unchanged.

---

# 60. Synthetic Ranking Controls

Before RI01 A/B, implement small graph-only controls.

### Control 1 — Unique Feature

One feature connected only to concept A.

Expected:

```text
A = winner
```

### Control 2 — Equal Generic Feature

One feature connected equally to A and B.

Expected:

```text
AMBIGUOUS
```

### Control 3 — Unequal Existing Weights

\[
W(f,A)=0.8
\]

\[
W(f,B)=0.2
\]

Expected:

\[
\rho(f,A)=0.8
\]

\[
\rho(f,B)=0.2
\]

### Control 4 — Duplicate Path

Same evidence source reaches A twice through duplicate equivalent paths.

Expected:

same support as once.

### Control 5 — Reciprocal Edge

Forward and reverse representation exist.

Expected:

not double counted.

### Control 6 — Generic + Specific

Generic evidence supports A/B equally.

Specific evidence supports B strongly.

Expected:

B wins.

---

# 61. Evidence Conservation Property Test

For every evidence source with \(Z_f>0\):

\[
\left|
\sum_c\rho(f,c)-1
\right|
\]

must be zero under canonical deterministic arithmetic, or within existing repository numeric representation rules if exact binary arithmetic prevents literal equality.

Do not invent a new semantic epsilon.

---

# 62. Property-Based Verification Families

Required property families should include:

1. local normalization conservation;
2. candidate-order permutation invariance;
3. duplicate path invariance;
4. reciprocal-edge non-duplication;
5. high-fanout support boundedness;
6. weight proportionality;
7. exact-tie ambiguity;
8. serialization order non-authority;
9. read-only graph invariance;
10. locality.

---

# 63. Candidate Order Permutation Invariance

Permuting candidate iteration order must not change:

- support values;
- winner;
- ambiguity set.

Required:

\[
Permutation(Candidates)
\Rightarrow
SameSemanticOutcome
\]

---

# 64. Evidence Order Permutation Invariance

Permuting evidence-source iteration order must not change the final result.

---

# 65. Duplicate Path Invariance

Adding a duplicate equivalent traversal path from the same canonical evidence source to the same candidate must not increase candidate support.

---

# 66. High-Fanout Boundedness

If one evidence source is connected equally to \(n\) candidates:

\[
\rho(f,c)=\frac{1}{n}
\]

for each.

The total remains:

\[
1
\]

regardless of \(n\).

---

# 67. Weight Proportionality

For fixed candidate set:

\[
\frac{\rho(f,c_i)}{\rho(f,c_j)}
=
\frac{W_{f,c_i}}{W_{f,c_j}}
\]

when both weights are positive.

---

# 68. Locality Test

LESR must not inspect unrelated graph components.

Changing a disconnected part of graph must not affect ranking result.

---

# 69. Read-Only Test

Graph digest before ranking:

```text
D_before
```

after ranking:

```text
D_after
```

Required:

\[
D_{before}=D_{after}
\]

---

# 70. No-New-State Audit

Inspect schema and graph objects for any new persistent field.

Required:

```text
NewPersistentFields = 0
```

---

# 71. No-New-Law Audit

Required:

```text
NewNormativeLaws = 0
```

No hidden "Law 18" or equivalent.

---

# 72. No-New-Parameter Audit

Required:

```text
NewLearnedScalars = 0
NewSemanticThresholds = 0
NewFeatureFamilyWeights = 0
```

---

# 73. Complexity Bound

For query evidence set \(Q\):

\[
T_{LESR}
=
O\left(
\sum_{f\in Q}|C_f|
\right)
\]

Memory overhead:

\[
O(|Candidates|)
\]

transient only.

No complexity proportional to total graph size is authorized.

---

# 74. Failure-Atomicity

If ranking encounters invalid local data:

- do not mutate graph;
- do not partially commit result;
- return explicit failure/unsupported diagnostic.

No persistent side effects.

---

# 75. Deterministic Replay

Using same:

- frozen graph;
- query evidence;
- context;
- candidate set;

must produce bit-identical candidate support serialization and semantic outcome.

Required replay family:

at least 30 identical repetitions per canonical control and RI01 probe set.

---

# 76. Implementation Workstreams

### XMRR-W01 — Current Ranking Dependency Inventory

Map current cross-modal candidate ranking path.

### XMRR-W02 — Evidence Identity Canonicalization

Deduplicate canonical evidence sources.

### XMRR-W03 — Local Candidate Neighbor Extraction

Reuse lawful eligible neighbor set.

### XMRR-W04 — LESR Computation

Implement \(\rho\) and \(S(c|Q)\).

### XMRR-W05 — Exact-Tie Ambiguity

Remove lexical winner authority.

### XMRR-W06 — Read-Only Telemetry

Expose support decomposition.

### XMRR-W07 — Synthetic Controls

Verify local mathematics.

### XMRR-W08 — Frozen RI01 A/B

Run old vs new on exact B30 state.

### XMRR-W09 — Regression

Verify Text→Visual and repository tests.

### XMRR-W10 — Static / Forbidden Audit

Verify no law/state/parameter leakage.

---

# 77. Required Release Gates

### XMRR-G01 — Candidate Discovery Conservation

Candidate discovery unchanged.

### XMRR-G02 — Evidence Deduplication

Duplicate paths do not inflate support.

### XMRR-G03 — Reciprocal Non-Duplication

Reverse edges do not double count evidence.

### XMRR-G04 — Local Evidence Conservation

Each evidence source has bounded normalized support.

### XMRR-G05 — Existing Weight Proportionality

Local support follows existing edge strength.

### XMRR-G06 — High-Fanout Boundedness

Generic feature fanout cannot multiply support mass.

### XMRR-G07 — Exact-Tie Ambiguity

Exact tied top support produces AMBIGUOUS.

### XMRR-G08 — Lexical Authority Removal

Alphabetical/canonical order has no semantic winner power.

### XMRR-G09 — Read-Only Graph Safety

Ranking mutates no persistent state.

### XMRR-G10 — No New Persistent State

Schema delta = 0.

### XMRR-G11 — No New Law/Parameter

No new normative law or learned scalar.

### XMRR-G12 — Frozen RI01 A/B Complete

Same B30 graph + same 20 probes evaluated.

### XMRR-G13 — No Correct→Wrong Regression

Previously justified correct winners are not degraded to wrong winners.

### XMRR-G14 — Reverse Retrieval Regression

Text→Visual remains 10/10.

### XMRR-G15 — Complexity/Locality Bound

No global graph scan.

### XMRR-G16 — Full Repository Regression

Pytest, Ruff, type check all pass.

Required:

\[
\boxed{16/16\ PASS}
\]

---

# 78. Required Implementation Artifacts

Produce:

```text
DGCA-CROSS-MODAL-RETRIEVAL-RANKING-REPAIR-IMPLEMENTATION-VERIFICATION-REPORT.md

xmrr_dependency_inventory.json
xmrr_runtime_changes.json
xmrr_invariants.json
xmrr_forbidden_mechanisms.json
xmrr_release_gates.json
xmrr_synthetic_controls.json
xmrr_property_tests.json
xmrr_determinism.json
xmrr_locality.json
xmrr_readonly_graph_check.json
xmrr_ri01_ab_results.jsonl
xmrr_ri01_ab_summary.json
xmrr_reverse_retrieval_regression.json
xmrr_signature_verification.json
xmrr_failures.jsonl
```

---

# 79. Required A/B Scientific Answers

The implementation report must answer:

1. Did candidate discovery remain identical?
2. Did evidence deduplication remove duplicate path inflation?
3. Did reciprocal edges remain non-duplicative?
4. Did each evidence source conserve total support?
5. Did high-fanout generic features receive lower per-candidate support?
6. Were existing edge weight ratios preserved?
7. Did exact ties become AMBIGUOUS?
8. Did lexical ordering lose semantic winner authority?
9. Did graph state remain unchanged during ranking?
10. Did RI01 candidate sets remain identical?
11. How many old wrong cases became correct?
12. How many old wrong cases became ambiguous?
13. How many remained wrong?
14. Did any old correct case become wrong?
15. Did any old correct case become ambiguous because old success came from forced tie-breaking?
16. What happened to the 6 forensic exact-tie errors?
17. Did generic feature contribution decrease?
18. Did discriminative feature contribution become relatively stronger?
19. Did Text→Visual remain 10/10?
20. Did architecture signature remain lawful?
21. Were any new laws introduced?
22. Were any persistent fields introduced?
23. Were any learned parameters introduced?
24. Is the cross-modal ranking bottleneck resolved, reduced, or unchanged?

---

# 80. Allowed Repair Outcomes

```text
CROSSMODAL_RANKING_REPAIR_DEMONSTRATED
CROSSMODAL_RANKING_BOTTLENECK_REDUCED
CROSSMODAL_RANKING_BOTTLENECK_UNCHANGED
EXACT_TIE_FALSE_CERTAINTY_REMOVED
GENERIC_FEATURE_DOMINANCE_REDUCED
PARTIAL_REPAIR
REPAIR_REGRESSION
IMPLEMENTATION_BLOCKED
```

---

# 81. No Scientific Overclaim

Even if held-out retrieval reaches 20/20, do not claim:

- general visual understanding;
- solved multimodal grounding;
- arbitrary concept recognition;
- universal ranking optimality.

Permitted claim:

> On the frozen RI01 learned graph and held-out probe set, locality-preserving evidence-share ranking corrected or reduced the forensic-proven unweighted ranking failure without architecture/encoder retraining.

---

# 82. Closure Criterion

The repair may be architecturally closed only if:

\[
\boxed{
EvidenceSupportIsBounded
}
\]

and:

\[
\boxed{
DuplicatePathsDoNotCreateDuplicateVotes
}
\]

and:

\[
\boxed{
ExactTie\Rightarrow Ambiguous
}
\]

and:

\[
\boxed{
LexicalOrderingAuthority=0
}
\]

and:

\[
\boxed{
GraphMutationDuringRanking=0
}
\]

and:

\[
\boxed{
NewLaw=0
}
\]

and:

\[
\boxed{
NewPersistentState=0
}
\]

and:

\[
\boxed{
NewLearnedParameters=0
}
\]

---

# 83. Required Final Metrics Block

```text
============================================================
DGCA — CROSS-MODAL RETRIEVAL RANKING REPAIR

SPECIFICATION:
DGCA-Cross-Modal-Retrieval-Ranking-Repair-Formal-Architectural-Specification-v1.0

REPAIR:
LOCAL EVIDENCE SHARE RANKING (LESR)

PARENT CAUSAL VERDICT:
CROSSMODAL_RANKING_BOTTLENECK

CANDIDATE DISCOVERY:
UNCHANGED / CHANGED

NEW COGNITIVE PRIMITIVES:
0 / NONZERO

NEW PERSISTENT FIELDS:
0 / NONZERO

NEW LEARNED SCALARS:
0 / NONZERO

NEW NORMATIVE LAWS:
0 / NONZERO

NEW GLOBAL AUTHORITY:
0 / NONZERO

GLOBAL GRAPH SCAN:
0 / NONZERO

DUPLICATE PATH VOTE INFLATION:
0 / NONZERO

RECIPROCAL EDGE DOUBLE COUNTING:
0 / NONZERO

LOCAL EVIDENCE CONSERVATION:
PASS / FAIL

EXACT TOP TIE:
AMBIGUOUS / FORCED WINNER

LEXICAL ORDER WINNER AUTHORITY:
0 / NONZERO

NEAR-TIE THRESHOLD:
0 / NONZERO

GRAPH MUTATION DURING RANKING:
0 / NONZERO

RI01 FROZEN B30 STATE:
USED / NOT USED

RI01 HELD-OUT PROBES:
20

OLD CORRECT:
10

OLD WRONG:
10

OLD AMBIGUOUS:
0

NEW CORRECT:
...

NEW WRONG:
...

NEW AMBIGUOUS:
...

NEW NO_RESULT:
...

WRONG -> CORRECT:
...

WRONG -> AMBIGUOUS:
...

WRONG -> WRONG:
...

CORRECT -> CORRECT:
...

CORRECT -> AMBIGUOUS:
...

CORRECT -> WRONG:
...

OLD EXACT TIES:
6

NEW FORCED TIE WINNERS:
...

GENERIC FEATURE CONTRIBUTION:
OLD ...
NEW ...

DISCRIMINATIVE FEATURE CONTRIBUTION:
OLD ...
NEW ...

TEXT -> VISUAL REGRESSION:
... / 10

XMRR INVARIANTS:
x / 20

FORBIDDEN MECHANISM AUDIT:
x / 16

RELEASE GATES:
x / 16

FULL PYTEST:
...

RUFF:
PASS / FAIL

TYPE CHECK:
PASS / FAIL

ARCHITECTURE SIGNATURE:
...

SIGNATURE STATUS:
MATCH / AUTHORIZED NEW IMPLEMENTATION BASELINE / MISMATCH

FINAL REPAIR VERDICT:
...

READY TO RE-CLOSE RI01 PHASE B:
YES / NO

READY FOR AUDIO ENCODER V2:
YES / NO
============================================================
```

---

# 84. Historical Lineage

The following facts remain historical and immutable:

- Vision Encoder v2 was closed before this repair.
- RI01 Phase A demonstrated real-image visual representation.
- RI01 Phase B formed persistent cross-modal associations.
- RI01 held-out image→text retrieval was 10/20.
- RI01 forensics proved the primary bottleneck was ranking.
- This repair is downstream of those findings.

Do not rewrite old reports as if LESR existed during RI01.

---

# 85. Final Architectural Statement

The repair is defined as:

\[
\boxed{
\textbf{Local Evidence Share Ranking (LESR)}
}
\]

with:

\[
\boxed{
\rho(f,c)
=
\frac{W_{f,c}}
{\sum_{k\in C_f}W_{f,k}}
}
\]

and:

\[
\boxed{
S(c|Q)
=
\sum_{f\in Q}
\frac{A_f}{\sum_g A_g}
\cdot
\rho(f,c)
}
\]

subject to:

\[
\boxed{
OneEvidenceSource
\Rightarrow
BoundedTotalSupport
}
\]

\[
\boxed{
DuplicateTraversal
\neq
IndependentEvidence
}
\]

\[
\boxed{
ExactTopTie
\Rightarrow
AMBIGUOUS
}
\]

\[
\boxed{
LexicalOrderingAuthority=0
}
\]

The amendment changes retrieval ranking semantics only.

DGCA memory, encoders, learning laws, and persistent graph schema remain unchanged.

