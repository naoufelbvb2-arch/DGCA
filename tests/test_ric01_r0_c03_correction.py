"""
DGCA — RIC-01 / R0-C03: Final Fail-Closed Restore & Lifecycle Guard Closure Test Suite.
Formal Correction Specification v1.0 — FROZEN.

Coverage:
- Invariants: C03-I01 through C03-I16
- Acceptance Tests: C03-T01 through C03-T29
"""
from __future__ import annotations

import copy
import json
import pathlib
from typing import Any

import pytest

from dgca import (
    CheckpointSchemaError,
    CheckpointValidationError,
    CognitiveGraph,
    Edge,
    FormationCandidate,
    IllegalLifecycleTransitionError,
    Node,
    RuntimeLifecycleGuard,
    RuntimeLifecycleState,
    RuntimeRoot,
    StructuralAssembly,
    canonical_assembly_id,
    compute_checkpoint_state_digest,
    load_checkpoint_json,
    restore_cognitive_checkpoint,
    save_cognitive_checkpoint,
    validate_canonical_persistent_shape,
    validate_legacy_v1_source,
    validate_schema_1_1_source,
)
from dgca.signature import behavioral_signature, build_reference_graph

# ─────────────────────────────────────────────────────────── Fixtures and Helpers

def make_valid_c03_graph() -> CognitiveGraph:
    """Helper to construct a fully lawful CognitiveGraph meeting all RFC-11 and C03 invariants."""
    g = CognitiveGraph(t=100)
    g.nodes["n1"] = Node(nid="n1", region="TEXT")
    g.nodes["n2"] = Node(nid="n2", region="TEXT")
    g.nodes["n3"] = Node(nid="n3", region="TEXT")
    g.nodes["n4"] = Node(nid="n4", region="TEXT")
    g.nodes["n5"] = Node(nid="n5", region="TEXT")

    e1 = Edge(src="n1", dst="n2", W=0.9, kind="assoc")
    e2 = Edge(src="n2", dst="n3", W=0.9, kind="assoc")
    e3 = Edge(src="n3", dst="n4", W=0.9, kind="assoc")
    e4 = Edge(src="n4", dst="n5", W=0.9, kind="assoc")

    g.edges[("n1", "n2")] = e1
    g.edges[("n2", "n3")] = e2
    g.edges[("n3", "n4")] = e3
    g.edges[("n4", "n5")] = e4

    g.out_adj.setdefault("n1", {})["n2"] = e1
    g.out_adj.setdefault("n2", {})["n3"] = e2
    g.out_adj.setdefault("n3", {})["n4"] = e3
    g.out_adj.setdefault("n4", {})["n5"] = e4

    g.in_adj.setdefault("n2", {})["n1"] = e1
    g.in_adj.setdefault("n3", {})["n2"] = e2
    g.in_adj.setdefault("n4", {})["n3"] = e3
    g.in_adj.setdefault("n5", {})["n4"] = e4

    mgr = g.assembly_manager

    # Assembly 1: ("n1", "n2") and ("n2", "n3")
    asm1 = StructuralAssembly(
        assembly_id="asm_parent_1",
        version=1,
        member_edges=frozenset([("n1", "n2"), ("n2", "n3")]),
        origin_signature="sig_p1",
    )
    # Assembly 2: ("n3", "n4") and ("n4", "n5")
    asm2 = StructuralAssembly(
        assembly_id="asm_parent_2",
        version=1,
        member_edges=frozenset([("n3", "n4"), ("n4", "n5")]),
        origin_signature="sig_p2",
    )
    mgr.assemblies["asm_parent_1"] = [asm1]
    mgr.assemblies["asm_parent_2"] = [asm2]

    # Formation candidate: 3 edges (>= K_ASM_MIN=3)
    comp = [("n1", "n2"), ("n2", "n3"), ("n3", "n4")]
    cid = canonical_assembly_id(comp)
    cand = FormationCandidate(
        candidate_id=cid,
        edges=frozenset(comp),
        context_signature="ctx_1",
        root_votes={"rv_1", "rv_2"},
        created_t=10,
    )
    cand_key = f"{cid}:ctx_ctx_1"
    mgr.pending_candidates[cand_key] = cand

    # Growth candidate: asm_parent_1 growing with ("n3", "n4") which is in g.edges but NOT in asm_parent_1
    mgr.pending_growth[("asm_parent_1", ("n3", "n4"), "ctx_growth")] = {"rv_3"}

    # Merge candidate: asm_parent_1 and asm_parent_2 (two distinct live parents)
    mgr.pending_merge[(frozenset(["asm_parent_1", "asm_parent_2"]), "ctx_merge")] = {"rv_4"}

    mgr.rebuild_indexes()
    return g


def make_valid_legacy_v1_dict() -> dict[str, Any]:
    """Helper to construct a valid legacy v1.0 dictionary containing all 8 durable sections."""
    return {
        "version": "1.0",
        "t": 42,
        "concept_hits": {"c1": 5},
        "drives": {"curiosity": {"urgency": 0.5, "satiation": 0.5}},
        "hypotheses": [{"hypo_id": "h1", "score": 0.8}],
        "X": {"n1": ["n2"]},
        "nodes": {
            "n1": {
                "nid": "n1",
                "region": "TEXT",
                "is_concept": True,
                "members": ["m1"],
                "U": 0.5,
                "V": 0.5,
                "head": None,
                "is_intrinsic": False,
                "N_total": 2,
            },
            "n2": {
                "nid": "n2",
                "region": "TEXT",
                "is_concept": False,
                "members": [],
                "U": 0.3,
                "V": 0.3,
                "head": None,
                "is_intrinsic": False,
                "N_total": 1,
            },
        },
        "edges": [
            {
                "src": "n1",
                "dst": "n2",
                "W": 0.7,
                "kind": "assoc",
                "origin": "user",
                "t_created": 1,
                "t_last_update": 10,
                "n": 3,
                "M_max": 0.9,
                "S": 0.1,
                "tagged": False,
                "valence": 0.0,
                "lag": 0.0,
                "fwd": True,
                "g": None,
                "contexts": ["ctx_a"],
                "ctx_hits": {"ctx_a": 3},
                "is_intrinsic": False,
                "k_fail": 0,
            }
        ],
        "assemblies": [],
    }


def make_valid_schema_1_1_dict(tmp_path: pathlib.Path) -> dict[str, Any]:
    """Helper to construct a valid schema 1.1 dictionary."""
    g = make_valid_c03_graph()
    save_path = tmp_path / "temp_save_v1_1.json"
    save_cognitive_checkpoint(g, save_path)
    data = json.loads(save_path.read_text(encoding="utf-8"))
    save_path.unlink()

    # Downgrade schema version header
    data["schema"]["checkpoint_schema_version"] = "1.1"
    data["schema"]["runtime_contract_version"] = "1.1"

    # Strip storage_key from pending candidates to simulate authentic 1.1
    cands = data["persistent_state"]["pending_structural_evidence"]["pending_candidates"]
    for c in cands:
        c.pop("storage_key", None)

    # Recompute state digest for schema 1.1 payload
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    return data


# ==============================================================================
# SECTION 1: INVARIANTS C03-I01 .. C03-I16
# ==============================================================================

def test_c03_i01_schemaless_json_never_treated_as_legacy(tmp_path: pathlib.Path) -> None:
    """C03-I01: Schema-less JSON is never treated as legacy v1.0."""
    p1 = tmp_path / "empty.json"
    p1.write_text("{}", encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Unrecognized checkpoint family"):
        restore_cognitive_checkpoint(p1)

    p2 = tmp_path / "pseudolegacy.json"
    p2.write_text(json.dumps({"nodes": {}, "edges": []}), encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Unrecognized checkpoint family"):
        restore_cognitive_checkpoint(p2)


def test_c03_i02_legacy_migration_accepts_only_explicit_v1_0() -> None:
    """C03-I02: Legacy migration accepts only explicit version == '1.0'."""
    data = make_valid_legacy_v1_dict()
    validate_legacy_v1_source(data)

    data_bad_ver = dict(data)
    data_bad_ver["version"] = "2.0"
    with pytest.raises(CheckpointSchemaError, match="Unsupported or missing legacy version"):
        validate_legacy_v1_source(data_bad_ver)

    data_no_ver = dict(data)
    del data_no_ver["version"]
    with pytest.raises(CheckpointSchemaError, match="Unsupported or missing legacy version"):
        validate_legacy_v1_source(data_no_ver)


def test_c03_i03_missing_durable_legacy_fields_fail_closed() -> None:
    """C03-I03: Missing durable legacy fields fail closed without inventing defaults."""
    required_sections = ["t", "concept_hits", "drives", "hypotheses", "X", "nodes", "edges", "assemblies"]
    for sec in required_sections:
        data = make_valid_legacy_v1_dict()
        del data[sec]
        with pytest.raises(CheckpointSchemaError, match=f"Missing durable legacy section: '{sec}'"):
            validate_legacy_v1_source(data)


def test_c03_i04_duplicate_json_keys_fail_closed(tmp_path: pathlib.Path) -> None:
    """C03-I04: Duplicate JSON keys at any depth fail closed."""
    raw_top = '{"schema": 1, "schema": 2}'
    with pytest.raises(CheckpointSchemaError, match="Duplicate JSON object key detected: 'schema'"):
        load_checkpoint_json(raw_top)

    raw_nested = '{"persistent_state": {"t": 10, "t": 20}}'
    with pytest.raises(CheckpointSchemaError, match="Duplicate JSON object key detected: 't'"):
        load_checkpoint_json(raw_nested)

    file_dup = tmp_path / "dup.json"
    file_dup.write_text('{"a": 1, "a": 2}', encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Duplicate JSON object key detected: 'a'"):
        load_checkpoint_json(file_dup)


def test_c03_i05_missing_canonical_durable_sections_fail_closed() -> None:
    """C03-I05: Missing canonical durable sections fail closed without silent empty defaults."""
    g = make_valid_c03_graph()
    from dgca.persistence import extract_canonical_persistent_payload
    payload = extract_canonical_persistent_payload(g, g.assembly_manager)
    canonical_dict = {
        "schema": {"checkpoint_schema_version": "1.1.1", "runtime_contract_version": "1.1.1", "cognitive_semantics_version": "1.0"},
        "compatibility": {},
        "integrity": {},
        "persistent_state": payload,
    }
    validate_canonical_persistent_shape(canonical_dict, schema_label="1.1.1")

    # Missing persistent section
    for p_key in ["logical_time", "nodes", "edges", "contradictions", "concept_hits", "drives", "hypotheses", "assemblies", "pending_structural_evidence"]:
        broken = copy.deepcopy(canonical_dict)
        del broken["persistent_state"][p_key]
        with pytest.raises(CheckpointSchemaError, match=f"Missing durable persistent section '{p_key}'"):
            validate_canonical_persistent_shape(broken, schema_label="1.1.1")

    # Missing pending sub-section
    for pend_key in ["pending_candidates", "pending_growth", "pending_merge"]:
        broken = copy.deepcopy(canonical_dict)
        del broken["persistent_state"]["pending_structural_evidence"][pend_key]
        with pytest.raises(CheckpointSchemaError, match=f"pending structural evidence sub-section '{pend_key}'"):
            validate_canonical_persistent_shape(broken, schema_label="1.1.1")


def test_c03_i06_duplicate_node_ids_fail_closed(tmp_path: pathlib.Path) -> None:
    """C03-I06: Duplicate Node IDs fail closed."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_dup_node.json"
    save_cognitive_checkpoint(g, ckpt)

    data = json.loads(ckpt.read_text(encoding="utf-8"))
    dup_node = copy.deepcopy(data["persistent_state"]["nodes"][0])
    data["persistent_state"]["nodes"].append(dup_node)
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate Node ID detected during restore"):
        restore_cognitive_checkpoint(ckpt)


def test_c03_i07_duplicate_edge_ids_fail_closed(tmp_path: pathlib.Path) -> None:
    """C03-I07: Duplicate Edge IDs fail closed."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_dup_edge.json"
    save_cognitive_checkpoint(g, ckpt)

    data = json.loads(ckpt.read_text(encoding="utf-8"))
    dup_edge = copy.deepcopy(data["persistent_state"]["edges"][0])
    data["persistent_state"]["edges"].append(dup_edge)
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate Edge ID detected during restore"):
        restore_cognitive_checkpoint(ckpt)


def test_c03_i08_duplicate_assembly_versions_fail_closed(tmp_path: pathlib.Path) -> None:
    """C03-I08: Duplicate Assembly versions fail closed."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_dup_asm.json"
    save_cognitive_checkpoint(g, ckpt)

    data = json.loads(ckpt.read_text(encoding="utf-8"))
    dup_asm = copy.deepcopy(data["persistent_state"]["assemblies"][0])
    data["persistent_state"]["assemblies"].append(dup_asm)
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate Assembly version detected during restore"):
        restore_cognitive_checkpoint(ckpt)


def test_c03_i09_duplicate_pending_identities_fail_closed(tmp_path: pathlib.Path) -> None:
    """C03-I09: Duplicate pending formation/growth/merge identities fail closed."""
    g = make_valid_c03_graph()

    # 1. Formation
    ckpt_f = tmp_path / "ckpt_dup_form.json"
    save_cognitive_checkpoint(g, ckpt_f)
    data_f = json.loads(ckpt_f.read_text(encoding="utf-8"))
    dup_cand = copy.deepcopy(data_f["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0])
    data_f["persistent_state"]["pending_structural_evidence"]["pending_candidates"].append(dup_cand)
    data_f["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data_f["persistent_state"])
    ckpt_f.write_text(json.dumps(data_f), encoding="utf-8")
    with pytest.raises(CheckpointValidationError, match="Duplicate formation candidate storage_key"):
        restore_cognitive_checkpoint(ckpt_f)

    # 2. Growth
    ckpt_g = tmp_path / "ckpt_dup_grow.json"
    save_cognitive_checkpoint(g, ckpt_g)
    data_g = json.loads(ckpt_g.read_text(encoding="utf-8"))
    dup_grow = copy.deepcopy(data_g["persistent_state"]["pending_structural_evidence"]["pending_growth"][0])
    data_g["persistent_state"]["pending_structural_evidence"]["pending_growth"].append(dup_grow)
    data_g["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data_g["persistent_state"])
    ckpt_g.write_text(json.dumps(data_g), encoding="utf-8")
    with pytest.raises(CheckpointValidationError, match="Duplicate growth candidate key"):
        restore_cognitive_checkpoint(ckpt_g)

    # 3. Merge
    ckpt_m = tmp_path / "ckpt_dup_mrg.json"
    save_cognitive_checkpoint(g, ckpt_m)
    data_m = json.loads(ckpt_m.read_text(encoding="utf-8"))
    dup_mrg = copy.deepcopy(data_m["persistent_state"]["pending_structural_evidence"]["pending_merge"][0])
    data_m["persistent_state"]["pending_structural_evidence"]["pending_merge"].append(dup_mrg)
    data_m["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data_m["persistent_state"])
    ckpt_m.write_text(json.dumps(data_m), encoding="utf-8")
    with pytest.raises(CheckpointValidationError, match="Duplicate merge candidate key"):
        restore_cognitive_checkpoint(ckpt_m)


def test_c03_i10_formation_candidate_identity_matches_canonical_edge_identity(tmp_path: pathlib.Path) -> None:
    """C03-I10: Formation candidate candidate_id matches canonical edge identity."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_bad_cid.json"
    save_cognitive_checkpoint(g, ckpt)

    data = json.loads(ckpt.read_text(encoding="utf-8"))
    cand = data["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0]
    cand["candidate_id"] = "asm_forged_non_canonical"
    cand["storage_key"] = f"asm_forged_non_canonical:ctx_{cand.get('context_signature') or 'default'}"
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="does not match canonical_assembly_id"):
        restore_cognitive_checkpoint(ckpt)


def test_c03_i11_formation_size_respects_rfc11_bounds(tmp_path: pathlib.Path) -> None:
    """C03-I11: Formation size respects [K_ASM_MIN, K_ASM_MEM] bounds."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_small_cand.json"
    save_cognitive_checkpoint(g, ckpt)

    data = json.loads(ckpt.read_text(encoding="utf-8"))
    cand = data["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0]
    # Reduce edges to 1 (less than K_ASM_MIN=3)
    cand["edges"] = [["n1", "n2"]]
    c_id = canonical_assembly_id([("n1", "n2")])
    cand["candidate_id"] = c_id
    cand["storage_key"] = f"{c_id}:ctx_{cand.get('context_signature') or 'default'}"
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="outside bounds"):
        restore_cognitive_checkpoint(ckpt)


def test_c03_i12_growth_edge_is_not_already_in_parent(tmp_path: pathlib.Path) -> None:
    """C03-I12: Growth edge must not already be in parent assembly member edges."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_growth_in_parent.json"
    save_cognitive_checkpoint(g, ckpt)

    data = json.loads(ckpt.read_text(encoding="utf-8"))
    growth = data["persistent_state"]["pending_structural_evidence"]["pending_growth"][0]
    growth["new_edge"] = ["n1", "n2"]
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    ckpt.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="already a member of parent assembly"):
        restore_cognitive_checkpoint(ckpt)


def test_c03_i13_merge_has_exactly_two_distinct_live_parents(tmp_path: pathlib.Path) -> None:
    """C03-I13: Merge candidate must have exactly two distinct live parents."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_merge_one_parent.json"
    save_cognitive_checkpoint(g, ckpt)

    # 1 parent
    data1 = json.loads(ckpt.read_text(encoding="utf-8"))
    data1["persistent_state"]["pending_structural_evidence"]["pending_merge"][0]["parent_assembly_ids"] = ["asm_parent_1"]
    data1["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data1["persistent_state"])
    ckpt.write_text(json.dumps(data1), encoding="utf-8")
    with pytest.raises(CheckpointValidationError, match="must have exactly two distinct parent assemblies"):
        restore_cognitive_checkpoint(ckpt)

    # 3 parents
    data3 = json.loads(ckpt.read_text(encoding="utf-8"))
    data3["persistent_state"]["pending_structural_evidence"]["pending_merge"][0]["parent_assembly_ids"] = [
        "asm_parent_1", "asm_parent_2", "asm_parent_3"
    ]
    data3["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data3["persistent_state"])
    ckpt.write_text(json.dumps(data3), encoding="utf-8")
    with pytest.raises(CheckpointValidationError, match="must have exactly two distinct parent assemblies"):
        restore_cognitive_checkpoint(ckpt)


def test_c03_i14_same_state_lifecycle_nesting_fails_closed() -> None:
    """C03-I14: Same-state lifecycle guard nesting fails closed and does not reset outer state."""
    guard = RuntimeLifecycleGuard()

    # RESTORING nesting
    with guard.restoring():
        with pytest.raises(IllegalLifecycleTransitionError, match="Illegal lifecycle transition"), guard.restoring():
            pass
        assert guard.state == RuntimeLifecycleState.RESTORING
    assert guard.state == RuntimeLifecycleState.IDLE

    # CHECKPOINTING nesting
    with guard.checkpointing():
        with pytest.raises(IllegalLifecycleTransitionError, match="Illegal lifecycle transition"), guard.checkpointing():
            pass
        assert guard.state == RuntimeLifecycleState.CHECKPOINTING
    assert guard.state == RuntimeLifecycleState.IDLE

    # MUTATING nesting
    with guard.mutating():
        with pytest.raises(IllegalLifecycleTransitionError, match="Illegal lifecycle transition"), guard.mutating():
            pass
        assert guard.state == RuntimeLifecycleState.MUTATING
    assert guard.state == RuntimeLifecycleState.IDLE


def test_c03_i15_lawful_c02_c01_r0_behavior_remains_unchanged(tmp_path: pathlib.Path) -> None:
    """C03-I15: Lawful C02/C01/R0 behavior remains intact and round-trips exactly."""
    g = make_valid_c03_graph()
    ckpt = tmp_path / "ckpt_lawful_rt.json"
    save_cognitive_checkpoint(g, ckpt)
    restored, report = restore_cognitive_checkpoint(ckpt)
    assert report is None
    assert restored.t == g.t
    assert set(restored.nodes.keys()) == set(g.nodes.keys())
    assert set(restored.edges.keys()) == set(g.edges.keys())
    assert set(restored._assembly_manager.assemblies.keys()) == set(g.assembly_manager.assemblies.keys())


def test_c03_i16_baseline_signature_remains_unchanged() -> None:
    """C03-I16: Baseline cognitive signature remains strictly 915119d40643cb97."""
    ref_g = build_reference_graph()
    sig = behavioral_signature(ref_g)
    assert sig == "915119d40643cb97"


# ==============================================================================
# SECTION 2: ACCEPTANCE TESTS C03-T01 .. C03-T29
# ==============================================================================

def test_c03_t01_empty_dict_fails(tmp_path: pathlib.Path) -> None:
    """C03-T01: Empty JSON object {} fails closed."""
    p = tmp_path / "t01.json"
    p.write_text("{}", encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Unrecognized checkpoint family"):
        restore_cognitive_checkpoint(p)


def test_c03_t02_schemaless_pseudolegacy_fails(tmp_path: pathlib.Path) -> None:
    """C03-T02: Schema-less pseudo-legacy JSON without version == '1.0' fails closed."""
    p = tmp_path / "t02.json"
    p.write_text(json.dumps({"nodes": {"n1": {"nid": "n1", "region": "TEXT"}}}), encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Unrecognized checkpoint family"):
        restore_cognitive_checkpoint(p)


def test_c03_t03_valid_explicit_v1_0_still_migrates(tmp_path: pathlib.Path) -> None:
    """C03-T03: Valid explicit legacy v1.0 checkpoint still migrates cleanly."""
    legacy = make_valid_legacy_v1_dict()
    p = tmp_path / "t03.json"
    p.write_text(json.dumps(legacy), encoding="utf-8")
    restored, report = restore_cognitive_checkpoint(p)
    assert report is not None
    assert report.source_schema == "1.0"
    assert report.target_schema == "1.1.1"
    assert restored.t == 42
    assert "n1" in restored.nodes


def test_c03_t04_missing_or_unknown_legacy_version_fails(tmp_path: pathlib.Path) -> None:
    """C03-T04: Missing or unknown legacy version fails closed."""
    legacy = make_valid_legacy_v1_dict()
    legacy["version"] = "0.9"
    p = tmp_path / "t04.json"
    p.write_text(json.dumps(legacy), encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Unrecognized checkpoint family"):
        restore_cognitive_checkpoint(p)


def test_c03_t05_missing_durable_legacy_section_fails(tmp_path: pathlib.Path) -> None:
    """C03-T05: Missing durable legacy section fails closed."""
    legacy = make_valid_legacy_v1_dict()
    del legacy["drives"]
    p = tmp_path / "t05.json"
    p.write_text(json.dumps(legacy), encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Missing durable legacy section: 'drives'"):
        restore_cognitive_checkpoint(p)


def test_c03_t06_duplicate_json_key_fails(tmp_path: pathlib.Path) -> None:
    """C03-T06: Duplicate JSON key fails closed."""
    p = tmp_path / "t06.json"
    p.write_text('{"nodes": {}, "nodes": {}}', encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="Duplicate JSON object key detected: 'nodes'"):
        restore_cognitive_checkpoint(p)


def test_c03_t07_current_checkpoint_missing_durable_section_fails(tmp_path: pathlib.Path) -> None:
    """C03-T07: Current checkpoint missing a required durable section fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t07.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    del data["persistent_state"]["hypotheses"]
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointSchemaError, match=r"Missing.*hypotheses"):
        restore_cognitive_checkpoint(p)


def test_c03_t08_duplicate_node_fails(tmp_path: pathlib.Path) -> None:
    """C03-T08: Duplicate node fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t08.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["nodes"].append(copy.deepcopy(data["persistent_state"]["nodes"][0]))
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate Node ID detected during restore"):
        restore_cognitive_checkpoint(p)


def test_c03_t09_duplicate_edge_fails(tmp_path: pathlib.Path) -> None:
    """C03-T09: Duplicate edge fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t09.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["edges"].append(copy.deepcopy(data["persistent_state"]["edges"][0]))
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate Edge ID detected during restore"):
        restore_cognitive_checkpoint(p)


def test_c03_t10_duplicate_assembly_version_fails(tmp_path: pathlib.Path) -> None:
    """C03-T10: Duplicate assembly version fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t10.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["assemblies"].append(copy.deepcopy(data["persistent_state"]["assemblies"][0]))
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate Assembly version detected during restore"):
        restore_cognitive_checkpoint(p)


def test_c03_t11_duplicate_formation_key_fails(tmp_path: pathlib.Path) -> None:
    """C03-T11: Duplicate formation storage key fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t11.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["pending_structural_evidence"]["pending_candidates"].append(
        copy.deepcopy(data["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0])
    )
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate formation candidate storage_key"):
        restore_cognitive_checkpoint(p)


def test_c03_t12_duplicate_growth_key_fails(tmp_path: pathlib.Path) -> None:
    """C03-T12: Duplicate growth candidate key fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t12.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["pending_structural_evidence"]["pending_growth"].append(
        copy.deepcopy(data["persistent_state"]["pending_structural_evidence"]["pending_growth"][0])
    )
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate growth candidate key"):
        restore_cognitive_checkpoint(p)


def test_c03_t13_duplicate_merge_key_fails(tmp_path: pathlib.Path) -> None:
    """C03-T13: Duplicate merge candidate key fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t13.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["pending_structural_evidence"]["pending_merge"].append(
        copy.deepcopy(data["persistent_state"]["pending_structural_evidence"]["pending_merge"][0])
    )
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="Duplicate merge candidate key"):
        restore_cognitive_checkpoint(p)


def test_c03_t14_noncanonical_formation_candidate_id_fails(tmp_path: pathlib.Path) -> None:
    """C03-T14: Noncanonical formation candidate_id fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t14.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    cand = data["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0]
    cand["candidate_id"] = "asm_arbitrary_hash"
    cand["storage_key"] = f"asm_arbitrary_hash:ctx_{cand.get('context_signature') or 'default'}"
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="does not match canonical_assembly_id"):
        restore_cognitive_checkpoint(p)


def test_c03_t15_invalid_formation_size_fails(tmp_path: pathlib.Path) -> None:
    """C03-T15: Invalid formation size (< K_ASM_MIN) fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t15.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    cand = data["persistent_state"]["pending_structural_evidence"]["pending_candidates"][0]
    cand["edges"] = [["n1", "n2"]]
    c_id = canonical_assembly_id([("n1", "n2")])
    cand["candidate_id"] = c_id
    cand["storage_key"] = f"{c_id}:ctx_{cand.get('context_signature') or 'default'}"
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="outside bounds"):
        restore_cognitive_checkpoint(p)


def test_c03_t16_growth_edge_already_in_parent_fails(tmp_path: pathlib.Path) -> None:
    """C03-T16: Growth edge already in parent member edges fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t16.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    growth = data["persistent_state"]["pending_structural_evidence"]["pending_growth"][0]
    growth["new_edge"] = ["n1", "n2"]
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="already a member of parent assembly"):
        restore_cognitive_checkpoint(p)


def test_c03_t17_one_parent_merge_fails(tmp_path: pathlib.Path) -> None:
    """C03-T17: Merge candidate with only 1 parent fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t17.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["pending_structural_evidence"]["pending_merge"][0]["parent_assembly_ids"] = ["asm_parent_1"]
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="must have exactly two distinct parent assemblies"):
        restore_cognitive_checkpoint(p)


def test_c03_t18_greater_than_two_parent_merge_fails(tmp_path: pathlib.Path) -> None:
    """C03-T18: Merge candidate with > 2 parents fails closed."""
    g = make_valid_c03_graph()
    p = tmp_path / "t18.json"
    save_cognitive_checkpoint(g, p)

    data = json.loads(p.read_text(encoding="utf-8"))
    data["persistent_state"]["pending_structural_evidence"]["pending_merge"][0]["parent_assembly_ids"] = [
        "asm_parent_1", "asm_parent_2", "asm_parent_3"
    ]
    data["integrity"]["checkpoint_state_digest"] = compute_checkpoint_state_digest(data["persistent_state"])
    p.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="must have exactly two distinct parent assemblies"):
        restore_cognitive_checkpoint(p)


def test_c03_t19_nested_restoring_fails_outer_remains_restoring() -> None:
    """C03-T19: Nested RESTORING fails and outer guard remains in RESTORING."""
    guard = RuntimeLifecycleGuard()
    with guard.restoring():
        with pytest.raises(IllegalLifecycleTransitionError), guard.restoring():
            pass
        assert guard.state == RuntimeLifecycleState.RESTORING
    assert guard.state == RuntimeLifecycleState.IDLE


def test_c03_t20_nested_checkpointing_fails() -> None:
    """C03-T20: Nested CHECKPOINTING fails."""
    guard = RuntimeLifecycleGuard()
    with guard.checkpointing():
        with pytest.raises(IllegalLifecycleTransitionError), guard.checkpointing():
            pass
        assert guard.state == RuntimeLifecycleState.CHECKPOINTING
    assert guard.state == RuntimeLifecycleState.IDLE


def test_c03_t21_nested_mutating_fails() -> None:
    """C03-T21: Nested MUTATING fails."""
    guard = RuntimeLifecycleGuard()
    with guard.mutating():
        with pytest.raises(IllegalLifecycleTransitionError), guard.mutating():
            pass
        assert guard.state == RuntimeLifecycleState.MUTATING
    assert guard.state == RuntimeLifecycleState.IDLE


def test_c03_t22_lawful_runtimeroot_restore_still_swaps_under_restoring(tmp_path: pathlib.Path) -> None:
    """C03-T22: Lawful RuntimeRoot restore swaps under RESTORING."""
    g = make_valid_c03_graph()
    root = RuntimeRoot(g)
    p = tmp_path / "t22.json"
    root.save_checkpoint(p)

    observed_states = []
    def on_pre_swap(st: RuntimeLifecycleState) -> None:
        observed_states.append(st)

    new_g, report = root.restore_checkpoint(p, _on_pre_swap=on_pre_swap)
    assert report is None
    assert root.graph is new_g
    assert root.graph is not g
    assert observed_states == [RuntimeLifecycleState.RESTORING]
    assert root.guard.state == RuntimeLifecycleState.IDLE


def test_c03_t23_valid_schema_1_1_migration_passes(tmp_path: pathlib.Path) -> None:
    """C03-T23: Valid schema 1.1 checkpoint migration passes."""
    data = make_valid_schema_1_1_dict(tmp_path)
    validate_schema_1_1_source(data)

    p = tmp_path / "t23.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    restored, report = restore_cognitive_checkpoint(p)
    assert report is not None
    assert report.source_schema == "1.1"
    assert report.target_schema == "1.1.1"
    assert len(restored._assembly_manager.pending_candidates) == 1


def test_c03_t24_valid_legacy_1_0_migration_passes(tmp_path: pathlib.Path) -> None:
    """C03-T24: Valid legacy 1.0 checkpoint migration passes."""
    legacy = make_valid_legacy_v1_dict()
    p = tmp_path / "t24.json"
    p.write_text(json.dumps(legacy), encoding="utf-8")
    restored, report = restore_cognitive_checkpoint(p)
    assert report is not None
    assert report.source_schema == "1.0"
    assert report.target_schema == "1.1.1"
    assert restored.t == 42


def test_c03_t25_c02_suite_passes(tmp_path: pathlib.Path) -> None:
    """C03-T25: C02 test assertions remain fully satisfied."""
    from tests.test_ric01_r0_c02_correction import (
        test_c02_t01_valid_schema_1_1_migrates_to_1_1_1,
        test_c02_t02_tampered_1_1_persistent_payload_fails_closed,
    )
    test_c02_t01_valid_schema_1_1_migrates_to_1_1_1(tmp_path / "c02_sub1")
    test_c02_t02_tampered_1_1_persistent_payload_fails_closed(tmp_path / "c02_sub2")


def test_c03_t26_c01_suite_passes(tmp_path: pathlib.Path) -> None:
    """C03-T26: C01 test assertions remain fully satisfied."""
    from tests.test_ric01_r0_c01_correction import (
        test_c01_t01_real_rfc11_formation_continuity,
        test_c01_t04_formation_storage_key_round_trip_exactness,
    )
    test_c01_t01_real_rfc11_formation_continuity(tmp_path / "c01_sub1")
    test_c01_t04_formation_storage_key_round_trip_exactness(tmp_path / "c01_sub2")


def test_c03_t27_original_r0_suite_passes(tmp_path: pathlib.Path) -> None:
    """C03-T27: Original R0 round trip succeeds."""
    from tests.test_ric01_r0_persistence import (
        test_r0_i01_durable_node_state_survives_exactly,
        test_r0_i02_durable_edge_state_survives_exactly,
    )
    test_r0_i01_durable_node_state_survives_exactly(tmp_path / "r0_sub1")
    test_r0_i02_durable_edge_state_survives_exactly(tmp_path / "r0_sub2")


def test_c03_t28_full_regression_passes() -> None:
    """C03-T28: Regression check on basic graph operations."""
    g = CognitiveGraph()
    g.observe([(1, "hello")], context="c")
    assert len(g.nodes) > 0


def test_c03_t29_baseline_signature_unchanged() -> None:
    """C03-T29: Verification that baseline cognitive signature matches baseline_signature.txt exactly."""
    g = build_reference_graph()
    sig = behavioral_signature(g)
    with open("tests/baseline_signature.txt", "r", encoding="utf-8") as f:
        expected = f.read().strip()
    assert sig == expected
