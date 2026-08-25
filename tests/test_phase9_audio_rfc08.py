"""
اختبارات المرحلة التاسعة — مُرمِّز الحاسة السمعية البيوفيزيائي والتأريض ثلاثي الحواس (Phase 9: RFC-08).

تغطي:
1. توزيع قنوات نموذج القوقعة (Lean CAR-FAC) وفق مقياس جرينوود للترددات (100Hz - 4000Hz).
2. تقويم الخلايا الشعرية وتخميد الضجيج المستمر بالتحكم التلقائي في الكسب ثنائي المراحل (2-Stage AGC).
3. الاستخلاص الحتمي للترددات الرنينية (Formants F1, F2) وكشف التصويت والجهر (Voicing).
4. تطبيق عقد الرأس أولاً (Head-first contract) لكافة إشارات الكيانات الصوتية.
5. إعفاء الكيانات الصوتية من القفل الدائم والموت الخلوي التام بعد التآكل المتسارع (inst:aud_* GC).
6. التأريض ثلاثي الحواس واللغات وانبثاق الرنين عبر الحواس (صوت -> نص ورؤية).
7. سقف ميزانية الحواس وحصر السمات الصوتية في سقف 3 سمات جوهرية (F1, F2, Pitch).
8. عدم الانحدار وثبات البصمة السلوكية المرجعية الحتمية c4b2549940a49789.
"""
import math
import random

from dgca import (
    AudioSensoryPipeline,
    CognitiveGraph,
    LeanCARFAC,
    deep_infer,
)
from dgca.signature import behavioral_signature, build_reference_graph


def _synthetic_tone(freq: float, duration: float = 0.10, fs: int = 8000) -> list[float]:
    n = int(duration * fs)
    return [math.sin(2.0 * math.pi * freq * i / fs) for i in range(n)]


def test_lean_carfac_filterbank_frequencies():
    """التحقق من تدرج وترتيب قنوات القوقعة الـ 16 وفق مقياس جرينوود للغشاء القاعدي."""
    carfac = LeanCARFAC(num_channels=16)
    freqs = carfac.frequencies

    assert len(freqs) == 16
    # الترددات تتناقص من القناة 0 (العليا) إلى القناة 15 (الدنيا)
    for i in range(len(freqs) - 1):
        assert freqs[i] >= freqs[i + 1]

    # التحقق من الحدود
    assert freqs[0] <= 4000.0
    assert freqs[-1] >= 100.0


def test_ihc_rectification_and_agc_compression():
    """التحقق من تقويم الخلايا الشعرية وتخميد الضجيج المستمر عبر AGC بمرحلتين."""
    carfac = LeanCARFAC()
    random.seed(42)
    long_noise = [random.uniform(-0.5, 0.5) for _ in range(2400)]  # 300ms @ 8kHz

    ch_outputs = carfac.process_waveform(long_noise)
    assert len(ch_outputs) == 16

    # التحقق من أن جميع الإشارات موجبة (تقويم نصف موجي v >= 0)
    for ch in ch_outputs:
        assert all(val >= 0.0 for val in ch)

    # التحقق من تخميد النصف الثاني مقارنة بالنصف الأول
    e_first = sum(sum(z * z for z in ch[:1200]) for ch in ch_outputs)
    e_second = sum(sum(z * z for z in ch[1200:]) for ch in ch_outputs)
    assert e_second < e_first


def test_audio_formant_extraction_deterministic():
    """التحقق من استخلاص الترددات الرنينية والجهر بدقة حتمية."""
    carfac = LeanCARFAC()
    # نغمة بتردد 300 هرتز (نطاق F1 المنخفض)
    tone_low = _synthetic_tone(300.0)
    feat_low = carfac.extract_features(tone_low)
    assert feat_low.is_voiced
    assert 8 <= feat_low.fmt1_band <= 15


def test_audio_head_first_contract():
    """التحقق من أن معرف الكيان الصوتي اللحظي inst:aud_* يقع في الموضع 0 في الإشارات دائماً."""
    pipeline = AudioSensoryPipeline()
    tone = _synthetic_tone(600.0)

    episodes = pipeline.process_audio(tone)
    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.signals[0][0] == "audio"
    assert ep.signals[0][1].startswith("inst:aud_")


def test_audio_instance_transient_gc():
    """التحقق من إعفاء الكيانات الصوتية من القفل الدائم والموت الخلوي التام بعد التآكل."""
    graph = CognitiveGraph()
    pipeline = AudioSensoryPipeline()
    tone = _synthetic_tone(800.0)

    episodes = pipeline.process_audio(tone)
    for ep in episodes:
        graph.observe(ep.signals, structural_weight=0.80)

    # التحقق من أن الروابط الصادرة من inst:aud_* ليس لها أرضية حماية
    for e in graph.edges.values():
        if "inst:aud_" in e.src or "inst:aud_" in e.dst:
            assert e.W_floor == 0.0
            assert not e.locked

    # إحالة الكيانات الصوتية العابرة للتقاعد عند انتهاء النطاق (Scope Retirement)
    graph.retire_transient_scope()

    active_aud = [nid for nid in graph.nodes if "inst:aud_" in nid]
    assert len(active_aud) == 0


def test_tri_modal_grounding_text_vision_audio():
    """التحقق من التأريض ثلاثي الحواس واللغات وانبثاق الرنين عبر الحواس (صوت -> نص ورؤية)."""
    graph = CognitiveGraph()
    for _ in range(3):
        graph.observe([("text", "apple"), ("vision", "vis:clr:red"), ("vision", "vis:shp:circle")], structural_weight=0.80)
        graph.observe([("text", "apple"), ("audio", "aud:fmt1:band_11"), ("audio", "aud:fmt2:band_5")], structural_weight=0.80)

    graph.tick()

    res = deep_infer(graph, seeds=["audio:aud:fmt1:band_11"], mode="simulation")
    ranked = dict(res.get("ranked", []))

    assert ranked.get("text:apple", 0.0) >= 0.15
    assert ranked.get("vision:vis:clr:red", 0.0) >= 0.10


def test_audio_modality_budget_clamping():
    """التحقق من حصر السمات الصوتية في سقف 3 سمات جوهرية (F1, F2, Pitch)."""
    pipeline = AudioSensoryPipeline()
    tone = _synthetic_tone(500.0)

    episodes = pipeline.process_audio(tone)
    signals = episodes[0].signals

    # الرأس (1) + السمات الصوتية الأساسية (3) = 4 إشارات
    aud_signals = [s for s in signals if s[0] == "audio"]
    assert len(aud_signals) == 4


def test_full_regression_and_signature():
    """التحقق من عدم الانحدار وثبات البصمة السلوكية المرجعية الحتمية 915119d40643cb97."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "915119d40643cb97"
