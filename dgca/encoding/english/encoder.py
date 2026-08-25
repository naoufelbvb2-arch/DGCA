"""
DGCA English Encoder v2 — Master Compiler Engine.
Executes the pure, deterministic, graph-free linguistic pipeline:
RawEnglish -> Normalization -> Tokenization -> Morphology -> SpanProtection ->
ClauseSegmentation -> SyntacticRoleParsing -> RelationBindingResolution -> EpisodeEmission.
Zero cognitive primitives, zero learned state, zero graph mutations.
"""
from __future__ import annotations

from dgca.encoder import SensoryEpisode
from dgca.encoding.english.clauses import segment_and_parse_clauses
from dgca.encoding.english.diagnostics import build_token_accounting
from dgca.encoding.english.emitter import emit_sensory_episodes
from dgca.encoding.english.normalize import normalize_text
from dgca.encoding.english.relations import resolve_clause_bindings
from dgca.encoding.english.spans import detect_protected_spans
from dgca.encoding.english.tokenize import tokenize_normalized
from dgca.encoding.english.types import EncoderAnalysisResult


class EnglishEncoderV2:
    """
    Pure, deterministic English linguistic front-end compiler for DGCA.
    Analyze != Learn.
    """

    def analyze(self, text: str, source_ref: str = "") -> EncoderAnalysisResult:
        """
        Pure, graph-free analysis of raw English text.
        Produces complete diagnostic tokens, spans, frames, and emitted SensoryEpisodes.
        """
        if not text or not text.strip():
            return EncoderAnalysisResult(
                raw_text=text,
                normalized_text="",
                tokens=(),
                spans=(),
                clauses=(),
                episodes=(),
                disposition="UNSUPPORTED",
                token_accounting=(),
                rule_provenance=(),
                diagnostics={"empty_input": True},
            )

        # 1. Normalization
        norm_res = normalize_text(text)

        # 2. Tokenization
        tokens = tokenize_normalized(norm_res)

        # 3. Span Protection
        spans = detect_protected_spans(tokens)

        # 4. Clause Segmentation & Parsing
        raw_frames = segment_and_parse_clauses(tokens, spans)

        # 5. Relation & Binding Resolution
        bound_frames = tuple(resolve_clause_bindings(f, source_ref) for f in raw_frames)

        # 6. Episode Emission
        emitted_eps: list[SensoryEpisode] = []
        rule_provenance: list[str] = []

        for f in bound_frames:
            emitted_eps.extend(emit_sensory_episodes(f, context=source_ref or None))
            rule_provenance.extend(f.rule_provenance)

        # 7. Token Accounting
        accounting = build_token_accounting(tokens, bound_frames)

        # 8. Determine Overall Disposition
        if not bound_frames:
            disposition = "UNSUPPORTED"
        else:
            disposition = "COMPLETE"

        return EncoderAnalysisResult(
            raw_text=text,
            normalized_text=norm_res.normalized_text,
            tokens=tokens,
            spans=spans,
            clauses=bound_frames,
            episodes=tuple(emitted_eps),
            disposition=disposition,
            token_accounting=accounting,
            rule_provenance=tuple(rule_provenance),
            diagnostics={
                "sentence_count": len(norm_res.sentence_spans),
                "token_count": len(tokens),
                "span_count": len(spans),
                "clause_count": len(bound_frames),
                "episode_count": len(emitted_eps),
            },
        )
