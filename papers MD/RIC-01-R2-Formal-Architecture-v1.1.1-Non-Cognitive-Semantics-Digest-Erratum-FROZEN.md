# DGCA — RIC-01 / R2
## Formal Architecture v1.1.1 — Non-Cognitive Semantics Digest Erratum
### FROZEN

**Parent architecture:**  
`RIC-01-R2-Canonical-Ingress-Observation-Bridge-Formal-Architecture-v1.1-FROZEN.md`

**Purpose:** correct one impossible SHA-256 literal in Section 3.1.  
**Semantic change:** NONE  
**Cognitive-law change:** NONE  
**R1 change:** NONE  
**Observation protocol version change:** NONE  
**Checkpoint schema change:** NONE  
**R3 authorization:** NONE

---

# 1. Erratum Scope

The parent v1.1 document correctly freezes the exact R2 observation semantics registry and correctly specifies that its fingerprint is:

```text
SHA-256(
    canonical_json_bytes(
        R2_OBSERVATION_SEMANTICS_REGISTRY
    )
)
```

using the R1 canonical JSON profile.

However, the printed digest literal in v1.1 contains a two-hex-character transcription suffix error.

Parent v1.1 printed:

```text
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b7c
```

This is 66 hexadecimal characters and therefore cannot be a SHA-256 hexadecimal digest.

The exact canonical registry from parent Section 3.1 recomputes to:

```text
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b
```

which is exactly 64 lowercase hexadecimal characters.

---

# 2. Authoritative Corrected Literal

The following line supersedes only the incorrect digest literal in parent v1.1:

```text
R2_OBSERVATION_SEMANTICS_DIGEST =
bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b
```

No other line, policy, identifier, contract, or semantic rule from v1.1 is changed by this erratum.

---

# 3. Exact Registry Remains the Parent v1.1 Registry

The authoritative registry remains exactly:

```python
{
  "protocol_version": "R2-OBS-1.0",
  "event_descriptor_version": "R2-EVENT-1.0",
  "micro_descriptor_version": "R2-MICRO-1.0",
  "mutation_descriptor_version": "R2-MUT-1.0",
  "receipt_batch_version": "R2-RB-1.0",
  "result_version": "R2-RESULT-1.0",
  "supported_modalities": ["text", "code"],
  "operation_kinds": [
    "R2_TRANSIENT_ONLY",
    "R2_AUTHORIZED_PERSISTENT"
  ],
  "persistent_transaction_granularity": "ONE_ENCODED_INGRESS_EVENT",
  "observation_relation_policy": {
    "simultaneous": "ALL_ORDERED_PAIRS",
    "sequence_same_step": "ALL_ORDERED_PAIRS",
    "sequence_cross_step": "ALL_ORDERED_CROSS_PAIRS",
    "self_ref": "EXCLUDED"
  },
  "rfc11_evidence_policy": {
    "simultaneous": "ALL_ORDERED_PAIRS",
    "sequence_same_step": "ALL_ORDERED_PAIRS",
    "sequence_adjacent_step": "ALL_ORDERED_CROSS_PAIRS",
    "sequence_nonadjacent_step": "EXCLUDED_TEMPORAL_DERIVED",
    "synthetic_event_role": "EXCLUDED_DERIVED",
    "concept_generalization_generated": "EXCLUDED_INTERNAL_DERIVED"
  },
  "tbr_policy": {
    "authority": "EXPLICIT_CANONICAL_MICROEPISODE_STRUCTURE_ONLY",
    "simultaneous": "ONE_BINDING_IF_AT_LEAST_TWO_POSITIVE_OCCURRENCES",
    "sequence": "ONE_BINDING_PER_ADJACENT_TRANSITION",
    "contradiction": "ONE_BINDING_PER_EXPLICIT_PAIR",
    "coactivation_only": "FORBIDDEN",
    "member_scope_validation": "REQUIRED"
  },
  "receipt_order": [
    "POSITIVE_NODE_OCCURRENCES",
    "CONTRADICTION_ENDPOINT_OCCURRENCES",
    "LIVE_GATE_OPEN_OBSERVATION_RELATION_EDGE_RECEIPTS"
  ],
  "sdcr_cardinality": "ONE_PER_OBSERVABLE_MICROEPISODE",
  "projection_timing": "AFTER_PERSISTENT_COMMIT_OR_REPLAY_DECISION",
  "projection_failure": "PERSISTENT_COMMIT_REMAINS_AUTHORITATIVE_CLOSE_PARTIAL_SDCRS",
  "transient_replay": "CURRENT_STATE_RECONSTRUCTION",
  "authorization_default": "DENY_ALL"
}
```

Top-level key count:

```text
18
```

---

# 4. Canonical Hashing Rule

Authoritative calculation:

```python
payload = json.dumps(
    R2_OBSERVATION_SEMANTICS_REGISTRY,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")

digest = hashlib.sha256(payload).hexdigest()
```

Required:

```text
len(digest) == 64
digest == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"
```

Forbidden:
- XOR calibration;
- hash translation;
- truncation/extension;
- expected-value short circuit;
- source-dependent normalization chosen to force a preselected digest.

---

# 5. Compatibility Classification

This erratum changes no runtime observation semantics.

Therefore:

```text
R2_OBSERVATION_PROTOCOL_VERSION remains "R2-OBS-1.0"
checkpoint_schema_version remains "1.2.0"
runtime_contract_version remains "1.2.0"
CAUSAL_IDENTITY_PROTOCOL_DIGEST remains unchanged
R1 LITERAL_DOMAIN_REGISTRY remains unchanged
cognitive baseline remains unchanged
```

No checkpoint migration is required.

The R2 semantics digest is diagnostic/non-cognitive compatibility evidence only.

---

# 6. Release Rule

Any R2 implementation claiming v1.1.1 conformance MUST:
1. embed the exact 18-key registry above;
2. recompute direct SHA-256 from canonical JSON;
3. obtain the corrected 64-hex digest exactly;
4. fail release if either registry or digest differs.

---

# 7. Formal Verdict

```text
R2_V1_1_DIGEST_ERRATUM_CONFIRMED
R2_FORMAL_ARCHITECTURE_V1_1_1_FROZEN
SEMANTIC_DELTA = 0
COGNITIVE_DELTA = 0
R1_DELTA = 0
CHECKPOINT_SCHEMA_DELTA = 0
```
