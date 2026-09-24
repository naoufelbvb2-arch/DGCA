# DGCA — RIC-03: Canonical Learning Runtime & Authority Separation

**Document ID:** `RIC-03-ARCH-1.0`  
**Status:** FROZEN / ADOPTED  
**Authoritative Baseline:** `cd05769dc09471592b92a9b07f720660bd5d57eb`  
**Domain:** System Composition, Learning Ingress & Authority Architecture  

---

## 1. Purpose & Problem Statement

Prior to RIC-03, DGCA possessed canonical persistent observation capability through the R2/R1 architecture:
`CanonicalObservationBridge` (`mode = ExecutionMode.AUTHORIZED_PERSISTENT`) &rarr; `PersistentObservationAuthorizer` &rarr; `CanonicalR1RuntimeRoot.execute_persistent_command()` &rarr; `CognitiveGraph.observe()/observe_sequence()` &rarr; Cognitive learning laws.

However, no canonical host-side runtime exposed this persistent path to host processes. As a result, experimental scripts and test harnesses were forced to directly access private R1 root methods or construct unmediated bridges, creating risks of authority leakage, cognitive shortcuts, and improper mutation.

RIC-03 establishes the canonical host-side persistent learning runtime without modifying underlying cognitive laws or bypassing R2/R1 governance. The objective is **not** to invent a new learning mechanism, but to expose and compose the existing canonical persistent observation path under strict separation of authority, explicit occurrence identity, immutable result encapsulation, and deterministic host-side operation serialization.

---

## 2. Target Authority Model & Architecture

```text
Host System Caller
      |
      v
CanonicalSystemRuntime (Lifecycle & Mutual Exclusion Host Gate)
      |
      +---- CanonicalChatRuntime (Conversational Ingress, TRANSIENT_ONLY, RFC13, RFC14)
      |
      +---- CanonicalLearningRuntime (Learning Request Owner)
                 | (passes private ephemeral capability)
                 v
            CanonicalObservationBridge (R2 Ingress Boundary)
                 | (delegates authorization check)
                 v
            CanonicalLearningAuthorizer (Learning Authorization Owner, verify_persistent_observation)
                 | (if authorized: delegates persistent execution)
                 v
            CanonicalR1RuntimeRoot (Persistent Mutation Authority, execute_persistent_command)
                 |
                 +---- CognitiveGraph (Learning Semantics Owner, observe/observe_sequence)
                 |
                 +---- CausalCommitLedger (Ledger Authority, Tx Record & Occurrence Proofs)
```

### 2.1 Authority Separation Matrix

| Authority Dimension | Owner Component | Responsibilities & Boundaries |
| :--- | :--- | :--- |
| **Learning Request Owner** | `CanonicalLearningRuntime` | Allocates monotonic operation index, generates occurrence keys, passes capability to bridge, closes observation results. Holds **zero** authorization and **zero** mutation authority. |
| **Learning Authorization Owner** | `CanonicalLearningAuthorizer` | Validates capability identity, modality (`"text"`), operation kind (`"R2_AUTHORIZED_PERSISTENT"`), and R1 health/lineage. Holds **zero** request authority, **zero** mutation authority, and never inspects text content. |
| **Persistent Mutation Authority** | `CanonicalR1RuntimeRoot` | Validates causal lineage, commits transactions to ledger, orchestrates graph execution. Sole gateway to persistent mutation. |
| **Learning Semantics Owner** | `CognitiveGraph` | Governs node allocation, synaptic weight updates, decay, and recurrence according to invariant cognitive laws. |
| **System Composition / Lifecycle** | `CanonicalSystemRuntime` | Host-side orchestration, manages lifecycle, serializes host operations (`IDLE`, `CHATTING`, `LEARNING`, `CHECKPOINTING`). |
| **Ordinary User Interface** | `CognitiveAgent` | External user conversational façade (`chat()`, `__call__()`). Possesses **zero** learning authority and no learning APIs. |

Under this model, **no single component owns all four aspects**: Request, Authorization, Mutation, and Cognitive Semantics.

---

## 3. Capability Lifecycle & Ephemerality

Persistent observation in DGCA requires an opaque authorization capability. In RIC-03, this capability adheres to strict lifecycle invariants:

1. **Opaque Object Identity:** The capability is an instance of `object()` (`self._capability = object()`), relying strictly on Python reference identity (`capability is self._capability`).
2. **Host-Created & Private:** Created internally by `CanonicalSystemRuntime.__init__` or `CanonicalLearningRuntime.create()`. It is never derived from text, never parameterized by user input, and never exposed via public properties.
3. **Ephemeral & Un-serializable:** The capability lives only in process memory for the lifetime of that runtime instance.
4. **Zero Checkpoint Persistence:** The capability is never included in checkpoint bundles (`save_canonical_r1_checkpoint`), state digests, or transaction records. Checkpoint schema remains strictly `1.2.0`.
5. **Fresh Capability on Boot and Restore:** Upon `CanonicalSystemRuntime.fresh()`, a fresh capability is instantiated. Upon `CanonicalSystemRuntime.from_checkpoint()`, a completely new fresh capability is instantiated. Capabilities from prior processes or checkpoints are invalid.
6. **No Result Leakage:** The capability is never stored or returned in `LearningResult` or any logging structure.

---

## 4. Learning Protocol Constants & Ingress Contracts

RIC-03 introduces canonical host-level learning constants:

```python
RIC03_LEARNING_PROTOCOL_VERSION: str = "RIC03-LEARN-1.0"
LEARNING_BOUNDARY_NAMESPACE: str = "DGCA:RIC03:LEARN:v1"
LEARNING_SOURCE_EVENT_KEY: str = "learning_observation"
LEARNING_INGRESS_BOUNDARY: str = "RIC03_LEARNING_TEXT"
```

- **Modality Support:** RIC-03 v1 strictly supports `"text"` modality. Ingress with any other modality (e.g., `"audio"`, `"vision"`) must fail closed.
- **Ingress Operation Kind:** Ingress specifies `operation_kind = "R2_AUTHORIZED_PERSISTENT"`.
- **Content Neutrality:** No keyword, semantic pattern, or syntax constitutes authority. Content never self-authorizes.

---

## 5. Canonical Learning Authorizer Specification

`CanonicalLearningAuthorizer` implements the R2 `PersistentObservationAuthorizer` protocol:

```python
class CanonicalLearningAuthorizer:
    def verify_persistent_observation(
        self,
        *,
        capability: object,
        root_external_episode_id: str,
        ingress_event_id: str,
        modality: str,
        operation_kind: str,
    ) -> bool: ...
```

### 5.1 Verification Logic & Rules
The authorizer grants persistent observation authority if and only if **all** of the following conditions evaluate to `True`:
1. `capability is self._capability` (exact object identity match; `None` or forged object returns `False`).
2. `modality == "text"` (unsupported modality returns `False`).
3. `operation_kind == "R2_AUTHORIZED_PERSISTENT"` (unexpected operation kind returns `False`).
4. `self._runtime_root.causal_runtime_health == CausalRuntimeHealth.HEALTHY`.
5. `self._runtime_root.canonical_lineage_state == CanonicalLineageState.VALID`.

### 5.2 Mandatory Authorizer Invariants
- **Fail-Closed Default:** Any failure, mismatch, or unexpected condition returns `False`.
- **Strict Boolean Type:** The return value is strictly `bool` (`True` or `False`), never a truthy non-bool.
- **Content Ignorance:** The authorizer does not accept, inspect, or process the raw text payload, prompt text, or context. Text content cannot grant or modify authority.

---

## 6. Canonical Learning Runtime Specification

`CanonicalLearningRuntime` orchestrates learning requests across the R2 observation bridge.

### 6.1 State & Construction
- Bound to a `CanonicalR1RuntimeRoot`, a `CanonicalLearningAuthorizer`, and an opaque capability.
- Receives bridge exclusively via `runtime_root.create_observation_bridge(authorizer=authorizer)`. It never directly constructs, touches, or invokes `CognitiveGraph`.
- Owns a unique session nonce: `session_nonce = uuid.uuid4().hex[:12]`.
- Owns a monotonically increasing counter: `learning_index: int = 0`.

### 6.2 Primary Execution Interface
```python
def learn_text(
    self,
    text: str,
    *,
    context: str | None = None,
    occurrence_key: str | None = None,
) -> LearningResult: ...
```

### 6.3 Execution Steps
1. **Pre-flight Argument Validation:** Validate `text` is a non-empty string. If invalid, raise `ValueError` immediately without incrementing `learning_index`.
2. **Index Allocation:** Increment `self._learning_index += 1`.
3. **Occurrence Key Resolution:**
   - If `occurrence_key is None`: `source_occurrence_key = f"auto:{self._session_nonce}:{self._learning_index}"`, `identity_mode = "AUTO"`.
   - If `occurrence_key is not None`: `source_occurrence_key = f"external:{occurrence_key}"`, `identity_mode = "EXTERNAL"`.
4. **Bridge Ingress Invocation:**
   Call `self._bridge.observe_text(...)` passing:
   - `boundary_namespace = LEARNING_BOUNDARY_NAMESPACE`
   - `source_occurrence_key = source_occurrence_key`
   - `source_event_key = LEARNING_SOURCE_EVENT_KEY`
   - `ingress_boundary = LEARNING_INGRESS_BOUNDARY`
   - `raw_text = text`
   - `context = context`
   - `mode = ExecutionMode.AUTHORIZED_PERSISTENT`
   - `capability = self._capability`
5. **Result Extraction & Cleanup:**
   Extract diagnostics from `CanonicalObservationResult`, construct immutable `LearningResult`, and **always** invoke `close_result(observation_result)` within a `finally` block.

---

## 7. Learning Occurrence Identity & Replay Semantics

Learning occurrence identity determines whether an observation is treated as a novel learning event, lawful reinforcement, or an idempotent replay:

### 7.1 AUTO Identity (`identity_mode == "AUTO"`)
- Formatted as `auto:<session_nonce>:<learning_index>`.
- Two successive calls with identical text under AUTO mode receive distinct occurrence keys (`auto:<nonce>:1` vs `auto:<nonce>:2`).
- Both calls execute persistently as distinct transactions with distinct persistent transaction IDs. This enables natural multi-exposure reinforcement.

### 7.2 Explicit Identity (`identity_mode == "EXTERNAL"`)
- Formatted as `external:<occurrence_key>`.
- **Same key + same text:** Evaluates to `PERSISTENT_REPLAY`. `persistent_executed` is `False`, zero duplicate learning occurs, and no new transaction is committed to the ledger.
- **Same key + different text:** Fails closed via R2/R1 causal identity validation (`CausalIdentityValidationError` or equivalent). Occurrence keys cannot be bound to conflicting content descriptors.
- **Replay Across Restore:** Explicit occurrence keys persist in the R1 causal ledger. A checkpoint restored from disk remembers previously committed explicit occurrence keys; replaying the same key and text after restore correctly yields `PERSISTENT_REPLAY` with `persistent_executed == False`.

---

## 8. Learning Index Failure Rule & Monotonicity

Once a `learning_index` is allocated for an operation, if downstream execution fails, raises an exception, or is aborted, that index is **never** reused. The next operation receives `learning_index + 1`. This prevents a failed occurrence identity from being re-associated with a subsequent unrelated payload.

---

## 9. Result Lifecycle & Resource Management

Host callers must not receive mutable internal representations or unclosed SDCR tokens.

### 9.1 Immutable LearningResult
```python
@dataclass(frozen=True)
class LearningResult:
    protocol_version: str
    learning_index: int
    identity_mode: str  # "AUTO" | "EXTERNAL"
    source_occurrence_key: str
    root_external_episode_id: str
    ingress_event_id: str
    observation_transaction_id: str
    persistent_transaction_id: str | None
    status: str
    persistent_phase: str
    persistent_executed: bool
    replayed: bool
    observable_child_count: int
```

### 9.2 Encapsulation & Closure Guarantees
- `LearningResult` never exposes internal capabilities, authorizers, graphs, ledgers, or raw observation results.
- `CanonicalObservationResult` is guaranteed closed via `try ... finally` in `learn_text()`.
- On execution error, transient representations are safely closed without leaking open SDCR structures.

---

## 10. No-Generation Ingress Policy

Canonical learning is strictly an **Ingress &rarr; Persistence** operation:
- Learning **does not** invoke `PatternCompletionEngine` (RFC13).
- Learning **does not** invoke surface generation (RFC14).
- Learning **does not** invoke recurrent generation (RFC15) or loop engine (RFC16).
- Learning **does not** invoke the legacy linearizer.
- Call count for RFC13 and RFC14 during `learn()` must be strictly 0.

---

## 11. System Runtime Integration & Operation Serialization

`CanonicalSystemRuntime` in `dgca/system_runtime.py` serves as the composed lifecycle owner.

### 11.1 System Operation States
```python
class SystemOperationState(str, enum.Enum):
    IDLE = "IDLE"
    CHATTING = "CHATTING"
    LEARNING = "LEARNING"
    CHECKPOINTING = "CHECKPOINTING"
```

### 11.2 Mutual Exclusion Invariants
Composed operations on a `CanonicalSystemRuntime` instance are strictly mutually exclusive:
- `chat()` enters `CHATTING` and restores `IDLE` in `finally`.
- `learn()` enters `LEARNING` and restores `IDLE` in `finally`.
- `save_checkpoint()` enters `CHECKPOINTING` and restores `IDLE` in `finally`.
- If an operation is attempted while the runtime is not `IDLE`, it fails closed by raising a deterministic `RuntimeError`.
- Nested or reentrant invocations fail closed.
- The operation state is transient host engineering state only; it is never persisted to checkpoints.

---

## 12. Checkpoint Persistence & Schema 1.2.0 Conservation

- Checkpoint schema version remains strictly `1.2.0`.
- Checkpoints contain **no** capability objects, session nonces, or operation state flags.
- Checkpoint state digest calculation remains identical.
- Upon checkpoint restore, cognitive state and the R1 commit ledger are restored, associations are retained, and fresh ephemeral learning capabilities are initialized.

---

## 13. CognitiveAgent & Cognitive Kernel Absolute Freeze

### 13.1 CognitiveAgent Immutability
`dgca/agent.py` remains 100% byte-identical to baseline `cd05769dc09471592b92a9b07f720660bd5d57eb`.
- Possesses **no** `learn()` or `learn_text()` methods.
- Conversational chat turns containing phrases such as `"learn this fact"` or `"remember this"` remain strictly transient.
- User conversational text cannot trigger persistent learning.

### 13.2 Cognitive Files Absolute Freeze
The following production files remain byte-identical:
- `dgca/agent.py`
- `dgca/graph.py`
- `dgca/causal_identity.py`
- `dgca/observation.py`
- `dgca/persistence.py`
- `dgca/chat_runtime.py`
- `dgca/completion.py`
- `dgca/generation.py`
- `dgca/recurrent.py`
- `dgca/loop.py`
- `dgca/encoder.py`
- `dgca/audio.py`
- `dgca/audio_v2.py`
- `dgca/vision.py`
- `dgca/legacy_agent.py`

---

## 14. Forbidden Paths & Anti-Shortcut Invariants

1. `dgca/learning_runtime.py` must never import `CognitiveGraph`.
2. No direct calls to `graph.observe()`, `graph.observe_sequence()`, `graph.link()`, or `graph.add_contradiction()` from outside R1/R2.
3. No direct mutation of node or synapse attributes.
4. No generation calls during learning.
5. No bypassing `CanonicalObservationBridge` or `CanonicalR1RuntimeRoot`.

---

## 15. Production Diff Scope

Against baseline `cd05769dc09471592b92a9b07f720660bd5d57eb`:
- **Added:** `dgca/learning_runtime.py`
- **Modified:** `dgca/system_runtime.py`
- **Byte-identical:** All other files in `dgca/**`.

---

## 16. Formal Semantics Registry & Canonical Digest

The RIC-03 learning runtime semantics registry freezes 21 architectural dimensions:

```python
RIC03_LEARNING_SEMANTICS_REGISTRY: dict[str, Any] = {
    "authorization_default": "DENY_ALL",
    "authorization_owner": "CanonicalLearningAuthorizer",
    "auto_identity_policy": "SESSION_NONCE_PLUS_MONOTONIC_INDEX",
    "capability_lifetime": "HOST_EPHEMERAL_PER_RUNTIME_INSTANCE",
    "capability_persistence": "NEVER_SERIALIZED_OR_CHECKPOINTED",
    "chat_learning_policy": "STRICTLY_TRANSIENT_NO_LEARNING_AUTHORITY",
    "checkpoint_policy": "CANONICAL_R1_SCHEMA_1_2_0_CONSERVED",
    "external_identity_policy": "EXTERNAL_PREFIXED_STABLE_IDENTIFIER",
    "generation_policy": "ZERO_GENERATION_INGRESS_PERSISTENCE_ONLY",
    "identity_policy": "CONTENT_INDEPENDENT_OCCURRENCE_KEY",
    "learning_semantics_owner": "CognitiveGraph",
    "mutation_authority": "CanonicalR1RuntimeRoot",
    "observation_mode": "AUTHORIZED_PERSISTENT",
    "observation_owner": "CanonicalObservationBridge",
    "operation_concurrency_policy": "SYSTEM_OPERATION_MUTUAL_EXCLUSION_FAIL_CLOSED",
    "protocol_version": "RIC03-LEARN-1.0",
    "request_owner": "CanonicalLearningRuntime",
    "result_lifecycle": "IMMUTABLE_LEARNING_RESULT_OBSERVATION_CLOSED_FINALLY",
    "same_occurrence_conflict_policy": "FAIL_CLOSED_CAUSAL_VIOLATION",
    "same_occurrence_same_descriptor_policy": "PERSISTENT_REPLAY_NOOP",
    "supported_modalities": ["text"],
}
```

### Canonical Digest
Computed via `hashlib.sha256(json.dumps(RIC03_LEARNING_SEMANTICS_REGISTRY, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()`:
`ac9927cf5f350bd63d3ab6d15d311989487f9b7123f59472bda1c78c7b6e90ba`

---

## 17. Verification Criteria & Acceptance Ledger

Full verification requires:
1. 55 dedicated tests in `tests/test_ric03_learning_runtime.py` covering Groups A through H.
2. Full repository regression suite passing with 0 failures, 0 errors, 0 skips.
3. R3 semantics digest matching `fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc`.
4. RFC13 signature `3adbfcfd1f24802a` and RFC14 signature `46213188cdb02ee8` preserved.
5. SCTT 8/8 learned associations and 4/4 OOD probes preserved.
6. Clean Ruff check across `dgca/`, `tests/`, `experiments/`, and `scripts/`.
