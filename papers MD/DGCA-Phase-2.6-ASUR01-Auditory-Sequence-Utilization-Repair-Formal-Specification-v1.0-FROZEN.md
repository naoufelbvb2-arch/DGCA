# DGCA Phase 2.6 — ASUR01
## Auditory Sequence Utilization Repair 01
## Formal Repair Specification v1.0

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Auditory Cross-Modal Retrieval Repair  
**Repair ID:** `ASUR01` — Auditory Sequence Utilization Repair 01  
**Document Type:** Formal Repair Specification  
**Version:** 1.0  
**Status:** **CANDIDATE FOR FREEZE REVIEW**

**Parent Trial:** `ATG01`  
**Parent ATG01 Commit:** `7e43974`  
**F01 Commit:** `74f788e`  
**ARSR01 Counterfactual Commit:** `c3bf4dc`  
**ARSR01 Implementation Commit:** `a26deb5`  
**Historical Cognitive Signature:** `915119d40643cb97`

**Residual Primary Bottleneck:** `AUDITORY_SEQUENCE_UTILIZATION_BOTTLENECK`  
**Authorized Repair Class:** `R-C SEQUENCE_UTILIZATION_REPAIR`

**Audio Encoder v2:** FROZEN  
**English Encoder v2:** FROZEN  
**Grounding Authority:** FROZEN  
**LESR:** FROZEN  
**LDSR v1.0:** IMPLEMENTED / RETAINED  
**IGSV:** UNCHANGED  
**Abstention Governance:** UNCHANGED  
**Persistent Schema:** FROZEN  
**DGCA Laws:** FROZEN

**Training / Backprop:** `0`  
**New Persistent Primitive:** `0`  
**New Persistent Field:** `0`  
**New Normative Law:** `0`  
**New Learned Scalar:** `0`  
**External Alignment:** `0`  
**DTW / Template Matching:** `0`

---

# 1. Formal Problem Statement

Post-ARSR01 validation preserved:

- `CorrectCandidatePresent = 20/20`
- `CorrectAcousticMemoryReinstated = 20/20`
- `G10/G20/G30/G40 = MATCH`

and improved median correct rank from `6.0 → 5.0`, but held-out outcomes remained `0/20 correct`, `19/20 wrong`, `1/20 ambiguous`.

F01 established:

```text
SEQUENCE SPECIFICITY = PARTIAL
SEQUENCE UTILIZATION = ABSENT
```

and showed that existing temporal transition structures generated during grounding contributed `0%` to lexical candidate scoring.

Therefore ASUR01 targets exactly one failure:

> Existing persistent auditory order is stored but not consumed by lexical retrieval.

# 2. Repair Objective

ASUR01 must test and, only if causally justified, enable:

`PersistentAuditoryTemporalOrder → LexicalCandidateEvidence`

using only already-existing lawful sequence relations.

The repair MUST NOT create a new sequence representation.

# 3. Core Scientific Principle

`A→B != B→A` and `A→B→C != {A,B,C}`.

Temporal order may contain lexical specificity not available in unordered descriptor evidence.

# 4. Scope Boundary

ASUR01 may change only transient auditory lexical retrieval scoring.

It MUST NOT change:
- Audio Encoder v2;
- English Encoder v2;
- grounding;
- persistent sequence creation;
- sequence persistence semantics;
- LESR;
- LDSR mathematics;
- IGSV;
- abstention governance;
- candidate discovery;
- reachability;
- persistent schema;
- DGCA Laws.

# 5. Mandatory Pre-Implementation Sequence Representation Audit

Before counterfactual scoring, inspect and freeze:
1. persistent sequence relation type(s);
2. endpoint identity semantics;
3. directionality semantics;
4. how auditory sequence relations are created during grounding;
5. whether sequence relations contain weights, contexts, or recurrence;
6. whether they are shared with other modalities;
7. how they are reached from auditory memory;
8. whether query-time ordered relations already exist transiently;
9. whether transition identities are canonical and deterministic.

Produce `asur01_sequence_representation_audit.json`.

If the existing system lacks a lawful persistent ordered relation suitable for retrieval:
`ASUR01_BLOCKED`.

Do NOT create a new sequence primitive.

# 6. Frozen Transition Identity

After audit, freeze one canonical existing transition identity:

`t = (source → destination)`

Direction is part of identity:

`(s→d) != (d→s)`

unless both separately exist.

# 7. Transition Eligibility

A transition contributes only if:
1. both endpoints are existing auditory evidence identities;
2. the ordered relation exists under current DGCA sequence semantics;
3. the query instantiates the same direction;
4. persistent transition evidence is reachable through grounded auditory memory;
5. no external alignment is required.

Else sequence contribution is zero.

# 8. Query Sequence Extraction

For query `Q=(q1,...,qm)`, extract adjacent transitions:

`T_Q = {(q1→q2), (q2→q3), ..., (q_{m-1}→q_m)}`

from the existing lawful Audio v2 downstream sequence representation.

No skip transitions may be synthesized unless already represented in current DGCA semantics and explicitly authorized by the audit.

# 9. No External Alignment

Forbidden:
- DTW;
- forced alignment;
- edit-distance alignment;
- longest-common-subsequence classifier;
- template search;
- waveform alignment;
- phoneme alignment.

# 10. Candidate Set

Freeze the same pre-scoring lexical candidate set used by installed post-ARSR01 retrieval:

`C_Q`, with `N_Q = |C_Q|`.

ASUR01 cannot add or remove candidates.

# 11. Persistent Transition-to-Concept Support

ASUR01 MUST NOT derive sequence support from generic endpoint-to-concept path multiplicity.

For persistent transition identity `t`, define:

`Gamma_t` = the set of already-existing independent grounding-context IDs carried by, or canonically attributable to, the persistent transition relation itself.

For lexical candidate `c`, define:

`Gamma_c` = the set of already-existing grounding-context IDs in which `c` was lawfully grounded to auditory memory under the frozen ATG01 grounding authority.

Then define the sequence-to-concept support set:

`Gamma_{t,c} = Gamma_t ∩ Gamma_c`

and the frozen transition support weight:

`W_{t,c} = |Gamma_{t,c}|`.

Thus `W_{t,c}` measures independent grounding episodes in which the ordered transition and lexical concept co-occurred under existing provenance.

Binding consequences:
- repeated graph paths do not multiply `W_{t,c}`;
- endpoint descriptor degree does not multiply `W_{t,c}`;
- candidate node degree does not multiply `W_{t,c}`;
- the same grounding context contributes at most once;
- no new persistent counter is created.

If the current persistent sequence relation lacks sufficient existing grounding-context provenance to construct `Gamma_t` exactly, then:

`ASUR01_COUNTERFACTUAL_BLOCKED`

Do NOT substitute endpoint paths or invent transition provenance.

# 12. Unsupported Candidate Rule

If:

`Gamma_{t,c} = empty`

then:

`W_{t,c}=0`.

No pseudo-count. No smoothing. No path-count fallback.

# 13. Sequence Local Distribution

If `Z_t = sum_k W_{t,k} > 0`, define:

`rho_Q(t,c) = W_{t,c}/Z_t`.

If `Z_t = 0`, transition contributes zero.

# 14. Sequence Differential Specificity

Reuse frozen LDSR:

`SeqLDSR_Q(t,c) = max(0, rho_Q(t,c) - 1/N_Q)`

No residual renormalization.

# 15. Generic Transition Null

Uniform support across all local candidates gives zero differential sequence support.

# 16. Strict-Subset Transition Specificity

For `N_Q=10` and support `(0.5,0.5,0,...)`, sequence residual is `(0.4,0.4,0,...)`.

# 17. Unique Transition Specificity

For `N_Q=10` and support `(1,0,...)`, sequence residual is `(0.9,0,...)`.

# 18. Query Transition Activation

The query may contain repeated occurrences of the same directional transition identity.

Let:

`U_Q = unique canonical directional transition identities present in T_Q`.

Each structural transition identity may contribute at most once per query. Repeated occurrences inside one utterance are not treated as independent lexical evidence.

For transition identity `t in U_Q`, use an already-existing transient activation/support `a_t >= 0`.

If multiple query occurrences map to the same `t`, use the maximum existing occurrence activation, not the sum.

If no meaningful existing activation exists, use equal transition activation:

`a_t = 1`.

# 19. Query Sequence Weight

Normalize over the unique active transition identities:

`q_t = a_t / sum_{u in U_Q} a_u`

when the denominator is positive.

If `U_Q` is empty, sequence contribution is zero.

This prevents repeated within-query transition occurrences from creating multiplicity inflation.

# 20. Candidate Sequence Score

Define:

`S_seq(c|Q) = sum_{t in U_Q} q_t * SeqLDSR_Q(t,c)`

Properties:
- nonnegative;
- transient;
- deterministic;
- local;
- bounded;
- non-learning.

# 21. No Endpoint Double Counting

Transition evidence may represent only ordered-relation information, not duplicate endpoint descriptor support already present in `S_base`.

Telemetry must separate:
- endpoint descriptor contribution;
- transition relation contribution.

# 22. Base Score

`S_base(c|Q)` is the exact installed post-ARSR01 auditory lexical score.

ASUR01 must reproduce it bit-identically before adding sequence evidence.

# 23. Scale-Compatibility Proof

The candidate specification proposed both direct addition and family-mass normalization. Freeze review rejects family-mass normalization because it can amplify arbitrarily weak nonzero sequence evidence to unit family mass.

ASUR01 therefore permits only direct addition, and only after proving that both score families are already bounded by construction.

For the installed post-ARSR01 base score, the counterfactual stage MUST verify exactly that:

`S_base(c|Q) = sum_f q_f * LDSR_Q(f,c)`

with:

`q_f >= 0`

and:

`sum_f q_f = 1`

(or a stricter existing bound `<=1`).

Because each LDSR evidence distribution has total differential mass `<=1`, this implies:

`sum_c S_base(c|Q) <= 1`.

For sequence evidence, by construction:

`sum_t q_t = 1`

and each `SeqLDSR` differential mass is `<=1`, therefore:

`sum_c S_seq(c|Q) <= 1`.

If the installed `S_base` cannot be reconstructed with this bounded local evidence-budget property, ASUR01 MUST return:

`ASUR01_COUNTERFACTUAL_BLOCKED`.

Do not invent a family normalization or mixing coefficient.

# 24. Frozen Combination Rule

The only authorized candidate combination is:

`S_ASUR(c|Q) = S_base(c|Q) + S_seq(c|Q)`.

This rule preserves the actual magnitude of sequence differential evidence. Tiny sequence evidence remains tiny. Strong sequence evidence remains strong.

No family is renormalized to unit mass merely because it is nonzero.

The combined candidate-score mass is bounded by:

`sum_c S_ASUR(c|Q) <= 2`.

The absolute bound is diagnostic only; no threshold is derived from it.

# 25. No Family-Mass Renormalization

The following rejected form is forbidden:

`base_norm = S_base / sum S_base`

`seq_norm = S_seq / sum S_seq`

`S = base_norm + seq_norm`.

Reason: if `S_seq` contains only epsilon-scale differential evidence, normalizing its family mass to 1 would amplify weak evidence and violate conservative repair.

# 26. No Learned or Hand-Tuned Mixing Coefficient

Forbidden any:

`S = S_base + lambda * S_seq`

with learned, hand-tuned, concept-specific, word-specific, or post-hoc `lambda`.

# 27. Directionality Property

`A→B` must not count as `B→A` unless reverse relation independently exists.

# 28. Reversal Adversarial Test

Use existing identities to compare `A→B` and `B→A`.

Required:
- correct direction uses matching relation;
- reverse contributes zero if absent;
- shared endpoints alone do not collapse directionality.

# 29. Bag-Equivalent Order Probe

Use transient diagnostic sequences with same unordered endpoint multiset but different order, e.g.:

`A→B→C` vs `A→C→B`.

If persistent transition support differs, sequence scores must be distinguishable.

# 30. No-Transition Fallback

If `|T_Q|=0`, then `S_seq=0` and final score equals `S_base` exactly.

# 31. Single-Transition Behavior

For one lawful transition, `q_t=1`, with no extra scaling.

# 32. Counterfactual Simulation Requirement

Implementation is forbidden until read-only counterfactual simulation completes on:

`20 heldout + 10 OOD + 8 permutation = 38 probes`.

# 33. Counterfactual Lineage

Required:
- ATG01 commit `7e43974`
- F01 commit `74f788e`
- ARSR01 simulation `c3bf4dc`
- ARSR01 implementation `a26deb5`
- Manifest SHA256 `41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7`

# 34. Counterfactual Reconstruction

For all 38 probes reconstruct exactly:
1. `C_Q`;
2. post-LDSR `S_base`;
3. ordered query transition identities;
4. persistent transition identities;
5. `W_{t,c}`;
6. `SeqLDSR`;
7. `q_t`;
8. `S_seq`;
9. frozen additive ASUR score;
10. frozen tie/commitment semantics.

If exact reconstruction fails:
`ASUR01_COUNTERFACTUAL_BLOCKED`.

# 35. Base Reproduction Gate

Before sequence addition reproduce installed ARSR01 outcomes exactly:

Held-out: `0 correct, 19 wrong, 1 ambiguous, 0 no retrieval, median rank 5.0`

OOD: `9 forced, 1 ambiguous, 0 no retrieval`

Permutation: `1/8 permuted correct, 1/8 natural dominant, 1/4 category coverage`

Required `38/38`.

# 36. Sequence Availability Metrics

Report:
- probes with `|T_Q|>0`;
- mean transitions/query;
- persistent transition matches/query;
- held-out probes with correct-concept sequence support;
- OOD probes with sequence support;
- permutation probes with permuted-target sequence support.

# 37. Sequence Coverage Gate

Require:

`CorrectConceptSequenceSupport >= 12/20`

for implementation authorization.

This is coverage, not accuracy.

# 38. Sequence Specificity Metrics

For every query transition report:
- fanout over `C_Q`;
- differential mass;
- candidate distribution;
- grounding context provenance;
- generic/shared/specific classification.

# 39. Transition Differential Mass

`M_t = sum_c SeqLDSR_Q(t,c)`.

It must obey the same local total-variation identity as LDSR.

# 40. Counterfactual Safety Gates

For the frozen additive ASUR combination, ALL safety gates must pass:

S1. Candidate discovery unchanged `38/38`.  
S2. Persistent mutation `0`.  
S3. Natural semantic target dominance in permutation `<=1/8` (installed ARSR01 parent value).  
S4. Post-ARSR01 base outcomes reproduce `38/38`.  
S5. No endpoint double counting and no generic path-multiplicity support.  
S6. Directionality adversarial tests PASS.  
S7. No-transition fallback exact.  
S8. Base-score bounded-budget proof and sequence-score bounded-budget proof PASS.  
S9. OOD forced grounded concepts do not increase above `9/10`.

All S1-S9 are required.

# 41. Counterfactual Efficacy Gates

ASUR01 implementation requires one **outcome-level** improvement AND one independent supporting improvement.

Outcome-level gates:

E1. Held-out correct `>=2/20`.  
E4. Permuted-target correct `>=3/8`.

At least ONE of E1 or E4 MUST pass.

Supporting gates:

E2. Median correct rank `<=4.0`.  
E3. At least `6/20` held-out probes improve correct rank, with at most `2/20` worsening by >1 rank.  
E5. At least `10/20` held-out probes receive positive correct-concept sequence contribution, and in at least 6 of those it exceeds sequence contribution to the parent winning wrong concept.

At least ONE of E2, E3, or E5 MUST also pass.

This prevents a repeat of ARSR01, where rank movement alone authorized an outcome-neutral implementation.

# 42. Strong Counterfactual Result

Descriptive only: `ASUR01_STRONG_COUNTERFACTUAL` if held-out correct `>=4/20` and/or permutation correct `>=4/8`, with all S1-S9 passing.

# 43. OOD Counterfactual Monitoring

ASUR01 is not an abstention repair.

Safety requires:

`OODForced_sim <= 9/10`.

This requirement is already binding as S9.

# 44. Reverse Retrieval

Counterfactual scope is auditory-to-lexical only.

Reverse Text-to-Audio remains unchanged.

# 45. Implementation Authorization

ImplementationAuthorized = YES only if:
1. sequence representation audit PASS;
2. sequence coverage gate PASS;
3. frozen additive combination passes S1-S9;
4. at least one outcome gate E1/E4 passes;
5. at least one supporting gate E2/E3/E5 passes;
6. all architectural invariants remain intact.

Otherwise: `ASUR01_PREIMPLEMENTATION_REJECTED`.

# 46. Counterfactual Selection Rule

There is no post-hoc combination selection.

The additive rule is frozen before execution. Counterfactual simulation may only accept or reject it.

# 47. No Outcome-Free Authorization

If only rank/support metrics improve but both E1 and E4 fail, implementation authorization MUST be `NO`, regardless of E2/E3/E5.

# 48. Implementation Scope

If authorized, code may only:
- expose/read existing query transitions;
- read existing persistent transition support;
- compute transient sequence differential specificity;
- aggregate with the frozen bounded additive rule only.

No learning change.

# 49. Complexity Bound

For `T=|T_Q|` and `N=|C_Q|`, sequence scoring must be `O(TN)` or better.

No global sequence scan.

# 50. Determinism

Identical graph/query must yield identical transition set, support, sequence score, final score, and winner/tie.

# 51. Grounding Conservation

Implementation must preserve exact post-ARSR01 grounding digests:

`G10/G20/G30/G40 = MATCH`.

# 52. Candidate Conservation

Pre-scoring candidate sets conserved for all 38 probes.

# 53. Reachability Conservation

Required:
- correct candidate present `20/20`;
- correct acoustic memory reinstated `20/20`.

# 54. Sequence Utilization Gate

After implementation, probes with matching persistent transition support must show nonzero sequence contribution for at least one candidate.

Target:
`PositiveCorrectSequenceContribution >=10/20`.

# 55. Exact ATG01 Re-Run

Use the same frozen 70 recordings, 70 speakers, manifest, grounding schedule, contexts, B0, encoders, grounding authority, LDSR, IGSV, abstention.

Only ASUR01 differs.

# 56. Held-Out Repair Gate

For full ASUR01 verification:
- correct `>=4/20`;
- wrong `<=15/20`;
- median correct rank `<=4.0`.

# 57. Permutation Repair Gate

Require:
- permuted-target correct `>=3/8`;
- natural-target dominant `<=2/8`.

# 58. OOD Non-Regression Gate

Require:
`OODForced <= 9/10`.

ASUR01 is not required to solve OOD.

# 59. Reverse Control Gate

Post-ASUR01 reverse Text→Audio must not introduce new wrong-dominant regression.

Parent post-LDSR:
`OWN 4/10, WRONG 0/10, AMBIGUOUS 6/10`.

# 60. Vision Regression

Required `UNCHANGED`.

# 61. Text-Only Regression

Required `UNCHANGED`.

# 62. Residual Failure Forensics

Reclassify residual failures using B1–B12 F01 taxonomy.

# 63. Next Repair Recommendation

After ASUR01, at most one recommendation:
- `R-B AUDIO_PROVENANCE_REPAIR_CANDIDATE`
- `R-D ABSTENTION_GOVERNANCE_REPAIR_CANDIDATE`
- `R-E AUDIO_REPRESENTATION_REVISIT_CANDIDATE`
- `NO_NEXT_REPAIR_YET`

No implementation.

# 64. Mathematical Invariants

M01 Directionality.  
M02 Generic transition null.  
M03 Strict-subset specificity retained.  
M04 Unique specificity retained.  
M05 No-transition → zero sequence contribution.  
M06 Single transition uses `q_t=1`.  
M07 Nonnegative sequence contribution.  
M08 Transition differential mass obeys TV identity.  
M09 No residual renormalization.  
M10 No endpoint descriptor double counting.  
M11 Candidate-order invariance.  
M12 Determinism.

# 65. Architectural Invariants

ASUR01-INV-01 Audio Encoder unchanged.  
ASUR01-INV-02 English Encoder unchanged.  
ASUR01-INV-03 Grounding unchanged.  
ASUR01-INV-04 LDSR unchanged.  
ASUR01-INV-05 LESR unchanged.  
ASUR01-INV-06 IGSV unchanged.  
ASUR01-INV-07 Abstention unchanged.  
ASUR01-INV-08 Existing sequence storage unchanged.  
ASUR01-INV-09 No new sequence primitive.  
ASUR01-INV-10 No new persistent field.  
ASUR01-INV-11 No new Law.  
ASUR01-INV-12 No learned scalar.  
ASUR01-INV-13 No external alignment.  
ASUR01-INV-14 No DTW/template classifier.  
ASUR01-INV-15 Candidate discovery unchanged.  
ASUR01-INV-16 Candidate sets conserved.  
ASUR01-INV-17 Reachability conserved.  
ASUR01-INV-18 Directionality conserved.  
ASUR01-INV-19 Generic transition null.  
ASUR01-INV-20 Strict-subset specificity retained.  
ASUR01-INV-21 Unique specificity retained.  
ASUR01-INV-22 No-transition fallback exact.  
ASUR01-INV-23 No endpoint double counting or generic candidate-path multiplicity.  
ASUR01-INV-24 Transition support derives only from independent existing grounding-context co-occurrence; repeated query transition identities contribute at most once.  
ASUR01-INV-25 Query-local only; no global sequence statistic.  
ASUR01-INV-26 Deterministic.  
ASUR01-INV-27 No scoring graph mutation.  
ASUR01-INV-28 Grounding digests conserved.  
ASUR01-INV-29 Vision unchanged.  
ASUR01-INV-30 Text-only unchanged.  
ASUR01-INV-31 Parent manifest unchanged.  
ASUR01-INV-32 Parent data unchanged.  
ASUR01-INV-33 Permutation safeguard enforced.  
ASUR01-INV-34 OOD non-regression monitored.  
ASUR01-INV-35 Residual failures retained.  
ASUR01-INV-36 Any next repair separately authorized.

Required: `36/36 PASS`.

# 66. Forbidden Mechanisms

1. Audio Encoder changes.  
2. English Encoder changes.  
3. Grounding changes.  
4. LDSR changes.  
5. LESR changes.  
6. IGSV changes.  
7. Abstention threshold.  
8. Confidence threshold.  
9. Learned sequence weight.  
10. Hand-tuned sequence multiplier or family-mass renormalization.  
11. Generic candidate-path multiplicity used as transition-to-concept support.  
12. Word/concept-specific sequence rule.  
13. Phoneme layer.  
14. ASR.  
15. Forced alignment.  
16. DTW.  
17. Edit-distance classifier.  
18. LCS classifier.  
19. Nearest sequence template.  
20. Whole-word template node.  
21. New persistent transition type.  
22. Persistent word-position field.  
23. Global sequence IDF.  
24. Corpus sequence statistics.  
25. Speaker embedding.  
26. New grounding exposures.  
27. Held-out learning.  
28. OOD learning.  
29. Candidate deletion.  
30. Candidate creation.  
31. Generic edge deletion.  
32. Negative persistent evidence.  
33. New Law.  
34. Data replacement.  
35. Bundling R-B.  
36. Bundling R-D.

Required: `36/36 PASS`.

# 67. Formal Release Gates

G01 Parent lineage verified.  
G02 Post-ARSR01 baseline reproduced exactly.  
G03 Existing persistent sequence representation audited.  
G04 Canonical directional transition identity frozen.  
G05 Query transition extraction frozen.  
G06 Transition-to-concept support construction frozen.  
G07 Sequence differential equation verified.  
G08 Directionality adversarial tests PASS.  
G09 Generic/strict-subset/unique sequence property tests PASS.  
G10 No-transition fallback PASS.  
G11 No endpoint double counting or generic path-multiplicity support PASS.  
G12 38/38 counterfactual probes reconstructable.  
G13 Sequence coverage `>=12/20` correct held-out support.  
G14 Base-score and sequence-score bounded-budget proof complete.  
G15 Family-mass renormalization absence verified.  
G16 Frozen additive combination verified exactly.  
G17 Frozen additive combination S1-S9 PASS.  
G18 At least one outcome gate E1/E4 AND one supporting gate E2/E3/E5 PASS.  
G19 Implementation minimal if authorized.  
G20 Candidate sets conserved `38/38`.  
G21 Reachability/correct candidate conserved `20/20`.  
G22 G10/G20/G30/G40 conserved.  
G23 Sequence utilization becomes nonzero as expected.  
G24 Held-out verification gate PASS.  
G25 Permutation verification gate PASS.  
G26 OOD/reverse/vision/text controls PASS.  
G27 `36/36` invariants + `36/36` forbidden PASS.  
G28 Full regression green + historical signature MATCH.

Required for full verification: `28/28 PASS`.

# 68. Allowed Counterfactual Verdicts

- `ASUR01_COUNTERFACTUAL_PASS`
- `ASUR01_PREIMPLEMENTATION_REJECTED`
- `ASUR01_COUNTERFACTUAL_BLOCKED`
- `ASUR01_COUNTERFACTUAL_SAFETY_FAIL`

# 69. Allowed Final Repair Verdicts

- `ASUR01_SEQUENCE_UTILIZATION_VERIFIED`
- `ASUR01_SEQUENCE_UTILIZATION_PARTIAL`
- `ASUR01_SEQUENCE_UTILIZATION_NO_EFFECT`
- `ASUR01_SEQUENCE_UTILIZATION_REGRESSION`
- `ASUR01_BLOCKED`

# 70. Verification Rule

`ASUR01_SEQUENCE_UTILIZATION_VERIFIED` requires:
- 28/28 gates;
- held-out correct `>=4/20`;
- wrong `<=15/20`;
- median correct rank `<=4.0`;
- permutation correct `>=3/8`;
- natural target dominant `<=2/8`;
- OOD forced `<=9/10`;
- no regression elsewhere;
- signature MATCH.

# 71. Partial Rule

Use `ASUR01_SEQUENCE_UTILIZATION_PARTIAL` if sequence evidence is lawfully used and causally improves ranking/outcomes, but one or more empirical gates fail without architectural regression.

# 72. No-Effect Rule

Use `ASUR01_SEQUENCE_UTILIZATION_NO_EFFECT` if scoring is correct and safe but has no meaningful causal benefit.

# 73. Regression Rule

Use `ASUR01_SEQUENCE_UTILIZATION_REGRESSION` if candidates/reachability are lost, grounding digests change, natural semantic dominance exceeds safeguard, Vision/Text regress, mutation occurs, or scope creeps.

# 74. Required Counterfactual Artifacts

- `ASUR01-SEQUENCE-COUNTERFACTUAL-REPORT.md`
- `asur01_lineage.json`
- `asur01_sequence_representation_audit.json`
- `asur01_transition_identity.json`
- `asur01_query_transition_extraction.jsonl`
- `asur01_transition_support.jsonl`
- `asur01_sequence_coverage.json`
- `asur01_sequence_specificity.jsonl`
- `asur01_base_reproduction.jsonl`
- `asur01_cf_additive_results.jsonl`
- `asur01_cf_additive_summary.json`
- `asur01_scale_budget_proof.json`
- `asur01_combination_freeze_verification.json`
- `asur01_directionality_tests.json`
- `asur01_bag_order_tests.json`
- `asur01_double_counting_audit.json`
- `asur01_counterfactual_safety_gates.json`
- `asur01_counterfactual_efficacy_gates.json`
- `asur01_counterfactual_verdict.json`

# 75. Required Implementation Artifacts

If implementation is authorized:
- `ASUR01-SEQUENCE-IMPLEMENTATION-VALIDATION-REPORT.md`
- `asur01_impl_baseline.json`
- `asur01_impl_code_identity.json`
- `asur01_impl_math_tests.json`
- `asur01_impl_property_tests.json`
- `asur01_impl_candidate_conservation.json`
- `asur01_impl_reachability.json`
- `asur01_impl_grounding_conservation.json`
- `asur01_cf_impl_consistency.json`
- `asur01_post_heldout.jsonl`
- `asur01_post_ood.jsonl`
- `asur01_post_reverse.jsonl`
- `asur01_post_permutation.jsonl`
- `asur01_sequence_contribution_delta.jsonl`
- `asur01_residual_forensics.jsonl`
- `asur01_next_repair_candidate.json`
- `asur01_invariants.json`
- `asur01_forbidden_mechanisms.json`
- `asur01_release_gates.json`
- `asur01_signature_verification.json`
- `asur01_failures.jsonl`

# 76. Required Final Counterfactual Metrics Block

```text
============================================================
DGCA PHASE 2.6 — ASUR01
PRE-IMPLEMENTATION COUNTERFACTUAL

PARENT ARSR01 COMMIT:
a26deb5

MANIFEST SHA256:
41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7

HISTORICAL SIGNATURE:
915119d40643cb97

BASE REPRODUCTION:
... /38

HELD-OUT WITH CORRECT SEQUENCE SUPPORT:
... /20

MEAN QUERY TRANSITIONS:
...

MEAN PERSISTENT MATCHED TRANSITIONS:
...

FROZEN ADDITIVE COMBINATION:
HELDOUT CORRECT ... /20
MEDIAN CORRECT RANK ...
PERMUTED CORRECT ... /8
NATURAL TARGET ... /8
OOD FORCED ... /10
SAFETY ... /9
OUTCOME EFFICACY E1/E4: PASS / FAIL
SUPPORTING EFFICACY E2/E3/E5: PASS / FAIL

AUTHORIZED COMBINATION:
ADDITIVE / NONE

COUNTERFACTUAL VERDICT:
...

IMPLEMENTATION AUTHORIZED:
YES / NO
============================================================
```

# 77. Formal Status

`ASUR01 — Auditory Sequence Utilization Repair 01 — Formal Repair Specification v1.0`

Status:

`FROZEN AFTER FREEZE REVIEW AMENDMENTS`

Binding amendments include context-provenance transition support, per-query transition-identity deduplication, rejection of family-mass normalization, frozen bounded additive combination, OOD non-regression as a safety gate, and outcome-level efficacy required before implementation authorization.

Next authorized phase: PRE-IMPLEMENTATION COUNTERFACTUAL SIMULATION ONLY.
