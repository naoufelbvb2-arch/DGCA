# DGCA — RIC-01 / R1
## Deterministic Causal Identity Protocol
### Formal Architecture Specification v1.3 — FROZEN

**Project:** DGCA  
**Program:** `RIC-01 — Canonical Runtime Integration Contract`  
**Stage:** `R1 — Deterministic Causal Identity Protocol`  
**Parent Stage:** `R0 — Persistence & Runtime Lifecycle — CLOSED`  
**Forensic Basis:** `RIC-01-R1-Causal-Identity-Forensics-Report-v1.0.md`  
**Freeze Review Basis:** `RIC-01-R1-Adversarial-Formal-Freeze-Review-v1.0.md`  
**Baseline Commit:** `0f9c397d1bd1fc02a678fa55a9206075efe2bc35`  
**Status:** `FROZEN`  
**Implementation authorization:** `NO — pending frozen implementation master prompt`

---

# 1. Mission

R1 establishes deterministic causal identity and cross-restart idempotency for persistent DGCA mutations without changing cognitive laws.

R1 answers:

```text
What is one independent external occurrence?
How are its children named deterministically?
How is causal replay distinguished from a new identical exposure?
How is a successful persistent mutation prevented from executing twice after restart?
```

The governing property is:

```text
same authoritative occurrence
+ same canonical operation
+ same compatible protocol
→ same causal identities
```

while:

```text
different authoritative occurrence
even with byte-identical content
→ different RootExternalEpisodeID
```

---

# 2. Constitutional Separation

R1 freezes:

```text
SemanticIdentity
!= CausalOccurrenceIdentity
!= PersistentMutationTransactionIdentity
!= ContentSignature
!= LocalEphemeralHandle
```

and:

```text
DeterministicIdentity
does not imply
PersistentCognition
```

No causal provenance record is knowledge, truth, belief, ranking evidence, or learned semantic state.

---

# 3. Identity Classes

R1 defines:

```text
SEMANTIC_IDENTITY
STRUCTURAL_IDENTITY
CAUSAL_ROOT_IDENTITY
CAUSAL_CHILD_IDENTITY
PERSISTENT_TRANSACTION_IDENTITY
DERIVED_OPERATIONAL_IDENTITY
CONTENT_SIGNATURE
LOCAL_EPHEMERAL_HANDLE
```

Identity class ownership is explicit and cannot be silently changed.

---

# 4. Existing Identities Preserved

R1 MUST preserve current semantic/structural identity semantics for:

```text
Node.nid
Edge(src,dst)
StructuralAssembly.assembly_id
StructuralAssembly.version
RFC-11 formation storage-key semantics
```

`canonical_assembly_id()` remains the authoritative assembly structural identity function.

R1 does not retrofit full-length R1 digests into existing frozen assembly IDs.

---

# 5. Authoritative External Occurrence Contract

A `RootExternalEpisodeID` represents one independent authoritative source occurrence.

The host boundary supplies:

```text
ExternalOccurrenceDescriptor
├── boundary_namespace: non-empty immutable string
└── source_occurrence_key: non-empty immutable string
```

Examples of lawful source occurrence keys:

```text
chat-message ID
durable queue event ID
dataset exposure ID
sensor capture-group ID
developer training-event ID
```

The occurrence key identifies occurrence, not content.

`boundary_namespace` and `source_occurrence_key` are trusted host/ingress metadata.

They MUST NOT be taken from ordinary message text or from a user-controlled free-form field that can impersonate another occurrence.

---

# 6. RootExternalEpisodeID

Canonical root:

```text
RootExternalEpisodeID =
DGCA_ID(
    domain="ROOT_EXTERNAL_EPISODE",
    payload={
      "boundary_namespace": boundary_namespace,
      "source_occurrence_key": source_occurrence_key
    }
)
```

Required:

```text
same namespace + same source occurrence key
→ same root

different source occurrence key
→ different root
```

even when content is identical.

Forbidden:

```text
RootExternalEpisodeID = Hash(raw_content)
```

---

# 7. Retry vs Independent Exposure

Canonical distinction:

```text
same transport/message occurrence retried
→ reuse same source_occurrence_key
→ same root

same dataset exposure replayed
→ reuse same exposure key
→ same root

new exposure of identical bytes/content
→ new source_occurrence_key
→ new root
```

R1 exact deduplication depends on upstream preservation of the authoritative occurrence key.

If an upstream source presents the same real-world event under a new occurrence key, R1 does not perform heuristic semantic duplicate detection.

---

# 8. Canonical Identity Function

R1 defines one authoritative derivation:

```text
DGCA_ID(domain, payload)
```

with protocol prefix:

```text
DGCA:R1:ID:v1
```

Canonical input:

```python
canonical_json = json.dumps(
    canonicalized_payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
)
```

Digest:

```text
SHA256(
    UTF8("DGCA:R1:ID:v1")
    || NUL
    || UTF8(domain)
    || NUL
    || UTF8(canonical_json)
)
```

Authoritative R1 identity uses the full 256-bit SHA-256 digest:

```text
64 lowercase hexadecimal characters
```

Readable type prefixes such as `root_`, `evt_`, `rid_`, `tx_` may be prepended.

---

# 9. Canonicalization

Canonical payload conversion:

```text
mapping
→ recursively canonical JSON object

set/frozenset
→ convert each member to its canonical JSON form, then sort lexicographically by canonical UTF-8 JSON bytes

unordered edge-set
→ sorted list of ["src","dst"]

ordered tuple/list
→ order preserved

None
→ JSON null

float
→ finite only
```

Forbidden identity inputs/encodings:

```text
NaN / Infinity
Python repr()
Python hash()
object address
filesystem path
process ID
wall-clock time
unordered iteration
```

---

# 10. Domain Separation

At minimum:

```text
ROOT_EXTERNAL_EPISODE
INGRESS_EVENT
OBSERVATION_TRANSACTION
MICRO_EPISODE
PARTICIPATION_RECEIPT
TRANSIENT_BINDING
REPRESENTATION
SETTLING_EPOCH
PATTERN_CANDIDATE
REINSTATEMENT_PROPOSAL
GENERATIVE_FRAME
LINEARIZABLE_OCCURRENCE
SURFACE_UNIT
SURFACE_CHUNK
GCE
CONTINUATION_COMMIT
EXPRESSION_RECEIPT
INTERNAL_WORK
DELIVERY
PERSISTENT_MUTATION
CAUSAL_PROVENANCE_EPOCH
```

Same payload under different domains MUST produce different IDs.

---

# 11. Short Aliases

Short aliases may be rendered for logs/UI only.

A short/truncated alias MUST NOT be used as:

```text
persistence key
dedup key
transaction key
canonical dictionary key
cross-subsystem identity reference
```

Existing legacy IDs are not automatically promoted to R1 authoritative IDs.

---

# 12. IngressEventID

An external root may contain one or more ingress sub-events.

Descriptor:

```text
IngressEventDescriptor
├── root_external_episode_id
├── source_event_key
├── modality
└── ingress_boundary
```

Canonical:

```text
IngressEventID =
DGCA_ID("INGRESS_EVENT", IngressEventDescriptor)
```

`source_event_key` is immutable within the root.

---

# 13. EventDescriptorDigest

R1 defines:

```text
EventDescriptorDigest =
SHA256(canonical canonical-event-descriptor JSON)
```

The exact payload/content fields of the canonical event descriptor are supplied by the R2 observation bridge contract.

R1 requires that the descriptor bind enough immutable ingress information to detect conflicting reuse of an EventID.

The descriptor digest is provenance, not cognitive evidence.

Canonical formula:

```text
event_descriptor_digest =
SHA256(
    canonical_json(canonical_event_descriptor)
)
```

R2 owns the exact canonical event descriptor fields.

R1 owns the canonicalization and hashing rule.


---

# 14. Observation Protocol Version

Canonical observation identity includes an explicit:

```text
observation_protocol_version
```

A canonical R1 `RuntimeRoot` MUST be constructed with an explicit non-empty observation protocol version.

There is no implicit/default canonical value such as:

```text
UNBOUND
DEFAULT
LEGACY
```

R1-only verification may use an explicit test value such as:

```text
R1_TEST_OBSERVATION_PROTOCOL_V1
```

R2 will freeze the production bridge version.

Migration into an R1 schema-1.2.0 runtime also requires an explicit target observation protocol version.

Changing `observation_protocol_version` does NOT automatically grant an existing RootExternalEpisodeID new independent evidence authority.

Checkpoint/runtime mismatch requires explicit migration/reprocessing policy or fails closed.

---

# 15. ObservationTransactionID

Canonical:

```text
ObservationTransactionID =
DGCA_ID(
    "OBSERVATION_TRANSACTION",
    {
      "root_external_episode_id": ...,
      "ingress_event_id": ...,
      "operation_kind": ...,
      "observation_protocol_version": ...
    }
)
```

R2 owns execution of the observation transaction.

R1 owns its identity rule.

---

# 16. MicroEpisodeID

One observation transaction may deterministically decompose into multiple sensory children.

Canonical:

```text
MicroEpisodeID =
DGCA_ID(
    "MICRO_EPISODE",
    {
      "observation_transaction_id": ...,
      "child_index": zero_based_index,
      "canonical_episode_descriptor": ...
    }
)
```

Encoder output order is semantic if the encoder contract says it is ordered; that order MUST be preserved.

---

# 17. Root Vote Rule

Multiple microepisodes do not become multiple independent external episodes.

For RFC-11:

```text
one RootExternalEpisodeID
→ at most one root vote
per pending formation/growth/merge record
```

Forbidden:

```text
MicroEpisodeID used as independent RFC-11 root vote
```

---

# 18. ParticipationReceiptID

Canonical receipt identity:

```text
ParticipationReceiptID =
DGCA_ID(
    "PARTICIPATION_RECEIPT",
    {
      "micro_episode_id": ...,
      "participation_kind": ...,
      "element_ref": canonical_ref,
      "scope_refs": canonical_scope,
      "slot_index": ...
    }
)
```

Receipt values/support remain operational fields.

R2 may freeze additional descriptor fields only if required to distinguish lawful receipt occurrences without violating R1.

---

# 19. TransientBindingReceiptID

Canonical:

```text
TBRID =
DGCA_ID(
    "TRANSIENT_BINDING",
    {
      "micro_episode_id": ...,
      "binding_scope_id": ...,
      "member_receipt_refs": canonical ordered refs,
      "binding_index": ...
    }
)
```

TBR remains transient and non-cognitive.

---

# 20. Representation Content Signature

Existing RFC-12 content signature is preserved as:

```text
RepresentationContentSignature
```

It answers content equivalence.

It does NOT identify causal occurrence.

Allowed:

```text
same representation content under root A and root B
→ same RepresentationContentSignature
→ different RepresentationIDs
```

---

# 21. OperationalRepresentationDigest

R1 introduces a deterministic operational snapshot digest distinct from the content signature.

It is derived from the accepted operational representation inputs:

```text
context binding
active assembly refs
canonical accepted ParticipationReceipt descriptors
canonical accepted TBR descriptors
participating refs implied/accepted by those records
snapshot coordinate
```

Support/activation/relational-drive values that influence operational RFC-12 state MUST be included in this digest using finite canonical numeric encoding.

This closes the v1.0 freeze-review ambiguity where two operationally different snapshots could share one content signature.

---

# 22. Canonical RepresentationID

Canonical RID:

```text
RepresentationID =
DGCA_ID(
    "REPRESENTATION",
    {
      "causal_parent_ref": ...,
      "snapshot_or_microtick": ...,
      "operational_representation_digest": ...
    }
)
```

`causal_parent_ref` is mandatory on the canonical path.

It may be:

```text
ObservationTransactionID
MicroEpisodeID
explicit internal settling/work child reference
other R1-authorized internal causal parent
```

It MUST NOT be fabricated as a new external root.

---

# 23. RFC-12 Legacy Path

Current random:

```text
rep_<uuid4>
```

may remain temporarily available only as:

```text
LEGACY_NON_CANONICAL
```

for regression compatibility.

R1 implementation MUST add an explicit:

```text
CANONICAL_R1_IDENTITY_MODE
```

or equivalent explicit causal-identity API.

R1 MUST NOT silently switch historical callers to new IDs if doing so alters unrelated baseline behavior.

R2/R3 canonical runtime MUST use R1 canonical mode.

---

# 24. Internal Lineage Rule

Internal reasoning/completion/generation descendants inherit an existing causal root/internal parent.

Forbidden:

```text
internal work
→ source_origin EXTERNAL
→ new external root
```

unless a genuine external boundary occurrence exists.

---

# 25. PatternCandidateID

Canonical candidate identity is representation-scoped:

```text
PatternCandidateID =
DGCA_ID(
    "PATTERN_CANDIDATE",
    {
      "parent_representation_id": ...,
      "candidate_kind": ...,
      "seed_refs": canonical set,
      "structural_refs": canonical set,
      "assembly_refs": canonical set,
      "scope_view": ordered/canonical,
      "context_ref": ...
    }
)
```

Existing ranking/completion semantics are unchanged.

---

# 26. ReinstatementProposalID

Canonical proposal identity:

```text
ReinstatementProposalID =
DGCA_ID(
    "REINSTATEMENT_PROPOSAL",
    {
      "settling_epoch_id": ...,
      "parent_representation_id": ...,
      "candidate_id": ...,
      "target_ref": ...,
      "scope_view": ...,
      "role_ref": ...
    }
)
```

`graph.t` alone is not causal identity authority.

---

# 27. SettlingEpochID

Canonical:

```text
SettlingEpochID =
DGCA_ID(
    "SETTLING_EPOCH",
    {
      "root_representation_id": ...,
      "root_causal_authority_ref": ...,
      "memory_snapshot_ref": ...,
      "work_ref": ...
    }
)
```

`work_ref` distinguishes intentionally separate settling executions over the same representation/state.

Container length is forbidden as canonical epoch authority.

---

# 28. GenerativeFrameID

Canonical frame descriptor retains current semantic ingredients:

```text
parent RepresentationID
anchors
scope
role bindings
```

but uses `DGCA_ID("GENERATIVE_FRAME", ...)`.

No generation decision semantics change.

---

# 29. LinearizableOccurrenceID

Canonical:

```text
LinearizableOccurrenceID =
DGCA_ID(
    "LINEARIZABLE_OCCURRENCE",
    {
      "frame_id": ...,
      "role_authority_ref": ...,
      "filler_ref": ...,
      "occurrence_kind": ...,
      "occurrence_index": ... if required
    }
)
```

Ambiguous string concatenation is not authoritative canonical encoding.

---

# 30. SurfaceUnitID

Canonical:

```text
SurfaceUnitID =
DGCA_ID(
    "SURFACE_UNIT",
    {
      "parent_representation_id": ...,
      "source_occurrence_ref": ...,
      "unit_index": ...,
      "surface_form": ...
    }
)
```

A truncated parent RID is forbidden.

---

# 31. SurfaceChunkID

Canonical chunk identity represents the committed causal surface object:

```text
SurfaceChunkID =
DGCA_ID(
    "SURFACE_CHUNK",
    {
      "parent_representation_id": ...,
      "ordered_surface_unit_ids": ...,
      "rendered_text": ...,
      "closure_reason": ...,
      "origin_lineage": ...
    }
)
```

Same text may lawfully yield different chunk IDs if causal alignment differs.

---

# 32. GCEID

Canonical GCE ID:

```text
GCEID =
DGCA_ID(
    "GCE",
    {
      "root_authority_ref": ...,
      "work_ref": ...,
      "continuation_event_ref": optional
    }
)
```

Forbidden:

```text
len(_epochs) as canonical identity authority
```

---

# 33. ExpressiveObligationID

Current obligation semantics may remain.

Canonical R1 path uses domain-separated canonical encoding of:

```text
root authority
semantic element
role scope / participation kind
lawful alternative branch if any
```

No generation/ranking change is authorized.

---

# 34. ContinuationCommitID

Canonical:

```text
ContinuationCommitID =
DGCA_ID(
    "CONTINUATION_COMMIT",
    {
      "epoch_id": ...,
      "parent_representation_id": ...,
      "obligation_id": ...,
      "progress_snapshot_digest": ...
    }
)
```

The progress digest is computed from the canonical ordered progress receipt refs.

`len(progress_receipt_refs)` alone is forbidden as canonical authority.

---

# 35. ExpressionReceiptID

Canonical descriptor preserves current semantics:

```text
root authority
parent RID
chunk ID
source occurrence ref
canonical expressed elements
```

encoded through `DGCA_ID("EXPRESSION_RECEIPT", ...)`.

---

# 36. InternalWorkID

Canonical:

```text
InternalWorkID =
DGCA_ID(
    "INTERNAL_WORK",
    {
      "root_authority_ref": ...,
      "subsystem_kind": ...,
      "scope_refs": canonical,
      "prerequisite_work_ids": canonical,
      "work_index_or_role": ...
    }
)
```

No global container length is permitted.

---

# 37. DeliveryID

Retry semantics remain:

```text
same committed chunk delivery retry
→ same DeliveryID
```

Canonical:

```text
DeliveryID =
DGCA_ID(
    "DELIVERY",
    {
      "surface_chunk_id": ...,
      "parent_representation_id": ...,
      "delivery_channel_ref": optional
    }
)
```

Retry count does not create a new delivery identity.

---

# 38. NEW_ROOT Rule

For a validated independent external event:

```text
TaskRelationView(
    relation_kind="NEW_ROOT"
).target_root_ref
=
event.root_external_episode_id
```

Canonical path MUST NOT create a competing root by hashing EventID.

---

# 39. Test-Only Synthetic Roots

Content-hash roots used in deterministic RFC tests may remain only as:

```text
TEST_ONLY_SYNTHETIC_ROOT
```

They MUST NOT be used by production canonical ingress.

---

# 40. PersistentMutationCommand

R1 wraps one already-authorized persistent mutation command.

```text
PersistentMutationCommand
├── mutation_owner_ref
├── mutation_kind
├── canonical_targets
├── canonical_mutation_descriptor
└── owner_defined_transaction_scope
```

The command is the unit that must be idempotent under replay.

It is NOT necessarily one edge update or one mathematical Law invocation.

Examples:

```text
one entire canonical observation transaction
one explicit RFC-16 Law-2 reinforcement command
one RFC-11/Law-14 structural participation command
```

A command may internally execute multiple already-frozen law operations.

R1 does not force per-edge transaction granularity.

R2 MUST freeze the transaction boundary used by its canonical observation bridge.

---

# 41. PersistentMutationTransactionID

R1-A01 binding rule:

Persistent transaction identity is root-scoped by default.

```text
TxID =
DGCA_ID(
    "PERSISTENT_MUTATION",
    {
      "root_external_episode_id": ...,
      "mutation_owner_ref": ...,
      "mutation_kind": ...,
      "canonical_targets": ...,
      "canonical_mutation_descriptor": ...,
      "owner_defined_transaction_scope": ...
    }
)
```

`ingress_event_id` is provenance but is NOT part of the default independent-mutation identity.

---

# 42. Owner-Defined Transaction Scope

The owner-defined scope reproduces existing lawful mutation granularity.

It may distinguish multiple genuinely separate owner operations under one root, for example:

```text
different ordered sequence-transition slots
different explicit mutation kinds
different target sets
```

It MUST NOT manufacture multiple independent external evidence votes where the owner law uses RootExternalEpisodeID independence.

Changing transaction scope cannot bypass RFC-11 root-vote deduplication.

`owner_defined_transaction_scope` MUST be deterministically derived by the authorized mutation-owner contract.

It MUST NOT be an arbitrary untrusted ingress/user nonce that can be varied to bypass replay idempotency.

Likewise `canonical_targets` and `canonical_mutation_descriptor` are derived/validated by the authorized owner/bridge contract, not accepted as unchecked user authority.

For R2 canonical sensory learning, the bridge MUST explicitly state whether the entire `graph.observe`/`observe_sequence` operation is one wrapped command; R1 does not decompose it implicitly into per-edge transactions.

---

# 43. Transaction Provenance

Although EventID is not a default TxID input, a committed transaction record retains the causal provenance that produced it.

Minimum:

```text
transaction_id
root_external_episode_id
ingress_event_id
event_descriptor_digest
mutation_owner_ref
mutation_kind
mutation_descriptor_digest
owner_defined_transaction_scope
observation_protocol_version
```

Canonical formula:

```text
mutation_descriptor_digest =
SHA256(
    canonical_json(canonical_mutation_descriptor)
)
```


---

# 44. Durable Causal Provenance State

R1 introduces:

```text
DURABLE_CAUSAL_PROVENANCE_STATE
```

owned by runtime/host infrastructure.

It is not part of `CognitiveGraph`.

Primary component:

```text
CausalCommitLedger
```

The ledger owns only replay/idempotency provenance.

---

# 45. CausalCommitLedger State

Minimum durable state:

```text
committed_transactions:
    TxID -> CausalCommitRecord

committed_event_bindings:
    IngressEventID -> EventBindingRecord

causal_provenance_epoch:
    CausalProvenanceEpoch
```

No ranking/learning score is permitted.


---

# 46. Exact Ledger Retention

Under the `EXACT_R1` contract, committed transaction membership for the active checkpoint lineage is exact.

Forbidden:

```text
TTL deletion of committed TxIDs
LRU deletion
bounded replay-cache eviction
Bloom-filter-only replacement
probabilistic membership
lossy compaction
```

Exact archival or compaction is permitted only if:

```text
TxID membership remains exact
descriptor-conflict detection remains exact
restore/replay semantics remain exact
```

A future bounded-history mode must use a different explicit contract and MUST NOT claim R1 exact cross-restart idempotency.

---

# 47. EventBindingRecord

For every ingress event that contributes to a committed persistent transaction, persist:

```text
ingress_event_id
root_external_episode_id
event_descriptor_digest
observation_protocol_version
```

Required:

```text
same IngressEventID + same descriptor
→ replay-compatible

same IngressEventID + different descriptor
→ FAIL CLOSED
```

Events that never contribute to persistent mutation need not be retained durably by R1.

---

# 48. CausalCommitRecord

Minimum:

```text
transaction_id
root_external_episode_id
ingress_event_id
event_descriptor_digest
mutation_owner_ref
mutation_kind
mutation_descriptor_digest
owner_defined_transaction_scope
observation_protocol_version
```

Every ledger transaction record represents a successfully completed persistent owner mutation.

There is no durable `IN_PROGRESS` transaction state.

---

# 49. Transaction Collision Rule

If ledger already contains TxID:

```text
same canonical transaction descriptor digest
+ compatible provenance binding
→ IDEMPOTENT_REPLAY

different descriptor or conflicting provenance
→ FAIL CLOSED
```

A TxID collision never silently aliases two operations.

---

# 50. Exactly-Once Persistent-Effect Rule

Canonical healthy-runtime flow:

```text
1. require runtime_health == HEALTHY and canonical_lineage_state == VALID
2. existing owner/evidence authority authorizes a PersistentMutationCommand
3. derive Root/Event provenance
4. validate/stage event binding
5. derive canonical TxID for the whole authorized command
6. check committed ledger

if committed:
    return IDEMPOTENT_REPLAY
    ΔPersistentState = 0

if absent:
    enter lifecycle MUTATING
    execute existing owner mutation
    on owner success:
        append CausalCommitRecord
    exit MUTATING
```

The ledger does NOT grant learning authority.

---

# 51. Owner Failure Semantics

R1 does not claim rollback for arbitrary current in-place mutators.

If owner mutation raises before successful completion:

```text
no CausalCommitRecord is written
runtime enters MUTATION_FAILED / FAIL_STOP state
canonical save is forbidden
further canonical persistent mutation is forbidden
```

Recovery requires discarding/restoring from the last valid checkpoint or another explicit host recovery path.

If graph mutation succeeded but ledger append itself fails, the same fail-stop rule applies.

This prevents a partially failed in-memory runtime from being checkpointed as a valid committed state.

---

# 52. Runtime Health State

R1 introduces non-cognitive transient runtime health:

```text
HEALTHY
MUTATION_FAILED
```

It is not persistent cognition.

Cold restore of a valid checkpoint creates:

```text
HEALTHY
```

A `MUTATION_FAILED` runtime cannot use canonical R1 save or canonical persistent mutation APIs.

---

# 53. Crash Semantics

DGCA persistent cognition is checkpoint-based.

If the process crashes before a post-mutation checkpoint:

```text
in-memory graph mutation is lost
in-memory committed ledger record is lost
restart loads prior checkpoint
replay may execute once again
```

This is correct because the prior mutation did not survive persistently.

For every persisted checkpoint, graph state and ledger state are atomically bundled.

Thus R1 guarantees exactly-once **persisted effect** for successfully committed R1 transactions whose authoritative occurrence key is preserved.

---

# 54. RuntimeRoot Ownership

Candidate canonical runtime:

```text
CanonicalR1RuntimeRoot
├── graph/internal cognitive runtime
├── causal_commit_ledger: CausalCommitLedger
├── causal_runtime_health
├── canonical_lineage_state
├── explicit observation_protocol_version
├── runtime configuration
└── R0 lifecycle guard
```

The ledger and health state are infrastructure, not cognition.

---

# 55. Canonical vs Legacy Runtime

R1 freezes:

```text
CANONICAL_R1
    deterministic causal lineage
    durable persistent-command idempotency
    R1 checkpoint bundle

LEGACY_NON_CANONICAL
    historical direct mutation APIs
    NO_R1_IDEMPOTENCY_GUARANTEE
```

The exact R1 replay guarantee applies only to persistent writes executed through the canonical R1 mutation wrapper.

Legacy calls such as direct:

```text
graph.observe(...)
graph.observe_sequence(...)
RFC16.process_validated_learning(...)
other low-level persistent mutators
```

remain outside the R1 exactly-once guarantee unless explicitly wrapped by the canonical R1 transaction API.

R1 implementation may preserve legacy defaults to conserve baseline.

R2/R3 production canonical paths MUST route every persistent write through `CANONICAL_R1`.

---


## Canonical lineage validity

A canonical R1 runtime also owns transient non-cognitive:

```text
canonical_lineage_state =
    VALID
    INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
```

New canonical runtime construction and valid canonical restore initialize:

```text
VALID
```

Production canonical APIs MUST NOT expose an unguarded public persistent-write path.

If an explicit legacy/unsafe persistent mutation escape hatch is invoked through the canonical runtime:

```text
canonical_lineage_state =
    INVALIDATED_BY_UNTRACKED_PERSISTENT_MUTATION
```

An invalidated runtime MUST fail closed on:

```text
canonical R1 save
canonical R1 persistent mutation command
```

Recovery requires constructing/restoring a new valid canonical runtime.

Deliberate direct access to private/internal mutable graph objects outside the canonical API contract receives no R1 guarantee.

R1 does not require a full-graph digest after every training transaction merely to police deliberate private-API bypass.

# 56. Checkpoint Schema Extension

R1 canonical runtime checkpoint:

```text
checkpoint_schema_version = "1.2.0"
runtime_contract_version = "1.2.0"
cognitive_semantics_version = "1.0"
causal_identity_protocol_version = "1.0"
```

R1 does not justify a cognitive semantics version change.

---

# 57. Observation Compatibility

Checkpoint schema also records:

```text
observation_protocol_version
```

The running canonical runtime must match it unless an explicit migration/reprocessing policy exists.

A bridge-version change cannot silently make an old root independent evidence again.

---

# 58. CausalProvenanceEpoch

Durable:

```text
CausalProvenanceEpoch
├── epoch_id
├── history_status
└── base_state_digest
```

For native R1 creation:

```text
history_status = R1_TRACKED
```

For migration from pre-R1 checkpoints:

```text
history_status = PRE_R1_HISTORY_UNAVAILABLE
```

The epoch is provenance coverage metadata.

It is NOT included in RootExternalEpisodeID or TxID derivation.

---

# 59. Deterministic Provenance Epoch ID

Migration/native initialization derives epoch ID deterministically:

```text
epoch_id =
DGCA_ID(
    "CAUSAL_PROVENANCE_EPOCH",
    {
      "base_state_digest": checkpoint_state_digest,
      "source_schema": ...,
      "causal_identity_protocol_version": "1.0"
    }
)
```

No random epoch identifier is required.

---

# 60. Pre-R1 Guarantee Boundary

Migration from a pre-R1 checkpoint creates an empty ledger.

Therefore:

```text
R1 exactly-once replay guarantee
applies to persistent transactions first committed
under an R1-tracked provenance epoch.
```

A pre-R1 event replayed after migration may execute because its historical transaction was never recorded.

This limitation MUST be disclosed in migration diagnostics.

No pre-R1 causal history is fabricated.

---

# 61. Checkpoint 1.2.0 Structure

```text
DGCA_COGNITIVE_CHECKPOINT
│
├── schema
│   ├── checkpoint_schema_version
│   ├── runtime_contract_version
│   ├── cognitive_semantics_version
│   ├── causal_identity_protocol_version
│   └── observation_protocol_version
│
├── compatibility
│   ├── region_schema_digest
│   ├── active_law_digest
│   ├── assembly_policy_digest
│   ├── combined_semantics_digest
│   ├── causal_identity_protocol_digest
│   └── observation_protocol_digest
│
├── persistent_state
│   └── [R0 payload unchanged]
│
├── causal_provenance_state
│   ├── causal_provenance_epoch
│   ├── committed_event_bindings
│   └── committed_transactions
│
├── integrity
│   ├── checkpoint_state_digest
│   ├── causal_provenance_digest
│   └── checkpoint_bundle_digest
│
└── diagnostic_metadata
```

---

# 62. Cognitive Digest Conservation

R0:

```text
checkpoint_state_digest
```

continues to hash only the R0 persistent cognitive/structural/internal/hypothesis state.

R1 causal provenance MUST NOT enter that digest.

Therefore a ledger-only change:

```text
checkpoint_state_digest unchanged
causal_provenance_digest changed
checkpoint_bundle_digest changed
```

---

# 63. Causal Provenance Digest

Canonical:

```text
causal_provenance_digest =
SHA256(
    canonical_json(causal_provenance_state)
)
```

using the same finite/deterministic canonicalization rules.

Ledger order is canonical by authoritative identity key.

---

# 64. Checkpoint Bundle Digest

R1-A07 binding formula:

```text
checkpoint_bundle_digest =
SHA256(
    canonical_json({
      "checkpoint_state_digest": ...,
      "causal_provenance_digest": ...,
      "combined_semantics_digest": ...,
      "causal_identity_protocol_digest": ...,
      "observation_protocol_digest": ...,
      "causal_provenance_epoch": ...
    })
)
```

No informal string concatenation is authoritative.

---

# 65. Atomic Persistence

R0 atomic same-directory checkpoint commit is extended to the 1.2.0 bundle.

For every successfully persisted R1 transaction, checkpoint state must never contain:

```text
mutation persisted / TxID absent
```

or:

```text
TxID persisted / mutation absent
```

because graph and ledger are serialized from one `RuntimeRoot` at one lifecycle barrier into one atomic file replacement.

---

# 66. Save Barrier

Canonical R1 save requires:

```text
lifecycle == IDLE
runtime_health == HEALTHY
canonical_lineage_state == VALID
```

It serializes graph state and causal provenance under one barrier.

`MUTATION_FAILED` runtime save MUST fail closed.

---

# 67. Restore

Canonical 1.2.0 restore constructs:

```text
NEW CognitiveGraph
NEW CausalCommitLedger
NEW RuntimeRoot
HEALTHY runtime state
fresh RFC12–RFC16 engines
```

and atomically swaps the authoritative root under R0 `RESTORING`.

No old ledger/engine object crosses the restore boundary.

---

# 68. Migration 1.1.1 → 1.2.0

Migration preserves R0 `persistent_state` exactly.

Creates:

```text
committed_event_bindings = {}
committed_transactions = {}
causal_provenance_epoch.history_status =
    PRE_R1_HISTORY_UNAVAILABLE
```

Migration report MUST state:

```text
Pre-R1 persistent mutation causal commit history
was not recorded and cannot be reconstructed.
```

---

# 69. Legacy Migration Chain

Supported chain:

```text
1.0
→ existing lawful R0 migration
→ 1.1.1 state
→ 1.2.0 R1 bundle

1.1
→ existing lawful R0 migration
→ 1.1.1 state
→ 1.2.0 R1 bundle
```

No unavailable causal history may be invented.

---

# 70. Identity Protocol Compatibility

Checkpoint includes deterministic:

```text
causal_identity_protocol_digest
```

over canonical R1 identity protocol constants/domain registry/version.

Mismatch:

```text
explicit supported migration
or
FAIL CLOSED
```

Identity formulas cannot change silently.

---


## Exact causal identity protocol digest payload

Freeze:

```text
causal_identity_protocol_digest =
SHA256(
    canonical_json({
      "protocol_version": "1.0",
      "protocol_prefix": "DGCA:R1:ID:v1",
      "hash_algorithm": "SHA-256",
      "authoritative_digest_hex_chars": 64,
      "canonical_json": {
        "sort_keys": true,
        "separators": [",", ":"],
        "ensure_ascii": false,
        "allow_nan": false
      },
      "domain_registry": [
        "CAUSAL_PROVENANCE_EPOCH",
        "CONTINUATION_COMMIT",
        "DELIVERY",
        "EXPRESSION_RECEIPT",
        "GCE",
        "GENERATIVE_FRAME",
        "INGRESS_EVENT",
        "INTERNAL_WORK",
        "LINEARIZABLE_OCCURRENCE",
        "MICRO_EPISODE",
        "OBSERVATION_TRANSACTION",
        "PARTICIPATION_RECEIPT",
        "PATTERN_CANDIDATE",
        "PERSISTENT_MUTATION",
        "REINSTATEMENT_PROPOSAL",
        "REPRESENTATION",
        "ROOT_EXTERNAL_EPISODE",
        "SETTLING_EPOCH",
        "SURFACE_CHUNK",
        "SURFACE_UNIT",
        "TRANSIENT_BINDING"
      ],
      "canonicalization_profile": {
        "mappings": "recursive-json-object",
        "sets_frozensets": "canonical-sorted-list",
        "unordered_edge_sets": "canonical-sorted-[src,dst]-list",
        "ordered_list_tuple": "preserve-order",
        "strings": "exact-unicode-codepoint-sequence-no-implicit-normalization",
        "none": "json-null",
        "floats": "finite-json-number-only"
      }
    })
)
```

The authoritative domain registry is the literal list embedded above and MUST match Section 10. The canonicalization profile is also compatibility-bound.

Changing any of these fields requires explicit identity-protocol compatibility governance.

# 71. Observation Protocol Compatibility

Checkpoint includes:

```text
observation_protocol_version
observation_protocol_digest
```

A canonical R1 persistent transaction record also retains the observation protocol version that generated its event/mutation provenance.

Changing observation protocol requires explicit compatibility/migration governance.

It does not reset RFC-11 root-vote identity.

---


## Exact observation protocol digest payload

Freeze:

```text
observation_protocol_digest =
SHA256(
    canonical_json({
      "observation_protocol_version": <explicit non-empty runtime value>
    })
)
```

There is no implicit canonical observation protocol version.

# 72. Committed Event Binding

Before first persistent transaction for an ingress event:

```text
if EventID absent:
    stage binding for commit

if EventID present + same descriptor:
    replay-compatible

if EventID present + different descriptor:
    FAIL CLOSED
```

Binding and transaction record become durable only after owner mutation succeeds.

If mutation fails, staged binding is not committed.

---

# 73. Root-Level vs Event-Level Dedup

Event provenance and persistent mutation identity are separate.

Default:

```text
TxID root-scoped
EventID retained as provenance
```

This prevents multisensory/sub-event decomposition from manufacturing repeated persistent mutations for the same root/owner/target operation.

An owner-specific scope may lawfully create multiple root-contained transactions only when existing frozen owner semantics require it.

---

# 74. Existing Graph Episode Marker

Current:

```text
ep<t>
```

remains a local perceptual coincidence handle for existing Law-1 source validation.

It is NOT RootExternalEpisodeID.

R2 may pass MicroEpisode/Observation identity into an adapted canonical observation envelope, but R1 does not redefine Law-1 mathematics.

---

# 75. ActiveAssembly UUID Boundary

Current random `ActiveAssembly.activation_id` may remain:

```text
LOCAL_EPHEMERAL_HANDLE
```

provided it never becomes:

```text
persistent key
root identity
TxID input
canonical cross-subsystem parent
```

If a later canonical API requires an activation ID to cross a subsystem boundary, it must receive an R1 deterministic child identity.

---

# 76. QuantityNormalizer Instance Counter Boundary

Current process-order `inst:` counter is classified:

```text
ENCODER_LOCAL_INSTANCE_ID
```

R1 does not promote it into causal identity.

R2/Text-Encoder audit must not use it as Root/Event/Observation/MicroEpisode identity.

---

# 77. Mutation Owners

R1 transaction infrastructure can wrap only explicitly authorized existing persistent owners.

Initial target ownership classes include:

```text
Law1_HebbianCreation
Law2_HebbianReinforcement
Law14_AssemblyParticipation
```

R1 does not authorize these owners for ordinary users.

R2/R3 define who may invoke persistent learning.

---

# 78. No Hidden Learning Authority

A valid:

```text
RootExternalEpisodeID
IngressEventID
TxID
```

does NOT make an event eligible to learn.

Required logical ordering:

```text
external authority/evidence eligibility
→ owner authorization
→ R1 transaction identity/idempotency
→ persistent mutation
```

Never:

```text
valid ID
→ learning permission
```

---

# 79. R1 Invariants

```text
R1-I01  Same authoritative occurrence descriptor yields same RootExternalEpisodeID.
R1-I02  Different occurrence keys yield different roots despite identical content.
R1-I03  Root identity never derives from content alone.
R1-I04  DGCA_ID is deterministic and domain-separated.
R1-I05  Authoritative R1 IDs use full SHA-256 digest.
R1-I06  Ordered identity fields preserve order; unordered fields canonicalize.
R1-I07  One root may own many microepisodes without multiplying RFC-11 independent votes.
R1-I08  Canonical receipt IDs replay exactly.
R1-I09  Canonical TBR IDs replay exactly.
R1-I10  OperationalRepresentationDigest binds accepted operational receipt/TBR state.
R1-I11  Same causal snapshot replay yields same RID.
R1-I12  Same content under different roots may share content signature but not RID.
R1-I13  Canonical RID path contains no random UUID.
R1-I14  Candidate/proposal IDs are parent-causally scoped.
R1-I15  Canonical GCE ID is independent of unrelated epoch count.
R1-I16  SurfaceUnit ID uses full canonical parent identity.
R1-I17  NEW_ROOT reuses validated RootExternalEpisodeID.
R1-I18  Default persistent TxID is root-scoped, not event-scoped.
R1-I19  Same lawful persistent operation replay resolves to same TxID.
R1-I20  Same TxID committed replay causes zero persistent mutation.
R1-I21  New independent identical exposure may produce a new lawful transaction.
R1-I22  Conflicting EventID descriptor reuse fails closed.
R1-I23  Durable causal ledger is non-cognitive.
R1-I24  Ledger state never authorizes or ranks cognition.
R1-I25  Owner failure writes no committed ledger record.
R1-I26  Owner/ledger partial failure places canonical runtime in fail-stop state.
R1-I27  Fail-stop runtime cannot canonical-save.
R1-I28  R0 cognitive state digest excludes causal provenance.
R1-I29  Causal provenance and graph state persist atomically in one bundle.
R1-I30  Bundle digest binds graph, provenance, semantics, identity protocol, observation protocol, and provenance epoch.
R1-I31  Pre-R1 migration never fabricates commit history.
R1-I32  Pre-R1 exactly-once limitation is explicitly disclosed.
R1-I33  Causal identity protocol mismatch fails closed.
R1-I34  Observation protocol mismatch fails closed absent explicit migration.
R1-I35  Canonical R1 mode is additive; legacy compatibility remains explicitly non-canonical.
R1-I36  Baseline cognitive signature remains unchanged.
R1-I37  Canonical R1 runtime requires explicit non-empty observation_protocol_version.
R1-I38  R1 exact idempotency guarantee applies only to canonical wrapped persistent commands.
R1-I39  Exact ledger membership is never lost through TTL/LRU/probabilistic pruning.
R1-I40  Identity and observation protocol digests use the exact frozen canonical payloads.
R1-I41  Transaction granularity is owner-command scoped and does not force per-edge law transactions.
R1-I42  Canonical runtime lineage begins VALID after construction/restore.
R1-I43  Explicit unsafe/legacy persistent mutation invalidates canonical lineage.
R1-I44  Invalidated canonical lineage cannot canonical-save or execute canonical persistent commands.
R1-I45  Event descriptor digest uses the frozen canonical SHA-256 formula.
R1-I46  Mutation descriptor digest uses the frozen canonical SHA-256 formula.
R1-I47  Protocol digest binds the literal domain registry and canonicalization profile.
R1-I48  Root source-occurrence metadata is host-authoritative, not message-text authority.
R1-I49  Owner-defined transaction scope is deterministic owner-derived state, not an untrusted replay-bypass nonce.
```

---

# 80. Acceptance Tests

```text
R1-T01 same occurrence descriptor → same root across fresh processes
R1-T02 same content + different occurrence keys → different roots
R1-T03 same occurrence retry → same root
R1-T04 different boundary namespaces → different roots
R1-T05 empty occurrence key/namespace rejected
R1-T06 identity domain separation
R1-T07 unordered payload insertion/order independence
R1-T08 ordered child order changes identity where order is semantic
R1-T09 non-finite canonical payload rejected
R1-T10 full authoritative digest width enforced
R1-T11 deterministic ParticipationReceiptID replay
R1-T12 deterministic TBRID replay
R1-T13 operational digest changes when support/accepted operational receipt state changes
R1-T14 same causal snapshot RID exact across fresh engines
R1-T15 same content/different root: same content signature allowed, different RID
R1-T16 canonical RID API contains no uuid/random input
R1-T17 legacy random RID path remains explicitly non-canonical
R1-T18 candidate identity isolated by parent RID
R1-T19 proposal identity isolated by epoch/RID
R1-T20 frame/occurrence replay stable under canonical RID
R1-T21 GCE ID unaffected by unrelated epoch creation
R1-T22 continuation commit uses progress digest rather than count-only identity
R1-T23 full-parent SurfaceUnit identity collision regression
R1-T24 same committed chunk retry → same DeliveryID
R1-T25 NEW_ROOT target equals event root
R1-T26 same root + same owner/target mutation from different ingress sub-events → same default TxID
R1-T27 owner-defined lawful transaction scope can distinguish separate root-contained operations
R1-T28 first authorized Tx mutates once and records event binding + commit
R1-T29 same Tx replay same process → zero persistent delta
R1-T30 same Tx replay after checkpoint/restart → zero persistent delta
R1-T31 identical content under new root → independent lawful TxID
R1-T32 same EventID + changed descriptor → fail closed
R1-T33 TxID collision/conflicting descriptor → fail closed
R1-T34 ledger does not change checkpoint_state_digest
R1-T35 causal provenance digest deterministic
R1-T36 checkpoint bundle digest deterministic structured binding
R1-T37 graph + ledger 1.2.0 round-trip
R1-T38 ledger malformed duplicate/corrupt identity fails closed
R1-T39 mutation callback raises before success → no commit + runtime fail-stop
R1-T40 ledger append failure after owner success → runtime fail-stop
R1-T41 fail-stop runtime canonical save rejected
R1-T42 restore from last valid checkpoint returns HEALTHY
R1-T43 1.1.1 migration → empty ledger + PRE_R1_HISTORY_UNAVAILABLE
R1-T44 migrated pre-R1 limitation present in report
R1-T45 1.0/1.1 migration chain remains valid
R1-T46 causal identity protocol mismatch fails closed
R1-T47 observation protocol mismatch fails closed
R1-T48 observation protocol change does not create new RFC-11 root vote authority
R1-T49 RFC-11 pending root-vote persistence behavior conserved
R1-T50 RFC-12–RFC-16 transient cold-restart semantics conserved
R1-T51 all R0/C01/C02/C03 suites pass
R1-T52 full repository regression passes
R1-T53 baseline cognitive signature unchanged
R1-T54 canonical RuntimeRoot without explicit observation protocol version fails closed
R1-T55 schema-1.2.0 migration without explicit target observation protocol version fails closed
R1-T56 canonical whole-command replay dedups all persistent effects inside one wrapped command
R1-T57 legacy direct mutation path is explicitly outside R1 idempotency guarantee
R1-T58 exact ledger rejects/does not expose lossy pruning in EXACT_R1 mode
R1-T59 causal identity protocol digest matches exact frozen payload
R1-T60 observation protocol digest matches exact frozen payload
R1-T61 new/restored canonical runtime lineage is VALID
R1-T62 explicit unsafe legacy persistent mutation invalidates canonical lineage
R1-T63 invalidated lineage canonical save fails closed
R1-T64 invalidated lineage canonical persistent command fails closed
R1-T65 event descriptor digest exact canonical formula
R1-T66 mutation descriptor digest exact canonical formula
R1-T67 identity protocol digest changes if literal domain registry/profile is altered
R1-T68 untrusted raw message content cannot directly choose RootExternalEpisodeID source occurrence authority
R1-T69 varying an untrusted caller nonce cannot create a distinct canonical transaction scope
```

---

# 81. Mandatory Adversarial Scenarios

```text
A. identical user text sent as two independent messages
   → distinct roots

B. exact retry of one message
   → same root

C. one root split into several modalities/microepisodes
   → one RFC-11 independent root vote

D. same root/same mutation reached through two ingress sub-events
   → one default persistent Tx

E. replay committed Tx after restart
   → zero second persistent delta

F. reuse EventID with modified payload descriptor
   → fail closed

G. owner mutates partially then raises
   → no commit record
   → runtime fail-stop
   → save prohibited

H. unrelated GCE creation order changed
   → target canonical GCEID unchanged

I. same representation content under different roots
   → content signatures may match
   → RIDs differ

J. migrated pre-R1 checkpoint replays old historical event
   → system does NOT claim prior-history dedup guarantee
   → limitation is explicit

K. observation protocol version changes
   → checkpoint/runtime mismatch fail closed
   → no automatic new evidence vote
```

---

# 82. Forbidden Mechanisms

R1 MUST NOT:

```text
use content hash as production RootExternalEpisodeID
use uuid/randomness for canonical R1 IDs
use process/global container length as canonical identity authority
use truncated aliases as authoritative keys
persist causal provenance inside CognitiveGraph
mix causal ledger into cognitive state digest
use ledger as learning/evidence authorization
create multiple RFC-11 independent votes from microepisodes
silently reprocess old roots after observation protocol changes
fabricate pre-R1 causal commit history
claim rollback of arbitrary current owner mutation
checkpoint a mutation-failed runtime
lossily prune committed causal provenance while claiming EXACT_R1
produce a canonical R1 checkpoint after canonical_lineage_state is invalidated
change Law mathematics
change ranking/generation cognition
start R2/R3
resume Audio
```

---

# 83. Explicit Non-Goals

R1 does not implement:

```text
ordinary-user vs developer learning permissions
the full Encoder→Observation→RFC11→RFC12 bridge
CognitiveAgent v2
chat UX
English Encoder robustness fixes
Audio work
new cognitive laws
semantic duplicate inference
distributed multi-writer transaction consensus
```

---

# 84. Release Gates

R1 implementation may close only if:

```text
Canonical Root Identity:
PASS

Independent Identical Exposure Separation:
PASS

Canonical Child Identity:
PASS

Canonical RID:
PASS

Downstream Canonical Identity:
PASS

Root-Scoped Persistent Tx Identity:
PASS

Durable Event Binding:
PASS

Cross-Restart Idempotency:
PASS

Mutation Failure Fail-Stop:
PASS

Causal Ledger Non-Cognitive Isolation:
PASS

Checkpoint 1.2.0 Bundle:
PASS

R0 Cognitive Digest Conservation:
PASS

Migration Disclosure:
PASS

Identity Protocol Firewall:
PASS

Observation Protocol Firewall:
PASS

Legacy/Canonical Mode Separation:
PASS

Explicit Observation Protocol Binding:
PASS

Persistent Command Granularity:
PASS

Exact Ledger Retention:
PASS

Exact Protocol Digest Payloads:
PASS

Canonical Lineage Validity:
PASS

Descriptor Digest Formulas:
PASS

R0/C01/C02/C03 Regression:
100% PASS

Full Regression:
100% PASS

Cognitive Baseline Signature:
UNCHANGED
```

---

# 85. Formal Candidate State

```text
==================================================
DGCA — RIC-01 / R1

CONTRACT:
Deterministic Causal Identity Protocol

SPECIFICATION:
v1.3 FROZEN

ROOT IDENTITY:
AUTHORITATIVE OCCURRENCE-BASED

CONTENT-HASH ROOT:
FORBIDDEN

CANONICAL ID DIGEST:
FULL SHA-256

REPRESENTATION CONTENT SIGNATURE:
SEPARATE FROM RID

CANONICAL RID:
CAUSAL + OPERATIONAL SNAPSHOT-BOUND

PERSISTENT TxID:
ROOT-SCOPED BY DEFAULT

INGRESS EVENT:
PROVENANCE, NOT DEFAULT INDEPENDENT TX AUTHORITY

DURABLE EVENT BINDING:
REQUIRED FOR PERSISTENT-WRITE EVENTS

CAUSAL COMMIT LEDGER:
REQUIRED

LEDGER OWNERSHIP:
NON-COGNITIVE RUNTIME PROVENANCE

MUTATION FAILURE:
FAIL-STOP, NO FALSE ROLLBACK CLAIM

PRE-R1 HISTORY:
UNAVAILABLE / EXPLICITLY DISCLOSED

CAUSAL PROVENANCE EPOCH:
REQUIRED

CHECKPOINT:
1.2.0 CANDIDATE

COGNITIVE SEMANTICS VERSION:
1.0

OBSERVATION PROTOCOL COMPATIBILITY:
MANDATORY

LEGACY APIs:
MAY REMAIN EXPLICITLY NON-CANONICAL

R0:
REMAINS CLOSED

R2/R3:
NOT AUTHORIZED

IMPLEMENTATION:
NOT AUTHORIZED YET
==================================================
```

---

# 86. Binding Review Closure

This v1.2 candidate incorporates all amendments from:

```text
R1-A01 .. R1-A08
R1-B01 .. R1-B05
R1-C01 .. R1-C02
```

No amendment changes cognitive law mathematics.

---

# 87. Frozen State

The Final Closure Freeze Review v1.3 found:

```text
fatal architectural defects = 0
remaining freeze blockers = 0
formal freeze = authorized
```

Therefore the authoritative R1 architecture state is:

```text
RIC-01 / R1
Deterministic Causal Identity Protocol
v1.3 — FROZEN
```

The next permitted artifact is:

```text
RIC-01 / R1
Strict Implementation & Verification Master Prompt
```

No code implementation is authorized until that master prompt is itself frozen.
