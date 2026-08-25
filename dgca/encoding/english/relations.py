"""
DGCA English Encoder v2 — Layer 7: Relation & Binding Resolution.
Handles deterministic instance ID derivation, relational preposition operators,
quantity bindings, and same-head multi-role separation.
Zero mutable global counters. Zero external world semantics.
"""
from __future__ import annotations

import hashlib

from dgca.encoding.english.types import ClauseFrame, NounPhraseView


def derive_deterministic_instance_id(head: str, role: str, modifier_str: str, source_ref: str = "") -> str:
    """
    Derives a deterministic, immutable instance ID from head lemma, role, modifiers, and source coordinates.
    Zero mutable global state.
    """
    key = f"{source_ref}_{head}_{role}_{modifier_str}".encode()
    h = hashlib.sha256(key).hexdigest()[:8]
    return f"inst:{head}:{h}"


def resolve_clause_bindings(frame: ClauseFrame, source_ref: str = "") -> ClauseFrame:
    """
    Resolves instance bindings and same-head multi-role separation within a ClauseFrame.
    """
    subj = frame.subject
    obj = frame.object
    prep_rels = frame.prepositional_relations

    new_subj = subj
    new_obj = obj
    new_prep_rels: list[tuple[str, NounPhraseView]] = []
    qty_bindings: list[tuple[str, str]] = []

    # Check if object has quantity
    if obj and obj.quantity:
        inst_id = derive_deterministic_instance_id(obj.head_lemma, "obj_qty", f"qty_{obj.quantity}", source_ref)
        new_obj = NounPhraseView(
            head_lemma=obj.head_lemma,
            head_token=obj.head_token,
            modifiers=obj.modifiers,
            determiner=obj.determiner,
            quantity=obj.quantity,
            protected_span=obj.protected_span,
            instance_binding=inst_id,
        )
        qty_bindings.append((inst_id, obj.quantity))

    # Check same-head multi-role binding (e.g. "converts light energy into chemical energy")
    # Compare obj head vs prep_obj head
    if obj and prep_rels:
        for prep_str, pobj in prep_rels:
            if pobj.head_lemma == obj.head_lemma:
                # Same head in multiple roles! Generate distinct deterministic instance bindings
                mod1_str = "_".join(obj.modifiers)
                mod2_str = "_".join(pobj.modifiers)
                inst1 = derive_deterministic_instance_id(obj.head_lemma, "obj", mod1_str, source_ref)
                inst2 = derive_deterministic_instance_id(pobj.head_lemma, "prep_obj", mod2_str, source_ref)

                new_obj = NounPhraseView(
                    head_lemma=obj.head_lemma,
                    head_token=obj.head_token,
                    modifiers=obj.modifiers,
                    determiner=obj.determiner,
                    quantity=obj.quantity,
                    protected_span=obj.protected_span,
                    instance_binding=inst1,
                )
                new_pobj = NounPhraseView(
                    head_lemma=pobj.head_lemma,
                    head_token=pobj.head_token,
                    modifiers=pobj.modifiers,
                    determiner=pobj.determiner,
                    quantity=pobj.quantity,
                    protected_span=pobj.protected_span,
                    instance_binding=inst2,
                )
                new_prep_rels.append((prep_str, new_pobj))
            else:
                # Check if pobj has quantity
                if pobj.quantity:
                    inst_p = derive_deterministic_instance_id(pobj.head_lemma, "pobj_qty", f"qty_{pobj.quantity}", source_ref)
                    pobj_bound = NounPhraseView(
                        head_lemma=pobj.head_lemma,
                        head_token=pobj.head_token,
                        modifiers=pobj.modifiers,
                        determiner=pobj.determiner,
                        quantity=pobj.quantity,
                        protected_span=pobj.protected_span,
                        instance_binding=inst_p,
                    )
                    new_prep_rels.append((prep_str, pobj_bound))
                    qty_bindings.append((inst_p, pobj.quantity))
                else:
                    new_prep_rels.append((prep_str, pobj))
    elif prep_rels:
        for prep_str, pobj in prep_rels:
            if pobj.quantity:
                inst_p = derive_deterministic_instance_id(pobj.head_lemma, "pobj_qty", f"qty_{pobj.quantity}", source_ref)
                pobj_bound = NounPhraseView(
                    head_lemma=pobj.head_lemma,
                    head_token=pobj.head_token,
                    modifiers=pobj.modifiers,
                    determiner=pobj.determiner,
                    quantity=pobj.quantity,
                    protected_span=pobj.protected_span,
                    instance_binding=inst_p,
                )
                new_prep_rels.append((prep_str, pobj_bound))
                qty_bindings.append((inst_p, pobj.quantity))
            else:
                new_prep_rels.append((prep_str, pobj))

    return ClauseFrame(
        subject=new_subj,
        predicate=frame.predicate,
        predicate_token=frame.predicate_token,
        object=new_obj,
        subject_modifiers=frame.subject_modifiers,
        object_modifiers=frame.object_modifiers,
        prepositional_relations=tuple(new_prep_rels),
        quantity_bindings=tuple(qty_bindings),
        negated=frame.negated,
        voice=frame.voice,
        passive_agent=frame.passive_agent,
        passive_patient=frame.passive_patient,
        inherited_subject_ref=frame.inherited_subject_ref,
        dependent_clauses=frame.dependent_clauses,
        rule_provenance=frame.rule_provenance,
        disposition=frame.disposition,
    )
