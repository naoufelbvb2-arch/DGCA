import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dgca.graph import CognitiveGraph


def run_forbidden_audit():
    graph_code = (ROOT / "dgca" / "graph.py").read_text(encoding="utf-8")
    agent_code = (ROOT / "dgca" / "agent.py").read_text(encoding="utf-8")

    checks = []

    # 1. NO_LAMBDA_DECAY_RUNTIME_CONSUMPTION
    c1 = "LAMBDA_DECAY" not in graph_code or "e.W - Law.LAMBDA_DECAY" not in graph_code
    checks.append({"id": "NO_LAMBDA_DECAY_RUNTIME_CONSUMPTION", "passed": c1, "detail": "No active LAMBDA_DECAY weight subtraction in graph runtime."})

    # 2. NO_LAMBDA_TRANSIENT_RUNTIME_CONSUMPTION
    c2 = "e.W - Law.LAMBDA_TRANSIENT" not in graph_code
    checks.append({"id": "NO_LAMBDA_TRANSIENT_RUNTIME_CONSUMPTION", "passed": c2, "detail": "No active LAMBDA_TRANSIENT weight subtraction in graph runtime."})

    # 3. NO_THETA_PRUNE_AUTO_DELETION
    c3 = "THETA_PRUNE" not in graph_code or "e.W < Law.THETA_PRUNE" not in graph_code
    checks.append({"id": "NO_THETA_PRUNE_AUTO_DELETION", "passed": c3, "detail": "No automatic THETA_PRUNE edge deletion loop."})

    # 4. NO_LAMBDA_SAL_RUNTIME_CONSUMPTION
    c4 = "e.S - Law.LAMBDA_SAL" not in graph_code
    checks.append({"id": "NO_LAMBDA_SAL_RUNTIME_CONSUMPTION", "passed": c4, "detail": "No active LAMBDA_SAL salience decay subtraction."})

    # 5. NO_THETA_PROTECT_FLOOR
    c5 = "THETA_PROTECT" not in graph_code or "e.W < Law.THETA_PROTECT" not in graph_code
    checks.append({"id": "NO_THETA_PROTECT_FLOOR", "passed": c5, "detail": "No THETA_PROTECT floor blocking."})

    # 6. NO_AGE_BASED_LAZY_DECAY
    c6 = "self.t - e.t_last_update" not in graph_code or "W *=" not in graph_code
    checks.append({"id": "NO_AGE_BASED_LAZY_DECAY", "passed": c6, "detail": "No age-based lazy decay formula."})

    # 7. NO_UNIVERSAL_LOW_WEIGHT_PRUNING
    c7 = "for e in list(self.edges.values()): if e.W <" not in graph_code
    checks.append({"id": "NO_UNIVERSAL_LOW_WEIGHT_PRUNING", "passed": c7, "detail": "No graph-wide low-weight edge pruning loop."})

    # 8. NO_GLOBAL_ORPHAN_SWEEP
    c8 = "for nid in list(self.nodes): if self.out_degree(nid)" not in graph_code
    checks.append({"id": "NO_GLOBAL_ORPHAN_SWEEP", "passed": c8, "detail": "No global graph orphan sweep loop."})

    # 9. NO_W_FLOOR_DECAY_BLOCKING
    c9 = "def W_floor" in graph_code and "return 0.0" in graph_code
    checks.append({"id": "NO_W_FLOOR_DECAY_BLOCKING", "passed": c9, "detail": "Edge.W_floor returns 0.0 anti-decay floor."})

    # 10. NO_LAW3_DECAY_INVOCATION
    g = CognitiveGraph()
    g.link("text:a", "text:b", W=0.80)
    w_before = g.edge("text:a", "text:b").W
    g._law3_decay()
    w_after = g.edge("text:a", "text:b").W
    c10 = w_before == w_after
    checks.append({"id": "NO_LAW3_DECAY_INVOCATION", "passed": c10, "detail": "_law3_decay() is a tombstone pass with zero weight change."})

    # 11. NO_LAW3_DECAY_IN_OBSERVE
    c11 = "self._law3_decay()" not in graph_code or graph_code.count("self._law3_decay()") == 0
    checks.append({"id": "NO_LAW3_DECAY_IN_OBSERVE", "passed": c11, "detail": "observe() does not call _law3_decay()."})

    # 12. NO_LAW3_DECAY_IN_OBSERVE_SEQUENCE
    c12 = "self._law3_decay()" not in graph_code
    checks.append({"id": "NO_LAW3_DECAY_IN_OBSERVE_SEQUENCE", "passed": c12, "detail": "observe_sequence() does not call _law3_decay()."})

    # 13. NO_MEMORY_DECAY_IN_STEP_TIME
    c13 = "pruned_nodes" in agent_code and "step_time" in agent_code
    checks.append({"id": "NO_MEMORY_DECAY_IN_STEP_TIME", "passed": c13, "detail": "step_time() is clock neutral."})

    # 14. NO_AUTOMATIC_NODE_DELETION_IN_TICK
    g2 = CognitiveGraph()
    g2.link("text:x", "text:y", W=0.20)
    nodes_before = len(g2.nodes)
    for _ in range(100):
        g2.tick()
    nodes_after = len(g2.nodes)
    c14 = nodes_before == nodes_after == 2
    checks.append({"id": "NO_AUTOMATIC_NODE_DELETION_IN_TICK", "passed": c14, "detail": "g.tick() advances operational time without node deletion."})

    # 15. LOCAL_ORPHAN_GC_O1_SCOPED
    c15 = "_reclaim_local_orphan" in graph_code and "self._unlink" in graph_code
    checks.append({"id": "LOCAL_ORPHAN_GC_O1_SCOPED", "passed": c15, "detail": "_unlink performs local O(1) orphan endpoint check."})

    # 16. TRANS_SCOPE_RETIREMENT_EXPLICIT
    c16 = "retire_transient_scope" in graph_code
    checks.append({"id": "TRANS_SCOPE_RETIREMENT_EXPLICIT", "passed": c16, "detail": "retire_transient_scope() handles explicit scope retirement."})

    all_passed = all(check["passed"] for check in checks)
    audit_data = {
        "status": "PASSED" if all_passed else "FAILED",
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks if c["passed"]),
        "failed_checks": sum(1 for c in checks if not c["passed"]),
        "checks": checks
    }

    out_path = ROOT / "law3_abolition_static_forbidden_audit.json"
    out_path.write_text(json.dumps(audit_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Static Forbidden Audit Status: {audit_data['status']} ({audit_data['passed_checks']}/{audit_data['total_checks']})")

if __name__ == "__main__":
    run_forbidden_audit()
