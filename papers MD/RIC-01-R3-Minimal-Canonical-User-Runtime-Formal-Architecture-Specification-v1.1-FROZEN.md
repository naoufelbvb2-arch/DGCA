# DGCA — RIC-01 / R3 Minimal
## Minimal Canonical User Runtime
### Formal Architecture Specification v1.1 — FROZEN

**Program:** `RIC-01 — Canonical Runtime Integration Contract`  
**Stage:** `R3 — Minimal Canonical User Runtime`  
**Baseline:** `c04c0820ef3cb329008a6bc7be0d9c4fd8754403`  
**Status:** `FROZEN — IMPLEMENTATION NOT YET AUTHORIZED`  
**R0:** `CLOSED`  
**R1:** `CLOSED`  
**R2:** `CLOSED`  
**RFC-15 in R3-Min:** `DEFERRED`  
**RFC-16 full-loop ingress in R3-Min:** `NOT USED`  
**Audio:** `DEFERRED / OUT OF SCOPE`  
**Vision modification:** `OUT OF SCOPE`  
**Text Encoder redesign:** `OUT OF SCOPE; use current frozen/current encoder contract`  
**New cognitive law:** `NONE`

---

# 0. Constitutional Goal

R3-Min exists to make DGCA usable as one simple, canonical, non-learning text agent.

The ordinary user contract is:

```python
from dgca import CognitiveAgent

agent = CognitiveAgent()
reply = agent.chat("Why does the ocean become warm?")
print(reply)
```

Optional shorthand:

```python
reply = agent("Why does the ocean become warm?")
```

A trained canonical checkpoint may be loaded as:

```python
agent = CognitiveAgent.from_checkpoint("brain.json")
reply = agent.chat("Why does the ocean become warm?")
```

The user must not select:
- retrieval mode;
- reasoning mode;
- generation mode;
- learning mode;
- RFC number;
- cognitive subsystem.

The user provides text. DGCA performs one lawful canonical cognitive path.

---

# 1. R3-Min Scope

R3-Min contains only the minimum runtime needed to prove that the closed R0/R1/R2 infrastructure and RFC-13/RFC-14 cognition can produce a user-facing answer safely.

Included:

```text
Canonical runtime boot/restore
R2 text ingress in TRANSIENT_ONLY
RFC-13 bounded pattern completion
strict transient activation isolation
RFC-14 bounded hierarchical generation
SurfaceChunk.rendered_text publication
deterministic transient cleanup
simple CognitiveAgent.chat()
simple plain-text REPL
```

Explicitly deferred until R3-Min succeeds:

```text
RFC-15 recurrent continuation
long/multi-chunk generation
RFC-16 canonical R2 handoff integration
long-term conversation memory
Developer Mode UX/API
persistent user learning
code-chat routing
Audio
Vision redesign
Text Encoder redesign
REST server
GUI
plugins/actions
agentic tool execution
```

---

# 2. Governing Principles

R3-Min freezes the following architectural principles:

```text
Observation != Learning
Retrieval != Learning
Generation != Learning
Content != Authority
Identity != Authority
Transient Activation != Persistent Activation Accounting
One User Turn = One Authoritative External Ingress
R2 Owns External Ingress
RFC-13 Owns Pattern Completion
RFC-14 Owns Surface Generation
CognitiveAgent Owns No Cognitive Law
```

R3-Min is an orchestration/runtime integration stage, not a new cognition stage.

---

# 3. Frozen Runtime Semantics Registry

The R3-Min v1.1 semantics registry contains exactly **32** top-level entries:

```json
{
  "activation_scope_lifetime": "RFC13_CALL_ONLY_RESTORE_BEFORE_RFC14",
  "activation_sink_contract": "EXISTING_NODES_ONLY_TRANSIENT_FIELDS_ONLY",
  "anchor_policy": "EXTERNAL_POSITIVE_NODE_RECEIPTS_ONLY",
  "checkpoint_restore": "CANONICAL_R1_SCHEMA_1_2_0",
  "chunk_policy": "JOIN_NONEMPTY_RENDERED_TEXT_WITH_SINGLE_SPACE",
  "completion_activation_mode": "SCOPED_TRANSIENT_UNCOUNTED_RESTORED",
  "completion_budget": "LAW_E_BUDGET_0",
  "completion_canonical_identity": true,
  "completion_owner": "RFC13",
  "external_ingress_count_per_turn": "EXACTLY_ONE",
  "fallback_text": "I don't have enough information.",
  "fresh_bootstrap": "QUANTITY_BACKBONE_BEFORE_R1_PROVENANCE_EPOCH",
  "fresh_prediction_policy": "DISABLED",
  "generation_budget": 1.0,
  "generation_canonical_identity": true,
  "generation_owner": "RFC14",
  "ingress_owner": "R2_CANONICAL_OBSERVATION_BRIDGE",
  "language_context": "en",
  "learning_api": "ABSENT",
  "legacy_compatibility": "EXPLICIT_LEGACY_COGNITIVE_AGENT",
  "legacy_linearizer_policy": "FORBIDDEN_ON_CANONICAL_PATH",
  "loop_policy": "RFC16_NO_EXTERNAL_INGRESS_ON_R3_MIN_PATH",
  "multi_microepisode_policy": "PROCESS_ALL_OBSERVABLE_CHILDREN_IN_CANONICAL_CHILD_ORDER",
  "observation_mode": "TRANSIENT_ONLY",
  "occurrence_policy": "HOST_SESSION_NONCE_PLUS_MONOTONIC_TURN",
  "protocol_version": "R3-MIN-1.0",
  "public_api": ["chat", "__call__", "from_checkpoint"],
  "recurrent_policy": "RFC15_DEFERRED",
  "restore_prediction_policy": "DISABLED",
  "supported_modalities": ["text"],
  "transient_cleanup_policy": "CLOSE_R2_AND_RFC13_DERIVED_SDCRS",
  "turn_concurrency": "SINGLE_ACTIVE_TURN_FAIL_CLOSED"
}
```

Canonical hashing rule:

```python
payload = json.dumps(
    R3_MIN_RUNTIME_SEMANTICS_REGISTRY,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")

digest = hashlib.sha256(payload).hexdigest()
```

Frozen digest:

```text
fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc
```

Required:

```text
top-level entry count == 32
len(digest) == 64
digest is lowercase hexadecimal
```

Forbidden:
- expected-value short circuit;
- XOR/hash calibration;
- registry rewriting to force a chosen digest;
- checkpointing this registry as cognitive state.

The registry is a non-cognitive runtime compatibility fingerprint.


# 4. Canonical Architecture

The only R3-Min user-turn path is:

```text
User Text
   │
   ▼
CognitiveAgent.chat()
   │
   ▼
CanonicalChatRuntime
   │
   ├── trusted host turn occurrence allocation
   │
   ▼
CanonicalR1RuntimeRoot
   │
   ▼
R2 CanonicalObservationBridge
   │
   │ mode = TRANSIENT_ONLY
   ▼
CanonicalObservationResult
   │
   ├── MicroEpisode[0] → SDCR[0]
   ├── MicroEpisode[1] → SDCR[1]
   └── ...
   │
   ▼
for each observable child in canonical child order:
   │
   ├── external direct cue anchors
   │
   ▼
RFC-13 Pattern Completion
   │
   │ activation = scoped transient only
   ▼
Settled SDCR
   │
   ▼
RFC-14 execute_generative_pass()
   │
   ▼
SurfaceChunk.rendered_text
   │
   ▼
collect non-empty chunks
   │
   ▼
join with one ASCII space
   │
   ▼
close all transient representations
   │
   ▼
return str
```

There is no canonical R3-Min branch to:
- `LinearizationEngine`;
- RFC-15;
- `execute_canonical_full_loop()`;
- persistent observation;
- raw graph mutation.

---

# 5. Runtime Ownership

## 5.1 CanonicalR1RuntimeRoot remains the persistent authority owner

It continues to own:
- raw canonical graph;
- causal ledger;
- runtime health;
- canonical lineage state;
- R0 lifecycle guard;
- R2 observation bridge creation.

R3-Min MUST NOT weaken R1 encapsulation.

## 5.2 New non-cognitive runtime object

R3-Min introduces:

```text
CanonicalChatRuntime
```

Recommended file:

```text
dgca/chat_runtime.py
```

It owns **no persistent cognition**.

It receives the private graph only from `CanonicalR1RuntimeRoot`, never from an ordinary caller.

Recommended factory:

```python
runtime_root.create_chat_runtime(...)
```

The factory may internally call:

```python
runtime_root.create_observation_bridge()
```

The ordinary user never sees either bridge or raw graph.

## 5.3 CognitiveAgent becomes a thin façade

`CognitiveAgent` owns:
- a canonical runtime root;
- a canonical chat runtime;
- optional read-only last-turn diagnostics.

It MUST NOT instantiate duplicate RFC-13/RFC-14 engines.

It MUST NOT own a raw public mutable graph.

---

# 6. Fresh Canonical Boot

Fresh `CognitiveAgent()` creation must follow this order:

```text
1. Construct fresh CognitiveGraph(enable_prediction=False).
2. Install intrinsic/bootstrap structures that are part of the initial cognitive state.
3. Initialize the quantity backbone unconditionally as the frozen default intrinsic bootstrap.
4. Extract canonical persistent payload.
5. Compute checkpoint/base state digest.
6. Create native R1 provenance epoch from that state.
7. Create CausalCommitLedger.
8. Create CanonicalR1RuntimeRoot with:
       observation_protocol_version = "R2-OBS-1.0"
       fresh RuntimeLifecycleGuard
9. Create CanonicalChatRuntime through runtime-root authority.
10. Allocate a new non-cognitive chat session nonce.
```

No persistent mutation may occur after step 6 except through R1-governed persistent authority.

Ordinary R3-Min chat never requests such authority.

---

# 7. Canonical Checkpoint Restore

R3-Min supports:

```python
CognitiveAgent.from_checkpoint(filepath)
```

The implementation must use:

```text
restore_canonical_r1_checkpoint(...)
```

with:

```text
expected_observation_protocol_version = "R2-OBS-1.0"
enable_prediction = False
```

The restored `CanonicalR1RuntimeRoot` becomes the only persistent authority root.

R3-Min MUST NOT:
- call legacy `graph.load()`;
- manually rebind individual engines;
- silently migrate an unsupported checkpoint outside the canonical R0/R1 migration path.

The migration report may be retained as developer diagnostics but is not cognitive state.

Ordinary R3-Min does not require a public `save()` method because chat cannot learn.

Developer/training checkpoint publication remains outside R3-Min.

---

# 8. Public CognitiveAgent API

The canonical ordinary API is intentionally small.

Required:

```python
class CognitiveAgent:
    def chat(self, text: str) -> str: ...
    def __call__(self, text: str) -> str: ...

    @classmethod
    def from_checkpoint(cls, filepath: str | Path) -> "CognitiveAgent": ...
```

Optional read-only diagnostic:

```python
@property
def last_turn(self) -> R3TurnResult | None: ...
```

Forbidden on canonical `CognitiveAgent`:

```text
perceive_text
perceive_code
learn
learn_text
learn_code
authorized_persistent
raw_graph
mutable_graph
ledger_mutator
/feed_to_graph
```

A legacy compatibility class, if retained for old regression tests, must:
- have a different explicit name;
- not be exported as top-level `dgca.CognitiveAgent`;
- not be used by the canonical REPL.

Recommended name:

```text
LegacyCognitiveAgent
```

---

# 9. Chat Input Contract

`chat(text)` accepts exactly one ordinary text string.

Fail-closed validation:

```text
not isinstance(text, str)  → TypeError
text.strip() == ""         → ValueError
```

R3-Min does not inspect text to infer:
- learning intent;
- code intent;
- analogy intent;
- reasoning mode;
- persistence authority.

Examples that remain transient:

```text
"remember this permanently"
"fact: ..."
"correction: ..."
"learn that ..."
"store this"
```

They are just user content.

---

# 10. Trusted Host Occurrence Identity

Each `chat()` invocation represents one distinct external occurrence.

Identity MUST NOT be derived from text content.

R3-Min host occurrence descriptor:

```text
boundary_namespace = "DGCA:R3:CHAT:v1"
source_occurrence_key = <session_nonce> + ":" + <turn_index>
source_event_key = "user_message"
ingress_boundary = "R3_CHAT_TEXT"
```

Where:

```text
session_nonce
```

is non-cognitive host/runtime state, unique to one chat-runtime session.

```text
turn_index
```

is a monotonic non-negative session counter.

Two distinct calls with identical text MUST produce different Roots.

A failed turn still consumed a real external occurrence and therefore MUST NOT reuse its turn index.

For deterministic tests, an internal/developer-only constructor hook MAY inject a fixed session nonce.

The ordinary public constructor does not expose this complexity.

---

# 11. Single Active Turn Rule

R3-Min permits only one active chat turn per `CanonicalChatRuntime`.

Required lifecycle:

```text
IDLE → RUNNING → IDLE
```

A concurrent or reentrant second turn must fail closed with an R3 lifecycle error.

This is required because RFC-13 transient activation isolation temporarily projects activation onto graph node transient fields.

R3-Min makes no concurrency guarantees beyond one active turn per runtime.

---

# 12. R2 Ingress Contract

The chat runtime must invoke:

```python
bridge.observe_text(
    boundary_namespace=...,
    source_occurrence_key=...,
    source_event_key="user_message",
    ingress_boundary="R3_CHAT_TEXT",
    raw_text=text,
    context=None,
    mode=ExecutionMode.TRANSIENT_ONLY,
)
```

Hard invariants:

```text
mode == TRANSIENT_ONLY
capability is never supplied
persistent_phase == NOT_REQUESTED
persistent_transaction_id is None
persistent_executed is False
```

R3-Min never creates a second external ingress record for the same turn.

---

# 13. Zero-Observable-Content Contract

If R2 returns:

```text
status == NO_OBSERVABLE_CONTENT
```

or:

```text
representations == ()
```

R3-Min returns the fixed non-cognitive fallback:

```text
I don't have enough information.
```

The fallback is a runtime status rendering.

It is not claimed to be generated knowledge.

The R2 observation result must still be closed.

---

# 14. Multi-MicroEpisode Policy

R2 is frozen to one SDCR per observable MicroEpisode.

R3-Min MUST NOT merge MicroEpisodes into a synthetic persistent or pseudo-persistent representation.

Instead:

```text
PROCESS_ALL_OBSERVABLE_CHILDREN_IN_CANONICAL_CHILD_ORDER
```

Algorithm:

```text
rep_by_id = representations indexed by representation_id

for micro_record in result.micro_episodes in child_index order:
    if micro_record.representation_id is None:
        continue
    rep = rep_by_id[micro_record.representation_id]
    process rep independently through RFC13 → RFC14
```

This preserves R2 causal boundaries and avoids introducing a new cross-MicroEpisode cognition primitive.

---

# 15. Anchor Authority

RFC-14 anchors MUST come from direct positive external node participation in the original R2 child representation.

Definition:

```text
AnchorRefs(child) =
{
    receipt.element_ref
    for receipt in child.participation_receipts
    if receipt.participation_kind == "node"
    and receipt.origin_lineage == "external"
    and receipt.activation_magnitude > 0
    and receipt.element_ref in child.participating_node_refs
}
```

R3-Min MUST NOT:
- rank anchors by keyword;
- pick semantic “important words” using a new heuristic;
- select retrieved nodes as new root authority;
- use global graph scanning to choose anchors.

If `AnchorRefs(child)` is empty, that child produces no RFC-14 chunk.

---

# 16. RFC-13 Completion Contract

For every observable R2 child with at least one anchor, R3-Min calls RFC-13 Law-15 settling with:

```text
canonical_identity = True
root_authority_ref = R2 RootExternalEpisodeID
initial_representation = current R2 child SDCR
budget = Law.E_BUDGET_0
```

A deterministic R1 `InternalWorkID` must be derived for each child:

```text
domain = INTERNAL_WORK
root_authority_ref = RootExternalEpisodeID
subsystem_kind = "RFC13_COMPLETION"
scope_refs = sorted(AnchorRefs)
prerequisite_work_ids = []
work_index_or_role = {
    "observation_transaction_id": ...,
    "micro_episode_id": ...,
    "child_index": ...
}
```

The resulting InternalWorkID is passed as RFC-13 `work_ref`.

No new R3 identity domain is required.

---

# 17. R3-B01 — Transient Activation Isolation Contract

This is the only production integration prerequisite discovered by R3-F01.

Current RFC-13 settling reinstates accepted nodes through `Node.excite()`, while `Node.excite()` increments durable `N_total`.

R3-Min therefore introduces a scoped runtime writer:

```text
TransientActivationScope
```

and a narrow RFC13 seam:

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

RFC13 gains only an optional parameter conceptually equivalent to:

```python
run_settling_epoch(
    ...,
    activation_sink: CompletionActivationSink | None = None,
)
```

## 17.1 Default RFC13 conservation

If:

```text
activation_sink is None
```

RFC13 retains its existing direct `Node.excite()` behavior.

R3-Min MUST NOT alter default RFC13 semantics or behavioral signature.

## 17.2 Existing-node-only authority

The R3 sink may operate only on a node ID already present in the graph.

Unknown node ID:

```text
FAIL CLOSED
```

The sink may never:
- create a node;
- remove a node;
- create/update/remove an Edge;
- modify graph.t;
- modify N_total;
- modify U/V/members/head/is_concept/is_intrinsic;
- modify contradictions;
- modify assemblies;
- modify causal ledger/provenance.

## 17.3 First-touch snapshot

Before the first scoped write to node `n`, capture exactly:

```text
A_before
t_spawn_before
episode_before
```

A node written multiple times in one RFC13 call is snapshotted only on first touch.

## 17.4 Scoped excitation semantics

The sink writes exactly the transient fields that ordinary `Node.excite()` would expose to Law15:

```text
A       = min(Law.C_MAX, value)
t_spawn = t
episode = episode
```

It does **not** increment `N_total`.

During RFC13 settling, all ordinary RFC13 reads of `Node.A` see these scoped values.

Thus:
- seed activation propagation;
- inhibition pressure;
- iterative settling;

retain their existing physics.

## 17.5 Exact scope lifetime

The activation scope lifetime is **only the RFC13 call**:

```text
enter TransientActivationScope
    run RFC13 settling
exit TransientActivationScope
    restore A/t_spawn/episode
then
    run RFC14 on the settled SDCR
```

RFC14 never runs while RFC13 scoped graph activation remains projected.

## 17.6 Restoration

On both success and exception, in `finally`, restore every touched node exactly:

```text
A       = A_before
t_spawn = t_spawn_before
episode = episode_before
```

Required durable invariants:

```text
N_total_after == N_total_before
all durable node fields after == before
all durable edge fields after == before
```

The scope becomes CLOSED after restoration.

Any write attempted after scope close fails closed.

## 17.7 No mutate-then-restore loophole

Forbidden:

```text
call Node.excite()
then decrement/restore N_total afterward
```

R3-Min prevents the unauthorized durable mutation from occurring.


# 18. RFC-13 Derived Representation Lifecycle

Law-15 may create new RFC-12 SDCR snapshots over multiple settling iterations.

R3-Min must track all representations created by one completion operation.

Required behavior:

```text
active_representation_ids_before = snapshot
run RFC13
active_representation_ids_after = snapshot
completion_created_ids = after - before
```

The final settled representation remains available only until RFC-14 generation for that child completes.

After generation:
- close every R3/RFC-13-created representation for that child;
- preserve the original R2 representation until the enclosing R2 result is closed.

No active RFC-13 derived SDCR may remain after the turn.

Closed representation diagnostic retention inside RFC-12 is not persistent cognition and is not changed by R3-Min.

Long-session memory retention of closed diagnostic SDCRs is explicitly a post-R3-Min engineering audit item.

---

# 19. RFC-14 Generation Contract

For each settled child:

```python
generation_scope = GenerationScope(
    task_ref=root_external_episode_id,
    query_ref=observation_transaction_id,
    event_ref=micro_episode_id,
)
```

Call:

```python
handoff = graph.generation_engine.execute_generative_pass(
    representation=settled_representation,
    anchor_refs=AnchorRefs(child),
    generation_scope=generation_scope,
    language_context="en",
    budget=1.0,
    canonical_identity=True,
)
```

Canonical user-facing cognitive text is:

```text
handoff.surface_chunk_view.rendered_text
```

No second text generator is allowed.

---

# 20. RFC-14 Closure Handling

A `SurfaceChunk` may close as:

```text
COMPLETE
CONFLICT
AMBIGUOUS
PARTIAL_BUDGET
UNDERSPECIFIED
```

R3-Min does not fabricate additional semantic content for any closure type.

Rule:

```text
if rendered_text.strip() != "":
    publish that rendered text as this child's chunk
else:
    publish no chunk for that child
```

The turn-level fallback is used only if all children produce no non-empty chunk.

---

# 21. Turn-Level Chunk Assembly

Let:

```text
C = non-empty RFC14 rendered_text chunks
```

in canonical R2 child order.

If `C` is non-empty:

```text
answer = " ".join(C)
```

Exactly one ASCII space separates adjacent non-empty chunks.

R3-Min adds:
- no punctuation;
- no capitalization repair;
- no template sentence;
- no explanatory boilerplate;
- no lexical substitutions.

Language-quality work follows empirical evaluation after the model can actually chat.

---

# 22. Fixed Fallback

The only runtime-generated semantic-neutral fallback string is:

```text
I don't have enough information.
```

It is used when:
- no R2 observable representation exists; or
- all observable children fail to produce any non-empty RFC-14 text.

R3-Min must not convert a failure into a plausible invented answer.

---

# 23. RFC-15 Deferral

RFC-15 is explicitly outside the R3-Min execution path.

During ordinary R3-Min chat:

```text
recurrent_engine MUST NOT be invoked
GCE MUST NOT be created
ExpressionReceipt MUST NOT be created
ContinuationCommit MUST NOT be created
```

This is deliberate.

The purpose is to prove the smallest working model first:

```text
R2 → RFC13 → RFC14 → text
```

After R3-Min acceptance, a later stage may add RFC-15 continuation:

```text
R3.1 / R3-Continuation
```

without changing R2 ingress authority or ordinary learning safety.

---

# 24. RFC-16 Deferral / Compatibility Rule

R3-Min does not delete RFC-16.

However:

```text
UnifiedGenerativeCognitiveLoopEngine.execute_canonical_full_loop()
```

must not be called from `CognitiveAgent.chat()` because its current external-event ingress predates the closed R2 authority path.

A later RFC-16 integration may add a method that consumes an existing:

```text
RootExternalEpisodeID
ObservationTransactionID
R2 SDCR
```

rather than constructing a second root from question content.

That work is explicitly after R3-Min.

---

# 25. Legacy Linearizer Rule

Canonical R3-Min chat must not instantiate or call:

```text
LinearizationEngine.answer_query()
LinearizationEngine.generate()
```

The legacy linearizer may remain in the repository for compatibility tests or historical APIs, but it is not part of canonical chat.

A spy/mock acceptance test must prove zero calls from R3-Min.

---

# 26. No Persistent Learning Surface

Ordinary R3-Min exposes no learning API.

Hard rule:

```text
CognitiveAgent has no public operation capable of supplying
ExecutionMode.AUTHORIZED_PERSISTENT or an R2 capability object.
```

Persistent learning will later live behind explicit Developer Mode authority.

It is not part of this stage.

---

# 27. Turn Cleanup

Cleanup is deterministic and failure-safe.

For each child:

```text
1. Enter RFC13 TransientActivationScope.
2. Run RFC13.
3. Exit scope immediately:
       restore A/t_spawn/episode exactly.
4. Run RFC14 using the settled SDCR.
5. Close every RFC13-derived SDCR created for that child.
```

For the enclosing turn:

```text
6. Close the R2 CanonicalObservationResult in turn-level finally.
7. Return/raise only after the R3 turn lifecycle owner returns to IDLE.
```

If RFC13 raises:
- activation scope restores first;
- any RFC13-created SDCRs are closed;
- R2 result is closed;
- turn returns to IDLE.

If RFC14 raises:
- RFC13 activation has already been restored;
- RFC13-derived SDCRs are closed;
- R2 result is closed;
- turn returns to IDLE.

Unexpected internal exceptions may propagate as Python exceptions.

They must not be converted into fabricated natural-language answers.


# 28. Persistent-State Conservation

For every successful ordinary chat turn, the following canonical persistent state must remain exactly unchanged:

```text
logical_time
nodes durable fields
N_total
edges and all durable edge fields
contradictions
concept_hits
drives
hypotheses
assemblies
pending structural evidence
causal ledger committed transactions
causal ledger event bindings
causal provenance epoch
```

The following may change transiently during execution and are restored/closed as specified:

```text
Node.A
Node.t_spawn
Node.episode
RFC12 active SDCRs
RFC13 candidates/proposals/settling state
RFC14 frames/chunks
diagnostic counters
reconstructible caches
R3 turn diagnostics
```

Production `chat()` is not required to hash the entire persistent graph before/after every turn.

The exact digest equality is a mandatory acceptance test and optional developer assertion mode.

---

# 29. Canonical Lineage Conservation

Before ordinary chat:

```text
runtime.canonical_lineage_state == VALID
runtime.causal_runtime_health == HEALTHY
```

After successful ordinary chat:

```text
runtime.canonical_lineage_state == VALID
runtime.causal_runtime_health == HEALTHY
```

R3-Min must never use:

```text
unsafe_mutable_graph()
unsafe_mutable_ledger()
unsafe_legacy_mutation_escape_hatch()
```

---

# 30. R3TurnResult — Diagnostic View

Recommended transient diagnostic object:

```python
@dataclass(frozen=True)
class R3TurnResult:
    protocol_version: str
    session_turn_index: int
    root_external_episode_id: str
    ingress_event_id: str
    observation_transaction_id: str
    micro_episode_ids: tuple[str, ...]
    input_representation_ids: tuple[str, ...]
    settled_representation_ids: tuple[str, ...]
    surface_chunk_ids: tuple[str, ...]
    completion_closure_reasons: tuple[str, ...]
    generation_closure_reasons: tuple[str, ...]
    text: str
    used_fallback: bool
```

It is:
- transient;
- non-cognitive;
- not checkpointed;
- read-only to users.

`CognitiveAgent.chat()` returns only `.text`.

---

# 31. Recommended Module Layout

```text
dgca/
├── agent.py
├── chat_runtime.py          # NEW
├── causal_identity.py       # narrow create_chat_runtime factory only
├── completion.py            # narrow activation_sink seam only
├── observation.py           # unchanged semantics
├── representation.py        # unchanged semantics
├── generation.py            # unchanged semantics
├── recurrent.py             # unchanged, unused in R3-Min
├── loop.py                  # unchanged, unused as ingress
└── legacy_agent.py          # optional compatibility extraction

scripts/
└── repl.py                  # canonical plain-text chat
```

Avoid creating a broad new framework.

---

# 32. Canonical REPL

Canonical `scripts/repl.py` target:

```text
DGCA> Why does the ocean become warm?
<answer>

DGCA> ...
```

Allowed local command:

```text
/quit
```

Optionally:

```text
/exit
```

Forbidden:

```text
/learn
/ask
/code
/analogy
/compare
```

Plain text always routes to:

```python
agent.chat(text)
```

The REPL does not infer hidden modes.

---

# 33. R3-Min Invariants

```text
R3-I01  CognitiveAgent.chat(text) is the canonical ordinary-user entry point.
R3-I02  CognitiveAgent.__call__(text) delegates exactly to chat(text).
R3-I03  from_checkpoint uses canonical R1 restore.
R3-I04  ordinary chat invokes R2 exactly once per turn.
R3-I05  R2 mode is always TRANSIENT_ONLY.
R3-I06  ordinary Agent exposes no persistent capability.
R3-I07  raw user content cannot grant learning authority.
R3-I08  Root identity is occurrence-derived, never content-hash-derived.
R3-I09  distinct identical-text calls create distinct Roots.
R3-I10  all observable R2 children are processed in child order.
R3-I11  R2 children are not merged by a new cognition primitive.
R3-I12  anchors are direct positive external node receipts only.
R3-I13  RFC13 uses canonical identities.
R3-I14  RFC13 receives the original R2 Root authority.
R3-I15  RFC13 scoped activation preserves Law-15 reads of Node.A.
R3-I16  RFC13 scoped activation never increments N_total.
R3-I17  touched A/t_spawn/episode fields are restored exactly.
R3-I18  RFC13 derived SDCRs are closed after their RFC14 generation.
R3-I19  R2 observation results are closed in finally.
R3-I20  RFC14 uses canonical identities.
R3-I21  RFC14 rendered_text is the only cognitive user-visible surface.
R3-I22  non-empty child chunks are joined only with one ASCII space.
R3-I23  empty overall generation returns only the fixed fallback.
R3-I24  Legacy LinearizationEngine is not called.
R3-I25  RFC15 recurrent engine is not called.
R3-I26  RFC16 full-loop ingress is not called.
R3-I27  one runtime permits one active turn only.
R3-I28  no ordinary chat changes canonical persistent payload.
R3-I29  no ordinary chat changes causal ledger.
R3-I30  no ordinary chat changes RFC11 persistent structural evidence.
R3-I31  canonical lineage remains VALID.
R3-I32  runtime health remains HEALTHY.
R3-I33  fresh and restored R3-Min prediction side path is disabled.
R3-I34  RFC13 completion budget is exactly Law.E_BUDGET_0.
R3-I35  RFC14 generation budget is exactly 1.0.
R3-I36  language_context is fixed to "en".
R3-I37  Audio is not invoked.
R3-I38  Vision is not modified or invoked by text chat.
R3-I39  no new cognitive law is introduced.
R3-I40  R3 turn diagnostics are transient and not checkpointed.
R3-I41  ordinary REPL contains no /learn path.
R3-I42  any future RFC15 addition must preserve I01–I41 unless explicitly re-frozen.
```

---

# 34. Acceptance Matrix

## A — Boot

```text
A01 fresh CognitiveAgent constructs a healthy canonical R1 runtime.
A02 fresh runtime uses observation protocol R2-OBS-1.0.
A03 fresh lineage is VALID.
A04 top-level dgca.CognitiveAgent is the new canonical Agent.
A05 raw mutable graph is not exposed publicly.
```

## B — Checkpoint

```text
B01 from_checkpoint restores canonical schema 1.2.0.
B02 R2 protocol mismatch fails closed.
B03 malformed/integrity-invalid checkpoint fails closed.
B04 restored agent can execute chat().
B05 no legacy graph.load() path is used.
```

## C — Occurrence identity

```text
C01 first chat allocates one Root.
C02 second identical-text chat allocates a different Root.
C03 Root derivation does not contain/hash raw text as occurrence authority.
C04 failed turn index is not reused.
C05 fixed test session nonce + same turn index reproduces same Root.
```

## D — R2

```text
D01 bridge.observe_text is invoked exactly once per chat.
D02 mode is TRANSIENT_ONLY.
D03 capability is absent.
D04 persistent_phase is NOT_REQUESTED.
D05 ledger is unchanged.
D06 content such as "fact:" cannot change D02-D05.
```

## E — Multi-child

```text
E01 zero-child returns fallback.
E02 one-child path executes once.
E03 N observable children execute in exact child_index order.
E04 representation_id=None children are skipped.
E05 no synthetic merged R2 representation is created.
```

## F — Anchors

```text
F01 anchors come only from positive external node receipts.
F02 completed/recalled nodes are not promoted to root anchors.
F03 empty anchor set skips generation for that child.
F04 no stopword/keyword ranking chooses anchors.
```

## G — RFC13 isolation

```text
G01 RFC13 can accept at least one reinstatement under R3 scope.
G02 touched Node.A is visible during settling.
G03 inhibition sees scoped Node.A.
G04 N_total before == N_total after for all nodes.
G05 A before == A after for all touched nodes.
G06 t_spawn before == t_spawn after.
G07 episode before == episode after.
G08 restoration occurs after RFC13 exception.
G09 RFC13 legacy path without activation sink preserves old behavior.
G10 RFC13 behavioral signature on legacy/default path is unchanged.
G11 R3 invokes RFC13 with budget == Law.E_BUDGET_0.
```

## H — Representations

```text
H01 completion-created SDCRs are tracked.
H02 final settled SDCR is available through RFC14 call.
H03 all completion-created SDCRs are CLOSED after child completion.
H04 original R2 SDCR remains alive until R2 result cleanup.
H05 all original R2 SDCRs are CLOSED after turn cleanup.
H06 no ACTIVE R3-created representation survives the turn.
```

## I — RFC14

```text
I01 RFC14 canonical_identity=True.
I02 GenerationScope carries current Root/Observation/MicroEpisode refs.
I03 language_context == "en".
I04 returned child text is SurfaceChunk.rendered_text.
I05 no legacy LinearizationEngine text substitution occurs.
I06 RFC14 behavioral signature remains unchanged.
I07 R3 invokes RFC14 with budget == 1.0.
```

## J — Turn text

```text
J01 one non-empty chunk returns exactly that string.
J02 multiple non-empty chunks join with exactly one ASCII space.
J03 empty chunks are omitted.
J04 all-empty output returns exact fixed fallback.
J05 R3 adds no punctuation/capitalization/template text to a non-empty chunk.
```

## K — Deferred systems

```text
K01 recurrent_engine is not invoked.
K02 no GCE exists because of ordinary R3-Min chat.
K03 loop_engine.execute_canonical_full_loop is not invoked.
K04 LinearizationEngine.answer_query is not invoked.
K05 Audio encoders are not invoked.
K06 Vision encoders are not invoked.
```

## L — Persistent conservation

```text
L01 canonical persistent payload digest before == after.
L02 graph logical_time before == after.
L03 all durable node fields before == after.
L04 all durable edge fields before == after.
L05 contradictions before == after.
L06 concept_hits before == after.
L07 drives before == after.
L08 hypotheses before == after.
L09 assemblies before == after.
L10 pending structural evidence before == after.
L11 causal ledger before == after.
L12 causal provenance epoch before == after.
```

## M — Lifecycle/failure

```text
M01 second concurrent chat fails closed.
M02 nested/reentrant chat fails closed.
M03 turn owner returns to IDLE after success.
M04 turn owner returns to IDLE after failure.
M05 transient cleanup executes after RFC13 failure.
M06 transient cleanup executes after RFC14 failure.
M07 runtime health remains HEALTHY for transient cognitive failure.
M08 canonical lineage remains VALID.
```

## N — Public surface

```text
N01 CognitiveAgent has chat().
N02 CognitiveAgent has __call__().
N03 CognitiveAgent has from_checkpoint().
N04 CognitiveAgent does not expose perceive_text().
N05 CognitiveAgent does not expose perceive_code().
N06 CognitiveAgent does not expose learn().
N07 canonical REPL has no /learn command.
N08 plain REPL text routes directly to chat().
```

---

# 35. Required Regression Gates

Before R3-Min can close:

```text
1. Full pre-R3 repository test suite must pass.
   Tests that exercise RFC09 Agent behavior may change imports only to the explicit
   LegacyCognitiveAgent compatibility owner; their behavioral assertions must not be
   deleted, weakened, or semantically rewritten merely to make R3 pass.

2. R1 causal identity protocol digest remains unchanged.

3. R2 observation semantics digest remains unchanged:
   bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b

4. Existing RFC13 behavioral signature must remain unchanged on default/legacy path.

5. Existing RFC14 behavioral signature must remain unchanged.

6. No R0/R1/R2 persistent/checkpoint semantics change.

7. No Audio or Vision regression is introduced.

8. Ruff/type/static quality gates remain clean according to repository policy.
```

---

# 36. No-Go Implementations

The following implementations fail R3-Min by definition:

```text
CognitiveAgent.chat() calls legacy query()
CognitiveAgent.chat() calls perceive_text()
CognitiveAgent.chat() calls encoder.feed_to_graph()
chat text decides whether learning is authorized
chat text prefixes like "fact:" enable persistent mutation
ordinary Agent accepts capability objects
R2 is invoked with AUTHORIZED_PERSISTENT
R2 runs, then RFC16 creates a second external event/root
RootExternalEpisodeID = hash(text)
RFC13 calls ordinary Node.excite() on R3 transient path
RFC13 increments N_total then rolls it back afterward
RFC13 activation is detached so Law15 cannot see Node.A
RFC13 derived ACTIVE SDCRs leak after the turn
RFC14 is bypassed by LinearizationEngine
R3 modifies RFC14 output with hand-built semantic templates
R3 invokes RFC15 before R3-Min acceptance
R3 opens Audio work
R3 redesigns Text Encoder
R3 adds a new cognitive law
R3 uses unsafe_mutable_graph()
R3 stores session transcript as persistent cognition
```

Particularly forbidden:

```text
"mutate persistent state, then restore it"
```

R3-Min must prevent the unauthorized persistent mutation from occurring in the first place.

---

# 37. Implementation Change Budget

R3-Min should remain narrow.

Expected production changes:

```text
NEW:
dgca/chat_runtime.py
tests/test_ric01_r3_minimal_*.py

MODIFY NARROWLY:
dgca/agent.py
dgca/causal_identity.py
dgca/completion.py
dgca/__init__.py
scripts/repl.py
```

Required compatibility extraction if the old RFC09 Agent remains under test:

```text
dgca/legacy_agent.py
    LegacyCognitiveAgent
```

The old behavior is conserved there; top-level `dgca.CognitiveAgent` is the canonical R3-Min Agent.

No expected cognitive changes to:

```text
dgca/observation.py
dgca/representation.py
dgca/generation.py
dgca/recurrent.py
dgca/loop.py
dgca/audio*
dgca/vision*
```

If implementation requires broad modifications to these files, implementation must stop and return to architecture review.

---

# 38. Implementation Sequence

After this specification survives adversarial review and is frozen, implementation should proceed in this order:

```text
R3-P1  TransientActivationScope + RFC13 activation_sink seam
R3-P2  CanonicalChatRuntime
R3-P3  CognitiveAgent v2 façade + canonical fresh boot
R3-P4  from_checkpoint canonical restore
R3-P5  canonical plain-text REPL
R3-P6  acceptance + persistent-conservation tests
R3-P7  full regression and independent audit
```

Do not implement RFC-15 in any R3-P1..P7 step.

---

# 39. Success Definition

R3-Min is successful when this works:

```python
agent = CognitiveAgent.from_checkpoint("trained_brain.json")
print(agent.chat("Why does the ocean become warm?"))
```

and the answer comes from:

```text
R2 current perception
→ RFC13 stored-knowledge reinstatement
→ RFC14 surface generation
```

while proving:

```text
persistent cognitive state delta = 0
causal ledger delta = 0
RFC11 persistent evidence delta = 0
legacy linearizer calls = 0
RFC15 calls = 0
RFC16 second ingress calls = 0
active transient representation leakage = 0
```

Language quality does not need to be perfect for R3-Min closure.

The purpose of R3-Min is to expose the real cognitive architecture so that later empirical evaluation can reveal actual model bottlenecks instead of hiding them behind legacy heuristics.

---

# 40. Post-R3-Min Roadmap

Only after R3-Min passes independently:

```text
1. Run first real conversational/generative evaluation.
2. Measure retrieval quality.
3. Measure RFC14 surface quality.
4. Measure failure/ambiguity/underspecification rates.
5. Then add RFC15 recurrent continuation.
6. Re-evaluate long generation.
7. Later integrate RFC16 with R2-native existing-root handoff.
8. Later audit/rebuild Text Encoder.
9. Later large-scale real-data benchmark.
```

RFC-15 addition must be evidence-driven by limits found in the working minimal model.

---

# 41. Frozen Verdict

```text
==========================================================
DGCA — RIC-01 / R3 MINIMAL
FORMAL ARCHITECTURE SPECIFICATION v1.1 — FROZEN

BASELINE:
c04c0820ef3cb329008a6bc7be0d9c4fd8754403

USER API:
chat(text) -> str

CANONICAL PATH:
R2 TRANSIENT_ONLY
→ RFC13 TRANSIENT-ISOLATED COMPLETION
→ RFC14 SINGLE-PASS GENERATION
→ SurfaceChunk.rendered_text

RFC13 BUDGET:
Law.E_BUDGET_0

RFC14 BUDGET:
1.0

RFC15:
DEFERRED UNTIL R3-MIN SUCCESS

RFC16 FULL-LOOP INGRESS:
NOT USED

LEGACY LINEARIZER:
FORBIDDEN ON CANONICAL PATH

PERSISTENT LEARNING:
ABSENT FROM ORDINARY AGENT

NEW COGNITIVE LAW:
NO

R3-MIN SEMANTICS DIGEST:
fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc

ADVERSARIAL FREEZE REVIEW:
PASS

FREEZE BLOCKERS:
0

STATUS:
FROZEN

IMPLEMENTATION:
NOT YET AUTHORIZED
==========================================================
```