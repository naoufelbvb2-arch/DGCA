# DGCA Phase 2.6 — ARSR01 / LDSR v1.0

## Formal Repair Specification v1.0

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Auditory Cross-Modal Retrieval Repair  
**Repair Program:** `ARSR01` — Auditory Retrieval Specificity Repair 01  
**Component:** `LDSR v1.0` — Local Differential Specificity Residual  
**Document Type:** Formal Repair Specification  
**Version:** 1.0  
**Status:** **CANDIDATE FOR FREEZE REVIEW**  

**Authorized By:** `ATG01-F01`  
**Authorized Repair Class:** `R-A RETRIEVAL_SPECIFICITY_REPAIR`  
**Parent ATG01 Commit:** `7e43974`  
**F01 Commit:** `74f788e`  
**Parent Manifest SHA256:** `41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7`  
**Parent Behavioral Digest:** `abef5a931451bddb87c1492a928fc2d635f01ab89f22f066de1c58b63a65bddc`  
**Historical Cognitive Signature:** `915119d40643cb97`  

**Audio Encoder v2:** FROZEN  
**English Encoder v2:** FROZEN  
**Grounding Authority:** FROZEN  
**LESR Base Semantics:** FROZEN  
**IGSV:** FROZEN  
**Sequence Utilization:** UNCHANGED  
**Abstention Governance:** UNCHANGED  
**Persistent Schema:** FROZEN  
**DGCA Laws:** FROZEN  

**Training / Backprop:** `0`  
**New Persistent Primitive:** `0`  
**New Persistent Field:** `0`  
**New Normative Law:** `0`  
**New Learned Scalar:** `0`  
**Global Corpus Statistic:** `0`  
**IDF / TF-IDF:** `0`

---

# 1. Formal Problem Statement

ATG01-F01 established:

\[
CorrectCandidatePresent = 20/20
\]

\[
CorrectAcousticMemoryReinstated = 20/20
\]

but:

\[
Correct = 0/20
\]

with:

\[
Wrong = 19/20
\]

and:

\[
OODForced = 9/10
\]

The earliest information-loss stage was:

\[
\boxed{SPECIFICITY\_PROVENANCE}
\]

The primary forensic verdict was:

\[
\boxed{AUDITORY\_RETRIEVAL\_SPECIFICITY\_BOTTLENECK}
\]

ARSR01 therefore repairs only the transient interpretation of existing local evidence during auditory lexical competition.

---

# 2. Repair Scope

ARSR01 MUST NOT change:

- Audio Encoder v2;
- English Encoder v2;
- grounding formation;
- existing persistent cross-modal relations;
- LESR base weight semantics;
- IGSV provenance semantics;
- temporal sequence generation;
- pattern completion;
- abstention governance;
- any DGCA Law;
- persistent graph schema.

ARSR01 changes only the transient candidate contribution computed from an already available LESR distribution.

---

# 3. Existing LESR Input

For a query \(Q\), let:

\[
C_Q
\]

be the canonical local lexical candidate set produced by frozen candidate discovery **before LDSR scoring**.

Define:

\[
N_Q=|C_Q|
\]

For evidence item \(f\), existing LESR/local support provides nonnegative candidate weights:

\[
W_{f,c}\ge0
\]

for \(c\in C_Q\), with:

\[
W_{f,c}=0
\]

when \(f\) does not support candidate \(c\).

When total support is positive, define the local evidence distribution:

\[
\rho_Q(f,c)=
\frac{W_{f,c}}
{\sum_{k\in C_Q}W_{f,k}}
\]

so:

\[
\sum_{c\in C_Q}\rho_Q(f,c)=1
\]

This preserves existing LESR weight semantics. LDSR does not alter \(W\).

---

# 4. Proven Failure Mode

ATG01-F01 showed that broad acoustic evidence may support most or all lexical candidates.

If evidence \(f\) supports all \(N_Q\) local candidates equally:

\[
\rho_Q(f,c)=\frac1{N_Q}
\]

for all \(c\in C_Q\).

This evidence contains zero lexical discrimination inside the current local competition, yet the pre-repair scorer still adds positive support to every candidate.

That behavior is the exact target of ARSR01.

A second required property follows:

If \(f\) supports only a strict subset of \(C_Q\), it still carries useful differential information by excluding the remaining candidates, even when support is equal inside that subset.

Therefore the baseline MUST be defined over \(C_Q\), not only over the support subset of \(f\).

---

# 5. LDSR Local Query Baseline

For:

\[
N_Q=|C_Q|
\]

define:

\[
u_Q=\frac1{N_Q}
\]

for \(N_Q\ge1\).

This is a transient query-local baseline.

Forbidden:

- global vocabulary size;
- global concept inventory;
- corpus document frequency;
- global concept frequency;
- offline IDF.

---

# 6. LDSR Differential Residual — FROZEN FORM

For every \(c\in C_Q\):

\[
\boxed{
LDSR_Q(f,c)
=
\max\left(0,\rho_Q(f,c)-\frac1{N_Q}\right)
}
\]

This **unnormalized positive residual** is the authoritative LDSR v1.0 formula.

No post-residual renormalization is permitted.

Interpretation:

\[
LDSR_Q(f,c)>0
\]

iff evidence \(f\) favors candidate \(c\) above the local uniform query baseline.

\[
LDSR_Q(f,c)=0
\]

means \(f\) provides no positive differential preference for \(c\).

No negative evidence semantics are introduced.

---

# 7. Why Residual Renormalization Is Forbidden

The rejected candidate form normalized positive residuals back to unit mass.

That behavior is forbidden because it can amplify arbitrarily weak asymmetry.

Example:

\[
\rho=(0.51,0.49)
\]

with:

\[
N_Q=2
\]

gives:

\[
LDSR=(0.01,0)
\]

under the frozen form.

Renormalizing this to:

\[
(1,0)
\]

would convert weak evidence into absolute evidence and violate conservative repair.

Therefore:

\[
\boxed{\text{No residual renormalization}}
\]

is a binding invariant.

---

# 8. Uniform-Evidence Lawful Null

If:

\[
\rho_Q(f,c)=\frac1{N_Q}
\]

for every \(c\in C_Q\),

then:

\[
\boxed{LDSR_Q(f,c)=0\quad\forall c}
\]

The persistent associations remain unchanged.

Only transient lexical discrimination becomes zero.

---

# 9. Strict-Subset Specificity

Suppose \(N_Q=10\) and evidence \(f\) supports exactly two candidates equally:

\[
\rho_Q(f,A)=0.5
\]

\[
\rho_Q(f,B)=0.5
\]

with all other candidates receiving zero.

Then:

\[
LDSR_Q(f,A)=0.4
\]

\[
LDSR_Q(f,B)=0.4
\]

and all other candidates receive zero.

Thus evidence that excludes eight of ten local alternatives remains strongly informative even if it cannot distinguish between the two supported candidates.

---

# 10. Unique-Support Specificity

Suppose \(N_Q=10\) and only one candidate receives support:

\[
\rho_Q(f,A)=1
\]

Then:

\[
LDSR_Q(f,A)=0.9
\]

This is lawful maximally local specificity relative to the current ten-candidate competition.

For \(N_Q=1\), the residual is zero because no lexical alternative exists inside the local competition; this is a differential-scoring fact, not an abstention rule.

---

# 11. Differential Mass / Total-Variation Property

Define:

\[
M_f=
\sum_{c\in C_Q}LDSR_Q(f,c)
\]

Then:

\[
0\le M_f<1
\]

for finite \(N_Q>1\), and:

\[
\boxed{
M_f=
\frac12
\sum_{c\in C_Q}
\left|
\rho_Q(f,c)-\frac1{N_Q}
\right|
}
\]

Thus \(M_f\) is exactly the total-variation distance between the evidence distribution and the local uniform distribution.

Consequences:

- uniform evidence → \(M_f=0\);
- weak asymmetry → small \(M_f\);
- strong specificity → large \(M_f\);
- no arbitrary threshold or learned scale is required.

The auditory lexical contribution becomes:

\[
\boxed{
Contribution_{ARSR}(f,c)
=
q_f\cdot LDSR_Q(f,c)
}
\]

for the authorized auditory lexical retrieval path only.

# 12. Scope Guard

LDSR v1.0 applies only when all are true:

1. retrieval path is auditory cross-modal lexical retrieval;
2. LESR produced a lawful local candidate distribution;
3. the evidence item participates in that local candidate competition;
4. the call is transient/read-only with respect to graph state.

Otherwise preserve existing behavior.

---

# 13. No Vision Spillover

Vision retrieval MUST remain bitwise behaviorally unchanged unless a separate future generalization audit authorizes modality-generic LDSR.

Required:

\[
VisionBehavior_{post}=VisionBehavior_{pre}
\]

for frozen vision regression probes.

---

# 14. No Text-Only Spillover

Text-only retrieval must remain unchanged.

---

# 15. No IGSV Repair

F01 reported:

```text
IGSV_PROVENANCE_MISMATCH
```

ARSR01 MUST NOT fix it.

No audio provenance grouping may be added in this repair.

---

# 16. No Sequence Repair

F01 reported:

```text
SEQUENCE_UTILIZATION = ABSENT
```

ARSR01 MUST NOT add sequence scoring.

---

# 17. No Abstention Repair

ARSR01 MUST NOT introduce:

- confidence threshold;
- margin threshold;
- OOD threshold;
- entropy threshold.

Any increased abstention must emerge naturally from zeroing non-differential evidence under existing rules.

---

# 18. Pre-Implementation Counterfactual Simulation

Before any code change, use frozen F01 score-decomposition telemetry.

Required input lineage:

```text
ATG01 commit: 7e43974
F01 commit: 74f788e
Manifest SHA256:
41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7
```

No graph mutation.

---

# 19. Counterfactual Simulation Set

Run LDSR mathematically over frozen telemetry for:

```text
20 held-out Audio→Text probes
10 OOD probes
8 permutation probes
```

Total:

\[
38
\]

counterfactual probes.

Reverse Text→Audio is analyzed separately because ARSR01 is authorized first for auditory→lexical competition.

---

# 20. Counterfactual Held-Out Metrics

Report pre→simulated:

- correct /20;
- wrong /20;
- ambiguous /20;
- no retrieval /20;
- correct rank mean;
- correct rank median;
- concepts with >=1 correct /10.

---

# 21. Counterfactual OOD Metrics

Report pre→simulated:

- forced grounded concept /10;
- ambiguous /10;
- no retrieval /10.

---

# 22. Counterfactual Permutation Metrics

Report pre→simulated:

- permuted-target correct /8;
- natural-target dominant /8;
- category coverage /4.

---

# 23. Simulation Acceptance Gate

Implementation is authorized only if simulation satisfies ALL safety conditions:

### S1
The **pre-scoring discovery candidate set** is unchanged for all simulated probes.

### S2
No persistent state is changed.

### S3
Permutation control shows no increase in natural-semantic-target dominance.

And at least ONE efficacy condition:

### E1
Held-out correct count increases by at least 2 probes.

OR

### E2
Held-out median correct rank improves by at least 1 full rank position.

OR

### E3
OOD forced mappings decrease by at least 2.

OR

### E4
Permutation permuted-target correct count increases by at least 2.

If no efficacy condition holds:

```text
ARSR01_PREIMPLEMENTATION_REJECTED
```

Do not modify retrieval code.

No additional undefined notion of “material improvement” may be introduced.

---

# 24. Simulation Does Not Prove Repair

A passing counterfactual simulation only authorizes implementation.

It does NOT establish:

```text
ARSR01_VERIFIED
```

or:

```text
ATG01_REPAIRED
```

---

# 25. Implementation Form

Preferred implementation is a pure deterministic function:

```text
local_differential_specificity_residual(...)
```

Input:

- existing LESR local supports;
- local candidate identities;
- existing q_f where applicable.

Output:

- transient LDSR-adjusted contributions.

No graph write.

---

# 26. Persistent-State Constraint

Required:

\[
\Delta PersistentMemory=0
\]

for the LDSR function itself.

---

# 27. Complexity Constraint

For evidence item with \(K_f\) candidate concepts:

\[
T_{LDSR}=O(K_f)
\]

\[
S_{LDSR}=O(K_f)
\]

or better.

No global scan.

---

# 28. Determinism Constraint

For identical local support input:

\[
LDSR(x)=LDSR(x)
\]

bitwise/canonical deterministic under existing numeric policy.

Candidate ordering must not affect results.

---

# 29. Mathematical Property Tests

Required property families:

### P01 Uniform Null
Uniform distribution over all \(C_Q\) candidates:

\[
\rho_Q(c)=1/N_Q
\]

implies all LDSR values are zero.

### P02 Strict-Subset Specificity
If support is uniform over a strict subset \(m<N_Q\):

\[
\rho_Q=1/m
\]

on supported candidates, then each supported candidate receives:

\[
1/m-1/N_Q>0
\]

and unsupported candidates receive zero.

### P03 Unique Support
For \(N_Q>1\), a uniquely supported candidate receives:

\[
1-1/N_Q
\]

### P04 Weak-Asymmetry Preservation
For \(\rho=(0.51,0.49)\), \(N_Q=2\):

\[
LDSR=(0.01,0)
\]

and MUST NOT be renormalized to \((1,0)\).

### P05 Nonnegativity
\[
LDSR\ge0
\]

### P06 Total-Variation Identity
\[
\sum_c LDSR_Q(f,c)
=
\frac12\sum_c\left|\rho_Q(f,c)-1/N_Q\right|
\]

### P07 Bounded Differential Mass
\[
0\le\sum_c LDSR_Q(f,c)\le1-1/N_Q
\]

for \(N_Q\ge1\).

### P08 Permutation Invariance
Renaming/reordering candidate IDs preserves corresponding values.

### P09 Scale Invariance of W
Multiplying all \(W_{f,c}\) by a positive constant does not change LDSR.

### P10 Unsupported Candidate Zero
Candidate with \(W_{f,c}=0\) cannot receive LDSR evidence.

### P11 Query Locality
Changing concepts outside the frozen pre-scoring \(C_Q\) has no effect.

### P12 Determinism
Repeated identical input produces identical output.

### P13 No Persistent Mutation
Graph digest unchanged.

### P14 Candidate-Order Invariance
Canonical candidate order affects serialization only, never numeric result.

# 30. Edge Cases

Must define/test:

- \(N_Q=0\): no lexical competition; no LDSR contribution, no error;
- \(N_Q=1\): zero differential contribution because no local alternative exists;
- evidence supports one candidate while \(N_Q>1\): contribution \(1-1/N_Q\);
- evidence supports a strict subset equally: positive residual retained;
- all \(W=0\): follow existing LESR invalid/zero-support semantics; LDSR must not invent support;
- floating underflow;
- exact ties;
- very large \(N_Q\);
- duplicate candidate IDs rejected/deduplicated according to existing canonical identity rules;
- pre-scoring candidate set \(C_Q\) must be frozen before LDSR and cannot be changed by LDSR itself.

---

# 31. Integration Point

LDSR must be inserted:

\[
After\ LESR\ local\ distribution
\]

and:

\[
Before\ final\ candidate\ aggregation
\]

for authorized auditory lexical retrieval.

It MUST NOT alter candidate discovery.

---

# 32. Candidate Discovery Conservation

Required for the **pre-scoring discovery candidate set**:

\[
C_{Q,post}=C_{Q,pre}
\]

for all ATG01 held-out, OOD, and permutation probes.

LDSR may change final numeric support or the existing downstream commitment outcome, but it MUST NOT create, delete, or rediscover lexical candidates.

---

# 33. Reachability Conservation

Required:

\[
Reachability_{post}=Reachability_{pre}
\]

for all parent probes.

---

# 34. Grounding Conservation

Re-running the exact 40 grounding exposures with LDSR present but retrieval inactive during learning must produce identical:

- G10 digest;
- G20 digest;
- G30 digest;
- G40 digest;
- cross-modal edge identities;
- context sets;
- persistent weights.

---

# 35. ATG01 Repair Rerun

After implementation, rerun exact frozen ATG01 protocol with:

```text
same 70 recordings
same 70 speakers
same manifest
same grounding schedule
same contexts
same B0 semantics
same encoders
same grounding authority
same IGSV
same sequence handling
same abstention rules
```

Only LDSR differs in authorized retrieval.

---

# 36. Rerun Held-Out Metrics

Report:

```text
pre → post
```

for:

- correct /20;
- wrong /20;
- no retrieval /20;
- ambiguous /20;
- correct reachable /20;
- correct candidate /20;
- concepts with >=1 correct /10.

---

# 37. Rerun Reverse Metrics

Even though LDSR targets auditory→lexical retrieval, rerun reverse Text→Audio controls to prove no regression:

- own /10;
- wrong /10;
- no retrieval /10;
- ambiguous /10.

Expected ideally unchanged unless shared retrieval code lawfully causes a documented effect.

---

# 38. Rerun OOD Metrics

Report:

- forced /10;
- ambiguous /10;
- no retrieval /10.

No new OOD threshold.

---

# 39. Rerun Permutation Metrics

Report:

- permuted-target correct /8;
- natural-target dominant /8;
- category coverage /4.

This remains a causal safeguard.

---

# 40. Primary Repair Success Gate

ARSR01 full repair PASS requires ALL:

### R1
Pre-scoring discovery candidate sets unchanged 38/38 held-out/OOD/permutation probes.

### R2
Correct candidate remains present 20/20 held-out.

### R3
Correct acoustic memory remains reinstated 20/20.

### R4
Grounding G10/G20/G30/G40 digests unchanged.

### R5
Held-out correct improves from 0/20 to at least:

\[
\boxed{4/20}
\]

### R6
Held-out wrong decreases from 19/20 to at most:

\[
\boxed{15/20}
\]

### R7
OOD forced known concepts decreases from 9/10 to at most:

\[
\boxed{6/10}
\]

### R8
Permutation permuted-target correct does not decrease below 2/8.

### R9
Natural-target dominance does not increase above 2/8.

### R10
No label leakage, new learned state, or schema changes.

### R11
Historical signature MATCH.

### R12
Full regression green.

These thresholds establish causal usefulness of R-A; they do not require ATG01 full demonstration yet.

---

# 41. Strong Repair Result

Descriptive only:

```text
ARSR01_STRONG_EFFECT
```

may be reported if:

\[
HeldOutCorrect\ge8/20
\]

and:

\[
OODForced\le4/10
\]

while permutation causal safeguards remain intact.

This is not required for repair acceptance.

---

# 42. Full ATG01 Re-Pass Is Separate

If repaired ATG01 reaches the original full ATG01 gates, report it separately.

Do not redefine original ATG01 thresholds.

Original full demonstration requirements remain authoritative.

---

# 43. Residual-Forensics Rule

After ARSR01 rerun, classify residual failed probes using existing F01 taxonomy.

If majority residual failures are:

```text
B8 SEQUENCE_NOT_UTILIZED
```

then `R-C SEQUENCE_UTILIZATION_REPAIR` may become the next candidate.

If residual OOD failure is primarily:

```text
B9 ABSTENTION_COMMITMENT
```

then `R-D` may become candidate.

If residual specificity is linked to IGSV provenance mismatch:

```text
R-B
```

may become candidate.

No next repair is automatic.

---

# 44. No Multi-Repair Creep

ARSR01 implementation must not include:

- audio provenance grouping;
- sequence weighting;
- new abstention rule.

A patch containing more than R-A scope fails governance.

---

# 45. Architectural Invariants

### ARSR01-INV-01
Audio Encoder unchanged.

### ARSR01-INV-02
English Encoder unchanged.

### ARSR01-INV-03
Grounding unchanged.

### ARSR01-INV-04
LESR base semantics preserved.

### ARSR01-INV-05
IGSV unchanged.

### ARSR01-INV-06
Sequence handling unchanged.

### ARSR01-INV-07
Abstention rules unchanged.

### ARSR01-INV-08
Candidate discovery unchanged.

### ARSR01-INV-09
Candidate sets conserved.

### ARSR01-INV-10
Reachability conserved.

### ARSR01-INV-11
LDSR strictly local.

### ARSR01-INV-12
No global statistics.

### ARSR01-INV-13
No learned scalar.

### ARSR01-INV-14
No new persistent primitive.

### ARSR01-INV-15
No new persistent field.

### ARSR01-INV-16
No new Law.

### ARSR01-INV-17
Uniform local evidence contributes zero discrimination.

### ARSR01-INV-18
Differential evidence nonnegative.

### ARSR01-INV-19
Differential evidence mass equals local total-variation distance from uniform; no residual renormalization.

### ARSR01-INV-20
Residual renormalization is forbidden; weak asymmetry must remain weak.

### ARSR01-INV-21
Unsupported candidates receive zero.

### ARSR01-INV-22
Pure deterministic function.

### ARSR01-INV-23
No graph mutation.

### ARSR01-INV-24
Grounding digests conserved.

### ARSR01-INV-25
Vision behavior conserved.

### ARSR01-INV-26
Text-only behavior conserved.

### ARSR01-INV-27
Parent manifest unchanged.

### ARSR01-INV-28
Parent data unchanged.

### ARSR01-INV-29
No post-hoc threshold.

### ARSR01-INV-30
Permutation causal safeguard retained.

### ARSR01-INV-31
OOD improvement emerges without new OOD rule.

### ARSR01-INV-32
Residual failures retained.

### ARSR01-INV-33
Repair is causally isolated.

### ARSR01-INV-34
Historical signature conserved.

### ARSR01-INV-35
Full regression green.

### ARSR01-INV-36
No claim beyond evidence; any next repair requires separate authorization.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 46. Forbidden Mechanisms

Forbidden:

1. Audio Encoder change;
2. English Encoder change;
3. grounding change;
4. LESR base-weight change;
5. IGSV change;
6. sequence repair;
7. abstention threshold;
8. confidence threshold;
9. OOD-specific logic;
10. word-specific logic;
11. class-specific logic;
12. IDF;
13. TF-IDF;
14. corpus statistics;
15. learned temperature;
16. learned scaling;
17. learned threshold;
18. trained classifier;
19. ASR;
20. phoneme layer;
21. speaker embedding;
22. new grounding exposure;
23. new persistent specificity field;
24. new persistent fanout field;
25. new persistent primitive;
26. new Law;
27. negative persistent edge semantics;
28. deletion of generic edges;
29. candidate deletion based on LDSR;
30. parent data replacement;
31. test cherry-picking;
32. hidden post-hoc retuning;
33. Vision-path modification;
34. text-only path modification;
35. suppressing failed residual probes;
36. bundling R-B/R-C/R-D into ARSR01.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 47. Release Gates

### ARSR01-G01
Parent/F01 lineage verified.

### ARSR01-G02
Formal LDSR equation frozen.

### ARSR01-G03
Counterfactual telemetry simulation read-only.

### ARSR01-G04
Simulation safety S1–S3 PASS.

### ARSR01-G05
At least one simulation efficacy E1–E4 PASS.

### ARSR01-G06
Pure LDSR property tests PASS.

### ARSR01-G07
Uniform-null, strict-subset specificity, unique-support, and weak-asymmetry behavior verified.

### ARSR01-G08
Total-variation identity and bounded differential mass verified.

### ARSR01-G09
Locality verified.

### ARSR01-G10
Determinism verified.

### ARSR01-G11
No persistent mutation.

### ARSR01-G12
Candidate discovery conserved.

### ARSR01-G13
Candidate sets conserved.

### ARSR01-G14
Reachability conserved.

### ARSR01-G15
Grounding G10/G20/G30/G40 conserved.

### ARSR01-G16
Vision regression unchanged.

### ARSR01-G17
Text-only regression unchanged.

### ARSR01-G18
Exact ATG01 rerun completed.

### ARSR01-G19
Held-out causal improvement gate R5/R6 PASS.

### ARSR01-G20
OOD causal improvement gate R7 PASS.

### ARSR01-G21
Permutation safeguards R8/R9 PASS.

### ARSR01-G22
Reverse control completed.

### ARSR01-G23
No label leakage.

### ARSR01-G24
No repair-scope creep.

### ARSR01-G25
Residual forensics completed.

### ARSR01-G26
36/36 invariants PASS.

### ARSR01-G27
36/36 forbidden PASS.

### ARSR01-G28
Full regression + signature MATCH.

Required for repair closure:

\[
\boxed{28/28\ PASS}
\]

---

# 48. Allowed Final Repair Verdicts

Exactly one:

```text
ARSR01_LDSR_VERIFIED
ARSR01_LDSR_PARTIAL
ARSR01_LDSR_NO_EFFECT
ARSR01_LDSR_REGRESSION
ARSR01_PREIMPLEMENTATION_REJECTED
ARSR01_BLOCKED
```

---

# 49. ARSR01_LDSR_VERIFIED

Use only if:

- simulation gate passed;
- 36/36 invariants PASS;
- 36/36 forbidden PASS;
- 28/28 release gates PASS;
- causal held-out improvement PASS;
- causal OOD improvement PASS;
- permutation safeguards PASS;
- regression/signature PASS.

---

# 50. ARSR01_LDSR_PARTIAL

Use if:

- LDSR behaves mathematically correctly and safely;
- some causal improvement occurs;
- but one or more empirical repair thresholds fail;
- no catastrophic regression occurs.

Do not silently add a second repair.

---

# 51. ARSR01_LDSR_NO_EFFECT

Use if:

- implementation is correct;
- safety holds;
- but held-out/OOD/permutation evidence shows no meaningful causal benefit.

---

# 52. ARSR01_LDSR_REGRESSION

Use if LDSR causes:

- candidate loss;
- reachability loss;
- grounding change;
- Vision/text regression;
- permutation causal deterioration;
- new forced errors beyond allowed safeguard.

---

# 53. Required Machine-Readable Artifacts

Produce:

```text
ARSR01-LDSR-REPAIR-REPORT.md

arsr01_lineage.json
arsr01_formula.json
arsr01_counterfactual_heldout.jsonl
arsr01_counterfactual_ood.jsonl
arsr01_counterfactual_permutation.jsonl
arsr01_counterfactual_summary.json

arsr01_property_tests.json
arsr01_locality.json
arsr01_determinism.json
arsr01_mutation_audit.json

arsr01_candidate_conservation.json
arsr01_reachability_conservation.json
arsr01_grounding_digest_conservation.json
arsr01_vision_regression.json
arsr01_text_regression.json

arsr01_atg01_heldout_results.jsonl
arsr01_atg01_heldout_summary.json
arsr01_reverse_results.jsonl
arsr01_ood_results.jsonl
arsr01_permutation_results.jsonl

arsr01_pre_post_contribution_delta.jsonl
arsr01_residual_forensics.jsonl

arsr01_invariants.json
arsr01_forbidden_mechanisms.json
arsr01_release_gates.json
arsr01_signature_verification.json
arsr01_failures.jsonl
```

---

# 54. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — ARSR01 / LDSR v1.0

REPAIR:
ARSR01

COMPONENT:
LDSR v1.0

AUTHORIZED CLASS:
R-A RETRIEVAL_SPECIFICITY_REPAIR

PARENT ATG01 COMMIT:
7e43974

PARENT F01 COMMIT:
74f788e

PARENT MANIFEST SHA256:
41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7

HISTORICAL COGNITIVE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / MISMATCH

COUNTERFACTUAL SIMULATION:
PASS / FAIL / BLOCKED

SIM HELD-OUT:
CORRECT ... /20
WRONG ... /20
AMBIGUOUS ... /20
NO RETRIEVAL ... /20

SIM OOD:
FORCED ... /10
AMBIGUOUS ... /10
NO RETRIEVAL ... /10

SIM PERMUTATION:
PERMUTED CORRECT ... /8
NATURAL TARGET DOMINANT ... /8

IMPLEMENTATION:
EXECUTED / NOT_EXECUTED

NEW PERSISTENT PRIMITIVES:
0 / NONZERO

NEW PERSISTENT FIELDS:
0 / NONZERO

NEW LAWS:
0 / NONZERO

NEW LEARNED SCALARS:
0 / NONZERO

CANDIDATE SET CONSERVATION:
... / ...

REACHABILITY CONSERVATION:
... / ...

GROUNDING DIGESTS:
G10 MATCH / MISMATCH
G20 MATCH / MISMATCH
G30 MATCH / MISMATCH
G40 MATCH / MISMATCH

POST-REPAIR HELD-OUT:
CORRECT ... /20
WRONG ... /20
AMBIGUOUS ... /20
NO RETRIEVAL ... /20

POST-REPAIR OOD:
FORCED ... /10
AMBIGUOUS ... /10
NO RETRIEVAL ... /10

POST-REPAIR REVERSE:
OWN ... /10
WRONG ... /10
AMBIGUOUS ... /10
NO RETRIEVAL ... /10

POST-REPAIR PERMUTATION:
PERMUTED CORRECT ... /8
NATURAL TARGET DOMINANT ... /8
CATEGORY COVERAGE ... /4

ARSR01 INVARIANTS:
x /36

FORBIDDEN MECHANISMS:
x /36

RELEASE GATES:
x /28

FULL PYTEST:
...

RUFF:
PASS / FAIL

TYPE CHECK:
PASS / FAIL

FINAL REPAIR VERDICT:
...
============================================================
```

---

# 55. Final Status

\[
\boxed{
\textbf{ARSR01 / LDSR v1.0 — FORMAL REPAIR SPECIFICATION COMPLETE}
}
\]

Status:

```text
FROZEN AFTER FREEZE REVIEW AMENDMENTS
```

Binding freeze amendments:
- baseline is over the pre-scoring local query candidate set \(C_Q\);
- residual is NOT renormalized;
- weak evidence remains weak;
- strict-subset evidence remains informative;
- candidate-set conservation refers to pre-scoring discovery candidates;
- simulation safety has no undefined “material improvement” clause.

No implementation is authorized before the separate counterfactual-simulation gate passes.
