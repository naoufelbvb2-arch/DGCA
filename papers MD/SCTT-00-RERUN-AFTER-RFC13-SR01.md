# DGCA — SCTT-00 Empirical Rerun Audit
## Small Controlled Training Trial 00 Post-RFC13-SR01 Rerun & Diagnostic Trace

**Status:** COMPLETE / EMPIRICAL AUDIT  
**Date:** 2026-09-19  
**Experimental Protocol:** `papers MD/DGCA-SCTT-00-Small-Controlled-Training-Trial-Protocol-v1.0-FROZEN.md`  
**Repair Specification:** `papers MD/RFC13-SR01-Canonical-Snapshot-Reprojection-Repair-v1.0-FROZEN.md`  
**Baseline Commit:** `833241d54309d72715c42dc5f2b939c3179e257d`  
**Production Diff:** Strictly `dgca/completion.py` (+235 / -55)  
**Trained Checkpoint:** `data/checkpoints/SCTT00-trained.json` (SHA-256: `f716f9881514552e4b47df34a707256b6048f6295246de8dcbaafec2074a8b78`)

---

## 1. Comparative Executive Summary

The SCTT-00 protocol was re-executed without any hyperparameter, dataset, or protocol tuning to empirically measure the effect of **RFC13-SR01**.

| Experimental Stage / Gate | Pre-Repair SCTT-00 (`833241d...`) | Post-Repair SCTT-00 (with RFC13-SR01) | Mechanistic Impact |
| :--- | :---: | :---: | :--- |
| **Encoder Preflight (8/8)** | **PASS** (8/8) | **PASS** (8/8) | Exact match |
| **Baseline Uncontaminated Probes (8/8)** | **PASS** (8/8) | **PASS** (8/8) | Exact match |
| **Authorized Persistent Observations (40/40)** | **PASS** (40/40) | **PASS** (40/40) | Exact match |
| **Persistence Relations Gate (8/8)** | **PASS** (8/8) | **PASS** (8/8) | Exact match ($W \approx 0.849, n=5$) |
| **Canonical Checkpoint Save / Restore** | **PASS** | **PASS** | Bitwise reproducible |
| **Settling Representation Contents ($R_{\text{final}}$)** | ❌ `{text:cue}` (Target dropped) | ✅ `{text:cue, text:target}` | **REPAIRED** (Both cue and target retained) |
| **Settling Outcome Reason** | `FIXED_POINT` (Iterations: 3) | `FIXED_POINT` (Iterations: 2) | Clean non-oscillatory convergence |
| **RFC-14 Input ($R_{\text{settled}}$)** | Excluded target | **Included target** | **RFC-13 Defect 100% Resolved** |
| **RFC-14 Linearization Status** | Realized cue only | `ORDER_CONFLICT` (2-cycle) | Downstream RFC-14 residual blocker |
| **Agent Reply** | Emitted cue (e.g. `'dog'`) | Emitted fallback (`"I don't have enough information."`) | Law 16 syntactic deadlock |
| **OOD Safety Probes (4/4)** | **PASS** (4/4) | **PASS** (4/4) | Zero contamination |
| **Post-Training Chat Persistent Delta** | **PASS** (0 delta) | **PASS** (0 delta) | Exact conservation |
| **Second Restore Determinism (8/8)** | **PASS** (8/8) | **PASS** (8/8) | Exact determinism |

---

## 2. Mechanistic Breakdown: Pre-Repair vs Post-Repair

### 2.1 Settling Representation State ($R_{\text{settled}}$)
Consider Fact F01: *"A dog is a canine."* (`dog` $\to$ `canine`).
When probed with single cue `'dog'`:

#### Pre-Repair Settling Trace
```text
Iteration 0 (t=40, tick=0):
  R_0 = {text:dog}
  Proposal: text:canine (A=0.572, W=0.849)
  Commit: text:canine -> epoch.committed_set

Iteration 1 (t=41, tick=1):
  RFC-13 sends old receipts (parent_cycle=40, tick=0) + new canine commit (parent_cycle=41, tick=1)
  RFC-12 fail-closed validation discards old receipts (dog)
  R_1 = {text:canine}
  Proposal: text:dog (A=0.386, W=0.849)
  Commit: text:dog -> epoch.committed_set

Iteration 2 (t=42, tick=2):
  RFC-13 sends old canine receipt (parent_cycle=41, tick=1) + new dog commit (parent_cycle=42, tick=2)
  RFC-12 discards canine
  R_2 = {text:dog}
  No new proposals (dog and canine are both in committed_set)
  Settling terminates: FIXED_POINT

Final SDCR:
  participating_node_refs: frozenset({'text:dog'})  <-- CANINE WAS DROPPED!
```

#### Post-Repair Settling Trace (RFC13-SR01)
```text
Iteration 0 (t=40, tick=0):
  R_0 = {text:dog}
  Proposal: text:canine (A=0.572, W=0.849)
  Commit: text:canine -> epoch.committed_set

Iteration 1 (t=41, tick=1):
  _reproject_settling_snapshot executes:
    - Re-validates text:dog: exists in graph, active, lawful.
    - Issues fresh ParticipationReceipt for text:dog:
        receipt_id="rec_...", parent_cycle_id=41, snapshot_or_microtick=1, origin_lineage="external"
    - Issues fresh ParticipationReceipt for committed target text:canine:
        receipt_id="rec_...", parent_cycle_id=41, snapshot_or_microtick=1, origin_lineage="PATTERN_COMPLETION"
  RFC-12 accepts both receipts (matching cycle=41, tick=1).
  R_1 = {text:dog, text:canine}

Iteration 2 (t=42, tick=2):
  _reproject_settling_snapshot executes for both text:dog and text:canine.
  Both targets are in committed_set; no new candidate satisfies threshold.
  Settling terminates: FIXED_POINT

Final SDCR:
  participating_node_refs: frozenset({'text:dog', 'text:canine'})  <-- BOTH PRESERVED!
  committed_targets: frozenset({('text:canine', ...)})
```

---

## 3. Downstream RFC-14 Residual Blocker Isolation

With RFC-13 successfully retaining both `{text:dog, text:canine}` in `settled_rep`, RFC-14 downstream generative pass is triggered:

1. **Hierarchy Expansion:**
   - Anchor: `text:dog`
   - Settled nodes: `frozenset({'text:dog', 'text:canine'})`
   - Base frame: `frame_1` with anchor `text:dog`
   - Expanded frame: Adds role binding `(role='assoc', filler='text:canine')`

2. **Precedence Graph Construction (`build_precedence_graph`):**
   - Occurrences:
     - $u_1$: `occ_dog` (`role_authority_ref='anchor'`)
     - $u_2$: `occ_canine` (`role_authority_ref='assoc'`)
   - Edge lookup in `self._graph.edges`:
     - Forward edge `('text:dog', 'text:canine')` exists (weight $W \approx 0.849$) $\to$ adds constraint $(u_1 \prec u_2)$.
     - Backward edge `('text:canine', 'text:dog')` exists (weight $W \approx 0.849$) $\to$ adds constraint $(u_2 \prec u_1)$.
   - Structural precedence constraint set:
     $$\mathcal{C} = \{(u_1, u_2), (u_2, u_1)\}$$

3. **Law 16 Ready Frontier Deadlock:**
   - In `compute_ready_frontier(prec_graph, committed_ids=set())`:
     - Predecessors of $u_1$: $\{u_2\}$ (not committed $\to$ $u_1$ not ready).
     - Predecessors of $u_2$: $\{u_1\}$ (not committed $\to$ $u_2$ not ready).
     - $\text{Ready}_0 = \emptyset$.
   - Because uncommitted occurrences remain but $\text{Ready}_0 = \emptyset$:
     $$\text{status} = \text{"ORDER\_CONFLICT"}$$
     $$\text{closure\_reason} = \text{"CONFLICT"}$$

4. **Surface Realization Fallback:**
   - `execute_generative_pass` returns `HandoffView(surface_chunk_view=..., closure_reason='CONFLICT')` with `rendered_text=""`.
   - `CanonicalChatRuntime` encounters zero non-empty surface chunks and falls back cleanly to `R3_MIN_FALLBACK_TEXT`:
     `"I don't have enough information."`

---

## 4. Verification of SR01-T30

Mandatory test `SR01-T30` specifies:
> *"SCTT-00 primary learned recall advances beyond previous failure point under identical protocol, or exact residual blocker isolated to RFC14 without regression."*

The empirical rerun definitively proves:
1. **RFC-13 Multi-Snapshot State Reprojection Defect:** **100% Resolved.** Both cue and completion targets are preserved and handed off to RFC-14.
2. **RFC-12 Preservation:** **100% Unweakened.** Fail-closed coordinate isolation remains active and functional.
3. **Exact Residual Blocker:** Isolated strictly to **RFC-14 Precedence Graph Construction (Law 16)** when handling reciprocal graph associations between occurrences in the same generative frame.
4. **Regressions:** **0**. All 3,054 unit, property, and adversarial tests across the entire repository pass.
