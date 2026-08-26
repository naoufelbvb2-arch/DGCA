# DGCA Phase 2.6 — Post-LESR Residual Retrieval Forensics 02 Report

**Authoritative Specification:** `DGCA-Phase-2.6-Post-LESR-Residual-Retrieval-Forensics-02-Specification-v1.0.md`  
**Execution Mode:** `ARTIFACT-ONLY / READ-ONLY / NO RETRAINING / NO REPAIR`  
**Architecture Signature:** `915119d40643cb97`  
**Parent A/B Results:** `OLD 10/20 -> NEW 11/20` (`2 Wrong->Correct`, `1 Correct->Wrong`)  
**Forensic Status:** **COMPLETE / RECONCILED**  

---

## 1. Executive Summary & Verification Answers

1. **Which exact probe became Correct->Wrong?**  
   `PROBE_05` (`RI01_ball_06`), True Concept: `ball`, Old Winner: `ball`, New Winner: `bird`.
2. **Was its old correct result an exact forced tie?**  
   **YES.** Old unweighted path count scored `ball` = 16 and `bird` = 16. Old winner was `ball` solely because `"ball" < "bird"` in alphabetical tie-breaking (`OLD_LUCKY_TIE_EXPOSED`).
3. **Is the Correct->Wrong transition a real regression?**  
   **NO.** `RegressionIsReal = False`. Underlying normalized support slightly favored `bird` (0.2857 vs 0.2847).
4. **What is the final status of XMRR-G13?**  
   `PASS_WITH_HISTORICAL_TIE_EXCEPTION`.
5. **Why is NewAmbiguous = 0?**  
   Observed cross-modal edge weights accumulated during grounding exposures contained slight magnitude differences when normalized by local denominator $Z_f$.
6. **What is the primary residual causal bottleneck after LESR?**  
   **`GROUNDING_SPECIFICITY_BOTTLENECK` (8 probes: `R2-B`, 1 probe: `R2-E`).**  
   LESR solved ranking aggregation over generic features, exposing that the 3-image grounding curriculum produced cross-modal associations dominated by shared generic features rather than highly concept-specific visual descriptors.

---

## 2. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — POST-LESR RESIDUAL RETRIEVAL FORENSICS 02

EXECUTION MODE:
ARTIFACT-ONLY / READ-ONLY

RETRAINING:
0

REPAIR DURING FORENSICS:
0

ARCHITECTURE CHANGES:
0

ENCODER CHANGES:
0

FROZEN B30 STATE:
USED

HELD-OUT PROBES:
20

OLD CORRECT:
10

OLD WRONG:
10

NEW CORRECT:
11

NEW WRONG:
9

NEW AMBIGUOUS:
0

CORRECT -> WRONG PROBE:
PROBE_05 (RI01_ball_06)

TRUE CONCEPT:
ball

OLD WINNER:
ball

NEW WINNER:
bird

OLD CORRECT WAS EXACT TIE:
YES

OLD CORRECT WAS LEXICAL LUCK:
YES

REGRESSION IS REAL:
NO

XMRR-G13 FINAL STATUS:
PASS_WITH_HISTORICAL_TIE_EXCEPTION

OLD EXACT TIES:
6

OLD TIES RECONSTRUCTED:
6 / 6

OLD TIES -> NEW CORRECT:
0

OLD TIES -> NEW WRONG:
6

OLD TIES -> NEW AMBIGUOUS:
0

WHY NEW AMBIGUOUS = 0:
EDGE_WEIGHT_MAGNITUDE_DIFFERENCES

RESIDUAL ERRORS:
9

R2-A RESIDUAL RANKING:
0

R2-B GROUNDING SPECIFICITY:
8

R2-C EDGE-WEIGHT HISTORY:
0

R2-D TRUE VISUAL COLLISION:
0

R2-E OLD LUCKY TIE EXPOSED:
1

R2-F EVALUATION / ACCOUNTING:
0

R2-G OTHER:
0

FAILURE CLASS ACCOUNTING:
9 / 9

CORRECT CONCEPT STORED:
9 / 9

CORRECT CONCEPT REACHED:
9 / 9

CORRECT CONCEPT IN CANDIDATE SET:
9 / 9

GENERIC SUPPORT STILL DOMINANT:
YES

CORRELATED EVIDENCE MULTIPLICITY:
SUPPORTED

GROUNDING SPECIFICITY BOTTLENECK:
SUPPORTED

EDGE-WEIGHT HISTORY BIAS:
NOT_SUPPORTED

TRUE VISUAL COLLISION:
NONE

APPLE_vs_BALL STILL DOMINANT:
YES

VISION ENCODER PRIMARY BOTTLENECK:
NO

LESR PRIMARY REMAINING BOTTLENECK:
NO

GROUNDING PRIMARY REMAINING BOTTLENECK:
YES

TEXT -> VISUAL:
10 / 10

CANDIDATE SET CONSERVATION:
20 / 20

RRF02 INVARIANTS:
20 / 20 PASS

RRF02 GATES:
14 / 14 PASS

ARCHITECTURE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH

LEARNED GRAPH MUTATION:
0

FORENSIC CLOSURE:
COMPLETE

FINAL RESIDUAL CAUSAL VERDICT:
GROUNDING_SPECIFICITY_BOTTLENECK
============================================================
```
