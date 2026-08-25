"""
DGCA English Encoder v2 — Layer 1: Normalization.
Performs deterministic Unicode normalization, canonical punctuation/quote mapping,
and whitespace normalization while maintaining an exact per-character source offset map.
"""
from __future__ import annotations

import re
import unicodedata

from dgca.encoding.english.types import NormalizationResult

# Canonical replacements
_QUOTE_MAP = {
    "\u201c": '"', "\u201d": '"', "\u00ab": '"', "\u00bb": '"',
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u0060": "'", "\u00b4": "'",
}
_DASH_MAP = {
    "\u2013": "-", "\u2014": "-", "\u2015": "-", "\u2212": "-",
}


def normalize_text(raw_text: str) -> NormalizationResult:
    """
    Normalizes raw English Unicode text and builds an exact character-level offset map.
    norm_to_raw_offsets[i] = index in raw_text corresponding to normalized_text[i].
    """
    if not raw_text:
        return NormalizationResult(
            raw_text="",
            normalized_text="",
            norm_to_raw_offsets=[],
            sentence_spans=(),
        )

    # Step 1: Character-by-character replacement with raw offset tracking
    norm_chars: list[str] = []
    norm_to_raw: list[int] = []

    for raw_idx, ch in enumerate(raw_text):
        # 1. Quote normalization
        if ch in _QUOTE_MAP:
            ch = _QUOTE_MAP[ch]
        # 2. Dash normalization
        elif ch in _DASH_MAP:
            ch = _DASH_MAP[ch]

        # 3. Unicode NFKC normalization
        nfkc_ch = unicodedata.normalize("NFKC", ch)
        for sub_ch in nfkc_ch:
            norm_chars.append(sub_ch)
            norm_to_raw.append(raw_idx)

    # Step 2: Whitespace normalization (collapse consecutive spaces, but preserve newlines)
    collapsed_chars: list[str] = []
    collapsed_offsets: list[int] = []
    in_space = False

    for i, ch in enumerate(norm_chars):
        if ch in (" ", "\t", "\r"):
            if not in_space:
                collapsed_chars.append(" ")
                collapsed_offsets.append(norm_to_raw[i])
                in_space = True
        else:
            in_space = False
            collapsed_chars.append(ch)
            collapsed_offsets.append(norm_to_raw[i])

    normalized_str = "".join(collapsed_chars)

    # Step 3: Sentence boundary detection
    # Split on sentence terminals (. ! ?) not inside abbreviations/decimals
    sentence_spans: list[tuple[int, int]] = []
    s_start = 0

    # Match sentence boundaries
    pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\n]|$)|(?<=\n)\s*')
    pos = 0
    while pos < len(normalized_str):
        # Check non-boundary cases like "3.14", "U.S.", "Dr."
        m = pattern.search(normalized_str, pos)
        if not m:
            break
        split_point = m.start()
        # Verify it's not an initialism like U.S. or decimal like 3.14
        if split_point > 0 and normalized_str[split_point] == '.':
            # Decimal check
            if split_point + 1 < len(normalized_str) and normalized_str[split_point - 1].isdigit() and normalized_str[split_point + 1].isdigit():
                pos = m.end()
                continue
            # Initialism check: e.g. "U.S. "
            if split_point >= 2 and normalized_str[split_point - 2] == '.' and normalized_str[split_point - 1].isupper():
                pos = m.end()
                continue

        seg = normalized_str[s_start:split_point].strip()
        if seg:
            # Get raw coordinates
            first_idx = s_start
            while first_idx < split_point and normalized_str[first_idx] == " ":
                first_idx += 1
            last_idx = split_point - 1
            while last_idx >= first_idx and normalized_str[last_idx] == " ":
                last_idx -= 1
            if first_idx <= last_idx:
                raw_start = collapsed_offsets[first_idx]
                raw_end = collapsed_offsets[last_idx] + 1
                sentence_spans.append((raw_start, raw_end))

        s_start = m.end()
        pos = m.end()

    # Trailing segment
    trailing = normalized_str[s_start:].strip()
    if trailing:
        first_idx = s_start
        while first_idx < len(normalized_str) and normalized_str[first_idx] == " ":
            first_idx += 1
        last_idx = len(normalized_str) - 1
        while last_idx >= first_idx and normalized_str[last_idx] == " ":
            last_idx -= 1
        if first_idx <= last_idx:
            raw_start = collapsed_offsets[first_idx]
            raw_end = collapsed_offsets[last_idx] + 1
            sentence_spans.append((raw_start, raw_end))

    if not sentence_spans and normalized_str.strip():
        sentence_spans.append((0, len(raw_text)))

    return NormalizationResult(
        raw_text=raw_text,
        normalized_text=normalized_str,
        norm_to_raw_offsets=collapsed_offsets,
        sentence_spans=tuple(sentence_spans),
    )
