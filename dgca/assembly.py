"""
DGCA — RFC-11 / Law 14: Local Assemblies & Emergent Structural Organization.

المعمارية:
1. StructuralAssembly: نموذج بنيوي نقي غير قابل للتعديل (Immutable & Versioned).
2. ActiveAssembly: حالة تشغيلية مؤقتة (Transient Working State) مثبتة بنسخة بنيوية محددة.
3. AssemblyPolicy: سجل معايير وسياسات التنظيم البنيوي وفصل النسخ.
4. AssemblyManager: محرك القانون 14 لإدارة النشوء، التنشيط، التنافس، والتحولات البنيوية (Growth, Sanitation, Split, Merge, Retirement).
5. حماية الملكية المعرفية: المعرفة تسكن في الروابط (Edges) حصراً، والقانون 14 ينظم العلاقات دون أي نسخ أو تعديل معرفي (Δ CognitiveState = 0).
"""
from __future__ import annotations

import hashlib
import math
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from .graph import CognitiveGraph


# ─────────────────────────────────────────────────────────── 1. سجل السياسات (Policy Registry)
@dataclass
class AssemblyPolicy:
    """سجل ثوابت وسياسات التنظيم البنيوي للقانون 14 (RFC-11)."""

    policy_version: int = 1
    K_ASM_MIN: int = 3          # K_ASM^min — أدنى عدد روابط لتكوين تجمع قانوني
    N_ASM_CONFIRM: int = 5      # N_ASM^confirm — عدد التجارب الخارجية المستقلة لتأكيد التحول البنيوي
    A_MAX: int = 4              # A_max — أقصى عدد تجمعات منطقية ينتمي إليها الرابط الواحد
    K_ASM_MEM: int = 32         # K_ASM^mem — أقصى عدد روابط داخل التجمع الواحد (سقف السعة)
    K_ASM_ACTIVE: int = 8       # K_ASM^active — سقف التجمعات النشطة المتزامنة
    K_STRUCT_PENDING: int = 64  # K_struct^pending — سقف المرشحات البنيوية قيد الانتظار


# ─────────────────────────────────────────────────────────── 2. النموذج البنيوي (Structural Assembly)
@dataclass(frozen=True)
class StructuralAssembly:
    """التجمع البنيوي الدائم (Immutable & Versioned).

    لا يملك أي حالة معرفية (Cognition) أو أوزان أو مشاعر أو احتمالات.
    يحفظ مراجع العضوية والهوية والنسخة وسلسلة النسب فقط.
    """

    assembly_id: str
    version: int
    member_edges: frozenset[tuple[str, str]]
    origin_signature: str
    predecessor_version: int | None = None
    parent_assemblies: tuple[str, ...] = field(default_factory=tuple)
    is_retired: bool = False

    def __post_init__(self) -> None:
        # فحص دستوري صارم: يُحظر وجود أي خاصية معرفية مكتسبة في كائن التجمع البنيوي
        forbidden_attrs = {
            "weight", "confidence", "salience", "context_belief",
            "causal_strength", "prediction_memory", "evidence",
            "learned_excitability", "activation_strength", "winner_count",
            "loss_count", "global_importance", "score",
        }
        for attr in forbidden_attrs:
            if hasattr(self, attr) and getattr(self, attr) is not None:
                raise AttributeError(f"RFC11 Violation: Forbidden cognitive attribute '{attr}' on StructuralAssembly")

    @property
    def member_nodes(self) -> frozenset[str]:
        """العقد الأعضاء المشتقة حصراً من أطراف الروابط الأعضاء (RFC11-INV-005)."""
        nodes = set()
        for u, v in self.member_edges:
            nodes.add(u)
            nodes.add(v)
        return frozenset(nodes)

    def boundary_nodes(self, graph: CognitiveGraph) -> set[str]:
        """عقد الحدود: عقد أعضاء متصلة بروابط خارج التجمع في الرسم الحي."""
        b_nodes = set()
        m_edges = self.member_edges
        for u in self.member_nodes:
            # نفحص الروابط الخارجة والداخلة
            for e in graph.out_edges(u):
                if (e.src, e.dst) not in m_edges:
                    b_nodes.add(u)
                    break
            if u not in b_nodes:
                for e in graph.in_edges(u):
                    if (e.src, e.dst) not in m_edges:
                        b_nodes.add(u)
                        break
        return b_nodes

    def boundary_edges(self, graph: CognitiveGraph) -> set[tuple[str, str]]:
        """روابط الحدود: روابط حية في الرسم غير منتمية للتجمع لكن أحد طرفيها عضو فيه."""
        b_edges = set()
        m_nodes = self.member_nodes
        m_edges = self.member_edges
        for u in m_nodes:
            for e in graph.out_edges(u):
                pair = (e.src, e.dst)
                if pair not in m_edges:
                    b_edges.add(pair)
            for e in graph.in_edges(u):
                pair = (e.src, e.dst)
                if pair not in m_edges:
                    b_edges.add(pair)
        return b_edges

    def is_connected(self) -> bool:
        """التحقق من اتصال مجموعة الروابط الأعضاء."""
        if not self.member_edges:
            return False
        # بناء رسم جوار محلي للأطراف
        adj: dict[str, set[str]] = defaultdict(set)
        for u, v in self.member_edges:
            adj[u].add(v)
            adj[v].add(u)

        start = next(iter(adj))
        visited = set()
        queue = [start]
        visited.add(start)

        while queue:
            curr = queue.pop(0)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == len(adj)


# ─────────────────────────────────────────────────────────── 3. الحالة التشغيلية المؤقتة (Active Assembly)
@dataclass
class ActiveAssembly:
    """الحالة التشغيلية المؤقتة للتجمع النشط (Transient Working State)."""

    activation_id: str
    assembly_id: str
    pinned_version: int
    seeds: set[str] = field(default_factory=set)
    participants: set[str] = field(default_factory=set)
    active_edges: set[tuple[str, str]] = field(default_factory=set)
    frontier: set[str] = field(default_factory=set)
    context_binding: str | None = None
    status: str = "INITIATED"  # INITIATED -> ACTIVE -> CLOSED
    budget: float = 1.0
    created_tick: int = 0

    def close(self) -> None:
        """إغلاق الحالة التشغيلية دون أي تعديل في الذاكرة المعرفية للروابط."""
        self.status = "CLOSED"


# ─────────────────────────────────────────────────────────── 4. المرشحات البنيوية قيد الانتظار (Candidate State)
@dataclass
class FormationCandidate:
    """مرشح تكوين تجمع بنيوي قيد جمع الأدلة الخارجية المستقلة."""

    candidate_id: str
    edges: frozenset[tuple[str, str]]
    context_signature: str | None
    root_votes: set[str] = field(default_factory=set)
    created_t: int = 0


# ─────────────────────────────────────────────────────────── 5. سجل التشخيص والمراقبة (Observability)
@dataclass
class AssemblyObservability:
    """عدادات تشخيصية غير معرفية للمراقبة والتحقق (Observability Only)."""

    assembly_candidates_examined: int = 0
    edges_examined_for_assembly: int = 0
    structural_votes_accepted: int = 0
    structural_votes_rejected: int = 0
    duplicate_root_votes: int = 0
    self_derived_votes_rejected: int = 0
    assemblies_formed: int = 0
    growth_commits: int = 0
    sanitize_commits: int = 0
    split_commits: int = 0
    merge_commits: int = 0
    retirement_commits: int = 0
    stale_proposals_rejected: int = 0
    membership_capacity_rejections: int = 0
    assembly_capacity_rejections: int = 0
    physical_edge_transmissions: int = 0
    deduplicated_transmissions: int = 0
    active_assemblies_peak: int = 0
    pending_candidates_peak: int = 0
    versions_hot: int = 0
    versions_protected: int = 0


def canonical_assembly_id(edges: frozenset[tuple[str, str]]) -> str:
    """توليد معرف حتمي ثابت لمجموعة روابط مرتبة معيارياً."""
    sorted_edges = sorted(f"{u}->{v}" for u, v in edges)
    raw_key = "DGCA_ASM:" + ";".join(sorted_edges)
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
    return f"asm_{digest}"


# ─────────────────────────────────────────────────────────── 6. محرك القانون 14 (AssemblyManager)
class AssemblyManager:
    """مدير التجمعات المحلية ومحرك القانون 14 في معمارية DGCA."""

    def __init__(self, graph: CognitiveGraph, policy: AssemblyPolicy | None = None) -> None:
        self.graph = graph
        self.policy = policy or AssemblyPolicy()
        self.observability = AssemblyObservability()

        # السجل البنيوي: mapping logical AID -> list[StructuralAssembly versions]
        self.assemblies: dict[str, list[StructuralAssembly]] = {}

        # الفهرس العكسي القابل لإعادة البناء: mapping edge (src, dst) -> set[AID]
        self.edge_to_assemblies: dict[tuple[str, str], set[str]] = defaultdict(set)

        # المرشحات البنيوية قيد جمع الأصوات
        self.pending_candidates: dict[str, FormationCandidate] = {}
        self.pending_growth: dict[tuple[str, tuple[str, str], str | None], set[str]] = defaultdict(set)
        self.pending_merge: dict[tuple[frozenset[str], str | None], set[str]] = defaultdict(set)

        # النسخ المحمية أثناء التنشيط المفتوح
        self.protected_versions: set[tuple[str, int]] = set()

        # التجمعات النشطة الحالية
        self.active_instances: dict[str, ActiveAssembly] = {}

        # منع مضاعفة الطاقة: مفتاح الإرسال الفيزيائي (ParentCycle, MicroTick, Edge, Context)
        self.seen_transmissions: set[tuple[int, int, tuple[str, str], str | None]] = set()

    # ── القراءة والاسترجاع
    def get_latest_version(self, assembly_id: str) -> StructuralAssembly | None:
        """استرجاع أحدث نسخة منشورة للتجمع."""
        versions = self.assemblies.get(assembly_id)
        if not versions:
            return None
        return versions[-1]

    def get_assembly(self, assembly_id: str, version: int | None = None) -> StructuralAssembly | None:
        """استرجاع نسخة محددة أو أحدث نسخة."""
        versions = self.assemblies.get(assembly_id)
        if not versions:
            return None
        if version is None:
            return versions[-1]
        for asm in versions:
            if asm.version == version:
                return asm
        return None

    def live_assemblies(self) -> list[StructuralAssembly]:
        """قائمة التجمعات الحية غير المتقاعدة."""
        result = []
        for versions in self.assemblies.values():
            latest = versions[-1]
            if not latest.is_retired:
                result.append(latest)
        return result

    # ── التحقق من صحة الفهارس وإعادة بنائها (Reconstructible Indexes)
    def rebuild_indexes(self) -> None:
        """إعادة بناء الفهرس العكسي بالكامل من السجلات البنيوية المعتمدة."""
        self.edge_to_assemblies.clear()
        for versions in self.assemblies.values():
            latest = versions[-1]
            if not latest.is_retired:
                for edge in latest.member_edges:
                    self.edge_to_assemblies[edge].add(latest.assembly_id)

    # ── فحص الاتصال واستخراج المكونات المتصلة (Connected Components)
    @staticmethod
    def extract_connected_components(edges: set[tuple[str, str]]) -> list[frozenset[tuple[str, str]]]:
        """استخراج المكونات المتصلة قانونياً من مجموعة روابط دون أي بحث توافقي فرعي."""
        if not edges:
            return []

        adj: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for u, v in edges:
            adj[u].add((u, v))
            adj[v].add((u, v))

        unvisited_edges = set(edges)
        components = []

        while unvisited_edges:
            seed_edge = next(iter(unvisited_edges))
            comp_edges = set()
            edge_queue = [seed_edge]
            comp_edges.add(seed_edge)
            unvisited_edges.remove(seed_edge)

            while edge_queue:
                u, v = edge_queue.pop(0)
                for node in (u, v):
                    for inc_edge in adj[node]:
                        if inc_edge in unvisited_edges:
                            unvisited_edges.remove(inc_edge)
                            comp_edges.add(inc_edge)
                            edge_queue.append(inc_edge)

            components.append(frozenset(comp_edges))

        return components

    # ── استقبال الأدلة البنيوية الخارجية (Provenance & Structural Evidence Intake)
    def record_participation(
        self,
        participating_edges: list[tuple[str, str]],
        context: str | None = None,
        root_episode_id: str | None = None,
        valid_origin: bool = True,
        self_derived: bool = False,
    ) -> list[str]:
        """معالجة مشاركة مجموعة روابط في تجربة إدراكية خارجية مستقلة.

        يُطبق جدار الحماية ضد البيانات الذاتية، ويمنع تضخم الأصوات.
        يعيد قائمة بمعرفات التجمعات التي تأثرت أو أُنشئت.
        """
        self.observability.edges_examined_for_assembly += len(participating_edges)

        # جدار الحماية: التحقق من المصدر الخارجي الصالح
        if not valid_origin or self_derived or root_episode_id is None:
            self.observability.self_derived_votes_rejected += 1
            self.observability.structural_votes_rejected += 1
            return []

        # استبعاد الروابط اللحظية المؤقتة (inst:)
        eligible_edges = {
            (u, v) for u, v in participating_edges
            if not (u.startswith("inst:") or v.startswith("inst:") or ":inst:" in u or ":inst:" in v)
            and self.graph.edge(u, v) is not None
        }

        if not eligible_edges:
            return []

        self.observability.structural_votes_accepted += 1
        affected_assemblies = []

        # استخراج المكونات المتصلة المتزامنة
        components = self.extract_connected_components(eligible_edges)

        for comp in components:
            comp_size = len(comp)
            # فحص الحجم الأدنى والأقصى
            if comp_size < self.policy.K_ASM_MIN:
                continue

            if comp_size > self.policy.K_ASM_MEM:
                # مكون فائق الحجم: لا تكوين مباشر، ولا اقتطاع عشوائي (Fail closed)
                self.observability.assembly_capacity_rejections += 1
                continue

            # فحص التطابق مع تجمع قائم (Exact Duplicate Reuse)
            existing_match = None
            for versions in self.assemblies.values():
                latest = versions[-1]
                if not latest.is_retired and latest.member_edges == comp:
                    existing_match = latest
                    break

            if existing_match:
                # التجمع موجود مسبقاً — لا تكرار
                affected_assemblies.append(existing_match.assembly_id)
                continue

            # فحص إمكانية النمو (Growth Candidate): إضافة رابط حدودي واحد لتجمع قائم
            growth_found = False
            for versions in self.assemblies.values():
                latest = versions[-1]
                if latest.is_retired:
                    continue
                diff = comp - latest.member_edges
                if len(diff) == 1 and latest.member_edges.issubset(comp):
                    new_edge = next(iter(diff))
                    g_key = (latest.assembly_id, new_edge, context)
                    self.pending_growth[g_key].add(root_episode_id)
                    if len(self.pending_growth[g_key]) >= self.policy.N_ASM_CONFIRM:
                        new_asm = self.commit_growth(latest.assembly_id, new_edge)
                        if new_asm:
                            affected_assemblies.append(new_asm.assembly_id)
                            self.pending_growth.pop(g_key, None)
                    growth_found = True
                    break

            if growth_found:
                continue

            # فحص إمكانية الدمج (Merge Candidate): اتحاد تام لتجمعين قائمين
            merge_found = False
            live_asms = self.live_assemblies()
            for i in range(len(live_asms)):
                for j in range(i + 1, len(live_asms)):
                    a_asm, b_asm = live_asms[i], live_asms[j]
                    if comp == (a_asm.member_edges | b_asm.member_edges):
                        m_key = (frozenset([a_asm.assembly_id, b_asm.assembly_id]), context)
                        self.pending_merge[m_key].add(root_episode_id)
                        if len(self.pending_merge[m_key]) >= self.policy.N_ASM_CONFIRM:
                            merged = self.commit_merge(a_asm.assembly_id, b_asm.assembly_id)
                            if merged:
                                affected_assemblies.append(merged.assembly_id)
                                self.pending_merge.pop(m_key, None)
                        merge_found = True
                        break
                if merge_found:
                    break

            if merge_found:
                continue

            # مسار النشوء الجديد (Formation Candidate): مفصول بالسياق الدقيق (RFC11-B04)
            cand_key = f"{canonical_assembly_id(comp)}:ctx_{context or 'default'}"
            cand = self.pending_candidates.get(cand_key)
            if cand is None:
                if len(self.pending_candidates) >= self.policy.K_STRUCT_PENDING:
                    # تجاوز سقف المرشحات قيد الانتظار
                    self.observability.assembly_capacity_rejections += 1
                    continue
                cand = FormationCandidate(
                    candidate_id=canonical_assembly_id(comp),
                    edges=comp,
                    context_signature=context,
                    created_t=self.graph.t,
                )
                self.pending_candidates[cand_key] = cand

            # تسجيل الصوت البنيوي (Deduplicated by RootExternalEpisodeID)
            cand.root_votes.add(root_episode_id)

            if len(cand.root_votes) >= self.policy.N_ASM_CONFIRM:
                new_asm = self.commit_formation(cand)
                if new_asm:
                    affected_assemblies.append(new_asm.assembly_id)
                    self.pending_candidates.pop(cand_key, None)

        return affected_assemblies

    # ── التثبيت والتحولات البنيوية الذرية (Atomic Commits)
    def commit_formation(self, candidate: FormationCandidate) -> StructuralAssembly | None:
        """تثبيت نشوء تجمع بنيوي جديد (Version 1)."""
        edges = candidate.edges
        if not edges or len(edges) < self.policy.K_ASM_MIN or len(edges) > self.policy.K_ASM_MEM:
            return None

        # التحقق من سقف تعدد العضوية (Poly-membership Limit: |M(e)| <= A_max)
        for e in edges:
            current_memberships = len(self.edge_to_assemblies.get(e, set()))
            if current_memberships >= self.policy.A_MAX:
                self.observability.membership_capacity_rejections += 1
                return None

        # إنشاء النسخة الأولى
        assembly_id = candidate.candidate_id
        asm = StructuralAssembly(
            assembly_id=assembly_id,
            version=1,
            member_edges=edges,
            origin_signature=f"ctx:{candidate.context_signature or 'default'}",
        )

        self.assemblies[assembly_id] = [asm]
        for e in edges:
            self.edge_to_assemblies[e].add(assembly_id)

        self.observability.assemblies_formed += 1
        return asm

    def commit_growth(self, assembly_id: str, new_edge: tuple[str, str]) -> StructuralAssembly | None:
        """تثبيت نمو التجمع بإضافة رابط حدودي واحد (Growth Commit -> Version v+1)."""
        versions = self.assemblies.get(assembly_id)
        if not versions:
            return None
        latest = versions[-1]
        if latest.is_retired:
            return None

        # التحقق من سقف السعة
        if len(latest.member_edges) + 1 > self.policy.K_ASM_MEM:
            self.observability.assembly_capacity_rejections += 1
            return None

        # التحقق من سقف تعدد العضوية للرابط الجديد
        if len(self.edge_to_assemblies.get(new_edge, set())) >= self.policy.A_MAX:
            self.observability.membership_capacity_rejections += 1
            return None

        new_edges = frozenset(set(latest.member_edges) | {new_edge})
        new_version = latest.version + 1

        updated_asm = StructuralAssembly(
            assembly_id=assembly_id,
            version=new_version,
            member_edges=new_edges,
            origin_signature=latest.origin_signature,
            predecessor_version=latest.version,
            parent_assemblies=latest.parent_assemblies,
        )

        versions.append(updated_asm)
        self.edge_to_assemblies[new_edge].add(assembly_id)
        self.observability.growth_commits += 1
        return updated_asm

    def commit_sanitation(self, assembly_id: str, dead_edges: set[tuple[str, str]]) -> StructuralAssembly | None:
        """تنظيف الروابط الميتة/المحذوفة بالقانون 3 ونشر نسخة منقحة (Sanitation Commit)."""
        versions = self.assemblies.get(assembly_id)
        if not versions:
            return None
        latest = versions[-1]
        if latest.is_retired:
            return None

        remaining_edges = frozenset(set(latest.member_edges) - dead_edges)

        # تحديث الفهرس العكسي للروابط المنظفة
        for e in dead_edges:
            self.edge_to_assemblies[e].discard(assembly_id)

        # فحص الحجم المتبقي
        if len(remaining_edges) < self.policy.K_ASM_MIN:
            # تقاعد التجمع لعدم كفاية الحجم الأدنى
            self.retire_assembly(assembly_id)
            self.observability.sanitize_commits += 1
            return None

        # فحص الاتصال
        comps = self.extract_connected_components(set(remaining_edges))
        if len(comps) == 1:
            # التجمع ما زال متصلاً: نشر نسخة منقحة
            new_version = latest.version + 1
            sanitized = StructuralAssembly(
                assembly_id=assembly_id,
                version=new_version,
                member_edges=remaining_edges,
                origin_signature=latest.origin_signature,
                predecessor_version=latest.version,
                parent_assemblies=latest.parent_assemblies,
            )
            versions.append(sanitized)
            self.observability.sanitize_commits += 1
            return sanitized
        else:
            # انقطاع الاتصال: تشغيل الانشطار البنيوي (Split)
            self.commit_split(assembly_id, comps)
            self.observability.sanitize_commits += 1
            return None

    def commit_split(self, parent_assembly_id: str, components: list[frozenset[tuple[str, str]]]) -> list[StructuralAssembly]:
        """انشطار التجمع المنقطع إلى تجمعات فرعية مستقلة مع تقاعد التجمع الأب."""
        parent_versions = self.assemblies.get(parent_assembly_id)
        if not parent_versions:
            return []
        parent = parent_versions[-1]

        # تقاعد التجمع الأب
        self.retire_assembly(parent_assembly_id)

        created_children = []
        for comp in components:
            if len(comp) < self.policy.K_ASM_MIN:
                # أجزاء دون الحد الأدنى لا تُنشئ تجمعاً، وروابطها تبقى في الرسم
                for e in comp:
                    self.edge_to_assemblies[e].discard(parent_assembly_id)
                continue

            child_id = canonical_assembly_id(comp)
            child = StructuralAssembly(
                assembly_id=child_id,
                version=1,
                member_edges=comp,
                origin_signature=parent.origin_signature,
                parent_assemblies=(parent_assembly_id,),
            )
            self.assemblies[child_id] = [child]
            for e in comp:
                self.edge_to_assemblies[e].discard(parent_assembly_id)
                self.edge_to_assemblies[e].add(child_id)
            created_children.append(child)

        self.observability.split_commits += 1
        return created_children

    def commit_merge(self, parent_a_id: str, parent_b_id: str) -> StructuralAssembly | None:
        """دمج غير تدميري لتجمعين في تجمع اتحاد جديد (Merge Non-Destructive v1)."""
        asm_a = self.get_latest_version(parent_a_id)
        asm_b = self.get_latest_version(parent_b_id)
        if not asm_a or not asm_b or asm_a.is_retired or asm_b.is_retired:
            return None

        merged_edges = frozenset(set(asm_a.member_edges) | set(asm_b.member_edges))

        # التحقق من سقف السعة
        if len(merged_edges) > self.policy.K_ASM_MEM:
            self.observability.assembly_capacity_rejections += 1
            return None

        # التحقق من سقف تعدد العضوية لكافة الروابط
        for e in merged_edges:
            current_count = len(self.edge_to_assemblies.get(e, set()))
            # إذا كان الرابط موجوداً بالفعل في أحد الأبوين، فلن يتغير عدد عضوياته الحالية إلا بـ +1
            already_member = (parent_a_id in self.edge_to_assemblies.get(e, set())) or (parent_b_id in self.edge_to_assemblies.get(e, set()))
            if not already_member and current_count >= self.policy.A_MAX:
                self.observability.membership_capacity_rejections += 1
                return None
            elif already_member and current_count >= self.policy.A_MAX:
                # رابط مشترك وصل السقف بالفعل
                self.observability.membership_capacity_rejections += 1
                return None

        merged_id = canonical_assembly_id(merged_edges)
        merged_asm = StructuralAssembly(
            assembly_id=merged_id,
            version=1,
            member_edges=merged_edges,
            origin_signature=f"merge:{parent_a_id}+{parent_b_id}",
            parent_assemblies=(parent_a_id, parent_b_id),
        )

        self.assemblies[merged_id] = [merged_asm]
        for e in merged_edges:
            self.edge_to_assemblies[e].add(merged_id)

        # في المعمارية v1، الأبوان يبقيان حيين (Non-destructive)
        self.observability.merge_commits += 1
        return merged_asm

    def retire_assembly(self, assembly_id: str) -> None:
        """إحالة التجمع إلى التقاعد ومنع قبول تنشيطات جديدة."""
        versions = self.assemblies.get(assembly_id)
        if not versions:
            return
        latest = versions[-1]
        if not latest.is_retired:
            retired_asm = StructuralAssembly(
                assembly_id=assembly_id,
                version=latest.version + 1,
                member_edges=latest.member_edges,
                origin_signature=latest.origin_signature,
                predecessor_version=latest.version,
                parent_assemblies=latest.parent_assemblies,
                is_retired=True,
            )
            versions.append(retired_asm)
            for e in latest.member_edges:
                self.edge_to_assemblies[e].discard(assembly_id)
            self.observability.retirement_commits += 1

    # ── التنافس والاختيار المحلي (Competition, Selection & Local Dominance)
    def select_assemblies(
        self,
        cues: dict[str, float],
        context: str | None = None,
        theta_active: float = 0.05,
    ) -> list[tuple[StructuralAssembly, float, set[str]]]:
        """اختيار التجمعات النشطة محلياً عبر تغطية الإشارات والتوصيلية المعيارية للبذور.

        تستهلك حالة ما بعد القانون 4 (Post-Law-4).
        تطبق الهيمنة المحلية (Local Dominance) والكبح عند الدخول (Admission-Only Inhibition).
        تحافظ على الغموض التام (Exact Ambiguity Preservation).
        """
        # فلترة البذور النشطة
        active_cues = {u: a for u, a in cues.items() if a >= theta_active}
        if not active_cues:
            return []

        # 1. البحث المحلي عن المرشحات عبر الروابط المكشوفة محلياً (Local Discovery — NO Global Scan)
        candidate_aids = set()
        for u in active_cues:
            for e in self.graph.out_edges(u):
                if e.gate_open(context):
                    candidate_aids.update(self.edge_to_assemblies.get((e.src, e.dst), set()))
            for e in self.graph.in_edges(u):
                if e.gate_open(context):
                    candidate_aids.update(self.edge_to_assemblies.get((e.src, e.dst), set()))

        if not candidate_aids:
            return []

        self.observability.assembly_candidates_examined += len(candidate_aids)
        total_cue_activation = sum(active_cues.values())

        scored_candidates: list[dict[str, Any]] = []

        # 2. حساب الدعم والتوصيلية لكل مرشح
        for aid in candidate_aids:
            asm = self.get_latest_version(aid)
            if not asm or asm.is_retired:
                continue

            asm_nodes = asm.member_nodes
            # البذور القانونية للتجمع
            seeds_a = {u for u in active_cues if u in asm_nodes}
            if not seeds_a:
                continue

            # أ. تغطية الإشارات (Cue Coverage)
            seed_activation_sum = sum(active_cues[u] for u in seeds_a)
            cov_a = seed_activation_sum / total_cue_activation if total_cue_activation > 0 else 0.0

            # ب. التوصيلية المعيارية للبذور (Seed-Normalized Conductance)
            cond_terms = []
            for u in seeds_a:
                # أعلى وزن لرابط عضو يخرج أو يدخل قانونياً من البذرة u في السياق الحالي
                max_w = 0.0
                for u_edge, v_edge in asm.member_edges:
                    if u_edge == u or v_edge == u:
                        e_obj = self.graph.edge(u_edge, v_edge)
                        if e_obj and e_obj.gate_open(context):
                            max_w = max(max_w, e_obj.W)
                sigma_g = 1.0 - math.exp(-max_w)
                cond_terms.append(active_cues[u] * sigma_g)

            cond_a = sum(cond_terms) / seed_activation_sum if seed_activation_sum > 0 else 0.0

            # ج. الدعم الكلي (Assembly Cue Support)
            q_a = cov_a * cond_a

            scored_candidates.append({
                "asm": asm,
                "seeds": seeds_a,
                "q": q_a,
                "cov": cov_a,
                "cond": cond_a,
            })

        if not scored_candidates:
            return []

        # 3. الهيمنة المحلية (Local Dominance Filtering)
        # B dominates A (B ▷ A) if S_A* ⊆ S_B* and Q_B >= Q_A with at least one strict advantage
        non_dominated = []
        for i, cand_a in enumerate(scored_candidates):
            is_dominated = False
            for j, cand_b in enumerate(scored_candidates):
                if i == j:
                    continue
                seeds_a = cand_a["seeds"]
                seeds_b = cand_b["seeds"]
                q_a = cand_a["q"]
                q_b = cand_b["q"]

                if seeds_a.issubset(seeds_b) and q_b >= q_a and ((seeds_b > seeds_a) or (q_b > q_a)):
                    is_dominated = True
                    break
            if not is_dominated:
                non_dominated.append(cand_a)

        # 4. الترتيب وحفظ الغموض والسعة (Ambiguity Preservation & Capacity)
        non_dominated.sort(key=lambda x: x["q"], reverse=True)

        selected: list[tuple[StructuralAssembly, float, set[str]]] = []
        capacity_limit = self.policy.K_ASM_ACTIVE

        # تجميع المرشحات المتساوية تماماً في الدعم المعرفي
        idx = 0
        while idx < len(non_dominated) and len(selected) < capacity_limit:
            current_q = non_dominated[idx]["q"]
            tie_group = []
            while idx < len(non_dominated) and abs(non_dominated[idx]["q"] - current_q) < 1e-9:
                tie_group.append(non_dominated[idx])
                idx += 1

            if len(selected) + len(tie_group) <= capacity_limit:
                for item in tie_group:
                    selected.append((item["asm"], item["q"], item["seeds"]))
            else:
                # تعادل يتجاوز السعة المتبقية: الامتناع عن الاختيار العشوائي بالمعرفات (Deferred Ambiguity)
                # لا نكسر التعادل المعرفي بمعرف رقمي
                break

        return selected

    # ── إدارة التنشيط الفيزيائي ودورة الحياة (Active Assembly Lifecycle)
    def activate(
        self,
        assembly: StructuralAssembly,
        seeds: set[str],
        context: str | None = None,
    ) -> ActiveAssembly:
        """بدء تنشيط تشغيلي لتجمع مثبت بالنسخة الحالية."""
        act_id = f"act_{uuid.uuid4().hex[:8]}"
        act = ActiveAssembly(
            activation_id=act_id,
            assembly_id=assembly.assembly_id,
            pinned_version=assembly.version,
            seeds=set(seeds),
            participants=set(seeds),
            frontier=set(seeds),
            context_binding=context,
            status="ACTIVE",
            created_tick=self.graph.t,
        )
        self.active_instances[act_id] = act
        self.protected_versions.add((assembly.assembly_id, assembly.version))

        self.observability.active_assemblies_peak = max(
            self.observability.active_assemblies_peak, len(self.active_instances)
        )

        return act

    def close_activation(self, activation: ActiveAssembly) -> None:
        """إغلاق التنشيط وإلغاء حماية النسخة في حال عدم وجود تنشيطات أخرى عليها."""
        activation.close()
        self.active_instances.pop(activation.activation_id, None)

        # فحص هل توجد تنشيطات أخرى لنفس النسخة
        still_protected = any(
            act.assembly_id == activation.assembly_id and act.pinned_version == activation.pinned_version
            for act in self.active_instances.values()
        )
        if not still_protected:
            self.protected_versions.discard((activation.assembly_id, activation.pinned_version))

    def track_physical_transmission(
        self,
        parent_cycle_id: int,
        micro_tick: int,
        edge: tuple[str, str],
        context: str | None = None,
    ) -> bool:
        """التحقق من عدم تكرار الإرسال الفيزيائي للرابط المشترك في نفس الميكرو-تكة.

        يعيد True إذا كان هذا الإرسال الأول المسموح به، وFalse إذا كان مكرراً ومحجوباً.
        """
        key = (parent_cycle_id, micro_tick, edge, context)
        if key in self.seen_transmissions:
            self.observability.deduplicated_transmissions += 1
            return False
        self.seen_transmissions.add(key)
        self.observability.physical_edge_transmissions += 1
        return True


# ─────────────────────────────────────────────────────────── 7. البصمة السلوكية الحتمية للقانون 14 (Law 14 Signature)
def law14_behavioral_signature(manager: AssemblyManager) -> str:
    """بصمة سلوكية حتمية مشفرة لملخص حالة التجمعات البنيوية للقانون 14."""
    rows = []
    for aid in sorted(manager.assemblies.keys()):
        versions = manager.assemblies[aid]
        for asm in versions:
            edges_str = ",".join(sorted(f"{u}->{v}" for u, v in asm.member_edges))
            parents_str = ",".join(sorted(asm.parent_assemblies))
            rows.append(
                f"ASM|{asm.assembly_id}|v{asm.version}|{int(asm.is_retired)}|"
                f"{asm.predecessor_version or ''}|{parents_str}|{edges_str}"
            )
    blob = "\n".join(rows)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
