"""
DGCA English Encoder v2 — Stage E2B Verification Suite.
Tests Layer 3 (Morphology) and Layer 4 (Span Protection).
"""
from dgca.encoding.english.morphology import classify_morphology, lemmatize_noun, lemmatize_verb
from dgca.encoding.english.spans import detect_protected_spans
from dgca.encoding.english.tokenize import tokenize


def test_e2b_invariable_and_proper_nouns_preserved():
    """EN2-INV-08: Invariable singular nouns ending in -s must never be suffix-stripped."""
    for word in ("Mars", "physics", "species", "news", "mathematics", "series", "Celsius", "photosynthesis"):
        tok = tokenize(word)[0]
        mf = classify_morphology(tok)
        assert mf.lemma == word.lower(), f"Corrupted lemma for {word}: {mf.lemma}"
        assert mf.is_plural is False


def test_e2b_regular_plurals():
    plurals = {
        "birds": "bird", "animals": "animal", "moons": "moon",
        "feathers": "feather", "eggs": "egg", "lions": "lion",
        "falcons": "falcon", "tables": "table", "cats": "cat",
        "dogs": "dog", "degrees": "degree", "trees": "tree",
    }
    for plural_form, expected_sing in plurals.items():
        lemma, is_p = lemmatize_noun(plural_form)
        assert lemma == expected_sing, f"Expected {expected_sing}, got {lemma}"
        assert is_p is True


def test_e2b_irregular_plurals():
    irregulars = {
        "mice": "mouse", "children": "child", "men": "man",
        "women": "woman", "feet": "foot", "teeth": "tooth",
    }
    for irr_form, expected_sing in irregulars.items():
        lemma, is_p = lemmatize_noun(irr_form)
        assert lemma == expected_sing
        assert is_p is True


def test_e2b_open_class_regular_verbs():
    """EN2-INV-07: General conservative morphology handles regular verbs without finite lists."""
    regular_verbs = {
        "invented": "invent", "chased": "chase", "converted": "convert",
        "orbits": "orbit", "hunts": "hunt", "freezes": "freeze",
        "lived": "live", "lives": "live", "created": "create",
    }
    for v_surf, expected_lemma in regular_verbs.items():
        lemma, _is_past, _is_3s = lemmatize_verb(v_surf)
        assert lemma == expected_lemma, f"Expected {expected_lemma}, got {lemma} for {v_surf}"


def test_e2b_proper_name_span_protection():
    """EN2-INV-09: Multi-token proper names are protected as unified identities."""
    cases = [
        ("New York City is large.", "new_york_city"),
        ("The United States has fifty states.", "united_states"),
        ("Alexander Graham Bell invented the telephone.", "alexander_graham_bell"),
    ]
    for text, expected_sym in cases:
        tokens = tokenize(text)
        spans = detect_protected_spans(tokens)
        symbols = [s.canonical_symbol for s in spans]
        assert expected_sym in symbols, f"Missing {expected_sym} in {symbols}"


def test_e2b_adversarial_span_false_merger():
    """Adversarial check: Sentence-initial capitalized subject + verb must not merge into a span."""
    text = "Falcons hunt small animals."
    tokens = tokenize(text)
    spans = detect_protected_spans(tokens)
    symbols = [s.canonical_symbol for s in spans]
    assert "falcons_hunt" not in symbols
