"""
DGCA English Encoder v2 Package.
"""
from dgca.encoding.english.encoder import EnglishEncoderV2
from dgca.encoding.english.normalize import normalize_text
from dgca.encoding.english.tokenize import tokenize, tokenize_normalized
from dgca.encoding.english.types import (
    ClauseFrame,
    EncoderAnalysisResult,
    NounPhraseView,
    ProtectedSpan,
    Token,
    TokenAccountingRecord,
    TokenKind,
)

__all__ = [
    "ClauseFrame",
    "EncoderAnalysisResult",
    "EnglishEncoderV2",
    "NounPhraseView",
    "ProtectedSpan",
    "Token",
    "TokenAccountingRecord",
    "TokenKind",
    "normalize_text",
    "tokenize",
    "tokenize_normalized",
]
