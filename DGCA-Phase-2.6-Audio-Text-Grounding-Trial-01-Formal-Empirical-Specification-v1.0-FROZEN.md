# DGCA Phase 2.6 — Audio↔Text Grounding Trial 01

## Formal Empirical Specification v1.0

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Trial:** `ATG01` — Audio↔Text Grounding Trial 01  
**Document Type:** Formal Empirical Specification  
**Version:** 1.0  
**Status:** **FORMAL SPECIFICATION — CANDIDATE FOR FREEZE**  
**Parent Design:** `DGCA-Phase-2.6-Audio-Text-Grounding-Trial-01-Architectural-Empirical-Design-v1.0.md`  
**Audio Encoder:** `DGCA Audio Encoder v2 — IMPLEMENTED / VERIFIED / FROZEN / REAL-AUDIO VALIDATED`  
**English Encoder:** `DGCA English Encoder v2 — IMPLEMENTED / VERIFIED / FROZEN`  
**Parent Audio Trial:** `SRA01 — REAL_AUDIO_REPRESENTATION_DEMONSTRATED`  
**Audio Encoder Commit:** `8c2c48f`  
**SRA01 Artifact Commit:** `627e678`  
**Historical Cognitive Signature:** `915119d40643cb97`  
**Training / Backpropagation:** `0`  
**Pretrained ASR / Alignment:** `0`  
**Manual Cross-Modal Edge Injection:** `0`  
**New Persistent Cognitive Primitives:** `0`  
**New Persistent Fields:** `0`  
**New Normative Laws:** `0`  
**Production-Graph Mutation:** `0`  
**Primary Data Source:** `Google Speech Commands v0.02`  
**Primary Sample Rate:** `16 kHz`  
**Primary Grounded Concepts:** `10`  
**Grounding Recordings:** `40`  
**Held-Out Recordings:** `20`  
**OOD Recordings:** `10`  
**Primary Manifest Source Recordings:** `70`

---

# 1. Formal Scientific Question

ATG01 MUST answer:

\[
\boxed{
\textbf{Can DGCA learn a persistent lexical association from repeated real spoken-word/text co-occurrence and retrieve the correct text concept from a held-out utterance produced by a globally unseen speaker?}
}
\]

The target causal chain is:

\[
RawSpeech
\rightarrow
AudioEncoderV2
\rightarrow
AudioTemporalIR
\rightarrow
ExistingDGCASensorySequence
\]

then, only during grounding:

\[
AudioExperience
+
TextExperience
+
IndependentGroundingContext
\rightarrow
ExistingDGCALearning
\]

and during held-out retrieval:

\[
HeldOutAudio
\rightarrow
ExistingAudioMemory
\rightarrow
CrossModalEvidence
\rightarrow
TextConcept
\]

---

# 2. Primary Claim Boundary

ATG01 may establish:

\[
\boxed{
RealSpokenWord\leftrightarrow LexicalConceptGrounding
}
\]

and:

\[
\boxed{
UnseenSpeakerAudio\rightarrow TextConceptTransfer
}
\]

It MUST NOT claim:

- open-vocabulary ASR;
- sentence transcription;
- phoneme recognition;
- accent/dialect recognition;
- speaker identification;
- source separation;
- speech generation;
- human auditory equivalence.

---

# 3. Dataset Authority

ATG01 uses:

```text
Google Speech Commands v0.02
```

The acquisition script MUST use the official v0.02 archive or a byte-equivalent official mirror.

Expected official archive identifier:

```text
speech_commands_v0.02.tar.gz
```

Audio source properties used by ATG01:

```text
WAV
mono
16000 Hz
isolated spoken words
```

No TensorFlow model is used.

---

# 4. Speaker Identity Convention

For Speech Commands filenames of the form:

```text
<speaker_id>_nohash_<utterance_index>.wav
```

the experimental speaker identity is:

```text
<speaker_id>
```

i.e. the filename prefix before:

```text
_nohash_
```

This metadata is used only for split integrity.

It MUST NOT enter DGCA cognition.

---

# 5. Frozen Grounded Concept Set

The exact grounded lexical concepts are:

```text
C00 bird
C01 cat
C02 dog
C03 tree
C04 bed
C05 house
C06 no
C07 go
C08 on
C09 off
```

Total:

\[
\boxed{10}
\]

No concept substitution is permitted after specification freeze.

---

# 6. Frozen OOD Concept Set

The exact ungrounded OOD words are:

```text
O00 yes
O01 up
O02 down
O03 left
O04 right
O05 stop
O06 one
O07 two
O08 three
O09 happy
```

Total:

\[
\boxed{10}
\]

These words MUST NEVER participate in grounding.

No persistent `unknown` concept is created.

---

# 7. Why OOD Exists

ATG01 must detect forced lexical mapping.

For OOD audio:

\[
Audio_{OOD}
\]

preferred lawful outcomes are:

```text
NO_TEXT_CONCEPT_RETRIEVED
AMBIGUOUS
```

A learned grounded concept returned as a unique dominant answer is counted as an OOD false association.

---

# 8. Source-Item Accounting

For each grounded concept:

```text
4 grounding recordings
2 held-out recordings
```

Thus:

\[
10\times4=40
\]

grounding recordings,

\[
10\times2=20
\]

held-out recordings.

Plus:

\[
10
\]

OOD recordings.

Total:

\[
\boxed{70\ genuine\ recorded\ source\ items}
\]

---

# 9. Global Speaker-Disjoint Requirement

ATG01 requires, if dataset availability satisfies the rule:

\[
\boxed{70\ unique\ speaker\ IDs}
\]

Therefore:

\[
GroundingSpeakers
\cap
HeldOutSpeakers
=
\varnothing
\]

\[
GroundingSpeakers
\cap
OODSpeakers
=
\varnothing
\]

\[
HeldOutSpeakers
\cap
OODSpeakers
=
\varnothing
\]

and no speaker appears in two selected source items.

---

# 10. Speaker-Uniqueness Failure Rule

Speaker uniqueness is a hard protocol requirement for v1.0.

If deterministic selection cannot produce 70 unique eligible speaker IDs:

```text
ATG01_DATA_SPLIT_BLOCKED
```

Do NOT silently relax uniqueness.

A future v1.1 may define a weaker split if necessary.

---

# 11. Audio Eligibility

Every selected WAV MUST satisfy:

```text
sample_rate = 16000
channel_count = 1
finite samples
valid decode
genuine recorded speech
word folder matches experimental metadata label
```

Recommended duration eligibility:

\[
0.30s \le T \le 1.20s
\]

A source slightly shorter than one second is lawful and MUST NOT be padded merely to create equal duration.

---

# 12. No Grounding Audio Augmentation

Forbidden for all primary 40 grounding items:

- padding to fixed one-second identity for semantic convenience;
- time stretch;
- pitch shift;
- noise augmentation;
- denoising;
- class-dependent gain;
- resampling;
- voice conversion;
- silence trimming based on word content;
- forced alignment.

Use the original lawful waveform.

---

# 13. Deterministic Selection Seed

Root selection seed:

```text
DGCA-ATG01-SELECTION-v1.0
```

Candidate digest:

\[
H=
SHA256(
seed
||":"
||role
||":"
||concept
||":"
||speakerID
||":"
||filename
)
\]

Sort ascending hexadecimal digest.

---

# 14. Deterministic Global Selection Algorithm

Maintain:

```text
USED_SPEAKERS = {}
```

Use canonical grounded concept order C00..C09.

## Stage A — Grounding

For rounds:

```text
G1
G2
G3
G4
```

iterate concepts C00..C09.

For each concept choose the lowest-hash eligible file whose speaker is not in `USED_SPEAKERS`.

Add speaker to `USED_SPEAKERS`.

Result:

\[
40\ unique\ grounding\ speakers
\]

## Stage B — Held-Out

For rounds:

```text
H1
H2
```

iterate C00..C09.

Choose lowest-hash remaining eligible file with globally unused speaker.

Result:

\[
20\ new\ heldout\ speakers
\]

## Stage C — OOD

Iterate O00..O09.

Choose lowest-hash eligible file with globally unused speaker.

Result:

\[
10\ new\ OOD\ speakers
\]

Final:

\[
|USED\_SPEAKERS|=70
\]

---

# 15. Lawful Candidate Rejection

Before manifest freeze only, a candidate may be rejected for:

- corrupt decode;
- wrong sample rate;
- wrong channel count;
- invalid duration;
- NaN/Inf;
- missing provenance;
- duplicate speaker already used.

The selector MUST log every rejection and advance to the next candidate in the same deterministic hash order.

No listening-based rejection.

---

# 16. Canonical Item IDs

Grounding:

```text
ATG01-G-C00-R1
...
ATG01-G-C09-R4
```

Held-out:

```text
ATG01-H-C00-01
ATG01-H-C00-02
...
ATG01-H-C09-02
```

OOD:

```text
ATG01-OOD-O00
...
ATG01-OOD-O09
```

Cognitive stream scope IDs MUST use opaque IDs derived from these roles without lexical word names.

---

# 17. Manifest Freeze

Before any primary graph learning:

write:

```text
atg01_manifest.json
```

containing all 70 source items.

Required:

```text
40 grounding
20 held-out
10 OOD
70 unique speakers
```

Compute:

```text
ATG01ManifestSHA256
```

The manifest is immutable after freeze.

---

# 18. Required Manifest Fields

Each source item MUST include:

```text
trial_id
role
concept_code
semantic_label_eval_or_grounding_only
source_dataset
dataset_version
source_file
source_sha256

speaker_id_eval_only
sample_rate
channels
duration_s

selection_seed
selection_hash
selection_round

audio_encoder_input_fields
text_encoder_input_fields_if_grounding

eligible = true
rejection_history_if_any
```

The manifest MUST clearly show:

```text
audio_encoder_input_fields
```

contains no lexical label.

---

# 19. Label-Leakage Firewall

Audio Encoder v2 receives only:

```text
waveform
sample_rate=16000
channel_count=1
opaque stream_scope_id
stream controls
```

It MUST NOT receive:

```text
word label
folder name
speaker ID
filename
transcript
concept code
expected result
text IR
gold class
```

---

# 20. Text Encoder Input

During grounding only, English Encoder v2 receives exactly one lowercase word from C00..C09.

Examples:

```text
bird
cat
dog
```

No sentence or definition is supplied.

---

# 21. Text Minimality

Forbidden:

```text
"this sound means bird"
"the spoken word is bird"
"bird animal"
phonetic transcription
pronunciation guide
```

The text experience is exactly the lexical item.

---

# 22. Clean Experimental Graph B0

Before ATG01 primary grounding:

create a fresh isolated experimental graph.

Required:

```text
prior ATG01 memory = 0
prior SRA01 learning memory = 0
prior RI01 learning memory = 0
grounded C00..C09 trial associations = 0
```

The architecture/code is normal DGCA; only learned trial state is clean.

---

# 23. Production Isolation

ATG01 MUST NOT operate on the production learned graph.

Required:

\[
\boxed{
\Delta PersistentProductionGraph=0
}
\]

---

# 24. B0 Audit

Record:

```text
node count
edge count
assembly count
cross-modal edge count
active transient count
graph digest
historical cognitive architecture signature
```

Write:

```text
atg01_b0.json
```

---

# 25. Grounding Authority

ATG01 MUST reuse the lawful cross-modal grounding mechanism already established for prior DGCA real-image grounding.

The modality changes from visual experience to audio sequence experience.

Authority does not change.

Forbidden:

```text
manual graph.link(...)
manual edge creation
paired_text inside audio encoder
direct label assignment to audio descriptors
```

---

# 26. Grounding Orchestrator Contract

A grounding episode receives:

```text
AudioExperience
TextExperience
GroundingContextID
```

and invokes only existing DGCA learning authority.

The orchestrator itself has no learned state and no semantic classifier.

---

# 27. Grounding Context IDs

Exactly 40 unique context IDs:

```text
ATG01-GCTX-001
...
ATG01-GCTX-040
```

One context represents one independent real co-occurrence episode.

No context is reused.

---

# 28. Independent Recurrence

If an edge has existing authorized context-set semantics:

\[
n(f,c)=|edge.contexts|
\]

then each ATG01 grounding context may contribute at most once.

Required:

\[
SameContextReplay
\Rightarrow
NoIndependentRecurrenceIncrement
\]

---

# 29. Grounding Curriculum

Four rounds are required.

Canonical concept indices:

\[
0..9
\]

Round order:

### Round 1
\[
0,1,2,3,4,5,6,7,8,9
\]

### Round 2
cyclic shift by 3:

\[
3,4,5,6,7,8,9,0,1,2
\]

### Round 3
cyclic shift by 6:

\[
6,7,8,9,0,1,2,3,4,5
\]

### Round 4
cyclic shift by 9:

\[
9,0,1,2,3,4,5,6,7,8
\]

Each concept therefore appears once per round.

---

# 30. Grounding Recording Assignment

For concept \(c\):

```text
R1 uses grounding selection round G1
R2 uses G2
R3 uses G3
R4 uses G4
```

No recording repeats.

---

# 31. Grounding Sequence Count

Exactly:

\[
\boxed{40\ grounding\ episodes}
\]

No extra exposure.

No replay for reinforcement.

No held-out exposure.

---

# 32. Grounding Checkpoints

Record after:

```text
G10
G20
G30
G40
```

where the number refers to executed grounding episodes in curriculum order.

Write canonical graph digests at each checkpoint.

---

# 33. Grounding Telemetry

For each episode record:

```text
grounding context ID
audio source trial ID
text concept code
audio event count
audio descriptor identities
audio sequence digest

text representation identity

cross-modal edges created
cross-modal edges reinforced
edge identities
edge weights before/after
edge.contexts before/after where applicable

persistent node delta
persistent edge delta
transient created/retired
transient leakage
```

---

# 34. No Grounding Failure Repair

If one grounding episode produces unexpected behavior:

record it.

Do NOT:

- replace recording;
- add an extra exposure;
- modify thresholds;
- modify retrieval;
- modify encoder;
- manually repair edge.

---

# 35. Transient Retirement

After each grounding episode:

all AudioTemporalIR/TextIR/compiler transient structures must retire under existing rules.

Required:

```text
transient leakage = 0
```

at stable checkpoint.

---

# 36. Cross-Modal Formation Gate

After G40, each of the 10 text concepts MUST have at least one persistent lawful cross-modal association attributable to ATG01 grounding contexts.

Required:

\[
10/10
\]

---

# 37. Independent Reinforcement Gate

For each concept, at least one cross-modal association path or equivalent persistent relational structure must show support from:

\[
\ge2
\]

independent grounding contexts by G40.

Required:

\[
10/10
\]

This gate does NOT require the same raw acoustic descriptor to appear in all four speakers.

---

# 38. Four-Exposure Accounting

For every concept:

all four unique context IDs must be traceable in grounding telemetry.

Required:

\[
4/4
\]

episodes executed per concept.

---

# 39. Retrieval Authority Audit

Before held-out scoring, run a read-only audit of:

- audio-event candidate discovery;
- sequence reinstatement;
- pattern completion;
- cross-modal candidate reachability;
- LESR applicability;
- IGSV applicability;
- exact tie behavior.

Write:

```text
atg01_retrieval_authority_audit.json
```

---

# 40. LESR Rule

LESR may be used only if the current implementation is modality-generic for the relevant cross-modal edges.

Do not modify LESR.

If code contains a visual-only assumption affecting audio:

```text
LESR_AUDIO_AUTHORITY = BLOCKED
```

---

# 41. IGSV Rule

IGSV may be used only for already-authorized modality-independent semantics such as independent context recurrence.

Vision-specific provenance grouping MUST NOT be copied into audio evidence without a separate proof.

If current IGSV implementation requires vision-specific provenance:

```text
IGSV_AUDIO_AUTHORITY = PARTIAL_OR_BLOCKED
```

Do not repair it during ATG01.

---

# 42. Retrieval Stack Outcome

Before primary retrieval set one:

```text
AUDIO_RETRIEVAL_STACK_AUTHORIZED
AUDIO_RETRIEVAL_STACK_PARTIAL
AUDIO_RETRIEVAL_STACK_BLOCKED
```

If `BLOCKED`, ATG01 may report grounding formation but cannot claim full retrieval demonstration.

---

# 43. Held-Out Evaluation Isolation

Each held-out probe runs:

- from fresh transient state;
- against a read-only clone/snapshot of the G40 learned graph;
- with learning disabled.

Required:

\[
\Delta PersistentEvaluationGraph=0
\]

---

# 44. Held-Out Audio→Text Probes

Exactly:

\[
\boxed{20}
\]

two per grounded concept.

No held-out audio appears in learning.

All held-out speakers are globally unseen.

---

# 45. Canonical Retrieval Procedure

For held-out audio:

1. AudioEncoderV2 produces AudioTemporalIR.
2. Compile lawfully to existing sensory/sequence representation.
3. Run existing reinstatement/candidate discovery.
4. Collect reachable text concepts among learned lexical concepts.
5. Apply frozen retrieval ranking.
6. If no text candidate: `NO_TEXT_CONCEPT_RETRIEVED`.
7. If exact top tie: `AMBIGUOUS`.
8. Else unique top text concept is returned.

No lexical fallback.

---

# 46. Held-Out Outcome Classes

Exactly:

```text
CORRECT_TEXT_CONCEPT_RETRIEVED
WRONG_TEXT_CONCEPT_RETRIEVED
NO_TEXT_CONCEPT_RETRIEVED
AMBIGUOUS
```

---

# 47. Candidate Reachability

For each probe record separately:

```text
correct concept stored?
correct concept reachable?
correct concept candidate?
correct concept rank
winner
score/evidence decomposition
```

A wrong winner with correct candidate present is not classified as representation failure automatically.

---

# 48. Primary Correctness Metrics

Report:

\[
Correct
\]

\[
Wrong
\]

\[
NoRetrieval
\]

\[
Ambiguous
\]

out of 20.

Also report concept-level:

```text
0/2
1/2
2/2
```

for each of 10 concepts.

---

# 49. Primary Demonstration Accuracy Gate

For full `AUDIO_TEXT_GROUNDING_DEMONSTRATED` candidate status:

\[
\boxed{Correct\ge12/20}
\]

and:

\[
\boxed{Wrong\le4/20}
\]

and:

\[
\boxed{CorrectConceptReachable\ge16/20}
\]

and at least:

\[
\boxed{8/10\ concepts}
\]

must achieve at least one correct held-out probe.

The remaining outcomes may be abstentions or ambiguity.

---

# 50. Statistical Reference

Under a simple 10-way uniform forced-choice null:

\[
p=0.1
\]

the probability of at least 12 correct in 20 is approximately:

\[
5.8\times10^{-8}
\]

This is reference evidence only.

ATG01 does not assume real errors are independent uniform random choices, and the system is permitted to abstain.

---

# 51. Strong Held-Out Result

A stronger descriptive status may be recorded if:

\[
Correct\ge16/20
\]

with:

\[
Wrong\le2/20
\]

but this is not required for trial validity.

---

# 52. Failure Localization

Every non-correct held-out probe MUST receive one evidence-based category:

```text
F-A AUDIO_REPRESENTATION_MISMATCH
F-B SEQUENCE_REINSTATEMENT_FAILURE
F-C CANDIDATE_DISCOVERY_FAILURE
F-D CROSSMODAL_ASSOCIATION_MISSING
F-E RANKING_LOSS
F-F SPECIFICITY_GENERICITY_LOSS
F-G EXACT_TIE_AMBIGUITY
F-H UNKNOWN_OTHER
```

---

# 53. Failure Classification Rules

### F-A
Held-out AudioTemporalIR has insufficient overlap/reinstatement with grounded acoustic memory before cross-modal candidate formation.

### F-B
Relevant acoustic evidence exists but ordered sequence/reinstatement fails.

### F-C
Correct text concept is stored/associated but never becomes candidate.

### F-D
Expected cross-modal association was not formed during G40.

### F-E
Correct candidate exists but unique wrong candidate ranks higher.

### F-F
Wrong ranking is traceable to generic/shared acoustic evidence overwhelming more specific evidence.

### F-G
Correct and one or more competitors have exact top support; system lawfully abstains.

### F-H
No prior class fits.

No repair inside ATG01.

---

# 54. Reverse Text→Audio Trial

After held-out Audio→Text probes, evaluate exactly 10 text-only probes.

For each C00..C09:

1. encode the one-word text;
2. enter read-only retrieval;
3. retrieve/reinstate associated audio memory structures;
4. do not generate waveform.

---

# 55. Reverse Outcome Classes

```text
OWN_AUDIO_STRUCTURE_RETRIEVED
WRONG_AUDIO_STRUCTURE_DOMINANT
NO_AUDIO_STRUCTURE_RETRIEVED
AMBIGUOUS
```

---

# 56. Reverse Success Gate

For candidate full demonstration:

\[
\boxed{
OWN\_AUDIO\_STRUCTURE\_RETRIEVED\ge8/10
}
\]

and:

\[
WRONG\_AUDIO\_STRUCTURE\_DOMINANT\le1/10
\]

---

# 57. Reverse Retrieval Evidence

Record:

- grounded audio evidence reachable;
- source grounding context IDs;
- event/descriptor identities;
- competitor audio memories;
- ranking/evidence if applicable.

No waveform synthesis metric.

---

# 58. OOD Probe Execution

Exactly 10 OOD recordings.

Each runs from fresh transient state against read-only G40 graph.

No OOD learning.

---

# 59. OOD Outcome Classes

```text
FORCED_GROUNDED_CONCEPT
AMBIGUOUS
NO_TEXT_CONCEPT_RETRIEVED
```

---

# 60. OOD False-Association Gate

For candidate full demonstration:

\[
\boxed{
FORCED\_GROUNDED\_CONCEPT\le2/10
}
\]

Therefore at least:

\[
8/10
\]

must abstain or remain ambiguous.

No post-hoc confidence threshold is added.

---

# 61. OOD Forensics

For every forced OOD mapping record:

- returned concept;
- candidate set;
- generic acoustic evidence;
- sequence overlap;
- specificity evidence;
- whether the same error appears in held-out probes.

---

# 62. Passive Retention Check

After G40 create a canonical cross-modal memory snapshot.

Advance exactly:

\[
128
\]

no-evidence/passive runtime steps using existing lawful runtime semantics.

No new sensory episode.

---

# 63. Passive Retention Requirement

For all ATG01 cross-modal edges/contexts under observation:

\[
Weight_{after}=Weight_{before}
\]

\[
Contexts_{after}=Contexts_{before}
\]

unless an already-existing non-passive lawful mechanism explicitly fires and is documented.

Expected:

\[
\boxed{PassiveDrift=0}
\]

---

# 64. Grounding Replay Determinism

Execute the exact 40 grounding curriculum on a second fresh isolated graph with identical manifest and schedule.

Required:

\[
Digest_{G10}^{(1)}=Digest_{G10}^{(2)}
\]

\[
Digest_{G20}^{(1)}=Digest_{G20}^{(2)}
\]

\[
Digest_{G30}^{(1)}=Digest_{G30}^{(2)}
\]

\[
Digest_{G40}^{(1)}=Digest_{G40}^{(2)}
\]

---

# 65. Replay Retrieval Determinism

Run the 20 held-out probes on both replay graphs.

Required canonical outcome equality:

\[
20/20
\]

---

# 66. Acoustic Preflight

Before any learning, generate read-only AudioTemporalIR digests for all 70 source items.

Record:

```text
status
events
descriptors
periodicity
ordered IR digest
```

No graph learning.

---

# 67. Preflight Validity Gate

Required:

```text
70/70 valid
UNSUPPORTED = 0
crashes = 0
NaN/Inf = 0
```

No source item may be replaced after manifest freeze.

---

# 68. Sensory Collision Analysis

Across 60 grounded/held-out words report:

- exact canonical AudioTemporalIR collisions;
- cross-concept exact collisions;
- same-concept exact collisions;
- unordered descriptor-set collisions;
- ordered-sequence distinctions.

No classifier is trained.

---

# 69. Cross-Speaker Acoustic Consistency

For each concept compare its 6 source recordings.

Report:

```text
event-count distribution
spectral-band recurrence
periodicity recurrence
energy-dynamic recurrence
ordered event motifs
descriptor overlap
```

This is diagnostic only.

---

# 70. Permutation Causal Control

ATG01 includes one required secondary causal control using a fresh isolated graph.

Concepts:

```text
P0 bird
P1 cat
P2 dog
P3 tree
```

Fixed cyclic mapping:

```text
audio(bird) -> text(cat)
audio(cat)  -> text(dog)
audio(dog)  -> text(tree)
audio(tree) -> text(bird)
```

---

# 71. Permutation Data

Reuse only the already frozen source recordings for these four audio-word categories.

Use:

```text
4 grounding recordings per acoustic word
2 held-out recordings per acoustic word
```

No new data is selected.

The graph is fresh and contains no primary ATG01 learned state.

---

# 72. Permutation Grounding

Exactly:

\[
4\times4=16
\]

grounding episodes.

Use the same cross-modal grounding authority.

Text labels follow the frozen cyclic permutation.

---

# 73. Permutation Held-Out Probes

Exactly:

\[
4\times2=8
\]

read-only held-out audio probes.

Correct answer is the deliberately paired text concept, not the natural word identity.

---

# 74. Permutation Success Gate

For causal-support PASS:

\[
\boxed{
PermutedTargetCorrect\ge6/8
}
\]

and all four acoustic categories must achieve at least:

\[
1/2
\]

correct permuted-target retrieval.

Additionally:

\[
NaturalSemanticTargetDominant\le1/8
\]

unless natural and permuted target are identical, which does not occur in this mapping.

---

# 75. Permutation Interpretation

If permutation control passes, it supports:

\[
\boxed{
CrossModalPairingWasLearnedFromGrounding
}
\]

rather than an explanation based on hidden natural-word semantics in Audio Encoder v2.

It does not independently prove all primary generalization properties.

---

# 76. No Permutation Contamination

Primary and permutation graphs are physically/logically isolated.

Required:

\[
\Delta PrimaryGraphFromPermutation=0
\]

---

# 77. Candidate-Discovery Audit for Wrong Probes

For every wrong/no/ambiguous probe, output:

```text
acoustic evidence reached
text candidates discovered
correct concept presence
candidate scores
supporting edges
grounding context counts
sequence contributions
generic evidence contributions
tie details
```

This is mandatory for future causal repair.

---

# 78. No Repair During Trial

ATG01 is frozen evaluation.

Forbidden after seeing results:

- add exposure;
- remove exposure;
- change speaker;
- change word set;
- change ranking;
- change specificity;
- add threshold;
- change Audio v2;
- change Text Encoder;
- add sequence matcher;
- add phoneme layer.

A later forensic RFC/spec handles repairs.

---

# 79. No Vision Grounding During ATG01

Even though `bird`, `cat`, `dog`, and `tree` align with prior vision concepts, no image input is permitted in ATG01.

The tri-modal test occurs later on a fresh protocol.

---

# 80. Persistent-State Boundaries

ATG01 may lawfully create persistent graph state only during:

```text
40 primary grounding episodes
16 permutation-control grounding episodes on separate graph
```

All other phases are read-only.

---

# 81. Historical Cognitive Signature

The architectural signature:

```text
915119d40643cb97
```

must remain unchanged.

Experimental graph content may have separate digests.

---

# 82. Primary Behavioral Digest

Create:

```text
ATG01BehavioralDigest
```

over canonical:

- manifest digest;
- grounding schedule;
- G10/G20/G30/G40 graph digests;
- 20 held-out outcomes;
- 10 reverse outcomes;
- 10 OOD outcomes;
- passive retention result;
- replay digests;
- permutation-control outcomes;
- invariant/gate summaries.

This does not replace cognitive lineage.

---

# 83. Grounding Evidence Provenance

Independent grounding episode identity must remain auditable.

If `edge.contexts` is the current lawful carrier, use only existing semantics.

Do NOT add:

```text
audio_grounding_count
speaker_count
word_count
```

as new persistent fields.

---

# 84. Speaker-Specific Evidence

One-off speaker-specific evidence is allowed to exist.

ATG01 does not manually prune it.

The scientific question is whether repeated cross-speaker grounding allows concept-relevant evidence to become sufficiently useful for held-out transfer.

---

# 85. Periodicity Is Not Lexical Meaning

A periodicity band shared by many words/speakers is generic acoustic evidence.

ATG01 must inspect whether generic periodicity dominates lexical retrieval.

Do not manually downweight it.

---

# 86. Sequence Evidence

Audio word representation is temporal.

Diagnostics MUST retain:

\[
E_1\rightarrow E_2\rightarrow \ldots
\]

No trial report may evaluate only an unordered descriptor bag.

---

# 87. No External Sequence Matcher

Forbidden:

- DTW keyword classifier;
- edit distance on event sequences used as a classifier;
- handcrafted template matching;
- nearest stored waveform;
- cosine classifier external to DGCA.

Sequence support must arise through existing DGCA machinery.

---

# 88. No External Speech Knowledge

Forbidden:

- pronunciation dictionary;
- phoneme lexicon;
- IPA labels;
- ASR model;
- acoustic model;
- language model;
- speaker embedding;
- pretrained speech representation.

---

# 89. Primary Trial Invariants

### ATG01-INV-01
Audio Encoder v2 unchanged.

### ATG01-INV-02
English Encoder v2 unchanged.

### ATG01-INV-03
Speech Commands v0.02 source fixed.

### ATG01-INV-04
Exactly 10 grounded concepts.

### ATG01-INV-05
Exactly 10 ungrounded OOD words.

### ATG01-INV-06
Exactly 70 primary source recordings.

### ATG01-INV-07
70 globally unique speakers.

### ATG01-INV-08
40 grounding /20 held-out /10 OOD.

### ATG01-INV-09
No audio label leakage.

### ATG01-INV-10
Minimal one-word text input only.

### ATG01-INV-11
Clean isolated B0 graph.

### ATG01-INV-12
Production graph unchanged.

### ATG01-INV-13
Existing lawful cross-modal grounding only.

### ATG01-INV-14
No manual cross-modal edges.

### ATG01-INV-15
Unique grounding context per exposure.

### ATG01-INV-16
Four independent exposures per concept.

### ATG01-INV-17
Held-out speakers unseen globally.

### ATG01-INV-18
Held-out evaluation read-only.

### ATG01-INV-19
OOD evaluation read-only.

### ATG01-INV-20
Reverse retrieval read-only.

### ATG01-INV-21
No conventional training/backprop.

### ATG01-INV-22
No pretrained speech model.

### ATG01-INV-23
No phoneme/forced alignment supervision.

### ATG01-INV-24
No new persistent primitive.

### ATG01-INV-25
No new persistent field.

### ATG01-INV-26
No new Law.

### ATG01-INV-27
No retrieval repair during trial.

### ATG01-INV-28
Ambiguity may abstain.

### ATG01-INV-29
Sequence order preserved in diagnostics.

### ATG01-INV-30
Independent recurrence auditable.

### ATG01-INV-31
Passive drift zero.

### ATG01-INV-32
Grounding replay deterministic.

### ATG01-INV-33
Permutation graph isolated.

### ATG01-INV-34
Permutation control uses learned pairing.

### ATG01-INV-35
Failures retained and localized.

### ATG01-INV-36
Scientific claim bounded.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 90. Forbidden Mechanisms

Verify absence of:

1. paired_text inside Audio Encoder;
2. word label passed to audio path;
3. folder label passed to audio path;
4. speaker ID passed to audio path;
5. semantic filename scope;
6. manual graph.link cross-modal injection;
7. direct audio-to-label node construction;
8. pretrained ASR;
9. forced aligner;
10. phoneme labels;
11. pronunciation dictionary;
12. pretrained speech embeddings;
13. speaker embeddings;
14. speaker classifier;
15. keyword classifier;
16. DTW external classifier;
17. waveform nearest-neighbor classifier;
18. new learned ranking model;
19. post-hoc confidence threshold;
20. post-hoc label threshold;
21. Audio v2 modification;
22. Text Encoder modification;
23. LESR modification;
24. IGSV modification;
25. blind reuse of visual provenance grouping;
26. new persistent SpokenWord primitive;
27. new persistent Speaker primitive;
28. new persistent grounding counter;
29. new normative Law;
30. held-out learning;
31. OOD learning;
32. reverse-probe learning;
33. failure-based recording replacement;
34. failure deletion;
35. forced winner on exact tie;
36. production graph contamination.

Required:

\[
\boxed{36/36\ PASS}
\]

---

# 91. Release Gates

### ATG01-G01 — Repository Baseline
pytest/Ruff/type/signature green before trial.

### ATG01-G02 — Dataset Provenance
Official Speech Commands v0.02 provenance/hash recorded.

### ATG01-G03 — Concept Sets
10 grounded +10 OOD exact word sets frozen.

### ATG01-G04 — Global Speaker Split
70 unique speakers proven.

### ATG01-G05 — Manifest Freeze
70 source items frozen before graph learning.

### ATG01-G06 — Acoustic Preflight
70/70 valid Audio v2 representations.

### ATG01-G07 — Label Firewall
Zero lexical/speaker semantic input to audio path.

### ATG01-G08 — B0 Isolation
Clean experimental graph and production isolation proven.

### ATG01-G09 — Grounding Authority
Existing lawful cross-modal mechanism reused.

### ATG01-G10 — Grounding Curriculum
Exactly 40 scheduled primary episodes.

### ATG01-G11 — Cross-Modal Formation
10/10 concepts form persistent cross-modal association.

### ATG01-G12 — Independent Reinforcement
10/10 concepts show >=2-context persistent support.

### ATG01-G13 — Transient Retirement
Zero transient leakage.

### ATG01-G14 — Retrieval Authority Audit
Audio retrieval stack explicitly classified/authorized.

### ATG01-G15 — Held-Out Completeness
20/20 unseen-speaker probes executed read-only.

### ATG01-G16 — Primary Held-Out Gate
Correct >=12/20; Wrong <=4/20; correct reachable >=16/20; >=8/10 concepts at least one correct.

### ATG01-G17 — Reverse Retrieval
Own audio structure >=8/10; wrong dominant <=1/10.

### ATG01-G18 — OOD Abstention
Forced grounded concept <=2/10.

### ATG01-G19 — Failure Localization
Every non-correct held-out/OOD/reverse result forensically classified.

### ATG01-G20 — Passive Retention
128-step passive drift = 0.

### ATG01-G21 — Replay Determinism
G10/G20/G30/G40 digests and held-out outcomes reproduce exactly.

### ATG01-G22 — Permutation Control
>=6/8 permuted-target correct; every category >=1/2; natural-target dominance <=1/8.

### ATG01-G23 — No Trial Repair
Architecture/retrieval/data unchanged after freeze.

### ATG01-G24 — Production Isolation
Production graph delta = 0.

### ATG01-G25 — Persistent Schema
New persistent primitives/fields = 0.

### ATG01-G26 — Law/Learning Governance
New laws/learned scalars/backprop = 0.

### ATG01-G27 — Full Regression
Full pytest/Ruff/type checks pass.

### ATG01-G28 — Historical Signature
915119d40643cb97 MATCH.

Required for full candidate closure:

\[
\boxed{28/28\ PASS}
\]

---

# 92. Final Verdict Vocabulary

Allowed primary verdicts:

```text
AUDIO_TEXT_GROUNDING_DEMONSTRATED
AUDIO_TEXT_GROUNDING_PARTIAL
AUDIO_TEXT_RETRIEVAL_BOTTLENECK
AUDIO_GROUNDING_REPRESENTATION_BOTTLENECK
AUDIO_TEXT_GROUNDING_FAILED
ATG01_BLOCKED
```

---

# 93. AUDIO_TEXT_GROUNDING_DEMONSTRATED

May be used only if:

- 36/36 invariants PASS;
- 36/36 forbidden audit PASS;
- 28/28 gates PASS;
- cross-modal association formation is demonstrated;
- unseen-speaker held-out gate passes;
- OOD false-association gate passes;
- reverse retrieval gate passes;
- permutation causal control passes;
- no leakage/repair occurs;
- regression/signature remain green.

---

# 94. AUDIO_TEXT_GROUNDING_PARTIAL

Use if:

- cross-modal associations form and persist;
- some held-out unseen-speaker transfer is real;
- safety/isolation/leakage invariants pass;
- but one or more empirical retrieval/reverse/OOD/permutation gates miss full threshold.

This should normally trigger forensic analysis rather than immediate architectural redesign.

---

# 95. AUDIO_TEXT_RETRIEVAL_BOTTLENECK

Use if a substantial majority of wrong probes satisfy:

\[
CorrectConceptStored
\land
Reachable
\land
Candidate
\]

but lose ranking/specificity.

---

# 96. AUDIO_GROUNDING_REPRESENTATION_BOTTLENECK

Use if held-out recordings frequently fail before correct cross-modal candidate formation because acoustic memory reinstatement/generalization is insufficient.

---

# 97. AUDIO_TEXT_GROUNDING_FAILED

Use if:

- lawful cross-modal associations fail to form for many concepts;
- associations do not persist;
- held-out transfer remains near-null despite valid candidates/authority;
- or causal permutation does not follow learned pairings while natural mapping appears suspiciously successful.

---

# 98. ATG01_BLOCKED

Use if:

- 70 unique-speaker split cannot be constructed;
- dataset/provenance unavailable;
- B0 isolation unavailable;
- grounding authority unavailable;
- retrieval stack is completely blocked;
- baseline is red;
- label firewall cannot be proven.

---

# 99. Required Machine-Readable Artifacts

Produce:

```text
ATG01-AUDIO-TEXT-GROUNDING-TRIAL-REPORT.md

atg01_baseline.json
atg01_data_source.json
atg01_manifest.json
atg01_manifest_digest.json
atg01_selection_rejections.jsonl
atg01_speaker_split.json
atg01_grounding_schedule.json
atg01_label_firewall.json

atg01_audio_preflight.jsonl
atg01_acoustic_collision_analysis.json
atg01_cross_speaker_analysis.json

atg01_b0.json
atg01_grounding_episodes.jsonl
atg01_grounding_checkpoints.json
atg01_crossmodal_formation.json
atg01_independent_reinforcement.json
atg01_transient_retirement.json

atg01_retrieval_authority_audit.json
atg01_heldout_results.jsonl
atg01_heldout_summary.json
atg01_candidate_reachability.jsonl
atg01_failure_forensics.jsonl

atg01_reverse_results.jsonl
atg01_reverse_summary.json

atg01_ood_results.jsonl
atg01_ood_summary.json

atg01_retention.json
atg01_replay_determinism.json

atg01_permutation_manifest.json
atg01_permutation_grounding.jsonl
atg01_permutation_results.jsonl
atg01_permutation_summary.json

atg01_graph_isolation.json
atg01_invariants.json
atg01_forbidden_mechanisms.json
atg01_release_gates.json
atg01_signature_verification.json
atg01_behavioral_digest.json
atg01_failures.jsonl
```

---

# 100. Required Human-Readable Report

`ATG01-AUDIO-TEXT-GROUNDING-TRIAL-REPORT.md` MUST include:

1. Executive verdict;
2. repository baseline;
3. Speech Commands v0.02 provenance;
4. concept/OOD sets;
5. deterministic source selection;
6. 70-speaker split;
7. frozen manifest digest;
8. audio-label firewall;
9. acoustic preflight;
10. sensory collision analysis;
11. B0 clean graph;
12. grounding schedule;
13. G10/G20/G30/G40 checkpoints;
14. cross-modal formation;
15. independent recurrence/reinforcement;
16. transient retirement;
17. retrieval authority audit;
18. 20 held-out unseen-speaker results;
19. candidate reachability;
20. failure taxonomy;
21. reverse Text→Audio retrieval;
22. OOD abstention;
23. passive retention;
24. replay determinism;
25. 4-concept permutation causal control;
26. graph isolation;
27. invariants;
28. forbidden mechanisms;
29. gates;
30. full regression;
31. signature;
32. behavioral digest;
33. bounded scientific claims;
34. readiness for tri-modal Audio+Vision+Text trial.

---

# 101. Required Final Metrics Block

End the report with:

```text
============================================================
DGCA PHASE 2.6 — AUDIO↔TEXT GROUNDING TRIAL 01

TRIAL:
ATG01

DATASET:
GOOGLE SPEECH COMMANDS v0.02

AUDIO ENCODER:
DGCA AUDIO ENCODER v2

TEXT ENCODER:
DGCA ENGLISH ENCODER v2

HISTORICAL COGNITIVE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / MISMATCH

TRAINING / BACKPROP:
0

NEW PERSISTENT PRIMITIVES:
0 / NONZERO

NEW PERSISTENT FIELDS:
0 / NONZERO

NEW NORMATIVE LAWS:
0 / NONZERO

PRIMARY SOURCE RECORDINGS:
70

UNIQUE SPEAKERS:
...

GROUNDED CONCEPTS:
10

GROUNDING RECORDINGS:
40

HELD-OUT RECORDINGS:
20

OOD RECORDINGS:
10

GROUNDING SPEAKERS:
40

HELD-OUT SPEAKERS:
20

OOD SPEAKERS:
10

GLOBAL SPEAKER OVERLAP:
0 / NONZERO

MANIFEST:
FROZEN / NOT_FROZEN

MANIFEST SHA256:
...

AUDIO LABEL LEAKAGE:
0 / NONZERO

PRETRAINED ASR / ALIGNER:
0 / NONZERO

MANUAL CROSS-MODAL EDGES:
0 / NONZERO

B0 PRIOR TRIAL MEMORY:
0 / NONZERO

GROUNDING EPISODES:
40 / 40

CONCEPTS WITH PERSISTENT CROSSMODAL ASSOCIATION:
... / 10

CONCEPTS WITH >=2 INDEPENDENT CONTEXT SUPPORT:
... / 10

TRANSIENT LEAKAGE:
0 / NONZERO

RETRIEVAL STACK:
AUTHORIZED / PARTIAL / BLOCKED

HELD-OUT AUDIO→TEXT:
CORRECT: ... / 20
WRONG: ... / 20
NO RETRIEVAL: ... / 20
AMBIGUOUS: ... / 20

CORRECT CONCEPT REACHABLE:
... / 20

CONCEPTS WITH >=1 CORRECT HELD-OUT:
... / 10

REVERSE TEXT→AUDIO:
OWN STRUCTURE: ... / 10
WRONG DOMINANT: ... / 10
NO RETRIEVAL: ... / 10
AMBIGUOUS: ... / 10

OOD:
FORCED GROUNDED CONCEPT: ... / 10
AMBIGUOUS: ... / 10
NO RETRIEVAL: ... / 10

PASSIVE RETENTION DRIFT:
0 / NONZERO

GROUNDING REPLAY:
DETERMINISTIC / NONDETERMINISTIC

PERMUTATION CONTROL:
PERMUTED TARGET CORRECT: ... / 8
NATURAL TARGET DOMINANT: ... / 8
CATEGORY COVERAGE: ... / 4

PRODUCTION GRAPH MUTATION:
0 / NONZERO

ATG01 INVARIANTS:
x / 36

FORBIDDEN MECHANISMS:
x / 36

RELEASE GATES:
x / 28

FULL PYTEST:
...

RUFF:
PASS / FAIL

TYPE CHECK:
PASS / FAIL

ATG01 BEHAVIORAL DIGEST:
...

FINAL VERDICT:
...

READY FOR SMALL AUDIO+VISION+TEXT TRIAL:
YES / NO
============================================================
```

---

# 102. Readiness for Tri-Modal Trial

Set:

```text
READY_FOR_SMALL_AUDIO_VISION_TEXT_TRIAL = YES
```

only if:

```text
AUDIO_TEXT_GROUNDING_DEMONSTRATED
```

or a narrowly justified `PARTIAL` where the remaining failure is downstream and does not undermine lawful cross-modal formation.

The tri-modal trial MUST be separately designed and authorized.

---

# 103. Data Repository Policy

Do not commit the full Speech Commands archive.

Preferred repository content:

- acquisition script;
- manifest;
- hashes;
- speaker split;
- grounding schedule;
- telemetry;
- reports.

Raw WAV files remain in ignored local trial storage unless repository policy explicitly allows otherwise.

---

# 104. Pre-Execution Freeze Checklist

Before starting any grounding:

```text
[ ] baseline green
[ ] Speech Commands v0.02 provenance verified
[ ] 70 unique speakers selected
[ ] 40/20/10 role counts exact
[ ] manifest frozen
[ ] manifest SHA256 recorded
[ ] grounding schedule frozen
[ ] audio firewall verified
[ ] B0 graph digest recorded
[ ] grounding authority audited
[ ] no production graph mutation path
```

If any item is false:

```text
DO NOT START GROUNDING
```

---

# 105. Final Formal Decision

The formal ATG01 experiment is:

\[
\boxed{
10\ concepts
\times
4\ independent\ cross-speaker\ grounding\ episodes
}
\]

followed by:

\[
\boxed{
20\ heldout\ unseen-speaker\ Audio\rightarrow Text\ probes
}
\]

plus:

\[
\boxed{
10\ Text\rightarrow AudioMemory\ probes
}
\]

plus:

\[
\boxed{
10\ ungrounded\ OOD\ audio\ probes
}
\]

plus:

\[
\boxed{
128\ passive\ retention\ steps
}
\]

plus:

\[
\boxed{
FullGroundingReplay
}
\]

plus a fresh-graph:

\[
\boxed{
4\text{-concept}\ PermutationCausalControl
}
\]

---

# 106. Pre-Freeze Status

\[
\boxed{
\textbf{DGCA Phase 2.6 — Audio↔Text Grounding Trial 01 — Formal Empirical Specification v1.0}
}
\]

Status:

```text
CANDIDATE FOR FREEZE REVIEW
```

No grounding execution is authorized until freeze review is complete.


---

# 107. Normative Freeze Clarifications — Binding v1.0

The following clarifications were adopted during adversarial freeze review.
They are normative and override any earlier ambiguous wording.

## ATG01-FC-01 — Exact Dataset Archive Identity

ATG01 v1.0 uses the main Google Speech Commands v0.02 archive:

```text
https://storage.googleapis.com/download.tensorflow.org/data/speech_commands_v0.02.tar.gz
```

Expected archive SHA256:

```text
af14739ee7dc311471de98f5f9d2c9191b18aedfe957f4a6ff791c709868ff58
```

The acquisition runner MUST verify this digest before extraction.

The separate `speech_commands_test_set_v0.02.tar.gz` archive is NOT used by ATG01 v1.0.

The archive's `validation_list.txt` and `testing_list.txt` may be retained as provenance metadata, but ATG01 role assignment is governed exclusively by the frozen 70-unique-speaker selection algorithm in this specification.

---

## ATG01-FC-02 — Dataset Labels Are Experimental Metadata Only

Directory word labels and filename speaker IDs may be read only by:

- deterministic dataset selection;
- split-integrity verification;
- grounding-orchestrator text pairing;
- offline correctness/forensic reporting.

They MUST NOT enter:

- AudioEncoderV2;
- AudioTemporalIR;
- audio stream scope identity;
- candidate scoring;
- acoustic memory;
- retrieval ranking.

Thus:

\[
DatasetMetadataAuthority
\neq
AudioCognitiveAuthority
\]

---

## ATG01-FC-03 — Encoder Code Identity Freeze

The trial MUST record SHA256 digests for the exact source files implementing:

```text
AudioEncoderV2
EnglishEncoderV2
grounding authority
LESR
IGSV
retrieval / completion path
```

The Audio v2 implementation must be behaviorally/source-identical to the authorized implementation from commit `8c2c48f`, unless a later commit changed only trial/report artifacts and the relevant source digest still matches.

The English Encoder v2 and retrieval stack must likewise be unchanged during the trial.

Any cognitive/retrieval source change after manifest/spec freeze:

```text
ATG01_PROTOCOL_VIOLATION
```

---

## ATG01-FC-04 — Text-Concept Preflight

Before B0 grounding, encode each exact grounded lexical item once on an isolated non-learning preflight path.

Required:

```text
10/10 text inputs accepted lawfully
10/10 canonical lexical identities stable
0 duplicate persistent concept identities for the same lexical item
0 cross-label identity collisions
```

The preflight MUST NOT create persistent trial memory.

If the existing English Encoder cannot lawfully represent an isolated one-word input:

```text
ATG01_BLOCKED
```

No sentence wrapper may be invented.

---

## ATG01-FC-05 — Manifest Selection Must Not Depend on Audio v2 Output

The 70-item manifest is frozen using only:

- source provenance;
- exact label folder;
- speaker identity;
- waveform technical validity;
- duration;
- deterministic hashes.

Audio v2 representation quality MUST NOT be used to accept/reject candidate files.

Therefore an item that later produces weak/no acoustic evidence remains in the frozen trial.

This prevents model-conditioned cherry-picking.

---

## ATG01-FC-06 — Whole Audio Experience Grounding Boundary

The cross-modal grounding unit is the complete lawful persistent audio experience compiled from one selected WAV.

All lawful audio events from the stream retain their existing temporal order and common grounding-context provenance.

The grounding mechanism MAY associate persistent audio evidence reachable from that experience with the text experience under existing lawful authority.

It MUST NOT:

- create a persistent edge to transient `AudioTemporalIR`;
- flatten away existing temporal relations as a replacement ontology;
- choose a human-designated "important" frame/event;
- manually select phonetic segments.

Thus:

\[
WholeAudioExperience
\rightarrow
ExistingPersistentAudioEvidence
\]

before cross-modal association.

---

## ATG01-FC-07 — Exact Retrieval Path Freeze

Before the first held-out probe, the authority audit MUST serialize the exact retrieval path used by:

- primary held-out Audio→Text;
- OOD Audio→Text;
- permutation Audio→Text;
- reverse Text→Audio where applicable.

The path includes:

```text
candidate discovery
completion/reinstatement stage
LESR enabled/disabled
IGSV enabled/disabled
sequence evidence handling
tie rule
abstention rule
```

Once frozen, the path is identical for every probe of that direction.

No per-probe fallback or alternate scorer is allowed.

---

## ATG01-FC-08 — Full Demonstration Requires AUTHORIZED Retrieval

For:

```text
AUDIO_TEXT_GROUNDING_DEMONSTRATED
```

the pre-held-out authority verdict MUST be:

```text
AUDIO_RETRIEVAL_STACK_AUTHORIZED
```

If:

```text
AUDIO_RETRIEVAL_STACK_PARTIAL
```

the maximum allowed primary verdict is:

```text
AUDIO_TEXT_GROUNDING_PARTIAL
```

or an evidence-specific bottleneck verdict.

If:

```text
AUDIO_RETRIEVAL_STACK_BLOCKED
```

no held-out grounding-demonstration verdict is allowed.

Grounding-formation evidence may still be reported.

---

## ATG01-FC-09 — IGSV / LESR Non-Requirement Rule

ATG01 does NOT require both LESR and IGSV to be enabled.

It requires only that the exact selected retrieval path be lawful and frozen.

If IGSV contains vision-specific provenance assumptions, it must be disabled for audio rather than altered during ATG01.

Disabling an unauthorized component is not a repair if decided and recorded BEFORE the first held-out probe.

No component state may change after held-out evaluation begins.

---

## ATG01-FC-10 — OOD Forced-Mapping Definition

For an OOD probe:

```text
FORCED_GROUNDED_CONCEPT
```

means the frozen retrieval path returns one unique learned lexical concept as top result.

No confidence threshold is applied.

If there is an exact top tie:

```text
AMBIGUOUS
```

If no learned text concept is returned:

```text
NO_TEXT_CONCEPT_RETRIEVED
```

This definition prevents post-hoc calibration.

---

## ATG01-FC-11 — Reverse “Own Audio Structure” Definition

For text concept \(c\):

```text
OWN_AUDIO_STRUCTURE_RETRIEVED
```

requires that the frozen reverse retrieval path reaches a unique dominant persistent audio-associated structure whose ATG01 grounding provenance includes one or more grounding contexts paired with \(c\).

If the dominant structure is grounded only to another lexical concept:

```text
WRONG_AUDIO_STRUCTURE_DOMINANT
```

If multiple concept-grounded audio structures tie at top:

```text
AMBIGUOUS
```

If no persistent audio-associated structure is retrieved:

```text
NO_AUDIO_STRUCTURE_RETRIEVED
```

No waveform generation is involved.

---

## ATG01-FC-12 — Canonical Experimental Graph Digest

Checkpoint/replay digests MUST be computed from canonical persistent learned state only.

Include, as applicable:

- persistent node structural identity;
- persistent edge structural identity;
- edge cognitive state;
- canonical context membership;
- assembly membership;
- lawful persistent sequence/temporal relations.

Exclude:

- wall-clock timestamps;
- Python object addresses;
- filesystem paths;
- transient IR;
- runtime counters without cognitive meaning;
- benchmark telemetry.

Stable canonical ordering MUST be defined before G1.

---

## ATG01-FC-13 — B0 Equality Across Replays

Primary grounding replay requires the second isolated graph to begin from a B0 canonical digest identical to the first primary B0.

If B0 digests differ:

```text
REPLAY_DETERMINISM = INVALID
```

Do not compare G10/G20/G30/G40 across unequal initial states.

---

## ATG01-FC-14 — Permutation Control Schedule

The permutation-control graph uses exactly the primary selected recordings for:

```text
bird
cat
dog
tree
```

and the same projected four-round order as the primary curriculum restricted to C00..C03.

Permutation grounding contexts are fresh:

```text
ATG01-PCTX-001 .. ATG01-PCTX-016
```

They are not shared with primary contexts.

Held-out permutation probes use the same 8 held-out recordings for those four acoustic categories and remain read-only.

No new recording selection occurs.

---

## ATG01-FC-15 — Permutation Control Semantic Firewall

The cyclic text mapping is external experimental pairing only:

```text
bird audio -> cat text
cat audio -> dog text
dog audio -> tree text
tree audio -> bird text
```

Audio Encoder v2 still receives no lexical label.

The permutation graph begins from clean B0 and contains no primary ATG01 learned state.

The natural word identity is used only for offline causal comparison.

---

## ATG01-FC-16 — Passive Retention Execution Authority

The required 128 passive steps MUST use the already-existing lawful DGCA no-evidence/passive runtime step semantics.

ATG01 MUST NOT invent a new tick primitive or retention mechanism.

If no existing deterministic passive-step API/semantics can be invoked without adding architecture:

```text
ATG01-G20 = BLOCKED
```

and full demonstration is blocked.

---

## ATG01-FC-17 — Statistical Reference Is Descriptive Only

The frozen primary gate remains:

\[
Correct\ge12/20
\]

with the additional reachability/error/concept-coverage constraints already specified.

For a simple 10-way independent uniform forced-choice null:

\[
P(X\ge12),\ X\sim Binomial(20,0.1)
\approx
5.814917984782005\times10^{-8}
\]

This number is reported only as a descriptive reference.

It MUST NOT be used as the sole scientific proof because:

- probes share one learned graph;
- outcomes may not be independent;
- the system may abstain;
- candidate availability is structured.

The permutation causal control and OOD behavior remain mandatory.

---

## ATG01-FC-18 — Held-Out Gate Is a Conjunction

ATG01-G16 passes only if ALL are true:

\[
Correct\ge12/20
\]

\[
Wrong\le4/20
\]

\[
CorrectConceptReachable\ge16/20
\]

\[
ConceptsWithAtLeastOneCorrect\ge8/10
\]

No weighted averaging across these conditions.

---

## ATG01-FC-19 — Permutation Gate Is a Conjunction

ATG01-G22 passes only if ALL are true:

\[
PermutedTargetCorrect\ge6/8
\]

\[
All4AcousticCategories\ge1/2
\]

\[
NaturalSemanticTargetDominant\le1/8
\]

No partial credit can make G22 PASS.

---

## ATG01-FC-20 — Trial Mutation Boundary

After the ATG01 manifest, schedule, retrieval path, and B0 are frozen, only experimental graph state produced by the predeclared grounding episodes may change.

The following must remain unchanged until final report:

- Audio Encoder v2 code/constants;
- English Encoder v2 code;
- grounding mechanism;
- retrieval path;
- LESR/IGSV code/configuration;
- concept/OOD sets;
- source recordings;
- speaker split;
- grounding schedule;
- success thresholds.

Any change requires a new trial version.

---

## ATG01-FC-21 — Full Closure Requirements

Full ATG01 closure requires simultaneously:

```text
36/36 invariants PASS
36/36 forbidden mechanisms PASS
28/28 release gates PASS
AUDIO_RETRIEVAL_STACK_AUTHORIZED
full regression PASS
historical cognitive signature MATCH
production graph mutation = 0
trial mutation violations = 0
```

The primary final verdict may then be evaluated under Sections 93–98.

---

# 108. Formal Freeze Decision

The adversarial freeze review found:

```text
Fatal architectural defect = 0
Fatal empirical-design defect = 0
Unresolved implementation-authority ambiguity after clarifications = 0
New persistent primitive necessity = FALSE
New Law necessity = FALSE
```

Therefore:

\[
\boxed{
\textbf{DGCA Phase 2.6 — Audio↔Text Grounding Trial 01 — Formal Empirical Specification v1.0 — FROZEN}
}
\]

The next authorized step is to build the ATG01 Master Data Acquisition, Grounding, Retrieval & Verification Prompt.

No ATG01 data acquisition or grounding execution is authorized before that master prompt is reviewed.
