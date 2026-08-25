"""
DGCA Phase 2.5 — Real-Data Trial 01 Free Generation Longitudinal Inspector.
"""
import json
import os

RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw_responses")
checkpoints = ["M0", "M1K", "M10K", "M50K", "M100K", "MFULL"]

all_responses = {}
for cp in checkpoints:
    path = os.path.join(RESPONSES_DIR, f"{cp}_raw_responses.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            recs = json.load(f)
        all_responses[cp] = {r["probe_id"]: r for r in recs if r["bank"] == "Bank E — Free Generation"}

print("======================================================================")
print("BANK E — 20 FREE GENERATION PROBES LONGITUDINAL COMPARISON")
print("======================================================================")

sample_probe_ids = sorted(next(iter(all_responses.values())).keys())

for pid in sample_probe_ids:
    prompt = all_responses["M0"][pid]["prompt"]
    print(f"\n[{pid}] PROMPT: \"{prompt}\"")
    for cp in checkpoints:
        if cp in all_responses and pid in all_responses[cp]:
            resp = all_responses[cp][pid]["raw_dgca_response"]
            closure = all_responses[cp][pid]["closure_reason"]
            lat = all_responses[cp][pid]["latency_ms"]
            print(f"  {cp:<6} -> {resp} [Closure: {closure}, Latency: {lat:.1f} ms]")
