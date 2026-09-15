# DGCA Phase 2.6 — BTSR01

## Bounded Tonotopic Selection Repair 01

# Strict Read-Only Pre-Implementation Counterfactual Master Report v1.0 — FINAL

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6  
**Repair ID:** `BTSR01`  
**Execution Mode:** `STRICT_READ_ONLY_PREIMPLEMENTATION_COUNTERFACTUAL`  
**Parent Repair:** `BFAR01_COUNTERFACTUAL_EFFICACY_FAIL` (commit `0e4afdf`)  
**Parent Forensic:** `BFAR01_F01_FORENSIC_PASS` (commit `73a283b`)  
**Parent Closure:** `BFAR01_F01_C01_CLOSED_WITH_CLARIFICATIONS` (commit `cbd6617`)  
**Historical Cognitive Signature:** `915119d40643cb97` (MATCH)  
**Production Diff (`dgca/*.py`):** 0 lines  
**Authoritative Verdict:** `BTSR01_COUNTERFACTUAL_EFFICACY_FAIL`  
**BTSR Structural Selection Validated:** NO  
**BTSR01 Component Validated:** NO  
**Production Implementation Authorized:** NO  

---

# 1. Executive Verdict

The strict read-only counterfactual execution of **BTSR01 (Bounded Tonotopic Selection Repair 01)** has completed with 100% empirical rigor. The fixed 8-stratum tonotopic selection rule was executed under strict read-only conditions without modifying production cognition.

The counterfactual demonstrates that while the fixed tonotopic selection hypothesis successfully repairs parent failure `CA1_01` (achieving positive causal margin +3.2607 and closure), it **fails** to resolve the causal selection bottleneck across the broader grounded domain:
- **Causal Boundary Support:** 9/12 (3 causal boundaries remain unsupported).
- **Grounded Causal Path Membership:** 10/17 (7 relations lack a complete retained causal path).
- **Parent L1 Repairs:** 2/3/3 repaired (`CA1_01` repaired; `CA1_04` and `CA2_08` remain unclosed).
- **New Grounded L1 Failures:** 6 new membership dropouts occur due to same-stratum competition displacing essential acoustic components.
- **Positive Grounded Causal Margins:** 5/17 (only 5 of 17 grounded relations achieve positive causal margin under frozen LDSR/ASUR).
- **CA1 Grounded Closure:** 3/4.
- **CA2 Grounded Closure:** 2/13.

Because the required structural selection gates (path membership 17/17, parent L1 repairs 3/3, 0 new L1 failures, and boundary support 12/12) are not met, the structural selection hypothesis is **falsified**. Under Section 54, 58, and 82 of the Frozen Specification, the authoritative formal verdict is:

```text
BTSR01_COUNTERFACTUAL_EFFICACY_FAIL
```

Production implementation is strictly **NOT AUTHORIZED**. Under Section 93, no ad-hoc tuning or automatic redesign is permitted; frozen failure forensics are returned.

---

# 2. Governance Lineage

Ancestry includes:
- `6fd2157` (AEMG01 v1.3 COUNTERFACTUAL_PASS)
- `57d3240` (ADCAR01 COUNTERFACTUAL_EFFICACY_FAIL)
- `65b1c30` (ADCAR01-F01 FORENSIC_PASS)
- `a526b42` (ADCAR01-F01-C01 CLOSED_WITH_CLARIFICATIONS)
- `0e4afdf` (BFAR01 COUNTERFACTUAL_EFFICACY_FAIL)
- `73a283b` (BFAR01-F01 FORENSIC_PASS)
- `cbd6617` (BFAR01-F01-C01 CLOSED_WITH_CLARIFICATIONS)

All ancestors verified: 7/7 PASS.

---

# 3. Parent Reproduction

Parent findings reproduced:
- Total competitor relations: 19 (17 grounded, 2 non-grounded).
- Minimax capacity: $K^{transition,global}_{max} = 1 < B_{audio,event} = 8$.
- Grounded relations requiring >8 budget: 0/17.
- BFAR positive grounded margins: 9/17.

---

# 4. Grounded / Non-Grounded Domain

- Grounded competitor relations: 17/19 (4 CA1, 13 CA2).
- Non-grounded relations: 2/19 (`CA1_03`, `CA2_07`, probe `ATG01-H-C08-01` with 0 grounding witnesses). Excluded from causal denominators.

---

# 5. Frozen 12-Boundary Inventory

The 12 immutable grounding-derived causal boundary IDs are reproduced exactly:
1. `ATG01-H-C01-01_B0_1`
2. `ATG01-H-C01-01_B1_2`
3. `ATG01-H-C02-01_B3_4`
4. `ATG01-H-C02-01_B4_5`
5. `ATG01-H-C05-01_B1_2`
6. `ATG01-H-C07-01_B1_2`
7. `ATG01-H-C09-01_B0_1`
8. `ATG01-H-C09-01_B1_2`
9. `ATG01-H-C04-02_B1_2`
10. `ATG01-H-C06-02_B0_1`
11. `ATG01-H-C09-02_B3_4`
12. `ATG01-H-C09-02_B4_5`

Inventory match: 12/12 EXACT.

---

# 6. BTSR Selector Definition

Fixed 8-stratum tonotopic selector:
- Primary selection: within each non-empty fixed stratum, pick descriptor with highest within-event support. Tie break: earlier canonical support order, lower channel index.
- Periodicity authority: if modal periodicity is valid, spectral capacity is 7. If 8 winners exist, remove lowest-support winner (tie break: later canonical support order, higher channel index).
- Residual fill: fill unused capacity from valid unselected descriptors in global support order without displacing primary winners.

---

# 7. Fixed Stratum Map

Formula: $g(i) = \lfloor i / 3 
floor$.
- $S_0 = [0, 1, 2]$
- $S_1 = [3, 4, 5]$
- $S_2 = [6, 7, 8]$
- $S_3 = [9, 10, 11]$
- $S_4 = [12, 13, 14]$
- $S_5 = [15, 16, 17]$
- $S_6 = [18, 19, 20]$
- $S_7 = [21, 22, 23]$

Event-dependent repartition: 0. Periodicity-dependent repartition: 0.

---

# 8. Event Projection Audit

- Total child events projected: 302 across 70 recordings.
- Max tokens per event: 8.
- Budget violations: 0.

---

# 9. Budget Audit

$|F_{BTSR}(E)| \le 8$ holds across all 302 events. 0 budget exceptions.

---

# 10. Selector Firewall

- Label dependence: 0
- Heldout dependence: 0
- Candidate dependence: 0
- Graph-memory dependence: 0
- Speaker dependence: 0
- Forensic-oracle dependence: 0

Firewall integrity: PASS.

---

# 11. Tonotopic Coverage

Distribution of primary stratum winners across the 302 events:
- S0: 278
- S1: 251
- S2: 197
- S3: 134
- S4: 107
- S5: 53
- S6: 52
- S7: 35

---

# 12. Periodicity Displacement

- Events with valid modal periodicity: 203
- Events with 8 primary winners where periodicity removed 1 winner: 2
- Max direct periodicity displacement: 1 slot/event.

---

# 13. Residual Fill

- Events using residual fill: 291 / 302
- Total residual fill selections: 648
- Mean residual slots per event: 2.1457
- Max residual slots per event: 5
- Fraction of spectral selections from residual fill: 0.3697

---

# 14. T0 Base & Candidate Conservation

- T0 base semantic diff: 0
- T0 continuation diff: 0
- Child lexical authority: 0
- Candidate set diff: 0

---

# 15. Transition Construction

Constructed using exact actual-adjacency over consecutive child events: $(u, v) \in F(E_t) 	imes F(E_{t+1})$. Raw transition opportunity ceiling $\le 64$ per boundary preserved.

---

# 16. Transition Authority

- Duplicate query transitions: 0
- Duplicate context authority: 0
- Non-adjacent authority: 0
- Heldout-derived authority: 0
- Authority verdict: `NO_UNLAWFUL_TRANSITION_AUTHORITY_INFLATION`.

---

# 17. Grounded Path Retention

- Grounded causal path membership: 10/17 (Required: 17/17) -> FAIL.

---

# 18. Parent L1 Repair

- Parent L1 targets: `CA1_01`, `CA1_04`, `CA2_08`.
- Repaired: 2/3 (`CA1_01` repaired; `CA1_04` and `CA2_08` unresolved) -> FAIL.

---

# 19. Grounded L2 Realization

- Grounded L2 realizability: 9/17 (Required: 17/17) -> FAIL.

---

# 20. Causal-Boundary Support

- Grounded causal boundary support: 9/12 (Required: 12/12) -> FAIL.
- Unsupported boundaries (3):
  1. `ATG01-H-C01-01_B0_1` (cat)
  2. `ATG01-H-C07-01_B1_2` (go)
  3. `ATG01-H-C09-01_B0_1` (off)

---

# 21. Same-Stratum Causal Collisions

- Events with same-stratum causal collision: 9
- Total causal collisions: 19
- Recovered by residual fill: 7
- Unrecovered collisions: 17
- Unrecovered collisions causing path loss: 6

---

# 22. Grounded Causal Margins

Positive grounded causal margins: 5/17 (Required: 17/17) -> FAIL.

---

# 23. CA1 Grounded Closure

CA1 grounded closure: 3/4 (Required: 4/4) -> FAIL.

---

# 24. CA2 Grounded Closure

CA2 grounded closure: 2/13 (Required: 13/13) -> FAIL.

---

# 25. Sequence Signal

Sequence signal present: 20/20 (Required: 20/20) -> PASS.

---

# 26. Heldout Rank Telemetry

- Correct Rank-1: 4/20
- Wrong: 16/20
- Median correct rank: 5
- Mean correct rank: 5.15

---

# 27. Non-Grounded Telemetry

Probe `ATG01-H-C08-01` (`on` vs `off` / `bird`):
- Parent rank: 8, BTSR rank: 9
- Parent S_seq: 1.4572, BTSR S_seq: 1.4572
- State: NOT_FORCED_NOT_GROUNDED. Causal denominators unaffected.

---

# 28. OOD Safety

- OOD probes evaluated: 10/10 safe.
- Newly forced OOD: 0.

---

# 29. Candidate / Base Conservation

- Candidate set diff: 0
- Base semantic diff: 0
- Sequence-to-base conductance: 0

---

# 30. BFAR-vs-BTSR Transition Topology

- Distinct transitions: BFAR 765 vs BTSR 799
- Grounding->heldout recurrent: BFAR 499 vs BTSR 567
- Median boundary fanout: BFAR 64 vs BTSR 40

---

# 31. Causal Descriptor Recovery

- Parent BFAR dropped causal descriptors: 30
- Recovered by BTSR: 6
- Still dropped under BTSR: 24
- New causal descriptors lost: 12

---

# 32. Rank 8–11 Recovery Audit

- Rank 8 retention: 2/4
- Rank 9 retention: 1/4
- Rank 10 retention: 1/4
- Rank 11 retention: 0/1

---

# 33. Reversal (T2)

- Multiset preservation: IDENTICAL
- Event order: EXACTLY_REVERSED
- Asymmetric directional effect: PASS (20/20 probes)

---

# 34. Streaming / Chunk Equivalence

Whole vs chunked streaming projection: EXACT PASS.

---

# 35. SRA01 Safety

Audio v2 frontend invariants preserved: PASS.

---

# 36. Text / Vision Isolation

- Text behavior change: 0
- Vision behavior change: 0
- Isolation status: PASS.

---

# 37. Prechecks

Evaluated: 26/26 PASS.

---

# 38. Invariants

Evaluated: 48/48 PASS.

---

# 39. Forbidden Mechanisms

Evaluated: 42/42 PASS (0 violations).

---

# 40. Release Gates

Evaluated: 44. Passed: 35/44. Failed: 9/44 (G24, G25, G26, G27, G28, G29, G30, G31, G32).

---

# 41. Execution Integrity

Evaluated: 12/12 PASS.

---

# 42. Deterministic Replay

- Pass 1 hash: `75db074afb5e0101191fe090de8c06b29ef702fdf2e2a8afd4e1158e975fa638`
- Pass 2 hash: `75db074afb5e0101191fe090de8c06b29ef702fdf2e2a8afd4e1158e975fa638`
- Match: EXACT PASS.

---

# 43. Regression

- Before: 2,440 / 2,440 PASS
- After: 2,440 / 2,440 PASS

---

# 44. Production Integrity

Production source diff: 0 lines. Production hashes: MATCH.

---

# 45. Structural-Selection Verdict

`BTSR_STRUCTURAL_SELECTION_VALIDATED: NO`  
(Failed due to path membership dropouts, unrecovered same-stratum collisions, and 3 unsupported causal boundaries).

---

# 46. Component-Validation Verdict

`BTSR01_COMPONENT_VALIDATED: NO`  
(Efficacy gates failed under unchanged LDSR/ASUR).

---

# 47. Final Metrics

Comprehensive metrics recorded in canonical artifacts and Section 48/90 blocks.

---

# 48. Final Formal Verdict

```text
BTSR01_COUNTERFACTUAL_EFFICACY_FAIL
```

---

# 49. Next-Stage Authorization

Under Section 93:
- Production implementation: Strictly **NOT AUTHORIZED**.
- Sequence-discrimination repair next: **NOT APPLICABLE** (structural selection hypothesis failed; failure was in descriptor topology, not solely downstream margin accumulation).
- Automatic redesign: **FORBIDDEN**. Frozen failure forensics returned.

---

# 90. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — BTSR01

EXECUTION MODE:
STRICT_READ_ONLY_PREIMPLEMENTATION_COUNTERFACTUAL

FORMAL REPAIR SPECIFICATION:
v1.1 FROZEN

MASTER PROMPT:
v1.0 FROZEN

PARENT:
BFAR01_COUNTERFACTUAL_EFFICACY_FAIL

PARENT FORENSIC:
BFAR01_F01_FORENSIC_PASS

PARENT CLOSURE:
BFAR01_F01_C01_CLOSED_WITH_CLARIFICATIONS

HISTORICAL SIGNATURE:
MATCH

PARENT REPRODUCTION:
PASS

BTSR SELECTOR:
FIXED_8_STRATUM_TONOTOPIC_SELECTION

SPECTRAL CHANNELS:
24

FIXED STRATA:
8

CHANNELS PER STRATUM:
3

EVENT_DEPENDENT_REPARTITION:
0

PERIODICITY_DEPENDENT_REPARTITION:
0

B_AUDIO_EVENT:
8

MAX BTSR TOKENS/EVENT:
8

BUDGET VIOLATIONS:
0

EVENTS ANALYZED:
302

NEW DESCRIPTORS:
0

COMPOUND TOKENS:
0

WHOLE_PROFILE TOKENS:
0

PAIR TOKENS:
0

SELECTOR LABEL DEPENDENCE:
0

SELECTOR HELDOUT DEPENDENCE:
0

SELECTOR CANDIDATE DEPENDENCE:
0

SELECTOR GRAPH_MEMORY DEPENDENCE:
0

SELECTOR SPEAKER DEPENDENCE:
0

SELECTOR FORENSIC_ORACLE DEPENDENCE:
0

GROUNDING_DERIVED RELATIONS:
17/19

NON_GROUNDED RELATIONS:
2/19

GROUNDED CAUSAL BOUNDARY INVENTORY:
12/12

GROUNDED CAUSAL PATH MEMBERSHIP:
10/17

PARENT L1 FAILURES REPAIRED:
2/3

NEW GROUNDED L1 FAILURES:
6

GROUNDED L2 REALIZABILITY:
9/17

GROUNDED CAUSAL BOUNDARY SUPPORT:
9/12

EVENTS WITH CAUSAL SAME_STRATUM COLLISION:
9

TOTAL CAUSAL SAME_STRATUM COLLISIONS:
19

COLLISIONS RECOVERED BY RESIDUAL FILL:
7

UNRECOVERED COLLISIONS:
17

UNRECOVERED COLLISIONS CAUSING GROUNDED PATH LOSS:
6

EVENTS USING RESIDUAL FILL:
291

TOTAL RESIDUAL FILL SELECTIONS:
648

RESIDUAL FILL FRACTION:
0.3697

EVENTS WITH VALID PERIODICITY:
203

PERIODICITY WINNER DISPLACEMENTS:
2

PERIODICITY CAUSAL WINNER DISPLACEMENTS:
0

POSITIVE GROUNDED CAUSAL MARGINS:
5/17

CA1 GROUNDED CAUSAL CLOSURE:
3/4

CA2 GROUNDED CAUSAL CLOSURE:
2/13

SEQUENCE SIGNAL PRESENT:
20/20

PARENT BFAR DROPPED CAUSAL DESCRIPTORS:
30

RECOVERED BY BTSR:
6

STILL DROPPED:
24

NEW CAUSAL DESCRIPTORS LOST:
12

RANK_8 CAUSAL RETENTION:
2/4

RANK_9 CAUSAL RETENTION:
1/4

RANK_10 CAUSAL RETENTION:
1/4

RANK_11 CAUSAL RETENTION:
0/1

BFAR DISTINCT TRANSITIONS:
765

BTSR DISTINCT TRANSITIONS:
799

BFAR GROUNDING→HELDOUT RECURRENT TRANSITIONS:
499

BTSR GROUNDING→HELDOUT RECURRENT TRANSITIONS:
567

BFAR MEDIAN TRANSITION FANOUT:
64

BTSR MEDIAN TRANSITION FANOUT:
40

T0 BASE SEMANTIC DIFF:
0

T0 CONTINUATION DIFF:
0

CANDIDATE SET DIFF:
0

SEQUENCE→BASE CONDUCTANCE:
0

TRANSITION AUTHORITY:
NO_UNLAWFUL_TRANSITION_AUTHORITY_INFLATION

T1 HELDOUT:
correct=4/20
wrong=16/20
ambiguous=0/20

T1 MEDIAN CORRECT RANK:
5

T1 MEAN CORRECT RANK:
5.15

NON_GROUNDED TELEMETRY:
probe ATG01-H-C08-01 (on vs off/bird): rank 9, S_seq 1.4572, state NOT_FORCED_NOT_GROUNDED

OOD SAFETY:
10/10

NEWLY FORCED OOD:
0

T2 DESCRIPTOR MULTISET:
IDENTICAL

T2 EVENT ORDER:
EXACTLY_REVERSED

T2 ASYMMETRIC DIRECTIONAL EFFECT:
PASS

STREAMING/CHUNK:
PASS

SRA01:
PASS

TEXT ISOLATION:
PASS

VISION ISOLATION:
PASS

NEW NODE TYPES:
0

NEW EDGE TYPES:
0

NEW PERSISTENT FIELDS:
0

NEW LAWS:
0

PRECHECKS:
26/26

INVARIANTS:
48/48

FORBIDDEN:
42/42

RELEASE GATES:
35/44

EXECUTION INTEGRITY:
12/12

DETERMINISTIC REPLAY:
PASS

DETERMINISTIC HASH PASS 1:
75db074afb5e0101191fe090de8c06b29ef702fdf2e2a8afd4e1158e975fa638

DETERMINISTIC HASH PASS 2:
75db074afb5e0101191fe090de8c06b29ef702fdf2e2a8afd4e1158e975fa638

REGRESSION BEFORE:
2440/2440

REGRESSION AFTER:
2440/2440

PRODUCTION SOURCE DIFF:
0

PRODUCTION HASHES:
MATCH

BTSR_STRUCTURAL_SELECTION_VALIDATED:
NO

BTSR01_COMPONENT_VALIDATED:
NO

RESIDUAL_SEQUENCE_DISCRIMINATION:
NOT_APPLICABLE

SEQUENCE_DISCRIMINATION_REPAIR_NEXT:
NOT_APPLICABLE

FINAL VERDICT:
BTSR01_COUNTERFACTUAL_EFFICACY_FAIL

PRODUCTION IMPLEMENTATION AUTHORIZED:
NO

NEXT STAGE IF FULL PASS:
AUDIO_COMPOSITE_REPAIR_COUNTERFACTUAL
============================================================
```
