# DGCA Phase 2.5 — Real-Data Trial 01
# Pilot Stage Execution & Release Report

```
========================================================================================================
PROJECT:                          DGCA — Dynamic Graph Cognitive Architecture
TRIAL:                            DGCA Phase 2.5 — Real-Data Trial 01
STAGE:                            Pilot Stage (100 Deterministic Train Articles)
DATASET:                          wikimedia/wikipedia (20231101.simple)
DATASET SHA256:                   31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0
ROW COUNT:                        241,787 rows
TRAIN / HELDOUT SPLIT:            217,503 Train (89.96%) / 24,284 HeldOut (10.04%)
PILOT ARTICLES:                   100 articles selected by SHA256("RDT01-PILOT-v1\0" || ArticleID)
PILOT DISPOSAL:                   VERIFIED (Pilot model discarded; Clean M0 established)
PILOT RELEASE GATES:              12 / 12 PASS
========================================================================================================
```

---

## 1. Dataset Verification & Identity

| Property | Authoritative Specification | Measured / Verified Local Value | Status |
|---|---|---|---|
| **Repository** | `wikimedia/wikipedia` | `wikimedia/wikipedia` | **MATCH** |
| **Config** | `20231101.simple` | `20231101.simple` | **MATCH** |
| **Format** | Parquet | Parquet (`pyarrow` compatible) | **MATCH** |
| **Local File Path** | `data/simplewiki_20231101.parquet` | `data/simplewiki_20231101.parquet` (149.62 MB) | **MATCH** |
| **Local File SHA256** | `31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0` | `31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0` | **BIT-EXACT MATCH** |
| **Exact Row Count** | 241,787 rows | 241,787 rows | **BIT-EXACT MATCH** |
| **Field Schema** | `id: string`, `url: string`, `title: string`, `text: string` | `id: string`, `url: string`, `title: string`, `text: string` | **MATCH** |

---

## 2. Deterministic Partition & Pilot Selection

* **Train / HeldOut Split**:
  $$h_i = \text{SHA256}(\text{"RDT01-SPLIT-v1\textbackslash 0"} \parallel \text{ArticleID}_i)$$
  $$u_i = \text{uint64}(h_i[:8]) \implies \text{HeldOut iff } u_i \bmod 10 = 0$$
  - **Train partition**: 217,503 rows (89.96%)
  - **HeldOut partition**: 24,284 rows (10.04%)
  - Manifest stored at [`data/manifests/train_heldout_summary.json`](file:///c:/Users/Laptop/Desktop/DGCA%20FLASH/data/manifests/train_heldout_summary.json)
* **Deterministic Training Order**:
  $$o_i = \text{SHA256}(\text{"RDT01-ORDER-v1\textbackslash 0"} \parallel \text{ArticleID}_i)$$
  - Train articles sorted in ascending lexicographical order of $o_i$.
  - Manifest stored at [`data/manifests/ordered_train_ids.json`](file:///c:/Users/Laptop/Desktop/DGCA%20FLASH/data/manifests/ordered_train_ids.json)
* **Deterministic Pilot Selection**:
  $$p_i = \text{SHA256}(\text{"RDT01-PILOT-v1\textbackslash 0"} \parallel \text{ArticleID}_i)$$
  - First 100 Train rows sorted by $p_i$ selected.
  - Manifest stored at [`data/manifests/pilot_manifest.json`](file:///c:/Users/Laptop/Desktop/DGCA%20FLASH/data/manifests/pilot_manifest.json)
  - Sample Pilot Article IDs: `207357`, `34305`, `115053`, `788647`, `321482`, `221609`, `153024`, `32267`, `987930`...

---

## 3. Pilot Ingestion Execution & Lineage Verification

During the 100-article Pilot execution:
* **Articles Ingested**: 100
* **Segments Ingested**: 1,989 valid natural text segments
* **Words Ingested**: 15,844 natural words
* **One Article = One Root Episode**:
  Every segment of an article shared the exact `RootExternalEpisodeID` computed as $\text{SHA256}(\text{DatasetSnapshotID} \parallel \text{ArticleID})$.
* **Segment Lineage & Determinism**:
  $$\text{SegmentEventID} = \text{SHA256}(\text{RootExternalEpisodeID} \parallel \text{SegmentIndex} \parallel \text{SegmentTextHash})$$

---

## 4. Pilot Isolation, Deduplication & Restorability Tests

### 4.1 Retry Deduplication Test
* Re-ingesting an already-seen pilot article (`ArticleID: 207357`) produced **0 new learning effects** and flagged **23 duplicate segment events** via `is_novel == False`.
* Proves that transport/crash retry does not multiply evidence episodes.

### 4.2 Article Boundary Settling & Quiescence
* At the conclusion of each article, `graph.tick()` and `derive_root_quiescence(root_ep_id, empty_frontier)` settled transient activation.
* Active transient nodes with residual episode tags: **0** (strictly zero transient leakage into next article).

### 4.3 Checkpoint Save/Restore Round-Trip
* State digest before serialization: `eba17bb64b706dda...`
* State digest after reconstruction via `CognitiveGraph.from_dict`: `eba17bb64b706dda...`
* **Bit-Exact Identity: 100% MATCH**.

### 4.4 Evaluation Clone Isolation
* Source pilot model state digest before running evaluation probes: `eba17bb64b706dda...`
* 10 evaluation probes executed against disposable clone `clone_g`.
* Source pilot model state digest after evaluation: `eba17bb64b706dda...`
* **Persistent Mutations to Training Instance: 0**.

---

## 5. Exact 12 Pilot Release Gates Evaluation

| Pilot Release Gate | Evaluated Lower-Level Evidence & Audit Findings | Status |
|---|---|---|
| **P-G01** — Dataset artifact identity & SHA256 | Local Parquet SHA256 matches frozen hash `31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0`. | **PASS** |
| **P-G02** — Schema and exact row count | Exactly 241,787 rows with columns `['id', 'url', 'title', 'text']`. | **PASS** |
| **P-G03** — Deterministic Train/HeldOut manifest | Manifest frozen at `data/manifests/train_heldout_summary.json` (217,503 Train / 24,284 HeldOut). | **PASS** |
| **P-G04** — Deterministic training-order manifest | Manifest frozen at `data/manifests/ordered_train_ids.json`. | **PASS** |
| **P-G05** — 100-article pilot processes lineage | All 100 pilot articles ingested under deterministic root/segment lineage. | **PASS** |
| **P-G06** — Retry/recovery does not duplicate learning | Re-ingested article produced 0 learning effects and 23 duplicate event flags. | **PASS** |
| **P-G07** — Article-end settling/quiescence | 0 active transient nodes across article boundaries. | **PASS** |
| **P-G08** — Telemetry & failure logging complete | Telemetry captured 1,989 segments, 15,844 words, and CPU/wall-clock metrics. | **PASS** |
| **P-G09** — Checkpoint save/restore state digest | Reconstructed graph produces bit-exact identical SHA-256 state digest. | **PASS** |
| **P-G10** — Evaluation clone produces zero mutation | Source graph digest unchanged before and after evaluation probes. | **PASS** |
| **P-G11** — Phase-II signatures & no new primitives | Phase-I baseline signature `c4b2549940a49789` verified; 0 new primitives / 0 new laws. | **PASS** |
| **P-G12** — Pilot model discarded & clean M0 established | Pilot model discarded from memory; fresh clean $M_0$ initialized. | **PASS** |

---

## 6. Pilot Release Verdict

```
========================================================================================================
PILOT RELEASE GATES: 12 / 12 PASS

PILOT STATUS:
PILOT DISCARDED — CLEAN M0 ESTABLISHED
MAIN TRIAL 01 IS AUTHORIZED TO PROCEED
========================================================================================================
```
