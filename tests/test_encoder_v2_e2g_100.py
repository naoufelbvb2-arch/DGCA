"""
DGCA English Encoder v2 — Stage E2G: 100 Natural English Sentences Evaluation.
Verifies accuracy, No-Silent-Loss, and deterministic replay against the frozen gold dataset.
Required: >= 90% PASS (Target: 100 / 100 PASS).
"""
import json
from pathlib import Path

import pytest

from dgca.encoding.english import EnglishEncoderV2


@pytest.fixture
def gold_dataset():
    data_path = Path(__file__).parent / "data_encoder_v2_gold_100.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def encoder():
    return EnglishEncoderV2()


def test_e2g_100_sentences_accuracy(encoder, gold_dataset):
    assert len(gold_dataset) == 100
    passed = 0
    failures = []

    for item in gold_dataset:
        sid = item["id"]
        text = item["text"]
        expected_disp = item["disposition"]
        expected_heads = item["heads"]
        is_neg = item["negated"]

        res = encoder.analyze(text)

        # 1. Check disposition
        if res.disposition != expected_disp:
            failures.append(f"{sid}: disposition mismatch (got {res.disposition}, expected {expected_disp})")
            continue

        # 2. Check negation
        actual_neg = any(c.negated for c in res.clauses) if res.clauses else (len(res.episodes) > 0 and len(res.episodes[0].contradictions) > 0)
        if actual_neg != is_neg:
            failures.append(f"{sid}: negation mismatch (got {actual_neg}, expected {is_neg})")
            continue

        # 3. Check heads present in analysis
        emitted_heads = set()
        for f in res.clauses:
            if f.subject:
                emitted_heads.add(f.subject.head_lemma)
            if f.object:
                emitted_heads.add(f.object.head_lemma)
            for _, pobj in f.prepositional_relations:
                emitted_heads.add(pobj.head_lemma)
            for dep in f.dependent_clauses:
                if dep.subject:
                    emitted_heads.add(dep.subject.head_lemma)
                if dep.object:
                    emitted_heads.add(dep.object.head_lemma)
                for _, dpobj in dep.prepositional_relations:
                    emitted_heads.add(dpobj.head_lemma)

        # Also check single copular properties where subject is the only head
        all_lemmas = emitted_heads.union({t.normalized_surface for t in res.tokens})
        missing_heads = [h for h in expected_heads if h not in emitted_heads and h not in all_lemmas]
        if missing_heads:
            failures.append(f"{sid}: missing heads {missing_heads} (emitted: {emitted_heads})")
            continue

        # 4. Check No-Silent-Loss
        assert len(res.token_accounting) == len(res.tokens)

        # 5. Deterministic replay
        res_replay = encoder.analyze(text)
        assert res.episodes == res_replay.episodes

        passed += 1

    accuracy = passed / len(gold_dataset)
    assert passed >= 90, f"Stage E2G accuracy {accuracy:.1%} below 90% threshold! Failures: {failures[:10]}"
    assert passed == 100, f"Stage E2G passed {passed}/100 sentences. Failures: {failures}"
