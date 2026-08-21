"""
DGCA — RFC-13 v1.0 & Law 15 v1.0
Pattern Completion, Pattern Separation & Bounded Pattern Reinstatement & Competitive Settling

Authoritative Specification: RFC-13-DGCA-Pattern-Completion-Separation-Law-15-v1.0.md
Status: FROZEN / ADOPTED
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .config import Law
from .representation import (
    ParticipationReceipt,
    SparseDistributedCognitiveRepresentation,
)

if TYPE_CHECKING:
    from .graph import CognitiveGraph


# ─────────────────────────────────────────────────────────── Observability (Non-Cognitive)
@dataclass
class CompletionObservability:
    """عدادات مراقبة غير معرفية وخالصة التشخيص (لا تؤثر على الديناميكيات أو التعلم)."""

    sdcr_nodes_inspected: int = 0
    sdcr_edges_inspected: int = 0
    local_assembly_refs_inspected: int = 0
    candidates_formed: int = 0
    frontier_targets_inspected: int = 0
    ingress_refs_inspected: int = 0
    proposals_created: int = 0
    competition_groups_formed: int = 0
    root_witness_checks: int = 0
    scoped_commits: int = 0
    remote_objects_inspected: int = 0
    settling_iterations: int = 0
    invalidations_count: int = 0
    budget_exhaustions_count: int = 0

    def reset(self) -> None:
        for fld in self.__dataclass_fields__:
            setattr(self, fld, 0)


# ─────────────────────────────────────────────────────────── Transient Data Structures
@dataclass(frozen=True)
class PatternCandidate:
    """P_k = <CID_k, RID_t, RCC_k, S_k, G_k, Q_k, E_k>

    عرض مشتق ومؤقت (Derived Transient View) ولا يملك أي حالة معرفية دائمة.
    """

    candidate_id: str
    parent_representation_id: str
    rcc_id: str | None
    seed_refs: frozenset[str]
    structural_refs: frozenset[str | tuple[str, str]]
    assembly_refs: frozenset[str]
    scope_view: tuple[str, ...]
    context_ref: str | None
    role_ref: str | None
    evidence_view: dict[str, Any]
    created_t: int = 0

    def candidate_signature(self) -> str:
        """بصمة تشخيصية غير معرفية للمرشح."""
        parts = [
            self.parent_representation_id,
            self.rcc_id or "none",
            ",".join(sorted(self.seed_refs)),
            ",".join(sorted(str(r) for r in self.structural_refs)),
            ",".join(sorted(self.assembly_refs)),
            ",".join(self.scope_view),
            self.context_ref or "none",
            self.role_ref or "none",
        ]
        return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class ReinstatementProposal:
    """q = <QID, ParentRID, CandidateRef, TargetRef, IngressRefs, ScopeView, RootCueRefs>

    سجل تشغيلي مؤقت (Transient Operational Record) يمثل مقترح استعادة لم يبت فيه بعد.
    """

    proposal_id: str
    parent_representation_id: str
    settling_epoch_id: str | None
    candidate_ref: str
    target_ref: str | tuple[str, str]
    target_kind: str  # "node" or "edge"
    ingress_refs: frozenset[tuple[str, str]]
    scope_view: tuple[str, ...]
    root_cue_refs: frozenset[str]
    role_ref: str | None = None
    estimated_activation: float = 0.0
    provenance: str = "PATTERN_COMPLETION"
    created_t: int = 0


@dataclass(frozen=True)
class CompetitiveAlternativeSet:
    """CAS_K = <CompetitionKey_K, CandidateRefs_K, ProposalRefs_K>

    عرض مشتق للمرشحين المتنافسين داخل مفتاح تنافس محلي مشترك.
    """

    competition_key: str
    candidate_refs: frozenset[str]
    proposal_refs: frozenset[str]


@dataclass
class SettlingEpoch:
    """SE = <SEID, RootRID, RootAuthorityRefs, MemorySnapshotRef, RemainingBudget, CommittedSet>

    حالة حوكمة تشغيلية مؤقتة متعددة اللقطات (Law 15 Multi-Snapshot Governance State).
    """

    epoch_id: str
    root_representation_id: str
    root_authority_refs: frozenset[str]
    memory_snapshot_ref: str
    remaining_budget: float
    committed_set: set[tuple[Any, tuple[str, ...], str | None]] = field(default_factory=set)
    closure_reason: str | None = None
    status: str = "ACTIVE"  # "ACTIVE" or "CLOSED"
    created_t: int = 0
    step_count: int = 0

    def close(self, reason: str) -> None:
        self.status = "CLOSED"
        self.closure_reason = reason


@dataclass(frozen=True)
class SettlingOutcomeView:
    """SettlingOutcomeView = <ClosureReason, UnresolvedAlternativeViews>

    واجهة تسليم مشتقة لقراءة مخرجات مرحلة الاستقرار.
    """

    closure_reason: str
    iterations: int
    committed_targets: frozenset[tuple[Any, tuple[str, ...], str | None]]
    unresolved_alternatives: list[dict[str, Any]]
    final_representation_id: str
    budget_consumed: float


# ─────────────────────────────────────────────────────────── Pattern Completion Engine
class PatternCompletionEngine:
    """محرك استكمال وفصل الأنماط والقانون 15 (Law 15 Settling Engine).

    محرك وظيفي خالص لا يملك أي معرفة دائمة، ويعمل عبر لقطات SDCR المعيارية المجمدة.
    """

    def __init__(self, graph: CognitiveGraph) -> None:
        self._graph = graph
        self.observability = CompletionObservability()
        self._candidate_cache: dict[str, list[PatternCandidate]] = {}
        self._active_epochs: dict[str, SettlingEpoch] = {}

    def clear_caches(self) -> None:
        """مسح الذاكرة المؤقتة الشفافة دون أي أثر دلالي."""
        self._candidate_cache.clear()

    def get_memory_snapshot_ref(self) -> str:
        """حساب البصمة المعيارية للحالة المعرفية والبنيوية الدائمة الحالية."""
        rows = []
        for (u, v), e in sorted(self._graph.edges.items()):
            ctxs = ",".join(sorted(e.contexts))
            rows.append(f"e:{u}->{v}|W={e.W:.4f}|g={e.g}|k={e.kind}|c=[{ctxs}]")
        for nid, n in sorted(self._graph.nodes.items()):
            rows.append(f"n:{nid}|r={n.region}|c={int(n.is_concept)}|i={int(n.is_intrinsic)}")
        for k, v in sorted(self._graph.X.items()):
            rows.append(f"X:{k}={','.join(sorted(v))}")
        if hasattr(self._graph, "_assembly_manager") and self._graph._assembly_manager is not None:
            mgr = self._graph.assembly_manager
            for aid, versions in sorted(mgr.assemblies.items()):
                latest = versions[-1]
                rows.append(f"asm:{aid}|v={latest.version}|m={len(latest.member_edges)}|r={int(latest.is_retired)}")
        return hashlib.sha256("\n".join(rows).encode()).hexdigest()[:16]

    # ─────────────────────────────────────────────────────── RFC-13.2: Candidate Formation
    def discover_candidates(
        self,
        representation: SparseDistributedCognitiveRepresentation,
        rcc_filter: str | None = None,
    ) -> list[PatternCandidate]:
        """اكتشاف مرشحي الأنماط محلياً انطلاقاً من عناصر التمثيل الحالي الحاضرة فعلياً.

        الحظر الدستوري: يُمنع المسح الشامل لكل العقد، الروابط، التجميعات، أو المفاهيم.
        """
        self.observability.sdcr_nodes_inspected += len(representation.participating_node_refs)
        self.observability.sdcr_edges_inspected += len(representation.participating_edge_refs)

        cache_key = f"{representation.representation_id}|{rcc_filter or 'all'}"
        if cache_key in self._candidate_cache:
            return self._candidate_cache[cache_key]

        candidates_map: dict[str, PatternCandidate] = {}
        t_now = self._graph.t
        ctx = representation.context_binding_ref

        # استخراج الإيصالات الحالية ومجموعات النطاق والأدوار
        receipts_by_element: dict[str, list[ParticipationReceipt]] = {}
        for r in representation.participation_receipts:
            elem_key = r.element_ref if isinstance(r.element_ref, str) else f"{r.element_ref[0]}->{r.element_ref[1]}"
            receipts_by_element.setdefault(elem_key, []).append(r)

        # 1. الاكتشاف عبر التجميعات النشطة والمحلية المرتبطة بالعقد الحالية
        if hasattr(self._graph, "assembly_manager"):
            mgr = self._graph.assembly_manager
            live_asms = mgr.live_assemblies()
            for node_id in sorted(representation.participating_node_refs):
                matching_asms = [asm for asm in live_asms if node_id in asm.member_nodes]
                self.observability.local_assembly_refs_inspected += len(matching_asms)
                for asm in matching_asms:
                    if asm.is_retired:
                        continue
                    # تجميع العقد والروابط البنيوية للتجميعة
                    structural_refs: set[str | tuple[str, str]] = set()
                    for edge_pair in asm.member_edges:
                        structural_refs.add(edge_pair)
                        structural_refs.add(edge_pair[0])
                        structural_refs.add(edge_pair[1])

                    # استخراج البذور الحاضرة فعلياً من التمثيل الحالي
                    seeds = {n for n in structural_refs if isinstance(n, str) and n in representation.participating_node_refs}
                    if not seeds:
                        continue

                    # استخراج النطاقات المتوافقة للبذور
                    scopes: set[str] = set()
                    for s in seeds:
                        for rec in receipts_by_element.get(s, []):
                            scopes.update(rec.scope_refs)
                    scope_tuple = tuple(sorted(scopes)) if scopes else ("global",)

                    cid_parts = [asm.assembly_id, ",".join(sorted(seeds)), ",".join(scope_tuple), ctx or "none"]
                    cid = f"cand_asm_{hashlib.sha256('|'.join(cid_parts).encode('utf-8')).hexdigest()[:12]}"

                    if cid not in candidates_map:
                        cand = PatternCandidate(
                            candidate_id=cid,
                            parent_representation_id=representation.representation_id,
                            rcc_id=rcc_filter,
                            seed_refs=frozenset(seeds),
                            structural_refs=frozenset(structural_refs),
                            assembly_refs=frozenset([asm.assembly_id]),
                            scope_view=scope_tuple,
                            context_ref=ctx,
                            role_ref=None,
                            evidence_view={
                                "type": "assembly",
                                "assembly_id": asm.assembly_id,
                                "seeds_count": len(seeds),
                                "total_members": len(asm.member_edges),
                            },
                            created_t=t_now,
                        )
                        candidates_map[cid] = cand

        # 2. الاكتشاف عبر الجوار المحلي للروابط القائمة
        for node_id in sorted(representation.participating_node_refs):
            for e in self._graph.out_edges(node_id):
                if not e.gate_open(ctx):
                    continue
                # التأكد من أن الرابط سياقي ومفتوح
                edge_pair = (e.src, e.dst)
                seeds = {e.src}
                if e.dst in representation.participating_node_refs:
                    seeds.add(e.dst)

                scopes = set()
                for s in seeds:
                    for rec in receipts_by_element.get(s, []):
                        scopes.update(rec.scope_refs)
                scope_tuple = tuple(sorted(scopes)) if scopes else ("global",)

                cid_parts = [f"edge_{e.src}_{e.dst}", ",".join(sorted(seeds)), ",".join(scope_tuple), ctx or "none"]
                cid = f"cand_edge_{hashlib.sha256('|'.join(cid_parts).encode('utf-8')).hexdigest()[:12]}"

                if cid not in candidates_map:
                    cand = PatternCandidate(
                        candidate_id=cid,
                        parent_representation_id=representation.representation_id,
                        rcc_id=rcc_filter,
                        seed_refs=frozenset(seeds),
                        structural_refs=frozenset([e.src, e.dst, edge_pair]),
                        assembly_refs=frozenset(),
                        scope_view=scope_tuple,
                        context_ref=ctx,
                        role_ref=None,
                        evidence_view={"type": "edge", "kind": e.kind, "W": e.W},
                        created_t=t_now,
                    )
                    candidates_map[cid] = cand

        result = sorted(candidates_map.values(), key=lambda c: c.candidate_id)
        self.observability.candidates_formed += len(result)
        self._candidate_cache[cache_key] = result
        return result

    # ─────────────────────────────────────────────────────── RFC-13.3: Frontier & Eligibility
    def derive_completion_frontier(
        self,
        candidate: PatternCandidate,
        representation: SparseDistributedCognitiveRepresentation,
    ) -> list[str]:
        """اشتقاق حد الاستكمال المحلي المباشر (Immediate Local Frontier F_P(t))."""
        participating = representation.participating_node_refs
        frontier: set[str] = set()

        for ref in candidate.structural_refs:
            if isinstance(ref, str) and ref not in participating and ref in self._graph.nodes:
                # التحقق من وجود مسار محلي مباشر من البذور الحاضرة
                for seed in candidate.seed_refs:
                    e = self._graph.edge(seed, ref)
                    if e and e.gate_open(candidate.context_ref):
                        frontier.add(ref)
                        break

        self.observability.frontier_targets_inspected += len(frontier)
        return sorted(frontier)

    def evaluate_reinstatement_eligibility(
        self,
        candidate: PatternCandidate,
        representation: SparseDistributedCognitiveRepresentation,
        settling_epoch: SettlingEpoch | None = None,
    ) -> list[ReinstatementProposal]:
        """تقييم أهلية الاستعادة باستخدام فيزياء القانون 4 والقانون 7 القائمة دون أي عتبات أو مكافآت جديدة."""
        proposals: list[ReinstatementProposal] = []
        frontier = self.derive_completion_frontier(candidate, representation)
        ctx = candidate.context_ref
        t_now = self._graph.t

        root_cues = settling_epoch.root_authority_refs if settling_epoch else candidate.seed_refs

        for target in frontier:
            # التحقق من أن الهدف غير نشط حالياً في التمثيل
            if target in representation.participating_node_refs:
                continue

            # جمع روافد التنشيط المحلية المباشرة من البذور الحاضرة
            ingress_edges: list[tuple[str, str]] = []
            raw_incoming: dict[str, float] = {}

            for seed in sorted(candidate.seed_refs):
                e = self._graph.edge(seed, target)
                if e and e.gate_open(ctx):
                    self.observability.ingress_refs_inspected += 1
                    # استخراج قيمة تنشيط العقدة البذرة
                    a_src = self._graph.nodes[seed].A if seed in self._graph.nodes else Law.C_MAX
                    if a_src <= 0.0:
                        a_src = Law.C_MAX  # افتراض كامل للبذور الحاضرة في التمثيل

                    raw_val = a_src * e.W * Law.E_BUDGET_0
                    if e.kind != "assoc":
                        raw_val *= Law.DELTA_GEN
                    raw_incoming[target] = raw_incoming.get(target, 0.0) + raw_val
                    ingress_edges.append((seed, target))

            if not ingress_edges:
                continue

            # تطبيق سقف الصادر والمثبطات التنافسية الموجودة (Law 4 / Law 7 physics)
            total_in = raw_incoming.get(target, 0.0)
            press = sum(
                self._graph.nodes[k].A
                for k in self._graph.X.get(target, ())
                if k in self._graph.nodes
            )
            net_signal = total_in - Law.BETA_INHIBIT * press
            estimated_a = min(Law.C_MAX, self._graph._sigma(net_signal)) if hasattr(self._graph, "_sigma") else min(Law.C_MAX, max(0.0, net_signal))

            # شرط الأهلية: تجاوز أدنى إشارة معتبرة للنظام (MIN_SIGNAL)
            if estimated_a > Law.MIN_SIGNAL:
                qid_parts = [candidate.candidate_id, target, ",".join(candidate.scope_view), str(t_now)]
                qid = f"rp_{hashlib.sha256('|'.join(qid_parts).encode('utf-8')).hexdigest()[:12]}"
                proposal = ReinstatementProposal(
                    proposal_id=qid,
                    parent_representation_id=representation.representation_id,
                    settling_epoch_id=settling_epoch.epoch_id if settling_epoch else None,
                    candidate_ref=candidate.candidate_id,
                    target_ref=target,
                    target_kind="node",
                    ingress_refs=frozenset(ingress_edges),
                    scope_view=candidate.scope_view,
                    root_cue_refs=frozenset(root_cues),
                    role_ref=candidate.role_ref,
                    estimated_activation=estimated_a,
                    provenance="PATTERN_COMPLETION",
                    created_t=t_now,
                )
                proposals.append(proposal)
                self.observability.proposals_created += 1

        return sorted(proposals, key=lambda p: p.proposal_id)

    # ─────────────────────────────────────────────────────── RFC-13.4: Pattern Separation
    def group_competitive_alternatives(
        self,
        candidates: list[PatternCandidate],
        proposals: list[ReinstatementProposal],
    ) -> list[CompetitiveAlternativeSet]:
        """تجميع البدائل المتنافسة محلياً عبر مفاتيح التنافس الموروثة حصراً."""
        prop_by_cand: dict[str, list[ReinstatementProposal]] = {}
        for p in proposals:
            prop_by_cand.setdefault(p.candidate_ref, []).append(p)

        def _norm_nid(nid: str) -> str:
            return nid if ":" in nid else f"text:{nid}"

        # 1. فهرس عكسي محلي: mapping node -> list[PatternCandidate]
        cand_by_node: dict[str, list[PatternCandidate]] = {}
        cand_by_role: dict[str, list[PatternCandidate]] = {}
        for c in candidates:
            for r in c.structural_refs:
                if isinstance(r, str):
                    cand_by_node.setdefault(r, []).append(c)
                    cand_by_node.setdefault(_norm_nid(r), []).append(c)
            if c.role_ref:
                cand_by_role.setdefault(c.role_ref, []).append(c)

        groups: dict[str, set[str]] = {}

        # 2. التنافس المحلي عبر مصفوفة التناقض X دون أي فحص شامل
        seen_pairs: set[tuple[str, str]] = set()
        for c1 in candidates:
            c1_nodes = [r for r in c1.structural_refs if isinstance(r, str)]
            for n1 in c1_nodes:
                n1_text = _norm_nid(n1)
                contradictory_nodes = set(self._graph.X.get(n1, ())) | set(self._graph.X.get(n1_text, ()))
                for n2 in contradictory_nodes:
                    for c2 in cand_by_node.get(n2, []):
                        if c1.candidate_id != c2.candidate_id:
                            pair_key = (min(c1.candidate_id, c2.candidate_id), max(c1.candidate_id, c2.candidate_id))
                            if pair_key not in seen_pairs:
                                seen_pairs.add(pair_key)
                                k_parts = [pair_key[0], pair_key[1]]
                                comp_key = f"comp_excl_{hashlib.sha256('|'.join(k_parts).encode()).hexdigest()[:10]}"
                                groups.setdefault(comp_key, set()).update(k_parts)

        # 3. التنافس المحلي عبر حصرية النطاق للأدوار المشتركة
        for role_cands in cand_by_role.values():
            if len(role_cands) > 1:
                for i, c1 in enumerate(role_cands):
                    for c2 in role_cands[i + 1 :]:
                        if (
                            c1.scope_view != c2.scope_view
                            and "global" not in c1.scope_view
                            and "global" not in c2.scope_view
                        ):
                            pair_key = (min(c1.candidate_id, c2.candidate_id), max(c1.candidate_id, c2.candidate_id))
                            if pair_key not in seen_pairs:
                                seen_pairs.add(pair_key)
                                k_parts = [pair_key[0], pair_key[1]]
                                comp_key = f"comp_excl_{hashlib.sha256('|'.join(k_parts).encode()).hexdigest()[:10]}"
                                groups.setdefault(comp_key, set()).update(k_parts)

        cas_list: list[CompetitiveAlternativeSet] = []
        for comp_key, cand_ids in sorted(groups.items()):
            p_ids: set[str] = set()
            for cid in cand_ids:
                for p in prop_by_cand.get(cid, []):
                    p_ids.add(p.proposal_id)
            cas = CompetitiveAlternativeSet(
                competition_key=comp_key,
                candidate_refs=frozenset(cand_ids),
                proposal_refs=frozenset(p_ids),
            )
            cas_list.append(cas)
            self.observability.competition_groups_formed += 1

        return cas_list

    def arbitrate_competition(
        self,
        cas: CompetitiveAlternativeSet,
        candidates_map: dict[str, PatternCandidate],
        proposals_map: dict[str, ReinstatementProposal],
        root_authority: frozenset[str],
    ) -> tuple[str, frozenset[str], list[ReinstatementProposal]]:
        """تحكيم التنافس عبر الاحتواء التام لشهود الجذر (Strict Root-Witness Set Inclusion).

        Returns: (verdict: "RESOLVED" | "AMBIGUOUS", winner_candidates, approved_proposals)
        """
        # بناء مجموعات شهود الجذر لكل مرشح
        witness_sets: dict[str, frozenset[str]] = {}
        for cid in sorted(cas.candidate_refs):
            cand = candidates_map.get(cid)
            if cand:
                # الشهود هم فقط البذور الحاضرة في RootAuthority الأصلية
                w_set = frozenset(cand.seed_refs.intersection(root_authority))
                witness_sets[cid] = w_set
                self.observability.root_witness_checks += 1

        # فحص الهيمنة الصارمة (Strict Proper Superset)
        dominated: set[str] = set()
        cids = sorted(cas.candidate_refs)
        for i, c1 in enumerate(cids):
            for c2 in cids[i + 1 :]:
                w1 = witness_sets.get(c1, frozenset())
                w2 = witness_sets.get(c2, frozenset())
                if w1 > w2:  # w1 is strict proper superset of w2
                    dominated.add(c2)
                elif w2 > w1:  # w2 is strict proper superset of w1
                    dominated.add(c1)

        non_dominated = [cid for cid in cids if cid not in dominated]

        # 1. إذا بقي مرشح مهيمن واحد
        if len(non_dominated) == 1:
            winner_cid = non_dominated[0]
            approved = [
                p for pid in cas.proposal_refs
                if (p := proposals_map.get(pid)) and p.candidate_ref == winner_cid
            ]
            return "RESOLVED", frozenset([winner_cid]), approved

        # 2. حالة الغموض (AMBIGUOUS): الحفاظ على البدائل واستخراج المقترحات المشتركة الآمنة (Shared-Safe)
        proposals_by_cand: dict[str, list[ReinstatementProposal]] = {}
        for pid in cas.proposal_refs:
            p = proposals_map.get(pid)
            if p and p.candidate_ref in non_dominated:
                proposals_by_cand.setdefault(p.candidate_ref, []).append(p)

        # المقترحات المشتركة الآمنة: يجب أن تتفق عليها كافة البدائل غير المهيمن عليها
        shared_safe: list[ReinstatementProposal] = []
        if non_dominated:
            first_cand = non_dominated[0]
            for p1 in proposals_by_cand.get(first_cand, []):
                # مطابقة الهدف والنطاق والدور
                target_key = (p1.target_ref, p1.scope_view, p1.role_ref)
                is_shared_across_all = True
                for other_cid in non_dominated[1:]:
                    other_props = proposals_by_cand.get(other_cid, [])
                    other_keys = {(op.target_ref, op.scope_view, op.role_ref) for op in other_props}
                    if target_key not in other_keys:
                        is_shared_across_all = False
                        break
                if is_shared_across_all:
                    shared_safe.append(p1)

        return "AMBIGUOUS", frozenset(non_dominated), shared_safe

    # ─────────────────────────────────────────────────────── RFC-13.5 / Law 15: Settling
    def run_settling_epoch(
        self,
        initial_representation: SparseDistributedCognitiveRepresentation,
        budget: float = Law.E_BUDGET_0,
    ) -> tuple[SparseDistributedCognitiveRepresentation, SettlingOutcomeView]:
        """تشغيل دورة الاستقرار المتكرر للقانون 15 عبر لقطات SDCR متتالية حتى التوقف الحتمي."""
        t_start = self._graph.t
        root_rid = initial_representation.representation_id
        root_authority = frozenset(initial_representation.participating_node_refs)
        memory_snap = self.get_memory_snapshot_ref()

        epoch_id = f"se_{hashlib.sha256(f'{root_rid}|{t_start}|{memory_snap}'.encode()).hexdigest()[:12]}"
        epoch = SettlingEpoch(
            epoch_id=epoch_id,
            root_representation_id=root_rid,
            root_authority_refs=root_authority,
            memory_snapshot_ref=memory_snap,
            remaining_budget=budget,
            created_t=t_start,
        )
        self._active_epochs[epoch_id] = epoch

        current_rep = initial_representation
        unresolved_cas_records: list[dict[str, Any]] = []
        iterations = 0

        while epoch.status == "ACTIVE":
            iterations += 1
            self.observability.settling_iterations += 1
            epoch.step_count = iterations

            # 1. فحص ثبات الذاكرة الدائمة (Memory Snapshot Invalidation Check)
            current_snap = self.get_memory_snapshot_ref()
            if current_snap != epoch.memory_snapshot_ref:
                epoch.close("INVALIDATED")
                self.observability.invalidations_count += 1
                break

            # 2. فحص استنزاف الميزانية الموروثة غير المتجددة
            if epoch.remaining_budget <= 0.0:
                epoch.close("BUDGET_EXHAUSTED")
                self.observability.budget_exhaustions_count += 1
                break

            # 3. اكتشاف المرشحين محلياً
            candidates = self.discover_candidates(current_rep)
            if not candidates:
                epoch.close("FIXED_POINT")
                break

            candidates_map = {c.candidate_id: c for c in candidates}

            # 4. تقييم أهلية المقترحات
            all_proposals: list[ReinstatementProposal] = []
            for cand in candidates:
                props = self.evaluate_reinstatement_eligibility(cand, current_rep, settling_epoch=epoch)
                all_proposals.extend(props)

            if not all_proposals:
                epoch.close("FIXED_POINT")
                break

            proposals_map = {p.proposal_id: p for p in all_proposals}

            # 5. تجميع التنافس وتحكيمه
            cas_list = self.group_competitive_alternatives(candidates, all_proposals)
            competing_proposal_ids: set[str] = set()
            approved_from_arbitration: list[ReinstatementProposal] = []
            has_ambiguity_this_round = False

            for cas in cas_list:
                competing_proposal_ids.update(cas.proposal_refs)
                verdict, non_dom, approved = self.arbitrate_competition(
                    cas, candidates_map, proposals_map, epoch.root_authority_refs
                )
                approved_from_arbitration.extend(approved)
                if verdict == "AMBIGUOUS":
                    has_ambiguity_this_round = True
                    unresolved_cas_records.append({
                        "competition_key": cas.competition_key,
                        "non_dominated_candidates": sorted(non_dom),
                        "iteration": iterations,
                    })

            # المقترحات غير المتنافسة تُقبل تلقائياً
            independent_proposals = [
                p for p in all_proposals if p.proposal_id not in competing_proposal_ids
            ]
            all_approved = approved_from_arbitration + independent_proposals

            # 6. تصفية المقترحات ضد CommittedSet (منع إعادة الاستعادة داخل نفس Epoch)
            new_commits: list[ReinstatementProposal] = []
            for p in all_approved:
                commit_key = (p.target_ref, p.scope_view, p.role_ref)
                if commit_key not in epoch.committed_set:
                    new_commits.append(p)

            # 7. فحص التقدم (Progress Check)
            if not new_commits:
                if has_ambiguity_this_round or unresolved_cas_records:
                    epoch.close("AMBIGUOUS_FIXED_POINT")
                else:
                    epoch.close("FIXED_POINT")
                break

            # 8. تنفيذ معاملة الاستعادة الذرية (Failure-Atomic Commit Transaction)
            # استهلاك الميزانية الموروثة
            step_cost = Law.GAMMA
            epoch.remaining_budget = max(0.0, epoch.remaining_budget - step_cost)

            # تسجيل التثبيت وإصدار التنشيط الداخلي القانوني
            new_receipts: list[ParticipationReceipt] = list(current_rep.participation_receipts)
            for p in new_commits:
                commit_key = (p.target_ref, p.scope_view, p.role_ref)
                epoch.committed_set.add(commit_key)
                self.observability.scoped_commits += 1

                # تنشيط العقدة فيزيائياً في الرسم البياني بصفة مؤقتة
                if isinstance(p.target_ref, str) and p.target_ref in self._graph.nodes:
                    node_obj = self._graph.nodes[p.target_ref]
                    node_obj.excite(t_start + iterations, p.estimated_activation)

                # إضافة إيصال مشاركة جديد يحمل provenance = PATTERN_COMPLETION
                rec_id = f"rec_comp_{p.proposal_id}"
                new_rec = ParticipationReceipt(
                    receipt_id=rec_id,
                    element_ref=p.target_ref,
                    parent_cycle_id=t_start + iterations,
                    snapshot_or_microtick=iterations,
                    origin_lineage="PATTERN_COMPLETION",
                    participation_kind=p.target_kind,
                    scope_refs=p.scope_view,
                    activation_magnitude=p.estimated_activation,
                    relational_drive=p.estimated_activation,
                )
                new_receipts.append(new_rec)

            # 9. إعادة بناء لقطة SDCR جديدة معيارية عبر المحرك (RFC-12 Canonical Re-entry)
            rep_engine = self._graph.representation_engine
            current_rep = rep_engine.build_representation(
                parent_cycle_id=t_start + iterations,
                snapshot_or_microtick=iterations,
                context=current_rep.context_binding_ref,
                participation_receipts=new_receipts,
                transient_bindings=list(current_rep.transient_binding_receipts),
                active_assemblies=current_rep.active_assembly_refs,
            )

        budget_spent = budget - epoch.remaining_budget
        outcome_view = SettlingOutcomeView(
            closure_reason=epoch.closure_reason or "FIXED_POINT",
            iterations=iterations,
            committed_targets=frozenset(epoch.committed_set),
            unresolved_alternatives=unresolved_cas_records,
            final_representation_id=current_rep.representation_id,
            budget_consumed=budget_spent,
        )

        return current_rep, outcome_view


# ─────────────────────────────────────────────────────────── Behavioral Signature
def rfc13_behavioral_signature(engine: PatternCompletionEngine) -> str:
    """توليد البصمة السلوكية المعيارية لـ RFC-13 / Law 15 عبر سيناريو تحقق مرجعي شامل."""
    g = engine._graph
    # إعداد سيناريو مرجعي محلي متعدد الحالات
    u1, v1 = "canon_u1", "canon_v1"
    g.link(u1, v1, W=0.85)
    g.link(v1, "canon_target1", W=0.80)
    g.node(u1, "text").excite(1, 0.9)
    g.node(v1, "text").excite(1, 0.85)

    r = [
        ParticipationReceipt("r_c1", u1, 1, 0, "external", "node", activation_magnitude=0.9),
        ParticipationReceipt("r_c2", v1, 1, 0, "external", "node", activation_magnitude=0.85),
        ParticipationReceipt("r_c12", (u1, v1), 1, 0, "external", "edge", relational_drive=0.85),
    ]
    rep_engine = g.representation_engine
    rep0 = rep_engine.build_representation(1, 0, None, r)

    rep_final, outcome = engine.run_settling_epoch(rep0, budget=1.0)
    final_sig = rep_engine.canonical_representation_signature(rep_final)

    digest_parts = [
        outcome.closure_reason,
        str(outcome.iterations),
        str(len(outcome.committed_targets)),
        f"{outcome.budget_consumed:.4f}",
        final_sig,
    ]
    return hashlib.sha256("|".join(digest_parts).encode("utf-8")).hexdigest()[:16]
