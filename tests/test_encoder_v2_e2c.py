"""
DGCA English Encoder v2 — Stage E2C Verification Suite.
Tests Layer 5 (Clause Segmentation) and Layer 6 (Noun-Phrase Parsing).
"""
from dgca.encoding.english.clauses import segment_and_parse_clauses
from dgca.encoding.english.noun_phrases import parse_noun_phrase
from dgca.encoding.english.spans import detect_protected_spans
from dgca.encoding.english.tokenize import tokenize


def test_e2c_noun_phrase_modifiers_and_quantities():
    tokens = tokenize("The two red apples")
    np_view, consumed = parse_noun_phrase(tokens)
    assert np_view is not None
    assert np_view.determiner == "the"
    assert np_view.quantity == "2"
    assert np_view.modifiers == ("red",)
    assert np_view.head_lemma == "apple"
    assert consumed == len(tokens)


def test_e2c_noun_phrase_protected_span():
    text = "The United States is large."
    tokens = tokenize(text)
    spans = detect_protected_spans(tokens)
    np_view, _consumed = parse_noun_phrase(tokens, spans)
    assert np_view is not None
    assert np_view.determiner == "the"
    assert np_view.head_lemma == "united_states"
    assert np_view.protected_span is not None


def test_e2c_coordinated_predicates():
    """EN2-INV-14: Distinguishes coordinated predicates from flat whole-sentence cliques."""
    text = "Birds have feathers and lay eggs."
    tokens = tokenize(text)
    frames = segment_and_parse_clauses(tokens)
    assert len(frames) == 2

    # Frame 1: birds have feathers
    f1 = frames[0]
    assert f1.subject.head_lemma == "bird"
    assert f1.predicate == "have"
    assert f1.object.head_lemma == "feather"

    # Frame 2: (birds) lay eggs with inherited subject
    f2 = frames[1]
    assert f2.subject.head_lemma == "bird"
    assert f2.predicate == "lay"
    assert f2.object.head_lemma == "egg"
    assert f2.inherited_subject_ref == "bird"
    assert "ENC2-R-COORD-PRED" in f2.rule_provenance


def test_e2c_fail_closed_on_unsupported_syntax():
    """EN2-INV-19: Unsupported syntax fails closed without guessing semantic relations."""
    text = "Although whereas quickly running very fast."
    tokens = tokenize(text)
    frames = segment_and_parse_clauses(tokens)
    # Must fail closed: no false SVO invented!
    assert len(frames) == 0
