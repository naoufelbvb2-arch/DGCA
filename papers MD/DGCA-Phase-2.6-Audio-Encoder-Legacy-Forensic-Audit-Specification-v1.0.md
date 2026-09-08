# DGCA Phase 2.6 — Audio Encoder Legacy Forensic Audit Specification v1.0

## Architectural, DSP, Temporal, Safety, and Real-Audio Diagnosis Before Audio Encoder v2

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Component Under Audit:** Legacy Audio Encoder / RFC-08 Audio Sensory Pipeline  
**Document Type:** Formal Forensic Audit Specification  
**Version:** 1.0  
**Status:** **FORENSIC PROTOCOL — CANDIDATE FOR FREEZE**  
**Execution Mode:** **READ-ONLY DIAGNOSIS / NO AUDIO-V2 IMPLEMENTATION / NO LEARNING REPAIR**  
**Primary Legacy Implementation:** `dgca/audio.py`  
**Legacy Architectural Source:** `RFC-08 — Biomimetic Auditory Pipeline & Lean CAR-FAC Grounding`  
**Historical Architecture Signature:** `915119d40643cb97`  
**Vision Encoder v2:** **FROZEN / OUT OF SCOPE**  
**LESR v1.0:** **FROZEN / OUT OF SCOPE**  
**IGSV v1.0:** **FROZEN / OUT OF SCOPE**  
**New Cognitive Primitives:** `0`  
**New Persistent Fields:** `0`  
**New Normative Laws:** `0`  
**Primary Deliverable:** **Evidence-Based Audio Encoder v2 Requirements Matrix**

---

# 1. Purpose

The purpose of this forensic audit is not to improve the current Audio Encoder.

The purpose is to determine, with implementation-level and empirical evidence:

\[
\boxed{
\textbf{What must Audio Encoder v2 actually be?}
}
\]

The audit must establish:

1. what the legacy encoder truly computes;
2. which RFC-08 claims are actually implemented;
3. which implementation elements preserve useful auditory information;
4. where spectral, temporal, source, and event information is lost;
5. whether silence/low-energy inputs fail closed;
6. whether streaming continuity exists;
7. whether the current F1/F2/F0/onset labels are scientifically justified by the computation;
8. whether current source-separation claims have real evidence;
9. whether paired text leaks semantic authority into the sensory encoder;
10. which components must be kept, fixed, redesigned, replaced, or deferred in Audio Encoder v2.

---

# 2. Governing Rule

\[
\boxed{
\textbf{Diagnose Before Redesign}
}
\]

This forensic protocol does NOT authorize:

- implementation of Audio Encoder v2;
- replacement of `dgca/audio.py`;
- adoption of external CAR-FAC code;
- addition of an FFT/STFT/MFCC frontend;
- addition of a neural audio model;
- addition of source-separation models;
- graph learning changes;
- Law changes;
- new persistent state;
- new cognitive primitives;
- new learned parameters.

The final report must stop at:

\[
\boxed{
AudioEncoderV2Requirements
}
\]

---

# 3. Frozen Architectural Context

The audit occurs after:

- English Encoder v2 closure;
- Vision Encoder v2 closure;
- LESR repair;
- IGSV grounding-specificity repair.

Those systems must remain untouched.

Audio is evaluated as an independent sensory frontend first.

Cross-modal grounding may be inspected only to identify legacy coupling/leakage.

---

# 4. Legacy RFC-08 Intended Architecture

RFC-08 describes the intended auditory path as approximately:

```text
Raw Waveform
    ↓
16-Channel Greenwood Tonotopic Resonator Cascade
    ↓
IHC Half-Wave/Cubic Transduction + Smoothing
    ↓
Two-Stage Fast/Slow AGC
    ↓
F1 / F2 / F0-Voicing / Onset Discretization
    ↓
Audio Sensory Episode
    ↓
Tri-Modal Grounding
```

The forensic audit must distinguish:

\[
\boxed{
DocumentedIntent
}
\]

from:

\[
\boxed{
ImplementedBehavior
}
\]

---

# 5. Current Implementation Facts to Reproduce Before Diagnosis

The current `dgca/audio.py` implementation must be independently re-read and reproduced.

Known code-level behaviors requiring audit include:

- `LeanCARFAC(num_channels=16)`;
- Greenwood-like frequency generation;
- independent per-frequency 2-pole IIR resonator processing;
- half-wave cubic transform;
- per-channel fast/slow envelope adaptation;
- whole-segment channel-energy accumulation;
- F1 band selected from channels 8..15;
- F2 band selected from channels 2..7;
- voicing returned as Boolean;
- onset returned as Boolean;
- `AudioSensoryPipeline` emits one `simultaneous` episode;
- emitted persistent acoustic descriptors are limited to F1-band, F2-band, voiced/unvoiced;
- `paired_text` may be injected from inside audio pipeline;
- mutable `_uid_counter` generates transient audio IDs;
- empty waveform returns default F1/F2 values.

These are hypotheses to be verified from the exact current code and tests.

---

# 6. Primary Forensic Questions

## AEF-Q01 — CAR-FAC Claim

Does the implementation actually satisfy the structural properties required to call itself a cascade of asymmetric resonators with fast-acting compression?

---

## AEF-Q02 — Tonotopic Coverage

How many of the nominal 16 channels are numerically distinct and meaningfully responsive at supported sample rates?

---

## AEF-Q03 — Nyquist Safety

Are any channels at or above Nyquist, degenerate, dead, duplicated, or unstable?

---

## AEF-Q04 — Streaming State

Does segmenting one continuous waveform into multiple calls preserve the same cochlear response as processing it continuously?

---

## AEF-Q05 — Temporal Information

How much time-order information survives `extract_features()` and `process_audio()`?

---

## AEF-Q06 — Acoustic Identity

Can temporally distinct sounds with similar global energy spectra collapse to the same persistent audio feature set?

---

## AEF-Q07 — Formant Validity

Do `fmt1_band` and `fmt2_band` behave as meaningful formant-like evidence or merely global low/high dominant-band winners?

---

## AEF-Q08 — Pitch Validity

Does the encoder estimate pitch \(F_0\), or only binary periodicity/voicing?

---

## AEF-Q09 — Onset Validity

Can the encoder represent onset timing, multiple onsets, offsets, rhythm, or only one whole-segment Boolean?

---

## AEF-Q10 — Silence Safety

Does silence/empty/near-silence produce zero acoustic evidence, or fabricated categorical features?

---

## AEF-Q11 — Dynamic Range / AGC

Does adaptation improve useful signal representation across amplitudes and sustained noise, and is its state persistent across streaming segments?

---

## AEF-Q12 — Source Mixtures

What happens when two simultaneous sources are physically mixed before encoding?

---

## AEF-Q13 — Source Separation Evidence

Has any existing benchmark actually demonstrated source separation, or only discrimination of separately processed signals?

---

## AEF-Q14 — Real Recorded Audio

How does the current encoder behave on real human speech and environmental recordings rather than synthetic sinusoidal WAV files?

---

## AEF-Q15 — Semantic Leakage

Does `paired_text` allow sensory encoder code to supply semantic information that should belong to cross-modal orchestration?

---

## AEF-Q16 — Determinism

Is output semantic identity deterministic with respect to waveform content, or dependent on mutable call order via transient IDs?

---

## AEF-Q17 — Sensory Budget

Does the legacy `B_audio=3` preserve enough information for sequence learning, or cause catastrophic auditory compression?

---

## AEF-Q18 — DGCA Sequence Compatibility

Does the current output give DGCA any meaningful sequence structure on which Laws/RFCs for temporal learning can operate?

---

# 7. Forensic Failure Taxonomy

Every observed architectural defect must be classified.

### AEF-A — FRONTEND_TOPOLOGY_MISMATCH

Documented cochlear topology does not match implemented filter topology.

### AEF-B — NUMERICAL_CHANNEL_DEFECT

Dead, duplicated, unstable, Nyquist-invalid, or ineffective channels.

### AEF-C — STREAMING_STATE_LOSS

Continuous signal state is reset across calls.

### AEF-D — TEMPORAL_INFORMATION_COLLAPSE

Distinct temporal structures collapse to identical/near-identical whole-segment descriptors.

### AEF-E — FEATURE_SEMANTICS_OVERCLAIM

Feature name claims more than computation establishes, e.g. `F1`, `F2`, or `F0`.

### AEF-F — NO_EVIDENCE_FAIL_OPEN

Silence/no signal produces fabricated acoustic evidence.

### AEF-G — SOURCE_MIXTURE_FAILURE

Mixed sources are collapsed with no defensible organization/separation.

### AEF-H — BENCHMARK_CLAIM_GAP

Existing benchmark does not actually test the capability its label claims.

### AEF-I — SENSORY_SEMANTIC_LEAKAGE

Encoder accepts/injects semantic paired text.

### AEF-J — IDENTITY_NONDETERMINISM

Semantic episode identity depends on mutable call order.

### AEF-K — BUDGET_INFORMATION_BOTTLENECK

Fixed feature budget destroys necessary temporal/spectral evidence.

### AEF-L — REAL_AUDIO_GENERALIZATION_FAILURE

Synthetic controls pass but real recorded audio fails materially.

### AEF-M — OTHER_CAUSALLY_PROVEN

Only with explicit evidence.

---

# 8. Audit Source Hierarchy

Evidence authority order:

1. current executable implementation;
2. current tests;
3. current benchmark scripts;
4. current empirical outputs;
5. RFC-08 documented intent;
6. historical README/claims.

If documentation conflicts with executable behavior:

\[
\boxed{
ExecutableBehaviorWinsForForensicFact
}
\]

---

# 9. No Historical Claim Rewriting

Do not rewrite RFC-08.

Report discrepancies explicitly:

```text
RFC08_CLAIM
IMPLEMENTED_BEHAVIOR
MATCH_STATUS
FORENSIC_IMPACT
```

---

# 10. CAR-FAC Reference Boundary

The audit may use the official CAR-FAC design as an external architectural reference only to determine whether the legacy implementation should be described as:

```text
CARFAC
LEAN_CARFAC
CARFAC_INSPIRED
PARALLEL_RESONATOR_BANK
OTHER
```

The audit does NOT require Audio Encoder v2 to use full official CAR-FAC.

---

# 11. CAR-FAC Structural Claim Audit

Inspect whether current implementation contains:

- actual cascade between resonator stages;
- asymmetric resonators;
- pole-zero asymmetry or equivalent;
- CAR state;
- IHC state;
- AGC state;
- feedback/coupling from AGC into cochlear mechanics;
- cross-channel AGC coupling;
- persistent runtime state between waveform segments.

Produce:

```text
aef_carfac_claim_audit.json
```

---

# 12. Filter Topology Reconstruction

For every nominal channel record:

```text
ChannelIndex
CenterFrequency
SampleRate
Nyquist
Q
Bandwidth
b0
b1
b2
a1
a2
DistinctFromAdjacent
Finite
Stable
EffectiveGain
```

At minimum audit:

```text
fs = 8000
fs = 16000
```

---

# 13. Greenwood Mapping Audit

Compare:

- RFC-08 formula;
- implemented formula;
- actual generated center frequencies.

Report exact 16-channel lists.

Check:

- monotonicity;
- duplicates;
- clamping;
- effective low/high bounds;
- spacing.

Produce:

```text
aef_frequency_map.json
```

---

# 14. Nyquist / Dead Channel Test

For each supported sample rate:

\[
f_c < f_s/2
\]

must be audited.

If:

\[
f_c=f_s/2
\]

or filter input gain collapses numerically, record dead/degenerate behavior.

No code fix in this trial.

---

# 15. Pure-Tone Response Sweep

Generate deterministic low-level diagnostic sine tones across the supported frequency range.

Recommended frequencies:

```text
80
100
125
160
200
250
315
400
500
630
800
1000
1250
1600
2000
2500
3150
3800 Hz
```

At each valid sample rate:

- encode equal-duration/equal-RMS tone;
- record all channel energies;
- record winning F1/F2 bands;
- record voicing;
- record onset.

Output:

```text
aef_tone_sweep.jsonl
```

---

# 16. Channel Selectivity Metric

For each tone \(f_t\), report:

\[
PeakChannel
\]

\[
PeakCenterFrequency
\]

\[
FrequencyError
\]

\[
PeakToSecondRatio
\]

\[
ResponseSpread
\]

No pass threshold is invented before results.

---

# 17. Impulse Response Audit

Use an impulse and inspect each channel.

Measure:

- response length;
- ringing;
- peak;
- stability;
- relative delay;
- whether channels behave independently;
- whether there is any cascade propagation.

---

# 18. White / Pink / Sustained Noise Controls

Use deterministic noise seeds.

Measure:

- per-channel response distribution;
- fast envelope evolution;
- slow envelope evolution;
- initial vs sustained output;
- recovery after noise offset.

---

# 19. IHC Audit

Reconstruct exactly whether the implementation performs:

\[
HalfWave
\]

\[
CubicNonlinearity
\]

\[
ExplicitLowPassSmoothing
\]

Report each independently.

Do not infer smoothing from AGC envelopes unless code semantics justify it.

---

# 20. AGC Audit

Determine exact implemented semantics of fast and slow adaptation.

Measure:

- amplitude compression;
- sustained-level adaptation;
- attack;
- release;
- recovery;
- segment-boundary discontinuity.

Report whether AGC is:

```text
LOCAL_PER_CHANNEL
CROSS_CHANNEL_COUPLED
STATEFUL_STREAMING
CALL_LOCAL_RESETTING
FEEDBACK_TO_CAR
POST_IHC_ONLY
```

---

# 21. Streaming Equivalence Test

Create continuous waveform \(X\).

Process once:

\[
R_{full}=Encoder(X)
\]

Then split:

\[
X=X_1||X_2||X_3
\]

process sequentially through intended streaming API/state.

Compare channel-level response near boundaries.

If the implementation has no persistent state, record:

\[
\boxed{
StreamingStateAbsent
}
\]

Do not patch it.

---

# 22. Segmentation Sensitivity

For the same physical waveform:

- process whole;
- split at arbitrary point;
- split at silence;
- split at onset;
- split into small chunks.

Measure changes in extracted features.

A sensory frontend intended for streaming should not change acoustic identity merely because API chunk boundaries move, except for explicitly bounded event-window semantics.

---

# 23. Silence / No-Evidence Safety Audit

Test:

1. `[]`
2. zeros of length 10
3. zeros of length 100
4. zeros of length 8000
5. near-zero noise
6. DC offset only
7. sub-threshold signal

Record:

```text
AudioFeatures
EmittedSignals
SensoryEpisodeCount
StructuralWeight
PersistentFeatureCandidates
```

Required forensic question:

\[
\boxed{
NoSignal\rightarrow NoAcousticEvidence?
}
\]

---

# 24. Fail-Closed Standard for Audio v2 Requirements

The forensic report must decide whether Audio v2 requires:

```text
COMPLETE
SAFE_PARTIAL
UNSUPPORTED / NO_EVIDENCE
```

semantics analogous to other DGCA encoders.

Do not implement them in this audit.

---

# 25. F1/F2 Semantic Audit

The current implementation must be evaluated under the literal computation it performs.

Test whether `fmt1_band` / `fmt2_band` track:

- synthetic simple resonances;
- harmonic tones;
- two-tone combinations;
- broadband noise;
- real sustained vowels;
- real consonants;
- environmental sounds.

Determine whether the correct scientific name should be:

```text
FORMANT
DOMINANT_LOW_BAND
DOMINANT_HIGH_BAND
RESONANCE_BIN
OTHER
```

---

# 26. No Ground-Truth Formant Dependency in Runtime

External tools may be used only for forensic evaluation/ground truth if explicitly documented.

They must not be integrated into DGCA.

The audit should prefer controlled synthetic signals and known-labeled real vowel datasets where possible.

---

# 27. F0 / Voicing Audit

Determine exactly what `_detect_voicing()` outputs.

Test:

- pure periodic tones across 80–400 Hz;
- tones outside range;
- harmonically rich periodic signals;
- whispered/unvoiced speech;
- white noise;
- voiced human vowels;
- musical notes;
- amplitude-modulated noise.

Report:

```text
PitchEstimated = YES/NO
VoicingOnly = YES/NO
```

---

# 28. Pitch-Identity Requirement Question

The forensic report must explicitly decide whether Audio Encoder v2 needs to retain a bounded pitch estimate rather than only `voiced/unvoiced`.

No implementation here.

---

# 29. Onset Audit

Current onset detector must be tested on:

- onset at beginning;
- onset at 25%;
- onset at 50%;
- onset at 75%;
- multiple onsets;
- gradual attack;
- silence;
- continuous steady tone.

Report:

```text
DetectsPresence
DetectsTiming
DetectsMultipleEvents
DetectsOffsets
```

---

# 30. Temporal Information Retention Audit

This is a primary gate.

Construct waveform pairs with:

- identical component frequencies;
- identical approximate RMS;
- identical total duration;
- different temporal order.

Example:

\[
A = Tone_{300}\rightarrow Tone_{1000}
\]

\[
B = Tone_{1000}\rightarrow Tone_{300}
\]

Audit whether:

\[
LegacyFeatures(A)=LegacyFeatures(B)
\]

or nearly so.

---

# 31. Temporal Permutation Family

Test:

```text
A→B
B→A
A→silence→B
B→silence→A
A→B→A
B→A→B
```

using same component inventory.

Record feature collisions.

Produce:

```text
aef_temporal_collision.jsonl
```

---

# 32. Sequence Information Metric

For each controlled family report:

```text
WaveformPair
TemporalOrderDifferent
LegacyFeatureTupleA
LegacyFeatureTupleB
Collision
ChannelEnergyDistance
GraphSignalSetDistance
```

No learned metric.

---

# 33. Whole-Segment Compression Audit

Quantify information retained at three levels:

### Level 1
Raw waveform duration \(N\)

### Level 2
Cochlear channel-time matrix

### Level 3
`AudioFeatures`

### Level 4
Persistent graph-facing audio tokens

Report:

```text
RawSamples
ChannelTimeValues
FeatureScalars
PersistentAudioTokens
TemporalPositionsRetained
```

---

# 34. Audio Sensory Budget Audit

Legacy RFC-08 uses three persistent core descriptors:

\[
B_{audio}=3
\]

The report must determine whether this budget:

```text
SUFFICIENT
TOO_AGGRESSIVE
CONTEXT_DEPENDENT
UNJUSTIFIED
```

for:

- simple steady vowels;
- spoken syllables;
- spoken words;
- environmental events;
- multi-event clips.

---

# 35. DGCA Temporal Compatibility Audit

Inspect `SensoryEpisode(kind="simultaneous")` output.

Determine whether audio pipeline ever emits:

- multiple ordered sensory episodes;
- temporal transitions;
- frame identity;
- event boundaries;
- duration;
- onset location;
- offset location.

If not:

\[
\boxed{
GraphReceivesNoAuditorySequence
}
\]

must be explicitly evaluated.

---

# 36. Real Recorded Audio Requirement

Synthetic audio alone is insufficient for forensic closure.

The audit must include a small real-recorded set.

If no real recordings are available:

\[
\boxed{
REAL\_AUDIO\_BRANCH=BLOCKED
}
\]

Do not substitute generated sine WAV files and call them real audio.

---

# 37. Real-Audio Forensic Set — Minimum Categories

Use actual microphone/recorded audio from lawfully available sources.

Minimum categories:

### Speech
- at least 3 speakers;
- sustained vowels;
- short syllables;
- short words;
- different pitch ranges.

### Non-speech
- clap/impulse;
- door/knock-like transient;
- engine/fan-like sustained sound;
- bird-like/natural sound;
- music or tonal instrument;
- environmental noise.

### Silence / room tone
- actual room silence;
- microphone background noise.

Recommended total:

\[
\boxed{
24\text{–}40\ real\ clips
}
\]

This is a diagnostic set, not a training corpus.

---

# 38. No Semantic Recognition Requirement Yet

The real-audio audit does NOT require the legacy encoder to name words or objects.

It asks whether acoustic representations are:

- non-fabricated;
- stable;
- discriminative;
- temporally informative;
- amplitude robust;
- speaker-variable but structurally meaningful.

---

# 39. Speaker Variation Audit

Use same short utterance from multiple speakers where possible.

Compare:

- raw legacy feature tuple;
- channel energy profile;
- voicing;
- onset;
- collisions.

Question:

Does the frontend preserve shared acoustic structure without collapsing all speaker variation or overfitting pitch?

---

# 40. Same-Speaker Different-Utterance Audit

Compare multiple utterances from one speaker.

A useful encoder should not let speaker identity dominate all content variation.

No speaker classifier is required.

---

# 41. Amplitude Invariance Audit

For same recording, scale amplitude by deterministic factors:

```text
0.25
0.5
1.0
2.0 with clipping prevented
```

Measure feature stability and channel representation changes.

This tests AGC/compression behavior.

---

# 42. Additive Noise Audit

For selected clean recordings, create deterministic mixtures at multiple SNRs.

Use only evaluation transformations.

Report representation stability.

No denoiser.

---

# 43. Two-Source Mixture Audit

This is mandatory.

Create:

\[
Mix=\alpha X+(1-\alpha)Y
\]

for:

- two voices;
- voice + tone;
- voice + noise;
- two environmental sources.

Process the MIXED waveform once.

Do not process sources separately and call that source separation.

---

# 44. Source-Mixture Forensic Questions

For each mixture:

- does output preserve evidence from both sources?
- does one source suppress the other?
- does output become a third unrelated fingerprint?
- are there any separate source identities?
- does the encoder produce one collapsed global representation?

---

# 45. Cocktail-Party Claim Audit

Inspect all historical tests/benchmarks labeled:

```text
cocktail party
source grouping
speaker separation
```

For each classify:

```text
ACTUAL_MIXTURE_TEST
SEPARATE_SIGNAL_DISCRIMINATION
SYNTHETIC_ONLY
REAL_MIXTURE
SOURCE_SEPARATION_DEMONSTRATED
NOT_DEMONSTRATED
```

Produce:

```text
aef_cocktail_party_claim_audit.json
```

---

# 46. Source Separation Is Not Automatically an Encoder Requirement

The audit must distinguish:

\[
\boxed{
CochlearEncoding
}
\]

from:

\[
\boxed{
AuditorySourceOrganization
}
\]

If source organization requires a separate post-cochlear subsystem, the report should say so.

Do not force it into Audio Encoder v2 without unique necessity.

---

# 47. Paired-Text Leakage Audit

Inspect:

```text
process_audio(..., paired_text=...)
```

Determine:

- whether text is appended inside the same sensory episode;
- whether encoder itself can supply semantic text;
- whether this violates post-Vision encoder authority separation.

Classify:

```text
PURE_SENSOR
SENSOR_PLUS_GROUNDING_ORCHESTRATOR
SEMANTIC_LEAKAGE_RISK
```

---

# 48. Audio Encoder Authority Principle

The final requirements matrix must evaluate adoption of:

\[
\boxed{
AudioEncoderMayDescribeSignal
}
\]

but:

\[
\boxed{
AudioEncoderMustNotSupplyLearnedMeaning
}
\]

No implementation during audit.

---

# 49. UID Determinism Audit

Test same waveform:

- fresh pipeline;
- repeated call;
- after unrelated calls;
- different call ordering.

Record:

```text
PersistentFeatureSet
TransientUID
EpisodeSerialization
```

Determine whether semantic determinism is distinct from transient identity determinism.

---

# 50. Required Identity Decision

The report must state whether Audio Encoder v2 should:

- receive external scope ID;
- derive deterministic transient identity;
- preserve mutable counter;
- use another existing DGCA identity mechanism.

Do not implement.

---

# 51. Structural Weight Audit

Current code assigns:

\[
0.80
\]

when:

\[
Voiced \land Onset
\]

Determine:

- architectural owner of `0.80`;
- whether RFC-08 uniquely justifies it;
- whether it is a hard-coded semantic/salience policy;
- whether it changes learning outcomes;
- whether it should survive v2.

No code changes.

---

# 52. Hard-Coded Threshold Inventory

Inventory all numeric audio policy constants, including:

- 16 channels;
- 100 Hz;
- 4000 Hz;
- bandwidth/Q construction;
- 5 ms;
- 100 ms;
- 0.6;
- 2.5;
- pitch 80–400 Hz;
- voicing threshold;
- onset threshold;
- structural weight 0.80;
- budget 3.

Classify each:

```text
PHYSICAL_CONSTRAINT
DSP_DESIGN_CONSTANT
HEURISTIC
SEMANTIC_POLICY
LEGACY_UNJUSTIFIED
```

---

# 53. Sample-Rate Audit

Test at least:

```text
8000 Hz
16000 Hz
```

Where possible include:

```text
22050 or 24000 Hz
```

only as diagnostic, not new supported spec.

Determine whether feature identity changes merely because sample rate changes for equivalent signals.

---

# 54. Duration Audit

Test same stable acoustic content at durations:

```text
50 ms
100 ms
250 ms
500 ms
1 s
2 s
```

Determine minimum useful duration and whether whole-segment integration biases results.

---

# 55. Boundary Condition Audit

Test:

- very short waveform;
- odd lengths;
- empty;
- NaN/Inf if input contract allows checking;
- clipped waveform;
- DC;
- extreme amplitude.

Fail closed; no crash or fabricated semantic confidence.

---

# 56. Legacy Test Coverage Audit

Inspect every current audio test.

For each record:

```text
TestName
WhatItActuallyTests
WhatClaimItAppearsToSupport
SyntheticOrReal
TemporalOrStatic
MixtureOrSeparate
ScientificStrength
MissingControls
```

Produce:

```text
aef_legacy_test_coverage.json
```

---

# 57. Legacy Benchmark Audit

Inspect all benchmark scripts touching audio.

Separate:

\[
BenchmarkName
\]

from:

\[
CapabilityActuallyMeasured
\]

No historical benchmark claim may be carried forward without matching evidence.

---

# 58. Representation Collision Audit

Across the forensic dataset, define legacy graph-facing signature:

```text
(fmt1_band, fmt2_band, voiced/unvoiced)
```

Count:

- total clips;
- unique signatures;
- collisions;
- cross-category collisions;
- temporal-permutation collisions;
- speaker collisions;
- source-mixture collisions.

---

# 59. Collision Interpretation

High collision rate is not automatically fatal if higher temporal structures exist.

But if the graph receives only the three-token signature, collisions become architectural evidence of information loss.

---

# 60. Channel-Time Sufficiency Comparison

Important diagnostic:

If the pre-collapse 16-channel time response distinguishes two signals that graph-facing features collapse, then the bottleneck is:

\[
\boxed{
FeatureDiscretization / TemporalCollapse
}
\]

not necessarily the cochlear frontend.

This distinction is required.

---

# 61. Frontend vs Discretizer Causal Isolation

For every failure, identify earliest loss point:

```text
RAW_INPUT
FILTERBANK
IHC
AGC
WHOLE_SEGMENT_AGGREGATION
F1_F2_SELECTION
VOICING
ONSET
SENSORY_EPISODE_PACKAGING
GRAPH_BUDGET
```

---

# 62. Audio v2 Requirements Matrix

This is the primary final artifact.

For each component:

```text
Component
LegacyBehavior
Evidence
FailureClass
Decision
RequiredV2Behavior
MustPreserve
MustRemove
MustAdd
NewPrimitiveNeeded
NewLawNeeded
Priority
```

Allowed decisions:

```text
KEEP
KEEP_WITH_FIX
REDESIGN
REPLACE
REMOVE
DEFER_TO_POST_ENCODER_SUBSYSTEM
```

---

# 63. Required Components in Matrix

At minimum:

1. raw waveform input contract;
2. sample normalization;
3. frequency mapping;
4. resonator topology;
5. IHC transduction;
6. fast adaptation;
7. slow adaptation;
8. streaming state;
9. spectral-time representation;
10. silence/no-evidence handling;
11. pitch/periodicity representation;
12. onset/offset representation;
13. event segmentation;
14. F1/F2 naming/semantics;
15. audio feature vocabulary;
16. temporal sequence output;
17. sensory budget;
18. transient identity;
19. paired-text coupling;
20. structural weight policy;
21. source mixtures;
22. source organization;
23. real-audio validation.

---

# 64. V2 Requirement Classification

Each requirement must be marked:

```text
PROVEN_NECESSARY
STRONGLY_SUPPORTED
PLAUSIBLE_BUT_UNPROVEN
NOT_NECESSARY
DEFERRED
```

Do not convert intuition into a mandatory architecture requirement.

---

# 65. New Primitive Necessity Audit

For every proposed v2 requirement ask:

\[
CanExistingSensoryEpisode / Sequence / Context / TransientStructuresRepresentThis?
\]

Only if no:

\[
UniqueArchitecturalNecessity(NewPrimitive)
\]

may be considered later.

This audit itself must not add one.

---

# 66. New Law Necessity Audit

Expected default:

\[
\boxed{
UniqueArchitecturalNecessity(NewLaw)=FALSE
}
\]

If any observation appears to require a new Law, report it as an unresolved proposal only.

No adoption.

---

# 67. Expected Layer Separation Candidate

The forensic report must assess whether evidence supports separating Audio v2 into:

```text
A. Signal Normalization
B. Cochlear / Time-Frequency Frontend
C. Temporal Acoustic Frames
D. Event / Onset / Offset Segmentation
E. Sparse Acoustic Descriptors
F. Temporal Audio IR / Existing Sensory Sequence
G. Separate Auditory Source Organization
H. Separate Cross-Modal Grounding Orchestration
```

This is a hypothesis, not pre-approved architecture.

---

# 68. Temporal IR Necessity Question

The audit must explicitly answer:

\[
\boxed{
DoesAudioV2NeedTemporalIR?
}
\]

Evidence must come from temporal collision tests and DGCA sequence compatibility.

---

# 69. Frame vs Event Representation Question

Determine whether v2 should expose:

```text
fixed temporal frames
event-driven segments
hybrid frames + event boundaries
```

No implementation.

---

# 70. Sparse Representation Requirement

Even if temporal structure is preserved, Audio v2 must remain sparse and bounded.

The audit should estimate:

- events/sec;
- tokens/event;
- active spectral channels/event;
- graph-facing episode rate.

Do not set final budgets until evidence exists.

---

# 71. Avoid Dense Spectrogram Dump

Audio v2 must not automatically dump every sample or every time-frequency bin into the graph.

The report must propose bounded sensory compression preserving causal temporal structure.

---

# 72. Real-Time / Streaming Complexity

Measure current legacy runtime on:

- 1 s;
- 5 s;
- 10 s;

at supported rates.

Report:

```text
WallTime
RealTimeFactor
PeakMemory
OutputSize
```

This is diagnostic, not a performance gate yet.

---

# 73. Audio Forensic Invariants

### AEF-INV-01 — Read-Only Diagnosis

No audio implementation modification.

### AEF-INV-02 — Architecture Frozen

No graph/law/schema changes.

### AEF-INV-03 — Current Code Is Evidence

Claims follow executable behavior.

### AEF-INV-04 — RFC Intent Kept Separate

Documentation is not treated as proof of implementation.

### AEF-INV-05 — Synthetic ≠ Real

Generated WAV is never labeled real-recorded audio.

### AEF-INV-06 — Separate Signals ≠ Mixture Separation

Source separation requires mixed-input evaluation.

### AEF-INV-07 — No Signal Must Be Audited

Silence path explicitly tested.

### AEF-INV-08 — Temporal Order Explicitly Tested

Whole-segment features cannot substitute for sequence evidence.

### AEF-INV-09 — Streaming Continuity Explicitly Tested

Chunk boundaries are audited.

### AEF-INV-10 — Channel Numerics Explicitly Tested

No nominal channel count accepted without effective response evidence.

### AEF-INV-11 — Feature Names Do Not Establish Semantics

F1/F2/F0 claims require behavior evidence.

### AEF-INV-12 — No External Learned Audio Model

Forensics may not outsource representation to ML.

### AEF-INV-13 — No Semantic Leakage

Paired-text coupling is audited, not used to improve results.

### AEF-INV-14 — Real Audio Required for Full Closure

Synthetic-only closure forbidden.

### AEF-INV-15 — Source Organization Separated from Encoding

Do not conflate cochlear representation and source separation.

### AEF-INV-16 — Failure Localized to Earliest Stage

Do not blame filterbank for downstream collapse without evidence.

### AEF-INV-17 — Same Input Determinism Audited

Call-order dependence is measured.

### AEF-INV-18 — No New Threshold Tuning

No tuning against forensic dataset.

### AEF-INV-19 — No V2 Implementation

Audit stops at requirements.

### AEF-INV-20 — No New Persistent State

Delta = 0.

### AEF-INV-21 — No New Law

Delta = 0.

### AEF-INV-22 — Historical Signature Preserved

No mutation.

### AEF-INV-23 — Requirements Are Evidence-Labeled

Every mandatory v2 requirement cites causal evidence.

### AEF-INV-24 — Scientific Claim Bounded

No human-hearing/source-separation claim without direct evidence.

Required:

\[
\boxed{24/24}
\]

---

# 74. Forbidden Actions Audit

The forensic execution must prove absence of:

1. Audio Encoder code modification;
2. graph mutation;
3. new persistent fields;
4. new cognitive primitives;
5. new Law;
6. new learned parameter;
7. threshold tuning on real-audio set;
8. pretrained speech model;
9. pretrained source-separation model;
10. pretrained embeddings;
11. text-label leakage into acoustic evaluation;
12. filename-label leakage into encoder;
13. synthetic audio mislabeled real;
14. separate-source test mislabeled source separation;
15. post-hoc replacement of failed clips;
16. hidden normalization chosen per class;
17. manual feature-family weights;
18. V2 implementation during audit.

Required:

\[
\boxed{18/18\ PASS}
\]

---

# 75. Forensic Gates

### AEF-G01 — Baseline Reproduction
Current Audio tests and behavior reproduced.

### AEF-G02 — RFC-vs-Code Claim Audit
Documented vs implemented behavior mapped.

### AEF-G03 — Filterbank Numerical Audit
All channels inspected.

### AEF-G04 — Tone / Impulse Response Audit
Frontend selectivity characterized.

### AEF-G05 — IHC / AGC Audit
Implemented dynamics mapped.

### AEF-G06 — Streaming-State Audit
Continuity status established.

### AEF-G07 — Silence / Low-Energy Audit
Fail-open/closed status established.

### AEF-G08 — F1/F2/F0/Onset Semantic Audit
Feature claims bounded.

### AEF-G09 — Temporal Collision Audit
Sequence retention quantified.

### AEF-G10 — Sensory Episode / Budget Audit
Graph-facing information loss quantified.

### AEF-G11 — Mixture Audit
Actual mixed signals tested.

### AEF-G12 — Cocktail-Party Claim Audit
Historical claim reconciled.

### AEF-G13 — Real Recorded Audio Audit
Minimum real-audio set executed.

### AEF-G14 — Paired-Text Authority Audit
Semantic coupling classified.

### AEF-G15 — UID / Determinism Audit
Identity behavior classified.

### AEF-G16 — Hard-Coded Policy Audit
Constants classified.

### AEF-G17 — V2 Requirements Matrix Complete
Every component has evidence-based disposition.

### AEF-G18 — Architecture Necessity Review
New Law/primitive necessity evaluated.

### AEF-G19 — Full Forensic Invariants
24/24.

### AEF-G20 — Historical Signature / No Mutation
Signature preserved.

Required for full closure:

\[
\boxed{20/20\ PASS}
\]

---

# 76. Required Machine-Readable Artifacts

Produce:

```text
DGCA-AUDIO-ENCODER-LEGACY-FORENSIC-AUDIT-REPORT.md

aef_baseline.json
aef_rfc08_vs_code.json
aef_carfac_claim_audit.json
aef_frequency_map.json
aef_filter_coefficients.jsonl
aef_tone_sweep.jsonl
aef_impulse_response.jsonl
aef_noise_agc.jsonl
aef_streaming_state.json
aef_segmentation_sensitivity.jsonl
aef_silence_safety.jsonl
aef_formant_semantics.jsonl
aef_pitch_voicing.jsonl
aef_onset_semantics.jsonl
aef_temporal_collision.jsonl
aef_representation_compression.json
aef_budget_audit.json
aef_mixture_results.jsonl
aef_cocktail_party_claim_audit.json
aef_real_audio_manifest.json
aef_real_audio_results.jsonl
aef_speaker_variation.json
aef_amplitude_invariance.jsonl
aef_noise_robustness.jsonl
aef_paired_text_authority.json
aef_uid_determinism.json
aef_structural_weight_audit.json
aef_numeric_policy_inventory.json
aef_sample_rate_audit.jsonl
aef_duration_audit.jsonl
aef_boundary_conditions.jsonl
aef_legacy_test_coverage.json
aef_legacy_benchmark_audit.json
aef_collision_summary.json
aef_loss_stage_localization.jsonl
aef_runtime_benchmark.json
aef_audio_v2_requirements_matrix.json
aef_invariants.json
aef_forbidden_actions.json
aef_gates.json
aef_signature_verification.json
aef_failures.jsonl
```

---

# 77. Required Human-Readable Report Structure

The master report must contain:

1. Executive forensic verdict;
2. RFC-08 vs implementation;
3. actual frontend topology;
4. numerical frequency/channel findings;
5. IHC findings;
6. AGC findings;
7. streaming findings;
8. silence safety findings;
9. temporal-collapse findings;
10. F1/F2/F0/onset semantic findings;
11. source-mixture findings;
12. real-recorded audio findings;
13. benchmark-claim reconciliation;
14. sensory authority / paired-text findings;
15. UID/determinism findings;
16. representation-budget findings;
17. earliest-loss causal map;
18. Audio v2 requirements matrix;
19. New Law / primitive necessity conclusion;
20. final readiness decision for Audio Encoder v2 design.

---

# 78. Allowed Legacy Encoder Verdicts

Use evidence-supported labels only:

```text
LEGACY_AUDIO_FRONTEND_PARTIALLY_USEFUL
LEGACY_AUDIO_FRONTEND_NUMERICALLY_DEFECTIVE
LEGACY_AUDIO_TEMPORAL_COLLAPSE_CONFIRMED
LEGACY_AUDIO_FEATURE_SEMANTICS_OVERCLAIMED
LEGACY_AUDIO_FAILS_CLOSED_SAFETY
LEGACY_AUDIO_FAILS_OPEN_ON_SILENCE
LEGACY_AUDIO_REAL_AUDIO_GENERALIZATION_PARTIAL
LEGACY_AUDIO_REAL_AUDIO_GENERALIZATION_FAILED
LEGACY_AUDIO_SOURCE_SEPARATION_NOT_DEMONSTRATED
LEGACY_AUDIO_SOURCE_MIXTURE_COLLAPSE_CONFIRMED
LEGACY_AUDIO_PAIRED_TEXT_AUTHORITY_VIOLATION
LEGACY_AUDIO_V2_REDESIGN_REQUIRED
FORENSIC_CLOSURE_PARTIAL
FORENSIC_CLOSURE_BLOCKED
```

Multiple verdicts may coexist where causal layers differ.

---

# 79. Required Final Audio v2 Questions

The forensic report must answer explicitly:

1. Should Audio v2 retain the current Greenwood mapping?
2. Should the 16-channel count remain?
3. Should a true cascade be required?
4. Is full official CAR-FAC necessary?
5. Should resonators remain simple deterministic DSP?
6. Should IHC half-wave/cubic transduction remain?
7. Is explicit IHC smoothing required?
8. Should fast/slow adaptation remain?
9. Must AGC state persist across chunks?
10. Must cochlear/filter state persist across chunks?
11. Should audio v2 expose a channel-time representation?
12. Does v2 require temporal frames?
13. Does v2 require event-driven segmentation?
14. Does v2 require onset timing?
15. Does v2 require offset timing?
16. Does v2 require actual pitch estimate or bounded pitch band?
17. Should F1/F2 naming be retained, replaced, or deferred?
18. Must silence produce NO_EVIDENCE?
19. Must low-energy ambiguity fail closed?
20. Must paired_text be removed from the sensory encoder?
21. Must transient scope identity come from outside the encoder?
22. Is `structural_weight=0.80` justified?
23. Is `B_audio=3` defensible?
24. How many sparse descriptors per temporal event appear sufficient?
25. Can existing `SensoryEpisode` represent audio temporal structure?
26. Is a new Audio IR required?
27. Is a new persistent primitive required?
28. Is a new normative Law required?
29. Should source separation live inside the encoder?
30. Or should auditory source organization be a separate subsystem?
31. What minimum real-audio benchmark must Audio v2 pass before grounding?
32. What are the exact mandatory requirements for Audio Encoder v2?

---

# 80. Expected Necessity Defaults

Unless evidence disproves:

\[
\boxed{
UniqueArchitecturalNecessity(NewLaw)=FALSE
}
\]

\[
\boxed{
UniqueArchitecturalNecessity(NewPersistentCognitivePrimitive)=FALSE
}
\]

A transient Audio IR may be justified if existing `SensoryEpisode` cannot safely encode sparse temporal structure.

That decision belongs to this audit.

---

# 81. Required Final Metrics Block

```text
============================================================
DGCA PHASE 2.6 — AUDIO ENCODER LEGACY FORENSIC AUDIT

EXECUTION MODE:
READ-ONLY FORENSIC

AUDIO-V2 IMPLEMENTATION:
0

ARCHITECTURE CHANGES:
0

PERSISTENT SCHEMA CHANGES:
0

NEW LAWS:
0

HISTORICAL SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / MISMATCH

LEGACY IMPLEMENTATION:
dgca/audio.py

RFC-08 VS IMPLEMENTATION:
MATCH / PARTIAL / MATERIAL_MISMATCH

CAR-FAC STRUCTURAL CLAIM:
SUPPORTED / PARTIAL / NOT_SUPPORTED

FILTER TOPOLOGY:
CASCADE / PARALLEL / OTHER

NOMINAL CHANNELS:
...

DISTINCT EFFECTIVE CHANNELS @8KHZ:
...

DISTINCT EFFECTIVE CHANNELS @16KHZ:
...

DEAD / DEGENERATE CHANNELS:
...

STREAMING STATE:
PRESENT / ABSENT / PARTIAL

CHUNK-BOUNDARY EQUIVALENCE:
PASS / FAIL

IHC:
...

AGC:
...

AGC STATE PERSISTS:
YES / NO

SILENCE -> ACOUSTIC EVIDENCE:
YES / NO

EMPTY INPUT -> FABRICATED FEATURES:
YES / NO

TEMPORAL ORDER RETAINED:
YES / NO / PARTIAL

TEMPORAL COLLISION RATE:
...

GRAPH-FACING AUDIO TOKENS PER SEGMENT:
...

F1 CLAIM:
SUPPORTED / OVERCLAIMED / PARTIAL

F2 CLAIM:
SUPPORTED / OVERCLAIMED / PARTIAL

F0 ESTIMATE:
PRESENT / ABSENT

VOICING ONLY:
YES / NO

ONSET PRESENCE:
SUPPORTED / UNSUPPORTED

ONSET TIMING:
PRESENT / ABSENT

MULTIPLE EVENTS:
REPRESENTED / COLLAPSED

REAL RECORDED AUDIO CLIPS:
...

REAL AUDIO BRANCH:
COMPLETE / PARTIAL / BLOCKED

REAL-AUDIO SIGNATURE COLLISIONS:
...

ACTUAL MIXTURE TESTS:
...

SOURCE SEPARATION:
DEMONSTRATED / NOT_DEMONSTRATED

SOURCE MIXTURE COLLAPSE:
YES / NO / PARTIAL

PAIRED_TEXT INSIDE ENCODER:
YES / NO

SEMANTIC AUTHORITY LEAKAGE RISK:
YES / NO

TRANSIENT UID CALL-ORDER DEPENDENT:
YES / NO

B_AUDIO = 3:
SUFFICIENT / TOO_AGGRESSIVE / CONTEXT_DEPENDENT / UNJUSTIFIED

TEMPORAL AUDIO IR NECESSITY:
PROVEN / STRONGLY_SUPPORTED / UNPROVEN / NOT_NEEDED

SOURCE ORGANIZATION:
ENCODER / SEPARATE_SUBSYSTEM / UNRESOLVED

NEW PERSISTENT PRIMITIVE NECESSARY:
YES / NO / UNRESOLVED

NEW LAW NECESSARY:
YES / NO / UNRESOLVED

AEF INVARIANTS:
x / 24

FORBIDDEN ACTIONS:
x / 18

FORENSIC GATES:
x / 20

FINAL LEGACY AUDIO VERDICT:
...

AUDIO ENCODER V2 REDESIGN:
REQUIRED / PARTIAL / NOT_REQUIRED

READY FOR AUDIO ENCODER V2 ARCHITECTURAL DESIGN:
YES / NO

============================================================
```

---

# 82. Closure Rule

The forensic audit closes only if:

\[
\boxed{
FrontendTopologyKnown
}
\]

and:

\[
\boxed{
ChannelNumericsKnown
}
\]

and:

\[
\boxed{
StreamingSemanticsKnown
}
\]

and:

\[
\boxed{
SilenceSafetyKnown
}
\]

and:

\[
\boxed{
TemporalInformationLossKnown
}
\]

and:

\[
\boxed{
FeatureSemanticValidityKnown
}
\]

and:

\[
\boxed{
RealAudioBehaviorKnown
}
\]

and:

\[
\boxed{
ActualMixtureBehaviorKnown
}
\]

and:

\[
\boxed{
V2RequirementsMatrixComplete
}
\]

---

# 83. Blocker Rule

If real recorded audio cannot be obtained:

do not claim complete forensic closure.

Use:

\[
\boxed{
FORENSIC\_CLOSURE\_PARTIAL
}
\]

with real-audio branch explicitly blocked.

Synthetic-only evidence is insufficient to finalize Audio Encoder v2 requirements.

---

# 84. Final Scientific Principle

The audit must locate the earliest information bottleneck.

If:

\[
CochlearTimeResponse
\]

still distinguishes sounds but:

\[
F1/F2/Voicing
\]

collapses them, then do not redesign the cochlear frontend unnecessarily.

If the channel-time response itself is defective, redesign must begin earlier.

Therefore:

\[
\boxed{
\textbf{Repair the earliest proven information-loss stage, not the most visible downstream symptom.}
}
\]

---

# 85. Final Deliverable

The final deliverable is not Audio Encoder v2.

It is:

\[
\boxed{
\textbf{DGCA Audio Encoder v2 — Evidence-Based Architectural Requirements}
}
\]

derived from:

\[
LegacyCode
+
DSPControls
+
TemporalControls
+
RealRecordedAudio
+
ActualSourceMixtures
+
DGCAAuthorityAudit
\]

Only after this forensic closure may:

\[
\boxed{
\textbf{DGCA Audio Encoder v2 — Architectural Design v1.0}
}
\]

be opened.
