"""
DGCA English Encoder v2 — Stage E2F: Canonical Acceptance Suite (ENC2-C01 .. ENC2-C15).
Authoritative verification of the 15 canonical sentences from Section 11 of the specification.
Required result: 15 / 15 PASS.
"""
import pytest

from dgca.encoding.english import EnglishEncoderV2


@pytest.fixture
def encoder():
    return EnglishEncoderV2()


def test_enc2_c01_copular_nominal(encoder):
    """ENC2-C01 — Copular Nominal: 'A falcon is a bird.'"""
    res = encoder.analyze("A falcon is a bird.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 1
    ep = res.episodes[0]
    assert ep.kind == "simultaneous"
    assert ("text", "falcon") in ep.signals
    assert ("text", "bird") in ep.signals
    # No 'is' cognitive node
    assert not any(sym == "is" for _, sym in ep.signals)


def test_enc2_c02_copular_nominal_of_complement(encoder):
    """ENC2-C02 — Copular Nominal + Of Complement: 'A falcon is a bird of prey.'"""
    res = encoder.analyze("A falcon is a bird of prey.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 2

    ep_sim = next(e for e in res.episodes if e.kind == "simultaneous")
    assert ("text", "falcon") in ep_sim.signals
    assert ("text", "bird") in ep_sim.signals

    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [[("text", "bird")], [("text", "rel:of")], [("text", "prey")]]


def test_enc2_c03_active_svo_modifier(encoder):
    """ENC2-C03 — Active SVO + Modifier: 'Falcons hunt small animals.'"""
    res = encoder.analyze("Falcons hunt small animals.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 2

    ep_sim = next(e for e in res.episodes if e.kind == "simultaneous")
    assert ("text", "animal") in ep_sim.signals
    assert ("text", "small") in ep_sim.signals

    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [[("text", "falcon")], [("text", "hunt")], [("text", "animal")]]


def test_enc2_c04_possession(encoder):
    """ENC2-C04 — Possession: 'Birds have feathers.'"""
    res = encoder.analyze("Birds have feathers.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 1
    ep = res.episodes[0]
    assert ep.kind == "sequence"
    assert ep.steps == [[("text", "bird")], [("text", "have")], [("text", "feather")]]


def test_enc2_c05_coordinated_predicates(encoder):
    """ENC2-C05 — Coordinated Predicates: 'Birds have feathers and lay eggs.'"""
    res = encoder.analyze("Birds have feathers and lay eggs.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 2

    ep1, ep2 = res.episodes
    assert ep1.kind == "sequence"
    assert ep1.steps == [[("text", "bird")], [("text", "have")], [("text", "feather")]]

    assert ep2.kind == "sequence"
    assert ep2.steps == [[("text", "bird")], [("text", "lay")], [("text", "egg")]]

    # No 'and' cognitive node
    all_symbols = [s for e in res.episodes for step in e.steps for _, s in step]
    assert "and" not in all_symbols


def test_enc2_c06_natural_svo(encoder):
    """ENC2-C06 — Natural SVO: 'The Earth orbits the Sun.'"""
    res = encoder.analyze("The Earth orbits the Sun.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 1
    ep = res.episodes[0]
    assert ep.kind == "sequence"
    assert ep.steps == [[("text", "earth")], [("text", "orbit")], [("text", "sun")]]


def test_enc2_c07_proper_identity_quantity(encoder):
    """ENC2-C07 — Proper Identity + Quantity: 'Mars has two moons.'"""
    res = encoder.analyze("Mars has two moons.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 2

    ep_sim = next(e for e in res.episodes if e.kind == "simultaneous")
    syms = [s for _, s in ep_sim.signals]
    assert any(s.startswith("inst:moon:") for s in syms)
    assert "moon" in syms
    assert ("quantity", "2") in ep_sim.signals

    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps[0] == [("text", "mars")]
    assert ep_seq.steps[1] == [("text", "have")]
    assert ep_seq.steps[2][0][1].startswith("inst:moon:")
    # Mars MUST NOT become mar
    assert "mar" not in syms


def test_enc2_c08_explicit_negation(encoder):
    """ENC2-C08 — Explicit Negation: 'Mars is not a star.'"""
    res = encoder.analyze("Mars is not a star.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 1
    ep = res.episodes[0]
    assert ep.contradictions == [("text:mars", "text:star")]
    assert len(ep.signals) == 0
    # No positive mars + star episode; 'not' is not a cognitive node


def test_enc2_c09_modifiers_spatial_relation(encoder):
    """ENC2-C09 — Modifiers + Spatial Relation: 'The red apple is on the wooden table.'"""
    res = encoder.analyze("The red apple is on the wooden table.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 3

    # 1. simultaneous: apple, red
    ep_app = next(e for e in res.episodes if e.kind == "simultaneous" and ("text", "apple") in e.signals)
    assert ("text", "red") in ep_app.signals

    # 2. simultaneous: table, wooden
    ep_tbl = next(e for e in res.episodes if e.kind == "simultaneous" and ("text", "table") in e.signals)
    assert ("text", "wooden") in ep_tbl.signals

    # 3. sequence: apple -> rel:on -> table
    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [[("text", "apple")], [("text", "rel:on")], [("text", "table")]]


def test_enc2_c10_passive_voice(encoder):
    """ENC2-C10 — Passive Voice: 'The mouse was chased by the black cat.'"""
    res = encoder.analyze("The mouse was chased by the black cat.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 2

    # 1. simultaneous: cat, black
    ep_cat = next(e for e in res.episodes if e.kind == "simultaneous")
    assert ("text", "cat") in ep_cat.signals
    assert ("text", "black") in ep_cat.signals

    # 2. sequence: cat -> chase -> mouse
    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [[("text", "cat")], [("text", "chase")], [("text", "mouse")]]


def test_enc2_c11_same_head_multi_role_binding(encoder):
    """ENC2-C11 — Same-Head Multi-Role Binding: 'Photosynthesis converts light energy into chemical energy.'"""
    res = encoder.analyze("Photosynthesis converts light energy into chemical energy.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 3

    sim_eps = [e for e in res.episodes if e.kind == "simultaneous"]
    assert len(sim_eps) == 2
    # Check light energy
    ep_light = next(e for e in sim_eps if any(s == "light" for _, s in e.signals))
    inst_light = next(s for _, s in ep_light.signals if s.startswith("inst:energy:"))

    # Check chemical energy
    ep_chem = next(e for e in sim_eps if any(s == "chemical" for _, s in e.signals))
    inst_chem = next(s for _, s in ep_chem.signals if s.startswith("inst:energy:"))

    assert inst_light != inst_chem

    # sequence: photosynthesis -> convert -> inst:energy:A -> rel:into -> inst:energy:B
    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [
        [("text", "photosynthesis")],
        [("text", "convert")],
        [("text", inst_light)],
        [("text", "rel:into")],
        [("text", inst_chem)],
    ]


def test_enc2_c12_proper_name_relation(encoder):
    """ENC2-C12 — Proper-Name Relation: 'New York City is in the United States.'"""
    res = encoder.analyze("New York City is in the United States.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 1
    ep = res.episodes[0]
    assert ep.kind == "sequence"
    assert ep.steps == [[("text", "new_york_city")], [("text", "rel:in")], [("text", "united_states")]]


def test_enc2_c13_proper_name_subject_past_verb(encoder):
    """ENC2-C13 — Proper-Name Subject + Past Verb: 'Alexander Graham Bell invented the telephone.'"""
    res = encoder.analyze("Alexander Graham Bell invented the telephone.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 1
    ep = res.episodes[0]
    assert ep.kind == "sequence"
    assert ep.steps == [[("text", "alexander_graham_bell")], [("text", "invent")], [("text", "telephone")]]


def test_enc2_c14_event_numeric_condition(encoder):
    """ENC2-C14 — Event + Numeric Condition: 'Water freezes at zero degrees Celsius.'"""
    res = encoder.analyze("Water freezes at zero degrees Celsius.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 2

    ep_sim = next(e for e in res.episodes if e.kind == "simultaneous")
    syms = [s for _, s in ep_sim.signals]
    assert any(s.startswith("inst:degree:") for s in syms)
    assert "degree" in syms
    assert "celsius" in syms
    assert ("quantity", "0") in ep_sim.signals

    inst_deg = next(s for _, s in ep_sim.signals if s.startswith("inst:degree:"))
    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [[("text", "water")], [("text", "freeze")], [("text", "rel:at")], [("text", inst_deg)]]


def test_enc2_c15_relative_clause(encoder):
    """ENC2-C15 — Relative Clause: 'A lion is a large cat that lives in Africa.'"""
    res = encoder.analyze("A lion is a large cat that lives in Africa.")
    assert res.disposition == "COMPLETE"
    assert len(res.episodes) == 3

    # 1. simultaneous: cat, large
    ep_large = next(e for e in res.episodes if e.kind == "simultaneous" and any(s == "large" for _, s in e.signals))
    assert ("text", "cat") in ep_large.signals

    # 2. simultaneous: lion, cat
    ep_lion = next(e for e in res.episodes if e.kind == "simultaneous" and any(s == "lion" for _, s in e.signals))
    assert ("text", "cat") in ep_lion.signals

    # 3. sequence: cat -> live -> rel:in -> africa
    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [[("text", "cat")], [("text", "live")], [("text", "rel:in")], [("text", "africa")]]
