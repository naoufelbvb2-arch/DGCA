"""
DGCA — RFC-16 v1.0
Unified Generative Cognitive Loop Engine & Protocol Orchestration.

Authoritative Specification: RFC-16-DGCA-Unified-Generative-Cognitive-Loop-v1.0.md
Status: ARCHITECTURE v1.0 FROZEN | IMPLEMENTATION VERIFIED
Constitutional Motto: RFC16 = Protocol, not Brain
Law 18 Status: NOT JUSTIFIED / NOT ADOPTED
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dgca.config import Law
from dgca.generation import SurfaceChunk
from dgca.representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
)

if TYPE_CHECKING:
    from dgca.graph import CognitiveGraph
    from dgca.recurrent import GenerativeContinuationEpoch


# ─────────────────────────────────────────────────────────── 1. Observability (Non-Cognitive)
@dataclass
class UnifiedLoopObservability:
    """عدادات مراقبة غير معرفية وتشخيصية محضة لحلقة التنسيق الموحدة (RFC-16)."""

    ingress_events: int = 0
    dedup_rejections: int = 0
    authority_views_derived: int = 0
    evidence_eligibility_checks: int = 0
    learning_mutations_attributed: int = 0
    unauthorized_feedback_blocks: int = 0
    internal_work_frontiers_derived: int = 0
    internal_dispatches: int = 0
    stale_revalidations: int = 0
    delivery_attempts: int = 0
    delivery_retries: int = 0
    delivery_acks: int = 0
    cancellations_processed: int = 0
    new_gce_continuations: int = 0
    quiescence_events: int = 0
    fixed_point_stops: int = 0

    def reset(self) -> None:
        for fld in self.__dataclass_fields__:
            setattr(self, fld, 0)


# ─────────────────────────────────────────────────────────── 2. Derived Operational Views & Transient Records
@dataclass(frozen=True)
class ExternalEventRecord:
    """
    سجل تشغيلي مؤقت لحدث وارد من الحدود الخارجية المصرح بها (Authorized External Ingress).
    """
    event_id: str
    root_external_episode_id: str
    ingress_boundary: str
    source_origin: str  # "EXTERNAL"
    raw_content: str
    modality: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source_origin != "EXTERNAL":
            raise ValueError("ExternalEventRecord must have source_origin == 'EXTERNAL'")
        if not self.root_external_episode_id:
            raise ValueError("root_external_episode_id is mandatory for causal identity")


@dataclass(frozen=True)
class FeedbackAuthorityView:
    """
    واجهة مشتقة لتصنيف السلطات الممنوحة للمدخلات الخارجية دون ادعاء الحقيقة الدلالية أو التعلم المباشر.
    """
    event_id: str
    root_external_episode_id: str
    is_task_control: bool = False
    task_control_kind: str | None = None  # "CONTINUE", "STOP", "CHANGE_LANGUAGE", "CANCEL", "REPEAT"
    is_evaluation: bool = False
    evaluation_kind: str | None = None  # "CORRECT", "WRONG", "POSITIVE", "NEGATIVE"
    is_corrective_claim: bool = False
    claimed_elements: tuple[str, ...] = ()
    is_environmental_observation: bool = False
    is_delivery_ack: bool = False


@dataclass(frozen=True)
class EvidenceEligibilityView:
    """
    واجهة مشتقة لحراسة الأهلية الدليلية قبل أي وصول لقنوات التعلم التكراري أو تعديل الأوزان.
    """
    event_id: str
    root_external_episode_id: str
    is_eligible: bool
    source_contract: str
    rejection_reason: str | None = None


@dataclass(frozen=True)
class LearningAttributionRecord:
    """
    سجل تتبع سببي كامل يثبت إسناد أي تعديل معرفي دائم إلى مالك تعلم سابق مجمد (Laws 1-15).
    """
    attribution_id: str
    root_external_episode_id: str
    eligibility_ref: str
    validation_owner: str  # e.g., "Law1_HebbianCreation", "Law2_HebbianReinforcement", "Law14_AssemblyParticipation"
    local_transaction_id: str
    mutated_elements: tuple[str, ...]
    mutation_kind: str


@dataclass(frozen=True)
class InternalWorkAuthorityView:
    """
    واجهة مشتقة لسلطة عمل معرفي داخلي محدد النطاق (Scope-local internal work).
    """
    work_id: str
    root_authority_ref: str
    subsystem_kind: str  # "RFC13_COMPLETION", "REASONING", "RFC14_GENERATION", "RFC15_RECURRENT"
    scope_nodes: tuple[str, ...]
    is_authorized: bool
    prerequisite_work_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkDependencyView:
    """
    واجهة مشتقة لتبعيات العمل المعرفي الداخلي المشتقة من السلطة المحلية للعمل.
    """
    work_id: str
    unmet_dependencies: tuple[str, ...]
    is_satisfied: bool


@dataclass(frozen=True)
class InternalWorkFrontier:
    """
    جبهة العمل الداخلي الجاهز للتنفيذ دون أي ترتيب أو تفضيل مركزي من متحكم عالمي.
    """
    ready_work: tuple[InternalWorkAuthorityView, ...]
    blocked_work: tuple[InternalWorkAuthorityView, ...]
    status: str  # "READY", "BLOCKED", "EMPTY", "AMBIGUOUS"


@dataclass(frozen=True)
class DeliveryStatusView:
    """
    سجل تشغيلي مؤقت لحالة نقل وتوصيل المخرج السطحي الملتزم إلى البيئة الخارجية.
    """
    delivery_id: str
    surface_chunk_id: str
    parent_rid: str
    status: str  # "DELIVERED", "FAILED", "RETRYING", "ACKNOWLEDGED", "CANCELLED"
    retry_count: int = 0


@dataclass(frozen=True)
class TaskRelationView:
    """
    واجهة مشتقة للعلاقة بين الحدث الخارجي والمهمة الحالية (استمرار، تعديل، إلغاء، جذر جديد).
    """
    relation_kind: str  # "CONTINUES", "MODIFIES", "CORRECTS", "CANCELS", "NEW_ROOT"
    target_root_ref: str
    is_authorized: bool
    revalidation_required: bool = False


@dataclass(frozen=True)
class OrchestrationSnapshotView:
    """
    لقطة تشغيلية مؤقتة غير مستدامة لحالة التنسيق الحالية للجذر المعرفي.
    """
    snapshot_id: str
    root_authority_ref: str
    current_graph_version: int
    active_work_ids: tuple[str, ...]
    open_gce_ids: tuple[str, ...]
    quiescence_status: str


@dataclass(frozen=True)
class InterruptionAuthorityView:
    """
    واجهة مشتقة لسلطة المقاطعة أو الإلغاء المشتقة من الأحداث الخارجية الصريحة.
    """
    action: str  # "CANCEL", "CORRECT", "IGNORE"
    affected_root_refs: tuple[str, ...]
    invalidated_work_ids: tuple[str, ...]


@dataclass(frozen=True)
class RootQuiescenceView:
    """
    واجهة مشتقة لسكون الحلقة عند استقرار الحالة أو انتظار مدخلات خارجية مستقلة.
    """
    root_authority_ref: str
    is_quiescent: bool
    quiescence_reason: str  # "ALL_WORK_COMPLETE", "NO_READY_WORK", "WAITING_EXTERNAL_INPUT", "BUDGET_EXHAUSTED", "MUTUAL_AMBIGUITY", "BLOCKED"


@dataclass(frozen=True)
class UnifiedNoProgressSignature:
    """
    بصمة تشغيلية مشتقة لاكتشاف النقطة الثابتة دون تقدم وتجنب الدوران العقيم.
    """
    root_ref: str
    state_version_digest: str
    work_frontier_digest: str
    gce_progress_digest: str
    blocker_digest: str


# ─────────────────────────────────────────────────────────── 3. Unified Orchestration Engine
class UnifiedGenerativeCognitiveLoopEngine:
    """
    محرك بروتوكول التنسيق المعرفي التوليدي الموحد (RFC-16 v1.0).
    لا يمتلك معرفة دلالية ولا يمثل متحكماً عالمياً ولا يضيف قوانين جديدة (Law 18 = NOT ADOPTED).
    """

    def __init__(self, graph: CognitiveGraph) -> None:
        self._graph = graph
        self.observability = UnifiedLoopObservability()

        # سجلات تشغيلية مؤقتة (Ephemeral operational tables)
        self._processed_episodes: set[str] = set()
        self._ingress_events: dict[str, ExternalEventRecord] = {}
        self._delivery_records: dict[str, DeliveryStatusView] = {}
        self._learning_attributions: list[LearningAttributionRecord] = []
        self._active_roots: set[str] = set()
        self._cancelled_roots: set[str] = set()

    # ── Phase 2: External Ingress & Episode Deduplication ──

    def ingress_external_event(
        self,
        event_id: str,
        root_external_episode_id: str,
        raw_content: str,
        ingress_boundary: str = "api_gateway",
        source_origin: str = "EXTERNAL",
        modality: str = "text",
        is_internal_call: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[ExternalEventRecord | None, bool]:
        """
        استقبال حدث خارجي عبر منفذ دخول مصرح به مع حراسة المصدر وحظر توليد الدليل الداخلي ذاتياً.
        """
        self.observability.ingress_events += 1

        # حظر توليد صفة الخارجي ذاتياً من داخل الكود المعرفي
        if is_internal_call or source_origin != "EXTERNAL":
            self.observability.unauthorized_feedback_blocks += 1
            return None, False

        # فحص تكرار الحلقة السببية الخارجية ذاتها (Root Episode Deduplication)
        # النقل المكرر أو التعدد الحسي لنفس الحلقة لا يضاعف فرص التعلم
        is_novel_episode = root_external_episode_id not in self._processed_episodes
        self._processed_episodes.add(root_external_episode_id)

        rec = ExternalEventRecord(
            event_id=event_id,
            root_external_episode_id=root_external_episode_id,
            ingress_boundary=ingress_boundary,
            source_origin="EXTERNAL",
            raw_content=raw_content,
            modality=modality,
            metadata=metadata or {},
        )
        self._ingress_events[event_id] = rec
        return rec, is_novel_episode

    # ── Phase 3: Feedback Authority Classification & Evidence Firewall ──

    def derive_feedback_authority(self, event: ExternalEventRecord) -> FeedbackAuthorityView:
        """
        اشتقاق تصنيف سلطة الملاحظات الخارجية دون تعديل الذاكرة المعرفية مباشرة.
        """
        self.observability.authority_views_derived += 1
        content_lower = event.raw_content.strip().lower()

        # 1. سلطة التحكم بالمهمة
        is_task_control = False
        control_kind = None
        if content_lower in ("continue", "next", "more"):
            is_task_control = True
            control_kind = "CONTINUE"
        elif content_lower in ("stop", "halt", "quit"):
            is_task_control = True
            control_kind = "STOP"
        elif content_lower in ("cancel", "abort"):
            is_task_control = True
            control_kind = "CANCEL"
        elif content_lower.startswith("repeat") or content_lower == "again":
            is_task_control = True
            control_kind = "REPEAT"
        elif content_lower.startswith("lang:") or content_lower in ("arabic", "english", "french"):
            is_task_control = True
            control_kind = "CHANGE_LANGUAGE"

        # 2. سلطة التقييم
        is_eval = False
        eval_kind = None
        eval_pos = ("correct", "good", "great", "right", "pass", "praise")
        eval_neg = ("wrong", "bad", "incorrect", "fail", "criticism")
        words = set(content_lower.replace(":", " ").replace(",", " ").split())
        if not content_lower.startswith(("correction:", "fact:")):
            if any(k in words or content_lower == k for k in eval_pos):
                is_eval = True
                eval_kind = "POSITIVE"
            elif any(k in words or content_lower == k for k in eval_neg):
                is_eval = True
                eval_kind = "NEGATIVE"

        # 3. إشعار الاستلام
        is_ack = content_lower in ("ack", "delivered", "read_receipt", "seen")

        # 4. الادعاء التصحيحي الدلالي
        is_corrective = False
        claimed_elems: tuple[str, ...] = ()
        if content_lower.startswith(("correction:", "fact:")):
            is_corrective = True
            claimed_part = event.raw_content.split(":", 1)[1].strip()
            claimed_elems = tuple(part.strip() for part in claimed_part.split(",") if part.strip())

        # 5. الملاحظة البيئية المستقلة
        is_env = event.metadata.get("is_sensor_observation", False)

        return FeedbackAuthorityView(
            event_id=event.event_id,
            root_external_episode_id=event.root_external_episode_id,
            is_task_control=is_task_control,
            task_control_kind=control_kind,
            is_evaluation=is_eval,
            evaluation_kind=eval_kind,
            is_corrective_claim=is_corrective,
            claimed_elements=claimed_elems,
            is_environmental_observation=is_env,
            is_delivery_ack=is_ack,
        )

    def evaluate_evidence_eligibility(
        self,
        event: ExternalEventRecord,
        auth_view: FeedbackAuthorityView,
        is_novel_episode: bool,
    ) -> EvidenceEligibilityView:
        """
        حراسة أهلية الدليل: التأكد من أن الحدث الخارجي مؤهل لدخول قنوات التعلم الشرعية.
        الملاحظات العشوائية أو التكرار غير المصرح به أو تقارير الاستلام تُرفض كدليل للتعلم الدائم.
        """
        self.observability.evidence_eligibility_checks += 1

        # رفض إعادة النقل كدليل مستقل
        if not is_novel_episode:
            return EvidenceEligibilityView(
                event_id=event.event_id,
                root_external_episode_id=event.root_external_episode_id,
                is_eligible=False,
                source_contract="UNAUTHORIZED_RETRY",
                rejection_reason="TRANSPORT_RETRY_DUPLICATE",
            )

        # إشعار الاستلام لا يمثل دليلاً دلالياً
        if auth_view.is_delivery_ack:
            return EvidenceEligibilityView(
                event_id=event.event_id,
                root_external_episode_id=event.root_external_episode_id,
                is_eligible=False,
                source_contract="TRANSPORT_ONLY",
                rejection_reason="DELIVERY_ACK_NOT_EVIDENCE",
            )

        # التحكم بالمهمة لا يمثل دليلاً معرفياً للتعلم
        if auth_view.is_task_control and not auth_view.is_corrective_claim:
            return EvidenceEligibilityView(
                event_id=event.event_id,
                root_external_episode_id=event.root_external_episode_id,
                is_eligible=False,
                source_contract="TASK_CONTROL_ONLY",
                rejection_reason="TASK_CONTROL_CANNOT_LEARN",
            )

        # التقييم المحض (إيجابي/سلبي) لا يخلق دليلاً دلالياً بديلاً إلا بعقد نتيجة صريح
        if auth_view.is_evaluation and not auth_view.is_corrective_claim and not auth_view.is_environmental_observation:
            has_outcome_contract = event.metadata.get("has_outcome_contract", False)
            if not has_outcome_contract:
                return EvidenceEligibilityView(
                    event_id=event.event_id,
                    root_external_episode_id=event.root_external_episode_id,
                    is_eligible=False,
                    source_contract="RAW_EVALUATION",
                    rejection_reason="EVALUATION_WITHOUT_OUTCOME_CONTRACT",
                )

        # التحقق من وجود سلطة مصدر مصرح بها (Authorized Source Contract)
        has_authorized_source = event.metadata.get("authorized_source", False)
        if not has_authorized_source and not auth_view.is_environmental_observation:
            return EvidenceEligibilityView(
                event_id=event.event_id,
                root_external_episode_id=event.root_external_episode_id,
                is_eligible=False,
                source_contract="UNTRUSTED_EXTERNAL_CLAIM",
                rejection_reason="UNAUTHORIZED_SOURCE_CONTRACT",
            )

        # الملاحظات البيئية أو الادعاءات المعتمدة قانونياً
        contract = event.metadata.get("source_contract", "AUTHORIZED_EXTERNAL_EVIDENCE")
        return EvidenceEligibilityView(
            event_id=event.event_id,
            root_external_episode_id=event.root_external_episode_id,
            is_eligible=True,
            source_contract=contract,
            rejection_reason=None,
        )


    # ── Phase 4: Learning Attribution & Positive Learning Control ──

    def process_validated_learning(
        self,
        event: ExternalEventRecord,
        eligibility: EvidenceEligibilityView,
        learning_owner: str,
        elements: tuple[str, ...],
        target_dst: str | None = None,
        weight_delta: float = 0.1,
    ) -> tuple[bool, LearningAttributionRecord | None]:
        """
        تنفيذ معاملة التعلم المحلي تحت سلطة المالك المجمد الموجود أصلاً (وليس RFC-16).
        """
        if not eligibility.is_eligible:
            self.observability.unauthorized_feedback_blocks += 1
            return False, None

        tx_id = f"tx_{hashlib.sha256(f'{event.root_external_episode_id}_{learning_owner}_{elements}'.encode()).hexdigest()[:12]}"

        # تفويض التعديل لمالك التعلم الأصلي
        if learning_owner == "Law1_HebbianCreation" and len(elements) >= 2:
            src, dst = elements[0], elements[1]
            self._graph.link(src, dst, W=Law.W_BASE, contexts=("en",))
        elif learning_owner == "Law2_HebbianReinforcement" and len(elements) >= 2:
            src, dst = elements[0], elements[1]
            existing = self._graph.edge(src, dst)
            if existing is not None:
                new_w = min(Law.W_MAX, existing.W + weight_delta)
                self._graph.link(src, dst, W=new_w, contexts=existing.contexts)
            else:
                self._graph.link(src, dst, W=Law.W_BASE, contexts=("en",))
        elif learning_owner == "Law14_AssemblyParticipation" and len(elements) >= 2:
            edges = [(elements[i], elements[i + 1]) for i in range(len(elements) - 1)]
            self._graph.assembly_manager.record_participation(
                edges,
                root_episode_id=event.root_external_episode_id,
                valid_origin=True,
            )

        attr_rec = LearningAttributionRecord(
            attribution_id=f"attr_{tx_id}",
            root_external_episode_id=event.root_external_episode_id,
            eligibility_ref=event.event_id,
            validation_owner=learning_owner,
            local_transaction_id=tx_id,
            mutated_elements=elements,
            mutation_kind="PERSISTENT_COGNITIVE_UPDATE",
        )
        self._learning_attributions.append(attr_rec)
        self.observability.learning_mutations_attributed += 1
        return True, attr_rec

    # ── Phase 5: Internal Work Orchestration & Dependency Frontier ──

    def derive_internal_work_frontier(
        self,
        root_authority_ref: str,
        work_items: tuple[InternalWorkAuthorityView, ...],
        completed_work_ids: set[str],
    ) -> InternalWorkFrontier:
        """
        اشتقاق جبهة العمل الداخلي المؤهل بناءً على توفر السلطة واستيفاء التبعيات فقط دون ترتيب تفضيلي.
        """
        self.observability.internal_work_frontiers_derived += 1

        if root_authority_ref in self._cancelled_roots:
            return InternalWorkFrontier(ready_work=(), blocked_work=(), status="CANCELLED")

        ready: list[InternalWorkAuthorityView] = []
        blocked: list[InternalWorkAuthorityView] = []

        for w in work_items:
            if not w.is_authorized or w.root_authority_ref != root_authority_ref:
                continue
            if w.work_id in completed_work_ids:
                continue
            unmet = [dep for dep in w.prerequisite_work_ids if dep not in completed_work_ids]
            if not unmet:
                ready.append(w)
            else:
                blocked.append(w)

        status = "READY" if ready else ("BLOCKED" if blocked else "EMPTY")
        return InternalWorkFrontier(
            ready_work=tuple(ready),
            blocked_work=tuple(blocked),
            status=status,
        )

    # ── Phase 6: Subsystem Integration & Fresh Execution ──

    def dispatch_internal_work(
        self,
        work: InternalWorkAuthorityView,
        representation: SparseDistributedCognitiveRepresentation,
        observed_version: int,
        budget: float = 10.0,
    ) -> tuple[str, Any]:
        """
        تنفيذ العمل المعرفي الداخلي عبر المالك المجمد الأصلي مع التحقق من عدم تقادم الحالة (Staleness).
        """
        self.observability.internal_dispatches += 1

        if work.root_authority_ref in self._cancelled_roots:
            return "CANCELLED", None

        # التحقق من صلاحية الحالة المشاهدة (Staleness check)
        current_version = self._graph.t
        if current_version != observed_version:
            self.observability.stale_revalidations += 1
            # إذا تغيرت الحالة المعرفية، يجب رفض العمل المتقادم أو إعادة اشتقاقه
            return "STALE_REJECTED", None

        if work.subsystem_kind == "RFC13_COMPLETION":
            comp_res = self._graph.completion_engine.run_settling_epoch(
                initial_representation=representation,
                budget=budget,
            )
            return "SUCCESS", comp_res

        elif work.subsystem_kind == "RFC14_GENERATION":
            gen_eng = self._graph.generation_engine
            frame = gen_eng.build_generative_frame(representation, frozenset(work.scope_nodes))
            hierarchy = gen_eng.build_hierarchy([frame])
            expanded_h, _ = gen_eng.expand_hierarchy(hierarchy, representation, budget=budget)
            prefix, _ = gen_eng.linearize_hierarchy(expanded_h, budget=budget)
            chunk = gen_eng.realize_surface_chunk(prefix, str(representation.representation_id), budget=budget)
            return "SUCCESS", chunk

        elif work.subsystem_kind == "RFC15_RECURRENT":
            rec_eng = self._graph.recurrent_engine
            epoch = rec_eng.create_epoch(work.root_authority_ref)
            closure, handoff = rec_eng.execute_recurrent_epoch(epoch.epoch_id, representation, budget=budget)
            return "SUCCESS", (closure, handoff)

        elif work.subsystem_kind == "REASONING":
            from dgca.reasoning import deep_infer
            res = deep_infer(self._graph, list(work.scope_nodes), mode="simulation")
            return "SUCCESS", res

        return "UNAUTHORIZED_SUBSYSTEM", None

    # ── Phase 7: Generation / Delivery Separation & Delivery Retry ──

    def deliver_surface_output(
        self,
        surface_chunk: SurfaceChunk,
        parent_rid: str,
        simulate_transport_failure: bool = False,
    ) -> DeliveryStatusView:
        """
        توصيل المخرج السطحي الملتزم إلى البيئة الخارجية.
        فشل التوصيل أو إعادة النقل لا يلغي إيصال التعبير التوليدي ولا يضاعف التقدم.
        """
        self.observability.delivery_attempts += 1
        did = f"del_{hashlib.sha256(f'{surface_chunk.chunk_id}_{parent_rid}'.encode()).hexdigest()[:12]}"

        if simulate_transport_failure:
            status_view = DeliveryStatusView(
                delivery_id=did,
                surface_chunk_id=surface_chunk.chunk_id,
                parent_rid=parent_rid,
                status="FAILED",
                retry_count=0,
            )
        else:
            status_view = DeliveryStatusView(
                delivery_id=did,
                surface_chunk_id=surface_chunk.chunk_id,
                parent_rid=parent_rid,
                status="DELIVERED",
                retry_count=0,
            )
        self._delivery_records[did] = status_view
        return status_view

    def retry_delivery(self, delivery_id: str, success: bool = True) -> DeliveryStatusView:
        """
        إعادة محاولة نقل نفس المخرج الملتزم سابقاً دون استدعاء التوليد أو إنشاء إيصال تعبيري جديد.
        """
        self.observability.delivery_retries += 1
        old_view = self._delivery_records.get(delivery_id)
        if old_view is None:
            raise KeyError(f"Delivery record {delivery_id} not found")

        new_status = "DELIVERED" if success else "FAILED"
        new_view = DeliveryStatusView(
            delivery_id=old_view.delivery_id,
            surface_chunk_id=old_view.surface_chunk_id,
            parent_rid=old_view.parent_rid,
            status=new_status,
            retry_count=old_view.retry_count + 1,
        )
        self._delivery_records[delivery_id] = new_view
        return new_view

    def acknowledge_delivery(self, delivery_id: str) -> DeliveryStatusView:
        """
        تسجيل إشعار استلام النقل. إشعار النقل لا يمثل اتفاقاً دلالياً ولا حقيقة دائمية.
        """
        self.observability.delivery_acks += 1
        old_view = self._delivery_records.get(delivery_id)
        if old_view is None:
            raise KeyError(f"Delivery record {delivery_id} not found")

        ack_view = DeliveryStatusView(
            delivery_id=old_view.delivery_id,
            surface_chunk_id=old_view.surface_chunk_id,
            parent_rid=old_view.parent_rid,
            status="ACKNOWLEDGED",
            retry_count=old_view.retry_count,
        )
        self._delivery_records[delivery_id] = ack_view
        return ack_view

    # ── Phase 8: Task Continuation, Cancellation & Multi-Root Isolation ──

    def process_task_relation(
        self,
        event: ExternalEventRecord,
        current_root_ref: str,
        closed_gce: GenerativeContinuationEpoch | None = None,
    ) -> tuple[TaskRelationView, str | None]:
        """
        معالجة علاقة المهمة (استمرار، إلغاء، جذر جديد) بناءً على سلطة المهمة الصريحة.
        الحقبة المغلقة CLOSED GCE لا يُعاد فتحها أبداً؛ الاستمرار ينشئ حقبة جديدة GCE_2.
        """
        auth_view = self.derive_feedback_authority(event)

        if auth_view.is_task_control and auth_view.task_control_kind == "CANCEL":
            self._cancelled_roots.add(current_root_ref)
            self.observability.cancellations_processed += 1
            return (
                TaskRelationView(
                    relation_kind="CANCELS",
                    target_root_ref=current_root_ref,
                    is_authorized=True,
                    revalidation_required=False,
                ),
                None,
            )

        if auth_view.is_task_control and auth_view.task_control_kind == "CONTINUE":
            self.observability.new_gce_continuations += 1
            new_gce_id = None
            if closed_gce is not None and closed_gce.lifecycle == "CLOSED":
                # إنشاء حقبة جديدة تماماً بسلطة ميزانية جديدة
                new_gce_id = f"gce_{hashlib.sha256(f'{current_root_ref}_{event.event_id}'.encode()).hexdigest()[:12]}"
                self._graph.recurrent_engine.create_epoch(
                    root_authority_ref=current_root_ref,
                    epoch_id=new_gce_id,
                )
            return (
                TaskRelationView(
                    relation_kind="CONTINUES",
                    target_root_ref=current_root_ref,
                    is_authorized=True,
                    revalidation_required=True,
                ),
                new_gce_id,
            )

        if auth_view.is_corrective_claim:
            return (
                TaskRelationView(
                    relation_kind="CORRECTS",
                    target_root_ref=current_root_ref,
                    is_authorized=True,
                    revalidation_required=True,
                ),
                None,
            )

        # حدث مستقل تماماً يمثل جذراً جديداً
        new_root_id = f"root_{hashlib.sha256(event.event_id.encode()).hexdigest()[:12]}"
        self._active_roots.add(new_root_id)
        return (
            TaskRelationView(
                relation_kind="NEW_ROOT",
                target_root_ref=new_root_id,
                is_authorized=True,
                revalidation_required=False,
            ),
            None,
        )

    # ── Phase 9: Quiescence & Bounded Termination ──

    def derive_root_quiescence(
        self,
        root_authority_ref: str,
        frontier: InternalWorkFrontier,
        has_waiting_external_dependency: bool = False,
        budget_available: float = 10.0,
    ) -> RootQuiescenceView:
        """
        اشتقاق حالة السكون (Quiescence) للجذر المعرفي دون اللجوء إلى عدادات دوران تحكمية.
        """
        self.observability.quiescence_events += 1

        if root_authority_ref in self._cancelled_roots:
            return RootQuiescenceView(
                root_authority_ref=root_authority_ref,
                is_quiescent=True,
                quiescence_reason="ROOT_CANCELLED",
            )

        if has_waiting_external_dependency:
            # الانتظار لمدخلات خارجية مستقلة هو سكون شرعي وليس فشلاً أو اكتمالاً
            return RootQuiescenceView(
                root_authority_ref=root_authority_ref,
                is_quiescent=True,
                quiescence_reason="WAITING_EXTERNAL_INPUT",
            )

        if frontier.status == "EMPTY":
            return RootQuiescenceView(
                root_authority_ref=root_authority_ref,
                is_quiescent=True,
                quiescence_reason="ALL_WORK_COMPLETE",
            )

        if frontier.status == "AMBIGUOUS":
            return RootQuiescenceView(
                root_authority_ref=root_authority_ref,
                is_quiescent=True,
                quiescence_reason="MUTUAL_AMBIGUITY",
            )

        if budget_available <= 0.0:
            return RootQuiescenceView(
                root_authority_ref=root_authority_ref,
                is_quiescent=True,
                quiescence_reason="BUDGET_EXHAUSTED",
            )

        if frontier.status == "BLOCKED":
            return RootQuiescenceView(
                root_authority_ref=root_authority_ref,
                is_quiescent=True,
                quiescence_reason="NO_READY_WORK",
            )

        return RootQuiescenceView(
            root_authority_ref=root_authority_ref,
            is_quiescent=False,
            quiescence_reason="ACTIVE_WORK_AVAILABLE",
        )

    # ── Phase 10: Full Canonical Execution & Replay ──

    def execute_canonical_full_loop(
        self,
        question_text: str,
        concept_nodes: list[str],
        language_context: str = "en",
    ) -> tuple[SurfaceChunk | None, DeliveryStatusView | None, RootQuiescenceView]:
        """
        تنفيذ السيناريو المتكامل القياسي الشامل للحلقة المعرفية التوليدية الموحدة (RFC16-B12):
        دخول خارجي -> تمثيل -> استدلال/إتمام -> توليد هرمي -> تسليم -> استمرار -> سكون شرعي.
        """
        # 1. External Ingress
        event_id = f"ev_canon_{hashlib.sha256(question_text.encode()).hexdigest()[:8]}"
        root_ep_id = f"ep_canon_{hashlib.sha256(question_text.encode()).hexdigest()[:8]}"
        ev_rec, _is_novel = self.ingress_external_event(
            event_id=event_id,
            root_external_episode_id=root_ep_id,
            raw_content=question_text,
            ingress_boundary="canonical_ingress",
        )
        assert ev_rec is not None

        # 2. Build SDCR
        receipts = [
            ParticipationReceipt(
                receipt_id=f"rcpt_canon_{nid}",
                element_ref=nid,
                parent_cycle_id=1,
                snapshot_or_microtick=0,
                origin_lineage="external",
                participation_kind="node",
                activation_magnitude=0.9,
            )
            for nid in concept_nodes
        ]
        rep = self._graph.representation_engine.build_representation(1, 0, None, receipts)
        object.__setattr__(rep, "representation_id", "rep_canonical_loop")

        # 3. Stage A: Reasoning Work
        reas_id = f"work_reas_{event_id}"
        work_reas = InternalWorkAuthorityView(
            work_id=reas_id,
            root_authority_ref=root_ep_id,
            subsystem_kind="REASONING",
            scope_nodes=tuple(concept_nodes[:1]),
            is_authorized=True,
        )
        f_reas = self.derive_internal_work_frontier(root_ep_id, (work_reas,), set())
        assert f_reas.status == "READY"
        st_reas, _ = self.dispatch_internal_work(work_reas, rep, observed_version=self._graph.t)
        assert st_reas == "SUCCESS"

        # 4. Stage B: Generation Work (Dependent on reasoning completion)
        gen_id = f"work_gen_{event_id}"
        work_gen = InternalWorkAuthorityView(
            work_id=gen_id,
            root_authority_ref=root_ep_id,
            subsystem_kind="RFC14_GENERATION",
            scope_nodes=tuple(concept_nodes),
            is_authorized=True,
            prerequisite_work_ids=(reas_id,),
        )
        f_gen = self.derive_internal_work_frontier(root_ep_id, (work_reas, work_gen), {reas_id})
        assert f_gen.status == "READY"

        status, chunk = self.dispatch_internal_work(
            work=work_gen,
            representation=rep,
            observed_version=self._graph.t,
            budget=20.0,
        )
        assert status == "SUCCESS"
        assert isinstance(chunk, SurfaceChunk)

        # 5. Delivery Publication & Acknowledgment
        del_view = self.deliver_surface_output(chunk, str(rep.representation_id))
        assert del_view.status == "DELIVERED"
        ack_view = self.acknowledge_delivery(del_view.delivery_id)
        assert ack_view.status == "ACKNOWLEDGED"

        # 6. External Continuation Request
        ev_cont, _ = self.ingress_external_event(
            event_id=f"ev_cont_{event_id}",
            root_external_episode_id=f"ep_cont_{root_ep_id}",
            raw_content="continue",
        )
        assert ev_cont is not None
        task_rel, _ = self.process_task_relation(ev_cont, root_ep_id)
        assert task_rel.relation_kind == "CONTINUES"

        # 7. Final Lawful Quiescence
        done_frontier = self.derive_internal_work_frontier(root_ep_id, (work_reas, work_gen), {reas_id, gen_id})
        q_view = self.derive_root_quiescence(root_ep_id, done_frontier)
        assert q_view.is_quiescent is True

        return chunk, del_view, q_view


# ─────────────────────────────────────────────────────────── Behavioral Signature
def rfc16_behavioral_signature(engine: UnifiedGenerativeCognitiveLoopEngine) -> str:
    """
    حساب البصمة السلوكية المعيارية لـ RFC-16 من الحالة التشغيلية المشتقة وسجل الإسناد السببي.
    """
    rows: list[str] = []

    for eid in sorted(engine._ingress_events.keys()):
        ev = engine._ingress_events[eid]
        rows.append(f"EV|{ev.event_id}|root={ev.root_external_episode_id}|src={ev.source_origin}|mod={ev.modality}")

    for attr in engine._learning_attributions:
        elems = ",".join(sorted(str(e) for e in attr.mutated_elements))
        rows.append(f"ATTR|{attr.attribution_id}|ep={attr.root_external_episode_id}|own={attr.validation_owner}|elems=[{elems}]")

    for did in sorted(engine._delivery_records.keys()):
        d = engine._delivery_records[did]
        rows.append(f"DEL|{d.delivery_id}|chunk={d.surface_chunk_id}|st={d.status}|retries={d.retry_count}")

    for root in sorted(engine._cancelled_roots):
        rows.append(f"CANCEL|{root}")

    rows.append(
        f"OBS|ingress={engine.observability.ingress_events}|dedup={engine.observability.dedup_rejections}|"
        f"attr={engine.observability.learning_mutations_attributed}|unauth_blocks={engine.observability.unauthorized_feedback_blocks}|"
        f"dispatches={engine.observability.internal_dispatches}|deliveries={engine.observability.delivery_attempts}|"
        f"retries={engine.observability.delivery_retries}|quiescence={engine.observability.quiescence_events}"
    )

    blob = "\n".join(rows).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]
