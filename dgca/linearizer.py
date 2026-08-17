"""
محرك فك التشبيك والتوليد الخطي وحلقة الفعل (RFC-05: Graph-to-Sequence Linearization & Action Loop).

المبدأ الحاكم:
«المعرفة شبكة متوازية موزعة (Structure)، بينما التفكير والكلام مسار ديناميكي مؤقت
ينبثق من الشبكة دون أن يمس استقرارها الدائم (Dynamics)».
"""
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from .graph import CognitiveGraph
from .numbers import compare_quantities
from .reasoning import compose_relations, deep_infer


@dataclass
class ResponsePacket:
    """كائن المخرج النهائي الصادر من حلقة التوليد وفك التشبيك."""

    status: Literal["SUCCESS", "NO_RESONANT_PATH", "INCOMPLETE"]
    text: str = ""
    tokens: list[str] = field(default_factory=list)
    action_payload: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    trajectory: list[str] = field(default_factory=list)


def _clean_token(nid: str) -> str:
    """إزالة البادئات التنسيقية لتحويل معرف العقدة إلى كلمة نصية مقروءة."""
    if ":" in nid:
        parts = nid.split(":", 1)
        return parts[1]
    return nid


class LinearizationEngine:
    """محرك فك التشبيك والتوليد الخطي المستلهم عصبياً."""

    def __init__(self, graph: CognitiveGraph):
        self.graph = graph
        self.theta_path = 0.20
        self.theta_gen = 0.15

    def _normalize_nid(self, name: str) -> str:
        """مطابقة الاسم مع المعرف الفعلي في الرسم البياني."""
        if ":" in name:
            return name
        for prefix in ("text", "quantity", "hub", "vision", "audio", "ev", "cat"):
            candidate = f"{prefix}:{name}"
            if candidate in self.graph.nodes:
                return candidate
        return f"text:{name}"

    def _extract_trajectory(
        self,
        seeds: list[str],
        target: str | None = None,
        context: str | None = None,
    ) -> dict[str, float]:
        """استخلاص المسار الرنيني في وضع المحاكاة العازلة 100% دون أي تعديل في الرسم."""
        norm_seeds = [self._normalize_nid(s) for s in seeds]
        norm_target = self._normalize_nid(target) if target else None

        r = deep_infer(
            self.graph,
            norm_seeds,
            context=context,
            target=norm_target,
            mode="simulation",
        )

        energy_dict = {s: 1.0 for s in norm_seeds if s in self.graph.nodes}
        for nid, val in r.get("ranked", []):
            energy_dict[nid] = float(val)

        return energy_dict

    def _competitive_queue(
        self,
        energy_dict: dict[str, float],
        start_node: str,
        max_steps: int = 10,
    ) -> list[str]:
        """طابور التنافس والكبح الديناميكي لمنع الدوران والتكرار (Inhibition of Return)."""
        suppressed_nodes: set[str] = set()
        ordered: list[str] = [start_node]
        suppressed_nodes.add(start_node)
        curr = start_node

        for _ in range(max_steps - 1):
            candidates = {}
            for e in self.graph.out_edges(curr):
                if e.dst not in suppressed_nodes and energy_dict.get(e.dst, 0.0) >= self.theta_gen:
                    score = energy_dict[e.dst] * e.W
                    candidates[e.dst] = score

            if not candidates:
                break

            winner = max(candidates, key=lambda k: candidates[k])
            ordered.append(winner)
            suppressed_nodes.add(winner)
            curr = winner

        return ordered

    def generate(
        self,
        seeds: list[str],
        target: str | None = None,
        context: str | None = None,
        output_format: Literal["text", "code", "action"] = "text",
    ) -> ResponsePacket:
        """يستخلص المسار الرنيني ويفك تشبيكه عبر طابور التنافس وقوالب البناء السطحي."""
        norm_seeds = [self._normalize_nid(s) for s in seeds]
        norm_target = self._normalize_nid(target) if target else None

        # 1. فحص المقارنة العددية المباشرة (RFC-01)
        if (
            norm_target
            and len(norm_seeds) == 1
            and norm_seeds[0].startswith("quantity:")
            and norm_target.startswith("quantity:")
        ):
            val_a_str = _clean_token(norm_seeds[0])
            val_b_str = _clean_token(norm_target)
            if val_a_str.isdigit() and val_b_str.isdigit():
                val_a = int(val_a_str)
                val_b = int(val_b_str)
                cmp_res = compare_quantities(self.graph, val_a, val_b)
                if cmp_res == 1:
                    tokens = [str(val_a), "is", "greater", "than", str(val_b)]
                elif cmp_res == -1:
                    tokens = [str(val_a), "is", "less", "than", str(val_b)]
                else:
                    tokens = [str(val_a), "is", "equal", "to", str(val_b)]
                text = " ".join(tokens)
                return ResponsePacket(
                    status="SUCCESS",
                    text=text,
                    tokens=tokens,
                    confidence=1.0,
                    trajectory=[norm_seeds[0], norm_target],
                )

        # 2. فحص عقد الأحداث المركبة ev:*
        ev_node = None
        for s in norm_seeds:
            if s.startswith("ev:"):
                ev_node = s
                break
        if not ev_node and norm_target:
            for n in self.graph.nodes:
                if n.startswith("ev:") and norm_seeds[0].split(":", 1)[1] in n and norm_target.split(":", 1)[1] in n:
                    ev_node = n
                    break

        if ev_node:
            role_edges = sorted(
                [e for e in self.graph.out_edges(ev_node) if e.kind.startswith("role")],
                key=lambda e: e.kind,
            )
            if role_edges:
                tokens = []
                for e in role_edges:
                    clean_d = _clean_token(e.dst)
                    if "inst:" in clean_d or clean_d.startswith("vis_"):
                        shape_n = next(
                            (
                                e_out.dst
                                for e_out in self.graph.out_edges(e.dst)
                                if "shp:" in e_out.dst
                            ),
                            None,
                        )
                        if shape_n:
                            tokens.append(_clean_token(shape_n).replace("shp:", ""))
                        else:
                            tokens.append(clean_d)
                    elif clean_d.startswith("rel:"):
                        tokens.append("is")
                        tokens.append(clean_d.replace("rel:", ""))
                    else:
                        tokens.append(clean_d)

                text = " ".join(tokens)
                return ResponsePacket(
                    status="SUCCESS",
                    text=text,
                    tokens=tokens,
                    confidence=0.95,
                    trajectory=[ev_node] + [e.dst for e in role_edges],
                )

        # 3. فحص الاستدلال المتعدي (Transitive Deduction Explanation)
        if norm_target and len(norm_seeds) == 1:
            src = norm_seeds[0]
            dst = norm_target
            # فحص وجود وسيط B
            for e1 in self.graph.out_edges(src):
                mid = e1.dst
                e2 = self.graph.edge(mid, dst)
                if e2 is not None:
                    comp = compose_relations(self.graph, src, e1.kind, mid, e2.kind, dst)
                    if comp is not None:
                        src_clean = _clean_token(src)
                        mid_clean = _clean_token(mid)
                        dst_clean = _clean_token(dst)
                        comp_clean = comp.replace("role:", "")
                        e1_clean = e1.kind.replace("role:", "")
                        if comp_clean in ("greater", "taller", "less"):
                            text = f"{src_clean} is {comp_clean} than {dst_clean} because {src_clean} is {e1_clean} than {mid_clean}"
                        elif comp_clean in ("parent", "grandparent", "grandchild", "ancestor", "part_of"):
                            text = f"{src_clean} is {comp_clean} of {dst_clean} because {src_clean} is {e1_clean} of {mid_clean}"
                        else:
                            text = f"{src_clean} {comp_clean} {dst_clean} because {src_clean} {e1_clean} {mid_clean}"
                        tokens = text.split()
                        return ResponsePacket(
                            status="SUCCESS",
                            text=text,
                            tokens=tokens,
                            confidence=0.90,
                            trajectory=[src, mid, dst],
                        )

        # 4. استخلاص المسار الرنيني العازل (Ephemeral Overlay Trajectory)
        energy_dict = self._extract_trajectory(seeds, target, context)

        # بوابة منع الهلوسة الصارمة (Anti-Hallucination Gate)
        if norm_target and energy_dict.get(norm_target, 0.0) < self.theta_path:
            return ResponsePacket(status="NO_RESONANT_PATH")

        # 5. طابور التنافس والكبح (Competitive Queuing)
        ordered_nodes = self._competitive_queue(energy_dict, norm_seeds[0])

        # 6. قوالب الكود البرمجي (Code Realization)
        if output_format == "code":
            func_name = _clean_token(norm_seeds[0])
            params = []
            for e in self.graph.out_edges(norm_seeds[0]):
                if "param" in e.dst or "pos_" in e.dst:
                    params.append(_clean_token(e.dst))
            if not params:
                params = [_clean_token(n) for n in ordered_nodes[1:] if "param" in n or "pos_" in n]
            code_text = f"out = {func_name}({', '.join(params)})" if params else f"out = {func_name}()"
            return ResponsePacket(
                status="SUCCESS",
                text=code_text,
                tokens=code_text.replace("(", " ( ").replace(")", " ) ").replace(",", " , ").split(),
                confidence=0.90,
                trajectory=ordered_nodes,
            )

        # 7. قوالب الأفعال (Action Realization)
        if output_format == "action":
            action_name = _clean_token(norm_seeds[0])
            target_name = _clean_token(norm_target) if norm_target else (_clean_token(ordered_nodes[1]) if len(ordered_nodes) > 1 else None)
            args_list = [_clean_token(n) for n in ordered_nodes[2:]]
            payload = {
                "action": action_name,
                "target": target_name,
                "args": args_list,
            }
            return ResponsePacket(
                status="SUCCESS",
                text=f"EXECUTE: {action_name}({target_name})",
                action_payload=payload,
                confidence=0.88,
                trajectory=ordered_nodes,
            )

        # 8. قوالب التوصيف الاسمي والخصائص (Attributive / Copular)
        if len(ordered_nodes) >= 2:
            entity = _clean_token(ordered_nodes[0])
            attr = _clean_token(ordered_nodes[1])
            tokens = [entity, "is", attr]
            text = f"{entity} is {attr}"
            return ResponsePacket(
                status="SUCCESS",
                text=text,
                tokens=tokens,
                confidence=energy_dict.get(ordered_nodes[1], 0.5),
                trajectory=ordered_nodes,
            )

        tokens = [_clean_token(n) for n in ordered_nodes]
        return ResponsePacket(
            status="SUCCESS",
            text=" ".join(tokens),
            tokens=tokens,
            confidence=0.50,
            trajectory=ordered_nodes,
        )

    def answer_query(self, prompt: str, target: str | None = None) -> ResponsePacket:
        """استقبال استفسار باللغة الطبيعية واستخراج البذور وتوليد الإجابة."""
        words = [
            w.lower()
            for w in re.findall(r"[a-zA-Z0-9_]+", prompt)
            if w.lower()
            not in {
                "what",
                "does",
                "the",
                "is",
                "a",
                "an",
                "do",
                "did",
                "can",
                "how",
                "why",
                "where",
                "who",
                "which",
            }
        ]
        seeds = words if words else [prompt.strip()]
        return self.generate(seeds=seeds, target=target)
