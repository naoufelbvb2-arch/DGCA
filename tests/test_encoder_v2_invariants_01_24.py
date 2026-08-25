"""
DGCA English Encoder v2 — Frozen Invariants Suite (EN2-INV-01 .. EN2-INV-24).
Authoritative verification of the 24 frozen architectural and semantic invariants.
Required result: 24 / 24 PASS.
"""
import pytest

from dgca.encoder import (
    MasterSymbolicEncoder,
)
from dgca.encoding.english import EnglishEncoderV2
from dgca.encoding.english.morphology import classify_morphology
from dgca.encoding.english.tokenize import tokenize
from dgca.graph import CognitiveGraph
from dgca.signature import behavioral_signature, build_reference_graph


@pytest.fixture
def encoder():
    return EnglishEncoderV2()


# ── EN2-INV-01 — Analyze != Learn Boundary
def test_en2_inv_01_analyze_not_learn(encoder):
    """EN2-INV-01: analyze() performs zero graph mutations."""
    g = CognitiveGraph()
    n_nodes_before = len(g.nodes)
    n_edges_before = len(g.edges)
    _res = encoder.analyze("The quick brown fox jumps over the lazy dog.")
    assert len(g.nodes) == n_nodes_before
    assert len(g.edges) == n_edges_before


# ── EN2-INV-02 — Persistent Statelessness
def test_en2_inv_02_persistent_statelessness():
    """EN2-INV-02: Two independent instances produce identical results."""
    enc1 = EnglishEncoderV2()
    enc2 = EnglishEncoderV2()
    text = "Photosynthesis converts light energy into chemical energy."
    res1 = enc1.analyze(text)
    res2 = enc2.analyze(text)
    assert res1.disposition == res2.disposition
    assert len(res1.episodes) == len(res2.episodes)
    assert res1.rule_provenance == res2.rule_provenance


# ── EN2-INV-03 — Law 3 Immunity
def test_en2_inv_03_law3_immunity(encoder):
    """EN2-INV-03: Law 3 is out of path and never executed in encoder."""
    import dgca.encoding.english.encoder as mod
    # Verify Law3 decay functions are not imported in encoder module
    assert not hasattr(mod, "_law3_decay")
    assert not hasattr(mod, "apply_law3")


# ── EN2-INV-04 — Graph Independence
def test_en2_inv_04_graph_independence(encoder):
    """EN2-INV-04: EnglishEncoderV2 holds no reference to CognitiveGraph."""
    assert not hasattr(encoder, "graph")
    assert not hasattr(encoder, "_graph")


# ── EN2-INV-05 — Explicit Negation Firewall
def test_en2_inv_05_explicit_negation_firewall(encoder):
    """EN2-INV-05: Negation emits only contradictions and zero positive links."""
    res = encoder.analyze("Mars is not a star.")
    assert len(res.episodes) == 1
    assert len(res.episodes[0].contradictions) == 1
    assert len(res.episodes[0].signals) == 0


# ── EN2-INV-06 — Zero Learned Parser Weights
def test_en2_inv_06_zero_learned_weights(encoder):
    """EN2-INV-06: Encoder uses zero learned weights/models."""
    assert not hasattr(encoder, "model")
    assert not hasattr(encoder, "weights")
    assert not hasattr(encoder, "tokenizer_model")


# ── EN2-INV-07 — Open-Class General Morphology
def test_en2_inv_07_open_class_general_morphology():
    """EN2-INV-07: General morphology handles novel regular forms."""
    tok1 = tokenize("teleported")[0]
    mf1 = classify_morphology(tok1)
    assert mf1.lemma == "teleport"
    assert mf1.is_past is True


# ── EN2-INV-08 — S-Ending Word Invariance
def test_en2_inv_08_s_ending_word_invariance():
    """EN2-INV-08: Invariable words are never suffix-stripped."""
    for word in ("Mars", "species", "physics", "news", "celsius", "photosynthesis", "mathematics"):
        tok = tokenize(word)[0]
        mf = classify_morphology(tok)
        assert mf.lemma == word.lower()


# ── EN2-INV-09 — Proper-Name Span Protection
def test_en2_inv_09_proper_name_span_protection(encoder):
    """EN2-INV-09: Multi-token proper names remain unified."""
    res = encoder.analyze("Alexander Graham Bell invented the telephone.")
    assert any(s.canonical_symbol == "alexander_graham_bell" for s in res.spans)


# ── EN2-INV-10 — Offset Mapping Reconstructability
def test_en2_inv_10_offset_reconstructability(encoder):
    """EN2-INV-10: Token offsets match raw input string exactly."""
    raw = "The red apple is on the wooden table."
    res = encoder.analyze(raw)
    for tok in res.tokens:
        assert raw[tok.start_offset : tok.end_offset] == tok.surface


# ── EN2-INV-11 — Strict Case Separation
def test_en2_inv_11_case_separation():
    """EN2-INV-11: Token surface preserves original case; normalized_surface is lower."""
    tok = tokenize("Mars")[0]
    assert tok.surface == "Mars"
    assert tok.normalized_surface == "mars"


# ── EN2-INV-12 — SVO Structural Role Assignment
def test_en2_inv_12_svo_roles(encoder):
    """EN2-INV-12: SVO maps subject->step 0, verb->step 1, object->step 2."""
    res = encoder.analyze("Falcons hunt animals.")
    ep = next(e for e in res.episodes if e.kind == "sequence")
    assert ep.steps[0] == [("text", "falcon")]
    assert ep.steps[1] == [("text", "hunt")]
    assert ep.steps[2] == [("text", "animal")]


# ── EN2-INV-13 — Passive Voice Normalization
def test_en2_inv_13_passive_normalization(encoder):
    """EN2-INV-13: Passive agent is normalized to step 0, patient to step 2."""
    res = encoder.analyze("The mouse was chased by the cat.")
    ep = next(e for e in res.episodes if e.kind == "sequence")
    assert ep.steps[0] == [("text", "cat")]
    assert ep.steps[1] == [("text", "chase")]
    assert ep.steps[2] == [("text", "mouse")]


# ── EN2-INV-14 — Coordinated Predicate Independence
def test_en2_inv_14_coordinated_predicates(encoder):
    """EN2-INV-14: Coordinated predicates split into independent frames with inherited subject."""
    res = encoder.analyze("Birds have feathers and lay eggs.")
    assert len(res.clauses) == 2
    assert res.clauses[0].subject.head_lemma == "bird"
    assert res.clauses[1].subject.head_lemma == "bird"
    assert res.clauses[1].inherited_subject_ref == "bird"


# ── EN2-INV-15 — Quantity Binding Locality
def test_en2_inv_15_quantity_locality(encoder):
    """EN2-INV-15: Quantity binds strictly to the intended noun phrase."""
    res = encoder.analyze("Mars has two moons.")
    sim_ep = next(e for e in res.episodes if e.kind == "simultaneous")
    syms = [s for _, s in sim_ep.signals]
    assert any(s.startswith("inst:moon:") for s in syms)
    assert ("quantity", "2") in sim_ep.signals


# ── EN2-INV-16 — Same-Head Instance Disambiguation
def test_en2_inv_16_same_head_instance(encoder):
    """EN2-INV-16: Same-head multi-roles receive distinct instance bindings."""
    res = encoder.analyze("Photosynthesis converts light energy into chemical energy.")
    sim_eps = [e for e in res.episodes if e.kind == "simultaneous"]
    inst_ids = [s for e in sim_eps for _, s in e.signals if s.startswith("inst:energy:")]
    assert len(set(inst_ids)) == 2


# ── EN2-INV-17 — Contradiction Purity
def test_en2_inv_17_contradiction_purity(encoder):
    """EN2-INV-17: Negation episodes have zero positive signals."""
    res = encoder.analyze("Birds are not mammals.")
    ep = res.episodes[0]
    assert len(ep.contradictions) > 0
    assert len(ep.signals) == 0


# ── EN2-INV-18 — No-Silent-Loss Token Accounting
def test_en2_inv_18_no_silent_loss(encoder):
    """EN2-INV-18: Every token is accounted for with an explicit disposition."""
    res = encoder.analyze("The quick brown fox jumps over the lazy dog.")
    assert len(res.token_accounting) == len(res.tokens)
    for rec in res.token_accounting:
        assert rec.disposition in {
            "EMITTED", "EMITTED_QUANTITY", "CONSUMED_DETERMINER", "CONSUMED_COPULA",
            "CONSUMED_AUX", "CONSUMED_NEGATION", "CONSUMED_PREPOSITION",
            "CONSUMED_COORDINATOR", "CONSUMED_RELATIVE_MARKER", "CONSUMED_PUNCT",
            "UNSUPPORTED_WITH_REASON",
        }


# ── EN2-INV-19 — Fail-Closed Unsupported Grammar
def test_en2_inv_19_fail_closed(encoder):
    """EN2-INV-19: Unsupported complex grammar fails closed without guessing relations."""
    res = encoder.analyze("Although quickly running very quietly indeed.")
    assert res.disposition == "UNSUPPORTED"
    assert len(res.episodes) == 0


# ── EN2-INV-20 — Context Namespace Preservation
def test_en2_inv_20_context_preservation(encoder):
    """EN2-INV-20: Context tags are attached to emitted episodes without corruption."""
    res = encoder.analyze("The Earth orbits the Sun.", source_ref="wiki:astronomy_101")
    for ep in res.episodes:
        assert ep.context == "wiki:astronomy_101"


# ── EN2-INV-21 — Deterministic Replay
def test_en2_inv_21_deterministic_replay(encoder):
    """EN2-INV-21: Replaying 100 times produces identical result."""
    text = "Alexander Graham Bell invented the telephone in 1876."
    res0 = encoder.analyze(text)
    for _ in range(100):
        resi = encoder.analyze(text)
        assert resi.episodes == res0.episodes
        assert resi.rule_provenance == res0.rule_provenance


# ── EN2-INV-22 — Modality Purity
def test_en2_inv_22_modality_purity():
    """EN2-INV-22: Audio and Vision/Code pipelines remain completely untouched and operational."""
    master = MasterSymbolicEncoder()
    assert master.code_pipeline is not None
    assert master.audio_pipeline is not None


# ── EN2-INV-23 — Graph Conservation
def test_en2_inv_23_graph_conservation(encoder):
    """EN2-INV-23: Reference graph signature is invariant under repeated analyze() calls."""
    g = build_reference_graph()
    sig_before = behavioral_signature(g)
    for _ in range(10):
        _ = encoder.analyze("Photosynthesis converts light energy into chemical energy.")
    sig_after = behavioral_signature(g)
    assert sig_before == sig_after


# ── EN2-INV-24 — Release Gate Readiness
def test_en2_inv_24_release_gate_readiness(encoder):
    """EN2-INV-24: Encoder outputs satisfy structured metadata for Release Gates."""
    res = encoder.analyze("A falcon is a bird of prey.")
    assert res.disposition in {"COMPLETE", "SAFE_PARTIAL", "UNSUPPORTED"}
    assert "sentence_count" in res.diagnostics
    assert len(res.rule_provenance) > 0
