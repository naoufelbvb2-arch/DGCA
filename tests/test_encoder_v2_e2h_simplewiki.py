"""
DGCA English Encoder v2 — Stage E2H: Simple Wikipedia Empirical Evaluation (200 Sentences).
Tests real natural sentences from simplewiki_20231101.parquet under graph-free, learning-free execution.
GraphLearning = OFF, Law 3 OUT OF PATH.
"""
import json
from pathlib import Path

import pytest

from dgca.encoding.english import EnglishEncoderV2
from dgca.signature import behavioral_signature, build_reference_graph


@pytest.fixture(scope="module")
def wiki_sentences():
    json_path = Path(__file__).parent / "data_simplewiki_sample_200.json"
    if not json_path.exists():
        pytest.skip("Simple Wikipedia sample json file not found")

    with open(json_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    assert len(sentences) == 200
    return sentences


def test_e2h_simplewiki_graph_conservation_and_robustness(wiki_sentences):
    encoder = EnglishEncoderV2()
    g = build_reference_graph()
    sig_before = behavioral_signature(g)
    n_nodes_before = len(g.nodes)
    n_edges_before = len(g.edges)

    dispositions = {"COMPLETE": 0, "SAFE_PARTIAL": 0, "UNSUPPORTED": 0}
    total_tokens = 0
    accounted_tokens = 0

    for i, sent in enumerate(wiki_sentences):
        # 1. Non-crashing execution
        res = encoder.analyze(sent, source_ref=f"wiki:test_{i}")
        dispositions[res.disposition] += 1

        # 2. Reconstructability check
        for tok in res.tokens:
            raw_slice = sent[tok.start_offset : tok.end_offset]
            assert raw_slice == tok.surface

        # 3. No-Silent-Loss Token Accounting
        total_tokens += len(res.tokens)
        accounted_tokens += len(res.token_accounting)
        assert len(res.token_accounting) == len(res.tokens)

        # 4. Context namespace preservation
        for ep in res.episodes:
            assert ep.context == f"wiki:test_{i}"

        # 5. Deterministic replay check
        res_replay = encoder.analyze(sent, source_ref=f"wiki:test_{i}")
        assert res.episodes == res_replay.episodes

    # 6. Graph conservation check (Zero mutations)
    sig_after = behavioral_signature(g)
    assert sig_before == sig_after
    assert len(g.nodes) == n_nodes_before
    assert len(g.edges) == n_edges_before
    assert accounted_tokens == total_tokens
