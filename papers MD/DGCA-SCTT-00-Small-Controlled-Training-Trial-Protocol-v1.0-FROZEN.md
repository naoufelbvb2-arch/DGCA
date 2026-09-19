# DGCA — SCTT-00
## Small Controlled Training Trial 00
### Canonical Learn → Persist → Reload → Retrieve → Generate
### Experimental Protocol v1.0 — FROZEN

**Repository baseline:** `833241d54309d72715c42dc5f2b939c3179e257d`  
**RIC-01:** `CLOSED`  
**R3-Min:** `CLOSED`  
**RFC-15:** `DEFERRED / FORBIDDEN IN THIS TRIAL`  
**Production cognitive code changes:** `FORBIDDEN`  
**Trial status:** `FROZEN / EXECUTION AUTHORIZED`

---

# 1. Scientific Question

Can a fresh DGCA learn a tiny set of text relations through the canonical R2 persistent path, save the learned state in a canonical schema-1.2.0 checkpoint, destroy the training runtime, reload the checkpoint through `CognitiveAgent.from_checkpoint()`, and retrieve/express the learned targets through the ordinary R3-Min path:

```text
R2 TRANSIENT_ONLY
→ RFC13
→ RFC14
→ SurfaceChunk.rendered_text
```

The first trial deliberately does **not** test fluent question answering.

---

# 2. Frozen Fact Bank

| ID | Training sentence | Probe cue | Expected target |
|---|---|---|---|
| F01 | `A dog is a canine.` | `dog` | `canine` |
| F02 | `A cat is a feline.` | `cat` | `feline` |
| F03 | `A robin is a bird.` | `robin` | `bird` |
| F04 | `A rose is a flower.` | `rose` | `flower` |
| F05 | `An apple is a fruit.` | `apple` | `fruit` |
| F06 | `A car is a vehicle.` | `car` | `vehicle` |
| F07 | `Ice is solid.` | `ice` | `solid` |
| F08 | `Water is liquid.` | `water` | `liquid` |

No other training text is permitted.

---

# 3. Encoder Preflight — Hard Gate

Before the first persistent exposure, run all eight sentences through the current text encoder without persistent mutation.

For each fact record the exact emitted `SensoryEpisode` descriptors.

Required for all F01..F08:

```text
non-empty encoder output
subject represented
target represented
deterministic repeated encoding
```

If any fact does not encode both intended terms into usable observable structure:

```text
SCTT00_BLOCKED
failure_stage = E0_ENCODER
```

STOP before training.

---

# 4. Fresh Canonical Training Runtime

Construct the training runtime with the same canonical fresh boot sequence as R3-Min:

```text
CognitiveGraph(enable_prediction=False)
→ init_quantity_backbone(graph)
→ extract_canonical_persistent_payload
→ state digest
→ create_native_r1_provenance_epoch
→ CausalCommitLedger
→ CanonicalR1RuntimeRoot(
      observation_protocol_version="R2-OBS-1.0",
      lifecycle_guard=RuntimeLifecycleGuard()
   )
```

No legacy agent. No prediction side path.

---

# 5. Training Authority

Training must use:

```text
CanonicalR1RuntimeRoot.create_observation_bridge(authorizer=...)
ExecutionMode.AUTHORIZED_PERSISTENT
```

with a private opaque capability.

The experiment-only authorizer returns literal `True` only if:
- `capability is expected_capability`;
- `modality == "text"`;
- `operation_kind == "R2_AUTHORIZED_PERSISTENT"`.

Forbidden:
- `CognitiveAgent.chat()` for training;
- `LegacyCognitiveAgent`;
- direct `graph.observe()` / `graph.observe_sequence()` calls by the harness;
- `graph._link()`;
- manual Edge construction;
- raw graph persistence.

---

# 6. Baseline Probe

Before training, use a separate fresh ordinary `CognitiveAgent()` and probe:

```text
dog
cat
robin
rose
apple
car
ice
water
```

If any expected target already appears in its matching output:

```text
SCTT00_BLOCKED
reason = BASELINE_CONTAMINATION
```

---

# 7. Exposure Schedule

Exactly five independent exposures per fact:

```text
8 facts × 5 cycles = 40 authorized observations
```

Round-robin order F01..F08 for cycles 1..5.

Identity:

```text
boundary_namespace = "DGCA:SCTT00:TRAIN:v1"
source_occurrence_key = "SCTT00:<FactID>:E<ExposureNumber>"
source_event_key = "training_fact"
ingress_boundary = "SCTT00_CANONICAL_TEXT_TRAINING"
```

Each exposure must be an independent Root occurrence.

---

# 8. Per-Exposure Gate

Require for each observation:

```text
status == PERSISTENT_EXECUTED
mode == AUTHORIZED_PERSISTENT
persistent_phase == COMMITTED
persistent_transaction_id is not None
persistent_executed is True
```

Record all causal and transaction IDs.

Always close the returned observation result.

Expected total:

```text
40 PERSISTENT_EXECUTED
0 PERSISTENT_REPLAY
0 authorization failures
```

---

# 9. No Mid-Trial Tuning

After exposure 1 begins:

```text
NO dataset edits
NO budget edits
NO threshold edits
NO encoder edits
NO RFC13 edits
NO RFC14 edits
NO Law edits
NO extra repetitions for failures
```

---

# 10. Storage Audit

After cycle 5 record for each pair:
- subject node;
- target node;
- direct edges in both directions;
- edge kind;
- `W`;
- `n`;
- contexts;
- `ctx_hits`.

Also record:
- node count;
- edge count;
- logical time;
- RFC11 pending state;
- assembly count;
- committed transaction count;
- canonical persistent digest.

Primary persistence gate:

```text
8/8 intended subject-target relationships persist
in a form derivable from the frozen encoder emissions.
```

Assembly formation is diagnostic only.

---

# 11. Canonical Save

Require:

```text
runtime health == HEALTHY
canonical lineage == VALID
```

Save only with:

```python
save_canonical_r1_checkpoint(...)
```

Recommended output:

```text
data/checkpoints/SCTT00-trained.json
```

Record:
- checkpoint bundle digest;
- state digest;
- provenance digest;
- file SHA-256;
- schema/runtime/observation versions.

Then destroy all training-runtime references.

---

# 12. Primary Post-Restore Retrieval

Restore only with:

```python
CognitiveAgent.from_checkpoint("data/checkpoints/SCTT00-trained.json")
```

Probe exactly:

```text
dog
cat
robin
rose
apple
car
ice
water
```

Record output and full `R3TurnResult`.

---

# 13. Correct Recall Definition

PASS iff:
- expected target appears as a complete output token;
- expected target was absent from the input cue;
- no competing target from another trained pair appears.

Examples:

```text
dog → dog canine      PASS
dog → canine          PASS
dog → dog             FAIL
dog → feline          FAIL_SPECIFICITY
dog → canine feline   FAIL_SPECIFICITY
```

Strict gate:

```text
8/8 correct learned recalls
```

---

# 14. OOD Safety Controls

Probe exactly:

```text
stone
horse
train
banana
```

None may emit any trained target:

```text
canine
feline
bird
flower
fruit
vehicle
solid
liquid
```

Required:

```text
4/4 OOD safe
```

---

# 15. Ordinary-Chat Persistent Conservation

For every post-training probe:

```text
persistent digest before == after
ledger unchanged
logical time unchanged
RFC11 pending state unchanged
N_total unchanged
```

Any delta caused by ordinary R3 chat:

```text
E6_SAFETY
SCTT00_FAIL
```

---

# 16. Clean-Restore Determinism

Restore the exact checkpoint into a second fresh `CognitiveAgent`.

Repeat all eight primary cues.

Required:
- same output strings;
- same completion closure reasons;
- same generation closure reasons;
- same classification.

Causal IDs may differ.

Gate: `8/8`.

---

# 17. Exploratory Natural Questions — Diagnostic Only

After scored gates:

```text
What is a dog?
What is a cat?
What is a robin?
What is an apple?
```

Record only. Do not use for PASS/FAIL.

---

# 18. Failure Taxonomy

```text
E0_ENCODER
E1_PERSISTENCE
E2_RETRIEVAL
E3_GENERATION
E4_SPECIFICITY
E5_RESTORE
E6_SAFETY
E7_NONDETERMINISM
```

Every failed primary pair must be assigned to the first failing stage.

---

# 19. Success Gates

`SCTT00_PASS` requires:

```text
Encoder preflight                    8/8
Baseline uncontaminated              8/8
Authorized observations            40/40
Replay substitutions                 0
Persistence relation gate            8/8
Canonical checkpoint save          PASS
Canonical checkpoint restore       PASS
Primary learned recall               8/8
OOD safety                           4/4
Post-training chat persistent delta    0
Restore determinism                  8/8
Runtime health                   HEALTHY
Canonical lineage                  VALID
RFC15 calls                            0
Production cognitive code changes      0
```

---

# 20. Verdict Vocabulary

Exactly one:

```text
SCTT00_PASS
SCTT00_FAIL
SCTT00_BLOCKED
```

---

# 21. Allowed Scope

Allowed execution artifacts only:

```text
experiments/sctt00.py
tests/test_sctt00_harness.py
experiments/results/sctt00-results.json
papers MD/SCTT-00-EXECUTION-REPORT.md
data/checkpoints/SCTT00-trained.json
```

Any required production `dgca/` change means:

```text
SCTT00_BLOCKED
```

Do not patch the model during this experiment.
