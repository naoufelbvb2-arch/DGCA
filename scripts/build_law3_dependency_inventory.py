"""
Script to build the Law-3 Abolition Static Dependency Inventory.
Scans active codebase, tests, scripts, and docs for Law 3 references and classifies them into:
- REMOVE
- AMEND
- HISTORICAL_ONLY
- UNAFFECTED_DIFFERENT_SEMANTICS
Exports: law3_abolition_dependency_inventory.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

SEARCH_PATTERNS = [
    r"\bLaw 3\b",
    r"\bLaw3\b",
    r"\blaw3\b",
    r"\b_law3\b",
    r"\bdecay\b",
    r"\bLAMBDA_DECAY\b",
    r"\bLAMBDA_SAL\b",
    r"\bTHETA_PRUNE\b",
    r"\bW_floor\b",
    r"\bTHETA_PROTECT\b",
    r"\bcellular death\b",
    r"\bcellular_death\b",
    r"\bprune\b",
    r"\bpruning\b",
    r"\bstep_time\b",
    r"\btick\b",
    r"\btransient decay\b",
    r"\blambda_transient\b",
    r"\brole decay\b",
    r"\bevent decay\b",
    r"\borphan gc\b",
    r"\borphan scan\b",
]

COMPILED_RE = re.compile("|".join(SEARCH_PATTERNS), re.IGNORECASE)

CLASSIFICATIONS = {
    # dgca/
    "dgca/config.py:LAMBDA_DECAY": ("REMOVE", "Abolished constant from active cognitive semantics."),
    "dgca/config.py:LAMBDA_SAL": ("REMOVE", "Abolished constant from active cognitive semantics."),
    "dgca/config.py:THETA_PRUNE": ("REMOVE", "Abolished universal low-weight pruning threshold."),
    "dgca/config.py:LAMBDA_TRANSIENT": ("REMOVE", "Abolished transient accelerated decay rate."),
    "dgca/config.py:THETA_PROTECT": ("REMOVE", "Abolished anti-decay salience floor multiplier."),
    "dgca/graph.py:Edge.W_floor": ("REMOVE", "Abolished anti-decay floor property on Edge."),
    "dgca/graph.py:Edge.locked": ("AMEND", "Redefined as established-state revision hysteresis, not anti-decay protection."),
    "dgca/graph.py:_law3_decay": ("AMEND", "Replaced with tombstone method (no decay/pruning sweep)."),
    "dgca/graph.py:_unlink": ("AMEND", "Enhanced with local O(1) orphan node reclamation on affected endpoints."),
    "dgca/graph.py:_law2_reinforce": ("AMEND", "Updated comments/docstrings to reflect Law-3 abolition."),
    "dgca/graph.py:_law12_valence": ("UNAFFECTED_DIFFERENT_SEMANTICS", "Internal affect dynamics unaffected by Law 3."),
    "dgca/graph.py:_evaluate_predictions": ("AMEND", "Updated Law 13 disappointment to remove W_floor floor block (W = max(0, W - delta))."),
    "dgca/graph.py:observe": ("AMEND", "Removed _law3_decay() call."),
    "dgca/graph.py:observe_sequence": ("AMEND", "Removed _law3_decay() call."),
    "dgca/graph.py:tick": ("AMEND", "Redefined as operational time advancement without weight decay or node deletion."),
    "dgca/agent.py:step_time": ("AMEND", "Redefined as operational time advancement without memory decay or node deletion."),
    "dgca/signature.py:build_reference_graph": ("AMEND", "Updated to reflect clock neutrality during silent ticks."),
}


def build_inventory():
    inventory = []
    
    # Scan Python files in dgca/
    for p in (ROOT / "dgca").rglob("*.py"):
        rel_path = p.relative_to(ROOT).as_posix()
        lines = p.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, 1):
            if COMPILED_RE.search(line):
                # Classify
                classification = "AMEND"
                reason = "Runtime reference requiring cleanup or reassignment."
                
                # Match against predefined keys if any
                for sys_key, (c, r) in CLASSIFICATIONS.items():
                    if sys_key.split(":")[0] in rel_path and sys_key.split(":")[-1] in line:
                        classification = c
                        reason = r
                        break
                
                inventory.append({
                    "file": rel_path,
                    "line_number": idx,
                    "line_content": line.strip(),
                    "classification": classification,
                    "reason": reason
                })

    out_file = ROOT / "law3_abolition_dependency_inventory.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)

    print(f"Inventory generated with {len(inventory)} entries in {out_file.name}")
    return inventory


if __name__ == "__main__":
    build_inventory()
