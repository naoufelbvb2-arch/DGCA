# DGCA Audio Encoder v2 — Formal Architectural Specification v1.0

## Stateful Sparse Temporal Auditory Compiler

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Phase:** 2.6 — Multimodal Encoder & Grounding Validation  
**Component:** Audio Encoder v2  
**Document Type:** Formal Architectural Specification  
**Version:** 1.0  
**Status:** **FORMAL SPECIFICATION — CANDIDATE FOR FREEZE / PRE-IMPLEMENTATION**  
**Parent Design:** `DGCA-Audio-Encoder-v2-Architectural-Design-v1.0.md`  
**Parent Forensics:** `DGCA-Phase-2.6-Audio-Encoder-Legacy-Forensic-Audit-Specification-v1.0.md`  
**Historical Architecture Signature:** `915119d40643cb97`  
**Implementation Status:** **NOT IMPLEMENTED**  
**New Persistent Cognitive Primitives:** `0`  
**New Persistent Fields:** `0`  
**New Learned Scalars:** `0`  
**New Normative Laws:** `0`  
**Primary New Structures:** transient only  
**Core Verdict:** `AudioEncoderV2 = Stateful Sparse Temporal Auditory Compiler`

---

# 1. Normative Objective

Audio Encoder v2 MUST transform a continuous waveform into a deterministic, bounded, sparse, temporally ordered acoustic representation suitable for existing DGCA sensory and sequence machinery.

The normative transformation is:

\[
\boxed{
RawAudioStream
\rightarrow
StatefulTonotopicResponse
\rightarrow
TemporalAcousticFrames
\rightarrow
SparseAcousticEvents
\rightarrow
AudioTemporalIR
\rightarrow
ExistingSensoryEpisode/Sequence
}
\]

It MUST NOT collapse an entire clip into one orderless global feature tuple.

---

# 2. Constitutional Constraints

The implementation MUST preserve:

\[
\boxed{NewLaw=0}
\]

\[
\boxed{NewPersistentCognitivePrimitive=0}
\]

\[
\boxed{NewPersistentField=0}
\]

\[
\boxed{NewLearnedScalar=0}
\]

\[
\boxed{Backpropagation=0}
\]

\[
\boxed{PretrainedAudioSemantics=0}
\]

The encoder is sensory infrastructure, not a semantic model.

---

# 3. Governing Principles

### AE2-P01 — Audio Is Temporal

\[
AudioRepresentation \neq StaticFeatureBag
\]

### AE2-P02 — Sensor Authority Is Non-Semantic

\[
AudioEncoderMayDescribeSignal
\]

but:

\[
AudioEncoderMustNotSupplyLearnedMeaning
\]

### AE2-P03 — Chunk Boundaries Are Not Cognitive Boundaries

\[
ChunkBoundary\neq CognitiveBoundary
\]

### AE2-P04 — No Signal Does Not Fabricate Sound Identity

\[
NoLawfulAcousticEvidence
\Rightarrow
NoAcousticFeatureEmission
\]

### AE2-P05 — Dense Internal DSP, Sparse External Emission

\[
InternalDSP \;\text{may be dense}
\]

while:

\[
GraphFacingEvidence \;\text{must be sparse}
\]

### AE2-P06 — Descriptor Multiplicity Is Not Evidence Independence

\[
DescriptorMultiplicity\neq EvidenceIndependence
\]

### AE2-P07 — Source Organization Is Downstream

\[
AuditorySourceOrganization\neq AudioEncoding
\]

---

# 4. Normative Pipeline

```text
Raw Audio Stream
      |
      v
[AE2-A] Canonical Input Contract
      |
      v
[AE2-B] Stateful Tonotopic Filterbank
      |
      v
[AE2-C] IHC-like Rectification + Compression + Smoothing
      |
      v
[AE2-D] Fast/Slow Local Adaptation
      |
      v
[AE2-E] 10 ms Acoustic Frames / 5 ms Hop
      |
      +-----------------------+
      |                       |
      v                       v
[AE2-F1] Sparse Spectrum   [AE2-F2] Periodicity
      |                       |
      +-----------+-----------+
                  |
                  v
[AE2-G] Spectral/Energy Novelty + Boundary Evidence
                  |
                  v
[AE2-H] Acoustic Event Organizer
                  |
                  v
[AE2-I] AudioTemporalIR (TRANSIENT)
                  |
                  v
[AE2-J] Existing DGCA SensoryEpisode / Sequence Compiler
```

---

# 5. Input Contract

A canonical processing call MUST receive:

```text
samples
sample_rate_hz
channel_count
stream_scope_id
end_of_stream
reset
```

`stream_scope_id` MUST be supplied by the caller or existing DGCA orchestration.

The encoder MUST NOT create a global mutable UID authority.

---

# 6. Supported Input Sample Rates

Normative v1.0 supported rates:

```text
8000 Hz
16000 Hz
24000 Hz
48000 Hz
```

Any other rate returns:

```text
UNSUPPORTED
```

unless a future specification adds deterministic resampling.

Audio Encoder v2 v1.0 MUST NOT silently resample unsupported rates.

---

# 7. Channel Contract

Normative core processing is mono.

If `channel_count == 1`:

```text
SUPPORTED
```

If `channel_count > 1`:

- channel provenance MUST be preserved at the input boundary;
- v1.0 MAY deterministically downmix only if explicitly invoked by a caller policy;
- default core behavior is `SAFE_PARTIAL` or `UNSUPPORTED_MULTICHANNEL` unless a normative downmix path is implemented.

No binaural localization claim is permitted in v1.0.

---

# 8. Sample Value Contract

Canonical samples MUST be finite floating-point values in:

\[
[-1,1]
\]

Values outside the range MUST NOT be silently clipped unless the caller explicitly requests canonicalization.

NaN or Inf:

```text
UNSUPPORTED
```

Empty input:

```text
NO_EVIDENCE
```

---

# 9. Audio Stream State

A transient `AudioStreamState` MUST exist per active stream scope.

Candidate normative fields:

```text
stream_scope_id
sample_rate_hz
filter_z1[24]
filter_z2[24]
ihc_state[24]
fast_state[24]
slow_state[24]
frame_buffer
periodicity_buffer
previous_frame_spectrum
previous_frame_energy
novelty_baseline
event_state
frame_index
event_index
last_event_end
end_of_stream
```

This state is runtime-only.

---

# 10. State Reset Semantics

State is reset ONLY when:

```text
reset == True
```

or:

```text
stream_scope_id changes
```

or after finalization of a completed stream.

Ordinary chunk calls with the same stream scope MUST retain state.

---

# 11. Tonotopic Channel Count

Normative v1.0 channel count:

\[
\boxed{N_a=24}
\]

This is a fixed DSP design constant, not a learned parameter.

Rationale:

- greater spectral resolution than legacy 16;
- remains computationally bounded;
- enough spacing for sparse local peaks;
- does not imply semantic classes.

---

# 12. Tonotopic Frequency Range

For sample rate \(f_s\):

\[
f_{low}=80\;Hz
\]

\[
f_{high}
=
\min(12000,\;0.45f_s)
\]

Required:

\[
f_{high} < \frac{f_s}{2}
\]

At all supported rates.

---

# 13. ERB-Rate Frequency Mapping

Audio Encoder v2 uses ERB-rate spacing.

Define:

\[
ERBrate(f)
=
21.4\log_{10}\left(1+4.37\frac{f}{1000}\right)
\]

and inverse:

\[
ERB^{-1}(e)
=
\frac{1000}{4.37}
\left(10^{e/21.4}-1\right)
\]

Let:

\[
e_{low}=ERBrate(f_{low})
\]

\[
e_{high}=ERBrate(f_{high})
\]

For channel \(k\in\{0,\ldots,N_a-1\}\):

\[
e_k
=
e_{low}
+
\frac{k}{N_a-1}(e_{high}-e_{low})
\]

\[
\boxed{
f_k=ERB^{-1}(e_k)
}
\]

---

# 14. Frequency Map Invariants

Required:

\[
80=f_0<f_1<\ldots<f_{23}=f_{high}
\]

within floating-point tolerance.

Forbidden:

- duplicate centers;
- clamping multiple channels to one center;
- center at Nyquist;
- center above Nyquist.

---

# 15. ERB Bandwidth

Define equivalent rectangular bandwidth:

\[
BW(f)
=
24.7\left(1+4.37\frac{f}{1000}\right)
\]

For each channel:

\[
Q_k
=
\frac{f_k}{BW(f_k)}
\]

with normative lower bound:

\[
Q_k \ge 0.5
\]

The lower bound is numerical safety only.

---

# 16. Filter Topology

Each channel MUST use a deterministic stateful second-order band-pass biquad.

Audio v2 MUST NOT call this a true CAR-FAC.

Normative description:

\[
\boxed{StatefulERBSpacedBiquadFilterbank}
\]

---

# 17. Biquad Coefficients

For channel center \(f_k\):

\[
\omega_k
=
2\pi\frac{f_k}{f_s}
\]

\[
\alpha_k
=
\frac{\sin(\omega_k)}{2Q_k}
\]

Unnormalized coefficients:

\[
b_0=\alpha_k
\]

\[
b_1=0
\]

\[
b_2=-\alpha_k
\]

\[
a_0=1+\alpha_k
\]

\[
a_1=-2\cos(\omega_k)
\]

\[
a_2=1-\alpha_k
\]

Normalize all coefficients by \(a_0\).

---

# 18. Filter Numerical Safety

At construction time, every channel MUST satisfy:

```text
all coefficients finite
a0 != 0
0 < fk < Nyquist
filter stable under normative unit tests
nonzero impulse response
distinct center from adjacent channels
```

Failure causes encoder initialization failure.

No dead channel is tolerated.

---

# 19. Stateful Filter Processing

The biquad states MUST survive chunk calls.

For each channel:

\[
y_k[t]
=
b_0x[t]+z_{1,k}[t]
\]

\[
z_{1,k}[t+1]
=
b_1x[t]-a_1y_k[t]+z_{2,k}[t]
\]

\[
z_{2,k}[t+1]
=
b_2x[t]-a_2y_k[t]
\]

Equivalent stable Direct Form II Transposed implementation is allowed.

---

# 20. IHC Rectification

For channel output \(y_k[t]\):

\[
r_k[t]=\max(0,y_k[t])
\]

Half-wave rectification is mandatory.

---

# 21. IHC Compression

Normative compression:

\[
\boxed{
c_k[t]=r_k[t]^{1/3}
}
\]

No learned exponent.

The cube-root is a DSP compression constant.

---

# 22. IHC Smoothing

Normative time constant:

\[
\tau_{ihc}=2\;ms
\]

For sample interval:

\[
\Delta t=1/f_s
\]

EMA coefficient:

\[
\beta_{ihc}
=
1-e^{-\Delta t/\tau_{ihc}}
\]

State update:

\[
h_k[t]
=
h_k[t-1]
+
\beta_{ihc}(c_k[t]-h_k[t-1])
\]

State survives chunk boundaries.

---

# 23. Fast Adaptation

Normative:

\[
\tau_f=10\;ms
\]

\[
\beta_f
=
1-e^{-\Delta t/\tau_f}
\]

\[
F_k[t]
=
F_k[t-1]+\beta_f(h_k[t]-F_k[t-1])
\]

---

# 24. Slow Adaptation

Normative:

\[
\tau_s=100\;ms
\]

\[
\beta_s
=
1-e^{-\Delta t/\tau_s}
\]

\[
S_k[t]
=
S_k[t-1]+\beta_s(h_k[t]-S_k[t-1])
\]

---

# 25. Adapted Channel Activity

Define:

\[
\boxed{
A_k[t]
=
\frac{h_k[t]}
{1+\frac12F_k[t]+\frac12S_k[t]}
}
\]

This is local sensory compression.

It MUST NOT be interpreted as attention or semantic importance.

---

# 26. Frame Duration

Normative acoustic frame:

\[
T_f=10\;ms
\]

Normative hop:

\[
T_h=5\;ms
\]

At sample rate \(f_s\):

\[
L_f=round(T_ff_s)
\]

\[
L_h=round(T_hf_s)
\]

---

# 27. Frame Window

Normative frame window:

\[
\boxed{\text{Hann window}}
\]

Internal frame energy summaries MUST apply the same deterministic window at all supported sample rates.

---

# 28. Frame-Level Channel Energy

For frame \(n\), channel \(k\):

\[
E_{k,n}
=
\frac{
\sum_{t\in frame_n} w[t]A_k[t]^2
}{
\sum_t w[t]
}
\]

where \(w[t]\) is the Hann window.

---

# 29. Broadband Frame Energy

Define:

\[
E_n^{raw}
=
\frac1{L_f}
\sum_{t\in frame_n}x[t]^2
\]

and RMS:

\[
RMS_n=\sqrt{E_n^{raw}}
\]

Energy is tracked separately from normalized spectral shape.

---

# 30. Exact Digital Silence

If:

\[
\max_t |x[t]|=0
\]

over all samples accumulated for a frame:

\[
FrameStatus=NO\_EVIDENCE
\]

and no spectral or periodicity descriptor is emitted.

---

# 31. Near-Silence Floor

Normative absolute digital floor:

\[
RMS_n < 10^{-5}
\]

causes:

```text
LOW_ENERGY
```

Such a frame MAY contribute to a temporal gap, but MUST NOT emit spectral identity unless independent spectral prominence or periodicity evidence passes its own support rule.

This threshold is a DSP design constant, not learned.

---

# 32. Spectral Normalization

For nonzero total adapted channel energy:

\[
Z_n=\sum_kE_{k,n}
\]

If:

\[
Z_n>0
\]

define:

\[
p_{k,n}
=
\frac{E_{k,n}}{Z_n}
\]

Else no spectral evidence.

Thus:

\[
\sum_k p_{k,n}=1
\]

---

# 33. Local Spectral Peaks

A channel \(k\) is a local peak if:

\[
p_{k,n}>p_{k-1,n}
\]

and:

\[
p_{k,n}\ge p_{k+1,n}
\]

with boundary handling for channels 0 and 23.

Equal plateaus are resolved by choosing the lowest-frequency member only.

No iteration-order authority.

---

# 34. Spectral Peak Prominence

Let:

\[
m_n = median(p_{\cdot,n})
\]

A local peak is eligible if:

\[
p_{k,n}\ge 2m_n
\]

and:

\[
p_{k,n}\ge 0.05
\]

These are fixed DSP support constants.

No class-specific tuning.

---

# 35. Maximum Sparse Peaks Per Frame

Normative:

\[
\boxed{K_{frame}=4}
\]

Eligible peaks are ordered by:

1. descending \(p_{k,n}\);
2. ascending channel index as deterministic tie-break.

Select first four.

This tie-break has only representation-order authority, not semantic winner authority.

---

# 36. Spectral Band Descriptor

Each selected peak emits transient frame evidence:

```text
band_index
center_frequency_hz
relative_energy_share
provenance = spectral_peak
```

Graph-facing compilation may discretize by band index, not raw frequency float.

---

# 37. Periodicity Window

Normative periodicity analysis uses a trailing window:

\[
T_p=40\;ms
\]

updated at each 5 ms frame hop.

This longer window is independent of the 10 ms acoustic frame.

---

# 38. Periodicity Input Signal

Periodicity MUST be computed from the canonical mono waveform or another pre-envelope signal that preserves fine temporal structure.

It MUST NOT use only the slow IHC envelope.

---

# 39. Periodicity Search Range

Normative lag/frequency range:

\[
80\;Hz\le f_p\le 500\;Hz
\]

Equivalent lag bounds:

\[
\tau_{min}
=
\left\lfloor
\frac{f_s}{500}
\right\rfloor
\]

\[
\tau_{max}
=
\left\lceil
\frac{f_s}{80}
\right\rceil
\]

---

# 40. Normalized Autocorrelation

For periodicity buffer \(u[t]\), subtract mean first:

\[
v[t]=u[t]-\bar u
\]

For lag \(\tau\):

\[
R(\tau)
=
\frac{
\sum_t v[t]v[t-\tau]
}{
\sqrt{
\sum_t v[t]^2
\sum_t v[t-\tau]^2
}
+\epsilon
}
\]

with:

\[
\epsilon=10^{-12}
\]

numerical only.

---

# 41. Periodicity Support Rule

Let:

\[
R^*=\max_{\tau}R(\tau)
\]

and earliest lag among equal maxima:

\[
\tau^*
\]

Periodicity is supported if:

\[
R^*\ge 0.60
\]

and frame/window RMS is not LOW_ENERGY.

Otherwise:

```text
NO_PERIODICITY_EVIDENCE
```

---

# 42. Periodicity Frequency

If supported:

\[
f_p=\frac{f_s}{\tau^*}
\]

The graph MUST NOT receive raw \(f_p\) as an unbounded float.

---

# 43. Periodicity Bands

Normative logarithmic pitch/periodicity bins:

```text
P0: 80–110 Hz
P1: >110–155 Hz
P2: >155–220 Hz
P3: >220–310 Hz
P4: >310–440 Hz
P5: >440–500 Hz
```

These are acoustic periodicity ranges only.

They MUST NOT encode speaker sex, identity, or semantic class.

---

# 44. Periodicity Strength

Transient IR retains:

\[
R^*
\]

for event aggregation/diagnostics.

Graph-facing v1.0 emits only the periodicity band identity when supported.

---

# 45. Spectral Novelty

Define normalized spectral change:

\[
D^{spec}_n
=
\frac12
\sum_k
|p_{k,n}-p_{k,n-1}|
\]

for two valid spectral frames.

Range:

\[
0\le D^{spec}_n\le1
\]

---

# 46. Energy Novelty

Define:

\[
D^{eng}_n
=
\min\left(
1,
\left|
\log
\frac{RMS_n+\epsilon}
{RMS_{n-1}+\epsilon}
\right|
\right)
\]

with:

\[
\epsilon=10^{-12}
\]

---

# 47. Combined Novelty

Normative:

\[
\boxed{
D_n
=
0.7D^{spec}_n+0.3D^{eng}_n
}
\]

These are DSP weights, not semantic learned weights.

---

# 48. Novelty Baseline

Maintain transient EMA:

\[
\mu_n
=
(1-\lambda)\mu_{n-1}
+
\lambda D_n
\]

with effective time constant:

\[
\tau_D=250\;ms
\]

where:

\[
\lambda
=
1-e^{-T_h/\tau_D}
\]

---

# 49. Onset / Transition Candidate

A transition candidate is generated if:

\[
D_n \ge \max(0.25,\;2.5\mu_{n-1})
\]

and current frame is not `NO_EVIDENCE`.

This is class-independent signal policy.

---

# 50. Offset Candidate

An offset candidate occurs if:

- current frame is `NO_EVIDENCE` or `LOW_ENERGY`;
- previous event was active;
- condition persists for at least:

\[
T_{off}=20\;ms
\]

---

# 51. Onset Confirmation

An onset candidate becomes an event onset only if non-low-energy evidence persists for at least:

\[
T_{on}=10\;ms
\]

Exception:

A transient with peak RMS at least 4× the previous 100 ms RMS baseline may be emitted as a short transient event without 10 ms persistence.

This permits clicks/claps.

---

# 52. Event Refractory Interval

Normative minimum separation between independent event onsets:

\[
T_{ref}=20\;ms
\]

Within the refractory interval, new novelty contributes to the current event unless the previous event already ended.

This bounds event rate to at most approximately 50 onsets/sec.

---

# 53. Event Maximum Duration

Normative maximum event segment duration:

\[
T_{event,max}=1000\;ms
\]

If an acoustically continuous event exceeds this duration, it is split into deterministic continuation segments:

```text
CONTINUATION
```

The next event retains transient continuity metadata.

No semantic new event claim is implied.

---

# 54. Event Minimum Duration

Ordinary non-transient event minimum:

\[
T_{event,min}=10\;ms
\]

Shorter events are allowed only under the transient exception in AE2 §51.

---

# 55. Event Aggregation

For event \(j\), aggregate frame evidence over frames \(a..b\).

Event spectral support for band \(k\):

\[
S_{k,j}
=
\frac1{b-a+1}
\sum_{n=a}^{b}p_{k,n}
\]

using only frames where band spectrum is valid.

---

# 56. Event Spectral Peak Selection

Select local event spectral peaks using the same local-peak logic as frames.

Normative event spectral budget:

\[
\boxed{K_{event}=4}
\]

A band must appear as an eligible frame peak in at least:

\[
20\%
\]

of event-valid frames OR have event-average share:

\[
S_{k,j}\ge0.08
\]

to be eligible.

---

# 57. Event Periodicity

For all supported periodicity frames in event \(j\), determine the modal periodicity band.

Exact ties:

```text
NO_SINGLE_PERIODICITY_BAND
```

No lexical/index forced winner.

---

# 58. Event Energy Dynamics

Compute:

```text
event_rms_start
event_rms_median
event_rms_end
```

Graph-facing energy state is one of:

```text
RISING
STEADY
FALLING
PULSE
```

based on deterministic relative comparisons.

---

# 59. Energy Dynamic Rule

Let:

\[
r_s=RMS_{start}
\]

\[
r_m=median(RMS)
\]

\[
r_e=RMS_{end}
\]

Normative:

```text
RISING  if re >= 1.5*rs and rm >= rs
FALLING if rs >= 1.5*re and rm >= re
PULSE   if rm >= 2*max(rs,re)
STEADY  otherwise
```

No absolute loudness class is implied.

---

# 60. Event Duration State

If existing DGCA sequence timing preserves exact event duration, graph-facing duration token MUST be omitted.

The transient IR always stores exact start/end times.

Default v1.0:

\[
\boxed{NoPersistentDurationToken}
\]

unless implementation audit proves timing would otherwise be lost.

---

# 61. AcousticFrameIR Contract

Normative transient fields:

```text
frame_index: int
start_sample: int
end_sample: int
start_time_s: float
end_time_s: float

status:
  COMPLETE
  SAFE_PARTIAL
  LOW_ENERGY
  NO_EVIDENCE
  UNSUPPORTED

rms: float
normalized_spectrum[24]: transient-only
active_peaks: <=4

periodicity_supported: bool
periodicity_hz: optional float transient-only
periodicity_band: optional P0..P5
periodicity_strength: optional float

spectral_novelty: float
energy_novelty: float
combined_novelty: float

onset_candidate: bool
offset_candidate: bool
```

No field is persistent cognitive state.

---

# 62. AcousticEventIR Contract

Normative transient fields:

```text
event_index
stream_scope_id

start_frame
end_frame
start_time_s
end_time_s

status
continuation_from
continuation_to

spectral_bands <= 4
periodicity_band optional
energy_dynamic_state

onset_time_s
offset_time_s optional

source_provenance
diagnostics
```

---

# 63. AudioTemporalIR Contract

Normative:

```text
stream_scope_id
sample_rate_hz
status
events[]
diagnostics
```

Events MUST be time-ascending and non-overlapping within v1.0 core encoding.

Source-overlap organization is not handled here.

---

# 64. Canonical Ordering

Events:

\[
(start\_time,\ event\_index)
\]

Spectral bands inside an event:

1. descending event support;
2. ascending band index for exact support tie.

Periodicity has no forced winner on exact modal tie.

---

# 65. Graph-Facing Event Signals

A completed event may compile to neutral audio signals:

```text
aud:band:<0..23>          up to 4
aud:periodicity:<P0..P5> optional 1
aud:energy:<RISING|STEADY|FALLING|PULSE> optional 1
aud:boundary:onset       optional transient/event metadata
aud:boundary:offset      optional transient/event metadata
```

Boundary tokens SHOULD preferably be sequence metadata rather than persistent semantic nodes.

---

# 66. Per-Event Graph Evidence Budget

Normative persistent/graph-facing descriptor ceiling:

\[
\boxed{B_{audio,event}=8}
\]

This includes all acoustic descriptor tokens emitted for one event.

Sequence metadata does not count as an acoustic descriptor token if represented by existing temporal relations.

---

# 67. Budget Allocation

Maximum recommended:

```text
4 spectral bands
1 periodicity band
1 energy dynamic descriptor
2 reserved slots
```

Reserved slots MUST NOT be populated without formal evidence and authorization.

No automatic “fill to 8”.

---

# 68. No Global Clip Budget

There is no global:

\[
B_{audio}=3
\]

for the entire clip.

Budget is per event.

---

# 69. Event Rate Bound

Because:

\[
T_{ref}=20ms
\]

the theoretical independent onset rate is bounded at approximately:

\[
50/s
\]

Long-event continuation also has \(T_{event,max}=1s\).

Implementation MUST verify graph emission remains bounded.

---

# 70. Existing DGCA Sequence Compilation

Each `AcousticEventIR` compiles into an existing `SensoryEpisode` or the nearest existing equivalent.

The implementation MUST audit existing sequence APIs before adding any new persistent representation.

Required default:

\[
\boxed{ReuseExistingSequenceMachinery}
\]

---

# 71. Event Sequence Order

For events:

\[
E_1,E_2,\ldots,E_m
\]

the compiler MUST preserve:

\[
E_1\rightarrow E_2\rightarrow \cdots\rightarrow E_m
\]

using existing lawful temporal/sequence relation.

---

# 72. Gap Preservation

If event \(E_i\) ends at \(t_a\) and \(E_{i+1}\) begins at \(t_b\):

\[
Gap=t_b-t_a
\]

must remain available through existing timing/context metadata.

Silence MUST NOT be converted into fake spectral tokens.

---

# 73. No Paired Text

Audio Encoder v2 API MUST NOT accept:

```text
paired_text
gold_label
semantic_class
expected_word
speaker_label
```

Grounding occurs externally.

---

# 74. No Sensor-Owned Structural Weight

Audio Encoder v2 MUST NOT assign a cognitive `structural_weight` based on voiced/onset/audio content.

Any such authority belongs to existing downstream law/orchestration.

---

# 75. No Global Mutable UID

Forbidden:

```text
self._uid_counter
global_audio_counter
process_order_identity
```

Local deterministic IDs derive from:

```text
stream_scope_id
frame_index
event_index
```

---

# 76. Source Organization Boundary

Audio v2 core does NOT emit multiple source identities from one mixture.

Permitted claim:

```text
mixture evidence preservation
```

Forbidden claim:

```text
source separation
cocktail party solved
speaker streams recovered
```

---

# 77. Multi-Channel Preservation

If stereo input support is implemented later, channel provenance MUST remain transiently available to a future source-organization/localization subsystem.

No cross-channel semantic fusion is authorized here.

---

# 78. Evidence Provenance Families

Every graph-facing descriptor MUST be traceable to one transient provenance family:

```text
SPECTRAL_PEAK
PERIODICITY
ENERGY_DYNAMICS
BOUNDARY
TIMING
```

This supports future correlated-evidence audits.

---

# 79. Provenance Is Not a Cognitive Node

No persistent graph node named:

```text
spectral_peak_source
periodicity_source
energy_source
```

is created solely for provenance.

---

# 80. Chunk Equivalence

For a fixed stream \(X\):

\[
X=X_1||X_2||\ldots||X_m
\]

Processing as one chunk or arbitrary chunks MUST produce semantically equivalent final `AudioTemporalIR`.

Allowed differences:

- transient buffering timestamps within less than one hop;
- diagnostic floating-point accumulation under declared tolerance.

Event sequence, descriptor identities, and statuses MUST match.

---

# 81. Chunk Equivalence Tolerance

Numeric transient diagnostics may differ by at most:

\[
10^{-9}
\]

absolute for canonical deterministic test signals where identical operation order is preserved.

If chunking changes operation order, comparison must use semantic IR equivalence rather than bit identity.

---

# 82. Temporal Order Requirement

For controlled:

\[
A\rightarrow B
\]

and:

\[
B\rightarrow A
\]

AudioTemporalIR MUST differ in event order.

Required release test family includes at least 20 temporal permutations.

---

# 83. Silence Safety

Required tests:

```text
[]
zeros
near-zero noise
DC
room tone
silence gaps
```

Digital silence MUST produce no spectral/periodicity event.

Near-silence MUST NOT fabricate fixed band identities.

---

# 84. DC Safety

A DC-only waveform MUST NOT produce lawful tonotopic event evidence unless the filterbank legitimately produces a transient only at the change boundary.

Sustained DC is not an acoustic resonance identity.

---

# 85. Invalid Input Failure Atomicity

Invalid input MUST NOT:

- mutate graph;
- increment learned evidence;
- modify unrelated stream state;
- emit partial cognitive events.

It returns `UNSUPPORTED`.

---

# 86. Stream Scope Isolation

State from:

```text
stream A
```

MUST NOT leak into:

```text
stream B
```

Separate scopes have separate runtime state.

---

# 87. Determinism

Same:

```text
samples
sample_rate
scope
reset pattern
chunk boundaries
```

MUST produce identical canonical IR.

No randomized processing.

---

# 88. Sample-Rate Physical Consistency

Equivalent tones at supported rates should map to the nearest same physical ERB channel region.

No exact token identity across different sample-rate-specific upper ranges is required above the lower shared frequency range.

---

# 89. Pure Tone Selectivity

For a tone at channel center \(f_k\), the corresponding or immediately adjacent channel MUST be among top-2 frame peaks after transient startup.

This is a DSP acceptance condition.

---

# 90. Dead Channel Prohibition

Every channel MUST show nonzero response to its own center-frequency tone.

Required:

\[
24/24
\]

per supported sample rate.

---

# 91. Channel Distinctness

For adjacent center-frequency tones, the peak-response channel should not collapse universally to the same channel.

A full confusion matrix must be reported.

---

# 92. IHC / Adaptation Tests

Must include:

- impulse;
- step-like tone onset;
- sustained tone;
- amplitude scaling;
- sustained broadband noise;
- recovery after offset.

---

# 93. Periodicity Tests

At minimum test:

```text
80
100
120
160
200
250
320
400
500 Hz
```

plus:

- harmonically rich periodic signals;
- noise;
- amplitude-modulated noise;
- real voiced speech.

---

# 94. Periodicity Exact-Tie Rule

If two lag candidates have exactly equal maximum support, choose the shorter lag only for transient numerical representation if required by implementation.

Graph-facing periodicity band MUST become ambiguous/unsupported if the equal maxima map to distinct bins.

No silent false certainty.

---

# 95. Event Boundary Tests

Must include:

- onset at start;
- onset at arbitrary chunk boundary;
- onset mid-chunk;
- offset;
- two events;
- rapid click pair;
- gradual attack;
- spectral transition without silence;
- long sustained event;
- silence gap.

---

# 96. Event Continuation Test

A 3-second steady tone MUST produce bounded continuation events according to \(T_{event,max}=1s\), preserving continuation relation and not pretending they are independent semantic sounds.

---

# 97. Sparse Emission Test

For every event:

\[
DescriptorCount\le8
\]

Required 100%.

---

# 98. Frame Non-Persistence

No `AcousticFrameIR` field may enter persistent graph state directly unless compiled into an authorized event descriptor.

Static audit required.

---

# 99. No Dense Spectrogram Graph Dump

Forbidden code pattern:

```text
for each frame:
  for each channel:
      graph.observe(...)
```

unless current event compilation proves it is bounded and only sparse selected evidence is emitted.

---

# 100. Complexity Requirement

For \(N\) input samples:

\[
O(N\cdot24)
\]

frontend target.

Frame/event work MUST be linear in frame count and channel count.

Forbidden:

\[
O(T^2)
\]

full-frame all-pairs comparison.

---

# 101. Runtime Target

On reference development hardware, 10 seconds of 16 kHz mono audio SHOULD process with:

\[
RealTimeFactor < 1
\]

This is a performance target, not a cognitive validity condition.

Actual benchmark hardware must be reported.

---

# 102. Memory Requirement

Runtime memory MUST remain bounded with stream duration except for the explicitly returned current input-scope `AudioTemporalIR`.

Streaming mode SHOULD allow event consumption so completed old events need not remain indefinitely.

---

# 103. Real-Audio Validation Before Scientific Freeze

Implementation may be architecturally closed after synthetic/property/regression verification.

Scientific closure requires `Small Real Audio Trial 01`.

The trial is a separate empirical protocol.

---

# 104. Minimum Small Real Audio Trial 01

Target at least:

\[
\boxed{30\ genuine\ recorded\ clips}
\]

recommended distribution:

```text
12 speech
10 environmental/non-speech
4 room-tone/silence
4 mixtures
```

At least 3 human speakers.

No synthetic substitution.

---

# 105. Real-Audio Trial Phase A

Unimodal only.

Required metrics:

- COMPLETE/SAFE_PARTIAL/NO_EVIDENCE;
- event count;
- temporal stability;
- chunk equivalence;
- descriptor sparsity;
- recurrence across repeated/similar recordings;
- collisions.

No text grounding.

---

# 106. Real-Audio Trial Phase B

Only if Phase A valid:

Audio↔Text grounding may be tested through external grounding orchestration.

No `paired_text` inside encoder.

---

# 107. Mixture Claims

Even if mixed clips produce useful evidence, permitted claim is:

```text
MIXTURE_EVIDENCE_PRESERVED
```

not:

```text
SOURCE_SEPARATION_DEMONSTRATED
```

unless a future dedicated subsystem proves separation.

---

# 108. Legacy Token Migration

The following legacy tokens are deprecated in v2:

```text
aud:fmt1:band_*
aud:fmt2:band_*
aud:pitch:voiced
aud:pitch:unvoiced
```

unless explicitly mapped for backward-compatibility testing only.

They MUST NOT be the core v2 representation.

---

# 109. Legacy API Migration

Legacy:

```text
process_audio(waveform, paired_text=...)
```

is replaced conceptually by:

```text
begin_stream(...)
process_chunk(...)
end_stream(...)
```

or an equivalent stateful API.

A convenience one-shot API MAY wrap these without changing semantics.

---

# 110. One-Shot Equivalence

`process_waveform_once(X)` MUST be semantically equivalent to:

```text
begin_stream
process_chunk(X)
end_stream
```

---

# 111. Status Semantics

Canonical statuses:

```text
COMPLETE
SAFE_PARTIAL
NO_EVIDENCE
UNSUPPORTED
```

`LOW_ENERGY` is frame-internal and need not be top-level final status.

---

# 112. COMPLETE

All required audio processing succeeded and at least one lawful acoustic event exists.

---

# 113. SAFE_PARTIAL

Processing succeeded but evidence was incomplete, e.g.:

- truncated stream;
- multi-channel input partially handled by explicit policy;
- insufficient periodicity window;
- event at stream boundary not fully closed.

No guessed missing evidence.

---

# 114. NO_EVIDENCE

Valid input contained no lawful acoustic event under the signal rules.

No fabricated spectral identity.

---

# 115. UNSUPPORTED

Invalid or unsupported input contract.

No graph emission.

---

# 116. Forbidden Semantic Features

Audio v2 MUST NOT emit direct learned labels such as:

```text
word
phoneme
speaker
gender
emotion
instrument
bird
dog
car
music
language
```

unless learned downstream as ordinary DGCA concepts.

---

# 117. Forbidden External Models

Core implementation MUST NOT depend on:

```text
Whisper
wav2vec
HuBERT
CLAP
YAMNet
VGGish
speaker embeddings
neural VAD
neural source separation
```

---

# 118. Forbidden Hand Semantic Weights

No:

```text
pitch_is_more_important = 2.0
speech_band_weight = ...
formant_weight = ...
```

DSP coefficients are allowed only where specified here.

---

# 119. New Law Necessity

\[
\boxed{
UniqueArchitecturalNecessity(NewLaw)=FALSE
}
\]

Implementation MUST NOT introduce Law 19 or any equivalent.

---

# 120. New Persistent Primitive Necessity

\[
\boxed{
UniqueArchitecturalNecessity(NewPersistentPrimitive)=FALSE
}
\]

`AudioStreamState`, `AcousticFrameIR`, `AcousticEventIR`, `AudioTemporalIR` are transient only.

---

# 121. Audio Source Primitive

No persistent `AudioSource` primitive is authorized.

Source organization remains deferred.

---

# 122. Core Invariants

### AE2-INV-01 — Pure Sensory Authority
No semantic input to encoder.

### AE2-INV-02 — Stateful Stream Continuity
Same scope preserves DSP state.

### AE2-INV-03 — Scope Isolation
Different streams share no runtime state.

### AE2-INV-04 — Sub-Nyquist Channels
All centers strictly below Nyquist.

### AE2-INV-05 — Unique Channels
No duplicate frequency centers.

### AE2-INV-06 — No Dead Channels
Every channel responds to center tone.

### AE2-INV-07 — No Fabricated Silence Features
Digital silence emits no acoustic identity.

### AE2-INV-08 — Temporal Order Preserved
Meaningful A→B vs B→A remains ordered differently.

### AE2-INV-09 — Multiple Events Supported
One clip may produce multiple events.

### AE2-INV-10 — Timed Onset
Onset has a temporal location.

### AE2-INV-11 — Timed Offset
Offset has a temporal location when closed.

### AE2-INV-12 — Periodicity Beyond Binary Voicing
Supported periodicity produces bounded periodicity evidence.

### AE2-INV-13 — F1/F2 Core Semantics Removed
No formant overclaim.

### AE2-INV-14 — Sparse Graph Emission
At most 8 event descriptors.

### AE2-INV-15 — Internal Frames Transient
No direct persistent frame state.

### AE2-INV-16 — No Paired Text
Audio API does not accept semantic paired text.

### AE2-INV-17 — No Global Mutable UID
Identity derives from scope/time.

### AE2-INV-18 — No Sensor Structural Weight
No cognitive salience assigned by encoder.

### AE2-INV-19 — Source Separation Not Claimed
Mixture representation ≠ separation.

### AE2-INV-20 — Existing Sequence Reuse
No new persistent audio sequence ontology.

### AE2-INV-21 — No New Law
Delta laws = 0.

### AE2-INV-22 — No New Persistent Primitive
Delta primitives = 0.

### AE2-INV-23 — No Learned Scalar
All constants fixed DSP policy.

### AE2-INV-24 — Determinism
Same inputs/state produce same canonical IR.

### AE2-INV-25 — Chunk Equivalence
Chunking does not change semantic IR.

### AE2-INV-26 — Failure Atomicity
Invalid input emits no partial learned state.

### AE2-INV-27 — Complexity Linear
No quadratic temporal algorithm.

### AE2-INV-28 — Scientific Claim Bounded
No recognition/source-separation overclaim.

Required:

\[
\boxed{28/28\ PASS}
\]

---

# 123. Forbidden Mechanisms Audit

Verify absence of:

1. paired text inside encoder;
2. gold label input;
3. pretrained speech model;
4. pretrained audio embedding;
5. pretrained VAD;
6. pretrained source separator;
7. backprop;
8. learned frontend weights;
9. learned semantic feature weights;
10. new persistent audio primitive;
11. new persistent field;
12. new normative law;
13. global graph scan;
14. global mutable audio UID;
15. sensor-owned structural weight;
16. F1/F2 semantic claims without estimator;
17. dense every-frame-every-channel graph emission;
18. silence fallback bands;
19. lexical tie winner for periodicity ambiguity;
20. hidden resampling of unsupported rates;
21. silent clipping of invalid input;
22. source-separation claim from separate-signal tests;
23. class-specific thresholds;
24. real-audio tuning before frozen benchmark.

Required:

\[
\boxed{24/24\ PASS}
\]

---

# 124. Synthetic Acceptance Families

Required families:

```text
SA-01 frequency map
SA-02 center-tone selectivity
SA-03 channel impulse
SA-04 silence safety
SA-05 near-silence safety
SA-06 DC safety
SA-07 state continuity
SA-08 chunk equivalence
SA-09 amplitude scaling
SA-10 fast/slow adaptation
SA-11 periodicity
SA-12 aperiodic noise
SA-13 onset timing
SA-14 offset timing
SA-15 multiple events
SA-16 temporal permutations
SA-17 long-event continuation
SA-18 short transient
SA-19 sample-rate consistency
SA-20 mixture preservation
```

---

# 125. Property Test Families

At minimum:

### P01 — Frequency Monotonicity
24 unique ordered channels.

### P02 — Nyquist Safety
All supported rates.

### P03 — Center-Tone Liveness
24/24 channels respond.

### P04 — Determinism
Repeated runs identical.

### P05 — Chunk Equivalence
Random chunk boundaries.

### P06 — Scope Isolation
Interleaved streams do not interfere.

### P07 — Silence Non-Fabrication
All zero inputs.

### P08 — Temporal Permutation Distinction
Order preserved.

### P09 — Event Budget
Descriptors ≤ 8.

### P10 — Event Rate Bound
Refractory respected.

### P11 — No Persistent Frame State
Schema/static audit.

### P12 — No Semantic Input
API/static audit.

### P13 — Periodicity Conservation
Supported periodic signal maps consistently.

### P14 — Aperiodic Abstention
Noise does not force pitch band.

### P15 — Long-Stream Bounded Memory
Runtime state bounded.

### P16 — Invalid Input Atomicity
No graph mutation.

Required property seeds/cases:

\[
\boxed{\ge 30\ deterministic\ cases\ per\ applicable\ family}
\]

---

# 126. Adversarial Test Families

At minimum 24 cases including:

- empty;
- NaN;
- Inf;
- unsupported sample rate;
- channel mismatch;
- extreme amplitude;
- digital silence;
- DC;
- alternating chunk sizes;
- one-sample chunks;
- onset exactly at boundary;
- offset exactly at boundary;
- rapid clicks;
- periodic signal near 80 Hz;
- periodic signal near 500 Hz;
- periodic signal outside range;
- two equal autocorrelation maxima;
- flat spectrum;
- four+ spectral peaks;
- long steady tone;
- high-rate event train;
- voice+noise mixture;
- two-tone mixture;
- state reset mid-stream.

---

# 127. Benchmark Families

Required pre-release benchmarks:

```text
B01 1s @ 8k
B02 10s @ 8k
B03 1s @ 16k
B04 10s @ 16k
B05 1s @ 24k
B06 10s @ 24k
B07 1s @ 48k
B08 10s @ 48k
B09 long silence
B10 dense transient train
B11 sustained periodic
B12 actual real-audio batch
```

Report wall time, real-time factor, peak memory, event count, descriptor count.

---

# 128. Release Gates

### AE2-G01 — Input Contract
Valid/invalid behavior complete.

### AE2-G02 — Frequency Map
24 unique sub-Nyquist channels at all supported rates.

### AE2-G03 — Stateful Filterbank
State survives chunks.

### AE2-G04 — IHC
Rectification/compression/smoothing verified.

### AE2-G05 — Adaptation
Fast/slow dynamics verified.

### AE2-G06 — Frame Semantics
10ms/5ms frame contract verified.

### AE2-G07 — Sparse Spectrum
≤4 peaks/frame and deterministic.

### AE2-G08 — Periodicity
P0..P5 behavior and abstention verified.

### AE2-G09 — Boundary Detection
Timed onset/offset verified.

### AE2-G10 — Multi-Event
Multiple events preserved.

### AE2-G11 — Silence Safety
No fabricated features.

### AE2-G12 — Temporal Order
A→B != B→A.

### AE2-G13 — Chunk Equivalence
Semantic IR invariant to chunking.

### AE2-G14 — Event Budget
≤8 descriptors/event.

### AE2-G15 — Sequence Compiler
Existing DGCA sequence machinery reused.

### AE2-G16 — No Paired Text
Static/API audit.

### AE2-G17 — No Persistent Audio Primitive
Schema delta 0.

### AE2-G18 — No New Law
Law delta 0.

### AE2-G19 — No Learned Parameter
Static audit.

### AE2-G20 — No Source-Separation Overclaim
Mixture claim bounded.

### AE2-G21 — Determinism
Replay deterministic.

### AE2-G22 — Failure Atomicity
Invalid inputs non-mutating.

### AE2-G23 — Full Repository Regression
Pytest/Ruff/type-check pass.

### AE2-G24 — Signature Accounting
Historical cognitive signature preserved unless an explicitly authorized runtime-only signature is added.

Required:

\[
\boxed{24/24\ PASS}
\]

for architectural implementation closure.

---

# 129. Signature Policy

Historical cognitive baseline:

```text
915119d40643cb97
```

Audio v2 MUST NOT alter existing persistent cognitive schema/signature merely by introducing transient encoder runtime structures.

If a new behavioral encoder signature is created, it MUST be recorded separately and MUST NOT replace historical cognitive lineage.

---

# 130. Implementation Artifacts

Required:

```text
DGCA-AUDIO-ENCODER-V2-IMPLEMENTATION-VERIFICATION-REPORT.md

ae2_input_contract.json
ae2_frequency_map.json
ae2_filter_coefficients.jsonl
ae2_filter_liveness.jsonl
ae2_ihc_tests.jsonl
ae2_adaptation_tests.jsonl
ae2_frame_tests.jsonl
ae2_sparse_spectrum.jsonl
ae2_periodicity.jsonl
ae2_boundary_tests.jsonl
ae2_event_tests.jsonl
ae2_temporal_permutations.jsonl
ae2_chunk_equivalence.jsonl
ae2_scope_isolation.json
ae2_silence_safety.jsonl
ae2_mixture_preservation.jsonl
ae2_sequence_compiler.json
ae2_determinism.json
ae2_property_tests.json
ae2_adversarial.json
ae2_benchmarks.json
ae2_invariants.json
ae2_forbidden_mechanisms.json
ae2_release_gates.json
ae2_signature_verification.json
ae2_failures.jsonl
```

---

# 131. Implementation Workstreams

```text
AE2-W01 Canonical Input Contract
AE2-W02 ERB Frequency Map
AE2-W03 Stateful Biquad Filterbank
AE2-W04 IHC + Adaptation
AE2-W05 Frame Engine
AE2-W06 Sparse Spectrum
AE2-W07 Periodicity Branch
AE2-W08 Novelty / Boundary Engine
AE2-W09 Event Organizer
AE2-W10 AudioTemporalIR
AE2-W11 Existing Sequence Compiler
AE2-W12 Safety / Determinism
AE2-W13 Synthetic Verification
AE2-W14 Full Regression
```

Small Real Audio Trial 01 is a separate post-implementation empirical workstream.

---

# 132. Implementation Order

Implementation MUST proceed in this order:

1. input contract;
2. stream state;
3. ERB map;
4. filterbank;
5. IHC;
6. adaptation;
7. frame engine;
8. silence/no-evidence;
9. sparse spectrum;
10. periodicity;
11. novelty;
12. onset/offset;
13. event organizer;
14. AudioTemporalIR;
15. sequence compiler;
16. property/adversarial tests;
17. benchmarks;
18. full regression.

Do NOT start cross-modal grounding during Audio v2 core implementation.

---

# 133. Legacy Compatibility Tests

The implementation SHOULD retain legacy encoder code only as a baseline comparison until v2 closure.

It MUST NOT silently force v2 output to reproduce scientifically invalid legacy `F1/F2` tokens.

---

# 134. Scientific Closure Levels

### Architectural Closure

Requires:

- 28/28 invariants;
- 24/24 forbidden audit;
- 24/24 release gates;
- full repository regression.

### Empirical Real-Audio Closure

Requires separate Small Real Audio Trial 01.

Therefore:

\[
ArchitecturalClosure
\neq
RealWorldAudioValidation
\]

---

# 135. Allowed Implementation Verdicts

```text
AUDIO_V2_IMPLEMENTED_VERIFIED
AUDIO_V2_ARCHITECTURALLY_VALID
AUDIO_V2_TEMPORAL_REPRESENTATION_DEMONSTRATED
AUDIO_V2_STREAMING_EQUIVALENCE_DEMONSTRATED
AUDIO_V2_SILENCE_FAIL_CLOSED_DEMONSTRATED
AUDIO_V2_PARTIAL
AUDIO_V2_IMPLEMENTATION_BLOCKED
AUDIO_V2_REGRESSION
```

---

# 136. No Overclaim

Even if all synthetic and implementation gates pass, do not claim:

- speech recognition;
- speaker recognition;
- semantic sound recognition;
- source separation;
- human auditory equivalence;
- robust real-world audio understanding.

---

# 137. Required Final Metrics Block

```text
============================================================
DGCA AUDIO ENCODER v2 — IMPLEMENTATION VERIFICATION

SPECIFICATION:
DGCA-Audio-Encoder-v2-Formal-Architectural-Specification-v1.0

ARCHITECTURE:
STATEFUL SPARSE TEMPORAL AUDITORY COMPILER

NEW PERSISTENT COGNITIVE PRIMITIVES:
0 / NONZERO

NEW PERSISTENT FIELDS:
0 / NONZERO

NEW LEARNED SCALARS:
0 / NONZERO

NEW NORMATIVE LAWS:
0 / NONZERO

SUPPORTED SAMPLE RATES:
8000 / 16000 / 24000 / 48000

TONOTOPIC CHANNELS:
24

FREQUENCY MAP:
ERB

DEAD CHANNELS:
...

DUPLICATED CHANNELS:
...

STREAM STATE:
PRESENT / ABSENT

CHUNK EQUIVALENCE:
PASS / FAIL

IHC:
HALF-WAVE + CUBE-ROOT + 2MS SMOOTHING

FAST ADAPTATION:
10MS

SLOW ADAPTATION:
100MS

FRAME:
10MS

HOP:
5MS

MAX FRAME PEAKS:
4

PERIODICITY RANGE:
80–500 HZ

PERIODICITY BANDS:
6

TIMED ONSET:
YES / NO

TIMED OFFSET:
YES / NO

MULTIPLE EVENTS:
YES / NO

EVENT REFRACTORY:
20MS

MAX EVENT DURATION:
1000MS

MAX EVENT DESCRIPTORS:
8

SILENCE FABRICATES FEATURES:
YES / NO

PAIRED_TEXT INSIDE ENCODER:
YES / NO

GLOBAL MUTABLE UID:
YES / NO

SENSOR STRUCTURAL WEIGHT:
YES / NO

SOURCE SEPARATION CLAIM:
YES / NO

AUDIO TEMPORAL IR:
TRANSIENT / PERSISTENT

EXISTING DGCA SEQUENCE REUSED:
YES / NO

AE2 INVARIANTS:
x / 28

FORBIDDEN MECHANISMS:
x / 24

RELEASE GATES:
x / 24

PROPERTY TESTS:
...

ADVERSARIAL TESTS:
...

FULL PYTEST:
...

RUFF:
PASS / FAIL

TYPE CHECK:
PASS / FAIL

HISTORICAL COGNITIVE SIGNATURE:
915119d40643cb97

SIGNATURE STATUS:
MATCH / AUTHORIZED_SEPARATE_ENCODER_SIGNATURE / MISMATCH

FINAL VERDICT:
...

READY FOR SMALL REAL AUDIO TRIAL 01:
YES / NO
============================================================
```

---

# 138. Formal Freeze Decisions

The following are normative v1.0:

\[
N_a=24
\]

\[
FrequencyMap=ERB
\]

\[
f_{low}=80Hz
\]

\[
f_{high}=\min(12000,0.45f_s)
\]

\[
IHC=HalfWave+CubeRoot+2msEMA
\]

\[
FastAdaptation=10ms
\]

\[
SlowAdaptation=100ms
\]

\[
Frame=10ms
\]

\[
Hop=5ms
\]

\[
K_{frame}=4
\]

\[
PeriodicityWindow=40ms
\]

\[
PeriodicityRange=80..500Hz
\]

\[
PeriodicitySupport=0.60
\]

\[
Novelty=0.7Spectral+0.3Energy
\]

\[
OnsetThreshold=\max(0.25,2.5Baseline)
\]

\[
T_{on}=10ms
\]

\[
T_{off}=20ms
\]

\[
T_{ref}=20ms
\]

\[
T_{event,max}=1000ms
\]

\[
K_{event}=4
\]

\[
B_{audio,event}=8
\]

---

# 139. Final Formal Architecture Decision

\[
\boxed{
\textbf{DGCA Audio Encoder v2}
=
\textbf{Stateful ERB-Spaced Sparse Temporal Auditory Compiler}
}
\]

It uses deterministic signal processing to preserve bounded temporal acoustic evidence and compiles that evidence into existing DGCA event/sequence machinery.

It explicitly excludes semantic labeling and source-separation authority.

---

# 140. Pre-Implementation Status

\[
\boxed{
\textbf{FORMAL ARCHITECTURAL SPECIFICATION v1.0 — READY FOR FREEZE REVIEW}
}
\]

After freeze, the next step is:

\[
\boxed{
\textbf{Master Implementation & Verification Prompt — Audio Encoder v2}
}
\]


---

# 141. Normative Freeze Clarifications — Binding v1.0

The following clarifications were adopted during formal freeze review.
They are **normative** and override any earlier ambiguous wording in this document.

## AE2-FC-01 — Mono-Only v1.0 Core

Audio Encoder v2 v1.0 core is normatively:

```text
channel_count == 1
```

Any input with:

```text
channel_count != 1
```

returns:

```text
UNSUPPORTED
```

unless an upstream caller has already produced a canonical mono waveform.

The encoder itself performs no implicit downmixing in v1.0.

Future multi-channel preservation/localization remains deferred.

---

## AE2-FC-02 — Runtime-State Initialization

For a new `stream_scope_id`, all DSP/runtime state initializes deterministically:

```text
filter_z1[:] = 0
filter_z2[:] = 0
ihc_state[:] = 0
fast_state[:] = 0
slow_state[:] = 0

frame_index = 0
event_index = 0

previous_frame_spectrum = UNAVAILABLE
previous_frame_energy = UNAVAILABLE

novelty_baseline = 0

event_state = NO_EVIDENCE
```

No historical state is inherited from any other stream.

---

## AE2-FC-03 — Frame Anchoring and Chunk Independence

Frame and hop boundaries are anchored to the absolute sample index of the stream:

\[
sample\_index=0
\]

for the first sample of the stream.

Frame segmentation MUST therefore be independent of API chunk boundaries.

The runtime retains sufficient overlap/buffer state such that:

```text
process_once(X)
```

and:

```text
process_chunks(X1, X2, ..., Xm)
```

produce the same canonical frame boundaries and semantically equivalent `AudioTemporalIR`.

Chunks MUST NOT restart frame phase.

---

## AE2-FC-04 — LOW_ENERGY Authority

A frame with:

```text
status = LOW_ENERGY
```

MUST NOT emit graph-facing:

```text
spectral band identity
periodicity band identity
energy-dynamic identity
```

It may participate only in:

- temporal gap accounting;
- onset/offset confirmation;
- event termination;
- transient diagnostics.

Thus:

\[
LOW\_ENERGY
\Rightarrow
NoAcousticIdentityEmission
\]

This closes the legacy fail-open path for near-silence.

---

## AE2-FC-05 — Novelty Across Evidence Gaps

`D_spec`, `D_eng`, and combined novelty are computed only when both the previous and current frames contain valid non-low-energy acoustic evidence.

Transitions obey:

```text
NO_EVIDENCE / LOW_ENERGY -> VALID_EVIDENCE
    => onset candidate

VALID_EVIDENCE -> NO_EVIDENCE / LOW_ENERGY
    => offset candidate

NO_EVIDENCE / LOW_ENERGY -> NO_EVIDENCE / LOW_ENERGY
    => no novelty event
```

The first valid frame of a new stream therefore does not depend on an undefined previous spectrum.

---

## AE2-FC-06 — Event-Onset Timestamp

After the \(T_{on}=10ms\) persistence requirement is satisfied, the event onset timestamp is assigned to the **first valid frame in the confirmed run**, not the later confirmation frame.

For the short-transient exception, onset time is the first qualifying transient frame.

---

## AE2-FC-07 — Event-Offset Timestamp

After \(T_{off}=20ms\) of continuous `LOW_ENERGY` / `NO_EVIDENCE`, the event offset timestamp is assigned to the end of the **last valid acoustic frame before the low-energy run**.

The low-energy frames themselves do not become part of the acoustic event.

---

## AE2-FC-08 — Boundary Representation Authority

In v1.0:

```text
aud:boundary:onset
aud:boundary:offset
```

MUST NOT be emitted as persistent acoustic descriptor tokens.

Onset/offset are represented through:

- `AcousticEventIR` timestamps;
- existing DGCA temporal/sequence metadata during compilation.

Therefore the normal graph-facing acoustic descriptor maximum is:

```text
4 spectral
+ 1 periodicity
+ 1 energy dynamic
= 6 active descriptors
```

while:

\[
B_{audio,event}=8
\]

remains a hard future-safe ceiling with two reserved slots that MUST remain unused in v1.0.

---

## AE2-FC-09 — No Forced Periodicity on LOW_ENERGY

Periodicity support is evaluated only for valid non-low-energy frames/windows.

A high autocorrelation value in a low-energy or no-evidence window does not authorize a periodicity token.

---

## AE2-FC-10 — Event Non-Overlap

Audio Encoder v2 core emits a single ordered event stream:

\[
E_1 \rightarrow E_2 \rightarrow \cdots
\]

Core `AcousticEventIR` events MUST NOT overlap in time.

Overlapping physical sources remain unresolved mixtures for the future Auditory Source Organization subsystem.

---

## AE2-FC-11 — Graph Mutation Boundary

Audio Encoder v2 and all transient IR construction are graph-independent.

Graph mutation may occur only after an `AcousticEventIR` has been compiled into an existing lawful DGCA sensory/sequence episode and passed to existing learning authority.

Encoder failures, `NO_EVIDENCE`, `LOW_ENERGY`, and `UNSUPPORTED` MUST cause:

\[
\Delta PersistentGraph = 0
\]

---

## AE2-FC-12 — Formal Freeze Status

With these clarifications, the formal specification is adopted as:

\[
\boxed{
\textbf{DGCA Audio Encoder v2 — Formal Architectural Specification v1.0 — FROZEN}
}
\]

Normative DSP constants and contracts in this document are frozen for v1.0 implementation and may be changed only by a later explicit amendment/version after empirical evidence.
