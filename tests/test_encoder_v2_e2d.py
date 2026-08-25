"""
DGCA English Encoder v2 — Stage E2D Verification Suite.
Tests Layer 6 (Syntactic Role Parsing) and Layer 7 (Relation & Binding Resolution).
"""
from dgca.encoding.english.clauses import segment_and_parse_clauses
from dgca.encoding.english.relations import resolve_clause_bindings
from dgca.encoding.english.tokenize import tokenize


def test_e2d_active_svo_and_modifiers():
    text = "Falcons hunt small animals."
    tokens = tokenize(text)
    frames = segment_and_parse_clauses(tokens)
    assert len(frames) == 1
    f = frames[0]
    assert f.subject.head_lemma == "falcon"
    assert f.predicate == "hunt"
    assert f.object.head_lemma == "animal"
    assert f.object.modifiers == ("small",)


def test_e2d_passive_voice_agent_normalization():
    """EN2-INV-13: Normalized agent in subject position, patient in object position."""
    text = "The mouse was chased by the black cat."
    tokens = tokenize(text)
    frames = segment_and_parse_clauses(tokens)
    assert len(frames) == 1
    f = frames[0]
    assert f.voice == "PASSIVE"
    assert f.subject.head_lemma == "cat"
    assert f.subject.modifiers == ("black",)
    assert f.predicate == "chase"
    assert f.object.head_lemma == "mouse"


def test_e2d_explicit_negation():
    text = "Mars is not a star."
    tokens = tokenize(text)
    frames = segment_and_parse_clauses(tokens)
    assert len(frames) == 1
    f = frames[0]
    assert f.subject.head_lemma == "mars"
    assert f.object.head_lemma == "star"
    assert f.negated is True


def test_e2d_quantity_binding():
    """EN2-INV-15: Quantity binds deterministically to the intended noun phrase."""
    text = "Mars has two moons."
    tokens = tokenize(text)
    frames = segment_and_parse_clauses(tokens)
    assert len(frames) == 1
    f = resolve_clause_bindings(frames[0])
    assert f.subject.head_lemma == "mars"
    assert f.predicate == "have"
    assert f.object.head_lemma == "moon"
    assert f.object.quantity == "2"
    assert f.object.instance_binding.startswith("inst:moon:")


def test_e2d_same_head_multi_role_binding():
    """EN2-INV-16: Repeated same-head roles are separated into deterministic instances."""
    text = "Photosynthesis converts light energy into chemical energy."
    tokens = tokenize(text)
    frames = segment_and_parse_clauses(tokens)
    assert len(frames) == 1
    f = resolve_clause_bindings(frames[0])
    assert f.subject.head_lemma == "photosynthesis"
    assert f.predicate == "convert"
    assert f.object.head_lemma == "energy"
    assert f.object.modifiers == ("light",)
    assert f.object.instance_binding is not None

    prep_rel = f.prepositional_relations[0]
    assert prep_rel[0] == "rel:into"
    pobj = prep_rel[1]
    assert pobj.head_lemma == "energy"
    assert pobj.modifiers == ("chemical",)
    assert pobj.instance_binding is not None
    # Must have distinct instance IDs!
    assert f.object.instance_binding != pobj.instance_binding
