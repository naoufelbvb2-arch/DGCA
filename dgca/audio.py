"""
مُرمِّز الحاسة السمعية البيوفيزيائي والتأريض ثلاثي الحواس (RFC-08: Auditory Modality & Lean CAR-FAC Grounding).

المبدأ الحاكم:
«السمع ليس شبكة عصبية عمياء، بل محاكاة بيوفيزيائية لميكانيكا القوقعة وتدفق السوائل؛
تُفكك الموجة الصوتية إلى قنوات رنين غير متناظرة وضغط ديناميكي سريع لتوليد بصمات صوتية قطعية
تندمج مع الرؤية واللغة حول مراكز مفاهيم موحدة».
"""
import math
from dataclasses import dataclass
from typing import Literal

from .encoder import SensoryEpisode


@dataclass
class AudioFeatures:
    """المعالم الصوتية المستخلصة من نموذج القوقعة الحسابي."""

    fmt1_band: int  # 8 to 15 (التردد الرنيني الأول المنخفض-المتوسط)
    fmt2_band: int  # 2 to 7 (التردد الرنيني الثاني المتوسط-المرتفع)
    is_voiced: bool  # هل الإشارة نغمية/مجهورة (F0) أم ضجيج غير مصوت
    has_onset: bool  # هل تحتوي على بداية حادة / انفجار صوتي
    energy: float  # متوسط الطاقة الجذرية RMS


@dataclass
class AudioSegment:
    """مقطع صوتي مُرمَّز ومُعرَّف."""

    uid: str
    features: AudioFeatures
    paired_text: str | None = None


class LeanCARFAC:
    """محاكي القوقعة الفيزيائي الخفيف (Cascade of Asymmetric Resonators with Fast-Acting Compression)."""

    def __init__(self, num_channels: int = 16):
        self.num_channels = num_channels
        self.frequencies = self._compute_greenwood_frequencies(num_channels)

    def _compute_greenwood_frequencies(self, n_channels: int) -> list[float]:
        """حساب الترددات المميزة للقنوات وفق مقياس جرينوود للغشاء القاعدي (100Hz - 4000Hz)."""
        freqs = []
        for k in range(n_channels):
            # مقياس جرينوود لوغاريتمي متدرج من 4000 هرتز إلى 100 هرتز
            ratio = (n_channels - 1 - k) / max(1, n_channels - 1)
            # f_c = 165.4 * (10^(1.40 * ratio) - 0.88)
            f_c = 165.4 * (math.pow(10.0, 1.40 * ratio) - 0.88)
            f_c = max(100.0, min(4000.0, f_c))
            freqs.append(f_c)
        return freqs

    def _design_resonator(self, fc: float, fs: float) -> tuple[float, float, float, float, float]:
        """تصميم مرشح رقمي ثنائي القطب (2-Pole IIR Resonator) لكل قناة."""
        w0 = 2.0 * math.pi * fc / fs
        bw = max(60.0, fc / 4.5)
        q = fc / bw
        alpha = math.sin(w0) / (2.0 * q)
        b0 = alpha / (1.0 + alpha)
        b1 = 0.0
        b2 = -b0
        a1 = -2.0 * math.cos(w0) / (1.0 + alpha)
        a2 = (1.0 - alpha) / (1.0 + alpha)
        return b0, b1, b2, a1, a2

    def process_waveform(
        self, waveform: list[float], sample_rate: int = 8000
    ) -> list[list[float]]:
        """تمرير الموجة الصوتية عبر مصفوفة الرنين وتطبيق تقويم الخلايا الشعرية والضغط التلقائي."""
        if not waveform:
            return [[0.0] * 16]

        fs = float(sample_rate)

        # معاملات التكيف السريع والبطيء للتحكم التلقائي في الكسب (2-Stage AGC)
        lam_fast = math.exp(-1.0 / max(1.0, fs * 0.005))
        lam_slow = math.exp(-1.0 / max(1.0, fs * 0.100))

        channel_outputs: list[list[float]] = []

        for fc in self.frequencies:
            b0, b1, b2, a1, a2 = self._design_resonator(fc, fs)
            y_prev1, y_prev2 = 0.0, 0.0
            x_prev1, x_prev2 = 0.0, 0.0
            env_fast, env_slow = 0.0, 0.0

            ch_out: list[float] = []

            for x in waveform:
                # 1. ترشيح الرنين (CAR)
                y = b0 * x + b1 * x_prev1 + b2 * x_prev2 - a1 * y_prev1 - a2 * y_prev2
                x_prev2, x_prev1 = x_prev1, x
                y_prev2, y_prev1 = y_prev1, y

                # 2. تقويم وتنعيم الخلايا الشعرية الداخلية (IHC)
                ihc_v = math.pow(max(0.0, y), 3)

                # 3. التحكم التلقائي في الكسب بمرحلتين (2-Stage Multi-Rate AGC)
                env_fast = lam_fast * env_fast + (1.0 - lam_fast) * ihc_v
                env_slow = lam_slow * env_slow + (1.0 - lam_slow) * ihc_v
                # تخميد الضجيج المستمر مع الاستجابة السريعة للنبضات
                gain = 1.0 / (1.0 + 0.6 * env_fast + 2.5 * env_slow)
                z = ihc_v * gain
                ch_out.append(z)

            channel_outputs.append(ch_out)

        return channel_outputs

    def extract_features(
        self, waveform: list[float], sample_rate: int = 8000
    ) -> AudioFeatures:
        """استخلاص المعالم الصوتية الأساسية: الترددات الرنينية (F1, F2)، والجهر (F0)، ونبضات البداية."""
        if not waveform:
            return AudioFeatures(fmt1_band=11, fmt2_band=5, is_voiced=False, has_onset=False, energy=0.0)

        # حساب الطاقة الإجمالية
        rms = math.sqrt(sum(x * x for x in waveform) / max(1, len(waveform)))

        # تحليل القنوات عبر نموذج القوقعة
        ch_outputs = self.process_waveform(waveform, sample_rate=sample_rate)

        channel_energies = [sum(z * z for z in ch) for ch in ch_outputs]

        # استخراج F1 (أعلى طاقة في القنوات المنخفضة 8..15)
        f1_energies = [(channel_energies[k], k) for k in range(8, min(16, len(channel_energies)))]
        fmt1_band = max(f1_energies, key=lambda p: p[0])[1] if f1_energies else 11

        # استخراج F2 (أعلى طاقة في القنوات المتوسطة-المرتفعة 2..7)
        f2_energies = [(channel_energies[k], k) for k in range(2, min(8, len(channel_energies)))]
        fmt2_band = max(f2_energies, key=lambda p: p[0])[1] if f2_energies else 5

        # كشف التصويت والجهر عبر الترابط الذاتي للموجة (F0 Voicing Autocorrelation)
        is_voiced = self._detect_voicing(waveform, sample_rate)

        # كشف نبضات البداية (Onset Detection)
        has_onset = self._detect_onset(waveform)

        return AudioFeatures(
            fmt1_band=fmt1_band,
            fmt2_band=fmt2_band,
            is_voiced=is_voiced,
            has_onset=has_onset,
            energy=rms,
        )

    def _detect_voicing(self, waveform: list[float], sample_rate: int) -> bool:
        """كشف التصويت والجهر بالنبرة عبر الترابط الذاتي قصير المدى (80Hz - 400Hz)."""
        n = len(waveform)
        if n < 50:
            return False

        min_lag = max(1, int(sample_rate / 400))  # 400 Hz
        max_lag = min(n - 1, int(sample_rate / 80))   # 80 Hz

        energy = sum(x * x for x in waveform)
        if energy < 1e-6:
            return False

        best_autocorr = 0.0
        for lag in range(min_lag, max_lag + 1):
            corr = sum(waveform[i] * waveform[i + lag] for i in range(n - lag))
            norm_corr = corr / energy
            best_autocorr = max(best_autocorr, norm_corr)

        return best_autocorr >= 0.35

    def _detect_onset(self, waveform: list[float]) -> bool:
        """كشف البدايات الحادة والانفجارات الصوتية في مطلع الإشارة."""
        if len(waveform) < 20:
            return False
        first_quarter = waveform[: max(5, len(waveform) // 4)]
        mean_sq_total = sum(x * x for x in waveform) / len(waveform)
        max_peak = max(x * x for x in first_quarter)
        return max_peak >= (mean_sq_total * 2.5 + 1e-5)


class AudioSensoryPipeline:
    """مُرمِّز الحاسة السمعية وتوليد الحلقات الإدراكية والتأريض ثلاثي الحواس."""

    def __init__(self):
        self.carfac = LeanCARFAC()
        self._uid_counter = 0

    def process_audio(
        self,
        waveform: list[float],
        paired_text: str | None = None,
        context: str | None = None,
        sample_rate: int = 8000,
    ) -> list[SensoryEpisode]:
        """يحول الموجة الصوتية إلى حلقات إدراكية معيارية تطبق عقد الرأس أولاً وسقف ميزانية الحواس."""
        self._uid_counter += 1
        ephemeral_uid = f"inst:aud_{self._uid_counter}"

        features = self.carfac.extract_features(waveform, sample_rate=sample_rate)

        # تطبيق عقد الرأس أولاً: المعرف اللحظي في الموضع 0 متبوعاً بأهم 3 سمات صوتية جوهرية
        signals: list[tuple[Literal["audio", "text"], str]] = [
            ("audio", ephemeral_uid),
            ("audio", f"aud:fmt1:band_{features.fmt1_band}"),
            ("audio", f"aud:fmt2:band_{features.fmt2_band}"),
            ("audio", "aud:pitch:voiced" if features.is_voiced else "aud:pitch:unvoiced"),
        ]

        if paired_text:
            signals.append(("text", paired_text))

        # تعزيز البدايات الصوتية القوية بالبروز البنيوي الفطري (0.80)
        struct_weight = 0.80 if (features.is_voiced and features.has_onset) else 0.0

        return [
            SensoryEpisode(
                kind="simultaneous",
                context=context,
                signals=signals,
                structural_weight=struct_weight,
            )
        ]
