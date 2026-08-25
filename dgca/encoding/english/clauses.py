"""
DGCA English Encoder v2 — Layer 5: Clause Segmentation.
Segments multi-clause and coordinated sentences into independent ClauseFrames,
handling coordinated predicates with inherited subjects.
Zero flat whole-sentence co-occurrence.
"""
from __future__ import annotations

from dgca.encoding.english.morphology import COORDINATORS
from dgca.encoding.english.predicates import parse_clause
from dgca.encoding.english.types import ClauseFrame, ProtectedSpan, Token, TokenKind


def segment_and_parse_clauses(
    tokens: tuple[Token, ...],
    spans: tuple[ProtectedSpan, ...] = (),
) -> tuple[ClauseFrame, ...]:
    """
    Segments a sentence into structured ClauseFrames.
    Distinguishes coordinated predicates (Birds have feathers and lay eggs)
    from coordinated noun phrases.
    """
    if not tokens:
        return ()

    frames: list[ClauseFrame] = []
    idx = 0
    n = len(tokens)

    while idx < n:
        # Skip leading punctuation
        while idx < n and tokens[idx].token_kind == TokenKind.PUNCT:
            idx += 1
        if idx >= n:
            break

        # Parse first clause
        frame1, consumed = parse_clause(tokens[idx:], spans)
        if frame1 is None or consumed == 0:
            # Unsupported or safe partial
            break
        frames.append(frame1)
        idx += consumed

        # Check coordinator ("and", "or", "but")
        if idx < n and tokens[idx].normalized_surface in COORDINATORS:
            idx += 1  # Skip coordinator

            # Check if followed by coordinated predicate (e.g. "and lay eggs")
            # Try parsing with frame1.subject as inherited subject
            frame2, consumed2 = parse_clause(tokens[idx:], spans, inherited_subject=frame1.subject)
            if frame2 is not None and consumed2 > 0:
                # Attach provenance
                frame2_annotated = ClauseFrame(
                    subject=frame2.subject,
                    predicate=frame2.predicate,
                    predicate_token=frame2.predicate_token,
                    object=frame2.object,
                    subject_modifiers=frame2.subject_modifiers,
                    object_modifiers=frame2.object_modifiers,
                    prepositional_relations=frame2.prepositional_relations,
                    quantity_bindings=frame2.quantity_bindings,
                    negated=frame2.negated,
                    voice=frame2.voice,
                    inherited_subject_ref=frame1.subject.head_lemma if frame1.subject else None,
                    rule_provenance=("ENC2-R-COORD-PRED",),
                )
                frames.append(frame2_annotated)
                idx += consumed2
            else:
                break

    return tuple(frames)
