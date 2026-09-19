# DGCA — RFC14-POA01
## Precedence Ordering Authority Repair
### Formal Repair Specification v1.0 — FROZEN

**Trigger:** SCTT-00 rerun after RFC13-SR01  
**Observed residual:** RFC14 `ORDER_CONFLICT` on `{text:dog, text:canine}`  
**Parent architecture:** RFC-14 / Law 16 v1.0 — CLOSED / FROZEN  
**RFC15:** DEFERRED  
**Status:** FROZEN — IMPLEMENTATION AUTHORIZED SUBJECT TO COUNTERFACTUAL GATES

# 1. Empirical Trigger

After RFC13-SR01, SCTT-00 reached the intended final cognitive state:

```text
settled.participating_node_refs
= {text:dog, text:canine}
```

RFC14 then created reciprocal precedence constraints:

```text
dog < canine
canine < dog
```

and Law16 correctly closed with `ORDER_CONFLICT`.

The conflict came from using stored semantic association edges
`dog→canine` and `canine→dog` as if both were syntactic precedence authority.

# 2. Root Cause

Current `build_precedence_graph()` effectively treats any context-compatible directed graph Edge between two current fillers as:

```text
source occurrence MUST precede destination occurrence
```

This conflates directed semantic association with surface ordering authority.

English Encoder v2 emits a copular nominal definition such as:

```text
A dog is a canine.
```

as a **simultaneous** episode containing `dog` and `canine`. Graph learning lawfully creates both semantic directions. Those edges encode semantic association / role asymmetry, not two contradictory word-order commands.

# 3. Frozen RFC14 Semantics

RFC14 already requires:

```text
SemanticRole != SurfaceWordPosition
SyntaxKnowledge != LinearizationAuthority
PrecedenceAuthorityMustComeFromExistingContextCompatibleOrderingKnowledge
PropagationOrderCannotBeReinterpretedAsSurfaceSyntax
ActivationStrengthCannotByItselfDefineSurfaceOrdering
CanonicalIDOrderingCannotCreateSyntacticPrecedenceAuthority
MultipleReadyUnitsWithoutLawfulResolutionMustPreserveLinearizationAmbiguity
UnresolvedPrecedenceCyclesCannotBeBrokenByDroppingWeakestRelation
```

POA01 is therefore an implementation repair, not a new law.

# 4. Repair Principle

> A graph edge may contribute a Law16 precedence constraint only when that edge already carries lawful ordering authority. Directed semantic association alone is not ordering authority.

```text
EdgeExists(u,v) does NOT imply Precedes(u,v)
```

Required:

```text
Precedes(u,v)
iff
ActiveExistingOrderingAuthority(u,v,language_context)
```

# 5. Existing Ordering Authority in DGCA v1

POA01 adds no new learned field.

The current graph already stores positional sequence evidence in `Edge.lag`.

For `observe_sequence()`:
- forward earlier→later edges receive positive positional lag;
- reverse later→earlier edges receive negative positional lag.

Minimal current v1 authority:

```text
edge.lag > 0
```

subject to the existing language/context compatibility filter.

`lag == 0` is not order authority.

`lag < 0` on edge `u→v` does not authorize `u<v`.

# 6. Explicit Non-Authorities

The following MUST NOT by themselves create precedence:

```text
edge existence
edge.W
edge.n
edge.S
edge.fwd
edge direction alone
kind="assoc" with lag == 0
kind="sim"
kind="cat"
activation magnitude
propagation order
candidate order
frame ID
occurrence ID
scheduler order
lexicographic order
```

`edge.fwd` is role asymmetry (`head/place → attribute`) in current graph learning, not surface syntax authority.

# 7. Context Compatibility

Existing RFC14 language/context filtering remains in force.

An order-bearing edge contributes only if its ordering evidence is applicable to the active language/context.

# 8. True Conflict Preservation

If two independently lawful order-bearing relations authorize:

```text
u < v
v < u
```

then `ORDER_CONFLICT` remains correct.

No weakest-edge deletion, larger-W winner, larger-n winner, ID tie-break, or heuristic English preference.

# 9. No-Order Case

If no existing ordering authority relates two lawful ready occurrences, `LINEARIZATION_AMBIGUOUS` remains possible.

POA01 must not invent missing syntax merely for fluency.

# 10. Frame-Local Structural Ordering

POA01 does not redesign GenerativeFrame semantics.

Existing frame-local anchor/role orchestration remains unchanged.

This repair is limited to graph-edge-derived precedence constraints.

# 11. SCTT-00 Consequence

For learned definition:

```text
dog ↔ canine
```

the simultaneous co-occurrence edges have no positional sequence authority.

Therefore they MUST NOT create:

```text
dog < canine
canine < dog
```

The existing frame organization may then linearize anchor and role filler without the false graph cycle.

Empirical gate:

```text
probe = dog
output contains canine as a complete token
```

# 12. Sequence Preservation

For actually observed sequence `A → B → C`, positive-lag graph evidence must still create applicable forward precedence. Reverse negative-lag edges must not create reciprocal syntax constraints.

# 13. Production Scope

Expected production change:

```text
dgca/generation.py
```

No change should be required in:

```text
dgca/graph.py
dgca/encoding/
dgca/completion.py
dgca/representation.py
dgca/observation.py
dgca/recurrent.py
dgca/loop.py
```

Changing training to suppress reverse semantic edges is forbidden.

# 14. Mandatory Acceptance Tests

```text
POA01-T01 bidirectional assoc edges with lag=0 create zero reciprocal precedence.
POA01-T02 semantic edge direction alone is not precedence authority.
POA01-T03 W asymmetry alone is not precedence authority.
POA01-T04 n asymmetry alone is not precedence authority.
POA01-T05 fwd=True alone is not precedence authority.
POA01-T06 sim/cat relations do not create syntax precedence.
POA01-T07 positive lag creates forward precedence when context-compatible.
POA01-T08 negative lag on u→v does not create u<v.
POA01-T09 observe_sequence A→B yields forward, not reciprocal, Law16 order.
POA01-T10 observe_sequence A→B→C preserves ordering.
POA01-T11 incompatible language/context ordering evidence is ignored.
POA01-T12 genuine opposite order authorities still produce ORDER_CONFLICT.
POA01-T13 genuine conflict is not resolved by edge weight.
POA01-T14 genuine conflict is not resolved by IDs.
POA01-T15 no-order multiple-root case remains LINEARIZATION_AMBIGUOUS.
POA01-T16 RFC13-SR01 final {dog,canine} no longer creates false ORDER_CONFLICT.
POA01-T17 dog probe can surface canine through unchanged frame-local structure.
POA01-T18 generation causes zero persistent cognitive mutation.
POA01-T19 generation causes zero Assembly mutation.
POA01-T20 RFC15 remains unused.
POA01-T21 existing context isolation remains valid.
POA01-T22 weakest-edge-deletion defense remains valid using genuine order-bearing fixtures.
POA01-T23 deterministic fixed state/context/budget.
POA01-T24 all RFC13-SR01 tests pass unchanged.
POA01-T25 all R3-Min tests pass unchanged.
POA01-T26 exact frozen SCTT-00 rerun is untuned.
```

# 15. Existing Test Corrections

Any old test that creates a supposed precedence cycle using plain default:

```python
g.link("A", "B")
g.link("B", "A")
```

is semantically too weak because default assoc / zero-lag is not ordering authority.

Do NOT delete the conflict test. Strengthen its fixture with genuine ordering evidence.

Required distinction:

```text
real precedence cycle → ORDER_CONFLICT
mere bidirectional semantic association != precedence cycle
```

# 16. Counterfactual Gate

Before production edit, show:

```text
CURRENT:
dog↔canine semantic edges
→ reciprocal precedence
→ ORDER_CONFLICT

POA01:
same graph, same SDCR, same hierarchy
→ semantic edges excluded from precedence
→ no false reciprocal cycle
```

Also show:

```text
REAL SEQUENCE:
A before B
→ positive lag
→ A<B preserved
```

and:

```text
REAL CONFLICT:
A<B and B<A from genuine order evidence
→ ORDER_CONFLICT preserved
```

If any fails: `RFC14_POA01_BLOCKED`.

# 17. Regression Gates

Run POA01 tests, full RFC14 suites, RFC13-SR01, original RFC13, RFC12, R3-Min, R2/R1/R0, full pytest and Ruff.

No existing assertion may be weakened merely to get green.

# 18. Frozen Constants

Must remain unchanged:

```text
Cognitive law signature:
915119d40643cb97

R1:
f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398

R1 domains:
21

R2:
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b

R3:
fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc

checkpoint/runtime:
1.2.0

observation:
R2-OBS-1.0
```

# 19. Exact SCTT-00 Rerun

After repair, rerun exact frozen SCTT-00 unchanged. Required evidence:
- RFC13 retains subject+target;
- RFC14 has no false semantic-edge cycle;
- expected target appears for every primary pair;
- OOD remains safe;
- ordinary chat persistent delta remains zero;
- determinism remains intact.

# 20. Final Repair Verdict

```text
RFC14-POA01 FORMAL REPAIR

SEMANTIC ASSOCIATION != PRECEDENCE AUTHORITY
TRUE ORDER CONFLICT PRESERVATION: REQUIRED
NEW LAW: NO
NEW PERSISTENT FIELD: NO
NEW THRESHOLD: NO
GRAPH LEARNING: UNCHANGED
RFC13: UNCHANGED
RFC15: DEFERRED
IMPLEMENTATION: AUTHORIZED SUBJECT TO COUNTERFACTUAL + TEST GATES
```
