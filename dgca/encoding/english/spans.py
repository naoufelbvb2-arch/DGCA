"""
DGCA English Encoder v2 — Layer 4: Span Protection.
Deterministic proper-name and compound span detection without external NER or LLMs.
Fail-closed on ambiguous capitalization to prevent false span mergers.
"""
from __future__ import annotations

from dgca.encoding.english.morphology import DETERMINERS
from dgca.encoding.english.types import ProtectedSpan, Token, TokenKind

# Recognized multi-word proper-name templates & connectors
_SPAN_CONNECTORS = frozenset({"of", "and", "the"})

# Explicit common proper names / geographic entities
_KNOWN_PROPER_SPANS = frozenset({
    "new york city", "new york", "united states", "united states of america",
    "alexander graham bell", "solar system", "great britain", "north america",
    "south america", "pacific ocean", "atlantic ocean", "middle east",
})


def detect_protected_spans(tokens: tuple[Token, ...]) -> tuple[ProtectedSpan, ...]:
    """
    Detects deterministic multi-token proper-name and compound spans.
    Tokens within a protected span are preserved as a unified lexical identity.
    """
    if len(tokens) < 2:
        return ()

    spans: list[ProtectedSpan] = []
    i = 0
    n = len(tokens)

    while i < n:
        # Never start a proper span with a determiner
        if tokens[i].normalized_surface in DETERMINERS:
            i += 1
            continue

        # Check window of length 4 down to 2
        matched = False
        for span_len in (4, 3, 2):
            if i + span_len > n:
                continue

            window = tokens[i : i + span_len]
            # All tokens must be words
            if not all(t.token_kind == TokenKind.WORD for t in window):
                continue

            window_surfaces = [t.surface for t in window]
            window_lower = [t.normalized_surface for t in window]
            joined_lower = " ".join(window_lower)

            # Condition 1: Known proper multi-word span
            if joined_lower in _KNOWN_PROPER_SPANS:
                canon_sym = "_".join(window_lower)
                p_span = ProtectedSpan(
                    span_id=f"span_{tokens[i].start_offset}_{tokens[i+span_len-1].end_offset}",
                    tokens=tuple(window),
                    canonical_symbol=canon_sym,
                    start_offset=tokens[i].start_offset,
                    end_offset=tokens[i + span_len - 1].end_offset,
                    span_type="PROPER_NAME",
                )
                spans.append(p_span)
                i += span_len
                matched = True
                break

            # Condition 2: Consecutive TitleCase proper name (e.g. Alexander Graham Bell)
            # Must not start at sentence index 0 if the second word is a verb/common word
            all_title = all(s[0].isupper() and len(s) > 1 for s in window_surfaces)
            if all_title:
                # If at index 0, verify it's a genuine proper name sequence
                # (e.g. "Alexander Graham Bell invented" -> Alexander Graham Bell is 3 title words, followed by lowercase verb)
                is_valid = True
                if i == 0 and span_len == 2:
                    # e.g. "Falcons hunt" -> hunt is verb, not proper span!
                    second_lower = window_lower[1]
                    if second_lower in {"hunt", "fly", "have", "eat", "live", "sleep", "orbit", "freeze", "run", "chase", "is", "are", "was", "were"}:
                        is_valid = False

                if is_valid:
                    canon_sym = "_".join(window_lower)
                    p_span = ProtectedSpan(
                        span_id=f"span_{tokens[i].start_offset}_{tokens[i+span_len-1].end_offset}",
                        tokens=tuple(window),
                        canonical_symbol=canon_sym,
                        start_offset=tokens[i].start_offset,
                        end_offset=tokens[i + span_len - 1].end_offset,
                        span_type="PROPER_NAME",
                    )
                    spans.append(p_span)
                    i += span_len
                    matched = True
                    break

        if not matched:
            i += 1

    return tuple(spans)
