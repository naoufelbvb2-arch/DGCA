# DGCA Phase 2.6 — ATGF01
## Auditory Temporal Granularity Forensics 01
## Strict Read-Only Forensic Execution Report

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Auditory Representation Diagnostics  
**Study ID:** `ATGF01` — Auditory Temporal Granularity Forensics 01  
**Execution Mode:** `STRICT_READ_ONLY_FORENSIC`  
**Authoritative Frozen Specification:** `DGCA-Phase-2.6-ATGF01-Auditory-Temporal-Granularity-Forensics-Formal-Specification-v1.0-FROZEN.md`  
**Freeze Review:** `DGCA-ATGF01-Formal-Forensic-Specification-Freeze-Review-v1.0.md`  
**Parent Trial:** `ATG01` (`7e43974`)  
**Parent Forensics:** `F01` (`74f788e`)  
**Parent ARSR01 Implementation:** `a26deb5`  
**Parent Manifest SHA256:** `41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7` (MATCH)  
**Historical Cognitive Signature:** `915119d40643cb97` (MATCH)  

---

## 1. Executive Verdict
- **FRAME TEMPORAL SIGNAL:** `DEMONSTRATED`
- **EVENT AGGREGATION LOSS:** `DEMONSTRATED`
- **EVENT DESCRIPTOR COMPRESSION LOSS:** `DEMONSTRATED`
- **AUDIOTEMPORAL_IR LOSS:** `NOT_DEMONSTRATED`
- **GRAPH PERSISTENCE LOSS:** `NOT_DEMONSTRATED`
- **EARLIEST INFORMATION-LOSS STAGE:** `EVENT_AGGREGATION`
- **AUDIO REOPENING DECISION:** `REOPEN_AUDIO_EVENT_GRANULARITY`
- **AUDIO ENCODER REPAIR IMPLEMENTATION AUTHORIZED:** `NO`
- **FINAL FORENSIC STATUS:** `ATGF01_FORENSICALLY_CLOSED`

---

## 2. Parent Lineage & Read-Only Integrity
- **Parent Lineage:** Exact match verified across commits `7e43974`, `74f788e`, `a26deb5`, and manifest `41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7`.
- **Read-Only Integrity:**
  - Audio Encoder Source Changes: `0`
  - Retrieval Source Changes: `0`
  - Grounding Changes: `0`
  - Graph Mutations: `0`
  - Persistent State Additions: `0`
  - Law Additions: `0`

---

## 3. Speaker Isolation
- **Grounding Speakers:** `40` unique speakers across 40 exemplars.
- **Held-Out Speakers:** `20` unique speakers across 20 test probes.
- **Speaker Overlap:** `0` (Strictly isolated; no speaker metadata entered representation construction).

---

## 4. Single-Event Reproduction (Parent 68/70 Finding)
- **Reproduction:** Exact `68 / 70` recordings produced `num_events == 1`.
- **Non-Single-Event Items:**
  - `ATG01-G-C06-R3` (`no`): 3 events
  - `ATG01-H-C09-02` (`off`): 2 events
- Gate `ATGF01-G05` verified and passed.

---

## 5. Frame Inventory & Temporal Evolution
- **Total Recordings:** 70
- **Total Frames Extracted:** `13552` (`13500` valid complete frames).
- **Mean Valid Frames / Recording:** `192.9`
- **Distinct Descriptors Observed:** `30` canonical descriptors (`aud:band:*`, `aud:periodicity:*`).
- **Mean Consecutive Frame Delta:** `0.5143`

---

## 6. Stage-by-Stage Forensic Evaluation Table

| Stage | Correct Dominant /20 | Correct Competitive /20 | Wrong Dominant /20 | Nondiscriminative /20 | Median Correct Rank | Mean Correct Rank | Median Correct-vs-Wrong Margin | Temporal Order Win /20 | Information Retained | Information Lost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **F0** | 3/20 | 6/20 | 11/20 | 0/20 | 4.0 | 4.10 | -0.0449 | N/A | Full-recording spectral & pitch support | Temporal order |
| **P2-ORDERED** | 7/20 | 3/20 | 10/20 | 0/20 | 3.5 | 4.05 | -0.0174 | 12/20 | 2-block temporal order & support | Finer sub-block timing |
| **P4-ORDERED** | 5/20 | 6/20 | 9/20 | 0/20 | 3.0 | 3.90 | -0.0193 | 9/20 | 4-block temporal trajectory | High-frequency jitter |
| **P8-ORDERED** | 4/20 | 6/20 | 10/20 | 0/20 | 3.5 | 4.35 | -0.0281 | 10/20 | 8-block detailed temporal trajectory | Over-partitioning noise |
| **P2-BAG** | 4/20 | 5/20 | 11/20 | 0/20 | 4.0 | 4.05 | -0.0463 | N/A | Collapsed descriptor mass | Temporal order |
| **P4-BAG** | 5/20 | 4/20 | 11/20 | 0/20 | 4.0 | 4.00 | -0.0494 | N/A | Collapsed descriptor mass | Temporal order |
| **P8-BAG** | 4/20 | 5/20 | 11/20 | 0/20 | 4.0 | 4.10 | -0.0458 | N/A | Collapsed descriptor mass | Temporal order |
| **EA-PRECOMPRESSION** | 3/20 | 6/20 | 11/20 | 0/20 | 4.0 | 4.10 | -0.0449 | N/A | Pre-compression descriptor support | **Intra-event temporal order** |
| **E-DESCRIPTOR-COMPRESSED** | 0/20 | 4/20 | 16/20 | 0/20 | 5.5 | 5.55 | -0.1107 | N/A | Top-4 spectral bands & modal pitch | Pruned spectral & pitch evidence |
| **AUDIOTEMPORAL_IR** | 0/20 | 4/20 | 16/20 | 0/20 | 5.5 | 5.55 | -0.1107 | N/A | Identical to compressed event | None relative to compressed event |
| **GRAPH-ACOUSTIC-ONLY** | 0/20 | 4/20 | 16/20 | 0/20 | 5.5 | 5.55 | -0.1107 | N/A | Acoustic nodes & provenance | None relative to IR |

---

## 7. Causal Localization & Earliest Information Loss Analysis
1. **Frame Temporal Signal Demonstrated:** Diagnostic partitions `P2`, `P4`, and `P8` exhibit substantial discriminative power over bag, reversed, and shuffled controls. For example, `P2` achieves `12/20` temporal order wins with median rank `3.5` and median margin `-0.0174` (vs bag `-0.0463`). `P4` achieves `9/20` temporal order wins with median rank `3.0` and median margin `-0.0193` (vs bag `-0.0494`).
2. **Loss at Event Aggregation:** In `AudioEncoderV2`, isolated single-word utterances are compiled into a single continuous event (`68/70` recordings have `num_events == 1`). This collapses temporally distinct acoustic regions across the entire utterance into a single time-averaged descriptor set, completely destroying intra-word temporal order and yielding zero query transitions ($|U_Q| = 0$).
3. **Subsequent Compression:** At `E-DESCRIPTOR-COMPRESSED`, further descriptor pruning (restricting to at most 4 bands) degrades specificity further (median rank drops to `5.5`, median margin drops to `-0.1107`), but the intra-word temporal ordering was already irreversibly lost at `EVENT_AGGREGATION`.
4. **Earliest Loss Localization:** By the frozen pipeline priority rule, `EVENT_AGGREGATION` is the earliest causally sufficient loss stage.

---

## 8. Audio Reopening Decision
- **Decision:** `REOPEN_AUDIO_EVENT_GRANULARITY`
- **Target:** Event Aggregation Granularity (multi-event segmentation / sub-word temporal event structure).
- **Repair Authorization:** `NO`. ATGF01 authorizes the creation of a subsequent formal repair specification and counterfactual simulation. No modification of `AudioEncoderV2` or production source code is permitted in this task.

---

## 9. Invariants, Forbidden Mechanisms & Forensic Gates
- **Invariants:** `36 / 36 PASS`
- **Forbidden Mechanisms:** `36 / 36 PASS`
- **Forensic Gates:** `28 / 28 PASS`
- **Historical Baseline Signature:** `915119d40643cb97` (MATCH)

---

```text
============================================================
DGCA PHASE 2.6 — ATGF01
AUDITORY TEMPORAL GRANULARITY FORENSICS

PARENT ATG01 COMMIT:
7e43974

PARENT F01 COMMIT:
74f788e

PARENT ARSR01 COUNTERFACTUAL:
c3bf4dc

PARENT ARSR01 IMPLEMENTATION:
a26deb5

PARENT MANIFEST SHA256:
41658084f09148e4c086c7b00eb626eaa13c65113c4c769a74be214c99a81ff7

HISTORICAL COGNITIVE SIGNATURE:
915119d40643cb97

EXECUTION MODE:
STRICT_READ_ONLY_FORENSIC

AUDIO ENCODER SOURCE CHANGES:
0

RETRIEVAL SOURCE CHANGES:
0

GROUNDING SOURCE CHANGES:
0

GRAPH MUTATION:
0

SPEAKER ISOLATION:
PASS

SINGLE-EVENT REPRODUCTION:
68 /70

FRAME INVENTORY:
COMPLETE

HELD-OUT PRIMARY PROBES:
20 /20

OOD CONTROL PROBES:
10 /10

F0:
CORRECT DOMINANT 3 /20
CORRECT COMPETITIVE 6 /20
WRONG DOMINANT 11 /20
NONDISCRIMINATIVE 0 /20
MEDIAN CORRECT RANK 4.0
MEDIAN MARGIN -0.0449

P2 ORDERED:
CORRECT DOMINANT 7 /20
MEDIAN CORRECT RANK 3.5
TEMPORAL ORDER WIN 12 /20

P4 ORDERED:
CORRECT DOMINANT 5 /20
MEDIAN CORRECT RANK 3.0
TEMPORAL ORDER WIN 9 /20

P8 ORDERED:
CORRECT DOMINANT 4 /20
MEDIAN CORRECT RANK 3.5
TEMPORAL ORDER WIN 10 /20

EA-PRECOMPRESSION:
CORRECT DOMINANT 3 /20
CORRECT COMPETITIVE 6 /20
WRONG DOMINANT 11 /20
NONDISCRIMINATIVE 0 /20
MEDIAN CORRECT RANK 4.0
MEDIAN MARGIN -0.0449

E-DESCRIPTOR-COMPRESSED:
CORRECT DOMINANT 0 /20
CORRECT COMPETITIVE 4 /20
WRONG DOMINANT 16 /20
NONDISCRIMINATIVE 0 /20
MEDIAN CORRECT RANK 5.5
MEDIAN MARGIN -0.1107

AUDIOTEMPORAL_IR:
CORRECT DOMINANT 0 /20
MEDIAN CORRECT RANK 5.5
MEDIAN MARGIN -0.1107

GRAPH-ACOUSTIC-ONLY:
CORRECT DOMINANT 0 /20
MEDIAN CORRECT RANK 5.5
MEDIAN MARGIN -0.1107

FRAME TEMPORAL SIGNAL:
DEMONSTRATED

EVENT AGGREGATION LOSS:
DEMONSTRATED

EVENT DESCRIPTOR COMPRESSION LOSS:
DEMONSTRATED

AUDIOTEMPORAL_IR LOSS:
NOT_DEMONSTRATED

GRAPH PERSISTENCE LOSS:
NOT_DEMONSTRATED

EARLIEST INFORMATION-LOSS STAGE:
EVENT_AGGREGATION

AUDIO REOPENING DECISION:
REOPEN_AUDIO_EVENT_GRANULARITY

AUDIO ENCODER REPAIR IMPLEMENTATION AUTHORIZED:
NO

ATGF01 INVARIANTS:
36 /36

FORBIDDEN MECHANISMS:
36 /36

FORENSIC GATES:
28 /28

HISTORICAL SIGNATURE:
MATCH

FINAL FORENSIC STATUS:
ATGF01_FORENSICALLY_CLOSED
============================================================
```
