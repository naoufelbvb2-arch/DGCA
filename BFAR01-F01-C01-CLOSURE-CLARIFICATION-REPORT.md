# DGCA Phase 2.6 — BFAR01-F01-C01

## Grounded-Domain & Denominator Closure Clarification Audit 01

# Strict Read-Only Closure Clarification Report v1.0 — FINAL

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6  
**Audit ID:** `BFAR01-F01-C01`  
**Document Type:** Strict Read-Only Closure Clarification Audit Master Report  
**Version:** `1.0`  
**Execution Mode:** `STRICT_READ_ONLY_CLOSURE_CLARIFICATION`  
**Parent Forensic:** `BFAR01-F01` (`BFAR01_F01_FORENSIC_PASS`, commit `73a283b`)  
**Historical Cognitive Signature:** `915119d40643cb97` (MATCH)  
**Authoritative Verdict:** `BFAR01_F01_C01_CLOSED_WITH_CLARIFICATIONS`  
**Primary Forensic Conclusion:** `CONFIRMED`  
**Next Repair Direction:** `SELECTION_POLICY_REPAIR_JUSTIFIED`  
**Production Implementation:** `NOT AUTHORIZED`  
**Repair Design:** `FORBIDDEN`  

---

# 1. Executive Verdict

The strict read-only closure clarification audit **BFAR01-F01-C01** has completed with 100% mathematical and empirical fidelity. All eight clarification targets (Q1 through Q8) have been resolved. The core scientific finding of BFAR01-F01 ($K^{transition,global}_{max} = 1 <= 8$) is fully confirmed over the grounded causal relation domain. All reporting-domain, denominator, and terminology ambiguities are resolved without altering any parent forensic result or mutating production code.

Authoritative Verdict:
```text
BFAR01_F01_C01_CLOSED_WITH_CLARIFICATIONS
```

---

# 2. Clarification Q1: Grounded Relation Domain (17 vs 2)

- **Total Frozen Competitor Relations:** 19
- **Grounded Relations (17 / 19):**
  - CA1 (4): `CA1_01` (`cat` vs `dog`), `CA1_02` (`house` vs `bed`), `CA1_04` (`bird` vs `tree`), `CA1_05` (`go` vs `no`).
  - CA2 (13): `CA2_01` (`cat` vs `dog`), `CA2_02` (`dog` vs `on`), `CA2_03` (`tree` vs `cat`), `CA2_04` (`bed` vs `go`), `CA2_05` (`house` vs `cat`), `CA2_06` (`go` vs `bird`), `CA2_08` (`off` vs `on`), `CA2_09` (`bird` vs `dog`), `CA2_10` (`cat` vs `dog`), `CA2_11` (`bed` vs `dog`), `CA2_12` (`no` vs `on`), `CA2_13` (`go` vs `bird`), `CA2_14` (`off` vs `house`).
- **Non-Grounded Relations (2 / 19):**
  1. `CA1_03`: probe `ATG01-H-C08-01` (`on` vs `off`), 0 witnesses in grounding, CA1, parent BFAR outcome: UNRESOLVED (Rank 8).
  2. `CA2_07`: probe `ATG01-H-C08-01` (`on` vs `bird`), 0 witnesses in grounding, CA2, parent BFAR outcome: UNRESOLVED (Rank 8).
- **Reason Unavailable:** In ADCAR01-F01, heldout probe `ATG01-H-C08-01` had 0 recurrent causal witness containers connecting `on` to either competitor in the grounding schedule.

---

# 3. K-Domain Clarification

- **Authoritative Optimization Domain:** `GROUNDED_RELATIONS_ONLY` (17 relations).
- Under Binding Clarification C1, only relations with lawful grounding-derived causal paths can establish feasibility.
- **Result Statement:**
  - `GROUNDED STATIC CAUSAL RELATIONS: 17/17 feasible with K_transition_global_max = 1`
  - `NON-GROUNDED RELATIONS: 2/19 NOT_APPLICABLE_TO_GROUNDED_CAUSAL_COVER`

---

# 4. Decisions Requiring >8: Denominator Clarification

- **Clarified Reporting Formulation:**
  - `0/17 grounded relations require >8`
  - `2/19 relations N/A because no grounded causal path`
- **Classification:** `REPORTING_DENOMINATOR_CLARIFICATION`. The underlying scientific result is completely preserved.

---

# 5. Clarification Q2: CA2 13 Probes vs 14 Relations

- **CA2 Probe Denominator:** 13 (distinct witness-positive audio recordings evaluated in parent BFAR).
- **CA2 Competitor-Relation Denominator:** 14 (total frozen CA2 competitor relations in inventory).
- **Explanation:** Probe `ATG01-H-C08-01` (`on` vs `bird`) has 0 grounding witnesses. It was therefore excluded from the 13 witness-positive CA2 evaluation probes in parent BFAR, but was preserved in the 19-relation competitor inventory as `CA2_07`.
- **Classification:** No denominator defect; exact distinction between probe recordings (13) and competitor relations (14) confirmed.

---

# 6. CA1 Probes vs Relations Domain

- **CA1 Frozen Probes:** 5
- **CA1 Frozen Competitor Relations:** 5
- Mapping between CA1 probes and competitor relations is strictly 1-to-1 (`CA1_01` through `CA1_05`).

---

# 7. Clarification Q3: CLOSED vs Functional Rank-1

- **Distinction:** `CAUSAL_COMPETITOR_CLOSED != FINAL_PROBE_RANK_1`.
- A relation is `CLOSED` when its causal margin against the frozen competitor is positive ($Delta_causal > 0$).
- A probe achieves `Rank 1` only when the correct candidate scores higher than ALL 10 vocabulary candidates.
- **CA1 Audit:** 2 / 5 relations are causally closed (`ATG01-H-C05-01` and `ATG01-H-C07-02`), but only 1 / 5 probe achieved Rank 1 (`cat`), because `house` and `go` were superseded by non-competitor baseline scores.
- **CA2 Audit:** 7 / 14 relations are causally closed, but only 2 / 13 probes achieved Rank 1 (`cat` and `tree`).

---

# 8. Clarification Q4: Sequence Signal vs Margin

- **Clarification:** `SEQUENCE_DISCRIMINATIVE: 20/20` in the parent report denoted that every heldout probe had a non-zero, positive true-concept sequence score: $	ext{seq\_score}(c_{true}) > 0$.
- It did NOT denote that the causal margin against every competitor was positive ($Delta_causal > 0$).
- **Disaggregated Metrics Adopted:**
  - `SEQUENCE_SIGNAL_PRESENT: 20/20`
  - `FROZEN_CAUSAL_RELATIONS_WITH_POSITIVE_MARGIN: 9/17` (grounded) [9/19 total].

---

# 9. Clarification Q5: K=1 Static Assignment Integrity

- The exact minimax solution $K^{transition,global}_{max} = 1$ was verified using a **SINGLE GLOBAL STATIC ASSIGNMENT** C_E (for all E=1..302) simultaneously applied across the entire grounded domain.
- Relation-specific switching of $C_E$: **0**.
- At most 1 atomic descriptor per canonical event is retained globally.

---

# 10. K=0 Infeasibility Certificate

- Proof: At $K=0$, $C_E = empty_set$ for all $E$, so no atomic descriptors are retained.
- Because every grounded causal relation requires at least one transition between adjacent canonical events, $|C_E| >= 1$ is required for participating events.
- Thus at $K=0$, 0 relations can be covered. Infeasibility at $K=0$ is proven, certifying $K^*=1$ as the unique minimax optimum.

---

# 11. Clarification Q6: Empty Cores & Structural Redundancy

- `MINIMUM_COVER_CORE = 0` and `BUDGET_FEASIBLE_CORE = 0`.
- Meaning: There is no single event-descriptor pair $(E, d)$ that must appear in *every* optimal assignment or in *every* valid $<= 8$ assignment.
- This demonstrates extensive structural redundancy among alternative grounding transitions, NOT that descriptors are unneeded.

---

# 12. Minimum-Cover Union Breakdown

- `MINIMUM_COVER_UNION: 620 event-descriptor variables` $(E, d)$ across 302 canonical events.
- `UNIQUE DESCRIPTOR IDENTITIES: 25` (21 spectral bands + 4 periodicity bands).

---

# 13. Clarification Q7: Periodicity Role

- Periodicity is neither required by the grounded causal cover (`0`) nor causally blocking (`0`).
- Displaced causal descriptors (`5`) were causally redundant with other retained transitions.

---

# 14. Clarification Q8: Authoritative Grounded Failure Partition

Over the 17 grounded competitor relations:
- `CLOSED`: **9 / 17** (52.9%)
- `L1 MEMBERSHIP FAILURE`: **3 / 17** (`CA1_01`, `CA1_04`, `CA2_08`)
- `L2 DIRECTIONAL FAILURE`: **1 / 17** (`CA2_06` / `ATG01-H-C07-01`)
- `L3 NONPOSITIVE MARGIN`: **4 / 17** (`CA2_02`, `CA2_11`, `CA2_12`, `CA2_14`)
- Grounded Sum: **17 / 17**.
- Non-Grounded Relations: **2 / 19** (`CA1_03`, `CA2_07`).

---

# 15. Selection Repair Authorization

- $K^{transition,global}_{max} = 1 <= 8$ (Confirmed).
- Grounded unresolved relations exhibit genuine L1 selection loss (3 relations).
- Static budget insufficiency is `NOT_SUPPORTED`.
- **Authorized Next Step:** `FINAL_BOUNDED_SELECTION_REPAIR_FORMAL_DESIGN`.
- **Production Implementation:** Strictly `NOT AUTHORIZED`.

---

# 22. Required Final Clarification Block

```text
============================================================
DGCA PHASE 2.6 — BFAR01-F01-C01

PARENT:
BFAR01_F01_FORENSIC_PASS

PARENT COMMIT:
73a283b

GROUNDING-DERIVED COMPETITOR RELATIONS:
17/19

NON-GROUNDED RELATIONS:
2/19

K_ATOMIC_GLOBAL_MAX DOMAIN:
GROUNDED_RELATIONS_ONLY

K_ATOMIC_GLOBAL_MAX:
1

K_ATOMIC_DECISION_MAX:
1

K_TRANSITION_GLOBAL_MAX:
1

K_TRANSITION_DECISION_MAX:
1

STATIC GROUNDED CAUSAL FEASIBILITY:
PASS

RELATIONS REQUIRING >8:
0/17

RELATIONS N/A TO GROUNDED COVER:
2/19

CA1 PROBES:
5

CA1 COMPETITOR RELATIONS:
5

CA2 PROBES:
13

CA2 COMPETITOR RELATIONS:
14

CA2 13-vs-14 EXPLANATION:
13 witness-positive probes evaluated in parent BFAR vs 14 competitor relations in frozen inventory (probe ATG01-H-C08-01 has 0 grounding witnesses so was omitted from CA2-positive probes but retained as frozen relation CA2_07)

CAUSAL CLOSED != FINAL RANK-1:
CONFIRMED

SEQUENCE_SIGNAL_PRESENT:
20/20

POSITIVE GROUNDED CAUSAL MARGINS:
9/17

K=1 STATIC ASSIGNMENT:
SINGLE_GLOBAL_ASSIGNMENT

K=0:
INFEASIBLE

MINIMUM_COVER_CORE:
0

BUDGET_FEASIBLE_CORE:
0

MINIMUM_COVER_UNION EVENT-DESCRIPTOR VARIABLES:
620

MINIMUM_COVER_UNION UNIQUE DESCRIPTOR IDENTITIES:
25

PERIODICITY CAUSALLY REQUIRED:
0

PERIODICITY CAUSALLY BLOCKING:
0

GROUNDED FAILURE PARTITION:
CLOSED=9/17, L1_MEMBERSHIP_FAILURE=3/17, L2_DIRECTIONAL_FAILURE=1/17, L3_NONPOSITIVE_MARGIN=4/17

NON-GROUNDED RELATIONS:
2

PRIMARY FORENSIC CONCLUSION:
CONFIRMED

NEXT REPAIR DIRECTION:
SELECTION_POLICY_REPAIR_JUSTIFIED

PRODUCTION IMPLEMENTATION:
NOT AUTHORIZED
============================================================
```
