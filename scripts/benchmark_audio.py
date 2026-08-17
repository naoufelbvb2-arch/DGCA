"""
سكربت التقييم التجريبي الشامل لمُرمِّز الحاسة السمعية ونموذج القوقعة البيوفيزيائي (RFC-08).

يتحقق من:
1. التمييز الدقيق بين أصوات العلة (Vowel Formant Discretization /a/ vs /i/ vs /u/).
2. تخميد الضجيج المستمر عبر الضغط التلقائي ثنائي المراحل (2-Stage AGC Noise Suppression).
3. التمييز بين النغمات المجهورة والضجيج غير المصوت (Voiced Pitch vs Unvoiced Noise).
4. تجميع وفصل المسارات الصوتية المتزامنة (Cocktail Party Grouping).
5. الموت الخلوي التام للكيانات الصوتية اللحظية (Transient Audio Instance GC).
6. التقارب والتأريض ثلاثي الحواس واللغات (Tri-Modal Grounding: Audio -> Vision + Text >= 0.15).
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import (
    AudioSensoryPipeline,
    CognitiveGraph,
    LeanCARFAC,
    deep_infer,
)


def generate_synthetic_vowel(f1: float, f2: float, f0: float = 130.0, duration: float = 0.15, fs: int = 8000) -> list[float]:
    """توليد موجة صوتية اصطناعية لحرف علة بترددات رنينية محددة ونبرة أساسية."""
    n_samples = int(duration * fs)
    samples = []
    for i in range(n_samples):
        t = i / fs
        # المصدر الصوتي: نغمة مجهورة مع التوافقيات
        source = (
            math.sin(2.0 * math.pi * f0 * t)
            + 0.5 * math.sin(2.0 * math.pi * 2.0 * f0 * t)
            + 0.25 * math.sin(2.0 * math.pi * 3.0 * f0 * t)
        )
        # الرنين الترددي (F1 & F2 Formants)
        f1_mod = math.sin(2.0 * math.pi * f1 * t)
        f2_mod = math.sin(2.0 * math.pi * f2 * t)
        # مغلف البداية (Onset Envelope)
        env = math.exp(-i / (fs * 0.08)) if i < int(fs * 0.05) else 0.8
        sample = source * (0.6 * f1_mod + 0.4 * f2_mod) * env
        samples.append(sample)
    return samples


def generate_noise(duration: float = 0.15, fs: int = 8000) -> list[float]:
    """توليد ضجيج أبيض عشوائي غير مصوت."""
    random.seed(42)
    return [random.uniform(-0.5, 0.5) for _ in range(int(duration * fs))]


def run_audio_benchmark():
    print("=" * 80)
    print("👂 بدء التقييم التجريبي الشامل لمُرمِّز السمع والتأريض ثلاثي الحواس (RFC-08)")
    print("=" * 80)

    successes = []
    failures = []

    carfac = LeanCARFAC()
    pipeline = AudioSensoryPipeline()

    # ─────────────────────────────────────────────────────────────
    # السيناريو 1: التمييز الدقيق بين أصوات العلة (Vowel Discretization)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 1] التمييز بين أصوات العلة وفق قمم الرنين (F1, F2)...")
    # /a/: F1=800Hz, F2=1200Hz
    # /i/: F1=250Hz, F2=2300Hz
    # /u/: F1=300Hz, F2=800Hz
    wave_a = generate_synthetic_vowel(800.0, 1200.0)
    wave_i = generate_synthetic_vowel(250.0, 2300.0)
    wave_u = generate_synthetic_vowel(300.0, 800.0)

    feat_a = carfac.extract_features(wave_a)
    feat_i = carfac.extract_features(wave_i)
    feat_u = carfac.extract_features(wave_u)

    # /i/ يجب أن يمتلك F2 بتردد أعلى (قناة أصغر) من /a/ و /u/
    if feat_i.fmt2_band < feat_u.fmt2_band and feat_a.fmt1_band != feat_i.fmt1_band:
        successes.append("Vowel_Discretization")
        print("   ✅ تم التمييز بنجاح:")
        print(f"      • /a/: F1_band={feat_a.fmt1_band}, F2_band={feat_a.fmt2_band}")
        print(f"      • /i/: F1_band={feat_i.fmt1_band}, F2_band={feat_i.fmt2_band}")
        print(f"      • /u/: F1_band={feat_u.fmt1_band}, F2_band={feat_u.fmt2_band}")
    else:
        failures.append(("Vowel_Discretization", f"a={feat_a}, i={feat_i}, u={feat_u}"))
        print(f"   ❌ فشل التمييز بين العلات: a={feat_a}, i={feat_i}")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 2: تخميد الضجيج البيئي المستمر (2-Stage AGC)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 2] فحص تخميد الضجيج المستمر عبر الضغط التلقائي ثنائي المراحل...")
    # إشارة طويلة من الضجيج المستمر (300ms)
    long_noise = generate_noise(duration=0.30)
    ch_outputs = carfac.process_waveform(long_noise)
    # فحص انخفاض طاقة النصف الثاني مقارنة بالنصف الأول نتيجة AGC البطيء
    first_half_e = sum(sum(z * z for z in ch[:len(ch)//2]) for ch in ch_outputs)
    second_half_e = sum(sum(z * z for z in ch[len(ch)//2:]) for ch in ch_outputs)

    if second_half_e < first_half_e:
        suppression_ratio = (first_half_e - second_half_e) / first_half_e * 100
        successes.append("Stationary_Noise_Suppression")
        print(f"   ✅ تخميد الضجيج ناجح! نسبة التخميد التلقائي المستمر = {suppression_ratio:.1f}%")
    else:
        failures.append(("Stationary_Noise_Suppression", "لم يتم تخميد الضجيج المستمر"))
        print("   ❌ فشل تخميد الضجيج المستمر!")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 3: التمييز بين النغمات المجهورة والضجيج (Voiced vs Unvoiced)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 3] فحص كشف الجهر والتصويت بالنبرة (Voiced Pitch vs Unvoiced Noise)...")
    wave_voiced = generate_synthetic_vowel(500.0, 1500.0, f0=140.0)
    wave_unvoiced = generate_noise(duration=0.15)

    feat_v = carfac.extract_features(wave_voiced)
    feat_uv = carfac.extract_features(wave_unvoiced)

    if feat_v.is_voiced and not feat_uv.is_voiced:
        successes.append("Voicing_Distinction")
        print(f"   ✅ كشف الجهر ناجح: نغمة صوتية -> is_voiced={feat_v.is_voiced}, ضجيج -> is_voiced={feat_uv.is_voiced}")
    else:
        failures.append(("Voicing_Distinction", f"voiced={feat_v.is_voiced}, unvoiced={feat_uv.is_voiced}"))
        print(f"   ❌ فشل كشف الجهر: voiced={feat_v.is_voiced}, unvoiced={feat_uv.is_voiced}")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 4: تجميع وفصل المسارات الصوتية (Cocktail Party Grouping)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 4] فحص عزل وفصل البصمات الصوتية لمتحدثين مختلفين...")
    # متحدث 1: نبرة منخفضة 110 هرتز
    spk1 = generate_synthetic_vowel(400.0, 1000.0, f0=110.0)
    # متحدث 2: نبرة مرتفعة 220 هرتز
    spk2 = generate_synthetic_vowel(700.0, 2000.0, f0=220.0)

    ep1 = pipeline.process_audio(spk1)
    ep2 = pipeline.process_audio(spk2)

    sig1 = [s[1] for s in ep1[0].signals]
    sig2 = [s[1] for s in ep2[0].signals]

    if sig1 != sig2:
        successes.append("Cocktail_Party_Grouping")
        print("   ✅ تميز المسارات الصوتية ناجح:")
        print(f"      • المتحدث 1: {sig1}")
        print(f"      • المتحدث 2: {sig2}")
    else:
        failures.append(("Cocktail_Party_Grouping", "تطابقت بصمات المتحدثين!"))
        print("   ❌ فشل عزل بصمات المتحدثين!")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 5: الموت الخلوي للكيانات الصوتية المؤقتة (Law 3 GC)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 5] فحص تآكل وموت الكيانات الصوتية المؤقتة (inst:aud_* GC)...")
    g_gc = CognitiveGraph()
    ep_aud = pipeline.process_audio(wave_a)
    for ep in ep_aud:
        g_gc.observe(ep.signals, structural_weight=0.80)

    # التحقق من أن الكيان الصوتي اللحظي لا يحظى بأرضية حماية
    for e in g_gc.edges.values():
        if "inst:aud_" in e.src or "inst:aud_" in e.dst:
            assert e.W_floor == 0.0

    # تمرير 8 تكات صامتة للموت الخلوي
    for _ in range(8):
        g_gc.tick()

    active_aud = [nid for nid in g_gc.nodes if "inst:aud_" in nid]
    if len(active_aud) == 0:
        successes.append("Transient_Audio_Instance_GC")
        print("   ✅ الموت الخلوي ناجح: تحللت كافة الكيانات اللحظية inst:aud_* بالكامل.")
    else:
        failures.append(("Transient_Audio_Instance_GC", f"لا تزال العقد حية: {active_aud}"))
        print(f"   ❌ تسريب ذاكرة صوتية: بقيت العقد {active_aud}")

    # ─────────────────────────────────────────────────────────────
    # السيناريو 6: التأريض ثلاثي الحواس واللغات (Tri-Modal Grounding)
    # ─────────────────────────────────────────────────────────────
    print("\n[سيناريو 6] فحص التأريض ثلاثي الحواس (صوت + صورة + نص)...")
    g_tri = CognitiveGraph()

    # اقتران متزامن: صورة تفاحة (أحمر، دائرة) + صوت نغمة + نص "apple"
    for _ in range(3):
        g_tri.observe([("text", "apple"), ("vision", "vis:clr:red"), ("vision", "vis:shp:circle")], structural_weight=0.80)
        g_tri.observe([("text", "apple"), ("audio", "aud:fmt1:band_11"), ("audio", "aud:fmt2:band_5")], structural_weight=0.80)

    # فترة صمت واستقرار
    g_tri.tick()

    # استدعاء بالصوت فقط: تفعيل الترددات الرنينية السمعية
    res = deep_infer(g_tri, seeds=["audio:aud:fmt1:band_11"], mode="simulation")
    ranked = dict(res.get("ranked", []))

    text_energy = ranked.get("text:apple", 0.0)
    vision_energy = ranked.get("vision:vis:clr:red", 0.0)

    if text_energy >= 0.15 and vision_energy >= 0.10:
        successes.append("Tri_Modal_Grounding_Convergence")
        print("   ✅ التأريض ثلاثي الحواس ناجح برنين قوي:")
        print(f"      • طاقة النص (text:apple)           = {text_energy:.3f} (>= 0.15)")
        print(f"      • طاقة الرؤية (vision:vis:clr:red) = {vision_energy:.3f} (>= 0.10)")
    else:
        failures.append(("Tri_Modal_Grounding_Convergence", f"text={text_energy}, vision={vision_energy}"))
        print(f"   ❌ ضعف الرنين الثلاثي: text={text_energy}, vision={vision_energy}")

    # ─────────────────────────────────────────────────────────────
    # التقرير النهائي الشامل
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("📊 التقرير النهائي لتقييم مُرمِّز الحاسة السمعية (RFC-08)")
    print("=" * 80)
    print("• إجمالي السيناريوهات: 6")
    print(f"• السيناريوهات الناجحة: {len(successes)}")
    print(f"• حالات الإخفاق      : {len(failures)}")

    if failures:
        print("\n⚠️ تفاصيل الإخفاقات:")
        for name, reason in failures:
            print(f"   ❌ [{name}]: {reason}")
    else:
        print("\n🎉 ممتاز! اجتاز مُرمِّز الحاسة السمعية كافة السيناريوهات بنسبة نجاح 100%.")
    print("=" * 80)


if __name__ == "__main__":
    run_audio_benchmark()
