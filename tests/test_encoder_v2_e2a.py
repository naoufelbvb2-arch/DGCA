"""
DGCA English Encoder v2 — Stage E2A Verification Suite.
Tests Layer 1 (Normalization) and Layer 2 (Tokenization).
"""
from dgca.encoding.english.normalize import normalize_text
from dgca.encoding.english.tokenize import tokenize, tokenize_normalized
from dgca.encoding.english.types import TokenKind


def test_e2a_unicode_and_quote_normalization():
    raw = '“The Earth’s orbit — says Dr. Smith — is 3.14.”'
    norm = normalize_text(raw)
    assert '"' in norm.normalized_text
    assert "'" in norm.normalized_text
    assert "-" in norm.normalized_text
    assert len(norm.norm_to_raw_offsets) == len(norm.normalized_text)


def test_e2a_source_offset_reconstructability():
    raw = 'Alexander Graham Bell invented the telephone in the U.S. in 1876.'
    norm = normalize_text(raw)
    tokens = tokenize_normalized(norm)
    for tok in tokens:
        # Exact character slice from raw input must match surface (or uncontracted base)
        raw_slice = raw[tok.start_offset : tok.end_offset]
        assert raw_slice == tok.surface, f"Offset mismatch: {raw_slice!r} != {tok.surface!r}"


def test_e2a_contractions():
    raw = "Birds don't swim, but eagles can't either."
    tokens = tokenize(raw)
    surfaces = [t.surface for t in tokens]
    [t.normalized_surface for t in tokens]
    assert "do" in surfaces
    assert "n't" in surfaces
    assert "can" in surfaces
    assert "n't" in surfaces
    # Verify clitic info
    neg_tokens = [t for t in tokens if t.clitic_info == "CONTRACTION_NEGATION"]
    assert len(neg_tokens) == 2


def test_e2a_possessives():
    raw = "The Earth's atmosphere surrounds Mars."
    tokens = tokenize(raw)
    surfaces = [t.surface for t in tokens]
    assert "Earth" in surfaces
    assert "'s" in surfaces
    assert "Mars" in surfaces
    pos_tok = [t for t in tokens if t.clitic_info == "POSSESSIVE"]
    assert len(pos_tok) == 1
    assert pos_tok[0].surface == "'s"


def test_e2a_decimal_numbers_and_initialisms():
    raw = "Water freezes at 0 degrees and pi is 3.14 in the U.S."
    tokens = tokenize(raw)
    num_tokens = [t for t in tokens if t.token_kind == TokenKind.NUMBER]
    init_tokens = [t for t in tokens if t.token_kind == TokenKind.INITIALISM]

    assert any(t.surface == "0" for t in num_tokens)
    assert any(t.surface == "3.14" for t in num_tokens)
    assert any(t.surface == "U.S." for t in init_tokens)


def test_e2a_lexical_preservation():
    raw = "Mars has species of physics news."
    tokens = tokenize(raw)
    surfaces = [t.surface for t in tokens]
    # No suffix stripping in tokenization!
    assert "Mars" in surfaces
    assert "species" in surfaces
    assert "physics" in surfaces
    assert "news" in surfaces


def test_e2a_deterministic_replay():
    raw = "The quick brown fox jumps over 10 lazy dogs in New York City."
    toks1 = tokenize(raw)
    toks2 = tokenize(raw)
    assert toks1 == toks2
