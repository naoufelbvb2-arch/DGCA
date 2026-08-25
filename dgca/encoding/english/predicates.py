"""
DGCA English Encoder v2 — Syntactic Role & Predicate Parsing.
Template-bounded structural parsing for SVO, copulas, passives, negation,
prepositional relations, relative clauses, and coordinated predicates.
Zero learned parsers, zero LLMs, fail-closed on unsupported syntax.
"""
from __future__ import annotations

from dgca.encoding.english.morphology import (
    COPULAS,
    NEGATORS,
    PREPOSITIONS,
    RELATIVE_MARKERS,
    lemmatize_verb,
)
from dgca.encoding.english.noun_phrases import parse_noun_phrase
from dgca.encoding.english.types import ClauseFrame, NounPhraseView, ProtectedSpan, Token, TokenKind


def parse_clause(
    tokens: tuple[Token, ...],
    spans: tuple[ProtectedSpan, ...] = (),
    inherited_subject: NounPhraseView | None = None,
) -> tuple[ClauseFrame | None, int]:
    """
    Parses a single supported clause structure from `tokens`.
    Returns (ClauseFrame, tokens_consumed).
    """
    if not tokens:
        return None, 0

    idx = 0
    n = len(tokens)

    # 1. Parse Subject (or inherit if coordinated predicate)
    subject_np: NounPhraseView | None = None
    if inherited_subject is not None:
        subject_np = inherited_subject
    else:
        subject_np, consumed = parse_noun_phrase(tokens[idx:], spans)
        if subject_np is None or consumed == 0:
            return None, 0
        idx += consumed

    if idx >= n or tokens[idx].token_kind == TokenKind.PUNCT:
        return None, 0

    # 2. Check Negation on Subject (e.g. "No bird is a mammal")
    negated = (subject_np.determiner == "no")

    # 3. Check Predicate / Copula / Auxiliary
    verb_tok = tokens[idx]
    v_low = verb_tok.normalized_surface
    idx += 1

    # Case A: Copula ("is", "are", "was", "were", etc.)
    if v_low in COPULAS:
        # Check explicit negation after copula ("is not a star", "are not mammals")
        if idx < n and (tokens[idx].normalized_surface in NEGATORS or tokens[idx].clitic_info == "CONTRACTION_NEGATION"):
            negated = True
            idx += 1

        # Check Passive Voice: was/were/is/are + PARTICIPLE + by + AGENT
        if idx + 1 < n and tokens[idx + 1].normalized_surface == "by":
            participle_tok = tokens[idx]
            p_low = participle_tok.normalized_surface
            if p_low.endswith("ed") or p_low in {"eaten", "bitten", "seen", "caught", "built", "made", "given", "taken", "found", "chased"}:
                idx += 2  # Skip participle and 'by'
                agent_np, consumed_agent = parse_noun_phrase(tokens[idx:], spans)
                if agent_np is not None:
                    idx += consumed_agent
                    verb_lemma, _, _ = lemmatize_verb(participle_tok.surface)
                    frame = ClauseFrame(
                        subject=agent_np,  # Normalized agent in subject position
                        predicate=verb_lemma,
                        predicate_token=participle_tok,
                        object=subject_np,  # Normalized patient in object position
                        voice="PASSIVE",
                        passive_agent=agent_np,
                        passive_patient=subject_np,
                        negated=negated,
                        rule_provenance=("ENC2-R-PASSIVE-BY",),
                    )
                    return frame, idx

        # Check what follows:
        # A1: Prepositional relation ("is on the table", "is in the United States")
        if idx < n and tokens[idx].normalized_surface in PREPOSITIONS:
            prep_tok = tokens[idx]
            prep_str = prep_tok.normalized_surface
            idx += 1
            obj_np, consumed_obj = parse_noun_phrase(tokens[idx:], spans)
            if obj_np is not None:
                idx += consumed_obj
                frame = ClauseFrame(
                    subject=subject_np,
                    predicate="be",
                    predicate_token=verb_tok,
                    prepositional_relations=((f"rel:{prep_str}", obj_np),),
                    negated=negated,
                    rule_provenance=("ENC2-R-COPULA-PP",),
                )
                return frame, idx

        # A2: Nominal complement ("is a bird", "is a bird of prey", "is a large cat that...")
        obj_np, consumed_obj = parse_noun_phrase(tokens[idx:], spans)
        if obj_np is not None:
            idx += consumed_obj

            # Check if followed by prepositional complement ("of prey")
            prep_rels: list[tuple[str, NounPhraseView]] = []
            if idx < n and tokens[idx].normalized_surface in PREPOSITIONS:
                prep_str = tokens[idx].normalized_surface
                idx += 1
                prep_obj_np, consumed_pobj = parse_noun_phrase(tokens[idx:], spans)
                if prep_obj_np is not None:
                    idx += consumed_pobj
                    prep_rels.append((f"rel:{prep_str}", prep_obj_np))

            # Check if followed by relative clause ("that lives in Africa")
            dep_clauses: list[ClauseFrame] = []
            if idx < n and tokens[idx].normalized_surface in RELATIVE_MARKERS:
                idx += 1
                # Parse relative clause with obj_np as antecedent
                rel_frame, consumed_rel = parse_clause(tokens[idx:], spans, inherited_subject=obj_np)
                if rel_frame is not None:
                    idx += consumed_rel
                    dep_clauses.append(rel_frame)

            frame = ClauseFrame(
                subject=subject_np,
                predicate="be",
                predicate_token=verb_tok,
                object=obj_np,
                prepositional_relations=tuple(prep_rels),
                negated=negated,
                dependent_clauses=tuple(dep_clauses),
                rule_provenance=("ENC2-R-COPULA-NOMINAL",),
            )
            return frame, idx

        # A3: Adjective property ("is red", "is large")
        if idx < n and tokens[idx].token_kind == TokenKind.WORD:
            adj_tok = tokens[idx]
            idx += 1
            adj_lemma = adj_tok.normalized_surface
            frame = ClauseFrame(
                subject=subject_np,
                predicate="be",
                predicate_token=verb_tok,
                subject_modifiers=(adj_lemma,),
                negated=negated,
                rule_provenance=("ENC2-R-COPULA-ADJECTIVE",),
            )
            return frame, idx

    # Case B: Passive Voice ("was chased by the black cat", "is eaten by dogs")
    if v_low in COPULAS or (idx < n and tokens[idx-1].normalized_surface in COPULAS):
        # Already handled under copula or auxiliary
        pass

    # Check if this is an auxiliary copula leading to passive ("was chased by...")
    if v_low in COPULAS and idx < n and tokens[idx].token_kind == TokenKind.WORD:
        participle_tok = tokens[idx]
        p_low = participle_tok.normalized_surface
        if p_low.endswith("ed") or p_low in {"eaten", "bitten", "seen", "caught", "built", "made", "given", "taken", "found", "chased"}:
            idx += 1
            # Check "by" agent
            if idx < n and tokens[idx].normalized_surface == "by":
                idx += 1
                agent_np, consumed_agent = parse_noun_phrase(tokens[idx:], spans)
                if agent_np is not None:
                    idx += consumed_agent
                    verb_lemma, _, _ = lemmatize_verb(participle_tok.surface)
                    frame = ClauseFrame(
                        subject=agent_np,  # Normalized agent in subject position
                        predicate=verb_lemma,
                        predicate_token=participle_tok,
                        object=subject_np,  # Normalized patient in object position
                        voice="PASSIVE",
                        passive_agent=agent_np,
                        passive_patient=subject_np,
                        negated=negated,
                        rule_provenance=("ENC2-R-PASSIVE-BY",),
                    )
                    return frame, idx

    # Case C: Active Verb (SVO, S-V-PP, S-V-O-PP)
    verb_lemma, _, _ = lemmatize_verb(verb_tok.surface)

    # Check object NP
    obj_np, consumed_obj = parse_noun_phrase(tokens[idx:], spans)
    active_prep_rels: list[tuple[str, NounPhraseView]] = []

    if obj_np is not None:
        idx += consumed_obj
        # Check prepositional complement after object ("converts light energy into chemical energy")
        if idx < n and tokens[idx].normalized_surface in PREPOSITIONS:
            prep_str = tokens[idx].normalized_surface
            idx += 1
            pobj_np, consumed_pobj = parse_noun_phrase(tokens[idx:], spans)
            if pobj_np is not None:
                idx += consumed_pobj
                active_prep_rels.append((f"rel:{prep_str}", pobj_np))
    else:
        # Check prepositional complement directly after verb ("lives in Africa", "freezes at zero degrees Celsius")
        if idx < n and tokens[idx].normalized_surface in PREPOSITIONS:
            prep_str = tokens[idx].normalized_surface
            idx += 1
            pobj_np, consumed_pobj = parse_noun_phrase(tokens[idx:], spans)
            if pobj_np is not None:
                idx += consumed_pobj
                active_prep_rels.append((f"rel:{prep_str}", pobj_np))

    if obj_np is not None or active_prep_rels:
        frame = ClauseFrame(
            subject=subject_np,
            predicate=verb_lemma,
            predicate_token=verb_tok,
            object=obj_np,
            prepositional_relations=tuple(active_prep_rels),
            negated=negated,
            rule_provenance=("ENC2-R-ACTIVE-SVO" if obj_np else "ENC2-R-PP-RELATION",),
        )
        return frame, idx

    return None, 0
