# DGCA — RIC-02: Canonical System Runtime & CognitiveAgent Boundary Architecture

**Document ID:** `RIC-02-ARCH-2.0`  
**Status:** FROZEN / ADOPTED  
**Authoritative Baseline:** `006c16b8bba14ebdc78594604962437dd3e4d4ac`  
**Git Tag:** `SCTT00-VR01-VERIFIED`  
**Domain:** System Composition & Host Runtime Architecture  

---

## 1. Purpose & Problem Statement

Prior to RIC-02, `CognitiveAgent` in `dgca/agent.py` violated architectural single-responsibility principles by acting as both:
1. The external user-facing conversational façade (`chat()`, `__call__()`, `last_turn`); and
2. The canonical system composition, bootstrap, and lifecycle owner (instantiating `CognitiveGraph`, initializing the quantity backbone, extracting persistent payloads, computing state digests, creating R1 provenance epochs, constructing `CanonicalR1RuntimeRoot`, and restoring checkpoints).

This composition coupling caused:
- Internal authority leakage: tests and experimental harnesses accessed cognition through private agent properties (`agent._root`, `agent._chat_runtime`, `agent._chat_runtime._graph`).
- Contamination of the public user boundary with host engineering infrastructure.
- Inability to cleanly evolve host runtime composition without mutating the end-user agent surface.

RIC-02 formalizes an architectural boundary separation by introducing `CanonicalSystemRuntime` in `dgca/system_runtime.py` and reducing `CognitiveAgent` in `dgca/agent.py` to a strictly thin external façade.

---

## 2. Target System Architecture

```text
External Caller / User
      |
      v
CognitiveAgent (Thin Façade, __slots__ = ("_runtime",))
      |
      v
CanonicalSystemRuntime (Host-Side Composition Runtime)
      |
      +---- CanonicalChatRuntime (Conversational Ingress, RFC13, RFC14)
      |
      +---- CanonicalR1RuntimeRoot (System Integrity & Causal Lineage)
                    |
                    +---- CognitiveGraph (Symbolic & Episodic Substrate)
                    |
                    +---- CausalCommitLedger (Epoch & Transaction Ledger)
```

### Component Invariants

1. **`CognitiveAgent`:**
   - Must contain **no** cognitive algorithms, graph logic, bootstrap logic, checkpoint parsing, causal epoch construction, or cognitive routing.
   - Must hold only `self._runtime: CanonicalSystemRuntime`.
   - Must **not** import any cognitive modules (`graph`, `numbers`, `persistence`, `causal_identity`, `observation`, `completion`, `generation`, `recurrent`, `loop`).
   - Public API strictly conserved: `CognitiveAgent()`, `CognitiveAgent.from_checkpoint(path)`, `agent.chat(text)`, `agent(text)`, `agent.last_turn`.
   - Absolutely no `learn()`, `perceive_*()`, raw graph, or ledger APIs exposed.

2. **`CanonicalSystemRuntime`:**
   - Host-side composition runtime owning no cognition and introducing no new cognitive state.
   - Owns `CanonicalR1RuntimeRoot` and `CanonicalChatRuntime`.
   - Sole authority for fresh canonical bootstrap (`CanonicalSystemRuntime.fresh()`).
   - Sole authority for canonical checkpoint restore (`CanonicalSystemRuntime.from_checkpoint(path)`).
   - Sole authority for canonical checkpoint save (`runtime.save_checkpoint(path)`).
   - Delegates conversational execution (`chat()`) directly and exactly once to `CanonicalChatRuntime.chat()`.
   - Exposes diagnostic `last_turn` by delegation.

---

## 3. Lifecycle & Bootstrap Contracts

### 3.1 Fresh Canonical Bootstrap Contract (`CanonicalSystemRuntime.fresh()`)
The fresh canonical bootstrap sequence must exactly reproduce the canonical R1/R3 sequence:
1. `graph = CognitiveGraph(enable_prediction=False)`
2. `init_quantity_backbone(graph)`
3. `persistent_payload = extract_canonical_persistent_payload(graph)`
4. `state_digest = compute_checkpoint_state_digest(persistent_payload)`
5. `epoch = create_native_r1_provenance_epoch(state_digest)`
6. `ledger = CausalCommitLedger(epoch=epoch)`
7. `lifecycle_guard = RuntimeLifecycleGuard()`
8. `runtime_root = CanonicalR1RuntimeRoot(graph=graph, ledger=ledger, observation_protocol_version="R2-OBS-1.0", lifecycle_guard=lifecycle_guard)`
9. `chat_runtime = runtime_root.create_chat_runtime(session_nonce=session_nonce)`
10. Construct `CanonicalSystemRuntime(runtime_root=runtime_root, chat_runtime=chat_runtime)`.

### 3.2 Canonical Checkpoint Restore Contract (`CanonicalSystemRuntime.from_checkpoint(path)`)
1. Delegate directly to `restore_canonical_r1_checkpoint(filepath=path, expected_observation_protocol_version="R2-OBS-1.0", enable_prediction=False)`.
2. Obtain `runtime_root`.
3. Create `chat_runtime = runtime_root.create_chat_runtime(session_nonce=session_nonce)`.
4. Construct and return `CanonicalSystemRuntime`.

### 3.3 Canonical Checkpoint Save Contract (`runtime.save_checkpoint(path)`)
1. Delegate directly to `save_canonical_r1_checkpoint(self._runtime_root, filepath=path)`.
2. Return bundle digest.

### 3.4 Conversational Chat Contract (`runtime.chat(text)`)
1. Delegate directly and exactly once to `self._chat_runtime.chat(text)`.
2. Perform zero content inspection, zero routing, zero manual graph mutation, and zero fallback modification.
3. Diagnostic `last_turn` reflects `self._chat_runtime.last_turn`.

---

## 4. Cognitive Freeze & Production Immutability

The following production files remain frozen and byte-identical to the authoritative baseline:
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

Authorized production diff against `006c16b8bba14ebdc78594604962437dd3e4d4ac`:
- `dgca/agent.py` (MODIFIED — refactored to thin façade)
- `dgca/system_runtime.py` (ADDED — CanonicalSystemRuntime implementation)
- `dgca/__init__.py` (OPTIONAL — export CanonicalSystemRuntime)

---

## 5. Verification Invariants

1. `R3_MIN_RUNTIME_SEMANTICS_DIGEST` must remain unchanged:
   `fc357c3bf84a9e43488b58502f82b8d07d2936fcd12613d7050bf006de72efcc`
2. Fresh persistent state digest must remain identical:
   `975d6953a4dd34d39f6fa678fb37fe1289118b1b579ddc6576b4cb892f76ac32`
3. SCTT trained checkpoint state digest must remain identical:
   `548e6fee4b450ba841857ec209df9d0ffb467de62a8639d32fe290eb1b681c3a`
4. SCTT 8 learned probe responses must remain identical:
   - dog -> dog canine
   - cat -> cat feline
   - robin -> robin bird
   - rose -> rose flower
   - apple -> apple fruit
   - car -> car vehicle
   - ice -> ice solid
   - water -> water liquid
5. OOD responses must remain identical (pizza, computer, chair, ocean).
6. Post-training chat persistent delta must remain zero.
7. RFC15 remains unmaterialized, RFC16 remains unused.
8. RFC13 behavioral signature: `3adbfcfd1f24802a`
9. RFC14 behavioral signature: `46213188cdb02ee8`
