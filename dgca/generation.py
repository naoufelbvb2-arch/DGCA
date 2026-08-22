"""
DGCA — RFC-14 v1.0 / LAW 16 v1.0
Hierarchical Generative & Syntactic Dynamics + Law 16.

This module implements:
1. GenerativeFrame: The single new canonical transient operational primitive.
2. GenerativeHierarchy: Derived acyclic forest view over current generative frames.
3. Task-Scoped Local Expansion: Incremental expansion bounded by current SDCR and task scope.
4. LAW 16: Bounded Hierarchical Linearization & Local Syntactic Commitment (Precedence Graph, Ready Frontier).
5. Lexicalization & Morphology: Concept != Lexeme != SurfaceForm, local context-bound candidate lookup.
6. Surface Realization: SurfaceBundle, SurfaceUnit, SurfaceChunk with GENERATION/SelfDerived provenance.
7. RFC-14 -> RFC-15 Handoff: Minimal reference-based stale-detectable HandoffView.
"""
from __future__ import annotations

import dataclasses
import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .graph import CognitiveGraph
    from .representation import SparseDistributedCognitiveRepresentation

from .config import Law


# ─────────────────────────────────────────────────────────── 1. Constitutional Operational Primitives & Views
@dataclass(frozen=True)
class RoleBinding:
    """
    ربط دور دلالي غير مرتب مرجعي (RFC-14.2).
    يربط سلطة دور مع محتوى معرفي حالي أو إطار ابن.
    """
    role_authority_ref: str
    filler_ref: str  # CognitiveRef (node/edge) or ChildFrameID


@dataclass(frozen=True)
class GenerativeFrame:
    """
    إطار توليدي هرمي مرجعي مؤقت (RFC-14.2).
    الوحدة التشغيلية المرجعية الأساسية الوحيدة الجديدة في RFC-14.
    F = <FID, ParentRID, ScopeView, AnchorRefs, RoleBindings>
    """
    frame_id: str
    parent_representation_id: str
    scope_view: tuple[str, ...]
    anchor_refs: frozenset[str]
    role_bindings: tuple[RoleBinding, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.frame_id:
            raise ValueError("frame_id must be non-empty operational string")
        if not self.parent_representation_id:
            raise ValueError("parent_representation_id is mandatory and cannot be empty")
        if not self.anchor_refs:
            raise ValueError("anchor_refs must be non-empty current lawful references")


@dataclass
class GenerativeHierarchy:
    """
    منظور هرمي مشتق فوق الإطارات التوليدية الحالية (RFC-14.2 / 4.3).
    H_t = (F_t, E^F_t)
    """
    root_frame_ids: tuple[str, ...]
    frames: dict[str, GenerativeFrame]
    child_to_parent: dict[str, str] = field(default_factory=dict)
    is_acyclic: bool = True


@dataclass(frozen=True)
class GenerationScope:
    """
    نطاق التوليد المشتق من سلطة المهمة/الاستعلام الحالية (RFC-14.3).
    """
    task_ref: str | None = None
    query_ref: str | None = None
    event_ref: str | None = None
    reasoning_ref: str | None = None
    permitted_roles: frozenset[str] | None = None
    target_concept_ref: str | None = None


@dataclass(frozen=True)
class ExpansionOption:
    """
    خيار توسع هرمي محلي مشتق من حدود التوسع (RFC-14.3).
    """
    frame_id: str
    role_authority_ref: str
    filler_ref: str
    is_child_frame: bool = False


@dataclass(frozen=True)
class GenerativeExpansionFrontier:
    """
    جبهة التوسع التوليدي المحلي المؤقتة (RFC-14.3).
    """
    options: tuple[ExpansionOption, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LinearizableOccurrence:
    """
    ظهور خطي مشتق لإطار أو دور في التسلسل السطحي (RFC-14.4 / 6.3).
    الهوية هنا هي هوية ظهور تشغيلي وليست هوية معرفية ثابتة.
    """
    occurrence_id: str
    frame_id: str
    role_authority_ref: str
    filler_ref: str
    is_child_frame: bool = False
    scope_view: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PrecedenceGraph:
    """
    مخطط الأسبقية النحوية المشتق المحلي (RFC-14.4 / 6.4).
    G_F^prec = (U_F, C_F^prec)
    """
    occurrences: tuple[LinearizableOccurrence, ...]
    precedence_constraints: frozenset[tuple[str, str]] = field(default_factory=frozenset)  # (u_before_id, u_after_id)


@dataclass(frozen=True)
class LinearizationPrefix:
    """
    البادئة الخطية النحوية الملتزم بها مرحلياً بواسطة القانون 16 (RFC-14.4 / 6.5).
    """
    committed_occurrences: tuple[LinearizableOccurrence, ...]
    status: str  # "LINEARIZED", "PARTIAL", "LINEARIZATION_AMBIGUOUS", "ORDER_CONFLICT"
    remaining_uncommitted_ids: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class LexicalCandidate:
    """
    مرشح معجمي محلي مستخرج من علاقات المعجم الموروثة (RFC-14.5).
    """
    occurrence_id: str
    lexeme: str
    language_context: str
    morphosyntactic_features: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SurfaceBundle:
    """
    حزمة سطحية مشتقة لكل ظهور خطي (RFC-14.5 / 7.5).
    SB(u) = <SourceOccurrenceRef, LexicalFormRefs, SupportFormRefs, InternalOrderView>
    """
    source_occurrence_ref: str
    lexical_form_refs: tuple[str, ...]
    support_form_refs: tuple[str, ...] = field(default_factory=tuple)
    internal_order_view: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SourceAlignment:
    """
    محاذاة المصدر لكل وحدة سطحية منجزة لضمان عدم وجود وحدات شبحية (RFC-14.6 / 8.3).
    """
    surface_unit_id: str
    source_occurrence_ref: str | None = None
    grammatical_authority_ref: str | None = None


@dataclass(frozen=True)
class SurfaceUnit:
    """
    وحدة سطحية منجزة صوتياً أو نصياً (RFC-14.5 / 7.4).
    """
    unit_id: str
    surface_form: str
    source_alignment: SourceAlignment
    origin_lineage: str = "GENERATION"


@dataclass(frozen=True)
class SurfaceChunk:
    """
    قطعة سطحية منجزة لغوياً ذات حدود انبعاث قانونية (RFC-14.6 / 8.2).
    """
    chunk_id: str
    parent_representation_id: str
    surface_units: tuple[SurfaceUnit, ...]
    rendered_text: str
    closure_reason: str
    origin_lineage: str = "GENERATION"


@dataclass(frozen=True)
class ResidualView:
    """
    منظور المتبقي التوليدي المؤقت لتسليمه إلى RFC-15 (RFC-14.6 / 8.5).
    """
    parent_representation_id: str
    unconsumed_occurrences: tuple[LinearizableOccurrence, ...]
    unresolved_order_conflicts: tuple[str, ...] = field(default_factory=tuple)
    unresolved_lexical_blockers: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class HandoffView:
    """
    واجهة التسليم المرجعية من RFC-14 إلى RFC-15 (RFC-14.6 / 8.5).
    H_14->15 = <ParentRID, SurfaceChunkView, ResidualView, ClosureReason>
    """
    parent_representation_id: str
    surface_chunk_view: SurfaceChunk
    residual_view: ResidualView
    closure_reason: str


@dataclass
class GenerationObservability:
    """
    إحصائيات ومقاييس تشغيلية ورصد للأداء التشغيلي لمحرك التوليد.
    """
    frames_built: int = 0
    expansions_evaluated: int = 0
    linearization_steps: int = 0
    surface_units_emitted: int = 0
    ambiguity_events: int = 0
    order_conflicts: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


# ─────────────────────────────────────────────────────────── 2. Engine Implementation
class HierarchicalGenerativeEngine:
    """
    محرك الديناميكيات التوليدية الهرمية والتحويل التسلسلي النحوي والقانون 16 (RFC-14).
    """

    def __init__(self, graph: CognitiveGraph) -> None:
        self._graph = graph
        self._frame_cache: dict[str, GenerativeFrame] = {}
        self._precedence_cache: dict[str, PrecedenceGraph] = {}
        self._lexical_cache: dict[str, list[LexicalCandidate]] = {}
        self.observability = GenerationObservability()

    def clear_caches(self) -> None:
        """مسح الذاكرة المؤقتة الشفافة دون أي أثر دلالي."""
        self._frame_cache.clear()
        self._precedence_cache.clear()
        self._lexical_cache.clear()

    def get_memory_snapshot_ref(self) -> str:
        """حساب البصمة المعيارية للحالة المعرفية والبنيوية الدائمة الحالية."""
        h = hashlib.sha256()
        for (u, v), e in sorted(self._graph.edges.items()):
            ctxs = ",".join(sorted(e.contexts))
            h.update(f"e:{u}->{v}|W={e.W:.4f}|g={e.g}|k={e.kind}|c=[{ctxs}]\n".encode())
        for nid, n in sorted(self._graph.nodes.items()):
            h.update(f"n:{nid}|r={n.region}|c={int(n.is_concept)}|i={int(n.is_intrinsic)}\n".encode())
        for k, v in sorted(self._graph.X.items()):
            h.update(f"X:{k}={','.join(sorted(v))}\n".encode())
        if hasattr(self._graph, "_assembly_manager") and self._graph._assembly_manager is not None:
            mgr = self._graph.assembly_manager
            for aid, versions in sorted(mgr.assemblies.items()):
                latest = versions[-1]
                h.update(f"asm:{aid}|v={latest.version}|m={len(latest.member_edges)}|r={int(latest.is_retired)}\n".encode())
        return h.hexdigest()[:16]

    # ─────────────────────────────────────────────────────── RFC-14.2: GenerativeFrame Construction & Validation
    def build_generative_frame(
        self,
        representation: SparseDistributedCognitiveRepresentation,
        anchor_refs: frozenset[str],
        role_bindings: tuple[RoleBinding, ...] = (),
        scope_view: tuple[str, ...] | None = None,
    ) -> GenerativeFrame:
        """
        بناء إطار توليدي مرجعي مؤقت مرتبط بالتمثيل المعرفي الحالي (RFC-14.2).
        """
        if not anchor_refs:
            raise ValueError("anchor_refs cannot be empty")

        # التحقق من أن جميع المراسي موجودة وقانونية في التمثيل الحالي
        active_nodes = set(representation.participating_node_refs)
        for anchor in anchor_refs:
            if anchor not in active_nodes and anchor not in self._graph.nodes:
                raise ValueError(f"Anchor reference {anchor} is not a current lawful cognitive reference")

        # التحقق من الروابط الدلالية
        for b in role_bindings:
            if not b.role_authority_ref:
                raise ValueError("RoleBinding role_authority_ref cannot be empty")
            if not b.filler_ref:
                raise ValueError("RoleBinding filler_ref cannot be empty")

        # اشتقاق معرف تشغيلي فريد وحتمي
        scope = scope_view or ()
        anchor_sig = "_".join(sorted(anchor_refs))
        scope_sig = "_".join(sorted(scope))
        bindings_sig = "_".join(f"{b.role_authority_ref}:{b.filler_ref}" for b in sorted(role_bindings, key=lambda x: (x.role_authority_ref, x.filler_ref)))
        raw_sig = f"{representation.representation_id}|{anchor_sig}|{scope_sig}|{bindings_sig}"
        fid = f"frame_{hashlib.sha256(raw_sig.encode()).hexdigest()[:12]}"

        frame = GenerativeFrame(
            frame_id=fid,
            parent_representation_id=representation.representation_id,
            scope_view=scope,
            anchor_refs=anchor_refs,
            role_bindings=role_bindings,
        )
        self.observability.frames_built += 1
        return frame

    def validate_generative_frame(
        self,
        frame: GenerativeFrame,
        representation: SparseDistributedCognitiveRepresentation,
    ) -> bool:
        """
        التحقق من صحة الإطار التوليدي وعدم تقادمه مع التمثيل الحالي (RFC-14.2 / 9.4).
        """
        if frame.parent_representation_id != representation.representation_id:
            return False
        active_nodes = set(representation.participating_node_refs)
        for anchor in frame.anchor_refs:
            if anchor not in active_nodes and anchor not in self._graph.nodes:
                return False
        return True

    def build_hierarchy(self, frames: list[GenerativeFrame]) -> GenerativeHierarchy:
        """
        تكوين منظور هرمي مشتق متماسك ولاحلقي من قائمة الإطارات (RFC-14.2 / 4.3).
        """
        frame_dict = {f.frame_id: f for f in frames}
        child_to_parent: dict[str, str] = {}
        referenced_children: set[str] = set()

        for parent in frames:
            for b in parent.role_bindings:
                if b.filler_ref in frame_dict:
                    child_id = b.filler_ref
                    if child_id in child_to_parent and child_to_parent[child_id] != parent.frame_id:
                        # في النسخة v1 كل إطار ابن له أب واحد كحد أقصى
                        pass
                    child_to_parent[child_id] = parent.frame_id
                    referenced_children.add(child_id)

        # فحص اللا دورية (Acyclicity)
        is_acyclic = True
        for fid in frame_dict:
            visited = set()
            curr = fid
            while curr in child_to_parent:
                if curr in visited:
                    is_acyclic = False
                    break
                visited.add(curr)
                curr = child_to_parent[curr]
            if not is_acyclic:
                break

        # تحديد الجذور (الإطارات التي ليس لها أب)
        roots = tuple(f.frame_id for f in frames if f.frame_id not in referenced_children)
        return GenerativeHierarchy(
            root_frame_ids=roots,
            frames=frame_dict,
            child_to_parent=child_to_parent,
            is_acyclic=is_acyclic,
        )

    # ─────────────────────────────────────────────────────── RFC-14.3: Task-Scoped Local Expansion
    def derive_expansion_frontier(
        self,
        hierarchy: GenerativeHierarchy,
        representation: SparseDistributedCognitiveRepresentation,
        generation_scope: GenerationScope | None = None,
    ) -> GenerativeExpansionFrontier:
        """
        اشتقاق جبهة التوسع التوليدي المحلي المقيدة بالنطاق الحالي دون أي مسح شامل (RFC-14.3).
        """
        active_nodes = set(representation.participating_node_refs)
        options: list[ExpansionOption] = []
        seen_options: set[tuple[str, str, str]] = set()

        for fid, frame in hierarchy.frames.items():
            # فحص الروابط الحالية
            existing_fillers = {b.filler_ref for b in frame.role_bindings}

            # البحث عن الجيران النشطين محلياً فقط المتصلين بمراسي الإطار عبر out_adj
            for anchor in frame.anchor_refs:
                incident_edges = self._graph.out_adj.get(anchor, {})
                if len(incident_edges) <= len(active_nodes):
                    candidate_pairs = [
                        (v, edge) for v, edge in incident_edges.items()
                        if v in active_nodes and v not in existing_fillers
                    ]
                else:
                    candidate_pairs = [
                        (v, incident_edges[v]) for v in active_nodes
                        if v in incident_edges and v not in existing_fillers
                    ]

                for v, edge in candidate_pairs:
                    # فحص توافق الحواف وسياق النطاق
                    role_auth = edge.kind or "attribute"
                    if generation_scope and generation_scope.permitted_roles and role_auth not in generation_scope.permitted_roles:
                        continue

                    opt_key = (fid, role_auth, v)
                    if opt_key not in seen_options:
                        seen_options.add(opt_key)
                        options.append(
                            ExpansionOption(
                                frame_id=fid,
                                role_authority_ref=role_auth,
                                filler_ref=v,
                                is_child_frame=False,
                            )
                        )

        self.observability.expansions_evaluated += len(options)
        return GenerativeExpansionFrontier(options=tuple(options))

    def expand_hierarchy(
        self,
        hierarchy: GenerativeHierarchy,
        representation: SparseDistributedCognitiveRepresentation,
        generation_scope: GenerationScope | None = None,
        budget: float = 1.0,
    ) -> tuple[GenerativeHierarchy, float]:
        """
        توسيع الهرمية التوليدية تزايدياً في حدود الميزانية الموروثة المحدودة (RFC-14.3 / 5.5).
        """
        remaining_budget = budget
        step_cost = Law.GAMMA  # 0.20 per expansion step

        frontier = self.derive_expansion_frontier(hierarchy, representation, generation_scope)
        if not frontier.options or remaining_budget < step_cost:
            return hierarchy, 0.0

        new_frames = dict(hierarchy.frames)
        for opt in frontier.options:
            if remaining_budget < step_cost:
                break
            if opt.frame_id in new_frames:
                target_frame = new_frames[opt.frame_id]
                new_binding = RoleBinding(
                    role_authority_ref=opt.role_authority_ref,
                    filler_ref=opt.filler_ref,
                )
                updated_bindings = target_frame.role_bindings + (new_binding,)
                new_frames[opt.frame_id] = dataclasses.replace(
                    target_frame,
                    role_bindings=updated_bindings,
                )
                remaining_budget -= step_cost

        consumed = budget - remaining_budget
        expanded_hierarchy = self.build_hierarchy(list(new_frames.values()))
        return expanded_hierarchy, consumed

    # ─────────────────────────────────────────────────────── RFC-14.4 & LAW 16: Syntactic Ordering & Linearization
    def build_precedence_graph(
        self,
        hierarchy: GenerativeHierarchy,
        language_context: str = "en",
    ) -> PrecedenceGraph:
        """
        بناء مخطط الأسبقية النحوية المحلي من علاقات الترتيب الموروثة في Edge cognition (RFC-14.4 / 6.4).
        """
        occurrences: list[LinearizableOccurrence] = []
        occ_by_frame_and_filler: dict[tuple[str, str], str] = {}

        # 1. استخراج جميع الظهورات الخطية من الإطارات
        for fid, frame in sorted(hierarchy.frames.items()):
            # مرساة الإطار كظهور أساسي
            for anchor in sorted(frame.anchor_refs):
                occ_id = f"occ_{fid}_anchor_{anchor}"
                occ = LinearizableOccurrence(
                    occurrence_id=occ_id,
                    frame_id=fid,
                    role_authority_ref="anchor",
                    filler_ref=anchor,
                    is_child_frame=False,
                    scope_view=frame.scope_view,
                )
                occurrences.append(occ)
                occ_by_frame_and_filler[(fid, anchor)] = occ_id

            # الأدوار التابعة
            for b in sorted(frame.role_bindings, key=lambda x: (x.role_authority_ref, x.filler_ref)):
                is_child = b.filler_ref in hierarchy.frames
                occ_id = f"occ_{fid}_{b.role_authority_ref}_{b.filler_ref}"
                occ = LinearizableOccurrence(
                    occurrence_id=occ_id,
                    frame_id=fid,
                    role_authority_ref=b.role_authority_ref,
                    filler_ref=b.filler_ref,
                    is_child_frame=is_child,
                    scope_view=frame.scope_view,
                )
                occurrences.append(occ)
                occ_by_frame_and_filler[(fid, b.filler_ref)] = occ_id

        # 2. استخراج قيود الأسبقية النحوية من الحواف المعرفية الحالية فقط
        precedence_constraints: set[tuple[str, str]] = set()

        for occ_u in occurrences:
            for occ_v in occurrences:
                if occ_u.occurrence_id == occ_v.occurrence_id:
                    continue

                # فحص الحواف المتجهة بين الملاّت (fillers)
                u_ref, v_ref = occ_u.filler_ref, occ_v.filler_ref
                edge_uv = self._graph.edges.get((u_ref, v_ref))
                if edge_uv is not None and (not edge_uv.contexts or language_context in edge_uv.contexts or "global" in edge_uv.contexts):
                    # الحافة تشير إلى أسبقية u قبل v
                    precedence_constraints.add((occ_u.occurrence_id, occ_v.occurrence_id))

                # الأنماط النحوية الموروثة: المرساة تسبق توابعها في نفس الإطار افتراضياً إذا لم يوجد ترتيب معاكس
                if occ_u.frame_id == occ_v.frame_id and (occ_u.role_authority_ref == "anchor" and occ_v.role_authority_ref != "anchor"):
                    # قيود الأسبقية اللغوية المحددة (مثال: الإنجليزية SVO أو العربية VSO)
                    if language_context == "ar" and occ_v.role_authority_ref in ("verb", "predicate"):
                        # في العربية الفعل يسبق الفاعل
                        precedence_constraints.add((occ_v.occurrence_id, occ_u.occurrence_id))
                    else:
                        precedence_constraints.add((occ_u.occurrence_id, occ_v.occurrence_id))

        return PrecedenceGraph(
            occurrences=tuple(occurrences),
            precedence_constraints=frozenset(precedence_constraints),
        )

    def compute_ready_frontier(
        self,
        precedence_graph: PrecedenceGraph,
        committed_ids: set[str],
        in_preds_map: dict[str, set[str]] | None = None,
    ) -> list[LinearizableOccurrence]:
        """
        حساب جبهة الجاهزية النحوية وفق القانون 16 (RFC-14.4 / Section 10).
        Ready_k = { u in U_H \\ committed : Pred(u) subset_of committed }
        """
        if in_preds_map is None:
            in_preds_map = {}
            for u_before, u_after in precedence_graph.precedence_constraints:
                in_preds_map.setdefault(u_after, set()).add(u_before)

        ready: list[LinearizableOccurrence] = []
        for occ in precedence_graph.occurrences:
            if occ.occurrence_id in committed_ids:
                continue

            # استخراج جميع الأسلاف المطلوبين
            predecessors = in_preds_map.get(occ.occurrence_id)

            # الظهور جاهز إذا وفقط إذا كانت جميع الأسلاف قد تم الالتزام بها سابقاً
            if predecessors is None or predecessors.issubset(committed_ids):
                ready.append(occ)

        # ترتيب الحاويات حتمياً للتشغيل دون أي تفضيل دلالي
        ready.sort(key=lambda x: x.occurrence_id)
        return ready

    def linearize_hierarchy(
        self,
        hierarchy: GenerativeHierarchy,
        language_context: str = "en",
        budget: float = 1.0,
    ) -> tuple[LinearizationPrefix, float]:
        """
        تنفيذ القانون 16: التحويل التسلسلي الهرمي المحدود والالتزام النحوي المحلي (Law 16 v1.0).
        """
        prec_graph = self.build_precedence_graph(hierarchy, language_context)
        in_preds_map: dict[str, set[str]] = {}
        for u_before, u_after in prec_graph.precedence_constraints:
            in_preds_map.setdefault(u_after, set()).add(u_before)

        committed_occurrences: list[LinearizableOccurrence] = []
        committed_ids: set[str] = set()
        all_occurrence_ids = {occ.occurrence_id for occ in prec_graph.occurrences}

        remaining_budget = budget
        step_cost = Law.GAMMA

        status = "LINEARIZED"

        while len(committed_ids) < len(all_occurrence_ids):
            if remaining_budget < step_cost:
                status = "PARTIAL"
                break

            ready = self.compute_ready_frontier(prec_graph, committed_ids, in_preds_map)
            if not ready:
                # توجد عناصر متبقية لكن جبهة الجاهزية فارغة => تعارض أسبقية أو دورة (Order Conflict)
                status = "ORDER_CONFLICT"
                self.observability.order_conflicts += 1
                break

            if len(ready) > 1:
                # بدائل جاهزة متعددة قانونية بلا قيد أسبقية حاسم => الحفاظ على الغموض والإغلاق بـ LINEARIZATION_AMBIGUOUS
                status = "LINEARIZATION_AMBIGUOUS"
                self.observability.ambiguity_events += 1
                break

            # الالتزام بالوحدة الوحيدة الجاهزة قانونياً
            next_occ = ready[0]
            committed_occurrences.append(next_occ)
            committed_ids.add(next_occ.occurrence_id)
            remaining_budget -= step_cost
            self.observability.linearization_steps += 1

        uncommitted_remaining = frozenset(all_occurrence_ids - committed_ids)
        if not uncommitted_remaining and status == "LINEARIZED":
            status = "LINEARIZED"
        elif uncommitted_remaining and status not in ("ORDER_CONFLICT", "PARTIAL"):
            status = "LINEARIZATION_AMBIGUOUS"

        prefix = LinearizationPrefix(
            committed_occurrences=tuple(committed_occurrences),
            status=status,
            remaining_uncommitted_ids=uncommitted_remaining,
        )
        consumed = budget - remaining_budget
        return prefix, consumed

    # ─────────────────────────────────────────────────────── RFC-14.5: Lexicalization, Morphology & Surface Realization
    def resolve_lexical_candidates(
        self,
        occurrence: LinearizableOccurrence,
        language_context: str = "en",
    ) -> list[LexicalCandidate]:
        """
        استخراج المرشحات المعجمية المحلية المرتبطة بالظهور وسياق اللغة (RFC-14.5 / 7.1).
        Concept != Lexeme != InflectedSurfaceForm
        """
        cache_key = f"{occurrence.filler_ref}|{language_context}"
        if cache_key in self._lexical_cache:
            self.observability.cache_hits += 1
            return self._lexical_cache[cache_key]
        self.observability.cache_misses += 1

        raw_filler = occurrence.filler_ref
        lexeme = raw_filler.split(":")[-1] if ":" in raw_filler else raw_filler

        # التحويل المعجمي حسب سياق اللغة
        candidates: list[LexicalCandidate] = []

        # استخراج الترجمة أو الصيغة المعجمية من الحواف المعرفية المحلية عبر out_adj
        incident_edges = self._graph.out_adj.get(raw_filler, {})
        for v, edge in incident_edges.items():
            if (edge.kind == "translation" or "lexical" in edge.contexts) and (not edge.contexts or language_context in edge.contexts):
                v_clean = v.split(":")[-1] if ":" in v else v
                candidates.append(
                    LexicalCandidate(
                        occurrence_id=occurrence.occurrence_id,
                        lexeme=v_clean,
                        language_context=language_context,
                    )
                )

        if not candidates:
            # استخدام المعجم الافتراضي المباشر من المسمى النظيف
            candidates.append(
                LexicalCandidate(
                    occurrence_id=occurrence.occurrence_id,
                    lexeme=lexeme,
                    language_context=language_context,
                )
            )

        self._lexical_cache[cache_key] = candidates
        return candidates

    def build_surface_bundle(
        self,
        occurrence: LinearizableOccurrence,
        language_context: str = "en",
    ) -> SurfaceBundle:
        """
        بناء الحزمة السطحية للظهور مع مراعاة صيغ الدعم النحوي (RFC-14.5 / 7.5).
        """
        lex_cands = self.resolve_lexical_candidates(occurrence, language_context)
        selected_lexeme = lex_cands[0].lexeme if lex_cands else occurrence.filler_ref

        support_forms: list[str] = []

        # إضافة أدوات الدعم النحوي القانونية فقط عند وجود سلطة صريحة
        if occurrence.role_authority_ref in ("predicate", "attribute") and language_context == "en":
            # صيغة الرابطة الإنجليزية المشتقة من علاقة إسنادية
            pass

        return SurfaceBundle(
            source_occurrence_ref=occurrence.occurrence_id,
            lexical_form_refs=(selected_lexeme,),
            support_form_refs=tuple(support_forms),
            internal_order_view=(selected_lexeme,),
        )

    def realize_surface_chunk(
        self,
        prefix: LinearizationPrefix,
        parent_representation_id: str,
        language_context: str = "en",
        budget: float = 1.0,
    ) -> SurfaceChunk:
        """
        تحقيق القطعة السطحية الكاملة وتأكيد نسب التوليد (RFC-14.5 / RFC-14.6).
        """
        surface_units: list[SurfaceUnit] = []
        rendered_words: list[str] = []

        for i, occ in enumerate(prefix.committed_occurrences):
            bundle = self.build_surface_bundle(occ, language_context)
            for form in bundle.internal_order_view:
                unit_id = f"su_{parent_representation_id[:8]}_{i}_{form}"
                alignment = SourceAlignment(
                    surface_unit_id=unit_id,
                    source_occurrence_ref=occ.occurrence_id,
                    grammatical_authority_ref=occ.role_authority_ref,
                )
                unit = SurfaceUnit(
                    unit_id=unit_id,
                    surface_form=form,
                    source_alignment=alignment,
                    origin_lineage="GENERATION",
                )
                surface_units.append(unit)
                rendered_words.append(form)
                self.observability.surface_units_emitted += 1

        # تحديد علة الإغلاق
        if prefix.status == "LINEARIZED":
            closure_reason = "COMPLETE"
        elif prefix.status == "ORDER_CONFLICT":
            closure_reason = "CONFLICT"
        elif prefix.status == "LINEARIZATION_AMBIGUOUS":
            closure_reason = "AMBIGUOUS"
        else:
            closure_reason = "PARTIAL_BUDGET"

        rendered_text = " ".join(rendered_words)
        chunk_id = f"chunk_{hashlib.sha256((parent_representation_id + rendered_text).encode()).hexdigest()[:12]}"

        return SurfaceChunk(
            chunk_id=chunk_id,
            parent_representation_id=parent_representation_id,
            surface_units=tuple(surface_units),
            rendered_text=rendered_text,
            closure_reason=closure_reason,
            origin_lineage="GENERATION",
        )

    # ─────────────────────────────────────────────────────── RFC-14.6: Bounded Generative Execution & Handoff
    def execute_generative_pass(
        self,
        representation: SparseDistributedCognitiveRepresentation,
        anchor_refs: frozenset[str],
        generation_scope: GenerationScope | None = None,
        language_context: str = "en",
        budget: float = 1.0,
    ) -> HandoffView:
        """
        تنفيذ مسار التوليد غير التكراري المحدود وإصدار وثيقة التسليم إلى RFC-15 (RFC-14.6).
        G14(R_t, Q_G, C_L, B_0) -> <SurfaceChunk, HandoffView, ClosureReason>
        """
        # 1. التحقق من سلامة التمثيل المعرفي الحالي
        active_nodes = set(representation.participating_node_refs)
        valid_anchors = frozenset(a for a in anchor_refs if a in active_nodes or a in self._graph.nodes)

        if not valid_anchors:
            empty_chunk = SurfaceChunk(
                chunk_id="chunk_empty_invalid",
                parent_representation_id=representation.representation_id,
                surface_units=(),
                rendered_text="",
                closure_reason="UNDERSPECIFIED",
                origin_lineage="GENERATION",
            )
            empty_residual = ResidualView(
                parent_representation_id=representation.representation_id,
                unconsumed_occurrences=(),
            )
            return HandoffView(
                parent_representation_id=representation.representation_id,
                surface_chunk_view=empty_chunk,
                residual_view=empty_residual,
                closure_reason="UNDERSPECIFIED",
            )

        # 2. بناء الإطار المرجعي الأولي
        base_frame = self.build_generative_frame(
            representation=representation,
            anchor_refs=valid_anchors,
        )
        hierarchy = self.build_hierarchy([base_frame])

        # 3. توسيع الإطار محلياً في حدود النطاق والميزانية
        expanded_hierarchy, exp_cost = self.expand_hierarchy(
            hierarchy=hierarchy,
            representation=representation,
            generation_scope=generation_scope,
            budget=budget * 0.4,  # تخصيص جزء من الميزانية الموروثة للتوسع
        )

        # 4. تحويل الهرمية تسلسلياً بواسطة القانون 16
        lin_budget = budget - exp_cost
        prefix, _ = self.linearize_hierarchy(
            hierarchy=expanded_hierarchy,
            language_context=language_context,
            budget=lin_budget,
        )

        # 5. تحقيق القطعة السطحية
        chunk = self.realize_surface_chunk(
            prefix=prefix,
            parent_representation_id=representation.representation_id,
            language_context=language_context,
            budget=budget,
        )

        # 6. إعداد منظور المتبقي والتسليم
        all_prec = self.build_precedence_graph(expanded_hierarchy, language_context)
        committed_set = {occ.occurrence_id for occ in prefix.committed_occurrences}
        unconsumed = tuple(occ for occ in all_prec.occurrences if occ.occurrence_id not in committed_set)

        residual = ResidualView(
            parent_representation_id=representation.representation_id,
            unconsumed_occurrences=unconsumed,
        )

        return HandoffView(
            parent_representation_id=representation.representation_id,
            surface_chunk_view=chunk,
            residual_view=residual,
            closure_reason=chunk.closure_reason,
        )


# ─────────────────────────────────────────────────────────── 3. Deterministic Replay Signature
def rfc14_behavioral_signature(engine: HierarchicalGenerativeEngine) -> str:
    """
    حساب البصمة السلوكية الحتمية المعيارية لتنفيذ التوليد الهرمي والقانون 16 (RFC-14).
    """
    g = engine._graph
    # إعداد سيناريو توليدي معياري
    g.link("concept_cat", "furry", W=0.85, contexts=("en",))
    g.link("concept_cat", "meow", W=0.85, contexts=("en",))

    from .representation import ParticipationReceipt

    receipts = [
        ParticipationReceipt(
            receipt_id="r_cat_0",
            element_ref="concept_cat",
            parent_cycle_id=1,
            snapshot_or_microtick=0,
            origin_lineage="external",
            participation_kind="node",
            activation_magnitude=0.90,
        )
    ]
    rep = g.representation_engine.build_representation(1, 0, None, receipts)

    handoff = engine.execute_generative_pass(
        representation=rep,
        anchor_refs=frozenset(["concept_cat"]),
        language_context="en",
        budget=1.0,
    )

    rows = [
        f"chunk:{handoff.surface_chunk_view.rendered_text}",
        f"closure:{handoff.closure_reason}",
        f"units:{len(handoff.surface_chunk_view.surface_units)}",
        f"residual:{len(handoff.residual_view.unconsumed_occurrences)}",
    ]
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()[:16]
