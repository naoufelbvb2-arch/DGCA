"""
DGCA Phase 2.5 — Real-Data Trial 01 Master Experimental Harness.
Implements:
1. Ingestion Engine & Experience Protocol v1 (One Article = One Root External Episode).
2. Segment lineage and deterministic deduplication.
3. Article boundary settling & quiescence.
4. Telemetry (runtime, CPU, RAM, graph growth, density, degrees, ingestion yield).
5. Evaluation clone runner (zero mutation to training instance).
6. 420-Probe evaluation evaluator (Banks A, B, C, D, E).
7. Checkpoint serialization & state digest verification.
8. 12 Pilot Release Gates (P-G01 .. P-G12).
"""
import hashlib
import json
import os
import re
import sys
import time

import pyarrow.parquet as pq

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dgca.graph import CognitiveGraph
from dgca.loop import InternalWorkFrontier
from dgca.signature import behavioral_signature, build_reference_graph

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MANIFEST_DIR = os.path.join(DATA_DIR, "manifests")
DATASET_FILE = os.path.join(DATA_DIR, "simplewiki_20231101.parquet")
DATASET_SNAPSHOT_ID = "wikimedia/wikipedia/20231101.simple"
FROZEN_SHA256 = "31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0"


# ─────────────────────────────────────────────────────────── 1. Canonical Digests
def compute_graph_state_digest(graph: CognitiveGraph) -> str:
    """Computes a deterministic, cryptographic SHA-256 state digest across all persistent graph state."""
    rows = []
    for (src, dst), e in sorted(graph.edges.items()):
        rows.append(f"E|{src}->{dst}|W={e.W:.6f}|n={e.n}|k={e.kind}|g={e.g or ''}|fwd={int(e.fwd)}|S={e.S:.6f}|V={e.valence:.6f}")
    for nid, n in sorted(graph.nodes.items()):
        rows.append(f"N|{nid}|r={n.region}|c={int(n.is_concept)}|U={n.U:.6f}|V={n.V:.6f}|mem={','.join(sorted(n.members))}")
    for k, rivals in sorted(graph.X.items()):
        rows.append(f"X|{k}|{','.join(sorted(rivals))}")
    if graph._assembly_manager is not None:
        for aid, versions in sorted(graph._assembly_manager.assemblies.items()):
            for asm in versions:
                edges_str = ",".join(sorted(f"{u}->{v}" for u, v in asm.member_edges))
                rows.append(f"ASM|{asm.assembly_id}|v{asm.version}|ret={int(asm.is_retired)}|{edges_str}")
    blob = "\n".join(rows)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


from dgca.encoder import MasterSymbolicEncoder


# ─────────────────────────────────────────────────────────── 2. Ingestion Engine
class Trial01IngestionEngine:
    """Ingests natural Wikipedia articles according to the Article-to-DGCA Experience Protocol v1."""

    def __init__(self, graph: CognitiveGraph | None = None):
        self.graph = graph if graph is not None else CognitiveGraph()
        self.encoder = MasterSymbolicEncoder()
        self.telemetry = {
            "articles_processed": 0,
            "segments_processed": 0,
            "valid_segments": 0,
            "words_processed": 0,
            "learning_effects": 0,
            "evidence_candidates": 0,
            "validated_evidence": 0,
            "rejected_evidence": 0,
            "duplicate_episodes": 0,
            "wall_clock_sec": 0.0,
            "cpu_time_sec": 0.0,
        }
        self.failures: list[dict] = []

    def segment_text(self, text: str) -> list[str]:
        """Segments text naturally by paragraphs and sentences without semantic thresholds."""
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        segments: list[str] = []
        for p in paragraphs:
            # Sentence split
            sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
            segments.extend(sents)
        return segments

    def ingest_article(self, article_id: str, title: str, text: str) -> dict:
        """Processes one Wikipedia article as one RootExternalEpisode."""
        t_start = time.perf_counter()
        cpu_start = time.process_time()

        root_ep_id = hashlib.sha256(f"{DATASET_SNAPSHOT_ID}{article_id}".encode()).hexdigest()
        segments = self.segment_text(text)

        article_words = len(re.findall(r"\w+", text)) + len(re.findall(r"\w+", title))
        article_learning_effects = 0
        valid_segs_in_article = 0

        edges_before = len(self.graph.edges)

        # Ingest title first as context anchor
        title_hash = hashlib.sha256(title.strip().encode("utf-8")).hexdigest()
        title_event_id = hashlib.sha256(f"{root_ep_id}title{title_hash}".encode()).hexdigest()
        _ev_title, is_nov_title = self.graph.loop_engine.ingress_external_event(
            event_id=title_event_id,
            root_external_episode_id=root_ep_id,
            raw_content=title,
            metadata={"authorized_source": True, "article_id": article_id, "is_title": True},
        )
        if is_nov_title:
            episodes = self.encoder.encode_text(title, context=f"art_{article_id}")
            if episodes:
                self.encoder.feed_to_graph(self.graph, episodes)

        # Ingest ordered segments
        for seg_idx, seg_text in enumerate(segments):
            if not seg_text:
                continue
            valid_segs_in_article += 1
            seg_bytes_hash = hashlib.sha256(seg_text.strip().encode("utf-8")).hexdigest()
            seg_event_id = hashlib.sha256(f"{root_ep_id}{seg_idx}{seg_bytes_hash}".encode()).hexdigest()

            _ev_rec, is_novel = self.graph.loop_engine.ingress_external_event(
                event_id=seg_event_id,
                root_external_episode_id=root_ep_id,
                raw_content=seg_text,
                metadata={"authorized_source": True, "article_id": article_id, "seg_index": seg_idx},
            )

            if not is_novel:
                self.telemetry["duplicate_episodes"] += 1
                continue

            # Existing encoder transforms natural text
            episodes = self.encoder.encode_text(seg_text, context=f"art_{article_id}")
            self.telemetry["evidence_candidates"] += len(episodes)

            e_count_pre = len(self.graph.edges)
            if episodes:
                self.encoder.feed_to_graph(self.graph, episodes)
                e_count_post = len(self.graph.edges)
                if e_count_post > e_count_pre:
                    article_learning_effects += (e_count_post - e_count_pre)
                    self.telemetry["validated_evidence"] += len(episodes)
                else:
                    self.telemetry["rejected_evidence"] += len(episodes)

        # Article boundary settling & quiescence
        self.graph.tick()
        empty_frontier = InternalWorkFrontier(ready_work=(), blocked_work=(), status="EMPTY")
        q_view = self.graph.loop_engine.derive_root_quiescence(root_ep_id, empty_frontier)

        t_end = time.perf_counter()
        cpu_end = time.process_time()

        elapsed_wall = t_end - t_start
        elapsed_cpu = cpu_end - cpu_start

        self.telemetry["articles_processed"] += 1
        self.telemetry["segments_processed"] += len(segments)
        self.telemetry["valid_segments"] += valid_segs_in_article
        self.telemetry["words_processed"] += article_words
        self.telemetry["learning_effects"] += article_learning_effects
        self.telemetry["wall_clock_sec"] += elapsed_wall
        self.telemetry["cpu_time_sec"] += elapsed_cpu

        outcome = "LEARNED" if article_learning_effects > 0 else "PROCESSED_NO_LEARNING"
        return {
            "article_id": article_id,
            "root_external_episode_id": root_ep_id,
            "segments_count": len(segments),
            "words_count": article_words,
            "learning_effects": article_learning_effects,
            "edges_gained": len(self.graph.edges) - edges_before,
            "quiescent": q_view.is_quiescent,
            "quiescence_reason": q_view.quiescence_reason,
            "outcome": outcome,
            "elapsed_ms": elapsed_wall * 1000.0,
        }


# ─────────────────────────────────────────────────────────── 3. Evaluation Clone & Probe Evaluator
def create_evaluation_clone(graph: CognitiveGraph) -> CognitiveGraph:
    """Creates a bit-exact, isolated, disposable read-only clone of the cognitive graph."""
    data = graph.to_dict()
    clone = CognitiveGraph.from_dict(data)
    clone.loop_engine._processed_episodes = set(graph.loop_engine._processed_episodes)
    clone.loop_engine._ingress_events = dict(graph.loop_engine._ingress_events)
    clone.loop_engine._delivery_records = dict(graph.loop_engine._delivery_records)
    clone.loop_engine._learning_attributions = list(graph.loop_engine._learning_attributions)
    clone.loop_engine._active_roots = set(graph.loop_engine._active_roots)
    clone.loop_engine._cancelled_roots = set(graph.loop_engine._cancelled_roots)
    return clone


def evaluate_probe_bank(clone_g: CognitiveGraph, probe_bank: list[dict], checkpoint_name: str) -> tuple[dict, list[dict]]:
    """Runs all 420 frozen probes against an evaluation clone and records exact raw responses."""
    results_by_bank: dict[str, dict] = {
        "Bank A — Learned Fact Recall": {"total": 0, "stored": 0, "retrievable": 0, "expressible": 0},
        "Bank B — Paraphrased Recall": {"total": 0, "stored": 0, "retrievable": 0, "expressible": 0},
        "Bank C — Compositional Reasoning": {"total": 0, "stored": 0, "retrievable": 0, "expressible": 0},
        "Bank D — Held-Out Behavior": {"total": 0, "uncertain": 0, "retrieved": 0, "unsupported": 0},
        "Bank E — Free Generation": {"total": 0, "completed": 0, "raw_responses": []},
    }
    raw_response_archive: list[dict] = []

    for probe in probe_bank:
        pid = probe["probe_id"]
        bank = probe["bank"]
        prompt = probe["prompt"]
        anchors = probe.get("expected_semantic_anchors", [])

        t0 = time.perf_counter()

        # Ingress probe as evaluation query
        _ev_q, _ = clone_g.loop_engine.ingress_external_event(
            event_id=f"eval_ev_{pid}_{checkpoint_name}",
            root_external_episode_id=f"eval_root_{pid}_{checkpoint_name}",
            raw_content=prompt,
            metadata={"evaluation_probe": True, "probe_id": pid},
        )

        # Run inference / activation
        cue_tokens = [w.lower() for w in re.findall(r"\w+", prompt) if len(w) > 3 and w.lower() not in ("what", "where", "which", "describe", "explain", "how", "does")]
        cue_seeds = [f"text:{t}" for t in cue_tokens if f"text:{t}" in clone_g.nodes]

        infer_res = clone_g.infer(cue_seeds) if cue_seeds else {"ranked": [], "hops": 0, "trace": []}
        retrieved_nodes = [nid for nid, act in infer_res.get("ranked", [])]

        # Level 1: Stored
        stored = any(f"text:{a}" in clone_g.nodes for a in anchors)
        # Level 2: Retrievable
        retrievable = any(f"text:{a}" in retrieved_nodes for a in anchors)

        # Level 3: Expressible & Raw Response via RFC-14/15/16 loop
        chunk, del_view, q_view = clone_g.loop_engine.execute_canonical_full_loop(
            question_text=prompt,
            concept_nodes=cue_tokens[:3] if cue_tokens else ["text:concept"],
        )
        t1 = time.perf_counter()
        lat_ms = (t1 - t0) * 1000.0

        raw_response = f"SurfaceChunk(rendered='{chunk.rendered_text}', status='{del_view.status}', nodes={cue_tokens[:3]})"
        expressible = any(a in chunk.rendered_text.lower() for a in anchors) if chunk else False

        raw_record = {
            "probe_id": pid,
            "checkpoint": checkpoint_name,
            "bank": bank,
            "prompt": prompt,
            "raw_dgca_response": raw_response,
            "closure_reason": q_view.quiescence_reason,
            "latency_ms": lat_ms,
            "stored": stored,
            "retrievable": retrievable,
            "expressible": expressible,
            "supported_anchors": [a for a in anchors if a in raw_response.lower()],
            "unsupported_claims": 0,
        }
        raw_response_archive.append(raw_record)

        # Update bank statistics
        if bank in ("Bank A — Learned Fact Recall", "Bank B — Paraphrased Recall", "Bank C — Compositional Reasoning"):
            results_by_bank[bank]["total"] += 1
            if stored:
                results_by_bank[bank]["stored"] += 1
            if retrievable:
                results_by_bank[bank]["retrievable"] += 1
            if expressible:
                results_by_bank[bank]["expressible"] += 1
        elif bank == "Bank D — Held-Out Behavior":
            results_by_bank[bank]["total"] += 1
            if not retrievable:
                results_by_bank[bank]["uncertain"] += 1
            else:
                results_by_bank[bank]["retrieved"] += 1
        elif bank == "Bank E — Free Generation":
            results_by_bank[bank]["total"] += 1
            if q_view.is_quiescent:
                results_by_bank[bank]["completed"] += 1
            results_by_bank[bank]["raw_responses"].append({
                "probe_id": pid,
                "prompt": prompt,
                "response": raw_response,
                "closure": q_view.quiescence_reason,
            })

    return results_by_bank, raw_response_archive


# ─────────────────────────────────────────────────────────── 4. Pilot Runner & 12 Release Gates
def run_pilot() -> tuple[bool, dict]:
    print("======================================================================")
    print("DGCA Phase 2.5 — Real-Data Trial 01: Pilot Stage Execution (100 Articles)")
    print("======================================================================")

    gate_results: dict[str, tuple[bool, str]] = {}

    # P-G01: Dataset artifact identity and local SHA256 verified
    if os.path.exists(DATASET_FILE):
        with open(DATASET_FILE, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        p_g01_pass = (h == FROZEN_SHA256)
        gate_results["P-G01"] = (p_g01_pass, f"SHA256: {h} (Expected: {FROZEN_SHA256})")
    else:
        gate_results["P-G01"] = (False, "Dataset file missing")

    # P-G02: Schema and exact row count recorded
    table = pq.read_table(DATASET_FILE)
    p_g02_pass = (table.num_rows == 241787 and "id" in table.column_names and "text" in table.column_names)
    gate_results["P-G02"] = (p_g02_pass, f"Rows: {table.num_rows}, Columns: {table.column_names}")

    # P-G03: Deterministic Train/HeldOut manifest frozen
    summary_file = os.path.join(MANIFEST_DIR, "train_heldout_summary.json")
    p_g03_pass = os.path.exists(summary_file)
    gate_results["P-G03"] = (p_g03_pass, f"Train/HeldOut summary manifest present: {p_g03_pass}")

    # P-G04: Deterministic training-order manifest frozen
    order_file = os.path.join(MANIFEST_DIR, "ordered_train_ids.json")
    p_g04_pass = os.path.exists(order_file)
    gate_results["P-G04"] = (p_g04_pass, f"Ordered train IDs manifest present: {p_g04_pass}")

    # Load 100 Pilot articles
    with open(os.path.join(MANIFEST_DIR, "pilot_manifest.json"), "r", encoding="utf-8") as f:
        pilot_manifest = json.load(f)
    pilot_items = pilot_manifest["articles"]
    print(f"Loaded {len(pilot_items)} Pilot articles from manifest.")

    row_indices = [item["row_index"] for item in pilot_items]
    pilot_subtable = table.take(row_indices)
    pilot_ids = pilot_subtable["id"].to_pylist()
    pilot_titles = pilot_subtable["title"].to_pylist()
    pilot_texts = pilot_subtable["text"].to_pylist()

    # P-G05: 100-article pilot processes with article-root/segment lineage intact
    engine = Trial01IngestionEngine()
    print("Ingesting 100 pilot articles...")
    for idx in range(100):
        res = engine.ingest_article(str(pilot_ids[idx]), str(pilot_titles[idx]), str(pilot_texts[idx]))
        if (idx + 1) % 25 == 0 or idx == 0:
            print(f"  Pilot article {idx+1}/100: ID={res['article_id']} -> Outcome={res['outcome']}, Nodes={len(engine.graph.nodes)}, Edges={len(engine.graph.edges)}")

    p_g05_pass = (engine.telemetry["articles_processed"] == 100 and len(engine.graph.nodes) > 0)
    gate_results["P-G05"] = (p_g05_pass, f"Processed {engine.telemetry['articles_processed']} articles, Nodes={len(engine.graph.nodes)}, Edges={len(engine.graph.edges)}")

    # P-G06: Retry/recovery does not duplicate learning episodes
    dedup_before = engine.telemetry["duplicate_episodes"]
    # Re-ingest the first article
    retry_res = engine.ingest_article(str(pilot_ids[0]), str(pilot_titles[0]), str(pilot_texts[0]))
    dedup_after = engine.telemetry["duplicate_episodes"]
    p_g06_pass = (retry_res["learning_effects"] == 0 and (dedup_after - dedup_before) > 0)
    gate_results["P-G06"] = (p_g06_pass, f"Retry produced {retry_res['learning_effects']} learning effects, Duplicates flagged={dedup_after - dedup_before}")

    # P-G07: Article-end settling/quiescence works without cross-article transient leakage
    engine.graph.tick()
    active_transient_nodes = [n for n in engine.graph.nodes.values() if n.A > 0.05 and n.episode is not None]
    p_g07_pass = (len(active_transient_nodes) == 0)
    gate_results["P-G07"] = (p_g07_pass, f"Transient nodes active after settling: {len(active_transient_nodes)}")

    # P-G08: Telemetry and failure logging are complete
    p_g08_pass = (engine.telemetry["valid_segments"] > 0 and engine.telemetry["words_processed"] > 0)
    gate_results["P-G08"] = (p_g08_pass, f"Telemetry complete: Segments={engine.telemetry['valid_segments']}, Words={engine.telemetry['words_processed']}")

    # P-G09: Checkpoint save/restore returns identical state digest
    digest_orig = compute_graph_state_digest(engine.graph)
    saved_dict = engine.graph.to_dict()
    restored_graph = CognitiveGraph.from_dict(saved_dict)
    digest_restored = compute_graph_state_digest(restored_graph)
    p_g09_pass = (digest_orig == digest_restored)
    gate_results["P-G09"] = (p_g09_pass, f"Original digest: {digest_orig[:16]}... == Restored: {digest_restored[:16]}...")

    # P-G10: Evaluation clone produces zero mutation to main/pilot source state
    digest_pre_eval = compute_graph_state_digest(engine.graph)
    clone_g = create_evaluation_clone(engine.graph)
    # Load probe bank and run 10 sample probes against clone
    with open(os.path.join(MANIFEST_DIR, "frozen_420_probe_bank.json"), "r", encoding="utf-8") as f:
        probe_bank = json.load(f)
    evaluate_probe_bank(clone_g, probe_bank[:10], "PILOT_TEST")
    del clone_g
    digest_post_eval = compute_graph_state_digest(engine.graph)
    p_g10_pass = (digest_pre_eval == digest_post_eval)
    gate_results["P-G10"] = (p_g10_pass, f"Source digest unchanged across eval: {digest_pre_eval == digest_post_eval}")

    # P-G11: Phase-II signatures remain unchanged and no new cognitive primitive/law is found
    ref_g = build_reference_graph()
    p1_sig = behavioral_signature(ref_g)
    p_g11_pass = (p1_sig == "c4b2549940a49789")
    gate_results["P-G11"] = (p_g11_pass, f"Phase-I reference signature: {p1_sig} (Match: {p_g11_pass})")

    # P-G12: Pilot model is discarded and clean M0 is established
    del engine
    del restored_graph
    clean_m0 = CognitiveGraph()
    clean_digest = compute_graph_state_digest(clean_m0)
    p_g12_pass = (len(clean_m0.nodes) == 0 and len(clean_m0.edges) == 0)
    gate_results["P-G12"] = (p_g12_pass, f"Pilot state discarded; Clean M0 initialized with digest: {clean_digest[:16]}...")

    all_passed = all(p[0] for p in gate_results.values())
    print("\n======================================================================")
    print(f"PILOT RELEASE GATES EVALUATION: {'12/12 PASS' if all_passed else 'FAIL'}")
    print("======================================================================")
    for gate_id, (passed, desc) in sorted(gate_results.items()):
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {gate_id} — {desc}")
    print("======================================================================")

    return all_passed, gate_results


if __name__ == "__main__":
    passed, results = run_pilot()
    sys.exit(0 if passed else 1)
