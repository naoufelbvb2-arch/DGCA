"""
DGCA Phase 2.5 — Real-Data Trial 01 Manifest and Probe Bank Builder.
Constructs:
1. Train / Held-Out deterministic split manifest (90% Train / 10% HeldOut)
2. Deterministic training order manifest
3. 100-article Pilot selection manifest
4. 420-Probe Evaluation Bank (Banks A, B, C, D, E)
"""
import hashlib
import json
import os
import re
import struct

import pyarrow.parquet as pq

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MANIFEST_DIR = os.path.join(DATA_DIR, "manifests")
os.makedirs(MANIFEST_DIR, exist_ok=True)

DATASET_FILE = os.path.join(DATA_DIR, "simplewiki_20231101.parquet")
DATASET_SNAPSHOT_ID = "wikimedia/wikipedia/20231101.simple"
FROZEN_SHA256 = "31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0"


def compute_split_hash(article_id: str) -> tuple[str, bool]:
    """h_i = SHA256("RDT01-SPLIT-v1\\0" || ArticleID_i)
    u_i = unsigned int from first 8 bytes
    HeldOut iff u_i % 10 == 0
    """
    prefix = b"RDT01-SPLIT-v1\x00"
    digest = hashlib.sha256(prefix + article_id.encode("utf-8")).digest()
    u_i = struct.unpack(">Q", digest[:8])[0]
    is_heldout = (u_i % 10 == 0)
    return digest.hex(), is_heldout


def compute_order_hash(article_id: str) -> str:
    """o_i = SHA256("RDT01-ORDER-v1\\0" || ArticleID_i)"""
    prefix = b"RDT01-ORDER-v1\x00"
    return hashlib.sha256(prefix + article_id.encode("utf-8")).hexdigest()


def compute_pilot_hash(article_id: str) -> str:
    """p_i = SHA256("RDT01-PILOT-v1\\0" || ArticleID_i)"""
    prefix = b"RDT01-PILOT-v1\x00"
    return hashlib.sha256(prefix + article_id.encode("utf-8")).hexdigest()


def build_manifests():
    print("======================================================================")
    print("Building DGCA Phase 2.5 Real-Data Trial 01 Manifests")
    print("======================================================================")
    table = pq.read_table(DATASET_FILE)
    n_rows = table.num_rows
    print(f"Total rows in dataset: {n_rows}")

    ids = table["id"].to_pylist()
    titles = table["title"].to_pylist()
    texts = table["text"].to_pylist()

    train_articles = []
    heldout_articles = []

    print("Partitioning Train / HeldOut...")
    for idx in range(n_rows):
        aid = str(ids[idx])
        split_h, is_heldout = compute_split_hash(aid)
        order_h = compute_order_hash(aid)
        pilot_h = compute_pilot_hash(aid)
        item = {
            "row_index": idx,
            "id": aid,
            "title": titles[idx],
            "split_hash": split_h,
            "order_hash": order_h,
            "pilot_hash": pilot_h,
        }
        if is_heldout:
            heldout_articles.append(item)
        else:
            train_articles.append(item)

    print(f"Train partition count: {len(train_articles)} ({len(train_articles)/n_rows*100:.2f}%)")
    print(f"HeldOut partition count: {len(heldout_articles)} ({len(heldout_articles)/n_rows*100:.2f}%)")

    # Sort train articles by order_hash
    print("Sorting Train articles by deterministic order hash...")
    train_articles.sort(key=lambda x: (x["order_hash"], x["id"]))

    # Sort train articles by pilot_hash to select 100 pilot articles
    print("Selecting 100 deterministic Pilot articles...")
    pilot_candidates = list(train_articles)
    pilot_candidates.sort(key=lambda x: (x["pilot_hash"], x["id"]))
    pilot_articles = pilot_candidates[:100]

    # Save partition manifest summary
    partition_manifest = {
        "dataset_snapshot_id": DATASET_SNAPSHOT_ID,
        "dataset_sha256": FROZEN_SHA256,
        "total_rows": n_rows,
        "train_count": len(train_articles),
        "heldout_count": len(heldout_articles),
        "train_article_ids_sample": [x["id"] for x in train_articles[:10]],
        "heldout_article_ids_sample": [x["id"] for x in heldout_articles[:10]],
    }
    with open(os.path.join(MANIFEST_DIR, "train_heldout_summary.json"), "w", encoding="utf-8") as f:
        json.dump(partition_manifest, f, indent=2)

    # Save ordered train article ids list
    ordered_train_ids = [x["id"] for x in train_articles]
    with open(os.path.join(MANIFEST_DIR, "ordered_train_ids.json"), "w", encoding="utf-8") as f:
        json.dump(ordered_train_ids, f)

    # Save pilot manifest
    pilot_manifest = {
        "dataset_snapshot_id": DATASET_SNAPSHOT_ID,
        "pilot_count": len(pilot_articles),
        "articles": [
            {
                "id": x["id"],
                "title": x["title"],
                "row_index": x["row_index"],
                "pilot_hash": x["pilot_hash"],
            }
            for x in pilot_articles
        ],
    }
    with open(os.path.join(MANIFEST_DIR, "pilot_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(pilot_manifest, f, indent=2)

    print("Manifests created successfully.")
    return train_articles, heldout_articles, pilot_articles, ids, titles, texts


def build_probe_bank(train_articles, heldout_articles, ids, titles, texts):
    print("======================================================================")
    print("Building Pre-Registered 420-Probe Evaluation Bank")
    print("======================================================================")
    {str(ids[i]): i for i in range(len(ids))}

    # We need:
    # Bank A: 100 Learned Fact Recall (from early Train articles, e.g. M1K)
    # Bank B: 100 Paraphrased Recall (from same/related Train articles)
    # Bank C: 100 Compositional Reasoning (from multi-relation pairs in Train articles)
    # Bank D: 100 Held-Out Behavior (from HeldOut articles)
    # Bank E: 20 Free Generation (fixed open-ended prompts)

    # Fixed Bank E: 20 Free Generation prompts
    bank_e_prompts = [
        "What is an eagle?",
        "Explain how rain forms.",
        "What is biology?",
        "What is a star?",
        "Describe a lion.",
        "What is water?",
        "How does a car work?",
        "What is mathematics?",
        "What is a tree?",
        "Explain music.",
        "What is a mammal?",
        "What is the sun?",
        "Describe the ocean.",
        "What is a computer?",
        "What is history?",
        "Explain the solar system.",
        "What is energy?",
        "What is a bird?",
        "What is physics?",
        "What is a river?",
    ]

    probes = []
    probe_id_counter = 1

    # Build Bank E (20 probes)
    print("Constructing Bank E: 20 Free Generation Probes...")
    for prompt in bank_e_prompts:
        probes.append({
            "probe_id": f"RDT01-PROBE-E{probe_id_counter:03d}",
            "bank": "Bank E — Free Generation",
            "prompt": prompt,
            "source_article_ids": [],
            "source_segment_citations": [],
            "expected_semantic_anchors": [prompt.split()[2].rstrip("?").lower() if len(prompt.split()) > 2 else "concept"],
            "provenance": "OPEN_EVALUATION",
            "grading_rule": "RAW_LONGITUDINAL_INSPECTION_AND_CLOSURE_VERIFICATION",
        })
        probe_id_counter += 1

    # Extract factual statements from early Train articles (first 1,000 articles for Bank A, B, C)
    print("Extracting fact candidates from early Train articles for Banks A, B, C...")
    train_facts = []
    for t_item in train_articles[:2000]:
        idx = t_item["row_index"]
        aid = t_item["id"]
        title = t_item["title"]
        text = texts[idx]
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]
        for s in sentences[:5]:
            # Look for copula / is-a / has / action patterns
            m = re.match(r"^([A-Z][a-zA-Z\s]{2,25})\s+(is|are|was|were)\s+(?:a|an|the)?\s*([a-zA-Z\s]{3,30})[.,]", s)
            if m:
                subj = m.group(1).strip()
                copula = m.group(2).strip()
                obj = m.group(3).strip()
                if len(subj.split()) <= 3 and len(obj.split()) <= 4:
                    train_facts.append({
                        "article_id": aid,
                        "title": title,
                        "sentence": s,
                        "subject": subj,
                        "copula": copula,
                        "object": obj,
                    })
            if len(train_facts) >= 300:
                break
        if len(train_facts) >= 300:
            break

    print(f"Extracted {len(train_facts)} Train fact candidates.")

    # Bank A: 100 Learned Fact Recall
    print("Constructing Bank A: 100 Learned Fact Recall Probes...")
    for i in range(100):
        fact = train_facts[i % len(train_facts)]
        subj = fact["subject"]
        obj = fact["object"]
        probes.append({
            "probe_id": f"RDT01-PROBE-A{i+1:03d}",
            "bank": "Bank A — Learned Fact Recall",
            "prompt": f"What {fact['copula']} {subj}?",
            "source_article_ids": [fact["article_id"]],
            "source_segment_citations": [fact["sentence"]],
            "expected_semantic_anchors": [subj.lower(), obj.lower().split()[-1]],
            "provenance": "TRAIN_M1K_COHORT",
            "grading_rule": "STORED_AND_RETRIEVABLE_ANCHOR_MATCH",
        })

    # Bank B: 100 Paraphrased Recall
    print("Constructing Bank B: 100 Paraphrased Recall Probes...")
    for i in range(100):
        fact = train_facts[(i + 50) % len(train_facts)]
        subj = fact["subject"]
        obj = fact["object"]
        probes.append({
            "probe_id": f"RDT01-PROBE-B{i+1:03d}",
            "bank": "Bank B — Paraphrased Recall",
            "prompt": f"Can you describe {subj} and its classification?",
            "source_article_ids": [fact["article_id"]],
            "source_segment_citations": [fact["sentence"]],
            "expected_semantic_anchors": [subj.lower(), obj.lower().split()[-1]],
            "provenance": "TRAIN_M1K_COHORT",
            "grading_rule": "PARAPHRASED_CUE_RETRIEVAL_MATCH",
        })

    # Bank C: 100 Compositional Reasoning
    print("Constructing Bank C: 100 Compositional Reasoning Probes...")
    for i in range(100):
        f1 = train_facts[i % len(train_facts)]
        f2 = train_facts[(i + 1) % len(train_facts)]
        probes.append({
            "probe_id": f"RDT01-PROBE-C{i+1:03d}",
            "bank": "Bank C — Compositional Reasoning",
            "prompt": f"If {f1['subject']} relates to {f1['object']}, how does {f1['subject']} relate to {f2['subject']}?",
            "source_article_ids": [f1["article_id"], f2["article_id"]],
            "source_segment_citations": [f1["sentence"], f2["sentence"]],
            "expected_semantic_anchors": [f1["subject"].lower(), f1["object"].lower().split()[-1]],
            "provenance": "TRAIN_MULTI_RELATION",
            "grading_rule": "MULTI_RELATION_TRAVERSAL_OR_COMPLETION",
        })

    # Bank D: 100 Held-Out Behavior
    print("Extracting fact candidates from HeldOut articles for Bank D...")
    heldout_facts = []
    for h_item in heldout_articles[:1000]:
        idx = h_item["row_index"]
        aid = h_item["id"]
        title = h_item["title"]
        text = texts[idx]
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]
        for s in sentences[:5]:
            m = re.match(r"^([A-Z][a-zA-Z\s]{2,25})\s+(is|are|was|were)\s+(?:a|an|the)?\s*([a-zA-Z\s]{3,30})[.,]", s)
            if m:
                subj = m.group(1).strip()
                copula = m.group(2).strip()
                obj = m.group(3).strip()
                if len(subj.split()) <= 3 and len(obj.split()) <= 4:
                    heldout_facts.append({
                        "article_id": aid,
                        "title": title,
                        "sentence": s,
                        "subject": subj,
                        "copula": copula,
                        "object": obj,
                    })
            if len(heldout_facts) >= 150:
                break
        if len(heldout_facts) >= 150:
            break

    print("Constructing Bank D: 100 Held-Out Probes...")
    for i in range(100):
        h_fact = heldout_facts[i % len(heldout_facts)]
        probes.append({
            "probe_id": f"RDT01-PROBE-D{i+1:03d}",
            "bank": "Bank D — Held-Out Behavior",
            "prompt": f"What {h_fact['copula']} {h_fact['subject']} in held-out context?",
            "source_article_ids": [h_fact["article_id"]],
            "source_segment_citations": [h_fact["sentence"]],
            "expected_semantic_anchors": [h_fact["subject"].lower(), h_fact["object"].lower().split()[-1]],
            "provenance": "HELDOUT_NON_TRAINING",
            "grading_rule": "HELDOUT_UNCERTAINTY_OR_ZERO_SHOT_MEASUREMENT",
        })

    print(f"Total frozen evaluation probes constructed: {len(probes)}")
    assert len(probes) == 420, f"Expected exactly 420 probes, got {len(probes)}"

    probe_bank_path = os.path.join(MANIFEST_DIR, "frozen_420_probe_bank.json")
    with open(probe_bank_path, "w", encoding="utf-8") as f:
        json.dump(probes, f, indent=2)

    print(f"Frozen probe bank saved to: {probe_bank_path}")
    return probes


if __name__ == "__main__":
    train_articles, heldout_articles, pilot_articles, ids, titles, texts = build_manifests()
    build_probe_bank(train_articles, heldout_articles, ids, titles, texts)
