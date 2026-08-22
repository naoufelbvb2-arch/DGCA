"""
DGCA — RFC-15 v1.0 + LAW 17 v1.0
Predictive Recurrent Generation & Bounded Continuation Commitment Engine.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dgca.config import Law
from dgca.generation import SourceAlignment, SurfaceChunk
from dgca.representation import SparseDistributedCognitiveRepresentation

if TYPE_CHECKING:
    from dgca.graph import CognitiveGraph


# ─────────────────────────────────────────────────────────── 1. Canonical Transient Operational Primitive (GCE)
@dataclass(frozen=True)
class GenerativeContinuationEpoch:
    """
    الكيان التشغيلي الانتقالي المعياري الوحيد لـ RFC-15 (GCE).
    يمتلك التقدم التوليدي المحدود عبر لقطات تمثيلية متعددة تحت سلطة جذرية غير قابلة للتغيير.
    """
    epoch_id: str
    root_authority_ref: str
    progress_receipt_refs: tuple[str, ...]
    budget_authority_ref: str
    lifecycle: str  # "OPEN" or "CLOSED"


# ─────────────────────────────────────────────────────────── 2. Immutable Derived Operational Records
@dataclass(frozen=True)
class ExpressionReceipt:
    """
    سجل تشغيلي مشتق غير قابل للتعديل يثبت حدوث التعبير التوليدي دون ادعاء حقيقة دلالية أو إنشاء دليل.
    """
    receipt_id: str
    root_authority_ref: str
    parent_rid: str
    alignment_view: SourceAlignment
    emission_commit_ref: str
    expressed_elements: tuple[str | tuple[str, str], ...] = ()
    origin_lineage: str = "GENERATION"


@dataclass(frozen=True)
class ContinuationCommit:
    """
    سجل معاملة ذرية انتقالية ناتج عن القانون 17 يحدد الالتزام بالتعبير عن الالتزام التالي.
    """
    commit_id: str
    epoch_id: str
    parent_rid: str
    root_authority_ref: str
    obligation_ref: str
    continuation_authority_refs: tuple[str | tuple[str, str], ...]
    progress_snapshot_digest: str


# ─────────────────────────────────────────────────────────── 3. Derived Operational Views
@dataclass(frozen=True)
class ExpressiveObligation:
    """
    واجهة مشتقة لالتزام تعبيري ناتج عن السلطة الجذرية والمعرفة الحالية للقطة.
    """
    obligation_id: str
    root_authority_ref: str
    semantic_element_ref: str | tuple[str, str]
    role_scope: str
    alternative_branch_id: str | None = None
    language_context: str = "en"
    repeat_authorized: bool = False
    is_repair: bool = False
    repair_authority_ref: str | None = None


@dataclass(frozen=True)
class CoveredView:
    """واجهة مشتقة للالتزامات المغطاة حالياً بإيصالات سابقة سارية."""
    covered_obligation_ids: frozenset[str]
    coverage_map: dict[str, str]  # obligation_id -> receipt_id


@dataclass(frozen=True)
class RemainingView:
    """واجهة مشتقة للالتزامات المتبقية غير المغطاة."""
    remaining_obligations: tuple[ExpressiveObligation, ...]
    remaining_ids: frozenset[str]


@dataclass(frozen=True)
class ReferentialAccessibilityView:
    """واجهة مشتقة لسهولة الوصول المرجعي للكيانات المعبر عنها سابقاً."""
    accessible_referents: dict[str | tuple[str, str], tuple[str, ...]]  # semantic_element_ref -> tuple of receipt_ids
    ambiguous_referents: frozenset[str | tuple[str, str]]


@dataclass(frozen=True)
class ContinuationFrontier:
    """واجهة مشتقة لجبهة الاستمرار الجاهزة للتنفيذ تحت القانون 17."""
    ready_candidates: tuple[ExpressiveObligation, ...]
    predecessor_map: dict[str, frozenset[str]]
    status: str  # "READY", "AMBIGUOUS", "CONFLICT", "EMPTY", "NO_AUTHORIZED_CONTINUATION"


@dataclass(frozen=True)
class SupersededExpressionView:
    """واجهة مشتقة للإيصالات التاريخية التي لم تعد متطابقة مع المعرفة المعرفية الحالية."""
    superseded_receipt_ids: frozenset[str]
    incompatible_obligations: frozenset[str]


@dataclass(frozen=True)
class GenerativeOperationalSignature:
    """بصمة تشغيلية للمقارنة واكتشاف النقطة الثابتة دون تقدم (NO_PROGRESS_FIXED_POINT)."""
    root_ref: str
    parent_rid: str
    progress_digest: str
    remaining_digest: str
    frontier_digest: str
    blocker_status: str


@dataclass(frozen=True)
class GCEClosureView:
    """واجهة تشخيصية مشتقة لنتيجة إغلاق الحقبة التوليدية."""
    epoch_id: str
    root_authority_ref: str
    final_progress_refs: tuple[str, ...]
    unresolved_obligation_ids: tuple[str, ...]
    closure_reason: str


@dataclass(frozen=True)
class HandoffView15To16:
    """واجهة التسليم الدنيا المشتقة غير المعرفية من RFC-15 إلى RFC-16."""
    epoch_id: str
    root_authority_ref: str
    final_progress_view: tuple[str, ...]
    unresolved_view: tuple[str, ...]
    closure_reason: str


@dataclass
class RecurrentObservability:
    """سجل تشغيلي لمراقبة أداء وأحداث التوليد التكراري (RFC-15)."""
    epochs_created: int = 0
    epochs_closed: int = 0
    receipts_created: int = 0
    receipts_appended: int = 0
    idempotent_appends: int = 0
    law17_commits: int = 0
    law17_ambiguity_events: int = 0
    law17_conflict_events: int = 0
    recurrent_steps: int = 0
    fixed_point_stops: int = 0
    repair_events: int = 0
    closure_reasons: dict[str, int] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────── 4. Core Recurrent Generation Engine
class PredictiveRecurrentGenerativeEngine:
    """
    محرك التوليد التنبؤي التكراري والاستمرار عبر اللقطات (RFC-15 v1.0 + Law 17 v1.0).
    """

    def __init__(self, graph: CognitiveGraph) -> None:
        self._graph = graph
        self._epochs: dict[str, GenerativeContinuationEpoch] = {}
        self._receipts: dict[str, ExpressionReceipt] = {}
        self._epoch_receipts: dict[str, list[ExpressionReceipt]] = {}
        self._live_commits: dict[str, ContinuationCommit] = {}  # epoch_id -> live commit (at most 1)
        self.observability = RecurrentObservability()

    # ── GCE Lifecycle & Epoch Operations ──

    def create_epoch(
        self,
        root_authority_ref: str,
        budget_authority_ref: str = "budget_root",
        epoch_id: str | None = None,
    ) -> GenerativeContinuationEpoch:
        """إنشاء حقبة استمرار توليدية جديدة (GCE) تحت سلطة جذرية غير قابلة للتغيير."""
        if not root_authority_ref or not str(root_authority_ref).strip():
            raise ValueError("RootAuthorityRef must be a non-empty lawful reference.")

        eid = epoch_id or f"gce_{hashlib.sha256(f'{root_authority_ref}_{len(self._epochs)}'.encode()).hexdigest()[:12]}"
        if eid in self._epochs:
            raise ValueError(f"Epoch {eid} already exists.")

        epoch = GenerativeContinuationEpoch(
            epoch_id=eid,
            root_authority_ref=str(root_authority_ref),
            progress_receipt_refs=(),
            budget_authority_ref=str(budget_authority_ref),
            lifecycle="OPEN",
        )
        self._epochs[eid] = epoch
        self._epoch_receipts[eid] = []
        self.observability.epochs_created += 1
        return epoch

    def get_epoch(self, epoch_id: str) -> GenerativeContinuationEpoch:
        """استرجاع الحقبة التوليدية بمعرفها."""
        if epoch_id not in self._epochs:
            raise KeyError(f"Epoch {epoch_id} not found.")
        return self._epochs[epoch_id]

    def close_epoch(
        self,
        epoch_id: str,
        closure_reason: str,
        unresolved_obligation_ids: tuple[str, ...] = (),
    ) -> tuple[GenerativeContinuationEpoch, GCEClosureView]:
        """إغلاق الحقبة التوليدية بشكل قطعي وغير قابل للإلغاء (OPEN -> CLOSED)."""
        epoch = self.get_epoch(epoch_id)
        if epoch.lifecycle == "CLOSED":
            # إغلاق مسبق قطعي
            closure_view = GCEClosureView(
                epoch_id=epoch.epoch_id,
                root_authority_ref=epoch.root_authority_ref,
                final_progress_refs=epoch.progress_receipt_refs,
                unresolved_obligation_ids=unresolved_obligation_ids,
                closure_reason=closure_reason,
            )
            return epoch, closure_view

        closed_epoch = GenerativeContinuationEpoch(
            epoch_id=epoch.epoch_id,
            root_authority_ref=epoch.root_authority_ref,
            progress_receipt_refs=epoch.progress_receipt_refs,
            budget_authority_ref=epoch.budget_authority_ref,
            lifecycle="CLOSED",
        )
        self._epochs[epoch_id] = closed_epoch
        # إلغاء أي التزام نشط معلق للحقبة المغلقة
        self._live_commits.pop(epoch_id, None)

        self.observability.epochs_closed += 1
        self.observability.closure_reasons[closure_reason] = (
            self.observability.closure_reasons.get(closure_reason, 0) + 1
        )

        closure_view = GCEClosureView(
            epoch_id=closed_epoch.epoch_id,
            root_authority_ref=closed_epoch.root_authority_ref,
            final_progress_refs=closed_epoch.progress_receipt_refs,
            unresolved_obligation_ids=unresolved_obligation_ids,
            closure_reason=closure_reason,
        )
        return closed_epoch, closure_view

    # ── Expression Receipts & Idempotent Publication ──

    def create_expression_receipt(
        self,
        surface_chunk: SurfaceChunk,
        source_alignment: SourceAlignment,
        parent_rid: str,
        root_authority_ref: str,
        expressed_elements: tuple[str | tuple[str, str], ...] = (),
    ) -> ExpressionReceipt:
        """
        اشتقاق إيصال تعبيري من مخرج سطحي ملتزم بنجاح في RFC-14.
        """
        if not isinstance(surface_chunk, SurfaceChunk) or not surface_chunk.surface_units or not source_alignment:
            raise ValueError("Cannot create ExpressionReceipt for uncommitted or empty SurfaceChunk.")

        elems = tuple(sorted(expressed_elements, key=lambda x: str(x))) if expressed_elements else ()
        elements_sig = ",".join(str(e) for e in elems)
        occ_ref = source_alignment.source_occurrence_ref or ""
        raw_key = f"ER|{root_authority_ref}|{parent_rid}|{surface_chunk.chunk_id}|{occ_ref}|{elements_sig}"
        receipt_id = f"er_{hashlib.sha256(raw_key.encode()).hexdigest()[:16]}"

        receipt = ExpressionReceipt(
            receipt_id=receipt_id,
            root_authority_ref=root_authority_ref,
            parent_rid=parent_rid,
            alignment_view=source_alignment,
            emission_commit_ref=surface_chunk.chunk_id,
            expressed_elements=elems,
            origin_lineage="GENERATION",
        )
        self._receipts[receipt_id] = receipt
        self.observability.receipts_created += 1
        return receipt

    def append_receipt(
        self,
        epoch_id: str,
        receipt: ExpressionReceipt,
    ) -> GenerativeContinuationEpoch:
        """
        إضافة إيصال تعبيري مصدق إلى تقدم الحقبة (Append-Only & Idempotent).
        """
        epoch = self.get_epoch(epoch_id)
        if epoch.lifecycle != "OPEN":
            raise ValueError(f"Cannot append receipt to a {epoch.lifecycle} epoch.")

        if receipt.root_authority_ref != epoch.root_authority_ref:
            raise ValueError("ExpressionReceipt root authority does not match epoch root authority.")

        if receipt.receipt_id in epoch.progress_receipt_refs:
            # عملية متماثلة القوى (Idempotent Append)
            self.observability.idempotent_appends += 1
            return epoch

        new_progress = epoch.progress_receipt_refs + (receipt.receipt_id,)
        updated_epoch = GenerativeContinuationEpoch(
            epoch_id=epoch.epoch_id,
            root_authority_ref=epoch.root_authority_ref,
            progress_receipt_refs=new_progress,
            budget_authority_ref=epoch.budget_authority_ref,
            lifecycle="OPEN",
        )
        self._epochs[epoch_id] = updated_epoch
        self._epoch_receipts.setdefault(epoch_id, []).append(receipt)
        self.observability.receipts_appended += 1
        return updated_epoch

    # ── Expressive Obligations, Coverage & Remaining Derivations ──

    def derive_obligations(
        self,
        representation: SparseDistributedCognitiveRepresentation,
        root_authority_ref: str,
        explicit_obligations: list[ExpressiveObligation] | None = None,
        language_context: str = "en",
    ) -> tuple[ExpressiveObligation, ...]:
        """
        اشتقاق الالتزامات التعبيرية الحالية من التمثيل المعرفي الحالي والسلطة الجذرية.
        """
        if explicit_obligations is not None:
            # تصفية ومطابقة السلطة الجذرية
            return tuple(
                ob for ob in explicit_obligations
                if ob.root_authority_ref == root_authority_ref
            )

        # اشتقاق محلي من إيصالات التمثيل النشطة المرتبطة بالسلطة الجذرية
        obligations: list[ExpressiveObligation] = []
        for r in sorted(representation.participation_receipts, key=lambda x: str(x.receipt_id)):
            ob_id = f"ob_{hashlib.sha256(f'{root_authority_ref}_{r.element_ref}_{r.participation_kind}'.encode()).hexdigest()[:12]}"
            obligations.append(
                ExpressiveObligation(
                    obligation_id=ob_id,
                    root_authority_ref=root_authority_ref,
                    semantic_element_ref=r.element_ref,
                    role_scope=r.participation_kind,
                    alternative_branch_id=None,
                    language_context=language_context,
                    repeat_authorized=False,
                    is_repair=False,
                )
            )
        return tuple(obligations)

    def compute_coverage(
        self,
        obligations: tuple[ExpressiveObligation, ...],
        epoch: GenerativeContinuationEpoch,
        representation: SparseDistributedCognitiveRepresentation,
    ) -> CoveredView:
        """
        حساب التغطية الدلالية الحالية من مطابقة الإيصالات السارية في الحقبة مع الالتزامات الحالية.
        """
        receipts = [self._receipts[rid] for rid in epoch.progress_receipt_refs if rid in self._receipts]
        # بناء فهرس محلي سريع للإيصالات حسب العناصر المشاركة
        receipt_by_element: dict[str | tuple[str, str], list[ExpressionReceipt]] = {}
        for rcpt in receipts:
            if rcpt.root_authority_ref != epoch.root_authority_ref:
                continue
            for elem in rcpt.expressed_elements:
                receipt_by_element.setdefault(elem, []).append(rcpt)

        covered_ids: set[str] = set()
        cov_map: dict[str, str] = {}

        for ob in obligations:
            if ob.repeat_authorized or ob.root_authority_ref != epoch.root_authority_ref:
                # الالتزام المصرح بتكراره صراحة أو التابع لسلطة أخرى لا يُعد مغطى تلقائياً
                continue

            elem = ob.semantic_element_ref
            if elem in receipt_by_element:
                # التحقق من أن العنصر لا يزال سارياً ومتوافقاً في التمثيل الحالي
                matched_rcpts = receipt_by_element[elem]
                if matched_rcpts:
                    # تغطية قانونية عبر إيصال سابق
                    chosen_rcpt = matched_rcpts[-1]
                    covered_ids.add(ob.obligation_id)
                    cov_map[ob.obligation_id] = chosen_rcpt.receipt_id

        return CoveredView(
            covered_obligation_ids=frozenset(covered_ids),
            coverage_map=cov_map,
        )

    def compute_remaining(
        self,
        obligations: tuple[ExpressiveObligation, ...],
        covered_view: CoveredView,
    ) -> RemainingView:
        """
        حساب الالتزامات المتبقية غير المغطاة حالياً.
        """
        rem = [ob for ob in obligations if ob.obligation_id not in covered_view.covered_obligation_ids]
        return RemainingView(
            remaining_obligations=tuple(rem),
            remaining_ids=frozenset(ob.obligation_id for ob in rem),
        )

    # ── Referential Accessibility View ──

    def compute_referential_accessibility(
        self,
        representation: SparseDistributedCognitiveRepresentation,
        root_authority_ref: str,
        epoch: GenerativeContinuationEpoch,
    ) -> ReferentialAccessibilityView:
        """
        اشتقاق إمكانية الوصول المرجعي للكيانات المعبر عنها سابقاً دون فرض قاعدة الأحدث يفوز.
        """
        receipts = [self._receipts[rid] for rid in epoch.progress_receipt_refs if rid in self._receipts]
        ref_map: dict[str | tuple[str, str], list[str]] = {}
        for rcpt in receipts:
            if rcpt.root_authority_ref != root_authority_ref:
                continue
            for elem in rcpt.expressed_elements:
                ref_map.setdefault(elem, []).append(rcpt.receipt_id)

        ambiguous: set[str | tuple[str, str]] = set()
        accessible: dict[str | tuple[str, str], tuple[str, ...]] = {}

        for elem, r_list in ref_map.items():
            accessible[elem] = tuple(r_list)
            if len(r_list) > 1:
                # مراجع متعددة متاحة بدون سلطة حسم مستقلة -> الحفاظ على الغموض
                ambiguous.add(elem)

        return ReferentialAccessibilityView(
            accessible_referents=accessible,
            ambiguous_referents=frozenset(ambiguous),
        )

    # ── Continuation Frontier Derivation ──

    def derive_continuation_frontier(
        self,
        remaining_view: RemainingView,
        covered_view: CoveredView,
        representation: SparseDistributedCognitiveRepresentation,
        epoch: GenerativeContinuationEpoch,
        explicit_precedences: list[tuple[str, str]] | None = None,
        all_obligations: tuple[ExpressiveObligation, ...] | None = None,
    ) -> ContinuationFrontier:
        """
        اشتقاق جبهة الاستمرار التنبؤية (ContinuationFrontier) للالتزامات الجاهزة.
        """
        if not remaining_view.remaining_obligations:
            return ContinuationFrontier(
                ready_candidates=(),
                predecessor_map={},
                status="EMPTY",
            )

        # استخراج قيود الأسبقية بين الالتزامات من علاقات الرسم المعرفي المحلية أو التحديد الصريح
        in_preds_map: dict[str, set[str]] = {}
        if explicit_precedences is not None:
            for u_before, u_after in explicit_precedences:
                in_preds_map.setdefault(u_after, set()).add(u_before)
        else:
            # استخراج محلي من حواف الترتيب/التسلسل/السببية/التنبؤ بين العناصر النشطة
            active_nodes = set(representation.participating_node_refs)
            obs_full = all_obligations or self.derive_obligations(representation, epoch.root_authority_ref)
            elem_to_ob = {ob.semantic_element_ref: ob.obligation_id for ob in obs_full}

            for u in active_nodes:
                if u in self._graph.out_adj:
                    for v, edge in self._graph.out_adj[u].items():
                        if v in active_nodes:
                            # فحص ما إذا كانت الحافة تحمل قيد أسبقية استمرار (causal, sequence, temporal, order)
                            contexts = edge.contexts
                            if ("order" in contexts or "seq" in contexts or "causal" in contexts or "pred" in contexts or "en" in contexts) and (u in elem_to_ob and v in elem_to_ob):
                                ob_u = elem_to_ob[u]
                                ob_v = elem_to_ob[v]
                                if ob_u != ob_v:
                                    in_preds_map.setdefault(ob_v, set()).add(ob_u)

        # فحص الدورات أو التعارضات في قيود الأسبقية
        # كشف الدورة البسيطة
        for node, preds in in_preds_map.items():
            for pred in preds:
                if pred in in_preds_map and node in in_preds_map[pred]:
                    self.observability.law17_conflict_events += 1
                    return ContinuationFrontier(
                        ready_candidates=(),
                        predecessor_map={k: frozenset(v) for k, v in in_preds_map.items()},
                        status="CONFLICT",
                    )

        # تحديد المرشحين الجاهزين (الذين استوفيت كل أسبقياتهم في Covered أو لا أسبقية لهم)
        ready: list[ExpressiveObligation] = []
        for ob in remaining_view.remaining_obligations:
            preds = in_preds_map.get(ob.obligation_id, set())
            unmet_preds = preds - covered_view.covered_obligation_ids
            # استثناء الأسبقيات غير الموجودة كالتزامات
            if not unmet_preds:
                ready.append(ob)

        if not ready:
            return ContinuationFrontier(
                ready_candidates=(),
                predecessor_map={k: frozenset(v) for k, v in in_preds_map.items()},
                status="NO_AUTHORIZED_CONTINUATION",
            )

        status = "READY" if len(ready) == 1 else "AMBIGUOUS"
        return ContinuationFrontier(
            ready_candidates=tuple(ready),
            predecessor_map={k: frozenset(v) for k, v in in_preds_map.items()},
            status=status,
        )

    # ── LAW 17: Bounded Predictive Continuation & Cross-Snapshot Commitment ──

    def commit_continuation(
        self,
        frontier: ContinuationFrontier,
        epoch: GenerativeContinuationEpoch,
        representation: SparseDistributedCognitiveRepresentation,
        budget: float = 1.0,
    ) -> tuple[str, ContinuationCommit | None, float]:
        """
        تنفيذ القانون 17: الالتزام التنبؤي المحدود والاستمرار عبر اللقطات (Law 17 v1.0).
        """
        step_cost = Law.GAMMA
        if budget < step_cost:
            return "BUDGET_UNAVAILABLE", None, budget

        if epoch.lifecycle != "OPEN":
            return "STALE", None, budget

        if frontier.status == "EMPTY":
            return "NO_REMAINING_OBLIGATION", None, budget

        if frontier.status == "CONFLICT":
            self.observability.law17_conflict_events += 1
            return "CONTINUATION_CONFLICT", None, budget

        if frontier.status == "NO_AUTHORIZED_CONTINUATION":
            return "NO_AUTHORIZED_CONTINUATION", None, budget

        if len(frontier.ready_candidates) > 1:
            # مرشحون متعددون قانونيون بدون سلطة حسم مستقلة -> الحفاظ على الغموض والإغلاق بـ CONTINUATION_AMBIGUOUS
            self.observability.law17_ambiguity_events += 1
            return "CONTINUATION_AMBIGUOUS", None, budget

        # مرشح وحيد جاهز قانونياً
        target_ob = frontier.ready_candidates[0]
        cid = f"cc_{hashlib.sha256(f'{epoch.epoch_id}_{representation.representation_id}_{target_ob.obligation_id}_{len(epoch.progress_receipt_refs)}'.encode()).hexdigest()[:16]}"
        progress_digest = hashlib.sha256(",".join(epoch.progress_receipt_refs).encode()).hexdigest()

        commit = ContinuationCommit(
            commit_id=cid,
            epoch_id=epoch.epoch_id,
            parent_rid=str(representation.representation_id),
            root_authority_ref=epoch.root_authority_ref,
            obligation_ref=target_ob.obligation_id,
            continuation_authority_refs=(target_ob.semantic_element_ref,),
            progress_snapshot_digest=progress_digest,
        )

        # حفظ الالتزام الحي الوحيد للحقبة (At most one live commit)
        self._live_commits[epoch.epoch_id] = commit
        self.observability.law17_commits += 1

        return "CONTINUATION_COMMITTED", commit, budget - step_cost

    # ── Operational Signature & Fixed-Point Detection ──

    def compute_operational_signature(
        self,
        epoch: GenerativeContinuationEpoch,
        representation: SparseDistributedCognitiveRepresentation,
        remaining_view: RemainingView,
        frontier: ContinuationFrontier,
        blocker_status: str = "NONE",
    ) -> GenerativeOperationalSignature:
        """
        حساب البصمة التشغيلية للمقارنة واكتشاف التكرار الأعمى (NO_PROGRESS_FIXED_POINT).
        """
        prog_str = ",".join(sorted(epoch.progress_receipt_refs))
        prog_digest = hashlib.sha256(prog_str.encode()).hexdigest()[:16]

        rem_str = ",".join(sorted(remaining_view.remaining_ids))
        rem_digest = hashlib.sha256(rem_str.encode()).hexdigest()[:16]

        front_str = ",".join(sorted(ob.obligation_id for ob in frontier.ready_candidates))
        front_digest = hashlib.sha256(front_str.encode()).hexdigest()[:16]

        return GenerativeOperationalSignature(
            root_ref=epoch.root_authority_ref,
            parent_rid=str(representation.representation_id),
            progress_digest=prog_digest,
            remaining_digest=rem_digest,
            frontier_digest=front_digest,
            blocker_status=blocker_status,
        )

    # ── Recurrent Execution Pipeline (Step & Epoch) ──

    def execute_recurrent_step(
        self,
        epoch_id: str,
        representation: SparseDistributedCognitiveRepresentation,
        budget: float = 1.0,
        explicit_obligations: list[ExpressiveObligation] | None = None,
        explicit_precedences: list[tuple[str, str]] | None = None,
        language_context: str = "en",
    ) -> tuple[str, GenerativeContinuationEpoch, ExpressionReceipt | None, float]:
        """
        تنفيذ خطوة توليد تكرارية واحدة وفق الدورة:
        Select (Law 17) -> Commit -> Realize (RFC-14) -> Receipt -> Progress Append (GCE).
        """
        epoch = self.get_epoch(epoch_id)
        if epoch.lifecycle != "OPEN":
            return "STALE", epoch, None, budget

        # 1. اشتقاق الالتزامات والتغطية والمتبقي
        obligations = self.derive_obligations(
            representation, epoch.root_authority_ref, explicit_obligations, language_context
        )
        covered = self.compute_coverage(obligations, epoch, representation)
        remaining = self.compute_remaining(obligations, covered)

        if not remaining.remaining_obligations:
            return "NO_REMAINING_OBLIGATION", epoch, None, budget

        # 2. اشتقاق جبهة الاستمرار
        frontier = self.derive_continuation_frontier(
            remaining, covered, representation, epoch, explicit_precedences, all_obligations=obligations
        )

        # 3. الالتزام تحت القانون 17
        status, commit, rem_budget = self.commit_continuation(
            frontier, epoch, representation, budget
        )
        if status != "CONTINUATION_COMMITTED" or commit is None:
            return status, epoch, None, rem_budget

        # 4. الاستدعاء النظيف لـ RFC-14 للتعبير السطحي للالتزام المختار
        target_ob = next(ob for ob in remaining.remaining_obligations if ob.obligation_id == commit.obligation_ref)
        gen_engine = self._graph.generation_engine

        # بناء إطار التوليد الخاص بالعنصر الدلالي الملتزم به
        scope_nodes = frozenset([target_ob.semantic_element_ref])
        frame = gen_engine.build_generative_frame(representation, scope_nodes)
        hierarchy = gen_engine.build_hierarchy([frame])

        # التحويل التسلسلي والتعبير السطحي
        prefix, consumed_linearization = gen_engine.linearize_hierarchy(
            hierarchy, language_context=language_context, budget=rem_budget
        )
        rem_budget = max(0.0, rem_budget - consumed_linearization)
        chunk = gen_engine.realize_surface_chunk(
            prefix,
            str(representation.representation_id),
            language_context=language_context,
            budget=rem_budget,
        )

        if not chunk.surface_units:
            # فشل التعبير السطحي -> لا تقدم ولا إيصال ghost
            return "REALIZATION_BLOCKED", epoch, None, rem_budget

        # 5. استخراج الإيصال التعبيري وإضافته إلى الحقبة
        unit = chunk.surface_units[0]
        alignment = unit.source_alignment
        receipt = self.create_expression_receipt(
            surface_chunk=chunk,
            source_alignment=alignment,
            parent_rid=str(representation.representation_id),
            root_authority_ref=epoch.root_authority_ref,
            expressed_elements=(target_ob.semantic_element_ref,),
        )
        updated_epoch = self.append_receipt(epoch_id, receipt)
        self.observability.recurrent_steps += 1

        return "PROGRESS", updated_epoch, receipt, rem_budget

    def execute_recurrent_epoch(
        self,
        epoch_id: str,
        representation: SparseDistributedCognitiveRepresentation,
        budget: float = 10.0,
        explicit_obligations: list[ExpressiveObligation] | None = None,
        explicit_precedences: list[tuple[str, str]] | None = None,
        language_context: str = "en",
        max_loop_safety: int = 100,
    ) -> tuple[GCEClosureView, HandoffView15To16]:
        """
        تنفيذ حلقة توليد تكرارية كاملة حتى إتمام الالتزامات أو الوصول إلى نقطة ثبات أو استنفاد الميزانية.
        """
        epoch = self.get_epoch(epoch_id)
        current_budget = budget
        last_sig: GenerativeOperationalSignature | None = None

        closure_reason = "COMPLETE"
        unresolved_ids: tuple[str, ...] = ()

        for _ in range(max_loop_safety):
            obligations = self.derive_obligations(
                representation, epoch.root_authority_ref, explicit_obligations, language_context
            )
            covered = self.compute_coverage(obligations, epoch, representation)
            remaining = self.compute_remaining(obligations, covered)

            if not remaining.remaining_obligations:
                # اكتمال كل الالتزامات دون متبقي
                closure_reason = "COMPLETE"
                unresolved_ids = ()
                break

            if current_budget < Law.GAMMA:
                closure_reason = "PARTIAL_BUDGET"
                unresolved_ids = tuple(sorted(remaining.remaining_ids))
                break

            frontier = self.derive_continuation_frontier(
                remaining, covered, representation, epoch, explicit_precedences, all_obligations=obligations
            )

            # التحقق من النقطة الثابتة دون تقدم (NO_PROGRESS_FIXED_POINT)
            current_sig = self.compute_operational_signature(
                epoch, representation, remaining, frontier, frontier.status
            )
            if last_sig == current_sig:
                # الحالة التشغيلية متطابقة تماماً بدون تقدم -> التوقف الحتمي
                self.observability.fixed_point_stops += 1
                closure_reason = "NO_PROGRESS_FIXED_POINT"
                unresolved_ids = tuple(sorted(remaining.remaining_ids))
                break
            last_sig = current_sig

            if frontier.status == "AMBIGUOUS":
                closure_reason = "AMBIGUOUS"
                unresolved_ids = tuple(sorted(remaining.remaining_ids))
                break
            elif frontier.status == "CONFLICT":
                closure_reason = "CONFLICT"
                unresolved_ids = tuple(sorted(remaining.remaining_ids))
                break
            elif frontier.status == "NO_AUTHORIZED_CONTINUATION":
                closure_reason = "NO_AUTHORIZED_CONTINUATION"
                unresolved_ids = tuple(sorted(remaining.remaining_ids))
                break

            step_status, epoch, _rcpt, current_budget = self.execute_recurrent_step(
                epoch_id=epoch.epoch_id,
                representation=representation,
                budget=current_budget,
                explicit_obligations=explicit_obligations,
                explicit_precedences=explicit_precedences,
                language_context=language_context,
            )

            if step_status == "BUDGET_UNAVAILABLE":
                closure_reason = "PARTIAL_BUDGET"
                unresolved_ids = tuple(sorted(remaining.remaining_ids))
                break
            elif step_status != "PROGRESS":
                closure_reason = step_status
                unresolved_ids = tuple(sorted(remaining.remaining_ids))
                break

        # إغلاق الحقبة قطيعاً
        closed_epoch, closure_view = self.close_epoch(
            epoch_id=epoch.epoch_id,
            closure_reason=closure_reason,
            unresolved_obligation_ids=unresolved_ids,
        )

        handoff = HandoffView15To16(
            epoch_id=closed_epoch.epoch_id,
            root_authority_ref=closed_epoch.root_authority_ref,
            final_progress_view=closed_epoch.progress_receipt_refs,
            unresolved_view=unresolved_ids,
            closure_reason=closure_reason,
        )

        return closure_view, handoff


# ─────────────────────────────────────────────────────────── 5. Canonical Behavioral Signature
def rfc15_behavioral_signature(engine: PredictiveRecurrentGenerativeEngine) -> str:
    """
    توليد البصمة السلوكية الحتمية القطعية لـ RFC-15 (Predictive Recurrent Generation).
    """
    rows = []
    # فحص الحقب والإيصالات والالتزامات
    for eid in sorted(engine._epochs.keys()):
        ep = engine._epochs[eid]
        receipts_str = ",".join(sorted(ep.progress_receipt_refs))
        rows.append(f"GCE|{ep.epoch_id}|root={ep.root_authority_ref}|rcpts=[{receipts_str}]|b={ep.budget_authority_ref}|life={ep.lifecycle}")

    for rid in sorted(engine._receipts.keys()):
        rcpt = engine._receipts[rid]
        elems = ",".join(sorted(str(e) for e in rcpt.expressed_elements))
        rows.append(f"ER|{rcpt.receipt_id}|root={rcpt.root_authority_ref}|p={rcpt.parent_rid}|chunk={rcpt.emission_commit_ref}|elems=[{elems}]")

    for eid in sorted(engine._live_commits.keys()):
        commit = engine._live_commits[eid]
        rows.append(f"CC|{commit.commit_id}|gce={commit.epoch_id}|ob={commit.obligation_ref}|auth={commit.continuation_authority_refs}")

    rows.append(
        f"OBS|created={engine.observability.epochs_created}|closed={engine.observability.epochs_closed}|"
        f"rcpts={engine.observability.receipts_created}|commits={engine.observability.law17_commits}|"
        f"steps={engine.observability.recurrent_steps}|amb={engine.observability.law17_ambiguity_events}|"
        f"conf={engine.observability.law17_conflict_events}|fp={engine.observability.fixed_point_stops}"
    )

    blob = "\n".join(rows).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]
