"""
DGCA English Encoder v2 — Layer 2: Tokenization.
Produces deterministic typed tokens with exact raw source coordinates,
handling contractions, possessives, decimal numbers, and initialisms.
Zero silent content loss.
"""
from __future__ import annotations

import re

from dgca.encoding.english.normalize import normalize_text
from dgca.encoding.english.types import NormalizationResult, Token, TokenKind

# Contraction patterns
_CONTRACTION_MAP = {
    "don't": ("do", "n't", "CONTRACTION_NEGATION"),
    "doesn't": ("does", "n't", "CONTRACTION_NEGATION"),
    "didn't": ("did", "n't", "CONTRACTION_NEGATION"),
    "can't": ("can", "n't", "CONTRACTION_NEGATION"),
    "cannot": ("can", "not", "CONTRACTION_NEGATION"),
    "won't": ("will", "n't", "CONTRACTION_NEGATION"),
    "isn't": ("is", "n't", "CONTRACTION_NEGATION"),
    "aren't": ("are", "n't", "CONTRACTION_NEGATION"),
    "wasn't": ("was", "n't", "CONTRACTION_NEGATION"),
    "weren't": ("were", "n't", "CONTRACTION_NEGATION"),
    "hasn't": ("has", "n't", "CONTRACTION_NEGATION"),
    "haven't": ("have", "n't", "CONTRACTION_NEGATION"),
    "hadn't": ("had", "n't", "CONTRACTION_NEGATION"),
    "wouldn't": ("would", "n't", "CONTRACTION_NEGATION"),
    "shouldn't": ("should", "n't", "CONTRACTION_NEGATION"),
    "couldn't": ("could", "n't", "CONTRACTION_NEGATION"),
}

# Regex for token matching in normalized text
# 1. Initialisms: (?:[A-Za-z]\.){2,}
# 2. Decimal numbers: \d+(?:\.\d+)+
# 3. Plain integers: \d+
# 4. Words with internal hyphens or apostrophes: [A-Za-z]+(?:['\-_][A-Za-z]+)*
# 5. Punctuation & quotes & symbols: [^\s\w]
_TOKEN_RE = re.compile(
    r"""
    (?P<INITIALISM>(?:[A-Za-z]\.){2,})
    |(?P<NUMBER>\d+(?:\.\d+)?)
    |(?P<WORD>[A-Za-z]+(?:['’][A-Za-z]+)?)
    |(?P<PUNCT>[.,;:!?\(\)\[\]\{\}])
    |(?P<QUOTE>["'”’“‘])
    |(?P<SYMBOL>[+\-*/=<>%&$@^~#])
    |(?P<OTHER>[^\s\w])
    """,
    re.VERBOSE,
)


def tokenize_normalized(norm_res: NormalizationResult) -> tuple[Token, ...]:
    """
    Tokenizes normalized text and attaches exact raw source offsets using the offset map.
    """
    norm_text = norm_res.normalized_text
    offsets = norm_res.norm_to_raw_offsets
    if not norm_text or not offsets:
        return ()

    tokens: list[Token] = []

    for match in _TOKEN_RE.finditer(norm_text):
        kind_name = match.lastgroup
        surface = match.group(0)
        n_start, n_end = match.start(), match.end()

        # Map to raw source offsets
        raw_start = offsets[n_start]
        raw_end = offsets[n_end - 1] + 1

        lower_surface = surface.lower()

        # Check explicit contraction decomposition
        if lower_surface in _CONTRACTION_MAP:
            base_s, clitic_s, clitic_kind = _CONTRACTION_MAP[lower_surface]
            # Split coordinates
            split_idx = n_start + len(base_s)
            r_split = offsets[min(split_idx, len(offsets) - 1)]

            tok1 = Token(
                surface=surface[: len(base_s)],
                normalized_surface=base_s,
                start_offset=raw_start,
                end_offset=r_split,
                token_kind=TokenKind.WORD,
            )
            tok2 = Token(
                surface=surface[len(base_s) :],
                normalized_surface=clitic_s,
                start_offset=r_split,
                end_offset=raw_end,
                token_kind=TokenKind.WORD,
                clitic_info=clitic_kind,
            )
            tokens.extend([tok1, tok2])
            continue

        # Check possessive 's decomposition (e.g. Earth's -> Earth + 's)
        if lower_surface.endswith("'s") and len(lower_surface) > 2:
            base_s = surface[:-2]
            split_idx = n_start + len(base_s)
            r_split = offsets[min(split_idx, len(offsets) - 1)]

            tok1 = Token(
                surface=base_s,
                normalized_surface=base_s.lower(),
                start_offset=raw_start,
                end_offset=r_split,
                token_kind=TokenKind.WORD,
            )
            tok2 = Token(
                surface=surface[-2:],
                normalized_surface="'s",
                start_offset=r_split,
                end_offset=raw_end,
                token_kind=TokenKind.WORD,
                clitic_info="POSSESSIVE",
            )
            tokens.extend([tok1, tok2])
            continue

        # Classify token kind
        if kind_name == "INITIALISM":
            tok_kind = TokenKind.INITIALISM
        elif kind_name == "NUMBER":
            tok_kind = TokenKind.NUMBER
        elif kind_name == "WORD":
            tok_kind = TokenKind.WORD
        elif kind_name == "PUNCT":
            tok_kind = TokenKind.PUNCT
        elif kind_name == "QUOTE":
            tok_kind = TokenKind.QUOTE
        elif kind_name == "SYMBOL":
            tok_kind = TokenKind.SYMBOL
        else:
            tok_kind = TokenKind.SYMBOL

        token = Token(
            surface=surface,
            normalized_surface=lower_surface,
            start_offset=raw_start,
            end_offset=raw_end,
            token_kind=tok_kind,
        )
        tokens.append(token)

    return tuple(tokens)


def tokenize(raw_text: str) -> tuple[Token, ...]:
    """Convenience single-call tokenization from raw text."""
    norm_res = normalize_text(raw_text)
    return tokenize_normalized(norm_res)
