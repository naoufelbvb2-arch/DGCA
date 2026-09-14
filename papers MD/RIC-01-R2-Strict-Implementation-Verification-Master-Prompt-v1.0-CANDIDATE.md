# DGCA — RIC-01 / R2
## Canonical Ingress & Observation Bridge
### Strict Implementation & Verification Master Prompt v1.0 — CANDIDATE

**Authoritative architecture:**  
`RIC-01-R2-Canonical-Ingress-Observation-Bridge-Formal-Architecture-v1.1-FROZEN.md`

**Forensic basis:**  
`RIC-01-R2-F01-Canonical-Ingress-Observation-Bridge-Forensics-v1.0.md`

**Freeze review:**  
`RIC-01-R2-AFR01-Adversarial-Formal-Freeze-Review-v1.0.md`

**Implementation baseline:**  
`e0ce00283962ef4ae94ce3bed184fa9ca594bfbc`

**R0:** `CLOSED`  
**R1:** `CLOSED`  
**R2 implementation:** `AUTHORIZED ONLY BY THE FROZEN v1.1 SPEC`  
**R3:** `NOT AUTHORIZED`  
**Audio:** `DEFERRED / DO NOT TOUCH`  
**Vision:** `DO NOT MODIFY`  
**Prompt status:** `CANDIDATE — NOT YET EXECUTION-AUTHORIZED`

---

# 0. Mission

Implement the frozen R2 v1.1 Canonical Ingress & Observation Bridge exactly.

The implementation must connect, without redefining:

```text
trusted external occurrence
→ R1 RootExternalEpisodeID
→ R1 IngressEventID
→ deterministic symbolic Encoder
→ ordered Canonical MicroEpisodes
→ optional R1-governed persistent observation mutation
→ RFC-11 external structural evidence
→ canonical ParticipationReceipts / TBRs
→ read-only Assembly selection
→ RFC-12 canonical SDCR(s)
→ CanonicalObservationResult
```

The implementation must establish the constitutional runtime separation:

```text
Observation != Persistent Learning
Identity != Authority
Content != Authority
Transient Working State != Persistent Cognitive State
```

Ordinary/transient perception MUST function with zero persistent cognitive learning.

Do not implement R3 user UX or Developer Mode UX.

---

# 1. Absolute Source of Truth

Before modifying source, read the complete frozen architecture and AFR review.

If this prompt conflicts with:

```text
RIC-01-R2-Canonical-Ingress-Observation-Bridge-Formal-Architecture-v1.1-FROZEN.md
```

then:

```text
THE FROZEN R2 v1.1 SPEC WINS.
```

If implementation requires any of the following:

```text
new cognitive law
change to Law 1/2 mathematics
change to Law 11 sequence-learning mathematics
change to Law 14 thresholds/policy
change to RFC-12 representation scoring/binding constitution
change to R1 causal identity formulas
change to R1 TxID semantics
checkpoint schema bump beyond 1.2.0
Audio work
Vision redesign
R3 permissions/Agent UX
```

STOP and report:

```text
RIC01_R2_IMPLEMENTATION_BLOCKED
```

Do not improvise around a frozen boundary.

---

# 2. Mandatory Preflight

Before editing:

1. Record `git rev-parse HEAD`.
2. Confirm:
   ```text
   HEAD == e0ce00283962ef4ae94ce3bed184fa9ca594bfbc
   ```
   If not, stop and report the exact difference before implementation.
3. Record branch and upstream.
4. Confirm working-tree cleanliness.
5. Preserve any unrelated local work.
6. Run:
   ```text
   pytest tests/
   python -m ruff check dgca/ tests/
   ```
7. Record baseline cognitive signature.
8. Record:
   ```text
   CAUSAL_IDENTITY_PROTOCOL_DIGEST
   LITERAL_DOMAIN_REGISTRY
   checkpoint schema/runtime/cognitive versions
   ```
9. Read at minimum:
   ```text
   dgca/causal_identity.py
   dgca/encoder.py
   dgca/encoding/english/types.py
   dgca/encoding/english/emitter.py
   dgca/graph.py
   dgca/assembly.py
   dgca/representation.py
   dgca/loop.py
   dgca/agent.py
   dgca/persistence.py
   dgca/__init__.py
   all R0/R1/PIR tests
   tests/baseline_signature.txt
   ```
10. Record existing legacy ingress entry points:
    ```text
    MasterSymbolicEncoder.feed_to_graph
    CodeEncoder.feed
    CognitiveAgent.perceive_text
    CognitiveAgent.perceive_code
    graph.observe
    graph.observe_sequence
    RFC16 process_validated_learning
    ```

Expected immutable baselines:

```text
cognitive baseline signature =
915119d40643cb97

R1 causal identity protocol digest =
f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398

R1 literal identity domain count =
21

checkpoint_schema_version =
1.2.0

runtime_contract_version =
1.2.0
```

Do not change these to make R2 pass.

---

# 3. Mandatory R2 Protocol Constants

Implement exactly:

```text
R2_OBSERVATION_PROTOCOL_VERSION = "R2-OBS-1.0"

EVENT_DESCRIPTOR_VERSION        = "R2-EVENT-1.0"
MICRO_DESCRIPTOR_VERSION        = "R2-MICRO-1.0"
MUTATION_DESCRIPTOR_VERSION     = "R2-MUT-1.0"
RECEIPT_BATCH_VERSION           = "R2-RB-1.0"
OBSERVATION_RESULT_VERSION      = "R2-RESULT-1.0"
```

Implement the exact frozen semantics registry from Section 3.1 of the R2 v1.1 specification.

Required diagnostic/release fingerprint:

```text
R2_OBSERVATION_SEMANTICS_DIGEST =
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b7c
```

The implementation MUST recompute this value from the exact literal registry.

Forbidden:

```text
hard-code the expected digest without recomputing it
persist the R2 semantics registry as cognitive state
add a new R1 identity domain
change R1 protocol digest
```

---

# 4. Preferred Implementation Boundary

Prefer a dedicated module such as:

```text
dgca/observation.py
```

or equivalently narrow R2-named module.

It should own R2 orchestration types such as:

```text
CanonicalObservationBridge
PersistentObservationAuthorizer
CanonicalEventDescriptor helpers
CanonicalMicroEpisodeDescriptor helpers
CanonicalReceiptEntry
CanonicalBindingEntry
CanonicalReceiptBatch
CanonicalObservationResult
R2ProjectionFailure
R2 contract/validation errors
R2 protocol constants / semantics registry
```

The bridge MUST remain orchestration infrastructure.

It MUST NOT become:
- a learned controller;
- a semantic truth owner;
- a ranking engine;
- a new cognitive policy engine.

---

# 5. Runtime Binding / Raw Graph Capability

R2 requires trusted internal access to the canonical runtime's authoritative graph without invalidating R1 lineage.

The canonical bridge MUST be bound by a trusted runtime integration/factory mechanism.

If necessary, add a narrow R1-runtime internal binder/factory, for example conceptually:

```text
CanonicalR1RuntimeRoot.create_observation_bridge(...)
```

or another equivalent private capability binding.

Requirements:

```text
ordinary caller never receives raw CognitiveGraph
bridge never calls unsafe_mutable_graph()
bridge never calls unsafe_mutable_ledger()
bridge never exposes raw graph/ledger
persistent graph mutation happens only inside execute_persistent_command()
transient projection only performs read-only graph access + transient RFC12 operations
```

Do not weaken PIR-03 inspection encapsulation.

Do not make `runtime.graph` raw again.

---

# 6. Supported Modalities

Canonical R2-v1 supports only:

```text
text
code
```

Text path MUST use existing:

```text
MasterSymbolicEncoder.encode_text(...)
```

Code path MUST use existing:

```text
MasterSymbolicEncoder.encode_code(...)
```

Do not alter English Encoder v2 semantics.

Do not alter Audio.

Do not route Vision through R2-v1.

---

# 7. Trusted Occurrence Boundary

The canonical API must require trusted host occurrence information equivalent to:

```python
ExternalOccurrenceDescriptor(
    boundary_namespace=...,
    source_occurrence_key=...,
)
```

and a trusted:

```text
source_event_key
ingress_boundary
modality
```

Derive Root/Event IDs only through frozen R1 functions.

Raw content MUST NOT be able to choose:
- RootExternalEpisodeID;
- source occurrence key;
- persistent-learning capability.

Do not accept caller-supplied authoritative RootID/EventID as a convenience bypass for the public bridge.

Internal tests may construct exact trusted occurrence descriptors directly.

---

# 8. Canonical Event Descriptor v1

Implement strict validators/builders for exact schemas in Section 6 of the frozen spec.

## Text

Exact keys only:

```python
{
    "descriptor_version": "R2-EVENT-1.0",
    "modality": "text",
    "encoder_contract": "DGCA_SYMBOLIC_TEXT_V1",
    "payload": {
        "raw_text": <exact string>,
        "context": <string or None>,
    },
}
```

## Code

Exact keys only:

```python
{
    "descriptor_version": "R2-EVENT-1.0",
    "modality": "code",
    "encoder_contract": "DGCA_SYMBOLIC_CODE_V1",
    "payload": {
        "source_code": <exact string>,
        "module": <non-empty string>,
    },
}
```

Unknown keys fail closed.

No RootID/EventID/capability/retry counter may appear inside the event descriptor.

Compute:

```text
EventDescriptorDigest
```

using frozen R1 event-descriptor canonical hashing.

---

# 9. Ephemeral Ingress Binding Registry

Implement exactly the transient live-runtime registry:

```text
IngressEventID
→ (
    RootExternalEpisodeID,
    EventDescriptorDigest,
    "R2-OBS-1.0"
)
```

Rules:

```text
same EventID + same tuple → allowed live replay
same EventID + any mismatch → fail before encoding/mutation
```

This registry:
- is transient;
- is not checkpointed;
- is not cognitive state;
- does not modify R1 ledger on TRANSIENT_ONLY.

Persistent-mode durable binding remains owned by R1 ledger.

---

# 10. Encoder Invocation

Invoke the encoder exactly once per bridge execution.

Do not:
- pre-encode for identity and encode again for mutation;
- reorder episodes;
- silently drop episodes;
- merge episodes.

If encoder fails or returns malformed `SensoryEpisode`:
- persistent callback MUST NOT execute;
- RFC11 vote MUST NOT occur;
- no R1 transaction MUST commit.

Zero emitted episodes return:

```text
NO_OBSERVABLE_CONTENT
```

with zero MicroEpisodes, zero SDCRs, zero persistent delta.

---

# 11. Canonical MicroEpisode Descriptor

Implement exact Section-9 schema.

Preserve list order exactly.

Validate:
- allowed `kind`;
- non-empty region/symbol/contradiction strings;
- finite `structural_weight`;
- finite `valence`;
- simultaneous vs sequence shape constraints.

`child_index` is zero-based encoder emission order.

Derive one `ObservationTransactionID` for the whole ingress execution using exact operation kind:

```text
R2_TRANSIENT_ONLY
R2_AUTHORIZED_PERSISTENT
```

Derive each MicroEpisodeID through frozen R1.

Do not use:
- graph.t;
- ep<t>;
- hashes of raw text alone.

---

# 12. Execution Mode API

The bridge must expose exactly two semantic modes:

```text
TRANSIENT_ONLY
AUTHORIZED_PERSISTENT
```

The default MUST be:

```text
TRANSIENT_ONLY
```

Do not provide a convenience boolean API such as:

```python
authorized=True
learn=True
developer=True
```

Use an explicit mode enum/value.

---

# 13. PersistentObservationAuthorizer

Implement the exact deny-all-by-default protocol:

```python
@runtime_checkable
class PersistentObservationAuthorizer(Protocol):
    def verify_persistent_observation(
        self,
        *,
        capability: object,
        root_external_episode_id: str,
        ingress_event_id: str,
        modality: str,
        operation_kind: str,
    ) -> bool:
        ...
```

Bridge default:

```text
authorizer=None
```

means DENY ALL persistent observation.

Before any persistent mutation:

```text
authorizer present
capability present
operation kind exact
verifier returns literal True
```

Any:
- absence;
- `False`;
- exception;
- non-bool result

fails closed with zero persistent delta.

The capability MUST NOT enter:
- causal identity;
- mutation descriptor;
- graph memory;
- checkpoint state;
- observation result diagnostics containing raw secret/capability material.

Do not log/repr opaque capability content.

---

# 14. Canonical Node Projection

Implement exact frozen projection:

```text
positive signal:
region + ":" + symbol

contradiction endpoint:
if endpoint contains ":" → endpoint
else → "text:" + endpoint
```

Do not change existing graph naming semantics.

---

# 15. Observation Relation Classification

Implement deterministic observation-relation derivation exactly per Section 15.

## Simultaneous

First-occurrence unique NodeRefs, then all ordered non-self pairs.

## Sequence

Traverse source step/order then destination step/order.

Deduplicate ordered pair by first occurrence.

Classify each ordered pair by minimum step distance:

```text
0 → EXTERNAL_DIRECT_SAME_STEP
1 → EXTERNAL_DIRECT_ADJACENT_TEMPORAL
>1 → EXTERNAL_TEMPORAL_DERIVED
```

No set iteration may choose first occurrence.

---

# 16. RFC-11 Eligible Evidence

Implement exact frozen subset.

## Simultaneous

All observation relation pairs are RFC11-eligible.

## Sequence

Only:

```text
same-step
adjacent-step
```

ordered pairs are eligible.

Never vote:
- nonadjacent temporal-derived pair;
- `ev:` role edge;
- hub/concept edge;
- category/generalization edge;
- prediction/reasoning/generated edge.

Do not infer evidence from a graph diff.

After each persistent MicroEpisode graph observation:
- locally check eligible edge existence;
- call `record_participation()` only on verified eligible edges;
- use the SAME RootExternalEpisodeID for every MicroEpisode.

Let RFC11's own root sets remain the final vote-dedup authority.

---

# 17. Persistent Transaction Granularity

One encoded IngressEvent = one R1 persistent command.

Forbidden:

```text
one Tx per edge
one Tx per MicroEpisode
one Tx per contradiction
```

Construct exact frozen `PersistentMutationCommand`:

```text
mutation_owner_ref =
"RIC01_R2_CANONICAL_OBSERVATION_BRIDGE"

mutation_kind =
"CANONICAL_OBSERVATION_PERSISTENCE"
```

Implement exact `canonical_targets`, exact v1 mutation descriptor, and exact owner-defined scope from Section 18.

No transport retry nonce.

No capability object.

No arbitrary user metadata.

---

# 18. Persistent Callback Execution Order

Within one:

```text
CanonicalR1RuntimeRoot.execute_persistent_command(...)
```

callback, execute MicroEpisodes strictly in emitted order.

For each MicroEpisode:

1. persist explicit contradiction pairs first;
2. execute existing positive graph observation:
   - simultaneous → `graph.observe(...)`;
   - sequence → `graph.observe_sequence(...)`;
3. then derive/verify RFC11-eligible direct external edges;
4. record RFC11 participation with same RootExternalEpisodeID.

Contradiction-only simultaneous episode:
- persists contradictions;
- does not call `graph.observe()`.

All persistent effects MUST remain inside the one R1 owner callback.

---

# 19. Persistent Replay

When R1 returns already committed replay:

```text
mutator callback not invoked
persistent_executed = False
additional persistent graph delta = 0
additional RFC11 vote delta = 0
```

Continue to current-state transient projection.

Do not skip projection merely because persistence is replay.

---

# 20. Local RFC-12 Coordinates

Implement exact local cycle derivation:

```text
int(
    SHA256(
        UTF8("DGCA:R2:LOCAL_CYCLE:v1\0" + ObservationTransactionID)
    ).hexdigest(),
    16
)
```

Use:

```text
snapshot_or_microtick = child_index
```

These values are operational only.

Never treat them as causal authority.

---

# 21. Explicit Binding Plan Before Receipts

Before final node receipt construction, derive the entire deterministic binding plan from the canonical MicroEpisode descriptor.

A TBR is lawful ONLY when it corresponds to:
- explicit simultaneous structure;
- an adjacent sequence transition;
- an explicit contradiction pair.

Forbidden TBR authority:
- same Root alone;
- same MicroEpisode alone;
- same timestamp;
- same context;
- coactivation alone;
- graph neighborhood;
- semantic similarity.

---

# 22. ParticipationReceipt Construction

Implement exact frozen global slot order:

```text
1. positive node occurrences
2. contradiction endpoint occurrences
3. live gate-open observation-relation Edge receipts
```

Slots MUST be contiguous:

```text
0..N-1
```

Use exact R2 occurrence scopes and TBR binding scopes.

Every node receipt must contain:
- MicroEpisodeID;
- local occurrence scope;
- every exact TBR scope containing that occurrence;
- deterministic first-occurrence scope order.

Positive node receipt:

```text
origin_lineage = "external"
activation_magnitude = 1.0
relational_drive = 0.0
```

Contradiction endpoint receipt has the same external/activation semantics but does not imply positive association.

Known edge receipt:
- only live edge;
- only gate-open edge;
- only edge from observation-relation list;
- `relational_drive = edge.W`;
- `activation_magnitude = 0.0`.

A nonadjacent temporal-derived sequence relation MAY receive a read-only edge receipt if live/gate-open, even though it MUST NOT vote in RFC11.

Derive every ReceiptID from:
- MicroEpisodeID;
- kind;
- element ref;
- scope refs;
- exact slot.

---

# 23. TBR Construction

Implement exact frozen TBR policy.

## Simultaneous

Exactly one TBR if at least two positive occurrences.

Members are positive NodeRefs in occurrence order.

## Sequence

One TBR per adjacent transition only.

Members:
- all source-step NodeRefs in occurrence order;
- then all destination-step NodeRefs in occurrence order.

No nonadjacent transition TBR.

## Contradiction

One TBR per explicit contradiction pair.

Members are normalized endpoint refs in endpoint order.

## Scope / index

Exact scope:

```text
r2scope:<Micro_episode_id>:<scope_kind>:<scope_index>
```

Binding indexes are one contiguous deterministic sequence.

Derive every TBRID through frozen R1 helper.

Do not put ParticipationReceipt IDs into `member_receipt_refs`; current RFC12 semantics use participating element refs.

---

# 24. CanonicalReceiptBatch

Implement a transient envelope equivalent to the frozen logical structure:

```text
batch version
ObservationTransactionID
MicroEpisodeID
child_index
local_parent_cycle_id
snapshot_or_microtick
ordered receipt entries with slot indexes
ordered binding entries with binding indexes
```

This object MUST NOT be checkpointed.

It is the fail-closed causal validation boundary before RFC12.

---

# 25. Receipt Batch Validator

Implement every frozen Section-25 check.

Required:
- parent identity consistency;
- numeric coordinate consistency;
- exact contiguous slot/index sequences;
- ReceiptID re-derivation;
- TBRID re-derivation;
- `origin_lineage == "external"`;
- `origin_view == "external"`;
- TBR member participation;
- exact TBR scope present in matching node receipt;
- TBR is derivable from canonical MicroEpisode descriptor.

A correctly hashed but descriptor-invented TBR MUST fail.

Do not rely solely on RFC12's existing validator; R2 adds causal/scoped validation before calling RFC12.

---

# 26. Read-Only Assembly Selection

After persistent decision, or directly in transient mode:

derive cue activation from positive node receipts only.

Do not use contradiction-only endpoint receipts as positive Assembly cues.

Call existing:

```text
AssemblyManager.select_assemblies(...)
```

read-only.

Pass only stable:

```text
(assembly_id, version)
```

refs into RFC12.

Do not call `AssemblyManager.activate()` merely for R2 SDCR construction.

Do not introduce ActiveAssembly UUID into causal identity.

---

# 27. One SDCR per Observable MicroEpisode

For every MicroEpisode having at least one accepted ParticipationReceipt:

build exactly one canonical RFC12 representation.

Use:

```text
causal_parent_ref = MicroEpisodeID
```

and the exact local numeric coordinates.

Use only:
- validated ordered receipts;
- validated ordered TBRs;
- selected stable Assembly refs.

Do not create an aggregate ingress-level SDCR in R2-v1.

---

# 28. Projection Timing

## TRANSIENT_ONLY

Project against current unchanged graph.

## AUTHORIZED_PERSISTENT

Perform R1 persistent decision first.

Then project against post-decision current graph.

First commit may therefore be reflected immediately in:
- learned live Edge receipts;
- newly committed Assembly refs;
- updated relation strengths.

Replay performs no persistent mutation but still projects current state.

---

# 29. Projection Failure / R2ProjectionFailure

Implement explicit two-phase semantics:

```text
Persistent Phase:
NOT_REQUESTED | COMMITTED | REPLAY

Transient Phase:
PROJECTED | FAILED
```

If projection fails after persistent decision:
- persistent commit/replay remains authoritative;
- do not rollback;
- close every SDCR created by that failed projection attempt;
- raise explicit `R2ProjectionFailure`.

Failure MUST carry enough non-secret diagnostic state to distinguish:
- TxID;
- persistent_executed;
- persistent_committed;
- failed child index/stage.

Retry after a committed failure:
- reaches R1 replay/no-op;
- may reconstruct transient SDCRs;
- must not double-learn.

Do not set R1 runtime to MUTATION_FAILED merely because read-only/transient projection failed after successful persistent decision.

---

# 30. CanonicalObservationResult

Implement the frozen result shape and statuses.

Successful result only after all requested MicroEpisode projections succeed.

Required statuses:

```text
TRANSIENT_OBSERVED
PERSISTENT_EXECUTED
PERSISTENT_REPLAY
NO_OBSERVABLE_CONTENT
```

The result is transient operational state.

No result field becomes persistent cognition.

Do not include raw opaque authorization capability in result/diagnostics.

---

# 31. Result SDCR Lifecycle

Implement:

```text
close_result(result)
```

Idempotent.

It must close every still-active RFC12 representation created by that result.

It must not change:
- persistent graph state;
- RFC11 structural evidence;
- R1 causal ledger.

If projection fails midway:
- equivalent cleanup happens automatically.

Do not checkpoint result/receipt batches/SDCR operational state.

---

# 32. Contradictions

## TRANSIENT_ONLY

Contradiction:
- creates endpoint node receipts;
- creates contradiction TBR;
- does not modify graph.X;
- never becomes RFC11 positive edge evidence.

## AUTHORIZED_PERSISTENT

Persist exact contradiction updates inside the same R1 callback before positive observation.

Then project transiently afterward.

---

# 33. Valence / Structural Weight

Preserve exact encoder-emitted finite values in MicroEpisode descriptor.

In persistent mode:
- pass unchanged to existing graph observation API.

In transient mode:
- do not persist them;
- do not invent a new cognitive field;
- retain descriptor/result availability only.

---

# 34. RFC16 Firewall

Do not use:
- `process_validated_learning()`;
- `"fact:"`;
- `"correction:"`;
- `"correct"`;
- `"wrong"`;
- `"continue"`;
- `"stop"`

as canonical R2 learning authority.

These strings are ordinary content or legacy controls, never R2 persistent permission.

---

# 35. Legacy API Conservation

Do not delete legacy APIs in R2.

Preserve regression compatibility for:

```text
MasterSymbolicEncoder.feed_to_graph()
CodeEncoder.feed()
CognitiveAgent.perceive_text()
CognitiveAgent.perceive_code()
direct graph.observe()/observe_sequence()
RFC16 process_validated_learning()
```

But document/mark them as:

```text
LEGACY_NON_CANONICAL
```

where appropriate.

Do not rewire CognitiveAgent UX in R2.

R3 owns canonical user runtime integration.

---

# 36. Checkpoint / Protocol Compatibility

Do not bump checkpoint schema.

R2 uses existing R1 schema 1.2.0 observation-protocol fields.

Canonical bridge construction requires runtime protocol:

```text
R2-OBS-1.0
```

Do not silently reinterpret an existing schema-1.2.0 checkpoint from another observation protocol.

A pre-R1 `1.1.1` checkpoint may use the already-frozen R1 migration path only when explicitly migrated with target:

```text
R2-OBS-1.0
```

No new migration law is added in R2.

---

# 37. Failure Semantics

Preserve R1 fail-stop rules for failure inside persistent callback.

Do not implement generic rollback.

Transient pre-command failure:
- zero persistent delta.

Projection failure after commit:
- persistent state remains;
- partial SDCRs close;
- explicit R2ProjectionFailure.

---

# 38. Locality / Complexity

Forbidden:
- graph-global before/after diff;
- global graph scan to infer external evidence;
- whole-graph receipt enumeration.

Allowed complexity is local to:
- emitted episode size;
- pair relations from that episode;
- direct edge lookups;
- local Assembly selection;
- current receipt/TBR batch;
- RFC12 local build.

---

# 39. Mandatory Frozen Invariant Ledger

Implement traceable verification for every:

```text
R2-I01 .. R2-I58
```

from the frozen v1.1 architecture.

The verification report MUST list each invariant and its test/evidence mapping.

Do not merge multiple invariants into an opaque "covered" claim.

---

# 40. Mandatory Acceptance Test Ledger

Implement and execute every frozen:

```text
T01 .. T89
```

from Section 41 of the frozen v1.1 specification.

Tests may be parameterized, but the report must map every literal test ID to executed test function/case and PASS/FAIL.

No helper-only test may substitute for an end-to-end test when the frozen requirement names:
- bridge execution;
- RFC11 voting;
- RFC12 representation;
- persistent replay;
- result cleanup;
- authorization.

---

# 41. Mandatory Additional Adversarial Scenarios

In addition to T01..T89, execute explicit adversarial scenarios:

```text
A. one Root + 500 MicroEpisode participation calls for same candidate
   → RFC11 root vote remains one independent root vote

B. one MicroEpisode with same node repeated many times
   → receipt occurrences preserved
   → relation edge receipt dedup deterministic
   → no duplicate RFC11 independent vote

C. forged TBR with valid hash but wrong descriptor authority
   → batch rejected

D. forged TBR with valid members but receipt missing exact binding scope
   → batch rejected

E. same EventID reused with same raw text but changed context
   → live ingress binding conflict

F. same Root + different EventID + same compiled mutation intent
   → same R1 TxID, no duplicated persistent mutation

G. independent Root + identical text + valid capability
   → independent persistent mutation / RFC11 evidence

H. ordinary text contains serialized-looking capability/RootID
   → no authority escalation

I. authorizer object returns truthy non-bool
   → fail closed

J. persistent commit then forced RFC12 failure on child >0
   → partial SDCRs closed
   → persistent commit retained
   → retry is persistent replay

K. close_result twice
   → no exception
   → no persistent delta

L. transient-only execution with graph state digest before/after
   → exact persistent payload/digest equality

M. set/dict/hash iteration perturbation
   → same descriptor IDs / slots / bindings

N. sequence with three steps
   → step0↔step2 live edge may be read-only receipt
   → cannot enter RFC11 evidence

O. synthetic ev: edge created by sequence learning
   → never RFC11 vote

P. concept/generalization side-effect edge
   → never RFC11 vote

Q. contradiction-only transient MicroEpisode
   → endpoint receipts + TBR
   → graph.X unchanged
   → no RFC11 evidence
```

---

# 42. Fault Injection

Use mocks/fault injection where necessary for:

```text
encoder exception
authorizer exception
persistent callback failure
RFC12 representation build failure after earlier child success
result close failure handling
receipt/TBR tamper
R1 replay path
protocol mismatch
```

Do not add production test-only branches that alter cognitive semantics.

---

# 43. Suggested Test Organization

Prefer narrow test modules such as:

```text
tests/test_ric01_r2_identity.py
tests/test_ric01_r2_transient.py
tests/test_ric01_r2_persistent.py
tests/test_ric01_r2_receipts.py
tests/test_ric01_r2_rfc11.py
tests/test_ric01_r2_projection.py
tests/test_ric01_r2_adversarial.py
```

Exact organization may differ.

Every test name or docstring must expose the relevant:

```text
R2-Ixx
Txx
AFR/adversarial label
```

when applicable.

---

# 44. Required Regression Gates

After implementation run:

```text
all R2 tests
all R1 tests including PIR-01/PIR-02/PIR-03
all R0/C01/C02/C03 tests
full pytest tests/
python -m ruff check dgca/ tests/
baseline signature
R1 protocol digest
R1 literal domain registry
R2 semantics digest
checkpoint schema/version checks
```

Required:

```text
100% PASS

baseline =
915119d40643cb97

R1 protocol digest =
f526f9969af11f79982952c80afb810ed789fb961a3d6c20e7766d0dcf702398

R1 literal domains =
21

R2 semantics digest =
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b7c

checkpoint schema =
1.2.0
```

Do not update baseline/protocol constants to accommodate R2.

---

# 45. Scope Audit

Before finalization inspect:

```text
git diff e0ce00283962ef4ae94ce3bed184fa9ca594bfbc
git status
```

Authorized production changes are expected primarily in:
- a new R2 observation module;
- narrow trusted runtime binding in `dgca/causal_identity.py` if required;
- narrow exports in `dgca/__init__.py`;
- documentation/comments marking legacy ingress as noncanonical, if necessary.

Changes to:
- `graph.py`;
- `assembly.py`;
- `representation.py`;
- `encoder.py`

must be minimized and justified by an unavoidable frozen-contract integration need.

Forbidden without BLOCKED verdict:
- cognitive-law mathematics changes;
- Law thresholds;
- encoder semantic redesign;
- Audio;
- Vision;
- Agent/REPL UX;
- R3 permissions.

---

# 46. Public API Restraint

Export only the narrow R2 host/developer integration API required by the frozen architecture.

Do not publicly export:
- raw graph capability;
- mutable ledger;
- private receipt-construction internals;
- unsafe mutation helpers.

Keep internal graph mutation capability private to canonical runtime/bridge integration.

---

# 47. Required Implementation Report

Create:

```text
RIC-01-R2-IMPLEMENTATION-VERIFICATION-REPORT.md
```

and mirror under:

```text
papers MD/
```

The report MUST include:

```text
starting commit
final commit
branch/upstream
working-tree preflight
pre-implementation full-suite result
files created/modified
R2 module architecture
trusted runtime binding design
protocol constants
exact R2 semantics registry and digest
event descriptor implementation
MicroEpisode descriptor/identity implementation
authorization boundary
TRANSIENT_ONLY implementation
AUTHORIZED_PERSISTENT implementation
PersistentMutationCommand descriptor
RFC11 relation/evidence classification
TBR authority and scope validation
receipt-slot implementation
CanonicalReceiptBatch validation
Assembly read-only selection
RFC12 build path
post-commit projection failure semantics
close_result lifecycle
legacy API boundary
checkpoint/protocol compatibility
R2-I01..I58 matrix
T01..T89 matrix
adversarial A..Q matrix
R1 regression results
R0 regression results
full repository total
Ruff result
cognitive baseline before/after
R1 protocol digest before/after
R1 domain registry before/after
R2 semantics digest
checkpoint schema before/after
scope diff audit
deviations/unresolved issues
final commit SHA
exact final verdict
```

No unexecuted check may be reported as PASS.

---

# 48. Final Verdict Vocabulary

End with exactly one:

```text
RIC01_R2_IMPLEMENTATION_VERIFIED
```

or:

```text
RIC01_R2_IMPLEMENTATION_FAILED
```

or:

```text
RIC01_R2_IMPLEMENTATION_BLOCKED
```

`VERIFIED` requires:
- all frozen R2 v1.1 requirements implemented;
- all R2-I01..I58 mapped and verified;
- T01..T89 passing;
- adversarial A..Q passing;
- all prior R1/R0 tests passing;
- full repository regression passing;
- Ruff passing;
- cognitive baseline unchanged;
- R1 protocol digest unchanged;
- R1 domain registry unchanged;
- R2 semantics digest exact;
- checkpoint schema unchanged;
- no R3/Audio/Vision work.

---

# 49. Git Discipline

Do not overwrite unrelated user work.

Before final commit:
- review `git status`;
- review complete diff from the baseline.

Suggested commit message after all gates pass:

```text
RIC-01/R2: implement canonical ingress and observation bridge
```

Push only after verification if authorized by the working environment.

Report the full 40-character SHA.

---

# 50. Stop Rule

Even if:

```text
RIC01_R2_IMPLEMENTATION_VERIFIED
```

DO NOT START R3.

DO NOT modify Agent UX.

DO NOT begin Text Encoder robustness work.

DO NOT reopen Audio.

Stop after the R2 implementation report and commit.

R2 is declared CLOSED only after an independent post-implementation audit of the actual committed source.

---

# 51. Execution Order

```text
PHASE A  preflight + frozen-spec read
PHASE B  R2 protocol/constants/types/errors
PHASE C  trusted runtime bridge binding
PHASE D  event + MicroEpisode canonicalization
PHASE E  authorizer + transient-only path
PHASE F  relation classification + receipt/TBR planning
PHASE G  CanonicalReceiptBatch validation
PHASE H  authorized persistent R1 command + RFC11 integration
PHASE I  read-only Assembly selection + RFC12 canonical SDCR
PHASE J  projection failure + result lifecycle
PHASE K  T01..T89 + adversarial A..Q
PHASE L  prior R1/R0 regression + full suite
PHASE M  baseline/protocol/semantics/scope audit
PHASE N  report + commit + push
STOP
```

---

# 52. Final Instruction

Implement exactly:

```text
RIC-01 / R2
Canonical Ingress & Observation Bridge
Formal Architecture v1.1 — FROZEN
```

Be additive.

Be fail-closed.

Keep ordinary observation non-learning.

Preserve all cognitive laws.

Preserve R0/R1.

Do not start R3.

Return only after execution with:

```text
implementation summary
files changed
R2 test totals
T01..T89 result
adversarial A..Q result
all R1/R0 regression totals
full repository total
Ruff
baseline comparison
R1 protocol digest comparison
R2 semantics digest
checkpoint schema comparison
report path
full final commit SHA
exact final verdict
```

Then stop.
