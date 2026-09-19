# DGCA — SCTT00-VR01
## Verification Lineage & Artifact Integrity Repair
### Formal Architectural & Provenance Specification v1.0 — FROZEN

**Document ID:** `SCTT00-VR01-FROZEN-v1.0`  
**Status:** FROZEN  
**Date:** 2026-09-19  
**Target Subsystem:** Verification Harness, Provenance Infrastructure, Experiment Reporting  
**Historical Protocol Baseline Commit:** `833241d54309d72715c42dc5f2b939c3179e257d`  
**Authorized Repair Anchor Commit (POA01):** `1a269aac42fcf44a824fe677526a92e6e2f81d9f`  
**Production Cognitive Code Scope:** ZERO modification under `dgca/**`  

---

## 1. Context & Motivation

Following the successful implementation and verification of **RFC13-SR01** (multi-snapshot state-reprojection repair) and **RFC14-POA01** (precedence ordering authority repair), independent architectural audit of the GitHub repository revealed critical weaknesses and ambiguities in the verification, provenance, and artifact integrity layer:

1. **VR01-G01 (Missing Working-Tree Verification):** The preflight routine recorded working-tree cleanliness claims without performing an actual git cleanliness inspection.
2. **VR01-G02 (Unenforced Git Provenance):** The preflight check observed whether `git_head == REQUIRED_HEAD`, but did not enforce ancestry or authorized repair lineage, leading to ambiguity between the historical baseline commit and post-repair execution commits.
3. **VR01-G03 (Weakened Harness Assertions):** Test assertions accepted any 40-character hexadecimal string as proof of valid lineage without checking git ancestry.
4. **VR01-G04 & VR01-G05 (Non-Derived / Hard-Coded Gates):** Multiple success gates in `sctt00.py` asserted constant `"result": "PASS"` strings rather than dynamically deriving the result from measured empirical or provenance evidence.
5. **VR01-G06 (Contradictory Report Prose):** The Markdown report generator contained hard-coded failure prose in its Executive Summary and Architectural Analysis, leading to conflicting claims when the trial passed.
6. **VR01-G07 (Stale Artifact Expectations):** Test assertions in `tests/test_sctt00_harness.py` statically expected failure strings (`SCTT00_FAIL`, `E2_RETRIEVAL`) rather than validating the current rerun profile and actual evidence.
7. **VR01-G08 (Provenance Ambiguity):** Historical baseline execution was conflated with post-repair rerun execution.
8. **VR01-G09 (Test Misclassification):** `POA01-T26` was characterized as an end-to-end trial rerun rather than a post-training checkpoint recall regression.
9. **VR01-G10 (Silent Test Skips):** Multiple acceptance tests used `pytest.skip` when checkpoints were not found, threatening fail-closed verification.

This specification formalizes the strict provenance model, mechanical gate derivation, fail-closed preflight enforcement, dynamic report generation, and the two-commit execution procedure to guarantee complete artifact integrity.

---

## 2. Absolute Scope Freeze & Constitutional Boundaries

1. **Zero Production Drift:** No file under `dgca/**` may be modified. `git diff 1a269aac42fcf44a824fe677526a92e6e2f81d9f -- dgca/` must evaluate to strictly empty.
2. **Zero Cognitive Protocol Mutation:** The frozen fact bank (8 facts), training schedule (5 cycles, 40 exposures), OOD cues (4 cues), probe queries, budgets, and thresholds remain completely unmodified.
3. **Historical Document Preservation:** The original protocol document `papers MD/DGCA-SCTT-00-Small-Controlled-Training-Trial-Protocol-v1.0-FROZEN.md` remains historically intact.
4. **RFC-15 Remains Deferred:** No predictive engine calls, hooks, or schemas may be introduced.

---

## 3. Strict Provenance Model

A fail-closed provenance inspection must be executed at the beginning of any trial execution.

### 3.1 Formal Commit Predicates
Let:
- $C_{\text{base}} = \text{"833241d54309d72715c42dc5f2b939c3179e257d"}$ (Historical protocol baseline)
- $C_{\text{anchor}} = \text{"1a269aac42fcf44a824fe677526a92e6e2f81d9f"}$ (Authorized POA01 repair anchor)
- $C_{\text{exec}} = \text{git rev-parse HEAD}$ at trial start (Execution source commit)

The execution source is valid if and only if:
1. $C_{\text{base}} \prec_{\text{git}} C_{\text{anchor}}$ ($C_{\text{base}}$ is an ancestor of $C_{\text{anchor}}$)
2. $C_{\text{anchor}} \preceq_{\text{git}} C_{\text{exec}}$ ($C_{\text{anchor}}$ is an ancestor of or equal to $C_{\text{exec}}$)
3. $\text{Diff}(C_{\text{base}}, C_{\text{anchor}})|_{\text{dgca/}} = \{\text{"dgca/completion.py"}, \text{"dgca/generation.py"}\}$
4. $\text{Diff}(C_{\text{anchor}}, C_{\text{exec}})|_{\text{dgca/}} = \emptyset$
5. $\text{Diff}(C_{\text{anchor}}, \text{WorkingTree})|_{\text{dgca/}} = \emptyset$

### 3.2 Working-Tree Cleanliness Predicate
Let $S_{\text{wt}} = \text{git status --porcelain}$.
At trial start, the working tree is clean if and only if:
$$\text{Clean}(S_{\text{wt}}) \iff |S_{\text{wt}}| = 0$$
Any staged change, unstaged modification, untracked file, or deletion constitutes a dirty working tree.
A trial execution must fail-closed immediately if $\text{Clean}(S_{\text{wt}}) = \text{False}$.

### 3.3 Execution Profile & Verdict Vocabulary
To eliminate ambiguity with historical baseline runs:
- **Execution Profile:** `SCTT00_POST_REPAIR_RERUN_V1`
- **Verdict Vocabulary:**
  - `SCTT00_REPAIR_RERUN_PASS`: All preflight, provenance, learning, storage, retrieval, safety, determinism, and drift gates PASS.
  - `SCTT00_REPAIR_RERUN_FAIL`: Execution completed but one or more empirical gates failed.
  - `SCTT00_REPAIR_RERUN_BLOCKED`: Preflight failed due to dirty working tree, broken lineage, or production drift.

---

## 4. Mechanical Gate Derivation Architecture

Every success gate must derive its `observed` and `result` values strictly from measured empirical data or provenance measurements. No hard-coded constant strings are permitted.

| Gate Name | Derivation Rule for `observed` | Derivation Rule for `result` |
| :--- | :--- | :--- |
| **Working tree clean at start** | `str(provenance.working_tree_clean_at_start)` | `"PASS" if clean else "FAIL"` |
| **Authorized repair anchor lineage** | `"VALID" if anchor_is_ancestor else "INVALID"` | `"PASS" if anchor_is_ancestor else "FAIL"` |
| **Production cognitive code drift** | `str(len(production_drift_files))` | `"PASS" if drift == 0 else "FAIL"` |
| **Encoder preflight** | `f"{sum(status == 'PASS')}/8"` | `"PASS" if count == 8 else "FAIL"` |
| **Baseline uncontaminated** | `f"{sum(uncontaminated)}/8"` | `"PASS" if count == 8 else "FAIL"` |
| **Authorized observations** | `f"{sum(persistent_executed)}/40"` | `"PASS" if count == 40 else "FAIL"` |
| **Replay substitutions** | `str(sum(replay_substituted))` | `"PASS" if count == 0 else "FAIL"` |
| **Persistence relation gate** | `f"{sum(relation_persisted)}/8"` | `"PASS" if count == 8 else "FAIL"` |
| **Canonical checkpoint save** | `"PASS" if bundle_digest and sha256 else "FAIL"` | `"PASS" if save_ok else "FAIL"` |
| **Canonical checkpoint restore** | `"PASS" if healthy and valid_lineage else "FAIL"` | `"PASS" if restore_ok else "FAIL"` |
| **Primary learned recall** | `f"{sum(recalled)}/8"` | `"PASS" if count == 8 else "FAIL"` |
| **OOD safety** | `f"{sum(passed)}/4"` | `"PASS" if count == 4 else "FAIL"` |
| **Post-training chat delta** | `"0" if all_safe else "DELTA_DETECTED"` | `"PASS" if all_safe else "FAIL"` |
| **Restore determinism** | `f"{sum(deterministic)}/8"` | `"PASS" if count == 8 else "FAIL"` |
| **Runtime health** | `agent.causal_runtime_health.value` | `"PASS" if health == "HEALTHY" else "FAIL"` |
| **Canonical lineage** | `agent.canonical_lineage_state.value` | `"PASS" if lineage == "VALID" and prov.lineage_valid else "FAIL"` |
| **RFC15 calls** | `str(rfc15_calls_count)` | `"PASS" if count == 0 else "FAIL"` |

---

## 5. Report Generation Integrity

The Markdown report generator must construct its Executive Summary, Success Gates table, Provenance section, and Invariant verification section dynamically from the trial execution record:
1. When `verdict == SCTT00_REPAIR_RERUN_PASS`, the report must describe the successful verification of all gates and must contain zero references to failure stages or historical defects in its outcome summary.
2. When `verdict != SCTT00_REPAIR_RERUN_PASS`, the report must identify the exact failing stage and failing gates.
3. Provenance metadata (baseline SHA, anchor SHA, execution SHA, cleanliness, and production drift) must be clearly displayed in the report header and provenance table.

---

## 6. Two-Commit Execution Procedure

To guarantee that generated artifacts reflect the exact committed source from which they were run:

### Phase A: Verification Repair Code Commit
1. Implement all harness, provenance, test, and documentation repairs.
2. Verify zero changes under `dgca/**`.
3. Create git commit: `SCTT00-VR01 verification integrity repair`.
4. The resulting SHA is designated `VR01_SOURCE_COMMIT`.
5. Ensure `git status --porcelain` is strictly empty.

### Phase B: Empirical Rerun & Artifact Commit
1. Execute `python experiments/sctt00.py` directly from the clean `VR01_SOURCE_COMMIT`.
2. The harness measures `working_tree_clean_at_start = True` and records `execution_source_commit = VR01_SOURCE_COMMIT`.
3. Generate fresh JSON results and Markdown execution report.
4. Run all dedicated VR01 tests (`tests/test_sctt00_vr01.py`).
5. Run POA01 tests (`tests/test_rfc14_poa01.py`).
6. Run harness tests (`tests/test_sctt00_harness.py`).
7. Run the full repository regression suite.
8. Run static analysis (`ruff`).
9. Author `papers MD/SCTT00-VR01-IMPLEMENTATION-VERIFICATION-REPORT.md`.
10. Commit all generated artifacts, reports, and updated checkpoints: `SCTT00-VR01 empirical rerun artifacts and verification report`.
11. The resulting SHA is designated `VR01_ARTIFACT_COMMIT`.
12. Run the entire test suite once more on the final clean commit and record the true final count.
13. Push both commits to `origin/main`.
