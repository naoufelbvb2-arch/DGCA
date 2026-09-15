# DGCA — RIC-01 / R3 Minimal
## Adversarial Freeze Review v1.0

**Review target:**  
`RIC-01-R3-Minimal-Canonical-User-Runtime-Formal-Architecture-Specification-v1.0-CANDIDATE.md`

**Repository baseline:**  
`c04c0820ef3cb329008a6bc7be0d9c4fd8754403`

**Review mode:** STRICT READ-ONLY / ADVERSARIAL  
**Production code modified:** NO  
**RFC-15:** DEFERRED  
**New cognitive law:** NONE

---

# 1. Review Objective

Attack the candidate R3-Min architecture for loopholes that could produce a superficially working `chat()` while violating the closed R0/R1/R2 contracts.

Primary attack targets:

```text
persistent N_total drift during RFC13 completion
activation rollback disguised as non-learning
second external ingress through RFC16
legacy LinearizationEngine fallback
hidden keyword/mode routing
unbounded or implementation-defined budgets
ambiguous activation-scope lifetime
unsafe raw-graph exposure
non-deterministic fresh boot
restore-time prediction drift
legacy-agent regression laundering
multi-MicroEpisode reordering/merging
active SDCR leakage
exception-path lifecycle leakage
session identity derived from content
ordinary-user persistence capability leakage
RFC15 accidental invocation
```

---

# 2. Source-Grounded Findings

The review reconfirmed:

- `Node.excite()` modifies `A`, `t_spawn`, `episode`, and increments durable `N_total` for positive activation.
- Canonical persistence includes `N_total`, while `A`, `t_spawn`, and `episode` are restored as transient values on canonical restore.
- RFC13 currently has one production `node_obj.excite(...)` reinstatement write site inside Law-15 settling.
- RFC13 canonical settling already accepts `root_authority_ref`, `work_ref`, and `canonical_identity`.
- RFC14 `execute_generative_pass()` already supports a bounded `budget`, `language_context`, and `canonical_identity`.
- R2 result owns its original SDCRs and has an idempotent close lifecycle.
- `CanonicalR1RuntimeRoot.create_observation_bridge()` already demonstrates the lawful trusted-internal pattern of binding a private graph to a canonical subsystem without exposing it to ordinary callers.

These facts support a narrow R3 runtime seam rather than a cognitive redesign.

---

# 3. AFR-B01 — Budget Semantics Were Under-Specified

## Attack

The candidate said RFC13 should use the existing bounded budget and RFC14 should use the existing bounded default, but did not freeze exact values.

Two implementations could therefore claim R3-Min conformance while producing different retrieval/generation behavior merely by choosing different budgets.

## Resolution

Freeze:

```text
RFC13 completion budget = Law.E_BUDGET_0
RFC14 generation budget = 1.0
```

These are existing subsystem authorities/defaults; no new parameter is introduced.

**Result:** BLOCKER CLOSED BY v1.1 AMENDMENT.

---

# 4. AFR-B02 — Activation Scope Lifetime Was Ambiguous

## Attack

Candidate §17 said transient node fields restore when RFC13 returns/raises.

Candidate §27 could be read as restoring activation only during turn-final cleanup after RFC14.

Those are not equivalent.

Keeping scoped graph activation alive during RFC14 would silently expand the transient authority surface beyond the RFC13 owner.

## Resolution

Freeze exact lifetime:

```text
enter TransientActivationScope
    run RFC13 only
exit scope
    restore A/t_spawn/episode exactly
then run RFC14 from the settled SDCR receipts/state
```

Thus RFC14 receives the settled SDCR but not RFC13's temporary graph-field projection.

**Result:** BLOCKER CLOSED BY v1.1 AMENDMENT.

---

# 5. AFR-B03 — Activation Sink Authority Was Too Broad

## Attack

A generic callback/sink could be implemented to:
- create nodes;
- mutate N_total;
- modify edges;
- write contradictions;
- mutate arbitrary graph fields.

That would turn the proposed isolation seam into a new mutation backdoor.

## Resolution

Freeze a narrow interface conceptually equivalent to:

```python
class CompletionActivationSink(Protocol):
    def excite_existing_node(
        self,
        node_id: str,
        *,
        t: int,
        value: float,
        episode: str | None = None,
    ) -> None: ...
```

R3 implementation rules:

```text
existing nodes only
A/t_spawn/episode only
N_total unchanged
no Node creation
no Edge write
no graph.t write
no X/assembly/ledger write
unknown node -> fail closed
closed scope -> fail closed
first-touch snapshot only
finally restoration mandatory
```

RFC13 default path with `activation_sink=None` remains byte-behavior compatible with the frozen RFC13 legacy/default execution.

**Result:** BLOCKER CLOSED BY v1.1 AMENDMENT.

---

# 6. AFR-B04 — Fresh Boot Was Not Deterministic Enough

## Attack

Candidate fresh boot said the quantity backbone should be initialized "if it remains part of the default model."

That allows two conforming implementations with different intrinsic cognitive starting states.

## Resolution

The legacy canonical product behavior already treats the quantity backbone as intrinsic bootstrap state.

Freeze:

```text
fresh R3-Min CognitiveAgent MUST initialize quantity backbone
before R1 native provenance epoch/state digest creation.
```

Also freeze:

```text
fresh graph enable_prediction = False
```

**Result:** BLOCKER CLOSED BY v1.1 AMENDMENT.

---

# 7. AFR-B05 — Restore-Time Prediction Policy Was Ambiguous

## Attack

Fresh boot disabled prediction, but checkpoint restore did not explicitly freeze the runtime prediction configuration.

A restored chat agent could therefore run a different side path from a fresh agent.

## Resolution

Freeze canonical restore call with:

```text
expected_observation_protocol_version = "R2-OBS-1.0"
enable_prediction = False
```

Prediction is deferred from R3-Min.

**Result:** BLOCKER CLOSED BY v1.1 AMENDMENT.

---

# 8. AFR-B06 — Legacy Compatibility Escape Was Too Open

## Attack

The candidate regression gate allowed "tests intentionally migrated from old CognitiveAgent."

Without a conservation rule, this could be used to delete old behavior or weaken tests until the new API passes.

## Resolution

Freeze:

```text
old RFC09 implementation, if retained, moves to explicit
LegacyCognitiveAgent compatibility ownership.

Top-level dgca.CognitiveAgent becomes canonical R3-Min.

Legacy behavior must not be semantically rewritten merely to make R3 pass.
Regression tests that depend on RFC09 behavior must point explicitly to
LegacyCognitiveAgent rather than being weakened/deleted.
```

Canonical REPL never imports the legacy class.

**Result:** BLOCKER CLOSED BY v1.1 AMENDMENT.

---

# 9. AFR-B07 — R3 Semantics Fingerprint Needed Exact Freeze

The candidate registry/digest was internally correct, but freeze review added the resolved policies above.

The final v1.1 registry has exactly **32** top-level entries.

Canonical hashing rule:

```python
hashlib.sha256(
    json.dumps(
        registry,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
).hexdigest()
```

Final frozen R3-Min semantics digest:

```text
fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc
```

No calibration, XOR, or short-circuit is authorized.

**Result:** CLOSED.

---

# 10. Transient Activation Isolation Attack Review

The proposed design survives the important attacks:

### Attack A — positive reinstatement increments durable N_total

Prevented because R3 sink does not call normal `Node.excite()`.

### Attack B — increment N_total and restore it afterward

Explicitly forbidden. Unauthorized durable mutation must never occur.

### Attack C — detached overlay invisible to Law15

Rejected. Scoped `Node.A` is projected to the live transient field during RFC13 so inhibition and iterative settling observe it.

### Attack D — activation survives into RFC14

Rejected by the now-frozen RFC13-call-only scope lifetime.

### Attack E — exception leaves activation dirty

First-touch snapshots restore in `finally`.

### Attack F — sink becomes raw-graph escape

Rejected by the narrow existing-node/transient-field-only contract and private runtime ownership.

**Verdict:** PASS.

---

# 11. One-Ingress Authority Review

R3-Min freezes:

```text
one chat call
→ one host occurrence
→ one R2 observe_text()
```

It explicitly forbids:
- RFC16 full-loop external ingress;
- content-derived Root identity;
- legacy perceive/feed ingress.

Identical text in distinct turns has distinct occurrence authority.

**Verdict:** PASS.

---

# 12. Multi-MicroEpisode Review

The candidate processes every observable R2 child in canonical child order and never creates a synthetic merged representation.

This preserves R2 identity boundaries while still allowing a simple turn-level string join.

**Verdict:** PASS.

---

# 13. RFC14 Surface Review

The only cognitive text surface remains:

```text
SurfaceChunk.rendered_text
```

R3 adds no semantic template, punctuation rewrite, or legacy linearizer fallback.

The fixed fallback is used only when no child emits non-empty generated text.

**Verdict:** PASS.

---

# 14. RFC15 Deferral Review

RFC15 is absent from the minimal execution path.

This is architecturally safe because RFC14 already produces a bounded surface chunk.

Deferring recurrence reduces integration variables during the first real model interaction.

**Verdict:** PASS.

---

# 15. Runtime Encapsulation Review

A new `CanonicalR1RuntimeRoot.create_chat_runtime()` may bind the private graph internally in the same trusted pattern already used by `create_observation_bridge()`.

Hard requirement:

```text
CanonicalChatRuntime and CognitiveAgent expose no raw mutable graph.
```

No call to `unsafe_mutable_graph()` is permitted.

**Verdict:** PASS.

---

# 16. Failure/Lifecycle Review

Single-active-turn ownership plus `finally` cleanup gives deterministic failure handling.

Required exact order after child processing/failure:

```text
RFC13 scope already restored before RFC14
close RFC13-derived SDCRs
close R2 observation result
turn state -> IDLE
```

Unexpected internal exceptions may propagate as Python errors; they must not be converted into fabricated semantic answers.

**Verdict:** PASS.

---

# 17. Remaining Non-Blocking Engineering Debt

These are intentionally deferred and are not R3-Min freeze blockers:

```text
closed_representations diagnostic retention may grow over long sessions
generation/retrieval quality is unknown until empirical chat trials
fresh untrained agent may frequently return fallback
RFC15 is required later for longer continuation
RFC16 needs future R2-native handoff integration
Text Encoder robustness audit remains later work
```

None requires widening R3-Min now.

---

# 18. Final Freeze Verdict

After applying AFR-B01 through AFR-B07:

```text
==========================================================
DGCA — RIC-01 / R3 MINIMAL
ADVERSARIAL FREEZE REVIEW v1.0

R0 CONSERVATION:
PASS

R1 CAUSAL AUTHORITY:
PASS

R2 SOLE INGRESS AUTHORITY:
PASS

OBSERVATION/LEARNING SEPARATION:
PASS

RFC13 TRANSIENT ACTIVATION ISOLATION:
PASS

LAW15 SEMANTICS CONSERVATION:
PASS

RFC14 SURFACE AUTHORITY:
PASS

RFC15 DEFERRAL:
PASS

RFC16 SECOND-INGRESS FIREWALL:
PASS

LEGACY LINEARIZER FIREWALL:
PASS

MULTI-MICROEPISODE ORDERING:
PASS

TRANSIENT LIFECYCLE:
PASS

FRESH/RESTORE RUNTIME DETERMINISM:
PASS

LEGACY COMPATIBILITY GOVERNANCE:
PASS

NEW COGNITIVE LAW:
NO

FREEZE BLOCKERS:
0

FORMAL ARCHITECTURE v1.1:
AUTHORIZED TO FREEZE

IMPLEMENTATION:
NOT YET AUTHORIZED
==========================================================
```

Formal freeze target:

```text
RIC-01 / R3 Minimal
Minimal Canonical User Runtime
Formal Architecture Specification v1.1 — FROZEN
```
