# DGCA — RIC-01 / R2-PIR-03
## Final Independent Evidence Closure Audit v1.0

**Audited commit:** `ad6f4cf96d739a76e7c03d3aa43177c5d56ccf7f`  
**Parent:** `f1ab1aa1b7873bdefa663ef0c737cbee69332d10`  
**Production repair commit:** `76af710795285799d734846d377c44493c37ce0f`  
**Authoritative architecture:** `RIC-01-R2-Canonical-Ingress-Observation-Bridge-Formal-Architecture-v1.1-FROZEN.md`  
**Authoritative erratum:** `RIC-01-R2-Formal-Architecture-v1.1.1-Non-Cognitive-Semantics-Digest-Erratum-FROZEN.md`  
**Audit mode:** independent / read-only  
**R3 authorization:** NO

---

# 1. Executive Verdict

PIR-03 correctly preserved the production runtime: the commit contains no `dgca/` production changes.

It also repaired the PIR-02 verification report registry description and restored the **R2-I01..I58 invariant texts** to the frozen architecture wording, except for the intentionally corrected I04 digest wording governed by the v1.1.1 erratum.

However, PIR-03 still does **not** implement the exact frozen `T01..T89` acceptance ledger.

The committed `FROZEN_R2_TEST_OBLIGATIONS` is a hybrid ledger:
- T01..T12 are partly paraphrased;
- T13..T21 are not the frozen T13..T21 at all;
- T26..T43 are largely reassigned to unrelated PIR repair checks;
- T48 is reassigned;
- T52..T67 are largely reassigned;
- T75..T77 are reassigned;
- T68..T74 and T78..T89 are now mostly aligned.

Therefore the claim:

```text
"All 89 obligations restored to verbatim Section 5 frozen architecture wording"
```

is false in the committed code.

This is still a **release-evidence** defect, not a production-runtime defect.

```text
==================================================
DGCA — RIC-01 / R2-PIR-03
FINAL INDEPENDENT EVIDENCE CLOSURE AUDIT

PRODUCTION CODE:
UNCHANGED / PROVISIONALLY CONFORMANT

R2-I01..I58 TEXT LEDGER:
PASS
(I04 governed by v1.1.1 erratum)

T01..T89 EXACT FROZEN LEDGER:
FAIL

ADVERSARIAL A..Q:
NO NEW DEFECT FOUND

COGNITIVE-LAW DEFECTS:
0

PRODUCTION RUNTIME BLOCKERS:
0

RELEASE-EVIDENCE BLOCKERS:
1

R2:
OPEN — PIR-04 REQUIRED

R3:
NOT AUTHORIZED

FINAL VERDICT:
RIC01_R2_PIR03_INDEPENDENT_EVIDENCE_AUDIT_FAILED
==================================================
```

---

# 2. Scope Audit

The commit `ad6f4cf...` is exactly one commit ahead of `f1ab1aa...`.

Changed files are limited to:
- test/evidence files;
- PIR-02 report corrections;
- PIR-03 reports/audit artifact.

No production `dgca/` file is changed.

**Verdict:** PASS.

---

# 3. PIR-02 Report Consistency Repair

The PIR-02 report now replaces the obsolete registry keys:
- `contradiction_policy`
- `counterpart_contract`
- `event_envelope_version`
- `ordering_policy`
- `rfc11_structural_filter`
- `R2-RES-1.0`

with the actual v1.1.1 registry:
- `protocol_version`
- `event_descriptor_version`
- `operation_kinds`
- `observation_relation_policy`
- `rfc11_evidence_policy`
- `R2-RESULT-1.0`
- etc.

**Verdict:** CLOSED.

---

# 4. R2-I01..I58 Text Ledger

The committed invariant dictionary now matches the frozen architecture ledger:
- I01 Root identity authority;
- I02 raw content cannot grant persistent authority;
- I03 exact protocol;
- ...
- I58 observation-protocol governance.

The only deliberate wording delta is I04, where the impossible 66-hex digest from v1.1 is replaced by the corrected v1.1.1 erratum digest. This is lawful.

**Verdict:** PASS for invariant text identity.

Evidence quality is substantially improved, though several invariant rows remain broad mappings rather than one-to-one proofs. This alone is not the closure blocker because the related behaviors are covered elsewhere in the suite.

---

# 5. T01..T89 Ledger — Authoritative Frozen Source

The actual frozen v1.1 architecture contains, among others:

```text
T13 novel text TRANSIENT_ONLY → graph persistent state digest unchanged
T14 graph logical time unchanged
T15 no persistent Node created
T16 no persistent Edge created
T17 no graph.X contradiction written
T18 RFC11 pending candidates/growth/merge unchanged
T19 causal ledger unchanged
T20 RFC12 SDCR still contains transient novel node participation
T21 explicit novel/current relation can be represented by TBR without persistent Edge creation

T26 simultaneous descriptor with two nodes → exactly one lawful simultaneous TBR
T27 sequence descriptor → only adjacent-transition TBRs
T28 explicit contradiction pair → exactly one contradiction TBR
T29 invented TBR not derivable from descriptor → reject batch
T30 TBR member whose node receipt lacks exact binding_scope_id → reject batch

T31 every ReceiptID rederives from MicroEpisodeID + exact slot
T32 every TBRID rederives from MicroEpisodeID + exact binding index
T33 receipt slot gap/duplicate → reject entire batch
T34 receipt ID tamper → reject entire batch
T35 TBR ID tamper → reject entire batch
T36 numeric parent collision with different MicroEpisodeID cannot pass canonical batch validation

T37 simultaneous all ordered non-self pairs are observation relations
T38 sequence same-step relation is RFC11-eligible
T39 sequence adjacent-step relation is RFC11-eligible
T40 sequence nonadjacent relation may be a read-only Edge receipt but cannot vote in RFC11
T41 synthetic ev: role Edge cannot vote in RFC11
T42 concept/generalization Edge cannot vote in RFC11
T43 no graph-global diff is used to derive evidence

T48 transient observation creates zero RFC11 vote

T52 exact persistent retry → callback not executed
T53 retry → graph persistent state digest unchanged
T54 retry → RFC11 vote set unchanged
T55 same Root + transport-different subevent compiling to exact same mutation intent → same R1 TxID
T56 distinct Root + same content → distinct R1 TxID and independent evidence

T57 transient contradiction → TBR + endpoint receipts, graph.X unchanged
T58 authorized contradiction → graph.X written inside R1 command
T59 contradiction does not become RFC11 positive Edge evidence

T60 authorizer=None rejects persistent mode
T61 bare boolean authorization equivalent does not exist / is rejected
T62 authorizer false → zero mutation
T63 authorizer exception → zero mutation
T64 non-bool authorizer result → fail closed
T65 ordinary "fact: X" has no persistent authority
T66 ordinary "correction: X" has no persistent authority
T67 valid Root/Event IDs without capability have no persistent authority

T75 close_result closes all result SDCRs
T76 second close_result call is harmless
T77 close_result changes no persistent state digest or ledger
```

These texts are not what the PIR-03 matrix currently assigns to those IDs.

---

# 6. Concrete Mismatches in the Committed Matrix

## T13..T21

Committed:
```text
T13 text event descriptor validation
T14 code event descriptor validation
T15 sequence micro-episode descriptor dictionary
T16 context changes canonical micro-episode descriptor and ID
T17 malformed simultaneous empty descriptor rejected pre-mutation
T18 one-step sequence rejected pre-mutation
T19 generic raw payload with unknown field fails closed
T20 episode micro descriptor length mismatch fails closed
T21 default authorizer denies all persistent observation
```

Frozen:
```text
T13..T21 = transient-only state isolation / transient SDCR / novel TBR without persistent Edge
```

**Result:** FAIL.

## T26..T36

The committed ledger maps these IDs to authorizer and PIR-01 repair checks.

The frozen ledger requires:
- exact simultaneous/sequence/contradiction TBR construction;
- invented TBR rejection;
- member scope rejection;
- ReceiptID/TBRID rederivation;
- slot gap/duplicate;
- ID tamper;
- numeric parent collision.

**Result:** FAIL.

## T37..T43

The committed ledger assigns contradiction/close/replay-result checks.

The frozen ledger requires:
- observation relation classification;
- same-step/adjacent/nonadjacent RFC11 behavior;
- synthetic/concept exclusion;
- no global graph diff.

**Result:** FAIL.

## T48

Committed:
```text
serialized capability in text no authority escalation
```

Frozen:
```text
transient observation creates zero RFC11 vote
```

**Result:** FAIL.

## T52..T67

The committed ledger assigns receipt/TBR and RFC11 repair checks.

The frozen ledger requires:
- retry callback/digest/vote idempotence;
- root-equivalent Tx semantics;
- contradiction persistence semantics;
- authorizer/keyword/capability authority firewall.

**Result:** FAIL.

## T75..T77

Committed:
```text
T75 double close_result no persistent delta no failure
T76 partial projection failure removes earlier reps
T77 transient observation generates valid SDCR
```

Frozen:
```text
T75 close_result closes all result SDCRs
T76 second close_result call is harmless
T77 close_result changes no persistent state digest or ledger
```

**Result:** FAIL.

---

# 7. Meta-Test Does Not Detect This

The new matrix meta-test checks:
- the ID set exists;
- every text is non-empty;
- every evidence tuple is non-empty;
- referenced functions exist;
- no self-reference to the matrix file.

It does **not** compare `FROZEN_R2_TEST_OBLIGATIONS` against the authoritative frozen architecture text.

Therefore a complete but incorrectly numbered ledger passes.

This is exactly what happened.

---

# 8. High-Risk Test Quality Notes

The new PIR-03 high-risk suite is useful and closes several previously missing behaviors:
- T01..T05;
- T44..T50;
- T68..T74;
- T78..T89.

Two tests should be strengthened during the final evidence pass:

1. **T71 changed-graph replay RID**
   - current test changes an Edge weight and only asserts the replay RID is a non-empty string;
   - it does not prove `RID_after != RID_before`.
   - For evidence of “may lawfully produce a different current-state RID,” construct a lawful graph change known to alter the projected receipt/assembly set and assert a different RID while replay persistent delta remains zero.

2. **T70 unrelated graph change**
   - current test mutates the private graph directly with `graph.node()` / `graph._link()`;
   - use a separate lawful authorized Root transaction where feasible so the scenario does not rely on bypassing runtime lineage governance.

These are evidence-strengthening items; no production defect is inferred.

---

# 9. No New Production Defect Found

The audit found no new defect in:
- R2 runtime bridge;
- semantics digest;
- receipt/TBR validation;
- close lifecycle;
- authorization boundary;
- R1 persistent Tx integration;
- checkpoint compatibility.

No production source modification is authorized by this audit.

---

# 10. Required PIR-04 Closure

PIR-04 must be a **strict evidence-only correction**.

It must:
1. replace the entire `FROZEN_R2_TEST_OBLIGATIONS` dictionary with the exact frozen v1.1 T01..T89 text;
2. keep the v1.1.1 digest erratum only where relevant;
3. remap each exact obligation to semantically matching tests;
4. add missing tests only where no existing test proves the exact obligation;
5. strengthen T70/T71 evidence;
6. keep `dgca/` unchanged;
7. run full regressions.

---

# 11. Final Verdict

```text
RIC01_R2_PIR03_INDEPENDENT_EVIDENCE_AUDIT_FAILED
```

R2 remains runtime-complete but release-evidence-open.

R3 remains unauthorized.
