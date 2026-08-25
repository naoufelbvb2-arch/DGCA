"""
DGCA English Encoder v2 — Noun Phrase Parsing & Structure Extraction.
Extracts determiners, quantities, modifiers, protected spans, and head lemmas.
Fail-closed on unsupported syntax. No positional guessing.
"""
from __future__ import annotations

from dgca.encoding.english.morphology import (
    COPULAS,
    DETERMINERS,
    PREPOSITIONS,
    RELATIVE_MARKERS,
    lemmatize_noun,
)
from dgca.encoding.english.types import NounPhraseView, ProtectedSpan, Token, TokenKind

# Numeric word to digit string mapping
NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "twenty": "20", "fifty": "50", "hundred": "100",
}


KNOWN_VERB_STEMS = frozenset({
    "have", "has", "had", "lay", "lays", "laid", "hunt", "hunts", "hunted",
    "orbit", "orbits", "orbited", "invent", "invents", "invented",
    "convert", "converts", "converted", "freeze", "freezes", "froze",
    "live", "lives", "lived", "chase", "chases", "chased", "fly", "flies", "flew",
    "eat", "eats", "ate", "swim", "swims", "swam", "see", "saw", "seen",
    "make", "makes", "made", "build", "builds", "built", "give", "gives", "gave",
    "take", "takes", "took", "know", "knows", "knew", "think", "thinks", "thought",
    "find", "finds", "found", "bite", "bites", "bit", "bitten", "fall", "falls", "fell",
    "grow", "grows", "grew", "run", "runs", "ran", "sleep", "sleeps", "slept",
    "catch", "catches", "caught", "produce", "produces", "produced",
    "contain", "contains", "contained", "write", "writes", "wrote", "written",
})


def parse_noun_phrase(
    tokens: tuple[Token, ...],
    spans: tuple[ProtectedSpan, ...] = (),
) -> tuple[NounPhraseView | None, int]:
    """
    Parses a single Noun Phrase from the beginning of `tokens`.
    Returns (NounPhraseView, tokens_consumed). If no valid NP, returns (None, 0).
    """
    if not tokens:
        return None, 0

    idx = 0
    n = len(tokens)

    # 1. Check if tokens[idx] starts a protected span
    for span in spans:
        if span.start_offset == tokens[idx].start_offset:
            # Check length of span in tokens
            span_len = len(span.tokens)
            np_view = NounPhraseView(
                head_lemma=span.canonical_symbol,
                head_token=tokens[idx],
                protected_span=span,
            )
            return np_view, span_len

    # 2. Check Determiner
    det: str | None = None
    if idx < n and tokens[idx].normalized_surface in DETERMINERS:
        det = tokens[idx].normalized_surface
        idx += 1

    # 3. Check Quantity
    qty: str | None = None
    if idx < n:
        tok = tokens[idx]
        if tok.token_kind == TokenKind.NUMBER:
            qty = tok.normalized_surface
            idx += 1
        elif tok.normalized_surface in NUMBER_WORDS:
            qty = NUMBER_WORDS[tok.normalized_surface]
            idx += 1

    # 4. Check if a protected span starts here (e.g. after determiner "The United States")
    for span in spans:
        if idx < n and span.start_offset == tokens[idx].start_offset:
            span_len = len(span.tokens)
            np_view = NounPhraseView(
                head_lemma=span.canonical_symbol,
                head_token=tokens[idx],
                determiner=det,
                quantity=qty,
                protected_span=span,
            )
            return np_view, idx + span_len

    # 5. Collect Modifiers (adjectives/nouns) and Head
    # Words before verbs, copulas, prepositions, or sentence end
    content_words: list[Token] = []
    while idx < n:
        tok = tokens[idx]
        low = tok.normalized_surface

        # Stop boundaries
        if tok.token_kind == TokenKind.PUNCT:
            break
        if low in COPULAS or low in PREPOSITIONS or low in RELATIVE_MARKERS or low in {"and", "or", "but"}:
            break

        # Stop if we already have content words and this word is a verb predicate
        if content_words and (low in KNOWN_VERB_STEMS or (low.endswith("ed") and low not in {"red", "bed"})):
            break

        content_words.append(tok)
        idx += 1

    if not content_words:
        return None, 0

    UNIT_HEADS = frozenset({"degree", "degrees", "meter", "meters", "percent", "kilogram", "kilograms", "mile", "miles", "kilometer", "kilometers", "hour", "hours", "minute", "minutes", "second", "seconds"})

    # Check if first word is a unit following a quantity (e.g. "zero degrees Celsius")
    if len(content_words) > 1 and content_words[0].normalized_surface in UNIT_HEADS and qty is not None:
        head_token = content_words[0]
        mod_tokens = content_words[1:]
    else:
        # The last content word is the NP head; preceding words are modifiers
        head_token = content_words[-1]
        mod_tokens = content_words[:-1]

    head_lemma, _ = lemmatize_noun(head_token.surface)
    modifiers = tuple(t.normalized_surface for t in mod_tokens)

    np_view = NounPhraseView(
        head_lemma=head_lemma,
        head_token=head_token,
        modifiers=modifiers,
        determiner=det,
        quantity=qty,
    )
    return np_view, idx
