"""
DGCA English Encoder v2 — Core Data Types & Intermediate Representation.
Defines transient data structures for normalization, tokenization, morphology,
span protection, syntactic parsing, and episode emission.
All structures are non-cognitive, non-learning, graph-free, and deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TokenKind(str, Enum):
    WORD = "WORD"
    NUMBER = "NUMBER"
    PUNCT = "PUNCT"
    QUOTE = "QUOTE"
    SYMBOL = "SYMBOL"
    INITIALISM = "INITIALISM"


@dataclass(frozen=True)
class Token:
    """Deterministic token preserving exact original raw source coordinates."""
    surface: str
    normalized_surface: str
    start_offset: int
    end_offset: int
    token_kind: TokenKind
    clitic_info: str | None = None
    grammatical_class: str | None = None

    def __repr__(self) -> str:
        return f"Token('{self.surface}', {self.token_kind.value}, [{self.start_offset}:{self.end_offset}])"


@dataclass(frozen=True)
class NormalizationResult:
    """Result of Layer 1 Normalization with reconstructable source offset mapping."""
    raw_text: str
    normalized_text: str
    norm_to_raw_offsets: list[int]
    sentence_spans: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class MorphFeature:
    """Layer 3 Morphological feature for a token derived via deterministic rules."""
    lemma: str
    grammatical_class: str  # "NOUN", "VERB", "ADJ", "DET", "COPULA", "PREP", "NEG", "COORD", "REL", "QUANT", "PRON", "PUNCT", "OTHER"
    is_plural: bool = False
    is_past: bool = False
    is_proper: bool = False
    is_copula: bool = False
    is_passive_participle: bool = False
    is_third_singular: bool = False


@dataclass(frozen=True)
class ProtectedSpan:
    """Layer 4 Protected proper-name or compound span."""
    span_id: str
    tokens: tuple[Token, ...]
    canonical_symbol: str
    start_offset: int
    end_offset: int
    span_type: str = "PROPER_NAME"  # "PROPER_NAME", "COMPOUND"


@dataclass(frozen=True)
class NounPhraseView:
    """Layer 5/6 Noun Phrase Structural View."""
    head_lemma: str
    head_token: Token | None
    modifiers: tuple[str, ...] = ()
    determiner: str | None = None
    quantity: str | None = None
    protected_span: ProtectedSpan | None = None
    prepositional_complements: tuple[tuple[str, NounPhraseView], ...] = ()
    relative_clause: ClauseFrame | None = None
    instance_binding: str | None = None


@dataclass(frozen=True)
class ClauseFrame:
    """
    Layer 6/7 Transient Encoder-Local Intermediate Representation (IR).
    NOT a DGCA cognitive primitive. Graph-free, non-learning, transient.
    """
    subject: NounPhraseView | None = None
    predicate: str | None = None
    predicate_token: Token | None = None
    object: NounPhraseView | None = None
    subject_modifiers: tuple[str, ...] = ()
    object_modifiers: tuple[str, ...] = ()
    prepositional_relations: tuple[tuple[str, NounPhraseView], ...] = ()
    quantity_bindings: tuple[tuple[str, str], ...] = ()  # (head, quantity)
    negated: bool = False
    voice: str = "ACTIVE"  # "ACTIVE", "PASSIVE"
    passive_agent: NounPhraseView | None = None
    passive_patient: NounPhraseView | None = None
    inherited_subject_ref: str | None = None
    dependent_clauses: tuple[ClauseFrame, ...] = ()
    rule_provenance: tuple[str, ...] = ()
    disposition: str = "COMPLETE"  # "COMPLETE", "SAFE_PARTIAL", "UNSUPPORTED"


@dataclass(frozen=True)
class TokenAccountingRecord:
    """Diagnostic accounting record for every input content token (No-Silent-Loss)."""
    token_surface: str
    start_offset: int
    end_offset: int
    disposition: str  # "EMITTED_HEAD", "EMITTED_MODIFIER", "EMITTED_RELATION_OPERATOR", "EMITTED_PREDICATE", "CONSUMED_DETERMINER", "CONSUMED_COPULA", "CONSUMED_AUX", "CONSUMED_PUNCT", "CONSUMED_NEGATION", "UNSUPPORTED_WITH_REASON"
    reason: str
    target_ref: str | None = None


@dataclass(frozen=True)
class EncoderAnalysisResult:
    """Comprehensive, graph-free analysis outcome returned by EnglishEncoderV2.analyze()."""
    raw_text: str
    normalized_text: str
    tokens: tuple[Token, ...]
    spans: tuple[ProtectedSpan, ...]
    clauses: tuple[ClauseFrame, ...]
    episodes: tuple[Any, ...]  # Tuple of DGCA SensoryEpisodes
    disposition: str  # "COMPLETE", "SAFE_PARTIAL", "UNSUPPORTED"
    token_accounting: tuple[TokenAccountingRecord, ...]
    rule_provenance: tuple[str, ...]
    diagnostics: dict[str, Any] = field(default_factory=dict)
