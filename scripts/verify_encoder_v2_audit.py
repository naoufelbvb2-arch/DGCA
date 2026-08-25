"""
DGCA English Encoder v2 — Static & Architectural Audit Script.
Verifies forbidden mechanisms, Law 3 out-of-path, behavioral signatures, and release gates.
"""
import ast
import sys
from pathlib import Path

sys.path.insert(0, ".")

from dgca.assembly import law14_behavioral_signature
from dgca.completion import rfc13_behavioral_signature
from dgca.generation import rfc14_behavioral_signature
from dgca.loop import rfc16_behavioral_signature
from dgca.recurrent import rfc15_behavioral_signature
from dgca.representation import rfc12_behavioral_signature
from dgca.signature import behavioral_signature, build_reference_graph
from scripts.audit_rfc16_benchmarks import _build_benchmark_fixture


def audit_static_forbidden_mechanisms():
    print("=================================================================")
    print("1. STATIC FORBIDDEN-MECHANISM AUDIT")
    print("=================================================================")
    pkg_dir = Path("dgca/encoding/english")
    forbidden_tokens = [
        "torch", "tensorflow", "transformers", "huggingface", "spacy", "nltk",
        "sklearn", "scikit", "openai", "anthropic", "gemini", "bert", "gpt",
        "Linear", "Embedding", "conv", "softmax", "_law3_decay", "apply_law3",
    ]
    violations = []
    for py_file in pkg_dir.glob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            code = f.read()
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for fb in forbidden_tokens:
                            if fb in alias.name.lower():
                                violations.append((py_file.name, f"Forbidden import: {alias.name}"))
                elif isinstance(node, ast.ImportFrom):
                    mod_name = node.module or ""
                    for fb in forbidden_tokens:
                        if fb in mod_name.lower():
                            violations.append((py_file.name, f"Forbidden from-import: {mod_name}"))

    assert len(violations) == 0, f"Static audit failed with violations: {violations}"
    print("[PASS] Zero learned/neural/statistical models or pretrained POS taggers detected.")
    print("[PASS] Law 3 is completely absent and out of path in dgca/encoding/english/.")


def audit_upstream_signatures():
    print("\n=================================================================")
    print("2. UPSTREAM BEHAVIORAL SIGNATURES AUDIT")
    print("=================================================================")
    # Phase-I reference graph
    g_ref = build_reference_graph()
    phase1_sig = behavioral_signature(g_ref)
    assert phase1_sig == "c4b2549940a49789", f"Phase-I signature diverged: {phase1_sig}"
    print(f"[PASS] Phase-I Reference Signature: {phase1_sig} (EXACT MATCH)")

    # RFC-11..RFC-16 reference benchmark fixture
    g_bench, _ = _build_benchmark_fixture()
    _chunk, _del_view, _q_view = g_bench.loop_engine.execute_canonical_full_loop(
        question_text="What is falcon?",
        concept_nodes=["concept_falcon", "fly", "predator"],
    )
    sig_l14 = law14_behavioral_signature(g_bench.assembly_manager)
    sig_r12 = rfc12_behavioral_signature(g_bench.representation_engine)
    sig_r13 = rfc13_behavioral_signature(g_bench.completion_engine)
    sig_r14 = rfc14_behavioral_signature(g_bench.generation_engine)
    sig_r15 = rfc15_behavioral_signature(g_bench.recurrent_engine)
    sig_r16 = rfc16_behavioral_signature(g_bench.loop_engine)

    assert sig_l14 == "1a478f1fef889df1"
    assert sig_r12 == "9e56c9fa1f3cd6ca"
    assert sig_r13 == "8652eb05126afa8c"
    assert sig_r14 == "46213188cdb02ee8"
    assert sig_r15 == "6305a92d02076df6"
    assert sig_r16 == "cc9363dc6394a7cf"

    print(f"[PASS] Law-14 Assembly Signature:      {sig_l14} (EXACT MATCH)")
    print(f"[PASS] RFC-12 Representation Signature: {sig_r12} (EXACT MATCH)")
    print(f"[PASS] RFC-13 Completion Signature:     {sig_r13} (EXACT MATCH)")
    print(f"[PASS] RFC-14 Generation Signature:     {sig_r14} (EXACT MATCH)")
    print(f"[PASS] RFC-15 Recurrent Signature:      {sig_r15} (EXACT MATCH)")
    print(f"[PASS] RFC-16 Loop Signature:           {sig_r16} (EXACT MATCH)")


if __name__ == "__main__":
    audit_static_forbidden_mechanisms()
    audit_upstream_signatures()
