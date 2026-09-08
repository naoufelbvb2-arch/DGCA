# DGCA Phase 2.6 — AEGR01-F01
## Boundary-Induced Transition Specificity & Descriptor-Mass Forensics 01
## Master Forensic Report

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Auditory Representation / Retrieval Forensics  
**Study ID:** `AEGR01-F01`  
**Execution Mode:** `STRICT_READ_ONLY`  
**Authoritative Frozen Specification:** `DGCA-Phase-2.6-AEGR01-F01-Boundary-Transition-Specificity-Mass-Forensics-Formal-Specification-v1.0-FROZEN.md`  
**Freeze Review:** `DGCA-AEGR01-F01-Formal-Forensic-Specification-Freeze-Review-v1.0.md`  
**Parent AEGR01 Corrected Verdict:** `AEGR01_COUNTERFACTUAL_SAFETY_FAIL`  
**Parent ATGF01 Commit:** `d48c76a`  
**Parent ATG01 Commit:** `7e43974`  
**Parent F01 Commit:** `74f788e`  
**Parent ARSR01 Implementation Commit:** `a26deb5`  
**Historical Cognitive Signature:** `915119d40643cb97` (MATCH)  
**Parent Manifest SHA256:** `41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7` (MATCH)  

---

## 1. Executive Summary & Forensic Verdict
- **Primary Causal Verdict:** `MULTI_STAGE`
- **Next Repair Recommendation:** `AUDITORY_EVENT_EVIDENCE_MASS_GOVERNANCE_REPAIR_CANDIDATE`
- **Secondary Telemetry Finding:** `BOUNDARY_DENSITY_ASSOCIATED`
- **Final Forensic Status:** `AEGR01_F01_FORENSICALLY_CLOSED`
- **Code Modifications:** `0` (Audio source changes = 0, retrieval changes = 0, production graph mutations = 0)

---

## 2. Formal Scientific Findings

### Finding 1: Descriptor-Mass Expansion Drives OOD Safety Regression and Base Retrieval Benefit
- Finer sub-event aggregation increased retained descriptor mass from 479 to 1,217 occurrences (+738).
- Decomposing the mass shows:
  - **Distinct Mass Delta:** +300 new acoustic descriptor identities exposed across sub-events.
  - **Multiplicity Mass Delta:** +438 repeated descriptor occurrences within recordings.
- **Score-Decomposition Gate:** The installed non-sequence base scorer decomposes into individual descriptor contributions with 0.0 error across all 38 test probes.
- In production retrieval (`query_cross_modal`), query evidence is deduplicated ($B - C1 = 0$). Therefore, repeated multiplicity has zero direct effect on query scoring.
- Instead, the newly exposed descriptor identities ($C1 - C2$) drive both:
  1. **OOD Safety Regression:** In probe `ATG01-OOD-O08` ("three"), the parent single-event emitted only `aud:energy:PULSE`, producing a tie between `no` and `on` (ambiguous). Under AEGR01, 19 descriptors were emitted across 4 sub-events, exposing spectral bands that forced `house` as the winner. Under condition C2, removing newly exposed descriptors restored the probe to non-forced (`NO_RESULT / None`), satisfying criterion **DM1**.
  2. **Held-Out Base Retrieval Improvements:** 7 of 12 (58.3%) held-out probes whose M0 base rank improved under AEGR01 had their rank improvement reduced under C2, satisfying criterion **DM2**.
- Consequently, `DESCRIPTOR_MASS_DOMINANCE` is empirically and causally supported on the base evidence path.

### Finding 2: Descriptor-Compression Aliasing Drives Sequence Specificity Inversion
- In the sequence transition path ($D0 \to D1$), held-out correct retrieval regressed from 6/20 (D0) to 4/20 (D1), median rank worsened from 4.0 to 5.0, and 5 probes suffered large rank worsening (>= 2 ranks).
- Precompression support map analysis reveals:
  - In all 5 large regressions (**5/5, 100%**), the dominant wrong transition satisfied the retrieval-relevant compression alias condition: precompression evidence strongly favored the correct concept ($PreMatch(c^*) > PreMatch(w)$), but per-event descriptor compression merged distinct precompression acoustic profiles into identical coarse descriptors (`aud:band:1`, `aud:energy:FALLING`), creating generic transitions that gave more sequence weight to the wrong concept ($SeqLDSR(w) \ge SeqLDSR(c^*)$), satisfying criterion **CA1**.
  - In all 14 Q2 failures (**14/14, 100%**), wrong-dominant transitions exhibited precompression superiority for the correct concept that was erased by compressed transition identity, satisfying criterion **CA2**.
- Consequently, `DESCRIPTOR_COMPRESSION_ALIASING` is empirically and causally supported on the sequence transition path.

### Finding 3: Transition Genericity is Downstream of Compression Aliasing
- Transition fanout analysis classified 592 directional transitions into:
  - `UNIQUE` (K=1): 251 (42.4%)
  - `LOW_SHARED` (K=2..3): 170 (28.7%)
  - `MID_SHARED` (K=4..6): 97 (16.4%)
  - `HIGH_SHARED` (K=7..9): 61 (10.3%)
  - `GLOBAL` (K=10): 13 (2.2%)
- In all large regressions, wrong-sequence mass was heavily dominated by shared transitions ($K_t \ge 2$), satisfying criteria TG1 and TG2.
- Under Section 39's binding dependency rule, because transition genericity is mediated by the exact transition instances that suffer from compression aliasing, genericity is classified as a downstream manifestation of compression aliasing rather than an independent stage.

### Finding 4: Causal Separation & Multi-Stage Architecture
- Two independent causal mechanisms operate at two distinct architectural stages:
  1. **Base Evidence Stage:** Multi-event descriptor mass expansion forces OOD words and improves base lexical matching (`DESCRIPTOR_MASS_DOMINANCE`).
  2. **Sequence Transition Stage:** Per-event descriptor compression loses acoustic specificity across boundaries, generating shared transitions that invert sequence ranking (`DESCRIPTOR_COMPRESSION_ALIASING`).
- Therefore, the primary causal verdict is **`MULTI_STAGE`**.
- Per Section 43, the earliest independently proven upstream mechanism is **`DESCRIPTOR_MASS_DOMINANCE`** (order 1), which maps directly to:
  **AUDITORY_EVENT_EVIDENCE_MASS_GOVERNANCE_REPAIR_CANDIDATE**

---

## 3. Mandatory Metric Telemetry Block

```text
============================================================
DGCA PHASE 2.6 — AEGR01-F01
BOUNDARY-INDUCED TRANSITION SPECIFICITY & DESCRIPTOR-MASS FORENSICS

EXECUTION MODE:
STRICT_READ_ONLY

PARENT AEGR01 CORRECTED VERDICT:
AEGR01_COUNTERFACTUAL_SAFETY_FAIL

AUDIO SOURCE CHANGES:
0

BOUNDARY CHANGES:
0

PRODUCTION GRAPH MUTATION:
0

PARENT P/B/D0/D1 REPRODUCTION:
PASS

PARENT DESCRIPTOR MASS:
479

AEGR01 DESCRIPTOR MASS:
1217

DISTINCT-MASS DELTA:
+300

MULTIPLICITY-MASS DELTA:
+438

OOD FORCED P:
9 /10

OOD FORCED B:
10 /10

OOD FORCED C1:
10 /10

OOD FORCED C2:
9 /10

DESCRIPTOR-MASS CRITERION:
PASS

BOUNDARY DENSITY ASSOCIATION:
PRESENT

TRANSITIONS TOTAL:
592

UNIQUE:
251

LOW_SHARED:
170

MID_SHARED:
97

HIGH_SHARED:
61

GLOBAL:
13

D0→D1 LARGE REGRESSIONS TRACED:
5 /5

Q2 FAILURES TRACED:
14 /14

TRANSITION-GENERICITY CRITERION:
PASS

COMPRESSION-ALIAS CRITERION:
PASS

PRIMARY VERDICT:
MULTI_STAGE

NEXT REPAIR RECOMMENDATION:
AUDITORY_EVENT_EVIDENCE_MASS_GOVERNANCE_REPAIR_CANDIDATE

MATH PRECHECKS:
16 /16

INVARIANTS:
36 /36

FORBIDDEN:
36 /36

FORENSIC GATES:
28 /28

HISTORICAL SIGNATURE:
MATCH

FINAL STATUS:
AEGR01_F01_FORENSICALLY_CLOSED
============================================================
```
