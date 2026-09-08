# DGCA Phase 2.6 — ARSR01 / LDSR v1.0
## Formal Repair Specification Freeze Review v1.0

**Review Target:** `DGCA-Phase-2.6-ARSR01-LDSR-Formal-Repair-Specification-v1.0.md`  
**Review Outcome:** **PASS WITH BINDING MATHEMATICAL AMENDMENTS**  
**Frozen Output:** `DGCA-Phase-2.6-ARSR01-LDSR-Formal-Repair-Specification-v1.0-FROZEN.md`

# 1. Executive Finding

The original candidate specification contained a material mathematical defect in the proposed normalized residual form.

Two adversarial counterexamples exposed it.

## Defect A — Unique Evidence Was Destroyed

The candidate specification used the support-set size \(K_f\):

\[
b_f=1/K_f
\]

For \(K_f=1\):

\[
\rho=1,\quad b=1
\]

therefore:

\[
LDSR=0
\]

This incorrectly suppresses an evidence item that uniquely supports one candidate relative to a larger local lexical competition.

## Defect B — Weak Asymmetry Was Artificially Amplified

The candidate specification renormalized positive residuals to unit mass.

For:

\[
\rho=(0.51,0.49)
\]

and baseline \(0.5\):

\[
d^+=(0.01,0)
\]

but residual renormalization produces:

\[
(1,0)
\]

This turns arbitrarily weak evidence into absolute evidence and violates the conservative-repair requirement.

These defects are freeze-blocking in the unamended specification.

# 2. Binding Mathematical Correction

The review replaces support-subset baseline \(K_f\) with the frozen **pre-scoring local query candidate set**:

\[
C_Q
\]

\[
N_Q=|C_Q|
\]

For each evidence item \(f\):

\[
\rho_Q(f,c)
=
\frac{W_{f,c}}
{\sum_{k\in C_Q}W_{f,k}}
\]

with unsupported candidates carrying \(W=0\).

The local uniform query baseline is:

\[
u_Q=1/N_Q
\]

The frozen LDSR formula is:

\[
\boxed{
LDSR_Q(f,c)
=
\max\left(0,\rho_Q(f,c)-\frac1{N_Q}\right)
}
\]

No residual renormalization is permitted.

# 3. Why This Correction Is Better

### Uniform Generic Evidence

If all \(N_Q\) candidates receive equal support:

\[
\rho_Q=1/N_Q
\]

then:

\[
LDSR=0
\]

exactly as intended.

### Evidence Shared by a Strict Subset

For \(N_Q=10\), if two candidates receive equal support:

\[
\rho=(0.5,0.5,0,\dots)
\]

then:

\[
LDSR=(0.4,0.4,0,\dots)
\]

The evidence correctly retains information because it excludes eight alternatives.

### Unique Evidence

For \(N_Q=10\):

\[
\rho=(1,0,\dots)
\]

then:

\[
LDSR=(0.9,0,\dots)
\]

Unique local support remains strongly specific.

### Weak Evidence Remains Weak

For \(N_Q=2\):

\[
\rho=(0.51,0.49)
\]

then:

\[
LDSR=(0.01,0)
\]

not \((1,0)\).

# 4. Total-Variation Interpretation

The total differential mass is:

\[
M_f=\sum_c LDSR_Q(f,c)
\]

and equals:

\[
\boxed{
M_f=
\frac12\sum_c
\left|
\rho_Q(f,c)-1/N_Q
\right|
}
\]

Therefore LDSR has a principled interpretation:

\[
\boxed{
\text{local distance from non-discriminative uniform evidence}
}
\]

No learned threshold or global statistic is needed.

# 5. Governance Review

The amended specification preserves all authorized boundaries:

- R-A retrieval-specificity repair only;
- Audio Encoder frozen;
- English Encoder frozen;
- grounding frozen;
- LESR base weights frozen;
- IGSV unchanged;
- sequence utilization unchanged;
- abstention governance unchanged;
- no persistent state;
- no global IDF;
- no learned scalar;
- no new Law;
- no new primitive.

# 6. Simulation-Gate Clarification

The original S4 clause used undefined wording:

```text
At least one primary causal metric improves materially.
```

while E1–E4 already defined exact efficacy criteria.

S4 is removed.

Implementation authorization now requires:

- safety S1–S3;
- at least one exact efficacy condition E1–E4.

# 7. Candidate-Set Clarification

Candidate conservation now means:

\[
\boxed{
\text{pre-scoring discovery candidate set is unchanged}
}
\]

LDSR may alter numeric support and therefore downstream winner/tie/no-retrieval outcomes, but may not alter candidate discovery.

# 8. Freeze Decision

After applying the binding amendments, no fatal architectural, mathematical, or governance defect remains in the repair specification.

Final decision:

\[
\boxed{\textbf{ARSR01 / LDSR v1.0 FORMAL REPAIR SPECIFICATION — FROZEN}}
\]

Next authorized phase:

\[
\boxed{\textbf{PRE-IMPLEMENTATION COUNTERFACTUAL SIMULATION ONLY}}
\]

Implementation remains forbidden until the frozen simulation gate passes.
