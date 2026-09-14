# DGCA — RIC-01 / R1
## Deterministic Causal Identity Protocol
### Causal Identity Forensics Report v1.0

**Project:** DGCA  
**Program:** `RIC-01 — Canonical Runtime Integration Contract`  
**Stage:** `R1 — Deterministic Causal Identity Protocol`  
**Baseline Commit:** `0f9c397d1bd1fc02a678fa55a9206075efe2bc35`  
**Parent Stage:** `R0 — Persistence & Runtime Lifecycle — CLOSED`  
**Status:** `FORENSICS COMPLETE — FORMAL R1 SPECIFICATION NOT YET FROZEN`  
**Code mutation authorized:** `NO`

---

# 1. Purpose

This report inventories identity creation and causal propagation across the current DGCA runtime and determines what R1 must solve before R2 can build the canonical Encoder → Observation → RFC-11 → RFC-12 bridge.

R1 is not a learning-law redesign.

R1 must answer four questions:

1. What is the stable identity of one external causal occurrence?
2. How are deterministic child identities derived from that root?
3. How is replay distinguished from a genuinely new but semantically identical occurrence?
4. How is duplicate persistent mutation prevented across process restart?

The governing objective is:

```text
same authoritative causal occurrence
+ same canonical processing coordinates
+ same compatible protocol version
→ same causal identities

different authoritative causal occurrence
even with identical content
→ different RootExternalEpisodeID
```

---

# 2. Executive Verdict

The current repository fails a canonical deterministic causal-identity contract.

```text
R1 FORENSIC VERDICT:
DETERMINISTIC_CAUSAL_IDENTITY_PROTOCOL_MISSING
```

The failure is not one isolated UUID.

There are four distinct failure classes:

```text
F1  Root identity is caller supplied and has no canonical boundary contract.
F2  RFC-12 RepresentationID is random and contaminates downstream operational IDs.
F3  Several downstream IDs depend on local counters, graph time, container length, or incomplete causal inputs.
F4  There is no durable exactly-once persistent-mutation ledger across restart.
```

A fifth integration gap is also confirmed:

```text
F5  SensoryEpisode has no causal identity/provenance fields and feed_to_graph()
    directly mutates CognitiveGraph without a canonical observation transaction.
```

R2 will own the ingress bridge, but R1 must first define the identity protocol that R2 consumes.

---

# 3. Identity Taxonomy

R1 must keep these classes distinct.

## 3.1 Semantic Identity

Identity of durable cognitive/structural meaning.

Examples:

```text
Node.nid
Edge(src,dst)
StructuralAssembly.assembly_id
```

These identities are not external-event identities.

## 3.2 Causal Root Identity

Identity of one authoritative external occurrence.

Canonical name:

```text
RootExternalEpisodeID
```

It represents the source occurrence, not its textual content.

## 3.3 Causal Child Identity

Identity of deterministic descendants of one root:

```text
IngressEventID
ObservationTransactionID
MicroEpisodeID
ParticipationReceiptID
TransientBindingReceiptID
RepresentationID
```

## 3.4 Transaction Identity

Identity of an authorized persistent mutation attempt:

```text
PersistentMutationTransactionID
```

The same authorized mutation replayed for the same root must resolve to the same transaction identity.

## 3.5 Operational Derived Identity

Transient identities used by completion/generation/recurrent orchestration:

```text
SettlingEpochID
PatternCandidateID
ReinstatementProposalID
GenerativeFrameID
OccurrenceID
SurfaceUnitID
SurfaceChunkID
GCEID
ContinuationCommitID
ExpressionReceiptID
WorkID
DeliveryID
```

These may be transient, but any identity that crosses subsystem boundaries or participates in replay signatures must be deterministic from lawful parents.

## 3.6 Local Ephemeral Handle

A process-local handle with no cross-boundary semantic/causal authority.

Example:

```text
ActiveAssembly.activation_id
```

Such handles may remain non-deterministic only if they never become causal authority, persistence keys, replay-dedup keys, or downstream canonical identity inputs.

---

# 4. Root Identity — Critical Finding

A RootExternalEpisodeID MUST NOT be derived from raw content alone.

This is invalid:

```text
RootID = H("the cat is black")
```

because two independent exposures of the exact same sentence are two independent causal events and may lawfully count as two external evidence episodes.

The correct distinction is:

```text
same message transport retry
→ same root

same dataset exposure replay
→ same root

new exposure of identical content
→ new root
```

Therefore R1 requires an **authoritative external occurrence key** supplied by the host/ingress boundary.

Conceptual rule:

```text
RootExternalEpisodeID =
    H(
        protocol_domain,
        boundary_namespace,
        source_occurrence_key
    )
```

The `source_occurrence_key` may be:

```text
API message ID
durable queue/event ID
dataset item + exposure ID
sensor capture-group ID
developer training-event ID
```

A host may generate an opaque occurrence key once, but retries/replays of the same occurrence MUST reuse it.

Content hash may be recorded as a payload fingerprint, but it is not occurrence identity.

---

# 5. Current RFC-16 Root/Event Identity State

`ExternalEventRecord` contains both:

```text
event_id
root_external_episode_id
```

but both are supplied by the caller.

Current ingress deduplication is only:

```text
root_external_episode_id ∈ _processed_episodes
```

and `_processed_episodes` is transient runtime state.

Therefore:

```text
restart
→ _processed_episodes = empty
→ same root can appear novel again
```

This behavior is lawful under closed R0 because RFC-16 operational tables are transient, but it proves that R1 needs a separate cross-restart idempotency mechanism.

A second defect exists: current ingress does not enforce immutable mapping:

```text
EventID → RootID + payload identity
```

so caller-supplied identity collisions are not governed by a canonical R1 contract.

---

# 6. Current RFC-11 Identity Inventory

## 6.1 StructuralAssembly ID — GOOD

RFC-11 already has a correct deterministic structural identity:

```text
assembly_id =
asm_ + SHA256(
    "DGCA_ASM:" + canonical sorted member edges
)
```

This is structural/semantic identity and should remain unchanged.

## 6.2 Formation Candidate Identity — GOOD WITH CONTEXT STORAGE KEY

Formation uses:

```text
candidate_id = canonical_assembly_id(edge_component)
storage_key  = candidate_id + context
```

R0 already made the storage-key persistence exact.

Do not reinterpret this as RootExternalEpisodeID.

## 6.3 Root Votes — IMPORTANT EXISTING CAUSAL CONSUMER

RFC-11 pending evidence stores:

```text
root_votes: set[RootExternalEpisodeID]
```

This is the strongest existing consumer proving why root identity must distinguish:

```text
transport replay
vs
new independent exposure
```

## 6.4 ActiveAssembly.activation_id — RANDOM LOCAL HANDLE

Current code creates:

```text
act_<uuid4[:8]>
```

This is non-deterministic.

Forensics classification:

```text
LOCAL_EPHEMERAL_HANDLE
```

It does not currently define StructuralAssembly identity and SDCR uses `(assembly_id, version)` rather than `activation_id`.

R1 does not need to make this canonical unless later trace/replay requirements promote it into cross-subsystem causal authority.

---

# 7. Current Graph Perceptual Episode Identity

`CognitiveGraph.observe()` and `observe_sequence()` create:

```text
episode = "ep" + graph.t
```

after advancing logical graph time.

This identifier currently serves Law-1 source-coincidence validation:

```text
node_i.episode == node_j.episode != None
```

Forensics classification:

```text
LOCAL_PERCEPTUAL_COINCIDENCE_ID
```

It is NOT a RootExternalEpisodeID.

A single external message may be decomposed by the encoder into multiple `SensoryEpisode` objects, each of which may call `graph.observe()` separately and therefore create several `ep<t>` identities.

R1/R2 must not confuse:

```text
RootExternalEpisodeID       = one independent external occurrence
MicroEpisodeID              = one deterministic decomposition child
graph local episode marker  = one local observation/coincidence execution
```

---

# 8. Encoder / SensoryEpisode Gap

Current `SensoryEpisode` contains:

```text
kind
context
signals
steps
structural_weight
valence
contradictions
```

It contains no:

```text
RootExternalEpisodeID
ObservationTransactionID
MicroEpisodeID
causal parent reference
source occurrence key
```

`MasterSymbolicEncoder.feed_to_graph()` directly invokes:

```text
graph.observe(...)
graph.observe_sequence(...)
```

Therefore the current encoder path cannot propagate a canonical external root into RFC-11/RFC-12.

This is the R2 bridge problem, but R1 must define the identity fields/wrappers R2 will use.

R1 should NOT force cognitive identity fields into the pure encoder itself if a boundary-side observation envelope can carry them cleanly.

---

# 9. RFC-12 Identity Inventory

## 9.1 ParticipationReceipt.receipt_id — CALLER OWNED

The receipt type requires:

```text
receipt_id
```

but RFC-12 does not own a canonical constructor for it.

R1 must define deterministic receipt identity from causal parent + element/slot coordinates.

## 9.2 TBR.binding_id — CALLER OWNED

Likewise:

```text
binding_id
```

is caller supplied.

R1 must define canonical binding identity where TBRs are produced.

## 9.3 RepresentationID — CRITICAL FAILURE

Current RFC-12 creates:

```python
rep_id = f"rep_{uuid.uuid4().hex[:10]}"
```

Thus identical lawful input snapshots receive different RIDs across replay.

This is the primary operational determinism failure.

The RFC-12 object itself explicitly distinguishes:

```text
Operational RID != Semantic Identity
```

That distinction should be preserved.

R1 must therefore NOT replace RID with the content signature alone.

Correct property:

```text
same causal snapshot replay
→ same RID

different root occurrences with identical semantic content
→ different RID

same semantic content
→ may share RepresentationContentSignature
```

---

# 10. Representation Content Signature Is Not Occurrence Identity

RFC-12 already provides a canonical representation content signature based on canonical representation content rather than snapshot identity/time.

This is useful and should remain distinct:

```text
RepresentationContentSignature
≠
RepresentationID
```

The content signature answers:

```text
"Are these representation contents equivalent?"
```

The RID answers:

```text
"Which causal representation occurrence is this?"
```

R1 should use both rather than collapsing them.

---

# 11. RFC-13 Identity Inventory

## 11.1 PatternCandidate IDs — CONDITIONALLY DETERMINISTIC

Current candidate IDs are hashes of local structural data such as:

```text
assembly_id / edge
seed refs
scope
context
```

They do not necessarily include `parent_representation_id`.

Therefore two different causal representations can emit the same candidate ID when their local structural view matches.

Within one RID-scoped cache this may be harmless, but it is not a globally safe causal operational identity.

R1 should domain-separate and parent-scope any cross-boundary candidate identity.

## 11.2 ReinstatementProposal ID — FRAGILE

Current proposal identity includes:

```text
candidate_id
target
scope
graph.t
```

It does not directly bind to the parent RID or settling epoch.

`graph.t` is durable logical state but is not a substitute for causal parent identity.

This can create:

```text
cross-root collision
or
same-root replay instability after unrelated graph-time changes
```

R1 should derive proposal identity from the lawful causal parent:

```text
SettlingEpochID / ParentRID
+ CandidateID
+ Target
+ Scope
```

not from wall/process order or an unrelated local counter.

## 11.3 SettlingEpoch ID — INHERITS RID FAILURE

Current form:

```text
SEID = H(
    root_representation_id,
    graph.t,
    memory_snapshot_ref
)
```

This becomes deterministic only if the RID and causal execution coordinate are deterministic.

A repeated second settling operation over the same RID/state may also need an explicit operation/work coordinate to avoid accidental ID reuse.

## 11.4 Completion ParticipationReceipt IDs

Completion emits:

```text
rec_comp_<proposal_id>
```

This is good conditional composition if ProposalID becomes canonical.

---

# 12. RFC-14 Identity Inventory

## 12.1 GenerativeFrame ID — GOOD CONDITIONAL COMPOSITION

Current FrameID hashes:

```text
parent RepresentationID
anchors
scope
role bindings
```

This is a sound derived pattern, but it inherits RFC-12 RID randomness.

Once RID is canonical, FrameID becomes replay-stable.

## 12.2 LinearizableOccurrence IDs — DETERMINISTIC FROM FRAME

Occurrence IDs are derived from:

```text
FrameID
role
filler / anchor
```

Good conditional identity.

## 12.3 SurfaceUnit ID — WEAK / COLLISION-PRONE

Current unit IDs embed only:

```text
parent_representation_id[:8]
surface position
surface form
```

Truncating the RID to 8 characters is insufficient as a canonical cross-subsystem identity strategy.

R1 should eventually use a domain-separated digest over the full lawful parent identity and source occurrence reference.

## 12.4 SurfaceChunk ID — UNDER-SPECIFIED

Current chunk identity is based on:

```text
parent RepresentationID
rendered text
```

Two chunks with the same text and parent RID but different source alignments or closure semantics can collapse to one ID.

R1 should define whether chunk identity represents:

```text
rendered byte content
or
a causal committed surface object
```

For the latter, alignment/ordered units/closure reason belong in the identity descriptor.

---

# 13. RFC-15 Identity Inventory

## 13.1 GCE ID — ORDER/CONTAINER DEPENDENT

Default current form:

```text
gce_ + H(root_authority_ref, len(_epochs))
```

This is not a stable causal identity.

Changing the number/order of previously created epochs changes the ID.

R1 must replace the canonical path with an explicit causal derivation.

Legacy fallback may remain non-canonical for compatibility, but Agent/R2 canonical runtime must not depend on it.

## 13.2 ExpressiveObligation ID — DETERMINISTIC SEMANTIC-OPERATIONAL

Current form includes:

```text
root_authority_ref
semantic element
participation kind
```

This is stable, but it intentionally collapses identical obligations for the same root/element/kind.

R1 should not change its semantics unless causal tests prove a collision requiring occurrence distinction.

## 13.3 ContinuationCommit ID — PARTLY ORDER DEPENDENT

Current commit ID includes:

```text
epoch_id
representation_id
obligation_id
len(progress_receipt_refs)
```

The progress count is a local sequence proxy.

A stronger causal identity should use a canonical progress-state digest or explicit continuation step coordinate rather than container length alone.

## 13.4 ExpressionReceipt ID — GOOD CONDITIONAL COMPOSITION

Current ExpressionReceipt identity hashes:

```text
root authority
parent RID
chunk ID
source occurrence ref
expressed elements
```

This is a good deterministic pattern once its parents are canonical.

---

# 14. RFC-16 Identity Inventory

## 14.1 External Event / Root IDs — CALLER OWNED

No canonical source-key derivation contract currently exists.

## 14.2 `_processed_episodes` — TRANSIENT DEDUP ONLY

This prevents duplicate roots only during one runtime process.

It cannot provide cross-restart exactly-once learning.

## 14.3 Learning Transaction ID — GOOD FORM, NO COMMIT FIREWALL

Current:

```text
tx_id = H(
    RootExternalEpisodeID,
    learning_owner,
    elements
)
```

This is directionally correct.

However:

```text
process_validated_learning()
```

does not check a durable committed-transaction ledger before mutating cognition.

The graph's reinforcement law is not idempotent:

```text
replay
→ e.n increments again
→ W may increase again
→ context hit counts increase again
```

Therefore deterministic TxID alone is insufficient.

## 14.4 LearningAttribution ID

Current:

```text
attr_<tx_id>
```

Good conditional derivation, but attribution storage is transient.

## 14.5 Delivery ID — GOOD CONDITIONAL DERIVATION

Current:

```text
DeliveryID = H(chunk_id, parent_rid)
```

Retries reuse the same DeliveryID.

That is appropriate transport idempotency behavior.

## 14.6 Task NEW_ROOT — IDENTITY DUPLICATION DEFECT

Current code derives:

```text
new_root_id = H(event.event_id)
```

even though the incoming event already contains:

```text
event.root_external_episode_id
```

R1 should eliminate this competing root namespace in the canonical path.

For an independent event:

```text
NEW_ROOT target
=
validated event.root_external_episode_id
```

## 14.7 Canonical Full Loop Content-Hash Roots — TEST FIXTURE ONLY

The RFC-16 canonical helper derives event/root IDs from `question_text`.

That is acceptable as a deterministic test fixture.

It is NOT a valid production RootExternalEpisodeID algorithm because two independent identical user messages would collapse to one root.

R1 must label this explicitly as test-only deterministic replay scaffolding.

---

# 15. Cross-Restart Exactly-Once Mutation — Proof of Missing State

Consider one authorized Law-2 reinforcement transaction:

```text
Root R
Owner Law2
Elements (A,B)
TxID T
```

Current execution:

```text
apply reinforcement
append transient attribution
```

After checkpoint/restart, RFC-16 transient attribution/dedup state is gone by R0 design.

If the same external occurrence R is replayed:

```text
same TxID T
but no durable record that T committed
→ reinforcement can execute again
```

Because reinforcement modifies:

```text
Edge.W
Edge.n
Edge.ctx_hits
Edge.t_last_update
```

the second application is not equivalent to the first.

Therefore:

```text
Deterministic IDs alone
≠
exactly-once persistent mutation
```

A durable non-cognitive commit memory is required somewhere.

---

# 16. Required New R1 Ownership Class

Forensics concludes that R1 needs a durable provenance mechanism conceptually equivalent to:

```text
DURABLE_CAUSAL_PROVENANCE_STATE
```

Candidate runtime primitive:

```text
CausalCommitLedger
```

It is NOT:

```text
cognitive memory
belief
learning score
semantic knowledge
global reasoning controller
```

Its only authority is idempotency/provenance:

```text
PersistentMutationTransactionID
→ already committed / not committed
```

It must not decide whether a mutation is semantically valid.

Eligibility remains owned by the existing learning/evidence law and, later, R2/R3 authority boundaries.

---

# 17. Why a Durable Ledger Is Architecturally Necessary

The alternatives are worse:

## Store root history in every Edge

Rejected because this contaminates cognitive memory with runtime provenance and duplicates infrastructure across owners.

## Use RFC-16 `_processed_episodes`

Rejected because R0 correctly classifies it as transient orchestration state.

## Infer idempotency from current Edge weight/count

Impossible in general because the same final weight can be produced by multiple lawful histories.

## Use content hashing

Rejected because independent identical observations must remain independent causal episodes.

## Use bounded/prunable replay cache

Cannot guarantee exact cross-restart idempotency after eviction.

Therefore a durable exact commit ledger, or an equivalent external durable idempotency store with the same semantics, is required.

---

# 18. Persistence Integration Requirement

R1 must not silently place causal provenance inside `CognitiveGraph`.

Preferred ownership:

```text
RuntimeRoot
├── CognitiveGraph
├── CausalCommitLedger
└── Lifecycle/Configuration
```

Canonical checkpoint persistence must keep graph state and the durable ledger crash-consistent.

This implies an R1-controlled checkpoint-format extension or an equivalently atomic external store.

The likely clean design is:

```text
checkpoint schema 1.2.x
persistent_state              # unchanged cognitive/structural state
causal_provenance_state       # non-cognitive durable transaction ledger
```

with separate digests/ownership semantics.

This is an R1 integration extension, not a reopening of R0's cognitive-state ownership decision.

The exact schema MUST be frozen in the R1 Formal Specification before implementation.

---

# 19. Canonical Identity Derivation Requirements

R1 should use one domain-separated canonical identity function.

Conceptually:

```text
DGCA_ID(
    protocol_version,
    identity_domain,
    canonical_fields
)
```

with:

```text
canonical UTF-8 encoding
explicit field names
stable ordering for unordered sets/maps
preserved ordering for ordered sequences
length-safe serialization
SHA-256
```

Forbidden identity inputs:

```text
uuid4 for canonical cross-subsystem IDs
Python object repr as canonical serialization
process ID
wall-clock time
filesystem path
unordered dict/set iteration
container length as sole causal coordinate
truncated parent identity without collision analysis
raw content as RootExternalEpisodeID
```

---

# 20. Proposed Canonical Causal Tree

R1 Formal Specification should freeze a tree similar to:

```text
Authoritative External Occurrence Key
            │
            ▼
RootExternalEpisodeID
            │
            ├── IngressEventID
            │
            ├── ObservationTransactionID
            │       │
            │       ├── MicroEpisodeID[0]
            │       │       ├── ParticipationReceiptID...
            │       │       └── TBRID...
            │       │
            │       └── MicroEpisodeID[n]
            │
            ├── RepresentationID(snapshot/microtick)
            │       ├── SettlingEpochID
            │       │       ├── CandidateID
            │       │       └── ProposalID
            │       │
            │       ├── GenerativeFrameID
            │       │       ├── OccurrenceID
            │       │       ├── SurfaceUnitID
            │       │       └── SurfaceChunkID
            │       │
            │       └── GCEID
            │               ├── ContinuationCommitID
            │               └── ExpressionReceiptID
            │
            └── PersistentMutationTransactionID
                    └── CausalCommitLedger entry
```

Not every child must be persisted.

Persistence is determined by ownership, not by whether an ID is deterministic.

---

# 21. Root / Event / Transaction Separation

R1 must freeze these distinctions:

```text
RootExternalEpisodeID
    one independent source occurrence

IngressEventID
    one ingress envelope/sub-event under the root

ObservationTransactionID
    one canonical graph-observation transaction derived from the event

MicroEpisodeID
    one deterministic encoder-decomposition child

PersistentMutationTransactionID
    one authorized persistent write attributable to the root
```

One root may produce many microepisodes.

Those microepisodes MUST NOT become many independent RFC-11 root votes.

---

# 22. Required Root-Identity Contract

R1 should adopt:

```text
same authoritative source_occurrence_key
+ same boundary namespace
→ same RootExternalEpisodeID
```

and:

```text
different source_occurrence_key
→ different RootExternalEpisodeID
```

even when:

```text
payload bytes are identical
```

If an upstream system replays the same real-world occurrence under a brand-new occurrence key, DGCA cannot prove semantic identity without heuristic inference.

R1 must state this limitation explicitly.

Cross-restart dedup guarantees therefore depend on preservation of the authoritative source occurrence key.

---

# 23. Canonical RID Requirement

A RepresentationID should be derived from causal occurrence plus snapshot identity and canonical accepted inputs.

Conceptually:

```text
RID =
DGCA_ID(
    domain="REPRESENTATION",
    root_ref,
    observation_transaction_ref,
    snapshot_or_microtick,
    context,
    canonical accepted ParticipationReceipt IDs,
    canonical accepted TBR IDs,
    active assembly refs
)
```

The existing content signature remains separate.

A later internally generated representation must use its lawful internal causal parent, not pretend to be new external evidence.

---

# 24. Persistent Mutation Transaction Requirement

Conceptually:

```text
TxID =
DGCA_ID(
    domain="PERSISTENT_MUTATION",
    RootExternalEpisodeID,
    learning_owner,
    mutation_kind,
    canonical target refs,
    canonical mutation descriptor
)
```

Commit flow must be equivalent to:

```text
derive TxID
check durable CausalCommitLedger

if committed:
    return IDEMPOTENT_REPLAY
    perform no persistent mutation

if absent:
    execute already-authorized owner mutation
    record TxID as committed
```

The ledger check is not learning authorization.

It only prevents duplicate execution.

---

# 25. Crash Consistency Requirement

Graph mutation and durable transaction provenance must not become persistently separable.

The canonical persisted state after checkpoint must never represent:

```text
mutation persisted
ledger entry absent
```

or:

```text
ledger entry persisted
mutation absent
```

for the same committed transaction.

R1 Formal Specification must define how R1 extends the R0 atomic checkpoint boundary to include durable causal provenance.

---

# 26. Identity Versioning

Every canonical R1 ID derivation must include an identity protocol version/domain separator.

Example conceptual prefix:

```text
DGCA:R1:ID:v1
```

Changing canonical identity formulas in the future must require an explicit protocol version change.

Do not silently reinterpret old IDs.

---

# 27. Collision / Truncation Rule

Current code frequently truncates SHA-256 outputs to 8, 10, 12, or 16 hex characters.

R1 should define one minimum canonical digest width for cross-subsystem causal IDs.

For persistent transaction identity and root identity, 64-bit or shorter truncations are unnecessarily weak.

Recommended candidate for freeze review:

```text
128 bits = 32 hex characters
```

or full SHA-256 where storage cost is acceptable.

Local display aliases may be shorter, but aliases MUST NOT be authoritative identity keys.

---

# 28. Current Identity Classification Ledger

| Current identity | Class | Deterministic now? | Cross-boundary? | R1 action |
|---|---|---:|---:|---|
| `Node.nid` | semantic | yes | yes | preserve |
| `Edge(src,dst)` | semantic | yes | yes | preserve |
| `StructuralAssembly.assembly_id` | structural semantic | yes | yes | preserve |
| Formation `storage_key` | structural evidence key | yes | persisted | preserve |
| RFC11 root vote | causal root ref | caller dependent | persisted | canonicalize upstream |
| `ActiveAssembly.activation_id` | local handle | no (`uuid4`) | limited | may remain local |
| graph `ep<t>` | local perceptual coincidence | yes wrt graph time | no | do not treat as root |
| `ParticipationReceipt.receipt_id` | causal operational | caller supplied | yes | canonical builder |
| `TBR.binding_id` | causal operational | caller supplied | yes | canonical builder |
| `RepresentationID` | causal operational | **no** (`uuid4`) | **yes** | replace canonical path |
| Representation content signature | derived semantic signature | yes | yes | preserve distinct from RID |
| PatternCandidateID | derived operational | partially | yes | parent-scope |
| ProposalID | derived operational | fragile (`graph.t`) | yes | derive from epoch/RID |
| SettlingEpochID | operational epoch | conditional | yes | causal work coordinate |
| FrameID | derived operational | conditional on RID | yes | keep formula family |
| OccurrenceID | derived operational | conditional | yes | keep/strengthen encoding |
| SurfaceUnitID | operational | weak RID truncation | yes | strengthen |
| SurfaceChunkID | operational commit | under-specified | yes | strengthen descriptor |
| GCEID | operational epoch | **order dependent** | yes | replace canonical path |
| ObligationID | semantic-operational | yes | yes | preserve unless collision test |
| ContinuationCommitID | transaction-like operational | partly order dependent | yes | use progress digest/step |
| ExpressionReceiptID | derived operational | good conditional | yes | preserve family |
| RFC16 EventID | causal child | caller supplied | yes | canonical boundary derivation |
| RFC16 RootID | causal root | caller supplied | **yes** | canonical boundary derivation |
| Learning TxID | persistent transaction | deterministic descriptor | **yes** | canonical encode + durable ledger |
| AttributionID | provenance | conditional on TxID | yes | preserve family |
| DeliveryID | transport operational | good conditional | yes | preserve family |
| NEW_ROOT hash(event_id) | competing root identity | yes but wrong ownership | yes | replace with event RootID |

---

# 29. R1 Non-Goals

R1 must NOT:

```text
change Law 1 or Law 2 mathematics
change RFC-11 structural thresholds
change completion ranking
change generation semantics
change normal-user learning authority
build the Encoder→RFC11/RFC12 bridge
redesign CognitiveAgent
resume Audio work
perform the later Text Encoder robustness audit
```

Those belong to later stages.

---

# 30. R1 Required Deliverables

The next R1 architecture document must freeze:

```text
1. Identity taxonomy
2. Authoritative External Occurrence Contract
3. RootExternalEpisodeID formula
4. IngressEventID formula
5. ObservationTransactionID formula
6. MicroEpisodeID formula
7. ParticipationReceiptID / TBRID formulas
8. RepresentationID formula
9. downstream canonical identity inheritance rules
10. PersistentMutationTransactionID formula
11. CausalCommitLedger ownership and persistence
12. crash-consistency integration with R0 checkpoint
13. protocol versioning
14. collision/digest-width policy
15. migration/legacy compatibility
16. exact invariants and adversarial tests
```

---

# 31. Forensic Closure

```text
==================================================
RIC-01 / R1
CAUSAL IDENTITY FORENSICS v1.0

BASELINE:
0f9c397d1bd1fc02a678fa55a9206075efe2bc35

RANDOM RFC12 RID:
CONFIRMED

ROOT ID CANONICAL CONTRACT:
MISSING

CALLER-SUPPLIED RECEIPT/TBR IDS:
CONFIRMED

ORDER/COUNTER DEPENDENT DOWNSTREAM IDS:
CONFIRMED

RFC16 PROCESS-LOCAL ROOT DEDUP:
CONFIRMED

CROSS-RESTART EXACTLY-ONCE MUTATION:
NOT GUARANTEED

DURABLE CAUSAL PROVENANCE MECHANISM:
REQUIRED

CONTENT HASH AS ROOT ID:
REJECTED

STRUCTURAL ASSEMBLY ID:
ALREADY SOUND / PRESERVE

R0:
REMAINS CLOSED

R1 FORMAL SPECIFICATION:
AUTHORIZED TO DRAFT

CODE IMPLEMENTATION:
NOT AUTHORIZED
==================================================
```
