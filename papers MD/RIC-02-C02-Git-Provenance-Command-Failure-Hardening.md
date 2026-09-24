# DGCA — RIC-02-C02: Git Provenance Command Failure Hardening
## Strict Fail-Closed Command Execution Specification

**Document ID:** `RIC-02-C02-SPEC`  
**Status:** `RIC02_C02_VERIFIED`  
**Prior Baseline Commit:** `6c98104225975d1cb1ca50dbb34e90c7639bd631` (`origin/main`)  
**Historical Anchor:** `006c16b8bba14ebdc78594604962437dd3e4d4ac` (`SCTT00-VR01-VERIFIED`)  
**Domain:** Git Provenance Invariants & Verification Hardening  

---

## 1. Executive Summary & Defect Characterization

In the post-RIC-02 and C01 architecture, `measure_git_provenance()` in `experiments/sctt00.py` invoked git inspection subprocesses with `check=False` without verifying the subprocess `returncode`.

### The Residual Failure Mode:
Under unexpected git command failures (e.g. `exit code 128`, missing/corrupted git packfile, ambiguous object reference, or broken pipe), a failed git invocation typically emits:
- `returncode != 0`
- `stdout = ""` (or partial output)
- `stderr = "fatal: ..."`

Because `returncode` was uninspected and only `proc.stdout.splitlines()` was processed, `returncode = 128` accompanied by `stdout = ""` was interpreted as an empty changed-file list `[]`. In diff comparisons such as:
- Baseline to Anchor (`dgca/`)
- Anchor to Execution HEAD (`dgca/`)
- Anchor to Working Tree (`dgca/`)

A failed command silently masqueraded as **zero drift** (`[]`). This violated the fundamental fail-closed provenance principle: **command failure must never be interpreted as valid zero drift**.

---

## 2. Hardened Architecture & Implementation

### 2.1 The `_run_git_name_only_diff` Helper
A strict fail-closed command execution helper was introduced in `experiments/sctt00.py`:
```python
def _run_git_name_only_diff(
    args: list[str],
    repo_root: Path,
    provenance_errors: list[str],
) -> list[str]:
    """Runs a git diff --name-only command with strict returncode checking.

    Distinguishes success with empty output (valid zero diff) from command failure.
    On returncode == 0: returns normalized list of changed files.
    On returncode != 0 or OSError: records stderr/detail into provenance_errors and
    returns a singleton error list [f"ERROR: ..."], ensuring non-zero exit code never
    yields an empty list ([]).
    """
    cmd = ["git", "diff", "--name-only", *args, "--", "dgca/"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            stderr_detail = proc.stderr.strip()
            stdout_detail = proc.stdout.strip()
            detail = stderr_detail or stdout_detail or "empty error output"
            err = (
                f"ERROR: command {' '.join(cmd)} failed (rc={proc.returncode}): {detail}"
            )
            provenance_errors.append(err)
            return [err]
        return [
            f.replace("\\", "/").strip()
            for f in proc.stdout.splitlines()
            if f.strip()
        ]
    except (subprocess.SubprocessError, OSError) as e:
        err = f"ERROR: command {' '.join(cmd)} raised {type(e).__name__}: {e}"
        provenance_errors.append(err)
        return [err]
```

### 2.2 Working Tree Status Hardening
Subprocess handling for `git status --porcelain` was hardened identically:
```python
if proc_status.returncode != 0:
    stderr_detail = proc_status.stderr.strip() or "empty error output"
    err = f"ERROR: git status --porcelain failed (rc={proc_status.returncode}): {stderr_detail}"
    working_tree_clean_at_start = False
    dirty_entries = [err]
    provenance_errors.append(err)
else:
    status_lines = [line.strip() for line in proc_status.stdout.splitlines() if line.strip()]
    working_tree_clean_at_start = len(status_lines) == 0
    dirty_entries = status_lines
```
Even if `stdout` is empty, a non-zero exit code marks `working_tree_clean_at_start = False` and populates `provenance_errors`.

### 2.3 Early Preflight Gate
In `run_preflight()`:
```python
# 0. Fail-closed check on git command failures
if prov.get("provenance_errors"):
    raise RuntimeError(
        f"SCTT00_REPAIR_RERUN_BLOCKED: Git provenance command failure: "
        f"{prov['provenance_errors']}"
    )
```
Any command failure immediately blocks trial execution before any encoder, training, or chat execution can occur.

---

## 3. Behavioral Invariant Matrix: Success vs. Failure

| Scenario | Subprocess State | Observed Diff Result | Provenance Status | Preflight Action |
|---|---|---|---|---|
| **Clean / No Drift** | `rc = 0, stdout = ""` | `[]` | Clean / Valid | Allowed |
| **Command Failure (Empty Stdout)** | `rc = 128, stdout = ""` | `["ERROR: ..."]` | Invalid (`provenance_errors`) | **BLOCKED** |
| **Command Failure (Partial Stdout)** | `rc = 1, stdout = "dgca/..."` | `["ERROR: ..."]` | Invalid (`provenance_errors`) | **BLOCKED** |
| **Command Failure (Stderr Present)** | `rc = 128, stderr = "fatal..."` | `["ERROR: ... (fatal...)"]`| Invalid (`provenance_errors`) | **BLOCKED** |
| **Status Command Failure** | `rc != 0` on `status` | `dirty_entries = ["ERROR: ..."]`| `working_tree_clean_at_start = False` | **BLOCKED** |

---

## 4. Verification Suite (C02-T01 to C02-T09)

Implemented in `tests/test_sctt00_harness.py`:
- **`C02-T01`**: `test_c02_t01_baseline_to_anchor_git_diff_nonzero_blocks` — PASS
- **`C02-T02`**: `test_c02_t02_anchor_to_execution_git_diff_nonzero_blocks` — PASS
- **`C02-T03`**: `test_c02_t03_anchor_to_working_tree_git_diff_nonzero_blocks` — PASS
- **`C02-T04`**: `test_c02_t04_nonzero_git_diff_with_empty_stdout_cannot_become_empty_list` — PASS
- **`C02-T05`**: `test_c02_t05_nonzero_git_diff_with_partial_stdout_still_blocked` — PASS
- **`C02-T06`**: `test_c02_t06_successful_git_diff_with_empty_stdout_remains_valid_empty_diff` — PASS
- **`C02-T07`**: `test_c02_t07_stderr_error_detail_is_retained_for_diagnostics` — PASS
- **`C02-T08`**: `test_c02_t08_ordinary_current_ric02_head_blocks_sctt_preflight` — PASS
- **`C02-T09`**: `test_c02_t09_historical_committed_sctt_artifacts_remain_untouched` — PASS

---

## 5. Architectural Verdict

**Final Status:** `RIC02_C02_VERIFIED`  
*(Pending final formal system closure gate)*
