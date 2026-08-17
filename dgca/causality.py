"""
محرك السببية والتنبؤ والتعلم من الخيبة (RFC-02 / Law 13: Prediction & Causality Engine).

يوفر حساب القوة السببية التفاضلية المحلية (Local Differential Causality):
CausalStrength_ij = max(0, (n_ij / N_i^total) - BaseRate_j) * W_ij * 1{lag_ij > 0}
"""
from .graph import CognitiveGraph


def causal_strength(graph: CognitiveGraph, src: str, dst: str) -> float:
    """حساب القوة السببية التفاضلية المحلية لرابط موجه بين src و dst.

    - تفصل الاقتران الإحصائي الزائف عالي التكرار (BaseRate) عن السببية الحقيقية.
    - تشترط الأسبقية الزمنية (lag > 0).
    """
    e = graph.edge(src, dst)
    if e is None or e.lag <= 0.0:
        return 0.0

    n_src = graph.nodes.get(src)
    n_dst = graph.nodes.get(dst)
    if n_src is None or n_dst is None:
        return 0.0

    t_sys = max(1, graph.t)
    base_rate_dst = n_dst.N_total / t_sys
    p_cond = e.n / max(1, n_src.N_total)
    delta_p = max(0.0, p_cond - base_rate_dst)

    return delta_p * e.W
