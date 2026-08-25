"""
DGCA Phase 2.5 — Real-Data Trial 01 Main Training and Longitudinal Evaluation Runner.
Executes the cumulative one-pass main training ladder:
M0 -> M1K -> M10K -> M50K -> M100K -> MFULL
Runs frozen 420-probe bank against disposable evaluation clones at each checkpoint.
Captures exact raw responses, retention cohort K1 longitudinal tracking, and telemetry.
"""
import gc
import json
import os
import sys
import time

import psutil
import pyarrow.parquet as pq

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dgca.graph import CognitiveGraph
from scripts.trial01_harness import (
    Trial01IngestionEngine,
    compute_graph_state_digest,
    create_evaluation_clone,
    evaluate_probe_bank,
)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MANIFEST_DIR = os.path.join(DATA_DIR, "manifests")
CHECKPOINT_DIR = os.path.join(DATA_DIR, "checkpoints")
RESPONSES_DIR = os.path.join(DATA_DIR, "raw_responses")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs(RESPONSES_DIR, exist_ok=True)

DATASET_FILE = os.path.join(DATA_DIR, "simplewiki_20231101.parquet")
DATASET_SNAPSHOT_ID = "wikimedia/wikipedia/20231101.simple"
FROZEN_SHA256 = "31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0"


def execute_main_trial():
    print("======================================================================")
    print("DGCA Phase 2.5 — Real-Data Trial 01: Main Execution Ladder")
    print("======================================================================")
    process = psutil.Process(os.getpid())

    # 1. Load manifests
    print("Loading manifests...")
    with open(os.path.join(MANIFEST_DIR, "ordered_train_ids.json"), "r", encoding="utf-8") as f:
        ordered_train_ids = json.load(f)
    with open(os.path.join(MANIFEST_DIR, "frozen_420_probe_bank.json"), "r", encoding="utf-8") as f:
        probe_bank = json.load(f)

    print(f"Total ordered Train articles to process: {len(ordered_train_ids)}")
    print(f"Total frozen evaluation probes: {len(probe_bank)}")

    # Load dataset table indexed by ID
    print("Loading dataset table...")
    table = pq.read_table(DATASET_FILE)
    id_col = table["id"].to_pylist()
    title_col = table["title"].to_pylist()
    text_col = table["text"].to_pylist()

    id_to_idx = {str(id_col[i]): i for i in range(len(id_col))}
    print("Dataset index mapped.")

    # 2. Establish clean M0
    print("\n--- Establishing clean baseline M0 ---")
    clean_m0 = CognitiveGraph()
    m0_digest = compute_graph_state_digest(clean_m0)
    print(f"Clean M0 persistent state digest: {m0_digest}")

    engine = Trial01IngestionEngine(clean_m0)

    checkpoint_targets = [
        ("M0", 0),
        ("M1K", 1000),
        ("M10K", 10000),
        ("M50K", 50000),
        ("M100K", 100000),
        ("MFULL", len(ordered_train_ids)),
    ]

    checkpoint_records: list[dict] = []
    all_raw_responses: dict[str, list[dict]] = {}
    retention_cohort_k1: list[dict] = []

    # Helper function to evaluate and save checkpoint
    def process_checkpoint(name: str, current_count: int, interval_start_time: float):
        nonlocal retention_cohort_k1
        time.perf_counter()
        digest = compute_graph_state_digest(engine.graph)
        ram_mb = process.memory_info().rss / (1024 * 1024)

        n_nodes = len(engine.graph.nodes)
        n_edges = len(engine.graph.edges)
        n_asms = len(engine.graph.assembly_manager.live_assemblies()) if engine.graph._assembly_manager else 0
        density = (n_edges / (n_nodes * (n_nodes - 1))) if n_nodes > 1 else 0.0

        degrees = [len(engine.graph.out_adj.get(n, {})) + len(engine.graph.in_adj.get(n, {})) for n in engine.graph.nodes]
        avg_deg = sum(degrees) / len(degrees) if degrees else 0.0
        max_deg = max(degrees) if degrees else 0

        ingestion_yield = (engine.telemetry["learning_effects"] / max(1, engine.telemetry["valid_segments"]))
        learning_density_1k = (engine.telemetry["learning_effects"] / max(1, engine.telemetry["words_processed"])) * 1000.0

        print("\n======================================================================")
        print(f"CHECKPOINT REACHED: {name} (Articles: {current_count})")
        print(f"State Digest: {digest}")
        print(f"Graph State: Nodes={n_nodes}, Edges={n_edges}, Assemblies={n_asms}, Density={density:.6f}, AvgDeg={avg_deg:.2f}, MaxDeg={max_deg}")
        print(f"Telemetry: Segments={engine.telemetry['valid_segments']}, Words={engine.telemetry['words_processed']}, IngestionYield={ingestion_yield:.4f}")
        print(f"Resources: RAM={ram_mb:.2f} MB, CPU Time={engine.telemetry['cpu_time_sec']:.2f} s, Wall Clock={engine.telemetry['wall_clock_sec']:.2f} s")
        print("======================================================================")

        # Save serialized checkpoint
        cp_path = os.path.join(CHECKPOINT_DIR, f"{name}.json")
        with open(cp_path, "w", encoding="utf-8") as f:
            json.dump(engine.graph.to_dict(), f)
        cp_size_kb = os.path.getsize(cp_path) / 1024.0

        # Create evaluation clone
        print(f"Creating read-only evaluation clone for {name}...")
        clone_g = create_evaluation_clone(engine.graph)

        print(f"Evaluating 420 frozen probes on {name} clone...")
        bank_results, raw_records = evaluate_probe_bank(clone_g, probe_bank, name)
        del clone_g
        gc.collect()

        # Save raw responses
        resp_path = os.path.join(RESPONSES_DIR, f"{name}_raw_responses.json")
        with open(resp_path, "w", encoding="utf-8") as f:
            json.dump(raw_records, f, indent=2)
        all_raw_responses[name] = raw_records

        # Freeze retention cohort K1 at M1K
        if name == "M1K":
            retention_cohort_k1 = [
                r for r in raw_records
                if r["bank"] == "Bank A — Learned Fact Recall" and r["stored"]
            ][:30]
            print(f"Frozen retention cohort K1 with {len(retention_cohort_k1)} verified acquired facts.")

        # Evaluate retention cohort K1 if established
        retention_score = 0.0
        if retention_cohort_k1:
            k1_ids = {r["probe_id"] for r in retention_cohort_k1}
            current_k1_recs = [r for r in raw_records if r["probe_id"] in k1_ids]
            retained_count = sum(1 for r in current_k1_recs if r["stored"])
            retention_score = retained_count / len(retention_cohort_k1)
            print(f"Retention Cohort K1 Score: {retained_count}/{len(retention_cohort_k1)} ({retention_score*100:.1f}%)")

        # Verify source graph digest unchanged
        digest_after = compute_graph_state_digest(engine.graph)
        assert digest == digest_after, "FATAL: Evaluation mutated source training graph!"

        cp_record = {
            "checkpoint": name,
            "articles_count": current_count,
            "state_digest": digest,
            "nodes": n_nodes,
            "edges": n_edges,
            "assemblies": n_asms,
            "density": density,
            "avg_degree": avg_deg,
            "max_degree": max_deg,
            "ram_mb": ram_mb,
            "checkpoint_size_kb": cp_size_kb,
            "wall_clock_sec": engine.telemetry["wall_clock_sec"],
            "cpu_time_sec": engine.telemetry["cpu_time_sec"],
            "words_processed": engine.telemetry["words_processed"],
            "valid_segments": engine.telemetry["valid_segments"],
            "learning_effects": engine.telemetry["learning_effects"],
            "ingestion_yield": ingestion_yield,
            "learning_density_1k": learning_density_1k,
            "bank_results": bank_results,
            "retention_k1_score": retention_score,
        }
        checkpoint_records.append(cp_record)

    # Initial M0 evaluation
    t_start_total = time.perf_counter()
    process_checkpoint("M0", 0, t_start_total)

    # Main cumulative loop
    article_idx = 0
    total_articles = len(ordered_train_ids)

    for cp_name, cp_target in checkpoint_targets[1:]:
        t_interval_start = time.perf_counter()
        print(f"\n>>> Starting acquisition toward {cp_name} (Target: {cp_target} articles) <<<")

        while article_idx < cp_target and article_idx < total_articles:
            aid = ordered_train_ids[article_idx]
            row_idx = id_to_idx[aid]
            title = str(title_col[row_idx])
            text = str(text_col[row_idx])

            engine.ingest_article(aid, title, text)
            article_idx += 1

            if article_idx % 250 == 0:
                cur_ram = process.memory_info().rss / (1024 * 1024)
                rate = article_idx / max(0.001, engine.telemetry["wall_clock_sec"])
                print(f"  Processed {article_idx}/{cp_target} articles ({article_idx/total_articles*100:.1f}%) | Nodes: {len(engine.graph.nodes)} | Edges: {len(engine.graph.edges)} | Rate: {rate:.1f} art/s | RAM: {cur_ram:.1f} MB")

        # Process reached checkpoint
        process_checkpoint(cp_name, article_idx, t_interval_start)

    # Save complete checkpoint summary
    summary_path = os.path.join(DATA_DIR, "trial01_execution_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(checkpoint_records, f, indent=2)

    print("\n======================================================================")
    print("DGCA Phase 2.5 Real-Data Trial 01 Main Execution Ladder COMPLETE!")
    print(f"Summary saved to: {summary_path}")
    print("======================================================================")
    return checkpoint_records


if __name__ == "__main__":
    execute_main_trial()
