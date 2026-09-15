"""
DGCA — RIC-01 / R3 Minimal
Canonical User Chat Runtime (R3-MIN-1.0)

Authoritative Specification:
RIC-01-R3-Minimal-Canonical-User-Runtime-Formal-Architecture-Specification-v1.1-FROZEN.md
Status: FROZEN / ADOPTED
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from .causal_identity import derive_internal_work_id
from .config import Law
from .generation import GenerationScope
from .observation import ExecutionMode

if TYPE_CHECKING:
    from .causal_identity import CanonicalR1RuntimeRoot
    from .graph import CognitiveGraph
    from .observation import CanonicalObservationResult

# ─────────────────────────────────────────────────────────── Protocol Constants
R3_MIN_RUNTIME_PROTOCOL_VERSION: str = "R3-MIN-1.0"
R3_MIN_FALLBACK_TEXT: str = "I don't have enough information."
R3_MIN_LANGUAGE_CONTEXT: str = "en"
R3_MIN_GENERATION_BUDGET: float = 1.0

# ─────────────────────────────────────────────────────────── Exact Semantics Registry
R3_MIN_RUNTIME_SEMANTICS_REGISTRY: dict[str, Any] = {
    "activation_scope_lifetime": "RFC13_CALL_ONLY_RESTORE_BEFORE_RFC14",
    "activation_sink_contract": "EXISTING_NODES_ONLY_TRANSIENT_FIELDS_ONLY",
    "anchor_policy": "EXTERNAL_POSITIVE_NODE_RECEIPTS_ONLY",
    "checkpoint_restore": "CANONICAL_R1_SCHEMA_1_2_0",
    "chunk_policy": "JOIN_NONEMPTY_RENDERED_TEXT_WITH_SINGLE_SPACE",
    "completion_activation_mode": "SCOPED_TRANSIENT_UNCOUNTED_RESTORED",
    "completion_budget": "LAW_E_BUDGET_0",
    "completion_canonical_identity": True,
    "completion_owner": "RFC13",
    "external_ingress_count_per_turn": "EXACTLY_ONE",
    "fallback_text": "I don't have enough information.",
    "fresh_bootstrap": "QUANTITY_BACKBONE_BEFORE_R1_PROVENANCE_EPOCH",
    "fresh_prediction_policy": "DISABLED",
    "generation_budget": 1.0,
    "generation_canonical_identity": True,
    "generation_owner": "RFC14",
    "ingress_owner": "R2_CANONICAL_OBSERVATION_BRIDGE",
    "language_context": "en",
    "learning_api": "ABSENT",
    "legacy_compatibility": "EXPLICIT_LEGACY_COGNITIVE_AGENT",
    "legacy_linearizer_policy": "FORBIDDEN_ON_CANONICAL_PATH",
    "loop_policy": "RFC16_NO_EXTERNAL_INGRESS_ON_R3_MIN_PATH",
    "multi_microepisode_policy": "PROCESS_ALL_OBSERVABLE_CHILDREN_IN_CANONICAL_CHILD_ORDER",
    "observation_mode": "TRANSIENT_ONLY",
    "occurrence_policy": "HOST_SESSION_NONCE_PLUS_MONOTONIC_TURN",
    "protocol_version": "R3-MIN-1.0",
    "public_api": ["chat", "__call__", "from_checkpoint"],
    "recurrent_policy": "RFC15_DEFERRED",
    "restore_prediction_policy": "DISABLED",
    "supported_modalities": ["text"],
    "transient_cleanup_policy": "CLOSE_R2_AND_RFC13_DERIVED_SDCRS",
    "turn_concurrency": "SINGLE_ACTIVE_TURN_FAIL_CLOSED",
}


def compute_r3_min_runtime_semantics_digest() -> str:
    """Computes the direct SHA-256 digest of the canonical JSON representation of R3 semantics registry."""
    payload = json.dumps(
        R3_MIN_RUNTIME_SEMANTICS_REGISTRY,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


R3_MIN_RUNTIME_SEMANTICS_DIGEST: str = compute_r3_min_runtime_semantics_digest()


# ─────────────────────────────────────────────────────────── Transient Activation Scope
class TransientActivationScope:
    """Scoped transient activation writer isolated from persistent accounting (R3 §17).

    Guarantees:
    - Only writes Node.A, Node.t_spawn, Node.episode on existing nodes.
    - Captures (A, t_spawn, episode) on first touch.
    - Never mutates Node.N_total, Node.U, Node.V, or any durable field.
    - Unknown node ID fails closed (KeyError).
    - Writes after scope close fail closed (RuntimeError).
    - Restoration occurs in finally, restoring all touched nodes exactly.
    """

    def __init__(self, graph: CognitiveGraph) -> None:
        self._graph = graph
        self._snapshot: dict[str, tuple[float, int, str | None]] = {}
        self._closed: bool = False

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def touched_node_ids(self) -> frozenset[str]:
        return frozenset(self._snapshot.keys())

    def excite_existing_node(
        self,
        node_id: str,
        *,
        t: int,
        value: float,
        episode: str | None = None,
    ) -> None:
        if self._closed:
            raise RuntimeError("TransientActivationScope is closed")
        if node_id not in self._graph.nodes:
            raise KeyError(f"Unknown node ID: {node_id}")

        node = self._graph.nodes[node_id]
        if node_id not in self._snapshot:
            self._snapshot[node_id] = (node.A, node.t_spawn, node.episode)

        node.A = min(Law.C_MAX, value)
        node.t_spawn = t
        node.episode = episode

    def restore(self) -> None:
        if self._closed:
            return
        try:
            for node_id, (orig_A, orig_t, orig_ep) in self._snapshot.items():
                if node_id in self._graph.nodes:
                    node = self._graph.nodes[node_id]
                    node.A = orig_A
                    node.t_spawn = orig_t
                    node.episode = orig_ep
        finally:
            self._closed = True

    def __enter__(self) -> Self:
        if self._closed:
            raise RuntimeError("TransientActivationScope cannot be reused once closed")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.restore()


# ─────────────────────────────────────────────────────────── R3 Turn Result Diagnostics
@dataclass(frozen=True)
class R3TurnResult:
    """Transient diagnostic summary for one completed or failed chat turn (R3 §31)."""

    protocol_version: str
    session_turn_index: int
    root_external_episode_id: str
    ingress_event_id: str
    observation_transaction_id: str
    micro_episode_ids: tuple[str, ...]
    input_representation_ids: tuple[str, ...]
    settled_representation_ids: tuple[str, ...]
    surface_chunk_ids: tuple[str, ...]
    completion_closure_reasons: tuple[str, ...]
    generation_closure_reasons: tuple[str, ...]
    text: str
    used_fallback: bool


# ─────────────────────────────────────────────────────────── Canonical Chat Runtime
class CanonicalChatRuntime:
    """Canonical minimal user-facing chat runtime for DGCA (R3 §8-§23)."""

    def __init__(
        self,
        runtime_root: CanonicalR1RuntimeRoot,
        graph: CognitiveGraph,
        session_nonce: str | None = None,
    ) -> None:
        self._runtime_root = runtime_root
        self._graph = graph
        self._bridge = runtime_root.create_observation_bridge()

        if session_nonce is not None:
            if not isinstance(session_nonce, str) or not re.fullmatch(r"^[0-9a-f]{32}$", session_nonce):
                raise ValueError(
                    f"Injected session_nonce must be exactly 32 lowercase hex characters, got {session_nonce!r}"
                )
            self._session_nonce = session_nonce
        else:
            self._session_nonce = secrets.token_hex(16)

        self._turn_index: int = 0
        self._state: str = "IDLE"  # IDLE | RUNNING
        self._last_turn: R3TurnResult | None = None

    @property
    def session_nonce(self) -> str:
        return self._session_nonce

    @property
    def turn_index(self) -> int:
        return self._turn_index

    @property
    def state(self) -> str:
        return self._state

    @property
    def last_turn(self) -> R3TurnResult | None:
        return self._last_turn

    def chat(self, text: str) -> str:
        """Processes one user text turn through canonical R2 ingress, RFC13 settling, and RFC14 generation."""
        if self._state != "IDLE":
            raise RuntimeError(
                f"Single active turn violation: chat() invoked while in state '{self._state}'"
            )

        current_turn = self._turn_index
        self._turn_index += 1

        if not isinstance(text, str):
            raise TypeError(f"chat() expects str, got {type(text).__name__}")
        if not text.strip():
            raise ValueError("chat() text cannot be empty or whitespace-only")

        self._state = "RUNNING"

        obs_result: CanonicalObservationResult | None = None
        try:
            # 1. R2 Ingress
            source_occurrence_key = f"{self._session_nonce}:{current_turn}"
            obs_result = self._bridge.observe_text(
                boundary_namespace="DGCA:R3:CHAT:v1",
                source_occurrence_key=source_occurrence_key,
                source_event_key="user_message",
                ingress_boundary="R3_CHAT_TEXT",
                raw_text=text,
                context=None,
                mode=ExecutionMode.TRANSIENT_ONLY,
            )

            if obs_result.persistent_phase != "NOT_REQUESTED":
                raise RuntimeError(
                    f"R3 chat requires persistent_phase 'NOT_REQUESTED', got '{obs_result.persistent_phase}'"
                )
            if obs_result.persistent_transaction_id is not None:
                raise RuntimeError(
                    f"R3 chat requires persistent_transaction_id None, got '{obs_result.persistent_transaction_id}'"
                )
            if obs_result.persistent_executed is not False:
                raise RuntimeError(
                    f"R3 chat requires persistent_executed False, got {obs_result.persistent_executed}"
                )

            # Zero-content fallback check
            if obs_result.status == "NO_OBSERVABLE_CONTENT" or not obs_result.representations:
                turn_res = R3TurnResult(
                    protocol_version=R3_MIN_RUNTIME_PROTOCOL_VERSION,
                    session_turn_index=current_turn,
                    root_external_episode_id=obs_result.root_external_episode_id,
                    ingress_event_id=obs_result.ingress_event_id,
                    observation_transaction_id=obs_result.observation_transaction_id,
                    micro_episode_ids=tuple(m.micro_episode_id for m in obs_result.micro_episodes),
                    input_representation_ids=tuple(r.representation_id for r in obs_result.representations),
                    settled_representation_ids=(),
                    surface_chunk_ids=(),
                    completion_closure_reasons=(),
                    generation_closure_reasons=(),
                    text=R3_MIN_FALLBACK_TEXT,
                    used_fallback=True,
                )
                self._last_turn = turn_res
                return R3_MIN_FALLBACK_TEXT

            # 2. Multi-MicroEpisode processing in canonical child_index order
            rep_by_id = {r.representation_id: r for r in obs_result.representations}
            sorted_micro_records = sorted(obs_result.micro_episodes, key=lambda m: m.child_index)

            collected_chunks: list[str] = []
            settled_rep_ids: list[str] = []
            chunk_ids: list[str] = []
            comp_reasons: list[str] = []
            gen_reasons: list[str] = []

            for micro_rec in sorted_micro_records:
                if micro_rec.representation_id is None:
                    continue
                child_rep = rep_by_id.get(micro_rec.representation_id)
                if child_rep is None:
                    continue

                # Anchors derived exclusively from positive external node receipts
                anchor_refs = frozenset(
                    r.element_ref
                    for r in child_rep.participation_receipts
                    if r.participation_kind == "node"
                    and r.origin_lineage == "external"
                    and r.activation_magnitude > 0
                    and isinstance(r.element_ref, str)
                    and r.element_ref in child_rep.participating_node_refs
                )

                if not anchor_refs:
                    continue

                # Derive canonical InternalWorkID for RFC13
                internal_work_id = derive_internal_work_id(
                    root_authority_ref=obs_result.root_external_episode_id,
                    subsystem_kind="RFC13_COMPLETION",
                    scope_refs=sorted(anchor_refs),
                    prerequisite_work_ids=[],
                    work_index_or_role={
                        "observation_transaction_id": obs_result.observation_transaction_id,
                        "micro_episode_id": micro_rec.micro_episode_id,
                        "child_index": micro_rec.child_index,
                    },
                )

                # RFC13 Settling with TransientActivationScope
                active_before = set(self._graph.representation_engine.active_representations.keys())
                scope = TransientActivationScope(self._graph)
                rfc13_created_ids: set[str] = set()

                try:
                    try:
                        settled_rep, outcome = self._graph.completion_engine.run_settling_epoch(
                            initial_representation=child_rep,
                            budget=Law.E_BUDGET_0,
                            root_authority_ref=obs_result.root_external_episode_id,
                            work_ref=internal_work_id,
                            canonical_identity=True,
                            activation_sink=scope,
                        )
                    finally:
                        scope.restore()
                        active_now = set(self._graph.representation_engine.active_representations.keys())
                        rfc13_created_ids = active_now - active_before

                    settled_rep_ids.append(settled_rep.representation_id)
                    comp_reasons.append(outcome.closure_reason)

                    # RFC14 Generation executed after activation scope is restored
                    generation_scope = GenerationScope(
                        task_ref=obs_result.root_external_episode_id,
                        query_ref=obs_result.observation_transaction_id,
                        event_ref=micro_rec.micro_episode_id,
                    )
                    handoff = self._graph.generation_engine.execute_generative_pass(
                        representation=settled_rep,
                        anchor_refs=anchor_refs,
                        generation_scope=generation_scope,
                        language_context=R3_MIN_LANGUAGE_CONTEXT,
                        budget=R3_MIN_GENERATION_BUDGET,
                        canonical_identity=True,
                    )

                    rendered_text = handoff.surface_chunk_view.rendered_text
                    chunk_ids.append(handoff.surface_chunk_view.chunk_id)
                    gen_reasons.append(handoff.closure_reason)

                    if rendered_text.strip() != "":
                        collected_chunks.append(rendered_text)

                finally:
                    # Deterministic cleanup of all RFC13-created SDCRs
                    for rid in list(rfc13_created_ids):
                        rep_to_close = self._graph.representation_engine.active_representations.get(rid)
                        if rep_to_close is not None:
                            self._graph.representation_engine.close_representation(rep_to_close)

            if collected_chunks:
                reply_text = " ".join(collected_chunks)
                used_fallback = False
            else:
                reply_text = R3_MIN_FALLBACK_TEXT
                used_fallback = True

            turn_res = R3TurnResult(
                protocol_version=R3_MIN_RUNTIME_PROTOCOL_VERSION,
                session_turn_index=current_turn,
                root_external_episode_id=obs_result.root_external_episode_id,
                ingress_event_id=obs_result.ingress_event_id,
                observation_transaction_id=obs_result.observation_transaction_id,
                micro_episode_ids=tuple(m.micro_episode_id for m in obs_result.micro_episodes),
                input_representation_ids=tuple(r.representation_id for r in obs_result.representations),
                settled_representation_ids=tuple(settled_rep_ids),
                surface_chunk_ids=tuple(chunk_ids),
                completion_closure_reasons=tuple(comp_reasons),
                generation_closure_reasons=tuple(gen_reasons),
                text=reply_text,
                used_fallback=used_fallback,
            )
            self._last_turn = turn_res
            return reply_text

        finally:
            if obs_result is not None and not obs_result.is_closed:
                obs_result.close()
            self._state = "IDLE"
