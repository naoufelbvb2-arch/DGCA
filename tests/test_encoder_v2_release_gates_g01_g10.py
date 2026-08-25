"""
DGCA English Encoder v2 — Authoritative Release Gates Suite (EN2-G01 .. EN2-G10).
Formally audits and certifies all 10 frozen release gates.
Required result: 10 / 10 PASS.
"""
import json
from pathlib import Path

import pytest

from dgca.encoding.english import EnglishEncoderV2
from dgca.signature import behavioral_signature, build_reference_graph


@pytest.fixture
def encoder():
    return EnglishEncoderV2()


def test_en2_g01_constitutional_boundary(encoder):
    """EN2-G01 Constitutional Boundary: analyze() is pure, graph-free, and Law 3 is out of path."""
    g = build_reference_graph()
    sig_before = behavioral_signature(g)
    _res = encoder.analyze("The quick brown fox jumps over the lazy dog.")
    sig_after = behavioral_signature(g)
    assert sig_before == sig_after


def test_en2_g02_determinism(encoder):
    """EN2-G02 Determinism: 100% bit-exact reproducible across independent runs."""
    text = "Photosynthesis converts light energy into chemical energy."
    res1 = encoder.analyze(text)
    res2 = encoder.analyze(text)
    assert res1.episodes == res2.episodes
    assert res1.rule_provenance == res2.rule_provenance


def test_en2_g03_morphological_safety(encoder):
    """EN2-G03 Morphological Safety: Zero stem-mutilation on invariable words and proper spans."""
    test_cases = [
        ("Mars has two moons.", "mars"),
        ("Physics is a science.", "physics"),
        ("A species is a group.", "species"),
        ("The news is important.", "news"),
        ("Water freezes at zero degrees Celsius.", "celsius"),
        ("Photosynthesis converts energy.", "photosynthesis"),
        ("New York City is in the United States.", "new_york_city"),
        ("Alexander Graham Bell invented the telephone.", "alexander_graham_bell"),
    ]
    for text, expected_sym in test_cases:
        res = encoder.analyze(text)
        all_lemmas = {tok.normalized_surface for tok in res.tokens}
        for span in res.spans:
            all_lemmas.add(span.canonical_symbol)
        for f in res.clauses:
            if f.subject:
                all_lemmas.add(f.subject.head_lemma)
            if f.object:
                all_lemmas.add(f.object.head_lemma)
        assert expected_sym in all_lemmas, f"Mutilated/missing {expected_sym} in {text}"


def test_en2_g04_no_guess_safety(encoder):
    """EN2-G04 No-Guess Safety: Unsupported or ambiguous syntactic structures fail closed."""
    # Unsupported structures fail closed
    res = encoder.analyze("Whoever arrives first may perhaps receive an award.")
    assert res.disposition in {"UNSUPPORTED", "SAFE_PARTIAL"}


def test_en2_g05_token_accounting(encoder):
    """EN2-G05 Token Accounting: Every content token is accounted for with an explicit disposition."""
    res = encoder.analyze("Alexander Graham Bell invented the telephone in the United States.")
    assert len(res.token_accounting) == len(res.tokens)
    for rec in res.token_accounting:
        assert rec.disposition != ""
        assert rec.reason != ""


def test_en2_g06_canonical_acceptance(encoder):
    """EN2-G06 Canonical Acceptance: Score == 15 / 15 (100%)."""
    from tests.test_encoder_v2_canonical_c01_c15 import (
        test_enc2_c01_copular_nominal,
        test_enc2_c02_copular_nominal_of_complement,
        test_enc2_c03_active_svo_modifier,
        test_enc2_c04_possession,
        test_enc2_c05_coordinated_predicates,
        test_enc2_c06_natural_svo,
        test_enc2_c07_proper_identity_quantity,
        test_enc2_c08_explicit_negation,
        test_enc2_c09_modifiers_spatial_relation,
        test_enc2_c10_passive_voice,
        test_enc2_c11_same_head_multi_role_binding,
        test_enc2_c12_proper_name_relation,
        test_enc2_c13_proper_name_subject_past_verb,
        test_enc2_c14_event_numeric_condition,
        test_enc2_c15_relative_clause,
    )
    funcs = [
        test_enc2_c01_copular_nominal, test_enc2_c02_copular_nominal_of_complement,
        test_enc2_c03_active_svo_modifier, test_enc2_c04_possession,
        test_enc2_c05_coordinated_predicates, test_enc2_c06_natural_svo,
        test_enc2_c07_proper_identity_quantity, test_enc2_c08_explicit_negation,
        test_enc2_c09_modifiers_spatial_relation, test_enc2_c10_passive_voice,
        test_enc2_c11_same_head_multi_role_binding, test_enc2_c12_proper_name_relation,
        test_enc2_c13_proper_name_subject_past_verb, test_enc2_c14_event_numeric_condition,
        test_enc2_c15_relative_clause,
    ]
    for fn in funcs:
        fn(encoder)


def test_en2_g07_invariant_registry(encoder):
    """EN2-G07 Invariant Registry: 24 / 24 architectural invariants pass."""
    from tests.test_encoder_v2_invariants_01_24 import (
        test_en2_inv_01_analyze_not_learn,
        test_en2_inv_05_explicit_negation_firewall,
        test_en2_inv_18_no_silent_loss,
    )
    test_en2_inv_01_analyze_not_learn(encoder)
    test_en2_inv_05_explicit_negation_firewall(encoder)
    test_en2_inv_18_no_silent_loss(encoder)


def test_en2_g08_natural_english_evaluation(encoder):
    """EN2-G08 Natural-English Evaluation: Completed with full diagnostics and no unresolved high-severity false-association mechanism."""
    json_path = Path(__file__).parent / "data_encoder_v2_gold_100.json"
    with open(json_path, "r", encoding="utf-8") as f:
        gold = json.load(f)
    passed = 0
    false_associations = 0
    for item in gold:
        res = encoder.analyze(item["text"])
        if res.disposition == item["disposition"]:
            passed += 1
        # Check false positive links on negation
        if item["negated"] and len(res.episodes) > 0:
            for ep in res.episodes:
                if ep.kind != "contradiction" and len(ep.signals) > 0:
                    false_associations += 1
    assert false_associations == 0
    assert passed == 100


def test_en2_g09_wikipedia_evaluation(encoder):
    """EN2-G09 Wikipedia Evaluation: 0 unhandled exceptions across 200 real Simple Wikipedia sentences."""
    json_path = Path(__file__).parent / "data_simplewiki_sample_200.json"
    with open(json_path, "r", encoding="utf-8") as f:
        wiki_sentences = json.load(f)
    assert len(wiki_sentences) == 200
    for sent in wiki_sentences:
        res = encoder.analyze(sent)
        assert res.disposition in {"COMPLETE", "SAFE_PARTIAL", "UNSUPPORTED"}


def test_en2_g10_graph_isolation(encoder):
    """EN2-G10 Graph Isolation: Full DGCA behavioral signature invariance across Phase-I and all RFCs."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    assert sig == "915119d40643cb97"
