from dgca.encoding.english.morphology import (
    COORDINATORS,
    COPULAS,
    DETERMINERS,
    MODALS,
    NEGATORS,
    PREPOSITIONS,
    RELATIVE_MARKERS,
)
from dgca.encoding.english.types import ClauseFrame, Token, TokenAccountingRecord, TokenKind


def build_token_accounting(
    tokens: tuple[Token, ...],
    frames: tuple[ClauseFrame, ...],
) -> tuple[TokenAccountingRecord, ...]:
    """
    Produces complete token-by-token accounting records to ensure zero silent loss (EN2-INV-18).
    Every content token is EMITTED, CONSUMED_WITH_REASON, or UNSUPPORTED_WITH_REASON.
    """
    records: list[TokenAccountingRecord] = []

    # Collect all emitted tokens and consumed tokens from frames (recursively)
    emitted_surfaces: set[str] = set()

    def _collect_frame_surfaces(f: ClauseFrame) -> None:
        if f.subject:
            if f.subject.head_token:
                emitted_surfaces.add(f.subject.head_token.surface)
                emitted_surfaces.add(f.subject.head_token.normalized_surface)
            if f.subject.protected_span:
                for st in f.subject.protected_span.tokens:
                    emitted_surfaces.add(st.surface)
                    emitted_surfaces.add(st.normalized_surface)
            for mod in f.subject.modifiers:
                emitted_surfaces.add(mod)
        if f.predicate_token:
            emitted_surfaces.add(f.predicate_token.surface)
            emitted_surfaces.add(f.predicate_token.normalized_surface)
        if f.object:
            if f.object.head_token:
                emitted_surfaces.add(f.object.head_token.surface)
                emitted_surfaces.add(f.object.head_token.normalized_surface)
            if f.object.protected_span:
                for st in f.object.protected_span.tokens:
                    emitted_surfaces.add(st.surface)
                    emitted_surfaces.add(st.normalized_surface)
            for mod in f.object.modifiers:
                emitted_surfaces.add(mod)
        for prep_op, pobj in f.prepositional_relations:
            if pobj.head_token:
                emitted_surfaces.add(pobj.head_token.surface)
                emitted_surfaces.add(pobj.head_token.normalized_surface)
            if pobj.protected_span:
                for st in pobj.protected_span.tokens:
                    emitted_surfaces.add(st.surface)
                    emitted_surfaces.add(st.normalized_surface)
            for mod in pobj.modifiers:
                emitted_surfaces.add(mod)
        for dep in f.dependent_clauses:
            _collect_frame_surfaces(dep)

    for frm in frames:
        _collect_frame_surfaces(frm)

    for tok in tokens:
        surf = tok.surface
        low = tok.normalized_surface

        if tok.token_kind == TokenKind.PUNCT:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_PUNCT",
                reason="Punctuation delimiter",
            )
        elif low in DETERMINERS:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_DETERMINER",
                reason="Grammatical determiner consumed in noun phrase",
            )
        elif low in COPULAS:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_COPULA",
                reason="Grammatical copula consumed in clause framing",
            )
        elif low in MODALS or low in {"was", "were", "been", "being", "is", "are", "do", "does", "did", "have", "has", "had"} and surf not in emitted_surfaces:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_AUX",
                reason="Auxiliary or modal verb consumed in clause framing",
            )
        elif low in NEGATORS or tok.clitic_info == "CONTRACTION_NEGATION":
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_NEGATION",
                reason="Explicit negation operator routed to contradiction",
            )
        elif low in PREPOSITIONS or low == "by":
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_PREPOSITION",
                reason="Relational preposition operator in clause or passive structure",
            )
        elif low in COORDINATORS:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_COORDINATOR",
                reason="Grammatical coordinator connecting clauses or predicates",
            )
        elif low in RELATIVE_MARKERS:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="CONSUMED_RELATIVE_MARKER",
                reason="Relative pronoun introducing dependent relative clause",
            )
        elif tok.token_kind == TokenKind.NUMBER or low in {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "twenty", "fifty", "hundred"}:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="EMITTED_QUANTITY",
                reason="Quantity binding emitted in noun phrase episode",
                target_ref=low,
            )
        elif surf in emitted_surfaces or low in emitted_surfaces:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="EMITTED",
                reason="Emitted as head, modifier, predicate, or span member",
                target_ref=low,
            )
        else:
            rec = TokenAccountingRecord(
                token_surface=surf,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
                disposition="UNSUPPORTED_WITH_REASON",
                reason="Syntax structure around token is outside supported template grammar",
            )
        records.append(rec)

    return tuple(records)
