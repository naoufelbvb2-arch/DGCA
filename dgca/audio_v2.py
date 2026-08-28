"""
DGCA Audio Encoder v2 — Stateful Sparse Temporal Auditory Compiler.

Authoritative Specification:
DGCA-Audio-Encoder-v2-Formal-Architectural-Specification-v1.0-FROZEN.md

Freeze Review:
DGCA-Audio-Encoder-v2-Formal-Specification-Freeze-Review-v1.0.md
"""
import math
from dataclasses import dataclass, field
from typing import ClassVar, Literal

import numpy as np

from .encoder import SensoryEpisode

# =====================================================================
# 1. TRANSIENT DATASTRUCTURES (ENCODER-LOCAL IR — NO PERSISTENT SCHEMA DELTA)
# =====================================================================

@dataclass
class AudioStreamState:
    """الحالة الزمنية المستمرة لمجرى صوتي محدد (Runtime-Only Scope State)."""

    stream_scope_id: str
    sample_rate_hz: int
    num_channels: int = 24
    filter_z1: list[float] = field(default_factory=lambda: [0.0] * 24)
    filter_z2: list[float] = field(default_factory=lambda: [0.0] * 24)
    ihc_state: list[float] = field(default_factory=lambda: [0.0] * 24)
    fast_state: list[float] = field(default_factory=lambda: [0.0] * 24)
    slow_state: list[float] = field(default_factory=lambda: [0.0] * 24)

    sample_buffer: list[float] = field(default_factory=list)
    adapted_buffer: list[list[float]] = field(default_factory=lambda: [[] for _ in range(24)])
    periodicity_buffer: list[float] = field(default_factory=list)

    previous_frame_spectrum: list[float] | None = None
    previous_frame_energy: float | None = None
    novelty_baseline: float = 0.0
    recent_rms_100ms: list[float] = field(default_factory=list)

    event_state: str = "NO_EVIDENCE"  # "NO_EVIDENCE", "IN_EVENT"
    frame_index: int = 0
    event_index: int = 0
    absolute_sample_index: int = 0

    active_event_start_frame: int | None = None
    active_event_first_valid_frame: int | None = None
    active_event_frames: list = field(default_factory=list)
    active_event_continuation_from: str | None = None

    low_energy_run_count: int = 0
    candidate_onset_frame: int | None = None
    end_of_stream: bool = False


@dataclass(frozen=True)
class AcousticFrameIR:
    """تمثيل الإطار السمعي اللحظي (10ms frame / 5ms hop)."""

    frame_index: int
    start_sample: int
    end_sample: int
    start_time_s: float
    end_time_s: float
    status: Literal["COMPLETE", "SAFE_PARTIAL", "LOW_ENERGY", "NO_EVIDENCE", "UNSUPPORTED"]
    rms: float
    normalized_spectrum: tuple[float, ...]
    active_peaks: tuple[tuple[int, float], ...]  # (channel_idx, relative_energy_share) up to K_frame=4
    periodicity_supported: bool
    periodicity_hz: float | None
    periodicity_band: str | None  # "P0".."P5"
    periodicity_strength: float | None
    spectral_novelty: float
    energy_novelty: float
    combined_novelty: float
    onset_candidate: bool
    offset_candidate: bool


@dataclass(frozen=True)
class AcousticEventIR:
    """تمثيل الحدث السمعي المكتمل المجمع (Bounded Sparse Acoustic Event)."""

    event_index: int
    stream_scope_id: str
    start_frame: int
    end_frame: int
    start_time_s: float
    end_time_s: float
    status: Literal["COMPLETE", "SAFE_PARTIAL"]
    continuation_from: str | None
    continuation_to: str | None
    spectral_bands: tuple[int, ...]  # up to 4 ERB channel indices
    periodicity_band: str | None  # P0..P5
    energy_dynamic_state: Literal["RISING", "STEADY", "FALLING", "PULSE"]
    onset_time_s: float
    offset_time_s: float | None
    descriptors: tuple[tuple[str, str], ...]  # emitted graph tokens
    source_provenance: tuple[str, ...]


@dataclass(frozen=True)
class AudioTemporalIR:
    """المصفوفة السمعية الزمنية العابرة الشاملة (Transient Temporal Audio IR)."""

    stream_scope_id: str
    sample_rate_hz: int
    status: Literal["COMPLETE", "SAFE_PARTIAL", "NO_EVIDENCE", "UNSUPPORTED"]
    events: tuple[AcousticEventIR, ...]
    diagnostics: dict


# =====================================================================
# 2. STATEFUL ERB BIQUAD FILTERBANK
# =====================================================================

class StatefulERBSpacedBiquadFilterbank:
    """مصفوفة المرشحات الرقمية ثنائية القطب ذات التدرج المكافئ للترددات (ERB-Spaced Biquad Filterbank)."""

    def __init__(self, num_channels: int = 24):
        self.num_channels = num_channels

    def compute_erb_frequencies(self, fs: float) -> list[float]:
        """حساب الترددات المركزية 24 وفق مقياس ERB من 80 هرتز إلى min(12000, 0.45*fs)."""
        f_low = 80.0
        f_high = min(12000.0, 0.45 * fs)
        assert f_high < fs / 2.0, f"f_high {f_high} >= Nyquist {fs/2.0}"

        def erb_rate(f: float) -> float:
            return 21.4 * math.log10(1.0 + 4.37 * (f / 1000.0))

        def erb_inv(e: float) -> float:
            return (1000.0 / 4.37) * (math.pow(10.0, e / 21.4) - 1.0)

        e_low = erb_rate(f_low)
        e_high = erb_rate(f_high)

        freqs = []
        for k in range(self.num_channels):
            e_k = e_low + (k / max(1, self.num_channels - 1)) * (e_high - e_low)
            f_k = erb_inv(e_k)
            freqs.append(f_k)
        return freqs

    def design_biquad(self, fc: float, fs: float) -> tuple[float, float, float, float, float]:
        """تصميم مرشح biquad ثنائي القطب لمقياس ERB."""
        bw = 24.7 * (1.0 + 4.37 * (fc / 1000.0))
        q = max(0.5, fc / bw)

        w0 = 2.0 * math.pi * fc / fs
        alpha = math.sin(w0) / (2.0 * q)

        b0 = alpha
        b1 = 0.0
        b2 = -alpha
        a0 = 1.0 + alpha
        a1 = -2.0 * math.cos(w0)
        a2 = 1.0 - alpha

        return b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0


# =====================================================================
# 3. AUDIO ENCODER V2 CORE IMPLEMENTATION
# =====================================================================

class AudioEncoderV2:
    """مُرمِّز الحاسة السمعية v2: مترجم سمعي زمني مستمر ومحدود (Stateful Sparse Temporal Auditory Compiler)."""

    SUPPORTED_SAMPLE_RATES: ClassVar[set[int]] = {8000, 16000, 24000, 48000}
    NUM_CHANNELS = 24
    K_FRAME_PEAKS = 4
    K_EVENT_PEAKS = 4
    MAX_EVENT_DESCRIPTORS = 8

    def __init__(self):
        self.filterbank = StatefulERBSpacedBiquadFilterbank(num_channels=self.NUM_CHANNELS)
        self.active_streams: dict[str, AudioStreamState] = {}

    def get_or_create_stream_state(
        self,
        stream_scope_id: str,
        sample_rate_hz: int,
        reset: bool = False,
    ) -> AudioStreamState:
        """جلب أو إنشاء حالة المجرى السمعي المستمر."""
        if reset or stream_scope_id not in self.active_streams:
            state = AudioStreamState(
                stream_scope_id=stream_scope_id,
                sample_rate_hz=sample_rate_hz,
                num_channels=self.NUM_CHANNELS,
            )
            self.active_streams[stream_scope_id] = state
            return state

        state = self.active_streams[stream_scope_id]
        if state.sample_rate_hz != sample_rate_hz:
            state = AudioStreamState(
                stream_scope_id=stream_scope_id,
                sample_rate_hz=sample_rate_hz,
                num_channels=self.NUM_CHANNELS,
            )
            self.active_streams[stream_scope_id] = state
        return state

    def process_chunk(
        self,
        samples: list[float] | np.ndarray,
        sample_rate_hz: int,
        channel_count: int = 1,
        stream_scope_id: str = "default_stream",
        end_of_stream: bool = False,
        reset: bool = False,
    ) -> AudioTemporalIR:
        """معالجة مقطع موجي سمعي مستمر وفق عقد المدخلات المعياري AE2-A."""
        # 1. Input Contract Validation
        if channel_count != 1:
            return AudioTemporalIR(
                stream_scope_id=stream_scope_id,
                sample_rate_hz=sample_rate_hz,
                status="UNSUPPORTED",
                events=(),
                diagnostics={"error": f"Unsupported channel_count: {channel_count}. Core v1.0 requires mono (1)."},
            )

        if sample_rate_hz not in self.SUPPORTED_SAMPLE_RATES:
            return AudioTemporalIR(
                stream_scope_id=stream_scope_id,
                sample_rate_hz=sample_rate_hz,
                status="UNSUPPORTED",
                events=(),
                diagnostics={"error": f"Unsupported sample_rate_hz: {sample_rate_hz}."},
            )

        if isinstance(samples, np.ndarray):
            if samples.ndim > 1:
                return AudioTemporalIR(
                    stream_scope_id=stream_scope_id,
                    sample_rate_hz=sample_rate_hz,
                    status="UNSUPPORTED",
                    events=(),
                    diagnostics={"error": "Multi-dimensional ndarray unsupported in mono v1.0."},
                )
            samples_arr = samples.astype(np.float64)
        else:
            samples_arr = np.array(samples, dtype=np.float64) if samples else np.array([], dtype=np.float64)

        if samples_arr.size == 0 and not end_of_stream:
            return AudioTemporalIR(
                stream_scope_id=stream_scope_id,
                sample_rate_hz=sample_rate_hz,
                status="NO_EVIDENCE",
                events=(),
                diagnostics={"info": "Empty samples input."},
            )

        if samples_arr.size > 0 and (not np.all(np.isfinite(samples_arr)) or np.any(np.abs(samples_arr) > 1.0)):
            return AudioTemporalIR(
                stream_scope_id=stream_scope_id,
                sample_rate_hz=sample_rate_hz,
                status="UNSUPPORTED",
                events=(),
                diagnostics={"error": "Sample contains NaN/Inf or out of range [-1, 1]."},
            )

        samples_list = samples_arr.tolist()

        # 2. Get / Maintain Stream State
        state = self.get_or_create_stream_state(stream_scope_id, sample_rate_hz, reset=reset)
        state.end_of_stream = end_of_stream
        state.sample_buffer.extend(samples_list)

        max_p_samples = int(0.100 * sample_rate_hz)

        # DSP Setup
        fs = float(sample_rate_hz)
        dt = 1.0 / fs
        freqs = self.filterbank.compute_erb_frequencies(fs)

        coeffs = [self.filterbank.design_biquad(fc, fs) for fc in freqs]
        b0_lst = [c[0] for c in coeffs]
        b1_lst = [c[1] for c in coeffs]
        b2_lst = [c[2] for c in coeffs]
        a1_lst = [c[3] for c in coeffs]
        a2_lst = [c[4] for c in coeffs]

        beta_ihc = 1.0 - math.exp(-dt / 0.002)
        beta_fast = 1.0 - math.exp(-dt / 0.010)
        beta_slow = 1.0 - math.exp(-dt / 0.100)

        z1_lst = state.filter_z1
        z2_lst = state.filter_z2
        ihc_lst = state.ihc_state
        fast_lst = state.fast_state
        slow_lst = state.slow_state

        # Direct High-Speed Streaming List Append
        ad_buf = state.adapted_buffer
        for x in samples_list:
            state.absolute_sample_index += 1
            for k in range(self.NUM_CHANNELS):
                y_k = b0_lst[k] * x + z1_lst[k]
                z1_lst[k] = b1_lst[k] * x - a1_lst[k] * y_k + z2_lst[k]
                z2_lst[k] = b2_lst[k] * x - a2_lst[k] * y_k

                r_k = max(0.0, y_k)
                c_k = math.pow(r_k, 1.0 / 3.0) if r_k > 0.0 else 0.0

                ihc_lst[k] += beta_ihc * (c_k - ihc_lst[k])
                fast_lst[k] += beta_fast * (ihc_lst[k] - fast_lst[k])
                slow_lst[k] += beta_slow * (ihc_lst[k] - slow_lst[k])

                ad_buf[k].append(ihc_lst[k] / (1.0 + 0.5 * fast_lst[k] + 0.5 * slow_lst[k]))

        # Frame & Hop sizes
        L_f = max(1, round(0.010 * fs))
        L_h = max(1, round(0.005 * fs))

        emitted_events: list[AcousticEventIR] = []

        while len(state.sample_buffer) >= L_f or (state.end_of_stream and len(state.sample_buffer) > 0):
            if len(state.sample_buffer) >= L_f:
                frame_samples = state.sample_buffer[:L_f]
                frame_adapted = [ad_buf[k][:L_f] for k in range(self.NUM_CHANNELS)]
                hopped_smps = state.sample_buffer[:L_h]
                del state.sample_buffer[:L_h]
                for k in range(self.NUM_CHANNELS):
                    del ad_buf[k][:L_h]
                state.periodicity_buffer.extend(hopped_smps)
                if len(state.periodicity_buffer) > max_p_samples:
                    del state.periodicity_buffer[:-max_p_samples]
            else:
                frame_samples = state.sample_buffer
                frame_adapted = ad_buf
                state.periodicity_buffer.extend(frame_samples)
                if len(state.periodicity_buffer) > max_p_samples:
                    del state.periodicity_buffer[:-max_p_samples]
                state.sample_buffer = []
                state.adapted_buffer = [[] for _ in range(self.NUM_CHANNELS)]
                ad_buf = state.adapted_buffer

            # Frame Metrics (Vectorized)
            frame_idx = state.frame_index
            state.frame_index += 1

            start_sample = frame_idx * L_h
            end_sample = start_sample + len(frame_samples)
            start_time_s = start_sample / fs
            end_time_s = end_sample / fs

            f_smps_np = np.array(frame_samples, dtype=np.float64) if frame_samples else np.array([], dtype=np.float64)
            rms = math.sqrt(float(np.dot(f_smps_np, f_smps_np)) / len(frame_samples)) if f_smps_np.size > 0 else 0.0

            state.recent_rms_100ms.append(rms)
            if len(state.recent_rms_100ms) > 20:
                state.recent_rms_100ms.pop(0)

            max_abs = float(np.max(np.abs(f_smps_np))) if f_smps_np.size > 0 else 0.0
            if max_abs == 0.0:
                frame_status = "NO_EVIDENCE"
            elif rms < 1e-5:
                frame_status = "LOW_ENERGY"
            else:
                frame_status = "COMPLETE"

            hann_w = np.hanning(len(frame_samples))
            w_sum = float(np.sum(hann_w)) if len(frame_samples) > 0 else 1.0

            if len(frame_samples) > 0 and w_sum > 0:
                ch_arr = np.array(frame_adapted, dtype=np.float64)
                frame_energies = np.sum(hann_w * (ch_arr ** 2), axis=1) / w_sum
                frame_energies = frame_energies.tolist()
            else:
                frame_energies = [0.0] * self.NUM_CHANNELS

            z_n = sum(frame_energies)
            if z_n > 0.0 and frame_status == "COMPLETE":
                p_kn = [e / z_n for e in frame_energies]
            else:
                p_kn = [0.0] * self.NUM_CHANNELS

            active_peaks = []
            if frame_status == "COMPLETE" and z_n > 0.0:
                med_p = float(np.median(p_kn))
                local_peaks = []
                for k in range(self.NUM_CHANNELS):
                    val = p_kn[k]
                    if val < 0.05 or val < 2.0 * med_p:
                        continue
                    is_pk = False
                    if k == 0:
                        is_pk = (val >= p_kn[1]) if self.NUM_CHANNELS > 1 else True
                    elif k == self.NUM_CHANNELS - 1:
                        is_pk = (val > p_kn[k - 1])
                    else:
                        is_pk = (val > p_kn[k - 1]) and (val >= p_kn[k + 1])

                    if is_pk:
                        local_peaks.append((k, val))

                local_peaks.sort(key=lambda p: (-p[1], p[0]))
                active_peaks = local_peaks[: self.K_FRAME_PEAKS]

            # Fast Fully Vectorized FFT-based Periodicity Analysis
            periodicity_supported = False
            periodicity_hz = None
            periodicity_band = None
            periodicity_strength = None

            past_audio = state.periodicity_buffer + (frame_samples[L_h:] if len(frame_samples) > L_h else [])
            if frame_status == "COMPLETE" and len(past_audio) >= int(0.040 * fs):
                p_buf = np.array(past_audio[-int(0.040 * fs):], dtype=np.float64)
                p_buf_c = p_buf - np.mean(p_buf)
                var_p = float(np.sum(p_buf_c ** 2))

                if var_p > 1e-12:
                    min_lag = math.floor(fs / 500.0)
                    max_lag = math.ceil(fs / 80.0)
                    max_lag = min(max_lag, len(p_buf_c) - 1)

                    if max_lag >= min_lag:
                        n_fft = 2 ** math.ceil(math.log2(2 * len(p_buf_c)))
                        fft_p = np.fft.rfft(p_buf_c, n_fft)
                        autocorr = np.fft.irfft(fft_p * np.conj(fft_p), n_fft)[: max_lag + 1]

                        cum_sq = np.cumsum(p_buf_c ** 2)
                        tot_sq = cum_sq[-1]
                        lags = np.arange(min_lag, max_lag + 1)

                        cum_sq_prep = np.concatenate(([0.0], cum_sq))
                        v1_sq = np.maximum(1e-12, tot_sq - cum_sq_prep[lags - 1])
                        v2_sq = np.maximum(1e-12, cum_sq[-1 - lags])
                        denoms = np.sqrt(v1_sq * v2_sq)

                        corrs = autocorr[lags] / denoms
                        corrs = np.nan_to_num(corrs, nan=-1.0)

                        best_idx = int(np.argmax(corrs))
                        best_r = float(corrs[best_idx])
                        best_lag = int(lags[best_idx])

                        ties = [int(lags[i]) for i in range(len(lags)) if abs(corrs[i] - best_r) < 1e-6]

                        if best_r >= 0.60:
                            bands_for_ties = []
                            for lg in ties:
                                f_val = fs / lg
                                if 80 <= f_val <= 110:
                                    b_id = "P0"
                                elif 110 < f_val <= 155:
                                    b_id = "P1"
                                elif 155 < f_val <= 220:
                                    b_id = "P2"
                                elif 220 < f_val <= 310:
                                    b_id = "P3"
                                elif 310 < f_val <= 440:
                                    b_id = "P4"
                                elif 440 < f_val <= 500:
                                    b_id = "P5"
                                else:
                                    b_id = None
                                bands_for_ties.append(b_id)

                            distinct_bands = set(bands_for_ties) - {None}
                            if len(distinct_bands) == 1:
                                periodicity_supported = True
                                periodicity_hz = fs / best_lag
                                periodicity_band = next(iter(distinct_bands))
                                periodicity_strength = best_r

            # Novelty Calculation
            if state.previous_frame_spectrum is not None and frame_status == "COMPLETE":
                d_spec = 0.5 * sum(abs(p_kn[k] - state.previous_frame_spectrum[k]) for k in range(self.NUM_CHANNELS))
                eps = 1e-12
                d_eng = min(1.0, abs(math.log((rms + eps) / (state.previous_frame_energy + eps))))
                combined_novelty = 0.7 * d_spec + 0.3 * d_eng

                lambda_n = 1.0 - math.exp(-0.005 / 0.250)
                state.novelty_baseline = (1.0 - lambda_n) * state.novelty_baseline + lambda_n * combined_novelty
            else:
                d_spec = 0.0
                d_eng = 0.0
                combined_novelty = 0.0

            if frame_status == "COMPLETE":
                state.previous_frame_spectrum = p_kn
                state.previous_frame_energy = rms

            onset_cand = False
            offset_cand = False

            if frame_status == "COMPLETE" and (state.event_state == "NO_EVIDENCE" or combined_novelty >= max(0.25, 2.5 * state.novelty_baseline)):
                onset_cand = True

            if frame_status in ("LOW_ENERGY", "NO_EVIDENCE") and state.event_state == "IN_EVENT":
                offset_cand = True

            frame_ir = AcousticFrameIR(
                frame_index=frame_idx,
                start_sample=start_sample,
                end_sample=end_sample,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                status=frame_status,
                rms=rms,
                normalized_spectrum=tuple(p_kn),
                active_peaks=tuple(active_peaks),
                periodicity_supported=periodicity_supported,
                periodicity_hz=periodicity_hz,
                periodicity_band=periodicity_band,
                periodicity_strength=periodicity_strength,
                spectral_novelty=d_spec,
                energy_novelty=d_eng,
                combined_novelty=combined_novelty,
                onset_candidate=onset_cand,
                offset_candidate=offset_cand,
            )

            # 5. Event Organization
            if frame_status == "COMPLETE":
                state.low_energy_run_count = 0

                if state.event_state == "NO_EVIDENCE":
                    state.event_state = "IN_EVENT"
                    state.active_event_start_frame = frame_idx
                    state.active_event_first_valid_frame = frame_idx
                    state.active_event_frames = [frame_ir]
                else:
                    state.active_event_frames.append(frame_ir)
                    if len(state.active_event_frames) >= 200:
                        evt = self._compile_event(state, end_status="COMPLETE", continuation_to=f"evt_{state.event_index + 1}")
                        emitted_events.append(evt)
                        state.event_index += 1

                        state.active_event_start_frame = frame_idx
                        state.active_event_first_valid_frame = frame_idx
                        state.active_event_frames = [frame_ir]
                        state.active_event_continuation_from = evt.stream_scope_id
            else:
                if state.event_state == "IN_EVENT":
                    state.low_energy_run_count += 1
                    if state.low_energy_run_count >= 4:
                        evt = self._compile_event(state, end_status="COMPLETE")
                        emitted_events.append(evt)
                        state.event_index += 1

                        state.event_state = "NO_EVIDENCE"
                        state.active_event_start_frame = None
                        state.active_event_first_valid_frame = None
                        state.active_event_frames = []
                        state.active_event_continuation_from = None

            if state.end_of_stream and len(state.sample_buffer) < L_f:
                break

        if state.end_of_stream and state.event_state == "IN_EVENT" and state.active_event_frames:
            evt = self._compile_event(state, end_status="COMPLETE")
            emitted_events.append(evt)
            state.event_index += 1
            state.event_state = "NO_EVIDENCE"
            state.active_event_frames = []

        overall_status = "COMPLETE" if emitted_events else "NO_EVIDENCE"

        return AudioTemporalIR(
            stream_scope_id=stream_scope_id,
            sample_rate_hz=sample_rate_hz,
            status=overall_status,
            events=tuple(emitted_events),
            diagnostics={
                "frames_processed": state.frame_index,
                "events_emitted": len(emitted_events),
            },
        )

    def _compile_event(
        self,
        state: AudioStreamState,
        end_status: str = "COMPLETE",
        continuation_to: str | None = None,
    ) -> AcousticEventIR:
        """تجميع الأطر الزمنية السمعية إلى حدث سمعي محدد محدود (Acoustic Event IR)."""
        valid_frames = [f for f in state.active_event_frames if f.status == "COMPLETE"]
        if not valid_frames:
            valid_frames = state.active_event_frames

        first_f = valid_frames[0]
        last_f = valid_frames[-1]

        start_time_s = first_f.start_time_s
        end_time_s = last_f.end_time_s

        all_specs = [np.array(f.normalized_spectrum) for f in valid_frames]
        mean_spec = np.mean(all_specs, axis=0) if all_specs else np.zeros(self.NUM_CHANNELS)

        eligible_bands = []
        for k in range(self.NUM_CHANNELS):
            count_as_peak = sum(1 for f in valid_frames if any(p[0] == k for p in f.active_peaks))
            ratio = count_as_peak / max(1, len(valid_frames))
            if ratio >= 0.20 or mean_spec[k] >= 0.08:
                eligible_bands.append((k, mean_spec[k]))

        eligible_bands.sort(key=lambda b: (-b[1], b[0]))
        selected_bands = tuple([b[0] for b in eligible_bands[: self.K_EVENT_PEAKS]])

        p_bands = [f.periodicity_band for f in valid_frames if f.periodicity_supported and f.periodicity_band]
        if p_bands:
            from collections import Counter
            counts = Counter(p_bands)
            most_common = counts.most_common()
            if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
                modal_p_band = None
            else:
                modal_p_band = most_common[0][0]
        else:
            modal_p_band = None

        rms_vals = [f.rms for f in valid_frames]
        rs = rms_vals[0] if rms_vals else 0.0
        rm = float(np.median(rms_vals)) if rms_vals else 0.0
        re = rms_vals[-1] if rms_vals else 0.0

        if re >= 1.5 * rs and rm >= rs:
            dynamic_state = "RISING"
        elif rs >= 1.5 * re and rm >= re:
            dynamic_state = "FALLING"
        elif rm >= 2.0 * max(rs, re):
            dynamic_state = "PULSE"
        else:
            dynamic_state = "STEADY"

        descriptors = []
        for b in selected_bands:
            descriptors.append(("audio", f"aud:band:{b}"))
        if modal_p_band:
            descriptors.append(("audio", f"aud:periodicity:{modal_p_band}"))
        descriptors.append(("audio", f"aud:energy:{dynamic_state}"))

        return AcousticEventIR(
            event_index=state.event_index,
            stream_scope_id=state.stream_scope_id,
            start_frame=first_f.frame_index,
            end_frame=last_f.frame_index,
            start_time_s=start_time_s,
            end_time_s=end_time_s,
            status=end_status,
            continuation_from=state.active_event_continuation_from,
            continuation_to=continuation_to,
            spectral_bands=selected_bands,
            periodicity_band=modal_p_band,
            energy_dynamic_state=dynamic_state,
            onset_time_s=start_time_s,
            offset_time_s=end_time_s,
            descriptors=tuple(descriptors[: self.MAX_EVENT_DESCRIPTORS]),
            source_provenance=("SPECTRAL_PEAK", "PERIODICITY", "ENERGY_DYNAMICS", "TIMING"),
        )

    def process_waveform_once(
        self,
        samples: list[float] | np.ndarray,
        sample_rate_hz: int = 8000,
        channel_count: int = 1,
        stream_scope_id: str = "one_shot_stream",
    ) -> AudioTemporalIR:
        """معالجة موجة صوتية كاملة في نداء واحد عبر المجرى المستمر."""
        return self.process_chunk(
            samples=samples,
            sample_rate_hz=sample_rate_hz,
            channel_count=channel_count,
            stream_scope_id=stream_scope_id,
            end_of_stream=True,
            reset=True,
        )


# =====================================================================
# 4. AUDIO SENSORY PIPELINE V2 (SEQUENCE COMPILER)
# =====================================================================

class AudioSensoryPipelineV2:
    """مُرمِّز وتجميع الحلقات الإدراكية السمعية وفق بنية DGCA الحالية."""

    def __init__(self):
        self.encoder = AudioEncoderV2()

    def process_audio(
        self,
        waveform: list[float] | np.ndarray,
        context: str | None = None,
        sample_rate_hz: int = 8000,
        stream_scope_id: str = "default_scope",
    ) -> list[SensoryEpisode]:
        """يحول الموجة الصوتية إلى حلقات إدراكية معيارية عبر تجميع الأحداث الزمنية السمعية."""
        temporal_ir = self.encoder.process_waveform_once(
            samples=waveform,
            sample_rate_hz=sample_rate_hz,
            channel_count=1,
            stream_scope_id=stream_scope_id,
        )

        if temporal_ir.status in ("NO_EVIDENCE", "UNSUPPORTED") or not temporal_ir.events:
            return []

        episodes = []
        for evt in temporal_ir.events:
            ephemeral_uid = f"inst:aud_{evt.stream_scope_id}_{evt.event_index}"
            signals: list[tuple[Literal["audio"], str]] = [("audio", ephemeral_uid)]
            for s_mod, s_val in evt.descriptors:
                signals.append(("audio", s_val))

            episodes.append(
                SensoryEpisode(
                    kind="simultaneous",
                    context=context,
                    signals=signals,
                    structural_weight=0.0,
                )
            )

        return episodes
