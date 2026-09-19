# DGCA — SCTT00-VR01-C01
## Final Closure & Provenance Hardening Specification v1.0 — FROZEN

**Document Status:** FROZEN  
**Target Trial:** Small Controlled Training Trial 00 (SCTT-00)  
**Cognitive Protocol:** `papers MD/DGCA-SCTT-00-Small-Controlled-Training-Trial-Protocol-v1.0-FROZEN.md`  
**Execution Profile:** `SCTT00_POST_REPAIR_RERUN_V1`  
**Protocol Baseline Commit:** `833241d54309d72715c42dc5f2b939c3179e257d`  
**RFC13-SR01 Production Commit:** `e86b714fedd8a21a03b86aed9a086b5daf2aa02d`  
**RFC14-POA01 Production Anchor:** `1a269aac42fcf44a824fe677526a92e6e2f81d9f`  

---

### 1. Scope & Absolute Architectural Boundaries

This specification governs **ONLY** the verification, provenance, and artifact integrity layers of DGCA SCTT-00 following the audit of RFC14-POA01. The cognitive implementations of **RFC13-SR01** (Multi-Snapshot State Reprojection) and **RFC14-POA01** (Precedence Ordering Authority) are mathematically frozen and not under redesign.

#### Absolute Invariants:
1. **Zero Production Drift:** No file within `dgca/**` shall be modified (`git diff 1a269aac42fcf44a824fe677526a92e6e2f81d9f..HEAD -- dgca/` must evaluate to strictly empty).
2. **Cognitive Invariance:** Cognition, graph learning, completion settling, hierarchy expansion, linearization, token emission, encoder semantics, and checkpoint schema are strictly frozen.
3. **Protocol Invariance:** The frozen fact bank (F01..F08), 5-cycle round-robin exposure schedule (40 exposures), OOD cues, and diagnostic questions remain unchanged.
4. **RFC15 Deferred:** RFC15 predictive recurrent generation remains strictly deferred; `CognitiveGraph._recurrent_engine` must remain `None` throughout execution.

---

### 2. Three-Phase Closure Architecture

To resolve defect **C01-G01** (self-referential commit SHA embedding), SCTT00-VR01-C01 establishes a strictly sequenced three-phase commit procedure:

1. **Phase A: C01_SOURCE_COMMIT**
   - Fail-closed preflight hardening in `experiments/sctt00.py`.
   - Mechanical derivation of replay substitutions and RFC15 monitoring.
   - Removal from git of stale canonical empirical artifacts:
     * `data/checkpoints/SCTT00-trained.json`
     * `experiments/results/sctt00-results.json`
     * `papers MD/SCTT-00-EXECUTION-REPORT.md`
     * `papers MD/SCTT00-VR01-IMPLEMENTATION-VERIFICATION-REPORT.md`
   - Addition of test suites `C01-T01` through `C01-T18`.
   - Working tree strictly clean before rerun.

2. **Phase B: C01_ARTIFACT_COMMIT**
   - Clean rerun of `python experiments/sctt00.py` from `C01_SOURCE_COMMIT`.
   - Generates only the 3 canonical empirical artifacts:
     * `data/checkpoints/SCTT00-trained.json`
     * `experiments/results/sctt00-results.json`
     * `papers MD/SCTT-00-EXECUTION-REPORT.md`
   - Committed separately to yield a stable `C01_ARTIFACT_COMMIT`.

3. **Phase C: C01_CLOSURE_COMMIT**
   - Author `papers MD/SCTT00-VR01-C01-FINAL-CLOSURE-REPORT.md` referencing `C01_ARTIFACT_COMMIT` and earlier commits.
   - Never self-embed its own commit SHA.
   - Tag `SCTT00-VR01-VERIFIED` pointing to `C01_CLOSURE_COMMIT`.

---

### 3. Six-Point Fail-Closed Preflight Gate

`experiments/sctt00.py::run_preflight()` blocks execution before training if ANY condition fails:
1. Working tree clean at trial start (`git status --porcelain` is empty).
2. Baseline is ancestor of POA01 anchor (`git merge-base --is-ancestor`).
3. POA01 anchor is ancestor of execution source.
4. Baseline-to-anchor production delta is exactly `dgca/completion.py` and `dgca/generation.py`.
5. Anchor-to-execution production delta is empty.
6. Anchor-to-working-tree production drift is empty.

---

### 4. Mechanical Gate Derivations

1. **Replay Substitutions:** Counted dynamically from exposure records where `status == "PERSISTENT_REPLAY"` or `persistent_phase == "REPLAY"`. If count > 0, gate fails closed.
2. **RFC15 Unused:** `CognitiveGraph._recurrent_engine is None` measured across all trial graphs (baseline agent, training graph, primary restored agent, second restored agent). Any materialization causes gate failure.

---

### 5. Artifact Integrity & Test Fixtures

1. All artifact tests enforce `assert .is_file()`. Missing canonical artifacts fail immediately.
2. Unit tests requiring a checkpoint independently generate into an isolated temporary directory and never touch `data/checkpoints/SCTT00-trained.json`. Canonical artifact tests never silently regenerate missing files.

---

### 6. Acceptance & Verification Suites (C01-T01 .. C01-T18)

| Test ID | Contract Requirement |
|---|---|
| **C01-T01** | Baseline not ancestor of anchor -> preflight BLOCKED before training |
| **C01-T02** | Baseline -> anchor production delta mismatch -> preflight BLOCKED |
| **C01-T03** | Anchor not ancestor of execution -> preflight BLOCKED |
| **C01-T04** | Post-anchor `dgca/**` drift -> preflight BLOCKED |
| **C01-T05** | Dirty working tree -> preflight BLOCKED |
| **C01-T06** | Replay count mechanically derived from exposure records |
| **C01-T07** | Simulated `PERSISTENT_REPLAY` causes replay gate failure |
| **C01-T08** | RFC15 recurrent engine remains unmaterialized (`_recurrent_engine is None`) |
| **C01-T09** | Simulated RFC15 materialization causes RFC15 gate failure |
| **C01-T10** | Missing JSON artifact fails artifact integrity test |
| **C01-T11** | Missing Markdown report fails artifact integrity test |
| **C01-T12** | POA01 unit checkpoint fixture uses isolated temporary location |
| **C01-T13** | Missing canonical SCTT checkpoint is not silently regenerated by tests |
| **C01-T14** | Results JSON and SCTT Markdown report agree on execution source and verdict |
| **C01-T15** | Closure report's `C01_ARTIFACT_COMMIT` resolves to a real Git commit |
| **C01-T16** | `C01_ARTIFACT_COMMIT` is an ancestor of closure commit |
| **C01-T17** | All commit SHAs referenced in closure report exist in repository |
| **C01-T18** | Zero `dgca/**` production code changes from POA01 anchor through C01 closure |
