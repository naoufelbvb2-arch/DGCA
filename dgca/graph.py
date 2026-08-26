"""
الطبقة الحالية: العقدة، الرابط، الشبكة.

المعرفة تسكن في الروابط لا في العقد. العقدة موزّع طاقة محايد خفيف الحسابات،
تحمل تنشيطاً متبقياً يتلاشى ولا تخزّن شيئاً دائماً. الرابط هو المستودع الحقيقي
للذاكرة.

القوانين المطبَّقة حتى الآن: 1 (النشوء)، 2 (التعزيز)، 3 (التآكل)، 5 (التثبيت)، 6 (المصدر).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .config import HUB, Law


# ─────────────────────────────────────────────────────────── العقدة
@dataclass
class Node:
    """حزمة إشارة S_i = <A_i(t), t_spawn, O_i>."""

    nid: str                       # المعرّف، بصيغة "region:symbol"
    region: str                    # O_i — وسم المصدر الحسي
    is_concept: bool = False       # عقدة مفهوم مجرّد في المنطقة المركزية
    A: float = 0.0                 # A_i(t) — التنشيط، ذاكرة قصيرة المدى
    t_spawn: int = -999            # زمن انطلاق الإشارة الحالية
    episode: str | None = None     # معرّف الحلقة الإدراكية
    members: set = field(default_factory=set)   # أعضاء المفهوم (للمفاهيم فقط)
    U: float = 0.0                 # منفعة المفهوم
    V: float = 0.0                 # القطبية الوجدانية المكتسبة
    head: str | None = None        # المكان الذي انبثق عنه المفهوم
    is_intrinsic: bool = False     # عقدة جوهرية معفاة من التقليم
    N_total: int = 0               # عداد التكات الكلية التي نُشطت فيها العقدة (ق13)

    def excite(self, t: int, value: float, episode: str | None = None) -> None:
        """تنشيط العقدة عند التكة t، مسقوفاً بـ C_MAX."""
        self.A = min(Law.C_MAX, value)
        self.t_spawn = t
        self.episode = episode
        if value > 0.0:
            self.N_total += 1

    def relax(self) -> None:
        """A ← ρ·A،  episode ← ∅ — تآكل التنشيط، والحلقة تُغلق بانتهاء التكة.

        التنشيط المتبقي يبقى (العقدة ما زالت ساخنة)، لكن الحلقة التي وُلد فيها
        تنتهي. بدون هذا يجتاز زوجٌ باقٍ من تكة سابقة فحصَ المصدر مرة ثانية،
        فيُعزَّز مرتين ويكتسب سياق تكة لم يقع فيها اقترانه.
        """
        self.A *= Law.RHO_ACTIVATION
        if self.A < 0.01:
            self.A = 0.0
        self.episode = None


def _is_instance(nid: str) -> bool:
    return (
        nid.startswith(("inst:", "instance:"))
        or ":inst:" in nid
        or nid.split(":", 1)[-1].startswith("inst:")
    )


# ─────────────────────────────────────────────────────────── الرابط
@dataclass
class Edge:
    """مستودع المعرفة."""

    src: str                       # الطرف المصدر
    dst: str                       # الطرف الهدف
    W: float = 0.0                 # الوزن
    kind: str = "assoc"            # النوع
    origin: str = ""               # وسم المصدر
    t_created: int = 0             # البصمة الزمنية — الإنشاء
    t_last_update: int = 0         # البصمة الزمنية — آخر تحديث
    n: int = 0                     # عدّاد التعزيز
    M_max: float = 1.0             # أعلى معزّز حسّي
    S: float = 0.0                 # البروز
    tagged: bool = False           # عبر عتبة الوسم
    valence: float = 0.0           # القطبية
    lag: float = 0.0               # متوسط الفارق الموضعي
    fwd: bool = False              # رابط مكان→صفة
    g: str | None = None           # البوابة السياقية
    contexts: set = field(default_factory=set)
    ctx_hits: dict = field(default_factory=dict)
    is_intrinsic: bool = False     # رابط جوهري دائم معفى من التآكل
    k_fail: int = 0                # عداد الخيبة المتتالية لفشل التوقع (ق13)

    def gate_open(self, ctx: str | None) -> bool:
        """الرابط بلا بوابة مفتوح دائماً؛ وإلا يفتح لسياقه وحده."""
        return self.g is None or self.g == ctx

    # ── ق5 — خصائص محسوبة، لا حقول مخزّنة: الحالة تُشتقّ ولا تُفترق عنها أبداً
    @property
    def locked(self) -> bool:
        """W ≥ θ_solid ∧ n ≥ n_min ∧ (|C| ≥ κ ∨ g ≠ ∅).

        التجميد يحتاج آليتين معاً: تصفير ΔW يمنع الزيادة، وإعفاء التكة في ق3
        يمنع النقصان. الأرضية وحدها كانت ستهبط بالرابط من وزنه المكتسب إلى
        θ_solid عند أول تكة. ومن هنا دلالتان متمايزتان مقصودتان: المقفل
        المستعمَل يتجمّد عند وزنه المكتسب، والمقفل المهجور ينزل إلى الأرضية
        ويستقر عندها فلا يُنسى أبداً.

        تُستثنى عقد الحالات العابرة (inst:) وروابطها من القفل الدائم لتتآكل وتُحذف.
        يُلغى القفل بالتباطؤ (hysteresis unlock) بعد 3 خيبات متتالية (k_fail ≥ 3).
        """
        if _is_instance(self.src) or _is_instance(self.dst):
            return False
        if self.k_fail >= Law.K_FAIL_UNLOCK:
            return False
        return (
            self.W >= Law.THETA_SOLID
            and self.n >= Law.N_MIN
            and (len(self.contexts) >= Law.KAPPA_CTX or self.g is not None)
        )

    @property
    def P(self) -> int:
        """P_ij = 1 − 1{مقفل} — معامل التعديل: صفر يجمّد الرابط."""
        return 0 if self.locked else 1

    @property
    def W_floor(self) -> float:
        """أرضية التآكل ملغاة بإلغاء القانون 3. تعيد 0.0 دوماً."""
        return 0.0


# ─────────────────────────────────────────────────────────── الشبكة
@dataclass
class CognitiveGraph:
    """الشبكة: عقد وروابط، مع فهرسي جوار مرآتين لـ edges.

    الثبات البنيوي: out_adj و in_adj مرآتان لـ edges ولا يجوز أن يفترقا عنه.
    كل إنشاء أو حذف أو إعادة توجيه يمرّ عبر _link / _unlink حصراً.
    """

    t: int = 0
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[tuple[str, str], Edge] = field(default_factory=dict)
    out_adj: dict[str, dict[str, Edge]] = field(default_factory=dict)
    in_adj: dict[str, dict[str, Edge]] = field(default_factory=dict)
    X: dict[str, set[str]] = field(default_factory=dict)   # مجموعات التناقض
    concept_hits: dict[str, int] = field(default_factory=dict)   # تكرار المكان
    drives: dict[str, dict] = field(default_factory=dict)        # ق12 — الدوافع
    dmg: float = 0.0                                             # تلف هذه التكة
    goal: str | None = None                                      # الهدف الجاري
    outcome: float = 0.0                                         # أثر حسم الهدف
    log: list[str] = field(default_factory=list)
    enable_prediction: bool = False                              # تفعيل ق13
    prediction_pool: dict[str, float] = field(default_factory=dict)       # بركة التنبؤ
    prediction_sources: dict[str, list[str]] = field(default_factory=dict) # مصادر التوقع
    hypotheses: list[dict] = field(default_factory=list)                   # مستودع الفرضيات القياسية المعزولة (RFC-07)
    _assembly_manager: Any = field(default=None, repr=False)
    _representation_engine: Any = field(default=None, repr=False)
    _completion_engine: Any = field(default=None, repr=False)
    _generation_engine: Any = field(default=None, repr=False)
    _recurrent_engine: Any = field(default=None, repr=False)
    _loop_engine: Any = field(default=None, repr=False)

    @property
    def assembly_manager(self) -> Any:
        """محرك التجمعات المحلية للقانون 14 (RFC-11)."""
        if self._assembly_manager is None:
            from .assembly import AssemblyManager
            self._assembly_manager = AssemblyManager(self)
        return self._assembly_manager

    @assembly_manager.setter
    def assembly_manager(self, mgr: Any) -> None:
        self._assembly_manager = mgr

    @property
    def representation_engine(self) -> Any:
        """محرك التمثيل المعرفي الموزع المتناثر وإيصالات الربط المؤقت (RFC-12)."""
        if self._representation_engine is None:
            from .representation import RepresentationEngine
            self._representation_engine = RepresentationEngine(self)
        return self._representation_engine

    @representation_engine.setter
    def representation_engine(self, engine: Any) -> None:
        self._representation_engine = engine

    @property
    def completion_engine(self) -> Any:
        """محرك استكمال وفصل الأنماط والقانون 15 (RFC-13)."""
        if self._completion_engine is None:
            from .completion import PatternCompletionEngine
            self._completion_engine = PatternCompletionEngine(self)
        return self._completion_engine

    @completion_engine.setter
    def completion_engine(self, engine: Any) -> None:
        self._completion_engine = engine

    @property
    def generation_engine(self) -> Any:
        """محرك الديناميكيات التوليدية الهرمية والتحويل التسلسلي النحوي والقانون 16 (RFC-14)."""
        if self._generation_engine is None:
            from .generation import HierarchicalGenerativeEngine
            self._generation_engine = HierarchicalGenerativeEngine(self)
        return self._generation_engine

    @generation_engine.setter
    def generation_engine(self, engine: Any) -> None:
        self._generation_engine = engine

    @property
    def recurrent_engine(self) -> Any:
        """محرك التوليد التنبؤي التكراري والاستمرار عبر اللقطات والقانون 17 (RFC-15)."""
        if self._recurrent_engine is None:
            from .recurrent import PredictiveRecurrentGenerativeEngine
            self._recurrent_engine = PredictiveRecurrentGenerativeEngine(self)
        return self._recurrent_engine

    @recurrent_engine.setter
    def recurrent_engine(self, engine: Any) -> None:
        self._recurrent_engine = engine

    @property
    def loop_engine(self) -> Any:
        """محرك التنسيق المعرفي التوليدي الموحد وحلقة البيئة والمهمة (RFC-16)."""
        if self._loop_engine is None:
            from .loop import UnifiedGenerativeCognitiveLoopEngine
            self._loop_engine = UnifiedGenerativeCognitiveLoopEngine(self)
        return self._loop_engine

    @loop_engine.setter
    def loop_engine(self, engine: Any) -> None:
        self._loop_engine = engine

    @property
    def concepts(self) -> dict[str, Node]:
        """العقد المفاهيمية المعممة المشتقة بالقانون 10 أو القوالب القياسية."""
        return {nid: n for nid, n in self.nodes.items() if n.is_concept}

    # ── العقد
    def node(
        self,
        nid: str,
        region: str,
        is_concept: bool = False,
        is_intrinsic: bool = False,
    ) -> Node:
        """يُنشئ عند الغياب، ويعيد الموجود عند الحضور."""
        n = self.nodes.get(nid)
        if n is None:
            n = Node(nid, region, is_concept=is_concept, is_intrinsic=is_intrinsic)
            self.nodes[nid] = n
        else:
            if is_concept:
                n.is_concept = True
            if is_intrinsic:
                n.is_intrinsic = True
        return n

    # ── قراءة الروابط
    def edge(self, a: str, b: str) -> Edge | None:
        return self.edges.get((a, b))

    def out_edges(self, nid: str) -> list[Edge]:
        return list(self.out_adj.get(nid, {}).values())

    def in_edges(self, nid: str) -> list[Edge]:
        return list(self.in_adj.get(nid, {}).values())

    # ── كتابة الروابط (المنفذ الوحيد)
    def _link(
        self,
        e_or_src: Edge | str,
        dst: str | None = None,
        W: float = 1.0,
        kind: str = "assoc",
        **kwargs,
    ) -> None:
        """يضيف الرابط إلى الثلاثة. يدعم كائن Edge أو المعاملات المباشرة."""
        if isinstance(e_or_src, Edge):
            e = e_or_src
        else:
            e = Edge(
                e_or_src,
                str(dst),
                W=W,
                kind=kind,
                t_created=self.t,
                t_last_update=self.t,
                **kwargs,
            )
        self._unlink(e.src, e.dst)
        reg_src = e.src.split(":", 1)[0] if ":" in e.src else "text"
        reg_dst = e.dst.split(":", 1)[0] if ":" in e.dst else "text"
        if e.src not in self.nodes:
            self.node(e.src, reg_src)
        if e.dst not in self.nodes:
            self.node(e.dst, reg_dst)
        self.edges[(e.src, e.dst)] = e
        self.out_adj.setdefault(e.src, {})[e.dst] = e
        self.in_adj.setdefault(e.dst, {})[e.src] = e

    def _unlink(self, a: str, b: str) -> None:
        """يحذف من الثلاثة بلا شرط. آمن على رابط غير موجود."""
        existed = (a, b) in self.edges
        self.edges.pop((a, b), None)
        self.out_adj.get(a, {}).pop(b, None)
        self.in_adj.get(b, {}).pop(a, None)
        if existed:
            if self._assembly_manager is not None:
                affected = list(self._assembly_manager.edge_to_assemblies.get((a, b), set()))
                for aid in affected:
                    self._assembly_manager.commit_sanitation(aid, {(a, b)})
            # RFC-10: Local Orphan Reclamation after lawful edge removal
            for endpoint in (a, b):
                self._reclaim_local_orphan(endpoint)

    def _reclaim_local_orphan(self, nid: str) -> None:
        """RFC-10 Local Orphan Reclamation: Reclaims endpoint if operationally orphaned after edge removal."""
        n = self.nodes.get(nid)
        if n is None or n.is_intrinsic:
            return
        if (
            not self.out_adj.get(nid)
            and not self.in_adj.get(nid)
            and (not n.is_concept or nid.startswith(("ev:", "inst:")) or ":inst:" in nid)
        ):
            self._remove_node(nid)

    # الاسم العام الصريح للربط والفك
    link = _link
    unlink = _unlink

    # ── ق6 — البصمة الزمنية والمصدر
    @staticmethod
    def _valid_origin(i: Node, j: Node) -> bool:
        """1_ValidOrigin(i,j) = 1  ⟺  episode_i = episode_j ≠ ∅.

        الزمن والمصدر هما ما يفصل الاقتران الحقيقي عن الصدفة: إشارتان من حلقتين
        إدراكيتين مختلفتين قد تتصادفا بلا أي علاقة.
        """
        return i.episode is not None and i.episode == j.episode

    # ── ق1 — النشوء والتأسيس
    def _law1_create(self, i: Node, j: Node) -> Edge | None:
        """E_edge(i,j) = 1  ⟺  (A_i·A_j ≥ θ_creation) ∧ 1_ValidOrigin ∧ (edge ∉ E).

        W_ij^(init) = W_base. العتبة شاملة. الرابط موجّه: (i,j) و(j,i) رابطان مستقلان.

        العتبة هي البوابة الوحيدة لحدث الارتباط: رابط قائم بين عقدتين تنشيطهما دون θ
        لا يُعزَّز ولا يُعفى من التآكل. السبب الحاسم أن التعزيز يضبط t_last_update
        فيمنح حصانة من التآكل تلك التكة — فلو سمحنا به دون العتبة لصار أي تنشيط
        متبقٍّ ضئيل يحفظ الرابط في النسيان.

        وصحة المصدر شرط على النشوء لا على التعزيز وحده، وإلا أُنشئ الرابط الزائف
        بـ W_base ثم تُرك للتقليم، وهي تكلفة ذاكرة بلا فائدة.
        """
        if i.A * j.A < Law.THETA_CREATION:
            return None
        if not self._valid_origin(i, j):
            return None
        existing = self.edge(i.nid, j.nid)
        if existing is not None:
            return existing
        e = Edge(
            i.nid,
            j.nid,
            Law.W_BASE,
            origin=f"{i.region}→{j.region}",
            t_created=self.t,
            t_last_update=self.t,
        )
        self._link(e)
        return e

    # ── ق2 — التعزيز الترابطي المزدوج (بصيغته الموحّدة بعد ق5 وق6)
    def _law2_reinforce(
        self,
        e: Edge,
        i: Node,
        j: Node,
        M: float,
        context: str | None = None,
        head: str | None = None,
        v: float = 0.0,
        zeta: float | None = None,
        structural_weight: float = 0.0,
    ) -> None:
        """ΔW_ij = η·M_sensory·(A_i·A_j)·e^(−α|t_recv − t_spawn^(i)|)·1_ValidOrigin·P_ij
        ·ζ(i,j)·(1 − W_ij/W_max).

        عامل التشبّع يمنع القفز إلى السقف من ملاحظة واحدة، فيبقى الوزن معنى إحصائياً.

        ق2-ب — عدم تناظر الدور: ζ = 1 للمكان→صفة، ζ_back للصفة→مكان، ζ_lat للصفة→صفة.
        الحلقة الإدراكية ليست زمرة متناظرة: «تفاحة حلوة» تجعل الحلاوة صفة للتفاحة
        لا العكس.

        وعند head = None تبقى ζ = 1 محايدة: التخميد ادّعاء عن الدور، وغياب
        المعلومة ليس ادّعاءً بضدّها. القراءة الحرفية («غير ذلك ⟹ ζ_lat») كانت
        ستخمد كل نداء مباشر إلى العُشر بلا مبرر.

        عند 1_ValidOrigin = 0 لا يقع حدث تعزيز إطلاقاً — لا وزن ولا n ولا contexts
        ولا t_last_update. تحديث المحاسبة مع ΔW=0 يبدو غير ضار، لكنه يلوّث contexts
        بسياقات لم يقع فيها اقتران، ويضخّم n فيمنح القفل لرابط لم يُعزَّز فعلياً.
        """
        if not self._valid_origin(i, j):
            return
        # ق8 — البروز: ε مفاجأةٌ تُقاس على الوزن قبل التحديث، فالرابط القوي لا يفاجئ
        eps = max(0.0, i.A * j.A - i.A * e.W)
        aff = (Law.W_NEG if v < 0.0 else Law.W_POS) * abs(v)
        sigma = min(1.0, max(0.0, Law.W_EPSILON * eps + aff + structural_weight))
        # القطبية تُكتب مع S وبشرطها: الزوج (S, valence) سجلٌّ متماسك لأقوى حدث
        # مرّ بالرابط. لو كُتبت وحدها لبقي S = 1.0 لصدمة قديمة وقطبيتها صفر.
        if sigma > e.S:
            e.S = sigma
            e.valence = v
        if sigma >= Law.THETA_SALIENCE:
            e.tagged = True
        if zeta is None:
            # ζ من الدور: الوسم fwd لا يقع إلا هنا، فالتعاقب الزمني ليس دوراً
            if head is None:
                zeta = 1.0
            elif i.nid == head:
                zeta = 1.0
                e.fwd = True
            elif j.nid == head:
                zeta = Law.ZETA_BACK
            else:
                zeta = Law.ZETA_LAT
        coherence = math.exp(-Law.ALPHA * abs(self.t - i.t_spawn))
        dW = Law.ETA * M * (i.A * j.A) * coherence * e.P * zeta * (1.0 - e.W / Law.W_MAX)
        # التضخيم للانفعال وحده: المفاجأة تُسرّع التعلّم مرة واحدة أصلاً عبر
        # عامل التشبّع، وتضخيمها ثانيةً حسابٌ مكرّر يُسرّع كل رابط بلا سبب.
        dW *= 1.0 + Law.MU_SALIENCE * aff
        e.W = min(Law.W_MAX, e.W + dW)
        e.n += 1
        e.t_last_update = self.t
        if context is not None:
            e.contexts.add(context)
            e.ctx_hits[context] = e.ctx_hits.get(context, 0) + 1

    # ── ق3 — ملغى ومحجوز (LAW 3 — ABOLISHED / RESERVED)
    def _law3_decay(self) -> None:
        """LAW 3 — ABOLISHED / RESERVED (Tombstone).
        No runtime weight decay, salience decay, universal low-weight pruning, or global orphan scanning.
        """

    def retire_transient_scope(self, context: str | None = None) -> int:
        """RFC-01 / RFC-06: Explicit scope-driven retirement of transient inst:* instances."""
        doomed_edges = []
        for (u, v), e in list(self.edges.items()):
            if (_is_instance(u) or _is_instance(v)) and (context is None or context in e.contexts):
                doomed_edges.append((u, v))
        for u, v in doomed_edges:
            self._unlink(u, v)
        return len(doomed_edges)

    # ── ق9 — التعميم والتجريد
    def _neighborhood(self, nid: str) -> dict[str, float]:
        """N(i) = {k : kind_ik = assoc ∧ W_ik ≥ W_sim^min} — الجوار المعتبر وأوزانه."""
        return {
            e.dst: e.W
            for e in self.out_edges(nid)
            if e.kind == "assoc" and e.W >= Law.W_SIM_MIN
        }

    def _sim(self, i: str, j: str) -> tuple[float, int]:
        """sim(i→j) = Σ_{k∈N(i)∩N(j)} min(W_ik, W_jk) / Σ_{k∈N(i)} W_ik.

        غير متناظرة عمداً: المقام جوار i وحده. فالوافد بصفتين مشتركتين مع الراسخ
        يبلغ sim ≈ 1 فيرث منه، بينما الراسخ الغني لا يتعلّم من الوافد شيئاً —
        وهكذا يقع التعميم من مشاهدتين دون أن يُلوَّث الأصل.
        """
        n_i = self._neighborhood(i)
        total = sum(n_i.values())
        if not total:
            return 0.0, 0
        n_j = self._neighborhood(j)
        shared = n_i.keys() & n_j.keys()
        return sum(min(n_i[k], n_j[k]) for k in shared) / total, len(shared)

    def _drop_sim(self, nid: str) -> None:
        """يزيل روابط التماثل الخارجة من العقدة — تُعاد حسابها لا تُصان.

        روابط الأدوار مسجَّلة من ترتيب وقع لا مشتقّة من جوار، فلا تُمسّ. وروابط
        الصنف تخصّ عقدة الصنف لا العضو: حذف نصفها هنا يترك بنية نصف قائمة،
        وحياتها كلها بيد قاعدة التراجع التي تحذف الصنف بعقدته وروابطه معاً.
        """
        for e in list(self.out_edges(nid)):
            if e.kind == "sim" and not e.is_intrinsic:
                self._unlink(nid, e.dst)

    def _law9_generalize(self, touched: list[Node]) -> None:
        """sim(i→j) ≥ θ_sim ⟹ رابط kind="sim" بوزن sim، ويُحذف فور هبوطها.

        ق4 تسبق ق9: التناقض يُبطل التماثل، وإلا عاد التماثل يصل ما فصلته البوابات.
        المرشّحون عبر in_adj لجيران i — لا مسحاً لكل الروابط.
        """
        for n in touched:
            self._drop_sim(n.nid)
        for n in touched:
            i = n.nid
            n_i = self._neighborhood(i)
            candidates: set[str] = set()
            for k in n_i:
                candidates |= set(self.in_adj.get(k, {}))
            candidates.discard(i)
            for j in candidates - self.X.get(i, set()):
                direct = self.edge(i, j)
                if direct is not None and direct.kind == "assoc":
                    continue    # اقتران مباشر قائم: لا يُشتقّ تماثل فوقه ولا يُطمس
                s, overlap = self._sim(i, j)
                if overlap >= Law.F_MIN and s >= Law.THETA_SIM:
                    self._link(
                        Edge(i, j, s, kind="sim", t_created=self.t, t_last_update=self.t)
                    )
        for n in touched:
            self._law9_category(n.nid)
        # تراجع الأصناف: الفحص على أعضاء الصنف القائم، لا على مجموعة التماثل
        # الحالية — فانضمام وافد يشارك صفة واحدة يُسقط الجوار المشترك للمجموعة
        # الموسَّعة، وليس فيه عليها لأن أعضاءها بلا الوافد صنف صحيح.
        for nid in [n for n in self.nodes if n.startswith("cat:")]:
            members = self.nodes[nid].members
            hoods = [set(self._neighborhood(m)) for m in members]
            if len(members) < Law.M_CAT or len(set.intersection(*hoods)) < Law.F_MIN:
                self._drop_node(nid)

    def _law9_category(self, nid: str) -> None:
        """|G| ≥ m_cat ∧ |∩_{m∈G} N(m)| ≥ f_min ⟹ عقدة صنف مجرّد.

        G = العقدة وكل ما يربطه بها تماثل في أي من الاتجاهين. الاسم من أعلى
        صفتين مشتركتين، مرتّبتين بأعلى أدنى وزن عبر الأعضاء ثم بالاسم.
        """
        group = {nid}
        group |= {e.dst for e in self.out_edges(nid) if e.kind == "sim"}
        group |= {e.src for e in self.in_edges(nid) if e.kind == "sim"}
        if len(group) < Law.M_CAT:
            return
        hoods = {m: self._neighborhood(m) for m in group}
        shared = set.intersection(*(set(h) for h in hoods.values()))
        if len(shared) < Law.F_MIN:
            return
        ranked = sorted(shared, key=lambda k: (-min(h[k] for h in hoods.values()), k))
        # المعرّف كاملاً بإبدال ':' بنقطة — وإلا اندمج text:round و vision:round صامتاً
        label = "cat:" + "+".join(sorted(k.replace(":", ".") for k in ranked[:2]))
        c = self.node(label, HUB)
        c.members |= group
        for m in group:
            for a, b in ((label, m), (m, label)):
                self._link(
                    Edge(a, b, Law.THETA_SIM, kind="cat",
                         t_created=self.t, t_last_update=self.t)
                )

    # ── ق12 — الحالة الداخلية
    def add_drive(
        self, name: str, level: float = 1.0, weight: float = 1.0, decay: float = 0.0
    ) -> None:
        """دافع d بمستوى x_d ∈ [0,1] ووزن ω_d ومعدل استنزاف ρ_d."""
        x = min(1.0, max(0.0, level))
        self.drives[name] = {"x": x, "w": weight, "rho": decay, "prev": x}

    def consume(self, name: str, amount: float) -> None:
        d = self.drives[name]
        d["x"] = min(1.0, max(0.0, d["x"] - amount))

    def restore(self, name: str, amount: float) -> None:
        d = self.drives[name]
        d["x"] = min(1.0, max(0.0, d["x"] + amount))

    def damage(self, magnitude: float) -> None:
        self.dmg += magnitude

    def set_goal(self, target: str) -> None:
        self.goal = target

    def resolve_goal(self, success: bool) -> None:
        """o = +g_succ عند النجاح، و−g_fail عند الفشل. البلوغ يأتي من الخارج."""
        self.outcome = Law.G_SUCC if success else -Law.G_FAIL
        self.goal = None

    def _law12_tick(self) -> None:
        """x_d ← max(0, x_d − ρ_d) — الموارد تنضب بمرور الزمن وحده."""
        for d in self.drives.values():
            d["x"] = max(0.0, d["x"] - d["rho"])

    def _law12_valence(self) -> float:
        """v = clip(κ·Σ ω_d u_d Δx_d / Σ ω_d − λ_dmg·dmg + o, −1, +1).

        u_d = 1 + γ_u(1 − x_d): العجز العميق يُضخّم إلحاحه. والوجدان يُقاس على
        الفارق لا المستوى المطلق — مورد ممتلئ لا يُفرح، والفرح في سدّ العجز.
        """
        total_w = sum(d["w"] for d in self.drives.values())
        drive_term = 0.0
        if total_w > 0.0:
            drive_term = Law.KAPPA_V * sum(
                d["w"] * (1.0 + Law.GAMMA_U * (1.0 - d["x"])) * (d["x"] - d["prev"])
                for d in self.drives.values()
            ) / total_w
        v = min(1.0, max(-1.0, drive_term - Law.LAMBDA_DMG * self.dmg + self.outcome))
        self.dmg = 0.0
        self.outcome = 0.0
        for d in self.drives.values():
            d["prev"] = d["x"]
        return v

    def expected_valence(self, seed: str, context: str | None = None) -> dict:
        """v̂(x) = Σ_j A_j(x)·V_j / Σ_j A_j(x) — حكم وجداني بالانتشار. قراءة خالصة."""
        r = self.infer([seed], context)
        ranked = r["ranked"]
        total = sum(a for _, a in ranked)
        v = sum(a * self.nodes[nid].V for nid, a in ranked) / total if total else 0.0
        verdict = "good" if v > 0.05 else "bad" if v < -0.05 else "neutral"
        return {"v": v, "verdict": verdict, "via_generalization": r["via_generalization"]}

    # ── المفاهيم المجردة
    def _spawn_concept(
        self,
        active: list[Node],
        context: str | None,
        M: float,
        valence: float = 0.0,
        structural_weight: float = 0.0,
    ) -> Node | None:
        """label(c) = hub:symbol(head)،  members(c) |= {head} ∪ E_t.

        الشرط: حلقة فيها نمطان حسيان مختلفان على الأقل، وتكرار المكان نفسه
        ≥ CONCEPT_MIN مرة. العدّاد على head لا على التركيبة: الهوية هي المكان،
        فلو كانت التركيبة لوُلد مفهوم جديد مع كل مصادفة وانفجر المركز.

        روابط المفهوم ζ = 1 في الاتجاهين — المفهوم هوية لا صفة — لكن الخارجة
        منه وحدها fwd، فتدخل في تنافس ق4 فتُبوَّب تلقائياً.
        """
        if not active:
            return None
        head = active[0]
        if _is_instance(head.nid):
            return None
        if len({n.region for n in active if n.region != HUB}) < 2:
            return None
        self.concept_hits[head.nid] = self.concept_hits.get(head.nid, 0) + 1
        if self.concept_hits[head.nid] < Law.CONCEPT_MIN:
            return None

        c = self.node(f"{HUB}:{head.nid.split(':', 1)[1]}", HUB, is_concept=True)
        c.is_concept = True
        c.head = head.nid
        c.excite(self.t, Law.C_MAX, head.episode)
        c.U += 1.0
        c.members |= {n.nid for n in active}
        for n in active:
            for i, j in ((c, n), (n, c)):
                e = self._law1_create(i, j)
                if e is not None:
                    # head=None ⟹ ζ = 1، ووجدان الحلقة يسري على روابط المفهوم كغيرها
                    self._law2_reinforce(
                        e, i, j, M, context, None, valence, structural_weight=structural_weight
                    )
                    if i is c:
                        e.fwd = True
        if len(c.members) > Law.K_MEMBERS:
            ranked = sorted(
                (m for m in c.members if m != c.head),
                key=lambda m: (-(self.edge(c.head, m).W if self.edge(c.head, m) else 0.0), m),
            )
            c.members = {c.head} | set(ranked[: Law.K_MEMBERS - 1])
        return c

    def _remove_node(self, nid: str) -> None:
        """يمحو العقدة أثراً أثراً: روابطها، ثم اسمها من مجموعات التناقض، والفهارس، ثم هي."""
        for e in list(self.out_edges(nid)):
            self._unlink(nid, e.dst)
        for e in list(self.in_edges(nid)):
            self._unlink(e.src, nid)
        self.out_adj.pop(nid, None)
        self.in_adj.pop(nid, None)
        self.X.pop(nid, None)
        for owner in list(self.X):
            self.X[owner].discard(nid)
            if not self.X[owner]:
                del self.X[owner]
        self.nodes.pop(nid, None)

    def _drop_node(self, nid: str) -> None:
        self._remove_node(nid)

    def _law10_merge(self, c: Node) -> Node:
        """(J ≥ θ_merge) ∨ (Cont = 1) ⟹ دمج في الأعلى U، والنواة = الأعضاء دون الرأس.

        استثناء الرأس ضروري: بدونه لا يتجاوز مفهومان متطابقان تماماً J = 0.5،
        لأن اسمَيهما يفترقان دوماً. cat و kitty قطّتهما واحدة واسماهما مختلفان.

        المرشّحون يُبلَغون عبر الأعضاء لا بمسح كل المركز: الشرطان معاً يوجبان
        تقاطعاً غير خالٍ، والمفهوم موصول بكل عضو له، فمن لا يشارك عضواً لا يندمج.
        """
        candidates: set[str] = set()
        for m in c.members:
            candidates |= set(self.in_adj.get(m, ()))
            candidates |= set(self.out_adj.get(m, ()))
        others = [
            n for n in (self.nodes.get(nid) for nid in sorted(candidates))
            if n is not None and n.region == HUB and n is not c
            and not n.nid.startswith(("cat:", "ev:"))
        ]
        for other in others:
            if other.nid not in self.nodes or c.nid not in self.nodes:
                continue
            core_c, core_o = c.members - {c.head}, other.members - {other.head}
            if not core_c or not core_o:
                continue
            inter = len(core_c & core_o)
            j_index = inter / len(core_c | core_o)
            cont = inter / min(len(core_c), len(core_o))
            if j_index < Law.THETA_MERGE and cont < 1.0:
                continue
            keep, drop = sorted((c, other), key=lambda n: (-n.U, n.nid))
            for e in list(self.out_edges(drop.nid)):
                self._unlink(drop.nid, e.dst)
                rival = self.edge(keep.nid, e.dst)
                if e.dst != keep.nid and (rival is None or e.W > rival.W):
                    e.src = keep.nid
                    self._link(e)
            for e in list(self.in_edges(drop.nid)):
                self._unlink(e.src, drop.nid)
                rival = self.edge(e.src, keep.nid)
                if e.src != keep.nid and (rival is None or e.W > rival.W):
                    e.dst = keep.nid
                    self._link(e)
            keep.members |= drop.members
            keep.U += drop.U
            self._drop_node(drop.nid)
            self._say(f"merge {drop.nid} → {keep.nid}")
            c = keep
        return c

    def _law10_capacity(self) -> None:
        """|Hub| > C_hub ⟹ تقليم أدنى المفاهيم U، وفضّ التعادل بأصغر اسم.

        المركز مورد محدود تتنافس عليه المفاهيم، لا مستودع مفتوح.
        """
        # الأصناف تجريد مشتقّ يُعاد بناؤه، فلا يزاحم المفاهيم على سعة المركز
        hubs = [
            n for n in self.nodes.values()
            if n.region == HUB and not n.nid.startswith(("cat:", "ev:"))
        ]
        if len(hubs) <= Law.C_HUB:
            return
        for n in sorted(hubs, key=lambda n: (n.U, n.nid))[: len(hubs) - Law.C_HUB]:
            self._drop_node(n.nid)
            self._say(f"prune {n.nid}")

    # ── ق4 — نشوء البوابة والتناقض
    def _law4_autogate(self, seeds: list[Node] | None = None) -> None:
        """التنافس بين رابطَي مصدر واحد: fwd(a)∧fwd(b) ∧ region(dst_a)=region(dst_b)
        ∧ C_a∩C_b=∅ ∧ C_a≠∅≠C_b  ⟹  g ← argmax_c ctxhits(c) لكلٍّ، وتناقض متبادل.

        البوابة تنشأ من البيانات لا من مُعلِّم: حين يخرج من مكان واحد مساران إلى
        منطقة واحدة، ولا يجتمعان في سياق واحد قط، فذلك بذاته دليل على أنهما معنيان
        ظرفيّان لا صفتان لشيء واحد.

        شرط fwd جوهري: بدونه يصير sweet→apple و sweet→pear في سياقين مختلفين
        «تناقضاً»، وهما مجرد كائنين يشتركان في صفة — وتلك هي الحالة الشائعة.

        النطاق: المصادر التي تغيّرت روابطها هذه التكة، لا كل مصادر الشبكة —
        فتنافس مصدرٍ لا يتبدّل إلا بتبدّل روابطه هو. و`seeds=None` تفحص الكل.

        وفور إسناد أي بوابة تدخل جيرانُ الهدف الواردون النطاق: روابط المفهوم
        تُوسم fwd والمفهوم ليس إشارةً في التكة، فلولا هذا الانتشار لبقي
        `hub:bat` بلا بوابة بينما `text:bat` مبوَّب — خطأ لا يُسقطه اختبار
        وتكشفه البصمة.
        """
        pending = list(self.out_adj) if seeds is None else [n.nid for n in seeds]
        seen: set[str] = set()
        while pending:
            src = pending.pop()
            if src in seen:
                continue
            seen.add(src)
            rivals = [e for e in self.out_edges(src) if e.fwd and e.contexts]
            for idx, ea in enumerate(rivals):
                for eb in rivals[idx + 1:]:
                    if self.nodes[ea.dst].region != self.nodes[eb.dst].region:
                        continue
                    if ea.contexts & eb.contexts:
                        continue
                    ea.g = min(ea.ctx_hits, key=lambda c, h=ea.ctx_hits: (-h[c], c))
                    eb.g = min(eb.ctx_hits, key=lambda c, h=eb.ctx_hits: (-h[c], c))
                    self.X.setdefault(ea.dst, set()).add(eb.dst)
                    self.X.setdefault(eb.dst, set()).add(ea.dst)
                    for dst in (ea.dst, eb.dst):
                        pending += [s for s in self.in_adj.get(dst, ()) if s not in seen]

    def add_contradiction(self, a: str, b: str) -> None:
        """ق4 — تسجيل تناقض صريح متبادل بين عقدتين في مصفوفة التناقض X."""
        self._link_contradiction(a, b)

    def _link_contradiction(self, a: str, b: str) -> None:
        """ق4 — تسجيل تناقض صريح متبادل بين عقدتين في مصفوفة التناقض X."""
        nid_a = a if ":" in a else f"text:{a}"
        nid_b = b if ":" in b else f"text:{b}"
        self.X.setdefault(nid_a, set()).add(nid_b)
        self.X.setdefault(nid_b, set()).add(nid_a)

    # ── حلقة الإدراك
    def observe(
        self,
        signals: list[tuple[str, str]],
        context: str | None = None,
        valence: float | None = None,
        structural_weight: float = 0.0,
    ) -> None:
        """تكة إدراكية واحدة: ق12، ثم إثارة، ثم ق1+ق2 على كل زوج مرتب نشط،
        ثم المفاهيم، ثم ق4، ثم ق3.

        v تُشتقّ من الحالة الداخلية، والتمرير الصريح يتجاوزها للاختبار والتحليل.
        """
        if self.enable_prediction:
            actual_nids = {f"{region}:{symbol}" for region, symbol in signals}
            self._evaluate_predictions(actual_nids)
        self.t += 1
        self._law12_tick()
        computed = self._law12_valence()
        v = computed if valence is None else valence
        episode = f"ep{self.t}"
        # M_sensory = 1 + M_boost·(|الأنماط الحسية في الإشارات الواردة| − 1) ≥ 1
        M = max(1.0, 1.0 + Law.M_BOOST * (len({region for region, _ in signals}) - 1))
        # الرأس: أول إشارة في الحلقة — هو ما يكسر تناظر الدور
        head = f"{signals[0][0]}:{signals[0][1]}" if signals else None
        active = []
        for region, symbol in signals:
            n = self.node(f"{region}:{symbol}", region)
            n.excite(self.t, 1.0, episode)
            active.append(n)
        # الطبع على الرأس وحده: القطبية تلتصق بالمكان، والصفات المشتركة تكتسب
        # دلالتها بالانتشار — وإلا صبغ جوعٌ عابر كلَّ صفة حضرت معه.
        if active:
            active[0].V = (1.0 - Law.RHO_V) * active[0].V + Law.RHO_V * v
        # التنشيط المتبقي من تكات سابقة يدخل البركة، فيربط عبر الزمن.
        # البركة = إشارات هذه التكة وحدها. العقد الباقية من تكات سابقة تحمل
        # تنشيطاً متبقياً لكن relax صفّر حلقتها، فيردّها فحص المصدر في ق1 حتماً.
        # مسحُ كل العقد ليُرفض معظمها كلفةٌ بحجم الشبكة بلا أثر في النتيجة.
        pool = list({n.nid: n for n in active}.values())
        for i in pool:
            for j in pool:
                if i is j:
                    continue
                e = self._law1_create(i, j)
                if e is not None:
                    self._law2_reinforce(
                        e, i, j, M, context, head, v, structural_weight=structural_weight
                    )
        seeds = list(active)
        concept = self._spawn_concept(
            active, context, M, v, structural_weight=structural_weight
        )
        if concept is not None:
            seeds.append(self._law10_merge(concept))
            self._law10_capacity()
        self._law4_autogate([n for n in seeds if n.nid in self.nodes])
        self._law9_generalize(active)
        if self.enable_prediction:
            self._compute_predictions()

    def tick(self) -> None:
        """تكة إدراكية صامتة: تآكل واضمحلال بدون إشارات جديدة وتحديث القوانين الدورية."""
        self.observe([])

    # ── ق4 — توازن الطاقة والسعة
    @staticmethod
    def _sigma(x: float) -> float:
        """σ(x) = 1 − e^(−x) — تخميد الوارد، لا يبلغ C_max مهما كبر الدخل.

        بدونه تتضخّم عقدة وصلتها عشرة مسارات ضعيفة فتتفوّق على عقدة وصلها مسار
        واحد قوي: التشبّع الأسّي يجعل قوة المسار أهم من عدد المسارات.
        """
        if x <= 0.0:
            return 0.0
        return 1.0 - math.exp(-x)

    def _cap_outflow(self, shares: dict[str, float]) -> dict[str, float]:
        """Σ_j A_out(i→j) ≤ C_max^(i) — قصّ بنسبة واحدة يحفظ الترتيب النسبي.

        العقدة موزّع محايد: لا تخلق طاقة، ولا يخرج منها ما يجاوز سقفاً واحداً.
        """
        total = sum(shares.values())
        if total <= Law.C_MAX:
            return shares
        scale = Law.C_MAX / total
        return {dst: share * scale for dst, share in shares.items()}

    # ── ق7 — الاستدلال الانبثاقي
    def infer(
        self,
        seeds: list[str],
        context: str | None = None,
        target: str | None = None,
        resonant: bool = False,
        mode: str = "standard",
    ) -> dict:
        """A_j = min(C_max, σ(Σ_i A_i·W_ij·R_j·E^(h)·G_ij(c) − β·Σ_{k∈X(j)} A_k)).

        E^(h) = E^(0) − γ(h−1)، و R_j = 1{j ∉ V}·1{j ≠ parent(i)}: البثّ الواحد
        يمنع الدوران بنيوياً، ومنع الارتداد يمنع أقصر حلقة ممكنة بين رابطين متقابلين.

        الرابط المغلق بوابةً لا يُحتسب في سقف الصادر أصلاً — يُستبعد قبله فلا
        يستهلك حصة. والكبح يُطرح بعد التجميع وقبل σ، فقيمة المنافس هي الأعلى بين
        ما ورده في هذه القفزة وما بلغه من تنشيط سابق.

        قراءة خالصة: لا يعدّل وزناً ولا t ولا تنشيط عقدة ولا g ولا X.
        الحالة كلها محلّية في activation.
        """
        if resonant or mode == "resonant":
            from .reasoning import deep_infer as _deep_infer

            return _deep_infer(self, seeds, context=context, target=target, mode=mode)

        activation = {nid: Law.C_MAX for nid in seeds if nid in self.nodes}
        visited = set(activation)
        parent: dict[str, str] = {}
        generalized: set[str] = set()   # بُلِّغت عبر مشتقّ — وكل ما بعدها
        frontier = list(activation)
        trace: list[dict] = []
        hop = 0
        while frontier:
            E = Law.E_BUDGET_0 - Law.GAMMA * hop
            if E <= 0.0:
                break
            hop += 1
            incoming: dict[str, float] = {}
            # parent = مَن ساقَ فعلاً أكبر قدر من التنشيط: المقارنة على القيمة
            # المقصوصة نفسها التي تُجمَّع، لا على الخام قبل سقف الصادر.
            best_capped: dict[str, float] = {}
            derived_src: set[str] = set()   # بُلِّغت هذه القفزة عبر رابط مشتقّ
            for src in frontier:
                raw = {}
                for e in self.out_edges(src):
                    if e.dst in visited or e.dst == parent.get(src):
                        continue
                    if not e.gate_open(context):
                        continue
                    raw[e.dst] = activation[src] * e.W * E
                    if e.kind != "assoc":
                        # A_j *= δ_gen لكل رابط مشتقّ: التخميد على الحصة قبل سقف
                        # الصادر، فالمعرفة المستنتَجة تُزاحم المباشرة مخمَّدةً لا كاملة.
                        raw[e.dst] *= Law.DELTA_GEN
                        derived_src.add(e.dst)
                for dst, share in self._cap_outflow(raw).items():
                    if share <= Law.MIN_SIGNAL:
                        continue
                    incoming[dst] = incoming.get(dst, 0.0) + share
                    if share > best_capped.get(dst, 0.0):
                        best_capped[dst] = share
                        parent[dst] = src
            activated = []
            for dst, total in incoming.items():
                press = sum(
                    max(incoming.get(k, 0.0), activation.get(k, 0.0))
                    for k in self.X.get(dst, ())
                )
                a = min(Law.C_MAX, self._sigma(total - Law.BETA_INHIBIT * press))
                if a <= Law.MIN_SIGNAL:
                    continue
                activation[dst] = a
                visited.add(dst)
                activated.append(dst)
                if dst in derived_src or parent.get(dst) in generalized:
                    generalized.add(dst)
            trace.append({"hop": hop, "E": round(E, 2), "activated": activated})
            frontier = activated
        ranked = sorted(
            ((nid, round(a, 3)) for nid, a in activation.items() if nid not in seeds),
            key=lambda pair: (-pair[1], pair[0]),
        )
        return {
            "answer": ranked[0][0] if ranked else None,
            "ranked": ranked,
            "hops": len(trace),
            "trace": trace,
            "via_generalization": generalized,
        }

    def query_cross_modal(
        self,
        query_signals: list[tuple[str, str]],
        target_prefix: str = "text:",
    ) -> dict:
        """Local Evidence Share Ranking (LESR v1.0) for cross-modal retrieval.

        Read-only retrieval path implementing Local Evidence Conservation and Exact-Top-Tie
        Ambiguity semantics according to DGCA-Cross-Modal-Retrieval-Ranking-Repair-Formal-Architectural-Specification-v1.0.md.
        """
        # Deduplicate query evidence nodes within query scope
        evidence_nodes = []
        seen = set()
        for mod, val in query_signals:
            if val.startswith("inst:"):
                continue
            v_node = val if val.startswith(f"{mod}:") else f"{mod}:{val}"
            if v_node in self.nodes and v_node not in seen:
                seen.add(v_node)
                evidence_nodes.append(v_node)

        if not evidence_nodes:
            return {
                "outcome": "NO_RESULT",
                "winner": None,
                "scores": {},
                "ranked": [],
                "ambiguous_candidates": [],
            }

        # Calculate Local Evidence Share for each evidence source
        q_share = 1.0 / len(evidence_nodes)
        candidate_supports: dict[str, float] = {}
        evidence_decompositions: dict[str, dict[str, float]] = {}

        for f in evidence_nodes:
            # Gather unique candidate neighbors and maximum edge weights (reciprocal deduplication)
            candidate_weights: dict[str, float] = {}
            for e in list(self.out_edges(f)) + list(self.in_edges(f)):
                target = e.dst if e.src == f else e.src
                if target.startswith(target_prefix):
                    candidate_weights[target] = max(candidate_weights.get(target, 0.0), e.W)

            Z_f = sum(candidate_weights.values())
            if Z_f > 0.0:
                for c, w in candidate_weights.items():
                    rho_f_c = w / Z_f
                    contrib = q_share * rho_f_c
                    candidate_supports[c] = candidate_supports.get(c, 0.0) + contrib
                    evidence_decompositions.setdefault(c, {})[f] = contrib

        if not candidate_supports:
            return {
                "outcome": "NO_RESULT",
                "winner": None,
                "scores": {},
                "ranked": [],
                "ambiguous_candidates": [],
            }

        # Identify maximum support and check for exact top ties
        max_score = max(candidate_supports.values())
        top_candidates = [c for c, s in candidate_supports.items() if abs(s - max_score) < 1e-12]

        ranked = sorted(
            [{"concept": c.replace(target_prefix, ""), "score": s, "node": c} for c, s in candidate_supports.items()],
            key=lambda x: (-x["score"], x["concept"]),
        )

        if len(top_candidates) == 1:
            winner_node = top_candidates[0]
            winner_concept = winner_node.replace(target_prefix, "")
            outcome = "WINNER"
            ambiguous_candidates = []
        else:
            winner_concept = None
            outcome = "AMBIGUOUS"
            ambiguous_candidates = sorted([c.replace(target_prefix, "") for c in top_candidates])

        return {
            "outcome": outcome,
            "winner": winner_concept,
            "scores": candidate_supports,
            "ranked": ranked,
            "ambiguous_candidates": ambiguous_candidates,
            "evidence_decompositions": evidence_decompositions,
        }

    # ── ق11 — التتابع الزمني والدور
    def observe_sequence(
        self,
        steps: list[list[tuple[str, str]]],
        context: str | None = None,
        valence: float | None = None,
        structural_weight: float = 0.0,
    ) -> None:
        """E_t = [L_0, …, L_p] — خطوات مرتّبة في حلقة إدراكية واحدة وتكة واحدة.

        ζ داخل الخطوة منطق ق2-ب برأس الخطوة، وعبر الخطوات موضعي:
        e^(−α_lag(p_j−p_i−1)) أماماً، وζ_rev·e^(−α_lag(p_i−p_j−1)) عكساً.

        «الكلب عضّ الرجل» ≠ «الرجل عضّ الكلب» بنفس العقد ونفس الأزواج. والوزن
        الاتجاهي وحده لا يكفي: الزوجان متماثلان إحصائياً في مدوّنة تحمل الجهتين،
        فالترتيب يُطبع في هوية بنية ثالثة هي عقدة الحدث بأدوارها الموضعية.
        """
        if self.enable_prediction:
            actual_nids = {f"{region}:{symbol}" for step in steps for region, symbol in step}
            self._evaluate_predictions(actual_nids)
        self.t += 1
        self._law12_tick()
        computed = self._law12_valence()
        v = computed if valence is None else valence
        episode = f"ep{self.t}"
        layers: list[list[Node]] = []
        for step in steps:
            layer = []
            for region, symbol in step:
                n = self.node(f"{region}:{symbol}", region)
                n.excite(self.t, 1.0, episode)
                layer.append(n)
            layers.append(layer)
        active = [n for layer in layers for n in layer]
        if not active:
            return
        active[0].V = (1.0 - Law.RHO_V) * active[0].V + Law.RHO_V * v
        M = max(1.0, 1.0 + Law.M_BOOST * (len({n.region for n in active}) - 1))

        for p_i, layer_i in enumerate(layers):
            head = layer_i[0].nid
            for p_j, layer_j in enumerate(layers):
                for i in layer_i:
                    for j in layer_j:
                        if i is j:
                            continue
                        e = self._law1_create(i, j)
                        if e is None:
                            continue
                        if p_i == p_j:
                            self._law2_reinforce(
                                e, i, j, M, context, head, v, structural_weight=structural_weight
                            )
                            continue
                        gap = abs(p_j - p_i) - 1
                        zeta = math.exp(-Law.ALPHA_LAG * gap)
                        if p_j < p_i:
                            zeta *= Law.ZETA_REV
                        # الفارق الموضعي متوسط متحرك، ويُحدَّث قبل زيادة n
                        e.lag = (e.lag * e.n + (p_j - p_i)) / (e.n + 1)
                        self._law2_reinforce(
                            e, i, j, M, context, None, v, zeta, structural_weight=structural_weight
                        )

        if len(layers) > 1:
            label = "ev:" + "->".join(lr[0].nid.split(":", 1)[1] for lr in layers)
            ev = self.node(label, HUB)
            ev.excite(self.t, Law.C_MAX, episode)
            ev.members |= {n.nid for n in active}
            for k, layer in enumerate(layers):
                for a, b in ((label, layer[0].nid), (layer[0].nid, label)):
                    e = self.edge(a, b)
                    if e is None:
                        e = Edge(a, b, Law.W_BASE, kind=f"role{k}", t_created=self.t)
                        self._link(e)
                    e.W = min(Law.W_MAX, e.W + Law.ETA * (1.0 - e.W))
                    e.n += 1
                    e.t_last_update = self.t

        seeds = list(active)
        concept = self._spawn_concept(
            active, context, M, v, structural_weight=structural_weight
        )
        if concept is not None:
            seeds.append(self._law10_merge(concept))
            self._law10_capacity()
        self._law4_autogate([n for n in seeds if n.nid in self.nodes])
        self._law9_generalize(active)
        if self.enable_prediction:
            self._compute_predictions()

    # ── ق13 — التنبؤ والسببية والتعلم من الخيبة
    def _compute_predictions(self) -> None:
        """ق13 — حساب التنشيط الاستشرافي Â_j(t) عبر روابط fwd للعقد النشطة في t-1،
        وإدخال العقد في بركة التنبؤ إذا بلغت Â_j ≥ θ_pred (0.25).
        """
        self.prediction_pool.clear()
        self.prediction_sources.clear()
        raw_energy: dict[str, float] = {}
        sources: dict[str, list[str]] = {}
        for nid, node in self.nodes.items():
            if node.A <= 0.0:
                continue
            for e in self.out_edges(nid):
                if e.fwd or e.kind == "role0":
                    raw_energy[e.dst] = raw_energy.get(e.dst, 0.0) + node.A * e.W
                    sources.setdefault(e.dst, []).append(nid)
        for dst, total in raw_energy.items():
            a_hat = self._sigma(total)
            if a_hat >= Law.THETA_PRED:
                self.prediction_pool[dst] = a_hat
                self.prediction_sources[dst] = sources[dst]

    def _evaluate_predictions(self, actual_active: set[str]) -> None:
        """ق13 — تقييم خطأ التنبؤ ε_j = A_actual − Â_j على بركة التنبؤ حصراً (O(1)).
        - عند الخيبة (ε < 0): تآكل خيبة فوري ΔW = η_disappoint · |ε| · (1 − Locked·0.8)،
          وزيادة عداد k_fail، واشتقاق نبضة فشل الهدف o(t) = −g_fail · |ε_goal|.
        - عند النجاح (ε ≥ 0): تصفير k_fail.
        """
        if not self.prediction_pool:
            return
        for dst, a_hat in list(self.prediction_pool.items()):
            a_actual = 1.0 if dst in actual_active else 0.0
            eps = a_actual - a_hat
            if eps < 0.0:
                decay_delta = Law.ETA_DISAPPOINT * abs(eps)
                for src in self.prediction_sources.get(dst, []):
                    e = self.edge(src, dst)
                    if e is not None and not e.is_intrinsic:
                        attenuation = (1.0 - 0.8) if e.locked else 1.0
                        delta = decay_delta * attenuation
                        e.W = max(0.0, e.W - delta)
                        e.k_fail += 1
                if self.goal is not None:
                    target_matches = self.goal == dst or dst.endswith(f":{self.goal}")
                    if target_matches:
                        self.outcome = -Law.G_FAIL * abs(eps)
                        self.goal = None
            else:
                for src in self.prediction_sources.get(dst, []):
                    e = self.edge(src, dst)
                    if e is not None:
                        e.k_fail = 0

    def predict_next(self, prefix: list[str], context: str | None = None) -> dict:
        """score(ev|prefix) = (Σ_k W(ev,h_k)·1{kind=role_k} + W(ev,h_next)) / (|prefix|+1).

        المطابقة موضعية ومن الموضع صفر: بادئة لم تُرَ تعيد None ولا تخترع.
        قراءة خالصة.
        """
        scored: dict[str, float] = {}
        for nid in [n for n in self.nodes if n.startswith("ev:")]:
            total = 0.0
            for k, item in enumerate(prefix):
                e = self.edge(nid, item)
                if e is None or e.kind != f"role{k}":
                    break
                total += e.W
            else:
                nxt = [e for e in self.out_edges(nid) if e.kind == f"role{len(prefix)}"]
                if nxt:
                    score = (total + nxt[0].W) / (len(prefix) + 1)
                    scored[nxt[0].dst] = max(scored.get(nxt[0].dst, 0.0), score)
        ranked = sorted(
            ((n, round(s, 3)) for n, s in scored.items()),
            key=lambda pair: (-pair[1], pair[0]),
        )
        return {"answer": ranked[0][0] if ranked else None, "ranked": ranked}

    # ── متفرقات
    def _say(self, msg: str) -> None:
        self.log.append(f"[t={self.t}] {msg}")

    def stats(self) -> dict:
        return {
            "t": self.t,
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "concepts": sum(1 for n in self.nodes.values() if n.is_concept),
        }

    # ── التخزين والاسترجاع (Graph Persistence & Serialization - RFC-11)
    def to_dict(self) -> dict[str, Any]:
        """تحويل الشبكة بالكامل إلى قاموس بيانات قياسي قابل للتحويل لـ JSON."""
        nodes_data = {}
        for nid, n in self.nodes.items():
            nodes_data[nid] = {
                "nid": n.nid,
                "region": n.region,
                "is_concept": n.is_concept,
                "A": n.A,
                "t_spawn": n.t_spawn,
                "episode": n.episode,
                "members": list(n.members),
                "U": n.U,
                "V": n.V,
                "head": n.head,
                "is_intrinsic": n.is_intrinsic,
                "N_total": n.N_total,
            }

        edges_data = []
        for e in self.edges.values():
            edges_data.append({
                "src": e.src,
                "dst": e.dst,
                "W": e.W,
                "kind": e.kind,
                "origin": e.origin,
                "t_created": e.t_created,
                "t_last_update": e.t_last_update,
                "n": e.n,
                "M_max": e.M_max,
                "S": e.S,
                "tagged": e.tagged,
                "valence": e.valence,
                "lag": e.lag,
                "fwd": e.fwd,
                "g": e.g,
                "contexts": list(e.contexts),
                "ctx_hits": e.ctx_hits,
                "is_intrinsic": e.is_intrinsic,
                "k_fail": e.k_fail,
            })

        x_data = {k: list(v) for k, v in self.X.items()}

        assemblies_data = []
        if self._assembly_manager is not None:
            for versions in self._assembly_manager.assemblies.values():
                for asm in versions:
                    assemblies_data.append({
                        "assembly_id": asm.assembly_id,
                        "version": asm.version,
                        "member_edges": [list(e) for e in asm.member_edges],
                        "origin_signature": asm.origin_signature,
                        "predecessor_version": asm.predecessor_version,
                        "parent_assemblies": list(asm.parent_assemblies),
                        "is_retired": asm.is_retired,
                    })

        return {
            "version": "1.0",
            "t": self.t,
            "enable_prediction": self.enable_prediction,
            "concept_hits": self.concept_hits,
            "drives": self.drives,
            "dmg": self.dmg,
            "goal": self.goal,
            "outcome": self.outcome,
            "hypotheses": self.hypotheses,
            "X": x_data,
            "nodes": nodes_data,
            "edges": edges_data,
            "assemblies": assemblies_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CognitiveGraph:
        """إعادة بناء شبكة معرفية كاملة من قاموس بيانات."""
        g = cls(
            t=data.get("t", 0),
            enable_prediction=data.get("enable_prediction", False),
            concept_hits=data.get("concept_hits", {}),
            drives=data.get("drives", {}),
            dmg=data.get("dmg", 0.0),
            goal=data.get("goal"),
            outcome=data.get("outcome", 0.0),
            hypotheses=data.get("hypotheses", []),
        )

        for k, v in data.get("X", {}).items():
            g.X[k] = set(v)

        for nid, ndata in data.get("nodes", {}).items():
            n = Node(
                nid=ndata["nid"],
                region=ndata["region"],
                is_concept=ndata.get("is_concept", False),
                A=ndata.get("A", 0.0),
                t_spawn=ndata.get("t_spawn", -999),
                episode=ndata.get("episode"),
                members=set(ndata.get("members", [])),
                U=ndata.get("U", 0.0),
                V=ndata.get("V", 0.0),
                head=ndata.get("head"),
                is_intrinsic=ndata.get("is_intrinsic", False),
                N_total=ndata.get("N_total", 0),
            )
            g.nodes[nid] = n

        for edata in data.get("edges", []):
            e = Edge(
                src=edata["src"],
                dst=edata["dst"],
                W=edata.get("W", 0.0),
                kind=edata.get("kind", "assoc"),
                origin=edata.get("origin", ""),
                t_created=edata.get("t_created", 0),
                t_last_update=edata.get("t_last_update", 0),
                n=edata.get("n", 0),
                M_max=edata.get("M_max", 1.0),
                S=edata.get("S", 0.0),
                tagged=edata.get("tagged", False),
                valence=edata.get("valence", 0.0),
                lag=edata.get("lag", 0.0),
                fwd=edata.get("fwd", False),
                g=edata.get("g"),
                contexts=set(edata.get("contexts", [])),
                ctx_hits=edata.get("ctx_hits", {}),
                is_intrinsic=edata.get("is_intrinsic", False),
                k_fail=edata.get("k_fail", 0),
            )
            g.edges[(e.src, e.dst)] = e
            g.out_adj.setdefault(e.src, {})[e.dst] = e
            g.in_adj.setdefault(e.dst, {})[e.src] = e

        if data.get("assemblies"):
            from .assembly import AssemblyManager, StructuralAssembly
            mgr = AssemblyManager(g)
            for adata in data["assemblies"]:
                asm = StructuralAssembly(
                    assembly_id=adata["assembly_id"],
                    version=adata["version"],
                    member_edges=frozenset((pair[0], pair[1]) for pair in adata["member_edges"]),
                    origin_signature=adata["origin_signature"],
                    predecessor_version=adata.get("predecessor_version"),
                    parent_assemblies=tuple(adata.get("parent_assemblies", ())),
                    is_retired=adata.get("is_retired", False),
                )
                mgr.assemblies.setdefault(asm.assembly_id, []).append(asm)
            mgr.rebuild_indexes()
            g.assembly_manager = mgr

        return g

    def save(self, filepath: str) -> None:
        """حفظ بنية الشبكة في ملف JSON."""
        import json
        import os

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self, filepath: str) -> None:
        """تحميل واستبدال بنية الشبكة من ملف JSON."""
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        loaded = self.from_dict(data)
        self.t = loaded.t
        self.enable_prediction = loaded.enable_prediction
        self.concept_hits = loaded.concept_hits
        self.drives = loaded.drives
        self.dmg = loaded.dmg
        self.goal = loaded.goal
        self.outcome = loaded.outcome
        self.hypotheses = loaded.hypotheses
        self.X = loaded.X
        self.nodes = loaded.nodes
        self.edges = loaded.edges
        self.out_adj = loaded.out_adj
        self.in_adj = loaded.in_adj

    @classmethod
    def load_from_file(cls, filepath: str) -> CognitiveGraph:
        """تحميل وإنشاء شبكة معرفية مباشرة من ملف JSON."""
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
