# DGCA — RIC-01 / R1-PIR-02
## Final Independent Closure Audit v1.0

**Implementation commit:** `11d255d44abee245b533945027419d1bca2f47d4`
**Repair base:** `bf764033dbbeec59c507e0f137d2fbbb513582e1`
**Audit mode:** Independent read-only source audit
**R2 authorization:** NO

# Executive verdict

PIR-02 materially closes the nine previously identified integration defects, but three frozen closure requirements remain violated in committed source.

```text
RIC01_R1_PIR02_FINAL_AUDIT_FAILED
R1 = OPEN
R2 = NOT AUTHORIZED
remaining closure blockers = 3
fatal cognitive-law defects = 0
```

# PIR03-B01 — Safe canonical inspection is still not actually detached

`CanonicalR1RuntimeRoot.graph` returns raw `_graph` whenever `_in_command` is true.

`CognitiveGraphInspectionView` still exposes live `_assembly_manager` and RFC12–RFC16 engine objects via underscore properties.

Node/Edge projections use `copy.copy()`, which leaves nested mutable state shared:
- `Node.members`
- `Edge.contexts`
- `Edge.ctx_hits`

`CausalLedgerInspectionView` still exposes the mutating `commit_transaction()` method.

This violates the frozen PIR-02 contract that the public safe inspection surface is detached/non-live at all times, including during canonical mutation execution.

# PIR03-B02 — Provenance epoch identity is silently repaired

`CausalProvenanceEpoch.__post_init__()` recomputes a mismatching `epoch_id` and writes it back via `object.__setattr__`.

The frozen PIR-02 contract requires arbitrary/mismatching canonical epoch IDs to fail closed on canonical construction/restore, not be silently normalized.

The current PIR-02 test suite explicitly expects recomputation, so the frozen rule is not tested correctly.

# PIR03-B03 — Transaction-ID restore validation accepts arbitrary prefixes

`validate_causal_provenance_state()` strips everything before the first underscore in `transaction_id`, then validates only the remaining 64 lowercase hex characters.

Canonical committed TxIDs are stored without an arbitrary prefix. A value such as:

```text
evil_<64 lowercase hex>
```

can therefore pass the shape validator.

Frozen PIR-02 requires exact canonical authoritative form.

# Accepted PIR-02 repairs

Independent source review confirms the following improvements:

```text
ExpressiveObligation uses INTERNAL_WORK
literal domain registry unchanged
protocol digest unchanged
RFC13 cache mode separation
RFC14 frame re-ID path
RFC15 canonical progress digest repair
canonical GCE authority hardening
RFC16 canonical DeliveryID integration
pre-mutation event digest validation
pre-save provenance validation
migration disclosure-chain accumulation
directory-fsync resource hardening
```

# Verification evidence note

The implementation report states:

```text
44/44 PIR-02 PASS
136/136 R1 PASS
2730/2730 repository PASS
Ruff PASS
baseline = 915119d40643cb97
```

These reported local results are not disputed. GitHub exposes no commit-status checks or workflow runs for this commit. The three residual blockers are visible directly in source.

# Closure requirement

A narrow `R1-PIR-03` repair is sufficient. No R1 redesign is required.

R1 may close only after:
- public `runtime.graph` never becomes raw during command execution;
- Node/Edge nested mutable state is detached;
- safe graph inspection exposes no live manager/engines;
- safe ledger inspection exposes no mutation method;
- arbitrary canonical epoch IDs fail closed;
- transaction IDs require exact canonical lowercase-64-hex shape;
- all prior R1/R0 regressions pass;
- baseline remains `915119d40643cb97`;
- protocol digest remains unchanged;
- R2 remains unstarted.
