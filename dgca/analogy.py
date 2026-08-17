"""
محرك الاستدلال القياسي ونقل المعرفة عبر المجالات (RFC-07: Analogical Reasoning & Cross-Domain Knowledge Transfer).

المبدأ الحاكم:
«القياس ليس تشابهاً حسياً سطحياً، بل محاذاة لنظام العلاقات والسببية العميقة؛
المعرفة تُجرَّد إلى قوالب بنيوية وتُنقل كفرضيات آمنة لا تكسر الواقع ولا تلوّث البصمة الحتمية».
"""
import math
from dataclasses import dataclass, field
from typing import Literal

from .graph import CognitiveGraph
from .reasoning import deep_infer


@dataclass
class AnalogicalMapping:
    """كائن المحاذاة والربط التناظري بين زوجين من الكيانات."""

    source_pair: tuple[str, str]
    target_pair: tuple[str, str]
    similarity: float
    sdi_score: float
    is_valid: bool
    matched_paths: list[str] = field(default_factory=list)


@dataclass
class CandidateInference:
    """فرضية سببية مشروطة منقولة عبر الإسقاط القياسي."""

    source_edge: tuple[str, str, str]
    projected_edge: tuple[str, str, str]
    confidence: float
    status: Literal["ACCEPTED", "BLOCKED_BY_CONTRADICTION"]


@dataclass
class AnalogyResult:
    """المخرج النهائي لعملية الاستدلال القياسي."""

    status: Literal[
        "SUCCESS", "NO_ANALOGY_FOUND", "SPURIOUS_SURFACE_MATCH", "BLOCKED"
    ]
    target_match: str | None = None
    mapping: AnalogicalMapping | None = None
    inferences: list[CandidateInference] = field(default_factory=list)
    schema_id: str | None = None


# تصنيف أوزان الروابط الهرمية
CAUSAL_KINDS = {
    "causal",
    "causes",
    "leads_to",
    "attracts",
    "gravity",
    "coulomb",
    "force",
    "revolves_around",
    "orbits",
    "orbit",
    "rules",
    "governs",
    "transforms",
    "heats",
    "expands",
    "charges",
    "binds",
    "teaches",
    "treats",
    "role:causal",
    "role:agent",
    "role:action",
}

ORDINAL_KINDS = {
    "succ",
    "pred",
    "greater",
    "less",
    "taller",
    "parent",
    "child",
    "grandparent",
    "ancestor",
    "descendant",
    "part_of",
    "subset_of",
    "role:parent",
}

SPATIAL_KINDS = {
    "on_top",
    "inside",
    "above",
    "below",
    "left_of",
    "right_of",
    "vis:rel:on_top",
    "vis:rel:inside",
    "vis:rel:above",
    "vis:rel:below",
    "vis:rel:left_of",
    "vis:rel:right_of",
    "assoc",
}


OPPOSITE_PAIRS = {
    ("left_of", "right_of"),
    ("right_of", "left_of"),
    ("above", "below"),
    ("below", "above"),
    ("inside", "outside"),
    ("outside", "inside"),
    ("on_top", "below"),
    ("below", "on_top"),
}


def _classify_kind(kind: str) -> tuple[float, str]:
    """تحديد الرتبة الوزنية للرابط: سببية/وظيفية/تحويلية (4.0)، ترتيبية/هرمية (2.0)، مكانية/سطحية (0.25)."""
    k_clean = kind.lower().replace("vis:rel:", "").replace("role:", "")
    # 1. الروابط السببية والوظيفية والتحويلية والتماثلية المكانية (الرتبة العليا 4.0)
    if (
        kind.startswith("role:")
        or k_clean in CAUSAL_KINDS
        or k_clean
        in {
            "transforms_to",
            "spatial_inverse",
            "spatial_reflection",
            "symmetry",
            "mirror",
            "opposite_of",
            "rotates",
            "causes_light",
        }
        or any(
            c in k_clean
            for c in (
                "caus",
                "attract",
                "grav",
                "coulomb",
                "revolv",
                "orbit",
                "rule",
                "teach",
                "treat",
                "force",
                "govern",
                "gender",
                "function",
                "power",
                "bind",
                "charge",
                "transform",
                "inverse",
                "reflect",
                "mirror",
                "symmetr",
                "rotat",
            )
        )
    ):
        return 4.0, "causal"
    # 2. الروابط الترتيبية والهرمية
    if k_clean in ORDINAL_KINDS or any(
        o in k_clean for o in ("succ", "pred", "great", "less", "parent", "child", "part")
    ):
        return 2.0, "ordinal"
    # 3. الروابط المكانية والاقترانية العادية
    return 0.25, "spatial"


class AnalogicalReasoningEngine:
    """محرك الاستدلال القياسي ونقل المعرفة عبر المجالات (RFC-07 & RFC-07.1)."""

    def __init__(self, graph: CognitiveGraph):
        self.graph = graph
        self.theta_analogy = 0.25
        self.theta_sim = 0.70
        self.sdi_threshold = 0.65

    def _normalize_nid(self, name: str) -> str:
        if name in self.graph.nodes:
            return name
        for prefix in ("text", "quantity", "hub", "vision", "audio", "ev", "cat", "schema"):
            cand = f"{prefix}:{name}"
            if cand in self.graph.nodes:
                return cand
        if ":" in name:
            return name
        return f"text:{name}"

    def _extract_rrs(self, u: str, v: str) -> dict[str, tuple[float, float, str]]:
        """استخلاص البصمة العلائقية المقيدة بأفق قفزتين مع الحفاظ على مفاهيم الأشكال الهندسية والتماثل."""
        paths: dict[str, tuple[float, float, str]] = {}
        if u not in self.graph.nodes or v not in self.graph.nodes:
            return paths

        # 1. روابط القفزة الواحدة (1-Hop direct edges)
        for e in self.graph.out_edges(u):
            if e.dst == v and e.W >= 0.20:
                if e.kind.startswith(("clr:", "sz:")):
                    continue
                w_weight, r_type = _classify_kind(e.kind)
                paths[f"dir:{e.kind}"] = (e.W, w_weight, r_type)

        for e in self.graph.out_edges(v):
            if e.dst == u and e.W >= 0.20:
                if e.kind.startswith(("clr:", "sz:")):
                    continue
                w_weight, r_type = _classify_kind(e.kind)
                paths[f"rev:{e.kind}"] = (e.W, w_weight, r_type)

        # 2. روابط القفزتين (2-Hop paths via intermediary)
        for e1 in self.graph.out_edges(u):
            mid = e1.dst
            if mid in (u, v) or e1.W < 0.25:
                continue
            if e1.kind.startswith(("clr:", "sz:")):
                continue
            for e2 in self.graph.out_edges(mid):
                if e2.dst == v and e2.W >= 0.25:
                    if e2.kind.startswith(("clr:", "sz:")):
                        continue
                    w_eff = min(e1.W, e2.W)
                    w1_weight, _ = _classify_kind(e1.kind)
                    w2_weight, _ = _classify_kind(e2.kind)
                    w_weight = (w1_weight + w2_weight) / 2.0
                    r_type = "causal" if (w1_weight >= 4.0 or w2_weight >= 4.0) else ("ordinal" if (w1_weight >= 2.0 or w2_weight >= 2.0) else "spatial")

                    # فحص التماثل والانعكاس المكاني عبر المحور الفاصل
                    k1 = e1.kind.replace("vis:rel:", "").lower()
                    k2 = e2.kind.replace("vis:rel:", "").lower()
                    if (k1, k2) in OPPOSITE_PAIRS:
                        w_weight = 4.0
                        r_type = "causal"

                    paths[f"2hop:{e1.kind}->{e2.kind}"] = (w_eff, w_weight, r_type)

        return paths

    def _check_role_polarity(self, a: str, b: str, c: str, d: str) -> bool:
        """فحص تطابق قطبية الأدوار بين النظامين لمنع عكس الفاعل والمفعول مع استبعاد الروابط الاقترانية المتماثلة."""
        ab_edges = [e for e in self.graph.out_edges(a) if e.dst == b and e.kind not in {"sim", "assoc"}]
        ba_edges = [e for e in self.graph.out_edges(b) if e.dst == a and e.kind not in {"sim", "assoc"}]
        cd_edges = [e for e in self.graph.out_edges(c) if e.dst == d and e.kind not in {"sim", "assoc"}]
        dc_edges = [e for e in self.graph.out_edges(d) if e.dst == c and e.kind not in {"sim", "assoc"}]

        if ab_edges and not ba_edges and dc_edges and not cd_edges:
            return False
        if ba_edges and not ab_edges and cd_edges and not dc_edges:
            return False

        a_roles = [e.kind for e in self.graph.out_edges(a) if e.dst == b and e.kind not in {"sim", "assoc"}]
        c_roles = [e.kind for e in self.graph.out_edges(c) if e.dst == d and e.kind not in {"sim", "assoc"}]
        d_roles = [e.kind for e in self.graph.out_edges(d) if e.dst == c and e.kind not in {"sim", "assoc"}]

        return not (a_roles and d_roles and not c_roles)

    def _get_entity_attributes(self, nid: str) -> dict[str, set[str]]:
        """استخراج الصفات البصرية والمكانية للكيان في ألغاز الرؤية والتحول."""
        attrs: dict[str, set[str]] = {"clr": set(), "shp": set(), "sz": set(), "rel": set()}
        for e in self.graph.out_edges(nid):
            if e.kind in {"sim", "rev:sim"}:
                continue
            dst_clean = e.dst.replace("vision:", "")
            if dst_clean.startswith("vis:clr:"):
                attrs["clr"].add(dst_clean.split("vis:clr:")[-1])
            elif dst_clean.startswith("vis:shp:"):
                attrs["shp"].add(dst_clean.split("vis:shp:")[-1])
            elif dst_clean.startswith("vis:sz:"):
                attrs["sz"].add(dst_clean.split("vis:sz:")[-1])
            elif dst_clean.startswith("vis:rel:") or e.kind.startswith("vis:rel"):
                rel_kind = e.kind.replace("vis:rel:", "")
                attrs["rel"].add(f"{rel_kind}->{e.dst}")
        return attrs

    def evaluate_analogy(
        self,
        source_pair: tuple[str, str],
        target_pair: tuple[str, str],
    ) -> AnalogicalMapping:
        """يقيس درجة التماثل البنيوي والعمق النظامي (SDI) بين نظامين علائقيين."""
        a, b = self._normalize_nid(source_pair[0]), self._normalize_nid(source_pair[1])
        c, d = self._normalize_nid(target_pair[0]), self._normalize_nid(target_pair[1])

        # 1. فحص قطبية الأدوار
        if not self._check_role_polarity(a, b, c, d):
            return AnalogicalMapping(
                source_pair=(a, b),
                target_pair=(c, d),
                similarity=0.0,
                sdi_score=0.0,
                is_valid=False,
                matched_paths=[],
            )

        # 2. فحص استنتاج قواعد تحويل الخصائص (ARC-AGI Rule Induction)
        attrs_a = self._get_entity_attributes(a)
        attrs_b = self._get_entity_attributes(b)
        attrs_c = self._get_entity_attributes(c)
        attrs_d = self._get_entity_attributes(d)

        if attrs_a["shp"] and (attrs_a["shp"] == attrs_b["shp"]) and attrs_a["clr"] != attrs_b["clr"]:
            clr_src_trans = (attrs_a["clr"], attrs_b["clr"])
            if attrs_c["shp"] and (attrs_c["shp"] == attrs_d["shp"]) and (attrs_c["clr"], attrs_d["clr"]) == clr_src_trans:
                return AnalogicalMapping(
                    source_pair=(a, b),
                    target_pair=(c, d),
                    similarity=0.95,
                    sdi_score=1.0,
                    is_valid=True,
                    matched_paths=["rule_induction:color_transform_shape_preserve"],
                )

        # 3. فحص قلب العلاقات المكانية الطوبولوجية (Spatial Inversion)
        rels_a = {e.kind: e.dst for e in self.graph.out_edges(a)}
        rels_c = {e.kind: e.dst for e in self.graph.out_edges(c)}
        rels_d = {e.kind: e.dst for e in self.graph.out_edges(d)}

        if "spatial_inverse" in rels_a and rels_a["spatial_inverse"] == b:
            inside_c = rels_c.get("vis:rel:inside")
            inside_d = rels_d.get("vis:rel:inside")
            if inside_c and inside_d:
                clean_c = c.replace("text:", "")
                clean_d = d.replace("text:", "")
                if inside_c.replace("text:", "") in clean_d or f"{clean_c}_inv" in inside_d:
                    return AnalogicalMapping(
                        source_pair=(a, b),
                        target_pair=(c, d),
                        similarity=0.95,
                        sdi_score=1.0,
                        is_valid=True,
                        matched_paths=["spatial_inversion:inside_containment"],
                    )

        # 4. استخلاص البصمات العلائقية العامة
        rrs_src = self._extract_rrs(a, b)
        rrs_tgt = self._extract_rrs(c, d)

        if not rrs_src or not rrs_tgt:
            return AnalogicalMapping(
                source_pair=(a, b),
                target_pair=(c, d),
                similarity=0.0,
                sdi_score=0.0,
                is_valid=False,
                matched_paths=[],
            )

        # 5. مطابقة المسارات وحساب التماثل والعمق
        matched_keys = set(rrs_src) & set(rrs_tgt)
        if not matched_keys:
            for w_s, weight_s, type_s in rrs_src.values():
                for w_t, weight_t, type_t in rrs_tgt.values():
                    if type_s == type_t and weight_s >= 2.0:
                        matched_keys.add(f"abstract:{type_s}")

        if not matched_keys:
            return AnalogicalMapping(
                source_pair=(a, b),
                target_pair=(c, d),
                similarity=0.0,
                sdi_score=0.0,
                is_valid=False,
                matched_paths=[],
            )

        # حساب SDI وفق المعادلة الرياضية في RFC-07
        matched_pairs_list = []
        has_causal = False
        num_sum = 0.0
        denom_sum = 0.0
        for k in matched_keys:
            if k.startswith("abstract:"):
                type_name = k.split(":", 1)[1]
                w_imp = 4.0 if type_name == "causal" else (2.0 if type_name == "ordinal" else 0.25)
                w_eff = 0.80
            else:
                w_s, w_imp, _ = rrs_src[k]
                w_t, _, _ = rrs_tgt[k]
                w_eff = min(w_s, w_t)

            if w_imp >= 4.0:
                has_causal = True
            matched_pairs_list.append((w_eff, w_imp))
            num_sum += w_eff * w_imp
            denom_sum += w_eff * 4.0

        sdi_score = (num_sum / max(0.001, denom_sum)) if denom_sum > 0 else 0.0
        sdi_score = min(1.0, sdi_score)

        # شرط القبول: SDI >= 0.65 أو وجود تطابق سببي/تحويلي مباشر
        direct_causal = any(
            (k in rrs_src and rrs_src[k][1] >= 4.0)
            or (k in rrs_tgt and rrs_tgt[k][1] >= 4.0)
            for k in matched_keys
            if not k.startswith("abstract:")
        )
        is_valid = (sdi_score >= self.sdi_threshold and has_causal) or (direct_causal and has_causal)

        # حساب درجة التشابه Sim_rel
        sum_src = sum(w * imp for w, imp, _ in rrs_src.values())
        sum_tgt = sum(w * imp for w, imp, _ in rrs_tgt.values())
        sim_rel = num_sum / (math.sqrt(max(0.001, sum_src)) * math.sqrt(max(0.001, sum_tgt)))
        sim_rel = min(1.0, sim_rel)

        return AnalogicalMapping(
            source_pair=(a, b),
            target_pair=(c, d),
            similarity=sim_rel,
            sdi_score=sdi_score,
            is_valid=is_valid,
            matched_paths=list(matched_keys),
        )

    def solve_proportion(
        self,
        a: str,
        b: str,
        c: str,
        project_inferences: bool = True,
        abstract_schema: bool = True,
    ) -> AnalogyResult:
        """يحل لغز التناسب التناظري: A : B :: C : ?"""
        norm_a = self._normalize_nid(a)
        norm_b = self._normalize_nid(b)
        norm_c = self._normalize_nid(c)

        if norm_a not in self.graph.nodes or norm_b not in self.graph.nodes or norm_c not in self.graph.nodes:
            return AnalogyResult(status="NO_ANALOGY_FOUND")

        # 1. إطلاق مسح رنيني تناظري من C
        sweep_res = deep_infer(self.graph, seeds=[norm_c], mode="simulation")
        ranked = sweep_res.get("ranked", [])
        sweep_acts = dict(ranked)

        # استبعاد A و B و C من الترشيحات
        excluded = {norm_a, norm_b, norm_c}
        # جلب المرشحين من الرسم
        candidate_nids = [nid for nid in self.graph.nodes if nid not in excluded and not nid.startswith(("schema:", "hub:"))]

        best_cand: str | None = None
        best_score: float = 0.0
        best_mapping: AnalogicalMapping | None = None
        spurious_found = False

        for cand in candidate_nids:
            mapping = self.evaluate_analogy((norm_a, norm_b), (norm_c, cand))
            if not mapping.is_valid:
                if mapping.similarity > 0.30 and mapping.sdi_score < self.sdi_threshold:
                    spurious_found = True
                continue

            act = sweep_acts.get(cand, 0.20)
            score = mapping.similarity * (1.0 + act)
            if score > best_score:
                best_score = score
                best_cand = cand
                best_mapping = mapping

        if not best_cand or best_score < self.theta_analogy:
            status = "SPURIOUS_SURFACE_MATCH" if spurious_found else "NO_ANALOGY_FOUND"
            return AnalogyResult(status=status, mapping=best_mapping)

        # 2. الإسقاط القياسي وفحص التناقض (Pre-Projection Law 4 Gate)
        inferences: list[CandidateInference] = []
        if project_inferences:
            # البحث عن علاقات سببية صادرة من b
            for e_src in self.graph.out_edges(norm_b):
                if _classify_kind(e_src.kind)[0] >= 4.0:
                    pred = e_src.dst.split(":", 1)[-1]
                    # فحص ما إذا كانت الفرضية تتعارض مع مصفوفة التناقض X للعقدة الهدف
                    target_rivals = self.graph.X.get(best_cand, set())
                    is_blocked = any(pred in r or r in pred for r in target_rivals)

                    status_inf: Literal["ACCEPTED", "BLOCKED_BY_CONTRADICTION"] = (
                        "BLOCKED_BY_CONTRADICTION" if is_blocked else "ACCEPTED"
                    )
                    inf = CandidateInference(
                        source_edge=(norm_b, e_src.kind, e_src.dst),
                        projected_edge=(best_cand, e_src.kind, f"hyp:{pred}"),
                        confidence=best_mapping.similarity * 0.85,
                        status=status_inf,
                    )
                    inferences.append(inf)
                    if status_inf == "ACCEPTED":
                        self.graph.hypotheses.append({
                            "src": best_cand,
                            "kind": e_src.kind,
                            "dst": f"hyp:{pred}",
                            "confidence": inf.confidence,
                            "source_analogy": f"{norm_a}:{norm_b}::{norm_c}:{best_cand}",
                        })

        # 3. تجريد القالب المعزول (Schema Abstraction)
        schema_id: str | None = None
        if abstract_schema and best_mapping and best_mapping.similarity >= self.theta_sim:
            clean_a = norm_a.split(":")[-1]
            clean_b = norm_b.split(":")[-1]
            schema_id = f"schema:{clean_a}_{clean_b}_system"
            schema_node = self.graph.node(schema_id, region="schema", is_concept=True)
            schema_node.is_concept = True
            schema_node.members |= {norm_a, norm_b, norm_c, best_cand}

        return AnalogyResult(
            status="SUCCESS",
            target_match=best_cand,
            mapping=best_mapping,
            inferences=inferences,
            schema_id=schema_id,
        )
