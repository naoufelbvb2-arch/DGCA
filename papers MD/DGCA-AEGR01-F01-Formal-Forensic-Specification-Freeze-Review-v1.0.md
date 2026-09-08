# DGCA Phase 2.6 — AEGR01-F01
## Boundary-Induced Transition Specificity & Descriptor-Mass Forensics 01
## Formal Forensic Specification Freeze Review v1.0

**Review Target:** `DGCA-Phase-2.6-AEGR01-F01-Boundary-Transition-Specificity-Mass-Forensics-Formal-Specification-v1.0.md`  
**Frozen Output:** `DGCA-Phase-2.6-AEGR01-F01-Boundary-Transition-Specificity-Mass-Forensics-Formal-Specification-v1.0-FROZEN.md`  
**Review Outcome:** **PASS WITH BINDING FORENSIC AMENDMENTS**  
**Historical Cognitive Signature:** `915119d40643cb97`

# 1. Executive Decision

The candidate forensic design correctly targeted the new unresolved region after
AEGR01:

- descriptor-mass expansion;
- transition genericity/collision;
- descriptor-compression aliasing.

Freeze review found four material issues that required amendment before execution:

1. C1/C2 mass controls were not safe to interpret unless the parent M0 score
   could first be decomposed and reproduced exactly from individual descriptor
   contributions.
2. the original compression-alias definition was too broad and could classify
   ordinary many-to-one compression as pathological aliasing.
3. boundary-density oversegmentation could not be promoted to a causal verdict
   because the forensic protocol freezes all boundaries and authorizes no
   boundary-removal counterfactual.
4. multi-stage classification could double-count one causal mechanism when
   compression aliasing itself creates downstream transition genericity.

All four are corrected in the frozen specification.

Final status:

\[
\boxed{
\textbf{AEGR01-F01 Formal Forensic Specification v1.0 — FROZEN}
}
\]

Only strict read-only forensic execution is authorized.

---

# 2. Parent Governance State

Freeze review confirms the corrected parent state:

```text
M0 OOD forced = 10/10
S15 = FAIL
Safety = 15/16
AEGR01 counterfactual verdict = AEGR01_COUNTERFACTUAL_SAFETY_FAIL
Implementation Authorized = NO
```

AEGR01-F01 must not inherit the erroneous `16/16 safety PASS` wording from the
uncorrected execution report.

---

# 3. Defect A — C1/C2 Could Become Approximate Counterfactuals

The candidate specification proposed:

- C1: descriptor deduplication;
- C2: parent-identity intersection.

But if the installed M0 score cannot be reconstructed exactly as a sum of
descriptor-level contributions, C1/C2 would become approximations of an unknown
scorer.

Any conclusion about descriptor mass would then be unreliable.

---

# 4. Binding Score-Decomposition Gate

Before C1/C2:

the exact B/M0 non-sequence score ledger must reproduce every candidate score,
winner and tie state for:

- 20 held-out probes;
- 10 OOD probes;
- 8 permutation probes.

Required:

\[
Score^{ledger}_{B}(c)=Score^{actual}_{B}(c)
\]

for every candidate.

If exact reproduction is impossible:

```text
AEGR01_F01_BLOCKED
```

C1/C2 may not be estimated.

This prevents forensic controls from silently changing retrieval semantics.

---

# 5. Frozen C1 / C2 Interpretation

### C1 — Recording-Local Descriptor Deduplication

Each descriptor identity may contribute at most once per recording to the
read-only base-score ledger.

Purpose:

separate repeated descriptor multiplicity from distinct acoustic identities.

### C2 — Parent-Identity Intersection

Only descriptor identities already present in the same recording's parent
single-event compressed identity set may contribute to the read-only base ledger.

Purpose:

separate newly exposed identities from multiplicity.

Both are forensic decompositions only.

Neither may be proposed as a production repair.

---

# 6. Descriptor-Mass Causal Criterion

`DESCRIPTOR_MASS_DOMINANCE` requires BOTH:

### DM1
The OOD commitment regression must revert to the parent commitment state under
C1 or C2.

### DM2
At least half of the held-out rank improvements P→B must lose at least one rank
of improvement under C1 or C2.

Thus descriptor mass must explain both:
- a meaningful part of the held-out benefit;
- the OOD safety regression.

---

# 7. Defect B — Original Compression Alias Definition Was Too Broad

A rule like:

```text
different precompression support maps -> same compressed descriptor
```

would classify normal lossy compression as aliasing almost everywhere.

That does not prove a retrieval-relevant defect.

The alias definition therefore required a stronger causal condition.

---

# 8. Frozen Retrieval-Relevant Alias Definition

For a compressed directional transition:

\[
t=(u\rightarrow v)
\]

trace each grounding occurrence back to its exact ordered ATGF01
precompression event-support pair:

\[
\Pi=(A_u^{pre},A_v^{pre})
\]

For held-out query pair \(\Pi_Q\), compute:

\[
Sim_{pre}(\Pi_Q,\Pi_j)
=
\frac12[
WJ(A_u^Q,A_u^j)+WJ(A_v^Q,A_v^j)
]
\]

using the frozen ATGF01 weighted-Jaccard metric.

For candidate concept \(c\):

\[
PreMatch(t,c)=
\max_{j\in Groundings(t,c)}
Sim_{pre}(\Pi_Q,\Pi_j)
\]

A retrieval-relevant compression alias exists only when:

1. the same compressed directional transition supports correct and wrong
   concepts;
2. compressed sequence scoring gives the wrong concept at least as much
   contribution as the correct concept;
3. precompression evidence satisfies:

\[
PreMatch(correct)>PreMatch(wrong)
\]

Therefore the precompression representation distinguishes the correct grounding
better, but the compressed transition identity loses that distinction.

No similarity threshold.
No clustering.

---

# 9. Frozen Compression-Alias Criterion

`DESCRIPTOR_COMPRESSION_ALIASING` requires:

### CA1
At least `3/5` large D0→D1 regression probes contain a dominant wrong-support
transition satisfying the retrieval-relevant alias definition.

### CA2
At least `8/14` Q2 failures contain a wrong/shared transition where
precompression evidence favors the correct concept but compressed sequence
contribution fails to preserve that ordering.

No alias-transition removal or oracle rescoring is allowed.

This keeps the study explanatory rather than repair-like.

---

# 10. Transition Genericity Criterion

`TRANSITION_GENERICITY_COLLISION` requires BOTH:

### TG1
At least `3/5` large D0→D1 regressions are primarily T2/T3/T4/T5.

### TG2
For at least `8/14` Q2-failure probes, more than half of the strongest wrong
candidate's sequence mass is contributed by shared transitions:

\[
K_t\ge2
\]

The majority condition is diagnostic only.

No transition is pruned.

---

# 11. Defect C — Boundary Density Was Not Causally Testable

The candidate design listed:

`BOUNDARY_DENSITY_OVERSEGMENTATION`

as a possible primary verdict.

But AEGR01-F01 freezes boundary sets and forbids:
- boundary deletion;
- boundary movement;
- alternate boundary rules.

Therefore density can only be correlated with failures, not causally isolated.

---

# 12. Frozen Boundary-Density Rule

Boundary density may be reported only as:

```text
BOUNDARY_DENSITY_ASSOCIATED
```

It is a secondary diagnostic observation.

It cannot become the primary verdict.

It cannot authorize:

`AEGR01_BOUNDARY_SELECTIVITY_REVISIT`.

Any future boundary-selectivity repair would require a separate causal
counterfactual.

---

# 13. Defect D — Multi-Stage Double Counting

Compression aliasing can itself make compressed transitions shared/generic.

If the same transition instances satisfy both:
- compression aliasing;
- transition genericity;

then calling this `MULTI_STAGE` would count one upstream cause twice.

---

# 14. Frozen Multi-Stage Independence Rule

`MULTI_STAGE` requires at least two mechanisms with independent causal evidence.

If transition genericity is supported only by the same transition instances
already explained by compression aliasing:

```text
PRIMARY = DESCRIPTOR_COMPRESSION_ALIASING
```

not `MULTI_STAGE`.

Likewise descriptor-mass dominance must be independently supported through C1/C2
effects.

---

# 15. Frozen Primary Verdict Vocabulary

Exactly one:

```text
DESCRIPTOR_MASS_DOMINANCE
TRANSITION_GENERICITY_COLLISION
DESCRIPTOR_COMPRESSION_ALIASING
MULTI_STAGE
NO_PRIMARY_FAILURE_FOUND
INCONCLUSIVE
```

Boundary density is excluded from primary verdicts.

---

# 16. Frozen Repair Recommendation Mapping

### Descriptor mass dominance

```text
AUDITORY_EVENT_EVIDENCE_MASS_GOVERNANCE_REPAIR_CANDIDATE
```

This avoids prematurely assuming the event compressor itself is wrong.

### Transition genericity collision

```text
AUDIO_TRANSITION_SPECIFICITY_REPAIR_CANDIDATE
```

### Descriptor compression aliasing

```text
EVENT_DESCRIPTOR_COMPRESSION_REPAIR_CANDIDATE
```

### No primary failure / inconclusive

```text
NO_REPAIR_YET
```

Abstention repair remains deferred because the OOD failure emerged after an
upstream representation change.

---

# 17. Why Mass Governance Is Separate from Compression

AEGR01 increased retained descriptor mass because multiple lawful events are each
compressed independently.

That does not by itself prove that per-event compression is incorrect.

A future mass-governance repair may need to act on:
- evidence contribution conservation;
- event-family mass;
- retrieval contribution semantics;

rather than deleting acoustic descriptors.

The forensic study must localize this before design.

---

# 18. Governance Counts

Frozen specification verifies:

\[
\boxed{16/16\ mathematical\ prechecks}
\]

\[
\boxed{36/36\ architectural\ invariants}
\]

\[
\boxed{36/36\ forbidden\ mechanisms}
\]

\[
\boxed{28/28\ forensic\ gates}
\]

for full forensic closure.

---

# 19. What This Freeze Does Not Authorize

No:
- source changes;
- boundary tuning;
- event deletion;
- transition pruning;
- descriptor suppression;
- fanout cutoff;
- abstention threshold;
- OOD-specific rule;
- compression repair;
- retrieval repair;
- new Law;
- new persistent state.

All C1/C2/alias operations are diagnostic ledgers only.

---

# 20. Final Freeze Verdict

The candidate specification is superseded by:

`DGCA-Phase-2.6-AEGR01-F01-Boundary-Transition-Specificity-Mass-Forensics-Formal-Specification-v1.0-FROZEN.md`

Final status:

\[
\boxed{
\textbf{AEGR01-F01 FORMAL FORENSIC SPECIFICATION v1.0 — FROZEN}
}
\]

---

# 21. Next Authorized Step

The next and only authorized step is:

\[
\boxed{
\textbf{AEGR01-F01 STRICT READ-ONLY FORENSIC EXECUTION}
}
\]

The execution must return:

- exactly one primary causal verdict;
- exactly one repair recommendation;
- no implementation.

If the score decomposition cannot be reconstructed exactly, or required
precompression transition provenance is unavailable:

```text
AEGR01_F01_BLOCKED
```

No approximation is permitted.
