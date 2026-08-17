"""
بيئة الوكيل الإدراكي التفاعلي والواجهة الحية (Interactive Multimodal Agent Runtime — RFC-09).

يُنسق هذا الموديل كافة الأنظمة الفرعية لمنظومة DGCA:
- تشفير الحواس (MasterSymbolicEncoder).
- النواة والذاكرة الطوبولوجية (CognitiveGraph).
- محرك فك التشبيك والتوليد اللغوي (LinearizationEngine).
- محرك الاستدلال القياسي (AnalogicalReasoningEngine).
- العمود الفقري الفطري للأرقام والمقارنة (Quantity Backbone).
"""

from dataclasses import dataclass
from typing import Any

from .analogy import AnalogicalReasoningEngine
from .encoder import MasterSymbolicEncoder
from .graph import CognitiveGraph
from .linearizer import LinearizationEngine
from .numbers import compare_quantities, init_quantity_backbone


@dataclass
class AgentInteraction:
    """سجل تفاعل واحد للوكيل الإدراكي."""

    kind: str
    input_payload: Any
    output_payload: Any
    status: str


class CognitiveAgent:
    """الوكيل الإدراكي التفاعلي الشامل لمعمارية DGCA."""

    def __init__(self, enable_prediction: bool = True):
        self.graph = CognitiveGraph(enable_prediction=enable_prediction)
        init_quantity_backbone(self.graph)
        self.encoder = MasterSymbolicEncoder()
        self.linearizer = LinearizationEngine(self.graph)
        self.analogy = AnalogicalReasoningEngine(self.graph)
        self.history: list[AgentInteraction] = []

    def perceive_text(
        self, text: str, context: str | None = None
    ) -> dict[str, Any]:
        """معالجة وإدخال نص طبيعي إلى الذاكرة."""
        episodes = self.encoder.encode_text(text, context=context)
        ingested = self.encoder.feed_to_graph(self.graph, episodes)
        res = {
            "status": "INGESTED",
            "episodes_count": len(episodes),
            "events_created": ingested,
        }
        self.history.append(AgentInteraction("learn_text", text, res, "OK"))
        return res

    def perceive_code(
        self, code_str: str, module: str = "main"
    ) -> dict[str, Any]:
        """معالجة وإدخال كود بايثون إلى الذاكرة."""
        episodes = self.encoder.encode_code(code_str, module=module)
        ingested = self.encoder.feed_to_graph(self.graph, episodes)
        res = {
            "status": "INGESTED_CODE",
            "episodes_count": len(episodes),
            "events_created": ingested,
        }
        self.history.append(AgentInteraction("learn_code", code_str, res, "OK"))
        return res

    def query(self, prompt: str, target: str | None = None) -> str:
        """إجراء استدلال رنيني وصياغة إجابة طبيعية متماسكة."""
        pkt = self.linearizer.answer_query(prompt, target=target)
        self.history.append(
            AgentInteraction(
                "query", prompt, pkt.text, "SUCCESS" if pkt.text else "NO_REPLY"
            )
        )
        return pkt.text

    def solve_analogy(self, a: str, b: str, c: str) -> dict[str, Any]:
        """حل لغز التناسب التناظري a : b :: c : ?"""
        res = self.analogy.solve_proportion(a, b, c)
        out = {
            "status": res.status,
            "target_match": res.target_match,
            "similarity": res.mapping.similarity if res.mapping else 0.0,
            "sdi": res.mapping.sdi_score if res.mapping else 0.0,
        }
        self.history.append(
            AgentInteraction("analogy", (a, b, c), out, res.status)
        )
        return out

    def compare(self, n1: int, n2: int) -> str:
        """مقارنة مقدارين عبر العمود الفقري الفطري للأرقام."""
        c = compare_quantities(self.graph, n1, n2)
        if c == 1:
            verdict = f"{n1} is greater than {n2}"
        elif c == -1:
            verdict = f"{n1} is less than {n2}"
        else:
            verdict = f"{n1} is equal to {n2}"
        self.history.append(
            AgentInteraction("compare", (n1, n2), verdict, "OK")
        )
        return verdict

    def step_time(self, ticks: int = 1) -> dict[str, int]:
        """تمرير تكات زمنية صامتة لتفعيل التآكل والموت الخلوي."""
        nodes_before = len(self.graph.nodes)
        for _ in range(ticks):
            self.graph.tick()
        nodes_after = len(self.graph.nodes)
        return {
            "ticks": ticks,
            "pruned_nodes": max(0, nodes_before - nodes_after),
            "remaining_nodes": nodes_after,
        }

    def inspect_node(self, nid: str) -> dict[str, Any]:
        """فحص تفصيلي لحالة العقدة والروابط ومجموعات التناقض."""
        norm_nid = self.analogy._normalize_nid(nid)
        if norm_nid not in self.graph.nodes:
            return {"error": f"Node '{nid}' not found in graph"}
        node = self.graph.nodes[norm_nid]
        out_edges = [
            (e.dst, e.W, e.kind) for e in self.graph.out_edges(norm_nid)
        ]
        in_edges = [(e.src, e.W, e.kind) for e in self.graph.in_edges(norm_nid)]
        return {
            "nid": node.nid,
            "region": node.region,
            "A": node.A,
            "U": node.U,
            "is_concept": node.is_concept,
            "out_edges": out_edges,
            "in_edges": in_edges,
            "rivals_X": list(self.graph.X.get(norm_nid, set())),
        }

    def get_stats(self) -> dict[str, int]:
        """إحصائيات حية للذاكرة والرسم البياني."""
        concepts_count = len(self.graph.concepts)
        return {
            "nodes_count": len(self.graph.nodes),
            "edges_count": len(self.graph.edges),
            "concepts_count": concepts_count,
            "hypotheses_count": len(self.graph.hypotheses),
            "history_count": len(self.history),
        }

    def save_brain(self, filepath: str) -> None:
        """حفظ الشبكة المعرفية بالكامل إلى ملف JSON."""
        self.graph.save(filepath)

    def load_brain(self, filepath: str) -> None:
        """تحميل شبكة معرفية من ملف JSON وإعادة ربط محركات التوليد والاستدلال بها."""
        self.graph.load(filepath)
        self.linearizer = LinearizationEngine(self.graph)
        self.analogy = AnalogicalReasoningEngine(self.graph)
