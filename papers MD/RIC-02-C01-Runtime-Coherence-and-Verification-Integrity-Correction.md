# DGCA — RIC-02-C01: Runtime Coherence & Verification Integrity Correction

**Document ID:** `RIC-02-C01-SPEC`  
**Status:** `RIC02_C01_VERIFIED`  
**Prior Baseline Commit:** `ce8ba8fb55ba1ce9d296eaf09c9f35ada85abeed` (RIC-02 initial implementation)  
**Parent Anchor Commit:** `eb72fabfa4a983dcd82bf4bfa5defae4ceb6d988` (`origin/main`)  
**Historical SCTT Anchor:** `006c16b8bba14ebdc78594604962437dd3e4d4ac` (`SCTT00-VR01-VERIFIED`)  
**Domain:** System Runtime Architectural Integrity & Verification Provenance  

---

## 1. Executive Summary & Purpose

RIC-02-C01 is a strict, narrow correction addressing runtime coherence defects and verification integrity shortcuts introduced during the RIC-02 system-boundary refactor.

While RIC-02 successfully established `CanonicalSystemRuntime` in `dgca/system_runtime.py` and refactored `CognitiveAgent` in `dgca/agent.py` to a thin external façade, several critical architectural invariants and verification protocols were compromised:
1. **Unchecked Constructor Coupling:** `CanonicalSystemRuntime.__init__` accepted arbitrary instances without verifying type or mutual binding coherence between `CanonicalR1RuntimeRoot` and `CanonicalChatRuntime`.
2. **Test-Convenience Alias Pollution:** Properties `_root`, `_graph`, and `_ledger` were added to `CanonicalSystemRuntime` as backwards-compatibility shims for legacy test harnesses, re-introducing leaky internal authority.
3. **Verification Provenance Bypass:** In `experiments/sctt00.py`, a shortcut (`target_exec = SCTT00_VERIFIED_ANCHOR_COMMIT`) and working-tree bypass (`is_post_sctt00`) silently masked post-anchor production drift, subverting the fail-closed integrity of SCTT-00 preflight.
4. **Permissive Duck-Typing:** Functions `_extract_graph_from_target` and `_extract_root_from_target` in `experiments/sctt00.py` and permissive extraction in `compute_safety_snapshot` obscured runtime typing violations.
5. **OOD Probe Contamination:** In `tests/test_ric02_system_runtime.py`, the frozen SCTT-00 OOD cues (`stone`, `horse`, `train`, `banana`) were replaced by ad-hoc probes (`pizza`, `computer`, etc.).

RIC-02-C01 completely resolves all five issues while maintaining absolute byte-identity across all 14 frozen cognitive files.

> [!IMPORTANT]
> This correction achieves **`RIC02_C01_VERIFIED`**. Per specification, RIC-02 is **not** declared finally closed until formal gate sign-off.

---

## 2. Absolute Cognitive Freeze

All 14 core cognitive production files remain 100% byte-identical to the authoritative baseline:
- `dgca/graph.py`
- `dgca/causal_identity.py`
- `dgca/observation.py`
- `dgca/persistence.py`
- `dgca/chat_runtime.py`
- `dgca/completion.py`
- `dgca/generation.py`
- `dgca/recurrent.py`
- `dgca/loop.py`
- `dgca/encoder.py`
- `dgca/audio.py`
- `dgca/audio_v2.py`
- `dgca/vision.py`
- `dgca/legacy_agent.py`

Furthermore, `dgca/agent.py` remains untouched from its thin façade state (`__slots__ = ("_runtime",)`), and `dgca/__init__.py` remains untouched.

---

## 3. Detailed Analysis of Defects & Architectural Corrections

### 3.1 C01-G01: Restoration of SCTT Fail-Closed Provenance
- **Defect:** `experiments/sctt00.py` previously checked if the verified anchor `SCTT00_VERIFIED_ANCHOR_COMMIT` was an ancestor of execution HEAD. If so, it substituted `target_exec = SCTT00_VERIFIED_ANCHOR_COMMIT` and bypassed working-tree diff checks (`if not is_post_sctt00:`). This permitted post-anchor production changes to go undetected during preflight.
- **Correction:** The anchor bypass was eliminated. `execution_source_commit` is now unconditionally the target of diff measurements.
- **Fail-Closed Semantics:** On current HEAD (which contains post-anchor production changes in `dgca/agent.py` and `dgca/system_runtime.py`), `run_preflight()` strictly detects the production drift between anchor and execution HEAD, raising a deterministic `RuntimeError`:
  ```python
  RuntimeError: SCTT00_REPAIR_RERUN_BLOCKED: Unauthorized dgca/** production drift (anchor to execution): ['dgca/__init__.py', 'dgca/agent.py', 'dgca/system_runtime.py']
  ```
- SCTT is a historical regression suite anchored to commit `006c16b8bba14ebdc78594604962437dd3e4d4ac`. It must reject execution on newer production code fail-closed.

### 3.2 C01-G02: Strict Constructor Coherence in CanonicalSystemRuntime
- **Defect:** `CanonicalSystemRuntime.__init__` previously performed trivial assignments:
  ```python
  self._runtime_root = runtime_root
  self._chat_runtime = chat_runtime
  ```
  It accepted arbitrary objects and permitted mismatched pairs where `chat_runtime` referenced a different root or graph than `runtime_root`.
- **Correction:** `CanonicalSystemRuntime.__init__` now enforces strict structural invariance:
  ```python
  if not isinstance(runtime_root, CanonicalR1RuntimeRoot):
      raise TypeError(
          f"runtime_root must be an instance of CanonicalR1RuntimeRoot, got {type(runtime_root).__name__}"
      )
  if not isinstance(chat_runtime, CanonicalChatRuntime):
      raise TypeError(
          f"chat_runtime must be an instance of CanonicalChatRuntime, got {type(chat_runtime).__name__}"
      )
  if chat_runtime._runtime_root is not runtime_root:
      raise ValueError(
          "Runtime coherence error: chat_runtime._runtime_root is not runtime_root"
      )
  if chat_runtime._graph is not runtime_root._graph:
      raise ValueError(
          "Runtime coherence error: chat_runtime._graph is not runtime_root._graph"
      )
  ```

### 3.3 C01-G03: Complete Removal of Test-Convenience Aliases
- **Defect:** `CanonicalSystemRuntime` provided properties `_root`, `_graph`, and `_ledger` for test convenience.
- **Correction:** All three properties have been permanently excised. Callers and test harnesses must explicitly navigate canonical ownership paths:
  - `runtime.runtime_root` (for root operations)
  - `runtime.runtime_root._graph` (for internal graph assertions where authorized)
  - `runtime.runtime_root._ledger` (for ledger verification)
  - `runtime.chat_runtime` (for chat runtime inspection)

### 3.4 C01-G04: Strict Typing in Safety Snapshots & OOD Restoration
- **Defect:** `experiments/sctt00.py` used helper methods `_extract_graph_from_target` and `_extract_root_from_target` to duck-type through `CognitiveAgent`, `CanonicalSystemRuntime`, or other objects.
- **Correction:** The helpers were removed. `compute_safety_snapshot` now strictly requires `CanonicalSystemRuntime | CanonicalR1RuntimeRoot`:
  ```python
  def compute_safety_snapshot(target: CanonicalSystemRuntime | CanonicalR1RuntimeRoot) -> dict[str, Any]:
      if isinstance(target, CanonicalSystemRuntime):
          r = target.runtime_root
      elif isinstance(target, CanonicalR1RuntimeRoot):
          r = target
      else:
          raise TypeError(
              f"Target must be CanonicalSystemRuntime or CanonicalR1RuntimeRoot, got {type(target).__name__}"
          )
      g = r._graph
      ...
  ```
- **OOD Restored:** Frozen SCTT-00 OOD probes (`stone`, `horse`, `train`, `banana`) were restored to primary verification status, confirming exact echo outputs and zero learned target contamination. Extra exploratory probes (`pizza`, `computer`, `chair`, `ocean`) were segregated as secondary RIC-02 probes.

---

## 4. Verification & Test Suite Matrix

### 4.1 C01 Test Suite (C01-T01 through C01-T16)
All 16 required C01 verification tests were added to `tests/test_ric02_system_runtime.py`:
- `test_c01_t01_post_sctt_unauthorized_dgca_change_detected` — PASS
- `test_c01_t02_post_sctt_dirty_dgca_working_tree_detected` — PASS
- `test_c01_t03_historical_artifact_verification_remains_valid` — PASS
- `test_c01_t04_current_head_sctt_preflight_blocks_without_silent_whitelist` — PASS
- `test_c01_t05_canonical_system_runtime_matching_pair_accepted` — PASS
- `test_c01_t06_mismatched_root_chat_pair_rejected` — PASS
- `test_c01_t07_mismatched_graph_binding_rejected` — PASS
- `test_c01_t08_fresh_produces_coherent_pair` — PASS
- `test_c01_t09_from_checkpoint_produces_coherent_pair` — PASS
- `test_c01_t10_canonical_system_runtime_has_no_root_alias` — PASS
- `test_c01_t11_canonical_system_runtime_has_no_graph_alias` — PASS
- `test_c01_t12_canonical_system_runtime_has_no_ledger_alias` — PASS
- `test_c01_t13_cognitive_agent_remains_thin_with_only_runtime_slot` — PASS
- `test_c01_t14_frozen_sctt_ood_exact_outputs` — PASS
- `test_c01_t15_all_four_sctt_ood_probes_contain_zero_learned_targets` — PASS
- `test_c01_t16_optional_ric02_extra_ood_probes_classified_as_additional` — PASS

### 4.2 Overall Test Matrix
| Test Suite | Tests Run | Result | Notes |
|---|---|---|---|
| `tests/test_ric02_system_runtime.py` | 52 | **52 PASSED** | All 36 RIC02 tests + 16 C01 tests |
| `tests/test_sctt00_vr01.py` | 41 | **41 PASSED** | SCTT-00 VR01 verification suite |
| `tests/test_sctt00_harness.py` | 3 | **3 PASSED** | Preflight, artifact conformance, chat conservation |
| `tests/test_ric01_r3_min.py` | 36 | **36 PASSED** | R3 minimal runtime semantics |
| `tests/test_ric01_r3_min_pir01.py` | 18 | **18 PASSED** | PIR-01 invariant suite |
| `tests/test_rfc14_poa01.py` | 26 | **26 PASSED** | POA-01 invariant suite |
| **Complete Repository Suite** (`pytest tests/`) | **3,173** | **3,173 PASSED** | 0 failures, 0 errors, 0 skips |

### 4.3 Code Quality & Linter Gate
- `python -m ruff check dgca/system_runtime.py experiments/sctt00.py tests/test_ric02_system_runtime.py tests/test_sctt00_harness.py tests/test_sctt00_vr01.py`: **0 errors** (All checks passed).

---

## 5. Architectural Verdict

**Final Status:** `RIC02_C01_VERIFIED`  
**Closing Status:** PENDING FINAL SYSTEM CLOSURE GATE
