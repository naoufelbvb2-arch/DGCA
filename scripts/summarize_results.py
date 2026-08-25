"""
DGCA Phase 2.5 — Real-Data Trial 01 Results Summarizer.
"""
import json
import os

summary_path = os.path.join(os.path.dirname(__file__), "..", "data", "trial01_execution_summary.json")
with open(summary_path, "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"{'CP':<6} | {'Articles':<8} | {'Nodes':<6} | {'Edges':<6} | {'Density':<8} | {'RAM_MB':<8} | {'Wall_s':<8} | {'Bank A (S/R/E)':<16} | {'Bank B (S/R/E)':<16} | {'Bank C (S/E)':<12} | {'Bank D (Unc/Ret)':<16} | {'Ret K1':<8}")
print("-" * 140)
for r in records:
    cp = r["checkpoint"]
    art = r["articles_count"]
    nodes = r["nodes"]
    edges = r["edges"]
    dens = f"{r['density']:.4f}"
    ram = f"{r['ram_mb']:.1f}"
    wall = f"{r['wall_clock_sec']:.2f}"
    ba = r["bank_results"]["Bank A — Learned Fact Recall"]
    bb = r["bank_results"]["Bank B — Paraphrased Recall"]
    bc = r["bank_results"]["Bank C — Compositional Reasoning"]
    bd = r["bank_results"]["Bank D — Held-Out Behavior"]
    ba_str = f"{ba['stored']}/{ba['retrievable']}/{ba['expressible']}"
    bb_str = f"{bb['stored']}/{bb['retrievable']}/{bb['expressible']}"
    bc_str = f"{bc['stored']}/{bc['expressible']}"
    bd_str = f"{bd['uncertain']}/{bd['retrieved']}"
    ret = f"{r['retention_k1_score']*100:.1f}%"
    print(f"{cp:<6} | {art:<8} | {nodes:<6} | {edges:<6} | {dens:<8} | {ram:<8} | {wall:<8} | {ba_str:<16} | {bb_str:<16} | {bc_str:<12} | {bd_str:<16} | {ret:<8}")
