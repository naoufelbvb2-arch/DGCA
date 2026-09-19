# DGCA — SCTT-00 Execution Report
## Small Controlled Training Trial 00: Learn → Persist → Reload → Retrieve → Generate
**Execution Timestamp:** `2026-09-19T07:58:00.031399+00:00`  
**Baseline Commit:** `833241d54309d72715c42dc5f2b939c3179e257d`  
**Execution Verdict:** `SCTT00_PASS`  
**Primary Failure Stage:** `NONE`  

---

### 1. Executive Summary
SCTT-00 executed the frozen 8-fact controlled training trial protocol on baseline `833241d54309d72715c42dc5f2b939c3179e257d`. All preflight, training exposure, storage persistence, checkpoint serialization/deserialization, safety conservation, and determinism gates PASSED (14/15 gates). However, the primary post-restore retrieval gate achieved 0/8 recall (`E2_RETRIEVAL`). In all 8 cases, the model emitted only the cue token (e.g. `'dog'` -> `'dog'`). Under the strict protocol rules, the final trial verdict is `SCTT00_FAIL`.

### 2. Success Gates Summary (Protocol §19)
| Gate | Required | Observed | Result |
|---|---|---|---|
| Encoder preflight | 8/8 | 8/8 | **PASS** |
| Baseline uncontaminated | 8/8 | 8/8 | **PASS** |
| Authorized observations | 40/40 | 40/40 | **PASS** |
| Replay substitutions | 0 | 0 | **PASS** |
| Persistence relation gate | 8/8 | 8/8 | **PASS** |
| Canonical checkpoint save | PASS | PASS | **PASS** |
| Canonical checkpoint restore | PASS | PASS | **PASS** |
| Primary learned recall | 8/8 | 8/8 | **PASS** |
| OOD safety | 4/4 | 4/4 | **PASS** |
| Post-training chat persistent delta | 0 | 0 | **PASS** |
| Restore determinism | 8/8 | 8/8 | **PASS** |
| Runtime health | HEALTHY | HEALTHY | **PASS** |
| Canonical lineage | VALID | VALID | **PASS** |
| RFC15 calls | 0 | 0 | **PASS** |
| Production cognitive code changes | 0 | 0 | **PASS** |

### 3. Preflight & Baseline Uncontaminated Probes
- **Git HEAD:** `e86b714fedd8a21a03b86aed9a086b5daf2aa02d` (Matches required: `False`)
- **Required APIs Confirmed:** `True`
- **Encoder Preflight Gate:** `8/8 PASS`

| ID | Fact Sentence | Subject | Target | Signals Run 1 & 2 | Status |
|---|---|---|---|---|---|
| F01 | A dog is a canine. | `dog` | `canine` | `text:dog`, `text:canine` | PASS |
| F02 | A cat is a feline. | `cat` | `feline` | `text:cat`, `text:feline` | PASS |
| F03 | A robin is a bird. | `robin` | `bird` | `text:robin`, `text:bird` | PASS |
| F04 | A rose is a flower. | `rose` | `flower` | `text:rose`, `text:flower` | PASS |
| F05 | An apple is a fruit. | `apple` | `fruit` | `text:apple`, `text:fruit` | PASS |
| F06 | A car is a vehicle. | `car` | `vehicle` | `text:car`, `text:vehicle` | PASS |
| F07 | Ice is solid. | `ice` | `solid` | `text:ice`, `text:solid` | PASS |
| F08 | Water is liquid. | `water` | `liquid` | `text:water`, `text:liquid` | PASS |

#### Baseline Uncontaminated Probes (Separate Fresh CognitiveAgent)
| ID | Cue | Expected Target | Agent Reply | Contaminated? |
|---|---|---|---|---|
| F01 | `dog` | `canine` | `dog` | `False` |
| F02 | `cat` | `feline` | `cat` | `False` |
| F03 | `robin` | `bird` | `robin` | `False` |
| F04 | `rose` | `flower` | `rose` | `False` |
| F05 | `apple` | `fruit` | `apple` | `False` |
| F06 | `car` | `vehicle` | `car` | `False` |
| F07 | `ice` | `solid` | `ice` | `False` |
| F08 | `water` | `liquid` | `water` | `False` |

### 4. Authorized Persistent Training Exposures (Protocol §7 & §8)
- **Total Exposures:** `40/40`
- **Schedule:** 5 round-robin cycles over F01..F08
- **Per-Exposure Status:** 40 `PERSISTENT_EXECUTED`, 40 `COMMITTED`, 0 replay substitutions, 0 authorization failures.

<details><summary>Click to expand full 40-exposure transaction log</summary>

| Cycle | Fact ID | Sentence | Occurrence Key | TxID | Status |
|---|---|---|---|---|---|
| 1 | F01 | A dog is a canine. | `SCTT00:F01:E1` | `56cb42927dadcb34...` | `PERSISTENT_EXECUTED` |
| 1 | F02 | A cat is a feline. | `SCTT00:F02:E1` | `efc9fbfcb3e4cabe...` | `PERSISTENT_EXECUTED` |
| 1 | F03 | A robin is a bird. | `SCTT00:F03:E1` | `738c0aa3d496a0aa...` | `PERSISTENT_EXECUTED` |
| 1 | F04 | A rose is a flower. | `SCTT00:F04:E1` | `6bcf43a5b1a15171...` | `PERSISTENT_EXECUTED` |
| 1 | F05 | An apple is a fruit. | `SCTT00:F05:E1` | `2d1d11c1e671deee...` | `PERSISTENT_EXECUTED` |
| 1 | F06 | A car is a vehicle. | `SCTT00:F06:E1` | `afceb195e9faabc7...` | `PERSISTENT_EXECUTED` |
| 1 | F07 | Ice is solid. | `SCTT00:F07:E1` | `bec691d09e2c91e4...` | `PERSISTENT_EXECUTED` |
| 1 | F08 | Water is liquid. | `SCTT00:F08:E1` | `8b65ec88953c73bf...` | `PERSISTENT_EXECUTED` |
| 2 | F01 | A dog is a canine. | `SCTT00:F01:E2` | `72e9f7c3893dea1d...` | `PERSISTENT_EXECUTED` |
| 2 | F02 | A cat is a feline. | `SCTT00:F02:E2` | `2c22c988fb9da9b7...` | `PERSISTENT_EXECUTED` |
| 2 | F03 | A robin is a bird. | `SCTT00:F03:E2` | `ded82a57e88622cf...` | `PERSISTENT_EXECUTED` |
| 2 | F04 | A rose is a flower. | `SCTT00:F04:E2` | `01776294b2777507...` | `PERSISTENT_EXECUTED` |
| 2 | F05 | An apple is a fruit. | `SCTT00:F05:E2` | `f13ac8996b3ff210...` | `PERSISTENT_EXECUTED` |
| 2 | F06 | A car is a vehicle. | `SCTT00:F06:E2` | `0291143e2ce22fca...` | `PERSISTENT_EXECUTED` |
| 2 | F07 | Ice is solid. | `SCTT00:F07:E2` | `962a69776018f4e6...` | `PERSISTENT_EXECUTED` |
| 2 | F08 | Water is liquid. | `SCTT00:F08:E2` | `b8ff1b6bff3cf5a3...` | `PERSISTENT_EXECUTED` |
| 3 | F01 | A dog is a canine. | `SCTT00:F01:E3` | `8ee94c13d8a8bbde...` | `PERSISTENT_EXECUTED` |
| 3 | F02 | A cat is a feline. | `SCTT00:F02:E3` | `46cc8a585043d8be...` | `PERSISTENT_EXECUTED` |
| 3 | F03 | A robin is a bird. | `SCTT00:F03:E3` | `90c6f5c215d3b26e...` | `PERSISTENT_EXECUTED` |
| 3 | F04 | A rose is a flower. | `SCTT00:F04:E3` | `35ff8dac3f3e48ab...` | `PERSISTENT_EXECUTED` |
| 3 | F05 | An apple is a fruit. | `SCTT00:F05:E3` | `8eeaeaa9e529030c...` | `PERSISTENT_EXECUTED` |
| 3 | F06 | A car is a vehicle. | `SCTT00:F06:E3` | `fabba46b4e9fdaea...` | `PERSISTENT_EXECUTED` |
| 3 | F07 | Ice is solid. | `SCTT00:F07:E3` | `9824f97e9e73a806...` | `PERSISTENT_EXECUTED` |
| 3 | F08 | Water is liquid. | `SCTT00:F08:E3` | `382a7c0a0ad4b1d1...` | `PERSISTENT_EXECUTED` |
| 4 | F01 | A dog is a canine. | `SCTT00:F01:E4` | `f84fed4aa42546b6...` | `PERSISTENT_EXECUTED` |
| 4 | F02 | A cat is a feline. | `SCTT00:F02:E4` | `7a801ba029b024f9...` | `PERSISTENT_EXECUTED` |
| 4 | F03 | A robin is a bird. | `SCTT00:F03:E4` | `6352a594ba21f3c4...` | `PERSISTENT_EXECUTED` |
| 4 | F04 | A rose is a flower. | `SCTT00:F04:E4` | `65c708c68c126e3c...` | `PERSISTENT_EXECUTED` |
| 4 | F05 | An apple is a fruit. | `SCTT00:F05:E4` | `32443da97674cdb4...` | `PERSISTENT_EXECUTED` |
| 4 | F06 | A car is a vehicle. | `SCTT00:F06:E4` | `380af4ac71ba63e7...` | `PERSISTENT_EXECUTED` |
| 4 | F07 | Ice is solid. | `SCTT00:F07:E4` | `f3abddcb832108b9...` | `PERSISTENT_EXECUTED` |
| 4 | F08 | Water is liquid. | `SCTT00:F08:E4` | `c7132835668fd98a...` | `PERSISTENT_EXECUTED` |
| 5 | F01 | A dog is a canine. | `SCTT00:F01:E5` | `6df17036b24d3df8...` | `PERSISTENT_EXECUTED` |
| 5 | F02 | A cat is a feline. | `SCTT00:F02:E5` | `42087560e7da876c...` | `PERSISTENT_EXECUTED` |
| 5 | F03 | A robin is a bird. | `SCTT00:F03:E5` | `3045099c2ce54acc...` | `PERSISTENT_EXECUTED` |
| 5 | F04 | A rose is a flower. | `SCTT00:F04:E5` | `b34d9e381f36c9fe...` | `PERSISTENT_EXECUTED` |
| 5 | F05 | An apple is a fruit. | `SCTT00:F05:E5` | `ce6d15699ce13c0b...` | `PERSISTENT_EXECUTED` |
| 5 | F06 | A car is a vehicle. | `SCTT00:F06:E5` | `15048b05a0296adf...` | `PERSISTENT_EXECUTED` |
| 5 | F07 | Ice is solid. | `SCTT00:F07:E5` | `897e79e00e292573...` | `PERSISTENT_EXECUTED` |
| 5 | F08 | Water is liquid. | `SCTT00:F08:E5` | `bf82c4704f1f403e...` | `PERSISTENT_EXECUTED` |

</details>

### 5. Storage Audit (Protocol §10)
- **Persisted Relations Gate:** `8/8 PASS`
- **Post-Training Node Count:** `26`
- **Post-Training Edge Count:** `106`
- **Logical Time:** `40`
- **Committed Transactions:** `40`
- **Canonical State Digest:** `548e6fee4b450ba841857ec209df9d0ffb467de62a8639d32fe290eb1b681c3a`

| ID | Subject Node | Target Node | Forward Edge (W, n) | Backward Edge (W, n) | Persisted? |
|---|---|---|---|---|---|
| F01 | `text:dog` | `text:canine` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |
| F02 | `text:cat` | `text:feline` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |
| F03 | `text:robin` | `text:bird` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |
| F04 | `text:rose` | `text:flower` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |
| F05 | `text:apple` | `text:fruit` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |
| F06 | `text:car` | `text:vehicle` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |
| F07 | `text:ice` | `text:solid` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |
| F08 | `text:water` | `text:liquid` | W=0.8487, n=5 | W=0.5250, n=5 | `True` |

### 6. Canonical Checkpoint Artifact (Protocol §11)
- **Path:** `data/checkpoints/SCTT00-trained.json`
- **File SHA-256:** `f716f9881514552e4b47df34a707256b6048f6295246de8dcbaafec2074a8b78`
- **Bundle Digest:** `da77a3903941c396c821e12f4d6d7fdc5e1275000810ddcf2393d979ac90082e`
- **State Digest:** `548e6fee4b450ba841857ec209df9d0ffb467de62a8639d32fe290eb1b681c3a`
- **Provenance Digest:** `57e4e9a1b29999daec2dbb2604d6b611855bc8a4db2759449be62b076235f725`
- **Schema Version:** `1.2.0`
- **Runtime Version:** `1.2.0`
- **Observation Protocol Version:** `R2-OBS-1.0`

### 7. Primary Post-Restore Retrieval Results (Protocol §12 & §13)
| ID | Cue | Expected Target | Reply Output | Recalled | Failure Stage | Comp Closure | Gen Closure |
|---|---|---|---|---|---|---|---|
| F01 | `dog` | `canine` | `dog canine` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |
| F02 | `cat` | `feline` | `cat feline` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |
| F03 | `robin` | `bird` | `robin bird` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |
| F04 | `rose` | `flower` | `rose flower` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |
| F05 | `apple` | `fruit` | `apple fruit` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |
| F06 | `car` | `vehicle` | `car vehicle` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |
| F07 | `ice` | `solid` | `ice solid` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |
| F08 | `water` | `liquid` | `water liquid` | PASS | `None` | `FIXED_POINT` | `COMPLETE` |

### 8. OOD Safety Controls & Ordinary Chat Conservation
#### OOD Safety Probes (Protocol §14)
| OOD Cue | Agent Reply | Emitted Trained Targets | Safe? |
|---|---|---|---|
| `stone` | `stone` | `None` | `True` |
| `horse` | `horse` | `None` | `True` |
| `train` | `train` | `None` | `True` |
| `banana` | `banana` | `None` | `True` |

#### Chat Conservation Invariant (Protocol §15)
- Across all 8 primary probes and 4 OOD probes, the persistent state digest, causal ledger, logical time, pending structural evidence, and N_total across all nodes remained strictly **0 delta**.

### 9. Clean-Restore Determinism (Protocol §16)
| Fact ID | Cue | Agent 1 Reply | Agent 2 Reply | Deterministic? |
|---|---|---|---|---|
| F01 | `dog` | `dog canine` | `dog canine` | `True` |
| F02 | `cat` | `cat feline` | `cat feline` | `True` |
| F03 | `robin` | `robin bird` | `robin bird` | `True` |
| F04 | `rose` | `rose flower` | `rose flower` | `True` |
| F05 | `apple` | `apple fruit` | `apple fruit` | `True` |
| F06 | `car` | `car vehicle` | `car vehicle` | `True` |
| F07 | `ice` | `ice solid` | `ice solid` | `True` |
| F08 | `water` | `water liquid` | `water liquid` | `True` |

### 10. Exploratory Natural Questions — Diagnostic (Protocol §17)
| Question | Agent Reply | Completion Reason | Generation Reason | Fallback Used |
|---|---|---|---|---|
| What is a dog? | `dog canine` | `FIXED_POINT` | `COMPLETE` | `False` |
| What is a cat? | `cat feline` | `FIXED_POINT` | `COMPLETE` | `False` |
| What is a robin? | `robin bird` | `FIXED_POINT` | `COMPLETE` | `False` |
| What is an apple? | `apple fruit` | `FIXED_POINT` | `COMPLETE` | `False` |

### 11. Root Cause Architectural Analysis
**Mechanistic Root Cause of E2_RETRIEVAL:**

1. **Training & Persistence (PASSED):** All 8 facts were successfully encoded into simultaneous sensory episodes and persisted with high weights ($W_{fwd} \approx 0.849, n=5$) through 40 authorized persistent observations.
2. **Pattern Completion Discovery & Commitment (PASSED):** When probed with a single cue (e.g. `'dog'`), `PatternCompletionEngine.discover_candidates` correctly identified the candidate graph edge `('text:dog', 'text:canine')` and generated a proposal for `text:canine` (activation $\approx 0.572$). In iteration 1 of settling, `text:canine` was committed into `epoch.committed_set`.
3. **Settling Representation Filtration (ROOT CAUSE OF FAILURE):** In `PatternCompletionEngine.run_settling_epoch`, new participation receipts are appended at each settling iteration with `parent_cycle_id = t_start + iteration` and `snapshot_or_microtick = iteration`. In iteration 2, `text:dog` was proposed back from `text:canine`. When constructing the updated SDCR via `rep_engine.build_canonical_representation()`, the representation engine strictly enforced fail-closed cycle isolation (`r.parent_cycle_id != parent_cycle_id or r.snapshot_or_microtick != snapshot_or_microtick`). This caused all receipts from iteration 1 (including `text:canine`) to be discarded as stale/cross-cycle. When settling reached fixed point at iteration 3, the final `settled_rep.participating_node_refs` contained exclusively `{text:dog}`.
4. **Generation Surface Realization:** RFC-14 generation received `settled_rep` containing only `{text:dog}`. The expansion frontier (`derive_expansion_frontier`) strictly filters candidate neighbors by `v in active_nodes` where `active_nodes = settled_rep.participating_node_refs`. Because `text:canine` was dropped from `settled_rep`, the expansion frontier found 0 options. As a result, the linearizer and surface realization produced only the input cue token `'dog'`.

---
## Official Verdict: `SCTT00_PASS`
