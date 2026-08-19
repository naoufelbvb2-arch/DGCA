"""
DGCA — RFC-12 v1.0: Sparse Distributed Cognitive Representation (SDCR) & Transient Binding Receipts (TBR).

Constitutional ownership hierarchy:
- Node: Transient Operational Unit
- Edge: Persistent Cognitive Memory Owner
- StructuralAssembly: Persistent Structural Organization Owner
- ActiveAssembly: Transient Working Organization
- SDCR: Transient Distributed Representation State
- PersistentCognition(RFC-12) = ∅
- Law 15 is explicitly NOT introduced.
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from typing import Any

from .graph import CognitiveGraph


# ─────────────────────────────────────────────────────────── 1. الإيصالات التشغيلية (Receipts)
@dataclass(frozen=True)
class ParticipationReceipt:
    """إيصال مشاركة تشغيلي مؤقت لعنصر (عقدة أو رابط) في دورة إدراكية محددة."""

    receipt_id: str
    element_ref: str | tuple[str, str]
    parent_cycle_id: int
    snapshot_or_microtick: int
    origin_lineage: str = "external"  # external | recall | reasoning | prediction | simulation | generation
    participation_kind: str = "node"  # node | edge
    scope_refs: tuple[str, ...] = ()
    relational_drive: float = 0.0  # D_e* للرابط من مسار الانتقال
    activation_magnitude: float = 0.0  # A_u* للعقدة
    created_t: int = 0

    def __post_init__(self) -> None:
        # منع الحقول المعرفية المكتسبة المحرمة
        forbidden = {
            "weight", "salience", "confidence", "truth", "belief", "score",
            "learned_importance", "embedding", "vector"
        }
        for attr in forbidden:
            if hasattr(self, attr):
                raise ValueError(f"Forbidden cognitive attribute '{attr}' on ParticipationReceipt.")


@dataclass(frozen=True)
class TransientBindingReceipt:
    """
    إيصال الربط المؤقت (TBR).
    Primitive تشغيلية مؤقتة محصورة في النطاق واللقطة لربط التراكيب المستجدة
    دون إنشاء روابط معرفية دائمة أو تنشيط أو تصويت بنيوي.
    """

    binding_id: str
    parent_snapshot_ref: tuple[int, int]  # (parent_cycle_id, snapshot_or_microtick)
    binding_scope_id: str
    member_receipt_refs: tuple[str | tuple[str, str], ...]
    origin_view: str = "external"
    created_t: int = 0

    def __post_init__(self) -> None:
        # التحقق الدستوري الصارم لـ TBR (RFC-12 Section 6.3)
        forbidden = {
            "conductance", "weight", "propagation", "salience", "confidence",
            "energy", "score", "learned_strength"
        }
        for attr in forbidden:
            if hasattr(self, attr):
                raise ValueError(f"Forbidden attribute '{attr}' on TransientBindingReceipt (TBR).")


# ─────────────────────────────────────────────────────────── 2. التمثيل المعرفي الموزع المتناثر (SDCR)
@dataclass
class SparseDistributedCognitiveRepresentation:
    """
    التمثيل المعرفي الموزع المتناثر (SDCR) — R_t.
    الحالة التشغيلية المؤقتة والمحدودة محلياً للتعبير المعرفي الموزع الحالي.
    R_t = < RID_t, P_t, C_t, A_t, V_t, E_t, B_t, Pi_t, Status_t >
    """

    representation_id: str  # معرف تشغيلي فقط (Operational RID != Semantic Identity)
    parent_cycle_id: int
    snapshot_or_microtick: int
    context_binding_ref: str | None = None
    active_assembly_refs: frozenset[tuple[str, int]] = frozenset()  # (assembly_id, pinned_version)
    participating_node_refs: frozenset[str] = frozenset()
    participating_edge_refs: frozenset[tuple[str, str]] = frozenset()
    transient_binding_receipts: tuple[TransientBindingReceipt, ...] = ()
    participation_receipts: tuple[ParticipationReceipt, ...] = ()
    status: str = "ACTIVE"  # ACTIVE -> CLOSED

    def __post_init__(self) -> None:
        # منع أي حقول معرفية مكتسبة أو متجهات كثيفة
        forbidden = {
            "weight", "salience", "confidence", "truth", "belief", "score",
            "learned_vector", "embedding", "frequency", "long_term_memory"
        }
        for attr in forbidden:
            if hasattr(self, attr):
                raise ValueError(f"Forbidden persistent cognitive attribute '{attr}' on SDCR.")

    def close(self) -> None:
        """إغلاق التمثيل المعرفي الحالي ليصبح غير قابل للتعديل تماماً."""
        self.status = "CLOSED"


# ─────────────────────────────────────────────────────────── 3. الرؤى المشتقة (Derived Views)
@dataclass(frozen=True)
class ContextualFacetView:
    """رؤية وجهية سياقية مشتقة لمرجع معرفي محدد داخل التمثيل الحالي."""

    referent_id: str
    context: str | None
    participating_nodes: frozenset[str]
    participating_edges: frozenset[tuple[str, str]]
    active_assemblies: frozenset[tuple[str, int]]
    binding_scopes: tuple[str, ...]
    node_supports: dict[str, float]
    edge_supports: dict[tuple[str, str], float]


@dataclass(frozen=True)
class ScopeView:
    """رؤية مشتقة لنطاق تجميعي محدد (Scope View)."""

    scope_id: str
    member_elements: tuple[str | tuple[str, str], ...]
    binding_receipt: TransientBindingReceipt | None
    coherence_component_index: int | None


# ─────────────────────────────────────────────────────────── 4. واجهة القراءة البحتة (RepresentationView)
class RepresentationView:
    """
    واجهة قراءة بحتة (Pure Read-Only Projection) لتمثيل معرفي محدد.
    لا تستطيع تعديل الحالة المعرفية ولا تنفيذ استكشاف كلي للرسم البياني ولا إحداث تنشيط.
    """

    def __init__(self, representation: SparseDistributedCognitiveRepresentation, engine: RepresentationEngine) -> None:
        self._rep = representation
        self._engine = engine

    @property
    def representation_id(self) -> str:
        return self._rep.representation_id

    @property
    def parent_cycle(self) -> int:
        return self._rep.parent_cycle_id

    @property
    def microtick(self) -> int:
        return self._rep.snapshot_or_microtick

    @property
    def context(self) -> str | None:
        return self._rep.context_binding_ref

    @property
    def status(self) -> str:
        return self._rep.status

    def participating_nodes(self) -> frozenset[str]:
        return self._rep.participating_node_refs

    def participating_edges(self) -> frozenset[tuple[str, str]]:
        return self._rep.participating_edge_refs

    def active_assemblies(self) -> frozenset[tuple[str, int]]:
        return self._rep.active_assembly_refs

    def binding_receipts(self) -> tuple[TransientBindingReceipt, ...]:
        return self._rep.transient_binding_receipts

    def participation_receipts(self) -> tuple[ParticipationReceipt, ...]:
        return self._rep.participation_receipts

    def coherence_components(self) -> list[frozenset[str]]:
        return self._engine.get_coherence_components(self._rep)

    def node_support(self, node_id: str) -> float:
        return self._engine.compute_node_support(self._rep, node_id)

    def edge_support(self, edge: tuple[str, str]) -> float:
        return self._engine.compute_edge_support(self._rep, edge)

    def typed_support_map(self) -> dict[str, Any]:
        return self._engine.compute_typed_support_map(self._rep)

    def referents(self) -> set[str]:
        return self._engine.get_referents(self._rep)

    def facet_view(self, referent_id: str) -> ContextualFacetView | None:
        return self._engine.get_contextual_facet(self._rep, referent_id)

    def scope_view(self, scope_id: str) -> ScopeView | None:
        return self._engine.get_scope_view(self._rep, scope_id)

    def provenance(self, element: str | tuple[str, str]) -> list[str]:
        return self._engine.get_element_provenance(self._rep, element)

    def canonical_signature(self) -> str:
        return self._engine.canonical_representation_signature(self._rep)

    def query(self, query_filter: dict[str, Any]) -> dict[str, Any]:
        """
        استعلام مقيد بالتمثيل الحالي فقط (Query-Scoped Readout).
        لا يقوم باكتشاف محتوى بعيد في الرسم البياني ولا ينفذ Softmax.
        """
        self._engine.observability.readout_queries += 1
        results: dict[str, Any] = {}

        # تصفية حسب العقد المشاركة
        if "node" in query_filter:
            target_n = query_filter["node"]
            if target_n in self._rep.participating_node_refs:
                results["node"] = target_n
                results["support"] = self.node_support(target_n)
                results["provenance"] = self.provenance(target_n)
            else:
                self._engine.observability.remote_scan_attempts_rejected += 1

        # تصفية حسب المرجع
        if "referent" in query_filter:
            target_ref = query_filter["referent"]
            facet = self.facet_view(target_ref)
            if facet:
                results["facet"] = facet

        # تصفية حسب النطاق
        if "scope" in query_filter:
            s_view = self.scope_view(query_filter["scope"])
            if s_view:
                results["scope"] = s_view

        # تصفية حسب أصل البيانات
        if "origin" in query_filter:
            req_origin = query_filter["origin"]
            matching_nodes = [
                r.element_ref for r in self._rep.participation_receipts
                if r.participation_kind == "node" and r.origin_lineage == req_origin
            ]
            results["matching_elements"] = matching_nodes

        return results


# ─────────────────────────────────────────────────────────── 5. عدادات المراقبة التشخيصية (Observability)
@dataclass
class RepresentationObservability:
    """عدادات مراقبة غير معرفية لتتبع أداء التمثيل وتدفق الإيصالات."""

    representations_created: int = 0
    representations_closed: int = 0
    participation_receipts_seen: int = 0
    participation_receipts_accepted: int = 0
    stale_receipts_rejected: int = 0
    cross_cycle_receipts_rejected: int = 0
    nodes_in_representation: int = 0
    edges_in_representation: int = 0
    residual_nodes: int = 0
    residual_edges: int = 0
    binding_receipts_seen: int = 0
    binding_receipts_accepted: int = 0
    binding_receipts_rejected: int = 0
    binding_members_processed: int = 0
    coherence_components_count: int = 0
    scope_mismatch_bridges_rejected: int = 0
    identity_unresolved_count: int = 0
    readout_queries: int = 0
    remote_scan_attempts_rejected: int = 0
    support_node_computations: int = 0
    support_edge_computations: int = 0
    cache_hits: int = 0
    cache_rebuilds: int = 0
    global_nodes_examined: int = 0
    global_edges_examined: int = 0


# ─────────────────────────────────────────────────────────── 6. محرك التمثيل المعرفي (RepresentationEngine)
class RepresentationEngine:
    """
    المحرك التشغيلي المسؤول عن بناء وإدارة التمثيلات المعرفية الموزعة المتناثرة (SDCR)
    وإيصالات الربط المؤقتة (TBR) والرؤى المشتقة دون أي حالة معرفية مكتسبة دائمة.
    """

    def __init__(self, graph: CognitiveGraph) -> None:
        self.graph = graph
        self.observability = RepresentationObservability()
        self.active_representations: dict[str, SparseDistributedCognitiveRepresentation] = {}
        self.closed_representations: dict[str, SparseDistributedCognitiveRepresentation] = {}

        # ذاكرة تخزين مؤقت قابلة لإعادة البناء بالكامل (Reconstructible Derived Caches)
        self._rcc_cache: dict[str, list[frozenset[str]]] = {}
        self._support_cache: dict[str, dict[str, Any]] = {}
        self._signature_cache: dict[str, str] = {}
        self.cache_enabled: bool = True

    def clear_caches(self) -> None:
        """مسح كافة ذواكر التخزين المؤقت لإثبات الشفافية الدلالية (P08)."""
        self._rcc_cache.clear()
        self._support_cache.clear()
        self._signature_cache.clear()
        self.observability.cache_rebuilds += 1

    # ── بناء التمثيل المعرفي من الإيصالات (Receipt-Driven Construction)
    def build_representation(
        self,
        parent_cycle_id: int,
        snapshot_or_microtick: int,
        context: str | None,
        participation_receipts: list[ParticipationReceipt],
        transient_bindings: list[TransientBindingReceipt] | None = None,
        active_assemblies: set[tuple[str, int]] | None = None,
    ) -> SparseDistributedCognitiveRepresentation:
        """
        بناء تمثيل معرفي موزع متناثر انطلاقاً من إيصالات المشاركة والربط الحالية حصراً.
        لا يقوم بمسح شامل للرسم البياني (Zero Global Scan).
        """
        self.observability.representations_created += 1
        valid_receipts: list[ParticipationReceipt] = []
        participating_nodes: set[str] = set()
        participating_edges: set[tuple[str, str]] = set()

        for r in participation_receipts:
            self.observability.participation_receipts_seen += 1

            # رفض الإيصالات المنتمية لدورة أو لقطة مختلفة (Fail-Closed Isolation)
            if r.parent_cycle_id != parent_cycle_id:
                self.observability.cross_cycle_receipts_rejected += 1
                continue
            if r.snapshot_or_microtick != snapshot_or_microtick:
                self.observability.stale_receipts_rejected += 1
                continue

            if r.participation_kind == "node":
                node_id = str(r.element_ref)
                node_obj = self.graph.nodes.get(node_id)
                # التحقق من وجود العقدة ونشاطها القانوني الحالي
                if (node_obj is not None and node_obj.A > 0.0) or r.activation_magnitude > 0.0:
                    participating_nodes.add(node_id)
                    valid_receipts.append(r)
                    self.observability.participation_receipts_accepted += 1
            elif r.participation_kind == "edge":
                edge_pair = tuple(r.element_ref)  # type: ignore
                edge_obj = self.graph.edge(edge_pair[0], edge_pair[1])
                # التحقق من قانونية الرابط وانفتاح بوابته في السياق الحالي
                if edge_obj is not None and edge_obj.gate_open(context):
                    participating_edges.add(edge_pair)
                    valid_receipts.append(r)
                    self.observability.participation_receipts_accepted += 1

        # التأكد من أن أطراف الروابط المشاركة تدخل ضمن العقد المشاركة (Endpoints Closure)
        for u, v in participating_edges:
            participating_nodes.add(u)
            participating_nodes.add(v)

        # معالجة إيصالات الربط المؤقتة (TBRs)
        valid_tbrs: list[TransientBindingReceipt] = []
        if transient_bindings:
            for tbr in transient_bindings:
                self.observability.binding_receipts_seen += 1
                # التحقق من تطابق اللقطة والنطاق
                if tbr.parent_snapshot_ref != (parent_cycle_id, snapshot_or_microtick):
                    self.observability.binding_receipts_rejected += 1
                    continue

                # التحقق من أن أعضاء الربط مشاركون فعلياً في اللقطة الحالية
                all_members_participating = True
                for member in tbr.member_receipt_refs:
                    self.observability.binding_members_processed += 1
                    if (
                        (isinstance(member, str) and member not in participating_nodes)
                        or (isinstance(member, tuple) and member not in participating_edges)
                    ):
                        all_members_participating = False
                        break

                if all_members_participating and tbr.binding_scope_id:
                    valid_tbrs.append(tbr)
                    self.observability.binding_receipts_accepted += 1
                else:
                    self.observability.binding_receipts_rejected += 1

        rep_id = f"rep_{uuid.uuid4().hex[:10]}"
        rep = SparseDistributedCognitiveRepresentation(
            representation_id=rep_id,
            parent_cycle_id=parent_cycle_id,
            snapshot_or_microtick=snapshot_or_microtick,
            context_binding_ref=context,
            active_assembly_refs=frozenset(active_assemblies or ()),
            participating_node_refs=frozenset(participating_nodes),
            participating_edge_refs=frozenset(participating_edges),
            transient_binding_receipts=tuple(valid_tbrs),
            participation_receipts=tuple(valid_receipts),
            status="ACTIVE",
        )

        self.active_representations[rep_id] = rep
        self.observability.nodes_in_representation += len(participating_nodes)
        self.observability.edges_in_representation += len(participating_edges)

        # حساب العقد والروابط المتبقية خارج التجمعات النشطة (Residual Activity)
        asm_nodes: set[str] = set()
        asm_edges: set[tuple[str, str]] = set()
        if self.graph._assembly_manager is not None:
            for aid, v_num in rep.active_assembly_refs:
                asm_obj = self.graph._assembly_manager.get_assembly(aid, v_num)
                if asm_obj:
                    asm_nodes.update(asm_obj.member_nodes)
                    asm_edges.update(asm_obj.member_edges)

        res_nodes = len(participating_nodes - asm_nodes)
        res_edges = len(participating_edges - asm_edges)
        self.observability.residual_nodes += res_nodes
        self.observability.residual_edges += res_edges

        return rep

    def close_representation(self, representation: SparseDistributedCognitiveRepresentation) -> None:
        """إغلاق تمثيل معرفي وجعله نهائياً غير قابل للتعديل."""
        representation.close()
        if representation.representation_id in self.active_representations:
            self.closed_representations[representation.representation_id] = representation
            del self.active_representations[representation.representation_id]
        self.observability.representations_closed += 1

    # ── حساب الدعم المعرفي المصنف المشتق (Derived Typed Support)
    def compute_node_support(self, rep: SparseDistributedCognitiveRepresentation, node_id: str) -> float:
        """
        حساب الدعم المعرفي للعقدة: s_V(u) = Norm_A(A_u*).
        قراءة بحتة مشتقة من حالة التنشيط القانونية الحالية.
        """
        if node_id not in rep.participating_node_refs:
            return 0.0
        self.observability.support_node_computations += 1

        # البحث في إيصالات المشاركة الحالية
        for r in rep.participation_receipts:
            if r.participation_kind == "node" and r.element_ref == node_id and r.activation_magnitude > 0.0:
                return min(1.0, max(0.0, r.activation_magnitude))

        node_obj = self.graph.nodes.get(node_id)
        if node_obj:
            return min(1.0, max(0.0, node_obj.A))
        return 0.0

    def compute_edge_support(self, rep: SparseDistributedCognitiveRepresentation, edge: tuple[str, str]) -> float:
        """
        حساب الدعم المعرفي للرابط: s_E(e) = 1 - e^(-D_e*).
        قراءة بحتة مشتقة من شدة الانتقال أو وزن الرابط القانوني في السياق الحالي.
        """
        if edge not in rep.participating_edge_refs:
            return 0.0
        self.observability.support_edge_computations += 1

        # البحث في إيصالات المشاركة
        d_val = 0.0
        for r in rep.participation_receipts:
            if r.participation_kind == "edge" and r.element_ref == edge and r.relational_drive > 0.0:
                d_val = r.relational_drive
                break

        if d_val <= 0.0:
            edge_obj = self.graph.edge(edge[0], edge[1])
            if edge_obj and edge_obj.gate_open(rep.context_binding_ref):
                d_val = edge_obj.W

        import math
        return 1.0 - math.exp(-d_val)

    def compute_typed_support_map(self, rep: SparseDistributedCognitiveRepresentation) -> dict[str, Any]:
        """توليد خارطة الدعم المعرفي المصنف لجميع عناصر التمثيل الحالي."""
        if self.cache_enabled and rep.representation_id in self._support_cache:
            self.observability.cache_hits += 1
            return self._support_cache[rep.representation_id]

        node_supports = {u: self.compute_node_support(rep, u) for u in sorted(rep.participating_node_refs)}
        edge_supports = {e: self.compute_edge_support(rep, e) for e in sorted(rep.participating_edge_refs)}

        support_map = {
            "node_supports": node_supports,
            "edge_supports": edge_supports,
        }
        if self.cache_enabled:
            self._support_cache[rep.representation_id] = support_map

        return support_map

    # ── استخراج مكونات التماسك التمثيلي (Representational Coherence Components - RCCs)
    def get_coherence_components(self, rep: SparseDistributedCognitiveRepresentation) -> list[frozenset[str]]:
        """
        بناء المكونات المتماسكة للتمثيل (RCCs) المشتقة محلياً عبر الاتحاد والتجزئة (Union-Find)
        فوق الرسم البياني الفائق للربط: H_R = (V_R, E_R, B_R) مع شرط توافق النطاقات.
        """
        if self.cache_enabled and rep.representation_id in self._rcc_cache:
            self.observability.cache_hits += 1
            return self._rcc_cache[rep.representation_id]

        parent: dict[str, str] = {u: u for u in rep.participating_node_refs}

        def find(u: str) -> str:
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        def union(u: str, v: str) -> None:
            root_u = find(u)
            root_v = find(v)
            if root_u != root_v:
                parent[root_v] = root_u

        # 1. روابط الرسم البياني المشاركة فعلياً (Participating Edges)
        for u, v in rep.participating_edge_refs:
            if u in parent and v in parent:
                union(u, v)

        # 2. إيصالات الربط المؤقتة (TBRs) — معالجة خطية O(N) دون تمدد زوجي تربيعي
        for tbr in rep.transient_binding_receipts:
            members = [m for m in tbr.member_receipt_refs if isinstance(m, str) and m in parent]
            if len(members) >= 2:
                pivot = members[0]
                for m in members[1:]:
                    union(pivot, m)

        # تجميع العقد حسب الجذر المشترك
        groups: dict[str, set[str]] = {}
        for u in rep.participating_node_refs:
            root = find(u)
            groups.setdefault(root, set()).add(u)

        rccs = [frozenset(g) for g in groups.values()]
        rccs.sort(key=lambda g: sorted(g))

        self.observability.coherence_components_count = len(rccs)
        if self.cache_enabled:
            self._rcc_cache[rep.representation_id] = rccs

        return rccs

    # ── الرؤى السياقية والمرجعيات (Referential Identity & Facet Views)
    def get_referents(self, rep: SparseDistributedCognitiveRepresentation) -> set[str]:
        """استخراج المراجع والمفاهيم المركزية والكيانات الحالية دون خلق هويات جديدة."""
        referents: set[str] = set()
        for u in rep.participating_node_refs:
            node_obj = self.graph.nodes.get(u)
            if (node_obj and (node_obj.is_concept or node_obj.region == "concept")) or u.startswith(("hub:", "concept:", "cat:", "inst:")):
                referents.add(u)
        return referents

    def get_contextual_facet(
        self, rep: SparseDistributedCognitiveRepresentation, referent_id: str
    ) -> ContextualFacetView | None:
        """توليد الرؤية الوجهية السياقية للمرجع المحدد داخل التمثيل الحالي."""
        if referent_id not in rep.participating_node_refs:
            return None

        # استخراج المكون المتماسك الحاوي للمرجع
        rccs = self.get_coherence_components(rep)
        target_comp: frozenset[str] = frozenset()
        for comp in rccs:
            if referent_id in comp:
                target_comp = comp
                break

        comp_nodes = frozenset(target_comp or {referent_id})
        comp_edges = frozenset(
            (u, v) for (u, v) in rep.participating_edge_refs if u in comp_nodes and v in comp_nodes
        )

        scopes = set()
        for tbr in rep.transient_binding_receipts:
            if any(m in comp_nodes for m in tbr.member_receipt_refs):
                scopes.add(tbr.binding_scope_id)

        node_supp = {u: self.compute_node_support(rep, u) for u in sorted(comp_nodes)}
        edge_supp = {e: self.compute_edge_support(rep, e) for e in sorted(comp_edges)}

        return ContextualFacetView(
            referent_id=referent_id,
            context=rep.context_binding_ref,
            participating_nodes=comp_nodes,
            participating_edges=comp_edges,
            active_assemblies=rep.active_assembly_refs,
            binding_scopes=tuple(sorted(scopes)),
            node_supports=node_supp,
            edge_supports=edge_supp,
        )

    def get_scope_view(self, rep: SparseDistributedCognitiveRepresentation, scope_id: str) -> ScopeView | None:
        """توليد رؤية مشتقة لنطاق تجميعي محدد."""
        matching_tbr: TransientBindingReceipt | None = None
        for tbr in rep.transient_binding_receipts:
            if tbr.binding_scope_id == scope_id:
                matching_tbr = tbr
                break

        member_elements: set[str | tuple[str, str]] = set()
        for r in rep.participation_receipts:
            if scope_id in r.scope_refs:
                member_elements.add(r.element_ref)

        if matching_tbr:
            member_elements.update(matching_tbr.member_receipt_refs)

        if not member_elements and not matching_tbr:
            return None

        rccs = self.get_coherence_components(rep)
        comp_idx: int | None = None
        for i, comp in enumerate(rccs):
            if any(m in comp for m in member_elements if isinstance(m, str)):
                comp_idx = i
                break

        return ScopeView(
            scope_id=scope_id,
            member_elements=tuple(sorted(member_elements, key=lambda x: str(x))),
            binding_receipt=matching_tbr,
            coherence_component_index=comp_idx,
        )

    def get_element_provenance(
        self, rep: SparseDistributedCognitiveRepresentation, element: str | tuple[str, str]
    ) -> list[str]:
        """استخراج سلالة ومصدر مشاركة العنصر دون تبييض مصادره الذاتية."""
        provenances = []
        for r in rep.participation_receipts:
            if r.element_ref == element:
                provenances.append(r.origin_lineage)
        return provenances or ["unknown"]

    # ── البصمة التمثيلية المعيارية (Canonical Representation Signature)
    def canonical_representation_signature(self, rep: SparseDistributedCognitiveRepresentation) -> str:
        """
        حساب البصمة التشفيرية المعيارية لمحتوى التمثيل (Content Signature).
        تعتمد حصرياً على المحتوى الدلالي المعياري (السياق، العقد، الروابط، التجمعات، الروابط المؤقتة)
        ولا تعتمد على معرف اللقطة أو زمن الساعة لضمان المطابقة القطعية الحتمية.
        """
        if self.cache_enabled and rep.representation_id in self._signature_cache:
            self.observability.cache_hits += 1
            return self._signature_cache[rep.representation_id]

        rows = []
        rows.append(f"context:{rep.context_binding_ref or 'none'}")

        # التجمعات النشطة
        for aid, v_num in sorted(rep.active_assembly_refs):
            rows.append(f"asm:{aid}:v{v_num}")

        # العقد المشاركة
        for u in sorted(rep.participating_node_refs):
            supp = self.compute_node_support(rep, u)
            prov = sorted(self.get_element_provenance(rep, u))
            rows.append(f"node:{u}|s={supp:.4f}|p={','.join(prov)}")

        # الروابط المشاركة
        for u, v in sorted(rep.participating_edge_refs):
            supp = self.compute_edge_support(rep, (u, v))
            prov = sorted(self.get_element_provenance(rep, (u, v)))
            rows.append(f"edge:{u}->{v}|s={supp:.4f}|p={','.join(prov)}")

        # إيصالات الربط المؤقتة
        for tbr in sorted(rep.transient_binding_receipts, key=lambda b: b.binding_scope_id):
            members_str = ",".join(str(m) for m in sorted(tbr.member_receipt_refs, key=lambda x: str(x)))
            rows.append(f"tbr:{tbr.binding_scope_id}|members={members_str}|origin={tbr.origin_view}")

        raw_payload = "\n".join(rows).encode("utf-8")
        sig = hashlib.sha256(raw_payload).hexdigest()[:16]

        if self.cache_enabled:
            self._signature_cache[rep.representation_id] = sig

        return sig

    def get_view(self, representation: SparseDistributedCognitiveRepresentation) -> RepresentationView:
        """الحصول على واجهة قراءة آمنة بحتة للتمثيل الحالي."""
        return RepresentationView(representation, self)


# ─────────────────────────────────────────────────────────── 7. البصمة السلوكية الحتمية للقانون 12
def rfc12_behavioral_signature(engine: RepresentationEngine) -> str:
    """
    توليد بصمة سلوكية قطعية شاملة لمعمارية RFC-12
    تغطي كافة الأنماط (تجمعات نشطة، نشاط مستجد، تراكيب متداخلة، ربط TBR، ومكونات RCC متعددة).
    """
    rows = []
    # فحص كافة التمثيلات الحالية والمغلقة
    all_reps = list(engine.active_representations.values()) + list(engine.closed_representations.values())
    all_reps.sort(key=lambda r: (r.parent_cycle_id, r.snapshot_or_microtick, sorted(r.participating_node_refs)))

    for rep in all_reps:
        sig = engine.canonical_representation_signature(rep)
        rccs = engine.get_coherence_components(rep)
        rccs_str = ";".join(",".join(sorted(c)) for c in rccs)
        rows.append(f"rep:c{rep.parent_cycle_id}:t{rep.snapshot_or_microtick}|sig={sig}|rcc={rccs_str}")

    digest_bytes = "\n".join(rows).encode("utf-8")
    return hashlib.sha256(digest_bytes).hexdigest()[:16]
