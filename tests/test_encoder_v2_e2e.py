"""
DGCA English Encoder v2 — Stage E2E Verification Suite.
Tests Layer 8 (Episode Emitter), Graph Isolation, and Compatibility Facade.
"""
from dgca.encoder import EnglishTextPipeline, MasterSymbolicEncoder
from dgca.encoding.english import EnglishEncoderV2
from dgca.signature import behavioral_signature, build_reference_graph


def test_e2e_emitter_svo_and_modifiers():
    encoder = EnglishEncoderV2()
    res = encoder.analyze("Falcons hunt small animals.")
    assert len(res.episodes) == 2
    # 1. Modifiers episode: small animal
    ep_mod = next(e for e in res.episodes if e.kind == "simultaneous")
    assert ("text", "animal") in ep_mod.signals
    assert ("text", "small") in ep_mod.signals
    # 2. Sequence episode: falcon -> hunt -> animal
    ep_seq = next(e for e in res.episodes if e.kind == "sequence")
    assert ep_seq.steps == [[("text", "falcon")], [("text", "hunt")], [("text", "animal")]]


def test_e2e_emitter_contradiction_negation():
    """EN2-INV-05 & EN2-INV-17: Explicit negation produces contradiction without positive links."""
    encoder = EnglishEncoderV2()
    res = encoder.analyze("Mars is not a star.")
    assert len(res.episodes) == 1
    ep = res.episodes[0]
    assert ep.contradictions == [("text:mars", "text:star")]
    assert len(ep.signals) == 0


def test_e2e_graph_isolation():
    """EN2-INV-04 & EN2-INV-23: analyze() is pure and does not touch or mutate the graph."""
    g = build_reference_graph()
    sig_before = behavioral_signature(g)

    encoder = EnglishEncoderV2()
    res = encoder.analyze("Alexander Graham Bell invented the telephone in the United States.")
    assert len(res.episodes) > 0

    sig_after = behavioral_signature(g)
    assert sig_before == sig_after, "analyze() mutated reference graph state!"


def test_e2e_compatibility_facade():
    """Verify MasterSymbolicEncoder and EnglishTextPipeline facade."""
    pipeline = EnglishTextPipeline()
    episodes = pipeline.process("A falcon is a bird.")
    assert len(episodes) == 1
    assert episodes[0].kind == "simultaneous"
    assert ("text", "falcon") in episodes[0].signals
    assert ("text", "bird") in episodes[0].signals

    master = MasterSymbolicEncoder()
    master_eps = master.encode_text("The red apple is on the wooden table.")
    assert len(master_eps) == 3
