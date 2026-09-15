"""RIC-01 / R2: Traceable Requirement, Test Obligation, and Adversarial Matrix.

Authoritative verification matrix for:
- 58 Architecture Invariants (R2-I01 through R2-I58)
- 89 Test Obligations (T01 through T89)
- 17 Adversarial Scenarios (A through Q)
- Execution Mode Conformance (TRANSIENT_ONLY vs AUTHORIZED_PERSISTENT)
"""
import importlib

import pytest

from dgca.observation import (
    R2_OBSERVATION_SEMANTICS_DIGEST,
    ExecutionMode,
    compute_r2_observation_semantics_digest,
)
from tests.test_ric01_r2_authorizer import SimpleObservationAuthorizer
from tests.test_ric01_r2_pir03 import _make_bridge

# ─────────────────────────────────────────────────────────── Invariants R2-I01 .. R2-I58
FROZEN_R2_INVARIANTS: dict[str, str] = {
    "R2-I01": "Trusted occurrence metadata, not raw content, owns RootExternalEpisode identity.",
    "R2-I02": "Raw user text/code cannot grant persistent-learning authority.",
    "R2-I03": "R2-v1 protocol version is exactly R2-OBS-1.0.",
    "R2-I04": "The frozen R2 semantics registry hashes to the corrected v1.1.1 digest.",
    "R2-I05": "Same event descriptor canonicalizes to the same EventDescriptorDigest.",
    "R2-I06": "Encoder emitted order is authoritative and never sorted.",
    "R2-I07": "child_index is zero-based emitted episode order.",
    "R2-I08": "Same event/mode/protocol/encoder output derives the same ordered MicroEpisodeIDs.",
    "R2-I09": "TRANSIENT_ONLY changes no persistent graph field.",
    "R2-I10": "TRANSIENT_ONLY changes no RFC11 pending structural evidence.",
    "R2-I11": "TRANSIENT_ONLY changes no R1 causal commit ledger record.",
    "R2-I12": "AUTHORIZED_PERSISTENT requires a trusted authorizer and opaque capability.",
    "R2-I13": "Missing authorizer means DENY ALL persistent observation.",
    "R2-I14": "Identity values alone never confer mutation authority.",
    "R2-I15": "No boolean convenience authorization path exists.",
    "R2-I16": "One encoded IngressEvent maps to one R1 persistent owner transaction.",
    "R2-I17": "Persistent transport replay executes zero additional graph mutation.",
    "R2-I18": "Persistent transport replay executes zero additional RFC11 vote.",
    "R2-I19": "All MicroEpisodes from one ingress preserve the same RootExternalEpisodeID.",
    "R2-I20": "RFC11 evidence is a strict provenance-classified subset of observation relations.",
    "R2-I21": "Simultaneous ordered pairs may be RFC11 external evidence.",
    "R2-I22": "Sequence same-step and adjacent-step ordered pairs may be RFC11 external evidence.",
    "R2-I23": "Sequence nonadjacent temporal pairs never vote in RFC11 under R2-v1.",
    "R2-I24": "Synthetic ev: role edges never vote as independent RFC11 evidence in R2-v1.",
    "R2-I25": "Concept/generalization/reasoning/generated edges never vote as external evidence.",
    "R2-I26": "One Root cannot create multiple independent votes for one RFC11 candidate.",
    "R2-I27": "Novel transient nodes require no persistent graph node.",
    "R2-I28": "Explicit current observation binding requires no persistent graph edge.",
    "R2-I29": "A TBR is derived only from explicit canonical MicroEpisode structure.",
    "R2-I30": "Same root/time/context/coactivation alone never authorizes a TBR.",
    "R2-I31": "Canonical node receipts carry deterministic MicroEpisode-derived ReceiptIDs.",
    "R2-I32": "Canonical Edge receipts exist only for live gate-open observation-relation Edges.",
    "R2-I33": "A lawful Edge receipt may exist even when that relation is RFC11-ineligible.",
    "R2-I34": "TBR IDs are deterministic descendants of MicroEpisodeID.",
    "R2-I35": "Node receipt scope_refs explicitly contain each TBR scope in which that occurrence participates.",
    "R2-I36": "Receipt slots are contiguous and deterministic.",
    "R2-I37": "TBR binding indexes are contiguous and deterministic.",
    "R2-I38": "Receipt/TBR IDs are rederived and validated before RFC12 construction.",
    "R2-I39": "TBR descriptor authority and member scope are revalidated against the MicroEpisode descriptor.",
    "R2-I40": "Legacy numeric RFC12 coordinates never become causal authority.",
    "R2-I41": "Assembly selection may occur in transient mode without structural voting.",
    "R2-I42": "RFC11 record_participation may occur only inside the authorized R1 command.",
    "R2-I43": "Explicit contradiction persistence may occur only inside the authorized R1 command.",
    "R2-I44": "One canonical SDCR is built per observable MicroEpisode.",
    "R2-I45": "Canonical RFC12 causal_parent_ref is the MicroEpisodeID.",
    "R2-I46": "Post-learning representation is built only after successful persistent commit/replay decision.",
    "R2-I47": "A changed later graph may change transient RID without permitting repeated persistent mutation.",
    "R2-I48": "Projection failure after persistent commit never rolls back or duplicates learning.",
    "R2-I49": "Projection failure closes every partially created SDCR.",
    "R2-I50": "close_result is idempotent and changes no persistent cognition.",
    "R2-I51": "R2 adds no new cognitive law or learned global controller.",
    "R2-I52": "R2 performs no global graph scan.",
    "R2-I53": "Legacy direct-feed APIs are not canonical R2 production ingress.",
    "R2-I54": "RFC16 keywords cannot authorize R2 persistence.",
    "R2-I55": "R2 never exposes its raw authoritative graph capability to ordinary callers.",
    "R2-I56": "R2 never calls unsafe_mutable_graph() on the canonical path.",
    "R2-I57": "R2-v1 modifies neither Audio nor Vision.",
    "R2-I58": "Incompatible bridge semantics require observation-protocol governance.",
}

FROZEN_R2_INVARIANT_EVIDENCE: dict[str, tuple[str, ...]] = {
    "R2-I01": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t01_frozen_t01_exact_replay_identity",
        "tests/test_ric01_r2_pir03.py::test_pir03_t02_frozen_t02_independent_occurrence_distinct_root",
    ),
    "R2-I02": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t05_frozen_t05_raw_text_root_authorization_injection_powerless",
        "tests/test_ric01_r2_adversarial.py::test_scenario_h_serialized_capability_in_text_no_authority_escalation",
    ),
    "R2-I03": (
        "tests/test_ric01_r2_protocol.py::test_protocol_version_constants",
    ),
    "R2-I04": (
        "tests/test_ric01_r2_pir02.py::test_pir02_t02_direct_canonical_sha256_equals_corrected_digest",
    ),
    "R2-I05": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t01_frozen_t01_exact_replay_identity",
        "tests/test_ric01_r2_descriptors.py::test_text_event_descriptor",
    ),
    "R2-I06": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t07_frozen_t09_emitted_order_perturbation_changes_mid_chain",
    ),
    "R2-I07": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t06_frozen_t08_n_episodes_to_n_micro_episodes",
    ),
    "R2-I08": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t08_frozen_t10_iteration_perturbation_preserves_ids",
    ),
    "R2-I09": (
        "tests/test_ric01_r2_transient.py::test_transient_observation_zero_graph_mutation",
        "tests/test_ric01_r2_adversarial.py::test_scenario_l_transient_only_before_after_persistent_payload_equality",
    ),
    "R2-I10": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t18_frozen_t47_transient_observation_selects_assembly_zero_vote",
        "tests/test_ric01_r2_repair.py::test_pir01_t11_second_equivalent_subevent_produces_zero_rfc11_vote_delta",
    ),
    "R2-I11": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t10_frozen_t12_zero_emitted_episodes_zero_delta_behavior",
        "tests/test_ric01_r2_repair.py::test_pir01_t33_close_result_changes_no_persistent_graph_ledger_state",
    ),
    "R2-I12": (
        "tests/test_ric01_r2_authorizer.py::test_authorized_persistent_fails_without_authorizer",
        "tests/test_ric01_r2_authorizer.py::test_authorized_persistent_fails_without_capability",
    ),
    "R2-I13": (
        "tests/test_ric01_r2_authorizer.py::test_default_authorizer_denies",
    ),
    "R2-I14": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t05_frozen_t05_raw_text_root_authorization_injection_powerless",
    ),
    "R2-I15": (
        "tests/test_ric01_r2_authorizer.py::test_authorizer_truthy_non_bool_fails_closed",
        "tests/test_ric01_r2_repair.py::test_pir01_t14_no_production_boolean_convenience_authorization_path",
    ),
    "R2-I16": (
        "tests/test_ric01_r2_persistent.py::test_authorized_persistent_single_command_and_replay",
    ),
    "R2-I17": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t23_frozen_t70_replay_after_unrelated_graph_change_zero_persistent_delta",
        "tests/test_ric01_r2_repair.py::test_pir01_t10_second_equivalent_subevent_produces_zero_graph_delta",
    ),
    "R2-I18": (
        "tests/test_ric01_r2_repair.py::test_pir01_t11_second_equivalent_subevent_produces_zero_rfc11_vote_delta",
    ),
    "R2-I19": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t06_frozen_t08_n_episodes_to_n_micro_episodes",
    ),
    "R2-I20": (
        "tests/test_ric01_r2_rfc11.py::test_rfc11_sequence_adjacent_vs_nonadjacent",
        "tests/test_ric01_r2_rfc11.py::test_rfc11_firewall_excludes_role_cat_hub_inst",
    ),
    "R2-I21": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t22_frozen_t69_fifth_independent_rfc11_vote_forms_assembly_visible_in_same_event_sdcr",
    ),
    "R2-I22": (
        "tests/test_ric01_r2_repair.py::test_pir01_t23_reverse_adjacent_sequence_edge_is_rfc11_eligible",
    ),
    "R2-I23": (
        "tests/test_ric01_r2_rfc11.py::test_rfc11_sequence_adjacent_vs_nonadjacent",
        "tests/test_ric01_r2_adversarial.py::test_scenario_n_three_step_sequence_step0_step2_never_rfc11_evidence",
    ),
    "R2-I24": (
        "tests/test_ric01_r2_adversarial.py::test_scenario_o_synthetic_ev_edge_never_rfc11_vote",
        "tests/test_ric01_r2_rfc11.py::test_rfc11_firewall_excludes_role_cat_hub_inst",
    ),
    "R2-I25": (
        "tests/test_ric01_r2_adversarial.py::test_scenario_p_concept_generalization_side_effect_edge_never_rfc11_vote",
    ),
    "R2-I26": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t20_frozen_t50_many_micro_episodes_same_root_do_not_multiply_candidate_vote",
        "tests/test_ric01_r2_adversarial.py::test_scenario_a_500_calls_one_root_one_independent_vote",
    ),
    "R2-I27": (
        "tests/test_ric01_r2_transient.py::test_transient_observation_zero_graph_mutation",
    ),
    "R2-I28": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t11_frozen_t22_coactivation_alone_cannot_create_tbr",
    ),
    "R2-I29": (
        "tests/test_ric01_r2_receipts.py::test_batch_validation_rejects_invented_tbr_scope",
        "tests/test_ric01_r2_adversarial.py::test_scenario_c_forged_tbr_valid_hash_wrong_descriptor_authority_rejected",
    ),
    "R2-I30": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t11_frozen_t22_coactivation_alone_cannot_create_tbr",
        "tests/test_ric01_r2_pir03.py::test_pir03_t12_frozen_t23_same_root_alone_cannot_create_tbr",
        "tests/test_ric01_r2_pir03.py::test_pir03_t13_frozen_t24_same_context_alone_cannot_create_tbr",
        "tests/test_ric01_r2_pir03.py::test_pir03_t14_frozen_t25_same_timestamp_alone_cannot_create_tbr",
    ),
    "R2-I31": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t08_frozen_t10_iteration_perturbation_preserves_ids",
        "tests/test_ric01_r2_repair.py::test_pir01_t18_node_receipt_scope_begins_with_micro_episode_id",
    ),
    "R2-I32": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t15_frozen_t44_live_gate_open_relation_edge_receipt",
        "tests/test_ric01_r2_pir03.py::test_pir03_t16_frozen_t45_gate_closed_relation_no_edge_receipt",
    ),
    "R2-I33": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t15_frozen_t44_live_gate_open_relation_edge_receipt",
        "tests/test_ric01_r2_adversarial.py::test_scenario_n_three_step_sequence_step0_step2_never_rfc11_evidence",
    ),
    "R2-I34": (
        "tests/test_ric01_r2_pir02.py::test_pir02_t08_derive_expected_receipt_plan_purity_and_fields",
    ),
    "R2-I35": (
        "tests/test_ric01_r2_repair.py::test_pir01_t18_node_receipt_scope_begins_with_micro_episode_id",
        "tests/test_ric01_r2_adversarial.py::test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected",
    ),
    "R2-I36": (
        "tests/test_ric01_r2_receipts.py::test_batch_validation_rejects_slot_gap",
    ),
    "R2-I37": (
        "tests/test_ric01_r2_repair.py::test_pir01_t15_simultaneous_duplicate_occurrences_preserved_in_tbr_members",
        "tests/test_ric01_r2_pir02.py::test_pir02_t14_lawful_duplicate_node_occurrences_pass_validation",
    ),
    "R2-I38": (
        "tests/test_ric01_r2_pir02.py::test_pir02_t08_derive_expected_receipt_plan_purity_and_fields",
    ),
    "R2-I39": (
        "tests/test_ric01_r2_adversarial.py::test_scenario_c_forged_tbr_valid_hash_wrong_descriptor_authority_rejected",
    ),
    "R2-I40": (
        "tests/test_ric01_r2_repair.py::test_pir01_t20_exact_r2relation_edge_scope_and_relation_index",
    ),
    "R2-I41": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t18_frozen_t47_transient_observation_selects_assembly_zero_vote",
    ),
    "R2-I42": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t19_frozen_t49_authorized_path_records_only_eligible_verified_evidence",
        "tests/test_ric01_r2_pir03.py::test_pir03_t22_frozen_t69_fifth_independent_rfc11_vote_forms_assembly_visible_in_same_event_sdcr",
    ),
    "R2-I43": (
        "tests/test_ric01_r2_adversarial.py::test_scenario_q_contradiction_only_transient_endpoint_receipts_tbr_graph_unchanged",
    ),
    "R2-I44": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t06_frozen_t08_n_episodes_to_n_micro_episodes",
        "tests/test_ric01_r2_repair.py::test_pir01_t27_per_micro_episode_trace_contains_batch_assemblies_rid",
    ),
    "R2-I45": (
        "tests/test_ric01_r2_transient.py::test_transient_observation_generates_valid_sdcr",
    ),
    "R2-I46": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t21_frozen_t68_first_authorized_learning_exposes_learned_edge_in_same_event_sdcr",
    ),
    "R2-I47": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t24_frozen_t71_changed_graph_may_change_replay_rid",
    ),
    "R2-I48": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t25_frozen_t72_commit_survives_projection_failure",
    ),
    "R2-I49": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t26_frozen_t73_partial_sdcrs_close",
        "tests/test_ric01_r2_adversarial.py::test_scenario_j_commit_then_forced_later_child_rfc12_failure",
    ),
    "R2-I50": (
        "tests/test_ric01_r2_pir02.py::test_pir02_t16_close_result_direct_idempotency_engine_called_once",
        "tests/test_ric01_r2_repair.py::test_pir01_t33_close_result_changes_no_persistent_graph_ledger_state",
    ),
    "R2-I51": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t38_frozen_t88_r1_protocol_digest_unchanged",
        "tests/test_ric01_r2_pir03.py::test_pir03_t39_frozen_t89_legacy_baseline_behavior_regression_compatible",
    ),
    "R2-I52": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t19_frozen_t49_authorized_path_records_only_eligible_verified_evidence",
    ),
    "R2-I53": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t39_frozen_t89_legacy_baseline_behavior_regression_compatible",
    ),
    "R2-I54": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t05_frozen_t05_raw_text_root_authorization_injection_powerless",
        "tests/test_ric01_r2_adversarial.py::test_scenario_h_serialized_capability_in_text_no_authority_escalation",
    ),
    "R2-I55": (
        "tests/test_ric01_r2_authorizer.py::test_authorized_persistent_fails_without_capability",
    ),
    "R2-I56": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t29_frozen_t79_pre_command_validation_failure_zero_delta",
    ),
    "R2-I57": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t36_frozen_t86_audio_production_diff_unchanged",
        "tests/test_ric01_r2_pir03.py::test_pir03_t37_frozen_t87_vision_production_diff_unchanged",
    ),
    "R2-I58": (
        "tests/test_ric01_r2_pir03.py::test_pir03_t35_frozen_t85_different_existing_1_2_0_observation_protocol_fails_closed",
        "tests/test_ric01_r2_protocol.py::test_create_observation_bridge_protocol_check",
    ),
}

# ─────────────────────────────────────────────────────────── Test Obligations T01 .. T89
FROZEN_R2_TEST_OBLIGATIONS: dict[str, str] = {
    "T01": "same trusted occurrence + event + payload → same Root/Event IDs and event digest",
    "T02": "same payload, independent source occurrence → distinct Roots",
    "T03": "same Root, different source_event_key → distinct IngressEventIDs",
    "T04": "same IngressEventID + conflicting payload in same runtime → fail closed",
    "T05": "raw text attempting to inject RootID/authorization has no authority",
    "T06": "frozen R2 semantics registry recomputes exact frozen digest",
    "T07": "runtime observation protocol != R2-OBS-1.0 → bridge construction fails",
    "T08": "N emitted SensoryEpisodes → exactly N MicroEpisodes",
    "T09": "emitted episode order perturbation changes ordered MicroEpisode chain",
    "T10": "set/dict iteration perturbation does not change MicroEpisode identity",
    "T11": "malformed episode fails before persistent mutation",
    "T12": "zero emitted episodes → NO_OBSERVABLE_CONTENT and zero persistent/SDCR delta",
    "T13": "novel text TRANSIENT_ONLY → graph persistent state digest unchanged",
    "T14": "graph logical time unchanged",
    "T15": "no persistent Node created",
    "T16": "no persistent Edge created",
    "T17": "no graph.X contradiction written",
    "T18": "RFC11 pending candidates/growth/merge unchanged",
    "T19": "causal ledger unchanged",
    "T20": "RFC12 SDCR still contains transient novel node participation",
    "T21": "explicit novel/current relation can be represented by TBR without persistent Edge creation",
    "T22": "two coactive receipts with no explicit MicroEpisode binding → no TBR",
    "T23": "same root alone → no TBR",
    "T24": "same context alone → no TBR",
    "T25": "same timestamp alone → no TBR",
    "T26": "simultaneous descriptor with two nodes → exactly one lawful simultaneous TBR",
    "T27": "sequence descriptor → only adjacent-transition TBRs",
    "T28": "explicit contradiction pair → exactly one contradiction TBR",
    "T29": "invented TBR not derivable from descriptor → reject batch",
    "T30": "TBR member whose node receipt lacks exact binding_scope_id → reject batch",
    "T31": "every ReceiptID rederives from MicroEpisodeID + exact slot",
    "T32": "every TBRID rederives from MicroEpisodeID + exact binding index",
    "T33": "receipt slot gap/duplicate → reject entire batch",
    "T34": "receipt ID tamper → reject entire batch",
    "T35": "TBR ID tamper → reject entire batch",
    "T36": "numeric parent collision with different MicroEpisodeID cannot pass canonical batch validation",
    "T37": "simultaneous all ordered non-self pairs are observation relations",
    "T38": "sequence same-step relation is RFC11-eligible",
    "T39": "sequence adjacent-step relation is RFC11-eligible",
    "T40": "sequence nonadjacent relation may be a read-only Edge receipt but cannot vote in RFC11",
    "T41": "synthetic ev: role Edge cannot vote in RFC11",
    "T42": "concept/generalization Edge cannot vote in RFC11",
    "T43": "no graph-global diff is used to derive evidence",
    "T44": "known gate-open observation relation → canonical Edge receipt accepted",
    "T45": "gate-closed Edge → no Edge receipt",
    "T46": "read-only Edge receipt does not reinforce W/n/context hits",
    "T47": "transient observation can select an existing Assembly",
    "T48": "transient observation creates zero RFC11 vote",
    "T49": "authorized persistent observation records only eligible verified external evidence",
    "T50": "N MicroEpisodes under one Root cannot add N independent votes to same candidate",
    "T51": "authorized ingress first execution → one R1 transaction",
    "T52": "exact persistent retry → callback not executed",
    "T53": "retry → graph persistent state digest unchanged",
    "T54": "retry → RFC11 vote set unchanged",
    "T55": "same Root + transport-different subevent compiling to exact same mutation intent → same R1 TxID",
    "T56": "distinct Root + same content → distinct R1 TxID and independent evidence",
    "T57": "transient contradiction → TBR + endpoint receipts, graph.X unchanged",
    "T58": "authorized contradiction → graph.X written inside R1 command",
    "T59": "contradiction does not become RFC11 positive Edge evidence",
    "T60": "authorizer=None rejects persistent mode",
    "T61": "bare boolean authorization equivalent does not exist / is rejected",
    "T62": "authorizer false → zero mutation",
    "T63": "authorizer exception → zero mutation",
    "T64": "non-bool authorizer result → fail closed",
    "T65": "ordinary \"fact: X\" has no persistent authority",
    "T66": "ordinary \"correction: X\" has no persistent authority",
    "T67": "valid Root/Event IDs without capability have no persistent authority",
    "T68": "first authorized learning may expose newly learned direct Edge in same event's SDCR",
    "T69": "fifth independent RFC11 vote may form Assembly visible in same event's post-commit SDCR",
    "T70": "replay after unrelated graph change still has zero persistent delta",
    "T71": "replay after graph change may lawfully produce different current-state RID",
    "T72": "persistent commit succeeds then child projection fails → commit remains recorded",
    "T73": "same failure closes all earlier child SDCRs",
    "T74": "retry after projection failure → R1 replay + successful projection without double learning",
    "T75": "close_result closes all result SDCRs",
    "T76": "second close_result call is harmless",
    "T77": "close_result changes no persistent state digest or ledger",
    "T78": "encoder exception → zero persistent delta",
    "T79": "pre-command validation failure → zero persistent delta",
    "T80": "callback partial mutation + exception → R1 MUTATION_FAILED",
    "T81": "fail-stop runtime cannot canonical-save or accept further persistent commands",
    "T82": "R2-OBS-1.0 checkpoint restores only under matching expected protocol",
    "T83": "no checkpoint schema bump beyond 1.2.0",
    "T84": "pre-R1 1.1.1 migration may explicitly target R2-OBS-1.0 through existing R1 migration",
    "T85": "no automatic reinterpretation of an existing different 1.2.0 observation protocol",
    "T86": "Audio files unchanged",
    "T87": "Vision files unchanged",
    "T88": "R1 causal identity protocol digest unchanged",
    "T89": "legacy baseline behavior remains regression-compatible outside canonical R2 path",
}

FROZEN_R2_TEST_EVIDENCE: dict[str, tuple[str, ...]] = {
    "T01": ("tests/test_ric01_r2_pir03.py::test_pir03_t01_frozen_t01_exact_replay_identity",),
    "T02": ("tests/test_ric01_r2_pir03.py::test_pir03_t02_frozen_t02_independent_occurrence_distinct_root",),
    "T03": ("tests/test_ric01_r2_pir03.py::test_pir03_t03_frozen_t03_same_root_different_event_keys_distinct_event_ids",),
    "T04": ("tests/test_ric01_r2_pir03.py::test_pir03_t04_frozen_t04_live_event_id_conflict",),
    "T05": ("tests/test_ric01_r2_pir03.py::test_pir03_t05_frozen_t05_raw_text_root_authorization_injection_powerless",),
    "T06": ("tests/test_ric01_r2_pir04.py::test_pir04_t06_frozen_t06_semantics_registry_recomputes_exact_digest",),
    "T07": ("tests/test_ric01_r2_pir04.py::test_pir04_t07_frozen_t07_protocol_mismatch_fails_bridge_construction",),
    "T08": ("tests/test_ric01_r2_pir03.py::test_pir03_t06_frozen_t08_n_episodes_to_n_micro_episodes",),
    "T09": ("tests/test_ric01_r2_pir03.py::test_pir03_t07_frozen_t09_emitted_order_perturbation_changes_mid_chain",),
    "T10": ("tests/test_ric01_r2_pir03.py::test_pir03_t08_frozen_t10_iteration_perturbation_preserves_ids",),
    "T11": ("tests/test_ric01_r2_pir03.py::test_pir03_t09_frozen_t11_malformed_emitted_episode_fails_before_persistent_mutation",),
    "T12": ("tests/test_ric01_r2_pir03.py::test_pir03_t10_frozen_t12_zero_emitted_episodes_zero_delta_behavior",),
    "T13": ("tests/test_ric01_r2_pir04.py::test_pir04_t13_frozen_t13_transient_only_state_digest_unchanged",),
    "T14": ("tests/test_ric01_r2_pir04.py::test_pir04_t14_frozen_t14_transient_only_logical_time_unchanged",),
    "T15": ("tests/test_ric01_r2_pir04.py::test_pir04_t15_frozen_t15_transient_only_no_persistent_node_created",),
    "T16": ("tests/test_ric01_r2_pir04.py::test_pir04_t16_frozen_t16_transient_only_no_persistent_edge_created",),
    "T17": ("tests/test_ric01_r2_pir04.py::test_pir04_t17_frozen_t17_transient_only_no_graph_contradiction_written",),
    "T18": ("tests/test_ric01_r2_pir04.py::test_pir04_t18_frozen_t18_transient_only_rfc11_pending_queues_unchanged",),
    "T19": ("tests/test_ric01_r2_pir04.py::test_pir04_t19_frozen_t19_transient_only_causal_ledger_unchanged",),
    "T20": ("tests/test_ric01_r2_pir04.py::test_pir04_t20_frozen_t20_transient_only_sdcr_contains_novel_node_participation",),
    "T21": ("tests/test_ric01_r2_pir04.py::test_pir04_t21_frozen_t21_explicit_novel_relation_represented_by_tbr_without_persistent_edge",),
    "T22": ("tests/test_ric01_r2_pir03.py::test_pir03_t11_frozen_t22_coactivation_alone_cannot_create_tbr",),
    "T23": ("tests/test_ric01_r2_pir03.py::test_pir03_t12_frozen_t23_same_root_alone_cannot_create_tbr",),
    "T24": ("tests/test_ric01_r2_pir03.py::test_pir03_t13_frozen_t24_same_context_alone_cannot_create_tbr",),
    "T25": ("tests/test_ric01_r2_pir03.py::test_pir03_t14_frozen_t25_same_timestamp_alone_cannot_create_tbr",),
    "T26": ("tests/test_ric01_r2_pir04.py::test_pir04_t26_frozen_t26_simultaneous_descriptor_two_nodes_one_tbr",),
    "T27": ("tests/test_ric01_r2_pir04.py::test_pir04_t27_frozen_t27_sequence_descriptor_only_adjacent_transition_tbrs",),
    "T28": ("tests/test_ric01_r2_pir04.py::test_pir04_t28_frozen_t28_explicit_contradiction_pair_one_tbr",),
    "T29": ("tests/test_ric01_r2_pir04.py::test_pir04_t29_frozen_t29_invented_tbr_not_derivable_from_descriptor_rejected",),
    "T30": ("tests/test_ric01_r2_pir04.py::test_pir04_t30_frozen_t30_tbr_member_lacking_exact_binding_scope_rejected",),
    "T31": ("tests/test_ric01_r2_pir04.py::test_pir04_t31_frozen_t31_receipt_id_rederives_from_micro_id_and_slot",),
    "T32": ("tests/test_ric01_r2_pir04.py::test_pir04_t32_frozen_t32_tbr_id_rederives_from_micro_id_and_index",),
    "T33": ("tests/test_ric01_r2_pir04.py::test_pir04_t33_frozen_t33_receipt_slot_gap_duplicate_rejects_batch",),
    "T34": ("tests/test_ric01_r2_pir04.py::test_pir04_t34_frozen_t34_receipt_id_tamper_rejects_batch",),
    "T35": ("tests/test_ric01_r2_pir04.py::test_pir04_t35_frozen_t35_tbr_id_tamper_rejects_batch",),
    "T36": ("tests/test_ric01_r2_pir04.py::test_pir04_t36_frozen_t36_numeric_parent_collision_cannot_pass_batch_validation",),
    "T37": ("tests/test_ric01_r2_pir04.py::test_pir04_t37_frozen_t37_simultaneous_all_ordered_non_self_pairs_are_relations",),
    "T38": ("tests/test_ric01_r2_pir04.py::test_pir04_t38_frozen_t38_sequence_same_step_relation_rfc11_eligible",),
    "T39": ("tests/test_ric01_r2_pir04.py::test_pir04_t39_frozen_t39_sequence_adjacent_step_relation_rfc11_eligible",),
    "T40": ("tests/test_ric01_r2_pir04.py::test_pir04_t40_frozen_t40_sequence_nonadjacent_relation_no_rfc11_vote",),
    "T41": ("tests/test_ric01_r2_pir04.py::test_pir04_t41_frozen_t41_synthetic_ev_role_edge_cannot_vote_rfc11",),
    "T42": ("tests/test_ric01_r2_pir04.py::test_pir04_t42_frozen_t42_concept_generalization_edge_cannot_vote_rfc11",),
    "T43": ("tests/test_ric01_r2_pir04.py::test_pir04_t43_frozen_t43_no_graph_global_diff_used_to_derive_evidence",),
    "T44": ("tests/test_ric01_r2_pir03.py::test_pir03_t15_frozen_t44_live_gate_open_relation_edge_receipt",),
    "T45": ("tests/test_ric01_r2_pir03.py::test_pir03_t16_frozen_t45_gate_closed_relation_no_edge_receipt",),
    "T46": ("tests/test_ric01_r2_pir03.py::test_pir03_t17_frozen_t46_read_only_edge_receipt_changes_no_w_n_context",),
    "T47": ("tests/test_ric01_r2_pir03.py::test_pir03_t18_frozen_t47_transient_observation_selects_assembly_zero_vote",),
    "T48": ("tests/test_ric01_r2_pir04.py::test_pir04_t48_frozen_t48_transient_observation_creates_zero_rfc11_vote",),
    "T49": ("tests/test_ric01_r2_pir03.py::test_pir03_t19_frozen_t49_authorized_path_records_only_eligible_verified_evidence",),
    "T50": ("tests/test_ric01_r2_pir03.py::test_pir03_t20_frozen_t50_many_micro_episodes_same_root_do_not_multiply_candidate_vote",),
    "T51": ("tests/test_ric01_r2_pir04.py::test_pir04_t51_frozen_t51_authorized_ingress_first_execution_one_r1_tx",),
    "T52": ("tests/test_ric01_r2_pir04.py::test_pir04_t52_frozen_t52_exact_persistent_retry_callback_not_executed",),
    "T53": ("tests/test_ric01_r2_pir04.py::test_pir04_t53_frozen_t53_retry_graph_persistent_state_digest_unchanged",),
    "T54": ("tests/test_ric01_r2_pir04.py::test_pir04_t54_frozen_t54_retry_rfc11_vote_set_unchanged",),
    "T55": ("tests/test_ric01_r2_pir04.py::test_pir04_t55_frozen_t55_same_root_transport_different_subevent_same_intent_same_r1_txid",),
    "T56": ("tests/test_ric01_r2_pir04.py::test_pir04_t56_frozen_t56_distinct_root_same_content_distinct_r1_txid_and_independent_evidence",),
    "T57": ("tests/test_ric01_r2_pir04.py::test_pir04_t57_frozen_t57_transient_contradiction_graph_x_unchanged",),
    "T58": ("tests/test_ric01_r2_pir04.py::test_pir04_t58_frozen_t58_authorized_contradiction_graph_x_written_in_r1_command",),
    "T59": ("tests/test_ric01_r2_pir04.py::test_pir04_t59_frozen_t59_contradiction_does_not_become_rfc11_positive_edge_evidence",),
    "T60": ("tests/test_ric01_r2_pir04.py::test_pir04_t60_frozen_t60_authorizer_none_rejects_persistent_mode",),
    "T61": ("tests/test_ric01_r2_pir04.py::test_pir04_t61_frozen_t61_bare_boolean_auth_equivalent_absent_or_rejected",),
    "T62": ("tests/test_ric01_r2_pir04.py::test_pir04_t62_frozen_t62_authorizer_false_zero_mutation",),
    "T63": ("tests/test_ric01_r2_pir04.py::test_pir04_t63_frozen_t63_authorizer_exception_zero_mutation",),
    "T64": ("tests/test_ric01_r2_pir04.py::test_pir04_t64_frozen_t64_non_bool_authorizer_result_fails_closed",),
    "T65": ("tests/test_ric01_r2_pir04.py::test_pir04_t65_frozen_t65_ordinary_fact_x_no_persistent_authority",),
    "T66": ("tests/test_ric01_r2_pir04.py::test_pir04_t66_frozen_t66_ordinary_correction_x_no_persistent_authority",),
    "T67": ("tests/test_ric01_r2_pir04.py::test_pir04_t67_frozen_t67_valid_root_event_ids_without_capability_no_persistent_authority",),
    "T68": ("tests/test_ric01_r2_pir03.py::test_pir03_t21_frozen_t68_first_authorized_learning_exposes_learned_edge_in_same_event_sdcr",),
    "T69": ("tests/test_ric01_r2_pir03.py::test_pir03_t22_frozen_t69_fifth_independent_rfc11_vote_forms_assembly_visible_in_same_event_sdcr",),
    "T70": ("tests/test_ric01_r2_pir03.py::test_pir03_t23_frozen_t70_replay_after_unrelated_graph_change_zero_persistent_delta",),
    "T71": ("tests/test_ric01_r2_pir03.py::test_pir03_t24_frozen_t71_changed_graph_may_change_replay_rid",),
    "T72": ("tests/test_ric01_r2_pir03.py::test_pir03_t25_frozen_t72_commit_survives_projection_failure",),
    "T73": ("tests/test_ric01_r2_pir03.py::test_pir03_t26_frozen_t73_partial_sdcrs_close",),
    "T74": ("tests/test_ric01_r2_pir03.py::test_pir03_t27_frozen_t74_retry_is_replay_with_successful_projection",),
    "T75": ("tests/test_ric01_r2_pir04.py::test_pir04_t75_frozen_t75_close_result_closes_all_result_sdcrs",),
    "T76": ("tests/test_ric01_r2_pir04.py::test_pir04_t76_frozen_t76_second_close_result_is_harmless",),
    "T77": ("tests/test_ric01_r2_pir04.py::test_pir04_t77_frozen_t77_close_result_changes_no_persistent_digest_or_ledger",),
    "T78": ("tests/test_ric01_r2_pir03.py::test_pir03_t28_frozen_t78_encoder_exception_zero_persistent_delta",),
    "T79": ("tests/test_ric01_r2_pir03.py::test_pir03_t29_frozen_t79_pre_command_validation_failure_zero_delta",),
    "T80": ("tests/test_ric01_r2_pir03.py::test_pir03_t30_frozen_t80_partial_persistent_callback_mutation_exception_mutation_failed",),
    "T81": ("tests/test_ric01_r2_pir03.py::test_pir03_t31_frozen_t81_fail_stop_blocks_save_and_further_persistent_commands",),
    "T82": ("tests/test_ric01_r2_pir03.py::test_pir03_t32_frozen_t82_matching_protocol_restore",),
    "T83": ("tests/test_ric01_r2_pir03.py::test_pir03_t33_frozen_t83_checkpoint_schema_remains_1_2_0",),
    "T84": ("tests/test_ric01_r2_pir03.py::test_pir03_t34_frozen_t84_explicit_pre_r1_migration_target_r2_obs_1_0",),
    "T85": ("tests/test_ric01_r2_pir03.py::test_pir03_t35_frozen_t85_different_existing_1_2_0_observation_protocol_fails_closed",),
    "T86": ("tests/test_ric01_r2_pir03.py::test_pir03_t36_frozen_t86_audio_production_diff_unchanged",),
    "T87": ("tests/test_ric01_r2_pir03.py::test_pir03_t37_frozen_t87_vision_production_diff_unchanged",),
    "T88": ("tests/test_ric01_r2_pir03.py::test_pir03_t38_frozen_t88_r1_protocol_digest_unchanged",),
    "T89": ("tests/test_ric01_r2_pir03.py::test_pir03_t39_frozen_t89_legacy_baseline_behavior_regression_compatible",),
}

# ─────────────────────────────────────────────────────────── Adversarial Scenarios A .. Q
FROZEN_R2_ADVERSARIAL_SCENARIOS: dict[str, str] = {
    "A": "tests/test_ric01_r2_adversarial.py::test_scenario_a_500_calls_one_root_one_independent_vote",
    "B": "tests/test_ric01_r2_adversarial.py::test_scenario_b_repeated_same_node_occurrences_receipts_preserved_dedup",
    "C": "tests/test_ric01_r2_adversarial.py::test_scenario_c_forged_tbr_valid_hash_wrong_descriptor_authority_rejected",
    "D": "tests/test_ric01_r2_adversarial.py::test_scenario_d_forged_tbr_valid_members_wrong_receipt_scope_rejected",
    "E": "tests/test_ric01_r2_adversarial.py::test_scenario_e_same_eventid_same_text_changed_context_conflict",
    "F": "tests/test_ric01_r2_adversarial.py::test_scenario_f_same_root_different_eventid_same_intent_same_r1_txid",
    "G": "tests/test_ric01_r2_adversarial.py::test_scenario_g_independent_root_identical_text_valid_capability_independent_learning",
    "H": "tests/test_ric01_r2_adversarial.py::test_scenario_h_serialized_capability_in_text_no_authority_escalation",
    "I": "tests/test_ric01_r2_adversarial.py::test_scenario_i_authorizer_returns_truthy_non_bool_fails_closed",
    "J": "tests/test_ric01_r2_adversarial.py::test_scenario_j_commit_then_forced_later_child_rfc12_failure",
    "K": "tests/test_ric01_r2_adversarial.py::test_scenario_k_double_close_result_no_persistent_delta_no_failure",
    "L": "tests/test_ric01_r2_adversarial.py::test_scenario_l_transient_only_before_after_persistent_payload_equality",
    "M": "tests/test_ric01_r2_adversarial.py::test_scenario_m_iteration_perturbation_identical_canonical_ids_slots_bindings",
    "N": "tests/test_ric01_r2_adversarial.py::test_scenario_n_three_step_sequence_step0_step2_never_rfc11_evidence",
    "O": "tests/test_ric01_r2_adversarial.py::test_scenario_o_synthetic_ev_edge_never_rfc11_vote",
    "P": "tests/test_ric01_r2_adversarial.py::test_scenario_p_concept_generalization_side_effect_edge_never_rfc11_vote",
    "Q": "tests/test_ric01_r2_adversarial.py::test_scenario_q_contradiction_only_transient_endpoint_receipts_tbr_graph_unchanged",
}


# ─────────────────────────────────────────────────────────── Meta-Tests
def test_matrix_invariants_exact_registry_and_resolution():
    """PIR03-G01..G03: Exactly 58 frozen invariants with exact text and semantic test resolution."""
    expected_ids = {f"R2-I{i:02d}" for i in range(1, 59)}
    assert set(FROZEN_R2_INVARIANTS.keys()) == expected_ids
    assert set(FROZEN_R2_INVARIANT_EVIDENCE.keys()) == expected_ids

    # I04 exact digest assertion
    assert compute_r2_observation_semantics_digest() == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"
    assert R2_OBSERVATION_SEMANTICS_DIGEST == "bb1489016229f321ff2381cbdec163a8ac741841ba1dfe89b732ddba67828d9b"

    # Semantic test node resolution
    for inv_id in expected_ids:
        text = FROZEN_R2_INVARIANTS[inv_id]
        assert isinstance(text, str) and text.strip(), f"Invariant {inv_id} text is empty"

        evidence_nodes = FROZEN_R2_INVARIANT_EVIDENCE[inv_id]
        assert isinstance(evidence_nodes, tuple) and len(evidence_nodes) > 0, (
            f"Invariant {inv_id} has empty evidence"
        )
        for ref in evidence_nodes:
            assert "test_ric01_r2_matrix.py" not in ref, (
                f"Invariant {inv_id} evidence ref {ref} must not point to matrix test file itself"
            )
            mod_path, func_name = ref.split("::")
            module_name = mod_path.replace("/", ".").replace("\\", ".").replace(".py", "")
            mod = importlib.import_module(module_name)
            fn = getattr(mod, func_name, None)
            assert fn is not None and callable(fn), f"Invariant {inv_id} evidence {ref} is not callable"


def test_matrix_test_obligations_exact_registry_and_resolution():
    """PIR03-G04..G06: Exactly 89 frozen test obligations with exact text and semantic test resolution."""
    expected_ids = {f"T{i:02d}" for i in range(1, 90)}
    assert set(FROZEN_R2_TEST_OBLIGATIONS.keys()) == expected_ids
    assert set(FROZEN_R2_TEST_EVIDENCE.keys()) == expected_ids

    for t_id in expected_ids:
        text = FROZEN_R2_TEST_OBLIGATIONS[t_id]
        assert isinstance(text, str) and text.strip(), f"Obligation {t_id} text is empty"

        evidence_nodes = FROZEN_R2_TEST_EVIDENCE[t_id]
        assert isinstance(evidence_nodes, tuple) and len(evidence_nodes) > 0, (
            f"Obligation {t_id} has empty evidence"
        )
        for ref in evidence_nodes:
            assert "test_ric01_r2_matrix.py" not in ref, (
                f"Obligation {t_id} evidence ref {ref} must not point to matrix test file itself"
            )
            mod_path, func_name = ref.split("::")
            module_name = mod_path.replace("/", ".").replace("\\", ".").replace(".py", "")
            mod = importlib.import_module(module_name)
            fn = getattr(mod, func_name, None)
            assert fn is not None and callable(fn), f"Obligation {t_id} evidence {ref} is not callable"


def test_matrix_frozen_test_obligations_canonical_hash():
    """PIR04: Exact cryptographic verification of the 89 frozen test obligations ledger."""
    import hashlib
    import json
    raw = json.dumps(FROZEN_R2_TEST_OBLIGATIONS, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert h == "948b24270fd9b1d1d8cac4a0e5850c31508c3f5818ef45046fca2ed257488156", (
        f"FROZEN_R2_TEST_OBLIGATIONS hash mismatch: got {h}"
    )


def test_matrix_frozen_invariants_canonical_hash():
    """PIR04: Exact cryptographic verification of the 58 frozen invariants ledger."""
    import hashlib
    import json
    raw = json.dumps(FROZEN_R2_INVARIANTS, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert h == "8966d536288145c906693f6b61a231f0f5735d43dd0d4267354419555837dd6d", (
        f"FROZEN_R2_INVARIANTS hash mismatch: got {h}"
    )


def test_matrix_adversarial_scenarios_resolution():
    """PIR03-G11: Exactly 17 adversarial scenarios A..Q mapped and resolvable."""
    expected_scenarios = {chr(c) for c in range(ord("A"), ord("Q") + 1)}
    assert set(FROZEN_R2_ADVERSARIAL_SCENARIOS.keys()) == expected_scenarios

    for scenario_letter in sorted(expected_scenarios):
        ref = FROZEN_R2_ADVERSARIAL_SCENARIOS[scenario_letter]
        assert "tests/test_ric01_r2_adversarial.py" in ref
        mod_path, func_name = ref.split("::")
        module_name = mod_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name, None)
        assert fn is not None and callable(fn), f"Adversarial scenario {scenario_letter} ref {ref} is not callable"


@pytest.mark.parametrize(
    "mode,expected_status",
    [
        (ExecutionMode.TRANSIENT_ONLY, "TRANSIENT_OBSERVED"),
        (ExecutionMode.AUTHORIZED_PERSISTENT, "PERSISTENT_EXECUTED"),
    ],
)
def test_matrix_execution_modes(mode, expected_status):
    """Execution mode conformance for transient vs persistent."""
    authorizer = SimpleObservationAuthorizer(allow=True)
    bridge, _, _ = _make_bridge(authorizer=authorizer)
    res = bridge.observe_text(
        boundary_namespace="matrix",
        source_occurrence_key=f"occ_{mode.value}",
        source_event_key=f"evt_{mode.value}",
        ingress_boundary="matrix_b",
        raw_text="Matrix test sentence.",
        mode=mode,
        capability="valid_cap" if mode == ExecutionMode.AUTHORIZED_PERSISTENT else None,
    )
    assert res.status == expected_status
