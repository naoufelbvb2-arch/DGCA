# DGCA — RIC-01 / R3 Minimal
## Post-Implementation Independent Audit v1.0

**Audited implementation commit:** `11350944c6b662e1546afde73da903e9974d645c`  
**Immediate parent commit:** `462d102876eb68600bfa8e35fcdcfe31d987258a`  
**Architectural baseline:** `c04c0820ef3cb329008a6bc7be0d9c4fd8754403`  
**Authoritative architecture:** `papers MD/RIC-01-R3-Minimal-Canonical-User-Runtime-Formal-Architecture-Specification-v1.1-FROZEN.md`  
**Audit mode:** independent / read-only  
**Repository mutation by auditor:** none  
**RFC-15:** deferred  
**R3-Min closure:** not yet authorized

---

# 1. Executive Verdict

The R3-Min implementation is substantially correct and the canonical runtime path is real:

```text
CognitiveAgent.chat()
→ R2 TRANSIENT_ONLY
→ RFC13 with scoped transient activation
→ restore transient node activation
→ RFC14 bounded generation
→ SurfaceChunk.rendered_text
→ deterministic cleanup
```

The source audit confirms the major architectural goals:
- R2 is the sole external ingress for ordinary chat;
- RFC13 default behavior is preserved behind an optional activation sink;
- R3 transient completion does not call `Node.excite()` and does not increment `N_total`;
- activation is restored before RFC14;
- RFC15 is not part of the chat path;
- RFC16 full-loop ingress is not part of the chat path;
- legacy LinearizationEngine is not the response generator;
- R2/RFC13 representations are cleaned up;
- the new canonical `CognitiveAgent` is a thin façade;
- the old RFC09 behavior is preserved as `LegacyCognitiveAgent`.

However, R3-Min cannot be closed yet.

The independent audit found **two release blockers** and one report-lineage correction:

```text
R3MIN-PIR01-B01
Public host/runtime authority leakage:
CognitiveAgent publicly exposes enable_prediction and session_nonce.

R3MIN-PIR01-B02
Verification artifact contradicts the frozen/implemented R3 semantics registry
and misstates several implementation facts.

R3MIN-PIR01-D01
The report names c04c0820... as "Base Commit" even though the immediate
implementation parent is 462d102... after the user’s docs-only repo reorganization.
```

No new cognitive-law defect was found.

Final audit verdict:

```text
RIC01_R3_MIN_POST_IMPLEMENTATION_AUDIT_FAILED
R3_MIN_REMAINS_OPEN
R3_MIN_PIR01_REQUIRED
RFC15_REMAINS_DEFERRED
```

---

# 2. Commit / Scope Audit

Git history is:

```text
c04c0820ef3cb329008a6bc7be0d9c4fd8754403
RIC-01/R2-PIR-04: close exact frozen acceptance ledger evidence

462d102876eb68600bfa8e35fcdcfe31d987258a
docs: reorganize project papers, specifications, and forensic data into papers MD/

11350944c6b662e1546afde73da903e9974d645c
RIC-01/R3-Min: implement minimal canonical user runtime
```

Thus:
- `c04c0820...` is the correct architectural/production baseline;
- `462d102...` is the immediate implementation parent;
- the intermediate commit is documentation/data reorganization, not production cognitive change.

Comparing `462d102...` to `11350944...` gives the expected narrow R3 implementation scope:
- `dgca/chat_runtime.py` added;
- `dgca/legacy_agent.py` added;
- `dgca/agent.py` rewritten;
- narrow changes to `dgca/completion.py`, `dgca/causal_identity.py`, `dgca/__init__.py`;
- canonical REPL rewrite;
- one legacy RFC09 test import migration;
- R3-Min verification suite;
- implementation reports.

**Scope verdict:** PASS.

---

# 3. Confirmed Correct Production Work

## 3.1 Exact R3 semantics registry in production

`dgca/chat_runtime.py` contains the frozen 32-entry v1.1 registry, including:

```text
activation_scope_lifetime
activation_sink_contract
anchor_policy
checkpoint_restore
chunk_policy
completion_activation_mode
completion_budget
completion_canonical_identity
completion_owner
external_ingress_count_per_turn
fallback_text
fresh_bootstrap
fresh_prediction_policy
generation_budget
generation_canonical_identity
generation_owner
ingress_owner
language_context
learning_api
legacy_compatibility
legacy_linearizer_policy
loop_policy
multi_microepisode_policy
observation_mode
occurrence_policy
protocol_version
public_api
recurrent_policy
restore_prediction_policy
supported_modalities
transient_cleanup_policy
turn_concurrency
```

The implementation computes direct canonical SHA-256.

Expected and implemented digest:

```text
fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc
```

No XOR calibration or expected-value short circuit is present.

**Verdict:** PASS.

## 3.2 TransientActivationScope

The implementation:
- snapshots `(A, t_spawn, episode)` on first touch;
- writes only `A`, `t_spawn`, and `episode`;
- does not call `Node.excite()`;
- does not modify `N_total`;
- rejects unknown nodes;
- restores exact first-touch values;
- closes against reuse.

**Verdict:** PASS.

## 3.3 RFC13 seam

`PatternCompletionEngine.run_settling_epoch()` gained only:

```text
activation_sink: CompletionActivationSink | None = None
```

Accepted reinstatement:
- uses the sink when supplied;
- falls back to the original `node_obj.excite(...)` when not supplied.

This preserves the legacy/default RFC13 path.

**Verdict:** PASS.

## 3.4 CanonicalChatRuntime causal path

The source implements:
- one R2 `observe_text()` call per turn;
- `ExecutionMode.TRANSIENT_ONLY`;
- no capability / no persistent transaction;
- child ordering by `child_index`;
- anchors from positive external node receipts;
- canonical RFC13 InternalWorkID;
- RFC13 budget `Law.E_BUDGET_0`;
- transient activation restoration before RFC14;
- RFC14 budget `1.0`;
- `language_context="en"`;
- canonical RFC14 identities;
- exact `SurfaceChunk.rendered_text`;
- one-space chunk joining;
- exact fixed fallback;
- RFC13-derived representation cleanup;
- R2 result cleanup in outer `finally`;
- lifecycle return to IDLE.

**Verdict:** PASS.

## 3.5 Legacy / deferred-system firewalls

The canonical REPL routes ordinary text only through `agent.chat()`.

No `/learn`, `/ask`, `/code`, `/analogy`, or `/compare` routing exists.

The canonical chat runtime has no RFC15 or RFC16 full-loop call.

Legacy RFC09 behavior is moved to explicit `LegacyCognitiveAgent`.

**Verdict:** PASS.

---

# 4. R3MIN-PIR01-B01 — Public Runtime Authority Leakage

## Severity

`HIGH — FROZEN PUBLIC CONTRACT / CAUSAL HOST AUTHORITY`

The frozen v1.1 architecture requires fresh ordinary construction to be:

```python
CognitiveAgent()
```

with:

```text
CognitiveGraph(enable_prediction=False)
```

and says deterministic fixed session-nonce injection is only an internal/developer test hook.

The implemented public constructor is:

```python
CognitiveAgent(
    *,
    enable_prediction: bool = False,
    session_nonce: str | None = None,
)
```

and uses:

```python
graph = CognitiveGraph(enable_prediction=enable_prediction)
```

The public `from_checkpoint()` also accepts:

```python
session_nonce: str | None = None
```

This creates two public authority leaks.

---

## 4.1 Prediction policy can be overridden by ordinary caller

A normal caller can execute:

```python
agent = CognitiveAgent(enable_prediction=True)
```

This violates frozen invariant:

```text
R3-I33
fresh and restored R3-Min prediction side path is disabled.
```

The fact that the default is False is insufficient; the frozen contract says ordinary R3-Min does not expose that runtime-mode choice.

---

## 4.2 Host occurrence authority can be supplied by ordinary caller

A normal caller can execute:

```python
agent = CognitiveAgent(session_nonce="a" * 32)
```

or:

```python
CognitiveAgent.from_checkpoint(path, session_nonce="a" * 32)
```

The R3-Min freeze review specifically classified session nonce as:
- host-controlled;
- non-cognitive;
- not user-controlled;
- deterministic injection allowed only by a private/internal test hook.

The current public API lets ordinary callers choose a component of RootExternalEpisode occurrence authority.

That is not a persistent-learning capability, but it violates the frozen host/causal boundary.

---

## 4.3 The tests normalize the violation

Current C05 evidence creates:

```python
CognitiveAgent(session_nonce=fixed_nonce)
```

twice to test deterministic Root identity.

Therefore the suite does not merely miss the violation; it uses the forbidden public hook as its accepted test mechanism.

No acceptance test verifies:

```text
CognitiveAgent(enable_prediction=True) -> TypeError / impossible public API
CognitiveAgent(session_nonce=...) -> TypeError / impossible public API
CognitiveAgent.from_checkpoint(..., session_nonce=...) -> TypeError / impossible public API
```

---

## Required repair

Canonical public signatures must become:

```python
CognitiveAgent()
CognitiveAgent.from_checkpoint(filepath)
```

No `enable_prediction`.

No `session_nonce`.

Fresh boot must hard-code:

```python
CognitiveGraph(enable_prediction=False)
```

Restore must continue hard-coding:

```text
enable_prediction=False
```

Deterministic tests may use a clearly private/internal construction seam, e.g.:

```python
CognitiveAgent._for_test(session_nonce=...)
```

or a private `CanonicalChatRuntime` test factory.

That seam must not appear as an ordinary public constructor parameter.

---

# 5. R3MIN-PIR01-B02 — Verification Report Contradicts Frozen/Implemented Semantics

## Severity

`HIGH — RELEASE EVIDENCE / ARCHITECTURAL TRACEABILITY`

The production `dgca/chat_runtime.py` registry is correct.

The frozen v1.1 architecture registry is correct.

But `RIC-01-R3-MIN-IMPLEMENTATION-VERIFICATION-REPORT.md` claims that the “exact 32-entry semantics registry” is a different dictionary.

The report lists keys such as:

```text
allow_prompt_authority
anchor_source
causal_epoch_mutation_on_chat
checkpoint_schema_version
completion_creates_learning_evidence
completion_scope_restores_node_a
deterministic_ordering
empty_generation_fallback
generation_surface
learning_method_exposed
...
```

Those are not the frozen R3-Min registry.

The authoritative frozen/implemented registry instead begins:

```text
activation_scope_lifetime
activation_sink_contract
anchor_policy
checkpoint_restore
chunk_policy
completion_activation_mode
completion_budget
...
```

Thus the verification artifact currently contains two incompatible claims simultaneously:

```text
"exact frozen registry digest MATCH"
```

and:

```text
a different 32-key registry literal
```

The code is correct; the report is wrong.

---

## 5.1 Additional report implementation mismatches

The report also says `TransientActivationScope` does:

```text
node.A = max(node.A, value)
```

but production code does:

```text
node.A = min(Law.C_MAX, value)
```

The production code matches the frozen architecture.

The report also describes Root derivation through a helper/path that is not what `CanonicalChatRuntime` actually does; production correctly supplies the trusted boundary/source occurrence data to the R2 bridge.

These are documentation/evidence defects, not runtime defects.

---

## 5.2 Exact-registry evidence should be strengthened

The test currently proves:
- entry count is 32;
- computed digest matches the frozen digest;
- mutating a copied registry changes the digest.

That is strong cryptographic evidence and the current production registry is correct.

However, after the R2 evidence-history, the final repair should also embed the exact frozen registry literal in the verification test and assert direct dictionary equality.

This makes the release artifact self-checking instead of relying only on a digest constant.

---

## Required repair

Correct both verification-report copies so their registry section is the exact frozen 32-entry registry.

Correct all implementation descriptions to match source.

Add a static exact-registry equality test.

Do not change the correct production registry.

---

# 6. R3MIN-PIR01-D01 — Implementation Parent / Architectural Baseline Distinction

The report says:

```text
Base Commit: c04c0820...
```

That SHA is the architectural/production baseline.

But the actual immediate parent of the implementation commit is:

```text
462d102876eb68600bfa8e35fcdcfe31d987258a
```

which is the user’s documentation-only repo reorganization commit.

The corrected report should state both:

```text
Architectural / production baseline:
c04c0820ef3cb329008a6bc7be0d9c4fd8754403

Immediate implementation parent:
462d102876eb68600bfa8e35fcdcfe31d987258a
```

This is not an R3 runtime blocker by itself, but it matters for future exact-diff audits.

---

# 7. CI Qualification

The audited final commit has:
- no combined GitHub status checks;
- no associated GitHub Actions workflow runs.

Therefore:

```text
2987 passed
Ruff clean
```

are committed local verification evidence, not independently observed CI evidence.

This does not imply they are false.

It only limits what the independent audit can claim.

---

# 8. PIR-01 Repair Gates

Required gates:

```text
PIR01-G01  public CognitiveAgent constructor has no enable_prediction parameter
PIR01-G02  public CognitiveAgent constructor has no session_nonce parameter
PIR01-G03  public from_checkpoint has no session_nonce parameter
PIR01-G04  fresh graph always has enable_prediction=False
PIR01-G05  restored graph always has enable_prediction=False
PIR01-G06  deterministic test nonce injection exists only behind private/internal seam
PIR01-G07  ordinary user cannot choose host session nonce
PIR01-G08  two ordinary identical-text turns still produce distinct Roots
PIR01-G09  private fixed-nonce deterministic test still reproduces Root
PIR01-G10  exact frozen 32-entry registry dictionary equality test passes
PIR01-G11  direct R3 digest remains fc357c3b...
PIR01-G12  both implementation reports contain the exact frozen registry
PIR01-G13  reports correctly describe min(Law.C_MAX, value)
PIR01-G14  reports distinguish architectural baseline from immediate parent
PIR01-G15  all R3-I01..I42 remain passing
PIR01-G16  all A01..N08 remain passing
PIR01-G17  ADV-A..ADV-T remain passing
PIR01-G18  persistent payload/ledger/RFC11 deltas remain zero
PIR01-G19  RFC13 default behavioral signature unchanged
PIR01-G20  RFC14 behavioral signature unchanged
PIR01-G21  RFC15 zero-call proof remains
PIR01-G22  RFC16 full-loop zero-call proof remains
PIR01-G23  legacy linearizer zero-call proof remains
PIR01-G24  full R0/R1/R2 regression passes
PIR01-G25  full repository regression passes
PIR01-G26  Ruff passes
PIR01-G27  baseline/R1/R2/checkpoint constants unchanged
PIR01-G28  no RFC15/Audio/Vision/Text-Encoder work
```

---

# 9. Final Status

```text
==================================================
DGCA — RIC-01 / R3 MINIMAL
POST-IMPLEMENTATION INDEPENDENT AUDIT

IMPLEMENTATION SHA:
11350944c6b662e1546afde73da903e9974d645c

CORE CHAT PATH:
SUBSTANTIALLY VERIFIED

PRODUCTION COGNITIVE-LAW DEFECTS:
0

OPEN RELEASE BLOCKERS:
2

PUBLIC AUTHORITY BOUNDARY:
REPAIR REQUIRED

VERIFICATION ARTIFACT CONSISTENCY:
REPAIR REQUIRED

R3-MIN:
OPEN

RFC15:
DEFERRED

NEXT:
R3-MIN-PIR-01

FINAL VERDICT:
RIC01_R3_MIN_POST_IMPLEMENTATION_AUDIT_FAILED
==================================================
```
