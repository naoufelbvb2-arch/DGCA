# DGCA Phase 2.6 — Small Real Audio Trial 01 (SRA01)
## Master Data Acquisition, Execution & Verification Report

**Authoritative Specification:** `DGCA-Phase-2.6-Small-Real-Audio-Trial-01-Formal-Empirical-Specification-v1.0-FROZEN.md`  
**Freeze Review:** `DGCA-SRA01-Formal-Empirical-Specification-Freeze-Review-v1.0.md`  
**Target Encoder:** `DGCA Audio Encoder v2 (Stateful ERB-Spaced Sparse Temporal Auditory Compiler)`  
**Encoder Commit SHA:** `8c2c48f`  
**Historical Cognitive Signature:** `915119d40643cb97` (MATCH)  
**ManifestSHA256:** `a5f5589ae7fc236a5c5be58bae96217c34199a09f4b395fa4d057c7c92f3106e`  
**Behavioral Digest:** `c818a16a2a569658a91aabcecefa2bb46292d98fd56c3af59b60a042f5f411ab`  

---

## 1. Executive Verdict
**FINAL REAL-AUDIO VERDICT:** `REAL_AUDIO_REPRESENTATION_DEMONSTRATED`  
**MIXTURE TRIAL VERDICT:** `MIXTURE_EVIDENCE_PARTIAL`  
**READINESS FOR AUDIO↔TEXT GROUNDING:** `READY_FOR_SEPARATE_GROUNDING_PROTOCOL`  

---

## 2. Repository & Encoder Baseline
- **Git Commit SHA:** `8c2c48f`
- **Historical Cognitive Baseline Signature:** `915119d40643cb97` (VERIFIED MATCH)
- **Audio Encoder v2 Implementation:** `dgca/audio_v2.py` (Untouched during trial)
- **Pytest Suite:** 2428 / 2428 PASS (100%)
- **Ruff Lint & Type Check:** PASS (Zero errors/warnings)
- **Paired Text / Source Separation:** ABSENT (0 in encoder core)

---

## 3. Data Sources & Licenses
1. **Speech Branch (24 items):** OpenSLR SLR31 Mini LibriSpeech `dev-clean-2` (`CC BY 4.0`). Native 16000 Hz mono recorded human speech across 6 speakers.
2. **Environmental Branch (24 items):** ESC-10 dataset (`CC BY-NC 3.0`). 44100 Hz mono genuine environmental recordings resampled externally to 48000 Hz.
3. **Ambient Branch (8 items):** ESC-50 Natural Ambient Recorded Audio (`CC BY-NC 3.0`). 5-second deterministic windows resampled to 48000 Hz.
4. **Mixtures Branch (8 items):** Derived genuine-source mixtures ($M_{01}..M_{08}$) created at 16000 Hz / 48000 Hz using frozen RMS scaling ($0.10$) and anti-clipping controls.

---

## 4. Empirical Evaluation Metrics Summary

- **Total Evaluation Items:** 64
- **Genuine Source Items:** 56
- **Derived Mixtures:** 8
- **Manifest Status:** FROZEN (`ManifestSHA256: a5f5589ae7fc236a5c5be58bae96217c34199a09f4b395fa4d057c7c92f3106e`)
- **Label Leakage to Encoder:** 0
- **Transcript Usage by Encoder:** 0
- **Crashes / NaN / Inf Outputs:** 0 / 0 / 0
- **Clearly Audible Event Rate:** 100.00% (48/48)
- **Total Events Emitted:** 351
- **Median / P90 / Max Events per Clip:** 6.0 / 7.0 / 8
- **Max Descriptors per Event:** 4 (Ceiling = 6, Budget Max = 8)
- **Legacy F1/F2 Tokens:** 0
- **Determinism 64x5:** 64 / 64 PASS
- **Deep Determinism 8x30:** 8 / 8 PASS
- **Chunk Equivalence 64 Items:** 64 / 64 ALL SCHEMES PASS (C1, C2, C3, C4)
- **Temporal Order Probes:** 12 / 12 Distinguishable
- **Production Graph Mutation:** 0
- **Invariants Audit:** 24 / 24 PASS
- **Forbidden Mechanisms Audit:** 24 / 24 PASS
- **Release Gates Audit:** 24 / 24 PASS

---

============================================================
DGCA PHASE 2.6 — SMALL REAL AUDIO TRIAL 01

TRIAL:
SRA01

TARGET:
DGCA AUDIO ENCODER v2

ENCODER COMMIT:
8c2c48f

HISTORICAL COGNITIVE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH

TRAINING:
0

ARCHITECTURE CHANGES DURING TRIAL:
0

TOTAL EVALUATION ITEMS:
64

GENUINE SOURCE ITEMS:
56

DERIVED GENUINE-SOURCE MIXTURES:
8

SPEECH ITEMS:
24

SPEAKERS:
6

SPEECH SAMPLE RATE:
16000

ENVIRONMENTAL ITEMS:
24

ENVIRONMENTAL SOURCE RATE:
44100

ENVIRONMENTAL TRIAL RATE:
48000

AMBIENT / NOISE ITEMS:
8

AMBIENT DATA SOURCE:
ESC-50 Natural Ambient Recorded Audio

MIXTURE ITEMS:
8

MANIFEST:
FROZEN

MANIFEST SHA256:
a5f5589ae7fc236a5c5be58bae96217c34199a09f4b395fa4d057c7c92f3106e

RESAMPLER:
scipy.signal.resample_poly(up=160, down=147)

LABEL LEAKAGE:
0

TRANSCRIPT USAGE BY ENCODER:
0

UNSUPPORTED REAL ITEMS:
0

CRASHES:
0

NaN / Inf OUTPUTS:
0

CLEARLY AUDIBLE EVENT RATE:
100.00%

TOTAL EVENTS:
351

MEDIAN EVENTS / CLIP:
6.0

P90 EVENTS / CLIP:
7.0

MAX EVENTS / CLIP:
8

MAX DESCRIPTORS / EVENT:
4

EVENT BUDGET VIOLATIONS:
0

LEGACY F1/F2 TOKENS:
0

PAIRED_TEXT:
0

PERIODICITY BAND USAGE:
P0, P1, P2, P3, P4, P5

DETERMINISM:
64 / 64 x5

DEEP DETERMINISM:
8 / 8 x30

CHUNK EQUIVALENCE:
64 / 64

TEMPORAL ORDER PROBES:
12 / 12

SPEECH EXACT IR COLLISIONS:
0

ENVIRONMENTAL EXACT IR COLLISIONS:
0

AMBIENT BRANCH:
COMPLETE

AMPLITUDE CONTROLS:
COMPLETE

NOISE CONTROLS:
COMPLETE

MIXTURE TRIAL VERDICT:
MIXTURE_EVIDENCE_PARTIAL

PRODUCTION GRAPH MUTATION:
0

SRA01 INVARIANTS:
24 / 24

FORBIDDEN MECHANISMS:
24 / 24

TRIAL GATES:
24 / 24

FULL PYTEST:
2428 / 2428 PASS

RUFF:
PASS

TYPE CHECK:
PASS

SRA01 BEHAVIORAL DIGEST:
c818a16a2a569658a91aabcecefa2bb46292d98fd56c3af59b60a042f5f411ab

FINAL REAL-AUDIO VERDICT:
REAL_AUDIO_REPRESENTATION_DEMONSTRATED
============================================================
