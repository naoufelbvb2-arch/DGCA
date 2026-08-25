"""
DGCA English Encoder v2 — Layer 8: Episode Emitter.
Translates structured ClauseFrames into canonical DGCA SensoryEpisodes.
Pure, deterministic, graph-free translation.
Zero learning, zero graph mutation, zero world-knowledge augmentation.
"""
from __future__ import annotations

from dgca.encoder import QUANTITY, TEXT, SensoryEpisode
from dgca.encoding.english.types import ClauseFrame, NounPhraseView


def _emit_np_episodes(np_view: NounPhraseView, context: str | None = None) -> list[SensoryEpisode]:
    """Emits simultaneous modifier and quantity episodes for a noun phrase."""
    episodes: list[SensoryEpisode] = []
    head = np_view.head_lemma
    inst = np_view.instance_binding

    # Quantity episode
    if np_view.quantity:
        ref = inst if inst else head
        signals = [(TEXT, ref), (TEXT, head), (QUANTITY, np_view.quantity)]
        # If modifiers present, attach them
        for mod in np_view.modifiers:
            signals.append((TEXT, mod))
        episodes.append(SensoryEpisode(kind="simultaneous", context=context, signals=signals))
    elif np_view.modifiers:
        # Modifier episode(s)
        ref = inst if inst else head
        if inst:
            signals = [(TEXT, inst), (TEXT, head)] + [(TEXT, m) for m in np_view.modifiers]
            episodes.append(SensoryEpisode(kind="simultaneous", context=context, signals=signals))
        else:
            signals = [(TEXT, head)] + [(TEXT, m) for m in np_view.modifiers]
            episodes.append(SensoryEpisode(kind="simultaneous", context=context, signals=signals))

    return episodes


def emit_sensory_episodes(
    frame: ClauseFrame,
    context: str | None = None,
    is_dependent: bool = False,
) -> list[SensoryEpisode]:
    """
    Translates a ClauseFrame into canonical DGCA SensoryEpisodes.
    """
    episodes: list[SensoryEpisode] = []

    subj = frame.subject
    obj = frame.object
    pred = frame.predicate
    negated = frame.negated
    prep_rels = frame.prepositional_relations
    dep_clauses = frame.dependent_clauses

    if subj is None:
        return []

    subj_ref = subj.instance_binding if subj.instance_binding else subj.head_lemma
    obj_ref = obj.instance_binding if obj and obj.instance_binding else (obj.head_lemma if obj else None)

    # 1. Emit Subject Modifier / Quantity Episodes (skip if dependent relative clause)
    if not is_dependent:
        episodes.extend(_emit_np_episodes(subj, context))

    # 2. Emit Object Modifier / Quantity Episodes
    if obj:
        episodes.extend(_emit_np_episodes(obj, context))

    # 3. Explicit Negation -> Contradiction Episode (Zero Positive Associations)
    if negated:
        if obj_ref:
            episodes.append(SensoryEpisode(
                kind="simultaneous",
                context=context,
                contradictions=[(f"text:{subj_ref}", f"text:{obj_ref}")],
            ))
        return episodes

    # 4. Copular Nominal Definition: "A falcon is a bird." -> simultaneous(falcon, bird)
    if pred == "be" and obj_ref:
        episodes.append(SensoryEpisode(
            kind="simultaneous",
            context=context,
            signals=[(TEXT, subj_ref), (TEXT, obj_ref)],
        ))

    # 5. Copular Property: "The apple is red."
    elif pred == "be" and frame.subject_modifiers and not obj_ref and not prep_rels:
        for mod in frame.subject_modifiers:
            episodes.append(SensoryEpisode(
                kind="simultaneous",
                context=context,
                signals=[(TEXT, subj_ref), (TEXT, mod)],
            ))

    # 6. Active SVO or Verb Sequence
    elif pred and pred != "be" and obj_ref and not prep_rels:
        # sequence: [subj] -> [pred] -> [obj]
        episodes.append(SensoryEpisode(
            kind="sequence",
            context=context,
            steps=[[(TEXT, subj_ref)], [(TEXT, pred)], [(TEXT, obj_ref)]],
        ))

    # 7. SVO with Prepositional Extension: "converts light energy into chemical energy"
    elif pred and pred != "be" and obj_ref and prep_rels:
        steps = [[(TEXT, subj_ref)], [(TEXT, pred)], [(TEXT, obj_ref)]]
        for prep_op, pobj in prep_rels:
            episodes.extend(_emit_np_episodes(pobj, context))
            pobj_ref = pobj.instance_binding if pobj.instance_binding else pobj.head_lemma
            steps.extend([[(TEXT, prep_op)], [(TEXT, pobj_ref)]])
        episodes.append(SensoryEpisode(kind="sequence", context=context, steps=steps))

    # 8. Verb with Preposition directly: "freezes at zero degrees Celsius"
    elif pred and pred != "be" and not obj_ref and prep_rels:
        steps = [[(TEXT, subj_ref)], [(TEXT, pred)]]
        for prep_op, pobj in prep_rels:
            episodes.extend(_emit_np_episodes(pobj, context))
            pobj_ref = pobj.instance_binding if pobj.instance_binding else pobj.head_lemma
            steps.extend([[(TEXT, prep_op)], [(TEXT, pobj_ref)]])
        episodes.append(SensoryEpisode(kind="sequence", context=context, steps=steps))

    # 9. Copular Prepositional: "The apple is on the table." / "A falcon is a bird of prey."
    if pred == "be" and prep_rels:
        origin_ref = obj_ref if obj_ref else subj_ref
        for prep_op, pobj in prep_rels:
            episodes.extend(_emit_np_episodes(pobj, context))
            pobj_ref = pobj.instance_binding if pobj.instance_binding else pobj.head_lemma
            episodes.append(SensoryEpisode(
                kind="sequence",
                context=context,
                steps=[[(TEXT, origin_ref)], [(TEXT, prep_op)], [(TEXT, pobj_ref)]],
            ))

    # 10. Dependent / Relative Clauses
    for dep_frame in dep_clauses:
        episodes.extend(emit_sensory_episodes(dep_frame, context, is_dependent=True))

    return episodes
